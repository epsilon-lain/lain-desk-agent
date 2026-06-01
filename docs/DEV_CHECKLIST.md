# Developer Checklist

Use this checklist before committing or pushing changes.

## Before Committing

1. Confirm the work is scoped to the requested change.
2. Review `git status --short`.
3. Review the diff for accidental runtime behavior changes:

```powershell
git diff -- src tests ui docs
```

4. Run the standard verification commands:

```powershell
python -m compileall src tests
python -m unittest discover -s tests
node --check ui/app.js
git diff --check
```

Success means:

- Python sources and tests compile.
- Unit tests pass.
- UI JavaScript parses.
- Git reports no whitespace errors.

## Safety Boundary Checks

The current hard boundary must remain true:

- no real mouse or keyboard desktop control
- no click/type/hotkey/press/scroll/switch_app execution
- `/execute` is wait-only
- preview-only contracts are never executable
- Click Readiness blocks click execution
- AI Planner remains proposal-only
- no screenshots, `screenshot_path`, or `image_bytes` go to the LLM
- no API keys or secrets are committed

Search for accidental real desktop actuation:

```powershell
rg -n "pyautogui\.(click|move|write|press|hotkey|scroll)|moveTo\(|typewrite\(|hotkey\(|press\(|scroll\(" src tests ui
```

Expected result: no real mouse/keyboard actuation calls.

Search for accidental secret-looking text before committing docs or logs:

```powershell
rg -n "OPENAI_API_KEY|sk-|api[_-]?key|Authorization|Bearer" .
```

Expected result: placeholders or intentional documentation only, never real
keys.

## Local Cockpit Check

Start the server:

```powershell
$env:PYTHONPATH = "src"
python -m lain_desk_agent.main --port 8000
```

Open:

```text
http://127.0.0.1:8000/
```

Check:

- Runtime Status says desktop control is disabled.
- Execution policy lists only `wait` as executable.
- Planner mode is shown without exposing secrets.
- Demo scenario panel runs without screenshots, OCR, or desktop control.
- Planner Evaluation panel shows all 4 demo scenarios.
- Click Readiness diagnostics show blockers for preview-only click contracts.
- The cockpit has no horizontal scrollbar.

## API Smoke Checks

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/runtime/status"
Invoke-RestMethod "http://127.0.0.1:8000/execution-policy"
Invoke-RestMethod "http://127.0.0.1:8000/planner-evaluation/demo"
```

Expected:

- `/runtime/status` reports `desktop_control: false`.
- `/execution-policy` reports `wait` executable and all desktop-control actions
  blocked.
- `/planner-evaluation/demo` returns 4 demo scenarios.
- `dangerous_send` and `dangerous_delete` include high-risk readiness blockers.
- `browser_search` remains preview-only click with blocked readiness.
- `app_mismatch` remains `switch_app_hint` with click readiness
  `not_applicable`.

Verify `/execute` rejects click:

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

Expected result: `403`.

## Before Pushing

1. Make sure the working tree contains only intended files.
2. Re-run the standard verification commands.
3. Confirm no generated logs, screenshots, API keys, or pasted terminal/chat
   logs are staged.
4. Keep historical draft docs out of current safety policy unless explicitly
   labeled as historical.
