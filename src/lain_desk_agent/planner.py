"""Planner Proposal v0: create one conservative, non-executed action proposal."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProposedAction:
    type: str
    target: str
    parameters: dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    risk: str = "low"
    requires_approval: bool = False


@dataclass(frozen=True)
class Proposal:
    proposal_id: str
    source_ui_state_id: str
    action: ProposedAction

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def propose(ui_state: dict[str, Any]) -> dict[str, Any]:
    """Return a single deterministic next-action proposal without executing it."""

    ui_state_id = str(ui_state.get("ui_state_id") or "state_0001")
    state_guess = str(ui_state.get("state_guess") or "unknown")
    summary = str(ui_state.get("summary") or "")
    window_title = str(ui_state.get("window_title") or "")

    if state_guess == "browser_window" and _suggests_login(f"{window_title} {summary}"):
        action = ProposedAction(
            type="wait_for_user",
            target="current_window",
            reason=(
                "The current page appears to require login. "
                "The agent should not handle login."
            ),
            risk="high",
            requires_approval=True,
        )
    else:
        action = ProposedAction(
            type="no_op",
            target="current_window",
            reason="No reliable next action yet.",
            risk="low",
            requires_approval=False,
        )

    proposal = Proposal(
        proposal_id=_proposal_id_from_ui_state_id(ui_state_id),
        source_ui_state_id=ui_state_id,
        action=action,
    )

    return proposal.to_dict()


def _proposal_id_from_ui_state_id(ui_state_id: str) -> str:
    if ui_state_id.startswith("state_"):
        return f"proposal_{ui_state_id.removeprefix('state_')}"

    return "proposal_0001"


def _suggests_login(text: str) -> bool:
    haystack = text.lower()
    login_tokens = [
        "login",
        "log in",
        "sign in",
        "signin",
        "auth",
        "authentication",
        "password",
        "账户登录",
        "登录",
        "密码",
    ]

    return any(token in haystack for token in login_tokens)
