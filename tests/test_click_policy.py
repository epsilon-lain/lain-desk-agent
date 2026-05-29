from __future__ import annotations

import os
import unittest
from unittest.mock import patch

import _path  # noqa: F401
from lain_desk_agent.capabilities import get_capability
from lain_desk_agent.click_policy import (
    click_readiness_metadata,
    click_readiness_not_applicable,
    evaluate_click_readiness,
)
from lain_desk_agent.main import click_readiness_for_response
from lain_desk_agent.permission_profile import get_permission_profile_payload


class ClickReadinessPolicyTests(unittest.TestCase):
    def test_preview_click_contract_is_blocked_by_current_runtime_policy(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            readiness = evaluate_click_readiness(
                _click_contract(status="preview_only"),
                {"decision": "allowed", "risk": "low"},
                get_capability("click"),
                get_permission_profile_payload(),
            )

        self.assertIs(readiness["ready"], False)
        self.assertEqual(readiness["status"], "blocked")
        self.assertEqual(readiness["risk"], "medium")
        self.assertIn("preview-only contract", readiness["reasons"])
        self.assertIn("click capability disabled", readiness["reasons"])
        self.assertIn("permission profile does not allow click", readiness["reasons"])

    def test_high_risk_label_blocks_otherwise_ready_click_contract(self) -> None:
        readiness = evaluate_click_readiness(
            _click_contract(status="approved_for_execution", target_label="Delete account"),
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
        )

        self.assertIs(readiness["ready"], False)
        self.assertEqual(readiness["status"], "blocked")
        self.assertEqual(readiness["risk"], "high")
        self.assertEqual(readiness["reasons"], ["high-risk target label"])

    def test_chinese_high_risk_label_blocks_click_contract(self) -> None:
        readiness = evaluate_click_readiness(
            _click_contract(status="approved_for_execution", target_label="确认支付"),
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
        )

        self.assertIs(readiness["ready"], False)
        self.assertIn("high-risk target label", readiness["reasons"])

    def test_safety_blocked_prevents_readiness(self) -> None:
        readiness = evaluate_click_readiness(
            _click_contract(status="approved_for_execution", target_label="Search"),
            {"decision": "blocked", "risk": "high"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
        )

        self.assertIs(readiness["ready"], False)
        self.assertIn("safety decision blocked", readiness["reasons"])

    def test_invalid_geometry_prevents_readiness(self) -> None:
        contract = _click_contract(status="approved_for_execution")
        contract["bbox"] = {"x": 1, "y": 2, "width": 0, "height": 4}
        contract["center"] = {"x": "nan", "y": 4}

        readiness = evaluate_click_readiness(
            contract,
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
        )

        self.assertIs(readiness["ready"], False)
        self.assertIn("invalid bbox", readiness["reasons"])
        self.assertIn("invalid center", readiness["reasons"])

    def test_otherwise_ready_click_contract_can_be_marked_ready_by_policy_inputs(self) -> None:
        readiness = evaluate_click_readiness(
            _click_contract(status="approved_for_execution", target_label="Search"),
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
        )

        self.assertIs(readiness["ready"], True)
        self.assertEqual(readiness["status"], "ready")
        self.assertEqual(readiness["reasons"], [])

    def test_non_click_response_is_not_applicable(self) -> None:
        readiness = click_readiness_for_response(
            {
                "action_id": "action_0001",
                "type": "switch_app",
                "status": "preview_only",
                "executed": False,
            },
            {"decision": "allowed", "risk": "low"},
        )

        self.assertEqual(readiness, click_readiness_not_applicable())

    def test_metadata_describes_disabled_static_policy(self) -> None:
        metadata = click_readiness_metadata()

        self.assertIs(metadata["enabled"], False)
        self.assertEqual(metadata["reason"], "Real click execution is not enabled.")
        self.assertIn("click capability is enabled and executable", metadata["required_checks"])
        self.assertIn("发送", metadata["high_risk_labels"])


def _click_contract(
    status: str,
    target_label: str = "Search",
) -> dict[str, object]:
    return {
        "action_id": "action_0001",
        "source_proposal_id": "proposal_0001",
        "type": "click",
        "target_element_id": "element_0001",
        "target_label": target_label,
        "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
        "center": {"x": 50, "y": 32},
        "status": status,
        "executed": False,
    }


def _profile_payload_with_click_allowed() -> dict[str, object]:
    return {
        "profile": "click_allowed_for_policy_test",
        "profiles": {
            "click_allowed_for_policy_test": {
                "allowed_actions": ["click"],
            },
        },
    }


if __name__ == "__main__":
    unittest.main()
