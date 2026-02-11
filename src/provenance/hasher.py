"""
Provenance module — SHA-256 hashing and run card generation.

Implements the lightweight provenance protocol from the JAIR paper,
adapted for evidence synthesis pipelines.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def compute_call_hash(
    prompt: str,
    input_text: str,
    model_id: str,
    temperature: float,
    seed: Optional[int] = None,
) -> str:
    """Compute SHA-256 hash of a single LLM call's inputs."""
    fields = {
        "prompt": prompt,
        "input_text": input_text,
        "model_id": model_id,
        "temperature": temperature,
        "seed": seed,
    }
    canonical = json.dumps(fields, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def compute_output_hash(output_text: str) -> str:
    """Compute SHA-256 hash of the LLM output."""
    return hashlib.sha256(output_text.encode()).hexdigest()


def create_call_record(
    corpus_id: str,
    call_hash: str,
    output_hash: str,
    model_id: str,
    provider: str,
    stage: str,
    run_id: int,
    inference_result: dict,
) -> dict:
    """Create a provenance record for a single LLM call."""
    return {
        "corpus_id": corpus_id,
        "stage": stage,
        "run_id": run_id,
        "model_id": model_id,
        "provider": provider,
        "call_hash": call_hash,
        "output_hash": output_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "inference_duration_ms": inference_result.get("inference_duration_ms"),
        "input_tokens": inference_result.get("input_tokens") or inference_result.get("prompt_eval_count"),
        "output_tokens": inference_result.get("output_tokens") or inference_result.get("eval_count"),
        "stop_reason": (
            inference_result.get("stop_reason")
            or inference_result.get("done_reason")
            or inference_result.get("finish_reason")
        ),
    }


def create_run_card(
    run_id: int,
    model_id: str,
    provider: str,
    stage: str,
    total_calls: int,
    successful_calls: int,
    failed_calls: int,
    call_records: list[dict],
    model_info: dict,
    config: dict,
    start_time: str,
    end_time: str,
) -> dict:
    """Create a run card summarizing a complete experimental run."""
    # Compute aggregate hash over all outputs
    all_output_hashes = sorted(r["output_hash"] for r in call_records)
    aggregate_hash = hashlib.sha256(
        "|".join(all_output_hashes).encode()
    ).hexdigest()

    durations = [r["inference_duration_ms"] for r in call_records if r["inference_duration_ms"]]
    total_duration = sum(durations) if durations else 0

    return {
        "run_card_version": "1.0",
        "run_id": run_id,
        "stage": stage,
        "model_id": model_id,
        "provider": provider,
        "model_info": model_info,
        "config": {
            "temperature": config.get("temperature", 0),
            "seed": config.get("seed"),
            "max_tokens": config.get("max_tokens") or config.get("num_predict") or config.get("max_output_tokens"),
        },
        "execution": {
            "start_time": start_time,
            "end_time": end_time,
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "total_duration_ms": round(total_duration, 1),
            "mean_duration_ms": round(total_duration / len(durations), 1) if durations else 0,
        },
        "provenance": {
            "aggregate_output_hash": aggregate_hash,
            "hash_algorithm": "sha256",
        },
    }


def save_run_outputs(
    output_dir: str,
    run_id: int,
    model_id: str,
    stage: str,
    results: list[dict],
    call_records: list[dict],
    run_card: dict,
):
    """Save all outputs for a single run to disk."""
    base = Path(output_dir) / model_id / stage / f"run_{run_id:03d}"
    base.mkdir(parents=True, exist_ok=True)

    # Save results
    with open(base / "results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Save call records (provenance)
    with open(base / "call_records.json", "w", encoding="utf-8") as f:
        json.dump(call_records, f, indent=2, ensure_ascii=False)

    # Save run card
    with open(base / "run_card.json", "w", encoding="utf-8") as f:
        json.dump(run_card, f, indent=2, ensure_ascii=False)

    return str(base)
