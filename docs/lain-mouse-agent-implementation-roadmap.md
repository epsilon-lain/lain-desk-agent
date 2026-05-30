# Lain Mouse Agent - Implementation Roadmap

This document turns the prototype vision into an engineering path. The goal is
to avoid starting with a giant "AI desktop agent" problem. Build one narrow,
observable, interruptible loop first, then make each layer smarter.

## 1) Guiding principle

The project should grow as a supervised loop, but not by rushing into broad
desktop execution. The current route is:

```text
Read-only loop matures
-> target proposal
-> safety decision
-> tiny actuation
-> verification
-> expand action types later
```

Every milestone should keep the loop inspectable. A weak read-only loop that can
explain what it sees is more useful than an eager actor that cannot justify or
verify its next step.

## 2) Reset phase map

### Phase 0 - Local Console Shell

Status: complete.

Goal: Mirai opens, shows status, and shows details.

### Phase 1 - Observation Snapshot

Status: complete.

Goal: capture screenshot, cursor, active window title/app, screen size,
`runs/` snapshots, and audit log.

### Phase 2 - Understanding Read-only

Status: complete to v1.2.

Goal: convert observations into `ui_state`, including `app_guess`,
`state_guess`, `visible_text`, `visible_text_boxes`, and OCR-backed
`visible_elements[type="text"]`.

### Phase 3 - Proposal-only Planner

Status: in progress.

Goal: Planner reads `visible_elements` and proposes a small next-step hint. It
may emit `target_hint` with `target_element_id`, `reason`, `risk`, and
`requires_approval`. It must not emit executable desktop actions such as
`click`, `type`, `hotkey`, or `submit`.

### Phase 4 - Safety Gate v0

Status: in progress.

Goal: classify proposals as `allowed`, `needs_approval`, or `blocked` before
any actuation exists.

### Phase 5 - Actuation v0

Status: future.

Goal: connect only tiny safe actions at first, such as `wait`, `no_op`, or a
mouse move preview. Do not add typing, sending, deleting, submitting, or broad
clicking yet.

### Phase 6 - Verification v0

Status: future.

Goal: after any action, observe again and compare before/after. If uncertain,
stop.

## 3) Recommended v0 stack

Keep v0 boring and local:

- Runtime: Python.
- UI: simple local web UI or small desktop window.
- Screen capture: platform library first, abstracted behind one interface.
- Mouse/keyboard: user-space automation library, abstracted behind one interface.
- Logs: JSONL action trace.
- Agent model: start with a rule/manual planner, then add a vision/LLM planner.

The first version should optimize for debuggability, not elegance.

## 4) Core module contracts

### Observation

Responsible for collecting what the agent can currently know.

Output shape:

```json
{
  "timestamp": "2026-05-24T12:00:00Z",
  "screenshot_path": "runs/001/obs_0001.png",
  "screen_size": [1920, 1080],
  "cursor": [812, 441],
  "active_window": {
    "title": "Example",
    "app": "ExampleApp"
  }
}
```

### Planner

Responsible for proposing the next target or non-action from the user goal and
latest UI state.

Current proposal shape:

```json
{
  "type": "target_hint",
  "target_element_id": "element_0007",
  "reason": "The task mentions Search and OCR found matching text.",
  "risk": "low",
  "requires_approval": false
}
```

Planner should read only `visible_elements`. It should not care whether an
element came from OCR, DOM, accessibility, or vision.

### Safety

Responsible for deciding whether a proposal can proceed.

Minimum rules:

- Read-only proposals such as `no_op` and `target_hint` can be allowed.
- Early executable actions are blocked until Actuation v0 explicitly supports
  them.
- Sending messages, submitting forms, deleting, overwriting, paying, changing
  settings, or account/security changes require confirmation.
- `ESC` must stop the run as soon as possible.

### Actuation

Responsible for executing only normalized actions. It should not contain task
logic.

Supported v0 actions:

- `move`
- `click`
- `double_click`
- `type_text`
- `hotkey`
- `scroll`
- `wait`

### Verification

Responsible for checking whether the action probably worked.

Start simple:

- Compare before/after screenshots.
- Confirm that the active window changed when expected.
- Confirm that typed text appears when OCR is available.
- Let the planner request manual confirmation when automated verification is
  uncertain.

### Audit

Responsible for making every run inspectable.

Each run should create:

- `run.json`: task metadata and final status.
- `events.jsonl`: observations, planned actions, confirmations, execution
  results, verification results, and errors.
- `screenshots/`: captured before/after images.

## 5) Perception sources v2

Future perception sources should all feed the same `visible_elements` list:

- OCR source: already present, maps text boxes to `element[type="text"]`.
- DOM source: future, read-only, explicitly authorized, maps HTML controls to
  `button`, `input`, and `link`.
- Accessibility source: future, read-only, maps platform controls to `button`
  and `textbox`.
- Vision source: future fallback, maps semantic candidates to
  `possible_button` and `possible_input`.

Planner stays source-agnostic and reads only `visible_elements`.

## 6) Build milestones

### Milestone 0 - Repository skeleton

Goal: make the project runnable with no intelligence yet.

Deliverables:

- Python package/app skeleton.
- `README` setup instructions.
- `runs/` output ignored by git.
- Basic CLI command: `lain-agent run`.

Done when:

- The command starts a run, writes a log file, and exits cleanly.

### Milestone 1 - Observe-only loop

Goal: prove screen capture, cursor capture, active-window capture, and logging.

Deliverables:

- `observe()` function.
- Screenshot saved per observation.
- JSONL log entries.

Done when:

- Running the app captures the screen every N seconds until stopped.
- `ESC` or a stop command terminates the loop.

### Milestone 2 - Manual action loop

Goal: prove the safety and audit shell before adding broad actuation.

Deliverables:

- UI shows a structured proposal.
- Safety gate classifies the proposal.
- Actuation supports only tiny safe actions such as `wait`, `no_op`, or move
  preview.
- Before/after observations are saved for any action that does run.

Done when:

- A developer can inspect the target hint, safety decision, and resulting log
  without the agent typing, clicking, submitting, or deleting anything.

### Milestone 3 - Scripted demo planner

Goal: create one deterministic multi-step workflow using the same loop.

Deliverables:

- A small planner that returns the next action from a predefined scenario.
- Verification after each step.
- Recovery behavior for failed verification.

Done when:

- The project can complete one harmless desktop workflow, such as opening a text
  editor and typing a short draft without sending/submitting anything.

### Milestone 4 - Vision-assisted grounding

Goal: move from text-only OCR targets to richer read-only perception sources.

Deliverables:

- DOM, accessibility, or vision sources behind explicit read-only integration.
- Candidate UI elements with type, label, bounding box, source, and confidence.
- Conservative source fusion into `visible_elements`.

Done when:

- Planner can point at a visible target by `element_id`, such as "New",
  "Search", or an input field, without hard-coded coordinates.

### Milestone 5 - LLM planner

Goal: let the planner choose actions from task intent and observed UI state.

Deliverables:

- Planner prompt/schema.
- Strict action JSON validation.
- Refusal/replan path for uncertain or unsafe actions.
- Confirmation gate before high-risk actions.

Done when:

- The agent can complete a small multi-step workflow from a natural-language
  instruction while staying inside the same safety boundaries.

### Milestone 6 - Public prototype polish

Goal: make the repo understandable and safe for early users.

Deliverables:

- Threat model / misuse statement.
- Setup guide.
- Demo recording.
- Example run logs.
- Issue templates for bugs and safety reports.

Done when:

- A new developer can clone the repo, run the demo, inspect the logs, and
  understand what the project explicitly refuses to do.

## 7) First demo path

Use a harmless workflow before touching chat apps or irreversible actions.

Recommended first demo:

```text
User goal: "Open a local text editor and write a short note."
```

Why this is the right first demo:

- It exercises screen observation.
- It exercises window/app switching.
- It exercises typing.
- It exercises verification.
- It avoids sending, deleting, paying, or submitting anything.

Only after this loop is reliable should the project use messaging-app demos, and
those must stop at a confirmation gate before sending.

## 8) What to build next

The next concrete step is not model intelligence and not broad execution. It is
the proposal/safety slice:

1. Planner v1 emits `target_hint` from `visible_elements`.
2. Safety Gate v0 classifies proposals.
3. Mirai details show the safety decision.
4. Actuation remains disconnected except for future tiny safe actions.
5. Verification is added before expanding action types.

Once that exists, every later improvement has a place to plug in.
