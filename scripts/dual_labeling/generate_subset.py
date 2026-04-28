"""Generate stratified subset of 100 abstracts for dual-human labeling.

Stratification:
    - 25 clear-include
    - 25 clear-exclude
    - 50 ambiguous
Within each stratum: stratified by year tertile (old/mid/recent) to avoid
temporal bias, then uniform random sampling with fixed seed (42).

Output: data/dual_labeling/exports/subset_100.json
"""
from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS_PATH = ROOT / "data" / "corpus" / "corpus_500.json"
OUTPUT_PATH = ROOT / "data" / "dual_labeling" / "exports" / "subset_100.json"

STRATA_TARGETS = {"include": 25, "exclude": 25, "ambiguous": 50}
SEED = 42


def year_tertile(year: int, tertiles: tuple[int, int]) -> str:
    low, high = tertiles
    if year <= low:
        return "old"
    if year <= high:
        return "mid"
    return "recent"


def stratified_sample(items: list[dict], n: int, rng: random.Random) -> list[dict]:
    years = sorted(int(x["year"]) for x in items)
    if len(years) < 6:
        rng.shuffle(items)
        return items[:n]
    t1 = years[len(years) // 3]
    t2 = years[(2 * len(years)) // 3]

    buckets: dict[str, list[dict]] = defaultdict(list)
    for x in items:
        buckets[year_tertile(int(x["year"]), (t1, t2))].append(x)

    per_bucket = n // 3
    remainder = n - per_bucket * 3
    sampled: list[dict] = []
    for i, key in enumerate(["old", "mid", "recent"]):
        take = per_bucket + (1 if i < remainder else 0)
        pool = buckets[key]
        rng.shuffle(pool)
        sampled.extend(pool[:take])
    return sampled


def main() -> None:
    corpus = json.loads(CORPUS_PATH.read_text())["corpus"]
    rng = random.Random(SEED)

    by_cat: dict[str, list[dict]] = defaultdict(list)
    for item in corpus:
        by_cat[item["gold_category"]].append(item)

    subset: list[dict] = []
    for cat, target in STRATA_TARGETS.items():
        pool = by_cat[cat]
        picked = stratified_sample(pool, target, rng)
        for x in picked:
            x_out = {
                "corpus_id": x["corpus_id"],
                "pmid": x["pmid"],
                "title": x["title"],
                "abstract": x["abstract"],
                "authors": x["authors"],
                "journal": x["journal"],
                "year": x["year"],
                "doi": x.get("doi", ""),
                "heuristic_category": x["gold_category"],
            }
            subset.append(x_out)

    rng.shuffle(subset)
    for i, x in enumerate(subset, start=1):
        x["labeling_id"] = f"LBL-{i:03d}"

    out = {
        "metadata": {
            "version": "1.0",
            "n_total": len(subset),
            "strata": STRATA_TARGETS,
            "stratification": "category x year_tertile",
            "seed": SEED,
            "source_corpus": str(CORPUS_PATH.relative_to(ROOT)),
            "purpose": "dual-human labeling for kappa estimation",
        },
        "items": subset,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False))

    from collections import Counter
    cat_count = Counter(x["heuristic_category"] for x in subset)
    year_count = Counter(x["year"] for x in subset)
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Total: {len(subset)}")
    print(f"By category: {dict(cat_count)}")
    print(f"Year range: {min(year_count)}-{max(year_count)}")


if __name__ == "__main__":
    main()
