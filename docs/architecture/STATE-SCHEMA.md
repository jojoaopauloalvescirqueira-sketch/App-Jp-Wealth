# Estado persistido — visão inicial

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

Perfil/foto (`jpwealth_local_profile_v1`), posição de Notas (`jpwealth_notes_launcher_position_v1`), navegação/layouts e preferências Galton são locais e excluídos. Cache público e handles não constituem dados portáteis. Contrato de fonte, limites e confirmação: [DB-STORAGE-GOVERNANCE](DB-STORAGE-GOVERNANCE.md).

## Agregado Forex da revisão local

`S.forex` schemaVersion1 guarda accounts por ID, activeAccountId, market, h4Closes, grid, reserves, proposals, auditLog e migration explícita; `operationBudgets` é extensão opcional de declarações versionadas associadas a uma única operação. Ordens registradas capturam orderId, recordVersion, recordStatus, revisões e contexto de política; futuras observações não preenchem retroativamente o histórico ausente. `S.ledgerHistory` schemaVersion1 conserva eventos before/after, e as extensões opcionais do planejamento preservam envelope v1. Novas versões incompatíveis não são normalizadas como se fossem atuais. Contrato, comandos e limites em [FOREX-V11-ENGINE](FOREX-V11-ENGINE.md). O estado efêmero do editor não pertence a S ou ao backup.

## Extensões opcionais do Execution Board (2026-09-15)

`forex.instrumentContexts` schema1 conserva observações por conta/período/instrumento/moeda, componentes preço/ATR55-660H4/contrato/conversões, revisão e anterior. `forex.dailyReferences` schema1 conserva lotes datados do provedor diário. Escrita somente por comandos de `00-forex-state.js`; ausência não cria valor em render. Ordens capturam `instrumentObservation`/`dailyReference` disponíveis, sem preencher contexto histórico ausente. Rascunhos do Board são Map em RAM, fora de S/backup. Schema futuro é opaco e impede nova escrita/importação incompatível. Contrato detalhado em [FOREX-EXECUTION-BOARD.md](FOREX-EXECUTION-BOARD.md).

## Contextos operacionais por conta (revisão local)

`S.forex.accountContexts` schemaVersion1 contém envelope com revisão, contas por `forexAccountId`, períodos por identificador estável, período corrente, SI, saldo book, moeda, fonte, observações, no máximo uma operação ativa por conta entre todos os seus períodos, fases, ordens, fechamentos e eventos de revisão. `archivedAccounts` conserva a ficha histórica sanitizada; uma conta com operação ativa precisa finalizá-la antes do arquivamento, e uma conta arquivada não pode receber nova escrita operacional sem recadastro. O seletor operacional é efêmero e independente de `forex.activeAccountId`, utilizado pela análise do Consolidado. Leitores recebem conta e período; escritores revalidam identidade, revisão e epoch no ato de confirmação. A validação de backup rejeita ordens ou operações com vínculo de conta/período/moeda divergente. Em Operação, a faixa superior lê o início do período selecionado, sem apresentar a data global antiga como se fosse daquela conta. `S.phases`, `S.activeOperation`, `S.ledger` e `S.period` permanecem como legado global imutável na transição. `accountContexts.legacy` guarda seu snapshot integral. Após prévia e confirmação explícita, `associations` vincula somente por referência itens cujo identificador de conta, período e moeda coincidem com o contexto confirmado; divergências permanecem `UNRECONCILED`. Esses vínculos não transferem fatos aos lançamentos/ordens atuais nem ampliam totais; nenhuma atribuição automática à Mestre ou conversão das quatro grades antigas em seis fases é autorizada. Backup/restauração inclui somente fatos confirmados; Finalizar Sessão preserva o agregado e elimina desbloqueios e processos temporários.

O período contextual também guarda `grid` e `reserves` confirmados. ATR e demais observações de instrumento usam conta/período/instrumento, mesmo quando ainda não há observação antiga de equity; ausência de equity continua impedindo os cálculos que a exigem. H4 é um histórico por conta/período. Orçamento prospectivo usa a moeda confirmada do período e se associa, quando único e cronologicamente anterior, ao primeiro fato registrado no software na mesma transação; a associação não prova execução externa anterior nem autoriza execução. Redução exige risco comprometido calculável, sem presumir zero. A consulta de histórico de conta arquivada é somente leitura e não altera a seleção operacional. Formulários do Fator de Correção mantêm o destino do rascunho e recusam gravação depois de troca de conta/período até revisão explícita.
