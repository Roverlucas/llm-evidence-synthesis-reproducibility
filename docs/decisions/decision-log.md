# Decision Log

| # | Date | Decision | Alternatives | Rationale | Decided by |
|---|------|----------|-------------|-----------|------------|
| 1 | 2026-02-11 | Scope to PM2.5 → respiratory hospitalizations | NO₂/asthma, O₃/cardiovascular, smoke/hospitalizations | Most abundant literature with standardized RR reporting; cleaner time-series design | Study Conductor |
| 2 | 2026-02-11 | Corpus size = 200 abstracts | 300, 500 | Balances gold-standard feasibility with statistical power; 50/50/100 split ensures all categories covered | Study Conductor |
| 3 | 2026-02-11 | 3 models: LLaMA 3 8B + Claude Sonnet + Gemini 2.5 Pro | More models, GPT-4 | Reuses JAIR infrastructure; covers local vs API comparison; OpenAI quota exhausted | Study Conductor |
| 4 | 2026-02-11 | 30 repetitions per model per stage | 10, 50, 100 | Sufficient for bootstrap CIs and kappa estimation; manageable API cost | Study Conductor |
| 5 | 2026-02-11 | Defer GRADE/policy variants to follow-up | Include in v1 | Prevents scope creep; core 4 RQs are already a complete paper | Study Conductor |
| 6 | 2026-02-11 | Public repository from start | Private until submission | Aligns with open science principles and reproducibility thesis | Study Conductor |
