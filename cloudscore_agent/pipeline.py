from __future__ import annotations

from pathlib import Path

from .ingestion import load_usage_records
from .normalization import normalize_records
from .profiles import build_profile


def run_pipeline(data_path: str | Path):
    raw_records = load_usage_records(data_path)
    facts = normalize_records(raw_records)
    return build_profile(facts)
