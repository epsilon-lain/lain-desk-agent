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

## Completed

- Observation / Understanding
- Planner Context Bundle
- Rule-based Planner
- Proposal-only AI Planner
- AI Planner test harness
- AI Planner runtime status fields
- Planner Trace
- Planner Evaluation Harness
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

Status: started with compact visible-element normalization and high-risk label
hints.

Goal: improve `visible_elements` without adding desktop control.

- Normalize planner-context visible elements into a stable compact shape:
  `id`, `label`/`text`, `type`/`kind`, `bbox`, `confidence`, `source`, and
  `risk_hint`.
- Keep OCR/demo/accessibility-stub sources explicitly marked as read-only
  grounding.
- Add an accessibility source, DOM source, or improved OCR source.
- Keep every grounding source read-only.
- Improve visible element labels, bounding boxes, confidence scores, and source
  metadata.
- Keep planner inputs compact.
- Continue excluding screenshot bytes and screenshot paths from LLM payloads.

## Phase 6: Click Readiness Hardening

Goal: make preview-only click contracts safer before any real click experiment.

- Strengthen high-risk label policy.
- Add stale observation checks.
- Add coordinate and DPI checks.
- Improve bbox and center validation.
- Keep real click disabled by default.
- Keep click readiness as a blocker, not a permission grant.

## Phase 7: Sandboxed Real-action Experiment

Goal: design a tightly bounded experiment before any limited real desktop
action exists.

- Start only after explicit design approval.
- Prefer an internal or local safe target first.
- Keep the experiment behind Capability Registry, Permission Profile, explicit
  user approval, and Execution Policy.
- Require post-action observation and verification.
- Record audit events for every request, block, execution, and verification.
- Do not broaden the default product behavior.

## Phase 8: Limited Desktop Control

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
