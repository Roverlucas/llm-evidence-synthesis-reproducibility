"""Small-literature simulation (P0.2, R2/R4/R5 blocker; HKSJ extension per P2.a).

For each model × run, subsample k in {10, 15, 20, 30} articles and compute
pooled random-effects estimate using BOTH:
  - DerSimonian-Laird (DL) with Wald-z CI (original)
  - Hartung-Knapp-Sidik-Jonkman (HKSJ) with t(k-1) CI (P2.a sensitivity)

Check whether:
    (a) 95% CI crosses null (RR=1) in ANY of the 10 runs for a given subsample
    (b) the cross-run reversal pattern ("unstable null-crossing") is preserved
        under the more conservative HKSJ correction

This addresses the "So what?" question by demonstrating concrete scenarios
where LLM non-determinism changes the meta-analytic conclusion under both
the liberal (DL) and the conservative (HKSJ) variance estimators recommended
by Cochrane Handbook 6.5+ for k<10.

Output: analysis/blindage/small_literature_sim.json
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from collections import defaultdict
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "analysis" / "blindage" / "extraction_long.json"
OUT = ROOT / "analysis" / "blindage" / "small_literature_sim.json"

MODELS = ["llama3-8b", "mistral-7b", "gemma2-9b",
          "claude-sonnet-4-5", "gemini-2.5-pro", "gpt-4.1"]

SEED = 42
K_VALUES = [10, 15, 20, 30]
N_SUBSAMPLES = 200
ALPHA = 0.05
Z_CRIT = 1.959964


def valid_log_rr(r: dict) -> tuple[float, float] | None:
    rr = r.get("effect_estimate")
    lo = r.get("ci_lower")
    hi = r.get("ci_upper")
    if rr is None or lo is None or hi is None:
        return None
    try:
        rr, lo, hi = float(rr), float(lo), float(hi)
    except (TypeError, ValueError):
        return None
    if rr <= 0 or lo <= 0 or hi <= 0:
        return None
    if not (lo < rr < hi):
        return None
    if rr < 0.3 or rr > 5.0:
        return None
    log_rr = math.log(rr)
    se = (math.log(hi) - math.log(lo)) / (2 * 1.96)
    var = se * se
    if var <= 0:
        return None
    return log_rr, var


def pool_random_effects(estimates: list[tuple[float, float]]) -> dict | None:
    """DL random-effects + HKSJ correction. Returns both CIs."""
    k = len(estimates)
    if k < 2:
        return None
    thetas = [e[0] for e in estimates]
    vars_fe = [e[1] for e in estimates]
    w = [1.0 / v for v in vars_fe]
    sum_w = sum(w)
    theta_fe = sum(wi * ti for wi, ti in zip(w, thetas)) / sum_w
    Q = sum(wi * (ti - theta_fe) ** 2 for wi, ti in zip(w, thetas))
    df = k - 1
    sum_w2 = sum(wi ** 2 for wi in w)
    c = sum_w - sum_w2 / sum_w
    tau2 = max(0.0, (Q - df) / c) if c > 0 else 0.0
    w_star = [1.0 / (v + tau2) for v in vars_fe]
    sum_ws = sum(w_star)
    theta_re = sum(wi * ti for wi, ti in zip(w_star, thetas)) / sum_ws

    # DL CI
    se_dl = math.sqrt(1.0 / sum_ws)
    dl_lo = theta_re - Z_CRIT * se_dl
    dl_hi = theta_re + Z_CRIT * se_dl

    # HKSJ CI
    q_star = sum(wi * (ti - theta_re) ** 2 for wi, ti in zip(w_star, thetas)) / df
    se_hksj = math.sqrt(q_star / sum_ws)
    t_crit = float(stats.t.ppf(0.975, df=df))
    hksj_lo = theta_re - t_crit * se_hksj
    hksj_hi = theta_re + t_crit * se_hksj

    return {
        "pooled_log_rr": theta_re,
        "pooled_rr": math.exp(theta_re),
        "se_log_dl": se_dl,
        "se_log_hksj": se_hksj,
        "ci_lower_rr_dl": math.exp(dl_lo),
        "ci_upper_rr_dl": math.exp(dl_hi),
        "ci_lower_rr_hksj": math.exp(hksj_lo),
        "ci_upper_rr_hksj": math.exp(hksj_hi),
        "tau2": tau2,
        "Q": Q,
        "df": df,
        "k": k,
        "crosses_null_dl": dl_lo < 0 < dl_hi,
        "crosses_null_hksj": hksj_lo < 0 < hksj_hi,
    }


def first_estimate_per_item(rows: list[dict]) -> list[tuple[str, tuple[float, float]]]:
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
    rows_per_model = defaultdict(lambda: defaultdict(list))
    for r in rows:
        rows_per_model[r["model"]][r["run_id"]].append(r)

    rng = random.Random(SEED)

    report = {
        "metadata": {
            "k_values": K_VALUES,
            "n_subsamples_per_k": N_SUBSAMPLES,
            "seed": SEED,
            "pooling_method": "DerSimonian-Laird random-effects on log(RR), "
                              "with Hartung-Knapp-Sidik-Jonkman (HKSJ) variance correction "
                              "as P2.a sensitivity (Cochrane Handbook 6.5+).",
            "null_value": 1.0,
            "z_critical_dl": Z_CRIT,
        },
        "models": {},
    }

    for model in MODELS:
        report["models"][model] = {}
        runs_dict = rows_per_model[model]
        if not runs_dict:
            continue
        run_ids = sorted(runs_dict)
        run_estimates = {rid: dict(first_estimate_per_item(runs_dict[rid])) for rid in run_ids}
        all_ids = sorted({cid for d in run_estimates.values() for cid in d})

        if len(all_ids) < max(K_VALUES):
            print(f"SKIP {model}: only {len(all_ids)} items with valid first-estimate")
            continue

        for k in K_VALUES:
            subsample_results = []
            for sample_idx in range(N_SUBSAMPLES):
                sampled_ids = rng.sample(all_ids, k)
                per_run_pooled = {}
                for run_id in run_ids:
                    est_for_run = [run_estimates[run_id][cid]
                                   for cid in sampled_ids
                                   if cid in run_estimates[run_id]]
                    if len(est_for_run) < 2:
                        per_run_pooled[run_id] = None
                        continue
                    per_run_pooled[run_id] = pool_random_effects(est_for_run)
                valid_rrs = [v["pooled_rr"] for v in per_run_pooled.values() if v]
                valid_dl_cross = [v["crosses_null_dl"] for v in per_run_pooled.values() if v]
                valid_hksj_cross = [v["crosses_null_hksj"] for v in per_run_pooled.values() if v]
                if valid_rrs:
                    subsample_results.append({
                        "sampled_ids": sampled_ids,
                        "pooled_rrs_per_run": {str(rid): (per_run_pooled[rid]["pooled_rr"] if per_run_pooled[rid] else None)
                                               for rid in run_ids},
                        "range_pooled_rr": max(valid_rrs) - min(valid_rrs),
                        "min_pooled_rr": min(valid_rrs),
                        "max_pooled_rr": max(valid_rrs),
                        "n_runs_cross_null_dl": sum(valid_dl_cross),
                        "n_runs_cross_null_hksj": sum(valid_hksj_cross),
                        "any_run_cross_null_dl": any(valid_dl_cross),
                        "any_run_cross_null_hksj": any(valid_hksj_cross),
                        "all_runs_cross_null_dl": all(valid_dl_cross) if valid_dl_cross else False,
                        "all_runs_cross_null_hksj": all(valid_hksj_cross) if valid_hksj_cross else False,
                    })
            ranges = [s["range_pooled_rr"] for s in subsample_results]
            n_any_cross_dl = sum(1 for s in subsample_results if s["any_run_cross_null_dl"])
            n_all_cross_dl = sum(1 for s in subsample_results if s["all_runs_cross_null_dl"])
            n_unstable_null_dl = sum(1 for s in subsample_results
                                     if 0 < s["n_runs_cross_null_dl"] < len(run_ids))
            n_any_cross_hksj = sum(1 for s in subsample_results if s["any_run_cross_null_hksj"])
            n_all_cross_hksj = sum(1 for s in subsample_results if s["all_runs_cross_null_hksj"])
            n_unstable_null_hksj = sum(1 for s in subsample_results
                                       if 0 < s["n_runs_cross_null_hksj"] < len(run_ids))
            ranges_sorted = sorted(ranges)
            mean_range = sum(ranges) / len(ranges) if ranges else 0.0
            median_range = ranges_sorted[len(ranges_sorted) // 2] if ranges_sorted else 0.0
            p95_range = (ranges_sorted[min(len(ranges_sorted) - 1, int(0.95 * len(ranges_sorted)))]
                         if ranges_sorted else 0.0)
            report["models"][model][f"k={k}"] = {
                "n_subsamples": len(subsample_results),
                "mean_range_pooled_rr": round(mean_range, 4),
                "median_range_pooled_rr": round(median_range, 4),
                "p95_range_pooled_rr": round(p95_range, 4),
                # DL (original)
                "n_subsamples_any_run_crosses_null_DL": n_any_cross_dl,
                "n_subsamples_all_runs_cross_null_DL": n_all_cross_dl,
                "n_subsamples_UNSTABLE_null_crossing_DL": n_unstable_null_dl,
                "pct_unstable_null_crossing_DL": round(n_unstable_null_dl / len(subsample_results), 4)
                                                if subsample_results else 0.0,
                # HKSJ
                "n_subsamples_any_run_crosses_null_HKSJ": n_any_cross_hksj,
                "n_subsamples_all_runs_cross_null_HKSJ": n_all_cross_hksj,
                "n_subsamples_UNSTABLE_null_crossing_HKSJ": n_unstable_null_hksj,
                "pct_unstable_null_crossing_HKSJ": round(n_unstable_null_hksj / len(subsample_results), 4)
                                                  if subsample_results else 0.0,
            }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, indent=2, sort_keys=False)
    report["sha256_self"] = hashlib.sha256(payload.encode()).hexdigest()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=False))

    print(f"\n{'Model':<20} {'k':>4} | {'mean range':>10} {'p95 range':>10} | "
          f"{'% unstable DL':>14} {'% unstable HKSJ':>16}")
    for m in MODELS:
        for k in K_VALUES:
            r = report["models"].get(m, {}).get(f"k={k}")
            if r:
                print(f"{m:<20} {k:>4} | {r['mean_range_pooled_rr']:>10.4f} {r['p95_range_pooled_rr']:>10.4f} | "
                      f"{r['pct_unstable_null_crossing_DL']:>14.2%} {r['pct_unstable_null_crossing_HKSJ']:>16.2%}")
    print(f"\nWrote {OUT.relative_to(ROOT)}")
    print("\nKey interpretation:")
    print("  % UNSTABLE null-cross = fraction of subsamples where pooled 95% CI crosses null")
    print("  in SOME runs but not others - i.e., meta-analytic conclusion DEPENDS on LLM run.")
    print("  HKSJ widens CIs (more conservative) so unstable% under HKSJ >= unstable% under DL")
    print("  in expectation when the variance correction matters.")


if __name__ == "__main__":
    main()
