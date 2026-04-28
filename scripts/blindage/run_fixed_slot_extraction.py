"""P1.2 — Fixed-slot extraction sensitivity experiment.

Runs the fixed-slot extraction prompt (single primary estimate, no array)
on 3 cloud models × 10 runs × 100 abstracts to test whether prompt-design
amplification accounts for the cloud APIs' high non-determinism rates.

Comparison:
    - Current (variable-length array): Claude EMR=0.05, Gemini=0.20, GPT-4.1=0.15
    - Fixed-slot (single estimate): TO BE MEASURED

Cost estimate (3 × 10 × 100 = 3000 calls):
    - Claude Sonnet 4.5: ~$2.50 (1500 input + 500 output tokens × $3/$15 per 1M)
    - GPT-4.1: ~$2.00 ($2/$8 per 1M)
    - Gemini 2.5 Pro: free tier
    - TOTAL: ~$5

Output: data/raw_outputs/{model}_fixedslot/extraction/run_NNN/
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

CORPUS = ROOT / "data" / "corpus" / "corpus_500.json"
PROMPT = (ROOT / "configs" / "prompts" / "extraction_fixed_slot.txt").read_text()
SLEEP = 0.5

# Provider config (uses existing runners)
MODELS = {
    "claude-sonnet-4-5-fixedslot": {
        "runner": "claude_runner",
        "model_arg": "claude-sonnet-4-5-20250929",
        "max_tokens": 1500,
    },
    "gemini-2.5-pro-fixedslot": {
        "runner": "gemini_runner",
        "model_arg": "gemini-2.5-pro",
        "max_tokens": 4096,
    },
    "gpt-4.1-fixedslot": {
        "runner": "openai_runner",
        "model_arg": "gpt-4.1",
        "max_tokens": 1500,
    },
}


def load_runner(name: str):
    if name == "claude_runner":
        from models.claude_runner import run_inference
    elif name == "gemini_runner":
        from models.gemini_runner import run_inference
    elif name == "openai_runner":
        from models.openai_runner import run_inference
    else:
        raise ValueError(f"Unknown runner: {name}")
    return run_inference


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
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=True).encode()).hexdigest()


def call_runner(run_inf, model_arg, prompt, abs_text, max_tokens):
    """Call runner with appropriate kwargs per provider."""
    # Try with seed first
    try:
        return run_inf(
            prompt=prompt, input_text=abs_text, model=model_arg,
            temperature=0.0, max_tokens=max_tokens, seed=42,
        )
    except TypeError:
        pass
    # Try without seed (Claude)
    try:
        return run_inf(
            prompt=prompt, input_text=abs_text, model=model_arg,
            temperature=0.0, max_tokens=max_tokens,
        )
    except TypeError:
        pass
    # Try gemini-style (max_output_tokens)
    return run_inf(
        prompt=prompt, input_text=abs_text, model=model_arg,
        temperature=0.0, max_output_tokens=max_tokens, seed=42,
    )


def get_duration_ms(resp):
    return resp.get("inference_duration_ms") or resp.get("duration_ms") or 0


def run_one(model_name: str, run_id: int):
    cfg = MODELS[model_name]
    run_inf = load_runner(cfg["runner"])
    items = [c for c in json.loads(CORPUS.read_text())["corpus"]
             if c["gold_category"] == "include"]
    out_dir = ROOT / "data" / "raw_outputs" / model_name / "extraction" / f"run_{run_id:03d}"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    call_records = []
    t_start = datetime.now(timezone.utc)
    print(f"  {model_name} run_{run_id:03d}: {len(items)} items", flush=True)

    for i, item in enumerate(items):
        abs_text = f"Title: {item['title']}\nAbstract: {item['abstract']}"
        try:
            resp = call_runner(run_inf, cfg["model_arg"], PROMPT, abs_text, cfg["max_tokens"])
            text_out = resp.get("output_text") or resp.get("output", "")
            parsed = parse_json_output(text_out)
            oh = output_hash(parsed) if parsed else output_hash({"_raw": text_out})
            results.append({
                "corpus_id": item["corpus_id"],
                "pmid": item.get("pmid"),
                "run_id": run_id, "model_id": model_name,
                "output": parsed or {"_raw_unparseable": text_out[:500]},
                "valid": parsed is not None, "output_hash": oh,
            })
            call_records.append({
                "corpus_id": item["corpus_id"], "stage": "extraction",
                "run_id": run_id, "model_id": model_name,
                "output_hash": oh, "timestamp": datetime.now(timezone.utc).isoformat(),
                "inference_duration_ms": get_duration_ms(resp),
                "input_tokens": resp.get("input_tokens"),
                "output_tokens": resp.get("output_tokens"),
            })
            if (i + 1) % 25 == 0:
                done = sum(1 for r in results if r["valid"])
                print(f"    {i+1}/{len(items)}  ok={done}", flush=True)
        except Exception as e:
            print(f"    ERR {item['corpus_id']}: {str(e)[:200]}", flush=True)
            results.append({"corpus_id": item["corpus_id"], "run_id": run_id,
                            "model_id": model_name, "output": None,
                            "valid": False, "error": str(e)[:500],
                            "output_hash": None})
        time.sleep(SLEEP)

    t_end = datetime.now(timezone.utc)
    rc = {
        "model_id": model_name, "stage": "extraction", "run_id": run_id,
        "n_items": len(items),
        "n_success": sum(1 for r in results if r["valid"]),
        "n_fail": sum(1 for r in results if not r["valid"]),
        "started": t_start.isoformat(), "ended": t_end.isoformat(),
        "duration_seconds": (t_end - t_start).total_seconds(),
        "total_input_tokens": sum(c.get("input_tokens") or 0 for c in call_records),
        "total_output_tokens": sum(c.get("output_tokens") or 0 for c in call_records),
    }
    (out_dir / "results.json").write_text(json.dumps(results, indent=2))
    (out_dir / "call_records.json").write_text(json.dumps(call_records, indent=2))
    (out_dir / "run_card.json").write_text(json.dumps(rc, indent=2))
    return rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=list(MODELS) + ["all"])
    ap.add_argument("--runs", default="1-10")
    args = ap.parse_args()
    if "-" in args.runs:
        lo, hi = args.runs.split("-")
        runs = range(int(lo), int(hi) + 1)
    else:
        runs = [int(r) for r in args.runs.split(",")]
    models = list(MODELS) if args.model == "all" else [args.model]
    print(f"=== Fixed-Slot Extraction Sensitivity ===", flush=True)
    print(f"Models: {models}  Runs: {list(runs)}", flush=True)
    for m in models:
        for r in runs:
            rc = run_one(m, r)
            print(f"  [{m}] run_{r:03d}: {rc['n_success']}/{rc['n_items']} success, "
                  f"{rc['duration_seconds']:.0f}s, "
                  f"tokens in={rc['total_input_tokens']} out={rc['total_output_tokens']}", flush=True)


if __name__ == "__main__":
    main()
