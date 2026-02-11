# Gold Standard Labeling Guide

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
*Date: 2026-02-11*
