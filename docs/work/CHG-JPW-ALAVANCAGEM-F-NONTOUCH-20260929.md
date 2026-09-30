# CHG-JPW-ALAVANCAGEM-F-NONTOUCH-20260929 — 1.7.0

```yaml
schema: jp-harness/chg/v1
change_id: CHG-JPW-ALAVANCAGEM-F-NONTOUCH-20260929
status: approved_for_local_implementation
objective: F diagnostico selecionavel e primeiro nao toque teorico nos horizontes 1W/2W
risk_level: N3
authority_required: A4
target:
  root: /private/tmp/jpw-alavancagem-atual-20260926
  branch: codex/jpw-alavancagem-atual-20260926
  baseline_sha: f5145b25e86af6b4ccbfef847cba0d84d74e7c8a
derived_from: jpw-alavancagem-atual-20260929-r10
baseline_version: 1.6.0
baseline_build: 2ff5bb108d9b8af1
baseline_fingerprint: f1e86778bbebf2e38240ab58ec3201a48b99c987d4c485fa6d1c71d07765eeb9
approved_by: Proprietario, pedido PLEASE IMPLEMENT THIS PLAN para 1.7.0 nesta conversa
```

## Brief, autoridade e limite

O indicador MT5 de r10 calcula duas escalas temporais de 7/14 dias sem F, enquanto a pagina interna distribui fontes e orientacao. A autorizacao atual aprova **F=1,5 como padrao e F=1,8 como alternativa selecionavel somente no diagnostico do indicador**. O parametro canonico P-21 do Anexo continua `PENDING`, nao homologado; esta implementacao nao o altera nem fornece validacao empirica. N e definido por fechamentos H4 projetados para cada janela; a preferencia de F nao eleva calendario `Estimated` a `Current`.

O resultado antes e uma escala `ATR × √N`; depois, as linhas permanentes mostram `Raiz N diagnostica 1W/2W` com `Dpreco = ATR(55,H4) × √N × F` e `D% = 100 × Dpreco / P0`, com F explicito. A mesma amostra de Bid/Ask, ATR, horarios e qualidade atende os dois horizontes. `Details` oferece F 1,5/F 1,8, Aplicar e Cancelar, persistencia por instalacao/conta/simbolo exato, e a probabilidade browniana ideal `2Φ(√(8/π)F)−1` de primeiro nao toque de **barreira adversa hipotetica fixa criada no instante da leitura**. A probabilidade e igual em 1W e 2W para o mesmo F porque cada barreira hipotetica e recalculada com `√N`; nao e probabilidade do SL vigente, lucro ou eficacia observada. Os valores de referencia do Artigo 9 sao 98,332% e 99,593% para F=1,5 e 1,8.

O F padrao 1,5 opera somente quando nao existe preferencia salva. Registro corrompido ou incompativel bloqueia a saida diagnostica e requer tratamento explicito, sem fallback silencioso. A nova preferencia nao migra nem modifica N/F manual legado, cenarios, snapshots do EA, MDD, Genese, USC ou dados operacionais. Nenhum valor de conta e enviado ao site ou incluido no ZIP. `Current` continuara a descrever somente qualidade dos dados, nao homologacao do modelo.

## Proveniencia e preflight

| Fonte | Identidade/estado | Uso |
|---|---|---|
| r10 congelado em `outputs/jpw-alavancagem-atual-v160-r10-20260929` | 72/72 arquivos coincidem com snapshot e worktree; fingerprint acima; auditoria `BLOCKED`, full 55 PASS/2 PRODUCT_FAIL, MT5 nativo NOT_RUN | base e reversao; nenhuma falha reclassificada |
| Artigo 9, vault `2 - TRABALHO/2B - ARTIGOS E PESQUISA MODELO JP WEALTH` | SHA-256 `9a1639ee849bc1c2f0ef97243138f92be9fb24732b1e061f730effb5c5057842`; Tabela 2 e hipoteses brownianas | referencia teorica, nao validacao empirica |
| `docs/normative/ANEXO_PARAMETRICO_CANONICO.md` | P-21 `PENDING`; P-22 indeterminado caso a caso | autoridade normativa preservada |
| Harness externo canonico | SHA-256 `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`; §§12–19 e 36–48 | controle de mudanca e auditoria; nao editar |
| MetaQuotes `MathCumulativeDistributionNormal` | biblioteca `Math\Stat\Normal.mqh`; checar codigo de erro e finitude | implementacao de Φ, sujeita a compilacao nativa |

`tools/agent_preflight.py --mode audit` passou com avisos de historico da worktree; `--mode edit` parou por alteracoes existentes. A restricao foi reconciliada sem limpeza: os 66 caminhos de `git status --porcelain -uall` pertencem integralmente aos 72 arquivos do manifesto r10, todos conferidos por hash antes da escrita. Nao havia arquivo de trabalho inesperado. O aviso de contexto antigo nao concede autoridade; as fontes canônicas acima foram lidas diretamente. O preflight nao foi modificado.

## Escopo, validacao e rollback

Permitidos: CHG/ACTIVE-TASK, indicador, novos include/store/testes MQL5 e testes host correspondentes, README, pagina interna, manifesto, ZIP e derivados oficiais; evidencias externas, focais, full bruto e auditoria independente. Proibidos: mudanca do Anexo, Estatuto, Harness, quality gate/classificadores, conta real, ordem, stop, instalacao no MT5 operacional, commit, push, merge, deploy ou publicacao. A preferencia e esquema local novo, versionado e separado; a gravacao deve ser atomica no nivel logico com lock sem espera, dois slots recuperaveis, checksum e rejeicao de conflito.

Antes da entrega, conferir aritmetica de F=1,5 e 1,8, Tabela 2, independencia em N para barreiras proporcionais, qualidade de calendario/quote, Aplicar/Cancelar, conta/simbolo, corrupcao, duas instancias, falha de dados, geometria e paginacao. Executar focais pertinentes e um full bruto, preservar logs e classificacao. Compilacao/execucao dos bytes novos somente em MT5 isolado; sem ambiente utilizavel marcar `NOT_RUN`, sem `.ex5` ou prontidao operacional. Congelar candidate derivado com hashes/fingerprint e encaminhar auditoria independente. Resultado r10 permanece historico. Rollback: restaurar somente os bytes alterados desde o snapshot r10; nao tocar nos registros locais do usuario ou no projeto normativo.

## Resultado e recibos

Pendente de implementacao, verificacao, freeze e parecer. Human Acceptance e qualquer acao Git/publicacao sao etapas separadas.
