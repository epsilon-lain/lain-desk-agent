from __future__ import annotations

import unittest

import _path  # noqa: F401
from lain_desk_agent.actuation import ActuationBlockedError, execute_action_contract
from lain_desk_agent.main import (
    action_blocked_event,
    action_contract_from_execute_payload,
    action_executed_event,
    action_execution_requested_event,
)


class WaitOnlyActuationTests(unittest.TestCase):
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

        self.assertEqual(context.exception.reason, "Only wait action contracts can be executed.")

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

        self.assertEqual(context.exception.reason, "Only wait action contracts can be executed.")

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


if __name__ == "__main__":
    unittest.main()
