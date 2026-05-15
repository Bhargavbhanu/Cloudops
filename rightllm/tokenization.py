from __future__ import annotations

import re

TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, int(len(TOKEN_RE.findall(text)) * 1.08))


def predict_completion_tokens(prompt: str, task_category: str, max_tokens: int) -> int:
    prompt_tokens = estimate_tokens(prompt)
    multipliers = {
        "classification": 0.12,
        "formatting": 0.18,
        "extraction": 0.28,
        "summarization": 0.34,
        "rag_search": 0.42,
        "analytics": 0.55,
        "conversational_ai": 0.62,
        "moderate_reasoning": 0.74,
        "structured_output": 0.78,
        "complex_reasoning": 0.95,
        "code_generation": 1.1,
    }
    predicted = int(prompt_tokens * multipliers.get(task_category, 0.55)) + 48
    return max(16, min(max_tokens, predicted))
