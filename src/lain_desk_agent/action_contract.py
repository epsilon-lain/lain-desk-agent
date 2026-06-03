"""Preview-only action contracts for future actuation."""

from __future__ import annotations

import math
from typing import Any


ACTION_ID = "action_0001"


def action_contract_from_proposal(proposal: dict[str, Any]) -> dict[str, Any] | None:
    """Convert a read-only proposal into a preview-only action contract."""

    action = proposal.get("action")
    if not isinstance(action, dict):
        return None

    action_type = action.get("type")

    if action_type == "target_hint":
        return _click_contract(proposal, action)

    if action_type == "switch_app_hint":
        return _switch_app_contract(proposal, action)

    return None


def _click_contract(proposal: dict[str, Any], action: dict[str, Any]) -> dict[str, Any] | None:
    bbox = _normalized_bbox(action.get("target_bbox"))
    if bbox is None:
        return None

    return {
        "action_id": ACTION_ID,
        "source_proposal_id": str(proposal.get("proposal_id") or ""),
        "type": "click",
        "target_element_id": str(action.get("target_element_id") or ""),
        "target_label": str(action.get("target_label") or ""),
        "target_role": str(action.get("target_role") or ""),
        "target_confidence": action.get("target_confidence"),
        "target_source": str(action.get("target_source") or ""),
        "target_risk_hint": str(action.get("target_risk_hint") or ""),
        "target_timestamp": str(action.get("target_timestamp") or ""),
        "bbox": bbox,
        "center": {
            "x": round(bbox["x"] + bbox["width"] / 2),
            "y": round(bbox["y"] + bbox["height"] / 2),
        },
        "status": "preview_only",
        "executed": False,
    }


def _switch_app_contract(proposal: dict[str, Any], action: dict[str, Any]) -> dict[str, Any]:
    parameters = action.get("parameters")
    if not isinstance(parameters, dict):
        parameters = {}

    return {
        "action_id": ACTION_ID,
        "source_proposal_id": str(proposal.get("proposal_id") or ""),
        "type": "switch_app",
        "target_app": str(action.get("target") or ""),
        "parameters": {
            "current_app": str(parameters.get("current_app") or ""),
        },
        "status": "preview_only",
        "executed": False,
    }


def _normalized_bbox(value: Any) -> dict[str, float] | None:
    if not isinstance(value, dict):
        return None

    try:
        bbox = {
            "x": float(value["x"]),
            "y": float(value["y"]),
            "width": float(value["width"]),
            "height": float(value["height"]),
        }
    except (KeyError, TypeError, ValueError):
        return None

    if not all(math.isfinite(number) for number in bbox.values()):
        return None

    if bbox["width"] <= 0 or bbox["height"] <= 0:
        return None

    return {key: _compact_number(number) for key, number in bbox.items()}


def _compact_number(value: float) -> float | int:
    return int(value) if value.is_integer() else value
