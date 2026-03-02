#!/bin/bash
# Optimized Gemma runner — flash attention + num_batch 2048
# Night mode: max GPU/memory utilization
set -e
cd /Users/lucasrover/llm-evidence-synthesis-reproducibility
source .venv/bin/activate

LOGFILE="run_sequential.log"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOGFILE"; }

log "=== Gemma 2 9B Optimized Runner Started ==="
log "  Flash Attention: ON"
log "  num_batch: 2048"
log "  num_gpu: 99 (all layers)"

python run_experiment.py --model gemma2-9b --runs 1-10 2>&1 | tee -a "$LOGFILE"

log "=== Gemma 2 9B Complete ==="

# Final push
git push 2>&1 | tee -a "$LOGFILE" || log "Git push failed"
log "=== ALL EXPERIMENTS DONE! ==="
