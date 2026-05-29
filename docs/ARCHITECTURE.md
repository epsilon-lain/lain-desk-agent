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

Understanding turns an observation into `ui_state`. Current perception is OCR-first and exposes fields such as `app_guess`, `state_guess`, `visible_text`, `visible_text_boxes`, and `visible_elements`.

### Planner

Planner proposes conservative read-only actions:

- `target_hint` when a visible element appears relevant
- `switch_app_hint` when the task names a different app than the current `app_guess`
- `no_op` when no reliable next step exists

Planner does not produce executable click/type actions.

### Safety Gate

Safety Gate classifies proposals as:

- `allowed`
- `needs_approval`
- `blocked`

This decision is surfaced in the UI and recorded with approval/reject audit events. Approval logging does not execute an action.

### Action Contract

Action Contract converts some proposals into future-facing contracts:

- `target_hint` with a bbox becomes a preview-only `click` contract
- `switch_app_hint` becomes a preview-only `switch_app` contract
- `no_op` produces no contract

Current contracts from planning are `preview_only` and are never executable.

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

## Safety boundaries

The current safety boundaries are intentionally narrow:

- `wait` is the only executable action.
- `click`, `type`, `type_text`, `hotkey`, `press`, `scroll`, and `switch_app` are disabled.
- Click readiness exists, but real click readiness is blocked in v0.3.
- `preview_only` contracts are never executable.
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
