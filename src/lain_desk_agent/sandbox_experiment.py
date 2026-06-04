"""Phase 8 dry-run sandbox experiment gate.

This module defines the structure for a future one-window, one-target sandbox
action experiment. It intentionally performs no desktop actuation: the default
path is dry-run, and requests for real action are skipped unless a future,
separately approved adapter is added behind the Phase 7 gate.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


FAILURE_MISSING_PHASE7_CHECKLIST = "missing_phase7_checklist"
FAILURE_MISSING_USER_APPROVAL = "missing_user_approval"
FAILURE_MISSING_AUDIT_PLAN = "missing_audit_plan"
FAILURE_MISSING_ACTION_CONTRACT = "missing_action_contract"
FAILURE_MISSING_TARGET = "missing_target"
FAILURE_MISSING_EMERGENCY_STOP = "missing_emergency_stop"
FAILURE_REAL_ACTION_DISABLED = "real_action_disabled"
FAILURE_READINESS_NOT_READY = "readiness_not_ready"
FAILURE_HIGH_RISK_TARGET = "high_risk_target"
FAILURE_LOW_CONFIDENCE_TARGET = "low_confidence_target"
FAILURE_STALE_OBSERVATION = "stale_observation"
FAILURE_INVALID_TARGET_GEOMETRY = "invalid_target_geometry"
FAILURE_MISSING_POST_ACTION_VERIFICATION = "missing_post_action_verification"
FAILURE_FORBIDDEN_ACTION_TYPE = "forbidden_action_type"
FAILURE_OUTSIDE_SANDBOX_SCOPE = "outside_sandbox_scope"

EVENT_SANDBOX_EXPERIMENT_REQUESTED = "sandbox_experiment_requested"
EVENT_SANDBOX_GATE_PASSED = "sandbox_gate_passed"
EVENT_SANDBOX_GATE_BLOCKED = "sandbox_gate_blocked"
EVENT_SANDBOX_DRY_RUN_COMPLETED = "sandbox_dry_run_completed"
EVENT_SANDBOX_REAL_ACTION_SKIPPED = "sandbox_real_action_skipped"
EVENT_SANDBOX_POST_ACTION_VERIFICATION_PLANNED = "sandbox_post_action_verification_planned"

REQUIRED_PHASE7_CHECKLIST_ITEMS = (
    "explicit_experiment_name",
    "dry_run_status_recorded",
    "explicit_user_approval",
    "target_from_visible_elements",
    "current_observation_freshness",
    "click_readiness",
    "low_risk_target",
    "valid_geometry",
    "action_contract_present",
    "audit_event_before_action",
    "audit_event_after_action",
    "post_action_verification",
    "emergency_stop_available",
    "sandbox_scope_limited",
    "forbidden_actions_respected",
)

FORBIDDEN_ACTION_TYPES = (
    "delete",
    "file_delete",
    "hotkey",
    "launch_app",
    "press",
    "scroll",
    "send",
    "shell",
    "submit",
    "switch_app",
    "type",
    "type_text",
)

ALLOWED_SANDBOX_ACTION_TYPES = ("click",)
LOW_RISK_VALUES = ("low", "normal")
KNOWN_COORDINATE_SPACES = {"screen", "viewport", "desktop"}
DEFAULT_MAX_OBSERVATION_AGE_SECONDS = 10.0
MIN_SANDBOX_TARGET_CONFIDENCE = 0.45


@dataclass(frozen=True)
class SandboxExperimentConfig:
    """Static scope and safety settings for one named sandbox experiment."""

    experiment_name: str = ""
    dry_run: bool = True
    real_action_enabled: bool = False
    allowed_action_type: str = "click"
    allowed_window_id: str = ""
    allowed_target_id: str = ""
    max_observation_age_seconds: float = DEFAULT_MAX_OBSERVATION_AGE_SECONDS
    phase7_checklist: dict[str, bool] = field(default_factory=dict)
    expected_readiness_blocker_codes: tuple[str, ...] = ()
    forbidden_action_types: tuple[str, ...] = FORBIDDEN_ACTION_TYPES
    emergency_stop_available: bool = False
    emergency_stop_active: bool = False
    audit_events_required: bool = True


@dataclass(frozen=True)
class SandboxExperimentRequest:
    """Runtime request data consumed by the Phase 8 dry-run gate."""

    user_approved: bool = False
    action_contract: dict[str, Any] | None = None
    click_readiness: dict[str, Any] | None = None
    visible_elements: list[dict[str, Any]] = field(default_factory=list)
    safety_decision: dict[str, Any] | None = None
    screen: dict[str, Any] | None = None
    observation_timestamp: str = ""
    post_action_verification_plan: dict[str, Any] | None = None
    sandbox_window_id: str = ""
    current_time: datetime | None = None
    audit_context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SandboxExperimentResult:
    """Structured outcome for a dry-run sandbox experiment request."""

    experiment_name: str
    dry_run: bool
    real_action_enabled: bool
    status: str
    gate_passed: bool
    simulated: bool
    real_action_attempted: bool
    failure_reasons: list[str]
    audit_events: list[dict[str, Any]]
    validation: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation for tests or future UI debug."""

        return {
            "experiment_name": self.experiment_name,
            "dry_run": self.dry_run,
            "real_action_enabled": self.real_action_enabled,
            "status": self.status,
            "gate_passed": self.gate_passed,
            "simulated": self.simulated,
            "real_action_attempted": self.real_action_attempted,
            "failure_reasons": list(self.failure_reasons),
            "audit_events": [dict(event) for event in self.audit_events],
            "validation": dict(self.validation),
        }


def validate_phase7_gate(
    config: SandboxExperimentConfig,
    request: SandboxExperimentRequest,
) -> dict[str, Any]:
    """Validate the Phase 7 checklist before a sandbox experiment can proceed."""

    failure_reasons: list[str] = []
    checks: list[dict[str, Any]] = []

    _check(
        checks,
        "experiment_name",
        bool(config.experiment_name.strip()),
        FAILURE_MISSING_PHASE7_CHECKLIST,
        failure_reasons,
    )
    _check(
        checks,
        "dry_run_status_recorded",
        isinstance(config.dry_run, bool) and isinstance(config.real_action_enabled, bool),
        FAILURE_MISSING_PHASE7_CHECKLIST,
        failure_reasons,
    )
    _check(
        checks,
        "phase7_checklist",
        _phase7_checklist_complete(config.phase7_checklist),
        FAILURE_MISSING_PHASE7_CHECKLIST,
        failure_reasons,
        {
            "required_items": list(REQUIRED_PHASE7_CHECKLIST_ITEMS),
            "missing_items": _missing_phase7_checklist_items(config.phase7_checklist),
        },
    )
    _check(
        checks,
        "user_approval",
        request.user_approved,
        FAILURE_MISSING_USER_APPROVAL,
        failure_reasons,
    )
    _check(
        checks,
        "audit_events_required",
        config.audit_events_required,
        FAILURE_MISSING_AUDIT_PLAN,
        failure_reasons,
    )
    _check(
        checks,
        "emergency_stop_available",
        config.emergency_stop_available and not config.emergency_stop_active,
        FAILURE_MISSING_EMERGENCY_STOP,
        failure_reasons,
    )

    action_contract = request.action_contract if isinstance(request.action_contract, dict) else None
    _check(
        checks,
        "action_contract_present",
        action_contract is not None,
        FAILURE_MISSING_ACTION_CONTRACT,
        failure_reasons,
    )
    if action_contract is None:
        _check(
            checks,
            "post_action_verification",
            _has_post_action_verification_plan(request.post_action_verification_plan),
            FAILURE_MISSING_POST_ACTION_VERIFICATION,
            failure_reasons,
        )
        return {
            "passed": not failure_reasons,
            "failure_reasons": _unique(failure_reasons),
            "checks": checks,
        }

    action_type = _string_field(action_contract, "type")
    target_id = _raw_string_field(action_contract, "target_element_id").strip()
    forbidden_action_types = {item.lower() for item in config.forbidden_action_types}
    if action_type in forbidden_action_types:
        _check(checks, "forbidden_action_type", False, FAILURE_FORBIDDEN_ACTION_TYPE, failure_reasons)
    else:
        _check(checks, "forbidden_action_type", True, FAILURE_FORBIDDEN_ACTION_TYPE, failure_reasons)

    allowed_action = (
        action_type in ALLOWED_SANDBOX_ACTION_TYPES
        and action_type == config.allowed_action_type
    )
    _check(checks, "allowed_action_type", allowed_action, FAILURE_OUTSIDE_SANDBOX_SCOPE, failure_reasons)

    target_element = _find_visible_target(request.visible_elements, target_id)
    target_present = bool(target_id) and target_element is not None
    _check(
        checks,
        "target_present",
        target_present,
        FAILURE_MISSING_TARGET,
        failure_reasons,
    )

    target_in_scope = target_present
    if config.allowed_target_id:
        target_in_scope = target_in_scope and target_id == config.allowed_target_id
    if config.allowed_window_id:
        target_in_scope = target_in_scope and request.sandbox_window_id == config.allowed_window_id
    _check(
        checks,
        "target_from_visible_elements",
        (not target_present) or target_in_scope,
        FAILURE_OUTSIDE_SANDBOX_SCOPE,
        failure_reasons,
    )

    _check(
        checks,
        "low_risk_target",
        _low_risk_target(action_contract, target_element, request.safety_decision),
        FAILURE_HIGH_RISK_TARGET,
        failure_reasons,
    )
    _check(
        checks,
        "target_confidence",
        _target_confidence_ready(action_contract, target_element),
        FAILURE_LOW_CONFIDENCE_TARGET,
        failure_reasons,
        {"min_confidence": MIN_SANDBOX_TARGET_CONFIDENCE},
    )
    _check(
        checks,
        "observation_freshness",
        _fresh_observation(config, request, action_contract, target_element),
        FAILURE_STALE_OBSERVATION,
        failure_reasons,
    )
    _check(
        checks,
        "target_geometry",
        _valid_target_geometry(action_contract, request.screen),
        FAILURE_INVALID_TARGET_GEOMETRY,
        failure_reasons,
    )
    _check(
        checks,
        "click_readiness",
        _readiness_allows_dry_run(config, request.click_readiness),
        FAILURE_READINESS_NOT_READY,
        failure_reasons,
        {"expected_blocker_codes": list(config.expected_readiness_blocker_codes)},
    )
    _check(
        checks,
        "post_action_verification",
        _has_post_action_verification_plan(request.post_action_verification_plan),
        FAILURE_MISSING_POST_ACTION_VERIFICATION,
        failure_reasons,
    )

    return {
        "passed": not failure_reasons,
        "failure_reasons": _unique(failure_reasons),
        "checks": checks,
    }


def run_sandbox_experiment(
    config: SandboxExperimentConfig | None = None,
    request: SandboxExperimentRequest | None = None,
) -> SandboxExperimentResult:
    """Run the Phase 8 sandbox framework without performing real desktop input."""

    config = config or SandboxExperimentConfig()
    request = request or SandboxExperimentRequest()

    audit_events = [
        _audit_event(EVENT_SANDBOX_EXPERIMENT_REQUESTED, config, request, []),
    ]
    validation = validate_phase7_gate(config, request)
    failure_reasons = list(validation["failure_reasons"])

    if not validation["passed"]:
        audit_events.append(_audit_event(EVENT_SANDBOX_GATE_BLOCKED, config, request, failure_reasons))
        return SandboxExperimentResult(
            experiment_name=config.experiment_name,
            dry_run=config.dry_run,
            real_action_enabled=config.real_action_enabled,
            status="blocked",
            gate_passed=False,
            simulated=True,
            real_action_attempted=False,
            failure_reasons=failure_reasons,
            audit_events=audit_events,
            validation=validation,
        )

    audit_events.append(_audit_event(EVENT_SANDBOX_GATE_PASSED, config, request, []))
    audit_events.append(_audit_event(EVENT_SANDBOX_POST_ACTION_VERIFICATION_PLANNED, config, request, []))

    if config.dry_run:
        audit_events.append(_audit_event(EVENT_SANDBOX_DRY_RUN_COMPLETED, config, request, []))
        return SandboxExperimentResult(
            experiment_name=config.experiment_name,
            dry_run=config.dry_run,
            real_action_enabled=config.real_action_enabled,
            status="dry_run_completed",
            gate_passed=True,
            simulated=True,
            real_action_attempted=False,
            failure_reasons=[],
            audit_events=audit_events,
            validation=validation,
        )

    audit_events.append(
        _audit_event(
            EVENT_SANDBOX_REAL_ACTION_SKIPPED,
            config,
            request,
            [FAILURE_REAL_ACTION_DISABLED],
        )
    )
    return SandboxExperimentResult(
        experiment_name=config.experiment_name,
        dry_run=config.dry_run,
        real_action_enabled=config.real_action_enabled,
        status="real_action_skipped",
        gate_passed=True,
        simulated=True,
        real_action_attempted=False,
        failure_reasons=[FAILURE_REAL_ACTION_DISABLED],
        audit_events=audit_events,
        validation=validation,
    )


def _check(
    checks: list[dict[str, Any]],
    name: str,
    passed: bool,
    failure_reason: str,
    failure_reasons: list[str],
    detail: dict[str, Any] | None = None,
) -> None:
    check = {
        "name": name,
        "passed": bool(passed),
        "failure_reason": "" if passed else failure_reason,
    }
    if detail:
        check.update(detail)
    checks.append(check)
    if not passed:
        failure_reasons.append(failure_reason)


def _phase7_checklist_complete(checklist: dict[str, bool]) -> bool:
    if not isinstance(checklist, dict):
        return False
    return not _missing_phase7_checklist_items(checklist)


def _missing_phase7_checklist_items(checklist: dict[str, bool]) -> list[str]:
    if not isinstance(checklist, dict):
        return list(REQUIRED_PHASE7_CHECKLIST_ITEMS)
    return [item for item in REQUIRED_PHASE7_CHECKLIST_ITEMS if checklist.get(item) is not True]


def _string_field(mapping: dict[str, Any] | None, key: str) -> str:
    if not isinstance(mapping, dict):
        return ""
    return str(mapping.get(key) or "").strip().lower()


def _find_visible_target(
    visible_elements: list[dict[str, Any]],
    target_id: str,
) -> dict[str, Any] | None:
    if not target_id:
        return None

    for element in visible_elements:
        if isinstance(element, dict) and str(element.get("id") or "").strip() == target_id:
            return element
    return None


def _low_risk_target(
    action_contract: dict[str, Any] | None,
    target_element: dict[str, Any] | None,
    safety_decision: dict[str, Any] | None,
) -> bool:
    risk_values = [
        _string_field(action_contract, "risk"),
        _string_field(action_contract, "target_risk_hint"),
        _string_field(target_element, "risk_hint"),
    ]
    if isinstance(safety_decision, dict):
        risk_values.extend(
            [
                str(safety_decision.get("risk") or "").strip().lower(),
                str(safety_decision.get("decision") or "").strip().lower(),
            ]
        )

    meaningful_values = [value for value in risk_values if value]
    if not meaningful_values:
        return False

    return all(value in LOW_RISK_VALUES or value == "allowed" for value in meaningful_values)


def _target_confidence_ready(
    action_contract: dict[str, Any] | None,
    target_element: dict[str, Any] | None,
) -> bool:
    confidence = _finite_float(_mapping_value(action_contract, "target_confidence"))
    if confidence is None:
        confidence = _finite_float(_mapping_value(target_element, "confidence"))
    return confidence is not None and confidence >= MIN_SANDBOX_TARGET_CONFIDENCE


def _mapping_value(mapping: dict[str, Any] | None, key: str) -> Any:
    if not isinstance(mapping, dict):
        return None
    return mapping.get(key)


def _finite_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _fresh_observation(
    config: SandboxExperimentConfig,
    request: SandboxExperimentRequest,
    action_contract: dict[str, Any] | None,
    target_element: dict[str, Any] | None,
) -> bool:
    timestamp = (
        request.observation_timestamp
        or _raw_string_field(action_contract, "target_timestamp")
        or _raw_string_field(target_element, "timestamp")
    )
    observed_at = _parse_iso8601(timestamp)
    if observed_at is None:
        return False

    now = request.current_time or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    age = (now - observed_at).total_seconds()
    return 0 <= age <= config.max_observation_age_seconds


def _raw_string_field(mapping: dict[str, Any] | None, key: str) -> str:
    if not isinstance(mapping, dict):
        return ""
    value = mapping.get(key)
    return value if isinstance(value, str) else str(value or "")


def _parse_iso8601(value: str) -> datetime | None:
    if not value:
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _valid_target_geometry(
    action_contract: dict[str, Any] | None,
    screen: dict[str, Any] | None,
) -> bool:
    if not isinstance(action_contract, dict) or not isinstance(screen, dict):
        return False

    bbox = _geometry_mapping(action_contract.get("bbox"), ("x", "y", "width", "height"))
    center = _geometry_mapping(action_contract.get("center"), ("x", "y"))
    viewport = _geometry_mapping(screen, ("width", "height"))
    if bbox is None or center is None or viewport is None:
        return False
    if bbox["width"] <= 0 or bbox["height"] <= 0:
        return False
    if viewport["width"] <= 0 or viewport["height"] <= 0:
        return False
    if _coordinate_space(screen) not in KNOWN_COORDINATE_SPACES:
        return False
    if _screen_scale(screen) is None:
        return False

    expected_center = {
        "x": round(bbox["x"] + bbox["width"] / 2),
        "y": round(bbox["y"] + bbox["height"] / 2),
    }
    if center != expected_center:
        return False

    if bbox["x"] < 0 or bbox["y"] < 0:
        return False
    if bbox["x"] + bbox["width"] > viewport["width"]:
        return False
    if bbox["y"] + bbox["height"] > viewport["height"]:
        return False
    if center["x"] < 0 or center["y"] < 0:
        return False
    if center["x"] > viewport["width"] or center["y"] > viewport["height"]:
        return False

    return True


def _coordinate_space(screen: dict[str, Any]) -> str:
    return str(screen.get("coordinate_space") or screen.get("space") or "").strip().lower()


def _screen_scale(screen: dict[str, Any]) -> float | None:
    for key in ["dpi_scale", "scale", "device_pixel_ratio"]:
        value = _finite_float(screen.get(key))
        if value is not None:
            return value
    return None


def _geometry_mapping(value: Any, required_keys: tuple[str, ...]) -> dict[str, int] | None:
    if not isinstance(value, dict):
        return None

    numbers: dict[str, int] = {}
    for key in required_keys:
        try:
            number = float(value[key])
        except (KeyError, TypeError, ValueError):
            return None
        if not math.isfinite(number):
            return None
        if not number.is_integer():
            return None
        numbers[key] = int(number)
    return numbers


def _readiness_allows_dry_run(
    config: SandboxExperimentConfig,
    click_readiness: dict[str, Any] | None,
) -> bool:
    if not isinstance(click_readiness, dict):
        return False
    if click_readiness.get("ready") is True and click_readiness.get("status") == "ready":
        return True

    actual_codes = {
        str(code)
        for code in click_readiness.get("blocker_codes", [])
        if isinstance(code, str)
    }
    expected_codes = set(config.expected_readiness_blocker_codes)
    if not expected_codes:
        return False

    return (
        config.dry_run
        and not config.real_action_enabled
        and expected_codes.issubset(actual_codes)
    )


def _has_post_action_verification_plan(plan: dict[str, Any] | None) -> bool:
    if not isinstance(plan, dict):
        return False
    if plan.get("enabled") is not True:
        return False
    return bool(
        str(plan.get("method") or "").strip()
        or str(plan.get("expected_state") or "").strip()
        or str(plan.get("expected_state_change") or "").strip()
    )


def _audit_event(
    event_type: str,
    config: SandboxExperimentConfig,
    request: SandboxExperimentRequest,
    failure_reasons: list[str],
) -> dict[str, Any]:
    action_contract = request.action_contract if isinstance(request.action_contract, dict) else {}
    timestamp = request.current_time or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    return {
        "type": event_type,
        "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
        "phase": "phase8_sandbox_experiment",
        "experiment_name": config.experiment_name,
        "dry_run": config.dry_run,
        "real_action_enabled": config.real_action_enabled,
        "action_id": str(action_contract.get("action_id") or ""),
        "action_type": str(action_contract.get("type") or ""),
        "target_element_id": str(action_contract.get("target_element_id") or ""),
        "target_label": str(action_contract.get("target_label") or ""),
        "sandbox_window_id": request.sandbox_window_id,
        "failure_reasons": list(failure_reasons),
        "audit_context": dict(request.audit_context),
    }


def _unique(values: list[str]) -> list[str]:
    unique_values: list[str] = []
    for value in values:
        if value not in unique_values:
            unique_values.append(value)
    return unique_values
