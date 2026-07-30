# Sub-registration update — for OSF component `8z6fy`

**What this is.** Item (d) of the contingency registered in `fgn3e`
(DOI `10.17605/OSF.IO/FGN3E`, frozen 2026-05-12):

> "If overall Cohen's kappa < 0.80 in Stage A, we will not abandon the analysis but
> will (a) report the result transparently, (b) examine disagreement patterns
> qualitatively, (c) update the labeling_protocol.md to address the ambiguity, and
> (d) document the deviation in a sub-registration update."

That condition was met on 2026-07-29. **How to post it:** open component `8z6fy` on
OSF, add this as a wiki page or an uploaded file named
`sub-registration-update-2026-07-29.md`. Do not attempt to edit `fgn3e` — a
registration is immutable by design, and that immutability is what makes it worth
citing.

Text below is ready to paste.

---

## Sub-registration update — 29 July 2026

### 1. Outcome against the pre-specified target

Stage A dual-independent screening is complete. Both raters labeled all 100
abstracts of the stratified subset.

| Quantity | Value | 95% CI |
|---|---|---|
| Cohen's κ, 3-class | 0.529 (SE 0.074) | [0.383, 0.674] |
| Cohen's κ, binary (n=95) | 0.556 | [0.400, 0.712] |
| Raw agreement | 75.0% | — |
| Discordances | 25 / 100 | — |

**Both pre-specified gates were missed**: the κ ≥ 0.80 target (Cochrane Handbook
§4.6.6) and the expectation of a discordance rate below 15%. We report both as
measured. Per item (a) of the contingency, no target was revised after the fact.

The shortfall against the target is itself decisive (z = −3.65, p = 1.3×10⁻⁴). With
n = 100 the interval spans "fair" through "substantial", so we report the value
relative to the threshold and do not assign it a descriptive band.

Two alternative explanations were tested and rejected. The prevalence index is 0.189
and PABAK (0.558 binary) is nearly identical to κ, so the coefficient is not
depressed by skewed marginals — the "kappa paradox" is not operating. Weighted κ
(linear 0.541, quadratic 0.548, on the ordinal include–uncertain–exclude ordering)
shifts the estimate by less than 0.02, so the result is not an artefact of the
three-class scale.

### 2. Qualitative examination of the disagreement (item b)

The disagreement is directional rather than diffuse. Binary discordant cells are 2
versus 19 (exact McNemar p = 2.2×10⁻⁴); marginal homogeneity is rejected on the
3-class table (Stuart–Maxwell χ²(2) = 15.4, p = 4.6×10⁻⁴); bias index 0.179. Rater 2
returned 49 INCLUDE decisions against rater 1's 30.

Of the 25 discordances, 19 run in that same direction, and **17 of those 19 turn on
inclusion criterion 5** (quantitative effect estimate). The registered protocol v1.1
stated the criterion as "reports RR, OR, HR (or equivalent) with 95% CI" in its
inclusion list, while its exclusion list read "no quantitative effect estimate
extractable from the abstract". The first wording admits a stated intention to report
an effect; the second demands the values themselves. Both raters applied a defensible
reading; they applied different ones.

Compounding this, the v1.1 decision table specified outcomes for failure in two or
more criteria and for a borderline single criterion, but **not for clear failure in
exactly one criterion** — the configuration of those 17 abstracts.

Neither rater deviated from the registered protocol. The protocol was underspecified.

### 3. Protocol amendment (item c)

`labeling_protocol.md` is amended to v1.2:

- **Criterion 5 is split into levels.** 5a: numeric point estimate *and* numeric 95%
  interval present → satisfied. 5b: the effect is said to have been estimated but the
  values are absent → **uncertain**, not exclude, because abstract-only screening
  cannot verify what the abstract omits. 5c: no estimate and no mention → counts as
  failure.
- **Criteria are weighted by kind.** Structural criteria (original study, PM2.5
  exposure, respiratory hospitalization, English) exclude on a single clear failure.
  Conditional criteria (design, effect reporting) yield *uncertain* on a single
  failure. Precedence: exclude > uncertain > include.

The amendment was written **after** the κ was known. That sequence is disclosed in
the amendment itself, in the manuscript, and here. It follows item (c) of the
registered contingency rather than departing from it.

### 4. Recalibration round, and what it cannot establish

A blinded round restricted to the 25 discordant items is underway. Each rater
re-rates only those items, without seeing the other's decisions or their own earlier
ones. The 75 concordant items are not reopened.

**This round does not produce a second estimate of κ, and we will not report one.**
Because re-measurement is conditioned on prior disagreement, a coefficient recomputed
over the full corpus afterwards rises mechanically: at a sufficiently high resolution
rate it would cross the Cochrane threshold by construction, carrying no evidential
content. The outcome is reported as **post-hoc reconciliation agreement, conditional
on the initially discordant items**. κ = 0.529 stands as the study's agreement
estimate.

Establishing that the v1.2 amendment repairs the ambiguity would require a **fresh
independent sample** (n ≈ 30–40 suffices for a directional check), not a re-rating of
the same items. We register that as the appropriate next step and do not claim it as
a result.

### 5. Deviation from the registration: tie-breaker

The registration states: "unresolved items are decided by the senior author (Y.d.S.T.)
as tie-breaker." **This role has been reassigned to the first author (L.R.)**, and we
disclose it as a deviation.

Because the first author's models are the object of evaluation against this gold
standard, the deviation carries a conflict that the original assignment avoided. The
mitigations are: tie-breaks apply only to items still discordant after consensus;
they are adjudicated against the written criteria with no access to any model output;
and each is logged with the criterion invoked, so every adjudicated item can be
audited individually. The resulting gold standard records, per abstract, whether its
label came from first-round agreement, post-recalibration agreement, consensus, or
tie-break.

### 6. Substitution of the Stage-B extraction subset

The registration deposited `extraction_25_labeler{1,2}.csv`, a 25-item extraction
subset. That subset was drawn from the LLM **silver-internal** standard, before any
human label existed. Checked against the human consensus, **only 13 of the 25 survive**;
15 items the humans include were absent from it.

Scoring the models against a reference derived from model output would be circular, so
Stage B is rebuilt from the human gold standard. The 13/25 overlap is retained and
reported as a finding in its own right: direct evidence that LLM-based screening
admits material that human raters reject.

### 7. Additional analyses not in the registration

Reported as post-hoc, since the registration specified only the κ point estimates:
analytic and bootstrap intervals for κ (percentile and BCa), PABAK, prevalence and
bias indices, exact McNemar and Stuart–Maxwell tests of marginal homogeneity, and
stratum-specific agreement.

The stratified analysis produced a finding that qualifies the study's accuracy
figures, so we record it here rather than only in the manuscript:

| Stratum | n | Raw agreement | Cohen's κ | PABAK |
|---|---|---|---|---|
| clear-exclude | 25 | 1.000 | undefined (expected agreement = 1) | 1.000 |
| clear-include | 25 | 0.680 | 0.359 | 0.360 |
| ambiguous | 50 | 0.660 | 0.398 | 0.320 |

The gold standard is **asymmetrically valid**. Both raters endorsed exclusion for all
25 abstracts the automated rule called clearly excludable. Of the 25 it called clearly
includable, rater 1 endorsed inclusion for 13 and rater 2 for 21, and 8 of the 25
discordances fall inside that stratum. Reported specificity therefore rests on labels
the raters confirm; reported sensitivity rests on include-side labels they
substantially contest and is read as a lower bound. Relatedly, the automated rule's
"no errors on the held-out validation set" is now stated with a rule-of-three bound
(≈6% at 95% confidence) instead of as 100% precision.

### 8. Raters

Stage A was labeled by Isabelle (rater 1, returned 2026-07-29) and Luiza Iltchechen
(rater 2, returned 2026-07-15). Each was blinded to the other throughout. Their credit
in the manuscript — co-authorship or acknowledgment — is being settled and will be
stated in the submitted version.

### 9. Materials

All artefacts are in the project repository under `data/dual_labeling/`: both returned
label sets with their raw sources and SHA-256 hashes, the agreement statistics, the 25
discordances, the v1.2 protocol, the blinded recalibration sheets, and the analysis
scripts.
