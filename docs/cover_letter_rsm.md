# Cover Letter — Research Synthesis Methods Submission

**Status:** DRAFT v1 — 2026-05-20 (awaiting P1-A dual-labeling completion before final send)

**To:** Editors-in-Chief, *Research Synthesis Methods*
Dimitris Mavridis & Therese Pigott
**From:** Lucas Rover (Corresponding Author), Universidade Tecnológica Federal do Paraná
**Subject:** Submission: "Reproducibility of Pollution–Health Evidence Synthesis Using LLM-Assisted Screening and Extraction"

---

Dear Professors Mavridis and Pigott,

We are pleased to submit our original research article, **"Reproducibility of Pollution–Health Evidence Synthesis Using LLM-Assisted Screening and Extraction"**, for consideration in *Research Synthesis Methods*.

## What we did

We conducted what we believe is the most comprehensive empirical evaluation of LLM reproducibility in evidence synthesis published to date: **36,000 LLM calls across 120 experiment runs**, applying six *deployment stacks*---three local (LLaMA 3 8B, Mistral 7B, Gemma 2 9B served via Ollama on Apple M4) and three API-served (Claude Sonnet 4.5/Anthropic, Gemini 2.5 Pro/Google, GPT-4.1/OpenAI)---to a 500-abstract PubMed corpus on PM₂.₅ and respiratory hospitalizations, through both abstract screening and structured data extraction.

## Why this matters for RSM readers

1. **Direct response to your 2025 RSM editorial on GenAI-assisted evidence synthesis** (Weber et al., DOI: 10.1017/rsm.2025.10018). The editorial called for methodological work characterizing reproducibility of generative-AI-assisted SR, including specific reporting requirements for prompt design, random-seed control, and external validation. Every requirement is addressed empirically in this manuscript.

2. **Direct response to the Cochrane 2024 guidance** requiring inter-run agreement statistics for AI-assisted screening and extraction. We provide paired EMR and pairwise-disagreement reporting at the granularity Cochrane requires, plus chance-corrected Fleiss' κ across runs.

3. **Falsifies a widely-held assumption.** Studies routinely report 94–97 % LLM "reproducibility" using per-field metrics over 2–3 repetitions. Applying a stricter whole-output metric across 10 repetitions reveals only **5–20 % of cloud-API extraction outputs are truly identical**---a measurement gap of nearly 20×.

4. **Establishes the unit of reproducibility.** Our same-weights desconfound experiment (serving identical `meta-llama/llama-3-8b-instruct` weights locally via Ollama and via DeepInfra cloud) demonstrates that 39 % systematic disagreement between the two deployments is attributable to the **serving stack, not the model**. This reframes "which model" as the wrong abstraction for LLM-assisted SR documentation.

5. **Quantifies downstream impact.** A small-literature simulation under Hartung-Knapp-Sidik-Jonkman (Cochrane Handbook 6.5+ recommendation for k<10) shows up to **48.5 %** of k=10 subsamples experience run-dependent null-crossing reversals, depending on which LLM run generated the inputs.

## Methodological rigor we provide

- 10 repetitions per model × stage (vs. typical 2–3 in prior work)
- Pre-registered post-revision analyses (commits as cryptographic timestamps)
- Two independent silver standards: within-study majority vote + external DeepSeek-R1 (different family, different training corpus, different decoding paradigm)
- Dual independent human labeling on a stratified 100-abstract subset (in progress; Cochrane κ ≥ 0.80 target; results to be reported in the camera-ready version)
- SHA-256 provenance hashes on every input, output, and configuration
- Fleiss' κ multi-rater agreement across runs (in addition to EMR)
- McNemar's paired contrasts (replacing the original two-proportion z-test where outcomes are paired)
- HKSJ variance correction alongside DerSimonian-Laird
- Mechanism-mapping table (6 mechanisms × 5 deployment stacks) with documented/likely/possible/precluded classifications

## Open Science

- **OSF project**: registered, DOI [10.17605/OSF.IO/VR934](https://doi.org/10.17605/OSF.IO/VR934)
- **GitHub repository** (frozen at submission tag `v1.0-osf-deposit`): https://github.com/Roverlucas/llm-evidence-synthesis-reproducibility
- **License**: code under MIT; data, prompts, and manuscript materials under CC-BY 4.0
- **Companion paper**: Rover & Tadano (2026), "Hidden Non-Determinism in Large Language Model APIs: A Lightweight Provenance Protocol", JAIR (in press); the provenance protocol applied here is validated independently in that paper.

## Statement of originality and authorship

The work has not been published previously and is not under consideration elsewhere. Both authors approved the final version. The two authors contributed as follows: **Lucas Rover** conceived the study, designed the protocol, developed the software, conducted all experiments and analyses, and wrote the manuscript. **Yara de Souza Tadano** supervised the research, contributed to methodology design, and reviewed the manuscript. We declare no competing interests.

## Suggested reviewers (to be confirmed)

We respectfully suggest the following reviewers, all of whom have published methodological work in LLM-assisted evidence synthesis or LLM non-determinism and have no co-authorship or institutional conflict with us:

- **Gerald Gartlehner, MD MPH** — Danube University Krems, Austria — author of the most-cited LLM extraction reproducibility paper (Claude 2, JCE 2024). gerald.gartlehner@donau-uni.ac.at
- **Yutaka Oami, MD PhD** — University of Tsukuba, Japan — author of GPT-4 Turbo screening evaluations published in RSM. (email TBD)
- **Linnea Jensen, MD** — Aarhus University, Denmark — author of ChatGPT-4o inter-session extraction reliability (2025). (email TBD)
- **Berkant Atil** — author of "Non-Determinism of 'Deterministic' LLM Settings" (2024). (email TBD)

We respectfully request that the following be excluded from review because of recent overlapping work or close collaboration:
- (No exclusions at this time. Confirm with co-author Yara Tadano before final submission.)

## Anticipated timing

- **Pre-submission inquiry**: drafted 2026-03-20, status to be confirmed before final submission.
- **Dual-labeling P1-A**: in progress (Profa. Yara is recruiting the two independent validators); expected completion within ~3 weeks; results integrated in camera-ready version.
- **Target submission date**: ~2026-06-15 (subject to dual-labeling completion).

Thank you for considering our work. We would be delighted to address any preliminary questions during the inquiry phase.

Best regards,

**Lucas Rover, MSc**
PhD Student, Programa de Pós-Graduação em Sustentabilidade Ambiental Urbana
Universidade Tecnológica Federal do Paraná (UTFPR), Curitiba, Brazil
ORCID: [0000-0001-6641-9224](https://orcid.org/0000-0001-6641-9224)
Email: lucasrover@alunos.utfpr.edu.br
On behalf of co-author **Yara de Souza Tadano, DSc** (UTFPR, supervisor)

---

## Pre-submission checklist for Lucas before final send

- [ ] Confirm pre-submission inquiry was sent (check email sent items / confirm with Yara)
- [ ] Confirm dual-labeling Fleiss κ results integrated into main.tex §3.3
- [ ] Replace "results to be reported in the camera-ready version" placeholder
- [ ] Confirm suggested-reviewer emails for Oami, Jensen, Atil
- [ ] Get Yara's sign-off on final manuscript + cover letter
- [ ] Verify OSF deposit is public and contains all files per MANIFEST.md
- [ ] Verify GitHub tag `v1.0-osf-deposit` matches the submitted manuscript commit
- [ ] Tag a `v1.1-rsm-submission` if any post-deposit edits were made
- [ ] Zenodo DOI minted (if separate from OSF DOI)
- [ ] All co-authors approved (currently 2: L.R., Y.S.T.)

---

*Last updated: 2026-05-20*
