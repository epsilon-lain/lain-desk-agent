# API reference

Version: v0.3 guarded wait-only cockpit

This document describes the current local HTTP API. The API is intentionally conservative: planning is read-only, action contracts are preview-first, and execution is limited to approved `wait` contracts.

## Safety summary

- `/execute` only supports approved `wait` contracts.
- `click`, `type`, `type_text`, `hotkey`, `press`, `scroll`, and `switch_app` are not executable.
- `preview_only` action contracts are never executable.
- There is no real mouse or keyboard desktop control.
- Approval/rejection records audit events only; it does not execute an action.

## GET /observation

Purpose: Capture and return a read-only observation snapshot.

Method: `GET`

Parameters: none.

Important response fields:

- `observation_id`
- `timestamp`
- `active_window`
- `screen`
- `screen.screenshot_path`
- `cursor`

Safety notes:

- Captures a screenshot and metadata only.
- Does not move, click, type, press keys, scroll, or launch apps.
- Uses Resource Guard before/after snapshot creation.
- Appends `observation.created` to the run event log.

## GET /understanding

Purpose: Capture an observation and convert it into a read-only `ui_state`.

Method: `GET`

Parameters: none.

Important response fields:

- `ui_state_id`
- `source_observation_id`
- `app_guess`
- `state_guess`
- `summary`
- `confidence`
- `visible_text`
- `visible_text_boxes`
- `visible_elements`

Safety notes:

- Read-only perception path.
- Does not infer executable controls beyond the current understanding model.
- Does not execute proposals or actions.

## GET /proposal?task=...

Purpose: Capture, understand, propose one conservative next step, assess safety, and build preview-only action metadata when possible.

Method: `GET`

Query parameters:

- `task`: optional user task text.

Important response fields:

- `ui_state`
- `proposal`
- `proposal.proposal_id`
- `proposal.action`
- `proposal.action.type`
- `proposal.action.reason`
- `proposal.action.risk`
- `proposal.action.requires_approval`
- `action_contract`
- `safety_decision`
- `click_readiness`

Current proposal action types:

- `target_hint`
- `switch_app_hint`
- `no_op`

Safety notes:

- Does not execute anything.
- `target_hint` can become a preview-only `click` action contract.
- `switch_app_hint` can become a preview-only `switch_app` action contract.
- Preview-only contracts are not executable.
- If the action contract is a click contract, `click_readiness` explains why real click execution is blocked.

Example request:

```text
GET http://127.0.0.1:8000/proposal?task=Search
```

Example PowerShell:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/proposal?task=Search"
```

## POST /approval

Purpose: Record an approval or rejection decision for a proposal.

Method: `POST`

Body fields:

- `decision`: `"approved"` or `"rejected"`
- `proposal_id`
- `proposal`
- `safety_decision`
- `task`: optional task text

Important response fields:

- `status`: `"recorded"`

Safety notes:

- Records `proposal.approved` or `proposal.rejected`.
- Does not execute the proposal.
- Does not change action contract status.
- Does not move, click, type, press keys, scroll, or launch apps.

## GET /events?limit=...

Purpose: Return recent audit events from the current run.

Method: `GET`

Query parameters:

- `limit`: optional number of events to return. Defaults to 20 and is capped by the server.

Important response fields:

- `events`
- `events[].type`
- `events[].timestamp`

Common event types:

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

Safety notes:

- Read-only event log endpoint.
- Missing event files return an empty event list.
- Malformed JSON lines are skipped safely.

## GET /capabilities

Purpose: Return the current Capability Registry.

Method: `GET`

Parameters: none.

Important response fields:

- `capabilities.wait.enabled`
- `capabilities.wait.executable`
- `capabilities.click.enabled`
- `capabilities.type.enabled`
- `capabilities.hotkey.enabled`
- `capabilities.scroll.enabled`
- `capabilities.switch_app.enabled`
- each capability's `risk` and `reason`

Safety notes:

- `wait` is enabled and executable.
- `click`, `type`, `type_text`, `hotkey`, `press`, `scroll`, and `switch_app` are disabled and not executable.
- This endpoint reports policy; it does not change policy.

## GET /permission-profile

Purpose: Return the active execution permission profile and known profile definitions.

Method: `GET`

Parameters: none.

Important response fields:

- `profile`
- `default_profile`
- `profiles.safe_readonly`
- `profiles.wait_only`
- `profiles.experimental_desktop_control`

Safety notes:

- Default profile is `wait_only`.
- `safe_readonly` allows no executable actions.
- `wait_only` allows only `wait`.
- `experimental_desktop_control` exists as a named profile but does not enable mouse or keyboard actions.
- This endpoint reports policy; it does not switch profiles.

## GET /click-readiness

Purpose: Return static Click Readiness Policy metadata.

Method: `GET`

Parameters: none.

Important response fields:

- `enabled`
- `reason`
- `required_checks`
- `high_risk_labels`

Safety notes:

- `enabled` is currently `false`.
- Real click execution is not enabled.
- High-risk labels such as send, submit, delete, pay, confirm, password, login, and Chinese equivalents are blocked by policy.

## GET /runtime/status

Purpose: Return a compact read-only summary of the runtime safety state.

Method: `GET`

Parameters: none.

Important response fields:

- `runtime.mode`
- `runtime.desktop_control`
- `runtime.actuation`
- `runtime.verification`
- `permission_profile`
- `capabilities`
- `click_readiness.enabled`
- `click_readiness.reason`
- `resource_guard.enabled`
- `resource_guard.max_observations_per_run`
- `resource_guard.max_run_size_mb`
- `resource_guard.min_free_disk_mb`

Safety notes:

- Read-only summary endpoint.
- Reports that desktop control is disabled.
- Reports wait-only actuation and enabled verification.

Example request:

```text
GET http://127.0.0.1:8000/runtime/status
```

Example PowerShell:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/runtime/status"
```

## POST /execute

Purpose: Execute an approved wait-only action contract and verify it with a post-execution observation.

Method: `POST`

Body fields:

- `action_contract`: action contract object
- `task`: optional task/audit text

The body may also be a direct action contract object.

Approved wait contract fields:

- `action_id`
- `type`: must be `"wait"`
- `parameters.duration_ms`
- `status`: must be `"approved_for_execution"`
- `executed`: must be `false`

Important success response fields:

- `status`
- `type`
- `duration_ms`
- `executed`
- `execution_result`
- `verification_result`
- `post_observation_id`

Important blocked response fields:

- `status`: `"blocked"`
- `reason`
- `executed`: `false`

Safety notes:

- Only `wait` can execute.
- Wait duration is capped by the backend.
- `preview_only` contracts are rejected.
- `click`, `type`, `type_text`, `hotkey`, `press`, `scroll`, and `switch_app` contracts are rejected.
- Rejected actions do not trigger verification.
- Approved wait execution appends execution and verification events.
- No real mouse or keyboard desktop control exists.

Example request:

```powershell
$body = @{
  action_contract = @{
    action_id = "manual_wait_0001"
    type = "wait"
    parameters = @{ duration_ms = 1000 }
    status = "approved_for_execution"
    executed = $false
  }
  task = "wait self-test"
} | ConvertTo-Json -Depth 6

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/execute" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```
