"""Rebuild the Stage-B extraction set from the human gold standard.

The original ``extraction_25_*.csv`` was drawn from the LLM silver standard before
any human labelling existed. Against the human consensus only 13 of those 25
survived, so the extraction set is rebuilt here from the gold standard instead.

Under protocol v1.2 §2.1, an INCLUDE decision already implies level 5a (numeric
point estimate plus numeric 95% CI in the abstract) — an abstract that only
mentions the effect without values resolves to UNCERTAIN, not INCLUDE. So the
extraction set is exactly the gold-standard INCLUDEs. A regex heuristic flags any
INCLUDE whose abstract shows no numeric CI, for manual review before sending;
the heuristic never removes an item on its own.

Usage:
    python scripts/dual_labeling/rebuild_extraction_set.py \
        --gold data/dual_labeling/gold_subset_100_final.json \
        --subset data/dual_labeling/exports/subset_100_labeler1.csv \
        --out data/dual_labeling/exports/
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from _ci_heuristic import has_numeric_ci

EXTRACTION_FIELDS = [
    "effect_measure", "effect_estimate", "ci_lower", "ci_upper", "lag",
    "exposure_increment", "outcome_specific", "study_design", "study_location",
    "population", "n_estimates_in_abstract", "notes",
]
META_COLS = ["labeling_id", "pmid", "doi", "year", "journal", "title", "abstract", "url"]

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True, type=Path)
    ap.add_argument("--subset", required=True, type=Path,
                    help="any subset_100_labeler*.csv — used for abstract metadata")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--legacy-set", type=Path,
                    help="previous extraction_25_*.csv, to report the overlap")
    args = ap.parse_args()

    gold = json.loads(args.gold.read_text())
    includes = [i["labeling_id"] for i in gold["items"] if i.get("decision") == "INCLUDE"]

    subset = pd.read_csv(args.subset)
    df = subset[subset["labeling_id"].isin(includes)][META_COLS].copy()
    df = df.set_index("labeling_id").loc[includes].reset_index()

    no_ci = df[~df["abstract"].map(has_numeric_ci)]["labeling_id"].tolist()

    args.out.mkdir(parents=True, exist_ok=True)
    for prefix, name in [("labeler1", "Isabelle"), ("labeler2", "Luiza")]:
        out_df = df.copy()
        for field in EXTRACTION_FIELDS:
            out_df[f"{prefix}_{field}"] = ""
        path = args.out / f"extraction_{prefix}.csv"
        out_df.to_csv(path, index=False)
        print(f"{name:9s} -> {path}  ({len(out_df)} abstracts)")

    if args.legacy_set and args.legacy_set.exists():
        legacy = set(pd.read_csv(args.legacy_set)["labeling_id"])
        kept = legacy & set(includes)
        print(f"\nlegacy silver-standard set: n={len(legacy)}")
        print(f"  survived human gold standard: {len(kept)}/{len(legacy)}")
        print(f"  dropped (LLM-only includes):  {len(legacy - set(includes))}")
        print(f"  new (human-only includes):    {len(set(includes) - legacy)}")

    if no_ci:
        print(f"\nFLAG — {len(no_ci)} INCLUDE(s) with no numeric 95% CI detected by regex.")
        print("Review manually before sending; v1.2 §2.1 says INCLUDE implies level 5a.")
        print(f"  {no_ci}")


if __name__ == "__main__":
    main()
