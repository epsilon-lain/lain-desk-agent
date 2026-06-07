from __future__ import annotations

import unittest
from pathlib import Path

import _path  # noqa: F401


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AI_HANDOFF_DOC = PROJECT_ROOT / "docs" / "AI_HANDOFF_CONTEXT.md"
README_DOC = PROJECT_ROOT / "README.md"


class AIHandoffContextDocTests(unittest.TestCase):
    def test_ai_handoff_context_exists_and_has_required_boundary_phrases(self) -> None:
        text = AI_HANDOFF_DOC.read_text(encoding="utf-8")
        normalized = text.lower()

        for phrase in [
            "repository purpose",
            "current architecture",
            "current phase",
            "hard safety boundary",
            "dry-run",
            "read-only",
            "debug-only",
            "no real desktop actions",
            "no sandbox or replay `/execute` call",
            "no real-action toggle",
            "imported bundles are untrusted input",
            "ai handoff",
            "do not enable real actions unless the phase 10 readiness checklist",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)

    def test_ai_handoff_context_lists_important_files_and_commands(self) -> None:
        text = AI_HANDOFF_DOC.read_text(encoding="utf-8")

        for phrase in [
            "docs/PROJECT_HEALTH_SNAPSHOT.md",
            "docs/PHASE_10_READINESS_CHECKLIST.md",
            "docs/SAFETY_INVARIANTS.md",
            "src/lain_desk_agent/phase9_experiment.py",
            "src/lain_desk_agent/sandbox_experiment.py",
            "ui/app.js",
            "scripts/safety_scan.py",
            "scripts/verify.ps1",
            "scripts/project_status.ps1",
            ".\\scripts\\verify.ps1",
            "python scripts\\safety_scan.py",
            "node --check ui/app.js",
            "git diff --check",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_ai_handoff_context_distinguishes_debug_from_control(self) -> None:
        text = AI_HANDOFF_DOC.read_text(encoding="utf-8")

        for phrase in [
            "Proposal is not execution",
            "Readiness is not permission",
            "Cockpit display is not authorization",
            "Replay is read-only",
            "Validation errors do not mutate runtime state",
            "Known Safe Next Steps",
            "Known Dangerous Next Steps",
            "Copyable Mini-prompt",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_ai_handoff_context_is_linked_from_readme(self) -> None:
        self.assertIn(
            "docs/AI_HANDOFF_CONTEXT.md",
            README_DOC.read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
