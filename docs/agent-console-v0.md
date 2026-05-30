# Agent Console v0

This document defines the first shared product step for `lain-desk-agent`.

In this project, **Lain is the human operator**. The program is the local desktop
agent being supervised by Lain.

The v0 console is not a full autonomous assistant. It is a small floating
control surface for a supervised observe-plan-act loop.

## 1) Core idea

The console should make the agent's current state visible before it acts.

```text
Lain gives a task
-> agent observes the screen
-> agent explains what it thinks is happening
-> agent proposes one small next action
-> Lain can approve, reject, or stop
-> agent executes only that small action
-> agent observes again
-> repeat
```

The important product promise is:

> The agent does not silently run ahead. Lain can see, interrupt, and correct the
> loop.

## 2) Layout

The first UI should be a compact floating window. It does not need to show the
current screenshot by default because Lain can see the real desktop and mouse
movement directly. Screenshot capture, OCR, and UI element detection can run in
the background.

```text
+------------------------------------------------+
| Mirai                                      -  x |
+------------------------------------------------+
| Agent: This page needs login.                  |
| Please complete it manually.                   |
|                                                |
|                    [ Done ]                    |
+------------------------------------------------+
| Now: waiting for you                           |
| > details                                      |
+------------------------------------------------+
| ! Emergency stop: ESC                          |
+------------------------------------------------+
```

Target size for the real desktop shell: roughly `360-460px` wide and `360-520px`
tall. The browser prototype may be larger while the visual design is being
reviewed.

### Title bar

The title bar shows the agent display name, such as `Mirai`. This is not the
project name. The display name should be user-configurable.

Required elements:

- Agent display name.
- Minimize control.
- Close control.

### Message area

The message area is where the agent explains what it needs from Lain.

Required elements:

- Speaker label, such as `Agent:`.
- Short agent message.
- One fixed primary action slot.

The primary action slot is stable. Its text may change by state:

- `Done`
- `Approve`
- `Reject`
- `Continue`
- `Retry`
- `Pause`

For the first UI pass, `Done` is acceptable.

### Status area

The status area shows what the agent is doing now.

Required elements:

- `Now:` status line.
- Collapsed `details` section.

Example statuses:

- `waiting for you`
- `observing screen`
- `planning next action`
- `moving mouse to search box`
- `typing text`
- `waiting for page load`
- `blocked: login required`
- `stopped`

The `details` section may expose debug context without making the main UI large:

- Current app/page guess.
- Current state.
- Last action.
- Next action.
- Risk reason.

### Emergency stop

The emergency stop must always be visible.

Required elements:

- Red danger treatment.
- Label: `Emergency stop: ESC`.
- Click/tap stop behavior.
- Keyboard `ESC` stop behavior.

## 3) UI state model

Every loop step should be representable by this compact UI state:

```json
{
  "agent_name": "Mirai",
  "message": {
    "speaker": "Agent",
    "body": "This page needs login. Please complete it manually."
  },
  "primary_action": {
    "label": "Done",
    "enabled": true
  },
  "status": "waiting for you",
  "details": {
    "current_app": "Browser",
    "state": "login required",
    "next_action": "wait_for_user",
    "risk": "protected login flow"
  },
  "emergency_stop": {
    "label": "Emergency stop: ESC",
    "enabled": true
  }
}
```

The backend may keep richer observation state, including screenshots and
recognized UI elements. The main window only needs to show the information Lain
needs to supervise the next step.

## 4) Run status values

The internal run loop should still track structured statuses:

- `idle`
- `observing`
- `planning`
  - `waiting_for_approval`
  - `acting`
  - `verifying`
- `stopped`
- `done`
- `error`

These statuses can be translated into short `Now:` messages for the floating UI.

## 5) Approval rules

The console should require explicit approval for risky actions.

### Low-risk actions

These may run without approval while the run is active:

- Move mouse.
- Click ordinary UI controls.
- Scroll.
- Wait.
- Use harmless keyboard shortcuts.
- Type into a local draft area.

### High-risk actions

These must pause and ask Lain first:

- Send a message.
- Submit a form.
- Delete files or content.
- Overwrite files.
- Make payments.
- Change account, privacy, security, or system settings.
- Enter passwords, tokens, payment details, or private credentials.
- Interact with captchas or security checks.

When approval is required, the console must show:

- The exact proposed action.
- The target.
- The reason.
- The risk category.
- What could go wrong.

The agent must not execute the action until Lain approves it.

## 6) Button behavior

### Approve

Allows the currently proposed action to run once.

`Approve` does not grant permission for the whole task. After the action runs,
the agent must observe again and produce a new proposed action.

### Reject

Blocks the current proposed action and asks the agent to replan.

The UI may optionally allow Lain to add a correction, such as:

```text
Don't click that button. Use the search field instead.
```

### Stop

Stops the current run as quickly as possible.

The stop behavior should also be available through a keyboard emergency stop,
preferred: `ESC`.

## 7) First non-AI prototype

The first console does not need a smart planner.

It can use mocked or manually entered understanding and actions while the shell
is being built. The point of the first version is to prove the product loop:

```text
agent message displayed
-> Now status displayed
-> primary action displayed
-> details optionally expanded
-> action accepted/rejected/stopped
-> log written
```

This lets the project validate the control surface before depending on OCR,
vision models, or LLM planning.

## 8) Definition of done for console v0

Console v0 is done when:

- The UI renders as a compact floating window.
- The agent display name is visible and can be renamed.
- The UI shows an agent message.
- The fixed primary action slot exists.
- The UI shows a short `Now:` status.
- A collapsed `details` section exists for debug context.
- `Emergency stop: ESC` is always visible.
- Pressing `ESC` updates the UI to stopped.
- High-risk actions cannot execute without approval.
- The run log records observations, proposals, approvals, rejections, actions,
  and stop events.
