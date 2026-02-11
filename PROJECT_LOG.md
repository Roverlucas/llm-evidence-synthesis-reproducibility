# PROJECT LOG — LLM Evidence Synthesis Reproducibility

> Este arquivo rastreia toda evolução do projeto para continuidade entre sessões.
> **Sempre atualize este arquivo ao final de cada sessão ou marco relevante.**

---

## Informações do Projeto

| Campo | Valor |
|-------|-------|
| **Título** | Reproducibility of Pollution-Health Evidence Synthesis using LLM-Assisted Screening and Extraction |
| **ID** | paper-2026-002 |
| **Repositório** | https://github.com/Roverlucas/llm-evidence-synthesis-reproducibility |
| **Diretório local** | `/Users/lucasrover/llm-evidence-synthesis-reproducibility/` |
| **Squad** | Paper Factory (`/Users/lucasrover/Downloads/mmos-main/squads/paper-factory/`) |
| **Journal alvo (A)** | Research Synthesis Methods (IF 6.1) |
| **Idioma** | English |
| **PI** | Lucas Rover |
| **Criado em** | 2026-02-11 |

---

## Status Atual

| Fase | Status | Gate Score | Data |
|------|--------|------------|------|
| **Fase 0: Intake & Kickoff** | DONE | 85/100 | 2026-02-11 |
| **Fase 1: Scoping & Lacuna** | DONE | — | 2026-02-11 |
| **Fase 2: Desenho Metodológico** | DONE | — | 2026-02-11 |
| Fase 3: Execução Técnica | PENDING | — | — |
| Fase 4: Escrita | PENDING | — | — |
| Fase 5: Submissão | PENDING | — | — |

---

## Histórico de Sessões

### Sessão 1 — 2026-02-11

**Agentes ativados:** @study-conductor, @literature-specialist, @journal-strategy, @methodology-specialist

**Entregáveis produzidos:**

1. **Fase 0 — Kickoff (COMPLETO)**
   - `docs/project_charter/charter-v1.yaml` — Charter com 4 RQs, hipóteses H0/H1, tese, riscos
   - `docs/decisions/decision-log.md` — 9 decisões registradas
   - `configs/experiment.yaml` — Configuração completa do experimento
   - `configs/prompts/screening.txt` — Prompt de triagem de abstracts
   - `configs/prompts/extraction.txt` — Prompt de extração de dados
   - `configs/schemas/screening_output.json` — JSON Schema de triagem
   - `configs/schemas/extraction_output.json` — JSON Schema de extração
   - Commit: `75292f2` — feat: initialize project structure and charter

2. **Fase 1 — Literature Review (COMPLETO)**
   - `data/literature/paper-2026-002/search-strategy.md` — Estratégia de busca (3 bases, 3 blocos conceituais)
   - `data/literature/paper-2026-002/evidence-matrix.md` — 28 refs em 6 domínios
   - `data/literature/paper-2026-002/gap-analysis.md` — 3 gaps P0, 2 gaps P1
   - `data/literature/paper-2026-002/journal-strategy.md` — A/B/C definidos
   - Commit: `75ba8d6` — feat: complete Phase 1 literature review and journal strategy

3. **Fase 2 — Desenho Metodológico (COMPLETO)**
   - `data/methods/paper-2026-002/methods-spec.md` — Spec completa (11 seções)
   - `data/methods/paper-2026-002/validity-assessment.md` — 10 ameaças mapeadas, 4 tipos de validade
   - Decisões 10-13 registradas no decision log

---

## Decisões-Chave (Resumo)

| # | Decisão | Rationale |
|---|---------|-----------|
| 1 | Escopo: PM2.5 → respiratório | Mais abundante, RR padronizado |
| 2 | Corpus: 500 abstracts (100/100/300) | Robustez estatística |
| 3 | 3 modelos: LLaMA 3 8B + Claude + Gemini | Reutiliza infra JAIR + local vs API |
| 4 | 30 repetições por modelo | Suficiente para bootstrap + kappa |
| 5 | Variantes GRADE/policy → follow-up | Evitar scope creep |
| 6 | Repo público desde o início | Ciência aberta |
| 7 | Journal A: Research Synthesis Methods | Melhor fit para métodos de evidence synthesis |

---

## Números-Chave da Literatura

- **~875 papers** no PubMed sobre PM2.5 + respiratory hospitalization
- **RR típico**: ~1.01-1.02 por 10 µg/m³ (all-respiratory); 1.023-1.048 (asthma)
- **28 referências** mapeadas na evidence matrix
- **3 gaps P0**: (1) ninguém traçou propagação de não-determinismo pelo pipeline completo; (2) zero estudos em PM2.5/saúde respiratória; (3) nenhum framework de proveniência para evidence synthesis
- **LLM screening accuracy**: 82-98% na literatura (varia por modelo/prompt)
- **LLM extraction accuracy**: 80-96% (Claude-3.5 lidera com 96.2%)
- **Non-determinism**: até 15% variação em settings "determinísticos" (Atil 2024)

---

## Tese (v0.2)

> "Despite growing adoption of LLMs in environmental health evidence synthesis, no study has quantified how API-level non-determinism propagates through the full pipeline — from abstract screening through data extraction to meta-analytic pooling. This study demonstrates that identical LLM configurations produce variable screening decisions and extracted effect sizes, leading to materially different meta-analytic conclusions, and proposes a lightweight provenance framework to detect and mitigate this instability."

---

## Research Questions

| RQ | Questão | Métricas |
|----|---------|----------|
| RQ1 | Triagem varia entre runs idênticos? | flip_rate, Cohen's kappa run-to-run, F1 vs gold |
| RQ2 | Extração numérica (RR/CI) varia materialmente? | EMR, absolute_error_RR, absolute_error_CI |
| RQ3 | Variação altera efeito combinado? | pooled_effect variation, CI_crossing_null, I2 variation |
| RQ4 | Protocolo de proveniência reduz variação? | cost vs stability, stability vs accuracy |

---

## Próximos Passos (em ordem)

1. ~~Finalizar Fase 2 — Methods Specification~~ DONE
2. **[NEXT] Construir corpus de 500 abstracts** — Query PubMed API, exportar ~600, labeling humano, selecionar 500 (100/100/300)
3. **Implementar pipeline** — Runners de screening e extração (reutilizar JAIR runners)
4. **Executar experimentos** — 30 runs × 3 modelos × 2 stages (~58,500 LLM calls)
5. **Meta-análise** — DerSimonian-Laird random effects por run, variação do efeito combinado
6. **Mitigation comparison** — Baseline vs guardrails vs dual-pass vs HITL
7. **Escrever manuscrito** — Methods → Results → Discussion (target: Research Synthesis Methods)
8. **Submeter** — Research Synthesis Methods (A) | J Clin Epidemiol (B) | npj Dig Med (C)

---

## Relação com Paper JAIR

Este paper **estende** o protocolo de proveniência do JAIR para um domínio aplicado:

| Aspecto | JAIR (paper-2026-001) | Este paper (paper-2026-002) |
|---------|----------------------|----------------------------|
| Foco | Diagnóstico geral de não-determinismo | Impacto em evidence synthesis real |
| Domínio | Genérico (sumarização, multi-turn, RAG) | Saúde ambiental (PM2.5 + respiratório) |
| Pipeline | Prompt → output | Screening → extração → meta-análise |
| Framework | Proveniência genérica | Proveniência + guardrails + HITL |
| Modelos | 8 (3 local + 5 API) | 3 (1 local + 2 API) |
| Repo | `genai-reproducibility-protocol` | `llm-evidence-synthesis-reproducibility` |

---

## Arquivos-Chave

```
docs/project_charter/charter-v1.yaml    ← Charter completo
docs/decisions/decision-log.md          ← Todas as decisões
configs/experiment.yaml                 ← Config do experimento
configs/prompts/screening.txt           ← Prompt de triagem
configs/prompts/extraction.txt          ← Prompt de extração
data/literature/paper-2026-002/         ← Literature review completa
data/methods/paper-2026-002/            ← Desenho metodológico
PROJECT_LOG.md                          ← ESTE ARQUIVO
```

---

*Última atualização: 2026-02-11 — Sessão 1*
