# EU AI Act (Regulation 2024/1689) Compliance Mapping

**Regulation**: 2024/1689 of the European Parliament and of the Council ("AI Act")
**Entry into force**: 2024-08-01
**Full applicability**: 2026-08-02
**Risk classification**: Most LLM-MAS finance deployments are classified as **HIGH-RISK** (Annex III, §5: "Access to essential public services and benefits" / "Creditworthiness assessment")

## Article-Level Mapping

| Article | Requirement | L4 Component | Reference Implementation |
|---|---|---|---|
| Art. 9 | Risk management system | `L4GovernanceLayer` (orchestrator) | `src/l4_governance.py` |
| Art. 10 | Data and data governance | `LongTermMemory` (L2) + `AuditLog` (L4) | `src/l2_capability.py`, `src/l4_governance.py` |
| Art. 11 | Technical documentation | `docs/` directory in this repo | This repository |
| Art. 12 | Record-keeping (automatic logging) | `AuditLog` (L4) | `src/l4_governance.py` |
| Art. 13 | Transparency to deployers | `HITLCheckpoint` (L4) | `src/l4_governance.py` |
| Art. 14 | Effective human oversight | `HITLCheckpoint` (L4) | `src/l4_governance.py` |
| Art. 15 | Accuracy, robustness, cybersecurity | `ConvergenceDetector` (L3) + `FailureRecovery` (L4) | `src/l3_collaboration.py`, `src/l4_governance.py` |
| Art. 17 | Quality management system | `L4GovernanceLayer` + policy in `schemas/permission.yaml` | This repository |

## Implementation Reference

The default L4 permission policy (`schemas/permission.yaml`) already implements Articles 12, 13, 14, and 17. To extend to Articles 10 and 15, the deployer must:

1. Configure `LongTermMemory` (L2) to retain training/evaluation data provenance for ≥ 6 months
2. Configure `ConvergenceDetector` (L3) threshold per the deployment's accuracy requirement
3. Configure `FailureRecovery` (L4) with explicit rollback semantics for all side-effecting tools

## Audit-Trail Tags

The L4 `AuditLog` automatically emits the following compliance tags for regulated actions:

- `EU_AI_ACT_ART_12` — emitted on every audit entry (logging requirement)
- `EU_AI_ACT_ART_14` — emitted when `HITLCheckpoint` is invoked

## Open Questions

- **Article 9.7**: The AI Act requires that the "level of accuracy ... be declared in the instructions for use". We recommend the seven-dimensional evaluation framework as the canonical declaration, but this is not yet regulatory guidance.
- **Article 15.4**: The AI Act requires cybersecurity measures "appropriate to the circumstances". We recommend SSVP (per Rodrigues, 2026) + L4 hash-chained audit log; independent regulatory guidance is pending.
