"""Export dual-labeling subset to Rayyan CSV and Google Sheets CSV formats.

Rayyan CSV columns follow their standard import schema:
    key,title,authors,journal,issn,volume,issue,pages,day,month,year,
    publisher,location,url,language,abstract,notes,doi,pmc_id,pubmed_id,keywords

Google Sheets: simpler format with labeling columns pre-added for each labeler.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUBSET_PATH = ROOT / "data" / "dual_labeling" / "exports" / "subset_100.json"
RAYYAN_OUT = ROOT / "data" / "dual_labeling" / "exports" / "subset_100_rayyan.csv"
SHEETS_OUT_L1 = ROOT / "data" / "dual_labeling" / "exports" / "subset_100_labeler1.csv"
SHEETS_OUT_L2 = ROOT / "data" / "dual_labeling" / "exports" / "subset_100_labeler2.csv"


def author_str(authors: list) -> str:
    if isinstance(authors, list):
        parts = []
        for a in authors:
            if isinstance(a, dict):
                name = " ".join(filter(None, [a.get("given", ""), a.get("family", "")])).strip()
                parts.append(name or a.get("name", ""))
            else:
                parts.append(str(a))
        return "; ".join(p for p in parts if p)
    return str(authors or "")


def export_rayyan(items: list[dict], path: Path) -> None:
    cols = [
        "key", "title", "authors", "journal", "issn", "volume", "issue", "pages",
        "day", "month", "year", "publisher", "location", "url", "language",
        "abstract", "notes", "doi", "pmc_id", "pubmed_id", "keywords",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, quoting=csv.QUOTE_ALL)
        w.writeheader()
        for x in items:
            w.writerow({
                "key": x["labeling_id"],
                "title": x["title"],
                "authors": author_str(x["authors"]),
                "journal": x["journal"],
                "year": x["year"],
                "abstract": x["abstract"],
                "doi": x.get("doi", ""),
                "pubmed_id": x["pmid"],
                "language": "English",
                "issn": "", "volume": "", "issue": "", "pages": "",
                "day": "", "month": "", "publisher": "", "location": "",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{x['pmid']}/" if x["pmid"] else "",
                "notes": "", "pmc_id": "", "keywords": "",
            })
    print(f"Rayyan CSV: {path.relative_to(ROOT)}  (n={len(items)})")


def export_sheets(items: list[dict], path: Path, labeler_name: str) -> None:
    cols = [
        "labeling_id", "pmid", "year", "journal", "title", "abstract",
        "url",
        f"{labeler_name}_decision",      # INCLUDE / EXCLUDE / UNCERTAIN
        f"{labeler_name}_confidence",    # HIGH / MEDIUM / LOW
        f"{labeler_name}_rationale",     # free-text short
        f"{labeler_name}_criteria_failed",  # if EXCLUDE, which criteria
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, quoting=csv.QUOTE_ALL)
        w.writeheader()
        for x in items:
            w.writerow({
                "labeling_id": x["labeling_id"],
                "pmid": x["pmid"],
                "year": x["year"],
                "journal": x["journal"],
                "title": x["title"],
                "abstract": x["abstract"],
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{x['pmid']}/" if x["pmid"] else "",
                f"{labeler_name}_decision": "",
                f"{labeler_name}_confidence": "",
                f"{labeler_name}_rationale": "",
                f"{labeler_name}_criteria_failed": "",
            })
    print(f"Sheets CSV ({labeler_name}): {path.relative_to(ROOT)}")


def main() -> None:
    subset = json.loads(SUBSET_PATH.read_text())["items"]
    export_rayyan(subset, RAYYAN_OUT)
    export_sheets(subset, SHEETS_OUT_L1, "labeler1")
    export_sheets(subset, SHEETS_OUT_L2, "labeler2")


if __name__ == "__main__":
    main()
