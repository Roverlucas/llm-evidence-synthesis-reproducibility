# OSF Upload Manifest

Files to upload, grouped by OSF component. Sizes are approximate; total deposit ≈ 75 MB (well within OSF free-tier limits).

---

## Component 1 — Manuscript

| File | Path in repo | Size | Notes |
|------|-------------|------|-------|
| main.pdf | `article/main.pdf` | ~780 KB | Current draft, 29 pp |
| main.tex | `article/main.tex` | ~80 KB | LaTeX source |
| references.bib | `article/references.bib` | varies | Bibliography |
| supplementary.pdf | `article/supplementary.pdf` | ~410 KB | 19 pp |
| supplementary.tex | `article/supplementary.tex` | varies | LaTeX source |
| CUP-JNL-DTM.cls | `article/CUP-JNL-DTM.cls` | small | Template (RSM-compatible) |

---

## Component 2 — Data

| File / Folder | Path in repo | Size | Notes |
|---------------|-------------|------|-------|
| corpus_500.json | `data/corpus/corpus_500.json` | ~5 MB | 500 PubMed abstracts (titles + abstracts + metadata) |
| gold_standard/ | `data/gold_standard/` | ~1 MB | Heuristic gold labels + templates |
| raw_outputs/ | `data/raw_outputs/` | ~50 MB | Full LLM outputs per stack/run (12 stacks × 10 runs × 2 stages) |
| dual_labeling/ | `data/dual_labeling/` | ~1.2 MB | Protocol v1.2, both returned label sets, agreement statistics, reconciliation package |

Optional: zip `raw_outputs/` per stack for cleaner browsing on OSF.

---

## Component 3 — Code (link, not upload)

Link the OSF "Code" component to the GitHub repo at the deposit commit:

- **URL**: https://github.com/Roverlucas/llm-evidence-synthesis-reproducibility
- **Commit at deposit**: `38873a2` (2026-05-11)
- **Tag**: create `v1.0-osf-deposit` before linking — `git tag -a v1.0-osf-deposit -m "OSF deposit snapshot" && git push origin v1.0-osf-deposit`
- **Zenodo integration**: connect repo to Zenodo (https://zenodo.org/account/settings/github/) so future tags auto-mint Zenodo DOIs as well

---

## Component 4 — Analyses

| File | Path in repo | Notes |
|------|-------------|-------|
| fleiss_kappa.json | `analysis/fleiss_kappa.json` | Inter-run agreement (P1.c) |
| bertscore_results.json | `analysis/bertscore_results.json` | Raw F1 |
| bertscore_results_full.json | `analysis/bertscore_results_full.json` | Raw + rescaled F1 (P1.a) |
| blindage/ | `analysis/blindage/` | 16 sensitivity analyses |
| → multiple_comparison.json | `analysis/blindage/multiple_comparison.json` | McNemar + Holm + BH-FDR (P1.b) |
| → random_effects_per_run.json | `analysis/blindage/random_effects_per_run.json` | DL + HKSJ (P2.a) |
| → small_literature_sim.json | `analysis/blindage/small_literature_sim.json` | Unstable null-crossing rates |
| → rule_of_three.json | `analysis/blindage/rule_of_three.json` | EMR=1.000 CI fix |

---

## Component 5 — Pre-Registration: Dual-Human Labeling

✅ **Done.** Registered as frozen OSF Registration `fgn3e` (DOI `10.17605/OSF.IO/FGN3E`) on 2026-05-12, using the "OSF Preregistration" template, from component `8z6fy`. Public, not embargoed. It pre-dates all label collection.

Deposited at registration time (the pre-commitment layer):

| File | Path in repo | Notes |
|------|-------------|-------|
| labeling_protocol.md | `data/dual_labeling/protocols/labeling_protocol.md` | v1.1 (2026-04-25) — the version registered |
| invite_email_template.md | `data/dual_labeling/protocols/invite_email_template.md` | Recruitment template |
| subset_100_labeler{1,2}.csv | `data/dual_labeling/exports/` | Blank templates as sent to the raters |
| extraction_25_labeler{1,2}.csv | `data/dual_labeling/exports/` | Blank templates (superseded — see below) |
| compute_kappa.py | `scripts/dual_labeling/compute_kappa.py` | Cohen's κ computation, registered before use |

Produced after registration (the evidence layer, for the sub-registration update):

| File | Path in repo | Notes |
|------|-------------|-------|
| subset_100_labeler1_RETURNED.csv | `data/dual_labeling/returned/` | Isabelle, 2026-07-29 (+ raw `.xlsx` source) |
| subset_100_labeler2_RETURNED.csv | `data/dual_labeling/returned/` | Luiza, 2026-07-15 |
| kappa_report.json, kappa_statistics.json | `data/dual_labeling/results/` | κ, intervals, PABAK, marginal-homogeneity tests, per-stratum |
| discordances.csv, confusion_matrix.csv | `data/dual_labeling/results/` | The 25 discordant items |
| labeling_protocol.md | `data/dual_labeling/protocols/` | **v1.2** — the registered contingency (c) |
| reconciliation/ | `data/dual_labeling/reconciliation/` | Blinded re-rating sheets + coordinator audit sheet |
| kappa_statistics.py, build_gold_standard.py, rebuild_extraction_set.py, ingest_labeler1_xlsx.py | `scripts/dual_labeling/` | Analysis and consolidation tooling |

⚠️ The `extraction_25_*` templates registered in May are superseded: that subset was drawn from the LLM silver standard before human labels existed, and only 13 of its 25 items survive human consensus. Stage B is rebuilt from the human gold standard; the substitution and its reason belong in the sub-registration update.

⚠️ `PROVENANCE_SHA256.txt` must be regenerated before re-depositing — the archived copy predates every file in the evidence layer above.

---

## Total deposit estimate

- Manuscript: ~1.5 MB
- Data: ~56 MB (or ~10 MB if `raw_outputs/` is zipped and partially curated)
- Code: link only (0 MB on OSF)
- Analyses: ~10 MB
- Pre-Registration: ~50 KB

**Total**: ~70-75 MB — well within OSF free tier (5 GB per file, no total cap).

---

## SHA-256 Provenance

All JSON analysis files already include sha256 hashes embedded in their `metadata` block. To generate a master provenance file for the upload:

```bash
cd /Users/lucasrover/llm-evidence-synthesis-reproducibility
find article data analysis -type f \( -name "*.pdf" -o -name "*.tex" -o -name "*.json" -o -name "*.csv" -o -name "*.md" \) \
  -exec shasum -a 256 {} \; > osf_package/PROVENANCE_SHA256.txt
```

Upload `PROVENANCE_SHA256.txt` as the last file in the OSF root so reviewers can verify any downloaded artifact.
