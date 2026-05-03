# ICS (Incident Command System) — Research Report
## Mapping to AI Agent Coordination

> Prepared for: fishtank / attend agent coordination design
> Date: 2026-02-22

---

## Overview

The Incident Command System (ICS) is a standardized, on-scene, all-hazards incident management approach that was developed in the 1970s after communication failures during large California wildfires. It has since become the national standard for emergency incident management in the US (mandated under NIMS — National Incident Management System). The core insight: command structures fail not from lack of resources, but from lack of management discipline — unclear roles, skipped levels, ad-hoc terminology, and span-of-control violations.

The reason ICS is relevant to AI agent coordination: the same failure modes exist. Agents create unclear handoffs, skip levels, invent their own terminology, and overload supervisors. ICS has solved these problems for humans. The solutions translate directly.

---

## 1. Five Functional Sections

Every ICS organization has exactly five sections. At small incidents (Type 4-5), one person fills all roles. At large incidents (Type 1-2), each section may have hundreds of personnel. The structure is always the same.

```
                    ┌─────────────────────┐
                    │   Incident Command  │
                    │  (IC / Unified CMD) │
                    └──────────┬──────────┘
                               │
         ┌──────────┬──────────┼──────────┬──────────┐
         ▼          ▼          ▼          ▼          ▼
    Operations   Planning   Logistics  Finance/   Safety*
      Section     Section   Section    Admin      (Staff)
```

*Safety, Public Information, and Liaison are Command Staff positions that report directly to the IC, not section chiefs.

### Operations Section
- Directs all tactical field resources
- Responsible for carrying out the incident objectives
- Has direct control over branches, divisions, groups, and task forces
- Operations Section Chief is the "hands" of the IC

### Planning Section
- Collects, evaluates, and disseminates information
- Develops the Incident Action Plan (IAP) for each operational period
- Tracks resources (check-in/check-out)
- Maintains situation status and resource status
- "Situational awareness engine" — keeps the IC informed

### Logistics Section
- Provides all support resources: communications, facilities, food, transportation, medical
- Ensures personnel have what they need to operate
- Manages supply, ground support, communications, food, medical units

### Finance/Administration Section
- Tracks all costs, contracts, compensation, and time
- Usually only activated at extended incidents
- Provides cost-benefit analysis for resource decisions

### Command (IC / Unified Command)
- Single point of accountability for all incident objectives
- Sets priorities, approves IAP, manages overall strategy
- In Unified Command, multiple ICs from different agencies share the role with a single voice
- The IC is the **human in the loop** — only one person (or unified group) holds command authority

---

## 2. The 14 NIMS Management Characteristics

These are the foundational principles that make ICS work across all incident types and agencies:

1. **Common Terminology** — Standardized names for organizational functions, resource types, and facilities. No 10-codes, no agency-specific jargon. "Plain English only."
2. **Modular Organization** — Structure expands top-down based on complexity. Only what's needed is activated.
3. **Management by Objectives** — Specific, measurable goals drive all activity. Everyone knows what success looks like this period.
4. **Incident Action Planning** — Written plan for each operational period capturing priorities, objectives, strategies, assignments.
5. **Manageable Span of Control** — 1 supervisor : 3-7 subordinates. Optimal is 1:5. Violation of this is a red flag.
6. **Incident Facilities and Locations** — Designated, standardized locations: Incident Command Post, Staging Area, Base Camp, etc.
7. **Comprehensive Resource Management** — Resources are tracked from pre-deployment through demobilization. Every resource has a status at all times.
8. **Integrated Communications** — Common comms plan established before operations. Interoperable. Plain language.
9. **Establishment and Transfer of Command** — Clear process for designating IC and handing off. Briefing is mandatory.
10. **Chain of Command and Unity of Command** — Orderly hierarchy. Every person reports to exactly one supervisor. No dotted lines. No matrix reporting.
11. **Unified Command** — Multi-agency incidents can share command while maintaining single voice.
12. **Accountability** — Check-in/check-out. Every person tracked. No self-deployment.
13. **Dispatch/Deployment** — Resources deploy ONLY when requested through established systems. No freelancing.
14. **Information and Intelligence Management** — Structured processes for gathering, analyzing, and sharing incident info.

---

## 3. Incident Types — 5-Level Classification

Incidents are typed 1-5 (5=smallest, 1=largest). The type determines what level of ICS structure to activate.

| Type | Complexity | Personnel | Duration | Resources |
|------|-----------|-----------|----------|-----------|
| 5 | Minimal | 1-6 | Single operational period | 1-2 single resources |
| 4 | Low | <25 | Single op period, first 6-12h | Local jurisdiction |
| 3 | Moderate | Up to 200/period | Multiple op periods | Some out-of-area resources |
| 2 | High | Up to 500/period | Multiple periods, multi-day | Regional/national resources |
| 1 | Extreme | 500+ | Weeks to months | National; all sections fully staffed |

### Type 5 (Minimal)
- IC fills all Command and General Staff roles
- No formal IAP required (verbal is fine)
- Contained within one operational period
- Example: a fender-bender, a small brush fire, a single-agent task

### Type 4 (Low)
- A few positions formally activated beyond IC
- Simple written IAP may be produced
- Local resources sufficient
- Example: a multi-car accident, a 2-3 agent coordinated task

### Type 3 (Moderate)
- Incident Management Team (IMT) activated
- All Command and General Staff positions filled
- Written IAP required
- Multiple operational periods
- Example: a week-long wildfire, a major software incident, a sustained multi-team project

### Type 2 (High)
- Beyond local capabilities; regional resources engaged
- Full ICS organizational chart activated
- Requires national resource support
- Example: a major hurricane response

### Type 1 (Extreme)
- National mobilization
- Full ICS organization, potentially thousands of personnel
- Weeks to months duration
- Examples: 9/11 response, Deepwater Horizon, COVID-19

**Key principle**: Incidents can be typed DOWN as well as up. When conditions improve, demobilize. The same system that handles a Type 5 (one person) scales to a Type 1 (thousands) without changing the structure.

---

## 4. Operational Periods

An **operational period** is the scheduled time for execution of a given set of tactical actions. It is the fundamental time unit of ICS operations.

### Duration
- **Typically 12 or 24 hours** for active incidents
- Fast-moving incidents: 12-hour shifts (two per day)
- Slower incidents: 24-hour periods
- Very small incidents (Type 5): single operational period, no cycle needed

### The Planning Cycle ("Planning P")
The Planning P is the visual representation of how each operational period is planned:

```
                    Incident
                   Objectives
                       │
                       ▼
               Strategy Meeting
                       │
                       ▼
               Tactics Meeting
                       │
                       ▼
           Planning Meeting (IAP finalized)
                       │
                       ▼
        Operational Period Briefing ("Shift Brief")
                       │
                       ▼
              OPERATIONS EXECUTE
                       │
                       ▼
               (next period begins)
```

### What Happens at Period Boundaries

**End of period:**
- Outgoing IC/section chiefs debrief: what happened, what changed, resource status
- Documentation completed (ICS-209 status summary, ICS-211 check-in/out)

**Transfer of command briefing (mandatory):**
1. Incident history and current status
2. Objectives and current IAP
3. Resource assignments and org chart
4. Resources ordered but not yet arrived
5. Facilities established
6. Communications plan
7. Constraints, limitations, and hazards
8. Incident potential for next period

**Beginning of period:**
- Operations Period Briefing: all operational supervisors briefed on objectives, assignments, comms, safety
- Supervisors brief their subordinates before going operational

**Critical rule**: The incoming IC must be fully briefed before assuming command. A partial handoff is worse than no handoff.

---

## 5. Span of Control

The single most important structural principle in ICS:

> **One supervisor to no more than 7 subordinates. Optimal is 1:5. Minimum is 1:3.**

If a supervisor is managing more than 7 resources, they must reorganize — add a layer (branch, division, group) and delegate. If managing fewer than 3, consider consolidating.

### Why This Number Works
- Human working memory can track ~5 active items
- Under stress, effective span drops further
- At 7+, supervisors lose situational awareness and begin to fail
- At 3-, the overhead of the supervisory layer isn't justified

### Organizational Expansion Triggered by Span
When Operations has too many resources for one Operations Section Chief:
1. Add **Branches** (by geography or function)
2. Add **Divisions** (geographic) or **Groups** (functional) under branches
3. Add **Task Forces** (mixed resources with a common comm channel) or **Strike Teams** (same-type resources)

Every expansion creates a new supervisor who reports to exactly one person above them.

---

## 6. Standardized Roles and Position Descriptions

Every ICS position has:
- A standardized title
- A standardized position description (what you do, what you're responsible for)
- Qualification requirements (training, experience, certification)
- A Position Task Book for trainees

**Key positions at every incident:**

| Position | Level | Reports To | Function |
|----------|-------|------------|----------|
| Incident Commander (IC) | Command | Agency/Jurisdiction | Overall command authority |
| Safety Officer (SO) | Command Staff | IC | Identifies/mitigates safety hazards |
| Public Information Officer (PIO) | Command Staff | IC | Media, public communications |
| Liaison Officer (LOFR) | Command Staff | IC | Coordinates with other agencies |
| Operations Section Chief (OSC) | General Staff | IC | Tactical execution |
| Planning Section Chief (PSC) | General Staff | IC | Situational awareness, IAP |
| Logistics Section Chief (LSC) | General Staff | IC | Support and resources |
| Finance/Admin Section Chief (FSC) | General Staff | IC | Costs and administration |
| Branch Director | Operations | OSC | Manages 3-5 divisions/groups |
| Division/Group Supervisor | Operations | Branch or OSC | Manages 3-7 resources |
| Task Force Leader | Operations | Division/Group | 2-5 resources, same task |
| Strike Team Leader | Operations | Division/Group | Same-type resources, common task |

**Plug-and-play principle**: Any ICS-qualified person can fill any ICS position anywhere in the country. The position description is standardized. There is no "our way of doing it" — only the ICS way.

---

## 7. Standard Forms (ICS-200 through ICS-225+)

ICS has standardized every document that flows through an incident. This eliminates ambiguity and ensures complete information transfer.

| Form | Name | Purpose |
|------|------|---------|
| ICS-201 | Incident Briefing | Initial incident documentation; used for transfer of command briefings; captures situation, objectives, resource summary, org chart |
| ICS-202 | Incident Objectives | Basic strategy, objectives, priorities, safety considerations for an operational period |
| ICS-203 | Organization Assignment List | Who is filling which ICS position; the org chart in tabular form |
| ICS-204 | Assignment List | Individual assignments for each division/group; what you do this period |
| ICS-205 | Incident Radio Communications Plan | Every radio channel, frequency, assignment, purpose |
| ICS-205A | Communications List | Phone numbers, contact info for all key personnel |
| ICS-206 | Medical Plan | Medical aid stations, hospital locations, medical procedures |
| ICS-207 | Incident Organization Chart | Visual org chart |
| ICS-208 | Safety Message | Safety hazards, mitigation measures for the period |
| ICS-209 | Incident Status Summary | High-level summary for leadership, EOC, media; incident status, resources, objectives, weather |
| ICS-210 | Resource Status Change | Tracks changes to resource status (assigned, available, out of service) |
| ICS-211 | Check-In/Out List | Every person and resource entering or leaving the incident |
| ICS-213 | General Message | Written message form; used when voice comms can't reach recipient |
| ICS-213 RR | Resource Request | Formal request for additional resources |
| ICS-214 | Activity Log | Running log of significant events for any position |
| ICS-215 | Operational Planning Worksheet | Documents tactical decisions for next operational period |
| ICS-215A | Incident Action Plan Safety Analysis | Identifies hazards associated with tactics in the IAP |
| ICS-220 | Air Operations Summary | All aircraft assignments, frequencies, airspace |
| ICS-225 | Incident Personnel Performance Rating | Post-incident evaluation of personnel performance |

**Why standardization matters**: When an out-of-area team arrives, they can pick up any form and immediately understand the incident status. There is no learning curve for the paperwork.

---

## 8. Communication Protocols

ICS communication has strict protocols designed to prevent the failures that killed firefighters in 1970:

### Plain Language
- **No 10-codes.** No agency-specific jargon. Plain English at all times.
- Everyone uses the same words for the same things.

### Chain of Command — Information Flow
- Information flows UP the chain: field → division/group supervisor → branch director → OSC → IC
- Assignments flow DOWN the chain: IC → OSC → branch → division → resource
- **You never skip a level.** A resource does not report directly to the IC; they report to their supervisor who aggregates and escalates.
- A resource does not receive assignments from anyone other than their direct supervisor.

### Common Operating Picture
- Planning Section is responsible for maintaining the COP — the shared situational awareness of all incident elements
- Everyone should have the same picture; no one should be working with outdated information
- Information that affects the COP must flow up the chain immediately

### Operational Radio Protocols
- Each operational period has a written communications plan (ICS-205)
- Channels are assigned by function (command channel, tactical channel, support channel, etc.)
- Net control manages channel traffic
- All significant transmissions are logged

### The ICS-213 General Message
- When voice communication can't reach someone or when a message needs to be in writing, use ICS-213
- Three-part form: sender, message, response
- Creates a paper trail for all significant communications

---

## 9. Modularity — The Key Strength

The same system that handles a Type 5 (one person) handles a Type 1 (5,000+ people). This is not a metaphor — the forms are the same, the titles are the same, the principles are the same.

### Type 5: One Person, All Roles
```
IC (also: OSC, PSC, LSC, FSC)
├── Resource A
└── Resource B
```
The IC does everything. No forms required beyond ICS-201 if they feel like it.

### Type 4: IC + Some Staff
```
IC
├── Safety Officer (if needed)
├── Resource A
├── Resource B
└── Resource C
```
Still simple. Verbal IAP. IC stays in the loop on everything.

### Type 3: Full Command Staff
```
IC
├── Safety Officer
├── PIO
├── Operations Section Chief
│   ├── Division A Supervisor
│   │   ├── Strike Team 1
│   │   └── Strike Team 2
│   └── Division B Supervisor
│       └── Task Force 3
├── Planning Section Chief
├── Logistics Section Chief
└── Finance Section Chief
```
Written IAP required. 12-24 hour operational periods. Multiple teams.

### Type 1: Full Activation
Every section fully staffed with branches under Operations, multiple shifts, dozens of ICS forms generated per operational period, external agency coordination, public information operations.

**The critical insight**: Every person who trains in ICS can operate effectively at any type level because the system is modular and the positions are standardized. You don't need different training for Type 5 vs Type 3. You need the same training applied at different scales.

---

## 10. Mapping ICS to AI Agent Coordination

This section maps each ICS concept to fishtank/attend patterns.

### Events as Containers (ICS: Incidents)

| ICS | Agent Pattern |
|-----|--------------|
| Incident | A task/project/investigation — the container for all coordination |
| Incident name | Project or channel name in fishtank (e.g., `tank`, `datateam`) |
| Incident type (1-5) | Complexity level: Type 5 = single agent, Type 1 = full fleet |
| Incident duration | Task scope: single-session vs multi-day vs ongoing |

**A fishtank "event" is an ICS incident.** It has a defined scope, a defined IC (human), and a beginning and end. Agents don't persist between events — they mobilize and demobilize.

### Incident Commander = Human in the Loop

| ICS | Agent Pattern |
|-----|--------------|
| Incident Commander | The human (Rob) or a designated human supervisor |
| IC sets objectives | Human defines task goals before agents begin |
| IC approves IAP | Human reviews/approves supervisor's plan before execution |
| IC is the single authority | All final decisions route to the human; no autonomous consensus |
| Command staff report to IC | Supervisor agents report to human |

**No "dotted line" relationships.** A worker reports to exactly one supervisor. A supervisor reports to the IC (human). The human is not optional — removing the IC makes it not ICS, it makes it autonomous chaos.

### Five Sections → Agent Roles

| ICS Section | Agent Role Equivalent |
|------------|----------------------|
| Operations | Worker agents — do the actual work (code, search, write) |
| Planning | Supervisor agents — build the plan, track status, update COP |
| Logistics | Resource-fetching agents — spawn new workers, manage tools |
| Finance/Admin | Not currently needed (cost tracking is the human's problem) |
| Command Staff (Safety) | Review agents — check work product for correctness |

In practice, a supervisor agent fills both Planning and Logistics roles for small events.

### Span of Control → Supervisor:Worker Ratio

| ICS | Agent Pattern |
|-----|--------------|
| 1:5 optimal span | One supervisor manages 3-7 worker agents |
| >7 requires expansion | Add an intermediate supervisor level |
| <3 consolidate | A supervisor with one worker is overhead |

A supervisor with 8 active workers is in violation of ICS principles. The fix: add a Branch Director (senior supervisor) who manages two Supervisors, each with 3-4 workers.

### Operational Periods → Session Cycles

| ICS | Agent Pattern |
|-----|--------------|
| 12-hour operational period | A single Claude Code session (~hours) |
| Period briefing | Context handoff at session start (CLAUDE.md, clog prime, attend glimpse) |
| IAP | The task list for this session (clog tasks) |
| Transfer of command briefing | Session handoff: clog sync, git push, status DM to human |
| Period documentation | clog log entries, attend narrations, git commits |

**The end-of-session protocol IS a transfer of command.** It must include: what was accomplished, what changed, resource status (what's still running), outstanding orders, and incident potential (what to expect next session).

### Standardized Forms → Structured DMs

| ICS Form | Agent Pattern |
|----------|--------------|
| ICS-201 (Incident Briefing) | Session start DM: "I'm claude:fab8, assigned to tank, here's my status and plan" |
| ICS-202 (Objectives) | clog task list shared with human at start of session |
| ICS-204 (Assignments) | Supervisor DM to worker: "Task: [description]. Report to claude:fab8 when done." |
| ICS-209 (Status Summary) | Periodic status DM to human: "Here's what's done, what's in progress, what's blocked" |
| ICS-213 (General Message) | fishtank DM with `tk s source:prefix@user "message"` |
| ICS-214 (Activity Log) | clog log entries |
| ICS-211 (Check-in/Check-out) | `tk register` / `tk deregister` hooks |

The worker protocol already implements ICS-213 (DM to supervisor when task complete). The gap is ICS-209: periodic status summaries from supervisor to human.

### Chain of Command → No Skipping Levels

| ICS Rule | Agent Rule |
|----------|-----------|
| Resources report only to their direct supervisor | Worker sends DM to `claude:sup-prefix@user`, not to `@rob` |
| Never skip a level | Worker doesn't DM the human directly unless the supervisor is unreachable |
| Assignments flow down only from direct supervisor | Worker only acts on tasks from its supervisor, not from other workers or other supervisors |

**The current fishtank protocol partially enforces this.** Workers use `claude:fab8@rob` (supervisor session DM), not `@rob` (human DM). The gap: workers sometimes `tk s @rob` directly when they should escalate through the supervisor.

### Unity of Command → Single Supervisor

| ICS Rule | Agent Rule |
|----------|-----------|
| Every person has exactly one supervisor | Every worker is assigned to exactly one supervisor agent |
| No matrix reporting | A worker does not receive tasks from both supervisor A and supervisor B |
| Reassignment requires formal process | A worker can only be re-tasked by their supervisor or by the IC (human) |

### Common Terminology → Standardized Role Labels

| ICS | Agent Pattern |
|-----|--------------|
| "Operations Section Chief" | `--status supervisor` in wait mode |
| "Worker" (resource) | `--status worker` in wait mode |
| Standard position titles | Standard `tk wait --status` values |
| "Incident" | "Event" or "project" in fishtank |
| "Operational period" | "Session" |

The `tk wait --status supervisor/worker` pattern is already implementing ICS terminology. Extend this: `--status planner`, `--status reviewer`, `--status logistics` could map to more specific ICS roles.

### Modularity → Single-Agent to Fleet

| ICS | Agent Pattern |
|-----|--------------|
| Type 5: IC fills all roles | One Claude session does everything |
| Type 4-3: IC + a few staff | Human + one supervisor agent + 2-3 workers |
| Type 2-1: Full activation | Human IC + multiple supervisor agents + full worker fleet |

The system should work the same whether it's one agent or fifty. The forms (DM protocols), chain of command, span of control — all apply at both scales. A human shouldn't need to learn "fleet mode" vs "solo mode" — ICS scales both ways invisibly.

### Transfer of Command — The Critical Gap

The weakest point in current agent coordination is the **transfer of command**. When a session ends:
- There is no mandatory briefing structure
- The next session has no standardized way to receive incident status
- Workers may have outstanding tasks with no supervisor to report to

**ICS fix**: Every session end requires a transfer-of-command briefing equivalent, covering:
1. What was accomplished (done clog tasks)
2. What is in progress (in_progress clog tasks + who owns them)
3. Resources outstanding (active worker sessions)
4. Orders placed but not yet filled (tasks dispatched but not confirmed)
5. Constraints and blockers
6. Incident potential (expected next steps)

This maps directly to the current session-close protocol: `clog sync`, `git push`, status DM to human. The missing piece: a formal ICS-201-equivalent DM that the next supervisor can read cold.

---

## 11. What ICS Gets Right That Most Systems Get Wrong

1. **Discipline over capability.** ICS success comes from following the process, not from how smart individual participants are. A mediocre but disciplined team beats a brilliant but undisciplined one.

2. **Scalability is built in, not bolted on.** You don't "switch to fleet mode" — you just add layers when span of control is violated.

3. **Documentation drives accountability.** Every assignment is written down. Every resource is tracked. No "I thought you were handling that."

4. **Transfer of command is a ritual.** Not optional, not informal. The incoming IC cannot assume command without a briefing. This prevents the catastrophic "I thought they knew" failure.

5. **The IC is always human.** ICS has never contemplated a non-human Incident Commander. The human has situational awareness, moral authority, and accountability that no system can replicate. Agents are resources — they don't command; they execute.

6. **Common terminology enables interoperability.** Any trained person can walk into any incident and immediately understand the structure. This is the goal for AI agents: any Claude session should be able to read a supervisor's DMs and immediately understand the situation.

---

## Sources

- [ICS Organizational Structure and Elements — FEMA](https://training.fema.gov/emiweb/is/icsresource/assets/ics%20organizational%20structure%20and%20elements.pdf)
- [14 Management Characteristics of NIMS — EMSI](https://www.emsics.com/resources/reference-documents/14-management-characteristics-of-nims/)
- [Incident Command System — Wikipedia](https://en.wikipedia.org/wiki/Incident_Command_System)
- [NIMS Incident Complexity Guide — FEMA](https://www.fema.gov/sites/default/files/documents/nims-incident-complexity-guide.pdf)
- [Incident Action Planning Process "The Planning P" — FEMA](https://training.fema.gov/emiweb/is/icsresource/assets/incident%20action%20planning%20process.pdf)
- [Transfer of Command — FEMA](https://training.fema.gov/emiweb/is/icsresource/assets/transfer%20of%20command.pdf)
- [Common ICS Forms Descriptions — EMSI](https://www.emsics.com/resources/icsforms/common-ics-forms-descriptions/)
- [ICS 200 — Lesson 2: ICS Features and Principles — USDA](https://www.usda.gov/sites/default/files/documents/ICS200Lesson02.pdf)
- [Incident Command System: History, Structure, and Modern Applications — Silent Beacon](https://silentbeacon.com/incident-command-system-ics-history-structure-and-modern-applications/)
- [EMS Incident Command System — StatPearls/NCBI](https://www.ncbi.nlm.nih.gov/books/NBK441863/)
- [Incident Complexity: Comparing Industry Tiers and NIMS Incident Types — EMSI](https://www.emsics.com/incident-complexity-comparing-industry-tiers-nims-incident-types/)
- [Wildland Fire ICS Levels — National Park Service](https://www.nps.gov/articles/wildland-fire-incident-command-system-levels.htm)
