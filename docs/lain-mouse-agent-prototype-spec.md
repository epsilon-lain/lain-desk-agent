# Lain Mouse Agent (Prototype) – Product Understanding & v0 Scope

This document captures the intended direction of the open-source **Lain Mouse Agent** prototype.

## 1) Goal (What this project is)

Build a **general-purpose desktop interaction shell** where an AI agent can:

1. Observe the current screen.
2. Understand the current UI state.
3. Decide the next target element.
4. Convert target to actionable coordinates or keystrokes.
5. Execute mouse/keyboard action.
6. Re-observe the screen.
7. Verify whether the action succeeded.

The project focuses on this closed-loop interaction pattern, not on one specific app.

## 2) Non-goals (What this project is NOT)

- Not a WeChat-only automation script.
- Not a game bot or anti-cheat bypass tool.
- Not a permission-escalation framework.
- Not a bot designed to bypass captchas/password/payment confirmation/security barriers.

## 3) Demo scenario (example only)

Example command:

> “Go to WeChat and send XX a sticker that you think represents a smile.”

This is only a demonstration task used to validate the general loop. Implementation must remain app-agnostic.

## 4) Safety and security constraints (hard requirements)

1. **User-permission boundary only**: operate strictly as the current logged-in user.
2. **No bypass behavior**: no bypass of permissions, security boundaries, captchas, passwords, payment confirmations, anti-cheat, or privacy controls.
3. **Emergency stop**: global stop hotkey, preferred `ESC`.
4. **Action logging**: every action and observation step must be logged with timestamps.
5. **High-risk confirmation gate**: explicit user confirmation required before:
   - sending messages
   - deleting files
   - submitting forms
   - making payments
   - overwriting files
   - changing account/security settings
6. **User-space only (v0)**: no kernel driver.
7. **Open-source friendly**: easy to run, easy to understand, clean architecture, suitable for GitHub.

## 5) Minimal v0 architecture

- **Chat UI layer**: simple local text box for natural-language tasks.
- **Perception layer**: screen capture + cursor state + optional OCR/vision model.
- **Planner layer**: decide next action from current state and task goal.
- **Grounding layer**: map semantic target ("Send button") to concrete coordinates.
- **Actuation layer**: mouse move/click, keyboard input, shortcuts.
- **Verification layer**: compare post-action observation against expected state transition.
- **Safety layer**: risk classifier, confirmation prompts, emergency stop monitoring.
- **Audit layer**: structured logs, replayable action trace.

## 6) Suggested v0 execution loop

```text
while task_not_done:
  obs_t = observe_screen_and_pointer()
  state_t = infer_ui_state(obs_t)
  action_t = plan_next_action(state_t, user_goal)

  if is_high_risk(action_t):
      require_explicit_user_confirmation()
      if not confirmed: stop_or_replan()

  execute(action_t)
  obs_t1 = observe_screen_and_pointer()

  if verify_success(obs_t, action_t, obs_t1):
      continue
  else:
      recover_or_replan()
```

## 7) Acceptance criteria for first public prototype

- Can accept a natural-language desktop task in local chat UI.
- Can perform at least one multi-step cross-app workflow using the observe→act→verify loop.
- Emergency stop (`ESC`) reliably interrupts execution.
- High-risk actions cannot run without user confirmation.
- Action logs are readable and sufficient for debugging/replay.
- README explains setup, limitations, and safety boundaries clearly.

## 8) Open-source release checklist (recommended)

- Threat model / misuse statement in repo.
- Safety disclaimer and explicit prohibited use cases.
- Reproducible local setup instructions.
- Example tasks and demo GIF/video.
- Issue templates for bug/safety reports.
