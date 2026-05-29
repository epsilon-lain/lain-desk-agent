# Quick test guide

Use this guide to verify the current v0.3 guarded wait-only cockpit.

## Start server

From PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m lain_desk_agent.main
```

## Open cockpit

Open:

```text
http://127.0.0.1:8000/
```

## Test Plan

1. Enter `Search` in the task box.
2. Click `Plan`.
3. Expect either `target_hint` or `no_op`, depending on the current screen.
4. Expect no real desktop action. Planning may show a preview or explanation, but it must not move, click, type, press keys, scroll, or launch apps.

## Test wait self-test

1. Click `Run wait self-test`.
2. Expect an executed `wait` result.
3. Expect `verification_result` status `verified`.
4. Expect recent events to include:
   - `action.execution_requested`
   - `action.executed`
   - `action.verified`

## Test safety boundary

Confirm:

- `click`, `type`, `hotkey`, `scroll`, and `switch_app` remain disabled.
- Desktop control is disabled.
- No mouse or keyboard control occurs.

## Useful endpoints

```text
/runtime/status
/capabilities
/permission-profile
/click-readiness
/events
```
