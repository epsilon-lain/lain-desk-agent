# Roadmap

This roadmap keeps the project small and testable. Each stage should work before the next stage starts.

## Stage 0: Repository foundation

- [x] README with project goal.
- [x] Python project config.
- [x] Minimal FastAPI backend.
- [x] Safety model.

## Stage 1: Local control panel

Goal: a tiny local web page where the user can start/stop a supervised session.

Tasks:

- Add a simple frontend page served by the backend.
- Show current session state.
- Add Start and Stop buttons.
- Show that real input control is disabled.

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
