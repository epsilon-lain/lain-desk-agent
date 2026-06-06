from __future__ import annotations

import inspect
import json
import threading
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.request import urlopen

import _path  # noqa: F401
from lain_desk_agent import phase9_experiment
from lain_desk_agent.main import create_server
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
    PHASE9_EXPORT_BUNDLE_VERSION,
    PHASE9_EXPORT_PROJECT_PHASE,
    PHASE9_EXPORT_REPORT_VERSION,
    PHASE9_REPORT_FIELDS,
    MockApprovalState,
    MockEmergencyStopState,
    MockPostActionVerificationPlan,
    MockRollbackPlan,
    Phase9ExperimentConfig,
    Phase9ExperimentRequest,
    build_phase9_ai_readable_summary,
    build_phase9_experiment_report,
    build_phase9_export_report,
    build_phase9_reproducibility_bundle,
    evaluate_phase9_experiment_scenarios,
    phase9_experiment_scenario_ids,
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
PROJECT_ROOT = Path(__file__).resolve().parents[1]
UI_INDEX_HTML = PROJECT_ROOT / "ui" / "index.html"
UI_APP_JS = PROJECT_ROOT / "ui" / "app.js"

PHASE9_COCKPIT_FIELDS = {
    "experiment_id",
    "experiment_name",
    "scenario_name",
    "dry_run",
    "real_action_enabled",
    "real_action_skipped",
    "gate_passed",
    "actual_outcome",
    "failure_reason_codes",
    "blocker_codes",
    "mock_approval_checked",
    "user_approval_present",
    "emergency_stop_available",
    "post_action_verification_planned",
    "rollback_plan_recorded",
    "sandbox_scope",
    "action_type",
    "target_risk_hint",
    "target_confidence",
    "readiness_ready",
    "audit_event_names",
    "notes",
}

PHASE9_EXPORT_REQUIRED_FIELDS = {
    "report_version",
    "generated_at",
    "project_phase",
    "dry_run",
    "real_action_enabled",
    "real_action_skipped",
    "experiment_id",
    "sandbox_scope",
    "action_type",
    "gate_passed",
    "actual_outcome",
    "failure_reason_codes",
    "blocker_codes",
    "target_risk_hint",
    "target_confidence",
    "readiness_ready",
    "user_approval_present",
    "emergency_stop_available",
    "post_action_verification_planned",
    "rollback_plan_recorded",
    "audit_event_names",
    "audit_timeline",
    "notes",
}


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

    def test_phase9_demo_report_exposes_cockpit_shape(self) -> None:
        report = evaluate_phase9_experiment_scenarios()

        self.assertEqual(report["report_type"], "phase9_minimal_sandbox_experiment")
        self.assertEqual(report["phase"], "phase9_1")
        self.assertEqual(report["cockpit_exposure_phase"], "phase9_2")
        self.assertIs(report["external_llm_calls"], False)
        self.assertIs(report["real_desktop_actions"], False)
        self.assertEqual(report["scenario_ids"], list(PHASE9_MINIMAL_SCENARIO_IDS))
        self.assertEqual(phase9_experiment_scenario_ids(), list(PHASE9_MINIMAL_SCENARIO_IDS))
        self.assertEqual(report["summary"]["real_action_enabled_count"], 0)
        self.assertEqual(report["summary"]["real_action_attempted_count"], 0)
        self.assertEqual(report["summary"]["real_action_skipped_count"], 1)

        for scenario in report["scenarios"]:
            with self.subTest(scenario=scenario["scenario_id"]):
                self.assertTrue(PHASE9_COCKPIT_FIELDS.issubset(scenario))
                self.assertTrue(set(PHASE9_REPORT_FIELDS).issubset(scenario))
                self.assertIs(scenario["mock_approval_checked"], True)
                self.assertIn("window_id", scenario["sandbox_scope"])
                self.assertIn("target_id", scenario["sandbox_scope"])
                self.assertIn("phase9_experiment_requested", scenario["audit_event_names"])
                self.assertIs(scenario["actual_outcome"]["real_action_attempted"], False)

        self.assertIn("phase9_export_bundle", report)
        self.assertEqual(report["export_phase"], PHASE9_EXPORT_PROJECT_PHASE)

    def test_phase9_export_report_contains_required_fields(self) -> None:
        report = evaluate_phase9_experiment_scenarios()
        export_report = build_phase9_export_report(report)

        self.assertTrue(PHASE9_EXPORT_REQUIRED_FIELDS.issubset(export_report))
        self.assertEqual(export_report["report_version"], PHASE9_EXPORT_REPORT_VERSION)
        self.assertEqual(export_report["project_phase"], PHASE9_EXPORT_PROJECT_PHASE)
        self.assertEqual(export_report["generated_at"], "deterministic_phase9_fixture")
        self.assertIs(export_report["real_action_enabled"], False)
        self.assertIs(export_report["real_action_skipped"], True)
        self.assertIs(export_report["actual_outcome"]["real_action_attempted"], False)
        self.assertIn("missing_user_approval", export_report["failure_reason_codes"])
        self.assertIn("stale_observation", export_report["blocker_codes"])
        self.assertIn("phase9_experiment_requested", export_report["audit_event_names"])
        self.assertEqual(
            len(export_report["audit_timeline"]),
            sum(len(scenario["audit_event_names"]) for scenario in report["scenarios"]),
        )

        for scenario in export_report["scenarios"]:
            with self.subTest(scenario=scenario["scenario_id"]):
                self.assertTrue(PHASE9_EXPORT_REQUIRED_FIELDS.issubset(scenario))
                self.assertIn("audit_timeline", scenario)

    def test_phase9_ai_readable_summary_contains_handoff_context(self) -> None:
        export_report = build_phase9_export_report(evaluate_phase9_experiment_scenarios())
        summary = build_phase9_ai_readable_summary(export_report)

        for expected_text in [
            "phase_9_4",
            "dry_run",
            "real_action_enabled=no",
            "Gate result",
            "failure_reason_codes",
            "blocker_codes",
            "approval_present",
            "emergency_stop_available",
            "verification_planned",
            "rollback_recorded",
            "real_action_skipped=yes",
            "Recommended next debugging focus",
            "Safety boundary",
            "Real desktop actions remain disabled",
        ]:
            with self.subTest(expected_text=expected_text):
                self.assertIn(expected_text, summary)

    def test_phase9_reproducibility_bundle_is_stable_and_sanitized(self) -> None:
        report = evaluate_phase9_experiment_scenarios()
        bundle = build_phase9_reproducibility_bundle(report)

        self.assertEqual(bundle["bundle_type"], "phase9_reproducibility_bundle")
        self.assertEqual(bundle["bundle_version"], PHASE9_EXPORT_BUNDLE_VERSION)
        self.assertEqual(bundle["project_phase"], PHASE9_EXPORT_PROJECT_PHASE)
        self.assertIn("phase9_report", bundle)
        self.assertIn("ai_readable_summary", bundle)
        self.assertIn("minimal_reproduction_metadata", bundle)
        self.assertIn("audit_event_order", bundle["minimal_reproduction_metadata"])
        self.assertIn("failure_reason_codes", bundle["minimal_reproduction_metadata"])
        self.assertIn("blocker_codes", bundle["minimal_reproduction_metadata"])
        self.assertIn("safety_boundary_statement", bundle)

        bundle_text = json.dumps(bundle, sort_keys=True).lower()
        for forbidden_text in ["token", "secret", "api_key", "password", "credential"]:
            with self.subTest(forbidden_text=forbidden_text):
                self.assertNotIn(forbidden_text, bundle_text)

        self.assertNotIn("browser_credentials_allowed", bundle_text)
        self.assertIn("real desktop actions remain disabled", bundle_text)

    def test_phase9_cockpit_endpoint_is_read_only_and_stable(self) -> None:
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
                with urlopen(f"http://{host}:{port}/phase9-experiment/demo", timeout=5) as response:
                    payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            thread.join(timeout=2)
            server.server_close()

        self.assertEqual(payload["report_type"], "phase9_minimal_sandbox_experiment")
        self.assertEqual(payload["cockpit_exposure_phase"], "phase9_2")
        self.assertEqual(payload["scenario_ids"], list(PHASE9_MINIMAL_SCENARIO_IDS))
        self.assertEqual(payload["summary"]["real_action_attempted_count"], 0)
        self.assertTrue(PHASE9_COCKPIT_FIELDS.issubset(payload["scenarios"][0]))
        self.assertIn("phase9_export_bundle", payload)
        self.assertIn("phase9_report", payload["phase9_export_bundle"])
        self.assertIn("ai_readable_summary", payload["phase9_export_bundle"])

    def test_phase9_cockpit_endpoint_can_filter_one_scenario(self) -> None:
        server = create_server("127.0.0.1", 0)
        host, port = server.server_address
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            with urlopen(
                f"http://{host}:{port}/phase9-experiment/demo?scenario_id=missing_user_approval_blocks",
                timeout=5,
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            thread.join(timeout=2)
            server.server_close()

        self.assertEqual(payload["scenario_count"], 1)
        self.assertEqual(payload["scenario_ids"], ["missing_user_approval_blocks"])
        self.assertEqual(payload["scenarios"][0]["scenario_id"], "missing_user_approval_blocks")

    def test_phase9_cockpit_ui_selectors_and_strings_exist(self) -> None:
        html = UI_INDEX_HTML.read_text(encoding="utf-8")
        source = UI_APP_JS.read_text(encoding="utf-8")

        for element_id in [
            "phase9ExperimentPanel",
            "loadPhase9Experiment",
            "phase9ExperimentControls",
            "phase9OutcomeFilter",
            "phase9GateBlockerFilter",
            "phase9ApprovalFilter",
            "phase9RiskFilter",
            "phase9ReadinessFilter",
            "phase9ScenarioTypeFilter",
            "phase9GroupMode",
            "phase9AuditGroupMode",
            "phase9AuditSortMode",
            "expandPhase9Scenarios",
            "collapsePhase9Scenarios",
            "expandPhase9Audit",
            "collapsePhase9Audit",
            "resetPhase9Filters",
            "copyPhase9AISummary",
            "copyPhase9JsonReport",
            "copyPhase9ReproBundle",
            "phase9QuickFilters",
            "phase9ExportCopyStatus",
            "phase9Counts",
            "phase9ExperimentStatus",
            "phase9ExperimentSummary",
            "phase9ExperimentTimeline",
            "phase9ExperimentResults",
        ]:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', html)
                self.assertIn(f"#{element_id}", source)

        for visible_label in [
            "Phase 9 dry-run harness",
            "Approval state",
            "Emergency stop",
            "Verification",
            "Rollback",
            "Sandbox scope",
            "Real action",
            "Phase 9 audit event sequence",
            "Gate blocker",
            "Scenario type",
            "Group by",
            "Audit group",
            "Audit order",
            "original order",
            "blocker severity",
            "Copy AI summary",
            "Copy JSON report",
            "Copy repro bundle",
        ]:
            with self.subTest(visible_label=visible_label):
                self.assertIn(visible_label, source + html)

    def test_phase9_cockpit_filters_counts_and_grouping_hooks_exist(self) -> None:
        source = UI_APP_JS.read_text(encoding="utf-8")

        for function_name in [
            "currentPhase9ExperimentFilters",
            "populatePhase9ExperimentFilters",
            "phase9ExperimentFilteredScenarios",
            "phase9ScenarioMatchesFilters",
            "renderPhase9QuickFilters",
            "renderPhase9ExperimentCounts",
            "phase9ExperimentScenarioGroups",
            "phase9ExperimentScenarioGroupSection",
            "phase9OutcomeKind",
            "phase9RiskLevel",
            "phase9ReadinessStatus",
            "phase9GateBlockerCodes",
            "phase9BlockerSeverity",
            "phase9ScenarioBlockerSeverity",
            "copyPhase9ExportPayload",
            "buildPhase9ExportPayload",
            "phase9ReproducibilityBundle",
            "buildPhase9ClientExportReport",
            "buildPhase9AIReadableSummary",
            "phase9RecommendedFocus",
        ]:
            with self.subTest(function_name=function_name):
                self.assertIn(f"function {function_name}", source)

        for dataset_field in [
            "phase9HarnessCard",
            "scenarioType",
            "outcome",
            "gateBlockers",
            "riskLevel",
            "readinessStatus",
            "phase9CountKey",
            "phase9QuickFilter",
            "phase9ScenarioGroup",
        ]:
            with self.subTest(dataset_field=dataset_field):
                self.assertIn(f"dataset.{dataset_field}", source)

        for group_name in ["blockers", "approval", "risk", "readiness", "skipped"]:
            with self.subTest(group_name=group_name):
                self.assertIn(f"{group_name}:", source)

    def test_phase9_cockpit_audit_drilldown_hooks_exist(self) -> None:
        source = UI_APP_JS.read_text(encoding="utf-8")
        styles = (PROJECT_ROOT / "ui" / "styles.css").read_text(encoding="utf-8")

        for function_name in [
            "phase9AuditEventDrilldownList",
            "phase9AuditEventDrilldownDetails",
            "phase9AuditEventDetailRows",
            "setPhase9AuditDetailsOpen",
            "setPhase9ScenarioDetailsOpen",
        ]:
            with self.subTest(function_name=function_name):
                self.assertIn(f"function {function_name}", source)

        self.assertIn("data-phase9-audit-event-details", source)
        self.assertIn("dataset.auditOrder", source)
        self.assertIn("dataset.originalOrder", source)
        self.assertIn("dataset.scenarioAuditOrder", source)
        self.assertIn("dataset.gateStatus", source)
        self.assertIn("dataset.blockerSeverity", source)
        self.assertIn("dataset.phase9EventKind", source)
        self.assertIn("dataset.phase9AuditEventChip", source)
        self.assertIn("phase9-audit-event-details", source)
        self.assertIn(".phase9-audit-event-details", styles)
        self.assertIn(".phase9-audit-event-summary", styles)
        self.assertIn(".phase9-audit-event-detail-grid", styles)

    def test_phase9_cockpit_advanced_audit_timeline_hooks_exist(self) -> None:
        source = UI_APP_JS.read_text(encoding="utf-8")
        styles = (PROJECT_ROOT / "ui" / "styles.css").read_text(encoding="utf-8")

        for function_name in [
            "renderPhase9ExperimentTimeline",
            "phase9TimelineEventRecords",
            "phase9TimelineEventRecord",
            "phase9SortedTimelineEvents",
            "phase9TimelineEventGroups",
            "phase9TimelineEventGroupKey",
            "phase9TimelineEventGroupTitle",
            "phase9TimelineEventGroupSection",
            "phase9TimelineEventList",
            "phase9TimelineSortLabel",
            "phase9AuditEventKind",
        ]:
            with self.subTest(function_name=function_name):
                self.assertIn(f"function {function_name}", source)

        for required_string in [
            "phase9_experiment_requested",
            "phase9_mock_approval_checked",
            "phase9_emergency_stop_checked",
            "phase9_gate_passed",
            "phase9_gate_blocked",
            "phase9_dry_run_completed",
            "phase9_real_action_skipped",
            "phase9_rollback_plan_recorded",
            "phase9_post_action_verification_planned",
            "Approval state",
            "Emergency stop",
            "Verification",
            "Rollback",
        ]:
            with self.subTest(required_string=required_string):
                self.assertIn(required_string, source)

        for dataset_field in [
            "phase9AuditGroupMode",
            "phase9AuditSortMode",
            "phase9AuditGroup",
            "phase9TimelineEventList",
            "phase9TimelineEvent",
            "phase9EventKind",
            "originalOrder",
            "scenarioAuditOrder",
        ]:
            with self.subTest(dataset_field=dataset_field):
                self.assertIn(f"dataset.{dataset_field}", source)

        self.assertIn(".phase9-audit-timeline-group", styles)
        self.assertIn(".phase9-audit-timeline-group-title", styles)
        self.assertIn('data-phase9-event-kind="success"', styles)
        self.assertIn('data-phase9-event-kind="warning"', styles)
        self.assertIn('data-phase9-event-kind="blocked"', styles)
        self.assertIn('data-phase9-event-kind="skipped"', styles)

    def test_phase9_cockpit_ui_is_read_only(self) -> None:
        source = UI_APP_JS.read_text(encoding="utf-8")
        start = source.index("async function loadPhase9Experiment")
        end = source.index("function setSandboxEvaluationSummary", start)
        phase9_ui_source = source[start:end]

        self.assertIn('fetch("/phase9-experiment/demo")', phase9_ui_source)
        for forbidden_fragment in [
            'fetch("/execute"',
            "fetch('/execute'",
            'fetch("/approval"',
            "fetch('/approval'",
            "recordApprovalDecision",
            "runWaitExecutionSelfTest",
            "realActionEnabled = true",
            "real_action_enabled = true",
            ".click(",
            ".type(",
            "hotkey(",
            "switch_app",
        ]:
            with self.subTest(fragment=forbidden_fragment):
                self.assertNotIn(forbidden_fragment, phase9_ui_source)

        self.assertIn("phase9ExperimentScenarioCard", source)
        self.assertIn("renderPhase9ExperimentTimeline", source)
        self.assertIn("phase9_real_action_skipped", source)
        self.assertIn("navigator.clipboard.writeText", phase9_ui_source)
        self.assertIn("phase9_export_bundle", phase9_ui_source)

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
