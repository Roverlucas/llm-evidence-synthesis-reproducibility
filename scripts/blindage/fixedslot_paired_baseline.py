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
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from arms import CLAUDE, CLAUDE_FIXEDSLOT, CLAUDE_T1, CLAUDE_T1_FIXEDSLOT  # noqa: E402  (headline Claude arm, decision 41)

RAW = Path("data/raw_outputs")
STACKS = {
    CLAUDE: CLAUDE_FIXEDSLOT,
    "gemini-2.5-pro": "gemini-2.5-pro-fixedslot",
    "gpt-4.1": "gpt-4.1-fixedslot",
    # Temperature-1.0 Claude pair, reported in the supplement as a contrast (decision 41).
    CLAUDE_T1: CLAUDE_T1_FIXEDSLOT,
}


def parsed_hash(output) -> str:
    """Hash of the parsed output re-serialised with sorted keys.

    This is how the fixed-slot script defines output identity; applying it to the
    baseline gives an identity-matched comparison (the stored baseline hash is of
    the raw response text, which also differs on whitespace and key order).
    """
    return hashlib.sha256(json.dumps(output, sort_keys=True, ensure_ascii=True).encode()).hexdigest()


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    """Wilson 95% interval for a proportion k/n."""
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return c - h, c + h


def load_runs(stack_dir: Path, identity: str = "stored") -> dict[int, dict[str, str]]:
    """Map run_id -> {corpus_id: output identity} for the extraction stage."""
    runs: dict[int, dict[str, str]] = {}
    for run_path in sorted((stack_dir / "extraction").glob("run_*")):
        results = run_path / "results.json"
        if not results.exists():
            continue
        run_id = int(run_path.name.split("_")[1])
        runs[run_id] = {
            r["corpus_id"]: (parsed_hash(r.get("output")) if identity == "parsed" else r.get("output_hash"))
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

        parsed_runs = load_runs(RAW / stack, identity="parsed")
        vals_p = [emr(parsed_runs, t) for t in triples]
        paired_p = [v for v, _ in vals_p if v == v]
        base_paired_parsed = sum(paired_p) / len(paired_p)

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
            "baseline_emr_3run_paired_parsed_identity": round(base_paired_parsed, 4),
            "fixed_slot_emr_wilson95": [round(x, 4) for x in wilson(round(fixed_emr * fixed_n), fixed_n)],
            "relative_change_vs_paired_parsed_identity_pct": pct(fixed_emr, base_paired_parsed),
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
