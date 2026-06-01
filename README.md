# lain-desk-agent

Mirai is a local, supervised desktop-agent cockpit for testing a guarded
observe-plan-preview loop. The current project is v0.3: a read-only cockpit
with wait-only execution and a proposal-only AI Planner path.

It is not an autonomous desktop controller. It does not provide real mouse or
keyboard control.

## Current State

The cockpit can:

- observe and understand the current desktop state
- build compact planner context
- produce rule-based or optional AI proposal-only suggestions
- validate proposals through Safety Gate
- create preview-only action contracts
- explain Click Readiness blockers with structured diagnostics
- compare rule-based and AI proposal outputs on built-in demo scenarios
- run an approved `wait` self-test
- show Runtime Status, Execution Policy, events, planner trace, and readiness
  debug summaries

Current proposal action types are:

- `no_op`
- `target_hint`
- `switch_app_hint`

Current executable action types:

- `wait` only, and only when the action contract is approved for execution

## Hard Safety Boundary

- No real mouse or keyboard desktop control.
- `click`, `type`, `type_text`, `hotkey`, `press`, `scroll`, and `switch_app`
  are disabled and non-executable.
- Preview-only contracts are never executable.
- Click Readiness is a blocker and diagnostic surface, not permission to click.
- The AI Planner is proposal-only.
- LLM output must pass validation before it can become a proposal.
- Screenshots, `screenshot_path`, and `image_bytes` are not sent to the LLM.
- API keys and secrets must not be committed, logged, or pasted into docs.
- `/proposal` never executes desktop input.
- `/execute` remains wait-only.

## Run The Cockpit

From PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m lain_desk_agent.main
```

Open:

```text
http://127.0.0.1:8000/
```

If port 8000 is busy, choose another port:

```powershell
$env:PYTHONPATH = "src"
python -m lain_desk_agent.main --port 8010
```

## Run Tests

Run the local verification script:

```powershell
.\scripts\verify.ps1
```

Manual equivalent:

```powershell
python -m compileall src tests
python -m unittest discover -s tests
node --check ui/app.js
python scripts/safety_scan.py
git diff --check
```

The safety scan checks runtime code under `src/` for obvious real desktop
actuation calls. The GitHub Actions CI runs the same core compile, test, and
JavaScript parse checks on push and pull request.

## Verify Proposal-only / Wait-only Behavior

Start the server, then use:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/runtime/status"
Invoke-RestMethod "http://127.0.0.1:8000/execution-policy"
Invoke-RestMethod "http://127.0.0.1:8000/planner-evaluation/demo"
```

Expected:

- Runtime Status reports desktop control disabled.
- Execution Policy reports only `wait` executable under the current profile.
- Planner Evaluation returns demo scenarios only and does not observe the real
  desktop, call OpenAI, or execute actions.
- `browser_search` may produce a preview-only click contract, but Click
  Readiness remains blocked.
- `dangerous_send` and `dangerous_delete` show high-risk readiness blockers.
- `app_mismatch` remains a `switch_app_hint` with click readiness
  `not_applicable`.

To verify `/execute` rejects click contracts:

```powershell
$body = @{
  action_contract = @{
    type = "click"
    status = "approved_for_execution"
    executed = $false
  }
} | ConvertTo-Json -Depth 6

try {
  Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/execute" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
} catch {
  $_.Exception.Response.StatusCode.value__
}
```

Expected result: HTTP `403`.

## Optional AI Planner Test Mode

Default planner mode is rule-based and does not call an external API.

Proposal-only AI Planner mode is opt-in:

```powershell
$env:LAIN_AGENT_PLANNER_MODE = "ai_proposal"
$env:OPENAI_API_KEY = "<your-openai-api-key>"
```

Do not commit or paste real API keys. See
[`docs/AI_PLANNER_TESTING.md`](docs/AI_PLANNER_TESTING.md).

## What Not To Do

- Do not enable click, type, hotkey, press, scroll, or switch-app execution.
- Do not add `pyautogui.click`, `moveTo`, `write`, `press`, `hotkey`, or
  `scroll` calls.
- Do not change `/execute` to accept non-wait contracts.
- Do not send screenshots or screenshot paths to the LLM.
- Do not store secrets, API keys, terminal logs, or pasted chat logs in the
  repository.
- Do not treat historical draft docs as current safety policy.

## Current Docs

- [`docs/SAFETY.md`](docs/SAFETY.md)
- [`docs/DEV_CHECKLIST.md`](docs/DEV_CHECKLIST.md)
- [`docs/ROADMAP.md`](docs/ROADMAP.md)
- [`docs/API.md`](docs/API.md)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/OBSERVATION.md`](docs/OBSERVATION.md)
- [`docs/UNDERSTANDING.md`](docs/UNDERSTANDING.md)
- [`docs/PLANNER.md`](docs/PLANNER.md)
- [`docs/AI_PLANNER_TESTING.md`](docs/AI_PLANNER_TESTING.md)
- [`docs/QUICK_TEST.md`](docs/QUICK_TEST.md)

## Historical Drafts

These files predate v0.3 and should not be treated as current safety policy:

- `docs/agent-console-v0.md`
- `docs/lain-mouse-agent-implementation-roadmap.md`
- `docs/lain-mouse-agent-prototype-spec.md`
