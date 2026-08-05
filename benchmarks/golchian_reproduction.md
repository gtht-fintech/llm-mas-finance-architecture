# Golchian (2026) Framework Comparison — Reproduction Notes

**Source**: Golchian, P. (2026). "CrewAI vs LangGraph vs AutoGen 2026: Pricing, Benchmarks, and Which One to Build On."
**URL**: https://pooyagolchian.com/blog/crewai-vs-langgraph-autogen-comparison-2026/
**Type**: Personal blog post (NOT peer-reviewed)

## ⚠️ Critical Caveat

This is a **personal blog post**, not a peer-reviewed publication. The methodology has been critiqued in independent analyses (e.g., Groundy et al., 2026-05) on the following grounds:

1. **Single-author benchmark**: The author runs all benchmarks on a single machine (Apple M4 Max, 64GB RAM), with no replication on cloud infrastructure.
2. **Limited model diversity**: Only one model (Qwen3 32B via Ollama) is tested per tier; results do not generalize to claude-opus-5, gpt-5.6-sol, or DeepSeek.
3. **Subjective task suite**: The 200 tasks per tier are constructed by the author; their difficulty distribution may not match real-world MAS workloads.
4. **No independent replication**: As of 2026-08, no third party has independently reproduced these numbers.

**Recommendation**: Treat this benchmark as **industry-sensing data, not as rigorous academic evidence**. The paper's §4.5 framework-comparison table cites it for directional context only.

## Reproduced Numbers

The following numbers are quoted from the original blog post and are used in the paper's §4.5:

| Framework | Tier | Pass Rate (%) |
|---|---|---|
| LangGraph | Complex (>7 steps) | **87** |
| AutoGen | Complex (>7 steps) | 81 |
| CrewAI | Complex (>7 steps) | 74 |
| LangGraph | Medium (4-6 steps) | 92 |
| AutoGen | Medium (4-6 steps) | 89 |
| CrewAI | Medium (4-6 steps) | 86 |
| LangGraph | Simple (1-3 steps) | 96 |
| AutoGen | Simple (1-3 steps) | 95 |
| CrewAI | Simple (1-3 steps) | 94 |

The paper reports the **complex-tier** gap (LangGraph 87 - CrewAI 74 = 13 pp; LangGraph 87 - AutoGen 81 = 6 pp). This is the most defensible claim from the original source.

## Reproduction Script (sketch)

```python
# benchmarks/reproduce_golchian.py
# ⚠️ WARNING: This script is a sketch. The original methodology is not
# fully reproducible because the task suite is not public.

from typing import Callable
import statistics

def evaluate_framework(framework: str, tasks: list[dict], llm: Callable) -> dict:
    """Evaluate a single framework on a list of tasks."""
    results = {"pass": 0, "fail": 0, "by_complexity": {}}
    for task in tasks:
        complexity = task["complexity"]  # "simple" / "medium" / "complex"
        if complexity not in results["by_complexity"]:
            results["by_complexity"][complexity] = {"pass": 0, "fail": 0, "total": 0}
        # ... (framework-specific execution; see original blog for details)
        # This is a stub; the full reproduction requires:
        # 1. The original task suite (NOT public)
        # 2. The original Qwen3-32B + Ollama configuration
        # 3. The original evaluation rubric
        pass
    return results

# NOTE: A faithful reproduction is not possible without the original
# task suite. We strongly recommend independent re-runs on the
# GAIA benchmark (Mialon et al., 2023) or AgentBench (Liu et al., 2023)
# for academically defensible results.
```

## Recommended Independent Benchmarks

For academically rigorous framework comparison, we recommend:

1. **GAIA** (Mialon et al., 2023, arXiv:2311.12983) — 450 tasks across 3 difficulty levels
2. **AgentBench** (Liu et al., 2023, arXiv:2308.03688) — 8 environments, 1,000+ tasks
3. **SWE-bench** (Jimenez et al., 2023, arXiv:2310.06770) — Real GitHub issues as tasks
4. **MAST taxonomy** (Cemri et al., 2025, arXiv:2503.13657) — Failure-mode coverage rather than absolute accuracy

## Open Questions

- Why does LangGraph outperform on complex tasks but only match on simple tasks?
- Is the gap due to framework architecture, or to better defaults for the Qwen3 32B model?
- Does the gap persist on claude-opus-5 / gpt-5.6-sol / DeepSeek?
