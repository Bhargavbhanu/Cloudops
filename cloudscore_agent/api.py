from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .assistant import answer_question
from .pipeline import run_pipeline


def make_handler(data_path: str):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            profile = run_pipeline(data_path)
            if parsed.path == "/health":
                self._json({"status": "ok", "service": "cloudscore-agent"})
            elif parsed.path == "/profile":
                self._json(asdict(profile))
            elif parsed.path == "/ask":
                question = parse_qs(parsed.query).get("q", ["What should we focus on?"])[0]
                self._json(answer_question(profile, question))
            else:
                self._json(
                    {"error": "not_found", "routes": ["/health", "/profile", "/ask?q=..."]},
                    status=404,
                )

        def log_message(self, format, *args):
            return

        def _json(self, payload, status: int = 200):
            body = json.dumps(payload, indent=2, default=str).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the CloudScore agent API locally.")
    parser.add_argument("--data", required=True, help="Path to cloud usage JSON export")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), make_handler(args.data))
    print(f"CloudScore API listening on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
