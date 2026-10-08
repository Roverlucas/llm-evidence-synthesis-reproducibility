#!/bin/zsh
# Decision 41: Claude arm re-run at temperature 0 (sequential, synchronous API).
set -a; source ~/.env; set +a
cd "$(dirname "$0")/.."
PY=.venv/bin/python
echo "== start $(date -u +%FT%TZ)"
$PY run_experiment.py --model claude-sonnet-4-5-t0 --stage extraction --runs 1-10
$PY scripts/blindage/run_fixed_slot_extraction.py --model claude-sonnet-4-5-t0-fixedslot --runs 1-3
$PY run_experiment.py --model claude-sonnet-4-5-t0 --stage screening --runs 1-10
echo "== end $(date -u +%FT%TZ)"
