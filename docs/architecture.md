# Four-Layer Reference Architecture

This document specifies the **four-layer reference architecture (L1 Model / L2 Capability / L3 Collaboration / L4 Governance)** for LLM-based Multi-Agent Systems in high-stakes finance deployments, as introduced in the accompanying paper (EAAI submission, 2026).

The architecture is **framework-agnostic**: it does not depend on LangGraph, CrewAI, AutoGen, or any specific framework. Each layer can be implemented using any combination of these frameworks, or in custom code.

## Design Principles

1. **Separation of mechanism from policy.** The L4 layer separates *how* permissions are enforced (mechanism: PermissionGate, AuditLog, HITLCheckpoint) from *what* is permitted (policy: `schemas/permission.yaml`). The same codebase can be deployed in any jurisdiction with only configuration changes.
2. **Deny by default.** The L4 permission policy is `default_decision: DENY`. Any action not explicitly listed is denied. This is GDPR Art. 25 ("data protection by default") and EU AI Act Art. 17 ("quality management system") in a single line.
3. **Hash-chained audit log.** Every L4 decision emits a tamper-evident audit entry. The hash chain (SHA-256) provides cryptographic assurance of audit-log integrity.
4. **Human-in-the-loop on side effects.** Any side-effecting action (order placement, account transfer, report publish) requires explicit human approval via `HITLCheckpoint`. Timeouts default to denial.
5. **Sycophancy mitigation.** The L3 `ConvergenceDetector` flags sycophantic convergence in multi-agent debate (per Wynn et al., 2025 and Rodrigues, 2026). Mitigations include SSVP (Shared State Verification Protocol) and explicit anti-sycophancy prompts.

## Layer Specifications

### L1 Model Layer

Responsibilities:
- Base LLM selection (per deployment's accuracy/latency/cost requirements)
- Tiered invocation (FAST / MID / FRONTIER tiers)
- Model routing (cost-aware)
- Fallback handling (rate limits, outages)
- Capability probing (latency, throughput, accuracy)

**Reference implementation**: [`src/l1_model.py`](../src/l1_model.py)

### L2 Capability Layer

Responsibilities:
- Tool registry and adapter pattern
- Short-term (in-context) memory with summarization
- Long-term (vector + structured) memory with hybrid retrieval
- RAG with BM25 + dense retrieval
- Permission-aware tool invocation (delegated to L4)

**Reference implementation**: [`src/l2_capability.py`](../src/l2_capability.py)

### L3 Collaboration Layer

Responsibilities:
- Topology selection (SOP, state machine, role-play, blackboard)
- Message-passing protocol (sync vs async)
- Turn-taking and deadlock detection
- Convergence / sycophancy detection

**Reference implementation**: [`src/l3_collaboration.py`](../src/l3_collaboration.py)

### L4 Governance Layer (the paper's novel contribution)

Responsibilities:
- Permission gates (per-agent, per-tool, per-action)
- Append-only audit log (hash-chained, tamper-evident)
- Compliance mapping (EU AI Act, GDPR, PIPL, NIST AI RMF)
- Failure recovery (rollback, compensating actions via saga pattern)
- Human-in-the-loop (HITL) checkpoints
- Sycophantic-convergence mitigation

**Reference implementation**: [`src/l4_governance.py`](../src/l4_governance.py)

## Cross-Layer Interactions

| Interaction | Direction | Description |
|---|---|---|
| L1 → L4 | L1 invokes L4 for every model call | L4 records the call in the audit log (token cost, model ID, latency) |
| L2 → L4 | L2 invokes L4 before any side-effecting tool | L4 checks permission and either allows, denies, or requires HITL |
| L3 → L4 | L3 invokes L4 on convergence detection | L4 emits a `sycophantic_convergence` audit entry and may halt the debate |
| L4 → L1 | L4 routes high-stakes synthesis to FRONTIER tier | The default L4 policy has implicit model-tier preferences |
| L4 → L2 | L4 may invoke `LongTermMemory` for audit retention | E.g., retain order history for regulatory reporting |

## Comparison with Existing Frameworks

| Framework | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| MetaGPT | ✓ (single tier) | ✓ (tools) | ✓ (SOP) | ✗ |
| CrewAI | ✓ (multi-tier) | ✓ (tools + memory) | ✓ (role-play) | ✗ (no formal permission gate) |
| AutoGen | ✓ (multi-tier) | ✓ (tools + memory) | ✓ (group chat) | ✗ (no formal permission gate) |
| LangGraph | ✓ (multi-tier) | ✓ (tools + memory) | ✓ (state machine) | △ (interrupt primitive, but no audit log) |
| CAMEL | ✓ (single tier) | ✓ (tools) | ✓ (role-play) | ✗ |
| **PilotDeck (this paper)** | ✓ | ✓ | ✓ | ✓ (Governance as first-class) |

## Failure-Mode Coverage

The L4 layer is designed to mitigate the 14 MAST failure modes identified by Cemri et al. (2025). The most significant mappings:

| MAST Failure Category | % of Failures | L4 Mitigation |
|---|---|---|
| System design issues | 44.2% | Permission gates + audit log + convergence detection |
| Inter-agent non-coordination | 32.3% | Convergence detection + SSVP (per Rodrigues 2026) |
| Task verification failure | 23.5% | Verification Pass Rate (VPR) indicator + HITL checkpoint |
| **Total covered by L4** | **76.5%** | |

The remaining 23.5% (single-agent reasoning errors, fact hallucination, etc.) require L1 / L2 improvements and are not in the L4 scope.

## Deployment Topology

A typical high-stakes finance deployment using the four-layer architecture:

```
                    ┌─────────────────────────────────────────┐
                    │              L4 Governance               │
                    │  (permissions, audit, HITL, recovery)   │
                    └─────────────────────────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    │              L3 Collaboration         │
                    │  (orchestration, convergence detect)  │
                    └──────────────────────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    │              L2 Capability             │
                    │  (tools, memory, RAG)                  │
                    └──────────────────────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    │              L1 Model                  │
                    │  (tiered LLM invocation)               │
                    └──────────────────────────────────────┘
```

In a LangGraph implementation, the L4 layer is a `node` that runs in parallel with the L3 orchestration graph, intercepting every side-effecting tool call. In a CrewAI implementation, the L4 layer is a custom `step_callback` that wraps each agent action. The reference implementations in `src/` are framework-agnostic and can be ported to either.
