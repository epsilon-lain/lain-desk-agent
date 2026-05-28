from __future__ import annotations

import unittest

from lain_desk_agent.planner import propose
from lain_desk_agent.safety import assess_proposal


class PlannerSafetyTests(unittest.TestCase):
    def test_task_match_returns_target_hint(self) -> None:
        proposal = propose(
            {
                "ui_state_id": "state_0042",
                "state_guess": "browser_window",
                "task": "Search for docs",
                "visible_elements": [
                    {
                        "id": "element_0007",
                        "type": "text",
                        "label": "Search",
                        "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
                        "confidence": 0.91,
                    }
                ],
            }
        )

        action = proposal["action"]
        self.assertEqual(action["type"], "target_hint")
        self.assertEqual(action["target_element_id"], "element_0007")
        self.assertNotIn(action["type"], {"click", "type", "hotkey", "submit"})

    def test_low_confidence_element_returns_no_op(self) -> None:
        proposal = propose(
            {
                "ui_state_id": "state_0001",
                "task": "Search",
                "visible_elements": [
                    {
                        "id": "element_0001",
                        "type": "text",
                        "label": "Search",
                        "confidence": 0.2,
                    }
                ],
            }
        )

        self.assertEqual(proposal["action"]["type"], "no_op")

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


if __name__ == "__main__":
    unittest.main()
