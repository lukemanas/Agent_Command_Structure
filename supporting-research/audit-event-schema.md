# Audit Event Schema — Governance Protocol

> Structured log format for governance actions. Designed to satisfy EU AI Act Articles 12 (record-keeping) and 19 (log retention). Every event answers: **who authorized what, when, what happened, what was the result.**

## Design Constraints

1. **Append-only.** Events are immutable once written. No updates, no deletes.
2. **Self-contained.** Each event carries enough context to be understood without joining against other data.
3. **Machine-readable.** JSON, one event per line (JSONL). Queryable, exportable, archivable.
4. **Period-scoped.** Events are partitioned by project and operational period. A period's audit trail is a single, ordered sequence.
5. **Reconstructable.** The complete governance history of an operational period can be rebuilt from its audit events alone.

---

## Base Event Structure

Every audit event shares this envelope:

```json
{
  "version": "1",
  "event_id": "evt-a1b2c3d4",
  "timestamp": "2026-03-30T14:30:00Z",
  "project_id": "auth-refactor-001",
  "period_number": 1,
  "event_type": "checkin.passed",
  "actor": {
    "agent_id": "worker-1",
    "role": "worker",
    "human": "luke",
    "machine": "host-2"
  },
  "detail": { },
  "outcome": "success"
}
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | yes | Schema version (currently `"1"`) |
| `event_id` | string | yes | Unique event identifier (UUID or prefixed ID) |
| `timestamp` | string | yes | ISO 8601 UTC timestamp |
| `project_id` | string | yes | Project this event belongs to |
| `period_number` | int | yes | Operational period number (0 for pre-period events like project init) |
| `event_type` | string | yes | Dot-namespaced event type (see catalog below) |
| `actor` | object | yes | Who performed or triggered this action |
| `actor.agent_id` | string | yes | Agent name or `"human:<name>"` for human actions |
| `actor.role` | string | yes | Role at time of action (`worker`, `supervisor`, `chief-of-staff`, `planner`, `human`) |
| `actor.human` | string | yes | Human operator responsible for this agent |
| `actor.machine` | string | no | Machine the agent ran on |
| `detail` | object | yes | Event-type-specific payload (see catalog) |
| `outcome` | string | yes | `"success"`, `"failure"`, or `"denied"` |
| `reason` | string | no | Human-readable explanation (required when outcome is `failure` or `denied`) |
| `related_events` | []string | no | Event IDs of causally related events |

---

## Event Catalog

### Lifecycle Events

#### `project.initiated`
Project created from SOW. Marks the transition from base state to harness.

```json
{
  "event_type": "project.initiated",
  "actor": { "agent_id": "human:luke", "role": "human", "human": "luke" },
  "detail": {
    "sow": {
      "project_title": "Auth Module Refactor",
      "objective": "Replace session storage with new token-based auth",
      "risk_classification": "low",
      "collaborator_ids": ["~rob"]
    }
  },
  "outcome": "success"
}
```

#### `lifecycle.transition`
Phase transition in the governance lifecycle.

```json
{
  "event_type": "lifecycle.transition",
  "detail": {
    "from_phase": "harness",
    "to_phase": "planning",
    "trigger": "sow_approved"
  }
}
```

Valid phases: `base`, `harness`, `planning`, `operational`, `demobilization`.

#### `period.started`
Operational period begins (MOBILIZE state entered).

```json
{
  "event_type": "period.started",
  "detail": {
    "oap_hash": "sha256:abc123...",
    "duration_estimate": "4h",
    "objective_count": 2,
    "assignment_count": 3,
    "risk_classification": "low"
  }
}
```

#### `period.state_changed`
Period state machine transition.

```json
{
  "event_type": "period.state_changed",
  "detail": {
    "from_state": "MOBILIZE",
    "to_state": "EXECUTE",
    "trigger": "cos_ready_signal"
  }
}
```

Valid states: `MOBILIZE`, `EXECUTE`. Demobilization is a lifecycle phase, not a period state.

#### `period.completed`
Operational period ends.

```json
{
  "event_type": "period.completed",
  "detail": {
    "exit_reason": "all_objectives_verified",
    "objectives_completed": 2,
    "objectives_total": 2,
    "duration_actual": "3h42m",
    "duration_estimate": "4h",
    "agents_spawned": 4,
    "agents_failed": 0
  }
}
```

`exit_reason` values: `all_objectives_verified`, `timer_expired`, `human_terminated`.

---

### OAP Events

#### `oap.submitted`
Planning agent submits OAP for human review.

```json
{
  "event_type": "oap.submitted",
  "actor": { "agent_id": "planner-1", "role": "planner", "human": "luke" },
  "detail": {
    "oap_hash": "sha256:abc123...",
    "objective_ids": ["obj-1", "obj-2"],
    "duration_estimate": "4h",
    "assignment_count": 3
  }
}
```

#### `oap.approved`
Human approves OAP. This is the authorization gate — execution cannot begin without it.

```json
{
  "event_type": "oap.approved",
  "actor": { "agent_id": "human:luke", "role": "human", "human": "luke" },
  "detail": {
    "oap_hash": "sha256:abc123...",
    "approval_method": "command"
  }
}
```

#### `oap.scope_reduced`
Human reduces OAP scope mid-period (scope can shrink, never expand).

```json
{
  "event_type": "oap.scope_reduced",
  "actor": { "agent_id": "human:luke", "role": "human", "human": "luke" },
  "detail": {
    "removed_objectives": ["obj-3"],
    "reason": "Deprioritized — not needed for initial release"
  }
}
```

---

### Agent Events

#### `agent.spawned`
Agent created within the project.

```json
{
  "event_type": "agent.spawned",
  "actor": { "agent_id": "cos-1", "role": "chief-of-staff", "human": "luke" },
  "detail": {
    "spawned_agent": "worker-1",
    "spawned_role": "worker",
    "runtime": "claude",
    "machine": "host-2",
    "objective_ids": ["obj-1"],
    "skill": "worker"
  }
}
```

#### `checkin.passed`
Agent passes the checkin gate (orientation validated before work begins).

```json
{
  "event_type": "checkin.passed",
  "actor": { "agent_id": "worker-1", "role": "worker", "human": "luke" },
  "detail": {
    "validated_fields": ["role", "objective_ids", "period_state", "risk_tier", "supervisor"],
    "validator": "orchestrator"
  }
}
```

#### `checkin.failed`
Agent fails the checkin gate.

```json
{
  "event_type": "checkin.failed",
  "actor": { "agent_id": "worker-1", "role": "worker", "human": "luke" },
  "detail": {
    "failed_fields": ["period_state"],
    "expected": "MOBILIZE",
    "actual": "EXECUTE",
    "attempt": 2,
    "max_attempts": 3
  },
  "outcome": "failure"
}
```

#### `checkin.comprehension_validated`
CoS validates agent comprehension (soft enforcement, separate from mechanical checkin).

```json
{
  "event_type": "checkin.comprehension_validated",
  "actor": { "agent_id": "cos-1", "role": "chief-of-staff", "human": "luke" },
  "detail": {
    "validated_agent": "worker-1",
    "verdict": "pass"
  }
}
```

#### `agent.failed`
Agent failure detected by supervisory chain.

```json
{
  "event_type": "agent.failed",
  "actor": { "agent_id": "sup-1", "role": "supervisor", "human": "luke" },
  "detail": {
    "failed_agent": "worker-1",
    "failure_mode": "unresponsive",
    "detection_method": "silence_timeout",
    "replacement_spawned": "worker-1b"
  }
}
```

#### `agent.killed`
Agent terminated (demob, failure replacement, or human command).

```json
{
  "event_type": "agent.killed",
  "detail": {
    "killed_agent": "worker-1",
    "reason": "period_demobilization",
    "killed_by": "cos-1"
  }
}
```

---

### Issue Events

#### `issue.created`
CoS creates a GitHub issue from an OAP objective.

```json
{
  "event_type": "issue.created",
  "actor": { "agent_id": "cos-1", "role": "chief-of-staff", "human": "luke" },
  "detail": {
    "objective_id": "obj-1",
    "github_issue": 42,
    "assigned_to": "worker-1",
    "acceptance_criteria_count": 2
  }
}
```

#### `issue.transitioned`
Issue state change (role-gated).

```json
{
  "event_type": "issue.transitioned",
  "actor": { "agent_id": "worker-1", "role": "worker", "human": "luke" },
  "detail": {
    "objective_id": "obj-1",
    "github_issue": 42,
    "from_state": "in-progress",
    "to_state": "ready-for-review"
  }
}
```

Valid transitions and required roles:
- `open` → `in-progress` (worker)
- `in-progress` → `ready-for-review` (worker)
- `ready-for-review` → `pending-review` (supervisor — must verify acceptance criteria)
- `pending-review` → `closed` (CoS — adversarial review)
- any → `open` (CoS — reopen after failed review)

#### `issue.verified`
Acceptance criteria verified before close.

```json
{
  "event_type": "issue.verified",
  "actor": { "agent_id": "sup-1", "role": "supervisor", "human": "luke" },
  "detail": {
    "objective_id": "obj-1",
    "github_issue": 42,
    "verification_method": "automated_tests",
    "test_count": 14,
    "tests_passing": 14,
    "criteria_met": ["All existing tests pass", "New store handles 1000 concurrent sessions"]
  }
}
```

---

### Escalation Events

#### `escalation.raised`
Blocker escalated through chain of command.

```json
{
  "event_type": "escalation.raised",
  "actor": { "agent_id": "worker-1", "role": "worker", "human": "luke" },
  "detail": {
    "escalated_to": "sup-1",
    "blocker_type": "out-of-scope",
    "objective_id": "obj-2",
    "description": "Need write access to legacy-auth repo not listed in OAP"
  }
}
```

#### `escalation.resolved`
Escalation resolved at some level of the chain.

```json
{
  "event_type": "escalation.resolved",
  "detail": {
    "resolved_by": "cos-1",
    "resolution": "Resequenced obj-2 to start after obj-1 completes",
    "related_events": ["evt-escalation-123"]
  }
}
```

---

### Access Control Events

#### `acl.granted`
Network ACL tag applied to project agents from OAP requirements. (Reference implementations: Tailscale ACL tags, Kubernetes NetworkPolicies, Calico, AWS SCPs.)

```json
{
  "event_type": "acl.granted",
  "detail": {
    "tag": "tag:project-auth-refactor-001",
    "acl_rules": [
      {"dest": "github.com:443", "action": "accept"},
      {"dest": "api.github.com:443", "action": "accept"}
    ],
    "derived_from": "oap.objectives[0].required_access",
    "oap_hash": "sha256:abc123..."
  }
}
```

#### `acl.revoked`
ACL tags revoked (primary revocation mechanism on period close).

```json
{
  "event_type": "acl.revoked",
  "detail": {
    "tag": "tag:project-auth-refactor-001",
    "reason": "period_demobilization",
    "revoked_rules_count": 2
  }
}
```

#### `credential.issued`
Credentials mounted into project container from vault.

```json
{
  "event_type": "credential.issued",
  "detail": {
    "credential_type": "github_token",
    "scope": "acme-corp/auth-service:write",
    "expires_at": "2026-03-30T18:30:00Z",
    "issued_to": "project-container:auth-refactor-001"
  }
}
```

#### `credential.expired`
Credentials expired or revoked.

```json
{
  "event_type": "credential.expired",
  "detail": {
    "credential_type": "github_token",
    "reason": "period_demobilization"
  }
}
```

---

### Timer Events

#### `timer.extended`
Human extends the operational period timer (only human can do this).

```json
{
  "event_type": "timer.extended",
  "actor": { "agent_id": "human:luke", "role": "human", "human": "luke" },
  "detail": {
    "previous_duration": "4h",
    "extension": "2h",
    "new_duration": "6h",
    "requested_by": "cos-1",
    "justification": "obj-2 migration testing taking longer than estimated"
  }
}
```

#### `timer.expired`
Timer reached zero without extension.

```json
{
  "event_type": "timer.expired",
  "detail": {
    "duration": "4h",
    "objectives_completed": 1,
    "objectives_total": 2
  }
}
```

---

### Demobilization Events

#### `arr.submitted`
After-Action Report submitted for human review.

```json
{
  "event_type": "arr.submitted",
  "actor": { "agent_id": "cos-1", "role": "chief-of-staff", "human": "luke" },
  "detail": {
    "objectives_completed": 2,
    "objectives_total": 2,
    "arr_hash": "sha256:def456...",
    "duration_actual": "3h42m"
  }
}
```

#### `arr.approved`
Human reviews and approves the ARR.

```json
{
  "event_type": "arr.approved",
  "actor": { "agent_id": "human:luke", "role": "human", "human": "luke" },
  "detail": {
    "arr_hash": "sha256:def456...",
    "merge_commit": "abc1234"
  }
}
```

---

## Event Type Summary

| Category | Event Types | Count |
|----------|------------|-------|
| Lifecycle | `project.initiated`, `lifecycle.transition`, `period.started`, `period.state_changed`, `period.completed` | 5 |
| OAP | `oap.submitted`, `oap.approved`, `oap.scope_reduced` | 3 |
| Agent | `agent.spawned`, `checkin.passed`, `checkin.failed`, `checkin.comprehension_validated`, `agent.failed`, `agent.killed` | 6 |
| Issue | `issue.created`, `issue.transitioned`, `issue.verified` | 3 |
| Escalation | `escalation.raised`, `escalation.resolved` | 2 |
| Access | `acl.granted`, `acl.revoked`, `credential.issued`, `credential.expired` | 4 |
| Timer | `timer.extended`, `timer.expired` | 2 |
| Demobilization | `arr.submitted`, `arr.approved` | 2 |
| **Total** | | **27** |

---

## Compliance Mapping

| EU AI Act Requirement | Audit Events That Satisfy It |
|----------------------|------------------------------|
| Art. 12 — Automated action logging | All 27 event types; every governance action is recorded |
| Art. 12 — Identify reference period | `period.started`, `period.completed` bracket each OP |
| Art. 14 — Human oversight at decision points | `oap.approved`, `timer.extended`, `oap.scope_reduced`, `arr.approved` — all require `actor.role: "human"` |
| Art. 19 — Documented authorization trail | `oap.approved` → `acl.granted` → `credential.issued` — unbroken chain from approval to access |
| Art. 19 — Log retention | Events are append-only JSONL, partitioned by project/period, archivable |
| Rollback procedure | `arr.approved` records `merge_commit` — one commit per OP = one rollback point |

---

## Storage

Events are written as JSONL (one JSON object per line) to an append-only stream. Storage backend is implementation-specific:
- **Append-only stream (e.g., Redis stream, Kafka topic, NATS JetStream):** keyed by `<project_id>:<period_number>`
- **File-based:** `<project>/.governance/audit/period-<N>.jsonl`
- **Enterprise:** Forward to SIEM, Splunk, or compliance system via webhook

Retention policy: events are retained for the lifetime of the project plus any regulatory retention period (EU AI Act Art. 19 requires logs retained "for a period appropriate to the intended purpose of the AI system" — minimum recommended: 5 years for regulated industries).
