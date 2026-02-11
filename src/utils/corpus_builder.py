"""
Corpus Builder — Classify and select 500 abstracts for the study.

Heuristic classification based on inclusion/exclusion criteria:
  - Clearly Include (100): PM2.5 + respiratory hospitalization + time-series + effect estimate
  - Clearly Exclude (100): Reviews, PM10-only, mortality-only, cardiovascular, non-English
  - Ambiguous (300): Partial matches — borderline exposure, outcome, or design

Usage:
    python -m src.utils.corpus_builder
"""

import json
import re
import hashlib
from pathlib import Path
from datetime import datetime, timezone

# ── Keyword patterns for classification ──────────────────────────

# Exposure: PM2.5
PAT_PM25 = re.compile(
    r'\bPM\s*2\.?5\b|fine\s+particulate\s+matter|'
    r'particulate\s+matter\s+2\.5|PM₂\.₅',
    re.IGNORECASE,
)
PAT_PM10_ONLY = re.compile(
    r'\bPM\s*10\b|coarse\s+particulate',
    re.IGNORECASE,
)

# Outcome: Respiratory hospitalization
PAT_RESPIRATORY = re.compile(
    r'respiratory|asthma|COPD|chronic\s+obstructive|pneumonia|'
    r'bronchit|bronchiolitis|wheez|lung\s+disease',
    re.IGNORECASE,
)
PAT_HOSPITALIZATION = re.compile(
    r'hospital\s*(?:ization|admission|visit)|'
    r'emergency\s+department|ED\s+visit|'
    r'emergency\s+room|inpatient|'
    r'hospital\s+(?:discharge|record)',
    re.IGNORECASE,
)
PAT_MORTALITY = re.compile(
    r'mortality|death|fatal|survival\s+analysis',
    re.IGNORECASE,
)

# Design: Time-series / case-crossover
PAT_TIMESERIES = re.compile(
    r'time[\s-]series|case[\s-]crossover|distributed\s+lag|'
    r'Poisson\s+regression|GAM\b|generalized\s+additive|'
    r'DLNM|time[\s-]stratified',
    re.IGNORECASE,
)

# Effect estimate
PAT_EFFECT = re.compile(
    r'relative\s+risk|RR\b|odds\s+ratio|OR\b|hazard\s+ratio|HR\b|'
    r'risk\s+ratio|percent\s+(?:change|increase)|'
    r'(?:95|90)\s*%?\s*(?:CI|confidence\s+interval)|'
    r'per\s+\d+\s*(?:µg|ug|μg)/m[³3]',
    re.IGNORECASE,
)

# Exclusion patterns
PAT_REVIEW = re.compile(
    r'systematic\s+review|meta[\s-]analysis|scoping\s+review|'
    r'narrative\s+review|umbrella\s+review|literature\s+review',
    re.IGNORECASE,
)
PAT_ANIMAL = re.compile(
    r'\bmice\b|\brats?\b|\bmurine\b|in[\s-]vitro|cell\s+line|'
    r'\banimal\b.*\bmodel\b',
    re.IGNORECASE,
)
PAT_CARDIOVASCULAR = re.compile(
    r'cardiovascular|cardiac|myocardial\s+infarction|stroke|'
    r'heart\s+failure|coronary|ischemic\s+heart',
    re.IGNORECASE,
)


def classify_abstract(article: dict) -> dict:
    """
    Classify an article as include/exclude/ambiguous.
    Returns classification with scores and reasons.
    """
    text = f"{article.get('title', '')} {article.get('abstract', '')}"
    pub_types = " ".join(article.get("pub_types", []))
    mesh = " ".join(article.get("mesh_terms", []))
    full_text = f"{text} {pub_types} {mesh}"

    # Score each criterion
    has_pm25 = bool(PAT_PM25.search(text))
    has_pm10_only = bool(PAT_PM10_ONLY.search(text)) and not has_pm25
    has_respiratory = bool(PAT_RESPIRATORY.search(text))
    has_hospitalization = bool(PAT_HOSPITALIZATION.search(text))
    has_mortality_only = bool(PAT_MORTALITY.search(text)) and not has_hospitalization
    has_timeseries = bool(PAT_TIMESERIES.search(full_text))
    has_effect = bool(PAT_EFFECT.search(text))
    is_review = bool(PAT_REVIEW.search(full_text)) or "Review" in pub_types
    is_animal = bool(PAT_ANIMAL.search(text))
    has_cardiovascular = bool(PAT_CARDIOVASCULAR.search(text)) and not has_respiratory

    # Inclusion score (0-5)
    inclusion_score = sum([
        has_pm25,
        has_respiratory,
        has_hospitalization,
        has_timeseries,
        has_effect,
    ])

    # Exclusion flags
    exclusion_reasons = []
    if is_review:
        exclusion_reasons.append("review/meta-analysis")
    if is_animal:
        exclusion_reasons.append("animal/in-vitro")
    if has_pm10_only:
        exclusion_reasons.append("PM10-only")
    if has_mortality_only:
        exclusion_reasons.append("mortality-only")
    if has_cardiovascular:
        exclusion_reasons.append("cardiovascular-only")

    # Classification logic
    if exclusion_reasons:
        category = "exclude"
    elif inclusion_score >= 4:
        category = "include"
    elif inclusion_score >= 2:
        category = "ambiguous"
    else:
        category = "exclude"

    return {
        "category": category,
        "inclusion_score": inclusion_score,
        "criteria": {
            "pm25": has_pm25,
            "respiratory": has_respiratory,
            "hospitalization": has_hospitalization,
            "timeseries": has_timeseries,
            "effect_estimate": has_effect,
        },
        "exclusion_reasons": exclusion_reasons,
    }


def build_corpus(
    broad_path: str = "data/corpus/raw/pubmed_broad.json",
    design_path: str = "data/corpus/raw/pubmed_design.json",
    exclude_path: str = "data/corpus/raw/pubmed_exclude_candidates.json",
    output_path: str = "data/corpus/corpus_500.json",
    target_include: int = 100,
    target_exclude: int = 100,
    target_ambiguous: int = 300,
):
    """Build the final 500-abstract corpus."""
    print("=== Corpus Builder ===\n")

    # Load all sources
    articles_by_pmid = {}

    for path_str, label in [
        (broad_path, "broad"),
        (design_path, "design"),
        (exclude_path, "exclude_candidates"),
    ]:
        path = Path(path_str)
        if not path.exists():
            print(f"WARNING: {path} not found, skipping")
            continue
        with open(path) as f:
            data = json.load(f)
        for art in data:
            pmid = art["pmid"]
            if pmid not in articles_by_pmid:
                art["_source"] = label
                articles_by_pmid[pmid] = art
            else:
                # Track all sources
                existing = articles_by_pmid[pmid].get("_source", "")
                if label not in existing:
                    articles_by_pmid[pmid]["_source"] = f"{existing}+{label}"

    print(f"Total unique articles: {len(articles_by_pmid)}")

    # Classify all
    includes = []
    excludes = []
    ambiguous = []

    for pmid, art in articles_by_pmid.items():
        classification = classify_abstract(art)
        art["_classification"] = classification

        cat = classification["category"]
        if cat == "include":
            includes.append(art)
        elif cat == "exclude":
            excludes.append(art)
        else:
            ambiguous.append(art)

    print(f"\nClassification results:")
    print(f"  Include:   {len(includes)}")
    print(f"  Exclude:   {len(excludes)}")
    print(f"  Ambiguous: {len(ambiguous)}")

    # Sort by inclusion score (highest first for include, lowest for exclude)
    includes.sort(key=lambda x: x["_classification"]["inclusion_score"], reverse=True)
    excludes.sort(key=lambda x: len(x["_classification"]["exclusion_reasons"]), reverse=True)
    ambiguous.sort(key=lambda x: x["_classification"]["inclusion_score"], reverse=True)

    # Select target counts
    selected_includes = includes[:target_include]
    selected_excludes = excludes[:target_exclude]
    selected_ambiguous = ambiguous[:target_ambiguous]

    # If we need more ambiguous, promote from lower-scoring includes or higher-scoring excludes
    deficit_ambiguous = target_ambiguous - len(selected_ambiguous)
    if deficit_ambiguous > 0:
        # Move borderline includes (score=4) to ambiguous
        overflow_includes = includes[target_include:]
        for art in overflow_includes[:deficit_ambiguous]:
            art["_classification"]["category"] = "ambiguous"
            art["_classification"]["_reclassified"] = "from_include_overflow"
            selected_ambiguous.append(art)
        deficit_ambiguous = target_ambiguous - len(selected_ambiguous)

    if deficit_ambiguous > 0:
        # Move borderline excludes (1 exclusion reason only) to ambiguous
        overflow_excludes = excludes[target_exclude:]
        borderline_excludes = [
            e for e in overflow_excludes
            if len(e["_classification"]["exclusion_reasons"]) == 1
        ]
        for art in borderline_excludes[:deficit_ambiguous]:
            art["_classification"]["category"] = "ambiguous"
            art["_classification"]["_reclassified"] = "from_exclude_overflow"
            selected_ambiguous.append(art)

    # Deficit check for includes
    deficit_include = target_include - len(selected_includes)
    if deficit_include > 0:
        # Promote top ambiguous to include
        for art in ambiguous[len(selected_ambiguous):len(selected_ambiguous) + deficit_include]:
            art["_classification"]["category"] = "include"
            art["_classification"]["_reclassified"] = "promoted_from_ambiguous"
            selected_includes.append(art)

    # Deficit check for excludes
    deficit_exclude = target_exclude - len(selected_excludes)
    if deficit_exclude > 0:
        print(f"WARNING: only {len(selected_excludes)} exclude candidates available "
              f"(need {target_exclude})")

    print(f"\nFinal selection:")
    print(f"  Include:   {len(selected_includes)} / {target_include}")
    print(f"  Exclude:   {len(selected_excludes)} / {target_exclude}")
    print(f"  Ambiguous: {len(selected_ambiguous)} / {target_ambiguous}")

    total = len(selected_includes) + len(selected_excludes) + len(selected_ambiguous)
    print(f"  TOTAL:     {total} / {target_include + target_exclude + target_ambiguous}")

    # Build final corpus
    corpus = []
    for idx, (category_list, category_label) in enumerate([
        (selected_includes, "include"),
        (selected_excludes, "exclude"),
        (selected_ambiguous, "ambiguous"),
    ]):
        for art in category_list:
            # Compute content hash for provenance
            content_str = f"{art['pmid']}|{art['title']}|{art['abstract']}"
            content_hash = hashlib.sha256(content_str.encode()).hexdigest()[:16]

            corpus.append({
                "corpus_id": f"ABS-{len(corpus) + 1:04d}",
                "pmid": art["pmid"],
                "title": art["title"],
                "abstract": art["abstract"],
                "authors": art.get("authors", []),
                "journal": art.get("journal", ""),
                "year": art.get("year", ""),
                "doi": art.get("doi", ""),
                "gold_category": category_label,
                "classification": {
                    "inclusion_score": art["_classification"]["inclusion_score"],
                    "criteria_met": art["_classification"]["criteria"],
                    "exclusion_reasons": art["_classification"]["exclusion_reasons"],
                },
                "content_hash": content_hash,
            })

    # Metadata
    metadata = {
        "created": datetime.now(timezone.utc).isoformat(),
        "version": "1.0",
        "total": len(corpus),
        "composition": {
            "include": len(selected_includes),
            "exclude": len(selected_excludes),
            "ambiguous": len(selected_ambiguous),
        },
        "sources": {
            "pubmed_broad": broad_path,
            "pubmed_design": design_path,
            "pubmed_exclude": exclude_path,
        },
        "classification_method": "heuristic_keyword_matching_v1",
        "note": "Gold standard labels are PRELIMINARY (heuristic). "
                "Final labels require dual-human review.",
    }

    output = {
        "metadata": metadata,
        "corpus": corpus,
    }

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nCorpus saved to {output_path}")
    print(f"SHA-256: {hashlib.sha256(json.dumps(output, sort_keys=True).encode()).hexdigest()[:16]}")

    # Summary stats
    years = [a.get("year", "") for a in corpus if a.get("year")]
    if years:
        print(f"\nYear range: {min(years)} - {max(years)}")
    journals = set(a.get("journal", "") for a in corpus if a.get("journal"))
    print(f"Unique journals: {len(journals)}")

    return output


if __name__ == "__main__":
    build_corpus()
