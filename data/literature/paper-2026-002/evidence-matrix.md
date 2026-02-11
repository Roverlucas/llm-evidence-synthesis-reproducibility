# Evidence Matrix

**Project:** paper-2026-002
**Date:** 2026-02-11
**Status:** Phase 1 — Initial mapping (to be expanded with full-text review)

---

## Domain 1: PM2.5 and Respiratory Hospitalizations (Meta-Analyses)

| Ref ID | Authors | Year | Journal | Design | Key Finding | RR per 10 µg/m³ | Quality | Relevance |
|--------|---------|------|---------|--------|-------------|------------------|---------|-----------|
| MA-01 | Atkinson et al. | 2014 | Thorax | SR + MA | Respiratory mortality +1.51% per 10 µg/m³ PM2.5 | 1.0151 [1.0101, 1.0201] | High | High |
| MA-02 | Zheng et al. | 2015 | PLOS ONE | SR + MA | Asthma ER/admissions +2.3% per 10 µg/m³ | 1.023 [1.015, 1.031] | High | High |
| MA-03 | Lim et al. | 2016 | JPMPH | SR + MA | Children's asthma admissions +4.8% | 1.048 [1.028, 1.067] | High | High |
| MA-04 | Delavar et al. | 2023 | BMC Public Health | SR + MA | COPD hospitalization +1.6%, high heterogeneity I²=94.86% | 1.016 [1.004, 1.029] | High | High |
| MA-05 | Orellano et al. | 2020 | Environ Int | SR + MA | All-cause mortality +0.65% (WHO guideline source) | 1.0065 [1.0044, 1.0086] | High | Medium |
| MA-06 | Luo et al. | 2023 | (China-specific) | SR + MA | Respiratory morbidity +0.96% (China, 145 studies) | ~1.0096 | High | Medium |
| MA-07 | Nhung et al. | 2017 | Environ Pollution | SR | Short-term PM2.5 and hospital admissions | varies | High | High |
| MA-08 | Boonvisut & Shinyama | 2023 | Atmosphere | Scoping | 138 time-series studies identified (2016-2021) | varies | Medium | High |

**Consensus:** Short-term RR per 10 µg/m³ PM2.5 for all-respiratory admissions: **~1.01-1.02** (1-2% increase). Children/asthma: 2-5%. COPD: ~1.6%.

---

## Domain 2: LLM-Assisted Abstract Screening

| Ref ID | Authors | Year | Journal | LLM | Domain | Key Finding | Accuracy | Relevance |
|--------|---------|------|---------|-----|--------|-------------|----------|-----------|
| SC-01 | Guo et al. | 2024 | JMIR | GPT-3.5/4 | Clinical | 24K abstracts, accuracy 0.91, sensitivity 0.76 | 0.91 | High |
| SC-02 | Li et al. | 2024 | Systematic Reviews | GPT-4o | Biomedical | Accuracy ≥0.90 consistently | 0.913 | High |
| SC-03 | Khraisha et al. | 2024 | Res Synth Methods | GPT-4 | Multi-language | Screening: none to moderate agreement after adjustment | Moderate | High |
| SC-04 | Oami et al. | 2024 | JAMA Net Open | LLM | Sepsis guidelines | Prospective diagnostic study | Varies | Medium |
| SC-05 | Dennstaedt et al. | 2024 | Systematic Reviews | Open LLMs | Biomedical | 4 models tested; sensitivity 82%, minor prompt changes → big impact | 0.82 | High |
| SC-06 | Krag et al. | 2024 | medRxiv | GPT-4o, Claude-3 | Clinical | 97-98% accuracy; dual-LLM+human achieves 91% automation | 0.97 | High |
| SC-07 | Lieberum et al. | 2025 | J Clin Epidemiol | GPT (89%) | All | Scoping review: 37 articles; half promising, half neutral | N/A | High |

---

## Domain 3: LLM-Assisted Data Extraction

| Ref ID | Authors | Year | Journal | LLM | Key Finding | Accuracy | Relevance |
|--------|---------|------|---------|-----|-------------|----------|-----------|
| EX-01 | Khan et al. | 2025 | JAMIA | GPT-4-turbo, Claude-3-Opus | Collaborative extraction: 51% discordants resolved, accuracy 0.76 | 0.76 | High |
| EX-02 | Annals of Internal Medicine | 2025 | Ann Intern Med | Claude 2.1/3.0/3.5 | AI-assisted: 91% accuracy vs 89% human; -41 min/study | 0.91 | High |
| EX-03 | Schmidt et al. | 2024 | arXiv | GPT-4 | ~80% accuracy (82% clinical, 72% social science) | 0.80 | High |
| EX-04 | TrialMind | 2025 | npj Digital Medicine | LLM pipeline | +71.4% recall, -44.2% screening time, +23.5% extraction accuracy | High | High |
| EX-05 | npj Digital Medicine | 2025 | npj Digital Medicine | Claude-3.5-Sonnet | 96.2% accuracy on complementary medicine trials | 0.962 | High |
| EX-06 | PMC 2025 | 2025 | PMC | GPT-4o | High concordance with original meta-analyses; CI discrepancies noted | High | High |

---

## Domain 4: LLM Non-Determinism and Reproducibility

| Ref ID | Authors | Year | Journal | Key Finding | Relevance |
|--------|---------|------|---------|-------------|-----------|
| ND-01 | Atil et al. | 2024 | arXiv | 5 LLMs, "deterministic" settings: accuracy varies up to 15%, best-to-worst gap 70% | **Critical** |
| ND-02 | Yuan et al. | 2025 | arXiv/NeurIPS | Numerical precision causes non-determinism; batch size, GPU count affect outputs; proposes LayerCast | **Critical** |
| ND-03 | Karelin et al. | 2025 | PhilSci-Archive | Transient chaos in transformers → significant output divergences; philosophical analysis | High |
| ND-04 | Heston & Khun | 2024 | Nature Medicine | 2,400 ICU cases: LLMs inconsistent across pathologies | Medium |
| ND-05 | Uncertainty Quant. | 2025 | arXiv | Stochastic generation → inconsistent medical outputs; Bayesian approaches proposed | High |

---

## Domain 5: LLM Variability Affecting Evidence Synthesis

| Ref ID | Authors | Year | Journal | Key Finding | Relevance |
|--------|---------|------|---------|-------------|-----------|
| VA-01 | Kuitunen et al. | 2024 | JEBM | GPT-4o RoB assessment: kappa=0.24 (slight); zero high-risk classifications | **Critical** |
| VA-02 | Taneri | 2025 | Cochrane CESM | GPT-4o vs human: kappa=0.51 (fair-moderate) on 84 RCTs across 8 reviews | **Critical** |
| VA-03 | Descamps et al. | 2025 | JEBM | Model update (4o → 4o-new): 38-point swing in agreement (80%→42%) | **Critical** |
| VA-04 | Minozzi et al. | 2024 | medRxiv | 157 trials, kappa=0.11-0.29 regardless of prompt engineering | High |
| VA-05 | Trevino-Juarez | 2024 | Med Sci Educator | GPT-4 agreement: 41.91%-80.93% across RoB domains | High |

---

## Domain 6: LLM + Environmental Health

| Ref ID | Authors | Year | Journal | Key Finding | Relevance |
|--------|---------|------|---------|-------------|-----------|
| EH-01 | Zuo et al. | 2025 | Environ Evidence | ChatGPT-3.5 fine-tuned for env. screening; kappa 0.53-0.84 | High |
| EH-02 | Nykvist et al. | 2025 | Environ Evidence | GPT-4: 100% recall, 50% time savings in env. SR | High |
| EH-03 | ACS Environ Au | 2024 | ACS Environ Au | GPT-4: precision 0.96, recall 1.00 in wastewater epidemiology | High |
| EH-04 | Berger-Tal et al. | 2024 | Trends Ecol Evol | AI for evidence synthesis in conservation; transparency needed | Medium |
| EH-05 | Taylor & Francis | 2025 | Front Toxicol | LLM data extraction in toxicology; hallucination risks flagged | Medium |

---

## Claims Support Map

| Claim | Supporting Refs | Contra Refs | Gap? | Evidence Level |
|-------|----------------|-------------|------|----------------|
| PM2.5 → respiratory hospitalization is well-established | MA-01 thru MA-08 | None | No | High (GRADE) |
| LLMs can screen abstracts with high accuracy | SC-01,02,06 | SC-03,05 (variability) | Partial | Moderate |
| LLM screening performance varies by prompt/model | SC-05, SC-06, VA-03 | None | No | Moderate |
| LLM data extraction achieves 80-96% accuracy | EX-01 thru EX-06 | None | No | Moderate |
| "Deterministic" LLM settings still produce variation | ND-01, ND-02 | None | No | Moderate |
| LLM variability can alter RoB/quality assessments | VA-01 thru VA-05 | None | No | Moderate |
| Model updates cause conclusion-changing shifts | VA-03 | None | No | Low (single study) |
| **No study has measured how LLM non-determinism propagates through a full evidence synthesis pipeline to alter meta-analytic conclusions** | — | — | **YES — PRIMARY GAP** | — |
| **No study has applied LLM screening/extraction to PM2.5/respiratory health specifically** | — | — | **YES** | — |
| **No study proposes provenance framework for LLM-assisted evidence synthesis** | — | — | **YES** | — |

---

*Evidence Matrix v1.0 — Literature Specialist*
*28 references mapped across 6 domains*
*3 primary gaps identified*
*Date: 2026-02-11*
