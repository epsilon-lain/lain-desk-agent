"""Deterministic Phase 8.1 sandbox gate evaluation and trace reporting.

The evaluation scenarios in this module are fixture-only. They reuse the Phase
8 sandbox gate, normalized target fields, action-contract shape, and readiness
diagnostics, but they never observe the live desktop and never execute actions.
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
    FAILURE_MISSING_ACTION_CONTRACT,
    FAILURE_MISSING_AUDIT_PLAN,
    FAILURE_MISSING_EMERGENCY_STOP,
    FAILURE_MISSING_POST_ACTION_VERIFICATION,
    FAILURE_MISSING_TARGET,
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
    """Return sandbox evaluation scenario IDs in deterministic order."""

    return list(_SCENARIO_BUILDERS)


def sandbox_evaluation_scenario_input(scenario_id: str) -> dict[str, Any]:
    """Return one fixture-backed sandbox scenario definition."""

    normalized_id = str(scenario_id or "")
    builder = _SCENARIO_BUILDERS.get(normalized_id)
    if builder is None:
        raise UnknownSandboxEvaluationScenarioError(
            f"Unknown sandbox evaluation scenario '{normalized_id}'."
        )
    return builder()


def evaluate_sandbox_experiment_scenarios(
    scenario_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Evaluate all or selected sandbox gate fixtures without real actions."""

    selected_ids = scenario_ids if scenario_ids is not None else sandbox_evaluation_scenario_names()
    scenarios = [evaluate_sandbox_experiment_scenario(scenario_id) for scenario_id in selected_ids]
    return {
        "report_type": "sandbox_experiment_evaluation",
        "phase": "phase8_1",
        "source": "sandbox_evaluation_scenarios",
        "external_llm_calls": False,
        "real_desktop_actions": False,
        "scenario_count": len(scenarios),
        "scenario_ids": [scenario["scenario_id"] for scenario in scenarios],
        "summary": _summary(scenarios),
        "report_notes": [
            "Phase 8.1 evaluates dry-run sandbox gate behavior only.",
            "Sandbox evaluation is not execution permission.",
            "No scenario observes the live desktop or calls an execution path.",
        ],
        "scenarios": scenarios,
    }


def evaluate_sandbox_experiment_scenario(scenario_id: str) -> dict[str, Any]:
    """Evaluate one deterministic sandbox gate fixture."""

    definition = sandbox_evaluation_scenario_input(scenario_id)
    result = run_sandbox_experiment(definition["config"], definition["request"])
    actual_outcome = _actual_outcome(result, definition["request"])
    expectation = _expectation_report(definition["expected_outcome"], actual_outcome)

    return {
        "scenario_id": definition["scenario_id"],
        "scenario_name": definition["scenario_name"],
        "scenario": definition["scenario_id"],
        "expected_outcome": definition["expected_outcome"],
        "expected": definition["expected_outcome"],
        "actual_outcome": actual_outcome,
        "actual": actual_outcome,
        "passed": expectation["passed"],
        "pass_fail": "pass" if expectation["passed"] else "fail",
        "expectation": expectation,
        "gate_passed": actual_outcome["gate_passed"],
        "dry_run": actual_outcome["dry_run"],
        "real_action_enabled": actual_outcome["real_action_enabled"],
        "real_action_skipped": actual_outcome["real_action_skipped"],
        "failure_reason_codes": actual_outcome["failure_reason_codes"],
        "failure_reasons": actual_outcome["failure_reason_codes"],
        "blocker_codes": actual_outcome["blocker_codes"],
        "audit_event_names": actual_outcome["audit_event_names"],
        "post_action_verification_planned": actual_outcome["post_action_verification_planned"],
        "target_risk_hint": actual_outcome["target_risk_hint"],
        "target_confidence": actual_outcome["target_confidence"],
        "readiness_ready": actual_outcome["readiness_ready"],
        "action_type": actual_outcome["action_type"],
        "notes": list(definition["notes"]),
        "trace": _trace(definition, result, actual_outcome),
    }


def _scenario(
    scenario_id: str,
    scenario_name: str,
    expected_outcome: dict[str, Any],
    *,
    config: SandboxExperimentConfig | None = None,
    request: SandboxExperimentRequest | None = None,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "scenario_name": scenario_name,
        "config": config or _config(),
        "request": request or _request(),
        "expected_outcome": expected_outcome,
        "notes": list(notes or []),
    }


def _dry_run_success_all_gates_pass() -> dict[str, Any]:
    return _scenario(
        "dry_run_success_all_gates_pass",
        "Dry-run success with all Phase 7 gates satisfied",
        _expected_outcome(
            status="dry_run_completed",
            gate_passed=True,
            audit_event_names=_dry_run_success_events(),
            post_action_verification_planned=True,
        ),
        notes=["All gate inputs are deterministic fixtures."],
    )


def _real_action_disabled_skips_non_dry_run() -> dict[str, Any]:
    return _scenario(
        "real_action_disabled_skips_non_dry_run",
        "Non-dry-run request safely skips because real actions are disabled",
        _expected_outcome(
            status="real_action_skipped",
            gate_passed=True,
            dry_run=False,
            failure_reason_codes=[FAILURE_REAL_ACTION_DISABLED],
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
        notes=["The framework returns a skipped result instead of attempting action."],
    )


def _missing_user_approval_blocks() -> dict[str, Any]:
    return _blocked_scenario(
        "missing_user_approval_blocks",
        "Missing user approval blocks",
        [FAILURE_MISSING_USER_APPROVAL],
        request=_request(user_approved=False),
    )


def _stale_observation_blocks() -> dict[str, Any]:
    stale_timestamp = (SANDBOX_EVALUATION_NOW - timedelta(seconds=30)).isoformat().replace(
        "+00:00",
        "Z",
    )
    return _blocked_scenario(
        "stale_observation_blocks",
        "Stale observation blocks",
        [FAILURE_STALE_OBSERVATION],
        ["stale_observation"],
        config=_config(expected_readiness_blocker_codes=("stale_observation",)),
        request=_request(
            observation_timestamp=stale_timestamp,
            click_readiness=_blocked_readiness("stale_observation"),
        ),
    )


def _high_risk_target_blocks() -> dict[str, Any]:
    return _blocked_scenario(
        "high_risk_target_blocks",
        "High-risk target blocks",
        [FAILURE_HIGH_RISK_TARGET],
        ["high_risk_requires_approval"],
        config=_config(expected_readiness_blocker_codes=("high_risk_requires_approval",)),
        request=_request(
            action_contract=_contract(risk="high", target_risk_hint="high_risk"),
            click_readiness=_blocked_readiness("high_risk_requires_approval"),
            visible_elements=[_visible_element(risk_hint="high_risk")],
            safety_decision={"decision": "needs_approval", "risk": "high"},
        ),
    )


def _unknown_risk_target_blocks() -> dict[str, Any]:
    return _blocked_scenario(
        "unknown_risk_target_blocks",
        "Unknown-risk target blocks",
        [FAILURE_HIGH_RISK_TARGET],
        ["unknown_risk_target"],
        config=_config(expected_readiness_blocker_codes=("unknown_risk_target",)),
        request=_request(
            action_contract=_contract(target_risk_hint="unknown"),
            click_readiness=_blocked_readiness("unknown_risk_target"),
            visible_elements=[_visible_element(risk_hint="unknown")],
        ),
    )


def _low_confidence_target_blocks() -> dict[str, Any]:
    return _blocked_scenario(
        "low_confidence_target_blocks",
        "Low-confidence target blocks",
        [FAILURE_LOW_CONFIDENCE_TARGET],
        ["low_confidence_target"],
        config=_config(expected_readiness_blocker_codes=("low_confidence_target",)),
        request=_request(
            action_contract=_contract(target_confidence=0.2),
            click_readiness=_blocked_readiness("low_confidence_target"),
            visible_elements=[_visible_element(confidence=0.2)],
        ),
    )


def _invalid_bbox_blocks() -> dict[str, Any]:
    return _blocked_scenario(
        "invalid_bbox_blocks",
        "Invalid bbox blocks",
        [FAILURE_INVALID_TARGET_GEOMETRY],
        ["invalid_bbox"],
        config=_config(expected_readiness_blocker_codes=("invalid_bbox",)),
        request=_request(
            action_contract=_contract(bbox={"x": 10, "y": 20, "width": 0, "height": 24}),
            click_readiness=_blocked_readiness("invalid_bbox"),
        ),
    )


def _bbox_center_mismatch_blocks() -> dict[str, Any]:
    return _blocked_scenario(
        "bbox_center_mismatch_blocks",
        "BBox center mismatch blocks",
        [FAILURE_INVALID_TARGET_GEOMETRY],
        ["bbox_center_mismatch"],
        config=_config(expected_readiness_blocker_codes=("bbox_center_mismatch",)),
        request=_request(
            action_contract=_contract(center={"x": 99, "y": 99}),
            click_readiness=_blocked_readiness("bbox_center_mismatch"),
        ),
    )


def _missing_viewport_or_coordinate_space_blocks() -> dict[str, Any]:
    return _blocked_scenario(
        "missing_viewport_or_coordinate_space_blocks",
        "Missing viewport or coordinate space blocks",
        [FAILURE_INVALID_TARGET_GEOMETRY],
        ["coordinate_space_unknown", "dpi_uncertain"],
        config=_config(
            expected_readiness_blocker_codes=("coordinate_space_unknown", "dpi_uncertain")
        ),
        request=_request(
            screen={"width": 200, "height": 120},
            click_readiness=_blocked_readiness("coordinate_space_unknown", "dpi_uncertain"),
        ),
    )


def _missing_post_action_verification_blocks() -> dict[str, Any]:
    return _blocked_scenario(
        "missing_post_action_verification_blocks",
        "Missing post-action verification blocks",
        [FAILURE_MISSING_POST_ACTION_VERIFICATION],
        request=_request(post_action_verification_plan=None),
    )


def _forbidden_action_type_blocks() -> dict[str, Any]:
    return _blocked_scenario(
        "forbidden_action_type_blocks",
        "Forbidden action type blocks",
        [FAILURE_FORBIDDEN_ACTION_TYPE, FAILURE_OUTSIDE_SANDBOX_SCOPE],
        request=_request(action_contract=_contract(action_type="switch_app")),
    )


def _outside_sandbox_scope_blocks() -> dict[str, Any]:
    return _blocked_scenario(
        "outside_sandbox_scope_blocks",
        "Target outside sandbox scope blocks",
        [FAILURE_OUTSIDE_SANDBOX_SCOPE],
        config=_config(allowed_target_id="other_sandbox_target"),
    )


def _readiness_not_ready_blocks() -> dict[str, Any]:
    return _blocked_scenario(
        "readiness_not_ready_blocks",
        "Unexpected readiness blocker blocks",
        [FAILURE_READINESS_NOT_READY],
        ["preview_only_contract"],
        request=_request(click_readiness=_blocked_readiness("preview_only_contract")),
    )


def _missing_emergency_stop_blocks() -> dict[str, Any]:
    return _blocked_scenario(
        "missing_emergency_stop_blocks",
        "Missing emergency stop blocks",
        [FAILURE_MISSING_EMERGENCY_STOP],
        config=_config(emergency_stop_available=False),
    )


def _missing_audit_plan_blocks() -> dict[str, Any]:
    return _blocked_scenario(
        "missing_audit_plan_blocks",
        "Missing audit plan blocks",
        [FAILURE_MISSING_AUDIT_PLAN],
        config=_config(audit_events_required=False),
    )


def _missing_action_contract_blocks() -> dict[str, Any]:
    return _blocked_scenario(
        "missing_action_contract_blocks",
        "Missing action contract blocks",
        [FAILURE_MISSING_ACTION_CONTRACT],
        request=_request(action_contract=None),
    )


def _missing_target_blocks() -> dict[str, Any]:
    return _blocked_scenario(
        "missing_target_blocks",
        "Missing target blocks",
        [FAILURE_MISSING_TARGET],
        ["missing_target"],
        config=_config(expected_readiness_blocker_codes=("missing_target",)),
        request=_request(
            visible_elements=[],
            click_readiness=_blocked_readiness("missing_target"),
        ),
    )


def _blocked_scenario(
    scenario_id: str,
    scenario_name: str,
    failure_reason_codes: list[str],
    blocker_codes: list[str] | None = None,
    *,
    config: SandboxExperimentConfig | None = None,
    request: SandboxExperimentRequest | None = None,
) -> dict[str, Any]:
    return _scenario(
        scenario_id,
        scenario_name,
        _expected_outcome(
            status="blocked",
            gate_passed=False,
            failure_reason_codes=failure_reason_codes,
            blocker_codes=blocker_codes or [],
            audit_event_names=_blocked_events(),
        ),
        config=config,
        request=request,
    )


_SCENARIO_BUILDERS = {
    "dry_run_success_all_gates_pass": _dry_run_success_all_gates_pass,
    "real_action_disabled_skips_non_dry_run": _real_action_disabled_skips_non_dry_run,
    "missing_user_approval_blocks": _missing_user_approval_blocks,
    "stale_observation_blocks": _stale_observation_blocks,
    "high_risk_target_blocks": _high_risk_target_blocks,
    "unknown_risk_target_blocks": _unknown_risk_target_blocks,
    "low_confidence_target_blocks": _low_confidence_target_blocks,
    "invalid_bbox_blocks": _invalid_bbox_blocks,
    "bbox_center_mismatch_blocks": _bbox_center_mismatch_blocks,
    "missing_viewport_or_coordinate_space_blocks": _missing_viewport_or_coordinate_space_blocks,
    "missing_post_action_verification_blocks": _missing_post_action_verification_blocks,
    "forbidden_action_type_blocks": _forbidden_action_type_blocks,
    "outside_sandbox_scope_blocks": _outside_sandbox_scope_blocks,
    "readiness_not_ready_blocks": _readiness_not_ready_blocks,
    "missing_emergency_stop_blocks": _missing_emergency_stop_blocks,
    "missing_audit_plan_blocks": _missing_audit_plan_blocks,
    "missing_action_contract_blocks": _missing_action_contract_blocks,
    "missing_target_blocks": _missing_target_blocks,
}


def _expected_outcome(
    *,
    status: str,
    gate_passed: bool,
    dry_run: bool = True,
    real_action_enabled: bool = False,
    real_action_skipped: bool = False,
    failure_reason_codes: list[str] | None = None,
    blocker_codes: list[str] | None = None,
    audit_event_names: list[str],
    post_action_verification_planned: bool = False,
    real_action_attempted: bool = False,
) -> dict[str, Any]:
    return {
        "status": status,
        "gate_passed": gate_passed,
        "dry_run": dry_run,
        "real_action_enabled": real_action_enabled,
        "real_action_skipped": real_action_skipped,
        "failure_reason_codes": list(failure_reason_codes or []),
        "blocker_codes": list(blocker_codes or []),
        "audit_event_names": list(audit_event_names),
        "post_action_verification_planned": post_action_verification_planned,
        "real_action_attempted": real_action_attempted,
    }


def _actual_outcome(
    result: SandboxExperimentResult,
    request: SandboxExperimentRequest,
) -> dict[str, Any]:
    audit_event_names = _audit_event_names(result)
    readiness = request.click_readiness if isinstance(request.click_readiness, dict) else {}
    return {
        "status": result.status,
        "gate_passed": result.gate_passed,
        "dry_run": result.dry_run,
        "real_action_enabled": result.real_action_enabled,
        "real_action_skipped": EVENT_SANDBOX_REAL_ACTION_SKIPPED in audit_event_names,
        "failure_reason_codes": list(result.failure_reasons),
        "blocker_codes": _readiness_blocker_codes(readiness),
        "audit_event_names": audit_event_names,
        "post_action_verification_planned": (
            EVENT_SANDBOX_POST_ACTION_VERIFICATION_PLANNED in audit_event_names
        ),
        "target_risk_hint": _target_risk_hint(request),
        "target_confidence": _target_confidence(request),
        "readiness_ready": bool(readiness.get("ready")) if readiness else False,
        "action_type": _action_type(request),
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
        "failure_reason_codes",
        "blocker_codes",
        "audit_event_names",
        "post_action_verification_planned",
        "real_action_attempted",
    ]:
        if expected.get(field) != actual.get(field):
            failures.append(
                f"{field} expected {expected.get(field)!r} but got {actual.get(field)!r}"
            )

    if actual.get("real_action_attempted") is True:
        failures.append("real_action_attempted must remain false")

    return {
        "passed": not failures,
        "failures": failures,
        "expected_outcome": expected,
        "actual_outcome": actual,
    }


def _summary(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    failed = [scenario for scenario in scenarios if not scenario["passed"]]
    return {
        "total_scenario_count": len(scenarios),
        "passed_scenario_count": len(scenarios) - len(failed),
        "failed_scenario_count": len(failed),
        "scenarios_with_failures": [scenario["scenario_id"] for scenario in failed],
        "all_expected_outcomes_passed": not failed,
        "gate_passed_count": sum(1 for scenario in scenarios if scenario["gate_passed"]),
        "gate_blocked_count": sum(1 for scenario in scenarios if not scenario["gate_passed"]),
        "dry_run_scenario_count": sum(1 for scenario in scenarios if scenario["dry_run"]),
        "real_action_enabled_count": sum(1 for scenario in scenarios if scenario["real_action_enabled"]),
        "real_action_skipped_count": sum(1 for scenario in scenarios if scenario["real_action_skipped"]),
        "real_action_attempted_count": sum(
            1 for scenario in scenarios if scenario["actual_outcome"]["real_action_attempted"]
        ),
        "post_action_verification_planned_count": sum(
            1 for scenario in scenarios if scenario["post_action_verification_planned"]
        ),
        "failure_reason_codes": _code_summary(scenarios, "failure_reason_codes"),
        "blocker_codes": _code_summary(scenarios, "blocker_codes"),
        "audit_event_names": _code_summary(scenarios, "audit_event_names"),
    }


def _trace(
    definition: dict[str, Any],
    result: SandboxExperimentResult,
    actual_outcome: dict[str, Any],
) -> dict[str, Any]:
    return {
        "scenario_id": definition["scenario_id"],
        "scenario_name": definition["scenario_name"],
        "result_status": result.status,
        "gate_passed": result.gate_passed,
        "dry_run": result.dry_run,
        "real_action_enabled": result.real_action_enabled,
        "real_action_skipped": actual_outcome["real_action_skipped"],
        "failure_reason_codes": list(result.failure_reasons),
        "blocker_codes": list(actual_outcome["blocker_codes"]),
        "audit_event_names": _audit_event_names(result),
        "post_action_verification_planned": actual_outcome["post_action_verification_planned"],
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


def _readiness_blocker_codes(readiness: dict[str, Any]) -> list[str]:
    codes = readiness.get("blocker_codes")
    if not isinstance(codes, list):
        return []
    return [str(code) for code in codes if str(code)]


def _target_risk_hint(request: SandboxExperimentRequest) -> str:
    contract = request.action_contract if isinstance(request.action_contract, dict) else {}
    risk_hint = str(contract.get("target_risk_hint") or "").strip()
    if risk_hint:
        return risk_hint

    element = _first_visible_element(request)
    return str(element.get("risk_hint") or "") if element else ""


def _target_confidence(request: SandboxExperimentRequest) -> float | None:
    contract = request.action_contract if isinstance(request.action_contract, dict) else {}
    value = _finite_float(contract.get("target_confidence"))
    if value is not None:
        return value

    element = _first_visible_element(request)
    return _finite_float(element.get("confidence")) if element else None


def _action_type(request: SandboxExperimentRequest) -> str:
    contract = request.action_contract if isinstance(request.action_contract, dict) else {}
    return str(contract.get("type") or "")


def _first_visible_element(request: SandboxExperimentRequest) -> dict[str, Any] | None:
    for element in request.visible_elements:
        if isinstance(element, dict):
            return element
    return None


def _finite_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number


def _code_summary(scenarios: list[dict[str, Any]], field: str) -> dict[str, list[str]]:
    summary: dict[str, list[str]] = {}
    for scenario in scenarios:
        scenario_id = str(scenario.get("scenario_id") or "")
        values = scenario.get(field)
        if not isinstance(values, list):
            continue
        for value in values:
            text = str(value or "")
            if not text:
                continue
            summary.setdefault(text, [])
            if scenario_id and scenario_id not in summary[text]:
                summary[text].append(scenario_id)
    return summary


def _dry_run_success_events() -> list[str]:
    return [
        EVENT_SANDBOX_EXPERIMENT_REQUESTED,
        EVENT_SANDBOX_GATE_PASSED,
        EVENT_SANDBOX_POST_ACTION_VERIFICATION_PLANNED,
        EVENT_SANDBOX_DRY_RUN_COMPLETED,
    ]


def _blocked_events() -> list[str]:
    return [
        EVENT_SANDBOX_EXPERIMENT_REQUESTED,
        EVENT_SANDBOX_GATE_BLOCKED,
    ]


def _blocked_readiness(*blocker_codes: str) -> dict[str, Any]:
    return {
        "ready": False,
        "status": "blocked",
        "blocker_codes": list(blocker_codes),
    }


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
