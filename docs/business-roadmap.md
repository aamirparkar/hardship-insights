# Business roadmap and delivery evidence

## Decision focus

Support leaders need to understand where customers encounter friction, whether assistance is timely and appropriate, and how complete the outcome evidence is. This roadmap connects those questions to analytical, platform and operating capabilities. It distinguishes delivered behaviour from planned work and does not claim production readiness or actual customer impact.

| Workstream | Business decision | Deliverable and acceptance evidence | Status |
| --- | --- | --- | --- |
| Strategy and prioritisation | Where should investment go next? | Prioritised roadmap, growth/use-case options, cost assumptions and technology adoption decisions | Roadmap established; operating proposal planned |
| Metric design | Are teams interpreting measures consistently? | Versioned formula, schema, grain, denominator, exclusions and owner; worked definition-change review | Initial catalogue implemented; ownership/change workflow to extend |
| Lending products | Can results be compared fairly? | Mortgages, personal loans, auto loans and credit cards with product-specific eligibility and currency boundaries | Four labels implemented; shared mechanics need refinement |
| Submission and onboarding | Can institutions submit usable data efficiently? | AU/UK schemas, cleansing, valid/invalid examples, rejection reports, resubmission, receipts and onboarding guide | Initial validation implemented; full workflow planned |
| Engineering and partners | Is a release ready to accept? | SQL/Python pipeline, contracts, lineage, CI, partner build specification and acceptance/sign-off scenario | Local pipeline/tests implemented; partner pack planned |
| Reporting and insight | What should a support manager investigate? | Streamlit views, executive brief, commercial insight example and Power BI/DAX reconciled to SQL reference cases | Streamlit implemented; Power BI and brief planned |
| External context | What else could explain a trend? | Public series with source terms, provenance, publication dates, revisions and failure handling | Sources identified; integration planned |
| Statistical evaluation | How reliable is a comparison? | Cohort intervals, stratification, missingness/sensitivity analysis and intervention evaluation design | Descriptive measures implemented; research report planned |
| Prediction and forecasting | How might demand or outcomes evolve? | Baselines, temporal validation, uncertainty/calibration, explainability and large-volume benchmarks | Planned |
| Model lifecycle and responsible AI | When should a model be changed or withheld? | Batch scoring, monitoring, retraining/rollback and bounded AI-ingestion evaluation with human review | Planned |
| Azure and portability | Can execution be reproduced beyond a laptop? | Executed Azure ingestion/metric path, infrastructure configuration, cost/teardown evidence and a portability check | Planned; access/cost review precedes provisioning |
| Governance and assurance | Can results withstand review? | Definition control, lineage, test evidence, assurance/security responses, access/retention proposals, incident scenario and AU/UK applicability review | Initial controls implemented; production assurance pack planned |
| Communication and capability | Can colleagues and clients use the insight? | Client/executive/technical presentations, team learning module, skills proposal, stakeholder decisions and 30/60/90-day operating plan | Documentation started; operating artefacts planned |

## Review rules

Link completed work to code, contracts, run evidence or a clearly labelled worked scenario. Proposed controls remain distinct from implemented controls. Technical capabilities require observed execution. Record access/licensing constraints and remaining gaps. Team and client scenarios are demonstrations, not claims of real engagements.

Increasing requests may reflect changing capture or access; quicker processing does not establish appropriate assistance; payment status is not a complete measure of wellbeing. Preserve these distinctions in investigations and evaluation proposals.

## Current evidence

- `src/hardship_insights/`: generation, validation, loading, publication and snapshot export.
- `dbt/`: dimensional/fact models, outcome eligibility and data tests.
- `dashboard/app.py`: operations, outcomes and provenance with filters and version-aware caching.
- `tests/`: determinism, reference cases, rejection protection and dashboard checks.
- `docs/metric-catalogue.md`: implemented definitions and simulation limitations.
- `demo/`: validated synthetic snapshot for sharing.

See the [implementation plan](implementation-plan.md) for sequencing and the [data strategy](data-strategy.md) for sourcing and control design.
