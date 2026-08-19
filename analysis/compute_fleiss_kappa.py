#!/usr/bin/env python3
"""Compute Fleiss' kappa for inter-run agreement on LLM screening/extraction (P1.c).

Fleiss' kappa quantifies inter-rater agreement for nominal categorical decisions
where each item is rated by the same set of raters. Here the 10 runs of a given
model serve as the "raters" and each abstract (screening) or extraction-field
value (extraction) is an "item".

Computed for each model:
  - Screening decisions (3-class: include/exclude/uncertain), n_items=500
  - Extraction overall (binary: identical-hash-with-run-1 vs not)
  - Extraction per categorical field (study_design, population) where defined.

For each kappa we report:
  - kappa (Fleiss' point estimate)
  - 95% asymptotic CI (Fleiss, Cohen, Everitt 1969; standard error via the
    closed-form variance formula in statsmodels' kappa SE computation
    -- statsmodels does not return SE so we compute it ourselves).
  - n_raters (10), n_items, k_categories

Reference: Fleiss J.L. (1971). Measuring nominal scale agreement among many
raters. Psychological Bulletin, 76(5):378-382.

SE formula (Fleiss 1971 eq. 13):
    SE(kappa) = sqrt( 2 * (sum p_j^2 - (2 * N - 3) * (sum p_j^2)^2
                            + 2 * (N - 2) * sum p_j^3) /
                      (N * n_raters * (n_raters - 1) *
                       (1 - sum p_j^2)^2) )
where p_j is the overall proportion in category j, N = n_items.

Output: analysis/fleiss_kappa.json
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from collections import defaultdict

import numpy as np
from statsmodels.stats.inter_rater import aggregate_raters, fleiss_kappa

SEED = 42
np.random.seed(SEED)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw_outputs")
OUT_PATH = os.path.join(BASE_DIR, "analysis", "fleiss_kappa.json")

MODELS = [
    "llama3-8b", "mistral-7b", "gemma2-9b",
    "claude-sonnet-4-5", "gemini-2.5-pro", "gpt-4.1",
]
NUM_RUNS = 10
SCREEN_CATEGORIES = ["include", "exclude", "uncertain"]
EXTR_CAT_FIELDS = ["study_design", "population"]  # categorical-ish; location is too long-tailed


def fleiss_se_null(table: np.ndarray) -> float:
    """SE of Fleiss' kappa under the null hypothesis kappa = 0, per Fleiss (1971) eq. 13.

    Note what this is and is not. The expression depends only on the marginal
    category proportions P_j, on N and on n; no term carries the observed
    agreement p_o. That is the asymptotic variance *under H0*, which is the
    right quantity for testing kappa = 0 and the wrong one for placing an
    interval around an estimated kappa. Used that way it produces upper limits
    above 1.000 whenever agreement is high, and assigns different standard
    errors to stacks whose kappa is exactly 1.000.

    Retained for the significance test only. Intervals come from
    ``fleiss_ci_bootstrap``.

    table: (N, k) int array of counts (rows sum to n_raters).
    """
    N = table.shape[0]
    n = int(table.sum(axis=1)[0])  # same for all rows
    P_j = table.sum(axis=0) / (N * n)
    sum_pj2 = float((P_j ** 2).sum())
    sum_pj3 = float((P_j ** 3).sum())
    denom = (1.0 - sum_pj2)
    if denom == 0 or N * n * (n - 1) == 0:
        return float("nan")
    num = 2.0 * (sum_pj2 - (2.0 * n - 3.0) * (sum_pj2 ** 2) + 2.0 * (n - 2.0) * sum_pj3)
    var = num / (N * n * (n - 1) * (denom ** 2))
    if var < 0:
        return float("nan")
    return math.sqrt(var)



def fleiss_ci_bootstrap(full: np.ndarray, n_boot: int = 10000, seed: int = 42) -> tuple:
    """Percentile bootstrap CI for Fleiss' kappa, resampling ITEMS with replacement.

    The item is the sampling unit: each bootstrap replicate draws N item-rows
    from the count table and recomputes kappa. This respects the [-1, 1] range
    of the statistic and does not assume a null value.

    Where every replicate returns kappa = 1.000 the interval is degenerate, and
    the caller should report the rule-of-three bound on the non-match rate
    instead, as the manuscript already does for EMR = 1.000 cells.
    """
    rng = np.random.default_rng(seed)
    N = full.shape[0]
    reps = np.empty(n_boot, dtype=float)
    for b in range(n_boot):
        idx = rng.integers(0, N, size=N)
        try:
            reps[b] = fleiss_kappa(full[idx])
        except Exception:
            reps[b] = np.nan
    reps = reps[~np.isnan(reps)]
    if reps.size == 0:
        return (float("nan"), float("nan"), True)
    lo, hi = np.percentile(reps, [2.5, 97.5])
    degenerate = bool(np.allclose(reps, 1.0))
    return (float(lo), float(hi), degenerate)


def fleiss_with_ci(rater_matrix: np.ndarray, categories: list[str]) -> dict:
    """rater_matrix: (n_items, n_raters) categorical (string) array.

    Uses statsmodels aggregate_raters + fleiss_kappa, then computes asymptotic SE.
    Returns {kappa, ci_lower, ci_upper, se, n_items, n_raters, k_categories, P_j}.
    """
    # aggregate_raters expects a 2D matrix of labels per (item, rater)
    table, cats = aggregate_raters(rater_matrix)
    # statsmodels.aggregate_raters returns columns sorted by appearance.
    # Force consistent ordering by re-mapping to user-supplied `categories`.
    # If a category never appeared, add a zero column.
    cat_to_col = {c: i for i, c in enumerate(list(cats))}
    n_items, _ = table.shape
    n_raters = int(table.sum(axis=1)[0])
    full = np.zeros((n_items, len(categories)), dtype=int)
    for j, c in enumerate(categories):
        if c in cat_to_col:
            full[:, j] = table[:, cat_to_col[c]]
    # Some labels may exist outside our list; add them as extra columns.
    extra_cats = [c for c in cats if c not in categories]
    if extra_cats:
        for c in extra_cats:
            full = np.hstack([full, table[:, [cat_to_col[c]]]])
        categories = list(categories) + extra_cats

    k = fleiss_kappa(full)
    se = fleiss_se_null(full)  # for the H0 test only; see docstring
    ci_lo, ci_hi, degenerate = fleiss_ci_bootstrap(full)
    if degenerate:
        # every replicate agrees perfectly: an interval is uninformative and the
        # rule-of-three bound on the non-match rate is the honest statement.
        ci_lo, ci_hi = 1.0, 1.0
    return {
        "kappa": round(float(k), 4),
        "se_under_null": round(float(se), 6) if not math.isnan(se) else None,
        "ci_method": "percentile bootstrap over items, 10,000 resamples, seed 42",
        "ci_lower": round(float(ci_lo), 4) if not math.isnan(ci_lo) else None,
        "ci_upper": round(float(ci_hi), 4) if not math.isnan(ci_hi) else None,
        "ci_degenerate_all_ones": bool(degenerate),
        "n_items": int(n_items),
        "n_raters": int(n_raters),
        "k_categories": len(categories),
        "categories": categories,
    }


def load_screening_decisions(model: str) -> np.ndarray:
    """Return (n_items, n_raters) array of decision strings."""
    by_run = {}
    for r in range(1, NUM_RUNS + 1):
        path = os.path.join(RAW_DIR, model, "screening", f"run_{r:03d}", "results.json")
        with open(path) as f:
            data = json.load(f)
        by_run[r] = {item["corpus_id"]: item for item in data}
    all_ids = set(by_run[1].keys())
    for r in range(2, NUM_RUNS + 1):
        all_ids &= set(by_run[r].keys())
    corpus_ids = sorted(all_ids)
    matrix = []
    for cid in corpus_ids:
        row = []
        valid = True
        for r in range(1, NUM_RUNS + 1):
            output = by_run[r][cid].get("output")
            if output is None or "decision" not in output:
                valid = False
                break
            row.append(str(output["decision"]))
        if valid:
            matrix.append(row)
    return np.array(matrix, dtype=object)


def load_extraction_field(model: str, field: str) -> np.ndarray:
    """For categorical extraction fields. Bins low-frequency labels into 'other'
    only at the per-field level (we keep them as-is to give Fleiss its true k)."""
    by_run = {}
    for r in range(1, NUM_RUNS + 1):
        path = os.path.join(RAW_DIR, model, "extraction", f"run_{r:03d}", "results.json")
        with open(path) as f:
            data = json.load(f)
        by_run[r] = {item["corpus_id"]: item for item in data}
    all_ids = set(by_run[1].keys())
    for r in range(2, NUM_RUNS + 1):
        all_ids &= set(by_run[r].keys())
    corpus_ids = sorted(all_ids)
    matrix = []
    for cid in corpus_ids:
        row = []
        valid = True
        for r in range(1, NUM_RUNS + 1):
            output = by_run[r][cid].get("output")
            if output is None or "error" in output:
                valid = False
                break
            row.append(str(output.get(field, "")))
        if valid:
            matrix.append(row)
    return np.array(matrix, dtype=object)


def load_extraction_hash_binary(model: str) -> tuple[np.ndarray, list[str]]:
    """Binary inter-run agreement: each rater 'votes' the bucket-id of its output_hash.
    Items where all 10 runs share a hash -> single category. Items where 10 runs
    produce 10 distinct hashes -> 10 different categories. Fleiss handles this
    naturally because aggregate_raters bins by exact label.
    """
    by_run = {}
    for r in range(1, NUM_RUNS + 1):
        path = os.path.join(RAW_DIR, model, "extraction", f"run_{r:03d}", "results.json")
        with open(path) as f:
            data = json.load(f)
        by_run[r] = {item["corpus_id"]: item for item in data}
    all_ids = set(by_run[1].keys())
    for r in range(2, NUM_RUNS + 1):
        all_ids &= set(by_run[r].keys())
    corpus_ids = sorted(all_ids)
    matrix = []
    all_hashes = set()
    for cid in corpus_ids:
        row = []
        valid = True
        for r in range(1, NUM_RUNS + 1):
            h = by_run[r][cid].get("output_hash")
            if h is None:
                valid = False
                break
            row.append(h)
            all_hashes.add(h)
        if valid:
            matrix.append(row)
    return np.array(matrix, dtype=object), sorted(all_hashes)


def main() -> None:
    report = {
        "metadata": {
            "method": "Fleiss' kappa (Fleiss 1971) for inter-run agreement; "
                      "each of 10 LLM runs is one rater.",
            "se_formula": "Fleiss 1971 eq. 13 (asymptotic). 95% CI = kappa +- 1.96 * SE.",
            "interpretation": "Landis & Koch (1977): <0 poor, 0.0-0.2 slight, "
                              "0.21-0.4 fair, 0.41-0.6 moderate, 0.61-0.8 substantial, "
                              "0.81-1.0 almost perfect.",
            "seed": SEED,
            "num_runs": NUM_RUNS,
        },
        "screening": {},
        "extraction_overall_hash": {},
        "extraction_field": {f: {} for f in EXTR_CAT_FIELDS},
    }

    print("=" * 80)
    print(f"{'Model':<22} {'Stage/Field':<30} {'κ':>8} {'95% CI':>20} {'N items':>9}")
    print("-" * 80)

    for model in MODELS:
        # ---- Screening (3-class) ----
        try:
            scr = load_screening_decisions(model)
            res = fleiss_with_ci(scr, SCREEN_CATEGORIES)
            report["screening"][model] = res
            ci_str = f"[{res['ci_lower']:.3f}, {res['ci_upper']:.3f}]" if res["ci_lower"] is not None else "[--, --]"
            print(f"{model:<22} {'screening (3-class)':<30} {res['kappa']:>8.4f} {ci_str:>20} {res['n_items']:>9}")
        except Exception as e:
            report["screening"][model] = {"error": str(e)}
            print(f"{model:<22} {'screening':<30} ERROR: {e}")

        # ---- Extraction overall hash ----
        try:
            mat, all_hashes = load_extraction_hash_binary(model)
            # Use unique hashes as the implicit category set
            res = fleiss_with_ci(mat, all_hashes)
            report["extraction_overall_hash"][model] = res
            ci_str = f"[{res['ci_lower']:.3f}, {res['ci_upper']:.3f}]" if res["ci_lower"] is not None else "[--, --]"
            print(f"{model:<22} {'extraction hash (full out)':<30} {res['kappa']:>8.4f} {ci_str:>20} {res['n_items']:>9}")
        except Exception as e:
            report["extraction_overall_hash"][model] = {"error": str(e)}
            print(f"{model:<22} {'extraction hash':<30} ERROR: {e}")

        # ---- Extraction per categorical field ----
        for field in EXTR_CAT_FIELDS:
            try:
                mat = load_extraction_field(model, field)
                # Categories = unique observed
                cats = sorted({str(x) for row in mat for x in row})
                res = fleiss_with_ci(mat, cats)
                report["extraction_field"][field][model] = res
                ci_str = f"[{res['ci_lower']:.3f}, {res['ci_upper']:.3f}]" if res["ci_lower"] is not None else "[--, --]"
                print(f"{model:<22} {('extr ' + field):<30} {res['kappa']:>8.4f} {ci_str:>20} {res['n_items']:>9}")
            except Exception as e:
                report["extraction_field"][field][model] = {"error": str(e)}
                print(f"{model:<22} {('extr ' + field):<30} ERROR: {e}")

    print("=" * 80)
    payload = json.dumps(report, indent=2, sort_keys=False)
    sha = hashlib.sha256(payload.encode()).hexdigest()
    report["sha256_self"] = sha
    with open(OUT_PATH, "w") as f:
        json.dump(report, f, indent=2, sort_keys=False)
    print(f"\nWrote {OUT_PATH}")
    print(f"sha256: {sha}")


if __name__ == "__main__":
    main()
