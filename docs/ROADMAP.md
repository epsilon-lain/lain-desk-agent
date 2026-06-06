# Roadmap

## Current State

Current version: v0.3 guarded wait-only cockpit + proposal-only AI planner.

Mirai is currently a supervised local cockpit for observing, understanding,
planning, previewing, and safely testing a narrow execution path. The project
does not provide real mouse or keyboard desktop control. `wait` is the only
executable action.

Phase 4 AI Planner integration is now wired end to end for proposal generation:
`planner_context` can feed optional `ai_proposal` mode, every AI output is
validated, `/proposal` returns compact `planner_trace`, and unsafe or invalid
AI output remains a safe `no_op`.

Phase 6 Planner Evaluation Expansion is implemented as a deterministic,
read-only reliability suite. It compares rule-based and AI proposal planner
behavior across normalized `visible_elements` and `ui_tree` fixtures before any
real action experiment.

Phase 6.5 Click Readiness Hardening is implemented as structured theoretical
pre-execution diagnostics. It adds stable blocker codes and stricter coordinate,
freshness, confidence, risk, and ambiguity checks while real clicks remain
disabled.

Phase 7 is a design-only sandbox action gate. It records the requirements for
any future minimal real-action experiment, but it does not implement or enable
real desktop actions.

Phase 8 now has a dry-run sandbox experiment framework. It validates the
Phase 7 gate shape, records structured audit events, and skips any non-dry-run
request because no real-action adapter exists.

Phase 8.1 adds deterministic sandbox experiment evaluation and trace reporting.
It evaluates only fixture-backed dry-run and skipped outcomes, including gate
failure reasons and audit event ordering.

Phase 8.2 exposes that sandbox evaluation trace in the cockpit as read-only
debug output. It does not add execution controls or real-action permissions.

Phase 8.3 polishes that cockpit trace with read-only filters, fixture-set
views, summary counts, collapsible scenario details, and audit event sequence
views. It does not add execution controls or real-action permissions.

Phase 8.4 adds cockpit trace readability polish: clearer status chips, blocker
severity/descriptions, compact summary cards, improved empty states, and more
legible audit event chips. It is still read-only/debug-only.

Phase 8.5 refines cockpit trace navigation with blocker-group quick filters,
reset/copy-summary display controls, text mini-bars, and scenario grouping.
It remains local-only UI behavior over the existing deterministic report.

Phase 9 is now designed as a minimal sandbox real-action experiment plan, but
it is still design-only, dry-run-only, and not execution permission. It selects
a tiny deterministic scenario subset, requires Phase 7 gate validation, uses
mock approval and mock emergency stop hooks, and preserves the Phase 8 report
shape.

Phase 9.1 implements the first minimal sandbox experiment harness as
dry-run-only simulation. It reuses the Phase 7 gate through the Phase 8 sandbox
framework, adds mock approval, mock emergency stop, mock verification, and mock
rollback checks, and always reports `real_action_attempted = false`.

Phase 9.2 exposes the Phase 9.1 dry-run harness report in the cockpit as
read-only debug output. It displays mock approval, emergency stop,
verification, rollback, blockers, and audit trace data without adding any
execution control.

Phase 9.3 improves the Phase 9 cockpit audit timeline with local-only grouping,
original-order metadata, event chips, and expandable event detail rows. It is
still read-only/debug-only and does not add execution control.

## Completed

- Observation / Understanding
- Planner Context Bundle
- Rule-based Planner
- Proposal-only AI Planner
- AI Planner test harness
- AI Planner runtime status fields
- Planner Trace
- Planner Evaluation Harness
- Planner Evaluation Expansion
- Planner Evaluation cockpit panel
- Safety Gate
- Action Contract
- Click Readiness Policy
- Click Readiness Hardening
- Phase 7 Sandbox Action Design Gate
- Phase 8 Dry-run Sandbox Experiment Framework
- Phase 8.1 Sandbox Evaluation Trace
- Phase 8.2 Sandbox Evaluation Cockpit Trace
- Phase 8.3 Sandbox Trace Cockpit UX
- Phase 8.4 Sandbox Trace UX Polish
- Phase 8.5 Sandbox Trace UX Refinements
- Phase 9 Minimal Sandbox Experiment Design
- Phase 9.1 Minimal Sandbox Experiment Harness
- Phase 9.2 Phase 9 Harness Cockpit Display
- Phase 9.3 Phase 9 Advanced Audit Timeline UX
- Capability Registry
- Permission Profile
- Execution Policy Matrix
- wait-only Actuation
- wait-only Verification
- Runtime Status
- Event Viewer
- Demo Scenario Simulator
- CI
- Documentation

## Current Hard Boundary

- No real mouse or keyboard desktop control.
- No click, type, hotkey, or scroll execution.
- No `switch_app` execution.
- No screenshot is sent to the LLM.
- No API keys are committed or logged.
- AI Planner output is proposal-only.
- LLM output must be validated before it can become a proposal.
- Unsafe or invalid AI output becomes safe `no_op`.
- `/proposal` is inspectable but never executes desktop input.
- `/execute` remains wait-only.
- Phase 8 sandbox experiments are dry-run or skipped only.
- Phase 8.1 sandbox evaluation is fixture-only and performs no actions.
- Phase 8.2 cockpit trace exposure is read-only/debug-only.
- Phase 8.3 sandbox trace UX is read-only/debug-only.
- Phase 8.4 sandbox trace polish is read-only/debug-only.
- Phase 8.5 sandbox trace refinements are read-only/debug-only.
- Phase 9 minimal sandbox experiment design is design-only, dry-run-only, and
  not execution permission.
- Phase 9.1 minimal sandbox experiment harness is dry-run-only simulation and
  not execution permission.
- Phase 9.2 Phase 9 harness cockpit display is read-only/debug-only and not
  execution permission.
- Phase 9.3 Phase 9 advanced audit timeline UX is read-only/debug-only and not
  execution permission.

## Phase 4: AI Planner Evaluation And Reliability

Status: integration path complete; evaluation and reliability work continues.

Goal: evaluate the optional `ai_proposal` planner while keeping it proposal-only.

- Preserve the end-to-end path:
  `planner_context -> ai_proposal -> validate_ai_proposal -> proposal response`.
- Keep `/proposal` responses inspectable with compact `planner_trace`.
- Report `planner_mode`, API key configuration, and AI planner usability in
  Runtime Status.
- Fallback safely on missing API key, API call failure, malformed AI output,
  unknown action types, and unsafe executable action proposals.
- Compare rule-based output against `ai_proposal` output.
- Use the Planner Evaluation Harness to compare both planners on demo/read-only
  scenarios without external LLM calls or desktop control.
- Show demo evaluation reports in the cockpit as a read-only panel.
- Summarize planner evaluation observations for strategy tuning, including
  agreement, preview-only contracts, blocked click readiness, and read-only
  risk hints.
- Validate AI output quality across demo scenarios and live read-only
  observations.
- Improve the planner prompt and payload shape.
- Keep all AI outputs limited to:
  - `no_op`
  - `target_hint`
  - `switch_app_hint`
- Keep all AI outputs behind `validate_ai_proposal`, Safety Gate, Action
  Contract, Click Readiness, Capability Registry, Permission Profile, and
  Execution Policy.

## Phase 5: Better Read-only Grounding

Status: schema baseline and fixture-friendly `ui_tree` adapter implemented;
live read-only sources still pending.

Goal: improve `visible_elements` without adding desktop control.

- Normalize visible elements into the stable `VisibleElement` shape:
  `id`, normalized `label`/`text`, `role`, `bbox`, `center`, `confidence`,
  `source`, `risk_hint`, and `timestamp`.
- Keep sources explicitly marked as read-only grounding with source values
  limited to `ocr`, `ui_tree`, or `manual`.
- Convert fixture-provided `ui_tree` nodes into the same schema without using
  live OS automation APIs.
- Keep hidden or disabled `ui_tree` nodes low-confidence so they remain debug
  grounding rather than target candidates.
- Filter malformed, out-of-bounds, unlabeled, and invalid-schema elements
  before they can become planner targets.
- Treat low-confidence or ambiguous target matches as `no_op`.
- Add a live read-only accessibility source, DOM source, or improved OCR source.
- Keep every grounding source read-only.
- Improve visible element labels, bounding boxes, confidence scores, and source
  metadata.
- Keep planner inputs compact.
- Continue excluding screenshot bytes and screenshot paths from LLM payloads.

## Phase 6: Planner Evaluation Expansion

Status: implemented as a read-only, preview-only evaluation suite.

Goal: evaluate planner reliability before any real action experiment.

- Compare rule-based planner output against deterministic AI proposal planner
  output without external LLM calls.
- Define fixture-level expected behavior for action type, risk,
  `requires_approval`, preview-only contract state, readiness status, and
  blocker reason.
- Cover normal safe `ui_tree` buttons, disabled or hidden `ui_tree` buttons,
  low-confidence targets, ambiguous same-label targets, high-risk targets,
  invalid or missing bbox targets, mixed manual plus `ui_tree` sources, and no
  visible target.
- Require conservative degradation: ambiguous, low-confidence, disabled,
  hidden, invalid-geometry, or missing-target states become `no_op`, blocked,
  or preview-only outcomes.
- Continue routing every proposal through Safety Gate, Action Contract, Click
  Readiness, and Execution Policy summaries.
- Keep all evaluation paths read-only and preview-only; no real
  click/type/hotkey/scroll/switch_app execution is enabled.

## Phase 6.5: Click Readiness Hardening

Status: implemented as structured read-only readiness diagnostics.

Goal: make preview-only click contracts stricter and easier to test before any
real click experiment.

- Record stable blocker codes including stale observation, missing or invalid
  geometry, center mismatch, out-of-viewport targets, unknown coordinate space,
  uncertain DPI, low-confidence targets, hidden or disabled targets, ambiguous
  targets, high-risk approval gates, and policy-disabled actions.
- Validate bbox and center against declared viewport metadata.
- Block readiness when coordinate space or DPI/scale metadata is unavailable.
- Consume preview-contract target schema fields such as role, source,
  confidence, timestamp, and `target_risk_hint`.
- Keep high-risk targets preview-only and approval-gated.
- Show blocker codes, human-readable blocker copy, target risk/confidence, and
  coordinate debug in the Cockpit and planner evaluation reports.
- Keep readiness as a theoretical pre-execution check, not an execution
  permission.
- Keep real click disabled by default.
- Keep click readiness as a blocker, not a permission grant.

## Phase 7: Sandboxed Real Action Experiment Design Gate

Status: design-only gate documented in
`docs/PHASE_7_SANDBOX_ACTION_DESIGN.md`.

Goal: define the minimum safety, permission, approval, audit, verification, and
rollback requirements before any real-action experiment can be implemented.

- Do not implement real click/type/hotkey/scroll/switch_app execution.
- Do not enable any new Capability Registry, Permission Profile, or Execution
  Policy permission.
- Require one test window, one test target, one low-risk action, and dry-run as
  the default.
- Require explicit user approval tied to one action contract.
- Require visible target confirmation, fresh observation, valid bbox/center,
  viewport, coordinate-space, DPI, confidence, risk, and ambiguity checks.
- Require audit events before and after any future action.
- Require post-action screenshot or state verification.
- Require emergency stop behavior and rollback/reset expectations.
- Block any real-action Phase 8 adapter until the Phase 7 checklist is
  satisfied and separately approved.

## Phase 8: Sandboxed Real-action Experiment

Status: dry-run skeleton implemented; real-action adapter still blocked until
the Phase 7 checklist is satisfied and explicitly approved.

Goal: validate the smallest possible sandbox experiment shape before adding
any real desktop action adapter.

- Keep the default product behavior wait-only and dry-run.
- Define `SandboxExperimentConfig`, `SandboxExperimentRequest`,
  `SandboxExperimentResult`, `validate_phase7_gate(...)`, and
  `run_sandbox_experiment(...)`.
- Treat `dry_run = true` and `real_action_enabled = false` as the default
  safety posture.
- Return simulated dry-run results when all gates pass.
- Return `sandbox_real_action_skipped` for non-dry-run requests while no
  separately approved adapter exists.
- Use one deterministic local fixture or mocked target first.
- Limit scope to one visible test window and one explicitly marked test target.
- Keep system settings, file deletion, shell execution, credential fields,
  external websites, destructive actions, and hidden/background actions out of
  scope.
- Keep the experiment behind Safety Gate, Action Contract, Click Readiness,
  Capability Registry, Permission Profile, explicit user approval, and
  Execution Policy.
- Require post-action observation and verification.
- Record audit events for every request, block, approval, execution,
  verification, rollback, and emergency stop.
- Do not broaden default product behavior or enable click/type/hotkey/scroll/
  switch_app in production.

## Phase 8.1: Sandbox Experiment Evaluation And Trace

Status: implemented as deterministic dry-run evaluation.

Goal: make the sandbox gate inspectable before any real-action adapter exists.

- Add deterministic sandbox scenarios for dry-run success, real-action skip,
  missing approval, stale observation, high-risk and unknown-risk targets,
  low-confidence targets, invalid bbox, bbox/center mismatch, missing viewport
  or coordinate metadata, missing post-action verification, forbidden action
  types, out-of-scope targets, readiness blockers, missing emergency stop,
  missing audit plan, missing action contract, and missing target.
- Report scenario ID/name, expected and actual outcome, pass/fail, gate status,
  failure reason codes, readiness blocker codes, audit event names, dry-run
  status, real-action-enabled status, real-action-skipped status, post-action
  verification planning, target risk hint, target confidence, readiness state,
  action type, and notes.
- Include trace/debug output with validation checks and audit event ordering.
- Keep evaluation fixture-only and backend/test-only; no live desktop
  observation, no `/execute` call, no UI real-action trigger, and no desktop
  control API.
- Preserve disabled click/type/hotkey/scroll/switch_app permissions.

## Phase 8.2: Sandbox Evaluation Cockpit Trace

Status: implemented as read-only cockpit debug integration.

Goal: make deterministic sandbox gate behavior inspectable in the cockpit
without adding any real-action path.

- Expose the existing `sandbox_evaluation.py` report through a read-only
  cockpit endpoint.
- Display scenario ID/name, expected versus actual outcome, pass/fail, gate
  status, failure reason codes, readiness blocker codes, audit event names,
  dry-run status, real-action-enabled status, real-action-skipped status,
  post-action verification planning, target risk/confidence, readiness state,
  action type, notes, and trace debug JSON.
- Show empty/error states when the report is unavailable.
- Keep the cockpit panel debug-only: no execute button, no approval button, no
  real-action toggle, and no sandbox UI path to `/execute`.
- Keep the endpoint fixture-backed and deterministic; no live desktop
  observation, no actuation, and no desktop control API.
- Preserve disabled click/type/hotkey/scroll/switch_app permissions.

## Phase 8.3: Sandbox Trace Cockpit UX

Status: implemented as read-only cockpit UX polish.

Goal: make deterministic sandbox evaluation traces easier to inspect without
adding any execution path.

- Add cockpit filters for pass/fail, fixture set, scenario type, and blocker
  code.
- Show summary counts for total, visible, passed, failed, and real-action
  skipped scenarios.
- Render scenario cards with stable trace fields for expected versus actual
  outcome, failure reason codes, blocker codes, audit event names, dry-run
  state, real-action-skipped state, post-action verification planning, target
  risk/confidence, readiness state, and action type.
- Add read-only expand/collapse controls for scenario details.
- Add per-scenario and visible-scenario audit event sequence views.
- Keep all controls local to deterministic report display: no execute button,
  no approval button, no real-action toggle, no sandbox path to `/execute`, and
  no desktop control API.
- Preserve `real_action_enabled = false` fixture behavior and disabled
  click/type/hotkey/scroll/switch_app permissions.

## Phase 8.4: Sandbox Trace UX Polish

Status: implemented as read-only cockpit readability polish.

Goal: make sandbox evaluation traces easier to scan without changing behavior
or safety boundaries.

- Add clearer status chips for pass, fail, skipped, and blocked outcomes.
- Add blocker severity styling and inline descriptions for common blocker
  codes.
- Render compact summary cards for total, visible, passed, failed, skipped,
  and blocked scenarios.
- Improve empty filter states by showing the active local filters.
- Improve audit timeline readability with short event labels and tone styling.
- Keep all data sourced from the existing Phase 8.1/8.2 deterministic report
  shape; no second trace format is introduced.
- Keep filters and polish local-only in the browser: no execute button, no
  approval button, no real-action toggle, no sandbox path to `/execute`, and no
  desktop control API.
- Preserve disabled click/type/hotkey/scroll/switch_app permissions and
  `real_action_enabled = false` sandbox behavior.

## Phase 8.5: Sandbox Trace UX Refinements

Status: implemented as read-only cockpit navigation refinements.

Goal: make sandbox evaluation traces easier to navigate while preserving the
existing deterministic report shape and safety boundaries.

- Add local-only quick filter chips for geometry, readiness, approval, risk,
  scope, and audit-related sandbox blockers.
- Add a reset filters control that only resets browser-side filter state.
- Add a copy summary control that copies the currently visible deterministic
  sandbox summary JSON/debug text; it does not call backend endpoints.
- Add lightweight text bars for passed, failed, skipped, and blocked counts.
- Group visible scenarios by scenario type or outcome to improve scanning.
- Strengthen visual distinction between passed dry-runs, skipped non-dry-run
  requests, blocked gates, and failed expectations.
- Keep all fields sourced from the existing Phase 8.1/8.2 report; no second
  sandbox trace format is introduced and existing `data-*` attributes remain
  stable.
- Keep every control local-only in the browser: no execute button, no approval
  button, no real-action toggle, no sandbox path to `/execute`, and no desktop
  control API.
- Preserve disabled click/type/hotkey/scroll/switch_app permissions and
  `real_action_enabled = false` sandbox behavior.

## Phase 9: Minimal Sandbox Real-action Experiment Design

Status: design-only gate documented in
`docs/PHASE_9_MINIMAL_SANDBOX_EXPERIMENT_DESIGN.md`.

Goal: define the smallest future sandbox experiment shape while preserving
the current dry-run-only runtime.

- Select a very small deterministic subset of Phase 8.1 sandbox scenarios:
  dry-run success, real-action-disabled skip, missing approval, stale
  observation, high-risk target, missing audit plan, and missing action
  contract.
- Keep `dry_run = true`, `real_action_enabled = false`, and
  `real_action_attempted = false`.
- Simulate only a fixture-level low-risk target action. Do not perform real
  click/type/hotkey/scroll/switch_app and do not call `/execute`.
- Require Phase 7 gate validation before any simulated outcome.
- Block missing audit plan, missing action contract, high-risk target, stale
  observation, missing approval, invalid geometry, missing verification plan,
  and missing emergency stop.
- Define mock user approval and mock emergency stop hooks.
- Define mock post-action verification and mock rollback expectations.
- Preserve Phase 8 deterministic report fields, scenario fields, and audit
  event ordering.
- Require tests for no real desktop API imports, dry-run field completeness,
  blocker enforcement, Phase 7 gate behavior, and safety scan compatibility.
- Do not modify Execution Policy, Permission Profile, Capability Registry, or
  any permission matrix.
- Do not implement the real-action adapter yet.

## Phase 9.1: Minimal Sandbox Experiment Harness

Status: implemented as deterministic dry-run harness code.

Goal: execute the Phase 9 specification safely as fixture simulation before any
real-action adapter is considered.

- Define `Phase9ExperimentConfig`, `Phase9ExperimentRequest`,
  `Phase9ExperimentResult`, `MockApprovalState`,
  `MockEmergencyStopState`, `MockPostActionVerificationPlan`, and
  `MockRollbackPlan`.
- Keep `dry_run = true`, `real_action_enabled = false`, and
  `real_action_attempted = false` as the default safety posture.
- Reuse the Phase 7 gate validation through the existing Phase 8 sandbox
  framework, then add Phase 9 checks for allowed scenario ID, narrow sandbox
  scope, approval binding, inactive emergency stop, rollback planning, and
  disabled real-action state.
- Return only simulated `dry_run_completed`, `blocked`, or
  `real_action_skipped` outcomes.
- Emit deterministic Phase 9 audit events for request, mock approval check,
  emergency stop check, gate pass/block, verification planning, rollback
  planning, dry-run completion, and real-action skip.
- Preserve Phase 8 report fields through `build_phase9_experiment_report(...)`
  so future cockpit/debug surfaces can inspect expected versus actual outcome,
  failure reasons, blockers, audit order, dry-run state, skipped state,
  verification planning, target risk/confidence, readiness state, action type,
  notes, and trace.
- Block missing approval, missing emergency stop, active emergency stop,
  missing verification, missing rollback, missing target, missing action
  contract, missing audit plan, high-risk or unknown-risk target, stale
  observation, invalid geometry, low confidence, readiness failure, forbidden
  action type, broad sandbox scope, and any real-action-enabled request without
  a future separately approved gate.
- Do not add a cockpit endpoint, execute button, approval button, real-action
  toggle, sandbox action trigger, `/execute` call, desktop control dependency,
  or permission change.

## Phase 9.2: Phase 9 Harness Cockpit Display

Status: implemented as read-only cockpit debug integration.

Goal: make Phase 9.1 dry-run harness status inspectable in the cockpit without
adding any execution path.

- Expose deterministic Phase 9.1 harness scenarios through
  `GET /phase9-experiment/demo`.
- Keep the endpoint fixture-backed and deterministic; no live desktop
  observation, no understanding pass, no action execution, and no desktop
  control API.
- Display experiment ID/name, scenario name, gate status, actual outcome,
  dry-run state, real-action-enabled state, real-action-skipped state, failure
  reason codes, blocker codes, mock approval checked/present state, emergency
  stop state, post-action verification planning, rollback planning, sandbox
  scope, target risk/confidence, readiness state, action type, notes, and the
  Phase 9 audit event sequence.
- Keep the cockpit panel read-only: no execute button, approval button,
  real-action toggle, click/type/hotkey/scroll/switch_app control, sandbox
  action trigger, `/execute` call, or action-performing endpoint.
- Preserve disabled click/type/hotkey/scroll/switch_app permissions and
  `real_action_enabled = false` default behavior.

## Phase 9.3: Phase 9 Advanced Audit Timeline UX

Status: implemented as read-only cockpit UX polish.

Goal: make Phase 9 audit traces easier to inspect without changing the
deterministic report shape or adding execution permission.

- Keep using the Phase 9.1 report fields exposed by the Phase 9.2 endpoint.
- Add local-only audit timeline grouping by scenario, gate status, blocker
  severity, and event type.
- Preserve original audit order with rendered metadata while allowing
  scenario-first local display ordering.
- Add expandable event detail rows for event name, scenario ID, gate status,
  blocker/failure codes, mock approval state, emergency stop state,
  verification planning, rollback planning, dry-run state, and skipped state.
- Add event chips for request, approval check, emergency stop check, gate
  pass/block, verification planning, rollback planning, dry-run completion,
  and real-action skip.
- Keep all controls browser-local: no execute button, approval button,
  real-action toggle, sandbox action trigger, `/execute` call, or
  action-performing endpoint.
- Preserve disabled click/type/hotkey/scroll/switch_app permissions and
  `real_action_enabled = false` default behavior.

## Phase 10: Limited Desktop Control

Goal: consider narrow desktop control only after the Phase 7 checklist and
Phase 9 dry-run design plus Phase 9.1 harness gates are satisfied and
separately approved.

- Enable click, type, hotkey, and scroll only as individually gated
  capabilities.
- Keep each action type behind permission profile checks.
- Keep user approval for risky actions.
- Keep post-action verification.
- Never enable broad autonomous execution by default.
- Maintain a safe fallback path when confidence, validation, or verification
  fails.

## Historical Drafts

The following untracked historical drafts predate v0.3 and should not be treated
as current safety policy:

- `docs/agent-console-v0.md`
- `docs/lain-mouse-agent-implementation-roadmap.md`
- `docs/lain-mouse-agent-prototype-spec.md`

They may describe broad mouse or keyboard execution as a future or prototype
goal. Current v0.3 behavior is stricter: wait is the only executable action,
click/type/hotkey/scroll/switch_app remain disabled, and the AI Planner is
proposal-only.
