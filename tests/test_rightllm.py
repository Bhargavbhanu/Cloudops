import unittest

from rightllm.advisor import recommend_model
from rightllm.gateway import RightLLMGateway
from rightllm.migration import simulate_migration
from rightllm.models import GatewayRequest, TenantContext


class RightLLMTest(unittest.TestCase):
    def test_gateway_routes_simple_tasks_to_lower_cost_model(self):
        gateway = RightLLMGateway()
        response = gateway.chat(
            GatewayRequest(
                prompt="Classify this support ticket as billing, login, or bug.",
                task_category="classification",
                baseline_provider="openai",
                baseline_model="gpt-4o",
                quality_requirement=0.82,
            )
        )
        self.assertIn(response.provider, {"google", "aws-bedrock", "groq"})
        self.assertGreater(response.routing.estimated_savings_usd, 0)
        self.assertIn("executed_lower_cost_model_route", response.optimization_actions)

    def test_semantic_cache_hits_repeated_prompts(self):
        gateway = RightLLMGateway()
        request = GatewayRequest(
            prompt="Summarize the May LLM spend dashboard for the executive team.",
            task_category="summarization",
        )
        first = gateway.chat(request)
        second = gateway.chat(request)
        self.assertFalse(first.cache.hit)
        self.assertTrue(second.cache.hit)
        self.assertEqual(second.token_usage.cost_usd, 0.0)

    def test_policy_budget_pressure_triggers_actions(self):
        gateway = RightLLMGateway()
        response = gateway.chat(
            GatewayRequest(
                prompt="Analyze customer churn drivers using recent LLM traces.",
                task_category="analytics",
                tenant=TenantContext(
                    "acme", "finance", "retention-ai", "analyst-1", monthly_budget_usd=100, month_to_date_spend_usd=91
                ),
            )
        )
        self.assertEqual(response.policy.status, "warning")
        self.assertIn("prefer_low_cost_models", response.optimization_actions)

    def test_advisor_returns_ranked_savings(self):
        result = recommend_model(
            "Extract account ids and invoice totals from support notes.",
            "extraction",
            250000,
        )
        self.assertTrue(result["provider_ranking"])
        self.assertGreaterEqual(result["recommended_model"]["monthly_savings_usd"], 0)

    def test_migration_simulator_scores_target(self):
        result = simulate_migration(
            "openai",
            "gpt-4o",
            "google",
            "gemini-1.5-flash",
            "summarization",
        )
        self.assertGreater(result["cost_reduction_percent"], 50)
        self.assertIn("migration_confidence_score", result)


if __name__ == "__main__":
    unittest.main()
