# Reproducibility of Pollution-Health Evidence Synthesis using LLM-Assisted Screening and Extraction

> Can LLM non-determinism alter the conclusions of environmental health meta-analyses?

**Status:** manuscript prepared for *Research Synthesis Methods*. All LLM experiments
are complete. Stage A of the dual-human validation is complete and reported; Stage B
(dual-human extraction) is in progress and is the only work still outstanding.

| Deposit | DOI |
|---------|-----|
| OSF project | [10.17605/OSF.IO/VR934](https://doi.org/10.17605/OSF.IO/VR934) |
| OSF registration — dual-human labeling protocol, frozen 2026-05-12, before any label was collected | [10.17605/OSF.IO/FGN3E](https://doi.org/10.17605/OSF.IO/FGN3E) |

## Overview

This project investigates whether large language model (LLM) non-determinism
introduces unreported variation in evidence synthesis pipelines for environmental
health research (pollution-health associations). We measure instability across
three stages --- abstract screening, data extraction, and meta-analytic pooling ---
and propose a provenance-based mitigation framework.

## Research Questions

| RQ | Question |
|----|----------|
| **RQ1** | Does screening (include/exclude) vary across repeated runs with identical configurations? |
| **RQ2** | Does numerical data extraction (RR/CI95%) vary materially across runs? |
| **RQ3** | Does this variation alter the pooled effect in meta-analysis? |
| **RQ4** | Can a provenance + verification protocol reduce variation and improve auditability? |

## Study Design

- **Domain**: PM2.5 and respiratory hospitalizations (time-series studies)
- **Corpus**: 500 abstracts (100 include / 100 exclude / 300 ambiguous)
- **Source**: PubMed
- **Models**: 6 total
  - **Local** (Ollama): LLaMA 3 8B, Mistral 7B, Gemma 2 9B
  - **Cloud API**: Claude Sonnet 4.5 (Anthropic), Gemini 2.5 Pro (Google), GPT-4.1 (OpenAI)
- **Repetitions**: 10 per model per stage
- **Total**: 36,000 LLM calls across 120 experiment runs

## Pipeline

```
Stage A: Screening       --> include/exclude decisions (10 runs x 6 models = 30,000 calls)
Stage B: Extraction      --> structured JSON with effect estimates (10 runs x 6 models = 6,000 calls)
Analysis: Meta-analytic propagation, semantic equivalence, BERTScore
```

## Human validation of the gold standard

The reference labels used for the secondary accuracy analysis were produced by an
automated keyword rule, so we validated them against human judgement on a stratified
100-abstract subset, labeled independently by two raters blinded to each other. The
protocol was pre-registered on OSF before collection (see DOI above).

Agreement fell **below** the pre-registered Cochrane target of κ ≥ 0.80:

| Quantity | Value | 95% CI |
|---|---|---|
| Cohen's κ, 3-class | 0.529 | [0.383, 0.674] |
| Cohen's κ, binary | 0.556 | [0.400, 0.712] |
| Raw agreement | 75.0% | — |
| Discordances | 25 / 100 | — |

We report this as measured rather than revising the target, which is what the
registration pre-specified for exactly this outcome. Two things make the result
informative rather than merely disappointing.

The disagreement is **directional**, not noise: discordant cells run 2 versus 19
(exact McNemar p = 2.2×10⁻⁴; Stuart-Maxwell χ²(2) = 15.4, p = 4.6×10⁻⁴). It traces to
a single ambiguous inclusion criterion, which the protocol has since been amended to
disambiguate (v1.2). Neither rater departed from the protocol — the protocol was
underspecified.

And agreement is **asymmetric across strata**, which qualifies every accuracy figure
in the paper:

| Stratum | n | Raw agreement | Cohen's κ | PABAK |
|---|---|---|---|---|
| clear-exclude | 25 | 1.000 | undefined (expected agreement = 1) | 1.000 |
| clear-include | 25 | 0.680 | 0.359 | 0.360 |
| ambiguous | 50 | 0.660 | 0.398 | 0.320 |

The exclude side is unanimous, so reported specificity is firm. The include side is
contested, so reported sensitivity is read as a lower bound.

Reproduce these numbers with:

```bash
python scripts/dual_labeling/compute_kappa.py \
  --labeler1 data/dual_labeling/returned/subset_100_labeler1_RETURNED.csv \
  --labeler2 data/dual_labeling/returned/subset_100_labeler2_RETURNED.csv \
  --out data/dual_labeling/results/

python scripts/dual_labeling/kappa_statistics.py \
  --labeler1 data/dual_labeling/returned/subset_100_labeler1_RETURNED.csv \
  --labeler2 data/dual_labeling/returned/subset_100_labeler2_RETURNED.csv \
  --subset data/dual_labeling/exports/subset_100.json \
  --out data/dual_labeling/results/kappa_statistics.json
```

## Prerequisites

- **Python 3.12+** (developed with 3.14.3)
- **Ollama** (for local models): Install from https://ollama.com
- **API Keys** (for cloud models): Anthropic, Google AI, OpenAI

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/Roverlucas/llm-evidence-synthesis-reproducibility.git
cd llm-evidence-synthesis-reproducibility

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
# For exact reproducibility of our environment:
# pip install -r requirements-lock.txt

# 4. Configure API keys (create .env from template)
cp .env.example .env
# Edit .env and add your API keys:
#   ANTHROPIC_API_KEY=sk-ant-...
#   GEMINI_API_KEY=AIzaSy...
#   OPENAI_API_KEY=sk-proj-...

# 5. Pull local models (if running local experiments)
ollama pull llama3:8b
ollama pull mistral:7b
ollama pull gemma2:9b
```

## Running Experiments

```bash
# Run a single model/stage/run
python run_experiment.py --model llama3-8b --stage screening --runs 1-10

# Run all models (caution: takes hours and costs API credits)
python run_experiment.py --model all --stage all --runs 1-10
```

## Running Analysis

```bash
# Main reproducibility analysis (EMR + bootstrap CIs)
python run_analysis.py

# Semantic equivalence + meta-analytic propagation
python analysis/run_semantic_and_meta.py

# BERTScore computation (requires GPU/MPS)
python analysis/compute_bertscore.py

# Timing and cost analysis
python scripts/compute_timing_costs.py

# Or run the full analysis pipeline:
bash run_full_analysis.sh
```

## Running Tests

```bash
pytest tests/ -v
```

## Project Structure

```
src/
  screening/        # Stage A: abstract screening pipeline
  extraction/       # Stage B: structured data extraction
  meta_analysis/    # Stage C: meta-analysis utilities
  provenance/       # Hashing, run cards, audit trail
  models/           # Model runners (Ollama, Claude, Gemini, OpenAI)
  utils/            # Shared utilities
data/
  corpus/           # Abstract corpus (500 PubMed abstracts)
  gold_standard/    # Screening labels from the automated rule (all 500)
  dual_labeling/    # Human validation on a stratified 100-abstract subset
    protocols/      #   labeling protocol (v1.2) + rater guides
    exports/        #   blank templates as sent to the raters
    returned/       #   completed label sets + raw sources + sha256
    results/        #   kappa, intervals, confusion matrix, discordances
    reconciliation/ #   blinded re-rating sheets for the v1.2 round
  raw_outputs/      # Raw LLM outputs per run (tracked for reproducibility)
analysis/
  figures/          # Publication-ready figures
  tables/           # Result tables
  bootstrap/        # Bootstrap CIs (10,000 resamples)
article/            # Manuscript (LaTeX, CUP-JNL-DTM template for RSM)
configs/            # Experiment configurations and prompts
scripts/
  dual_labeling/    # Ingest, agreement statistics, gold-standard consolidation
  blindage/         # Robustness analyses (McNemar, HKSJ, small-literature sim)
  check_pending.sh          # Blocks tagging while any placeholder remains
  verify_reported_numbers.py # Checks manuscript figures against source JSONs
tests/              # Automated tests (pytest)
docs/
  project_charter/  # Project charter and scope
  decisions/        # Decision log
  submission_checklist.md        # What is blocked, and on whom
  osf_subregistration_update.md  # Registered contingency, item (d)
```

### Guards against stale numbers

Two scripts exist because prose drifts away from code. `verify_reported_numbers.py`
confronts every agreement figure asserted in the manuscript against the JSON that
produced it, and checks that it appears in each document that must state it.
`check_pending.sh` refuses to let a submission be tagged while any placeholder,
promissory phrase, or undeclared protocol deviation survives. Both are wired into the
test suite where applicable.

## Key Outputs

| File | Description |
|------|-------------|
| `analysis/reproducibility_results.json` | EMR + bootstrap CIs for all models |
| `analysis/semantic_and_meta_results.json` | Semantic equivalence + meta-analysis |
| `analysis/bertscore_results.json` | BERTScore F1 (all-pairs, roberta-large) |
| `analysis/timing_and_costs.json` | Timing and cost breakdown |
| `analysis/figures/emr_comparison.pdf` | EMR comparison bar chart |
| `analysis/figures/field_emr_heatmap.pdf` | Field-level EMR heatmap |
| `analysis/fleiss_kappa.json` | Inter-run Fleiss' κ per deployment stack |
| `data/dual_labeling/results/kappa_report.json` | Human Cohen's κ, confusion matrix, discordance list |
| `data/dual_labeling/results/kappa_statistics.json` | Intervals, PABAK, Byrt indices, marginal-homogeneity tests, per-stratum agreement |

## Related Work

This study builds on the provenance protocol developed in:

> "Hidden Non-Determinism in Large Language Model APIs: A Lightweight Provenance
> Protocol for Reproducible Generative AI Research" (JAIR, 2026)
> [Repository](https://github.com/Roverlucas/genai-reproducibility-protocol)

## Citing

If you use this code or data, please cite the OSF deposit until the article appears:

> Rover, L., & de Souza Tadano, Y. (2026). *Reproducibility of Pollution–Health
> Evidence Synthesis using LLM-Assisted Screening and Extraction*. Open Science
> Framework. https://doi.org/10.17605/OSF.IO/VR934

The labeling protocol has its own registration DOI
([10.17605/OSF.IO/FGN3E](https://doi.org/10.17605/OSF.IO/FGN3E)) and should be cited
directly when referring to the pre-commitment rather than to the study.

## License

Code under MIT. Data, prompts, and manuscript materials under CC BY 4.0.
Abstracts are PubMed metadata and remain subject to their original terms.
