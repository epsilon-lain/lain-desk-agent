from __future__ import annotations

import os
import unittest
from unittest.mock import patch

import _path  # noqa: F401
from lain_desk_agent.actuation import ActuationBlockedError, execute_action_contract
from lain_desk_agent.permission_profile import PERMISSION_PROFILE_ENV
from lain_desk_agent.main import (
    action_blocked_event,
    action_contract_from_execute_payload,
    action_executed_event,
    action_execution_requested_event,
    action_verification_failed_event,
    action_verified_event,
)


class WaitOnlyActuationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._profile_patch = patch.dict(os.environ, {PERMISSION_PROFILE_ENV: "wait_only"})
        self._profile_patch.start()

    def tearDown(self) -> None:
        self._profile_patch.stop()

    def test_approved_wait_contract_executes_and_caps_duration(self) -> None:
        slept: list[float] = []
        contract = {
            "action_id": "action_wait_0001",
            "source_proposal_id": "proposal_wait_0001",
            "type": "wait",
            "parameters": {"duration_ms": 5000},
            "status": "approved_for_execution",
            "executed": False,
        }

        result = execute_action_contract(contract, sleep_fn=slept.append)

        self.assertEqual(slept, [3.0])
        self.assertEqual(
            result,
            {
                "status": "executed",
                "type": "wait",
                "duration_ms": 3000,
                "executed": True,
            },
        )

    def test_preview_only_click_contract_is_blocked(self) -> None:
        with self.assertRaises(ActuationBlockedError) as context:
            execute_action_contract(
                {
                    "action_id": "action_0001",
                    "type": "click",
                    "status": "preview_only",
                    "executed": False,
                },
                sleep_fn=lambda _: None,
            )

        self.assertEqual(
            context.exception.reason,
            "Blocked by Capability Registry: Click execution is disabled in Capability Registry v0.",
        )

    def test_switch_app_contract_is_blocked(self) -> None:
        with self.assertRaises(ActuationBlockedError) as context:
            execute_action_contract(
                {
                    "action_id": "action_0001",
                    "type": "switch_app",
                    "status": "approved_for_execution",
                    "executed": False,
                },
                sleep_fn=lambda _: None,
            )

        self.assertEqual(
            context.exception.reason,
            "Blocked by Capability Registry: App switching is disabled in Capability Registry v0.",
        )

    def test_type_contract_is_blocked_by_capability_registry(self) -> None:
        with self.assertRaises(ActuationBlockedError) as context:
            execute_action_contract(
                {
                    "action_id": "action_type_0001",
                    "type": "type",
                    "status": "approved_for_execution",
                    "executed": False,
                },
                sleep_fn=lambda _: None,
            )

        self.assertEqual(
            context.exception.reason,
            "Blocked by Capability Registry: Typing execution is disabled in Capability Registry v0.",
        )

    def test_wait_contract_is_blocked_by_safe_readonly_profile(self) -> None:
        with patch.dict(os.environ, {PERMISSION_PROFILE_ENV: "safe_readonly"}):
            with self.assertRaises(ActuationBlockedError) as context:
                execute_action_contract(
                    {
                        "action_id": "action_wait_safe_readonly",
                        "type": "wait",
                        "status": "approved_for_execution",
                        "executed": False,
                    },
                    sleep_fn=lambda _: None,
                )

        self.assertEqual(
            context.exception.reason,
            "Blocked by permission profile 'safe_readonly': action type 'wait' is not allowed for execution.",
        )

    def test_preview_only_wait_contract_is_blocked(self) -> None:
        with self.assertRaises(ActuationBlockedError) as context:
            execute_action_contract(
                {
                    "action_id": "action_wait_0002",
                    "type": "wait",
                    "status": "preview_only",
                    "executed": False,
                },
                sleep_fn=lambda _: None,
            )

        self.assertEqual(context.exception.reason, "Action contract is not approved for execution.")

    def test_executed_wait_contract_is_blocked(self) -> None:
        with self.assertRaises(ActuationBlockedError) as context:
            execute_action_contract(
                {
                    "action_id": "action_wait_0003",
                    "type": "wait",
                    "status": "approved_for_execution",
                    "executed": True,
                },
                sleep_fn=lambda _: None,
            )

        self.assertEqual(context.exception.reason, "Action contract has already been executed.")

    def test_execute_payload_accepts_wrapped_or_direct_contract(self) -> None:
        contract = {"action_id": "action_wait_0004", "type": "wait"}

        self.assertIs(action_contract_from_execute_payload({"action_contract": contract}), contract)
        self.assertEqual(action_contract_from_execute_payload(contract), contract)

    def test_execution_audit_events_use_small_contract_fields(self) -> None:
        contract = {
            "action_id": "action_wait_0005",
            "source_proposal_id": "proposal_wait_0005",
            "type": "wait",
            "status": "approved_for_execution",
            "executed": False,
        }
        result = {
            "status": "executed",
            "type": "wait",
            "duration_ms": 250,
            "executed": True,
        }

        requested = action_execution_requested_event(contract, task="wait")
        executed = action_executed_event(contract, result, task="wait")
        blocked = action_blocked_event(contract, "blocked for test", task="wait")

        self.assertEqual(requested["type"], "action.execution_requested")
        self.assertEqual(executed["type"], "action.executed")
        self.assertEqual(blocked["type"], "action.blocked")
        self.assertEqual(requested["action_contract_type"], "wait")
        self.assertEqual(executed["result"], result)
        self.assertIs(executed["executed"], True)
        self.assertEqual(blocked["reason"], "blocked for test")

    def test_verification_audit_events_use_small_contract_fields(self) -> None:
        contract = {
            "action_id": "action_wait_0006",
            "source_proposal_id": "proposal_wait_0006",
            "type": "wait",
            "status": "approved_for_execution",
            "executed": False,
        }
        result = {
            "status": "executed",
            "type": "wait",
            "duration_ms": 100,
            "executed": True,
        }
        verification_result = {
            "status": "verified",
            "reason": "Wait action completed and a post-execution observation was captured.",
            "expected_change": "none",
            "confidence": 0.8,
        }

        verified = action_verified_event(
            contract,
            result,
            verification_result,
            post_observation_id="obs_0002",
            task="wait",
        )
        failed = action_verification_failed_event(
            contract,
            result,
            {"status": "unknown", "reason": "Post-execution observation failed: disk low"},
            task="wait",
        )

        self.assertEqual(verified["type"], "action.verified")
        self.assertEqual(verified["action_contract_type"], "wait")
        self.assertEqual(verified["post_observation_id"], "obs_0002")
        self.assertEqual(verified["verification_result"], verification_result)
        self.assertIs(verified["executed"], True)
        self.assertNotIn("screenshot_path", verified)
        self.assertEqual(failed["type"], "action.verification_failed")
        self.assertEqual(failed["reason"], "Post-execution observation failed: disk low")


if __name__ == "__main__":
    unittest.main()
