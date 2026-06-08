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
- Phase 10 readiness is documentation, tests, auditability, handoff, and
  release-candidate hardening only.
- Phase 10.1 readiness cockpit can display deterministic GO/NO-GO data, but it
  remains NO-GO by default and does not grant execution permission.
- Phase 10.2 global status cockpit can display deterministic project health,
  safety, readiness, Phase 9 export/import/replay validation state,
  verification expectations, and AI handoff context, but it remains
  read-only/dry-run/debug-only and does not grant execution permission.
- Phase 10.3 release-candidate guardrails add deterministic bundle validation
  helpers, browser-local cockpit validation, documentation, and regression
  tests for the current NO-GO boundary, but they remain read-only/local
  validation only and do not grant execution permission.

## Current Safety Boundary

The safety boundary is unchanged:

- No real desktop actions.
- No real click, type, hotkey, scroll, or switch_app execution.
- No execute buttons, approval buttons, real-action toggles, or sandbox action
  triggers in the cockpit.
- No real-action toggle.
- No calls to `/execute` from sandbox or replay UI paths.
- No /execute calls from sandbox or replay UI paths.
- No `pyautogui` click/move/write/press/hotkey/scroll actuation, `pynput`,
  `keyboard`, `mouse`, `win32api`, `ctypes` `SendInput` / `mouse_event`,
  `xdotool`, AppleScript UI scripting, or other real desktop actuation API.
  The existing `pyautogui` observer dependency is read-only screenshot,
  cursor, and screen-size capture only.
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
- Load and display a deterministic Phase 10 readiness report from
  `/phase10-readiness/demo`.
- Copy Phase 10 AI handoff summary, readiness JSON, no-go reasons, and safety
  invariants from already loaded browser state.
- Load and display a deterministic Phase 10.2 global status report from
  `/phase10-global-status/demo`.
- Copy Phase 10.2 global status JSON, AI handoff summary, no-go reasons,
  verification commands, and safety boundary from already loaded browser
  state.

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
- Treat cockpit display, export, import, replay, validation, readiness, or AI
  handoff as authorization to execute.
- Treat the Phase 10.2 Global Status / AI Handoff dashboard as permission,
  authorization, execution, or AI control.
- Treat the Phase 10.3 guardrail pack as approval to implement real actions.
- Treat a valid Phase 10.3 guardrail bundle as permission to execute.

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
- Phase 10 readiness / release-candidate hardening: project status docs,
  safety invariants, AI handoff context, and read-only status helper.
- Phase 10.1 readiness cockpit and report: deterministic NO-GO readiness
  report, read-only endpoint, cockpit display, and copy helpers.
- Phase 10.2 global status cockpit and AI handoff dashboard: deterministic
  NO-GO global status report, read-only endpoint, project health summary,
  Phase 9 validation state, local filters, and copy helpers.
- Phase 10.3 readiness regression pack and release-candidate guardrails:
  deterministic guardrail validation helpers, browser-local cockpit
  validation, NO-GO guardrail document, and source-level regression tests.

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
python -m unittest discover -s tests -p test_release_candidate_guardrails.py
python -m unittest discover -s tests -p test_phase10_guardrails.py
```

Read-only project status helper:

```powershell
.\scripts\project_status.ps1
```

## Latest Expected Verification State

The expected release-prep state is:

- `.\scripts\verify.ps1` passes.
- `python scripts\safety_scan.py` passes with no forbidden runtime desktop
  actuation calls found.
- `git diff --check` passes.
- `node --check ui/app.js` passes.
- Full unittest discovery passes.
- Latest stable full test count is expected to be in the mid-250s; small
  documentation or invariant-test additions may move it upward.
- Phase 9 replay and validation tests remain deterministic and do not require
  live desktop access.
- Phase 10.2 global status tests remain deterministic and do not require live
  desktop access.
- Phase 10.3 guardrail validation and tests remain deterministic and do not
  require live desktop access.

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
- AI handoff text can become stale if Phase 10 readiness docs are not updated
  alongside future architecture or roadmap edits.

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

Current Phase 10 readiness status: not ready for real action implementation.
The repository is ready for additional dry-run hardening, docs, tests, and
auditability work.

Phase 10.1 report status: `go_for_phase10 = false`,
`real_actions_enabled = false`, and
`phase10_real_actions_implemented = false`.

Phase 10.2 global status report status: `go_for_phase10 = false`,
`real_actions_enabled = false`, and
`phase10_real_actions_implemented = false`. The Global Status / AI Handoff
dashboard is visibility only. Readiness is not permission, cockpit display is
not authorization, export/import/replay is not execution, and AI handoff is
not AI control.

Phase 10.3 guardrail status: deterministic validation and regression
protection only. The guardrail pack validates pasted release-candidate bundles
locally, returns validation summaries and debug focus, and does not add
endpoints, permission changes, real-action controls, mutation paths, desktop
actuation, or authorization.

## Recommended Next Work

- Keep Phase 9 replay validation stable while adding small regression tests for
  any cockpit UX changes.
- Add a concise release checklist that references this snapshot, safety scan,
  and `verify.ps1`.
- Review Phase 9 copy/export payloads for sensitive debug text before any public
  demo.
- Consider a read-only architecture diagram for the Phase 9 bundle lifecycle:
  export, import, validate, replay, and AI handoff.
- Use `docs/PHASE_10_READINESS_CHECKLIST.md`,
  `docs/AI_HANDOFF_CONTEXT.md`, and `docs/SAFETY_INVARIANTS.md` as the first
  handoff bundle for future Phase 10 discussions.
- Use `/phase10-global-status/demo` and the Phase 10.2 cockpit panel as a
  compact read-only handoff layer for current project health and no-go state.
- Use `docs/PHASE_10_RELEASE_CANDIDATE_GUARDRAILS.md`,
  `tests/test_release_candidate_guardrails.py`, and
  `tests/test_phase10_guardrails.py` for release-candidate regression
  protection.
- Defer all real-action work until Phase 10 is explicitly approved and scoped.

## AI Handoff Summary

For the next AI handoff:

- Treat this repository as a dry-run, read-only, debug-only cockpit.
- Preserve the hard safety boundary: no real desktop actions and no `/execute`
  path from Phase 8 or Phase 9 cockpit UI.
- Phase 9.x is about deterministic sandbox reports, reproducibility bundles,
  import/replay validation, and cockpit readability.
- Phase 10.2 is about deterministic global status visibility and AI handoff,
  not desktop control.
- Phase 10.3 is about deterministic release-candidate validation and
  regression protection, not desktop control.
- Imported bundles are untrusted local input.
- Prefer docs and tests for release-prep work unless the user explicitly asks
  for runtime changes.
- Always run `.\scripts\verify.ps1`, `python scripts\safety_scan.py`,
  `git diff --check`, and `node --check ui/app.js` after UI or safety-related
  edits.

## Under 20-line Future Codex Explanation

1. `lain-desk-agent` is a supervised local desktop-agent cockpit.
2. It is dry-run, read-only, and debug-only for sandbox/replay paths.
3. The only executable action remains approved `wait`.
4. Real click/type/hotkey/scroll/switch_app are disabled.
5. Phase 8 validates sandbox gates with deterministic dry-run reports.
6. Phase 9 adds a dry-run harness with mock approval, emergency stop,
   verification, rollback, export, import, validation, and replay.
7. Imported bundles are untrusted input.
8. Replay is read-only.
9. Proposal is not execution.
10. Readiness is not permission.
11. Cockpit display is not authorization.
12. Execution Policy, Permission Profile, and Capability Registry remain
    separate gates.
13. Do not add `/execute` from sandbox or replay UI.
14. Do not add real desktop APIs.
15. Do not add real-action toggles or execute controls.
16. Phase 10 real actions are not implemented yet.
17. Read `docs/PHASE_10_READINESS_CHECKLIST.md` before Phase 10 work.
18. The Phase 10.1 readiness panel reports NO-GO by default.
19. The Phase 10.2 global status panel reports NO-GO by default.
20. The Phase 10.3 guardrail pack is local validation/tests only.
