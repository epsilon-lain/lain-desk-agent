"""Execution Permission Profile v0."""

from __future__ import annotations

import os
from copy import deepcopy
from typing import Any


PERMISSION_PROFILE_ENV = "LAIN_DESK_AGENT_PERMISSION_PROFILE"
DEFAULT_PERMISSION_PROFILE = "wait_only"
SAFE_FALLBACK_PROFILE = "safe_readonly"

_PERMISSION_PROFILES: dict[str, dict[str, Any]] = {
    "safe_readonly": {
        "allowed_actions": [],
        "reason": "No actions are executable in the safe_readonly permission profile.",
    },
    "wait_only": {
        "allowed_actions": ["wait"],
        "reason": "Only wait actions are executable in the wait_only permission profile.",
    },
    "experimental_desktop_control": {
        "allowed_actions": ["wait"],
        "reason": "Experimental desktop control is named but does not enable mouse or keyboard actions yet.",
    },
}


def get_current_permission_profile() -> str:
    profile = os.environ.get(PERMISSION_PROFILE_ENV, DEFAULT_PERMISSION_PROFILE).strip()

    if profile in _PERMISSION_PROFILES:
        return profile

    return SAFE_FALLBACK_PROFILE


def is_profile_allowed_for_action(action_type: str) -> bool:
    profile = get_current_permission_profile()
    profile_config = _PERMISSION_PROFILES[profile]
    return str(action_type or "") in profile_config["allowed_actions"]


def get_permission_profile_payload() -> dict[str, Any]:
    profile = get_current_permission_profile()
    return {
        "profile": profile,
        "default_profile": DEFAULT_PERMISSION_PROFILE,
        "profiles": deepcopy(_PERMISSION_PROFILES),
    }


def permission_profile_block_reason(action_type: str) -> str:
    profile = get_current_permission_profile()
    return (
        f"Blocked by permission profile '{profile}': action type '{action_type}' "
        "is not allowed for execution."
    )
