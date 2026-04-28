"""Export extraction labeling CSVs for the 25 INCLUDE abstracts in the dual-labeling subset.

Adds extraction task on top of the screening task. The 25 include items become the
extraction gold standard - the FIRST real human extraction gold for this study.

Output:
    data/dual_labeling/exports/extraction_25_labeler1.csv
    data/dual_labeling/exports/extraction_25_labeler2.csv
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUBSET = ROOT / "data" / "dual_labeling" / "exports" / "subset_100.json"
OUT_L1 = ROOT / "data" / "dual_labeling" / "exports" / "extraction_25_labeler1.csv"
OUT_L2 = ROOT / "data" / "dual_labeling" / "exports" / "extraction_25_labeler2.csv"


def export(items: list[dict], path: Path, labeler_name: str) -> None:
    cols = [
        "labeling_id", "pmid", "title", "abstract", "url",
        f"{labeler_name}_effect_measure",       # RR / OR / HR / IRR
        f"{labeler_name}_effect_estimate",      # numeric
        f"{labeler_name}_ci_lower",
        f"{labeler_name}_ci_upper",
        f"{labeler_name}_lag",                  # 0 / 0-1 / 1 / 2 / etc
        f"{labeler_name}_exposure_increment",   # per 10 ug/m3 / per IQR
        f"{labeler_name}_outcome_specific",     # all_respiratory / asthma / COPD / pneumonia
        f"{labeler_name}_study_design",         # time_series / case_crossover
        f"{labeler_name}_study_location",
        f"{labeler_name}_population",           # general / elderly / children
        f"{labeler_name}_n_estimates_in_abstract",  # how many distinct estimates
        f"{labeler_name}_notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, quoting=csv.QUOTE_ALL)
        w.writeheader()
        for it in items:
            row = {c: "" for c in cols}
            row["labeling_id"] = it["labeling_id"]
            row["pmid"] = it["pmid"]
            row["title"] = it["title"]
            row["abstract"] = it["abstract"]
            row["url"] = f"https://pubmed.ncbi.nlm.nih.gov/{it['pmid']}/" if it["pmid"] else ""
            w.writerow(row)
    print(f"Wrote {path.relative_to(ROOT)}  ({len(items)} items)")


def main() -> None:
    subset = json.loads(SUBSET.read_text())["items"]
    include_only = [it for it in subset if it["heuristic_category"] == "include"]
    print(f"Filtering to INCLUDE items: {len(include_only)}/{len(subset)}")
    export(include_only, OUT_L1, "labeler1")
    export(include_only, OUT_L2, "labeler2")


if __name__ == "__main__":
    main()
