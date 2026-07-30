# Rodada de recalibração v1.2 — instruções

**Data:** 2026-07-29
**Para:** Isabelle (labeler1) e Luiza Iltchechen (labeler2)
**Tempo estimado:** ~30-40 min (25 abstracts)

---

## O que aconteceu

Vocês duas terminaram a triagem independente dos 100 abstracts. Obrigado — os dois
conjuntos chegaram completos e íntegros.

Concordância bruta: **75%** (75 dos 100). O κ de Cohen ficou em **0.529**, abaixo do
alvo Cochrane de 0.80.

**Isso não é erro de vocês.** Ao analisar as 25 discordâncias, 19 seguem exatamente o
mesmo padrão e 17 delas dependem de um único ponto: o **critério 5**. O texto do
protocolo v1.1 permitia duas leituras igualmente defensáveis, e cada uma de vocês
adotou uma. A tabela de decisão, além disso, dizia o que fazer quando o abstract falha
em 2 critérios ou fica borderline em 1 — mas não dizia o que fazer quando ele **falha
claramente em exatamente 1**, que é o caso desses 17.

Ou seja: o protocolo estava incompleto. Foi corrigido.

## O que mudou no protocolo (v1.2)

Leiam as seções **§0**, **§2.1** e **§4** do
[`../protocols/labeling_protocol.md`](../protocols/labeling_protocol.md). O essencial:

**Critério 5 agora tem níveis.**

| Nível | O abstract traz | Decisão |
|-------|-----------------|---------|
| 5a | Estimativa numérica **e** IC 95% numérico | critério atendido |
| 5b | Diz que estimou o efeito, mas **sem os valores** | **UNCERTAIN** |
| 5c | Nada, nem menção | conta como falha |

A lógica do 5b: a triagem é só sobre o abstract. Um estudo que diz ter estimado o
efeito quase certamente reporta os números no texto completo — o abstract é que é
omisso, não o estudo. Marcar EXCLUDE afirmaria algo sobre o estudo que não temos como
verificar; marcar INCLUDE afirmaria que checamos o critério quando não checamos.

**Peso dos critérios.** Falha clara em critério **estrutural** (1 estudo original,
2 PM2.5, 3 hospitalização respiratória, 6 inglês) → **EXCLUDE**, mesmo que seja só um.
Falha apenas no critério **4** (design) ou **5b** → **UNCERTAIN**. Falha em 2 ou mais →
EXCLUDE. Quando duas regras se aplicam: EXCLUDE > UNCERTAIN > INCLUDE.

## O que fazer

1. Abrir **apenas o seu arquivo**:
   - Isabelle → `recalibration_labeler1.csv`
   - Luiza → `recalibration_labeler2.csv`
2. São os **25 abstracts em que houve discordância**. Os 75 concordantes não são
   reabertos.
3. Reavaliar cada um **sob a v1.2**, preenchendo as colunas `*_v12`
   (`decision_v12`, `confidence_v12`, `rationale_v12`, `criteria_failed_v12`).
4. **Continua sendo independente.** O seu arquivo não mostra a decisão da outra, nem a
   sua decisão anterior — é de propósito. Não combinem antes de terminar.
5. Devolver o CSV preenchido para o Lucas.

Mudar de decisão é esperado e não é problema. Manter a decisão também é uma resposta
válida — se sob a regra nova você continua achando a mesma coisa, registre isso.

## O que acontece depois

O que ainda ficar discordante vai para uma reunião curta de consenso; sem consenso, o
Lucas dá o tie-break, registrando qual critério invocou.

## Sobre o κ de 0.529

Ele **será publicado assim**, independentemente do que esta rodada produzir. Não se troca
um resultado pelo outro.

E uma coisa importante, para tirar qualquer pressão de cima de vocês: **esta rodada não
gera um novo κ.** Como só estamos reavaliando os itens em que houve discordância, qualquer
coeficiente recalculado sobre os 100 subiria automaticamente — não porque a concordância
real melhorou, mas por causa de como o subconjunto foi escolhido. O que a rodada mede é
quantos dos 25 convergem, e isso é reportado como tal.

Então não existe "número a bater" aqui. Se você reler um abstract sob a regra nova e
continuar achando o mesmo, registre o mesmo. Manter a decisão é uma resposta tão útil
quanto mudá-la.

Isso é deliberado: um protocolo escrito por pesquisadores treinados ainda assim
produziu 25% de discordância na primeira rodada. Num artigo sobre reprodutibilidade de
triagem, isso é dado, não constrangimento — é a linha de base humana contra a qual os
LLMs estão sendo medidos.
