#!/usr/bin/env python3
"""Compute comprehensive timing and cost data for all 6 models.

Reads run_card.json and call_records.json from each model/stage/run,
aggregates timing, token counts, and estimates costs.

Output: analysis/timing_and_costs.json
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("/Users/lucasrover/llm-evidence-synthesis-reproducibility")
RAW_DIR = BASE_DIR / "data" / "raw_outputs"
OUT_DIR = BASE_DIR / "analysis"

MODELS = [
    "llama3-8b",
    "mistral-7b",
    "gemma2-9b",
    "claude-sonnet-4-5",
    "gemini-2.5-pro",
    "gpt-4.1",
]

STAGES = ["screening", "extraction"]

COST_TABLE = {
    "gpt-4.1": {"input_per_1m": 2.00, "output_per_1m": 8.00, "provider": "openai"},
    "claude-sonnet-4-5": {"input_per_1m": 3.00, "output_per_1m": 15.00, "provider": "anthropic"},
    "gemini-2.5-pro": {"input_per_1m": 0.00, "output_per_1m": 0.00, "provider": "google", "note": "Free tier used"},
    "llama3-8b": {"input_per_1m": 0.00, "output_per_1m": 0.00, "provider": "ollama", "note": "Local inference"},
    "mistral-7b": {"input_per_1m": 0.00, "output_per_1m": 0.00, "provider": "ollama", "note": "Local inference"},
    "gemma2-9b": {"input_per_1m": 0.00, "output_per_1m": 0.00, "provider": "ollama", "note": "Local inference"},
}

LOCAL_COST = {
    "power_watts": 15,
    "cost_per_kwh": 0.10,
}


def parse_iso(ts):
    ts = ts.strip()
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts)


def compute_electricity_cost(total_ms):
    hours = total_ms / 1000.0 / 3600.0
    kwh = LOCAL_COST["power_watts"] / 1000.0 * hours
    return kwh * LOCAL_COST["cost_per_kwh"]


def process_run(model, stage, run_id):
    run_dir = RAW_DIR / model / stage / f"run_{run_id:03d}"
    run_card_path = run_dir / "run_card.json"
    call_records_path = run_dir / "call_records.json"

    result = {
        "run_id": run_id,
        "model": model,
        "stage": stage,
        "exists": False,
    }

    if not run_card_path.exists():
        return result

    with open(run_card_path) as f:
        rc = json.load(f)

    exe = rc.get("execution", {})
    result.update({
        "exists": True,
        "start_time": exe.get("start_time"),
        "end_time": exe.get("end_time"),
        "total_calls": exe.get("total_calls", 0),
        "successful_calls": exe.get("successful_calls", 0),
        "failed_calls": exe.get("failed_calls", 0),
        "total_duration_ms": exe.get("total_duration_ms", 0.0),
        "mean_duration_ms": exe.get("mean_duration_ms", 0.0),
    })

    if exe.get("start_time") and exe.get("end_time"):
        try:
            start = parse_iso(exe["start_time"])
            end = parse_iso(exe["end_time"])
            result["wall_clock_seconds"] = (end - start).total_seconds()
        except Exception:
            result["wall_clock_seconds"] = None
    else:
        result["wall_clock_seconds"] = None

    total_input_tokens = 0
    total_output_tokens = 0
    call_count = 0
    durations = []

    if call_records_path.exists():
        with open(call_records_path) as f:
            records = json.load(f)

        for rec in records:
            call_count += 1
            total_input_tokens += (rec.get("input_tokens") or 0)
            total_output_tokens += (rec.get("output_tokens") or 0)
            if rec.get("inference_duration_ms") is not None:
                durations.append(rec["inference_duration_ms"])

    result["token_counts"] = {
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
        "records_processed": call_count,
    }

    if durations:
        sorted_d = sorted(durations)
        n = len(sorted_d)
        p25 = sorted_d[n // 4]
        p75 = sorted_d[(3 * n) // 4]
        result["duration_stats_from_records"] = {
            "count": n,
            "sum_ms": round(sum(durations), 2),
            "mean_ms": round(sum(durations) / n, 2),
            "min_ms": round(min(durations), 2),
            "max_ms": round(max(durations), 2),
            "median_ms": round(sorted_d[n // 2], 2),
            "p25_ms": round(p25, 2),
            "p75_ms": round(p75, 2),
        }

    return result


def aggregate_model_stage(runs):
    valid = [r for r in runs if r["exists"]]
    if not valid:
        return {"n_runs": 0, "note": "no data found"}

    total_duration_ms = sum(r["total_duration_ms"] for r in valid)
    total_calls = sum(r["total_calls"] for r in valid)
    successful_calls = sum(r["successful_calls"] for r in valid)
    failed_calls = sum(r["failed_calls"] for r in valid)
    total_input_tokens = sum(r["token_counts"]["total_input_tokens"] for r in valid)
    total_output_tokens = sum(r["token_counts"]["total_output_tokens"] for r in valid)
    wall_clocks = [r["wall_clock_seconds"] for r in valid if r.get("wall_clock_seconds") is not None]

    agg = {
        "n_runs": len(valid),
        "total_calls": total_calls,
        "successful_calls": successful_calls,
        "failed_calls": failed_calls,
        "timing": {
            "total_inference_duration_ms": round(total_duration_ms, 2),
            "total_inference_duration_min": round(total_duration_ms / 60000.0, 2),
            "total_inference_duration_hr": round(total_duration_ms / 3600000.0, 4),
            "mean_duration_per_call_ms": round(total_duration_ms / successful_calls, 2) if successful_calls > 0 else None,
            "mean_duration_per_run_ms": round(total_duration_ms / len(valid), 2),
            "mean_duration_per_run_min": round(total_duration_ms / len(valid) / 60000.0, 2),
        },
        "tokens": {
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "mean_input_per_call": round(total_input_tokens / successful_calls, 1) if successful_calls > 0 else None,
            "mean_output_per_call": round(total_output_tokens / successful_calls, 1) if successful_calls > 0 else None,
        },
    }

    if wall_clocks:
        total_wc = sum(wall_clocks)
        agg["wall_clock"] = {
            "total_seconds": round(total_wc, 2),
            "total_minutes": round(total_wc / 60.0, 2),
            "total_hours": round(total_wc / 3600.0, 4),
            "mean_per_run_seconds": round(total_wc / len(wall_clocks), 2),
            "mean_per_run_minutes": round(total_wc / len(wall_clocks) / 60.0, 2),
        }

    all_dur_stats = [r["duration_stats_from_records"] for r in valid if "duration_stats_from_records" in r]
    if all_dur_stats:
        agg["timing"]["aggregate_call_stats"] = {
            "total_calls_with_duration": sum(s["count"] for s in all_dur_stats),
            "global_mean_ms": round(
                sum(s["sum_ms"] for s in all_dur_stats) / sum(s["count"] for s in all_dur_stats), 2
            ),
            "min_across_runs_ms": round(min(s["min_ms"] for s in all_dur_stats), 2),
            "max_across_runs_ms": round(max(s["max_ms"] for s in all_dur_stats), 2),
        }

    starts = [r["start_time"] for r in valid if r.get("start_time")]
    ends = [r["end_time"] for r in valid if r.get("end_time")]
    if starts and ends:
        agg["time_window"] = {
            "first_run_start": min(starts),
            "last_run_end": max(ends),
        }

    return agg


def compute_costs(model, stage_aggs):
    cost_info = COST_TABLE[model]
    costs = {"provider": cost_info["provider"]}

    total_input = 0
    total_output = 0
    total_duration_ms = 0.0

    for stage_name, agg in stage_aggs.items():
        if isinstance(agg, dict) and "tokens" in agg:
            total_input += agg["tokens"]["total_input_tokens"]
            total_output += agg["tokens"]["total_output_tokens"]
        if isinstance(agg, dict) and "timing" in agg:
            total_duration_ms += agg["timing"]["total_inference_duration_ms"]

    costs["total_input_tokens"] = total_input
    costs["total_output_tokens"] = total_output
    costs["total_tokens"] = total_input + total_output

    api_input_cost = (total_input / 1_000_000) * cost_info["input_per_1m"]
    api_output_cost = (total_output / 1_000_000) * cost_info["output_per_1m"]
    costs["api_cost_usd"] = {
        "input_cost": round(api_input_cost, 4),
        "output_cost": round(api_output_cost, 4),
        "total_cost": round(api_input_cost + api_output_cost, 4),
        "pricing": {
            "input_per_1m_tokens": cost_info["input_per_1m"],
            "output_per_1m_tokens": cost_info["output_per_1m"],
        },
    }

    if cost_info["provider"] == "ollama":
        elec = compute_electricity_cost(total_duration_ms)
        costs["electricity_cost_usd"] = {
            "total_cost": round(elec, 6),
            "assumptions": {
                "power_watts": LOCAL_COST["power_watts"],
                "cost_per_kwh_usd": LOCAL_COST["cost_per_kwh"],
                "total_inference_hours": round(total_duration_ms / 3600000.0, 4),
            },
        }
        costs["total_estimated_cost_usd"] = round(elec, 4)
    else:
        costs["total_estimated_cost_usd"] = round(api_input_cost + api_output_cost, 4)

    if "note" in cost_info:
        costs["note"] = cost_info["note"]

    return costs


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    summary = {
        "metadata": {
            "generated_at": datetime.now(tz=None).isoformat() + "Z",
            "project": "LLM Evidence Synthesis Reproducibility",
            "base_dir": str(BASE_DIR),
            "models": MODELS,
            "stages": STAGES,
            "runs_per_condition": 10,
            "calls_per_run": 500,
            "design": "6 models x 2 stages x 10 runs x 500 calls = 60,000 LLM calls",
            "cost_assumptions": {
                "gpt-4.1": "$2.00/1M input, $8.00/1M output",
                "claude-sonnet-4-5": "$3.00/1M input, $15.00/1M output",
                "gemini-2.5-pro": "Free tier (rate-limited)",
                "local_models": "Electricity only: M4 ~15W, $0.10/kWh",
            },
        },
        "models": {},
        "grand_totals": {},
    }

    grand_total_calls = 0
    grand_successful = 0
    grand_failed = 0
    grand_duration_ms = 0.0
    grand_input_tokens = 0
    grand_output_tokens = 0
    grand_cost = 0.0
    grand_wall_clock = 0.0

    for model in MODELS:
        print(f"Processing {model}...")
        model_data = {"stages": {}, "runs": {}}

        for stage in STAGES:
            runs = []
            for run_id in range(1, 11):
                run_data = process_run(model, stage, run_id)
                runs.append(run_data)

            model_data["runs"][stage] = runs
            agg = aggregate_model_stage(runs)
            model_data["stages"][stage] = agg

        cross = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_inference_duration_ms": 0.0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_wall_clock_seconds": 0.0,
        }

        for stage in STAGES:
            agg = model_data["stages"][stage]
            if "n_runs" in agg and agg["n_runs"] > 0:
                cross["total_calls"] += agg.get("total_calls", 0)
                cross["successful_calls"] += agg.get("successful_calls", 0)
                cross["failed_calls"] += agg.get("failed_calls", 0)
                cross["total_inference_duration_ms"] += agg.get("timing", {}).get("total_inference_duration_ms", 0.0)
                cross["total_input_tokens"] += agg.get("tokens", {}).get("total_input_tokens", 0)
                cross["total_output_tokens"] += agg.get("tokens", {}).get("total_output_tokens", 0)
                cross["total_wall_clock_seconds"] += agg.get("wall_clock", {}).get("total_seconds", 0.0)

        cross["total_tokens"] = cross["total_input_tokens"] + cross["total_output_tokens"]
        cross["total_inference_duration_min"] = round(cross["total_inference_duration_ms"] / 60000.0, 2)
        cross["total_inference_duration_hr"] = round(cross["total_inference_duration_ms"] / 3600000.0, 4)
        cross["total_wall_clock_minutes"] = round(cross["total_wall_clock_seconds"] / 60.0, 2)
        cross["total_wall_clock_hours"] = round(cross["total_wall_clock_seconds"] / 3600.0, 4)
        if cross["successful_calls"] > 0:
            cross["mean_duration_per_call_ms"] = round(
                cross["total_inference_duration_ms"] / cross["successful_calls"], 2
            )
            cross["mean_input_tokens_per_call"] = round(
                cross["total_input_tokens"] / cross["successful_calls"], 1
            )
            cross["mean_output_tokens_per_call"] = round(
                cross["total_output_tokens"] / cross["successful_calls"], 1
            )
            cross["throughput_tokens_per_second"] = round(
                cross["total_tokens"] / (cross["total_inference_duration_ms"] / 1000.0), 2
            )

        model_data["cross_stage_totals"] = cross
        model_data["costs"] = compute_costs(model, model_data["stages"])

        per_run_summary = {}
        for stage in STAGES:
            per_run_summary[stage] = []
            for r in model_data["runs"][stage]:
                entry = {
                    "run_id": r["run_id"],
                    "exists": r["exists"],
                    "total_duration_ms": r.get("total_duration_ms"),
                    "mean_duration_ms": r.get("mean_duration_ms"),
                    "successful_calls": r.get("successful_calls"),
                    "failed_calls": r.get("failed_calls"),
                    "wall_clock_seconds": r.get("wall_clock_seconds"),
                    "input_tokens": r.get("token_counts", {}).get("total_input_tokens"),
                    "output_tokens": r.get("token_counts", {}).get("total_output_tokens"),
                }
                if "duration_stats_from_records" in r:
                    entry["call_duration_p25_ms"] = r["duration_stats_from_records"]["p25_ms"]
                    entry["call_duration_median_ms"] = r["duration_stats_from_records"]["median_ms"]
                    entry["call_duration_p75_ms"] = r["duration_stats_from_records"]["p75_ms"]
                per_run_summary[stage].append(entry)
        model_data["per_run_summary"] = per_run_summary
        del model_data["runs"]

        summary["models"][model] = model_data

        grand_total_calls += cross["total_calls"]
        grand_successful += cross["successful_calls"]
        grand_failed += cross["failed_calls"]
        grand_duration_ms += cross["total_inference_duration_ms"]
        grand_input_tokens += cross["total_input_tokens"]
        grand_output_tokens += cross["total_output_tokens"]
        grand_cost += model_data["costs"]["total_estimated_cost_usd"]
        grand_wall_clock += cross["total_wall_clock_seconds"]

    summary["grand_totals"] = {
        "total_calls": grand_total_calls,
        "successful_calls": grand_successful,
        "failed_calls": grand_failed,
        "total_inference_duration_ms": round(grand_duration_ms, 2),
        "total_inference_duration_min": round(grand_duration_ms / 60000.0, 2),
        "total_inference_duration_hr": round(grand_duration_ms / 3600000.0, 4),
        "total_wall_clock_seconds": round(grand_wall_clock, 2),
        "total_wall_clock_minutes": round(grand_wall_clock / 60.0, 2),
        "total_wall_clock_hours": round(grand_wall_clock / 3600.0, 4),
        "total_input_tokens": grand_input_tokens,
        "total_output_tokens": grand_output_tokens,
        "total_tokens": grand_input_tokens + grand_output_tokens,
        "total_estimated_cost_usd": round(grand_cost, 4),
        "cost_breakdown": {
            "api_models_cost_usd": round(
                sum(
                    summary["models"][m]["costs"]["total_estimated_cost_usd"]
                    for m in MODELS
                    if COST_TABLE[m]["provider"] != "ollama"
                ),
                4,
            ),
            "local_electricity_cost_usd": round(
                sum(
                    summary["models"][m]["costs"]["total_estimated_cost_usd"]
                    for m in MODELS
                    if COST_TABLE[m]["provider"] == "ollama"
                ),
                6,
            ),
        },
        "mean_duration_per_call_ms": round(grand_duration_ms / grand_successful, 2) if grand_successful > 0 else None,
    }

    out_path = OUT_DIR / "timing_and_costs.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\nOutput written to: {out_path}")
    print(f"\n{'='*70}")
    print("GRAND TOTALS")
    print(f"{'='*70}")
    gt = summary["grand_totals"]
    print(f"Total calls:          {gt['total_calls']:,}")
    print(f"Successful calls:     {gt['successful_calls']:,}")
    print(f"Failed calls:         {gt['failed_calls']:,}")
    print(f"Total inference time: {gt['total_inference_duration_hr']:.2f} hours ({gt['total_inference_duration_min']:.1f} min)")
    print(f"Total wall clock:     {gt['total_wall_clock_hours']:.2f} hours ({gt['total_wall_clock_minutes']:.1f} min)")
    print(f"Total tokens:         {gt['total_tokens']:,} (in: {gt['total_input_tokens']:,}, out: {gt['total_output_tokens']:,})")
    print(f"Mean per call:        {gt['mean_duration_per_call_ms']:.1f} ms")
    print(f"Total cost:           ${gt['total_estimated_cost_usd']:.4f}")
    print()

    hdr = f"{'Model':<22} {'Calls':>7} {'OK':>7} {'Fail':>5} {'Infer(hr)':>10} {'Wall(hr)':>10} {'InTok':>10} {'OutTok':>10} {'Cost($)':>10}"
    print(hdr)
    print("-" * len(hdr))
    for model in MODELS:
        m = summary["models"][model]
        c = m["cross_stage_totals"]
        cost = m["costs"]["total_estimated_cost_usd"]
        print(
            f"{model:<22} {c['total_calls']:>7,} {c['successful_calls']:>7,} {c['failed_calls']:>5,} "
            f"{c['total_inference_duration_hr']:>10.3f} {c['total_wall_clock_hours']:>10.3f} "
            f"{c['total_input_tokens']:>10,} {c['total_output_tokens']:>10,} "
            f"${cost:>9.4f}"
        )

    print(f"\n{'='*70}")
    print("THROUGHPUT (tokens/sec)")
    print(f"{'='*70}")
    for model in MODELS:
        c = summary["models"][model]["cross_stage_totals"]
        tp = c.get("throughput_tokens_per_second", 0)
        mean_ms = c.get("mean_duration_per_call_ms", 0)
        print(f"  {model:<22} {tp:>8.1f} tok/s   (mean {mean_ms:.0f} ms/call)")


if __name__ == "__main__":
    main()
