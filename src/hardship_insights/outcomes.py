"""Synthetic account histories, governed dbt build, and atomic database promotion."""

import calendar
import csv
import hashlib
import json
import os
import random
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

import duckdb

from hardship_insights.pipeline import build

ROOT = Path(__file__).resolve().parents[2]
TABLE_FIELDS = {
    "accounts": ["account_id", "request_id", "customer_id", "product", "currency", "monthly_due"],
    "assistance": ["episode_id", "request_id", "account_id", "start_date", "planned_end_date", "assistance_type"],
    "account_months": ["account_id", "month_end", "observed", "days_past_due", "scheduled_due", "actual_paid"],
}


def month_end(value: date, offset: int = 0) -> date:
    year, month = divmod(value.year * 12 + value.month - 1 + offset, 12)
    return date(year, month + 1, calendar.monthrange(year, month + 1)[1])


def generate_outcomes(config: dict, source: Path) -> dict:
    rng = random.Random(config["seed"] + 1000)
    cutoff = date.fromisoformat(config["cutoff"])
    first = date.fromisoformat(config["start_date"])
    params = config.get("outcomes", {})
    missing = params.get("missing_observation_probability", 0.05)
    current = params.get("current_payment_probability", 0.78)
    if not 0 <= missing <= 1 or not 0 <= current <= 1:
        raise ValueError("Outcome probabilities must be in [0,1]")
    with (source / "requests.csv").open(newline="", encoding="utf-8") as file:
        requests = list(csv.DictReader(file))
    handles = {name: (source / f"{name}.csv").open("w", newline="", encoding="utf-8") for name in TABLE_FIELDS}
    counts = dict.fromkeys(TABLE_FIELDS, 0)
    try:
        writers = {name: csv.DictWriter(file, fieldnames=TABLE_FIELDS[name], lineterminator="\n") for name, file in handles.items()}
        for writer in writers.values():
            writer.writeheader()
        for row in requests:
            account = "A" + row["customer_id"][1:]
            due = {"mortgage": 2000, "personal_loan": 350, "auto_loan": 550, "credit_card": 120}[row["product"]]
            writers["accounts"].writerow(dict(zip(TABLE_FIELDS["accounts"], [account, row["request_id"], row["customer_id"], row["product"], row["currency"], due])))
            counts["accounts"] += 1
            assistance_start = assistance_end = None
            if row["status"] == "approved":
                assistance_start = date.fromisoformat(row["decision_date"])
                assistance_end = month_end(assistance_start, rng.choice([1, 2, 3]))
                writers["assistance"].writerow(dict(zip(TABLE_FIELDS["assistance"], ["E" + row["request_id"][1:], row["request_id"], account, assistance_start, assistance_end, "reduced_payment"])))
                counts["assistance"] += 1
            offset = 0
            while (period := month_end(first, offset)) <= cutoff:
                offset += 1
                observed = rng.random() >= missing
                past_due = 0 if rng.random() < current else rng.choice([15, 30, 60])
                scheduled = due // 2 if assistance_start and assistance_start <= period <= assistance_end else due
                paid = scheduled if past_due == 0 else round(scheduled * rng.choice([0, 0.5]))
                writers["account_months"].writerow(dict(zip(TABLE_FIELDS["account_months"], [account, period, str(observed).lower(), past_due if observed else "", scheduled, paid if observed else ""])))
                counts["account_months"] += 1
    finally:
        for file in handles.values():
            file.close()
    manifest_path = source / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["outcome_generator_version"] = "0.2.0"
    for name in TABLE_FIELDS:
        filename = f"{name}.csv"
        manifest["files"][filename] = {"rows": counts[name], "sha256": hashlib.sha256((source / filename).read_bytes()).hexdigest()}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def build_full(source: Path, output: Path, cutoff: date) -> dict:
    """Build privately, validate all facts, and promote only after dbt tests pass."""
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((source / "manifest.json").read_text())
    for filename, entry in manifest["files"].items():
        if Path(filename).name != filename:
            raise ValueError("Manifest filenames must be local basenames")
        if hashlib.sha256((source / filename).read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"Source hash mismatch: {filename}")
    with tempfile.TemporaryDirectory(prefix="run-", dir=output) as scratch:
        work = Path(scratch)
        try:
            result = build(source / "requests.csv", work, cutoff)
            dbpath = (work / "hardship.duckdb").resolve()
            with duckdb.connect(str(dbpath)) as con:
                for name in TABLE_FIELDS:
                    con.execute(f"create table raw_{name} as select * from read_csv(?, all_varchar=true)", [str(source / f"{name}.csv")])
                con.execute("alter table run_metadata add column build_scope varchar default 'outcomes'")
                con.execute("alter table run_metadata add column quality_status varchar default 'passed'")
                con.execute("alter table run_metadata add column manifest_json varchar")
                con.execute("update run_metadata set manifest_json = ?", [json.dumps(manifest, sort_keys=True)])
            env = dict(os.environ, HARDSHIP_DB_PATH=dbpath.as_posix(), DBT_SEND_ANONYMOUS_USAGE_STATS="false")
            command = [sys.executable, "-m", "dbt.cli.main", "build", "--project-dir", str(ROOT / "dbt"), "--profiles-dir", str(ROOT / "dbt"), "--target-path", str(work / "target"), "--log-path", str(work / "logs"), "--vars", json.dumps({"cutoff": cutoff.isoformat()})]
            process = subprocess.run(command, env=env, capture_output=True, text=True)
            (output / "dbt-build.log").write_text(process.stdout + process.stderr, encoding="utf-8")
            if process.returncode:
                raise ValueError("dbt build/test failed; see dbt-build.log")
            with duckdb.connect(str(dbpath), read_only=True) as con:
                result["outcome_counts"] = dict(zip(["episodes", "mature", "missing_followup", "eligible", "stable"], con.execute("select count(*), count(*) filter(where mature), count(*) filter(where mature and not complete_followup), count(*) filter(where eligible), count(*) filter(where is_stable) from fct_episode_outcome").fetchone()))
            result["build_scope"] = "outcomes"
            # The database is the dashboard's single source of truth and publication unit.
            os.replace(dbpath, output / "hardship.duckdb")
            for name in ["manifest.json", "run_results.json"]:
                (output / f"dbt-{name}").write_bytes((work / "target" / name).read_bytes())
            (output / "submission_receipt.json").write_text(json.dumps({**result, "manifest": manifest}, indent=2) + "\n", encoding="utf-8")
            (output / "metrics.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            return result
        except Exception as error:
            (output / "submission_receipt.json").write_text(json.dumps({"status": "rejected", "build_scope": "outcomes", "error": str(error), "synthetic": True}, indent=2) + "\n", encoding="utf-8")
            raise
