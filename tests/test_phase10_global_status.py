from __future__ import annotations

import json
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.request import urlopen

import _path  # noqa: F401
from lain_desk_agent.main import create_server
from lain_desk_agent.phase10_global_status import (
    build_phase10_global_ai_handoff_payload,
    build_phase10_global_status_report,
    build_phase10_global_status_summary,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GLOBAL_STATUS_MODULE = PROJECT_ROOT / "src" / "lain_desk_agent" / "phase10_global_status.py"
UI_INDEX_HTML = PROJECT_ROOT / "ui" / "index.html"
UI_APP_JS = PROJECT_ROOT / "ui" / "app.js"
UI_STYLES_CSS = PROJECT_ROOT / "ui" / "styles.css"


class Phase10GlobalStatusTests(unittest.TestCase):
    def test_phase10_global_status_module_exists(self) -> None:
        self.assertTrue(GLOBAL_STATUS_MODULE.exists())

    def test_global_status_report_contains_required_fields_and_no_go_flags(self) -> None:
        report = build_phase10_global_status_report()

        for field in [
            "report_version",
            "project_phase",
            "dry_run",
            "read_only",
            "debug_only",
            "real_actions_enabled",
            "phase10_real_actions_implemented",
            "go_for_phase10",
            "no_go_reasons",
            "completed_phase_summary",
            "safety_boundary",
            "safety_invariants",
            "important_docs",
            "important_runtime_files",
            "verification_commands",
            "current_cockpit_capabilities",
            "forbidden_actions",
            "forbidden_apis",
            "ai_handoff_summary",
            "recommended_next_work",
        ]:
            with self.subTest(field=field):
                self.assertIn(field, report)

        self.assertEqual(report["report_version"], "phase10_global_status_v1")
        self.assertIn("Phase 10.2", report["project_phase"])
        self.assertIs(report["dry_run"], True)
        self.assertIs(report["read_only"], True)
        self.assertIs(report["debug_only"], True)
        self.assertIs(report["real_actions_enabled"], False)
        self.assertIs(report["phase10_real_actions_implemented"], False)
        self.assertIs(report["go_for_phase10"], False)
        self.assertIn("real_actions_disabled", report["no_go_reasons"])
        self.assertIn("phase10_real_actions_not_implemented", report["no_go_reasons"])
        self.assertEqual(build_phase10_global_status_report(), report)

    def test_global_status_report_lists_forbidden_apis_and_verification_commands(self) -> None:
        report = build_phase10_global_status_report()
        commands = "\n".join(report["verification_commands"])

        for command_fragment in [
            "verify.ps1",
            "safety_scan.py",
            "node --check ui/app.js",
            "git diff --check",
        ]:
            with self.subTest(command_fragment=command_fragment):
                self.assertIn(command_fragment, commands)

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

    def test_global_status_report_includes_phase9_validation_state(self) -> None:
        report = build_phase10_global_status_report()
        state = report["phase9_export_import_replay_validation_state"]

        self.assertEqual(state["source"], "deterministic_phase9_fixture")
        self.assertGreater(state["scenario_count"], 0)
        self.assertEqual(state["validation_status"], "valid")
        self.assertIs(state["validation_passed"], True)
        self.assertEqual(state["replay_status"], "replayed")
        self.assertIs(state["replay_allowed_as_read_only"], True)
        self.assertIs(state["real_action_enabled"], False)
        self.assertIs(state["execution_attempted"], False)
        self.assertIs(state["state_mutation"], False)

    def test_global_status_handoff_payload_and_summary_exist(self) -> None:
        handoff = build_phase10_global_ai_handoff_payload()
        summary = build_phase10_global_status_summary()

        self.assertEqual(handoff["payload_version"], "phase10_global_ai_handoff_v1")
        self.assertIn("ai_handoff_summary", handoff)
        self.assertIn("Phase 10.2", handoff["project_phase"])
        self.assertEqual(summary["summary_version"], "phase10_global_status_summary_v1")
        self.assertEqual(summary["status"], "NO-GO")
        self.assertIs(summary["go_for_phase10"], False)
        self.assertEqual(summary["phase9_validation_status"], "valid")

    def test_global_status_report_has_no_sensitive_field_names(self) -> None:
        report = build_phase10_global_status_report()
        encoded = json.dumps(report).lower()

        for forbidden in ["secret", "token", "api_key", "password"]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, encoded)

    def test_global_status_endpoint_is_read_only_and_deterministic(self) -> None:
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
                    f"http://{host}:{port}/phase10-global-status/demo",
                    timeout=5,
                ) as response:
                    payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            thread.join(timeout=2)
            server.server_close()

        self.assertEqual(payload["report_version"], "phase10_global_status_v1")
        self.assertIs(payload["go_for_phase10"], False)
        self.assertIs(payload["real_actions_enabled"], False)
        self.assertIs(payload["phase10_real_actions_implemented"], False)

    def test_global_status_module_has_no_execution_calls_or_desktop_apis(self) -> None:
        source = GLOBAL_STATUS_MODULE.read_text(encoding="utf-8")

        for forbidden in [
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
            "execute_action_contract",
            "fetch(",
            '"/execute"',
            "'/execute'",
            "real_action_enabled = True",
            "realActionEnabled = true",
        ]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_global_status_cockpit_hooks_exist_and_are_read_only(self) -> None:
        html = UI_INDEX_HTML.read_text(encoding="utf-8")
        source = UI_APP_JS.read_text(encoding="utf-8")
        styles = UI_STYLES_CSS.read_text(encoding="utf-8")

        for element_id in [
            "phase10GlobalStatusPanel",
            "loadPhase10GlobalStatus",
            "phase10GlobalStatusStatus",
            "phase10GlobalStatusFilter",
            "phase10GlobalStatusGroups",
            "copyPhase10GlobalStatusJson",
            "copyPhase10GlobalAIHandoffSummary",
            "copyPhase10GlobalNoGoReasons",
            "copyPhase10GlobalVerificationCommands",
            "copyPhase10GlobalSafetyBoundary",
            "expandPhase10GlobalStatusGroups",
            "collapsePhase10GlobalStatusGroups",
        ]:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', html)
                self.assertIn(f"#{element_id}", source)

        for function_name in [
            "loadPhase10GlobalStatus",
            "renderPhase10GlobalStatus",
            "renderPhase10GlobalStatusGroups",
            "renderPhase10GlobalStatusStrip",
            "copyPhase10GlobalStatusPayload",
            "copyPhase10GlobalStatusJsonPayload",
            "copyPhase10GlobalAIHandoffPayload",
            "copyPhase10GlobalNoGoReasonsPayload",
            "copyPhase10GlobalVerificationCommandsPayload",
            "copyPhase10GlobalSafetyBoundaryPayload",
            "setPhase10GlobalStatusGroupsOpen",
        ]:
            with self.subTest(function_name=function_name):
                self.assertIn(f"function {function_name}", source)

        global_source = _source_between(
            source,
            "async function loadPhase10GlobalStatus",
            "function setPhase9ExperimentSummary",
        )
        self.assertIn('fetch("/phase10-global-status/demo")', global_source)
        self.assertIn("navigator.clipboard.writeText", global_source)
        for forbidden in [
            'fetch("/execute"',
            "fetch('/execute'",
            'fetch("/approval"',
            "fetch('/approval'",
            "runWaitExecutionSelfTest",
            "recordApprovalDecision",
            "real_action_enabled = true",
            "realActionEnabled = true",
            "pyautogui",
            "pynput",
            "win32api",
            "SendInput",
            "mouse_event",
            "xdotool",
            "AppleScript",
        ]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, global_source)

        panel_html = _source_between(
            html,
            'id="phase10GlobalStatusPanel"',
            'id="safetyActionArea"',
        )
        for forbidden in ["approve", "/execute", "real-action toggle"]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, panel_html.lower())

        self.assertIn(".phase10-global-status-panel", styles)


def _source_between(source: str, start_marker: str, end_marker: str) -> str:
    start = source.index(start_marker)
    end = source.index(end_marker, start)
    return source[start:end]


if __name__ == "__main__":
    unittest.main()
