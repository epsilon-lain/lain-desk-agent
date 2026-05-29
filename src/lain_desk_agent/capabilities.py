"""Capability Registry v0: central action execution policy."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


_CAPABILITIES: dict[str, dict[str, Any]] = {
    "wait": {
        "enabled": True,
        "executable": True,
        "risk": "low",
        "reason": "Wait is the only enabled executable action in Capability Registry v0.",
    },
    "click": {
        "enabled": False,
        "executable": False,
        "risk": "medium",
        "reason": "Click execution is disabled in Capability Registry v0.",
    },
    "type": {
        "enabled": False,
        "executable": False,
        "risk": "high",
        "reason": "Typing execution is disabled in Capability Registry v0.",
    },
    "type_text": {
        "enabled": False,
        "executable": False,
        "risk": "high",
        "reason": "Typing execution is disabled in Capability Registry v0.",
    },
    "hotkey": {
        "enabled": False,
        "executable": False,
        "risk": "high",
        "reason": "Hotkey execution is disabled in Capability Registry v0.",
    },
    "press": {
        "enabled": False,
        "executable": False,
        "risk": "high",
        "reason": "Key press execution is disabled in Capability Registry v0.",
    },
    "scroll": {
        "enabled": False,
        "executable": False,
        "risk": "medium",
        "reason": "Scroll execution is disabled in Capability Registry v0.",
    },
    "switch_app": {
        "enabled": False,
        "executable": False,
        "risk": "medium",
        "reason": "App switching is disabled in Capability Registry v0.",
    },
}


def get_capabilities() -> dict[str, dict[str, Any]]:
    return deepcopy(_CAPABILITIES)


def get_capability(action_type: str) -> dict[str, Any]:
    capability = _CAPABILITIES.get(str(action_type or ""))
    if capability is None:
        return {
            "enabled": False,
            "executable": False,
            "risk": "unknown",
            "reason": f"Action type '{action_type}' is not registered in Capability Registry v0.",
        }

    return deepcopy(capability)


def is_action_executable(action_type: str) -> bool:
    capability = get_capability(action_type)
    return bool(capability.get("enabled")) and bool(capability.get("executable"))
