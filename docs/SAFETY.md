# Safety Gate v0

Safety Gate v0 classifies a proposal before any actuation is connected.

It does not execute actions. It only returns one decision:

- `allowed`
- `needs_approval`
- `blocked`

## Flow

```text
proposal
-> assess_proposal(proposal)
-> safety_decision
```

The `/proposal` endpoint returns the decision next to the proposal:

```json
{
  "proposal": {},
  "safety_decision": {
    "decision": "allowed",
    "reason": "This proposal is read-only and does not execute desktop input.",
    "risk": "low"
  }
}
```

## v0 rules

- `no_op` and `target_hint` are allowed because they are read-only.
- `click`, `type`, `hotkey`, `scroll`, `submit`, `send`, and `delete` are
  blocked because executable input actions are outside the current phase.
- Any proposal marked `requires_approval: true`, `risk: medium`, or
  `risk: high` returns `needs_approval` unless the action type is directly
  blocked.
- Unknown action types are blocked.

Safety Gate v0 intentionally arrives before Actuation. This keeps the project
honest: every future action type must pass through a visible decision point
before it can affect the desktop.
