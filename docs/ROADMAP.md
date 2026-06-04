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

## Phase 9: Limited Desktop Control

Goal: consider narrow desktop control only after the Phase 8 dry-run framework
is reliable and the Phase 7 real-action checklist is satisfied.

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
