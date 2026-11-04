# Rodada de recalibração v1.2 — instruções

**Data:** 2026-07-29
**Para:** labeler1 (Rater 1) e labeler2 (Rater 2)
**Tempo estimado:** ~15 min de leitura + ~30-40 min de reavaliação (25 abstracts)

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

Leiam **§0**, **§2.1**, **§4** e os **Exemplos 3, 5 e 6** (§7) do
[`protocolo_v1.2.md`](protocolo_v1.2.md) — os exemplos 5 e 6 são novos e cobrem
exatamente o ponto que gerou as discordâncias. O essencial:

**Critério 5 agora tem três níveis.**

| Nível | O abstract traz | Decisão |
|-------|-----------------|---------|
| 5a | Estimativa numérica **e** IC 95% numérico | critério atendido |
| 5b | Diz que estimou o efeito, mas **sem os valores** | **UNCERTAIN** |
| 5c | Nenhuma estimativa e nenhuma menção a uma | **EXCLUDE** |

Por que 5b e 5c terminam em decisões opostas, sendo os dois falha do mesmo critério:
em **5b** o abstract afirma que o efeito foi estimado, então o número existe no texto
completo e é o abstract que o omitiu — marcar EXCLUDE afirmaria algo sobre o estudo que
não temos como verificar, e marcar INCLUDE afirmaria que checamos o critério quando não
checamos. Em **5c** não há menção alguma; a ausência total é evidência razoável de que
o estudo não produziu estimativa extraível, e aí EXCLUDE se sustenta. A diferença não é
o critério que falhou, é quanta informação o abstract dá sobre a falha.

**Peso dos critérios.** Falha clara em critério **estrutural** (1 estudo original,
2 PM2.5, 3 hospitalização respiratória, 6 inglês) → **EXCLUDE**, mesmo que seja só um.
Falha apenas no critério **4** (design) ou no **5b** → **UNCERTAIN**. Falha em 2 ou
mais → EXCLUDE. Quando duas regras se aplicam: EXCLUDE > UNCERTAIN > INCLUDE.

Se aparecer um caso que **nenhuma linha da tabela cobre**, não improvise: marque
UNCERTAIN, escreva no rationale qual foi o impasse, e avise o Lucas. Foi justamente um
caso não coberto que produziu a discordância da primeira rodada.

## O que fazer

1. Abrir **apenas o seu arquivo** (vem em `.xlsx` e `.csv` — use o que preferir):
   - Rater 1 → `recalibracao_labeler1`
   - Rater 2 → `recalibracao_labeler2`
2. São os **25 abstracts em que houve discordância**. Os 75 concordantes não são
   reabertos.
3. Reavaliar cada um **sob a v1.2**, preenchendo as colunas `*_v12`
   (`decision_v12`, `confidence_v12`, `rationale_v12`, `criteria_failed_v12`).
4. **Continua sendo independente.** O seu arquivo não mostra a decisão da outra, nem a
   sua decisão anterior — é de propósito. Não combinem antes de terminar.
5. Devolver o arquivo preenchido para o Lucas.

## O que acontece depois

O que ainda ficar discordante vai para uma reunião curta de consenso; sem consenso, a
Profa. Yara dá o tie-break, registrando qual critério invocou. O gold standard final
guarda, para cada abstract, se a decisão veio de concordância direta, da recalibração,
do consenso ou do tie-break — dá para auditar item por item.

## Sobre o κ de 0.529: não há número a bater

Ele **será publicado assim**, independentemente do que esta rodada produzir. Não se
troca um resultado pelo outro.

E o motivo mais importante para vocês não sentirem pressão: **esta rodada não gera um
novo κ.** Como só estamos reavaliando os itens em que houve discordância, qualquer
coeficiente recalculado sobre os 100 subiria automaticamente — não porque a concordância
real melhorou, mas por causa de como o subconjunto foi escolhido. O que a rodada mede é
quantos dos 25 convergem, e é assim que vai ser reportado.

Então: se você reler um abstract sob a regra nova e continuar achando o mesmo, registre
o mesmo. Manter a decisão é uma resposta tão útil quanto mudá-la.

Vale dizer por que o κ baixo não é um problema a ser escondido. Um protocolo escrito
por pesquisadores treinados ainda assim produziu 25% de discordância na primeira
rodada. Num artigo sobre reprodutibilidade de triagem, isso é dado, não constrangimento
— é a linha de base humana contra a qual os LLMs estão sendo medidos, e ela só existe
porque vocês duas rotularam de forma genuinamente independente.

## Anonimização (2026-11-04)

Por decisão do primeiro autor, as avaliadoras aparecem no repositório só como Rater 1
(labeler1) e Rater 2 (labeler2). As planilhas `returned/*_RETURNED_SOURCE.xlsx` foram
anonimizadas no conteúdo e no metadado de autor; as decisões, critérios e justificativas
não mudaram. SHA-256 dos arquivos originais, guardados fora do repositório:

- recalibration_labeler1_RETURNED_SOURCE.xlsx: `23d3ea9290215fde0bc78f7078feca7cae1f2bd4fd7d022bcfa98d113e966725`
- recalibration_labeler2_RETURNED_SOURCE.xlsx: `ab874b092f855633e762a8e57059b1f96d02b600a27ff9480f05d3f377711af4`
- tiebreak_Yara_RETURNED_SOURCE.xlsx: `c7b6227d793ca37154dee08ff2913605e8522c2ba7f4f7364b1845f1b58a4ff8`
