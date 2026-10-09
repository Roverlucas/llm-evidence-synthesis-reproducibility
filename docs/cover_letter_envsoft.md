# Cover Letter — Environmental Modelling & Software

**Status:** DRAFT v1 — 2026-08-22. Awaiting the tie-break on 11 residual disagreements before final send.

**To:** The Editors, *Environmental Modelling & Software*
**From:** Lucas Rover (Corresponding Author), Universidade Tecnológica Federal do Paraná, Curitiba, Brazil
**Subject:** Submission — "A reproducibility audit harness for LLM-assisted evidence extraction in environmental assessment"

---

Dear Editors,

We are submitting the manuscript above for consideration as a Research Article.

## What the paper does

Environmental evidence bases and regulatory reviews are increasingly assembled with the help of large language models. When a pipeline step is delegated to an LLM, that step becomes software — but software with a property the components around it do not have: running it twice on the same input does not guarantee the same output, and whether it happens to behave deterministically depends on how the model is served rather than on which model was named in the methods.

We audit that property across a complete two-stage extraction pipeline. Six deployment stacks — three served locally through Ollama, three through commercial APIs — each executed ten times over a 500-abstract corpus on fine particulate matter and respiratory health, screening and then extracting structured data. 35,636 of 36,000 calls completed. A decision model that returns option probabilities instead of sampled text was added on the screening stage.

Five results:

1. **Local stacks returned bit-identical output across all ten runs; API-served stacks reached an extraction Exact Match Rate of 0.150 to 0.470** at temperature zero verified as transmitted. The most reproducible of the three is the one that accepts no seed.

2. **The same weights, served differently, disagree.** Running `meta-llama/llama-3-8b-instruct` locally and through a cloud endpoint produced systematic disagreement on 167 of the 430 abstracts where both returned a decision, all in the same direction. The variation is a property of the serving stack, not of the model.

3. **Constraining the output shape is not a fix.** Against a run-count-matched baseline, a fixed-slot prompt degraded reproducibility on one stack, improved it on another and left the third unchanged.

4. **Schema conformance is a separate axis from reproducibility.** The local stacks reproduce perfectly while returning schema-valid extraction output on 38–43% of calls; one cloud stack conforms on 2.6%. Determinism and usability are different properties, and measuring only the first hides the second.

5. **Returning the distribution does not remove the variation.** The decision model reached a screening Exact Match Rate of 0.956, inside the range of the generative API stacks, and the probability it assigned to the same option moved between identical calls for most abstracts. What the distribution adds is visibility: an abstract whose probabilities move can be routed to a human reader.

## Why EMS

The journal's scope covers quality assurance and evaluation of models, data and procedures, with reliability and validation backed by quantitative results. That is the register of this paper: it does not advance a hydrological or epidemiological claim, it measures whether a procedure now entering environmental workflows behaves as its users assume.

Three papers in EMS made us confident this is the right venue, and each shaped the manuscript.

**Yoon et al. (2026, 203:107030)** scaled open-weight models for hydropower regulatory extraction. Their experimental setup fixes temperature at zero "thereby eliminating sampling variability and facilitating consistent outputs across multiple experimental runs", and executes each configuration once. We cite this not as a criticism — it is the field's standard practice and their documentation of it is exemplary, which is precisely what let us identify the premise — but because it states plainly the assumption our paper sets out to test.

**Park et al. (2026, 205:107142)** reached the same boundary we did, from the opposite side. Constraining an LLM agent to operate SWAT+ through a typed, range-validated interface shortened its calibration path from 62.0 to 21.9 model evaluations and produced reviewable provenance — the structure delivered on control. What it did not deliver was validity: an acceptable goodness-of-fit did not guarantee hydrological quality, and a corruption task showed that logs and range constraints alone could not detect a physically corrupted model state. We constrain the output format and find no consistent reproducibility gain; they constrain the interface and find control without correctness. Both results say the control layer is necessary and not sufficient.

**Schlögl et al. (2026, 200:106962)** catalogue the barriers to reproducibility in geoscientific data analysis and already name ours — "non-deterministic model outputs from generative AI" — among them. They name it; they were not designed to measure it. This paper supplies the measurement, in the dimension their taxonomy calls methodological reproducibility.

We also note **Zhu et al. (2025, 186:106323)**, whose framework diagnoses the individual processes where computational reproducibility fails. That diagnostic step presumes a process that behaves the same way when re-executed. The two quantities we report are cheap enough to serve as the per-process check such a framework would need to reach an LLM-mediated step.

## What we release

`llm-repro-harness` places any set of endpoints behind one runner interface and takes the corpus, prompts, schema, endpoint list, decoding parameters and repetition count from configuration rather than code. It emits a run card per call and computes Exact Match Rate with bootstrap intervals, pairwise disagreement, inter-run Fleiss' κ, schema conformance, and the propagation of run-to-run variation into a pooled estimate.

We are aware that per-vendor numbers age. Stacks observed in a given window will not survive the next provider-side update---one of ours is now scheduled for retirement--- and that is the reason the instrument exists rather than an objection to it: a figure that expires needs a procedure that can be re-run. The environmental evidence task here exercises the harness on a case where the downstream consequence is measurable. It is the demonstration, not the scope.

Code: https://github.com/Roverlucas/llm-evidence-synthesis-reproducibility (MIT). Data and frozen artefacts: OSF `vr934`, https://doi.org/10.17605/OSF.IO/VR934 (CC BY 4.0). Human labeling protocol as an immutable pre-registration: https://doi.org/10.17605/OSF.IO/FGN3E.

## Two things we report against ourselves

We would rather you meet these here than find them in the manuscript.

**The human reference standard missed its target.** Two blinded raters working from the pre-registered protocol reached κ = 0.529 against a pre-specified 0.80. We report the shortfall as measured, trace it to one under-specified inclusion criterion, and carry the standard forward as asymmetrically valid — firm on specificity, a lower bound on sensitivity — rather than recomputing a coefficient that would clear the threshold with no evidential content behind it.

**One of our own clients did not transmit the configuration we declared.** It attached the temperature field to the request body only when the value exceeded zero, so 6,000 Claude calls requesting zero were sent without it and ran at the provider default of 1.0. The run cards recorded 0.0 regardless, because the provenance hash was computed over the requested parameters rather than the transmitted payload. We found this by reading the client, not by instrument. We corrected the client so that every call record stores the temperature actually sent, re-ran the complete Claude arm at zero in October 2026 with the same snapshot, and fixed in the public decision log, as the re-run started, that it would replace the first execution whatever its values. The first execution is reported in the Supplement as a temperature contrast. The cost is that the Claude stack is eight months younger than the others and ran on a snapshot now announced for retirement; we state both in the paper. The defect is the paper's own recommendation arrived at the hard way: provenance must record what was transmitted, not what was requested.

## Declarations

The work is original, is not under consideration elsewhere, and all authors have approved the submission. We declare no competing interests. AI-based tools were used for code development and manuscript editing; the timeline separating result computation from writing assistance is documented in the manuscript and auditable in the public commit history.

Thank you for considering our work.

**Lucas Rover, MSc**
PhD Student, Programa de Pós-Graduação em Sustentabilidade Ambiental Urbana
Universidade Tecnológica Federal do Paraná
lucasrover@alunos.utfpr.edu.br · ORCID 0000-0001-6641-9224
