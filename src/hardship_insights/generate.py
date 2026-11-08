"""Generate deterministic submissions; assumptions are illustrative, never estimated."""

import csv
import hashlib
import json
import random
from datetime import date, timedelta
from pathlib import Path

FIELDS = [
    "request_id", "customer_id", "institution_id", "jurisdiction", "currency",
    "product", "channel", "notice_date", "days_past_due", "status",
    "decision_date", "closure_date",
]
PRODUCTS = ["mortgage", "personal_loan", "auto_loan", "credit_card"]


def generate(config: dict, output: Path) -> dict:
    """Write a single request per selected customer and a content-addressed manifest."""
    cutoff = date.fromisoformat(config["cutoff"])
    start = date.fromisoformat(config["start_date"])
    if start > cutoff or not isinstance(config["customers"], int) or config["customers"] < 1:
        raise ValueError("Require a positive customer count and start_date <= cutoff")
    assumptions = config["assumptions"]
    for value in assumptions.values():
        if not 0 <= value <= 1:
            raise ValueError("Probabilities must be between zero and one")
    rng = random.Random(config["seed"])
    output.mkdir(parents=True, exist_ok=True)
    path = output / "requests.csv"
    count = 0
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        for customer in range(1, config["customers"] + 1):
            if rng.random() >= assumptions["request_probability"]:
                continue
            count += 1
            market = rng.choice(["AU", "UK"])
            notice = start + timedelta(days=rng.randint(0, (cutoff - start).days))
            terminal = notice + timedelta(days=rng.randint(1, 35))
            withdrawn = rng.random() < assumptions["withdrawal_probability"]
            approved = rng.random() < assumptions["approval_probability_after_nonwithdrawal"]
            status = "withdrawn" if withdrawn else ("approved" if approved else "declined")
            if terminal > cutoff:
                status = "pending"
            arrears = "" if rng.random() < assumptions["unknown_arrears_probability"] else rng.choice([0, 0, 0, 15, 30, 60, 90])
            writer.writerow({
                "request_id": f"R{count:07d}", "customer_id": f"C{customer:07d}",
                "institution_id": f"{market}_FICTIONAL_{rng.randint(1, 3)}",
                "jurisdiction": market, "currency": "AUD" if market == "AU" else "GBP",
                "product": rng.choice(PRODUCTS), "channel": rng.choice(["web", "phone", "branch"]),
                "notice_date": notice.isoformat(), "days_past_due": arrears, "status": status,
                "decision_date": terminal.isoformat() if status in {"approved", "declined"} else "",
                "closure_date": terminal.isoformat() if status == "withdrawn" else "",
            })
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    manifest = {
        "synthetic": True, "generator_version": "0.1.0", "config": config,
        "config_sha256": config_hash, "files": {"requests.csv": {"sha256": digest, "rows": count}},
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
