from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import _path  # noqa: F401
from lain_desk_agent.main import read_recent_events


class RunEventViewerTests(unittest.TestCase):
    def test_missing_events_file_returns_empty_list(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertEqual(read_recent_events(run_dir=temp_dir), [])

    def test_recent_events_are_returned_newest_first(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            events_path = Path(temp_dir) / "events.jsonl"
            _write_events(
                events_path,
                [
                    {"type": "observation.created", "timestamp": "2026-01-01T00:00:00Z"},
                    {"type": "proposal.approved", "timestamp": "2026-01-01T00:00:01Z"},
                    {"type": "snapshot.deleted", "timestamp": "2026-01-01T00:00:02Z"},
                ],
            )

            events = read_recent_events(run_dir=temp_dir, limit=2)

        self.assertEqual([event["type"] for event in events], ["snapshot.deleted", "proposal.approved"])

    def test_malformed_lines_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            events_path = Path(temp_dir) / "events.jsonl"
            events_path.write_text(
                "\n".join(
                    [
                        json.dumps({"type": "observation.created"}),
                        "{not json",
                        json.dumps({"type": "proposal.rejected"}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            events = read_recent_events(run_dir=temp_dir, limit=5)

        self.assertEqual([event["type"] for event in events], ["proposal.rejected", "observation.created"])


def _write_events(path: Path, events: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(event, ensure_ascii=False) + "\n" for event in events),
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
