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
            "visible_text": ["Search"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_demo_search",
                    "source": "demo",
                    "type": "button",
                    "label": "Search",
                    "bbox": {"x": 420, "y": 88, "width": 96, "height": 34},
                    "confidence": 0.96,
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
            "visible_text": ["Send"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_demo_send",
                    "source": "demo",
                    "type": "button",
                    "label": "Send",
                    "bbox": {"x": 890, "y": 700, "width": 84, "height": 36},
                    "confidence": 0.97,
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
            "visible_text": ["Delete"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_demo_delete",
                    "source": "demo",
                    "type": "button",
                    "label": "Delete",
                    "bbox": {"x": 168, "y": 54, "width": 82, "height": 32},
                    "confidence": 0.95,
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
            "visible_text": ["Search"],
            "visible_text_boxes": [],
            "visible_elements": [
                {
                    "id": "element_demo_chrome_search",
                    "source": "demo",
                    "type": "button",
                    "label": "Search",
                    "bbox": {"x": 420, "y": 88, "width": 96, "height": 34},
                    "confidence": 0.96,
                }
            ],
            "summary": "Demo Chrome window while the task asks for WeChat.",
            "confidence": 0.99,
        },
    },
}


def run_demo_scenario(name: str = DEFAULT_DEMO_SCENARIO, task: str = "") -> dict[str, Any]:
    scenario_name = str(name or DEFAULT_DEMO_SCENARIO)
    scenario = _SCENARIOS.get(scenario_name)
    if scenario is None:
        raise UnknownDemoScenarioError(f"Unknown demo scenario '{scenario_name}'.")

    effective_task = str(task or scenario["default_task"])
    ui_state = deepcopy(scenario["ui_state"])
    ui_state["task"] = effective_task

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
    )
