from __future__ import annotations

import os
import unittest
from unittest.mock import patch

import _path  # noqa: F401
from lain_desk_agent.permission_profile import (
    DEFAULT_PERMISSION_PROFILE,
    PERMISSION_PROFILE_ENV,
    get_current_permission_profile,
    get_permission_profile_payload,
    is_profile_allowed_for_action,
    permission_profile_block_reason,
)


class PermissionProfileTests(unittest.TestCase):
    def test_default_profile_is_wait_only(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_current_permission_profile(), DEFAULT_PERMISSION_PROFILE)
            self.assertTrue(is_profile_allowed_for_action("wait"))
            self.assertFalse(is_profile_allowed_for_action("click"))

    def test_safe_readonly_allows_no_actions(self) -> None:
        with patch.dict(os.environ, {PERMISSION_PROFILE_ENV: "safe_readonly"}):
            self.assertEqual(get_current_permission_profile(), "safe_readonly")
            self.assertFalse(is_profile_allowed_for_action("wait"))
            self.assertFalse(is_profile_allowed_for_action("click"))

    def test_experimental_profile_does_not_enable_desktop_control(self) -> None:
        with patch.dict(os.environ, {PERMISSION_PROFILE_ENV: "experimental_desktop_control"}):
            self.assertEqual(get_current_permission_profile(), "experimental_desktop_control")
            self.assertTrue(is_profile_allowed_for_action("wait"))
            self.assertFalse(is_profile_allowed_for_action("click"))
            self.assertFalse(is_profile_allowed_for_action("type"))
            self.assertFalse(is_profile_allowed_for_action("hotkey"))
            self.assertFalse(is_profile_allowed_for_action("scroll"))

    def test_unknown_profile_falls_back_to_safe_readonly(self) -> None:
        with patch.dict(os.environ, {PERMISSION_PROFILE_ENV: "oops"}):
            self.assertEqual(get_current_permission_profile(), "safe_readonly")
            self.assertFalse(is_profile_allowed_for_action("wait"))

    def test_permission_profile_payload_is_json_ready(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            payload = get_permission_profile_payload()

        self.assertEqual(payload["profile"], "wait_only")
        self.assertEqual(payload["default_profile"], "wait_only")
        self.assertIn("safe_readonly", payload["profiles"])
        self.assertIn("experimental_desktop_control", payload["profiles"])

    def test_permission_profile_block_reason_names_profile(self) -> None:
        with patch.dict(os.environ, {PERMISSION_PROFILE_ENV: "safe_readonly"}):
            reason = permission_profile_block_reason("wait")

        self.assertIn("Blocked by permission profile 'safe_readonly'", reason)
        self.assertIn("wait", reason)


if __name__ == "__main__":
    unittest.main()
