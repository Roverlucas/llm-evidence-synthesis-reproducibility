"""
Semantic Equivalence Analysis + Meta-Analytic Propagation Experiment.

1. Semantic EMR: normalize text fields, compare with fuzzy matching
2. Meta-analysis: pool effect estimates per run, check if significance flips
"""
import json
import math
import os
import re
from collections import defaultdict
from pathlib import Path

BASE = Path("/Users/lucasrover/llm-evidence-synthesis-reproducibility")
RAW = BASE / "data" / "raw_outputs"
OUT = BASE / "analysis"

# ── Helpers ──────────────────────────────────────────────────

def load_results(model: str, stage: str, run: int) -> list:
    path = RAW / model / stage / f"run_{run:03d}" / "results.json"
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)

def normalize_text(s):
    """Normalize free-text for semantic comparison."""
    if s is None:
        return ""
    s = str(s).lower().strip()
    # Remove trailing punctuation
    s = s.rstrip(".,;:")
    # Normalize whitespace
    s = re.sub(r'\s+', ' ', s)
    # Normalize common abbreviations
    s = s.replace("united states of america", "united states")
    s = s.replace("u.s.a.", "united states")
    s = s.replace("u.s.", "united states")
    s = s.replace("usa", "united states")
    s = s.replace("u.k.", "united kingdom")
    s = s.replace("uk", "united kingdom")
    # Remove "the " prefix for locations
    if s.startswith("the "):
        s = s[4:]
    return s

def levenshtein_ratio(s1, s2):
    """Compute Levenshtein similarity ratio (0-1)."""
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    len1, len2 = len(s1), len(s2)
    if len1 == 0 or len2 == 0:
        return 0.0
    # Simple DP Levenshtein
    matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    for i in range(len1 + 1):
        matrix[i][0] = i
    for j in range(len2 + 1):
        matrix[0][j] = j
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            matrix[i][j] = min(
                matrix[i-1][j] + 1,
                matrix[i][j-1] + 1,
                matrix[i-1][j-1] + cost
            )
    distance = matrix[len1][len2]
    max_len = max(len1, len2)
    return 1.0 - (distance / max_len)


# ══════════════════════════════════════════════════════════════
#  PART 1: SEMANTIC EQUIVALENCE ANALYSIS
# ══════════════════════════════════════════════════════════════

def compute_semantic_emr(model: str, n_runs: int = 10):
    """Compute EMR at three levels: exact, normalized, fuzzy."""
    # Load all runs
    runs_data = {}
    for r in range(1, n_runs + 1):
        results = load_results(model, "extraction", r)
        for item in results:
            cid = item.get("corpus_id")
            output = item.get("output", {})
            # Include all items with outputs (not just valid ones)
            if cid and output:
                runs_data.setdefault(cid, {})[r] = output

    # Only keep articles present in all runs
    complete = {cid: data for cid, data in runs_data.items() if len(data) == n_runs}
    n_items = len(complete)
    if n_items == 0:
        return {}

    fields = ["study_design", "study_location", "study_period", "population", "sample_size"]

    # Per-field analysis
    field_results = {}
    for field in fields:
        exact_match = 0
        normalized_match = 0
        fuzzy_match = 0

        for cid, run_outputs in complete.items():
            values = [str(run_outputs.get(field, "")) for r, run_outputs in sorted(run_outputs.items())]

            # Exact match
            if len(set(values)) == 1:
                exact_match += 1
                normalized_match += 1
                fuzzy_match += 1
            else:
                # Normalized match
                norm_values = [normalize_text(v) for v in values]
                if len(set(norm_values)) == 1:
                    normalized_match += 1
                    fuzzy_match += 1
                else:
                    # Fuzzy match: all pairs above 0.9 similarity
                    ref = norm_values[0]
                    all_fuzzy = all(levenshtein_ratio(ref, v) >= 0.90 for v in norm_values[1:])
                    if all_fuzzy:
                        fuzzy_match += 1

        field_results[field] = {
            "exact_emr": round(exact_match / n_items, 3),
            "normalized_emr": round(normalized_match / n_items, 3),
            "fuzzy_emr": round(fuzzy_match / n_items, 3),
        }

    # Whole-output EMR at each level
    exact_whole = 0
    normalized_whole = 0
    fuzzy_whole = 0

    for cid, run_outputs in complete.items():
        all_exact = True
        all_normalized = True
        all_fuzzy = True

        for field in fields:
            values = [str(run_outputs.get(field, "")) for r, run_outputs in sorted(run_outputs.items())]
            if len(set(values)) != 1:
                all_exact = False
                norm_values = [normalize_text(v) for v in values]
                if len(set(norm_values)) != 1:
                    all_normalized = False
                    ref = norm_values[0]
                    if not all(levenshtein_ratio(ref, v) >= 0.90 for v in norm_values[1:]):
                        all_fuzzy = False

        # Also check estimate count
        est_counts = []
        for r, out in sorted(run_outputs.items()):
            estimates = out.get("estimates", [])
            est_counts.append(len(estimates))

        if len(set(est_counts)) != 1:
            all_exact = False
            all_normalized = False
            all_fuzzy = False

        if all_exact:
            exact_whole += 1
        if all_normalized:
            normalized_whole += 1
        if all_fuzzy:
            fuzzy_whole += 1

    return {
        "n_items": n_items,
        "field_results": field_results,
        "whole_output": {
            "exact_emr": round(exact_whole / n_items, 3),
            "normalized_emr": round(normalized_whole / n_items, 3),
            "fuzzy_emr": round(fuzzy_whole / n_items, 3),
        }
    }


# ══════════════════════════════════════════════════════════════
#  PART 2: META-ANALYTIC PROPAGATION EXPERIMENT
# ══════════════════════════════════════════════════════════════

def inverse_variance_meta(estimates):
    """
    Fixed-effect inverse-variance meta-analysis.
    Input: list of (log_effect, se) tuples.
    Returns: pooled_effect, pooled_se, z, p_value.
    """
    if not estimates:
        return None, None, None, None

    weights = []
    weighted_sum = 0.0
    for log_eff, se in estimates:
        if se <= 0:
            continue
        w = 1.0 / (se * se)
        weights.append(w)
        weighted_sum += w * log_eff

    if not weights:
        return None, None, None, None

    total_weight = sum(weights)
    pooled_log = weighted_sum / total_weight
    pooled_se = math.sqrt(1.0 / total_weight)
    z = pooled_log / pooled_se
    # Two-tailed p-value using normal approximation
    p = 2.0 * (1.0 - normal_cdf(abs(z)))

    pooled_effect = math.exp(pooled_log)
    return pooled_effect, pooled_se, z, p

def normal_cdf(x):
    """Standard normal CDF approximation."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def se_from_ci(log_lower, log_upper, ci_level=95):
    """Compute SE from log-transformed CI bounds."""
    if ci_level == 95:
        z = 1.96
    elif ci_level == 99:
        z = 2.576
    else:
        z = 1.96
    se = (log_upper - log_lower) / (2 * z)
    return se

def run_meta_analysis_experiment(model: str, n_runs: int = 10):
    """
    For each run, pool all RR estimates and compute significance.
    Show how the pooled estimate and p-value vary across runs.
    """
    run_results = []

    for r in range(1, n_runs + 1):
        results = load_results(model, "extraction", r)

        # Collect all usable estimates
        estimates_for_pooling = []
        articles_used = 0

        for item in results:
            output = item.get("output", {})
            estimates = output.get("estimates", [])

            for est in estimates:
                effect = est.get("effect_estimate")
                ci_lo = est.get("ci_lower")
                ci_hi = est.get("ci_upper")
                measure = est.get("effect_measure", "")

                # Only use RR/OR/HR with valid CIs
                if measure not in ("RR", "OR", "HR", "IRR"):
                    continue
                if effect is None or ci_lo is None or ci_hi is None:
                    continue
                try:
                    effect = float(effect)
                    ci_lo = float(ci_lo)
                    ci_hi = float(ci_hi)
                except (ValueError, TypeError):
                    continue
                if effect <= 0 or ci_lo <= 0 or ci_hi <= 0:
                    continue
                if ci_lo >= ci_hi:
                    continue

                try:
                    log_eff = math.log(effect)
                    log_lo = math.log(ci_lo)
                    log_hi = math.log(ci_hi)
                    se = se_from_ci(log_lo, log_hi)
                    if se > 0:
                        estimates_for_pooling.append((log_eff, se))
                        articles_used += 1
                except (ValueError, ZeroDivisionError):
                    continue

        pooled_eff, pooled_se, z, p = inverse_variance_meta(estimates_for_pooling)

        run_results.append({
            "run": r,
            "n_estimates": len(estimates_for_pooling),
            "pooled_effect": round(pooled_eff, 6) if pooled_eff is not None else None,
            "pooled_se": round(pooled_se, 6) if pooled_se is not None else None,
            "z_score": round(z, 4) if z is not None else None,
            "p_value": round(p, 6) if p is not None else None,
            "significant_005": p < 0.05 if p is not None else None,
        })

    return run_results


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    results = {}

    # ── Part 1: Semantic EMR ──
    print("=" * 60)
    print("PART 1: SEMANTIC EQUIVALENCE ANALYSIS")
    print("=" * 60)

    ALL_MODELS = [
        "llama3-8b", "mistral-7b", "gemma2-9b",
        "claude-sonnet-4-5", "gemini-2.5-pro", "gpt-4.1",
    ]

    for model in ALL_MODELS:
        print(f"\n── {model} ──")
        sem = compute_semantic_emr(model)
        results[f"{model}_semantic"] = sem

        if sem:
            print(f"  Items: {sem['n_items']}")
            print(f"\n  Whole-output EMR:")
            print(f"    Exact (hash):     {sem['whole_output']['exact_emr']}")
            print(f"    Normalized:       {sem['whole_output']['normalized_emr']}")
            print(f"    Fuzzy (≥90%):     {sem['whole_output']['fuzzy_emr']}")
            print(f"\n  Field-level EMR (Exact → Normalized → Fuzzy):")
            for field, vals in sem['field_results'].items():
                print(f"    {field:20s}  {vals['exact_emr']:.3f} → {vals['normalized_emr']:.3f} → {vals['fuzzy_emr']:.3f}")

    # ── Part 2: Meta-Analysis ──
    print("\n" + "=" * 60)
    print("PART 2: META-ANALYTIC PROPAGATION EXPERIMENT")
    print("=" * 60)

    for model in ALL_MODELS:
        print(f"\n── {model} ──")
        meta = run_meta_analysis_experiment(model)
        results[f"{model}_meta"] = meta

        effects = [r["pooled_effect"] for r in meta if r["pooled_effect"] is not None]
        p_values = [r["p_value"] for r in meta if r["p_value"] is not None]
        sig_counts = sum(1 for r in meta if r.get("significant_005"))

        print(f"  {'Run':>4s}  {'N est':>6s}  {'Pooled RR':>10s}  {'p-value':>10s}  {'Sig?':>5s}")
        print(f"  {'─'*4}  {'─'*6}  {'─'*10}  {'─'*10}  {'─'*5}")
        for r in meta:
            eff_str = f"{r['pooled_effect']:.4f}" if r['pooled_effect'] is not None else "---"
            p_str = f"{r['p_value']:.6f}" if r['p_value'] is not None else "---"
            sig_str = "YES" if r.get('significant_005') else "no"
            print(f"  {r['run']:4d}  {r['n_estimates']:6d}  {eff_str:>10s}  {p_str:>10s}  {sig_str:>5s}")

        if effects:
            print(f"\n  Pooled effect range: {min(effects):.4f} – {max(effects):.4f}")
            print(f"  P-value range:      {min(p_values):.6f} – {max(p_values):.6f}")
            print(f"  Significant at 0.05: {sig_counts}/{len(meta)} runs")
            if sig_counts > 0 and sig_counts < len(meta):
                print(f"  ⚠ SIGNIFICANCE FLIPS across runs!")

    # ── Part 3: Per-Article Significance Flip Analysis ──
    print("\n" + "=" * 60)
    print("PART 3: PER-ARTICLE SIGNIFICANCE FLIPS")
    print("=" * 60)

    for model in ALL_MODELS:
        print(f"\n── {model} ──")

        # For each article, per run: take the PRIMARY estimate (first RR/OR/HR)
        # and track whether it's significant across runs
        primary_sig = {}    # cid -> {run: bool}
        primary_effect = {} # cid -> {run: float}
        estimate_counts = {} # cid -> {run: int}

        for r in range(1, 11):
            run_results = load_results(model, "extraction", r)
            for item in run_results:
                cid = item.get("corpus_id")
                if not cid:
                    continue
                output = item.get("output", {})
                estimates = output.get("estimates", [])

                # Count all usable estimates
                usable = []
                for est in estimates:
                    effect = est.get("effect_estimate")
                    ci_lo = est.get("ci_lower")
                    ci_hi = est.get("ci_upper")
                    measure = est.get("effect_measure", "")

                    if measure not in ("RR", "OR", "HR", "IRR"):
                        continue
                    try:
                        effect = float(effect) if effect is not None else None
                        ci_lo = float(ci_lo) if ci_lo is not None else None
                        ci_hi = float(ci_hi) if ci_hi is not None else None
                    except (ValueError, TypeError):
                        continue
                    if not all(v is not None and v > 0
                              for v in [effect, ci_lo, ci_hi]):
                        continue
                    if ci_lo >= ci_hi:
                        continue
                    usable.append((effect, ci_lo, ci_hi))

                estimate_counts.setdefault(cid, {})[r] = len(usable)

                # Take primary (first) estimate
                if usable:
                    effect, ci_lo, ci_hi = usable[0]
                    sig = not (ci_lo <= 1.0 <= ci_hi)
                    primary_sig.setdefault(cid, {})[r] = sig
                    primary_effect.setdefault(cid, {})[r] = effect

        # Count articles with significance flips (primary estimate)
        total_articles = 0
        flipped_articles = 0
        varying_effects = 0
        varying_n_estimates = 0

        for cid, run_sigs in primary_sig.items():
            if len(run_sigs) >= 5:
                total_articles += 1
                sig_values = list(run_sigs.values())
                if True in sig_values and False in sig_values:
                    flipped_articles += 1

        for cid, run_effects in primary_effect.items():
            if len(run_effects) >= 5:
                effects = list(run_effects.values())
                if len(set(round(e, 4) for e in effects)) > 1:
                    varying_effects += 1

        for cid, run_counts in estimate_counts.items():
            counts = list(run_counts.values())
            if len(set(counts)) > 1:
                varying_n_estimates += 1

        flip_pct = flipped_articles / max(total_articles, 1) * 100

        print(f"  Articles with primary estimate in >=5 runs: {total_articles}")
        print(f"  Primary estimate significance FLIPS: {flipped_articles} ({flip_pct:.1f}%)")
        print(f"  Articles with varying primary effect: {varying_effects}/{total_articles}")
        print(f"  Articles with varying estimate counts: {varying_n_estimates}/{len(estimate_counts)}")

        # Show examples of flips
        flip_examples = []
        for cid, run_sigs in primary_sig.items():
            if len(run_sigs) >= 5:
                sig_values = list(run_sigs.values())
                if True in sig_values and False in sig_values:
                    effects = primary_effect.get(cid, {})
                    eff_vals = [effects[r] for r in sorted(effects.keys())]
                    sig_str = ''.join(['Y' if run_sigs.get(r, False) else 'n'
                                      for r in sorted(run_sigs.keys())])
                    flip_examples.append((cid, sig_str, min(eff_vals), max(eff_vals)))

        if flip_examples:
            print(f"\n  Example flips (Y=sig, n=not sig):")
            for cid, sig_str, eff_min, eff_max in flip_examples[:5]:
                print(f"    {cid}: [{sig_str}] effect={eff_min:.3f}–{eff_max:.3f}")

        results[f"{model}_flips"] = {
            "total_articles": total_articles,
            "flipped_articles": flipped_articles,
            "flip_pct": round(flip_pct, 1),
            "varying_effects": varying_effects,
            "varying_n_estimates": varying_n_estimates,
            "total_with_estimates": len(estimate_counts),
        }

    # ── Save results ──
    out_path = OUT / "semantic_and_meta_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n\nResults saved to {out_path}")
