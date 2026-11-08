"""Export only the synthetic facts needed by the public read-only dashboard."""

import argparse
import gzip
import json
from pathlib import Path

import duckdb


def export_demo(database: Path, destination: Path):
    with duckdb.connect(str(database), read_only=True) as con:
        metadata = json.loads(con.execute("select * from run_metadata").fetchdf().to_json(orient="records"))[0]
        if metadata.get("synthetic") is not True or metadata.get("quality_status") != "passed" or metadata.get("build_scope") != "outcomes":
            raise ValueError("Export requires a validated synthetic outcome build")
        applications = con.execute("select jurisdiction,product,channel,notice_date,decision_date,days_past_due,status from fct_application").fetchdf()
        outcomes = con.execute("select jurisdiction,product,channel,contact_cohort,mature,eligible,is_stable from fct_episode_outcome").fetchdf()
    payload = {"format_version": 1, "metadata": metadata,
               "applications": json.loads(applications.to_json(orient="records", date_format="iso")),
               "outcomes": json.loads(outcomes.to_json(orient="records"))}
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(gzip.compress(json.dumps(payload, sort_keys=True).encode(), mtime=0))
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=Path("data/warehouse/hardship.duckdb"))
    parser.add_argument("--output", type=Path, default=Path("demo/snapshot.json.gz"))
    args = parser.parse_args()
    export_demo(args.database, args.output)
    print(f"Exported validated SYNTHETIC dashboard snapshot: {args.output}")
