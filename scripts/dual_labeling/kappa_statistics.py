"""Extended agreement statistics for the Stage-A dual-human screening.

``compute_kappa.py`` reports the point estimates that the pre-registration asked
for. Research Synthesis Methods reviewers will ask for more, and the paper's own
thesis — that point estimates hide variability — makes a bare kappa
self-undermining. This module adds:

    - analytic 95% CI for Cohen's kappa (Fleiss-Cohen-Everitt delta method, via
      statsmodels) plus percentile and BCa bootstrap for concordance
    - a one-sided test of kappa against the pre-specified Cochrane threshold
    - linearly and quadratically weighted kappa as a sensitivity check
    - PABAK, prevalence index and bias index, which together settle whether the
      low kappa is an artefact of skewed marginals (the "kappa paradox")
    - marginal-homogeneity tests (exact McNemar on the binary collapse,
      Stuart-Maxwell on the 3-class table) that formalise the directional
      criterion-5 divergence
    - stratum-specific agreement, which is where the gold standard turns out to
      be asymmetrically valid

Established implementations are preferred over hand-rolled formulas so a reviewer
can check the method against a citable source.

Usage:
    python scripts/dual_labeling/kappa_statistics.py \
        --labeler1 data/dual_labeling/returned/subset_100_labeler1_RETURNED.csv \
        --labeler2 data/dual_labeling/returned/subset_100_labeler2_RETURNED.csv \
        --subset data/dual_labeling/exports/subset_100.json \
        --out data/dual_labeling/results/kappa_statistics.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.contingency_tables import SquareTable, mcnemar
from statsmodels.stats.inter_rater import cohens_kappa

CATEGORIES = ["INCLUDE", "EXCLUDE", "UNCERTAIN"]
# Ordinal ordering for weighted kappa only: UNCERTAIN sits between the two poles.
ORDINAL_SCALE = ["INCLUDE", "UNCERTAIN", "EXCLUDE"]
COCHRANE_TARGET = 0.80
SEED = 42
N_BOOT = 10_000


def contingency(c1: np.ndarray, c2: np.ndarray, k: int) -> np.ndarray:
    """k x k contingency table over fixed integer codes, zeros kept.

    Built explicitly rather than via a helper so that categories absent from the
    data still occupy their row and column — dropping them would silently change
    the expected-agreement term.
    """
    table = np.zeros((k, k), dtype=float)
    for a, b in zip(c1, c2):
        table[int(a), int(b)] += 1
    return table


def coded(series: pd.Series, categories: list[str]) -> np.ndarray:
    """Map decisions onto integer codes in a fixed category order."""
    lookup = {c: i for i, c in enumerate(categories)}
    return series.astype(str).str.strip().str.upper().map(lookup).to_numpy()


def kappa_block(c1: np.ndarray, c2: np.ndarray, categories: list[str]) -> dict:
    """Point estimate, analytic SE/CI, weighted variants and PABAK."""
    k = len(categories)
    table = contingency(c1, c2, k)

    res = cohens_kappa(table, return_results=True)
    out = {
        "n": int(len(c1)),
        "categories": categories,
        "kappa": float(res.kappa),
        "se": float(res.std_kappa),
        "ci95": [float(res.kappa_low), float(res.kappa_upp)],
        "percent_agreement": float(np.mean(c1 == c2)),
        "confusion_matrix": table.astype(int).tolist(),
    }

    # Weighted kappa needs an ORDINAL scale, so it is computed on a re-ordered
    # table with UNCERTAIN between INCLUDE and EXCLUDE. Weighting the analysis
    # order (INCLUDE, EXCLUDE, UNCERTAIN) would treat include-vs-exclude as one
    # step and exclude-vs-uncertain as one step, which is not the intended scale.
    if k == 3 and categories == CATEGORIES:
        order = [CATEGORIES.index(c) for c in ORDINAL_SCALE]
        ordinal_table = table[np.ix_(order, order)]
        out["ordinal_scale_used"] = ORDINAL_SCALE
        for name, wt in [("linear", "linear"), ("quadratic", "quadratic")]:
            out[f"kappa_weighted_{name}"] = float(
                cohens_kappa(ordinal_table, wt=wt, return_results=True).kappa
            )

    # PABAK removes the prevalence/bias dependence that makes kappa hard to read.
    # Brennan-Prediger / PABAK generalised to k categories: (k*po - 1)/(k - 1).
    # The familiar 2*po-1 is the k=2 special case; applying it to a 3-class table
    # understates the coefficient (0.500 instead of 0.625 at po=0.75).
    _k = len(CATEGORIES)
    out["pabak"] = float((_k * out["percent_agreement"] - 1) / (_k - 1))
    out["pabak_n_categories"] = _k

    # One-sided test against the pre-specified threshold. Uses the observed SE,
    # not the null SE: the null SE is only valid for testing kappa = 0.
    if out["se"] > 0:
        z = (out["kappa"] - COCHRANE_TARGET) / out["se"]
        out["test_vs_cochrane"] = {
            "target": COCHRANE_TARGET,
            "z": float(z),
            "p_one_sided": float(stats.norm.cdf(z)),
            "below_target": bool(out["kappa"] < COCHRANE_TARGET),
        }
    return out


def bootstrap_ci(c1: np.ndarray, c2: np.ndarray, categories: list[str]) -> dict:
    """Percentile and BCa intervals for Cohen's kappa."""
    rng = np.random.default_rng(SEED)
    n, k = len(c1), len(categories)

    def kappa_of(idx: np.ndarray) -> float:
        t = contingency(c1[idx], c2[idx], k)
        po = np.trace(t) / t.sum()
        pe = float((t.sum(axis=0) / t.sum() * (t.sum(axis=1) / t.sum())).sum())
        return 1.0 if pe == 1.0 and po == 1.0 else (po - pe) / (1 - pe)

    theta_hat = kappa_of(np.arange(n))
    boot = np.array([kappa_of(rng.integers(0, n, n)) for _ in range(N_BOOT)])
    boot = boot[np.isfinite(boot)]

    percentile = [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]

    # BCa: bias correction z0 from the bootstrap distribution, acceleration a
    # from the jackknife.
    prop = np.mean(boot < theta_hat)
    result = {"theta_hat": float(theta_hat), "percentile_ci95": percentile,
              "n_boot": int(len(boot))}
    if 0 < prop < 1:
        z0 = stats.norm.ppf(prop)
        jack = np.array([kappa_of(np.delete(np.arange(n), i)) for i in range(n)])
        jack = jack[np.isfinite(jack)]
        dev = jack.mean() - jack
        denom = 6 * (np.sum(dev ** 2) ** 1.5)
        a = float(np.sum(dev ** 3) / denom) if denom != 0 else 0.0
        lo, hi = [], []
        for alpha, target in [(0.025, lo), (0.975, hi)]:
            zc = stats.norm.ppf(alpha)
            adj = z0 + (z0 + zc) / (1 - a * (z0 + zc))
            target.append(float(np.percentile(boot, 100 * stats.norm.cdf(adj))))
        result |= {"bca_ci95": [lo[0], hi[0]], "z0": float(z0), "acceleration": a}
    else:
        result |= {"bca_ci95": None,
                   "note": "BCa undefined: bootstrap distribution degenerate"}
    return result


def marginal_tests(c1: np.ndarray, c2: np.ndarray, binary_mask: np.ndarray) -> dict:
    """Is the disagreement directional, or symmetric noise?"""
    t3 = contingency(c1, c2, 3)
    # shift_zeros defaults to True, which adds 0.5 to every empty cell and makes
    # this 100-item table sum to 101. The continuity correction is meant for
    # sparse tables where a zero would make the statistic undefined; here both
    # statistics are well defined without it, and the published figure should
    # reproduce from the published table.
    sq = SquareTable(t3, shift_zeros=False)
    homogeneity = sq.homogeneity()  # Stuart-Maxwell
    symmetry = sq.symmetry()        # Bowker

    b1, b2 = c1[binary_mask], c2[binary_mask]
    t2 = contingency(b1, b2, 2)
    mc = mcnemar(t2, exact=True)

    return {
        "stuart_maxwell_3class": {
            "statistic": float(homogeneity.statistic),
            "df": int(homogeneity.df),
            "p_value": float(homogeneity.pvalue),
        },
        "bowker_symmetry_3class": {
            "statistic": float(symmetry.statistic),
            "df": int(symmetry.df),
            "p_value": float(symmetry.pvalue),
        },
        "mcnemar_binary_exact": {
            "statistic": float(mc.statistic),
            "p_value": float(mc.pvalue),
            "discordant_cells": [int(t2[0, 1]), int(t2[1, 0])],
            "n": int(binary_mask.sum()),
        },
        "interpretation": (
            "A significant result means the two labelers do not merely disagree, "
            "they disagree directionally: one is systematically more inclusive. "
            "That is the statistical signature of divergent protocol reading, not "
            "of random rater noise."
        ),
    }


def indices(c1: np.ndarray, c2: np.ndarray, binary_mask: np.ndarray) -> dict:
    """Prevalence and bias indices on the binary collapse (Byrt et al. 1993)."""
    b1, b2 = c1[binary_mask], c2[binary_mask]
    t = contingency(b1, b2, 2)
    n = t.sum()
    a, b, c, d = t[0, 0], t[0, 1], t[1, 0], t[1, 1]
    return {
        "prevalence_index": float(abs(a - d) / n),
        "bias_index": float(abs(b - c) / n),
        "note": (
            "A low prevalence index means the kappa paradox is NOT operating: the "
            "coefficient is not artificially depressed by skewed marginals, so the "
            "low value cannot be explained away on that ground."
        ),
    }


def per_stratum(df: pd.DataFrame) -> dict:
    """Agreement within each sampling stratum."""
    out = {}
    for name, grp in df.groupby("heuristic_category"):
        c1 = coded(grp["labeler1_decision"], CATEGORIES)
        c2 = coded(grp["labeler2_decision"], CATEGORIES)
        po = float(np.mean(c1 == c2))
        entry = {"n": int(len(grp)), "percent_agreement": po,
                 "pabak": float((len(CATEGORIES) * po - 1) / (len(CATEGORIES) - 1)),
                 "pabak_n_categories": len(CATEGORIES)}
        try:
            table = contingency(c1, c2, 3)
            pe = float((table.sum(axis=0) / table.sum()
                        * (table.sum(axis=1) / table.sum())).sum())
            if pe >= 1.0:
                entry |= {
                    "kappa": None,
                    "kappa_note": (
                        "undefined: expected agreement = 1 (degenerate marginals). "
                        "Perfect observed agreement with no reportable coefficient "
                        "— this is why PABAK is reported alongside."
                    ),
                }
            else:
                entry["kappa"] = float(cohens_kappa(table, return_results=True).kappa)
        except Exception as exc:
            entry |= {"kappa": None, "kappa_note": f"not computable: {exc}"}
        # How often did each labeler endorse the heuristic rule's own category?
        for lab in ("labeler1", "labeler2"):
            dec = grp[f"{lab}_decision"].astype(str).str.strip().str.upper()
            entry[f"{lab}_endorsed_stratum_label"] = int((dec == name.upper()).sum())
        out[name] = entry
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labeler1", required=True, type=Path)
    ap.add_argument("--labeler2", required=True, type=Path)
    ap.add_argument("--subset", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    l1 = pd.read_csv(args.labeler1)[["labeling_id", "labeler1_decision"]]
    l2 = pd.read_csv(args.labeler2)[["labeling_id", "labeler2_decision"]]
    subset = json.loads(args.subset.read_text())
    strata = pd.DataFrame(
        [{"labeling_id": i["labeling_id"],
          "heuristic_category": i["heuristic_category"]} for i in subset["items"]]
    )

    df = l1.merge(l2, on="labeling_id").merge(strata, on="labeling_id")
    if len(df) != len(l1):
        raise ValueError(f"join lost rows: {len(l1)} -> {len(df)}")

    c1 = coded(df["labeler1_decision"], CATEGORIES)
    c2 = coded(df["labeler2_decision"], CATEGORIES)
    binary_mask = (c1 != 2) & (c2 != 2)

    three = kappa_block(c1, c2, CATEGORIES)
    b1, b2 = c1[binary_mask], c2[binary_mask]
    binary = kappa_block(b1, b2, CATEGORIES[:2])

    payload = {
        "metadata": {
            "labeler1": "Isabelle", "labeler2": "Luiza Iltchechen",
            "protocol_version_at_labeling": "1.1",
            "seed": SEED, "n_bootstrap": N_BOOT,
            "sources": {"labeler1": str(args.labeler1), "labeler2": str(args.labeler2)},
        },
        "three_class": three,
        "binary_include_vs_exclude": binary,
        "bootstrap_three_class": bootstrap_ci(c1, c2, CATEGORIES),
        "marginal_homogeneity": marginal_tests(c1, c2, binary_mask),
        "byrt_indices": indices(c1, c2, binary_mask),
        "per_stratum": per_stratum(df),
        "decision_counts": {
            "labeler1": df["labeler1_decision"].value_counts().to_dict(),
            "labeler2": df["labeler2_decision"].value_counts().to_dict(),
        },
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False))

    t = three["test_vs_cochrane"]
    print(f"kappa 3-class = {three['kappa']:.4f}  95% CI "
          f"[{three['ci95'][0]:.3f}, {three['ci95'][1]:.3f}]  SE={three['se']:.4f}")
    print(f"kappa binary  = {binary['kappa']:.4f}  95% CI "
          f"[{binary['ci95'][0]:.3f}, {binary['ci95'][1]:.3f}]")
    print(f"vs Cochrane {COCHRANE_TARGET}: z={t['z']:.2f}  p={t['p_one_sided']:.2e}")
    print(f"PABAK={three['pabak']:.3f}  "
          f"prevalence={payload['byrt_indices']['prevalence_index']:.3f}  "
          f"bias={payload['byrt_indices']['bias_index']:.3f}")
    mh = payload["marginal_homogeneity"]
    print(f"Stuart-Maxwell chi2({mh['stuart_maxwell_3class']['df']})="
          f"{mh['stuart_maxwell_3class']['statistic']:.2f}  "
          f"p={mh['stuart_maxwell_3class']['p_value']:.2e}")
    print(f"McNemar exact p={mh['mcnemar_binary_exact']['p_value']:.2e}  "
          f"discordant={mh['mcnemar_binary_exact']['discordant_cells']}")
    boot = payload["bootstrap_three_class"]
    print(f"bootstrap percentile {[round(v,3) for v in boot['percentile_ci95']]}  "
          f"BCa {[round(v,3) for v in boot['bca_ci95']] if boot.get('bca_ci95') else None}")
    print("\nper stratum:")
    for name, s in payload["per_stratum"].items():
        k = f"{s['kappa']:.3f}" if s["kappa"] is not None else "undefined"
        print(f"  {name:10s} n={s['n']:3d}  agree={s['percent_agreement']:.3f}  "
              f"kappa={k:>9s}  PABAK={s['pabak']:.3f}")
    print(f"\nwritten: {args.out}")


if __name__ == "__main__":
    main()
