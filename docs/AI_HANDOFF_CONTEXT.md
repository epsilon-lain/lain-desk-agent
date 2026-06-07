# AI Handoff Context

This document is optimized for future AI assistants and Codex sessions. Read it
before changing Phase 8, Phase 9, safety, cockpit replay, or Phase 10 readiness
work.

## Repository Purpose

`lain-desk-agent` is a supervised local desktop-agent cockpit. It observes,
understands, proposes, previews, evaluates, exports, imports, validates, and
replays deterministic dry-run traces.

It is not an autonomous desktop controller.

## Current Architecture In Brief

```text
observe -> understand -> propose -> safety gate -> action contract
-> click readiness diagnostics -> capability/profile/policy summaries
-> wait-only execution path
```

Sandbox and Phase 9 paths are separate read-only debug paths:

```text
Phase 8/9 fixtures -> gate validation -> dry-run report
-> cockpit display -> export bundle -> local import -> validation -> replay
```

Proposal is not execution. Readiness is not permission.
Cockpit display is not authorization.

## Current Phase

The project is post-Phase 9.x dry-run sandbox hardening and entering Phase 10
readiness / release-candidate preparation.

Phase 10 real actions are not implemented yet.

## Hard Safety Boundary

- dry-run, read-only, debug-only for sandbox and replay paths
- no real desktop actions
- no real click/type/hotkey/scroll/switch_app
- no sandbox or replay `/execute` call
- no execute button, real-action approval button, sandbox action trigger, or
  real-action toggle
- no real-action toggle
- no `pyautogui`, `pynput`, `keyboard`, `mouse`, `win32api`, `ctypes`
  `SendInput` / `mouse_event`, `xdotool`, AppleScript UI scripting, or other
  real desktop control API
- no permission broadening in Execution Policy, Permission Profile, Capability
  Registry, or permission matrix

## Important Files

- `README.md`: quick project entry point.
- `docs/PROJECT_HEALTH_SNAPSHOT.md`: current health and release-prep snapshot.
- `docs/PHASE_10_READINESS_CHECKLIST.md`: gate before future Phase 10 work.
- `docs/SAFETY_INVARIANTS.md`: invariants that must not regress.
- `docs/PHASE_7_SANDBOX_ACTION_DESIGN.md`: original sandbox gate design.
- `docs/PHASE_9_MINIMAL_SANDBOX_EXPERIMENT_DESIGN.md`: Phase 9 dry-run design.
- `src/lain_desk_agent/sandbox_experiment.py`: Phase 8 dry-run gate.
- `src/lain_desk_agent/sandbox_evaluation.py`: deterministic Phase 8 report.
- `src/lain_desk_agent/phase9_experiment.py`: Phase 9 dry-run harness,
  export/import/replay helpers, and validation.
- `src/lain_desk_agent/main.py`: HTTP endpoints; sandbox/Phase 9 endpoints are
  deterministic read-only report endpoints.
- `ui/app.js`, `ui/index.html`, `ui/styles.css`: cockpit UI and local-only
  replay/debug controls.
- `scripts/safety_scan.py`: runtime desktop actuation scan.
- `scripts/verify.ps1`: standard verification chain.
- `scripts/project_status.ps1`: read-only project health command helper.

## Important Test Commands

```powershell
.\scripts\verify.ps1
python scripts\safety_scan.py
git diff --check
node --check ui/app.js
python -m unittest discover -s tests
```

## What Not To Touch

Do not change these to allow real actions unless a new user request explicitly
satisfies `docs/PHASE_10_READINESS_CHECKLIST.md`:

- Execution Policy
- Permission Profile
- Capability Registry
- permission matrix
- safety_scan.py protections
- Phase 7 gate
- Phase 9 gate
- replay validation
- audit constraints

## Current Dry-run Pipeline

- Phase 8 validates sandbox gate inputs and returns dry-run, blocked, or
  real-action-skipped results.
- Phase 8.1 evaluates deterministic scenarios.
- Phase 8.2 through 8.5 expose and polish cockpit trace display.
- Phase 9.1 runs a deterministic dry-run harness with mock approval, mock
  emergency stop, mock verification, and mock rollback.
- Phase 9.2 through 9.8 expose, export, import, replay, validate, and polish
  the Phase 9 dry-run report.

No Phase 8 or Phase 9 path performs real action.

## Phase 9 Export / Import / Replay Pipeline

```text
deterministic Phase 9 report
-> JSON export report
-> AI-readable summary
-> reproducibility bundle
-> pasted local import
-> deterministic validation
-> read-only replay report
-> cockpit display and copy helpers
```

Imported bundles are untrusted input.
Validation errors do not mutate runtime state.
Replay is read-only.

## Known Safe Next Steps

- Add docs and tests for release preparation.
- Improve AI handoff wording.
- Add read-only validation coverage.
- Add cockpit readability polish that only changes local display.
- Add deterministic fixtures that remain dry-run and do not observe live
  desktop state.

## Known Dangerous Next Steps

- Enabling click/type/hotkey/scroll/switch_app.
- Adding a real desktop control dependency.
- Adding a sandbox action trigger in the cockpit.
- Making imported bundles executable.
- Treating readiness as permission.
- Treating proposal or validation as execution.
- Changing Capability Registry, Permission Profile, or Execution Policy to
  allow broad desktop control.

## Exact Instruction For Future AI

Do not enable real actions unless the Phase 10 readiness checklist is
explicitly satisfied by a new user request and all required gates, approvals,
tests, documentation, emergency stop, rollback, audit, and verification
requirements are implemented and reviewed.

## Copyable Mini-prompt

```text
You are working on lain-desk-agent, a supervised local desktop-agent cockpit.
The current project is dry-run/read-only/debug-only for sandbox and replay
paths. Real click/type/hotkey/scroll/switch_app are disabled. Do not add real
desktop APIs, /execute paths from sandbox/replay UI, approval buttons for real
action, real-action toggles, or permission changes. Read
docs/PROJECT_HEALTH_SNAPSHOT.md, docs/SAFETY_INVARIANTS.md, and
docs/PHASE_10_READINESS_CHECKLIST.md before editing. Preserve proposal is not
execution, readiness is not permission, cockpit display is not authorization,
and imported bundles are untrusted input. Run verify.ps1, safety_scan.py,
git diff --check, and node --check ui/app.js.
```
