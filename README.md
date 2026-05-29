# lain-desk-agent

A local desktop agent prototype for building a guarded desktop interaction
loop. The current version can observe, understand, propose, audit, and run a
safe wait-only self-test. It does not provide real mouse or keyboard desktop
control.

## Current route

This repository is for **Lain Mouse Agent**: a general desktop interaction
prototype with a visible brake. The current priority is not autonomy. It is
making the local loop observable, explainable, and conservative before adding
real execution.

Current route:

```text
Read-only perception loop
-> target proposal
-> safety decision
-> wait-only actuation
-> verification
-> expand action types later
```

The purpose is to validate a general interaction shell, not to build an
app-specific script.

## Current status: v0.3 guarded wait-only cockpit

The current cockpit supports:

- observe / understand / propose
- Safety Gate decisions
- preview-only Action Contracts
- Capability Registry
- Permission Profile
- Click Readiness Policy
- wait-only Actuation
- wait-only Verification
- Runtime Status
- Event Viewer
- Resource Guard

Important boundary: there is still no real mouse or keyboard control. Click,
type, hotkey, scroll, and app-switch actions are disabled. Preview-only
contracts are never executable, and click readiness currently blocks real click
execution.

## How to run

From PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m lain_desk_agent.main
```

Then open:

```text
http://127.0.0.1:8000/
```

## Terminology

- **Lain**: the human operator/user.
- **Agent**: the local desktop program being supervised by Lain.
- **Console**: the local UI where Lain gives tasks, reviews the agent's understanding, approves/rejects actions, and stops runs.

## Safety boundaries

- Operates only within the current user's permissions.
- Does not bypass security boundaries, captchas, passwords, payment confirmations, anti-cheat, or privacy protections.
- Must support emergency stop (preferred: `ESC`).
- Must log every action.
- High-risk actions require explicit user confirmation.
- v0 is user-space only (no kernel drivers).
- v0.3 has no real mouse/keyboard desktop control; only wait is executable.

## Spec

See the detailed prototype scope, constraints, and implementation path:

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/agent-console-v0.md`](docs/agent-console-v0.md)
- [`docs/OBSERVATION.md`](docs/OBSERVATION.md)
- [`docs/UNDERSTANDING.md`](docs/UNDERSTANDING.md)
- [`docs/PLANNER.md`](docs/PLANNER.md)
- [`docs/SAFETY.md`](docs/SAFETY.md)
- [`docs/lain-mouse-agent-prototype-spec.md`](docs/lain-mouse-agent-prototype-spec.md)
- [`docs/lain-mouse-agent-implementation-roadmap.md`](docs/lain-mouse-agent-implementation-roadmap.md)

## UI prototype

The first static Agent Console prototype lives in [`ui/index.html`](ui/index.html).
It is intentionally dependency-free while the project validates the supervised
observe-plan-act interface.
