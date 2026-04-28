"""Cross-validate silver-internal (6 models × 10 runs majority) vs
silver-external (DeepSeek-R1 × 5 runs majority).

If silvers converge highly, both are validated as comparative anchors and
the original 6 models are NOT systematically biased relative to an
independent reasoning model.

Output: analysis/blindage/silver_cross_validation.json
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INTERNAL = ROOT / "analysis" / "blindage" / "silver_standard_internal.json"
EXTERNAL = ROOT / "analysis" / "blindage" / "silver_standard_external.json"
OUT = ROOT / "analysis" / "blindage" / "silver_cross_validation.json"

NUMERIC_FIELDS = ["effect_estimate", "ci_lower", "ci_upper"]
CATEGORICAL_FIELDS = ["effect_measure", "outcome_specific", "exposure_increment", "lag"]
NUMERIC_TOL = 0.05  # More tolerant since these are independent consensuses


def num_match(a, b, tol=NUMERIC_TOL):
    if a is None or b is None:
        return None  # Cannot compare
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return None


def cat_match(a, b):
    if a is None or b is None:
        return None
    return str(a).strip().lower() == str(b).strip().lower()


def main():
    si = json.loads(INTERNAL.read_text())["silver_by_item"]
    se = json.loads(EXTERNAL.read_text())["silver_by_item"]

    common = sorted(set(si) & set(se))
    field_results = {}
    for f in NUMERIC_FIELDS + CATEGORICAL_FIELDS:
        n_compared = 0
        n_match = 0
        n_si_only = 0
        n_se_only = 0
        for cid in common:
            si_val = si[cid]["consensus"].get(f)
            se_val = se[cid]["consensus"].get(f)
            if f in NUMERIC_FIELDS:
                cmp = num_match(si_val, se_val)
            else:
                cmp = cat_match(si_val, se_val)
            if cmp is None:
                if si_val is not None and se_val is None:
                    n_se_only += 1
                elif se_val is not None and si_val is None:
                    n_si_only += 1
                continue
            n_compared += 1
            if cmp:
                n_match += 1
        agreement = (n_match / n_compared) if n_compared else None
        field_results[f] = {
            "n_compared": n_compared,
            "n_match": n_match,
            "agreement": round(agreement, 4) if agreement is not None else None,
            "n_only_internal": n_si_only,
            "n_only_external": n_se_only,
        }

    # Spearman ρ on numeric effect_estimate (rank correlation)
    pairs = []
    for cid in common:
        a = si[cid]["consensus"].get("effect_estimate")
        b = se[cid]["consensus"].get("effect_estimate")
        if a is not None and b is not None:
            try:
                pairs.append((float(a), float(b)))
            except (TypeError, ValueError):
                pass

    def rank(values):
        sorted_idx = sorted(range(len(values)), key=lambda i: values[i])
        ranks = [0.0] * len(values)
        for r, i in enumerate(sorted_idx):
            ranks[i] = r + 1
        return ranks

    if len(pairs) >= 2:
        a_vals = [p[0] for p in pairs]
        b_vals = [p[1] for p in pairs]
        a_ranks = rank(a_vals)
        b_ranks = rank(b_vals)
        n = len(pairs)
        mean_a = sum(a_ranks) / n
        mean_b = sum(b_ranks) / n
        cov = sum((a_ranks[i] - mean_a) * (b_ranks[i] - mean_b) for i in range(n))
        var_a = sum((x - mean_a) ** 2 for x in a_ranks)
        var_b = sum((x - mean_b) ** 2 for x in b_ranks)
        spearman = cov / math.sqrt(var_a * var_b) if var_a > 0 and var_b > 0 else None
    else:
        spearman = None

    report = {
        "method": "Cross-validation of silver-internal (6 models × 10 runs majority) "
                  "vs silver-external (DeepSeek-R1 × 5 runs majority).",
        "numeric_tolerance": NUMERIC_TOL,
        "n_common_items": len(common),
        "field_agreement": field_results,
        "spearman_rho_effect_estimate": round(spearman, 4) if spearman is not None else None,
        "n_pairs_for_spearman": len(pairs),
        "interpretation": (
            "Silvers converge well (≥75% agreement on most fields)" if all(
                fr["agreement"] is not None and fr["agreement"] >= 0.75
                for fr in field_results.values()
            )
            else "Silvers diverge on at least one field — investigate"
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2))

    print(f"Common items: {len(common)}")
    print(f"\n{'Field':<25} {'n_compared':>12} {'n_match':>10} {'agreement':>12}")
    for f, r in field_results.items():
        ag = f"{r['agreement']:.4f}" if r['agreement'] is not None else "NA"
        print(f"{f:<25} {r['n_compared']:>12} {r['n_match']:>10} {ag:>12}")
    print(f"\nSpearman ρ on effect_estimate: {spearman:.4f}" if spearman else "\nSpearman ρ: NA")
    print(f"\n{report['interpretation']}")
    print(f"\nWrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
