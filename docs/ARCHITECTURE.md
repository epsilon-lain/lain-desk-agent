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
invalid geometry, missing post-action verification, forbidden action types,
out-of-scope targets, readiness blockers, and missing emergency stop. Each
scenario reports pass/fail, gate status, failure reason codes, audit event
names, dry-run status, real-action-enabled status, real-action-skipped status,
post-action verification planning, and validation-check trace data.

Phase 8.1 remains fixture-only. It does not observe the live desktop, does not
call `/execute`, does not add UI controls, does not change Capability Registry,
Permission Profile, or Execution Policy, and does not import any desktop
control API.

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
