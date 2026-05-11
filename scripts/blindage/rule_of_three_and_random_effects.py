"""Rule-of-three upper bounds for zero-variation cells + full random-effects
meta-analysis per model x run (P1.1 + P1.6).

Replaces bootstrap [1.000, 1.000] CIs with more informative rule-of-three
95% upper bounds on the non-match rate.

Computes both DerSimonian-Laird (DL) AND Hartung-Knapp-Sidik-Jonkman (HKSJ)
random-effects pooled estimates for each model x run. Per RSM P2.a audit:
Cochrane Handbook 6.5+ recommends HKSJ over DL for k<10 because DL is known
to be liberal (anti-conservative) in small-k meta-analyses. We retain DL for
backward comparability and report HKSJ as the primary sensitivity analysis.

HKSJ formula (Hartung & Knapp 2001):
    Use the DL tau^2 estimate (or any tau^2 estimator).
    weights w_i* = 1 / (vars_i + tau^2)
    pooled theta_RE = sum(w_i* y_i) / sum(w_i*)
    Hartung-Knapp adjusted variance:
        q* = (1 / (k - 1)) * sum( w_i* * (y_i - theta_RE)^2 )
        SE_HKSJ = sqrt( q* / sum(w_i*) )
    CI: theta_RE +- t_{0.975, k-1} * SE_HKSJ
    (vs. DL standard: theta_RE +- 1.96 * sqrt(1 / sum(w_i*)))

Note: HKSJ collapses to DL/Wald when q* coincides with 1/sum(w_i*) (i.e.,
homogeneity), but generally yields wider CIs because:
  (a) it uses t(k-1) instead of z, and
  (b) q* >= 1/sum(w_i*) in expectation under heterogeneity.

Output:
    analysis/blindage/rule_of_three.json
    analysis/blindage/random_effects_per_run.json
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
LONG = ROOT / "analysis" / "blindage" / "extraction_long.json"
REPRO = ROOT / "analysis" / "reproducibility_results.json"
RULE3_OUT = ROOT / "analysis" / "blindage" / "rule_of_three.json"
RE_OUT = ROOT / "analysis" / "blindage" / "random_effects_per_run.json"

MODELS = ["llama3-8b", "mistral-7b", "gemma2-9b",
          "claude-sonnet-4-5", "gemini-2.5-pro", "gpt-4.1"]

SEED = 42  # deterministic ordering only; the inverse-variance pool has no RNG


def rule_of_three(n: int) -> float:
    return 3.0 / n if n > 0 else float("inf")


def build_rule_of_three_report() -> dict:
    repro = json.loads(REPRO.read_text())
    report = {
        "method": "Rule of three: 95% upper bound on non-match rate when 0 non-matches observed in n items",
        "formula": "UCL_{95%}(non-match rate) = 3/n  (Hanley & Lippman-Hand, JAMA 1983)",
        "rationale": "Bootstrap CI [1.000, 1.000] is uninformative when EMR=1.000 with 0 variation.",
        "items": {},
    }
    for model in MODELS:
        if model not in repro:
            continue
        item = {}
        for stage in ("screening", "extraction"):
            s = repro[model].get(stage)
            if not s:
                continue
            emr = s.get("emr", 1.0)
            n = s.get("n_abstracts") or s.get("n_articles")
            if emr >= 0.9999 and n:
                upper = rule_of_three(n)
                item[stage] = {
                    "emr": emr, "n": n,
                    "rule_of_three_upper_bound": round(upper, 4),
                    "recommended_reporting": (
                        f"EMR = 1.000  (non-match rate $\\leq${upper:.3f}, "
                        f"95% upper bound, n={n})"
                    ),
                }
            else:
                item[stage] = {
                    "emr": emr, "n": n,
                    "note": "Not applicable: EMR < 1.0, standard bootstrap CI is informative",
                }
        report["items"][model] = item
    return report


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
    if se <= 0:
        return None
    return log_rr, se * se


def pool_de_fe_hksj(estimates: list[tuple[float, float]]) -> dict | None:
    """Compute DL random-effects AND HKSJ-corrected random-effects in one pass.

    Returns a dict with both DL and HKSJ CIs on the same tau^2 (method-of-moments).
    """
    k = len(estimates)
    if k < 2:
        return None
    thetas = [e[0] for e in estimates]
    vars_fe = [e[1] for e in estimates]
    w_fe = [1.0 / v for v in vars_fe]
    sum_w = sum(w_fe)
    theta_fe = sum(wi * ti for wi, ti in zip(w_fe, thetas)) / sum_w
    Q = sum(wi * (ti - theta_fe) ** 2 for wi, ti in zip(w_fe, thetas))
    df = k - 1
    sum_w2 = sum(wi ** 2 for wi in w_fe)
    c = sum_w - sum_w2 / sum_w
    tau2 = max(0.0, (Q - df) / c) if c > 0 else 0.0
    i2 = max(0.0, (Q - df) / Q) * 100 if Q > 0 else 0.0

    # DL random-effects
    w_re = [1.0 / (v + tau2) for v in vars_fe]
    sum_ws = sum(w_re)
    theta_re = sum(wi * ti for wi, ti in zip(w_re, thetas)) / sum_ws
    se_re_dl = math.sqrt(1.0 / sum_ws)
    z = 1.959964
    ci_re_dl = (math.exp(theta_re - z * se_re_dl), math.exp(theta_re + z * se_re_dl))

    # HKSJ correction (Hartung & Knapp 2001):
    #   q* = (1/(k-1)) * sum(w_i* * (y_i - theta_RE)^2)
    #   SE_HKSJ = sqrt(q* / sum(w_i*))
    #   CI uses t(k-1)
    q_star = sum(wi * (ti - theta_re) ** 2 for wi, ti in zip(w_re, thetas)) / (k - 1)
    se_re_hksj = math.sqrt(q_star / sum_ws)
    t_crit = float(stats.t.ppf(0.975, df=k - 1))
    ci_re_hksj = (math.exp(theta_re - t_crit * se_re_hksj),
                  math.exp(theta_re + t_crit * se_re_hksj))

    # FE
    se_fe = math.sqrt(1.0 / sum_w)
    ci_fe = (math.exp(theta_fe - z * se_fe), math.exp(theta_fe + z * se_fe))

    return {
        "k": k, "df": df, "Q": Q, "tau2": tau2, "I2_pct": i2,
        # FE
        "theta_fe_log": theta_fe, "rr_fe": math.exp(theta_fe), "ci_fe": ci_fe,
        # RE-DL
        "theta_re_log": theta_re, "rr_re": math.exp(theta_re),
        "se_re_dl": se_re_dl, "ci_re_dl": ci_re_dl,
        "ci_re_dl_crosses_null": ci_re_dl[0] < 1 < ci_re_dl[1],
        # RE-HKSJ
        "se_re_hksj": se_re_hksj, "t_crit_hksj": t_crit,
        "ci_re_hksj": ci_re_hksj,
        "ci_re_hksj_crosses_null": ci_re_hksj[0] < 1 < ci_re_hksj[1],
        # convenience flags
        "ci_fe_crosses_null": ci_fe[0] < 1 < ci_fe[1],
    }


def build_random_effects_per_run() -> dict:
    rows = json.loads(LONG.read_text())
    per_model_run = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r["estimate_idx"] != 0:
            continue
        if r["effect_measure"] not in ("RR", "OR", "HR", "IRR"):
            continue
        le = valid_log_rr(r)
        if le is None:
            continue
        per_model_run[r["model"]][r["run_id"]].append(le)

    report = {
        "method": (
            "DerSimonian-Laird (DL) and Hartung-Knapp-Sidik-Jonkman (HKSJ) "
            "random-effects pooling on log(RR). Same tau^2 estimator (method-of-moments); "
            "HKSJ uses adjusted variance q*/sum(w*) and t(k-1) critical value. "
            "Reported per RSM P2.a audit (Cochrane Handbook 6.5+ recommends HKSJ for k<10)."
        ),
        "tau2_estimator": "method-of-moments (DL)",
        "z_critical_DL": 1.959964,
        "models": {},
    }
    for model in MODELS:
        runs = per_model_run.get(model)
        if not runs:
            continue
        report["models"][model] = {"runs": {}, "summary": {}}
        fe_rrs, re_rrs, i2s, tau2s = [], [], [], []
        dl_ci_low, dl_ci_hi, hksj_ci_low, hksj_ci_hi = [], [], [], []
        dl_widths, hksj_widths = [], []
        n_dl_cross, n_hksj_cross = 0, 0
        for run_id, ests in sorted(runs.items()):
            p = pool_de_fe_hksj(ests)
            if not p:
                continue
            report["models"][model]["runs"][str(run_id)] = {
                "k_studies": p["k"],
                "pooled_rr_FE": round(p["rr_fe"], 4),
                "ci_FE": [round(p["ci_fe"][0], 4), round(p["ci_fe"][1], 4)],
                "pooled_rr_RE": round(p["rr_re"], 4),
                "ci_RE_DL": [round(p["ci_re_dl"][0], 4), round(p["ci_re_dl"][1], 4)],
                "ci_RE_HKSJ": [round(p["ci_re_hksj"][0], 4), round(p["ci_re_hksj"][1], 4)],
                "se_re_dl": round(p["se_re_dl"], 6),
                "se_re_hksj": round(p["se_re_hksj"], 6),
                "t_crit_hksj": round(p["t_crit_hksj"], 4),
                "tau2": round(p["tau2"], 6),
                "I2_pct": round(p["I2_pct"], 2),
                "ci_DL_crosses_null": p["ci_re_dl_crosses_null"],
                "ci_HKSJ_crosses_null": p["ci_re_hksj_crosses_null"],
            }
            fe_rrs.append(p["rr_fe"])
            re_rrs.append(p["rr_re"])
            i2s.append(p["I2_pct"])
            tau2s.append(p["tau2"])
            dl_ci_low.append(p["ci_re_dl"][0]); dl_ci_hi.append(p["ci_re_dl"][1])
            hksj_ci_low.append(p["ci_re_hksj"][0]); hksj_ci_hi.append(p["ci_re_hksj"][1])
            dl_widths.append(p["ci_re_dl"][1] - p["ci_re_dl"][0])
            hksj_widths.append(p["ci_re_hksj"][1] - p["ci_re_hksj"][0])
            if p["ci_re_dl_crosses_null"]:
                n_dl_cross += 1
            if p["ci_re_hksj_crosses_null"]:
                n_hksj_cross += 1
        n = len(fe_rrs)
        if n:
            report["models"][model]["summary"] = {
                "n_runs": n,
                "mean_FE_pooled_rr": round(sum(fe_rrs) / n, 4),
                "range_FE_pooled_rr": round(max(fe_rrs) - min(fe_rrs), 4),
                "mean_RE_pooled_rr": round(sum(re_rrs) / n, 4),
                "range_RE_pooled_rr": round(max(re_rrs) - min(re_rrs), 4),
                "mean_I2_pct": round(sum(i2s) / n, 2),
                "mean_tau2": round(sum(tau2s) / n, 6),
                "mean_DL_ci_lower": round(sum(dl_ci_low) / n, 4),
                "mean_DL_ci_upper": round(sum(dl_ci_hi) / n, 4),
                "mean_HKSJ_ci_lower": round(sum(hksj_ci_low) / n, 4),
                "mean_HKSJ_ci_upper": round(sum(hksj_ci_hi) / n, 4),
                "mean_DL_ci_width": round(sum(dl_widths) / n, 4),
                "mean_HKSJ_ci_width": round(sum(hksj_widths) / n, 4),
                "HKSJ_DL_width_ratio": (round(sum(hksj_widths) / sum(dl_widths), 3)
                                        if sum(dl_widths) > 0 else None),
                "n_runs_DL_crosses_null": n_dl_cross,
                "n_runs_HKSJ_crosses_null": n_hksj_cross,
                "pct_runs_DL_crosses_null": round(n_dl_cross / n, 4),
                "pct_runs_HKSJ_crosses_null": round(n_hksj_cross / n, 4),
            }
    return report


def main() -> None:
    rule3 = build_rule_of_three_report()
    RULE3_OUT.parent.mkdir(parents=True, exist_ok=True)
    RULE3_OUT.write_text(json.dumps(rule3, indent=2))

    re_report = build_random_effects_per_run()
    payload = json.dumps(re_report, indent=2)
    re_report["sha256_self"] = hashlib.sha256(payload.encode()).hexdigest()
    re_report["seed"] = SEED
    RE_OUT.write_text(json.dumps(re_report, indent=2))

    print("=== RULE OF THREE ===")
    for m, item in rule3["items"].items():
        for stage, s in item.items():
            if "rule_of_three_upper_bound" in s:
                print(f"  {m:<20} {stage:<10} EMR=1.000 -> UCL={s['rule_of_three_upper_bound']:.4f} (n={s['n']})")

    print("\n=== RANDOM-EFFECTS PER RUN (DL vs HKSJ) ===")
    print(f"{'Model':<20} {'mean RE RR':>10} {'mean DL CI':>22} {'mean HKSJ CI':>22} {'HKSJ/DL width':>14} {'% DL cross':>12} {'% HKSJ cross':>14}")
    for m, d in re_report["models"].items():
        s = d.get("summary")
        if not s:
            continue
        dl_ci = f"[{s['mean_DL_ci_lower']:.4f}, {s['mean_DL_ci_upper']:.4f}]"
        hksj_ci = f"[{s['mean_HKSJ_ci_lower']:.4f}, {s['mean_HKSJ_ci_upper']:.4f}]"
        ratio = s.get("HKSJ_DL_width_ratio", float("nan"))
        print(f"{m:<20} {s['mean_RE_pooled_rr']:>10.4f} {dl_ci:>22} {hksj_ci:>22} {ratio:>14.3f} {s['pct_runs_DL_crosses_null']:>12.2%} {s['pct_runs_HKSJ_crosses_null']:>14.2%}")

    print(f"\nWrote:")
    print(f"  {RULE3_OUT.relative_to(ROOT)}")
    print(f"  {RE_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
