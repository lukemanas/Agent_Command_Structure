# Governance Protocol — 2026-04-30

A substrate-agnostic governance protocol for agentic harnesses. Five lifecycle phases — Base, Initiation, Planning, Operational Period, Demobilization — across three cross-cutting horizontals: Capability Governance, Common Operating Picture (COP), and Data Governance. Described in terms of orchestrators, execution sandboxes, scoped network identity, credential vaults, and skills. No requirement depends on a specific product.

---

## Governing Principle

**Agents can always think. They can only act inside the project sandbox.**

Thinking — analysis, summarization, planning, information gathering, agent-to-agent communication — is always allowed. Acting — writing files, creating artifacts, modifying external systems — requires a project sandbox with approved scope, credentials, and human oversight.

---

## Threat Model

The protocol exists to make agentic execution recoverable when something goes wrong. The table below enumerates the failure modes the design addresses and the controls that catch each. Where a control is weak, the gap is named.

| Threat | Control | Strength |
|---|---|---|
| Prompt injection at SOW intake | Human approves SOW; risk classification is a separate manual step | Hard at the human boundary |
| Prompt injection via context (codebase, docs, tool output) | Sandbox boundary; OAP-declared `required_access`; classification labels on data | Hard |
| Prompt injection via inbound agent-to-agent messages | Network ACLs (chain-of-command messaging); message classification check | Hard |
| Scope drift mid-OP | OAP immutability; scope-can-shrink-not-grow; CoS adversarial review; human at the exits | Hard for state, soft for intent |
| Credential exfiltration | Sandbox boundary; scoped network identity; time-bounded vault credentials | Hard |
| Lateral movement across projects | Per-project sandbox; project-scoped network segment; per-project credential scope | Hard |
| Model deception in verification (claims-without-evidence) | Verified-before-close; CoS adversarial review; human reviews ARR | Soft — relies on review depth |
| Replay or forgery of checkin tokens | Identity & authentication boundary (capabilities bound to project, period, role, agent) | Hard, given correct implementation |
| Stale-state action | Orientation at boundaries; COP is current state, not history | Soft (skill-enforced at task boundaries) |
| Tool poisoning via context | `required_access` declared in OAP, not derived from context | Hard |
| Skill supply chain | Registry as source of truth; skills loaded by orchestrator from a trusted source | **Weak — protocol does not specify skill signing or verification** |
| Memory poisoning across OPs | High risk: ARR is sole input + sandbox destroyed. Low risk: human-approved ARR. | Hard at high risk, soft at low |
| Audit-trail gap | Every governance action is recorded; OP fully reconstructable | Hard |
| Human approval fatigue | Approvals concentrated at semantic boundaries (SOW, OAP, ARR, merge) — not per-tool-call | Soft — by design |

The protocol does not currently address: container-escape vulnerabilities (CVE-2024-21626 class) that breach the sandbox boundary, data poisoning of the project repository between OPs, model collusion when multiple agents share a sandbox, side-channel attacks via timing or resource consumption, or compromised-orchestrator scenarios. These are out of scope for v1.

---

## Capability Governance

### Identity and authentication

Before issuing actor capabilities — credentials, write access, role-gated state transitions — the orchestrator MUST authenticate the agent and bind the issued capabilities to a `(project_id, period_number, role, agent_address)` tuple. The binding is asserted on every privileged action and validated by the orchestrator. Capabilities expire at the period boundary or sandbox destruction, whichever comes first. The protocol does not specify the authentication mechanism, only that the binding be unforgeable to the agent.

This is the axiom on which role-gating rests. Without it, every other rule in this section is bypassable.

### Three layers of enforcement

1. **Sandbox boundary (hard).** The project runs inside an execution sandbox. No ambient credentials, no host filesystem access. Cannot reach what isn't provided. The orchestrator composes the sandbox from a profile (mounts, ACLs, credentials); the vault sources credentials; the orchestrator never stores secrets.
2. **Network isolation (hard).** Cryptographic identity controls who can reach what. ACLs enforced at the network layer, scoped by risk tier and OAP. Transport encryption is a property of this layer, not a separate mechanism.
3. **Skills (soft).** Skills tell the agent its role, chain of command, and constraints. Not system-enforced — the agent follows the rules because the skill instructs it to. If skills fail, layers 1 and 2 catch it.

A registry is the source of truth for what profile each agent has, and informs all three layers.

### Capability profiles

- **Analyst (base, network-scoped).** Runs on the agent's home network — no project sandbox. Inbox + agent-to-agent messaging. No external credentials. Skill: analyst.
- **Planner (project-scoped).** Sandbox with inbox + repo write credential. Skill: planner.
- **Actor (project-scoped).** Sandbox with full project credentials from the vault, scoped by OAP. Skill: CoS / supervisor / worker.

Governance is subtractive: the sandbox starts empty and the profile adds what's needed. Phase transitions are sandbox-config events — entering planning mounts planning credentials; entering OP mounts actor credentials and broadens ACLs; demobilization destroys the sandbox.

### Risk classification

The human sets a binary risk tier on the SOW. Every other behavior in the protocol references this table.

| Dimension | Low | High |
|---|---|---|
| Sandbox model | One project sandbox shared by all agents | Role-scoped sub-sandboxes within the project |
| Persistence | Sandbox persists between OPs | Sandbox destroyed each OP |
| External references | Read-only references allowed | No external references; data copied in |
| Network reach | Project sandbox can reach scoped external resources | No reach outside the project segment |
| OP length | Longer, flexible | Shorter, more human checkpoints |
| Inter-OP context | Agents carry own memory | ARR is sole input, human-approved |
| Credential rotation | Rotated via vault each OP | Destroyed with the sandbox |
| Personal-agent contact during OP | Allowed | Blocked; human is the air lock |

The planning agent's sandbox persists across OPs regardless of tier (unless performance drops). The human can destroy any sandbox at any time.

### Authorization matrix

The orchestrator is the only entity that *executes* state transitions. Roles authorize; the orchestrator validates and applies.

| Action | Human | Planning | CoS | Supervisor | Worker | Orchestrator |
|---|---|---|---|---|---|---|
| Run initiation / set risk classification | ✓ | — | — | — | — | executes |
| Approve OAP / approve ARR / merge to main | ✓ | — | — | — | — | executes |
| Author OAP draft | — | ✓ | — | — | — | — |
| Spawn CoS | — | — | — | — | — | ✓ (on OAP approval) |
| Spawn supervisor | — | — | ✓ | — | — | executes |
| Spawn worker | — | — | ✓ | ✓ | — | executes |
| Create / update objective records | — | — | ✓ | ✓ (own team) | comments only | — |
| Transition: in-progress, ready-for-review | — | — | — | — | ✓ | enforces |
| Transition: pending-review | — | — | — | ✓ | — | enforces |
| Transition: closed | — | — | ✓ | — | — | enforces |
| Reduce / defer / cancel scope mid-OP | ✓ | — | (relays) | — | — | executes |
| Add or expand scope mid-OP | ✗ (next OAP only) | ✗ | ✗ | ✗ | ✗ | rejects |
| Terminate period | ✓ | — | (requests) | — | — | enforces |
| Issue actor credentials | — | — | — | — | — | ✓ (post-checkin) |
| Destroy any sandbox | ✓ | — | — | — | — | executes |

At small scale, a single agent holds multiple roles and the matrix collapses accordingly — but the orchestrator's enforcement role does not. Per premise P32 (unmanned functions roll up), one agent may simultaneously occupy the planning, CoS, supervisor, and worker rows; the orchestrator's role-binding check still runs on each row independently, so every privileged action is validated against the matrix even when the same agent appears on both sides of the authorization.

---

## Data Governance

Messages carry a classification label; the agent registry has a clearance field; transport checks label against clearance before delivery. Initially everything is internal-or-below — the check always passes — but the enforcement point exists from day one. No sanitizing process or RBAC integration yet. Cheap to build, prevents retrofit later.

---

## Base Operating State

A shared agent network. Every human has a personal agent — a networked Claude/ChatGPT equivalent.

**What agents can do:** chat with their human; think, analyze, plan, recommend; agent-to-agent messaging; read by permission/classification; search (web, enterprise data, codebase); produce drafts in-conversation.

**What agents cannot do:** execute plans, change state in any external system, create durable artifacts.

**Exit condition:** when the human asks the agent to *do* rather than *think about*, the agent recognizes the cognition/execution boundary and initiates the SOW process.

---

## Initiating the Harness

The personal agent drafts (or the human supplies) a SOW. The human selects risk classification as a separate, deliberate step. Initiation is a single human command; the schema is the gate. On validation failure: error and halt. On success: project sandbox is created and the planning agent spawns automatically with actor profile and planner skill. Project initiation is the first audit event.

**SOW:**
```
project_title        string  required
objective            string  required
project_id           string  required, unique
risk_classification  enum    required (low | high)
collaborator_ids     []string optional
context              []string optional (links/paths/commands)
```

**Project sandbox on creation:** sandbox image with the agent runtime + project toolchain + orchestrator client (no credentials yet); project repository (mounted as a volume); project-scoped network segment; project communication channels; registry entry (project ID, risk tier, status, agents, active period).

**Context preparation** follows the risk tier (see table): low risk references context outside the sandbox; high risk copies context into the sandbox at initiation.

---

## Planning Phase

**Actors:** human, planning agent.

**Flow:**
1. Planning agent orients (SOW, codebase, files, skills) and researches as needed.
2. Planning agent **scopes**: single-OP or multi-OP. Multi-OP work yields an optional Project Plan first (see Appendix A); single-OP goes straight to OAP draft.
3. Planning agent and human iterate on the OAP. Human talks directly to the planning agent. Personal-agent contact follows the risk tier.
4. Human approves OAP → schema validation. Pass: OAP committed to the project repository (immutable); audit trail begins. Fail: halt.
5. Orchestrator spawns the CoS, who passes the checkin gate, orients, creates objective records from the OAP (with operational detail: reporting, branch, when-blocked, when-done), and spawns the crew. Each spawn passes the checkin gate.
6. CoS transitions the period to EXECUTE and notifies the human.

The SOW is archived to `history/` after the scoping decision.

**OAP — Operational Action Plan:**

The contract for a single OP. Defines what will be done and by whom. Scope can shrink mid-OP but never expand.
```
period_number     int       required
duration_estimate string    optional (planning estimate, not protocol-enforced — e.g., "4h", "2d")
strategy          string    optional
context           []Context optional
  type            string    e.g., "codebase", "doc", "url"
  ref             string    path, URL, identifier
  description     string    why this matters
objectives        []Obj     required
  id              string    required
  title           string    required
  description     string    optional
  priority        string    optional
  criteria        []string  required (acceptance criteria)
  context         []Context optional
  required_access []string  optional (credentials/access)
  risks           []string  optional
  dependencies    []string  optional
assignments       []Assign  required
  role            string    required (e.g., "supervisor", "worker")
  objective_ids   []string  required
  skill           string    required
  tools           []string  optional
```

**Objective Record (CoS creates from OAP):**

The working unit during execution. Adds operational detail to each OAP objective.
```
title           string    from objective
project_id      string
assigned_to     string    agent address
skills          []string
tools           []string
priority        string
objective       Obj       (id, description, criteria, context, required_access, risks, dependencies — from OAP)
reporting       { reports_to, check_in, when_blocked }
process         { branch, review, when_done }
notes           string
```

**Two separate agents** (planning + CoS), not one. CoS is the manager; planning agent is the strategist. Merging creates scope so wide that operational firefighting crowds out strategy. Separation also creates a natural quality check.

**Planning agent lifecycle.** Persists across the entire project. Initially carries an actor profile; available throughout for reference and replanning. During each OP, works ahead on the next OAP using the live COP. Has a role in demobilization — wrote the OAP, knows what success looks like. Human can wind it down at any time.

**File lifecycle.** `sow.json` lives at the project root during planning, archived to `history/` after OAP approval. `oap.json` is committed on approval. Historical OAPs and ARRs accumulate in `history/period-N/`.

---

## Common Operating Picture (COP)

Project-scoped situational-awareness layer spanning Planning, OP, and Demobilization.

**Principles.** Information flows freely; direction flows through chain of command. Agents self-orient — the system provides the picture; the agent maintains its own awareness. Agents must report blockers, risks, and anomalies up the chain. The COP is current state, not history — overwritten, not appended.

### Architecture

- **Objective tracker** = project-management state. OAP approval creates one record per objective. CoS and supervisors manage through the tracker (updates, comments, labels, reassignment). Implementations may use any system supporting per-record state, comments, labels, and assignment.
- **Coordination store** = infrastructure state. Period state machine (phase), agent registry (keys, profiles, checkin status), audit trail.
- **COP query** = computed view. Reads tracker + coordination store, returns role-filtered output (worker sees own assignments and immediate blockers; supervisor sees the team; CoS sees everything). No persistent COP document.

### Checkin gate

The protocol's spawn-time orientation enforcement. Every agent passes it before any action — CoS, supervisors, workers, replacement agents. No bypass.

1. Agent spawns into the project sandbox with restricted access (can receive messages, read COP).
2. Agent reads its skill and the COP.
3. Agent runs checkin: declares role, objectives, supervisor, period state, risk tier, constraints.
4. Orchestrator validates each field against COP state (mechanical comparison).
5. Pass → role-scoped credentials and access. Fail → corrective message and retry; after N failures, kill and notify the human.

What this catches: skill didn't load, hallucinated assignment, stale state. What it doesn't catch: parroting fields without comprehension. To parrot correctly the agent must have read the COP and skill. Comprehension is what review loops (CoS check-ins, demob) are for.

A second layer exists for non-spawn contexts: when the CoS or a supervisor onboards an agent to a specific assignment, the agent restates that assignment in its own words and the supervising role judges comprehension. Soft enforcement; the supervisor can reject and respawn.

### Orientation boundaries

Agents do not poll continuously — context bloat would distract from execution. They orient only at:

| Boundary | Who | Mechanism |
|---|---|---|
| Spawn | every agent | checkin gate (hard) |
| Task completion | the agent finishing | reads COP before next task (skills) |
| Period transition | everyone | full re-orient |

### Update flow

The orchestrator writes mechanical state (objective status from the tracker, registry events) deterministically. CoS and supervisors write management context (priorities, notes, reassignments, judgment-required blockers) through tracker record updates. The COP query merges both at read time.

---

## Operational Period

The framework scales with the OAP — same invariants whether one agent wears all hats or twenty agents organize under a CoS and supervisors.

### Invariants

| # | Invariant | Enforcement | Mechanism |
|---|---|---|---|
| 1 | Checkin gate before any work | hard | orchestrator validates fields against COP |
| 2 | Project isolation | hard | sandbox boundary; no host or cross-project access |
| 3 | Record transitions are role-gated | hard | orchestrator checks caller's role |
| 4 | Period termination triggered by all-objectives-verified or human command | hard | orchestrator gates the exit condition |
| 5 | Agents never touch main | hard | branch protection |
| 6 | Chain-of-command messaging | hard | network ACL enforcement |
| 7 | Verified-before-close on every objective | soft | supervisor/CoS attests; human reviews at demob |
| 8 | Tests/criteria of acceptable quality | soft | CoS adversarial review |
| 9 | CoS review is thorough | soft | human reviews at demob |
| 10 | Complete audit trail | hard | every governance action recorded; OP fully reconstructable |
| 11 | Human at the exits | protocol | human approves OAP, reviews ARR, merges to main |

### Scaling

| OAP size | Roles | Review | Branching |
|---|---|---|---|
| 1 objective, trivial | single agent (all roles) | human at demob | feature branch |
| 2–3, moderate | CoS + workers | CoS reviews workers; human at demob | feature branch ± topic branches |
| 5+, complex | CoS + supervisors + workers | supervisor → CoS adversarial → human | feature branch + per-objective topic branches |

### Period state machine

```
MOBILIZE → EXECUTE → [Demobilization]
```

- **MOBILIZE.** OAP approved; agents spawning and checking in. Supervisors (or the single agent) write tests for code objectives and confirm red. Entry: OAP approval.
- **EXECUTE.** Work happening. Entry: CoS signals ready. Exit: all objectives verified-before-close, or human termination. Either exit transitions to Demobilization.

### Spawn at scale

CoS spawns supervisors into the sandbox (or sub-sandboxes at high risk); each passes the checkin gate. Supervisors read their objective records, write tests for code objectives (recording the verification method on the record), then spawn workers — who pass the checkin gate and start executing.

### Verification

Verified-before-close. Code objectives use TDD: supervisor writes the tests, worker makes them green. This prevents agents from verifying broken behavior, gives binary pass/fail goals, and catches hallucinations. Non-code objectives use explicit criteria from the OAP (e.g., "12 meetings scheduled with agendas"). The verification method is recorded on every objective record; no objective closes without it.

### Execution flow

Workers execute against records and report milestones and blockers up. Supervisors validate (run tests for code, check criteria for non-code), comment, and either transition the record or send the worker back. Supervisors roll up to the CoS, who manages the operation, escalations, and record updates.

### Record lifecycle (role-gated)

```
open → in-progress → ready-for-review → pending-review → closed
         (worker)      (worker)         (supervisor)      (CoS)
```

At small scale the single agent manages its own transitions and the human reviews at demob.

### CoS adversarial review

When a supervisor moves a record to `pending-review`, the CoS reads the verification evidence and judges whether the verification actually covers the criteria, whether anything is missing (edge cases, integration points), and whether this objective's work coheres with the others. Weak or incomplete → reopen with feedback. Satisfactory → close.

### Period termination

The bound on a period is scope, not time. A period ends when all objectives are verified-before-close or when the human terminates it. The CoS monitors progress against scope and surfaces blockers; if work cannot finish — due to scope misjudgment, missing context, or external blockers — the CoS escalates to the human in natural language with what's done, what's left, and why. The human either authorizes termination (incomplete objectives are documented in the ARR; the OP transitions to Demobilization) or pauses for replanning. CoS failing to recognize a stalled period is a performance signal.

A `duration_estimate` on the OAP is a planning aid for operators, not a protocol-enforced timer; adopters who want a hard wall-clock cap can implement one as an extension to the protocol.

### Scope changes mid-OP

Scope can shrink, never grow. The human can remove, deprioritize, or cancel objectives at any time and the CoS adjusts. Adding or changing objectives requires a new OAP through the planning cycle — preventing scope creep from undermining the review structure.

### Planning agent during the OP

Primary role: working ahead on the next OAP using the COP. Secondary role: advising the CoS on intent, ambiguity, and project-plan alignment. Not in the chain of command during execution — the strategist sitting next to the commander.

### Agent failure

The level above detects (silence, stalled progress) and respawns. Worker → supervisor; supervisor → CoS; CoS → human. The replacement passes the checkin gate, orients from the COP, and inherits the role. No special health-check infrastructure needed.

### Reporting

Records are the durable record; messages are the push notification. Workers update records as work progresses and message supervisors when something material changes. Messages are natural language — no structured reporting format initially. Judgment failures (rubber-stamping, drift, ignored blockers) are caught by the human at demob, with the planning agent as an earlier signal because it is reading the COP for the next OAP.

### Blockers

Escalate through the chain: worker → supervisor → CoS → human. No bypassing. Each level attempts resolution first. Within-scope blockers (technical, dependencies) get resolved internally. Out-of-scope blockers (access, credentials, scope ambiguity) reach the human.

---

## Credential Management

The sandbox boundary closes the credential gap — agents cannot reach host credentials because they don't run on the host.

- **Orchestrator composes** what credentials the project needs from the OAP, requests them from the vault, and mounts them into the sandbox. Never stores secrets.
- **Vault sources** scoped, time-bounded credentials through a pluggable interface. The vault is replaceable; small orgs without one substitute orchestrator-managed project tokens behind the same interface.
- **Sandbox enforces.** Credentials exist only inside the sandbox. Sandbox destroyed = credentials gone.

**Lifecycle.** Project initiation requests project-scoped credentials; mount follows the risk tier (shared at low, role-scoped at high); OP boundary rotates (low) or destroys (high); demobilization destroys the sandbox and credentials expire. No manual revocation needed.

---

## Demobilization

The CoS produces an ARR (After-Action Review) at the end of every OP. The planning agent reviews it and may comment. The human approves it; on rejection, the OP is treated as aborted. At high risk the ARR is the *sole* input to the next OAP — no agent memory carries across the OP boundary.

**ARR:**
```
period_number       int        required
status              enum       required (complete | partial | aborted)
objectives_outcome  []         required
  id                string     matches OAP objective ID
  outcome           enum       verified | partial | not-attempted | failed
  verification      string     method recorded (test paths, criteria evidence)
  notes             string     what was done, what wasn't, why
incomplete          []string   objective IDs not closed
scope_changes       []         what was reduced/deferred and why
  type              enum       reduce | defer | cancel
  objective_ids     []string
  reason            string
  authorized_by     string
performance         []         per-agent signals
  agent             string     address
  role              string
  signal            string     what worked, what didn't
  evidence          string     pointer to record/comment/log
risks_observed      []string   near-misses; things that almost broke
recommendations_for_next_oap []string
audit_summary       string     pointer to the full audit stream
human_decision      enum       required (accept | reject | accept-with-changes)
human_comments      string
```

Required: `period_number`, `status`, `objectives_outcome`, `human_decision`. Authored by the CoS, reviewed by the planning agent, approved by the human.

**Sandbox teardown** follows the risk tier: high risk destroys the sandbox at OP end and revokes credentials; low risk persists the sandbox into the next OP and rotates credentials at the OP boundary. Either way, the project sandbox is destroyed and credentials expire when the *project* itself demobilizes.

**Record cleanup.** Open objective records that did not close are documented in the ARR. They flow into the next OAP through the normal planning cycle, not as direct carryover.

---

## Open Questions

- **Trigger semantics.** All-objectives-verified transitions automatically to Demobilization; human-command is the override and the only other path out of EXECUTE. Specify whether the CoS confirms or the orchestrator transitions unilaterally.
- **Performance measurement.** The ARR carries per-agent signals; the protocol does not yet specify how those signals affect future profile assignment, capability scope, or registry status.
- **Project-level demobilization.** Distinct from OP-level demobilization, not yet differentiated in the protocol.
- **Skill supply chain.** Currently "trust the registry." Signing, verification, and version pinning are open.
- **Cross-orchestrator interop.** v1 does not specify handoff between conformant orchestrators (e.g., a Claude-hosted project handing to an ADK-hosted one). Out of scope for v1.

---

## Appendix A — Project Plan (multi-OP, optional)

Roadmap for projects spanning multiple OPs. Produced by the planning agent when scoping deems the work too large for a single OP.

```
project_id        string    from SOW
title             string    human-readable
mission           string    project-level success
scope             []Phase
  phase           string    e.g., "Foundation", "Migration"
  description     string
  objectives      []string  high-level descriptions for this phase
success_criteria  []string  how the project is judged complete
```
