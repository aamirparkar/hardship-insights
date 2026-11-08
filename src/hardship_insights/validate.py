"""Fail closed: invalid submissions never reach analytical tables."""

import csv
from datetime import date
from pathlib import Path

from hardship_insights.generate import FIELDS, PRODUCTS


def validate(path: Path, cutoff: date) -> tuple[list[dict], list[dict]]:
    rows, errors, seen, customers = [], [], set(), set()
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            return [], [{"row": 1, "field": "header", "error": "Schema 1.0 column names/order required"}]
        for line, row in enumerate(reader, 2):
            rows.append(row)

            def fail(field, message):
                errors.append({"row": line, "field": field, "error": message})

            if None in row or any(value is None for value in row.values()):
                fail("row", "Wrong number of columns")
                continue
            for field in ["request_id", "customer_id", "institution_id"]:
                if not row[field].strip():
                    fail(field, "Required identifier")
            for field, keys in [("request_id", seen), ("customer_id", customers)]:
                if row[field] in keys:
                    fail(field, "Duplicate identifier; v1 supports one request per customer")
                keys.add(row[field])
            for field, allowed in {
                "jurisdiction": {"AU", "UK"}, "product": set(PRODUCTS),
                "channel": {"web", "phone", "branch"},
                "status": {"approved", "declined", "withdrawn", "lost_contact", "pending"},
            }.items():
                if row[field] not in allowed:
                    fail(field, "Unrecognised value")
            if row["currency"] != {"AU": "AUD", "UK": "GBP"}.get(row["jurisdiction"]):
                fail("currency", "Currency must match jurisdiction")
            if row["days_past_due"]:
                try:
                    if int(row["days_past_due"]) < 0:
                        raise ValueError
                except ValueError:
                    fail("days_past_due", "Expected non-negative integer or empty for unknown")
            dates = {}
            for field in ["notice_date", "decision_date", "closure_date"]:
                if not row[field]:
                    continue
                try:
                    dates[field] = date.fromisoformat(row[field])
                    if dates[field] > cutoff:
                        fail(field, "After observation cutoff")
                except ValueError:
                    fail(field, "Expected ISO date YYYY-MM-DD")
            if not row["notice_date"]:
                fail("notice_date", "Required")
            for field in ["decision_date", "closure_date"]:
                if field in dates and "notice_date" in dates and dates[field] < dates["notice_date"]:
                    fail(field, "Before notice date")
            decided = row["status"] in {"approved", "declined"}
            closed = row["status"] in {"withdrawn", "lost_contact"}
            if bool(row["decision_date"]) != decided:
                fail("decision_date", "Required only for approved/declined requests")
            if bool(row["closure_date"]) != closed:
                fail("closure_date", "Required only for withdrawn/lost-contact requests")
    return rows, errors
