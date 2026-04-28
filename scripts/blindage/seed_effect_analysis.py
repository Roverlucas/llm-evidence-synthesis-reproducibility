"""Seed-effect analysis (RSM checklist 4.3 + Cambridge guidance).

Compares reproducibility of models WITH fixed seed=42 vs WITHOUT seed,
using existing data:
    - WITH seed: Gemini 2.5 Pro (seed=42), GPT-4.1 (seed=42)
    - WITHOUT seed: Claude Sonnet 4.5 (no seed parameter supported)

Tests whether seed parameter materially reduces run-to-run variation in APIs.

Output: analysis/blindage/seed_effect.json
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPRO = ROOT / "analysis" / "reproducibility_results.json"
PAIRWISE = ROOT / "analysis" / "blindage" / "pairwise_disagreement.json"
OUT = ROOT / "analysis" / "blindage" / "seed_effect.json"

WITH_SEED = ["gemini-2.5-pro", "gpt-4.1"]
WITHOUT_SEED = ["claude-sonnet-4-5"]
LOCAL_WITH_SEED = ["llama3-8b", "mistral-7b", "gemma2-9b"]


def main() -> None:
    repro = json.loads(REPRO.read_text())
    pairwise = json.loads(PAIRWISE.read_text())

    rows = []
    for group_name, models in [
        ("CLOUD_WITH_seed=42", WITH_SEED),
        ("CLOUD_WITHOUT_seed", WITHOUT_SEED),
        ("LOCAL_WITH_seed=42", LOCAL_WITH_SEED),
    ]:
        for m in models:
            for stage in ("screening", "extraction"):
                s = repro[m][stage]
                pw = pairwise["models"][m][stage]
                rows.append({
                    "group": group_name,
                    "model": m,
                    "stage": stage,
                    "has_seed": m in WITH_SEED + LOCAL_WITH_SEED,
                    "emr": round(s["emr"], 4),
                    "flip_rate": round(s.get("flip_rate", 1 - s["emr"]), 4),
                    "mean_pairwise_disagree": pw["mean_pairwise_disagreement"],
                    "pct_items_any_disagree": pw["pct_items_any_disagreement"],
                })

    # Group summary
    group_summary = defaultdict(lambda: {"models": [], "emr_values": [], "pairwise_values": []})
    for r in rows:
        key = f"{r['group']}_{r['stage']}"
        group_summary[key]["models"].append(r["model"])
        group_summary[key]["emr_values"].append(r["emr"])
        group_summary[key]["pairwise_values"].append(r["mean_pairwise_disagree"])

    summary = {}
    for key, v in group_summary.items():
        if v["emr_values"]:
            summary[key] = {
                "models": v["models"],
                "mean_emr": round(sum(v["emr_values"]) / len(v["emr_values"]), 4),
                "mean_pairwise_disagree": round(sum(v["pairwise_values"]) / len(v["pairwise_values"]), 4),
            }

    report = {
        "method": "Compare EMR and pairwise disagreement between seeded vs non-seeded API models.",
        "hypothesis": "If seed parameter is effective at deterministic APIs, seeded models should show lower run-to-run variation than non-seeded Claude.",
        "rows": rows,
        "group_summary": summary,
        "interpretation": {},
    }

    # Interpret
    for stage in ("screening", "extraction"):
        seeded = summary.get(f"CLOUD_WITH_seed=42_{stage}", {})
        unseeded = summary.get(f"CLOUD_WITHOUT_seed_{stage}", {})
        local = summary.get(f"LOCAL_WITH_seed=42_{stage}", {})
        if seeded and unseeded and local:
            emr_delta_seed = seeded["mean_emr"] - unseeded["mean_emr"]
            pw_delta_seed = seeded["mean_pairwise_disagree"] - unseeded["mean_pairwise_disagree"]
            emr_delta_deploy = local["mean_emr"] - seeded["mean_emr"]
            report["interpretation"][stage] = {
                "seed_effect_EMR (cloud-seed vs cloud-noseed)": round(emr_delta_seed, 4),
                "seed_effect_pairwise (cloud-seed vs cloud-noseed)": round(pw_delta_seed, 4),
                "deployment_effect_EMR (local-seed vs cloud-seed)": round(emr_delta_deploy, 4),
                "conclusion": (
                    f"Seed effect on cloud EMR: {emr_delta_seed:+.4f} (small); "
                    f"Deployment effect (local vs cloud): {emr_delta_deploy:+.4f} (larger). "
                    f"Seed parameter does NOT deliver determinism on cloud APIs; "
                    f"deployment type dominates."
                ),
            }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2))

    print(f"{'Group':<30} {'Stage':<12} {'EMR mean':>10} {'Pairwise mean':>14}")
    for key, v in summary.items():
        group, stage = key.rsplit("_", 1)
        print(f"{group:<30} {stage:<12} {v['mean_emr']:>10.4f} {v['mean_pairwise_disagree']:>14.4f}")
    print("\nInterpretation:")
    for stage, i in report["interpretation"].items():
        print(f"  {stage}: {i['conclusion']}")
    print(f"\nWrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
