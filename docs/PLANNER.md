# Planner Proposal v0

Planner Proposal v0 creates one conservative next-action proposal from the
current UI state. It is proposal-only and read-only: it never executes the
proposed action.

## Flow

```text
GET /proposal
-> observe()
-> understand(observation)
-> propose(ui_state)
-> return ui_state + proposal
```

## Output

```json
{
  "proposal_id": "proposal_0001",
  "source_ui_state_id": "state_0001",
  "action": {
    "type": "wait_for_user",
    "target": "current_window",
    "parameters": {},
    "reason": "The current page appears to require login. The agent should not handle login.",
    "risk": "high",
    "requires_approval": true
  }
}
```

The HTTP endpoint returns:

```json
{
  "ui_state": {},
  "proposal": {}
}
```

## Rules

Planner v0 is deterministic and rule-based:

- If `state_guess` is `browser_window` and the active window title or summary
  suggests a login flow, propose `wait_for_user` with `risk: high`.
- Otherwise propose `no_op` with `risk: low` and reason
  `No reliable next action yet.`

## Boundaries

Planner Proposal v0 does not use:

- LLMs
- OCR
- AI vision
- Safety Gate
- Actuation
- Verification
- Mouse or keyboard control

It does not add executable `click`, `type`, `hotkey`, or `scroll` actions.
