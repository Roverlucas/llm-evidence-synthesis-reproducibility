"""Analyze fixed-slot extraction results vs variable-length baseline (P1.2).

Compares EMR (output_hash-based) of fixed-slot extraction (3 runs × 100 items)
against the variable-length original (10 runs × 100 items).

Output: analysis/blindage/fixed_slot_comparison.json
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw_outputs"
REPRO = ROOT / "analysis" / "reproducibility_results.json"
OUT = ROOT / "analysis" / "blindage" / "fixed_slot_comparison.json"

FIXED_SLOT_MODELS = {
    "claude-sonnet-4-5-fixedslot": "claude-sonnet-4-5",
    "gemini-2.5-pro-fixedslot": "gemini-2.5-pro",
    "gpt-4.1-fixedslot": "gpt-4.1",
}


def load_extraction_runs(model_dir: str) -> dict[int, dict[str, str]]:
    """Returns {run_id: {corpus_id: output_hash}}."""
    out = {}
    ext_dir = RAW / model_dir / "extraction"
    if not ext_dir.exists():
        return out
    for run_dir in sorted(ext_dir.iterdir()):
        if not run_dir.is_dir():
            continue
        run_id = int(run_dir.name.split("_")[-1])
        results = run_dir / "results.json"
        if not results.exists():
            continue
        records = json.loads(results.read_text())
        run_data = {r["corpus_id"]: r.get("output_hash") for r in records if r.get("valid")}
        out[run_id] = run_data
    return out


def emr(runs: dict[int, dict[str, str]]) -> tuple[float, int, int]:
    if not runs:
        return None, 0, 0
    items = set.intersection(*[set(d.keys()) for d in runs.values()])
    items = [i for i in items if all(runs[r][i] is not None for r in runs)]
    n = len(items)
    if n == 0:
        return None, 0, 0
    matches = sum(1 for i in items if len(set(runs[r][i] for r in runs)) == 1)
    return matches / n, matches, n


def pairwise_disagreement(runs: dict[int, dict[str, str]]) -> float | None:
    if len(runs) < 2:
        return None
    items_any = set()
    for r in runs:
        items_any.update(runs[r].keys())
    fractions = []
    for item in items_any:
        decs = [runs[r].get(item) for r in runs if runs[r].get(item) is not None]
        if len(decs) < 2:
            continue
        n_pairs = 0
        n_dis = 0
        for a, b in combinations(decs, 2):
            n_pairs += 1
            if a != b:
                n_dis += 1
        fractions.append(n_dis / n_pairs)
    return sum(fractions) / len(fractions) if fractions else None


def main():
    repro = json.loads(REPRO.read_text())
    report = {
        "method": "Compare fixed-slot extraction (single primary_estimate) vs variable-length array baseline.",
        "comparison_per_model": {},
    }
    for fs_model, base_model in FIXED_SLOT_MODELS.items():
        fs_runs = load_extraction_runs(fs_model)
        baseline = repro[base_model]["extraction"]
        baseline_emr = baseline["emr"]
        baseline_field_emr = baseline.get("field_emr", {})
        baseline_estimate_count_stability = baseline.get("estimate_count_stability")
        fs_emr_pt, fs_match, fs_n = emr(fs_runs)
        fs_pair_dis = pairwise_disagreement(fs_runs)
        delta_abs = (fs_emr_pt - baseline_emr) if fs_emr_pt is not None else None
        delta_rel = (delta_abs / baseline_emr * 100) if (delta_abs is not None and baseline_emr > 0) else None
        report["comparison_per_model"][fs_model] = {
            "baseline_model": base_model,
            "baseline_emr_variable_length": round(baseline_emr, 4),
            "baseline_n_articles": baseline.get("n_articles"),
            "baseline_n_runs": 10,
            "fixed_slot_emr": round(fs_emr_pt, 4) if fs_emr_pt is not None else None,
            "fixed_slot_n_articles": fs_n,
            "fixed_slot_n_runs": len(fs_runs),
            "delta_emr_absolute": round(delta_abs, 4) if delta_abs is not None else None,
            "delta_emr_relative_pct": round(delta_rel, 2) if delta_rel is not None else None,
            "fixed_slot_pairwise_disagreement": round(fs_pair_dis, 4) if fs_pair_dis is not None else None,
            "interpretation": (
                "FIXED-SLOT REDUCES NON-DETERMINISM" if delta_abs is not None and delta_abs > 0.1
                else "FIXED-SLOT MINIMALLY CHANGES NON-DETERMINISM" if delta_abs is not None and abs(delta_abs) <= 0.1
                else "FIXED-SLOT INCREASES NON-DETERMINISM" if delta_abs is not None
                else "INSUFFICIENT DATA"
            ),
        }

    # Summary
    deltas = [r["delta_emr_absolute"] for r in report["comparison_per_model"].values()
              if r["delta_emr_absolute"] is not None]
    if deltas:
        report["summary"] = {
            "mean_delta_emr": round(sum(deltas) / len(deltas), 4),
            "interpretation_overall": (
                f"Across 3 cloud models, fixed-slot extraction changes EMR by an average of "
                f"{sum(deltas)/len(deltas):+.4f}. "
                f"This is {'a meaningful reduction in non-determinism' if sum(deltas)/len(deltas) > 0.1 else 'a minor change'}, "
                f"suggesting that prompt-design "
                f"{'IS a major contributor' if sum(deltas)/len(deltas) > 0.1 else 'is NOT the sole contributor'} "
                f"to extraction non-determinism."
            ),
        }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2))

    print(f"{'Model':<35} {'Baseline EMR':>14} {'Fixed-slot EMR':>16} {'Δ abs':>10} {'Δ rel':>10}")
    for fs_model, r in report["comparison_per_model"].items():
        b = r["baseline_emr_variable_length"]
        f = r["fixed_slot_emr"]
        da = r["delta_emr_absolute"]
        dr = r["delta_emr_relative_pct"]
        print(f"{fs_model:<35} {b:>14.4f} {f:>16.4f} {da:>+10.4f} {dr:>+9.1f}%")
    print()
    if "summary" in report:
        print(f"Mean Δ EMR: {report['summary']['mean_delta_emr']:+.4f}")
        print(report["summary"]["interpretation_overall"])
    print(f"\nWrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
