"""Compact context bundle for a future AI planner."""

from __future__ import annotations

from typing import Any

from .click_policy import HIGH_RISK_LABELS, click_readiness_metadata
from .execution_policy import ACTION_TYPES, execution_policy_summary
from .permission_profile import get_permission_profile_payload


MAX_VISIBLE_ELEMENTS = 20
MAX_VISIBLE_ELEMENT_TEXT_LENGTH = 80
MAX_VISIBLE_TEXT_PREVIEW = 8
MAX_VISIBLE_TEXT_LENGTH = 120
MAX_RECENT_EVENTS = 5


def build_planner_context(
    task: str,
    ui_state: dict[str, Any],
    runtime_status: dict[str, Any] | None = None,
    recent_events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a compact, read-only planner context without calling an LLM."""

    safe_ui_state = ui_state if isinstance(ui_state, dict) else {}
    safe_runtime_status = runtime_status if isinstance(runtime_status, dict) else _default_runtime_status()
    safe_recent_events = recent_events if isinstance(recent_events, list) else []

    return {
        "task": str(task or ""),
        "app_guess": _optional_string(safe_ui_state.get("app_guess")),
        "state_guess": str(safe_ui_state.get("state_guess") or "unknown"),
        "summary": str(safe_ui_state.get("summary") or ""),
        "confidence": _bounded_float(safe_ui_state.get("confidence")),
        "screen": _screen_size(safe_ui_state),
        "source_observation_id": str(safe_ui_state.get("source_observation_id") or ""),
        "visible_elements": _compact_visible_elements(safe_ui_state.get("visible_elements")),
        "visible_text": _compact_visible_text(safe_ui_state.get("visible_text")),
        "safety_runtime": _safety_runtime_summary(safe_runtime_status),
        "recent_events": _compact_recent_events(safe_recent_events),
        "limits": {
            "max_visible_elements": MAX_VISIBLE_ELEMENTS,
            "max_visible_text_preview": MAX_VISIBLE_TEXT_PREVIEW,
            "max_recent_events": MAX_RECENT_EVENTS,
        },
    }


def _default_runtime_status() -> dict[str, Any]:
    permission_payload = get_permission_profile_payload()
    click_readiness = click_readiness_metadata()
    return {
        "runtime": {
            "desktop_control": False,
        },
        "permission_profile": str(permission_payload.get("profile") or "unknown"),
        "execution_policy": execution_policy_summary(),
        "click_readiness": {
            "enabled": bool(click_readiness.get("enabled")),
            "reason": str(click_readiness.get("reason") or ""),
        },
    }


def _safety_runtime_summary(runtime_status: dict[str, Any]) -> dict[str, Any]:
    runtime = runtime_status.get("runtime")
    if not isinstance(runtime, dict):
        runtime = {}

    execution_policy = runtime_status.get("execution_policy")
    if not isinstance(execution_policy, dict):
        execution_policy = execution_policy_summary()

    click_readiness = runtime_status.get("click_readiness")
    if not isinstance(click_readiness, dict):
        click_readiness = {}

    executable_actions = [
        str(action)
        for action in execution_policy.get("executable_actions", [])
        if str(action) in ACTION_TYPES
    ]
    blocked_actions = [action for action in ACTION_TYPES if action not in executable_actions]

    return {
        "desktop_control": False,
        "permission_profile": str(
            runtime_status.get("permission_profile")
            or execution_policy.get("current_profile")
            or "unknown"
        ),
        "executable_actions": executable_actions,
        "blocked_actions": blocked_actions,
        "blocked_actions_count": len(blocked_actions),
        "click_readiness": {
            "enabled": bool(click_readiness.get("enabled", False)),
            "status": str(click_readiness.get("status") or ("enabled" if click_readiness.get("enabled") else "blocked")),
            "reason": str(click_readiness.get("reason") or ""),
        },
    }


def _compact_visible_elements(value: Any) -> dict[str, Any]:
    elements = value if isinstance(value, list) else []
    compact_items = []

    for index, element in enumerate(elements[:MAX_VISIBLE_ELEMENTS]):
        if not isinstance(element, dict):
            continue

        compact_items.append(_compact_visible_element(element, index))

    return {
        "count": len(elements),
        "items": compact_items,
        "truncated": len(elements) > MAX_VISIBLE_ELEMENTS,
        "summary": _visible_elements_summary(compact_items),
    }


def _compact_visible_element(element: dict[str, Any], index: int) -> dict[str, Any]:
    label = _element_label(element)
    text = _truncate_element_text(str(element.get("text") or label))
    raw_type = _short_text(_first_text(element, ["type", "kind", "role"]), 32)
    kind = _infer_element_kind(raw_type, label)
    source = _short_text(_first_text(element, ["source", "origin", "source_type"]) or "unknown", 32)

    return {
        "id": _stable_element_id(element, index),
        "type": raw_type or kind,
        "kind": kind,
        "label": label,
        "text": text,
        "bbox": _compact_bbox(element.get("bbox")),
        "confidence": _bounded_float(element.get("confidence")),
        "source": source,
        "risk_hint": _risk_hint_for_label(label),
    }


def _stable_element_id(element: dict[str, Any], index: int) -> str:
    element_id = _short_text(str(element.get("id") or "").strip(), 64)
    if element_id:
        return element_id

    return f"element_{index + 1:04d}"


def _element_label(element: dict[str, Any]) -> str:
    return _truncate_element_text(_first_text(element, ["label", "text", "name", "title", "value"]))


def _first_text(element: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        value = element.get(key)
        if value is None:
            continue

        text = " ".join(str(value).split())
        if text:
            return text

    return ""


def _infer_element_kind(raw_type: str, label: str) -> str:
    normalized_type = _normalized_text(raw_type)
    normalized_label = _normalized_text(label)

    if normalized_type in {"button", "link", "input", "textbox", "text", "menu", "checkbox"}:
        return normalized_type

    if normalized_type in {"edit", "textfield"}:
        return "input"

    if normalized_type in {"statictext", "label"}:
        return "text"

    if normalized_label in {"search", "find", "ok", "cancel", "done", "continue", "next", "back"}:
        return "button_like_text"

    return normalized_type or "unknown"


def _risk_hint_for_label(label: str) -> str:
    normalized_label = _normalized_text(label)
    if not normalized_label:
        return "none"

    for high_risk_label in HIGH_RISK_LABELS:
        normalized_risk = _normalized_text(high_risk_label)
        if normalized_risk and normalized_risk in normalized_label:
            return "high"

    return "none"


def _visible_elements_summary(items: list[dict[str, Any]]) -> dict[str, Any]:
    sources: dict[str, int] = {}
    risk_hints: dict[str, int] = {}

    for item in items:
        source = str(item.get("source") or "unknown")
        risk_hint = str(item.get("risk_hint") or "none")
        sources[source] = sources.get(source, 0) + 1
        risk_hints[risk_hint] = risk_hints.get(risk_hint, 0) + 1

    return {
        "item_count": len(items),
        "sources": sources,
        "risk_hints": risk_hints,
    }


def _compact_visible_text(value: Any) -> dict[str, Any]:
    texts = [str(text) for text in value] if isinstance(value, list) else []
    preview = [_truncate_text(text) for text in texts[:MAX_VISIBLE_TEXT_PREVIEW]]

    return {
        "count": len(texts),
        "preview": preview,
        "truncated": len(texts) > MAX_VISIBLE_TEXT_PREVIEW
        or any(len(text) > MAX_VISIBLE_TEXT_LENGTH for text in texts[:MAX_VISIBLE_TEXT_PREVIEW]),
    }


def _compact_recent_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    event_items = [
        _event_summary(event)
        for event in events[:MAX_RECENT_EVENTS]
        if isinstance(event, dict)
    ]

    return {
        "count": len(event_items),
        "items": event_items,
        "truncated": len(events) > MAX_RECENT_EVENTS,
    }


def _event_summary(event: dict[str, Any]) -> dict[str, str]:
    event_type = str(event.get("type") or "event")
    return {
        "type": event_type,
        "timestamp": str(event.get("timestamp") or ""),
        "summary": _event_summary_text(event, event_type),
    }


def _event_summary_text(event: dict[str, Any], event_type: str) -> str:
    if event_type == "observation.created":
        return _with_identifier("Observation captured", event.get("observation_id"))

    if event_type in {"proposal.approved", "proposal.rejected"}:
        return _with_identifier(event_type.replace(".", " "), event.get("proposal_id"))

    if event_type == "action_contract.created":
        return _with_identifier("Action contract created", event.get("action_contract_type"))

    if event_type in {"action.executed", "action.blocked", "action.verified", "action.verification_failed"}:
        return _with_identifier(event_type.replace(".", " "), event.get("action_contract_type"))

    if event_type == "snapshot.deleted":
        return _with_identifier("Snapshot deleted", event.get("observation_id"))

    return event_type


def _with_identifier(prefix: str, identifier: Any) -> str:
    value = str(identifier or "")
    return f"{prefix}: {value}" if value else prefix


def _screen_size(ui_state: dict[str, Any]) -> dict[str, int] | None:
    screen = ui_state.get("screen")
    if not isinstance(screen, dict):
        return None

    width = _positive_int(screen.get("width"))
    height = _positive_int(screen.get("height"))
    if width is None or height is None:
        return None

    return {"width": width, "height": height}


def _compact_bbox(value: Any) -> dict[str, int | float] | None:
    if not isinstance(value, dict):
        return None

    bbox: dict[str, int | float] = {}
    for key in ["x", "y", "width", "height"]:
        number = _finite_number(value.get(key))
        if number is None:
            return None
        bbox[key] = number

    if bbox["width"] <= 0 or bbox["height"] <= 0:
        return None

    return bbox


def _positive_int(value: Any) -> int | None:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None

    return number if number > 0 else None


def _bounded_float(value: Any) -> float:
    number = _finite_number(value)
    if number is None:
        return 0.0

    return max(0.0, min(float(number), 1.0))


def _finite_number(value: Any) -> int | float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if number != number or number in {float("inf"), float("-inf")}:
        return None

    return int(number) if number.is_integer() else number


def _truncate_text(text: str) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= MAX_VISIBLE_TEXT_LENGTH:
        return normalized

    return f"{normalized[: MAX_VISIBLE_TEXT_LENGTH - 3]}..."


def _truncate_element_text(text: str) -> str:
    return _short_text(text, MAX_VISIBLE_ELEMENT_TEXT_LENGTH)


def _short_text(text: str, max_length: int) -> str:
    normalized = " ".join(str(text or "").split())
    if len(normalized) <= max_length:
        return normalized

    return f"{normalized[: max(0, max_length - 3)]}..."


def _normalized_text(text: str) -> str:
    return " ".join(str(text or "").casefold().split())


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None

    return str(value)
