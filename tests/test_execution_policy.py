from __future__ import annotations

import json
import os
import threading
import unittest
from unittest.mock import patch
from urllib.request import urlopen

import _path  # noqa: F401
from lain_desk_agent.execution_policy import ACTION_TYPES, PROFILES, execution_policy_payload
from lain_desk_agent.main import create_server
from lain_desk_agent.permission_profile import PERMISSION_PROFILE_ENV


class ExecutionPolicyMatrixTests(unittest.TestCase):
    def test_policy_matrix_lists_all_profiles_and_actions(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            payload = execution_policy_payload()

        self.assertEqual(payload["profiles"], PROFILES)
        self.assertEqual(payload["action_types"], ACTION_TYPES)

        for profile in PROFILES:
            with self.subTest(profile=profile):
                self.assertEqual(set(payload["matrix"][profile]), set(ACTION_TYPES))

    def test_safe_readonly_blocks_every_action(self) -> None:
        with patch.dict(os.environ, {PERMISSION_PROFILE_ENV: "safe_readonly"}):
            payload = execution_policy_payload()

        profile_policy = payload["matrix"]["safe_readonly"]
        self.assertEqual(payload["summary"]["executable_actions"], [])
        self.assertEqual(payload["summary"]["blocked_actions_count"], len(ACTION_TYPES))

        for action_type in ACTION_TYPES:
            with self.subTest(action_type=action_type):
                self.assertIs(profile_policy[action_type]["allowed"], False)
                self.assertIs(profile_policy[action_type]["executable"], False)
                self.assertEqual(profile_policy[action_type]["mode"], "blocked")

    def test_wait_only_executes_only_wait(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            payload = execution_policy_payload()

        profile_policy = payload["matrix"]["wait_only"]
        self.assertEqual(payload["current_profile"], "wait_only")
        self.assertEqual(payload["summary"]["executable_actions"], ["wait"])
        self.assertEqual(payload["summary"]["blocked_actions_count"], 5)
        self.assertIs(profile_policy["wait"]["allowed"], True)
        self.assertIs(profile_policy["wait"]["executable"], True)
        self.assertEqual(profile_policy["wait"]["mode"], "wait_only")

        for action_type in ["click", "type", "hotkey", "scroll", "switch_app"]:
            with self.subTest(action_type=action_type):
                self.assertIs(profile_policy[action_type]["allowed"], False)
                self.assertIs(profile_policy[action_type]["executable"], False)
                self.assertEqual(profile_policy[action_type]["mode"], "blocked")

    def test_experimental_profile_keeps_desktop_actions_non_executable(self) -> None:
        with patch.dict(os.environ, {PERMISSION_PROFILE_ENV: "experimental_desktop_control"}):
            payload = execution_policy_payload()

        profile_policy = payload["matrix"]["experimental_desktop_control"]
        self.assertEqual(payload["summary"]["executable_actions"], ["wait"])

        for action_type in ["click", "type", "hotkey", "scroll", "switch_app"]:
            with self.subTest(action_type=action_type):
                self.assertIs(profile_policy[action_type]["allowed"], False)
                self.assertIs(profile_policy[action_type]["executable"], False)
                self.assertEqual(profile_policy[action_type]["mode"], "future_experimental")

    def test_execution_policy_endpoint_returns_matrix_without_observing(self) -> None:
        server = create_server("127.0.0.1", 0)
        host, port = server.server_address
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            with (
                patch("lain_desk_agent.main.observe", side_effect=AssertionError("observe called")),
                patch("lain_desk_agent.main.understand", side_effect=AssertionError("understand called")),
            ):
                with urlopen(f"http://{host}:{port}/execution-policy", timeout=5) as response:
                    payload = json.loads(response.read().decode("utf-8"))
        finally:
            server.shutdown()
            thread.join(timeout=2)
            server.server_close()

        self.assertEqual(payload["action_types"], ACTION_TYPES)
        self.assertEqual(payload["profiles"], PROFILES)
        self.assertIn("wait_only", payload["matrix"])
        self.assertFalse(payload["desktop_control"])


if __name__ == "__main__":
    unittest.main()
