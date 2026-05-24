# Safety model

`lain-desk-agent` is a supervised local desktop agent. It should behave like a visible helper acting under the current user's normal permissions, not like a hidden automation system.

## Allowed direction

- Observe the user's screen only after the local app is started by the user.
- Propose actions before executing risky operations.
- Execute only actions that the user could perform with normal mouse and keyboard input.
- Keep an emergency stop mechanism available before real input control exists.
- Record action plans, confirmations, and executed actions.

## Not allowed

- Bypassing passwords, captchas, paywalls, anti-cheat systems, or security prompts.
- Storing user passwords or secret tokens in plaintext.
- Confirming payments, deleting important data, sending messages, or changing account settings without explicit human approval.
- Running hidden background control without a visible local session.
- Escalating permissions beyond the current user account.

## Human confirmation levels

### Low risk

Examples: reading the screen, opening a harmless local page, moving focus between windows.

Default behavior: allowed during an active supervised session.

### Medium risk

Examples: typing into a text field, clicking a normal button, opening a website.

Default behavior: propose first; execute only after the user approves in the app.

### High risk

Examples: sending a message, submitting a form, deleting a file, changing settings, installing software.

Default behavior: require explicit confirmation with a clear summary of the exact action.

### Blocked

Examples: password/captcha bypass, payment confirmation, anti-cheat evasion, stealth control, privilege escalation.

Default behavior: refuse.

## MVP rule

The current MVP must not move the mouse, type keys, or capture the screen yet. It only provides a safe backend shape for future work.
