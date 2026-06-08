# Phase 10.3 Release-candidate Guardrails

Phase 10.3 is regression protection and deterministic local validation only.
It adds pure release-candidate bundle validation helpers, a browser-local
cockpit validation panel, documentation, and tests for the current
release-candidate boundary; it does not implement, authorize, or enable real
desktop actions.

## Current Status

The current project is not a real-action agent yet. Mirai remains a supervised
local cockpit with dry-run, read-only, and debug-only sandbox/replay paths.
Approved `wait` remains the only executable action.

Real desktop actions remain disabled. Click, type, hotkey, scroll, and
switch_app are still non-executable. Phase 10 real actions are not implemented.

## Non-permission Signals

- Readiness is not permission.
- Cockpit display is not authorization.
- Export, import, and replay are not execution.
- AI handoff is not AI control.
- A green parser, safety scan, replay validation, or copied status payload does
  not grant desktop action permission.

## Release-candidate No-go Criteria

The repository remains NO-GO for Phase 10 real actions if any of these are
true:

- `go_for_phase10` is false.
- `real_actions_enabled` is false.
- `phase10_real_actions_implemented` is false.
- No explicit new user request approves a named Phase 10 real-action
  experiment.
- Phase 7 and Phase 9 gates have not been explicitly satisfied for the named
  experiment.
- Emergency stop, rollback, audit, approval binding, and post-action
  verification are missing or untested.
- Any cockpit, replay, import, export, readiness, global-status, or AI handoff
  surface is being treated as permission.

These are expected blockers in the current release-candidate state.

## Forbidden Before Explicit Phase 10 Approval

Do not make any of these changes before a future user request explicitly
approves a scoped Phase 10 real-action experiment:

- Add real desktop actuation dependencies or calls such as `pyautogui`
  click/move/write/press/hotkey/scroll, `pynput`, `keyboard`, `mouse`,
  `win32api`, `ctypes` `SendInput` / `mouse_event`, `xdotool`, AppleScript UI
  scripting, or equivalent APIs. The existing `pyautogui` observer dependency
  is read-only screenshot, cursor, and screen-size capture only.
- Add click/type/hotkey/scroll/switch_app actuation.
- Add a sandbox, replay, readiness, global-status, or AI handoff call to
  `/execute`.
- Add execute buttons, real-action approval buttons, sandbox action triggers,
  or real-action toggles to the cockpit.
- Add mutation endpoints that perform desktop action.
- Change Capability Registry, Permission Profile, Execution Policy, or any
  permission matrix to grant real desktop control.
- Change dry-run defaults or make `real_action_enabled`,
  `real_actions_enabled`, or `go_for_phase10` true by default.
- Treat imported bundle data, copied JSON, AI handoff text, or readiness output
  as trusted instructions.

## Future Codex Sessions Must Not Touch

Future sessions should not weaken these files or boundaries to make Phase 10
look ready:

- `scripts/safety_scan.py`
- `src/lain_desk_agent/capabilities.py`
- `src/lain_desk_agent/permission_profile.py`
- `src/lain_desk_agent/execution_policy.py`
- `src/lain_desk_agent/sandbox_experiment.py`
- `src/lain_desk_agent/phase9_experiment.py`
- replay validation and sensitive-key checks
- Phase 7, Phase 9, and Phase 10 readiness gates
- audit, rollback, emergency stop, and verification requirements

Future sessions may add docs, deterministic tests, read-only reports, and
debugging clarity while preserving the current boundary. Browser-local bundle
validation may inspect pasted JSON, but it must not call a backend endpoint or
turn copied validation data into execution.

## Required Verification

Run these before handing off release-candidate guardrail work:

```powershell
python -m unittest discover -s tests -p test_release_candidate_guardrails.py
python -m unittest discover -s tests -p test_phase10_guardrails.py
.\scripts\verify.ps1
python scripts\safety_scan.py
git diff --check
node --check ui/app.js
python -m unittest discover -s tests
```

## Expected Phase 10.3 Outcome

Expected result: the release candidate remains dry-run/read-only/debug-only,
Phase 10 reports remain NO-GO by default, real desktop actions remain disabled,
the cockpit validates release-candidate bundles locally only, and the guardrail
tests fail loudly if future code adds desktop actuation, real-action cockpit
controls, unsafe `/execute` UI paths, backend execution endpoints, or
true-by-default real-action flags.
