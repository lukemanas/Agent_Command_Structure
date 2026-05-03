# AI Agent Governance at Scale

> The biggest problem with diffusion is that nobody knows how to govern AI agents at scale.

This is a governance protocol. The ICS framing isn't a metaphor — it's a direct answer to the question every enterprise is asking: how do you deploy AI agents across a team without one person screwing everything up?

The answer is the same one emergency management found fifty years ago. You structure the work. You scope the communication. You put a human at every decision point. And you make the whole thing auditable so that when something breaks, you can trace it, roll it back, and fix the process.

---

## The Core Problem

AI agents are powerful and cheap to run. The hard part isn't capability — it's control. When you hand a CLI tool to a team, you need to know:

- **Who authorized what.** Which human approved which plan? Which supervisor dispatched which task?
- **Who can see what.** Can a worker read the general channel? Can an agent in one project eavesdrop on another?
- **What happened when.** If production breaks at 3am, can you trace it to a specific agent's operational period?
- **How to stop it.** Can you revoke an agent's access, kill its session, roll back its work?

Without structure, you get diffusion of responsibility. Twelve agents running, nobody in charge, and when something goes wrong nobody knows who did what or how to undo it.

---

## Human in the Loop — Always

The Incident Commander is always human. This isn't a philosophical stance about AI safety — it's operational necessity. Someone has to:

- Set objectives before agents start working
- Approve plans before agents execute them
- Review results at defined intervals
- Decide when to stop, scale up, or roll back

The human doesn't need to review every line of code. That's the whole point of the hierarchy — supervisors aggregate and filter so the human gets signal, not noise. But the human is always at the top, and nothing deploys without their sign-off.

In an enterprise context, "the human" might be a team. The cyber team reviews security-sensitive changes. The enterprise architecture team reviews structural decisions. The product owner reviews features. ICS handles this through Unified Command — multiple authorities sharing the IC role with a single voice. The structure supports it.

---

## Operational Periods and Review Cycles

An operational period is a bounded window of execution followed by a mandatory review. In ICS, this is typically 12 or 24 hours. The protocol uses two risk tiers (low / high) for the MVP — the binary classification drives container model, persistence, isolation, and review depth. The 4-tier cadence table below is a reference *configuration* an adopter can implement on top of the binary risk model, not a load-bearing part of the protocol.

### Risk-Based Review Cadence (illustrative)

| Cadence | Review Frequency | Example | Maps to |
|---------|------------------|---------|---------|
| **Critical** | Every agent turn | Production deployment, security-sensitive changes | High risk, short OP |
| **High** | Every 1-2 hours | Customer-facing features, data pipeline changes | High risk |
| **Moderate** | Every 4-6 hours | Internal tools, non-critical infrastructure | Low risk, short OP |
| **Low** | Every 12 hours | Documentation, research, prototyping | Low risk |

The protocol invariant is that an OP has a duration estimate and a mandatory review at the boundary. The cadence above is one adopter's calibration; the load-bearing risk classification is the binary tier (low / high) defined in the MVP design.

A halt mechanism is the enforcement primitive. When an agent's turn ends, the halt mechanism blocks until a human review passes. Implementations vary — Claude Code uses stop hooks, other runtimes use their own checkpoint primitives — but the protocol requires only that *some* halt mechanism exists, that the human can trigger it, and that an agent cannot bypass it.

This is the lever that makes AI agents deployable in regulated environments. The compliance team doesn't need to understand the code. They need to know: how often does a human review? What's the blast radius if something goes wrong between reviews? What's the rollback procedure?

### What Happens at a Checkpoint

At the end of every operational period:

1. **Run the full test suite.** Every agent or group is responsible for running tests and reporting results. Not just their tests — the full suite. If your change broke something in another module, the checkpoint catches it.
2. **Report status.** What was accomplished, what changed, what's still in progress, what's blocked. This is the ICS-209 (Incident Status Summary) — a structured briefing that anyone can read cold.
3. **Human reviews.** The IC (or delegated reviewer) reads the status, checks test results, and either approves the next period or intervenes.
4. **Transfer of command.** If the session is ending, the outgoing agent writes a briefing that the next session can pick up without context loss. Mandatory. Not optional.

The key difference between this and a fire: **you can roll back**. Every operational period produces a single identifiable rollback artifact (one merge commit per OP in the git reference). If a checkpoint reveals a problem, you revert to the last known-good state. The auditability is built in — version control history, agent activity logs, observation logs, and the audit event stream all create a paper trail that didn't exist in the 1970s.

---

## Risk-Tiered Model Selection

Not every ICS section needs the same resources. A Type 3 wildfire doesn't send its best tacticians to run the supply depot. The same principle applies to model selection.

Different agent roles have different risk profiles, and the model should match:

| ICS Section | Agent Role | Risk | Model Tier | Rationale |
|------------|-----------|------|-----------|-----------|
| **Command** | Human IC | — | Human judgment | Final authority, no delegation |
| **Planning** | Strategy/planning agents | High | Highest quality (Opus) | A bad plan wastes every downstream resource. The cost of a wrong strategy is multiplied across every agent that executes it. |
| **Operations** | Execution workers | Moderate | Mid-tier (Sonnet) | Executing well-defined tasks against a known plan. The plan already absorbs the complexity. |
| **Logistics** | Comms, context management | Low | Cheapest with largest context (Gemini) | Summarization, routing, context aggregation. Needs capacity more than reasoning depth. |
| **Safety** | Review/audit agents | High | High quality (Opus) | Catching mistakes requires the same depth as making the plan. |

This is resource optimization through role differentiation. You don't burn Opus tokens on a worker implementing a function that was fully specified by the planning agent. You don't trust Haiku with the strategic plan that determines whether the whole sprint succeeds or fails.

A conformant orchestrator should support per-role model selection. Planning agents on the highest-quality model, workers on a mid-tier, logistics on a high-context model — the protocol is the same; only the resource allocation changes.

---

## Planning Parallel to Operations

In real ICS, the Planning Section doesn't wait for Operations to finish before planning the next period. While today's teams are in the field executing the current Incident Action Plan, the Planning Section is already building tomorrow's IAP — running the Planning P cycle one period ahead.

The protocol supports this. A planning agent and an operations supervisor can run concurrently:

```
Human (IC)
├── Planning Agent (high-quality model)   ← building next period's task list
│   └── Research workers                  ← gathering context, analyzing options
└── Operations Supervisor                  ← executing current period's tasks
    ├── Worker 1 (mid-tier)
    ├── Worker 2 (mid-tier)
    └── Worker 3 (mid-tier)
```

The planning agent reads the current period's status via the COP (common operating picture), incorporates what's learned, and prepares the next period's assignments. When the current operational period ends and the checkpoint completes, the next period's plan is already written. The human reviews and approves it. Operations pivots without downtime.

This is how you sustain high throughput without sacrificing oversight. The human reviews at every boundary, but the machine never idles waiting for a plan.

### Broker Pods

When the span of control exceeds 5-7 workers, ICS calls for an intermediate supervisor layer. In this protocol, that's the **broker** — a Division Supervisor that automates the review pipeline for a single issue.

A broker pod is a three-agent unit:

```
Supervisor
├── Broker (high-quality model)   ← coordinates the review pipeline
│   └── Implementer                ← writes code (spawned by broker)
└── (other brokers/workers)
```

The broker receives an issue from the supervisor, spawns an implementer, and runs:
1. **Plan review** — implementer writes plan, broker runs an ephemeral review (typically a different model family for adversarial diversity)
2. **Code review** — implementer writes code, broker runs an ephemeral review
3. **Report** — broker reports the approved branch to the supervisor

Each review step loops up to 5 rounds before escalating. The broker does not edit files, merge, manage labels, or contact the human. The authority chain is unchanged: broker → supervisor → chief-of-staff → human.

Killing a broker cascades to children — killing the broker also kills its implementer.

---

## Enterprise Deployment

The governance structure maps directly to enterprise compliance requirements:

### Audit Trail

Every action produces records across multiple systems:

| Record Type | System | Retention |
|------------|--------|-----------|
| Code changes | Version control commits (standardized, per-period) | Permanent |
| Agent activity | Observation / narration log | Configurable |
| Communication | Persistent messaging substrate (encrypted at rest and in transit) | Configurable |
| Test results | Reported at each checkpoint | Per-period |
| Authorization | Human approvals in the audit event stream (`oap.approved`, `arr.approved`, etc.) | Permanent |
| Governance actions | Audit event stream (see audit-event-schema.md, 27 typed events) | Permanent (5+ years for regulated industries) |

### SOPs for Review Teams

The operational period structure creates natural insertion points for enterprise review processes:

- **Cyber/Security team** reviews at every checkpoint for production-bound changes. The test suite includes security scans. Results are part of the status report.
- **Enterprise architecture** reviews at period boundaries when structural changes are proposed. The planning agent's output includes architectural impact analysis.
- **Product/editorial** reviews at period boundaries for user-facing changes. The status report includes before/after descriptions.

These teams don't need to be in the loop on every agent turn. They review at the cadence that matches their risk tolerance — and the operational period structure guarantees they'll have a clean checkpoint to review against.

### Access Control

Scoped communication isn't just about efficiency — it's about information security:

- Workers can only read their own session DMs. They can't see other workers' tasks, other projects' channels, or the human's DM stream.
- Supervisors see their workers' reports and the project channel. They don't see other supervisors' workers.
- The human sees everything — general, DMs, all project channels.
- Authenticated encryption on the messaging substrate ensures that infrastructure access does not imply message-content access. Adopters select the algorithm; the protocol requires authenticated encryption at rest and in transit.

This maps to enterprise IAM. Different roles get different visibility. The scoping is enforced by the protocol and by the substrate's network/IAM controls, not by trust.

### Rollback Procedure

When a checkpoint reveals a problem:

1. Identify which operational period introduced the issue (version-control history + audit event stream)
2. Identify which agent and task were responsible (audit event stream — `agent.spawned`, `issue.transitioned`, etc.)
3. Revert to the last known-good commit
4. Re-run the test suite to confirm the revert is clean
5. Reassign the failed task with corrected instructions

Unlike a wildfire, every state is recoverable. The standardized commit discipline (one commit per operational period, tests passing at each boundary) means you always have a clean rollback point.

---

## The Governance Stack

The protocol layers (top three) are what gets standardized. The substrate layers (bottom three) are adopter choice — every adopter brings their own implementation.

```
┌─────────────────────────────────────────────────────┐
│                   GOVERNANCE LAYER                   │  ← protocol
│  Risk tiers · Review cadences · Model selection      │
│  SOPs · Audit event schema · Rollback procedure      │
├─────────────────────────────────────────────────────┤
│                   COMMAND LAYER                       │  ← protocol
│  Human IC · Unified Command · Operational periods    │
│  Checkpoints · Transfer of command                   │
├─────────────────────────────────────────────────────┤
│                 COORDINATION LAYER                    │  ← protocol
│  Supervisors · Workers · Span of control             │
│  Chain of command · Unity of command                  │
├─────────────────────────────────────────────────────┤
│                COMMUNICATION SUBSTRATE                │  ← adopter
│  Persistent messaging · Scoped channels · Auth crypto │
│  Halt mechanism · Persistent mailboxes                │
├─────────────────────────────────────────────────────┤
│                OBSERVATION SUBSTRATE                  │  ← adopter
│  Activity logs · COP store · Cross-machine sync      │
├─────────────────────────────────────────────────────┤
│                 EXECUTION SUBSTRATE                   │  ← adopter
│  VCS · Tests · Deployment pipeline · Code changes    │
│  Per-OP rollback artifact (one merge commit)         │
└─────────────────────────────────────────────────────┘
```

The governance layer sits on top — it doesn't replace the substrate, it structures how the substrate is used and who reviews what. Different adopters can swap the substrate (Redis vs. NATS, GitHub vs. Linear, Tailscale vs. Calico) and the governance layer is unchanged.

---

## Why ICS Works Here

ICS wasn't designed for AI. It was designed for a simpler problem: how do you coordinate hundreds of people from different agencies who've never worked together, under extreme time pressure, with lives at stake?

The answer was: standardize everything. Standardize the roles so anyone can fill any position. Standardize the forms so anyone can read any report. Standardize the communication so information flows through defined channels. And put a human in charge — always — because someone has to be accountable.

AI agent coordination has the same failure modes at lower stakes. Agents from different model families, different sessions, different machines. No shared context. No shared terminology. No clear hierarchy. The fix is the same fix, because the problem is the same problem: coordination fails not from lack of capability, but from lack of management discipline.

This protocol implements that discipline as infrastructure. The semantics are in the spec. The hierarchy is in the addressing. The checkpoints are in the lifecycle phases and the halt mechanism. And the human is always in the loop — not because we don't trust the agents, but because governance requires it.
