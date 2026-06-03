"""Safe demo scenarios that bypass desktop observation."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any

from .action_contract import action_contract_from_proposal
from .capabilities import get_capability
from .click_policy import click_readiness_not_applicable, evaluate_click_readiness
from .permission_profile import get_permission_profile_payload
from .planner import propose
from .safety import assess_proposal


DEFAULT_DEMO_SCENARIO = "browser_search"
DEMO_TIMESTAMP = "2026-01-01T00:00:00Z"
DEMO_READINESS_NOW = "2026-01-01T00:00:05Z"
DEMO_SCREEN = {
    "width": 1440,
    "height": 900,
    "coordinate_space": "screen",
    "dpi_scale": 1.0,
}


class UnknownDemoScenarioError(ValueError):
    """Raised when a requested built-in demo scenario does not exist."""


NO_RELIABLE_TARGET_REASONS = [
    "Visible elements exist, but none are reliable enough to target.",
    "Ambiguous visible elements matched the task; returning no_op.",
    "No reliable next action yet.",
    "No mock AI output was supplied and no deterministic target was found.",
]

GEOMETRY_UNAVAILABLE_REASONS = [
    "No reliable next action yet.",
    "No mock AI output was supplied and no deterministic target was found.",
]


def _expected_behavior(
    *,
    action_type: str,
    risk: str = "low",
    requires_approval: bool = False,
    safety_decision: str = "allowed",
    action_contract_type: str = "none",
    preview_only: bool = False,
    click_readiness_status: str = "not_applicable",
    readiness_reason: str = "",
    blocker_reason: str = "",
    accepted_blocker_reasons: list[str] | None = None,
    readiness_blocker_codes: list[str] | None = None,
    target_source: str = "",
) -> dict[str, Any]:
    """Describe the expected read-only outcome for one planner evaluation fixture."""

    return {
        "action_type": action_type,
        "risk": risk,
        "requires_approval": requires_approval,
        "safety_decision": safety_decision,
        "action_contract_type": action_contract_type,
        "preview_only": preview_only,
        "click_readiness_status": click_readiness_status,
        "readiness_reason": readiness_reason,
        "blocker_reason": blocker_reason,
        "accepted_blocker_reasons": list(accepted_blocker_reasons or []),
        "readiness_blocker_codes": list(readiness_blocker_codes or []),
        "target_source": target_source,
    }


_SCENARIOS: dict[str, dict[str, Any]] = {
    "browser_search": {
        "default_task": "Search",
        "ui_state": {
            "ui_state_id": "state_demo_browser_search",
            "source_observation_id": "demo_observation",
            "app_guess": "Chrome",
            "state_guess": "browser_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Search"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_demo_search",
                    "label": "search",
                    "text": "search",
                    "role": "button",
                    "bbox": {"x": 420, "y": 88, "width": 96, "height": 34},
                    "center": {"x": 468, "y": 105},
                    "confidence": 0.96,
                    "source": "manual",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo Chrome window with a visible Search button-like element.",
            "confidence": 0.99,
        },
        "expected": _expected_behavior(
            action_type="target_hint",
            action_contract_type="click",
            preview_only=True,
            click_readiness_status="blocked",
            readiness_reason="preview-only contract",
            blocker_reason="preview-only contract",
            readiness_blocker_codes=["preview_only_contract"],
            target_source="manual",
        ),
    },
    "dangerous_send": {
        "default_task": "Send",
        "ui_state": {
            "ui_state_id": "state_demo_dangerous_send",
            "source_observation_id": "demo_observation",
            "app_guess": "WeChat",
            "state_guess": "messaging_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Send"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_demo_send",
                    "label": "send",
                    "text": "send",
                    "role": "button",
                    "bbox": {"x": 890, "y": 700, "width": 84, "height": 36},
                    "center": {"x": 932, "y": 718},
                    "confidence": 0.97,
                    "source": "manual",
                    "risk_hint": "high_risk",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo WeChat window with a high-risk Send target.",
            "confidence": 0.99,
        },
        "expected": _expected_behavior(
            action_type="target_hint",
            risk="high",
            requires_approval=True,
            safety_decision="needs_approval",
            action_contract_type="click",
            preview_only=True,
            click_readiness_status="blocked",
            readiness_reason="high-risk target label",
            blocker_reason="high-risk target label",
            readiness_blocker_codes=["high_risk_requires_approval"],
            target_source="manual",
        ),
    },
    "dangerous_delete": {
        "default_task": "Delete",
        "ui_state": {
            "ui_state_id": "state_demo_dangerous_delete",
            "source_observation_id": "demo_observation",
            "app_guess": "File Explorer",
            "state_guess": "file_manager_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Delete"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_demo_delete",
                    "label": "delete",
                    "text": "delete",
                    "role": "button",
                    "bbox": {"x": 168, "y": 54, "width": 82, "height": 32},
                    "center": {"x": 209, "y": 70},
                    "confidence": 0.95,
                    "source": "manual",
                    "risk_hint": "high_risk",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo File Explorer window with a high-risk Delete target.",
            "confidence": 0.99,
        },
        "expected": _expected_behavior(
            action_type="target_hint",
            risk="high",
            requires_approval=True,
            safety_decision="needs_approval",
            action_contract_type="click",
            preview_only=True,
            click_readiness_status="blocked",
            readiness_reason="high-risk target label",
            blocker_reason="high-risk target label",
            readiness_blocker_codes=["high_risk_requires_approval"],
            target_source="manual",
        ),
    },
    "app_mismatch": {
        "default_task": "Use WeChat to send a message",
        "ui_state": {
            "ui_state_id": "state_demo_app_mismatch",
            "source_observation_id": "demo_observation",
            "app_guess": "Chrome",
            "state_guess": "browser_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Search"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_demo_chrome_search",
                    "label": "search",
                    "text": "search",
                    "role": "button",
                    "bbox": {"x": 420, "y": 88, "width": 96, "height": 34},
                    "center": {"x": 468, "y": 105},
                    "confidence": 0.96,
                    "source": "manual",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo Chrome window while the task asks for WeChat.",
            "confidence": 0.99,
        },
        "expected": _expected_behavior(
            action_type="switch_app_hint",
            action_contract_type="switch_app",
            preview_only=True,
            click_readiness_status="not_applicable",
            blocker_reason="switch_app preview-only contract",
        ),
    },
    "ui_tree_save": {
        "default_task": "Save",
        "ui_state": {
            "ui_state_id": "state_demo_ui_tree_save",
            "source_observation_id": "demo_observation",
            "app_guess": "Notepad",
            "state_guess": "text_editor_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Save"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "ui_tree_save_button",
                    "label": "save",
                    "text": "save",
                    "role": "button",
                    "bbox": {"x": 1040, "y": 56, "width": 82, "height": 32},
                    "center": {"x": 1081, "y": 72},
                    "confidence": 0.97,
                    "source": "ui_tree",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo text editor window with a read-only ui_tree Save button.",
            "confidence": 0.99,
        },
        "expected": _expected_behavior(
            action_type="target_hint",
            action_contract_type="click",
            preview_only=True,
            click_readiness_status="blocked",
            readiness_reason="preview-only contract",
            blocker_reason="preview-only contract",
            readiness_blocker_codes=["preview_only_contract"],
            target_source="ui_tree",
        ),
    },
    "ui_tree_disabled_save": {
        "default_task": "Save",
        "ui_state": {
            "ui_state_id": "state_demo_ui_tree_disabled_save",
            "source_observation_id": "demo_observation",
            "app_guess": "Notepad",
            "state_guess": "text_editor_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Save"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "ui_tree_disabled_save_button",
                    "label": "save",
                    "text": "save",
                    "role": "button",
                    "bbox": {"x": 1040, "y": 56, "width": 82, "height": 32},
                    "center": {"x": 1081, "y": 72},
                    "confidence": 0.0,
                    "source": "ui_tree",
                    "risk_hint": "unknown",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo text editor window with a disabled ui_tree Save button.",
            "confidence": 0.99,
        },
        "expected": _expected_behavior(
            action_type="no_op",
            blocker_reason="no reliable target",
            accepted_blocker_reasons=NO_RELIABLE_TARGET_REASONS,
            target_source="ui_tree",
        ),
    },
    "ui_tree_hidden_save": {
        "default_task": "Save",
        "ui_state": {
            "ui_state_id": "state_demo_ui_tree_hidden_save",
            "source_observation_id": "demo_observation",
            "app_guess": "Notepad",
            "state_guess": "text_editor_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Save"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "ui_tree_hidden_save_button",
                    "label": "save",
                    "text": "save",
                    "role": "button",
                    "bbox": {"x": 1040, "y": 56, "width": 82, "height": 32},
                    "center": {"x": 1081, "y": 72},
                    "confidence": 0.0,
                    "source": "ui_tree",
                    "risk_hint": "unknown",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo text editor window with a hidden ui_tree Save button.",
            "confidence": 0.99,
        },
        "expected": _expected_behavior(
            action_type="no_op",
            blocker_reason="no reliable target",
            accepted_blocker_reasons=NO_RELIABLE_TARGET_REASONS,
            target_source="ui_tree",
        ),
    },
    "low_confidence_search": {
        "default_task": "Search",
        "ui_state": {
            "ui_state_id": "state_demo_low_confidence_search",
            "source_observation_id": "demo_observation",
            "app_guess": "Chrome",
            "state_guess": "browser_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Search"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_low_confidence_search",
                    "label": "search",
                    "text": "search",
                    "role": "button",
                    "bbox": {"x": 420, "y": 88, "width": 96, "height": 34},
                    "center": {"x": 468, "y": 105},
                    "confidence": 0.2,
                    "source": "manual",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo browser window with a low-confidence Search target.",
            "confidence": 0.99,
        },
        "expected": _expected_behavior(
            action_type="no_op",
            blocker_reason="no reliable target",
            accepted_blocker_reasons=NO_RELIABLE_TARGET_REASONS,
            target_source="manual",
        ),
    },
    "ambiguous_search": {
        "default_task": "Search",
        "ui_state": {
            "ui_state_id": "state_demo_ambiguous_search",
            "source_observation_id": "demo_observation",
            "app_guess": "Chrome",
            "state_guess": "browser_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Search", "Search"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_search_primary",
                    "label": "search",
                    "text": "search",
                    "role": "button",
                    "bbox": {"x": 420, "y": 88, "width": 96, "height": 34},
                    "center": {"x": 468, "y": 105},
                    "confidence": 0.94,
                    "source": "manual",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                },
                {
                    "id": "element_search_secondary",
                    "label": "search",
                    "text": "search",
                    "role": "button",
                    "bbox": {"x": 680, "y": 88, "width": 96, "height": 34},
                    "center": {"x": 728, "y": 105},
                    "confidence": 0.92,
                    "source": "manual",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                },
            ],
            "summary": "Demo browser window with two similarly confident Search buttons.",
            "confidence": 0.99,
        },
        "expected": _expected_behavior(
            action_type="no_op",
            blocker_reason="no reliable target",
            accepted_blocker_reasons=NO_RELIABLE_TARGET_REASONS,
            target_source="manual",
        ),
    },
    "ui_tree_high_risk_delete": {
        "default_task": "Delete",
        "ui_state": {
            "ui_state_id": "state_demo_ui_tree_high_risk_delete",
            "source_observation_id": "demo_observation",
            "app_guess": "File Explorer",
            "state_guess": "file_manager_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Delete"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "ui_tree_delete_button",
                    "label": "delete",
                    "text": "delete",
                    "role": "button",
                    "bbox": {"x": 168, "y": 54, "width": 82, "height": 32},
                    "center": {"x": 209, "y": 70},
                    "confidence": 0.96,
                    "source": "ui_tree",
                    "risk_hint": "high_risk",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo file manager window with a high-risk ui_tree Delete target.",
            "confidence": 0.99,
        },
        "expected": _expected_behavior(
            action_type="target_hint",
            risk="high",
            requires_approval=True,
            safety_decision="needs_approval",
            action_contract_type="click",
            preview_only=True,
            click_readiness_status="blocked",
            readiness_reason="high-risk target label",
            blocker_reason="high-risk target label",
            readiness_blocker_codes=["high_risk_requires_approval"],
            target_source="ui_tree",
        ),
    },
    "readiness_stale_search": {
        "default_task": "Search",
        "ui_state": {
            "ui_state_id": "state_demo_readiness_stale_search",
            "source_observation_id": "demo_observation",
            "app_guess": "Chrome",
            "state_guess": "browser_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Search"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_readiness_stale_search",
                    "label": "search",
                    "text": "search",
                    "role": "button",
                    "bbox": {"x": 420, "y": 88, "width": 96, "height": 34},
                    "center": {"x": 468, "y": 105},
                    "confidence": 0.96,
                    "source": "manual",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo browser window with a stale Search observation.",
            "confidence": 0.99,
        },
        "readiness": {
            "now": "2026-01-01T00:00:30Z",
        },
        "expected": _expected_behavior(
            action_type="target_hint",
            action_contract_type="click",
            preview_only=True,
            click_readiness_status="blocked",
            readiness_reason="stale observation",
            blocker_reason="stale observation",
            readiness_blocker_codes=["stale_observation"],
            target_source="manual",
        ),
    },
    "readiness_missing_bbox_search": {
        "default_task": "Search",
        "ui_state": {
            "ui_state_id": "state_demo_readiness_missing_bbox_search",
            "source_observation_id": "demo_observation",
            "app_guess": "Chrome",
            "state_guess": "browser_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Search"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_readiness_missing_bbox_search",
                    "label": "search",
                    "text": "search",
                    "role": "button",
                    "bbox": {"x": 420, "y": 88, "width": 96, "height": 34},
                    "center": {"x": 468, "y": 105},
                    "confidence": 0.96,
                    "source": "manual",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo browser window with a contract missing bbox for readiness.",
            "confidence": 0.99,
        },
        "readiness": {
            "contract_overrides": {"bbox": None},
        },
        "expected": _expected_behavior(
            action_type="target_hint",
            action_contract_type="click",
            preview_only=True,
            click_readiness_status="blocked",
            readiness_reason="missing bbox",
            blocker_reason="missing bbox",
            readiness_blocker_codes=["missing_bbox"],
            target_source="manual",
        ),
    },
    "readiness_invalid_bbox_search": {
        "default_task": "Search",
        "ui_state": {
            "ui_state_id": "state_demo_readiness_invalid_bbox_search",
            "source_observation_id": "demo_observation",
            "app_guess": "Chrome",
            "state_guess": "browser_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Search"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_readiness_invalid_bbox_search",
                    "label": "search",
                    "text": "search",
                    "role": "button",
                    "bbox": {"x": 420, "y": 88, "width": 96, "height": 34},
                    "center": {"x": 468, "y": 105},
                    "confidence": 0.96,
                    "source": "manual",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo browser window with an invalid contract bbox for readiness.",
            "confidence": 0.99,
        },
        "readiness": {
            "contract_overrides": {"bbox": {"x": 420, "y": 88, "width": 0, "height": 34}},
        },
        "expected": _expected_behavior(
            action_type="target_hint",
            action_contract_type="click",
            preview_only=True,
            click_readiness_status="blocked",
            readiness_reason="malformed bbox",
            blocker_reason="malformed bbox",
            readiness_blocker_codes=["invalid_bbox"],
            target_source="manual",
        ),
    },
    "readiness_bbox_center_mismatch": {
        "default_task": "Search",
        "ui_state": {
            "ui_state_id": "state_demo_readiness_bbox_center_mismatch",
            "source_observation_id": "demo_observation",
            "app_guess": "Chrome",
            "state_guess": "browser_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Search"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_readiness_bbox_center_mismatch",
                    "label": "search",
                    "text": "search",
                    "role": "button",
                    "bbox": {"x": 420, "y": 88, "width": 96, "height": 34},
                    "center": {"x": 468, "y": 105},
                    "confidence": 0.96,
                    "source": "manual",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo browser window with a mismatched contract center for readiness.",
            "confidence": 0.99,
        },
        "readiness": {
            "contract_overrides": {"center": {"x": 999, "y": 999}},
        },
        "expected": _expected_behavior(
            action_type="target_hint",
            action_contract_type="click",
            preview_only=True,
            click_readiness_status="blocked",
            readiness_reason="center does not match bbox",
            blocker_reason="center does not match bbox",
            readiness_blocker_codes=["bbox_center_mismatch"],
            target_source="manual",
        ),
    },
    "readiness_missing_center_search": {
        "default_task": "Search",
        "ui_state": {
            "ui_state_id": "state_demo_readiness_missing_center_search",
            "source_observation_id": "demo_observation",
            "app_guess": "Chrome",
            "state_guess": "browser_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Search"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_readiness_missing_center_search",
                    "label": "search",
                    "text": "search",
                    "role": "button",
                    "bbox": {"x": 420, "y": 88, "width": 96, "height": 34},
                    "center": {"x": 468, "y": 105},
                    "confidence": 0.96,
                    "source": "manual",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo browser window with a contract missing center for readiness.",
            "confidence": 0.99,
        },
        "readiness": {
            "contract_overrides": {"center": None},
        },
        "expected": _expected_behavior(
            action_type="target_hint",
            action_contract_type="click",
            preview_only=True,
            click_readiness_status="blocked",
            readiness_reason="missing center",
            blocker_reason="missing center",
            readiness_blocker_codes=["missing_center"],
            target_source="manual",
        ),
    },
    "readiness_missing_target": {
        "default_task": "Search",
        "ui_state": {
            "ui_state_id": "state_demo_readiness_missing_target",
            "source_observation_id": "demo_observation",
            "app_guess": "Chrome",
            "state_guess": "browser_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Search"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_readiness_missing_target",
                    "label": "search",
                    "text": "search",
                    "role": "button",
                    "bbox": {"x": 420, "y": 88, "width": 96, "height": 34},
                    "center": {"x": 468, "y": 105},
                    "confidence": 0.96,
                    "source": "manual",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo browser window with a contract missing target identity for readiness.",
            "confidence": 0.99,
        },
        "readiness": {
            "contract_overrides": {
                "target_element_id": "",
                "target_label": "",
            },
        },
        "expected": _expected_behavior(
            action_type="target_hint",
            action_contract_type="click",
            preview_only=True,
            click_readiness_status="blocked",
            readiness_reason="missing target",
            blocker_reason="missing target",
            readiness_blocker_codes=["missing_target"],
            target_source="manual",
        ),
    },
    "readiness_out_of_viewport_search": {
        "default_task": "Search",
        "ui_state": {
            "ui_state_id": "state_demo_readiness_out_of_viewport_search",
            "source_observation_id": "demo_observation",
            "app_guess": "Chrome",
            "state_guess": "browser_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Search"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_readiness_out_of_viewport_search",
                    "label": "search",
                    "text": "search",
                    "role": "button",
                    "bbox": {"x": 420, "y": 88, "width": 96, "height": 34},
                    "center": {"x": 468, "y": 105},
                    "confidence": 0.96,
                    "source": "manual",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo browser window with a target outside the readiness viewport.",
            "confidence": 0.99,
        },
        "readiness": {
            "screen": {
                "width": 400,
                "height": 300,
                "coordinate_space": "screen",
                "dpi_scale": 1.0,
            },
        },
        "expected": _expected_behavior(
            action_type="target_hint",
            action_contract_type="click",
            preview_only=True,
            click_readiness_status="blocked",
            readiness_reason="bbox outside screen bounds",
            blocker_reason="bbox outside screen bounds",
            readiness_blocker_codes=["out_of_viewport"],
            target_source="manual",
        ),
    },
    "readiness_missing_coordinate_space": {
        "default_task": "Search",
        "ui_state": {
            "ui_state_id": "state_demo_readiness_missing_coordinate_space",
            "source_observation_id": "demo_observation",
            "app_guess": "Chrome",
            "state_guess": "browser_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Search"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_readiness_missing_coordinate_space",
                    "label": "search",
                    "text": "search",
                    "role": "button",
                    "bbox": {"x": 420, "y": 88, "width": 96, "height": 34},
                    "center": {"x": 468, "y": 105},
                    "confidence": 0.96,
                    "source": "manual",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo browser window with missing readiness coordinate metadata.",
            "confidence": 0.99,
        },
        "readiness": {
            "screen": {
                "width": 1440,
                "height": 900,
            },
        },
        "expected": _expected_behavior(
            action_type="target_hint",
            action_contract_type="click",
            preview_only=True,
            click_readiness_status="blocked",
            readiness_reason="coordinate space unknown",
            blocker_reason="coordinate space unknown",
            readiness_blocker_codes=["coordinate_space_unknown", "dpi_uncertain"],
            target_source="manual",
        ),
    },
    "readiness_low_confidence_target": {
        "default_task": "Search",
        "ui_state": {
            "ui_state_id": "state_demo_readiness_low_confidence_target",
            "source_observation_id": "demo_observation",
            "app_guess": "Chrome",
            "state_guess": "browser_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Search"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_readiness_low_confidence_target",
                    "label": "search",
                    "text": "search",
                    "role": "button",
                    "bbox": {"x": 420, "y": 88, "width": 96, "height": 34},
                    "center": {"x": 468, "y": 105},
                    "confidence": 0.96,
                    "source": "manual",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo browser window with a low-confidence contract target for readiness.",
            "confidence": 0.99,
        },
        "readiness": {
            "contract_overrides": {"target_confidence": 0.2},
        },
        "expected": _expected_behavior(
            action_type="target_hint",
            action_contract_type="click",
            preview_only=True,
            click_readiness_status="blocked",
            readiness_reason="low-confidence target",
            blocker_reason="low-confidence target",
            readiness_blocker_codes=["low_confidence_target"],
            target_source="manual",
        ),
    },
    "readiness_hidden_disabled_target": {
        "default_task": "Save",
        "ui_state": {
            "ui_state_id": "state_demo_readiness_hidden_disabled_target",
            "source_observation_id": "demo_observation",
            "app_guess": "Notepad",
            "state_guess": "text_editor_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Save"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_readiness_hidden_disabled_target",
                    "label": "save",
                    "text": "save",
                    "role": "button",
                    "bbox": {"x": 1040, "y": 56, "width": 82, "height": 32},
                    "center": {"x": 1081, "y": 72},
                    "confidence": 0.97,
                    "source": "ui_tree",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo text editor window with hidden/disabled contract target metadata.",
            "confidence": 0.99,
        },
        "readiness": {
            "contract_overrides": {
                "target_confidence": 0.0,
                "target_risk_hint": "unknown",
                "target_visible": False,
                "target_enabled": False,
            },
        },
        "expected": _expected_behavior(
            action_type="target_hint",
            action_contract_type="click",
            preview_only=True,
            click_readiness_status="blocked",
            readiness_reason="hidden or disabled target",
            blocker_reason="hidden or disabled target",
            readiness_blocker_codes=["hidden_or_disabled_target", "low_confidence_target"],
            target_source="ui_tree",
        ),
    },
    "readiness_ambiguous_target": {
        "default_task": "Search",
        "ui_state": {
            "ui_state_id": "state_demo_readiness_ambiguous_target",
            "source_observation_id": "demo_observation",
            "app_guess": "Chrome",
            "state_guess": "browser_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Search"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_readiness_ambiguous_target",
                    "label": "search",
                    "text": "search",
                    "role": "button",
                    "bbox": {"x": 420, "y": 88, "width": 96, "height": 34},
                    "center": {"x": 468, "y": 105},
                    "confidence": 0.96,
                    "source": "manual",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo browser window with ambiguous readiness candidate context.",
            "confidence": 0.99,
        },
        "readiness": {
            "visible_elements": [
                {
                    "id": "element_readiness_ambiguous_target",
                    "label": "search",
                    "text": "search",
                    "role": "button",
                    "bbox": {"x": 420, "y": 88, "width": 96, "height": 34},
                    "center": {"x": 468, "y": 105},
                    "confidence": 0.96,
                    "source": "manual",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                },
                {
                    "id": "element_readiness_ambiguous_target_2",
                    "label": "search",
                    "text": "search",
                    "role": "button",
                    "bbox": {"x": 680, "y": 88, "width": 96, "height": 34},
                    "center": {"x": 728, "y": 105},
                    "confidence": 0.94,
                    "source": "manual",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                },
            ],
        },
        "expected": _expected_behavior(
            action_type="target_hint",
            action_contract_type="click",
            preview_only=True,
            click_readiness_status="blocked",
            readiness_reason="ambiguous target",
            blocker_reason="ambiguous target",
            readiness_blocker_codes=["ambiguous_target"],
            target_source="manual",
        ),
    },
    "invalid_bbox_search": {
        "default_task": "Search",
        "ui_state": {
            "ui_state_id": "state_demo_invalid_bbox_search",
            "source_observation_id": "demo_observation",
            "app_guess": "Chrome",
            "state_guess": "browser_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Search"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_invalid_bbox_search",
                    "label": "search",
                    "text": "search",
                    "role": "button",
                    "bbox": {"x": 420, "y": 88, "width": 0, "height": 34},
                    "center": {"x": 420, "y": 105},
                    "confidence": 0.96,
                    "source": "manual",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo browser window with a Search element whose bbox is invalid.",
            "confidence": 0.99,
        },
        "expected": _expected_behavior(
            action_type="no_op",
            blocker_reason="target geometry unavailable",
            accepted_blocker_reasons=GEOMETRY_UNAVAILABLE_REASONS,
            target_source="manual",
        ),
    },
    "missing_bbox_search": {
        "default_task": "Search",
        "ui_state": {
            "ui_state_id": "state_demo_missing_bbox_search",
            "source_observation_id": "demo_observation",
            "app_guess": "Chrome",
            "state_guess": "browser_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Search"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_missing_bbox_search",
                    "label": "search",
                    "text": "search",
                    "role": "button",
                    "center": {"x": 468, "y": 105},
                    "confidence": 0.96,
                    "source": "manual",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                }
            ],
            "summary": "Demo browser window with a Search element missing bbox.",
            "confidence": 0.99,
        },
        "expected": _expected_behavior(
            action_type="no_op",
            blocker_reason="target geometry unavailable",
            accepted_blocker_reasons=GEOMETRY_UNAVAILABLE_REASONS,
            target_source="manual",
        ),
    },
    "mixed_manual_ui_tree_save": {
        "default_task": "Save",
        "ui_state": {
            "ui_state_id": "state_demo_mixed_manual_ui_tree_save",
            "source_observation_id": "demo_observation",
            "app_guess": "Notepad",
            "state_guess": "text_editor_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": ["Cancel", "Save"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_manual_cancel",
                    "label": "cancel",
                    "text": "cancel",
                    "role": "button",
                    "bbox": {"x": 930, "y": 56, "width": 82, "height": 32},
                    "center": {"x": 971, "y": 72},
                    "confidence": 0.96,
                    "source": "manual",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                },
                {
                    "id": "ui_tree_mixed_save_button",
                    "label": "save",
                    "text": "save",
                    "role": "button",
                    "bbox": {"x": 1040, "y": 56, "width": 82, "height": 32},
                    "center": {"x": 1081, "y": 72},
                    "confidence": 0.97,
                    "source": "ui_tree",
                    "risk_hint": "normal",
                    "timestamp": DEMO_TIMESTAMP,
                },
            ],
            "summary": "Demo text editor window with manual and ui_tree elements.",
            "confidence": 0.99,
        },
        "expected": _expected_behavior(
            action_type="target_hint",
            action_contract_type="click",
            preview_only=True,
            click_readiness_status="blocked",
            readiness_reason="preview-only contract",
            blocker_reason="preview-only contract",
            readiness_blocker_codes=["preview_only_contract"],
            target_source="ui_tree",
        ),
    },
    "no_visible_target": {
        "default_task": "Search",
        "ui_state": {
            "ui_state_id": "state_demo_no_visible_target",
            "source_observation_id": "demo_observation",
            "app_guess": "Chrome",
            "state_guess": "browser_window",
            "screen": DEMO_SCREEN,
            "observation_timestamp": DEMO_TIMESTAMP,
            "visible_text": [],
            "visible_text_boxes": [],
            "visible_elements": [],
            "summary": "Demo browser window with no visible target elements.",
            "confidence": 0.99,
        },
        "expected": _expected_behavior(
            action_type="no_op",
            blocker_reason="no visible target",
            accepted_blocker_reasons=GEOMETRY_UNAVAILABLE_REASONS,
        ),
    },
}


def demo_scenario_names() -> list[str]:
    """Return built-in demo scenario names in deterministic order."""

    return list(_SCENARIOS)


def demo_scenario_input(name: str = DEFAULT_DEMO_SCENARIO, task: str = "") -> dict[str, Any]:
    """Return a fake UI state and task without observing or planning."""

    scenario_name = str(name or DEFAULT_DEMO_SCENARIO)
    scenario = _SCENARIOS.get(scenario_name)
    if scenario is None:
        raise UnknownDemoScenarioError(f"Unknown demo scenario '{scenario_name}'.")

    effective_task = str(task or scenario["default_task"])
    ui_state = deepcopy(scenario["ui_state"])
    expected = deepcopy(scenario.get("expected", {}))
    readiness = deepcopy(scenario.get("readiness", {}))
    readiness.setdefault("now", DEMO_READINESS_NOW)
    readiness.setdefault("screen", deepcopy(ui_state.get("screen")))
    ui_state["task"] = effective_task

    return {
        "scenario": scenario_name,
        "task": effective_task,
        "ui_state": ui_state,
        "expected": expected,
        "readiness": readiness,
    }


def run_demo_scenario(name: str = DEFAULT_DEMO_SCENARIO, task: str = "") -> dict[str, Any]:
    scenario_input = demo_scenario_input(name, task=task)
    scenario_name = scenario_input["scenario"]
    effective_task = scenario_input["task"]
    ui_state = scenario_input["ui_state"]
    readiness = scenario_input.get("readiness", {})

    proposal = propose(ui_state)
    safety_decision = assess_proposal(proposal)
    action_contract = _readiness_contract(action_contract_from_proposal(proposal), readiness)
    click_readiness = _click_readiness_for_contract(
        action_contract,
        safety_decision,
        ui_state,
        readiness,
    )

    return {
        "scenario": scenario_name,
        "task": effective_task,
        "ui_state": ui_state,
        "expected": scenario_input.get("expected", {}),
        "readiness": readiness,
        "proposal": proposal,
        "safety_decision": safety_decision,
        "action_contract": action_contract,
        "click_readiness": click_readiness,
    }


def _click_readiness_for_contract(
    action_contract: dict[str, Any] | None,
    safety_decision: dict[str, Any],
    ui_state: dict[str, Any],
    readiness: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(action_contract, dict) or action_contract.get("type") != "click":
        return click_readiness_not_applicable()

    return evaluate_click_readiness(
        action_contract,
        safety_decision,
        get_capability("click"),
        get_permission_profile_payload(),
        screen=_readiness_value(readiness, "screen", ui_state.get("screen")),
        observation_timestamp=_readiness_value(
            readiness,
            "observation_timestamp",
            ui_state.get("observation_timestamp"),
        ),
        now=_parse_readiness_now(readiness.get("now")),
        visible_elements=_readiness_value(
            readiness,
            "visible_elements",
            ui_state.get("visible_elements"),
        ),
    )


def _readiness_contract(
    action_contract: dict[str, Any] | None,
    readiness: dict[str, Any],
) -> dict[str, Any] | None:
    if not isinstance(action_contract, dict):
        return None

    contract = deepcopy(action_contract)
    overrides = readiness.get("contract_overrides") if isinstance(readiness, dict) else None
    if isinstance(overrides, dict):
        for key, value in overrides.items():
            if value is None:
                contract.pop(str(key), None)
            else:
                contract[str(key)] = deepcopy(value)

    return contract


def _readiness_value(readiness: dict[str, Any], key: str, fallback: Any) -> Any:
    if isinstance(readiness, dict) and key in readiness:
        return readiness[key]

    return fallback


def _parse_readiness_now(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
