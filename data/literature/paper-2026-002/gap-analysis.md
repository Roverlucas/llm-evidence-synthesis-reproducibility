# Gap Analysis Report

**Project:** paper-2026-002
**Date:** 2026-02-11
**Literature Specialist:** Phase 1 delivery

---

## Gap 1 (P0): No study measures how LLM non-determinism propagates through a full evidence synthesis pipeline

- **Type:** Evidência + Metodológica
- **Severity:** Alta
- **Evidence:**
  - Atil et al. (2024, ND-01): Documented up to 15% accuracy variation in "deterministic" LLM settings, but only measured task-level performance, not downstream pipeline effects
  - Descamps et al. (2025, VA-03): Showed model updates cause 38-point swings in RoB agreement, but did not trace to meta-analytic outcomes
  - Lieberum et al. (2025, SC-07): Scoping review of 37 articles flagged reproducibility as open concern but found zero studies quantifying propagation
  - Khan et al. (2025, EX-01): Showed 51% discordance in collaborative extraction but did not compute impact on pooled estimates
- **What's missing:** No study has connected the chain: screening variation → extraction variation → pooled effect variation → conclusion change
- **Our contribution:** We measure all four stages end-to-end, quantifying exactly how much non-determinism at each stage propagates to the final meta-analytic conclusion
- **Impact:** Directly addresses whether LLM-assisted systematic reviews are trustworthy for policy decisions
- **Manuscript phrase:** *"To our knowledge, no study has quantified how LLM non-determinism propagates through the full evidence synthesis pipeline — from abstract screening through data extraction to meta-analytic pooling — to alter quantitative conclusions."*

---

## Gap 2 (P0): No LLM screening/extraction study in PM2.5 / respiratory health epidemiology

- **Type:** Evidência (domain-specific)
- **Severity:** Alta
- **Evidence:**
  - Zuo et al. (2025, EH-01): LLM screening in environmental evidence, but for stream fecal coliform / land use — not air pollution
  - Nykvist et al. (2025, EH-02): LLM screening for EV charging infrastructure
  - ACS Environ Au (2024, EH-03): LLM screening in wastewater epidemiology
  - Berger-Tal et al. (2024, EH-04): AI for conservation evidence synthesis
  - **Zero papers** apply LLM screening or extraction to air pollution epidemiology (PM2.5, NO₂, O₃) specifically
- **What's missing:** The largest and most policy-relevant domain in environmental health (air pollution) has no LLM-assisted evidence synthesis studies
- **Our contribution:** First study to apply and evaluate LLM-assisted screening and extraction in PM2.5 / respiratory health, a domain directly informing WHO air quality guidelines
- **Impact:** Validates (or invalidates) LLM tools in the domain that matters most for public health policy
- **Manuscript phrase:** *"While LLMs have been evaluated for systematic reviews in wastewater epidemiology and conservation science, no study has assessed their performance — or reproducibility — in the extensively studied domain of particulate matter and respiratory health."*

---

## Gap 3 (P0): No provenance framework for LLM-assisted evidence synthesis

- **Type:** Metodológica
- **Severity:** Alta
- **Evidence:**
  - Lieberum et al. (2025, SC-07): Noted lack of standardized reporting for LLM-assisted steps
  - Zuo et al. (2025, EH-01): Noted "inconsistent application of eligibility criteria in LLM screening affects reproducibility and transparency"
  - Dennstaedt et al. (2024, SC-05): "Minor prompt changes had considerable impact on performance" — but no audit trail proposed
  - Our JAIR paper (2026): Proposes provenance protocol for generative AI, but not yet applied to evidence synthesis
- **What's missing:** No structured, implementable framework for tracking and auditing LLM decisions within a systematic review pipeline (run cards, input hashes, decision traces)
- **Our contribution:** We extend the JAIR provenance protocol to evidence synthesis, with specific run cards for screening decisions, extraction outputs, and meta-analytic inputs
- **Impact:** Provides the community with a practical, open-source framework for auditable LLM-assisted reviews
- **Manuscript phrase:** *"Current LLM-assisted systematic review studies lack standardized provenance tracking, making it impossible to audit which LLM decisions produced which meta-analytic conclusions."*

---

## Gap 4 (P1): No study evaluates mitigation strategies (guardrails, dual-pass, HITL) for LLM evidence synthesis

- **Type:** Metodológica
- **Severity:** Média
- **Evidence:**
  - Krag et al. (2024, SC-06): Dual-LLM+human achieved 91% automation, 8% error — but only for screening, not full pipeline
  - Khan et al. (2025, EX-01): Collaborative LLM extraction improved concordance, but measured only extraction, not downstream impact
  - No study compares cost vs stability vs accuracy across multiple mitigation levels
- **Our contribution:** We implement and compare 4 levels (baseline → guardrails → dual-pass → HITL) and measure their effect on pipeline stability AND final meta-analytic conclusions
- **Manuscript phrase:** *"While dual-LLM approaches have shown promise for screening and extraction individually, no study has evaluated graded mitigation strategies for their ability to stabilize end-to-end evidence synthesis outcomes."*

---

## Gap 5 (P1): High heterogeneity in PM2.5 meta-analyses is acknowledged but not linked to methodological variation in synthesis tools

- **Type:** Teorica
- **Severity:** Média
- **Evidence:**
  - Delavar et al. (2023, MA-04): I²=94.86% in COPD meta-analysis
  - Multiple meta-analyses report substantial heterogeneity attributed to population, geography, lag selection
  - **No meta-analysis considers the possibility that the synthesis tool itself introduces heterogeneity**
- **Our contribution:** We demonstrate a new source of heterogeneity: the LLM tool used for screening/extraction can alter which studies enter the meta-analysis and what effect sizes are extracted
- **Manuscript phrase:** *"Existing meta-analyses attribute heterogeneity to clinical and methodological diversity; we identify a novel source — the evidence synthesis tool itself — that has been entirely overlooked."*

---

## Priority Summary

| Gap | Priority | Directly Addresses RQ | Contribution Type |
|-----|----------|----------------------|-------------------|
| Gap 1 — Full pipeline propagation | P0 | RQ1 + RQ2 + RQ3 | Diagnostic (core) |
| Gap 2 — PM2.5 domain gap | P0 | All | Domain application |
| Gap 3 — Provenance framework | P0 | RQ4 | Prescriptive (framework) |
| Gap 4 — Mitigation comparison | P1 | RQ4 | Prescriptive (practical) |
| Gap 5 — Tool-induced heterogeneity | P1 | RQ3 | Theoretical (novel concept) |

---

*Gap Analysis v1.0 — Literature Specialist*
*5 gaps identified (3 P0, 2 P1)*
*Date: 2026-02-11*
