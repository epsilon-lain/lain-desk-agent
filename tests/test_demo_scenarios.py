from __future__ import annotations

import json
import os
import threading
import unittest
from urllib.request import urlopen
from unittest.mock import patch

import _path  # noqa: F401
from lain_desk_agent.demo_scenarios import run_demo_scenario
from lain_desk_agent.main import create_server


class DemoScenarioTests(unittest.TestCase):
    def test_browser_search_returns_target_hint_with_blocked_click_readiness(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            payload = run_demo_scenario("browser_search", task="Search")

        action = payload["proposal"]["action"]
        self.assertEqual(payload["scenario"], "browser_search")
        self.assertEqual(payload["ui_state"]["app_guess"], "Chrome")
        self.assertEqual(action["type"], "target_hint")
        self.assertEqual(action["target_label"], "search")
        self.assertEqual(payload["action_contract"]["type"], "click")
        self.assertEqual(payload["action_contract"]["status"], "preview_only")
        self.assertIs(payload["action_contract"]["executed"], False)
        self.assertEqual(payload["click_readiness"]["status"], "blocked")
        self.assertIs(payload["click_readiness"]["ready"], False)
        self.assertIn("preview-only contract", payload["click_readiness"]["reasons"])
        self.assertIn("click capability disabled", payload["click_readiness"]["reasons"])
        self.assertIn("preview_only_contract", payload["click_readiness"]["blocker_codes"])
        self.assertIn("action_not_enabled_by_policy", payload["click_readiness"]["blocker_codes"])

    def test_dangerous_send_blocks_readiness_for_high_risk_label(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            payload = run_demo_scenario("dangerous_send", task="Send")

        self.assertEqual(payload["proposal"]["action"]["type"], "target_hint")
        self.assertEqual(payload["action_contract"]["target_label"], "send")
        self.assertEqual(payload["action_contract"]["target_risk_hint"], "high_risk")
        self.assertEqual(payload["click_readiness"]["status"], "blocked")
        self.assertIs(payload["click_readiness"]["ready"], False)
        self.assertEqual(payload["click_readiness"]["risk"], "high")
        self.assertIn("high-risk target label", payload["click_readiness"]["reasons"])
        self.assertIn("high_risk_requires_approval", payload["click_readiness"]["blocker_codes"])

    def test_dangerous_delete_blocks_readiness_for_high_risk_label(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            payload = run_demo_scenario("dangerous_delete", task="Delete")

        self.assertEqual(payload["proposal"]["action"]["type"], "target_hint")
        self.assertEqual(payload["action_contract"]["target_label"], "delete")
        self.assertEqual(payload["action_contract"]["target_risk_hint"], "high_risk")
        self.assertEqual(payload["click_readiness"]["status"], "blocked")
        self.assertIs(payload["click_readiness"]["ready"], False)
        self.assertEqual(payload["click_readiness"]["risk"], "high")
        self.assertIn("high-risk target label", payload["click_readiness"]["reasons"])
        self.assertIn("high_risk_requires_approval", payload["click_readiness"]["blocker_codes"])

    def test_app_mismatch_returns_switch_app_hint(self) -> None:
        payload = run_demo_scenario("app_mismatch")

        action = payload["proposal"]["action"]
        self.assertEqual(action["type"], "switch_app_hint")
        self.assertEqual(action["target"], "WeChat")
        self.assertEqual(action["parameters"]["current_app"], "Chrome")
        self.assertEqual(payload["action_contract"]["type"], "switch_app")
        self.assertEqual(payload["click_readiness"]["status"], "not_applicable")

    def test_ui_tree_save_returns_preview_target_hint(self) -> None:
        payload = run_demo_scenario("ui_tree_save")

        action = payload["proposal"]["action"]
        self.assertEqual(action["type"], "target_hint")
        self.assertEqual(action["target_source"], "ui_tree")
        self.assertEqual(action["target_label"], "save")
        self.assertEqual(payload["action_contract"]["type"], "click")
        self.assertEqual(payload["action_contract"]["status"], "preview_only")
        self.assertIs(payload["action_contract"]["executed"], False)
        self.assertEqual(payload["click_readiness"]["status"], "blocked")

    def test_disabled_ui_tree_save_returns_no_op(self) -> None:
        payload = run_demo_scenario("ui_tree_disabled_save")

        self.assertEqual(payload["proposal"]["action"]["type"], "no_op")
        self.assertIsNone(payload["action_contract"])
        self.assertEqual(payload["click_readiness"]["status"], "not_applicable")
        self.assertEqual(payload["expected"]["action_type"], "no_op")
        self.assertEqual(payload["ui_state"]["visible_elements"][0]["source"], "ui_tree")
        self.assertEqual(payload["ui_state"]["visible_elements"][0]["confidence"], 0.0)

    def test_conservative_no_op_demo_scenarios_do_not_create_contracts(self) -> None:
        for scenario_name in [
            "ui_tree_hidden_save",
            "low_confidence_search",
            "ambiguous_search",
            "invalid_bbox_search",
            "missing_bbox_search",
            "no_visible_target",
        ]:
            with self.subTest(scenario=scenario_name):
                payload = run_demo_scenario(scenario_name)

                self.assertEqual(payload["expected"]["action_type"], "no_op")
                self.assertEqual(payload["proposal"]["action"]["type"], "no_op")
                self.assertIsNone(payload["action_contract"])
                self.assertEqual(payload["click_readiness"]["status"], "not_applicable")

    def test_ui_tree_high_risk_delete_is_preview_only_and_approval_gated(self) -> None:
        payload = run_demo_scenario("ui_tree_high_risk_delete")
        action = payload["proposal"]["action"]

        self.assertEqual(payload["expected"]["action_type"], "target_hint")
        self.assertEqual(action["type"], "target_hint")
        self.assertEqual(action["target_source"], "ui_tree")
        self.assertEqual(action["target_risk_hint"], "high_risk")
        self.assertEqual(action["risk"], "high")
        self.assertIs(action["requires_approval"], True)
        self.assertEqual(payload["safety_decision"]["decision"], "needs_approval")
        self.assertEqual(payload["action_contract"]["type"], "click")
        self.assertEqual(payload["action_contract"]["status"], "preview_only")
        self.assertIs(payload["action_contract"]["executed"], False)
        self.assertEqual(payload["click_readiness"]["status"], "blocked")
        self.assertIn("high-risk target label", payload["click_readiness"]["reasons"])
        self.assertIn("high_risk_requires_approval", payload["click_readiness"]["blocker_codes"])

    def test_readiness_hardening_demo_scenarios_expose_blocker_codes(self) -> None:
        cases = {
            "readiness_stale_search": "stale_observation",
            "readiness_missing_bbox_search": "missing_bbox",
            "readiness_invalid_bbox_search": "invalid_bbox",
            "readiness_bbox_center_mismatch": "bbox_center_mismatch",
            "readiness_missing_center_search": "missing_center",
            "readiness_missing_target": "missing_target",
            "readiness_out_of_viewport_search": "out_of_viewport",
            "readiness_missing_coordinate_space": "coordinate_space_unknown",
            "readiness_low_confidence_target": "low_confidence_target",
            "readiness_hidden_disabled_target": "hidden_or_disabled_target",
            "readiness_ambiguous_target": "ambiguous_target",
        }

        for scenario_name, blocker_code in cases.items():
            with self.subTest(scenario=scenario_name):
                payload = run_demo_scenario(scenario_name)

                self.assertEqual(payload["proposal"]["action"]["type"], "target_hint")
                self.assertEqual(payload["action_contract"]["type"], "click")
                self.assertEqual(payload["click_readiness"]["status"], "blocked")
                self.assertIs(payload["click_readiness"]["ready"], False)
                self.assertIn(blocker_code, payload["click_readiness"]["blocker_codes"])

    def test_mixed_manual_and_ui_tree_sources_selects_matching_ui_tree_target(self) -> None:
        payload = run_demo_scenario("mixed_manual_ui_tree_save")
        action = payload["proposal"]["action"]

        self.assertEqual(payload["expected"]["target_source"], "ui_tree")
        self.assertEqual(action["type"], "target_hint")
        self.assertEqual(action["target_label"], "save")
        self.assertEqual(action["target_source"], "ui_tree")
        self.assertEqual(payload["action_contract"]["target_source"], "ui_tree")
        self.assertEqual(payload["action_contract"]["status"], "preview_only")

    def test_endpoint_does_not_observe_or_understand(self) -> None:
        server = create_server("127.0.0.1", 0)
        host, port = server.server_address
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            with (
                patch("lain_desk_agent.main.observe", side_effect=AssertionError("observe called")),
                patch("lain_desk_agent.main.understand", side_effect=AssertionError("understand called")),
            ):
                with urlopen(
                    f"http://{host}:{port}/demo/scenario?name=browser_search&task=Search",
                    timeout=5,
                ) as response:
                    payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            thread.join(timeout=2)
            server.server_close()

        self.assertEqual(payload["scenario"], "browser_search")
        self.assertEqual(payload["proposal"]["action"]["type"], "target_hint")
        self.assertEqual(payload["click_readiness"]["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
