"""Minimal HTTP entrypoint for lain-desk-agent."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .observation import DEFAULT_RUN_DIR, observe
from .planner import propose
from .safety import assess_proposal
from .understanding import understand


UI_DIR = Path(__file__).resolve().parents[2] / "ui"
STATIC_ROUTES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
}


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

        if path in STATIC_ROUTES:
            self._handle_static_file(path)
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

        self._send_json({"error": "not found"}, status=404)

    def _handle_observation(self) -> None:
        try:
            observation = observe()
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)
            return

        self._send_json(observation)

    def _handle_understanding(self) -> None:
        try:
            observation = observe()
            ui_state = understand(observation)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)
            return

        self._send_json(ui_state)

    def _handle_proposal(self) -> None:
        try:
            query = parse_qs(urlparse(self.path).query)
            observation = observe()
            ui_state = understand(observation)
            planner_input = {
                **ui_state,
                "window_title": (observation.get("active_window") or {}).get("title"),
                "task": _first_query_value(query, "task"),
            }
            proposal = propose(planner_input)
            safety_decision = assess_proposal(proposal)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)
            return

        self._send_json(
            {
                "ui_state": ui_state,
                "proposal": proposal,
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
    run_path = Path(run_dir)
    run_path.mkdir(parents=True, exist_ok=True)

    with (run_path / "events.jsonl").open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")


def _first_query_value(query: dict[str, list[str]], key: str) -> str:
    values = query.get(key) or []
    return values[0] if values else ""


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
