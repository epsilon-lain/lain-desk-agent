"""Read-only planner evaluation harness for demo scenarios."""

from __future__ import annotations

from typing import Any

from .action_contract import action_contract_from_proposal
from .ai_planner import ALLOWED_PROPOSAL_ACTION_TYPES, build_ai_proposal_result_from_context
from .capabilities import get_capability
from .click_policy import click_readiness_not_applicable, evaluate_click_readiness
from .demo_scenarios import demo_scenario_input, demo_scenario_names
from .execution_policy import execution_policy_summary
from .permission_profile import get_permission_profile_payload
from .planner import propose
from .planner_context import build_planner_context
from .safety import assess_proposal


def evaluate_demo_scenarios(
    names: list[str] | None = None,
    task_overrides: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Evaluate rule-based and deterministic AI proposals on demo scenarios."""

    scenario_names = names if names is not None else demo_scenario_names()
    scenarios = [
        evaluate_demo_scenario(
            name,
            task=(task_overrides or {}).get(name, ""),
        )
        for name in scenario_names
    ]

    return {
        "report_type": "planner_evaluation",
        "source": "demo_scenarios",
        "external_llm_calls": False,
        "scenario_count": len(scenarios),
        "summary": _report_summary(scenarios),
        "scenarios": scenarios,
    }


def evaluate_demo_scenario(name: str, task: str = "") -> dict[str, Any]:
    """Evaluate one built-in fake UI state without observing the desktop."""

    scenario_input = demo_scenario_input(name, task=task)
    planner_context = build_planner_context(
        scenario_input["task"],
        scenario_input["ui_state"],
        recent_events=[],
    )
    rule_based_proposal = propose(_rule_based_input_from_context(planner_context))
    ai_result = build_ai_proposal_result_from_context(planner_context)
    ai_proposal = ai_result["proposal"]

    rule_based_result = _pipeline_result(rule_based_proposal)
    ai_result_payload = {
        **_pipeline_result(ai_proposal),
        "validation": ai_result.get("validation", {}),
    }
    differences = _compare_results(rule_based_result, ai_result_payload)
    notes = _scenario_notes(rule_based_result, ai_result_payload, planner_context, differences)

    return {
        "scenario": scenario_input["scenario"],
        "inputs": {
            "task": scenario_input["task"],
            "app_guess": planner_context.get("app_guess"),
            "state_guess": planner_context.get("state_guess"),
            "visible_elements": planner_context.get("visible_elements"),
            "grounding_hints": _grounding_hints(planner_context),
            "safety_runtime": planner_context.get("safety_runtime"),
        },
        "rule_based": rule_based_result,
        "ai_proposal": ai_result_payload,
        "differences": differences,
        "notes": notes,
    }


def _rule_based_input_from_context(planner_context: dict[str, Any]) -> dict[str, Any]:
    visible_elements = planner_context.get("visible_elements")
    visible_text = planner_context.get("visible_text")
    return {
        "ui_state_id": _source_ui_state_id(planner_context),
        "source_observation_id": str(planner_context.get("source_observation_id") or ""),
        "app_guess": planner_context.get("app_guess"),
        "state_guess": str(planner_context.get("state_guess") or "unknown"),
        "summary": str(planner_context.get("summary") or ""),
        "confidence": planner_context.get("confidence", 0.0),
        "visible_text": visible_text.get("preview", []) if isinstance(visible_text, dict) else [],
        "visible_elements": visible_elements.get("items", []) if isinstance(visible_elements, dict) else [],
        "task": str(planner_context.get("task") or ""),
    }


def _pipeline_result(proposal: dict[str, Any]) -> dict[str, Any]:
    safety_decision = assess_proposal(proposal)
    action_contract = action_contract_from_proposal(proposal)
    click_readiness = _click_readiness_for_contract(action_contract, safety_decision)

    return {
        "proposal": _compact_proposal(proposal),
        "proposal_type": _proposal_action_type(proposal),
        "safety_decision": safety_decision,
        "action_contract": _compact_action_contract(action_contract),
        "click_readiness": click_readiness,
        "execution_policy": execution_policy_summary(),
        "safe_read_only": _is_safe_read_only(proposal, safety_decision, action_contract),
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


def _compact_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    action = proposal.get("action") if isinstance(proposal, dict) else {}
    if not isinstance(action, dict):
        action = {}

    return {
        "proposal_id": str(proposal.get("proposal_id") or "") if isinstance(proposal, dict) else "",
        "source_ui_state_id": str(proposal.get("source_ui_state_id") or "") if isinstance(proposal, dict) else "",
        "action": {
            "type": str(action.get("type") or ""),
            "target": str(action.get("target") or ""),
            "target_element_id": str(action.get("target_element_id") or ""),
            "target_label": str(action.get("target_label") or ""),
            "target_bbox": action.get("target_bbox") if isinstance(action.get("target_bbox"), dict) else None,
            "risk": str(action.get("risk") or ""),
            "requires_approval": bool(action.get("requires_approval")),
            "reason": str(action.get("reason") or ""),
        },
    }


def _compact_action_contract(action_contract: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(action_contract, dict):
        return None

    return {
        "type": str(action_contract.get("type") or ""),
        "status": str(action_contract.get("status") or ""),
        "executed": bool(action_contract.get("executed")),
        "target_label": str(action_contract.get("target_label") or ""),
        "target_app": str(action_contract.get("target_app") or ""),
    }


def _compare_results(rule_based: dict[str, Any], ai_proposal: dict[str, Any]) -> dict[str, Any]:
    rule_action = _result_action(rule_based)
    ai_action = _result_action(ai_proposal)
    rule_type = str(rule_action.get("type") or "")
    ai_type = str(ai_action.get("type") or "")
    notes: list[str] = []

    if rule_type != ai_type:
        notes.append("proposal type differs")

    if _action_target(rule_action) != _action_target(ai_action):
        notes.append("proposal target differs")

    if not _ai_validation_accepted(ai_proposal):
        notes.append("AI output was rejected by validate_ai_proposal")

    if ai_type not in ALLOWED_PROPOSAL_ACTION_TYPES:
        notes.append("AI proposal type is outside the proposal-only allowlist")

    if not notes:
        notes.append("rule-based and ai_proposal agree on action type and target")

    return {
        "same_proposal_type": rule_type == ai_type,
        "same_target": _action_target(rule_action) == _action_target(ai_action),
        "rule_based_type": rule_type,
        "ai_proposal_type": ai_type,
        "rule_based_target": _action_target(rule_action),
        "ai_proposal_target": _action_target(ai_action),
        "notes": notes,
    }


def _scenario_notes(
    rule_based: dict[str, Any],
    ai_proposal: dict[str, Any],
    planner_context: dict[str, Any],
    differences: dict[str, Any],
) -> list[str]:
    notes = list(differences.get("notes", []))
    risk_hints = [
        hint
        for hint in _grounding_hints(planner_context)
        if hint.get("risk_hint") and hint.get("risk_hint") != "none"
    ]

    if risk_hints:
        notes.append("visible_elements include high-risk grounding hints")

    for label, result in [("rule_based", rule_based), ("ai_proposal", ai_proposal)]:
        contract = result.get("action_contract")
        if isinstance(contract, dict) and contract.get("status") == "preview_only":
            notes.append(f"{label} produced a preview-only {contract.get('type')} contract")

        readiness = result.get("click_readiness")
        if isinstance(readiness, dict) and readiness.get("status") == "blocked":
            notes.append(f"{label} click readiness is blocked")

    return _unique_notes(notes)


def _report_summary(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    differences_count = sum(
        1
        for scenario in scenarios
        if not scenario["differences"]["same_proposal_type"]
        or not scenario["differences"]["same_target"]
    )
    ai_rejections = sum(
        1
        for scenario in scenarios
        if not _ai_validation_accepted(scenario["ai_proposal"])
    )
    unsafe_ai_outputs = sum(
        1
        for scenario in scenarios
        if scenario["ai_proposal"]["proposal_type"] not in ALLOWED_PROPOSAL_ACTION_TYPES
    )
    all_safe = all(
        scenario["rule_based"]["safe_read_only"] and scenario["ai_proposal"]["safe_read_only"]
        for scenario in scenarios
    )

    return {
        "consistent_count": len(scenarios) - differences_count,
        "differences_count": differences_count,
        "ai_rejections": ai_rejections,
        "unsafe_ai_outputs": unsafe_ai_outputs,
        "all_safe_read_only": all_safe,
    }


def _grounding_hints(planner_context: dict[str, Any]) -> list[dict[str, Any]]:
    visible_elements = planner_context.get("visible_elements")
    items = visible_elements.get("items", []) if isinstance(visible_elements, dict) else []
    hints = []

    for item in items:
        if not isinstance(item, dict):
            continue

        role_hint = item.get("role_hint")
        risk_hint = item.get("risk_hint")
        if role_hint or risk_hint:
            hints.append(
                {
                    "id": str(item.get("id") or ""),
                    "label": str(item.get("label") or ""),
                    "role_hint": str(role_hint or ""),
                    "risk_hint": str(risk_hint or "none"),
                    "source": str(item.get("source") or "unknown"),
                }
            )

    return hints


def _is_safe_read_only(
    proposal: dict[str, Any],
    safety_decision: dict[str, Any],
    action_contract: dict[str, Any] | None,
) -> bool:
    action_type = _proposal_action_type(proposal)
    contract_safe = (
        action_contract is None
        or (
            action_contract.get("status") == "preview_only"
            and bool(action_contract.get("executed")) is False
        )
    )

    return (
        action_type in ALLOWED_PROPOSAL_ACTION_TYPES
        and safety_decision.get("decision") in {"allowed", "needs_approval"}
        and contract_safe
    )


def _result_action(result: dict[str, Any]) -> dict[str, Any]:
    proposal = result.get("proposal")
    if not isinstance(proposal, dict):
        return {}

    action = proposal.get("action")
    return action if isinstance(action, dict) else {}


def _proposal_action_type(proposal: dict[str, Any]) -> str:
    action = proposal.get("action") if isinstance(proposal, dict) else None
    if not isinstance(action, dict):
        return ""

    return str(action.get("type") or "")


def _action_target(action: dict[str, Any]) -> str:
    return str(action.get("target_element_id") or action.get("target") or "")


def _ai_validation_accepted(result: dict[str, Any]) -> bool:
    validation = result.get("validation")
    return isinstance(validation, dict) and bool(validation.get("valid"))


def _source_ui_state_id(planner_context: dict[str, Any]) -> str:
    source_observation_id = str(planner_context.get("source_observation_id") or "")
    if source_observation_id.startswith("obs_"):
        return f"state_{source_observation_id.removeprefix('obs_')}"

    if source_observation_id:
        return f"state_{source_observation_id}"

    return "state_planner_context"


def _unique_notes(notes: list[str]) -> list[str]:
    unique: list[str] = []
    for note in notes:
        if note and note not in unique:
            unique.append(note)

    return unique
