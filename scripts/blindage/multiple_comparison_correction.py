"""Multiple comparison correction for field-level EMR contrasts (P1.5, R3).

Applies Holm-Bonferroni and Benjamini-Hochberg FDR correction to the pairwise
field-level EMR contrasts between cloud API models (Claude vs Gemini vs GPT-4.1).

Tests per field: 3 pairwise comparisons × 5 fields = 15 contrasts per stage.
Null hypothesis: two models have equal field-level EMR (H0: p1 = p2).
Test: two-proportion z-test on n_matches / n_items.

Output: analysis/blindage/multiple_comparison.json
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPRO = ROOT / "analysis" / "reproducibility_results.json"
OUT = ROOT / "analysis" / "blindage" / "multiple_comparison.json"

CLOUD_MODELS = ["claude-sonnet-4-5", "gemini-2.5-pro", "gpt-4.1"]


def z_test_two_props(p1: float, n1: int, p2: float, n2: int) -> float:
    """Two-proportion z-test. Returns p-value (two-sided)."""
    if n1 == 0 or n2 == 0:
        return 1.0
    k1 = p1 * n1
    k2 = p2 * n2
    p_pool = (k1 + k2) / (n1 + n2)
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    if se == 0:
        return 1.0 if p1 == p2 else 0.0
    z = (p1 - p2) / se
    # Two-sided p-value
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    return p


def holm_bonferroni(ps: list[float]) -> list[float]:
    """Holm-Bonferroni step-down adjusted p-values."""
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    adj = [0.0] * m
    prev = 0.0
    for rank, idx in enumerate(order):
        adj_p = (m - rank) * ps[idx]
        adj_p = min(1.0, max(adj_p, prev))  # monotone
        prev = adj_p
        adj[idx] = adj_p
    return adj


def benjamini_hochberg(ps: list[float]) -> list[float]:
    """Benjamini-Hochberg FDR adjusted p-values."""
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    adj = [0.0] * m
    prev = 1.0
    for rank in range(m - 1, -1, -1):
        idx = order[rank]
        adj_p = ps[idx] * m / (rank + 1)
        adj_p = min(1.0, min(adj_p, prev))  # monotone non-decreasing
        prev = adj_p
        adj[idx] = adj_p
    return adj


def main() -> None:
    repro = json.loads(REPRO.read_text())
    # For each cloud model, collect field_emr dict
    fields = None
    field_emrs = {}  # {model: {field: emr}}
    n_items = {}
    for m in CLOUD_MODELS:
        ext = repro[m]["extraction"]
        field_emrs[m] = ext["field_emr"]
        n_items[m] = ext["n_articles"]
        if fields is None:
            fields = sorted(ext["field_emr"].keys())

    contrasts = []
    for field in fields:
        pairs = [(CLOUD_MODELS[i], CLOUD_MODELS[j])
                 for i in range(len(CLOUD_MODELS))
                 for j in range(i + 1, len(CLOUD_MODELS))]
        for m1, m2 in pairs:
            p1 = field_emrs[m1][field]
            p2 = field_emrs[m2][field]
            n1 = n_items[m1]
            n2 = n_items[m2]
            p = z_test_two_props(p1, n1, p2, n2)
            contrasts.append({
                "field": field,
                "model_1": m1,
                "emr_1": round(p1, 4),
                "n_1": n1,
                "model_2": m2,
                "emr_2": round(p2, 4),
                "n_2": n2,
                "raw_p_value": round(p, 6),
                "emr_diff": round(p1 - p2, 4),
            })

    # Also include global EMR contrasts across stages
    for stage in ("screening", "extraction"):
        pairs = [(CLOUD_MODELS[i], CLOUD_MODELS[j])
                 for i in range(len(CLOUD_MODELS))
                 for j in range(i + 1, len(CLOUD_MODELS))]
        for m1, m2 in pairs:
            s1 = repro[m1][stage]
            s2 = repro[m2][stage]
            p1 = s1["emr"]
            p2 = s2["emr"]
            n1 = s1.get("n_abstracts") or s1.get("n_articles")
            n2 = s2.get("n_abstracts") or s2.get("n_articles")
            p = z_test_two_props(p1, n1, p2, n2)
            contrasts.append({
                "field": f"{stage}_overall_EMR",
                "model_1": m1,
                "emr_1": round(p1, 4),
                "n_1": n1,
                "model_2": m2,
                "emr_2": round(p2, 4),
                "n_2": n2,
                "raw_p_value": round(p, 6),
                "emr_diff": round(p1 - p2, 4),
            })

    ps = [c["raw_p_value"] for c in contrasts]
    holm = holm_bonferroni(ps)
    bh = benjamini_hochberg(ps)
    for c, h, b in zip(contrasts, holm, bh):
        c["holm_adj_p"] = round(h, 6)
        c["bh_fdr_adj_p"] = round(b, 6)
        c["significant_raw_05"] = c["raw_p_value"] < 0.05
        c["significant_holm_05"] = c["holm_adj_p"] < 0.05
        c["significant_bh_05"] = c["bh_fdr_adj_p"] < 0.05

    n_sig_raw = sum(1 for c in contrasts if c["significant_raw_05"])
    n_sig_holm = sum(1 for c in contrasts if c["significant_holm_05"])
    n_sig_bh = sum(1 for c in contrasts if c["significant_bh_05"])

    report = {
        "method": "Two-proportion z-test on pairwise field-level EMR contrasts between cloud APIs.",
        "corrections": {
            "holm_bonferroni": "Step-down adjusted p-values, FWER control",
            "benjamini_hochberg": "BH-FDR, false discovery rate control",
        },
        "n_contrasts_total": len(contrasts),
        "n_significant_raw_0.05": n_sig_raw,
        "n_significant_holm_0.05": n_sig_holm,
        "n_significant_bh_0.05": n_sig_bh,
        "contrasts": contrasts,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2))

    # Print headline table
    print(f"Total contrasts: {len(contrasts)}")
    print(f"  Significant at raw p<0.05: {n_sig_raw}")
    print(f"  Significant after Holm-Bonferroni: {n_sig_holm}")
    print(f"  Significant after BH-FDR: {n_sig_bh}")
    print()
    print(f"{'Field':<28} {'Models':<40} {'Δ EMR':>8} {'Raw p':>10} {'Holm':>10} {'BH':>10}")
    for c in contrasts:
        marker = "*" if c["significant_holm_05"] else ("•" if c["significant_bh_05"] else " ")
        print(f"{c['field']:<28} {c['model_1']+' vs '+c['model_2']:<40} {c['emr_diff']:>8.4f} {c['raw_p_value']:>10.4f} {c['holm_adj_p']:>10.4f} {c['bh_fdr_adj_p']:>10.4f} {marker}")
    print(f"\n(* = Holm significant, • = BH-FDR significant)")
    print(f"\nWrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
