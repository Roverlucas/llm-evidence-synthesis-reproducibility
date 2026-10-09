"""Request size and recorded provider in the same-weights comparison (screening).

Mean input tokens per call for the local LLaMA 3 8B stack and for the cloud arm,
from the deposited call records, and the provider field as recorded. The cloud
script wrote a fixed provider string; the run cards record the route actually used.

Output: analysis/blindage/samemodel_payload.json
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw_outputs"
OUT = ROOT / "analysis" / "blindage" / "samemodel_payload.json"


def arm(stack: str) -> dict:
    toks, providers, cards = [], Counter(), Counter()
    for path in sorted((RAW / stack / "screening").glob("run_*")):
        for r in json.loads((path / "call_records.json").read_text()):
            if r.get("input_tokens"):
                toks.append(r["input_tokens"])
            providers[r.get("provider")] += 1
        card = json.loads((path / "run_card.json").read_text())
        cards[card.get("provider")] += 1
    return {
        "n_calls_with_tokens": len(toks),
        "mean_input_tokens": round(sum(toks) / len(toks), 1),
        "call_record_provider": dict(providers),
        "run_card_provider": {str(k): v for k, v in cards.items()},
    }


def main() -> None:
    local, cloud = arm("llama3-8b"), arm("llama3-8b-cloud")
    payload = {
        "local": local,
        "cloud": cloud,
        "input_token_difference_pct_of_local": round(
            100 * (local["mean_input_tokens"] - cloud["mean_input_tokens"]) / local["mean_input_tokens"], 1),
    }
    body = json.dumps(payload, indent=2, sort_keys=True).encode()
    payload["sha256_self"] = hashlib.sha256(body).hexdigest()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
