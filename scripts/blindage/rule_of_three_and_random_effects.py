"""Rule-of-three upper bounds for zero-variation cells + full random-effects
meta-analysis per model × run (P1.1 + P1.6).

Replaces bootstrap [1.000, 1.000] CIs with more informative rule-of-three
95% upper bounds on the non-match rate.

Also computes DerSimonian-Laird random-effects pooled estimate for each
model × run using ALL valid first-estimates (not subsamples).

Output:
    analysis/blindage/rule_of_three.json
    analysis/blindage/random_effects_per_run.json
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LONG = ROOT / "analysis" / "blindage" / "extraction_long.json"
REPRO = ROOT / "analysis" / "reproducibility_results.json"
RULE3_OUT = ROOT / "analysis" / "blindage" / "rule_of_three.json"
RE_OUT = ROOT / "analysis" / "blindage" / "random_effects_per_run.json"

MODELS = ["llama3-8b", "mistral-7b", "gemma2-9b",
          "claude-sonnet-4-5", "gemini-2.5-pro", "gpt-4.1"]


def rule_of_three(n: int) -> float:
    """Upper 95% bound on proportion when 0 events observed in n trials."""
    return 3.0 / n if n > 0 else float("inf")


def build_rule_of_three_report() -> dict:
    repro = json.loads(REPRO.read_text())
    report = {
        "method": "Rule of three: 95% upper bound on non-match rate when 0 non-matches observed in n items",
        "formula": "UCL_{95%}(non-match rate) = 3/n  (Hanley & Lippman-Hand, JAMA 1983)",
        "rationale": "Bootstrap CI [1.000, 1.000] is uninformative when EMR=1.000 with 0 variation. Rule of three provides a principled upper bound on the unseen non-match rate.",
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
                    "emr": emr,
                    "n": n,
                    "rule_of_three_upper_bound": round(upper, 4),
                    "recommended_reporting": f"EMR = 1.000  (non-match rate $\\leq${upper:.3f}, 95% upper bound, n={n})",
                }
            else:
                item[stage] = {
                    "emr": emr,
                    "n": n,
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


def pool_de_fe(estimates: list[tuple[float, float]], method: str = "DL") -> dict:
    """Fixed-effect and random-effects (DerSimonian-Laird) pooling."""
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
    i2 = max(0.0, (Q - df) / Q) * 100 if Q > 0 else 0.0
    # FE CI
    se_fe = math.sqrt(1.0 / sum_w)
    # RE
    w_re = [1.0 / (v + tau2) for v in vars_fe]
    sum_ws = sum(w_re)
    theta_re = sum(wi * ti for wi, ti in zip(w_re, thetas)) / sum_ws
    se_re = math.sqrt(1.0 / sum_ws)
    z = 1.959964
    return {
        "k": k,
        "theta_fe_log": theta_fe,
        "rr_fe": math.exp(theta_fe),
        "ci_fe": (math.exp(theta_fe - z * se_fe), math.exp(theta_fe + z * se_fe)),
        "theta_re_log": theta_re,
        "rr_re": math.exp(theta_re),
        "ci_re": (math.exp(theta_re - z * se_re), math.exp(theta_re + z * se_re)),
        "tau2": tau2,
        "Q": Q,
        "df": df,
        "I2_pct": i2,
        "ci_fe_crosses_null": math.exp(theta_fe - z * se_fe) < 1 < math.exp(theta_fe + z * se_fe),
        "ci_re_crosses_null": math.exp(theta_re - z * se_re) < 1 < math.exp(theta_re + z * se_re),
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
        "method": "DerSimonian-Laird random-effects + fixed-effect inverse-variance",
        "note": "Each row = pooled estimate using first valid effect per abstract for one model × run.",
        "models": {},
    }
    for model in MODELS:
        runs = per_model_run.get(model)
        if not runs:
            continue
        report["models"][model] = {"runs": {}, "summary": {}}
        fe_rrs, re_rrs, i2s, tau2s = [], [], [], []
        re_ci_low, re_ci_hi = [], []
        n_re_crosses = 0
        for run_id, ests in sorted(runs.items()):
            p = pool_de_fe(ests)
            if not p:
                continue
            report["models"][model]["runs"][str(run_id)] = {
                "k_studies": p["k"],
                "pooled_rr_FE": round(p["rr_fe"], 4),
                "ci_FE": [round(p["ci_fe"][0], 4), round(p["ci_fe"][1], 4)],
                "pooled_rr_RE": round(p["rr_re"], 4),
                "ci_RE": [round(p["ci_re"][0], 4), round(p["ci_re"][1], 4)],
                "tau2": round(p["tau2"], 6),
                "I2_pct": round(p["I2_pct"], 2),
                "ci_FE_crosses_null": p["ci_fe_crosses_null"],
                "ci_RE_crosses_null": p["ci_re_crosses_null"],
            }
            fe_rrs.append(p["rr_fe"])
            re_rrs.append(p["rr_re"])
            i2s.append(p["I2_pct"])
            tau2s.append(p["tau2"])
            re_ci_low.append(p["ci_re"][0])
            re_ci_hi.append(p["ci_re"][1])
            if p["ci_re_crosses_null"]:
                n_re_crosses += 1
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
                "mean_RE_ci_lower": round(sum(re_ci_low) / n, 4),
                "mean_RE_ci_upper": round(sum(re_ci_hi) / n, 4),
                "RE_ci_width_mean": round(sum(hi - lo for lo, hi in zip(re_ci_low, re_ci_hi)) / n, 4),
                "n_runs_RE_crosses_null": n_re_crosses,
                "pct_runs_RE_crosses_null": round(n_re_crosses / n, 4),
            }
    return report


def main() -> None:
    rule3 = build_rule_of_three_report()
    RULE3_OUT.parent.mkdir(parents=True, exist_ok=True)
    RULE3_OUT.write_text(json.dumps(rule3, indent=2))

    re_report = build_random_effects_per_run()
    RE_OUT.write_text(json.dumps(re_report, indent=2))

    # Print headlines
    print("=== RULE OF THREE ===")
    for m, item in rule3["items"].items():
        for stage, s in item.items():
            if "rule_of_three_upper_bound" in s:
                print(f"  {m:<20} {stage:<10} EMR=1.000 -> UCL={s['rule_of_three_upper_bound']:.4f} (n={s['n']})")

    print("\n=== RANDOM-EFFECTS PER RUN (DerSimonian-Laird) ===")
    print(f"{'Model':<20} {'mean FE RR':>12} {'range FE':>10} {'mean RE RR':>12} {'range RE':>10} {'% runs RE cross null':>22}")
    for m, d in re_report["models"].items():
        s = d["summary"]
        if not s:
            continue
        print(f"{m:<20} {s['mean_FE_pooled_rr']:>12.4f} {s['range_FE_pooled_rr']:>10.4f} {s['mean_RE_pooled_rr']:>12.4f} {s['range_RE_pooled_rr']:>10.4f} {s['pct_runs_RE_crosses_null']:>22.2%}")

    print(f"\nWrote:")
    print(f"  {RULE3_OUT.relative_to(ROOT)}")
    print(f"  {RE_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
