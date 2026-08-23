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

## Park, Park, Kim & Jin (2026) — EMS 205:107142
**read_depth: full-text** · via ScienceDirect com acesso institucional UTFPR, 2026-08-22 (10.406 palavras)

**O que é:** introduz o **Hydro-MCP**, um framework Model Context Protocol que restringe a operação
do SWAT+ mediada por LLM através de schemas de função tipados, validação de faixa de parâmetros,
feedback diagnóstico estruturado e log de trajetória. Ablação de seis níveis na bacia urbana de
Jungnangcheon, mais baselines de referência, um stress test rural em Jiseokcheon e uma tarefa
held-out de corrupção.

**Achados (números do abstract e da §5):**
- Caminho de calibração mais curto: **21,9 ± 5,3 vs 62,0 ± 16,5** avaliações de modelo (p < 0,001,
  Wilcoxon), com performance terminal praticamente inalterada (NSE mensal ≈ 0,893).
- Baseline de busca aleatória exigiu **menos** avaliações porém com NSE terminal levemente inferior —
  ou seja, o ganho é de operação guiada por LLM, não de eficiência de amostragem.
- Bacia rural: configuração completa atinge conclusão operacional em 10/10 execuções; níveis 2–3 não
  iniciam simulação alguma (0/30).
- **"acceptable KGE did not guarantee hydrological quality"** — expôs *zombie calibration*.
- Tarefa de corrupção: **"logs and range constraints alone cannot detect physically corrupted model
  states"**; valores fisicamente impossíveis de SOL_K (5.000–15.000 mm h⁻¹) não geraram relatório de
  corrupção nem pelo agente restrito nem pelo baseline com script.

**A convergência real com o nosso trabalho — e NÃO é a que eu havia suposto do título.**
Eu havia inferido que o estudo mostrava interfaces estruturadas "entregando menos do que o desenho
sugere". Errado: elas entregam bastante — controle operacional e proveniência revisável. O que não
entregam é **validade**. Isso espelha exatamente o nosso par EMR/conformidade: reproduzir
perfeitamente não garante saída utilizável, e restringir o formato (fixed-slot) não melhora a
reprodutibilidade. Ambos localizam a mesma fronteira por lados opostos: a camada de controle é
necessária e não suficiente.

⚠️ **Enquadramento a imitar.** A frase deles sobre a falha da tarefa de corrupção é o modelo do que
o Lucas pediu: *"is not a failure of the MCP concept, it is a measurement of where that concept
currently sits in the design space, and a specification of the next layer required to advance it."*
Precedente, na revista-alvo, de limitação apresentada como especificação.

---

## Zhu, Chen, Ren, He, Sun, Zhang, Wen, Yue & Lü (2025) — EMS 186:106323
**read_depth: full-text** · via ScienceDirect com acesso institucional UTFPR, 2026-08-22 (9.770 palavras)

**O que é:** framework integrado para avaliar reprodutibilidade computacional de *geo-simulation
experiments* (GSEs), em duas partes: (1) avaliar o workflow computacional como um todo e (2)
investigar processos individuais para identificar inconsistências. Modelo de avaliação com dimensões
e métricas qualitativas e quantitativas, mais um sistema protótipo.

**Por que importa para nós:** o passo diagnóstico pressupõe que um processo, isolado, se comporta
da mesma forma ao ser re-executado — o que é verdade dos componentes computacionais baseados em
serviço para os quais o framework foi desenhado. Um passo mediado por LLM não se comporta assim.

**Verificado por busca no texto integral:** o artigo **não menciona** large language models, nem
não-determinismo, nem aleatoriedade em nenhum ponto do corpo (a única ocorrência de termo
correlato está numa referência bibliográfica). A afirmação de que se trata de um componente que
tais frameworks ainda não alcançam está, portanto, fundamentada — não é inferência do título.

**Limitação que eles próprios declaram:** aplicação confinada a GSEs baseados em serviço.
