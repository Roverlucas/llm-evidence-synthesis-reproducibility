"""
Fetch articles that should be EXCLUDED from the corpus.
These are near-miss papers: PM10-only, mortality-only, reviews, non-English, etc.
Used to populate the "clearly exclude" category (100 abstracts).
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.utils.pubmed_fetch import fetch_corpus

# Query 1: PM10-only studies (no PM2.5)
QUERY_PM10_ONLY = (
    '("PM10" OR "coarse particulate") '
    'NOT ("PM2.5" OR "fine particulate") '
    'AND ("respiratory" OR "hospitalization") '
    'AND ("time series" OR "case-crossover")'
)

# Query 2: Mortality-only (no hospitalization)
QUERY_MORTALITY = (
    '("PM2.5" OR "fine particulate matter") '
    'AND ("mortality" OR "death") '
    'NOT ("hospitalization" OR "hospital admission" OR "emergency department") '
    'AND ("respiratory") '
    'AND ("time series" OR "case-crossover")'
)

# Query 3: Reviews and meta-analyses about PM2.5
QUERY_REVIEWS = (
    '("PM2.5" OR "fine particulate matter") '
    'AND ("respiratory" OR "hospitalization") '
    'AND ("systematic review"[Publication Type] OR "meta-analysis"[Publication Type] '
    'OR "review"[Publication Type])'
)

# Query 4: Non-respiratory outcomes (cardiovascular)
QUERY_CARDIOVASCULAR = (
    '("PM2.5" OR "fine particulate matter") '
    'AND ("cardiovascular" OR "cardiac" OR "stroke" OR "myocardial infarction") '
    'NOT ("respiratory" OR "asthma" OR "COPD" OR "pneumonia") '
    'AND ("hospitalization" OR "hospital admission") '
    'AND ("time series" OR "case-crossover")'
)


if __name__ == "__main__":
    api_key = os.environ.get("NCBI_API_KEY")
    all_exclude = []

    queries = [
        ("PM10-only", QUERY_PM10_ONLY, 150),
        ("Mortality-only", QUERY_MORTALITY, 150),
        ("Reviews", QUERY_REVIEWS, 150),
        ("Cardiovascular", QUERY_CARDIOVASCULAR, 150),
    ]

    for label, query, retmax in queries:
        print(f"\n{'='*60}")
        print(f"Fetching: {label}")
        print(f"{'='*60}")
        articles = fetch_corpus(
            query=query,
            retmax=retmax,
            api_key=api_key,
        )
        for art in articles:
            art["exclude_reason"] = label
        all_exclude.extend(articles)

    # Deduplicate
    seen = set()
    unique = []
    for art in all_exclude:
        if art["pmid"] not in seen:
            seen.add(art["pmid"])
            unique.append(art)

    print(f"\n{'='*60}")
    print(f"Total exclude candidates: {len(all_exclude)} → {len(unique)} unique")
    print(f"{'='*60}")

    out_path = Path("data/corpus/raw/pubmed_exclude_candidates.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)
    print(f"Saved to {out_path}")
