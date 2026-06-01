# Safety

Current version: v0.3 guarded wait-only cockpit + proposal-only AI Planner.

Mirai is a supervised local cockpit for observing, understanding, proposing,
previewing, and testing a narrow wait-only execution path. It is intentionally
conservative. The project currently has no real mouse or keyboard desktop
control.

## Current Hard Boundary

- No real mouse or keyboard desktop control.
- `wait` is the only executable action.
- `click`, `type`, `type_text`, `hotkey`, `press`, `scroll`, and `switch_app`
  are disabled and non-executable.
- `/execute` accepts only approved wait contracts.
- `/proposal` never executes desktop input.
- Preview-only contracts are never executable.
- Click Readiness is a blocker and diagnostic surface, not permission to click.
- AI Planner output is proposal-only.
- LLM output is validated before it can become a proposal.
- Screenshots, `screenshot_path`, and `image_bytes` are not sent to the LLM.
- API keys and secrets must not be committed, logged, or pasted into docs.

## Proposal And Safety Flow

```text
observation / demo state
-> understanding
-> planner context
-> rule-based or proposal-only AI planner
-> validate proposal
-> Safety Gate
-> preview-only Action Contract
-> Click Readiness diagnostics
```

Allowed proposal-only action types:

- `no_op`
- `target_hint`
- `switch_app_hint`

Executable action types are not valid AI Planner outputs. Unsafe or malformed AI
output becomes a safe `no_op`.

## Safety Gate

Safety Gate classifies proposals before any execution path can be considered.

Decision values:

- `allowed`
- `needs_approval`
- `blocked`

Current rules:

- `no_op`, `target_hint`, and `switch_app_hint` are read-only proposal actions.
- Executable action proposals such as `click`, `type`, `hotkey`, `press`,
  `scroll`, `send`, `delete`, `submit`, `launch_app`, and executable
  `switch_app` are rejected.
- Unknown action types are blocked.
- Higher-risk read-only proposals can require approval, but approval records an
  audit event only. It does not execute the proposal.

## Action Contracts

Action Contracts are preview-first descriptions of possible future actions.

Current preview contracts:

- `target_hint` may produce a preview-only `click` contract.
- `switch_app_hint` may produce a preview-only `switch_app` contract.

Important: preview-only contracts are never executable. A preview-only click
contract means "this is the area a future click might target," not "click is
allowed."

## Click Readiness

Click Readiness explains why a preview-only click contract is not executable.

It currently checks:

- contract exists and is a click contract
- contract is not preview-only
- contract has not already executed
- bbox exists and is well-formed
- bbox is inside screen bounds when screen bounds are available
- center point is well-formed
- observation is fresh when timestamp is available
- click capability is enabled and executable
- permission profile allows click
- Safety Gate did not block
- target label is not high-risk

Current behavior:

- Preview-only click contracts always block readiness.
- Disabled click capability blocks readiness.
- Permission profile blocks click readiness.
- High-risk labels such as send/delete/pay/confirm/password/login block
  readiness.
- Missing, malformed, out-of-bounds, or stale geometry blocks readiness.

Readiness diagnostics are read-only. They do not grant permission and do not
change execution policy.

## Capability Registry And Permission Profile

Capability Registry currently marks:

- `wait`: enabled and executable
- `click`, `type`, `type_text`, `hotkey`, `press`, `scroll`, `switch_app`:
  disabled and non-executable

Permission profiles:

- `safe_readonly`: no actions executable
- `wait_only`: only `wait` executable
- `experimental_desktop_control`: defined for future design work, but still
  does not enable mouse or keyboard control

## Execution Policy

The Execution Policy Matrix exposes how each action type behaves across
permission profiles. It is read-only policy data. It does not enable execution.

Current executable action list under the default profile:

- `wait`

Everything else remains blocked.

## AI Planner Boundary

Default planner mode is `rule_based`.

Optional `ai_proposal` mode:

- requires `LAIN_AGENT_PLANNER_MODE=ai_proposal`
- requires `OPENAI_API_KEY`
- sends only compact planner context
- does not send screenshot bytes, screenshot paths, or secrets
- accepts only `no_op`, `target_hint`, and `switch_app_hint`
- validates all output before creating a proposal
- falls back safely on invalid or unsafe output

## Demo And Evaluation Harness

Demo scenarios and planner evaluation are read-only.

They do not:

- call `observe()`
- take screenshots
- use OCR
- control the desktop
- call OpenAI
- execute actions

They exercise the same proposal, safety, action contract, and click readiness
surfaces using fake UI states.

## Manual Safety Checks

Before committing safety-sensitive changes, run:

```powershell
python -m compileall src tests
python -m unittest discover -s tests
node --check ui/app.js
python scripts/safety_scan.py
git diff --check
```

Verify `/execute` still rejects click contracts with HTTP `403`.

Search for accidental desktop actuation additions:

```powershell
python scripts/safety_scan.py
```

The scan should report no forbidden runtime desktop actuation calls under
`src/`.
