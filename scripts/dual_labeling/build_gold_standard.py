"""Consolidate the human gold standard for Stage A screening.

Resolution order, per abstract, with the source recorded for every single item:

    1. ``agreement_round1``  — both labelers agreed in the independent v1.1 round
    2. ``agreement_round2``  — they disagreed, then agreed in the blinded v1.2
                               recalibration round
    3. ``consensus``         — still disagreed, resolved in the consensus meeting
    4. ``tiebreak``          — no consensus, decided by the coordinator

Every item lands in exactly one bucket and the bucket is written to the output,
so a reviewer can audit how much of the gold standard rests on each mechanism.

The round-1 kappa is NOT recomputed here — it is archived in
``results/kappa_report.json`` and stands as the study's agreement estimate.

This script deliberately does NOT emit a post-recalibration kappa. Round 2 re-rates
only the items that already disagreed, so any coefficient recomputed over the full
corpus afterwards rises mechanically: at a high enough resolution rate it crosses
the Cochrane threshold by construction and carries no evidential content. What is
reported instead is the reconciliation convergence rate — how many of the initially
discordant items the two labelers now agree on — which is descriptive and conditional
on that selected subset by definition.

Usage:
    python scripts/dual_labeling/build_gold_standard.py \
        --labeler1 data/dual_labeling/returned/subset_100_labeler1_RETURNED.csv \
        --labeler2 data/dual_labeling/returned/subset_100_labeler2_RETURNED.csv \
        --recal1 data/dual_labeling/reconciliation/recalibration_labeler1.csv \
        --recal2 data/dual_labeling/reconciliation/recalibration_labeler2.csv \
        --audit data/dual_labeling/reconciliation/coordinator_audit_sheet.csv \
        --out data/dual_labeling/gold_subset_100_final.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

DECISIONS = {"INCLUDE", "EXCLUDE", "UNCERTAIN"}


def norm(value: object) -> str:
    return str(value).strip().upper() if pd.notna(value) else ""


def convergence_rate(pairs: list[tuple[str, str]]) -> float | None:
    """Share of re-rated items on which the two labelers now agree.

    Descriptive by construction: the denominator is the set of items that
    disagreed in round 1, so this is not an agreement coefficient and must never
    be presented as one.
    """
    if not pairs:
        return None
    return sum(1 for a, b in pairs if a == b) / len(pairs)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labeler1", required=True, type=Path)
    ap.add_argument("--labeler2", required=True, type=Path)
    ap.add_argument("--recal1", type=Path, help="blinded v1.2 re-rating, labeler1")
    ap.add_argument("--recal2", type=Path, help="blinded v1.2 re-rating, labeler2")
    ap.add_argument("--audit", type=Path, help="coordinator sheet with consensus/tiebreak")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--allow-unresolved", action="store_true",
                    help="write the file even if some abstracts are still unresolved")
    args = ap.parse_args()

    l1 = pd.read_csv(args.labeler1).set_index("labeling_id")
    l2 = pd.read_csv(args.labeler2).set_index("labeling_id")

    def load_recal(path: Path | None, prefix: str) -> dict[str, str]:
        if path is None or not path.exists():
            return {}
        df = pd.read_csv(path).set_index("labeling_id")
        col = f"{prefix}_decision_v12"
        if col not in df.columns:
            return {}
        return {i: norm(v) for i, v in df[col].items() if norm(v) in DECISIONS}

    r1, r2 = load_recal(args.recal1, "labeler1"), load_recal(args.recal2, "labeler2")

    audit_consensus: dict[str, str] = {}
    audit_tiebreak: dict[str, dict] = {}
    if args.audit and args.audit.exists():
        adf = pd.read_csv(args.audit).set_index("labeling_id")
        for lid, row in adf.iterrows():
            if norm(row.get("consensus_decision")) in DECISIONS:
                audit_consensus[lid] = norm(row.get("consensus_decision"))
            if norm(row.get("tiebreak_decision")) in DECISIONS:
                audit_tiebreak[lid] = {
                    "decision": norm(row.get("tiebreak_decision")),
                    "criterion": str(row.get("tiebreak_criterion", "") or "").strip(),
                    "rationale": str(row.get("tiebreak_rationale", "") or "").strip(),
                }

    gold: list[dict] = []
    unresolved: list[str] = []
    round2_pairs: list[tuple[str, str]] = []

    for lid in l1.index:
        d1, d2 = norm(l1.at[lid, "labeler1_decision"]), norm(l2.at[lid, "labeler2_decision"])
        entry = {"labeling_id": lid, "labeler1_round1": d1, "labeler2_round1": d2}

        if d1 == d2:
            entry |= {"decision": d1, "resolution_source": "agreement_round1"}
            gold.append(entry)
            continue

        v1, v2 = r1.get(lid), r2.get(lid)
        if v1 and v2:
            round2_pairs.append((v1, v2))
            entry |= {"labeler1_round2": v1, "labeler2_round2": v2}
            if v1 == v2:
                entry |= {"decision": v1, "resolution_source": "agreement_round2"}
                gold.append(entry)
                continue

        if lid in audit_consensus:
            entry |= {"decision": audit_consensus[lid], "resolution_source": "consensus"}
            gold.append(entry)
            continue

        if lid in audit_tiebreak:
            tb = audit_tiebreak[lid]
            entry |= {
                "decision": tb["decision"],
                "resolution_source": "tiebreak",
                "tiebreak_criterion": tb["criterion"],
                "tiebreak_rationale": tb["rationale"],
            }
            gold.append(entry)
            continue

        entry |= {"decision": None, "resolution_source": "UNRESOLVED"}
        gold.append(entry)
        unresolved.append(lid)

    sources = Counter(e["resolution_source"] for e in gold)
    decisions = Counter(e["decision"] for e in gold if e["decision"])
    convergence = convergence_rate(round2_pairs)

    payload = {
        "metadata": {
            "protocol_version": "1.2",
            "labeler1": "Isabelle",
            "labeler2": "Luiza Iltchechen",
            "tiebreaker": "Lucas Rover",
            "n_abstracts": len(gold),
            "n_unresolved": len(unresolved),
            "unresolved_ids": unresolved,
        },
        "agreement": {
            "study_estimate_round1": (
                "kappa = 0.5287 (3-class), 0.5562 (binary); see "
                "results/kappa_report.json and results/kappa_statistics.json"
            ),
            "reconciliation_convergence_rate": (
                round(convergence, 4) if convergence is not None else None
            ),
            "reconciliation_n_items": len(round2_pairs),
            "note": (
                "reconciliation_convergence_rate is NOT a kappa and must not be "
                "reported as one. Its denominator is the set of items that "
                "disagreed in round 1, so it is descriptive and conditional on "
                "that selected subset. No post-recalibration coefficient is "
                "emitted, because re-rating only the discordant items would raise "
                "a recomputed full-corpus kappa by construction."
            ),
        },
        "resolution_sources": dict(sources),
        "decisions": dict(decisions),
        "items": gold,
    }

    if unresolved and not args.allow_unresolved:
        print(f"ERROR: {len(unresolved)} abstracts unresolved: {unresolved}", file=sys.stderr)
        print("Fill consensus_decision/tiebreak_decision in the audit sheet, or pass "
              "--allow-unresolved to write a partial gold standard.", file=sys.stderr)
        sys.exit(1)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False))

    print(f"gold standard: {args.out}")
    print(f"resolution sources: {dict(sources)}")
    print(f"decisions: {dict(decisions)}")
    if convergence is not None:
        print(f"reconciliation convergence (not a kappa): {convergence:.1%} "
              f"of {len(round2_pairs)} re-rated items")
    if unresolved:
        print(f"WARNING: {len(unresolved)} unresolved: {unresolved}")


if __name__ == "__main__":
    main()
