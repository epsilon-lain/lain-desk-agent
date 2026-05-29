"""Observation v0: capture the current desktop state without controlling input."""

from __future__ import annotations

import ctypes
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .resource_guard import cleanup_run_snapshots, ensure_min_free_disk


DEFAULT_RUN_DIR = Path("runs") / "run_001"


@dataclass(frozen=True)
class ScreenInfo:
    width: int
    height: int
    screenshot_path: str


@dataclass(frozen=True)
class CursorInfo:
    x: int
    y: int


@dataclass(frozen=True)
class ActiveWindowInfo:
    title: str | None
    app_name: str | None


@dataclass(frozen=True)
class Observation:
    observation_id: str
    timestamp: str
    screen: ScreenInfo
    cursor: CursorInfo
    active_window: ActiveWindowInfo

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def observe(run_dir: str | Path = DEFAULT_RUN_DIR) -> dict[str, Any]:
    """Capture one desktop observation and persist it under the run directory."""

    pyautogui = _load_pyautogui()
    run_path = Path(run_dir)
    run_path.mkdir(parents=True, exist_ok=True)
    ensure_min_free_disk(run_path)

    observation_id = _next_observation_id(run_path)
    timestamp = _utc_timestamp()
    screenshot_path = run_path / f"{observation_id}.png"
    snapshot_path = run_path / f"{observation_id}.json"

    screen_width, screen_height = pyautogui.size()
    cursor_x, cursor_y = pyautogui.position()
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)

    observation = Observation(
        observation_id=observation_id,
        timestamp=timestamp,
        screen=ScreenInfo(
            width=int(screen_width),
            height=int(screen_height),
            screenshot_path=_relative_posix(screenshot_path),
        ),
        cursor=CursorInfo(
            x=int(cursor_x),
            y=int(cursor_y),
        ),
        active_window=_get_active_window_info(),
    )
    observation_json = observation.to_dict()

    _write_json(snapshot_path, observation_json)
    _append_event(
        run_path / "events.jsonl",
        {
            "type": "observation.created",
            "timestamp": timestamp,
            "observation_id": observation_id,
            "observation_path": _relative_posix(snapshot_path),
            "screenshot_path": observation_json["screen"]["screenshot_path"],
        },
    )
    cleanup_run_snapshots(run_path)

    return observation_json


def _load_pyautogui() -> Any:
    try:
        import pyautogui
    except ImportError as exc:
        raise RuntimeError("pyautogui is required for Observation v0") from exc

    return pyautogui


def _next_observation_id(run_path: Path) -> str:
    max_number = 0

    for path in run_path.glob("obs_*.json"):
        try:
            number = int(path.stem.removeprefix("obs_"))
        except ValueError:
            continue

        max_number = max(max_number, number)

    return f"obs_{max_number + 1:04d}"


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _relative_posix(path: Path) -> str:
    try:
        return path.relative_to(Path.cwd()).as_posix()
    except ValueError:
        return path.as_posix()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _append_event(path: Path, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _get_active_window_info() -> ActiveWindowInfo:
    if os.name != "nt":
        return ActiveWindowInfo(title=None, app_name=None)

    try:
        return _get_active_window_info_windows()
    except Exception:
        return ActiveWindowInfo(title=None, app_name=None)


def _get_active_window_info_windows() -> ActiveWindowInfo:
    user32 = ctypes.windll.user32
    hwnd = user32.GetForegroundWindow()

    if not hwnd:
        return ActiveWindowInfo(title=None, app_name=None)

    title = _get_window_title(user32, hwnd)
    app_name = _get_window_app_name(user32, hwnd)

    return ActiveWindowInfo(title=title, app_name=app_name)


def _get_window_title(user32: Any, hwnd: int) -> str | None:
    length = user32.GetWindowTextLengthW(hwnd)

    if length <= 0:
        return None

    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value or None


def _get_window_app_name(user32: Any, hwnd: int) -> str | None:
    process_id = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))

    if not process_id.value:
        return None

    kernel32 = ctypes.windll.kernel32
    process_query_limited_information = 0x1000
    handle = kernel32.OpenProcess(process_query_limited_information, False, process_id.value)

    if not handle:
        return None

    try:
        buffer = ctypes.create_unicode_buffer(32768)
        size = ctypes.c_ulong(len(buffer))
        success = kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size))

        if not success:
            return None

        return Path(buffer.value).name or None
    finally:
        kernel32.CloseHandle(handle)
