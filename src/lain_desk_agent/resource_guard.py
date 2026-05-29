"""Runtime storage checks and snapshot retention for local runs."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


BYTES_PER_MB = 1024 * 1024
SNAPSHOT_RE = re.compile(r"^obs_(\d{4})$")

max_observations_per_run = 100
max_run_size_mb = 300
min_free_disk_mb = 1024


@dataclass(frozen=True)
class ResourceLimits:
    max_observations_per_run: int = max_observations_per_run
    max_run_size_mb: float = max_run_size_mb
    min_free_disk_mb: float = min_free_disk_mb


@dataclass(frozen=True)
class SnapshotPair:
    observation_id: str
    number: int
    json_path: Path
    png_path: Path


DEFAULT_LIMITS = ResourceLimits()


class ResourceGuardError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        available_free_disk_mb: float,
        min_free_disk_mb: float,
    ) -> None:
        super().__init__(message)
        self.available_free_disk_mb = available_free_disk_mb
        self.min_free_disk_mb = min_free_disk_mb

    def to_payload(self) -> dict[str, Any]:
        return {
            "error": str(self),
            "error_type": "resource_guard",
            "available_free_disk_mb": round(self.available_free_disk_mb, 2),
            "min_free_disk_mb": self.min_free_disk_mb,
        }


def ensure_min_free_disk(
    run_dir: str | Path,
    limits: ResourceLimits = DEFAULT_LIMITS,
    disk_usage: Callable[[Path], Any] = shutil.disk_usage,
) -> None:
    """Raise before taking a screenshot if local free disk is too low."""

    usage = disk_usage(Path(run_dir))
    available_free_disk_mb = usage.free / BYTES_PER_MB

    if available_free_disk_mb < limits.min_free_disk_mb:
        raise ResourceGuardError(
            "Insufficient local storage for observation.",
            available_free_disk_mb=available_free_disk_mb,
            min_free_disk_mb=limits.min_free_disk_mb,
        )


def cleanup_run_snapshots(
    run_dir: str | Path,
    limits: ResourceLimits = DEFAULT_LIMITS,
) -> list[dict[str, Any]]:
    """Delete oldest observation snapshot pairs until current run limits fit."""

    run_path = Path(run_dir)
    snapshots = _list_snapshot_pairs(run_path)
    deleted_events: list[dict[str, Any]] = []

    while snapshots:
        too_many = len(snapshots) > limits.max_observations_per_run
        too_large = _run_size_bytes(run_path) > _mb_to_bytes(limits.max_run_size_mb)

        if not too_many and not too_large:
            break

        # Keep the newest snapshot available for the just-created UI state.
        if len(snapshots) <= 1:
            break

        reason = "max_observations_per_run" if too_many else "max_run_size_mb"
        snapshot = snapshots.pop(0)
        deleted_event = _delete_snapshot_pair(snapshot, reason)

        if deleted_event is not None:
            _append_event(run_path / "events.jsonl", deleted_event)
            deleted_events.append(deleted_event)

    return deleted_events


def _list_snapshot_pairs(run_path: Path) -> list[SnapshotPair]:
    json_paths = {path.stem: path for path in run_path.glob("obs_*.json")}
    png_paths = {path.stem: path for path in run_path.glob("obs_*.png")}
    snapshots: list[SnapshotPair] = []

    for stem in sorted(json_paths.keys() & png_paths.keys()):
        match = SNAPSHOT_RE.fullmatch(stem)
        if not match:
            continue

        snapshots.append(
            SnapshotPair(
                observation_id=stem,
                number=int(match.group(1)),
                json_path=json_paths[stem],
                png_path=png_paths[stem],
            )
        )

    return sorted(snapshots, key=lambda snapshot: snapshot.number)


def _delete_snapshot_pair(snapshot: SnapshotPair, reason: str) -> dict[str, Any] | None:
    deleted_paths: list[str] = []

    try:
        for path in (snapshot.json_path, snapshot.png_path):
            if path.exists():
                path.unlink()
                deleted_paths.append(_relative_posix(path))
    except OSError:
        return None

    if not deleted_paths:
        return None

    return {
        "type": "snapshot.deleted",
        "timestamp": _utc_timestamp(),
        "observation_id": snapshot.observation_id,
        "reason": reason,
        "snapshot_path": _relative_posix(snapshot.json_path),
        "screenshot_path": _relative_posix(snapshot.png_path),
        "deleted_paths": deleted_paths,
    }


def _run_size_bytes(run_path: Path) -> int:
    total = 0

    for path in run_path.glob("*"):
        if path.is_file():
            total += path.stat().st_size

    return total


def _mb_to_bytes(value: float) -> int:
    return int(value * BYTES_PER_MB)


def _append_event(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _relative_posix(path: Path) -> str:
    try:
        return path.relative_to(Path.cwd()).as_posix()
    except ValueError:
        return path.as_posix()


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
