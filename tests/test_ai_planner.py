from __future__ import annotations

import json
import unittest

import _path  # noqa: F401
from lain_desk_agent.action_contract import action_contract_from_proposal
from lain_desk_agent.ai_planner import (
    ALLOWED_PROPOSAL_ACTION_TYPES,
    build_ai_planner_prompt_or_payload,
    build_ai_proposal_from_context,
    validate_ai_proposal,
)
from lain_desk_agent.main import click_readiness_for_response
from lain_desk_agent.planner_context import build_planner_context
from lain_desk_agent.safety import assess_proposal


class AIPlannerHarnessTests(unittest.TestCase):
    def test_prompt_payload_is_compact_and_explicitly_proposal_only(self) -> None:
        context = _planner_context()
        payload = build_ai_planner_prompt_or_payload(context)
        encoded = json.dumps(payload)

        self.assertEqual(payload["planner"]["mode"], "test_harness_only")
        self.assertIs(payload["planner"]["external_llm_calls"], False)
        self.assertEqual(payload["allowed_proposal_action_types"], ALLOWED_PROPOSAL_ACTION_TYPES)
        self.assertEqual(payload["task"], "Search")
        self.assertEqual(payload["visible_elements"]["count"], 2)
        self.assertEqual(len(payload["visible_elements"]["items"]), 2)
        self.assertEqual(payload["safety_runtime"]["executable_actions"], ["wait"])
        self.assertNotIn("screenshot_path", encoded)
        self.assertNotIn("image_bytes", encoded)

    def test_valid_mock_target_hint_becomes_proposal(self) -> None:
        proposal = build_ai_proposal_from_context(
            _planner_context(),
            {
                "type": "target_hint",
                "target_element_id": "element_search",
                "target_label": "Ignored label",
                "target_bbox": {"x": 999, "y": 999, "width": 1, "height": 1},
                "reason": "Use the visible search target.",
            },
        )

        action = proposal["action"]
        self.assertTrue(proposal["proposal_id"].startswith("proposal_ai_"))
        self.assertEqual(action["type"], "target_hint")
        self.assertEqual(action["target_element_id"], "element_search")
        self.assertEqual(action["target_label"], "Search")
        self.assertEqual(action["target_bbox"], {"x": 30, "y": 40, "width": 120, "height": 36})
        self.assertEqual(action["risk"], "low")
        self.assertIs(action["requires_approval"], False)

    def test_valid_mock_switch_app_hint_becomes_proposal(self) -> None:
        proposal = build_ai_proposal_from_context(
            _planner_context(task="Use WeChat", app_guess="Chrome"),
            {
                "action": {
                    "type": "switch_app_hint",
                    "target_app": "WeChat",
                    "reason": "Task asks for WeChat.",
                }
            },
        )

        action = proposal["action"]
        self.assertEqual(action["type"], "switch_app_hint")
        self.assertEqual(action["target"], "WeChat")
        self.assertEqual(action["parameters"], {"current_app": "Chrome"})
        self.assertEqual(action["risk"], "low")

    def test_valid_mock_no_op_becomes_proposal(self) -> None:
        proposal = build_ai_proposal_from_context(
            _planner_context(),
            {"type": "no_op", "reason": "Need more context."},
        )

        action = proposal["action"]
        self.assertEqual(action["type"], "no_op")
        self.assertEqual(action["target"], "current_window")
        self.assertEqual(action["reason"], "Need more context.")
        self.assertIsNone(action_contract_from_proposal(proposal))

    def test_mock_click_output_is_rejected_as_no_op(self) -> None:
        proposal = build_ai_proposal_from_context(
            _planner_context(),
            {"type": "click", "target_element_id": "element_search"},
        )

        action = proposal["action"]
        self.assertEqual(action["type"], "no_op")
        self.assertIn("Executable action type 'click'", action["reason"])

    def test_mock_executable_outputs_are_rejected_as_no_op(self) -> None:
        executable_action_types = [
            "type",
            "type_text",
            "hotkey",
            "press",
            "scroll",
            "send",
            "delete",
            "submit",
            "launch_app",
            "switch_app",
        ]

        for action_type in executable_action_types:
            with self.subTest(action_type=action_type):
                proposal = build_ai_proposal_from_context(
                    _planner_context(),
                    {"action": {"type": action_type}},
                )

                self.assertEqual(proposal["action"]["type"], "no_op")
                self.assertIn(f"Executable action type '{action_type}'", proposal["action"]["reason"])

    def test_malformed_output_is_rejected_safely(self) -> None:
        cases = [
            ("{not json", "not valid JSON"),
            (["nope"], "must be a JSON object or dict"),
            ({"action": "click"}, "structured action object"),
        ]

        for raw_output, reason_fragment in cases:
            with self.subTest(raw_output=raw_output):
                proposal = build_ai_proposal_from_context(_planner_context(), raw_output)

                self.assertEqual(proposal["action"]["type"], "no_op")
                self.assertIn(reason_fragment, proposal["action"]["reason"])

    def test_missing_target_element_id_is_rejected_safely(self) -> None:
        validation = validate_ai_proposal(
            json.dumps({"type": "target_hint", "target_element_id": "element_missing"}),
            _planner_context(),
        )
        proposal = build_ai_proposal_from_context(
            _planner_context(),
            {"type": "target_hint", "target_element_id": "element_missing"},
        )

        self.assertIs(validation["valid"], False)
        self.assertEqual(proposal["action"]["type"], "no_op")
        self.assertIn("not present in planner_context", proposal["action"]["reason"])

    def test_validated_target_hint_passes_existing_pipeline_as_preview_only(self) -> None:
        context = _planner_context()
        validation = validate_ai_proposal(
            {"type": "target_hint", "target_element_id": "element_search"},
            context,
        )
        proposal = build_ai_proposal_from_context(context, validation["action"])
        safety_decision = assess_proposal(proposal)
        action_contract = action_contract_from_proposal(proposal)
        click_readiness = click_readiness_for_response(action_contract, safety_decision)

        self.assertIs(validation["valid"], True)
        self.assertEqual(safety_decision["decision"], "allowed")
        self.assertEqual(action_contract["type"], "click")
        self.assertEqual(action_contract["status"], "preview_only")
        self.assertIs(action_contract["executed"], False)
        self.assertEqual(click_readiness["status"], "blocked")
        self.assertIn("preview-only contract", click_readiness["reasons"])
        self.assertIn("click capability disabled", click_readiness["reasons"])


def _planner_context(task: str = "Search", app_guess: str = "Chrome") -> dict[str, object]:
    return build_planner_context(
        task,
        {
            "ui_state_id": "state_0042",
            "source_observation_id": "obs_0042",
            "app_guess": app_guess,
            "state_guess": "browser_window",
            "summary": "A compact fake UI state for AI planner harness tests.",
            "confidence": 0.91,
            "screen": {
                "width": 1440,
                "height": 900,
                "screenshot_path": "runs/run_001/obs_0042.png",
            },
            "visible_elements": [
                {
                    "id": "element_search",
                    "type": "button",
                    "label": "Search",
                    "bbox": {"x": 30, "y": 40, "width": 120, "height": 36},
                    "confidence": 0.96,
                },
                {
                    "id": "element_cancel",
                    "type": "button",
                    "label": "Cancel",
                    "bbox": {"x": 180, "y": 40, "width": 100, "height": 36},
                    "confidence": 0.95,
                },
            ],
            "visible_text": ["Search", "Cancel"],
        },
        runtime_status={
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
        },
        recent_events=[
            {
                "type": "observation.created",
                "timestamp": "2026-01-01T00:00:00Z",
                "observation_id": "obs_0042",
                "screenshot_path": "runs/run_001/obs_0042.png",
            }
        ],
    )


if __name__ == "__main__":
    unittest.main()
