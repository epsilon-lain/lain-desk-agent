from __future__ import annotations

import unittest

import _path  # noqa: F401
from lain_desk_agent.capabilities import get_capabilities, get_capability, is_action_executable


class CapabilityRegistryTests(unittest.TestCase):
    def test_wait_is_enabled_and_executable(self) -> None:
        capability = get_capability("wait")

        self.assertIs(capability["enabled"], True)
        self.assertIs(capability["executable"], True)
        self.assertEqual(capability["risk"], "low")
        self.assertTrue(is_action_executable("wait"))

    def test_mouse_keyboard_and_switch_actions_are_disabled(self) -> None:
        capabilities = get_capabilities()

        for action_type in ["click", "type", "type_text", "hotkey", "press", "scroll", "switch_app"]:
            with self.subTest(action_type=action_type):
                self.assertIn(action_type, capabilities)
                self.assertIs(capabilities[action_type]["enabled"], False)
                self.assertIs(capabilities[action_type]["executable"], False)
                self.assertFalse(is_action_executable(action_type))
                self.assertIn("Capability Registry v0", capabilities[action_type]["reason"])

    def test_unknown_action_is_not_executable(self) -> None:
        capability = get_capability("launch_app")

        self.assertIs(capability["enabled"], False)
        self.assertIs(capability["executable"], False)
        self.assertEqual(capability["risk"], "unknown")
        self.assertIn("not registered", capability["reason"])
        self.assertFalse(is_action_executable("launch_app"))

    def test_get_capabilities_returns_a_copy(self) -> None:
        capabilities = get_capabilities()
        capabilities["wait"]["enabled"] = False

        self.assertIs(get_capability("wait")["enabled"], True)


if __name__ == "__main__":
    unittest.main()
