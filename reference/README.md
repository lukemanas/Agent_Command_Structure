# AgentCS reference CLI

Minimal Python implementation of the AgentCS governance protocol. Single user, single machine, file-based. Demonstrates the protocol's enforcement points end-to-end.

## What this proves

| Protocol element | How the CLI demonstrates it |
|---|---|
| Schema validation as the gate | `init` rejects malformed SOWs; `propose-oap` rejects malformed OAPs; `review-arr` rejects malformed ARRs. |
| Project sandbox lifecycle | `~/.agentcs/projects/<id>/` *is* the sandbox. `demob` clears the registry and archives state. |
| Identity & authentication boundary | Caller identity is `AGENTCS_AS`; every privileged action is bound to a registry entry. (Real auth is out of scope for this minimal demo.) |
| Checkin gate (mechanical) | `checkin` rejects on role/period/risk/objective-id mismatch against the OAP. |
| Role-gated state transitions | `transition` consults a static role/state matrix and rejects unauthorized callers. |
| Verified-before-close | `transition X closed` rejects if `verification` is empty. |
| Scope-can-shrink-not-grow | `scope add` always rejects; `scope reduce` is human-only. |
| Human at the exits | `init`, `approve-oap`, `scope reduce`, `review-arr`, `demob` all require role=human. |
| Audit trail | Every governance action writes a typed JSONL event to `audit.jsonl`. |

## Quickstart

```bash
cd examples
bash demo.sh
```

This runs the full lifecycle including expected rejections — checkin failures, premature actions, verified-before-close violations, scope-expansion attempts. Each rejection is the protocol enforcing an invariant.

## Manual walkthrough

```bash
# isolate state for the demo
export AGENTCS_HOME=$PWD/.acs-demo
alias acs='python3 agentcs.py'

# 1. human initiation
acs init --from-file examples/sow.json
acs status

# 2. planner drafts OAP, human approves
AGENTCS_AS=planning-1 acs propose-oap --from-file examples/oap.json
acs approve-oap

# 3. CoS passes the gate, spawns crew, creates issues
AGENTCS_AS=cos-1 acs checkin --role cos --period 1 --risk low
AGENTCS_AS=cos-1 acs spawn worker-1 --role worker --skill worker
AGENTCS_AS=cos-1 acs create-issues

# 4. worker checks in and executes
AGENTCS_AS=worker-1 acs checkin --role worker --period 1 --risk low --objectives obj-1,obj-2
AGENTCS_AS=worker-1 acs transition issue-obj-1 in-progress
AGENTCS_AS=worker-1 acs verify issue-obj-1 "pytest passed"
AGENTCS_AS=worker-1 acs transition issue-obj-1 ready-for-review

# 5. CoS reviews, closes
AGENTCS_AS=cos-1 acs transition issue-obj-1 pending-review
AGENTCS_AS=cos-1 acs transition issue-obj-1 closed

# 6. demob
AGENTCS_AS=cos-1 acs propose-arr
acs review-arr accept
acs demob

# 7. inspect audit
acs audit
```

## Identity model

The CLI uses `AGENTCS_AS=<agent_id>` to simulate which agent is invoking. Identity is bound to a registry entry created by `init`, `approve-oap`, or `spawn`. Without `AGENTCS_AS`, the caller is `human`.

This is **not** authentication — it's the role-binding semantics the protocol requires, demonstrated mechanically. A production implementation would replace this with a cryptographic binding (per the protocol's identity & authentication boundary).

## State layout

```
$AGENTCS_HOME/
  active                    # current project ID
  projects/
    <project-id>/
      sow.json              # original SOW (archived to history/final/ at demob)
      oap.json              # current OAP (archived at demob)
      state.json            # phase, period, registry, issues, drafts
      audit.jsonl           # append-only JSONL audit log
      history/
        period-1/
          arr.json          # archived ARR per period
        final/              # SOW + OAP at demob
```

## Running with real Claude Code agents

The `run` verb launches a real Claude Code subprocess for any registered agent. The agent gets a prompt assembled from `skills/<role>.md` + a JSON context block + the path to the AgentCS CLI. Its `AGENTCS_AS` is bound so every CLI call it makes is attributed to that agent in the audit log.

Requires `claude` in your PATH (Claude Code installed). Otherwise use `--dry-run` to preview the prompt.

```bash
export AGENTCS_HOME=$PWD/.acs-demo
alias acs='python3 agentcs.py'

# 1. human initiates
acs init --from-file examples/sow.json

# 2. real planning agent drafts OAP
acs run planning-1                  # launches Claude Code, planner skill loaded
# (preview without burning tokens:)
acs run planning-1 --dry-run

# 3. human reviews proposed OAP and approves
acs status                          # shows [proposed OAP awaiting human approval]
acs approve-oap                     # CoS spawns

# 4. real CoS runs the OP — auto-cascade by default
acs run cos-1                       # CoS launches workers itself, then reviews and proposes ARR
# or, for a step-by-step screencast where you narrate each agent:
#   acs run cos-1 --stepped         # CoS exits after creating issues; you launch each worker
#   acs run worker-1                # worker does the work, moves issues to ready-for-review
#   acs run cos-1 --stepped         # CoS resumes, reviews, closes, proposes ARR

# 5. human reviews ARR
acs review-arr accept

# 6. demob
acs demob

# 7. inspect attributed audit log
acs audit --project demo-001
```

The audit log will show `oap_proposed` attributed to `planning-1`, `checkin_passed` to `cos-1`, `verification_recorded` to `worker-1`, etc. — not to `human`. That's the protocol functioning with real LLM agents inside it.

You can override the Claude Code flags via env var:
```bash
AGENTCS_CLAUDE_FLAGS="--permission-mode bypassPermissions" acs run cos-1
```
Default is `--permission-mode acceptEdits`.

### Skills

Three role skills ship with this reference:

- `skills/planner.md` — drafts the OAP from the SOW; submits via `propose-oap`
- `skills/cos.md` — branches on `mode`: in `auto` it runs the entire OP including nested worker invocations; in `stepped` it exits at the worker handoff and resumes after the human runs workers
- `skills/worker.md` — checks in, executes assigned issues, records verification, moves to ready-for-review

Each skill explicitly enumerates what the agent **cannot** do — the protocol's invariants as constraints the agent reads. The orchestrator enforces the same invariants regardless of whether the agent honors them, so bad agents get rejected and the rejection lands in the audit log.

### Mode (CoS only)

The `run` verb takes an optional `--stepped` flag, which sets `"mode": "stepped"` in the agent's context block. The CoS skill reads this and chooses behavior:

| Mode | What CoS does | Best for |
|---|---|---|
| `auto` (default) | One `run cos-1` invocation drives the entire OP: checkin → spawn workers → create issues → launch workers as nested subprocesses → review → close → propose ARR | "It just works" demo; minimum operator steps |
| `stepped` | CoS exits after creating issues. Human runs each worker explicitly. Human re-runs `cos-1 --stepped` to resume into review and ARR. | Screencasts where you narrate each agent's actions; debugging |

Verified end-to-end: in auto mode, one `run cos-1` after `init` + `approve-oap` produces a fully closed OP with attributed audit trail across cos-1 (manager actions) and worker-1 (execution actions).

## What's intentionally out of scope (for v0)

- Containers / sandbox isolation (filesystem dirs stand in)
- Network ACLs (single CLI process)
- Vault / credential mounting (registry status is the proxy)
- Cryptographic identity (env var binding)
- Multi-OP project plans (single OP only)
- Supervisor layer (CoS + workers only)
- Real Claude/Codex/Gemini agent processes (CLI invocations stand in)

These are all implementation upgrades on a working protocol. The point of this build is that the *protocol mechanics* — schema gates, checkin gate, role-gated transitions, verified-before-close, scope invariants, audit trail — are visibly enforced.

## Verbs

| Verb | Caller | Purpose |
|---|---|---|
| `init` | human | Create project from SOW; spawn planning agent |
| `status` | any | Show project phase, period, agents, issues |
| `propose-oap` | planner | Submit draft OAP for human approval |
| `approve-oap` | human | Approve OAP; spawn CoS; transition to MOBILIZE |
| `checkin` | any agent | Pass orientation gate (role/period/risk/objectives validated against OAP) |
| `spawn` | cos | Create a worker or supervisor (must check in before acting) |
| `create-issues` | cos | Translate OAP objectives → issue records; transition to EXECUTE |
| `transition` | role-gated | Move issue through `open → in-progress → ready-for-review → pending-review → closed` |
| `verify` | worker / supervisor / cos | Record verification evidence on an issue |
| `scope reduce` | human | Remove an objective from the OAP mid-OP |
| `scope add` | (anyone) | Always rejected — the protocol's contract |
| `propose-arr` | cos | Generate ARR with auto-derived objective outcomes |
| `review-arr` | human | Accept / reject / accept-with-changes |
| `demob` | human | Destroy project sandbox; clear registry |
| `cop` | any | Role-filtered situational view |
| `audit` | any | Dump audit log |
| `run` | any | Launch a real Claude Code agent for a registered role (skill + context + AGENTCS_AS) |

## Audit events

The 19 event types currently emitted (subset of the 27 in the canonical schema):

```
project_initiated, oap_proposed, oap_approved, oap_rejected,
agent_spawned, checkin_attempted, checkin_passed, checkin_failed,
issue_created, issue_transitioned, issue_transition_rejected,
scope_reduced, scope_expansion_rejected,
period_started, period_ended,
arr_proposed, arr_approved, arr_rejected,
verification_recorded, sandbox_destroyed
```

Each event is a JSONL record: `{ts, event_type, project_id, actor, payload}`.
