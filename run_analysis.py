#!/usr/bin/env python3
"""
Analysis script for LLM Evidence Synthesis Reproducibility Experiment.

Computes:
  - Screening EMR (Exact Match Rate) per model
  - Extraction EMR per model
  - Screening accuracy vs gold standard
  - Pairwise agreement (Fleiss' kappa)
  - Bootstrap confidence intervals (10k resamples)
  - Field-level extraction variation
  - Summary tables and figures
"""

import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

# ── Paths ────────────────────────────────────────────────────────────
DATA_DIR = Path("data/raw_outputs")
GOLD_DIR = Path("data/gold_standard")
OUT_DIR = Path("analysis")
TABLES_DIR = OUT_DIR / "tables"
FIGURES_DIR = OUT_DIR / "figures"
BOOTSTRAP_DIR = OUT_DIR / "bootstrap"

MODELS = ["claude-sonnet-4-5", "llama3-8b", "gemini-2.5-pro"]
STAGES = ["screening", "extraction"]
N_RUNS = 10
N_BOOTSTRAP = 10_000

for d in [TABLES_DIR, FIGURES_DIR, BOOTSTRAP_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ── Data Loading ─────────────────────────────────────────────────────
def load_results(model: str, stage: str) -> dict[int, list[dict]]:
    """Load results for all runs of a model/stage. Returns {run_id: [results]}."""
    runs = {}
    for run_id in range(1, N_RUNS + 1):
        path = DATA_DIR / model / stage / f"run_{run_id:03d}" / "results.json"
        if path.exists():
            with open(path) as f:
                runs[run_id] = json.load(f)
    return runs


def load_gold_screening() -> dict[str, str]:
    """Load gold standard screening labels. Returns {corpus_id: label}."""
    with open(GOLD_DIR / "screening_labels.json") as f:
        data = json.load(f)
    labels = {}
    for item in data["labels"]:
        labels[item["corpus_id"]] = item["heuristic_label"]
    return labels


# ── Screening Analysis ───────────────────────────────────────────────
def compute_screening_emr(runs: dict[int, list[dict]]) -> dict:
    """Compute EMR for screening: fraction of abstracts with identical decisions across all runs."""
    # Build {corpus_id: [decision_per_run]}
    decisions = defaultdict(list)
    for run_id in sorted(runs.keys()):
        for item in runs[run_id]:
            cid = item["corpus_id"]
            output = item.get("output", {})
            if "error" in output:
                decisions[cid].append("ERROR")
            else:
                decisions[cid].append(output.get("decision", "ERROR"))

    # Only consider abstracts present in ALL runs
    n_runs = len(runs)
    valid_ids = [cid for cid, decs in decisions.items() if len(decs) == n_runs]

    exact_matches = 0
    for cid in valid_ids:
        if len(set(decisions[cid])) == 1:
            exact_matches += 1

    emr = exact_matches / len(valid_ids) if valid_ids else 0.0

    # Flip rate: fraction that changed at least once
    flip_rate = 1.0 - emr

    # Per-abstract agreement distribution
    agreement_dist = []
    for cid in valid_ids:
        most_common = Counter(decisions[cid]).most_common(1)[0][1]
        agreement_dist.append(most_common / n_runs)

    return {
        "emr": emr,
        "flip_rate": flip_rate,
        "n_abstracts": len(valid_ids),
        "n_runs": n_runs,
        "exact_matches": exact_matches,
        "mean_agreement": float(np.mean(agreement_dist)) if agreement_dist else 0.0,
        "decisions": {cid: decisions[cid] for cid in valid_ids},
    }


def compute_screening_accuracy(runs: dict[int, list[dict]], gold: dict[str, str]) -> dict:
    """Compute screening accuracy vs gold standard per run."""
    per_run = {}
    for run_id in sorted(runs.keys()):
        tp = fp = tn = fn = 0
        for item in runs[run_id]:
            cid = item["corpus_id"]
            if cid not in gold:
                continue
            pred = item.get("output", {}).get("decision", "error")
            true = gold[cid]
            if pred == "include" and true == "include":
                tp += 1
            elif pred == "include" and true == "exclude":
                fp += 1
            elif pred == "exclude" and true == "exclude":
                tn += 1
            elif pred == "exclude" and true == "include":
                fn += 1

        total = tp + fp + tn + fn
        accuracy = (tp + tn) / total if total > 0 else 0
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

        per_run[run_id] = {
            "accuracy": accuracy,
            "sensitivity": sensitivity,
            "specificity": specificity,
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        }

    accuracies = [v["accuracy"] for v in per_run.values()]
    return {
        "per_run": per_run,
        "mean_accuracy": float(np.mean(accuracies)),
        "std_accuracy": float(np.std(accuracies)),
        "mean_sensitivity": float(np.mean([v["sensitivity"] for v in per_run.values()])),
        "mean_specificity": float(np.mean([v["specificity"] for v in per_run.values()])),
    }


# ── Extraction Analysis ──────────────────────────────────────────────
def compute_extraction_emr(runs: dict[int, list[dict]]) -> dict:
    """Compute EMR for extraction: fraction of articles with identical outputs across all runs."""
    outputs = defaultdict(list)
    for run_id in sorted(runs.keys()):
        for item in runs[run_id]:
            cid = item["corpus_id"]
            outputs[cid].append(item.get("output_hash", ""))

    n_runs = len(runs)
    valid_ids = [cid for cid, hashes in outputs.items() if len(hashes) == n_runs]

    exact_matches = 0
    for cid in valid_ids:
        if len(set(outputs[cid])) == 1:
            exact_matches += 1

    emr = exact_matches / len(valid_ids) if valid_ids else 0.0

    return {
        "emr": emr,
        "n_articles": len(valid_ids),
        "n_runs": n_runs,
        "exact_matches": exact_matches,
        "hashes": {cid: outputs[cid] for cid in valid_ids},
    }


def compute_extraction_field_variation(runs: dict[int, list[dict]]) -> dict:
    """Compute field-level variation in extraction outputs."""
    fields_to_check = [
        "study_design", "study_location", "study_period",
        "population", "sample_size",
    ]
    estimate_fields = ["effect_measure", "effect_estimate", "ci_lower", "ci_upper", "lag"]

    # Build {corpus_id: {field: [values_per_run]}}
    field_values = defaultdict(lambda: defaultdict(list))
    estimate_data = defaultdict(list)  # {corpus_id: [list_of_estimates_per_run]}

    n_runs = len(runs)
    for run_id in sorted(runs.keys()):
        for item in runs[run_id]:
            cid = item["corpus_id"]
            output = item.get("output", {})
            if "error" in output:
                continue
            for f in fields_to_check:
                field_values[cid][f].append(str(output.get(f, "")))
            estimate_data[cid].append(output.get("estimates", []))

    # Compute per-field EMR
    field_emr = {}
    for f in fields_to_check:
        matches = 0
        total = 0
        for cid, fv in field_values.items():
            if len(fv[f]) == n_runs:
                total += 1
                if len(set(fv[f])) == 1:
                    matches += 1
        field_emr[f] = matches / total if total > 0 else 0.0

    # Compute estimate-level variation
    n_estimates_vary = 0
    n_articles_with_estimates = 0
    for cid, est_runs in estimate_data.items():
        if len(est_runs) < n_runs:
            continue
        # Compare number of estimates across runs
        n_est = [len(e) for e in est_runs]
        if any(n > 0 for n in n_est):
            n_articles_with_estimates += 1
            if len(set(n_est)) > 1:
                n_estimates_vary += 1

    return {
        "field_emr": field_emr,
        "n_articles_with_estimates": n_articles_with_estimates,
        "n_estimates_count_varies": n_estimates_vary,
        "estimate_count_stability": 1.0 - (n_estimates_vary / n_articles_with_estimates)
            if n_articles_with_estimates > 0 else 0.0,
    }


# ── Bootstrap CIs ────────────────────────────────────────────────────
def bootstrap_emr(decisions_or_hashes: dict[str, list], n_bootstrap: int = N_BOOTSTRAP) -> dict:
    """Bootstrap CI for EMR (per-abstract/article exact match)."""
    ids = list(decisions_or_hashes.keys())
    n = len(ids)

    # Per-item: 1 if all runs match, 0 otherwise
    per_item = []
    for cid in ids:
        vals = decisions_or_hashes[cid]
        per_item.append(1 if len(set(vals)) == 1 else 0)
    per_item = np.array(per_item)

    point_estimate = float(per_item.mean())

    # Bootstrap
    rng = np.random.default_rng(42)
    boot_emrs = []
    for _ in range(n_bootstrap):
        sample = rng.choice(per_item, size=n, replace=True)
        boot_emrs.append(float(sample.mean()))

    boot_emrs = np.array(boot_emrs)
    ci_lower = float(np.percentile(boot_emrs, 2.5))
    ci_upper = float(np.percentile(boot_emrs, 97.5))

    return {
        "emr": point_estimate,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "n_items": n,
        "n_bootstrap": n_bootstrap,
    }


# ── Main Analysis ────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  LLM Evidence Synthesis — Reproducibility Analysis")
    print("=" * 60)

    gold = load_gold_screening()
    all_results = {}

    # ── Per-model analysis ───────────────────────────────────────
    for model in MODELS:
        print(f"\n{'─' * 60}")
        print(f"  Model: {model}")
        print(f"{'─' * 60}")

        # Screening
        screening_runs = load_results(model, "screening")
        if screening_runs:
            scr_emr = compute_screening_emr(screening_runs)
            scr_acc = compute_screening_accuracy(screening_runs, gold)
            scr_boot = bootstrap_emr(scr_emr["decisions"])

            print(f"\n  SCREENING ({scr_emr['n_abstracts']} abstracts × {scr_emr['n_runs']} runs)")
            print(f"    EMR:          {scr_emr['emr']:.3f}  [{scr_boot['ci_lower']:.3f}, {scr_boot['ci_upper']:.3f}]")
            print(f"    Flip rate:    {scr_emr['flip_rate']:.3f}")
            print(f"    Mean agree:   {scr_emr['mean_agreement']:.3f}")
            print(f"    Accuracy:     {scr_acc['mean_accuracy']:.3f} ± {scr_acc['std_accuracy']:.3f}")
            print(f"    Sensitivity:  {scr_acc['mean_sensitivity']:.3f}")
            print(f"    Specificity:  {scr_acc['mean_specificity']:.3f}")
        else:
            scr_emr = scr_acc = scr_boot = None
            print("  SCREENING: No data")

        # Extraction
        extraction_runs = load_results(model, "extraction")
        if extraction_runs:
            ext_emr = compute_extraction_emr(extraction_runs)
            ext_field = compute_extraction_field_variation(extraction_runs)
            ext_boot = bootstrap_emr(ext_emr["hashes"])

            print(f"\n  EXTRACTION ({ext_emr['n_articles']} articles × {ext_emr['n_runs']} runs)")
            print(f"    EMR:          {ext_emr['emr']:.3f}  [{ext_boot['ci_lower']:.3f}, {ext_boot['ci_upper']:.3f}]")
            print(f"    Field-level EMR:")
            for field, emr_val in ext_field["field_emr"].items():
                print(f"      {field:20s}: {emr_val:.3f}")
            print(f"    Estimate count stability: {ext_field['estimate_count_stability']:.3f}")
        else:
            ext_emr = ext_field = ext_boot = None
            print("  EXTRACTION: No data")

        all_results[model] = {
            "screening_emr": scr_emr,
            "screening_accuracy": scr_acc,
            "screening_bootstrap": scr_boot,
            "extraction_emr": ext_emr,
            "extraction_field_variation": ext_field,
            "extraction_bootstrap": ext_boot,
        }

    # ── Summary Table ────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print("  SUMMARY TABLE")
    print(f"{'=' * 60}")
    print(f"\n  {'Model':<22} {'Scr EMR':>10} {'Scr CI':>18} {'Ext EMR':>10} {'Ext CI':>18}")
    print(f"  {'─' * 22} {'─' * 10} {'─' * 18} {'─' * 10} {'─' * 18}")

    for model in MODELS:
        r = all_results[model]
        s_emr = r["screening_bootstrap"]["emr"] if r["screening_bootstrap"] else 0
        s_ci = f"[{r['screening_bootstrap']['ci_lower']:.3f}, {r['screening_bootstrap']['ci_upper']:.3f}]" if r["screening_bootstrap"] else "N/A"
        e_emr = r["extraction_bootstrap"]["emr"] if r["extraction_bootstrap"] else 0
        e_ci = f"[{r['extraction_bootstrap']['ci_lower']:.3f}, {r['extraction_bootstrap']['ci_upper']:.3f}]" if r["extraction_bootstrap"] else "N/A"
        print(f"  {model:<22} {s_emr:>10.3f} {s_ci:>18} {e_emr:>10.3f} {e_ci:>18}")

    # ── Save results ─────────────────────────────────────────────
    # Clean results for JSON serialization (remove large data)
    save_results = {}
    for model, r in all_results.items():
        save_results[model] = {
            "screening": {
                "emr": r["screening_bootstrap"]["emr"] if r["screening_bootstrap"] else None,
                "ci_lower": r["screening_bootstrap"]["ci_lower"] if r["screening_bootstrap"] else None,
                "ci_upper": r["screening_bootstrap"]["ci_upper"] if r["screening_bootstrap"] else None,
                "n_abstracts": r["screening_emr"]["n_abstracts"] if r["screening_emr"] else None,
                "flip_rate": r["screening_emr"]["flip_rate"] if r["screening_emr"] else None,
                "mean_agreement": r["screening_emr"]["mean_agreement"] if r["screening_emr"] else None,
                "accuracy": r["screening_accuracy"]["mean_accuracy"] if r["screening_accuracy"] else None,
                "sensitivity": r["screening_accuracy"]["mean_sensitivity"] if r["screening_accuracy"] else None,
                "specificity": r["screening_accuracy"]["mean_specificity"] if r["screening_accuracy"] else None,
            },
            "extraction": {
                "emr": r["extraction_bootstrap"]["emr"] if r["extraction_bootstrap"] else None,
                "ci_lower": r["extraction_bootstrap"]["ci_lower"] if r["extraction_bootstrap"] else None,
                "ci_upper": r["extraction_bootstrap"]["ci_upper"] if r["extraction_bootstrap"] else None,
                "n_articles": r["extraction_emr"]["n_articles"] if r["extraction_emr"] else None,
                "field_emr": r["extraction_field_variation"]["field_emr"] if r["extraction_field_variation"] else None,
                "estimate_count_stability": r["extraction_field_variation"]["estimate_count_stability"] if r["extraction_field_variation"] else None,
            },
        }

    with open(OUT_DIR / "reproducibility_results.json", "w") as f:
        json.dump(save_results, f, indent=2)
    print(f"\n  Results saved to: {OUT_DIR / 'reproducibility_results.json'}")

    # Save bootstrap CIs
    bootstrap_data = {}
    for model in MODELS:
        r = all_results[model]
        bootstrap_data[model] = {
            "screening": r["screening_bootstrap"],
            "extraction": r["extraction_bootstrap"],
        }
    with open(BOOTSTRAP_DIR / "bootstrap_cis.json", "w") as f:
        json.dump(bootstrap_data, f, indent=2)
    print(f"  Bootstrap CIs saved to: {BOOTSTRAP_DIR / 'bootstrap_cis.json'}")

    # ── Generate figures ─────────────────────────────────────────
    try:
        generate_figures(all_results)
    except ImportError as e:
        print(f"\n  WARNING: Could not generate figures ({e}). Install matplotlib/seaborn.")

    print(f"\n{'=' * 60}")
    print("  ANALYSIS COMPLETE")
    print(f"{'=' * 60}")

    return all_results


def generate_figures(all_results: dict):
    """Generate comparison figures."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # ── Figure 1: EMR Comparison Bar Chart ───────────────────────
    fig, ax = plt.subplots(figsize=(10, 6))

    models_short = ["Claude\nSonnet 4.5", "LLaMA 3\n8B", "Gemini 2.5\nPro"]
    x = np.arange(len(MODELS))
    width = 0.35

    scr_emrs = []
    ext_emrs = []
    scr_errs = []
    ext_errs = []

    for model in MODELS:
        r = all_results[model]
        sb = r["screening_bootstrap"]
        eb = r["extraction_bootstrap"]

        scr_emrs.append(sb["emr"] if sb else 0)
        ext_emrs.append(eb["emr"] if eb else 0)
        scr_errs.append([
            sb["emr"] - sb["ci_lower"] if sb else 0,
            sb["ci_upper"] - sb["emr"] if sb else 0,
        ])
        ext_errs.append([
            eb["emr"] - eb["ci_lower"] if eb else 0,
            eb["ci_upper"] - eb["emr"] if eb else 0,
        ])

    scr_err_low = [e[0] for e in scr_errs]
    scr_err_high = [e[1] for e in scr_errs]
    ext_err_low = [e[0] for e in ext_errs]
    ext_err_high = [e[1] for e in ext_errs]

    bars1 = ax.bar(x - width / 2, scr_emrs, width, label="Screening",
                   color="#2196F3", yerr=[scr_err_low, scr_err_high], capsize=5)
    bars2 = ax.bar(x + width / 2, ext_emrs, width, label="Extraction",
                   color="#FF9800", yerr=[ext_err_low, ext_err_high], capsize=5)

    ax.set_ylabel("Exact Match Rate (EMR)", fontsize=12)
    ax.set_title("Reproducibility: Exact Match Rate by Model and Stage", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(models_short, fontsize=11)
    ax.legend(fontsize=11)
    ax.set_ylim(0, 1.05)
    ax.axhline(y=1.0, color="gray", linestyle="--", alpha=0.3)
    ax.grid(axis="y", alpha=0.3)

    # Add value labels
    for bar in bars1:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., h + 0.03, f"{h:.3f}",
                ha="center", va="bottom", fontsize=10)
    for bar in bars2:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., h + 0.03, f"{h:.3f}",
                ha="center", va="bottom", fontsize=10)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "emr_comparison.pdf", dpi=300)
    fig.savefig(FIGURES_DIR / "emr_comparison.png", dpi=150)
    plt.close()
    print(f"  Figure saved: {FIGURES_DIR / 'emr_comparison.pdf'}")

    # ── Figure 2: Field-level EMR heatmap ────────────────────────
    fields = ["study_design", "study_location", "study_period", "population", "sample_size"]
    field_data = []
    for model in MODELS:
        r = all_results[model]
        fv = r["extraction_field_variation"]
        if fv:
            field_data.append([fv["field_emr"].get(f, 0) for f in fields])
        else:
            field_data.append([0] * len(fields))

    fig, ax = plt.subplots(figsize=(10, 4))
    data = np.array(field_data)
    im = ax.imshow(data, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")

    ax.set_xticks(range(len(fields)))
    ax.set_xticklabels([f.replace("_", "\n") for f in fields], fontsize=10)
    ax.set_yticks(range(len(MODELS)))
    ax.set_yticklabels(models_short, fontsize=11)
    ax.set_title("Extraction Field-Level EMR by Model", fontsize=14)

    # Add text annotations
    for i in range(len(MODELS)):
        for j in range(len(fields)):
            ax.text(j, i, f"{data[i, j]:.2f}", ha="center", va="center",
                    color="black" if data[i, j] > 0.5 else "white", fontsize=11)

    plt.colorbar(im, ax=ax, label="EMR")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "field_emr_heatmap.pdf", dpi=300)
    fig.savefig(FIGURES_DIR / "field_emr_heatmap.png", dpi=150)
    plt.close()
    print(f"  Figure saved: {FIGURES_DIR / 'field_emr_heatmap.pdf'}")


if __name__ == "__main__":
    main()
