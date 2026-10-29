# Gerenciamento anual — complemento vigente 26/10/2026

O novo agregado opcional `S.managementAnnual` tem `schemaVersion:1`, `revision`, `plans[]` e `audit[]`. Cada plano identifica conta, período e ano e preserva `config`, `openingSource`, revisões em `history[]`, declarações explícitas em `declarations[]` e retratos anuais imutáveis em `snapshots[]`. Ausência do agregado em backup antigo é válida e consultas não o criam. Versão futura ou conteúdo inválido seguem recuperação, preservando os bytes de origem.

Resultados reais permanecem exclusivamente no ledger canônico dos períodos Forex, escritos por `recordAccountLedger`. Um retrato anual contém cópias históricas identificadas para auditoria; não é uma segunda fonte de resultados ativos. A moeda do plano deve corresponder à moeda confirmada do período; ausência e divergência impedem leitura/ativação como fato confirmado.

Backup Completo inclui o agregado confirmado e a finalização da sessão o preserva pelo documento longitudinal existente. Rascunhos são trabalho em memória recuperável como texto, sem autorização reutilizável para gravar. Seleção e layout de Gerenciamento não persistem dados financeiros. [Contrato, APIs e compatibilidade](MANAGEMENT-ANNUAL.md).

## Fotografias anteriores preservadas

# Estado persistido — visão inicial

## Primeiro acesso vazio — contrato24/10/2026

[Plano aprovado](../superpowers/plans/2026-10-24-empty-first-use.md), contratos PRODUCT/TESTS em docs/work. A implementação e suas provas pertencem ao candidato desta tarefa; fotografias anteriores não o aprovam.

- Contas, períodos, operações e históricos pessoais nascem vazios. Catálogos, política, referências públicas datadas e exemplos identificados de simuladores permanecem. Sugestões editáveis de formulários não são fatos registrados.
- `params.saldoIni` e `saldoAtu` aceitam `null` explícito como não informado; `inicio`, nome/perfil do período e capital nominal legado ficam vazios inicialmente. ATRs, exposição e lote legados sem observação aceitam `null`. Não usar coerção numérica para apresentar ausência como zero. Um zero explicitamente registrado continua distinto.
- `checklist[].items[].v` aceita `null` (não respondido) ou os inteiros0/1/2. A pontuação/classificação somente aparece com todos os itens respondidos e ao menos um item. Chave apagada, string, booleano, fração ou valor fora da faixa continuam inválidos. Respostas antigas são preservadas.
- O envelope do Backup Completo permanece; o domínio desses campos foi ampliado. O candidato novo deve ler backups antigos e fazer roundtrip dos novos. Leitores antigos podem recusar os novos nulos: não há compatibilidade bidirecional universal.
- Não há exclusão retroativa por nome/valor semelhante aos antigos exemplos. Dados confirmados e campos desconhecidos compatíveis são preservados.


## Chave principal

```text
jpwealth_v9_state
```

## Agregados principais de `S`

- `params`: saldo, datas, MDD, alarme, gênese, VRM e referências.
- `matrix`: dados compatíveis/históricos preservados; a política vigente usa `JPWForex.policy`, não reinterpreta quatro índices como seis fases.
- `instruments`: instrumentos, preços, contratos, tetos e bloqueios.
- `profiles`: perfis de risco derivados da fonte central.
- `accounts`: parque de contas e dados operacionais.
- `fxConsolidated`: análise descritiva MT5, schema 1, com `accounts[]`
  (identidades/vínculos, orders/deals/positions e summaries), `receipts[]`,
  `revisions[]` e `defaultAccountId`. Não inclui arquivos originais, credenciais
  ou cópia de operações manuais. Backup completo inclui o agregado; Finalizar
  Sessão preserva a versão confirmada e identidades históricas mínimas, sem
  reativar contas operacionais. Seleção analítica não altera a conta ativa.
  Versões incompatíveis permanecem opacas. Contrato em
  [FOREX-CONSOLIDATED.md](FOREX-CONSOLIDATED.md).
- `phases`: grades e ordens da operação única.
- `ledger`: fechamentos diários do período.
- `ledgerArchive`: snapshots de períodos anteriores.
- `transitionLog`: auditoria de transições e eventos.
- `period`: identificação e perfil do período.
- `onboarding`: formulário de início e governança.
- `mei`: configuração e histórico do modelo estatístico.
- `quarantine`: intervalo de quarentena operacional.
- `fxPlanning`: Planejamento FX — plano (baseline congelado, premissas vigentes,
  revisões, fechamentos mensais, ledger cambial) e trilha de auditoria própria.
  Derivados nunca persistem; contrato em `FX-PLANNING.md`.
- `nocoda`: Estudos NoCoda — mapa `instrumentId → estudo vigente` com as três
  âncoras do canal. Um estudo por instrumento; derivados nunca persistem.
  Contrato em `NOCODA-STUDIES.md`.
- `activeOperation`: entidade da **Operação Única em curso**, ou `null` quando
  não há operação. `null` é estado real — "nenhuma operação" —, e não ausência de
  dado. Nasce no ato em que a primeira ordem se torna operacional e morre na
  Finalização formal. Guarda `operationId`, `openedAt` com `openedAtSource`
  (`genesis_transition` | `manual_legacy` | `null` — abertura de legado nunca é
  inventada), `maxAccountPhaseReached` (índice ou `null`; desconhecido **não** é
  Fase 1) e, quando houve falha de captura, `phaseCaptureFault`, que jamais é
  apagada por sucesso posterior. Contrato de encerramento no Art. 4.4 do
  Estatuto: zeragem tática sem confirmação escrita não extingue a Operação.
- `operationHistory`: memória institucional das operações finalizadas —
  `{schemaVersion, records[]}`. Registros são **imutáveis**: instrumento e
  direção da tese, timestamps com proveniência, `referenceBalance` congelado
  (o denominador do retorno precisa continuar auditável anos depois),
  `netResult`, `defenseCount` com `defenseCountSource`, fases máximas e
  `ordersSnapshot` desacoplado por `structuredClone`. `maxAccountPhaseIntegrity`
  admite **três** valores — `observed`, `unobserved` e `degraded` —, porque
  "capturado", "nunca capturado" e "captura falhou" são estados
  epistemologicamente distintos e o par binário anterior fazia o terceiro se
  passar pelo primeiro. O literal persistido para o estado do meio é
  `unobserved`; `unknown` aparece em discussão como sinônimo informal, mas não é
  o valor gravado. Invariante de integridade: `openedAt <= closedAt` quando
  ambos existem; uma operação não pode terminar antes de começar.
  O Consolidado Manual consulta esta mesma fonte, sem duplicá-la. Finalizar
  Sessão preserva o histórico confirmado; a exclusão total explícita mantém
  seu contrato. Campos capturados ausentes não são preenchidos pelo cadastro
  atual. Versões futuras permanecem opacas para evitar normalização destrutiva.
- `personalFinance`: Finanças Pessoais — domínio fechado (não cruza trading),
  schema v1 **congelado**: `{schemaVersion, moneyUnit:'BRL_CENTS', months{},
  recurringIncome[], debts[], creditLines[], scenarios[]}`. Montantes são
  inteiros em centavos de BRL; `null` = não informado ≠ `0` explícito. Mês
  ausente é virtual (projeção); o mês nasce no primeiro ato de edição, nunca
  por cópia nem em render. Dívida é identidade temporal
  (`startMonth`/`closedMonth`, sem status persistido); saldo é observação
  mensal em `months[*].debtSnapshots`. Derivados nunca persistem. `moneyUnit`
  inesperada jamais é reinterpretada → módulo em modo leitura. Memória
  longitudinal: sobrevive a Finalizar Sessão por herança explícita. O
  normalizador repara FORMA e jamais conteúdo (valor inválido é preservado e
  sinalizado, nunca "consertado"). Contrato em `PERSONAL-FINANCE.md`.
- `pivotStudies`: Estudos dos Pivots — lista histórica de estudos por
  instrumento e período, cada um contendo seus pivots H1/H4. Vários estudos do
  mesmo instrumento coexistem. Só causas persistem (timeframe, extremos de tempo
  e preço, correção informada); direção, amplitude, duração, ranking e toda a
  estatística são derivados. Contrato em `PIVOT-STUDIES.md`.

## Desfecho de gravação — fora do documento persistido

`operationProbePersisted(record)` responde em **três** estados sobre uma
tentativa específica de gravação:

| desfecho | significado | consequência |
|---|---|---|
| `CONFIRMED` | `operationId` **e** `finalizedAt` daquela tentativa estão no disco | mantém o candidato; finalização concluída |
| `NOT_PERSISTED` | evidência positiva de que a tentativa não chegou ao disco | rollback seguro |
| `UNKNOWN` | não se prova presença nem ausência | congela: sem rollback, sem veredito, gravação vetada |

A confirmação exige os **dois** campos. Só o `operationId` não basta: uma
tentativa anterior da mesma operação pode ter gravado, e confirmar por
identidade daria como persistida uma gravação que não foi esta.

`save() === false` continua sendo prova de não-escrita — os portões retornam
antes de tocar no armazenamento, o erro de serialização retorna antes do
`setItem`, e `setItem` é atômico. A ambiguidade vive exclusivamente no caminho
de **exceção**, que pode vir de antes ou de depois da escrita.

A barreira do `UNKNOWN` é de **sessão** e não entra no documento persistido —
gravá-la exigiria a gravação que ela veta. Contrato completo na regra 7 de
`DB-STORAGE-GOVERNANCE.md`.

## Regras de evolução

1. Toda chave nova entra em `DEFAULTS`.
2. `migrate()` deve aceitar estados anteriores sem perda silenciosa.
3. Migração nunca pode apagar campo desconhecido sem autorização formal.
4. Antes de mudança de schema, criar fixture anonimizada e teste de ida/volta de backup.
5. Credenciais não devem integrar fixtures, repositório ou commits.
6. Registro histórico não se reescreve. Um campo cujo domínio de valores cresce
   — como `maxAccountPhaseIntegrity`, que passou de dois para três — deixa os
   registros antigos como estão; corrigir rótulo em massa é pior que o rótulo
   antigo, porque destrói a distinção entre o que foi observado e o que foi
   inferido depois.

## Cobertura de exportação e preferências locais

O backup completo clona `S`; a lista deste inventário não filtra campos. `personalFinance`, `alladin`, `nocoda`, `pivotStudies`, `mvpNotes` e `fxPlanning`, além do núcleo operacional, são agregados de dados cobertos. `build` e `cobertura` são metadados descritivos adicionais do envelope de backup, sem mudança nos schemas dos domínios.

Perfil/foto, posição/aparência de Notas, navegação/layouts e preferências Galton são incorporados ao bloco opcional `workspace` schemaVersion1; o journal de importação e os rascunhos recuperados ficam em `state.workspaceRecovery`. Veja [COMPLETE-BACKUP](COMPLETE-BACKUP.md). Cache público e handles não constituem dados portáteis. Contrato de fonte, limites e confirmação: [DB-STORAGE-GOVERNANCE](DB-STORAGE-GOVERNANCE.md).

## Agregado Forex da revisão local

`S.forex` schemaVersion1 guarda accounts por ID, activeAccountId, market, h4Closes, grid, reserves, proposals, auditLog e migration explícita; `operationBudgets` é extensão opcional de declarações versionadas associadas a uma única operação. Ordens registradas capturam orderId, recordVersion, recordStatus, revisões e contexto de política; futuras observações não preenchem retroativamente o histórico ausente. `S.ledgerHistory` schemaVersion1 conserva eventos before/after, e as extensões opcionais do planejamento preservam envelope v1. Novas versões incompatíveis não são normalizadas como se fossem atuais. Contrato, comandos e limites em [FOREX-V11-ENGINE](FOREX-V11-ENGINE.md). Edições pendentes são material de revisão no workspace do backup, separado dos fatos confirmados.

## Extensões opcionais do Execution Board (2026-09-15)

`forex.instrumentContexts` schema1 conserva observações por conta/período/instrumento/moeda, componentes preço/ATR55-660H4/contrato/conversões, revisão e anterior. `forex.dailyReferences` schema1 conserva lotes datados do provedor diário. Escrita somente por comandos de `00-forex-state.js`; ausência não cria valor em render. Ordens capturam `instrumentObservation`/`dailyReference` disponíveis, sem preencher contexto histórico ausente. Rascunhos do Board continuam Map em RAM; o backup captura uma cópia para revisão em `workspace.drafts`, sem registrá-la como operação. Schema futuro é opaco e impede nova escrita/importação incompatível. Contrato detalhado em [FOREX-EXECUTION-BOARD.md](FOREX-EXECUTION-BOARD.md).

## Contextos operacionais por conta (revisão local)

`S.forex.accountContexts` schemaVersion1 contém envelope com revisão, contas por `forexAccountId`, períodos por identificador estável, período corrente, SI, saldo book, moeda, fonte, observações, no máximo uma operação ativa por conta entre todos os seus períodos, fases, ordens, fechamentos e eventos de revisão. `archivedAccounts` conserva a ficha histórica sanitizada; uma conta com operação ativa precisa finalizá-la antes do arquivamento, e uma conta arquivada não pode receber nova escrita operacional sem recadastro. O seletor operacional é efêmero e independente de `forex.activeAccountId`, utilizado pela análise do Consolidado. Leitores recebem conta e período; escritores revalidam identidade, revisão e epoch no ato de confirmação. A validação de backup rejeita ordens ou operações com vínculo de conta/período/moeda divergente. Em Operação, a faixa superior lê o início do período selecionado, sem apresentar a data global antiga como se fosse daquela conta. `S.phases`, `S.activeOperation`, `S.ledger` e `S.period` permanecem como legado global imutável na transição. `accountContexts.legacy` guarda seu snapshot integral. Após prévia e confirmação explícita, `associations` vincula somente por referência itens cujo identificador de conta, período e moeda coincidem com o contexto confirmado; divergências permanecem `UNRECONCILED`. Esses vínculos não transferem fatos aos lançamentos/ordens atuais nem ampliam totais; nenhuma atribuição automática à Mestre ou conversão das quatro grades antigas em seis fases é autorizada. Backup/restauração inclui somente fatos confirmados; Finalizar Sessão preserva o agregado e elimina desbloqueios e processos temporários.

O período contextual também guarda `grid` e `reserves` confirmados. ATR e demais observações de instrumento usam conta/período/instrumento, mesmo quando ainda não há observação antiga de equity; ausência de equity continua impedindo os cálculos que a exigem. H4 é um histórico por conta/período. Orçamento prospectivo usa a moeda confirmada do período e se associa, quando único e cronologicamente anterior, ao primeiro fato registrado no software na mesma transação; a associação não prova execução externa anterior nem autoriza execução. Redução exige risco comprometido calculável, sem presumir zero. A consulta de histórico de conta arquivada é somente leitura e não altera a seleção operacional. Formulários do Fator de Correção mantêm o destino do rascunho e recusam gravação depois de troca de conta/período até revisão explícita.


## Identidade e diagnósticos da Execution Board — 2026-09-22

Ordens recebem opcionalmente `brokerHash` textual e `identityContractVersion:1`. O marcador exige ID manual já no registro de uma pendente nova; HASH é exigido nos estados aberto/fechado, inclusive ao abrir essa pendente. Legados sem o marcador continuam válidos sem essas referências. Revisões e snapshots preservam os campos; nenhum ticket é associado automaticamente. HASH não é número nem identificador global.

`S.forex.executionDiagnostics` é extensão opcional `{schemaVersion:1, records:[]}`. Cada registro vincula `accountId`, `periodId`, `instrumentId`, `revision`, `declaredAt`, `declaredBy`, `oneWeek` e `twoWeeks`; horizontes aceitam `{n,f}` ou `null`. N é inteiro positivo em candles H4; F é positivo. Revisões anteriores permanecem em `previous`. Ausência não cria valores padrão no estado. O motivo do ato acompanha o auditLog. Writers seguem confirmação, epoch e revisão do agregado. Esses dados são cenários declarados, separados de observações ATR/mercado e de P21.

Validação do Backup Completo inclui a extensão e o HASH em ordens/revisões/histórico antes da escrita; backup antigo sem extensão permanece válido. `calculationInputs.executionDiagnostics` captura os parâmetros disponíveis em cada registro ou correção factual da ordem. A finalização conserva a última versão confirmada no snapshot; uma nova declaração de N/F não reescreve ordens já registradas ou histórico. Rascunhos do formulário ficam em RAM e podem ser incluídos como material recuperável, sem confirmar fatos financeiros. Contrato em [FOREX-EXECUTION-BOARD](FOREX-EXECUTION-BOARD.md).


## Extensões documentais de conta/perfil (CHG-FOREX-CONTAS-PERIODO-20260923)

Extensões opcionais, sem migração em massa nem alteração das versões existentes:
- `S.accounts[].accountEnvironment`: `real`, `demo`, vazio/unknown ou ausente; declaração cadastral sem inferência.
- `S.accounts[].riskProfileAssignment`: schemaVersion 1, accountId, profileKey, revision, assignedAt, source, declaredBy, reason e previous. Chaves conhecidas: base/longevity/high_longevity/high_longevity_plus. Revisão encadeada; valores financeiros não são copiados.
- `accountContexts.accounts[id].periods[periodId].riskProfileSnapshot`: captura documental só em criação explícita de primeiro período ou período posterior. Referências de conta, período, perfil, atribuição, data e política; status DOCUMENTARY_ONLY. Conciliação histórica e auto-período de observação não completam perfil.
- `recordContext.riskProfileSnapshot`: cópia do período na operação. Histórico não consulta cadastro atual para preencher lacunas.

Escolha deliberada muda atribuição cadastral; reload, sessão, mês, consulta e edição de metadados não ativam o novo perfil no período existente. O motor mantém a política corrente, independente da captura documental. Nomes antigos em `perfil` são evidência legada quando não há atribuição confirmada. A leitura não infere Base.

Importação valida extensões antes da primeira escrita, preserva unknown fields compatíveis e aceita documentos antigos sem elas. Credenciais continuam excluídas por política existente.

`accountContexts.archivedAccounts[id].previous` preserva arquivamentos anteriores ao recadastrar e arquivar novamente a mesma identidade. Recadastro conserva metadados e períodos, sem copiar saldos ou credenciais. A lista de arquivados exclui identidades com cadastro ativo, sem remover seus registros históricos.

A seleção de consulta e a seleção operacional são RAM. Confirmar cadastro/período conserva o par operacional anterior, inclusive ausência explícita de período. Arquivar a conta operacional, após validação de ausência de operação em andamento, deixa a seleção explicitamente vazia nessa sessão; outra conta não é ativada pelo gesto. A recarga conserva o comportamento legado de resolução inicial.

## Planejamento independente — 20/10/2026

`patrimonialPlanning` é opcional: `{schemaVersion:1,revision,accounts,archive,audit,operations}`. Não aparece em DEFAULTS nem é criado por leitura. Cada conta possui identidade, metadados e plano próprio, com referência inicial, premissas vigentes, resultados USD, aportes, saques, fechamentos e histórico. Projeções futuras ficam separadas dos fatos: taxa vazia é `null`; aporte futuro vazio é `''`, conservado como vazio e calculado como zero. Esses valores não criam lançamentos.

Dois campos opcionais descrevem a continuidade após reinícios, sem mudança de `schemaVersion`:

- `patrimonialPlanning.pendingConfiguration: {accountId,scope:'TODAS',at}` registra que todos os planos ativos foram arquivados e aguarda um novo formulário. A identidade referenciada existe, está inativa e não há outra conta ativa. Somente `createAccount` confirmado reutiliza essa identidade, cria o novo plano e remove o marcador. Cancelar a configuração conserva o estado pendente e os arquivos anteriores.
- `account.plan.incomeBaselineGoals` guarda os objetivos de renda vigentes no reinício individual. São objetivos normalizados, com valor, moeda, equivalente USD e cotação da conversão quando aplicável. A comparação de renda usa esse campo quando presente; nos planos anteriores, usa `reference.config.goals`. A referência financeira inicial permanece preservada, com sua associação atualizada para a nova identidade do plano.

`resetAccount` e `resetAll` validam uma prévia do alcance e a frase de confirmação antes de preparar um único candidato do documento principal. Os planos anteriores são copiados integralmente para `archive`, com metadados da conta, `reason:'restartPlan'`, `resetScope` e data. O reinício individual cria outra identidade de plano, reaplica as premissas e limpa lançamentos, fechamentos, alterações de projeção e parada de aportes da operação atual. O reinício total inativa os alvos e cria `pendingConfiguration`, sem inventar uma conta ativa ou substituir o arquivo anterior. `restartPlan` é o comando distinto de iniciar outro plano e criar nova referência; exige confirmação e ausência de fatos registrados incompatíveis.

O candidato só é adotado em memória após confirmação e releitura pelo escritor existente. Tokens de conta, plano, revisões e contexto impedem aplicar rascunhos sobre bases alteradas; resultado indeterminado não autoriza repetição automática. Versão incompatível bloqueia comandos e preserva dados. Os rascunhos de formulário permanecem em memória durante a sessão quando a janela é fechada ou uma ação é recusada; o Backup Completo os transporta separadamente como material de trabalho, sem convertê-los em fatos. Rascunhos importados exigem leitura, cópia e conferência manual.

`fxPlanning` permanece como legado somente exportável; nenhum campo é convertido. O formato de Backup Completo continua contendo o documento integral. Contratos detalhados: [PLANNING](PLANNING.md) e [edição mensal vigente](PLANNING-MONTHLY.md).


## Agenda pessoal opcional —23/10/2026

O plano humano Calendário e Agenda autoriza S.personalAgenda opcional; a regra histórica genérica de acrescentar toda chave a DEFAULTS não se aplica a este agregado, assim como ao Planejamento opcional. Ausência permanece virtual e não escreve. Envelope schemaVersion1/revision/items; esquema futuro e extensões preservados, comandos recusados se incompatível. Writer confirmado, sem alteração de fórmulas/migração financeira. Backup transporta objeto integral e importação recusa contêiner escalar antes da adoção. [Contrato e provas](CALENDAR-AGENDA.md).
