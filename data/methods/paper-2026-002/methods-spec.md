# Methods Specification — paper-2026-002

**Agent:** @methodology-specialist
**Date:** 2026-02-11
**Status:** Complete — ready for Gate 2 review

---

## 1. Study Design

### Selected Design: Repeated-Measures Computational Experiment

**Type:** Empirical reproducibility study with multi-stage pipeline evaluation

**Rationale:** The research questions ask whether identical LLM configurations produce
variable outputs across repeated runs and whether this variation propagates to meta-analytic
conclusions. This requires a controlled, repeated-measures design where:
- The **input is fixed** (same 500 abstracts, same prompts, same configurations)
- The **only source of variation** is the LLM's inherent non-determinism
- **Multiple repetitions** (30 per model) enable statistical estimation of variation
- A **gold standard** provides ground truth for accuracy measurement

### Alternatives Considered

| Design | Fit | Pros | Cons | Decision |
|--------|-----|------|------|----------|
| **Repeated-measures computational** | **Best** | Controls all inputs; isolates non-determinism; enables bootstrap CIs | Requires gold standard; computationally intensive | **SELECTED** |
| Single-run accuracy study | Low | Simpler; less computation | Cannot measure variation; answers different question | Rejected |
| Multi-prompt comparison | Medium | Tests prompt sensitivity | Confounds prompt variation with non-determinism | Rejected — could be extension |
| Simulation study (synthetic data) | Medium | Full control; no gold standard needed | Lacks ecological validity; reviewers may question relevance | Rejected |

### Paradigm

```yaml
paradigm:
  epistemology: "positivist"
  approach: "deductive (hypothetico-deductive)"
  strategy: "computational experiment"
  time_horizon: "cross-sectional (repeated measures within single time window)"
  data_type: "quantitative"
```

---

## 2. Study Components

### 2.1 Corpus Construction

```yaml
corpus:
  topic: "PM2.5 and respiratory hospitalizations (time-series studies)"
  target_size: 500
  source_databases: ["PubMed", "Scopus"]
  search_strategy: "data/literature/paper-2026-002/search-strategy.md"

  composition:
    clearly_include: 100
    clearly_exclude: 100
    ambiguous: 300

  classification_criteria:
    clearly_include: "Meets ALL 6 inclusion criteria unambiguously based on title+abstract"
    clearly_exclude: "Fails ≥2 inclusion criteria clearly (wrong exposure, wrong outcome, wrong design, or non-original)"
    ambiguous: "Borderline on ≥1 criterion: mixed exposures, unclear outcome specificity, borderline design, or partial effect estimate reporting"

  gold_standard:
    method: "dual-human independent labeling + discordance resolution"
    labelers: 2  # minimum; ideally one with environmental epidemiology expertise
    resolution: "third-party adjudication or consensus discussion"
    output_per_abstract:
      screening: "include | exclude (binary, after resolution)"
      extraction: "structured JSON with RR, CI, lag, etc. (for included studies)"
    inter_rater_metrics: "Cohen's kappa, percent agreement"
```

### 2.2 Models Under Study

```yaml
models:
  - id: "llama3-8b"
    type: "local"
    provider: "Ollama v0.15.5"
    architecture: "LLaMA 3 8B Instruct"
    parameters: 8B
    quantization: "Q4_0"  # verify exact quant in Ollama
    temperature: 0
    seed: 42
    num_predict: 2048
    determinism_control: "seed + temperature=0"
    expected_behavior: "Near-deterministic (local inference, fixed seed)"
    weights_hash: "sha256 of model weights via Ollama API"

  - id: "claude-sonnet-4-5"
    type: "api"
    provider: "Anthropic"
    architecture: "Claude Sonnet 4.5"
    temperature: 0
    max_tokens: 2048
    seed: null  # Claude API does not support seed parameter
    determinism_control: "temperature=0 only"
    expected_behavior: "Non-deterministic (no seed support, server-side variation)"

  - id: "gemini-2.5-pro"
    type: "api"
    provider: "Google"
    architecture: "Gemini 2.5 Pro"
    temperature: 0
    max_output_tokens: 8192  # thinking model needs larger budget
    seed: 42  # supported but does NOT guarantee determinism per Google docs
    determinism_control: "temperature=0 + seed=42 (not guaranteed)"
    expected_behavior: "Non-deterministic (seed supported but not honored)"
```

### 2.3 Experimental Pipeline (4 Stages)

```
┌──────────────────────────────────────────────────────────────────┐
│ STAGE A: SCREENING                                               │
│ Input: 500 abstracts × fixed prompt × inclusion criteria         │
│ Output: {decision, confidence, rationale, key_fields} per abstract│
│ Runs: 30 per model = 90 total screening batches                  │
│ Total LLM calls: 90 × 500 = 45,000                              │
└──────────────────┬───────────────────────────────────────────────┘
                   │ included abstracts (vary per run!)
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│ STAGE B: EXTRACTION                                              │
│ Input: included abstracts from Stage A × extraction prompt       │
│ Output: {RR, CI_lower, CI_upper, lag, exposure, population} JSON │
│ Runs: 30 per model (using each run's own screening results)      │
│ Total LLM calls: ~90 × ~150 (est. avg included) = ~13,500       │
└──────────────────┬───────────────────────────────────────────────┘
                   │ extracted effect sizes (vary per run!)
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│ STAGE C: META-ANALYSIS                                           │
│ Input: extracted data per run (from Stage B)                     │
│ Method: DerSimonian-Laird random-effects                         │
│ Output: pooled_effect, CI_pooled, I², tau², Q per run            │
│ Computations: 90 independent meta-analyses                       │
│ Deterministic: yes (same input → same output)                    │
└──────────────────┬───────────────────────────────────────────────┘
                   │ 90 pooled estimates
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│ STAGE D: MITIGATION COMPARISON                                   │
│ Levels: baseline | guardrails | dual-pass | human-in-loop        │
│ Measure: stability improvement vs. cost                          │
│ Applied post-hoc to Stage A+B outputs                            │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. Variables

### 3.1 Independent Variables

```yaml
independent_variables:
  - name: "model"
    type: "categorical (3 levels)"
    levels: ["llama3-8b", "claude-sonnet-4-5", "gemini-2.5-pro"]
    role: "Between-model comparison"

  - name: "run_id"
    type: "ordinal (1-30)"
    role: "Within-model repeated measure"

  - name: "mitigation_level"
    type: "categorical (4 levels)"
    levels: ["baseline", "guardrails", "dual_pass", "human_in_loop"]
    role: "Treatment comparison (Stage D)"

  - name: "abstract_category"
    type: "categorical (3 levels)"
    levels: ["clearly_include", "clearly_exclude", "ambiguous"]
    role: "Moderator — variation expected to differ by category"
```

### 3.2 Dependent Variables (Outcome Metrics)

```yaml
# ── STAGE A: Screening Metrics ──
screening_metrics:
  - name: "flip_rate"
    definition: "Proportion of abstracts receiving different decisions across 30 runs"
    formula: "n_abstracts_with_any_flip / n_total_abstracts"
    unit: "proportion [0, 1]"
    level: "per-model aggregate"

  - name: "decision_entropy"
    definition: "Shannon entropy of include/exclude decisions per abstract across 30 runs"
    formula: "H = -Σ p(d) log₂ p(d) for d ∈ {include, exclude, uncertain}"
    unit: "bits"
    level: "per-abstract"

  - name: "cohens_kappa_pairwise"
    definition: "Mean Cohen's kappa between all pairs of runs for the same model"
    formula: "mean(κ(run_i, run_j)) for all i < j"
    unit: "κ ∈ [-1, 1]"
    level: "per-model"

  - name: "F1_vs_gold"
    definition: "F1 score of each run against gold standard"
    formula: "2 × (precision × recall) / (precision + recall)"
    unit: "F1 ∈ [0, 1]"
    level: "per-run"

  - name: "sensitivity_specificity"
    definition: "True positive rate and true negative rate vs gold"
    unit: "[0, 1]"
    level: "per-run"

# ── STAGE B: Extraction Metrics ──
extraction_metrics:
  - name: "exact_match_rate"
    definition: "Proportion of extracted fields that exactly match gold standard"
    formula: "n_exact_matches / n_total_fields"
    unit: "proportion [0, 1]"
    level: "per-run"

  - name: "RR_absolute_error"
    definition: "Mean absolute error of extracted RR vs gold standard RR"
    formula: "mean(|RR_extracted - RR_gold|)"
    unit: "absolute RR difference"
    level: "per-run"

  - name: "CI_absolute_error"
    definition: "Mean absolute error of extracted CI bounds vs gold"
    formula: "mean(|CI_extracted - CI_gold|) for both lower and upper"
    unit: "absolute CI difference"
    level: "per-run"

  - name: "extraction_validity_rate"
    definition: "Proportion of extractions passing JSON schema + range checks"
    unit: "proportion [0, 1]"
    level: "per-run"

  - name: "hallucination_rate"
    definition: "Proportion of extracted values with no basis in the abstract text"
    unit: "proportion [0, 1]"
    level: "per-run"

# ── STAGE C: Meta-Analysis Metrics ──
meta_metrics:
  - name: "pooled_effect_variation"
    definition: "SD of pooled RR estimates across 30 runs for same model"
    unit: "SD of log(RR)"
    level: "per-model"

  - name: "CI_crossing_null_rate"
    definition: "Proportion of runs where pooled CI crosses RR=1 (no effect)"
    formula: "n_runs_CI_crosses_1 / 30"
    unit: "proportion [0, 1]"
    level: "per-model"
    significance: "CONCLUSION-CHANGING metric — primary outcome for RQ3"

  - name: "I2_variation"
    definition: "Range and SD of I² heterogeneity statistic across runs"
    unit: "percentage points"
    level: "per-model"

  - name: "n_studies_included_variation"
    definition: "Range in number of studies entering meta-analysis across runs"
    formula: "max(n_included) - min(n_included) across 30 runs"
    unit: "count"
    level: "per-model"

# ── STAGE D: Mitigation Metrics ──
mitigation_metrics:
  - name: "stability_improvement"
    definition: "Reduction in flip_rate and extraction error vs baseline"
    formula: "(metric_baseline - metric_mitigated) / metric_baseline"
    unit: "proportion reduction"

  - name: "additional_cost"
    definition: "Extra API calls, human review time, and compute cost"
    unit: "USD or API calls"

  - name: "accuracy_change"
    definition: "Change in F1/RR_error vs gold after applying mitigation"
    unit: "delta F1 or delta absolute error"
```

---

## 4. Procedure (Step-by-Step Protocol)

### Phase 1: Corpus Construction (Est. 1-2 weeks)

```
1.1  Execute PubMed search using documented strategy
     → Export to JSON/CSV (title, abstract, PMID, authors, year, journal)
1.2  Execute Scopus search (same strategy adapted)
     → Export same fields
1.3  Deduplicate using DOI/PMID matching
1.4  Random sample ~600 abstracts (oversample for attrition during labeling)
1.5  Two human labelers independently classify each abstract:
     → include / exclude (binary)
     → For included: extract RR, CI, lag, exposure, population
1.6  Compute inter-rater agreement (Cohen's kappa)
1.7  Resolve discordances via discussion or third adjudicator
1.8  Select final 500 abstracts (100 include / 100 exclude / 300 ambiguous)
     → "Ambiguous" = abstracts where human labelers initially disagreed
       OR where criteria applicability is borderline
1.9  Store as gold_standard.json with all labels and extraction values
```

### Phase 2: Pipeline Implementation (Est. 1 week)

```
2.1  Implement model runners (reuse from JAIR paper):
     → ollama_runner.py (LLaMA 3 8B)
     → claude_runner.py (Claude Sonnet 4.5)
     → gemini_runner.py (Gemini 2.5 Pro)
2.2  Implement screening pipeline:
     → Load prompt template + abstract
     → Call model → parse JSON response
     → Validate against screening_output.json schema
     → Log: input_hash, output_hash, model, seed, temperature, timestamp
2.3  Implement extraction pipeline:
     → Same as screening but with extraction prompt
     → Validate against extraction_output.json schema
     → Numeric range checks (RR ∈ [0.5, 5.0], CI consistency)
2.4  Implement meta-analysis module:
     → DerSimonian-Laird random-effects model
     → Input: extracted RR + CI per study per run
     → Output: pooled RR, pooled CI, I², tau², Q
2.5  Implement provenance module:
     → SHA-256 hashing of inputs and outputs
     → Run card generation (JSON per run)
2.6  Write pytest test suite for all modules
```

### Phase 3: Experiment Execution (Est. 1-2 weeks)

```
3.1  STAGE A — Screening:
     For each model (3):
       For each run (1-30):
         For each abstract (500):
           → Call model with screening prompt
           → Store response + provenance
         → Compute run-level metrics (F1, kappa vs gold)
       → Compute model-level metrics (flip_rate, mean kappa)

3.2  STAGE B — Extraction:
     For each model (3):
       For each run (1-30):
         For each abstract marked "include" in this run:
           → Call model with extraction prompt
           → Validate JSON schema + numeric ranges
           → Store response + provenance
         → Compute run-level metrics (EMR, RR error, CI error)

3.3  STAGE C — Meta-analysis:
     For each model (3):
       For each run (1-30):
         → Collect extracted RR + CI for included studies
         → Run DerSimonian-Laird random-effects meta-analysis
         → Store: pooled_RR, pooled_CI, I², tau², Q, n_studies
       → Compute: SD(pooled_RR), CI_crossing_null_rate, I² range

3.4  STAGE D — Mitigation comparison:
     For each mitigation level (4):
       Apply post-hoc to Stage A + B outputs:
       → Baseline: raw outputs
       → Guardrails: reject invalid JSON + out-of-range values → re-query
       → Dual-pass: compare run pairs → consensus on agreement, flag on disagreement
       → Human-in-loop: review flagged items only
       → Recompute all metrics under each mitigation level
```

### Phase 4: Analysis (Est. 1 week)

```
4.1  Descriptive statistics per model per stage
4.2  Bootstrap confidence intervals (10,000 resamples, percentile method)
4.3  Comparison across models:
     → Local (LLaMA) vs API (Claude, Gemini)
     → Kruskal-Wallis or equivalent non-parametric tests
4.4  Subgroup analysis by abstract category:
     → clearly_include vs ambiguous vs clearly_exclude
4.5  Generate figures:
     → Fig 1: Forest plot of pooled effects across 30 runs per model
     → Fig 2: Flip rate heatmap by abstract × model
     → Fig 3: RR extraction error distribution
     → Fig 4: CI crossing null probability by model
     → Fig 5: Stability vs cost tradeoff (mitigation levels)
     → Fig 6: PRISMA-like flow diagram of the study
4.6  Sensitivity analyses:
     → Effect of corpus subset (random 250 vs full 500)
     → Effect of N runs (10, 20, 30) on metric stability
```

---

## 5. Statistical Analysis Plan

```yaml
statistical_plan:
  # Primary analyses
  primary:
    - analysis: "Flip rate estimation with 95% CI"
      test: "Bootstrap percentile CI (10,000 resamples)"
      justification: "Non-parametric; no distributional assumptions"

    - analysis: "Pairwise run agreement"
      test: "Cohen's kappa (mean and range across all run pairs)"
      justification: "Standard metric for inter-rater agreement"

    - analysis: "F1 vs gold standard"
      test: "Per-run F1 with bootstrap CI"
      justification: "Standard classification metric"

    - analysis: "Pooled effect variation"
      test: "SD and range of log(RR) across 30 runs per model"
      justification: "Direct measure of outcome variability"

    - analysis: "CI crossing null rate"
      test: "Proportion of runs with CI crossing RR=1"
      justification: "Primary conclusion-changing metric"

  # Secondary analyses
  secondary:
    - analysis: "Model comparison (local vs API)"
      test: "Mann-Whitney U or Kruskal-Wallis"
      justification: "Non-parametric; small group sizes (3 models)"

    - analysis: "Category subgroup (include/exclude/ambiguous)"
      test: "Stratified analysis with separate flip rates"
      justification: "Ambiguous abstracts expected to show more variation"

    - analysis: "Mitigation effectiveness"
      test: "Paired Wilcoxon signed-rank (baseline vs each level)"
      justification: "Paired comparison of same runs under different mitigation"

  # Sensitivity analyses
  sensitivity:
    - analysis: "Corpus subset (250 random vs full 500)"
      purpose: "Assess robustness of results to corpus size"

    - analysis: "Run count impact (10, 20, 30)"
      purpose: "Assess how many runs needed for stable estimates"

  # Software
  software:
    - "Python 3.14+ (numpy, scipy, pandas)"
    - "statsmodels (meta-analysis)"
    - "matplotlib + seaborn (visualization)"

  # Multiple comparisons
  correction: "Bonferroni where applicable (3 models × 4 stages = 12 primary comparisons)"
  alpha: 0.05
```

---

## 6. Validity Threat Assessment

| # | Threat | Type | Severity | Mitigation | Residual Risk |
|---|--------|------|----------|------------|---------------|
| V1 | Gold standard quality (human error in labeling) | Internal | HIGH | Dual labelers + discordance resolution + kappa reporting | MEDIUM |
| V2 | Prompt sensitivity (results depend on specific prompt wording) | Construct | HIGH | Fixed prompt across all models and runs; document exact prompt; sensitivity analysis in follow-up | MEDIUM |
| V3 | Model version changes (API model updates during experiment) | Internal | HIGH | Record model version hash per run; execute all runs within narrow time window | LOW |
| V4 | Abstract order effects (batch processing order affects outputs) | Internal | LOW | Fixed order across all runs; shuffle-order sensitivity test | LOW |
| V5 | Single topic (PM2.5 only — may not generalize to other domains) | External | MEDIUM | Acknowledged as limitation; topic chosen for abundance and standardization | MEDIUM |
| V6 | Single prompt per stage (may not represent all reasonable prompts) | Construct | MEDIUM | Prompt designed from systematic review criteria; acknowledged as limitation | MEDIUM |
| V7 | 30 runs may be insufficient for rare events | Statistical | LOW | 30 runs × 500 abstracts = 15,000 observations per model; bootstrap CIs quantify uncertainty | LOW |
| V8 | API rate limits / throttling may introduce systematic differences | Internal | LOW | Controlled batch sizes; exponential backoff; timestamps logged | LOW |
| V9 | Gold standard extraction subjectivity (RR selection from multi-lag studies) | Internal | MEDIUM | Pre-defined extraction protocol; prefer lag 0-1 or primary reported estimate | LOW |
| V10 | Temporal confound (API behavior changes over study period) | Internal | MEDIUM | Narrow execution window; run cards with timestamps; check for drift | LOW |

### Overall Validity Assessment

- **Internal validity:** MEDIUM-HIGH (controlled experiment, but gold standard quality is key dependency)
- **External validity:** MEDIUM (single topic, single prompt, 3 models — acknowledged as initial study)
- **Construct validity:** MEDIUM (flip rate and CI-crossing-null are meaningful proxies, but don't capture all forms of non-determinism)
- **Statistical conclusion validity:** HIGH (30 runs × 500 abstracts; bootstrap CIs; sensitivity analyses)

---

## 7. Reporting Guidelines

### Selected: Hybrid STROBE-Computational + PRISMA-S

**Rationale:** No single reporting guideline perfectly fits a computational reproducibility
experiment. We adopt a hybrid approach:

- **STROBE (modified)** for the overall study reporting (observational computational experiment)
- **PRISMA-S** for search strategy documentation
- **Custom reproducibility checklist** based on our JAIR provenance protocol

Key reporting items:
- Full prompts published in appendix
- All code open-source (GitHub)
- Run cards and provenance hashes for all 45,000+ LLM calls
- Gold standard dataset published (with abstracts under fair use)
- Bootstrap CI methodology documented
- Sensitivity analysis results reported regardless of direction

---

## 8. Ethical Considerations

```yaml
ethics:
  human_participants: false  # computational study using published abstracts
  ethical_approval: "Not required (no human subjects; uses publicly available bibliographic data)"
  data_privacy: "No patient data involved; abstracts are public"
  consent: "N/A"

  ai_ethics:
    - "API usage within terms of service of Anthropic and Google"
    - "No attempt to circumvent safety measures"
    - "Transparent reporting of model limitations"

  open_science:
    - "Code: fully open-source (MIT license)"
    - "Data: gold standard dataset and all raw outputs published"
    - "Provenance: run cards for all LLM calls"
    - "Pre-registration: consider OSF before execution"

  conflict_of_interest: "None to declare"
  funding: "Self-funded / not applicable"
```

---

## 9. Limitations (Pre-drafted for Discussion)

### Methodological Limitations

1. **Single domain:** This study evaluates LLM reproducibility in the specific domain of PM2.5
   and respiratory hospitalizations. While chosen for its abundance of standardized studies,
   findings may not generalize to other environmental health domains or other fields of medicine.
   Future studies should replicate this methodology across diverse clinical and environmental topics.

2. **Fixed prompt design:** We use a single, carefully designed prompt per stage. Prompt engineering
   choices may influence both the absolute performance and the degree of non-determinism observed.
   The impact of prompt variation is beyond the scope of this study but represents an important
   avenue for future research.

3. **Three models:** While our selection spans local (Ollama/LLaMA) and API-based (Claude, Gemini)
   providers, it does not cover all commercially available LLMs. Results should be interpreted as
   illustrative of the non-determinism phenomenon rather than comprehensive across all LLMs.

4. **Gold standard limitations:** Human labeling of abstract screening decisions involves inherent
   subjectivity, particularly for ambiguous cases. We mitigate this through dual-labeling and
   discordance resolution, and report inter-rater agreement to quantify residual uncertainty.

5. **Abstract-level analysis only:** We base screening and extraction on titles and abstracts,
   not full texts. This mirrors common practice in rapid screening but may introduce classification
   errors that would be resolved with full-text review.

6. **Meta-analysis methodology:** We employ the DerSimonian-Laird random-effects estimator for
   simplicity and comparability with existing PM2.5 meta-analyses. Alternative estimators (REML,
   Hartung-Knapp) may yield different results; this is noted as a limitation.

---

## 10. Sample Size Justification

```yaml
sample_size:
  corpus: 500
  rationale: |
    With 500 abstracts and 30 runs per model:
    - 15,000 screening decisions per model → sufficient to detect flip rates ≥1%
      with 95% CI width ≤ ±0.6% (binomial proportion CI)
    - 30 runs → 435 pairwise comparisons for kappa estimation
    - ~150 included studies × 30 runs → ~4,500 extracted effect sizes per model
    - 30 independent meta-analyses per model → SD of pooled effect estimable
      with reasonable precision

  power_analysis: |
    For the primary outcome (CI_crossing_null_rate):
    - If true rate = 20% (6/30 runs cross null), 95% CI = [8%, 37%] (binomial exact)
    - If true rate = 50% (15/30), 95% CI = [31%, 69%]
    - 30 runs per model is sufficient to distinguish "rare" from "common" crossing
    - Pre-registration of 30 runs prevents optional stopping

  total_llm_calls: |
    Stage A: 3 models × 30 runs × 500 abstracts = 45,000
    Stage B: 3 models × 30 runs × ~150 abstracts = ~13,500
    Total: ~58,500 LLM calls
    Estimated API cost: ~$50-100 (based on JAIR experience)
```

---

## 11. Provenance Protocol

```yaml
provenance:
  description: "Extended from JAIR paper's lightweight provenance protocol"

  per_call_record:
    - input_hash: "SHA-256 of (prompt_template + abstract_text)"
    - output_hash: "SHA-256 of raw response text"
    - model_id: "exact model identifier"
    - model_version: "version hash or API model name"
    - temperature: 0
    - seed: "model-specific seed value or null"
    - timestamp_utc: "ISO 8601"
    - latency_ms: "response time"
    - token_count: "{input_tokens, output_tokens}"

  per_run_card:
    - run_id: "model_stageX_runNN"
    - batch_hash: "SHA-256 of all input hashes"
    - results_hash: "SHA-256 of all output hashes"
    - n_abstracts: 500
    - n_valid_responses: "count of schema-valid responses"
    - n_invalid_responses: "count of schema-invalid responses"
    - execution_time_total: "seconds"
    - environment: "hardware, OS, Python version, library versions"

  per_model_summary:
    - model_id: "..."
    - n_runs: 30
    - aggregate_metrics: "flip_rate, mean_kappa, mean_F1, pooled_RR_SD"
    - all_run_cards: "[list of run card file paths]"
```

---

*Methods Specification v1.0 — @methodology-specialist*
*Project: paper-2026-002*
*Date: 2026-02-11*
*Ready for Gate 2 review*
