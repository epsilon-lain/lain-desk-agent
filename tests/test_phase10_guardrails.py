from __future__ import annotations

import json
import unittest
from pathlib import Path

import _path  # noqa: F401
from lain_desk_agent.phase10_global_status import build_phase10_global_status_report
from lain_desk_agent.phase10_guardrails import (
    PHASE10_GUARDRAIL_AUDIT_ORDER,
    PHASE10_GUARDRAIL_BUNDLE_VERSION,
    PHASE10_GUARDRAIL_REPORT_VERSION,
    build_phase10_guardrail_validation_report,
    build_phase10_release_candidate_bundle,
    validate_phase10_release_candidate_bundle,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PHASE10_GUARDRAILS_MODULE = PROJECT_ROOT / "src" / "lain_desk_agent" / "phase10_guardrails.py"
PHASE10_EXPERIMENT_MODULE = PROJECT_ROOT / "src" / "lain_desk_agent" / "phase10_experiment.py"
UI_INDEX_HTML = PROJECT_ROOT / "ui" / "index.html"
UI_APP_JS = PROJECT_ROOT / "ui" / "app.js"
UI_STYLES_CSS = PROJECT_ROOT / "ui" / "styles.css"


class Phase10GuardrailBackendTests(unittest.TestCase):
    def test_release_candidate_bundle_validates_as_read_only_no_go(self) -> None:
        bundle = build_phase10_release_candidate_bundle()
        validation = validate_phase10_release_candidate_bundle(bundle)
        report = build_phase10_guardrail_validation_report(bundle)

        self.assertEqual(bundle["bundle_version"], PHASE10_GUARDRAIL_BUNDLE_VERSION)
        self.assertEqual(bundle["report_version"], PHASE10_GUARDRAIL_REPORT_VERSION)
        self.assertFalse(bundle["phase10_report"]["go_for_phase10"])
        self.assertTrue(validation["valid"])
        self.assertEqual(validation["status"], "valid")
        self.assertTrue(validation["validation_summary"]["validation_passed"])
        self.assertTrue(validation["validation_summary"]["replay_allowed_as_read_only"])
        self.assertEqual(validation["error_codes"], [])
        self.assertEqual(validation["unsafe_flags_detected"], [])
        self.assertGreater(len(validation["consistency_checks"]), 0)
        self.assertGreater(len(validation["audit_order_checks"]), 0)
        self.assertIn("validation_bundle", validation)
        self.assertEqual(report["validation_summary"], validation["validation_summary"])
        self.assertFalse(report["execution_attempted"])
        self.assertFalse(report["state_mutation"])

    def test_validation_bundle_is_reproducible_and_redacts_sensitive_keys(self) -> None:
        bundle = build_phase10_release_candidate_bundle()
        bundle["phase10_report"]["nested"] = {"access_key": "do-not-keep"}
        first = validate_phase10_release_candidate_bundle(bundle)
        second = validate_phase10_release_candidate_bundle(json.loads(json.dumps(bundle)))

        self.assertFalse(first["valid"])
        self.assertIn("suspicious_sensitive_key", first["error_codes"])
        self.assertEqual(
            first["validation_bundle"]["source_bundle_digest"],
            second["validation_bundle"]["source_bundle_digest"],
        )
        encoded = json.dumps(first["validation_bundle"])
        self.assertNotIn("do-not-keep", encoded)
        self.assertIn("[redacted-sensitive-key]", encoded)

    def test_validation_blocks_guardrail_regressions(self) -> None:
        base_bundle = build_phase10_release_candidate_bundle()
        cases = [
            (
                "real_actions_enabled",
                lambda bundle: bundle["phase10_report"].update({"real_actions_enabled": True}),
                {"real_action_enabled_in_bundle", "unsafe_bundle_flags"},
            ),
            (
                "go_for_phase10",
                lambda bundle: bundle["phase10_report"].update({"go_for_phase10": True}),
                {"go_for_phase10_in_bundle"},
            ),
            (
                "readiness_ready",
                lambda bundle: bundle["phase10_report"]["readiness"].update({"ready": True}),
                {"readiness_go_in_bundle"},
            ),
            (
                "approval_granted",
                lambda bundle: bundle["phase10_report"]["approval"].update({"approval_status": "approved"}),
                {"approval_implies_real_action"},
            ),
            (
                "audit_order",
                lambda bundle: bundle["phase10_report"].update(
                    {"audit_event_names": list(reversed(PHASE10_GUARDRAIL_AUDIT_ORDER))}
                ),
                {"inconsistent_audit_order"},
            ),
            (
                "scope_allows_action",
                lambda bundle: bundle["phase10_report"]["scope"].update(
                    {"allowed_action_types": ["click"]}
                ),
                {"unsafe_action_type"},
            ),
            (
                "execute_path",
                lambda bundle: bundle.update({"debug_endpoint": "/execute"}),
                {"execute_path_in_bundle"},
            ),
            (
                "permission_policy_changed",
                lambda bundle: bundle["phase10_report"]["consistency"].update(
                    {"permission_policy_changed": True}
                ),
                {"permission_policy_changed"},
            ),
        ]

        for case_name, mutate, expected_codes in cases:
            with self.subTest(case_name=case_name):
                bundle = json.loads(json.dumps(base_bundle))
                mutate(bundle)
                validation = validate_phase10_release_candidate_bundle(bundle)
                self.assertFalse(validation["valid"])
                self.assertTrue(expected_codes.issubset(set(validation["error_codes"])))
                self.assertFalse(validation["validation_summary"]["replay_allowed_as_read_only"])

    def test_global_status_includes_guardrail_validation_state(self) -> None:
        report = build_phase10_global_status_report()
        state = report["phase10_guardrail_validation_state"]

        self.assertEqual(state["source"], "deterministic_phase10_guardrail_fixture")
        self.assertEqual(state["validation_status"], "valid")
        self.assertTrue(state["validation_passed"])
        self.assertTrue(state["replay_allowed_as_read_only"])
        self.assertEqual(state["validation_error_count"], 0)
        self.assertFalse(state["real_actions_enabled"])
        self.assertFalse(state["phase10_real_actions_implemented"])
        self.assertFalse(state["go_for_phase10"])


class Phase10GuardrailCockpitTests(unittest.TestCase):
    def test_phase10_guardrail_cockpit_hooks_exist(self) -> None:
        html = UI_INDEX_HTML.read_text(encoding="utf-8")
        source = UI_APP_JS.read_text(encoding="utf-8")
        styles = UI_STYLES_CSS.read_text(encoding="utf-8")
        combined = html + source

        for hook in [
            "phase10GuardrailsPanel",
            "phase10GuardrailBundleInput",
            "loadPhase10GuardrailDemo",
            "validatePhase10GuardrailBundle",
            "phase10GuardrailValidationCounts",
            "phase10GuardrailValidationFilters",
            "phase10GuardrailValidationGroups",
            "copyPhase10GuardrailValidationSummary",
            "copyPhase10GuardrailValidationErrors",
            "copyPhase10GuardrailDebugFocus",
            "copyPhase10GuardrailValidationJson",
            "expandPhase10GuardrailGroups",
            "collapsePhase10GuardrailGroups",
            "data-phase10-replay-validation-health-strip",
            "phase10ReplayValidationFilter",
            "phase10ReplayValidationSection",
            "phase10ReplayValidationIssue",
        ]:
            with self.subTest(hook=hook):
                self.assertIn(hook, combined)

        for function_name in [
            "buildPhase10GuardrailDemoBundle",
            "validatePhase10GuardrailBundleObject",
            "renderPhase10GuardrailValidationCounts",
            "renderPhase10GuardrailValidationFilters",
            "renderPhase10GuardrailValidationGroups",
            "phase10GuardrailValidationSections",
            "setPhase10GuardrailGroupsOpen",
            "copyPhase10GuardrailValidationSummaryPayload",
            "copyPhase10GuardrailValidationErrorsPayload",
            "copyPhase10GuardrailDebugFocusPayload",
            "copyPhase10GuardrailValidationJsonPayload",
        ]:
            with self.subTest(function_name=function_name):
                self.assertIn(f"function {function_name}", source)

        for css_selector in [
            ".phase10-guardrails-panel",
            ".phase10-guardrail-health-strip",
            ".phase10-guardrail-filter-chip",
            ".phase10-guardrail-validation-groups",
            ".phase10-guardrail-validation-section",
            ".phase10-guardrail-validation-list",
            ".phase10-guardrail-validation-details",
        ]:
            with self.subTest(css_selector=css_selector):
                self.assertIn(css_selector, styles)

    def test_phase10_guardrail_ui_section_is_browser_local_and_read_only(self) -> None:
        source = UI_APP_JS.read_text(encoding="utf-8")
        start = source.index("function renderPhase10Guardrails")
        end = source.index("function setPhase9ExperimentSummary", start)
        section = source[start:end]

        self.assertIn("button.addEventListener", section)
        self.assertIn("renderPhase10GuardrailValidationGroups(validation)", section)
        for forbidden_fragment in [
            "fetch(",
            '"/execute"',
            "'/execute'",
            '"/approval"',
            "'/approval'",
            "recordApprovalDecision",
            "runWaitExecutionSelfTest",
            "realActionEnabled = true",
            "real_action_enabled = true",
            "execute_action_contract",
            "pyautogui",
            "pynput",
            "win32api",
            "SendInput",
            "mouse_event",
            "xdotool",
            "AppleScript",
        ]:
            with self.subTest(forbidden_fragment=forbidden_fragment):
                self.assertNotIn(forbidden_fragment, section)

    def test_phase10_guardrail_source_does_not_add_runtime_execution(self) -> None:
        source = (
            PHASE10_GUARDRAILS_MODULE.read_text(encoding="utf-8")
            + PHASE10_EXPERIMENT_MODULE.read_text(encoding="utf-8")
        )

        for forbidden_fragment in [
            "execute_action_contract",
            "def _handle_execute",
            "fetch(",
            "import pyautogui",
            "from pyautogui",
            "import pynput",
            "from pynput",
            "import keyboard",
            "import mouse",
            "import win32api",
            "SendInput(",
            "mouse_event(",
            "xdotool",
            "AppleScript UI scripting",
        ]:
            with self.subTest(forbidden_fragment=forbidden_fragment):
                self.assertNotIn(forbidden_fragment, source)


if __name__ == "__main__":
    unittest.main()
