# PIPL (Personal Information Protection Law of the PRC) Compliance Mapping

**Law**: Personal Information Protection Law of the People's Republic of China (中华人民共和国个人信息保护法)
**Entry into force**: 2021-11-01
**Scope**: All processing of personal information of natural persons within the territory of the PRC

## Article-Level Mapping

| Article | Requirement | L4 Component | Reference Implementation |
|---|---|---|---|
| Art. 13 | Lawful basis (consent, contract, legal obligation, etc.) | `PermissionGate` | `src/l4_governance.py` |
| Art. 14 | Explicit consent | `HITLCheckpoint` | `src/l4_governance.py` |
| Art. 17 | Notification of processing | `AuditLog` (provenance recording) | `src/l4_governance.py` |
| Art. 19 | Retention period | `MemoryEntry.ttl_seconds` (L2) | `src/l2_capability.py` |
| Art. 23 | Data subject rights (access, correction, deletion) | `LongTermMemory` + `AuditLog.export` | `src/l2_capability.py` |
| Art. 24 | Automated decision-making transparency | `HITLCheckpoint` + audit log entry | `src/l4_governance.py` |
| Art. 27 | Cross-border transfer restrictions | `PermissionGate` with jurisdiction check | `src/l4_governance.py` |
| Art. 38 | Cross-border transfer mechanisms | `PermissionGate` (whitelist of jurisdictions) | `schemas/permission.yaml` |
| Art. 44-50 | Sensitive personal information | `PermissionGate` with elevated `REQUIRE_APPROVAL` | `schemas/permission.yaml` |
| Art. 51-59 | Security obligations | `AuditLog` (tamper-evidence) + `FailureRecovery` | `src/l4_governance.py` |
| Art. 66 | Records of processing | `AuditLog` | `src/l4_governance.py` |

## Implementation Reference

PIPL's Article 24 (automated decision-making) is similar to GDPR Art. 22 but with stricter "transparency" requirements. The L4 `HITLCheckpoint` already implements both; the audit-log entry for each `tool.invoke:order.place` and `report.publish` action includes:

- The agent ID (Article 17: notification)
- The decision rationale (Article 24: transparency)
- The approver's role (Article 14: explicit consent)
- The data subject's pseudonymized identifier (Article 17)

For cross-border transfer (Art. 38), the `PermissionGate` can be extended with a jurisdiction check. The default policy assumes all agents operate in a single jurisdiction; multi-jurisdiction deployments must add per-agent `jurisdiction` fields and a `jurisdictions.allowed` whitelist in `permission.yaml`.

## Audit-Trail Tags

- `PIPL_ART_24` — on any `tool.invoke:order.place`, `tool.invoke:account.transfer`, or `report.publish`
- `PIPL_ART_38` — on any cross-border data access

## Open Questions

- **Article 27 (cross-border)**: PIPL restricts cross-border data transfer; LLM API calls to non-PRC providers may constitute cross-border transfer of personal information embedded in prompts. We recommend stripping personal information from prompts at the L2 layer (`LongTermMemory.put` with automatic pseudonymization) before any cross-border LLM call.
- **Article 19 (retention)**: PIPL requires "the minimum necessary retention period". The default `MemoryEntry.ttl_seconds` is `None` (no expiry); deployers must set explicit TTLs based on business need.
