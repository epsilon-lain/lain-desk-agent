"""Click Readiness Policy v0.2: strict non-executing click eligibility checks."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

from .observer import HIGH_RISK_LABELS, normalize_label_text

REQUIRED_CHECKS = [
    "action_contract exists",
    "action_contract.type is click",
    "action_contract.status is approved_for_execution and not preview_only",
    "action_contract.executed is false",
    "bbox is present",
    "bbox has valid x, y, width, height",
    "bbox is inside screen bounds when screen bounds are available",
    "center has valid x, y",
    "center matches bbox center",
    "click capability is enabled and executable",
    "permission profile allows click",
    "safety decision is not blocked",
    "target label is not high risk",
    "observation is fresh when timestamp is available",
]

DEFAULT_MAX_OBSERVATION_AGE_SECONDS = 10.0


def evaluate_click_readiness(
    action_contract: dict[str, Any] | None,
    safety_decision: dict[str, Any] | None,
    capability: dict[str, Any] | None,
    permission_profile: dict[str, Any] | str | None,
    screen: dict[str, Any] | None = None,
    observation_timestamp: str | None = None,
    now: datetime | None = None,
    max_observation_age_seconds: float = DEFAULT_MAX_OBSERVATION_AGE_SECONDS,
) -> dict[str, Any]:
    reasons: list[str] = []
    checks: list[dict[str, Any]] = []
    risk = _capability_risk(capability)

    if not isinstance(action_contract, dict):
        _add_check(checks, "action_contract_present", False, "missing action contract")
        return _blocked(["missing action contract"], risk=risk, checks=checks)

    if action_contract.get("type") != "click":
        return click_readiness_not_applicable("action contract is not click")

    _add_check(checks, "action_contract_present", True)
    _add_check(checks, "click_contract", True)

    status = str(action_contract.get("status") or "")
    if status == "preview_only":
        _block(checks, reasons, "contract_status", "preview-only contract")
    elif status != "approved_for_execution":
        _block(checks, reasons, "contract_status", "action contract is not approved_for_execution")
    else:
        _add_check(checks, "contract_status", True)

    if bool(action_contract.get("executed")):
        _block(checks, reasons, "not_executed", "action contract already executed")
    else:
        _add_check(checks, "not_executed", True)

    bbox_status, bbox = _bbox_status(action_contract.get("bbox"))
    if bbox_status == "missing":
        _block(checks, reasons, "bbox_present", "missing bbox")
        _add_check(checks, "bbox_shape", "not_applicable", "bbox is missing")
    elif bbox_status == "malformed":
        _add_check(checks, "bbox_present", True)
        _block(checks, reasons, "bbox_shape", "malformed bbox")
    else:
        _add_check(checks, "bbox_present", True)
        _add_check(checks, "bbox_shape", True)

    center = _normalized_point(action_contract.get("center"))
    if center is None:
        _block(checks, reasons, "center_shape", "invalid center")
    else:
        _add_check(checks, "center_shape", True)

    _check_center_matches_bbox(checks, reasons, bbox, center)
    _check_screen_bounds(checks, reasons, bbox, screen)

    _check_observation_freshness(
        checks,
        reasons,
        observation_timestamp,
        now,
        max_observation_age_seconds,
    )

    if not _capability_allows_click(capability):
        _block(checks, reasons, "click_capability", "click capability disabled")
    else:
        _add_check(checks, "click_capability", True)

    if not _permission_profile_allows_click(permission_profile):
        _block(checks, reasons, "permission_profile", "permission profile does not allow click")
    else:
        _add_check(checks, "permission_profile", True)

    if _safety_blocks(safety_decision):
        _block(checks, reasons, "safety_decision", "safety decision blocked")
    else:
        _add_check(checks, "safety_decision", True)

    if _has_high_risk_label(action_contract):
        _block(checks, reasons, "target_label_risk", "high-risk target label")
        risk = "high"
    else:
        _add_check(checks, "target_label_risk", True)

    if reasons:
        return _blocked(reasons, risk=risk, checks=checks)

    return {
        "ready": True,
        "status": "ready",
        "reasons": [],
        "risk": risk,
        "checks": checks,
    }


def click_readiness_not_applicable(reason: str = "") -> dict[str, Any]:
    checks = []
    if reason:
        _add_check(checks, "click_contract", "not_applicable", reason)

    return {
        "ready": False,
        "status": "not_applicable",
        "reasons": [],
        "risk": "none",
        "checks": checks,
    }


def click_readiness_metadata() -> dict[str, Any]:
    return {
        "enabled": False,
        "reason": "Real click execution is not enabled.",
        "required_checks": list(REQUIRED_CHECKS),
        "high_risk_labels": list(HIGH_RISK_LABELS),
        "max_observation_age_seconds": DEFAULT_MAX_OBSERVATION_AGE_SECONDS,
    }


def _blocked(reasons: list[str], risk: str, checks: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "ready": False,
        "status": "blocked",
        "reasons": reasons,
        "risk": risk,
        "checks": checks,
    }


def _block(checks: list[dict[str, Any]], reasons: list[str], name: str, reason: str) -> None:
    reasons.append(reason)
    _add_check(checks, name, False, reason)


def _add_check(
    checks: list[dict[str, Any]],
    name: str,
    passed: bool | str,
    reason: str = "",
) -> None:
    if passed is True:
        status = "passed"
    elif passed is False:
        status = "blocked"
    else:
        status = str(passed)

    check: dict[str, Any] = {
        "name": name,
        "status": status,
    }
    if reason:
        check["reason"] = reason

    checks.append(check)


def _bbox_status(value: Any) -> tuple[str, dict[str, float] | None]:
    if value is None:
        return "missing", None

    if not isinstance(value, dict):
        return "malformed", None

    try:
        bbox = {
            "x": float(value["x"]),
            "y": float(value["y"]),
            "width": float(value["width"]),
            "height": float(value["height"]),
        }
    except (KeyError, TypeError, ValueError):
        return "malformed", None

    if not all(math.isfinite(number) for number in bbox.values()) or bbox["width"] <= 0 or bbox["height"] <= 0:
        return "malformed", None

    return "valid", bbox


def _normalized_point(value: Any) -> dict[str, float] | None:
    if not isinstance(value, dict):
        return None

    try:
        point = {
            "x": float(value["x"]),
            "y": float(value["y"]),
        }
    except (KeyError, TypeError, ValueError):
        return None

    if not all(math.isfinite(number) for number in point.values()):
        return None

    return point


def _capability_allows_click(capability: dict[str, Any] | None) -> bool:
    if not isinstance(capability, dict):
        return False

    return bool(capability.get("enabled")) and bool(capability.get("executable"))


def _capability_risk(capability: dict[str, Any] | None) -> str:
    if not isinstance(capability, dict):
        return "unknown"

    return str(capability.get("risk") or "unknown")


def _check_screen_bounds(
    checks: list[dict[str, Any]],
    reasons: list[str],
    bbox: dict[str, float] | None,
    screen: dict[str, Any] | None,
) -> None:
    if bbox is None:
        _add_check(checks, "bbox_screen_bounds", "not_applicable", "bbox is unavailable")
        return

    bounds = _screen_bounds(screen)
    if bounds is None:
        _add_check(checks, "bbox_screen_bounds", "not_applicable", "screen bounds unavailable")
        return

    screen_width, screen_height = bounds
    in_bounds = (
        bbox["x"] >= 0
        and bbox["y"] >= 0
        and bbox["x"] + bbox["width"] <= screen_width
        and bbox["y"] + bbox["height"] <= screen_height
    )

    if not in_bounds:
        _block(checks, reasons, "bbox_screen_bounds", "bbox outside screen bounds")
        return

    _add_check(checks, "bbox_screen_bounds", True)


def _check_center_matches_bbox(
    checks: list[dict[str, Any]],
    reasons: list[str],
    bbox: dict[str, float] | None,
    center: dict[str, float] | None,
) -> None:
    if bbox is None or center is None:
        _add_check(checks, "center_bbox_consistency", "not_applicable", "bbox or center unavailable")
        return

    expected = {
        "x": round(bbox["x"] + bbox["width"] / 2),
        "y": round(bbox["y"] + bbox["height"] / 2),
    }
    actual = {
        "x": round(center["x"]),
        "y": round(center["y"]),
    }
    if actual != expected:
        _block(checks, reasons, "center_bbox_consistency", "center does not match bbox")
        return

    _add_check(checks, "center_bbox_consistency", True)


def _screen_bounds(screen: dict[str, Any] | None) -> tuple[float, float] | None:
    if not isinstance(screen, dict):
        return None

    try:
        width = float(screen["width"])
        height = float(screen["height"])
    except (KeyError, TypeError, ValueError):
        return None

    if not math.isfinite(width) or not math.isfinite(height) or width <= 0 or height <= 0:
        return None

    return width, height


def _check_observation_freshness(
    checks: list[dict[str, Any]],
    reasons: list[str],
    observation_timestamp: str | None,
    now: datetime | None,
    max_observation_age_seconds: float,
) -> None:
    if not observation_timestamp:
        _add_check(checks, "observation_freshness", "not_applicable", "observation timestamp unavailable")
        return

    observed_at = _parse_timestamp(observation_timestamp)
    if observed_at is None:
        _block(checks, reasons, "observation_freshness", "malformed observation timestamp")
        return

    current_time = now or datetime.now(timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)

    max_age = _positive_float(max_observation_age_seconds)
    age_seconds = max(0.0, (current_time - observed_at).total_seconds())
    if max_age is not None and age_seconds > max_age:
        _block(checks, reasons, "observation_freshness", "stale observation")
        return

    _add_check(checks, "observation_freshness", True)


def _parse_timestamp(value: str) -> datetime | None:
    if not isinstance(value, str):
        return None

    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    return timestamp


def _positive_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    return number if math.isfinite(number) and number > 0 else None


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
    risk_hint = str(action_contract.get("target_risk_hint") or "").strip().lower()
    if risk_hint in {"high", "high_risk"}:
        return True

    label = normalize_label_text(action_contract.get("target_label"))
    return any(normalize_label_text(high_risk_label) in label for high_risk_label in HIGH_RISK_LABELS)
