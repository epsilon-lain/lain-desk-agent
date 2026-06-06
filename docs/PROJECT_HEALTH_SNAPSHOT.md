# Project Health Snapshot

This snapshot records the current release-prep state for the dry-run desktop
agent cockpit. It is intended for future AI assistants, Codex sessions, and
developers who need a fast, accurate handoff without re-deriving the safety
model from the full repository history.

## Current Project Status

Mirai / `lain-desk-agent` is a supervised local desktop-agent cockpit for
observing, planning, previewing, evaluating, exporting, importing, and replaying
deterministic dry-run traces.

The project is still read-only and debug-only for desktop interaction. It can
run approved `wait` behavior through the existing contract path, but it does
not perform real desktop input. Phase 9.x work has focused on dry-run sandbox
experiment design, deterministic harness reporting, cockpit inspection, export,
bundle import, replay, and replay validation hardening.

Latest expected state:

- Phase 9 dry-run sandbox work is implemented through the cockpit debug
  surfaces.
- Phase 9 reproducibility bundles can be exported, imported, validated, and
  replayed locally.
- Imported bundles are treated as untrusted input.
- Replay validation is local-only and does not change runtime behavior.
- No real desktop actions are enabled.

## Current Safety Boundary

The safety boundary is unchanged:

- No real desktop actions.
- No real click, type, hotkey, scroll, or switch_app execution.
- No execute buttons, approval buttons, real-action toggles, or sandbox action
  triggers in the cockpit.
- No calls to `/execute` from sandbox or replay UI paths.
- No `pyautogui`, `pynput`, `keyboard`, `mouse`, `win32api`, `ctypes`
  `SendInput` / `mouse_event`, `xdotool`, AppleScript UI scripting, or other
  real desktop control API.
- No changes to Execution Policy, Permission Profile, Capability Registry, or
  any permission matrix to grant real action permissions.
- Dry-run mode remains the default inspection and experiment posture.

Readiness, validation, replay eligibility, and audit checks are diagnostic
signals only. They are not execution permission.

## What The Cockpit Can Do

The cockpit can:

- Show runtime status, execution policy, events, planner trace, and readiness
  diagnostics.
- Display deterministic planner evaluation and sandbox evaluation reports.
- Show Phase 9 dry-run harness scenario outcomes, blockers, support-state
  checks, and audit traces.
- Render grouped and filterable Phase 9 audit timelines.
- Copy read-only Phase 9 JSON reports, AI-readable summaries, validation
  summaries, validation errors, debug focus text, and reproducibility bundles
  from already loaded browser state.
- Import a Phase 9 reproducibility bundle as local untrusted text.
- Validate imported bundles for required fields, unsafe flags, sensitive key
  findings, consistency, audit ordering, and read-only replay eligibility.
- Replay deterministic audit timelines locally for debugging and handoff.

## What The Cockpit Cannot Do

The cockpit cannot:

- Click, type, press hotkeys, scroll, or switch applications.
- Execute sandbox actions.
- Grant user approval for real actions.
- Toggle real action enablement.
- Upload imported bundles for execution.
- Treat imported bundle data as trusted.
- Convert readiness or validation success into actuation permission.
- Modify Execution Policy, Permission Profile, Capability Registry, or the
  permission matrix from the UI.

## Completed Phase Summary

- Phase 4: proposal-only AI planner integration and validation path.
- Phase 5: normalized visible elements and read-only ui_tree grounding.
- Phase 6: deterministic planner evaluation expansion.
- Phase 6.5: click readiness hardening with structured blocker codes.
- Phase 7: sandbox action design-only safety gate.
- Phase 8: dry-run sandbox experiment framework.
- Phase 8.1: deterministic sandbox evaluation and trace reporting.
- Phase 8.2: cockpit sandbox evaluation trace exposure.
- Phase 8.3 to 8.5: sandbox trace UX filters, grouping, chips, counts, and
  read-only copy/debug controls.
- Phase 9: minimal sandbox real-action experiment design, still dry-run-only.
- Phase 9.1: deterministic Phase 9 dry-run experiment harness.
- Phase 9.2: cockpit display for Phase 9 harness status.
- Phase 9.3: advanced audit timeline UX.
- Phase 9.4: report export and reproducibility bundle.
- Phase 9.5: bundle import and deterministic replay.
- Phase 9.6: replay validation hardening for imported bundles.
- Phase 9.7 / 9.8: replay validation cockpit UX polish for health strips,
  issue groups, copy helpers, and AI handoff readability.

## Test And Verification Commands

Primary verification:

```powershell
.\scripts\verify.ps1
```

Manual equivalent:

```powershell
python -m compileall src tests
python -m unittest discover -s tests
node --check ui/app.js
python scripts\safety_scan.py
git diff --check
```

Targeted checks commonly used during Phase 9.x work:

```powershell
python -m unittest discover -s tests -p test_phase9_experiment.py
python -m unittest discover -s tests -p test_project_health_snapshot.py
python scripts\safety_scan.py
node --check ui/app.js
```

## Latest Expected Verification State

The expected release-prep state is:

- `.\scripts\verify.ps1` passes.
- `python scripts\safety_scan.py` passes with no forbidden runtime desktop
  actuation calls found.
- `git diff --check` passes.
- `node --check ui/app.js` passes.
- Full unittest discovery passes.
- Phase 9 replay and validation tests remain deterministic and do not require
  live desktop access.

## Known Non-goals

- Building a general-purpose desktop controller.
- Enabling real click/type/hotkey/scroll/switch_app actions.
- Adding a real desktop action adapter.
- Adding execution controls to the cockpit.
- Treating Phase 9 imported bundles as trusted instructions.
- Changing Execution Policy, Permission Profile, Capability Registry, or
  permission matrix behavior.
- Sending screenshots, credentials, or sensitive local state to an LLM.

## Known Remaining Risks

- UI complexity has grown around Phase 9 replay, filtering, grouping, copy, and
  validation controls; tests should keep guarding read-only behavior.
- Imported bundle text is intentionally untrusted; future fields must preserve
  local-only parsing and validation.
- Copy/export payloads may contain debugging context from deterministic reports;
  users should still review content before sharing it outside the repository.
- Readiness and validation names can sound action-oriented; documentation and UI
  copy must keep saying they are diagnostics, not permission.
- Future Phase 10 work could accidentally broaden execution if it bypasses the
  Phase 7 gate, safety scan, or permission boundaries.

## Phase 10 Readiness Checklist

Phase 10 readiness requires all of the following before any implementation is
considered:

- Phase 7 checklist reviewed and explicitly satisfied.
- Separate user approval for any Phase 10 implementation work.
- A named, single-purpose sandbox scope.
- One visible test window and one visible test target.
- Low-risk target only.
- Fresh observation and valid normalized target geometry.
- Valid action contract, readiness result, audit plan, post-action verification
  plan, rollback expectation, and emergency stop behavior.
- Dry-run remains the default.
- Real action remains disabled unless a future task explicitly approves a
  separately guarded adapter.
- Safety scan updated only for an explicitly guarded experimental path, never
  for general desktop control.
- Execution Policy, Permission Profile, Capability Registry, and permission
  matrix changes are reviewed as separate safety-sensitive work.

## Recommended Next Work

- Keep Phase 9 replay validation stable while adding small regression tests for
  any cockpit UX changes.
- Add a concise release checklist that references this snapshot, safety scan,
  and `verify.ps1`.
- Review Phase 9 copy/export payloads for sensitive debug text before any public
  demo.
- Consider a read-only architecture diagram for the Phase 9 bundle lifecycle:
  export, import, validate, replay, and AI handoff.
- Defer all real-action work until Phase 10 is explicitly approved and scoped.

## AI Handoff Summary

For the next AI handoff:

- Treat this repository as a dry-run, read-only, debug-only cockpit.
- Preserve the hard safety boundary: no real desktop actions and no `/execute`
  path from Phase 8 or Phase 9 cockpit UI.
- Phase 9.x is about deterministic sandbox reports, reproducibility bundles,
  import/replay validation, and cockpit readability.
- Imported bundles are untrusted local input.
- Prefer docs and tests for release-prep work unless the user explicitly asks
  for runtime changes.
- Always run `.\scripts\verify.ps1`, `python scripts\safety_scan.py`,
  `git diff --check`, and `node --check ui/app.js` after UI or safety-related
  edits.
