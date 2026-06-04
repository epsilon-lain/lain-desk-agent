"""Deterministic Phase 8.1 sandbox experiment evaluation.

The scenarios in this module exercise only the dry-run sandbox framework. They
do not observe the live desktop, do not call the execution endpoint, and do not
perform any real desktop action.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

from .sandbox_experiment import (
    EVENT_SANDBOX_DRY_RUN_COMPLETED,
    EVENT_SANDBOX_EXPERIMENT_REQUESTED,
    EVENT_SANDBOX_GATE_BLOCKED,
    EVENT_SANDBOX_GATE_PASSED,
    EVENT_SANDBOX_POST_ACTION_VERIFICATION_PLANNED,
    EVENT_SANDBOX_REAL_ACTION_SKIPPED,
    FAILURE_FORBIDDEN_ACTION_TYPE,
    FAILURE_HIGH_RISK_TARGET,
    FAILURE_INVALID_TARGET_GEOMETRY,
    FAILURE_LOW_CONFIDENCE_TARGET,
    FAILURE_MISSING_POST_ACTION_VERIFICATION,
    FAILURE_MISSING_USER_APPROVAL,
    FAILURE_OUTSIDE_SANDBOX_SCOPE,
    FAILURE_READINESS_NOT_READY,
    FAILURE_REAL_ACTION_DISABLED,
    FAILURE_STALE_OBSERVATION,
    REQUIRED_PHASE7_CHECKLIST_ITEMS,
    SandboxExperimentConfig,
    SandboxExperimentRequest,
    SandboxExperimentResult,
    run_sandbox_experiment,
)


SANDBOX_EVALUATION_NOW = datetime(2026, 1, 1, 0, 0, 5, tzinfo=timezone.utc)
SANDBOX_OBSERVATION_TIMESTAMP = "2026-01-01T00:00:00Z"
SANDBOX_WINDOW_ID = "sandbox_window"
SANDBOX_TARGET_ID = "sandbox_target_button"
SANDBOX_ACTION_ID = "sandbox_action_0001"


class UnknownSandboxEvaluationScenarioError(ValueError):
    """Raised when a requested built-in sandbox scenario does not exist."""


def sandbox_evaluation_scenario_names() -> list[str]:
    """Return Phase 8.1 sandbox scenario names in deterministic order."""

    return list(_SCENARIO_BUILDERS)


def sandbox_evaluation_scenario_input(name: str) -> dict[str, Any]:
    """Return one deterministic sandbox config/request/expectation fixture."""

    scenario_name = str(name or "")
    builder = _SCENARIO_BUILDERS.get(scenario_name)
    if builder is None:
        raise UnknownSandboxEvaluationScenarioError(
            f"Unknown sandbox evaluation scenario '{scenario_name}'."
        )
    return builder()


def evaluate_sandbox_experiment_scenarios(names: list[str] | None = None) -> dict[str, Any]:
    """Evaluate all or selected dry-run sandbox experiment fixtures."""

    scenario_names = names if names is not None else sandbox_evaluation_scenario_names()
    scenarios = [evaluate_sandbox_experiment_scenario(name) for name in scenario_names]
    return {
        "report_type": "sandbox_experiment_evaluation",
        "phase": "phase8_1",
        "source": "sandbox_evaluation_scenarios",
        "external_llm_calls": False,
        "real_desktop_actions": False,
        "scenario_count": len(scenarios),
        "summary": _summary(scenarios),
        "report_notes": [
            "Phase 8.1 evaluates sandbox gate behavior only.",
            "Dry-run remains the default and real_action_enabled remains false by default.",
            "No scenario calls real desktop actuation or changes execution permissions.",
        ],
        "scenarios": scenarios,
    }


def evaluate_sandbox_experiment_scenario(name: str) -> dict[str, Any]:
    """Evaluate one deterministic dry-run sandbox experiment fixture."""

    scenario = sandbox_evaluation_scenario_input(name)
    result = run_sandbox_experiment(scenario["config"], scenario["request"])
    actual = _actual_outcome(result)
    expectation = _expectation_report(scenario["expected"], actual)

    return {
        "scenario": scenario["scenario"],
        "description": scenario["description"],
        "expected": scenario["expected"],
        "actual": actual,
        "passed": expectation["passed"],
        "pass_fail": "pass" if expectation["passed"] else "fail",
        "expectation": expectation,
        "gate_passed": result.gate_passed,
        "failure_reasons": list(result.failure_reasons),
        "audit_event_names": _audit_event_names(result),
        "dry_run": result.dry_run,
        "real_action_enabled": result.real_action_enabled,
        "real_action_skipped": actual["real_action_skipped"],
        "post_action_verification_planned": actual["post_action_verification_planned"],
        "trace": _trace(scenario, result, actual),
    }


def _scenario(
    name: str,
    description: str,
    expected: dict[str, Any],
    config: SandboxExperimentConfig | None = None,
    request: SandboxExperimentRequest | None = None,
) -> dict[str, Any]:
    return {
        "scenario": name,
        "description": description,
        "config": config or _config(),
        "request": request or _request(),
        "expected": expected,
    }


def _sandbox_dry_run_success() -> dict[str, Any]:
    return _scenario(
        "sandbox_dry_run_success",
        "All Phase 7 gates are satisfied and the experiment completes as dry-run.",
        _expected(
            status="dry_run_completed",
            gate_passed=True,
            audit_event_names=[
                EVENT_SANDBOX_EXPERIMENT_REQUESTED,
                EVENT_SANDBOX_GATE_PASSED,
                EVENT_SANDBOX_POST_ACTION_VERIFICATION_PLANNED,
                EVENT_SANDBOX_DRY_RUN_COMPLETED,
            ],
            post_action_verification_planned=True,
        ),
    )


def _real_action_disabled_skip() -> dict[str, Any]:
    return _scenario(
        "real_action_disabled_skip",
        "A non-dry-run request reaches the framework while real_action_enabled is false.",
        _expected(
            status="real_action_skipped",
            gate_passed=True,
            dry_run=False,
            failure_reasons=[FAILURE_REAL_ACTION_DISABLED],
            audit_event_names=[
                EVENT_SANDBOX_EXPERIMENT_REQUESTED,
                EVENT_SANDBOX_GATE_PASSED,
                EVENT_SANDBOX_POST_ACTION_VERIFICATION_PLANNED,
                EVENT_SANDBOX_REAL_ACTION_SKIPPED,
            ],
            real_action_skipped=True,
            post_action_verification_planned=True,
        ),
        config=_config(dry_run=False, real_action_enabled=False),
    )


def _missing_user_approval() -> dict[str, Any]:
    return _blocked_scenario(
        "missing_user_approval",
        "The request does not carry an explicit user approval flag.",
        [FAILURE_MISSING_USER_APPROVAL],
        request=_request(user_approved=False),
    )


def _stale_observation() -> dict[str, Any]:
    stale_timestamp = (SANDBOX_EVALUATION_NOW - timedelta(seconds=30)).isoformat().replace(
        "+00:00",
        "Z",
    )
    return _blocked_scenario(
        "stale_observation",
        "The observation timestamp is older than the configured freshness window.",
        [FAILURE_STALE_OBSERVATION],
        request=_request(observation_timestamp=stale_timestamp),
    )


def _high_risk_target() -> dict[str, Any]:
    return _blocked_scenario(
        "high_risk_target",
        "The target is marked high-risk by visible_elements and action contract metadata.",
        [FAILURE_HIGH_RISK_TARGET],
        request=_request(
            action_contract=_contract(risk="high", target_risk_hint="high_risk"),
            visible_elements=[_visible_element(risk_hint="high_risk")],
            safety_decision={"decision": "needs_approval", "risk": "high"},
        ),
    )


def _unknown_risk_target() -> dict[str, Any]:
    return _blocked_scenario(
        "unknown_risk_target",
        "The target carries unknown risk metadata and must not become actionable.",
        [FAILURE_HIGH_RISK_TARGET],
        request=_request(
            action_contract=_contract(target_risk_hint="unknown"),
            visible_elements=[_visible_element(risk_hint="unknown")],
        ),
    )


def _low_confidence_target() -> dict[str, Any]:
    return _blocked_scenario(
        "low_confidence_target",
        "The target confidence is below the sandbox readiness threshold.",
        [FAILURE_LOW_CONFIDENCE_TARGET, FAILURE_READINESS_NOT_READY],
        request=_request(
            action_contract=_contract(target_confidence=0.2),
            click_readiness={
                "ready": False,
                "status": "blocked",
                "blocker_codes": ["low_confidence_target"],
            },
            visible_elements=[_visible_element(confidence=0.2)],
        ),
    )


def _invalid_geometry() -> dict[str, Any]:
    return _blocked_scenario(
        "invalid_bbox_center",
        "The target center does not match the declared bbox.",
        [FAILURE_INVALID_TARGET_GEOMETRY],
        request=_request(action_contract=_contract(center={"x": 99, "y": 99})),
    )


def _missing_post_action_verification() -> dict[str, Any]:
    return _blocked_scenario(
        "missing_post_action_verification",
        "No post-action verification plan is present.",
        [FAILURE_MISSING_POST_ACTION_VERIFICATION],
        request=_request(post_action_verification_plan=None),
    )


def _forbidden_action_type() -> dict[str, Any]:
    return _blocked_scenario(
        "forbidden_action_type",
        "The action type is outside the one-action sandbox scope and is forbidden.",
        [FAILURE_FORBIDDEN_ACTION_TYPE, FAILURE_OUTSIDE_SANDBOX_SCOPE],
        request=_request(action_contract=_contract(action_type="switch_app")),
    )


def _outside_sandbox_scope() -> dict[str, Any]:
    return _blocked_scenario(
        "outside_sandbox_scope",
        "The target does not match the single allowed sandbox target.",
        [FAILURE_OUTSIDE_SANDBOX_SCOPE],
        config=_config(allowed_target_id="other_sandbox_target"),
    )


def _readiness_not_ready() -> dict[str, Any]:
    return _blocked_scenario(
        "readiness_not_ready",
        "Click readiness returns a blocker that was not declared as expected dry-run behavior.",
        [FAILURE_READINESS_NOT_READY],
        request=_request(
            click_readiness={
                "ready": False,
                "status": "blocked",
                "blocker_codes": ["preview_only_contract"],
            }
        ),
    )


def _missing_emergency_stop() -> dict[str, Any]:
    return _blocked_scenario(
        "missing_emergency_stop",
        "The experiment does not expose the required emergency stop gate.",
        [FAILURE_OUTSIDE_SANDBOX_SCOPE],
        config=_config(emergency_stop_available=False),
    )


def _blocked_scenario(
    name: str,
    description: str,
    failure_reasons: list[str],
    config: SandboxExperimentConfig | None = None,
    request: SandboxExperimentRequest | None = None,
) -> dict[str, Any]:
    return _scenario(
        name,
        description,
        _expected(
            status="blocked",
            gate_passed=False,
            failure_reasons=failure_reasons,
            audit_event_names=[
                EVENT_SANDBOX_EXPERIMENT_REQUESTED,
                EVENT_SANDBOX_GATE_BLOCKED,
            ],
        ),
        config=config,
        request=request,
    )


_SCENARIO_BUILDERS = {
    "sandbox_dry_run_success": _sandbox_dry_run_success,
    "real_action_disabled_skip": _real_action_disabled_skip,
    "missing_user_approval": _missing_user_approval,
    "stale_observation": _stale_observation,
    "high_risk_target": _high_risk_target,
    "unknown_risk_target": _unknown_risk_target,
    "low_confidence_target": _low_confidence_target,
    "invalid_bbox_center": _invalid_geometry,
    "missing_post_action_verification": _missing_post_action_verification,
    "forbidden_action_type": _forbidden_action_type,
    "outside_sandbox_scope": _outside_sandbox_scope,
    "readiness_not_ready": _readiness_not_ready,
    "missing_emergency_stop": _missing_emergency_stop,
}


def _expected(
    *,
    status: str,
    gate_passed: bool,
    dry_run: bool = True,
    real_action_enabled: bool = False,
    failure_reasons: list[str] | None = None,
    audit_event_names: list[str],
    real_action_skipped: bool = False,
    post_action_verification_planned: bool = False,
) -> dict[str, Any]:
    return {
        "status": status,
        "gate_passed": gate_passed,
        "dry_run": dry_run,
        "real_action_enabled": real_action_enabled,
        "failure_reasons": list(failure_reasons or []),
        "audit_event_names": list(audit_event_names),
        "real_action_skipped": real_action_skipped,
        "post_action_verification_planned": post_action_verification_planned,
        "real_action_attempted": False,
    }


def _actual_outcome(result: SandboxExperimentResult) -> dict[str, Any]:
    audit_event_names = _audit_event_names(result)
    return {
        "status": result.status,
        "gate_passed": result.gate_passed,
        "dry_run": result.dry_run,
        "real_action_enabled": result.real_action_enabled,
        "failure_reasons": list(result.failure_reasons),
        "audit_event_names": audit_event_names,
        "real_action_skipped": EVENT_SANDBOX_REAL_ACTION_SKIPPED in audit_event_names,
        "post_action_verification_planned": (
            EVENT_SANDBOX_POST_ACTION_VERIFICATION_PLANNED in audit_event_names
        ),
        "real_action_attempted": result.real_action_attempted,
    }


def _expectation_report(expected: dict[str, Any], actual: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []

    for field in [
        "status",
        "gate_passed",
        "dry_run",
        "real_action_enabled",
        "real_action_skipped",
        "post_action_verification_planned",
        "real_action_attempted",
    ]:
        if expected.get(field) != actual.get(field):
            failures.append(
                f"{field} expected {expected.get(field)!r} but got {actual.get(field)!r}"
            )

    expected_reasons = [str(reason) for reason in expected.get("failure_reasons", [])]
    actual_reasons = [str(reason) for reason in actual.get("failure_reasons", [])]
    if expected_reasons:
        missing_reasons = [reason for reason in expected_reasons if reason not in actual_reasons]
        if missing_reasons:
            failures.append(
                f"failure_reasons missing {missing_reasons!r} from {actual_reasons!r}"
            )
    elif actual_reasons:
        failures.append(f"failure_reasons expected [] but got {actual_reasons!r}")

    expected_events = [str(event) for event in expected.get("audit_event_names", [])]
    actual_events = [str(event) for event in actual.get("audit_event_names", [])]
    if expected_events != actual_events:
        failures.append(
            f"audit_event_names expected {expected_events!r} but got {actual_events!r}"
        )

    if actual.get("real_action_attempted") is True:
        failures.append("real_action_attempted must remain false")

    return {
        "passed": not failures,
        "failures": failures,
        "expected": expected,
        "actual": actual,
    }


def _summary(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    failed = [scenario for scenario in scenarios if not scenario["passed"]]
    return {
        "total_scenario_count": len(scenarios),
        "passed_scenario_count": len(scenarios) - len(failed),
        "failed_scenario_count": len(failed),
        "scenarios_with_failures": [scenario["scenario"] for scenario in failed],
        "all_expected_outcomes_passed": not failed,
        "gate_passed_count": sum(1 for scenario in scenarios if scenario["gate_passed"]),
        "gate_blocked_count": sum(1 for scenario in scenarios if not scenario["gate_passed"]),
        "dry_run_scenario_count": sum(1 for scenario in scenarios if scenario["dry_run"]),
        "real_action_enabled_count": sum(1 for scenario in scenarios if scenario["real_action_enabled"]),
        "real_action_skipped_count": sum(
            1 for scenario in scenarios if scenario["real_action_skipped"]
        ),
        "real_action_attempted_count": sum(
            1 for scenario in scenarios if scenario["actual"]["real_action_attempted"]
        ),
        "post_action_verification_planned_count": sum(
            1 for scenario in scenarios if scenario["post_action_verification_planned"]
        ),
        "failure_reason_codes": _failure_reason_summary(scenarios),
        "audit_event_names": _audit_event_summary(scenarios),
    }


def _trace(
    scenario: dict[str, Any],
    result: SandboxExperimentResult,
    actual: dict[str, Any],
) -> dict[str, Any]:
    return {
        "scenario": scenario["scenario"],
        "result_status": result.status,
        "gate_passed": result.gate_passed,
        "dry_run": result.dry_run,
        "real_action_enabled": result.real_action_enabled,
        "real_action_skipped": actual["real_action_skipped"],
        "post_action_verification_planned": actual["post_action_verification_planned"],
        "failure_reasons": list(result.failure_reasons),
        "audit_event_names": _audit_event_names(result),
        "validation_checks": _validation_checks(result.validation),
    }


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


def _audit_event_names(result: SandboxExperimentResult) -> list[str]:
    return [
        str(event.get("type") or "")
        for event in result.audit_events
        if isinstance(event, dict)
    ]


def _failure_reason_summary(scenarios: list[dict[str, Any]]) -> dict[str, list[str]]:
    summary: dict[str, list[str]] = {}
    for scenario in scenarios:
        scenario_name = str(scenario.get("scenario") or "")
        for reason in scenario.get("failure_reasons", []):
            reason_text = str(reason or "")
            if not reason_text:
                continue
            summary.setdefault(reason_text, [])
            if scenario_name and scenario_name not in summary[reason_text]:
                summary[reason_text].append(scenario_name)
    return summary


def _audit_event_summary(scenarios: list[dict[str, Any]]) -> dict[str, list[str]]:
    summary: dict[str, list[str]] = {}
    for scenario in scenarios:
        scenario_name = str(scenario.get("scenario") or "")
        for event_name in scenario.get("audit_event_names", []):
            event_text = str(event_name or "")
            if not event_text:
                continue
            summary.setdefault(event_text, [])
            if scenario_name and scenario_name not in summary[event_text]:
                summary[event_text].append(scenario_name)
    return summary


def _config(**overrides: Any) -> SandboxExperimentConfig:
    values = {
        "experiment_name": "phase8_1_fixture_click",
        "dry_run": True,
        "real_action_enabled": False,
        "allowed_action_type": "click",
        "allowed_window_id": SANDBOX_WINDOW_ID,
        "allowed_target_id": SANDBOX_TARGET_ID,
        "phase7_checklist": _phase7_checklist(),
        "emergency_stop_available": True,
    }
    values.update(overrides)
    return SandboxExperimentConfig(**values)


def _request(**overrides: Any) -> SandboxExperimentRequest:
    values = {
        "user_approved": True,
        "action_contract": _contract(),
        "click_readiness": {"ready": True, "status": "ready", "blocker_codes": []},
        "visible_elements": [_visible_element()],
        "safety_decision": {"decision": "allowed", "risk": "low"},
        "screen": _screen(),
        "observation_timestamp": SANDBOX_OBSERVATION_TIMESTAMP,
        "post_action_verification_plan": _verification_plan(),
        "sandbox_window_id": SANDBOX_WINDOW_ID,
        "current_time": SANDBOX_EVALUATION_NOW,
        "audit_context": {"run_id": "sandbox_eval_run_0001"},
    }
    values.update(overrides)
    return SandboxExperimentRequest(**deepcopy(values))


def _contract(
    action_type: str = "click",
    risk: str = "low",
    target_risk_hint: str = "normal",
    target_confidence: float = 0.96,
    bbox: dict[str, int] | None = None,
    center: dict[str, int] | None = None,
) -> dict[str, Any]:
    return {
        "action_id": SANDBOX_ACTION_ID,
        "source_proposal_id": "sandbox_proposal_0001",
        "type": action_type,
        "risk": risk,
        "target_element_id": SANDBOX_TARGET_ID,
        "target_label": "sandbox test button",
        "target_role": "button",
        "target_confidence": target_confidence,
        "target_source": "ui_tree",
        "target_risk_hint": target_risk_hint,
        "target_timestamp": SANDBOX_OBSERVATION_TIMESTAMP,
        "bbox": bbox or {"x": 10, "y": 20, "width": 80, "height": 24},
        "center": center or {"x": 50, "y": 32},
        "status": "approved_for_execution",
        "executed": False,
    }


def _visible_element(
    risk_hint: str = "normal",
    confidence: float = 0.96,
) -> dict[str, Any]:
    return {
        "id": SANDBOX_TARGET_ID,
        "label": "sandbox test button",
        "text": "sandbox test button",
        "role": "button",
        "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
        "center": {"x": 50, "y": 32},
        "confidence": confidence,
        "source": "ui_tree",
        "risk_hint": risk_hint,
        "timestamp": SANDBOX_OBSERVATION_TIMESTAMP,
    }


def _screen() -> dict[str, Any]:
    return {
        "width": 200,
        "height": 120,
        "coordinate_space": "screen",
        "dpi_scale": 1.0,
    }


def _verification_plan() -> dict[str, Any]:
    return {
        "enabled": True,
        "method": "fixture_state_assertion",
        "expected_state": "sandbox target selected",
    }


def _phase7_checklist() -> dict[str, bool]:
    return {item: True for item in REQUIRED_PHASE7_CHECKLIST_ITEMS}
