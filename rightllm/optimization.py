from __future__ import annotations

import re

from .tokenization import estimate_tokens


FILLER_PHRASES = (
    "please note that",
    "it is important to understand that",
    "as an ai language model",
    "in order to",
    "kindly",
)


def fingerprint_prompt(prompt: str) -> str:
    normalized = re.sub(r"\s+", " ", prompt.strip().lower())
    normalized = re.sub(r"\d{4}-\d{2}-\d{2}", "<date>", normalized)
    normalized = re.sub(r"\b[0-9a-f]{8,}\b", "<id>", normalized)
    return normalized


def compress_prompt(prompt: str, max_reduction: float = 0.28) -> tuple[str, int]:
    before = estimate_tokens(prompt)
    optimized = prompt.strip()
    for phrase in FILLER_PHRASES:
        optimized = re.sub(phrase, "", optimized, flags=re.IGNORECASE)
    optimized = re.sub(r"\s+", " ", optimized)
    optimized = re.sub(r"(\b[\w-]+\b)(\s+\1\b)+", r"\1", optimized, flags=re.IGNORECASE)

    words = optimized.split()
    target_len = int(len(words) * (1 - max_reduction))
    if len(words) > 260 and target_len > 0:
        head = words[: int(target_len * 0.72)]
        tail = words[-int(target_len * 0.28) :]
        optimized = " ".join(head + ["[context pruned for token budget]"] + tail)

    after = estimate_tokens(optimized)
    if after >= before:
        return prompt.strip(), 0
    return optimized, before - after


def classify_complexity(prompt: str, task_category: str) -> str:
    tokens = estimate_tokens(prompt)
    hard_terms = ("prove", "debug", "architecture", "root cause", "tradeoff", "migrate")
    if task_category in {"complex_reasoning", "code_generation"} or any(t in prompt.lower() for t in hard_terms):
        return "complex"
    if tokens > 1200 or task_category in {"analytics", "structured_output", "moderate_reasoning"}:
        return "moderate"
    return "simple"
