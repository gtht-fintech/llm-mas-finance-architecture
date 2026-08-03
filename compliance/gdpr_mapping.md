# GDPR (Regulation 2016/679) Compliance Mapping

**Regulation**: 2016/679 of the European Parliament and of the Council (General Data Protection Regulation)
**Entry into force**: 2018-05-25
**Scope**: All processing of personal data of EU/EEA data subjects

## Article-Level Mapping

| Article | Requirement | L4 Component | Reference Implementation |
|---|---|---|---|
| Art. 5 | Principles (lawfulness, purpose limitation, data minimisation) | `PermissionGate` + policy in `schemas/permission.yaml` | `src/l4_governance.py` |
| Art. 6 | Lawfulness of processing | `PermissionGate` (ALLOW/DENY based on legal basis) | `src/l4_governance.py` |
| Art. 7 | Conditions for consent | `HITLCheckpoint` (explicit human approval) | `src/l4_governance.py` |
| Art. 15 | Right of access | `AuditLog` (data subject can request their data) | `src/l4_governance.py` |
| Art. 16 | Right to rectification | `LongTermMemory.put()` with key-based update | `src/l2_capability.py` |
| Art. 17 | Right to erasure | `LongTermMemory` with explicit deletion primitive | `src/l2_capability.py` |
| Art. 20 | Right to data portability | `AuditLog` export | `src/l4_governance.py` |
| Art. 22 | Automated individual decision-making | `HITLCheckpoint` (mandatory for all automated decisions) | `src/l4_governance.py` |
| Art. 25 | Data protection by design and by default | `default_decision: DENY` in `schemas/permission.yaml` | `schemas/permission.yaml` |
| Art. 30 | Records of processing activities | `AuditLog` (hash-chained, append-only) | `src/l4_governance.py` |
| Art. 32 | Security of processing | `AuditLog.verify_chain()` + `FailureRecovery` | `src/l4_governance.py` |
| Art. 33 | Notification of personal data breach | `AuditLog` (timeline reconstruction) | `src/l4_governance.py` |
| Art. 35 | Data protection impact assessment | `docs/` (architecture spec serves as DPIA baseline) | This repository |

## Implementation Reference

The L4 layer implements GDPR "data protection by design and by default" (Art. 25) via the `default_decision: DENY` policy setting. Any action not explicitly granted in the policy is denied by default; the deployer must explicitly enumerate each permitted (agent, action, resource) triple.

Article 22 (automated decision-making) is the most critical for finance: every `tool.invoke:order.place` and `tool.invoke:account.transfer` action requires HITL approval. The `HITLCheckpoint` component implements this; the default `permission.yaml` already configures it for the `trading_agent`.

## Audit-Trail Tags

The L4 `AuditLog` automatically emits:

- `GDPR_ART_22` — on any `tool.invoke:order.place` or `tool.invoke:account.transfer`
- `GDPR_ART_30` — on every audit entry (records of processing)

## Open Questions

- **Article 17 erasure vs Article 30 records**: Erasure requests conflict with audit-log retention requirements. We recommend a 7-year retention for the audit log, with personal data fields pseudonymized after the data subject's relationship with the controller ends.
- **Article 22 in high-frequency trading**: The right to human intervention in every automated decision creates latency pressure. The default `HITLCheckpoint` includes a 5-minute timeout (configurable) for `order.place`; after timeout the action is denied by default (`on_timeout: "deny"` in `permission.yaml`).
