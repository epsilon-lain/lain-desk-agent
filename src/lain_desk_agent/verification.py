"""Verification v0: verify wait-only execution without expecting UI changes."""

from __future__ import annotations

from typing import Any


def verify_execution(
    action_contract: dict[str, Any],
    execution_result: dict[str, Any],
    post_observation: dict[str, Any] | None,
) -> dict[str, Any]:
    """Verify an executed action using a safe post-execution observation."""

    action_type = str(action_contract.get("type") or "")

    if action_type != "wait":
        return _unknown_result(
            "Verification v0 only supports wait actions.",
            expected_change="unknown",
        )

    if execution_result.get("status") != "executed" or execution_result.get("type") != "wait":
        return _unknown_result("Wait action did not report successful execution.")

    if not isinstance(post_observation, dict) or not post_observation:
        return _unknown_result("Post-execution observation was not available.")

    return {
        "status": "verified",
        "reason": "Wait action completed and a post-execution observation was captured.",
        "expected_change": "none",
        "confidence": 0.8,
    }


def verification_failed_result(reason: str) -> dict[str, Any]:
    return _unknown_result(f"Post-execution observation failed: {reason}")


def _unknown_result(reason: str, expected_change: str = "none") -> dict[str, Any]:
    return {
        "status": "unknown",
        "reason": reason,
        "expected_change": expected_change,
        "confidence": 0.0,
    }
