# Understanding v1.0

Understanding v1.0 is a read-only layer that converts an Observation snapshot
into a simple UI state snapshot.

OCR belongs in Understanding, not Observation. Observation captures raw desktop
state and saves the screenshot path. Understanding may read that screenshot and
extract `visible_text` from it.

This layer does not use AI vision, planning, safety decisions, actuation,
verification, or mouse/keyboard control.

## Input

Understanding v1.0 receives the Observation JSON returned by `observe()`:

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
  "visible_text": ["Example text"],
  "visible_elements": [],
  "summary": "The active window appears to be Chrome. OCR detected 1 text line(s). No UI elements are recognized yet.",
  "confidence": 0.35
}
```

## Behavior

The implementation is intentionally conservative:

- `app_guess` comes from deterministic matching against `active_window.app_name`
  and `active_window.title`.
- `state_guess` is a broad window category such as `browser_window`,
  `messaging_window`, `text_editor_window`, or `application_window`.
- `visible_text` comes from OCR against `observation.screen.screenshot_path`.
- `visible_elements` remains `[]` unless a future deterministic detector exists.
- `confidence` remains low because OCR text is not the same as UI element
  detection.

## OCR Behavior

OCR is optional and best-effort. If OCR is unavailable, not installed, cannot
read the screenshot, or fails for any reason, Understanding returns:

```json
{
  "visible_text": []
}
```

The request must not crash because OCR is missing.

The implementation uses `pytesseract` when it is available. Enabling OCR on a
developer machine requires both the Python package and the local Tesseract OCR
engine. Without those, Understanding still works and returns `visible_text: []`.

### Windows install steps

Install the Python packages:

```powershell
python -m pip install -r requirements.txt
```

Install Tesseract OCR for Windows. The recommended Windows installer is the
UB Mannheim build:

```text
https://ub-mannheim.github.io/Tesseract_Dokumentation/Tesseract_Doku_Windows.html
```

Install it to the default location:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

Adding Tesseract to `PATH` is recommended. After opening a new PowerShell,
verify:

```powershell
tesseract --version
```

If Tesseract is not on `PATH`, Understanding v1.0 also tries the default Windows
path:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

Verify that Python can call Tesseract:

```powershell
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

Understanding v1.0 does not infer buttons, input boxes, menus, or clickable
elements from OCR text. `visible_elements` stays `[]`.

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
