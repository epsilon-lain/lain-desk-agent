from __future__ import annotations

import unittest
from pathlib import Path

import _path  # noqa: F401


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAFETY_INVARIANTS_DOC = PROJECT_ROOT / "docs" / "SAFETY_INVARIANTS.md"
README_DOC = PROJECT_ROOT / "README.md"
ARCHITECTURE_DOC = PROJECT_ROOT / "docs" / "ARCHITECTURE.md"
PROJECT_STATUS_SCRIPT = PROJECT_ROOT / "scripts" / "project_status.ps1"
UI_APP_JS = PROJECT_ROOT / "ui" / "app.js"
PHASE10_READINESS_MODULE = PROJECT_ROOT / "src" / "lain_desk_agent" / "phase10_readiness.py"
PHASE8_RUNTIME_FILES = [
    PROJECT_ROOT / "src" / "lain_desk_agent" / "sandbox_experiment.py",
    PROJECT_ROOT / "src" / "lain_desk_agent" / "sandbox_evaluation.py",
    PROJECT_ROOT / "src" / "lain_desk_agent" / "phase9_experiment.py",
]


class SafetyInvariantsTests(unittest.TestCase):
    def test_safety_invariants_doc_exists_and_has_required_phrases(self) -> None:
        text = SAFETY_INVARIANTS_DOC.read_text(encoding="utf-8")
        normalized = text.lower()

        for phrase in [
            "dry-run",
            "read-only",
            "debug-only",
            "no real desktop actions",
            "no sandbox path calls `/execute`",
            "no real-action toggle",
            "imported bundles are untrusted input",
            "replay is read-only",
            "validation errors do not mutate runtime state",
            "execution policy",
            "permission profile",
            "capability registry",
            "readiness is not permission",
            "proposal is not execution",
            "cockpit display is not authorization",
            "phase 10 real-action implementation",
            "go_for_phase10",
            "phase10_real_actions_implemented",
            "no real-action adapter",
            "verify.ps1",
            "safety_scan.py",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)

    def test_safety_invariants_doc_is_linked_from_readme_and_architecture(self) -> None:
        for doc in [README_DOC, ARCHITECTURE_DOC]:
            with self.subTest(doc=doc.name):
                self.assertIn(
                    "docs/SAFETY_INVARIANTS.md",
                    doc.read_text(encoding="utf-8"),
                )

    def test_phase8_and_phase9_runtime_files_do_not_import_real_actuation_apis(self) -> None:
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
            "keyboard",
            "mouse",
            "SendInput",
            "mouse_event",
            "xdotool",
            "AppleScript",
        ]

        for path in PHASE8_RUNTIME_FILES:
            source = path.read_text(encoding="utf-8")
            for fragment in forbidden_fragments:
                with self.subTest(path=path.name, fragment=fragment):
                    self.assertNotIn(fragment, source)

    def test_phase8_and_phase9_runtime_files_do_not_call_execute_or_enable_real_action(self) -> None:
        forbidden_fragments = [
            '"/execute"',
            "'/execute'",
            "fetch(",
            "execute_action_contract",
            "real_action_enabled = True",
            "real_action_enabled=True",
            "realActionEnabled = true",
        ]

        for path in PHASE8_RUNTIME_FILES:
            source = path.read_text(encoding="utf-8")
            for fragment in forbidden_fragments:
                with self.subTest(path=path.name, fragment=fragment):
                    self.assertNotIn(fragment, source)

    def test_phase10_readiness_module_has_no_execution_calls_or_imports(self) -> None:
        source = PHASE10_READINESS_MODULE.read_text(encoding="utf-8")

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

    def test_sandbox_and_phase9_ui_sections_do_not_trigger_execution(self) -> None:
        source = UI_APP_JS.read_text(encoding="utf-8")
        sandbox_ui = _source_between(
            source,
            "async function loadSandboxEvaluation",
            "function setPlannerEvaluationSummary",
        )
        phase9_ui = _source_between(
            source,
            "async function loadPhase9Experiment",
            "function setSandboxEvaluationSummary",
        )

        for name, section in {"sandbox": sandbox_ui, "phase9": phase9_ui}.items():
            for fragment in [
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
                "keyboard",
                "mouse",
                "win32api",
                "SendInput",
                "mouse_event",
                "xdotool",
                "AppleScript",
            ]:
                with self.subTest(section=name, fragment=fragment):
                    self.assertNotIn(fragment, section)

    def test_phase10_readiness_ui_section_does_not_trigger_execution(self) -> None:
        source = UI_APP_JS.read_text(encoding="utf-8")
        phase10_ui = _source_between(
            source,
            "async function loadPhase10Readiness",
            "function setPhase9ExperimentSummary",
        )

        self.assertIn('fetch("/phase10-readiness/demo")', phase10_ui)
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
                self.assertNotIn(forbidden, phase10_ui)

    def test_project_status_helper_is_read_only(self) -> None:
        text = PROJECT_STATUS_SCRIPT.read_text(encoding="utf-8")

        for required in [
            "git status --short",
            "git log -n 5 --oneline",
            "python -m unittest discover -s tests",
            "python scripts/safety_scan.py",
            "node --check ui/app.js",
            "git diff --check",
        ]:
            with self.subTest(required=required):
                self.assertIn(required, text)

        for forbidden in [
            "git add",
            "git commit",
            "git push",
            "/execute",
            "Invoke-WebRequest",
            "Invoke-RestMethod",
        ]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, text)


def _source_between(source: str, start_marker: str, end_marker: str) -> str:
    start = source.index(start_marker)
    end = source.index(end_marker, start)
    return source[start:end]


if __name__ == "__main__":
    unittest.main()
