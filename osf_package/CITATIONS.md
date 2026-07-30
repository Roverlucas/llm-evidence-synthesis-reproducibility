# Citation Snippets — Ready to Paste

**Both OSF deposits exist and their DOIs are final.** Verified against the OSF API on 2026-07-29.

| Object | ID | DOI | Date |
|--------|----|-----|------|
| Project (public, 4 components) | `vr934` | `10.17605/OSF.IO/VR934` | created 2026-05-11 |
| Registration — Dual-Human Labeling Protocol (frozen, public, not embargoed) | `fgn3e` | `10.17605/OSF.IO/FGN3E` | registered 2026-05-12 |

The registration is a frozen snapshot of the component `8z6fy` and **pre-dates all label collection** (labels returned 2026-07-15 and 2026-07-29), so pre-commitment claims about the labeling protocol are supportable. Note the distinction when writing: `vr934` is a *project* (mutable, no `date_registered`), `fgn3e` is a *registration*. Only the second supports the phrase "pre-registered".

---

## 1. For the NatComms Revision Manuscript

### In-text citation
> "Validation of the silver-standard methodology across 500 abstracts is reported in our companion paper (Rover & Tadano, under review at *Research Synthesis Methods*; OSF: 10.17605/OSF.IO/VR934)."

⚠️ Uses `Rover & Tadano` to match the two-author byline and the BibTeX entry below. If the RSM author list expands to include the raters, switch both this snippet and the BibTeX to `Rover et al.` in the same edit — earlier drafts had `et al.` here beside a two-author BibTeX, which is the inconsistency this note exists to prevent.

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

> **Data Availability.** All data, code, and protocols supporting this study are deposited at the Open Science Framework (https://doi.org/10.17605/OSF.IO/VR934) and the underlying code is mirrored on GitHub (https://github.com/Roverlucas/llm-evidence-synthesis-reproducibility). The dual-human labeling protocol is deposited separately as a frozen OSF registration (https://doi.org/10.17605/OSF.IO/FGN3E, 2026-05-12), which pre-dates label collection. Stage-A screening labels, agreement statistics, and the v1.2 protocol amendment are in the repository under `data/dual_labeling/`; Stage-B extraction labels are pending and will be added in a sub-registration update.

> ⚠️ Before pasting: replace the GitHub URL with the tag for the submitted version. The earlier `v1.0-osf-deposit` tag points at `506adcd` (2026-05-11) and predates the dual-labeling evidence entirely — citing it would send reviewers to a snapshot that does not contain the results the paper reports. The commit `38873a2` referenced in earlier drafts is *not* the tagged commit; do not cite the two as if they were the same.

---

## 3. For the RSM Manuscript — Pre-Commitment Statement

✅ **Already applied.** The registration DOI is now stated inline in the Methods where
the dual-labeling validation is introduced, together with the registration date and the
label-return dates, so no separate footnote is needed. `scripts/check_pending.sh` fails
if a pre-registration claim ever appears in `main.tex` without the DOI beside it.

Kept here as the canonical wording, in case it is needed for another venue:

> The dual-human labeling protocol (Cochrane κ≥0.80 target, two independent raters each blinded to the other, tie-broken by the senior author) was pre-registered on OSF prior to label collection (https://doi.org/10.17605/OSF.IO/FGN3E).

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

> Rover, L., & Tadano, Y. S. (2026). Pre-registration: Dual-Human Labeling Protocol for LLM Evidence-Synthesis Validation. OSF Registrations. https://doi.org/10.17605/OSF.IO/FGN3E

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
| `10.17605/OSF.IO/FGN3E` | Pre-Registration DOI (different — sub-component) |
| `osf.io/vr934` | Short URL of project |
| `osf.io/fgn3e` | Short URL of pre-registration |

Files containing placeholders to update:
- `osf_package/README.md`
- `osf_package/CITATIONS.md`
- `article/main.tex` (Data Availability + footnote)
- Companion paper's response letter
