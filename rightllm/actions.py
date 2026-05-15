from __future__ import annotations

from .models import GatewayRequest, PolicyDecision, RoutingDecision


def autonomous_actions(
    request: GatewayRequest,
    policy: PolicyDecision,
    routing: RoutingDecision,
    cache_hit: bool,
    prompt_tokens_saved: int,
) -> list[str]:
    actions: list[str] = []
    if prompt_tokens_saved > 0:
        actions.append(f"compressed_prompt_saved_{prompt_tokens_saved}_tokens")
    if not cache_hit and request.task_category in {"summarization", "classification", "rag_search"}:
        actions.append("scheduled_semantic_cache_write")
    if routing.estimated_savings_usd > 0:
        actions.append("executed_lower_cost_model_route")
    if routing.estimated_latency_ms > request.latency_sla_ms:
        actions.append("armed_provider_failover")
    actions.extend(policy.actions)
    return list(dict.fromkeys(actions))
