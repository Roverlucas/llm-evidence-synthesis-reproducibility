# Validity Threat Assessment — paper-2026-002

**Agent:** @methodology-specialist
**Date:** 2026-02-11

---

## Internal Validity: MEDIUM-HIGH

| # | Threat | Severity | Mitigation | Residual |
|---|--------|----------|------------|----------|
| V1 | Gold standard error | HIGH | Dual labelers + resolution + kappa | MEDIUM |
| V2 | Model version drift during experiment | HIGH | Narrow execution window + version hashing | LOW |
| V3 | API rate limit / throttling effects | LOW | Exponential backoff + timestamps | LOW |
| V4 | Abstract order effects | LOW | Fixed order + shuffle sensitivity test | LOW |
| V8 | Confounding by response time (latency → different server load) | LOW | Log latency; check correlation with output variation | LOW |
| V9 | Gold standard extraction subjectivity | MEDIUM | Pre-defined protocol; prefer primary estimate | LOW |
| V10 | Temporal confound (API behavior change) | MEDIUM | Narrow window; timestamps; drift check | LOW |

**Assessment:** Most threats are well-controlled. V1 (gold standard quality) is the
most significant residual threat — the entire study depends on a reliable ground truth.

---

## External Validity: MEDIUM

| # | Threat | Severity | Mitigation | Residual |
|---|--------|----------|------------|----------|
| V5 | Single domain (PM2.5 only) | MEDIUM | Chosen for standardization; acknowledged as limitation | MEDIUM |
| E1 | Single language (English abstracts only) | LOW | PM2.5 literature is predominantly English | LOW |
| E2 | Three models (not all LLMs) | MEDIUM | Covers local + 2 major API providers; representative not exhaustive | MEDIUM |
| E3 | Abstract-only (no full-text) | MEDIUM | Mirrors rapid screening practice; acknowledged | MEDIUM |
| E4 | 2026 snapshot (models evolve rapidly) | MEDIUM | Version documentation; findings are lower-bound estimate | MEDIUM |

**Assessment:** Results directly apply to PM2.5/respiratory time-series reviews using
these 3 models. Broader generalization is plausible but not confirmed — acknowledged as
primary limitation.

---

## Construct Validity: MEDIUM

| # | Threat | Severity | Mitigation | Residual |
|---|--------|----------|------------|----------|
| V6 | Single prompt (construct underrepresentation) | MEDIUM | Based on systematic review criteria; acknowledged | MEDIUM |
| C1 | Flip rate as proxy for instability | LOW | Directly measures decision change; well-defined | LOW |
| C2 | CI-crossing-null as proxy for "conclusion change" | LOW | Standard interpretation in meta-analysis | LOW |
| C3 | EMR may not capture semantic equivalence | LOW | Supplement with RR absolute error | LOW |

**Assessment:** Metrics are well-aligned with constructs of interest. Single prompt is the
main construct validity concern.

---

## Statistical Conclusion Validity: HIGH

| # | Threat | Severity | Mitigation | Residual |
|---|--------|----------|------------|----------|
| V7 | 30 runs insufficient for rare events | LOW | 30 × 500 = 15,000 observations; bootstrap CIs | LOW |
| S1 | Multiple comparisons inflation | LOW | Bonferroni correction; pre-specified analyses | LOW |
| S2 | Non-normal distributions | LOW | Non-parametric tests throughout | LOW |
| S3 | Dependent observations (same abstracts across runs) | MEDIUM | Per-abstract analysis + cluster-aware bootstrap | LOW |

**Assessment:** Large observation count, non-parametric approach, and pre-registered
analyses minimize statistical conclusion threats.

---

## Summary Matrix

| Validity Type | Rating | Primary Threat | Residual Risk |
|---------------|--------|----------------|---------------|
| Internal | MEDIUM-HIGH | Gold standard quality (V1) | MEDIUM |
| External | MEDIUM | Single domain (V5) | MEDIUM |
| Construct | MEDIUM | Single prompt (V6) | MEDIUM |
| Statistical Conclusion | HIGH | Multiple comparisons (S1) | LOW |

---

## Limitations → Discussion Framing

| Limitation | Type | Severity | Discussion Framing |
|-----------|------|----------|-------------------|
| Single domain (PM2.5) | External | Medium | "Chosen for abundance and standardization; future work should replicate across domains" |
| Single prompt per stage | Construct | Medium | "Prompt sensitivity is an important future direction; our results are prompt-specific" |
| Three models | External | Medium | "Representative of local vs API paradigm; not exhaustive" |
| Gold standard subjectivity | Internal | Medium | "Mitigated by dual labeling (kappa = X); residual uncertainty acknowledged" |
| Abstract-only screening | External | Medium | "Mirrors common rapid screening practice; full-text would reduce ambiguity" |
| DerSimonian-Laird estimator | Statistical | Low | "Chosen for comparability with existing PM2.5 meta-analyses; alternatives noted" |

---

*Validity Assessment v1.0 — @methodology-specialist*
*Date: 2026-02-11*
