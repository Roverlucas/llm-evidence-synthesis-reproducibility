#!/usr/bin/env bash
# Assembles the files uploaded to Editorial Manager (Environmental Modelling & Software)
# into article/submission_envsoft/. Run from anywhere; requires TinyTeX (elsarticle) and pandoc.
#
#   bash article/build_submission.sh
#
# The package is refused while any \pending placeholder remains (scripts/check_pending.sh).
set -euo pipefail
cd "$(dirname "$0")"

TEX=$(ls -d ~/Library/TinyTeX/bin/*/ 2>/dev/null | head -1)
[[ -n "$TEX" ]] && export PATH="$TEX:$PATH"

bash ../scripts/check_pending.sh

./sync_figures.sh

pdflatex -interaction=nonstopmode main.tex >/dev/null
bibtex main >/dev/null
pdflatex -interaction=nonstopmode main.tex >/dev/null
pdflatex -interaction=nonstopmode main.tex >/dev/null
pdflatex -interaction=nonstopmode supplementary.tex >/dev/null
pdflatex -interaction=nonstopmode supplementary.tex >/dev/null

OUT=submission_envsoft
rm -rf -- "./$OUT"
mkdir -p "$OUT"
cp main.tex references.bib main.bbl main.pdf "$OUT/"
# Editorial Manager may flatten folders, so figures go next to main.tex (\graphicspath also finds them there).
cp figures/Figure_1.pdf figures/Figure_2.pdf figures/Figure_3.pdf "$OUT/"
cp highlights.txt "$OUT/highlights.txt"
# Graphical abstract left out until the authors approve it (article/graphical_abstract.*).
cp supplementary.pdf "$OUT/Supplementary_material.pdf"
pandoc ../docs/cover_letter_envsoft.md -o "$OUT/cover_letter.docx"

echo "Package written to article/$OUT:"
ls -1R "$OUT"
