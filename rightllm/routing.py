from __future__ import annotations

from .catalog import MODEL_CATALOG, ModelProfile, get_model
from .models import GatewayRequest, RoutingDecision
from .optimization import classify_complexity
from .tokenization import estimate_tokens, predict_completion_tokens


class RoutingEngine:
    def decide(self, request: GatewayRequest, optimized_prompt: str) -> RoutingDecision:
        prompt_tokens = estimate_tokens(optimized_prompt)
        completion_tokens = predict_completion_tokens(
            optimized_prompt, request.task_category, request.max_tokens
        )
        baseline = get_model(request.baseline_provider, request.baseline_model)
        baseline_cost = estimate_cost(baseline, prompt_tokens, completion_tokens)
        complexity = classify_complexity(optimized_prompt, request.task_category)
        candidates = [
            model
            for model in MODEL_CATALOG
            if prompt_tokens + completion_tokens <= model.context_window
            and model.quality_score >= request.quality_requirement
            and model.health_score >= 0.9
            and _supports_task(model, request.task_category, complexity)
        ]
        if not candidates:
            candidates = [baseline]

        def score(model: ModelProfile) -> float:
            cost = estimate_cost(model, prompt_tokens, completion_tokens)
            latency_fit = max(0.2, 1 - (model.p95_latency_ms / max(request.latency_sla_ms * 1.6, 1)))
            budget_pressure = request.tenant.month_to_date_spend_usd / max(
                request.tenant.monthly_budget_usd, 1
            )
            cost_weight = 0.5 + min(0.3, budget_pressure)
            quality_weight = 0.35 if complexity != "simple" else 0.22
            latency_weight = 0.18 if request.tenant.priority != "critical" else 0.28
            return (
                (1 / (1 + cost * 1000)) * cost_weight
                + model.quality_score * quality_weight
                + latency_fit * latency_weight
                + model.health_score * 0.08
            )

        selected = max(candidates, key=score)
        selected_cost = estimate_cost(selected, prompt_tokens, completion_tokens)
        savings = max(0.0, baseline_cost - selected_cost)
        confidence = min(0.99, 0.68 + selected.health_score * 0.16 + selected.quality_score * 0.14)
        reason = (
            f"{complexity} {request.task_category} routed to {selected.id}: "
            f"quality {selected.quality_score:.2f}, p95 {selected.p95_latency_ms}ms, "
            f"estimated cost ${selected_cost:.5f}."
        )
        return RoutingDecision(
            provider=selected.provider,
            model=selected.model,
            estimated_cost_usd=round(selected_cost, 6),
            estimated_latency_ms=selected.p95_latency_ms,
            confidence_score=round(confidence, 3),
            optimization_reason=reason,
            estimated_savings_usd=round(savings, 6),
        )


def estimate_cost(model: ModelProfile, prompt_tokens: int, completion_tokens: int) -> float:
    return (prompt_tokens / 1000) * model.input_cost_per_1k + (
        completion_tokens / 1000
    ) * model.output_cost_per_1k


def _supports_task(model: ModelProfile, task_category: str, complexity: str) -> bool:
    if task_category in model.task_fit:
        return True
    if complexity == "simple" and {"classification", "summarization", "formatting"} & set(model.task_fit):
        return True
    if complexity == "moderate" and "moderate_reasoning" in model.task_fit:
        return True
    return False
