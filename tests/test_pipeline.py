import copy
import csv
import json
from datetime import date
from pathlib import Path

import duckdb
import pytest

from hardship_insights.generate import FIELDS, generate
from hardship_insights.pipeline import build


def config():
    value = json.loads(Path("config/simulation.json").read_text())
    value["customers"] = 300
    return value


def write_requests(path, overrides):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for index, values in enumerate(overrides):
            row = dict.fromkeys(FIELDS, "")
            row.update(request_id=f"R{index}", customer_id=f"C{index}", institution_id="AU_FICTIONAL_1",
                       jurisdiction="AU", currency="AUD", product="mortgage", channel="phone",
                       notice_date="2026-10-01", days_past_due="0", status="pending")
            row.update(values)
            writer.writerow(row)


def test_reproducible_sources_and_metrics(tmp_path):
    first = generate(config(), tmp_path / "a")
    second = generate(config(), tmp_path / "b")
    assert first == second
    a = build(tmp_path / "a/requests.csv", tmp_path / "wa", date(2026, 10, 31))
    b = build(tmp_path / "b/requests.csv", tmp_path / "wb", date(2026, 10, 31))
    assert a == b
    changed = copy.deepcopy(config())
    changed["seed"] += 1
    assert generate(changed, tmp_path / "c")["files"] != first["files"]


def test_golden_denominators_and_reconciliation(tmp_path):
    source = tmp_path / "input.csv"
    write_requests(source, [
        {"status": "approved", "decision_date": "2026-10-03"},
        {"status": "declined", "decision_date": "2026-10-07", "days_past_due": "30"},
        {"status": "withdrawn", "closure_date": "2026-10-04", "days_past_due": ""},
        {"status": "pending"},
    ])
    result = build(source, tmp_path / "warehouse", date(2026, 10, 31))
    metric = result["metrics"][0]
    assert metric["requests"] == 4
    assert sum(metric[key] for key in ["approved", "declined", "dropout", "pending"]) == 4
    assert metric["dropout_rate"] == 0.25
    assert metric["arrears_observed"] == 3
    assert metric["arrears_unknown"] == 1
    assert metric["early_contact_rate"] == pytest.approx(2 / 3)
    assert metric["decision_days_median"] == 4
    assert metric["pending_age_days_median"] == 30


@pytest.mark.parametrize("bad", [
    {"notice_date": "2026-11-01"},
    {"status": "approved", "decision_date": "2026-09-30"},
    {"status": "pending", "decision_date": "2026-10-02"},
    {"days_past_due": "-1"}, {"currency": "GBP"}, {"product": "unknown"},
    {"notice_date": "bad-date"}, {"customer_id": ""},
])
def test_rejection_preserves_published_database(tmp_path, bad):
    source = tmp_path / "input.csv"
    warehouse = tmp_path / "warehouse"
    write_requests(source, [{}])
    build(source, warehouse, date(2026, 10, 31))
    before = (warehouse / "hardship.duckdb").read_bytes()
    write_requests(source, [bad])
    with pytest.raises(ValueError, match="rejected"):
        build(source, warehouse, date(2026, 10, 31))
    assert (warehouse / "hardship.duckdb").read_bytes() == before
    assert json.loads((warehouse / "submission_receipt.json").read_text())["status"] == "rejected"
    with duckdb.connect(str(warehouse / "hardship.duckdb"), read_only=True) as con:
        assert con.execute("select count(*) from fct_application").fetchone()[0] == 1


def test_empty_denominator_and_duplicate_rejection(tmp_path):
    source = tmp_path / "input.csv"
    write_requests(source, [{"days_past_due": ""}])
    result = build(source, tmp_path / "w", date(2026, 10, 31))
    assert result["metrics"][0]["early_contact_rate"] is None
    assert result["metrics"][0]["decision_days_median"] is None
    write_requests(source, [{}, {"request_id": "R0"}])
    with pytest.raises(ValueError):
        build(source, tmp_path / "w", date(2026, 10, 31))
