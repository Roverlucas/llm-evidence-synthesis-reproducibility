#!/usr/bin/env python3
"""Compute BERTScore F1 between run 1 (reference) and runs 2-10 for extraction outputs."""

import json
import os

import torch
from bert_score import score as bert_score

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_DIR = "/Users/lucasrover/llm-evidence-synthesis-reproducibility"
RAW_DIR = os.path.join(BASE_DIR, "data", "raw_outputs")
OUT_PATH = os.path.join(BASE_DIR, "analysis", "bertscore_results.json")
MODELS = ["claude-sonnet-4-5", "gemini-2.5-pro", "llama3-8b"]
NUM_RUNS = 10
TEXT_FIELDS = ["study_design", "study_location", "study_period", "population", "sample_size"]


def item_to_text(item: dict) -> str:
    """Concatenate extraction fields into a single text string."""
    output = item.get("output") or {}
    parts = []
    for field in TEXT_FIELDS:
        val = output.get(field)
        if val is None:
            val = ""
        else:
            val = str(val)
        parts.append(val)
    return " | ".join(parts)


def load_runs(model: str) -> dict:
    """Load all 10 runs for a model. Returns {run_id: {corpus_id: item}}."""
    runs = {}
    for r in range(1, NUM_RUNS + 1):
        path = os.path.join(RAW_DIR, model, "extraction", f"run_{r:03d}", "results.json")
        with open(path) as f:
            data = json.load(f)
        runs[r] = {item["corpus_id"]: item for item in data}
    return runs


def main():
    results = {}

    for model in MODELS:
        sep = "=" * 60
        print(f"\n{sep}")
        print(f"Model: {model}")
        print(sep)

        runs = load_runs(model)

        # Find corpus_ids present in ALL 10 runs with non-None output
        all_ids = None
        for r in range(1, NUM_RUNS + 1):
            ids_with_output = {
                cid for cid, item in runs[r].items()
                if item.get("output") is not None
            }
            if all_ids is None:
                all_ids = ids_with_output
            else:
                all_ids &= ids_with_output

        corpus_ids = sorted(all_ids)
        print(f"  Articles present in all 10 runs with output: {len(corpus_ids)}")

        # Build reference texts (run 1) and candidate texts (runs 2-10)
        refs = []
        cands = []
        pair_labels = []  # (corpus_id, run_id) for debugging

        for cid in corpus_ids:
            ref_text = item_to_text(runs[1][cid])
            for r in range(2, NUM_RUNS + 1):
                cand_text = item_to_text(runs[r][cid])
                refs.append(ref_text)
                cands.append(cand_text)
                pair_labels.append((cid, r))

        total_pairs = len(refs)
        print(f"  Total (article x run) pairs: {total_pairs}")

        if total_pairs == 0:
            print("  WARNING: No pairs to compute. Skipping.")
            results[model] = {
                "n_articles": len(corpus_ids),
                "n_pairs": 0,
                "mean_f1": None,
                "min_f1": None,
                "prop_ge_0.95": None,
                "prop_ge_0.99": None,
            }
            continue

        # Compute BERTScore in batch
        print(f"  Computing BERTScore (roberta-large) for {total_pairs} pairs ...")
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"  Device: {device}")

        P, R, F1 = bert_score(
            cands,
            refs,
            model_type="roberta-large",
            num_layers=17,
            batch_size=64,
            device=device,
            verbose=True,
        )

        f1_list = F1.tolist()

        mean_f1 = sum(f1_list) / len(f1_list)
        min_f1 = min(f1_list)
        prop_95 = sum(1 for v in f1_list if v >= 0.95) / len(f1_list)
        prop_99 = sum(1 for v in f1_list if v >= 0.99) / len(f1_list)

        n_95 = sum(1 for v in f1_list if v >= 0.95)
        n_99 = sum(1 for v in f1_list if v >= 0.99)
        n_total = len(f1_list)

        print(f"\n  Results for {model}:")
        print(f"    Mean BERTScore F1:   {mean_f1:.4f}")
        print(f"    Min  BERTScore F1:   {min_f1:.4f}")
        print(f"    Prop F1 >= 0.95:     {prop_95:.4f} ({n_95}/{n_total})")
        print(f"    Prop F1 >= 0.99:     {prop_99:.4f} ({n_99}/{n_total})")

        # Find lowest-scoring pairs for inspection
        indexed = sorted(enumerate(f1_list), key=lambda x: x[1])
        print("\n  Lowest 5 pairs:")
        for idx, val in indexed[:5]:
            cid, run = pair_labels[idx]
            print(f"    {cid} run_{run:03d}: F1={val:.4f}")
            print(f"      ref:  {refs[idx][:120]}")
            print(f"      cand: {cands[idx][:120]}")

        results[model] = {
            "n_articles": len(corpus_ids),
            "n_pairs": total_pairs,
            "mean_f1": round(mean_f1, 6),
            "min_f1": round(min_f1, 6),
            "prop_ge_0.95": round(prop_95, 6),
            "prop_ge_0.99": round(prop_99, 6),
        }

    # Save results
    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n\nResults saved to {OUT_PATH}")

    # Print summary table
    sep80 = "=" * 80
    dash80 = "-" * 80
    header = f"{'Model':<25} {'N_pairs':>8} {'Mean F1':>10} {'Min F1':>10} {'>=0.95':>10} {'>=0.99':>10}"
    print(f"\n{sep80}")
    print(header)
    print(dash80)
    for model in MODELS:
        r = results[model]
        if r["n_pairs"] == 0:
            print(f"{model:<25} {'0':>8} {'N/A':>10} {'N/A':>10} {'N/A':>10} {'N/A':>10}")
        else:
            np_ = r["n_pairs"]
            mf = r["mean_f1"]
            mnf = r["min_f1"]
            p95 = r["prop_ge_0.95"]
            p99 = r["prop_ge_0.99"]
            print(f"{model:<25} {np_:>8} {mf:>10.4f} {mnf:>10.4f} {p95:>10.4f} {p99:>10.4f}")
    print(sep80)


if __name__ == "__main__":
    main()
