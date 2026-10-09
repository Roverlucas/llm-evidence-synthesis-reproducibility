"""Run-to-run spread of Jev's option probabilities on screening (decision 42).

EMR, accuracy, sensitivity and specificity for Jev come from run_analysis.py
(analysis/supplementary_arms_results.json). This script adds the one metric that
exists only for a decision model: how much the probability Jev assigns to each
option moves between identical calls. No calibration claim is made from it.

Output: analysis/blindage/jev_screening.json
"""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from arms import JEV  # noqa: E402

RAW = ROOT / "data" / "raw_outputs" / JEV / "screening"
OUT = ROOT / "analysis" / "blindage" / "jev_screening.json"
OPTIONS = ["include", "exclude", "uncertain"]


def main() -> None:
    probs = defaultdict(lambda: defaultdict(list))   # cid -> option -> [p per run]
    choices = defaultdict(list)                      # cid -> [choice per run]
    n_calls = n_failed = 0
    for run_dir in sorted(RAW.glob("run_*")):
        for r in json.loads((run_dir / "results.json").read_text()):
            n_calls += 1
            if not r.get("valid"):
                n_failed += 1
                continue
            out = r["output"]
            choices[r["corpus_id"]].append(out["decision"])
            for opt in OPTIONS:
                probs[r["corpus_id"]][opt].append(out["probabilities"][opt])

    # Spread of each option's probability across runs, per abstract.
    ranges = {opt: [] for opt in OPTIONS}
    sds = {opt: [] for opt in OPTIONS}
    for cid in probs:
        for opt in OPTIONS:
            vals = probs[cid][opt]
            ranges[opt].append(max(vals) - min(vals))
            sds[opt].append(statistics.pstdev(vals))

    # Probability of the modal choice, and how often it sits below 0.5.
    modal_p = []
    for cid, cs in choices.items():
        modal = Counter(cs).most_common(1)[0][0]
        modal_p.append(statistics.mean(probs[cid][modal]))

    flipped = [cid for cid, cs in choices.items() if len(set(cs)) > 1]
    flip_range = [max(probs[c][o]) - min(probs[c][o]) for c in flipped for o in OPTIONS]

    payload = {
        "n_calls": n_calls,
        "n_failed_calls": n_failed,
        "n_abstracts": len(choices),
        "decision_counts": dict(Counter(c for cs in choices.values() for c in cs)),
        "probability_range_across_runs": {
            opt: {"mean": round(statistics.mean(ranges[opt]), 4),
                  "median": round(statistics.median(ranges[opt]), 4),
                  "max": round(max(ranges[opt]), 4),
                  "share_zero": round(sum(v == 0 for v in ranges[opt]) / len(ranges[opt]), 4)}
            for opt in OPTIONS
        },
        "probability_sd_across_runs_mean": {opt: round(statistics.mean(sds[opt]), 4) for opt in OPTIONS},
        "modal_choice_probability": {
            "mean": round(statistics.mean(modal_p), 4),
            "share_below_0.5": round(sum(p < 0.5 for p in modal_p) / len(modal_p), 4),
        },
        "flipping_abstracts": {
            "n": len(flipped),
            "max_probability_range": round(max(flip_range), 4) if flip_range else None,
        },
    }
    body = json.dumps(payload, indent=2, sort_keys=True).encode()
    payload["sha256_self"] = hashlib.sha256(body).hexdigest()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
