"""P0.1 — LLaMA cloud desconfound experiment (Editor blocker #1).

Runs LLaMA 3.1 8B Instant via Groq cloud with the SAME prompt, seed, temperature
as the local LLaMA 3 8B via Ollama. Any EMR difference vs local is attributable
to DEPLOYMENT infrastructure (not model/prompt).

Design:
    - Model: llama-3.1-8b-instant (Groq)
    - Local counterpart: llama3:8b (Ollama) — achieved EMR=1.000 with seed=42
    - Stages: screening (500 × 10) + extraction (100 × 10) = 6000 calls
    - Seed: 42 (same as local)
    - Temperature: 0.0 (same as local)

Rate limits: Groq free tier limits llama-3.1-8b-instant to:
    - 30 requests/minute
    - 14,400 requests/day
We pace at 2s between calls (30 rpm) plus retry with backoff on 429.

Outputs:
    data/raw_outputs/llama3-8b-cloud/{screening,extraction}/run_NNN/
        - results.json
        - call_records.json
        - run_card.json
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

from models.openrouter_runner import run_inference  # noqa: E402

MODEL_NAME = "llama3-8b-cloud"
CLOUD_MODEL = "meta-llama/llama-3-8b-instruct"  # EXACT same version as local llama3:8b
PROVIDER = "DeepInfra"  # Pin single provider for reproducibility
CORPUS = ROOT / "data" / "corpus" / "corpus_500.json"
PROMPTS = {
    "screening": (ROOT / "configs" / "prompts" / "screening.txt").read_text(),
    "extraction": (ROOT / "configs" / "prompts" / "extraction.txt").read_text(),
}
RAW_ROOT = ROOT / "data" / "raw_outputs" / MODEL_NAME

RATE_LIMIT_SLEEP = 1.0  # seconds between calls (DeepInfra has higher rate limits)
MAX_RETRIES = 3
BACKOFF_SECONDS = [5, 15, 45]

N_RUNS = 10
STAGES = {
    "screening": {"max_tokens": 512, "filter": None},  # all 500 abstracts
    "extraction": {"max_tokens": 2048, "filter": "include"},  # 100 include abstracts only
}


def canonical_hash(prompt: str, input_text: str, model: str, temperature: float, seed: int | None) -> str:
    fields = {
        "prompt": prompt,
        "input_text": input_text,
        "model_id": model,
        "temperature": temperature,
        "seed": seed,
    }
    canonical = json.dumps(fields, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def output_hash(output_obj) -> str:
    canonical = json.dumps(output_obj, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def parse_json_output(text: str) -> dict | None:
    """Tolerant JSON parse: finds the first valid JSON object in the response."""
    text = text.strip()
    # Strip markdown code fences
    if text.startswith("```"):
        text = text.split("```", 2)[1] if text.count("```") >= 2 else text
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Fallback: find first {...} balanced block
    depth = 0
    start = None
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


def load_items(stage: str):
    corpus = json.loads(CORPUS.read_text())["corpus"]
    if STAGES[stage]["filter"] == "include":
        corpus = [c for c in corpus if c["gold_category"] == "include"]
    return corpus


def call_with_retry(prompt: str, input_text: str, max_tokens: int, seed: int) -> dict:
    for attempt in range(MAX_RETRIES + 1):
        try:
            return run_inference(
                prompt=prompt,
                input_text=input_text,
                model=CLOUD_MODEL,
                temperature=0.0,
                seed=seed,
                max_tokens=max_tokens,
                timeout=120,
                provider_preferences=[PROVIDER],
            )
        except RuntimeError as e:
            msg = str(e)
            if "429" in msg or "rate" in msg.lower():
                wait = BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)]
                print(f"    rate-limited, sleeping {wait}s...")
                time.sleep(wait)
                continue
            if attempt < MAX_RETRIES:
                wait = BACKOFF_SECONDS[min(attempt, len(BACKOFF_SECONDS) - 1)]
                print(f"    error '{msg[:80]}', retry {attempt+1}/{MAX_RETRIES} after {wait}s")
                time.sleep(wait)
                continue
            raise


def run_one(stage: str, run_id: int) -> dict:
    prompt = PROMPTS[stage]
    items = load_items(stage)
    out_dir = RAW_ROOT / stage / f"run_{run_id:03d}"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    call_records = []
    t_start = datetime.now(timezone.utc)

    print(f"  run_{run_id:03d}: {len(items)} items")
    for i, item in enumerate(items):
        abs_text = f"Title: {item['title']}\nAbstract: {item['abstract']}"
        ch = canonical_hash(prompt, abs_text, CLOUD_MODEL, 0.0, 42)

        try:
            resp = call_with_retry(
                prompt=prompt,
                input_text=abs_text,
                max_tokens=STAGES[stage]["max_tokens"],
                seed=42,
            )
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
                "stage": stage,
                "run_id": run_id,
                "model_id": MODEL_NAME,
                "provider": "groq",
                "call_hash": ch,
                "output_hash": oh,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "inference_duration_ms": resp["duration_ms"],
                "input_tokens": resp["input_tokens"],
                "output_tokens": resp["output_tokens"],
                "finish_reason": resp["finish_reason"],
            })
            if (i + 1) % 50 == 0:
                print(f"    {i+1}/{len(items)} done")
        except Exception as e:
            print(f"    ERROR on {item['corpus_id']}: {str(e)[:200]}")
            results.append({
                "corpus_id": item["corpus_id"],
                "run_id": run_id,
                "model_id": MODEL_NAME,
                "output": None,
                "valid": False,
                "error": str(e)[:500],
                "output_hash": None,
            })
        time.sleep(RATE_LIMIT_SLEEP)

    t_end = datetime.now(timezone.utc)
    run_card = {
        "model_id": MODEL_NAME,
        "provider": "openrouter:DeepInfra",
        "underlying_model": CLOUD_MODEL,
        "stage": stage,
        "run_id": run_id,
        "temperature": 0.0,
        "seed": 42,
        "max_tokens": STAGES[stage]["max_tokens"],
        "n_items": len(items),
        "n_success": sum(1 for r in results if r["valid"]),
        "n_fail": sum(1 for r in results if not r["valid"]),
        "started": t_start.isoformat(),
        "ended": t_end.isoformat(),
        "duration_seconds": (t_end - t_start).total_seconds(),
        "total_input_tokens": sum(c.get("input_tokens") or 0 for c in call_records),
        "total_output_tokens": sum(c.get("output_tokens") or 0 for c in call_records),
    }

    (out_dir / "results.json").write_text(json.dumps(results, indent=2))
    (out_dir / "call_records.json").write_text(json.dumps(call_records, indent=2))
    (out_dir / "run_card.json").write_text(json.dumps(run_card, indent=2))
    return run_card


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=list(STAGES), required=True)
    ap.add_argument("--runs", default="1-10")
    args = ap.parse_args()

    if "-" in args.runs:
        lo, hi = args.runs.split("-")
        runs = range(int(lo), int(hi) + 1)
    else:
        runs = [int(r) for r in args.runs.split(",")]

    print(f"=== LLaMA 3 8B Cloud (OpenRouter:DeepInfra) — desconfound experiment ===")
    print(f"Stage: {args.stage}  Runs: {list(runs)}  Model: {CLOUD_MODEL}  Provider: {PROVIDER}")
    for r in runs:
        rc = run_one(args.stage, r)
        print(f"  run_{r:03d}: {rc['n_success']}/{rc['n_items']} success, "
              f"duration={rc['duration_seconds']:.0f}s, "
              f"tokens in={rc['total_input_tokens']} out={rc['total_output_tokens']}")


if __name__ == "__main__":
    main()
