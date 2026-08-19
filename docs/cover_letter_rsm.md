# Cover Letter — Research Synthesis Methods Submission

**Status:** DRAFT v2 — 2026-07-29. Stage-A dual labeling complete; awaiting Stage-B extraction labels before final send.

**To:** Editors-in-Chief, *Research Synthesis Methods*
Dimitris Mavridis & Terri D. Pigott
**From:** Lucas Rover (Corresponding Author), Universidade Tecnológica Federal do Paraná
**Subject:** Submission: "Reproducibility of Pollution–Health Evidence Synthesis Using LLM-Assisted Screening and Extraction"

---

Dear Professors Mavridis and Pigott,

We are pleased to submit our original research article, **"Reproducibility of Pollution–Health Evidence Synthesis Using LLM-Assisted Screening and Extraction"**, for consideration in *Research Synthesis Methods*.

## What we did

We conducted what we believe is the most comprehensive empirical evaluation of LLM reproducibility in evidence synthesis published to date: **36,000 LLM calls across 120 experiment runs**, applying six *deployment stacks*---three local (LLaMA 3 8B, Mistral 7B, Gemma 2 9B served via Ollama on Apple M4) and three API-served (Claude Sonnet 4.5/Anthropic, Gemini 2.5 Pro/Google, GPT-4.1/OpenAI)---to a 500-abstract PubMed corpus on PM₂.₅ and respiratory hospitalizations, through both abstract screening and structured data extraction.

## Why this matters for RSM readers

1. **Direct response to your 2025 RSM editorial on GenAI-assisted evidence synthesis** (Farotimi, Dunn, Van Lissa, Polanin, Mavridis & Pigott, DOI: 10.1017/rsm.2025.10058). The editorial called for methodological work characterizing reproducibility of generative-AI-assisted SR, including specific reporting requirements for prompt design, random-seed control, and external validation. Every requirement is addressed empirically in this manuscript.

2. **Falsifies a widely-held assumption.** Studies routinely report 94–97 % LLM "reproducibility" using per-field metrics over 2–3 repetitions. Applying a stricter whole-output metric across 10 repetitions reveals only **5–20 % of cloud-API extraction outputs are truly identical**---a measurement gap of nearly 20×.

3. **Establishes the unit of reproducibility.** Our same-weights desconfound experiment (serving identical `meta-llama/llama-3-8b-instruct` weights locally via Ollama and via DeepInfra cloud) produces 39 % systematic disagreement between the two deployments, showing that **identical weights do not yield identical behaviour once the serving stack changes**. The two arms share weights, prompt source, temperature and seed but not a byte-identical payload, and the manuscript scopes the inference accordingly. This reframes "which model" as the wrong abstraction for LLM-assisted SR documentation.

4. **Quantifies downstream impact.** A small-literature simulation under Hartung-Knapp-Sidik-Jonkman (Cochrane Handbook 6.5+ recommendation for k<10) shows up to **48.5 %** of k=10 subsamples experience run-dependent null-crossing reversals, depending on which LLM run generated the inputs.

## Methodological rigor we provide

- 10 repetitions per model × stage (vs. typical 2–3 in prior work)
- A formally pre-registered human validation protocol, frozen on OSF two months before any label was collected (DOI 10.17605/OSF.IO/FGN3E). Post-revision analyses were committed to the public repository before result computation; we describe those as timestamped, not pre-registered, and keep the distinction explicit in the manuscript.
- Two independent silver standards: within-study majority vote + external DeepSeek-R1 (different family, different training corpus, different decoding paradigm)
- Dual independent human labeling on a stratified 100-abstract subset, **completed and reported as measured**: Cohen's κ = 0.529 (95% CI 0.383–0.674), below the pre-registered Cochrane target of 0.80. We report the shortfall rather than soften it, and the manuscript treats it as a finding: the disagreement proved to be directional (exact McNemar p = 2.2×10⁻⁴) and traceable to a single ambiguous inclusion criterion, which we diagnosed, amended, and documented in a protocol revision. We believe an RSM readership will find the measured human baseline more useful than the aspirational threshold it failed to meet — particularly since it also revealed that our gold standard is asymmetrically valid, with a unanimous exclude side and a contested include side.
- SHA-256 provenance hashes on every input, output, and configuration
- Fleiss' κ multi-rater agreement across runs (in addition to EMR)
- McNemar's paired contrasts (replacing the original two-proportion z-test where outcomes are paired)
- HKSJ variance correction alongside DerSimonian-Laird
- Mechanism-mapping table (6 mechanisms × 5 deployment stacks) with documented/likely/possible/precluded classifications

## Open Science

- **OSF project**: public, DOI [10.17605/OSF.IO/VR934](https://doi.org/10.17605/OSF.IO/VR934)
- **Pre-registration of the human validation protocol**: frozen OSF registration of 2026-05-12, DOI [10.17605/OSF.IO/FGN3E](https://doi.org/10.17605/OSF.IO/FGN3E) — predates label collection
- **GitHub repository**: https://github.com/Roverlucas/llm-evidence-synthesis-reproducibility (submission tag to be set at final send; the older `v1.0-osf-deposit` tag predates the dual-labeling results and must not be cited as the submitted version)
- **License**: code under MIT; data, prompts, and manuscript materials under CC-BY 4.0
- **Companion paper**: Rover & Tadano (2026), "Hidden Non-Determinism in Large Language Model APIs: A Lightweight Provenance Protocol", JAIR (in press); the provenance protocol applied here is validated independently in that paper.

## Statement of originality and authorship

The work has not been published previously and is not under consideration elsewhere. Both authors approved the final version. The two authors contributed as follows: **Lucas Rover** conceived the study, designed the protocol, developed the software, conducted all experiments and analyses, and wrote the manuscript. **Yara de Souza Tadano** supervised the research, contributed to methodology design, and reviewed the manuscript. We declare no competing interests.

## Suggested reviewers (to be confirmed)

We respectfully suggest the following reviewers, all of whom have published methodological work in LLM-assisted evidence synthesis or LLM non-determinism and have no co-authorship or institutional conflict with us:

- **Gerald Gartlehner, MD MPH** — Danube University Krems, Austria — author of the most-cited LLM extraction reproducibility paper (Claude 2, Research Synthesis Methods 15(4):576–589, 2024). gerald.gartlehner@donau-uni.ac.at
- **Takehiko Oami, MD PhD** — Chiba University Graduate School of Medicine, Japan — author of GPT-4 Turbo screening evaluations published in RSM. (email TBD)
- **Mathias K. Jensen** — author of ChatGPT-4o inter-session extraction reliability (2025). (email TBD)
- **Berk Atil** — author of "Non-Determinism of 'Deterministic' LLM Settings" (2024). (email TBD)

We have no exclusion requests.

Thank you for considering our work.

Best regards,

**Lucas Rover, MSc**
PhD Student, Programa de Pós-Graduação em Sustentabilidade Ambiental Urbana
Universidade Tecnológica Federal do Paraná (UTFPR), Curitiba, Brazil
ORCID: [0000-0001-6641-9224](https://orcid.org/0000-0001-6641-9224)
Email: lucasrover@alunos.utfpr.edu.br
On behalf of co-author **Yara de Souza Tadano, DSc** (UTFPR, supervisor)

---

*Last updated: 2026-07-29. Internal checklist moved to `docs/submission_checklist.md` so that it cannot be sent to the editors with this letter.*
