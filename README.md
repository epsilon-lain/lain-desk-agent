# lain-desk-agent

A local desktop agent prototype that observes the screen and controls mouse/keyboard actions within the current user's permission boundaries.

The first milestone is intentionally small: a local Python backend with clear safety rules, a health endpoint, and a place to grow screen observation, action planning, and human approval flows.

## Project principles

- Stay inside the current user's normal desktop permissions.
- Do not bypass passwords, captchas, paywalls, anti-cheat systems, or operating-system security boundaries.
- Ask for human confirmation before high-risk actions.
- Keep an emergency stop path available before any real mouse/keyboard automation is enabled.
- Log planned and executed actions so the user can inspect what happened.

## Current MVP

This repository currently starts with a minimal FastAPI backend:

- `GET /health` checks whether the local server is running.
- `GET /session` returns the current agent session state.
- `POST /session/start` starts a supervised local session.
- `POST /session/stop` stops the local session.

No real screen reading, mouse movement, or keyboard control is enabled yet. That is deliberate.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e .
uvicorn lain_desk_agent.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/health
```

## Next steps

1. Add a tiny web chat UI.
2. Add screen snapshot capture as a read-only tool.
3. Add an action planner that only proposes actions at first.
4. Add human approval before executing any mouse/keyboard action.
5. Add emergency stop handling and action logs before enabling automation.

See `docs/SAFETY.md` and `docs/ROADMAP.md` for the working plan.
