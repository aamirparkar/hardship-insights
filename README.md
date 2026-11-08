# Hardship Insights

An independent case study by Aamir Parkar exploring how financial difficulty teams can identify support barriers, monitor service responsiveness and assess observed payment outcomes.

The product connects three business questions: where do requests stop progressing, how promptly do customers receive a decision, and what can be observed after assistance ends? Metric definitions, coverage and source lineage accompany the results so a support leader can decide what to investigate.

Not commissioned by or affiliated with Humbli. No customer data or proprietary scoring methods are used. All dashboard results will be labelled synthetic; simulated associations do not establish real-world impact.

Implemented stack: Python, DuckDB, dbt and Streamlit. The [business roadmap](docs/business-roadmap.md) includes Power BI, Azure, forecasting and predictive-model lifecycle work, each tied to an operational decision and verification criteria.

Source repository: https://github.com/aamirparkar/hardship-insights

## View the demo

The dashboard includes a bundled, validated synthetic snapshot so a fresh checkout can display the results without generating data. Launch with `streamlit run dashboard/app.py`. If a local warehouse database exists it takes precedence; otherwise the snapshot is loaded. Set `HARDSHIP_DEMO_MODE=1` to force snapshot mode. Results are cached with file-version invalidation and a five-minute expiry.

[Hosting and sharing instructions](docs/sharing.md) cover Streamlit Community Cloud deployment. No live dashboard URL has been verified yet. The dataset is synthetic, fixed at the stated cutoff, and intended to demonstrate engineering and analytical judgement.

## Status

Local demonstrator verified on 9 November 2026: synthetic requests, account-month payment histories, assistance episodes, submission validation, dbt models/tests and a Streamlit dashboard. Sixteen Python/application tests pass; the default dbt build passes 21 data tests and creates six models. Public-source ingestion, session/learning facts, Power BI, Azure and model lifecycle work remain planned. GitHub Actions is configured; remote execution status is separate from local verification.

## Purpose

Created to demonstrate how a governed data solution can help financial institutions understand the hardship support journey, investigate process barriers and monitor outcomes after assistance. The demonstration combines reproducible synthetic data, documented metrics, automated quality checks and interactive reporting.

Development used AI assistance. Assumptions, implementation and validation evidence are documented for review; simulated results do not establish real-world customer benefit.

## Run locally

Use Python 3.12 (tested locally with 3.12.10). From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock.txt
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m hardship_insights.cli
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

Open http://127.0.0.1:8501 once Streamlit starts. For loopback-only local serving, add `--server.address 127.0.0.1`. Virtual environments and local runtime folders are ignored by git. On macOS/Linux use `.venv/bin/python` for the environment commands.

Default configuration is `config/simulation.json`: seed 42, 10,000 candidate customers, January 2024 through October 2026, fictional AU/UK institutions and four products. This produced 3,470 requests and 2,207 assistance episodes. Counts reflect authored assumptions, not population estimates. Account histories currently cover support applicants only; they are not an entire lending portfolio. The generator treats planned assistance endings as actual endings and does not simulate extensions yet.

Outputs (all ignored by git):

- `data/synthetic/`: requests, accounts, assistance, account-month CSVs and a source manifest with hashes.
- `data/warehouse/submission_receipt.json`: accepted/rejected status and actionable row/field errors.
- `data/warehouse/hardship.duckdb`: raw/fact/dimensional tables, operations/outcome marts and run metadata.
- `data/warehouse/metrics.json`: metric values with counts, cutoff and provenance.
- `data/warehouse/dbt-build.log`, `dbt-manifest.json` and `dbt-run_results.json`: build/test and lineage evidence.

Use `--config PATH` or `--output PATH` to customise a run. Use `--submission PATH` for the original request-only validation/build mode; this does not create an outcome dashboard. Invalid submissions exit with an error and preserve previously published data. Full builds run in a private staging directory and promote the database after dbt checks pass. The dashboard reads that database as its single source of truth. Run one writer at a time; close database readers before publishing on Windows.

Metrics include status counts, dropout rate, early-contact rate, decision time, pending age, three month-end payment stability and follow-up coverage. See the [implemented metric catalogue](docs/metric-catalogue.md). The dashboard filters by market/product/channel and makes rates unavailable below 20 eligible observations. Analytical tables retain unsuppressed values. AppTest verifies rendering/filter behaviour; automated browser visual verification was unavailable.

- [Source register](docs/source-register.md)
- [Literature review and product implications](docs/literature-review.md)
- [Architecture and metric contracts](docs/architecture.md)
- [Implementation plan](docs/implementation-plan.md)
- [Business roadmap and delivery evidence](docs/business-roadmap.md)
- [Data sourcing and governance strategy](docs/data-strategy.md)
- [Hosting and sharing](docs/sharing.md)
