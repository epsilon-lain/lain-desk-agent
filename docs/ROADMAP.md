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

## Phase 7: Click Readiness Hardening

Status: started with structured readiness checks for preview-only click
contracts, center/bbox consistency checks, Cockpit visibility for readiness
diagnostics, and copy-friendly debug summaries.

Goal: make preview-only click contracts safer before any real click experiment.

- Strengthen high-risk label policy.
- Add stale observation checks.
- Add coordinate and DPI checks.
- Improve bbox and center validation.
- Consume preview-contract target schema fields such as role, source,
  confidence, timestamp, and `target_risk_hint`.
- Show structured readiness diagnostics in the Cockpit for live proposals and
  planner evaluation reports.
- Provide copy-friendly read-only readiness debug summaries for blocked click
  previews.
- Keep real click disabled by default.
- Keep click readiness as a blocker, not a permission grant.

## Phase 8: Sandboxed Real-action Experiment

Goal: design a tightly bounded experiment before any limited real desktop
action exists.

- Start only after explicit design approval.
- Prefer an internal or local safe target first.
- Keep the experiment behind Capability Registry, Permission Profile, explicit
  user approval, and Execution Policy.
- Require post-action observation and verification.
- Record audit events for every request, block, execution, and verification.
- Do not broaden the default product behavior.

## Phase 9: Limited Desktop Control

Goal: consider narrow desktop control only after Phase 7 is reliable.

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
