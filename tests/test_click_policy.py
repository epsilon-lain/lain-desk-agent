from __future__ import annotations

import os
import unittest
from datetime import datetime, timedelta, timezone
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


TEST_NOW = datetime(2026, 1, 1, 0, 0, 5, tzinfo=timezone.utc)


class ClickReadinessPolicyTests(unittest.TestCase):
    def test_preview_click_contract_is_blocked_by_current_runtime_policy(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            readiness = evaluate_click_readiness(
                _click_contract(status="preview_only"),
                {"decision": "allowed", "risk": "low"},
                get_capability("click"),
                get_permission_profile_payload(),
                screen=_screen(),
                now=TEST_NOW,
            )

        self.assertIs(readiness["ready"], False)
        self.assertEqual(readiness["status"], "blocked")
        self.assertEqual(readiness["risk"], "medium")
        self.assertIn("preview-only contract", readiness["reasons"])
        self.assertIn("click capability disabled", readiness["reasons"])
        self.assertIn("permission profile does not allow click", readiness["reasons"])
        self.assertIn("preview_only_contract", readiness["blocker_codes"])
        self.assertIn("action_not_enabled_by_policy", readiness["blocker_codes"])
        self.assertEqual(_check_status(readiness, "contract_status"), "blocked")
        self.assertEqual(_check_status(readiness, "click_capability"), "blocked")
        self.assertEqual(_check_status(readiness, "permission_profile"), "blocked")

    def test_preview_only_blocks_otherwise_ready_contract(self) -> None:
        readiness = evaluate_click_readiness(
            _click_contract(status="preview_only"),
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
            screen=_screen(),
            now=TEST_NOW,
        )

        self.assertIs(readiness["ready"], False)
        self.assertEqual(readiness["reasons"], ["preview-only contract"])
        self.assertEqual(readiness["blocker_codes"], ["preview_only_contract"])
        self.assertEqual(_check_status(readiness, "contract_status"), "blocked")

    def test_disabled_click_capability_blocks_readiness(self) -> None:
        readiness = evaluate_click_readiness(
            _click_contract(status="approved_for_execution"),
            {"decision": "allowed", "risk": "low"},
            {"enabled": False, "executable": False, "risk": "medium"},
            _profile_payload_with_click_allowed(),
            screen=_screen(),
            now=TEST_NOW,
        )

        self.assertIs(readiness["ready"], False)
        self.assertIn("click capability disabled", readiness["reasons"])
        self.assertIn("action_not_enabled_by_policy", readiness["blocker_codes"])
        self.assertEqual(_check_status(readiness, "click_capability"), "blocked")

    def test_permission_profile_blocks_readiness(self) -> None:
        readiness = evaluate_click_readiness(
            _click_contract(status="approved_for_execution"),
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            get_permission_profile_payload(),
            screen=_screen(),
            now=TEST_NOW,
        )

        self.assertIs(readiness["ready"], False)
        self.assertIn("permission profile does not allow click", readiness["reasons"])
        self.assertIn("action_not_enabled_by_policy", readiness["blocker_codes"])
        self.assertEqual(_check_status(readiness, "permission_profile"), "blocked")

    def test_high_risk_label_blocks_otherwise_ready_click_contract(self) -> None:
        readiness = evaluate_click_readiness(
            _click_contract(status="approved_for_execution", target_label="Delete account"),
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
            screen=_screen(),
            now=TEST_NOW,
        )

        self.assertIs(readiness["ready"], False)
        self.assertEqual(readiness["status"], "blocked")
        self.assertEqual(readiness["risk"], "high")
        self.assertEqual(readiness["reasons"], ["high-risk target label"])
        self.assertEqual(readiness["blocker_codes"], ["high_risk_requires_approval"])
        self.assertEqual(_check_status(readiness, "target_label_risk"), "blocked")

    def test_chinese_high_risk_label_blocks_click_contract(self) -> None:
        readiness = evaluate_click_readiness(
            _click_contract(status="approved_for_execution", target_label="确认支付"),
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
            screen=_screen(),
            now=TEST_NOW,
        )

        self.assertIs(readiness["ready"], False)
        self.assertIn("high-risk target label", readiness["reasons"])
        self.assertIn("high_risk_requires_approval", readiness["blocker_codes"])

    def test_safety_blocked_prevents_readiness(self) -> None:
        readiness = evaluate_click_readiness(
            _click_contract(status="approved_for_execution", target_label="Search"),
            {"decision": "blocked", "risk": "high"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
            screen=_screen(),
            now=TEST_NOW,
        )

        self.assertIs(readiness["ready"], False)
        self.assertIn("safety decision blocked", readiness["reasons"])
        self.assertIn("safety_decision_blocked", readiness["blocker_codes"])

    def test_invalid_geometry_prevents_readiness(self) -> None:
        contract = _click_contract(status="approved_for_execution")
        contract["bbox"] = {"x": 1, "y": 2, "width": 0, "height": 4}
        contract["center"] = {"x": "nan", "y": 4}

        readiness = evaluate_click_readiness(
            contract,
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
            screen=_screen(),
            now=TEST_NOW,
        )

        self.assertIs(readiness["ready"], False)
        self.assertIn("malformed bbox", readiness["reasons"])
        self.assertIn("invalid center", readiness["reasons"])
        self.assertIn("invalid_bbox", readiness["blocker_codes"])
        self.assertIn("missing_center", readiness["blocker_codes"])
        self.assertEqual(_check_status(readiness, "bbox_shape"), "blocked")
        self.assertEqual(_check_status(readiness, "center_shape"), "blocked")

    def test_missing_bbox_prevents_readiness(self) -> None:
        contract = _click_contract(status="approved_for_execution")
        del contract["bbox"]

        readiness = evaluate_click_readiness(
            contract,
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
            screen=_screen(),
            now=TEST_NOW,
        )

        self.assertIs(readiness["ready"], False)
        self.assertIn("missing bbox", readiness["reasons"])
        self.assertIn("missing_bbox", readiness["blocker_codes"])
        self.assertEqual(_check_status(readiness, "bbox_present"), "blocked")

    def test_malformed_bbox_prevents_readiness(self) -> None:
        contract = _click_contract(status="approved_for_execution")
        contract["bbox"] = {"x": 1, "y": 2, "width": "wide", "height": 4}

        readiness = evaluate_click_readiness(
            contract,
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
            screen=_screen(),
            now=TEST_NOW,
        )

        self.assertIs(readiness["ready"], False)
        self.assertIn("malformed bbox", readiness["reasons"])
        self.assertIn("invalid_bbox", readiness["blocker_codes"])
        self.assertEqual(_check_status(readiness, "bbox_shape"), "blocked")

    def test_out_of_bounds_bbox_prevents_readiness_when_screen_bounds_available(self) -> None:
        contract = _click_contract(status="approved_for_execution")
        contract["bbox"] = {"x": 95, "y": 20, "width": 80, "height": 24}

        readiness = evaluate_click_readiness(
            contract,
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
            screen=_screen(width=100, height=100),
            now=TEST_NOW,
        )

        self.assertIs(readiness["ready"], False)
        self.assertIn("bbox outside screen bounds", readiness["reasons"])
        self.assertIn("out_of_viewport", readiness["blocker_codes"])
        self.assertEqual(_check_status(readiness, "bbox_screen_bounds"), "blocked")

    def test_missing_center_prevents_readiness(self) -> None:
        contract = _click_contract(status="approved_for_execution")
        del contract["center"]

        readiness = evaluate_click_readiness(
            contract,
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
            screen=_screen(),
            now=TEST_NOW,
        )

        self.assertIs(readiness["ready"], False)
        self.assertIn("missing center", readiness["reasons"])
        self.assertIn("missing_center", readiness["blocker_codes"])

    def test_bbox_center_mismatch_prevents_readiness(self) -> None:
        contract = _click_contract(status="approved_for_execution")
        contract["center"] = {"x": 99, "y": 99}

        readiness = evaluate_click_readiness(
            contract,
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
            screen=_screen(),
            now=TEST_NOW,
        )

        self.assertIs(readiness["ready"], False)
        self.assertIn("center does not match bbox", readiness["reasons"])
        self.assertIn("bbox_center_mismatch", readiness["blocker_codes"])
        self.assertEqual(readiness["coordinate_debug"]["expected_center"], {"x": 50, "y": 32})

    def test_unknown_coordinate_space_and_dpi_block_readiness(self) -> None:
        readiness = evaluate_click_readiness(
            _click_contract(status="approved_for_execution"),
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
            screen={"width": 100, "height": 100},
            now=TEST_NOW,
        )

        self.assertIs(readiness["ready"], False)
        self.assertIn("coordinate_space_unknown", readiness["blocker_codes"])
        self.assertIn("dpi_uncertain", readiness["blocker_codes"])

    def test_missing_screen_blocks_coordinate_space(self) -> None:
        readiness = evaluate_click_readiness(
            _click_contract(status="approved_for_execution"),
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
            now=TEST_NOW,
        )

        self.assertIs(readiness["ready"], False)
        self.assertIn("coordinate_space_unknown", readiness["blocker_codes"])

    def test_stale_observation_prevents_readiness_when_timestamp_available(self) -> None:
        now = datetime(2026, 1, 1, 12, 0, 20, tzinfo=timezone.utc)
        stale_timestamp = (now - timedelta(seconds=20)).isoformat().replace("+00:00", "Z")

        readiness = evaluate_click_readiness(
            _click_contract(status="approved_for_execution"),
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
            observation_timestamp=stale_timestamp,
            now=now,
            max_observation_age_seconds=10,
            screen=_screen(),
        )

        self.assertIs(readiness["ready"], False)
        self.assertIn("stale observation", readiness["reasons"])
        self.assertIn("stale_observation", readiness["blocker_codes"])
        self.assertEqual(_check_status(readiness, "observation_freshness"), "blocked")

    def test_low_confidence_target_prevents_readiness(self) -> None:
        readiness = evaluate_click_readiness(
            _click_contract(status="approved_for_execution", target_confidence=0.2),
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
            screen=_screen(),
            now=TEST_NOW,
        )

        self.assertIs(readiness["ready"], False)
        self.assertIn("low-confidence target", readiness["reasons"])
        self.assertIn("low_confidence_target", readiness["blocker_codes"])

    def test_hidden_or_disabled_target_prevents_readiness(self) -> None:
        contract = _click_contract(
            status="approved_for_execution",
            target_confidence=0.0,
            target_source="ui_tree",
            target_risk_hint="unknown",
        )
        contract["target_visible"] = False
        contract["target_enabled"] = False

        readiness = evaluate_click_readiness(
            contract,
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
            screen=_screen(),
            now=TEST_NOW,
        )

        self.assertIs(readiness["ready"], False)
        self.assertIn("hidden or disabled target", readiness["reasons"])
        self.assertIn("hidden_or_disabled_target", readiness["blocker_codes"])
        self.assertIn("low_confidence_target", readiness["blocker_codes"])

    def test_ambiguous_target_prevents_readiness_when_candidates_are_supplied(self) -> None:
        contract = _click_contract(status="approved_for_execution")

        readiness = evaluate_click_readiness(
            contract,
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
            screen=_screen(),
            now=TEST_NOW,
            visible_elements=[
                _visible_element("element_0001", "Search", 0.92, x=10),
                _visible_element("element_0002", "Search", 0.9, x=120),
            ],
        )

        self.assertIs(readiness["ready"], False)
        self.assertIn("ambiguous target", readiness["reasons"])
        self.assertIn("ambiguous_target", readiness["blocker_codes"])

    def test_unknown_risk_target_prevents_readiness(self) -> None:
        readiness = evaluate_click_readiness(
            _click_contract(status="approved_for_execution", target_risk_hint="unknown"),
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
            screen=_screen(),
            now=TEST_NOW,
        )

        self.assertIs(readiness["ready"], False)
        self.assertIn("target risk is unknown", readiness["reasons"])
        self.assertIn("unknown_risk_target", readiness["blocker_codes"])

    def test_otherwise_ready_click_contract_can_be_marked_ready_by_policy_inputs(self) -> None:
        readiness = evaluate_click_readiness(
            _click_contract(status="approved_for_execution", target_label="Search"),
            {"decision": "allowed", "risk": "low"},
            {"enabled": True, "executable": True, "risk": "medium"},
            _profile_payload_with_click_allowed(),
            screen=_screen(),
            now=TEST_NOW,
        )

        self.assertIs(readiness["ready"], True)
        self.assertEqual(readiness["status"], "ready")
        self.assertEqual(readiness["reasons"], [])
        self.assertEqual(readiness["blocker_codes"], [])
        self.assertEqual(_check_status(readiness, "contract_status"), "passed")
        self.assertEqual(_check_status(readiness, "bbox_shape"), "passed")

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
        self.assertIn("bbox is inside declared viewport bounds", metadata["required_checks"])
        self.assertIn("coordinate_space_unknown", metadata["blocker_codes"])
        self.assertIn("发送", metadata["high_risk_labels"])
        self.assertGreater(metadata["max_observation_age_seconds"], 0)


def _click_contract(
    status: str,
    target_label: str = "Search",
    target_confidence: float = 0.92,
    target_source: str = "manual",
    target_risk_hint: str = "normal",
) -> dict[str, object]:
    return {
        "action_id": "action_0001",
        "source_proposal_id": "proposal_0001",
        "type": "click",
        "target_element_id": "element_0001",
        "target_label": target_label,
        "target_role": "button",
        "target_confidence": target_confidence,
        "target_source": target_source,
        "target_risk_hint": target_risk_hint,
        "target_timestamp": "2026-01-01T00:00:00Z",
        "bbox": {"x": 10, "y": 20, "width": 80, "height": 24},
        "center": {"x": 50, "y": 32},
        "status": status,
        "executed": False,
    }


def _screen(width: int = 200, height: int = 120) -> dict[str, object]:
    return {
        "width": width,
        "height": height,
        "coordinate_space": "screen",
        "dpi_scale": 1.0,
    }


def _visible_element(element_id: str, label: str, confidence: float, x: int) -> dict[str, object]:
    return {
        "id": element_id,
        "label": label,
        "text": label,
        "role": "button",
        "bbox": {"x": x, "y": 20, "width": 80, "height": 24},
        "center": {"x": x + 40, "y": 32},
        "confidence": confidence,
        "source": "manual",
        "risk_hint": "normal",
        "timestamp": "2026-01-01T00:00:00Z",
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


def _check_status(readiness: dict[str, object], name: str) -> str:
    checks = readiness.get("checks")
    if not isinstance(checks, list):
        raise AssertionError("readiness checks must be a list")

    for check in checks:
        if isinstance(check, dict) and check.get("name") == name:
            return str(check.get("status") or "")

    raise AssertionError(f"missing readiness check {name}")


def _check_code(readiness: dict[str, object], name: str) -> str:
    checks = readiness.get("checks")
    if not isinstance(checks, list):
        raise AssertionError("readiness checks must be a list")

    for check in checks:
        if isinstance(check, dict) and check.get("name") == name:
            return str(check.get("code") or "")

    raise AssertionError(f"missing readiness check {name}")


if __name__ == "__main__":
    unittest.main()
