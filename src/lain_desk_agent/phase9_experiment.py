"""Phase 9.1 dry-run-only minimal sandbox experiment harness.

The harness executes the Phase 9 experiment specification as deterministic
fixture simulation. It reuses the Phase 8 sandbox gate for Phase 7 checks,
adds mock approval, emergency stop, verification, and rollback requirements,
and never performs desktop actuation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .sandbox_experiment import (
    DEFAULT_MAX_OBSERVATION_AGE_SECONDS,
    FAILURE_MISSING_PHASE7_CHECKLIST,
    FAILURE_MISSING_USER_APPROVAL,
    FAILURE_OUTSIDE_SANDBOX_SCOPE,
    FAILURE_REAL_ACTION_DISABLED,
    FORBIDDEN_ACTION_TYPES,
    SandboxExperimentConfig,
    SandboxExperimentRequest,
    validate_phase7_gate,
)


PHASE9_MINIMAL_SCENARIO_IDS = (
    "dry_run_success_all_gates_pass",
    "real_action_disabled_skips_non_dry_run",
    "missing_user_approval_blocks",
    "stale_observation_blocks",
    "high_risk_target_blocks",
    "missing_audit_plan_blocks",
    "missing_action_contract_blocks",
)

FAILURE_MISSING_ROLLBACK_PLAN = "missing_rollback_plan"
FAILURE_EMERGENCY_STOP_ACTIVE = "emergency_stop_active"

EVENT_PHASE9_EXPERIMENT_REQUESTED = "phase9_experiment_requested"
EVENT_PHASE9_GATE_PASSED = "phase9_gate_passed"
EVENT_PHASE9_GATE_BLOCKED = "phase9_gate_blocked"
EVENT_PHASE9_MOCK_APPROVAL_CHECKED = "phase9_mock_approval_checked"
EVENT_PHASE9_EMERGENCY_STOP_CHECKED = "phase9_emergency_stop_checked"
EVENT_PHASE9_DRY_RUN_COMPLETED = "phase9_dry_run_completed"
EVENT_PHASE9_POST_ACTION_VERIFICATION_PLANNED = "phase9_post_action_verification_planned"
EVENT_PHASE9_ROLLBACK_PLAN_RECORDED = "phase9_rollback_plan_recorded"
EVENT_PHASE9_REAL_ACTION_SKIPPED = "phase9_real_action_skipped"

PHASE9_REPORT_FIELDS = (
    "scenario_id",
    "scenario_name",
    "expected_outcome",
    "actual_outcome",
    "passed",
    "gate_passed",
    "failure_reason_codes",
    "blocker_codes",
    "audit_event_names",
    "dry_run",
    "real_action_enabled",
    "real_action_skipped",
    "post_action_verification_planned",
    "target_risk_hint",
    "target_confidence",
    "readiness_ready",
    "action_type",
    "notes",
    "trace",
)

DEFAULT_ALLOWED_WINDOW_ID = "sandbox_window"
DEFAULT_ALLOWED_TARGET_ID = "sandbox_target_button"
DEFAULT_ALLOWED_ACTION_TYPE = "click"


@dataclass(frozen=True)
class MockApprovalState:
    """Deterministic approval fixture bound to one contract and target."""

    present: bool = False
    user_approved: bool = False
    action_contract_id: str = ""
    target_id: str = ""
    observation_id: str = ""
    approved_at: str = ""
    expires_at: str = ""


@dataclass(frozen=True)
class MockEmergencyStopState:
    """Deterministic emergency-stop fixture for Phase 9 gate checks."""

    available: bool = False
    active: bool = False
    checked_at: str = ""


@dataclass(frozen=True)
class MockPostActionVerificationPlan:
    """Mock-only verification plan; it never observes live post-action state."""

    present: bool = False
    planned: bool = False
    simulated: bool = True
    method: str = "fixture_state_assertion"
    expected_state_change: str = "sandbox target would be selected"
    observed_state_change: str = "not_observed"
    passed: bool = True


@dataclass(frozen=True)
class MockRollbackPlan:
    """Mock-only rollback/reset plan for deterministic fixture state."""

    present: bool = False
    simulated: bool = True
    strategy: str = "reset_fixture_state"
    sandbox_only: bool = True


@dataclass(frozen=True)
class Phase9ExperimentConfig:
    """Static scope and safety settings for one Phase 9 dry-run experiment."""

    experiment_id: str = ""
    dry_run: bool = True
    real_action_enabled: bool = False
    allowed_action_type: str = DEFAULT_ALLOWED_ACTION_TYPE
    allowed_window_id: str = DEFAULT_ALLOWED_WINDOW_ID
    allowed_target_id: str = DEFAULT_ALLOWED_TARGET_ID
    max_observation_age_seconds: float = DEFAULT_MAX_OBSERVATION_AGE_SECONDS
    phase7_checklist: dict[str, bool] = field(default_factory=dict)
    expected_readiness_blocker_codes: tuple[str, ...] = ()
    forbidden_action_types: tuple[str, ...] = FORBIDDEN_ACTION_TYPES
    audit_plan_present: bool = True
    allowed_scenario_ids: tuple[str, ...] = PHASE9_MINIMAL_SCENARIO_IDS
    future_real_action_gate_approved: bool = False


@dataclass(frozen=True)
class Phase9ExperimentRequest:
    """Fixture request data consumed by the Phase 9.1 dry-run harness."""

    scenario_id: str = ""
    scenario_name: str = ""
    expected_outcome: dict[str, Any] = field(default_factory=dict)
    sandbox_scope: dict[str, Any] = field(default_factory=dict)
    approval: MockApprovalState | None = None
    emergency_stop: MockEmergencyStopState | None = None
    post_action_verification_plan: MockPostActionVerificationPlan | None = None
    rollback_plan: MockRollbackPlan | None = None
    action_contract: dict[str, Any] | None = None
    click_readiness: dict[str, Any] | None = None
    visible_elements: list[dict[str, Any]] = field(default_factory=list)
    safety_decision: dict[str, Any] | None = None
    screen: dict[str, Any] | None = None
    observation_timestamp: str = ""
    observation_id: str = ""
    sandbox_window_id: str = ""
    current_time: datetime | None = None
    audit_context: dict[str, Any] = field(default_factory=dict)
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class Phase9ExperimentResult:
    """Structured Phase 9.1 dry-run outcome compatible with Phase 8 reports."""

    experiment_id: str
    scenario_id: str
    scenario_name: str
    expected_outcome: dict[str, Any]
    status: str
    gate_passed: bool
    dry_run: bool
    real_action_enabled: bool
    simulated: bool
    real_action_attempted: bool
    real_action_skipped: bool
    failure_reason_codes: list[str]
    blocker_codes: list[str]
    audit_events: list[dict[str, Any]]
    validation: dict[str, Any]
    post_action_verification_planned: bool
    rollback_plan_recorded: bool
    target_risk_hint: str
    target_confidence: float | None
    readiness_ready: bool
    action_type: str
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Return the Phase 8-compatible scenario report shape."""

        actual_outcome = self.actual_outcome()
        passed = _expectation_matches(self.expected_outcome, actual_outcome)
        return {
            "experiment_id": self.experiment_id,
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
            "expected_outcome": dict(self.expected_outcome),
            "actual_outcome": actual_outcome,
            "passed": passed,
            "gate_passed": self.gate_passed,
            "failure_reason_codes": list(self.failure_reason_codes),
            "blocker_codes": list(self.blocker_codes),
            "audit_event_names": self.audit_event_names(),
            "dry_run": self.dry_run,
            "real_action_enabled": self.real_action_enabled,
            "real_action_skipped": self.real_action_skipped,
            "post_action_verification_planned": self.post_action_verification_planned,
            "target_risk_hint": self.target_risk_hint,
            "target_confidence": self.target_confidence,
            "readiness_ready": self.readiness_ready,
            "action_type": self.action_type,
            "notes": list(self.notes),
            "trace": self.trace(),
        }

    def actual_outcome(self) -> dict[str, Any]:
        """Return deterministic outcome fields shared with sandbox evaluation."""

        return {
            "status": self.status,
            "gate_passed": self.gate_passed,
            "dry_run": self.dry_run,
            "real_action_enabled": self.real_action_enabled,
            "real_action_skipped": self.real_action_skipped,
            "failure_reason_codes": list(self.failure_reason_codes),
            "blocker_codes": list(self.blocker_codes),
            "audit_event_names": self.audit_event_names(),
            "post_action_verification_planned": self.post_action_verification_planned,
            "real_action_attempted": self.real_action_attempted,
        }

    def audit_event_names(self) -> list[str]:
        """Return audit event names in recorded order."""

        return [str(event.get("type") or "") for event in self.audit_events]

    def trace(self) -> dict[str, Any]:
        """Return stable debug details for cockpit-compatible inspection."""

        return {
            "experiment_id": self.experiment_id,
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
            "result_status": self.status,
            "gate_passed": self.gate_passed,
            "dry_run": self.dry_run,
            "real_action_enabled": self.real_action_enabled,
            "real_action_skipped": self.real_action_skipped,
            "failure_reason_codes": list(self.failure_reason_codes),
            "blocker_codes": list(self.blocker_codes),
            "audit_event_names": self.audit_event_names(),
            "post_action_verification_planned": self.post_action_verification_planned,
            "rollback_plan_recorded": self.rollback_plan_recorded,
            "validation_checks": _validation_checks(self.validation),
        }


def validate_phase9_gate(
    config: Phase9ExperimentConfig,
    request: Phase9ExperimentRequest,
) -> dict[str, Any]:
    """Validate Phase 9-specific requirements plus the reused Phase 7 gate."""

    phase7_validation = validate_phase7_gate(
        _phase8_config(config, request),
        _phase8_request(config, request),
    )
    checks = list(phase7_validation.get("checks", []))
    failure_reasons = list(phase7_validation.get("failure_reasons", []))

    _check(
        checks,
        "phase9_experiment_id",
        bool(config.experiment_id.strip()),
        FAILURE_MISSING_PHASE7_CHECKLIST,
        failure_reasons,
    )
    _check(
        checks,
        "phase9_scenario_scope",
        _scenario_in_scope(config, request),
        FAILURE_OUTSIDE_SANDBOX_SCOPE,
        failure_reasons,
        {"allowed_scenario_ids": list(config.allowed_scenario_ids)},
    )
    _check(
        checks,
        "sandbox_scope_limited",
        _sandbox_scope_limited(config, request),
        FAILURE_OUTSIDE_SANDBOX_SCOPE,
        failure_reasons,
    )
    _check(
        checks,
        "mock_approval_bound",
        _mock_approval_valid(config, request),
        FAILURE_MISSING_USER_APPROVAL,
        failure_reasons,
    )
    _check(
        checks,
        "mock_emergency_stop_inactive",
        _mock_emergency_stop_inactive(request.emergency_stop),
        FAILURE_EMERGENCY_STOP_ACTIVE,
        failure_reasons,
    )
    _check(
        checks,
        "mock_rollback_plan",
        _rollback_plan_present(request.rollback_plan),
        FAILURE_MISSING_ROLLBACK_PLAN,
        failure_reasons,
    )
    _check(
        checks,
        "real_action_future_gate",
        (not config.real_action_enabled) or config.future_real_action_gate_approved,
        FAILURE_REAL_ACTION_DISABLED,
        failure_reasons,
    )

    unique_reasons = _unique(failure_reasons)
    return {
        "passed": not unique_reasons,
        "failure_reasons": unique_reasons,
        "checks": checks,
        "phase7_validation": dict(phase7_validation),
    }


def run_phase9_experiment(
    config: Phase9ExperimentConfig | None = None,
    request: Phase9ExperimentRequest | None = None,
) -> Phase9ExperimentResult:
    """Run the Phase 9.1 harness as dry-run simulation only."""

    config = config or Phase9ExperimentConfig()
    request = request or Phase9ExperimentRequest()
    audit_events: list[dict[str, Any]] = []

    audit_events.append(_audit_event(EVENT_PHASE9_EXPERIMENT_REQUESTED, config, request, []))
    audit_events.append(_audit_event(EVENT_PHASE9_MOCK_APPROVAL_CHECKED, config, request, []))
    audit_events.append(_audit_event(EVENT_PHASE9_EMERGENCY_STOP_CHECKED, config, request, []))

    validation = validate_phase9_gate(config, request)
    failure_reasons = list(validation["failure_reasons"])
    blocker_codes = _readiness_blocker_codes(request.click_readiness)

    if not validation["passed"]:
        audit_events.append(
            _audit_event(EVENT_PHASE9_GATE_BLOCKED, config, request, failure_reasons)
        )
        real_action_skipped = FAILURE_REAL_ACTION_DISABLED in failure_reasons
        if real_action_skipped:
            audit_events.append(
                _audit_event(EVENT_PHASE9_REAL_ACTION_SKIPPED, config, request, failure_reasons)
            )
        return _result(
            config=config,
            request=request,
            status="real_action_skipped" if real_action_skipped else "blocked",
            gate_passed=False,
            failure_reasons=failure_reasons,
            blocker_codes=blocker_codes,
            audit_events=audit_events,
            validation=validation,
            real_action_skipped=real_action_skipped,
            post_action_verification_planned=False,
            rollback_plan_recorded=False,
        )

    audit_events.append(_audit_event(EVENT_PHASE9_GATE_PASSED, config, request, []))
    audit_events.append(
        _audit_event(EVENT_PHASE9_POST_ACTION_VERIFICATION_PLANNED, config, request, [])
    )
    audit_events.append(_audit_event(EVENT_PHASE9_ROLLBACK_PLAN_RECORDED, config, request, []))

    if config.dry_run:
        audit_events.append(_audit_event(EVENT_PHASE9_DRY_RUN_COMPLETED, config, request, []))
        return _result(
            config=config,
            request=request,
            status="dry_run_completed",
            gate_passed=True,
            failure_reasons=[],
            blocker_codes=blocker_codes,
            audit_events=audit_events,
            validation=validation,
            real_action_skipped=False,
            post_action_verification_planned=True,
            rollback_plan_recorded=True,
        )

    failure_reasons = [FAILURE_REAL_ACTION_DISABLED]
    audit_events.append(
        _audit_event(EVENT_PHASE9_REAL_ACTION_SKIPPED, config, request, failure_reasons)
    )
    return _result(
        config=config,
        request=request,
        status="real_action_skipped",
        gate_passed=True,
        failure_reasons=failure_reasons,
        blocker_codes=blocker_codes,
        audit_events=audit_events,
        validation=validation,
        real_action_skipped=True,
        post_action_verification_planned=True,
        rollback_plan_recorded=True,
    )


def build_phase9_experiment_report(results: list[Phase9ExperimentResult]) -> dict[str, Any]:
    """Build a Phase 8-shaped report from deterministic Phase 9.1 results."""

    scenarios = [result.to_dict() for result in results]
    failed = [scenario for scenario in scenarios if not scenario["passed"]]
    return {
        "report_type": "phase9_minimal_sandbox_experiment",
        "phase": "phase9_1",
        "source": "phase9_experiment_harness",
        "external_llm_calls": False,
        "real_desktop_actions": False,
        "scenario_count": len(scenarios),
        "scenario_ids": [scenario["scenario_id"] for scenario in scenarios],
        "summary": {
            "total_scenario_count": len(scenarios),
            "passed_scenario_count": len(scenarios) - len(failed),
            "failed_scenario_count": len(failed),
            "scenarios_with_failures": [scenario["scenario_id"] for scenario in failed],
            "all_expected_outcomes_passed": not failed,
            "gate_passed_count": sum(1 for scenario in scenarios if scenario["gate_passed"]),
            "gate_blocked_count": sum(1 for scenario in scenarios if not scenario["gate_passed"]),
            "dry_run_scenario_count": sum(1 for scenario in scenarios if scenario["dry_run"]),
            "real_action_enabled_count": sum(
                1 for scenario in scenarios if scenario["real_action_enabled"]
            ),
            "real_action_skipped_count": sum(
                1 for scenario in scenarios if scenario["real_action_skipped"]
            ),
            "real_action_attempted_count": sum(
                1 for scenario in scenarios if scenario["actual_outcome"]["real_action_attempted"]
            ),
            "post_action_verification_planned_count": sum(
                1 for scenario in scenarios if scenario["post_action_verification_planned"]
            ),
        },
        "report_notes": [
            "Phase 9.1 executes only deterministic dry-run simulation.",
            "The harness is not execution permission.",
            "No scenario observes the live desktop or calls an execution path.",
        ],
        "scenarios": scenarios,
    }


def _phase8_config(
    config: Phase9ExperimentConfig,
    request: Phase9ExperimentRequest,
) -> SandboxExperimentConfig:
    emergency_stop = request.emergency_stop
    return SandboxExperimentConfig(
        experiment_name=config.experiment_id,
        dry_run=config.dry_run,
        real_action_enabled=config.real_action_enabled,
        allowed_action_type=config.allowed_action_type,
        allowed_window_id=config.allowed_window_id,
        allowed_target_id=config.allowed_target_id,
        max_observation_age_seconds=config.max_observation_age_seconds,
        phase7_checklist=dict(config.phase7_checklist),
        expected_readiness_blocker_codes=tuple(config.expected_readiness_blocker_codes),
        forbidden_action_types=tuple(config.forbidden_action_types),
        emergency_stop_available=bool(emergency_stop and emergency_stop.available),
        emergency_stop_active=bool(emergency_stop and emergency_stop.active),
        audit_events_required=config.audit_plan_present,
    )


def _phase8_request(
    config: Phase9ExperimentConfig,
    request: Phase9ExperimentRequest,
) -> SandboxExperimentRequest:
    return SandboxExperimentRequest(
        user_approved=_mock_approval_valid(config, request),
        action_contract=request.action_contract,
        click_readiness=request.click_readiness,
        visible_elements=list(request.visible_elements),
        safety_decision=request.safety_decision,
        screen=request.screen,
        observation_timestamp=request.observation_timestamp,
        post_action_verification_plan=_phase8_verification_plan(
            request.post_action_verification_plan
        ),
        sandbox_window_id=request.sandbox_window_id or _scope_string(request.sandbox_scope, "window_id"),
        current_time=request.current_time,
        audit_context={
            **dict(request.audit_context),
            "scenario_id": request.scenario_id,
            "experiment_id": config.experiment_id,
        },
    )


def _phase8_verification_plan(
    plan: MockPostActionVerificationPlan | None,
) -> dict[str, Any] | None:
    if plan is None or not plan.present:
        return None
    return {
        "enabled": bool(plan.planned and plan.simulated),
        "method": plan.method,
        "expected_state_change": plan.expected_state_change,
        "observed_state_change": plan.observed_state_change,
        "passed": plan.passed,
    }


def _result(
    *,
    config: Phase9ExperimentConfig,
    request: Phase9ExperimentRequest,
    status: str,
    gate_passed: bool,
    failure_reasons: list[str],
    blocker_codes: list[str],
    audit_events: list[dict[str, Any]],
    validation: dict[str, Any],
    real_action_skipped: bool,
    post_action_verification_planned: bool,
    rollback_plan_recorded: bool,
) -> Phase9ExperimentResult:
    return Phase9ExperimentResult(
        experiment_id=config.experiment_id,
        scenario_id=request.scenario_id,
        scenario_name=request.scenario_name,
        expected_outcome=dict(request.expected_outcome),
        status=status,
        gate_passed=gate_passed,
        dry_run=config.dry_run,
        real_action_enabled=config.real_action_enabled,
        simulated=True,
        real_action_attempted=False,
        real_action_skipped=real_action_skipped,
        failure_reason_codes=_unique(failure_reasons),
        blocker_codes=blocker_codes,
        audit_events=audit_events,
        validation=validation,
        post_action_verification_planned=post_action_verification_planned,
        rollback_plan_recorded=rollback_plan_recorded,
        target_risk_hint=_target_risk_hint(request),
        target_confidence=_target_confidence(request),
        readiness_ready=_readiness_ready(request.click_readiness),
        action_type=_action_type(request),
        notes=list(request.notes),
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


def _scenario_in_scope(config: Phase9ExperimentConfig, request: Phase9ExperimentRequest) -> bool:
    return bool(request.scenario_id) and request.scenario_id in config.allowed_scenario_ids


def _sandbox_scope_limited(
    config: Phase9ExperimentConfig,
    request: Phase9ExperimentRequest,
) -> bool:
    scope = request.sandbox_scope
    if not isinstance(scope, dict):
        return False
    if _scope_string(scope, "window_id") != config.allowed_window_id:
        return False
    if _scope_string(scope, "target_id") != config.allowed_target_id:
        return False
    if scope.get("one_window_only") is not True:
        return False
    if scope.get("one_target_only") is not True:
        return False
    forbidden_flags = (
        "system_settings_allowed",
        "file_deletion_allowed",
        "shell_execution_allowed",
        "browser_credentials_allowed",
        "external_websites_allowed",
        "destructive_actions_allowed",
        "hidden_background_actions_allowed",
    )
    return not any(scope.get(flag) is True for flag in forbidden_flags)


def _mock_approval_valid(
    config: Phase9ExperimentConfig,
    request: Phase9ExperimentRequest,
) -> bool:
    approval = request.approval
    contract = request.action_contract if isinstance(request.action_contract, dict) else {}
    if approval is None or not approval.present or not approval.user_approved:
        return False
    if approval.action_contract_id != str(contract.get("action_id") or ""):
        return False
    if approval.target_id != str(contract.get("target_element_id") or ""):
        return False
    if approval.observation_id and approval.observation_id != request.observation_id:
        return False
    if _approval_expired(approval, request.current_time):
        return False
    return bool(config.experiment_id)


def _approval_expired(approval: MockApprovalState, current_time: datetime | None) -> bool:
    if not approval.expires_at:
        return True
    expires_at = _parse_iso8601(approval.expires_at)
    if expires_at is None:
        return True
    now = current_time or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return expires_at <= now


def _mock_emergency_stop_inactive(stop: MockEmergencyStopState | None) -> bool:
    if stop is None or not stop.available:
        return True
    return not stop.active


def _rollback_plan_present(plan: MockRollbackPlan | None) -> bool:
    if plan is None:
        return False
    return bool(plan.present and plan.simulated and plan.sandbox_only and plan.strategy.strip())


def _audit_event(
    event_type: str,
    config: Phase9ExperimentConfig,
    request: Phase9ExperimentRequest,
    failure_reason_codes: list[str],
) -> dict[str, Any]:
    timestamp = request.current_time or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return {
        "type": event_type,
        "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
        "phase": "phase9_1_minimal_sandbox_experiment",
        "experiment_id": config.experiment_id,
        "scenario_id": request.scenario_id,
        "scenario_name": request.scenario_name,
        "expected_outcome": dict(request.expected_outcome),
        "failure_reason_codes": list(failure_reason_codes),
        "blocker_codes": _readiness_blocker_codes(request.click_readiness),
        "dry_run": config.dry_run,
        "real_action_enabled": config.real_action_enabled,
        "target_risk_hint": _target_risk_hint(request),
        "target_confidence": _target_confidence(request),
        "readiness_ready": _readiness_ready(request.click_readiness),
        "action_type": _action_type(request),
        "sandbox_scope": dict(request.sandbox_scope),
    }


def _readiness_blocker_codes(readiness: dict[str, Any] | None) -> list[str]:
    if not isinstance(readiness, dict):
        return []
    codes = readiness.get("blocker_codes")
    if not isinstance(codes, list):
        return []
    return [str(code) for code in codes if str(code)]


def _target_risk_hint(request: Phase9ExperimentRequest) -> str:
    contract = request.action_contract if isinstance(request.action_contract, dict) else {}
    risk_hint = str(contract.get("target_risk_hint") or "").strip()
    if risk_hint:
        return risk_hint
    for element in request.visible_elements:
        if isinstance(element, dict):
            return str(element.get("risk_hint") or "").strip()
    return ""


def _target_confidence(request: Phase9ExperimentRequest) -> float | None:
    contract = request.action_contract if isinstance(request.action_contract, dict) else {}
    value = _finite_float(contract.get("target_confidence"))
    if value is not None:
        return value
    for element in request.visible_elements:
        if isinstance(element, dict):
            return _finite_float(element.get("confidence"))
    return None


def _action_type(request: Phase9ExperimentRequest) -> str:
    contract = request.action_contract if isinstance(request.action_contract, dict) else {}
    return str(contract.get("type") or "")


def _readiness_ready(readiness: dict[str, Any] | None) -> bool:
    return bool(isinstance(readiness, dict) and readiness.get("ready") is True)


def _finite_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number


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


def _scope_string(scope: dict[str, Any], key: str) -> str:
    if not isinstance(scope, dict):
        return ""
    return str(scope.get(key) or "").strip()


def _validation_checks(validation: dict[str, Any]) -> list[dict[str, Any]]:
    checks = validation.get("checks")
    if not isinstance(checks, list):
        return []
    return [
        {
            "name": str(check.get("name") or ""),
            "passed": bool(check.get("passed")),
            "failure_reason": str(check.get("failure_reason") or ""),
        }
        for check in checks
        if isinstance(check, dict)
    ]


def _expectation_matches(expected: dict[str, Any], actual: dict[str, Any]) -> bool:
    if not expected:
        return True
    for key, value in expected.items():
        if actual.get(key) != value:
            return False
    return actual.get("real_action_attempted") is False


def _unique(values: list[str]) -> list[str]:
    unique_values: list[str] = []
    for value in values:
        if value not in unique_values:
            unique_values.append(value)
    return unique_values
