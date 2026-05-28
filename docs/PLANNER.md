# Planner Proposal v1

Planner Proposal v1 creates one conservative next-step proposal from the current
UI state. It is proposal-only and read-only: it never executes the proposed
action and never emits executable desktop input such as `click`, `type`,
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
    "target_label": "Search",
    "target_bbox": {
      "x": 120,
      "y": 240,
      "width": 80,
      "height": 24
    },
    "parameters": {},
    "reason": "The task mentions text similar to 'Search', and visible_elements contains a matching read-only element.",
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

Planner v1 is deterministic and rule-based:

- If `state_guess` is `browser_window` and the active window title or summary
  suggests a login flow, propose `wait_for_user` with `risk: high`.
- If a `task` query parameter is supplied, match task tokens against
  `visible_elements[*].label`. A confident match becomes a `target_hint`.
- If no task is supplied, only a small set of generic labels such as `Search`,
  `Find`, `OK`, `Done`, `Continue`, `Open`, `New`, or `Save` can become a
  `target_hint`.
- Otherwise propose `no_op` with `risk: low` and reason
  `No reliable next action yet.`

## Boundaries

Planner Proposal v1 does not use:

- LLMs
- AI vision
- Actuation
- Verification
- Mouse or keyboard control

It does not add executable `click`, `type`, `hotkey`, or `scroll` actions.
Planner reads `visible_elements` only; it does not care whether an element came
from OCR, DOM, accessibility, or vision.

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
  "reason": "The task mentions text similar to 'Search', and visible_elements contains a matching read-only element.",
  "risk": "low",
  "requires_approval": false
}
```
