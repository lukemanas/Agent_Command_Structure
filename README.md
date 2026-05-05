# Agent Command Structure (ACS)

Theoretical framework for a substrate-agnostic governance protocol for coordinating fleets of agents under human authority. Adapted from the Incident Command System (ICS / NIMS) — the federally mandated coordination framework that has run US emergency response, hospital incident management, and critical infrastructure operations for fifty years.

## Why this exists

**The limiting factor on scaling agentic infrastructure is the capacity of humans to direct and control it.** A frontier-AI deployment is not a single model — one of the major advantages of AI is massive parallelism, with many instances, often heterogeneous, working against problems too large for any one of them. You want tactical authority distributed but aligned. Deployment at that scale introduces failure modes that a one-to-one human-agent interaction does not. How do you coordinate across so many actors? How do small misunderstandings of the common operating picture aggregate up to systemic failure? How do you limit blast radius and ensure agents only act within their authority?

These are not novel problems. We have been managing large fleets of independent minds — minds that communicate in natural language and exercise judgment under uncertainty — for all of human history. That is what organizations are. A CEO does not know what each individual worker does on a given Tuesday; they manage at a layer of abstraction, through accountability structures, performance controls, and risk tolerance. Agents change the speed and the scale, not the structure of the problem. The bottleneck stays where it has always been: a single human's capacity to direct, observe, and intervene is finite, and it does not grow with fleet size.

The Incident Command System (ICS / NIMS) addresses exactly this in human contexts. It is a command-and-collaborate structure in which one person is accountable for the outcome, authority is delegated explicitly, and coordination scales without changing the structure of accountability. Many of its principles — plan before execute, management by objectives, transfer of command — already show up as emerging best practices in agentic coding and orchestration. ACS adapts those mechanisms to the agentic context.

## Governing principles

1. **Human Authority** — Humans command, agents execute. Every agent has a named human principal. Irreversible actions require explicit human authorization.
2. **Command Authority** — Unity of command: one supervisor per agent. Chain of command is directional — assignments down, status up. No level-skipping.
3. **Management by Objectives** — Every agent has a specific, assessable objective per period. No freelancing — report out-of-scope findings, don't act on them.
4. **Plan Before Execute** — No agent deploys without an approved OAP. Work runs in bounded operational periods.
5. **Situational Awareness** — Common Operating Picture scoped by role. The IC sees everything; workers see their assignment.

These are the load-bearing principles. The full set — including the formal premises (P1–P70) and the 14 NIMS Management Characteristics they extend — lives in [`supporting-research/premises.md`](supporting-research/premises.md) and [`supporting-research/ics-research.md`](supporting-research/ics-research.md).

## Regulatory fit

The audit-event schema and authorization matrix were designed to generate the artifacts the EU AI Act requires of high-risk systems (enforcement: August 2, 2026). A draft crosswalk in [`supporting-research/compliance-mapping.md`](supporting-research/compliance-mapping.md) (currently flagged stale, pending rebuild against the current substrate-agnostic spec) maps protocol-level controls against:

- **EU AI Act** — Articles 12 (record-keeping), 14 (human oversight), 19 (log retention)
- **NIST AI RMF** and **NIST CSF 2.0**
- **ISO 42001** (AI management systems) and **ISO 27001**

The concrete artifacts: 27 typed audit events emitted across the lifecycle, a role-gated authorization matrix, and an After-Action Review with a named human decision on every operational period.

The protocol as specified addresses these requirements structurally — the lifecycle, the audit stream, and the human checkpoints map directly to record-keeping, log-retention, and human-oversight obligations. Today the benefit is partial but real: a lightweight implementation can satisfy compliance at the protocol layer, but realizing it in production still requires bespoke wiring into a specific agent runtime. Embedded in a platform — where the runtime itself enforces checkin gates, role transitions, and verified-before-close — the same protocol produces compliance evidence by default. That is the form in which the regulatory benefit becomes wide-reaching.

## What's in this repo

- [**`governance-protocol.md`**](governance-protocol.md) — the canonical specification. Threat model, lifecycle phases, authorization matrix, OAP/ARR schemas, identity & authentication boundary.
- [**`reference/`**](reference/) — minimal Python reference implementation. Demonstrates the protocol's enforcement points in a single-machine CLI (schema gates, role-gated transitions, verified-before-close, audit trail). Includes a runnable demo and optional integration with real Claude Code agents.
- [**`supporting-research/`**](supporting-research/) — the body of work behind the protocol:
  - [`premises.md`](supporting-research/premises.md) — formal premises (axiom / derived / empirical) with explicit dependencies
  - [`protocol-plan.md`](supporting-research/protocol-plan.md) — the five-component decomposition
  - [`audit-event-schema.md`](supporting-research/audit-event-schema.md) — 27 typed governance events, EU AI Act mapped
  - [`ics-research.md`](supporting-research/ics-research.md) — ICS / NIMS source material and its mapping to agent coordination
  - [`compliance-mapping.md`](supporting-research/compliance-mapping.md) — draft crosswalk against EU AI Act, NIST, and ISO frameworks (currently flagged stale, pending rebuild)
- [**`Agent_CS.excalidraw`**](Agent_CS.excalidraw) — visual reference of the lifecycle and enforcement layers.

## Status

ACS is a research artifact in three phases.

1. **Protocol design** — the canonical specification ([`governance-protocol.md`](governance-protocol.md)) and the supporting research (premises, audit-event schema, compliance crosswalk, ICS source material). Substantially complete; in active iteration.
2. **Reference architecture** — the minimal Python CLI in [`reference/`](reference/) demonstrates the protocol's enforcement points across the lifecycle (schema gates, role-gated transitions, verified-before-close, audit trail). A fuller reference architecture with real container, network, and vault enforcement is the next deliverable.
3. **Experimental design** — a structured evaluation of the protocol's governance properties against agentic-fleet workloads, with named comparison conditions and measurable outcomes. Planned, not yet drafted.

The work is offered for evaluation, criticism, and collaboration. Adversarial review is the most useful contribution. Known gaps named in the spec: skill supply chain, container-escape threat model, multi-OP planning-agent context, cross-orchestrator interop. See [`governance-protocol.md`](governance-protocol.md) § Open Questions and the threat-model table.

## Citation

> Manas, L. (2026). *Agent Command Structure (ACS): a theoretical framework for a substrate-agnostic governance protocol for AI agent fleets.* https://github.com/lukemanas/Agent_Command_Structure

## Author

Luke Manas — [linkedin.com/in/luke-manas](https://linkedin.com/in/luke-manas)

Feedback and collaboration welcome.
