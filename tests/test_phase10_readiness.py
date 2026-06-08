from __future__ import annotations

import json
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.request import urlopen

import _path  # noqa: F401
from lain_desk_agent.main import create_server
from lain_desk_agent.phase10_readiness import (
    PHASE10_NO_GO_REASONS,
    build_phase10_ai_handoff_summary,
    build_phase10_blocker_summary,
    build_phase10_go_no_go_report,
    build_phase10_readiness_report,
    build_phase10_safety_invariant_report,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PHASE10_DOC = PROJECT_ROOT / "docs" / "PHASE_10_READINESS_CHECKLIST.md"
README_DOC = PROJECT_ROOT / "README.md"
ROADMAP_DOC = PROJECT_ROOT / "docs" / "ROADMAP.md"
ARCHITECTURE_DOC = PROJECT_ROOT / "docs" / "ARCHITECTURE.md"
STATUS_JSON = PROJECT_ROOT / "docs" / "project_status_snapshot.json"
UI_INDEX_HTML = PROJECT_ROOT / "ui" / "index.html"
UI_APP_JS = PROJECT_ROOT / "ui" / "app.js"
UI_STYLES_CSS = PROJECT_ROOT / "ui" / "styles.css"


class Phase10ReadinessDocTests(unittest.TestCase):
    def test_phase10_readiness_report_defaults_to_no_go(self) -> None:
        report = build_phase10_readiness_report()

        self.assertEqual(report["report_version"], "phase10_readiness_v1")
        self.assertIn("Phase 10.1", report["project_phase"])
        self.assertIs(report["dry_run"], True)
        self.assertIs(report["read_only"], True)
        self.assertIs(report["debug_only"], True)
        self.assertIs(report["real_actions_enabled"], False)
        self.assertIs(report["phase10_real_actions_implemented"], False)
        self.assertIs(report["go_for_phase10"], False)
        self.assertIs(report["external_llm_calls"], False)
        self.assertIs(report["real_desktop_actions"], False)
        self.assertEqual(build_phase10_readiness_report(), report)

        for reason in [
            "phase10_real_actions_not_implemented",
            "real_actions_disabled",
            "manual_phase10_approval_not_recorded",
            "real_action_adapter_absent",
            "live_sandbox_scope_not_selected",
            "live_post_action_verification_not_implemented",
        ]:
            with self.subTest(reason=reason):
                self.assertIn(reason, report["no_go_reasons"])

    def test_phase10_readiness_report_has_required_shape(self) -> None:
        report = build_phase10_readiness_report()

        for field in [
            "safety_boundary",
            "completed_phase_summary",
            "required_gates",
            "readiness_checks",
            "safety_invariants",
            "known_blockers",
            "required_manual_checks",
            "required_test_commands",
            "ai_handoff_summary",
            "recommended_next_work",
            "forbidden_actions",
            "forbidden_apis",
            "important_files",
            "audit_notes",
            "go_no_go",
        ]:
            with self.subTest(field=field):
                self.assertIn(field, report)

        for command in [
            ".\\scripts\\verify.ps1",
            "python scripts\\safety_scan.py",
            "node --check ui/app.js",
            "git diff --check",
        ]:
            with self.subTest(command=command):
                self.assertIn(command, report["required_test_commands"])

        for api_name in [
            "pyautogui",
            "pynput",
            "keyboard",
            "mouse",
            "win32api",
            "ctypes SendInput",
            "ctypes mouse_event",
            "xdotool",
            "AppleScript UI scripting",
        ]:
            with self.subTest(api_name=api_name):
                self.assertIn(api_name, report["forbidden_apis"])

    def test_phase10_readiness_report_contains_no_secret_values(self) -> None:
        encoded = json.dumps(build_phase10_readiness_report()).lower()

        for forbidden in ["sk-", "password=", "token=", "api_key=", "secret="]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)

    def test_phase10_helper_reports_are_deterministic_and_no_go(self) -> None:
        blockers = build_phase10_blocker_summary()
        go_no_go = build_phase10_go_no_go_report(list(PHASE10_NO_GO_REASONS), [])
        invariants = build_phase10_safety_invariant_report()
        summary = build_phase10_ai_handoff_summary(list(PHASE10_NO_GO_REASONS))

        self.assertIs(blockers["go_for_phase10"], False)
        self.assertIn("phase10_real_actions_not_implemented", blockers["no_go_reasons"])
        self.assertEqual(go_no_go["status"], "NO-GO")
        self.assertIs(go_no_go["permission_granted"], False)
        self.assertIn("readiness is not permission", invariants["invariants"])
        self.assertIn("Phase 10 real actions are not implemented", summary)

    def test_phase10_readiness_endpoint_is_read_only_and_deterministic(self) -> None:
        server = create_server("127.0.0.1", 0)
        host, port = server.server_address
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            with (
                patch("lain_desk_agent.main.observe", side_effect=AssertionError("observe called")),
                patch(
                    "lain_desk_agent.main.execute_action_contract",
                    side_effect=AssertionError("execution called"),
                ),
            ):
                with urlopen(
                    f"http://{host}:{port}/phase10-readiness/demo",
                    timeout=5,
                ) as response:
                    payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            thread.join(timeout=2)
            server.server_close()

        self.assertEqual(payload["report_version"], "phase10_readiness_v1")
        self.assertIs(payload["go_for_phase10"], False)
        self.assertIs(payload["real_actions_enabled"], False)
        self.assertIs(payload["phase10_real_actions_implemented"], False)

    def test_phase10_cockpit_ui_hooks_exist_and_are_read_only(self) -> None:
        html = UI_INDEX_HTML.read_text(encoding="utf-8")
        source = UI_APP_JS.read_text(encoding="utf-8")
        styles = UI_STYLES_CSS.read_text(encoding="utf-8")

        for element_id in [
            "phase10ReadinessPanel",
            "loadPhase10Readiness",
            "phase10ReadinessStatus",
            "phase10ReadinessGroupFilter",
            "phase10ReadinessGroups",
            "copyPhase10AIHandoffSummary",
            "copyPhase10ReadinessJson",
            "copyPhase10NoGoReasons",
            "copyPhase10SafetyInvariants",
            "expandPhase10ReadinessGroups",
            "collapsePhase10ReadinessGroups",
        ]:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', html)
                self.assertIn(f"#{element_id}", source)

        for function_name in [
            "loadPhase10Readiness",
            "renderPhase10Readiness",
            "renderPhase10ReadinessGroups",
            "renderPhase10ReadinessStrip",
            "copyPhase10ReadinessPayload",
            "copyPhase10AIHandoffSummaryPayload",
            "copyPhase10ReadinessJsonPayload",
            "copyPhase10NoGoReasonsPayload",
            "copyPhase10SafetyInvariantsPayload",
            "setPhase10ReadinessGroupsOpen",
        ]:
            with self.subTest(function_name=function_name):
                self.assertIn(f"function {function_name}", source)

        phase10_source = _source_between(
            source,
            "async function loadPhase10Readiness",
            "function setPhase9ExperimentSummary",
        )
        self.assertIn('fetch("/phase10-readiness/demo")', phase10_source)
        self.assertIn("navigator.clipboard.writeText", phase10_source)
        for forbidden in [
            'fetch("/execute"',
            "fetch('/execute'",
            'fetch("/approval"',
            "fetch('/approval'",
            "realActionEnabled = true",
            "real_action_enabled = true",
            "runWaitExecutionSelfTest",
            "recordApprovalDecision",
        ]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, phase10_source)

        self.assertIn(".phase10-readiness-panel", styles)
        self.assertIn(".phase10-readiness-chip", styles)
        self.assertIn(".phase10-readiness-section", styles)

    def test_project_status_snapshot_v3_records_phase10_no_go(self) -> None:
        payload = json.loads(STATUS_JSON.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema_version"], "project_status_snapshot_v3")
        self.assertIn("Phase 10.3", payload["project_phase"])
        self.assertIs(payload["dry_run_default"], True)
        self.assertIs(payload["read_only_default"], True)
        self.assertIs(payload["debug_only_default"], True)
        self.assertIs(payload["real_actions_enabled"], False)
        self.assertIs(payload["phase10_real_actions_implemented"], False)
        self.assertIs(payload["go_for_phase10"], False)
        self.assertIs(payload["global_status_cockpit"], True)
        self.assertIn(".\\scripts\\verify.ps1", payload["verification_commands"])

    def test_phase10_readiness_doc_exists_and_states_not_implemented(self) -> None:
        text = PHASE10_DOC.read_text(encoding="utf-8")
        normalized = text.lower()

        for phrase in [
            "phase 10 real actions are not implemented yet",
            "dry-run",
            "read-only",
            "debug-only",
            "no real desktop actions",
            "safety boundary",
            "no sandbox path may call `/execute`",
            "no real-action toggle",
            "readiness is not permission",
            "proposal is not execution",
            "cockpit display is not authorization",
            "phase 10.1 readiness cockpit status",
            "phase 10.2 global status cockpit status",
            "go_for_phase10 = false",
            "real actions are still disabled",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)

    def test_phase10_readiness_doc_covers_required_gate_topics(self) -> None:
        text = PHASE10_DOC.read_text(encoding="utf-8")

        for phrase in [
            "Prerequisite Gates Before Any Real Action Experiment",
            "Required Approvals",
            "Emergency Stop Requirements",
            "Post-action Verification Requirements",
            "Rollback Requirements",
            "Audit Logging Requirements",
            "Dry-run Parity Requirements",
            "Sandbox Scope Requirements",
            "Forbidden Actions",
            "Forbidden APIs",
            "Required Tests Before Phase 10 Implementation",
            "Required Manual Checks Before Phase 10 Implementation",
            "Required Documentation Before Phase 10 Implementation",
            "Go / No-go Checklist",
            "Stop Immediately If",
            "AI Handoff Checklist",
            "Phase 10.1 Readiness Cockpit Status",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_phase10_readiness_doc_mentions_core_safety_artifacts(self) -> None:
        text = PHASE10_DOC.read_text(encoding="utf-8")

        for phrase in [
            "Execution Policy",
            "Permission Profile",
            "Capability Registry",
            "verify.ps1",
            "safety_scan.py",
            "git diff --check",
            "node --check ui/app.js",
            "imported bundles are untrusted input",
            "phase10_real_actions_not_implemented",
            "real_action_adapter_absent",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_phase10_readiness_is_linked_from_project_docs(self) -> None:
        for doc in [README_DOC, ROADMAP_DOC, ARCHITECTURE_DOC]:
            with self.subTest(doc=doc.name):
                self.assertIn(
                    "docs/PHASE_10_READINESS_CHECKLIST.md",
                    doc.read_text(encoding="utf-8"),
                )


def _source_between(source: str, start_marker: str, end_marker: str) -> str:
    start = source.index(start_marker)
    end = source.index(end_marker, start)
    return source[start:end]


if __name__ == "__main__":
    unittest.main()
