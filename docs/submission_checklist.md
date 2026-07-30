# Submission checklist — RSM

Moved out of `cover_letter_rsm.md` on 2026-07-29: an internal checklist inside the
cover-letter file risks being sent to the editors along with the letter.

Status as of 2026-07-29.

## Blocked on the labelers

- [ ] Blinded recalibration round returned by both labelers (25 items each)
- [ ] Gold standard consolidated (`build_gold_standard.py`; refuses to write while any item is unresolved)
- [ ] Stage-B extraction set rebuilt from the human gold standard (`rebuild_extraction_set.py`)
- [ ] Stage-B extraction labels returned (~2 h per labeler)
- [ ] Per-field extraction agreement computed (`compute_extraction_agreement.py`)
- [ ] Every `\pending{}` marker resolved in `main.tex` / `supplementary.tex` (`scripts/check_pending.sh`)

## Blocked on Lucas — decisions

- [x] ~~Tie-breaker~~ — **settled 2026-07-29: stays with Y.d.S.T., as registered.** No deviation on roles to declare. Reasoning in decision-log entry 22.
- [ ] Fresh-sample validation of protocol v1.2 (n≈30–40): run it, or state in the limitations that the amendment is unvalidated. The recalibration round cannot serve this purpose.
- [ ] Authorship: 2 → 5. Needs Isabelle's surname, ORCIDs and affiliations for all three additions, CRediT roles, and the acknowledgment rewritten (co-authors cannot be thanked in Acknowledgments).

## Blocked on Lucas — actions outside the repo

- [ ] Pre-submission inquiry: `docs/pre-submission-inquiry-rsm.md` is still marked DRAFT. Confirm whether it was sent, or send it.
- [ ] Sub-registration update on OSF component `8z6fy` — item (d) of the registered contingency. Text prepared in `docs/osf_subregistration_update.md`.
- [ ] Fix the public description of project `vr934`: it currently shows the pre-registration abstract instead of the project overview, so a reviewer opening the project sees the whole study described as if it were only the labeling protocol.
- [ ] Zenodo deposit: reserve the DOI, insert it into the Data Availability statement, then publish.
- [ ] Push the local commits (@devops) and tag the submitted version.
- [ ] Confirm suggested-reviewer emails for Oami, Jensen, Atil.
- [ ] Yara's sign-off on the final manuscript and cover letter.

## Optional — raises defensibility

- [ ] Forest plots from `random_effects_per_run.json` and `small_literature_sim.json` (highest-value figure work for an RSM readership)
- [ ] Paired effect size for the 21 McNemar contrasts. Note: **not** Cohen's h, which assumes independent proportions and would reintroduce the pairing error that McNemar was adopted to fix — use the discordant-cell odds ratio or paired risk difference.
- [ ] BCa bootstrap for EMR intervals (already computed for the human κ; the three interval methods agree to ~0.002 there, so the gain is small)
- [ ] Reporting checklists: code/software and ML reporting

## Done 2026-07-29

- [x] Stage-A dual labeling complete, κ = 0.529 (95% CI 0.383–0.674) reported as measured
- [x] Extended agreement statistics (CI, PABAK, prevalence/bias indices, McNemar, Stuart-Maxwell, per-stratum)
- [x] Protocol v1.2 amendment (criterion 5 levels; structural vs conditional criteria)
- [x] `YYYYY` placeholders replaced with the real registration DOI `FGN3E`
- [x] Pre-registration disclosure corrected — the manuscript was understating what exists
- [x] main/supplementary contradiction over gold-standard construction resolved
- [x] "rule precision = 100%" qualified with a rule-of-three bound
- [x] κ≥0.80 benchmark comparisons rewritten (construct mismatch: self-consistency ≠ inter-rater agreement)
- [x] Asymmetric validity of the gold standard documented; sensitivity now read as a lower bound
- [x] Cover-letter overclaim removed ("pre-registered post-revision analyses")
