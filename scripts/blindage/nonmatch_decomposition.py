"""Split each stack's EMR non-matches into failed-call items and genuine changes.

EMR counts a failed call as a non-match (its error output differs from the
decisions or outputs of the other runs). This script separates, per stack and
stage, the non-matching items that involve at least one failed call from those
where every run returned an output and the outputs still differ.

Output: analysis/blindage/nonmatch_decomposition.json
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from arms import JEV, MODELS  # noqa: E402

RAW = ROOT / "data" / "raw_outputs"
OUT = ROOT / "analysis" / "blindage" / "nonmatch_decomposition.json"


def failed(item: dict) -> bool:
    out = item.get("output")
    return out is None or (isinstance(out, dict) and "error" in out)


def value(item: dict, stage: str):
    if failed(item):
        return "ERROR"
    return item["output"].get("decision") if stage == "screening" else item.get("output_hash")


def decompose(stack: str, stage: str) -> dict | None:
    runs = sorted((RAW / stack / stage).glob("run_*/results.json"))
    if not runs:
        return None
    vals, fails = defaultdict(list), defaultdict(int)
    for path in runs:
        for item in json.loads(path.read_text()):
            vals[item["corpus_id"]].append(value(item, stage))
            fails[item["corpus_id"]] += failed(item)
    full = {c: v for c, v in vals.items() if len(v) == len(runs)}
    nonmatch = [c for c, v in full.items() if len(set(v)) > 1]
    with_fail = [c for c in nonmatch if fails[c] > 0]
    return {
        "n_runs": len(runs),
        "n_items": len(full),
        "n_nonmatch": len(nonmatch),
        "n_nonmatch_with_failed_call": len(with_fail),
        "n_nonmatch_all_runs_returned": len(nonmatch) - len(with_fail),
        "items_with_failed_call": sorted(with_fail),
    }


def main() -> None:
    payload = {"definition": __doc__.strip().splitlines()[0], "stacks": {}}
    for stack in MODELS + [JEV]:
        payload["stacks"][stack] = {st: decompose(stack, st) for st in ("screening", "extraction")}
    body = json.dumps(payload, indent=2, sort_keys=True).encode()
    payload["sha256_self"] = hashlib.sha256(body).hexdigest()
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True))
    for s, v in payload["stacks"].items():
        for st, d in v.items():
            if d:
                print(f"{s:22s} {st:10s} nonmatch {d['n_nonmatch']:3d}  with failed call {d['n_nonmatch_with_failed_call']:3d}  all returned {d['n_nonmatch_all_runs_returned']:3d}")


if __name__ == "__main__":
    main()
