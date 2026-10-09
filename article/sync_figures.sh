#!/usr/bin/env bash
# Copies the figures produced by the analysis into article/figures/ under the
# Figure_<n> names the journal asks for, in order of appearance in main.tex.
set -euo pipefail
cd "$(dirname "$0")"
src=../analysis/figures
cp "$src/pipeline_diagram.pdf"  figures/Figure_1.pdf
cp "$src/emr_comparison.pdf"    figures/Figure_2.pdf
cp "$src/field_emr_heatmap.pdf" figures/Figure_3.pdf
