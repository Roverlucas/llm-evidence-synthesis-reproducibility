#!/usr/bin/env python3
"""Compute BERTScore F1 for extraction outputs using all-pairs comparison (10 choose 2 = 45 pairs per article)."""

import json
import math
import os
from itertools import combinations

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
    run_pairs = list(combinations(range(1, NUM_RUNS + 1), 2))  # 45 pairs
    print(f"All-pairs comparison: {len(run_pairs)} run pairs per article (10 choose 2)")

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
        print(f"  Articles present in all 10 runs: {len(corpus_ids)}")

        # Build all-pairs: refs and cands
        refs = []
        cands = []
        pair_labels = []  # (corpus_id, run_a, run_b)

        for cid in corpus_ids:
            for ra, rb in run_pairs:
                text_a = item_to_text(runs[ra][cid])
                text_b = item_to_text(runs[rb][cid])
                refs.append(text_a)
                cands.append(text_b)
                pair_labels.append((cid, ra, rb))

        total_pairs = len(refs)
        print(f"  Total all-pairs: {total_pairs} ({len(corpus_ids)} articles x {len(run_pairs)} pairs)")

        if total_pairs == 0:
            results[model] = {
                "n_articles": len(corpus_ids),
                "n_pairs": 0,
                "mean_f1": None, "std_f1": None, "min_f1": None,
                "prop_ge_0.95": None, "prop_ge_0.99": None,
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
        n = len(f1_list)
        mean_f1 = sum(f1_list) / n
        var_f1 = sum((x - mean_f1) ** 2 for x in f1_list) / n
        std_f1 = math.sqrt(var_f1)
        min_f1 = min(f1_list)
        max_f1 = max(f1_list)
        n_95 = sum(1 for v in f1_list if v >= 0.95)
        n_99 = sum(1 for v in f1_list if v >= 0.99)

        print(f"\n  Results for {model} (all-pairs):")
        print(f"    Mean BERTScore F1:   {mean_f1:.4f} +/- {std_f1:.4f}")
        print(f"    Min  BERTScore F1:   {min_f1:.4f}")
        print(f"    Max  BERTScore F1:   {max_f1:.4f}")
        print(f"    Prop F1 >= 0.95:     {n_95/n:.4f} ({n_95}/{n})")
        print(f"    Prop F1 >= 0.99:     {n_99/n:.4f} ({n_99}/{n})")

        # Per-article mean F1
        article_means = {}
        for i, (cid, ra, rb) in enumerate(pair_labels):
            article_means.setdefault(cid, []).append(f1_list[i])
        per_article = {cid: sum(vs)/len(vs) for cid, vs in article_means.items()}
        lowest_articles = sorted(per_article.items(), key=lambda x: x[1])[:5]

        print(f"\n  Lowest 5 articles (by mean F1 across all pairs):")
        for cid, amean in lowest_articles:
            scores = article_means[cid]
            print(f"    {cid}: mean={amean:.4f}, min={min(scores):.4f}, max={max(scores):.4f}")

        results[model] = {
            "n_articles": len(corpus_ids),
            "n_pairs": total_pairs,
            "mean_f1": round(mean_f1, 6),
            "std_f1": round(std_f1, 6),
            "min_f1": round(min_f1, 6),
            "max_f1": round(max_f1, 6),
            "prop_ge_0.95": round(n_95 / n, 6),
            "prop_ge_0.99": round(n_99 / n, 6),
        }

    # Save results
    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n\nResults saved to {OUT_PATH}")

    # Print summary table
    sep80 = "=" * 80
    dash80 = "-" * 80
    header = f"{'Model':<25} {'Pairs':>7} {'Mean F1':>10} {'SD':>8} {'Min':>8} {'>=0.95':>8} {'>=0.99':>8}"
    print(f"\n{sep80}")
    print(header)
    print(dash80)
    for model in MODELS:
        r = results[model]
        if r["n_pairs"] == 0:
            print(f"{model:<25} {'0':>7}")
        else:
            print(f"{model:<25} {r['n_pairs']:>7} {r['mean_f1']:>10.4f} {r['std_f1']:>8.4f} {r['min_f1']:>8.4f} {r['prop_ge_0.95']:>8.4f} {r['prop_ge_0.99']:>8.4f}")
    print(sep80)


if __name__ == "__main__":
    main()
