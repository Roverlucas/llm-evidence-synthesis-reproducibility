#!/usr/bin/env bash
# Build Zenodo upload tarball.
# Run from project root: bash docs/zenodo/build_tarball.sh
set -euo pipefail

VERSION="${VERSION:-v1.0}"
OUT_DIR="dist"
TARBALL="${OUT_DIR}/llm-evidence-synthesis-reproducibility-${VERSION}.tar.gz"

mkdir -p "$OUT_DIR"

echo "Building tarball: ${TARBALL}"
echo "Version: ${VERSION}"
echo

# Files/directories to INCLUDE in the deposit
INCLUDES=(
    "data/corpus/corpus_500.json"
    "data/gold_standard/"
    "data/dual_labeling/"
    "data/raw_outputs/"
    "configs/"
    "src/"
    "scripts/"
    "tests/"
    "analysis/blindage/"
    "analysis/reproducibility_results.json"
    "analysis/semantic_and_meta_results.json"
    "analysis/bertscore_results.json"
    "analysis/timing_and_costs.json"
    "analysis/figures/"
    "analysis/tables/"
    "analysis/bootstrap/"
    "article/main.tex"
    "article/supplementary.tex"
    "article/references.bib"
    "article/CUP-JNL-DTM.cls"
    "requirements.txt"
    "requirements-lock.txt"
    "README.md"
    "LICENSE"
    "PROJECT_LOG.md"
    "docs/zenodo/zenodo_metadata.json"
    "docs/zenodo/upload_instructions.md"
    ".env.example"
    ".gitignore"
)

# EXCLUDE patterns (large files we don't want in the deposit)
EXCLUDE_PATTERNS=(
    --exclude='*.aux'
    --exclude='*.bbl'
    --exclude='*.bcf'
    --exclude='*.blg'
    --exclude='*.log'
    --exclude='*.out'
    --exclude='*.run.xml'
    --exclude='*.toc'
    --exclude='__pycache__'
    --exclude='*.pyc'
    --exclude='.pytest_cache'
    --exclude='.venv'
    --exclude='*.pdf'
    --exclude='monitor.log'
    --exclude='analysis_run.log'
    --exclude='gpt41_rerun.log'
    --exclude='run_sequential.log'
)

# Check that all includes exist
echo "Checking files exist..."
MISSING=0
for path in "${INCLUDES[@]}"; do
    if [ ! -e "$path" ]; then
        echo "  MISSING: $path"
        MISSING=1
    else
        size=$(du -sh "$path" 2>/dev/null | cut -f1)
        echo "  OK ($size): $path"
    fi
done

if [ "$MISSING" -ne 0 ]; then
    echo
    echo "WARNING: some paths missing. Continue anyway? (y/N)"
    read -r reply
    [ "$reply" != "y" ] && exit 1
fi

echo
echo "Building tarball..."
tar -czf "$TARBALL" "${EXCLUDE_PATTERNS[@]}" "${INCLUDES[@]}"

SIZE=$(du -sh "$TARBALL" | cut -f1)
echo
echo "✓ Tarball ready: $TARBALL ($SIZE)"
echo
echo "Next steps:"
echo "  1. Inspect: tar -tzf $TARBALL | head -30"
echo "  2. Upload to Zenodo: see docs/zenodo/upload_instructions.md"
