# Public demonstration snapshot

`snapshot.json.gz` is a deterministic compressed export from the validated synthetic database. It contains only the application/outcome fields needed to reproduce dashboard filters and summaries, plus source provenance. Account/customer/request identifiers are omitted. It is not real customer data.

Regenerate after a successful pipeline build:

```powershell
.\.venv\Scripts\python.exe -m hardship_insights.export_demo
```

The dashboard uses this snapshot when its local database is absent. Set `HARDSHIP_DEMO_MODE=1` to explicitly test snapshot mode locally. The deployment requires no database service, credentials or pipeline execution at startup. Cache entries are invalidated by file modification time and size, with a five-minute expiry.

The source CSVs, full database and local working notes remain outside git. Refreshing the hosted data requires explicitly exporting and publishing a new snapshot.
