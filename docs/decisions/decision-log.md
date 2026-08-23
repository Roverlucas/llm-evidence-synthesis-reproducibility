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

## 23 — 2026-08-08 · Recalibration round sent as one joint message, due 22 Aug
Decided by Lucas. The v1.2 package (blinded 25-item sheet per labeler, protocol, cover
note) went out in a single email to both labelers with the senior author in copy, rather
than the two separate threads drafted first. The separate-thread draft was a reaction to
the round-one incident, where one labeler received the other's template and the role had
to be reassigned after ingestion; that failure mode is now handled upstream instead, by
`export_recalibration_xlsx.py`, which stamps the labeler's name onto the file name, the
identification header and the instructions sheet, and refuses to write a sheet carrying
a foreign labeler column or a pre-filled decision.

Blinding is unaffected either way — the sheets contain no decision from either round or
either rater. The exposure a joint thread does create is on the return leg, so the email
asks for the filled sheet to come back to the sender alone rather than reply-all, which
would put one labeler's decisions in front of the other before she closes her own.

Deadline 22 August 2026, against ~50 minutes of work. What follows on return:
`build_gold_standard.py` → `rebuild_extraction_set.py` → Stage B. This round still does
not produce a second κ (entry 17).

## 24 — 2026-08-08 · Contingency item (d) discharged: sub-registration update posted
The κ<0.80 contingency registered in `fgn3e` required four things; (a) transparent
reporting, (b) qualitative examination of the disagreement and (c) the protocol
amendment were done on 2026-07-29, leaving (d), documenting the deviation in a
sub-registration update, outstanding since then. It is now posted on component `8z6fy`,
public and readable without a login, as both a wiki page (`ecd9h`) and a file,
`sub-registration-update-2026-07-29.md`, whose sha256 matches the source in
`docs/osf_subregistration_update.md` byte for byte.

Posted to the component, not to `fgn3e`. Editing a registration is neither possible nor
desirable: its immutability is the property that makes citing it meaningful, and an
amendable pre-registration would be no pre-registration at all.

Two forms rather than one because they answer different questions. The wiki is what a
reader lands on from the component page; the file is what a reader can download and
hash against the repository. The nine files already deposited on the component were
verified intact after the upload.

With this, every deviation from `fgn3e` is now declared in a citable public location:
the missed κ target, the protocol amendment written after the κ was known, the
Stage-B subset substitution (entry 19), the post-hoc statistics, and the tie-breaker
reconsideration that was reverted (entries 18 and 22).

## 25 — 2026-08-19 · Labeler1 recalibration ingested; movement is one-directional
Isabelle returned the blinded v1.2 sheet three days before the deadline. All 25 items
complete, ids and abstracts byte-identical to what was sent, no column from the other
labeler present. Archived at
`data/dual_labeling/reconciliation/returned/recalibration_labeler1_RETURNED{.csv,_SOURCE.xlsx}`,
source sha256 `23d3ea92...e966725`.

Round 2 counts 13 EXCLUDE / 9 UNCERTAIN / 3 INCLUDE. Eight of the 25 moved against her own
round-1 decision, and every one of them moved the same way — seven EXCLUDE→UNCERTAIN and one
EXCLUDE→INCLUDE, with no movement in the opposite direction. That is the shape predicted on
2026-08-08 from the CI heuristic, which found a numeric interval in only 5 of the 19
asymmetric cases: rule 5b routes an abstract that claims an effect without reporting it to
UNCERTAIN rather than to INCLUDE. Seven of the eight landed on 5b.

The prediction holding is not itself evidence that the amendment works. Both the heuristic
and rule 5b read the same feature of the abstract — whether numeric values are present — so
agreement between them is close to mechanical. What it does support is narrower: the round-1
disagreement was information the protocol failed to ask for, not two readers judging the same
evidence differently.

Ingestion is a new script, `ingest_recalibration_xlsx.py`, because the v1.1 ingestor's
criteria vocabulary is `[1-6]` and would reject the 5a/5b/5c levels v1.2 exists to introduce.
It validates the return against the §4 decision table, which is fully deterministic, and the
25 rows are consistent with it on every row. A bare `5` is rejected rather than resolved:
that ambiguity is what produced κ=0.529, and a script that guessed would hide its return.
25 tests cover the table, including the 5b/5c divergence and the Excel `4.0` artefact.

No coefficient computed, per entry 17. Still blocked on labeler2 before
`build_gold_standard.py` can run.

## 26 — 2026-08-19 · Misattributed citation to the target journal's own guidance, corrected
`main.tex:917` claimed "Cambridge RSM guidance §4.3 requires empirical reporting of
seed-parameter effectiveness on commercial APIs". Verified against the source: there is no
§4.3. The document has five numbered sections and no numbered subsections, and section 4 is
"Reproducibility and transparency". What it actually requires is documenting specific
random-seed values, and for commercial models, API versions and access dates. It never asks
for an empirical test of whether the seed works — which is precisely the gap Finding 6 fills.

The bib entry was wrong on every field that identifies the work. Key `weber2025...` names an
author who is not on the paper. Two authors were listed where there are six, in reverse
position: Pigott is last, not first, and her name is Terri, not Therese. No DOI, volume,
number or pages. Correct record: Farotimi, Dunn, Van Lissa, Polanin, Mavridis & Pigott,
Research Synthesis Methods 17(2), 237–239, doi:10.1017/rsm.2025.10058, published 11 Dec 2025.

This one mattered more than an ordinary citation defect. The misattribution was to the
editorial board of the journal we are submitting to, in a manuscript about the reliability of
AI-assisted evidence synthesis, and the fabricated element was a section number — the kind of
specificity a reader reads as evidence the source was opened. Two of the six authors would
have been reviewing it.

Rewritten to what the guidance says, which is rhetorically stronger: the journal requires the
seed to be documented but stops short of establishing whether documenting it delivers
determinism. Finding 6 answers a question its own guidance leaves open. Recompiled with
TinyTeX: 33pp, zero undefined references. Note that TeX Live 2026 basic cannot build this
document at all — `etoc.sty` is missing there.

## 27 — 2026-08-19 · The CAPES agreement does not cover this journal
RSM left Wiley at the end of 2024 and has been published by Cambridge University Press since
2025. The manuscript already targets Cambridge (`main.tex:5`, class `CUP-JNL-DTM`), but the
funding consequence was never recorded: no file in `article/` or `docs/` mentions APC, open
access or CAPES.

Two independent exclusions. Cambridge is not among the seven publishers in the CAPES
2026–2028 cycle (ACS, ACM, Elsevier, IEEE, Royal Society, Springer Nature, Wiley). And RSM is
wholly gold OA, which the agreement excludes on its own terms — it covers hybrid titles only.
APC is £2,610 / US$3,655. Under Wiley this would have been covered.

Cambridge's Open Equity Initiative does not list Brazil; its Group B is Botswana, Colombia,
Egypt, Georgia and Namibia. What remains is an individual waiver request, which Cambridge
states it accepts from any corresponding author not otherwise covered.

Consequence for the backup list: of the three, only J Clin Epidemiol (Elsevier, hybrid,
IF 5.8) is plausibly APC-free. npj Digital Medicine and BMC Med Res Methodol are both gold OA
under Springer Nature and fail the hybrid-only rule. Evidence levels: E0 for the publisher and
for the absence of any APC mention in the repo; E1 for the publisher list; E2 for the APC
figure and the Equity Initiative, where cambridge.org returned HTTP 429 on direct reads.

## 28 — 2026-08-19 · Citation audit: the §4.3 defect was not isolated
Swept all 51 bib entries after entry 26, checking key-to-author consistency, truncated author
lists, and missing identifiers, then verified the suspicious ones against the source. Most of
what the sweep flagged is noise — arXiv preprints legitimately have no DOI and `and others` is
ordinary shorthand. What survived verification is a recurring pattern of wrong identity, not
missing metadata:

| Entry | Defect | Source |
|---|---|---|
| `oami2024screening` | author **Takeshi** → Takehiko Oami; issue 6 → **7** | PMID 38976267 |
| `li2025jamia` | author **Jun Li** → Ying Li (+9 co-authors); pages 789–801 → **616–625** | doi:10.1093/jamia/ocaf030 |
| `karelin2024indeterminism` | year 2024 → **2025** | PhilSci-Archive 26807 |
| `cochrane2024_ai_guidance` | **source does not exist** — see below | url 404 |

Three of the four are a wrong given name or a wrong locator on a real paper: the same defect
as Therese/Terri Pigott. The internal tell was already in the file — `oami2024screening` and
`oami2025optimal` are the same author under two different first names, one of them wrong.
These are references filled in without opening the source.

`cochrane2024_ai_guidance` is the serious one. Its URL, https://methods.cochrane.org/ai-guidance,
returns 404, and no Cochrane document by that title exists. `main.tex:85` uses it to assert
that Cochrane "requires that AI-assisted SR tools report inter-run agreement statistics — which
the paired EMR and pairwise-disagreement reporting in this paper supplies". That is a fabricated
normative requirement the paper then claims to satisfy, sitting on the line directly after the
fabricated RSM §4.3 of entry 26. Two consecutive sentences, same construction, two different
standards bodies.

The real document is RAISE (Responsible AI in evidence SynthEsis), plus the November 2025 joint
position statement across Cochrane, Campbell, JBI and Environmental Evidence. RAISE requires
disclosure of tool and version, description of the human-AI workflow, and reporting of
validation data — not inter-run agreement. Substituting it would change the claim, so the line
is left standing for the author to decide; it must not survive to submission either way.
Not fixed here because the substitute has not been read in full, per the read-before-citing rule.

Everything else verified clean, including all five Research Synthesis Methods citations.

## 29 — 2026-08-19 · Entries 26 and 28 reopened: both reported work as done that was not
A 22-specialist panel audit found that this log is not trustworthy about its own closures.

Entry 26 declared the fabricated "RSM guidance §4.3" corrected. It corrected `main.tex:917`
and left `supplementary.tex:999`, which carried the identical sentence. Entry 28 closed with
"Everything else verified clean, including all five Research Synthesis Methods citations."
That was false: `khraisha2024gpt4` reads 15(5):707–722; the article is at **15(4):616–626**,
doi:10.1002/jrsm.1715. What was verified was that the journal field said Research Synthesis
Methods, not that the locators resolved. Stating the stronger claim was the error.

The shared cause is scope. Both sweeps ran over `article/` and never over `docs/`, where the
cover letter carries the same class of defect in worse form — see entry 30.

Fixed here: `supplementary.tex:999` rewritten to what the guidance actually says, matching
`main.tex:917`; `khraisha2024gpt4` given its real locators, full title and DOI. Author list
left as `and others` deliberately — the co-authors were not verified, and filling them from
memory is the exact defect under audit. Both documents recompile clean (main 33pp, supp 23pp,
zero undefined references). "§4.3" now appears nowhere in either .tex.

Still open and now confirmed in three places rather than one: `cochrane2024_ai_guidance`,
whose URL 404s, cited at `main.tex:85` and sold as argument 2 in `cover_letter_rsm.md:24`.
Entry 28 already ruled it must not survive submission. It survives. Left standing only
because deletion changes a claim the author should approve, not because it is defensible.

## 30 — 2026-08-19 · The three P0 blockers from the panel audit, resolved
### P0-1 · The desconfound arms did not send the same payload
`run_llama_cloud_desconfound.py:146` passes the uninterpolated template, `{title}` and
`{abstract}` literal, as the prompt and the article as a separate message part.
`src/screening/runner.py:194-195` interpolates before the call and the Ollama layer then
appends the article again. Re-measured here over the deposited call records: mean input
tokens 1,279.3 local vs 842.3 cloud (−34.2%), and **0 of the 500 canonical call hashes are
shared**. Output ceilings also differed, 2,048 local vs 512 cloud.

Corrected by scoping the claim, not by deleting the finding. `main.tex` no longer says
"configuration identical to the local Ollama deployment"; it now enumerates what was held
constant (weights, prompt source, temperature, seed) and what was not (payload rendering,
token ceiling), and states that the condition varies the serving stack *including its
request-rendering layer* rather than isolating infrastructure from payload construction.
The abstract and the table caption were brought in line.

One measurement removes a competing explanation rather than adding one: **all 4,266 completed
cloud calls returned `finish_reason = stop`**, so nothing hit the 512-token ceiling and
truncation cannot account for the 167/0 asymmetry. The causal story for *why* the arms
diverge is deliberately absent from the manuscript — it would be E3, and the E0 facts carry
the scoped claim without it.

### P0-2 · The fabricated Cochrane requirement, removed from all four locations
The sentence at `main.tex:85` credited a nonexistent document (url 404) with requiring
inter-run agreement statistics and then claimed the paper supplies them. Deleted, together
with the `.bib` entry and argument 2 of the cover letter; `supplementary.tex:999` was cleared
in entry 29. Not replaced by RAISE or the November 2025 joint statement: neither was read in
full, and neither asks for inter-run agreement, so the clause "which this paper supplies"
would not survive the substitution. The paragraph loses nothing that it could support.

### P0-3 · The cover letter, corrected against Crossref
`10.1017/rsm.2025.10018` resolves to Nussbaumer-Streit et al., *Knowledge user involvement is
still uncommon in published rapid reviews*, RSM 16(6):876–899 — a different article. The
editorial is Farotimi, Dunn, Van Lissa, Polanin, Mavridis & Pigott, 10.1017/rsm.2025.10058.
"Weber et al." names nobody on it. The salutation read "Therese Pigott"; she is **Terri D.
Pigott**, and she and Mavridis are both authors of the editorial and the recipients of the
letter. Suggested reviewers: Yutaka → **Takehiko** Oami (Chiba, not Tsukuba); Linnea →
**Mathias K.** Jensen; Berkant → **Berk** Atil; Gartlehner's paper is Research Synthesis
Methods 15(4):576–589, not JCE — the letter told RSM that a paper from its own volume 15 had
appeared elsewhere.

Both documents recompile clean (main 33pp, supp 23pp, zero undefined). 151 tests pass.
`check_pending.sh` still reports BLOCKED, correctly: three `\pending` markers awaiting
labeler2 and the submission tag, and three reviewer emails only the author can supply.
Those are open work, not defects.

## 31 — 2026-08-19 · Cluster 2A: the numbers that did not come out of the artefacts
Every figure below was re-measured here against the deposited artefacts, not taken from the
panel's report.

| Claim | Was | Is | Source |
|---|---|---|---|
| calls | 35,996 / 99.99% | **35,638 / 98.99%** | `timing_and_costs.json` grand_totals |
| "each achieved 500/500" | 4 stacks | Claude and GPT-4.1 only; Mistral 4,970, Gemma 4,930 | same |
| Mistral include rate | ~98% | **94.0%** (4,660 of 4,960 parsed) | recount of 5,000 calls |
| accuracy denominator | 500 | **192–200** per stack | `run_analysis.py:121-130` drops the 300 ambiguous |
| meta-analytic k | 100 | **39–63** | `random_effects_per_run.json` |
| pooled RR range | 1.015–1.038 | 1.012–1.038 | same |
| cost ratio | 267× per hour | 266× total, ≈1,400× per hour | $69.40/33h vs $0.26/174h |
| local–cloud gap | 19× | **20×** | 1.000 / 0.050 |
| non-identical outputs | 85–95% | 80–95% | Gemini EMR is exactly 0.200 |

Two of these are not arithmetic slips. `main.tex:298` promised the ambiguous stratum would be
"reported separately in all accuracy computations"; no such stratification exists anywhere in
the supplement, and the stratum is silently dropped from the denominator instead. The text now
says what the code does. And the varying k is not noise to be corrected away: k moves with the
run because extraction non-determinism decides whether an article yields a usable estimate,
which makes it a result rather than a defect, now stated as one.

**Heterogeneity, previously absent, is now reported**: I² 90.97–94.71%, τ² 1.4e-5 to 2.9e-4
across the 60 combinations. The values were already in the JSON. Submitting a random-effects
meta-analysis to a journal of meta-analysis methodologists without them was the most
predictable reviewer objection in the whole audit.

**The "upper bounds" claim is withdrawn.** The manuscript argued that enrichment with 60%
ambiguous abstracts made its flip rates conservative for ordinary reviews. Measured, 260 of
those 300 abstracts carry inclusion_score 5 — the same score as every clear-include — and all
300 carry zero exclusion reasons. The stratum marks where the automated rule lacked confidence,
not where a human would hesitate. No directional claim replaces it; the honest position is that
transfer to other corpora is untested.

## 32 — 2026-08-19 · Fleiss intervals were computed under the null
`compute_fleiss_kappa.py` used Fleiss (1971) eq. 13, whose expression contains no term for the
observed agreement: it is the asymptotic variance under H₀ κ=0, correct for testing that null
and wrong for an interval around an estimated κ. Two symptoms were already printed in the
supplement: **18 of 24 intervals had upper limits above 1.000** (Mistral screening reached
1.104), and three stacks with κ exactly 1.000 carried different standard errors.

Replaced with a percentile bootstrap resampling items (10,000 resamples, seed 42). Zero
intervals now exceed 1.000. The point estimates are unchanged; the intervals widen honestly,
Claude's whole-output κ going from [0.178, 0.181] to [0.133, 0.226]. Cells where every resample
returns 1.000 are flagged degenerate, with the rule-of-three bound named as the informative
quantity — consistent with how the main text already handles EMR = 1.000.

The chance correction is also declared inert for the whole-output hash column: 667 categories
over 100 items for Claude gives p_e ≈ 0.003, so κ collapses onto the pairwise concordance
already tabulated. The column is kept for its ordering, the Landis–Koch bands are no longer
applied to it, and the Cochrane comparison is dropped there. Per-field κ, with single-digit
category counts, is unaffected and stands.

Also removed: "Per RSM P1.a/P1.b/P2.a audit" from the supplement. Internal workflow shorthand
that an editor would read as numbered reports the journal had already issued.

## 33 — 2026-08-20 · The Claude stack never received temperature=0
`src/models/claude_runner.py` attached the `temperature` field to the request body only when
the requested value exceeded zero: `if temperature > 0.0: payload["temperature"] = temperature`.
This study requests zero. The field was therefore never sent on any of the 6,000 Claude calls,
and those requests ran at the Anthropic Messages API default, which the documentation gives as
**1.0 — the maximum of that API's range**. Every other runner in `src/models/` transmits the
field unconditionally; the defect is specific to this one client.

The run cards recorded `config.temperature: 0.0` regardless, and the call hash was computed
over the recorded value rather than the transmitted payload. The provenance trail built to make
configuration auditable asserted, for 6,000 calls, a setting that was never on the wire.

Three claims were rescoped rather than deleted:

- **The headline gap no longer rests on Claude.** The abstract now computes it from GPT-4.1
  (0.150) and Gemini (0.200), both verified to have transmitted temperature=0, against local
  1.000 — a 5–7× gap rather than the 20× that came from Claude's 0.050. This is a genuine loss
  of magnitude and is stated as such. Claude is reported as a separate case.
- **Finding 6 was rebuilt on within-stack evidence.** It previously contrasted "seeded" cloud
  stacks against "unseeded" Claude and called the difference a seed effect. Those arms differ
  in provider, infrastructure, API layer and now temperature at once — the exact inference
  §3.3 forbids. Withdrawn. What replaces it is cleaner and needs no cross-provider contrast:
  Gemini and GPT-4.1 transmitted seed=42 and temperature=0 on all 6,000 of their calls and
  still returned extraction EMR of 0.200 and 0.150. A seed that exists, is accepted and is
  verifiably sent does not make an API-served extraction pipeline reproducible. The within-stack
  ablation that would isolate the seed was not run and is named as the next experiment.
- **The supplement's seed table** keeps its rows but loses its causal reading, and its caption
  now says what varies between them.

Not re-run. Re-running produces a different experiment, not a corrected one, and the deposited
artefacts would cease to be the artefacts the analysis was performed on. The client is fixed
for future use, with a comment stating that the deposited data predates the fix.

The defect is declared in the configuration table and given the first slot in the limitations
section, ahead of the scope choices, because it is not a scope choice. It is also an instance
of this paper's own thesis: one conditional in a client, invisible in the configuration table,
in the run card and in the hash, silently detached the executed configuration from the declared
one. The recommendation that provenance must record what was transmitted rather than what was
requested is now arrived at from our own failure.

Also fixed: `\emr` was used twice in `supplementary.tex`, where the macro is not defined — it
is declared in `main.tex` only. The supplement had been emitting a PDF with two undefined
control sequences. Replaced with `\textrm{EMR}`.

## 34 — 2026-08-20 · Two high-yield, low-cost corrections
Working by return per hour rather than down the list.

**The printed inclusion criteria were not the executed ones.** `main.tex:291` listed criterion 3
as "respiratory outcome (hospitalization, ED visits, **or mortality**)" and criterion 6 as
"peer-reviewed publication". The screening prompt that actually ran
(`configs/prompts/screening.txt`) says "respiratory hospitalization or emergency department
visit" and "Published in English", and the human labeling protocol says the same, adding
"Mortalidade-only = exclui". So the manuscript printed criteria that contradicted both the code
and the instrument the raters followed.

This one had a cost beyond tidiness. A reviewer comparing the printed criteria against the
labels would conclude the raters excluded studies the protocol admitted — reading a κ of 0.529
as rater error when the raters followed their protocol exactly. The corpus construction
confirms the executed reading: `pubmed_fetch_exclude.py` uses a mortality query to populate the
negative controls, so mortality-only abstracts are deliberate excludes. Text now matches the
prompt and the protocol verbatim, and says so.

**PABAK used the two-category formula on a three-class table.** `kappa_statistics.py` computed
`2*p_o - 1` unconditionally. That is the k=2 special case of Brennan-Prediger; for k categories
it is `(k*p_o - 1)/(k - 1)`. Corrected in both the overall and the per-stratum path:

| | Was | Is |
|---|---|---|
| overall, 3-class | 0.500 | **0.625** |
| clear-include stratum | 0.360 | **0.520** |
| ambiguous stratum | 0.320 | **0.490** |

The binary collapse (0.558) was already correct and is unchanged. Note the direction: the error
was **understating** PABAK, which made the "kappa paradox is not operating" argument at
`supp:276` look stronger than the data supported, since a PABAK sitting close to κ was the
evidence for it. With the correct value the three-class PABAK is 0.625 against κ=0.529, so that
sentence was rewritten to rest on the binary collapse, where the two genuinely do coincide, and
to name the chance-agreement term as the reason for the three-class gap. The refutation
survives; its support is now the comparison that actually carries it.

`verify_reported_numbers.py` still passes on all its claims after the recomputation.

Also corrected in passing: two uses of `\emr` in `supplementary.tex`, a macro defined only in
`main.tex`. The supplement had been emitting a PDF with undefined control sequences, and the
check I had been running grepped for the string "undefined" rather than for `^!` in the log,
so it reported clean. Both documents now build with zero errors and zero undefined references.

## 35 — 2026-08-20 · Six corrections cleared while Stage B waits on labeler2
None of these depend on the pending labels, so they were done in one pass.

**Fixed-slot compared 3 runs against a 10-run baseline (item 5).** EMR is monotonically
non-increasing in run count — each extra run is another chance for an item to differ — so the
comparison credited the fixed-slot prompt with an advantage it partly obtained by being
measured over fewer repetitions. New script `scripts/blindage/fixedslot_paired_baseline.py`
recomputes the baseline over all C(10,3)=120 three-run subsets:

| Stack | vs 10-run baseline | vs matched 3-run baseline |
|---|---|---|
| Claude | −40.0% | **−70.2%** |
| Gemini | −9.1% | **−47.9%** (sign of the reading flips) |
| GPT-4.1 | +196.3% | **+23.8%** |

This strengthens the section rather than weakening it. Fixed-slot prompting now *degrades*
reproducibility on two of three stacks and improves it modestly on one, so the refutation of
"fixed-slot will resolve cloud non-determinism" is sharper: constraining the output shape does
not merely fail to fix the problem, it usually makes it worse. The caption also carries the
real coverage (100/99/99 articles), against the "100 INCLUDE articles" it claimed before.

**Schema conformance is a second reliability axis, and it was unmeasured (items 33, 34).**
New script `scripts/blindage/schema_conformance.py`, new §4.9 and Table 8:

| Stack | Screening | Extraction |
|---|---|---|
| LLaMA / Mistral / Gemma (local) | 87.0 / 84.2 / 96.2% | **38.0 / 43.0 / 40.0%** |
| Claude / Gemini / GPT-4.1 | 100 / 99.7 / 100% | 70.4 / **2.6%** / 64.9% |

Two readings, opposite directions. The local stacks reach EMR=1.000 on extraction while
conforming in 38–43% of calls: they reproduce, perfectly, a set that is mostly records a review
team would repair by hand. Deterministic and usable are different claims and this paper
establishes only the first. On the other side, Gemini conforms on 2.6% of extraction calls —
951 failures being a null where the schema types a string — and the meta-analysis still
harvests 39–45 estimates per Gemini run from outputs its own validator rejects 97 times in 100.

Item 34 resolves into the same finding. The manuscript attributed the deterministic local
failures to "response length constraints"; they are not truncation. The returned text sits far
below the 2,048-token ceiling and the failures are enum-orthography violations
(`case-crossover` for `case_crossover`), two values where the schema allows one, and nulls in
typed fields. The corrected mechanism supports the structured-output argument better than the
one it replaces.

**Stuart-Maxwell was computed on a table summing to 101 (item 19).** `SquareTable` defaults to
`shift_zeros=True`, adding 0.5 to each empty cell. Both statistics are well defined without the
correction here, and the published figure should reproduce from the published table. With
`shift_zeros=False`: Stuart-Maxwell χ²(2)=**16.41**, p=**2.73e-4** (was 15.38, 4.57e-4), Bowker
χ²(3)=**17.76**, p=**4.93e-4**. The directional-disagreement conclusion gets stronger.

**A dimensionally incoherent inequality (item 21).** `supp:997` justified HKSJ with
`q* ≥ 1/Σw*`, comparing quantities of different dimensions — in a journal of meta-analysis
methodologists. HKSJ widens relative to DL when the variance-inflation factor `q* ≥ 1`.

**κ=0.529 now appears in the abstract (item 38).** The one formally pre-registered component,
whose target was missed, was absent from the abstract while an informal Git pre-commit was
mentioned. It now has its own labelled block, reporting the shortfall as measured and the gold
standard as asymmetrically valid. This converts the paper's most exposed number into its
clearest signal of integrity, and it is better for an editor to meet it in the abstract than to
discover it in §3.6.

**run_experiment.py no longer pushes over the deposited evidence (item 54).** `_auto_commit`
ran `git add data/raw_outputs/` + commit + push unconditionally on every run, and the README
instructs exactly that command. A replicator following our own documentation would commit their
outputs over the deposited artefacts and push them to the shared remote. Now opt-in via
`AIOX_AUTOCOMMIT=1`, and the push is gone entirely.

Both documents build clean (main 35pp, supplement 23pp, zero errors, zero undefined refs); 151
tests pass. `check_pending.sh` still blocks on the three `\pending` markers awaiting Stage B and
three reviewer emails — open work, not defects.

## 37 — 2026-08-22 · Positioning pass for EMS, and two self-contradictions it caught
An academic-marketing pass reframed the paper for the target journal. It also found four defects,
two of which were mine and of a kind I had already committed twice: correcting a claim in one place
and not sweeping for where it repeated.

| # | Defect | Status |
|---|---|---|
| D1 | Contribution 6 still asserted the seed "delivers a 6× smaller effect than the deployment paradigm" — the exact reading **withdrawn** in Finding 6 and in the supplement | fixed |
| D2 | Finding 5 in the Discussion still carried +196%, −40%, −7.6% — the unmatched numbers §4.9 explicitly rejects, in the same manuscript | fixed |
| D3 | `compute_call_hash` hashed the **requested** parameters; the paper's own central lesson is that provenance must record what was **transmitted** | implemented |
| D4 | "151 tests" — 132 test functions collecting 151 cases | made precise |

**D3 was the one worth stopping for.** The manuscript argues that a provenance record must be
computed over the request body as sent, because a conditional in a client can silently separate it
from the configuration requested — which is exactly what happened to us on 6,000 Claude calls. The
released harness did not implement that. A reviewer on the software track would have opened
`hasher.py` and found the paper's recommendation absent from the paper's own tool. `compute_call_hash`
now accepts the transmitted payload and gives it precedence; the requested-parameter path survives as
a labelled fallback. Three tests cover it, one of which reproduces the original failure directly:
a payload that omits `temperature` must not hash identically to one that sends it. Suite: 151 → 154.

**Limitations reframed under one standing rule:** a sceptical reviewer must still be able to state
exactly what was not done. Verified against the compiled PDF — "We did not execute it", "We did not
raise the target, drop a rater, or recompute the coefficient", "deterministic, not that they are
ready to use", and "have not validated the findings on an independent corpus" all survive verbatim.
The reframing changed the frame, not the picture: the single corpus is now presented as what makes
the stack comparison clean rather than as an apology, and the missing seed ablation as the immediate
next measurement that the harness runs as a configuration change. Two entries are new (the κ and the
local-stack conformance); both were already stated elsewhere in the paper and neither introduces a
number. Per SA-QG-012 they await the author's ratification.

**Journal anchoring:** the four EMS papers now appear in the Introduction, at Finding 5, in the
tool-developer paragraph, in the preamble to the recommendations, and in the Conclusion. Park et al.
carries the most weight: a negative result on structured tool interfaces from this journal's own
pages, converging with our fixed-slot result from a different environmental domain.

⚠️ **BLOCKED (R1):** none of the four EMS papers has been read in full text. Every sentence citing
them is written to stay at title level for that reason, and Park et al.'s characterisation in
particular must be checked against its conclusions before submission.

## 38 — 2026-08-22 · The four EMS papers read; two changed the argument, two are blocked
The R1 gate flagged in entry 37 is discharged for two of the four and stands for the other two.
`data/fichamentos/envsoft_prior_work.md` records all four with `read_depth`.

**Yoon et al. (2026), read in full via arXiv:2511.11821 — and it gave us a better anchor than the
one we had.** Its §3.8 states, verbatim: *"Temperature was fixed at 0 across all model inferences,
thereby eliminating sampling variability and facilitating consistent outputs across multiple
experimental runs"*, and immediately after: *"Each model-method permutation was executed once."*
The study does not measure run-to-run variability; it measures accuracy against a gold standard.
So a 2026 paper in the target journal states, openly, exactly the premise this paper tests, and
treats a single execution as sufficient because the decoding parameters are believed to make
repetition redundant.

The introduction now uses that, and uses it without disparaging the study. The choice is the
field's convention, not an error, and the fact that these authors documented it clearly is what
makes it testable. The text says so in terms: the question is not whether that study was well
conducted but whether the premise it shares with the field survives measurement. This is a far
stronger opening than the generic "work has begun mapping the shift" it replaces.

**Schlögl et al. (2026), read in full via EGUsphere 2025-5210.** Its barrier catalogue already
names our problem — *"non-deterministic model outputs from generative AI"* — and notes that LLM
adoption introduces reproducibility challenges of a new kind. It names and does not measure, and is
not designed to. It also supplies a vocabulary worth adopting: methodological vs results vs
inferential reproducibility. We now locate this paper explicitly in the first of the three, which
is more precise than the undifferentiated word we were using.

**Park et al. and Zhu et al. are BLOCKED and the manuscript was weakened accordingly.** Verified
2026-08-22: Unpaywall `closed` for both, Semantic Scholar not open access, Europe PMC has no record
of either DOI, ScienceDirect 403, no preprint found.

The Park claim was the costly one. The manuscript asserted that structured tool interfaces "were
found to deliver less than their design implies" and claimed convergence with our fixed-slot result
— an assertion about that paper's conclusion, derived from its title. The title reads "what
structured tool interfaces do and do not provide", which does not license a direction. **Removed.**
The convergence argument, which was the most rhetorically valuable of the four anchors, is gone
until someone reads the paper. The Zhu characterisation was softened the same way.

This is a net loss of one strong argument and a net gain of a stronger one, and the trade is
correct in both directions: the Yoon anchor is now evidenced, and the Park anchor was not.

Read the two blocked papers through the UTFPR institutional access before submission. If Park et
al. does converge, the claim deserves to return — with the quotation behind it.

## 39 — 2026-08-22 · All four EMS papers read in full; the Park inference had been wrong
The two paywalled papers were reached through the browser under the author's institutional access.
`data/fichamentos/envsoft_prior_work.md` now records `read_depth: full-text` for all four. The R1
gate from entries 37 and 38 is discharged.

**The Park inference had been wrong, and reading it is what showed how.** From the title —
"what structured tool interfaces do and do not provide" — the manuscript had claimed the study
found structured interfaces "deliver less than their design implies", and asserted convergence with
our fixed-slot result. Entry 38 removed that as unverifiable. Now verified, it was also inaccurate.

Hydro-MCP delivers a great deal: it shortened the LLM agent's calibration path from 62.0 to 21.9
model evaluations (p<0.001) with terminal performance unchanged, and produced reviewable
operational provenance. What it did not deliver is **validity**. An acceptable KGE did not
guarantee hydrological quality — they name the failure mode *zombie calibration* — and a held-out
corruption task found that "logs and range constraints alone cannot detect physically corrupted
model states": physically impossible SOL_K values of 5,000–15,000 mm h⁻¹ went unreported by both
the constrained agent and the scripted baseline.

That is a **better** convergence than the one we claimed, and it is the same boundary as ours seen
from the opposite side. They constrain the interface and find control without correctness; we
constrain the output shape and find no reproducibility gain, then find EMR = 1.000 sitting beside
38–43% schema conformance. Both results say the control layer is necessary and not sufficient, and
that the layer which would fix it is not the control layer. The Discussion now states this with
their numbers.

**Zhu et al.** proposes a two-part framework: assess the overall computational workflow, then
diagnose the individual processes where reproducibility fails. Full-text search confirms the paper
never mentions large language models, non-determinism or randomness anywhere in the body — the one
related term appears in a reference. So the diagnostic step presumes a process that behaves the
same way when re-executed, which is true of the service-based components it targets and false of an
LLM-mediated one. Our claim now rests on that verification rather than on the title, and the text
offers EMR and conformance as the per-process check such a framework would need.

**One thing worth stealing from Park et al.**, recorded in the fichamento: their sentence on the
corruption failure — "is not a failure of the MCP concept, it is a measurement of where that concept
currently sits in the design space, and a specification of the next layer required to advance it."
That is precisely the register the limitations section was reframed into, and it is precedent from
the target journal itself.

Net effect of reading all four: one anchor recovered and strengthened (Park), one grounded
(Zhu), one already strong (Yoon, whose stated premise this paper tests), one sharpened
(Schlögl, whose barrier catalogue names our problem without measuring it).

## 40 — 2026-08-22 · Body reduced to seven tables; cover letter rewritten for EMS
**Five tables moved to the supplement:** corpus composition, mechanism mapping, computational
resources, field-level EMR (the heatmap figure already carries it) and semantic equivalence. The
body keeps the seven that carry the argument: the prior-work comparison, the deployment-stack
configurations, screening and extraction reproducibility, fixed-slot, the same-weights desconfound
and schema conformance. Main went from 83 to 79 pages, supplement from 25 to 27.

Two mistakes on the way, both caught by checking rather than by assuming. The moved blocks were
appended after `\end{document}`, so they compiled into nothing and their labels never reached the
`.aux` — which is why the cross-references stayed unresolved through two full builds. And
`tab:meta`, which had gone to the supplement earlier with the meta-analysis section, still had a
same-document `\ref` in the body. Both fixed; zero `??` in the compiled PDF, zero undefined
references, 154 tests passing.

**Cover letter rewritten as `docs/cover_letter_envsoft.md`.** The RSM letter is kept, not deleted:
it remains the artefact for that submission route if the EMS one does not work out.

The new letter argues from the journal's own pages, which is what reading the four papers bought.
Yoon et al. is cited as the statement of the premise this paper tests — explicitly not as a
criticism, since it is the field's standard practice and their clear documentation of it is what
made the premise identifiable. Park et al. is cited as the same boundary reached from the opposite
side, with their numbers: 62.0 to 21.9 evaluations, control and provenance delivered, validity not.
Schlögl et al. is cited as having named the barrier we measure. Zhu et al. as the framework whose
per-process diagnostic an LLM step does not yet fit.

The letter also reports two things against ourselves before the editor can find them: the κ that
missed its target, and the client that did not transmit the configuration we declared. Both are in
the manuscript; putting them in the letter is a deliberate choice about which impression the editor
forms first.

Verified: no RSM residue, no superseded figure, and every number in the letter traced to the
manuscript.
