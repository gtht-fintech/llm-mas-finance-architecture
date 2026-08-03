"""
L1 Model Layer Reference Implementation
========================================

This module illustrates the L1 Model Layer of the four-layer reference
architecture proposed in the accompanying paper. L1 is responsible for
base LLM selection, tiered invocation (e.g., cheap local models for
routing, frontier models for synthesis), and model routing.

Key responsibilities:
- Tiered model registry (fast / mid / frontier tiers)
- Cost-aware routing
- Fallback handling (rate limits, outages)
- Capability probing (latency, throughput, accuracy)

Reference: paper §4.1 (L1 Model Layer specification)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
import time


class ModelTier(str, Enum):
    """Three-tier model registry. The actual deployment is framework-agnostic."""
    FAST = "fast"        # local 7-8B models, sub-100ms latency
    MID = "mid"          # 70B+ open-source, ~500ms latency
    FRONTIER = "frontier"  # GPT-4o / Claude 3.5+ Sonnet, ~1-2s latency


@dataclass
class ModelProfile:
    """Capability profile of a single LLM endpoint."""
    name: str
    tier: ModelTier
    cost_per_1k_tokens_usd: float
    avg_latency_ms: float
    context_window: int
    accuracy_proxy: float = 0.0  # 0-1, last benchmark score
    max_concurrent: int = 100


@dataclass
class RoutingDecision:
    """Result of the L1 routing decision."""
    model: ModelProfile
    reason: str
    estimated_cost_usd: float
    estimated_latency_ms: float


class ModelRouter:
    """
    L1 Model Router. Implements cost-aware tiered invocation.

    The router applies three policies in order:
    1. Hard constraints (max_cost_usd, max_latency_ms)
    2. Capability threshold (min_accuracy_proxy)
    3. Load balancing (current_concurrent < max_concurrent)

    For high-stakes finance use cases the paper recommends:
    - FRONTIER for: final synthesis, audit-grade outputs, compliance-bound
      decisions
    - MID for: planning, intermediate reasoning, tool selection
    - FAST for: routing, classification, simple extraction
    """

    def __init__(self, registry: list[ModelProfile]):
        self.registry = {m.name: m for m in registry}
        self._concurrency: dict[str, int] = {m.name: 0 for m in registry}

    def route(
        self,
        task_type: str,
        required_tier: ModelTier = ModelTier.MID,
        max_cost_usd: Optional[float] = None,
        max_latency_ms: Optional[float] = None,
        min_accuracy: Optional[float] = None,
    ) -> RoutingDecision:
        """Return the optimal model for the given task under the constraints."""
        candidates = [m for m in self.registry.values()
                      if m.tier == required_tier
                      and self._concurrency[m.name] < m.max_concurrent]
        if min_accuracy is not None:
            candidates = [m for m in candidates if m.accuracy_proxy >= min_accuracy]
        if max_cost_usd is not None:
            candidates = [m for m in candidates if m.cost_per_1k_tokens_usd <= max_cost_usd]
        if max_latency_ms is not None:
            candidates = [m for m in candidates if m.avg_latency_ms <= max_latency_ms]
        if not candidates:
            raise RuntimeError(
                f"No model satisfies constraints (tier={required_tier}, "
                f"max_cost={max_cost_usd}, max_latency={max_latency_ms}, "
                f"min_accuracy={min_accuracy})"
            )

        # Pick the highest-accuracy model among candidates
        chosen = max(candidates, key=lambda m: m.accuracy_proxy)
        return RoutingDecision(
            model=chosen,
            reason=f"tier={required_tier.value}, highest accuracy in tier",
            estimated_cost_usd=chosen.cost_per_1k_tokens_usd,
            estimated_latency_ms=chosen.avg_latency_ms,
        )

    def acquire(self, model_name: str) -> None:
        """Increment the concurrency counter for a model."""
        self._concurrency[model_name] += 1

    def release(self, model_name: str) -> None:
        """Decrement the concurrency counter for a model."""
        self._concurrency[model_name] = max(0, self._concurrency[model_name] - 1)


# Default registry for high-stakes finance deployments
def default_registry() -> list[ModelProfile]:
    """Return a sensible default registry. Numbers are 2026-Q2 estimates."""
    return [
        # FAST tier (local, sub-100ms)
        ModelProfile("qwen2.5-7b-instruct",      ModelTier.FAST,     0.0001,  80,   32000, accuracy_proxy=0.62, max_concurrent=200),
        ModelProfile("llama-3.1-8b-instruct",    ModelTier.FAST,     0.0001,  90,   32000, accuracy_proxy=0.65, max_concurrent=200),
        # MID tier (open-source 70B+)
        ModelProfile("qwen2.5-72b-instruct",     ModelTier.MID,      0.0009, 450,  128000, accuracy_proxy=0.78, max_concurrent=80),
        ModelProfile("llama-3.1-70b-instruct",   ModelTier.MID,      0.0009, 500,  128000, accuracy_proxy=0.79, max_concurrent=80),
        # FRONTIER tier (proprietary)
        ModelProfile("gpt-4o-2024-08",           ModelTier.FRONTIER, 0.0050, 1200, 128000, accuracy_proxy=0.88, max_concurrent=200),
        ModelProfile("claude-3-5-sonnet-20241022", ModelTier.FRONTIER, 0.0060, 1400, 200000, accuracy_proxy=0.89, max_concurrent=200),
    ]


if __name__ == "__main__":
    router = ModelRouter(default_registry())

    # Example 1: route a routing-classification task to FAST tier
    decision = router.route(task_type="routing", required_tier=ModelTier.FAST)
    print(f"[Routing]    -> {decision.model.name}  (cost ${decision.estimated_cost_usd}/1k, {decision.estimated_latency_ms}ms)")

    # Example 2: route a final-synthesis task to FRONTIER tier
    decision = router.route(task_type="synthesis", required_tier=ModelTier.FRONTIER, min_accuracy=0.85)
    print(f"[Synthesis]  -> {decision.model.name}  (cost ${decision.estimated_cost_usd}/1k, {decision.estimated_latency_ms}ms)")

    # Example 3: route a planning task to MID tier with cost constraint
    decision = router.route(task_type="planning", required_tier=ModelTier.MID, max_cost_usd=0.001)
    print(f"[Planning]   -> {decision.model.name}  (cost ${decision.estimated_cost_usd}/1k, {decision.estimated_latency_ms}ms)")
