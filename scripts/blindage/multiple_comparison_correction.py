"""Multiple comparison correction for field-level EMR contrasts (P1.5, R3).

Per RSM P1.b audit: pairwise EMR contrasts between cloud APIs (Claude vs Gemini
vs GPT-4.1) are PAIRED proportions on the same 100 articles (or 500 abstracts
for screening overall EMR). The original implementation used a two-proportion
z-test (statsmodels.proportions_ztest semantics), which assumes independent
samples and inflates Type I error for paired data.

This script replaces that with McNemar's test on the article-level (or
abstract-level) binary outcome b_i^M = 1 if model M produced identical output
for item i across all 10 runs, else 0. McNemar is the canonical paired-binary
test: it conditions on the discordant pairs (cells b, c in the 2x2 table) and
uses an exact binomial p-value (mid-p when both b+c <= 25, asymptotic chi-square
with continuity correction otherwise; we use the asymptotic-with-correction by
default via statsmodels.stats.contingency_tables.mcnemar).

Holm-Bonferroni (FWER) and Benjamini-Hochberg (FDR) corrections are then applied
to the full set of contrasts.

Output: analysis/blindage/multiple_comparison.json
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from statsmodels.stats.contingency_tables import mcnemar

ROOT = Path(__file__).resolve().parents[2]
REPRO = ROOT / "analysis" / "reproducibility_results.json"
OUT = ROOT / "analysis" / "blindage" / "multiple_comparison.json"
RAW_DIR = ROOT / "data" / "raw_outputs"

CLOUD_MODELS = ["claude-sonnet-4-5", "gemini-2.5-pro", "gpt-4.1"]
FIELDS_EXTRACTION = ["study_design", "study_location", "study_period", "population", "sample_size"]
NUM_RUNS = 10
SEED = 42  # deterministic ordering only; mcnemar itself has no RNG


# ---------------------------------------------------------------------------
# Item-level paired binary outcomes
# ---------------------------------------------------------------------------
def load_extraction_runs(model: str) -> dict[int, list[dict]]:
    """{run_id: list_of_items}."""
    runs = {}
    for r in range(1, NUM_RUNS + 1):
        p = RAW_DIR / model / "extraction" / f"run_{r:03d}" / "results.json"
        with open(p) as f:
            runs[r] = json.load(f)
    return runs


def load_screening_runs(model: str) -> dict[int, list[dict]]:
    runs = {}
    for r in range(1, NUM_RUNS + 1):
        p = RAW_DIR / model / "screening" / f"run_{r:03d}" / "results.json"
        with open(p) as f:
            runs[r] = json.load(f)
    return runs


def per_article_field_match_vector(model: str, field: str) -> dict[str, int]:
    """{corpus_id: 1 if all 10 runs produced identical 'field' value, else 0}.

    Items where any run is missing/has-no-output are excluded (returned dict
    will not include that corpus_id).
    """
    runs = load_extraction_runs(model)
    # corpus_ids with output in ALL 10 runs (consistent with run_analysis.compute_extraction_field_variation)
    by_run = {r: {it["corpus_id"]: it for it in items} for r, items in runs.items()}
    all_ids = set(by_run[1].keys())
    for r in range(2, NUM_RUNS + 1):
        all_ids &= set(by_run[r].keys())
    out = {}
    for cid in sorted(all_ids):
        vals = []
        skip = False
        for r in range(1, NUM_RUNS + 1):
            it = by_run[r][cid]
            output = it.get("output")
            if output is None or "error" in (output or {}):
                skip = True
                break
            vals.append(str(output.get(field, "")))
        if skip:
            continue
        out[cid] = 1 if len(set(vals)) == 1 else 0
    return out


def per_article_extraction_overall_match_vector(model: str) -> dict[str, int]:
    """{corpus_id: 1 if all 10 runs produced identical output_hash, else 0}."""
    runs = load_extraction_runs(model)
    by_run = {r: {it["corpus_id"]: it for it in items} for r, items in runs.items()}
    all_ids = set(by_run[1].keys())
    for r in range(2, NUM_RUNS + 1):
        all_ids &= set(by_run[r].keys())
    out = {}
    for cid in sorted(all_ids):
        hashes = [by_run[r][cid].get("output_hash") for r in range(1, NUM_RUNS + 1)]
        if any(h is None for h in hashes):
            continue
        out[cid] = 1 if len(set(hashes)) == 1 else 0
    return out


def per_abstract_screening_match_vector(model: str) -> dict[str, int]:
    """{corpus_id: 1 if all 10 runs gave the same screening decision, else 0}."""
    runs = load_screening_runs(model)
    by_run = {r: {it["corpus_id"]: it for it in items} for r, items in runs.items()}
    all_ids = set(by_run[1].keys())
    for r in range(2, NUM_RUNS + 1):
        all_ids &= set(by_run[r].keys())
    out = {}
    for cid in sorted(all_ids):
        decisions = []
        skip = False
        for r in range(1, NUM_RUNS + 1):
            it = by_run[r][cid]
            output = it.get("output")
            if output is None:
                skip = True
                break
            decisions.append(str(output.get("decision", "")))
        if skip:
            continue
        out[cid] = 1 if len(set(decisions)) == 1 else 0
    return out


# ---------------------------------------------------------------------------
# McNemar pairwise test
# ---------------------------------------------------------------------------
def mcnemar_pair(v1: dict[str, int], v2: dict[str, int]) -> dict:
    """Paired McNemar on the common items.

    Contingency:
                       M2 match  M2 mismatch
        M1 match           a           b
        M1 mismatch        c           d
    McNemar tests H0: P(M1 match) = P(M2 match), conditional on discordants
    (b + c). We use statsmodels' default chi-square with continuity correction
    when b + c >= 25, else the exact binomial mid-p.
    """
    common = sorted(set(v1) & set(v2))
    a = b = c = d = 0
    for cid in common:
        x, y = v1[cid], v2[cid]
        if x == 1 and y == 1: a += 1
        elif x == 1 and y == 0: b += 1
        elif x == 0 and y == 1: c += 1
        else: d += 1
    table = [[a, b], [c, d]]
    n = a + b + c + d
    p1 = (a + b) / n if n else 0.0  # M1 match rate
    p2 = (a + c) / n if n else 0.0  # M2 match rate
    # statsmodels: exact=True for binomial when discordants <= 25, else chi-sq w/ correction
    if (b + c) == 0:
        # Perfect agreement -> no test statistic; null cannot be rejected
        return {
            "n_common": n, "a": a, "b": b, "c": c, "d": d,
            "p_M1": round(p1, 4), "p_M2": round(p2, 4),
            "discordants": 0,
            "test": "no_discordants",
            "raw_p_value": 1.0,
            "statistic": None,
        }
    use_exact = (b + c) <= 25
    res = mcnemar(table, exact=use_exact, correction=not use_exact)
    return {
        "n_common": n, "a": a, "b": b, "c": c, "d": d,
        "p_M1": round(p1, 4), "p_M2": round(p2, 4),
        "discordants": b + c,
        "test": "exact_binomial" if use_exact else "chi2_continuity_corrected",
        "raw_p_value": float(res.pvalue),
        "statistic": float(res.statistic) if res.statistic is not None else None,
    }


# ---------------------------------------------------------------------------
# Multiple comparison correction
# ---------------------------------------------------------------------------
def holm_bonferroni(ps: list[float]) -> list[float]:
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    adj = [0.0] * m
    prev = 0.0
    for rank, idx in enumerate(order):
        adj_p = (m - rank) * ps[idx]
        adj_p = min(1.0, max(adj_p, prev))
        prev = adj_p
        adj[idx] = adj_p
    return adj


def benjamini_hochberg(ps: list[float]) -> list[float]:
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    adj = [0.0] * m
    prev = 1.0
    for rank in range(m - 1, -1, -1):
        idx = order[rank]
        adj_p = ps[idx] * m / (rank + 1)
        adj_p = min(1.0, min(adj_p, prev))
        prev = adj_p
        adj[idx] = adj_p
    return adj


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    np.random.seed(SEED)

    # Build per-model item-level vectors
    print("Building paired item-level binary vectors ...")
    field_vecs = {m: {} for m in CLOUD_MODELS}
    for m in CLOUD_MODELS:
        for f in FIELDS_EXTRACTION:
            field_vecs[m][f] = per_article_field_match_vector(m, f)
        print(f"  {m}: extraction fields built ({len(field_vecs[m][FIELDS_EXTRACTION[0]])} articles)")

    ext_overall = {m: per_article_extraction_overall_match_vector(m) for m in CLOUD_MODELS}
    scr_overall = {m: per_abstract_screening_match_vector(m) for m in CLOUD_MODELS}
    for m in CLOUD_MODELS:
        print(f"  {m}: extraction overall ({len(ext_overall[m])}), screening overall ({len(scr_overall[m])})")

    contrasts = []
    pairs = [(CLOUD_MODELS[i], CLOUD_MODELS[j])
             for i in range(len(CLOUD_MODELS))
             for j in range(i + 1, len(CLOUD_MODELS))]

    # Per-field contrasts
    for field in FIELDS_EXTRACTION:
        for m1, m2 in pairs:
            v1, v2 = field_vecs[m1][field], field_vecs[m2][field]
            r = mcnemar_pair(v1, v2)
            contrasts.append({
                "field": field, "stage": "extraction_field",
                "model_1": m1, "model_2": m2,
                "p_M1_consistency": r["p_M1"], "p_M2_consistency": r["p_M2"],
                "emr_diff": round(r["p_M1"] - r["p_M2"], 4),
                "n_common": r["n_common"],
                "discordants": r["discordants"],
                "b_cell_M1match_M2miss": r["b"], "c_cell_M1miss_M2match": r["c"],
                "test": r["test"],
                "raw_p_value": round(r["raw_p_value"], 6),
                "statistic": r["statistic"],
            })

    # Overall extraction EMR contrasts
    for m1, m2 in pairs:
        r = mcnemar_pair(ext_overall[m1], ext_overall[m2])
        contrasts.append({
            "field": "extraction_overall_EMR", "stage": "extraction",
            "model_1": m1, "model_2": m2,
            "p_M1_consistency": r["p_M1"], "p_M2_consistency": r["p_M2"],
            "emr_diff": round(r["p_M1"] - r["p_M2"], 4),
            "n_common": r["n_common"],
            "discordants": r["discordants"],
            "b_cell_M1match_M2miss": r["b"], "c_cell_M1miss_M2match": r["c"],
            "test": r["test"],
            "raw_p_value": round(r["raw_p_value"], 6),
            "statistic": r["statistic"],
        })

    # Overall screening EMR contrasts
    for m1, m2 in pairs:
        r = mcnemar_pair(scr_overall[m1], scr_overall[m2])
        contrasts.append({
            "field": "screening_overall_EMR", "stage": "screening",
            "model_1": m1, "model_2": m2,
            "p_M1_consistency": r["p_M1"], "p_M2_consistency": r["p_M2"],
            "emr_diff": round(r["p_M1"] - r["p_M2"], 4),
            "n_common": r["n_common"],
            "discordants": r["discordants"],
            "b_cell_M1match_M2miss": r["b"], "c_cell_M1miss_M2match": r["c"],
            "test": r["test"],
            "raw_p_value": round(r["raw_p_value"], 6),
            "statistic": r["statistic"],
        })

    ps = [c["raw_p_value"] for c in contrasts]
    holm = holm_bonferroni(ps)
    bh = benjamini_hochberg(ps)
    for c, h, b_ in zip(contrasts, holm, bh):
        c["holm_adj_p"] = round(h, 6)
        c["bh_fdr_adj_p"] = round(b_, 6)
        c["significant_raw_05"] = c["raw_p_value"] < 0.05
        c["significant_holm_05"] = c["holm_adj_p"] < 0.05
        c["significant_bh_05"] = c["bh_fdr_adj_p"] < 0.05

    n_sig_raw = sum(1 for c in contrasts if c["significant_raw_05"])
    n_sig_holm = sum(1 for c in contrasts if c["significant_holm_05"])
    n_sig_bh = sum(1 for c in contrasts if c["significant_bh_05"])

    report = {
        "method": (
            "McNemar paired test on per-item binary consistency (1=all 10 runs identical, "
            "0=otherwise) for each pair of cloud-API deployment stacks. Replaces the prior "
            "two-proportion z-test (which incorrectly assumed independent samples)."
        ),
        "test_implementation": (
            "statsmodels.stats.contingency_tables.mcnemar. Exact mid-p binomial when "
            "discordants (b+c) <= 25; chi-square with continuity correction otherwise."
        ),
        "corrections": {
            "holm_bonferroni": "Step-down adjusted p-values, FWER control",
            "benjamini_hochberg": "BH-FDR, false discovery rate control",
        },
        "n_contrasts_total": len(contrasts),
        "n_significant_raw_0.05": n_sig_raw,
        "n_significant_holm_0.05": n_sig_holm,
        "n_significant_bh_0.05": n_sig_bh,
        "seed": SEED,
        "contrasts": contrasts,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, indent=2, sort_keys=False)
    sha = hashlib.sha256(payload.encode()).hexdigest()
    report["sha256_self"] = sha
    OUT.write_text(json.dumps(report, indent=2, sort_keys=False))

    print(f"\nTotal contrasts: {len(contrasts)}")
    print(f"  Significant at raw p<0.05: {n_sig_raw}")
    print(f"  Significant after Holm-Bonferroni: {n_sig_holm}")
    print(f"  Significant after BH-FDR: {n_sig_bh}")
    print()
    print(f"{'Field':<26} {'Pair':<40} {'b':>4} {'c':>4} {'Δp':>8} {'Raw p':>10} {'Holm':>10} {'BH':>10}")
    for c in contrasts:
        marker = "*" if c["significant_holm_05"] else ("." if c["significant_bh_05"] else " ")
        print(f"{c['field']:<26} {c['model_1']+' vs '+c['model_2']:<40} "
              f"{c['b_cell_M1match_M2miss']:>4} {c['c_cell_M1miss_M2match']:>4} "
              f"{c['emr_diff']:>8.4f} {c['raw_p_value']:>10.4f} "
              f"{c['holm_adj_p']:>10.4f} {c['bh_fdr_adj_p']:>10.4f} {marker}")
    print(f"\n(* = Holm significant, . = BH-FDR significant)")
    print(f"\nWrote {OUT.relative_to(ROOT)}")
    print(f"sha256: {sha}")


if __name__ == "__main__":
    main()
