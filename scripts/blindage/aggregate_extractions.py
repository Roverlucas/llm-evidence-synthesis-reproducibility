"""Aggregate extraction outputs across all models and runs.

Produces a canonical long-form DataFrame-like JSON for downstream analyses:
    model, run_id, corpus_id, estimate_idx, effect_measure, effect_estimate,
    ci_lower, ci_upper, lag, outcome_specific, covariates_str, output_hash

Writes: analysis/blindage/extraction_long.json
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw_outputs"
OUT = ROOT / "analysis" / "blindage" / "extraction_long.json"

MODELS = ["llama3-8b", "mistral-7b", "gemma2-9b",
          "claude-sonnet-4-5", "gemini-2.5-pro", "gpt-4.1"]


def covariates_str(cov) -> str:
    if cov is None:
        return ""
    if isinstance(cov, list):
        return ";".join(sorted(str(c).lower() for c in cov))
    return str(cov).lower()


def main() -> None:
    long_rows = []
    for model in MODELS:
        extraction_dir = RAW / model / "extraction"
        if not extraction_dir.exists():
            print(f"SKIP {model}: no extraction dir")
            continue
        for run_dir in sorted(extraction_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            run_id = int(run_dir.name.split("_")[-1])
            results_path = run_dir / "results.json"
            if not results_path.exists():
                continue
            records = json.loads(results_path.read_text())
            for r in records:
                out = r.get("output") or {}
                ests = out.get("estimates") or []
                if not ests:
                    long_rows.append({
                        "model": model,
                        "run_id": run_id,
                        "corpus_id": r["corpus_id"],
                        "estimate_idx": None,
                        "n_estimates": 0,
                        "effect_measure": None,
                        "effect_estimate": None,
                        "ci_lower": None,
                        "ci_upper": None,
                        "lag": None,
                        "outcome_specific": None,
                        "exposure_increment": None,
                        "covariates_str": "",
                        "output_hash": r.get("output_hash"),
                        "valid": r.get("valid"),
                    })
                else:
                    for i, e in enumerate(ests):
                        long_rows.append({
                            "model": model,
                            "run_id": run_id,
                            "corpus_id": r["corpus_id"],
                            "estimate_idx": i,
                            "n_estimates": len(ests),
                            "effect_measure": e.get("effect_measure"),
                            "effect_estimate": e.get("effect_estimate"),
                            "ci_lower": e.get("ci_lower"),
                            "ci_upper": e.get("ci_upper"),
                            "lag": e.get("lag"),
                            "outcome_specific": e.get("outcome_specific"),
                            "exposure_increment": e.get("exposure_increment"),
                            "covariates_str": covariates_str(e.get("covariates")),
                            "output_hash": r.get("output_hash"),
                            "valid": r.get("valid"),
                        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(long_rows, default=str))
    print(f"wrote {OUT.relative_to(ROOT)}  n_rows={len(long_rows)}")
    # Summary
    from collections import Counter
    by_model = Counter(r["model"] for r in long_rows)
    n_estimates = sum(1 for r in long_rows if r["effect_estimate"] is not None)
    print(f"rows w/ estimate: {n_estimates}")
    for m, n in sorted(by_model.items()):
        n_est_m = sum(1 for r in long_rows if r["model"] == m and r["effect_estimate"] is not None)
        print(f"  {m}: total={n} w_estimate={n_est_m}")


if __name__ == "__main__":
    main()
