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
| **Fase 3a: Corpus** | DONE | — | 2026-02-11 |
| **Fase 3b: Pipeline** | DONE | — | 2026-02-11 |
| Fase 3c: Execução (120 runs × 6 stacks) | DONE | — | 2026-05-11 |
| Fase 4: Escrita | DONE | — | 2026-05-11 |
| Fase 4b: Blindagem estatística (P1/P2) | DONE | — | 2026-05-11 |
| Fase 4c: Validação dual-humana — Stage A | DONE | κ=0.529 (abaixo do alvo, reportado) | 2026-07-29 |
| Fase 4d: Validação dual-humana — Stage B | IN PROGRESS | bloqueado nas labelers | — |
| Fase 5: Submissão | PENDING | 4 `\pending` + ações do Lucas | — |

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

### Sessão 2 — 2026-02-11

**Agentes ativados:** @technical-executor

**Entregáveis produzidos:**

4. **Fase 3a — Corpus (COMPLETO)**
   - `src/utils/pubmed_fetch.py` — Script PubMed E-utilities (esearch + efetch via urllib)
   - `src/utils/pubmed_fetch_exclude.py` — Busca de candidatos a exclusão (PM10, mortality, reviews, cardiovascular)
   - `src/utils/corpus_builder.py` — Classificador heurístico + seleção de 500 abstracts
   - `src/utils/gold_standard.py` — Infraestrutura de labeling (dual-human protocol)
   - `data/corpus/raw/pubmed_broad.json` — 573 artigos (broad query)
   - `data/corpus/raw/pubmed_design.json` — 222 artigos (design-filtered)
   - `data/corpus/raw/pubmed_exclude_candidates.json` — 475 candidatos a exclusão
   - `data/corpus/corpus_500.json` — **CORPUS FINAL: 500 abstracts (100/100/300)**
   - `data/gold_standard/screening_labels.json` — Labels de triagem (200 auto + 300 para revisão)
   - `data/gold_standard/extraction_labels.json` — Templates de extração (100 includes)
   - `data/gold_standard/labeling_guide.md` — Guia para anotadores humanos
   - `data/gold_standard/corpus_stats.json` — Estatísticas do corpus
   - `tests/test_corpus.py` — 18 testes de integridade (18/18 passing)
   - Corpus stats: 500 abstracts, 148 journals, years 1994-2026, mean abstract ~1873 chars
   - PubMed results: 636 (broad) + 222 (design) + 475 (exclude) = 1,021 unique → 500 selected

### Sessão 3 — 2026-02-11

**Agentes ativados:** @technical-executor

**Entregáveis produzidos:**

5. **Fase 3b — Pipeline de Screening & Extração (COMPLETO)**
   - `src/models/ollama_runner.py` — Runner LLaMA 3 8B via Ollama (urllib)
   - `src/models/claude_runner.py` — Runner Claude Sonnet 4.5 via Anthropic API
   - `src/models/gemini_runner.py` — Runner Gemini 2.5 Pro via Google AI API
   - `src/provenance/hasher.py` — SHA-256 hashing + run cards + provenance records
   - `src/screening/runner.py` — Pipeline de triagem (Stage A, 500 abstracts)
   - `src/extraction/runner.py` — Pipeline de extração (Stage B, 100 incluídos)
   - `src/utils/env_loader.py` — Loader de .env para API keys
   - `run_experiment.py` — Orquestrador completo (30 runs × 3 modelos × 2 stages)
   - `tests/test_pipeline.py` — 25 testes de pipeline (43/43 total passando)
   - Dry-run validado: Claude screening 3/3 successful + extraction 2/2 successful
   - Run 1 do Claude screening em execução (dados experimentais reais)
   - API keys configuradas: Anthropic + OpenAI + DeepSeek + Perplexity (Gemini pendente)

---

### Sessão 2026-07-29 — Fechamento do Stage A e correções de integridade

**Marco:** a validação dual-humana Stage A fechou. Isabelle (labeler1) entregou os
100/100 restantes; Luiza (labeler2) havia entregue em 2026-07-15.

**Resultado:** κ de Cohen = **0.529** (95% CI [0.383, 0.674]), binário 0.556
[0.400, 0.712], concordância bruta 75%, 25 discordâncias. **Abaixo do alvo Cochrane
de 0.80** — reportado como medido, sem revisar o alvo, exatamente como a contingência
pré-registrada em `fgn3e` determinava.

**Diagnóstico:** a discordância é direcional (McNemar exato p=2.2e-4; Stuart-Maxwell
χ²(2)=15.4, p=4.6e-4), não ruído. 19 das 25 discordâncias correm na mesma direção e
17 delas dependem de um único critério ambíguo (o 5). Nenhuma labeler violou o
protocolo — o protocolo estava incompleto. Emendado para v1.2.

**Descoberta importante sobre o OSF:** existem DOIS objetos, e confundi-los gerou um
falso alarme de integridade. `vr934` é o *projeto*; `fgn3e` é a *registration* do
protocolo de labeling, congelada em 2026-05-12, dois meses antes de qualquer label
chegar. O placeholder `YYYYY` que ficou órfão no `CITATIONS.md` era o DOI dela. A
registration pende do componente `8z6fy` — consultar `/v2/nodes/8z6fy/registrations/`,
não o endpoint do projeto raiz, que retorna zero e engana. O manuscrito estava
**subdeclarando**: dizia "not formally pre-registered" sobre uma validação que tem
DOI próprio.

**Defeitos de integridade corrigidos no manuscrito:**
1. `supplementary.tex` afirmava que os 200 abstracts "clear" foram rotulados por dois
   humanos com terceiro revisor — contradizia o `main.tex` (regra automatizada).
   Nenhum humano rotulou aqueles 200.
2. "rule precision = 100%" não sobrevive à validação: dos 25 abstracts que a regra
   chamou de claramente incluíveis, as raters endossaram 13 e 21. Trocado por limite
   de regra de três (~6%).
3. κ≥0.80 vinha sendo usado para comparar com EMR/Fleiss inter-run — construtos
   diferentes (autoconsistência de um rater vs concordância entre dois).
4. Cover letter alegava "pre-registered post-revision analyses (commits as
   cryptographic timestamps)". Commits git não são pré-registro.

**Gold standard é assimetricamente válido:** lado exclude unânime (25/25), lado
include contestado (0.680, κ=0.359). Consequência adotada no manuscrito:
especificidade firme, sensibilidade lida como lower bound.

**Achado metodológico:** a rodada de reconciliação **não produz um segundo κ**.
Condicionar a remedição à discordância prévia empurra qualquer coeficiente
recalculado para cima por construção. Reportado como concordância pós-hoc condicional.
Validar a v1.2 exigiria amostra nova e independente (n≈30-40).

**Tie-breaker:** considerado passar de Y.d.S.T. para L.R. e **revertido no mesmo dia**
(decision-log 18 SUPERSEDED → 22). Fica com a Yara: Lucas construiu o pipeline
pontuado contra este gold standard, então a adjudicação final com coautora que não o
construiu mantém o padrão independente — e zera o desvio de pré-registro.

**Ferramental novo:** `ingest_labeler1_xlsx.py`, `kappa_statistics.py`,
`build_reconciliation_package.py`, `build_gold_standard.py`,
`rebuild_extraction_set.py`, `_ci_heuristic.py`, `check_pending.sh`,
`verify_reported_numbers.py` (+18 testes). Suíte: 108 → 126.

**Estado do manuscrito:** 33pp + 23pp, compila sem erro, 0 referências indefinidas,
31 afirmações numéricas conferidas contra a fonte automaticamente.

**Commits:** `8e4bd39`, `ca0a3cc`, `a8391a8`, `de038a7`, `8347ae4`, `5f661e6` —
todos em `origin/main`.

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
2. ~~Construir corpus de 500 abstracts~~ DONE (573 broad + 222 design + 475 exclude → 500 selecionados)
3. ~~Implementar pipeline~~ DONE (3 runners + screening + extraction + provenance + orchestrator)
4. ~~Executar experimentos~~ DONE (120 runs × 6 deployment stacks, 36.000 chamadas)
5. ~~Meta-análise~~ DONE (DL + HKSJ, simulação de literatura pequena)
6. ~~Escrever manuscrito~~ DONE (33pp + 23pp suplementar, compila limpo)
7. ~~Validação dual-humana Stage A~~ DONE (κ=0.529, abaixo do alvo, reportado como medido)

**Bloqueado nas labelers:**
8. **[NEXT]** Rodada de recalibração v1.2 — 25 itens × 2 raters (~35 min cada). Pacote
   pronto em `~/Downloads/recalibracao_v12_2026-07-29/`, ainda não enviado.
9. Fechar gold standard (`build_gold_standard.py` recusa gravar com item não resolvido)
10. Reconstruir Stage B a partir do gold humano (`rebuild_extraction_set.py`)
11. Extração dual-humana (~2h por rater) + concordância por campo

**Bloqueado no Lucas (independente das labelers):**
12. Author block 2 → 5: sobrenome da Isabelle, ORCIDs e afiliações dos três novos
13. Postar sub-registration update no componente OSF `8z6fy` — item (d) da contingência
    registrada; texto pronto em `docs/osf_subregistration_update.md`
14. Corrigir a descrição pública do projeto `vr934` — hoje mostra o resumo do
    pré-registro em vez da visão geral do estudo
15. Confirmar se o pre-submission inquiry da RSM foi enviado
16. Reservar DOI do Zenodo e inserir no Data Availability antes de publicar o depósito
17. Decidir sobre a amostra fresca (n≈30-40) para validar a v1.2 — rodar, ou declarar
    nas limitações que a emenda não foi validada. Se rodar, enviar junto com a
    recalibração para não gastar duas rodadas de espera humana.

**Opcional (eleva a defensibilidade):**
18. Forest plots a partir de `random_effects_per_run.json` e `small_literature_sim.json`
19. Effect size pareado para os 21 contrastes — **não** Cohen's h, que assume proporções
    independentes e reintroduziria o erro de pareamento que o McNemar veio corrigir
20. Checklists de reporting (código/software + ML)

21. **Submeter** — Research Synthesis Methods (A) | J Clin Epidemiol (B) | npj Dig Med (C)

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
data/corpus/corpus_500.json             ← CORPUS FINAL (500 abstracts)
data/gold_standard/                     ← Labels + templates + guia
src/utils/pubmed_fetch.py               ← Fetcher PubMed E-utilities
src/utils/corpus_builder.py             ← Classificador + seleção
tests/test_corpus.py                    ← 18 testes de integridade
PROJECT_LOG.md                          ← ESTE ARQUIVO
```

---

## Números do Corpus

- **1,021 artigos únicos** recuperados do PubMed (3 queries)
- **573** broad query (PM2.5 + respiratory + hospitalization + time-series)
- **222** design-filtered query (mais restrita)
- **475** exclude candidates (PM10-only, mortality, reviews, cardiovascular)
- **500 selecionados**: 100 include (score 5/5) + 100 exclude (razões claras) + 300 ambiguous
- **148 journals** representados
- **Years**: 1994–2026
- **Mean abstract length**: ~1,873 chars
- **18/18 testes** de integridade passando

---

*Última atualização: 2026-07-29 — Stage A dual-humano fechado (κ=0.529), correções de integridade, push para origin/main*
