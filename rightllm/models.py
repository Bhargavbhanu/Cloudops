from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


TASK_CATEGORIES = {
    "classification",
    "summarization",
    "extraction",
    "conversational_ai",
    "code_generation",
    "complex_reasoning",
    "moderate_reasoning",
    "rag_search",
    "analytics",
    "formatting",
    "structured_output",
}


@dataclass
class TenantContext:
    organization_id: str
    team_id: str
    project_id: str
    user_id: str
    role: str = "member"
    priority: str = "standard"
    monthly_budget_usd: float = 50000.0
    month_to_date_spend_usd: float = 0.0


@dataclass
class GatewayRequest:
    prompt: str
    task_category: str = "conversational_ai"
    baseline_provider: str = "openai"
    baseline_model: str = "gpt-4o"
    max_tokens: int = 1024
    quality_requirement: float = 0.82
    latency_sla_ms: int = 2200
    stream: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    tenant: TenantContext = field(
        default_factory=lambda: TenantContext(
            "demo-enterprise", "platform", "ai-assistant", "demo-user"
        )
    )
    request_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float


@dataclass
class RoutingDecision:
    provider: str
    model: str
    estimated_cost_usd: float
    estimated_latency_ms: int
    confidence_score: float
    optimization_reason: str
    estimated_savings_usd: float


@dataclass
class CacheDecision:
    hit: bool
    layer: str
    confidence_score: float
    trust_score: float
    key: str
    reason: str


@dataclass
class PolicyDecision:
    allowed: bool
    status: str
    reasons: list[str]
    actions: list[str]


@dataclass
class GatewayResponse:
    request_id: str
    content: str
    provider: str
    model: str
    token_usage: TokenUsage
    latency_ms: int
    cache: CacheDecision
    routing: RoutingDecision
    policy: PolicyDecision
    quality_score: float
    hallucination_score: float
    optimization_actions: list[str]
    trace: dict[str, Any]


@dataclass
class UsageMetric:
    timestamp: datetime
    organization_id: str
    team_id: str
    project_id: str
    user_id: str
    provider: str
    model: str
    task_category: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    latency_ms: int
    cache_hit: bool
    quality_score: float
    status: str


@dataclass
class Recommendation:
    title: str
    impact: str
    monthly_savings_usd: float
    confidence: float
    action: str
    evidence: dict[str, Any] = field(default_factory=dict)
