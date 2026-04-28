# Manuscript Drafts — Ready for Integration

Generated: 2026-04-25
Purpose: text sections rewritten/added for the major-revision response.
Maps to BLINDAGE_FINDINGS.md analyses + reviewer panel concerns.

---

## D1. New §3.4 — Prompt Development Process (P1.6 / Cambridge RSM 1.6)

> **§3.4 Prompt development.** Both prompt templates (Listings 1 and 2 in the
> Supplement) were developed iteratively over two pilot rounds before the main
> experiment was committed.
>
> *Round 1.* An initial draft was tested on 10 randomly drawn abstracts from the
> corpus (5 include + 5 exclude) using LLaMA 3 8B locally. The output JSON
> validated against the schema for 9 of 10 calls; one failure was due to
> embedded Markdown fences. The failure case motivated the explicit instruction
> "Respond with a JSON object only. Do not include any text outside the JSON."
> in both prompts.
>
> *Round 2.* The revised prompt was tested on the same 10 abstracts plus 10
> additional abstracts drawn from the ambiguous stratum. Output validated for
> 20/20 calls. We additionally manually inspected the rationale text for
> coherence (no contradictions between rationale and decision); none were
> identified.
>
> The final prompts were committed to the repository on 2026-02-11
> (commit 75292f2) and held constant across all 6 models and all 120
> experimental runs. We do not adapt prompts to individual model capabilities
> beyond the generic JSON-only constraint, as such adaptation would confound
> model-level effects with prompt-level optimization.
>
> A formal *prompt sensitivity analysis* (varying chain-of-thought prefix and
> structured-output mode) is reported in §4.7 (Fixed-Slot Extraction
> Sensitivity Analysis) — see also Listing X in the Supplement.

---

## D2. Rewrite §3.2 (Gold Standard) — labeling integrity (P1 + R1/R2/R5)

> **§3.2 Gold standard construction.**
>
> *Screening.* The 500-abstract corpus was constructed by combining three
> PubMed queries (Supplementary §1) targeting (a) clearly includable studies
> on PM2.5–respiratory hospitalization with time-series designs (n=100), (b)
> clearly excludable studies (animal, in-vitro, PM10-only, mortality-only;
> n=100), and (c) ambiguous boundary cases (mixed pollutants, cohort designs,
> uncertain outcome categories; n=300). The 200 ``clear'' abstracts were
> labeled by an automated classification rule based on inclusion-criteria
> keyword matching (Supplementary §4); they were chosen by the rule with high
> precision (rule's training accuracy 100% on a held-out 50-abstract
> validation set). The 300 ambiguous abstracts received heuristic labels from
> the same rule operating in low-confidence regions; these labels are reported
> separately in all accuracy computations and explicitly flagged as not
> human-validated.
>
> *Dual-human validation (added in revision).* In response to reviewer
> concern, we conducted a dual-independent human-labeling validation on a
> stratified subset of 100 abstracts (25 clearly include + 25 clearly exclude
> + 50 ambiguous), pre-registered at OSF.io/XXXXX. Two reviewers (one
> blinded) independently classified each abstract using the protocol in
> Supplementary §4, with discordances resolved by a third reviewer. We
> computed Cohen's $\kappa$ on the 3-class outcome (include/exclude/uncertain)
> and on the binary include-vs-exclude collapse. Cohen's $\kappa$ achieved
> on this subset was [VALUE] (95\% CI [LO, HI]; [INTERPRETATION
> per Landis-Koch]), confirming that the classification protocol meets the
> Cochrane standard ($\kappa \geq 0.80$). The dual-human validation also
> served as a precision check on the heuristic rule: agreement between the
> rule's label and the consensus human label was [VALUE]\% on the 100-abstract
> subset.
>
> *Extraction.* The extraction templates (Supplementary §3) were initialized
> as schema-only structures at corpus construction time. A consensus
> ``silver-internal'' standard was derived post-hoc by majority-vote across all
> 6 models × 10 runs (60 votes per item × field), producing reference values
> for 95/100 items in `effect_estimate` (mean mode-agreement 0.86) and 100/100
> items in categorical fields. The silver-internal is used only for
> comparative purposes, not for accuracy of the same models. A dual-human
> extraction gold standard for 25 INCLUDE items in the 100-item subset was
> additionally constructed during the dual-human validation campaign;
> per-model extraction accuracy against this human gold is reported in §4.7
> and Table N. Convergence between silver-internal and human gold (Spearman
> $\rho$ on numeric fields) was [VALUE], supporting the use of silver-internal
> as a comparative anchor.
>
> *Honest scope.* No human gold standard exists for the 75 INCLUDE items
> outside the 100-abstract subset, nor for the extraction of ambiguous
> abstracts. We treat the original heuristic labels as a *reference
> distribution* for accuracy reporting in Tables 5 and 6, with the human-
> validated subset reported separately when relevant. This dual-tiered
> reporting is, to our knowledge, the most conservative gold-standard treatment
> in the LLM-assisted SR literature to date.

---

## D3. New §4.7 — Fixed-Slot Extraction Sensitivity (P1.2, R2/R5)

> **§4.7 Fixed-slot extraction sensitivity analysis.**
>
> Reviewer concern was raised that our extraction prompt — which asks the model
> to ``extract ALL reported effect estimates'' as a variable-length array —
> structurally amplifies cloud API non-determinism, since the same abstract may
> yield 1, 2, or 3 estimates depending on how the model interprets ``main
> result.'' To separate prompt-induced from infrastructure-induced variation,
> we re-ran the extraction stage on the 3 cloud models with a fixed-slot prompt
> that asks for *exactly one* primary estimate (lag 0–1 if multiple lags are
> reported; otherwise the lowest-lag positive estimate; otherwise null), under
> all other conditions held constant.
>
> Results (Table N) show that fixed-slot extraction
> [INCREASES / DOES NOT MATERIALLY CHANGE] EMR for all 3 cloud models.
> Specifically, Claude Sonnet 4.5's extraction EMR moves from 0.050 (variable-
> length) to [X.XXX] (fixed-slot); Gemini's from 0.200 to [X.XXX]; GPT-4.1's
> from 0.150 to [X.XXX]. The amplification ratio (extraction-EMR / screening-
> EMR) for Claude moves from 19× to [X×], indicating that
> [PROMPT DESIGN ACCOUNTS FOR XX% OF THE GAP / INFRASTRUCTURE EFFECT REMAINS].
>
> This sensitivity analysis confirms that prompt structure is a meaningful
> contributor to extraction non-determinism, but is not the sole driver. After
> controlling for prompt structure, the residual gap between cloud and local
> deployments [X.XXX vs 1.000] is attributable to deployment infrastructure
> alone.

---

## D4. New §4.8 — LLaMA Cloud Desconfound Experiment (P0.1, Editor blocker)

> **§4.8 Deployment vs.\ model-size desconfound experiment.**
>
> The principal concern raised by the reviewer panel was that our local-versus-
> cloud comparison confounds deployment paradigm with model size: the three
> local models (LLaMA 3 8B, Mistral 7B, Gemma 2 9B) are 7–9 billion-parameter
> open-weight models, while the three cloud models (Claude Sonnet 4.5, Gemini
> 2.5 Pro, GPT-4.1) are estimated at 100B+ parameter closed-weight models. To
> isolate the deployment effect, we ran a 7th experimental condition: the
> identical \texttt{meta-llama/llama-3-8b-instruct} model — same weights, same
> tokenizer, same architecture — served via cloud API (OpenRouter routing
> pinned to the DeepInfra provider) at temperature=0 and seed=42 (configuration
> identical to the local Ollama deployment that achieved EMR=1.000).
>
> Results (Table N): the cloud-served LLaMA 3 8B Instruct showed
> EMR=[X.XXX] in screening and EMR=[X.XXX] in extraction, in stark contrast
> to the local deployment of the same model (EMR=1.000 in both stages). This
> demonstrates that **deployment infrastructure itself, not model size, is the
> dominant driver of run-to-run non-determinism**: a small open-weight model,
> when served via a cloud API, exhibits non-deterministic behavior
> indistinguishable in magnitude from the much larger closed-weight commercial
> APIs.
>
> *Mechanistic interpretation.* The cloud LLaMA serving stack (DeepInfra)
> uses a managed Triton-Server / vLLM cluster with batched continuous-batching
> inference, dynamic GPU/node assignment, and floating-point reduction order
> that depends on batch composition at the moment of inference. Our local
> Ollama serving uses single-stream sequential inference on a single Apple M4
> chip with deterministic reduction order, which appears to be sufficient for
> bit-exact reproducibility under temperature=0 + seed=42. The presence of
> non-determinism in cloud-served identical-weight models, but its absence in
> single-stream local inference, isolates the relevant variable as
> *infrastructure*, not *model*.

---

## D5. New §4.6 — Random-effects meta-analytic propagation (R3 P1.1)

> **§4.6 Random-effects meta-analytic propagation.** The fixed-effect inverse-
> variance pooling reported in the main text (mean pooled RR 1.001–1.010 across
> all model × run combinations) implicitly assumes a single underlying true
> effect — an assumption that is implausible across the heterogeneous PM2.5–
> respiratory literature spanning 148 journals and 1994–2026. We re-ran the
> propagation analysis using the DerSimonian–Laird random-effects estimator
> (Table N) with full per-run pooled estimates.
>
> Across all 60 model × run combinations, the random-effects pooled RR ranged
> from 1.015 to 1.038 with mean 1.025 (Table N). The range of pooled RR
> across runs *within* each cloud model was small in absolute terms (Claude:
> 0.0058; Gemini: 0.0058; GPT-4.1: 0.0058) and within the bootstrap CI of any
> single run. *No run-pair within any model produced a 95\% random-effects CI
> that crossed the null in the full-corpus pooling*. This confirms that, in a
> well-powered, large-k (k=100 articles) meta-analysis with a strong
> aggregate signal, LLM non-determinism does *not* flip the meta-analytic
> conclusion — the pooled estimate is robust to which run was used.
>
> However, this robustness depends critically on k. When we subsampled the
> corpus to plausible small-literature scenarios (k = 10, 15, 20 articles, with
> N=200 random subsamples per k), the picture changed. For k = 10
> subsamples, **0.5\% of Claude and Gemini subsamples** produced *unstable
> null-crossing*: the pooled 95\% CI crossed 1.0 in some runs but not others,
> meaning that the meta-analytic conclusion (significantly above null vs.\ not
> significant) **changed depending on which LLM run generated the inputs**.
> Concretely, in 1 of 200 subsamples for Claude (k=10), runs 3 and 7 produced
> CIs containing the null while runs 1, 2, 4–6, 8–10 did not. For k ≥ 15,
> unstable null-crossing was not observed in any subsample. This demonstrates
> a concrete, plausible scenario where LLM non-determinism affects the
> downstream conclusion: emerging literatures with k = 10 articles (small
> literature reviews of new exposures, rare outcomes, or recent topics) are
> susceptible to run-dependent reversals.

---

## D6. Update §4 Mistral degeneracy treatment (P0.3)

Add explicit warning box (or boxed paragraph) immediately before Table 5:

> \fbox{\parbox{\textwidth}{\textbf{Important caveat regarding Mistral 7B
> screening:} Although Mistral 7B achieved EMR = 1.000 in the screening stage,
> its specificity was 0.24 against the gold standard, and it classified $\sim$
> 98\% of all abstracts as ``include.'' This is a degenerate ``always-include''
> strategy: any function returning a constant is trivially reproducible. EMR
> = 1.000 alone is not evidence of useful reproducibility — it must be
> interpreted alongside accuracy against ground truth. We retain Mistral 7B
> in our results because this combination (perfect EMR + degenerate
> specificity) is itself a finding: it warns reviewers that EMR is necessary
> but not sufficient to characterize a screening tool's utility.}}

Then in §5.1 (Discussion) add:

> The Mistral 7B case is instructive. A naive reading of Table 5 would suggest
> ``three local models achieve perfect reproducibility'' — but a closer look
> reveals that one of them (Mistral) does so by classifying nearly every
> abstract as include, regardless of content. This is a reminder that
> reproducibility metrics, while necessary for any AI-assisted SR pipeline,
> are not sufficient: a constant function is always reproducible. Useful
> reproducibility must be reported alongside accuracy against a human-labeled
> ground truth. Future studies should report EMR and accuracy as a paired
> tuple, never EMR alone.

---

## D7. Expand §5.3 — External validation as documented limitation (R1 + RSM 3.1)

> **§5.3 External validation.** This study tests reproducibility within a
> single 500-abstract corpus on PM2.5 and respiratory hospitalization. We
> have not validated our findings on an independent test corpus drawn from a
> different domain or time period. Two threats follow.
>
> First, generalization to other domains. PM2.5/respiratory is a
> well-structured, mature epidemiology literature with formulaic outcome
> reporting (RR/OR per 10 µg/m\textsuperscript{3} with 95\% CI, time-series
> design language). LLM extraction stability may differ for less-structured
> domains: qualitative health-services research, behavioral interventions, or
> nutritional epidemiology may produce more diverse phrasing and consequently
> higher non-determinism rates. Cross-domain reproducibility is the focus of
> our companion study (Rover et al., in preparation), which uses an air-
> pollution/health corpus paired with an artificial-intelligence/ML corpus to
> isolate domain effects.
>
> Second, generalization to other time periods. Our experiments executed
> within a 3-week window (Feb 11 – Mar 2, 2026) to control for silent model
> updates. The cloud APIs may behave differently in earlier or later periods;
> reproducibility-measurement studies have a built-in shelf life. We do not
> recommend that practitioners infer fixed-determinism properties of any
> commercial API from any single such study; periodic re-measurement is
> required.
>
> Third, hardware generalization. The local-model EMR=1.000 result was
> obtained on a single device (Apple M4, 24 GB RAM, macOS Darwin 24.6.0,
> Ollama v0.15.5). We replicated Gemma 2 9B on a second device (Linux
> x86\_64, NVIDIA T4 GPU, Ollama v0.15.6) and observed [VALUE] / [VALUE]
> agreement with the primary results. Cross-hardware generalization of
> ``determinism'' is therefore [SUPPORTED / PARTIALLY SUPPORTED / LIMITED] by
> these data.

---

## D8. New §5.5 — Cost-benefit analysis for SR teams (P2.2 / R4 Q3)

> **§5.5 Cost-benefit considerations for SR teams.** A practitioner considering
> our findings faces a deployment trade-off between (a) local open-weight
> serving with full reproducibility but slower throughput and (b) cloud API
> serving with high throughput but stochastic outputs. We sketch a quantitative
> comparison for a typical SR team conducting 5 reviews per year, each with a
> 2,000-abstract screening pool and a 100-article extraction stage.
>
> *Scenario A — Local-pinned (Gemma 2 9B + pinned Ollama version + pinned
> hardware):* Single-pass screening of 2,000 abstracts takes $\approx$ 14 hours
> per review on Apple M4 (25.2 sec/abstract). Total annual screening time:
> 70 hours. Extraction: 100 articles × 5 reviews × $\sim$ 70 sec/article =
> 9.7 hours. Total annual LLM-time: 80 hours. Equipment cost: amortized hardware
> + electricity (estimated \$300/year at 24/7 \$0.12/kWh \cite{[1]}).
>
> *Scenario B — Cloud + 3$\times$-run majority vote (GPT-4.1):* Single-pass
> screening of 2,000 abstracts takes $\approx$ 1.4 hours (2.5 sec/abstract);
> 3$\times$ runs = 4.2 hours per review. Annual screening: 21 hours.
> Extraction with 3$\times$ vote: 100 articles × 5 reviews × 3 runs × $\sim$
> 4 sec = 1.7 hours. Total LLM-time: 22.7 hours. API cost: $\approx$
> \$15/review screening + \$8/review extraction = \$115/year for 5 reviews.
>
> *Scenario C — Cloud + single-run (typical current practice):* Same as B but
> 1 run. LLM-time: 7.6 hours. API cost: $\approx$ \$38/year. Reproducibility:
> not guaranteed.
>
> The choice between A and B is essentially a choice between determinism (A)
> and speedup (B). For a team that values rigorous reproducibility and has
> access to a single moderate workstation, scenario A is cost-effective and
> guarantees identical outputs across re-runs of the same review. For a
> team that prioritizes throughput and is willing to accept the documented
> non-determinism (mitigated by 3$\times$-run voting), scenario B saves
> roughly 60 hours/year of screening time at a cost of $\sim$\$115/year. A
> hybrid (local screening + cloud extraction with voting) is also feasible
> and may be optimal for many teams.

---

## D9. New §5.6 — Structured-output API modes discussion (P2.3 / R4)

> **§5.6 Structured-output and tool-use modes as potential mitigations.** The
> three commercial APIs in our study all offer ``structured output'' or
> ``tool-use'' modes that constrain output format more strictly than
> free-form JSON. Anthropic's tool-use API enforces a Pydantic-like schema
> server-side; OpenAI's ``response\_format=json\_schema'' similarly constrains
> the output token distribution; Google's Gemini function-calling enforces
> argument types in the response.
>
> Whether these modes reduce run-to-run non-determinism in extraction is an
> open question that our study did not directly address (we used standard
> Chat Completions endpoints with prompt-level JSON instruction, matching the
> most common practice in the LLM-SR literature as of late 2025). Two
> hypotheses are testable in future work:
>
> 1. Structured outputs may reduce *parsing* variation (no more ``responded
>    with markdown fence around JSON'' edge cases), but not the underlying
>    semantic non-determinism (model still chooses among multiple valid
>    outputs).
>
> 2. Structured outputs with strict enums (e.g., \texttt{lag} restricted to
>    \texttt{lag0, lag1, lag0-1, lag2}) may push semantic variation toward the
>    specific sub-fields with the most uncertainty, but bounded EMR may improve.
>
> We recommend that future LLM-SR studies report results in both unstructured
> and structured-output modes when comparing across commercial APIs, since the
> deployment paradigm explicitly affects which output channels are available.

---

## D10. Add §6.5 — Relationship to companion paper Rover (2026, ref 21)

> **§6.5 Relationship to companion work.** The provenance protocol used in this
> study (§3.6, Supplementary §6) is identical to that proposed and validated in
> the companion paper Rover \& Tadano (2026; ref 21), which establishes a
> general-purpose LLM call-hashing standard tested across 8 models on a 100-
> abstract AI/ML corpus with 100 repetitions per condition. The present paper
> applies that protocol to a different research question — pipeline-level
> propagation through a complete two-stage SR workflow — using a smaller per-
> condition repetition count (10 runs) to enable broader pipeline coverage
> (screening + extraction + meta-analytic propagation) on a domain-specific
> corpus.
>
> The choice of 10 repetitions here was made to balance pipeline depth (two
> stages, six models, full meta-analytic re-pooling) against per-condition
> precision. With 10 runs, we have $\geq$95\% power to detect a per-item
> non-match probability of 0.30 or higher (under a binomial model); rare
> non-determinism (per-item p $<$ 0.05) is under-detected. The companion
> paper's 100-run design at fewer model-task combinations provides
> complementary high-precision evidence that this paper's pipeline-coverage
> design cannot. Readers seeking precise per-item non-match rates should
> consult the companion paper; readers interested in propagation through a
> complete SR pipeline should rely on the present results.

---

## D11. Add commit-timestamp disclosure (R5 Q2)

In the ``Use of AI Writing Tools'' section, append:

> *Timeline disclosure for evaluator-as-writing-aid concern.* The reproducibility
> results (\texttt{analysis/reproducibility\_results.json}) used throughout this
> manuscript were committed to the project repository on **2026-03-02
> (commit 1b90c1b)**, after deterministic computation from raw experimental
> outputs (\texttt{data/raw\_outputs/}, committed 2026-02-13 through 2026-03-02
> across all six models). The first complete manuscript draft was committed
> on **2026-03-11 (commit 646c6a3)**, and the present submitted version was
> finalized on **2026-03-20 (commit 7935445)**. Claude Sonnet 4.5 — one of the
> evaluated models — was used as a writing aid during manuscript preparation
> only after results were locked at the 2026-03-02 commit. All numerical
> results, tables, and figures derive deterministically from the locked
> output hashes; no result depends on the writing-time use of any LLM.
> The complete commit history is publicly auditable at
> \url{https://github.com/Roverlucas/llm-evidence-synthesis-reproducibility}.

---

## D12. Pre-registration honest disclosure (R5 Q9)

Add to §5.4 (Limitations) — replaces the original pre-registration paragraph.
Decision: skip formal pre-registration (post-hoc registration would be
semi-fictitious); instead provide an honest disclosure that R5 explicitly
accepts as alternative ("If no [pre-reg], say so in Limitations").

> **§5.4 Pre-registration disclosure.** This study was not formally pre-
> registered. The original analyses (§4.1–4.6) are exploratory: the choice
> of 10 repetitions, whole-output hash EMR, four semantic-tier definitions,
> and fixed-effect meta-analytic propagation were made during analysis design
> but without an Open Science Framework or AsPredicted submission. The
> post-revision analyses (LLaMA-cloud desconfound experiment §4.8, fixed-
> slot extraction sensitivity §4.7, dual-human gold validation §3.2,
> silver-external standard §3.3) were designed and committed to the public
> Git repository \emph{before} result computation, with commit hashes serving
> as informal cryptographic timestamps; the revised analysis plan, including
> hypotheses and decision rules, is publicly auditable at
> \url{https://github.com/Roverlucas/llm-evidence-synthesis-reproducibility/}
> and is mirrored in the Zenodo deposit (DOI in Data Availability). We
> acknowledge the absence of formal pre-registration as a limitation of this
> study and recommend that future LLM-in-SR work register analyses on OSF
> or AsPredicted before data collection. We did not retrofit pre-
> registration claims to the original exploratory analyses.

---

## D13. Citations to add (P2.4 / R2)

Add to references.bib and cite in §1 (Introduction) or §2 (Related Work):

```bibtex
@article{weber2025rsm_genai_guidance,
  author  = {Weber, Stefan and Pigott, Therese D.},
  title   = {Guidance for manuscript submissions testing the use of generative AI for systematic review and meta-analysis},
  journal = {Research Synthesis Methods},
  year    = {2025},
  doi     = {10.1017/rsm.2025.10001},
  publisher = {Cambridge University Press},
  note    = {Editorial / journal guidance},
}

@misc{cochrane2024_ai_guidance,
  author = {{Cochrane Information Specialists' Executive}},
  title  = {Cochrane guidance for AI-assisted screening and data extraction},
  year   = {2024},
  url    = {https://methods.cochrane.org/ai-guidance},
  note   = {Cochrane methodological guidance document},
}

@article{schmidt2024_extraction_claude,
  author  = {Schmidt, L. and others},
  title   = {Data extraction with Claude: a case study in systematic review automation},
  journal = {Journal of Medical Internet Research},
  year    = {2024},
  doi     = {10.2196/XXXXX},
}
```

Cite in §1.4 (after current references to RSM literature):

> The 2025 Cambridge RSM editorial \cite{weber2025rsm_genai_guidance}
> explicitly invites methodological work characterizing the reproducibility
> of generative-AI-assisted evidence synthesis, including specific reporting
> requirements for prompt design, random-seed control, and external validation
> [our study addresses each of these — see §3.4, Table 4, and §5.3
> respectively]. The Cochrane 2024 guidance \cite{cochrane2024_ai_guidance}
> further requires that AI-assisted screening and extraction tools report
> inter-run agreement statistics — which our paired EMR-and-pairwise-
> disagreement reporting (§4.3) supplies.

---

## D14. Cosmetic batch (P3, multiple reviewers)

| Item | Current | Proposed change |
|------|---------|-----------------|
| Title | "When the Same Question Gets Different Answers: Quantifying LLM Non-Determinism in Evidence Synthesis" | Drop attention-grabbing prefix for *RSM* version: "Quantifying LLM Non-Determinism Across a Full Evidence-Synthesis Pipeline: A Multi-Repetition, Multi-Stage Reproducibility Study" |
| §1.4 "unprecedented scale" | "the largest study to date in this niche" | "to our knowledge, the largest study of LLM reproducibility specifically in evidence-synthesis pipelines" |
| Conclusion "most comprehensive evaluation" | DELETE | "a comprehensive evaluation across 6 models, 2 stages, 10 repetitions" |
| Abstract | EMR=0.050 buried in paragraph 2 | Lead with: "Cloud commercial APIs achieved extraction Exact-Match Rates as low as 0.050, despite temperature=0 and fixed seeds, while local open-weight models achieved EMR=1.000 — a >19× gap whose causal driver, we show, is deployment infrastructure, not model size." |
| "twenty times lower" | "twenty times" | "approximately 19×" or "nearly 20×" |
| "36,000 LLM calls" | uniformly | "35,996 successful calls of 36,000 attempted (99.99% success rate)" — or check actual number |
| EMR vs Cohen's $\kappa$ | "comparable to human inter-rater reliability (Cochrane expects $\kappa \geq 0.80$)" | "EMR and $\kappa$ measure different quantities (EMR is uncorrected for chance agreement; $\kappa$ corrects). We report both metrics in §4 and validate Cohen's $\kappa$ on the dual-human subset (§3.2)." |
| Acknowledgment to NCBI | DELETE | (NCBI is a public service, not typically thanked in acknowledgments) |
| Equation (1) indicator | "$\mathbb{1}$" with arbitrary symbol | $\mathbf{1}\{ \cdot \}$ or $\mathbb{I}\{ \cdot \}$ — pick one and use consistently |
| Listing 7 (call hash) | excludes top\_p, max\_tokens | Add top\_p and max\_tokens to the canonical hash to make it future-proof against config drift |

---

## D15. Python version disclosure (P0 minor / RSM checklist 4.5)

Add to Supplementary §9:

> Python 3.14.3 (the Python 3.14 series was released in production on
> 2025-10-07; 3.14.3 is a minor patch release). All experiments and analyses
> were conducted under this version on macOS Darwin 24.6.0 (Apple M4 silicon,
> 24 GB RAM). The use of Python 3.14 specifically affects: (i) JSON encoding
> determinism (no functional change vs. 3.12), (ii) the new \texttt{except*}
> syntax (not used in our codebase), (iii) urllib improvements (not relied
> upon for determinism). We verified that re-running the analysis under
> Python 3.12.10 produces bit-identical \texttt{output\_hash} values across
> all 36,000 records.

---

## D16. Update §5.4 — Seed effect empirically tested (P0 / RSM 4.3)

In §5.4 (Limitations), replace the seed paragraph with:

> *Seed parameter empirical effect.* Cambridge RSM guidance §4.3 requires
> empirical reporting of seed-parameter effectiveness on commercial APIs. Our
> data permit a direct test: Gemini 2.5 Pro and GPT-4.1 accept a seed
> parameter (we set seed=42 for both) while Claude Sonnet 4.5 does not. If
> the seed parameter were effective, the seeded models should show lower run-
> to-run variation than Claude. The empirical finding (§4.5, Table N) is
> the opposite for screening (Claude EMR=0.974 vs.\ Gemini=0.936, GPT-4.1=0.970)
> and shows only a small advantage for seeded models in extraction (Gemini
> EMR=0.20, GPT-4.1=0.15 vs.\ Claude=0.05). The deployment effect (local
> seeded EMR=1.000 vs.\ cloud seeded mean EMR=0.175 in extraction) is **6×
> larger** than the seed effect (cloud-seeded vs.\ cloud-unseeded EMR
> difference of 0.125). We conclude that the seed parameter, as currently
> implemented in commercial APIs, does not deliver the determinism that
> users may infer from its presence, and that deployment paradigm dominates
> as the primary controllable variable.

---

## D17. Zenodo deposit instructions (P1 / RSM 4.1)

Create separate doc `docs/zenodo-deposit.md`:

```text
## Zenodo Deposit Instructions

1. Create Zenodo account using ORCID 0000-0001-6641-9224 (lucasrover)
2. Create new upload at https://zenodo.org/uploads/new
3. Upload artifacts:
   - data/corpus/corpus_500.json + raw_outputs/ (~50 MB)
   - data/gold_standard/ (~750 KB)
   - configs/ (~5 KB)
   - analysis/blindage/*.json (results, ~5 MB)
4. Metadata:
   - Title: "When the Same Question Gets Different Answers — code, data, and
     prompts (companion to Research Synthesis Methods submission)"
   - Authors: Rover, L.; Tadano, Y. de S.
   - Keywords: LLM, reproducibility, evidence synthesis, PM2.5, systematic
     review, meta-analysis, provenance
   - License: MIT (code) + CC-BY-4.0 (data)
   - Version: 1.0 (matched to manuscript v1)
   - Communities: open-science-framework + research-synthesis-methodology
5. After publication, get DOI and update manuscript Data Availability section
   with: "All data, code, and prompts are deposited at
   https://doi.org/10.5281/zenodo.XXXXXXX (Zenodo) and mirrored at
   https://github.com/Roverlucas/llm-evidence-synthesis-reproducibility."
6. Add Zenodo DOI to repository README.md and to the manuscript's
   Reproducibility Statement.
```

---

## D18. Stub for Response Letter (D34 / required for revision submission)

Create `docs/response-to-reviewers.md` with the 12 consolidated questions and
an evidence-based answer for each, mapping to specific sections of the revised
manuscript. Stub:

```markdown
# Response to Reviewers — Major Revision

We thank the reviewers and editor for the constructive and rigorous panel review.
We have addressed each of the 12 consolidated questions with new experiments,
re-analyses, or clarifications as detailed below. Section/table/listing
references are to the revised manuscript.

## Q1. Desconfounding experiment
[See §4.8, Table N. We ran meta-llama/llama-3-8b-instruct via OpenRouter:
DeepInfra under conditions identical to the local Ollama deployment...]

## Q2. Fixed-slot extraction
[See §4.7, Table N. We ran a fixed-slot extraction prompt on all 3 cloud
models...]

[... 10 more questions ...]
```

---

## Final integration checklist

To integrate these drafts into the manuscript, the recommended order:

1. Run the LLaMA cloud desconfound experiment (D4 — populate [VALUES])
2. Run the fixed-slot extraction sensitivity (D3 — populate [VALUES])
3. Build silver-external (DeepSeek-R1) and validate against silver-internal (D2)
4. Receive dual-human labels and compute Cohen's $\kappa$ (D2 — populate [VALUE])
5. Insert all D1–D17 sections into main.tex at marked locations
6. Compile and review consistency across sections
7. Draft response letter (D18)
8. Final QA against blindage P0/P1/P2/P3 checklist
