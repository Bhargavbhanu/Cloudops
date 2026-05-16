# Right LLM

Right LLM is an Autonomous LLM Cost Optimization and AI FinOps Platform. It sits between enterprise applications and LLM providers as a provider-agnostic optimization layer for routing, semantic caching, token reduction, budget governance, migration analysis, forecasting, observability, and autonomous optimization actions.

Live GitHub Pages dashboard: 
https://bhargavbhanu.github.io/Cloudops/

The repository contains a working backend core, local API server, static enterprise dashboard, Next.js 15 production console scaffold, tests, and cloud deployment assets.

## What Is Implemented

- AI gateway middleware with request normalization, policy enforcement, routing, token accounting, cost estimation, response normalization, trace metadata, and deterministic provider simulation.
- Semantic cache with L1 exact matching, L2 similarity matching, TTLs, trust scores, invalidation events, and cache analytics.
- Intelligent routing across OpenAI, Anthropic, Google Gemini, Groq, TogetherAI, Azure OpenAI, AWS Bedrock, and Ollama/local models.
- Prompt and token optimization with compression, context pruning hooks, fingerprinting, token prediction, and token budget enforcement.
- AI model advisor with output token prediction, model comparison, cost-quality ranking, latency estimates, confidence intervals, and monthly savings estimates.
- Migration simulator with cost reduction, latency delta, quality degradation, hallucination risk, JSON compatibility, and confidence score.
- Budget governance and policy engine with RBAC restrictions, premium model limits, unsafe prompt blocking, budget pressure actions, and runaway protection.
- Autonomous action engine for model downgrades, prompt compression, semantic cache activation, failover arming, and budget controls.
- Forecasting and analytics engine for usage summaries, provider/model distribution, SLA compliance, projected spend, savings forecasts, and recommendations.
- Enterprise dashboard at `web/index.html` and a Next.js 15/Tailwind/Recharts/Framer Motion scaffold in `frontend/`.
- Docker, docker-compose, Kubernetes, Helm, Terraform, and GitHub Actions CI artifacts.

## Architecture

```text
Enterprise Apps
  -> Right LLM Gateway
  -> Policy + Token Optimization
  -> Routing Decision Engine
  -> Semantic Cache
  -> Provider Adapter Layer
  -> LLM Providers
  -> Observability, Forecasting, Advisor, Governance, Autonomous Actions
```

Core Python modules live in `rightllm/`:

| Component | Module |
| --- | --- |
| Gateway orchestration | `rightllm.gateway` |
| Provider and model catalog | `rightllm.catalog` |
| Semantic cache | `rightllm.cache` |
| Routing engine | `rightllm.routing` |
| Token optimization | `rightllm.optimization` |
| Policy and governance | `rightllm.governance` |
| Usage analytics and forecasting | `rightllm.analytics` |
| Model advisor | `rightllm.advisor` |
| Migration simulator | `rightllm.migration` |
| REST/WebSocket API | `rightllm.api` |

## Local Quick Start

Run tests:

```powershell
python -m unittest discover -s tests
```

Start the standard-library API server:

```powershell
python -m rightllm.api --port 8080
```

Call the gateway:

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8080/gateway/chat `
  -ContentType "application/json" `
  -Body '{"prompt":"Classify this support ticket as billing or bug.","task_category":"classification"}'
```

Open the static dashboard:

```powershell
cd web
python -m http.server 8090 --bind 127.0.0.1
```

Then visit `http://127.0.0.1:8090`.

## Production Runtime

Install full production dependencies:

```powershell
python -m pip install -r requirements.txt
uvicorn rightllm.api:app --host 0.0.0.0 --port 8080
```

Start local infrastructure:

```powershell
docker compose up --build
```

Deploy primitives:

- Kubernetes manifests: `k8s/`
- Helm chart: `helm/right-llm/`
- AWS EKS baseline: `terraform/`
- CI: `.github/workflows/ci.yml`

## API Surface

- `POST /gateway/chat`
- `GET /analytics/usage`
- `POST /routing/decision`
- `POST /cache/search`
- `POST /advisor/recommend`
- `POST /migration/simulate`
- `GET /budgets/status`
- `GET /forecast/predict`
- `GET /actions/history`
- `POST /policies/enforce`
- `WS /ws/metrics` when running with FastAPI

## Database Design

The production schema should persist:

- `organizations`, `users`, `teams`, `projects`, `agents`
- `requests`, `responses`, `token_usage`
- `providers`, `models`, `routing_decisions`
- `cache_entries`, `optimization_actions`, `recommendations`
- `migration_reports`, `forecast_reports`, `budget_policies`, `audit_logs`

The current implementation keeps metrics in memory for deterministic local execution. The Docker and dependency scaffolding is ready for PostgreSQL, Redis, Qdrant, Celery, OpenTelemetry, Prometheus, and Grafana integration.

## Notes

Provider calls are simulated by default so the platform can be tested without API keys. The provider adapter boundary is intentionally isolated in `rightllm.gateway`; production deployments should replace `_simulate_provider_response` with LiteLLM calls plus encrypted tenant-scoped provider credentials.
