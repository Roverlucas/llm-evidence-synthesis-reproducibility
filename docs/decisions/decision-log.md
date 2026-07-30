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

## 14 — 2026-05-12 · OSF pre-registration of the human validation protocol
Registered the dual-labeling protocol as a frozen OSF registration (`fgn3e`, DOI
`10.17605/OSF.IO/FGN3E`) from component `8z6fy`, two months before any label was
collected. Registered the κ≥0.80 target *and* a contingency for missing it. The
contingency is what made the 2026-07-29 outcome orderly instead of improvised.
Note for future writing: `vr934` is a project, `fgn3e` is a registration — only the
second supports the phrase "pre-registered".

## 15 — 2026-07-29 · κ = 0.529 reported as measured; target not revised
Stage A closed below the pre-registered target (κ=0.529, 95% CI [0.383, 0.674];
25% discordance against an expected <15%). Both gates reported as missed. Rejected
the alternative of softening the target or reframing it as aspirational after the
fact. Ruled out the kappa-paradox explanation (prevalence index 0.189, PABAK≈κ) and
the scale explanation (weighted κ within 0.02).

## 16 — 2026-07-29 · Protocol amended to v1.2 (criterion 5)
17 of the 19 asymmetric discordances traced to one ambiguous criterion, plus a
decision table that never covered clear failure in exactly one criterion. Amended
per item (c) of the registered contingency: criterion 5 split into levels 5a/5b/5c
with 5b resolving to *uncertain*; structural criteria separated from conditional
ones. Amendment written after the κ was known, and that sequence is disclosed.

## 17 — 2026-07-29 · Recalibration round produces no second κ
Re-rating only the 25 discordant items cannot yield a comparable coefficient:
conditioning on prior disagreement raises a recomputed full-corpus κ mechanically,
crossing the Cochrane threshold by construction at a high enough resolution rate.
Reported as post-hoc reconciliation agreement conditional on those items. Validating
v1.2 properly needs a fresh independent sample (n≈30–40) — registered as a next step,
not claimed as a result. `build_gold_standard.py` was changed to refuse to emit such
a coefficient at all.

## 18 — 2026-07-29 · Tie-breaker reassigned Y.d.S.T. → L.R. — **SUPERSEDED by 22**
Decided by Lucas, then reverted the same day. Kept in this log because a decision log
that quietly deletes reversed decisions is not an audit trail. See entry 22 for the
reversal and its reasoning.

## 19 — 2026-07-29 · Stage-B extraction subset rebuilt from the human gold standard
The registered 25-item extraction subset came from the LLM silver standard; only 13
survive human consensus. Scoring models against a model-derived reference is circular,
so the subset is rebuilt from human labels. The 13/25 overlap is kept and reported as
a finding.

## 20 — 2026-07-29 · Gold standard declared asymmetrically valid
Stratified agreement: clear-exclude unanimous (25/25), clear-include 0.680 (κ=0.359),
ambiguous 0.660 (κ=0.398). Consequence adopted throughout the manuscript: specificity
is treated as firm, sensitivity as a lower bound. The automated rule's "100% precision"
claim replaced by a rule-of-three bound (≈6%).

## 21 — 2026-07-29 · κ≥0.80 comparisons rewritten as non-commensurable
EMR and inter-run Fleiss' κ measure one stack reproducing itself; Cohen's κ measures
two raters agreeing. Mistral-7B (EMR=1.000, specificity 0.240) makes the distinction
concrete. Removed the claim that the stacks "reach the Cochrane guideline".

## 22 — 2026-07-29 · Tie-breaker reverted to Y.d.S.T. (supersedes 18)
Decided by Lucas after learning that registration `fgn3e` names the senior author
explicitly — a fact not available when 18 was taken. Two reasons to revert, in order
of weight. First, independence: L.R. developed the pipeline whose outputs are scored
against this gold standard, so having L.R. adjudicate contested labels would make the
reference standard partly dependent on the author whose system it evaluates. Second,
there is no longer any pre-registration deviation on roles to declare or defend, which
removes a line of attack for free.

Net effect on the submission: the only deviations from `fgn3e` that remain are the
substitution of the Stage-B extraction subset (entry 19) and the post-hoc statistics
added beyond the registered point estimates. Neither concerns who decides what.
