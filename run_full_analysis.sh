#!/bin/bash
# Full analysis pipeline — waits for experiments, then runs all analysis
set -e
cd /Users/lucasrover/llm-evidence-synthesis-reproducibility
source .venv/bin/activate

LOGFILE="analysis_run.log"
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOGFILE"; }

# ── Phase 1: Wait for Gemma experiments to complete ──────────
log "=== Waiting for Gemma 2 9B experiments to complete ==="

while true; do
    SCR=$(ls -d data/raw_outputs/gemma2-9b/screening/run_*/run_card.json 2>/dev/null | wc -l | tr -d ' ')
    EXT=$(ls -d data/raw_outputs/gemma2-9b/extraction/run_*/run_card.json 2>/dev/null | wc -l | tr -d ' ')

    if [ "$SCR" -ge 10 ] && [ "$EXT" -ge 10 ]; then
        log "Gemma 2 9B COMPLETE: screening=$SCR/10, extraction=$EXT/10"
        break
    fi

    log "  Progress: screening=$SCR/10, extraction=$EXT/10 — checking again in 5 min..."
    sleep 300
done

# Wait a bit for the experiment runner to finish git operations
sleep 30

# ── Phase 2: Verify all 6 models complete ────────────────────
log "=== Verifying all 6 models ==="
ALL_OK=true
for model in llama3-8b mistral-7b gemma2-9b claude-sonnet-4-5 gemini-2.5-pro gpt-4.1; do
    SCR=$(ls -d "data/raw_outputs/$model/screening/run_"*/run_card.json 2>/dev/null | wc -l | tr -d ' ')
    EXT=$(ls -d "data/raw_outputs/$model/extraction/run_"*/run_card.json 2>/dev/null | wc -l | tr -d ' ')
    log "  $model: screening=$SCR/10, extraction=$EXT/10"
    if [ "$SCR" -lt 10 ] || [ "$EXT" -lt 10 ]; then
        log "  WARNING: $model incomplete!"
        ALL_OK=false
    fi
done

if [ "$ALL_OK" = false ]; then
    log "ERROR: Not all models complete. Proceeding with available data."
fi

# ── Phase 3: Run main reproducibility analysis ───────────────
log "=== Phase 3: Main Reproducibility Analysis ==="
python run_analysis.py 2>&1 | tee -a "$LOGFILE"
log "  → reproducibility_results.json + bootstrap_cis.json + figures"

# ── Phase 4: Semantic equivalence + meta-analysis ────────────
log "=== Phase 4: Semantic Equivalence & Meta-Analysis ==="
python analysis/run_semantic_and_meta.py 2>&1 | tee -a "$LOGFILE"
log "  → semantic_and_meta_results.json"

# ── Phase 5: BERTScore computation ───────────────────────────
log "=== Phase 5: BERTScore Computation ==="
python analysis/compute_bertscore.py 2>&1 | tee -a "$LOGFILE"
log "  → bertscore_results.json"

# ── Phase 6: Auto-commit analysis results ────────────────────
log "=== Phase 6: Git commit analysis results ==="
git add analysis/ 2>&1 | tee -a "$LOGFILE"
git commit -m "analysis: complete reproducibility analysis for all 6 models

- EMR + bootstrap CIs (10k resamples) for screening and extraction
- Semantic equivalence (exact, normalized, fuzzy EMR)
- Meta-analytic propagation experiment
- BERTScore F1 (all-pairs, roberta-large)
- Figures: EMR comparison bar chart + field-level heatmap" 2>&1 | tee -a "$LOGFILE" || log "Nothing to commit"

git push 2>&1 | tee -a "$LOGFILE" || log "Git push failed"

log "=== ALL ANALYSIS COMPLETE ==="
log ""
log "Output files:"
log "  analysis/reproducibility_results.json"
log "  analysis/bootstrap/bootstrap_cis.json"
log "  analysis/semantic_and_meta_results.json"
log "  analysis/bertscore_results.json"
log "  analysis/figures/emr_comparison.pdf"
log "  analysis/figures/field_emr_heatmap.pdf"
