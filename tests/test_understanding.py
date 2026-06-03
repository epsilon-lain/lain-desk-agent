from __future__ import annotations

import unittest

import _path  # noqa: F401
from lain_desk_agent.understanding import _visible_elements_from_text_boxes, understand


class UnderstandingVisibleElementTests(unittest.TestCase):
    def test_ocr_text_boxes_become_read_only_visible_elements(self) -> None:
        elements = _visible_elements_from_text_boxes(
            [
                {
                    "id": "ocr_0001",
                    "source": "ocr",
                    "text": "Search",
                    "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
                    "confidence": 0.92,
                }
            ],
            screen={"width": 200, "height": 120},
            timestamp="2026-01-01T00:00:00Z",
        )

        self.assertEqual(
            elements,
            [
                {
                    "id": "element_0001",
                    "label": "search",
                    "text": "search",
                    "role": "text",
                    "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
                    "center": {"x": 50, "y": 32},
                    "confidence": 0.92,
                    "source": "ocr",
                    "risk_hint": "normal",
                    "timestamp": "2026-01-01T00:00:00Z",
                }
            ],
        )

    def test_ocr_high_risk_label_gets_risk_hint(self) -> None:
        elements = _visible_elements_from_text_boxes(
            [
                {
                    "id": "ocr_0002",
                    "text": "Delete",
                    "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
                    "confidence": 0.9,
                }
            ],
            screen={"width": 200, "height": 120},
            timestamp="2026-01-01T00:00:00Z",
        )

        self.assertEqual(elements[0]["risk_hint"], "high_risk")

    def test_understanding_merges_ui_tree_elements_into_visible_elements(self) -> None:
        ui_state = understand(
            {
                "observation_id": "obs_0042",
                "timestamp": "2026-01-01T00:00:00Z",
                "screen": {"width": 400, "height": 400},
                "active_window": {"title": "Example", "app_name": "example.exe"},
                "ui_tree_elements": [
                    {
                        "automation_id": "save_button",
                        "name": "Save",
                        "text": "Save",
                        "control_type": "Button",
                        "bounding_rectangle": {"x": 100, "y": 200, "width": 80, "height": 32},
                        "is_enabled": True,
                        "is_visible": True,
                        "confidence": 0.95,
                    }
                ],
            }
        )

        self.assertEqual(ui_state["screen"], {"width": 400, "height": 400})
        self.assertEqual(ui_state["visible_elements"][0]["id"], "ui_tree_save_button")
        self.assertEqual(ui_state["visible_elements"][0]["label"], "save")
        self.assertEqual(ui_state["visible_elements"][0]["role"], "button")
        self.assertEqual(ui_state["visible_elements"][0]["source"], "ui_tree")
        self.assertEqual(ui_state["visible_elements"][0]["center"], {"x": 140, "y": 216})


if __name__ == "__main__":
    unittest.main()
