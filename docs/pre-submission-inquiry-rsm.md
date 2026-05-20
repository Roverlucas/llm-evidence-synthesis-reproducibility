# Pre-Submission Inquiry — Research Synthesis Methods

**Date:** 2026-03-20
**Status:** DRAFT — ready to send

---

## Email

**To:** dmavridi@uoi.gr, tpigott@gsu.edu
**From:** lucasrover@alunos.utfpr.edu.br
**Subject:** Pre-submission inquiry: Reproducibility of pollution-health evidence synthesis using LLM-assisted screening and extraction (36,000 LLM calls, 6 models)

---

Dear Professors Mavridis and Pigott,

I am writing to inquire whether the following manuscript would be suitable for Research Synthesis Methods.

**Title:** "Reproducibility of Pollution–Health Evidence Synthesis Using LLM-Assisted Screening and Extraction"

**Summary:** Large language models are increasingly used for abstract screening and data extraction in systematic reviews, yet a critical assumption — that identical inputs produce identical outputs — remains largely untested at scale. We conducted what we believe is the largest reproducibility experiment in this domain: 36,000 LLM calls across 120 experimental runs involving six models (LLaMA 3 8B, Mistral 7B, Gemma 2 9B, Claude Sonnet 4.5, Gemini 2.5 Pro, GPT-4.1) applied to a 500-abstract PubMed corpus on PM2.5 and respiratory health.

**Key findings:**
- All three locally deployed open-weight models achieved perfect determinism (EMR = 1.000) in both screening and extraction.
- Cloud API models exhibited substantial non-determinism: extraction Exact Match Rates ranged from 0.050 (Claude) to 0.200 (Gemini), despite temperature = 0 and fixed seeds.
- Structured extraction amplified non-determinism by 13–37× compared to binary screening — a phenomenon not previously documented.
- Prior studies report 94–97% reproducibility using per-field metrics and 2–3 repetitions; our whole-output analysis across 10 runs reveals that only 5–20% of extraction outputs are truly identical, exposing a measurement gap of nearly 20×.
- Meta-analytic propagation analysis showed that 5–21% of articles yielded different numbers of effect estimates across runs, meaning that the composition of a meta-analysis depends on which LLM run generated its inputs.

**Relevance to RSM:** This work directly addresses the reproducibility dimension of LLM-assisted evidence synthesis — a topic of growing interest in recent RSM publications, including Oami et al. (2025, doi:10.1017/rsm.2025.10014) and Li et al. (2025, doi:10.1017/rsm.2025.10007). While these studies evaluate LLM accuracy, our study is the first to systematically measure how non-determinism propagates through a complete two-stage synthesis pipeline and how it affects meta-analytic conclusions. We propose practical recommendations (multiple repetitions, provenance hashing, local deployment) that are immediately actionable by systematic reviewers.

The manuscript is approximately 8,000 words with 9 tables, 3 figures, and supplementary materials. All code, data, prompts, and raw outputs are publicly available. The manuscript is not under consideration elsewhere.

We would be grateful for your guidance on whether this work falls within the scope of RSM.

Thank you for your time and consideration.

Best regards,

Lucas Rover, MSc
PhD Student, Programa de Pós-Graduação em Sustentabilidade Ambiental Urbana
Universidade Tecnológica Federal do Paraná (UTFPR), Curitiba, Brazil
ORCID: 0000-0001-6641-9224
Email: lucasrover@alunos.utfpr.edu.br
