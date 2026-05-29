"""Click Readiness Policy v0: strict non-executing click eligibility checks."""

from __future__ import annotations

import math
from typing import Any


HIGH_RISK_LABELS = [
    "send",
    "submit",
    "delete",
    "remove",
    "pay",
    "purchase",
    "buy",
    "confirm",
    "password",
    "login",
    "sign in",
    "log in",
    "发送",
    "删除",
    "支付",
    "购买",
    "确认",
    "密码",
    "登录",
]

REQUIRED_CHECKS = [
    "action_contract exists",
    "action_contract.type is click",
    "action_contract.status is approved_for_execution",
    "action_contract.executed is false",
    "bbox has valid x, y, width, height",
    "center has valid x, y",
    "click capability is enabled and executable",
    "permission profile allows click",
    "safety decision is not blocked",
    "target label is not high risk",
]


def evaluate_click_readiness(
    action_contract: dict[str, Any] | None,
    safety_decision: dict[str, Any] | None,
    capability: dict[str, Any] | None,
    permission_profile: dict[str, Any] | str | None,
) -> dict[str, Any]:
    reasons: list[str] = []
    risk = _capability_risk(capability)

    if not isinstance(action_contract, dict):
        return _blocked(["missing action contract"], risk=risk)

    if action_contract.get("type") != "click":
        reasons.append("not a click action")

    status = str(action_contract.get("status") or "")
    if status == "preview_only":
        reasons.append("preview-only contract")
    elif status != "approved_for_execution":
        reasons.append("action contract is not approved_for_execution")

    if bool(action_contract.get("executed")):
        reasons.append("action contract already executed")

    if not _valid_bbox(action_contract.get("bbox")):
        reasons.append("invalid bbox")

    if not _valid_point(action_contract.get("center")):
        reasons.append("invalid center")

    if not _capability_allows_click(capability):
        reasons.append("click capability disabled")

    if not _permission_profile_allows_click(permission_profile):
        reasons.append("permission profile does not allow click")

    if _safety_blocks(safety_decision):
        reasons.append("safety decision blocked")

    if _has_high_risk_label(action_contract):
        reasons.append("high-risk target label")
        risk = "high"

    if reasons:
        return _blocked(reasons, risk=risk)

    return {
        "ready": True,
        "status": "ready",
        "reasons": [],
        "risk": risk,
    }


def click_readiness_not_applicable() -> dict[str, Any]:
    return {
        "ready": False,
        "status": "not_applicable",
        "reasons": [],
        "risk": "none",
    }


def click_readiness_metadata() -> dict[str, Any]:
    return {
        "enabled": False,
        "reason": "Real click execution is not enabled.",
        "required_checks": list(REQUIRED_CHECKS),
        "high_risk_labels": list(HIGH_RISK_LABELS),
    }


def _blocked(reasons: list[str], risk: str) -> dict[str, Any]:
    return {
        "ready": False,
        "status": "blocked",
        "reasons": reasons,
        "risk": risk,
    }


def _valid_bbox(value: Any) -> bool:
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


def _valid_point(value: Any) -> bool:
    if not isinstance(value, dict):
        return False

    try:
        x = float(value["x"])
        y = float(value["y"])
    except (KeyError, TypeError, ValueError):
        return False

    return math.isfinite(x) and math.isfinite(y)


def _capability_allows_click(capability: dict[str, Any] | None) -> bool:
    if not isinstance(capability, dict):
        return False

    return bool(capability.get("enabled")) and bool(capability.get("executable"))


def _capability_risk(capability: dict[str, Any] | None) -> str:
    if not isinstance(capability, dict):
        return "unknown"

    return str(capability.get("risk") or "unknown")


def _permission_profile_allows_click(permission_profile: dict[str, Any] | str | None) -> bool:
    if isinstance(permission_profile, dict):
        profile_name = str(permission_profile.get("profile") or "")
        profiles = permission_profile.get("profiles")

        if not isinstance(profiles, dict):
            return False

        profile_config = profiles.get(profile_name)
        if not isinstance(profile_config, dict):
            return False

        allowed_actions = profile_config.get("allowed_actions")
        if not isinstance(allowed_actions, list):
            return False

        return "click" in allowed_actions

    return False


def _safety_blocks(safety_decision: dict[str, Any] | None) -> bool:
    if not isinstance(safety_decision, dict):
        return False

    return safety_decision.get("decision") == "blocked"


def _has_high_risk_label(action_contract: dict[str, Any]) -> bool:
    label = _normalized_label_text(action_contract.get("target_label"))
    return any(_normalized_label_text(high_risk_label) in label for high_risk_label in HIGH_RISK_LABELS)


def _normalized_label_text(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())
