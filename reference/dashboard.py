#!/usr/bin/env python3
"""AgentCS dashboard — browser UI for the reference protocol implementation.

Stdlib-only. Serves a single page on http://127.0.0.1:8080 that:
  - Shows current phase, period, risk, agents, issues, and the audit log (live)
  - Lets the human do the four checkpoint actions: Approve OAP, Review ARR,
    Reduce Scope, Demob — when they're ready, not on a script's schedule
  - Lets the human launch agents (planning-1, cos-1, etc.) and watch their
    captured stdout in a side panel

Run:
    AGENTCS_HOME=/tmp/acs-ui-demo python3 dashboard.py
    open http://127.0.0.1:8080
"""
import json
import os
import subprocess
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
AGENTCS_PY = HERE / "agentcs.py"
HOME = Path(os.environ.get("AGENTCS_HOME", Path.home() / ".agentcs"))
HOST = os.environ.get("AGENTCS_DASH_HOST", "127.0.0.1")
PORT = int(os.environ.get("AGENTCS_DASH_PORT", "8080"))

# (agent_id, project_id) -> {proc, started_at, log_path, returncode}
_RUNS = {}
_RUNS_LOCK = threading.Lock()


# ---------------------------------------------------------------- helpers

def active_project_id():
    f = HOME / "active"
    return f.read_text().strip() if f.exists() else None


def project_dir(pid):
    return HOME / "projects" / pid


def list_projects():
    p = HOME / "projects"
    return sorted([d.name for d in p.iterdir() if d.is_dir()]) if p.exists() else []


def read_state(pid):
    f = project_dir(pid) / "state.json"
    return json.loads(f.read_text()) if f.exists() else None


def read_audit(pid, limit=80):
    f = project_dir(pid) / "audit.jsonl"
    if not f.exists():
        return []
    lines = f.read_text().splitlines()
    return [json.loads(line) for line in lines[-limit:]]


def read_agent_log(pid, agent_id, limit_bytes=20_000):
    log = project_dir(pid) / f"agent-{agent_id}.log"
    if not log.exists():
        return ""
    data = log.read_bytes()
    if len(data) > limit_bytes:
        data = b"...[truncated]...\n" + data[-limit_bytes:]
    return data.decode("utf-8", errors="replace")


def run_cli(args, env_extra=None):
    """Synchronous agentcs.py call. Returns (returncode, stdout)."""
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    cmd = [sys.executable, str(AGENTCS_PY)] + args
    proc = subprocess.run(cmd, env=env, cwd=HERE, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def start_agent(agent_id, stepped=False):
    """Launch agentcs.py run <id> in the background; capture output to a log file."""
    pid = active_project_id()
    if not pid:
        return False, "no active project"
    with _RUNS_LOCK:
        existing = _RUNS.get((agent_id, pid))
        if existing and existing["proc"].poll() is None:
            return False, f"{agent_id} is already running"
    log = project_dir(pid) / f"agent-{agent_id}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(log, "wb")
    cmd = [sys.executable, str(AGENTCS_PY), "run", agent_id]
    if stepped:
        cmd.append("--stepped")
    env = os.environ.copy()
    proc = subprocess.Popen(cmd, env=env, cwd=HERE, stdout=log_fh, stderr=subprocess.STDOUT)
    with _RUNS_LOCK:
        _RUNS[(agent_id, pid)] = {
            "proc": proc, "started_at": time.time(), "log_path": str(log), "log_fh": log_fh,
        }
    threading.Thread(target=_reap, args=((agent_id, pid),), daemon=True).start()
    return True, f"launched {agent_id}"


def _reap(key):
    with _RUNS_LOCK:
        run = _RUNS.get(key)
    if not run:
        return
    run["proc"].wait()
    try:
        run["log_fh"].close()
    except Exception:
        pass


def runs_for_project(pid):
    out = {}
    with _RUNS_LOCK:
        for (aid, p), info in _RUNS.items():
            if p != pid:
                continue
            running = info["proc"].poll() is None
            out[aid] = {
                "running": running,
                "returncode": None if running else info["proc"].returncode,
                "started_at": info["started_at"],
                "duration": time.time() - info["started_at"],
            }
    return out


# ---------------------------------------------------------------- API

def api_state(_qs):
    pid = active_project_id()
    if not pid:
        return 200, {"active": None, "projects": list_projects()}
    s = read_state(pid)
    audit = read_audit(pid)
    return 200, {
        "active": pid,
        "projects": list_projects(),
        "state": s,
        "audit": audit,
        "runs": runs_for_project(pid),
    }


def api_agent_log(qs):
    pid = active_project_id()
    aid = qs.get("agent", [""])[0]
    if not pid or not aid:
        return 400, {"error": "need agent and active project"}
    return 200, {"log": read_agent_log(pid, aid)}


def api_init(body):
    sow = body.get("sow")
    if not sow:
        return 400, {"error": "need 'sow' in body"}
    if isinstance(sow, str):
        try:
            sow = json.loads(sow)
        except json.JSONDecodeError as e:
            return 400, {"error": f"invalid JSON: {e}"}
    tmp = HERE / ".dashboard-tmp-sow.json"
    tmp.write_text(json.dumps(sow))
    rc, out = run_cli(["init", "--from-file", str(tmp)])
    tmp.unlink(missing_ok=True)
    return (200 if rc == 0 else 400), {"output": out, "rc": rc}


def api_run_agent(body):
    aid = body.get("agent_id")
    stepped = bool(body.get("stepped", False))
    if not aid:
        return 400, {"error": "need agent_id"}
    ok, msg = start_agent(aid, stepped=stepped)
    return (200 if ok else 400), {"message": msg}


def api_approve_oap(_body):
    rc, out = run_cli(["approve-oap"])
    return (200 if rc == 0 else 400), {"output": out, "rc": rc}


def api_review_arr(body):
    decision = body.get("decision", "accept")
    comment = body.get("comment", "")
    args = ["review-arr", decision]
    if comment:
        args += ["--comment", comment]
    rc, out = run_cli(args)
    return (200 if rc == 0 else 400), {"output": out, "rc": rc}


def api_demob(_body):
    rc, out = run_cli(["demob"])
    return (200 if rc == 0 else 400), {"output": out, "rc": rc}


def api_scope_reduce(body):
    oid = body.get("objective_id")
    reason = body.get("reason", "")
    if not oid:
        return 400, {"error": "need objective_id"}
    args = ["scope", "reduce", oid]
    if reason:
        args += ["--reason", reason]
    rc, out = run_cli(args)
    return (200 if rc == 0 else 400), {"output": out, "rc": rc}


def api_propose_oap(body):
    """Convenience for the demo: planner-impersonating shortcut to load the example OAP.

    In a real flow the planning agent does this; this endpoint exists so a human
    can also load a hand-edited OAP without invoking Claude Code.
    """
    oap = body.get("oap")
    if not oap:
        return 400, {"error": "need 'oap' in body"}
    if isinstance(oap, str):
        try:
            oap = json.loads(oap)
        except json.JSONDecodeError as e:
            return 400, {"error": f"invalid JSON: {e}"}
    tmp = HERE / ".dashboard-tmp-oap.json"
    tmp.write_text(json.dumps(oap))
    rc, out = run_cli(["propose-oap", "--from-file", str(tmp)],
                      env_extra={"AGENTCS_AS": "planning-1"})
    tmp.unlink(missing_ok=True)
    return (200 if rc == 0 else 400), {"output": out, "rc": rc}


ROUTES = {
    ("GET", "/api/state"): api_state,
    ("GET", "/api/agent-log"): api_agent_log,
    ("POST", "/api/init"): api_init,
    ("POST", "/api/run-agent"): api_run_agent,
    ("POST", "/api/approve-oap"): api_approve_oap,
    ("POST", "/api/review-arr"): api_review_arr,
    ("POST", "/api/demob"): api_demob,
    ("POST", "/api/scope-reduce"): api_scope_reduce,
    ("POST", "/api/propose-oap"): api_propose_oap,
}


# ---------------------------------------------------------------- HTML

INDEX_HTML = r"""<!doctype html>
<html><head><meta charset="utf-8"><title>AgentCS Dashboard</title>
<style>
  body{font:13px ui-monospace,SFMono-Regular,Menlo,monospace;margin:0;background:#111;color:#eee}
  header{padding:10px 16px;background:#000;border-bottom:1px solid #333;display:flex;align-items:center;gap:16px}
  header h1{font-size:14px;margin:0;color:#9cf}
  .badge{padding:2px 8px;border-radius:3px;font-weight:700;font-size:11px}
  .ph-NONE{background:#444;color:#aaa}
  .ph-PLANNING{background:#fa3;color:#000}
  .ph-MOBILIZE{background:#39f;color:#000}
  .ph-EXECUTE{background:#3c3;color:#000}
  .ph-DEMOB{background:#f63;color:#000}
  .ph-DEMOBILIZED{background:#666;color:#ddd}
  main{display:grid;grid-template-columns:240px 1fr 380px;gap:1px;background:#333;height:calc(100vh - 50px)}
  section{background:#111;padding:10px;overflow:auto}
  h2{font-size:11px;text-transform:uppercase;color:#888;margin:0 0 8px;letter-spacing:0.1em}
  .agent,.issue{border:1px solid #333;border-radius:3px;padding:8px;margin-bottom:6px;background:#1a1a1a}
  .agent .id,.issue .id{font-weight:700;color:#9cf}
  .agent .role{color:#aaa;font-size:11px}
  .status-active{color:#3c3}
  .status-spawned{color:#fa3}
  .status-running{color:#39f}
  .issue .state{font-size:10px;padding:1px 6px;border-radius:2px;background:#333;color:#ccc;float:right}
  .issue .state.closed{background:#3c3;color:#000}
  .issue .state.in-progress{background:#39f;color:#000}
  .issue .state.ready-for-review{background:#cc3;color:#000}
  .issue .state.pending-review{background:#fa3;color:#000}
  .crit{font-size:11px;color:#aaa;margin:4px 0 0 12px}
  .verif{font-size:11px;color:#3c3;margin-top:4px;padding:4px;background:#0a0a0a;border-left:2px solid #3c3;word-break:break-word}
  .audit{font-size:11px;line-height:1.5}
  .audit .ev{padding:2px 0;border-bottom:1px solid #1a1a1a}
  .audit .ts{color:#555}
  .audit .et{color:#9cf;font-weight:700}
  .audit .actor{color:#fa3}
  .audit .et-rejected,.audit .et-failed{color:#f63}
  .audit .et-passed,.audit .et-approved{color:#3c3}
  button{background:#333;color:#eee;border:1px solid #555;padding:6px 12px;font:inherit;cursor:pointer;border-radius:3px;margin:2px}
  button:hover:not(:disabled){background:#444}
  button:disabled{opacity:0.4;cursor:not-allowed}
  button.primary{background:#39f;color:#000;border-color:#39f;font-weight:700}
  button.primary:hover{background:#5af}
  button.danger{background:#f63;color:#000;border-color:#f63}
  .actions{padding:10px;background:#000;border-top:1px solid #333}
  textarea,input[type=text]{width:100%;background:#000;color:#eee;border:1px solid #444;padding:6px;font:inherit;border-radius:3px;box-sizing:border-box}
  textarea{min-height:140px;font-size:11px}
  .panel{margin-bottom:10px}
  .row{display:flex;gap:8px;align-items:center}
  .row > *{flex:1}
  details{margin:6px 0}
  summary{cursor:pointer;color:#9cf;font-size:11px}
  pre.log{background:#000;color:#9c9;padding:8px;overflow:auto;max-height:300px;font-size:11px;white-space:pre-wrap;word-break:break-word}
  .tag{display:inline-block;padding:1px 6px;background:#333;border-radius:2px;font-size:10px;margin-right:4px;color:#aaa}
  .empty{color:#666;font-style:italic;padding:8px;text-align:center}
  #toast{position:fixed;bottom:16px;right:16px;background:#39f;color:#000;padding:10px 16px;border-radius:4px;font-weight:700;display:none;z-index:1000}
  #toast.error{background:#f63}
</style></head><body>
<header>
  <h1>AgentCS</h1>
  <span id="proj">no project</span>
  <span id="phase" class="badge ph-NONE">—</span>
  <span id="meta"></span>
  <span style="flex:1"></span>
  <span id="active-runs"></span>
</header>
<main>
  <section>
    <h2>Agents</h2>
    <div id="agents"></div>
    <h2 style="margin-top:16px">Project Log</h2>
    <div id="agent-log-tabs"></div>
  </section>
  <section>
    <h2>Issues</h2>
    <div id="issues"></div>
    <h2 style="margin-top:16px">Agent Output</h2>
    <pre class="log" id="agent-log"><span class="empty">click an agent above to view its captured stdout</span></pre>
  </section>
  <section>
    <h2>Audit Log <span id="audit-count" style="color:#666;font-weight:normal"></span></h2>
    <div id="audit" class="audit"></div>
  </section>
</main>
<div class="actions" id="actions"></div>
<div id="toast"></div>
<script>
let SELECTED_AGENT = null;
let LAST_PHASE = null;

async function api(method, path, body) {
  const opts = { method, headers: {} };
  if (body) { opts.headers['Content-Type'] = 'application/json'; opts.body = JSON.stringify(body); }
  const r = await fetch(path, opts);
  return [r.status, await r.json()];
}

function toast(msg, isErr) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = isErr ? 'error' : '';
  t.style.display = 'block';
  setTimeout(() => t.style.display = 'none', 3000);
}

function el(tag, attrs, ...children) {
  const e = document.createElement(tag);
  for (const k in attrs) {
    if (k === 'class') e.className = attrs[k];
    else if (k.startsWith('on')) e.addEventListener(k.slice(2), attrs[k]);
    else e.setAttribute(k, attrs[k]);
  }
  for (const c of children) e.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
  return e;
}

async function runAgent(id, stepped) {
  const [s, r] = await api('POST', '/api/run-agent', { agent_id: id, stepped: !!stepped });
  if (s !== 200) toast(r.error || r.message, true); else toast(r.message);
  await refresh();
  SELECTED_AGENT = id;
}

async function refreshAgentLog() {
  if (!SELECTED_AGENT) return;
  const [s, r] = await api('GET', `/api/agent-log?agent=${encodeURIComponent(SELECTED_AGENT)}`);
  if (s === 200) {
    const log = document.getElementById('agent-log');
    log.textContent = r.log || '(no output yet)';
  }
}

async function refresh() {
  const [s, r] = await api('GET', '/api/state');
  if (s !== 200) return;
  const phase = r.state ? r.state.phase : 'NONE';

  document.getElementById('proj').textContent = r.active || '(no active project)';
  document.getElementById('phase').textContent = phase;
  document.getElementById('phase').className = 'badge ph-' + phase;
  document.getElementById('meta').textContent = r.state ? `period ${r.state.period_number} · risk ${r.state.risk}` : '';

  // agents
  const ag = document.getElementById('agents');
  ag.innerHTML = '';
  if (r.state) {
    for (const [id, info] of Object.entries(r.state.registry || {})) {
      const running = (r.runs || {})[id] && r.runs[id].running;
      const div = el('div', { class: 'agent' });
      div.appendChild(el('div', { class: 'id' }, id));
      div.appendChild(el('div', { class: 'role' }, info.role + ' · '));
      const status = el('span', { class: 'status-' + (running ? 'running' : info.status) }, running ? 'running…' : info.status);
      div.lastChild.appendChild(status);
      const btn = el('button', {
        onclick: () => runAgent(id, false),
        ...(running ? { disabled: '' } : {}),
      }, running ? '⟳' : '▶ run');
      const stepBtn = el('button', {
        onclick: () => runAgent(id, true),
        ...(running ? { disabled: '' } : {}),
      }, '▶ stepped');
      const viewBtn = el('button', {
        onclick: () => { SELECTED_AGENT = id; refreshAgentLog(); },
      }, 'log');
      const row = el('div', { class: 'row' }, btn, stepBtn, viewBtn);
      div.appendChild(row);
      ag.appendChild(div);
    }
  } else {
    ag.appendChild(el('div', { class: 'empty' }, 'no agents — initialize a project first'));
  }

  // active runs in header
  const runningIds = Object.entries(r.runs || {}).filter(([_, x]) => x.running).map(([k, _]) => k);
  document.getElementById('active-runs').innerHTML = runningIds.length
    ? '<span style="color:#39f">⟳ running: ' + runningIds.join(', ') + '</span>'
    : '';

  // issues
  const iss = document.getElementById('issues');
  iss.innerHTML = '';
  if (r.state) {
    const issues = Object.values(r.state.issues || {});
    if (issues.length === 0) {
      iss.appendChild(el('div', { class: 'empty' }, 'no issues yet'));
    }
    for (const i of issues) {
      const div = el('div', { class: 'issue' });
      div.appendChild(el('span', { class: 'state ' + i.state }, i.state));
      div.appendChild(el('div', { class: 'id' }, i.id + ' — ' + i.title));
      const tag = el('span', { class: 'tag' }, 'role: ' + (i.assigned_role || '—'));
      div.appendChild(tag);
      const critWrap = el('div');
      for (const c of (i.criteria || [])) {
        critWrap.appendChild(el('div', { class: 'crit' }, '✓ ' + c));
      }
      div.appendChild(critWrap);
      if (i.verification) {
        div.appendChild(el('div', { class: 'verif' }, 'verified: ' + i.verification));
      }
      iss.appendChild(div);
    }
  }

  // audit log
  const al = document.getElementById('audit');
  al.innerHTML = '';
  for (const ev of (r.audit || []).slice().reverse()) {
    const cls = ev.event_type.includes('rejected') || ev.event_type.includes('failed') ? 'et-rejected'
              : ev.event_type.includes('passed') || ev.event_type.includes('approved') ? 'et-passed' : 'et';
    const div = el('div', { class: 'ev' });
    div.appendChild(el('span', { class: 'ts' }, ev.ts.replace('T', ' ').slice(11, 19) + ' '));
    div.appendChild(el('span', { class: cls }, ev.event_type + ' '));
    div.appendChild(el('span', { class: 'actor' }, ev.actor));
    if (Object.keys(ev.payload || {}).length) {
      const summary = JSON.stringify(ev.payload).slice(0, 120);
      div.appendChild(el('div', { class: 'crit' }, summary));
    }
    al.appendChild(div);
  }
  document.getElementById('audit-count').textContent = '(' + (r.audit || []).length + ')';

  // contextual action panel
  renderActions(r);

  if (LAST_PHASE !== phase && LAST_PHASE !== null) toast('phase → ' + phase);
  LAST_PHASE = phase;
}

function renderActions(r) {
  const a = document.getElementById('actions');
  a.innerHTML = '';
  if (!r.active) {
    a.appendChild(el('h2', {}, 'Initialize a project'));
    const ta = el('textarea', { id: 'sow-input', placeholder: 'paste SOW JSON' });
    a.appendChild(ta);
    a.appendChild(el('button', { class: 'primary', onclick: async () => {
      const [s, x] = await api('POST', '/api/init', { sow: ta.value });
      if (s !== 200) toast(x.error || x.output, true); else { toast('project initiated'); refresh(); }
    }}, 'Init Project'));
    a.appendChild(el('button', { onclick: async () => {
      const r = await fetch('/example-sow').then(r => r.json());
      ta.value = JSON.stringify(r, null, 2);
    }}, 'Load example SOW'));
    return;
  }

  const s = r.state;

  if (s.proposed_oap) {
    a.appendChild(el('h2', {}, 'Proposed OAP awaiting approval'));
    const pre = el('pre', { class: 'log' });
    pre.textContent = JSON.stringify(s.proposed_oap, null, 2);
    a.appendChild(pre);
    a.appendChild(el('button', { class: 'primary', onclick: async () => {
      const [st, x] = await api('POST', '/api/approve-oap', {});
      if (st !== 200) toast(x.error || x.output, true); else { toast('OAP approved'); refresh(); }
    }}, '✓ Approve OAP'));
  }

  if (s.proposed_arr) {
    a.appendChild(el('h2', {}, 'Proposed ARR awaiting review'));
    const pre = el('pre', { class: 'log' });
    pre.textContent = JSON.stringify(s.proposed_arr, null, 2);
    a.appendChild(pre);
    const cmt = el('input', { type: 'text', placeholder: 'optional comment' });
    a.appendChild(cmt);
    const review = (decision) => async () => {
      const [st, x] = await api('POST', '/api/review-arr', { decision, comment: cmt.value });
      if (st !== 200) toast(x.error || x.output, true); else { toast('ARR ' + decision); refresh(); }
    };
    a.appendChild(el('button', { class: 'primary', onclick: review('accept') }, '✓ Accept'));
    a.appendChild(el('button', { onclick: review('accept-with-changes') }, 'Accept with changes'));
    a.appendChild(el('button', { class: 'danger', onclick: review('reject') }, '✗ Reject'));
  }

  if (s.phase === 'EXECUTE' && s.current_oap) {
    a.appendChild(el('h2', {}, 'Mid-OP scope changes'));
    const sel = el('select');
    for (const o of (s.current_oap.objectives || [])) {
      const opt = el('option', { value: o.id }); opt.textContent = `${o.id} — ${o.title}`;
      sel.appendChild(opt);
    }
    sel.style.background = '#000'; sel.style.color = '#eee'; sel.style.border = '1px solid #444';
    sel.style.padding = '6px'; sel.style.borderRadius = '3px';
    const reason = el('input', { type: 'text', placeholder: 'reason' });
    a.appendChild(el('div', { class: 'row' }, sel, reason));
    a.appendChild(el('button', { onclick: async () => {
      const [st, x] = await api('POST', '/api/scope-reduce', { objective_id: sel.value, reason: reason.value });
      if (st !== 200) toast(x.error || x.output, true); else { toast('scope reduced'); refresh(); }
    }}, '− Reduce scope (remove objective)'));
  }

  if (s.phase === 'DEMOB') {
    a.appendChild(el('h2', {}, 'Demobilize'));
    a.appendChild(el('div', { class: 'crit' }, 'Tear down the project sandbox. Registry cleared, credentials revoked, history archived.'));
    a.appendChild(el('button', { class: 'danger', onclick: async () => {
      if (!confirm('Demobilize project? This is the final step.')) return;
      const [st, x] = await api('POST', '/api/demob', {});
      if (st !== 200) toast(x.error || x.output, true); else { toast('project demobilized'); refresh(); }
    }}, '⚠ Demobilize'));
  }

  if (a.children.length === 0) {
    a.appendChild(el('div', { class: 'empty' },
      s.phase === 'PLANNING' ? 'Run planning-1 to draft the OAP.'
      : s.phase === 'MOBILIZE' || s.phase === 'EXECUTE' ? 'Run cos-1 (auto-cascades the OP) or run agents stepped.'
      : 'Project demobilized.'));
  }
}

// poll
refresh();
setInterval(refresh, 1500);
setInterval(refreshAgentLog, 1500);
</script>
</body></html>
"""


# Example SOW for the "Load example" button — read from disk so it stays in sync
def example_sow():
    p = HERE / "examples" / "sow.json"
    return json.loads(p.read_text()) if p.exists() else {}


# ---------------------------------------------------------------- HTTP

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_a, **_kw):
        return

    def _send(self, status, body, content_type="application/json"):
        if content_type == "application/json":
            payload = json.dumps(body).encode("utf-8")
        else:
            payload = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path, qs = parsed.path, urllib.parse.parse_qs(parsed.query)
        if path == "/" or path == "/index.html":
            return self._send(200, INDEX_HTML, content_type="text/html; charset=utf-8")
        if path == "/example-sow":
            return self._send(200, example_sow())
        fn = ROUTES.get(("GET", path))
        if not fn:
            return self._send(404, {"error": "not found"})
        status, body = fn(qs)
        return self._send(status, body)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        fn = ROUTES.get(("POST", parsed.path))
        if not fn:
            return self._send(404, {"error": "not found"})
        ln = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(ln) if ln else b""
        try:
            body = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            return self._send(400, {"error": "invalid JSON body"})
        status, resp = fn(body)
        return self._send(status, resp)


def main():
    print(f"AgentCS dashboard")
    print(f"  AGENTCS_HOME = {HOME}")
    print(f"  agentcs.py   = {AGENTCS_PY}")
    print(f"  serving      = http://{HOST}:{PORT}")
    print(f"  open in your browser; the human-checkpoint actions are buttons.")
    print()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")


if __name__ == "__main__":
    main()
