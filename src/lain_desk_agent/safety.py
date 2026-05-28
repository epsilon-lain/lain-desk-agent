"""Safety Gate v0: classify a proposal before any actuation exists."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class SafetyDecision:
    decision: str
    reason: str
    risk: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def assess_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    """Return allowed, needs_approval, or blocked for a proposal."""

    action = proposal.get("action") if isinstance(proposal, dict) else None
    if not isinstance(action, dict):
        return SafetyDecision(
            decision="blocked",
            reason="Proposal is missing a structured action.",
            risk="high",
        ).to_dict()

    action_type = str(action.get("type") or "unknown")
    risk = str(action.get("risk") or "unknown")
    requires_approval = bool(action.get("requires_approval"))

    if action_type in _BLOCKED_ACTION_TYPES:
        return SafetyDecision(
            decision="blocked",
            reason="Executable input actions are outside the current read-only phase.",
            risk=_highest_risk(risk, "high"),
        ).to_dict()

    if requires_approval or risk in {"medium", "high"}:
        return SafetyDecision(
            decision="needs_approval",
            reason="The proposal is marked as risky or approval-gated.",
            risk=_highest_risk(risk, "medium"),
        ).to_dict()

    if action_type in _ALLOWED_READ_ONLY_ACTION_TYPES:
        return SafetyDecision(
            decision="allowed",
            reason="This proposal is read-only and does not execute desktop input.",
            risk="low",
        ).to_dict()

    return SafetyDecision(
        decision="blocked",
        reason=f"Unknown proposal type '{action_type}' is not allowed by Safety Gate v0.",
        risk=_highest_risk(risk, "medium"),
    ).to_dict()


def _highest_risk(left: str, right: str) -> str:
    order = {"low": 0, "medium": 1, "high": 2}
    return left if order.get(left, 1) >= order.get(right, 1) else right


_ALLOWED_READ_ONLY_ACTION_TYPES = {
    "no_op",
    "switch_app_hint",
    "target_hint",
}

_BLOCKED_ACTION_TYPES = {
    "click",
    "double_click",
    "type",
    "type_text",
    "hotkey",
    "press",
    "scroll",
    "submit",
    "send",
    "delete",
}
