# Safety Invariants

These invariants define the current dry-run, read-only, debug-only safety model.
They should be treated as regression guards for future Codex sessions and human
developers.

## Runtime And API Invariants

- No real desktop actions.
- No real desktop APIs may be imported or called in runtime code.
- No `pyautogui`, `pynput`, `keyboard`, `mouse`, `win32api`, `ctypes`
  `SendInput` / `mouse_event`, `xdotool`, AppleScript UI scripting, or
  equivalent real desktop control API.
- No sandbox path calls `/execute`.
- No Phase 9 export/import/replay path calls `/execute`.
- No mutation endpoint performs sandbox action.
- `wait` remains the only executable action in the current runtime.
- Real click/type/hotkey/scroll/switch_app remain disabled.

## Cockpit UI Invariants

- No execute button for sandbox or Phase 9 real action.
- No approval button that triggers real action.
- No real-action toggle.
- No sandbox action trigger.
- No Phase 10 readiness UI trigger for real action.
- No Phase 10 global status UI trigger for real action.
- UI controls for sandbox, Phase 9, export, import, validation, replay,
  readiness, global status, filtering, grouping, expand/collapse, and copy are
  local-only or read-only report loading.
- Cockpit display is not authorization.

## Dry-run And Sandbox Invariants

- `dry_run` remains default.
- `real_action_enabled` remains false by default.
- `real_actions_enabled` remains false.
- `phase10_real_actions_implemented` remains false.
- `go_for_phase10` remains false by default.
- No real-action adapter exists in Phase 10.1.
- No real-action adapter exists in Phase 10.2.
- `real_action_attempted` remains false in Phase 8 and Phase 9 dry-run reports.
- Non-dry-run requests with real action disabled are skipped, not executed.
- Sandbox scope remains one named test window and one named target.
- High-risk, unknown-risk, low-confidence, stale, invalid-geometry, missing
  target, missing approval, missing audit, missing verification, missing
  emergency stop, and outside-scope paths block or skip conservatively.

## Replay And Bundle Invariants

- Imported bundles are untrusted input.
- Replay is read-only.
- Validation errors do not mutate runtime state.
- Export and copy helpers read already loaded deterministic report data.
- Exports do not include secrets, API keys, credentials, broad filesystem dumps,
  or live desktop screenshots outside deterministic fixture data.
- Replay validation may explain eligibility, but it does not grant execution
  permission.

## Gate Separation Invariants

- Execution Policy, Permission Profile, and Capability Registry remain separate
  from readiness and report display.
- Safety Gate, Action Contract, Click Readiness, Phase 7 Gate, Phase 9 Gate,
  replay validation, audit logging, and verification are separate checks.
- Readiness is not permission.
- Proposal is not execution.
- Action Contract is not execution permission.
- Validation is not mutation.
- Export/replay is not action.
- AI handoff is not AI control.
- Global status is not permission.

## Documentation Invariants

- Docs must clearly distinguish dry-run vs real action.
- Docs must clearly distinguish proposal vs execution.
- Docs must clearly distinguish readiness vs permission.
- Docs must clearly distinguish cockpit display vs authorization.
- Docs must state that Phase 10 real actions are not implemented yet.
- Docs must state that real desktop actions remain disabled.

## Test And Verification Invariants

- `.\scripts\verify.ps1` must pass.
- `python scripts\safety_scan.py` must pass.
- `git diff --check` must pass.
- `node --check ui/app.js` must pass.
- Full `python -m unittest discover -s tests` must pass.
- Source-level tests should complement `safety_scan.py` for sandbox, Phase 9,
  and cockpit read-only paths.

## Phase 10 Boundary Invariant

No Phase 10 real-action implementation may begin unless
`docs/PHASE_10_READINESS_CHECKLIST.md` is explicitly satisfied by a new user
request. Until then, Phase 10 readiness work is docs, tests, auditability,
handoff, and dry-run regression protection only.

Phase 10.1 readiness reporting is also not permission. The readiness report,
GO/NO-GO display, endpoint, and cockpit panel must remain read-only/debug-only,
must not call `/execute`, and must not add a real-action UI trigger.

Phase 10.2 global status reporting is visibility and handoff only. The global
status report, endpoint, and cockpit panel must remain dry-run/read-only/
debug-only, must report NO-GO while real actions are disabled, must not call
`/execute`, and must not add a real-action UI trigger. Readiness is not
permission, cockpit display is not authorization, export/import/replay is not
execution, and AI handoff is not AI control.
