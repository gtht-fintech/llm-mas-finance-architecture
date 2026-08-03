"""
L2 Capability Layer Reference Implementation
==============================================

This module illustrates the L2 Capability Layer of the four-layer
reference architecture. L2 provides the "abilities" agents use to act on
the world: tools, memory (short-term / long-term), and retrieval-augmented
generation (RAG).

Key responsibilities:
- Tool registry and adapter pattern
- Short-term (in-context) memory
- Long-term (vector + structured) memory
- RAG with hybrid (BM25 + dense) retrieval
- Permission-aware tool invocation (delegated from L4)

Reference: paper §4.2 (L2 Capability Layer specification)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
import hashlib
import time


@dataclass
class Tool:
    """A capability exposed to agents via the L2 layer."""
    name: str
    description: str
    function: Callable[..., Any]
    side_effect: bool = False  # if True, requires L4 permission gate
    cost_estimate_usd: float = 0.0
    p50_latency_ms: float = 100.0
    required_permission: str = "tool.invoke"


@dataclass
class MemoryEntry:
    """A single memory item with provenance and expiry."""
    key: str
    value: Any
    embedding: Optional[list[float]] = None
    created_at: float = field(default_factory=time.time)
    ttl_seconds: Optional[float] = None
    source: str = "agent"  # agent / user / tool
    permission_scope: str = "session"  # session / agent / global

    def is_expired(self) -> bool:
        if self.ttl_seconds is None:
            return False
        return (time.time() - self.created_at) > self.ttl_seconds


class ShortTermMemory:
    """In-context, conversation-scoped memory.

    Implements a sliding window with summarization. When the window
    exceeds `max_items`, the oldest items are summarized via a callable
    `summarizer` (typically a cheap L1 FAST-tier call).
    """

    def __init__(self, max_items: int = 50, summarizer: Optional[Callable[[list[MemoryEntry]], str]] = None):
        self.max_items = max_items
        self.summarizer = summarizer
        self._items: list[MemoryEntry] = []

    def put(self, entry: MemoryEntry) -> None:
        self._items.append(entry)
        if len(self._items) > self.max_items:
            evicted = self._items[:len(self._items) - self.max_items]
            self._items = self._items[-self.max_items:]
            if self.summarizer is not None:
                summary = self.summarizer(evicted)
                self._items.insert(0, MemoryEntry(key="__summary__", value=summary, source="summarizer"))

    def recent(self, k: int = 10) -> list[MemoryEntry]:
        return self._items[-k:]

    def clear(self) -> None:
        self._items.clear()


class LongTermMemory:
    """Persistent vector + structured memory with hybrid retrieval.

    In production this would be backed by:
    - Dense vectors: FAISS, Milvus, Pinecone, Weaviate
    - Sparse vectors: BM25 (rank_bm25, Elasticsearch)
    - Structured: PostgreSQL, MongoDB, etc.

    This reference implementation uses an in-memory store; the interface
    is the production-ready contract.
    """

    def __init__(self):
        self._dense: dict[str, list[float]] = {}
        self._structured: dict[str, dict[str, Any]] = {}

    def put(self, key: str, embedding: list[float], metadata: Optional[dict] = None) -> None:
        self._dense[key] = embedding
        if metadata:
            self._structured[key] = metadata

    def get(self, key: str) -> Optional[MemoryEntry]:
        if key not in self._dense:
            return None
        meta = self._structured.get(key, {})
        return MemoryEntry(
            key=key,
            value=meta.get("value"),
            embedding=self._dense[key],
            source=meta.get("source", "agent"),
            permission_scope=meta.get("permission_scope", "global"),
        )

    def hybrid_search(self, query_embedding: list[float], query_terms: list[str], top_k: int = 5) -> list[MemoryEntry]:
        """Hybrid BM25 + dense retrieval.

        Production deployments should use:
        - score = alpha * cosine(query_emb, emb) + (1 - alpha) * bm25(query_terms, text)
        - alpha typically 0.7-0.8 for high-recall domains
        """
        scored = []
        for key, emb in self._dense.items():
            cosine = self._cosine(query_embedding, emb)
            bm25 = self._bm25_proxy(query_terms, key)
            score = 0.75 * cosine + 0.25 * bm25
            scored.append((score, key))
        scored.sort(reverse=True)
        return [self.get(k) for _, k in scored[:top_k] if self.get(k) is not None]

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = sum(x * x for x in a) ** 0.5
        nb = sum(x * x for x in b) ** 0.5
        return dot / (na * nb + 1e-9)

    @staticmethod
    def _bm25_proxy(terms: list[str], key: str) -> float:
        """Trivial BM25 proxy based on term presence in key. Replace with rank_bm25 in prod."""
        key_l = key.lower()
        hits = sum(1 for t in terms if t.lower() in key_l)
        return hits / max(1, len(terms))


class ToolRegistry:
    """The L2 capability registry. Tools with `side_effect=True` require an
    L4 permission gate; this is enforced by the L4 layer, not L2."""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def list_side_effecting(self) -> list[Tool]:
        return [t for t in self._tools.values() if t.side_effect]


# Example tools for a finance deployment
def build_default_tool_registry() -> ToolRegistry:
    reg = ToolRegistry()
    # Read-only tools (no L4 permission gate needed)
    reg.register(Tool("market_data.fetch",   "Fetch current OHLCV + orderbook data",      lambda sym: {"sym": sym}, side_effect=False))
    reg.register(Tool("news.search",         "Search recent financial news",               lambda q: [], side_effect=False))
    reg.register(Tool("filings.search",      "Search SEC EDGAR / HKEX filings",            lambda q: [], side_effect=False))
    # Side-effecting tools (require L4 permission gate)
    reg.register(Tool("order.place",         "Place a live order at the broker API",       lambda o: {"id": "..."}, side_effect=True, required_permission="order.place"))
    reg.register(Tool("account.transfer",    "Internal account-to-account transfer",       lambda a: {"ok": True}, side_effect=True, required_permission="account.transfer"))
    reg.register(Tool("report.publish",      "Publish an investment-research report",      lambda r: {"url": "..."}, side_effect=True, required_permission="report.publish"))
    return reg


if __name__ == "__main__":
    reg = build_default_tool_registry()
    print(f"Registered {len(reg.list_side_effecting())} side-effecting tools requiring L4 permission gate")
    for t in reg.list_side_effecting():
        print(f"  - {t.name}  (requires: {t.required_permission})")
