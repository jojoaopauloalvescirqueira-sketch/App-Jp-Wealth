# Estado persistido — visão inicial

## Chave principal

```text
jpwealth_v9_state
```

## Agregados principais de `S`

- `params`: saldo, datas, MDD, alarme, gênese, VRM e referências.
- `matrix`: matriz quadrifásica base.
- `instruments`: instrumentos, preços, contratos, tetos e bloqueios.
- `profiles`: perfis de risco derivados da fonte central.
- `accounts`: parque de contas e dados operacionais.
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
  passar pelo primeiro. Invariante de integridade: `openedAt <= closedAt` quando
  ambos existem; uma operação não pode terminar antes de começar.
- `pivotStudies`: Estudos dos Pivots — lista histórica de estudos por
  instrumento e período, cada um contendo seus pivots H1/H4. Vários estudos do
  mesmo instrumento coexistem. Só causas persistem (timeframe, extremos de tempo
  e preço, correção informada); direção, amplitude, duração, ranking e toda a
  estatística são derivados. Contrato em `PIVOT-STUDIES.md`.

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
