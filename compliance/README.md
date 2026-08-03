# Compliance Mapping

This directory maps the **L4 Governance Layer** of the four-layer reference architecture to four major regulatory and standards frameworks. Each mapping identifies the specific L4 component(s) that satisfy a given regulatory requirement.

## Contents

| File | Regulatory Framework | Region | Status |
|---|---|---|---|
| [`eu_ai_act_mapping.md`](eu_ai_act_mapping.md) | EU AI Act (Regulation 2024/1689) | European Union | In force 2024-08-01; full applicability 2026-08-02 |
| [`gdpr_mapping.md`](gdpr_mapping.md) | General Data Protection Regulation (Regulation 2016/679) | European Union | In force |
| [`pipl_mapping.md`](pipl_mapping.md) | Personal Information Protection Law | People's Republic of China | In force 2021-11-01 |
| [`nist_ai_rmf_mapping.md`](nist_ai_rmf_mapping.md) | NIST AI Risk Management Framework 1.0 | United States | Voluntary (released 2023-01-26) |

## How to Read the Mappings

Each mapping document follows a common structure:

1. **Scope** — which L4 components and which MAS actions the regulation applies to
2. **Article-level mapping** — table mapping regulation articles to L4 components
3. **Implementation reference** — pointer to the corresponding reference implementation in `src/l4_governance.py`
4. **Audit-trail tags** — the `compliance_tags` emitted in the audit log for each regulated action
5. **Open questions** — items the paper flags for follow-up

## Cross-Framework Synthesis

The L4 governance layer is designed to be **regulation-agnostic at the component level** but **regulation-specific at the policy level**. The same `PermissionGate`, `AuditLog`, `FailureRecovery`, and `HITLCheckpoint` components support all four frameworks; only the policy in `schemas/permission.yaml` and the compliance tags in the audit log change.

This is the key architectural insight: by separating **mechanism** (the L4 components) from **policy** (the YAML/JSON configuration), the same codebase can be deployed in any jurisdiction with only configuration changes — no code modifications required.

## Compliance Tag Vocabulary

The full compliance-tag vocabulary is defined in `schemas/audit_log.json` under `compliance_tags`. New tags can be added without code changes; downstream consumers (regulatory reporting, internal audit dashboards) consume the tags to determine which regulations apply to which actions.
