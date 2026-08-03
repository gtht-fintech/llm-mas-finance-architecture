"""
L3 Collaboration Layer Reference Implementation
=================================================

This module illustrates the L3 Collaboration Layer of the four-layer
reference architecture. L3 governs how multiple agents coordinate:
orchestration topology (SOP, state machine, role-play, blackboard),
message-passing protocols, and turn-taking.

Key responsibilities:
- Topology selection (SOP / state machine / role-play / blackboard)
- Message-passing protocol (sync vs async)
- Turn-taking and deadlock detection
- Convergence / sycophancy detection (mitigation per Rodrigues, 2026)

Reference: paper §4.3 (L3 Collaboration Layer specification)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
import time


class TopologyType(str, Enum):
    SOP = "sop"                  # Standard Operating Procedure, MetaGPT-style
    STATE_MACHINE = "state_machine"  # LangGraph-style explicit states
    ROLE_PLAY = "role_play"      # CrewAI/AutoGen dynamic role assignment
    BLACKBOARD = "blackboard"    # Shared mutable state, asynchronous agents


@dataclass
class Message:
    """A message exchanged between agents in the L3 layer."""
    sender: str
    recipient: str
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConvergenceDetector:
    """Detects sycophantic convergence in multi-agent debate.

    Per Rodrigues (2026, arXiv:2606.21666), naive full-broadcast
    debate can produce 34% "context contamination". This detector
    flags when N consecutive rounds produce >85% token overlap, which
    is a strong indicator of sycophantic convergence (a known failure
    mode per Wynn et al., 2025).
    """

    overlap_threshold: float = 0.85
    consecutive_rounds: int = 2

    def __init__(self):
        self._recent_messages: list[set[str]] = []
        self._consecutive_high_overlap: int = 0

    def observe(self, message: Message) -> Optional[str]:
        tokens = set(message.content.lower().split())
        if not tokens:
            return None
        if self._recent_messages:
            last = self._recent_messages[-1]
            overlap = len(tokens & last) / max(1, len(tokens | last))
            if overlap >= self.overlap_threshold:
                self._consecutive_high_overlap += 1
                if self._consecutive_high_overlap >= self.consecutive_rounds:
                    return ("sycophantic_convergence",
                            f"overlap={overlap:.2f} for {self._consecutive_high_overlap} consecutive rounds")
            else:
                self._consecutive_high_overlap = 0
        self._recent_messages.append(tokens)
        if len(self._recent_messages) > 10:
            self._recent_messages.pop(0)
        return None

    def reset(self) -> None:
        self._recent_messages.clear()
        self._consecutive_high_overlap = 0


@dataclass
class CollaborationPolicy:
    """A single collaboration policy governing one L3 topology."""
    topology: TopologyType
    max_rounds: int = 10
    require_quorum: bool = False           # require N-of-M agents to agree
    quorum_size: int = 2
    enable_convergence_detection: bool = True
    timeout_seconds: float = 300.0

    def should_terminate(self, round_num: int, agreement_count: int) -> bool:
        if round_num >= self.max_rounds:
            return True
        if self.require_quorum and agreement_count >= self.quorum_size:
            return True
        return False


class CollaborationOrchestrator:
    """The L3 orchestrator. Reference implementation.

    In production this would be a LangGraph `StateGraph`, a CrewAI
    `Crew`, an AutoGen `GroupChat`, or a custom blackboard. This
    reference implementation is framework-agnostic.
    """

    def __init__(self, policy: CollaborationPolicy):
        self.policy = policy
        self.convergence = ConvergenceDetector() if policy.enable_convergence_detection else None
        self._messages: list[Message] = []

    def send(self, message: Message) -> Optional[str]:
        """Send a message. Returns a warning string if convergence is detected."""
        self._messages.append(message)
        if self.convergence is not None:
            return self.convergence.observe(message)
        return None

    def transcript(self) -> list[Message]:
        return list(self._messages)


if __name__ == "__main__":
    # Example 1: SOP topology (MetaGPT-style, deterministic)
    sop_policy = CollaborationPolicy(topology=TopologyType.SOP, max_rounds=20)
    print(f"SOP topology: max_rounds={sop_policy.max_rounds}, quorum={sop_policy.require_quorum}")

    # Example 2: Role-play with convergence detection (CrewAI-style)
    rp_policy = CollaborationPolicy(
        topology=TopologyType.ROLE_PLAY,
        max_rounds=10,
        require_quorum=True,
        quorum_size=3,
        enable_convergence_detection=True,
    )
    print(f"Role-play topology: max_rounds={rp_policy.max_rounds}, quorum=3-of-N, convergence_detection=True")

    # Example 3: State machine (LangGraph-style, explicit)
    sm_policy = CollaborationPolicy(topology=TopologyType.STATE_MACHINE, max_rounds=50, enable_convergence_detection=False)
    print(f"State-machine topology: max_rounds={sm_policy.max_rounds}, convergence_detection=False")
