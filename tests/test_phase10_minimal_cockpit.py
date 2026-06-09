from __future__ import annotations

import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
UI_INDEX_HTML = PROJECT_ROOT / "ui" / "index.html"
UI_APP_JS = PROJECT_ROOT / "ui" / "app.js"
UI_STYLES_CSS = PROJECT_ROOT / "ui" / "styles.css"
PHASE10_DOCS = [
    PROJECT_ROOT / "docs" / "ARCHITECTURE.md",
    PROJECT_ROOT / "docs" / "ROADMAP.md",
    PROJECT_ROOT / "docs" / "PHASE_10_READINESS_CHECKLIST.md",
    PROJECT_ROOT / "docs" / "SAFETY_INVARIANTS.md",
    PROJECT_ROOT / "docs" / "AI_HANDOFF_CONTEXT.md",
]


class Phase10MinimalCockpitTests(unittest.TestCase):
    def test_minimal_cockpit_html_hooks_exist(self) -> None:
        html = UI_INDEX_HTML.read_text(encoding="utf-8")

        for element_id in [
            "phase10MinimalCockpit",
            "phase10MinimalStatusbar",
            "phase10MinimalControls",
            "phase10ObservationModeToggle",
            "phase10InputPopup",
            "phase10InputTitle",
            "phase10InputReason",
            "phase10InputField",
            "phase10InputConfirm",
            "phase10InputCancel",
        ]:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', html)

        for hook in [
            "data-phase10-minimal-cockpit",
            "data-phase10-minimal-statusbar",
            "data-phase10-minimal-controls",
            "data-phase10-minimal-summary-cards",
            "data-phase10-minimal-scenario-groups",
            "data-phase10-input-popup",
            "data-phase10-input-field",
            "data-phase10-input-confirm",
            "data-phase10-input-cancel",
        ]:
            with self.subTest(hook=hook):
                self.assertIn(hook, html)

    def test_advanced_controls_are_hidden_by_default(self) -> None:
        html = UI_INDEX_HTML.read_text(encoding="utf-8")

        for hidden_fragment in [
            'id="phase10MinimalControls"\n                data-phase10-minimal-controls="true"\n                hidden',
            'id="phase10MinimalSummaryCards"\n                data-phase10-minimal-summary-cards="true"\n                hidden',
            'id="phase10MinimalScenarioGroups"\n                data-phase10-minimal-scenario-groups="true"\n                hidden',
        ]:
            with self.subTest(hidden_fragment=hidden_fragment):
                self.assertIn(hidden_fragment, html)

    def test_minimal_cockpit_js_functions_and_popup_hooks_exist(self) -> None:
        source = UI_APP_JS.read_text(encoding="utf-8")

        for function_name in [
            "initPhase10MinimalCockpit",
            "setPhase10MinimalStatus",
            "phase10HandleInputRequiredEvent",
            "showPhase10InputPopup",
            "closePhase10InputPopup",
            "recordPhase10DryRunInputMetadata",
            "bindPhase10InputPopup",
            "bindPhase10MinimalControls",
            "applyPhase10MinimalFilter",
            "setPhase10MinimalGroupsOpen",
        ]:
            with self.subTest(function_name=function_name):
                self.assertIn(f"function {function_name}", source)

        minimal_source = _source_between(
            source,
            "function initPhase10MinimalCockpit",
            "agentName.addEventListener",
        )
        for snippet in [
            'event.key === "Escape"',
            'addEventListener("submit"',
            "phase10InputCancel.addEventListener",
            "phase10InputPopup.showModal()",
            "phase10InputPopup.close()",
            "phase10InputRequired",
            "phase10CurrentInputType",
            "PHASE10_INPUT_REQUIRED_TYPES",
            "PHASE10_SECRET_INPUT_TYPES",
            "value_present",
            "raw_value_persisted: false",
        ]:
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, minimal_source)

    def test_input_metadata_does_not_persist_raw_sensitive_values(self) -> None:
        source = UI_APP_JS.read_text(encoding="utf-8")
        minimal_source = _source_between(
            source,
            "function initPhase10MinimalCockpit",
            "agentName.addEventListener",
        )

        self.assertIn('new Set(["approval", "password", "mfa", "login", "consent"])', source)
        self.assertIn('new Set(["password", "mfa", "login"])', source)
        for forbidden in [
            "raw_value:",
            "input_value:",
            "secret_value:",
            "password_value:",
            "mfa_value:",
            "login_value:",
            "phase10DryRunInputMetadata.push(phase10InputField.value",
            "localStorage.setItem(\"phase10",
            "window.localStorage.setItem(\"phase10",
        ]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, minimal_source)

    def test_minimal_cockpit_is_local_only_and_does_not_trigger_actions(self) -> None:
        source = UI_APP_JS.read_text(encoding="utf-8")
        minimal_source = _source_between(
            source,
            "function initPhase10MinimalCockpit",
            "agentName.addEventListener",
        )

        for forbidden in [
            "fetch(",
            '"/execute"',
            "'/execute'",
            '"/approval"',
            "'/approval'",
            "recordApprovalDecision",
            "runWaitExecutionSelfTest",
            "realActionEnabled = true",
            "real_action_enabled = true",
            "pyautogui",
            "pynput",
            "keyboard",
            "mouse_event",
            "win32api",
            "SendInput",
            "xdotool",
            "AppleScript",
        ]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, minimal_source)

    def test_minimal_cockpit_css_exists(self) -> None:
        styles = UI_STYLES_CSS.read_text(encoding="utf-8")

        for selector in [
            ".phase10-minimal-cockpit",
            ".phase10-minimal-statusbar",
            '[data-phase10-input-required="true"]',
            ".phase10-minimal-controls",
            ".phase10-minimal-summary-card",
            ".phase10-minimal-group",
            ".phase10-input-popup",
            ".phase10-input-popup::backdrop",
            ".phase10-input-actions",
        ]:
            with self.subTest(selector=selector):
                self.assertIn(selector, styles)

    def test_docs_cover_phase10_minimal_cockpit_boundary(self) -> None:
        combined = ""
        for path in PHASE10_DOCS:
            text = path.read_text(encoding="utf-8")
            combined += f"\n{text}"
            with self.subTest(path=path.name):
                self.assertIn("Phase 10.4", text)

        normalized = combined.lower()
        for phrase in [
            "minimal observation",
            "lazy popup",
            "dry-run",
            "read-only",
            "value_present",
            "raw secret",
            "does not grant execution permission",
            "real actions are still disabled",
            "/execute",
            "/approval",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)


def _source_between(source: str, start_marker: str, end_marker: str) -> str:
    start = source.index(start_marker)
    end = source.index(end_marker, start)
    return source[start:end]


if __name__ == "__main__":
    unittest.main()
