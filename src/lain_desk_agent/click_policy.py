"""Click Readiness Policy v0.3: strict non-executing click eligibility checks."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

from .observer import HIGH_RISK_LABELS, normalize_label_text

REQUIRED_CHECKS = [
    "action_contract exists",
    "action_contract.type is click",
    "target element is identified",
    "target confidence is high enough",
    "target risk is known and not approval-gated",
    "target is not hidden or disabled",
    "target selection is not ambiguous when candidates are provided",
    "action_contract.status is approved_for_execution and not preview_only",
    "action_contract.executed is false",
    "bbox is present",
    "bbox has valid x, y, width, height",
    "bbox is inside declared viewport bounds",
    "coordinate space is known",
    "DPI or scale metadata is known",
    "center has valid x, y",
    "center matches bbox center",
    "click capability is enabled and executable",
    "permission profile allows click",
    "safety decision is not blocked",
    "observation is fresh when timestamp is available",
]

DEFAULT_MAX_OBSERVATION_AGE_SECONDS = 10.0
MIN_READY_TARGET_CONFIDENCE = 0.45
KNOWN_COORDINATE_SPACES = {"screen", "viewport", "desktop"}


def evaluate_click_readiness(
    action_contract: dict[str, Any] | None,
    safety_decision: dict[str, Any] | None,
    capability: dict[str, Any] | None,
    permission_profile: dict[str, Any] | str | None,
    screen: dict[str, Any] | None = None,
    observation_timestamp: str | None = None,
    now: datetime | None = None,
    max_observation_age_seconds: float = DEFAULT_MAX_OBSERVATION_AGE_SECONDS,
    visible_elements: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return theoretical click readiness diagnostics without executing input."""

    reasons: list[str] = []
    blockers: list[dict[str, str]] = []
    checks: list[dict[str, Any]] = []
    risk = _capability_risk(capability)

    if not isinstance(action_contract, dict):
        _block(
            checks,
            reasons,
            blockers,
            "action_contract_present",
            "missing_target",
            "missing action contract",
        )
        return _blocked(
            reasons,
            risk=risk,
            checks=checks,
            blockers=blockers,
            target_debug={},
            coordinate_debug={},
        )

    if action_contract.get("type") != "click":
        return click_readiness_not_applicable("action contract is not click")

    _add_check(checks, "action_contract_present", True)
    _add_check(checks, "click_contract", True)

    target_debug = _target_debug(action_contract)
    coordinate_debug: dict[str, Any] = {
        "screen": _screen_debug(screen),
        "bbox": None,
        "center": None,
        "expected_center": None,
    }

    _check_target_present(checks, reasons, blockers, action_contract)
    _check_target_confidence(checks, reasons, blockers, action_contract)
    _check_hidden_or_disabled_target(checks, reasons, blockers, action_contract)
    _check_ambiguous_target(
        checks,
        reasons,
        blockers,
        action_contract,
        visible_elements,
    )

    status = str(action_contract.get("status") or "")
    if status == "preview_only":
        _block(
            checks,
            reasons,
            blockers,
            "contract_status",
            "preview_only_contract",
            "preview-only contract",
        )
    elif status != "approved_for_execution":
        _block(
            checks,
            reasons,
            blockers,
            "contract_status",
            "action_not_enabled_by_policy",
            "action contract is not approved_for_execution",
        )
    else:
        _add_check(checks, "contract_status", True)

    if bool(action_contract.get("executed")):
        _block(
            checks,
            reasons,
            blockers,
            "not_executed",
            "action_already_executed",
            "action contract already executed",
        )
    else:
        _add_check(checks, "not_executed", True)

    bbox_status, bbox = _bbox_status(action_contract.get("bbox"))
    coordinate_debug["bbox"] = bbox if bbox is not None else action_contract.get("bbox")
    if bbox_status == "missing":
        _block(checks, reasons, blockers, "bbox_present", "missing_bbox", "missing bbox")
        _add_check(checks, "bbox_shape", "not_applicable", "bbox is missing")
    elif bbox_status == "malformed":
        _add_check(checks, "bbox_present", True)
        _block(checks, reasons, blockers, "bbox_shape", "invalid_bbox", "malformed bbox")
    else:
        _add_check(checks, "bbox_present", True)
        _add_check(checks, "bbox_shape", True)

    center_status, center = _center_status(action_contract.get("center"))
    coordinate_debug["center"] = center if center is not None else action_contract.get("center")
    if center_status == "missing":
        _block(checks, reasons, blockers, "center_shape", "missing_center", "missing center")
    elif center_status == "malformed":
        _block(checks, reasons, blockers, "center_shape", "missing_center", "invalid center")
    else:
        _add_check(checks, "center_shape", True)

    _check_center_matches_bbox(checks, reasons, blockers, bbox, center, coordinate_debug)
    _check_screen_bounds(checks, reasons, blockers, bbox, screen)

    _check_observation_freshness(
        checks,
        reasons,
        blockers,
        _effective_timestamp(action_contract, observation_timestamp),
        now,
        max_observation_age_seconds,
    )

    if not _capability_allows_click(capability):
        _block(
            checks,
            reasons,
            blockers,
            "click_capability",
            "action_not_enabled_by_policy",
            "click capability disabled",
        )
    else:
        _add_check(checks, "click_capability", True)

    if not _permission_profile_allows_click(permission_profile):
        _block(
            checks,
            reasons,
            blockers,
            "permission_profile",
            "action_not_enabled_by_policy",
            "permission profile does not allow click",
        )
    else:
        _add_check(checks, "permission_profile", True)

    if _safety_blocks(safety_decision):
        _block(
            checks,
            reasons,
            blockers,
            "safety_decision",
            "safety_decision_blocked",
            "safety decision blocked",
            severity="high",
        )
    else:
        _add_check(checks, "safety_decision", True)

    risk = _check_target_risk(checks, reasons, blockers, action_contract, safety_decision, risk)

    if reasons:
        return _blocked(
            reasons,
            risk=risk,
            checks=checks,
            blockers=blockers,
            target_debug=target_debug,
            coordinate_debug=coordinate_debug,
        )

    return {
        "ready": True,
        "status": "ready",
        "reasons": [],
        "blocker_codes": [],
        "blockers": [],
        "risk": risk,
        "target": target_debug,
        "coordinate_debug": coordinate_debug,
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
        "blocker_codes": [],
        "blockers": [],
        "risk": "none",
        "target": {},
        "coordinate_debug": {},
        "checks": checks,
    }


def click_readiness_metadata() -> dict[str, Any]:
    return {
        "enabled": False,
        "reason": "Real click execution is not enabled.",
        "required_checks": list(REQUIRED_CHECKS),
        "blocker_codes": [
            "stale_observation",
            "missing_target",
            "missing_bbox",
            "invalid_bbox",
            "missing_center",
            "bbox_center_mismatch",
            "out_of_viewport",
            "coordinate_space_unknown",
            "dpi_uncertain",
            "low_confidence_target",
            "hidden_or_disabled_target",
            "ambiguous_target",
            "high_risk_requires_approval",
            "action_not_enabled_by_policy",
        ],
        "high_risk_labels": list(HIGH_RISK_LABELS),
        "min_target_confidence": MIN_READY_TARGET_CONFIDENCE,
        "max_observation_age_seconds": DEFAULT_MAX_OBSERVATION_AGE_SECONDS,
    }


def _blocked(
    reasons: list[str],
    risk: str,
    checks: list[dict[str, Any]],
    blockers: list[dict[str, str]],
    target_debug: dict[str, Any],
    coordinate_debug: dict[str, Any],
) -> dict[str, Any]:
    return {
        "ready": False,
        "status": "blocked",
        "reasons": reasons,
        "blocker_codes": _unique_strings([blocker["code"] for blocker in blockers]),
        "blockers": blockers,
        "risk": risk,
        "target": target_debug,
        "coordinate_debug": coordinate_debug,
        "checks": checks,
    }


def _block(
    checks: list[dict[str, Any]],
    reasons: list[str],
    blockers: list[dict[str, str]],
    name: str,
    code: str,
    reason: str,
    severity: str = "medium",
) -> None:
    reasons.append(reason)
    blockers.append(
        {
            "code": code,
            "reason": reason,
            "severity": severity,
        }
    )
    _add_check(checks, name, False, reason, code=code)


def _add_check(
    checks: list[dict[str, Any]],
    name: str,
    passed: bool | str,
    reason: str = "",
    code: str = "",
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
    if code:
        check["code"] = code
    if reason:
        check["reason"] = reason

    checks.append(check)


def _check_target_present(
    checks: list[dict[str, Any]],
    reasons: list[str],
    blockers: list[dict[str, str]],
    action_contract: dict[str, Any],
) -> None:
    target_id = str(action_contract.get("target_element_id") or "").strip()
    target_label = str(action_contract.get("target_label") or "").strip()
    if not target_id and not target_label:
        _block(checks, reasons, blockers, "target_present", "missing_target", "missing target")
        return

    _add_check(checks, "target_present", True)


def _check_target_confidence(
    checks: list[dict[str, Any]],
    reasons: list[str],
    blockers: list[dict[str, str]],
    action_contract: dict[str, Any],
) -> None:
    confidence = _finite_float(action_contract.get("target_confidence"))
    if confidence is None:
        _block(
            checks,
            reasons,
            blockers,
            "target_confidence",
            "low_confidence_target",
            "target confidence unavailable",
        )
        return

    if confidence < MIN_READY_TARGET_CONFIDENCE:
        _block(
            checks,
            reasons,
            blockers,
            "target_confidence",
            "low_confidence_target",
            "low-confidence target",
        )
        return

    _add_check(checks, "target_confidence", True)


def _check_hidden_or_disabled_target(
    checks: list[dict[str, Any]],
    reasons: list[str],
    blockers: list[dict[str, str]],
    action_contract: dict[str, Any],
) -> None:
    visible = action_contract.get("target_visible")
    enabled = action_contract.get("target_enabled")
    confidence = _finite_float(action_contract.get("target_confidence"))
    source = str(action_contract.get("target_source") or "").strip().lower()
    risk_hint = str(action_contract.get("target_risk_hint") or "").strip().lower()

    if visible is False or enabled is False:
        _block(
            checks,
            reasons,
            blockers,
            "target_visibility",
            "hidden_or_disabled_target",
            "hidden or disabled target",
        )
        return

    if source == "ui_tree" and risk_hint == "unknown" and confidence is not None and confidence <= 0:
        _block(
            checks,
            reasons,
            blockers,
            "target_visibility",
            "hidden_or_disabled_target",
            "hidden or disabled target",
        )
        return

    _add_check(checks, "target_visibility", True)


def _check_ambiguous_target(
    checks: list[dict[str, Any]],
    reasons: list[str],
    blockers: list[dict[str, str]],
    action_contract: dict[str, Any],
    visible_elements: list[dict[str, Any]] | None,
) -> None:
    if not isinstance(visible_elements, list):
        _add_check(checks, "target_ambiguity", "not_applicable", "visible candidates unavailable")
        return

    if _target_is_ambiguous(action_contract, visible_elements):
        _block(
            checks,
            reasons,
            blockers,
            "target_ambiguity",
            "ambiguous_target",
            "ambiguous target",
        )
        return

    _add_check(checks, "target_ambiguity", True)


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


def _center_status(value: Any) -> tuple[str, dict[str, float] | None]:
    if value is None:
        return "missing", None

    if not isinstance(value, dict):
        return "malformed", None

    try:
        point = {
            "x": float(value["x"]),
            "y": float(value["y"]),
        }
    except (KeyError, TypeError, ValueError):
        return "malformed", None

    if not all(math.isfinite(number) for number in point.values()):
        return "malformed", None

    return "valid", point


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
    blockers: list[dict[str, str]],
    bbox: dict[str, float] | None,
    screen: dict[str, Any] | None,
) -> None:
    if bbox is None:
        _add_check(checks, "bbox_screen_bounds", "not_applicable", "bbox is unavailable")
        _add_check(checks, "coordinate_space", "not_applicable", "bbox is unavailable")
        _add_check(checks, "dpi_scale", "not_applicable", "bbox is unavailable")
        return

    bounds = _screen_bounds(screen)
    if bounds is None:
        _block(
            checks,
            reasons,
            blockers,
            "bbox_screen_bounds",
            "coordinate_space_unknown",
            "coordinate space unknown",
        )
        _add_check(checks, "coordinate_space", "not_applicable", "screen bounds unavailable")
        _add_check(checks, "dpi_scale", "not_applicable", "screen bounds unavailable")
        return

    coordinate_space = _coordinate_space(screen)
    if coordinate_space not in KNOWN_COORDINATE_SPACES:
        _block(
            checks,
            reasons,
            blockers,
            "coordinate_space",
            "coordinate_space_unknown",
            "coordinate space unknown",
        )
    else:
        _add_check(checks, "coordinate_space", True)

    if _dpi_scale(screen) is None:
        _block(checks, reasons, blockers, "dpi_scale", "dpi_uncertain", "dpi is uncertain")
    else:
        _add_check(checks, "dpi_scale", True)

    screen_width, screen_height = bounds
    in_bounds = (
        bbox["x"] >= 0
        and bbox["y"] >= 0
        and bbox["x"] + bbox["width"] <= screen_width
        and bbox["y"] + bbox["height"] <= screen_height
    )

    if not in_bounds:
        _block(
            checks,
            reasons,
            blockers,
            "bbox_screen_bounds",
            "out_of_viewport",
            "bbox outside screen bounds",
        )
        return

    _add_check(checks, "bbox_screen_bounds", True)


def _check_center_matches_bbox(
    checks: list[dict[str, Any]],
    reasons: list[str],
    blockers: list[dict[str, str]],
    bbox: dict[str, float] | None,
    center: dict[str, float] | None,
    coordinate_debug: dict[str, Any],
) -> None:
    if bbox is None or center is None:
        _add_check(checks, "center_bbox_consistency", "not_applicable", "bbox or center unavailable")
        return

    expected = {
        "x": round(bbox["x"] + bbox["width"] / 2),
        "y": round(bbox["y"] + bbox["height"] / 2),
    }
    coordinate_debug["expected_center"] = expected
    actual = {
        "x": round(center["x"]),
        "y": round(center["y"]),
    }
    if actual != expected:
        _block(
            checks,
            reasons,
            blockers,
            "center_bbox_consistency",
            "bbox_center_mismatch",
            "center does not match bbox",
        )
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


def _coordinate_space(screen: dict[str, Any] | None) -> str:
    if not isinstance(screen, dict):
        return ""

    return str(screen.get("coordinate_space") or screen.get("space") or "").strip().lower()


def _dpi_scale(screen: dict[str, Any] | None) -> float | None:
    if not isinstance(screen, dict):
        return None

    for key in ["dpi_scale", "scale", "device_pixel_ratio"]:
        value = _finite_float(screen.get(key))
        if value is not None and value > 0:
            return value

    return None


def _check_observation_freshness(
    checks: list[dict[str, Any]],
    reasons: list[str],
    blockers: list[dict[str, str]],
    observation_timestamp: str | None,
    now: datetime | None,
    max_observation_age_seconds: float,
) -> None:
    if not observation_timestamp:
        _block(
            checks,
            reasons,
            blockers,
            "observation_freshness",
            "stale_observation",
            "observation timestamp unavailable",
        )
        return

    observed_at = _parse_timestamp(observation_timestamp)
    if observed_at is None:
        _block(
            checks,
            reasons,
            blockers,
            "observation_freshness",
            "stale_observation",
            "malformed observation timestamp",
        )
        return

    current_time = now or datetime.now(timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)

    max_age = _positive_float(max_observation_age_seconds)
    age_seconds = max(0.0, (current_time - observed_at).total_seconds())
    if max_age is not None and age_seconds > max_age:
        _block(
            checks,
            reasons,
            blockers,
            "observation_freshness",
            "stale_observation",
            "stale observation",
        )
        return

    _add_check(checks, "observation_freshness", True)


def _effective_timestamp(
    action_contract: dict[str, Any],
    observation_timestamp: str | None,
) -> str | None:
    for value in [
        observation_timestamp,
        action_contract.get("observation_timestamp"),
        action_contract.get("target_timestamp"),
    ]:
        if isinstance(value, str) and value.strip():
            return value

    return None


def _parse_timestamp(value: str | None) -> datetime | None:
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


def _check_target_risk(
    checks: list[dict[str, Any]],
    reasons: list[str],
    blockers: list[dict[str, str]],
    action_contract: dict[str, Any],
    safety_decision: dict[str, Any] | None,
    current_risk: str,
) -> str:
    risk_hint = str(action_contract.get("target_risk_hint") or "").strip().lower()

    if _has_high_risk_label(action_contract) or _safety_needs_approval(safety_decision):
        _block(
            checks,
            reasons,
            blockers,
            "target_label_risk",
            "high_risk_requires_approval",
            "high-risk target label",
            severity="high",
        )
        return "high"

    if risk_hint in {"", "unknown"}:
        _block(
            checks,
            reasons,
            blockers,
            "target_label_risk",
            "unknown_risk_target",
            "target risk is unknown",
        )
        return _highest_risk(current_risk, "medium")

    _add_check(checks, "target_label_risk", True)
    return current_risk


def _safety_needs_approval(safety_decision: dict[str, Any] | None) -> bool:
    if not isinstance(safety_decision, dict):
        return False

    return safety_decision.get("decision") == "needs_approval"


def _has_high_risk_label(action_contract: dict[str, Any]) -> bool:
    risk_hint = str(action_contract.get("target_risk_hint") or "").strip().lower()
    if risk_hint in {"high", "high_risk"}:
        return True

    label = normalize_label_text(action_contract.get("target_label"))
    return any(normalize_label_text(high_risk_label) in label for high_risk_label in HIGH_RISK_LABELS)


def _target_is_ambiguous(
    action_contract: dict[str, Any],
    visible_elements: list[dict[str, Any]],
) -> bool:
    target_label = normalize_label_text(action_contract.get("target_label"))
    target_role = normalize_label_text(action_contract.get("target_role")).replace(" ", "_")
    target_confidence = _finite_float(action_contract.get("target_confidence"))
    if not target_label or target_confidence is None:
        return False

    matching: list[dict[str, Any]] = []
    for element in visible_elements:
        if not isinstance(element, dict):
            continue
        label = normalize_label_text(element.get("label") or element.get("text"))
        role = normalize_label_text(element.get("role")).replace(" ", "_")
        confidence = _finite_float(element.get("confidence"))
        if (
            label == target_label
            and (not target_role or role == target_role)
            and confidence is not None
            and confidence >= MIN_READY_TARGET_CONFIDENCE
            and abs(confidence - target_confidence) <= 0.05
            and _bbox_status(element.get("bbox"))[0] == "valid"
        ):
            matching.append(element)

    return len(matching) > 1


def _target_debug(action_contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(action_contract.get("target_element_id") or ""),
        "label": str(action_contract.get("target_label") or ""),
        "role": str(action_contract.get("target_role") or ""),
        "source": str(action_contract.get("target_source") or ""),
        "confidence": action_contract.get("target_confidence"),
        "risk_hint": str(action_contract.get("target_risk_hint") or "unknown"),
        "timestamp": str(action_contract.get("target_timestamp") or ""),
        "visible": action_contract.get("target_visible"),
        "enabled": action_contract.get("target_enabled"),
    }


def _screen_debug(screen: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(screen, dict):
        return {}

    return {
        "width": screen.get("width"),
        "height": screen.get("height"),
        "coordinate_space": screen.get("coordinate_space") or screen.get("space"),
        "dpi_scale": screen.get("dpi_scale")
        or screen.get("scale")
        or screen.get("device_pixel_ratio"),
    }


def _finite_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    return number if math.isfinite(number) else None


def _highest_risk(left: str, right: str) -> str:
    order = {"none": 0, "low": 1, "medium": 2, "high": 3}
    return left if order.get(left, 2) >= order.get(right, 2) else right


def _unique_strings(values: list[str]) -> list[str]:
    unique: list[str] = []
    for value in values:
        if value and value not in unique:
            unique.append(value)

    return unique
