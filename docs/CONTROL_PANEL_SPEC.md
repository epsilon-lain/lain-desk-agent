# Agent Control Panel spec

The first real product surface of `lain-desk-agent` is the Agent Control Panel.

It is a local UI for supervised desktop automation. The user gives a task on the left; the right side shows what the agent currently understands and what it wants to do next.

## Goal

Build a local, visible, inspectable control panel before enabling any real desktop control.

The control panel must make the agent's internal state visible enough that the user can answer three questions:

1. What does the agent think is happening now?
2. What is the agent planning to do next?
3. Is it safe to approve that action?

## Layout

### Left panel: user task input

The left panel is for the user's instruction and session controls.

Required elements:

- Task input box.
- Submit task button.
- Current session status: `idle`, `running`, or `stopped`.
- Stop button that is always visible during an active session.

Example task:

```text
Open the browser and search for Framework Laptop.
```

### Right panel: agent understanding

The right panel displays the agent's current interpretation of the desktop state.

Required elements:

- Current screen screenshot.
- App/page guess, such as `Chrome / GitHub page` or `Windows desktop`.
- Recognized UI elements:
  - buttons
  - input boxes
  - menus
  - links
  - dialogs
- Proposed next action.
- Reason for the proposed action.
- Risk level.
- Approve button.
- Reject button.
- Stop button.

## Agent state model

The UI should be driven by an explicit state object instead of scattered frontend variables.

```json
{
  "session_status": "idle",
  "task": "",
  "screen": {
    "screenshot_url": null,
    "app_guess": null,
    "page_guess": null
  },
  "recognized_elements": [],
  "next_action": null,
  "risk_level": "none",
  "reason": null,
  "approval_required": false
}
```

## Recognized UI element shape

Each recognized UI element should have a simple inspectable shape.

```json
{
  "id": "element_1",
  "type": "button",
  "label": "Search",
  "bbox": {
    "x": 120,
    "y": 240,
    "width": 80,
    "height": 32
  },
  "confidence": 0.82
}
```

For the first UI-only version, these elements may be mocked. Real screen recognition comes later.

## Next action shape

The proposed next action should also be explicit.

```json
{
  "type": "click",
  "target_element_id": "element_1",
  "x": 160,
  "y": 256,
  "text": null
}
```

The first version should show this proposal but must not execute it.

## Risk levels

- `none`: no action proposed.
- `low`: read-only observation or harmless focus movement.
- `medium`: typing, clicking, opening a page, or changing local UI state.
- `high`: sending messages, submitting forms, deleting files, changing settings, installing software.
- `blocked`: password/captcha bypass, payment confirmation, anti-cheat evasion, stealth control, or privilege escalation.

## First implementation milestone

The first implementation should be a mocked control panel.

It should show:

- A two-column local page.
- A task input on the left.
- A screenshot placeholder on the right.
- Mock app/page guess.
- Mock recognized buttons/input boxes.
- Mock next action.
- Risk badge.
- Approve / Reject / Stop buttons.

No real screenshot capture, no real mouse movement, and no real keyboard input should be implemented in this milestone.

## Acceptance checklist

- [ ] The backend serves the local control panel.
- [ ] The page has a clear left task panel and right understanding panel.
- [ ] The UI can display a task submitted by the user.
- [ ] The UI can display current session state.
- [ ] The UI can display mocked screen understanding.
- [ ] The UI can display a proposed next action and reason.
- [ ] The UI can display risk level.
- [ ] Approve, Reject, and Stop buttons exist.
- [ ] Approve does not perform real desktop control yet.
- [ ] Stop is visible and easy to find.
