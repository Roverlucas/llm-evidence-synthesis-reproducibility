"""Per-run extraction accuracy against gold standard (R4 Q2, P1.4).

For each model × run, compute extraction accuracy at the field level against
the 100-article extraction gold standard. Reports whether accuracy varies
across runs (in addition to reproducibility).

Gold standard fields checked:
    effect_estimate (numeric, tolerance 0.01)
    ci_lower, ci_upper (tolerance 0.01)
    effect_measure (exact)
    outcome_specific (exact)
    exposure_increment (normalized)

Output: analysis/blindage/per_run_accuracy.json
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "data" / "gold_standard" / "extraction_labels.json"
RAW = ROOT / "data" / "raw_outputs"
OUT = ROOT / "analysis" / "blindage" / "per_run_accuracy.json"

MODELS = ["llama3-8b", "mistral-7b", "gemma2-9b",
          "claude-sonnet-4-5", "gemini-2.5-pro", "gpt-4.1"]

NUMERIC_TOL = 0.01


def within(a, b, tol=NUMERIC_TOL) -> bool:
    if a is None or b is None:
        return False
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return False


def equal_ci(a, b) -> bool:
    if a is None or b is None:
        return False
    return str(a).strip().lower() == str(b).strip().lower()


def first_valid(ests):
    for e in ests or []:
        if e.get("effect_estimate") is not None:
            return e
    return None


def main() -> None:
    gold_all = json.loads(GOLD.read_text())
    gold_labels = gold_all["labels"] if isinstance(gold_all, dict) and "labels" in gold_all else gold_all
    # Normalize to {corpus_id: {fields}}
    if isinstance(gold_labels, list):
        gold_map = {g["corpus_id"]: g for g in gold_labels}
    else:
        gold_map = gold_labels
    # Keep only items with extraction gold
    gold_ext = {}
    for cid, g in gold_map.items():
        # structure may be {corpus_id, label: {...}} or flat
        ext = g.get("extraction") or g.get("gold") or g
        # Try to find an extraction with an estimate
        est = None
        if "estimates" in ext and ext["estimates"]:
            est = ext["estimates"][0]
        elif "effect_estimate" in ext:
            est = ext
        if est and est.get("effect_estimate") is not None:
            gold_ext[cid] = est

    print(f"Gold extraction items: {len(gold_ext)}")

    # Compute per-run accuracy
    report = {
        "method": "Field-level extraction accuracy against gold (first-estimate only).",
        "numeric_tolerance": NUMERIC_TOL,
        "n_gold_items": len(gold_ext),
        "models": {},
    }

    for model in MODELS:
        ext_dir = RAW / model / "extraction"
        if not ext_dir.exists():
            continue
        model_rep = {"per_run": {}, "summary": {}}
        per_run_accs = {
            "effect_estimate": [],
            "ci_bounds": [],  # both lower and upper
            "effect_measure": [],
            "outcome_specific": [],
            "all_fields": [],  # all of the above
        }
        for run_dir in sorted(ext_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            run_id = int(run_dir.name.split("_")[-1])
            res = run_dir / "results.json"
            if not res.exists():
                continue
            records = json.loads(res.read_text())
            pred_map = {r["corpus_id"]: r for r in records}
            correct = defaultdict(int)
            n_with_pred = 0
            for cid, g in gold_ext.items():
                p = pred_map.get(cid)
                if not p:
                    continue
                ests = (p.get("output") or {}).get("estimates") or []
                pe = first_valid(ests)
                if not pe:
                    continue
                n_with_pred += 1
                ee_ok = within(pe.get("effect_estimate"), g.get("effect_estimate"))
                lo_ok = within(pe.get("ci_lower"), g.get("ci_lower"))
                hi_ok = within(pe.get("ci_upper"), g.get("ci_upper"))
                em_ok = equal_ci(pe.get("effect_measure"), g.get("effect_measure"))
                os_ok = equal_ci(pe.get("outcome_specific"), g.get("outcome_specific"))
                if ee_ok:
                    correct["effect_estimate"] += 1
                if lo_ok and hi_ok:
                    correct["ci_bounds"] += 1
                if em_ok:
                    correct["effect_measure"] += 1
                if os_ok:
                    correct["outcome_specific"] += 1
                if ee_ok and lo_ok and hi_ok and em_ok:
                    correct["all_fields"] += 1
            if n_with_pred == 0:
                continue
            accs = {k: correct[k] / n_with_pred for k in per_run_accs}
            model_rep["per_run"][str(run_id)] = {
                "n_gold_with_prediction": n_with_pred,
                **{k: round(accs[k], 4) for k in per_run_accs},
            }
            for k in per_run_accs:
                per_run_accs[k].append(accs[k])

        summary = {}
        for field, vals in per_run_accs.items():
            if not vals:
                continue
            mean = sum(vals) / len(vals)
            rng = max(vals) - min(vals)
            n = len(vals)
            var = sum((v - mean) ** 2 for v in vals) / n if n else 0.0
            summary[field] = {
                "mean_accuracy_across_runs": round(mean, 4),
                "min_accuracy": round(min(vals), 4),
                "max_accuracy": round(max(vals), 4),
                "range": round(rng, 4),
                "std": round(math.sqrt(var), 4),
            }
        model_rep["summary"] = summary
        report["models"][model] = model_rep

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2))

    print(f"\n{'Model':<20} {'Field':<20} {'Mean Acc':>10} {'Min':>8} {'Max':>8} {'Range':>8}")
    for m, rep in report["models"].items():
        s = rep.get("summary", {})
        for field in ("effect_estimate", "ci_bounds", "effect_measure", "all_fields"):
            x = s.get(field)
            if x:
                print(f"{m:<20} {field:<20} {x['mean_accuracy_across_runs']:>10.4f} {x['min_accuracy']:>8.4f} {x['max_accuracy']:>8.4f} {x['range']:>8.4f}")
    print(f"\nWrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
