from __future__ import annotations

import unittest

import _path  # noqa: F401
from lain_desk_agent.observer import (
    is_valid_visible_element,
    normalize_label_text,
    normalize_visible_element,
    normalize_visible_elements,
    visible_element_schema_errors,
)


class VisibleElementSchemaTests(unittest.TestCase):
    def test_normalizes_complete_visible_element_schema(self) -> None:
        element = normalize_visible_element(
            {
                "id": "Search Button!",
                "label": "  Search... ",
                "text": " Search ",
                "type": "Button",
                "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
                "confidence": 92,
                "source": "ocr",
            },
            screen={"width": 200, "height": 120},
            timestamp="2026-01-01T00:00:00Z",
        )

        self.assertEqual(
            element,
            {
                "id": "Search_Button",
                "label": "search",
                "text": "search",
                "role": "button",
                "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
                "center": {"x": 50, "y": 32},
                "confidence": 0.92,
                "source": "ocr",
                "risk_hint": "normal",
                "timestamp": "2026-01-01T00:00:00Z",
            },
        )
        self.assertTrue(is_valid_visible_element(element, screen={"width": 200, "height": 120}))

    def test_validation_reports_missing_fields(self) -> None:
        errors = visible_element_schema_errors({"id": "element_1"})

        self.assertIn("missing field: bbox", errors)
        self.assertIn("missing field: timestamp", errors)

    def test_out_of_bounds_bbox_is_rejected(self) -> None:
        element = normalize_visible_element(
            {
                "id": "element_outside",
                "label": "Search",
                "role": "button",
                "bbox": {"x": 90, "y": 20, "width": 80, "height": 24},
                "confidence": 0.9,
                "source": "manual",
            },
            screen={"width": 100, "height": 100},
            timestamp="2026-01-01T00:00:00Z",
        )

        self.assertIsNone(element)

    def test_center_must_match_bbox_for_schema_validation(self) -> None:
        errors = visible_element_schema_errors(
            {
                "id": "element_bad_center",
                "label": "search",
                "text": "search",
                "role": "button",
                "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
                "center": {"x": 99, "y": 99},
                "confidence": 0.8,
                "source": "manual",
                "risk_hint": "normal",
                "timestamp": "2026-01-01T00:00:00Z",
            },
            screen={"width": 200, "height": 120},
        )

        self.assertIn("center must match bbox center", errors)

    def test_duplicate_ids_are_made_unique(self) -> None:
        elements = normalize_visible_elements(
            [
                _element("shared", "Search", 10),
                _element("shared", "Find", 50),
            ],
            screen={"width": 200, "height": 120},
            timestamp="2026-01-01T00:00:00Z",
        )

        self.assertEqual([element["id"] for element in elements], ["shared", "shared_2"])

    def test_low_confidence_remains_valid_schema(self) -> None:
        element = normalize_visible_element(
            _element("element_low", "Search", 10, confidence=0.2),
            screen={"width": 200, "height": 120},
            timestamp="2026-01-01T00:00:00Z",
        )

        self.assertIsNotNone(element)
        self.assertEqual(element["confidence"], 0.2)
        self.assertTrue(is_valid_visible_element(element))

    def test_ambiguous_label_normalization_removes_special_characters(self) -> None:
        self.assertEqual(normalize_label_text("  Sear-ch!!!  "), "sear ch")

    def test_high_risk_label_is_inferred(self) -> None:
        element = normalize_visible_element(
            _element("element_delete", "Delete Account", 10),
            screen={"width": 200, "height": 120},
            timestamp="2026-01-01T00:00:00Z",
        )

        self.assertEqual(element["risk_hint"], "high_risk")


def _element(
    element_id: str,
    label: str,
    x: int,
    confidence: float = 0.9,
) -> dict[str, object]:
    return {
        "id": element_id,
        "label": label,
        "role": "button",
        "bbox": {"x": x, "y": 20, "width": 30, "height": 20},
        "confidence": confidence,
        "source": "manual",
    }


if __name__ == "__main__":
    unittest.main()
