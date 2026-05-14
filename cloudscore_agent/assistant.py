from __future__ import annotations

from dataclasses import asdict

from .models import CloudScoreProfile


def answer_question(profile: CloudScoreProfile, question: str) -> dict:
    q = question.lower()
    if any(term in q for term in ["save", "saving", "optimize", "recommend"]):
        relevant = [f for f in profile.findings if f.category == "optimization"] or profile.findings
        focus = "savings and optimization"
    elif any(term in q for term in ["anomaly", "anomalies", "spike", "increase", "why"]):
        relevant = [f for f in profile.findings if f.category == "anomaly"]
        focus = "anomalies"
    elif any(term in q for term in ["governance", "label", "owner", "chargeback"]):
        relevant = [f for f in profile.findings if f.category == "governance"]
        focus = "governance"
    elif any(term in q for term in ["score", "health"]):
        relevant = profile.findings
        focus = "CloudScore health"
    else:
        relevant = profile.findings[:5]
        focus = "overall cloud usage"

    savings = round(sum(f.estimated_monthly_savings for f in relevant), 2)
    return {
        "question": question,
        "focus": focus,
        "summary": _summary(profile, relevant, savings),
        "score": profile.score,
        "forecast_monthly_cost": profile.forecast_monthly_cost,
        "estimated_monthly_savings": savings,
        "recommendations": [asdict(f) for f in relevant],
    }


def _summary(profile: CloudScoreProfile, findings, savings: float) -> str:
    if not findings:
        return (
            f"CloudScore is {profile.score}. No matching findings were detected "
            "in the current profile."
        )
    top = findings[0]
    savings_text = f" Estimated monthly savings: ${savings:.2f}." if savings else ""
    description = top.description.rstrip(".")
    return f"CloudScore is {profile.score}. Top issue: {top.title}. {description}.{savings_text}"
