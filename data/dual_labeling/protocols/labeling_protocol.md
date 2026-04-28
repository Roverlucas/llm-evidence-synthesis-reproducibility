# Protocolo de Dual-Labeling — Estudo de Reprodutibilidade LLM

**Versão:** 1.1 (atualizada com extraction task)
**Data:** 2026-04-25
**Corpus:** 100 abstracts (subset estratificado de 500)
**Tempo estimado total:** ~5.5 horas
- **Stage A (screening):** 100 abstracts × ~2-3 min = ~3.5h
- **Stage B (extraction):** 25 INCLUDE abstracts × ~5 min = ~2h
**Princípios:** dual-independent (cegados um ao outro) + resolução de discordância

---

## 1. Contexto do estudo

Estamos medindo a **reprodutibilidade de LLMs** (Large Language Models) aplicados a triagem
de abstracts e extração de dados em revisões sistemáticas de epidemiologia ambiental
(PM2.5 e hospitalizações respiratórias). Este labeling gera o **gold standard humano**
usado para validar se os LLMs acertam a decisão correta.

**Sua tarefa:** para cada abstract, decidir se ele deve ser **INCLUÍDO** (estudo elegível para
meta-análise de PM2.5 × hospitalização respiratória) ou **EXCLUÍDO**, com confiança e rationale.

Você **NÃO vê** as decisões do outro labeler até o final. Discordâncias serão resolvidas em reunião
curta de consenso.

---

## 2. Critérios de inclusão (TODOS os 6 devem ser atendidos)

| # | Critério | Como verificar |
|---|----------|----------------|
| 1 | **Estudo original** | Não é review, meta-análise, editorial, comentário, carta |
| 2 | **Exposição: PM2.5** | Mede particulate matter fino (PM2.5, ≤2.5 µm). Estudos de PM10-only = exclui |
| 3 | **Outcome: hospitalização respiratória** | Hospital admission ou ED visit por causa respiratória. Mortalidade-only = exclui |
| 4 | **Design: time-series ou equivalente** | Time-series, case-crossover, ecológico. Cohort/cross-sectional isolado = UNCERTAIN |
| 5 | **Efeito quantitativo** | Reporta RR, OR, HR (ou equivalente) **com IC 95%** |
| 6 | **Idioma: inglês** | Publicado em inglês |

## 3. Critérios de exclusão (QUALQUER um dispara exclusão)

- Reviews, meta-análises, editoriais, comentários, cartas
- Estudos animais ou in-vitro
- PM10-only (sem análise separada de PM2.5)
- Mortalidade apenas (sem hospitalização/ED)
- Sem estimativa de efeito quantitativa extraível do abstract

## 4. Regras de decisão

| Cenário | Decisão |
|---------|---------|
| Atende aos 6 critérios de inclusão | **INCLUDE** |
| Falha claramente em ≥2 critérios | **EXCLUDE** |
| Borderline em 1 critério | **UNCERTAIN** |
| PM2.5 + respiratório mas cohort (não time-series) | **UNCERTAIN** |
| PM2.5 + respiratório mas ED visits pouco claros | **UNCERTAIN** |
| Multi-poluentes incluindo PM2.5 | **INCLUDE** (se PM2.5 reportado separadamente) |
| PM2.5 + respiratório + mortalidade + hospitalização | **INCLUDE** |

## 5. Escala de confiança

- **HIGH (0.8-1.0):** match ou mismatch claro
- **MEDIUM (0.5-0.79):** provável mas com alguma ambiguidade
- **LOW (0.0-0.49):** genuinamente incerto

---

## 6. Como labelar (Rayyan ou Google Sheets)

### Opção A — Rayyan (recomendada)

1. Acesse https://rayyan.ai e crie conta grátis
2. O labeler 1 (Lucas) cria o projeto e convida o labeler 2
3. Importar arquivo: `subset_100_rayyan.csv`
4. Em "Settings → Blind mode": **ativar** (essencial para independência)
5. Para cada abstract: clicar **Include** / **Exclude** / **Maybe (UNCERTAIN)**
6. Adicionar rationale em "Reason" quando for EXCLUDE ou UNCERTAIN
7. Exportar labels ao final (CSV)

### Opção B — Google Sheets (fallback)

1. Abrir o arquivo correspondente: `subset_100_labeler1.csv` (Lucas) ou `subset_100_labeler2.csv` (colega)
2. Importar em Google Sheets (File → Import → Upload)
3. Preencher as colunas **sem ver a planilha do outro labeler**:
   - `{labeler}_decision`: INCLUDE / EXCLUDE / UNCERTAIN
   - `{labeler}_confidence`: HIGH / MEDIUM / LOW
   - `{labeler}_rationale`: 1-2 frases (qual critério decidiu)
   - `{labeler}_criteria_failed`: números dos critérios que falharam (p.ex. "2,3" = PM2.5 e outcome)
4. Salvar como CSV e enviar ao final

---

## 7. Exemplos resolvidos (calibração rápida)

### Exemplo 1 — INCLUDE claro
> "We analyzed the association between PM2.5 exposure and hospital admissions for respiratory diseases in Seoul, Korea, using a time-series design from 2016 to 2020. Relative risk per 10 µg/m³ increase was 1.023 (95% CI: 1.005-1.042)."

**Decisão:** INCLUDE | **Confiança:** HIGH | **Rationale:** atende 6 critérios

### Exemplo 2 — EXCLUDE claro
> "This systematic review summarizes evidence on air pollution and respiratory outcomes across 45 cohort studies..."

**Decisão:** EXCLUDE | **Confiança:** HIGH | **Rationale:** systematic review, não estudo original (critério 1 falha) | **criteria_failed:** 1

### Exemplo 3 — UNCERTAIN
> "A prospective cohort of 2,500 COPD patients followed from 2015-2020 assessed long-term PM2.5 exposure and respiratory decline. Annual PM2.5 averages were associated with FEV1 decline."

**Decisão:** UNCERTAIN | **Confiança:** MEDIUM | **Rationale:** PM2.5 + respiratório ✓ mas cohort design (critério 4 borderline) e outcome não é hospitalização

### Exemplo 4 — EXCLUDE por exposição errada
> "Daily PM10 concentrations and emergency department visits for asthma in Mexico City, 2018-2020. Case-crossover design. OR per 10 µg/m³ PM10 = 1.015 (95% CI: 1.001-1.029)."

**Decisão:** EXCLUDE | **Confiança:** HIGH | **Rationale:** PM10-only, sem PM2.5 | **criteria_failed:** 2

---

## 8. Cronograma sugerido

| Atividade | Duração |
|-----------|---------|
| Ler protocolo + exemplos | 20 min |
| Calibração: 5 abstracts juntos (discussão) | 30 min |
| Labeling independente 100 abstracts | 3-4 h (pode parcelar em sessões) |
| Revisão de discordâncias | 30 min |

---

## 9. Stage B — Extraction Task (apenas INCLUDE items, 25 abstracts)

Para os 25 abstracts classificados como **INCLUDE** no Stage A, fazer também extração quantitativa.

### Arquivos
- `extraction_25_labeler1.csv` (Lucas)
- `extraction_25_labeler2.csv` (colega)

### Campos a extrair (do abstract)
| Campo | Exemplo | Regra |
|-------|---------|-------|
| effect_measure | RR / OR / HR / IRR | Tipo declarado no abstract |
| effect_estimate | 1.023 | Estimativa pontual |
| ci_lower | 1.005 | Limite inferior do IC95% |
| ci_upper | 1.042 | Limite superior do IC95% |
| lag | 0-1 | Lag do exposure-outcome (em dias) |
| exposure_increment | per 10 µg/m³ | Incremento de exposure |
| outcome_specific | all_respiratory | Categoria de outcome respiratório |
| study_design | time_series | Design declarado |
| study_location | "São Paulo, Brazil" | Cidade(s)/país |
| population | general | Categoria populacional |
| n_estimates_in_abstract | 3 | Quantos estimates distintos no abstract (mesmo se você só extrai 1 primário) |
| notes | "ED visits also reported" | Observações livres |

### Regras de seleção (quando há múltiplos estimates)

1. **Prefer all-respiratory** sobre condições específicas (asthma, COPD)
2. **Prefer single-pollutant model** sobre multi-pollutant
3. **Prefer lag 0-1** se múltiplos lags reportados sem "best designation"
4. **Convert para per 10 µg/m³** se diferente increment usado:
   - Exemplo: RR=1.005 per 1 µg/m³ → RR ≈ 1.005^10 = 1.051 per 10 µg/m³
5. **Se reporta % change**, converter: RR = 1 + (%change / 100)
6. **Se múltiplas estimates igualmente válidas**: escolher a primeira reportada

### Threshold de discordância

- effect_estimate: Δ > 0.005 → discordância
- CI bounds: Δ > 0.01 → discordância
- Categorical fields (effect_measure, outcome_specific, study_design): qualquer diferença → discordância

## 10. Resolução de discordâncias

Após ambos labelers terminarem (Stage A + B):

1. Lucas roda os scripts:
   - `scripts/dual_labeling/compute_kappa.py` → gera κ + discordâncias do screening
   - `scripts/dual_labeling/compute_extraction_agreement.py` → gera agreement + discordâncias da extraction (a criar)
2. Reunião curta (~30-45 min) para revisar casos onde discordamos
3. Decisão final por **consenso** (se não houver, Profa. Yara é tie-breaker)
4. Gold standards finais salvos em:
   - `data/dual_labeling/gold_subset_100_final.json` (screening)
   - `data/dual_labeling/extraction_gold_25_final.json` (extraction)

---

## 10. Como a sua contribuição será creditada

- **Acknowledgment** obrigatório na seção "Funding and Acknowledgments" do manuscrito
- **Co-autoria** negociável caso queira contribuir em outras partes (redação, revisão de resultados)
- Seu nome + ORCID aparece no repositório GitHub como contributor

---

## 11. Dúvidas

Contato direto: Lucas Rover
- Email: lucasrover@alunos.utfpr.edu.br
- Tel: +55 (48) 9 9974-8298

Dúvidas técnicas sobre o critério: discutir ANTES de labelar para não contaminar
independência.

---

*Protocolo baseado em:*
- *Cochrane Handbook for Systematic Reviews §4.6.6 (double screening)*
- *McHugh ML (2012) "Interrater reliability: the kappa statistic" Biochem Med*
- *PRISMA-S 2021*
