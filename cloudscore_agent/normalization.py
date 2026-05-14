from __future__ import annotations

from .models import RawUsageRecord, UsageFact


def normalize_records(records: list[RawUsageRecord]) -> list[UsageFact]:
    return [normalize_record(record) for record in records]


def normalize_record(record: RawUsageRecord) -> UsageFact:
    labels = {k.lower().strip(): v.strip() for k, v in record.labels.items()}
    owner = (record.owner or labels.get("owner") or "unassigned").strip().lower()
    business_unit = (
        record.business_unit
        or labels.get("business_unit")
        or labels.get("bu")
        or "unassigned"
    ).strip().lower()
    environment = (
        labels.get("env") or labels.get("environment") or "unknown"
    ).strip().lower()
    return UsageFact(
        provider=record.provider.lower().strip(),
        account_id=record.account_id.strip(),
        project_id=record.project_id.strip().lower(),
        service=record.service.strip(),
        sku=record.sku.strip(),
        region=record.region.strip().lower(),
        usage_date=record.usage_date,
        usage_quantity=max(record.usage_quantity, 0.0),
        usage_unit=record.usage_unit.strip().lower(),
        cost=max(record.cost, 0.0),
        currency=record.currency.upper().strip(),
        owner=owner,
        business_unit=business_unit,
        environment=environment,
        labels=labels,
    )
