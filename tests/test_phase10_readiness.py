from __future__ import annotations

import unittest
from pathlib import Path

import _path  # noqa: F401


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PHASE10_DOC = PROJECT_ROOT / "docs" / "PHASE_10_READINESS_CHECKLIST.md"
README_DOC = PROJECT_ROOT / "README.md"
ROADMAP_DOC = PROJECT_ROOT / "docs" / "ROADMAP.md"
ARCHITECTURE_DOC = PROJECT_ROOT / "docs" / "ARCHITECTURE.md"


class Phase10ReadinessDocTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
