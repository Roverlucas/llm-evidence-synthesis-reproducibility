# Protocolo de Dual-Labeling — Estudo de Reprodutibilidade LLM

**Versão:** 1.2 (desambiguação do critério 5 + regra de falha em critério único)
**Data:** 2026-07-29
**Corpus:** 100 abstracts (subset estratificado de 500)
**Tempo estimado total:** ~5.5 horas
- **Stage A (screening):** 100 abstracts × ~2-3 min = ~3.5h
- **Stage B (extraction):** abstracts INCLUDE do gold standard × ~5 min = ~2h
**Princípios:** dual-independent (cegados um ao outro) + resolução de discordância

---

## 0. Changelog e nota de transparência

### v1.2 (2026-07-29) — escrita APÓS o cálculo do κ inicial

A rodada Stage A independente foi concluída em 2026-07-29 com os dois labelers
(labeler1 e labeler2, 100/100 cada). O κ de Cohen pré-especificado resultou em
**0.529 (3 classes) / 0.556 (binário), concordância bruta 75%** — abaixo do alvo
Cochrane de 0.80.

A análise das 25 discordâncias mostrou que **19 são assimétricas** (labeler1
EXCLUDE / labeler2 INCLUDE) e **17 dessas 19 recaem sobre o critério 5**. As duas
labelers aplicaram leituras divergentes mas ambas defensáveis do texto v1.1:

- §2 dizia "Reporta RR, OR, HR (ou equivalente) **com IC 95%**" — compatível com
  aceitar a *menção* de que o estudo reporta o efeito;
- §3 dizia "sem estimativa de efeito quantitativa **extraível do abstract**" —
  compatível com exigir o *valor numérico*.

Além disso, a tabela de regras da §4 cobria "falha em ≥2 critérios" e "borderline
em 1 critério", mas **não cobria falha clara em exatamente 1 critério** — que é
precisamente o caso desses 17 abstracts. Nenhuma das labelers violou o protocolo;
o protocolo é que estava incompleto.

A v1.2 desambigua os dois pontos. **O κ de 0.529 permanece como o resultado de
concordância do estudo e será reportado no manuscrito como tal**, independentemente
do que a reconciliação produzir.

⚠️ **A rodada de reconciliação NÃO produz um segundo κ e não pode ser reportada
como tal.** Como a remedição é condicionada à discordância prévia, recalcular um
coeficiente sobre o corpus inteiro depois de rerrotular apenas os 25 itens
discordantes empurra o valor para cima mecanicamente — com taxa de resolução
suficientemente alta, cruzaria o limiar Cochrane **por construção**, sem nenhum
conteúdo evidencial. O resultado é reportado como *concordância pós-hoc de
reconciliação, condicional aos itens inicialmente discordantes*.

Demonstrar que a v1.2 corrige de fato a ambiguidade exigiria uma **amostra nova e
independente** (n≈30-40 basta para uma checagem direcional), não a rerrotulagem dos
mesmos itens. Fica registrado como próximo passo, não como resultado.

### v1.1 (2026-04-25)
Adição da extraction task (Stage B).

---

## 1. Contexto do estudo

Estamos medindo a **reprodutibilidade de LLMs** (Large Language Models) aplicados a triagem
de abstracts e extração de dados em revisões sistemáticas de epidemiologia ambiental
(PM2.5 e hospitalizações respiratórias). Este labeling gera o **gold standard humano**
usado para validar se os LLMs acertam a decisão correta.

**Sua tarefa:** para cada abstract, decidir se ele deve ser **INCLUÍDO** (estudo elegível para
meta-análise de PM2.5 × hospitalização respiratória) ou **EXCLUÍDO**, com confiança e rationale.

Você **NÃO vê** as decisões do outro labeler até o final — o cegamento mútuo é o que
torna a concordância entre vocês uma medida de verdade, e não de convergência social.
Discordâncias serão resolvidas em reunião curta de consenso; o que não fechar em
consenso vai para a Profa. Yara Tadano como tie-breaker (§10).

---

## 2. Critérios de inclusão (TODOS os 6 devem ser atendidos)

| # | Critério | Como verificar |
|---|----------|----------------|
| 1 | **Estudo original** | Não é review, meta-análise, editorial, comentário, carta |
| 2 | **Exposição: PM2.5** | Mede particulate matter fino (PM2.5, ≤2.5 µm). Estudos de PM10-only = exclui |
| 3 | **Outcome: hospitalização respiratória** | Hospital admission ou ED visit por causa respiratória. Mortalidade-only = exclui |
| 4 | **Design: time-series ou equivalente** | Time-series, case-crossover, ecológico. Cohort/cross-sectional isolado = UNCERTAIN |
| 5 | **Efeito quantitativo** | Ver §2.1 — regra desambiguada na v1.2 |
| 6 | **Idioma: inglês** | Publicado em inglês |

### 2.1 Critério 5 desambiguado (v1.2)

O critério 5 tem **dois níveis**, e a decisão depende de qual deles o abstract atinge:

| Nível | O que o abstract traz | Critério 5 | Decisão que dispara |
|-------|----------------------|-----------|--------------------|
| **5a** | Estimativa pontual numérica (RR, OR, HR, IRR ou % change) **e** IC 95% numérico | **ATENDIDO** | segue para os demais critérios |
| **5b** | Menciona que o efeito foi estimado, mas **sem os valores** (p.ex. "significantly associated", "reported relative risks", "large confidence intervals") | **NÃO atendido por informação insuficiente** | **UNCERTAIN** (não EXCLUDE) |
| **5c** | Nenhuma estimativa de efeito, nem menção — puramente descritivo/qualitativo | **NÃO atendido** | **EXCLUDE** se for a única falha (§4 explica por que difere de 5b) |

**Razão da regra 5b.** A triagem é feita apenas sobre o abstract. Um estudo que
declara ter estimado o efeito quase certamente reporta os valores no texto
completo — o abstract é que é omisso, não o estudo. Rotular esses casos como
EXCLUDE afirma algo sobre o *estudo* que a evidência disponível não sustenta;
rotular como INCLUDE afirma que o critério foi verificado quando não foi.
UNCERTAIN é a única categoria que descreve honestamente o estado da informação.

Consequência prática para o Stage B: como a extração exige `effect_estimate`,
`ci_lower` e `ci_upper` retirados do abstract, **apenas itens 5a entram no
conjunto de extração**.

## 3. Critérios de exclusão (QUALQUER um dispara exclusão)

- Reviews, meta-análises, editoriais, comentários, cartas
- Estudos animais ou in-vitro
- PM10-only (sem análise separada de PM2.5)
- Mortalidade apenas (sem hospitalização/ED)
- Nenhuma estimativa de efeito nem menção a ela no abstract (caso 5c; para o caso
  5b — menção sem valores — ver §2.1, que manda UNCERTAIN)

## 4. Regras de decisão

Os critérios não têm todos o mesmo peso. Os **estruturais** (1, 2, 3, 6) são
discriminadores absolutos: se o abstract falha em qualquer um deles, a
inelegibilidade é certa e verificável pelo próprio abstract. Os **condicionais**
(4, 5) dependem de informação que o abstract pode simplesmente ter omitido — e o
que separa "omitido" de "ausente" é justamente a distinção 5b/5c da §2.1.

A tabela abaixo cobre **todas** as combinações possíveis. Se você encontrar um caso
que não se encaixa em nenhuma linha, **não improvise**: registre UNCERTAIN com
rationale explicando o impasse e avise o Lucas. Foi um caso não coberto que produziu
25% de discordância na primeira rodada; a tabela não voltar a ter buracos é mais
importante do que qualquer decisão individual.

| Cenário | Decisão |
|---------|---------|
| Atende aos 6 critérios de inclusão | **INCLUDE** |
| Falha clara em **≥1 critério estrutural** (1, 2, 3 ou 6) | **EXCLUDE** |
| Falha em **≥2 critérios**, qualquer combinação | **EXCLUDE** |
| Falha **apenas** no critério 4 (design não é time-series/case-crossover/ecológico) | **UNCERTAIN** |
| Falha **apenas** no critério 5, caso **5b** (menção ao efeito, sem os valores) | **UNCERTAIN** |
| Falha **apenas** no critério 5, caso **5c** (nenhuma estimativa nem menção a ela) | **EXCLUDE** |
| Borderline em 1 critério | **UNCERTAIN** |
| PM2.5 + respiratório mas cohort (não time-series) | **UNCERTAIN** |
| PM2.5 + respiratório mas ED visits pouco claros | **UNCERTAIN** |
| Multi-poluentes incluindo PM2.5 | **INCLUDE** (se PM2.5 reportado separadamente) |
| PM2.5 + respiratório + mortalidade + hospitalização | **INCLUDE** |

**Por que 5b e 5c terminam em decisões opostas**, ambos sendo falha do mesmo
critério condicional: em 5b o abstract *afirma* que o efeito foi estimado, então o
estudo tem o número e o abstract é que o omitiu — não há base para afirmar nada
sobre a elegibilidade do estudo, e UNCERTAIN é a descrição honesta. Em 5c o abstract
não menciona estimativa alguma; a ausência total é evidência razoável de que o estudo
não produziu estimativa extraível, e aí EXCLUDE é uma inferência sustentada. A
diferença não é o critério que falhou, é **quanta informação o abstract oferece sobre
a falha**.

> Regra de desempate interna: quando duas linhas se aplicam, **EXCLUDE tem
> precedência sobre UNCERTAIN, e UNCERTAIN sobre INCLUDE**. Exemplo: falha no
> critério 2 (estrutural) + caso 5b → EXCLUDE.

## 5. Escala de confiança

- **HIGH (0.8-1.0):** match ou mismatch claro
- **MEDIUM (0.5-0.79):** provável mas com alguma ambiguidade
- **LOW (0.0-0.49):** genuinamente incerto

---

## 6. Como labelar (Rayyan ou Google Sheets)

### Opção A — Rayyan (recomendada)

1. Acesse https://rayyan.ai e crie conta grátis
2. Lucas (coordenador, não-labeler) cria o projeto e convida os dois labelers
3. Importar arquivo: `subset_100_rayyan.csv`
4. Em "Settings → Blind mode": **ativar** (essencial para independência)
5. Para cada abstract: clicar **Include** / **Exclude** / **Maybe (UNCERTAIN)**
6. Adicionar rationale em "Reason" quando for EXCLUDE ou UNCERTAIN
7. Exportar labels ao final (CSV)

### Opção B — Google Sheets (fallback)

1. Abrir o arquivo correspondente: `subset_100_labeler1.csv` (Isabelle) ou `subset_100_labeler2.csv` (Luiza)
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

### Exemplo 3 — UNCERTAIN por falha apenas no critério 4 (design)
> "A prospective cohort of 2,500 patients was followed from 2015-2020 to assess long-term PM2.5 exposure and hospital admissions for respiratory disease. Admission rates rose with annual PM2.5 averages (RR 1.04, 95% CI: 1.01-1.07)."

**Decisão:** UNCERTAIN | **Confiança:** MEDIUM | **Rationale:** PM2.5 ✓, hospitalização respiratória ✓, efeito com IC ✓ (nível 5a), mas design é cohort, não time-series/case-crossover — falha **só** no critério 4 | **criteria_failed:** 4

> ⚠️ Atenção à diferença: se esse mesmo abstract também não tivesse hospitalização
> (p.ex. só declínio de FEV1), seriam **dois** critérios falhando, um deles estrutural
> (o 3) — e a §4 manda **EXCLUDE**, não UNCERTAIN. UNCERTAIN é para falha isolada em
> critério condicional.

### Exemplo 4 — EXCLUDE por exposição errada
> "Daily PM10 concentrations and emergency department visits for asthma in Mexico City, 2018-2020. Case-crossover design. OR per 10 µg/m³ PM10 = 1.015 (95% CI: 1.001-1.029)."

**Decisão:** EXCLUDE | **Confiança:** HIGH | **Rationale:** PM10-only, sem PM2.5 (critério 2, estrutural) | **criteria_failed:** 2

### Exemplo 5 — UNCERTAIN pelo caso 5b (a novidade da v1.2)
> "We examined daily PM2.5 concentrations and hospital admissions for respiratory causes in three metropolitan areas using a time-series design. PM2.5 was significantly associated with increased admissions, with wide confidence intervals in the smaller city."

**Decisão:** UNCERTAIN | **Confiança:** MEDIUM | **Rationale:** critérios 1-4 e 6 ✓, mas o abstract afirma que houve estimativa e IC sem trazer os valores — caso **5b**, informação insuficiente | **criteria_failed:** 5

Este é o padrão que gerou 17 das 25 discordâncias da primeira rodada. Não é EXCLUDE:
o estudo declara ter estimado o efeito, então o número existe no texto completo. Não é
INCLUDE: o critério não foi verificado. É UNCERTAIN.

### Exemplo 6 — EXCLUDE pelo caso 5c
> "This paper describes the design and deployment of a low-cost PM2.5 sensor network in a metropolitan area and discusses its potential applications for respiratory health surveillance. Sensor performance and calibration procedures are reported."

**Decisão:** EXCLUDE | **Confiança:** HIGH | **Rationale:** não há estimativa de efeito nem menção a uma — caso **5c**; além disso não é estudo epidemiológico de associação (critério 1) | **criteria_failed:** 1,5

---

## 8. Cronograma sugerido

Rodada original (Stage A), já concluída:

| Atividade | Duração |
|-----------|---------|
| Ler protocolo + exemplos | 20 min |
| Calibração: 5 abstracts juntos (discussão) | 30 min |
| Labeling independente 100 abstracts | 3-4 h (pode parcelar em sessões) |

Rodada de recalibração v1.2 (atual):

| Atividade | Duração |
|-----------|---------|
| Ler §0, §2.1, §4 e os Exemplos 3, 5 e 6 | 15 min |
| Reavaliar os 25 itens discordantes, independentemente | 30-40 min |
| Reunião de consenso sobre o que restar | 30 min |

---

## 9. Stage B — Extraction Task (apenas INCLUDE do gold standard humano)

Para os abstracts classificados como **INCLUDE no gold standard humano** do Stage A
— e que atinjam o nível **5a** do critério 5 (§2.1) — fazer também extração
quantitativa.

> **Mudança na v1.2.** O conjunto de extração original (`extraction_25_*.csv`) foi
> montado a partir do silver standard gerado por LLM, antes da rotulagem humana.
> Confrontado com o consenso humano, apenas **13 dos 25** sobreviveram. O conjunto
> é reconstruído a partir do gold standard humano por
> `scripts/dual_labeling/rebuild_extraction_set.py`. A divergência 13/25 é
> preservada como resultado — é evidência direta de que a triagem por LLM admite
> material que humanos rejeitam.

### Arquivos
- `extraction_labeler1.csv` (Isabelle)
- `extraction_labeler2.csv` (Luiza)

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

**Atribuição de papéis (atualizada 2026-07-29):** labeler1 = Isabelle, labeler2 =
Luiza Iltchechen, tie-breaker = **Profa. Yara Tadano (Y.d.S.T.)** — o mesmo papel
previsto na v1.1 e registrado no pré-registro OSF `fgn3e`.

Houve uma consideração de transferir o tie-break para Lucas Rover em 2026-07-29; a
decisão foi **revertida no mesmo dia**, e o registro dessa reversão está em
`docs/decisions/decision-log.md` (entradas 18 e 22). O motivo de manter a Yara é
substantivo, não burocrático: Lucas é o primeiro autor e desenvolveu o pipeline cujas
saídas são pontuadas **contra** este gold standard. Deixar a adjudicação final com uma
coautora que não construiu o sistema mantém o padrão de referência independente do
objeto avaliado, e evita um desvio de pré-registro que teria de ser declarado e
defendido sem ganho nenhum em troca.

Mitigações que valem independentemente de quem adjudica: o tie-break é aplicado
**apenas** aos casos de discordância residual, sobre critérios de protocolo já
escritos, e **sem acesso às saídas dos LLMs** durante a decisão. Cada tie-break
registra critério invocado e justificativa em `reconciliation/` — auditável item a
item.

Após ambos labelers terminarem (Stage A + B):

1. Rodar os scripts:
   - `scripts/dual_labeling/compute_kappa.py` → κ + discordâncias do screening
   - `scripts/dual_labeling/compute_extraction_agreement.py` → agreement + discordâncias da extraction
2. **Sessão de recalibração v1.2** (~30 min): as duas labelers leem §0, §2.1 e §4
   revisados e reavaliam **apenas os itens em discordância**, de novo de forma
   independente. Os 75 itens concordantes não são reabertos.
3. Medir a **concordância pós-hoc de reconciliação** sobre os 25 itens (quantos
   convergiram). **Não** rodar `compute_kappa.py` sobre o corpus inteiro
   pós-recalibração: o número resultante não seria um κ interpretável (ver §0).
   O κ de 0.529 continua sendo o resultado de concordância do estudo.
4. Discordâncias que sobreviverem à recalibração vão a **consenso**; sem consenso,
   **tie-break pela Profa. Yara Tadano** com registro do critério invocado.
5. Gold standards finais salvos em:
   - `data/dual_labeling/gold_subset_100_final.json` (screening)
   - `data/dual_labeling/extraction_gold_final.json` (extraction)

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
