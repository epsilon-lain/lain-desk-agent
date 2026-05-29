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
from .observation import DEFAULT_RUN_DIR, observe
from .planner import propose
from .resource_guard import ResourceGuardError
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

        if path == "/events":
            self._handle_events()
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
            planner_input = {
                **ui_state,
                "window_title": (observation.get("active_window") or {}).get("title"),
                "task": _first_query_value(query, "task"),
            }
            proposal = propose(planner_input)
            action_contract = action_contract_from_proposal(proposal)
            if action_contract is not None:
                append_action_contract_event(
                    action_contract_event_from_contract(
                        action_contract,
                        task=planner_input["task"],
                    )
                )
            safety_decision = assess_proposal(proposal)
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
            }
        )

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
