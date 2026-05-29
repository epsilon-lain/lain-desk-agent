from __future__ import annotations

import unittest

import _path  # noqa: F401
from lain_desk_agent.action_contract import action_contract_from_proposal


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
        self.assertEqual(contract["action_id"], "action_0001")
        self.assertEqual(contract["source_proposal_id"], "proposal_0007")
        self.assertEqual(contract["type"], "click")
        self.assertEqual(contract["target_element_id"], "element_0007")
        self.assertEqual(contract["target_label"], "Search")
        self.assertEqual(contract["bbox"], {"x": 10, "y": 20, "width": 80, "height": 24})
        self.assertEqual(contract["center"], {"x": 50, "y": 32})
        self.assertEqual(contract["status"], "preview_only")
        self.assertIs(contract["executed"], False)

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
        self.assertEqual(contract["action_id"], "action_0001")
        self.assertEqual(contract["source_proposal_id"], "proposal_0008")
        self.assertEqual(contract["type"], "switch_app")
        self.assertEqual(contract["target_app"], "WeChat")
        self.assertEqual(contract["parameters"], {"current_app": "Chrome"})
        self.assertEqual(contract["status"], "preview_only")
        self.assertIs(contract["executed"], False)

    def test_no_op_returns_none(self) -> None:
        contract = action_contract_from_proposal(
            {
                "proposal_id": "proposal_0009",
                "action": {"type": "no_op"},
            }
        )

        self.assertIsNone(contract)

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
