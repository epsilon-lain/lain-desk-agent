# lain-desk-agent architecture

Version: v0.3 guarded wait-only cockpit

This document captures the current safety model for the local Mirai cockpit. The system is designed to be observable, explainable, and heavily gated before any desktop control is expanded. In v0.3, the only executable action is `wait`.

## Current pipeline

The intended guarded loop is:

```text
Task
-> observe
-> understand
-> propose
-> safety_decision
-> action_contract
-> click_readiness if click
-> capability/profile check
-> wait-only execute
-> post-observe
-> verify
-> events
```

In practice, this is split across two read-only and execution paths:

1. Planning path: `GET /proposal`

```text
task query
-> observe()
-> understand(observation)
-> propose(ui_state + task)
-> safety_decision
-> preview-only action_contract when possible
-> click_readiness for preview click contracts
-> action_contract.created event when a contract exists
-> JSON response
```

The planning path does not execute desktop input. It may identify a target, create a preview-only contract, and explain safety/readiness, but it does not move, click, type, press keys, scroll, or launch apps.

2. Execution path: `POST /execute`

```text
action_contract
-> action.execution_requested event
-> Capability Registry check
-> Permission Profile check
-> wait-only actuation
-> action.executed or action.blocked event
-> post-execution observe()
-> wait-only verify_execution(...)
-> action.verified or action.verification_failed event
-> JSON response
```

The execution path rejects non-wait actions, rejects `preview_only` contracts, and only executes a `wait` contract whose status is `approved_for_execution` and whose `executed` value is `false`.

## Components

### Observation

Observation captures a local read-only snapshot: screenshot, cursor position, active window metadata, screen size, snapshot files, and audit events. It does not control the mouse or keyboard.

### Understanding

Understanding turns an observation into `ui_state`. Current perception is OCR-first and exposes fields such as `app_guess`, `state_guess`, `screen`, `visible_text`, `visible_text_boxes`, and normalized `visible_elements`.

`visible_elements` use the `VisibleElement` schema from `observer.py`:

- `id`: unique string
- `label` and `text`: trimmed, lowercase, punctuation-stripped text
- `role`: normalized role such as `text` or `button`
- `bbox`: `{x, y, width, height}` integer screen coordinates
- `center`: `{x, y}` derived from `bbox`
- `confidence`: float from `0` to `1`
- `source`: `ocr`, `ui_tree`, or `manual`
- `risk_hint`: `normal`, `high_risk`, or `unknown`
- `timestamp`: ISO8601 observation time

Malformed, out-of-bounds, unlabeled, or non-normalized candidates are not used as grounded elements. This prevents partial OCR or fixture data from becoming target candidates.

The `ui_tree` source is currently a fixture-friendly read-only adapter. It
accepts plain dictionaries such as `name`, `control_type`, and
`bounding_rectangle`, then normalizes them through the same `VisibleElement`
schema. It does not call live accessibility automation or desktop input APIs.
Hidden or disabled `ui_tree` nodes are retained only as low-confidence debug
grounding with `risk_hint: "unknown"`, so they do not become planner targets.

### Planner

Planner proposes conservative read-only actions:

- `target_hint` when a visible element appears relevant
- `switch_app_hint` when the task names a different app than the current `app_guess`
- `no_op` when no reliable next step exists

Planner consumes the normalized `VisibleElement` fields only. Low-confidence elements are ignored, ambiguous same-label matches become `no_op`, and high-risk labels are marked as approval-gated proposal hints. The optional AI planner receives the same compact schema and rejects low-confidence target hints during local validation. Planner does not produce executable click/type actions.

### Safety Gate

Safety Gate classifies proposals as:

- `allowed`
- `needs_approval`
- `blocked`

This decision is surfaced in the UI and recorded with approval/reject audit events. Approval logging does not execute an action.

### Action Contract

Action Contract converts some proposals into future-facing contracts:

- `target_hint` with normalized `bbox`, `center`, `role`, `source`, `confidence`, `risk_hint`, and `timestamp` becomes a preview-only `click` contract
- `switch_app_hint` becomes a preview-only `switch_app` contract
- `no_op` produces no contract

Current contracts from planning are `preview_only` and are never executable.
An Action Contract describes a possible future action shape; it is not
execution permission. Execution eligibility is determined only after separate
Safety Gate, Readiness, Capability Registry, Permission Profile, Execution
Policy, user approval, audit, and verification requirements are satisfied.

### Capability Registry

Capability Registry centralizes action support:

- `wait`: enabled and executable, risk `low`
- `click`: disabled and not executable
- `type` / `type_text`: disabled and not executable
- `hotkey` / `press`: disabled and not executable
- `scroll`: disabled and not executable
- `switch_app`: disabled and not executable

Disabled actions return blocked responses with registry reasons.

### Permission Profile

Permission Profile adds a second runtime gate:

- `safe_readonly`: no actions executable
- `wait_only`: only `wait` executable
- `experimental_desktop_control`: named for future work, but currently still does not enable mouse or keyboard actions

The default profile is `wait_only`.

### Click Readiness Policy

Click Readiness Policy decides whether a click contract could ever become eligible for real click execution. In v0.3 it always blocks real click readiness because:

- planning creates `preview_only` click contracts
- click capability is disabled
- the current permission profile does not allow click

It also blocks high-risk labels such as `send`, `submit`, `delete`, `pay`, `confirm`, `password`, `login`, `发送`, `删除`, `支付`, `确认`, `密码`, and `登录`.

Readiness consumes the same target schema fields carried by the preview contract. It checks bbox shape, screen bounds, center consistency, observation freshness, disabled click capability, permission profile, Safety Gate result, and high-risk labels or `target_risk_hint`. A passing readiness diagnostic still would not execute in v0.3 because click capability and permission remain disabled.

Readiness is theoretical pre-execution diagnostics. It can explain or block a
future action, but it does not grant execution permission and it does not
override Action Contract status, Capability Registry, Permission Profile, or
Execution Policy.

### Actuation

Actuation v0 supports only `wait`.

The action must be:

- `type == "wait"`
- `status == "approved_for_execution"`
- `executed == false`
- allowed by Capability Registry
- allowed by Permission Profile

Wait duration is capped to a safe maximum. No mouse or keyboard APIs are called for actuation.

### Verification

Verification v0 supports wait-only execution. After an approved wait executes, the backend captures a post-execution observation and verifies:

- execution result status is `executed`
- execution result type is `wait`
- post-observation exists

Expected UI change for wait is `none`.

### Runtime Status

Runtime Status exposes a compact read-only summary:

- mode: `local`
- desktop control: disabled
- actuation: `wait_only`
- verification: enabled
- permission profile
- capabilities
- click readiness
- resource guard limits

### Event Viewer

Event Viewer reads recent audit events from the current run. Common events include:

- `observation.created`
- `action_contract.created`
- `proposal.approved`
- `proposal.rejected`
- `snapshot.deleted`
- `action.execution_requested`
- `action.executed`
- `action.blocked`
- `action.verified`
- `action.verification_failed`

### Resource Guard

Resource Guard prevents local snapshots from growing forever and fails safely when disk space is too low.

Current limits:

- `max_observations_per_run = 100`
- `max_run_size_mb = 300`
- `min_free_disk_mb = 1024`

Cleanup only scans the current run directory, deletes old `obs_XXXX.png` and `obs_XXXX.json` pairs, and never deletes `events.jsonl`.

### Phase 7 Sandbox Design Gate

Phase 7 is documentation and design only. It defines the required gates for a
future minimal sandbox action experiment, including explicit approval, visible
target confirmation, structured readiness blockers, audit events, post-action
verification, rollback expectations, emergency stop behavior, and a one-window
one-target sandbox scope.

Phase 7 does not implement real desktop control and does not change Capability
Registry, Permission Profile, Execution Policy, or any permission matrix.
Any real-action Phase 8 adapter remains blocked until the Phase 7 checklist in
`docs/PHASE_7_SANDBOX_ACTION_DESIGN.md` is satisfied and separately approved.

### Phase 8 Sandbox Experiment Framework

Phase 8 adds `sandbox_experiment.py` as a dry-run framework, not an actuation
layer. It defines a named sandbox experiment request/result shape, validates
the Phase 7 gate inputs, records structured audit event payloads, and returns
simulated outcomes.

The framework requires an explicit experiment name, user approval flag, target
from normalized `visible_elements`, fresh observation timestamp, low-risk
target, valid bbox/center/viewport geometry, click readiness or explicitly
expected dry-run blocker behavior, an action contract, post-action
verification plan, emergency stop availability, and a one-window/one-target
sandbox scope.

`dry_run` is true by default and `real_action_enabled` is false by default.
When a non-dry-run request reaches the framework, it emits
`sandbox_real_action_skipped` and sets `real_action_attempted: false` because no
real desktop adapter exists. This framework does not call `/execute`, does not
change Capability Registry, Permission Profile, or Execution Policy, and does
not import any desktop control API.

### Phase 8.1 Sandbox Evaluation

Phase 8.1 adds `sandbox_evaluation.py` as a deterministic report and trace
layer for the dry-run sandbox framework. It builds fixture-backed
`SandboxExperimentConfig` and `SandboxExperimentRequest` pairs, runs them
through `run_sandbox_experiment(...)`, and summarizes expected versus actual
outcomes.

The evaluation covers dry-run success, real-action skip, missing approval,
stale observations, high-risk and unknown-risk targets, low-confidence targets,
invalid bbox, bbox/center mismatch, missing viewport or coordinate metadata,
missing post-action verification, forbidden action types, out-of-scope targets,
readiness blockers, missing emergency stop, missing audit plan, missing action
contract, and missing target.

Each scenario reports `scenario_id`, `scenario_name`, expected outcome, actual
outcome, pass/fail, gate status, failure reason codes, readiness blocker codes,
audit event names, dry-run status, real-action-enabled status,
real-action-skipped status, post-action verification planning, target risk
hint, target confidence, readiness state, action type, notes, and
validation-check trace data.

Phase 8.1 remains fixture-only. It does not observe the live desktop, does not
call `/execute`, does not add UI controls or real-action triggers, does not
change Capability Registry, Permission Profile, or Execution Policy, and does
not import any desktop control API.

### Phase 8.2 Sandbox Evaluation Cockpit Trace

Phase 8.2 exposes the existing Phase 8.1 sandbox evaluation report in the
cockpit through `GET /sandbox-evaluation/demo`. The endpoint calls
`evaluate_sandbox_experiment_scenarios(...)` and returns the same deterministic
report shape; it does not observe the live desktop, understand a screen,
execute an action contract, or call `/execute`.

The cockpit panel is read-only debug output. It displays scenario name,
expected versus actual outcome, pass/fail, gate status, failure reason codes,
readiness blocker codes, audit event names, dry-run status,
real-action-enabled status, real-action-skipped status, post-action
verification planning, target risk/confidence, readiness state, action type,
notes, and trace JSON. It does not provide approve, execute, real-action
toggle, click/type/hotkey/scroll/switch_app, or sandbox action trigger
controls.

Phase 8.2 is not execution permission. It does not change Capability Registry,
Permission Profile, Execution Policy, Action Contract behavior, Click
Readiness, or the Phase 7 gate. It only makes deterministic gate behavior
inspectable before any future real-action adapter is considered.

### Phase 8.3 Sandbox Trace Cockpit UX

Phase 8.3 keeps the Phase 8.2 cockpit endpoint and Phase 8.1 report format
unchanged, then improves only the read-only presentation layer. The sandbox
trace panel filters the deterministic report by fixture set, pass/fail state,
scenario type, and blocker code. It also shows summary counts, stable
scenario-level trace fields, collapsible scenario details, and sequential audit
event views.

All Phase 8.3 controls are local display controls. Filtering, expand/collapse,
and audit timeline rendering operate on the already loaded JSON report. They
do not call `/execute`, do not record approvals, do not change
`real_action_enabled`, do not mutate Capability Registry, Permission Profile,
Execution Policy, Action Contract behavior, or Click Readiness, and do not
import any desktop control API.

### Phase 8.4 Sandbox Trace UX Polish

Phase 8.4 keeps the Phase 8.1 report format and Phase 8.2 cockpit endpoint
stable, then improves only cockpit readability. The sandbox trace panel now
uses clearer status chips, blocker severity styling, inline blocker
descriptions, compact summary cards, clearer filter-empty states, and more
legible audit event chips.

Phase 8.4 is still read-only/debug-only. The polish helpers operate on the
already loaded deterministic report in the browser. They do not call
`/execute`, do not record approvals, do not expose real-action toggles, do not
change `real_action_enabled`, do not mutate Capability Registry, Permission
Profile, Execution Policy, Action Contract behavior, or Click Readiness, and
do not import any desktop control API.

### Phase 8.5 Sandbox Trace UX Refinements

Phase 8.5 keeps the Phase 8.1 report format, Phase 8.2 endpoint, and existing
`data-*` attributes stable. It refines only the cockpit presentation layer with
blocker-group quick filters, reset filters, copy visible summary, text mini
bars, and grouped scenario sections.

All Phase 8.5 behavior is local to the browser after the deterministic report
has been loaded. Quick filters, reset filters, scenario grouping, text bars,
and copy summary controls do not call `/execute`, do not record approvals, do
not call action-performing endpoints, do not expose real-action toggles, do not
change `real_action_enabled`, do not mutate Capability Registry, Permission
Profile, Execution Policy, Action Contract behavior, or Click Readiness, and
do not import any desktop control API.

### Phase 9 Minimal Sandbox Experiment Design

Phase 9 is design-only and documented in
`docs/PHASE_9_MINIMAL_SANDBOX_EXPERIMENT_DESIGN.md`. It defines the smallest
future sandbox experiment shape but does not implement real desktop control.
The design remains dry-run-only: `dry_run` stays true by default,
`real_action_enabled` stays false, and `real_action_attempted` must remain
false for every scenario.

The Phase 9 design selects a tiny deterministic subset of existing Phase 8.1
sandbox scenarios: dry-run success, real-action-disabled skip, missing
approval, stale observation, high-risk target, missing audit plan, and missing
action contract. Each scenario must pass through the Phase 7 gate before any
simulated result is returned. Missing audit plan, missing action contract,
high-risk target, stale observation, missing approval, invalid geometry,
missing verification, or missing emergency stop blocks the experiment.

Phase 9 defines mock user approval, mock emergency stop, mock post-action
verification, and mock rollback only. It preserves the Phase 8 deterministic
report shape, including scenario ID/name, expected and actual outcome, failure
reason codes, blocker codes, audit event names, dry-run state,
real-action-enabled state, real-action-skipped state, post-action verification
planning, target risk/confidence, readiness state, action type, notes, and
trace.

Phase 9 does not call `/execute`, does not add action-performing endpoints, does
not add cockpit execute/approval/real-action controls, does not mutate
Capability Registry, Permission Profile, Execution Policy, Action Contract
behavior, or Click Readiness, and does not import any desktop control API.

### Phase 9.1 Minimal Sandbox Experiment Harness

Phase 9.1 implements `phase9_experiment.py` as a deterministic dry-run harness
for the Phase 9 design. It is not a real-action adapter. The harness defines
`Phase9ExperimentConfig`, `Phase9ExperimentRequest`, `Phase9ExperimentResult`,
mock approval state, mock emergency stop state, mock post-action verification,
and mock rollback plans.

The harness reuses the Phase 8 `validate_phase7_gate(...)` implementation for
Phase 7 checks, then adds Phase 9-specific validation for the minimal scenario
subset, one-window/one-target sandbox scope, approval binding, inactive
emergency stop, rollback planning, and disabled real-action state. It returns
only simulated `dry_run_completed`, `blocked`, or `real_action_skipped`
outcomes, and it always reports `real_action_attempted: false`.

Phase 9.1 emits Phase 8-compatible scenario report fields through
`build_phase9_experiment_report(...)`, including expected and actual outcome,
failure reason codes, blocker codes, audit event names, dry-run state,
real-action-skipped state, verification planning, target risk/confidence,
readiness state, action type, notes, and trace. Its audit event names are
Phase 9-specific debug events such as `phase9_experiment_requested`,
`phase9_gate_passed`, `phase9_gate_blocked`,
`phase9_post_action_verification_planned`, `phase9_rollback_plan_recorded`,
`phase9_dry_run_completed`, and `phase9_real_action_skipped`.

Phase 9.1 does not add a cockpit endpoint, does not add UI controls, does not
call `/execute`, does not observe the live desktop, does not change Capability
Registry, Permission Profile, Execution Policy, Action Contract behavior, or
Click Readiness, and does not import any desktop control API.

### Phase 9.2 Phase 9 Harness Cockpit Display

Phase 9.2 exposes the existing Phase 9.1 dry-run harness report in the cockpit
through `GET /phase9-experiment/demo`. The endpoint calls
`evaluate_phase9_experiment_scenarios(...)` and returns deterministic fixture
data only. It does not observe the live desktop, understand a screen, execute
an action contract, or call `/execute`.

The cockpit panel is read-only debug output for Phase 9 harness status. It
shows experiment ID/name, scenario name, dry-run state, real-action-enabled
state, real-action-skipped state, gate status, actual outcome, failure reason
codes, blocker codes, mock approval checked/present state, emergency stop
availability, post-action verification planning, rollback planning, sandbox
scope, target risk/confidence, readiness state, action type, notes, and the
Phase 9 audit event timeline.

Phase 9.2 does not add approve, execute, real-action toggle, click/type/
hotkey/scroll/switch_app, or sandbox action trigger controls. It does not
change Capability Registry, Permission Profile, Execution Policy, Action
Contract behavior, Click Readiness, or the Phase 7 gate.

### Phase 9.3 Phase 9 Advanced Audit Timeline UX

Phase 9.3 keeps the Phase 9.1 report fields and Phase 9.2 cockpit endpoint
stable, then improves only browser-side audit inspection. The Phase 9 cockpit
can group the already loaded audit events by scenario, gate status, blocker
severity, or event type, and it preserves original event ordering through
rendered metadata. Scenario and event detail rows show mock approval,
emergency stop, verification, rollback, gate status, blockers, failure reasons,
and dry-run/skipped state.

All Phase 9.3 controls are local display controls. Sorting, grouping, and
expand/collapse operate on the deterministic `/phase9-experiment/demo` JSON
after it has loaded. They do not call `/execute`, do not record approvals, do
not add real-action toggles, do not change Capability Registry, Permission
Profile, Execution Policy, Action Contract behavior, Click Readiness, or the
Phase 7 gate, and do not import any desktop control API.

### Phase 9.4 Phase 9 Report Export And Reproducibility Bundle

Phase 9.4 keeps the Phase 9.1 scenario report shape and the Phase 9.2
read-only endpoint stable, then derives an export bundle from that deterministic
report. The bundle includes a stable export report, an AI-readable handoff
summary, minimal reproduction metadata, audit event order, blocker/failure
codes, and a safety-boundary statement.

The export is for debugging, handoff, reproducibility, and AI-assisted review.
It avoids private auth material, live OS state, broad filesystem dumps, and
real desktop screenshots outside deterministic fixture data. Cockpit controls
copy the already loaded report, JSON export, or reproducibility bundle from
browser memory only. They do not call `/execute`, do not record approvals, do
not mutate runtime state, do not add real-action toggles, and do not alter
Capability Registry, Permission Profile, Execution Policy, Action Contract
behavior, Click Readiness, or the Phase 7 gate.

### Phase 9.5 Phase 9 Bundle Import And Replay

Phase 9.5 adds read-only import validation and replay for Phase 9.4
reproducibility bundles. Backend helpers validate required bundle/report
fields, safety-boundary text, audit timeline ordering, blocker/failure code
shape, dry-run state, real-action-disabled state, and suspicious sensitive-key
names before producing a deterministic replay report.

Replay is not execution. `validate_phase9_reproducibility_bundle(...)`,
`import_phase9_reproducibility_bundle(...)`, and
`replay_phase9_reproducibility_bundle(...)` inspect only the provided JSON-like
object. They do not read local files, crawl the filesystem, observe live OS
state, execute code, call action-performing endpoints, or change Capability
Registry, Permission Profile, Execution Policy, Action Contract behavior, Click
Readiness, or the Phase 7 gate.

The cockpit import/replay panel is browser-local. Users paste bundle JSON into
a textarea, validate it, replay the deterministic audit timeline, and copy a
replay report or AI-readable summary from browser memory. The panel does not
upload bundles, add approval or execute controls, record approvals, mutate
runtime state, or create a real-action trigger.

### Phase 9.6 Replay Validation Hardening

Phase 9.6 treats imported Phase 9 bundles as untrusted debug input and hardens
the existing Phase 9.5 validation format instead of creating a second replay
schema. Validation now includes deeper consistency checks for report version,
project phase, dry-run state, real-action-disabled state, skipped-state
consistency, gate/outcome consistency, failure and blocker code relationships,
audit event ordering, approval/emergency/verification/rollback state, target
risk and confidence, readiness and blockers, sandbox scope, action type, and
safety-boundary text.

The validation result includes structured errors, warnings, unsafe flag
findings, consistency check records, audit-order check records, sensitive-key
findings, read-only replay eligibility, and a recommended debug focus derived
only from validation findings and existing blocker/failure codes. The cockpit
shows these details as read-only chips, counts, and expandable JSON/debug
details. Phase 9.6 still does not upload bundles, observe the live desktop,
read local files, execute code, call action-performing endpoints, record
approvals, or modify any execution policy.

### Phase 9.7 Replay Validation Cockpit UX Polish

Phase 9.7 keeps the Phase 9.5/9.6 replay data shape and validation semantics
stable, then improves only the browser-side cockpit display. The replay panel
adds compact validation summary cards, local validation issue filters,
expandable issue groups for errors, warnings, unsafe flags, audit order,
sensitive key findings, consistency checks, and recommended debug focus, plus
copy helpers for validation summary, validation errors, debug focus, and replay
validation JSON.

All Phase 9.7 controls operate on already loaded in-memory replay validation
data. They do not upload bundles, fetch new execution data, record approvals,
mutate runtime state, call action-performing endpoints, or change replay
eligibility. Imported bundles remain untrusted input, and the cockpit remains
read-only/debug-only.

### Phase 9.8 Replay Validation Cockpit UX Polish

Phase 9.8 continues the replay validation cockpit polish while preserving the
Phase 9.5/9.6 replay data shape and Phase 9.7 read-only display behavior. The
cockpit includes explicit Phase 9 replay validation hooks, a validation health
strip, local-only validation filters, grouped issue sections, expand/collapse
controls, and copy helpers for validation summary, validation errors,
recommended debug focus, and replay validation JSON.

The Phase 9.8 UI reads only from the already-loaded bundle import/replay state
held in browser memory. It does not change replay semantics, upload imported
bundles, call action-performing endpoints, record approvals, mutate runtime
state, or alter Execution Policy, Permission Profile, Capability Registry,
Action Contract behavior, Click Readiness, or the Phase 7 gate.

### AI Handoff, Export, Import, And Replay Pipeline

The Phase 9 handoff pipeline is a read-only state-transfer/debug pipeline:

```text
deterministic Phase 9 report
-> export report
-> AI-readable summary
-> reproducibility bundle
-> local pasted import
-> validation of untrusted input
-> deterministic replay report
-> cockpit display and copy helpers
```

This pipeline is for reproducibility, debugging, regression review, and AI
handoff. It is not AI control and it is not execution permission. Imported
bundles are untrusted input. Validation errors do not mutate runtime state.
Replay is read-only. Copy/export controls read already loaded browser or
deterministic fixture state only.

### Safety Invariants Summary

The current release-candidate safety invariants are documented in
`docs/SAFETY_INVARIANTS.md`. In brief:

- no real desktop APIs in runtime paths
- no sandbox or replay `/execute` path
- no execute button, real-action approval button, sandbox action trigger, or
  real-action toggle
- `dry_run` remains default
- `real_action_enabled` remains false by default
- imported bundles are untrusted input
- readiness is not permission
- proposal is not execution
- cockpit display is not authorization
- Execution Policy, Permission Profile, and Capability Registry remain
  separate from readiness and report display

### Phase 10 Readiness Boundary

Phase 10 real actions are not implemented yet. Current Phase 10 work is
readiness and release-candidate hardening only: documentation, tests,
auditability, AI handoff quality, deterministic dry-run parity, and regression
protection.

Any future Phase 10 experiment must satisfy
`docs/PHASE_10_READINESS_CHECKLIST.md` and receive a separate user request.
Passing readiness diagnostics, replay validation, report export, imported
bundle validation, or cockpit display never grants execution permission.

### Phase 10.1 Readiness Report And Cockpit Panel

Phase 10.1 adds `src/lain_desk_agent/phase10_readiness.py` as a deterministic
readiness report builder. The module returns static, documentation-oriented
GO/NO-GO data for future Phase 10 work. The default is intentionally NO-GO:
`dry_run = true`, `read_only = true`, `debug_only = true`,
`real_actions_enabled = false`, `phase10_real_actions_implemented = false`,
and `go_for_phase10 = false`.

`GET /phase10-readiness/demo` exposes that report to the cockpit. The endpoint
does not observe the live desktop, inspect live OS state, read secrets, mutate
runtime state, call `/execute`, or call any action-performing endpoint.

The cockpit panel displays project phase, dry-run/read-only/debug-only status,
real-action-disabled status, no-go reasons, required gates, readiness checks,
safety invariants, forbidden actions/APIs, important files, verification
commands, recommended next work, and an AI handoff summary. Its controls are
local display and copy helpers only: group filter, expand/collapse, copy AI
handoff, copy readiness JSON, copy no-go reasons, and copy safety invariants.

Phase 10.1 readiness is not permission. Cockpit display is not authorization.
Export/import/replay is not execution. AI handoff is not AI control.

### Phase 10.2 Global Status Cockpit And AI Handoff Dashboard

Phase 10.2 adds `src/lain_desk_agent/phase10_global_status.py` as a
deterministic global status report builder. It summarizes the current
Phase 10 readiness state, project health, safety invariants, Phase 9
export/import/replay validation state, verification command expectations,
important docs/runtime files, current cockpit capabilities, no-go reasons, and
recommended next work.

`GET /phase10-global-status/demo` exposes the report to the cockpit. The
endpoint does not observe the live desktop, inspect live OS state, read private
runtime material, mutate state, call `/execute`, or call any action-performing
endpoint.

The cockpit panel displays a NO-GO status chip, dry-run/read-only/debug-only
state, real actions disabled state, Phase 10 implementation state, completed
phases, no-go reasons, safety boundary, safety invariants, forbidden
actions/APIs, verification commands, important docs/runtime files, Phase 9
validation state, recommended next work, and AI handoff summary. Its controls
are local display and copy helpers only: show-all/readiness/safety/docs/
verification/AI-handoff/no-go filters, expand/collapse, and copy helpers for
already loaded text or JSON.

Phase 10.2 does not grant execution permission. Readiness is not permission.
Cockpit display is not authorization. Export/import/replay is not execution.
AI handoff is not AI control. Real desktop actions remain disabled.

## Safety boundaries

The current safety boundaries are intentionally narrow:

- `wait` is the only executable action.
- `click`, `type`, `type_text`, `hotkey`, `press`, `scroll`, and `switch_app` are disabled.
- Click readiness exists, but real click readiness is blocked in v0.3.
- Click readiness is not execution permission.
- Action Contract and Execution Policy remain separate gates.
- `preview_only` contracts are never executable.
- Phase 8 sandbox experiments are dry-run or explicitly skipped; they are not
  execution permission.
- Phase 8.1 sandbox evaluation is a deterministic trace report, not an
  execution path.
- Phase 8.2 sandbox evaluation cockpit trace is read-only debug output, not an
  execution path.
- Phase 8.3 sandbox trace filters and detail controls are read-only display
  controls, not execution controls.
- Phase 8.4 sandbox trace readability polish is read-only display logic, not
  execution permission.
- Phase 8.5 sandbox trace quick filters, grouping, reset, text bars, and copy
  summary controls are read-only display helpers, not execution permission.
- Phase 9 minimal sandbox experiment design is dry-run-only and design-only;
  it is not execution permission.
- Phase 9.1 minimal sandbox experiment harness is dry-run-only simulation;
  it is not execution permission and it never attempts real desktop action.
- Phase 9.2 Phase 9 harness cockpit display is read-only debug output; it is
  not execution permission and it never attempts real desktop action.
- Phase 9.3 Phase 9 advanced audit timeline UX is browser-local read-only
  display logic; it is not execution permission and it never attempts real
  desktop action.
- Phase 9.4 Phase 9 report export and reproducibility bundle is read-only
  state-transfer/debug data; it is not execution permission and it never
  attempts real desktop action.
- Phase 9.5 Phase 9 bundle import and replay is read-only validation/debug
  output; it is not execution permission and it never attempts real desktop
  action.
- Phase 9.6 Phase 9 replay validation hardening is read-only validation/debug
  output for untrusted imported bundles; it is not execution permission and it
  never attempts real desktop action.
- Phase 9.7 Phase 9 replay validation cockpit UX polish is browser-local
  read-only display and copy logic; it is not execution permission and it never
  attempts real desktop action.
- Phase 9.8 Phase 9 replay validation cockpit UX polish is browser-local
  read-only filtering, grouping, expand/collapse, and copy logic; it is not
  execution permission and it never attempts real desktop action.
- Phase 10 readiness / release-candidate hardening is documentation, tests,
  auditability, AI handoff, and dry-run regression protection only; Phase 10
  real actions are not implemented yet.
- Phase 10.1 readiness cockpit is read-only/debug-only and reports NO-GO by
  default; it is not execution permission and it never attempts real desktop
  action.
- Phase 10.2 global status cockpit is read-only/debug-only and reports NO-GO
  handoff context; it is not authorization, execution permission, or AI
  control, and it never attempts real desktop action.
- Approval and rejection only record audit events.
- The UI may show a dry-run preview and screenshot overlay, but it does not interact with the desktop.
- There is no real mouse or keyboard desktop control.
- There is no app launching.
- There is no DOM extraction or LLM call path in the current cockpit flow.

## Endpoints

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/observation` | GET | Capture and return a read-only observation snapshot. |
| `/understanding` | GET | Capture an observation and return `ui_state`. |
| `/proposal` | GET | Capture, understand, propose, assess safety, build preview contracts, and return read-only planning data. |
| `/approval` | POST | Record proposal approval or rejection as an audit event. |
| `/events` | GET | Return recent events from the current run. |
| `/capabilities` | GET | Return the Capability Registry. |
| `/permission-profile` | GET | Return the active permission profile and known profiles. |
| `/click-readiness` | GET | Return static click readiness policy metadata. |
| `/runtime/status` | GET | Return the current runtime safety summary. |
| `/sandbox-evaluation/demo` | GET | Return deterministic Phase 8.1 sandbox evaluation trace for cockpit display; no observation or execution. |
| `/phase9-experiment/demo` | GET | Return deterministic Phase 9.1 dry-run harness trace for cockpit display; no observation or execution. |
| `/phase10-readiness/demo` | GET | Return deterministic Phase 10.1 readiness report for cockpit display; no observation or execution. |
| `/phase10-global-status/demo` | GET | Return deterministic Phase 10.2 global status and AI handoff report for cockpit display; no observation or execution. |
| `/execute` | POST | Execute only approved wait contracts and verify them. |

## Development rule

Future changes should preserve this order of expansion:

```text
read-only perception
-> target proposal
-> safety decision
-> preview-only action contract
-> capability/profile/readiness gates
-> minimal actuation
-> post-observation verification
```

Do not enable mouse or keyboard control by adding a bbox, an approval button, or a capability name alone. A real desktop action needs an explicit action type, enabled capability, allowed permission profile, non-preview contract status, safety clearance, readiness clearance, audit trail, and verification plan.
