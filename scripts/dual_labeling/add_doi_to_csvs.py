"""Add DOI column to dual-labeling CSV exports.

Reads canonical metadata from subset_100.json and merges DOI into the
4 labeler CSVs (subset_100_labeler{1,2}.csv, extraction_25_labeler{1,2}.csv)
and into subset_100_rayyan.csv.
"""
import csv
import json
from pathlib import Path

EXPORTS = Path(__file__).resolve().parents[2] / "data" / "dual_labeling" / "exports"
SOURCE_JSON = EXPORTS / "subset_100.json"


def load_doi_map() -> dict[str, str]:
    with SOURCE_JSON.open() as f:
        data = json.load(f)
    return {item["labeling_id"]: item.get("doi", "") for item in data["items"]}


def add_doi(csv_path: Path, doi_map: dict[str, str], after_col: str = "pmid") -> None:
    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    if "doi" in fieldnames:
        print(f"[skip] {csv_path.name} already has 'doi' column")
        return

    idx = fieldnames.index(after_col) + 1
    fieldnames.insert(idx, "doi")

    for row in rows:
        row["doi"] = doi_map.get(row["labeling_id"], "")

    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[ok]   {csv_path.name} — added DOI column ({sum(1 for r in rows if r['doi'])} / {len(rows)} populated)")


def main() -> None:
    doi_map = load_doi_map()
    print(f"Loaded {len(doi_map)} DOIs from {SOURCE_JSON.name}")
    print(f"Non-empty DOIs: {sum(1 for v in doi_map.values() if v)} / {len(doi_map)}\n")

    targets = [
        EXPORTS / "subset_100_labeler1.csv",
        EXPORTS / "subset_100_labeler2.csv",
        EXPORTS / "extraction_25_labeler1.csv",
        EXPORTS / "extraction_25_labeler2.csv",
        EXPORTS / "subset_100_rayyan.csv",
    ]
    for path in targets:
        if path.exists():
            add_doi(path, doi_map)
        else:
            print(f"[miss] {path.name} not found")


if __name__ == "__main__":
    main()
