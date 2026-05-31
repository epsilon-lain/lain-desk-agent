from __future__ import annotations

import json
import threading
import unittest
from unittest.mock import patch
from urllib.request import urlopen

import _path  # noqa: F401
from lain_desk_agent.main import create_server
from lain_desk_agent.planner_evaluation import evaluate_demo_scenario, evaluate_demo_scenarios


class PlannerEvaluationHarnessTests(unittest.TestCase):
    def test_demo_report_includes_rule_based_and_ai_outputs(self) -> None:
        report = evaluate_demo_scenarios()
        encoded = json.dumps(report)

        self.assertEqual(report["report_type"], "planner_evaluation")
        self.assertEqual(report["source"], "demo_scenarios")
        self.assertIs(report["external_llm_calls"], False)
        self.assertEqual(report["scenario_count"], 4)
        self.assertEqual(report["summary"]["unsafe_ai_outputs"], 0)
        self.assertEqual(report["summary"]["ai_rejections"], 0)
        self.assertIs(report["summary"]["all_safe_read_only"], True)
        self.assertNotIn("screenshot_path", encoded)
        self.assertNotIn("image_bytes", encoded)

        scenarios = {scenario["scenario"]: scenario for scenario in report["scenarios"]}
        self.assertEqual(set(scenarios), {"browser_search", "dangerous_send", "dangerous_delete", "app_mismatch"})
        self.assertEqual(scenarios["browser_search"]["rule_based"]["proposal_type"], "target_hint")
        self.assertEqual(scenarios["browser_search"]["ai_proposal"]["proposal_type"], "target_hint")
        self.assertEqual(scenarios["app_mismatch"]["rule_based"]["proposal_type"], "switch_app_hint")
        self.assertEqual(scenarios["app_mismatch"]["ai_proposal"]["proposal_type"], "switch_app_hint")

    def test_report_captures_visible_elements_and_risk_hints(self) -> None:
        scenario = evaluate_demo_scenario("dangerous_delete")
        visible_elements = scenario["inputs"]["visible_elements"]
        grounding_hints = scenario["inputs"]["grounding_hints"]

        self.assertEqual(visible_elements["count"], 1)
        self.assertEqual(visible_elements["items"][0]["label"], "Delete")
        self.assertEqual(visible_elements["items"][0]["source"], "demo")
        self.assertEqual(visible_elements["items"][0]["risk_hint"], "high")
        self.assertEqual(grounding_hints[0]["risk_hint"], "high")
        self.assertIn("visible_elements include high-risk grounding hints", scenario["notes"])
        self.assertIn("high-risk target label", scenario["rule_based"]["click_readiness"]["reasons"])
        self.assertIn("high-risk target label", scenario["ai_proposal"]["click_readiness"]["reasons"])

    def test_all_outputs_pass_existing_safety_surfaces_without_execution(self) -> None:
        report = evaluate_demo_scenarios()

        for scenario in report["scenarios"]:
            for planner_name in ["rule_based", "ai_proposal"]:
                with self.subTest(scenario=scenario["scenario"], planner=planner_name):
                    result = scenario[planner_name]
                    self.assertIs(result["safe_read_only"], True)
                    self.assertIn(result["safety_decision"]["decision"], {"allowed", "needs_approval"})
                    self.assertEqual(result["execution_policy"]["executable_actions"], ["wait"])

                    action_contract = result["action_contract"]
                    if action_contract is not None:
                        self.assertEqual(action_contract["status"], "preview_only")
                        self.assertIs(action_contract["executed"], False)
                        self.assertIn(action_contract["type"], {"click", "switch_app"})

                    self.assertNotEqual(result["proposal_type"], "click")
                    self.assertNotEqual(result["proposal_type"], "type")
                    self.assertNotEqual(result["proposal_type"], "hotkey")
                    self.assertNotEqual(result["proposal_type"], "scroll")
                    self.assertNotEqual(result["proposal_type"], "switch_app")

    def test_harness_is_repeatable(self) -> None:
        first = evaluate_demo_scenarios()
        second = evaluate_demo_scenarios()

        self.assertEqual(first, second)

    def test_demo_endpoint_returns_report_without_observing(self) -> None:
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
                    f"http://{host}:{port}/planner-evaluation/demo",
                    timeout=5,
                ) as response:
                    payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            thread.join(timeout=2)
            server.server_close()

        self.assertEqual(payload["scenario_count"], 4)
        self.assertIs(payload["summary"]["all_safe_read_only"], True)
        self.assertEqual(payload["scenarios"][0]["rule_based"]["proposal_type"], "target_hint")
        self.assertEqual(payload["scenarios"][0]["ai_proposal"]["proposal_type"], "target_hint")


if __name__ == "__main__":
    unittest.main()
