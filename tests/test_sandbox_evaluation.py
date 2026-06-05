from __future__ import annotations

import inspect
import json
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.request import urlopen

import _path  # noqa: F401
from lain_desk_agent import sandbox_evaluation, sandbox_experiment
from lain_desk_agent.main import create_server
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
)


EXPECTED_SCENARIO_IDS = [
    "dry_run_success_all_gates_pass",
    "real_action_disabled_skips_non_dry_run",
    "missing_user_approval_blocks",
    "stale_observation_blocks",
    "high_risk_target_blocks",
    "unknown_risk_target_blocks",
    "low_confidence_target_blocks",
    "invalid_bbox_blocks",
    "bbox_center_mismatch_blocks",
    "missing_viewport_or_coordinate_space_blocks",
    "missing_post_action_verification_blocks",
    "forbidden_action_type_blocks",
    "outside_sandbox_scope_blocks",
    "readiness_not_ready_blocks",
    "missing_emergency_stop_blocks",
    "missing_audit_plan_blocks",
    "missing_action_contract_blocks",
    "missing_target_blocks",
]

REQUIRED_RESULT_FIELDS = {
    "scenario_id",
    "scenario_name",
    "expected_outcome",
    "actual_outcome",
    "passed",
    "gate_passed",
    "dry_run",
    "real_action_enabled",
    "real_action_skipped",
    "failure_reason_codes",
    "blocker_codes",
    "audit_event_names",
    "post_action_verification_planned",
    "target_risk_hint",
    "target_confidence",
    "readiness_ready",
    "action_type",
    "notes",
}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
UI_INDEX_HTML = PROJECT_ROOT / "ui" / "index.html"
UI_APP_JS = PROJECT_ROOT / "ui" / "app.js"
UI_STYLES_CSS = PROJECT_ROOT / "ui" / "styles.css"


class SandboxEvaluationTests(unittest.TestCase):
    def test_scenario_ids_are_deterministic(self) -> None:
        self.assertEqual(sandbox_evaluation_scenario_names(), EXPECTED_SCENARIO_IDS)

    def test_report_summary_fields_are_deterministic(self) -> None:
        report = evaluate_sandbox_experiment_scenarios()
        summary = report["summary"]

        self.assertEqual(report["report_type"], "sandbox_experiment_evaluation")
        self.assertEqual(report["phase"], "phase8_1")
        self.assertIs(report["external_llm_calls"], False)
        self.assertIs(report["real_desktop_actions"], False)
        self.assertEqual(report["scenario_count"], len(EXPECTED_SCENARIO_IDS))
        self.assertEqual(report["scenario_ids"], EXPECTED_SCENARIO_IDS)
        self.assertEqual(summary["total_scenario_count"], len(EXPECTED_SCENARIO_IDS))
        self.assertEqual(summary["passed_scenario_count"], len(EXPECTED_SCENARIO_IDS))
        self.assertEqual(summary["failed_scenario_count"], 0)
        self.assertEqual(summary["scenarios_with_failures"], [])
        self.assertIs(summary["all_expected_outcomes_passed"], True)
        self.assertEqual(summary["gate_passed_count"], 2)
        self.assertEqual(summary["gate_blocked_count"], len(EXPECTED_SCENARIO_IDS) - 2)
        self.assertEqual(summary["real_action_enabled_count"], 0)
        self.assertEqual(summary["real_action_skipped_count"], 1)
        self.assertEqual(summary["real_action_attempted_count"], 0)
        self.assertEqual(summary["post_action_verification_planned_count"], 2)

    def test_each_scenario_has_required_result_model_fields(self) -> None:
        report = evaluate_sandbox_experiment_scenarios()

        for scenario in report["scenarios"]:
            with self.subTest(scenario=scenario["scenario_id"]):
                self.assertTrue(REQUIRED_RESULT_FIELDS.issubset(scenario))
                self.assertIs(scenario["passed"], True)
                self.assertEqual(scenario["pass_fail"], "pass")
                self.assertEqual(scenario["scenario"], scenario["scenario_id"])
                self.assertEqual(scenario["expected"], scenario["expected_outcome"])
                self.assertEqual(scenario["actual"], scenario["actual_outcome"])
                self.assertIs(scenario["actual_outcome"]["real_action_attempted"], False)
                self.assertEqual(
                    scenario["trace"]["failure_reason_codes"],
                    scenario["failure_reason_codes"],
                )
                self.assertEqual(
                    scenario["trace"]["blocker_codes"],
                    scenario["blocker_codes"],
                )

    def test_every_scenario_matches_expected_outcome(self) -> None:
        report = evaluate_sandbox_experiment_scenarios()

        for scenario in report["scenarios"]:
            with self.subTest(scenario=scenario["scenario_id"]):
                expected = scenario["expected_outcome"]
                actual = scenario["actual_outcome"]
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
                    self.assertEqual(actual[field], expected[field])

    def test_failure_reason_codes_are_summarized(self) -> None:
        report = evaluate_sandbox_experiment_scenarios()
        codes = report["summary"]["failure_reason_codes"]

        expected = {
            FAILURE_REAL_ACTION_DISABLED: ["real_action_disabled_skips_non_dry_run"],
            FAILURE_MISSING_USER_APPROVAL: ["missing_user_approval_blocks"],
            FAILURE_STALE_OBSERVATION: ["stale_observation_blocks"],
            FAILURE_HIGH_RISK_TARGET: [
                "high_risk_target_blocks",
                "unknown_risk_target_blocks",
            ],
            FAILURE_LOW_CONFIDENCE_TARGET: ["low_confidence_target_blocks"],
            FAILURE_INVALID_TARGET_GEOMETRY: [
                "invalid_bbox_blocks",
                "bbox_center_mismatch_blocks",
                "missing_viewport_or_coordinate_space_blocks",
            ],
            FAILURE_MISSING_POST_ACTION_VERIFICATION: [
                "missing_post_action_verification_blocks"
            ],
            FAILURE_FORBIDDEN_ACTION_TYPE: ["forbidden_action_type_blocks"],
            FAILURE_OUTSIDE_SANDBOX_SCOPE: [
                "forbidden_action_type_blocks",
                "outside_sandbox_scope_blocks",
            ],
            FAILURE_READINESS_NOT_READY: ["readiness_not_ready_blocks"],
            FAILURE_MISSING_EMERGENCY_STOP: ["missing_emergency_stop_blocks"],
            FAILURE_MISSING_AUDIT_PLAN: ["missing_audit_plan_blocks"],
            FAILURE_MISSING_ACTION_CONTRACT: ["missing_action_contract_blocks"],
            FAILURE_MISSING_TARGET: ["missing_target_blocks"],
        }

        for code, scenario_ids in expected.items():
            with self.subTest(code=code):
                self.assertEqual(codes[code], scenario_ids)

    def test_blocker_codes_are_propagated(self) -> None:
        report = evaluate_sandbox_experiment_scenarios()
        blocker_codes = report["summary"]["blocker_codes"]

        expected = {
            "stale_observation": ["stale_observation_blocks"],
            "high_risk_requires_approval": ["high_risk_target_blocks"],
            "unknown_risk_target": ["unknown_risk_target_blocks"],
            "low_confidence_target": ["low_confidence_target_blocks"],
            "invalid_bbox": ["invalid_bbox_blocks"],
            "bbox_center_mismatch": ["bbox_center_mismatch_blocks"],
            "coordinate_space_unknown": ["missing_viewport_or_coordinate_space_blocks"],
            "dpi_uncertain": ["missing_viewport_or_coordinate_space_blocks"],
            "preview_only_contract": ["readiness_not_ready_blocks"],
            "missing_target": ["missing_target_blocks"],
        }

        for code, scenario_ids in expected.items():
            with self.subTest(code=code):
                self.assertEqual(blocker_codes[code], scenario_ids)

    def test_audit_event_ordering_is_stable(self) -> None:
        success = evaluate_sandbox_experiment_scenario("dry_run_success_all_gates_pass")
        skipped = evaluate_sandbox_experiment_scenario("real_action_disabled_skips_non_dry_run")
        blocked = evaluate_sandbox_experiment_scenario("missing_user_approval_blocks")

        self.assertEqual(
            success["audit_event_names"],
            [
                EVENT_SANDBOX_EXPERIMENT_REQUESTED,
                EVENT_SANDBOX_GATE_PASSED,
                EVENT_SANDBOX_POST_ACTION_VERIFICATION_PLANNED,
                EVENT_SANDBOX_DRY_RUN_COMPLETED,
            ],
        )
        self.assertLess(
            success["audit_event_names"].index(EVENT_SANDBOX_GATE_PASSED),
            success["audit_event_names"].index(EVENT_SANDBOX_DRY_RUN_COMPLETED),
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
        self.assertNotIn(EVENT_SANDBOX_DRY_RUN_COMPLETED, blocked["audit_event_names"])

    def test_dry_run_success_path_reports_trace(self) -> None:
        scenario = evaluate_sandbox_experiment_scenario("dry_run_success_all_gates_pass")

        self.assertEqual(scenario["actual_outcome"]["status"], "dry_run_completed")
        self.assertIs(scenario["gate_passed"], True)
        self.assertIs(scenario["dry_run"], True)
        self.assertIs(scenario["real_action_enabled"], False)
        self.assertIs(scenario["real_action_skipped"], False)
        self.assertIs(scenario["post_action_verification_planned"], True)
        self.assertEqual(scenario["target_risk_hint"], "normal")
        self.assertEqual(scenario["target_confidence"], 0.96)
        self.assertIs(scenario["readiness_ready"], True)
        self.assertEqual(scenario["action_type"], "click")
        self.assertTrue(scenario["trace"]["validation_checks"])

    def test_real_action_skipped_path_reports_trace(self) -> None:
        scenario = evaluate_sandbox_experiment_scenario("real_action_disabled_skips_non_dry_run")

        self.assertEqual(scenario["actual_outcome"]["status"], "real_action_skipped")
        self.assertIs(scenario["gate_passed"], True)
        self.assertIs(scenario["dry_run"], False)
        self.assertIs(scenario["real_action_enabled"], False)
        self.assertIs(scenario["real_action_skipped"], True)
        self.assertEqual(scenario["failure_reason_codes"], [FAILURE_REAL_ACTION_DISABLED])
        self.assertIs(scenario["post_action_verification_planned"], True)

    def test_all_conservative_blocking_paths_block(self) -> None:
        blocking_scenarios = [
            scenario_id
            for scenario_id in EXPECTED_SCENARIO_IDS
            if scenario_id not in {
                "dry_run_success_all_gates_pass",
                "real_action_disabled_skips_non_dry_run",
            }
        ]

        for scenario_id in blocking_scenarios:
            with self.subTest(scenario=scenario_id):
                scenario = evaluate_sandbox_experiment_scenario(scenario_id)

                self.assertEqual(scenario["actual_outcome"]["status"], "blocked")
                self.assertIs(scenario["gate_passed"], False)
                self.assertEqual(
                    scenario["audit_event_names"],
                    [EVENT_SANDBOX_EXPERIMENT_REQUESTED, EVENT_SANDBOX_GATE_BLOCKED],
                )

    def test_report_is_repeatable(self) -> None:
        first = evaluate_sandbox_experiment_scenarios()
        second = evaluate_sandbox_experiment_scenarios()

        self.assertEqual(first, second)

    def test_no_desktop_control_api_is_imported_or_called(self) -> None:
        source = inspect.getsource(sandbox_evaluation) + inspect.getsource(sandbox_experiment)

        forbidden_fragments = [
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

    def test_cockpit_endpoint_exposes_stable_read_only_report(self) -> None:
        server = create_server("127.0.0.1", 0)
        host, port = server.server_address
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            with (
                patch("lain_desk_agent.main.observe", side_effect=AssertionError("observe called")),
                patch("lain_desk_agent.main.understand", side_effect=AssertionError("understand called")),
                patch(
                    "lain_desk_agent.main.execute_action_contract",
                    side_effect=AssertionError("execution called"),
                ),
            ):
                with urlopen(
                    f"http://{host}:{port}/sandbox-evaluation/demo",
                    timeout=5,
                ) as response:
                    payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            thread.join(timeout=2)
            server.server_close()

        self.assertEqual(payload["report_type"], "sandbox_experiment_evaluation")
        self.assertEqual(payload["phase"], "phase8_1")
        self.assertIs(payload["real_desktop_actions"], False)
        self.assertEqual(payload["scenario_ids"], EXPECTED_SCENARIO_IDS)
        self.assertEqual(payload["scenario_count"], len(EXPECTED_SCENARIO_IDS))
        self.assertEqual(payload["summary"]["real_action_attempted_count"], 0)
        self.assertEqual(payload["summary"]["real_action_enabled_count"], 0)

        scenario = payload["scenarios"][0]
        self.assertTrue(REQUIRED_RESULT_FIELDS.issubset(scenario))
        self.assertIn("expected_outcome", scenario)
        self.assertIn("actual_outcome", scenario)
        self.assertIn("trace", scenario)

    def test_cockpit_endpoint_can_filter_one_scenario_by_id(self) -> None:
        server = create_server("127.0.0.1", 0)
        host, port = server.server_address
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            with urlopen(
                f"http://{host}:{port}/sandbox-evaluation/demo?scenario_id=dry_run_success_all_gates_pass",
                timeout=5,
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            thread.join(timeout=2)
            server.server_close()

        self.assertEqual(payload["scenario_count"], 1)
        self.assertEqual(payload["scenario_ids"], ["dry_run_success_all_gates_pass"])
        self.assertEqual(payload["scenarios"][0]["scenario_id"], "dry_run_success_all_gates_pass")

    def test_cockpit_ui_sandbox_trace_does_not_trigger_execution(self) -> None:
        source = UI_APP_JS.read_text(encoding="utf-8")
        start = source.index("async function loadSandboxEvaluation")
        end = source.index("function setPlannerEvaluationSummary", start)
        sandbox_ui_source = source[start:end]

        self.assertIn('fetch("/sandbox-evaluation/demo")', sandbox_ui_source)
        for forbidden_fragment in [
            'fetch("/execute"',
            "fetch('/execute'",
            'fetch("/approval"',
            "fetch('/approval'",
            "recordApprovalDecision",
            "runWaitExecutionSelfTest",
        ]:
            with self.subTest(fragment=forbidden_fragment):
                self.assertNotIn(forbidden_fragment, sandbox_ui_source)

    def test_cockpit_ui_sandbox_trace_has_phase83_controls(self) -> None:
        html = UI_INDEX_HTML.read_text(encoding="utf-8")
        source = UI_APP_JS.read_text(encoding="utf-8")
        styles = UI_STYLES_CSS.read_text(encoding="utf-8")

        for element_id in [
            "sandboxEvaluationFixtureSet",
            "sandboxEvaluationResultFilter",
            "sandboxEvaluationTypeFilter",
            "sandboxEvaluationBlockerFilter",
            "expandSandboxScenarios",
            "collapseSandboxScenarios",
            "sandboxEvaluationCounts",
            "sandboxEvaluationTimeline",
        ]:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', html)
                self.assertIn(f"#{element_id}", source)

        for function_name in [
            "sandboxEvaluationFilteredScenarios",
            "sandboxScenarioMatchesFilters",
            "sandboxScenarioMatchesFixtureSet",
            "renderSandboxEvaluationTimeline",
            "setSandboxScenarioDetailsOpen",
        ]:
            with self.subTest(function_name=function_name):
                self.assertIn(f"function {function_name}", source)

        self.assertIn(".sandbox-evaluation-controls", styles)
        self.assertIn(".sandbox-evaluation-scenario-details", styles)

    def test_cockpit_ui_sandbox_trace_exposes_required_dom_fields(self) -> None:
        source = UI_APP_JS.read_text(encoding="utf-8")

        required_dataset_fields = [
            "scenarioId",
            "scenarioName",
            "passFail",
            "expectedOutcome",
            "actualOutcome",
            "failureReasonCodes",
            "blockerCodes",
            "auditEventNames",
            "dryRun",
            "realActionSkipped",
            "postActionVerificationPlanned",
            "targetRiskHint",
            "targetConfidence",
            "readinessReady",
            "actionType",
            "scenarioType",
        ]
        for field in required_dataset_fields:
            with self.subTest(field=field):
                self.assertIn(f"card.dataset.{field}", source)

        for visible_label in [
            "Failure reasons",
            "Blockers",
            "Audit events",
            "Dry-run",
            "Real action",
            "Post verify",
            "Target",
            "Readiness",
        ]:
            with self.subTest(label=visible_label):
                self.assertIn(f'"{visible_label}"', source)

    def test_cockpit_ui_sandbox_filters_and_detail_controls_are_read_only(self) -> None:
        source = UI_APP_JS.read_text(encoding="utf-8")
        start = source.index("async function loadSandboxEvaluation")
        end = source.index("function setPlannerEvaluationSummary", start)
        sandbox_ui_source = source[start:end]

        for control in [
            "sandboxEvaluationFixtureSet",
            "sandboxEvaluationResultFilter",
            "sandboxEvaluationTypeFilter",
            "sandboxEvaluationBlockerFilter",
        ]:
            with self.subTest(control=control):
                self.assertIn(f'{control}.addEventListener("change"', source)

        self.assertIn('expandSandboxScenarios.addEventListener("click"', source)
        self.assertIn('collapseSandboxScenarios.addEventListener("click"', source)
        self.assertIn('details[data-sandbox-scenario-details', sandbox_ui_source)

        for forbidden_fragment in [
            "real_action_enabled = true",
            "realActionEnabled = true",
            "click(",
            "type(",
            "hotkey",
            "switch_app",
        ]:
            with self.subTest(fragment=forbidden_fragment):
                if forbidden_fragment in {"click(", "type("}:
                    self.assertNotIn(f"desktop.{forbidden_fragment}", sandbox_ui_source)
                else:
                    self.assertNotIn(forbidden_fragment, sandbox_ui_source)


if __name__ == "__main__":
    unittest.main()
