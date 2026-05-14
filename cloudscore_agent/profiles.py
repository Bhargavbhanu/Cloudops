from __future__ import annotations

from .engines import (
    chargeback_by_business_unit,
    detect_anomalies,
    forecast_monthly_cost,
    governance_findings,
    optimization_findings,
    portfolio_by_service,
    score_cloud_usage,
    total_cost,
    unit_economics,
)
from .models import CloudScoreProfile, UsageFact


def build_profile(facts: list[UsageFact]) -> CloudScoreProfile:
    findings = [
        *detect_anomalies(facts),
        *optimization_findings(facts),
        *governance_findings(facts),
    ]
    forecast = forecast_monthly_cost(facts)
    score, reason = score_cloud_usage(findings, forecast)
    return CloudScoreProfile(
        total_cost=total_cost(facts),
        forecast_monthly_cost=forecast,
        score=score,
        score_reason=reason,
        portfolio=portfolio_by_service(facts),
        unit_economics=unit_economics(facts),
        chargeback=chargeback_by_business_unit(facts),
        findings=findings,
    )
