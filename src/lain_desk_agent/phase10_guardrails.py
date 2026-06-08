"""Deterministic Phase 10.3 release-candidate guardrail validation.

This module validates imported release-candidate bundles as read-only debug
data. It never observes live OS state, mutates runtime state, calls an
action-performing endpoint, or enables real desktop actions.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .phase10_readiness import PHASE10_NO_GO_REASONS, build_phase10_readiness_report


PHASE10_GUARDRAIL_BUNDLE_TYPE = "phase10_release_candidate_bundle"
PHASE10_GUARDRAIL_BUNDLE_VERSION = "phase10_release_candidate_bundle_v1"
PHASE10_GUARDRAIL_REPORT_VERSION = "phase10_guardrail_report_v1"
PHASE10_GUARDRAIL_VALIDATION_BUNDLE_VERSION = "phase10_guardrail_validation_bundle_v1"
PHASE10_GUARDRAIL_PROJECT_PHASE = "phase_10_3_release_candidate_guardrails"

PHASE10_GUARDRAIL_REQUIRED_BUNDLE_FIELDS = (
    "bundle_type",
    "bundle_version",
    "report_version",
    "project_phase",
    "phase10_report",
    "ai_handoff_summary",
    "safety_boundary_statement",
)

PHASE10_GUARDRAIL_REQUIRED_REPORT_FIELDS = (
    "report_version",
    "project_phase",
    "dry_run",
    "read_only",
    "debug_only",
    "real_actions_enabled",
    "phase10_real_actions_implemented",
    "go_for_phase10",
    "gate_blockers",
    "readiness",
    "approval",
    "audit_event_names",
    "audit_timeline",
    "scope",
    "consistency",
)

PHASE10_GUARDRAIL_AUDIT_ORDER = (
    "phase10_guardrail_bundle_loaded",
    "phase10_guardrail_safety_boundary_checked",
    "phase10_guardrail_readiness_checked",
    "phase10_guardrail_scope_checked",
    "phase10_guardrail_no_go_recorded",
    "phase10_guardrail_read_only_replay_allowed",
)

PHASE10_GUARDRAIL_SENSITIVE_KEY_FRAGMENTS = (
    "token",
    "secret",
    "api_key",
    "apikey",
    "password",
    "credential",
    "private_key",
    "access_key",
)

PHASE10_GUARDRAIL_FORBIDDEN_ACTION_TYPES = (
    "click",
    "type",
    "type_text",
    "hotkey",
    "press",
    "scroll",
    "switch_app",
)

PHASE10_GUARDRAIL_ACTION_ENDPOINT_FRAGMENT = "/" + "execute"


def build_phase10_release_candidate_bundle() -> dict[str, Any]:
    """Build a deterministic local Phase 10.3 release-candidate bundle."""

    readiness_report = build_phase10_readiness_report()
    no_go_reasons = _string_list(readiness_report.get("no_go_reasons"))
    if not no_go_reasons:
        no_go_reasons = list(PHASE10_NO_GO_REASONS)

    phase10_report = {
        "report_version": PHASE10_GUARDRAIL_REPORT_VERSION,
        "project_phase": PHASE10_GUARDRAIL_PROJECT_PHASE,
        "dry_run": True,
        "read_only": True,
        "debug_only": True,
        "real_action_enabled": False,
        "real_actions_enabled": False,
        "phase10_real_actions_implemented": False,
        "go_for_phase10": False,
        "gate_blockers": no_go_reasons,
        "readiness": {
            "status": "no_go",
            "ready": False,
            "blockers": no_go_reasons,
            "readiness_is_permission": False,
        },
        "approval": {
            "explicit_phase10_approval": False,
            "approval_status": "not_recorded",
            "approval_bound_to_contract": False,
        },
        "audit_event_names": list(PHASE10_GUARDRAIL_AUDIT_ORDER),
        "audit_timeline": _phase10_guardrail_audit_timeline(),
        "scope": {
            "scope_type": "release_candidate_guardrails",
            "one_window_only": True,
            "one_target_only": True,
            "sandbox_window_selected": False,
            "target_selected": False,
            "allowed_action_types": [],
            "forbidden_action_types": list(PHASE10_GUARDRAIL_FORBIDDEN_ACTION_TYPES),
            "desktop_control_apis_allowed": False,
            "new_backend_endpoints": False,
        },
        "consistency": {
            "readiness_is_permission": False,
            "cockpit_display_authorization": False,
            "export_import_replay_execution": False,
            "ai_handoff_control": False,
            "permission_policy_changed": False,
        },
    }

    bundle = {
        "bundle_type": PHASE10_GUARDRAIL_BUNDLE_TYPE,
        "bundle_version": PHASE10_GUARDRAIL_BUNDLE_VERSION,
        "report_version": PHASE10_GUARDRAIL_REPORT_VERSION,
        "project_phase": PHASE10_GUARDRAIL_PROJECT_PHASE,
        "phase10_report": phase10_report,
        "ai_handoff_summary": (
            "Phase 10.3 validates release-candidate guardrails as local "
            "read-only data. Real desktop actions remain disabled, readiness "
            "is not permission, cockpit display is not authorization, "
            "export/import/replay is not execution, and AI handoff is not AI "
            "control."
        ),
        "safety_boundary_statement": (
            "Phase 10.3 release-candidate guardrails are dry-run/read-only/"
            "debug-only. No real desktop actions, no action-performing "
            "endpoint, no approval/execute/real-action controls, and no "
            "permission changes are allowed."
        ),
    }
    return _sanitize_bundle_value(bundle)


def validate_phase10_release_candidate_bundle(bundle: Any) -> dict[str, Any]:
    """Validate an imported Phase 10.3 bundle without executing anything."""

    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    consistency_checks: list[dict[str, Any]] = []
    audit_order_checks: list[dict[str, Any]] = []

    if not isinstance(bundle, dict):
        _validation_error(
            errors,
            "missing_bundle_field",
            "bundle",
            "Release-candidate bundle must be a JSON object.",
        )
        return _validation_result(
            bundle, errors, warnings, consistency_checks, audit_order_checks
        )

    for field_name in PHASE10_GUARDRAIL_REQUIRED_BUNDLE_FIELDS:
        if field_name not in bundle:
            _validation_error(
                errors,
                "missing_bundle_field",
                field_name,
                "Required top-level release-candidate bundle field is missing.",
            )

    sensitive_paths = _sensitive_key_paths(bundle)
    if sensitive_paths:
        _validation_error(
            errors,
            "suspicious_sensitive_key",
            ", ".join(sensitive_paths[:5]),
            "Bundle contains key names that look like private material.",
        )

    if str(bundle.get("bundle_type") or "") != PHASE10_GUARDRAIL_BUNDLE_TYPE:
        _validation_error(
            errors,
            "unsupported_bundle_type",
            "bundle_type",
            f"Expected {PHASE10_GUARDRAIL_BUNDLE_TYPE}.",
        )
    if str(bundle.get("bundle_version") or "") != PHASE10_GUARDRAIL_BUNDLE_VERSION:
        _validation_error(
            errors,
            "unsupported_bundle_version",
            "bundle_version",
            f"Expected {PHASE10_GUARDRAIL_BUNDLE_VERSION}.",
        )
    if str(bundle.get("report_version") or "") != PHASE10_GUARDRAIL_REPORT_VERSION:
        _validation_error(
            errors,
            "invalid_report_version",
            "report_version",
            f"Expected {PHASE10_GUARDRAIL_REPORT_VERSION}.",
        )
    if str(bundle.get("project_phase") or "") != PHASE10_GUARDRAIL_PROJECT_PHASE:
        _validation_error(
            errors,
            "unsupported_project_phase",
            "project_phase",
            f"Expected {PHASE10_GUARDRAIL_PROJECT_PHASE}.",
        )

    phase10_report = bundle.get("phase10_report")
    if not isinstance(phase10_report, dict):
        _validation_error(
            errors,
            "missing_phase10_report",
            "phase10_report",
            "Bundle must contain a Phase 10 guardrail report object.",
        )
        return _validation_result(
            bundle, errors, warnings, consistency_checks, audit_order_checks
        )

    for field_name in PHASE10_GUARDRAIL_REQUIRED_REPORT_FIELDS:
        if field_name not in phase10_report:
            _validation_error(
                errors,
                "missing_bundle_field",
                f"phase10_report.{field_name}",
                "Required Phase 10 guardrail report field is missing.",
            )

    _validate_phase10_flags(phase10_report, errors)
    _validate_phase10_readiness_and_blockers(phase10_report, errors, consistency_checks)
    _validate_phase10_approval(phase10_report, errors, consistency_checks)
    _validate_phase10_scope(phase10_report, errors, consistency_checks)
    _validate_phase10_audit_order(phase10_report, errors, audit_order_checks)
    _validate_phase10_consistency(phase10_report, errors, consistency_checks)
    _validate_phase10_boundary_text(bundle, errors, consistency_checks)

    for finding in _execute_path_findings(bundle):
        _validation_error(
            errors,
            "execute_path_in_bundle",
            finding,
            "Release-candidate guardrail bundles must not define action-performing paths.",
        )

    return _validation_result(
        bundle, errors, warnings, consistency_checks, audit_order_checks
    )


def build_phase10_guardrail_validation_report(bundle: Any | None = None) -> dict[str, Any]:
    """Return a deterministic validation report for a bundle or the local fixture."""

    source_bundle = build_phase10_release_candidate_bundle() if bundle is None else bundle
    validation = validate_phase10_release_candidate_bundle(source_bundle)
    return {
        "report_version": PHASE10_GUARDRAIL_REPORT_VERSION,
        "project_phase": PHASE10_GUARDRAIL_PROJECT_PHASE,
        "dry_run": True,
        "read_only": True,
        "debug_only": True,
        "real_actions_enabled": False,
        "phase10_real_actions_implemented": False,
        "go_for_phase10": False,
        "validation": validation,
        "validation_summary": validation["validation_summary"],
        "validation_bundle": validation["validation_bundle"],
        "debug_focus": validation["recommended_debug_focus"],
        "state_mutation": False,
        "execution_attempted": False,
    }


def _validate_phase10_flags(
    report: dict[str, Any],
    errors: list[dict[str, str]],
) -> None:
    if report.get("dry_run") is not True or report.get("read_only") is not True or report.get("debug_only") is not True:
        _validation_error(
            errors,
            "non_dry_run_bundle",
            "phase10_report.dry_run",
            "Phase 10.3 bundles must remain dry-run/read-only/debug-only.",
        )
        _validation_error(
            errors,
            "unsafe_bundle_flags",
            "phase10_report.dry_run",
            "Unsafe runtime mode flag detected.",
        )
    if report.get("real_actions_enabled") is True or report.get("real_action_enabled") is True:
        _validation_error(
            errors,
            "real_action_enabled_in_bundle",
            "phase10_report.real_actions_enabled",
            "Release-candidate bundles must keep real actions disabled.",
        )
        _validation_error(
            errors,
            "unsafe_bundle_flags",
            "phase10_report.real_actions_enabled",
            "Unsafe real-action flag detected.",
        )
    if report.get("phase10_real_actions_implemented") is True:
        _validation_error(
            errors,
            "phase10_real_actions_implemented_in_bundle",
            "phase10_report.phase10_real_actions_implemented",
            "Phase 10.3 guardrails must not claim real actions are implemented.",
        )
    if report.get("go_for_phase10") is True:
        _validation_error(
            errors,
            "go_for_phase10_in_bundle",
            "phase10_report.go_for_phase10",
            "Phase 10.3 guardrail bundles must remain NO-GO.",
        )


def _validate_phase10_readiness_and_blockers(
    report: dict[str, Any],
    errors: list[dict[str, str]],
    consistency_checks: list[dict[str, Any]],
) -> None:
    blockers = _string_list(report.get("gate_blockers"))
    readiness = report.get("readiness") if isinstance(report.get("readiness"), dict) else {}
    readiness_blockers = _string_list(readiness.get("blockers"))
    readiness_ready = readiness.get("ready") is True or str(readiness.get("status") or "").lower() in {"go", "ready"}

    _record_check(
        consistency_checks,
        "gate_blockers_present_for_no_go",
        bool(blockers),
        "missing_gate_blockers",
        "phase10_report.gate_blockers",
        "NO-GO release-candidate bundles must include gate blockers.",
        errors,
    )
    _record_check(
        consistency_checks,
        "readiness_not_ready",
        not readiness_ready,
        "readiness_go_in_bundle",
        "phase10_report.readiness",
        "Readiness cannot be GO in Phase 10.3 guardrail bundles.",
        errors,
    )
    _record_check(
        consistency_checks,
        "readiness_blockers_match_gate_blockers",
        set(readiness_blockers) == set(blockers),
        "readiness_blocker_mismatch",
        "phase10_report.readiness.blockers",
        "Readiness blockers must match gate blockers for reproducible handoff.",
        errors,
    )


def _validate_phase10_approval(
    report: dict[str, Any],
    errors: list[dict[str, str]],
    consistency_checks: list[dict[str, Any]],
) -> None:
    approval = report.get("approval") if isinstance(report.get("approval"), dict) else {}
    approved = (
        approval.get("explicit_phase10_approval") is True
        or approval.get("approved") is True
        or str(approval.get("approval_status") or "").lower() in {"approved", "granted"}
    )
    _record_check(
        consistency_checks,
        "approval_not_granted",
        not approved,
        "approval_implies_real_action",
        "phase10_report.approval",
        "Phase 10.3 guardrail validation must not import real-action approval.",
        errors,
    )


def _validate_phase10_scope(
    report: dict[str, Any],
    errors: list[dict[str, str]],
    consistency_checks: list[dict[str, Any]],
) -> None:
    scope = report.get("scope") if isinstance(report.get("scope"), dict) else {}
    allowed_actions = _string_list(scope.get("allowed_action_types"))
    forbidden_action_set = set(PHASE10_GUARDRAIL_FORBIDDEN_ACTION_TYPES)
    unsafe_actions = [action for action in allowed_actions if action in forbidden_action_set]

    _record_check(
        consistency_checks,
        "scope_is_limited",
        scope.get("one_window_only") is True and scope.get("one_target_only") is True,
        "scope_not_limited",
        "phase10_report.scope",
        "Release-candidate scope must remain one-window and one-target limited.",
        errors,
    )
    _record_check(
        consistency_checks,
        "no_desktop_actions_allowed",
        not unsafe_actions and scope.get("desktop_control_apis_allowed") is not True,
        "unsafe_action_type",
        "phase10_report.scope.allowed_action_types",
        "Release-candidate guardrails must not allow desktop action types.",
        errors,
    )
    _record_check(
        consistency_checks,
        "no_new_backend_endpoints",
        scope.get("new_backend_endpoints") is not True,
        "mutation_endpoint_in_bundle",
        "phase10_report.scope.new_backend_endpoints",
        "Phase 10.3 must not add backend endpoints for guardrail validation.",
        errors,
    )


def _validate_phase10_audit_order(
    report: dict[str, Any],
    errors: list[dict[str, str]],
    audit_order_checks: list[dict[str, Any]],
) -> None:
    event_names = _string_list(report.get("audit_event_names"))
    timeline = report.get("audit_timeline")
    if not isinstance(timeline, list) or not timeline:
        _validation_error(
            errors,
            "missing_audit_timeline",
            "phase10_report.audit_timeline",
            "Release-candidate guardrail bundles require audit timeline data.",
        )
        return

    timeline_names: list[str] = []
    previous_order = 0
    for index, event in enumerate(timeline):
        field_path = f"phase10_report.audit_timeline[{index}]"
        if not isinstance(event, dict):
            _validation_error(errors, "malformed_audit_event", field_path, "Audit entries must be objects.")
            continue
        event_name = str(event.get("event_name") or "")
        order = event.get("order")
        if not event_name:
            _validation_error(errors, "malformed_audit_event", f"{field_path}.event_name", "Audit event name is missing.")
        if not isinstance(order, int) or order <= previous_order:
            _validation_error(errors, "inconsistent_audit_order", f"{field_path}.order", "Audit order must be strictly increasing.")
        previous_order = order if isinstance(order, int) else previous_order
        if event_name:
            timeline_names.append(event_name)

    _record_check(
        audit_order_checks,
        "audit_event_names_match_timeline",
        event_names == timeline_names,
        "inconsistent_audit_order",
        "phase10_report.audit_event_names",
        "audit_event_names must match audit_timeline event order.",
        errors,
    )

    positions = {event_name: index for index, event_name in enumerate(event_names)}
    for event_name in PHASE10_GUARDRAIL_AUDIT_ORDER:
        _record_check(
            audit_order_checks,
            f"{event_name}_present",
            event_name in positions,
            "missing_required_audit_event",
            "phase10_report.audit_event_names",
            f"{event_name} is required for Phase 10.3 guardrail validation.",
            errors,
        )
    for left, right in zip(PHASE10_GUARDRAIL_AUDIT_ORDER, PHASE10_GUARDRAIL_AUDIT_ORDER[1:]):
        if left in positions and right in positions:
            _record_check(
                audit_order_checks,
                f"{left}_before_{right}",
                positions[left] < positions[right],
                "inconsistent_audit_order",
                "phase10_report.audit_event_names",
                f"{left} must occur before {right}.",
                errors,
            )


def _validate_phase10_consistency(
    report: dict[str, Any],
    errors: list[dict[str, str]],
    consistency_checks: list[dict[str, Any]],
) -> None:
    consistency = report.get("consistency") if isinstance(report.get("consistency"), dict) else {}
    for key, code, detail in [
        ("readiness_is_permission", "readiness_treated_as_permission", "Readiness must remain non-permission."),
        ("cockpit_display_authorization", "cockpit_display_treated_as_authorization", "Cockpit display must remain non-authorization."),
        ("export_import_replay_execution", "replay_treated_as_execution", "Export/import/replay must remain non-execution."),
        ("ai_handoff_control", "ai_handoff_treated_as_control", "AI handoff must remain non-control."),
        ("permission_policy_changed", "permission_policy_changed", "Permission policy must not change in Phase 10.3."),
    ]:
        _record_check(
            consistency_checks,
            f"{key}_is_false",
            consistency.get(key) is False,
            code,
            f"phase10_report.consistency.{key}",
            detail,
            errors,
        )


def _validate_phase10_boundary_text(
    bundle: dict[str, Any],
    errors: list[dict[str, str]],
    consistency_checks: list[dict[str, Any]],
) -> None:
    boundary = str(bundle.get("safety_boundary_statement") or "").lower()
    for phrase, code in [
        ("dry-run", "missing_safety_boundary_statement"),
        ("read-only", "missing_safety_boundary_statement"),
        ("no real desktop actions", "missing_safety_boundary_statement"),
        ("no action-performing endpoint", "missing_safety_boundary_statement"),
        ("no permission changes", "missing_safety_boundary_statement"),
    ]:
        _record_check(
            consistency_checks,
            f"safety_boundary_mentions_{phrase}",
            phrase in boundary,
            code,
            "safety_boundary_statement",
            f"Safety boundary must mention {phrase}.",
            errors,
        )


def _validation_result(
    bundle: Any,
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
    consistency_checks: list[dict[str, Any]],
    audit_order_checks: list[dict[str, Any]],
) -> dict[str, Any]:
    phase10_report = (
        bundle.get("phase10_report")
        if isinstance(bundle, dict) and isinstance(bundle.get("phase10_report"), dict)
        else {}
    )
    error_codes = _unique_strings([error["code"] for error in errors])
    warning_codes = _unique_strings([warning["code"] for warning in warnings])
    sensitive_key_findings = _sensitive_key_paths(bundle)
    unsafe_flags = _unsafe_flags(error_codes, warning_codes, sensitive_key_findings)
    replay_allowed = not errors
    debug_focus = _debug_focus(
        error_codes,
        warning_codes,
        _string_list(phase10_report.get("gate_blockers")),
    )
    validation_summary = {
        "validation_passed": replay_allowed,
        "validation_errors": error_codes,
        "validation_warnings": warning_codes,
        "unsafe_flags_detected": unsafe_flags,
        "consistency_checks": consistency_checks,
        "audit_order_checks": audit_order_checks,
        "sensitive_key_findings": sensitive_key_findings,
        "replay_allowed_as_read_only": replay_allowed,
        "recommended_debug_focus": debug_focus,
    }
    validation_bundle = _validation_bundle(bundle, validation_summary, errors, warnings)

    return {
        "valid": replay_allowed,
        "status": "valid" if replay_allowed else "blocked",
        "error_codes": error_codes,
        "errors": errors,
        "warning_codes": warning_codes,
        "warnings": warnings,
        "validation_passed": replay_allowed,
        "validation_errors": error_codes,
        "validation_warnings": warning_codes,
        "bundle_version": str(bundle.get("bundle_version") or "") if isinstance(bundle, dict) else "",
        "report_version": (
            str(bundle.get("report_version") or phase10_report.get("report_version") or "")
            if isinstance(bundle, dict)
            else ""
        ),
        "safety_boundary_confirmed": _safety_boundary_confirmed(bundle) and replay_allowed,
        "unsafe_flags_detected": unsafe_flags,
        "consistency_checks": consistency_checks,
        "audit_order_checks": audit_order_checks,
        "sensitive_key_findings": sensitive_key_findings,
        "replay_allowed_as_read_only": replay_allowed,
        "recommended_debug_focus": debug_focus,
        "validation_summary": validation_summary,
        "validation_bundle": validation_bundle,
    }


def _validation_bundle(
    bundle: Any,
    validation_summary: dict[str, Any],
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> dict[str, Any]:
    sanitized_bundle = _sanitize_bundle_value(bundle)
    return {
        "bundle_type": "phase10_guardrail_validation_bundle",
        "bundle_version": PHASE10_GUARDRAIL_VALIDATION_BUNDLE_VERSION,
        "source_bundle_digest": _stable_digest(sanitized_bundle),
        "source_bundle_redacted": sanitized_bundle,
        "validation_summary": _sanitize_bundle_value(validation_summary),
        "errors": _sanitize_bundle_value(errors),
        "warnings": _sanitize_bundle_value(warnings),
        "dry_run": True,
        "read_only": True,
        "debug_only": True,
        "real_desktop_actions": False,
        "state_mutation": False,
        "execution_attempted": False,
    }


def _phase10_guardrail_audit_timeline() -> list[dict[str, Any]]:
    return [
        {
            "order": index + 1,
            "event_name": event_name,
            "module": "phase10_guardrails",
            "outcome": "recorded",
        }
        for index, event_name in enumerate(PHASE10_GUARDRAIL_AUDIT_ORDER)
    ]


def _record_check(
    checks: list[dict[str, Any]],
    name: str,
    passed: bool,
    code: str,
    field: str,
    detail: str,
    errors: list[dict[str, str]],
) -> None:
    checks.append(
        {
            "name": name,
            "passed": bool(passed),
            "code": "" if passed else code,
            "field": field,
            "detail": "" if passed else detail,
        }
    )
    if not passed:
        _validation_error(errors, code, field, detail)


def _validation_error(
    errors: list[dict[str, str]],
    code: str,
    field: str,
    detail: str,
) -> None:
    errors.append({"code": code, "field": field, "detail": detail})


def _execute_path_findings(value: Any, path: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            text_key = str(key)
            current_path = f"{path}.{text_key}" if path else text_key
            if (
                isinstance(item, str)
                and PHASE10_GUARDRAIL_ACTION_ENDPOINT_FRAGMENT in item
                and _is_endpoint_like_key(text_key)
            ):
                findings.append(current_path)
            findings.extend(_execute_path_findings(item, current_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            current_path = f"{path}[{index}]" if path else f"[{index}]"
            findings.extend(_execute_path_findings(item, current_path))
    return findings


def _is_endpoint_like_key(key: str) -> bool:
    lowered = key.lower()
    return any(fragment in lowered for fragment in ("endpoint", "path", "route", "url", "fetch"))


def _sensitive_key_paths(value: Any, path: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            text_key = str(key)
            current_path = f"{path}.{text_key}" if path else text_key
            if _is_sensitive_key(text_key):
                paths.append(current_path)
            paths.extend(_sensitive_key_paths(item, current_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            current_path = f"{path}[{index}]" if path else f"[{index}]"
            paths.extend(_sensitive_key_paths(item, current_path))
    return paths


def _is_sensitive_key(key: str) -> bool:
    normalized = key.lower()
    return any(fragment in normalized for fragment in PHASE10_GUARDRAIL_SENSITIVE_KEY_FRAGMENTS)


def _nested_true(value: Any, key_name: str) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key) == key_name and item is True:
                return True
            if _nested_true(item, key_name):
                return True
    if isinstance(value, list):
        return any(_nested_true(item, key_name) for item in value)
    return False


def _unsafe_flags(
    error_codes: list[str],
    warning_codes: list[str],
    sensitive_key_findings: list[str],
) -> list[str]:
    unsafe_codes = {
        "unsafe_bundle_flags",
        "real_action_enabled_in_bundle",
        "phase10_real_actions_implemented_in_bundle",
        "go_for_phase10_in_bundle",
        "readiness_go_in_bundle",
        "approval_implies_real_action",
        "unsafe_action_type",
        "execute_path_in_bundle",
        "mutation_endpoint_in_bundle",
        "permission_policy_changed",
        "suspicious_sensitive_key",
    }
    flags = [code for code in error_codes + warning_codes if code in unsafe_codes]
    if sensitive_key_findings and "suspicious_sensitive_key" not in flags:
        flags.append("suspicious_sensitive_key")
    return _unique_strings(flags)


def _debug_focus(
    error_codes: list[str],
    warning_codes: list[str],
    gate_blockers: list[str],
) -> str:
    codes = set(error_codes)
    codes.update(warning_codes)
    codes.update(gate_blockers)
    focus_rules = [
        ("suspicious_sensitive_key", "remove private or credential-like fields from the bundle"),
        ("unsafe_bundle_flags", "inspect dry-run and real-action flags"),
        ("real_action_enabled_in_bundle", "confirm real actions remain disabled"),
        ("go_for_phase10_in_bundle", "confirm Phase 10 remains NO-GO"),
        ("readiness_go_in_bundle", "inspect readiness status and blockers"),
        ("approval_implies_real_action", "remove approval-like real-action state"),
        ("inconsistent_audit_order", "inspect audit event ordering"),
        ("missing_required_audit_event", "restore required guardrail audit events"),
        ("unsafe_action_type", "remove desktop action types from scope"),
        ("execute_path_in_bundle", "remove action-performing endpoint references"),
        ("permission_policy_changed", "restore permission policy separation"),
        ("phase10_real_actions_not_implemented", "confirm no real-action implementation is present"),
        ("real_actions_disabled", "confirm disabled real-action state is expected"),
    ]
    focus = [recommendation for code, recommendation in focus_rules if code in codes]
    return "; ".join(focus[:4]) if focus else "review guardrail validation summary and audit order"


def _safety_boundary_confirmed(bundle: Any) -> bool:
    if not isinstance(bundle, dict):
        return False
    boundary = str(bundle.get("safety_boundary_statement") or "").lower()
    required_phrases = (
        "dry-run",
        "read-only",
        "no real desktop actions",
        "no action-performing endpoint",
        "no permission changes",
    )
    return all(phrase in boundary for phrase in required_phrases)


def _sanitize_bundle_value(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            text_key = str(key)
            sanitized[text_key] = (
                "[redacted-sensitive-key]" if _is_sensitive_key(text_key) else _sanitize_bundle_value(item)
            )
        return sanitized
    if isinstance(value, list):
        return [_sanitize_bundle_value(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _stable_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


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
