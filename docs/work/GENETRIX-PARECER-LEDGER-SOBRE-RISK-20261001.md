# Parecer cruzado do autor do Ledger sobre Risk/Supervisor

Data: 2026-10-01. Escopo: revisão independente de autoria, por leitura, dos quatro fontes Risk indicados abaixo. Não é aprovação do Ledger que este revisor escreveu. Nenhuma alteração nos fontes Risk, execução nativa, leitura de conta ou ordem foi realizada nesta revisão.

## Bytes examinados

- `MQL5/Experts/JPWealth/JPW_Genetrix_Supervisor.mq5`: `49f5500c94df132d218dbb426310c39ab9481e2dec54cbfd40280b3008a04bd1`.
- `MQL5/Include/JPWealth/JPW_Genetrix_Risk_Core.mqh`: `8541070cd2544cd44eb083fbca27ea82b3bba201c21ea75b46ab7cacbdf42f5e`.
- `MQL5/Include/JPWealth/JPW_Genetrix_Risk_Terminal.mqh`: `7a2de90a6b429a514653c1bba309272aab0944f42d6f18a057f2c400ce0cb68f`.
- `MQL5/Include/JPWealth/JPW_Genetrix_Risk_Store.mqh`: `fc5a858e2a28a67613734d12e266acb082b5b94100104e8246fb65375e20b442`.

Os caminhos são relativos a `mt5/jpw-alavancagem-atual/` no checkout isolado `/private/tmp/jpw-genetrix-risk-ledger-20261001`. Oráculo consultado sem alteração: `tests/fixtures/genetrix/risk-oracles-v1.json`, SHA-256 `1c3e9488dd4fe1825d439efc8ea71e83cd34762639ef12770bf33e0cd83f4b7e`.

## Achado material — RIS-AC15

**P1 de aceitação do adapter: a transição após fill da pendente não exige o vínculo deal → posição previsto no oráculo.** `Supervisor.mq5:166–184`, em `JPWSupervisorReconcile`, aceita a ausência da ordem corrente com histórico terminal, calcula volume por `ORDER_VOLUME_INITIAL − ORDER_VOLUME_CURRENT` e chama `JPWRiskApplyOutcome(...CONFIRMED...)`. Para FILLED marca proteção incompleta e usa texto que não atribui sucesso ao cancelamento, o que está correto. Porém não consulta os deals dessa ordem, `DEAL_POSITION_ID`, nem comprova a publicação da posição resultante ou seu encerramento posterior.

Ramo concreto: em UNKNOWN de cancelamento, `OrderSelect(ticket)=false`, `HistoryOrderSelect(ticket)=true`, estado FILLED e uma captura julgada Current bastam para retirar a intenção. O timer retorna sem emitir outra solicitação no mesmo evento; no próximo timer o planejamento pode prosseguir, mesmo que o vínculo contábil do fill ainda não esteja reconciliado. O inventário agregado recente é informação objetiva, mas não demonstra sozinho a correspondência daquele fill com o estado resultante. A sequência de transações do terminal não tem ordem de chegada garantida.

Isso é um bloqueio contratual do critério RIS-AC15 antes de qualificar o adapter/executor como aceito. Não é prova de ordem incorreta observada no MT5: tal reprodução permanece NOT_RUN. Recomenda-se conservar UNKNOWN até testemunho positivo de deals ligados à ordem e identificadores resultantes coerentes com o inventário/cadeia posterior; tratar seleção parcial e fills transitórios como não reconciliados. O autor do Risk deve corrigir e produzir evidência focal do ramo real antes de nova revisão.

## Aspectos sustentados pela leitura

- O único `OrderSend` está em `Supervisor.mq5:321`; os caminhos anteriores exigem armamento explícito, identidade exata de conta demo, hedging sem FIFO, permissões e conexão. Há rechecagem após persistir intenção e após `OrderCheck`; conta real não satisfaz os guards.
- A intenção é persistida antes de envio. Resultado incerto conserva UNKNOWN; ausência de alvo ou prazo decorrido não liberam sozinhos uma nova ação. Recusa de fechamento pausa o LIFO; recusa de cancelamento marca proteção incompleta. Resultado parcial conserva a intenção integral e depende de ordem terminal e resíduo observado antes de tentar o restante.
- `OnInit` desarma, preserva UNKNOWN/REMAINDER e gira o desafio de sessão. UNKNOWN não pode ser rearmado; resíduo positivamente reconciliado precisa de rearmamento explícito. Falha de armazenamento bloqueia novas solicitações. Arquivo temporário interrompido e slot corrompido bloqueiam leitura, sem fallback silencioso para um registro limpo mais antigo.
- O gatilho é razão não arredondada estritamente maior que 7, com equity corrente; a margem numérica em `ValidateSnapshot` é usada para reconciliação, não para alterar o gatilho. A proposta considera toda a conta. Pendentes são uma projeção estática ao preço de entrada, FX atual e equity congelada, não garantia futura ou veto externo.
- As unidades do Risk usam a conversão canônica de equity/notional e perfil contratual USC. Isso é distinto do compensado do Ledger, que conserva moeda original e percentual sobre saldo da amostra. Não há substituição entre as duas bases.
- O leitor público do Risk oferece estado registrado recente, não prova de executor ativo. A UI examinada por referência usa “armada no registro”, “estado registrado” e data da leitura, evitando atribuição de execução apenas pelo registro.

## Resultado e limites

Revisão documental: **CONDITIONAL / RIS-AC15 pendente**. Não identifiquei por leitura outro caminho concreto de nova solicitação durante UNKNOWN, rearmamento automático ou substituição silenciosa da base equity por saldo. Não executei o harness Risk nesta revisão, pois a execução e seus recibos pertencem ao autor e ao root. Compilação nativa, singleton/arquivos nativos, resposta do broker, corridas reais, instalação e execução demo: **NOT_RUN**. Checksums e guardas no fonte não equivalem a aceitação operacional.

Referência primária para a limitação de ordenação: https://www.mql5.com/en/docs/event_handlers/ontradetransaction . Propriedades de vínculo: https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties .

## Adendo — correção RIS-AC15 no candidato congelado

Data: 2026-10-01. O parecer inicial acima é preservado como registro dos bytes então examinados. Este adendo altera a conclusão sobre RIS-AC15 apenas para os novos bytes:

- Risk Core: `8325dde4504ca17e72ce94604ef18ceac06a525edf325afaa12f4f127c00a380`.
- Supervisor EA: `fe803f551b7f7d5f35f3e5b1f89937bb12259ae97b1787e4cac3a99260f51d95`.
- Harness host: `e9a445c66df1ceb0323cf7707d66119cb76179bc7e6ffa61d1698927883886dd`.
- Risk Terminal e Store: hashes preservados do parecer inicial.

### Verificação do delta

`Core.mqh:92–134`, `JPWRiskEntryFillLinked`, exige deals IN vinculados ao ticket da pendente e ao mesmo identificador/símbolo/direção. A soma dos volumes vinculados deve coincidir com o fill esperado; entradas e saídas OUT/OUT_BY devem ser coerentes. Deals duplicados, direção incompatível, excesso de saídas e tipo de entrada não suportado são recusados. A posição viva deve ter o mesmo identificador, símbolo, direção e volume remanescente. Se ela não existe mais, são necessárias saídas positivas e volume remanescente reconciliado em zero; a ausência isolada continua insuficiente.

`Supervisor.mq5:154–235`, `JPWSupervisorCancelTerminalOutcome`, lê os campos históricos da ordem com sucesso explícito, seleciona a cadeia pelo identificador e constrói a evidência de deals. FILLED sozinho não libera UNKNOWN. Seleção ausente, limite superior a 2048 registros, orçamento interrompido, correção/cancelamento de deal não resolvido, reversão e campo inválido conservam a intenção incerta. O ramo revalida os campos da ordem após a coleta. Para preenchimento integral usa volume inicial; para cancelamento com fill parcial usa inicial menos residual, sempre conferindo a soma dos IN da ordem. Cancelamento sem nenhum fill confirmado continua possível sem inventar deal.

Antes de aplicar CONFIRMED, o ramo atualiza identificador, ordem e deal testemunha e exige sucesso de `JPWSupervisorPersist("ENTRY_ORDER_DEALS_POSITION_CHAIN_CONFIRMED", "ENTRY_FILL_LINK_CONFIRMED")`. Falha dessa chamada retorna sem retirar UNKNOWN. A orquestração preserva a regra de não enviar outra solicitação no mesmo timer da reconciliação. Não houve alteração observada no gatilho 7x, nos guards demo/identidade/permissão ou na política de intenção integral/LIFO neste delta.

### Evidência executada pelo revisor

Executei uma vez o harness congelado, em processo host separado, com arquivos sintéticos temporários e nenhuma API de conta ou negociação. Recibo: `outputs/jpw-genetrix-risk-ledger-20261001/reviewer-ledger-risk-ris15-r1/receipt.json`; log: `execution.log` na mesma pasta. Compilação host e execução retornaram zero: **51 asserts PASS, incluindo os 13 asserts focais RIS-AC15**.

Os 13 verificam: FILLED sem deals; ordem errada; identificador errado; fill ainda sem posição; cadeia ligada com posição viva; encerramento posterior positivamente reconciliado; fill parcial seguido de cancelamento; orçamento incompleto; seleção acima do limite; deal cancelado; volume vivo incompatível; cancelamento sem fill; falha da persistência do testemunho. O corpo real de `JPWSupervisorCancelTerminalOutcome` e o Core são compilados; história e APIs do terminal são sintéticas. Não são casos integrais de MT5.

A chamada de persistência dentro desse corpo é uma seam sintética neste teste: ele comprova o guard e a ordem de chamada antes da liberação, **não comprova durabilidade nativa do testemunho nem a integração do fluxo completo EA → Store → broker**. Os checks de Store do harness executam separadamente seus corpos reais com primitivas host. O JSON independente congelado permaneceu referência documental do autor; esta execução não substitui a validação numérica independente do root.

### Conclusão atualizada

**P1 inicial fechado no nível de fonte e ramo host focal para os hashes deste adendo.** Não identifiquei neste delta outro bloqueio concreto equivalente à liberação por FILLED sozinho. Isso não muda o estado do caso integral, da orquestração completa do EA, da compilação/execução nativa, dos locks nativos, da durabilidade em falha real, das corridas do terminal ou da instalação/execução demo: **NOT_RUN**. A aceitação operacional continua condicionada à evidência correspondente; o histórico e o inventário não são certificados completos pelo teste sintético.
