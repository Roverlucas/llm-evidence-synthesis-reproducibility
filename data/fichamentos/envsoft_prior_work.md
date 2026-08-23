# Fichamentos — trabalho prévio no Environmental Modelling & Software

Lidos em 2026-08-22 para ancorar a submissão ao EMS. Duas entradas em texto integral,
duas bloqueadas por paywall e declaradas como tal.

---

## Yoon, Ashraf, Ruggles & Singh (2026) — EMS 203:107030
**read_depth: full-text** · via preprint arXiv:2511.11821 (9.499 palavras) · doi:10.1016/j.envsoft.2026.107030

**O que é:** avaliação sistemática de 7 modelos open-weight (0,6B–70B) na extração de informação
regulatória de documentos de licenciamento hidrelétrico. 17 campos, 209 segmentos de documento,
7 metodologias de prompting = 49 configurações.

**Achados:** limiar de 14B parâmetros onde validação por raciocínio passa de inviável (F1 < 0,15)
para viável (F1 = 0,64); modelos comerciais ~77% F1; alucinação seletiva por categoria, não uniforme;
recall próximo de 1,000 indica falha de extração, não sucesso.

**Por que importa para nós — literal, §3.8 Experimental setup:**
> "All experiments utilized deterministic generation parameters to ensure reproducibility.
> Temperature was fixed at 0 across all model inferences, **thereby eliminating sampling
> variability and facilitating consistent outputs across multiple experimental runs**."

E logo abaixo:
> "**Each model-method permutation was executed once** on the comprehensive dataset comprising
> 209 document segments."

O estudo **não mede** variabilidade entre execuções; mede acurácia contra gold standard. A premissa
de que temperature=0 torna a repetição redundante é declarada abertamente e não testada. É a
premissa que o nosso artigo mede.

⚠️ **Como citar:** sem depreciar. A escolha é a convenção do campo, e o mérito de tê-la declarado
com clareza é o que permite testá-la. Nosso texto diz explicitamente que a pergunta não é se o
estudo foi bem conduzido.

---

## Schlögl, Waltersdorfer, Regner, Siposova & Brenning (2026) — EMS 200:106962
**read_depth: full-text** · via preprint EGUsphere 2025-5210 (14.441 palavras) · doi:10.1016/j.envsoft.2026.106962

**O que é:** artigo de posição/prática sobre reprodutibilidade em análise de dados geocientíficos.
Distingue três dimensões, com definições próprias: *methodological reproducibility* (repetição
exata do procedimento dados código, dados e ambiente — inclui a computacional), *results
reproducibility* (replicação independente com dados próprios), *inferential reproducibility*
(conclusões qualitativamente similares).

**Por que importa para nós:** o catálogo de barreiras **já nomeia o nosso problema**:
> "non-deterministic model outputs from generative AI and Monte-Carlo simulation models"

e observa que "the increasing adoption of GeoAI, including large language models and spatially
aware AI frameworks, introduces new reproducibility challenges". Nomeia e **não mede** — não é um
estudo desenhado para isso. Nosso trabalho fornece a medição, na dimensão que eles chamam de
methodological reproducibility.

---

## 🔴 Park, Park, Kim & Jin (2026) — EMS 205:107142 — **BLOQUEADO**
**read_depth: title-only** · doi:10.1016/j.envsoft.2026.107142

Sem acesso ao texto. Verificado em 2026-08-22: Unpaywall `is_oa: false / closed`; Semantic Scholar
`isOpenAccess: false`; Europe PMC não registra o DOI; ScienceDirect retorna 403; nenhuma versão
preprint localizada.

**Consequência aplicada ao manuscrito:** a afirmação anterior de que o estudo encontrou que
interfaces estruturadas "entregam menos do que seu desenho sugere", e a alegação de convergência
com o nosso resultado de fixed-slot, **foram removidas**. O título diz "what structured tool
interfaces do and do not provide" e não autoriza inferir a direção do achado. O texto agora cita
apenas a existência da pergunta na revista.

**Antes de submeter:** ler pelo acesso institucional da UTFPR. Se o achado de fato convergir, a
afirmação de convergência é forte e deve voltar — com a evidência.

---

## 🔴 Zhu, Chen, Ren, He, Sun, Zhang, Wen, Yue & Lü (2025) — EMS 186:106323 — **BLOQUEADO**
**read_depth: title-only** · doi:10.1016/j.envsoft.2025.106323

Sem acesso, mesmas verificações e mesmo resultado.

**Consequência aplicada:** a afirmação de que um passo mediado por LLM é algo que tal framework
"não consegue ainda alcançar" foi suavizada para o que o título sustenta — que frameworks desse
tipo foram propostos, e que um componente não-determinístico difere do que eles foram construídos
para avaliar.
