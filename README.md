# CloudScore Agent MVP

CloudScore is a cloud usage intelligence.

Live dashboard: https://bhargavbhanu.github.io/Cloudops/

This MVP implements the first buildable slice:

- Read-only style data collection from local exported usage records
- Raw-to-curated normalization into typed usage facts
- Analysis engines for anomalies, optimization, governance, forecasting, and scoring
- Data profile generation for portfolio, opportunities, unit economics, remediation, and chargeback
- DEX-style assistant answers: what happened, why it matters, impact, recommendations, and savings

The code is dependency-light so it can run locally before being wired to Google Cloud, BigQuery, Cloud Run, Redis, dbt, and dashboards.

## Quick Start

```powershell
python -m cloudscore_agent.cli --data data/sample_usage.json --question "Where can we save money this month?"
python -m cloudscore_agent.cli --data data/sample_usage.json --question "Any anomalies?"
python -m cloudscore_agent.api --data data/sample_usage.json --port 8080
```

Then open:

```text
http://localhost:8080/health
http://localhost:8080/profile
http://localhost:8080/ask?q=Where%20can%20we%20save%20money%3F
```

## Architecture Mapping

| Draft Architecture Box | MVP Module |
| --- | --- |
| Cloud Providers / Data Collection | `cloudscore_agent.ingestion` |
| BigQuery Raw Layer | local JSON input in `data/` |
| Data Cleaning & Normalization | `cloudscore_agent.normalization` |
| BigQuery Curated Layer | in-memory `UsageFact` records |
| CloudScore Intelligence | `cloudscore_agent.engines` |
| Data Profiles | `cloudscore_agent.profiles` |
| Cloud Run API Services | `cloudscore_agent.api` |
| DEX AI Assistant | `cloudscore_agent.assistant` |

## Next Production Steps

1. Replace local JSON ingestion with GCP Billing Export, Cloud Asset Inventory, IAM, labels, and governance feeds.
2. Persist raw and curated layers in BigQuery.
3. Move transformations into dbt models.
4. Deploy the API to Cloud Run and add Redis for profile/answer caching.
5. Connect the assistant to an LLM with retrieved profile context and guarded read-only tools.
