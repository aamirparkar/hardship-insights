import argparse
import json
from datetime import date
from pathlib import Path

from hardship_insights.generate import generate
from hardship_insights.pipeline import build
from hardship_insights.outcomes import generate_outcomes, build_full


def main():
    parser = argparse.ArgumentParser(description="Generate and validate SYNTHETIC support requests")
    parser.add_argument("--config", type=Path, default=Path("config/simulation.json"))
    parser.add_argument("--output", type=Path, default=Path("data"))
    parser.add_argument("--submission", type=Path, help="Validate/build an existing schema-1.0 synthetic CSV")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if args.submission:
        source = args.submission
    else:
        generate(config, args.output / "synthetic")
        generate_outcomes(config, args.output / "synthetic")
        source = args.output / "synthetic" / "requests.csv"
    builder = build if args.submission else build_full
    result = builder(source if args.submission else source.parent, args.output / "warehouse", date.fromisoformat(config["cutoff"]))
    print(f"SYNTHETIC: accepted {result['rows']} requests; {len(result['metrics'])} market/product cohorts")
    print(f"Metrics: {args.output / 'warehouse' / 'metrics.json'}")


if __name__ == "__main__":
    main()
