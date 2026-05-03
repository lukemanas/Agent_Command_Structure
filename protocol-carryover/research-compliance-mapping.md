# Compliance Framework Mapping: Governance Protocol

> For each requirement, this document records: the specific control ID and text, what the protocol provides, coverage status, and at least one primary source.
>
> Coverage: ✅ Addressed · ⚠️ Partial · ❌ Gap · 🚫 Out of scope (physical or human layer)
>
> Relevance: 🔴 Directly applicable to the protocol layer · 🟡 Relevant with enterprise configuration · ⚪ Out of scope for a communication/governance protocol
>
> Last updated: February 23, 2026 (substrate-scrubbed April 2026 for the protocol carryover).
>
> **Note on substrate references in the "Tank Mechanism" column:** the original document was written against a specific reference implementation (Tank: Redis transport, attend daemon, fishtank streams, clog logs, `ft:sessions` registry). Where a cell still names those components, read them as "the protocol's reference-implementation equivalent." A substrate-neutral version of this table is on the carryover roadmap; this scrub generalizes the headline framing only.

---

## How to Read This Document

This is a **governance protocol**, not a compliance platform. It addresses controls at the **execution and communication layer** — session addressing, encrypted messaging, operational period mechanics, chain of command, audit trails. It does NOT address:
- Data governance for training data (ISO 42001 A.7.x — model development concern)
- Physical security (NERC CIP-006, CIP-014 — infrastructure concern)
- Personnel training and HR compliance (NERC CIP-004, HIPAA §164.308(a)(5) — human layer)
- Enterprise-level policy documents (ISO 42001 A.2.2 — management layer)

For each control, this document evaluates whether the protocol's current architecture addresses it, and where gaps exist in the protocol that would need to be filled.

---

## 1. EU AI Act

*Regulation (EU) 2024/1689. High-risk systems under Annex III (employment, credit, education, law enforcement AI) face Article 9–17 requirements. Enforcement deadline: August 2, 2026.*

Primary source: [EU AI Act full text](https://artificialintelligenceact.eu/)

| Article | Control Text | Protocol Mechanism | Coverage | Relevance |
|---------|-------------|----------------|----------|-----------|
| **Art. 9 — Risk Management** | "Providers shall establish, implement, document and maintain a risk management system…as a continuous iterative process run throughout the entire lifecycle." The system must identify and analyze risks, estimate their magnitude, and adopt targeted mitigation measures. ([Art. 9](https://artificialintelligenceact.eu/article/9/)) | Operational period checkpoints create bounded risk windows; risk-tiered model selection (critical/high/moderate/low cadences) scales review frequency to risk level; attend narration provides continuous monitoring | ✅ | 🔴 |
| **Art. 10 — Data Governance** | Training, validation, and testing data must be relevant, representative, and free of errors "to the best extent possible." Documented data governance practices required including design choices, collection methods, and bias examination. ([Art. 10](https://artificialintelligenceact.eu/article/10/)) | Session-scoped data access prevents cross-contamination; AES-256-GCM encrypted comms protect data in transit; fishtank message stream provides data access audit trail. NOTE: Tank does not govern training data — this requirement primarily applies to model providers. | ⚠️ Partial — applies at model layer | 🟡 |
| **Art. 11 — Technical Documentation** | Technical documentation must be drawn up before the system is placed into service and kept up to date. Must contain: general description, development process, components, monitoring/control procedures, validation results, and descriptions of any post-conformity changes. ([Art. 11](https://artificialintelligenceact.eu/article/11/), [Annex IV](https://artificialintelligenceact.eu/annex/4/)) | Transfer of Command briefings (ICS-201 equivalent) document current state, objectives, resources, and constraints at each session handoff; operational period IAP records; session metadata (project, role, model, scope) | ✅ | 🔴 |
| **Art. 12 — Record-Keeping** | High-risk AI systems must have automatic logging capabilities built in that record events relevant to identifying risk scenarios and supporting oversight. Logs must have timestamps. For remote biometric identification, additional fields required. ([Art. 12](https://artificialintelligenceact.eu/article/12/)) | attend narrations (timestamped, cross-machine) + clog task logs (per-task history) + fishtank message streams (append-only Redis) + human IC approvals in persistent DM trail. All records are append-only and include timestamps. | ✅ | 🔴 |
| **Art. 13 — Transparency** | Systems must be sufficiently transparent that deployers can interpret outputs and use them appropriately. Instructions for use must include: accuracy metrics, robustness levels, foreseeable risks, guidance on human oversight, and description of logging mechanisms. ([Art. 13](https://artificialintelligenceact.eu/article/13/)) | Session registry (`ft:sessions`) makes agent identity explicit; `source:prefix@user` addressing makes source type visible; attend narration is human-readable interpretation layer. No formal capability card format per agent type exists yet. | ⚠️ Partial — registry and addressing present; capability card format not standardized | 🔴 |
| **Art. 14 — Human Oversight** | Systems must be designed so natural persons can "decide, in any particular situation, not to use the system or to disregard, override or reverse" AI output. Humans must be able to interrupt via a "stop button or equivalent." Must address automation bias. ([Art. 14](https://artificialintelligenceact.eu/article/14/)) | Human IC at top of every command hierarchy; Safety Officer role has independent halt authority; stop hooks as interrupt mechanism; kill switch per session; no action proceeds past checkpoint without human approval | ✅ | 🔴 |
| **Art. 15 — Accuracy & Robustness** | Systems must achieve appropriate accuracy, robustness, and cybersecurity. Resilient to errors, faults, and inconsistencies in inputs. Resilient to adversarial inputs. Fallback plans documented. ([Art. 15](https://artificialintelligenceact.eu/article/15/)) | Rollback to last checkpoint commit; test suite required at every operational period boundary; structured failure reporting up chain of command. No adversarial input (prompt injection) testing framework built in. | ⚠️ Partial — rollback and testing strong; adversarial input testing absent | 🔴 |
| **Art. 17 — Quality Management System** | Providers must implement a documented QMS covering: regulatory strategy, design/QA procedures, data management, risk management, incident reporting, supplier management, and communication procedures. Named person responsible for QMS. ([Art. 17](https://artificialintelligenceact.eu/article/17/)) | Tank provides the operational governance layer (checkpoints, chain of command, audit trail) that a QMS would reference. Tank does NOT constitute a complete QMS — no formal AI policy document, no supplier management framework, no QMS review cadence generated | ⚠️ Partial — operational controls map well; formal QMS shell is enterprise responsibility | 🟡 |
| **Art. 19 — Log Retention** | Providers of high-risk AI systems must retain automatically generated logs for minimum **6 months** unless other law requires longer. Financial institutions must integrate logs into existing compliance documentation. ([Art. 19](https://artificialintelligenceact.eu/article/19/)) | Logs exist across attend/clog/fishtank/git. No enforced 6-month minimum retention policy; no archival tier separate from operational Redis streams. | ❌ Gap | 🔴 |
| **Annex III — System Inventory** | Operators must maintain an inventory of high-risk AI systems and classify them according to Annex III criteria before deployment. | No built-in AI system classification or pre-deployment registration mechanism | ❌ Gap | 🟡 |
| **Art. 9 — External Incident Reporting** | Incidents and near-misses must be reported to relevant competent national authorities. ([Art. 73](https://artificialintelligenceact.eu/article/73/)) | Internal incident trail (clog + attend) is comprehensive. No pipeline to external authorities (regulatory bodies, SIEM export). | ❌ Gap | 🟡 |

---

## 2. NIST AI Risk Management Framework 1.0

*Released January 26, 2023. Voluntary; required for US federal agencies. Four functions: Govern, Map, Measure, Manage.*

Primary sources: [NIST AI RMF 1.0 (PDF)](https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf), [NIST AIRC](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/)

### GOVERN

| Sub-ID | Control Text | Protocol Mechanism | Coverage | Relevance |
|--------|-------------|----------------|----------|-----------|
| **GV-1.1** | Legal and regulatory requirements involving AI are understood, managed, and documented | No built-in regulatory requirements registry or compliance mapping | ❌ Gap | 🟡 |
| **GV-1.4** | Organizational teams document policies, processes, and procedures for AI risk management throughout the AI lifecycle | Operational period lifecycle: plan → execute → checkpoint → review → next period; chain of command protocol | ✅ | 🔴 |
| **GV-1.6** | Mechanisms are in place to inventory AI systems | Session registry (`ft:sessions`) tracks active sessions; not a full pre-deployment AI system inventory | ⚠️ Partial | 🔴 |
| **GV-1.7** | Processes and procedures are in place for decommissioning and phasing out AI systems | session_end.sh deregisters from `ft:sessions`; Redis TTLs expire streams; no formal credential revocation confirmation | ⚠️ Partial | 🔴 |
| **GV-2.1** | Roles and responsibilities for risk management are established, communicated, and documented | ICS role hierarchy (IC → Supervisor → Worker); session registry with user owner; chain of command addressing | ✅ | 🔴 |
| **GV-2.2** | Personnel with AI risk management responsibilities have appropriate training and skills | Out of scope — human training compliance | 🚫 | ⚪ |
| **GV-3.2** | AI risk and impact metrics are documented for each specific AI system (human-AI role definitions) | Chain of command defines which decisions agents make autonomously vs. which require human approval; operational period checkpoints are the formal human approval boundary | ✅ | 🔴 |
| **GV-6.1** | Policies and procedures are in place for third-party entities including AI developers, vendors | No vendor risk management framework; LLM API provider risk not assessed | ❌ Gap | 🟡 |
| **GV-6.2** | Contingency processes for failures of third-party entities (e.g., model API unavailable) | Wait mode known-broken on Redis idle connection drops (tracked as GitHub issue #18); no model provider failover built in | ❌ Gap | 🔴 |

### MAP

| Sub-ID | Control Text | Protocol Mechanism | Coverage | Relevance |
|--------|-------------|----------------|----------|-----------|
| **Map-1.1** | Context is established for framing AI risks; intended purposes documented with a formal intended-use statement per AI system | Session metadata includes project, role, and scope; no standardized intended-use document format per agent type | ⚠️ Partial | 🔴 |
| **Map-2.2** | Knowledge about tasks, capabilities, and limitations is documented for each AI system | No formal capability/limitation card per agent type; what agent cannot do is undocumented | ❌ Gap | 🔴 |
| **Map-3.5** | Human oversight processes are defined; escalation path, alert recipient, and response time documented | Operational period checkpoints gate all decisions; chain of command escalation path defined by session addressing; human IC at top | ✅ | 🔴 |
| **Map-4.1** | Approaches for managing risks of AI systems in context are identified and categorized | Risk-tiered operational period cadences (critical/high/moderate/low); no legal risk documentation per deployment | ⚠️ Partial | 🟡 |
| **Map-5.1** | Likelihood and magnitude of impacts are characterized; impact register maintained | No formal impact register | ❌ Gap | 🟡 |

### MEASURE

| Sub-ID | Control Text | Protocol Mechanism | Coverage | Relevance |
|--------|-------------|----------------|----------|-----------|
| **Measure-2.4** | The functionality and behavior of the AI system and its components are monitored and evaluated in production | attend daemon monitors session activity; clog tracks task completion; no structured metrics dashboard or defined KPIs | ⚠️ Partial | 🔴 |
| **Measure-2.5** | AI system validity and reliability are demonstrated; regression tests with held-out benchmarks | Test suite required at every operational period checkpoint; no held-out benchmark set defined in protocol | ⚠️ Partial | 🔴 |
| **Measure-2.7** | AI system security and resilience evaluated; adversarial inputs (prompt injection) tested regularly | No adversarial input testing framework; prompt injection is a known gap for agent systems | ❌ Gap | 🔴 |
| **Measure-2.8** | Transparency and accountability risks examined; AI outputs must be interpretable by human reviewers | Chain of command ensures human-interpretable status reports at every checkpoint; attend narration is human-readable | ✅ | 🔴 |
| **Measure-3.1** | Approaches to identify existing and emergent risks are in place; anomaly detection on agent behavior | attend monitors sessions; no automated behavioral anomaly detection or statistical baseline | ⚠️ Partial | 🔴 |
| **Measure-3.3** | Feedback mechanisms for end users to report incorrect or harmful AI outputs exist | Human IC reviews at every checkpoint; no structured end-user feedback mechanism | ⚠️ Partial | 🟡 |
| **Measure-4.3** | Performance is tracked over time; alert on statistically significant degradation | No performance trend tracking or degradation alerting | ❌ Gap | 🟡 |

### MANAGE

| Sub-ID | Control Text | Protocol Mechanism | Coverage | Relevance |
|--------|-------------|----------------|----------|-----------|
| **Manage-1.2** | Risk treatments are prioritized and managed; higher-risk deployments receive more stringent controls | Risk-tiered operational period cadences (critical → every turn, low → every 12h); risk is explicit in period configuration | ✅ | 🔴 |
| **Manage-1.3** | Responses to identified risks are developed and documented before deployment | Rollback procedure documented in governance.md; kill switch per session; escalation to human IC | ✅ | 🔴 |
| **Manage-1.4** | Residual risks are documented and accepted by a named authority | No formal residual risk acceptance documentation | ❌ Gap | 🟡 |
| **Manage-2.4** | Automated circuit breakers exist to suspend AI systems when error rate exceeds threshold | No automated agent suspension on error threshold | ❌ Gap | 🔴 |
| **Manage-3.1** | Third-party AI resources are monitored; model API providers tracked for deprecations and security advisories | No model provider monitoring | ❌ Gap | 🟡 |
| **Manage-4.3** | Incidents communicated and tracked; central incident log with reportable AI incident definition | clog task history + attend narration trail; no central incident registry with defined reportable event criteria | ⚠️ Partial | 🔴 |

---

## 3. NIST CSF 2.0

*Released February 2024. Six functions: Govern, Identify, Protect, Detect, Respond, Recover. 106 subcategories.*

Primary sources: [NIST CSF 2.0 (PDF)](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf), [CSF Tools Reference](https://csf.tools/framework/csf-v2-0/)

### GOVERN

| Sub-ID | Control Text | Protocol Mechanism | Coverage | Relevance |
|--------|-------------|----------------|----------|-----------|
| **GV.OC-03** | Legal, regulatory, and contractual requirements regarding cybersecurity — including privacy and civil liberties — are understood and managed | No regulatory requirements register | ❌ Gap | 🟡 |
| **GV.RM-02** | Risk tolerance for the organization is established, communicated, and updated | Operational period risk tiers imply tolerance levels; not formally documented | ⚠️ Partial | 🟡 |
| **GV.RR-02** | Roles, responsibilities, and authorities related to cybersecurity risk management are established and communicated; every system has a named human owner | ICS role hierarchy; session registry; `@user` owner on every session | ✅ | 🔴 |
| **GV.SC-01** | A cybersecurity supply chain risk management program is established, authenticated, and approved | No supply chain risk program for AI model or framework vendors | ❌ Gap | 🟡 |
| **GV.SC-07** | Suppliers and third-party partner cybersecurity risks are continuously monitored | No vendor monitoring (model API changes, framework CVEs, incidents) | ❌ Gap | 🟡 |

### IDENTIFY

| Sub-ID | Control Text | Protocol Mechanism | Coverage | Relevance |
|--------|-------------|----------------|----------|-----------|
| **ID.AM-02** | Inventories of software, services, and systems are maintained; each agent registered with version, model, tools, owner | Active session registry (`ft:sessions`) exists; no version-pinned inventory or pre-deployment registration | ⚠️ Partial | 🔴 |
| **ID.AM-04** | External information systems and catalogs impacting the organization are catalogued | No external API inventory per agent type | ❌ Gap | 🟡 |
| **ID.AM-05** | Assets are prioritized based on classification, criticality, resources, and impact on mission | Risk tiers (critical/high/moderate/low) provide proportional controls; no formal data sensitivity classification | ⚠️ Partial | 🔴 |
| **ID.RA-01** | Vulnerabilities in assets are identified, validated, and recorded | No CVE or vulnerability tracking for agent framework dependencies | ❌ Gap | 🟡 |

### PROTECT

| Sub-ID | Control Text | Protocol Mechanism | Coverage | Relevance |
|--------|-------------|----------------|----------|-----------|
| **PR.AA-01** | Identities and credentials for authorized users, services, and hardware are managed, authenticated, and periodically reviewed | `source:prefix@user` session addressing; `ft:users` registry; no credential rotation schedule enforced | ⚠️ Partial | 🔴 |
| **PR.AA-05** | Access permissions, entitlements, and authorizations are defined in a policy, managed, enforced, and reviewed | Session-scoped DMs enforce least privilege; workers cannot access other sessions' channels by protocol design | ✅ | 🔴 |
| **PR.DS-01** | The confidentiality, integrity, and availability of data-at-rest are protected | AES-256-GCM on message content; git history encrypted at OS level (enterprise responsibility) | ✅ | 🔴 |
| **PR.DS-02** | The confidentiality, integrity, and availability of data-in-transit are protected | TLS on Redis transport + AES-256-GCM on content (defense in depth) | ✅ | 🔴 |
| **PR.PS-01** | Configuration management practices are established and applied | No formal configuration management for agent system prompts, model versions, tool permissions | ❌ Gap | 🔴 |
| **PR.PS-03** | Configuration change requests are reviewed, approved, and tracked | No change log for agent configuration changes | ❌ Gap | 🔴 |

### DETECT

| Sub-ID | Control Text | Protocol Mechanism | Coverage | Relevance |
|--------|-------------|----------------|----------|-----------|
| **DE.CM-03** | Personnel activity and technology usage are monitored to find potentially adverse events | clog task history; attend narration captures agent activity; no automated alerting thresholds | ⚠️ Partial | 🔴 |
| **DE.AE-01** | A baseline of network operations and expected data flows for users and systems is established and managed; anomalous activity is detected | No automated behavioral baselines or statistical deviation alerting | ❌ Gap | 🔴 |
| **DE.AE-02** | Potentially adverse events are analyzed to better characterize them | No automated anomaly classification pipeline | ❌ Gap | 🟡 |

### RESPOND / RECOVER

| Sub-ID | Control Text | Protocol Mechanism | Coverage | Relevance |
|--------|-------------|----------------|----------|-----------|
| **RS.MA-01** | The incident response plan is executed in coordination with relevant third parties as required | No notification pipeline to model providers or external authorities | ❌ Gap | 🟡 |
| **RS.AN-01** | Incidents are investigated to determine contributing factors and their impact | Full trail: git commits + attend narrations + clog + fishtank DM history; sufficient to reconstruct agent decision chain | ✅ | 🔴 |
| **RC.RM-02** | Recovery activities restore normal operations; rollback to previous stable configuration is documented | Standardized commits create known-good states; rollback procedure documented in governance.md | ✅ | 🔴 |

---

## 4. ISO/IEC 42001:2023 (AI Management System)

*Certifiable AI management system standard. Clauses 4–10 are normative requirements; Annex A provides 38 controls across 9 topic areas (A.2–A.10).*

Primary sources: [ISO 42001 Overview](https://www.iso.org/standard/42001), [ISMS.online Annex A](https://www.isms.online/iso-42001/annex-a-controls/), [Barr Advisory Clause Guide](https://www.barradvisory.com/resource/iso-42001-requirements-explained/)

### Core Clauses

| Clause | Control Text | Protocol Mechanism | Coverage | Relevance |
|--------|-------------|----------------|----------|-----------|
| **4.3** | Determine the scope of the AI management system; out-of-scope systems explicitly excluded with rationale | Session registry defines in-scope agents; no formal out-of-scope exclusion rationale | ⚠️ Partial | 🟡 |
| **5.2** | Top management must establish and maintain an AI policy; formal document signed by executive leadership | Human IC is structurally required; no organizational AI policy document is generated by the protocol | ❌ Gap | ⚪ |
| **6.1.2** | Conduct AI-specific risk assessments (bias, opacity, autonomy, model drift) — not generic IT risk | Risk-tiered operational periods; no AI-specific risk taxonomy or assessment methodology built in | ⚠️ Partial | 🟡 |
| **6.1.3** | Select controls from Annex A for each identified risk; document rationale for omitted controls | Tank addresses many Annex A controls operationally; no formal control selection audit trail | ⚠️ Partial | 🟡 |
| **8.1** | Controls must be operationally deployed, not just documented in a policy | Stop hooks, chain of command, checkpoints, encrypted messaging — all enforced at the protocol level, not aspirationally | ✅ | 🔴 |
| **8.4** | Maintain AI incident response procedures specific to AI (not just generic IT incident response) | clog + attend trail; rollback procedure; chain of command escalation — all AI-specific, not adapted from IT | ✅ | 🔴 |
| **9.1** | Monitor and measure AI system performance; KPIs defined; measured on schedule; results documented | attend collects activity data; clog tracks task completion; no structured KPI framework or measurement schedule | ⚠️ Partial | 🔴 |
| **9.2** | Conduct internal audits of the AIMS itself (the governance system, not just agent performance) | No AIMS-level audit mechanism | ❌ Gap | 🟡 |
| **10.1** | Nonconformities must be corrected with documented corrective actions (not just rollback) | Checkpoint failures trigger rollback; no formal corrective action tracking | ⚠️ Partial | 🟡 |

### Annex A Controls

| Control | Control Text | Protocol Mechanism | Coverage | Relevance |
|---------|-------------|----------------|----------|-----------|
| **A.2.2** | Establish a formal AI governance policy | Structural chain of command; no formal policy document artifact | ❌ Gap | ⚪ |
| **A.3.2** | Clear accountability for AI governance decisions; every AI system has a named responsible person | Session addressing includes `@user` owner; every session is traceable to a human | ✅ | 🔴 |
| **A.3.3** | Formal process for personnel to report AI governance concerns | No formal concern reporting mechanism | ❌ Gap | ⚪ |
| **A.4.2** | Maintain a complete inventory of all AI system dependencies | No dependency inventory (model versions, framework versions, tool dependencies) | ❌ Gap | 🟡 |
| **A.5.2** | Implement a structured methodology to evaluate AI externalities and impacts | Operational period blast radius bounding; no formal externality assessment methodology | ⚠️ Partial | 🟡 |
| **A.5.4** | Evaluate how AI decisions affect specific populations or groups (disparate impact) | No demographic impact assessment built in | ❌ Gap | ⚪ |
| **A.6.2.5** | Implement controlled procedures for deploying AI systems into production | Human IC approval gates at operational period boundaries; stop hooks enforce change control | ✅ | 🔴 |
| **A.6.2.6** | Implement ongoing surveillance and performance tracking in production | attend daemon + clog; no structured performance tracking dashboard | ⚠️ Partial | 🔴 |
| **A.6.2.7** | Maintain comprehensive technical records supporting auditability | Transfer of Command briefings; git history; attend logs; operational period IAPs | ✅ | 🔴 |
| **A.6.2.8** | Record event logs documenting AI system activities and decisions | attend narrations + clog task logs + fishtank streams (all timestamped, append-only) | ✅ | 🔴 |
| **A.7.2–A.7.6** | Document and manage datasets; data lineage; bias testing; processing procedures | Tank is a governance protocol; dataset governance applies to model training, not agent communication | 🚫 Out of scope | ⚪ |
| **A.8.2** | Provide materials explaining system functionality and limitations to end users | Session metadata partially addresses; no formal capability card standard | ⚠️ Partial | 🔴 |
| **A.8.4** | Establish procedures for notifying stakeholders of AI failures | Chain of command escalation routes failures to IC; no external stakeholder notification mechanism | ⚠️ Partial | 🟡 |
| **A.9.2** | Implement safeguards and guidelines preventing misuse in operational contexts | Scoped session DMs; encrypted comms; session addressing prevents spoofing | ✅ | 🔴 |
| **A.10.3** | Require supplier practices to align with organizational AI governance standards | No supplier governance program for model providers or framework vendors | ❌ Gap | 🟡 |

---

## 5. ISO/IEC 27001:2022 (Information Security Management)

*93 controls across four categories. Organizational (A.5) and technological (A.8) controls most relevant to Tank.*

Primary sources: [ISO 27001 Annex A Overview — DataGuard](https://www.dataguard.com/iso-27001/annex-a/), [A.5.15 Access Control — ISMS.online](https://www.isms.online/iso-27001/annex-a-2022/5-15-access-control-2022/), [A.5.16 Identity Management — ISMS.online](https://www.isms.online/iso-27001/annex-a-2022/5-16-identity-management-2022/)

| Control | Title | Control Text (summarized) | Protocol Mechanism | Coverage | Relevance |
|---------|-------|--------------------------|----------------|----------|-----------|
| **A.5.9** | Asset Inventory | Up-to-date inventory of all information assets, including non-human identities | Session registry tracks active agents; no pre-deployment or version-pinned inventory | ⚠️ Partial | 🔴 |
| **A.5.12** | Data Classification | Information classified by sensitivity level; handling rules applied | No data classification built in; agents do not tag outputs with input sensitivity | ❌ Gap | 🟡 |
| **A.5.15** | Access Control | Access rights based on need-to-know and need-to-use | Session-scoped DMs; workers see only their scope; project channels isolated; AES-256-GCM enforces no-key-no-data | ✅ | 🔴 |
| **A.5.16** | Identity Management | Full lifecycle management of all digital identities including non-human agents | `source:prefix@user` session identity; `ft:users` registry; session lifecycle hooks (start/end) | ✅ | 🔴 |
| **A.5.17** | Authentication Credentials | Rules for allocation and management of authentication credentials; rotation | TLS + AES-256-GCM; no credential rotation enforcement for session tokens | ⚠️ Partial | 🔴 |
| **A.5.18** | Access Rights Review | Access rights periodically reviewed and modified/revoked when no longer needed | No periodic access rights review for agent sessions | ❌ Gap | 🟡 |
| **A.5.19** | Supplier Information Security | Information security requirements defined for supplier relationships | No supplier security requirements for LLM providers or framework vendors | ❌ Gap | 🟡 |
| **A.5.24** | Incident Management Planning | Roles, responsibilities, and procedures for information security incident management | clog incident trail; rollback procedure; chain of command escalation; human IC has halt authority | ✅ | 🔴 |
| **A.5.28** | Collection of Evidence | Evidence for incidents maintained and preserved | Full trail (git + attend + clog + fishtank) preserved; no explicit forensic preservation policy (evidence isolated from operational modification) | ⚠️ Partial | 🔴 |
| **A.5.33** | Protection of Records | Records protected from loss, unauthorized access, and falsification | Redis streams are append-only; git history is immutable with standard commit discipline; no separate tamper-evident archival tier | ⚠️ Partial | 🔴 |
| **A.8.3** | Information Access Restriction | Restrict access to information and systems per access control policy | AES-256-GCM; no key, no data regardless of Redis access; scoped addressing enforced by protocol | ✅ | 🔴 |
| **A.8.9** | Configuration Management | Configurations documented, implemented, monitored, and audited | No formal configuration management for agent system prompts, model versions, tool configs | ❌ Gap | 🔴 |
| **A.8.12** | Data Leakage Prevention | Detect and prevent unauthorized disclosure of information | No DLP monitoring of agent outputs for inadvertent sensitive data disclosure | ❌ Gap | 🟡 |
| **A.8.15** | Logging | Activities, exceptions, faults, and security events logged in centralized, protected log store | attend narrations; clog task logs; fishtank streams — all timestamped, centralized | ✅ | 🔴 |
| **A.8.16** | Monitoring | Networks, systems, and applications monitored for anomalous behavior | attend cross-machine monitoring; session heartbeats; no behavioral anomaly detection | ⚠️ Partial | 🔴 |
| **A.8.24** | Use of Cryptography | Cryptography policy implemented; appropriate algorithms and key management | AES-256-GCM (content) + TLS (transport); key management via `~/.fishtank/config.yaml` | ✅ | 🔴 |
| **A.8.32** | Change Management | Material changes to information systems require formal approval and testing | No formal change approval workflow for agent configuration changes (prompt, model, tool permissions) | ❌ Gap | 🔴 |

---

## 6. NERC CIP (Critical Infrastructure Protection)

*Mandatory for North American Bulk Electric System (BES) operators. AI agents interacting with BES Cyber Systems inherit the impact classification of the systems they can access. Penalties up to $1M/day per violation.*

Primary sources: [NERC CIP Standards Index](https://www.nerc.com/standards/reliability-standards/cip), [CIP-007-6 (PDF)](https://www.nerc.com/pa/Stand/Reliability%20Standards/CIP-007-6.pdf), [NERC CIP Overview — RSI Security](https://blog.rsisecurity.com/nerc-cip-standards-summary-all-mandatory-requirements-explained/), [NERC CIP and AI — Frenos](https://frenos.io/blog/nerc-cip-ai)

| Standard | Requirement | Protocol Mechanism | Coverage | Relevance |
|----------|-------------|----------------|----------|-----------|
| **CIP-002 R1/R2** | Identify and classify each BES Cyber System as high/medium/low impact using Attachment 1 criteria. Review every 15 months with CIP Senior Manager approval. | Risk tiers (critical/high/moderate/low) are conceptually equivalent; no formal BES taxonomy mapping or 15-month review cycle | ⚠️ Partial | 🟡 |
| **CIP-003 R1/R2** | Documented cybersecurity policies covering all required areas; CIP Senior Manager with delegated authority | Human IC accountability; chain of command; policy enforcement via stop hooks | ✅ | 🔴 |
| **CIP-004 R1/R3** | Annual security awareness and CIP training program for all personnel with BES Cyber System access | Out of scope — human training compliance | 🚫 | ⚪ |
| **CIP-004 R4** | Quarterly review of access authorization list for BES Cyber Systems | No periodic access review mechanism | ❌ Gap | 🟡 |
| **CIP-005 R1** | Define ESP around all BES Cyber Systems; deny-by-default rules at all EAPs | TLS on Redis; AES-256-GCM; no formal ESP boundary definition with deny-by-default routing | ⚠️ Partial | 🔴 |
| **CIP-005 R2** | MFA required for all Interactive Remote Access; Intermediate System between external networks and BES | No MFA for agent-to-Redis authentication beyond TLS + shared key | ❌ Gap | 🔴 |
| **CIP-007 R1** | Only required ports enabled; all others disabled where technically feasible | Out of scope at protocol level — infrastructure configuration responsibility | 🚫 | ⚪ |
| **CIP-007 R2** | Security patches assessed within 35 days of vendor release; applied or documented compensating controls | No patch management for agent framework dependencies | ❌ Gap | 🟡 |
| **CIP-007 R4** | Security event logs retained minimum 90 calendar days; reviewed at intervals ≤15 days | attend + clog logs exist; no 90-day retention enforcement or 15-day review cadence | ⚠️ Partial | 🔴 |
| **CIP-008** | Cyber security incident classification, reporting, response, and notification to NERC | Internal incident trail (clog + attend) comprehensive; no NERC reporting pipeline | ❌ Gap | 🟡 |
| **CIP-010 R1/R2** | Baseline configuration maintained per BES Cyber System; automated monitoring for unauthorized changes | Standardized git commits per period create known-good baseline; no automated config drift detection | ⚠️ Partial | 🔴 |
| **CIP-011** | Classify BCSI; implement access controls; secure disposal procedures on decommission | Session-scoped access and encryption address access control; no BCSI classification or secure disposal procedure | ⚠️ Partial | 🟡 |
| **CIP-013** | Supply chain cyber security risk management plan: vendor vulnerability notification, software integrity verification, vendor remote access controls | No supply chain risk management for LLM providers or framework vendors | ❌ Gap | 🟡 |
| **CIP-006/014** | Physical security of BES Cyber Assets and transmission stations | Out of scope — physical layer | 🚫 | ⚪ |

---

## 7. SOC 2 Type II

*AICPA Trust Services Criteria. Type II examines operating effectiveness over a defined audit period (typically 6–12 months). Security (CC) is mandatory; Availability, Processing Integrity, Confidentiality, and Privacy are optional.*

Primary sources: [SOC 2 Common Criteria — Secureframe](https://secureframe.com/hub/soc-2/common-criteria), [SOC 2 CC6/CC7 Sub-criteria — Scrut](https://www.scrut.io/hub/soc-2/soc-2-common-criteria), [SOC 2 and AI Systems — Schellman](https://www.schellman.com/blog/soc-examinations/how-to-incorporate-ai-into-your-soc-2-examination)

| Criterion | Control Text | Protocol Mechanism | Coverage | Relevance |
|-----------|-------------|----------------|----------|-----------|
| **CC1.1** | Organization demonstrates commitment to integrity and ethical values; board and management set governance tone | Human IC is structural; no formal governance tone documentation generated by protocol | ⚠️ Partial | ⚪ |
| **CC1.4** | Management establishes authority and responsibility for pursuing objectives including AI governance | ICS chain of command; named human IC with defined authority over all agents | ✅ | 🔴 |
| **CC3.1** | Objectives specified with sufficient clarity to enable identification of risks | Operational period objectives are formal; session scope documented per period | ✅ | 🔴 |
| **CC3.2** | Risks to achievement of objectives are identified and analyzed | Risk-tiered checkpoints; no formal risk register per deployment | ⚠️ Partial | 🟡 |
| **CC3.4** | Changes that could significantly impact the system of internal controls are identified and assessed | Human IC gates operational period transitions; no automated change impact assessment | ⚠️ Partial | 🟡 |
| **CC6.1** | Logical and physical access controls restrict access to protected information | Session-scoped DMs; AES-256-GCM; role-based addressing; scoped access enforced by protocol | ✅ | 🔴 |
| **CC6.2** | Agent service accounts subject to same lifecycle management as human accounts (provision, review, deprovision) | Session registration/deregistration hooks; no periodic account review cadence | ⚠️ Partial | 🔴 |
| **CC6.3** | Access based on least privilege and separation of duties | Workers isolated to session DMs; project channels scoped by role; no cross-worker visibility | ✅ | 🔴 |
| **CC6.8** | Controls prevent or detect introduction of unauthorized software; agent code integrity validated at deployment | No integrity verification of agent code or model weights at deployment | ❌ Gap | 🟡 |
| **CC7.1** | Monitoring to detect changes that could introduce vulnerabilities | attend monitors session activity; no automated vulnerability-introducing change detection | ⚠️ Partial | 🔴 |
| **CC7.2** | Behavioral baselines established; statistical deviations generate alerts | No behavioral baselines or statistical alerting | ❌ Gap | 🔴 |
| **CC7.3** | Security events assessed; AI behavioral anomalies classified as events | No automated event classification pipeline | ❌ Gap | 🟡 |
| **CC7.4** | Robust incident response including agent suspension and evidence preservation | Kill switch per session; full audit trail for evidence; chain of command escalation | ✅ | 🔴 |
| **CC7.5** | Recovery from security incidents; restore from known-good state; post-incident review | Git rollback to last checkpoint; human IC post-period review | ✅ | 🔴 |
| **CC8.1** | All material system changes (agent prompts, model versions, tool permissions) tested and approved before deployment | Human IC approval gates at operational period boundaries; test suite required at every checkpoint | ✅ | 🔴 |
| **CC9.1** | Risk mitigation for internal business disruption | Rollback to last checkpoint; graceful session handoff | ✅ | 🔴 |
| **CC9.2** | Third-party vendor risks assessed and in vendor management program | No vendor management program for model API providers | ❌ Gap | 🟡 |
| **A1.1** | System available per SLA commitments | attend cross-machine mesh; session handoff failover; no formal SLA tooling or availability measurement | ⚠️ Partial | 🟡 |
| **PI1.1** | Processing is complete, accurate, and timely | Test suite at checkpoints; human review gates; attend narration verifies task completion | ✅ | 🔴 |

---

## 8. HIPAA Security Rule

*45 CFR Part 164, Subpart C. Applies to covered entities and business associates that create, receive, maintain, or transmit ePHI. AI agents processing ePHI are subject to both administrative (§164.308) and technical (§164.312) safeguards.*

Primary sources: [HIPAA Technical Safeguards §164.312 — AccountableHQ](https://www.accountablehq.com/post/hipaa-security-rule-technical-safeguards-the-complete-requirements-list-45-cfr-164-312), [HIPAA Administrative Safeguards §164.308 — AccountableHQ](https://www.accountablehq.com/post/45-cfr-164-308-explained-the-full-hipaa-administrative-safeguards-list), [HHS HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html)

### Administrative Safeguards — §164.308

| Standard | Code | Req. | Control Text | Protocol Mechanism | Coverage | Relevance |
|----------|------|------|-------------|----------------|----------|-----------|
| Risk Analysis | §164.308(a)(1)(ii)(A) | Required | Accurate and thorough assessment of potential risks to ePHI confidentiality, integrity, and availability | Operational period risk assessment; no formal ePHI risk analysis document generated | ⚠️ Partial | 🟡 |
| Risk Management | §164.308(a)(1)(ii)(B) | Required | Implement security measures sufficient to reduce identified ePHI risks to reasonable levels | Risk-tiered checkpoints; rollback procedure; scoped access and encryption | ✅ | 🔴 |
| Activity Review | §164.308(a)(1)(ii)(D) | Required | Regularly review records of information system activity; audit log review cadence | attend + clog reviewed at IC checkpoints; no enforced review cadence | ⚠️ Partial | 🔴 |
| Security Responsibility | §164.308(a)(2) | Required | Designate one individual responsible for security policies and procedures | Human IC is always human; named owner for every session | ✅ | 🔴 |
| Access Authorization | §164.308(a)(4)(ii)(B) | Addressable | Procedures for granting access to ePHI; formal authorization document per agent | Session-scoped access; no formal ePHI access authorization document per agent type | ⚠️ Partial | 🔴 |
| Termination Procedures | §164.308(a)(3)(ii)(C) | Addressable | Immediately terminate ePHI access when employment/engagement ends | session_end.sh deregisters; no formal ePHI access revocation confirmation | ⚠️ Partial | 🔴 |
| Incident Response | §164.308(a)(6)(ii) | Required | Identify, respond to, and document security incidents involving ePHI; report to OCR | clog + attend trail; rollback; escalation to IC; no OCR reporting pipeline | ⚠️ Partial | 🟡 |
| ePHI Data Backup | §164.308(a)(7)(ii)(A) | Required | Create and maintain retrievable exact copies of ePHI | Tank does not manage ePHI backup; this is enterprise responsibility; protocol should not be single point of ePHI access | ❌ Gap | ⚪ |
| Disaster Recovery | §164.308(a)(7)(ii)(B) | Required | Procedures for restoring ePHI data lost in emergencies | Rollback covers agent state; ePHI recovery plan is enterprise responsibility | ⚠️ Partial | ⚪ |
| Workforce Training | §164.308(a)(5) | Addressable | Security awareness and training for all workforce members | Out of scope — human compliance layer | 🚫 | ⚪ |

### Technical Safeguards — §164.312

| Standard | Code | Req. | Control Text | Protocol Mechanism | Coverage | Relevance |
|----------|------|------|-------------|----------------|----------|-----------|
| Access Control | §164.312(a)(1) | Required | Implement technical policies allowing only authorized persons and software programs to access ePHI | Session-scoped DMs; session_end.sh logoff; human IC override | ✅ | 🔴 |
| Unique User ID | §164.312(a)(2)(i) | Required | Assign unique identifier to every user AND software program | `source:prefix@user` addressing; `ft:users` registry; each session has unique prefix | ✅ | 🔴 |
| Automatic Logoff | §164.312(a)(2)(iii) | Addressable | Terminate electronic sessions after defined period of inactivity | Session TTL via Redis; no configurable inactivity timeout per session | ⚠️ Partial | 🔴 |
| Encryption/Decryption | §164.312(a)(2)(iv) | Addressable | Mechanism to encrypt and decrypt ePHI | AES-256-GCM on all message content | ✅ | 🔴 |
| Audit Controls | §164.312(b) | Required | Hardware, software, and procedural mechanisms to record and examine activity in ePHI-containing systems | attend narrations; clog; fishtank streams — all timestamped | ✅ | 🔴 |
| Integrity | §164.312(c)(1) | Required | Protect ePHI from improper alteration or destruction | Redis append-only streams; git history immutable | ✅ | 🔴 |
| Person/Entity Authentication | §164.312(d) | Required | Verify that persons or entities seeking access to ePHI are who they claim to be | Session registration; user registry; TLS mutual auth to Redis | ✅ | 🔴 |
| Transmission Security | §164.312(e)(1) | Required | Guard ePHI in transit from unauthorized access | TLS transport + AES-256-GCM content encryption (defense in depth) | ✅ | 🔴 |
| Integrity Controls in Transit | §164.312(e)(2)(i) | Addressable | Security measures to ensure transmitted ePHI is not improperly modified | AES-256-GCM is Authenticated Encryption with Associated Data (AEAD); integrity is built in | ✅ | 🔴 |

---

## Cross-Framework Summary

| Concern | EU AI Act | NIST AI RMF | NIST CSF 2.0 | ISO 42001 | ISO 27001 | NERC CIP | SOC 2 | HIPAA | **Tank** |
|---------|-----------|-------------|--------------|-----------|-----------|---------|-------|-------|----------|
| **Human Oversight** | Art. 14 | GV-3.2 | GV.RR-02 | A.3.2 | A.5.16 | CIP-004 | CC1.4 | §164.308(a)(2) | ✅ Strong |
| **Audit Trails / Logging** | Art. 12, 19 | Measure-2.4 | DE.CM-03 | A.6.2.8 | A.8.15 | CIP-007 R4 | CC7.1 | §164.312(b) | ✅ Strong |
| **Access Control / Least Privilege** | Art. 14, 15 | Map-3.5 | PR.AA-05 | A.9.2 | A.5.15, A.8.3 | CIP-005 | CC6.1–6.3 | §164.312(a) | ✅ Strong |
| **Encryption** | Art. 15 | — | PR.DS-01/02 | — | A.8.24 | CIP-005 | CC6.1 | §164.312(e) | ✅ Strong |
| **Identity Management** | — | GV-2.1 | GV.RR-02 | A.3.2 | A.5.16 | CIP-005 | CC6.2 | §164.312(a)(2)(i) | ✅ Strong |
| **Incident Response (internal)** | Art. 17 | Manage-4.3 | RS.AN-01 | A.8.4 | A.5.24 | CIP-008 | CC7.4 | §164.308(a)(6) | ✅ Strong |
| **Rollback / Recovery** | Art. 9 | Manage-1.3 | RC.RM-02 | A.6.2.5 | — | CIP-010 | CC7.5 | §164.308(a)(7) | ✅ Strong |
| **Risk-Based Review Frequency** | Art. 9 | Manage-1.2 | GV.RM-02 | Cl.6.1.2 | — | CIP-002 | CC3.1 | — | ✅ Strong |
| **Incident Reporting (external)** | Art. 9/73 | Manage-4.3 | RS.MA-01 | A.8.4 | A.5.24 | CIP-008 | — | §164.308(a)(6) | ❌ Gap |
| **Metrics Dashboard / Alerting** | — | Measure-2.4/4.3 | DE.AE-01 | Cl.9.1 | A.8.16 | CIP-007 R4 | CC7.2 | — | ❌ Gap |
| **Anomaly Detection (automated)** | Art. 15 | Measure-3.1 | DE.AE-01 | A.6.2.6 | A.8.16 | CIP-007 R4 | CC7.2 | — | ❌ Gap |
| **Log Retention Enforcement** | Art. 19 | — | — | — | A.5.33 | CIP-007 R4 | — | §164.308(a)(1)(ii)(D) | ❌ Gap |
| **Configuration Change Control** | Art. 17 | — | PR.PS-01/03 | A.6.2.5 | A.8.32 | CIP-010 | CC8.1 | — | ❌ Gap (agent configs) |
| **Supply Chain / Vendor Risk** | Art. 17 | GV-6.1/6.2 | GV.SC-01/07 | A.10.3 | A.5.19 | CIP-013 | CC9.2 | — | ❌ Gap |
| **AI System Inventory / Classification** | Annex III | GV-1.6 | ID.AM-02 | Cl.4.3 | A.5.9 | CIP-002 | — | — | ❌ Gap |
| **Data Classification** | — | — | ID.AM-05 | A.7.2 | A.5.12 | CIP-011 | CC6.3 | §164.312(a)(2)(iv) | ❌ Gap |
| **Adversarial Input Testing** | Art. 15 | Measure-2.7 | ID.RA-01 | — | — | — | — | — | ❌ Gap |
| **Personnel Training** | — | GV-2.2 | — | A.2.2 | — | CIP-004 | — | §164.308(a)(5) | 🚫 OOS |
| **Physical Security** | — | — | — | — | — | CIP-006/014 | — | — | 🚫 OOS |

---

## Consolidated Gap Priority List

| Priority | Gap | Affected Frameworks | Notes |
|----------|-----|---------------------|-------|
| **P1** | External reporting pipeline (SIEM, regulators, model providers) | EU AI Act Art. 73, NERC CIP-008, ISO 27001 A.5.24, NIST CSF RS.MA-01, HIPAA §164.308(a)(6) | Internal incident trail is comprehensive; need exportable report format, webhook to SIEM, and notification pipeline to regulators |
| **P1** | Metrics dashboard and automated alerting | NIST AI RMF Measure-2.4/4.3, ISO 42001 Cl.9.1, SOC 2 CC7.2, NIST CSF DE.AE-01 | All underlying data exists in attend/clog/fishtank; need aggregation layer, KPI framework, and threshold-based alerting |
| **P1** | Automated anomaly detection / behavioral baselines | NIST AI RMF Measure-3.1, NIST CSF DE.AE-01, SOC 2 CC7.2, ISO 27001 A.8.16, NERC CIP-007 R4 | attend monitors but no statistical baseline; human IC must notice anomalies manually; this is the biggest operational gap |
| **P2** | Log retention policy enforcement (minimum 6 months) | EU AI Act Art. 19, NERC CIP-007 R4 (90 days), ISO 27001 A.5.33 | Logs exist; no configurable retention enforcer; Redis streams can be capped; no archival tier |
| **P2** | Agent configuration change control (prompts, model versions, tool permissions) | ISO 27001 A.8.9/A.8.32, NIST CSF PR.PS-01/03, NERC CIP-010 | Changes to agent configurations have no formal approval workflow; this is also an adversarial attack vector (unauthorized prompt modification = unauthorized config change) |
| **P2** | Automated circuit breakers (suspend agent on error threshold) | NIST AI RMF Manage-2.4 | No mechanism to automatically suspend an agent when its error rate exceeds a threshold; requires human observation |
| **P2** | AI system inventory and pre-deployment classification | EU AI Act Annex III, NIST AI RMF GV-1.6, NIST CSF ID.AM-02 | Session registry tracks active sessions; no registry of agent types by risk level before deployment |
| **P3** | Supply chain / vendor risk program for LLM providers | NIST AI RMF GV-6.1/6.2, NIST CSF GV.SC-01/07, ISO 42001 A.10.3, ISO 27001 A.5.19, NERC CIP-013, SOC 2 CC9.2 | Significant gap for NERC CIP and regulated enterprise deployments; model API provider risk not assessed |
| **P3** | Adversarial input testing framework (prompt injection) | EU AI Act Art. 15, NIST AI RMF Measure-2.7, NIST CSF ID.RA-01 | Known attack vector for agent systems; no testing framework built in |
| **P3** | Data classification and labeling on agent outputs | ISO 27001 A.5.12, NIST CSF ID.AM-05, NERC CIP-011, SOC 2 CC6.3 | Agents process data of varying sensitivity; no mechanism to tag outputs with source data classification |
| **P4** | Periodic access rights review cadence | ISO 27001 A.5.18, NERC CIP-004 R4, SOC 2 CC6.2 | No periodic review of agent session access rights |
| **P4** | Credential rotation enforcement for session tokens | ISO 27001 A.5.17, NIST CSF PR.AA-01 | Session tokens persist; no rotation schedule |
| 🚫 | Physical security | NERC CIP-006/014 | Physical layer — out of scope |
| 🚫 | Personnel training and certification | NERC CIP-004 R1/R3, HIPAA §164.308(a)(5), NIST AI RMF GV-2.2 | Human compliance layer — out of scope |
| 🚫 | Training data governance and bias testing | ISO 42001 A.7.2–A.7.6 | Model development concern — out of scope for a governance protocol |
| 🚫 | Formal organizational policy documents (AI governance policy, QMS) | ISO 42001 A.2.2, Cl.5.2 | Management layer — Tank provides operational controls that a QMS references; does not generate the policy documents themselves |
