"""Ingest a blinded v1.2 recalibration return (round 2) from XLSX.

Round 2 re-rates only the 25 abstracts the two labelers disagreed on in round 1,
under protocol v1.2. The v1.1 ingestor cannot be reused: its criteria vocabulary
is ``[1-6]`` and would reject the ``5a/5b/5c`` levels that the whole point of
v1.2 introduced.

Beyond the arrival checks that round 1 got (complete columns, ids and abstracts
untouched, vocabulary conforming), this validates the return against the
**decision table in protocol v1.2 §4**, which is fully deterministic:

    no criterion failed                      -> INCLUDE
    >= 2 criteria failed (any combination)   -> EXCLUDE
    exactly one, structural (1, 2, 3, 6)     -> EXCLUDE
    exactly one, criterion 4                 -> UNCERTAIN
    exactly one, case 5b                     -> UNCERTAIN
    exactly one, case 5c                     -> EXCLUDE

A bare ``5`` is rejected rather than guessed: that ambiguity is the defect that
produced kappa = 0.529 in round 1, and silently resolving it here would hide a
recurrence. ``5a`` is a criterion *met*, so it is never a valid failure entry.

This script does not compute any agreement coefficient. Round 2 conditions on the
discordant items, so a recomputed coefficient rises by construction — see
``build_gold_standard.py``, which refuses to emit one.

Usage:
    python scripts/dual_labeling/ingest_recalibration_xlsx.py \
        --xlsx ~/Downloads/recalibracao_labeler1_Isabelle-2.xlsx \
        --template data/dual_labeling/reconciliation/recalibration_labeler1.csv \
        --round1 data/dual_labeling/returned/subset_100_labeler1_RETURNED.csv \
        --prefix labeler1 \
        --out data/dual_labeling/reconciliation/returned/recalibration_labeler1_RETURNED.csv \
        --archive-raw
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
STRUCTURAL = {"1", "2", "3", "6"}
CONDITIONAL = {"4", "5b", "5c"}
VALID_FAILURES = STRUCTURAL | CONDITIONAL
META_COLS = ["labeling_id", "pmid", "doi", "year", "journal", "title", "abstract", "url"]
LABEL_COLS = ["decision_v12", "confidence_v12", "rationale_v12", "criteria_failed_v12"]
SHEET = "recalibracao"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Portuguese conjunction used as a separator by one labeler ("3, 4 E 5"). Treated as
# punctuation, not as a criterion code.
_CONJUNCTIONS = {"E", "AND"}


def normalise_criteria(value: object, *, bare_five_as: str | None = None) -> object:
    """Canonicalise ``2; 3`` / ``2,3`` / ``4.0`` / ``3, 4 E 5`` into ``2,3``.

    Excel stores a lone ``4`` as the float ``4.0``; the trailing ``.0`` is a
    spreadsheet artefact, not a labeler choice, so it is stripped here rather
    than reported as a malformed entry. ``0`` means "no criterion failed" and
    normalises to empty, which is what an INCLUDE decision implies.

    ``bare_five_as`` handles a bare ``5`` where the v1.2 vocabulary requires
    ``5b`` or ``5c``. It is **off by default and must be passed explicitly**:
    guessing the level silently would reintroduce the very ambiguity that
    produced the round-1 kappa. Pass it only when the returned rationales
    determine the level independently, and record that determination.
    """
    if pd.isna(value):
        return value
    text = str(value).strip()
    if re.fullmatch(r"\d+\.0", text):
        text = text[:-2]
    parts = []
    for p in re.split(r"[;,\s]+", text):
        p = re.sub(r"\.0$", "", p.strip())
        if not p or p.upper() in _CONJUNCTIONS or p == "0":
            continue
        if p == "5" and bare_five_as:
            p = bare_five_as
        parts.append(p)
    return ",".join(parts)


def failures(value: object) -> list[str]:
    if pd.isna(value) or not str(value).strip():
        return []
    return str(value).split(",")


def decision_from_table(failed: list[str]) -> str:
    """Protocol v1.2 §4, applied literally. Precedence: EXCLUDE > UNCERTAIN > INCLUDE."""
    if not failed:
        return "INCLUDE"
    if len(failed) >= 2:
        return "EXCLUDE"
    only = failed[0]
    if only in STRUCTURAL or only == "5c":
        return "EXCLUDE"
    return "UNCERTAIN"  # criterion 4 or case 5b


def validate(df: pd.DataFrame, template: pd.DataFrame, prefix: str) -> list[str]:
    errors: list[str] = []

    if list(df["labeling_id"]) != list(template["labeling_id"]):
        errors.append("labeling_id differs from the sent template (order or content)")
    for col in ("title", "abstract"):
        if not (df[col].fillna("") == template[col].fillna("")).all():
            errors.append(f"{col} was edited relative to the sent template")

    other = "labeler2" if prefix == "labeler1" else "labeler1"
    if leaked := [c for c in df.columns if c.startswith(f"{other}_")]:
        errors.append(f"blinding broken: columns from the other labeler present: {leaked}")

    decision = df[f"{prefix}_decision_v12"].astype(str).str.strip().str.upper()
    confidence = df[f"{prefix}_confidence_v12"].astype(str).str.strip().str.upper()

    if (decision == "NAN").any():
        blank = df.loc[decision == "NAN", "labeling_id"].tolist()
        errors.append(f"decision column has empty cells: {blank}")
    if bad := sorted(set(decision) - DECISIONS - {"NAN"}):
        errors.append(f"decision values outside protocol vocabulary: {bad}")
    if bad := sorted(set(confidence) - CONFIDENCES - {"NAN"}):
        errors.append(f"confidence values outside protocol vocabulary: {bad}")

    rationale = df[f"{prefix}_rationale_v12"].astype(str).str.strip()
    if short := df.loc[rationale.str.len() < 5, "labeling_id"].tolist():
        errors.append(f"rationale missing or shorter than 5 characters: {short}")

    for _, row in df.iterrows():
        lid = row["labeling_id"]
        failed = failures(row[f"{prefix}_criteria_failed_v12"])
        if bad := [f for f in failed if f not in VALID_FAILURES]:
            hint = " (bare '5' is ambiguous under v1.2 — use 5b or 5c)" if "5" in bad else ""
            if "5a" in bad:
                hint = " ('5a' is a criterion met, never a failure)"
            errors.append(f"{lid}: criteria outside the v1.2 vocabulary: {bad}{hint}")
            continue
        if len(set(failed)) != len(failed):
            errors.append(f"{lid}: repeated criterion in {failed}")
            continue
        declared = str(row[f"{prefix}_decision_v12"]).strip().upper()
        expected = decision_from_table(sorted(set(failed)))
        if declared != expected:
            errors.append(
                f"{lid}: decision {declared} contradicts protocol v1.2 §4 — "
                f"criteria {failed or ['none']} imply {expected}"
            )

    return errors


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", required=True, type=Path)
    ap.add_argument("--template", required=True, type=Path)
    ap.add_argument("--round1", type=Path,
                    help="the labeler's own round-1 return, to report what changed")
    ap.add_argument("--prefix", default="labeler1", choices=["labeler1", "labeler2"])
    ap.add_argument("--sheet", default=SHEET)
    ap.add_argument("--bare-five-as", choices=["5b", "5c"], default=None,
                    help="map a bare '5' to this v1.2 level. Off by default; pass only "
                         "when the rationales determine the level, and say so in the log.")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--archive-raw", action="store_true",
                    help="copy the untouched workbook next to the CSV for provenance")
    args = ap.parse_args()

    xlsx = args.xlsx.expanduser()
    df = pd.read_excel(xlsx, sheet_name=args.sheet)
    template = pd.read_csv(args.template)

    col_criteria = f"{args.prefix}_criteria_failed_v12"
    df[col_criteria] = df[col_criteria].map(
        lambda v: normalise_criteria(v, bare_five_as=args.bare_five_as)
    )
    if args.bare_five_as:
        print(f"NOTE: bare '5' entries mapped to '{args.bare_five_as}' by explicit instruction.")
    for col in (f"{args.prefix}_decision_v12", f"{args.prefix}_confidence_v12"):
        df[col] = df[col].astype(str).str.strip().str.upper()

    if errors := validate(df, template, args.prefix):
        print("VALIDATION FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    out_df = df[META_COLS + [f"{args.prefix}_{c}" for c in LABEL_COLS]]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(args.out, index=False)

    if args.archive_raw:
        raw_dest = args.out.with_name(f"{args.out.stem}_SOURCE{xlsx.suffix}")
        raw_dest.write_bytes(xlsx.read_bytes())
        print(f"raw workbook archived: {raw_dest}")

    counts = out_df[f"{args.prefix}_decision_v12"].value_counts().to_dict()
    print(f"source xlsx sha256: {sha256(xlsx)}")
    print(f"output csv  sha256: {sha256(args.out)}")
    print(f"rows: {len(out_df)}  decisions: {counts}")
    print("protocol v1.2 §4 decision table: consistent on all rows")

    if args.round1 and args.round1.exists():
        r1 = pd.read_csv(args.round1).set_index("labeling_id")
        col = f"{args.prefix}_decision"
        if col in r1.columns:
            changed = [
                (lid, str(r1.at[lid, col]).strip().upper(), dec)
                for lid, dec in zip(out_df["labeling_id"], out_df[f"{args.prefix}_decision_v12"])
                if lid in r1.index and str(r1.at[lid, col]).strip().upper() != dec
            ]
            print(f"\nchanged vs own round 1: {len(changed)}/{len(out_df)}")
            for lid, before, after in changed:
                print(f"  {lid}: {before} -> {after}")
            print("\nThis is one rater's movement under a revised protocol, not agreement. "
                  "No coefficient is computed here.")

    print(f"\nwritten: {args.out}")


if __name__ == "__main__":
    main()
