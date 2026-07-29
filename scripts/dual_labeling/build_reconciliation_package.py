"""Build the v1.2 recalibration package from the Stage-A discordances.

Emits, for each labeler, a blinded CSV containing ONLY the discordant abstracts
with empty ``*_v12`` decision columns. Neither file reveals the other labeler's
original decision — the recalibration round must stay independent, exactly like
the first round. The pre-specified kappa is already computed and archived, so
nothing about this round can retroactively change it.

Also emits a coordinator-only audit sheet showing both sides plus the criterion
each labeler invoked, for the tie-break step that follows consensus.

Usage:
    python scripts/dual_labeling/build_reconciliation_package.py \
        --discordances data/dual_labeling/results/discordances.csv \
        --labeler1 data/dual_labeling/returned/subset_100_labeler1_RETURNED.csv \
        --labeler2 data/dual_labeling/returned/subset_100_labeler2_RETURNED.csv \
        --out data/dual_labeling/reconciliation/
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from _ci_heuristic import has_numeric_ci

META_COLS = ["labeling_id", "pmid", "doi", "year", "journal", "title", "abstract", "url"]
V12_SUFFIXES = ["decision_v12", "confidence_v12", "rationale_v12", "criteria_failed_v12"]


def build_blinded(source: pd.DataFrame, ids: list[str], prefix: str) -> pd.DataFrame:
    """One labeler's blinded re-rating sheet: metadata + empty v1.2 columns."""
    df = source[source["labeling_id"].isin(ids)][META_COLS].copy()
    df = df.set_index("labeling_id").loc[ids].reset_index()
    for suffix in V12_SUFFIXES:
        df[f"{prefix}_{suffix}"] = ""
    return df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--discordances", required=True, type=Path)
    ap.add_argument("--labeler1", required=True, type=Path)
    ap.add_argument("--labeler2", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    disc = pd.read_csv(args.discordances)
    l1 = pd.read_csv(args.labeler1)
    l2 = pd.read_csv(args.labeler2)
    ids = disc["labeling_id"].tolist()

    args.out.mkdir(parents=True, exist_ok=True)

    for src, prefix, path in [
        (l1, "labeler1", args.out / "recalibration_labeler1.csv"),
        (l2, "labeler2", args.out / "recalibration_labeler2.csv"),
    ]:
        build_blinded(src, ids, prefix).to_csv(path, index=False)
        print(f"blinded sheet: {path}  ({len(ids)} rows)")

    # Coordinator audit sheet — both sides visible, used only after the blinded
    # round, for consensus and tie-break.
    audit = disc.merge(
        l1[["labeling_id", "title", "abstract", "labeler1_criteria_failed"]],
        on="labeling_id", how="left",
    ).merge(
        l2[["labeling_id", "labeler2_criteria_failed"]],
        on="labeling_id", how="left",
    )
    # Decision support for the criterion-5 cases, coordinator-only: it must not
    # reach the blinded sheets, or it would anchor the independent re-rating.
    audit["heuristic_numeric_ci"] = audit["abstract"].map(has_numeric_ci)
    audit["consensus_decision"] = ""
    audit["tiebreak_decision"] = ""
    audit["tiebreak_criterion"] = ""
    audit["tiebreak_rationale"] = ""
    audit_path = args.out / "coordinator_audit_sheet.csv"
    audit.to_csv(audit_path, index=False)
    print(f"coordinator audit: {audit_path}  ({len(audit)} rows)")

    pattern = disc.groupby(["labeler1_decision", "labeler2_decision"]).size()
    print("\ndiscordance pattern:")
    print(pattern.to_string())


if __name__ == "__main__":
    main()
