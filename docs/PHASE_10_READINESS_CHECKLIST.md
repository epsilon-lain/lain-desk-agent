# Phase 10 Readiness Checklist

This checklist is the release-candidate hardening gate before any future
Phase 10 real-action experiment is even considered.

Phase 10 real actions are NOT implemented yet. The current project remains a
dry-run, read-only, debug-only cockpit with wait-only execution.

## Current Project Phase

- Current phase: post-Phase 9.x dry-run sandbox hardening.
- Current runtime: supervised local cockpit.
- Current executable action: approved `wait` only.
- Current sandbox state: deterministic dry-run reports, export/import/replay,
  validation, and cockpit debugging.
- Phase 10 status: readiness planning only; no real desktop action adapter
  exists.
- Phase 10.1 status: read-only readiness report and cockpit panel exist; they
  report NO-GO by default and do not grant execution permission.

## Hard Safety Boundary

- No real desktop actions.
- No real click/type/hotkey/scroll/switch_app execution.
- No sandbox path may call `/execute`.
- No execute button, approval button for real action, sandbox action trigger,
  or real-action toggle may be added.
- No real-action toggle.
- No mutation endpoint may perform desktop action.
- No `pyautogui`, `pynput`, `keyboard`, `mouse`, `win32api`, `ctypes`
  `SendInput` / `mouse_event`, `xdotool`, AppleScript UI scripting, or other
  real desktop control API may be imported or called.
- Execution Policy, Permission Profile, Capability Registry, and permission
  matrix must not be modified to allow real actions during readiness work.
- Safety Gate, Action Contract, Click Readiness, Phase 7 Gate, Phase 9 Gate,
  replay validation, and audit constraints must not be bypassed.

## Prerequisite Gates Before Any Real Action Experiment

Every future Phase 10 proposal must satisfy all of these before implementation:

- Phase 7 gate reviewed and explicitly satisfied.
- Phase 9 dry-run harness still passing and deterministic.
- Safety Gate result is low risk.
- Action Contract is present, non-preview for the future experiment, and bound
  to one sandbox target.
- Click Readiness, or the matching readiness policy, is ready with no blockers.
- Capability Registry grants only the exact experimental action, and only after
  a separate safety review.
- Permission Profile grants only the exact experimental action, and only after
  a separate safety review.
- Execution Policy grants only the exact experimental action, and only after a
  separate safety review.
- Audit plan, rollback plan, emergency stop, and post-action verification plan
  are all present before action.

Readiness is not permission. Proposal is not execution.
Cockpit display is not authorization.

## Required Approvals

- The user must explicitly approve the Phase 10 implementation task.
- The user must explicitly approve the exact experiment name, sandbox window,
  target, action type, and expected state change.
- Approval must bind to one action contract and expire on stale observation,
  target geometry change, active window change, target label change, or risk
  change.
- Approval must never be inferred from a successful dry-run, replay validation,
  export, import, or cockpit display.

## Emergency Stop Requirements

- Emergency stop must be visible and test-covered.
- Emergency stop must be checked after approval and immediately before any
  future action.
- Active emergency stop must block all non-wait actions.
- Missing emergency stop must block all non-wait actions.
- Emergency stop events must be audited.
- Emergency stop must force the experiment back to dry-run state.

## Post-action Verification Requirements

Future verification must:

- Capture post-action state inside the sandbox scope only.
- Compare against one explicit expected state change.
- Confirm the target window and target element are still the sandbox target.
- Confirm no forbidden surface received input.
- Record audit events for verification planned, passed, failed, or skipped.
- Treat missing verification as failure.

## Rollback Requirements

- Rollback must be planned before any future action.
- Rollback must be sandbox-only.
- Rollback must not use broader permissions than the original experiment.
- Rollback failure must be audited.
- No automatic retry is allowed.
- Prefer resetting a deterministic local fixture over performing a second
  desktop action.

## Audit Logging Requirements

At minimum, future Phase 10 audit records must include:

- experiment requested
- gate checked
- user approval checked
- emergency stop checked
- action contract checked
- readiness checked
- execution requested
- execution blocked or skipped
- post-action verification planned
- post-action verification result
- rollback planned or recorded

Audit logging failure is a blocker.

## Dry-run Parity Requirements

Before real action can be considered, the dry-run path must emit the same
scenario identifiers, blocker codes, failure reason codes, audit event order,
target risk/confidence, readiness status, and verification plan fields that the
future experiment would emit.

Dry-run remains the default. `real_action_enabled` remains false by default.

## Phase 10.1 Readiness Cockpit Status

Phase 10.1 adds:

- `src/lain_desk_agent/phase10_readiness.py`
- `GET /phase10-readiness/demo`
- a read-only cockpit Phase 10 readiness panel
- copy helpers for AI handoff summary, readiness JSON, no-go reasons, and
  safety invariants

The Phase 10.1 report is deterministic and current-state only. It must keep:

- `go_for_phase10 = false`
- `real_actions_enabled = false`
- `phase10_real_actions_implemented = false`
- `dry_run = true`
- `read_only = true`
- `debug_only = true`

Expected no-go reasons include:

- `phase10_real_actions_not_implemented`
- `real_actions_disabled`
- `manual_phase10_approval_not_recorded`
- `real_action_adapter_absent`
- `live_sandbox_scope_not_selected`
- `live_post_action_verification_not_implemented`

These no-go reasons are expected readiness blockers, not runtime errors.
Real actions are still disabled.

## Sandbox Scope Requirements

The first Phase 10 experiment scope must be:

- one named test window only
- one named test target only
- one low-risk action only
- deterministic fixture first
- no system settings
- no file deletion
- no shell execution
- no browser credential fields
- no external websites unless mocked locally
- no destructive actions
- no hidden/background actions

## Forbidden Actions

Forbidden actions include:

- click/type/hotkey/scroll/switch_app outside the named sandbox experiment
- send, submit, delete, pay, buy, confirm, login, password, credential, or
  payment-field interaction
- file deletion, shell execution, settings changes, external website
  interaction, hidden/background action, or automatic retry

## Forbidden APIs

Forbidden APIs include:

- `pyautogui`
- `pynput`
- `keyboard`
- `mouse`
- `win32api`
- `ctypes` `SendInput`
- `ctypes` `mouse_event`
- `xdotool`
- AppleScript UI scripting
- any equivalent real desktop control API

## Required Tests Before Phase 10 Implementation

- `.\scripts\verify.ps1`
- `python scripts\safety_scan.py`
- `git diff --check`
- `node --check ui/app.js`
- full `python -m unittest discover -s tests`
- source-level checks proving sandbox and Phase 9 paths do not call `/execute`
- tests proving dry-run defaults and `real_action_enabled = false`
- tests proving imported bundles are untrusted input
- tests proving replay is read-only and validation errors do not mutate runtime
  state

## Required Manual Checks Before Phase 10 Implementation

- Review this checklist.
- Review `docs/PHASE_7_SANDBOX_ACTION_DESIGN.md`.
- Review `docs/PHASE_9_MINIMAL_SANDBOX_EXPERIMENT_DESIGN.md`.
- Review `docs/SAFETY_INVARIANTS.md`.
- Confirm cockpit UI has no real-action trigger.
- Confirm no default permission grants real desktop action.
- Confirm safety scan still fails on obvious desktop actuation samples.

## Required Documentation Before Phase 10 Implementation

- Update architecture with the proposed experiment boundary.
- Update roadmap with exact Phase 10 scope and non-goals.
- Update safety invariants if any new gate is introduced.
- Add a rollback and emergency stop design note.
- Add an AI handoff warning that real actions remain disabled until the exact
  checklist is satisfied.

## Go / No-go Checklist

Go only if every item is true:

- [ ] Explicit user request for Phase 10 implementation exists.
- [ ] Phase 7 gate is satisfied.
- [ ] Phase 9 dry-run parity is satisfied.
- [ ] Sandbox scope is one window and one target.
- [ ] Action type is low risk and named.
- [ ] Emergency stop exists and is tested.
- [ ] Post-action verification exists and is tested.
- [ ] Rollback exists and is tested.
- [ ] Audit logging exists before and after the action.
- [ ] Dry-run remains default.
- [ ] `real_action_enabled` remains false by default.
- [ ] `verify.ps1` and `safety_scan.py` pass.

No-go if any item is false.

## Stop Immediately If...

- A change adds a real desktop API import.
- A sandbox or replay UI path calls `/execute`.
- A cockpit control can trigger real action.
- A permission profile grants broad desktop control.
- Imported bundle data is treated as trusted command input.
- Readiness is treated as permission.
- Proposal is treated as execution.
- Validation mutates runtime state.
- Audit logging is optional.
- Emergency stop is missing.

## AI Handoff Checklist

Future AI / Codex sessions must:

- Treat this repository as dry-run, read-only, debug-only.
- Preserve no real desktop actions.
- Run `.\scripts\verify.ps1`, `python scripts\safety_scan.py`,
  `git diff --check`, and `node --check ui/app.js`.
- Read `docs/AI_HANDOFF_CONTEXT.md` before making Phase 10-related changes.
- Do not enable real actions unless this Phase 10 readiness checklist is
  explicitly satisfied by a new user request.
