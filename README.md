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
- **Source**: PubMed / Scopus
- **Models**: 6 (3 local via Ollama: LLaMA 3 8B, Mistral 7B, Gemma 2 9B + 3 cloud APIs: Claude Sonnet 4.5, Gemini 2.5 Pro, GPT-4.1)
- **Repetitions**: 10 per model per stage
- **Gold standard**: Dual-human labeling with discordance resolution

## Pipeline

```
Stage A: Screening       --> include/exclude decisions (10 runs x 6 models = 30,000 calls)
Stage B: Extraction      --> structured JSON with effect estimates (10 runs x 6 models = 6,000 calls)
Analysis: Meta-analytic propagation, semantic equivalence, BERTScore
Total: 36,000 LLM calls across 120 experiment runs
```

## Project Structure

```
src/
  screening/        # Stage A: abstract screening pipeline
  extraction/       # Stage B: structured data extraction
  meta_analysis/    # Stage C: random-effects meta-analysis
  provenance/       # Hashing, run cards, audit trail
  models/           # Model runners (Ollama, Claude, Gemini)
  utils/            # Shared utilities
data/
  corpus/           # Abstract corpus (PubMed/Scopus exports)
  gold_standard/    # Human-labeled ground truth
  raw_outputs/      # Raw LLM outputs per run
analysis/
  figures/          # Publication-ready figures
  tables/           # Result tables
  bootstrap/        # Bootstrap CIs and robustness checks
article/            # Manuscript (LaTeX)
configs/            # Experiment configurations (YAML)
tests/              # Automated tests (pytest)
docs/
  project_charter/  # Project charter and scope
  decisions/        # Decision log
  sessions/         # Session handoffs
```

## Related Work

This study builds on the provenance protocol developed in:

> "Hidden Non-Determinism in Large Language Model APIs: A Lightweight Provenance
> Protocol for Reproducible Generative AI Research" (JAIR, 2026)
> [Repository](https://github.com/Roverlucas/genai-reproducibility-protocol)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Project Log

See [PROJECT_LOG.md](PROJECT_LOG.md) for session history, decisions, and next steps.

## License

MIT
