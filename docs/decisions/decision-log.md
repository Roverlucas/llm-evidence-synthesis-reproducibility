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
