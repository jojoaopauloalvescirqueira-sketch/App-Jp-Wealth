# Forex V11 — arquitetura da revisão local

Campanha FOREX-V11-CENTRAL-01. Base Git `edcdd82fee5a220fcee282552a5b607cec563d3f`.
Este documento descreve a implementação em revisão, não aceite, integração ou homologação financeira. Identidade final, resultados e recuperação pertencem ao manifesto/relatório externos da campanha.

## Autoridade e estados

Constituição I.6/I.7 → Estatuto V11 → Anexo somente nos elementos delegados → motor → UI. `src/js/00-core/00-forex-policy.js` registra versões, hashes, fontes por campo, unidades, vigência, autoridade e homologação. As cópias normativas não foram editadas.

Política ativa é imutável. `JPWForex.createEngine(policy)` permite calcular com uma política completa e explicitamente identificada; um cenário sintético não ativa nem homologa essa política. Funções puras retornam `{status,value,unit,findings,policyVersion,calculationMode}`. `null` significa ausência ou resultado não calculável, nunca zero implícito.

P-14/P-18/P-17 impedem admissão normativa. P-10 e P-30 não recebem percentuais históricos como fallback. P-23 continua PENDING, com a exclusão quantitativa expressa na fonte; sua ausência não cria um veto extra inventado. Duração de quarentena P-24 não vira 90 dias. O requisito de constituição de reservas e suas verificações permanece distinto do mero registro dos valores.

## Responsabilidade de cada camada

| Fonte | Responsabilidade |
|---|---|
| `00-core/00-forex-policy.js` | Catálogo normativo imutável e referências |
| `10-domain/00-forex-engine.js` | DD, fases, histerese, risco, alavancagem, VRM, reservas e limites puros |
| `10-domain/00-forex-state.js` | Observações explícitas, migração, audit trail, confirmação e propostas locais |
| `10-domain/02-risk-calculations.js` | Read-model único e adapter `compute()` para consumidores existentes |
| `10-domain/03-phase-transitions.js` e `11-operation-lifecycle.js` | Registro/correção/anulação factual, identidade, revisão e finalização |
| `30-accounting/01-daily-ledger.js` | Projeção contábil e eventos com before/after |
| `30-accounting/05-fx-planning/` | Um motor temporal com ACTUAL, PLAN e SCENARIO distintos |
| `20-ui/26-forex-engine-views.js` | Formulários e leitura de resultados; não contém fórmulas normativas |

## Fatos, elegibilidade e identidade

`S.forex` v1 reúne observações de conta, equity, mercado, H4 confirmado, grade e reservas; IDs, fontes, instantes e períodos são explícitos. `recordAccountFacts` não assume que saldo book é equity nem cria vínculo de conta por semelhança de nomes. Alterar SI ou moeda exige novo período declarado. Observação retroativa não substitui a observação atual; o rascunho permanece disponível para correção do ato. Grade conhecida pertence à operação; não é inferida pela quantidade de ordens. Candle H4 precisa ser registrado com fonte, conta e período, não apenas tempo decorrido. Somente fechamentos anteriores ou iguais ao instante observado podem sustentar sua fase.

Uma ordem pode ser registrada em fase restritiva ou com finding de desconformidade. Sua estrutura ainda é validada. Correção exige motivo e conserva revisão; anulação conserva o fato com `recordStatus: voided`. `recordContext` e snapshot de política dão proveniência à captura. A consulta explícita usa conta/período da operação, inclusive quando a seleção corrente é outra; uma identidade inexistente não cai na conta selecionada. Novas ordens conservam conta, período, moeda e `calculationInputs` (contrato, preços, volume e conversões observados no ato), com revisões before/after. Essa captura factual não é um snapshot pré-execução. Operações novas não recuperam contexto histórico ausente pelo cadastro atual. Legado preserva `LEGACY_UNRESOLVED` e seus quatro índices; não são reinterpretados como as seis fases atuais.

`compute()` é compatibilidade de apresentação; o risco agregado, orçamento prudencial e risco de admissão são resultados separados. Sem captura histórica anterior à execução, o risco de admissão não é reconstruído com stop ou cadastro atuais. Pendência sem estado explícito, ordem sem conta/período/moeda e reservas em outra unidade permanecem não conciliadas; os fatos são preservados. Lucro Técnico normativo continua não calculável; a soma positiva factual não se apresenta como sua definição. A12 e as dívidas normativas anteriores não são homologadas por esta campanha.

## Confirmação, erro e compatibilidade

Os comandos usam o escritor existente com proteção de revisão, epoch, conflito, recuperação e UNKNOWN. Recusa comprovada restaura somente os agregados do ato e seu log; não desfaz alterações legítimas de outros domínios. Desfecho desconhecido permanece bloqueado contra retry cego. O rascunho do formulário fica em memória e exige nova confirmação.

Não há migração em render/navegação. `migrateLegacy` é um ato explícito, versionado e auditado: conserva snapshot das fontes legadas e acrescenta identidade sem recalcular história. Envelope futuro/incompatível é preservado e recusado pela camada apropriada. O backup completo continua exportando `S`; nenhum segredo temporário do editor entra nele.

`S.ledger` continua a projeção ativa; `S.ledgerHistory` v1 conserva eventos de criação, correção e anulação. O plano continua no envelope `S.fxPlanning` v1; revisões novas usam `planningRevision:2`, `actualHistory`, `scenarios`, `scenarioArchive`, `rebases` e snapshots de cálculo. Planos retirados do ativo permanecem em `archivedPlans`.

Importar ACTUAL do ledger exige prévia vinculada a IDs/versões, conta/período, reconciliação da abertura e declaração de completude. Não há propagação automática nem sobrescrita silenciosa de realizado manual. Alterar a linha N recalcula N e posteriores, preservando anteriores e baseline. SCENARIO não grava ACTUAL ou o plano aprovado.

## Reservas e conflitos

FCR usa capital nominal da Mestre conforme PDF, não SI por conveniência. Dois capitais nominais explícitos divergentes exigem conciliação; o motor não escolhe o menor ou o mais recente por conveniência. Reservas são vinculadas à conta, período e moeda de sua observação. FEO utiliza montante real de seis meses explicitamente apurado, com referência ao método e aprovação das despesas; não aplica 21% nem deduz automaticamente seis vezes uma despesa mensal. Os conflitos com o Anexo e os requisitos de homologação permanecem em findings. Constituição, liquidez, abertura do período, distribuição e catraca são estados separados; cálculo de requisito não autoriza essas ações.

## Limite real do editor

O operador configura uma frase temporária própria. WebCrypto deriva o verificador com sal aleatório em RAM. Nenhuma senha previamente fornecida está em código, fixtures, bundle, hash fixo, log ou estado persistido. A sessão tem expiração de cinco minutos, trava ao fechar Configurações e é descartada ao encerrar o contexto. Resultados assíncronos tardios não reabrem sessão encerrada.

Esse mecanismo é fricção local, contornável pelo proprietário do navegador/DevTools; não autentica pessoa ou autoridade normativa. A ativação permanece indisponível sem ato e autoridade verificáveis. É possível registrar propostas com motivo, fonte, campo, antes/depois, identificação declarada e versão, sem afetar a política vigente. Não há backend, login online ou serviço novo.

## Validação e recuperação

Focais: `forex_v11_engine_test.py`, `forex_v11_state_test.py`, `forex_recording_test.py`, `forex_v11_ledger_planning_test.py` e `forex_v11_journey_test.py` e `forex_v11_read_model_test.py`. Regressões existentes afetadas preservam caracterizações da base nas evidências antes da atualização deliberada de contratos. Testes financeiros não substituem homologação empírica/normativa. Suítes, falhas anteriores, auditoria e limitações devem ser consultadas no relatório final, sem inferir aprovação desta descrição.

Geração de build e portátil somente por `tools/rebuild_monolith.py`. O precache inclui os novos scripts e mantém o protocolo PWA. Rollback limitado ao delta desta worktree a partir da base e snapshots externos; não autoriza reset, stash ou limpeza de outras árvores. `AGENTS`, fontes canônicas gerais de estado e handoffs protegidos permanecem intocados; suas declarações históricas não foram atualizadas nesta campanha.

## Histórico, unidades e confirmação de fase
A observação confirmada de equity atualiza o pico de fase somente da operação vinculada à mesma conta e período. A atualização participa da transação e de seu rollback; navegar ou renderizar não captura fatos.
`cycleRealizado` permanece um acumulado LEGACY sem unidade/contexto completo. Encerrar uma nova operação V11 não incrementa esse scalar: seu resultado auditável reside em `operationHistory.records`, com conta, período, moeda e snapshots capturados. Isso não converte nem reescreve resultados legados.
O histórico agrega valores apenas quando todos os resultados são conhecidos e a moeda capturada é única. Ausência de moeda, resultado ou contexto é visível; cadastro e matriz atuais não preenchem o passado. As fases legadas continuam identificadas como LEGACY. Cópias distinguem dados da operação, snapshot de entrada e observação disponível no fechamento; esta observação não promete equity medida no instante exato do encerramento. Lucro Técnico e demais lacunas de A12 continuam parciais.
Os adapters de risco/nocional usam conta, período e moeda do fato, sem fallback para a conta selecionada. Os valores factuais atuais não são um snapshot de admissão pré-execução.

## Declaração de orçamento e sequência indisponível
`forex.operationBudgets` é uma extensão opcional escrita somente pelo comando explícito. Cada declaração identifica conta, período, moeda, valor, fonte, autoria declarada, instante e revisões. A associação ao primeiro registro de uma operação ocorre no mesmo ato transacional. O mesmo orçamento não financia outra operação; aumento não é permitido e uma redução depende de RC conhecido. Declarações retrospectivas são identificadas; timestamps locais não comprovam pré-execução no mercado.
`computeSizingTrace` documenta a interrupção imposta pelos parâmetros P14/P18: primeira etapa BLOCKED, seguintes NOT_EVALUATED, volume final ausente. Tetos por fase/VRM são informações diagnósticas distintas de dimensionamento aprovado. Sem volume inicial normativamente calculável, mínimo de lote, arredondamento e etapa vinculante final não são apresentados como avaliados.
A consolidação de uma operação V11 com conta/período/moeda ausentes ou conflitantes é recusada por integridade monetária; os fatos continuam preservados e editáveis no alcance disponível. Esta revisão não infere vínculo histórico pela conta selecionada nem oferece reparação automática de contextos não capturados.

### Carregamento e status explícito de ordens
A recarga não transforma rascunho preenchido em ordem aberta, nem converte `Active` legado em fato V11. A contraprova executou o `migrate()` completo com dados sintéticos e comprovou a promoção antiga; a revisão remove apenas essa inferência. Atividade legada sem status conciliado permanece intacta e produz `ORDER_STATUS_UNRESOLVED`/NOT_COMPUTABLE no agregado, nunca risco zero presumido. Rascunhos explicitamente identificados ficam fora da exposição. O focal inclui recarga real, além da contraprova isolada; evidências antes/depois são preservadas no diretório da campanha.

## Execution Board — contexto por instrumento (2026-09-15)

A evolução local em [FOREX-EXECUTION-BOARD.md](FOREX-EXECUTION-BOARD.md) separa projeções factuais, rascunhos RAM e escrita por linha. `orderInputs` compartilha `executionBoard.instrumentInputs`: contratos/conversões por conta/período/instrumento, com origem. `readModel` usa ATR vinculado ao instrumento da Gênese única; ATR global é legado não distribuído. Policy/engine não mudam. Observações e referências diárias são comandos versionados, não cálculo na UI. Estado e validação exatos pertencem aos recibos externos da campanha; aceite/homologação permanecem separados.
