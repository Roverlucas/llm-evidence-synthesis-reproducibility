"""Pairwise disagreement statistic (R3 Q3).

For each model × stage × item, compute fraction of run-pairs that disagree
(based on output_hash). With 10 runs, there are C(10,2)=45 pairs per item,
giving ~4.5x more power than whole-output EMR.

Output: analysis/blindage/pairwise_disagreement.json
"""
from __future__ import annotations

import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw_outputs"
OUT = ROOT / "analysis" / "blindage" / "pairwise_disagreement.json"

MODELS = ["llama3-8b", "mistral-7b", "gemma2-9b",
          "claude-sonnet-4-5", "gemini-2.5-pro", "gpt-4.1"]
STAGES = ["screening", "extraction"]


def pairwise_fraction(hashes_per_run: dict[int, str]) -> float:
    runs = sorted(hashes_per_run)
    if len(runs) < 2:
        return 0.0
    n_pairs = 0
    n_disagree = 0
    for a, b in combinations(runs, 2):
        n_pairs += 1
        if hashes_per_run[a] != hashes_per_run[b]:
            n_disagree += 1
    return n_disagree / n_pairs


def main() -> None:
    # per-model, per-stage: { item_id: { run_id: canonical_value } }
    # For screening, canonical = decision (consistent with paper EMR)
    # For extraction, canonical = output_hash (consistent with paper EMR)
    data = {m: {s: defaultdict(dict) for s in STAGES} for m in MODELS}

    for model in MODELS:
        for stage in STAGES:
            stage_dir = RAW / model / stage
            if not stage_dir.exists():
                continue
            for run_dir in sorted(stage_dir.iterdir()):
                if not run_dir.is_dir():
                    continue
                run_id = int(run_dir.name.split("_")[-1])
                res = run_dir / "results.json"
                if not res.exists():
                    continue
                for r in json.loads(res.read_text()):
                    item = r["corpus_id"]
                    if stage == "screening":
                        val = (r.get("output") or {}).get("decision", "ERROR")
                    else:
                        val = r.get("output_hash", "")
                    data[model][stage][item][run_id] = val

    report = {"metadata": {
        "method": "pairwise output_hash disagreement",
        "n_runs_target": 10,
        "n_pairs_per_item": 45,
    }, "models": {}}

    for model in MODELS:
        report["models"][model] = {}
        for stage in STAGES:
            fractions = []
            full_pair_items = 0
            n_items = 0
            for item, run_hashes in data[model][stage].items():
                n_items += 1
                if len(run_hashes) >= 10:
                    full_pair_items += 1
                frac = pairwise_fraction(run_hashes)
                fractions.append(frac)
            if not fractions:
                continue
            n = len(fractions)
            mean = sum(fractions) / n
            # Items with ANY disagreement
            items_with_any = sum(1 for f in fractions if f > 0)
            # Median and p95
            sorted_fracs = sorted(fractions)
            median = sorted_fracs[n // 2]
            p95 = sorted_fracs[min(n - 1, int(0.95 * n))]
            # Distribution bins
            bins = {"0%": 0, "(0%, 10%]": 0, "(10%, 25%]": 0,
                    "(25%, 50%]": 0, "(50%, 75%]": 0, "(75%, 100%]": 0}
            for f in fractions:
                if f == 0:
                    bins["0%"] += 1
                elif f <= 0.10:
                    bins["(0%, 10%]"] += 1
                elif f <= 0.25:
                    bins["(10%, 25%]"] += 1
                elif f <= 0.50:
                    bins["(25%, 50%]"] += 1
                elif f <= 0.75:
                    bins["(50%, 75%]"] += 1
                else:
                    bins["(75%, 100%]"] += 1
            report["models"][model][stage] = {
                "n_items": n_items,
                "n_items_full_10_runs": full_pair_items,
                "mean_pairwise_disagreement": round(mean, 4),
                "median_pairwise_disagreement": round(median, 4),
                "p95_pairwise_disagreement": round(p95, 4),
                "n_items_any_disagreement": items_with_any,
                "pct_items_any_disagreement": round(items_with_any / n, 4),
                "distribution": bins,
            }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2))
    # Print summary table
    print(f"{'Model':<20} {'Stage':<12} {'Mean Pair-Disagree':>20} {'% Items Any':>14}")
    for m in MODELS:
        for s in STAGES:
            r = report["models"].get(m, {}).get(s)
            if r:
                print(f"{m:<20} {s:<12} {r['mean_pairwise_disagreement']:>20.4f} {r['pct_items_any_disagreement']:>14.2%}")
    print(f"\nWrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
