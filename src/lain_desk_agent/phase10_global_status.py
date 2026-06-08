"""Deterministic Phase 10.2 global status and AI handoff reporting.

This module is read-only, dry-run-only, and debug-only. It summarizes existing
project readiness and deterministic Phase 9 validation state; it does not
observe live OS state, mutate runtime state, or execute desktop actions.
"""

from __future__ import annotations

from typing import Any

from .phase9_experiment import (
    build_phase9_reproducibility_bundle,
    evaluate_phase9_experiment_scenarios,
    replay_phase9_reproducibility_bundle,
    validate_phase9_reproducibility_bundle,
)
from .phase10_readiness import (
    PHASE10_FORBIDDEN_APIS,
    PHASE10_NO_GO_REASONS,
    build_phase10_readiness_report,
)


PHASE10_GLOBAL_STATUS_REPORT_VERSION = "phase10_global_status_v1"
PHASE10_GLOBAL_HANDOFF_PAYLOAD_VERSION = "phase10_global_ai_handoff_v1"
PHASE10_GLOBAL_SUMMARY_VERSION = "phase10_global_status_summary_v1"
PHASE10_GLOBAL_PROJECT_PHASE = (
    "Phase 10.2 global status cockpit / AI handoff dashboard"
)

PHASE10_GLOBAL_VERIFICATION_COMMANDS = (
    ".\\scripts\\verify.ps1",
    "python scripts\\safety_scan.py",
    "node --check ui/app.js",
    "git diff --check",
    "python -m unittest discover -s tests",
)

PHASE10_GLOBAL_IMPORTANT_DOCS = (
    "README.md",
    "docs/PROJECT_HEALTH_SNAPSHOT.md",
    "docs/PHASE_10_READINESS_CHECKLIST.md",
    "docs/AI_HANDOFF_CONTEXT.md",
    "docs/SAFETY_INVARIANTS.md",
    "docs/project_status_snapshot.json",
    "docs/ROADMAP.md",
    "docs/ARCHITECTURE.md",
)

PHASE10_GLOBAL_IMPORTANT_RUNTIME_FILES = (
    "src/lain_desk_agent/phase10_global_status.py",
    "src/lain_desk_agent/phase10_readiness.py",
    "src/lain_desk_agent/phase9_experiment.py",
    "src/lain_desk_agent/main.py",
    "ui/index.html",
    "ui/app.js",
    "ui/styles.css",
    "scripts/project_status.ps1",
)

PHASE10_GLOBAL_FORBIDDEN_ACTIONS = (
    "real click execution",
    "real type execution",
    "real hotkey execution",
    "real scroll execution",
    "real switch_app execution",
    "sandbox action trigger",
    "action-performing cockpit control",
    "desktop mutation from replay validation",
    "treating readiness as permission",
    "treating cockpit display as authorization",
)


def build_phase10_global_status_report() -> dict[str, Any]:
    """Build the deterministic Phase 10.2 global status report."""

    readiness_report = build_phase10_readiness_report()
    no_go_reasons = _unique_strings(
        list(readiness_report.get("no_go_reasons") or PHASE10_NO_GO_REASONS)
    )
    phase9_validation_state = _phase9_export_import_replay_validation_state()
    ai_handoff_summary = _global_ai_handoff_summary(
        no_go_reasons,
        phase9_validation_state,
    )

    return {
        "report_version": PHASE10_GLOBAL_STATUS_REPORT_VERSION,
        "project_phase": PHASE10_GLOBAL_PROJECT_PHASE,
        "dry_run": True,
        "read_only": True,
        "debug_only": True,
        "real_actions_enabled": False,
        "phase10_real_actions_implemented": False,
        "go_for_phase10": False,
        "no_go_reasons": no_go_reasons,
        "completed_phase_summary": _completed_phase_summary(),
        "safety_boundary": _safety_boundary(),
        "safety_invariants": _safety_invariants(),
        "important_docs": list(PHASE10_GLOBAL_IMPORTANT_DOCS),
        "important_runtime_files": list(PHASE10_GLOBAL_IMPORTANT_RUNTIME_FILES),
        "verification_commands": list(PHASE10_GLOBAL_VERIFICATION_COMMANDS),
        "verification_command_status_expectations": _verification_expectations(),
        "current_cockpit_capabilities": _current_cockpit_capabilities(),
        "forbidden_actions": list(PHASE10_GLOBAL_FORBIDDEN_ACTIONS),
        "forbidden_apis": list(PHASE10_FORBIDDEN_APIS),
        "phase10_readiness_state": _phase10_readiness_state(readiness_report),
        "phase9_export_import_replay_validation_state": phase9_validation_state,
        "ai_handoff_summary": ai_handoff_summary,
        "recommended_next_work": _recommended_next_work(),
        "external_llm_calls": False,
        "real_desktop_actions": False,
        "state_mutation": False,
    }


def build_phase10_global_ai_handoff_payload() -> dict[str, Any]:
    """Return a compact AI handoff payload derived from the global report."""

    report = build_phase10_global_status_report()
    return {
        "payload_version": PHASE10_GLOBAL_HANDOFF_PAYLOAD_VERSION,
        "project_phase": report["project_phase"],
        "dry_run": report["dry_run"],
        "read_only": report["read_only"],
        "debug_only": report["debug_only"],
        "real_actions_enabled": report["real_actions_enabled"],
        "phase10_real_actions_implemented": report[
            "phase10_real_actions_implemented"
        ],
        "go_for_phase10": report["go_for_phase10"],
        "no_go_reasons": list(report["no_go_reasons"]),
        "safety_boundary": list(report["safety_boundary"]),
        "phase9_export_import_replay_validation_state": dict(
            report["phase9_export_import_replay_validation_state"]
        ),
        "verification_commands": list(report["verification_commands"]),
        "important_docs": list(report["important_docs"]),
        "important_runtime_files": list(report["important_runtime_files"]),
        "ai_handoff_summary": report["ai_handoff_summary"],
        "recommended_next_work": list(report["recommended_next_work"]),
    }


def build_phase10_global_status_summary() -> dict[str, Any]:
    """Return a small deterministic status summary for cockpit chips/tests."""

    report = build_phase10_global_status_report()
    phase9_state = report["phase9_export_import_replay_validation_state"]
    return {
        "summary_version": PHASE10_GLOBAL_SUMMARY_VERSION,
        "project_phase": report["project_phase"],
        "status": "NO-GO",
        "dry_run": report["dry_run"],
        "read_only": report["read_only"],
        "debug_only": report["debug_only"],
        "real_actions_enabled": report["real_actions_enabled"],
        "phase10_real_actions_implemented": report[
            "phase10_real_actions_implemented"
        ],
        "go_for_phase10": report["go_for_phase10"],
        "no_go_reason_count": len(report["no_go_reasons"]),
        "phase9_validation_status": phase9_state["validation_status"],
        "phase9_replay_status": phase9_state["replay_status"],
        "verification_expectation": "all listed commands are expected to pass",
    }


def _phase9_export_import_replay_validation_state() -> dict[str, Any]:
    phase9_report = evaluate_phase9_experiment_scenarios()
    bundle = build_phase9_reproducibility_bundle(phase9_report)
    validation = validate_phase9_reproducibility_bundle(bundle)
    replay_report = replay_phase9_reproducibility_bundle(bundle)
    validation_summary = replay_report.get("replay_validation_summary")
    if not isinstance(validation_summary, dict):
        validation_summary = {}

    return {
        "source": "deterministic_phase9_fixture",
        "report_type": str(phase9_report.get("report_type") or ""),
        "scenario_count": int(phase9_report.get("scenario_count") or 0),
        "export_bundle_version": str(bundle.get("bundle_version") or ""),
        "import_validation_read_only": True,
        "validation_status": str(validation.get("status") or "unknown"),
        "validation_passed": validation.get("valid") is True,
        "validation_error_count": len(_list_value(validation.get("validation_errors"))),
        "validation_warning_count": len(
            _list_value(validation.get("validation_warnings"))
        ),
        "unsafe_flag_count": len(_list_value(validation.get("unsafe_flags_detected"))),
        "private_material_finding_count": len(
            _list_value(validation_summary.get("sensitive_key_findings"))
        ),
        "replay_status": str(replay_report.get("replay_status") or "unknown"),
        "replay_allowed_as_read_only": validation_summary.get(
            "replay_allowed_as_read_only"
        )
        is True,
        "replay_timeline_event_count": len(
            _list_value(replay_report.get("replayed_audit_timeline"))
        ),
        "real_action_enabled": replay_report.get("real_action_enabled") is True,
        "dry_run": replay_report.get("dry_run") is True,
        "safety_boundary_confirmed": replay_report.get("safety_boundary_confirmed")
        is True,
        "state_mutation": False,
        "execution_attempted": False,
    }


def _phase10_readiness_state(readiness_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_report_version": str(readiness_report.get("report_version") or ""),
        "project_phase": str(readiness_report.get("project_phase") or ""),
        "dry_run": readiness_report.get("dry_run") is True,
        "read_only": readiness_report.get("read_only") is True,
        "debug_only": readiness_report.get("debug_only") is True,
        "real_actions_enabled": readiness_report.get("real_actions_enabled") is True,
        "phase10_real_actions_implemented": readiness_report.get(
            "phase10_real_actions_implemented"
        )
        is True,
        "go_for_phase10": readiness_report.get("go_for_phase10") is True,
        "no_go_reason_count": len(_list_value(readiness_report.get("no_go_reasons"))),
    }


def _global_ai_handoff_summary(
    no_go_reasons: list[str],
    phase9_validation_state: dict[str, Any],
) -> str:
    return (
        "Phase 10.2 adds a global status cockpit and AI handoff dashboard for "
        "visibility only. The repository remains dry-run/read-only/debug-only; "
        "real desktop actions are disabled, Phase 10 real actions are not "
        "implemented, and go_for_phase10 is false. Phase 9 export/import/replay "
        f"validation is {phase9_validation_state['validation_status']} and replay "
        f"is {phase9_validation_state['replay_status']} as deterministic local "
        "debug data. Readiness is not permission, cockpit display is not "
        "authorization, export/import/replay is not execution, and AI handoff "
        f"is not AI control. Current no-go reasons: {', '.join(no_go_reasons)}."
    )


def _completed_phase_summary() -> list[str]:
    return [
        "Phase 4 proposal-only AI planner integration",
        "Phase 5 read-only visible element grounding",
        "Phase 6 planner evaluation expansion",
        "Phase 6.5 click readiness hardening",
        "Phase 7 sandbox action design gate",
        "Phase 8 dry-run sandbox evaluation cockpit",
        "Phase 9 dry-run harness, export/import/replay, and validation",
        "Phase 10 readiness documentation and project health handoff",
        "Phase 10.1 read-only readiness cockpit",
        "Phase 10.2 global status cockpit and AI handoff dashboard",
    ]


def _safety_boundary() -> list[str]:
    return [
        "dry-run/read-only/debug-only global status reporting",
        "no real desktop actions",
        "no real click/type/hotkey/scroll/switch_app",
        "no cockpit display grants authorization",
        "no readiness result grants permission",
        "no export/import/replay path executes actions",
        "no AI handoff payload controls the agent",
        "no live OS state inspection for this report",
        "no runtime state mutation from this report",
    ]


def _safety_invariants() -> list[str]:
    return [
        "real_actions_enabled remains false",
        "phase10_real_actions_implemented remains false",
        "go_for_phase10 remains false",
        "dry_run remains true",
        "read_only remains true",
        "debug_only remains true",
        "Execution Policy remains separate from readiness display",
        "Permission Profile remains separate from cockpit display",
        "Capability Registry remains separate from AI handoff",
        "Phase 9 imported bundles remain untrusted local input",
        "Phase 9 replay remains read-only",
        "validation errors do not mutate runtime state",
    ]


def _verification_expectations() -> list[dict[str, str]]:
    return [
        {
            "command": command,
            "expected_status": "pass",
            "meaning": "regression check for the current dry-run cockpit state",
        }
        for command in PHASE10_GLOBAL_VERIFICATION_COMMANDS
    ]


def _current_cockpit_capabilities() -> list[str]:
    return [
        "runtime status display",
        "execution policy display",
        "capability and permission profile display",
        "planner trace display",
        "planner evaluation demo report",
        "Phase 8 sandbox evaluation trace display",
        "Phase 9 dry-run harness display",
        "Phase 9 export/import/replay validation display",
        "Phase 10.1 readiness display",
        "Phase 10.2 global status and AI handoff display",
        "local-only filters, expand/collapse, and copy helpers",
    ]


def _recommended_next_work() -> list[str]:
    return [
        "Keep Phase 10.2 as visibility, handoff, docs, and regression protection.",
        "Preserve the dry-run/read-only/debug-only cockpit boundary.",
        "Keep Phase 9 replay validation stable and deterministic.",
        "Run the verification command set after UI or safety-related edits.",
        "Defer real desktop action work until a future explicit request satisfies every Phase 10 gate.",
    ]


def _list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _unique_strings(values: list[Any]) -> list[str]:
    unique_values: list[str] = []
    for value in values:
        text = str(value)
        if text and text not in unique_values:
            unique_values.append(text)
    return unique_values
