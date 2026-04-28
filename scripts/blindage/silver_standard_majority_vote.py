"""Silver-internal: majority-vote consensus extraction from the 60K existing runs.

For each (corpus_id, field), compute the majority vote across all 6 models × 10 runs.
This produces a "wisdom of the crowd" silver standard that:
    1. Is free (uses data already collected)
    2. Is independent of any single model (majority across 60 measurements)
    3. Can be validated against human gold on the dual-labeling subset (25 INCLUDE items)

CAVEAT: this silver is NOT to be used as "gold" for accuracy metrics of the same
6 models — that would be circular. It IS legitimately used as:
    - Comparative anchor for cross-run stability analysis
    - Validation target: if silver ≈ human-gold on subset, silver is trustworthy for full 100
    - Benchmark for external silver (reasoning model) comparison

Output: analysis/blindage/silver_standard_internal.json
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LONG = ROOT / "analysis" / "blindage" / "extraction_long.json"
OUT = ROOT / "analysis" / "blindage" / "silver_standard_internal.json"

NUMERIC_FIELDS = ["effect_estimate", "ci_lower", "ci_upper"]
CATEGORICAL_FIELDS = ["effect_measure", "outcome_specific", "exposure_increment", "lag"]
NUMERIC_BIN = 0.01  # Round to nearest 0.01 for mode computation


def numeric_mode(values: list[float], bin_size: float = NUMERIC_BIN) -> tuple[float | None, int, int]:
    """Return (modal_value, n_at_mode, n_total_valid). Binning by rounding."""
    valid = []
    for v in values:
        if v is None:
            continue
        try:
            valid.append(round(float(v) / bin_size) * bin_size)
        except (TypeError, ValueError):
            continue
    if not valid:
        return None, 0, 0
    c = Counter(valid)
    mode, count = c.most_common(1)[0]
    return mode, count, len(valid)


def categorical_mode(values: list[str]) -> tuple[str | None, int, int]:
    valid = [v for v in values if v is not None and v != ""]
    if not valid:
        return None, 0, 0
    norm = [str(v).strip().lower() for v in valid]
    c = Counter(norm)
    mode, count = c.most_common(1)[0]
    return mode, count, len(norm)


def main() -> None:
    rows = json.loads(LONG.read_text())
    # Group by corpus_id; use first-estimate only (estimate_idx=0 or only estimate)
    by_item = defaultdict(list)
    for r in rows:
        if r["estimate_idx"] != 0:
            continue
        by_item[r["corpus_id"]].append(r)

    silver = {}
    fields_report = defaultdict(lambda: {"n_items_with_consensus": 0,
                                          "mean_agreement_at_mode": 0.0,
                                          "n_items_total": 0})
    for cid, records in by_item.items():
        consensus = {}
        item_report = {
            "n_total_records": len(records),
            "n_valid_by_field": {},
            "mode_agreement_by_field": {},
        }
        # Numeric fields
        for f in NUMERIC_FIELDS:
            vals = [r.get(f) for r in records]
            mode, count, n_valid = numeric_mode(vals)
            consensus[f] = mode
            item_report["n_valid_by_field"][f] = n_valid
            if n_valid > 0:
                item_report["mode_agreement_by_field"][f] = round(count / n_valid, 4)
                fields_report[f]["n_items_with_consensus"] += 1
                fields_report[f]["mean_agreement_at_mode"] += count / n_valid
            fields_report[f]["n_items_total"] += 1
        # Categorical fields
        for f in CATEGORICAL_FIELDS:
            vals = [r.get(f) for r in records]
            mode, count, n_valid = categorical_mode(vals)
            consensus[f] = mode
            item_report["n_valid_by_field"][f] = n_valid
            if n_valid > 0:
                item_report["mode_agreement_by_field"][f] = round(count / n_valid, 4)
                fields_report[f]["n_items_with_consensus"] += 1
                fields_report[f]["mean_agreement_at_mode"] += count / n_valid
            fields_report[f]["n_items_total"] += 1

        silver[cid] = {
            "consensus": consensus,
            "item_report": item_report,
        }

    # Normalize field-level averages
    for f, r in fields_report.items():
        if r["n_items_with_consensus"] > 0:
            r["mean_agreement_at_mode"] = round(
                r["mean_agreement_at_mode"] / r["n_items_with_consensus"], 4
            )

    report = {
        "method": "Majority-vote consensus across all 6 models × 10 runs (first-estimate).",
        "note": "Silver-internal. NOT to be used circularly; validate against human gold on subset.",
        "n_items": len(silver),
        "fields_report": dict(fields_report),
        "silver_by_item": silver,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2))

    print(f"Silver standard built for {len(silver)} items")
    print(f"\n{'Field':<25} {'Items w/ consensus':>20} {'Mean mode-agreement':>22}")
    for f, r in fields_report.items():
        print(f"{f:<25} {r['n_items_with_consensus']:>20} {r['mean_agreement_at_mode']:>22.4f}")
    print(f"\nWrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
