"""AI Planner test harness v0 using local mock outputs only."""

from __future__ import annotations

import json
import math
from typing import Any


ALLOWED_PROPOSAL_ACTION_TYPES = ["no_op", "target_hint", "switch_app_hint"]
BLOCKED_EXECUTABLE_ACTION_TYPES = {
    "click",
    "double_click",
    "type",
    "type_text",
    "hotkey",
    "press",
    "scroll",
    "send",
    "delete",
    "submit",
    "launch_app",
    "switch_app",
}
MAX_REASON_LENGTH = 240


def build_ai_planner_prompt_or_payload(planner_context: dict[str, Any]) -> dict[str, Any]:
    """Return the compact input a future AI planner would receive."""

    context = planner_context if isinstance(planner_context, dict) else {}
    return {
        "planner": {
            "mode": "test_harness_only",
            "external_llm_calls": False,
        },
        "task": str(context.get("task") or ""),
        "app_guess": _optional_string(context.get("app_guess")),
        "state_guess": str(context.get("state_guess") or "unknown"),
        "summary": str(context.get("summary") or ""),
        "visible_elements": _compact_visible_elements(context),
        "safety_runtime": _compact_safety_runtime(context),
        "recent_events": _compact_recent_events(context),
        "allowed_proposal_action_types": list(ALLOWED_PROPOSAL_ACTION_TYPES),
    }


def validate_ai_proposal(raw_output: Any, planner_context: dict[str, Any]) -> dict[str, Any]:
    """Validate a mock AI output and normalize it into a read-only proposal action."""

    parsed_output, parse_error = _parse_raw_output(raw_output)
    if parse_error:
        return _invalid(parse_error)

    action = _extract_action(parsed_output)
    if not isinstance(action, dict):
        return _invalid("Mock output must contain a structured action object.")

    action_type = _normalized_action_type(action.get("type") or action.get("action_type"))
    if not action_type:
        return _invalid("Mock output action is missing type.")

    if action_type in BLOCKED_EXECUTABLE_ACTION_TYPES:
        return _invalid(
            f"Executable action type '{action_type}' is not allowed in the AI planner harness."
        )

    if action_type not in ALLOWED_PROPOSAL_ACTION_TYPES:
        return _invalid(f"Unsupported proposal action type '{action_type}'.")

    if action_type == "no_op":
        return _valid(_no_op_action(_reason(action, "Mock AI planner selected no_op.")))

    if action_type == "target_hint":
        return _validate_target_hint(action, planner_context)

    return _validate_switch_app_hint(action, planner_context)


def build_ai_proposal_from_context(
    planner_context: dict[str, Any],
    mock_output: Any | None = None,
) -> dict[str, Any]:
    """Build a normal proposal from planner context and a validated mock output."""

    context = planner_context if isinstance(planner_context, dict) else {}
    raw_output = mock_output if mock_output is not None else _deterministic_mock_output(context)
    validation = validate_ai_proposal(raw_output, context)
    action = validation["action"] if validation["valid"] else _no_op_action(validation["reason"])

    return {
        "proposal_id": _proposal_id_from_context(context),
        "source_ui_state_id": _source_ui_state_id_from_context(context),
        "action": action,
    }


def _parse_raw_output(raw_output: Any) -> tuple[dict[str, Any] | None, str | None]:
    if isinstance(raw_output, dict):
        return raw_output, None

    if isinstance(raw_output, str):
        try:
            parsed = json.loads(raw_output)
        except json.JSONDecodeError:
            return None, "Mock output is not valid JSON."

        if isinstance(parsed, dict):
            return parsed, None

        return None, "Mock output JSON must decode to an object."

    return None, "Mock output must be a JSON object or dict."


def _extract_action(parsed_output: dict[str, Any]) -> dict[str, Any] | None:
    nested_action = parsed_output.get("action")
    if nested_action is None and ("type" in parsed_output or "action_type" in parsed_output):
        return parsed_output

    return nested_action if isinstance(nested_action, dict) else None


def _validate_target_hint(
    action: dict[str, Any],
    planner_context: dict[str, Any],
) -> dict[str, Any]:
    target_element_id = str(action.get("target_element_id") or "").strip()
    if not target_element_id:
        return _invalid("target_hint requires target_element_id.")

    element = _visible_element_by_id(planner_context).get(target_element_id)
    if element is None:
        return _invalid(f"target_element_id '{target_element_id}' is not present in planner_context.")

    bbox = element.get("bbox")
    if not _has_valid_bbox(bbox):
        return _invalid(f"target_element_id '{target_element_id}' does not have a valid bbox.")

    return _valid(
        {
            "type": "target_hint",
            "target": target_element_id,
            "target_element_id": target_element_id,
            "target_label": str(element.get("label") or ""),
            "target_bbox": bbox,
            "parameters": {},
            "reason": _reason(
                action,
                f"Mock AI planner selected visible element '{target_element_id}'.",
            ),
            "risk": "low",
            "requires_approval": False,
        }
    )


def _validate_switch_app_hint(
    action: dict[str, Any],
    planner_context: dict[str, Any],
) -> dict[str, Any]:
    target_app = str(action.get("target") or action.get("target_app") or "").strip()
    if not target_app:
        return _invalid("switch_app_hint requires target or target_app.")

    return _valid(
        {
            "type": "switch_app_hint",
            "target": target_app,
            "parameters": {
                "current_app": str(planner_context.get("app_guess") or "unknown"),
            },
            "reason": _reason(action, f"Mock AI planner suggested switching to {target_app}."),
            "risk": "low",
            "requires_approval": False,
        }
    )


def _deterministic_mock_output(planner_context: dict[str, Any]) -> dict[str, Any]:
    task = str(planner_context.get("task") or "")
    task_tokens = _tokens(task)
    target_app = _target_app_from_task(task)
    app_guess = str(planner_context.get("app_guess") or "unknown")

    if target_app and _canonical_app_name(app_guess) != target_app:
        return {
            "type": "switch_app_hint",
            "target": target_app,
            "reason": f"The task mentions {target_app}, but the active app appears to be {app_guess}.",
        }

    if task_tokens:
        for element in _visible_element_items(planner_context):
            if _tokens(str(element.get("label") or "")) & task_tokens:
                return {
                    "type": "target_hint",
                    "target_element_id": str(element.get("id") or ""),
                    "reason": "The mock planner found a visible element matching the task text.",
                }

    return {
        "type": "no_op",
        "reason": "No mock AI output was supplied and no deterministic target was found.",
    }


def _compact_visible_elements(planner_context: dict[str, Any]) -> dict[str, Any]:
    visible_elements = planner_context.get("visible_elements")
    if not isinstance(visible_elements, dict):
        return {"count": 0, "items": [], "truncated": False}

    items = [
        {
            "id": str(element.get("id") or ""),
            "type": str(element.get("type") or ""),
            "label": str(element.get("label") or ""),
            "bbox": element.get("bbox") if isinstance(element.get("bbox"), dict) else None,
            "confidence": _bounded_float(element.get("confidence")),
        }
        for element in _visible_element_items(planner_context)
    ]

    return {
        "count": _safe_int(visible_elements.get("count"), len(items)),
        "items": items,
        "truncated": bool(visible_elements.get("truncated", False)),
    }


def _compact_safety_runtime(planner_context: dict[str, Any]) -> dict[str, Any]:
    safety_runtime = planner_context.get("safety_runtime")
    if not isinstance(safety_runtime, dict):
        return {
            "desktop_control": False,
            "permission_profile": "unknown",
            "executable_actions": [],
            "blocked_actions": [],
            "blocked_actions_count": 0,
        }

    executable_actions = _string_list(safety_runtime.get("executable_actions"))
    blocked_actions = _string_list(safety_runtime.get("blocked_actions"))
    return {
        "desktop_control": False,
        "permission_profile": str(safety_runtime.get("permission_profile") or "unknown"),
        "executable_actions": executable_actions,
        "blocked_actions": blocked_actions,
        "blocked_actions_count": _safe_int(
            safety_runtime.get("blocked_actions_count"),
            len(blocked_actions),
        ),
        "click_readiness": _compact_click_readiness(safety_runtime.get("click_readiness")),
    }


def _compact_recent_events(planner_context: dict[str, Any]) -> dict[str, Any]:
    recent_events = planner_context.get("recent_events")
    if not isinstance(recent_events, dict):
        return {"count": 0, "items": [], "truncated": False}

    items = [
        {
            "type": str(event.get("type") or ""),
            "timestamp": str(event.get("timestamp") or ""),
            "summary": str(event.get("summary") or ""),
        }
        for event in recent_events.get("items", [])
        if isinstance(event, dict)
    ]
    return {
        "count": _safe_int(recent_events.get("count"), len(items)),
        "items": items,
        "truncated": bool(recent_events.get("truncated", False)),
    }


def _compact_click_readiness(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {
            "enabled": False,
            "status": "blocked",
            "reason": "",
        }

    return {
        "enabled": bool(value.get("enabled", False)),
        "status": str(value.get("status") or ("enabled" if value.get("enabled") else "blocked")),
        "reason": str(value.get("reason") or ""),
    }


def _visible_element_by_id(planner_context: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(element.get("id") or ""): element
        for element in _visible_element_items(planner_context)
        if str(element.get("id") or "")
    }


def _visible_element_items(planner_context: dict[str, Any]) -> list[dict[str, Any]]:
    visible_elements = planner_context.get("visible_elements")
    if not isinstance(visible_elements, dict):
        return []

    items = visible_elements.get("items")
    if not isinstance(items, list):
        return []

    return [element for element in items if isinstance(element, dict)]


def _has_valid_bbox(value: Any) -> bool:
    if not isinstance(value, dict):
        return False

    try:
        x = float(value["x"])
        y = float(value["y"])
        width = float(value["width"])
        height = float(value["height"])
    except (KeyError, TypeError, ValueError):
        return False

    return all(math.isfinite(number) for number in [x, y, width, height]) and width > 0 and height > 0


def _proposal_id_from_context(planner_context: dict[str, Any]) -> str:
    source_ui_state_id = _source_ui_state_id_from_context(planner_context)
    if source_ui_state_id.startswith("state_"):
        return f"proposal_ai_{source_ui_state_id.removeprefix('state_')}"

    return "proposal_ai_0001"


def _source_ui_state_id_from_context(planner_context: dict[str, Any]) -> str:
    source_observation_id = str(planner_context.get("source_observation_id") or "").strip()
    if source_observation_id.startswith("obs_"):
        return f"state_{source_observation_id.removeprefix('obs_')}"

    if source_observation_id:
        return f"state_{_safe_identifier(source_observation_id)}"

    return "state_ai_context"


def _safe_identifier(value: str) -> str:
    identifier = "".join(character.lower() if character.isalnum() else "_" for character in value)
    return "_".join(part for part in identifier.split("_") if part) or "ai_context"


def _valid(action: dict[str, Any]) -> dict[str, Any]:
    return {
        "valid": True,
        "reason": "accepted",
        "action": action,
    }


def _invalid(reason: str) -> dict[str, Any]:
    return {
        "valid": False,
        "reason": reason,
        "action": _no_op_action(reason),
    }


def _no_op_action(reason: str) -> dict[str, Any]:
    return {
        "type": "no_op",
        "target": "current_window",
        "parameters": {},
        "reason": _truncate_reason(reason),
        "risk": "low",
        "requires_approval": False,
    }


def _reason(action: dict[str, Any], fallback: str) -> str:
    raw_reason = str(action.get("reason") or "").strip()
    return _truncate_reason(raw_reason or fallback)


def _truncate_reason(reason: str) -> str:
    normalized = " ".join(str(reason or "").split())
    if len(normalized) <= MAX_REASON_LENGTH:
        return normalized

    return f"{normalized[: MAX_REASON_LENGTH - 3]}..."


def _normalized_action_type(value: Any) -> str:
    return str(value or "").strip().lower()


def _tokens(text: str) -> set[str]:
    normalized = "".join(character.lower() if character.isalnum() else " " for character in text)
    return {token for token in normalized.split() if len(token) >= 2}


def _target_app_from_task(task: str) -> str | None:
    normalized = " ".join(
        "".join(character.lower() if character.isalnum() else " " for character in task).split()
    )
    tokens = set(normalized.split())

    if "微信" in task or tokens & {"wechat", "weixin"}:
        return "WeChat"

    if tokens & {"chrome", "browser"}:
        return "Chrome"

    return None


def _canonical_app_name(app_name: str) -> str:
    tokens = _tokens(app_name)
    if "wechat" in tokens or "weixin" in tokens:
        return "WeChat"

    if "chrome" in tokens:
        return "Chrome"

    return app_name


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    return [str(item) for item in value]


def _safe_int(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _bounded_float(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0

    if number != number or number in {float("inf"), float("-inf")}:
        return 0.0

    return max(0.0, min(number, 1.0))


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None

    return str(value)
