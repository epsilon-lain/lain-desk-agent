# Planner Proposal v1.1

Planner Proposal v1.1 creates one conservative next-step proposal from the
current UI state. It is proposal-only and read-only: it never executes the
proposed action and never emits executable desktop input such as `click`, `type`,
`hotkey`, or `submit`.

## Flow

```text
GET /proposal
-> observe()
-> understand(observation)
-> propose(ui_state)
-> assess_proposal(proposal)
-> return ui_state + proposal + safety_decision
```

## Output

```json
{
  "proposal_id": "proposal_0001",
  "source_ui_state_id": "state_0001",
  "action": {
    "type": "target_hint",
    "target": "element_0007",
    "target_element_id": "element_0007",
    "target_label": "search",
    "target_bbox": {
      "x": 120,
      "y": 240,
      "width": 80,
      "height": 24
    },
    "target_center": {
      "x": 160,
      "y": 252
    },
    "target_role": "text",
    "target_confidence": 0.86,
    "target_source": "ocr",
    "target_risk_hint": "normal",
    "target_timestamp": "2026-05-28T12:00:00Z",
    "parameters": {},
    "reason": "The task mentions text similar to 'search', and visible_elements contains a matching read-only text element with risk_hint 'normal'.",
    "risk": "low",
    "requires_approval": false
  }
}
```

The HTTP endpoint returns:

```json
{
  "ui_state": {},
  "proposal": {},
  "safety_decision": {}
}
```

## Rules

Planner v1.1 is deterministic and rule-based:

- If the task mentions a known target app and `app_guess` does not match it,
  propose `switch_app_hint` before considering visible elements.
- If `state_guess` is `browser_window` and the active window title or summary
  suggests a login flow, propose `wait_for_user` with `risk: high`.
- If a `task` query parameter is supplied, match task tokens against
  `visible_elements[*].label`. A confident match becomes a `target_hint`.
- If multiple same-label candidates are similarly confident, return `no_op`
  instead of guessing.
- If a target candidate has low confidence, including a hidden or disabled
  fixture `ui_tree` node, return `no_op` instead of targeting it.
- If a matched element has `risk_hint: "high_risk"`, keep the output
  proposal-only but mark it `risk: "high"` and `requires_approval: true`.
- If no task is supplied, only a small set of generic labels such as `Search`,
  `Find`, `OK`, `Done`, `Continue`, `Open`, `New`, or `Save` can become a
  `target_hint`.
- Otherwise propose `no_op` with `risk: low` and reason
  `No reliable next action yet.`

## Boundaries

Planner Proposal v1.1 does not use:

- LLMs
- AI vision
- Actuation
- Verification
- Mouse or keyboard control

It does not add executable `click`, `type`, `hotkey`, or `scroll` actions.
Planner reads `visible_elements` only; it does not care whether an element came
from OCR, fixture `ui_tree`, DOM, accessibility, or vision. Planner context keeps those elements
compact and normalized with `id`, `label`/`text`, `role`, `bbox`, `center`,
`confidence`, `source`, `risk_hint`, and `timestamp`. These fields improve
read-only grounding only; they do not enable execution.

The optional AI planner receives the same compact fields and local validation
rejects low-confidence, invalid-geometry, or ambiguous same-label
`target_hint` selections before they can become proposal actions.

## Planner Evaluation Expansion

Phase 6 expands the deterministic Planner Evaluation Harness while keeping the
system read-only and preview-only. The harness compares the rule-based planner
and deterministic AI proposal planner against fixture-defined expected
behavior, then runs each proposal through Safety Gate, Action Contract, Click
Readiness, and Execution Policy summaries.

The demo suite now covers:

- Normal safe `ui_tree` button
- Disabled or hidden `ui_tree` button
- Low-confidence target
- Ambiguous same-label targets
- High-risk manual or `ui_tree` target
- Invalid or missing bbox target
- Mixed manual plus `ui_tree` sources
- No visible target

Each scenario records the expected action type, risk, approval requirement,
preview-only contract behavior, readiness status, and blocker reason. Unsafe or
ambiguous states are expected to degrade to `no_op`, blocked readiness, or
preview-only output. No evaluation scenario grants execution permission, and
`wait` remains the only executable action.

## Click Readiness Hardening

Phase 6.5 hardens Click Readiness as a theoretical pre-execution check. It
does not permit real clicks and does not override Safety Gate, Action Contract,
Capability Registry, Permission Profile, or Execution Policy.

Readiness now reports stable blocker codes alongside human-readable reasons:

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

It also exposes target risk, target confidence, blocker details, and coordinate
debug fields for cockpit and evaluation reports. These diagnostics can only
block readiness or explain why a preview is not ready; they are never execution
permission.

## App mismatch hint

Planner detects simple app mentions in the task:

- `wechat`, `微信`, `weixin` -> `WeChat`
- `chrome`, `browser` -> `Chrome`
- `vscode`, `vs code`, `code` -> `VS Code`
- `notepad` -> `Notepad`
- `powershell`, `terminal` -> `PowerShell`

If the task asks for a different app than the active `app_guess`, Planner
returns:

```json
{
  "type": "switch_app_hint",
  "target": "WeChat",
  "parameters": {
    "current_app": "Chrome"
  },
  "reason": "The task mentions WeChat, but the active window appears to be Chrome. Switch to WeChat before planning the next step.",
  "risk": "low",
  "requires_approval": false
}
```

This is only a hint. It does not open, focus, move to, or control any app.

## Task hint

The HTTP endpoint accepts an optional read-only task hint:

```text
GET http://127.0.0.1:8000/proposal?task=Search
```

This lets Planner produce a target hint like:

```json
{
  "type": "target_hint",
  "target_element_id": "element_0007",
  "reason": "The task mentions text similar to 'search', and visible_elements contains a matching read-only text element with risk_hint 'normal'.",
  "risk": "low",
  "requires_approval": false
}
```
