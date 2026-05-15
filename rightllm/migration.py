from __future__ import annotations

from .catalog import get_model


def simulate_migration(
    source_provider: str,
    source_model: str,
    target_provider: str,
    target_model: str,
    workload_category: str,
    monthly_tokens: int = 10_000_000,
) -> dict:
    source = get_model(source_provider, source_model)
    target = get_model(target_provider, target_model)
    input_tokens = int(monthly_tokens * 0.62)
    output_tokens = monthly_tokens - input_tokens
    source_cost = (input_tokens / 1000) * source.input_cost_per_1k + (
        output_tokens / 1000
    ) * source.output_cost_per_1k
    target_cost = (input_tokens / 1000) * target.input_cost_per_1k + (
        output_tokens / 1000
    ) * target.output_cost_per_1k
    quality_delta = target.quality_score - source.quality_score
    formatting_risk = 0.08 if workload_category in target.task_fit else 0.22
    confidence = max(0.35, min(0.97, 0.82 + quality_delta - formatting_risk / 2))
    return {
        "source": source.id,
        "target": target.id,
        "workload_category": workload_category,
        "source_monthly_cost_usd": round(source_cost, 2),
        "target_monthly_cost_usd": round(target_cost, 2),
        "cost_reduction_usd": round(source_cost - target_cost, 2),
        "cost_reduction_percent": round(((source_cost - target_cost) / max(source_cost, 1)) * 100, 1),
        "latency_change_ms": target.p95_latency_ms - source.p95_latency_ms,
        "quality_degradation": round(max(0.0, -quality_delta), 3),
        "hallucination_risk": round(max(0.03, 0.18 - target.reasoning_score * 0.1), 3),
        "formatting_compatibility": round(1 - formatting_risk, 3),
        "json_compatibility": round(0.97 if "structured_output" in target.task_fit else 0.84, 3),
        "migration_confidence_score": round(confidence, 3),
        "recommended_tests": [
            "Replay historical prompts",
            "Compare structured outputs side-by-side",
            "Run hallucination and refusal regression checks",
            "Validate latency under p95 production load",
        ],
    }
