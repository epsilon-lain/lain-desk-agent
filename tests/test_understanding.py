from __future__ import annotations

import unittest

import _path  # noqa: F401
from lain_desk_agent.understanding import _visible_elements_from_text_boxes


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
            ]
        )

        self.assertEqual(
            elements,
            [
                {
                    "id": "element_0001",
                    "source": "ocr",
                    "type": "text",
                    "kind": "text",
                    "label": "Search",
                    "text": "Search",
                    "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
                    "confidence": 0.92,
                    "source_ref": "ocr_0001",
                    "risk_hint": "none",
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
            ]
        )

        self.assertEqual(elements[0]["risk_hint"], "high")


if __name__ == "__main__":
    unittest.main()
