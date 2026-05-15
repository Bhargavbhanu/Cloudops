from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from .advisor import recommend_model
from .analytics import asdict_list
from .catalog import MODEL_CATALOG
from .gateway import RightLLMGateway
from .migration import simulate_migration
from .models import GatewayRequest, TenantContext

gateway = RightLLMGateway()


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return {k: _jsonable(v) for k, v in asdict(value).items()}
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def payload_to_request(payload: dict[str, Any]) -> GatewayRequest:
    tenant_payload = payload.get("tenant") or {}
    tenant = TenantContext(
        organization_id=tenant_payload.get("organization_id", "demo-enterprise"),
        team_id=tenant_payload.get("team_id", "platform"),
        project_id=tenant_payload.get("project_id", "ai-assistant"),
        user_id=tenant_payload.get("user_id", "demo-user"),
        role=tenant_payload.get("role", "member"),
        priority=tenant_payload.get("priority", "standard"),
        monthly_budget_usd=float(tenant_payload.get("monthly_budget_usd", 50000)),
        month_to_date_spend_usd=float(tenant_payload.get("month_to_date_spend_usd", 0)),
    )
    return GatewayRequest(
        prompt=str(payload.get("prompt", "Summarize the current AI spend posture.")),
        task_category=str(payload.get("task_category", "conversational_ai")),
        baseline_provider=str(payload.get("baseline_provider", "openai")),
        baseline_model=str(payload.get("baseline_model", "gpt-4o")),
        max_tokens=int(payload.get("max_tokens", 1024)),
        quality_requirement=float(payload.get("quality_requirement", 0.82)),
        latency_sla_ms=int(payload.get("latency_sla_ms", 2200)),
        stream=bool(payload.get("stream", False)),
        metadata=dict(payload.get("metadata") or {}),
        tenant=tenant,
    )


try:
    from fastapi import FastAPI, WebSocket

    app = FastAPI(title="Right LLM API", version="1.0.0")

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok", "service": "right-llm"}

    @app.post("/gateway/chat")
    async def gateway_chat(payload: dict) -> dict:
        return _jsonable(gateway.chat(payload_to_request(payload)))

    @app.get("/analytics/usage")
    async def analytics_usage() -> dict:
        return gateway.metrics.usage_summary()

    @app.post("/routing/decision")
    async def routing_decision(payload: dict) -> dict:
        request = payload_to_request(payload)
        return _jsonable(gateway.routing.decide(request, request.prompt))

    @app.post("/cache/search")
    async def cache_search(payload: dict) -> dict:
        decision, response = gateway.cache.search(str(payload.get("prompt", "")))
        return {"decision": _jsonable(decision), "response": response}

    @app.post("/advisor/recommend")
    async def advisor_recommend(payload: dict) -> dict:
        return recommend_model(**payload)

    @app.post("/migration/simulate")
    async def migration_simulate(payload: dict) -> dict:
        return simulate_migration(**payload)

    @app.get("/budgets/status")
    async def budgets_status() -> dict:
        summary = gateway.metrics.usage_summary()
        return {"status": "healthy", "spend_usd": summary["total_cost_usd"], "guardrails": ["quota", "throttle", "downgrade"]}

    @app.get("/forecast/predict")
    async def forecast_predict() -> dict:
        return gateway.metrics.forecast()

    @app.get("/actions/history")
    async def actions_history() -> dict:
        return {"actions": ["compress_prompts", "route_low_cost", "semantic_cache_write"]}

    @app.post("/policies/enforce")
    async def policies_enforce(payload: dict) -> dict:
        return _jsonable(gateway.policy.enforce(payload_to_request(payload)))

    @app.websocket("/ws/metrics")
    async def ws_metrics(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_json(gateway.metrics.usage_summary())
        await websocket.close()

except Exception:
    app = None


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._send({"status": "ok", "service": "right-llm"})
        elif parsed.path == "/analytics/usage":
            self._send(gateway.metrics.usage_summary())
        elif parsed.path == "/forecast/predict":
            self._send(gateway.metrics.forecast())
        elif parsed.path == "/actions/history":
            self._send({"actions": ["compress_prompts", "route_low_cost", "semantic_cache_write"]})
        elif parsed.path == "/models":
            self._send({"models": [_jsonable(model) for model in MODEL_CATALOG]})
        elif parsed.path == "/advisor/recommend":
            q = parse_qs(parsed.query)
            self._send(
                recommend_model(
                    prompt=q.get("prompt", ["Summarize usage"])[0],
                    task_category=q.get("task_category", ["summarization"])[0],
                    monthly_volume=int(q.get("monthly_volume", ["100000"])[0]),
                )
            )
        else:
            self._send({"error": "not_found"}, 404)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        parsed = urlparse(self.path)
        if parsed.path == "/gateway/chat":
            self._send(_jsonable(gateway.chat(payload_to_request(payload))))
        elif parsed.path == "/routing/decision":
            request = payload_to_request(payload)
            self._send(_jsonable(gateway.routing.decide(request, request.prompt)))
        elif parsed.path == "/cache/search":
            decision, response = gateway.cache.search(str(payload.get("prompt", "")))
            self._send({"decision": _jsonable(decision), "response": response})
        elif parsed.path == "/advisor/recommend":
            self._send(recommend_model(**payload))
        elif parsed.path == "/migration/simulate":
            self._send(simulate_migration(**payload))
        elif parsed.path == "/policies/enforce":
            self._send(_jsonable(gateway.policy.enforce(payload_to_request(payload))))
        else:
            self._send({"error": "not_found"}, 404)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(_jsonable(payload), indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Right LLM gateway API.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    print(f"Right LLM API listening on http://{args.host}:{args.port}")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
