"""Jev screening arm (decision 42): 500 abstracts × N runs through Vercel AI Gateway.

Same corpus, same criteria wording and same input formatting as the LLM stacks.
Output: data/raw_outputs/jev/screening/run_NNN/{results,call_records,run_card}.json

Usage:
    python scripts/run_jev_screening.py --runs 1-10
    python scripts/run_jev_screening.py --pilot 5     # prints answers, writes nothing
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from models.jev_runner import (  # noqa: E402
    DEFAULT_MODEL, get_model_info, run_decision, screening_criteria_from_prompt,
)

CORPUS = ROOT / "data" / "corpus" / "corpus_500.json"
PROMPT = ROOT / "configs" / "prompts" / "screening.txt"
MODEL_ID = "jev"
SLEEP = 0.2


def state_for(article: dict) -> str:
    # Same formatting as src/screening/runner.py
    return f"Title: {article['title']}\n\nAbstract: {article['abstract']}"


def answer_hash(choice, probabilities) -> str:
    obj = {"choice": choice, "probabilities": probabilities}
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


def run_one(run_id: int, articles: list[dict], instructions: str) -> dict:
    out_dir = ROOT / "data" / "raw_outputs" / MODEL_ID / "screening" / f"run_{run_id:03d}"
    card_path = out_dir / "run_card.json"
    if card_path.exists():
        card = json.loads(card_path.read_text())
        if card["execution"]["successful_calls"] == card["execution"]["total_calls"]:
            print(f"  run_{run_id:03d} already complete, skipping", flush=True)
            return card
    out_dir.mkdir(parents=True, exist_ok=True)

    results, records = [], []
    t_start = datetime.now(timezone.utc)
    for i, art in enumerate(articles):
        try:
            r = run_decision(state_for(art), instructions)
            if r["final_provider"] not in (None, "typesafe-ai"):
                raise RuntimeError(f"answered by {r['final_provider']}, not typesafe-ai")
            oh = answer_hash(r["choice"], r["probabilities"])
            results.append({
                "corpus_id": art["corpus_id"], "pmid": art.get("pmid"),
                "run_id": run_id, "model_id": MODEL_ID,
                "output": {"decision": r["choice"], "probabilities": r["probabilities"]},
                "valid": r["choice"] is not None, "output_hash": oh,
            })
            records.append({
                "corpus_id": art["corpus_id"], "stage": "screening", "run_id": run_id,
                "model_id": MODEL_ID, "provider": "typesafe-ai", "output_hash": oh,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "inference_duration_ms": r["inference_duration_ms"],
                "input_tokens": r["input_tokens"], "output_tokens": r["output_tokens"],
                "cost_usd": r["cost_usd"], "generation_id": r["generation_id"],
                "served_model": r["model_id"], "final_provider": r["final_provider"],
            })
        except Exception as e:  # keep going; the failure is recorded, not hidden
            print(f"    ERR {art['corpus_id']}: {str(e)[:200]}", flush=True)
            results.append({"corpus_id": art["corpus_id"], "run_id": run_id,
                            "model_id": MODEL_ID, "output": None, "valid": False,
                            "error": str(e)[:500], "output_hash": None})
        if (i + 1) % 50 == 0:
            print(f"    run_{run_id:03d} {i + 1}/{len(articles)}", flush=True)
        time.sleep(SLEEP)

    t_end = datetime.now(timezone.utc)
    ok = sum(1 for r in results if r["valid"])
    card = {
        "run_card_version": "1.0", "run_id": run_id, "stage": "screening",
        "model_id": MODEL_ID, "provider": "typesafe-ai",
        "model_info": get_model_info(DEFAULT_MODEL),
        "config": {"question_type": "choice", "options": ["include", "exclude", "uncertain"],
                   "gateway_only": ["typesafe-ai"], "fallbacks": "none"},
        "execution": {"start_time": t_start.isoformat(), "end_time": t_end.isoformat(),
                      "total_calls": len(results), "successful_calls": ok,
                      "failed_calls": len(results) - ok},
        "total_cost_usd": round(sum(float(c["cost_usd"] or 0) for c in records), 6),
    }
    (out_dir / "results.json").write_text(json.dumps(results, indent=2))
    (out_dir / "call_records.json").write_text(json.dumps(records, indent=2))
    card_path.write_text(json.dumps(card, indent=2))
    print(f"  run_{run_id:03d}: {ok}/{len(results)} ok, US$ {card['total_cost_usd']}", flush=True)
    return card


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="1-10")
    ap.add_argument("--pilot", type=int, default=0,
                    help="Print answers for the first N abstracts and write nothing")
    args = ap.parse_args()

    articles = json.loads(CORPUS.read_text())["corpus"]
    instructions = screening_criteria_from_prompt(PROMPT.read_text())

    if args.pilot:
        for art in articles[: args.pilot]:
            r = run_decision(state_for(art), instructions)
            print(json.dumps({"corpus_id": art["corpus_id"], "gold": art.get("gold_category"), **r}))
        return

    a, _, b = args.runs.partition("-")
    for run_id in range(int(a), int(b or a) + 1):
        run_one(run_id, articles, instructions)


if __name__ == "__main__":
    main()
