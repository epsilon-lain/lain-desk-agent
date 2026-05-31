"""Minimal HTTP entrypoint for lain-desk-agent."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

from .actuation import ActuationBlockedError, execute_action_contract
from .action_contract import action_contract_from_proposal
from .ai_planner import (
    AI_PROPOSAL_MODE,
    AIPlannerError,
    ai_planner_runtime_status,
    build_ai_proposal_result_with_llm,
    openai_api_key_from_env,
    planner_mode_from_env,
)
from .capabilities import get_capabilities, get_capability
from .click_policy import (
    click_readiness_metadata,
    click_readiness_not_applicable,
    evaluate_click_readiness,
)
from .demo_scenarios import UnknownDemoScenarioError, run_demo_scenario
from .execution_policy import execution_policy_payload, execution_policy_summary
from .observation import DEFAULT_RUN_DIR, observe
from .permission_profile import get_permission_profile_payload
from .planner import propose
from .planner_context import build_planner_context
from .planner_evaluation import evaluate_demo_scenarios
from .resource_guard import DEFAULT_LIMITS, ResourceGuardError
from .safety import assess_proposal
from .understanding import understand
from .verification import verification_failed_result, verify_execution


UI_DIR = Path(__file__).resolve().parents[2] / "ui"
RUNS_DIR = Path.cwd() / "runs"
STATIC_ROUTES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
}
DEFAULT_EVENTS_LIMIT = 20
MAX_EVENTS_LIMIT = 100


class AgentRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path == "/observation":
            self._handle_observation()
            return

        if path == "/understanding":
            self._handle_understanding()
            return

        if path == "/proposal":
            self._handle_proposal()
            return

        if path == "/planner-context":
            self._handle_planner_context()
            return

        if path == "/planner-evaluation/demo":
            self._handle_planner_evaluation_demo()
            return

        if path == "/demo/scenario":
            self._handle_demo_scenario()
            return

        if path == "/events":
            self._handle_events()
            return

        if path == "/capabilities":
            self._handle_capabilities()
            return

        if path == "/permission-profile":
            self._handle_permission_profile()
            return

        if path == "/execution-policy":
            self._handle_execution_policy()
            return

        if path == "/click-readiness":
            self._handle_click_readiness()
            return

        if path == "/runtime/status":
            self._handle_runtime_status()
            return

        if path in STATIC_ROUTES:
            self._handle_static_file(path)
            return

        if path.startswith("/runs/"):
            self._handle_run_file(path)
            return

        if path == "/health":
            self._send_json({"status": "ok"})
            return

        self._send_json({"error": "not found"}, status=404)

    def do_POST(self) -> None:
        path = urlparse(self.path).path

        if path == "/approval":
            self._handle_approval()
            return

        if path == "/execute":
            self._handle_execute()
            return

        self._send_json({"error": "not found"}, status=404)

    def _handle_observation(self) -> None:
        try:
            observation = observe()
        except ResourceGuardError as exc:
            self._send_json(exc.to_payload(), status=507)
            return
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)
            return

        self._send_json(observation)

    def _handle_understanding(self) -> None:
        try:
            observation = observe()
            ui_state = understand(observation)
        except ResourceGuardError as exc:
            self._send_json(exc.to_payload(), status=507)
            return
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)
            return

        self._send_json(ui_state)

    def _handle_proposal(self) -> None:
        try:
            query = parse_qs(urlparse(self.path).query)
            observation = observe()
            ui_state = understand(observation)
            screen = observation.get("screen") or {}
            ui_state = {
                **ui_state,
                "screen": screen,
                "screenshot_path": screen.get("screenshot_path"),
            }
            task = _first_query_value(query, "task")
            planner_input = {
                **ui_state,
                "window_title": (observation.get("active_window") or {}).get("title"),
                "task": task,
            }
            proposal, planner_metadata, planner_trace = proposal_for_current_planner(
                planner_input,
                ui_state,
                screen,
                task,
            )
            action_contract = action_contract_from_proposal(proposal)
            if action_contract is not None:
                append_action_contract_event(
                    action_contract_event_from_contract(
                        action_contract,
                        task=planner_input["task"],
                    )
                )
            safety_decision = assess_proposal(proposal)
            click_readiness = click_readiness_for_response(
                action_contract,
                safety_decision,
                screen=screen,
                observation_timestamp=observation.get("timestamp"),
            )
        except ResourceGuardError as exc:
            self._send_json(exc.to_payload(), status=507)
            return
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)
            return

        self._send_json(
            {
                "ui_state": ui_state,
                "proposal": proposal,
                "action_contract": action_contract,
                "safety_decision": safety_decision,
                "click_readiness": click_readiness,
                "planner": planner_metadata,
                "planner_trace": planner_trace,
            }
        )

    def _handle_planner_context(self) -> None:
        try:
            query = parse_qs(urlparse(self.path).query)
            task = _first_query_value(query, "task")
            observation = observe()
            ui_state = understand(observation)
            screen = observation.get("screen") or {}
            ui_state = {
                **ui_state,
                "screen": {
                    "width": screen.get("width"),
                    "height": screen.get("height"),
                },
            }
            planner_context = build_planner_context(
                task,
                ui_state,
                runtime_status=runtime_status_payload(),
                recent_events=read_recent_events(limit=5),
            )
        except ResourceGuardError as exc:
            self._send_json(exc.to_payload(), status=507)
            return
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)
            return

        self._send_json({"planner_context": planner_context})

    def _handle_demo_scenario(self) -> None:
        try:
            query = parse_qs(urlparse(self.path).query)
            payload = run_demo_scenario(
                name=_first_query_value(query, "name") or "browser_search",
                task=_first_query_value(query, "task"),
            )
        except UnknownDemoScenarioError as exc:
            self._send_json({"error": str(exc)}, status=404)
            return
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)
            return

        self._send_json(payload)

    def _handle_planner_evaluation_demo(self) -> None:
        try:
            query = parse_qs(urlparse(self.path).query)
            scenario_name = _first_query_value(query, "name")
            task = _first_query_value(query, "task")
            payload = evaluate_demo_scenarios(
                names=[scenario_name] if scenario_name else None,
                task_overrides={scenario_name: task} if scenario_name and task else None,
            )
        except UnknownDemoScenarioError as exc:
            self._send_json({"error": str(exc)}, status=404)
            return
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)
            return

        self._send_json(payload)

    def _handle_approval(self) -> None:
        try:
            payload = self._read_json_body()
            event = approval_event_from_payload(payload)
            append_approval_event(event)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
            return
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)
            return

        self._send_json({"status": "recorded"})

    def _handle_execute(self) -> None:
        try:
            payload = self._read_json_body()
            action_contract = action_contract_from_execute_payload(payload)
            task = str(payload.get("task") or "")
            append_run_event(action_execution_requested_event(action_contract, task=task))
            result = execute_action_contract(action_contract)
            append_run_event(action_executed_event(action_contract, result, task=task))
            verification_result, post_observation_id = verify_wait_execution_after_observe(
                action_contract,
                result,
                task=task,
            )
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
            return
        except ActuationBlockedError as exc:
            append_run_event(action_blocked_event(action_contract, exc.reason, task=task))
            self._send_json(
                {
                    "status": "blocked",
                    "reason": exc.reason,
                    "executed": False,
                },
                status=403,
            )
            return
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)
            return

        self._send_json(
            {
                **result,
                "execution_result": result,
                "verification_result": verification_result,
                "post_observation_id": post_observation_id,
            }
        )

    def _handle_events(self) -> None:
        query = parse_qs(urlparse(self.path).query)
        limit = _event_limit_from_query(query)
        events = read_recent_events(limit=limit)
        self._send_json({"events": events})

    def _handle_capabilities(self) -> None:
        self._send_json({"capabilities": get_capabilities()})

    def _handle_permission_profile(self) -> None:
        self._send_json(get_permission_profile_payload())

    def _handle_execution_policy(self) -> None:
        self._send_json(execution_policy_payload())

    def _handle_click_readiness(self) -> None:
        self._send_json(click_readiness_metadata())

    def _handle_runtime_status(self) -> None:
        self._send_json(runtime_status_payload())

    def _handle_static_file(self, path: str) -> None:
        filename, content_type = STATIC_ROUTES[path]
        file_path = UI_DIR / filename

        try:
            body = file_path.read_bytes()
        except OSError:
            self._send_json({"error": "ui file not found"}, status=404)
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle_run_file(self, path: str) -> None:
        file_path = _resolve_run_file_path(path)
        if file_path is None:
            self._send_json({"error": "run file not found"}, status=404)
            return

        try:
            body = file_path.read_bytes()
        except OSError:
            self._send_json({"error": "run file not found"}, status=404)
            return

        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict[str, Any]:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("Invalid Content-Length.") from exc

        if content_length <= 0:
            raise ValueError("Request body is required.")

        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Request body must be valid JSON.") from exc

        if not isinstance(payload, dict):
            raise ValueError("Request body must be a JSON object.")

        return payload

    def log_message(self, format: str, *args: Any) -> None:
        return


def create_server(host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), AgentRequestHandler)


def _resolve_run_file_path(path: str) -> Path | None:
    if not path.endswith(".png"):
        return None

    relative_path = Path(unquote(path).lstrip("/"))
    file_path = (Path.cwd() / relative_path).resolve()
    runs_dir = RUNS_DIR.resolve()

    if not _is_relative_to(file_path, runs_dir):
        return None

    return file_path


def _is_relative_to(path: Path, parent: Path) -> bool:
    return path == parent or parent in path.parents


def approval_event_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    decision = str(payload.get("decision") or "")
    if decision not in {"approved", "rejected"}:
        raise ValueError("decision must be approved or rejected.")

    proposal = payload.get("proposal")
    safety_decision = payload.get("safety_decision")
    proposal_id = str(payload.get("proposal_id") or "")

    if not proposal_id:
        raise ValueError("proposal_id is required.")

    if not isinstance(proposal, dict):
        raise ValueError("proposal must be a JSON object.")

    if not isinstance(safety_decision, dict):
        raise ValueError("safety_decision must be a JSON object.")

    event = {
        "type": f"proposal.{decision}",
        "timestamp": _utc_timestamp(),
        "proposal_id": proposal_id,
        "proposal": proposal,
        "safety_decision": safety_decision,
    }

    task = payload.get("task")
    if isinstance(task, str) and task:
        event["task"] = task

    return event


def append_approval_event(
    event: dict[str, Any],
    run_dir: str | Path = DEFAULT_RUN_DIR,
) -> None:
    append_run_event(event, run_dir=run_dir)


def action_contract_event_from_contract(
    action_contract: dict[str, Any],
    task: str = "",
) -> dict[str, Any]:
    event = {
        "type": "action_contract.created",
        "timestamp": _utc_timestamp(),
        "action_id": str(action_contract.get("action_id") or ""),
        "source_proposal_id": str(action_contract.get("source_proposal_id") or ""),
        "action_contract_type": str(action_contract.get("type") or ""),
        "status": str(action_contract.get("status") or ""),
        "executed": bool(action_contract.get("executed")),
    }

    if task:
        event["task"] = task

    return event


def append_action_contract_event(
    event: dict[str, Any],
    run_dir: str | Path = DEFAULT_RUN_DIR,
) -> None:
    append_run_event(event, run_dir=run_dir)


def action_contract_from_execute_payload(payload: dict[str, Any]) -> dict[str, Any]:
    action_contract = payload.get("action_contract")

    if action_contract is None and "type" in payload:
        action_contract = payload

    if not isinstance(action_contract, dict):
        raise ValueError("action_contract is required.")

    return action_contract


def click_readiness_for_response(
    action_contract: dict[str, Any] | None,
    safety_decision: dict[str, Any] | None,
    screen: dict[str, Any] | None = None,
    observation_timestamp: str | None = None,
) -> dict[str, Any]:
    if not isinstance(action_contract, dict) or action_contract.get("type") != "click":
        return click_readiness_not_applicable()

    return evaluate_click_readiness(
        action_contract,
        safety_decision,
        get_capability("click"),
        get_permission_profile_payload(),
        screen=screen,
        observation_timestamp=observation_timestamp,
    )


def proposal_for_current_planner(
    planner_input: dict[str, Any],
    ui_state: dict[str, Any],
    screen: dict[str, Any],
    task: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    planner_mode = planner_mode_from_env()
    if planner_mode != AI_PROPOSAL_MODE:
        proposal = propose(planner_input)
        return (
            proposal,
            _planner_metadata(planner_mode, "rule_based"),
            _planner_trace(
                planner_mode=planner_mode,
                planner_source="rule_based",
                ai_planner_available=False,
                external_llm_call_attempted=False,
                external_llm_call_succeeded=False,
                validation_status="not_applicable",
                fallback_used=False,
                context_summary=_planner_trace_context_from_ui_state(ui_state),
                output_action_type=_proposal_action_type(proposal),
            ),
        )

    planner_context: dict[str, Any] | None = None
    external_llm_call_attempted = False
    ai_status = ai_planner_runtime_status()
    try:
        api_key = openai_api_key_from_env()
        if not api_key:
            raise AIPlannerError("OPENAI_API_KEY is required for ai_proposal mode.")

        planner_context = build_planner_context(
            task,
            {
                **ui_state,
                "screen": {
                    "width": screen.get("width"),
                    "height": screen.get("height"),
                },
            },
            runtime_status=runtime_status_payload(),
            recent_events=read_recent_events(limit=5),
        )
        external_llm_call_attempted = True
        ai_result = build_ai_proposal_result_with_llm(planner_context, api_key=api_key)
        proposal = ai_result["proposal"]
        validation = ai_result.get("validation") if isinstance(ai_result, dict) else {}
        return (
            proposal,
            _planner_metadata(planner_mode, "ai_proposal"),
            _planner_trace(
                planner_mode=planner_mode,
                planner_source="ai",
                ai_planner_available=bool(ai_status.get("ai_planner_available")),
                external_llm_call_attempted=True,
                external_llm_call_succeeded=True,
                validation_status=_validation_status(validation),
                fallback_used=False,
                context_summary=_planner_trace_context_from_context(planner_context),
                output_action_type=_proposal_action_type(proposal),
                validation_reason=_validation_reason(validation),
            ),
        )
    except AIPlannerError as exc:
        proposal = propose(planner_input)
        fallback_reason = str(exc)
        return (
            proposal,
            _planner_metadata(planner_mode, "rule_based", fallback_reason=fallback_reason),
            _planner_trace(
                planner_mode=planner_mode,
                planner_source="fallback",
                ai_planner_available=bool(ai_status.get("ai_planner_available")),
                external_llm_call_attempted=external_llm_call_attempted,
                external_llm_call_succeeded=False,
                validation_status="not_applicable",
                fallback_used=True,
                fallback_reason=fallback_reason,
                context_summary=_planner_trace_context(planner_context, ui_state),
                output_action_type=_proposal_action_type(proposal),
            ),
        )
    except Exception:
        proposal = propose(planner_input)
        fallback_reason = "AI planner failed; fell back to rule-based planner."
        return (
            proposal,
            _planner_metadata(
                planner_mode,
                "rule_based",
                fallback_reason=fallback_reason,
            ),
            _planner_trace(
                planner_mode=planner_mode,
                planner_source="fallback",
                ai_planner_available=bool(ai_status.get("ai_planner_available")),
                external_llm_call_attempted=external_llm_call_attempted,
                external_llm_call_succeeded=False,
                validation_status="not_applicable",
                fallback_used=True,
                fallback_reason=fallback_reason,
                context_summary=_planner_trace_context(planner_context, ui_state),
                output_action_type=_proposal_action_type(proposal),
            ),
        )


def _planner_metadata(
    planner_mode: str,
    source: str,
    fallback_reason: str = "",
) -> dict[str, Any]:
    metadata = {
        "planner_mode": planner_mode,
        "source": source,
        "fallback": bool(fallback_reason),
    }

    if fallback_reason:
        metadata["fallback_reason"] = fallback_reason

    return metadata


def _planner_trace(
    *,
    planner_mode: str,
    planner_source: str,
    ai_planner_available: bool,
    external_llm_call_attempted: bool,
    external_llm_call_succeeded: bool,
    validation_status: str,
    fallback_used: bool,
    context_summary: dict[str, Any],
    output_action_type: str,
    fallback_reason: str = "",
    validation_reason: str = "",
) -> dict[str, Any]:
    trace = {
        "planner_mode": planner_mode,
        "planner_source": planner_source,
        "ai_planner_available": ai_planner_available,
        "external_llm_call_attempted": external_llm_call_attempted,
        "external_llm_call_succeeded": external_llm_call_succeeded,
        "validation_status": validation_status,
        "fallback_used": fallback_used,
        "context_summary": context_summary,
        "output_action_type": output_action_type,
    }

    if fallback_reason:
        trace["fallback_reason"] = fallback_reason

    if validation_reason and validation_status == "rejected":
        trace["validation_reason"] = validation_reason

    return trace


def _planner_trace_context(
    planner_context: dict[str, Any] | None,
    ui_state: dict[str, Any],
) -> dict[str, Any]:
    if isinstance(planner_context, dict):
        return _planner_trace_context_from_context(planner_context)

    return _planner_trace_context_from_ui_state(ui_state)


def _planner_trace_context_from_context(planner_context: dict[str, Any]) -> dict[str, Any]:
    visible_elements = planner_context.get("visible_elements")
    recent_events = planner_context.get("recent_events")
    safety_runtime = planner_context.get("safety_runtime")

    if not isinstance(visible_elements, dict):
        visible_elements = {}
    if not isinstance(recent_events, dict):
        recent_events = {}
    if not isinstance(safety_runtime, dict):
        safety_runtime = {}

    return {
        "visible_element_count": _safe_trace_int(visible_elements.get("count"), 0),
        "recent_event_count": _safe_trace_int(recent_events.get("count"), 0),
        "desktop_control": bool(safety_runtime.get("desktop_control", False)),
        "executable_actions": _trace_string_list(safety_runtime.get("executable_actions")),
    }


def _planner_trace_context_from_ui_state(ui_state: dict[str, Any]) -> dict[str, Any]:
    visible_elements = ui_state.get("visible_elements")
    visible_element_count = len(visible_elements) if isinstance(visible_elements, list) else 0
    policy_summary = execution_policy_summary()

    return {
        "visible_element_count": visible_element_count,
        "recent_event_count": len(read_recent_events(limit=5)),
        "desktop_control": False,
        "executable_actions": _trace_string_list(policy_summary.get("executable_actions")),
    }


def _validation_status(validation: Any) -> str:
    if not isinstance(validation, dict):
        return "not_applicable"

    return "accepted" if validation.get("valid") else "rejected"


def _validation_reason(validation: Any) -> str:
    if not isinstance(validation, dict):
        return ""

    return str(validation.get("reason") or "")


def _proposal_action_type(proposal: dict[str, Any]) -> str:
    action = proposal.get("action")
    if not isinstance(action, dict):
        return ""

    return str(action.get("type") or "")


def _safe_trace_int(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _trace_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    return [str(item) for item in value]


def runtime_status_payload() -> dict[str, Any]:
    click_readiness = click_readiness_metadata()
    limits = DEFAULT_LIMITS

    return {
        "runtime": {
            "mode": "local",
            "desktop_control": False,
            "actuation": "wait_only",
            "verification": True,
        },
        "permission_profile": str(get_permission_profile_payload().get("profile") or "unknown"),
        "capabilities": get_capabilities(),
        "execution_policy": execution_policy_summary(),
        "click_readiness": {
            "enabled": bool(click_readiness.get("enabled")),
            "reason": str(click_readiness.get("reason") or ""),
        },
        "ai_planner": ai_planner_runtime_status(),
        "resource_guard": {
            "enabled": True,
            "max_observations_per_run": limits.max_observations_per_run,
            "max_run_size_mb": limits.max_run_size_mb,
            "min_free_disk_mb": limits.min_free_disk_mb,
        },
    }


def action_execution_requested_event(
    action_contract: dict[str, Any],
    task: str = "",
) -> dict[str, Any]:
    event = {
        "type": "action.execution_requested",
        "timestamp": _utc_timestamp(),
        **_action_event_fields(action_contract),
    }

    if task:
        event["task"] = task

    return event


def action_executed_event(
    action_contract: dict[str, Any],
    result: dict[str, Any],
    task: str = "",
) -> dict[str, Any]:
    event = {
        "type": "action.executed",
        "timestamp": _utc_timestamp(),
        **_action_event_fields(action_contract),
        "executed": bool(result.get("executed")),
        "result": result,
    }

    if task:
        event["task"] = task

    return event


def action_blocked_event(
    action_contract: dict[str, Any],
    reason: str,
    task: str = "",
) -> dict[str, Any]:
    event = {
        "type": "action.blocked",
        "timestamp": _utc_timestamp(),
        **_action_event_fields(action_contract),
        "reason": reason,
    }

    if task:
        event["task"] = task

    return event


def verify_wait_execution_after_observe(
    action_contract: dict[str, Any],
    result: dict[str, Any],
    task: str = "",
) -> tuple[dict[str, Any], str | None]:
    post_observation: dict[str, Any] | None = None

    try:
        post_observation = observe()
        verification_result = verify_execution(action_contract, result, post_observation)
    except Exception as exc:
        verification_result = verification_failed_result(str(exc))
        append_run_event(
            action_verification_failed_event(
                action_contract,
                result,
                verification_result,
                task=task,
            )
        )
        return verification_result, None

    post_observation_id = _observation_id(post_observation)

    if verification_result.get("status") == "verified":
        append_run_event(
            action_verified_event(
                action_contract,
                result,
                verification_result,
                post_observation_id=post_observation_id,
                task=task,
            )
        )
    else:
        append_run_event(
            action_verification_failed_event(
                action_contract,
                result,
                verification_result,
                post_observation_id=post_observation_id,
                task=task,
            )
        )

    return verification_result, post_observation_id


def action_verified_event(
    action_contract: dict[str, Any],
    result: dict[str, Any],
    verification_result: dict[str, Any],
    post_observation_id: str | None = None,
    task: str = "",
) -> dict[str, Any]:
    event = {
        "type": "action.verified",
        "timestamp": _utc_timestamp(),
        **_action_event_fields(action_contract),
        "executed": bool(result.get("executed")),
        "result": result,
        "verification_result": verification_result,
    }

    if post_observation_id:
        event["post_observation_id"] = post_observation_id

    if task:
        event["task"] = task

    return event


def action_verification_failed_event(
    action_contract: dict[str, Any],
    result: dict[str, Any],
    verification_result: dict[str, Any],
    post_observation_id: str | None = None,
    task: str = "",
) -> dict[str, Any]:
    event = {
        "type": "action.verification_failed",
        "timestamp": _utc_timestamp(),
        **_action_event_fields(action_contract),
        "executed": bool(result.get("executed")),
        "result": result,
        "verification_result": verification_result,
        "reason": str(verification_result.get("reason") or "Verification failed."),
    }

    if post_observation_id:
        event["post_observation_id"] = post_observation_id

    if task:
        event["task"] = task

    return event


def _observation_id(observation: dict[str, Any] | None) -> str | None:
    if not isinstance(observation, dict):
        return None

    observation_id = observation.get("observation_id")
    return str(observation_id) if observation_id else None


def _action_event_fields(action_contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "action_id": str(action_contract.get("action_id") or ""),
        "source_proposal_id": str(action_contract.get("source_proposal_id") or ""),
        "action_contract_type": str(action_contract.get("type") or ""),
        "status": str(action_contract.get("status") or ""),
        "executed": bool(action_contract.get("executed")),
    }


def append_run_event(
    event: dict[str, Any],
    run_dir: str | Path = DEFAULT_RUN_DIR,
) -> None:
    run_path = Path(run_dir)
    run_path.mkdir(parents=True, exist_ok=True)

    with (run_path / "events.jsonl").open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")


def read_recent_events(
    run_dir: str | Path = DEFAULT_RUN_DIR,
    limit: int = DEFAULT_EVENTS_LIMIT,
) -> list[dict[str, Any]]:
    events_path = Path(run_dir) / "events.jsonl"

    if not events_path.exists():
        return []

    safe_limit = _bounded_event_limit(limit)
    events: list[dict[str, Any]] = []

    try:
        lines = events_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []

    for line in reversed(lines):
        if len(events) >= safe_limit:
            break

        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        if isinstance(event, dict):
            events.append(event)

    return events


def _first_query_value(query: dict[str, list[str]], key: str) -> str:
    values = query.get(key) or []
    return values[0] if values else ""


def _event_limit_from_query(query: dict[str, list[str]]) -> int:
    value = _first_query_value(query, "limit")

    try:
        limit = int(value)
    except ValueError:
        return DEFAULT_EVENTS_LIMIT

    return _bounded_event_limit(limit)


def _bounded_event_limit(limit: int) -> int:
    return min(max(limit, 1), MAX_EVENTS_LIMIT)


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the lain-desk-agent local HTTP server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    server = create_server(args.host, args.port)
    print(f"lain-desk-agent listening on http://{args.host}:{args.port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
