"""Build silver-external consensus from DeepSeek-R1 5-run extraction (Camada 2).

For each (corpus_id, field), compute majority vote across 5 R1 runs.
Output is a 100-item silver standard from a model FAMILY DIFFERENT from
the 6 evaluated models, providing an independent reference.

Output: analysis/blindage/silver_standard_external.json
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw_outputs" / "deepseek-r1-silver" / "extraction"
OUT = ROOT / "analysis" / "blindage" / "silver_standard_external.json"

NUMERIC_FIELDS = ["effect_estimate", "ci_lower", "ci_upper"]
CATEGORICAL_FIELDS = ["effect_measure", "outcome_specific", "exposure_increment", "lag"]
NUMERIC_BIN = 0.01


def numeric_mode(values, bin_size=NUMERIC_BIN):
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


def categorical_mode(values):
    valid = [str(v).strip().lower() for v in values if v is not None and str(v).strip()]
    if not valid:
        return None, 0, 0
    c = Counter(valid)
    mode, count = c.most_common(1)[0]
    return mode, count, len(valid)


def main():
    by_item = defaultdict(list)
    for run_dir in sorted(RAW.iterdir()) if RAW.exists() else []:
        if not run_dir.is_dir():
            continue
        results = run_dir / "results.json"
        if not results.exists():
            continue
        for r in json.loads(results.read_text()):
            cid = r["corpus_id"]
            out = r.get("output") or {}
            ests = out.get("estimates") or []
            # First valid estimate
            first_est = next((e for e in ests if e.get("effect_estimate") is not None), {})
            row = {f: first_est.get(f) for f in NUMERIC_FIELDS + CATEGORICAL_FIELDS}
            row["n_estimates"] = len(ests)
            row["study_id"] = out.get("study_id")
            row["study_location"] = out.get("study_location")
            row["valid"] = r.get("valid", False) and bool(first_est)
            by_item[cid].append(row)

    silver = {}
    field_stats = {f: {"n_with_consensus": 0, "mean_agreement": 0.0}
                   for f in NUMERIC_FIELDS + CATEGORICAL_FIELDS}
    for cid, rows in by_item.items():
        consensus = {}
        per_field = {}
        for f in NUMERIC_FIELDS:
            mode, count, n_valid = numeric_mode([r[f] for r in rows])
            consensus[f] = mode
            if n_valid > 0:
                per_field[f] = round(count / n_valid, 4)
                field_stats[f]["n_with_consensus"] += 1
                field_stats[f]["mean_agreement"] += count / n_valid
        for f in CATEGORICAL_FIELDS:
            mode, count, n_valid = categorical_mode([r[f] for r in rows])
            consensus[f] = mode
            if n_valid > 0:
                per_field[f] = round(count / n_valid, 4)
                field_stats[f]["n_with_consensus"] += 1
                field_stats[f]["mean_agreement"] += count / n_valid
        silver[cid] = {"consensus": consensus, "field_agreement": per_field, "n_valid_runs": len(rows)}

    for f, s in field_stats.items():
        if s["n_with_consensus"]:
            s["mean_agreement"] = round(s["mean_agreement"] / s["n_with_consensus"], 4)

    report = {
        "method": "Majority-vote consensus across DeepSeek-R1 (deepseek-reasoner) 5 runs.",
        "purpose": "Independent silver-external standard from a different model family (not in the 6 evaluated).",
        "n_items": len(silver),
        "n_runs_per_item": 5,
        "fields_report": field_stats,
        "silver_by_item": silver,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2))

    print(f"Silver-external built for {len(silver)} items from DeepSeek-R1 5 runs")
    print(f"\n{'Field':<25} {'Items w/ consensus':>20} {'Mean mode-agreement':>22}")
    for f, s in field_stats.items():
        print(f"{f:<25} {s['n_with_consensus']:>20} {s['mean_agreement']:>22.4f}")
    print(f"\nWrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
