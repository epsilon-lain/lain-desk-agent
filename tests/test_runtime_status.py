from __future__ import annotations

import os
import unittest
from unittest.mock import patch

import _path  # noqa: F401
from lain_desk_agent.main import runtime_status_payload
from lain_desk_agent.permission_profile import PERMISSION_PROFILE_ENV


class RuntimeStatusTests(unittest.TestCase):
    def test_runtime_status_payload_summarizes_safety_state(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            payload = runtime_status_payload()

        self.assertEqual(
            payload["runtime"],
            {
                "mode": "local",
                "desktop_control": False,
                "actuation": "wait_only",
                "verification": True,
            },
        )
        self.assertEqual(payload["permission_profile"], "wait_only")
        self.assertTrue(payload["capabilities"]["wait"]["enabled"])
        self.assertFalse(payload["capabilities"]["click"]["enabled"])
        self.assertEqual(
            payload["execution_policy"],
            {
                "current_profile": "wait_only",
                "desktop_control": False,
                "executable_actions": ["wait"],
                "blocked_actions_count": 5,
            },
        )
        self.assertFalse(payload["click_readiness"]["enabled"])
        self.assertEqual(payload["click_readiness"]["reason"], "Real click execution is not enabled.")
        self.assertEqual(
            payload["ai_planner"],
            {
                "status": "inactive",
                "planner_mode": "rule_based",
                "ai_planner_available": False,
                "external_llm_calls": False,
            },
        )
        self.assertEqual(
            payload["resource_guard"],
            {
                "enabled": True,
                "max_observations_per_run": 100,
                "max_run_size_mb": 300,
                "min_free_disk_mb": 1024,
            },
        )

    def test_runtime_status_uses_current_permission_profile(self) -> None:
        with patch.dict(os.environ, {PERMISSION_PROFILE_ENV: "safe_readonly"}):
            payload = runtime_status_payload()

        self.assertEqual(payload["permission_profile"], "safe_readonly")
        self.assertEqual(payload["runtime"]["actuation"], "wait_only")
        self.assertFalse(payload["runtime"]["desktop_control"])
        self.assertEqual(payload["execution_policy"]["current_profile"], "safe_readonly")
        self.assertEqual(payload["execution_policy"]["executable_actions"], [])
        self.assertEqual(payload["execution_policy"]["blocked_actions_count"], 6)

    def test_runtime_status_reports_ai_proposal_availability(self) -> None:
        with patch.dict(
            os.environ,
            {
                "LAIN_AGENT_PLANNER_MODE": "ai_proposal",
                "OPENAI_API_KEY": "test-key",
            },
        ):
            payload = runtime_status_payload()

        self.assertEqual(payload["ai_planner"]["status"], "available")
        self.assertEqual(payload["ai_planner"]["planner_mode"], "ai_proposal")
        self.assertIs(payload["ai_planner"]["ai_planner_available"], True)
        self.assertIs(payload["ai_planner"]["external_llm_calls"], True)

    def test_runtime_status_reports_missing_ai_key(self) -> None:
        with patch.dict(os.environ, {"LAIN_AGENT_PLANNER_MODE": "ai_proposal"}, clear=True):
            payload = runtime_status_payload()

        self.assertEqual(payload["ai_planner"]["status"], "missing_api_key")
        self.assertEqual(payload["ai_planner"]["planner_mode"], "ai_proposal")
        self.assertIs(payload["ai_planner"]["ai_planner_available"], False)
        self.assertIs(payload["ai_planner"]["external_llm_calls"], False)


if __name__ == "__main__":
    unittest.main()
