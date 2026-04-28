"""Small-literature simulation (P0.2, R2/R4/R5 blocker).

For each model × run, subsample k in {10, 15, 20} articles and compute
pooled random-effects estimate (DerSimonian-Laird). Check whether:
    (a) 95% CI crosses null (RR=1) in ANY of the 10 runs for a given subsample
    (b) distribution of pooled point estimates across runs is wider for smaller k

This addresses the "So what?" question by demonstrating concrete scenarios
where LLM non-determinism changes the meta-analytic conclusion.

Output: analysis/blindage/small_literature_sim.json
"""
from __future__ import annotations

import json
import math
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "analysis" / "blindage" / "extraction_long.json"
OUT = ROOT / "analysis" / "blindage" / "small_literature_sim.json"

MODELS = ["llama3-8b", "mistral-7b", "gemma2-9b",
          "claude-sonnet-4-5", "gemini-2.5-pro", "gpt-4.1"]

SEED = 42
K_VALUES = [10, 15, 20, 30]
N_SUBSAMPLES = 200  # Subsample iterations per k
ALPHA = 0.05


def valid_log_rr(r: dict) -> tuple[float, float] | None:
    """Return (log_rr, variance) if record has valid effect estimate."""
    rr = r.get("effect_estimate")
    lo = r.get("ci_lower")
    hi = r.get("ci_upper")
    if rr is None or lo is None or hi is None:
        return None
    try:
        rr, lo, hi = float(rr), float(lo), float(hi)
    except (TypeError, ValueError):
        return None
    # Sanity: must be positive, lo < rr < hi, all within epidemiologically plausible range
    if rr <= 0 or lo <= 0 or hi <= 0:
        return None
    if not (lo < rr < hi):
        return None
    if rr < 0.3 or rr > 5.0:
        return None
    log_rr = math.log(rr)
    # SE from CI: log(hi) - log(lo) = 2 * 1.96 * SE  =>  SE = (log(hi) - log(lo)) / (2*1.96)
    se = (math.log(hi) - math.log(lo)) / (2 * 1.96)
    var = se * se
    if var <= 0:
        return None
    return log_rr, var


def pool_random_effects(estimates: list[tuple[float, float]]) -> dict:
    """DerSimonian-Laird random-effects meta-analysis.

    Returns dict with pooled_log_rr, pooled_rr, se, ci_lower, ci_upper, tau2, Q, k.
    """
    k = len(estimates)
    if k < 2:
        return None
    thetas = [e[0] for e in estimates]
    vars_fe = [e[1] for e in estimates]
    w = [1.0 / v for v in vars_fe]
    sum_w = sum(w)
    sum_wt = sum(wi * ti for wi, ti in zip(w, thetas))
    theta_fe = sum_wt / sum_w
    # Heterogeneity Q
    Q = sum(wi * (ti - theta_fe) ** 2 for wi, ti in zip(w, thetas))
    df = k - 1
    sum_w2 = sum(wi ** 2 for wi in w)
    c = sum_w - sum_w2 / sum_w
    tau2 = max(0.0, (Q - df) / c) if c > 0 else 0.0
    # Random-effects weights
    w_star = [1.0 / (v + tau2) for v in vars_fe]
    sum_ws = sum(w_star)
    theta_re = sum(wi * ti for wi, ti in zip(w_star, thetas)) / sum_ws
    se_re = math.sqrt(1.0 / sum_ws)
    z = 1.959964  # 0.975 quantile
    ci_lo_log = theta_re - z * se_re
    ci_hi_log = theta_re + z * se_re
    rr_pooled = math.exp(theta_re)
    return {
        "pooled_log_rr": theta_re,
        "pooled_rr": rr_pooled,
        "se_log": se_re,
        "ci_lower_rr": math.exp(ci_lo_log),
        "ci_upper_rr": math.exp(ci_hi_log),
        "tau2": tau2,
        "Q": Q,
        "df": df,
        "k": k,
        "crosses_null": ci_lo_log < 0 < ci_hi_log,
    }


def first_estimate_per_item(rows: list[dict]) -> list[tuple[str, tuple[float, float]]]:
    """Per (corpus_id), keep the first valid estimate (estimate_idx=0).

    Returns list of (corpus_id, (log_rr, var)).
    """
    out = []
    for r in rows:
        if r["estimate_idx"] != 0:
            continue
        if r["effect_measure"] not in ("RR", "OR", "HR", "IRR"):
            continue
        le = valid_log_rr(r)
        if le is None:
            continue
        out.append((r["corpus_id"], le))
    return out


def main() -> None:
    rows = json.loads(INPUT.read_text())
    # Organize: rows_per_model[model][run_id] = list of {corpus_id, estimate}
    rows_per_model = defaultdict(lambda: defaultdict(list))
    for r in rows:
        rows_per_model[r["model"]][r["run_id"]].append(r)

    rng = random.Random(SEED)

    report = {"metadata": {
        "k_values": K_VALUES,
        "n_subsamples_per_k": N_SUBSAMPLES,
        "seed": SEED,
        "pooling_method": "DerSimonian-Laird random-effects on log(RR)",
        "null_value": 1.0,
    }, "models": {}}

    for model in MODELS:
        report["models"][model] = {}
        runs_dict = rows_per_model[model]
        if not runs_dict:
            continue
        run_ids = sorted(runs_dict)
        # For each run, build list of (corpus_id, log_rr, var)
        run_estimates = {}
        for run_id in run_ids:
            pairs = first_estimate_per_item(runs_dict[run_id])
            run_estimates[run_id] = dict(pairs)

        # Union of all corpus_ids that have a valid estimate in ANY run
        all_ids = set()
        for run_id, d in run_estimates.items():
            all_ids.update(d)
        all_ids = sorted(all_ids)

        if len(all_ids) < max(K_VALUES):
            print(f"SKIP {model}: only {len(all_ids)} items with valid first-estimate")
            continue

        for k in K_VALUES:
            subsample_results = []
            n_with_null_crossing_in_any_run = 0
            for sample_idx in range(N_SUBSAMPLES):
                sampled_ids = rng.sample(all_ids, k)
                per_run_pooled = {}
                any_null_crossing = False
                for run_id in run_ids:
                    est_for_run = []
                    for cid in sampled_ids:
                        if cid in run_estimates[run_id]:
                            est_for_run.append(run_estimates[run_id][cid])
                    if len(est_for_run) < 2:
                        per_run_pooled[run_id] = None
                        continue
                    pooled = pool_random_effects(est_for_run)
                    per_run_pooled[run_id] = pooled
                    if pooled and pooled["crosses_null"]:
                        any_null_crossing = True
                if any_null_crossing:
                    n_with_null_crossing_in_any_run += 1
                # Aggregate across runs: variation in pooled_rr
                valid_rrs = [v["pooled_rr"] for v in per_run_pooled.values() if v]
                valid_crosses = [v["crosses_null"] for v in per_run_pooled.values() if v]
                if valid_rrs:
                    subsample_results.append({
                        "sampled_ids": sampled_ids,
                        "pooled_rrs_per_run": {str(rid): (per_run_pooled[rid]["pooled_rr"] if per_run_pooled[rid] else None) for rid in run_ids},
                        "range_pooled_rr": max(valid_rrs) - min(valid_rrs),
                        "min_pooled_rr": min(valid_rrs),
                        "max_pooled_rr": max(valid_rrs),
                        "n_runs_cross_null": sum(valid_crosses),
                        "any_run_cross_null": any(valid_crosses),
                        "all_runs_cross_null": all(valid_crosses) if valid_crosses else False,
                    })
            # Summary
            ranges = [s["range_pooled_rr"] for s in subsample_results]
            n_any_cross = sum(1 for s in subsample_results if s["any_run_cross_null"])
            n_all_cross = sum(1 for s in subsample_results if s["all_runs_cross_null"])
            # Cases where null crossing CHANGES across runs (unstable)
            n_unstable_null = sum(1 for s in subsample_results
                                  if 0 < s["n_runs_cross_null"] < len(run_ids))
            ranges_sorted = sorted(ranges)
            mean_range = sum(ranges) / len(ranges) if ranges else 0.0
            median_range = ranges_sorted[len(ranges_sorted) // 2] if ranges_sorted else 0.0
            p95_range = ranges_sorted[min(len(ranges_sorted) - 1, int(0.95 * len(ranges_sorted)))] if ranges_sorted else 0.0
            report["models"][model][f"k={k}"] = {
                "n_subsamples": len(subsample_results),
                "mean_range_pooled_rr": round(mean_range, 4),
                "median_range_pooled_rr": round(median_range, 4),
                "p95_range_pooled_rr": round(p95_range, 4),
                "n_subsamples_any_run_crosses_null": n_any_cross,
                "n_subsamples_all_runs_cross_null": n_all_cross,
                "n_subsamples_UNSTABLE_null_crossing": n_unstable_null,
                "pct_unstable_null_crossing": round(n_unstable_null / len(subsample_results), 4) if subsample_results else 0.0,
            }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2))
    # Print headline
    print(f"\n{'Model':<20} {'k':>4} {'Mean range':>12} {'P95 range':>12} {'% UNSTABLE null-cross':>24}")
    for m in MODELS:
        for k in K_VALUES:
            r = report["models"].get(m, {}).get(f"k={k}")
            if r:
                print(f"{m:<20} {k:>4} {r['mean_range_pooled_rr']:>12.4f} {r['p95_range_pooled_rr']:>12.4f} {r['pct_unstable_null_crossing']:>24.2%}")
    print(f"\nWrote {OUT.relative_to(ROOT)}")
    print("\nKey interpretation:")
    print("  % UNSTABLE null-cross = fraction of subsamples where pooled 95% CI crosses null")
    print("  in SOME runs but not others - i.e., the meta-analytic conclusion DEPENDS on which")
    print("  LLM run was used. This is the headline finding.")


if __name__ == "__main__":
    main()
