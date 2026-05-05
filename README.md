# Agent Command Structure (ACS)

A substrate-agnostic governance protocol for coordinating fleets of AI agents under human authority. Adapted from the Incident Command System (ICS / NIMS) — the federally mandated coordination framework that has run US emergency response, hospital incident management, and critical infrastructure operations for fifty years.

## Governing principle

**Agents can always think. They can only act inside the project sandbox.**

Thinking — analysis, planning, information gathering, agent-to-agent communication — is always allowed. Acting — writing files, creating artifacts, modifying external systems — requires a project sandbox with approved scope, scoped credentials, and human oversight at the boundaries.

## Why this exists

**The limiting factor on scaling agentic infrastructure is the capability of humans to meaningfully direct and control it.** Enterprises are deploying agent fleets faster than they can govern them. The audit artifacts that regulators are about to demand do not yet exist in coherent form. The operational discipline required to run agents reliably at scale has no shared standard.

ICS / NIMS solves the structurally identical problem for human coordination — multiple actors with different authorities, working under time pressure, with clear accountability and recoverable failure modes. It has been refined for half a century in the highest-stakes operational environments in the United States. Agent Command Structure (ACS) adapts those mechanisms to the agentic context.

## Where this sits

ACS is not an orchestration framework, not a runtime, not an agent SDK. It is the governance layer beneath them — one layer above MCP (which standardizes tool access), one layer beneath managed-agent platforms (which run individual agents). Anything from LangGraph workflows to Claude Managed Agents to a Codex sandbox can run *inside* an ACS-conformant operational period.

Five lifecycle phases — Base, Initiation, Planning, Operational Period, Demobilization — across three cross-cutting horizontals: Capability Governance, Common Operating Picture, and Data Governance. The protocol is described in terms of orchestrators, sandboxes, scoped network identity, credential vaults, and skills. No requirement depends on a specific product.

## Regulatory fit

The audit-event schema and authorization matrix were designed to generate the artifacts the EU AI Act requires of high-risk systems (enforcement: August 2, 2026). The crosswalk in `supporting-research/compliance-mapping.md` maps controls directly to:

- **EU AI Act** — Articles 12 (record-keeping), 14 (human oversight), 19 (log retention)
- **NIST AI RMF** and **NIST CSF 2.0**
- **ISO 42001** (AI management systems) and **ISO 27001**

A conformant implementation can answer the compliance questions regulators will ask with existing artifacts, not bespoke evidence collection.

## What's in this repo

- **`governance-protocol.md`** — the canonical specification. Threat model, lifecycle phases, authorization matrix, OAP/ARR schemas, identity & authentication boundary.
- **`reference/`** — minimal Python reference implementation. Demonstrates the enforcement points end-to-end: schema gates, sandbox lifecycle, role-gated transitions, verified-before-close, complete audit trail. Includes a runnable demo and optional integration with real Claude Code agents.
- **`supporting-research/`** — the body of work behind the protocol:
  - `premises.md` — formal premises (axiom / derived / empirical) with explicit dependencies
  - `protocol-plan.md` — the five-component decomposition
  - `audit-event-schema.md` — 27 typed governance events, EU AI Act mapped
  - `ics-research.md` — ICS / NIMS source material and its mapping to agent coordination
  - `compliance-mapping.md` — full crosswalk against EU AI Act, NIST, and ISO frameworks
  - `protocol-rationale.md` — the case for an open governance standard
- **`Agent_CS.excalidraw`** — visual reference of the lifecycle and enforcement layers.

## Reading order

- **30 seconds:** this README + the governing principle.
- **30 minutes:** `governance-protocol.md` for the full specification.
- **2 hours:** run the reference (`reference/examples/demo.sh`) to watch the enforcement points reject malformed input in real time.
- **Deeper:** `supporting-research/premises.md` for the formal argument; `compliance-mapping.md` if you care about the regulatory artifacts.

## Status

Design phase, in active iteration. The reference implementation demonstrates the enforcement points in a single-machine CLI; it is not production code and intentionally defers containers, network ACLs, vaults, and cryptographic identity to real-world implementations of the protocol. ACS is offered for evaluation, criticism, and collaboration — adversarial review is the most useful contribution.

Known gaps explicitly named in the spec: skill supply chain (signing/verification), container-escape threat model, multi-OP planning-agent context, cross-orchestrator interop. See `governance-protocol.md` § Open Questions and the threat-model table.

## Citation

> Manas, L. (2026). *Agent Command Structure (ACS): a substrate-agnostic governance protocol for AI agent fleets.* https://github.com/lukemanas/Agent_Command_Structure

## License

CC BY 4.0 — free to use, share, and adapt with attribution.

## Author

Luke Manas — [linkedin.com/in/luke-manas](https://linkedin.com/in/luke-manas) — luke.manas@gmail.com

Feedback, criticism, and collaboration welcome. ACS benefits most from adversarial review.
