"""Validate and atomically publish a small DuckDB analytical run."""

import hashlib
import json
import os
from datetime import date
from pathlib import Path

import duckdb

from hardship_insights.validate import validate


def build(submission: Path, output: Path, cutoff: date) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    rows, errors = validate(submission, cutoff)
    source_hash = hashlib.sha256(submission.read_bytes()).hexdigest()
    receipt = {
        "schema_version": "1.0", "metric_version": "1.0", "synthetic": True,
        "cutoff": cutoff.isoformat(), "source_sha256": source_hash,
        "status": "rejected" if errors else "accepted", "rows": len(rows), "errors": errors,
    }
    (output / "submission_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    if errors:
        raise ValueError(f"Submission rejected: {len(errors)} errors; see {output / 'submission_receipt.json'}")
    staging = output / "build.duckdb"
    with duckdb.connect(str(staging)) as con:
        con.execute("create or replace table raw_requests as select * from read_csv(?, all_varchar=true)", [str(submission)])
        con.execute("""
            create or replace table fct_application as
            select * exclude(notice_date, decision_date, closure_date, days_past_due),
                   cast(notice_date as date) notice_date,
                   cast(decision_date as date) decision_date,
                   cast(closure_date as date) closure_date,
                   cast(days_past_due as integer) days_past_due
            from raw_requests
        """)
        con.execute("""
            create or replace table mart_support_operations as
            select jurisdiction, product, count(*) requests,
                count(*) filter(where status = 'approved') approved,
                count(*) filter(where status = 'declined') declined,
                count(*) filter(where status in ('withdrawn','lost_contact')) dropout,
                count(*) filter(where status = 'pending') pending,
                count(days_past_due) arrears_observed,
                count(*) filter(where days_past_due = 0) early_contact,
                count(*) filter(where days_past_due is null) arrears_unknown,
                count(decision_date) decided,
                median(date_diff('day', notice_date, decision_date)) decision_days_median,
                median(case when status = 'pending' then date_diff('day',notice_date,cast(? as date)) end) pending_age_days_median,
                count(*) filter(where status in ('withdrawn','lost_contact')) * 1.0 / count(*) dropout_rate,
                count(*) filter(where days_past_due = 0) * 1.0 / nullif(count(days_past_due),0) early_contact_rate
            from fct_application group by jurisdiction, product order by jurisdiction, product
        """, [cutoff.isoformat()])
        columns = [column[0] for column in con.execute("select * from mart_support_operations limit 0").description]
        metrics = [dict(zip(columns, row)) for row in con.execute("select * from mart_support_operations order by jurisdiction,product").fetchall()]
        con.execute("create or replace table run_metadata as select ? cutoff, ? source_sha256, '1.0' metric_version, true synthetic", [cutoff.isoformat(), source_hash])
    os.replace(staging, output / "hardship.duckdb")
    result = {**receipt, "metrics": metrics}
    (output / "metrics.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result
