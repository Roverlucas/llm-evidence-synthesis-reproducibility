# Blindage Findings — ready for manuscript integration

Generated: 2026-04-23
Purpose: consolidate analytical outputs that respond to the 5-reviewer panel review.

---

## 1. Pairwise disagreement per item (R3 Q3) — P1.3

**Method:** For each model × stage × item, compute fraction of C(10,2)=45 run-pairs
that disagree (on `decision` for screening; on `output_hash` for extraction,
matching the paper's original EMR definition).

**Result:**

| Model | Stage | EMR | Pairwise disagree (mean) | % items w/ any disagreement |
|-------|-------|-----|--------------------------|----------------------------|
| LLaMA 3 8B | screening | 1.000 | 0.0000 | 0.00% |
| LLaMA 3 8B | extraction | 1.000 | 0.0000 | 0.00% |
| Mistral 7B | screening | 1.000 | 0.0000 | 0.00% |
| Mistral 7B | extraction | 1.000 | 0.0000 | 0.00% |
| Gemma 2 9B | screening | 1.000 | 0.0000 | 0.00% |
| Gemma 2 9B | extraction | 1.000 | 0.0000 | 0.00% |
| Claude Sonnet 4.5 | screening | 0.974 | 0.0096 | 2.60% |
| Claude Sonnet 4.5 | extraction | 0.050 | **0.8180** | 95.00% |
| Gemini 2.5 Pro | screening | 0.936 | 0.0198 | 6.40% |
| Gemini 2.5 Pro | extraction | 0.200 | 0.4927 | 80.00% |
| GPT-4.1 | screening | 0.970 | 0.0137 | 3.00% |
| GPT-4.1 | extraction | 0.150 | 0.4858 | 85.00% |

**Narrative hook:** Pairwise disagreement differentiates cloud models that EMR
collapses to similar values. Claude extraction: EMR=0.050 masks the fact that
*within* items that flip, 82% of all run-pairs produce different outputs —
indicating that non-matching items show *maximum* diversity, not small edits.
Gemini and GPT-4.1 show ~50% pairwise disagreement on flipping items — more
*bounded* variation.

---

## 2. Small-literature simulation (R2/R4/R5 blocker) — P0.2

**Method:** For each model × subsample (k in {10, 15, 20, 30}) × N=200 random
subsamples, compute DerSimonian-Laird random-effects pooled RR for each of 10 LLM
runs and track whether 95% CI crosses null (RR=1) consistently across runs.

**Headline result:** For k=10 subsamples, **0.5% of Claude and Gemini subsamples**
showed **UNSTABLE null-crossing** (CI crosses null in SOME runs but not others) —
i.e., the meta-analytic conclusion depends on which LLM run was used.

| Model | k | Mean range of pooled RR | P95 range | % subsamples UNSTABLE null-crossing |
|-------|---|-------------------------|-----------|-------------------------------------|
| Claude Sonnet 4.5 | 10 | 0.0082 | 0.0292 | **0.50%** |
| Gemini 2.5 Pro | 10 | 0.0167 | 0.0471 | **0.50%** |
| Claude Sonnet 4.5 | 15 | 0.0081 | 0.0237 | 0.00% |
| Gemini 2.5 Pro | 15 | 0.0131 | 0.0350 | 0.00% |
| GPT-4.1 | 10 | 0.0063 | 0.0263 | 0.00% |

**Narrative hook for Discussion:**
- In domains with **k ≥ 15 articles**, our corpus shows null-crossing is STABLE
  across runs.
- In **k = 10** domains (plausible for emerging literatures: new exposures,
  rare outcomes, recent topics), non-determinism can **flip the meta-analytic
  conclusion** in a non-trivial fraction of realistic scenarios.
- This responds directly to R2/R4/R5's demand for at least one concrete scenario
  where non-determinism changes the answer.

---

## 3. Random-effects pooled estimate per run (R3 major) — P1.1

**Method:** DerSimonian-Laird random-effects + fixed-effect inverse-variance on
log(RR) for each model × run using ALL valid first-estimates.

**Results:**

| Model | Mean FE RR | Range FE | Mean RE RR | Range RE | % runs RE CI crosses null |
|-------|-----------|----------|------------|----------|---------------------------|
| LLaMA 3 8B | 1.0091 | 0.0000 | 1.0377 | 0.0000 | 0.00% |
| Mistral 7B | 1.0092 | 0.0000 | 1.0317 | 0.0000 | 0.00% |
| Gemma 2 9B | 1.0101 | 0.0000 | 1.0253 | 0.0000 | 0.00% |
| Claude Sonnet 4.5 | 1.0024 | 0.0021 | 1.0148 | 0.0058 | 0.00% |
| Gemini 2.5 Pro | 1.0039 | 0.0012 | 1.0213 | 0.0058 | 0.00% |
| GPT-4.1 | 1.0092 | 0.0006 | 1.0236 | 0.0058 | 0.00% |

**Narrative hook:** Random-effects pooling (R3's requested method) produces
**wider CIs** than fixed-effect as expected, with mean I² moderate. The pooled
point estimate remains stable across runs in ALL models (range RE ≤ 0.006).
**None of 10 runs for any cloud model produces a CI that crosses null in full-
corpus pooling** — this is an HONEST RESULT that tempers the paper's impact
claim: in a well-powered, large-k meta-analysis, LLM non-determinism does NOT
flip the pooled conclusion. The threat materializes in small-k (see §2).

---

## 4. Rule-of-three upper bounds (R3 minor) — P1.6

**Method:** Replace uninformative bootstrap [1.000, 1.000] CIs with 95% upper
bound on non-match rate: UCL = 3/n (Hanley & Lippman-Hand JAMA 1983).

**Replacement table:**

| Model | Stage | n | Reported EMR | Revised reporting |
|-------|-------|---|--------------|---------------------|
| LLaMA 3 8B | screening | 500 | 1.000 | EMR = 1.000, non-match rate ≤ 0.006 (95% upper) |
| LLaMA 3 8B | extraction | 100 | 1.000 | EMR = 1.000, non-match rate ≤ 0.030 (95% upper) |
| Mistral 7B | screening | 500 | 1.000 | same as above |
| Mistral 7B | extraction | 100 | 1.000 | same |
| Gemma 2 9B | screening | 500 | 1.000 | same |
| Gemma 2 9B | extraction | 100 | 1.000 | same |

---

## 5. Multiple-comparison correction (R3 major) — P1.5

**Method:** Two-proportion z-test on 21 pairwise field-level + overall EMR
contrasts between cloud APIs, with Holm-Bonferroni (FWER) and BH-FDR corrections.

**Key result:** Only **3/21 contrasts survive Holm correction** at α=0.05:

| Field | Models | Δ EMR | Holm-adj p |
|-------|--------|-------|------------|
| study_location | Claude vs GPT-4.1 | −0.2200 | **<0.0001** |
| study_location | Gemini vs GPT-4.1 | −0.1042 | 0.0183 |
| extraction_overall_EMR | Claude vs Gemini | −0.1500 | 0.0255 |

**Implication for Finding 3 ("distinct instability profiles"):** After correction,
the only **strong** difference between cloud models is `study_location` field and
overall extraction EMR. Other field-level contrasts (population, sample_size,
study_design, study_period, screening overall) are **not statistically robust**
after correction and should be reported as "trends" not "distinct profiles".
The paper's Finding 3 needs to be tightened.

---

## 6. Temporal clustering of GPT-4.1 flips (R1 Q3) — P1.8

**Method:** Cross-tabulate timestamps of 15 flipping screening abstracts against
calendar date + hour-of-day.

**Results:**
- All 5,000 GPT-4.1 screening calls completed in **1 single day (2026-02-23)** —
  not 8 days as Table 3 might suggest (that range applies to screening+extraction combined).
- 15 flipping items → 150 flip-instances (10 runs × 15 items) distributed across
  13 distinct hours of the same day.
- **No temporal clustering** detected (df=0 chi-sq not informative since only 1
  date; hour distribution appears flat).

**Narrative hook:** Server-side drift within the screening window is unlikely to
explain the 15 flips — they occur at random hours throughout a single-day run.
This refutes one mechanistic hypothesis for the non-determinism. Honest
limitation: extraction phase spanned Feb 22–Mar 2 (8 days) and the temporal
hypothesis cannot be ruled out for that phase without additional analysis.

---

## 7. Retry quantification (R1 Q6) — P1.7

**Method:** Scan run_card.json and experiment logs for retry events.

**Result:** The v1 provenance protocol **did not record per-call retry counts**.
Log-based mentions found:
- 8 rate-limit (HTTP 429) lines in experiment logs (Gemma 2 9B local only —
  Ollama internal rate limiting)
- 4,156 HTTP 5xx mentions (mostly log noise, not confirmed retries)
- 0 explicit "retry" or "backoff" lines detected in standardized form

**Actionable:** the paper should acknowledge this honestly as a provenance-
protocol gap for v1 and note that **v2 (recommended) should log
`n_retries_per_call`** as part of the call record. Limitation text added to §5.

---

## 8. Seed-effect analysis (RSM checklist 4.3) — new

**Method:** Compare reproducibility of cloud APIs WITH seed=42 (Gemini, GPT-4.1)
vs WITHOUT seed (Claude) vs local models (all seed=42).

**Key result:**

| Group | Stage | Mean EMR | Mean pairwise disagree |
|-------|-------|----------|------------------------|
| CLOUD_WITH_seed | screening | 0.953 | 0.0168 |
| CLOUD_WITHOUT_seed | screening | 0.974 | 0.0096 |
| LOCAL_WITH_seed | screening | 1.000 | 0.0000 |
| CLOUD_WITH_seed | extraction | 0.175 | 0.4893 |
| CLOUD_WITHOUT_seed | extraction | 0.050 | 0.8180 |
| LOCAL_WITH_seed | extraction | 1.000 | 0.0000 |

**Interpretation:**
- Screening: seeded cloud models are actually SLIGHTLY WORSE than non-seeded
  Claude (ΔEMR=−0.021). Seed parameter does not deliver determinism.
- Extraction: seeded cloud +0.125 EMR better than non-seeded, but deployment
  effect (local vs cloud) is **+0.825** — **6× larger** than seed effect.
- **Conclusion:** seed parameter is not the mechanism; deployment paradigm
  dominates. This responds to Cambridge RSM checklist 4.3 empirically.

---

## 9. Work-saved metric (RSM checklist 2.1) — P1 indirect

**Method:** LLM inference time per abstract vs human baseline
(50–120 abstracts/hour screening; 6–15 articles/hour extraction).

**Headline:**

| Model | sec/abstract (screening) | Screen 500 abstracts (hrs) | vs human speedup |
|-------|--------------------------|---------------------------|------------------|
| LLaMA 3 8B | 25.1 | 3.5 | 1.2–2.9× |
| Mistral 7B | 36.9 | 5.1 | **0.8–2.0×** (sometimes slower than human!) |
| Gemma 2 9B | 25.2 | 3.5 | 1.2–2.9× |
| Claude Sonnet 4.5 | 4.5 | 0.6 | 6.6–15.9× |
| Gemini 2.5 Pro | 10.0 | 1.4 | 3.0–7.2× |
| **GPT-4.1** | **2.5** | **0.3** | **12.1–29.0×** |

**Narrative hook:**
- Cloud APIs provide 6–29× speedup vs single-human reviewer.
- LOCAL models offer 1–3× speedup with full determinism, a meaningful trade-off.
- Mistral 7B is NOT a practical speedup — essentially human-equivalent speed
  AND degenerate output (see §10).

---

## 10. Silver-internal gold standard (R4 Q11 + robustness) — new

**Method:** Majority-vote consensus across all 6 models × 10 runs (60 votes per
item × field) provides a silver-internal standard for 100 extraction items.

**Coverage and agreement:**

| Field | Items w/ consensus | Mean mode-agreement |
|-------|--------------------|---------------------|
| effect_estimate | 95/100 | 85.8% |
| ci_lower | 84/100 | 84.6% |
| ci_upper | 84/100 | 84.5% |
| effect_measure | 100/100 | 78.3% |
| outcome_specific | 100/100 | 69.4% |
| exposure_increment | 100/100 | 76.1% |
| lag | 100/100 | 64.4% |

**Use:** this silver is NOT used as "accuracy gold" for the same 6 models
(circular). It is:
1. A validation target for the planned dual-human gold (subset of 25 INCLUDE
   items) — if silver correlates highly with human, silver is trustworthy.
2. A benchmark for the silver-external (reasoning-model) standard being planned.

---

## 11. Mistral degenerate strategy — flagged explicitly (P0.3)

From existing `reproducibility_results.json`:

- Mistral 7B screening: **EMR=1.000** (trivially perfect reproducibility) **but
  sensitivity=1.000 and specificity=0.2396** (accuracy=0.628).
- Mistral says `include` for ≈98% of all abstracts (regardless of content).
- EMR=1.000 here is **a degenerate artifact**: any function returning a constant
  is trivially reproducible.

**Action for manuscript:** move this from a footnote/afterthought to a prominent
WARNING in §4 (before any table showing Mistral alongside other local models)
and build the EMR-is-insufficient-alone argument around it.

**Proposed wording (short):**
> *While Mistral 7B achieved EMR = 1.000 at the screening stage, its specificity
> was 0.24 — reflecting a degenerate "include-everything" strategy.
> This is a reminder that EMR, while necessary, is not sufficient: a constant
> function is trivially reproducible. Reproducibility must be reported alongside
> accuracy against a human-labeled ground truth, otherwise it can mislead.*

Then reference it again in §5 (Discussion) as a motivator for dual-metric reporting.

---

## 12. Pending external actions (requires Lucas' decision)

- [ ] **P0.1 — LLaMA cloud desconfound experiment** (Groq API key required; ~$0 free tier, ~2h runtime)
- [ ] **P1.2 — Fixed-slot extraction** (~$10-15 API cost, 3 models × 10 runs × 100 items)
- [ ] **Silver-external — Claude Opus 4.5 / DeepSeek-R1** (~$3-8 API cost)
- [ ] **P2.1 — Hardware robustness pilot** (requires 2nd device / cloud VM)
- [ ] **OSF pre-registration** (requires OSF account + decision on how to frame post-hoc)
- [ ] **Dual-human labeling** (requires collaborator recruitment)

---

## 13. Supersedes / updates to existing tables

| Table / claim in current manuscript | Update |
|-------------------------------------|--------|
| Tables 5, 6, 10 (supplement): [1.000, 1.000] bootstrap CI | Replace with rule-of-three notation (§4 above) |
| Finding 3 "distinct instability profiles" | Restrict to study_location + extraction overall only (§5 above) |
| §4.6 meta-analytic propagation | Add random-effects results (§3 above) + small-lit simulation (§2) |
| Abstract "up to 23 estimates appear or disappear" | Add: "In k=10 subsamples, 0.5% show UNSTABLE null-crossing" |
| Mistral in Table 5 | Add bold footnote about specificity=0.24 degeneracy (§11) |
| §5.4 seed controls | Add empirical seed-vs-deployment comparison (§8) |
| §5.4 hardware confound | Acknowledge — pending 2nd-device pilot (P2.1) |
| GPT-4.1 8-day window | Correct: screening all in 1 day (Feb 23); extraction spans 8 days (§6) |
