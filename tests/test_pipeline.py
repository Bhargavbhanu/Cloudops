import unittest

from cloudscore_agent.assistant import answer_question
from cloudscore_agent.pipeline import run_pipeline


class PipelineTest(unittest.TestCase):
    def test_pipeline_generates_cloudscore_profile(self):
        profile = run_pipeline("data/sample_usage.json")
        self.assertGreater(profile.total_cost, 0)
        self.assertGreater(profile.forecast_monthly_cost, profile.total_cost)
        self.assertLess(profile.score, 100)
        self.assertTrue(profile.findings)

    def test_pipeline_detects_anomaly(self):
        profile = run_pipeline("data/sample_usage.json")
        categories = {finding.category for finding in profile.findings}
        self.assertIn("anomaly", categories)

    def test_assistant_returns_savings_answer(self):
        profile = run_pipeline("data/sample_usage.json")
        answer = answer_question(profile, "Where can we save money?")
        self.assertEqual(answer["focus"], "savings and optimization")
        self.assertGreater(answer["estimated_monthly_savings"], 0)


if __name__ == "__main__":
    unittest.main()
