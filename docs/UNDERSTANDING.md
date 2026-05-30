# Understanding v1.2

Understanding v1.2 is a read-only layer that converts an Observation snapshot
into a simple UI state snapshot.

OCR belongs in Understanding, not Observation. Observation captures raw desktop
state and saves the screenshot path. Understanding may read that screenshot and
extract `visible_text` from it.

This layer does not use AI vision, planning, safety decisions, actuation,
verification, or mouse/keyboard control.

## Input

Understanding v1.2 receives the Observation JSON returned by `observe()`:

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
  "visible_text_boxes": [
    {
      "id": "ocr_0001",
      "source": "ocr",
      "text": "Example",
      "bbox": {
        "x": 120,
        "y": 240,
        "width": 80,
        "height": 24
      },
      "confidence": 0.86
    }
  ],
  "visible_elements": [
    {
      "id": "element_0001",
      "source": "ocr",
      "type": "text",
      "kind": "text",
      "label": "Example",
      "text": "Example",
      "bbox": {
        "x": 120,
        "y": 240,
        "width": 80,
        "height": 24
      },
      "confidence": 0.86,
      "source_ref": "ocr_0001",
      "risk_hint": "none"
    }
  ],
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
- `visible_text_boxes` comes from OCR word-level data and includes text,
  bounding box, and normalized confidence.
- `visible_elements` maps OCR boxes into text-only elements with
  `type: "text"` and `kind: "text"`.
- High-risk labels such as `Send` or `Delete` receive a compact
  `risk_hint: "high"` marker. This is a hint for downstream safety display and
  validation only; it does not enable execution.
- `confidence` remains low because OCR text is not the same as UI element
  detection.

## Visible Data Fields

- `visible_text` is a plain string list from OCR. It is useful for summaries and
  quick display.
- `visible_text_boxes` is OCR word-level data with text, bbox, and OCR
  confidence.
- `visible_elements` is the unified UI-state element list. In v1.2, OCR boxes
  are mapped into this list only as text elements.

OCR text elements use this shape:

```json
{
  "id": "element_0001",
  "source": "ocr",
  "type": "text",
  "kind": "text",
  "label": "Search",
  "text": "Search",
  "bbox": {
    "x": 120,
    "y": 240,
    "width": 80,
    "height": 24
  },
  "confidence": 0.86,
  "source_ref": "ocr_0001",
  "risk_hint": "none"
}
```

OCR elements are not buttons, inputs, menus, links, or clickable controls.
They are read-only text grounding. `risk_hint` marks potentially sensitive
labels but is not a permission grant.

## OCR Behavior

OCR is optional and best-effort. If OCR is unavailable, not installed, cannot
read the screenshot, or fails for any reason, Understanding returns:

```json
{
  "visible_text": [],
  "visible_text_boxes": []
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

If Tesseract is not on `PATH`, Understanding v1.2 also tries the default Windows
path:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

Verify that Python can call Tesseract:

```powershell
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

Understanding v1.2 does not infer buttons, input boxes, menus, links, or
clickable elements from OCR text boxes. OCR boxes are mapped into
`visible_elements` only as `type: "text"`.

Future structured sources may also feed `visible_elements`, but are not
implemented yet:

- Browser DOM / HTML through explicit browser integration.
- Windows accessibility tree.
- Vision model output.

These future sources should be fused conservatively into `visible_elements`
without bypassing Planner, Safety, Actuation, or Verification.

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
