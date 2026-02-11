# Search Strategy Documentation

**Date:** 2026-02-11
**Type:** Systematic (multi-domain, 3 concept blocks)
**Databases:** PubMed, Scopus, Web of Science, Google Scholar, arXiv, medRxiv

---

## Search Terms and MeSH Terms

### Concept Block 1: PM2.5 / Air Pollution Exposure

```yaml
concept_1:
  label: "PM2.5 / Fine Particulate Matter"
  mesh_terms:
    - "Particulate Matter"[MeSH]
    - "Air Pollution"[MeSH]
    - "Environmental Exposure"[MeSH]
  free_text:
    - PM2.5
    - "fine particulate matter"
    - "fine particles"
    - "ambient particulate matter"
    - "particulate air pollution"
```

### Concept Block 2: Respiratory Hospitalizations

```yaml
concept_2:
  label: "Respiratory Hospitalizations / ED Visits"
  mesh_terms:
    - "Hospitalization"[MeSH]
    - "Respiratory Tract Diseases"[MeSH]
  free_text:
    - "hospital admission*"
    - hospitalization
    - "emergency department"
    - "ED visit*"
    - respiratory
    - asthma
    - COPD
    - pneumonia
    - bronchiolitis
```

### Concept Block 3: Time-Series / Epidemiological Design

```yaml
concept_3:
  label: "Time-Series / Case-Crossover Design"
  mesh_terms: []  # No formal MeSH term for time-series design
  free_text:
    - "time series"
    - "time-series"
    - "case-crossover"
    - "distributed lag"
    - "Poisson regression"
    - GAM
    - "generalized additive model"
```

---

## Search Strings by Database

### PubMed (Primary)

```
("Particulate Matter"[MeSH] OR "PM2.5" OR "fine particulate matter")
AND ("Hospitalization"[MeSH] OR "hospital admission*" OR "emergency department")
AND ("Respiratory Tract Diseases"[MeSH] OR "respiratory" OR "asthma" OR "COPD" OR "pneumonia")
AND ("time series" OR "case-crossover" OR "distributed lag")
```

**Results (2026-02-11):**

| Query Variant | Count |
|---------------|-------|
| Broad: PM2.5 AND respiratory AND hospitalization | ~875 |
| MeSH controlled | ~697 |
| With study design filter | ~169 |

### Scopus

```
TITLE-ABS-KEY("PM2.5" OR "fine particulate matter")
AND TITLE-ABS-KEY("hospitalization" OR "hospital admission" OR "emergency department")
AND TITLE-ABS-KEY("respiratory" OR "asthma" OR "COPD")
AND TITLE-ABS-KEY("time series" OR "case-crossover")
AND PUBYEAR > 2004
```

### Web of Science

```
TS=("PM2.5" OR "fine particulate matter")
AND TS=("hospitalization" OR "hospital admission")
AND TS=("respiratory" OR "asthma" OR "COPD")
AND TS=("time series" OR "case-crossover")
Timespan: 2005-2026
```

---

## Additional Searches: LLM + Evidence Synthesis

### PubMed

```
("large language model*" OR "LLM" OR "ChatGPT" OR "GPT-4" OR "Claude")
AND ("systematic review" OR "meta-analysis" OR "evidence synthesis")
AND ("screening" OR "data extraction" OR "abstract screening")
```

### arXiv / medRxiv

```
"large language model" AND ("systematic review" OR "evidence synthesis")
AND ("reproducibility" OR "non-determinism" OR "variability")
```

---

## Eligibility Criteria

### For PM2.5 Corpus (500 abstracts)

```yaml
inclusion:
  - "Original epidemiological study (not review/editorial)"
  - "Exposure: PM2.5 or fine particulate matter (<=2.5 um)"
  - "Outcome: respiratory hospitalization or ED visit"
  - "Design: time-series, case-crossover, or ecological"
  - "Reports RR, OR, HR, or equivalent with CI"
  - "Published in English"
  - "Published 2005-2026"

exclusion:
  - "Reviews, meta-analyses, editorials, commentaries"
  - "Animal or in-vitro studies"
  - "No quantitative effect estimate"
  - "PM10-only without PM2.5 analysis"
  - "Mortality-only without morbidity/hospitalization"
```

### Gold Standard Classification Target

| Category | Target n | Criteria |
|----------|----------|---------|
| Clearly include | 100 | Meets ALL inclusion criteria unambiguously |
| Clearly exclude | 100 | Fails >= 2 inclusion criteria clearly |
| Ambiguous | 300 | Borderline on exposure, outcome, or design; partially meets criteria |

---

## Estimated PRISMA Flow (Preliminary)

```
Identification:
  PubMed broad:          ~875
  Scopus:                ~600 (estimated)
  Web of Science:        ~400 (estimated)
  Other sources:         ~50
  TOTAL:                 ~1,925

Screening:
  After deduplication:   ~1,200 (estimated)
  Title screening:       ~1,200 → ~800 retained
  Abstract screening:    ~800 → ~500 for corpus

Corpus composition:
  Selected for study:    500 abstracts
  (100 include + 100 exclude + 300 ambiguous)
```

---

*Search Strategy v1.0 — Literature Specialist*
*Date: 2026-02-11*
