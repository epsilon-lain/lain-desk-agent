from __future__ import annotations

import unittest

import _path  # noqa: F401
from lain_desk_agent.verification import verification_failed_result, verify_execution


class WaitOnlyVerificationTests(unittest.TestCase):
    def test_wait_execution_with_post_observation_is_verified(self) -> None:
        result = verify_execution(
            {"type": "wait"},
            {"status": "executed", "type": "wait", "executed": True},
            {"observation_id": "obs_0002"},
        )

        self.assertEqual(
            result,
            {
                "status": "verified",
                "reason": "Wait action completed and a post-execution observation was captured.",
                "expected_change": "none",
                "confidence": 0.8,
            },
        )

    def test_wait_execution_without_post_observation_is_unknown(self) -> None:
        result = verify_execution(
            {"type": "wait"},
            {"status": "executed", "type": "wait", "executed": True},
            None,
        )

        self.assertEqual(result["status"], "unknown")
        self.assertEqual(result["expected_change"], "none")
        self.assertEqual(result["confidence"], 0.0)

    def test_non_wait_action_is_unknown(self) -> None:
        result = verify_execution(
            {"type": "click"},
            {"status": "executed", "type": "click", "executed": True},
            {"observation_id": "obs_0002"},
        )

        self.assertEqual(result["status"], "unknown")
        self.assertEqual(result["expected_change"], "unknown")

    def test_verification_failed_result_is_unknown(self) -> None:
        result = verification_failed_result("disk low")

        self.assertEqual(result["status"], "unknown")
        self.assertEqual(result["reason"], "Post-execution observation failed: disk low")
        self.assertEqual(result["expected_change"], "none")


if __name__ == "__main__":
    unittest.main()
