# Agent Command Structure (ACS)

A substrate-agnostic governance protocol for coordinating fleets of AI agents under human authority. The protocol structures agentic execution into auditable lifecycle phases with explicit human checkpoints, scoped capabilities, and a recoverable failure model. It is derived from the Incident Command System (ICS / NIMS) — the federally mandated coordination framework used across emergency management, hospital incident response, and infrastructure operations for the past fifty years.

## Governing principle

**Agents can always think. They can only act inside the project sandbox.**

Thinking — analysis, summarization, planning, information gathering, agent-to-agent communication — is always allowed. Acting — writing files, creating artifacts, modifying external systems — requires a project sandbox with approved scope, credentials, and human oversight at the boundaries.

## Why this exists

Enterprises are deploying AI agent fleets faster than they can govern them. The frameworks being adopted are largely improvised, the audit artifacts regulators will demand do not yet exist in coherent form, and the operational discipline required to run agents reliably at scale has no shared standard. ICS / NIMS solves the structurally identical problem for human coordination — multiple actors with different authorities, working under time pressure, with clear accountability and recoverable failure modes — and has been refined for half a century in the highest-stakes operational environments in the United States. This protocol adapts those mechanisms to the agentic context.

The work was developed independently, grounded in production AI deployment experience in critical infrastructure. It is offered as a draft research artifact, not a product.

## What's in this repo

- **`governance-protocol.md`** — the canonical protocol specification. Five lifecycle phases (Base, Initiation, Planning, Operational Period, Demobilization), three cross-cutting horizontals (Capability Governance, Common Operating Picture, Data Governance), and the threat model the design addresses.
- **`reference/`** — a minimal Python reference implementation demonstrating the protocol's enforcement points end-to-end: schema validation as the gate, sandbox lifecycle, role-gated state transitions, verified-before-close, complete audit trail. Includes a runnable demo.
- **`supporting-research/`** — the fuller body of work behind the protocol:
  - `premises.md` — formal premises with explicit dependencies
  - `protocol-plan.md` — the five-component decomposition
  - `audit-event-schema.md` — the typed governance event format
  - `ics-research.md` — source ICS / NIMS material and its mapping to agent coordination
  - `compliance-mapping.md` — crosswalk against EU AI Act, NIST AI RMF, and ISO 42001
  - `protocol-rationale.md` — the case for an open governance standard
- **`Agent_CS.excalidraw`** — visual reference diagram of the lifecycle and enforcement layers.

## Reading order

Most readers should start with **`governance-protocol.md`** for the canonical spec, then look at **`reference/`** to see the enforcement points operating end-to-end. The supporting-research folder is for readers who want to evaluate the formal premises, the regulatory mapping, or the source ICS / NIMS material directly.

## Status

Design phase, in active iteration. The reference implementation demonstrates the enforcement points but is not production code. No commercial deployment exists. The protocol is presented for evaluation, criticism, and collaboration.

## Citation

If you find this work useful, cite as:

> Manas, L. (2026). *Agent Command Structure: a substrate-agnostic governance protocol for AI agent fleets.* https://github.com/lukemanas/Agent_Command_Structure

## License

CC BY 4.0 — free to use, share, and adapt with attribution.

## Author

Luke Manas — [linkedin.com/in/luke-manas](https://linkedin.com/in/luke-manas) — luke.manas@gmail.com

Feedback, criticism, and collaboration are welcome. The protocol benefits most from adversarial review.
