# AI Planner Testing Guide

## Purpose

The AI Planner is proposal-only. It may suggest:

- `no_op`
- `target_hint`
- `switch_app_hint`

It must not execute actions. Every AI proposal still goes through:

- `validate_ai_proposal`
- Safety Gate
- Action Contract
- Click Readiness
- Capability Registry
- Permission Profile
- Execution Policy

## Safety Boundaries

- Do not commit API keys.
- Do not paste API keys into screenshots, issues, README, or docs.
- Do not send screenshots to the LLM in this version.
- Do not enable click, type, hotkey, or scroll.
- No real mouse or keyboard control exists.
- Unsafe AI output becomes a safe `no_op`.

## PowerShell Setup

Use a placeholder in documentation and examples. Set the real key only in your local shell session.

```powershell
$env:PYTHONPATH = "src"
$env:LAIN_AGENT_PLANNER_MODE = "ai_proposal"
$env:OPENAI_API_KEY = "<your-openai-api-key>"
python -m lain_desk_agent.main
```

To return to the default rule-based planner:

```powershell
$env:LAIN_AGENT_PLANNER_MODE = "rule_based"
```

## Local UI Test

Open:

```text
http://127.0.0.1:8000/
```

Check Runtime status:

```text
Planner: ai-proposal; LLM ready
```

Then:

1. Enter `Search`.
2. Click `Plan`.

Expected:

- AI may produce `target_hint`.
- `action_contract` may be a preview-only `click`.
- `click_readiness` remains blocked.
- No desktop action executes.

## API Test Commands

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/runtime/status"
Invoke-RestMethod "http://127.0.0.1:8000/planner-context?task=Search"
Invoke-RestMethod "http://127.0.0.1:8000/proposal?task=Search"
```

## Expected Safe Behavior

- `planner_context` contains compact state only.
- `planner_context` contains no `screenshot_path`.
- `planner_context` contains no `image_bytes`.
- LLM output is validated before use.
- Invalid or unsafe output returns `no_op`.
- Wait self-test remains the only executable path.

## Troubleshooting

- If PowerShell shows `>>`, press `Ctrl+C` and re-enter commands line by line.
- If Planner stays `rule_based`, check `LAIN_AGENT_PLANNER_MODE` and `OPENAI_API_KEY`.
- If the API call fails, the app should fallback safely.
- If an API key was exposed, revoke or rotate it.

## Verification Checklist

```powershell
python -m compileall src tests
python -m unittest discover -s tests
node --check ui/app.js
```

Also verify:

- `/runtime/status` reports the expected planner mode.
- `/proposal` still does not execute desktop input.
