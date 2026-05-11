# OSF Upload — Step-by-Step

Estimated total time: **~2 hours** (most is upload waiting; active work ~45 min).

---

## Step 0 — Prerequisites (5 min)

- [ ] OSF account: https://osf.io (free, login via ORCID for auto-linkage)
- [ ] ORCID of each co-author (see `CONTRIBUTORS.md`)
- [ ] GitHub repo tagged at the deposit commit:
  ```bash
  cd /Users/lucasrover/llm-evidence-synthesis-reproducibility
  git tag -a v1.0-osf-deposit -m "OSF deposit snapshot (2026-05-11)"
  git push origin v1.0-osf-deposit
  ```
- [ ] Generate the SHA-256 manifest:
  ```bash
  find article data analysis -type f \( -name "*.pdf" -o -name "*.tex" -o -name "*.json" -o -name "*.csv" -o -name "*.md" \) \
    -exec shasum -a 256 {} \; > osf_package/PROVENANCE_SHA256.txt
  ```

---

## Step 1 — Create the OSF Project (10 min)

1. Sign in at https://osf.io
2. Click **"Create new project"**
3. Fill:
   - **Title**: `Reproducibility of Pollution–Health Evidence Synthesis using LLM-Assisted Screening and Extraction`
   - **Description**: Paste the **Overview** section from `osf_package/README.md`
   - **Affiliated institution**: UTFPR (or leave blank if not in OSF's list)
   - **Category**: Project
   - **License**: CC-BY 4.0
4. Click **Create**

You now have a project page with a URL like `https://osf.io/abcd1`.

---

## Step 2 — Add Contributors (10 min)

In the project page → **Contributors** (left sidebar):

1. For each co-author from `CONTRIBUTORS.md`:
   - Click **"Add Contributor"**
   - Search by **name or ORCID** (preferred — auto-links profile)
   - If not on OSF: choose **"Add unregistered contributor"** and enter name + institutional email
2. Check **"Bibliographic Contributor"** for all (so they appear in auto-generated citations)
3. Set permission level:
   - You: **Administrator**
   - Profa. Yara: **Read+Write** (so she can edit)
   - Others: **Read** (or Read+Write if you want them to upload too)
4. **Order**: drag to match the manuscript author order (Rover, Siqueira, Bacalhau, Azevedo, Tadano)
5. Click **Save**

OSF will email each contributor an invite. They click to accept and OSF links their ORCID profile.

---

## Step 3 — Create the 5 Components (15 min)

In the project page → **"Add Component"** (top of file tree). Create these 5 components:

| Order | Component Name | Category | Description (1 sentence) |
|-------|---------------|----------|-------------------------|
| 1 | Manuscript | Article | Current draft of the manuscript and supplementary material (PDF + LaTeX source) |
| 2 | Data | Data | Corpus of 500 PubMed abstracts, gold standards, and raw LLM outputs (~50 MB) |
| 3 | Code | Software | Link to the GitHub repository at the deposit commit |
| 4 | Analyses | Analysis | Statistical analysis outputs (blindage suite, Fleiss' κ, BERTScore, HKSJ sensitivity) |
| 5 | Pre-Registration: Dual-Human Labeling | Other | Formal pre-registration of the dual-independent human-labeling protocol (in progress) |

For each component:
- Copy the relevant section of `README.md` into the component description
- Inherit project contributors (default: yes)
- Inherit license (default: CC-BY 4.0)

---

## Step 4 — Upload Files (60-90 min, mostly waiting)

For each component, drag-and-drop the files from `MANIFEST.md`. Order:

### 4.1 Manuscript component
Drag: `article/main.pdf`, `article/main.tex`, `article/references.bib`, `article/supplementary.pdf`, `article/supplementary.tex`, `article/CUP-JNL-DTM.cls`

### 4.2 Data component
Drag: `data/corpus/corpus_500.json`, `data/gold_standard/` (whole folder), `data/raw_outputs/` (whole folder; consider zipping per stack first to make navigation easier), `data/dual_labeling/` (whole folder)

**Tip**: For `raw_outputs/`, you can zip each stack subfolder before uploading:
```bash
cd /Users/lucasrover/llm-evidence-synthesis-reproducibility/data/raw_outputs
for d in */; do zip -r "${d%/}.zip" "$d"; done
```
Then upload the zips. This dramatically simplifies navigation.

### 4.3 Code component (no upload — link only)
- Click on the Code component
- **Add-ons** → **GitHub** → Connect → Authorize OSF
- Select repo `Roverlucas/llm-evidence-synthesis-reproducibility`
- (Optional, recommended) Connect Zenodo as well at https://zenodo.org/account/settings/github/ — push tag `v1.0-osf-deposit` and Zenodo mints a DOI automatically

### 4.4 Analyses component
Drag: `analysis/fleiss_kappa.json`, `analysis/bertscore_results.json`, `analysis/bertscore_results_full.json`, `analysis/blindage/` (whole folder)

### 4.5 Pre-Registration component
Drag: `data/dual_labeling/protocols/labeling_protocol.md`, `data/dual_labeling/protocols/invite_email_template.md`, 4 empty CSVs, `scripts/dual_labeling/compute_kappa.py`

### 4.6 Root — provenance manifest
Drag `osf_package/PROVENANCE_SHA256.txt` to the project root (not into a component).

---

## Step 5 — Create the Pre-Registration (Frozen) (15 min)

This is the **load-bearing** step that creates a permanent, immutable timestamp on the dual-labeling commitment.

1. Go to the **Pre-Registration: Dual-Human Labeling** component
2. Click **Registrations** (left sidebar) → **"New registration"**
3. Choose template: **"OSF Preregistration"** (good default; simpler than Registered Report)
4. Fill the template fields:
   - **Study design**: dual-independent labeling, 2 raters, 100 abstracts (Stage A) + 25 extractions (Stage B), Cochrane κ≥0.80 target, tie-breaker = senior author
   - **Hypotheses**: not applicable (this is a validation procedure, not a primary hypothesis)
   - **Analysis plan**: Cohen's κ (unweighted, binary collapse for INCLUDE/EXCLUDE), agreement % for extraction, MCC if useful
   - **Sample**: 100 abstracts from the 500-abstract main corpus, stratified
   - **Variables**: include/exclude (binary), confidence (HIGH/MED/LOW), rationale (free text), criteria_failed (numeric list); for Stage B: effect_estimate, ci_lower, ci_upper, lag, study_design, population
5. **Embargo**: 0 (immediate public) or up to 4 years if you want to defer disclosure of CSVs until the paper is accepted. **Recommendation**: 0 — full transparency strengthens credibility
6. Click **Register**

The registration is now **frozen and DOI'd**. You cannot edit content, but you can:
- Add more registrations later (e.g., post-completion update)
- Update the parent component freely (the registration stays as a snapshot)

---

## Step 6 — Verify and Make Public (10 min)

1. Project page → **Make Public** (top right)
2. OSF assigns the project DOI: `10.17605/OSF.IO/XXXXX`
3. Copy the DOI
4. Update `osf_package/CITATIONS.md` and the manuscript's footnote/data-availability statement with the real DOI
5. Edit `README.md` and `osf_package/README.md` in the repo to add the real DOI (commit + push)

---

## Step 7 — Update the Manuscript and Companion Paper (15 min)

Add the OSF DOI to:

1. **RSM manuscript** (`article/main.tex`):
   - Data Availability statement
   - Footnote on first mention of the dual-labeling protocol
2. **NatComms revision** (`/Users/lucasrover/paper-experiment/`):
   - Cite the RSM paper using the OSF DOI: `Rover et al. (in review, OSF: 10.17605/OSF.IO/XXXXX)`
3. **Both papers**: ensure citation snippets in `osf_package/CITATIONS.md` are consistent

---

## Common Pitfalls

| Problem | Fix |
|---------|-----|
| Co-authors don't accept invite | Re-send from Contributors page; check spam folder |
| Large file upload fails | Try Chrome (best OSF compatibility); use OSF's `osfclient` Python tool for batch uploads |
| GitHub link shows old commit | Ensure tag `v1.0-osf-deposit` is pushed; OSF caches for ~1h |
| Pre-registration won't accept "in progress" labeling | Choose "OSF Preregistration" template (most flexible); "Registered Report" templates are stricter |
| You forgot a file | Project files are mutable; just re-upload. Only Registrations are frozen |

---

## Time Budget

| Step | Duration |
|------|----------|
| 0 — Prerequisites | 5 min |
| 1 — Create project | 10 min |
| 2 — Add contributors | 10 min |
| 3 — Create components | 15 min |
| 4 — Upload files | 60-90 min |
| 5 — Pre-registration | 15 min |
| 6 — Verify and publish | 10 min |
| 7 — Update manuscripts | 15 min |
| **Total** | **~2-2.5 h** |

Most of step 4 is upload time — you can browse / answer email while files transfer.
