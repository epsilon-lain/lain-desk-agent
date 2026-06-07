"""Deterministic Phase 10 readiness reporting.

This module is read-only and dry-run-only. It reports whether the repository is
ready for a future Phase 10 real-action experiment; it does not implement,
enable, or call any real desktop action path.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


PHASE10_READINESS_REPORT_VERSION = "phase10_readiness_v1"
PHASE10_PROJECT_PHASE = "Phase 10.1 readiness cockpit / release-candidate hardening"
PHASE10_LATEST_COMPLETED_PHASE = "Phase 9.x dry-run sandbox, replay, and validation pipeline"

PHASE10_NO_GO_REASONS = (
    "phase10_real_actions_not_implemented",
    "real_actions_disabled",
    "manual_phase10_approval_not_recorded",
    "real_action_adapter_absent",
    "live_sandbox_scope_not_selected",
    "live_post_action_verification_not_implemented",
)

PHASE10_FORBIDDEN_ACTIONS = (
    "real click",
    "real type",
    "real hotkey",
    "real scroll",
    "real switch_app",
    "shell execution",
    "file deletion",
    "system settings change",
    "browser credential interaction",
    "external website interaction unless mocked locally",
    "hidden or background action",
)

PHASE10_FORBIDDEN_APIS = (
    "pyautogui",
    "pynput",
    "keyboard",
    "mouse",
    "win32api",
    "ctypes SendInput",
    "ctypes mouse_event",
    "xdotool",
    "AppleScript UI scripting",
)

PHASE10_REQUIRED_TEST_COMMANDS = (
    ".\\scripts\\verify.ps1",
    "python scripts\\safety_scan.py",
    "node --check ui/app.js",
    "git diff --check",
    "python -m unittest discover -s tests",
)

PHASE10_REQUIRED_MANUAL_CHECKS = (
    "Review docs/PHASE_10_READINESS_CHECKLIST.md.",
    "Confirm no real-action adapter exists.",
    "Confirm no sandbox or replay UI calls /execute.",
    "Confirm Execution Policy, Permission Profile, and Capability Registry remain unchanged.",
    "Confirm imported bundles are treated as untrusted input.",
    "Confirm emergency stop, rollback, and post-action verification are designed before implementation.",
)

PHASE10_IMPORTANT_FILES = (
    "docs/PROJECT_HEALTH_SNAPSHOT.md",
    "docs/PHASE_10_READINESS_CHECKLIST.md",
    "docs/AI_HANDOFF_CONTEXT.md",
    "docs/SAFETY_INVARIANTS.md",
    "docs/project_status_snapshot.json",
    "src/lain_desk_agent/phase10_readiness.py",
    "src/lain_desk_agent/phase9_experiment.py",
    "src/lain_desk_agent/sandbox_experiment.py",
    "src/lain_desk_agent/main.py",
    "ui/index.html",
    "ui/app.js",
    "ui/styles.css",
    "scripts/project_status.ps1",
)


@dataclass(frozen=True)
class Phase10ReadinessInput:
    """Explicit readiness flags for a future Phase 10 readiness calculation."""

    manual_phase10_approval_recorded: bool = False
    live_sandbox_scope_selected: bool = False
    live_post_action_verification_implemented: bool = False
    emergency_stop_implemented: bool = False
    rollback_implemented: bool = False
    real_action_adapter_present: bool = False
    phase10_real_actions_implemented: bool = False
    real_actions_enabled: bool = False
    dry_run: bool = True
    read_only: bool = True
    debug_only: bool = True
    additional_no_go_reasons: tuple[str, ...] = field(default_factory=tuple)


def build_phase10_readiness_report(
    readiness_input: Phase10ReadinessInput | None = None,
) -> dict[str, Any]:
    """Build the deterministic Phase 10 readiness report.

    The default report is intentionally NO-GO because Phase 10 real actions are
    not implemented and real desktop actions remain disabled.
    """

    readiness_input = readiness_input or Phase10ReadinessInput()
    no_go_reasons = build_phase10_blocker_summary(readiness_input)["no_go_reasons"]
    readiness_checks = _readiness_checks(readiness_input)
    safety_invariants = build_phase10_safety_invariant_report()
    ai_handoff_summary = build_phase10_ai_handoff_summary(no_go_reasons)
    go_no_go = build_phase10_go_no_go_report(no_go_reasons, readiness_checks)

    return {
        "report_version": PHASE10_READINESS_REPORT_VERSION,
        "project_phase": PHASE10_PROJECT_PHASE,
        "latest_completed_phase": PHASE10_LATEST_COMPLETED_PHASE,
        "dry_run": bool(readiness_input.dry_run),
        "read_only": bool(readiness_input.read_only),
        "debug_only": bool(readiness_input.debug_only),
        "real_actions_enabled": bool(readiness_input.real_actions_enabled),
        "phase10_real_actions_implemented": bool(
            readiness_input.phase10_real_actions_implemented
        ),
        "go_for_phase10": bool(go_no_go["go_for_phase10"]),
        "no_go_reasons": no_go_reasons,
        "safety_boundary": _safety_boundary(),
        "completed_phase_summary": _completed_phase_summary(),
        "required_gates": _required_gates(),
        "readiness_checks": readiness_checks,
        "safety_invariants": safety_invariants["invariants"],
        "known_blockers": _known_blockers(no_go_reasons),
        "required_manual_checks": list(PHASE10_REQUIRED_MANUAL_CHECKS),
        "required_test_commands": list(PHASE10_REQUIRED_TEST_COMMANDS),
        "ai_handoff_summary": ai_handoff_summary,
        "recommended_next_work": _recommended_next_work(),
        "forbidden_actions": list(PHASE10_FORBIDDEN_ACTIONS),
        "forbidden_apis": list(PHASE10_FORBIDDEN_APIS),
        "important_files": list(PHASE10_IMPORTANT_FILES),
        "audit_notes": _audit_notes(),
        "go_no_go": go_no_go,
        "external_llm_calls": False,
        "real_desktop_actions": False,
    }


def build_phase10_ai_handoff_summary(no_go_reasons: list[str] | None = None) -> str:
    """Return a compact handoff summary for future AI/Codex sessions."""

    reasons = ", ".join(no_go_reasons or list(PHASE10_NO_GO_REASONS))
    return (
        "Phase 10.1 reports readiness only. Phase 10 real actions are not "
        "implemented, real desktop actions remain disabled, and the current "
        "default is dry-run/read-only/debug-only. Treat no-go reasons as "
        f"expected blockers: {reasons}. Do not enable real actions unless a "
        "future explicit user request satisfies the Phase 10 readiness "
        "checklist, Phase 7 gate, Phase 9 gate, audit, rollback, emergency "
        "stop, and post-action verification requirements."
    )


def build_phase10_safety_invariant_report() -> dict[str, Any]:
    """Return deterministic safety invariants for cockpit/debug display."""

    invariants = [
        "no real desktop actions",
        "no sandbox or replay /execute path",
        "no execute button for sandbox actions",
        "no approval button that triggers real action",
        "no real-action toggle",
        "dry_run remains default",
        "real_actions_enabled remains false",
        "phase10_real_actions_implemented remains false",
        "imported bundles are untrusted input",
        "replay is read-only",
        "validation errors do not mutate runtime state",
        "readiness is not permission",
        "proposal is not execution",
        "cockpit display is not authorization",
        "AI handoff is not AI control",
    ]
    return {
        "report_type": "phase10_safety_invariant_report",
        "invariants": invariants,
        "passed": True,
    }


def build_phase10_blocker_summary(
    readiness_input: Phase10ReadinessInput | None = None,
) -> dict[str, Any]:
    """Return expected no-go reasons for the current pre-Phase-10 state."""

    readiness_input = readiness_input or Phase10ReadinessInput()
    no_go_reasons: list[str] = []
    if not readiness_input.phase10_real_actions_implemented:
        no_go_reasons.append("phase10_real_actions_not_implemented")
    if not readiness_input.real_actions_enabled:
        no_go_reasons.append("real_actions_disabled")
    if not readiness_input.manual_phase10_approval_recorded:
        no_go_reasons.append("manual_phase10_approval_not_recorded")
    if not readiness_input.real_action_adapter_present:
        no_go_reasons.append("real_action_adapter_absent")
    if not readiness_input.live_sandbox_scope_selected:
        no_go_reasons.append("live_sandbox_scope_not_selected")
    if not readiness_input.live_post_action_verification_implemented:
        no_go_reasons.append("live_post_action_verification_not_implemented")
    if not readiness_input.emergency_stop_implemented:
        no_go_reasons.append("live_emergency_stop_not_implemented")
    if not readiness_input.rollback_implemented:
        no_go_reasons.append("live_rollback_not_implemented")
    no_go_reasons.extend(str(reason) for reason in readiness_input.additional_no_go_reasons)

    return {
        "go_for_phase10": False,
        "no_go_reasons": _unique(no_go_reasons),
        "expected_blockers": True,
    }


def build_phase10_go_no_go_report(
    no_go_reasons: list[str] | None = None,
    readiness_checks: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return GO/NO-GO summary; default is conservative NO-GO."""

    reasons = list(no_go_reasons or PHASE10_NO_GO_REASONS)
    checks = deepcopy(readiness_checks or [])
    all_checks_passed = bool(checks) and all(bool(check.get("passed")) for check in checks)
    return {
        "go_for_phase10": False if reasons else all_checks_passed,
        "status": "NO-GO" if reasons or not all_checks_passed else "GO",
        "no_go_reasons": reasons,
        "readiness_checks_passed": all_checks_passed,
        "permission_granted": False,
        "notes": [
            "GO/NO-GO report is a diagnostic summary, not permission.",
            "Current deterministic report is expected to be NO-GO.",
        ],
    }


def _readiness_checks(readiness_input: Phase10ReadinessInput) -> list[dict[str, Any]]:
    checks = [
        ("dry_run_default", readiness_input.dry_run, "dry-run remains default"),
        ("read_only_default", readiness_input.read_only, "read-only remains default"),
        ("debug_only_default", readiness_input.debug_only, "debug-only remains default"),
        (
            "real_actions_disabled",
            not readiness_input.real_actions_enabled,
            "real desktop actions remain disabled",
        ),
        (
            "phase10_not_implemented",
            not readiness_input.phase10_real_actions_implemented,
            "Phase 10 real actions are not implemented",
        ),
        (
            "manual_phase10_approval_recorded",
            readiness_input.manual_phase10_approval_recorded,
            "future manual approval must be recorded before implementation",
        ),
        (
            "real_action_adapter_present",
            readiness_input.real_action_adapter_present,
            "future adapter must be separately designed and reviewed",
        ),
        (
            "live_sandbox_scope_selected",
            readiness_input.live_sandbox_scope_selected,
            "future live sandbox scope must be one window and one target",
        ),
        (
            "live_post_action_verification_implemented",
            readiness_input.live_post_action_verification_implemented,
            "future post-action verification must be implemented before action",
        ),
        (
            "emergency_stop_implemented",
            readiness_input.emergency_stop_implemented,
            "future emergency stop must exist before action",
        ),
        (
            "rollback_implemented",
            readiness_input.rollback_implemented,
            "future rollback/reset plan must exist before action",
        ),
    ]
    return [
        {
            "code": code,
            "passed": bool(passed),
            "status": "pass" if passed else "blocked",
            "description": description,
        }
        for code, passed, description in checks
    ]


def _safety_boundary() -> list[str]:
    return [
        "dry-run/read-only/debug-only readiness reporting",
        "no real desktop actions",
        "no real click/type/hotkey/scroll/switch_app",
        "no sandbox or replay /execute path",
        "no mutation endpoint for sandbox action",
        "Execution Policy, Permission Profile, and Capability Registry unchanged",
        "readiness is not permission",
        "proposal is not execution",
        "cockpit display is not authorization",
        "export/import/replay is not execution",
        "AI handoff is not AI control",
    ]


def _completed_phase_summary() -> list[str]:
    return [
        "visible_elements grounding",
        "ui_tree read-only grounding",
        "planner evaluation expansion",
        "click readiness hardening",
        "Phase 7 sandbox action design gate",
        "Phase 8 dry-run sandbox experiment gate and evaluation cockpit",
        "Phase 9 dry-run harness, export/import/replay, validation, and cockpit polish",
        "Phase 10 readiness checklist, AI handoff context, and safety invariants",
    ]


def _required_gates() -> list[dict[str, Any]]:
    return [
        {
            "code": "phase7_gate",
            "label": "Phase 7 Gate",
            "required": True,
            "current_status": "documented_not_satisfied_for_real_action",
        },
        {
            "code": "phase9_gate",
            "label": "Phase 9 Dry-run Gate",
            "required": True,
            "current_status": "dry_run_only",
        },
        {
            "code": "manual_approval",
            "label": "Explicit Manual Phase 10 Approval",
            "required": True,
            "current_status": "not_recorded",
        },
        {
            "code": "execution_policy_review",
            "label": "Execution Policy Review",
            "required": True,
            "current_status": "unchanged_wait_only",
        },
        {
            "code": "post_action_verification",
            "label": "Post-action Verification",
            "required": True,
            "current_status": "not_implemented_for_real_action",
        },
        {
            "code": "emergency_stop_and_rollback",
            "label": "Emergency Stop And Rollback",
            "required": True,
            "current_status": "mock_only_in_phase9",
        },
    ]


def _known_blockers(no_go_reasons: list[str]) -> list[dict[str, str]]:
    descriptions = {
        "phase10_real_actions_not_implemented": "Phase 10 real-action implementation has not started.",
        "real_actions_disabled": "Real desktop actions remain disabled.",
        "manual_phase10_approval_not_recorded": "No explicit Phase 10 implementation approval is recorded.",
        "real_action_adapter_absent": "No real-action adapter exists.",
        "live_sandbox_scope_not_selected": "No live one-window/one-target sandbox scope is selected.",
        "live_post_action_verification_not_implemented": "Live post-action verification is not implemented.",
        "live_emergency_stop_not_implemented": "Live emergency stop is not implemented for real action.",
        "live_rollback_not_implemented": "Live rollback/reset is not implemented for real action.",
    }
    return [
        {
            "code": reason,
            "severity": "expected_no_go",
            "description": descriptions.get(reason, "Expected Phase 10 readiness blocker."),
        }
        for reason in no_go_reasons
    ]


def _recommended_next_work() -> list[str]:
    return [
        "Keep Phase 10 work in docs, tests, and dry-run validation until explicitly approved.",
        "Review Phase 7 and Phase 10 checklists before any future implementation proposal.",
        "Add more deterministic readiness fixtures if future gates are proposed.",
        "Keep cockpit readiness display read-only and local-copy-only.",
        "Continue running verify.ps1, safety_scan.py, node --check ui/app.js, and git diff --check.",
    ]


def _audit_notes() -> list[str]:
    return [
        "Phase 10.1 readiness report is deterministic and does not mutate state.",
        "No live desktop observation is required for this report.",
        "No action-performing endpoint is called.",
        "NO-GO reasons are expected readiness blockers, not runtime errors.",
    ]


def _unique(values: list[str]) -> list[str]:
    unique_values: list[str] = []
    for value in values:
        if value not in unique_values:
            unique_values.append(value)
    return unique_values
