#!/bin/zsh
# Decision 41 addendum: screening run 6 aborted on 2026-10-08 after a local DNS outage
# (433/500 valid, 57 abstracts never sent). The partial run is archived, not deleted,
# and run 6 is executed again in full.
set -a; source ~/.env; set +a
cd "$(dirname "$0")/.."
SRC=data/raw_outputs/claude-sonnet-4-5-t0/screening/run_006
DST=data/aborted_runs/claude-sonnet-4-5-t0/screening/run_006_aborted_2026-10-08
mkdir -p "$(dirname $DST)"
[ -d "$SRC" ] && mv "$SRC" "$DST"
echo "== start $(date -u +%FT%TZ)"
.venv/bin/python run_experiment.py --model claude-sonnet-4-5-t0 --stage screening --runs 6
echo "== end $(date -u +%FT%TZ)"
