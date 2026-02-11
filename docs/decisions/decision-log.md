# Decision Log

| # | Date | Decision | Alternatives | Rationale | Decided by |
|---|------|----------|-------------|-----------|------------|
| 1 | 2026-02-11 | Scope to PM2.5 → respiratory hospitalizations | NO₂/asthma, O₃/cardiovascular, smoke/hospitalizations | Most abundant literature with standardized RR reporting; cleaner time-series design | Study Conductor |
| 2 | 2026-02-11 | Corpus size = 200 abstracts | 300, 500 | Balances gold-standard feasibility with statistical power; 50/50/100 split ensures all categories covered | Study Conductor |
| 3 | 2026-02-11 | 3 models: LLaMA 3 8B + Claude Sonnet + Gemini 2.5 Pro | More models, GPT-4 | Reuses JAIR infrastructure; covers local vs API comparison; OpenAI quota exhausted | Study Conductor |
| 4 | 2026-02-11 | 30 repetitions per model per stage | 10, 50, 100 | Sufficient for bootstrap CIs and kappa estimation; manageable API cost | Study Conductor |
| 5 | 2026-02-11 | Defer GRADE/policy variants to follow-up | Include in v1 | Prevents scope creep; core 4 RQs are already a complete paper | Study Conductor |
| 6 | 2026-02-11 | Public repository from start | Private until submission | Aligns with open science principles and reproducibility thesis | Study Conductor |
| 7 | 2026-02-11 | Corpus increased to 500 abstracts (100/100/300) | 200 (50/50/100) | Greater statistical robustness; larger ambiguous pool for meaningful variation detection | Study Conductor + PI |
| 8 | 2026-02-11 | Primary journal: Research Synthesis Methods | J Clin Epidemiol, npj Dig Med, Environ Int | Best scope fit for evidence synthesis methodology; already publishing LLM+SR papers; hybrid (no APC for subscription) | Literature Specialist + Journal Strategy |
| 9 | 2026-02-11 | 28 references mapped across 6 domains, 3 primary gaps identified | — | Evidence matrix complete for Phase 1; 3 P0 gaps justify all 4 RQs | Literature Specialist |
| 10 | 2026-02-11 | Study design: Repeated-measures computational experiment | Single-run accuracy, multi-prompt comparison, simulation | Only repeated-measures isolates non-determinism as sole source of variation | Methodology Specialist |
| 11 | 2026-02-11 | Reporting guideline: Hybrid STROBE-Computational + PRISMA-S | Pure STROBE, pure PRISMA, custom-only | No single guideline fits computational reproducibility experiment; hybrid captures all aspects | Methodology Specialist |
| 12 | 2026-02-11 | Meta-analysis estimator: DerSimonian-Laird random-effects | REML, Hartung-Knapp | Comparability with existing PM2.5 meta-analyses (Atkinson 2014, Zheng 2015) | Methodology Specialist |
| 13 | 2026-02-11 | Total ~58,500 LLM calls (45K screening + 13.5K extraction) | Fewer runs, fewer abstracts | 30 runs × 500 abstracts provides sufficient power for bootstrap CIs and kappa estimation | Methodology Specialist |
