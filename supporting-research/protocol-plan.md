# Governance Protocol Plan

> Working plan from a planning session on March 28, 2026. Carried over and substrate-scrubbed for forward use as a protocol spec independent of the original reference implementation.

---

## Context

The work is being framed as an open-source governance protocol for safely deploying AI agents at scale — the same pattern as MCP (tool connectivity), one layer up (fleet governance).

Key insight: MCP is a protocol. Earlier work on this resembled a software stack. The argument only works as a lightweight protocol spec, not a heavy binary.

The breakthrough: a network identity / ACL layer (e.g., Tailscale/Headscale, Calico, Kubernetes NetworkPolicies) collapses most of the governance enforcement into infrastructure primitives — identity, ACLs, network segmentation, network-level audit. What remains at the application layer is thin: a schema, lifecycle states, and conventions. That's a protocol.

Simplification: no literal timer on operational periods. OAPs scope to estimates; periods end when objectives are complete or the human kills the period.

---

## The Protocol: What Gets Standardized

1. **OAP Schema (Operational Action Plan)** — A JSON document defining what agents are authorized to do in a single work period: objectives, assignments, access requirements, acceptance criteria, duration estimate. Human approves before execution. Scope can shrink mid-period but never expand.

2. **Lifecycle States** — A state machine for governance phases: base → initiation → planning → operational period → demobilization. Each transition has defined rules and a human gate.

3. **Chain of Command Semantics** — How roles relate: workers → supervisors → CoS → human. Who can direct whom, who reports to whom, escalation rules. No bypassing, no freelancing.

4. **Audit Event Format** — Structured log entries answering: who authorized what, when, what happened, what was the result. The compliance artifact regulators need.

5. **Capability-to-Policy Mapping Convention** — How an OAP's access requirements translate to network identity / ACL policy in the adopter's network layer. The bridge between the governance document and infrastructure enforcement. Reference implementations: Tailscale ACL tags, Kubernetes NetworkPolicies, AWS Service Control Policies.

---

## Phase 1: Define the Protocol Spec

Extract and formalize what exists in the governance design doc, plus write the missing pieces.

| Component | Status | Work Needed |
|-----------|--------|-------------|
| OAP schema | ~80% designed in governance MVP design | Extract into standalone JSON Schema file |
| Lifecycle states | 5 phases defined, transition rules in prose | Formalize as state machine spec |
| Chain of command | Defined in governance doc and ICS research | Express as protocol semantics, not prose |
| Audit event format | Defined in audit-event-schema.md (27 events) | Promote to canonical spec |
| Capability-to-policy mapping | Convention sketched, not formalized | Define the OAP-to-network-policy mapping convention with at least two reference targets |

---

## Phase 2: Reference-Implementation Demo

Demonstrate the full governance lifecycle on commodity infrastructure:

- OAP is a JSON file committed to the project repo
- Human approves by reviewing and merging (or running a command)
- Agents spawn into containers, receive network identity and ACLs matching the OAP
- Chain of command runs through whatever messaging substrate the adopter uses
- Work tracked on the adopter's issue tracker
- Review happens at the end — human inspects results, merges to main
- The entire flow uses commodity tools (Docker, a network identity layer, an issue tracker, a messaging substrate)

This is the demo: the governance protocol running on existing infrastructure, not on a bespoke stack.

---

## Phase 3: Build Thin Orchestration (Post-Spec)

Optional application-level tooling that automates what the demo does manually:

- `oap validate` — schema validation
- `period start/end` — lifecycle transitions that update ACLs and agent state
- `checkin` — agent proves orientation before getting credentials
- Role-gated issue transitions (if the issue tracker's native labels aren't sufficient)

These are implementation conveniences, not protocol requirements. Built after the protocol is validated.

---

## The Deliverable

A protocol spec document plus at least one reference implementation demonstrating the governance lifecycle on commodity infrastructure.

"Here's what the standard looks like. Here's it working. Here's where the reference implementation runs."

---

## What's Designed vs. What's Built

**Designed at depth (in the carryover docs):**
- Five lifecycle phases with transition rules
- Three enforcement layers (container, network, protocol)
- OAP schema with field definitions
- Chain of command hierarchy
- Checkin gate design
- Credential management architecture (vault interface)
- Risk tier classification (low / high)
- Audit event schema (27 events)

**Not yet built at protocol level:**
- Formalized protocol spec extracted from the design docs
- Capability-to-network-policy mapping convention
- Container orchestration reference implementation
- Vault integration reference implementation
- Demobilization phase design (audit events exist; phase doc does not)

---

## Key Decisions

1. **Protocol, not stack.** Lightweight governance protocol, not a software product.
2. **Network identity / ACL layer is the enforcement backbone.** Identity, ACLs, segmentation, and network-level audit collapse into infrastructure primitives. The protocol does not mandate which network identity layer; reference implementations target Tailscale, Kubernetes NetworkPolicies, and similar.
3. **No literal timer.** Periods end on objective completion or human decision, not a clock.
4. **Spec first, build after.** Define the protocol, demo with existing tools, build orchestration later.
5. **Open standard, neutral home.** The spec is open-source and intended for governance under a neutral standards body. A vendor's runtime can serve as a reference implementation; the spec itself is not vendor-owned.
6. **OAP and Issue schemas stay separate.** The OAP is protocol-level — the governance contract the human signs off on, the document that drives policy mapping. Issues (work units a CoS creates from OAP objectives) are implementation-level — how a team tracks execution. The protocol standardizes the OAP; issue tracking is an adopter choice (GitHub, Linear, Jira). Keeps the protocol thin.
7. **All three major agent runtimes already support containers.** Claude Code (Docker devcontainers), Codex (native cloud containers), and Gemini CLI (microVM sandboxes) all support containerized agent execution. The governance protocol's container model aligns with the direction all three vendors are already moving.
