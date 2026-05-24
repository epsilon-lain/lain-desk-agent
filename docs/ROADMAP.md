# Roadmap

This roadmap keeps the project small and testable. Each stage should work before the next stage starts.

## Stage 0: Repository foundation

- [x] README with project goal.
- [x] Python project config.
- [x] Minimal FastAPI backend.
- [x] Safety model.
- [x] Agent Control Panel spec.

## Stage 1: Agent Control Panel

Goal: build the first real local UI surface for supervised desktop automation.

The control panel has two main areas:

- Left: Lain enters the task.
- Right: the program shows its current understanding.

The right panel should show:

- current screen screenshot or placeholder
- app/page guess
- recognized buttons, input boxes, menus, links, and dialogs
- proposed next action
- reason for the proposed action
- risk level
- Approve / Reject / Stop controls

Tasks:

- Serve a local web UI from the backend.
- Create a two-column control panel layout.
- Add task input and submit button.
- Show current session state.
- Show mocked screen understanding first.
- Show mocked recognized UI elements first.
- Show mocked next action and reason first.
- Show risk level.
- Add Approve / Reject / Stop buttons.
- Keep real screenshot capture and real input control disabled in this stage.

See `docs/CONTROL_PANEL_SPEC.md`.

## Stage 2: Read-only screen observation

Goal: add screen snapshot capture without taking any actions.

Tasks:

- Add a screen capture interface.
- Add platform notes for Windows, macOS, and Linux.
- Add a preview endpoint.
- Make capture opt-in from the visible local UI.

## Stage 3: Action proposal only

Goal: let the agent describe intended actions without executing them.

Tasks:

- Define an action schema: move, click, type, hotkey, wait.
- Add risk levels to actions.
- Log proposed actions.
- Show proposed actions in the UI.

## Stage 4: Human-approved execution

Goal: allow selected actions only after explicit user approval.

Tasks:

- Add approval flow for medium-risk actions.
- Add stronger confirmation for high-risk actions.
- Add emergency stop before enabling execution.
- Add action execution logs.

## Stage 5: Tool and app integrations

Goal: prefer official APIs when available, and use UI control only as a fallback.

Tasks:

- Add tool adapters for safe APIs.
- Keep credentials outside the repository.
- Add per-tool permission summaries.
- Add tests for blocked actions.
