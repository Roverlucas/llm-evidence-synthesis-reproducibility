#!/usr/bin/env python3
"""
Experiment Orchestrator — PM2.5 Evidence Synthesis Reproducibility Study.

Runs 30 repetitions × 3 models × 2 stages (screening + extraction).
Total: ~58,500 LLM calls.

Usage:
    # Full experiment (all models, all runs)
    python run_experiment.py

    # Single model
    python run_experiment.py --model llama3-8b

    # Specific run range
    python run_experiment.py --model claude-sonnet-4-5 --runs 1-5

    # Screening only
    python run_experiment.py --stage screening

    # Dry run (1 abstract, 1 run)
    python run_experiment.py --dry-run
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from src.utils.env_loader import load_env
load_env()  # Load .env before importing runners

from src.screening.runner import run_screening
from src.extraction.runner import run_extraction
from src.provenance.hasher import create_run_card, save_run_outputs


# ── Model configurations ────────────────────────────────────

MODEL_CONFIGS = {
    "llama3-8b": {
        "id": "llama3-8b",
        "provider": "ollama",
        "model": "llama3:8b",
        "endpoint": "http://localhost:11434",
        "temperature": 0.0,
        "seed": 42,
        "num_predict": 2048,
    },
    "claude-sonnet-4-5": {
        "id": "claude-sonnet-4-5",
        "provider": "anthropic",
        "model": "claude-sonnet-4-5-20250929",
        "temperature": 0.0,
        "max_tokens": 2048,
    },
    "gemini-2.5-pro": {
        "id": "gemini-2.5-pro",
        "provider": "google",
        "model": "gemini-2.5-pro",
        "temperature": 0.0,
        "max_output_tokens": 8192,
        "seed": 42,
    },
}

OUTPUT_DIR = "data/raw_outputs"
CORPUS_PATH = "data/corpus/corpus_500.json"
SCREENING_PROMPT_PATH = "configs/prompts/screening.txt"
EXTRACTION_PROMPT_PATH = "configs/prompts/extraction.txt"
SCREENING_SCHEMA_PATH = "configs/schemas/screening_output.json"
EXTRACTION_SCHEMA_PATH = "configs/schemas/extraction_output.json"


def load_corpus() -> tuple[list[dict], list[dict]]:
    """Load corpus and split into all/included-only."""
    with open(CORPUS_PATH) as f:
        data = json.load(f)

    all_articles = data["corpus"]
    included = [a for a in all_articles if a["gold_category"] == "include"]

    print(f"Corpus loaded: {len(all_articles)} total, {len(included)} included")
    return all_articles, included


def load_prompt(path: str) -> str:
    """Load prompt template."""
    with open(path) as f:
        return f.read()


def load_schema(path: str) -> dict:
    """Load JSON schema."""
    with open(path) as f:
        return json.load(f)


def get_model_info(model_config: dict) -> dict:
    """Get model info for provenance."""
    provider = model_config["provider"]
    if provider == "ollama":
        from src.models.ollama_runner import get_model_info
        return get_model_info(model_config["model"])
    elif provider == "anthropic":
        from src.models.claude_runner import get_model_info
        return get_model_info(model_config["model"])
    elif provider == "google":
        from src.models.gemini_runner import get_model_info
        return get_model_info(model_config["model"])
    return {}


def progress_bar(current: int, total: int, model: str = "", stage: str = ""):
    """Simple progress indicator."""
    pct = current / total * 100
    bar = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
    print(f"\r  [{bar}] {current}/{total} ({pct:.0f}%) ", end="", flush=True)


def run_single_experiment(
    model_id: str,
    run_id: int,
    stage: str,
    corpus: list[dict],
    included: list[dict],
    screening_prompt: str,
    extraction_prompt: str,
    screening_schema: dict,
    extraction_schema: dict,
) -> dict:
    """Run a single experiment (one model, one run, one stage)."""
    config = MODEL_CONFIGS[model_id]
    model_info = get_model_info(config)

    print(f"\n{'─' * 60}")
    print(f"  Model: {model_id} | Run: {run_id} | Stage: {stage}")
    print(f"{'─' * 60}")

    if stage == "screening":
        articles = corpus
        prompt = screening_prompt
        schema = screening_schema

        def cb(c, t):
            progress_bar(c, t, model_id, stage)

        results, records, stats = run_screening(
            corpus=articles,
            model_config=config,
            run_id=run_id,
            prompt_template=prompt,
            schema=schema,
            progress_callback=cb,
        )
    elif stage == "extraction":
        articles = included
        prompt = extraction_prompt
        schema = extraction_schema

        def cb(c, t):
            progress_bar(c, t, model_id, stage)

        results, records, stats = run_extraction(
            articles=articles,
            model_config=config,
            run_id=run_id,
            prompt_template=prompt,
            schema=schema,
            progress_callback=cb,
        )
    else:
        raise ValueError(f"Unknown stage: {stage}")

    print()  # newline after progress bar

    # Create run card
    run_card = create_run_card(
        run_id=run_id,
        model_id=model_id,
        provider=config["provider"],
        stage=stage,
        total_calls=stats["total"],
        successful_calls=stats["successful"],
        failed_calls=stats["failed"],
        call_records=records,
        model_info=model_info,
        config=config,
        start_time=stats["start_time"],
        end_time=stats["end_time"],
    )

    # Save outputs
    output_path = save_run_outputs(
        output_dir=OUTPUT_DIR,
        run_id=run_id,
        model_id=model_id,
        stage=stage,
        results=results,
        call_records=records,
        run_card=run_card,
    )

    print(f"  Results: {stats['successful']}/{stats['total']} successful, "
          f"{stats['valid']} valid")
    print(f"  Saved to: {output_path}")

    return stats


def run_full_experiment(
    models: list[str],
    runs: list[int],
    stages: list[str],
    dry_run: bool = False,
):
    """Run the full experiment for specified models, runs, and stages."""
    corpus, included = load_corpus()

    # Limit corpus for dry-run validation
    if dry_run:
        corpus = corpus[:5]
        included = [a for a in included if a["corpus_id"] in {c["corpus_id"] for c in corpus}]
        if not included:
            included = corpus[:2]  # fallback
        print(f"DRY RUN: limited to {len(corpus)} screening + {len(included)} extraction")
    screening_prompt = load_prompt(SCREENING_PROMPT_PATH)
    extraction_prompt = load_prompt(EXTRACTION_PROMPT_PATH)
    screening_schema = load_schema(SCREENING_SCHEMA_PATH)
    extraction_schema = load_schema(EXTRACTION_SCHEMA_PATH)

    total_experiments = len(models) * len(runs) * len(stages)
    total_calls = sum(
        len(corpus) if s == "screening" else len(included)
        for _ in models
        for _ in runs
        for s in stages
    )

    print(f"\n{'═' * 60}")
    print(f"  PM2.5 Evidence Synthesis — Reproducibility Experiment")
    print(f"{'═' * 60}")
    print(f"  Models: {', '.join(models)}")
    print(f"  Runs: {runs[0]}-{runs[-1]} ({len(runs)} runs)")
    print(f"  Stages: {', '.join(stages)}")
    print(f"  Total experiments: {total_experiments}")
    print(f"  Total LLM calls: {total_calls:,}")
    print(f"  Started: {datetime.now(timezone.utc).isoformat()}")
    print(f"{'═' * 60}")

    all_stats = []
    experiment_num = 0
    t0 = time.time()

    for model_id in models:
        for stage in stages:
            for run_id in runs:
                experiment_num += 1
                print(f"\n[{experiment_num}/{total_experiments}]", end="")

                try:
                    stats = run_single_experiment(
                        model_id=model_id,
                        run_id=run_id,
                        stage=stage,
                        corpus=corpus,
                        included=included,
                        screening_prompt=screening_prompt,
                        extraction_prompt=extraction_prompt,
                        screening_schema=screening_schema,
                        extraction_schema=extraction_schema,
                    )
                    all_stats.append(stats)
                except Exception as e:
                    print(f"\n  ERROR: {e}")
                    all_stats.append({
                        "run_id": run_id,
                        "model_id": model_id,
                        "stage": stage,
                        "error": str(e),
                    })

    elapsed = time.time() - t0

    # Save experiment summary
    summary = {
        "experiment": "pm25-respiratory-reproducibility",
        "completed": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(elapsed, 1),
        "models": models,
        "runs": list(runs),
        "stages": stages,
        "stats": all_stats,
    }

    summary_path = Path(OUTPUT_DIR) / "experiment_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'═' * 60}")
    print(f"  EXPERIMENT COMPLETE")
    print(f"  Elapsed: {elapsed / 60:.1f} minutes")
    print(f"  Summary: {summary_path}")
    print(f"{'═' * 60}")

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="PM2.5 Evidence Synthesis Reproducibility Experiment"
    )
    parser.add_argument(
        "--model", "-m",
        choices=list(MODEL_CONFIGS.keys()),
        help="Run for a specific model only",
    )
    parser.add_argument(
        "--runs", "-r",
        default="1-30",
        help="Run range (e.g., '1-30', '1-5', '10')",
    )
    parser.add_argument(
        "--stage", "-s",
        choices=["screening", "extraction"],
        help="Run a specific stage only",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run: 1 abstract, 1 run, 1 model",
    )
    args = parser.parse_args()

    # Parse models
    if args.model:
        models = [args.model]
    else:
        models = list(MODEL_CONFIGS.keys())

    # Parse runs
    if args.dry_run:
        runs = [1]
    elif "-" in args.runs:
        start, end = args.runs.split("-")
        runs = list(range(int(start), int(end) + 1))
    else:
        runs = [int(args.runs)]

    # Parse stages
    if args.stage:
        stages = [args.stage]
    else:
        stages = ["screening", "extraction"]

    # For dry run, use a mini corpus
    if args.dry_run:
        models = [models[0]]
        print("=== DRY RUN MODE ===")
        print("Using 5 abstracts, 1 run, 1 model for validation")

    run_full_experiment(models, runs, stages, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
