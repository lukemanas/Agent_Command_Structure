#!/usr/bin/env python3
"""AgentCS reference CLI — minimal implementation of the governance protocol.

Single-user, single-machine, file-based. Demonstrates protocol mechanics:
schema-validated SOW/OAP/ARR, project sandbox lifecycle, checkin gate,
role-gated issue transitions, scope-can-shrink-not-grow, verified-before-close,
JSONL audit log. No containers, no network, no real auth — agent identity is
simulated via the AGENTCS_AS environment variable.

Usage:
  AGENTCS_AS=human       python agentcs.py init --from-file examples/sow.json
  AGENTCS_AS=planning-1  python agentcs.py propose-oap --from-file examples/oap.json
  AGENTCS_AS=human       python agentcs.py approve-oap
  AGENTCS_AS=cos-1       python agentcs.py checkin --role cos --period 1 --risk low
  ...etc.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HOME = Path(os.environ.get("AGENTCS_HOME", Path.home() / ".agentcs"))
PROJECTS = HOME / "projects"
ACTIVE = HOME / "active"


# ---------------------------------------------------------------- utilities

def now():
    return datetime.now(timezone.utc).isoformat()


def project_dir(pid):
    return PROJECTS / pid


def load_state(pid):
    p = project_dir(pid) / "state.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def save_state(pid, state):
    p = project_dir(pid) / "state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=2))


def active_project():
    return ACTIVE.read_text().strip() if ACTIVE.exists() else None


def set_active(pid):
    HOME.mkdir(parents=True, exist_ok=True)
    ACTIVE.write_text(pid)


def fail(msg, code=1):
    sys.stderr.write(f"REJECTED: {msg}\n")
    sys.exit(code)


# ---------------------------------------------------------------- audit

AUDIT_EVENTS = {
    "project_initiated", "oap_proposed", "oap_approved", "oap_rejected",
    "agent_spawned", "checkin_attempted", "checkin_passed", "checkin_failed",
    "issue_created", "issue_transitioned", "issue_transition_rejected",
    "scope_reduced", "scope_expansion_rejected",
    "period_started", "period_ended",
    "arr_proposed", "arr_approved", "arr_rejected",
    "verification_recorded", "sandbox_destroyed",
}


def audit(pid, event_type, actor, payload=None):
    if event_type not in AUDIT_EVENTS:
        raise ValueError(f"unknown audit event: {event_type}")
    pdir = project_dir(pid)
    pdir.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": now(),
        "event_type": event_type,
        "project_id": pid,
        "actor": actor,
        "payload": payload or {},
    }
    with open(pdir / "audit.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")


# ---------------------------------------------------------------- identity

def caller():
    """Return (agent_id, effective_role, status). Human is implicit if AGENTCS_AS unset."""
    aid = os.environ.get("AGENTCS_AS", "human")
    if aid == "human":
        return "human", "human", "active"
    pid = active_project()
    if not pid:
        return aid, "unknown", "spawned"
    state = load_state(pid)
    info = state.get("registry", {}).get(aid) if state else None
    if not info:
        return aid, "unknown", "spawned"
    return aid, info["role"], info["status"]


def require_active(*roles):
    """Caller must be active and hold one of the named roles. Returns agent_id."""
    aid, role, status = caller()
    if role not in roles:
        fail(f"role '{role}' cannot perform this action (need one of: {', '.join(roles)})")
    if status != "active":
        fail(f"agent '{aid}' is '{status}', not active — must pass checkin first")
    return aid


# ---------------------------------------------------------------- schemas

def validate_sow(sow):
    for k in ("project_title", "objective", "project_id", "risk_classification"):
        if k not in sow:
            fail(f"SOW missing required field: {k}")
    if sow["risk_classification"] not in ("low", "high"):
        fail("SOW.risk_classification must be 'low' or 'high'")


def validate_oap(oap):
    for k in ("period_number", "duration", "objectives", "assignments"):
        if k not in oap:
            fail(f"OAP missing required field: {k}")
    if not oap["objectives"]:
        fail("OAP must have at least one objective")
    seen = set()
    for obj in oap["objectives"]:
        for k in ("id", "title", "criteria"):
            if k not in obj:
                fail(f"objective missing required field: {k}")
        if not obj["criteria"]:
            fail(f"objective {obj['id']} must have at least one acceptance criterion")
        if obj["id"] in seen:
            fail(f"duplicate objective id: {obj['id']}")
        seen.add(obj["id"])
    for asn in oap["assignments"]:
        for k in ("role", "objective_ids", "skill"):
            if k not in asn:
                fail(f"assignment missing required field: {k}")


def validate_arr(arr):
    for k in ("period_number", "status", "objectives_outcome", "human_decision"):
        if k not in arr:
            fail(f"ARR missing required field: {k}")
    if arr["status"] not in ("complete", "partial", "aborted"):
        fail("ARR.status must be complete | partial | aborted")
    if arr["human_decision"] not in ("accept", "reject", "accept-with-changes", "pending"):
        fail("ARR.human_decision invalid")


# ---------------------------------------------------------------- verbs

def cmd_init(args):
    """Human runs initiation. Schema is the gate."""
    aid, role, _ = caller()
    if role != "human":
        fail("only human can initiate a project")
    if args.from_file:
        sow = json.loads(Path(args.from_file).read_text())
    else:
        sow = {
            "project_title": input("Project title: "),
            "objective": input("Objective: "),
            "project_id": input("Project ID (unique): "),
            "risk_classification": input("Risk (low/high): ").strip(),
        }
    validate_sow(sow)
    pid = sow["project_id"]
    if project_dir(pid).exists():
        fail(f"project '{pid}' already exists")
    pdir = project_dir(pid)
    (pdir / "history").mkdir(parents=True)
    (pdir / "sow.json").write_text(json.dumps(sow, indent=2))
    state = {
        "project_id": pid,
        "phase": "PLANNING",
        "period_number": 0,
        "risk": sow["risk_classification"],
        "registry": {
            # Planning agent auto-active at spawn (no COP to check against yet).
            "planning-1": {"role": "planner", "skill": "planner", "status": "active"},
        },
        "issues": {},
        "current_oap": None,
        "proposed_oap": None,
        "proposed_arr": None,
    }
    save_state(pid, state)
    set_active(pid)
    audit(pid, "project_initiated", aid, {"sow": sow})
    audit(pid, "agent_spawned", "orchestrator",
          {"agent_id": "planning-1", "role": "planner", "auto_active": True})
    print(f"project '{pid}' initiated. phase=PLANNING. planning-1 spawned (active).")


def cmd_status(_args):
    pid = active_project()
    if not pid:
        fail("no active project")
    s = load_state(pid)
    print(f"project: {pid}")
    print(f"phase:   {s['phase']}")
    print(f"period:  {s['period_number']}")
    print(f"risk:    {s['risk']}")
    print(f"agents:  {len(s['registry'])}")
    print(f"issues:  {len(s['issues'])}")
    if s.get("current_oap"):
        oap = s["current_oap"]
        print(f"\ncurrent OAP — period {oap['period_number']}, duration {oap['duration']}")
        for obj in oap["objectives"]:
            iid = f"issue-{obj['id']}"
            st = s["issues"].get(iid, {}).get("state", "—")
            print(f"  {obj['id']}: {obj['title']} [{st}]")
    if s.get("proposed_oap"):
        print(f"\n[proposed OAP awaiting human approval]")
    if s.get("proposed_arr"):
        print(f"\n[proposed ARR awaiting human review]")


def cmd_propose_oap(args):
    aid = require_active("planner")
    pid = active_project()
    s = load_state(pid)
    oap = json.loads(Path(args.from_file).read_text())
    validate_oap(oap)
    s["proposed_oap"] = oap
    save_state(pid, s)
    audit(pid, "oap_proposed", aid, {"period": oap["period_number"]})
    print(f"OAP for period {oap['period_number']} proposed ({len(oap['objectives'])} objectives).")
    print("→ human: run `agentcs approve-oap`")


def cmd_approve_oap(_args):
    aid, role, _ = caller()
    if role != "human":
        fail("only human can approve OAP")
    pid = active_project()
    s = load_state(pid)
    oap = s.get("proposed_oap")
    if not oap:
        fail("no proposed OAP to approve")
    validate_oap(oap)
    pdir = project_dir(pid)
    s["current_oap"] = oap
    s["proposed_oap"] = None
    s["period_number"] = oap["period_number"]
    s["phase"] = "MOBILIZE"
    # Spawn the CoS implied by the OAP's assignments. Status starts as 'spawned' —
    # CoS must pass the checkin gate before it can act.
    cos_assn = next((a for a in oap["assignments"] if a["role"] == "cos"), None)
    if cos_assn and "cos-1" not in s["registry"]:
        s["registry"]["cos-1"] = {"role": "cos", "skill": cos_assn["skill"], "status": "spawned"}
        audit(pid, "agent_spawned", "orchestrator", {"agent_id": "cos-1", "role": "cos"})
    (pdir / "oap.json").write_text(json.dumps(oap, indent=2))
    save_state(pid, s)
    audit(pid, "oap_approved", aid, {"period": oap["period_number"]})
    audit(pid, "period_started", "orchestrator", {"period": oap["period_number"]})
    print(f"OAP approved. period {oap['period_number']} started → MOBILIZE.")
    print("→ cos-1 spawned (must pass checkin before acting)")


def cmd_checkin(args):
    """Mechanical validation against COP. Hard gate."""
    aid, _, _ = caller()
    pid = active_project()
    s = load_state(pid)
    if aid not in s["registry"]:
        audit(pid, "checkin_failed", aid, {"reason": "not in registry"})
        fail(f"agent '{aid}' not in registry")
    declared = {
        "role": args.role,
        "period_number": int(args.period),
        "risk": args.risk,
        "objective_ids": [o for o in args.objectives.split(",") if o] if args.objectives else [],
    }
    audit(pid, "checkin_attempted", aid, declared)
    expected = s["registry"][aid]
    if declared["role"] != expected["role"]:
        audit(pid, "checkin_failed", aid, {"reason": "role mismatch", "expected": expected["role"]})
        fail(f"role mismatch: declared '{declared['role']}', registry has '{expected['role']}'")
    if declared["period_number"] != s["period_number"]:
        audit(pid, "checkin_failed", aid, {"reason": "period mismatch", "expected": s["period_number"]})
        fail(f"period mismatch: declared {declared['period_number']}, current is {s['period_number']}")
    if declared["risk"] != s["risk"]:
        audit(pid, "checkin_failed", aid, {"reason": "risk mismatch", "expected": s["risk"]})
        fail(f"risk mismatch: declared '{declared['risk']}', project is '{s['risk']}'")
    oap = s["current_oap"]
    if oap is None:
        fail("no OAP — cannot validate objectives")
    valid_ids = {o["id"] for o in oap["objectives"]}
    for oid in declared["objective_ids"]:
        if oid not in valid_ids:
            audit(pid, "checkin_failed", aid, {"reason": f"unknown objective_id: {oid}"})
            fail(f"unknown objective_id: {oid}")
    s["registry"][aid]["status"] = "active"
    s["registry"][aid]["objective_ids"] = declared["objective_ids"]
    save_state(pid, s)
    audit(pid, "checkin_passed", aid, declared)
    print(f"checkin passed. agent '{aid}' now active.")


def cmd_spawn(args):
    """CoS spawns a worker or supervisor."""
    aid = require_active("cos")
    pid = active_project()
    s = load_state(pid)
    new_id = args.agent_id
    if new_id in s["registry"]:
        fail(f"agent '{new_id}' already registered")
    if args.role not in ("worker", "supervisor"):
        fail("can only spawn workers or supervisors")
    s["registry"][new_id] = {"role": args.role, "skill": args.skill, "status": "spawned"}
    save_state(pid, s)
    audit(pid, "agent_spawned", aid, {"agent_id": new_id, "role": args.role, "skill": args.skill})
    print(f"agent '{new_id}' spawned with role '{args.role}'. must pass checkin before acting.")


def cmd_create_issues(_args):
    """CoS translates OAP objectives into issue records → phase EXECUTE."""
    aid = require_active("cos")
    pid = active_project()
    s = load_state(pid)
    oap = s.get("current_oap")
    if not oap:
        fail("no current OAP")
    created = 0
    for obj in oap["objectives"]:
        iid = f"issue-{obj['id']}"
        if iid in s["issues"]:
            continue
        assn = next((a for a in oap["assignments"]
                     if obj["id"] in a.get("objective_ids", []) and a["role"] != "cos"), None)
        s["issues"][iid] = {
            "id": iid,
            "objective_id": obj["id"],
            "title": obj["title"],
            "criteria": obj["criteria"],
            "state": "open",
            "assigned_role": assn["role"] if assn else None,
            "verification": None,
        }
        audit(pid, "issue_created", aid, {"issue_id": iid, "objective_id": obj["id"]})
        created += 1
    s["phase"] = "EXECUTE"
    save_state(pid, s)
    print(f"created {created} issue(s). phase → EXECUTE.")


# Role-gated transition matrix: from_state → {to_state: [allowed_roles]}
TRANSITIONS = {
    "open":              {"in-progress":      ["worker"]},
    "in-progress":       {"ready-for-review": ["worker"]},
    "ready-for-review":  {"pending-review":   ["supervisor", "cos"]},
    "pending-review":    {"closed":           ["cos"],
                          "in-progress":      ["cos"]},
}


def cmd_transition(args):
    aid, role, status = caller()
    pid = active_project()
    s = load_state(pid)
    iid = args.issue_id
    if iid not in s["issues"]:
        fail(f"unknown issue: {iid}")
    issue = s["issues"][iid]
    target = args.to_state
    if status != "active" and role != "human":
        audit(pid, "issue_transition_rejected", aid,
              {"issue": iid, "reason": "agent not active"})
        fail(f"agent '{aid}' is '{status}', not active — must pass checkin first")
    allowed = TRANSITIONS.get(issue["state"], {}).get(target)
    if allowed is None:
        audit(pid, "issue_transition_rejected", aid,
              {"issue": iid, "from": issue["state"], "to": target, "reason": "invalid transition"})
        fail(f"invalid transition: {issue['state']} → {target}")
    if role not in allowed:
        audit(pid, "issue_transition_rejected", aid,
              {"issue": iid, "from": issue["state"], "to": target,
               "reason": f"role '{role}' not allowed", "allowed": allowed})
        fail(f"role '{role}' cannot transition {issue['state']} → {target} (allowed: {allowed})")
    if target == "closed" and not issue.get("verification"):
        audit(pid, "issue_transition_rejected", aid,
              {"issue": iid, "reason": "verified-before-close: no verification recorded"})
        fail("cannot close: verification is empty (verified-before-close)")
    prev = issue["state"]
    issue["state"] = target
    save_state(pid, s)
    audit(pid, "issue_transitioned", aid, {"issue": iid, "from": prev, "to": target})
    print(f"{iid}: {prev} → {target}")


def cmd_verify(args):
    """Worker or supervisor records verification evidence on an issue."""
    aid = require_active("worker", "supervisor", "cos")
    pid = active_project()
    s = load_state(pid)
    iid = args.issue_id
    if iid not in s["issues"]:
        fail(f"unknown issue: {iid}")
    s["issues"][iid]["verification"] = args.method
    save_state(pid, s)
    audit(pid, "verification_recorded", aid, {"issue": iid, "method": args.method})
    print(f"{iid}: verification recorded — {args.method}")


def cmd_scope(args):
    """Reduce or attempt to add scope. Add is always rejected — the protocol's invariant."""
    aid, role, _ = caller()
    pid = active_project()
    s = load_state(pid)
    if args.action == "add":
        audit(pid, "scope_expansion_rejected", aid, {"attempted_objective": args.objective_id})
        fail("scope can shrink, never grow. file a new OAP for additions.")
    if args.action == "reduce":
        if role != "human":
            fail("only human can reduce scope")
        oap = s["current_oap"]
        before = len(oap["objectives"])
        oap["objectives"] = [o for o in oap["objectives"] if o["id"] != args.objective_id]
        if len(oap["objectives"]) == before:
            fail(f"objective '{args.objective_id}' not in current OAP")
        for iid, issue in list(s["issues"].items()):
            if issue["objective_id"] == args.objective_id:
                del s["issues"][iid]
        save_state(pid, s)
        audit(pid, "scope_reduced", aid,
              {"objective_id": args.objective_id, "reason": args.reason or ""})
        print(f"scope reduced — removed objective '{args.objective_id}'.")


def cmd_propose_arr(_args):
    """CoS produces ARR. Outcomes are auto-derived from issue state."""
    aid = require_active("cos")
    pid = active_project()
    s = load_state(pid)
    oap = s["current_oap"]
    outcomes = []
    for obj in oap["objectives"]:
        iid = f"issue-{obj['id']}"
        issue = s["issues"].get(iid)
        if not issue:
            outcome, verification = "not-attempted", ""
        elif issue["state"] == "closed":
            outcome, verification = "verified", issue.get("verification") or ""
        elif issue["state"] in ("in-progress", "ready-for-review", "pending-review"):
            outcome, verification = "partial", issue.get("verification") or ""
        else:
            outcome, verification = "not-attempted", ""
        outcomes.append({"id": obj["id"], "outcome": outcome,
                         "verification": verification, "notes": ""})
    incomplete = [o["id"] for o in outcomes if o["outcome"] != "verified"]
    arr = {
        "period_number": s["period_number"],
        "status": "complete" if not incomplete else "partial",
        "objectives_outcome": outcomes,
        "incomplete": incomplete,
        "scope_changes": [],
        "performance": [],
        "risks_observed": [],
        "recommendations_for_next_oap": [],
        "human_decision": "pending",
        "human_comments": "",
    }
    s["proposed_arr"] = arr
    save_state(pid, s)
    audit(pid, "arr_proposed", aid,
          {"period": s["period_number"], "status": arr["status"], "incomplete": incomplete})
    print(f"ARR proposed. status={arr['status']}, incomplete={len(incomplete)}.")
    print("→ human: run `agentcs review-arr accept|reject|accept-with-changes`")


def cmd_review_arr(args):
    aid, role, _ = caller()
    if role != "human":
        fail("only human can review ARR")
    pid = active_project()
    s = load_state(pid)
    arr = s.get("proposed_arr")
    if not arr:
        fail("no proposed ARR")
    if args.decision not in ("accept", "reject", "accept-with-changes"):
        fail("decision must be: accept | reject | accept-with-changes")
    arr["human_decision"] = args.decision
    arr["human_comments"] = args.comment or ""
    validate_arr(arr)
    pdir = project_dir(pid)
    period_dir = pdir / "history" / f"period-{s['period_number']}"
    period_dir.mkdir(parents=True, exist_ok=True)
    (period_dir / "arr.json").write_text(json.dumps(arr, indent=2))
    s["proposed_arr"] = None
    if args.decision == "reject":
        audit(pid, "arr_rejected", aid, {"comments": args.comment or ""})
        print("ARR rejected. CoS must revise.")
    else:
        audit(pid, "arr_approved", aid, {"decision": args.decision})
        audit(pid, "period_ended", "orchestrator", {"period": s["period_number"]})
        s["phase"] = "DEMOB"
        print(f"ARR accepted. period {s['period_number']} ended → DEMOB.")
    save_state(pid, s)


def cmd_demob(_args):
    aid, role, _ = caller()
    if role != "human":
        fail("only human can demobilize")
    pid = active_project()
    s = load_state(pid)
    if s["phase"] != "DEMOB":
        fail(f"cannot demob from phase '{s['phase']}'")
    pdir = project_dir(pid)
    final_dir = pdir / "history" / "final"
    final_dir.mkdir(parents=True, exist_ok=True)
    for fname in ("sow.json", "oap.json"):
        f = pdir / fname
        if f.exists():
            f.rename(final_dir / fname)
    s["phase"] = "DEMOBILIZED"
    s["registry"] = {}
    save_state(pid, s)
    audit(pid, "sandbox_destroyed", aid, {})
    if ACTIVE.exists() and ACTIVE.read_text().strip() == pid:
        ACTIVE.unlink()
    print(f"project '{pid}' demobilized. registry cleared, credentials revoked.")


def cmd_cop(args):
    """Role-filtered situational view computed at read time."""
    pid = active_project()
    s = load_state(pid)
    aid, my_role, _ = caller()
    role = args.role or my_role
    print(f"=== COP (viewing-as: {role}) ===")
    print(f"project={pid}  phase={s['phase']}  period={s['period_number']}  risk={s['risk']}")
    if role in ("human", "cos", "planner"):
        print(f"\nagents ({len(s['registry'])}):")
        for k, v in s["registry"].items():
            print(f"  {k:15s} role={v['role']:10s} status={v['status']}")
        print(f"\nissues ({len(s['issues'])}):")
        for iid, issue in s["issues"].items():
            mark = "✓" if issue.get("verification") else " "
            print(f"  {iid:25s} [{issue['state']:18s}] {mark} {issue['title']}")
    else:
        my_obj_ids = s["registry"].get(aid, {}).get("objective_ids", [])
        print(f"\nyour assignments ({len(my_obj_ids)}):")
        for iid, issue in s["issues"].items():
            if issue["objective_id"] in my_obj_ids:
                print(f"  {iid:25s} [{issue['state']:18s}] {issue['title']}")


def cmd_run(args):
    """Launch a real Claude Code agent for a registered role.

    The agent runs as a subprocess of the orchestrator with AGENTCS_AS bound to
    its registered identity. The agent's prompt is composed of (a) the skill
    file for its role, (b) a JSON context block with the SOW/OAP/issues, and
    (c) instructions for invoking the AgentCS CLI to take protocol actions.
    """
    aid = args.agent_id
    pid = active_project()
    if not pid:
        fail("no active project")
    s = load_state(pid)
    if aid not in s["registry"]:
        fail(f"agent '{aid}' not in registry; spawn it first")
    info = s["registry"][aid]
    role = info["role"]

    skills_dir = Path(__file__).resolve().parent / "skills"
    skill_file = skills_dir / f"{role}.md"
    if not skill_file.exists():
        fail(f"no skill file for role '{role}' (looked at {skill_file})")
    skill = skill_file.read_text()

    sow_path = project_dir(pid) / "sow.json"
    sow = json.loads(sow_path.read_text()) if sow_path.exists() else None
    oap = s.get("current_oap")
    agentcs_py = Path(__file__).resolve()

    your_assignments = []
    if oap:
        your_assignments = [a for a in oap.get("assignments", []) if a.get("role") == role]
    issues_for_you = [i for i in s["issues"].values() if i.get("assigned_role") == role]

    mode = "stepped" if args.stepped else "auto"

    context_block = json.dumps({
        "agent_id": aid,
        "role": role,
        "project_id": pid,
        "phase": s["phase"],
        "period_number": s["period_number"],
        "risk": s["risk"],
        "mode": mode,
        "sow": sow,
        "oap": oap,
        "your_assignments": your_assignments,
        "issues_for_you": issues_for_you,
        "active_agents": [{"id": k, "role": v["role"], "status": v["status"]} for k, v in s["registry"].items()],
    }, indent=2)

    prompt = f"""You are agent `{aid}` operating under the AgentCS governance protocol.

# Skill instructions

{skill.replace("<agentcs_path>", str(agentcs_py))}

# Current context

```json
{context_block}
```

# Taking protocol actions

Run `python3 {agentcs_py}` with the verb you want. Your identity (`AGENTCS_AS={aid}`) is already set in your environment — don't override it.

Useful verbs:
- `python3 {agentcs_py} status`
- `python3 {agentcs_py} cop`
- `python3 {agentcs_py} checkin --role <role> --period <N> --risk <tier> [--objectives <ids>]`
- `python3 {agentcs_py} transition <issue_id> <state>`
- `python3 {agentcs_py} verify <issue_id> "<evidence>"`
- `python3 {agentcs_py} spawn <agent_id> --role <role> --skill <skill>`
- `python3 {agentcs_py} create-issues`
- `python3 {agentcs_py} run <agent_id>` (CoS only — launch a worker)
- `python3 {agentcs_py} propose-arr` (CoS only)
- `python3 {agentcs_py} propose-oap --from-file <path>` (planner only)

The orchestrator enforces the protocol's invariants. If you try to do something out of role, out of order, or with stale state, your action will be rejected and the rejection will be in the audit log. Read rejection messages carefully — they tell you what's wrong.

When you have completed your assignment per the skill, exit.
"""

    if args.dry_run:
        sep = "─" * 60
        print(f"{sep}\nprompt for agent '{aid}' (role: {role}, {len(prompt)} chars)\n{sep}\n")
        print(prompt)
        print(f"\n{sep}\n[dry-run] AGENTCS_AS={aid} claude -p <prompt>")
        return

    if not shutil.which("claude"):
        fail("`claude` CLI not found in PATH. Install Claude Code, or use --dry-run to preview the prompt.")

    env = os.environ.copy()
    env["AGENTCS_AS"] = aid

    extra_flags = os.environ.get("AGENTCS_CLAUDE_FLAGS", "--permission-mode acceptEdits").split()
    cmd = ["claude", "-p", prompt, *extra_flags]

    # Run from the reference root so `./demo-service/...` and other relative
    # paths in the OAP resolve consistently regardless of where the user
    # invoked agentcs from.
    agent_cwd = Path(__file__).resolve().parent

    print(f"→ launching Claude Code as '{aid}' (role: {role}). prompt={len(prompt)} chars. cwd={agent_cwd}")
    if args.verbose:
        print(f"   command: claude -p <prompt> {' '.join(extra_flags)}")
        print(f"   env: AGENTCS_AS={aid}")
    result = subprocess.run(cmd, env=env, cwd=agent_cwd)
    print(f"← agent '{aid}' exited (code={result.returncode}).")


def cmd_audit(args):
    pid = args.project or active_project()
    if not pid:
        fail("no active project (pass --project <id> to read a demobilized project's log)")
    f = project_dir(pid) / "audit.jsonl"
    if not f.exists():
        return
    for line in f.read_text().splitlines():
        r = json.loads(line)
        payload = json.dumps(r.get("payload", {}), separators=(",", ":"))
        print(f"{r['ts']}  {r['event_type']:30s}  {r['actor']:15s}  {payload}")


# ---------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(prog="agentcs", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("init", help="human: create project from SOW (requires schema-valid SOW)")
    sp.add_argument("--from-file", help="path to SOW JSON; if omitted, prompt interactively")
    sp.set_defaults(fn=cmd_init)

    sub.add_parser("status", help="show current project state").set_defaults(fn=cmd_status)

    sp = sub.add_parser("propose-oap", help="planner: write a draft OAP")
    sp.add_argument("--from-file", required=True)
    sp.set_defaults(fn=cmd_propose_oap)

    sub.add_parser("approve-oap", help="human: approve the proposed OAP").set_defaults(fn=cmd_approve_oap)

    sp = sub.add_parser("checkin", help="agent: declare orientation (mechanical gate)")
    sp.add_argument("--role", required=True)
    sp.add_argument("--period", required=True)
    sp.add_argument("--risk", required=True)
    sp.add_argument("--objectives", default="", help="comma-separated objective IDs")
    sp.set_defaults(fn=cmd_checkin)

    sp = sub.add_parser("spawn", help="cos: spawn a worker or supervisor")
    sp.add_argument("agent_id")
    sp.add_argument("--role", required=True, choices=["worker", "supervisor"])
    sp.add_argument("--skill", required=True)
    sp.set_defaults(fn=cmd_spawn)

    sub.add_parser("create-issues", help="cos: create issues from OAP → phase EXECUTE").set_defaults(fn=cmd_create_issues)

    sp = sub.add_parser("transition", help="role-gated issue state transition")
    sp.add_argument("issue_id")
    sp.add_argument("to_state")
    sp.set_defaults(fn=cmd_transition)

    sp = sub.add_parser("verify", help="record verification evidence on an issue")
    sp.add_argument("issue_id")
    sp.add_argument("method")
    sp.set_defaults(fn=cmd_verify)

    sp = sub.add_parser("scope", help="reduce scope or attempt to add (add is rejected)")
    sp.add_argument("action", choices=["reduce", "add"])
    sp.add_argument("objective_id")
    sp.add_argument("--reason")
    sp.set_defaults(fn=cmd_scope)

    sub.add_parser("propose-arr", help="cos: propose an ARR (auto-derived from issue state)").set_defaults(fn=cmd_propose_arr)

    sp = sub.add_parser("review-arr", help="human: approve or reject ARR")
    sp.add_argument("decision", choices=["accept", "reject", "accept-with-changes"])
    sp.add_argument("--comment")
    sp.set_defaults(fn=cmd_review_arr)

    sub.add_parser("demob", help="human: tear down project sandbox").set_defaults(fn=cmd_demob)

    sp = sub.add_parser("cop", help="role-filtered situational view")
    sp.add_argument("--role")
    sp.set_defaults(fn=cmd_cop)

    sp = sub.add_parser("audit", help="dump audit log")
    sp.add_argument("--project", help="project id (defaults to active project)")
    sp.set_defaults(fn=cmd_audit)

    sp = sub.add_parser("run", help="launch a real Claude Code agent for a registered role")
    sp.add_argument("agent_id")
    sp.add_argument("--dry-run", action="store_true", help="print the prompt without launching Claude Code")
    sp.add_argument("--verbose", action="store_true", help="print the launch command")
    sp.add_argument("--stepped", action="store_true",
                    help="ask the agent to stop at handoff points and let the human drive next-agent invocation; default is auto-cascade")
    sp.set_defaults(fn=cmd_run)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
