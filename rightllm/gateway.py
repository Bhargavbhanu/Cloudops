from __future__ import annotations

from datetime import datetime, timezone

from .actions import autonomous_actions
from .analytics import MetricsStore
from .cache import SemanticCache
from .catalog import get_model
from .governance import PolicyEngine
from .models import GatewayRequest, GatewayResponse, TokenUsage, UsageMetric
from .optimization import compress_prompt
from .routing import RoutingEngine
from .tokenization import estimate_tokens, predict_completion_tokens


class RightLLMGateway:
    def __init__(self) -> None:
        self.cache = SemanticCache()
        self.routing = RoutingEngine()
        self.policy = PolicyEngine()
        self.metrics = MetricsStore()

    def chat(self, request: GatewayRequest) -> GatewayResponse:
        policy = self.policy.enforce(request)
        if not policy.allowed:
            optimized_prompt = request.prompt
            routing = self.routing.decide(request, optimized_prompt)
            token_usage = TokenUsage(estimate_tokens(request.prompt), 0, estimate_tokens(request.prompt), 0.0)
            return GatewayResponse(
                request.request_id,
                "Request blocked by enterprise policy.",
                routing.provider,
                routing.model,
                token_usage,
                0,
                self.cache.search(request.prompt)[0],
                routing,
                policy,
                0.0,
                0.0,
                policy.actions,
                {"blocked": True},
            )

        optimized_prompt, tokens_saved = compress_prompt(request.prompt)
        cache_decision, cached = self.cache.search(optimized_prompt)
        routing = self.routing.decide(request, optimized_prompt)
        model = get_model(routing.provider, routing.model)
        prompt_tokens = estimate_tokens(optimized_prompt)
        completion_tokens = predict_completion_tokens(
            optimized_prompt, request.task_category, request.max_tokens
        )
        if cached:
            content = cached
            completion_tokens = estimate_tokens(content)
            latency_ms = 24
            cost_usd = 0.0
            quality_score = min(model.quality_score, cache_decision.trust_score)
        else:
            content = _simulate_provider_response(request, routing.provider, routing.model)
            latency_ms = model.p95_latency_ms
            cost_usd = routing.estimated_cost_usd
            quality_score = model.quality_score
            self.cache.write(optimized_prompt, content, quality_score, tokens_saved)

        token_usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            cost_usd=round(cost_usd, 6),
        )
        actions = autonomous_actions(request, policy, routing, cache_decision.hit, tokens_saved)
        hallucination_score = round(max(0.02, 0.18 - quality_score * 0.12), 3)
        response = GatewayResponse(
            request_id=request.request_id,
            content=content,
            provider=routing.provider,
            model=routing.model,
            token_usage=token_usage,
            latency_ms=latency_ms,
            cache=cache_decision,
            routing=routing,
            policy=policy,
            quality_score=round(quality_score, 3),
            hallucination_score=hallucination_score,
            optimization_actions=actions,
            trace={
                "optimized_prompt_tokens_saved": tokens_saved,
                "baseline": f"{request.baseline_provider}/{request.baseline_model}",
                "tenant": request.tenant.organization_id,
            },
        )
        self.metrics.append(
            UsageMetric(
                timestamp=datetime.now(timezone.utc),
                organization_id=request.tenant.organization_id,
                team_id=request.tenant.team_id,
                project_id=request.tenant.project_id,
                user_id=request.tenant.user_id,
                provider=response.provider,
                model=response.model,
                task_category=request.task_category,
                prompt_tokens=token_usage.prompt_tokens,
                completion_tokens=token_usage.completion_tokens,
                cost_usd=token_usage.cost_usd,
                latency_ms=response.latency_ms,
                cache_hit=response.cache.hit,
                quality_score=response.quality_score,
                status=response.policy.status,
            )
        )
        return response


def _simulate_provider_response(request: GatewayRequest, provider: str, model: str) -> str:
    task = request.task_category.replace("_", " ")
    return (
        f"Right LLM routed this {task} request to {provider}/{model}. "
        "The response preserves the requested outcome while applying token, cache, "
        "budget, and policy optimization controls."
    )
