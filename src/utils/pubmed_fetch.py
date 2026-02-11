"""
PubMed E-utilities fetcher for PM2.5/respiratory corpus construction.

Uses NCBI E-utilities (esearch + efetch) via urllib — no extra dependencies.
Respects NCBI rate limits (3 req/s without API key, 10 req/s with).

Usage:
    python -m src.utils.pubmed_fetch --output data/corpus/raw/pubmed_raw.json
"""

import json
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# Rate limit: 3 requests/sec without API key
REQUEST_DELAY = 0.35

# PubMed query for PM2.5 + respiratory hospitalizations + time-series
QUERY_BROAD = (
    '("Particulate Matter"[MeSH] OR "PM2.5" OR "fine particulate matter" '
    'OR "fine particles" OR "ambient particulate matter") '
    'AND ("Hospitalization"[MeSH] OR "hospital admission" OR "hospital admissions" '
    'OR "emergency department" OR "ED visit" OR "ED visits") '
    'AND ("Respiratory Tract Diseases"[MeSH] OR "respiratory" OR "asthma" '
    'OR "COPD" OR "pneumonia" OR "bronchitis" OR "bronchiolitis") '
    'AND ("time series" OR "time-series" OR "case-crossover" '
    'OR "distributed lag" OR "Poisson regression" OR "GAM" '
    'OR "generalized additive model")'
)

# Narrower query for design-filtered results
QUERY_DESIGN = (
    '("PM2.5" OR "fine particulate matter" OR "particulate matter 2.5") '
    'AND ("respiratory" OR "asthma" OR "COPD" OR "pneumonia") '
    'AND ("hospitalization" OR "hospital admission" OR "emergency department") '
    'AND ("time series" OR "time-series" OR "case-crossover")'
)


def esearch(query: str, retmax: int = 2000, api_key: Optional[str] = None) -> list[str]:
    """Search PubMed and return list of PMIDs."""
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": str(retmax),
        "retmode": "json",
        "sort": "relevance",
    }
    if api_key:
        params["api_key"] = api_key

    url = f"{ESEARCH_URL}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read().decode())

    result = data.get("esearchresult", {})
    count = int(result.get("count", 0))
    pmids = result.get("idlist", [])
    print(f"  esearch: {count} total results, fetched {len(pmids)} PMIDs")
    return pmids


def efetch_batch(pmids: list[str], api_key: Optional[str] = None) -> list[dict]:
    """Fetch article details for a batch of PMIDs (max 200 per request)."""
    articles = []
    batch_size = 200

    for i in range(0, len(pmids), batch_size):
        batch = pmids[i:i + batch_size]
        params = {
            "db": "pubmed",
            "id": ",".join(batch),
            "rettype": "xml",
            "retmode": "xml",
        }
        if api_key:
            params["api_key"] = api_key

        url = f"{EFETCH_URL}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url, timeout=60) as resp:
            xml_data = resp.read().decode()

        articles.extend(_parse_pubmed_xml(xml_data))
        print(f"  efetch: batch {i // batch_size + 1}, "
              f"fetched {len(batch)} articles (total: {len(articles)})")
        time.sleep(REQUEST_DELAY)

    return articles


def _parse_pubmed_xml(xml_str: str) -> list[dict]:
    """Parse PubMed XML to extract article metadata."""
    articles = []
    root = ET.fromstring(xml_str)

    for article_elem in root.findall(".//PubmedArticle"):
        try:
            art = _parse_single_article(article_elem)
            if art:
                articles.append(art)
        except Exception as e:
            pmid_el = article_elem.find(".//PMID")
            pmid = pmid_el.text if pmid_el is not None else "unknown"
            print(f"  WARNING: failed to parse PMID {pmid}: {e}")

    return articles


def _parse_single_article(elem) -> Optional[dict]:
    """Parse a single PubmedArticle XML element."""
    # PMID
    pmid_el = elem.find(".//PMID")
    if pmid_el is None:
        return None
    pmid = pmid_el.text

    # Title
    title_el = elem.find(".//ArticleTitle")
    title = title_el.text if title_el is not None else ""
    # Handle mixed content (italic tags etc.)
    if title_el is not None and title_el.text is None:
        title = ET.tostring(title_el, encoding="unicode", method="text").strip()

    # Abstract
    abstract_parts = []
    for abs_el in elem.findall(".//AbstractText"):
        label = abs_el.get("Label", "")
        text = ET.tostring(abs_el, encoding="unicode", method="text").strip()
        if label:
            abstract_parts.append(f"{label}: {text}")
        else:
            abstract_parts.append(text)
    abstract = " ".join(abstract_parts)

    # Skip if no abstract
    if not abstract.strip():
        return None

    # Authors
    authors = []
    for author_el in elem.findall(".//Author"):
        last = author_el.find("LastName")
        fore = author_el.find("ForeName")
        if last is not None:
            name = last.text
            if fore is not None:
                name = f"{last.text} {fore.text}"
            authors.append(name)

    # Journal
    journal_el = elem.find(".//Journal/Title")
    journal = journal_el.text if journal_el is not None else ""

    # Year
    year_el = elem.find(".//PubDate/Year")
    if year_el is None:
        year_el = elem.find(".//PubDate/MedlineDate")
    year = year_el.text[:4] if year_el is not None else ""

    # DOI
    doi = ""
    for id_el in elem.findall(".//ArticleId"):
        if id_el.get("IdType") == "doi":
            doi = id_el.text
            break

    # MeSH terms
    mesh_terms = []
    for mesh_el in elem.findall(".//MeshHeading/DescriptorName"):
        mesh_terms.append(mesh_el.text)

    # Publication type
    pub_types = []
    for pt_el in elem.findall(".//PublicationType"):
        pub_types.append(pt_el.text)

    # Keywords
    keywords = []
    for kw_el in elem.findall(".//Keyword"):
        if kw_el.text:
            keywords.append(kw_el.text)

    return {
        "pmid": pmid,
        "title": title,
        "abstract": abstract,
        "authors": authors,
        "journal": journal,
        "year": year,
        "doi": doi,
        "mesh_terms": mesh_terms,
        "pub_types": pub_types,
        "keywords": keywords,
    }


def fetch_corpus(
    query: str = QUERY_BROAD,
    retmax: int = 2000,
    output_path: Optional[str] = None,
    api_key: Optional[str] = None,
) -> list[dict]:
    """Full pipeline: search + fetch + deduplicate + save."""
    print(f"=== PubMed Corpus Fetch ===")
    print(f"Query: {query[:100]}...")
    print()

    # Step 1: Search
    print("[1/3] Searching PubMed...")
    pmids = esearch(query, retmax=retmax, api_key=api_key)
    if not pmids:
        print("ERROR: No results found.")
        return []

    # Step 2: Fetch details
    print(f"\n[2/3] Fetching {len(pmids)} article details...")
    articles = efetch_batch(pmids, api_key=api_key)

    # Step 3: Deduplicate by PMID
    seen = set()
    unique = []
    for art in articles:
        if art["pmid"] not in seen:
            seen.add(art["pmid"])
            unique.append(art)
    print(f"\n[3/3] Deduplication: {len(articles)} → {len(unique)} unique articles")

    # Save
    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(unique, f, indent=2, ensure_ascii=False)
        print(f"\nSaved {len(unique)} articles to {output_path}")

    return unique


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Fetch PM2.5 abstracts from PubMed")
    parser.add_argument(
        "--output", "-o",
        default="data/corpus/raw/pubmed_raw.json",
        help="Output JSON path",
    )
    parser.add_argument(
        "--query", "-q",
        choices=["broad", "design"],
        default="broad",
        help="Query type: 'broad' (default) or 'design' (stricter)",
    )
    parser.add_argument(
        "--retmax", "-n",
        type=int,
        default=2000,
        help="Maximum PMIDs to retrieve (default: 2000)",
    )
    args = parser.parse_args()

    api_key = os.environ.get("NCBI_API_KEY")
    query = QUERY_BROAD if args.query == "broad" else QUERY_DESIGN

    articles = fetch_corpus(
        query=query,
        retmax=args.retmax,
        output_path=args.output,
        api_key=api_key,
    )
    print(f"\nDone. Total articles with abstracts: {len(articles)}")
