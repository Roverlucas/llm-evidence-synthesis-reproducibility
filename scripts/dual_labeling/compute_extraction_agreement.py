"""Compute field-by-field agreement between two human extractors.

Complements compute_kappa.py (which handles 3-class screening) by quantifying
agreement on the structured extraction task. Reports:

    - Numeric fields (effect_estimate, ci_lower, ci_upper): exact match,
      tolerance-based agreement (default +-5% relative), and absolute difference.
    - Categorical fields (effect_measure, study_design, lag, outcome_specific):
      Cohen's kappa and percent agreement.
    - Free-text fields (study_location, population, exposure_increment): exact
      match, normalized match (lowercase + strip + whitespace), Jaccard token
      overlap, and Levenshtein-similarity ratio.
    - Count field (n_estimates_in_abstract): exact match and absolute
      difference distribution.

Outputs:
    - extraction_agreement_report.json (all metrics)
    - extraction_discordances.csv (every per-field discordance, for adjudication)
    - extraction_summary.csv (per-field summary metrics)

Usage:
    python scripts/dual_labeling/compute_extraction_agreement.py \\
        --labeler1 data/dual_labeling/exports/extraction_25_labeler1_done.csv \\
        --labeler2 data/dual_labeling/exports/extraction_25_labeler2_done.csv \\
        --out data/dual_labeling/results/

Notes:
    This is a v1 skeleton ready to run on the dual-labeling outputs when
    they return from the recruited validators (Profa. Yara's recruitment is
    in progress as of 2026-05-20). Edge cases revealed by real data may
    require tightening the normalization and tolerance rules.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

# Tolerance for numeric exact-match: equality after rounding to this many
# decimal places. Numeric agreement at +-5% relative is also reported separately.
NUMERIC_ROUND_DECIMALS = 3
NUMERIC_REL_TOLERANCE = 0.05  # +-5%

NUMERIC_FIELDS = ["effect_estimate", "ci_lower", "ci_upper"]
CATEGORICAL_FIELDS = ["effect_measure", "study_design", "lag", "outcome_specific"]
FREETEXT_FIELDS = ["study_location", "population", "exposure_increment"]
COUNT_FIELDS = ["n_estimates_in_abstract"]

ALL_SUBSTANTIVE_FIELDS = NUMERIC_FIELDS + CATEGORICAL_FIELDS + FREETEXT_FIELDS + COUNT_FIELDS


def _safe_float(v: str) -> float | None:
    if v is None:
        return None
    v = v.strip()
    if not v or v.lower() in {"na", "n/a", "none", "null", "missing"}:
        return None
    # Remove thousands separators conservatively
    v = v.replace(",", ".") if v.count(",") == 1 and v.count(".") == 0 else v
    try:
        return float(v)
    except ValueError:
        return None


def _normalize_text(v: str) -> str:
    if v is None:
        return ""
    v = v.strip().lower()
    v = re.sub(r"\s+", " ", v)
    v = re.sub(r"[\.\,;:\!\?]+$", "", v)
    return v


def _jaccard_tokens(a: str, b: str) -> float:
    ta = set(_normalize_text(a).split())
    tb = set(_normalize_text(b).split())
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _levenshtein_ratio(a: str, b: str) -> float:
    """Pure-Python Levenshtein similarity ratio (no external dependency)."""
    a, b = _normalize_text(a), _normalize_text(b)
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            curr[j] = min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost)
        prev = curr
    edit = prev[-1]
    max_len = max(len(a), len(b))
    return 1.0 - (edit / max_len)


def load_extractions(path: Path, labeler_prefix: str) -> dict[str, dict]:
    """Return {labeling_id: {field: value}} for the labeler.

    Expects columns prefixed with f"{labeler_prefix}_" (e.g., "labeler1_effect_estimate").
    """
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    if not rows:
        raise ValueError(f"Empty CSV: {path}")

    out: dict[str, dict] = {}
    for r in rows:
        lid = r.get("labeling_id") or r.get("key") or r.get("pmid")
        if not lid:
            continue
        rec = {}
        any_filled = False
        for field in ALL_SUBSTANTIVE_FIELDS:
            col = f"{labeler_prefix}_{field}"
            val = (r.get(col, "") or "").strip()
            rec[field] = val
            if val:
                any_filled = True
        if any_filled:
            out[lid] = rec
    return out


def cohen_kappa(l1: list[str], l2: list[str]) -> tuple[float, float]:
    categories = sorted({v for v in l1 + l2 if v})
    pairs = [(a, b) for a, b in zip(l1, l2) if a and b]
    if not pairs or len(categories) < 2:
        return (float("nan"), float("nan") if not pairs else (
            sum(1 for a, b in pairs if a == b) / len(pairs)
        ))
    n = len(pairs)
    po = sum(1 for a, b in pairs if a == b) / n
    c1 = Counter(a for a, _ in pairs)
    c2 = Counter(b for _, b in pairs)
    pe = sum((c1[c] / n) * (c2[c] / n) for c in categories)
    if pe == 1.0:
        return (1.0 if po == 1.0 else 0.0, po)
    return ((po - pe) / (1 - pe), po)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labeler1", required=True, type=Path)
    ap.add_argument("--labeler2", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--labeler1-prefix", default="labeler1")
    ap.add_argument("--labeler2-prefix", default="labeler2")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    l1 = load_extractions(args.labeler1, args.labeler1_prefix)
    l2 = load_extractions(args.labeler2, args.labeler2_prefix)

    common_ids = sorted(set(l1) & set(l2))
    if not common_ids:
        raise SystemExit("No common labeling_ids found across labelers — verify exports.")

    field_metrics: dict[str, dict] = {}
    discordances: list[dict] = []

    for field in ALL_SUBSTANTIVE_FIELDS:
        v1 = [l1[i][field] for i in common_ids]
        v2 = [l2[i][field] for i in common_ids]
        n = len(common_ids)

        if field in NUMERIC_FIELDS:
            exact = 0
            within_tol = 0
            diffs: list[float] = []
            for a, b, lid in zip(v1, v2, common_ids):
                fa, fb = _safe_float(a), _safe_float(b)
                if fa is None or fb is None:
                    continue
                if round(fa, NUMERIC_ROUND_DECIMALS) == round(fb, NUMERIC_ROUND_DECIMALS):
                    exact += 1
                denom = max(abs(fa), abs(fb), 1e-9)
                if abs(fa - fb) / denom <= NUMERIC_REL_TOLERANCE:
                    within_tol += 1
                diffs.append(abs(fa - fb))
                if abs(fa - fb) / denom > NUMERIC_REL_TOLERANCE:
                    discordances.append({
                        "labeling_id": lid, "field": field,
                        "labeler1": a, "labeler2": b,
                        "abs_diff": round(abs(fa - fb), 6),
                    })
            n_pair = exact + (n - exact)  # simplistic; we use len of diffs
            n_valid = len(diffs)
            field_metrics[field] = {
                "type": "numeric",
                "n_pairs_both_filled": n_valid,
                "exact_match_rate": round(exact / n_valid, 4) if n_valid else None,
                "within_5pct_rate": round(within_tol / n_valid, 4) if n_valid else None,
                "mean_abs_diff": round(sum(diffs) / n_valid, 4) if diffs else None,
                "max_abs_diff": round(max(diffs), 4) if diffs else None,
            }

        elif field in CATEGORICAL_FIELDS:
            kappa, agree = cohen_kappa(v1, v2)
            for a, b, lid in zip(v1, v2, common_ids):
                if a and b and a.strip().lower() != b.strip().lower():
                    discordances.append({
                        "labeling_id": lid, "field": field,
                        "labeler1": a, "labeler2": b,
                        "abs_diff": "",
                    })
            field_metrics[field] = {
                "type": "categorical",
                "n_pairs_both_filled": sum(1 for a, b in zip(v1, v2) if a and b),
                "cohen_kappa": None if kappa != kappa else round(kappa, 4),  # NaN check
                "percent_agreement": None if agree != agree else round(agree, 4),
            }

        elif field in FREETEXT_FIELDS:
            exact = sum(1 for a, b in zip(v1, v2) if a and b and a == b)
            norm = sum(1 for a, b in zip(v1, v2) if a and b and _normalize_text(a) == _normalize_text(b))
            jaccards = [_jaccard_tokens(a, b) for a, b in zip(v1, v2) if a and b]
            levs = [_levenshtein_ratio(a, b) for a, b in zip(v1, v2) if a and b]
            n_valid = len(jaccards)
            for a, b, lid in zip(v1, v2, common_ids):
                if a and b and _normalize_text(a) != _normalize_text(b):
                    discordances.append({
                        "labeling_id": lid, "field": field,
                        "labeler1": a, "labeler2": b,
                        "abs_diff": "",
                    })
            field_metrics[field] = {
                "type": "freetext",
                "n_pairs_both_filled": n_valid,
                "exact_match_rate": round(exact / n_valid, 4) if n_valid else None,
                "normalized_match_rate": round(norm / n_valid, 4) if n_valid else None,
                "mean_jaccard": round(sum(jaccards) / n_valid, 4) if jaccards else None,
                "mean_levenshtein_ratio": round(sum(levs) / n_valid, 4) if levs else None,
            }

        elif field in COUNT_FIELDS:
            exact = 0
            diffs: list[int] = []
            for a, b, lid in zip(v1, v2, common_ids):
                fa, fb = _safe_float(a), _safe_float(b)
                if fa is None or fb is None:
                    continue
                ia, ib = int(fa), int(fb)
                if ia == ib:
                    exact += 1
                else:
                    discordances.append({
                        "labeling_id": lid, "field": field,
                        "labeler1": str(ia), "labeler2": str(ib),
                        "abs_diff": str(abs(ia - ib)),
                    })
                diffs.append(abs(ia - ib))
            n_valid = len(diffs)
            field_metrics[field] = {
                "type": "count",
                "n_pairs_both_filled": n_valid,
                "exact_match_rate": round(exact / n_valid, 4) if n_valid else None,
                "mean_abs_diff": round(sum(diffs) / n_valid, 4) if diffs else None,
            }

    report = {
        "metadata": {
            "labeler1_file": str(args.labeler1),
            "labeler2_file": str(args.labeler2),
            "n_common_items": len(common_ids),
            "n_only_labeler1": len(set(l1) - set(l2)),
            "n_only_labeler2": len(set(l2) - set(l1)),
        },
        "field_metrics": field_metrics,
        "thresholds": {
            "numeric_relative_tolerance": NUMERIC_REL_TOLERANCE,
            "numeric_round_decimals": NUMERIC_ROUND_DECIMALS,
        },
        "n_total_discordances": len(discordances),
    }

    (args.out / "extraction_agreement_report.json").write_text(json.dumps(report, indent=2))

    if discordances:
        cols = ["labeling_id", "field", "labeler1", "labeler2", "abs_diff"]
        with (args.out / "extraction_discordances.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols + ["resolution", "resolver_notes"], quoting=csv.QUOTE_ALL)
            w.writeheader()
            for d in discordances:
                d.setdefault("resolution", "")
                d.setdefault("resolver_notes", "")
                w.writerow(d)

    # Per-field summary CSV
    summary_cols = ["field", "type", "n_pairs_both_filled", "primary_metric", "primary_value"]
    with (args.out / "extraction_summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=summary_cols)
        w.writeheader()
        for field, m in field_metrics.items():
            if m["type"] == "categorical":
                primary_metric, primary_value = "cohen_kappa", m.get("cohen_kappa")
            elif m["type"] == "numeric":
                primary_metric, primary_value = "within_5pct_rate", m.get("within_5pct_rate")
            elif m["type"] == "freetext":
                primary_metric, primary_value = "normalized_match_rate", m.get("normalized_match_rate")
            else:  # count
                primary_metric, primary_value = "exact_match_rate", m.get("exact_match_rate")
            w.writerow({
                "field": field,
                "type": m["type"],
                "n_pairs_both_filled": m.get("n_pairs_both_filled"),
                "primary_metric": primary_metric,
                "primary_value": primary_value,
            })

    print(f"n_common_items={len(common_ids)}  n_total_discordances={len(discordances)}")
    print(f"Outputs written to: {args.out}")


if __name__ == "__main__":
    main()
