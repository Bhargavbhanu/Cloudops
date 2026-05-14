from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Iterable

from .models import RawUsageRecord


def load_usage_records(path: str | Path) -> list[RawUsageRecord]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Usage data must be a JSON array of records")
    return [parse_raw_record(row) for row in payload]


def parse_raw_record(row: dict) -> RawUsageRecord:
    labels = row.get("labels") or {}
    if not isinstance(labels, dict):
        raise ValueError("labels must be an object")
    return RawUsageRecord(
        provider=str(row.get("provider", "gcp")).lower(),
        account_id=str(row.get("account_id", "unknown")),
        project_id=str(row["project_id"]),
        service=str(row["service"]),
        sku=str(row.get("sku", row["service"])),
        region=str(row.get("region", "global")),
        usage_date=date.fromisoformat(str(row["usage_date"])),
        usage_quantity=float(row.get("usage_quantity", 0.0)),
        usage_unit=str(row.get("usage_unit", "unit")),
        cost=float(row.get("cost", 0.0)),
        currency=str(row.get("currency", "USD")),
        labels={str(k): str(v) for k, v in labels.items()},
        owner=row.get("owner"),
        business_unit=row.get("business_unit"),
    )


def iter_records(path: str | Path) -> Iterable[RawUsageRecord]:
    yield from load_usage_records(path)
