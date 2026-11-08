import csv
import hashlib
import json
from datetime import date
from pathlib import Path

import duckdb
import pytest
from streamlit.testing.v1 import AppTest

from hardship_insights.generate import generate
from hardship_insights.export_demo import export_demo
from hardship_insights.outcomes import TABLE_FIELDS, build_full, generate_outcomes
from test_pipeline import write_requests


def write_csv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        writer.writerows(rows)


def refresh_manifest(source):
    files = {}
    for path in source.glob("*.csv"):
        with path.open(newline="") as file:
            count = len(list(csv.reader(file))) - 1
        files[path.name] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "rows": count}
    (source / "manifest.json").write_text(json.dumps({"synthetic": True, "config": {}, "files": files}))


@pytest.fixture(scope="module")
def outcome_run(tmp_path_factory):
    root = tmp_path_factory.mktemp("outcome-run")
    source = root / "source"
    source.mkdir()
    write_requests(source / "requests.csv", [{"notice_date": "2026-06-01", "status": "approved", "decision_date": "2026-06-03"} for _ in range(5)])
    write_csv(source / "accounts.csv", TABLE_FIELDS["accounts"], [[f"A{i}", f"R{i}", f"C{i}", "mortgage", "AUD", 2000] for i in range(5)])
    ends = ["2026-07-31", "2026-07-31", "2026-08-31", "2026-07-31", "2026-07-30"]
    write_csv(source / "assistance.csv", TABLE_FIELDS["assistance"], [[f"E{i}", f"R{i}", f"A{i}", "2026-06-03", end, "reduced_payment"] for i, end in enumerate(ends)])
    months = []
    for i in range(5):
        for month in ["2026-07-31", "2026-08-31", "2026-09-30", "2026-10-31"]:
            missing = i == 1 and month == "2026-09-30"
            dpd = 30 if i == 3 and month == "2026-09-30" else 0
            months.append([f"A{i}", month, str(not missing).lower(), "" if missing else dpd, 2000, "" if missing else (0 if dpd else 2000)])
    write_csv(source / "account_months.csv", TABLE_FIELDS["account_months"], months)
    refresh_manifest(source)
    result = build_full(source, root / "warehouse", date(2026, 10, 31))
    return root, source, result


def test_maturity_missingness_and_midmonth_boundary(outcome_run):
    root, _, result = outcome_run
    assert result["outcome_counts"] == {"episodes": 5, "mature": 4, "missing_followup": 1, "eligible": 3, "stable": 2}
    with duckdb.connect(str(root / "warehouse/hardship.duckdb"), read_only=True) as con:
        rows = con.execute("select episode_id, mature, observed_months, eligible, is_stable from fct_episode_outcome order by episode_id").fetchall()
        assert rows == [("E0", True, 3, True, True), ("E1", True, 2, False, False), ("E2", False, 2, False, False), ("E3", True, 3, True, False), ("E4", True, 3, True, True)]
        assert con.execute("select stability_rate, followup_coverage from mart_outcomes").fetchone() == pytest.approx((2 / 3, 3 / 4))


def test_invalid_account_month_blocks_publication(outcome_run):
    root, source, _ = outcome_run
    before = (root / "warehouse/hardship.duckdb").read_bytes()
    content = (source / "account_months.csv").read_text()
    # A duplicated key must fail even if the manifest accurately hashes the bad file.
    with (source / "account_months.csv").open("a") as file:
        file.write(content.splitlines()[1] + "\n")
    refresh_manifest(source)
    with pytest.raises(ValueError, match="dbt build/test failed"):
        build_full(source, root / "warehouse", date(2026, 10, 31))
    assert (root / "warehouse/hardship.duckdb").read_bytes() == before


def test_outcome_generation_is_deterministic(tmp_path):
    config = json.loads(Path("config/simulation.json").read_text())
    config["customers"] = 50
    generate(config, tmp_path / "a")
    generate(config, tmp_path / "b")
    assert generate_outcomes(config, tmp_path / "a") == generate_outcomes(config, tmp_path / "b")


def test_dashboard_filters_and_suppression(outcome_run, monkeypatch):
    root, _, _ = outcome_run
    monkeypatch.setenv("HARDSHIP_DASHBOARD_DB", str(root / "warehouse/hardship.duckdb"))
    app = AppTest.from_file(Path("dashboard/app.py").resolve()).run(timeout=30)
    assert not app.exception
    assert any(item.value == "Unavailable" for item in app.metric)
    app.sidebar.multiselect[1].set_value(["mortgage"]).run()
    assert not app.exception
    assert app.metric[0].value == "5"
    app.sidebar.multiselect[1].set_value([]).run()
    assert not app.exception
    assert any("No requests" in item.value for item in app.info)
    app.sidebar.multiselect[1].set_value(["mortgage"]).run()
    app.sidebar.multiselect[0].set_value(["UK"]).run()
    assert not app.exception
    assert any("No requests" in item.value for item in app.info)


def test_public_snapshot_matches_database(outcome_run, tmp_path, monkeypatch):
    root, _, _ = outcome_run
    snapshot = tmp_path / "snapshot.json.gz"
    payload = export_demo(root / "warehouse/hardship.duckdb", snapshot)
    first = snapshot.read_bytes()
    export_demo(root / "warehouse/hardship.duckdb", snapshot)
    assert first == snapshot.read_bytes()
    assert len(payload["applications"]) == 5
    assert sum(row["is_stable"] for row in payload["outcomes"]) == 2
    assert all("customer_id" not in row for row in payload["applications"])
    monkeypatch.setenv("HARDSHIP_DEMO_MODE", "1")
    monkeypatch.setenv("HARDSHIP_DEMO_SNAPSHOT_PATH", str(snapshot))
    app = AppTest.from_file(Path("dashboard/app.py").resolve()).run(timeout=30)
    assert not app.exception
    assert app.metric[0].value == "5"
