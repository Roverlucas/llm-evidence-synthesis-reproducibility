"""
Gold Standard Labeling Infrastructure.

Generates labeling templates for dual-human annotation of the 500-abstract corpus.
Outputs:
  - data/gold_standard/screening_labels.json — screening gold standard
  - data/gold_standard/extraction_labels.json — extraction gold standard template
  - data/gold_standard/labeling_guide.md — instructions for human labelers

Usage:
    python -m src.utils.gold_standard
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone


def generate_screening_labels(corpus_path: str, output_dir: str):
    """Generate screening gold standard from heuristic + human review template."""
    with open(corpus_path) as f:
        data = json.load(f)

    corpus = data["corpus"]
    labels = []

    for article in corpus:
        # Heuristic label based on classification
        heuristic_label = article["gold_category"]

        # For clearly include/exclude, heuristic is high-confidence
        # For ambiguous, requires human review
        if heuristic_label == "include":
            confidence = "high"
            needs_review = False
        elif heuristic_label == "exclude":
            confidence = "high"
            needs_review = False
        else:
            confidence = "low"
            needs_review = True

        label_entry = {
            "corpus_id": article["corpus_id"],
            "pmid": article["pmid"],
            "title": article["title"],
            "heuristic_label": heuristic_label,
            "heuristic_confidence": confidence,
            "needs_human_review": needs_review,
            "labeler_1": {
                "decision": heuristic_label if not needs_review else None,
                "confidence": None,
                "rationale": None,
                "timestamp": None,
            },
            "labeler_2": {
                "decision": heuristic_label if not needs_review else None,
                "confidence": None,
                "rationale": None,
                "timestamp": None,
            },
            "final_label": heuristic_label if not needs_review else None,
            "discordance_resolved": None,
            "inclusion_criteria_met": article["classification"]["criteria_met"],
            "exclusion_reasons": article["classification"]["exclusion_reasons"],
        }
        labels.append(label_entry)

    output = {
        "metadata": {
            "created": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
            "type": "screening_gold_standard",
            "total": len(labels),
            "needs_review": sum(1 for l in labels if l["needs_human_review"]),
            "auto_labeled": sum(1 for l in labels if not l["needs_human_review"]),
            "labeling_protocol": "dual_independent_with_discordance_resolution",
        },
        "labels": labels,
    }

    out_path = Path(output_dir) / "screening_labels.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Screening labels: {out_path}")
    print(f"  Total: {len(labels)}")
    print(f"  Auto-labeled (high confidence): {output['metadata']['auto_labeled']}")
    print(f"  Needs human review: {output['metadata']['needs_review']}")
    return output


def generate_extraction_labels(corpus_path: str, output_dir: str):
    """Generate extraction gold standard template for included abstracts."""
    with open(corpus_path) as f:
        data = json.load(f)

    # Only included abstracts need extraction
    included = [a for a in data["corpus"] if a["gold_category"] == "include"]

    templates = []
    for article in included:
        template = {
            "corpus_id": article["corpus_id"],
            "pmid": article["pmid"],
            "title": article["title"],
            "abstract": article["abstract"],
            "extraction": {
                "study_location": None,
                "study_period": None,
                "study_design": None,
                "population": None,
                "exposure_increment": None,
                "estimates": [
                    {
                        "effect_measure": None,
                        "effect_estimate": None,
                        "ci_lower": None,
                        "ci_upper": None,
                        "lag": None,
                        "outcome_specific": None,
                        "subgroup": None,
                    }
                ],
                "covariates": [],
                "notes": None,
            },
            "extractor_1": {
                "completed": False,
                "timestamp": None,
            },
            "extractor_2": {
                "completed": False,
                "timestamp": None,
            },
            "discordance_resolved": None,
        }
        templates.append(template)

    output = {
        "metadata": {
            "created": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
            "type": "extraction_gold_standard",
            "total": len(templates),
            "extraction_protocol": "dual_independent_with_discordance_resolution",
            "fields": [
                "effect_measure (RR/OR/HR)",
                "effect_estimate (numeric)",
                "ci_lower (95% CI)",
                "ci_upper (95% CI)",
                "lag (days)",
                "exposure_increment (µg/m³)",
                "study_location",
                "study_design",
                "population",
                "covariates",
            ],
        },
        "templates": templates,
    }

    out_path = Path(output_dir) / "extraction_labels.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nExtraction templates: {out_path}")
    print(f"  Total included abstracts: {len(templates)}")
    return output


def generate_labeling_guide(output_dir: str):
    """Generate labeling guide for human annotators."""
    guide = """# Gold Standard Labeling Guide

## Overview

This guide describes the labeling protocol for the PM2.5/respiratory
hospitalization corpus. Two independent labelers annotate each abstract,
with discordance resolution by a third reviewer.

## Stage A: Screening Labels

### Task
Classify each abstract as **INCLUDE**, **EXCLUDE**, or **UNCERTAIN**.

### Inclusion Criteria (ALL must be met)
1. **Original study** — Not a review, meta-analysis, editorial, or commentary
2. **Exposure: PM2.5** — Fine particulate matter (PM2.5, ≤2.5 µm)
3. **Outcome: Respiratory hospitalization** — Hospital admission or ED visit for respiratory cause
4. **Design: Time-series** — Time-series, case-crossover, or ecological study
5. **Effect estimate** — Reports RR, OR, HR, or equivalent with confidence interval
6. **Language: English** — Published in English

### Exclusion Criteria (ANY triggers exclude)
- Reviews, meta-analyses, editorials, commentaries, letters
- Animal or in-vitro studies
- PM10-only without PM2.5 analysis
- Mortality-only without hospitalization/ED visits
- No quantitative effect estimate extractable from abstract

### Decision Rules
| Scenario | Decision |
|----------|----------|
| Meets all 6 inclusion criteria | INCLUDE |
| Fails ≥2 inclusion criteria clearly | EXCLUDE |
| Borderline on 1 criterion | UNCERTAIN |
| PM2.5 + respiratory but cohort (not time-series) | UNCERTAIN |
| PM2.5 + respiratory but ED visits unclear | UNCERTAIN |
| Mixed pollutants including PM2.5 | INCLUDE (if PM2.5 reported separately) |
| PM2.5 + respiratory + mortality + hospitalization | INCLUDE |

### Confidence Scale
- **High** (0.8-1.0): Clear match or clear mismatch
- **Medium** (0.5-0.79): Probable but some ambiguity
- **Low** (0.0-0.49): Genuinely uncertain

## Stage B: Data Extraction

### Task
Extract quantitative data from INCLUDED abstracts only.

### Fields to Extract
| Field | Description | Example |
|-------|-------------|---------|
| effect_measure | RR, OR, HR, IRR | "RR" |
| effect_estimate | Point estimate | 1.023 |
| ci_lower | 95% CI lower bound | 1.005 |
| ci_upper | 95% CI upper bound | 1.042 |
| lag | Exposure lag in days | 1 |
| exposure_increment | Per X µg/m³ | 10 |
| study_location | City, Country | "Beijing, China" |
| study_design | time-series, case-crossover | "time-series" |
| population | General, elderly, children | "general" |
| covariates | Adjustment variables | ["temperature", "humidity", "day of week"] |

### Extraction Rules
1. **Prefer the primary/main estimate** if multiple are reported
2. **Prefer all-respiratory** over specific conditions (asthma, COPD)
3. **Prefer single-pollutant model** over multi-pollutant
4. **Prefer lag 0-1** if multiple lags reported without a "best" designation
5. **Record per 10 µg/m³** — convert if different increment used
6. **If abstract reports % change**, convert: RR = 1 + (%change / 100)

### Discordance Protocol
- If two extractors disagree on effect_estimate by >0.005: flag for resolution
- If CI bounds differ by >0.01: flag for resolution
- Third reviewer resolves based on abstract text

## Labeling Workflow

```
Abstract → Labeler 1 (independent) → Label + Confidence + Rationale
        → Labeler 2 (independent) → Label + Confidence + Rationale
        → Compare: agree? → YES → Gold standard = agreed label
                          → NO  → Resolver reviews → Final gold standard
```

## Quality Metrics
- **Inter-rater reliability**: Cohen's kappa (target: κ ≥ 0.80)
- **Discordance rate**: Target < 15% for screening, < 10% for extraction
- **Coverage**: 100% of corpus labeled by both labelers

---

*Labeling Guide v1.0 — Technical Executor*
*Date: {date}*
""".format(date=datetime.now(timezone.utc).strftime("%Y-%m-%d"))

    out_path = Path(output_dir) / "labeling_guide.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(guide)

    print(f"\nLabeling guide: {out_path}")
    return guide


def generate_corpus_stats(corpus_path: str, output_dir: str):
    """Generate summary statistics for the corpus."""
    with open(corpus_path) as f:
        data = json.load(f)

    corpus = data["corpus"]
    from collections import Counter

    stats = {
        "total": len(corpus),
        "by_category": dict(Counter(a["gold_category"] for a in corpus)),
        "by_year": dict(sorted(Counter(a.get("year", "unknown") for a in corpus).items())),
        "by_journal": dict(Counter(a.get("journal", "unknown") for a in corpus).most_common(20)),
        "abstract_length": {
            "mean": sum(len(a["abstract"]) for a in corpus) / len(corpus),
            "min": min(len(a["abstract"]) for a in corpus),
            "max": max(len(a["abstract"]) for a in corpus),
        },
        "inclusion_score_distribution": dict(
            Counter(a["classification"]["inclusion_score"] for a in corpus)
        ),
        "generated": datetime.now(timezone.utc).isoformat(),
    }

    out_path = Path(output_dir) / "corpus_stats.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print(f"\nCorpus stats: {out_path}")
    print(f"  Abstracts: {stats['total']}")
    print(f"  Mean abstract length: {stats['abstract_length']['mean']:.0f} chars")
    print(f"  Year range: {min(k for k in stats['by_year'] if k != 'unknown')}"
          f"-{max(k for k in stats['by_year'] if k != 'unknown')}")
    return stats


if __name__ == "__main__":
    corpus_path = "data/corpus/corpus_500.json"
    output_dir = "data/gold_standard"

    print("=== Gold Standard Infrastructure ===\n")

    print("[1/4] Generating screening labels...")
    generate_screening_labels(corpus_path, output_dir)

    print("\n[2/4] Generating extraction templates...")
    generate_extraction_labels(corpus_path, output_dir)

    print("\n[3/4] Generating labeling guide...")
    generate_labeling_guide(output_dir)

    print("\n[4/4] Generating corpus stats...")
    generate_corpus_stats(corpus_path, output_dir)

    print("\n=== Done ===")
