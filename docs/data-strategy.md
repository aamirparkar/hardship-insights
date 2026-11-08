# Data sourcing and governance strategy

## Decision

Use deterministic synthetic operational records plus real public contextual series. Public sources below supply economic context or survey evidence; they do not supply a linked lender support journey. Do not fabricate customer-level linkage to public aggregates. Public downloads, licensing and exact series selection remain to be implemented and verified.

## Source plan

| Layer | Source | Purpose |
| --- | --- | --- |
| Synthetic operations | Project-owned Python generator | Fictional accounts, payments, support requests, learning interactions, assistance and follow-up |
| Australian context | [RBA cash rate / F1](https://www.rba.gov.au/statistics/cash-rate/) and [statistical tables](https://www.rba.gov.au/statistics/tables/) | Historical rate context and external-data ingestion |
| Australian context | [ABS Labour Force](https://www.abs.gov.au/statistics/labour/employment-and-unemployment/labour-force-australia/latest-release) | Monthly labour-market context, with publication dates and methodological changes |
| UK context | [Bank of England database](https://www.bankofengland.co.uk/boeapps/database/) | UK rate series, selected with documented units and frequency |
| UK domain context | [FCA Financial Lives](https://www.fca.org.uk/financial-lives) | Published survey tables and definitions for contextual interpretation, not synthetic customer linkage |

Start with one RBA series and the synthetic operational layer. Add ABS and UK sources after the pipeline works. Review source terms before storing or redistributing files. Prefer aggregate FCA tables initially; individual responses have a separate access route and are unnecessary for the first release.

## Synthetic design

Initial target: 10,000 fictional customers across four lending products and AU/UK institutions, with 36 months of account history. These are configurable engineering choices, not representative sample sizes. Use a smaller fixture for CI and a larger optional performance benchmark.

Use a fixed seed, cutoff and versioned configuration. Preserve country, currency, product, institution, account and event grains. Generate chronological journeys with pending cases, withdrawals, missing follow-up, incorrect learning answers and unlinked sessions. Keep intentionally invalid submissions in separate validation fixtures; never mix them silently into accepted analytical tables.

Maintain an assumption register for each probability, balance range, delay and simulated relationship. Do not tune results to support a favourable narrative. If macroeconomic series influence simulation, label the relationship as an imposed scenario and retain a no-macro baseline. Model evaluation demonstrates technique; it does not validate real-world performance.

## Governance as functioning behaviour

| Control | Evidence in the solution |
| --- | --- |
| Source ownership and provenance | Source manifest with publisher, URL, licence/terms, series ID, retrieval time, reference period, publication date and file hash |
| Data contracts | Versioned schema with types, units, required fields, permitted values and product/market eligibility |
| Submission quality | Rejection/quarantine report, correction workflow, reconciliation and idempotent resubmission |
| Metric accountability | Definition, owner, approval state, effective date and calculation lineage for each measure |
| Safe publishing | Only validated runs feed reports; display freshness, coverage, denominator and synthetic/public provenance |
| Privacy and access | No personal identifiers; synthetic-data classification; production access/retention proposals and AU/UK applicability review clearly labelled as proposals |
| Change control | Definition-change example, reviewed release record and rollback exercise |
| Model governance | Versioned training/scoring inputs, temporal validation, monitoring thresholds, model card and retraining/rollback decisions |

Join contextual series by jurisdiction and time only. Forecast backtests must use information available at the prediction date. A current revised historical series is not automatically a valid real-time vintage; if vintages cannot be obtained, disclose that limitation and avoid claims of leakage-free operational backtesting with those features.

## Strategy demonstrated through decisions

Prioritise access friction, support responsiveness and observed outcomes. Explain the leader's decision behind each dashboard measure. Use a roadmap, cost assumptions, accountable owners and explicit acceptance criteria. Begin with a local reproducible pipeline, then demonstrate Power BI reporting and Azure execution with reconciled results. Review priorities against the [business roadmap](business-roadmap.md) at each milestone.

The solution should demonstrate that increasing requests can reflect improved access or capture, that quicker processing does not guarantee appropriate support, and that payment stability alone does not establish wellbeing. Include a worked investigation and proposed evaluation rather than invented commercial benefits.

## Immediate build order

1. Establish Python and pin a working environment.
2. Write submission schemas, generator assumptions and a small valid/invalid fixture.
3. Implement generation, ingestion, quality checks and one metric end to end.
4. Add the first public series with provenance and licensing records.
5. Expand the dashboard, analysis, model lifecycle and Power BI/Azure deliverables against the business roadmap and its acceptance criteria.
