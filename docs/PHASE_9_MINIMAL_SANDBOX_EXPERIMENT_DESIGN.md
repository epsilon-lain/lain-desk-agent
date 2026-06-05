# Phase 9 Minimal Sandbox Real-Action Experiment Design

Phase 9 is a design-only specification for the smallest future sandbox
experiment shape. It does not implement real desktop control, does not enable
new permissions, and does not add any action-performing endpoint.

The word "real-action" in this phase name describes the future experiment
category being designed, not current runtime behavior. The Phase 9 design can
only be executed as dry-run simulation.

## Purpose

Define a minimal, reviewable sandbox experiment plan that can validate the
Phase 7 gate, mock approval, mock emergency stop, audit trace, and mock
post-action verification before any real desktop action adapter exists.

Phase 9 is intended to answer:

- Which deterministic sandbox scenarios are allowed in the first experiment?
- Which Phase 7 gates must block unsafe paths?
- Which audit and report fields must be emitted?
- How should rollback and emergency stop behave while the experiment remains
  simulation-only?
- Which tests must prove that no real desktop actuation path exists?

## Non-goals

Phase 9 does not:

- Implement real click, type, hotkey, scroll, or app switching.
- Add pyautogui, pynput, keyboard, mouse, win32api input calls, ctypes
  SendInput/mouse_event, xdotool, AppleScript UI scripting, or any other real
  desktop control API.
- Call `/execute` from sandbox trace or sandbox experiment paths.
- Add execute buttons, approval buttons, real-action toggles, or sandbox action
  triggers to the cockpit.
- Do not modify Execution Policy, Permission Profile, Capability Registry, or
  any permission matrix.
- Create a second sandbox evaluation/report format.
- Perform hidden, background, off-screen, destructive, external website, shell,
  file deletion, or credential-field actions.

## Hard Defaults

All Phase 9 experiment specs must keep:

- `dry_run = true` by default.
- `real_action_enabled = false` by default.
- `real_action_attempted = false` for every scenario.
- `real_desktop_actions = false` for every report.
- The existing Phase 8.1/8.2 report fields and trace shape.
- The current wait-only production execution model.

Any non-dry-run request while `real_action_enabled = false` must return a
skipped/simulated result and must not call any action-performing endpoint.

## Minimal Scenario Scope

The initial Phase 9 design scope is a tiny subset of existing deterministic
Phase 8.1 sandbox scenarios. These scenarios are enough to exercise the happy
path, safe skip path, and mandatory Phase 7 blockers without introducing new
live desktop dependencies.

Allowed design subset:

| Scenario ID | Purpose | Expected behavior |
| --- | --- | --- |
| `dry_run_success_all_gates_pass` | Simulate the only eligible low-risk target path. | Gate passes, dry-run completes, no real action attempted. |
| `real_action_disabled_skips_non_dry_run` | Prove non-dry-run remains skipped while real actions are disabled. | Gate passes, real action is skipped, no real action attempted. |
| `missing_user_approval_blocks` | Prove mock approval is required. | Gate blocks with `missing_user_approval`. |
| `stale_observation_blocks` | Prove freshness is mandatory. | Gate blocks with `stale_observation`. |
| `high_risk_target_blocks` | Prove high-risk targets cannot enter the experiment. | Gate blocks with `high_risk_target` and approval/risk blocker codes. |
| `missing_audit_plan_blocks` | Prove audit planning is mandatory. | Gate blocks with `missing_audit_plan`. |
| `missing_action_contract_blocks` | Prove an action contract is mandatory. | Gate blocks with `missing_action_contract`. |

No additional scenarios may be added to Phase 9 without updating this design
and the deterministic tests.

## Simulated Target Action

The experiment may simulate only one target action:

- Action type: `click` as a fixture-level action contract type only.
- Target: one normalized visible element from the fixture.
- Target risk: `normal` only.
- Target confidence: must satisfy the existing sandbox threshold.
- Geometry: valid bbox, center, viewport, coordinate-space, and DPI metadata.
- Readiness: `ready: true` or an explicitly expected dry-run blocker behavior.

Simulation means:

- No OS mouse movement.
- No OS click.
- No typing.
- No hotkey.
- No scrolling.
- No app switching.
- No `/execute` call.
- No actuation adapter call.

The simulated result may state that the target would have been selected inside
the sandbox fixture, but it must not change desktop state.

## Mock Approval Hook

Phase 9 may define a mock approval hook for deterministic scenarios:

```text
mock_user_approval = {
  present: boolean,
  action_contract_id: string,
  approved_at: ISO8601 timestamp,
  expires_at: ISO8601 timestamp,
  observation_id: string,
  target_id: string
}
```

Rules:

- Missing mock approval blocks.
- Approval must bind to the same action contract and target.
- Approval must expire when observation freshness fails.
- Approval must not imply permission to execute.
- Approval must never be represented as a real cockpit approval button.

## Mock Emergency Stop Hook

Phase 9 may define a mock emergency stop hook:

```text
mock_emergency_stop = {
  available: boolean,
  active: boolean,
  checked_at: ISO8601 timestamp
}
```

Rules:

- Missing emergency stop availability blocks.
- Active emergency stop blocks.
- Emergency stop must be checked before any simulated action result.
- Emergency stop records a blocker/audit path only; it does not control real
  desktop state because no real action exists.

## Phase 7 Gate Integration

Every Phase 9 experiment scenario must pass through Phase 7 validation before
any simulated outcome is returned.

The gate must require:

- Explicit experiment name.
- `dry_run` recorded.
- `real_action_enabled` recorded and false by default.
- Target from normalized `visible_elements`.
- Current observation freshness.
- Low-risk target only.
- Valid bbox, center, viewport, coordinate-space, and DPI metadata.
- Click readiness ready, or an explicitly expected dry-run blocker behavior.
- Action contract present and scoped to the target.
- Mock user approval present and bound to the contract.
- Audit plan present.
- Mock post-action verification plan present.
- Mock emergency stop available and inactive.
- Sandbox scope limited to one test window and one test target.
- Forbidden action list respected.

Mandatory blockers:

- Missing audit plan blocks.
- Missing action contract blocks.
- High-risk target blocks.
- Unknown-risk target blocks.
- Stale observation blocks.
- Missing user approval blocks.
- Missing post-action verification blocks.
- Missing emergency stop blocks.
- Invalid geometry blocks.
- Low confidence blocks.
- Outside sandbox scope blocks.

When the gate blocks, the experiment must stop immediately and must not produce
a simulated action completion event.

## Report Shape

Phase 9 output must match the Phase 8 deterministic report fields. It must not
create a second sandbox trace format.

Top-level report fields:

- `report_type`
- `phase`
- `source`
- `external_llm_calls`
- `real_desktop_actions`
- `scenario_count`
- `scenario_ids`
- `summary`
- `report_notes`
- `scenarios`

Each scenario must include:

- `scenario_id`
- `scenario_name`
- `expected_outcome`
- `actual_outcome`
- `passed`
- `gate_passed`
- `failure_reason_codes`
- `blocker_codes`
- `audit_event_names`
- `dry_run`
- `real_action_enabled`
- `real_action_skipped`
- `post_action_verification_planned`
- `target_risk_hint`
- `target_confidence`
- `readiness_ready`
- `action_type`
- `notes`
- `trace`

`actual_outcome.real_action_attempted` must always be false in Phase 9 design
execution.

## Audit Events

Phase 9 design execution must reuse the existing Phase 8 sandbox experiment
audit event names for deterministic trace compatibility:

- `sandbox_experiment_requested`
- `sandbox_gate_passed`
- `sandbox_gate_blocked`
- `sandbox_post_action_verification_planned`
- `sandbox_dry_run_completed`
- `sandbox_real_action_skipped`

Sequential audit requirements:

- Every scenario starts with `sandbox_experiment_requested`.
- A passing gate records `sandbox_gate_passed`.
- A blocked gate records `sandbox_gate_blocked` and stops.
- A passing dry-run with verification planning records
  `sandbox_post_action_verification_planned`.
- A completed dry-run records `sandbox_dry_run_completed`.
- A non-dry-run request while real actions are disabled records
  `sandbox_real_action_skipped`.

Audit records must include scenario ID, expected outcome, actual outcome,
failure reason codes, blocker codes, dry-run state, real-action-enabled state,
target risk/confidence, readiness status, and action type.

## Mock Post-action Verification

Phase 9 may include mock post-action verification only:

```text
mock_post_action_verification = {
  planned: boolean,
  simulated: true,
  expected_state_change: string,
  observed_state_change: string,
  passed: boolean
}
```

Rules:

- Missing verification plan blocks.
- Verification must be represented in `post_action_verification_planned`.
- Verification must not capture a live post-action desktop state.
- Verification must not infer success from an actuation API result because no
  actuation API is called.

## Rollback And Emergency Stop

Phase 9 rollback is mock-only.

If Phase 7 validation fails:

- Return `status: blocked`.
- Record the blocker/failure reason codes.
- Record `sandbox_gate_blocked`.
- Do not simulate an action completion.
- Do not call `/execute`.
- Do not change state outside the sandbox fixture.

If dry-run simulation fails after gate pass:

- Record a simulated failure outcome.
- Keep `real_action_attempted = false`.
- Mark mock verification failed if applicable.
- Record a mock rollback note in `notes` or `trace`.
- Keep all state changes inside the deterministic fixture payload.

Emergency stop expectations:

- Mock emergency stop active means block.
- Mock emergency stop missing means block.
- Emergency stop cannot enable rollback actuation.
- The system remains in dry-run mode after any failure.

## Test Requirements

Phase 9 design implementation, when added later, must include deterministic
tests that prove:

- No real desktop API imports or calls are introduced.
- No sandbox path calls `/execute`.
- No sandbox UI adds execute buttons, approval buttons, real-action toggles, or
  sandbox action triggers.
- `dry_run = true` and `real_action_enabled = false` remain defaults.
- Dry-run success reports every Phase 8 scenario field.
- Non-dry-run with `real_action_enabled = false` reports real-action skipped.
- Missing audit plan blocks.
- Missing action contract blocks.
- High-risk target blocks.
- Stale observation blocks.
- Mock approval is required.
- Mock emergency stop is required and blocks when active.
- Audit event ordering is deterministic.
- Mock post-action verification planning is recorded.
- `scripts/safety_scan.py` passes.
- `scripts/verify.ps1` passes.

## Implementation Guardrails

Before any Phase 9 code exists:

- Keep this document as the source of truth.
- Do not change Execution Policy, Permission Profile, Capability Registry, or
  any permission matrix.
- Do not add desktop control dependencies.
- Do not add action-performing endpoints.
- Do not add cockpit controls that suggest real execution.
- Keep Phase 8.1/8.2 report compatibility.

## Design Verdict

Phase 9 is approved only as a minimal dry-run design. It authorizes no real
desktop action implementation and no permission change. The first future Phase
9 implementation must be deterministic, fixture-backed, Phase 7-gated,
mock-approved, mock-emergency-stopped, mock-verified, and compatible with the
existing Phase 8 sandbox evaluation trace format.
