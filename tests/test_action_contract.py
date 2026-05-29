from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import _path  # noqa: F401
from lain_desk_agent.action_contract import action_contract_from_proposal
from lain_desk_agent.main import (
    action_contract_event_from_contract,
    append_action_contract_event,
)


class ActionContractTests(unittest.TestCase):
    def test_target_hint_becomes_preview_click_contract(self) -> None:
        contract = action_contract_from_proposal(
            {
                "proposal_id": "proposal_0007",
                "action": {
                    "type": "target_hint",
                    "target_element_id": "element_0007",
                    "target_label": "Search",
                    "target_bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
                },
            }
        )

        self.assertIsNotNone(contract)
        event = action_contract_event_from_contract(contract, task="Search")
        self.assertEqual(contract["action_id"], "action_0001")
        self.assertEqual(contract["source_proposal_id"], "proposal_0007")
        self.assertEqual(contract["type"], "click")
        self.assertEqual(contract["target_element_id"], "element_0007")
        self.assertEqual(contract["target_label"], "Search")
        self.assertEqual(contract["bbox"], {"x": 10, "y": 20, "width": 80, "height": 24})
        self.assertEqual(contract["center"], {"x": 50, "y": 32})
        self.assertEqual(contract["status"], "preview_only")
        self.assertIs(contract["executed"], False)
        self.assertEqual(event["type"], "action_contract.created")
        self.assertEqual(event["action_id"], "action_0001")
        self.assertEqual(event["source_proposal_id"], "proposal_0007")
        self.assertEqual(event["action_contract_type"], "click")
        self.assertEqual(event["status"], "preview_only")
        self.assertIs(event["executed"], False)
        self.assertEqual(event["task"], "Search")

    def test_switch_app_hint_becomes_preview_switch_app_contract(self) -> None:
        contract = action_contract_from_proposal(
            {
                "proposal_id": "proposal_0008",
                "action": {
                    "type": "switch_app_hint",
                    "target": "WeChat",
                    "parameters": {"current_app": "Chrome"},
                },
            }
        )

        self.assertIsNotNone(contract)
        event = action_contract_event_from_contract(contract, task="use wechat")
        self.assertEqual(contract["action_id"], "action_0001")
        self.assertEqual(contract["source_proposal_id"], "proposal_0008")
        self.assertEqual(contract["type"], "switch_app")
        self.assertEqual(contract["target_app"], "WeChat")
        self.assertEqual(contract["parameters"], {"current_app": "Chrome"})
        self.assertEqual(contract["status"], "preview_only")
        self.assertIs(contract["executed"], False)
        self.assertEqual(event["type"], "action_contract.created")
        self.assertEqual(event["action_contract_type"], "switch_app")
        self.assertEqual(event["task"], "use wechat")

        with tempfile.TemporaryDirectory() as temp_dir:
            append_action_contract_event(event, run_dir=temp_dir)
            events_path = Path(temp_dir) / "events.jsonl"
            written = json.loads(events_path.read_text(encoding="utf-8").strip())

        self.assertEqual(written["type"], "action_contract.created")
        self.assertEqual(written["source_proposal_id"], "proposal_0008")
        self.assertEqual(written["action_contract_type"], "switch_app")

    def test_no_op_returns_none(self) -> None:
        contract = action_contract_from_proposal(
            {
                "proposal_id": "proposal_0009",
                "action": {"type": "no_op"},
            }
        )

        self.assertIsNone(contract)

    def test_action_contract_event_can_be_appended_to_jsonl(self) -> None:
        contract = action_contract_from_proposal(
            {
                "proposal_id": "proposal_0011",
                "action": {
                    "type": "target_hint",
                    "target_element_id": "element_0011",
                    "target_label": "Search",
                    "target_bbox": {"x": 1, "y": 2, "width": 3, "height": 4},
                },
            }
        )

        self.assertIsNotNone(contract)
        event = action_contract_event_from_contract(contract, task="Search")

        with tempfile.TemporaryDirectory() as temp_dir:
            append_action_contract_event(event, run_dir=temp_dir)
            events_path = Path(temp_dir) / "events.jsonl"
            written = json.loads(events_path.read_text(encoding="utf-8").strip())

        self.assertEqual(written["type"], "action_contract.created")
        self.assertEqual(written["action_id"], "action_0001")
        self.assertEqual(written["source_proposal_id"], "proposal_0011")
        self.assertEqual(written["action_contract_type"], "click")
        self.assertNotIn("bbox", written)
        self.assertNotIn("center", written)

    def test_target_hint_without_bbox_returns_none(self) -> None:
        contract = action_contract_from_proposal(
            {
                "proposal_id": "proposal_0010",
                "action": {
                    "type": "target_hint",
                    "target_element_id": "element_0010",
                    "target_label": "Search",
                },
            }
        )

        self.assertIsNone(contract)


if __name__ == "__main__":
    unittest.main()
