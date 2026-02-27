#!/bin/bash
# Sequential experiment runner: Mistral extraction → Gemma full
# Updated: 2026-02-27 (increased timeout to 600s, restart after hang fix)
set -e

cd /Users/lucasrover/llm-evidence-synthesis-reproducibility
source .venv/bin/activate

LOGFILE="run_sequential.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOGFILE"
}

log "=== Sequential Runner v2 Started ==="

# Phase 1: Mistral extraction (screening already done 10/10)
log "=== Phase 1: Mistral 7B (extraction only, screening 10/10 done) ==="
log "Running: python run_experiment.py --model mistral-7b --runs 1-10"

python run_experiment.py --model mistral-7b --runs 1-10 2>&1 | tee -a "$LOGFILE"

log "=== Mistral 7B Complete ==="

# Unload Mistral from VRAM before launching Gemma
log "Unloading Mistral from VRAM..."
curl -s http://localhost:11434/api/generate -d '{"model":"mistral:7b","keep_alive":0}' > /dev/null 2>&1
sleep 10

# Phase 2: Gemma full (screening 2/10 + extraction 0/10)
log "=== Phase 2: Gemma 2 9B (full) ==="
log "Running: python run_experiment.py --model gemma2-9b --runs 1-10"

python run_experiment.py --model gemma2-9b --runs 1-10 2>&1 | tee -a "$LOGFILE"

log "=== Gemma 2 9B Complete ==="

# Push all results
log "Pushing to GitHub..."
git push 2>&1 | tee -a "$LOGFILE" || log "Git push failed (no internet?)"

log "=== ALL EXPERIMENTS DONE! ==="
