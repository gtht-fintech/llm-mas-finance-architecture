# Seven-Dimensional Evaluation Framework

The paper proposes a standardized, reproducible seven-dimensional evaluation framework for LLM-based Multi-Agent Systems in finance. Each dimension is tied to a specific failure mode identified in the MAST taxonomy (Cemri et al., 2025, arXiv:2503.13657).

## The Seven Dimensions

| # | Metric | Type | Range | Higher is better? | MAST Failure Mitigated |
|---|---|---|---|---|---|
| 1 | Task Completion Rate (TCR) | % | 0-100 | ✓ | task verification failure |
| 2 | Communication Cost (CC) | USD / 1k tokens | ≥ 0 | (lower is better) | inter-agent non-coordination |
| 3 | Context Drift Score (CDS) | % | 0-100 | ✗ | context drift (system design) |
| 4 | Cumulative Return (CR) | % | unbounded | ✓ | n/a (financial) |
| 5 | Sharpe Ratio (SR) | ratio | unbounded | ✓ | n/a (financial) |
| 6 | Maximum Drawdown (MDD) | % | 0-100 | ✗ | n/a (financial) |
| 7 | Win Rate vs Benchmarks (WR) | % | 0-100 | ✓ | n/a (financial) |

Plus three auxiliary indicators:

| Aux # | Metric | Tied to |
|---|---|---|
| A1 | Verification Pass Rate (VPR) | task verification failure (23.5% of MAST failures) |
| A2 | Sycophantic Convergence Rate (SCR) | system design (44.2% of MAST failures) |
| A3 | Citation Coverage & Audit Completeness (CCAC) | compliance / audit failure |

## Metric Definitions

### 1. Task Completion Rate (TCR)

```
TCR = (tasks completed successfully / total tasks attempted) × 100%
```

- **Source**: Final state inspection (LangGraph `END` state, CrewAI task output)
- **Lower bound for publication**: > 60% (paper §5.1 reports values 65-85%)
- **Worst case (ChatDev, Cemri 2025)**: 25%

### 2. Communication Cost (CC)

```
CC = total USD spent on LLM calls / (1k tokens generated)
```

- **Source**: LangSmith / OpenLLMetry / OpenAI usage API
- **Includes**: Input tokens, output tokens, retrieval token cost, tool-call tokens
- **Reference (Bertalanič 2026)**: Homogeneous 7-8B debate → 2.1-3.4× isolated self-correction
- **Reference (Wynn 2025)**: Adding weaker LLM to debate can *increase* total cost without quality gain

### 3. Context Drift Score (CDS)

```
CDS = 1 - (intersection(context, baseline) / union(context, baseline))
```

- **Source**: Rodrigues (2026, arXiv:2606.21666) Context Divergence Score
- **Range**: 0 (no drift) → 1 (complete divergence)
- **Mitigation**: Shared State Verification Protocol (SSVP) — periodic re-broadcast of ground-truth state

### 4. Cumulative Return (CR)

```
CR = (V_end - V_start) / V_start × 100%
```

- **Source**: Back-test engine (Zipline, Backtrader, or proprietary)
- **Caveat**: The paper treats all reported CRs as pre-transaction-cost upper bounds (§5.1.3 caveat)

### 5. Sharpe Ratio (SR)

```
SR = (mean_return - risk_free_rate) / std(returns) × sqrt(annualization_factor)
```

- **Source**: Back-test engine
- **Caveat**: TradingAgents reports pre-cost SR; independent replication not yet established

### 6. Maximum Drawdown (MDD)

```
MDD = max over t of (V_peak_t - V_t) / V_peak_t × 100%
```

- **Source**: Back-test engine
- **Reference (MASFIN)**: −0.1% (8 weeks, as-reported)

### 7. Win Rate vs Benchmarks (WR)

```
WR = (weeks outperforming all 3 of S&P 500 / NASDAQ-100 / DJIA) / total weeks × 100%
```

- **Caveat**: 8-week MASFIN back-test reports 6/8 (75%); institutional standard requires 12-24 month minimum

## Auxiliary Indicators

### A1. Verification Pass Rate (VPR)

```
VPR = (claims that passed L4 verification / total claims) × 100%
```

- **Implementation**: L4 layer cross-checks each agent's output against ground-truth sources (filings, market data) before emitting
- **Target**: > 95% for production deployment

### A2. Sycophantic Convergence Rate (SCR)

```
SCR = (debate rounds with > 85% token overlap with previous round) / total debate rounds
```

- **Reference (Wynn 2025)**: high SCR correlates with low final accuracy
- **Mitigation**: SSVP (per Rodrigues 2026) + L4 governance check at convergence

### A3. Citation Coverage & Audit Completeness (CCAC)

```
CCAC = (claims with traceable source / total claims) × compliance_threshold_factor
```

- **Source**: L4 audit log inspection
- **Target**: 100% for any claim that influences a financial decision

## Reference Implementation

The seven dimensions are implemented in `src/eval/` (forthcoming). Each metric is a single function with the signature:

```python
def metric_name(trace: ExecutionTrace) -> float:
    ...
```

The `ExecutionTrace` is the unified data structure produced by the L4 audit log + LangSmith / OpenLLMetry trace export.
