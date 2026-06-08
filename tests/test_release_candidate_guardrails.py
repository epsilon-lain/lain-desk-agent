from __future__ import annotations

import ast
import json
import re
import unittest
from pathlib import Path

import _path  # noqa: F401
from lain_desk_agent.phase10_global_status import build_phase10_global_status_report
from lain_desk_agent.phase10_readiness import build_phase10_readiness_report


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src" / "lain_desk_agent"
UI_ROOT = PROJECT_ROOT / "ui"
STATUS_JSON = PROJECT_ROOT / "docs" / "project_status_snapshot.json"
PROJECT_STATUS_SCRIPT = PROJECT_ROOT / "scripts" / "project_status.ps1"

PY_RUNTIME_FILES = sorted(SRC_ROOT.glob("*.py"))
UI_RUNTIME_FILES = sorted(
    path for pattern in ("*.html", "*.js", "*.css") for path in UI_ROOT.glob(pattern)
)

FORBIDDEN_IMPORT_ROOTS = {
    "pynput",
    "keyboard",
    "mouse",
    "win32api",
}

FORBIDDEN_PYAUTOGUI_ATTRS = {
    "click",
    "doubleClick",
    "dragTo",
    "hotkey",
    "keyDown",
    "keyUp",
    "move",
    "moveTo",
    "mouseDown",
    "mouseUp",
    "press",
    "scroll",
    "typewrite",
    "write",
}

FORBIDDEN_CALL_ATTRS = {
    "SendInput",
    "mouse_event",
}

FORBIDDEN_COMMAND_STRINGS = {
    "xdotool",
    "osascript",
    "System Events",
}

REQUIRED_VERIFICATION_FRAGMENTS = (
    "scripts/verify.ps1",
    "safety_scan.py",
    "node --check ui/app.js",
    "git diff --check",
    "python -m unittest discover -s tests",
)

REQUIRED_IMPORTANT_DOCS = (
    "docs/PHASE_10_READINESS_CHECKLIST.md",
    "docs/AI_HANDOFF_CONTEXT.md",
    "docs/SAFETY_INVARIANTS.md",
    "docs/PROJECT_HEALTH_SNAPSHOT.md",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _runtime_text(paths: list[Path]) -> str:
    return "\n".join(_read(path) for path in paths)


def _normalize_command(command: str) -> str:
    return command.replace("\\", "/").lower()


def _function_name_before(source: str, index: int) -> str | None:
    function_pattern = re.compile(
        r"\b(?:async\s+)?function\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*\("
    )
    matches = list(function_pattern.finditer(source[:index]))
    if not matches:
        return None
    return matches[-1].group(1)


def _call_name(call: ast.Call) -> str:
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ""


def _call_owner_name(call: ast.Call) -> str:
    func = call.func
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        return func.value.id
    return ""


class ReleaseCandidateRuntimeGuardrailTests(unittest.TestCase):
    def test_runtime_python_does_not_import_desktop_actuation_packages(self) -> None:
        findings: list[str] = []

        for path in PY_RUNTIME_FILES:
            tree = ast.parse(_read(path), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        root = alias.name.split(".", 1)[0]
                        if root in FORBIDDEN_IMPORT_ROOTS:
                            findings.append(f"{path}: import {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    root = (node.module or "").split(".", 1)[0]
                    if root in FORBIDDEN_IMPORT_ROOTS:
                        findings.append(f"{path}: from {node.module} import ...")
                    if root == "pyautogui":
                        for alias in node.names:
                            if alias.name in FORBIDDEN_PYAUTOGUI_ATTRS:
                                findings.append(
                                    f"{path}: from pyautogui import {alias.name}"
                                )

        self.assertEqual(findings, [])

    def test_runtime_python_does_not_call_desktop_control_apis(self) -> None:
        findings: list[str] = []

        for path in PY_RUNTIME_FILES:
            tree = ast.parse(_read(path), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    call_name = _call_name(node)
                    if call_name in FORBIDDEN_CALL_ATTRS:
                        findings.append(f"{path}:{node.lineno} calls {call_name}")
                    if (
                        call_name in FORBIDDEN_PYAUTOGUI_ATTRS
                        and _call_owner_name(node) == "pyautogui"
                    ):
                        findings.append(f"{path}:{node.lineno} calls pyautogui.{call_name}")
                    for arg in list(node.args) + [
                        keyword.value for keyword in node.keywords if keyword.value
                    ]:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            for forbidden in FORBIDDEN_COMMAND_STRINGS:
                                if forbidden in arg.value:
                                    findings.append(
                                        f"{path}:{node.lineno} command string {forbidden}"
                                    )

        self.assertEqual(findings, [])

    def test_ui_execute_fetches_are_limited_to_wait_self_test(self) -> None:
        app_js = _read(UI_ROOT / "app.js")
        fetch_pattern = re.compile(r"fetch\(\s*([\"'])/execute\1")
        findings: list[str] = []

        for match in fetch_pattern.finditer(app_js):
            function_name = _function_name_before(app_js, match.start())
            if function_name != "runWaitExecutionSelfTest":
                findings.append(
                    f"unexpected /execute fetch in {function_name or 'global scope'}"
                )

        self.assertEqual(findings, [])

    def test_cockpit_has_no_real_action_controls(self) -> None:
        ui_text = _runtime_text(UI_RUNTIME_FILES)
        lowered = ui_text.lower()
        findings: list[str] = []

        toggle_id_pattern = re.compile(
            r"id\s*=\s*([\"'])([^\"']*(?:realaction|real-action|real_action)[^\"']*toggle[^\"']*)\1",
            re.IGNORECASE,
        )
        findings.extend(f"real-action toggle id {match.group(2)}" for match in toggle_id_pattern.finditer(ui_text))

        button_pattern = re.compile(r"<button\b[^>]*>(.*?)</button>", re.IGNORECASE | re.DOTALL)
        for match in button_pattern.finditer(ui_text):
            label = re.sub(r"<[^>]+>", "", match.group(1)).strip().lower()
            if label in {"execute", "execute action", "run action", "run sandbox action"}:
                findings.append(f"execute button label {label!r}")

        for snippet in (
            "approve real action",
            "approve execution",
            "approve desktop action",
            "approve sandbox action",
            "authorize real action",
            "enable real action",
        ):
            if snippet in lowered:
                findings.append(f"real-action approval/control phrase {snippet!r}")

        dynamic_button_patterns = (
            r"\.textContent\s*=\s*([\"'])Execute\1",
            r"\.innerText\s*=\s*([\"'])Execute\1",
            r"\.ariaLabel\s*=\s*([\"'])Execute\1",
        )
        for pattern in dynamic_button_patterns:
            if re.search(pattern, ui_text):
                findings.append(f"dynamic execute button pattern {pattern}")

        self.assertEqual(findings, [])

    def test_runtime_defaults_do_not_turn_on_phase10_or_real_actions(self) -> None:
        runtime_text = _runtime_text(PY_RUNTIME_FILES + UI_RUNTIME_FILES)
        default_true_patterns = (
            r"\breal_action_enabled\b\s*[:=]\s*true\b",
            r"\breal_action_enabled\b\s*[:=]\s*True\b",
            r"[\"']real_action_enabled[\"']\s*:\s*true\b",
            r"[\"']real_action_enabled[\"']\s*:\s*True\b",
            r"\bgo_for_phase10\b\s*[:=]\s*true\b",
            r"\bgo_for_phase10\b\s*[:=]\s*True\b",
            r"[\"']go_for_phase10[\"']\s*:\s*true\b",
            r"[\"']go_for_phase10[\"']\s*:\s*True\b",
        )

        findings = [
            pattern for pattern in default_true_patterns if re.search(pattern, runtime_text)
        ]

        self.assertEqual(findings, [])


class ReleaseCandidatePhase10ReportTests(unittest.TestCase):
    def assert_no_go_report_shape(self, report: dict[str, object]) -> None:
        self.assertIs(report["go_for_phase10"], False)
        self.assertIs(report["real_actions_enabled"], False)
        self.assertIs(report["phase10_real_actions_implemented"], False)
        self.assertTrue(report["no_go_reasons"])

        forbidden_actions = " ".join(report["forbidden_actions"])  # type: ignore[arg-type]
        for phrase in ("real click", "real type", "real hotkey", "real scroll", "real switch_app"):
            self.assertIn(phrase, forbidden_actions)

        forbidden_apis = " ".join(report["forbidden_apis"])  # type: ignore[arg-type]
        for api_name in (
            "pyautogui",
            "pynput",
            "keyboard",
            "mouse",
            "win32api",
            "SendInput",
            "mouse_event",
            "xdotool",
            "AppleScript UI scripting",
        ):
            self.assertIn(api_name, forbidden_apis)

        self.assertIn("ai_handoff_summary", report)
        ai_summary = str(report.get("ai_handoff_summary") or "")
        self.assertTrue(ai_summary)
        self.assertIn("not", ai_summary.lower())

        commands = report.get("required_test_commands") or report.get("verification_commands")
        self.assertIsInstance(commands, list)
        normalized_commands = "\n".join(_normalize_command(str(command)) for command in commands)  # type: ignore[union-attr]
        for fragment in REQUIRED_VERIFICATION_FRAGMENTS:
            self.assertIn(fragment, normalized_commands)

        serialized = json.dumps(report, sort_keys=True)
        sensitive_value_pattern = re.compile(
            r"(?i)(token|password|secret|api_key)\s*[:=]\s*[\"']?[^\"'\s,;]{4,}"
        )
        self.assertIsNone(sensitive_value_pattern.search(serialized))
        self.assertIsNone(re.search(r"sk-[A-Za-z0-9]{20,}", serialized))

    def test_phase10_readiness_report_stays_no_go(self) -> None:
        self.assert_no_go_report_shape(build_phase10_readiness_report())

    def test_phase10_global_status_report_stays_no_go(self) -> None:
        self.assert_no_go_report_shape(build_phase10_global_status_report())


class ProjectStatusSnapshotGuardrailTests(unittest.TestCase):
    def test_project_status_snapshot_is_valid_no_go_json(self) -> None:
        data = json.loads(_read(STATUS_JSON))

        self.assertIs(data["real_actions_enabled"], False)
        self.assertIs(data["phase10_real_actions_implemented"], False)
        self.assertIs(data["go_for_phase10"], False)

        commands = "\n".join(
            _normalize_command(command) for command in data["verification_commands"]
        )
        for fragment in REQUIRED_VERIFICATION_FRAGMENTS:
            self.assertIn(fragment, commands)

        important_docs = set(data["important_docs"])
        for doc_path in REQUIRED_IMPORTANT_DOCS:
            self.assertIn(doc_path, important_docs)


class ProjectStatusScriptGuardrailTests(unittest.TestCase):
    def test_project_status_script_remains_read_only(self) -> None:
        script = _read(PROJECT_STATUS_SCRIPT)
        lowered = script.lower()

        for required in ("safety_scan.py", "node --check ui/app.js", "git diff --check"):
            self.assertIn(required, lowered)

        forbidden_snippets = (
            "git add",
            "git commit",
            "git push",
            "/execute",
            "pyautogui",
            "pynput",
            "import keyboard",
            "import mouse",
            "win32api",
            "sendinput",
            "mouse_event",
            "xdotool",
            "applescript ui scripting",
        )
        for snippet in forbidden_snippets:
            self.assertNotIn(snippet, lowered)


if __name__ == "__main__":
    unittest.main()
