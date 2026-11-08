# Implemented metric catalogue: version 1.0

Owner: project author (demonstration role). Approval state: implemented, pending business review. Synthetic data only. SQL location: `src/hardship_insights/pipeline.py`, table `mart_support_operations`.

Every row is one jurisdiction/product cohort over the configured submission period through cutoff. No cross-currency aggregation occurs. Source schema: `generate.FIELDS`, version 1.0. There is at most one request per customer in this release. Decision dates and withdrawal/lost-contact closure dates are distinct.

| Output | Calculation / eligible population |
| --- | --- |
| requests | All valid requests with notice date on/before cutoff |
| approved / declined / dropout / pending | Mutually exclusive status counts; sum must equal requests |
| dropout_rate | Withdrawn plus lost-contact requests / all requests, including pending |
| arrears_observed / arrears_unknown | Requests with a known / missing arrears value at notice |
| early_contact_rate | Zero days past due / requests with observed arrears; null when none observed |
| decided | Approved plus declined requests with decision dates |
| decision_days_median | Median calendar-day difference from notice to decision, decided requests only |
| pending_age_days_median | Median calendar days since notice at cutoff for pending requests |

Rates are exported with their counts. The Streamlit dashboard applies the small-cohort display rule: rates below 20 eligible observations are unavailable. A zero denominator yields null, never zero. These definitions are our own and are not ASIC benchmark reproductions.

Each build writes a submission receipt with schema/metric versions, cutoff, source hash and row count. Validation rejects the whole submission with row/field errors. A rejection preserves the last accepted database and metrics. A successful run records provenance inside `run_metadata`. Run one writer at a time; stop readers before replacing the database on Windows.

Current generator assumptions are configured in `config/simulation.json`: uniform request dates; independent market/product/channel selection; authored request, withdrawal, approval and missing-arrears probabilities; a discrete arrears distribution; 1-35 day terminal delay. These relationships are illustrative and do not represent lending populations. Four products currently share the same mechanics; product-specific behaviour is future work.

## Outcome extension: 9 November 2026

SQL: `dbt/models/fct_episode_outcome.sql` and `mart_outcomes.sql`. Account grain: one account per applicant. Payment grain: one account/month-end. Assistance grain: one episode per approved request. The date dimension is `dimensions`; the account dimension is `dim_account`.

| Output | Definition |
| --- | --- |
| mature | The third month-end strictly after assistance ends is on/before cutoff |
| eligible | Mature with all three expected observations present and observed |
| is_stable | Eligible and zero days past due at all three month-ends |
| stability_rate | Stable episodes / eligible episodes |
| followup_coverage | Eligible episodes / all mature episodes |
| missing_followup | Mature but incomplete observations; excludes immature episodes |

This replaces the tentative "90-day" label: three month-end observations do not describe an exact 90-day period. Planned endings are treated as actual endings in the current synthetic scenario. Future planned endings cannot qualify. Mid-month endings correctly include the month-end later in that same month. Unknown payment observations are not treated as paid/current. The mart groups by market, product and contact-at-notice cohort; the dashboard aggregates episode facts to honour channel filtering and calculates rates from counts, not averages of rates.

Outcome simulation uses an independent seeded random stream. Current-payment and missing-observation probabilities are explicit configuration assumptions. Base monthly due values are 2000/350/550/120 local currency units for mortgages/personal/auto/card accounts respectively; assistance halves scheduled dues and ends 1-3 month-ends after approval. Non-current payments use authored discrete arrears/payment values. These simple mechanics do not model balances, interest accrual, wellbeing or causal effects.

The full build retains dbt lineage/test artifacts, validates source hashes, and only promotes the database after all data checks succeed. Sixteen Python/application tests include outcome golden cases, duplicate-month rejection preserving the accepted database, determinism and dashboard filter/suppression checks. The default dbt run passes 21 data tests. Runtime dependencies are pinned in requirements-dev.lock.txt.
