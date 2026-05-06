# Governance Premises V2 — Formal Revision (R2)

**Source:** Governance and Implementation Vision V2 (2026-02-23)
**Revised:** 2026-02-28 (adversarial review incorporated)
**Standard:** Each premise is a single falsifiable claim. Derived premises name all dependencies. Axioms are starting points not derived from other premises in this document. Empirical premises are marked [EMPIRICAL].

---

**Load-bearing premises** ⭐: P3 (attention ≠ awareness), P15 (delegation flows downward), P22 (strategic/tactical division), P28 (incident is universal)

**Note on terminology:** the premises use "incident" (NIMS-faithful); the canonical specification ([../governance-protocol.md](../governance-protocol.md)) uses "project" for the same concept. Treat the two as synonyms unless the surrounding text says otherwise.

---

## Section 1: Cognitive Architecture (P1–P5)

*What makes human and agentic cognition different in kind, not just degree.*

**P1. [AXIOM]** Human cognition is serial, deep, and finite. Agentic cognition is parallel, tireless, scalable, and context-limited. These are structural differences, not differences of degree.

*Note: 'Authoritative' is a governance property, not a cognitive one; introduced at P12.*

**P2. [EMPIRICAL]** Human attention is genuinely serial: two deep decision processes cannot run in parallel, and cognitive switching between tasks degrades the quality of each. Each unit of attention spent on shallow review is a unit unavailable for deep judgment. This is an empirical constraint on human cognition, not an organizational shortcoming.

**P3. ⭐ [AXIOM]** Attention and awareness are distinct cognitive functions. *Awareness* — knowing what is happening — can be broad, can be delegated, and can be provided by agents through synthesis and reporting. *Attention* — focused, deep engagement with a specific decision — is serial, scarce, and cannot be substituted or parallelized.

**P4. [DERIVED from P2, P3]** Given P2 and P3, governance that requires human attention wherever awareness would suffice spreads attention thin until each sign-off is awareness without attention — the form of oversight preserved, the substance gone.

**P5. [AXIOM]** The organizational value of agent deployment is the combination of both cognitive architectures: massive parallel execution capacity guided by human judgment through shared objectives and accountability. Neither architecture alone achieves this.

---

## Section 2: Governance, Authority, and the Bridge (P6–P13)

*Governance defined; human authority established; the bridge function explained.*

**P6. [AXIOM]** Governance is the mechanism for aligning who has the right to decide with who has the power to execute. When they are aligned, authorized people drive what gets done. When they diverge, one of two failure modes follows: authorized people cannot act, or capable people act without authorization.

**P7. [AXIOM]** Humans command; agents execute. Agents may recommend, but the decision belongs to the human.

**P8. [AXIOM]** Every agent must have a named human principal. An agent without an accountable owner is not a governed actor.

**P9. [DERIVED from P1, P7, P8]** Given P1 (agents are parallel and tireless but context-limited), P7 (humans command), and P8 (named principal required), agents have execution power but no inherent authority — no objectives of their own, no organizational context, no understanding of their principal's trade-offs. The gap between execution capability and decision authority is larger with agents than with any human worker.

**P10. [DERIVED from P6, P9]** Given P6 and P9, governance exists to close the authority-execution gap — to ensure that the humans with the right to decide are the ones actually driving what agents do, and that every agent action traces back to an explicit human authorization.

**P11. [DERIVED from P9, P10]** Given P9 and P10, governance cannot be reduced to capability controls alone. Firewalls, permissions, and rate limits address the execution side; they do not address the authority side. An agent operating within its technical permissions may still be taking actions its human principal did not authorize, did not anticipate, or would reject if asked.

**P12. [DERIVED from P11]** Given P11, addressing the authority gap requires structural governance: mechanisms that explicitly represent, track, and enforce authorization chains from every agent action back to its human principal. Norms and training are insufficient for agents: agents are context-limited (P1) and cannot reliably internalize informal authority boundaries that depend on organizational context they do not possess.

**P13. [DERIVED from P5, P6, P7]** Given P5, P6, and P7, governance is the bridge between the two cognitive architectures: it routes strategic decisions — what to pursue, within what constraints, with what trade-offs — to humans, and routes tactical decisions — how to achieve the objective within established constraints — to agents. The cognitive architecture best equipped for strategic decisions is the one with authority and organizational context (humans); best equipped for tactical execution is the one with scale and tirelessness (agents). Governance that routes either way incorrectly either depletes human attention on tactical detail or loses the substance of human authority on strategic choices.

**P14. [DERIVED from P13]** Given P13, governance fails in two directions: agents operating without human judgment execute the wrong thing at scale; humans overwhelmed past the point of genuine engagement produce theater, not oversight.

---

## Section 3: The Delegation Chain (P15–P21)

*How authority flows downward and what properties delegation must have.*

**P15. ⭐ [DERIVED from P7, P8]** Given P7 and P8, delegation is a grant of authority flowing downward through the hierarchy — a bounded subset of the human principal's jurisdictional authority. Permissions flow downward, never upward.

**P16. [AXIOM]** Authority is non-amplifying: delegation cannot create authority that the delegating principal does not hold. An agent cannot be granted access to systems, data, or capabilities that its human principal does not have access to.

**P17. [DERIVED from P15, P16]** Given P15 and P16, an agent cannot act where its human has no authority and cannot be granted more than the human holds. Every agent action is bounded first by the human's jurisdictional authority and second by the agent's delegation within it.

**P18. [DERIVED from P10, P15]** Given P10 and P15, every agent action must trace back to an explicit human authorization — through the agent's delegation, through the OAP, through the principal's jurisdiction. A gap anywhere in this chain is a governance failure, not an implementation gap.

**P19. [AXIOM]** Agents have no rights-bearing relationship with their principals. Delegation is a grant, not a transfer — revocable immediately, for any reason, without process. The human retains authority at all times.

**P20. [DERIVED from P6]** Given P6, an action is irreversible when its effects cannot be completely undone — when the pre-action state cannot be restored with no residual consequence. Irreversible actions are the limiting case of governance: once executed, the authority alignment cannot be corrected after the fact.

**P21. [DERIVED from P14, P17, P20]** Given P14, P17, and P20, regardless of delegation scope, irreversible actions require explicit human authorization before execution. An agent granted broad delegation does not inherit authority to take irreversible actions without specific approval for each such action: broad delegation covers the tactical domain; irreversibility is a strategic threshold.

---

## Section 4: Planning and Execution (P22–P27)

*How strategic intent becomes governed agent work, with enforced review cycles.*

**P22. ⭐ [AXIOM]** Strategic decisions — what objective to pursue, what constraints apply, and what trade-offs are acceptable — belong to humans. Tactical decisions — which approach, sequence, and method to use in achieving an established objective within established constraints — belong to agents. This boundary is the central division of authority in the governance framework.

**P23. [DERIVED from P1, P13, P22]** Given P1 (agents are context-limited), P13 (tactical discretion belongs to agents within boundaries), and P22, the strategic/tactical boundary cannot be maintained by agent judgment alone — agents lack the organizational context to know when they are crossing it. The boundary must be enforced structurally.

**P24. [DERIVED from P22, P23]** Given P22 and P23, at scale, tactical consistency within the agent domain requires Standard Operating Procedures — implemented as Skills — that codify the boundary with enough precision to be enforceable without case-by-case judgment.

**P25. [DERIVED from P15, P22]** Given P15 and P22, an Operational Action Plan (OAP — the protocol's term for what NIMS calls the IAP) is the authorization document: the IC's formal approval of what agents will do and within what constraints, including pre-authorized exceptions decided in advance with full context before operational pressure applies. No operational agent deploys without an approved OAP.

**P26. [DERIVED from P4, P25]** Given P4 and P25, work executes in bounded operational periods. The bound is scope: each period is defined by a fixed set of objectives that cannot expand mid-period. The period ends when all objectives are verified-before-close or when the human terminates it. Scope-immutability — combined with the human's unilateral termination authority — is the hard guarantee of a review cycle: a period with finite, immutable scope cannot run indefinitely, and the human can always terminate. Time-based duration limits are an adopter calibration on top of the scope bound, not a protocol requirement.

**P27. [DERIVED from P19, P26]** Given P19 (delegation is revocable) and P26 (work proceeds in bounded periods), delegation is time-bound: agent authorization does not persist indefinitely. Reauthorization is required at intervals aligned to the period structure; open-ended delegation that survives period boundaries without explicit renewal is not governed.

---

## Section 5: Scalable Structure (P28–P33)

*How the framework scales from individual to enterprise without losing governance integrity.*

**P28. ⭐ [AXIOM]** All operational agent work happens within an incident. There is no category of operational work exempt from incident governance — no routine track, no lightweight exception, no standing authorization for agents to act outside incident structure. The incident is the universal unit of governance.

**P29. [DERIVED from P1, P28]** Given P1 (agents are tireless and context-limited) and P28, agents do not self-limit: a tireless agent cannot moderate its own action volume based on fatigue, and a context-limited agent cannot recognize when routine actions are compounding into governance problems. Universal incident scope is therefore necessary, not bureaucratic.

**P30. [DERIVED from P28, P29]** Given P28 and P29, governance that exempts routine work creates an escape hatch that agents will fill. The correct design variable is not presence or absence of governance but weight: governance is proportional to risk and reversibility, and present in all work.

**P31. [DERIVED from P2, P30]** Given P2 (human attention is serial) and P30 (governance is proportional), a supervisor's capacity for genuine oversight is the binding constraint on span of control. When that capacity is exceeded, the structural response is to add a supervisory layer — not to stretch the existing supervisor — because human cognitive capacity cannot be expanded by fiat, and nominal supervision without genuine oversight is not governance.

**P32. [DERIVED from P30, P31]** Given P30 and P31, unmanned functions roll up: the IC handles planning when no planning agent is needed; the IC directly oversees workers when no supervisor layer is needed. Structure activates when complexity demands it and deactivates when it does not. The hierarchy is proportionally activated, not uniformly installed.

**P33. [DERIVED from P28]** Given P28 (all work within incidents), the incident is the container: it bounds scope, tracks agent activity, maintains the audit record, and provides the context in which every other structural component operates. Delegation, periods, roles, and Skills are all incident-scoped.

---

## Section 6: Communication (P34–P38)

*The properties the communication layer must have to support governed agent coordination.*

**P34. [AXIOM]** Every message is persisted before delivery. The persistent record is the authoritative history of what was communicated — not delivery confirmation, not acknowledgment, not the recipient's local state.

**P35. [DERIVED from P1, P9]** Given P1 (agents are context-limited) and P9 (agents have no inherent authority), agents cannot reliably infer command authority from sender, direction, or channel — they lack the organizational context to interpret implicit authority signals. A message that carries command weight must therefore be identifiable by its declared type: a directive is a directive because it is typed as one.

**P36. [DERIVED from P34]** Given P34 (persistent record), agents communicate through persistent mailboxes, not synchronous request-response. The persistent record makes blocking unnecessary: an agent does not need the recipient to be present to send a message, and does not need to wait for acknowledgment to confirm delivery.

**P37. [DERIVED from P7, P15]** Given P7 (humans command) and P15 (delegation flows downward), who can communicate with whom is determined by the governance structure, not by network reachability. Routing is a governance constraint enforced at the messaging layer.

**P38. [DERIVED from P3, P34]** Given P3 (attention ≠ awareness) and P34 (persistent raw record), the communication layer produces a raw record; from it, the system derives role-appropriate information products: raw stream for audit and forensics, aggregated status for supervisors, synthesized views for ICs. Each role receives information proportional to its governance responsibility — awareness at scope, not everything.

---

## Section 7: Structural Components (P39–P43)

*The concrete components that implement the governance framework.*

**P39. [DERIVED from P22, P7]** Given P22 and P7, agent roles — planning, chief-of-staff, supervisor, worker, specialist — are typed governance positions that determine authority, constraints, and responsibilities within the incident. Roles are not descriptive labels; they are governance-enforced constraints on behavior.

**P40. [DERIVED from P15, P18]** Given P15 and P18, delegation is the formal, auditable document expressing what an agent is authorized to do within an incident. It is both a permission boundary and an audit artifact — the link between every agent action and the human jurisdictional authority behind it.

**P41. [DERIVED from P24]** Given P24, Skills are the executable implementation of Standard Operating Procedures. A Skill that has not been reviewed and approved through change control is not a governed artifact; deploying ungoverned Skills is deploying ungoverned tactical behavior.

**P42. [AXIOM]** A halt mechanism must exist that immediately stops affected agents when triggered. Stop authority — the authority to trigger a halt — is distinct from redirect authority — the authority to assign new objectives after the halt. These are separate governance functions requiring separate authorization. The protocol does not specify the implementation of the halt mechanism (runtime stop hooks, container kill signals, or substrate-level disconnection are all conformant); it specifies that the mechanism must exist and be triggerable by humans without bypass.

**P43. [DERIVED from P28, P30]** Given P28 and P30, the portfolio governance problem — uncoordinated, duplicative, or poorly sequenced actions across multiple incidents — requires a jurisdictional visibility mechanism: a means by which a jurisdiction holder sees across active workstreams and can prioritize, sequence, and deduplicate before work is done.

---

## Section 8: Memory Governance (P44–P49)

*Persistent memory as a governed capability and live attack surface.*

**P44. [AXIOM]** Persistent memory that extends an agent's autonomous capability across time is a live attack surface. Adversarially crafted inputs can write to memory, persist across operational periods, and execute against a trigger weeks later without further user interaction.

**P45. [DERIVED from P17, P44]** Given P17 (agents bounded by delegation) and P44, persistent memory is subject to the same governance principles as any other capability: it must be authorized, scoped to the agent's delegation, auditable, and revocable.

**P46. [DERIVED from P26, P45]** Given P26 (work proceeds in bounded periods) and P45, agent memory is scoped to the current period by default. Memory that persists beyond the period boundary bypasses the review checkpoint that periods are designed to enforce. Cross-period retention requires explicit IC authorization declared in the OAP; cross-incident retention requires IC authorization from both incidents.

**P47. [DERIVED from P18, P45]** Given P18 (authorization chain must be complete) and P45, memory writes, reads, and retention decisions must be logged to the audit trail with the same rigor as any other agent action: which agent wrote what, under which delegation, in which period.

**P48. [DERIVED from P7, P45]** Given P7 (humans command) and P45 (memory is governed), the full memory state of any agent must be queryable at any point by the IC, the agent's owner, and authorized security staff. Memory that cannot be inspected by the humans in command is not governed memory.

**P49. [DERIVED from P46, P47]** Given P46 and P47, at the start of each operational period, memory state must be reviewed before operational agents begin work. Supervisors validate their workers' memory; the IC reviews supervisor memory. The chain of command is accountable for memory validation downward.

---

## Section 9: Observability (P50–P54)

*What makes human oversight operationally real rather than nominal.*

**P50. [AXIOM]** Agents are opaque by default. A governance framework that specifies human oversight without specifying what the human can see is a policy document, not a governance framework.

**P51. [DERIVED from P7, P50]** Given P7 (humans command) and P50 (agents are opaque by default), humans cannot exercise command authority over what they cannot observe. Observability is therefore mandatory for all operational agents and cannot be disabled by agents, owners, or incident commanders. An agent in a governed incident that does not emit observable data is not a governed actor.

**P52. [DERIVED from P51]** Given P51, observable behavior must span the full scope of agent activity: lifecycle transitions, task execution, tool usage, memory operations, communications, and escalations. No category is exempt; a gap in observable scope is a gap in command authority.

**P53. [DERIVED from P3, P38, P52]** Given P3 (attention ≠ awareness), P38 (role-appropriate information products), and P52, the observability layer must present information proportional to governance responsibility: real-time for the common operating picture, audit-retained for accountability, quiet by default so that items requiring attention surface with prominence rather than being buried in volume.

**P54. [DERIVED from P4, P53]** Given P4 (conflating attention and awareness fails at scale) and P53, a display that treats all information with equal weight produces alarm fatigue and defeats the attention-preservation function the governance structure exists to serve. Information must be prioritized by the action it demands.

---

## Section 10: Information Governance (P55–P59)

*Classification, access control, and data lifecycle for machine-speed information production.*

**P55. [AXIOM]** All information produced within an incident must carry a classification reflecting its sensitivity, assigned at creation, governing access across roles and boundaries. Reclassification is a governed action requiring human authorization, not an automatic adjustment.

**P56. [DERIVED from P17, P55]** Given P17 (agents bounded by delegation) and P55, role-based access controls determine who — within their delegation and role — can access information at each classification level. A jurisdictional planning agent with read access to an incident's status does not automatically access its detailed tool call records, credential logs, or memory state; those require separate authorization.

**P57. [DERIVED from P18, P56]** Given P18 (authorization chain must be complete) and P56, access decisions must be logged to the audit trail. An access event without a record breaks the authorization chain.

**P58. [DERIVED from P55]** Given P55, a framework that generates unclassified, ungoverned data as a side effect of its operation has created an information governance gap. The framework's own audit trail and communication records are subject to the same data governance regime as any other governed information produced within the incident.

**P59. [DERIVED from P58]** Given P58, information must carry sufficient metadata for adopter data governance policies to apply: retention periods, data residency, regulatory holds, deletion obligations, and encryption requirements. The framework must not make these policies impossible to implement.

---

## Section 11: Scaling (P60–P63)

*How the framework scales without collapsing governance into theater.*

**P60. [DERIVED from P2, P31]** Given P2 (human attention is serial and finite) and P31 (span of control is bounded by genuine oversight capacity), scale problems are solved by adding humans and agents together, not agents alone. An architecture where a single human nominally governs hundreds of agents through deep agent hierarchies is not governance — it is nominal supervision without genuine oversight.

**P61. [DERIVED from P30, P60]** Given P30 (governance is proportional) and P60, the framework supports governance configurations from minimal (one human, one agent) to full structure (multi-team enterprise). At individual scale, governance is minimal because risk is minimal but structurally real. At team scale, formal periods and SITREPs activate. At enterprise scale, unified command, embedded security and architecture, continuous audit, and enterprise observability integration activate. The structural logic is the same at every scale; only the weight differs.

**P62. [AXIOM]** Jurisdictional governance is a tier above incident governance. A jurisdiction holder — a human with authority across a domain that spans multiple incidents — requires cross-incident visibility that cannot be incident-scoped by definition.

**P63. [DERIVED from P28, P62]** Given P28 (incident is universal) and P62 (jurisdictional tier exists above it), jurisdictional planning agents are the governed exception to incident-scoped delegation. Their delegation is organizational-level, scoped to their jurisdiction, granting read access to incident status and outputs within that domain. This does not contradict P28: these agents operate within the organizational-level governance tier; read access to incident outputs is not the same as operational authority within any individual incident.

---

## Section 12: Framework vs. Adopter Responsibility (P64–P66)

*The boundary between what the framework specifies and what adopters decide.*

**P64. [AXIOM]** The framework is a protocol, not a platform. It specifies governance properties that must hold and structural components that enforce them; it does not mandate implementation choices, tooling, or policy specifics.

**P65. [DERIVED from P64]** Given P64, the framework defines: incident as universal unit, role types and constraints, delegation properties, period lifecycle and maximum duration enforcement, communication persistence and message typing, stop hook mechanism, audit trail requirements, memory scope model, observability mandate and scope, information classification requirements, and Skill lifecycle. Adopters define: risk tier thresholds, span of control ratios, authorization workflows, period cadence, staffing, classification levels, access policies, retention periods, domain-specific Skills, and compliance reporting.

**P66. [DERIVED from P64, P65]** Given P64 and P65, the framework must not make adopter policy choices impossible to implement. A framework that mandates a specific platform, encodes industry-specific policy, or generates ungovernable data has overreached and will be replaced by governance theater.

---

## Section 13: NIMS Alignment and Structural Extensions (P67–P70)

*Why NIMS maps directly and where agentic governance extends beyond it.*

**P67. [AXIOM]** NIMS solves a structurally identical problem to agentic governance: how do independent actors with different authorities coordinate toward shared objectives under pressure, with clear accountability and without a single controlling authority? The structural parallel is direct, not metaphorical.

**P68. [DERIVED from P67]** Given P67, the framework adapts NIMS management characteristics directly: unity of command, chain of command, span of control, incident action planning, modular organization, comprehensive resource management, integrated communications, and accountability. These map without loss.

**P69. [DERIVED from P1, P9, P67, P68]** Given P1, P9, P67, and P68, three adaptations are required beyond standard NIMS for the agentic context: (1) *Asynchronous-by-default communication* — agents benefit from persistent mailboxes; ICS relies on synchronous radio. (2) *Structurally enforced read constraints* — planning agents are constrained to read-only by the messaging layer; ICS cannot mechanically enforce this with human actors. (3) *Typed message authority* — agents cannot interpret cultural and situational authority signals; authority must be encoded in the declared message type.

**P70. [DERIVED from P44, P50, P55, P67]** Given P44, P50, P55, and P67, three governance areas are required beyond anything NIMS addresses: (1) *Memory governance* — persistent agent memory is an attack surface with no NIMS equivalent. (2) *Observability as infrastructure* — agents are opaque by default; NIMS operates with self-reporting humans who can be directly observed. (3) *Information governance at machine speed* — agents generate classified, governed information at volumes requiring structural treatment; NIMS relies on pre-existing institutional controls.

---

*70 premises total (P1–P70). Axioms: P1, P3, P6, P7, P8, P19, P22, P28, P34, P42, P44, P50, P55, P62, P64, P67 (16 axioms). Empirical: P2. Load-bearing ⭐: P3, P15, P22, P28.*
