# NIST AI Risk Management Framework (AI RMF 1.0) Compliance Mapping

**Framework**: NIST AI Risk Management Framework 1.0
**Released**: 2023-01-26 (NIST AI 100-1)
**Status**: Voluntary (no statutory force)
**Companion resources**: NIST AI RMF Generative AI Profile (NIST AI 600-1, 2024-07)

## Four-Function Mapping

The NIST AI RMF is organized into four core functions: **GOVERN**, **MAP**, **MEASURE**, **MANAGE**. The L4 Governance Layer is designed to support all four.

| Function | NIST Description | L4 Component(s) | Reference Implementation |
|---|---|---|---|
| **GOVERN** | Establish a culture of risk management | `L4GovernanceLayer` (orchestrator) + policy governance | `src/l4_governance.py`, `schemas/permission.yaml` |
| **MAP** | Establish the context to frame risks related to AI systems | `PermissionGate` (deny by default) + `AuditLog` (risk register) | `src/l4_governance.py` |
| **MEASURE** | Employ quantitative, qualitative, or mixed-method tools to analyze and track AI risk | Seven-dimensional evaluation framework | `docs/evaluation-framework.md` |
| **MANAGE** | Allocate risk resources to mapped and measured risks | `HITLCheckpoint` (escalation) + `FailureRecovery` (mitigation) | `src/l4_governance.py` |

## Subcategory Mapping (selected)

| Subcategory | NIST Description | L4 Implementation |
|---|---|---|
| GOVERN 1.2 | Legal and regulatory requirements are understood and managed | All four `compliance/*.md` mappings |
| GOVERN 2.1 | Roles and responsibilities are documented | `schemas/permission.yaml` (per-agent definitions) |
| GOVERN 4.1 | Organizational document management | `docs/` directory in this repo |
| MAP 1.1 | Context is established and understood | Architecture diagram (Figure 1 of paper) + this repository |
| MAP 3.1 | AI capabilities and risks are documented | Paper §6 (Risks) + `docs/evaluation-framework.md` |
| MEASURE 2.4 | Effectiveness of risk controls is evaluated | Seven-dimensional evaluation framework |
| MEASURE 2.11 | AI system performance is documented | `docs/evaluation-framework.md` |
| MANAGE 1.1 | AI risks are prioritized | `permission.yaml` compliance tags |
| MANAGE 2.1 | Resources for AI risk management are allocated | `HITLCheckpoint` (human-in-the-loop) |
| MANAGE 4.1 | AI risks are managed at the system level | `L4GovernanceLayer` (single governance interface) |

## Implementation Reference

NIST AI RMF's GOVERN function is most strongly supported by the `L4GovernanceLayer` orchestrator and the policy-as-code approach (`schemas/permission.yaml`). The MEASURE function is supported by the seven-dimensional evaluation framework; the MANAGE function is supported by `HITLCheckpoint` and `FailureRecovery`.

The NIST Generative AI Profile (NIST AI 600-1) adds specific guidance for LLM-based systems. The L4 layer addresses the following GV- (Govern), MS- (Map and Measure), and MG- (Manage) items:

- **GV-1.1-001** (Policies for AI risks): `schemas/permission.yaml` (policy-as-code)
- **MS-1.1-001** (Documentation of training data): `src/l2_capability.py` (`LongTermMemory` provenance)
- **MG-1.1-001** (AI system decommissioning): `LongTermMemory` deletion primitive

## Audit-Trail Tags

- `NIST_AI_RMF_GOVERN` — on every audit entry
- `NIST_AI_RMF_MAP` — on any `data.read` or `data.write`
- `NIST_AI_RMF_MEASURE` — on any evaluation-framework metric computation
- `NIST_AI_RMF_MANAGE` — on any `HITLCheckpoint` invocation

## Open Questions

- **GOVERN 2.2 (AI accountability)**: NIST recommends a named accountable individual for each AI system. The L4 layer supports this via the `agent_id` and `approver_role` fields, but the deployer must maintain the organization-level accountability register separately.
- **MEASURE 2.10 (post-deployment monitoring)**: NIST recommends continuous monitoring in production. We recommend integrating the L4 `AuditLog` with a SIEM (Security Information and Event Management) system for real-time alerting.
