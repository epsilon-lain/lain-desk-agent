"""Phase 9.1 dry-run-only minimal sandbox experiment harness.

The harness executes the Phase 9 experiment specification as deterministic
fixture simulation. It reuses the Phase 8 sandbox gate for Phase 7 checks,
adds mock approval, emergency stop, verification, and rollback requirements,
and never performs desktop actuation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from .sandbox_experiment import (
    DEFAULT_MAX_OBSERVATION_AGE_SECONDS,
    FAILURE_HIGH_RISK_TARGET,
    FAILURE_MISSING_ACTION_CONTRACT,
    FAILURE_MISSING_AUDIT_PLAN,
    FAILURE_MISSING_PHASE7_CHECKLIST,
    FAILURE_MISSING_USER_APPROVAL,
    FAILURE_OUTSIDE_SANDBOX_SCOPE,
    FAILURE_REAL_ACTION_DISABLED,
    FAILURE_STALE_OBSERVATION,
    FORBIDDEN_ACTION_TYPES,
    REQUIRED_PHASE7_CHECKLIST_ITEMS,
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
    "experiment_id",
    "experiment_name",
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
    "mock_approval_checked",
    "user_approval_present",
    "emergency_stop_available",
    "emergency_stop_active",
    "post_action_verification_planned",
    "rollback_plan_recorded",
    "target_risk_hint",
    "target_confidence",
    "readiness_ready",
    "action_type",
    "sandbox_scope",
    "notes",
    "trace",
)

DEFAULT_ALLOWED_WINDOW_ID = "sandbox_window"
DEFAULT_ALLOWED_TARGET_ID = "sandbox_target_button"
DEFAULT_ALLOWED_ACTION_TYPE = "click"
PHASE9_DEMO_NOW = datetime(2026, 1, 1, 0, 0, 5, tzinfo=timezone.utc)
PHASE9_DEMO_OBSERVATION_TIMESTAMP = "2026-01-01T00:00:00Z"
PHASE9_DEMO_OBSERVATION_ID = "phase9_observation_0001"
PHASE9_DEMO_ACTION_ID = "phase9_sandbox_action_0001"
PHASE9_EXPORT_REPORT_VERSION = "phase9_export_v1"
PHASE9_EXPORT_GENERATED_AT = "deterministic_phase9_fixture"
PHASE9_EXPORT_PROJECT_PHASE = "phase_9_4"
PHASE9_EXPORT_BUNDLE_VERSION = "phase9_repro_bundle_v1"
PHASE9_REPLAY_PROJECT_PHASE = "phase_9_5"
PHASE9_REPLAY_REPORT_VERSION = "phase9_replay_v1"
PHASE9_EXPORT_SAFETY_BOUNDARY = (
    "Phase 9.4 exports deterministic dry-run debug data only. Real desktop "
    "actions remain disabled, and no action-performing endpoint is called."
)
_SENSITIVE_KEY_FRAGMENTS = (
    "token",
    "secret",
    "api_key",
    "apikey",
    "password",
    "credential",
    "private_key",
    "access_key",
    "environment",
    "env_var",
)
PHASE9_BUNDLE_REQUIRED_FIELDS = (
    "bundle_type",
    "bundle_version",
    "report_version",
    "project_phase",
    "phase9_report",
    "ai_readable_summary",
    "minimal_reproduction_metadata",
    "safety_boundary_statement",
)
PHASE9_BUNDLE_METADATA_REQUIRED_FIELDS = (
    "scenario_ids",
    "experiment_id",
    "audit_event_order",
    "failure_reason_codes",
    "blocker_codes",
)
PHASE9_IMPORTED_REPORT_REQUIRED_FIELDS = (
    "experiment_id",
    "dry_run",
    "real_action_enabled",
    "real_action_skipped",
    "gate_passed",
    "actual_outcome",
    "failure_reason_codes",
    "blocker_codes",
    "audit_event_names",
    "audit_timeline",
    "sandbox_scope",
    "action_type",
    "target_risk_hint",
    "target_confidence",
    "readiness_ready",
    "user_approval_present",
    "emergency_stop_available",
    "post_action_verification_planned",
    "rollback_plan_recorded",
)


class UnknownPhase9ExperimentScenarioError(ValueError):
    """Raised when a requested built-in Phase 9 scenario does not exist."""


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
    sandbox_scope: dict[str, Any]
    user_approval_present: bool
    emergency_stop_available: bool
    emergency_stop_active: bool
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
            "experiment_name": self.experiment_id,
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
            "mock_approval_checked": EVENT_PHASE9_MOCK_APPROVAL_CHECKED in self.audit_event_names(),
            "user_approval_present": self.user_approval_present,
            "emergency_stop_available": self.emergency_stop_available,
            "emergency_stop_active": self.emergency_stop_active,
            "post_action_verification_planned": self.post_action_verification_planned,
            "rollback_plan_recorded": self.rollback_plan_recorded,
            "target_risk_hint": self.target_risk_hint,
            "target_confidence": self.target_confidence,
            "readiness_ready": self.readiness_ready,
            "action_type": self.action_type,
            "sandbox_scope": dict(self.sandbox_scope),
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
            "mock_approval_checked": EVENT_PHASE9_MOCK_APPROVAL_CHECKED in self.audit_event_names(),
            "user_approval_present": self.user_approval_present,
            "emergency_stop_available": self.emergency_stop_available,
            "emergency_stop_active": self.emergency_stop_active,
            "failure_reason_codes": list(self.failure_reason_codes),
            "blocker_codes": list(self.blocker_codes),
            "audit_event_names": self.audit_event_names(),
            "post_action_verification_planned": self.post_action_verification_planned,
            "rollback_plan_recorded": self.rollback_plan_recorded,
            "sandbox_scope": dict(self.sandbox_scope),
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
    report = {
        "report_type": "phase9_minimal_sandbox_experiment",
        "phase": "phase9_1",
        "cockpit_exposure_phase": "phase9_2",
        "export_phase": PHASE9_EXPORT_PROJECT_PHASE,
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
            "Phase 9.2 exposes this harness report in the cockpit as read-only debug output.",
            "The harness is not execution permission.",
            "No scenario observes the live desktop or calls an execution path.",
        ],
        "scenarios": scenarios,
    }
    report["phase9_export_bundle"] = build_phase9_reproducibility_bundle(report)
    return report


def build_phase9_export_report(report: dict[str, Any]) -> dict[str, Any]:
    """Return a stable Phase 9.4 export view derived from the cockpit report."""

    source_report = report if isinstance(report, dict) else {}
    scenarios = [
        _phase9_export_scenario(scenario)
        for scenario in source_report.get("scenarios", [])
        if isinstance(scenario, dict)
    ]
    audit_timeline = _phase9_audit_timeline(scenarios)
    failure_reason_codes = _unique(
        [
            code
            for scenario in scenarios
            for code in _string_list(scenario.get("failure_reason_codes"))
        ]
    )
    blocker_codes = _unique(
        [code for scenario in scenarios for code in _string_list(scenario.get("blocker_codes"))]
    )
    audit_event_names = _unique(
        [
            event_name
            for scenario in scenarios
            for event_name in _string_list(scenario.get("audit_event_names"))
        ]
    )
    summary = source_report.get("summary") if isinstance(source_report.get("summary"), dict) else {}

    export_report = {
        "report_version": PHASE9_EXPORT_REPORT_VERSION,
        "generated_at": PHASE9_EXPORT_GENERATED_AT,
        "project_phase": PHASE9_EXPORT_PROJECT_PHASE,
        "source_report_type": source_report.get("report_type", "phase9_minimal_sandbox_experiment"),
        "source_phase": source_report.get("phase", "phase9_1"),
        "dry_run": not any(
            isinstance(scenario.get("actual_outcome"), dict)
            and scenario["actual_outcome"].get("real_action_attempted") is True
            for scenario in scenarios
        ),
        "real_action_enabled": any(
            scenario.get("real_action_enabled") is True for scenario in scenarios
        ),
        "real_action_skipped": any(
            scenario.get("real_action_skipped") is True for scenario in scenarios
        ),
        "experiment_id": _common_or_mixed(
            [str(scenario.get("experiment_id") or "") for scenario in scenarios]
        ),
        "scenario_ids": [str(scenario.get("scenario_id") or "") for scenario in scenarios],
        "sandbox_scope": _common_scope(scenarios),
        "action_type": _common_or_mixed(
            [str(scenario.get("action_type") or "") for scenario in scenarios]
        ),
        "gate_passed": all(scenario.get("gate_passed") is True for scenario in scenarios),
        "actual_outcome": {
            "status": _aggregate_status(summary, scenarios),
            "scenario_count": len(scenarios),
            "gate_passed_count": int(summary.get("gate_passed_count") or 0),
            "gate_blocked_count": int(summary.get("gate_blocked_count") or 0),
            "real_action_attempted": False,
        },
        "failure_reason_codes": failure_reason_codes,
        "blocker_codes": blocker_codes,
        "target_risk_hint": _common_or_mixed(
            [str(scenario.get("target_risk_hint") or "") for scenario in scenarios]
        ),
        "target_confidence": _common_number(
            [scenario.get("target_confidence") for scenario in scenarios]
        ),
        "readiness_ready": all(scenario.get("readiness_ready") is True for scenario in scenarios),
        "user_approval_present": all(
            scenario.get("user_approval_present") is True for scenario in scenarios
        ),
        "emergency_stop_available": all(
            scenario.get("emergency_stop_available") is True for scenario in scenarios
        ),
        "post_action_verification_planned": all(
            scenario.get("post_action_verification_planned") is True for scenario in scenarios
        ),
        "rollback_plan_recorded": all(
            scenario.get("rollback_plan_recorded") is True for scenario in scenarios
        ),
        "audit_event_names": audit_event_names,
        "audit_timeline": audit_timeline,
        "notes": _unique(
            [
                note
                for scenario in scenarios
                for note in _string_list(scenario.get("notes"))
            ]
        ),
        "scenarios": scenarios,
    }
    return _sanitize_export_value(export_report)


def build_phase9_ai_readable_summary(export_report: dict[str, Any]) -> str:
    """Build a concise handoff summary for AI/debug review."""

    report = export_report if isinstance(export_report, dict) else {}
    actual_outcome = report.get("actual_outcome") if isinstance(report.get("actual_outcome"), dict) else {}
    failure_reason_codes = _string_list(report.get("failure_reason_codes"))
    blocker_codes = _string_list(report.get("blocker_codes"))
    gate = "passed" if report.get("gate_passed") is True else "blocked or mixed"
    dry_run = "yes" if report.get("dry_run") is True else "mixed"
    real_action_enabled = "yes" if report.get("real_action_enabled") is True else "no"
    real_action_skipped = "yes" if report.get("real_action_skipped") is True else "no"

    lines = [
        "Project phase: phase_9_4 Phase 9 dry-run harness export.",
        f"Run mode: dry_run={dry_run}; real_action_enabled={real_action_enabled}; real_action_skipped={real_action_skipped}.",
        (
            f"Gate result: {gate}; status={actual_outcome.get('status', 'unknown')}; "
            f"scenarios={actual_outcome.get('scenario_count', 0)}; "
            f"passed={actual_outcome.get('gate_passed_count', 0)}; "
            f"blocked={actual_outcome.get('gate_blocked_count', 0)}."
        ),
        (
            "Blockers/failure reasons: "
            f"failure_reason_codes={_format_codes(failure_reason_codes)}; "
            f"blocker_codes={_format_codes(blocker_codes)}."
        ),
        (
            "Gate support state: "
            f"approval_present={_yes_no(report.get('user_approval_present'))}; "
            f"emergency_stop_available={_yes_no(report.get('emergency_stop_available'))}; "
            f"verification_planned={_yes_no(report.get('post_action_verification_planned'))}; "
            f"rollback_recorded={_yes_no(report.get('rollback_plan_recorded'))}."
        ),
        f"Recommended next debugging focus: {_phase9_recommended_focus(report)}.",
        f"Safety boundary: {PHASE9_EXPORT_SAFETY_BOUNDARY}",
    ]
    return "\n".join(lines)


def build_phase9_reproducibility_bundle(report: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic, read-only bundle for handoff and reproduction."""

    export_report = build_phase9_export_report(report)
    bundle = {
        "bundle_type": "phase9_reproducibility_bundle",
        "bundle_version": PHASE9_EXPORT_BUNDLE_VERSION,
        "report_version": PHASE9_EXPORT_REPORT_VERSION,
        "generated_at": PHASE9_EXPORT_GENERATED_AT,
        "project_phase": PHASE9_EXPORT_PROJECT_PHASE,
        "phase9_report": export_report,
        "ai_readable_summary": build_phase9_ai_readable_summary(export_report),
        "minimal_reproduction_metadata": {
            "scenario_ids": list(export_report["scenario_ids"]),
            "experiment_id": export_report["experiment_id"],
            "stable_input_assumptions": [
                "fixture-backed Phase 9 harness data",
                "normalized visible element target data only",
                "mock approval, emergency stop, verification, and rollback state",
                "no live OS state or real desktop screenshots",
            ],
            "audit_event_order": list(export_report["audit_timeline"]),
            "failure_reason_codes": list(export_report["failure_reason_codes"]),
            "blocker_codes": list(export_report["blocker_codes"]),
            "excluded_material": [
                "private auth material",
                "live OS state",
                "full local filesystem dumps",
                "real desktop screenshots outside deterministic fixtures",
            ],
        },
        "safety_boundary_statement": PHASE9_EXPORT_SAFETY_BOUNDARY,
    }
    return _sanitize_export_value(bundle)


def validate_phase9_reproducibility_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    """Validate a Phase 9.4 bundle before read-only Phase 9.5 replay.

    Validation is deliberately conservative. It only inspects the provided
    object, rejects suspicious sensitive-key names, and refuses bundles that
    claim real action is enabled or that do not remain dry-run safe.
    """

    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    if not isinstance(bundle, dict):
        _phase9_validation_error(
            errors,
            "missing_bundle_field",
            "bundle",
            "Bundle must be a JSON object.",
        )
        return _phase9_bundle_validation_result(bundle, errors, warnings)

    for field_name in PHASE9_BUNDLE_REQUIRED_FIELDS:
        if field_name not in bundle:
            _phase9_validation_error(
                errors,
                "missing_bundle_field",
                field_name,
                "Required top-level bundle field is missing.",
            )

    sensitive_paths = _phase9_sensitive_key_paths(bundle)
    if sensitive_paths:
        _phase9_validation_error(
            errors,
            "suspicious_sensitive_key",
            ", ".join(sensitive_paths[:5]),
            "Bundle contains key names that look like private material.",
        )

    bundle_version = str(bundle.get("bundle_version") or "")
    if bundle_version and bundle_version != PHASE9_EXPORT_BUNDLE_VERSION:
        _phase9_validation_error(
            errors,
            "unsupported_bundle_version",
            "bundle_version",
            f"Unsupported bundle version: {bundle_version}.",
        )

    phase9_report = bundle.get("phase9_report")
    if not isinstance(phase9_report, dict):
        _phase9_validation_error(
            errors,
            "missing_phase9_report",
            "phase9_report",
            "Bundle must contain a Phase 9 export report object.",
        )
        return _phase9_bundle_validation_result(bundle, errors, warnings)

    report_version = str(bundle.get("report_version") or "")
    if report_version != PHASE9_EXPORT_REPORT_VERSION:
        _phase9_validation_error(
            errors,
            "invalid_report_version",
            "report_version",
            f"Expected {PHASE9_EXPORT_REPORT_VERSION}.",
        )

    nested_report_version = str(phase9_report.get("report_version") or "")
    if nested_report_version != PHASE9_EXPORT_REPORT_VERSION:
        _phase9_validation_error(
            errors,
            "invalid_report_version",
            "phase9_report.report_version",
            f"Expected {PHASE9_EXPORT_REPORT_VERSION}.",
        )

    for field_name in PHASE9_IMPORTED_REPORT_REQUIRED_FIELDS:
        if field_name not in phase9_report:
            _phase9_validation_error(
                errors,
                "missing_bundle_field",
                f"phase9_report.{field_name}",
                "Required Phase 9 report field is missing.",
            )

    if phase9_report.get("real_action_enabled") is True or _phase9_nested_true(
        phase9_report, "real_action_enabled"
    ):
        _phase9_validation_error(
            errors,
            "real_action_enabled_in_bundle",
            "phase9_report.real_action_enabled",
            "Imported bundles must keep real action disabled.",
        )

    actual_outcome = phase9_report.get("actual_outcome")
    if (
        phase9_report.get("dry_run") is not True
        or (isinstance(actual_outcome, dict) and actual_outcome.get("real_action_attempted") is True)
        or _phase9_nested_true(phase9_report, "real_action_attempted")
    ):
        _phase9_validation_error(
            errors,
            "non_dry_run_bundle",
            "phase9_report.dry_run",
            "Imported bundles must remain dry-run and never show real action attempted.",
        )

    if not _is_string_list(phase9_report.get("failure_reason_codes")):
        _phase9_validation_error(
            errors,
            "malformed_blocker_codes",
            "phase9_report.failure_reason_codes",
            "Failure reason codes must be a list of strings.",
        )
    if not _is_string_list(phase9_report.get("blocker_codes")):
        _phase9_validation_error(
            errors,
            "malformed_blocker_codes",
            "phase9_report.blocker_codes",
            "Blocker codes must be a list of strings.",
        )
    if not _is_string_list(phase9_report.get("audit_event_names")):
        _phase9_validation_error(
            errors,
            "malformed_audit_event",
            "phase9_report.audit_event_names",
            "Audit event names must be a list of strings.",
        )

    audit_timeline = phase9_report.get("audit_timeline")
    if not isinstance(audit_timeline, list) or not audit_timeline:
        _phase9_validation_error(
            errors,
            "missing_audit_timeline",
            "phase9_report.audit_timeline",
            "Phase 9 replay requires a non-empty audit timeline.",
        )
    else:
        _validate_phase9_audit_timeline(audit_timeline, errors)

    metadata = bundle.get("minimal_reproduction_metadata")
    if not isinstance(metadata, dict):
        _phase9_validation_error(
            errors,
            "missing_bundle_field",
            "minimal_reproduction_metadata",
            "Minimal reproduction metadata must be an object.",
        )
    else:
        _validate_phase9_minimal_reproduction_metadata(metadata, phase9_report, errors)

    safety_boundary = bundle.get("safety_boundary_statement")
    if not isinstance(safety_boundary, str) or not safety_boundary.strip():
        _phase9_validation_error(
            errors,
            "missing_safety_boundary_statement",
            "safety_boundary_statement",
            "Bundle must include the Phase 9 safety boundary statement.",
        )

    return _phase9_bundle_validation_result(bundle, errors, warnings)


def import_phase9_reproducibility_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    """Import a Phase 9.4 bundle into a read-only replay-ready structure."""

    validation = validate_phase9_reproducibility_bundle(bundle)
    phase9_report = (
        _sanitize_export_value(bundle.get("phase9_report"))
        if validation["valid"] and isinstance(bundle, dict)
        else {}
    )
    return {
        "import_status": "imported" if validation["valid"] else "blocked",
        "valid": validation["valid"],
        "validation": validation,
        "bundle_version": validation.get("bundle_version", ""),
        "report_version": validation.get("report_version", ""),
        "phase9_report": phase9_report,
        "safety_boundary_statement": (
            str(bundle.get("safety_boundary_statement") or "") if isinstance(bundle, dict) else ""
        ),
    }


def replay_phase9_reproducibility_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    """Replay a Phase 9.4 bundle as deterministic, read-only debug output."""

    return build_phase9_replay_report(bundle)


def build_phase9_replay_report(bundle: dict[str, Any]) -> dict[str, Any]:
    """Build the Phase 9.5 replay report without executing or mutating state."""

    imported = import_phase9_reproducibility_bundle(bundle)
    validation = imported["validation"]
    phase9_report = imported["phase9_report"] if validation["valid"] else {}
    audit_timeline = (
        _sanitize_export_value(phase9_report.get("audit_timeline"))
        if isinstance(phase9_report.get("audit_timeline"), list)
        else []
    )
    safety_boundary = imported.get("safety_boundary_statement", "")
    safety_confirmed = validation["valid"] and bool(str(safety_boundary).strip())

    return {
        "report_version": PHASE9_REPLAY_REPORT_VERSION,
        "generated_at": PHASE9_EXPORT_GENERATED_AT,
        "project_phase": PHASE9_REPLAY_PROJECT_PHASE,
        "source_bundle_version": validation.get("bundle_version", ""),
        "source_report_version": validation.get("report_version", ""),
        "replay_status": "replayed" if validation["valid"] else "blocked",
        "validation": validation,
        "original_experiment_id": str(phase9_report.get("experiment_id") or ""),
        "original_gate_passed": phase9_report.get("gate_passed") if validation["valid"] else None,
        "original_actual_outcome": (
            _sanitize_export_value(phase9_report.get("actual_outcome"))
            if isinstance(phase9_report.get("actual_outcome"), dict)
            else {}
        ),
        "original_failure_reason_codes": _string_list(phase9_report.get("failure_reason_codes")),
        "original_blocker_codes": _string_list(phase9_report.get("blocker_codes")),
        "original_audit_event_names": _string_list(phase9_report.get("audit_event_names")),
        "replayed_audit_timeline": audit_timeline,
        "replay_notes": _phase9_replay_notes(validation),
        "safety_boundary_confirmed": safety_confirmed,
        "safety_boundary_statement": safety_boundary,
        "dry_run": phase9_report.get("dry_run") if validation["valid"] else None,
        "real_action_enabled": (
            phase9_report.get("real_action_enabled") if validation["valid"] else None
        ),
        "real_action_skipped": (
            phase9_report.get("real_action_skipped") if validation["valid"] else None
        ),
    }


def _phase9_export_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    actual_outcome = (
        scenario.get("actual_outcome") if isinstance(scenario.get("actual_outcome"), dict) else {}
    )
    export_scenario = {
        "report_version": PHASE9_EXPORT_REPORT_VERSION,
        "generated_at": PHASE9_EXPORT_GENERATED_AT,
        "project_phase": PHASE9_EXPORT_PROJECT_PHASE,
        "experiment_id": str(scenario.get("experiment_id") or ""),
        "scenario_id": str(scenario.get("scenario_id") or ""),
        "scenario_name": str(scenario.get("scenario_name") or ""),
        "dry_run": bool(scenario.get("dry_run") is True),
        "real_action_enabled": bool(scenario.get("real_action_enabled") is True),
        "real_action_skipped": bool(scenario.get("real_action_skipped") is True),
        "sandbox_scope": _sanitize_export_value(scenario.get("sandbox_scope") or {}),
        "action_type": str(scenario.get("action_type") or ""),
        "gate_passed": bool(scenario.get("gate_passed") is True),
        "actual_outcome": _sanitize_export_value(actual_outcome),
        "failure_reason_codes": _string_list(scenario.get("failure_reason_codes")),
        "blocker_codes": _string_list(scenario.get("blocker_codes")),
        "target_risk_hint": str(scenario.get("target_risk_hint") or ""),
        "target_confidence": _finite_float(scenario.get("target_confidence")),
        "readiness_ready": bool(scenario.get("readiness_ready") is True),
        "user_approval_present": bool(scenario.get("user_approval_present") is True),
        "emergency_stop_available": bool(scenario.get("emergency_stop_available") is True),
        "post_action_verification_planned": bool(
            scenario.get("post_action_verification_planned") is True
        ),
        "rollback_plan_recorded": bool(scenario.get("rollback_plan_recorded") is True),
        "audit_event_names": _string_list(scenario.get("audit_event_names")),
        "audit_timeline": _phase9_scenario_audit_timeline(scenario),
        "notes": _string_list(scenario.get("notes")),
    }
    return _sanitize_export_value(export_scenario)


def _phase9_scenario_audit_timeline(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "order": index + 1,
            "scenario_id": str(scenario.get("scenario_id") or ""),
            "event_name": event_name,
            "gate_passed": bool(scenario.get("gate_passed") is True),
            "failure_reason_codes": _string_list(scenario.get("failure_reason_codes")),
            "blocker_codes": _string_list(scenario.get("blocker_codes")),
        }
        for index, event_name in enumerate(_string_list(scenario.get("audit_event_names")))
    ]


def _phase9_audit_timeline(scenarios: list[dict[str, Any]]) -> list[dict[str, Any]]:
    timeline: list[dict[str, Any]] = []
    order = 0
    for scenario in scenarios:
        for event in scenario.get("audit_timeline", []):
            if not isinstance(event, dict):
                continue
            order += 1
            timeline.append(
                {
                    **event,
                    "global_order": order,
                    "scenario_order": int(event.get("order") or 0),
                }
            )
    return timeline


def _aggregate_status(summary: dict[str, Any], scenarios: list[dict[str, Any]]) -> str:
    if not scenarios:
        return "empty"
    if summary.get("all_expected_outcomes_passed") is not True:
        return "failed_expectation"
    if any(scenario.get("real_action_skipped") is True for scenario in scenarios):
        return "dry_run_with_skipped_paths"
    if all(scenario.get("gate_passed") is True for scenario in scenarios):
        return "all_gates_passed"
    return "mixed_gate_results"


def _common_or_mixed(values: list[str]) -> str:
    present_values = [value for value in values if value]
    if not present_values:
        return ""
    first_value = present_values[0]
    return first_value if all(value == first_value for value in present_values) else "mixed"


def _common_scope(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    scopes = [
        scenario.get("sandbox_scope")
        for scenario in scenarios
        if isinstance(scenario.get("sandbox_scope"), dict)
    ]
    if not scopes:
        return {}
    first_scope = scopes[0]
    if all(scope == first_scope for scope in scopes):
        return _sanitize_export_value(first_scope)
    return {"scope": "mixed"}


def _common_number(values: list[Any]) -> float | None:
    numbers = [_finite_float(value) for value in values]
    present_numbers = [number for number in numbers if number is not None]
    if not present_numbers:
        return None
    first_number = present_numbers[0]
    return first_number if all(number == first_number for number in present_numbers) else None


def _phase9_recommended_focus(report: dict[str, Any]) -> str:
    codes = set(_string_list(report.get("failure_reason_codes")))
    codes.update(_string_list(report.get("blocker_codes")))
    focus: list[str] = []

    focus_rules = [
        ("missing_action_contract", "inspect action-contract fixture generation"),
        ("missing_audit_plan", "inspect audit-plan fixture coverage"),
        ("missing_user_approval", "inspect mock approval binding and freshness"),
        ("stale_observation", "inspect observation freshness assumptions"),
        ("high_risk_target", "inspect risk classification and target selection"),
        ("high_risk_requires_approval", "inspect high-risk blocker mapping"),
        ("real_action_disabled", "confirm skipped-path reporting remains explicit"),
        ("readiness_not_ready", "inspect readiness blocker expectations"),
    ]
    for code, recommendation in focus_rules:
        if code in codes:
            focus.append(recommendation)

    if not focus and report.get("gate_passed") is True:
        return "review successful dry-run audit order before any future design change"
    if not focus:
        return "review gate status, failure codes, and audit ordering"
    return "; ".join(focus[:3])


def _phase9_validation_error(
    errors: list[dict[str, str]],
    code: str,
    field: str,
    detail: str,
) -> None:
    errors.append({"code": code, "field": field, "detail": detail})


def _phase9_bundle_validation_result(
    bundle: Any,
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> dict[str, Any]:
    phase9_report = (
        bundle.get("phase9_report")
        if isinstance(bundle, dict) and isinstance(bundle.get("phase9_report"), dict)
        else {}
    )
    safety_boundary = (
        str(bundle.get("safety_boundary_statement") or "") if isinstance(bundle, dict) else ""
    )
    error_codes = _unique([error["code"] for error in errors])
    warning_codes = _unique([warning["code"] for warning in warnings])

    return {
        "valid": not errors,
        "status": "valid" if not errors else "blocked",
        "error_codes": error_codes,
        "errors": errors,
        "warning_codes": warning_codes,
        "warnings": warnings,
        "bundle_version": str(bundle.get("bundle_version") or "") if isinstance(bundle, dict) else "",
        "report_version": (
            str(bundle.get("report_version") or phase9_report.get("report_version") or "")
            if isinstance(bundle, dict)
            else ""
        ),
        "safety_boundary_confirmed": bool(safety_boundary.strip()) and not errors,
    }


def _phase9_sensitive_key_paths(value: Any, path: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            text_key = str(key)
            current_path = f"{path}.{text_key}" if path else text_key
            if _is_sensitive_export_key(text_key):
                paths.append(current_path)
            paths.extend(_phase9_sensitive_key_paths(item, current_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            current_path = f"{path}[{index}]" if path else f"[{index}]"
            paths.extend(_phase9_sensitive_key_paths(item, current_path))
    return paths


def _phase9_nested_true(value: Any, key_name: str) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key) == key_name and item is True:
                return True
            if _phase9_nested_true(item, key_name):
                return True
    if isinstance(value, list):
        return any(_phase9_nested_true(item, key_name) for item in value)
    return False


def _validate_phase9_audit_timeline(
    audit_timeline: list[Any],
    errors: list[dict[str, str]],
) -> None:
    global_orders: list[int] = []
    for index, event in enumerate(audit_timeline):
        field_path = f"phase9_report.audit_timeline[{index}]"
        if not isinstance(event, dict):
            _phase9_validation_error(
                errors,
                "malformed_audit_event",
                field_path,
                "Audit timeline entries must be objects.",
            )
            continue

        if not str(event.get("event_name") or ""):
            _phase9_validation_error(
                errors,
                "malformed_audit_event",
                f"{field_path}.event_name",
                "Audit event name is missing.",
            )
        if not str(event.get("scenario_id") or ""):
            _phase9_validation_error(
                errors,
                "malformed_audit_event",
                f"{field_path}.scenario_id",
                "Audit event scenario_id is missing.",
            )
        if not _is_positive_int(event.get("order")):
            _phase9_validation_error(
                errors,
                "malformed_audit_event",
                f"{field_path}.order",
                "Audit event scenario order must be a positive integer.",
            )
        if not _is_positive_int(event.get("global_order")):
            _phase9_validation_error(
                errors,
                "malformed_audit_event",
                f"{field_path}.global_order",
                "Audit event global order must be a positive integer.",
            )
        else:
            global_orders.append(int(event["global_order"]))

        if not _is_string_list(event.get("failure_reason_codes")):
            _phase9_validation_error(
                errors,
                "malformed_blocker_codes",
                f"{field_path}.failure_reason_codes",
                "Audit event failure reason codes must be a list of strings.",
            )
        if not _is_string_list(event.get("blocker_codes")):
            _phase9_validation_error(
                errors,
                "malformed_blocker_codes",
                f"{field_path}.blocker_codes",
                "Audit event blocker codes must be a list of strings.",
            )

    if global_orders and global_orders != list(range(1, len(audit_timeline) + 1)):
        _phase9_validation_error(
            errors,
            "malformed_audit_event",
            "phase9_report.audit_timeline",
            "Audit timeline global order must be deterministic and contiguous.",
        )


def _validate_phase9_minimal_reproduction_metadata(
    metadata: dict[str, Any],
    phase9_report: dict[str, Any],
    errors: list[dict[str, str]],
) -> None:
    for field_name in PHASE9_BUNDLE_METADATA_REQUIRED_FIELDS:
        if field_name not in metadata:
            _phase9_validation_error(
                errors,
                "missing_bundle_field",
                f"minimal_reproduction_metadata.{field_name}",
                "Required minimal reproduction metadata is missing.",
            )

    for code_field in ("failure_reason_codes", "blocker_codes"):
        if code_field in metadata and not _is_string_list(metadata.get(code_field)):
            _phase9_validation_error(
                errors,
                "malformed_blocker_codes",
                f"minimal_reproduction_metadata.{code_field}",
                "Minimal reproduction codes must be a list of strings.",
            )

    audit_event_order = metadata.get("audit_event_order")
    if "audit_event_order" in metadata and not isinstance(audit_event_order, list):
        _phase9_validation_error(
            errors,
            "malformed_audit_event",
            "minimal_reproduction_metadata.audit_event_order",
            "Audit event order metadata must be a list.",
        )
        return

    report_timeline = phase9_report.get("audit_timeline")
    if isinstance(audit_event_order, list) and isinstance(report_timeline, list):
        metadata_sequence = [
            str(event.get("event_name") or "") for event in audit_event_order if isinstance(event, dict)
        ]
        report_sequence = [
            str(event.get("event_name") or "") for event in report_timeline if isinstance(event, dict)
        ]
        if metadata_sequence != report_sequence:
            _phase9_validation_error(
                errors,
                "malformed_audit_event",
                "minimal_reproduction_metadata.audit_event_order",
                "Metadata audit event order must match the Phase 9 report timeline.",
            )


def _phase9_replay_notes(validation: dict[str, Any]) -> list[str]:
    if validation.get("valid") is True:
        return [
            "Phase 9.5 replay validated the imported reproducibility bundle.",
            "Replay preserves the original deterministic audit event order.",
            "Replay is read-only debug output; no action-performing endpoint is called.",
            "Real desktop actions remain disabled.",
        ]
    return [
        "Phase 9.5 replay was blocked by bundle validation.",
        f"Validation errors: {_format_codes(_string_list(validation.get('error_codes')))}.",
        "No state changes were made.",
    ]


def _is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _is_positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _sanitize_export_value(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            text_key = str(key)
            if _is_sensitive_export_key(text_key):
                continue
            sanitized[text_key] = _sanitize_export_value(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_export_value(item) for item in value]
    if isinstance(value, tuple):
        return [_sanitize_export_value(item) for item in value]
    return value


def _is_sensitive_export_key(key: str) -> bool:
    normalized = key.lower()
    return any(fragment in normalized for fragment in _SENSITIVE_KEY_FRAGMENTS)


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item)]


def _format_codes(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def _yes_no(value: Any) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return "unknown"


def phase9_experiment_scenario_ids() -> list[str]:
    """Return Phase 9 demo scenario IDs in deterministic order."""

    return list(PHASE9_MINIMAL_SCENARIO_IDS)


def phase9_experiment_scenario_input(scenario_id: str) -> dict[str, Any]:
    """Return one fixture-backed Phase 9 harness scenario definition."""

    normalized_id = str(scenario_id or "")
    builder = _PHASE9_SCENARIO_BUILDERS.get(normalized_id)
    if builder is None:
        raise UnknownPhase9ExperimentScenarioError(
            f"Unknown Phase 9 experiment scenario '{normalized_id}'."
        )
    return builder()


def evaluate_phase9_experiment_scenarios(
    scenario_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Evaluate deterministic Phase 9 harness fixtures without real actions."""

    selected_ids = scenario_ids if scenario_ids is not None else phase9_experiment_scenario_ids()
    results = []
    for scenario_id in selected_ids:
        definition = phase9_experiment_scenario_input(scenario_id)
        results.append(run_phase9_experiment(definition["config"], definition["request"]))
    return build_phase9_experiment_report(results)


def _phase9_dry_run_success_all_gates_pass() -> dict[str, Any]:
    return _phase9_scenario(
        "dry_run_success_all_gates_pass",
        "Dry-run success with all Phase 7 gates satisfied",
        _phase9_expected_outcome(status="dry_run_completed", gate_passed=True),
        notes=("Phase 9.1 fixture passes every gate and stays simulated.",),
    )


def _phase9_real_action_disabled_skips_non_dry_run() -> dict[str, Any]:
    return _phase9_scenario(
        "real_action_disabled_skips_non_dry_run",
        "Non-dry-run request skips because real actions are disabled",
        _phase9_expected_outcome(
            status="real_action_skipped",
            gate_passed=True,
            dry_run=False,
            real_action_skipped=True,
            failure_reason_codes=[FAILURE_REAL_ACTION_DISABLED],
            audit_event_names=[
                EVENT_PHASE9_EXPERIMENT_REQUESTED,
                EVENT_PHASE9_MOCK_APPROVAL_CHECKED,
                EVENT_PHASE9_EMERGENCY_STOP_CHECKED,
                EVENT_PHASE9_GATE_PASSED,
                EVENT_PHASE9_POST_ACTION_VERIFICATION_PLANNED,
                EVENT_PHASE9_ROLLBACK_PLAN_RECORDED,
                EVENT_PHASE9_REAL_ACTION_SKIPPED,
            ],
        ),
        config=_phase9_config(dry_run=False),
        notes=("The harness records a skip instead of attempting action.",),
    )


def _phase9_missing_user_approval_blocks() -> dict[str, Any]:
    return _phase9_blocked_scenario(
        "missing_user_approval_blocks",
        "Missing mock user approval blocks",
        [FAILURE_MISSING_USER_APPROVAL],
        request=_phase9_request(approval=MockApprovalState(present=False, user_approved=False)),
    )


def _phase9_stale_observation_blocks() -> dict[str, Any]:
    stale_timestamp = (PHASE9_DEMO_NOW - timedelta(seconds=30)).isoformat().replace(
        "+00:00",
        "Z",
    )
    return _phase9_blocked_scenario(
        "stale_observation_blocks",
        "Stale observation blocks",
        [FAILURE_STALE_OBSERVATION],
        ["stale_observation"],
        config=_phase9_config(expected_readiness_blocker_codes=("stale_observation",)),
        request=_phase9_request(
            observation_timestamp=stale_timestamp,
            click_readiness=_phase9_blocked_readiness("stale_observation"),
        ),
    )


def _phase9_high_risk_target_blocks() -> dict[str, Any]:
    return _phase9_blocked_scenario(
        "high_risk_target_blocks",
        "High-risk target blocks",
        [FAILURE_HIGH_RISK_TARGET],
        ["high_risk_requires_approval"],
        config=_phase9_config(expected_readiness_blocker_codes=("high_risk_requires_approval",)),
        request=_phase9_request(
            action_contract=_phase9_contract(risk="high", target_risk_hint="high_risk"),
            click_readiness=_phase9_blocked_readiness("high_risk_requires_approval"),
            visible_elements=[_phase9_visible_element(risk_hint="high_risk")],
            safety_decision={"decision": "needs_approval", "risk": "high"},
        ),
    )


def _phase9_missing_audit_plan_blocks() -> dict[str, Any]:
    return _phase9_blocked_scenario(
        "missing_audit_plan_blocks",
        "Missing audit plan blocks",
        [FAILURE_MISSING_AUDIT_PLAN],
        config=_phase9_config(audit_plan_present=False),
    )


def _phase9_missing_action_contract_blocks() -> dict[str, Any]:
    return _phase9_blocked_scenario(
        "missing_action_contract_blocks",
        "Missing action contract blocks",
        [FAILURE_MISSING_ACTION_CONTRACT],
        request=_phase9_request(
            action_contract=None,
            approval=_phase9_approval(action_contract_id="", target_id=""),
        ),
    )


def _phase9_scenario(
    scenario_id: str,
    scenario_name: str,
    expected_outcome: dict[str, Any],
    *,
    config: Phase9ExperimentConfig | None = None,
    request: Phase9ExperimentRequest | None = None,
    notes: tuple[str, ...] = (),
) -> dict[str, Any]:
    scenario_request = request or _phase9_request()
    scenario_request = Phase9ExperimentRequest(
        **{
            **scenario_request.__dict__,
            "scenario_id": scenario_id,
            "scenario_name": scenario_name,
            "expected_outcome": expected_outcome,
            "notes": notes or scenario_request.notes,
        }
    )
    return {
        "scenario_id": scenario_id,
        "scenario_name": scenario_name,
        "expected_outcome": expected_outcome,
        "config": config or _phase9_config(),
        "request": scenario_request,
    }


def _phase9_blocked_scenario(
    scenario_id: str,
    scenario_name: str,
    failure_reason_codes: list[str],
    blocker_codes: list[str] | None = None,
    *,
    config: Phase9ExperimentConfig | None = None,
    request: Phase9ExperimentRequest | None = None,
) -> dict[str, Any]:
    return _phase9_scenario(
        scenario_id,
        scenario_name,
        _phase9_expected_outcome(
            status="blocked",
            gate_passed=False,
            failure_reason_codes=failure_reason_codes,
            blocker_codes=blocker_codes or [],
            audit_event_names=[
                EVENT_PHASE9_EXPERIMENT_REQUESTED,
                EVENT_PHASE9_MOCK_APPROVAL_CHECKED,
                EVENT_PHASE9_EMERGENCY_STOP_CHECKED,
                EVENT_PHASE9_GATE_BLOCKED,
            ],
            post_action_verification_planned=False,
        ),
        config=config,
        request=request,
    )


_PHASE9_SCENARIO_BUILDERS = {
    "dry_run_success_all_gates_pass": _phase9_dry_run_success_all_gates_pass,
    "real_action_disabled_skips_non_dry_run": _phase9_real_action_disabled_skips_non_dry_run,
    "missing_user_approval_blocks": _phase9_missing_user_approval_blocks,
    "stale_observation_blocks": _phase9_stale_observation_blocks,
    "high_risk_target_blocks": _phase9_high_risk_target_blocks,
    "missing_audit_plan_blocks": _phase9_missing_audit_plan_blocks,
    "missing_action_contract_blocks": _phase9_missing_action_contract_blocks,
}


def _phase9_expected_outcome(
    *,
    status: str,
    gate_passed: bool,
    dry_run: bool = True,
    real_action_enabled: bool = False,
    real_action_skipped: bool = False,
    failure_reason_codes: list[str] | None = None,
    blocker_codes: list[str] | None = None,
    audit_event_names: list[str] | None = None,
    post_action_verification_planned: bool = True,
) -> dict[str, Any]:
    return {
        "status": status,
        "gate_passed": gate_passed,
        "dry_run": dry_run,
        "real_action_enabled": real_action_enabled,
        "real_action_skipped": real_action_skipped,
        "failure_reason_codes": list(failure_reason_codes or []),
        "blocker_codes": list(blocker_codes or []),
        "audit_event_names": list(audit_event_names or _phase9_dry_run_success_events()),
        "post_action_verification_planned": post_action_verification_planned,
        "real_action_attempted": False,
    }


def _phase9_dry_run_success_events() -> list[str]:
    return [
        EVENT_PHASE9_EXPERIMENT_REQUESTED,
        EVENT_PHASE9_MOCK_APPROVAL_CHECKED,
        EVENT_PHASE9_EMERGENCY_STOP_CHECKED,
        EVENT_PHASE9_GATE_PASSED,
        EVENT_PHASE9_POST_ACTION_VERIFICATION_PLANNED,
        EVENT_PHASE9_ROLLBACK_PLAN_RECORDED,
        EVENT_PHASE9_DRY_RUN_COMPLETED,
    ]


def _phase9_config(**overrides: Any) -> Phase9ExperimentConfig:
    values = {
        "experiment_id": "phase9_minimal_fixture_click",
        "dry_run": True,
        "real_action_enabled": False,
        "allowed_action_type": "click",
        "allowed_window_id": DEFAULT_ALLOWED_WINDOW_ID,
        "allowed_target_id": DEFAULT_ALLOWED_TARGET_ID,
        "phase7_checklist": _phase9_checklist(),
    }
    values.update(overrides)
    return Phase9ExperimentConfig(**values)


def _phase9_request(**overrides: Any) -> Phase9ExperimentRequest:
    values = {
        "scenario_id": "dry_run_success_all_gates_pass",
        "scenario_name": "Dry-run success with all Phase 7 gates satisfied",
        "sandbox_scope": _phase9_scope(),
        "approval": _phase9_approval(),
        "emergency_stop": MockEmergencyStopState(
            available=True,
            active=False,
            checked_at=PHASE9_DEMO_NOW.isoformat().replace("+00:00", "Z"),
        ),
        "post_action_verification_plan": MockPostActionVerificationPlan(
            present=True,
            planned=True,
            simulated=True,
        ),
        "rollback_plan": MockRollbackPlan(present=True, simulated=True, sandbox_only=True),
        "action_contract": _phase9_contract(),
        "click_readiness": {"ready": True, "status": "ready", "blocker_codes": []},
        "visible_elements": [_phase9_visible_element()],
        "safety_decision": {"decision": "allowed", "risk": "low"},
        "screen": _phase9_screen(),
        "observation_timestamp": PHASE9_DEMO_OBSERVATION_TIMESTAMP,
        "observation_id": PHASE9_DEMO_OBSERVATION_ID,
        "sandbox_window_id": DEFAULT_ALLOWED_WINDOW_ID,
        "current_time": PHASE9_DEMO_NOW,
        "audit_context": {"run_id": "phase9_demo_run_0001"},
        "notes": ("fixture-only",),
    }
    values.update(overrides)
    return Phase9ExperimentRequest(**values)


def _phase9_approval(
    action_contract_id: str = PHASE9_DEMO_ACTION_ID,
    target_id: str = DEFAULT_ALLOWED_TARGET_ID,
    observation_id: str = PHASE9_DEMO_OBSERVATION_ID,
) -> MockApprovalState:
    return MockApprovalState(
        present=True,
        user_approved=True,
        action_contract_id=action_contract_id,
        target_id=target_id,
        observation_id=observation_id,
        approved_at=PHASE9_DEMO_OBSERVATION_TIMESTAMP,
        expires_at=(PHASE9_DEMO_NOW + timedelta(seconds=5)).isoformat().replace("+00:00", "Z"),
    )


def _phase9_scope() -> dict[str, Any]:
    return {
        "window_id": DEFAULT_ALLOWED_WINDOW_ID,
        "target_id": DEFAULT_ALLOWED_TARGET_ID,
        "one_window_only": True,
        "one_target_only": True,
        "system_settings_allowed": False,
        "file_deletion_allowed": False,
        "shell_execution_allowed": False,
        "browser_credentials_allowed": False,
        "external_websites_allowed": False,
        "destructive_actions_allowed": False,
        "hidden_background_actions_allowed": False,
    }


def _phase9_contract(
    action_type: str = "click",
    risk: str = "low",
    target_risk_hint: str = "normal",
) -> dict[str, Any]:
    return {
        "action_id": PHASE9_DEMO_ACTION_ID,
        "source_proposal_id": "phase9_sandbox_proposal_0001",
        "type": action_type,
        "risk": risk,
        "target_element_id": DEFAULT_ALLOWED_TARGET_ID,
        "target_label": "phase9 sandbox test button",
        "target_role": "button",
        "target_confidence": 0.96,
        "target_source": "ui_tree",
        "target_risk_hint": target_risk_hint,
        "target_timestamp": PHASE9_DEMO_OBSERVATION_TIMESTAMP,
        "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
        "center": {"x": 50, "y": 32},
        "status": "approved_for_execution",
        "executed": False,
    }


def _phase9_visible_element(
    risk_hint: str = "normal",
    confidence: float = 0.96,
) -> dict[str, Any]:
    return {
        "id": DEFAULT_ALLOWED_TARGET_ID,
        "label": "phase9 sandbox test button",
        "text": "phase9 sandbox test button",
        "role": "button",
        "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
        "center": {"x": 50, "y": 32},
        "confidence": confidence,
        "source": "ui_tree",
        "risk_hint": risk_hint,
        "timestamp": PHASE9_DEMO_OBSERVATION_TIMESTAMP,
    }


def _phase9_screen() -> dict[str, Any]:
    return {
        "width": 200,
        "height": 120,
        "coordinate_space": "screen",
        "dpi_scale": 1.0,
    }


def _phase9_blocked_readiness(*blocker_codes: str) -> dict[str, Any]:
    return {
        "ready": False,
        "status": "blocked",
        "blocker_codes": list(blocker_codes),
    }


def _phase9_checklist() -> dict[str, bool]:
    return {item: True for item in REQUIRED_PHASE7_CHECKLIST_ITEMS}


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
        sandbox_scope=dict(request.sandbox_scope),
        user_approval_present=bool(request.approval and request.approval.present),
        emergency_stop_available=bool(request.emergency_stop and request.emergency_stop.available),
        emergency_stop_active=bool(request.emergency_stop and request.emergency_stop.active),
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
