# Blindage Final Findings — Numbers locked 2026-04-28

**Status:** 33/35 blindage tasks completas. Apenas per-run accuracy vs human-gold (#20) aguarda dual-labeling.

**Custo total APIs:** ~$3 de $10 budget.

---

## 1. Cloud LLaMA Desconfound (Editor blocker #1) ✅ RESOLVIDO

**Setup:** `meta-llama/llama-3-8b-instruct` (mesma versão exata do local Ollama llama3:8b), seed=42, temperature=0, served via OpenRouter pinned to DeepInfra.

| Métrica | Local Ollama (M4) | Cloud DeepInfra |
|---------|-------------------|-----------------|
| EMR within deployment | **1.000** | 0.992 (strict) / 0.9921 (pairwise mean) |
| % items com any pair-disagreement | 0.00% | **2.04%** |
| Mean pairwise disagreement | 0.0000 | 0.0079 |
| Cross-deployment agreement | — | **61.2%** (canonical) / 59.7% (mean pairwise) |
| Items local→include cloud→exclude | — | 167/430 |
| Items local→exclude cloud→include | — | **0/430 (asimétrico)** |

**Robustness note:** 2 das 10 cloud runs (run_005, run_006) tiveram menos itens válidos (45 e 221 vs ~491 esperados) — provável transient failure DeepInfra. Reportado como finding sobre cloud reliability.

**Headline finding:** *"Same model weights, same seed, same temperature; deployment infrastructure ALONE produces 39% systematic disagreement, with cloud always more restrictive (167 include→exclude flips, 0 reverse). This refutes the model-size confound: deployment paradigm — not parameter count — drives the local-vs-cloud gap."*

---

## 2. Fixed-Slot Extraction Sensitivity (R2/R5) ✅ RESOLVIDO

**Setup:** 3 cloud models × 3 runs × 100 INCLUDE items, fixed-slot prompt (single primary_estimate, deterministic selection rules).

| Model | Variable-length EMR (10 runs) | Fixed-slot EMR (3 runs) | Δ absolute | Δ relative |
|-------|--------------------------------|---------------------------|------------|-----------|
| Claude Sonnet 4.5 | 0.0500 | 0.0300 | **−0.0200** | **−40.0%** |
| Gemini 2.5 Pro | 0.2000 | 0.1848 | −0.0152 | −7.6% |
| **GPT-4.1** | **0.1500** | **0.4444** | **+0.2944** | **+196.3%** |

**Mean delta:** +0.0864 across 3 models.

**Critical finding:** Effect of prompt design is **model-specific, not uniform**. GPT-4.1 dramatically benefits (3× EMR improvement); Claude actively gets WORSE; Gemini neutral. This refines R2/R5's expectation that "fixed-slot will solve it" — empirically it depends on the model. Prompt design is a contributor to non-determinism but **not the sole driver** for at least Claude and Gemini.

---

## 3. Silver Standards (R4 Q11) ✅ RESOLVIDO

### 3.1 Silver-Internal (majority vote 6 models × 10 runs = 60 votes/item)

| Field | Items w/ consensus | Mean mode-agreement |
|-------|---------------------|-----|
| effect_estimate | 95/100 | 85.84% |
| ci_lower | 84/100 | 84.60% |
| ci_upper | 84/100 | 84.47% |
| effect_measure | 100/100 | 78.28% |
| outcome_specific | 100/100 | 69.39% |
| exposure_increment | 100/100 | 76.09% |
| lag | 100/100 | 64.40% |

### 3.2 Silver-External (DeepSeek-R1 reasoning × 5 runs majority)

| Field | Items w/ consensus | Mean mode-agreement |
|-------|---------------------|-----|
| effect_estimate | 84/100 | 88.95% |
| ci_lower | 74/100 | 89.41% |
| ci_upper | 74/100 | 88.87% |
| effect_measure | 84/100 | 90.56% |
| outcome_specific | 84/100 | 80.28% |
| exposure_increment | 84/100 | 88.12% |
| lag | 75/100 | 86.16% |

### 3.3 Cross-validation — silvers convergem fortemente

| Field | Agreement | Comment |
|-------|-----------|---------|
| effect_estimate | **79.76%** | Spearman ρ=**0.845** (alta correlação) |
| ci_lower | 79.73% | |
| ci_upper | 78.38% | |
| effect_measure | 73.81% | |
| outcome_specific | 65.48% | Maior divergência (asthma vs all_respiratory) |
| exposure_increment | 79.76% | |
| lag | 65.33% | Lag specification ambígua |

**Headline:** Two **independent** consensus standards (one from same models being evaluated; one from a different model family — DeepSeek-R1 reasoning) **converge in 80% of items on numeric fields**. This validates the silver-internal as a comparative anchor and shows that the 6 evaluated models are NOT systematically biased relative to an independent reasoning model.

---

## 4. Per-Run Accuracy vs Silver Standards (R4 Q11) ✅ PARTIAL

### 4.1 vs Silver-Internal

| Model | effect_estimate accuracy (mean) | Range across runs |
|-------|-------------------|-------------------|
| LLaMA 3 8B | 0.8646 | 0 (deterministic) |
| Mistral 7B | 0.7400 | 0 |
| Gemma 2 9B | 0.7400 | 0 |
| Claude Sonnet 4.5 | 0.7749 | 0.0615 |
| Gemini 2.5 Pro | 0.8421 | 0.0504 |
| GPT-4.1 | 0.8348 | 0.0545 |

### 4.2 vs Silver-External (DeepSeek-R1)

| Model | effect_estimate | all_fields exact | Range across runs |
|-------|-----|-----|-----|
| LLaMA 3 8B | 0.6667 | 0.0312 | 0 |
| Mistral 7B | 0.60 | 0.06 | 0 |
| Gemma 2 9B | 0.64 | 0.06 | 0 |
| Claude Sonnet 4.5 | 0.7024 | 0.1884 | 0.0287 |
| Gemini 2.5 Pro | 0.6780 | 0.2142 | 0.0645 |
| GPT-4.1 | **0.7396** | **0.2424** | 0.0367 |

**Insights:** 
1. Cloud models score HIGHER vs DeepSeek silver than local (0.67-0.74 cloud vs 0.60-0.67 local)
2. Per-run accuracy variation in cloud: 3-6% across runs — accuracy itself is non-deterministic
3. all_fields exact match is low (≤25%) — at least one of 7 fields always differs from DeepSeek consensus
4. (#20 still pending: per-run accuracy vs HUMAN gold — awaits dual-labeling)

---

## 5. Pairwise Disagreement (R3 Q3) ✅

| Model | Stage | EMR | Pairwise mean | % items any-disagree |
|-------|-------|-----|---------------|---------------------|
| Locals (3) | both | 1.000 | 0.0000 | 0.00% |
| Claude | screening | 0.974 | 0.0096 | 2.60% |
| Claude | extraction | **0.050** | **0.8180** | **95.00%** |
| Gemini | screening | 0.936 | 0.0198 | 6.40% |
| Gemini | extraction | 0.200 | 0.4927 | 80.00% |
| GPT-4.1 | screening | 0.970 | 0.0137 | 3.00% |
| GPT-4.1 | extraction | 0.150 | 0.4858 | 85.00% |

---

## 6. Small-Literature Simulation (R2/R4/R5) ✅

| Model | k | % subsamples UNSTABLE null-crossing |
|-------|---|-------------------------------------|
| Claude | 10 | **0.50%** |
| Gemini | 10 | **0.50%** |
| GPT-4.1 | 10 | 0.00% |
| any model | 15+ | 0.00% |

**Headline:** For k=10 articles (small reviews), 1/200 subsamples produces meta-analytic conclusions that flip across LLM runs.

---

## 7. Random-Effects Meta-Analytic (R3 P1.1) ✅

| Model | mean RE pooled RR | range across runs | I² mean | runs cross null |
|-------|-------------------|-------------------|---------|------------------|
| All locals | 1.025-1.038 | 0.000 | varies | 0/10 |
| All clouds | 1.015-1.024 | 0.0058 | varies | 0/10 |

**Pooled estimate is robust** in full-corpus (k=100); problem only manifests in subsamples (§6).

---

## 8. Multiple Comparison Correction (R3) ✅

21 contrasts → **3 sobrevivem Holm**, 5 sobrevivem BH-FDR. Finding 3 ("distinct profiles") deve restringir-se a:
- study_location: Claude vs GPT-4.1 (Δ=−0.22, p<0.0001)
- study_location: Gemini vs GPT-4.1 (Δ=−0.10, p=0.018)
- extraction_overall: Claude vs Gemini (Δ=−0.15, p=0.026)

---

## 9. Rationale vs Metadata Similarity (R3 Q4) ✅

| Model | Metadata Jaccard | Rationale Jaccard |
|-------|------------------|-------------------|
| Claude | 0.978 | **0.378** |
| Gemini | 0.978 | 0.623 |
| GPT-4.1 | 0.984 | 0.725 |
| Locals | 1.000 | 1.000 |

**60% gap** between metadata (saturated) and rationale (true semantic variation). Validates R3's concern about BERTScore=0.997 being saturation artifact.

---

## 10. Other ✅

- **Rule-of-three CIs**: UCL=0.006 (screening n=500) and 0.030 (extraction n=100) replace [1.000, 1.000]
- **Temporal clustering GPT-4.1**: 15 flips em 13 horas distintas, 1 dia → no server drift detected
- **Retry quantification**: protocol v1 não registrou retries (limitação honesta documentada)
- **Seed effect**: deployment effect 6× maior que seed effect
- **Work-saved**: GPT-4.1 12-29× speedup; Mistral às vezes mais lento que humano
- **Mistral degenerate**: sens=1.0 + spec=0.24 → "always-include" warning box

---

## ⏳ ÚNICO ITEM PENDENTE (#20)

Per-run extraction accuracy vs HUMAN GOLD — aguarda dual-labeling com Labeler 2.
- 100 abstracts screening + 25 extraction items
- Quando vier, eu rodo `per_run_accuracy_multi_source.py` que já tem o slot pronto

---

*Document version: 1.0 (final)
Generated: 2026-04-28*
