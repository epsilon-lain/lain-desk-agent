from __future__ import annotations

import json
import os
import threading
import unittest
from unittest.mock import patch
from urllib.request import urlopen

import _path  # noqa: F401
from lain_desk_agent.action_contract import action_contract_from_proposal
from lain_desk_agent.ai_planner import (
    ALLOWED_PROPOSAL_ACTION_TYPES,
    build_ai_planner_prompt_or_payload,
    build_ai_proposal_from_context,
    build_ai_proposal_result_from_context,
    build_ai_proposal_with_llm,
    build_openai_responses_payload,
    request_ai_proposal_from_openai,
    validate_ai_proposal,
)
from lain_desk_agent.main import click_readiness_for_response, create_server
from lain_desk_agent.planner_context import build_planner_context
from lain_desk_agent.safety import assess_proposal


class AIPlannerHarnessTests(unittest.TestCase):
    def test_prompt_payload_is_compact_and_explicitly_proposal_only(self) -> None:
        context = _planner_context()
        payload = build_ai_planner_prompt_or_payload(context)
        encoded = json.dumps(payload)

        self.assertEqual(payload["planner"]["mode"], "proposal_only")
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

    def test_unknown_action_type_is_rejected_as_no_op(self) -> None:
        proposal = build_ai_proposal_from_context(
            _planner_context(),
            {"type": "drag", "reason": "Try an unsupported action."},
        )

        self.assertEqual(proposal["action"]["type"], "no_op")
        self.assertIn("Unsupported proposal action type 'drag'", proposal["action"]["reason"])

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

    def test_openai_payload_is_sanitized_and_response_validates(self) -> None:
        seen_payloads = []

        def fake_post_json(url, payload, headers, timeout_seconds):
            seen_payloads.append(payload)
            self.assertEqual(url, "https://api.openai.com/v1/responses")
            self.assertIn("Authorization", headers)
            self.assertGreater(timeout_seconds, 0)
            encoded = json.dumps(payload)
            self.assertNotIn("screenshot_path", encoded)
            self.assertNotIn("image_bytes", encoded)
            self.assertNotIn("runs/run_001/obs_0042.png", encoded)
            return {
                "output_text": json.dumps(
                    {
                        "action": {
                            "type": "target_hint",
                            "target_element_id": "element_search",
                            "target": "",
                            "reason": "Use Search.",
                        }
                    }
                )
            }

        proposal = build_ai_proposal_with_llm(
            _planner_context(),
            api_key="test-secret",
            http_post_json=fake_post_json,
        )

        self.assertEqual(len(seen_payloads), 1)
        self.assertEqual(proposal["action"]["type"], "target_hint")
        self.assertEqual(proposal["action"]["target_element_id"], "element_search")
        self.assertEqual(proposal["action"]["target_label"], "Search")

    def test_openai_unsafe_output_is_rejected_safely(self) -> None:
        proposal = build_ai_proposal_with_llm(
            _planner_context(),
            api_key="test-secret",
            http_post_json=lambda *_args: {"output_text": '{"type": "click"}'},
        )

        self.assertEqual(proposal["action"]["type"], "no_op")
        self.assertIn("Executable action type 'click'", proposal["action"]["reason"])

    def test_openai_request_requires_api_key(self) -> None:
        with self.assertRaisesRegex(Exception, "OPENAI_API_KEY"):
            request_ai_proposal_from_openai(_planner_context(), api_key="")

    def test_openai_request_payload_asks_for_structured_json_only(self) -> None:
        payload = build_openai_responses_payload(_planner_context())

        self.assertEqual(payload["store"], False)
        self.assertEqual(payload["text"]["format"]["type"], "json_schema")
        self.assertEqual(
            payload["text"]["format"]["schema"]["properties"]["action"]["properties"]["type"]["enum"],
            ALLOWED_PROPOSAL_ACTION_TYPES,
        )

    def test_proposal_endpoint_stays_rule_based_without_api_key(self) -> None:
        payload = _proposal_endpoint_payload(
            env={},
            ai_side_effect=AssertionError("AI planner should not be called"),
        )

        self.assertEqual(payload["planner"]["planner_mode"], "rule_based")
        self.assertEqual(payload["planner"]["source"], "rule_based")
        self.assertEqual(payload["planner_trace"]["planner_mode"], "rule_based")
        self.assertEqual(payload["planner_trace"]["planner_source"], "rule_based")
        self.assertEqual(payload["planner_trace"]["validation_status"], "not_applicable")
        self.assertIs(payload["planner_trace"]["fallback_used"], False)
        self.assertEqual(payload["planner_trace"]["context_summary"]["visible_element_count"], 1)
        self.assertEqual(payload["planner_trace"]["context_summary"]["executable_actions"], ["wait"])
        self.assertEqual(payload["proposal"]["action"]["type"], "target_hint")
        self.assertEqual(payload["action_contract"]["type"], "click")
        self.assertEqual(payload["click_readiness"]["status"], "blocked")
        self.assertNotIn("screenshot_path", json.dumps(payload["planner_trace"]))

    def test_proposal_endpoint_trace_shape_is_compact(self) -> None:
        payload = _proposal_endpoint_payload(
            env={},
            ai_side_effect=AssertionError("AI planner should not be called"),
        )
        trace = payload["planner_trace"]
        context_summary = trace["context_summary"]

        self.assertEqual(
            set(trace),
            {
                "planner_mode",
                "planner_source",
                "ai_planner_available",
                "external_llm_call_attempted",
                "external_llm_call_succeeded",
                "validation_status",
                "fallback_used",
                "context_summary",
                "output_action_type",
            },
        )
        self.assertEqual(
            set(context_summary),
            {
                "visible_element_count",
                "recent_event_count",
                "desktop_control",
                "executable_actions",
            },
        )
        self.assertNotIn("image_bytes", json.dumps(trace))
        self.assertNotIn("runs/run_001/obs_0042.png", json.dumps(trace))

    def test_proposal_endpoint_uses_ai_mode_when_key_is_available(self) -> None:
        seen_contexts = []

        def fake_ai_planner(planner_context, api_key):
            seen_contexts.append(planner_context)
            encoded_context = json.dumps(planner_context)
            self.assertEqual(api_key, "test-secret")
            self.assertNotIn("screenshot_path", encoded_context)
            self.assertNotIn("runs/run_001/obs_0042.png", encoded_context)
            return build_ai_proposal_result_from_context(
                planner_context,
                {"type": "target_hint", "target_element_id": "element_search"},
            )

        payload = _proposal_endpoint_payload(
            env={
                "LAIN_AGENT_PLANNER_MODE": "ai_proposal",
                "OPENAI_API_KEY": "test-secret",
            },
            ai_side_effect=fake_ai_planner,
        )

        self.assertEqual(len(seen_contexts), 1)
        self.assertEqual(payload["planner"]["planner_mode"], "ai_proposal")
        self.assertEqual(payload["planner"]["source"], "ai_proposal")
        self.assertEqual(payload["planner"]["fallback"], False)
        self.assertEqual(payload["planner_trace"]["planner_mode"], "ai_proposal")
        self.assertEqual(payload["planner_trace"]["planner_source"], "ai")
        self.assertIs(payload["planner_trace"]["ai_planner_available"], True)
        self.assertIs(payload["planner_trace"]["external_llm_call_attempted"], True)
        self.assertIs(payload["planner_trace"]["external_llm_call_succeeded"], True)
        self.assertEqual(payload["planner_trace"]["validation_status"], "accepted")
        self.assertIs(payload["planner_trace"]["fallback_used"], False)
        self.assertEqual(payload["planner_trace"]["output_action_type"], "target_hint")
        self.assertEqual(payload["proposal"]["action"]["type"], "target_hint")
        self.assertEqual(payload["safety_decision"]["decision"], "allowed")
        self.assertEqual(payload["action_contract"]["status"], "preview_only")

    def test_proposal_endpoint_traces_rejected_ai_output(self) -> None:
        def fake_ai_planner(planner_context, api_key):
            self.assertEqual(api_key, "test-secret")
            return build_ai_proposal_result_from_context(planner_context, {"type": "click"})

        payload = _proposal_endpoint_payload(
            env={
                "LAIN_AGENT_PLANNER_MODE": "ai_proposal",
                "OPENAI_API_KEY": "test-secret",
            },
            ai_side_effect=fake_ai_planner,
        )

        self.assertEqual(payload["proposal"]["action"]["type"], "no_op")
        self.assertIsNone(payload["action_contract"])
        self.assertEqual(payload["click_readiness"]["status"], "not_applicable")
        self.assertEqual(payload["planner_trace"]["planner_source"], "ai")
        self.assertEqual(payload["planner_trace"]["validation_status"], "rejected")
        self.assertIn("Executable action type 'click'", payload["planner_trace"]["validation_reason"])
        self.assertIs(payload["planner_trace"]["fallback_used"], False)
        self.assertEqual(payload["planner_trace"]["output_action_type"], "no_op")

    def test_proposal_endpoint_falls_back_when_ai_key_is_missing(self) -> None:
        payload = _proposal_endpoint_payload(
            env={"LAIN_AGENT_PLANNER_MODE": "ai_proposal"},
            ai_side_effect=AssertionError("AI planner should not be called without a key"),
        )

        self.assertEqual(payload["planner"]["planner_mode"], "ai_proposal")
        self.assertEqual(payload["planner"]["source"], "rule_based")
        self.assertEqual(payload["planner"]["fallback"], True)
        self.assertIn("OPENAI_API_KEY", payload["planner"]["fallback_reason"])
        self.assertEqual(payload["planner_trace"]["planner_source"], "fallback")
        self.assertIs(payload["planner_trace"]["ai_planner_available"], False)
        self.assertIs(payload["planner_trace"]["external_llm_call_attempted"], False)
        self.assertIs(payload["planner_trace"]["external_llm_call_succeeded"], False)
        self.assertIs(payload["planner_trace"]["fallback_used"], True)
        self.assertIn("OPENAI_API_KEY", payload["planner_trace"]["fallback_reason"])
        self.assertEqual(payload["proposal"]["action"]["type"], "target_hint")

    def test_proposal_endpoint_falls_back_when_ai_planner_errors(self) -> None:
        payload = _proposal_endpoint_payload(
            env={
                "LAIN_AGENT_PLANNER_MODE": "ai_proposal",
                "OPENAI_API_KEY": "test-secret",
            },
            ai_side_effect=RuntimeError("network failure"),
        )

        self.assertEqual(payload["planner"]["planner_mode"], "ai_proposal")
        self.assertEqual(payload["planner"]["source"], "rule_based")
        self.assertEqual(payload["planner"]["fallback"], True)
        self.assertEqual(
            payload["planner"]["fallback_reason"],
            "AI planner failed; fell back to rule-based planner.",
        )
        self.assertEqual(payload["planner_trace"]["planner_source"], "fallback")
        self.assertIs(payload["planner_trace"]["external_llm_call_attempted"], True)
        self.assertIs(payload["planner_trace"]["external_llm_call_succeeded"], False)
        self.assertIs(payload["planner_trace"]["fallback_used"], True)
        self.assertEqual(
            payload["planner_trace"]["fallback_reason"],
            "AI planner failed; fell back to rule-based planner.",
        )
        self.assertEqual(payload["proposal"]["action"]["type"], "target_hint")


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


def _proposal_endpoint_payload(
    env: dict[str, str],
    ai_return_value: dict[str, object] | None = None,
    ai_side_effect: object | None = None,
) -> dict[str, object]:
    server = create_server("127.0.0.1", 0)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with (
            patch.dict(os.environ, env, clear=True),
            patch("lain_desk_agent.main.observe", return_value=_observation()),
            patch("lain_desk_agent.main.understand", return_value=_ui_state()),
            patch(
                "lain_desk_agent.main.build_ai_proposal_result_with_llm",
                return_value=ai_return_value,
                side_effect=ai_side_effect,
            ),
        ):
            with urlopen(f"http://{host}:{port}/proposal?task=Search", timeout=5) as response:
                return json.loads(response.read().decode("utf-8"))
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()


def _observation() -> dict[str, object]:
    return {
        "observation_id": "obs_0042",
        "screen": {
            "width": 1440,
            "height": 900,
            "screenshot_path": "runs/run_001/obs_0042.png",
        },
        "active_window": {
            "title": "Chrome",
            "app_name": "chrome.exe",
        },
    }


def _ui_state() -> dict[str, object]:
    return {
        "ui_state_id": "state_0042",
        "source_observation_id": "obs_0042",
        "app_guess": "Chrome",
        "state_guess": "browser_window",
        "summary": "A browser with Search visible.",
        "confidence": 0.9,
        "visible_text": ["Search"],
        "visible_text_boxes": [],
        "visible_elements": [
            {
                "id": "element_search",
                "type": "button",
                "label": "Search",
                "bbox": {"x": 30, "y": 40, "width": 120, "height": 36},
                "confidence": 0.96,
            }
        ],
    }


if __name__ == "__main__":
    unittest.main()
