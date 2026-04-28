"""Per-run extraction accuracy against multiple gold standard sources (R4 Q11).

Computes accuracy for each (model × run × field) against:
    1. silver_internal — majority vote of 6 models × 10 runs (already built)
    2. silver_external — DeepSeek-R1 majority of 5 runs (TBD when DeepSeek finishes)
    3. human_gold      — dual-human extraction on 25 INCLUDE items (TBD when labelers done)

Outputs accuracy matrices that allow:
    - Cross-source validation (does silver-internal agree with human gold?)
    - Per-run accuracy variation (does Run 3 of Claude differ from Run 7?)
    - Independent benchmark for each cloud model

Output: analysis/blindage/per_run_accuracy_multi.json
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SILVER_INT = ROOT / "analysis" / "blindage" / "silver_standard_internal.json"
SILVER_EXT = ROOT / "analysis" / "blindage" / "silver_standard_external.json"
HUMAN_GOLD = ROOT / "data" / "dual_labeling" / "extraction_gold_25_final.json"
LONG = ROOT / "analysis" / "blindage" / "extraction_long.json"
OUT = ROOT / "analysis" / "blindage" / "per_run_accuracy_multi.json"

NUMERIC_FIELDS = ["effect_estimate", "ci_lower", "ci_upper"]
CATEGORICAL_FIELDS = ["effect_measure", "outcome_specific", "exposure_increment", "lag"]
NUMERIC_TOL = 0.01

MODELS = ["llama3-8b", "mistral-7b", "gemma2-9b",
          "claude-sonnet-4-5", "gemini-2.5-pro", "gpt-4.1"]


def numeric_match(a, b, tol=NUMERIC_TOL):
    if a is None or b is None:
        return False
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def cat_match(a, b):
    if a is None or b is None:
        return False
    return str(a).strip().lower() == str(b).strip().lower()


def load_silver_internal() -> dict:
    """Returns {corpus_id: consensus_dict_of_fields}."""
    if not SILVER_INT.exists():
        return {}
    raw = json.loads(SILVER_INT.read_text())
    return {cid: r["consensus"] for cid, r in raw["silver_by_item"].items()}


def load_silver_external() -> dict:
    """Returns {corpus_id: consensus_from_deepseek_r1_5runs} when ready."""
    if not SILVER_EXT.exists():
        return {}
    raw = json.loads(SILVER_EXT.read_text())
    if "silver_by_item" in raw:
        return {cid: r["consensus"] for cid, r in raw["silver_by_item"].items()}
    return raw


def load_human_gold() -> dict:
    if not HUMAN_GOLD.exists():
        return {}
    raw = json.loads(HUMAN_GOLD.read_text())
    return {item["corpus_id"]: item["extraction"] for item in raw.get("items", [])}


def compute_accuracy(rows: list[dict], gold_map: dict) -> dict:
    """Per (model, run): accuracy against given gold."""
    by_model_run = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r["estimate_idx"] != 0:
            continue
        cid = r["corpus_id"]
        if cid not in gold_map:
            continue
        gold = gold_map[cid]
        # Compare each field
        scores = {}
        for f in NUMERIC_FIELDS:
            scores[f] = 1 if numeric_match(r.get(f), gold.get(f)) else 0
        for f in CATEGORICAL_FIELDS:
            scores[f] = 1 if cat_match(r.get(f), gold.get(f)) else 0
        scores["all_fields"] = 1 if all(scores.values()) else 0
        by_model_run[r["model"]][r["run_id"]].append(scores)

    # Aggregate
    results = {}
    for model in MODELS:
        if model not in by_model_run:
            continue
        runs_data = by_model_run[model]
        per_run = {}
        for run_id, items in sorted(runs_data.items()):
            n = len(items)
            agg = {f: sum(it[f] for it in items) / n for f in (
                NUMERIC_FIELDS + CATEGORICAL_FIELDS + ["all_fields"]
            )}
            per_run[str(run_id)] = {"n": n, **{k: round(v, 4) for k, v in agg.items()}}
        # Summary across runs
        all_acc = {f: [per_run[r][f] for r in per_run] for f in (
            NUMERIC_FIELDS + CATEGORICAL_FIELDS + ["all_fields"]
        )}
        summary = {}
        for f, vals in all_acc.items():
            if vals:
                summary[f] = {
                    "mean": round(sum(vals) / len(vals), 4),
                    "min": round(min(vals), 4),
                    "max": round(max(vals), 4),
                    "range": round(max(vals) - min(vals), 4),
                }
        results[model] = {"per_run": per_run, "summary_across_runs": summary}
    return results


def main():
    rows = json.loads(LONG.read_text())
    silver_int = load_silver_internal()
    silver_ext = load_silver_external()
    human = load_human_gold()

    report = {
        "method": "Per-run accuracy of each model × run against three gold standards.",
        "sources": {
            "silver_internal": {"available": bool(silver_int), "n_items": len(silver_int)},
            "silver_external": {"available": bool(silver_ext), "n_items": len(silver_ext)},
            "human_gold": {"available": bool(human), "n_items": len(human)},
        },
        "fields_evaluated": NUMERIC_FIELDS + CATEGORICAL_FIELDS + ["all_fields"],
        "numeric_tolerance": NUMERIC_TOL,
    }

    if silver_int:
        report["accuracy_vs_silver_internal"] = compute_accuracy(rows, silver_int)
    if silver_ext:
        report["accuracy_vs_silver_external"] = compute_accuracy(rows, silver_ext)
    if human:
        report["accuracy_vs_human_gold"] = compute_accuracy(rows, human)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2))

    print(f"Sources available:")
    for k, v in report["sources"].items():
        flag = "✓" if v["available"] else "✗ (not yet)"
        print(f"  {k}: {flag}  n_items={v['n_items']}")

    if "accuracy_vs_silver_internal" in report:
        print("\n=== ACCURACY vs SILVER-INTERNAL (effect_estimate field) ===")
        print(f"{'Model':<20} {'Run mean':>10} {'Run min':>10} {'Run max':>10} {'Range':>10}")
        for m, r in report["accuracy_vs_silver_internal"].items():
            s = r["summary_across_runs"].get("effect_estimate")
            if s:
                print(f"{m:<20} {s['mean']:>10.4f} {s['min']:>10.4f} {s['max']:>10.4f} {s['range']:>10.4f}")
    print(f"\nWrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
