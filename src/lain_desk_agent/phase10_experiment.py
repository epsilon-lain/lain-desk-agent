"""Phase 10 guardrail and experiment-display facade.

This file intentionally exposes only deterministic, read-only guardrail and
experiment-display helpers. It is not a real-action experiment adapter.
"""

from __future__ import annotations

from typing import Any

from .phase10_global_status import build_phase10_global_status_report
from .phase10_guardrails import (
    build_phase10_guardrail_validation_report,
    build_phase10_release_candidate_bundle,
    validate_phase10_release_candidate_bundle,
)
from .phase10_readiness import build_phase10_readiness_report


PHASE10_EXPERIMENT_DISPLAY_REPORT_VERSION = "phase10_experiment_display_v1"
PHASE10_EXPERIMENT_DISPLAY_PROJECT_PHASE = (
    "Phase 10.5 cockpit experiment / guardrail results display"
)


def build_phase10_experiment_display_report() -> dict[str, Any]:
    """Build deterministic read-only Phase 10 experiment display data.

    The report combines the existing readiness, global status, and guardrail
    validation structures for cockpit display. It does not observe the live
    desktop, mutate runtime state, call an action-performing endpoint, or
    enable any real desktop action.
    """

    readiness_report = build_phase10_readiness_report()
    global_status = build_phase10_global_status_report()
    guardrail_report = build_phase10_guardrail_validation_report()
    validation = guardrail_report.get("validation")
    if not isinstance(validation, dict):
        validation = {}

    no_go_reasons = _unique_strings(
        _string_list(readiness_report.get("no_go_reasons"))
        + _string_list(global_status.get("no_go_reasons"))
    )

    return {
        "report_version": PHASE10_EXPERIMENT_DISPLAY_REPORT_VERSION,
        "project_phase": PHASE10_EXPERIMENT_DISPLAY_PROJECT_PHASE,
        "dry_run": True,
        "read_only": True,
        "debug_only": True,
        "real_actions_enabled": False,
        "phase10_real_actions_implemented": False,
        "go_for_phase10": False,
        "experiment_status": _experiment_status(no_go_reasons),
        "guardrail_status": _guardrail_status(guardrail_report, validation),
        "no_go_reasons": no_go_reasons,
        "guardrail_checks": _guardrail_checks(validation),
        "safety_invariants": _string_list(global_status.get("safety_invariants")),
        "readiness_checks": list(readiness_report.get("readiness_checks") or []),
        "forbidden_actions": _string_list(global_status.get("forbidden_actions")),
        "forbidden_apis": _string_list(global_status.get("forbidden_apis")),
        "audit_notes": _audit_notes(readiness_report, validation),
        "recommended_next_work": _string_list(global_status.get("recommended_next_work")),
        "ai_handoff_summary": _ai_handoff_summary(no_go_reasons, validation),
        "verification_commands": _string_list(global_status.get("verification_commands")),
        "source_reports": {
            "readiness_report_version": str(readiness_report.get("report_version") or ""),
            "global_status_report_version": str(global_status.get("report_version") or ""),
            "guardrail_report_version": str(guardrail_report.get("report_version") or ""),
        },
        "state_mutation": False,
        "execution_attempted": False,
        "real_desktop_actions": False,
        "external_llm_calls": False,
    }


def build_phase10_guardrail_display_report() -> dict[str, Any]:
    """Return the guardrail portion of the deterministic display report."""

    report = build_phase10_experiment_display_report()
    return {
        "report_version": report["report_version"],
        "project_phase": report["project_phase"],
        "dry_run": report["dry_run"],
        "read_only": report["read_only"],
        "debug_only": report["debug_only"],
        "guardrail_status": report["guardrail_status"],
        "guardrail_checks": report["guardrail_checks"],
        "no_go_reasons": report["no_go_reasons"],
        "go_for_phase10": report["go_for_phase10"],
    }


def build_phase10_cockpit_experiment_summary() -> dict[str, Any]:
    """Return a compact summary for cockpit chips and tests."""

    report = build_phase10_experiment_display_report()
    return {
        "summary_version": "phase10_experiment_display_summary_v1",
        "project_phase": report["project_phase"],
        "status": "NO-GO",
        "experiment_status": report["experiment_status"]["status"],
        "guardrail_status": report["guardrail_status"]["status"],
        "dry_run": report["dry_run"],
        "read_only": report["read_only"],
        "debug_only": report["debug_only"],
        "real_actions_enabled": report["real_actions_enabled"],
        "phase10_real_actions_implemented": report[
            "phase10_real_actions_implemented"
        ],
        "go_for_phase10": report["go_for_phase10"],
        "no_go_reason_count": len(report["no_go_reasons"]),
        "guardrail_check_count": len(report["guardrail_checks"]),
    }


def _experiment_status(no_go_reasons: list[str]) -> dict[str, Any]:
    return {
        "status": "no_go_display_only",
        "label": "NO-GO display only",
        "dry_run": True,
        "read_only": True,
        "debug_only": True,
        "real_action_attempted": False,
        "real_action_skipped": True,
        "blocker_count": len(no_go_reasons),
        "notes": [
            "Phase 10.5 displays deterministic experiment and guardrail results only.",
            "No Phase 10 real-action experiment is implemented.",
            "Cockpit display is not authorization.",
        ],
    }


def _guardrail_status(
    guardrail_report: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    summary = validation.get("validation_summary")
    if not isinstance(summary, dict):
        summary = {}
    return {
        "status": str(validation.get("status") or "unknown"),
        "validation_passed": validation.get("valid") is True,
        "validation_error_count": len(_list_value(validation.get("errors"))),
        "validation_warning_count": len(_list_value(validation.get("warnings"))),
        "unsafe_flag_count": len(_list_value(validation.get("unsafe_flags_detected"))),
        "audit_order_issue_count": len(
            [
                check
                for check in _list_value(validation.get("audit_order_checks"))
                if isinstance(check, dict) and check.get("passed") is not True
            ]
        ),
        "consistency_issue_count": len(
            [
                check
                for check in _list_value(validation.get("consistency_checks"))
                if isinstance(check, dict) and check.get("passed") is not True
            ]
        ),
        "replay_allowed_as_read_only": summary.get("replay_allowed_as_read_only")
        is True,
        "debug_focus": str(
            summary.get("recommended_debug_focus")
            or guardrail_report.get("debug_focus")
            or ""
        ),
    }


def _guardrail_checks(validation: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for source_key, group in (
        ("consistency_checks", "consistency"),
        ("audit_order_checks", "audit"),
    ):
        for check in _list_value(validation.get(source_key)):
            if not isinstance(check, dict):
                continue
            checks.append(
                {
                    "group": group,
                    "name": str(check.get("name") or "check"),
                    "passed": check.get("passed") is True,
                    "status": "pass" if check.get("passed") is True else "blocked",
                    "code": str(check.get("code") or ""),
                    "field": str(check.get("field") or ""),
                    "detail": str(check.get("detail") or ""),
                }
            )
    return checks


def _audit_notes(
    readiness_report: dict[str, Any],
    validation: dict[str, Any],
) -> list[str]:
    notes = _string_list(readiness_report.get("audit_notes"))
    event_names = [
        str(event.get("event_name") or "")
        for event in _list_value(validation.get("validation_bundle", {}))
        if isinstance(event, dict)
    ]
    if not event_names:
        event_names = _string_list(validation.get("audit_event_names"))
    notes.extend(
        [
            "Phase 10.5 endpoint returns deterministic display data only.",
            "No live desktop observation, action adapter, or runtime mutation is used.",
            "Copy helpers read already loaded report data only.",
        ]
    )
    if event_names:
        notes.append("Guardrail audit events: " + ", ".join(event_names))
    return _unique_strings(notes)


def _ai_handoff_summary(
    no_go_reasons: list[str],
    validation: dict[str, Any],
) -> str:
    validation_status = str(validation.get("status") or "unknown")
    return (
        "Phase 10.5 adds a read-only cockpit display for deterministic Phase "
        "10 experiment and guardrail results. The display remains NO-GO by "
        "default: dry_run, read_only, and debug_only are true; real actions "
        "are disabled; Phase 10 real actions are not implemented; and "
        "go_for_phase10 is false. Guardrail validation status is "
        f"{validation_status}. Current no-go reasons: "
        f"{', '.join(no_go_reasons)}. Readiness is not permission, cockpit "
        "display is not authorization, export/copy is not execution, and AI "
        "handoff is not AI control."
    )


def _list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str) and item]


def _unique_strings(values: list[str]) -> list[str]:
    unique_values: list[str] = []
    for value in values:
        if value and value not in unique_values:
            unique_values.append(value)
    return unique_values


__all__ = [
    "build_phase10_cockpit_experiment_summary",
    "build_phase10_experiment_display_report",
    "build_phase10_guardrail_display_report",
    "build_phase10_guardrail_validation_report",
    "build_phase10_release_candidate_bundle",
    "validate_phase10_release_candidate_bundle",
]
