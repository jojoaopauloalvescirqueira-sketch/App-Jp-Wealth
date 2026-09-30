# CHG-JPW-ALAVANCAGEM-HORIZONS-20260929 — 1.6.0

```yaml
schema: jp-harness/chg/v1
change_id: CHG-JPW-ALAVANCAGEM-HORIZONS-20260929
status: approved_for_local_implementation
risk_level: N3
authority_required: A4
root: /private/tmp/jpw-alavancagem-atual-20260926
branch: codex/jpw-alavancagem-atual-20260926
base_sha: f5145b25e86af6b4ccbfef847cba0d84d74e7c8a
derived_from: jpw-alavancagem-atual-20260929-r9
baseline_version: 1.5.0
baseline_build: b448b7146f0a87b5
baseline_fingerprint: 9deb86863c0f7d358dbcb7dd667b118d6db1ab71bfdd21322b89ab80898f66e9
approved_by: Proprietário; PLEASE IMPLEMENT THIS PLAN, 1.6.0, nesta conversa.
```

## Brief e fronteira

O JP Wealth é apoio local à gestão de risco, sem oferecer sinal ou autorizar ordem. Este trabalho atende à leitura diagnóstica de horizontes semanais no MT5, sem alterar o motor financeiro do navegador. A pasta `mt5/jpw-alavancagem-atual` contém indicador, núcleos MQL5, scripts e documentação de instalação; a página Ferramentas e Serviços distribui somente fontes e orientação. Hoje, r9 apresenta um único Raiz N corrente com N/F manual e quatro linhas; depois haverá escalas temporais 1W/2W automáticas por símbolo exato, sem rotular como Raiz N calibrada na ausência de F homologado. Um EA opcional observará negócios executados localmente e gravará snapshots factuais, sem enviar ordens. Página, manifesto, ZIP e testes são consumidores da versão e do inventário.

Invariantes: alavancagem = nocional bruto/equity, flutuante, Gênese, DD/MDD e seus stores; nenhum valor N/F legado migra automaticamente. Nenhum fallback `F=1,25`, calendário aprovado fictício, ordem, stop, conta real, instalação operacional, alteração normativa ou alteração do Harness/quality gate. `Current` descreve apenas qualidade de dados, nunca aprovação do modelo. Falta de cotação, ATR, calendário ou política não produz zero aparente. Rollback: restaurar somente o delta 1.6 a partir do snapshot externo r9, mantendo inalterados os arquivos legados e os registros do usuário.

Autorizado: CHG/ACTIVE-TASK, MQL5 do indicador e novos includes/EA/testes específicos; README, página, manifesto e geradores/derivados oficiais; evidências externas, focais, full bruto e auditoria independente. Proibido: commit, push, merge, deploy, publicação, instalação em MT5 operacional, negociação, credenciais e dados reais. O pedido atual é autorização inequívoca da implementação local N3/A4, não das etapas Git.

## Fontes e proveniência

| Fonte | Identidade e trecho aplicável | Papel |
|---|---|---|
| `docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf` | SHA-256 `2dab6166bb8513cd9beb7fe39c574971af086ebae66683d99c0e6fac69eb6769`; Raiz N diagnóstica, F pendente | M0, não alterada |
| `docs/normative/ANEXO_PARAMETRICO_CANONICO.md` | P-21 F=`PENDING`; P-22 N caso a caso; canonicidade não é homologação | M0, não alterada |
| `docs/decisions/ADR-0009-fator-raiz-n.md` | SHA-256 `11129e7cd978732220959b698e694344cbd8b94e708f9737489a8de53e68f2c2`; `PROPOSTO`, decisão pendente | M2, não ativada |
| Artigo 9 no vault, atualmente `2 - TRABALHO/1B - MODELO JP WEALTH/Artigo_9_Modelo_Raiz_N_JP_Wealth.pdf` | SHA-256 `9a1639ee849bc1c2f0ef97243138f92be9fb24732b1e061f730effb5c5057842`; p. 5, 12–18: fórmula, horizonte prévio, F não homologado e registro inicial preservado | análise externa, lida diretamente; caminho do plano anterior foi movido |
| Deep Research recebida no Desktop | SHA-256 `f184289f619264553f5d9c4df9f8562eeec94afcdcaf6af5836083595a2bcd17`; calendário, observador e testes propostos | pesquisa, não decisão normativa nem prova de runtime |
| Harness canônico externo, atualmente `2 - TRABALHO/99A -   SOFTWARE DEV/99 - PROMPTS SOFTWARE DEV/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md` | SHA-256 `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`; §§12–19, 36–48 | control plane, leitura apenas |
| r9 congelado em `outputs/jpw-alavancagem-atual-v150-r9-20260929` | 63/63 arquivos vivos e snapshot conferidos; especificação externa idêntica; fingerprint acima | base de código/reversão, **BLOCKED**, full 53 PASS/4 PRODUCT_FAIL, MT5 nativo NOT_RUN |

O Artigo 9 não fixa calendário datado futuro, F universal ou preço da decisão humana. A escolha do usuário é um cenário padronizado 7/14 dias civis do servidor com N por fechamentos H4 esperados; não equivale ao horizonte justificadamente escolhido para um trade. `F=1,25` só entra em teste aritmético ilustrativo. Para promover Raiz N calibrada no futuro, exigir política versionada por horizonte/escopo/vigência/autoridade/hash aprovado; esta revisão não a fornece.

## Contrato técnico e segurança

1. Uma amostra corrente do símbolo exato: `P0=(Bid+Ask)/2` do mesmo tick, iATR(55,H4) da última barra fechada; preços positivos/finitos, histórico sincronizado e novo tick observado após inicialização para classificar atualidade. Limite técnico de 30 s. Calcular `ATR*sqrt(N)` e `100*ATR*sqrt(N)/P0`, sem USC em preço; apresentar 1W/2W como `Time Scale` sem F. Detalhes mostram N, preço, horários e qualidade.
2. N conta fechamentos H4 previstos em `t0 < fechamento <= fim`, com janelas móveis de 7 e 14 dias civis no relógio do servidor. Calendário datado versionado/aprovado e cobertura integral permitem `EXACT`; projeção por sessões de cotação recorrentes e confronto com barras observadas é `ESTIMATED`; metadados insuficientes/contraditórios dão `UNAVAILABLE`. Nenhum calendário aprovado é distribuído. Rejeitar DST/feriado não determinado como exatidão.
3. O EA local é observador somente leitura. Registra primeiro negócio executado por episódio, preço executado (não decisão), identidade opaca e ATR da última barra concluída antes do negócio. A grade recorrente e o N são resolvidos após o callback, com horário próprio de observação, sem alegar que esses metadados eram conhecidos no instante da execução ou da decisão humana. Operações parciais, adições e eventos repetidos são idempotentes; reversão netting inicia episódio novo. Callback tardio ou captura não comprovada recebe `RECONSTRUCTED` somente se o histórico for suficiente. SQLite local próprio com versão, transações e chaves idempotentes; falha ou conflito não cria alegação de captura concluída. Indicador consulta, não escreve, snapshots. Não usar APIs de envio de ordens.
4. Stores MDD, Gênese, USC e cenários manuais antigos permanecem independentes e legíveis. Nenhum dado de conta no site/ZIP; apenas fontes públicos. Downloads e HTML portátil/cache são gerados pelos comandos oficiais. Nenhum EX5 sem compilação real vinculada aos bytes.

Verificações: matemática e limites; dias úteis, 24/7, domingo parcial, feriado, DST, cobertura ausente; tick vencido/novo, histórico ATR insuficiente, virada H4; hedging, parcial, adição, reversão netting, duplicata, reinício e reconstrução tardia; integridade transacional e compatibilidade de stores; página, pacote, quatro layouts/offline; gate full bruto, diff/fingerprint e auditoria independente. Testes sintéticos não demonstram APIs MT5 nativas. Compilação/execução em MT5 isolado somente se ambiente utilizável; caso contrário `NOT_RUN`, sem EX5 ou prontidão. O r9 `BLOCKED` fica histórico e não é reclassificado.

## Resultado e recibos

Pendente de implementação, candidate freeze, focais, full, evidência nativa e parecer. Registrar comandos, saída integral e classificação `PASS`, `PRODUCT_FAIL`, `TEST_HARNESS_FAIL`, `ENVIRONMENT_ERROR`, `BASELINE_FAIL` ou `NOT_RUN` no conjunto externo deste CHG, sem compor PASS a partir de execuções diferentes. Human Acceptance e ações Git/publicação continuam posteriores.
