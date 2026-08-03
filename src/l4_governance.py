"""
L4 Governance Layer Reference Implementation
==============================================

This module illustrates the L4 Governance Layer of the four-layer
reference architecture. L4 is the novel contribution of the paper: it
provides runtime-enforced permissions, audit logging, compliance
mapping, failure recovery, and human-in-the-loop checkpoints.

Key responsibilities:
- Permission gates (per-agent, per-tool, per-action)
- Append-only audit log (forensic / regulatory)
- Compliance mapping (EU AI Act, GDPR, PIPL, NIST AI RMF)
- Failure recovery (rollback, compensating actions)
- Human-in-the-loop (HITL) checkpoints
- Sycophantic-convergence mitigation

Reference: paper §4.4 (L4 Governance Layer specification)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
import hashlib
import json
import time
import uuid


class PermissionAction(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


@dataclass
class AuditEntry:
    """A single append-only audit-log entry. The hash chain ensures tamper-evidence."""
    entry_id: str
    timestamp: str
    agent_id: str
    action: str
    resource: str
    decision: str
    rationale: str
    prev_hash: str
    entry_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id":     self.entry_id,
            "timestamp":    self.timestamp,
            "agent_id":     self.agent_id,
            "action":       self.action,
            "resource":     self.resource,
            "decision":     self.decision,
            "rationale":    self.rationale,
            "prev_hash":    self.prev_hash,
            "entry_hash":   self.entry_hash,
        }


class AuditLog:
    """Append-only, hash-chained audit log.

    Each entry's hash is computed as:
        entry_hash = SHA256(prev_hash || entry_id || timestamp || agent_id
                            || action || resource || decision || rationale)

    Any tampering with a historical entry breaks the chain. The full
    schema is in `schemas/audit_log.json`.
    """

    GENESIS_HASH = "0" * 64

    def __init__(self):
        self._entries: list[AuditEntry] = []

    def append(
        self,
        agent_id: str,
        action: str,
        resource: str,
        decision: str,
        rationale: str,
    ) -> AuditEntry:
        prev_hash = self._entries[-1].entry_hash if self._entries else self.GENESIS_HASH
        entry_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        payload = json.dumps({
            "entry_id":  entry_id,
            "timestamp": timestamp,
            "agent_id":  agent_id,
            "action":    action,
            "resource":  resource,
            "decision":  decision,
            "rationale": rationale,
        }, sort_keys=True, separators=(",", ":"))
        entry_hash = hashlib.sha256((prev_hash + payload).encode("utf-8")).hexdigest()
        entry = AuditEntry(
            entry_id=entry_id,
            timestamp=timestamp,
            agent_id=agent_id,
            action=action,
            resource=resource,
            decision=decision,
            rationale=rationale,
            prev_hash=prev_hash,
            entry_hash=entry_hash,
        )
        self._entries.append(entry)
        return entry

    def entries(self) -> list[AuditEntry]:
        return list(self._entries)

    def verify_chain(self) -> tuple[bool, Optional[str]]:
        """Verify the hash chain integrity. Returns (is_valid, first_invalid_entry_id)."""
        prev = self.GENESIS_HASH
        for e in self._entries:
            if e.prev_hash != prev:
                return False, e.entry_id
            payload = json.dumps({
                "entry_id":  e.entry_id,
                "timestamp": e.timestamp,
                "agent_id":  e.agent_id,
                "action":    e.action,
                "resource":  e.resource,
                "decision":  e.decision,
                "rationale": e.rationale,
            }, sort_keys=True, separators=(",", ":"))
            expected = hashlib.sha256((prev + payload).encode("utf-8")).hexdigest()
            if e.entry_hash != expected:
                return False, e.entry_id
            prev = e.entry_hash
        return True, None


class PermissionGate:
    """L4 permission gate. Decides ALLOW / DENY / REQUIRE_APPROVAL."""

    def __init__(self, policy_path: Optional[str] = None):
        # Reference: schemas/permission.yaml for the policy schema
        self._policy: dict[str, list[str]] = {
            # agent_id -> list of permitted actions
            "junior_quant_agent":  ["tool.invoke:market_data.fetch", "tool.invoke:news.search", "tool.invoke:filings.search"],
            "senior_quant_agent":  ["tool.invoke:*"],  # wildcard within the agent
            "trading_agent":       ["tool.invoke:order.place"],  # REQUIRES HITL approval
            "compliance_agent":    ["tool.invoke:report.publish"],
        }

    def check(self, agent_id: str, action: str, resource: str) -> PermissionAction:
        """Check if the agent is permitted to perform the action on the resource.

        Returns:
            ALLOW: permission granted
            DENY: permission denied (no human override possible)
            REQUIRE_APPROVAL: permission requires human-in-the-loop approval

        Logic (in order):
        1. If the agent is not in the policy -> DENY
        2. If the agent has the action in perms:
           - If the action is high-stakes (order.place, account.transfer) -> REQUIRE_APPROVAL
           - Otherwise -> ALLOW
        3. If the agent does not have the action in perms:
           - If the action is high-stakes -> REQUIRE_APPROVAL (but the HITL prompt
             will reveal the agent has no permission, and the human can deny)
           - Otherwise -> DENY
        """
        perms = self._policy.get(agent_id, [])
        if not perms:
            return PermissionAction.DENY
        high_stakes = action in {"order.place", "account.transfer"}
        full_action = f"{action}:{resource}"
        if full_action in perms or any(p.endswith(":*") and p.split(":")[0] == action for p in perms):
            return PermissionAction.REQUIRE_APPROVAL if high_stakes else PermissionAction.ALLOW
        # Agent has perms but not for this action
        return PermissionAction.REQUIRE_APPROVAL if high_stakes else PermissionAction.DENY


class FailureRecovery:
    """L4 failure recovery. Implements rollback and compensating actions.

    For each agent action that has side effects, a compensating action
    can be registered. On failure, the recovery routine executes the
    compensations in reverse order (saga pattern).
    """

    @dataclass
    class Compensation:
        description: str
        action: Callable[[], None]

    def __init__(self):
        self._stack: list[FailureRecovery.Compensation] = []

    def push(self, description: str, action: Callable[[], None]) -> None:
        """Push a compensation onto the stack."""
        self._stack.append(self.Compensation(description=description, action=action))

    def rollback(self) -> list[str]:
        """Execute compensations in reverse order. Returns descriptions of executed steps."""
        executed = []
        while self._stack:
            comp = self._stack.pop()
            try:
                comp.action()
                executed.append(comp.description)
            except Exception as e:
                executed.append(f"FAILED: {comp.description} ({e})")
        return executed


class HITLCheckpoint:
    """Human-in-the-loop checkpoint. Production deployments integrate with
    Slack, PagerDuty, or a custom review queue. This reference prints to
    stdout."""

    def __init__(self):
        self._pending: list[dict[str, Any]] = []

    def request_approval(self, agent_id: str, action: str, resource: str, context: dict[str, Any]) -> bool:
        """Request human approval. In production, this would block on a review queue.

        Returns True if approved, False if denied. The reference implementation
        always approves (TODO: integrate with real review UI).
        """
        request = {
            "request_id":  str(uuid.uuid4()),
            "timestamp":   datetime.now(timezone.utc).isoformat(),
            "agent_id":    agent_id,
            "action":      action,
            "resource":    resource,
            "context":     context,
        }
        self._pending.append(request)
        # In production, send to Slack / PagerDuty and block on response
        print(f"[HITL] Approval requested: agent={agent_id} action={action} resource={resource}")
        return True  # default approval in reference implementation


class L4GovernanceLayer:
    """The L4 layer orchestrator. Composes PermissionGate, AuditLog,
    FailureRecovery, and HITLCheckpoint into a single governance interface.
    """

    def __init__(self):
        self.permissions = PermissionGate()
        self.audit = AuditLog()
        self.recovery = FailureRecovery()
        self.hitl = HITLCheckpoint()

    def authorize(self, agent_id: str, action: str, resource: str, rationale: str = "") -> PermissionAction:
        """Check permission and emit an audit entry. Always emits an entry,
        regardless of decision (DENY actions are also audited)."""
        decision = self.permissions.check(agent_id, action, resource)
        decision_str = decision.value
        if decision == PermissionAction.REQUIRE_APPROVAL:
            approved = self.hitl.request_approval(agent_id, action, resource, {"rationale": rationale})
            decision_str = "approved" if approved else "denied_after_hitl"
        self.audit.append(
            agent_id=agent_id,
            action=action,
            resource=resource,
            decision=decision_str,
            rationale=rationale,
        )
        return decision


if __name__ == "__main__":
    l4 = L4GovernanceLayer()

    # Example 1: junior agent reads market data (ALLOW)
    d = l4.authorize("junior_quant_agent", "tool.invoke", "market_data.fetch", rationale="daily check")
    print(f"junior reads market data: {d.value}")

    # Example 2: trading agent places order (REQUIRE_APPROVAL — high-stakes)
    d = l4.authorize("trading_agent", "order.place", "order.place", rationale="AAPL buy 100 shares @ market")
    print(f"trading places order: {d.value}")

    # Example 3: unknown agent tries to transfer funds (DENY — not in policy)
    d = l4.authorize("rogue_agent", "account.transfer", "account.transfer", rationale="")
    print(f"rogue transfers: {d.value}")

    # Verify audit chain
    is_valid, invalid = l4.audit.verify_chain()
    print(f"\nAudit chain: {'VALID' if is_valid else f'INVALID at {invalid}'}")
    print(f"Audit entries: {len(l4.audit.entries())}")
