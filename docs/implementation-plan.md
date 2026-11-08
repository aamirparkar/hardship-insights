# Implementation plan

## Purpose and acceptance

Develop a reproducible decision-support product for financial difficulty teams. The solution should help leaders investigate access barriers, support responsiveness and observed outcomes, backed by traceable definitions and honest treatment of uncertainty. The [business roadmap](business-roadmap.md) connects each workstream to a decision, deliverable and acceptance criterion.

The current demonstrator uses synthetic data. Planned platform, analytical and operating capabilities remain in scope; this plan distinguishes delivered behaviour from future work.

## 1. Reproducible support-operations demonstrator

Delivered: seeded request generation; whole-submission request validation; accounts, assistance and monthly payment histories; DuckDB loading; six dbt models and 21 data tests; a Streamlit dashboard with market/product/channel filters; source provenance and a compact synthetic sharing snapshot.

Acceptance: a fresh environment can reproduce the pipeline; invalid request records and failing dbt tests block database promotion; outcome rates exclude immature/incomplete follow-up; denominators and missingness remain visible. Sixteen Python/application tests passed locally on 9 November 2026. CI is configured; remote execution status must be checked independently.

Remaining: session/learning/contact facts, product-specific simulation mechanics, complete dimensional coverage and stronger submission workflows. The current scenario has one request and account per applicant, one episode per approved request and planned assistance endings treated as actual endings.

## 2. Access, engagement and analytical depth

Implement separate session, learning-response and assistance-expiry contact events. Keep content exposure, knowledge, confidence and subsequent action distinct. Preserve anonymous participation and explicitly unknown linkage.

Extend product and AU/UK submission definitions. Integrate a public contextual series with source terms, publication dates, revisions and failure handling. Add cohort intervals, stratification and sensitivity to generation assumptions. Develop an interpretable outcome model and demand forecast against baselines with time-based evaluation. Demonstrate batch scoring, model monitoring, retraining decisions and rollback. Evaluate an AI-assisted ingestion aid against deterministic validation, retaining human review.

Acceptance: each analytical result traces to a contract and input version; evaluations show leakage controls, uncertainty, subgroup limitations and failures as well as improvements. Benchmark configurable volumes and report hardware/runtime/memory limits. Good fit to synthetic data is not evidence of real-world predictive usefulness.

## 3. Governance and operating model

Create a metric ownership model, release/sign-off workflow, client onboarding guide, partner build specification, assurance/security response pack and incident scenario. Review AU/UK privacy and regulatory applicability against current primary sources. Record retention, access and cross-border questions and accountable review ownership.

Develop a prioritised roadmap, cost assumptions, 30/60/90-day operating plan, team skills/development proposal and worked stakeholder decisions. Provide an executive brief, client-facing insight example and technical walkthrough. These are proposed operating practices and simulated scenarios, not claims of real client delivery.

Acceptance: each policy connects to a functioning control or a clearly labelled production proposal. Link an observation to an investigation, accountable owner and evaluation; do not invent commercial returns.

## 4. Power BI and Azure implementation

Discover tooling, licensing and service access. Prepare a costed minimal deployment before paid provisioning. Build a Power BI semantic model/report with DAX measures reconciled to SQL reference cases. Execute a synthetic submission-to-metric path in Azure, including metric computation there. Retain reproducible infrastructure/configuration and evidence of refresh, execution, cost and teardown.

Acceptance: demonstrate usable artefacts and observed runs. Architecture diagrams do not substitute for deployed behaviour. Keep unresolved access/licensing gaps explicit. Document a small portability check and alternative-platform tradeoffs without duplicating the entire system.

## 5. Product review and sharing

Review against the business roadmap, link delivered artefacts and identify remaining gaps. Balance product delivery with the governance, analysis and operating material needed to use it responsibly. Validate the hosted snapshot against the accepted database and verify the actual deployment URL before sharing it.

The code and synthetic snapshot were published to GitHub on 9 November 2026. Streamlit Community Cloud connection/deployment is being completed; no live URL is recorded as verified yet. See [sharing instructions](sharing.md).
