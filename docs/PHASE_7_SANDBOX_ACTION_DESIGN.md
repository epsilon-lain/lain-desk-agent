# Phase 7 Sandbox Action Design Gate

Phase 7 is a design-only gate for a future sandboxed real-action experiment.
It does not implement desktop control, does not enable any new permission, and
does not change the current wait-only execution model.

## Purpose

Define the minimum safety requirements that must exist before any future
Phase 8 sandbox action experiment can perform real desktop input.

The design covers:

- Permission gates
- Explicit user approval
- Visible target confirmation
- Audit events
- Readiness blockers
- Post-action verification
- Failure handling and rollback expectations
- The narrow sandbox scope for a first experiment

## Non-goals

Phase 7 does not:

- Implement real click, type, hotkey, scroll, or app switching.
- Enable real desktop action permissions.
- Add desktop control libraries or platform input APIs.
- Modify Capability Registry, Permission Profile, Execution Policy, or any
  permission matrix to allow real actions.
- Expand autonomous behavior.
- Add hidden or background actions.
- Create a general desktop automation agent.

## Hard Safety Boundaries

These boundaries remain active through Phase 7:

- `wait` is the only executable action.
- `click`, `type`, `type_text`, `hotkey`, `press`, `scroll`, and `switch_app`
  remain disabled.
- Preview-only contracts are never executable.
- Click Readiness is a blocker and diagnostic layer, not execution permission.
- Safety Gate, Action Contract, Capability Registry, Permission Profile, and
  Execution Policy remain separate gates.
- No real desktop control dependency may be imported or called.
- No hidden, background, or off-screen action may be performed.
- Dry-run and preview-only behavior remain the default.

## Allowed Future Sandbox Scope

Any Phase 8 experiment must be limited to all of the following:

- One explicitly created test window only.
- One explicitly marked test target only.
- One low-risk action type only, selected in the Phase 8 proposal.
- Deterministic local fixture or mock target first.
- No system settings.
- No file deletion.
- No shell execution.
- No browser credential fields.
- No external websites unless explicitly mocked or locally hosted.
- No destructive actions.
- No hidden or background actions.
- No action outside the visible viewport.

The first acceptable target should be an inert local test surface such as a
dedicated fixture window whose only state change is safe to verify.

## Explicitly Forbidden Actions

The following are forbidden for the sandbox experiment:

- Typing into password, token, credential, payment, or personal-data fields.
- Clicking send, submit, delete, remove, pay, buy, confirm, login, or similar
  high-risk controls.
- Changing system settings.
- Deleting, moving, renaming, overwriting, or uploading files.
- Running shell commands.
- Launching or switching apps as a real action.
- Interacting with external websites.
- Performing actions when the target is hidden, disabled, stale, ambiguous, or
  outside the declared viewport.
- Performing actions after approval expires or the observation changes.
- Retrying automatically after a failed action.

## Required Permission Gates

Before any future sandbox action can execute, all gates must pass in order:

1. Safety Gate classifies the proposal as low risk.
2. Action Contract is non-preview and explicitly scoped to the sandbox action.
3. Capability Registry has that exact action enabled for sandbox mode only.
4. Permission Profile explicitly allows that exact action in sandbox mode only.
5. Execution Policy lists that exact action as executable for the active
   sandbox profile.
6. Click Readiness, or the matching readiness policy for the chosen action,
   returns `ready: true`.
7. User approval is present, explicit, current, and tied to the same contract.
8. Audit logging succeeds before execution.
9. Emergency stop is still unset immediately before execution.

Failure at any gate must block execution and record an audit event.

## Required User Approval Flow

Approval must be explicit and specific. A generic prior approval is not enough.

The approval UI must show:

- The action type.
- The target label, role, source, confidence, risk hint, bbox, and center.
- A visual target overlay or equivalent visible target confirmation.
- The current app/window identity.
- The observation timestamp and freshness status.
- The exact expected state change.
- The fact that the action is real, not preview-only.

Approval must:

- Be a separate user action from proposal generation.
- Bind to one action contract ID.
- Expire when the observation becomes stale.
- Expire when bbox, center, target ID, target label, or active window changes.
- Be revocable through emergency stop before execution.
- Never approve batches or chains of actions.

## Required Audit Events

The following audit events must exist before any Phase 8 real-action adapter:

- `sandbox_action.proposed`
- `sandbox_action.readiness_checked`
- `sandbox_action.approval_requested`
- `sandbox_action.approved`
- `sandbox_action.rejected`
- `sandbox_action.execution_requested`
- `sandbox_action.execution_blocked`
- `sandbox_action.executed`
- `sandbox_action.post_observation_created`
- `sandbox_action.verified`
- `sandbox_action.verification_failed`
- `sandbox_action.rollback_requested`
- `sandbox_action.rollback_completed`
- `sandbox_action.rollback_failed`
- `sandbox_action.emergency_stopped`

Each event must include:

- Timestamp
- Run ID
- Proposal ID
- Action contract ID
- Action type
- Target ID and label
- Target bbox and center
- Safety decision
- Readiness status and blocker codes
- Permission profile
- Execution policy profile
- User approval status
- Result status

Audit logging failure must block execution.

## Required Readiness Blockers

The future sandbox experiment must continue to honor structured readiness
blockers from Phase 6.5, including:

- `stale_observation`
- `missing_target`
- `missing_bbox`
- `invalid_bbox`
- `missing_center`
- `bbox_center_mismatch`
- `out_of_viewport`
- `coordinate_space_unknown`
- `dpi_uncertain`
- `low_confidence_target`
- `hidden_or_disabled_target`
- `ambiguous_target`
- `high_risk_requires_approval`
- `action_not_enabled_by_policy`

Any blocker means execution is not allowed.

## Required Post-action Verification

Every future sandbox action must be followed by verification.

Verification must:

- Capture a post-action observation or screenshot.
- Compare the post-action state to an explicit expected state change.
- Confirm the target surface is still the sandbox test window.
- Confirm no forbidden surface received input.
- Record success or failure in the audit log.
- Never infer success only because the action API returned without error.

If verification cannot run, the action must be treated as failed.

## Failure Handling And Rollback

The sandbox experiment must define rollback before execution exists.

Minimum expectations:

- Failure to pass any gate blocks execution.
- Failure to write the pre-action audit log blocks execution.
- Failure during execution triggers emergency-stop state.
- Failure after execution requires post-action observation.
- Failed verification records `sandbox_action.verification_failed`.
- Rollback must be explicit, audited, and limited to the same sandbox target.
- Rollback must not use broader permissions than the original action.
- No automatic retry is allowed.
- The system must return to dry-run mode after a failure.

For the first experiment, rollback should preferably be "reset the local test
fixture" rather than another desktop action.

## Emergency Stop Behavior

Emergency stop must:

- Be visible in the cockpit.
- Be checked before execution.
- Be checked after user approval and immediately before the action.
- Block all non-wait actions when active.
- Record `sandbox_action.emergency_stopped`.
- Force the system back to dry-run mode.
- Prevent retries until the user explicitly clears it.

## Exit Criteria Before Implementation

Phase 8 real-action implementation may not begin until all of these are true:

- This design is reviewed and accepted.
- The allowed sandbox target is specified.
- The single action type is specified.
- The expected state change is specified.
- Permission gate changes are designed but not enabled by default.
- Audit event schemas are designed.
- Readiness blocker behavior is tested for the sandbox target.
- Post-action verification is designed.
- Rollback behavior is designed.
- Emergency stop behavior is designed.
- CI safety scan still forbids broad desktop-control imports.
- Dry-run remains the default mode.

## Phase 8 Dry-run Skeleton Note

Phase 8 may introduce a dry-run-only framework that validates this gate before
any real desktop input exists. That framework must keep `dry_run` true by
default, keep `real_action_enabled` false by default, emit structured
`sandbox_experiment_*` audit events, and skip any non-dry-run request while no
separately approved adapter exists.

The dry-run skeleton is not a permission change. It does not satisfy the
real-action exit criteria by itself, and it must not import or call desktop
control APIs.

## Phase 8.1 Evaluation Note

Phase 8.1 may add deterministic fixture scenarios and trace summaries for this
gate. Those scenarios are allowed only to validate dry-run, blocked, and
real-action-skipped outcomes. They may report Phase 7 checklist state, failure
reason codes, readiness blocker codes, audit event ordering, target risk,
target confidence, and post-action verification planning.

Phase 8.1 evaluation is not execution permission. A passing sandbox evaluation
does not enable click/type/hotkey/scroll/switch_app and does not satisfy the
real-action checklist below by itself.

## Checklist Before Any Phase 8 Real-action Experiment

Before implementing real actuation inside a minimal sandbox experiment:

- [ ] Confirm no real actions are enabled in the default profile.
- [ ] Confirm the experiment uses one test window only.
- [ ] Confirm the experiment uses one test target only.
- [ ] Confirm the target is low risk.
- [ ] Confirm the target is visible and inside the viewport.
- [ ] Confirm bbox, center, coordinate space, and DPI checks pass.
- [ ] Confirm observation freshness passes with an injectable clock.
- [ ] Confirm ambiguous targets are blocked.
- [ ] Confirm hidden or disabled targets are blocked.
- [ ] Confirm high-risk targets require approval and remain blocked for the
      first sandbox experiment.
- [ ] Confirm explicit user approval binds to one action contract.
- [ ] Confirm pre-action audit logging is required.
- [ ] Confirm post-action observation or screenshot verification is required.
- [ ] Confirm emergency stop blocks execution.
- [ ] Confirm rollback/reset is defined.
- [ ] Confirm no shell, file deletion, settings, credential fields, or external
      websites are involved.
- [ ] Confirm `scripts/safety_scan.py` passes.
- [ ] Confirm `scripts/verify.ps1` passes.

## Design Verdict

Phase 7 is only a gate. It authorizes no implementation and no permission
change. Phase 8 real-action behavior remains blocked until the checklist above
is satisfied and a separate implementation proposal is approved.
