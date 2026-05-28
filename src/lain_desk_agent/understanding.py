"""Understanding v1.0: convert an observation into a simple read-only UI state."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from shutil import which
from typing import Any


DEFAULT_WINDOWS_TESSERACT = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")


@dataclass(frozen=True)
class UIState:
    ui_state_id: str
    source_observation_id: str
    app_guess: str | None
    state_guess: str
    visible_text: list[str] = field(default_factory=list)
    visible_elements: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def understand(observation: dict[str, Any]) -> dict[str, Any]:
    """Create a conservative UI state from an Observation snapshot."""

    observation_id = str(observation.get("observation_id") or "obs_0001")
    active_window = observation.get("active_window") or {}
    screen = observation.get("screen") or {}
    title = active_window.get("title")
    app_name = active_window.get("app_name")
    screenshot_path = screen.get("screenshot_path")

    app_guess = _guess_app(app_name, title)
    state_guess = _guess_state(app_guess, app_name, title)
    visible_text = _extract_visible_text(screenshot_path)
    confidence = _confidence(app_guess, visible_text)
    summary = _build_summary(app_guess, visible_text)

    ui_state = UIState(
        ui_state_id=_state_id_from_observation_id(observation_id),
        source_observation_id=observation_id,
        app_guess=app_guess,
        state_guess=state_guess,
        visible_text=visible_text,
        visible_elements=[],
        summary=summary,
        confidence=confidence,
    )

    return ui_state.to_dict()


def _state_id_from_observation_id(observation_id: str) -> str:
    if observation_id.startswith("obs_"):
        return f"state_{observation_id.removeprefix('obs_')}"

    return "state_0001"


def _guess_app(app_name: str | None, title: str | None) -> str | None:
    haystack = " ".join(value for value in [app_name, title] if value).lower()

    if not haystack:
        return None

    app_rules = [
        ("chrome", "Chrome"),
        ("msedge", "Edge"),
        ("edge", "Edge"),
        ("firefox", "Firefox"),
        ("wechat", "WeChat"),
        ("weixin", "WeChat"),
        ("notepad", "Notepad"),
        ("code", "VS Code"),
        ("powershell", "PowerShell"),
        ("cmd", "Command Prompt"),
        ("explorer", "File Explorer"),
    ]

    for token, app_guess in app_rules:
        if token in haystack:
            return app_guess

    if app_name:
        return Path(app_name).stem

    return None


def _guess_state(app_guess: str | None, app_name: str | None, title: str | None) -> str:
    haystack = " ".join(value for value in [app_guess, app_name, title] if value).lower()

    if not haystack:
        return "unknown"

    if any(token in haystack for token in ["chrome", "edge", "firefox", "browser"]):
        return "browser_window"

    if "wechat" in haystack or "weixin" in haystack:
        return "messaging_window"

    if "notepad" in haystack:
        return "text_editor_window"

    if "code" in haystack:
        return "code_editor_window"

    if "powershell" in haystack or "command prompt" in haystack or "cmd" in haystack:
        return "terminal_window"

    if "explorer" in haystack:
        return "file_manager_window"

    return "application_window"


def _extract_visible_text(screenshot_path: str | None) -> list[str]:
    if not screenshot_path:
        return []

    try:
        from PIL import Image
        import pytesseract
    except Exception:
        return []

    if not _configure_tesseract(pytesseract):
        return []

    try:
        image_path = Path(screenshot_path)
        if not image_path.exists():
            return []

        raw_text = pytesseract.image_to_string(Image.open(image_path))
    except Exception:
        return []

    lines = []
    for line in raw_text.splitlines():
        normalized = " ".join(line.split())
        if normalized:
            lines.append(normalized)

    return lines


def _configure_tesseract(pytesseract: Any) -> bool:
    if which("tesseract"):
        return True

    if DEFAULT_WINDOWS_TESSERACT.exists():
        pytesseract.pytesseract.tesseract_cmd = str(DEFAULT_WINDOWS_TESSERACT)
        return True

    return False


def _confidence(app_guess: str | None, visible_text: list[str]) -> float:
    if app_guess and visible_text:
        return 0.35

    if app_guess:
        return 0.25

    if visible_text:
        return 0.2

    return 0.1


def _build_summary(app_guess: str | None, visible_text: list[str]) -> str:
    if app_guess:
        text_summary = (
            f"OCR detected {len(visible_text)} text line(s)."
            if visible_text
            else "No visible text was detected by OCR."
        )
        return (
            f"The active window appears to be {app_guess}. "
            f"{text_summary} No UI elements are recognized yet."
        )

    if visible_text:
        return (
            f"The active window is unknown. OCR detected {len(visible_text)} text line(s). "
            "No UI elements are recognized yet."
        )

    return (
        "The active window is unknown. No visible text was detected by OCR. "
        "No UI elements are recognized yet."
    )
