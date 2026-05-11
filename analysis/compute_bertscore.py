#!/usr/bin/env python3
"""Compute BERTScore F1 for extraction outputs using all-pairs comparison.

For each model, computes BERTScore F1 over 10-choose-2 = 45 run-pairs per article
(100 articles -> 4500 pairs per model). Reports BOTH raw F1 and rescaled F1
(rescale_with_baseline=True), per RSM P1.a audit recommendation: raw BERTScore
saturates near 1.0 even for unrelated pairs, so baseline rescaling is required
to interpret the magnitude of semantic agreement.

Outputs:
    analysis/bertscore_results.json       (raw F1 -- legacy, retained for back-compat)
    analysis/bertscore_results_full.json  (raw AND rescaled F1, provenance hash)
"""

import hashlib
import json
import math
import os
import random
import sys
from itertools import combinations

import numpy as np
import torch
from bert_score import score as bert_score

# ---------------------------------------------------------------------------
# Provenance / determinism
# ---------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.backends.mps.is_available():
    torch.mps.manual_seed(SEED)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw_outputs")
OUT_PATH = os.path.join(BASE_DIR, "analysis", "bertscore_results.json")
OUT_FULL_PATH = os.path.join(BASE_DIR, "analysis", "bertscore_results_full.json")
MODELS = [
    "llama3-8b", "mistral-7b", "gemma2-9b",
    "claude-sonnet-4-5", "gemini-2.5-pro", "gpt-4.1",
]
NUM_RUNS = 10
TEXT_FIELDS = ["study_design", "study_location", "study_period", "population", "sample_size"]
BERT_MODEL = "roberta-large"
BERT_LAYER = 17
BATCH_SIZE = 64


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


def summary_stats(f1_list):
    n = len(f1_list)
    if n == 0:
        return {"n": 0, "mean": None, "std": None, "min": None, "max": None,
                "prop_ge_0.95": None, "prop_ge_0.99": None}
    mean = sum(f1_list) / n
    var = sum((x - mean) ** 2 for x in f1_list) / n
    std = math.sqrt(var)
    minv = min(f1_list)
    maxv = max(f1_list)
    n_95 = sum(1 for v in f1_list if v >= 0.95)
    n_99 = sum(1 for v in f1_list if v >= 0.99)
    return {
        "n": n,
        "mean": round(mean, 6),
        "std": round(std, 6),
        "min": round(minv, 6),
        "max": round(maxv, 6),
        "prop_ge_0.95": round(n_95 / n, 6),
        "prop_ge_0.99": round(n_99 / n, 6),
    }


def main():
    legacy_results = {}
    full_results = {
        "metadata": {
            "seed": SEED,
            "bert_model": BERT_MODEL,
            "bert_layer": BERT_LAYER,
            "batch_size": BATCH_SIZE,
            "rescale_with_baseline": "Both raw and rescaled F1 computed in parallel "
            "(rescaled uses bert_score package's roberta-large baseline; reported per RSM P1.a audit).",
            "num_runs": NUM_RUNS,
            "text_fields": TEXT_FIELDS,
        },
        "models": {},
    }

    run_pairs = list(combinations(range(1, NUM_RUNS + 1), 2))  # 45 pairs
    print(f"All-pairs comparison: {len(run_pairs)} run pairs per article (10 choose 2)")

    for model in MODELS:
        sep = "=" * 60
        print(f"\n{sep}\nModel: {model}\n{sep}")

        runs = load_runs(model)

        # Find corpus_ids present in ALL 10 runs with non-None output
        all_ids = None
        for r in range(1, NUM_RUNS + 1):
            ids_with_output = {
                cid for cid, item in runs[r].items()
                if item.get("output") is not None
            }
            all_ids = ids_with_output if all_ids is None else all_ids & ids_with_output

        corpus_ids = sorted(all_ids)
        print(f"  Articles present in all 10 runs: {len(corpus_ids)}")

        # Build all-pairs: refs and cands
        refs, cands, pair_labels = [], [], []
        for cid in corpus_ids:
            for ra, rb in run_pairs:
                refs.append(item_to_text(runs[ra][cid]))
                cands.append(item_to_text(runs[rb][cid]))
                pair_labels.append((cid, ra, rb))

        total_pairs = len(refs)
        print(f"  Total all-pairs: {total_pairs}")

        if total_pairs == 0:
            legacy_results[model] = {
                "n_articles": len(corpus_ids), "n_pairs": 0,
                "mean_f1": None, "std_f1": None, "min_f1": None,
                "prop_ge_0.95": None, "prop_ge_0.99": None,
            }
            full_results["models"][model] = {
                "n_articles": len(corpus_ids), "n_pairs": 0,
                "raw_f1": summary_stats([]), "rescaled_f1": summary_stats([]),
            }
            continue

        device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"  Device: {device}")

        # ---- Raw F1 ----
        print(f"  [raw] Computing BERTScore ({BERT_MODEL}) for {total_pairs} pairs ...")
        _, _, F1_raw = bert_score(
            cands, refs,
            model_type=BERT_MODEL, num_layers=BERT_LAYER,
            batch_size=BATCH_SIZE, device=device, verbose=False,
            rescale_with_baseline=False,
            lang="en",
        )
        f1_raw = F1_raw.tolist()
        raw_stats = summary_stats(f1_raw)
        print(f"    raw mean F1     = {raw_stats['mean']:.4f} +/- {raw_stats['std']:.4f}")
        print(f"    raw min/max     = {raw_stats['min']:.4f} / {raw_stats['max']:.4f}")
        print(f"    raw prop>=0.95  = {raw_stats['prop_ge_0.95']:.4f}")

        # ---- Rescaled F1 ----
        print(f"  [rescaled] Recomputing with rescale_with_baseline=True ...")
        _, _, F1_rsc = bert_score(
            cands, refs,
            model_type=BERT_MODEL, num_layers=BERT_LAYER,
            batch_size=BATCH_SIZE, device=device, verbose=False,
            rescale_with_baseline=True,
            lang="en",
        )
        f1_rsc = F1_rsc.tolist()
        rsc_stats = summary_stats(f1_rsc)
        print(f"    rsc mean F1     = {rsc_stats['mean']:.4f} +/- {rsc_stats['std']:.4f}")
        print(f"    rsc min/max     = {rsc_stats['min']:.4f} / {rsc_stats['max']:.4f}")
        print(f"    rsc prop>=0.95  = {rsc_stats['prop_ge_0.95']:.4f}")

        # ---- Per-article means (raw) for legacy compatibility ----
        article_means = {}
        for i, (cid, ra, rb) in enumerate(pair_labels):
            article_means.setdefault(cid, []).append(f1_raw[i])

        # Legacy summary (raw-only, matches existing file)
        legacy_results[model] = {
            "n_articles": len(corpus_ids),
            "n_pairs": total_pairs,
            "mean_f1": raw_stats["mean"],
            "std_f1": raw_stats["std"],
            "min_f1": raw_stats["min"],
            "max_f1": raw_stats["max"],
            "prop_ge_0.95": raw_stats["prop_ge_0.95"],
            "prop_ge_0.99": raw_stats["prop_ge_0.99"],
        }

        full_results["models"][model] = {
            "n_articles": len(corpus_ids),
            "n_pairs": total_pairs,
            "raw_f1": raw_stats,
            "rescaled_f1": rsc_stats,
        }

    # Provenance hashes
    legacy_payload = json.dumps(legacy_results, indent=2, sort_keys=True)
    full_payload = json.dumps(full_results, indent=2, sort_keys=True)
    full_results["metadata"]["sha256_self"] = hashlib.sha256(full_payload.encode()).hexdigest()

    # Save
    with open(OUT_PATH, "w") as f:
        f.write(legacy_payload)
    with open(OUT_FULL_PATH, "w") as f:
        json.dump(full_results, f, indent=2, sort_keys=True)
    print(f"\nResults saved to:\n  {OUT_PATH}\n  {OUT_FULL_PATH}")

    # Summary table
    sep80 = "=" * 92
    dash80 = "-" * 92
    header = (f"{'Model':<25} {'Pairs':>7} | "
              f"{'raw mean':>9} {'raw min':>9} {'raw>=.95':>9} | "
              f"{'rsc mean':>9} {'rsc min':>9} {'rsc>=.95':>9}")
    print(f"\n{sep80}\n{header}\n{dash80}")
    for model in MODELS:
        r = full_results["models"][model]
        if r["n_pairs"] == 0:
            print(f"{model:<25} {'0':>7}")
            continue
        raw, rsc = r["raw_f1"], r["rescaled_f1"]
        print(f"{model:<25} {r['n_pairs']:>7} | "
              f"{raw['mean']:>9.4f} {raw['min']:>9.4f} {raw['prop_ge_0.95']:>9.4f} | "
              f"{rsc['mean']:>9.4f} {rsc['min']:>9.4f} {rsc['prop_ge_0.95']:>9.4f}")
    print(sep80)


if __name__ == "__main__":
    main()
