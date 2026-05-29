"""Actuation v0: execute only approved wait contracts."""

from __future__ import annotations

import time
from typing import Any, Callable

from .capabilities import get_capability, is_action_executable


MAX_WAIT_DURATION_MS = 3000


class ActuationBlockedError(RuntimeError):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def execute_action_contract(
    action_contract: dict[str, Any],
    sleep_fn: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """Execute the only supported v0 action: approved wait."""

    action_type = str(action_contract.get("type") or "")
    status = str(action_contract.get("status") or "")
    executed = bool(action_contract.get("executed"))

    if not is_action_executable(action_type):
        capability = get_capability(action_type)
        raise ActuationBlockedError(str(capability.get("reason") or "Action is not executable."))

    if status != "approved_for_execution":
        raise ActuationBlockedError("Action contract is not approved for execution.")

    if executed:
        raise ActuationBlockedError("Action contract has already been executed.")

    duration_ms = _wait_duration_ms(action_contract)
    sleep_fn(duration_ms / 1000)

    return {
        "status": "executed",
        "type": "wait",
        "duration_ms": duration_ms,
        "executed": True,
    }


def _wait_duration_ms(action_contract: dict[str, Any]) -> int:
    parameters = action_contract.get("parameters")
    if not isinstance(parameters, dict):
        parameters = {}

    raw_duration = action_contract.get("duration_ms", parameters.get("duration_ms", 0))

    try:
        duration_ms = int(raw_duration)
    except (TypeError, ValueError):
        duration_ms = 0

    return max(0, min(duration_ms, MAX_WAIT_DURATION_MS))
