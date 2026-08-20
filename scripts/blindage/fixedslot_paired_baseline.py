"""Recompute the fixed-slot comparison against a run-count-matched baseline.

The fixed-slot condition was executed with 3 runs; the variable-length baseline it
was compared against has 10. EMR is monotonically non-increasing in the number of
runs — every additional run is another chance for an item to disagree — so putting
a 3-run EMR next to a 10-run EMR credits the fixed-slot prompt with an improvement
that is partly an artefact of having been measured over fewer repetitions.

This script computes the baseline over every 3-run subset of the 10 available runs
(C(10,3) = 120 triples) and averages, giving a baseline at the same run count as the
condition it is compared with. It also reports how many articles each arm actually
covers, since the fixed-slot arm does not cover all 100 in every stack.

Usage:
    python scripts/blindage/fixedslot_paired_baseline.py \
        --out analysis/blindage/fixedslot_paired.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path

RAW = Path("data/raw_outputs")
STACKS = {
    "claude-sonnet-4-5": "claude-sonnet-4-5-fixedslot",
    "gemini-2.5-pro": "gemini-2.5-pro-fixedslot",
    "gpt-4.1": "gpt-4.1-fixedslot",
}


def load_runs(stack_dir: Path) -> dict[int, dict[str, str]]:
    """Map run_id -> {corpus_id: output_hash} for the extraction stage."""
    runs: dict[int, dict[str, str]] = {}
    for run_path in sorted((stack_dir / "extraction").glob("run_*")):
        results = run_path / "results.json"
        if not results.exists():
            continue
        run_id = int(run_path.name.split("_")[1])
        runs[run_id] = {
            r["corpus_id"]: r.get("output_hash")
            for r in json.load(open(results))
            if r.get("output_hash")
        }
    return runs


def emr(runs: dict[int, dict[str, str]], run_ids: tuple[int, ...]) -> tuple[float, int]:
    """Exact Match Rate over the given runs: share of items identical across all of them.

    Restricted to items present in every selected run, so the denominator is the set
    of articles the comparison can actually speak to.
    """
    selected = [runs[r] for r in run_ids]
    shared = set(selected[0])
    for s in selected[1:]:
        shared &= set(s)
    if not shared:
        return float("nan"), 0
    matches = sum(1 for cid in shared if len({s[cid] for s in selected}) == 1)
    return matches / len(shared), len(shared)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    payload: dict[str, dict] = {
        "method": (
            "Baseline EMR averaged over all C(10,3)=120 three-run subsets of the "
            "variable-length condition, matching the 3-run fixed-slot condition. "
            "EMR is monotonically non-increasing in run count, so the 10-run "
            "baseline previously used is not comparable to a 3-run condition."
        ),
        "stacks": {},
    }

    for stack, fixed_dir in STACKS.items():
        base_runs = load_runs(RAW / stack)
        fixed_runs = load_runs(RAW / fixed_dir)
        if len(base_runs) < 3 or not fixed_runs:
            continue

        fixed_ids = tuple(sorted(fixed_runs))
        fixed_emr, fixed_n = emr(fixed_runs, fixed_ids)

        base_full, base_full_n = emr(base_runs, tuple(sorted(base_runs)))

        triples = list(combinations(sorted(base_runs), 3))
        vals = [emr(base_runs, t) for t in triples]
        paired = [v for v, _ in vals if v == v]
        base_paired = sum(paired) / len(paired)

        def pct(new: float, old: float) -> float | None:
            return None if old == 0 else round(100.0 * (new - old) / old, 1)

        payload["stacks"][stack] = {
            "fixed_slot_emr": round(fixed_emr, 4),
            "fixed_slot_n_runs": len(fixed_runs),
            "fixed_slot_n_articles": fixed_n,
            "baseline_emr_10run": round(base_full, 4),
            "baseline_n_articles_10run": base_full_n,
            "baseline_emr_3run_paired": round(base_paired, 4),
            "baseline_n_triples": len(triples),
            "relative_change_vs_10run_baseline_pct": pct(fixed_emr, base_full),
            "relative_change_vs_paired_baseline_pct": pct(fixed_emr, base_paired),
        }

    body = json.dumps(payload, indent=2, sort_keys=True).encode()
    payload["sha256_self"] = hashlib.sha256(body).hexdigest()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True))

    print(f"{'stack':22s} {'fixed':>7s} {'base10':>8s} {'base3':>7s} "
          f"{'vs10':>8s} {'vs3':>8s}   n_art(fixed)")
    for s, v in payload["stacks"].items():
        print(f"{s:22s} {v['fixed_slot_emr']:7.3f} {v['baseline_emr_10run']:8.3f} "
              f"{v['baseline_emr_3run_paired']:7.3f} "
              f"{v['relative_change_vs_10run_baseline_pct']:+7.1f}% "
              f"{v['relative_change_vs_paired_baseline_pct']:+7.1f}%   "
              f"{v['fixed_slot_n_articles']}")
    print(f"\nwritten: {args.out}")


if __name__ == "__main__":
    main()
