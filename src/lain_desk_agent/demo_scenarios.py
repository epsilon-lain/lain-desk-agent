"""Safe demo scenarios that bypass desktop observation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .action_contract import action_contract_from_proposal
from .capabilities import get_capability
from .click_policy import click_readiness_not_applicable, evaluate_click_readiness
from .permission_profile import get_permission_profile_payload
from .planner import propose
from .safety import assess_proposal


DEFAULT_DEMO_SCENARIO = "browser_search"
DEMO_TIMESTAMP = "2026-01-01T00:00:00Z"
DEMO_SCREEN = {"width": 1440, "height": 900}


class UnknownDemoScenarioError(ValueError):
    """Raised when a requested built-in demo scenario does not exist."""


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
    ui_state["task"] = effective_task

    return {
        "scenario": scenario_name,
        "task": effective_task,
        "ui_state": ui_state,
    }


def run_demo_scenario(name: str = DEFAULT_DEMO_SCENARIO, task: str = "") -> dict[str, Any]:
    scenario_input = demo_scenario_input(name, task=task)
    scenario_name = scenario_input["scenario"]
    effective_task = scenario_input["task"]
    ui_state = scenario_input["ui_state"]

    proposal = propose(ui_state)
    safety_decision = assess_proposal(proposal)
    action_contract = action_contract_from_proposal(proposal)
    click_readiness = _click_readiness_for_contract(action_contract, safety_decision)

    return {
        "scenario": scenario_name,
        "task": effective_task,
        "ui_state": ui_state,
        "proposal": proposal,
        "safety_decision": safety_decision,
        "action_contract": action_contract,
        "click_readiness": click_readiness,
    }


def _click_readiness_for_contract(
    action_contract: dict[str, Any] | None,
    safety_decision: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(action_contract, dict) or action_contract.get("type") != "click":
        return click_readiness_not_applicable()

    return evaluate_click_readiness(
        action_contract,
        safety_decision,
        get_capability("click"),
        get_permission_profile_payload(),
        screen=action_contract.get("screen"),
        observation_timestamp=action_contract.get("observation_timestamp"),
    )
