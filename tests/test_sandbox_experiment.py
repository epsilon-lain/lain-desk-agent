from __future__ import annotations

import inspect
import unittest
from datetime import datetime, timedelta, timezone

import _path  # noqa: F401
from lain_desk_agent import sandbox_experiment
from lain_desk_agent.sandbox_experiment import (
    EVENT_SANDBOX_DRY_RUN_COMPLETED,
    EVENT_SANDBOX_EXPERIMENT_REQUESTED,
    EVENT_SANDBOX_GATE_BLOCKED,
    EVENT_SANDBOX_GATE_PASSED,
    EVENT_SANDBOX_POST_ACTION_VERIFICATION_PLANNED,
    EVENT_SANDBOX_REAL_ACTION_SKIPPED,
    FAILURE_FORBIDDEN_ACTION_TYPE,
    FAILURE_HIGH_RISK_TARGET,
    FAILURE_INVALID_TARGET_GEOMETRY,
    FAILURE_MISSING_PHASE7_CHECKLIST,
    FAILURE_MISSING_POST_ACTION_VERIFICATION,
    FAILURE_MISSING_USER_APPROVAL,
    FAILURE_OUTSIDE_SANDBOX_SCOPE,
    FAILURE_READINESS_NOT_READY,
    FAILURE_REAL_ACTION_DISABLED,
    FAILURE_STALE_OBSERVATION,
    REQUIRED_PHASE7_CHECKLIST_ITEMS,
    SandboxExperimentConfig,
    SandboxExperimentRequest,
    run_sandbox_experiment,
    validate_phase7_gate,
)


NOW = datetime(2026, 1, 1, 0, 0, 5, tzinfo=timezone.utc)
OBSERVATION_TIMESTAMP = "2026-01-01T00:00:00Z"


class SandboxExperimentTests(unittest.TestCase):
    def test_dry_run_experiment_succeeds_when_all_gates_are_satisfied(self) -> None:
        result = run_sandbox_experiment(_config(), _request())

        self.assertEqual(result.status, "dry_run_completed")
        self.assertIs(result.gate_passed, True)
        self.assertIs(result.simulated, True)
        self.assertIs(result.real_action_attempted, False)
        self.assertEqual(result.failure_reasons, [])
        self.assertEqual(
            _event_types(result),
            [
                EVENT_SANDBOX_EXPERIMENT_REQUESTED,
                EVENT_SANDBOX_GATE_PASSED,
                EVENT_SANDBOX_POST_ACTION_VERIFICATION_PLANNED,
                EVENT_SANDBOX_DRY_RUN_COMPLETED,
            ],
        )
        self.assertTrue(result.validation["passed"])
        self.assertTrue(result.to_dict()["dry_run"])

    def test_real_action_is_skipped_when_real_action_enabled_is_false(self) -> None:
        result = run_sandbox_experiment(
            _config(dry_run=False, real_action_enabled=False),
            _request(),
        )

        self.assertEqual(result.status, "real_action_skipped")
        self.assertIs(result.gate_passed, True)
        self.assertIs(result.simulated, True)
        self.assertIs(result.real_action_attempted, False)
        self.assertEqual(result.failure_reasons, [FAILURE_REAL_ACTION_DISABLED])
        self.assertEqual(_event_types(result)[-1], EVENT_SANDBOX_REAL_ACTION_SKIPPED)

    def test_missing_user_approval_blocks(self) -> None:
        result = run_sandbox_experiment(_config(), _request(user_approved=False))

        self.assertEqual(result.status, "blocked")
        self.assertIn(FAILURE_MISSING_USER_APPROVAL, result.failure_reasons)
        self.assertEqual(_event_types(result)[-1], EVENT_SANDBOX_GATE_BLOCKED)
        self.assertIs(result.real_action_attempted, False)

    def test_missing_phase7_checklist_blocks(self) -> None:
        result = run_sandbox_experiment(
            _config(phase7_checklist={}),
            _request(),
        )

        self.assertEqual(result.status, "blocked")
        self.assertIn(FAILURE_MISSING_PHASE7_CHECKLIST, result.failure_reasons)

    def test_outside_sandbox_scope_blocks(self) -> None:
        result = run_sandbox_experiment(
            _config(allowed_target_id="other_target"),
            _request(),
        )

        self.assertEqual(result.status, "blocked")
        self.assertIn(FAILURE_OUTSIDE_SANDBOX_SCOPE, result.failure_reasons)

    def test_high_risk_target_blocks(self) -> None:
        contract = _contract(target_risk_hint="high_risk", risk="high")
        element = _visible_element(risk_hint="high_risk")
        safety_decision = {"decision": "needs_approval", "risk": "high"}

        result = run_sandbox_experiment(
            _config(),
            _request(
                action_contract=contract,
                visible_elements=[element],
                safety_decision=safety_decision,
            ),
        )

        self.assertEqual(result.status, "blocked")
        self.assertIn(FAILURE_HIGH_RISK_TARGET, result.failure_reasons)

    def test_stale_observation_blocks(self) -> None:
        stale_timestamp = (NOW - timedelta(seconds=30)).isoformat().replace("+00:00", "Z")

        result = run_sandbox_experiment(
            _config(),
            _request(observation_timestamp=stale_timestamp),
        )

        self.assertEqual(result.status, "blocked")
        self.assertIn(FAILURE_STALE_OBSERVATION, result.failure_reasons)

    def test_invalid_bbox_or_center_blocks(self) -> None:
        contract = _contract(center={"x": 99, "y": 99})

        result = run_sandbox_experiment(_config(), _request(action_contract=contract))

        self.assertEqual(result.status, "blocked")
        self.assertIn(FAILURE_INVALID_TARGET_GEOMETRY, result.failure_reasons)

    def test_missing_post_action_verification_blocks(self) -> None:
        result = run_sandbox_experiment(
            _config(),
            _request(post_action_verification_plan=None),
        )

        self.assertEqual(result.status, "blocked")
        self.assertIn(FAILURE_MISSING_POST_ACTION_VERIFICATION, result.failure_reasons)

    def test_forbidden_action_type_blocks(self) -> None:
        contract = _contract(action_type="switch_app")

        result = run_sandbox_experiment(_config(), _request(action_contract=contract))

        self.assertEqual(result.status, "blocked")
        self.assertIn(FAILURE_FORBIDDEN_ACTION_TYPE, result.failure_reasons)
        self.assertIs(result.real_action_attempted, False)

    def test_expected_readiness_blocker_allows_dry_run_only(self) -> None:
        config = _config(expected_readiness_blocker_codes=("preview_only_contract",))
        request = _request(
            click_readiness={
                "ready": False,
                "status": "blocked",
                "blocker_codes": ["preview_only_contract"],
            }
        )

        result = run_sandbox_experiment(config, request)

        self.assertEqual(result.status, "dry_run_completed")
        self.assertEqual(result.failure_reasons, [])

    def test_unexpected_readiness_blocker_blocks(self) -> None:
        request = _request(
            click_readiness={
                "ready": False,
                "status": "blocked",
                "blocker_codes": ["preview_only_contract"],
            }
        )

        validation = validate_phase7_gate(_config(), request)

        self.assertFalse(validation["passed"])
        self.assertIn(FAILURE_READINESS_NOT_READY, validation["failure_reasons"])

    def test_no_real_desktop_actuation_api_is_imported_or_called(self) -> None:
        source = inspect.getsource(sandbox_experiment)

        forbidden_imports = [
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
        ]
        for forbidden_import in forbidden_imports:
            with self.subTest(forbidden_import=forbidden_import):
                self.assertNotIn(forbidden_import, source)


def _config(**overrides: object) -> SandboxExperimentConfig:
    values = {
        "experiment_name": "phase8_fixture_click",
        "dry_run": True,
        "real_action_enabled": False,
        "allowed_action_type": "click",
        "allowed_window_id": "sandbox_window",
        "allowed_target_id": "element_0001",
        "phase7_checklist": _phase7_checklist(),
        "emergency_stop_available": True,
    }
    values.update(overrides)
    return SandboxExperimentConfig(**values)


def _request(**overrides: object) -> SandboxExperimentRequest:
    values = {
        "user_approved": True,
        "action_contract": _contract(),
        "click_readiness": {"ready": True, "status": "ready", "blocker_codes": []},
        "visible_elements": [_visible_element()],
        "safety_decision": {"decision": "allowed", "risk": "low"},
        "screen": _screen(),
        "observation_timestamp": OBSERVATION_TIMESTAMP,
        "post_action_verification_plan": _verification_plan(),
        "sandbox_window_id": "sandbox_window",
        "current_time": NOW,
        "audit_context": {"run_id": "test_run_0001"},
    }
    values.update(overrides)
    return SandboxExperimentRequest(**values)


def _contract(
    action_type: str = "click",
    target_risk_hint: str = "normal",
    risk: str = "low",
    bbox: dict[str, int] | None = None,
    center: dict[str, int] | None = None,
) -> dict[str, object]:
    return {
        "action_id": "action_0001",
        "source_proposal_id": "proposal_0001",
        "type": action_type,
        "risk": risk,
        "target_element_id": "element_0001",
        "target_label": "sandbox test button",
        "target_role": "button",
        "target_confidence": 0.96,
        "target_source": "ui_tree",
        "target_risk_hint": target_risk_hint,
        "target_timestamp": OBSERVATION_TIMESTAMP,
        "bbox": bbox or {"x": 10, "y": 20, "width": 80, "height": 24},
        "center": center or {"x": 50, "y": 32},
        "status": "approved_for_execution",
        "executed": False,
    }


def _visible_element(risk_hint: str = "normal") -> dict[str, object]:
    return {
        "id": "element_0001",
        "label": "sandbox test button",
        "text": "sandbox test button",
        "role": "button",
        "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
        "center": {"x": 50, "y": 32},
        "confidence": 0.96,
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


def _verification_plan() -> dict[str, object]:
    return {
        "enabled": True,
        "method": "fixture_state_assertion",
        "expected_state": "sandbox target selected",
    }


def _phase7_checklist() -> dict[str, bool]:
    return {item: True for item in REQUIRED_PHASE7_CHECKLIST_ITEMS}


def _event_types(result: object) -> list[str]:
    return [str(event.get("type") or "") for event in result.audit_events]


if __name__ == "__main__":
    unittest.main()
