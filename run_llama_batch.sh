#!/bin/bash
# Run all 30 LLaMA 3 8B experiments (screening + extraction)
# Local Ollama — no API credits needed.
# Usage: ./run_llama_batch.sh [start_run] [end_run]
#   e.g. ./run_llama_batch.sh 2 30   (skip run 1 if already done)

START=${1:-1}
END=${2:-30}
MODEL="llama3-8b"

echo "════════════════════════════════════════════"
echo "  LLaMA 3 8B Batch — Runs ${START}-${END}"
echo "  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "════════════════════════════════════════════"

for RUN in $(seq $START $END); do
    echo ""
    echo "▶ Run ${RUN}/${END} — screening"
    PYTHONUNBUFFERED=1 .venv/bin/python run_experiment.py \
        --model $MODEL --runs $RUN --stage screening

    echo ""
    echo "▶ Run ${RUN}/${END} — extraction"
    PYTHONUNBUFFERED=1 .venv/bin/python run_experiment.py \
        --model $MODEL --runs $RUN --stage extraction

    echo ""
    echo "✓ Run ${RUN} complete at $(date -u +%H:%M:%S)"
done

echo ""
echo "════════════════════════════════════════════"
echo "  ALL ${END} RUNS COMPLETE"
echo "  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "════════════════════════════════════════════"
