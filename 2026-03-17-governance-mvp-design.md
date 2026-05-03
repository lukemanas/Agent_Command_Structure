# Governance Design — 2026-03-17

Design session working through the governance architecture one level below the lifecycle diagram. Covers all five lifecycle phases: Base Operating State, Initiating the Harness, Planning, Operational Period, and Demobilization (next steps). Cross-cutting sections cover Capability Governance, Data Governance, the Common Operating Picture, and Credential Management.

**Implementation targets:** Docker (containers), Tailscale (network identity/ACLs), enterprise vault (credentials). Design is implementation-agnostic — the architecture is described in terms of containers, network identity, and credential sources, not specific tools.

### MVP Checklist

1. Lifecycle phases exist and flow (base → harness → planning → OP → demob)
2. SOW and OAP as structured documents (schema exists, human approves)
3. Project container — created on initiation, destroyed on demob
4. Analyst/actor binary profiles — analyst on host, actor in container
5. Planning agent spawns, produces OAP, human approves
6. CoS spawns from OAP, creates issues, spawns crew
7. Checkin gate — validation before work begins
8. Timer — duration in OAP, CoS tracks, human extends
9. Verified-before-close — acceptance criteria on every objective
10. Human at the exits — approves OAP in, reviews ARR out, merges main
11. Branch protection — agents never touch main
12. Chain of command — workers → supervisors → CoS → human (protocol)

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

Transport encryption is a property of the network layer (WireGuard), not a separate enforcement mechanism. If protocol fails, the container boundary and network ACLs catch it.

### Three Components

1. **Registry** — source of truth for what profile an agent has. Informs all three layers.
2. **Container config** — translates profile into what's mounted (credentials, network access, volume mounts). Vault provides credentials, tank orchestrates. *(Layer 1: container boundary)*
3. **Network ACLs** — control what the container can reach, scoped by risk tier and OAP. *(Layer 2: network isolation)*
4. **Skills** — encode role behavior, chain of command, and constraints. The agent's instructions for how to operate within the framework. *(Layer 3: protocol)*

### Capability Profiles

Three profiles across the lifecycle:

**Agent as Analyst (base state, tank-scoped):**
- Runs on the host — no project container
- Inbox access and A2A messaging on the network
- No external credentials — cannot execute on external systems
- Skill: analyst skill (think, research, communicate, recommend)

**Agent as Planner (project-scoped):**
- Container config: inbox access + repo write credential from vault
- Skill: planner skill
- Initially gets actor container config; future: own planner profile with scoped planning permissions

**Agent as Actor (project-scoped):**
- Container config: full project credentials from vault, scoped by OAP. GitHub tokens, API keys, whatever the OAP defines.
- Skill: CoS / supervisor / worker skills
- Future: per-agent container configs based on OAP assignments

### Key Principles

- **Governance is subtractive.** Container starts empty — no credentials, no host access. The profile adds specific capabilities by mounting them.
- **Phase transition = container config event.** Enter planning → container gets planning credentials. Enter OP → container gets actor credentials and broader network ACLs. Demobilization → container destroyed, credentials expire.
- **Tank as orchestrator, vault as credential source.** Tank tells the vault what the agent needs (derived from the OAP), vault provides scoped, time-bounded credentials, tank mounts them into the container. Tank never stores secrets.
- **Binary profiles (analyst/actor) are sufficient.** Design for extensibility: container config as a composable set of mounts, ACLs, and credentials.

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
12. Tank spawns CoS → CoS goes through checkin gate (tank validates mechanical fields), gets actor keys
13. CoS orients — reads OAP, asks planning agent or human questions if needed
14. CoS creates GitHub issues from OAP objectives — adds operational detail (reporting, process, branching, blocked/done instructions)
15. CoS spawns crew based on OAP assignments — each agent goes through checkin gate (tank validates mechanical fields) AND comprehension validation (CoS validates the agent understands its assignment)
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
1. **Tank validates mechanical fields** — role, objective IDs, period state, risk tier. Exact match against COP. Hard enforcement — no keys without passing.
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
  skill           string    Skill to load (e.g., "fishtank:worker")
  tools           []string  Additional tools or access needed
```

Required fields: `period_number`, `duration`, `objectives` (id + title + criteria), `assignments` (role + skill). Everything else optional — planning agent fills what scope warrants, human demands what's missing.

**Issue (CoS creates from OAP, adds operational detail):**

The working unit during execution. CoS translates each OAP objective into a GitHub issue with operational detail — who to report to, what branch to work on, what to do when blocked or done.

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
- Issues become the live state — `tk cop` reads them
- Historical OAPs and ARRs accumulate in `history/period-N/`

### COP Initiation
The COP begins when the CoS creates issues (step 14). Before that, there's nothing to compute a view from. The CoS checkin (step 12) validates against the OAP directly, not the COP.

---

## Common Operating Picture (COP) — Cross-Cutting Design

The COP is the situational awareness layer that runs across Planning, Operational Period, and Demobilization. It is project-scoped.

> **TBD: This section depends on whether Tailscale replaces Redis or sits under it.** If Redis stays, the COP architecture (GitHub issues + Redis state) carries forward. If Redis is replaced, the persistence and state model needs rethinking. Awaiting Rob's input.

### Governing Principles

- **Information flows freely, direction flows through chain of command.** Any agent can read the COP. Orders and tasking go through the hierarchy. (From ICS: general staff can exchange information with anyone; direction follows the chain of command.)
- **Self-orientation.** Each agent is responsible for reading the COP and understanding its role. The system provides the picture; the agent maintains its own awareness.
- **Report up.** Agents must surface blockers, risks, and anomalies to their chain of command.
- **The COP is current state, not history.** It's a dashboard, not a feed. Overwritten, not appended.

### Architecture

**GitHub Issues = project management state.**
OAP approval creates GitHub issues — one per objective, assigned to agents, labeled with project/period, dependencies linked, acceptance criteria in the issue body. CoS and supervisors manage through GitHub: update issues, add comments, change labels, reassign.

**Redis = infrastructure state.**
Period state machine (phase, timer), agent registry (keys, profiles, checkin status), audit trail (append-only stream).

**`tk cop` = computed view.**
One command that reads GitHub issues + Redis state and returns a role-scoped view. No persistent COP document — computed on read, always current.

### Per-Role Views

**Worker sees:**
```
Project: tank-auth-rewrite
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

Every agent must demonstrate orientation before starting work.

> **TBD: The exact enforcement mechanism depends on the container and network model.** The sequence below describes the design intent — whether enforcement is container config, network ACLs, or application-level validation depends on Rob's answers.

**Sequence:**
1. Agent spawns into the project container with restricted access (can receive messages, can read COP)
2. Agent reads skill, reads COP
3. Agent runs checkin (declares its role, objectives, supervisor, period state, risk tier, constraints)
4. Tank validates each field against actual COP state (mechanical field comparison)
5. Pass → agent authorized to begin work (credentials/access scoped by role)
6. Fail → agent told what's wrong, retries. After N failures → killed, human notified.

**What this catches:** skill didn't load, hallucinated assignment, stale state.
**What it doesn't catch:** agent parrots fields without comprehension. Accepted tradeoff — to parrot correctly, the agent must read the COP and skill. Deeper comprehension is what review loops (CoS check-ins, demob) are for.

No agent bypasses this gate. CoS, supervisors, workers — same mechanism.

### COP Update Flow

1. **Tank updates mechanical state** — objective status (from GitHub), timer ticks, agent registration/deregistration. Deterministic, automatic.
2. **CoS/Supervisors update management context** — priorities, notes, reassignments, blockers requiring judgment. Written through GitHub issue updates.
3. **`tk cop` computes the merged view** — GitHub issues + Redis state, filtered by role.

---

## Operational Period — Design

### Design Principle: The Framework Scales with the OAP

Like ICS, the governance structure is always present but staffing scales with the work. A single-objective OAP uses the same invariants as a twenty-objective operation — one agent just wears all the hats. The framework should never be so heavy that people don't use it.

### Invariants (every OP, regardless of size)

1. **Timer** — human sets duration in OAP, tank tracks it, tank notifies CoS (or single agent) on expiry. Only human can extend (`tank period extend <duration>`).
2. **Checkin gate** — every agent proves orientation before starting work. Tank validates mechanical fields (role, objectives, period state, risk tier) against COP. Hard enforcement — no work without passing. The project container has credentials; the gate controls whether the agent is authorized to use them.
3. **Verified-before-close** — no objective closes without its acceptance criteria confirmed. Automated tests for code objectives (preferred wherever possible). Acceptance criteria confirmation for non-code objectives. Verification method recorded in the issue. Agents run verification, not tank.
4. **Human at the exits** — approves OAP going in, reviews ARR coming out, merges to main.
5. **Agents never touch main** — all work on feature/topic branches. Human merges after ARR approval. One merge commit = one rollback point for the entire OP's work.
6. **Complete audit trail** — every governance action during the OP is recorded: checkins, issue transitions, escalations, timer extensions, scope changes, agent failures, period completion. The OP must be fully reconstructable after the fact. Audit trail design lives in COP (TBD).

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
- **Human extends via command** — `tank period extend <duration>`. CoS explains the situation in natural language, the command is the approval.
- **Timer expiry without extension** — CoS tells agents to wrap up, collects status on incomplete work, transitions to Demobilization. Incomplete objectives documented in ARR, flow into the next OAP through the normal planning cycle.
- **CoS failing to anticipate timer expiry is a performance signal.**

### Period Completion

Two exits from the OP:

1. **All objectives verified-before-close** → CoS (or single agent) transitions to Demobilization.
2. **Timer expires** → CoS manages wind-down, then transitions to Demobilization with incomplete state.

### System Enforcement Summary

| Rule | Enforcement | Mechanism |
|------|------------|-----------|
| Checkin gate before work begins | System (hard) | Tank validates fields against COP |
| Project isolation | System (hard) | Container boundary — no host access, no cross-project access |
| Issue transitions are role-gated | System (hard) | Tank checks caller's role |
| Timer can't be extended by agents | System (hard) | Only human-authenticated command |
| Agents never touch main | System (hard) | Branch protection |
| Chain of command on messaging | System (hard) | Network ACL enforcement |
| Acceptance criteria verified before close | Protocol (soft) | Supervisor/CoS attests, human reviews at demob |
| Supervisor/CoS writes good tests | Protocol (soft) | CoS adversarial review |
| CoS does thorough review | Protocol (soft) | Human reviews at demob |

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

## Demobilization — Not Yet Designed

This phase needs the same level of design as Planning and Operational Period. Open questions:

- **Trigger** — what ends an OP (all objectives closed? timer expiry? human command?)
- **ARR structure** — required fields, who produces it, schema
- **Performance measurement** — dimensions, who evaluates, how it feeds back
- **Container teardown** — credential expiry, container destruction (high risk) or persistence (low risk), vault credential revocation
- **Issue cleanup / archival** — what happens to open issues, where does history live
- **Handoff to next OP** — ARR as prepared context, planning agent updates next OAP

### Cross-cutting (still open)
- Tailscale/Redis decision — does Tailscale replace Redis or sit under it? Blocks COP section.
- Network identity model — per-agent or per-machine? Blocks enforcement model details.
- Demo walkthrough — what's the 10-minute story through the lifecycle

---

## Credential Management — Decided

### Architecture

The container boundary closes the credential gap. Agents cannot access host credentials (~/.ssh, ~/.gitconfig, env vars) because they run inside project containers, not on the host.

- **Tank as orchestrator** — derives what credentials the project needs from the OAP, requests them from the vault, mounts them into the project container. Tank never stores secrets.
- **Vault as credential source** — enterprise IAM and keyvault provide scoped, time-bounded credentials. Tank speaks the vault's API through a pluggable credential source interface.
- **Container as enforcement** — credentials exist only inside the container. Container destroyed = credentials gone. No ambient access, no leakage between projects.

### Credential Lifecycle

1. **Project initiation** → tank requests project-scoped credentials from vault based on OAP requirements
2. **Mounted into project container** — available to all agents in the project (low risk) or scoped per role sub-container (high risk)
3. **OP boundary** → credentials rotated via vault (low risk, persistent container) or destroyed with the container (high risk)
4. **Demobilization** → container destroyed, credentials expire. No manual revocation needed.

### Demo Path

For the demo, vault integration is simulated — credentials injected as environment variables from local config into the container. The interface is identical; only the source differs. This proves the architecture without requiring a live vault.

### No-Vault Case (small orgs)

Small orgs without enterprise vault use tank-managed project tokens — tank generates scoped credentials and mounts them directly. Same container interface, tank is both orchestrator and source. Upgrade path to vault is swapping the source behind the interface.
