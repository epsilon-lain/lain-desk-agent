from __future__ import annotations

import inspect
import unittest

import _path  # noqa: F401
from lain_desk_agent import sandbox_evaluation, sandbox_experiment
from lain_desk_agent.sandbox_evaluation import (
    evaluate_sandbox_experiment_scenario,
    evaluate_sandbox_experiment_scenarios,
    sandbox_evaluation_scenario_names,
)
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
    FAILURE_LOW_CONFIDENCE_TARGET,
    FAILURE_MISSING_POST_ACTION_VERIFICATION,
    FAILURE_MISSING_USER_APPROVAL,
    FAILURE_OUTSIDE_SANDBOX_SCOPE,
    FAILURE_READINESS_NOT_READY,
    FAILURE_REAL_ACTION_DISABLED,
    FAILURE_STALE_OBSERVATION,
)


EXPECTED_SCENARIOS = [
    "sandbox_dry_run_success",
    "real_action_disabled_skip",
    "missing_user_approval",
    "stale_observation",
    "high_risk_target",
    "unknown_risk_target",
    "low_confidence_target",
    "invalid_bbox_center",
    "missing_post_action_verification",
    "forbidden_action_type",
    "outside_sandbox_scope",
    "readiness_not_ready",
    "missing_emergency_stop",
]


class SandboxEvaluationTests(unittest.TestCase):
    def test_scenario_names_are_deterministic(self) -> None:
        self.assertEqual(sandbox_evaluation_scenario_names(), EXPECTED_SCENARIOS)

    def test_evaluation_summary_fields_are_deterministic(self) -> None:
        report = evaluate_sandbox_experiment_scenarios()

        self.assertEqual(report["report_type"], "sandbox_experiment_evaluation")
        self.assertEqual(report["phase"], "phase8_1")
        self.assertIs(report["external_llm_calls"], False)
        self.assertIs(report["real_desktop_actions"], False)
        self.assertEqual(report["scenario_count"], len(EXPECTED_SCENARIOS))

        summary = report["summary"]
        self.assertEqual(summary["total_scenario_count"], len(EXPECTED_SCENARIOS))
        self.assertEqual(summary["passed_scenario_count"], len(EXPECTED_SCENARIOS))
        self.assertEqual(summary["failed_scenario_count"], 0)
        self.assertIs(summary["all_expected_outcomes_passed"], True)
        self.assertEqual(summary["gate_passed_count"], 2)
        self.assertEqual(summary["gate_blocked_count"], len(EXPECTED_SCENARIOS) - 2)
        self.assertEqual(summary["real_action_skipped_count"], 1)
        self.assertEqual(summary["real_action_attempted_count"], 0)
        self.assertEqual(summary["post_action_verification_planned_count"], 2)
        self.assertEqual(summary["scenarios_with_failures"], [])

    def test_each_scenario_matches_expected_outcome(self) -> None:
        report = evaluate_sandbox_experiment_scenarios()

        for scenario in report["scenarios"]:
            with self.subTest(scenario=scenario["scenario"]):
                self.assertIs(scenario["passed"], True)
                self.assertEqual(scenario["pass_fail"], "pass")
                self.assertEqual(scenario["actual"]["status"], scenario["expected"]["status"])
                self.assertEqual(
                    scenario["actual"]["gate_passed"],
                    scenario["expected"]["gate_passed"],
                )
                self.assertEqual(
                    scenario["actual"]["audit_event_names"],
                    scenario["expected"]["audit_event_names"],
                )
                self.assertIs(scenario["actual"]["real_action_attempted"], False)
                self.assertIs(scenario["trace"]["real_action_enabled"], scenario["real_action_enabled"])
                self.assertEqual(
                    scenario["trace"]["failure_reasons"],
                    scenario["failure_reasons"],
                )

    def test_failure_reason_codes_are_reported_by_summary(self) -> None:
        report = evaluate_sandbox_experiment_scenarios()
        codes = report["summary"]["failure_reason_codes"]

        expected_code_scenarios = {
            FAILURE_MISSING_USER_APPROVAL: ["missing_user_approval"],
            FAILURE_STALE_OBSERVATION: ["stale_observation"],
            FAILURE_HIGH_RISK_TARGET: ["high_risk_target", "unknown_risk_target"],
            FAILURE_LOW_CONFIDENCE_TARGET: ["low_confidence_target"],
            FAILURE_INVALID_TARGET_GEOMETRY: ["invalid_bbox_center"],
            FAILURE_MISSING_POST_ACTION_VERIFICATION: ["missing_post_action_verification"],
            FAILURE_FORBIDDEN_ACTION_TYPE: ["forbidden_action_type"],
            FAILURE_OUTSIDE_SANDBOX_SCOPE: [
                "forbidden_action_type",
                "outside_sandbox_scope",
                "missing_emergency_stop",
            ],
            FAILURE_READINESS_NOT_READY: ["low_confidence_target", "readiness_not_ready"],
            FAILURE_REAL_ACTION_DISABLED: ["real_action_disabled_skip"],
        }

        for code, scenario_names in expected_code_scenarios.items():
            with self.subTest(code=code):
                self.assertEqual(codes[code], scenario_names)

    def test_audit_event_ordering_for_success_skip_and_blocked_paths(self) -> None:
        success = evaluate_sandbox_experiment_scenario("sandbox_dry_run_success")
        skipped = evaluate_sandbox_experiment_scenario("real_action_disabled_skip")
        blocked = evaluate_sandbox_experiment_scenario("missing_user_approval")

        self.assertEqual(
            success["audit_event_names"],
            [
                EVENT_SANDBOX_EXPERIMENT_REQUESTED,
                EVENT_SANDBOX_GATE_PASSED,
                EVENT_SANDBOX_POST_ACTION_VERIFICATION_PLANNED,
                EVENT_SANDBOX_DRY_RUN_COMPLETED,
            ],
        )
        self.assertEqual(
            skipped["audit_event_names"],
            [
                EVENT_SANDBOX_EXPERIMENT_REQUESTED,
                EVENT_SANDBOX_GATE_PASSED,
                EVENT_SANDBOX_POST_ACTION_VERIFICATION_PLANNED,
                EVENT_SANDBOX_REAL_ACTION_SKIPPED,
            ],
        )
        self.assertEqual(
            blocked["audit_event_names"],
            [
                EVENT_SANDBOX_EXPERIMENT_REQUESTED,
                EVENT_SANDBOX_GATE_BLOCKED,
            ],
        )

    def test_dry_run_success_path_reports_trace(self) -> None:
        scenario = evaluate_sandbox_experiment_scenario("sandbox_dry_run_success")

        self.assertEqual(scenario["actual"]["status"], "dry_run_completed")
        self.assertIs(scenario["gate_passed"], True)
        self.assertIs(scenario["dry_run"], True)
        self.assertIs(scenario["real_action_enabled"], False)
        self.assertIs(scenario["real_action_skipped"], False)
        self.assertIs(scenario["post_action_verification_planned"], True)
        self.assertTrue(scenario["trace"]["validation_checks"])

    def test_real_action_skipped_path_reports_trace(self) -> None:
        scenario = evaluate_sandbox_experiment_scenario("real_action_disabled_skip")

        self.assertEqual(scenario["actual"]["status"], "real_action_skipped")
        self.assertIs(scenario["gate_passed"], True)
        self.assertIs(scenario["dry_run"], False)
        self.assertIs(scenario["real_action_enabled"], False)
        self.assertIs(scenario["real_action_skipped"], True)
        self.assertIn(FAILURE_REAL_ACTION_DISABLED, scenario["failure_reasons"])
        self.assertIs(scenario["post_action_verification_planned"], True)

    def test_report_is_repeatable(self) -> None:
        first = evaluate_sandbox_experiment_scenarios()
        second = evaluate_sandbox_experiment_scenarios()

        self.assertEqual(first, second)

    def test_no_desktop_control_api_is_imported_or_called(self) -> None:
        source = inspect.getsource(sandbox_evaluation) + inspect.getsource(sandbox_experiment)

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


if __name__ == "__main__":
    unittest.main()
