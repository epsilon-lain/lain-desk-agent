from __future__ import annotations

import unittest
from pathlib import Path

import _path  # noqa: F401


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DOC = PROJECT_ROOT / "docs" / "PROJECT_HEALTH_SNAPSHOT.md"
README_DOC = PROJECT_ROOT / "README.md"
ROADMAP_DOC = PROJECT_ROOT / "docs" / "ROADMAP.md"


class ProjectHealthSnapshotTests(unittest.TestCase):
    def test_project_health_snapshot_exists_and_has_handoff_phrases(self) -> None:
        self.assertTrue(SNAPSHOT_DOC.exists())
        text = SNAPSHOT_DOC.read_text(encoding="utf-8")
        normalized = text.lower()

        for phrase in [
            "dry-run",
            "read-only",
            "no real desktop actions",
            "phase 9",
            "phase 10 readiness",
            "safety boundary",
            "verify.ps1",
            "safety_scan.py",
            "ai handoff",
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


if __name__ == "__main__":
    unittest.main()
