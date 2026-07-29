"""Ingest the labeler1 (Isabelle) Stage-A screening return from XLSX.

The labeler received the ``subset_100_labeler2.csv`` template by mistake, so the
delivered workbook carries ``labeler2_*`` column names. This script archives the
raw workbook, validates it against the sent template, normalises the
``criteria_failed`` separator, and writes a canonical ``labeler1_*`` CSV that
``compute_kappa.py`` can consume.

Validation mirrors what was done for labeler2 (Luiza) on arrival:
    - all four decision columns complete (criteria_failed only where applicable)
    - labeling_id identical and in the same order as the sent template
    - abstracts and titles byte-identical (no accidental edits)
    - vocabulary conforms to protocol v1.1

Usage:
    python scripts/dual_labeling/ingest_labeler1_xlsx.py \
        --xlsx ~/Downloads/subset_100_labeler2_Isabelle.xlsx \
        --template data/dual_labeling/exports/subset_100_labeler2.csv \
        --out data/dual_labeling/returned/subset_100_labeler1_RETURNED.csv
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

import pandas as pd

DECISIONS = {"INCLUDE", "EXCLUDE", "UNCERTAIN"}
CONFIDENCES = {"HIGH", "MEDIUM", "LOW"}
CRITERIA_RE = re.compile(r"[1-6](,[1-6])*")
META_COLS = ["labeling_id", "pmid", "doi", "year", "journal", "title", "abstract", "url"]
LABEL_COLS = ["decision", "confidence", "rationale", "criteria_failed"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalise_criteria(value: object) -> object:
    """Accept ``2; 3`` / ``2,3`` / ``2 3`` and emit the protocol form ``2,3``."""
    if pd.isna(value):
        return value
    parts = [p.strip() for p in re.split(r"[;,\s]+", str(value).strip()) if p.strip()]
    return ",".join(parts)


def validate(df: pd.DataFrame, template: pd.DataFrame, src_prefix: str) -> list[str]:
    errors: list[str] = []

    if list(df["labeling_id"]) != list(template["labeling_id"]):
        errors.append("labeling_id differs from the sent template (order or content)")
    for col in ("title", "abstract"):
        if not (df[col].fillna("") == template[col].fillna("")).all():
            errors.append(f"{col} was edited relative to the sent template")

    decision = df[f"{src_prefix}_decision"].astype(str).str.strip().str.upper()
    confidence = df[f"{src_prefix}_confidence"].astype(str).str.strip().str.upper()

    if decision.isna().any() or (decision == "NAN").any():
        errors.append("decision column has empty cells")
    if bad := sorted(set(decision) - DECISIONS):
        errors.append(f"decision values outside protocol vocabulary: {bad}")
    if bad := sorted(set(confidence) - CONFIDENCES):
        errors.append(f"confidence values outside protocol vocabulary: {bad}")

    rationale = df[f"{src_prefix}_rationale"].astype(str).str.strip()
    if (rationale.str.len() < 5).any():
        errors.append("rationale missing or shorter than 5 characters on some rows")

    criteria = df[f"{src_prefix}_criteria_failed"]
    for idx, value in criteria.dropna().items():
        if not CRITERIA_RE.fullmatch(str(value)):
            errors.append(f"row {idx}: malformed criteria_failed {value!r}")
    # criteria_failed is expected exactly where the decision is not INCLUDE
    expected = decision != "INCLUDE"
    if not (criteria.notna() == expected).all():
        mismatched = df.loc[criteria.notna() != expected, "labeling_id"].tolist()
        errors.append(f"criteria_failed presence inconsistent with decision: {mismatched}")

    return errors


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", required=True, type=Path)
    ap.add_argument("--template", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--src-prefix", default="labeler2",
                    help="column prefix inside the delivered workbook")
    ap.add_argument("--dst-prefix", default="labeler1",
                    help="canonical prefix to write")
    ap.add_argument("--archive-raw", action="store_true",
                    help="copy the untouched workbook next to the CSV for provenance")
    args = ap.parse_args()

    xlsx = args.xlsx.expanduser()
    df = pd.read_excel(xlsx)
    template = pd.read_csv(args.template)

    # Normalise separators and casing first; validation then checks the canonical
    # form, so an accepted-but-non-canonical input (``2; 3``) is not a failure.
    df[f"{args.src_prefix}_criteria_failed"] = df[f"{args.src_prefix}_criteria_failed"].map(
        normalise_criteria
    )
    for col in (f"{args.src_prefix}_decision", f"{args.src_prefix}_confidence"):
        df[col] = df[col].astype(str).str.strip().str.upper()

    errors = validate(df, template, args.src_prefix)
    if errors:
        print("VALIDATION FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    rename = {f"{args.src_prefix}_{c}": f"{args.dst_prefix}_{c}" for c in LABEL_COLS}
    out_df = df.rename(columns=rename)[
        META_COLS + [f"{args.dst_prefix}_{c}" for c in LABEL_COLS]
    ]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(args.out, index=False)

    if args.archive_raw:
        raw_dest = args.out.with_name(f"{args.out.stem}_SOURCE{xlsx.suffix}")
        raw_dest.write_bytes(xlsx.read_bytes())
        print(f"raw workbook archived: {raw_dest}")

    counts = out_df[f"{args.dst_prefix}_decision"].value_counts().to_dict()
    print(f"source xlsx sha256: {sha256(xlsx)}")
    print(f"output csv  sha256: {sha256(args.out)}")
    print(f"rows: {len(out_df)}  decisions: {counts}")
    print(f"written: {args.out}")


if __name__ == "__main__":
    main()
