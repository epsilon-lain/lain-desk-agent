"""Read-only execution policy matrix for supported action types."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .capabilities import get_capability
from .permission_profile import get_current_permission_profile, get_permission_profile_payload


ACTION_TYPES = ["wait", "click", "type", "hotkey", "scroll", "switch_app"]
PROFILES = ["safe_readonly", "wait_only", "experimental_desktop_control"]


def execution_policy_payload() -> dict[str, Any]:
    current_profile = get_current_permission_profile()
    matrix = execution_policy_matrix()

    return {
        "current_profile": current_profile,
        "desktop_control": False,
        "action_types": list(ACTION_TYPES),
        "profiles": list(PROFILES),
        "matrix": matrix,
        "summary": execution_policy_summary(current_profile, matrix),
    }


def execution_policy_matrix() -> dict[str, dict[str, dict[str, Any]]]:
    profile_payload = get_permission_profile_payload()
    profiles = profile_payload.get("profiles")
    if not isinstance(profiles, dict):
        profiles = {}

    matrix: dict[str, dict[str, dict[str, Any]]] = {}
    for profile in PROFILES:
        profile_config = profiles.get(profile)
        if not isinstance(profile_config, dict):
            profile_config = {}

        allowed_actions = profile_config.get("allowed_actions")
        if not isinstance(allowed_actions, list):
            allowed_actions = []

        matrix[profile] = {
            action_type: _policy_entry(profile, action_type, allowed_actions)
            for action_type in ACTION_TYPES
        }

    return deepcopy(matrix)


def execution_policy_summary(
    profile: str | None = None,
    matrix: dict[str, dict[str, dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    current_profile = str(profile or get_current_permission_profile())
    policy_matrix = matrix if isinstance(matrix, dict) else execution_policy_matrix()
    profile_policy = policy_matrix.get(current_profile)
    if not isinstance(profile_policy, dict):
        profile_policy = {}

    executable_actions = [
        action_type
        for action_type in ACTION_TYPES
        if bool((profile_policy.get(action_type) or {}).get("executable"))
    ]

    return {
        "current_profile": current_profile,
        "desktop_control": False,
        "executable_actions": executable_actions,
        "blocked_actions_count": len(ACTION_TYPES) - len(executable_actions),
    }


def _policy_entry(
    profile: str,
    action_type: str,
    allowed_actions: list[Any],
) -> dict[str, Any]:
    capability = get_capability(action_type)
    capability_executable = bool(capability.get("enabled")) and bool(capability.get("executable"))
    allowed_by_profile = action_type in {str(action) for action in allowed_actions}
    executable = capability_executable and allowed_by_profile
    risk = _risk_for_action(action_type, capability)

    if executable and action_type == "wait":
        return {
            "allowed": True,
            "executable": True,
            "mode": "wait_only",
            "risk": risk,
            "reason": "Approved wait contracts may execute in this profile.",
        }

    if profile == "experimental_desktop_control" and action_type != "wait":
        return {
            "allowed": False,
            "executable": False,
            "mode": "future_experimental",
            "risk": risk,
            "reason": f"{_display_action(action_type)} is reserved for future experiments and remains non-executable.",
        }

    return {
        "allowed": False,
        "executable": False,
        "mode": "blocked",
        "risk": risk,
        "reason": _blocked_reason(profile, action_type, capability_executable, allowed_by_profile),
    }


def _blocked_reason(
    profile: str,
    action_type: str,
    capability_executable: bool,
    allowed_by_profile: bool,
) -> str:
    if not allowed_by_profile:
        return f"{_display_action(action_type)} is not allowed by the {profile} permission profile."

    if not capability_executable:
        return f"{_display_action(action_type)} is disabled by the Capability Registry."

    return f"{_display_action(action_type)} is blocked by the current execution policy."


def _risk_for_action(action_type: str, capability: dict[str, Any]) -> str:
    risk = str(capability.get("risk") or "")
    if risk in {"low", "medium", "high"}:
        return risk

    fallback = {
        "wait": "low",
        "click": "medium",
        "type": "high",
        "hotkey": "high",
        "scroll": "medium",
        "switch_app": "medium",
    }
    return fallback[action_type]


def _display_action(action_type: str) -> str:
    return action_type.replace("_", " ")
