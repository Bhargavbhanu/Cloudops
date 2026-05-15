from __future__ import annotations

from dataclasses import asdict

from .catalog import MODEL_CATALOG, get_model
from .routing import estimate_cost
from .tokenization import estimate_tokens, predict_completion_tokens


def recommend_model(
    prompt: str,
    task_category: str,
    monthly_volume: int,
    baseline_provider: str = "openai",
    baseline_model: str = "gpt-4o",
    expected_response_length: int = 1024,
) -> dict:
    prompt_tokens = estimate_tokens(prompt)
    output_tokens = predict_completion_tokens(prompt, task_category, expected_response_length)
    baseline = get_model(baseline_provider, baseline_model)
    baseline_monthly = estimate_cost(baseline, prompt_tokens, output_tokens) * monthly_volume
    ranked = []
    for model in MODEL_CATALOG:
        cost = estimate_cost(model, prompt_tokens, output_tokens)
        quality_fit = model.quality_score if task_category in model.task_fit else model.quality_score * 0.92
        ranked.append(
            {
                "provider": model.provider,
                "model": model.model,
                "predicted_output_tokens": output_tokens,
                "request_cost_usd": round(cost, 6),
                "monthly_cost_usd": round(cost * monthly_volume, 2),
                "monthly_savings_usd": round(max(0.0, baseline_monthly - cost * monthly_volume), 2),
                "latency_estimate_ms": model.p95_latency_ms,
                "quality_score": round(quality_fit, 3),
                "confidence_interval": [round(output_tokens * 0.72), round(output_tokens * 1.28)],
            }
        )
    ranked.sort(key=lambda row: (-(row["quality_score"] >= 0.82), row["monthly_cost_usd"]))
    return {
        "input_tokens": prompt_tokens,
        "predicted_output_tokens": output_tokens,
        "baseline": asdict(baseline),
        "recommended_model": ranked[0],
        "provider_ranking": ranked,
        "cost_quality_tradeoff": [
            {"model": f"{r['provider']}/{r['model']}", "cost": r["monthly_cost_usd"], "quality": r["quality_score"]}
            for r in ranked
        ],
    }
