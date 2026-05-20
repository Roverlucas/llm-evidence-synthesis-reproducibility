# Quick-Start: Como labelar 100 abstracts (versão "5 minutos")

**Para:** Labeler 2
**Tempo total:** ~4 horas (dá pra parcelar em 2-3 sessões)
**Você não precisa ler nada técnico antes** — este guia tem tudo. Se quiser detalhes, abra `labeling_protocol.md`.

---

## 🎯 O que você vai fazer (em 3 frases)

Você vai olhar **100 resuminhos de artigos científicos** (abstracts), um de cada vez.
Pra cada um, decidir se ele **entra** no nosso estudo, **fica de fora**, ou se você **tá em dúvida**.
A cada decisão, escrever 1 frase curta dizendo por quê.

É só isso. Sem código, sem estatística, sem ler artigo completo.

---

## 🚦 As 3 únicas decisões possíveis

| Caixinha | Quando usar | Exemplo curto |
|----------|-------------|---------------|
| 🟢 **INCLUDE** | O artigo mede **PM2.5** E olha **hospitalização respiratória** E é **estudo original** com **número e intervalo de confiança** | "PM2.5 e admissões hospitalares por asma, RR=1.02 (95% CI: 1.01-1.04)" |
| 🔴 **EXCLUDE** | Falta **claramente** algo da lista (ex: é review, mede só PM10, sem IC, mortalidade só) | "This systematic review of 45 studies..." → review, fora |
| 🟡 **UNCERTAIN** | Tá meio-termo, você tá em dúvida genuína em 1 critério | "Cohort de COPD seguido 5 anos, PM2.5 anual" — design não é bem time-series, fica UNCERTAIN |

> **Regra de ouro:** se você precisa ler 3 vezes pra decidir, **é UNCERTAIN**. Não force.

---

## 📋 A checklist (cole no monitor)

Pra ser **INCLUDE**, o abstract precisa atender aos **6 critérios**:

1. ✅ **Estudo original** — não é review, meta-análise, editorial, carta
2. ✅ **Mede PM2.5** — partículas finas (≤2,5 µm). Só PM10? FORA.
3. ✅ **Outcome: hospitalização respiratória** — admissão hospitalar ou pronto-socorro por causa respiratória (asma, COPD, pneumonia, etc.). Só mortalidade? FORA.
4. ✅ **Design: time-series ou parecido** — time-series, case-crossover, ecológico longitudinal. Cohort/cross-section puro? UNCERTAIN.
5. ✅ **Tem número + IC 95%** — reporta RR/OR/HR/IRR com intervalo de confiança 95%
6. ✅ **Em inglês**

**Falhou em 1 critério claramente → EXCLUDE.**
**Falhou em 1 critério na dúvida → UNCERTAIN.**
**Passou nos 6 → INCLUDE.**

---

## 🔄 O fluxo passo a passo

Veja a figura `flowchart.png` (anexa) — é literalmente isso:

```
Abrir CSV no Google Sheets
        ↓
Ler título + abstract (1 linha do CSV)
        ↓
Fazer as 6 perguntas da checklist
        ↓
Decidir: INCLUDE / EXCLUDE / UNCERTAIN
        ↓
Preencher 4 colunas (decisão, confiança, motivo, critérios que falharam)
        ↓
Próxima linha
```

---

## 📝 As 4 colunas que você preenche

Pra cada linha do CSV, preencha 4 células:

| Coluna | O que colocar | Exemplo |
|--------|---------------|---------|
| `labeler2_decision` | `INCLUDE` ou `EXCLUDE` ou `UNCERTAIN` | `INCLUDE` |
| `labeler2_confidence` | `HIGH` (claro) / `MEDIUM` (provável) / `LOW` (incerto) | `HIGH` |
| `labeler2_rationale` | 1 frase curtinha do porquê | "PM2.5 + hospital admissions, time-series, RR com IC 95%" |
| `labeler2_criteria_failed` | Números dos critérios que falharam (vírgula). Vazio se INCLUDE. | `2,3` (falhou PM2.5 e outcome) |

**Você NÃO precisa preencher** as colunas `labeler1_*` — essas são minhas, ficam vazias na sua planilha.

---

## 🎬 3 exemplos resolvidos (calibração)

### ✅ Exemplo 1 — INCLUDE
> "We analyzed PM2.5 exposure and hospital admissions for respiratory diseases in Seoul using a time-series design from 2016 to 2020. Relative risk per 10 µg/m³ increase was 1.023 (95% CI: 1.005-1.042)."

| Coluna | Resposta |
|--------|----------|
| decision | `INCLUDE` |
| confidence | `HIGH` |
| rationale | "PM2.5, hospital admissions, time-series, RR com IC 95%" |
| criteria_failed | (vazio) |

### ❌ Exemplo 2 — EXCLUDE
> "This systematic review summarizes evidence on air pollution and respiratory outcomes across 45 cohort studies..."

| Coluna | Resposta |
|--------|----------|
| decision | `EXCLUDE` |
| confidence | `HIGH` |
| rationale | "Systematic review, não estudo original" |
| criteria_failed | `1` |

### 🤔 Exemplo 3 — UNCERTAIN
> "A prospective cohort of 2,500 COPD patients followed from 2015-2020 assessed long-term PM2.5 exposure and respiratory decline. Annual PM2.5 averages were associated with FEV1 decline."

| Coluna | Resposta |
|--------|----------|
| decision | `UNCERTAIN` |
| confidence | `MEDIUM` |
| rationale | "PM2.5 + respiratório ok, mas cohort (não time-series) e outcome é FEV1, não hospitalização" |
| criteria_failed | `3,4` |

### ❌ Exemplo 4 — EXCLUDE por exposição errada
> "Daily PM10 concentrations and ED visits for asthma in Mexico City, 2018-2020. Case-crossover. OR per 10 µg/m³ PM10 = 1.015 (95% CI: 1.001-1.029)."

| Coluna | Resposta |
|--------|----------|
| decision | `EXCLUDE` |
| confidence | `HIGH` |
| rationale | "Só PM10, sem PM2.5 separadamente" |
| criteria_failed | `2` |

---

## 💻 Como abrir o arquivo (3 cliques)

### Opção A — Google Sheets (recomendada, 30 segundos)
1. Abra https://sheets.google.com
2. **File → Import → Upload** → escolha `subset_100_labeler2.csv` (anexo)
3. Pronto, começa a preencher

### Opção B — Rayyan (plataforma de revisão sistemática, tem blind mode)
1. Crie conta grátis em https://rayyan.ai
2. Avisa que aceita Rayyan — eu te envio convite pro projeto
3. Você vê os abstracts um por um, clica Include/Exclude/Maybe

### Opção C — Excel/LibreOffice
Igual ao Google Sheets — abrir o CSV, preencher, salvar como CSV de volta.

---

## ⏱️ Cronograma sugerido

| Etapa | Tempo |
|-------|-------|
| Ler este guia + ver fluxograma | 10 min |
| Fazer 5 abstracts juntos numa call comigo (calibração) | 30 min |
| Labelar 100 abstracts no seu ritmo (pode parcelar) | 3-4 h |
| Me devolver o CSV preenchido | — |
| Reunião curta pra discutir discordâncias | 30 min |

**Dica:** faz 25 abstracts por sessão. Em 4 sessões de ~50 min você acaba.

---

## 🔬 Etapa 2 — Extração (só pros 25 INCLUDE)

Depois que ambos terminamos o screening, dos abstracts que **ambos marcamos INCLUDE**, você faz uma 2ª passagem extraindo **números** (mais 2h, ~5 min cada).

Vai ser arquivo separado (`extraction_25_labeler2.csv`) com colunas pra:
- effect_measure (RR/OR/HR)
- effect_estimate (ex: 1.023)
- ci_lower / ci_upper (ex: 1.005 / 1.042)
- lag (ex: 0-1)
- outcome_specific (asthma / COPD / all_respiratory)
- study_design (time_series / case_crossover)
- + 4 campos contextuais

**Não se preocupe agora** — quando chegarmos lá eu te mando guia separado.

---

## 🙋 Dúvidas durante o labeling

**Antes de começar:** marca call de 15-30 min comigo. Eu mostro o paper, calibramos 5 abstracts juntos, esclareço dúvidas. **Essencial.**

**Durante:** se um abstract te confundir, **marca UNCERTAIN** e segue. NÃO me pergunta no meio do labeling — isso quebra a independência (princípio do dual-blind). Anota no rationale e a gente resolve depois na reunião de discordâncias.

**Bug técnico (CSV corrompido, etc.):** me chama no WhatsApp.

---

## ✨ Reconhecimento

- **Acknowledgment** garantido na seção "Funding and Acknowledgments" do manuscrito (Research Synthesis Methods / Cambridge)
- **Co-autoria negociável** se quiser contribuir em outras etapas (revisão de resultados, discussão)
- Seu nome + ORCID no GitHub como contributor + Zenodo deposit

---

## 📦 Anexos deste pacote

1. `quick_start_guide.md` — **este arquivo** (leia primeiro)
2. `flowchart.png` — fluxograma visual do processo de decisão
3. `labeling_protocol.md` — protocolo técnico completo (consulta opcional)
4. `subset_100_labeler2.csv` — planilha pra você preencher (screening)
5. `extraction_25_labeler2.csv` — planilha pra etapa 2 (envio depois)

---

**Contato Lucas Rover**
📧 lucasrover@alunos.utfpr.edu.br
📱 +55 (48) 9 9974-8298
🧑‍🎓 PhD student PPGSAU/UTFPR — orientadora: Profa. Dra. Yara Tadano
🆔 ORCID: 0000-0001-6641-9224
