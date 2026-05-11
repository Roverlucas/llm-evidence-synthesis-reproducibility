# Citation Snippets — Ready to Paste

**OSF project registered 2026-05-11**: https://osf.io/vr934 (DOI: `10.17605/OSF.IO/VR934`). The pre-registration sub-component (Step 5 of UPLOAD_INSTRUCTIONS) will issue a separate DOI — `YYYYY` placeholders below should be updated when that registration is created.

---

## 1. For the NatComms Revision Manuscript

### In-text citation
> "Validation of the silver-standard methodology across 500 abstracts is reported in our companion paper (Rover et al., under review at *Research Synthesis Methods*; OSF: 10.17605/OSF.IO/VR934)."

### BibTeX
```bibtex
@misc{rover2026rsm,
  title  = {Reproducibility of Pollution--Health Evidence Synthesis using LLM-Assisted Screening and Extraction},
  author = {Rover, Lucas and Tadano, Yara de Souza},
  year   = {2026},
  note   = {Manuscript under review at \textit{Research Synthesis Methods}},
  doi    = {10.17605/OSF.IO/VR934},
  url    = {https://osf.io/vr934}
}
```

---

## 2. For the RSM Manuscript — Data Availability Statement

> **Data Availability.** All data, code, and pre-registered protocols supporting this study are deposited at the Open Science Framework (https://doi.org/10.17605/OSF.IO/VR934) and the underlying code is mirrored on GitHub (https://github.com/Roverlucas/llm-evidence-synthesis-reproducibility, frozen at commit `38873a2`, tag `v1.0-osf-deposit`). The dual-human labeling protocol is pre-registered as a sub-component of the OSF project (https://doi.org/10.17605/OSF.IO/YYYYY); results of the dual-labeling validation are in progress at the time of submission and will be reported as a sub-registration update.

---

## 3. For the RSM Manuscript — Footnote on Pre-Commitment

Add a footnote where the dual-labeling protocol is first introduced (around `main.tex:289`):

> The dual-human labeling protocol (Cochrane κ≥0.80 target, two independent raters, tie-broken by the senior author) was pre-registered on OSF prior to label collection (https://doi.org/10.17605/OSF.IO/YYYYY).

---

## 4. For the OSF Project Description (auto-generated citation)

OSF auto-generates this for the project page. Paste it back into the manuscript references if needed:

> Rover, L., & Tadano, Y. S. (2026, May 11). Reproducibility of Pollution–Health Evidence Synthesis using LLM-Assisted Screening and Extraction. https://doi.org/10.17605/OSF.IO/VR934

---

## 5. For Linking Companion Papers

When the manuscripts are accepted:

- **RSM paper accepted** → update OSF citation note from "under review" to journal + volume/year
- **NatComms paper accepted** → add cross-link from RSM OSF project to NatComms DOI
- Both OSF entries should mutually cite each other in the "Wiki" or "Description"

---

## 6. Pre-Registration DOI (sub-component)

When the dual-labeling registration is created in Step 5 of `UPLOAD_INSTRUCTIONS.md`, OSF assigns a **separate DOI** (different from the main project DOI). Reference it as:

> Rover, L., & Tadano, Y. S. (2026). Pre-registration: Dual-Human Labeling Protocol for LLM Evidence-Synthesis Validation. OSF Registrations. https://doi.org/10.17605/OSF.IO/YYYYY

Use this DOI specifically in any text discussing the dual-labeling protocol commitment.

---

## 7. Twitter/Bluesky Announcement (optional, when public)

> 🧪 New OSF deposit: 500-abstract PM2.5/respiratory corpus, 36K LLM runs across 6 deployment stacks, full code+data+pre-registration. Manuscript on LLM non-determinism in evidence synthesis under review at @ResSynthMethods.
> 🔗 https://osf.io/vr934
> #OpenScience #ReproducibleResearch #SystematicReview #LLM

---

## DOI Placeholder Reminders

After OSF registration, **find-and-replace** the following placeholders across all files:

| Placeholder | Replace with |
|-------------|-------------|
| `10.17605/OSF.IO/VR934` | Main project DOI |
| `10.17605/OSF.IO/YYYYY` | Pre-Registration DOI (different — sub-component) |
| `osf.io/vr934` | Short URL of project |
| `osf.io/YYYYY` | Short URL of pre-registration |

Files containing placeholders to update:
- `osf_package/README.md`
- `osf_package/CITATIONS.md`
- `article/main.tex` (Data Availability + footnote)
- Companion paper's response letter
