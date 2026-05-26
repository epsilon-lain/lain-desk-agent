"""Minimal HTTP entrypoint for lain-desk-agent."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .observation import observe


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

        if path in STATIC_ROUTES:
            self._handle_static_file(path)
            return

        if path == "/health":
            self._send_json({"status": "ok"})
            return

        self._send_json({"error": "not found"}, status=404)

    def _handle_observation(self) -> None:
        try:
            observation = observe()
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)
            return

        self._send_json(observation)

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

    def log_message(self, format: str, *args: Any) -> None:
        return


def create_server(host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), AgentRequestHandler)


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
