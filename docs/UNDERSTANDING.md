# Understanding v0

Understanding v0 is a read-only layer that converts an Observation snapshot into
a simple UI state snapshot.

It does not use OCR, AI vision, planning, safety decisions, actuation,
verification, or mouse/keyboard control. It only uses metadata already present in
the Observation JSON.

## Input

Understanding v0 receives the Observation JSON returned by `observe()`:

```json
{
  "observation_id": "obs_0001",
  "timestamp": "2026-05-28T12:00:00Z",
  "screen": {
    "width": 1920,
    "height": 1080,
    "screenshot_path": "runs/run_001/obs_0001.png"
  },
  "cursor": {
    "x": 800,
    "y": 420
  },
  "active_window": {
    "title": "Example - Google Chrome",
    "app_name": "chrome.exe"
  }
}
```

## Output

```json
{
  "ui_state_id": "state_0001",
  "source_observation_id": "obs_0001",
  "app_guess": "Chrome",
  "state_guess": "browser_window",
  "visible_elements": [],
  "summary": "The active window appears to be Chrome. No UI elements are recognized yet.",
  "confidence": 0.25
}
```

## Behavior

The first implementation is intentionally conservative:

- `app_guess` comes from deterministic matching against `active_window.app_name`
  and `active_window.title`.
- `state_guess` is a broad window category such as `browser_window`,
  `messaging_window`, `text_editor_window`, or `application_window`.
- `visible_elements` remains `[]` unless a future deterministic detector exists.
- `confidence` is low because no screenshot interpretation is performed.

## HTTP Endpoint

Run the local server:

```powershell
$env:PYTHONPATH = "src"
python -m lain_desk_agent.main
```

Then call:

```text
GET http://127.0.0.1:8000/understanding
```

The endpoint first calls `observe()`, then converts that observation into a UI
state with `understand()`, and returns the UI state JSON.
