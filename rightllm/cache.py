from __future__ import annotations

import math
import time
from collections import Counter
from dataclasses import dataclass

from .models import CacheDecision
from .optimization import fingerprint_prompt


@dataclass
class CacheEntry:
    key: str
    prompt: str
    response: str
    embedding: Counter[str]
    created_at: float
    ttl_seconds: int
    quality_score: float
    token_savings: int


class SemanticCache:
    def __init__(self, similarity_threshold: float = 0.86) -> None:
        self.similarity_threshold = similarity_threshold
        self._entries: dict[str, CacheEntry] = {}

    def search(self, prompt: str) -> tuple[CacheDecision, str | None]:
        now = time.time()
        key = fingerprint_prompt(prompt)
        exact = self._entries.get(key)
        if exact and exact.created_at + exact.ttl_seconds > now:
            return (
                CacheDecision(True, "L1_EXACT", 1.0, exact.quality_score, key, "Exact prompt fingerprint match"),
                exact.response,
            )

        query = _embed(prompt)
        best: tuple[float, CacheEntry] | None = None
        for entry in self._entries.values():
            if entry.created_at + entry.ttl_seconds <= now:
                continue
            similarity = _cosine(query, entry.embedding)
            if not best or similarity > best[0]:
                best = (similarity, entry)

        if best and best[0] >= self.similarity_threshold:
            similarity, entry = best
            return (
                CacheDecision(
                    True,
                    "L2_SEMANTIC",
                    round(similarity, 3),
                    round(min(entry.quality_score, similarity), 3),
                    entry.key,
                    "Semantic similarity crossed trust threshold",
                ),
                entry.response,
            )

        return (
            CacheDecision(False, "MISS", 0.0, 0.0, key, "No reusable exact or semantic response"),
            None,
        )

    def write(
        self,
        prompt: str,
        response: str,
        quality_score: float,
        token_savings: int = 0,
        ttl_seconds: int = 3600,
    ) -> None:
        key = fingerprint_prompt(prompt)
        self._entries[key] = CacheEntry(
            key=key,
            prompt=prompt,
            response=response,
            embedding=_embed(prompt),
            created_at=time.time(),
            ttl_seconds=ttl_seconds,
            quality_score=quality_score,
            token_savings=token_savings,
        )

    def invalidate(self, event: str) -> int:
        if event in {"incident_resolved", "topology_updated", "knowledge_base_changed", "model_version_updated"}:
            count = len(self._entries)
            self._entries.clear()
            return count
        return 0

    def stats(self) -> dict[str, float]:
        return {"entries": len(self._entries), "similarity_threshold": self.similarity_threshold}


def _embed(text: str) -> Counter[str]:
    words = [w.lower() for w in text.split() if len(w) > 2]
    return Counter(words)


def _cosine(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0
    common = set(left) & set(right)
    dot = sum(left[token] * right[token] for token in common)
    left_norm = math.sqrt(sum(v * v for v in left.values()))
    right_norm = math.sqrt(sum(v * v for v in right.values()))
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)
