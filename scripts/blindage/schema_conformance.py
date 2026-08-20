"""Measure schema conformance per deployment stack and stage.

EMR asks whether repeated runs agree with each other. It says nothing about whether
what they agree on is usable. A stack can reproduce an unusable output perfectly:
the local stacks reach EMR = 1.000 on extraction while returning output that fails
the study's own JSON schema in roughly three of every five calls.

Conformance is therefore a second, orthogonal axis of reliability, and one that a
review team feels directly — a non-conforming record is one a human has to repair
by hand regardless of how reproducible it was.

The failure modes matter as much as the rates and are reported alongside. They are
not truncation: they are enum values the model rendered in its own orthography
("case-crossover" for "case_crossover"), two values returned where the schema
allows one, and nulls in fields typed as number or string.

Usage:
    python scripts/blindage/schema_conformance.py --out analysis/blindage/schema_conformance.json
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
from collections import Counter
from pathlib import Path

STACKS = [
    "llama3-8b", "mistral-7b", "gemma2-9b",
    "claude-sonnet-4-5", "gemini-2.5-pro", "gpt-4.1",
]
STAGES = ["screening", "extraction"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    payload: dict[str, dict] = {
        "definition": (
            "conformance = share of returned outputs that validate against the "
            "stage JSON schema, over all runs. Calls that returned no output at "
            "all are counted separately as 'no_output' and excluded from the "
            "conformance denominator."
        ),
        "stacks": {},
    }

    for stack in STACKS:
        entry: dict[str, dict] = {}
        for stage in STAGES:
            files = sorted(glob.glob(f"data/raw_outputs/{stack}/{stage}/run_*/results.json"))
            if not files:
                continue
            total = valid = no_output = 0
            errors: Counter = Counter()
            for f in files:
                for r in json.load(open(f)):
                    total += 1
                    out = r.get("output")
                    if out is None:
                        no_output += 1
                        continue
                    if r.get("valid"):
                        valid += 1
                    else:
                        err = str(out.get("_validation_error", "")).strip()
                        if err:
                            errors[err[:120]] += 1
            denom = total - no_output
            entry[stage] = {
                "calls": total,
                "no_output": no_output,
                "conforming": valid,
                "conformance": round(valid / denom, 4) if denom else None,
                "top_failure_modes": [
                    {"error": e, "n": n} for e, n in errors.most_common(3)
                ],
            }
        payload["stacks"][stack] = entry

    body = json.dumps(payload, indent=2, sort_keys=True).encode()
    payload["sha256_self"] = hashlib.sha256(body).hexdigest()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True))

    print(f"{'stack':22s} {'screening':>10s} {'extraction':>11s}")
    for s, v in payload["stacks"].items():
        sc = v.get("screening", {}).get("conformance")
        ex = v.get("extraction", {}).get("conformance")
        print(f"{s:22s} {sc if sc is None else f'{100*sc:9.1f}%'} "
              f"{ex if ex is None else f'{100*ex:10.1f}%'}")
    print(f"\nwritten: {args.out}")


if __name__ == "__main__":
    main()
