# OSF Project — README

**Project Title**: Reproducibility of Pollution–Health Evidence Synthesis using LLM-Assisted Screening and Extraction

**Short Title**: LLM Evidence Synthesis Reproducibility

**Status**: Manuscript under review at *Research Synthesis Methods* (Wiley, IF 6.1)

**Last updated**: 2026-05-11

---

## Overview

This OSF project hosts the materials underpinning the manuscript *"Reproducibility of Pollution–Health Evidence Synthesis Using LLM-Assisted Screening and Extraction"* by Rover and Tadano.

We measure whether large language model (LLM) non-determinism propagates through the full evidence-synthesis pipeline — abstract screening, numerical data extraction, and meta-analytic pooling — and whether this variation can alter conclusions in environmental health systematic reviews of PM2.5 and respiratory hospitalizations.

## Research Questions

| RQ | Question |
|----|----------|
| RQ1 | Does abstract screening vary across repeated runs of identical LLM configurations? |
| RQ2 | Does numerical data extraction (RR/CI95%) vary materially across runs? |
| RQ3 | Does this variation alter the pooled effect in a downstream meta-analysis? |
| RQ4 | Can a provenance + verification protocol reduce variation and improve auditability? |

## Study Design

- **Domain**: PM2.5 and respiratory hospitalizations (time-series studies)
- **Corpus**: 500 PubMed abstracts (100 include / 100 exclude / 300 ambiguous)
- **Deployment stacks evaluated**: 6 (3 local Ollama + 3 cloud APIs) + 1 quasi-isolation probe (DeepInfra hosting LLaMA 3 8B)
- **Repetitions**: 10 runs per stack per stage
- **Total LLM calls**: ~36,000 across 120 experiment runs (plus extensions)
- **Silver standard**: DeepSeek-R1 (independent provider/architecture/decoding paradigm) — 5 runs
- **Heuristic gold standard**: keyword rule, validated to 100% precision on a 50-abstract held-out set

## Unit of Analysis

Following methodological discussion in the parallel revision of our companion paper (Rover & Tadano, under review at *Nature Communications*), the unit of analysis throughout is the **deployment stack**: the tuple `(model_weights, provider, infrastructure, API_layer)`. For local Ollama stacks the tuple is transparent (weights hash, single-GPU M4, single replica). For cloud-API stacks the provider/infrastructure/API_layer are partially opaque — making this study a partial quasi-isolation probe rather than a comparison of pure model weights.

## OSF Components

This top-level project contains the following components, each with its own DOI:

1. **Manuscript** — current draft + supplementary material (PDF + LaTeX source)
2. **Data** — corpus, raw LLM outputs, gold standards
3. **Code** — link to GitHub repository (frozen commit hash)
4. **Analyses** — JSON outputs of all statistical analyses (blindage suite, Fleiss' κ, BERTScore, HKSJ sensitivity, etc.)
5. **Pre-Registration: Dual-Human Labeling Protocol** — formal pre-commitment to dual-independent human labeling (Stage A: 100 abstracts; Stage B: 25 extractions), Cohen's κ ≥ 0.80 target, currently in progress

## Reproducibility

- All analysis code: https://github.com/Roverlucas/llm-evidence-synthesis-reproducibility
- Frozen commit at time of OSF deposit: `38873a2`
- All randomness seeded with `seed = 42`
- SHA-256 provenance hashes embedded in every JSON output
- Tests: 108/108 passing
- Manuscript compiles cleanly: main 29 pp, supplementary 19 pp

## Companion Paper

Methodological and theoretical companion under major revision at *Nature Communications*:

> Rover, L., & Tadano, Y. S. (in revision). *Same Prompt, Different Answer: Hidden Non-Determinism in LLM APIs Undermines Scientific Reproducibility*. Nature Communications. Figshare DOI: 10.6084/m9.figshare.31653373

## License

CC-BY 4.0 for data and manuscript materials; MIT for code (see GitHub LICENSE).

## Citation

```bibtex
@misc{rover2026rsm_osf,
  title  = {Reproducibility of Pollution–Health Evidence Synthesis using LLM-Assisted Screening and Extraction},
  author = {Rover, Lucas and Tadano, Yara de Souza},
  year   = {2026},
  doi    = {10.17605/OSF.IO/VR934},
  note   = {OSF Project, manuscript under review at Research Synthesis Methods}
}
```

**OSF project URL**: https://osf.io/vr934 — registered 2026-05-11.

## Contact

Lucas Rover — lucasrover@alunos.utfpr.edu.br — ORCID 0000-0001-6641-9224
