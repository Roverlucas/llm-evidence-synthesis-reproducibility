"""Compute Cohen's kappa + percent agreement between two labelers.

Also exports:
    - discordances.csv (cases where labelers disagree, for resolution meeting)
    - kappa_report.json (metrics)
    - confusion_matrix.csv

Usage:
    python scripts/dual_labeling/compute_kappa.py \
        --labeler1 data/dual_labeling/exports/labeler1_done.csv \
        --labeler2 data/dual_labeling/exports/labeler2_done.csv \
        --out data/dual_labeling/results/

Accepts either the Google Sheets format (decision columns) or a Rayyan export
(inferred from column names).
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

LABEL_CATEGORIES = ["INCLUDE", "EXCLUDE", "UNCERTAIN"]


def load_labels(path: Path) -> dict[str, dict]:
    """Return {labeling_id: {decision, confidence, rationale, criteria_failed}}."""
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    if not rows:
        raise ValueError(f"Empty CSV: {path}")

    cols = rows[0].keys()
    # Detect format
    decision_col = next(
        (c for c in cols if c.endswith("_decision") or c.lower() == "decision"),
        None,
    )
    if decision_col is None:
        # Rayyan export: has included / excluded columns or inclusion_decision
        if "inclusion_decision" in cols:
            decision_col = "inclusion_decision"
        else:
            raise ValueError(f"Cannot find decision column in {path}. Cols: {list(cols)}")

    prefix = decision_col.rsplit("_decision", 1)[0] if decision_col.endswith("_decision") else ""

    out: dict[str, dict] = {}
    for r in rows:
        lid = r.get("labeling_id") or r.get("key") or r.get("pmid")
        if not lid:
            continue
        decision = (r[decision_col] or "").strip().upper()
        if decision in {"MAYBE", "UNSURE", "UNCERT"}:
            decision = "UNCERTAIN"
        if decision not in LABEL_CATEGORIES:
            continue  # skip unlabeled
        out[lid] = {
            "decision": decision,
            "confidence": (r.get(f"{prefix}_confidence", "") or "").strip().upper() or "",
            "rationale": (r.get(f"{prefix}_rationale", "") or "").strip(),
            "criteria_failed": (r.get(f"{prefix}_criteria_failed", "") or "").strip(),
        }
    return out


def cohen_kappa(l1: list[str], l2: list[str], categories: list[str]) -> float:
    """Compute Cohen's kappa without sklearn dependency."""
    n = len(l1)
    if n == 0 or n != len(l2):
        raise ValueError("Label lists must be non-empty and same length")

    # Observed agreement
    agree = sum(1 for a, b in zip(l1, l2) if a == b)
    po = agree / n

    # Expected agreement
    c1 = Counter(l1)
    c2 = Counter(l2)
    pe = sum((c1[cat] / n) * (c2[cat] / n) for cat in categories)

    if pe == 1.0:
        return 1.0 if po == 1.0 else 0.0
    return (po - pe) / (1 - pe)


def kappa_interpretation(k: float) -> str:
    # Landis & Koch 1977
    if k < 0:
        return "poor (worse than chance)"
    if k < 0.20:
        return "slight"
    if k < 0.40:
        return "fair"
    if k < 0.60:
        return "moderate"
    if k < 0.80:
        return "substantial"
    return "almost perfect"


def confusion_matrix(l1: list[str], l2: list[str], categories: list[str]) -> dict:
    m = {a: {b: 0 for b in categories} for a in categories}
    for a, b in zip(l1, l2):
        m[a][b] += 1
    return m


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labeler1", required=True, type=Path)
    ap.add_argument("--labeler2", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path, help="Output directory")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    l1 = load_labels(args.labeler1)
    l2 = load_labels(args.labeler2)

    common_ids = sorted(set(l1) & set(l2))
    only_l1 = sorted(set(l1) - set(l2))
    only_l2 = sorted(set(l2) - set(l1))

    d1 = [l1[i]["decision"] for i in common_ids]
    d2 = [l2[i]["decision"] for i in common_ids]

    kappa = cohen_kappa(d1, d2, LABEL_CATEGORIES)
    agreement = sum(1 for a, b in zip(d1, d2) if a == b) / len(d1) if d1 else 0.0
    cm = confusion_matrix(d1, d2, LABEL_CATEGORIES)

    # Kappa excluding UNCERTAIN (binary include/exclude)
    binary_pairs = [(a, b) for a, b in zip(d1, d2) if a != "UNCERTAIN" and b != "UNCERTAIN"]
    if binary_pairs:
        b1 = [a for a, _ in binary_pairs]
        b2 = [b for _, b in binary_pairs]
        kappa_binary = cohen_kappa(b1, b2, ["INCLUDE", "EXCLUDE"])
        agreement_binary = sum(1 for a, b in zip(b1, b2) if a == b) / len(b1)
    else:
        kappa_binary = None
        agreement_binary = None

    # Discordances
    discordances = []
    for lid in common_ids:
        a, b = l1[lid]["decision"], l2[lid]["decision"]
        if a != b:
            discordances.append({
                "labeling_id": lid,
                "labeler1_decision": a,
                "labeler1_confidence": l1[lid]["confidence"],
                "labeler1_rationale": l1[lid]["rationale"],
                "labeler2_decision": b,
                "labeler2_confidence": l2[lid]["confidence"],
                "labeler2_rationale": l2[lid]["rationale"],
                "resolution": "",
                "resolver_notes": "",
            })

    # Write outputs
    report = {
        "metadata": {
            "labeler1_file": str(args.labeler1),
            "labeler2_file": str(args.labeler2),
            "n_total_subset": len(common_ids),
            "n_only_labeler1": len(only_l1),
            "n_only_labeler2": len(only_l2),
        },
        "three_class": {
            "categories": LABEL_CATEGORIES,
            "cohen_kappa": round(kappa, 4),
            "kappa_interpretation": kappa_interpretation(kappa),
            "percent_agreement": round(agreement, 4),
            "n_discordances": len(discordances),
            "discordance_rate": round(len(discordances) / len(common_ids), 4) if common_ids else None,
            "confusion_matrix": cm,
        },
        "binary_include_vs_exclude": {
            "cohen_kappa": round(kappa_binary, 4) if kappa_binary is not None else None,
            "kappa_interpretation": kappa_interpretation(kappa_binary) if kappa_binary is not None else None,
            "percent_agreement": round(agreement_binary, 4) if agreement_binary is not None else None,
            "n_pairs": len(binary_pairs) if binary_pairs else 0,
        },
        "targets": {
            "cochrane_kappa": 0.80,
            "meets_target": kappa >= 0.80,
        },
    }

    (args.out / "kappa_report.json").write_text(json.dumps(report, indent=2))

    if discordances:
        cols = list(discordances[0].keys())
        with (args.out / "discordances.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, quoting=csv.QUOTE_ALL)
            w.writeheader()
            w.writerows(discordances)

    # Confusion matrix CSV
    with (args.out / "confusion_matrix.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["labeler1 \\ labeler2"] + LABEL_CATEGORIES)
        for cat in LABEL_CATEGORIES:
            w.writerow([cat] + [cm[cat][b] for b in LABEL_CATEGORIES])

    print(f"n_total_subset={len(common_ids)}  only_l1={len(only_l1)}  only_l2={len(only_l2)}")
    print(f"Cohen's kappa (3-class) = {kappa:.4f}  [{kappa_interpretation(kappa)}]")
    print(f"Percent agreement = {agreement:.2%}")
    print(f"Discordances: {len(discordances)}")
    if kappa_binary is not None:
        print(f"Cohen's kappa (binary) = {kappa_binary:.4f}  [{kappa_interpretation(kappa_binary)}]")
    meets = "YES" if kappa >= 0.80 else "NO"
    print(f"Meets Cochrane target (kappa >= 0.80): {meets}")
    print(f"Outputs written to: {args.out}")


if __name__ == "__main__":
    main()
