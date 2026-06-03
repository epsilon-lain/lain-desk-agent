from __future__ import annotations

import unittest

import _path  # noqa: F401
from lain_desk_agent.action_contract import action_contract_from_proposal
from lain_desk_agent.planner import propose
from lain_desk_agent.safety import assess_proposal


class PlannerSafetyTests(unittest.TestCase):
    def test_task_match_returns_target_hint(self) -> None:
        proposal = propose(
            {
                "ui_state_id": "state_0042",
                "app_guess": "Chrome",
                "state_guess": "browser_window",
                "task": "Search for docs",
                "visible_elements": [
                    {
                        "id": "element_0007",
                        "role": "text",
                        "label": "Search",
                        "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
                        "confidence": 0.91,
                        "source": "manual",
                    }
                ],
            }
        )

        action = proposal["action"]
        self.assertEqual(action["type"], "target_hint")
        self.assertEqual(action["target_element_id"], "element_0007")
        self.assertEqual(action["target_label"], "search")
        self.assertEqual(action["target_center"], {"x": 50, "y": 32})
        self.assertEqual(action["target_role"], "text")
        self.assertEqual(action["target_risk_hint"], "normal")
        self.assertNotIn(action["type"], {"click", "type", "hotkey", "submit"})

    def test_low_confidence_element_returns_no_op(self) -> None:
        proposal = propose(
            {
                "ui_state_id": "state_0001",
                "task": "Search",
                "visible_elements": [
                    {
                        "id": "element_0001",
                        "role": "text",
                        "label": "Search",
                        "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
                        "confidence": 0.2,
                        "source": "manual",
                    }
                ],
            }
        )

        self.assertEqual(proposal["action"]["type"], "no_op")

    def test_app_mismatch_returns_switch_app_hint(self) -> None:
        proposal = propose(
            {
                "ui_state_id": "state_0003",
                "app_guess": "Chrome",
                "state_guess": "browser_window",
                "task": "use wechat say hello",
                "visible_elements": [
                    {
                        "id": "element_0001",
                        "role": "text",
                        "label": "Search",
                        "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
                        "confidence": 0.9,
                        "source": "manual",
                    }
                ],
            }
        )

        action = proposal["action"]
        self.assertEqual(action["type"], "switch_app_hint")
        self.assertEqual(action["target"], "WeChat")
        self.assertEqual(action["parameters"]["current_app"], "Chrome")
        self.assertNotIn(action["type"], {"click", "type", "hotkey", "submit"})

    def test_app_match_keeps_target_hint_behavior(self) -> None:
        proposal = propose(
            {
                "ui_state_id": "state_0004",
                "app_guess": "WeChat",
                "task": "use wechat Search",
                "visible_elements": [
                    {
                        "id": "element_0001",
                        "role": "text",
                        "label": "Search",
                        "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
                        "confidence": 0.9,
                        "source": "manual",
                    }
                ],
            }
        )

        self.assertEqual(proposal["action"]["type"], "target_hint")

    def test_ambiguous_matching_elements_return_no_op(self) -> None:
        proposal = propose(
            {
                "ui_state_id": "state_0005",
                "app_guess": "Chrome",
                "task": "Search",
                "visible_elements": [
                    {
                        "id": "element_search_a",
                        "role": "button",
                        "label": "Search",
                        "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
                        "confidence": 0.91,
                        "source": "manual",
                    },
                    {
                        "id": "element_search_b",
                        "role": "button",
                        "label": "Search",
                        "bbox": {"x": 120, "y": 20, "width": 80, "height": 24},
                        "confidence": 0.9,
                        "source": "manual",
                    },
                ],
            }
        )

        self.assertEqual(proposal["action"]["type"], "no_op")

    def test_high_risk_target_hint_is_approval_gated(self) -> None:
        proposal = propose(
            {
                "ui_state_id": "state_0006",
                "app_guess": "File Explorer",
                "task": "Delete",
                "visible_elements": [
                    {
                        "id": "element_delete",
                        "role": "button",
                        "label": "Delete",
                        "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
                        "confidence": 0.91,
                        "source": "manual",
                    }
                ],
            }
        )

        action = proposal["action"]
        self.assertEqual(action["type"], "target_hint")
        self.assertEqual(action["target_risk_hint"], "high_risk")
        self.assertEqual(action["risk"], "high")
        self.assertIs(action["requires_approval"], True)

    def test_disabled_ui_tree_element_returns_no_op(self) -> None:
        proposal = propose(
            {
                "ui_state_id": "state_ui_tree_disabled",
                "app_guess": "Notepad",
                "task": "Save",
                "visible_elements": [
                    _ui_tree_element(
                        "ui_tree_save_disabled",
                        "save",
                        x=10,
                        confidence=0.0,
                        risk_hint="unknown",
                    )
                ],
            }
        )

        self.assertEqual(proposal["action"]["type"], "no_op")

    def test_low_confidence_ui_tree_element_returns_no_op(self) -> None:
        proposal = propose(
            {
                "ui_state_id": "state_ui_tree_low_confidence",
                "app_guess": "Notepad",
                "task": "Save",
                "visible_elements": [
                    _ui_tree_element(
                        "ui_tree_save_low",
                        "save",
                        x=10,
                        confidence=0.2,
                    )
                ],
            }
        )

        self.assertEqual(proposal["action"]["type"], "no_op")

    def test_ambiguous_ui_tree_targets_return_no_op(self) -> None:
        proposal = propose(
            {
                "ui_state_id": "state_ui_tree_ambiguous",
                "app_guess": "Notepad",
                "task": "Save",
                "visible_elements": [
                    _ui_tree_element("ui_tree_save_a", "save", x=10, confidence=0.91),
                    _ui_tree_element("ui_tree_save_b", "save", x=120, confidence=0.9),
                ],
            }
        )

        self.assertEqual(proposal["action"]["type"], "no_op")

    def test_high_risk_ui_tree_target_remains_preview_only(self) -> None:
        proposal = propose(
            {
                "ui_state_id": "state_ui_tree_delete",
                "app_guess": "File Explorer",
                "task": "Delete",
                "visible_elements": [
                    _ui_tree_element(
                        "ui_tree_delete",
                        "delete",
                        x=10,
                        confidence=0.91,
                        risk_hint="high_risk",
                    )
                ],
            }
        )
        contract = action_contract_from_proposal(proposal)

        action = proposal["action"]
        self.assertEqual(action["type"], "target_hint")
        self.assertEqual(action["target_source"], "ui_tree")
        self.assertEqual(action["target_risk_hint"], "high_risk")
        self.assertEqual(action["risk"], "high")
        self.assertIs(action["requires_approval"], True)
        self.assertEqual(contract["type"], "click")
        self.assertEqual(contract["status"], "preview_only")
        self.assertIs(contract["executed"], False)

    def test_safety_allows_read_only_target_hint(self) -> None:
        decision = assess_proposal(
            {
                "action": {
                    "type": "target_hint",
                    "risk": "low",
                    "requires_approval": False,
                }
            }
        )

        self.assertEqual(decision["decision"], "allowed")

    def test_safety_allows_read_only_switch_app_hint(self) -> None:
        decision = assess_proposal(
            {
                "action": {
                    "type": "switch_app_hint",
                    "risk": "low",
                    "requires_approval": False,
                }
            }
        )

        self.assertEqual(decision["decision"], "allowed")

    def test_safety_blocks_executable_click(self) -> None:
        decision = assess_proposal(
            {
                "action": {
                    "type": "click",
                    "risk": "low",
                    "requires_approval": False,
                }
            }
        )

        self.assertEqual(decision["decision"], "blocked")


def _ui_tree_element(
    element_id: str,
    label: str,
    x: int,
    confidence: float,
    risk_hint: str = "normal",
) -> dict[str, object]:
    return {
        "id": element_id,
        "label": label,
        "text": label,
        "role": "button",
        "bbox": {"x": x, "y": 20, "width": 80, "height": 24},
        "center": {"x": x + 40, "y": 32},
        "confidence": confidence,
        "source": "ui_tree",
        "risk_hint": risk_hint,
        "timestamp": "2026-01-01T00:00:00Z",
    }


if __name__ == "__main__":
    unittest.main()
