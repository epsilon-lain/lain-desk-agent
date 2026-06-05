from __future__ import annotations

import inspect
import unittest
from datetime import datetime, timedelta, timezone

import _path  # noqa: F401
from lain_desk_agent import phase9_experiment
from lain_desk_agent.phase9_experiment import (
    EVENT_PHASE9_DRY_RUN_COMPLETED,
    EVENT_PHASE9_EMERGENCY_STOP_CHECKED,
    EVENT_PHASE9_EXPERIMENT_REQUESTED,
    EVENT_PHASE9_GATE_BLOCKED,
    EVENT_PHASE9_GATE_PASSED,
    EVENT_PHASE9_MOCK_APPROVAL_CHECKED,
    EVENT_PHASE9_POST_ACTION_VERIFICATION_PLANNED,
    EVENT_PHASE9_REAL_ACTION_SKIPPED,
    EVENT_PHASE9_ROLLBACK_PLAN_RECORDED,
    FAILURE_EMERGENCY_STOP_ACTIVE,
    FAILURE_MISSING_ROLLBACK_PLAN,
    PHASE9_MINIMAL_SCENARIO_IDS,
    PHASE9_REPORT_FIELDS,
    MockApprovalState,
    MockEmergencyStopState,
    MockPostActionVerificationPlan,
    MockRollbackPlan,
    Phase9ExperimentConfig,
    Phase9ExperimentRequest,
    build_phase9_experiment_report,
    run_phase9_experiment,
    validate_phase9_gate,
)
from lain_desk_agent.sandbox_experiment import (
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
)


NOW = datetime(2026, 1, 1, 0, 0, 5, tzinfo=timezone.utc)
OBSERVATION_TIMESTAMP = "2026-01-01T00:00:00Z"
OBSERVATION_ID = "observation_0001"
ACTION_ID = "sandbox_action_0001"
TARGET_ID = "sandbox_target_button"
WINDOW_ID = "sandbox_window"


class Phase9ExperimentTests(unittest.TestCase):
    def test_dry_run_success_reports_phase8_shape(self) -> None:
        result = run_phase9_experiment(
            _config(),
            _request(expected_outcome=_expected(status="dry_run_completed", gate_passed=True)),
        )
        scenario = result.to_dict()

        self.assertEqual(result.status, "dry_run_completed")
        self.assertIs(result.gate_passed, True)
        self.assertIs(result.real_action_attempted, False)
        self.assertIs(result.real_action_skipped, False)
        self.assertEqual(result.failure_reason_codes, [])
        self.assertTrue(set(PHASE9_REPORT_FIELDS).issubset(scenario))
        self.assertIs(scenario["passed"], True)
        self.assertEqual(
            result.audit_event_names(),
            [
                EVENT_PHASE9_EXPERIMENT_REQUESTED,
                EVENT_PHASE9_MOCK_APPROVAL_CHECKED,
                EVENT_PHASE9_EMERGENCY_STOP_CHECKED,
                EVENT_PHASE9_GATE_PASSED,
                EVENT_PHASE9_POST_ACTION_VERIFICATION_PLANNED,
                EVENT_PHASE9_ROLLBACK_PLAN_RECORDED,
                EVENT_PHASE9_DRY_RUN_COMPLETED,
            ],
        )
        self.assertTrue(scenario["post_action_verification_planned"])
        self.assertTrue(scenario["trace"]["rollback_plan_recorded"])
        self.assertEqual(scenario["target_risk_hint"], "normal")
        self.assertEqual(scenario["target_confidence"], 0.96)
        self.assertEqual(scenario["action_type"], "click")

    def test_non_dry_run_with_real_actions_disabled_is_skipped_after_gate(self) -> None:
        result = run_phase9_experiment(
            _config(dry_run=False, real_action_enabled=False),
            _request(
                scenario_id="real_action_disabled_skips_non_dry_run",
                expected_outcome=_expected(
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
            ),
        )

        self.assertEqual(result.status, "real_action_skipped")
        self.assertIs(result.gate_passed, True)
        self.assertIs(result.real_action_skipped, True)
        self.assertIs(result.real_action_attempted, False)
        self.assertEqual(result.failure_reason_codes, [FAILURE_REAL_ACTION_DISABLED])
        self.assertIs(result.to_dict()["passed"], True)

    def test_real_action_enabled_without_future_gate_blocks_and_skips(self) -> None:
        result = run_phase9_experiment(
            _config(real_action_enabled=True),
            _request(),
        )

        self.assertEqual(result.status, "real_action_skipped")
        self.assertIs(result.gate_passed, False)
        self.assertIs(result.real_action_skipped, True)
        self.assertIn(FAILURE_REAL_ACTION_DISABLED, result.failure_reason_codes)
        self.assertEqual(result.audit_event_names()[-2:], [EVENT_PHASE9_GATE_BLOCKED, EVENT_PHASE9_REAL_ACTION_SKIPPED])
        self.assertIs(result.real_action_attempted, False)

    def test_missing_user_approval_blocks(self) -> None:
        result = run_phase9_experiment(
            _config(),
            _request(
                scenario_id="missing_user_approval_blocks",
                approval=MockApprovalState(present=True, user_approved=False),
            ),
        )

        self.assert_blocked_with(result, FAILURE_MISSING_USER_APPROVAL)

    def test_approval_binding_mismatch_blocks(self) -> None:
        result = run_phase9_experiment(
            _config(),
            _request(approval=_approval(action_contract_id="other_action")),
        )

        self.assert_blocked_with(result, FAILURE_MISSING_USER_APPROVAL)

    def test_stale_observation_blocks(self) -> None:
        stale_timestamp = (NOW - timedelta(seconds=30)).isoformat().replace("+00:00", "Z")
        result = run_phase9_experiment(
            _config(expected_readiness_blocker_codes=("stale_observation",)),
            _request(
                scenario_id="stale_observation_blocks",
                observation_timestamp=stale_timestamp,
                click_readiness=_blocked_readiness("stale_observation"),
            ),
        )

        self.assert_blocked_with(result, FAILURE_STALE_OBSERVATION)
        self.assertEqual(result.blocker_codes, ["stale_observation"])

    def test_high_risk_and_unknown_risk_targets_block(self) -> None:
        cases = [
            (
                "high_risk_target_blocks",
                _contract(risk="high", target_risk_hint="high_risk"),
                _visible_element(risk_hint="high_risk"),
                "high_risk_requires_approval",
            ),
            (
                "high_risk_target_blocks",
                _contract(target_risk_hint="unknown"),
                _visible_element(risk_hint="unknown"),
                "unknown_risk_target",
            ),
        ]

        for scenario_id, contract, element, blocker_code in cases:
            with self.subTest(blocker_code=blocker_code):
                result = run_phase9_experiment(
                    _config(expected_readiness_blocker_codes=(blocker_code,)),
                    _request(
                        scenario_id=scenario_id,
                        action_contract=contract,
                        visible_elements=[element],
                        click_readiness=_blocked_readiness(blocker_code),
                        safety_decision={"decision": "needs_approval", "risk": "high"},
                    ),
                )

                self.assert_blocked_with(result, FAILURE_HIGH_RISK_TARGET)
                self.assertIn(blocker_code, result.blocker_codes)

    def test_low_confidence_target_blocks(self) -> None:
        result = run_phase9_experiment(
            _config(expected_readiness_blocker_codes=("low_confidence_target",)),
            _request(
                action_contract=_contract(target_confidence=0.2),
                visible_elements=[_visible_element(confidence=0.2)],
                click_readiness=_blocked_readiness("low_confidence_target"),
            ),
        )

        self.assert_blocked_with(result, FAILURE_LOW_CONFIDENCE_TARGET)

    def test_invalid_bbox_or_center_blocks(self) -> None:
        cases = [
            _contract(bbox={"x": 10, "y": 20, "width": 0, "height": 24}),
            _contract(center={"x": 99, "y": 99}),
        ]

        for contract in cases:
            with self.subTest(contract=contract):
                result = run_phase9_experiment(
                    _config(expected_readiness_blocker_codes=("invalid_geometry",)),
                    _request(
                        action_contract=contract,
                        click_readiness=_blocked_readiness("invalid_geometry"),
                    ),
                )

                self.assert_blocked_with(result, FAILURE_INVALID_TARGET_GEOMETRY)

    def test_missing_target_blocks(self) -> None:
        result = run_phase9_experiment(
            _config(expected_readiness_blocker_codes=("missing_target",)),
            _request(visible_elements=[], click_readiness=_blocked_readiness("missing_target")),
        )

        self.assert_blocked_with(result, FAILURE_MISSING_TARGET)

    def test_missing_action_contract_blocks(self) -> None:
        result = run_phase9_experiment(
            _config(),
            _request(scenario_id="missing_action_contract_blocks", action_contract=None),
        )

        self.assert_blocked_with(result, FAILURE_MISSING_ACTION_CONTRACT)

    def test_missing_audit_plan_blocks(self) -> None:
        result = run_phase9_experiment(
            _config(audit_plan_present=False),
            _request(scenario_id="missing_audit_plan_blocks"),
        )

        self.assert_blocked_with(result, FAILURE_MISSING_AUDIT_PLAN)

    def test_missing_post_action_verification_blocks(self) -> None:
        result = run_phase9_experiment(
            _config(),
            _request(post_action_verification_plan=None),
        )

        self.assert_blocked_with(result, FAILURE_MISSING_POST_ACTION_VERIFICATION)

    def test_missing_and_active_emergency_stop_block(self) -> None:
        missing = run_phase9_experiment(_config(), _request(emergency_stop=None))
        active = run_phase9_experiment(
            _config(),
            _request(emergency_stop=MockEmergencyStopState(available=True, active=True)),
        )

        self.assert_blocked_with(missing, FAILURE_MISSING_EMERGENCY_STOP)
        self.assert_blocked_with(active, FAILURE_EMERGENCY_STOP_ACTIVE)
        self.assertIn(FAILURE_MISSING_EMERGENCY_STOP, active.failure_reason_codes)

    def test_missing_rollback_plan_blocks(self) -> None:
        result = run_phase9_experiment(_config(), _request(rollback_plan=None))

        self.assert_blocked_with(result, FAILURE_MISSING_ROLLBACK_PLAN)

    def test_forbidden_action_type_blocks(self) -> None:
        result = run_phase9_experiment(
            _config(),
            _request(action_contract=_contract(action_type="switch_app")),
        )

        self.assert_blocked_with(result, FAILURE_FORBIDDEN_ACTION_TYPE)
        self.assertIn(FAILURE_OUTSIDE_SANDBOX_SCOPE, result.failure_reason_codes)

    def test_outside_sandbox_scope_blocks(self) -> None:
        result = run_phase9_experiment(
            _config(),
            _request(sandbox_scope={**_scope(), "target_id": "other_target"}),
        )

        self.assert_blocked_with(result, FAILURE_OUTSIDE_SANDBOX_SCOPE)

    def test_too_broad_sandbox_scope_blocks(self) -> None:
        result = run_phase9_experiment(
            _config(),
            _request(sandbox_scope={**_scope(), "external_websites_allowed": True}),
        )

        self.assert_blocked_with(result, FAILURE_OUTSIDE_SANDBOX_SCOPE)

    def test_readiness_not_ready_blocks_unexpected_blocker(self) -> None:
        result = run_phase9_experiment(
            _config(),
            _request(click_readiness=_blocked_readiness("preview_only_contract")),
        )

        self.assert_blocked_with(result, FAILURE_READINESS_NOT_READY)
        self.assertEqual(result.blocker_codes, ["preview_only_contract"])

    def test_validate_phase9_gate_reuses_phase7_checks(self) -> None:
        validation = validate_phase9_gate(_config(), _request())
        check_names = {str(check.get("name") or "") for check in validation["checks"]}

        self.assertTrue(validation["passed"])
        for expected_check in [
            "phase7_checklist",
            "target_geometry",
            "observation_freshness",
            "click_readiness",
            "post_action_verification",
            "sandbox_scope_limited",
            "mock_rollback_plan",
        ]:
            with self.subTest(expected_check=expected_check):
                self.assertIn(expected_check, check_names)

    def test_phase9_report_is_phase8_compatible_and_safe(self) -> None:
        results = [
            run_phase9_experiment(
                _config(),
                _request(expected_outcome=_expected(status="dry_run_completed", gate_passed=True)),
            ),
            run_phase9_experiment(
                _config(dry_run=False),
                _request(
                    scenario_id="real_action_disabled_skips_non_dry_run",
                    expected_outcome=_expected(
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
                ),
            ),
        ]

        report = build_phase9_experiment_report(results)

        self.assertEqual(report["report_type"], "phase9_minimal_sandbox_experiment")
        self.assertEqual(report["phase"], "phase9_1")
        self.assertIs(report["external_llm_calls"], False)
        self.assertIs(report["real_desktop_actions"], False)
        self.assertEqual(report["summary"]["real_action_enabled_count"], 0)
        self.assertEqual(report["summary"]["real_action_attempted_count"], 0)
        self.assertEqual(report["summary"]["real_action_skipped_count"], 1)
        for scenario in report["scenarios"]:
            with self.subTest(scenario=scenario["scenario_id"]):
                self.assertTrue(set(PHASE9_REPORT_FIELDS).issubset(scenario))
                self.assertIs(scenario["passed"], True)
                self.assertIs(scenario["actual_outcome"]["real_action_attempted"], False)

    def test_config_defaults_stay_dry_run_and_real_actions_disabled(self) -> None:
        config = Phase9ExperimentConfig()

        self.assertIs(config.dry_run, True)
        self.assertIs(config.real_action_enabled, False)

    def test_minimal_scenario_subset_matches_phase9_design(self) -> None:
        self.assertEqual(
            PHASE9_MINIMAL_SCENARIO_IDS,
            (
                "dry_run_success_all_gates_pass",
                "real_action_disabled_skips_non_dry_run",
                "missing_user_approval_blocks",
                "stale_observation_blocks",
                "high_risk_target_blocks",
                "missing_audit_plan_blocks",
                "missing_action_contract_blocks",
            ),
        )

    def test_no_real_desktop_actuation_api_is_imported_or_called(self) -> None:
        source = inspect.getsource(phase9_experiment)

        forbidden_fragments = [
            '"/execute"',
            "execute_action_contract",
            "import pyautogui",
            "from pyautogui",
            "import pynput",
            "from pynput",
            "import keyboard",
            "from keyboard",
            "import mouse",
            "from mouse",
            "import win32api",
            "from win32api",
            "ctypes",
            "mouse_event",
            "SendInput",
            "xdotool",
            "osascript",
            "AppleScript",
        ]
        for fragment in forbidden_fragments:
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, source)

    def assert_blocked_with(self, result: object, failure_reason: str) -> None:
        self.assertEqual(result.status, "blocked")
        self.assertIs(result.gate_passed, False)
        self.assertIs(result.real_action_attempted, False)
        self.assertIn(failure_reason, result.failure_reason_codes)
        self.assertEqual(result.audit_event_names()[-1], EVENT_PHASE9_GATE_BLOCKED)
        self.assertNotIn(EVENT_PHASE9_DRY_RUN_COMPLETED, result.audit_event_names())


def _config(**overrides: object) -> Phase9ExperimentConfig:
    values = {
        "experiment_id": "phase9_minimal_fixture_click",
        "dry_run": True,
        "real_action_enabled": False,
        "allowed_action_type": "click",
        "allowed_window_id": WINDOW_ID,
        "allowed_target_id": TARGET_ID,
        "phase7_checklist": _phase7_checklist(),
    }
    values.update(overrides)
    return Phase9ExperimentConfig(**values)


def _request(**overrides: object) -> Phase9ExperimentRequest:
    values = {
        "scenario_id": "dry_run_success_all_gates_pass",
        "scenario_name": "Dry-run success with all Phase 7 gates satisfied",
        "expected_outcome": {},
        "sandbox_scope": _scope(),
        "approval": _approval(),
        "emergency_stop": MockEmergencyStopState(
            available=True,
            active=False,
            checked_at=NOW.isoformat().replace("+00:00", "Z"),
        ),
        "post_action_verification_plan": MockPostActionVerificationPlan(
            present=True,
            planned=True,
            simulated=True,
        ),
        "rollback_plan": MockRollbackPlan(present=True, simulated=True, sandbox_only=True),
        "action_contract": _contract(),
        "click_readiness": {"ready": True, "status": "ready", "blocker_codes": []},
        "visible_elements": [_visible_element()],
        "safety_decision": {"decision": "allowed", "risk": "low"},
        "screen": _screen(),
        "observation_timestamp": OBSERVATION_TIMESTAMP,
        "observation_id": OBSERVATION_ID,
        "sandbox_window_id": WINDOW_ID,
        "current_time": NOW,
        "audit_context": {"run_id": "phase9_test_run_0001"},
        "notes": ("fixture-only",),
    }
    values.update(overrides)
    return Phase9ExperimentRequest(**values)


def _expected(
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
) -> dict[str, object]:
    if audit_event_names is None:
        audit_event_names = [
            EVENT_PHASE9_EXPERIMENT_REQUESTED,
            EVENT_PHASE9_MOCK_APPROVAL_CHECKED,
            EVENT_PHASE9_EMERGENCY_STOP_CHECKED,
            EVENT_PHASE9_GATE_PASSED,
            EVENT_PHASE9_POST_ACTION_VERIFICATION_PLANNED,
            EVENT_PHASE9_ROLLBACK_PLAN_RECORDED,
            EVENT_PHASE9_DRY_RUN_COMPLETED,
        ]
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
        "real_action_attempted": False,
    }


def _approval(
    action_contract_id: str = ACTION_ID,
    target_id: str = TARGET_ID,
    observation_id: str = OBSERVATION_ID,
) -> MockApprovalState:
    return MockApprovalState(
        present=True,
        user_approved=True,
        action_contract_id=action_contract_id,
        target_id=target_id,
        observation_id=observation_id,
        approved_at=OBSERVATION_TIMESTAMP,
        expires_at=(NOW + timedelta(seconds=5)).isoformat().replace("+00:00", "Z"),
    )


def _scope() -> dict[str, object]:
    return {
        "window_id": WINDOW_ID,
        "target_id": TARGET_ID,
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


def _contract(
    action_type: str = "click",
    risk: str = "low",
    target_risk_hint: str = "normal",
    target_confidence: float = 0.96,
    bbox: dict[str, int] | None = None,
    center: dict[str, int] | None = None,
) -> dict[str, object]:
    return {
        "action_id": ACTION_ID,
        "source_proposal_id": "sandbox_proposal_0001",
        "type": action_type,
        "risk": risk,
        "target_element_id": TARGET_ID,
        "target_label": "sandbox test button",
        "target_role": "button",
        "target_confidence": target_confidence,
        "target_source": "ui_tree",
        "target_risk_hint": target_risk_hint,
        "target_timestamp": OBSERVATION_TIMESTAMP,
        "bbox": bbox or {"x": 10, "y": 20, "width": 80, "height": 24},
        "center": center or {"x": 50, "y": 32},
        "status": "approved_for_execution",
        "executed": False,
    }


def _visible_element(risk_hint: str = "normal", confidence: float = 0.96) -> dict[str, object]:
    return {
        "id": TARGET_ID,
        "label": "sandbox test button",
        "text": "sandbox test button",
        "role": "button",
        "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
        "center": {"x": 50, "y": 32},
        "confidence": confidence,
        "source": "ui_tree",
        "risk_hint": risk_hint,
        "timestamp": OBSERVATION_TIMESTAMP,
    }


def _screen() -> dict[str, object]:
    return {
        "width": 200,
        "height": 120,
        "coordinate_space": "screen",
        "dpi_scale": 1.0,
    }


def _blocked_readiness(*blocker_codes: str) -> dict[str, object]:
    return {
        "ready": False,
        "status": "blocked",
        "blocker_codes": list(blocker_codes),
    }


def _phase7_checklist() -> dict[str, bool]:
    return {item: True for item in REQUIRED_PHASE7_CHECKLIST_ITEMS}


if __name__ == "__main__":
    unittest.main()
