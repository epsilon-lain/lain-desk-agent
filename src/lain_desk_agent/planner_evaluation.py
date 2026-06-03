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
        "report_notes": [
            "risk_hint is a read-only label-level hint; it does not replace Safety Gate or Click Readiness.",
            "preview-only click contracts do not make click executable.",
            "switch_app preview contracts do not make app switching executable.",
        ],
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
    observation = _scenario_observation_record(
        scenario_input["scenario"],
        scenario_input["task"],
        planner_context,
        rule_based_result,
        ai_result_payload,
        differences,
        notes,
    )

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
        "observation": observation,
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
        screen=action_contract.get("screen"),
        observation_timestamp=action_contract.get("observation_timestamp"),
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

    status = str(action_contract.get("status") or "")
    return {
        "type": str(action_contract.get("type") or ""),
        "status": status,
        "preview_only": status == "preview_only",
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
    risk_hints = _high_risk_grounding_hints(planner_context)

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
    scenarios_with_risk_hints = [
        scenario["scenario"]
        for scenario in scenarios
        if _scenario_observation(scenario).get("risk_hints")
    ]
    scenarios_with_preview_clicks = [
        scenario["scenario"]
        for scenario in scenarios
        if _scenario_has_preview_contract(scenario, "click")
    ]
    scenarios_with_switch_app_previews = [
        scenario["scenario"]
        for scenario in scenarios
        if _scenario_has_preview_contract(scenario, "switch_app")
    ]
    scenarios_with_blocked_click_readiness = [
        scenario["scenario"]
        for scenario in scenarios
        if _scenario_has_blocked_click_readiness(scenario)
    ]

    return {
        "total_scenario_count": len(scenarios),
        "consistent_scenario_count": len(scenarios) - differences_count,
        "difference_count": differences_count,
        "unsafe_ai_output_count": unsafe_ai_outputs,
        "ai_rejection_count": ai_rejections,
        "scenarios_with_risk_hints": scenarios_with_risk_hints,
        "scenarios_with_preview_only_click_contracts": scenarios_with_preview_clicks,
        "scenarios_with_switch_app_preview_contracts": scenarios_with_switch_app_previews,
        "scenarios_with_blocked_click_readiness": scenarios_with_blocked_click_readiness,
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

        role = item.get("role")
        risk_hint = item.get("risk_hint")
        if role or risk_hint:
            hints.append(
                {
                    "id": str(item.get("id") or ""),
                    "label": str(item.get("label") or ""),
                    "role": str(role or ""),
                    "risk_hint": str(risk_hint or "unknown"),
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


def _scenario_observation_record(
    scenario_name: str,
    task: str,
    planner_context: dict[str, Any],
    rule_based: dict[str, Any],
    ai_proposal: dict[str, Any],
    differences: dict[str, Any],
    notes: list[str],
) -> dict[str, Any]:
    """Return a compact strategy-tuning observation for one scenario."""

    risk_hints = _high_risk_grounding_hints(planner_context)

    return {
        "scenario": scenario_name,
        "task": task,
        "element_count": _visible_element_count(planner_context),
        "risk_hints": risk_hints,
        "rule_based": _observation_proposal_summary(rule_based),
        "ai_proposal": _observation_proposal_summary(ai_proposal),
        "agreement": {
            "proposal_type": bool(differences.get("same_proposal_type")),
            "target": bool(differences.get("same_target")),
            "overall": bool(differences.get("same_proposal_type"))
            and bool(differences.get("same_target")),
        },
        "safety_status": {
            "rule_based": _observation_safety_summary(rule_based),
            "ai_proposal": _observation_safety_summary(ai_proposal),
        },
        "action_contract": {
            "rule_based": _observation_contract_summary(rule_based),
            "ai_proposal": _observation_contract_summary(ai_proposal),
        },
        "click_readiness": {
            "rule_based": _observation_click_readiness_summary(rule_based),
            "ai_proposal": _observation_click_readiness_summary(ai_proposal),
        },
        "strategy_notes": notes,
    }


def _visible_element_count(planner_context: dict[str, Any]) -> int:
    visible_elements = planner_context.get("visible_elements")
    if not isinstance(visible_elements, dict):
        return 0

    count = visible_elements.get("count")
    return count if isinstance(count, int) else 0


def _observation_proposal_summary(result: dict[str, Any]) -> dict[str, Any]:
    action = _result_action(result)
    return {
        "proposal_type": str(result.get("proposal_type") or action.get("type") or ""),
        "target": _action_target(action),
        "target_label": str(action.get("target_label") or ""),
    }


def _observation_safety_summary(result: dict[str, Any]) -> dict[str, Any]:
    safety_decision = result.get("safety_decision")
    if not isinstance(safety_decision, dict):
        return {"decision": "unknown", "reason": ""}

    return {
        "decision": str(safety_decision.get("decision") or "unknown"),
        "reason": str(safety_decision.get("reason") or ""),
    }


def _observation_contract_summary(result: dict[str, Any]) -> dict[str, Any]:
    action_contract = result.get("action_contract")
    if not isinstance(action_contract, dict):
        return {
            "type": "",
            "status": "none",
            "preview_only": False,
            "executed": False,
        }

    status = str(action_contract.get("status") or "")
    return {
        "type": str(action_contract.get("type") or ""),
        "status": status,
        "preview_only": bool(action_contract.get("preview_only")) or status == "preview_only",
        "executed": bool(action_contract.get("executed")),
    }


def _high_risk_grounding_hints(planner_context: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        hint
        for hint in _grounding_hints(planner_context)
        if hint.get("risk_hint") == "high_risk"
    ]


def _observation_click_readiness_summary(result: dict[str, Any]) -> dict[str, Any]:
    click_readiness = result.get("click_readiness")
    if not isinstance(click_readiness, dict):
        return {
            "status": "not_present",
            "ready": False,
            "reasons": [],
        }

    reasons = click_readiness.get("reasons")
    return {
        "status": str(click_readiness.get("status") or "unknown"),
        "ready": bool(click_readiness.get("ready")),
        "reasons": [str(reason) for reason in reasons] if isinstance(reasons, list) else [],
    }


def _scenario_observation(scenario: dict[str, Any]) -> dict[str, Any]:
    observation = scenario.get("observation")
    return observation if isinstance(observation, dict) else {}


def _scenario_has_preview_contract(scenario: dict[str, Any], contract_type: str) -> bool:
    observation = _scenario_observation(scenario)
    contracts = observation.get("action_contract")
    if not isinstance(contracts, dict):
        return False

    return any(
        isinstance(contract, dict)
        and contract.get("type") == contract_type
        and contract.get("preview_only") is True
        and contract.get("executed") is False
        for contract in contracts.values()
    )


def _scenario_has_blocked_click_readiness(scenario: dict[str, Any]) -> bool:
    observation = _scenario_observation(scenario)
    readiness_by_planner = observation.get("click_readiness")
    if not isinstance(readiness_by_planner, dict):
        return False

    return any(
        isinstance(readiness, dict) and readiness.get("status") == "blocked"
        for readiness in readiness_by_planner.values()
    )


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
