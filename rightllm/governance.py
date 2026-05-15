from __future__ import annotations

from .models import GatewayRequest, PolicyDecision
from .tokenization import estimate_tokens


class PolicyEngine:
    def enforce(self, request: GatewayRequest) -> PolicyDecision:
        reasons: list[str] = []
        actions: list[str] = []
        prompt_tokens = estimate_tokens(request.prompt)
        spend_ratio = request.tenant.month_to_date_spend_usd / max(
            request.tenant.monthly_budget_usd, 1
        )

        if request.tenant.role in {"intern", "contractor"} and request.baseline_model in {
            "gpt-4o",
            "claude-opus",
        }:
            reasons.append("Role cannot directly select premium frontier models")
            actions.append("route_to_approved_lower_cost_model")

        if prompt_tokens + request.max_tokens > 120000:
            reasons.append("Request exceeds enterprise token budget")
            actions.append("compress_and_prune_context")

        if spend_ratio >= 1:
            reasons.append("Budget is over limit")
            actions.extend(["throttle_non_critical_traffic", "downgrade_models"])
        elif spend_ratio >= 0.85:
            reasons.append("Budget is near limit")
            actions.append("prefer_low_cost_models")

        unsafe_terms = ("exfiltrate", "bypass policy", "steal api key")
        if any(term in request.prompt.lower() for term in unsafe_terms):
            return PolicyDecision(False, "blocked", ["Unsafe prompt pattern detected"], ["deny"])

        if reasons:
            status = "warning" if spend_ratio < 1 else "critical"
            return PolicyDecision(True, status, reasons, actions)
        return PolicyDecision(True, "healthy", ["All gateway policies passed"], [])
