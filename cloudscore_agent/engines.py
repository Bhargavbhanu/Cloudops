from __future__ import annotations

from collections import defaultdict
from statistics import mean

from .models import Finding, UsageFact


def total_cost(facts: list[UsageFact]) -> float:
    return round(sum(f.cost for f in facts), 2)


def forecast_monthly_cost(facts: list[UsageFact]) -> float:
    daily = defaultdict(float)
    for fact in facts:
        daily[fact.usage_date.isoformat()] += fact.cost
    if not daily:
        return 0.0
    return round(mean(daily.values()) * 30, 2)


def portfolio_by_service(facts: list[UsageFact]) -> dict[str, float]:
    totals = defaultdict(float)
    for fact in facts:
        totals[fact.service] += fact.cost
    return dict(sorted((k, round(v, 2)) for k, v in totals.items()))


def chargeback_by_business_unit(facts: list[UsageFact]) -> dict[str, float]:
    totals = defaultdict(float)
    for fact in facts:
        totals[fact.business_unit] += fact.cost
    return dict(sorted((k, round(v, 2)) for k, v in totals.items()))


def unit_economics(facts: list[UsageFact]) -> dict[str, float]:
    totals = defaultdict(float)
    for fact in facts:
        totals[fact.environment] += fact.cost
    return {f"cost_{env}": round(cost, 2) for env, cost in sorted(totals.items())}


def detect_anomalies(facts: list[UsageFact]) -> list[Finding]:
    by_service_day = defaultdict(lambda: defaultdict(float))
    for fact in facts:
        by_service_day[fact.service][fact.usage_date.isoformat()] += fact.cost

    findings: list[Finding] = []
    for service, daily in by_service_day.items():
        if len(daily) < 3:
            continue
        values = list(daily.values())
        baseline = mean(values)
        for day, cost in daily.items():
            if baseline > 0 and cost >= baseline * 1.6 and cost - baseline >= 25:
                findings.append(
                    Finding(
                        category="anomaly",
                        severity="high",
                        title=f"Spend spike in {service}",
                        description=(
                            f"{service} cost reached ${cost:.2f} on {day}, "
                            f"above its ${baseline:.2f} daily baseline."
                        ),
                        evidence={
                            "service": service,
                            "date": day,
                            "cost": round(cost, 2),
                            "baseline": round(baseline, 2),
                        },
                        recommendation=(
                            "Review recent deployments, traffic changes, and resource "
                            "scale settings for this service."
                        ),
                    )
                )
    return findings


def optimization_findings(facts: list[UsageFact]) -> list[Finding]:
    findings: list[Finding] = []
    by_project_service = defaultdict(float)
    for fact in facts:
        by_project_service[(fact.project_id, fact.service, fact.environment)] += fact.cost

    for (project, service, environment), cost in by_project_service.items():
        if environment in {"dev", "test", "unknown"} and cost >= 100:
            savings = round(cost * 0.25, 2)
            findings.append(
                Finding(
                    category="optimization",
                    severity="medium",
                    title=f"Tune non-production {service} spend",
                    description=f"{project} spends ${cost:.2f} on {service} in {environment}.",
                    estimated_monthly_savings=savings,
                    evidence={
                        "project_id": project,
                        "service": service,
                        "environment": environment,
                        "cost": round(cost, 2),
                    },
                    recommendation=(
                        "Apply schedules, right-size resources, and remove idle capacity "
                        "from non-production workloads."
                    ),
                )
            )
    return findings


def governance_findings(facts: list[UsageFact]) -> list[Finding]:
    findings: list[Finding] = []
    unassigned_cost = sum(
        f.cost for f in facts if f.owner == "unassigned" or f.business_unit == "unassigned"
    )
    if unassigned_cost > 0:
        findings.append(
            Finding(
                category="governance",
                severity="medium",
                title="Unassigned cloud spend",
                description=(
                    f"${unassigned_cost:.2f} has missing owner or business unit metadata."
                ),
                evidence={"unassigned_cost": round(unassigned_cost, 2)},
                recommendation=(
                    "Enforce labels for owner, business_unit, environment, application, "
                    "and cost_center."
                ),
            )
        )
    return findings


def score_cloud_usage(findings: list[Finding], monthly_forecast: float) -> tuple[int, str]:
    penalty = 0
    penalty += sum(18 for finding in findings if finding.severity == "high")
    penalty += sum(9 for finding in findings if finding.severity == "medium")
    if monthly_forecast > 10000:
        penalty += 5
    score = max(0, min(100, 100 - penalty))
    if score >= 85:
        reason = "Strong usage hygiene with manageable opportunities."
    elif score >= 65:
        reason = "Healthy baseline, but optimization and governance need attention."
    else:
        reason = "Material risks or savings opportunities need immediate action."
    return score, reason
