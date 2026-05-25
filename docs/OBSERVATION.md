# Observation v0

Observation v0 captures the current desktop state and saves it as a reusable
snapshot. It does not understand the screen, plan actions, control input, run
OCR, or use AI vision.

## Scope

Observation v0 records five things:

- Observation data structure.
- Screenshot capture.
- Cursor and screen info.
- Active window info.
- Audit log.

## Output Format

```json
{
  "observation_id": "obs_0001",
  "timestamp": "2026-05-25T12:00:00Z",
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
    "title": "Example",
    "app_name": "example.exe"
  }
}
```

If active window details are unavailable, `title` and `app_name` are returned as
`null`.

## Files Written

Each observation is written under:

```text
runs/run_001/
```

For `obs_0001`, the files are:

```text
runs/run_001/obs_0001.png
runs/run_001/obs_0001.json
runs/run_001/events.jsonl
```

The audit log receives one JSONL event per observation:

```json
{"type":"observation.created","timestamp":"...","observation_id":"obs_0001","observation_path":"runs/run_001/obs_0001.json","screenshot_path":"runs/run_001/obs_0001.png"}
```

## HTTP Endpoint

Install the runtime dependency first:

```powershell
python -m pip install -r requirements.txt
```

Run the local server with:

```powershell
$env:PYTHONPATH = "src"
python -m lain_desk_agent.main
```

Then call:

```text
GET http://127.0.0.1:8000/observation
```

The endpoint calls `observe()`, saves the screenshot and JSON snapshot, appends
to the audit log, and returns the observation JSON.

## Safety Boundary

Observation v0 uses `pyautogui` only for:

- `size()`
- `position()`
- `screenshot()`

It does not call mouse or keyboard input-control functions such as `click()`,
`moveTo()`, `write()`, `press()`, or `hotkey()`.
