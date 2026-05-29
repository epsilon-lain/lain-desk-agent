from __future__ import annotations

import json
import tempfile
import unittest
from collections import namedtuple
from pathlib import Path

import _path  # noqa: F401
from lain_desk_agent.resource_guard import (
    BYTES_PER_MB,
    ResourceGuardError,
    ResourceLimits,
    cleanup_run_snapshots,
    ensure_min_free_disk,
)


class ResourceGuardTests(unittest.TestCase):
    def test_cleanup_deletes_oldest_pairs_and_keeps_events_log(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_path = Path(temp_dir)
            events_path = run_path / "events.jsonl"
            events_path.write_text('{"type":"sentinel"}\n', encoding="utf-8")

            for number in range(1, 104):
                _write_snapshot_pair(run_path, number)

            cleanup_run_snapshots(
                run_path,
                ResourceLimits(
                    max_observations_per_run=100,
                    max_run_size_mb=300,
                    min_free_disk_mb=0,
                ),
            )

            self.assertFalse((run_path / "obs_0001.json").exists())
            self.assertFalse((run_path / "obs_0001.png").exists())
            self.assertFalse((run_path / "obs_0003.json").exists())
            self.assertFalse((run_path / "obs_0003.png").exists())
            self.assertTrue((run_path / "obs_0004.json").exists())
            self.assertTrue((run_path / "obs_0103.png").exists())
            self.assertTrue(events_path.exists())

            events = _read_jsonl(events_path)
            deleted_events = [event for event in events if event["type"] == "snapshot.deleted"]

        self.assertEqual(events[0]["type"], "sentinel")
        self.assertEqual(len(deleted_events), 3)
        self.assertEqual(deleted_events[0]["observation_id"], "obs_0001")
        self.assertEqual(deleted_events[0]["reason"], "max_observations_per_run")

    def test_cleanup_uses_run_size_limit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_path = Path(temp_dir)
            events_path = run_path / "events.jsonl"
            events_path.write_text("", encoding="utf-8")

            for number in range(1, 4):
                _write_snapshot_pair(run_path, number, screenshot_size=800)

            cleanup_run_snapshots(
                run_path,
                ResourceLimits(
                    max_observations_per_run=100,
                    max_run_size_mb=0.002,
                    min_free_disk_mb=0,
                ),
            )

            self.assertFalse((run_path / "obs_0001.json").exists())
            self.assertFalse((run_path / "obs_0001.png").exists())
            self.assertTrue((run_path / "obs_0003.json").exists())
            self.assertTrue(events_path.exists())

            deleted_events = [
                event for event in _read_jsonl(events_path) if event["type"] == "snapshot.deleted"
            ]

        self.assertGreaterEqual(len(deleted_events), 1)
        self.assertEqual(deleted_events[0]["reason"], "max_run_size_mb")

    def test_low_free_disk_raises_clear_error(self) -> None:
        disk_usage = namedtuple("usage", ["total", "used", "free"])

        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(ResourceGuardError) as context:
                ensure_min_free_disk(
                    temp_dir,
                    ResourceLimits(
                        max_observations_per_run=100,
                        max_run_size_mb=300,
                        min_free_disk_mb=1024,
                    ),
                    disk_usage=lambda _: disk_usage(
                        total=10 * BYTES_PER_MB,
                        used=9 * BYTES_PER_MB,
                        free=128 * BYTES_PER_MB,
                    ),
                )

        payload = context.exception.to_payload()
        self.assertEqual(payload["error"], "Insufficient local storage for observation.")
        self.assertEqual(payload["error_type"], "resource_guard")
        self.assertEqual(payload["min_free_disk_mb"], 1024)


def _write_snapshot_pair(
    run_path: Path,
    number: int,
    screenshot_size: int = 1,
) -> None:
    observation_id = f"obs_{number:04d}"
    (run_path / f"{observation_id}.json").write_text(
        json.dumps({"observation_id": observation_id}) + "\n",
        encoding="utf-8",
    )
    (run_path / f"{observation_id}.png").write_bytes(b"x" * screenshot_size)


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


if __name__ == "__main__":
    unittest.main()
