from __future__ import annotations

import unittest
import json
from pathlib import Path

import _path  # noqa: F401


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DOC = PROJECT_ROOT / "docs" / "PROJECT_HEALTH_SNAPSHOT.md"
README_DOC = PROJECT_ROOT / "README.md"
ROADMAP_DOC = PROJECT_ROOT / "docs" / "ROADMAP.md"
STATUS_JSON = PROJECT_ROOT / "docs" / "project_status_snapshot.json"


class ProjectHealthSnapshotTests(unittest.TestCase):
    def test_project_health_snapshot_exists_and_has_handoff_phrases(self) -> None:
        self.assertTrue(SNAPSHOT_DOC.exists())
        text = SNAPSHOT_DOC.read_text(encoding="utf-8")
        normalized = text.lower()

        for phrase in [
            "dry-run",
            "read-only",
            "debug-only",
            "no real desktop actions",
            "phase 9",
            "phase 10 readiness",
            "phase 10.1 readiness cockpit",
            "phase 10.2 global status",
            "go_for_phase10 = false",
            "safety boundary",
            "no /execute",
            "no real-action toggle",
            "imported bundles are untrusted input",
            "verify.ps1",
            "safety_scan.py",
            "ai handoff",
            "execution policy",
            "permission profile",
            "capability registry",
            "readiness is not permission",
            "proposal is not execution",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)

    def test_project_health_snapshot_is_linked_from_readme_and_roadmap(self) -> None:
        for doc in [README_DOC, ROADMAP_DOC]:
            with self.subTest(doc=doc.name):
                self.assertIn(
                    "docs/PROJECT_HEALTH_SNAPSHOT.md",
                    doc.read_text(encoding="utf-8"),
                )

    def test_project_status_snapshot_json_is_static_and_safe(self) -> None:
        payload = json.loads(STATUS_JSON.read_text(encoding="utf-8"))

        self.assertEqual(payload["project"], "lain-desk-agent")
        self.assertEqual(payload["schema_version"], "project_status_snapshot_v3")
        self.assertIs(payload["real_actions_enabled"], False)
        self.assertIs(payload["phase10_real_actions_implemented"], False)
        self.assertIs(payload["go_for_phase10"], False)
        self.assertIs(payload["dry_run_default"], True)
        self.assertIs(payload["read_only_default"], True)
        self.assertIs(payload["debug_only_default"], True)
        self.assertIs(payload["global_status_cockpit"], True)
        self.assertIn("docs/PHASE_10_READINESS_CHECKLIST.md", payload["important_docs"])
        self.assertIn("docs/project_status_snapshot.json", payload["important_docs"])
        self.assertIn("no real desktop actions", payload["safety_boundary"])
        self.assertIn("readiness is not permission", payload["safety_boundary"])
        self.assertIn("export/import/replay is not execution", payload["safety_boundary"])
        self.assertIn(".\\scripts\\verify.ps1", payload["verification_commands"])


if __name__ == "__main__":
    unittest.main()
