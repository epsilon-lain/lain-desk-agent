from __future__ import annotations

import json
import threading
import unittest
from unittest.mock import patch
from urllib.request import urlopen

import _path  # noqa: F401
from lain_desk_agent.main import create_server
from lain_desk_agent.planner_context import build_planner_context


class PlannerContextBundleTests(unittest.TestCase):
    def test_context_compacts_large_ui_state_without_screenshot_path(self) -> None:
        ui_state = _large_ui_state()
        context = build_planner_context(
            "Search",
            ui_state,
            runtime_status=_runtime_status(),
            recent_events=_events(8),
        )
        encoded = json.dumps(context)

        self.assertEqual(context["task"], "Search")
        self.assertEqual(context["app_guess"], "Chrome")
        self.assertEqual(context["screen"], {"width": 1920, "height": 1080})
        self.assertEqual(context["visible_elements"]["count"], 25)
        self.assertEqual(len(context["visible_elements"]["items"]), 20)
        self.assertTrue(context["visible_elements"]["truncated"])
        self.assertEqual(context["visible_text"]["count"], 12)
        self.assertEqual(len(context["visible_text"]["preview"]), 8)
        self.assertTrue(context["visible_text"]["truncated"])
        self.assertEqual(context["recent_events"]["count"], 5)
        self.assertTrue(context["recent_events"]["truncated"])
        self.assertNotIn("screenshot_path", encoded)
        self.assertNotIn("runs/run_001/obs_0001.png", encoded)

    def test_visible_elements_have_compact_normalized_shape(self) -> None:
        context = build_planner_context(
            "Search",
            _large_ui_state(),
            runtime_status=_runtime_status(),
            recent_events=[],
        )
        item = context["visible_elements"]["items"][0]

        self.assertEqual(
            set(item),
            {
                "id",
                "label",
                "text",
                "role",
                "bbox",
                "center",
                "confidence",
                "source",
                "risk_hint",
                "timestamp",
            },
        )
        self.assertEqual(item["id"], "element_0000")
        self.assertEqual(item["label"], "label 0")
        self.assertEqual(item["text"], "label 0")
        self.assertEqual(item["role"], "text")
        self.assertEqual(item["center"], {"x": 10, "y": 6})
        self.assertEqual(item["source"], "manual")
        self.assertEqual(item["risk_hint"], "normal")
        self.assertEqual(item["timestamp"], "2026-01-01T00:00:00Z")
        self.assertEqual(context["visible_elements"]["summary"]["item_count"], 20)
        self.assertEqual(context["visible_elements"]["summary"]["sources"], {"manual": 20})

    def test_visible_elements_missing_fields_are_filtered_safely(self) -> None:
        ui_state = _large_ui_state()
        ui_state["visible_elements"] = [
            {
                "text": "OK",
                "bbox": {"x": "bad", "y": 2, "width": 10, "height": 10},
            }
        ]

        context = build_planner_context(
            "OK",
            ui_state,
            runtime_status=_runtime_status(),
            recent_events=[],
        )

        self.assertEqual(context["visible_elements"]["count"], 0)
        self.assertEqual(context["visible_elements"]["items"], [])
        self.assertEqual(context["visible_elements"]["summary"]["item_count"], 0)

    def test_visible_elements_mark_high_risk_label_hint(self) -> None:
        ui_state = _large_ui_state()
        ui_state["visible_elements"] = [
            {
                "id": "danger_delete",
                "source": "manual",
                "role": "button",
                "label": "Delete account",
                "bbox": {"x": 10, "y": 20, "width": 120, "height": 32},
                "confidence": 0.97,
            }
        ]

        context = build_planner_context(
            "Delete",
            ui_state,
            runtime_status=_runtime_status(),
            recent_events=[],
        )
        item = context["visible_elements"]["items"][0]

        self.assertEqual(item["source"], "manual")
        self.assertEqual(item["role"], "button")
        self.assertEqual(item["risk_hint"], "high_risk")
        self.assertEqual(context["visible_elements"]["summary"]["risk_hints"], {"high_risk": 1})

    def test_visible_elements_preserve_ui_tree_source(self) -> None:
        ui_state = _large_ui_state()
        ui_state["visible_elements"] = [
            {
                "id": "ui_tree_save",
                "source": "ui_tree",
                "role": "button",
                "label": "Save",
                "bbox": {"x": 10, "y": 20, "width": 120, "height": 32},
                "confidence": 0.97,
            }
        ]

        context = build_planner_context(
            "Save",
            ui_state,
            runtime_status=_runtime_status(),
            recent_events=[],
        )
        item = context["visible_elements"]["items"][0]

        self.assertEqual(item["source"], "ui_tree")
        self.assertEqual(item["role"], "button")
        self.assertEqual(item["label"], "save")
        self.assertEqual(context["visible_elements"]["summary"]["sources"], {"ui_tree": 1})

    def test_context_summarizes_safety_runtime(self) -> None:
        runtime_status = _runtime_status()
        runtime_status["runtime"]["desktop_control"] = True
        context = build_planner_context(
            "Search",
            _large_ui_state(),
            runtime_status=runtime_status,
            recent_events=[],
        )

        safety_runtime = context["safety_runtime"]
        self.assertIs(safety_runtime["desktop_control"], False)
        self.assertEqual(safety_runtime["permission_profile"], "wait_only")
        self.assertEqual(safety_runtime["executable_actions"], ["wait"])
        self.assertIn("click", safety_runtime["blocked_actions"])
        self.assertEqual(safety_runtime["blocked_actions_count"], 5)
        self.assertEqual(safety_runtime["click_readiness"]["status"], "blocked")

    def test_planner_context_endpoint_uses_observation_path_and_returns_compact_bundle(self) -> None:
        server = create_server("127.0.0.1", 0)
        host, port = server.server_address
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            with (
                patch("lain_desk_agent.main.observe", return_value=_observation()),
                patch("lain_desk_agent.main.understand", return_value=_large_ui_state()),
                patch("lain_desk_agent.main.read_recent_events", return_value=_events(2)),
            ):
                with urlopen(
                    f"http://{host}:{port}/planner-context?task=Search",
                    timeout=5,
                ) as response:
                    payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            thread.join(timeout=2)
            server.server_close()

        context = payload["planner_context"]
        encoded = json.dumps(payload)
        self.assertEqual(context["task"], "Search")
        self.assertEqual(context["screen"], {"width": 1920, "height": 1080})
        self.assertEqual(context["visible_elements"]["count"], 25)
        self.assertEqual(len(context["visible_elements"]["items"]), 20)
        self.assertEqual(context["recent_events"]["count"], 2)
        self.assertNotIn("screenshot_path", encoded)
        self.assertNotIn("image_bytes", encoded)


def _large_ui_state() -> dict[str, object]:
    return {
        "ui_state_id": "state_0001",
        "source_observation_id": "obs_0001",
        "app_guess": "Chrome",
        "state_guess": "browser_window",
        "observation_timestamp": "2026-01-01T00:00:00Z",
        "summary": "A browser window with many OCR elements.",
        "confidence": 0.91,
        "screen": {
            "width": 1920,
            "height": 1080,
            "screenshot_path": "runs/run_001/obs_0001.png",
        },
        "visible_elements": [
            {
                "id": f"element_{index:04d}",
                "role": "text",
                "label": f"Label {index}",
                "bbox": {"x": index, "y": index + 1, "width": 20, "height": 10},
                "confidence": 0.8,
                "source": "manual",
                "raw_ocr": "not included",
            }
            for index in range(25)
        ],
        "visible_text": [
            f"Visible OCR line {index} " + ("x" * 160)
            for index in range(12)
        ],
        "visible_text_boxes": [{"text": "should not be included"}],
    }


def _runtime_status() -> dict[str, object]:
    return {
        "runtime": {
            "desktop_control": False,
        },
        "permission_profile": "wait_only",
        "execution_policy": {
            "current_profile": "wait_only",
            "desktop_control": False,
            "executable_actions": ["wait"],
            "blocked_actions_count": 5,
        },
        "click_readiness": {
            "enabled": False,
            "reason": "Real click execution is not enabled.",
        },
    }


def _events(count: int) -> list[dict[str, object]]:
    return [
        {
            "type": "observation.created",
            "timestamp": f"2026-01-01T00:00:0{index}Z",
            "observation_id": f"obs_{index:04d}",
            "screenshot_path": f"runs/run_001/obs_{index:04d}.png",
            "proposal": {"large": "payload"},
        }
        for index in range(count)
    ]


def _observation() -> dict[str, object]:
    return {
        "observation_id": "obs_0001",
        "screen": {
            "width": 1920,
            "height": 1080,
            "screenshot_path": "runs/run_001/obs_0001.png",
            "image_bytes": "not real bytes",
        },
        "active_window": {"title": "Chrome", "app_name": "chrome.exe"},
    }


if __name__ == "__main__":
    unittest.main()
