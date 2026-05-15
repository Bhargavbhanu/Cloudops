from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelProfile:
    provider: str
    model: str
    input_cost_per_1k: float
    output_cost_per_1k: float
    p50_latency_ms: int
    p95_latency_ms: int
    quality_score: float
    reasoning_score: float
    context_window: int
    compliance: tuple[str, ...]
    task_fit: tuple[str, ...]
    health_score: float = 0.99

    @property
    def id(self) -> str:
        return f"{self.provider}/{self.model}"


MODEL_CATALOG: tuple[ModelProfile, ...] = (
    ModelProfile(
        "openai",
        "gpt-4o",
        0.005,
        0.015,
        950,
        2100,
        0.96,
        0.96,
        128000,
        ("soc2", "hipaa", "gdpr"),
        ("complex_reasoning", "code_generation", "analytics", "structured_output"),
    ),
    ModelProfile(
        "anthropic",
        "claude-3-5-sonnet",
        0.003,
        0.015,
        880,
        1950,
        0.95,
        0.94,
        200000,
        ("soc2", "hipaa", "gdpr"),
        ("moderate_reasoning", "complex_reasoning", "summarization", "code_generation"),
    ),
    ModelProfile(
        "google",
        "gemini-1.5-flash",
        0.000075,
        0.0003,
        410,
        930,
        0.86,
        0.78,
        1000000,
        ("soc2", "gdpr"),
        ("classification", "summarization", "extraction", "formatting", "rag_search"),
    ),
    ModelProfile(
        "groq",
        "llama-3.1-70b-versatile",
        0.00059,
        0.00079,
        180,
        520,
        0.88,
        0.82,
        131000,
        ("soc2",),
        ("classification", "summarization", "conversational_ai", "formatting"),
    ),
    ModelProfile(
        "togetherai",
        "mixtral-8x22b",
        0.0009,
        0.0009,
        520,
        1100,
        0.84,
        0.8,
        65536,
        ("soc2",),
        ("extraction", "summarization", "analytics", "formatting"),
    ),
    ModelProfile(
        "azure-openai",
        "gpt-4o",
        0.0055,
        0.0165,
        980,
        2200,
        0.96,
        0.96,
        128000,
        ("soc2", "hipaa", "gdpr", "private_link"),
        ("complex_reasoning", "code_generation", "analytics", "structured_output"),
    ),
    ModelProfile(
        "aws-bedrock",
        "claude-3-haiku",
        0.00025,
        0.00125,
        470,
        950,
        0.84,
        0.76,
        200000,
        ("soc2", "hipaa", "gdpr"),
        ("classification", "summarization", "extraction", "rag_search"),
    ),
    ModelProfile(
        "ollama",
        "llama3.1:8b",
        0.0,
        0.0,
        1250,
        2900,
        0.72,
        0.66,
        32768,
        ("local",),
        ("classification", "formatting", "extraction"),
        health_score=0.95,
    ),
)


def get_model(provider: str, model: str) -> ModelProfile:
    for profile in MODEL_CATALOG:
        if profile.provider == provider and profile.model == model:
            return profile
    raise KeyError(f"Unknown model {provider}/{model}")
