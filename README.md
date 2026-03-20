# Reproducibility of Pollution-Health Evidence Synthesis using LLM-Assisted Screening and Extraction

> Can LLM non-determinism alter the conclusions of environmental health meta-analyses?

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
  gold_standard/    # Screening labels (heuristic + dual-human for 200)
  raw_outputs/      # Raw LLM outputs per run (tracked for reproducibility)
analysis/
  figures/          # Publication-ready figures
  tables/           # Result tables
  bootstrap/        # Bootstrap CIs (10,000 resamples)
article/            # Manuscript (LaTeX, CUP-JNL-DTM template for RSM)
configs/            # Experiment configurations and prompts
tests/              # Automated tests (pytest)
docs/
  project_charter/  # Project charter and scope
  decisions/        # Decision log
```

## Key Outputs

| File | Description |
|------|-------------|
| `analysis/reproducibility_results.json` | EMR + bootstrap CIs for all models |
| `analysis/semantic_and_meta_results.json` | Semantic equivalence + meta-analysis |
| `analysis/bertscore_results.json` | BERTScore F1 (all-pairs, roberta-large) |
| `analysis/timing_and_costs.json` | Timing and cost breakdown |
| `analysis/figures/emr_comparison.pdf` | EMR comparison bar chart |
| `analysis/figures/field_emr_heatmap.pdf` | Field-level EMR heatmap |

## Related Work

This study builds on the provenance protocol developed in:

> "Hidden Non-Determinism in Large Language Model APIs: A Lightweight Provenance
> Protocol for Reproducible Generative AI Research" (JAIR, 2026)
> [Repository](https://github.com/Roverlucas/genai-reproducibility-protocol)

## License

MIT
