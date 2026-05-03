# Governance Design — 2026-03-17 (substrate-scrubbed)

Design session working through the governance architecture one level below the lifecycle diagram. Covers all five lifecycle phases: Base Operating State, Initiating the Harness, Planning, Operational Period, and Demobilization. Cross-cutting sections cover Capability Governance, Data Governance, the Common Operating Picture, and Credential Management.

**Reference implementation targets:** containers (Docker, Podman, microVMs), a network identity / ACL layer (Tailscale, Kubernetes NetworkPolicies, Calico, AWS SCPs), an enterprise IAM / vault (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager). The protocol is described in terms of containers, network identity, and credential sources — not specific tools.

### Protocol Invariants

A conformant implementation of this protocol must satisfy each of these:

1. The five lifecycle phases exist and transition under defined rules (base → harness → planning → operational period → demobilization).
2. SOW and OAP exist as schema-validated structured documents; the human approves each before downstream phase entry.
3. A project container is created on initiation and destroyed (or scoped-rotated) at demob.
4. Three capability profiles exist: analyst (host, no container), planner (project container, scoped credentials for planning), actor (project container, scoped credentials per OAP).
5. A planning agent produces the OAP for human approval before any actor work begins.
6. A CoS (or designated agent at small scale) translates the OAP into work units and dispatches the crew.
7. Every agent passes a checkin gate before doing actor work.
8. Each operational period has a duration estimate; only the human can extend it.
9. No objective closes without acceptance-criteria verification recorded against the issue.
10. The human gates the entries and exits: approves OAP in, reviews ARR out, merges to main.
11. Agents never write to the protected branch of the project repo. The human merges.
12. The chain of command (workers → supervisors → CoS → human) is enforceable at the protocol layer; no bypassing, no freelancing.
13. Every governance action emits an audit event conforming to the protocol's audit event schema.

## Lifecycle Overview

Five phases, left to right:

1. **Base Operating State** — agents are analysts and communicators, not actors
2. **Initiating the Harness** — SOW, risk classification, project container creation
3. **Planning** — planning agent produces the OAP, human approves
4. **Operational Period** — bounded execution under CoS/SHOC management
5. **Demobilization** — mandated testing, ARR, human review

Three cross-cutting horizontals:

1. **Capability Governance** — enforcement model, profiles, credential management
2. **Common Operating Picture** — situational awareness, orientation, checkin gates
3. **Data Governance** — classification, clearance, sanitizing process

---

## Governing Principle

**Agents can always think. They can only act inside the project container.**

Thinking — analysis, summarization, planning, information gathering, A2A communication — is always allowed. Acting — writing files, creating artifacts, modifying external systems — requires a project container with approved scope, credentials, and human oversight.

---

## Capability Governance

### Enforcement Model (three layers)

1. **Container boundary (hard guarantee)** — the project runs inside a container. No ambient credentials, no host filesystem access. Cannot reach what isn't provided. Low risk: one project container, all agents share it. High risk: role-scoped sub-containers within the project for credential isolation between agents.
2. **Network isolation (hard guarantee)** — cryptographic identity controls who can reach what. Low risk: project container can reach external resources scoped by the OAP. High risk: no network access outside the project segment. ACLs enforced at the network layer.
3. **Protocol (soft enforcement)** — skills tell the agent its role and constraints. Agent tells human when something requires a different profile. Not system-enforced — the agent follows the rules because the skill instructs it to.

Transport encryption is a property of the network layer (e.g., WireGuard, mTLS, IPsec), not a separate enforcement mechanism. If protocol fails, the container boundary and network ACLs catch it.

### Three Components

1. **Registry** — source of truth for what profile an agent has. Informs all three layers. (Reference impl: Redis hash; any consistent registry works.)
2. **Container config** — translates profile into what's mounted (credentials, network access, volume mounts). The vault provides credentials; the orchestrator stitches them into the container at spawn. The orchestrator never stores secrets. *(Layer 1: container boundary)*
3. **Network ACLs** — control what the container can reach, scoped by risk tier and OAP. *(Layer 2: network isolation)*
4. **Skills** — encode role behavior, chain of command, and constraints. The agent's instructions for how to operate within the framework. *(Layer 3: protocol)*

### Capability Profiles

Three profiles across the lifecycle:

**Agent as Analyst (base state, organization-scoped):**
- Runs on the host — no project container
- Inbox access and A2A messaging on the messaging substrate
- No external credentials — cannot execute on external systems
- Skill: analyst skill (think, research, communicate, recommend)

**Agent as Planner (project-scoped):**
- Container config: inbox access + repo write credential from vault
- Skill: planner skill
- May initially share the actor container config; long-term, planners get a dedicated profile with scoped planning permissions

**Agent as Actor (project-scoped):**
- Container config: full project credentials from vault, scoped by OAP. Repository tokens, API keys, whatever the OAP defines.
- Skill: CoS / supervisor / worker skills
- Long-term: per-agent container configs based on OAP assignments

### Key Principles

- **Governance is subtractive.** The container starts empty — no credentials, no host access. The profile adds specific capabilities by mounting them.
- **Phase transition = container config event.** Enter planning → container gets planning credentials. Enter OP → container gets actor credentials and broader network ACLs. Demobilization → container destroyed, credentials expire.
- **Orchestrator routes; vault sources.** The orchestrator derives what the agent needs from the OAP and asks the vault; the vault returns scoped, time-bounded credentials; the orchestrator mounts them into the container. The orchestrator never stores secrets.
- **Three profiles, composable container config.** Container config is a composable set of mounts, ACLs, and credentials per profile, extensible to per-agent configs as scaling demands.

### Planning Agent Lifecycle

- Long-lived — persists from project start across multiple OP cycles until retired
- Mostly analyst behavior (research, analyze, recommend) but needs limited actor capability (write/commit OAP)
- Initially gets actor profile; future: own planner profile
- Available throughout the project for reference, replanning
- Has role in demobilization — wrote the OAP, knows what success looks like

### Agent Persistence by Risk Tier

- **Low risk:** Container persists between operational periods within the same project (if performance remains high). Credentials rotated via vault at each OP boundary.
- **High risk:** Container destroyed at end of each OP. New container, new network identity, fresh credentials from vault. No state carries over.
- Planning agent container persists regardless of risk tier (unless performance drops)
- Human can always destroy any agent's container at any time

---

## Data Governance

- Messages carry a classification label field
- Agent registry has a clearance field
- Transport checks label against clearance before delivery
- Initially everything is internal or below — the check always passes, but the enforcement point exists from day one
- No sensitive data, no sanitizing process, no air lock, no RBAC integration yet
- Cheap to build (string fields + one-line comparison), prevents retrofit later


---

## Base Operating State — Design

The base operating state exists within a tank network. Every human has a personal agent — the equivalent of a Claude or ChatGPT account, but networked.

### What agents can do
- Chat with their human (web chatbot equivalent)
- Think, analyze, summarize, plan, recommend
- A2A messaging with other agents (encrypted, like Slack for agents)
- Read files by permission/classification
- Search (web, enterprise data, codebase)
- Produce recommendations, drafts, plans — as long as they stay in the conversation

### What agents cannot do
- Execute plans (write files, create artifacts, send emails, schedule meetings)
- Change state in any system outside the conversation
- Create durable artifacts (dashboards, documents, code)

### Access
- Enterprise Common Operating Picture (data catalogs, SharePoint, etc.)
- Personal context (user files, preferences)
- Classification-controlled: internal and below = open, confidential and above = RBAC

### Exit condition
When the human asks the agent to *do something* rather than *think about something*, the agent recognizes this crosses the cognition/execution boundary and initiates the SOW process → transition to Initiating the Harness.

---

## Initiating the Harness — Design

### Trigger

The human asks their personal agent (analyst) to do something that requires execution. The agent recognizes this and initiates the SOW process. Lightweight by default — can be a 1 minute conversation.

### Scope of Work

The personal agent drafts or the human provides a SOW. Either way the agent presents it back for confirmation.

**SOW Data Structure:**

```
SOW {
  project_title:        string    (required)
  objective:            string    (required)
  project_id:           string    (required, unique)
  risk_classification:  enum      (required, human-set: low | high)
  collaborator_ids:     []string  (optional)
  context:              []string  (optional, links/paths/commands)
}
```

SOW is drafted with help from the SOW Skill on the personal agent.

### Flow

1. Personal agent helps draft SOW (or human provides it)
2. Human approves SOW content
3. Human manually selects risk classification (separate deliberate step — human must consciously choose low or high)
4. Risk classification inserted into SOW before validation
5. Human runs initiation command
6. Schema validation — all required fields present, project ID unique, risk classification set
7. Validation fails → error, lists missing fields, nothing happens
8. Validation passes → project container created

**The command is the approval. The schema is the gate.** Human can't initiate without a complete SOW.

Project initiation is an audit event (who created, when, with what SOW). But the full audit trail — every governance action recorded — is primarily for operational periods.

### Risk Classification (two tiers)

| Dimension | Low Risk | High Risk |
|-----------|----------|-----------|
| Container model | One project container, all agents share | Role-scoped sub-containers within project |
| Agent persistence | Container persists between OPs | Container destroyed each OP |
| Agent isolation | Read-only volume mounts outside project | No external mounts, data copied in |
| OP length | Longer, flexible | Shorter, more human checkpoints |
| Communication | Can communicate outside project | No communication outside project |
| Context between OPs | Agents carry own memory | ARR is sole input, human-approved |
| Blast radius | Broader access | Sealed — no ambient context, no drift, clean slate |

High risk = isolation chamber. Clean inputs, bounded execution, mandatory review, full teardown. Container destroyed at OP end. Prevents context poisoning, memory failure, and accumulated drift.

### Project Container

Created on successful SOW validation:

- **Container image** — base environment with runtime (Claude Code, Codex, Gemini), project toolchain, and tank CLI. No credentials until profile assignment.
- **Git repo** — version history, file structure, access control. Mounted as a volume into agent containers.
- **Network identity** — project-scoped network segment. Agent containers join this segment on spawn.
- **Project communication channels** — messaging within the project container boundary
- **Registry entry** — project ID, risk tier, status, assigned agents, active period

### Context Preparation

The personal agent gathers and packages starting context into the project container.

- **Low risk:** Context mounted as read-only volumes into agent containers. Agents can access references outside the project directory.
- **High risk:** Context copied into the container image at initiation. No external volume mounts, no network access outside the project segment. The container is the air gap.

### Planning Agent Spawns

On project initiation, the planning agent spawns automatically with actor profile and planner skill. Reads the SOW and prepared context. Begins the planning phase.

---

## Planning Phase — Design

### Actors
Human, Planning Agent

### Flow

1. Planning agent orients — reads SOW, context (codebase, history, files, skills)
2. Planning agent researches — codebase, docs, web, enterprise data as needed
3. Planning agent **scopes** — judges whether this is single-OP or multi-OP work
4. **If multi-OP:** planning agent produces a Project Plan, presents to human, they refine.
5. **If single-OP:** planning agent goes straight to OAP draft.
6. SOW archived to `history/` after scoping decision (consumed, no longer active).
7. Planning agent and human collaboratively scope, iterate, and draft the OAP. Human talks directly to planning agent (not through personal agent).
8. Planning agent can consult human's personal agent (low risk: open; high risk: restricted — personal agent cannot message into the container after initiation, human is the air lock)
9. Human approves OAP → schema validation (required fields present, correct types)
10. Validation fails → error, nothing happens
11. Validation passes → OAP committed to project repo (immutable), audit trail begins
12. The orchestrator spawns the CoS → CoS goes through checkin gate (orchestrator validates mechanical fields), gets actor keys
13. CoS orients — reads OAP, asks planning agent or human questions if needed
14. CoS creates issues from OAP objectives in the project's issue tracker — adds operational detail (reporting, process, branching, blocked/done instructions)
15. CoS spawns crew based on OAP assignments — each agent goes through checkin gate (orchestrator validates mechanical fields) AND comprehension validation (CoS validates the agent understands its assignment)
16. CoS transitions period to EXECUTE, notifies human: "Period N is live, here's the crew, here's the issues" → transition to Operational Period

### Planning Agent Lifecycle
- Persists across the entire project (not just one OP)
- During the OP, works alongside CoS — available for questions about the OAP
- Actively works ahead on the **next OAP** during delivery, so the transition between OPs is fast — just update based on the ARR
- Can be wound down by human at any time

### Handoff Design

**Personal Agent → Planning Agent (project creation only):**
- SOW in the project container as `sow.json` (structured, schema-validated)
- Prepared context in the project container (files, links, data). Low risk: references/links. High risk: data replicated into container.
- Human talks directly to the planning agent to fill intent and priority
- The goal is to identify the SOW early — personal agent's SOW Skill detects when conversation crosses from thinking to doing and prompts the human to set up a project. Keep pre-project conversations short.

**Planning Agent → CoS:**
- The OAP is the structured handoff
- The planning agent is the living context — CoS queries it, not a document
- Separation of concerns: planning agent writes the plan, CoS executes it. Natural check — CoS can push back.

**Existing projects (no handoff needed):**
- Human messages the planning agent directly within the project container
- New OP within existing project: planning agent has been working ahead, ARR from last OP is available, human and planning agent refine together

### Key Decision
Two separate agents (planning agent + CoS), not one merged agent. The CoS is a manager, the planning agent is a strategist. Merging them creates too wide a scope — operational firefighting crowds out strategic thinking. Separation also creates a natural quality check.

### Two-Level Checkin Validation
1. **The orchestrator validates mechanical fields** — role, objective IDs, period state, risk tier. Exact match against COP. Hard enforcement — no keys without passing.
2. **CoS validates comprehension** — agent restates its assignment in its own words. CoS judges whether the agent actually understands. Soft enforcement — CoS can reject and respawn.

### Data Structures

**Project Plan (multi-OP only, optional):**

Roadmap for projects that span multiple operational periods. Planning agent produces this when scoping determines the work is too large for a single OP.

```
project_id        string    Unique project identifier (from SOW)
title             string    Human-readable project name
mission           string    What success looks like for the entire project
scope             []Phase   Ordered phases of work
  phase           string    Phase name (e.g., "Foundation", "Migration")
  description     string    What this phase accomplishes
  objectives      []string  High-level objective descriptions for this phase
success_criteria  []string  How to judge the project as complete
```

**OAP — Operational Action Plan (always required):**

The contract for a single operational period. Defines what will be done, by whom, in how long. Human approves before execution begins. Scope can shrink mid-OP but never expand.

```
period_number     int       Which OP this is (1, 2, 3...)
duration          string    Time-bounded length (e.g., "4h", "2d")
strategy          string    How the objectives should be approached
context           []Context Supporting information for the period
  type            string    Context type (e.g., "codebase", "doc", "url")
  ref             string    Path, URL, or identifier
  description     string    Why this context matters
objectives        []Obj     What will be accomplished
  id              string    Unique objective ID (e.g., "obj-1")
  title           string    Short name
  description     string    What done looks like
  priority        string    Relative priority within the period
  criteria        []string  Acceptance criteria — how to verify completion
  context         []Context Objective-specific supporting information
  required_access []string  What credentials/access this objective needs
  risks           []string  Known risks or failure modes
  dependencies    []string  Other objective IDs this depends on
assignments       []Assign  Who does what
  role            string    Agent role (e.g., "supervisor", "worker")
  objective_ids   []string  Which objectives this agent owns
  skill           string    Skill identifier (e.g., "worker", "supervisor")
  tools           []string  Additional tools or access needed
```

Required fields: `period_number`, `duration`, `objectives` (id + title + criteria), `assignments` (role + skill). Everything else optional — planning agent fills what scope warrants, human demands what's missing.

**Issue (CoS creates from OAP, adds operational detail):**

The working unit during execution. CoS translates each OAP objective into an issue in the project's issue tracker, with operational detail — who to report to, what branch to work on, what to do when blocked or done. The protocol does not mandate the tracker; the issue is the unit, the tracker is adopter choice.

```
title             string    Issue title (from objective)
project_id        string    Project this belongs to
assigned_to       string    Agent address
skills            []string  Skills the assigned agent should load
tools             []string  Tools or access needed
priority          string    Relative priority within the period
objective                   The OAP objective this issue delivers
  id              string    Objective ID (matches OAP)
  description     string    What done looks like
  criteria        []string  Acceptance criteria
  context         []Context Objective-specific context
  required_access []string  Credentials needed
  risks           []string  Known risks
  dependencies    []string  Dependent objective IDs
reporting                   Chain of command instructions
  reports_to      string    Supervisor or CoS address
  check_in        string    When/how to report progress
  when_blocked    string    What to do when stuck
process                     Operational instructions
  branch          string    Git branch to work on
  review          string    How work gets reviewed
  when_done       string    What to do when finished
notes             string    Additional context from CoS
```

### File Lifecycle
- `sow.json` — project root during planning, archived to `history/` after OAP approval
- `oap.json` — committed to project repo on approval (immutable record)
- Issues become the live state — the COP read joins them with infrastructure state
- Historical OAPs and ARRs accumulate in `history/period-N/`

### COP Initiation
The COP begins when the CoS creates issues (step 14). Before that, there's nothing to compute a view from. The CoS checkin (step 12) validates against the OAP directly, not the COP.

---

## Common Operating Picture (COP) — Cross-Cutting Design

The COP is the situational awareness layer that runs across Planning, Operational Period, and Demobilization. It is project-scoped.

### Governing Principles

- **Information flows freely, direction flows through chain of command.** Any agent can read the COP. Orders and tasking go through the hierarchy. (From ICS: general staff can exchange information with anyone; direction follows the chain of command.)
- **Self-orientation.** Each agent is responsible for reading the COP and understanding its role. The system provides the picture; the agent maintains its own awareness.
- **Report up.** Agents must surface blockers, risks, and anomalies to their chain of command.
- **The COP is current state, not history.** It's a dashboard, not a feed. Overwritten, not appended.

### Architecture

The COP is a role-scoped projection over two backing stores: an issue tracker (project-management state) and a registry/state store (infrastructure state). The protocol does not mandate either; reference implementations have used GitHub Issues + Redis.

**Issue tracker = project-management state.**
OAP approval creates issues — one per objective, assigned to agents, labeled with project/period, dependencies linked, acceptance criteria in the issue body. CoS and supervisors manage through the tracker: update issues, add comments, change labels, reassign. Adopters select the tracker (GitHub, Linear, Jira, etc.).

**Registry / state store = infrastructure state.**
Period state machine (phase, timer), agent registry (keys, profiles, checkin status), audit trail (append-only stream). Adopters select the store; the protocol requires only that it support append-only audit semantics and reasonably consistent reads.

**COP view = computed projection.**
A single read operation that joins the issue-tracker state with the infrastructure state and returns a role-scoped view. No persistent COP document — computed on read, always current.

### Per-Role Views

**Worker sees:**
```
Project: auth-rewrite
Period: 2 | Phase: EXECUTE | Risk: high
Time remaining: 4h 12m

YOUR ASSIGNMENT
  obj-2: Migrate session storage [IN-PROGRESS]
  Criteria: All sessions use new store, zero downtime

REPORTS TO: sup-1
BLOCKERS: none on your objectives
NOTE: obj-3 is waiting on your work
```

**CoS sees:** full COP — all objectives, all agents, blockers, timer, planning agent status.

**Supervisor sees:** their team's objectives, their workers' status, relevant cross-cutting context.

### Orientation at Natural Boundaries

Agents do NOT maintain continuous situational awareness. They orient at natural boundaries:

| Boundary | Who orients | Mechanism |
|----------|------------|-----------|
| Spawn | Every agent | Checkin gate (hard enforcement) |
| Task completion | Agent finishing task | Reads COP before picking up next task (protocol) |
| Period transition | Everyone | All agents re-orient |

Between boundaries, agents are heads-down on their work. This is by design — continuous COP polling would bloat context and distract from execution.

### Checkin Gate — Spawn-Time Enforcement

Every agent must demonstrate orientation before starting work. The enforcement mechanism is implementation-specific (container config switch, network ACL grant, or application-level credential issuance); the protocol requires only that an agent that fails the gate cannot perform actor work.

**Sequence:**
1. Agent spawns into the project container with restricted access (can receive messages, can read COP)
2. Agent reads skill, reads COP
3. Agent runs checkin (declares its role, objectives, supervisor, period state, risk tier, constraints)
4. The orchestrator validates each field against actual COP state (mechanical field comparison)
5. Pass → agent authorized to begin work (credentials/access scoped by role)
6. Fail → agent told what's wrong, retries. After N failures → killed, human notified.

**What this catches:** skill didn't load, hallucinated assignment, stale state.
**What it doesn't catch:** agent parrots fields without comprehension. Accepted tradeoff — to parrot correctly, the agent must read the COP and skill. Deeper comprehension is what review loops (CoS check-ins, demob) are for.

No agent bypasses this gate. CoS, supervisors, workers — same mechanism.

### COP Update Flow

1. **The orchestrator updates mechanical state** — objective status (from the issue tracker), timer ticks, agent registration/deregistration. Deterministic, automatic.
2. **CoS/Supervisors update management context** — priorities, notes, reassignments, blockers requiring judgment. Written through issue tracker updates.
3. **A COP read computes the merged view** — issue tracker state + registry state, filtered by role.

---

## Operational Period — Design

### Design Principle: The Framework Scales with the OAP

Like ICS, the governance structure is always present but staffing scales with the work. A single-objective OAP uses the same invariants as a twenty-objective operation — one agent just wears all the hats. The framework should never be so heavy that people don't use it.

### Invariants (every OP, regardless of size)

1. **Timer** — human sets duration in OAP, the orchestrator tracks it, the orchestrator notifies CoS (or single agent) on expiry. Only the human can extend it (a human-authenticated extension command).
2. **Checkin gate** — every agent proves orientation before starting work. The orchestrator validates mechanical fields (role, objectives, period state, risk tier) against COP. Hard enforcement — no work without passing. The project container has credentials; the gate controls whether the agent is authorized to use them.
3. **Verified-before-close** — no objective closes without its acceptance criteria confirmed. Automated tests for code objectives (preferred wherever possible). Acceptance criteria confirmation for non-code objectives. Verification method recorded in the issue. Agents run verification.
4. **Human at the exits** — approves OAP going in, reviews ARR coming out, merges to main.
5. **Agents never touch main** — all work on feature/topic branches. Human merges after ARR approval. One merge commit = one rollback point for the entire OP's work. (Reference: git. The protocol requires a single identifiable rollback artifact per OP; git is the reference implementation.)
6. **Complete audit trail** — every governance action during the OP is recorded: checkins, issue transitions, escalations, timer extensions, scope changes, agent failures, period completion. The OP must be fully reconstructable after the fact. The schema for these events lives in `audit-event-schema.md` — 27 typed events covering lifecycle, OAP, agent, issue, escalation, access-control, timer, and demobilization actions, with EU AI Act Article 12/14/19 mapping included.

### How the OP Scales

| OAP size | Roles | Review | Branching |
|----------|-------|--------|-----------|
| 1 objective, trivial | Single agent (all roles) | Human reviews at demob | Feature branch |
| 2-3 objectives, moderate | CoS + workers (no supervisors) | CoS reviews workers, human at demob | Feature branch, topic branches optional |
| 5+ objectives, complex | CoS + supervisors + workers | Supervisor → CoS adversarial → human | Feature branch + topic branches per objective |

The invariants don't change across rows. The roles, review depth, and branching complexity scale with the OAP.

### Period State Machine

```
MOBILIZE → EXECUTE → [Demobilization phase]
```

- **MOBILIZE** — OAP approved, agents spawning, checking in through the gate. For code objectives, supervisors (or the single agent) write tests and record them in the issue. Entry: OAP approval.
- **EXECUTE** — work happening. Entry: CoS (or single agent) signals ready. Exit: all objectives verified-before-close → transition to Demobilization, OR timer expiry → CoS manages wind-down, then transitions to Demobilization.

Demobilization is the next lifecycle phase, not an OP state.

### Spawn Sequence (at scale)

1. CoS spawns supervisors into the project container (high risk: into role-scoped sub-containers)
2. Each supervisor checks in (tank validates mechanical fields + CoS validates comprehension)
3. Supervisor reads its assigned issues
4. For code objectives: supervisor writes tests for acceptance criteria (TDD — tests first), confirms tests fail (red)
5. Supervisor records tests/verification method in the issue
6. Supervisor spawns workers into the project container (high risk: into role-scoped sub-containers)
7. Workers check in (tank validates mechanical fields + supervisor validates comprehension)
8. Workers start executing — for code objectives, making the tests green

At small scale, the single agent does steps 3-8 itself.

### TDD for Code Objectives

TDD is best practice for AI agents (validated by Anthropic internally). Reasons:
- Prevents agents from writing tests that verify broken behavior
- Gives agents concrete, measurable goals (binary pass/fail)
- Catches hallucinations immediately
- Supervisor writes tests = supervisor understands the objective. Worker makes tests pass = worker delivers against a clear spec.

Not all objectives produce code, but all objectives require clear acceptance criteria that can be verified against. Tests are the preferred verification mechanism for code. Non-code objectives use explicit criteria defined in the OAP (e.g., "12 meetings scheduled with agendas," "financial records updated with Q1 numbers"). The verification method is recorded in the issue — no objective closes without it.

### Execution Flow

1. **Workers execute** against their assigned issues.
2. **Workers report to supervisors** on milestones and blockers.
3. **Supervisors validate** — run tests (code) or check acceptance criteria (non-code), review work, leave comments. Verified → transition issue. Not verified → send worker back.
4. **Supervisors report to CoS.** CoS manages the operation, handles escalations, updates issues.
5. **Timer ticks.** Tank tracks duration, notifies CoS as it approaches expiry.

### Issue Lifecycle (role-gated transitions)

```
open → in-progress → ready-for-review → pending-review → closed
         (worker)      (worker)         (supervisor:       (CoS:
                                         verifies work,    reviews quality,
                                         reviews,          checks coherence,
                                         comments)         approves)
```

- Worker can move to `in-progress` and `ready-for-review`
- Supervisor can move to `pending-review` (acceptance criteria must be verified)
- CoS can move to `closed` (adversarial review of verification quality and cross-objective coherence)
- Each transition is role-gated by tank
- At small scale (single agent), the agent manages its own transitions and human reviews at demob

### CoS Adversarial Review (at scale)

When a supervisor transitions an issue to `pending-review`, the CoS:
1. Reads the verification evidence (tests + implementation for code, output + criteria for non-code)
2. Evaluates: does the verification actually cover the acceptance criteria, or is it trivial?
3. Checks: is anything missing — edge cases, integration points?
4. Checks: does this objective's work play well with the other objectives?
5. If weak or incomplete → CoS reopens the issue, tells supervisor to improve
6. If satisfactory → CoS closes the issue

### Timer and Extensions

- **CoS is responsible for monitoring time.** When CoS sees work won't finish in time, it estimates the extension needed and requests it from the human — explaining what's done, what's remaining, how much time is needed, and why.
- **Human extends via a human-authenticated command.** CoS explains the situation in natural language; the command is the approval. Only the human's identity (not an agent's) can authorize the extension.
- **Timer expiry without extension** — CoS tells agents to wrap up, collects status on incomplete work, transitions to Demobilization. Incomplete objectives documented in ARR, flow into the next OAP through the normal planning cycle.
- **CoS failing to anticipate timer expiry is a performance signal.**

### Period Completion

Two exits from the OP:

1. **All objectives verified-before-close** → CoS (or single agent) transitions to Demobilization.
2. **Timer expires** → CoS manages wind-down, then transitions to Demobilization with incomplete state.

### System Enforcement Summary

| Rule | Enforcement | Mechanism |
|------|------------|-----------|
| Checkin gate before work begins | Infrastructure | Orchestrator validates fields against COP; failed checkins do not receive credentials |
| Project isolation | Infrastructure | Container boundary — no host access, no cross-project access |
| Issue transitions are role-gated | Infrastructure | Orchestrator (or tracker integration) checks caller's role |
| Timer can't be extended by agents | Infrastructure | Only a human-authenticated identity can issue the extension command |
| Agents never touch main | Infrastructure | Branch protection on the project repo |
| Chain of command on messaging | Infrastructure | Network ACL enforcement (high risk); protocol convention (low risk) |
| Acceptance criteria verified before close | Protocol (soft) | Supervisor/CoS attests, human reviews at demob |
| Supervisor/CoS writes good tests | Protocol (soft) | CoS adversarial review |
| CoS does thorough review | Protocol (soft) | Human reviews at demob |

Note on "infrastructure" enforcement: these rules are *hard* in a conformant reference implementation but only as hard as the substrate makes them. Threats outside the threat model (container escape, registry compromise, IAM compromise) defeat them. See the adversarial-review document for the explicit threat-model gaps.

### Blockers and Escalation

- **Blockers escalate through the chain of command:** worker → supervisor → CoS → human. No bypassing.
- **Each level attempts resolution before escalating.** Supervisor might reassign work. CoS might resequence objectives. The human only hears about blockers that nobody in the chain can solve.
- **Two kinds of blockers:**
  - **Within-scope** — technical problems, dependencies between objectives. Normal management. Supervisor or CoS resolves.
  - **Out-of-scope** — agent needs something the OAP didn't anticipate (access, credentials, scope ambiguity). These reach the human.

### Scope Changes Mid-OP

- **Scope can be reduced but not expanded.** The OAP is the contract — you can shrink it mid-flight but you can't grow it.
- **Remove, deprioritize, or cancel objectives** — human command, takes effect immediately. CoS adjusts.
- **Add or change objectives** — not allowed mid-OP. Goes into the next OAP through planning. Prevents scope creep from undermining the timer and review structure.

### Planning Agent During OP

- **Primary role: working ahead on the next OAP.** Reads the COP, watches how objectives progress, incorporates learnings.
- **Secondary role: advising CoS as needed.** Intent behind objectives, handling ambiguity, alignment with the project plan.
- **Not in the chain of command during execution.** The strategist sitting next to the commander.

### Agent Failure Mid-OP

- **One level up in the supervisory chain is responsible for detection and respawning.**
  - Worker fails → supervisor detects (silence, stalled progress), spawns replacement. New worker checks in through the gate, picks up the issue.
  - Supervisor fails → CoS detects, spawns replacement. New supervisor checks in, inherits the team's issues.
  - CoS fails → human detects (no status updates), spawns replacement. New CoS checks in against the OAP, reads COP, picks up management.
- **Detection is organic** — the agent above notices silence or stalled progress through normal management. No special health-check infrastructure needed.
- **The COP gives replacement agents everything they need to orient.** GitHub issues + project state = current picture. Checkin gate ensures the replacement understands before getting actor keys.

### Reporting

- **COP is the record, messages are the signal.** Two layers:
  - **GitHub issues are the durable record.** Workers update issue state (comments, label transitions) as work progresses. Source of truth.
  - **Fishtank messages are the push notification.** Workers message supervisors to flag milestones and blockers. Supervisors message CoS with rollups. The message is the signal that something changed.
- **Messages are natural language.** No structured reporting format initially.

### CoS Judgment Quality

- **Judgment failures are caught by humans and the planning agent.** If CoS is rubber-stamping reviews, ignoring blockers, or letting workers drift:
  - **Human** catches it at demob when reviewing the ARR. The backstop.
  - **Planning agent** may notice earlier — it's reading the COP to work on the next OAP. Can flag drift to the human.
- **No mechanical check for judgment quality.** System enforcement catches state errors; human review catches judgment errors.

---

## Demobilization — Design

Demobilization closes the operational period and returns the project to a between-OPs state (low risk) or a zeroed state (high risk). The audit-event-schema.md doc defines the events emitted; this section describes the phase mechanics.

### Triggers (any of)

1. **All objectives verified.** Every OAP objective is in `closed` state with `issue.verified` events recorded. CoS (or single agent) initiates demob.
2. **Timer expiry without extension.** CoS wraps incomplete work, marks status, initiates demob with `exit_reason: timer_expired`.
3. **Human termination.** Human issues a kill-period command. CoS wraps in place, initiates demob with `exit_reason: human_terminated`.

### ARR Structure

The After-Action Report is produced by the CoS (or single agent at small scale) for human review.

```
period_number       int
exit_reason         enum    all_objectives_verified | timer_expired | human_terminated
duration_estimate   string
duration_actual     string
objectives_total    int
objectives_completed int
objectives_summary  []      one entry per objective: id, title, status, verification, notes
agents_summary      []      spawned, failed, replaced
escalations         []      blockers escalated, how resolved
scope_changes       []      OAP scope reductions during the period
incomplete_work     []      what didn't ship and why; flows into next OAP
recommendations     string  for next OAP / next period
```

The ARR is committed to the project repo as `history/period-N/arr.json` (or equivalent) and emits an `arr.submitted` event. Human approval emits `arr.approved` with the merge commit ID.

### Container Teardown

| Risk Tier | Containers | Credentials | Network ACLs | State |
|-----------|------------|-------------|--------------|-------|
| Low | Persist between OPs | Rotated via vault at OP boundary | Tags revoked, reissued at next OP | Agent memory carries; ARR is supplemental input |
| High | Destroyed at OP end | Expire with the container; no carry-over | Tags revoked, fresh tags at next OP | No carry-over; ARR is sole input to next OAP |

The two-layer revocation is: (1) primary — ACL tags revoked on the network identity layer (governance document closed → access closed); (2) defense in depth — agents killed, containers destroyed (high risk).

### Issue Cleanup

- Verified-and-closed issues: archive label applied, retained in tracker for audit.
- Unverified-but-closed issues (timer expiry / human termination): annotated with exit reason in the issue body, archived.
- Open issues at demob: closed with status `incomplete-rollover`, content folded into the next OAP through the planning cycle. Never silently abandoned.

### Handoff to Next OP

- The ARR is the structured input to the next planning cycle.
- The planning agent (which has been working ahead during the OP) updates the next OAP based on the ARR and any incomplete-rollover issues.
- The human reviews and approves the next OAP — back to the Planning Phase.

### Performance Measurement

The ARR captures the dimensions; evaluation is human + planning agent:
- **Estimate accuracy** — duration_actual vs. duration_estimate.
- **Verification quality** — did acceptance criteria actually catch what they should have?
- **Escalation density** — how many blockers per objective; signal of OAP scoping quality.
- **Agent failure rate** — replacements per agent-hour; signal of profile/tier fit.

These are inputs to the next planning cycle, not standalone metrics for the agents.

---

## Credential Management — Decided

### Architecture

The container boundary closes the credential gap. Agents cannot access host credentials (~/.ssh, ~/.gitconfig, env vars) because they run inside project containers, not on the host.

- **Orchestrator routes; never stores.** The orchestrator derives what credentials the project needs from the OAP, requests them from the vault, and mounts them into the project container. The orchestrator never stores secrets.
- **Vault as credential source.** Enterprise IAM / vault provides scoped, time-bounded credentials. The orchestrator speaks the vault's API through a pluggable credential source interface. Reference implementations: HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager.
- **Container as enforcement.** Credentials exist only inside the container. Container destroyed = credentials gone. No ambient access, no leakage between projects.

### Credential Lifecycle

1. **Project initiation** → the orchestrator requests project-scoped credentials from the vault based on OAP requirements
2. **Mounted into project container** — available to all agents in the project (low risk) or scoped per role sub-container (high risk)
3. **OP boundary** → credentials rotated via vault (low risk, persistent container) or destroyed with the container (high risk)
4. **Demobilization** → container destroyed, credentials expire. No manual revocation needed.

### Demo Path

For an early reference demo, vault integration is simulated — credentials injected as environment variables from local config into the container. The interface is identical; only the source differs. This proves the architecture without requiring a live vault.

### No-Vault Case (small orgs)

Small orgs without enterprise vault use orchestrator-managed project tokens — the orchestrator generates scoped credentials and mounts them directly. Same container interface, orchestrator is both router and source. Upgrade path to a real vault is swapping the source behind the interface.
