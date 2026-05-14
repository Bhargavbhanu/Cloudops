from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass(frozen=True)
class RawUsageRecord:
    provider: str
    account_id: str
    project_id: str
    service: str
    sku: str
    region: str
    usage_date: date
    usage_quantity: float
    usage_unit: str
    cost: float
    currency: str = "USD"
    labels: dict[str, str] = field(default_factory=dict)
    owner: str | None = None
    business_unit: str | None = None


@dataclass(frozen=True)
class UsageFact:
    provider: str
    account_id: str
    project_id: str
    service: str
    sku: str
    region: str
    usage_date: date
    usage_quantity: float
    usage_unit: str
    cost: float
    currency: str
    owner: str
    business_unit: str
    environment: str
    labels: dict[str, str]


@dataclass(frozen=True)
class Finding:
    category: str
    severity: str
    title: str
    description: str
    estimated_monthly_savings: float = 0.0
    evidence: dict[str, Any] = field(default_factory=dict)
    recommendation: str = ""


@dataclass(frozen=True)
class CloudScoreProfile:
    total_cost: float
    forecast_monthly_cost: float
    score: int
    score_reason: str
    portfolio: dict[str, float]
    unit_economics: dict[str, float]
    chargeback: dict[str, float]
    findings: list[Finding]
