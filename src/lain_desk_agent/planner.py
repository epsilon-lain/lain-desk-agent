"""Planner Proposal v1: create one conservative, non-executed proposal."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProposedAction:
    type: str
    target: str = "current_window"
    target_element_id: str | None = None
    target_label: str | None = None
    target_bbox: dict[str, Any] | None = None
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
    app_guess = str(ui_state.get("app_guess") or "unknown")
    state_guess = str(ui_state.get("state_guess") or "unknown")
    summary = str(ui_state.get("summary") or "")
    window_title = str(ui_state.get("window_title") or "")
    visible_text = " ".join(str(text) for text in ui_state.get("visible_text") or [])
    task = str(ui_state.get("task") or ui_state.get("goal") or "")
    visible_elements = _visible_elements(ui_state)
    target_app = _target_app_from_task(task)

    if target_app and not _app_matches(app_guess, target_app):
        action = ProposedAction(
            type="switch_app_hint",
            target=target_app,
            parameters={
                "current_app": app_guess,
            },
            reason=(
                f"The task mentions {target_app}, but the active window appears to be "
                f"{app_guess}. Switch to {target_app} before planning the next step."
            ),
            risk="low",
            requires_approval=False,
        )
    elif state_guess == "browser_window" and _suggests_login(
        f"{window_title} {summary} {visible_text}"
    ):
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
    elif visible_elements:
        target = _select_target_element(visible_elements, task)
        if target:
            action = ProposedAction(
                type="target_hint",
                target=str(target.get("id") or "unknown"),
                target_element_id=str(target.get("id") or ""),
                target_label=str(target.get("label") or ""),
                target_bbox=target.get("bbox") if isinstance(target.get("bbox"), dict) else {},
                parameters={},
                reason=_target_hint_reason(target, task),
                risk="low",
                requires_approval=False,
            )
        else:
            action = ProposedAction(
                type="no_op",
                target="current_window",
                reason="Visible elements exist, but none are reliable enough to target.",
                risk="low",
                requires_approval=False,
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


def _target_app_from_task(task: str) -> str | None:
    normalized = _normalized_task_text(task)
    tokens = set(normalized.split())

    if "微信" in task or tokens & {"wechat", "weixin"}:
        return "WeChat"

    if tokens & {"chrome", "browser"}:
        return "Chrome"

    if "vs code" in normalized or tokens & {"vscode", "code"}:
        return "VS Code"

    if "notepad" in tokens:
        return "Notepad"

    if tokens & {"powershell", "terminal"}:
        return "PowerShell"

    return None


def _app_matches(app_guess: str, target_app: str) -> bool:
    return _canonical_app_name(app_guess) == target_app


def _canonical_app_name(app_name: str) -> str:
    normalized = _normalized_task_text(app_name)
    tokens = set(normalized.split())

    if "wechat" in tokens or "weixin" in tokens:
        return "WeChat"

    if "chrome" in tokens:
        return "Chrome"

    if "vs code" in normalized or "vscode" in tokens or "code" in tokens:
        return "VS Code"

    if "notepad" in tokens:
        return "Notepad"

    if "powershell" in tokens or "terminal" in tokens:
        return "PowerShell"

    return app_name


def _normalized_task_text(text: str) -> str:
    return " ".join("".join(character.lower() if character.isalnum() else " " for character in text).split())


def _visible_elements(ui_state: dict[str, Any]) -> list[dict[str, Any]]:
    elements = ui_state.get("visible_elements")
    if not isinstance(elements, list):
        return []

    return [element for element in elements if isinstance(element, dict)]


def _select_target_element(
    visible_elements: list[dict[str, Any]],
    task: str,
) -> dict[str, Any] | None:
    candidates = [
        element
        for element in visible_elements
        if _has_element_id(element)
        and _has_visible_label(element)
        and _element_confidence(element) >= 0.45
    ]

    if not candidates:
        return None

    task_tokens = _tokens(task)
    if task_tokens:
        scored = [
            (_task_match_score(element, task_tokens), _element_confidence(element), element)
            for element in candidates
        ]
        scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
        if scored[0][0] > 0:
            return scored[0][2]

        return None

    general_targets = [
        element
        for element in candidates
        if _normalized_label(element) in _GENERAL_TARGET_LABELS
    ]
    if general_targets:
        return max(general_targets, key=_element_confidence)

    return None


def _target_hint_reason(element: dict[str, Any], task: str) -> str:
    label = str(element.get("label") or "")

    if task.strip():
        return (
            f"The task mentions text similar to '{label}', and visible_elements "
            "contains a matching read-only element."
        )

    return (
        f"visible_elements contains a conservative target candidate labeled '{label}'. "
        "This is only a target hint, not an executable action."
    )


def _has_element_id(element: dict[str, Any]) -> bool:
    return bool(str(element.get("id") or "").strip())


def _has_visible_label(element: dict[str, Any]) -> bool:
    return bool(str(element.get("label") or "").strip())


def _element_confidence(element: dict[str, Any]) -> float:
    try:
        confidence = float(element.get("confidence", 0.0))
    except (TypeError, ValueError):
        return 0.0

    return max(0.0, min(confidence, 1.0))


def _task_match_score(element: dict[str, Any], task_tokens: set[str]) -> int:
    return len(_tokens(str(element.get("label") or "")) & task_tokens)


def _tokens(text: str) -> set[str]:
    normalized = "".join(character.lower() if character.isalnum() else " " for character in text)
    return {token for token in normalized.split() if len(token) >= 2}


def _normalized_label(element: dict[str, Any]) -> str:
    return " ".join(str(element.get("label") or "").lower().split())


_GENERAL_TARGET_LABELS = {
    "search",
    "find",
    "ok",
    "done",
    "continue",
    "next",
    "back",
    "open",
    "new",
    "save",
    "cancel",
}
