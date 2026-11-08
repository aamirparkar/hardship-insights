# Share the case study

Repository: https://github.com/aamirparkar/hardship-insights

## Streamlit Community Cloud

Deploy the existing Streamlit dashboard, using the bundled validated synthetic snapshot. In Community Cloud's Create app screen:

- Repository: `aamirparkar/hardship-insights`
- Branch: `main`
- Entrypoint: `dashboard/app.py`
- Python: `3.12` in Advanced settings
- Dashboard dependencies: `dashboard/requirements.txt` (discovered beside the entrypoint)

Select an available subdomain and deploy. Confirm the actual returned URL; a proposed subdomain is not proof of deployment. Check all three tabs, filters and synthetic-data labels before sharing. Audience permissions are configured in the hosting service. No application secrets are required.

Official instructions: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## What is published

Code, tests, design documentation and a small read-only synthetic snapshot. Local environments, generated source files, database files, secrets and PROJECT_CONTEXT.md are excluded. The snapshot omits account/customer/request IDs. It preserves the counts and filter behaviour of the accepted run, rather than regenerating data per visitor.

The repository does not hardcode a server bind address, allowing the hosting platform to configure it. For a loopback-only local launch, pass `--server.address 127.0.0.1`. The dashboard has a five-minute cache with file version invalidation. It does not run dbt during visitor interactions.

## Refresh

Build and test locally, export the demo snapshot, verify snapshot mode, then commit/push the reviewed changes. Community Cloud redeploys from the selected GitHub branch. GitHub Actions validates the full pipeline separately. Azure and Power BI remain later platform/reporting deliverables.
