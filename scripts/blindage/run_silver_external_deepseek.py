"""Silver-external gold standard via DeepSeek-R1 reasoning model.

Runs DeepSeek-R1 on all 100 INCLUDE abstracts × 5 runs to produce an
INDEPENDENT extraction reference for the existing 6-model study. R1 is
chosen because:
    1. Different provider family (DeepSeek vs OpenAI/Anthropic/Google/Meta)
    2. Different paradigm (explicit reasoning vs standard chat)
    3. Different training data (Chinese-led, mixed open/closed datasets)

This breaks the circularity that would arise from using majority-vote of the
same 6 evaluated models as their own gold.

5 runs per abstract because R1 is more stable than non-reasoning chat models;
majority/consensus across 5 runs gives a robust silver-external estimate.

Output: data/raw_outputs/deepseek-r1-silver/extraction/run_NNN/
        + analysis/blindage/silver_standard_external.json (consensus)
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from models.deepseek_runner import run_inference  # noqa: E402

MODEL_NAME = "deepseek-r1-silver"
DEEPSEEK_MODEL = "deepseek-reasoner"
CORPUS = ROOT / "data" / "corpus" / "corpus_500.json"
PROMPT = (ROOT / "configs" / "prompts" / "extraction.txt").read_text()
RAW_ROOT = ROOT / "data" / "raw_outputs" / MODEL_NAME

N_RUNS = 5
MAX_RETRIES = 2
BACKOFF = [10, 30]
SLEEP_BETWEEN = 1.0


def parse_json_output(text: str) -> dict | None:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1] if text.count("```") >= 2 else text
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    depth, start = 0, None
    for i, c in enumerate(text):
        if c == "{":
            if start is None:
                start = i
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError:
                    start = None
    return None


def output_hash(obj) -> str:
    canonical = json.dumps(obj, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def call_with_retry(prompt: str, input_text: str) -> dict:
    for attempt in range(MAX_RETRIES + 1):
        try:
            return run_inference(
                prompt=prompt,
                input_text=input_text,
                model=DEEPSEEK_MODEL,
                max_tokens=4096,
                timeout=180,
            )
        except RuntimeError as e:
            if attempt < MAX_RETRIES:
                wait = BACKOFF[min(attempt, len(BACKOFF) - 1)]
                print(f"    error: {str(e)[:80]}; retry {attempt+1}/{MAX_RETRIES} after {wait}s", flush=True)
                time.sleep(wait)
                continue
            raise


def run_one(run_id: int):
    items = [c for c in json.loads(CORPUS.read_text())["corpus"]
             if c["gold_category"] == "include"]
    out_dir = RAW_ROOT / "extraction" / f"run_{run_id:03d}"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    call_records = []
    t_start = datetime.now(timezone.utc)

    print(f"  run_{run_id:03d}: {len(items)} INCLUDE items via DeepSeek-R1", flush=True)
    for i, item in enumerate(items):
        abs_text = f"Title: {item['title']}\nAbstract: {item['abstract']}"
        try:
            resp = call_with_retry(PROMPT, abs_text)
            parsed = parse_json_output(resp["output_text"])
            oh = output_hash(parsed) if parsed else output_hash({"_raw": resp["output_text"]})
            results.append({
                "corpus_id": item["corpus_id"],
                "pmid": item.get("pmid"),
                "run_id": run_id,
                "model_id": MODEL_NAME,
                "output": parsed or {"_raw_unparseable": resp["output_text"][:500]},
                "valid": parsed is not None,
                "output_hash": oh,
            })
            call_records.append({
                "corpus_id": item["corpus_id"],
                "stage": "extraction",
                "run_id": run_id,
                "model_id": MODEL_NAME,
                "provider": "deepseek",
                "output_hash": oh,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "inference_duration_ms": resp["duration_ms"],
                "input_tokens": resp["input_tokens"],
                "output_tokens": resp["output_tokens"],
                "reasoning_tokens": resp.get("reasoning_tokens"),
                "finish_reason": resp["finish_reason"],
            })
            if (i + 1) % 10 == 0:
                done = sum(1 for r in results if r["valid"])
                print(f"    {i+1}/{len(items)}  ok={done}", flush=True)
        except Exception as e:
            print(f"    ERR {item['corpus_id']}: {str(e)[:200]}", flush=True)
            results.append({
                "corpus_id": item["corpus_id"], "run_id": run_id,
                "model_id": MODEL_NAME, "output": None,
                "valid": False, "error": str(e)[:500], "output_hash": None,
            })
        time.sleep(SLEEP_BETWEEN)

    t_end = datetime.now(timezone.utc)
    run_card = {
        "model_id": MODEL_NAME,
        "deepseek_model": DEEPSEEK_MODEL,
        "stage": "extraction",
        "run_id": run_id,
        "n_items": len(items),
        "n_success": sum(1 for r in results if r["valid"]),
        "n_fail": sum(1 for r in results if not r["valid"]),
        "started": t_start.isoformat(),
        "ended": t_end.isoformat(),
        "duration_seconds": (t_end - t_start).total_seconds(),
        "total_input_tokens": sum(c.get("input_tokens") or 0 for c in call_records),
        "total_output_tokens": sum(c.get("output_tokens") or 0 for c in call_records),
        "total_reasoning_tokens": sum(c.get("reasoning_tokens") or 0 for c in call_records),
    }
    (out_dir / "results.json").write_text(json.dumps(results, indent=2))
    (out_dir / "call_records.json").write_text(json.dumps(call_records, indent=2))
    (out_dir / "run_card.json").write_text(json.dumps(run_card, indent=2))
    return run_card


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="1-5")
    args = ap.parse_args()
    if "-" in args.runs:
        lo, hi = args.runs.split("-")
        runs = range(int(lo), int(hi) + 1)
    else:
        runs = [int(r) for r in args.runs.split(",")]
    print(f"=== DeepSeek-R1 Silver-External Gold Standard ===", flush=True)
    print(f"Model: {DEEPSEEK_MODEL}  Runs: {list(runs)}", flush=True)
    for r in runs:
        rc = run_one(r)
        print(f"  run_{r:03d}: {rc['n_success']}/{rc['n_items']} success, "
              f"{rc['duration_seconds']:.0f}s, "
              f"tokens in={rc['total_input_tokens']} out={rc['total_output_tokens']} "
              f"reasoning={rc['total_reasoning_tokens']}", flush=True)


if __name__ == "__main__":
    main()
