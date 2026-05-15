from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from statistics import mean

from .models import Recommendation, UsageMetric


class MetricsStore:
    def __init__(self) -> None:
        self.metrics: list[UsageMetric] = []

    def append(self, metric: UsageMetric) -> None:
        self.metrics.append(metric)

    def usage_summary(self) -> dict:
        if not self.metrics:
            return _empty_summary()
        total_cost = sum(m.cost_usd for m in self.metrics)
        prompt_tokens = sum(m.prompt_tokens for m in self.metrics)
        completion_tokens = sum(m.completion_tokens for m in self.metrics)
        cache_hits = sum(1 for m in self.metrics if m.cache_hit)
        p95_latency = sorted(m.latency_ms for m in self.metrics)[max(0, int(len(self.metrics) * 0.95) - 1)]
        by_provider = defaultdict(float)
        by_model = defaultdict(float)
        by_project = defaultdict(float)
        for metric in self.metrics:
            by_provider[metric.provider] += metric.cost_usd
            by_model[f"{metric.provider}/{metric.model}"] += metric.cost_usd
            by_project[metric.project_id] += metric.cost_usd
        return {
            "requests": len(self.metrics),
            "total_cost_usd": round(total_cost, 4),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "cache_hit_rate": round(cache_hits / len(self.metrics), 3),
            "p95_latency_ms": p95_latency,
            "average_quality_score": round(mean(m.quality_score for m in self.metrics), 3),
            "provider_distribution": _round_dict(by_provider),
            "model_distribution": _round_dict(by_model),
            "project_usage": _round_dict(by_project),
            "sla_compliance": round(
                sum(1 for m in self.metrics if m.latency_ms <= 2200) / len(self.metrics), 3
            ),
        }

    def forecast(self, days: int = 30) -> dict:
        if not self.metrics:
            return {"forecast_days": days, "projected_spend_usd": 0.0, "budget_exhaustion": None}
        first = min(m.timestamp for m in self.metrics)
        elapsed_days = max(1, (datetime.now(timezone.utc) - first).days + 1)
        daily_cost = sum(m.cost_usd for m in self.metrics) / elapsed_days
        projected = daily_cost * days
        growth = _growth_rate(self.metrics)
        return {
            "forecast_days": days,
            "projected_spend_usd": round(projected * (1 + growth), 2),
            "token_growth_rate": round(growth, 3),
            "savings_forecast_usd": round(projected * 0.42, 2),
            "optimization_opportunities": [
                "Increase semantic cache threshold coverage",
                "Move simple classification to Gemini Flash or Bedrock Haiku",
                "Compress prompts above 4k tokens automatically",
            ],
        }

    def recommendations(self) -> list[Recommendation]:
        summary = self.usage_summary()
        recs = [
            Recommendation(
                "Route simple traffic to low-cost fast models",
                "High",
                max(1200.0, summary["total_cost_usd"] * 0.34),
                0.91,
                "Enable weighted routing policy for classification, extraction, and formatting.",
                {"provider_distribution": summary["provider_distribution"]},
            ),
            Recommendation(
                "Expand semantic cache coverage",
                "Medium",
                max(600.0, summary["total_cost_usd"] * 0.18),
                0.86,
                "Turn on L2 semantic cache for repetitive support, analytics, and RAG prompts.",
                {"current_cache_hit_rate": summary["cache_hit_rate"]},
            ),
        ]
        if summary["p95_latency_ms"] > 2000:
            recs.append(
                Recommendation(
                    "Activate provider failover for latency spikes",
                    "Medium",
                    max(300.0, summary["total_cost_usd"] * 0.08),
                    0.82,
                    "Fail over traffic when provider p95 exceeds SLA for three windows.",
                    {"p95_latency_ms": summary["p95_latency_ms"]},
                )
            )
        return recs


def _empty_summary() -> dict:
    return {
        "requests": 0,
        "total_cost_usd": 0.0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "cache_hit_rate": 0.0,
        "p95_latency_ms": 0,
        "average_quality_score": 0.0,
        "provider_distribution": {},
        "model_distribution": {},
        "project_usage": {},
        "sla_compliance": 1.0,
    }


def _round_dict(values: dict[str, float]) -> dict[str, float]:
    return dict(sorted((key, round(value, 4)) for key, value in values.items()))


def _growth_rate(metrics: list[UsageMetric]) -> float:
    recent_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    recent = [m.prompt_tokens + m.completion_tokens for m in metrics if m.timestamp >= recent_cutoff]
    if len(recent) < 2:
        return 0.08
    return min(0.35, max(-0.2, (recent[-1] - recent[0]) / max(recent[0], 1)))


def asdict_list(items: list) -> list[dict]:
    return [asdict(item) for item in items]
