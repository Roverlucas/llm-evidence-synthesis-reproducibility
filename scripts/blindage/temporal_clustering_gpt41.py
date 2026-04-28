"""Temporal clustering of GPT-4.1 flipping abstracts (R1 Q3).

For each screening abstract that "flipped" (decision changed across runs),
analyze timestamps to detect whether flips cluster by:
    - calendar date
    - hour of day
    - run batch

Clustering would implicate server-side drift; absence partially rules it out.

Output: analysis/blindage/gpt41_temporal.json
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw_outputs" / "gpt-4.1"
OUT = ROOT / "analysis" / "blindage" / "gpt41_temporal.json"


def main() -> None:
    # Build: { corpus_id: { run_id: (decision, timestamp) } }
    by_item = defaultdict(dict)
    for run_dir in sorted((RAW / "screening").iterdir()):
        if not run_dir.is_dir():
            continue
        run_id = int(run_dir.name.split("_")[-1])
        results = json.loads((run_dir / "results.json").read_text())
        calls = json.loads((run_dir / "call_records.json").read_text())
        # Map corpus_id -> timestamp from calls
        ts_map = {c["corpus_id"]: c.get("timestamp") for c in calls}
        for r in results:
            cid = r["corpus_id"]
            decision = (r.get("output") or {}).get("decision", "ERROR")
            ts = ts_map.get(cid)
            by_item[cid][run_id] = (decision, ts)

    # Identify flipping items (decision changes across runs)
    flipping = {}
    for cid, runs in by_item.items():
        decisions = [v[0] for v in runs.values()]
        if len(set(decisions)) > 1:
            flipping[cid] = runs

    # Temporal analysis
    report = {
        "model": "gpt-4.1",
        "stage": "screening",
        "n_items_total": len(by_item),
        "n_items_flipping": len(flipping),
        "flipping_items": {},
        "date_histogram_flips": defaultdict(int),
        "hour_histogram_flips": defaultdict(int),
        "date_histogram_all_calls": defaultdict(int),
        "hour_histogram_all_calls": defaultdict(int),
    }

    for cid, runs in flipping.items():
        item_detail = {}
        for run_id, (decision, ts) in sorted(runs.items()):
            item_detail[run_id] = {"decision": decision, "timestamp": ts}
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    report["date_histogram_flips"][dt.strftime("%Y-%m-%d")] += 1
                    report["hour_histogram_flips"][dt.strftime("%H")] += 1
                except Exception:
                    pass
        report["flipping_items"][cid] = item_detail

    # All calls histogram (baseline)
    for cid, runs in by_item.items():
        for run_id, (decision, ts) in runs.items():
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    report["date_histogram_all_calls"][dt.strftime("%Y-%m-%d")] += 1
                    report["hour_histogram_all_calls"][dt.strftime("%H")] += 1
                except Exception:
                    pass

    # Test for clustering (chi-sq vs uniform on all-calls distribution)
    import math
    flip_dates = report["date_histogram_flips"]
    all_dates = report["date_histogram_all_calls"]
    total_flips = sum(flip_dates.values())
    total_all = sum(all_dates.values())
    if total_flips > 0 and total_all > 0:
        chi_sq = 0.0
        dates = sorted(all_dates)
        for d in dates:
            expected = total_flips * (all_dates[d] / total_all)
            observed = flip_dates.get(d, 0)
            if expected > 0:
                chi_sq += (observed - expected) ** 2 / expected
        df = len(dates) - 1
        # No scipy; use Wilson-Hilferty approx for chi-sq p-value
        # Approximation: for large df, ((chi_sq/df)^(1/3) - (1 - 2/(9*df))) / sqrt(2/(9*df)) ~ N(0,1)
        if df > 0:
            z = ((chi_sq / df) ** (1 / 3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
            # p-value (two-tailed normal)
            import math as m
            p = 0.5 * (1 + m.erf(z / m.sqrt(2)))
            p_approx = 1 - p  # upper tail
        else:
            z = None
            p_approx = None
        report["clustering_test"] = {
            "method": "Chi-squared goodness-of-fit (expected = all-calls date distribution)",
            "chi_sq": round(chi_sq, 4),
            "df": df,
            "wilson_hilferty_z": round(z, 4) if z is not None else None,
            "p_value_approx": round(p_approx, 4) if p_approx is not None else None,
            "interpretation": (
                "p < 0.05 would indicate temporal clustering (server-side drift likely)"
                if p_approx is not None and p_approx < 0.05
                else "No strong temporal clustering detected"
            ),
        }

    # Convert defaultdicts to dicts for JSON
    for k in ("date_histogram_flips", "hour_histogram_flips",
              "date_histogram_all_calls", "hour_histogram_all_calls"):
        report[k] = dict(report[k])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, default=str))

    print(f"GPT-4.1 screening: {report['n_items_flipping']}/{report['n_items_total']} items flipping")
    print(f"Flip date distribution: {sorted(report['date_histogram_flips'].items())}")
    if "clustering_test" in report:
        c = report["clustering_test"]
        print(f"Chi-sq = {c['chi_sq']}  df = {c['df']}  p ~ {c['p_value_approx']}")
        print(f"  {c['interpretation']}")
    print(f"\nWrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
