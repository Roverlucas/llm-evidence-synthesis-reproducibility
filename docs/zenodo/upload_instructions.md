# Zenodo Upload Instructions

**Quando usar:** após todos os experimentos de blindage terminarem (LLaMA cloud 10 runs, DeepSeek silver 5 runs, fixed-slot 3×3 runs) E após dual-labeling humano completar (Cohen's κ + extraction gold).

**Tempo estimado de upload:** 5-10 min

---

## Passo 1 — Preparar tarball

Já temos um script. Rode quando quiser:

```bash
cd /Users/lucasrover/llm-evidence-synthesis-reproducibility
bash docs/zenodo/build_tarball.sh
```

Isso gera `dist/llm-evidence-synthesis-reproducibility-v1.0.tar.gz` (~70MB).

**Conteúdo do tarball:**
- `corpus_500.json` (1.4 MB) — corpus completo
- `gold_standard/` — labels heurísticos + (depois) gold humano
- `dual_labeling/` — subset de 100 abstracts + protocolo + κ resultados
- `prompts/` — todos os prompts (variable-length + fixed-slot)
- `schemas/` — JSON schemas
- `raw_outputs/` (~50 MB) — todos os 36,000+ outputs
- `analysis/` — todos os JSONs de resultados (incluindo blindage)
- `scripts/` — todos os scripts reproduzíveis
- `article/main.tex` + `article/supplementary.tex` (sem PDFs compilados)
- `requirements-lock.txt`, `LICENSE`, `README.md`
- `docs/zenodo/zenodo_metadata.json` — metadata para upload

---

## Passo 2 — Upload no Zenodo

1. **Login:** https://zenodo.org → Sign in com ORCID 0000-0001-6641-9224
2. **New upload:** botão "+ Upload" no topo direito
3. **Drag & drop:** o arquivo `dist/llm-evidence-synthesis-reproducibility-v1.0.tar.gz`
4. **Aguardar upload** (~2-5 min para 70MB)

---

## Passo 3 — Preencher metadata

Use os valores do `zenodo_metadata.json` que está no tarball. Resumo:

| Campo | Valor |
|-------|-------|
| **Title** | Reproducibility of Pollution–Health Evidence Synthesis Using LLM-Assisted Screening and Extraction — code, data, prompts, and raw outputs (companion to Research Synthesis Methods submission) |
| **Upload type** | Dataset |
| **Authors** | Rover, Lucas (ORCID: 0000-0001-6641-9224) ; Tadano, Yara de Souza |
| **Affiliations** | UTFPR (PPGSAU para Lucas; Departamento de Matemática para Yara) |
| **Description** | (cole o conteúdo do `zenodo_metadata.json` campo `description` — Zenodo aceita HTML básico) |
| **Keywords** | (24 keywords listadas no JSON; cole separadas por vírgula) |
| **Publication date** | 2026-04-26 (ou data de upload) |
| **Language** | English |
| **License** | Creative Commons Attribution 4.0 (CC BY 4.0) |
| **Communities** | Open Science Framework + Reproducibility |
| **Related identifiers** | https://github.com/Roverlucas/llm-evidence-synthesis-reproducibility (relation: "is supplement to", type: software) |

---

## Passo 4 — Reservar DOI ANTES de publicar

Zenodo permite reservar DOI antes da publicação:

1. Em "Publication", clicar em **"Reserve DOI"**
2. Copiar o DOI gerado: `10.5281/zenodo.XXXXXXX`
3. **Adicionar este DOI ao manuscrito** em §Data Availability:

```latex
\section*{Data Availability}
All code, data, prompts, JSON schemas, raw experimental outputs (36,000+ LLM
calls), and analysis scripts are publicly available at:
\begin{itemize}
  \item Zenodo: \url{https://doi.org/10.5281/zenodo.XXXXXXX} (this version)
  \item GitHub: \url{https://github.com/Roverlucas/llm-evidence-synthesis-reproducibility}
\end{itemize}
The Zenodo deposit is the canonical archival reference; the GitHub
repository is updated continuously and serves as the development mirror.
```

4. **Após adicionar o DOI ao manuscrito**, voltar ao Zenodo e clicar **"Publish"**.

---

## Passo 5 — Após publicação

- Salvar permalink: `https://zenodo.org/records/XXXXXXX`
- DOI fica permanente: `10.5281/zenodo.XXXXXXX`
- Atualizar README.md do GitHub com badge:

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

---

## Versionamento

Se precisar atualizar (p.ex., após dual-labeling completar e gerar v1.1):

1. No Zenodo, ir ao record publicado
2. Clicar "New version"
3. Upload do novo tarball
4. Manter mesma metadata (Zenodo herda)
5. Publicar — gera novo DOI mas mantém o "concept DOI" original

---

## Checklist final pré-upload

- [ ] Tarball gerado (~70 MB)
- [ ] Metadata `zenodo_metadata.json` revisada
- [ ] DOI reservado e adicionado ao manuscrito
- [ ] Manuscrito menciona Zenodo em §Data Availability
- [ ] README do GitHub linka para Zenodo
- [ ] Após publicação, badge DOI no README

---

*Document version: 1.0
Last modified: 2026-04-26*
