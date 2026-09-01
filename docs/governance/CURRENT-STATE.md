# Estado atual do projeto

## Alladin ALD-05-S2 — criação de lançamento pela UI publicada — 2026-09-01

- Data da fotografia: 2026-09-01
Source revision representada: `964c38b724d8d048f8e7899637ef86e2ccda1cf9`
- **`main` == `origin/main` == `964c38b724d8d048f8e7899637ef86e2ccda1cf9`**;
  worktree em `main`, sem trabalho pendente.
- **ALD-05-S2 = PUBLICADO E CI-CONFIRMADO** (commit `964c38b`, CI **Run #50
  success**). A interface agora **cria lançamentos**: `DEPOSIT`, `WITHDRAWAL`,
  `TRANSFER`, `BUY`, `SELL`, `FEE`, `TAX`, `ADJUSTMENT_CREDIT` e
  `ADJUSTMENT_DEBIT` — um **modal único** no painel Lançamentos, com seletor de
  tipo e campos específicos por evento.
- **Ciclo completo disponível pela aplicação**: registrar → persistir →
  visualizar, em Lançamentos / Saldos / Posições — o dado econômico exibido
  volta **exclusivamente dos read-models**, nunca do formulário.
- **O domínio é a única autoridade**: uma chamada a
  `JPWAlladin.ledger.addTransaction` por submit; o payload jamais carrega
  `transactionId`, `recordedAt`, `status`, `currency`, `flowScope` ou
  `unitPrice`; dinheiro só por `money.parse` (minor units); `quantity`
  **verbatim** (grafia não-canônica é recusada pelo domínio, nunca corrigida
  pela UI); moeda derivada da conta, exibida read-only. Recusa nunca vira
  sucesso; rascunho sobrevive à recusa; double-submit inerte; cancelar é
  zero-write. Sob sentinela BLOCKING o CTA **não é renderizado** — e o write
  gate vale na abertura E no submit (estado que piora entre abrir e salvar é
  recusado pelo domínio).
- **REVERSAL permanece FORA** (slice própria) · **`dedupeKey` não exposta** ·
  **MD-2 permanece dívida** (envelope de `transactions()`, slice própria) ·
  **domínio/schema/persistência NÃO mudaram** (`13-alladin.js`, `index.html` e
  CSS intocados).
- **Tiers reais: `standard` 41 · `full` 52** — 41/41 e 52/52 locais; CI #50
  com a primeira execução remota de `tools/alladin_ui_tx_write_test.py`
  (TX-A..TX-N, datas fixas com varredura estrutural contra dependência de data
  corrente).
- **Dívidas e decisões futuras:** REVERSAL pela UI · envelope de
  `transactions()` (MD-2) · cost-basis N3 + arredondamento §29 + escala
  decimal por moeda (três pré-requisitos do ALD-04-S2) · varredura das 7
  suítes que fixam `'2026-08'` · **QA-D2** · dívida de nome
  `ALD_CAMPO_NAO_PERMITIDO_EM_DESPESA` · `ALD_REASON_NAO_PERMITIDO` como
  *tightening* aceito · in-kind/corporate actions.
- **Próxima decisão — gate humano:** REVERSAL pela UI, MD-2, ou destravar
  ALD-04-S2 pelas decisões normativas. **Nenhuma autorizada por este documento.**

## Alladin ALD-05-S1 — superfície econômica publicada — 2026-09-01 (fotografia histórica)

- Data da fotografia: 2026-09-01
Source revision representada: `212297accef9d81d28322147a1420bbd06eb2c95`
- **`main` == `origin/main` == `212297accef9d81d28322147a1420bbd06eb2c95`**;
  worktree em `main`, sem trabalho pendente.
- **ALD-05-S1 = PUBLICADO E CI-CONFIRMADO** (commit `212297a`, CI **Run #48
  success**). Pela primeira vez o Alladin é **visível na aplicação**:
  **Lançamentos, Saldos e Posições** existem como destinos read-only no
  `section#alladin`, depois dos quatro cadastrais — projetando
  `leitura.transactions()`, `leitura.saldoDeCaixa()` e `leitura.posicoes()`
  **sem nenhuma aritmética na UI** (dinheiro só por `money.format`, `quantity`
  como string canônica verbatim, nenhuma coluna de sinal/direção).
- **Invariante central provado nos dois sentidos**: read-model indisponível
  **jamais** vira zero, lista vazia ou tela normal — sob BLOCKING não há tabela,
  número nem texto de empty, só o aviso textual com os `issues` do domínio; e o
  inverso também vale: agregado legítimo vazio mostra EMPTY sem alarme falso, e
  saldo legitimamente zero continua exibível. Em Saldos o bloqueio é por linha.
- **Sentinela de integridade dos Lançamentos (MD-2/A)**: `transactions()` não
  tem envelope de qualidade e filtra registro não-objeto em silêncio; a
  confiabilidade vem de `posicoes()` + `compat()`. Guarda de apresentação, não
  regra econômica. **Dívida viva**: envelope próprio em slice específica.
  Fronteira do sentinela provada em E12b (moeda divergente só-caixa é acusada
  pela linha de Saldos, não por ele).
- **Repair temporal do finpes-budget** (`c3ad00d`, CI **Run #47 success**):
  cinco casos fixavam fixture em `'2026-08'` e liam a tela do mês **corrente**
  — passavam por coincidência de calendário e caíram juntos na virada para
  setembro. Test bug, produto intocado: os casos agora navegam com
  `fbGoTo(key)` e provam por rótulo (`.fb-month-label`) que renderizam o mês da
  fixture. O CI #47 rodou **em setembro** e passou — a prova real da correção.
- **Contrato de UI re-escopado (MD-1, decisão humana)**: os 4 destinos
  cadastrais seguem congelados em rótulo/ordem e **sem conteúdo econômico**
  (varredura agora POR PAINEL, não pela section — o rótulo da aba "Saldos" é
  navegação); suíte nova `tools/alladin_ui_ledger_test.py` (E1–E16 + E12b) no
  tier `standard`. **Tiers reais: `standard` 40 · `full` 51** — verificados
  40/40 e 51/51 locais e `standard` 40/40 no CI #48.
- **Dívidas e decisões futuras:** envelope de `transactions()` (MD-2) ·
  cost-basis N3 + arredondamento §29 + escala decimal por moeda (**três**
  pré-requisitos do ALD-04-S2) · escrita transacional pela UI (par natural do
  S1) · varredura das 7 suítes que fixam `'2026-08'` (mesma classe do repair;
  CI é UTC e a máquina local UTC−3 — divergência de mês por até 3h na virada) ·
  transferência in-kind e corporate actions · **QA-D2** · dívida de nome
  `ALD_CAMPO_NAO_PERMITIDO_EM_DESPESA` · `ALD_REASON_NAO_PERMITIDO` como
  *tightening* aceito.
- **Próxima decisão — gate humano:** produto (envelope de `transactions()`,
  escrita transacional pela UI, ou destravar ALD-04-S2 pelas três decisões
  normativas). **Nenhuma autorizada por este documento.**

## Alladin ALD-03-S4 — ADJUSTMENT publicado — 2026-08-31 (fotografia histórica)

- Data da fotografia: 2026-08-31
Source revision representada: `a88b4509ee1651dc9a9b1676ea20d55f1872f131`
- **`main` == `origin/main` == `a88b4509ee1651dc9a9b1676ea20d55f1872f131`**;
  worktree em `main`, sem trabalho pendente.
- **ALD-03-S4 = PUBLICADO E CI-CONFIRMADO** (commit `a88b450`). O ledger passou
  a registrar **diferença de caixa sem contraparte econômica identificável**:
  um extrato que não fecha por dois centavos, um crédito que o banco lançou e
  não explica, um arredondamento de custódia.
- **Contrato**: `ADJUSTMENT_CREDIT` = `cash delta = +amount` ·
  `ADJUSTMENT_DEBIT` = `cash delta = −amount` · `amount` **magnitude positiva**,
  nunca assinado · **direção exclusivamente pelo `eventType`** (sem campo
  `direction`) · **efeito em posição = zero** · **`flowScope` ausente** ·
  **sem vínculo a transação** · reversal pela **mecânica existente**.
- **Dois tipos em vez de um campo de direção**: a direção passa a ser protegida
  pelo mesmo código que já protege o resto do ledger — o espelho do par compara
  `reversedEventType` e o efeito da reversão é resolvido a partir do tipo do
  **original**. Um `direction` avulso seria um segundo lugar onde a direção
  mora, e o único protegido por nada.
- **`reason` OBRIGATÓRIO, campo próprio**: o ajuste é o único evento cujo valor
  **não pode ser conferido contra nada** — não há original de onde herdar nem
  contraparte com que comparar. A justificativa é parte da **forma** do
  registro. **`note` continua opcional e distinto**: nota é comentário, `reason`
  é justificativa, e uma não cobre a outra.
- **Fronteira normativa registrada, não implementada**: `ADJUSTMENT` **não é
  external flow** e **não é economic gain/loss**. **Nenhuma matemática de
  performance** e **nenhum Reconciliation Engine** foram implementados. Quando
  o Performance Book existir, ele **deve** segregar `ADJUSTMENT` explicitamente,
  jamais absorvê-lo no residual `Closing − Opening − NetExternalFlow`.
- **HARDENING — completude do cash delta**: `aldTxEfeito` **não pode mais
  assumir delta 0 silenciosamente**. `eventType` cash-affecting sem semântica
  explícita em `ALD_CASH_DELTA` agora é **BLOCKING** com diagnóstico próprio
  (`ALD_CASH_DELTA_AUSENTE`), distinto do reversal órfão. Isso **elimina a
  classe de falha "saldo plausível e falso por evento ignorado"** — a única do
  módulo capaz de produzir número confiável e errado em vez de recusa. **Sem
  guarda equivalente para `ALD_PAPEL_DELTA`**: ali a ausência é legítima.
- **`schemaVersion` 5 → 6 — identity migration** (um elo, carimbo puro): zero
  campo criado, alterado ou removido; **zero transformação econômica**; ledger
  **povoado preservado** byte a byte. **Mixed-build**: v6 lendo v5 **migra e
  preserva**; v5 lendo v6 responde **`READ_ONLY_FUTURE_SCHEMA`** e **para de
  escrever** — antes do carimbo o build antigo chamava um `ADJUSTMENT` válido
  de corrupção **e seguia escrevendo por cima**.
- **Evidência local**: candidate fingerprint
  `f14c43c7d27b8e74c116a573915d1f62a630d26c6458904f4492753970678e2e` ·
  mutations **MA-1..MA-7 = DEAD** (zero sobreviventes) · `fast` **4/4** ·
  `standard` **39/39** · `full` **50/50** · **non-PASS = 0**.
- **Evidência CI**: **Run #45** sobre `a88b450` — **completed / success**, job
  `quality` = **success**. O `standard` 39/39 é **consistente com o contrato de
  saída do quality gate** (`return 0 if all(check["result"] == "PASS" ...)`, ou
  seja, exit 0 exige que **toda** verificação seja PASS). **O log bruto não foi
  obtido nesta observação (HTTP 403)** — a afirmação é dedução do contrato, não
  leitura do artefato.
- **Dívidas e decisões futuras:** cost-basis N3 (necessário antes do ALD-04-S2
  se *specific identification* entrar em escopo) · escala decimal por moeda ·
  transferência in-kind · corporate actions · **QA-D2** · comentário "SOMENTE
  LEITURA" em `index.html` · **dívida de nome**:
  `ALD_CAMPO_NAO_PERMITIDO_EM_DESPESA` é usado **também** pela família só-caixa
  (o código diz "DESPESA" para um ajuste) · **`ALD_REASON_NAO_PERMITIDO`
  aceito como *tightening* do write contract** — recusar `reason` em tipo
  não-ADJUSTMENT em vez de descartá-lo em silêncio.
- **Próxima decisão — gate humano:** `ALD-04-S2` ou `QA-D2`.
  **Nenhuma autorizada por este documento.**

## Alladin ALD-03-S3 — FEE/TAX publicado — 2026-08-31 (fotografia histórica)

- Data da fotografia: 2026-08-31
Source revision representada: `928788966f05ecc50f294a1c4b936eb68f43e6b2`
- **`main` == `origin/main` == `928788966f05ecc50f294a1c4b936eb68f43e6b2`**;
  worktree em `main`, sem trabalho pendente.
- **ALD-03-S3 = PUBLICADO E CI-CONFIRMADO** (commit `9287889`). O ledger passou
  a registrar **despesa sem contraparte de trade**: `FEE` e `TAX` standalone
  (custódia, manutenção, imposto de período), que antes não tinham como ser
  registrados sem distorcer um `WITHDRAWAL`.
- **Contrato**: `cash delta = −amount` · **efeito em posição = zero** ·
  **`flowScope` ausente** (taxa não é retirada de capital; é custo que reduz o
  retorno) · moeda **derivada da CashAccount** · reversal pela **mecânica
  existente** · **sem vínculo a trade**.
- **BUY/SELL preservados**: `fees`/`taxes` de trade continuam **embutidos** no
  próprio trade, economicamente inalterados — nenhum trade foi decomposto,
  migrado ou reinterpretado. A ausência de vínculo torna a dupla contagem
  **irrepresentável**, **sem nenhuma heurística econômica** de double-count.
- **`schemaVersion` 4 → 5 — identity migration** (um elo, carimbo puro): zero
  campo criado, alterado ou removido; **zero transformação econômica**; ledger
  **povoado preservado** byte a byte na migração. O carimbo existe para que
  **mixed-build v4 lendo v5** responda `READ_ONLY_FUTURE_SCHEMA` — dado válido
  de versão futura deixa de ser confundido com corrupção.
- **Evidência**: mutation **8/8 DEAD** · `full` local **50/50** · **CI Run #43
  SUCCESS** com `PASS=39`, `PRODUCT_FAIL=0`, `TEST_HARNESS_FAIL=0`,
  `ENVIRONMENT_ERROR=0`, `BASELINE_FAIL=0`, `NOT_RUN=0`. Décimo verde
  consecutivo (#34–#43).
- **ADJUSTMENT continua FORA** — slice própria (S4); direção e semântica ainda
  **precisam de decisão humana**.
- **Dívidas e decisões futuras:** cost-basis N3 (necessário antes do ALD-04-S2
  se *specific identification* entrar em escopo) · escala decimal por moeda ·
  transferência in-kind e corporate actions · **QA-D2** · comentário "SOMENTE
  LEITURA" em `index.html`.
- **Próxima decisão — gate humano:** `ALD-03-S4` (ADJUSTMENT), `ALD-04-S2` ou
  `QA-D2`. **Nenhuma autorizada por este documento.**

## Alladin FULL HARDENING concluído — 2026-08-31 (fotografia histórica)

- Data da fotografia: 2026-08-31
Source revision representada: `3f2716da80f2d7367e61e535b3651426b8631e01`
- **`main` == `origin/main` == `3f2716da80f2d7367e61e535b3651426b8631e01`**;
  worktree em `main`, sem trabalho pendente.
- **ALLADIN FULL HARDENING = CONCLUÍDO** (commit `3f2716d`). Auditoria
  arquitetural adversarial encontrou e fechou um **cluster P0/P1 de integridade
  estrutural**: os read-models e o write gate confiavam em invariantes que só a
  porta de escrita impunha, e um agregado **persistido** adulterado produzia
  número financeiramente plausível e **falso**. O eixo é `aldFindIn`, que
  resolve todo id por **first-match** na leitura *e* na escrita — id canônico
  duplicado torna a identidade ambígua.
- **`aldIntegridadeEstrutural` protege os três pontos**: `saldoDeCaixa`,
  `posicoes` (⇒ `BLOCKING`) e **`aldMutate`** (⇒ recusa antes de `fn` rodar —
  nenhuma escrita nova sobre agregado de identidade ambígua). Valida:
  unicidade dos IDs canônicos `instrumentId`, `assetId`, `accountId`,
  `cashAccountId`, `transactionId`; `dedupeKey` única; **≤1 reversal por
  original**; pareamento **status⟺reversal** consistente; container
  `transactions` **fail-closed**; e o **saldo passou a bloquear future-schema**
  (guarda que só `posicoes` tinha).
- **Discriminação preservada:** dois fatos econômicos legítimos idênticos (ids
  distintos, sem `dedupeKey`) **continuam somando** — só a corrupção provável
  bloqueia.
- **Isolamento de Service Worker propagado** às suítes de app real apropriadas
  (`foundation`, `finalize_preservation`, `ui_crud`,
  `session_write_serialization`); a suíte do próprio SW segue sem bloqueio.
- **CI vigente: Run #41 (`3f2716d`) SUCCESS** — `PASS=39`, `PRODUCT_FAIL=0`,
  `TEST_HARNESS_FAIL=0`, `ENVIRONMENT_ERROR=0`, `BASELINE_FAIL=0`, `NOT_RUN=0`.
  Oitavo verde consecutivo (#34–#41).
- **Readiness local do candidato:** mutation **10/10**, `full` **50/50**,
  `standard` 39/39, `fast` 4/4.
- **Nenhum P0/P1 CONHECIDO restante dentro dos vetores auditados** — é a
  fronteira do que a auditoria exercitou, não prova universal de ausência.
- **Dívidas e decisões futuras:** escala decimal por moeda (antes de JPY/BTC ou
  valuation) · transferência in-kind e corporate actions (exigirão `accountId`
  first-class; trades atuais não migram) · cost-basis N3 / *specific
  identification* (só ela exigiria lot-ref no `SELL`, antes que vendas
  acumulem) · **QA-D2** · comentário "SOMENTE LEITURA" em `index.html`. Sobre o
  agregado v2 com `transactions` estruturalmente inválido: a escrita normal
  agora é **bloqueada** — o que resta é questão de *routing/recovery*, não de
  gravabilidade.
- **Próxima decisão — gate humano:** (1) `ALD-03-S3` — recomendado, aditivo e
  desbloqueado; (2) `ALD-04-S2` — depende da decisão N3 de cost basis;
  (3) `QA-D2`. **Nenhuma em implementação neste gate.**

## QA-D1 resolvido pela causa — 2026-08-31 (fotografia histórica)

- Data da fotografia: 2026-08-31
Source revision representada: `b7ada805f95ec44501804546ea8389d567bc80bb`
- **`main` == `origin/main` == `b7ada805f95ec44501804546ea8389d567bc80bb`**;
  worktree em `main`, sem trabalho pendente. CI Run #39 SUCCESS — sexto verde
  consecutivo (#34–#39).
- **QA-D1: RESOLVIDA — HARNESS BUG.** Causa raiz provada com sonda positiva e
  negativa: o `page.route` do Playwright não intercepta fetches servidos por
  Service Worker; após o reload do caso N, a PWA controlava a página e o
  `updateFxRates` do boot recebia cotação **real** por fora do stub — `ok>0`,
  `save()`, e o disco mudava na janela de comparação, acusando falsamente a
  superfície do Alladin. Correção em `b7ada805`: o harness de
  `alladin_ui_readonly_test.py` nasce com `service_workers="block"`. O produto
  não foi tocado — atualizar cotações no boot é comportamento legítimo.
  Sensibilidade preservada e provada por mutação real (MQ-1); suíte isolada
  6/6; `full` 50/50 na primeira execução.
- **Dívidas vivas:** QA-D2 · comentário "SOMENTE LEITURA" em `index.html`.
- **Próxima decisão — gate humano:** continuidade do ALD-04, `ALD-03-S3` ou
  QA-D2. **Nenhuma autorizada por este documento.**

## Alladin — Position Quantity Engine publicado — 2026-08-31 (fotografia histórica)

- Data da fotografia: 2026-08-31
Source revision representada: `29bb6ff722964dfd283558fc5bd73590a5a5b69b`
- **`main` == `origin/main` == `29bb6ff722964dfd283558fc5bd73590a5a5b69b`**;
  worktree em `main`, sem trabalho pendente.
- **ALD-04-S1 CONCLUÍDO.** Existe posição por quantidade **derivada** do
  ledger: `JPWAlladin.leitura.posicoes()`, identidade
  `instrumentId + accountId` (a custódia vem exclusivamente de
  `cashAccount.accountId`), BUY/SELL/REVERSAL agregados em `quantity` por
  aritmética decimal **exata** em BigInt, posição zerada fora da coleção,
  negativa como string assinada fiel (sem semântica de short), fail-closed
  global (adulteração, orfandade cadastral, moeda divergente e schema futuro
  ⇒ indisponível) e saída determinística. `schemaVersion` permanece **4** —
  zero estado persistido novo.
- **Não existe** (fronteira que não se antecipa): holding persistido ou
  consolidado, cost basis, valuation/current value, patrimônio consolidado,
  P&L, performance, benchmark, FX patrimonial e UI de posições.
- **CI vigente: Run #37 (`29bb6ff`) SUCCESS** — `standard` 39/39 no Ubuntu:
  `PASS=39, PRODUCT_FAIL=0, TEST_HARNESS_FAIL=0, ENVIRONMENT_ERROR=0,
  BASELINE_FAIL=0, NOT_RUN=0`. Quarto verde consecutivo (#34–#37).
- **Readiness local do candidato:** `fast` 4/4, `standard` 39/39, `full`
  **50/50**; suítes `alladin_position` P1–P17 e `alladin_unit` U1–U26;
  mutation MP-1..MP-11 = 11/11 DEAD.
- **Dívidas abertas:** **QA-D1** — disparou uma vez no primeiro `full` local
  do ALD-04-S1 (`alladin-ui-readonly`, caso N), passou isoladamente, o `full`
  subsequente fechou 50/50 e não reproduziu no CI #37; **continua ABERTA**,
  sem classificação definitiva. **QA-D2**. Comentário "SOMENTE LEITURA" em
  `index.html`.
- **Próxima decisão — gate humano:** continuidade do ALD-04, `ALD-03-S3`
  (FEE/TAX/ADJUSTMENT standalone) ou dívida técnica como QA-D1. **Nenhuma
  autorizada por este documento.**

## Alladin — BUY/SELL publicado, CI verde — 2026-08-30 (fotografia histórica)

- Data da fotografia: 2026-08-30
Source revision representada: `cc4714e4513016af636b17ca7948c2755f50ef03`
- **`main` == `origin/main` == `cc4714e4513016af636b17ca7948c2755f50ef03`**;
  worktree em `main`, sem trabalho pendente.
- **O ledger registra dinheiro E papel.** `S.alladin.transactions[]` com
  `DEPOSIT`, `WITHDRAWAL`, `TRANSFER`, `REVERSAL` (Cash Ledger, ALD-03 S1) e
  `BUY`/`SELL` (ALD-03 S2): um trade é UM registro de duas pernas — caixa
  `−(amount+fees+taxes)` / `+(amount−fees−taxes)` e papel `±quantity` —, com
  `fees`/`taxes` sempre presentes na forma persistida, `flowScope` **ausente**
  em trades (declará-lo é recusa por presença), consistência do par
  reversal↔original julgada também na leitura (`ALD_REVERSAL_INCONSISTENTE` ⇒
  BLOCKING) e guardas de inteiro seguro na escrita e a cada soma do saldo.
  `schemaVersion` **4** — carimbo puro de barreira de escrita; o build v3 lê
  fail-closed e é trancado (`READ_ONLY_FUTURE_SCHEMA`), provado por mixed-build
  contra o código real de `4057a39`.
- **Cadeia publicada desde a última fotografia:** `5a6f7c3` (ALD-03 S1 — Cash
  Ledger) → `93f6e78` (reconciliação de governança) → `4057a39` (CI-ENV-01-FIX)
  → `cc4714e` (ALD-03 S2 — BUY/SELL).
- **CI-ENV-01-FIX ✅ e a dívida `session-epoch-protocol` ENCERRADA** — causa
  raiz: o checkout do runner clonava raso (`fetch-depth: 1`) e os SHAs
  históricos pinados pelas suítes não existiam no clone; `E6/E15` reprovavam
  como `ENVIRONMENT_ERROR` e `F/F2` eram pulados em silêncio contando como
  PASS. Correção: `fetch-depth: 0` + política de `NOT_RUN` explícito (caso sem
  histórico nunca soma como aprovado). Registrada em `QUALITY-GATES.md`.
- **CI vigente: Run #35 (`cc4714e`) VERDE** — `standard` no Ubuntu com
  `PASS=38, PRODUCT_FAIL=0, TEST_HARNESS_FAIL=0, ENVIRONMENT_ERROR=0,
  BASELINE_FAIL=0, NOT_RUN=0`; segundo verde consecutivo (Run #34 idem). Com a
  política NOT_RUN, o verde autocertifica que os casos históricos
  (mixed-build/rollback) executaram de fato no runner.
- **Readiness local:** `fast` 4/4, `standard` 38/38, `full` **49/49**; suítes
  `alladin_ledger` L1–L29, `alladin_unit` U1–U25, `alladin_foundation` até
  V/V2; mutation do candidate S2: MS-1..MS-16 16/16.
- **Dívidas abertas:** QA-D1 · QA-D2 · comentário "SOMENTE LEITURA" em
  `index.html`.
- **Próxima decisão de arquitetura (gate humano, nenhuma autorizada):**
  `ALD-03-S3` — `FEE`/`TAX`/`ADJUSTMENT` standalone (DHs próprios em aberto:
  direção do ADJUSTMENT, flowScope de FEE) — **ou** progressão para `ALD-04`
  (Position Engine) conforme planejamento aprovado.

## Alladin — Cash Ledger publicado — 2026-08-29 (fotografia histórica)

- Data da fotografia: 2026-08-29
Source revision representada: `5a6f7c3af23cc4e901d3c49236d98184c6b570ea`
- **`main` == `origin/main` == `5a6f7c3af23cc4e901d3c49236d98184c6b570ea`**;
  worktree em `main`, sem trabalho pendente.
- **O Alladin passou a registrar fato econômico.** `S.alladin.transactions[]`
  com `DEPOSIT`, `WITHDRAWAL`, `TRANSFER` e `REVERSAL`; `POSTED` economicamente
  imutável e correção por reversão; saldo **sempre derivado** e fail-closed —
  não existe `CashAccount.balance` (ALD-I27). `schemaVersion` **3**: barreira de
  escrita, não migração de dados — um build v2 preserva a coleção que não
  conhece, mas entra em `READ_ONLY_FUTURE_SCHEMA` em vez de escrever sobre ela.
- **Cadeia publicada:** `39acdc6` (C3 concluído e integrado) → `c8c3190`
  (endurecimento pré-ledger: rollback do changeLog por conteúdo e import
  fail-closed) → `982fb7e` (marca do cabeçalho abre o Dashboard) → `5a6f7c3`
  (Cash Ledger).
- **Readiness:** `validate_project` PASS com 77 scripts e 429 IDs; `fast` 4/4,
  `standard` 38/38 e `full` **49/49**.
- **CI Run #32** (`5a6f7c3`): vermelho por `ENVIRONMENT_ERROR` em
  `session-epoch-protocol`, com `PASS=37`, `PRODUCT_FAIL=0` e
  `TEST_HARNESS_FAIL=0`. A suíte nova `alladin-ledger` **passou no runner
  Ubuntu**, assim como foundation, preservação, CRUD e leitura. Não é verde, não
  está resolvido, não é regressão de produto e não é atribuível ao Alladin.
- **Dívidas abertas:** QA-D1 · QA-D2 · `session-epoch-protocol` ·
  comentário "SOMENTE LEITURA" em `index.html`. QA local: orientação sobre
  cache de service worker registrada em `QUALITY-GATES.md`.
- **Próxima fronteira:** `ALD-03-S2` — `BUY`/`SELL`, `FEE`, `ADJUSTMENT` e o par
  atômico papel↔caixa. **Não autorizado.**


## Navegação — marca JP Wealth abre o Dashboard — candidato SUPERSEDIDO — 2026-08-29

> [!note] Este candidato não foi publicado
> O que segue descreve um candidato produzido em worktree que continha, ao mesmo
> tempo, trabalho não commitado do Alladin. **Ele nunca foi commitado.** A
> implementação definitiva da marca foi refeita sobre base limpa e publicada em
> `982fb7e`. O registro permanece por dois motivos: o agente identificou a
> contaminação e recusou-se a atribuir a si alterações alheias, e a QA daquela
> sessão produziu o achado sobre cache de service worker, hoje registrado em
> `QUALITY-GATES.md`. O `standard 38/38` citado abaixo **não é evidência isolada
> da logo** — foi medido com as suítes do Alladin presentes na árvore; a
> evidência válida da implementação publicada foi `standard` **37/37**, obtida
> depois em worktree limpo.

- Branch `codex/logo-link-dashboard`, `BASE_SHA`/`HEAD`
  `c8c31908e2bccbdb3a62e45c1b0ec4f6384cad9b`; candidato ainda sem commit.
- A marca do header agora é `button#brandHomeBtn`, com nome acessível, foco
  visível e alvo mínimo de 44 px. Clique, Enter e Espaço atravessam a rota
  canônica `dashboard`; a marca não cria nova rota nem escreve em estado ou
  storage.
- Build portátil regenerado pelo mecanismo oficial, ID
  `52a00fcfbd362f24`; manifest preserva 77 scripts e atualiza somente o hash do
  controlador de navegação alterado. `validate_project` PASS com 429 IDs.
- Teste focado PASS com Python 3.12.13/Playwright 1.60.0. Tier `standard`
  final: **38/38 PASS**, relatório
  `tools/.artifacts/quality-20260829T163558-standard.json`.
- Browser real PASS em 1440×900 e 390×844, temas escuro/claro: clique leva de
  Research/Alladin ao Dashboard, foco visível, zero overflow e zero erro de
  console. A primeira origem `127.0.0.1` expôs cache antigo do service worker;
  a QA do candidato foi confirmada em origem local limpa `localhost:8000`.
- As 13 alterações Alladin/ledger que já existiam antes desta tarefa foram
  confirmadas pelo gestor como suas, preservadas e mantidas fora do escopo
  lógico do logo. Elas ainda divergem das representações C3 abaixo e não foram
  reconciliadas, reinterpretadas nem autorizadas por esta mudança N1.
- Commit, push, merge e deploy não foram executados nem autorizados.

## Alladin C3 — cadastro patrimonial CONCLUÍDO E INTEGRADO — 2026-08-29

- Data da fotografia: 2026-08-29
Source revision representada: `39acdc68b40bcae7d81ac3b702fd20dd77cdff57`
- **`main` == `origin/main` == `39acdc68b40bcae7d81ac3b702fd20dd77cdff57`**: o C3
  foi integrado por **fast-forward** (sem merge commit) e publicado.
- Branch `fix/alladin-session-preservation`: local == `origin` == `39acdc6`,
  **convergida com a `main` — zero commits exclusivos**. Deixou de ser a linha
  ativa do ciclo; o worktree dedicado continua nela por conveniência operacional.
- **O C3 está CONCLUÍDO.** O Alladin deixou de ser destino sem função: as quatro
  entidades cadastrais têm leitura, criação, edição e ciclo `recordStatus` pela
  interface real, e toda mutação atravessa `JPWAlladin.cadastro` — a UI nunca
  escreve em `S`, nunca chama `save()` e nunca toca `localStorage`.

| Entidade | leitura | create | edit | recordStatus |
|---|---|---|---|---|
| Instrument | ✅ | ✅ | ✅ | ✅ |
| Asset | ✅ | ✅ | ✅ | ✅ (+ `lifecycleStatus` somente-leitura) |
| Account | ✅ | ✅ | ✅ | ✅ |
| CashAccount | ✅ | ✅ | ✅ | ✅ |

- **Cadeia do ciclo:** `1501d46` (C3-PRE + protocolo de geração; a mensagem do
  commit não descreve o conteúdo) → `dc8a3ec` (reconciliação com a Navigation)
  → `c2819af` (serialização cross-tab da escrita) → `94c383e` (C3-S1, leitura)
  → `d9bd71b` (salvaguardas pré-escrita) → `e5d6f36` (C3-S2-A) → `a725302`
  (C3-S2-B) → `f5124f4` (C3-S2-C, integridade da edição).
- **Blockers do primeiro Closure, todos fechados no S2-C:** `B-1` a rede de
  cripto não desaparece mais ao trocar de família; `B-2` valor de vocabulário
  fechado que este build não conhece é preservado e nunca normalizado em
  silêncio; `B-3` a recusa não apaga mais o rascunho de Account/CashAccount;
  `F-1` os rótulos de `lifecycleStatus` são exatamente o catálogo do domínio.
- **Fronteira congelada:** o C3 responde *"o que existe?"*. `ALD-03` responderá
  *"o que aconteceu economicamente?"* — ledger, transações, posições, saldos,
  valuations, patrimônio e performance. **Nada disso existe hoje**, nem como
  zero, e o ALD-03 **não está iniciado nem autorizado**.
- **Readiness:** `validate_project` PASS com 77 scripts e 428 IDs; `fast` 4/4,
  `standard` 37/37 e `full` **48/48 PASS**.
- **Dívidas de harness abertas** (caracterizadas, não corrigidas, e sem relação
  com o produto): **QA-D1** — o caso N de `alladin_ui_readonly_test.py` observa
  o documento inteiro enquanto `updateFxRates` escreve nele por conta própria;
  com o relógio de cotação ativo 1 em 6 execuções acusa, com ele neutralizado
  nenhuma acusa, e a escrita aparece também no controle que não toca no Alladin.
  **QA-D2** — `finalize_session_test.py` falha sob carga do tier num assert do
  Galton (`currentSpeed`); passa isolado e na baseline, causa não fechada.
  Corrigi-las é slice de harness próprio, jamais oportunismo dentro de outro.
- **CI do push da `main` (Run #28, tier `standard`, commit `39acdc6`): VERMELHO
  por erro de ambiente.** `PASS=36 · PRODUCT_FAIL=0 · TEST_HARNESS_FAIL=0 ·
  ENVIRONMENT_ERROR=1 · BASELINE_FAIL=0 · NOT_RUN=0`; a única falha foi
  `session-epoch-protocol`, classificada pelo próprio quality gate como
  **ENVIRONMENT_ERROR**. O runner conferiu: checkout `39acdc6`, Python 3.12.14,
  Playwright 1.60.0, Chromium instalado, e a falha veio depois de dezenas de
  suítes verdes. As suítes do Alladin passaram — `alladin-ui-readonly`,
  `alladin-ui-crud`, `alladin-finalize-preservation` e
  `session-write-serialization` todas PASS, e **QA-D1 não disparou**. O erro
  **permanece aberto**: não é regressão de produto, não é QA-D1 nem QA-D2, não
  é atribuível ao Alladin, e não está resolvido.

## Navigation — pós-merge final reconciliado — 2026-08-26

- **Base desta reconciliação:** `main` em
  `75d10bcb3dc02c1a62a369df6cc1cd17387488ec`, integração Navigation concluída
  por fast-forward. O presente checkpoint doc-only é filho direto dessa base e
  passa a ser a ponta local de `main` após o commit.
- **Histórico integrado:** NAV-01 `e2c34bb4c4ac0c0f7a2746ca4687c6a61f64f06d`,
  NAV-02 `9b5ea298953b3c8bb270864151a88e5c69419e61`, NAV-03
  `2c1e0a441d77e01c8c9acaf0506da333254c8196` e NAV-06A
  `75d10bcb3dc02c1a62a369df6cc1cd17387488ec`.
- **Produto:** cinco primários — Dashboard, Forex, Finanças Pessoais, Research
  e Alladin. Forex contém Visão Geral, Preparação, Conta, Operação, Apuração e
  Planejamento. Research contém Forex, Ações, Stocks, REITs e Others;
  Research/Forex contém Calendário, NoCoda e Pivots. Alladin permanece como
  placeholder estrutural e seu desenvolvimento funcional continua pausado.
  Galton permanece em Configurações.
- **Readiness:** runtime PASS; `validate_project` PASS com 76 scripts e 415 IDs;
  full **43/43 PASS**. O commit final desta reconciliação altera somente contexto
  operacional, sem invalidar as evidências de produto, browser ou PWA.
- **Git/publicação:** merge local concluído; `origin/main` permanece em
  `1eddd29ee73d3e8fbc1713e073a0c22ce71350ab`. Push e deploy estão pendentes e
  não foram executados.
- **Alladin:** worktree `fix/alladin-session-preservation` em `1eddd29e`, com
  12 arquivos modificados e três não rastreados; zero drift.
- **Coerência sistêmica:** os contextos operacionais afetados pelo merge foram
  reconciliados neste checkpoint; `SYSTEM RECONCILED = SIM`.

## NAV-03 — checkpoint interno commitado de Research Consolidation — 2026-08-26

- **BASE_SHA/commit:** `9b5ea298953b3c8bb270864151a88e5c69419e61` →
  `2c1e0a441d77e01c8c9acaf0506da333254c8196`, em `codex/navigation-ia`.
- **Contrato:** cinco primários preservados; `children('research')` expõe
  exatamente Forex, Ações, Stocks, REITs e Others. Research/Forex abre
  Calendário por default e possui somente Calendário, NoCoda e Pivots no N3.
- **Ownership:** `execEcal`, `execNocoda` e `execPivots` existem uma vez sob
  `section#research`; aliases históricos ativam Research/Forex/N3 e Exec retém
  somente overview, panel, motor e history como views canônicas.
- **Empty states:** Ações abre Brasil/B3 diretamente; Stocks, REITs e Others são
  neutros e não contêm métricas, números econômicos ou conteúdo funcional.
- **Galton:** permanece em Configurações, sem mudança de lifecycle, DOM,
  preferências, storage ou código funcional.
- **Persistência e Alladin:** nenhuma chave/rota persistida, zero escrita por
  navegação e nenhum acesso a `S.alladin`/`JPWAlladin`; worktree Alladin isolado.
- **Evidência corrente:** focais Research, Navigation IA, Exec/Calendário,
  NoCoda, Pivots e Settings/Galton PASS; `validate_project` PASS (76 scripts,
  415 IDs); fast **4/4 PASS**, standard **32/32 PASS** e full **43/43 PASS**.
  Browser pós-full PASS em desktop/mobile, claro/escuro, teclado, foco, N2/N3,
  hidden/inert, overflow e alvos móveis ≥44 px. PWA PASS em manifesto, hashes,
  precache, upgrade do service worker e reprodutibilidade do build oficial
  `aaa2262ae6fb0610`.
- **Git/publicação:** commit interno `2c1e0a4`; push, merge e deploy não foram
  autorizados nem executados.

## NAV-02 — checkpoint interno commitado de Forex Consolidation — 2026-08-26

- **BASE_SHA:** `e2c34bb4c4ac0c0f7a2746ca4687c6a61f64f06d`.
- **Branch/worktree:** `codex/navigation-ia`, worktree dedicado Navigation IA.
- **Contrato:** `routes()` mantém cinco primários; `children('forex')` expõe
  exatamente Visão Geral, Preparação, Conta, Operação, Apuração e Planejamento.
- **Estrutura:** sem `section#forex`, sem rename de `execNavTrigger`/
  `execNavSubmenu`; terceiro nível contextual reutiliza `JPWExec.ui` e
  `JPWFx.ui` sem estado paralelo.
- **Compatibilidade:** `motor`/Operação, `history`/Apuração, `fxplan`/Planejamento
  com visão corrente; `check`/Preparação e `tool-check`/Settings separados.
  Calendário, NoCoda e Pivots funcionam com `child:null` até o NAV-03.
- **Persistência e Alladin:** nenhuma chave/rota persistida; a navegação não
  chama `save()` nem toca `S.alladin`/`JPWAlladin`.
- **Evidência corrente:** build `3d51c530db465831`; seis focais NAV-02 PASS;
  `validate_project` PASS (75 scripts, 409 IDs); fast **4/4 PASS**; full
  **42/42 PASS**; browser pós-full PASS em desktop/mobile 390×844,
  claro/escuro, teclado, níveis 2/3, overflow e targets ≥44 px.
- **Git/publicabilidade:** commit interno `9b5ea298`; NAV-02 isolado não é
  publicável. Push, merge e deploy não foram autorizados.

## NAV-01 — checkpoint interno commitado de fundação semântica — 2026-08-25

- **BASE_SHA:** `1eddd29ee73d3e8fbc1713e073a0c22ce71350ab`.
- **Branch/worktree:** `codex/navigation-ia`, worktree dedicado Navigation IA.
- **TARGET CANÔNICO:** cinco primários — Dashboard, Forex, Finanças Pessoais,
  Research e Alladin.
- **CANDIDATO NAV-01:** registry público estrito, fachada de compatibilidade,
  cinco botões, `section#research` e placeholder estático `section#alladin`.
- **ESTADO PUBLICÁVEL:** ainda depende de NAV-02. NAV-01 isolado é auditável,
  mas não pode substituir o estado utilizável, ser mergeado ou publicado.
- **Persistência e Alladin:** nenhuma chave/rota persistida; a navegação não
  chama nem altera `S.alladin`, `JPWAlladin` ou `save()`.
- **Git/publicação:** commit interno
  `e2c34bb4c4ac0c0f7a2746ca4687c6a61f64f06d`; push, merge e deploy não foram
  autorizados nem executados.
- **Evidência desta fotografia:** rebuild oficial `eba48d278c6a5b58`; suíte
  `navigation_ia_test.py` e quatro focais PASS; `validate_project.py` PASS (75
  scripts, 409 IDs); tier full **42/42 PASS**. Chromium real cobriu desktop e
  mobile a 390 px, temas claro/escuro, foco/teclado e zero overflow horizontal.
  O teste N1-C mediu alvos móveis de 40 px e justificou o 26º arquivo
  condicional, `src/styles/app.css`; depois da correção, os cinco medem 44 px.
  Blast radius final: exatamente 26 arquivos.

- Data da fotografia: 2026-08-21
Source revision representada: `4d130faa44187ceb81ed35bce15425a9dc2e78c9`
- Branch atual: `main` (`main` = `origin/main` = `4d130fa`)
- **Integração contínua, pela primeira vez** (2026-08-17, merge `91687dc`):
  `.github/workflows/quality-gate.yml` restaurado de `045c264`, preservado na
  tag `archived/governanca-multiagente`. Até aqui `.github/` só tinha
  `pull_request_template.md`. **Atualização de 2026-08-20:** `main` já foi
  publicada com o workflow diversas vezes (pushes `fc29731`, `c6c1aa3`,
  `46bb776`, `29aca32` e `4d130fa`, verificados read-only desta máquina), logo o gatilho `push: main`
  ocorreu; **os resultados das execuções no GitHub não são verificáveis deste
  ambiente** (sem credencial para a API — `gh` indisponível). Detalhe na seção
  própria abaixo.
- Commit material anterior: série `b65dad3 → 6eee442` na branch
  `feature/exec-economic-calendar`
- **Calendário Econômico no Execution Board** (2026-08-17): terceiro destino do
  submenu, entre Painel Operacional e as ferramentas de estudo. **Um domínio,
  três superfícies** — workspace canônico `#execEcal`, projeção diária no card do
  Dashboard e o overlay `#ecalOverlay` com seus dois pontos de entrada
  preservados. Nenhuma duplicação de fetch, cache, sanitização, timers de
  domínio, identidade de evento ou regras de impacto. Detalhe no `CHANGELOG.md`;
  estado de verificação na seção própria abaixo.
- Anterior — commit material: `6964ab6` + `87019b6` na branch
  `fix/docs-script-count-drift`, integração `df964b9`
- **Reconciliação do drift documental** (2026-08-17): contagens defasadas e o
  parágrafo de acessibilidade do Planejamento FX. **Documentação apenas** —
  nenhum arquivo de runtime, teste, manifest, worker ou gerado foi tocado, e por
  isso nenhuma evidência anterior de gate foi invalidada. Detalhe no
  `CHANGELOG.md`; resumo na seção própria abaixo.
- Anterior — commit material: `ed92925` na branch `fix/bug-hunt-findings`,
  integração `a7183646a5be26fac5f422702cec4fb8a12c8053`
- Também integrado: `cdb5b50` na branch `fix/gate-timing-determinism`
  (merge `b1d0ab29c10aaf6ddf12276f03df781bd48ba0a6`)
- Submenu Estudos dos Pivots: integrado em `main` (`7a93602`, merge `a188f29`,
  reconciliação `f1c1f36`).
- Estado de publicação **em 2026-08-17** (registro do episódio; não descreve o
  remoto de hoje): `origin/main` estava em `c5b0b86`, de modo que **toda a
  série de submenus, inclusive os Estudos dos Pivots, já havia sido publicada** —
  o registro anterior de "push não executado" descrevia a sessão que o escreveu,
  não o estado do remoto. Somente os três commits daquela reconciliação
  (`6964ab6`, `87019b6`, `df964b9`) estavam à frente e aguardavam push do gestor.
  Ressalva daquele momento: a comparação usou o ref local de `origin/main`;
  `git fetch` falhou naquela máquina por ausência de credenciais, então o remoto
  ao vivo não foi consultado. O teste manual em navegador seguia pendente — o
  gestor autorizou merge e commit sem essa etapa.
- Correções de segurança dos três achados `Medium`: integradas em `main`
  (`4635794`, merge `dc55120`, reconciliação `f0aac02`) e publicadas.
- Migração do Motor de Lote: integrada em `main` (`792b705`, merge `043da1b`,
  reconciliação `a5d7b93`) e publicada pelo gestor.
- Histórico já em `origin/main`: segundo nível do Execution Board
  (`d2ad73f` → merge `83a18dd` → `60070a2`) e Estudos NoCoda
  (`c3c5f21` → merge `af229ad` → `60ec561`). Nenhum `git push` foi executado
  nesta sessão em momento algum — a publicação saiu por GitHub Desktop ou por
  outra sessão no mesmo checkout.
- Build local: `fa5b65ae5dd68125` — **inalterado**, porque nenhuma fonte mudou.
- Validade: qualquer mudança posterior em fonte, manifest, worker, testes ou
  gerados invalida as evidências afetadas e exige repetir o gate proporcional.

## Alladin — Fundação C1 e Modelo Cadastral C2 — 2026-08-20 a 2026-08-21

O domínio **Alladin** (Sistema Patrimonial e Consolidador de Investimentos;
ex-roadmap `INV-*`, renomeado pela spec canônica JPW-ALLADIN-SPEC V1.2.1,
externa ao repo) existe no produto com **duas camadas cadastrais**: a
infraestrutura (C1) e o modelo cadastral (C2). Contrato do domínio em
`docs/architecture/ALLADIN.md`. Cadeia de proveniência integral, cada elo
verificado por fingerprint:

| Etapa | Identificador |
|---|---|
| ALD-01 C1 candidate (fingerprint) | `fe616a7caf709faf3d62b9d2bbc93c0669a869bb4e371c02154766998555038a` |
| ALD-01 C1 — commit / merge | `85d1911` / `c6c1aa3` |
| Reconciliação documental C4-A (merge) | `46bb776` |
| ALD-02 C2 candidate (fingerprint) | `66ebf8401b123381a2d71dd3a63eafc5b21db21603f782b8368cf0d550e7bb7d` |
| ALD-02 C2 — commit / merge | `beea842` / `29aca32` |
| Reconciliação documental C4-C2-A (merge) | `4d130fa` |

**O que existe (C1 — infraestrutura):** agregado `S.alladin`, hoje em
**`schemaVersion 2`**; `alladinNormalizeState()` em `migrate()` com fail-closed
para versão futura legível (inteiro ou string de dígitos — agregado
byte-intacto, todo ato recusado, incompatibilidade exposta em
`JPWAlladin.compat()`) e cadeia de migração a partir da versão mais baixa;
dinheiro `{amount, currency}` em unidade mínima inteira (schema ISO 4217
aberto; runtime BRL/USD extensível por dado); `aldId`; write gate `aldMutate`,
agora **transacional** — snapshot antes do ato e restauração do agregado e do
`changeLog` quando `save()` recusa.

**O que existe (C2 — modelo cadastral):** as quatro entidades — `Instrument`,
`Asset`, `Account`, `CashAccount` — com atos de criação, edição e ciclo
cadastral `ACTIVE↔INACTIVE`. Account **é** a custódia financeira (custódia
física em `Asset.location`; não existe entidade `Custody`);
`owners[{name, shareBp, isSelf}]` com no máximo um `isSelf`, o que torna o valor
proporcional do operador computável sem inferência; três regimes de
classificação (fechado só onde há mandato normativo; `accountType`, `nature`,
`strategicPurpose` e `assetClass` são starter e aceitam valor novo); **dinheiro
líquido nunca é Asset** — invariante de runtime, não convenção; duplicidade
avisa e o registro nasce, com cripto exigindo `network`, que integra a chave de
identidade; `symbolHistory` append-only, e histórico ilegível recusa a edição
em vez de ser destruído; integridade referencial **hierárquica** (cash account
ativa exige conta ativa; a recíproca não vale). Migração v1→v2 é apenas o
carimbo da versão.

**Verificação:** duas suítes no tier `standard` — `alladin-unit` (U1–U21, em
Chromium isolado, sem app, sem DOM de produção, sem rede) e
`alladin-foundation` (migração v1→v2, round-trip com as quatro coleções
povoadas, fail-closed, **rollback duplo** — build pré-Alladin `fc29731` e build
do C1 `3f1f9bc` —, reload real, falha parcial em validação e em persistência
recusada, XSS/privacidade e round-trip de backup). Full 41/41 nos candidatos e
nas `main` integradas. Auditoria independente: no C1, zero graves e quatro
moderados; no C2, **três graves e dez menores**, todos corrigidos e re-testados
antes do commit.

**O que NÃO existe** (estado real, não desejado): transações, eventos, ledger,
holdings, posições, cost basis, valuation, performance, allocation, renda,
passivos patrimoniais, benchmark, UI e integrações Trading/PF/FX — **nada do
domínio econômico foi iniciado**. `ALD-03` (estado derivado) e `C3` (UI) não
autorizados.

> [!note] Superado em 2026-08-29 quanto à UI
> O parágrafo acima descreve o estado de 2026-08-21 e fica preservado como
> registro daquele momento. O **C3 foi autorizado, implementado e concluído**
> — ver a seção do topo. O que permanece verdadeiro é a metade econômica:
> transações, ledger, posições, valuation e performance continuam inexistentes,
> e o `ALD-03` segue não iniciado.

> [!note] Superado novamente em 2026-08-30 quanto ao ledger
> A afirmação acima sobre a "metade econômica" era verdadeira em 2026-08-29 e
> deixou de ser: o **ALD-03 S1/S2 está publicado** — transações de caixa e
> trades `BUY`/`SELL` existem, com saldo derivado. O que continua inexistente
> são posições, cost basis, valuation e performance — ver a seção do topo.

> [!note] Superado quanto às posições — ALD-04-S1 (2026-08-31)
> Posição por quantidade agora **existe** como read-model derivado
> (`JPWAlladin.leitura.posicoes()`), sem persistência. Continuam inexistentes:
> holding persistido/consolidado, cost basis, valuation/current value, P&L e
> performance.

**Resíduos registrados:** `ALD-I26` (Audit Trail) deferred ao ALD-07 por
decisão HD-6 — `dgLogChange` é log operacional não-canônico; referências
`INV-*` em comentários de código (`index.html:188/1044`,
`22-finpes-overview.js:11-12`, `12-personal-finance.js:493`) permanecem —
deferred, gate dedicado futuro, impacto nenhum; branches preservadas como
evidência histórica — `feature/alladin-foundation-c1`,
`feature/alladin-cadastral-c2`, `docs/alladin-c4-reconciliation`,
`docs/alladin-c4b-current-state` e `docs/alladin-c4-c2-reconciliation`
(FEATURE-CLEANUP-GATE futuro decidirá).

## Finanças Pessoais V1 — 2026-08-18 a 2026-08-19

Oito entregas integradas e publicadas em `origin/main`, em série sobre `main`:

| Entrega | Candidate | Merge |
|---|---|---|
| PF-01 Fundação (N2) | `49027c2` | `59a9681` |
| PF-02 Orçamento Mensal (N3) | `c52c52f` | `f6a7ffe` |
| PF-03 Dívidas & Crédito (N3) | `4ce3b4f` | `73bdaab` |
| PF-04 Comparativo Mensal (N3) | `e2509d7` | `bc6752a` |
| PF-05 Cenários (N3) | `aa0baa1` | `46dcbe6` |
| PF-06 Visão Geral (N1 condicionado, conduzido como N3) | `2377584` | `1a13a91` |
| PF-CLOSE-01 fronteira do domínio | `bd89c84` | `ff4cf3d` |
| PF-CLOSE-02 consistência da leitura monetária | `05aa41b` | `4b86bc6` |

**Estado funcional.** O módulo tem cinco destinos — Visão Geral, Orçamento
Mensal, Dívidas & Crédito, Comparativo Mensal e Cenários. O agregado
`S.personalFinance` permanece em `schemaVersion 1` congelado (`BRL_CENTS`,
inteiros em centavos), com nove suítes no tier `standard`. Nenhuma das entregas
introduziu campo persistido derivado: totais, coberturas, sobras, ratios e
utilização são recalculados a cada render.

**Fronteira do domínio.** Inventário e Patrimônio **não** pertencem a Finanças
Pessoais. A decisão de produto de 2026-08-19 os moveu para domínio próprio com
roadmap independente `INV-*` — desde 2026-08-20 nomeado **Alladin** (roadmap
`ALD-*`; fundação integrada, ver seção acima); `PF-07` e `PF-08` não existem. `PF-CLOSE-01`
removeu do runtime o submenu, o workspace `#finpesInventario`, a entrada em
`FINPES_VIEWS` e os dois placeholders que anunciavam esse futuro, sem perda de
métrica financeira. Resíduo conhecido: o comentário sobre `inventoryAssetRef`
em `src/js/10-domain/12-personal-finance.js:493` ainda cita PF-08 — comentário,
não contrato executável, reservado a gate próprio.

**Desvio de governança registrado.** `PF06-PROTOCOL-DEVIATION-01` — o push de
`1a13a91` para `origin/main` ocorreu fora da execução controlada do gate
(out-of-sequence external push). Impacto funcional e de integridade: nenhum —
o conteúdo remoto foi verificado idêntico ao candidate aprovado. Impacto de
governança: procedural. Nenhuma remediação destrutiva foi aplicada.

## Operação Única — Histórico e Finalização formal — 2026-08-17

Branch `feature/exec-operation-history`, série `c9fd11e → 17214ba`.
**Integrada** — candidate final `27a87cf` (rodadas corretivas posteriores a
`17214ba`), merge `--no-ff` `9ac5a8a` em `main` (2026-08-18). A afirmação
anterior ("Não integrada: aguarda tier full, inspeção visual humana e
autorização de merge") descrevia o estado de 2026-08-17 e ficou defasada.

**O que passou a existir.** A Operação Única deixou de ser um conceito implícito
nas grades e virou entidade persistida (`activeOperation`), com finalização
transacional e memória institucional (`operationHistory`) consultável no sétimo
workspace do Execution Board.

O ato central é a distinção que o Estatuto já fazia e o software não: **fechar a
última ordem não finaliza a Operação**. O Art. 4.4 diz textualmente que zeragem
tática sem confirmação escrita não a extingue, e prescreve dupla confirmação por
registro escrito `FECHADO` — que é exatamente o protocolo implementado na
revisão de finalização.

**Arquitetura em três camadas**, autorizada como opção B: fundação (entidade
persistida), finalização transacional (`candidato → validar → trocar → save() →
rollback`) e Histórico somente leitura. `cycleRealizado` manteve semântica
intocada; a consolidação existente foi incorporada ao fluxo transacional sob
autoridade A4 delimitada.

**Série corretiva após revisão adversarial.** Uma revisão por 24 agentes acusou
um BLOCKER de fiação e sete defeitos materiais. Todos corrigidos, cada um em
commit próprio, com campanha de mutação individual:

| item | commit | mutações |
|---|---|---|
| trilha de auditoria dentro do commit | `1a0c40c` | 7 |
| revisão igual ao snapshot persistido | `ba3be3a` | 19 |
| consistência temporal (`openedAt <= closedAt`) | `a21dcd8` | 10 |
| busca do Histórico deixa de destruir o próprio campo | `bfc2b59` | 5 |
| exclusividade da tese vale até a finalização formal | `f64cea2` | 8 |
| integridade da Fase da Conta com três estados | `be43dde` | 7 |
| citações penduradas na guarda de exclusividade | `17214ba` | — |
| **desfecho da gravação com três estados** | `e7313aa` | 9 |

**Segunda rodada corretiva — auditoria adversarial de nove lentes.** Ela devolveu
`AUDIT_FAIL` com 16 achados, 13 invalidantes, que colapsavam em três defeitos.
Todos produziam afirmação falsa em registro imutável:

| item | commit | mutações |
|---|---|---|
| **C** captura da Fase da Conta só em ato confirmado | `e6f653d` | 4 |
| **B** operação nasce antes dos efeitos que lhe pertencem | `58be507` + `fc25e7b` | 3 |
| **A** exclusão da última ordem abandona; órfã não é herdada | `13b9811` | 4 |
| **C×A** captura depois de resolvido o ciclo de vida | `d161207` | 3 |

**Terceira rodada — as regressões da própria correção C.** A auditoria dirigida a
C, B e A encontrou três caminhos em que a captura, retirada de `save()`, não
havia sido reposta:

| item | commit | mutações |
|---|---|---|
| **R1** breach que compromete o stop observa a fase | `ffa637a` + `c2b17c5` | 3 |
| **R2** status devolvido a não operacional retira a ordem | `356fe37` | 4 |
| **R3** Fase da Conta observada antes da revisão | `d328e2b` + `b5b5766` | 3 |
| **R4** troca de Par aceita observa a Fase da Conta | `ca301de` | 3 |

`480e7a2..ca301de` são **11 commits**, e nenhum deles tocou este arquivo nem o
`CHANGELOG` — a reconciliação documental que os cobre é a deste checkpoint.

**Reclassificação do R4, decidida pelo humano contra o parecer da auditoria.** O
achado de `04-stop-statistics.js` na saída terminal do laço de `<select>` havia
sido rebaixado a dívida, com o argumento de que o sítio é byte-idêntico antes e
depois de R1/R2/R3. O argumento prova apenas que não é regressão *daqueles*
patches. Como é **esta feature** que torna `maxAccountPhaseReached` dado
histórico imutável, qualquer caminho de uso ordinário capaz de subestimá-lo é
defeito do candidato: `PRODUCT_DEFECT`. Medido nos defaults de fábrica com saldo
40.000, trocar `USDJPY` por `EURUSD` numa ordem aberta leva o risco de 15,44 para
2.500 USD — drawdown de 6,25% contra teto de 4% da Fase 1 —, a conta opera na
Fase 2 no disco e na tela, e o máximo permanecia em zero.

**O princípio de C, completo depois de R1 e R4:**

```
valor transitório / digitando        -> não captura
guarda rejeita e reverte             -> não captura
valor sobrevive à guarda e persiste  -> CAPTURA
```

`operationTouchAccountPhase` nunca voltou para `save()`. Os oito sítios de
captura são todos atos semanticamente confirmados.

**Correção de rótulo, registrada porque o erro foi de método.** `be43dde` foi
commitado como se fosse o item #8 da fila e não era. Ele trata da integridade
ternária da **Fase da Conta** (`observed` / `unobserved` / `degraded`) e
permanece válido como hardening próprio. O #8 da fila era o **desfecho da
persistência**, corrigido em `e7313aa`.

A troca ocorreu após uma compactação de contexto. Eu havia perdido o
enunciado, declarei isso — e então formulei perguntas sobre o ternário errado,
tendo encontrado um ternário legítimo no código e o assumido como sendo o da
fila. As respostas confirmaram recomendações minhas sobre um assunto que não era
o item pendente, o que deu à correção uma aparência de validação que ela não
tinha. Perguntar sobre a coisa errada não é o mesmo que perguntar.

**92 experimentos de mutação ao longo das três rodadas**, todos acusados por
asserção própria ou registrados como no-op provado. Nenhum foi aceito por
`TypeError`. Treze precisaram de correção antes de valer como evidência: testes
que detectavam por exceção em vez de asserção, mutações infiéis (uma quebrava a
construção do modal, outra era inócua contra o caso escolhido), duas pareadas
com a função errada, uma que dependia de instrumentação herdada de outro teste, e
uma cuja igualdade passava sem haver observação alguma — revisão e registro
empatando em `null`.

Cinco sobreviventes ficaram registradas como **no-op provado**, não como lacuna:
anular `jaFinalizada` não produz duplicação porque três autoridades independentes
barram antes; a guarda `S.activeOperation &&` na captura é redundante depois de o
ciclo de vida estar resolvido; captura duplicada entre checkpoint e confirmação
não tem efeito porque a fase não muda entre os dois instantes; e capturar no
caminho revertido observa o valor já restaurado.

**Categoria de teste criada nesta série.** Um defeito de fiação passou por
testes unitários verdes: o gancho estava num laço morto (`querySelectorAll('input')`,
enquanto Status é um `<select>`). Ficou provado empiricamente que reintroduzir o
defeito faz o teste de fiação FALHAR enquanto o unitário PASSA. Daí
`operation_wiring_test.py`: evento real de DOM → domínio → estado → disco.

**Achado normativo.** A varredura das citações do código contra os 92 artigos da
Norma Vigente acusou **oito numerações penduradas** — `Art. 1.3, 3.5, 3.6, 3.7,
3.8, 3.10, 8.6, 9.5` — em doze arquivos. A Norma tem `3.1-3.4`, `8.1-8.5` e
`9.1-9.3`. Só foram corrigidas as três da guarda de exclusividade, únicas com
evidência textual do correspondente vigente. As demais seguem pendentes, na
seção de pendências.

**O defeito mais grave da série** foi o último. A sonda que decide o destino de
uma finalização devolvia booleano, e um `catch(_){ return false; }` transformava
leitura impossível em prova de ausência. Dali saía a perda silenciosa: `setItem`
grava, uma exceção posterior interrompe o fluxo, a leitura de volta falha, o
sistema conclui "não gravou", a memória volta para a operação ativa e o próximo
`save()` sobrescreve o disco — memória e disco discordando sobre se uma operação
financeira foi formalmente encerrada. Contrato em `DB-STORAGE-GOVERNANCE.md`,
regra 7.

**Evidência do candidato `ca301de`.** Gate `standard` 17/17 em cada commit da
série e tier `full` **28/28**, ambos lidos integralmente, com o artefato do
`full` registrando `head: ca301ded4c3c` — a verificação cobre o candidato exato,
e não uma aproximação dele.

**Vereditos de auditoria, em ordem:** `AUDIT_FAIL` (nove lentes, 13 invalidantes
→ C, B, A); `AUDIT_FAIL` (dirigida, 6 invalidantes → R1, R2, R3);
`AUDIT_PASS_WITH_DEBT` (dirigida a R1/R2/R3, 4/4 lentes, zero invalidantes, uma
dívida que o humano reclassificou como defeito → R4). A lente de interação
`R4×C` concluiu com zero achados.

**Lente `R4` independente — dispensada por waiver explícito.**

```
R4 independent audit:
NOT_EXECUTED / INFRASTRUCTURE_BLOCKED

causa:
quatro tentativas consecutivas encerradas por 529 Overloaded,
sem produção de evidência sobre o produto.

decisão:
waiver explícito aprovado pelo responsável;
a lente R4 independente NÃO permanece como gate pendente
para Human Acceptance ou integração.
```

**Taxonomia, para que não se leia o que não está escrito: `waiver ≠ AUDIT_PASS`.**
A lente não foi executada com sucesso em nenhuma das quatro tentativas — foi
dispensada conscientemente, pela indisponibilidade persistente da infraestrutura
e pela suficiência das evidências alternativas. Nenhuma das quatro falhas
produziu informação sobre o candidato, nem a favor nem contra.

Base objetiva do waiver:

```
R4 interface tests       3/3 PASS
mutation                 2 killed + 1 proven no-op
standard                 17/17 PASS
full                     28/28 PASS sobre ca301de
R4×C                     concluída, zero achados
```

As três propriedades que a lente tentaria falsificar — captura do pico na troca
aceita, monotonicidade no recuo, e não-contaminação na troca revertida — são
exatamente as três cobertas pelos testes de interface e provadas detectáveis pela
mutação dirigida. A lente seria uma quarta camada independente, por leitura de
código, e não a única evidência.

**Uma sessão futura não deve reabrir a R4 como gate.** Se houver motivo novo para
executá-la, isso é decisão nova, e não continuação de pendência.

**Estado do desenvolvimento.**

```
DESENVOLVIMENTO DO HISTÓRICO ENCERRADO
próximo gate = HUMAN ACCEPTANCE
```

Não há etapa técnica pendente antes da inspeção humana. Depois dela: integração
controlada, merge em `main`, validação pós-merge, e push somente com autorização
expressa.

**Fragilidades do harness, registradas e não corrigidas.** `nocoda_test.py`
(`run_no_operational_mutation`) falhou uma vez num `full` que competia com quatro
agentes de auditoria pela máquina, e passou 9/9 isolado, no `standard` e no
`full` sem carga: `TEST_HARNESS_FAIL` por sensibilidade temporal, com mecanismo
não identificado. O script de auditoria devolvia `AUDIT_PASS` com zero agentes
concluídos — corrigido nas execuções seguintes com gate de validade por lente, e
o defeito do padrão genérico fica registrado. Retomar uma execução que já era
retomada perde o cache dos agentes anteriores. E `page.evaluate` com duas
atribuições soltas faz o Playwright invocar a última função: um helper de teste
era chamado sem argumentos e o erro aparecia como se fosse do produto.

**Ponto para a auditoria dirigida.** A barreira do `UNKNOWN` é deliberadamente
de sessão. Falta verificar o comportamento **entre sessões**: com o estado nesse
desfecho, uma reabertura não pode ter fallback que transforme falha de leitura em
sobrescrita. O esperado é que o disco com o candidato carregue o candidato, o
disco com o estado anterior carregue o anterior, e um disco ilegível leve ao modo
de recuperação sem gravar por cima.

## Integração contínua — 2026-08-17

`.github/workflows/quality-gate.yml` existe em `main` desde o merge `91687dc`.
Antes disso o repositório **nunca teve CI**: `git log --all -- .github/workflows/`
devolve um único commit anterior, `045c264` (2026-08-10), que jamais foi
integrado e ficou invisível atrás de uma branch com nome enganoso.

| Gatilho | Tier | Observação |
|---|---|---|
| `push` em `main` | `standard` | Gatilho principal — o fluxo aqui é merge local + publicação direta, sem PR |
| `pull_request` | `standard` | Preservado do original, caso PRs voltem a ser usados |
| `workflow_dispatch` | `standard` ou `full` | Único caminho para o tier `full` |

`standard` em push e PR é o que `CHANGE-PROCESS.md` exige para N0-V e N1;
`full` fica para candidato de release e mudanças N2/N3.

Compatibilidade auditada: a única dependência externa dos testes é `playwright`
(pinada em `requirements-dev.txt`); o gate dispara subprocessos por
`sys.executable`, então o Python do `setup-python` é o mesmo que roda os testes;
e **Node.js não é requisito** — `validate_project.py` cai para o Chromium do
Playwright para validar sintaxe JavaScript.

**Pendências desta superfície:**

- **Gatilho já ocorreu; resultado não verificado.** (Atualização de
  2026-08-20:) `main` foi publicada com o workflow em `fc29731`, `c6c1aa3` e
  `46bb776` — o `push: main` disparou a estreia no GitHub. Os resultados das
  execuções não são verificáveis deste ambiente (sem credencial de API);
  conferir na aba Actions do repositório é pendência do gestor.
- **Os dois SHAs de action pinados não foram verificados**
  (`actions/checkout@11bd719`, `actions/setup-python@a26af69`). A máquina de
  trabalho não tem credencial de rede para a API do GitHub. A pinagem por SHA é
  a postura correta de supply chain e foi preservada; se a estreia falhar, é o
  primeiro suspeito — o gate em si roda 13/13 localmente.
- Um defeito do arquivo original foi corrigido antes de restaurar: `cache: pip`
  sem `cache-dependency-path` abortaria o passo de setup, porque o cache do
  `setup-python` procura `requirements.txt` ou `pyproject.toml` e este
  repositório não tem nenhum dos dois.

## Higiene de branches — 2026-08-17

O repositório passou de 24 branches locais para **uma** (`main`). Vinte e três
foram apagadas com autorização do gestor:

- **18 já mescladas** em `main` — apagadas com `git branch -d`, que recusa se
  houver commit fora de `main`. Nenhuma recusou; nada se perdeu, porque os
  commits seguem alcançáveis a partir de `main`.
- **5 não mescladas** — cada uma **convertida em tag anotada** `archived/<nome>`
  antes da exclusão. O conteúdo está preservado de forma permanente: tag é
  referência, e o `gc` nunca coleta commit alcançável por uma. A mensagem de
  cada tag traz o comando de retomada.

| Tag | Commit | Triagem |
|---|---|---|
| `archived/governanca-multiagente` | `045c264` | **Não superada** — virou o CI acima |
| `archived/onboarding-patrimonial-wip` | `46e0f42` | Metade já em `main`; a outra colide com a etapa `database` |
| `archived/settings-central-redesign` | `0092d26` | Superada por `657e59e`, em forma melhor |
| `archived/notes-header-unified-bar` | `b96d6f1` | Superada por `429afe2`; o JS mexe em nó que `main` apagou |
| `archived/reconcile-context-post-product` | `971226a` | Fotografia de contexto 74 commits atrasada |

Dois commits pendurados aparecem em `git fsck` (`f87c56f`, `a27d650`, ambos de
2026-08-16): são stashes do GitHub Desktop, anteriores a esta limpeza e não
relacionados a ela. Não foram inspecionados.

## Calendário Econômico — estado de verificação — 2026-08-17

A distinção abaixo é deliberada e não deve ser colapsada em leituras futuras:
**automação em Chromium headless ≠ inspeção visual humana.**

| Camada | Resultado | Escopo |
|---|---|---|
| `quality_gate.py --tier standard` | **PASS 13/13** | Zero `FAIL`, zero `NOT_RUN`, zero `ENVIRONMENT_ERROR`. Artefato `quality-20260817T151725-standard.json` |
| `run_economic_calendar()` | **PASS** | Novo. Fonte única, zero id duplicado, render na raiz correta, filtro, estabilidade após três idas e voltas |
| Teste de mutação | **PASS** | Quatro defeitos plantados, quatro acusados; controle verde após restaurar |
| `smoke_test.py` sobre o monólito | **PASS** | Zero `pageerror` — resolve empiricamente o risco de TDZ da chamada script 44 → 46 durante a avaliação |
| Evidência automatizada por captura | **COLETADA** | Cinco superfícies; zero id duplicado e zero overflow horizontal medidos em runtime |
| **Inspeção visual humana** | **NÃO REALIZADA** | Nenhum `PASS` visual foi registrado. O gestor autorizou o merge sem essa etapa |

Node.js **não** é requisito do tier standard: `validate_project.py` cai para o
Chromium do Playwright. O tier foi executado a partir de venv isolada com
`playwright==1.60.0`, o pino do `requirements-dev.txt`.

Pendências desta feature, para quem retomar:

- **Inspeção visual humana** das cinco superfícies (card do Dashboard, workspace,
  overlay, tema claro/escuro, mobile) segue em aberto.
- **Tier `full` não executado**, e com ele `service_worker_upgrade_test.py`. O
  registro do service worker falha no navegador embutido usado na captura —
  restrição de sandbox, com `sw.js` intocado por esta tarefa —, então o ciclo do
  worker não foi exercitado em lugar nenhum desta série.
- Dívidas **preexistentes** deliberadamente fora de escopo: os dois `setInterval`
  sem `clearInterval` em `15-ff-news.js`, a política de timezone implícita no
  fuso do dispositivo e os 7 ids duplicados do portátil (idênticos antes e
  depois desta série).

## Reconciliação do drift documental — 2026-08-17

Correção de números que a série de submenus deixou defasados: cada tarefa
reconciliou os arquivos do próprio escopo e outras páginas continuaram
declarando os valores antigos. As três correções foram conferidas contra o
disco, não contra a documentação vizinha:

- **Scripts:** `ARCHITECTURE.md` dizia 53 e `CODE-MAP.md`/`README.md` diziam 60;
  são 65. Verificado de forma independente: 65 em `src/js/manifest.json`, os
  mesmos 65 no precache de `sw.js` e a ordem do `index.html` idêntica à do
  manifest.
- **Tiers:** `README.md` e `QUALITY-GATES.md` diziam `standard` 9 e `full` 19;
  os valores reais, lidos de `TIERS` em `tools/quality_gate.py`, são 13 e 24.
  Esta página já registrava `PASS 24/24`, ou seja, a documentação contradizia a
  própria evidência do gate.
- **Padrão ARIA do Planejamento FX:** `FX-PLANNING.md` descrevia `tabpanel`,
  `aria-controls`, foco roving e navegação por setas. Nada disso existe desde
  que a faixa estrutural compartilhada assumiu a seleção dos modos — a string
  `tabpanel` não aparece em `src/js/` nem no `index.html`. Era o único ponto em
  que a documentação afirmava uma superfície de acessibilidade inexistente.

Preservados por serem históricos corretos, e não drift: "46 scripts" do baseline
`d9510dbb55f0`, "53 scripts" do candidato `codex/galton-board` e "63 scripts" na
evidência da `ACTIVE-TASK`.

Evidência: `quality_gate.py --tier fast` PASS 3/4 e `git diff --check` PASS. O
check `structure` (`validate_project.py`) retornou `ENVIRONMENT_ERROR` — **Node.js
e Playwright não estão instalados nesta máquina** —, e pela mesma causa os tiers
`standard` e `full` ficaram `NOT_RUN`. A mudança não alcança runtime, então a
lacuna não pesa sobre este changeset; mas qualquer tarefa futura que toque código
precisa de um ambiente com Node e Playwright para fechar o gate proporcional.

## Pendências abertas fora do escopo desta tarefa

- **Numerações de artigo penduradas no código** (2026-08-17). Oito citações
  apontam para artigos inexistentes na Norma Vigente: `Art. 1.3, 3.5, 3.6, 3.7,
  3.8, 3.10, 8.6, 9.5`, em doze arquivos — `Art. 3.10` sozinho em sete. Só as
  três da guarda de Operação Única Exclusiva foram corrigidas (`17214ba`), por
  serem as únicas com correspondente vigente verificado textualmente. Duas
  ocorrências de `Art. 3.5§2` — `04-patrimonial-simulation.js:142` e
  `11-operation-lifecycle.js:41` — foram deixadas intactas de propósito: tratam
  de consolidação e pré-condições de encerramento, e trocar citação por
  suposição seria o mesmo defeito com o sinal invertido.
- **Remediação de estado já conflitado** (2026-08-17). `f64cea2` impede a
  criação de operação com duas teses, mas não trata base que já esteja nesse
  estado. Um caso real exigiria ferramenta de retificação histórica com ato
  explícito, auditoria, proveniência e revisão humana — mudança própria, não
  apêndice do Histórico. Enquanto isso, a Finalização detecta e bloqueia, sem
  correção automática.
- **Ordem fechada é imutável na grade** (2026-08-17). `readOnly = isMigrada ||
  frozen || isFechada` desabilita `par`, `tipo` e `status`. É o que torna um
  conflito preexistente irreparável pela interface. Não foi alterado: reabrir
  ordem fechada tem consequências contábeis próprias e exige decisão humana.
- **`commitOnboardingStart` inalcançável por teste** (2026-08-17). O fluxo real
  de reinício de período é closure dentro de `openOnboardingModal`, com ~2 mil
  linhas. A garantia do reinício administrativo é hoje uma guarda estrutural
  sobre o código-fonte servido, e não prova de alcançabilidade pela interface.

- **Workspace "Visão Geral" do Execution Board segue vazio.** É o único dos cinco
  sem função: o `index.html` declara "superfície reservada … o conteúdo funcional
  será especificado em tarefa própria". Decisão deliberada desde `d2ad73f`, ainda
  sem tarefa aberta.
- **Cinco commits de documentação entraram direto em `main`, sem branch**
  (`9c15f36`, `9a30705`, `bae18b2`, `fd8103d`, `c5b0b86`), criando
  `00 - FILOSOFIA E PROJETO/` e `01 - ESTRUTURA DO SOFTWARE/`. Não tocam runtime.
  Ficam registrados porque contrariam a política de branch do `CLAUDE.md` e
  porque o preflight os vinha acusando como alteração material posterior à
  source revision.
- **Possível conflito de fonte normativa, aguardando decisão humana.** O
  `AGENTS.md` fixa `docs/normative/` como M0. A pasta nova
  `00 - FILOSOFIA E PROJETO/Norma Vigente/` contém um "Estatuto V10" e um
  "Antigo Estatuto" fora desse caminho. Se for material de trabalho, nada muda;
  se for norma vigente, existem duas fontes concorrentes. **Nenhum agente deve
  tratar a pasta nova como autoritativa até que o gestor decida** — `AGENTS.md`
  manda registrar o conflito em vez de escolher em silêncio.
- **Verificação humana em navegador continua `NOT_RUN`** para as telas da série
  de submenus, como já registrado abaixo.

## Estado confirmado no disco

- A aplicação continua estática, local-first, sem framework e sem backend
  obrigatório. O runtime permanece em scripts clássicos e globais.
- `src/js/manifest.json` contém 75 scripts. Os 67 da fotografia de 2026-08-17,
  os sete de Finanças Pessoais (`10-domain/12-personal-finance.js` e
  `20-ui/17..22-finpes-*.js`) e `10-domain/13-alladin.js` — o módulo do Alladin,
  que reúne a infraestrutura do C1 e o modelo cadastral do C2. `sw.js`, o HTML e o portátil permanecem reconciliados, e
  o precache cobre os 75. Tiers: `fast` 4, `standard` 30, `full` 41.
- As seis telas principais compartilham o shell horizontal do protótipo:
  Dashboard, Execution Board, Contas, Contabilidade, Planejamento FX e
  **Finanças Pessoais** (`#finpes`, menu `06`). A navegação clássica por
  sublinhado é o padrão; abaixo de 900 px ela vira uma gaveta vertical com os
  mesmos destinos.
- Dashboard: aviso de governança e cockpit ocupam largura total; Status, VRM,
  Notícias e Ações rápidas formam a faixa P2; Evolução e Ritmo usam razão 3:2;
  motivos, métricas, acompanhamento mensal, drawdown e comparação mensal ficam
  preservados em um único disclosure metodológico.
- Execution Board: segundo nível com cinco workspaces — Visão Geral
  (estrutural), Painel Operacional, Estudos NoCoda, Estudos dos Pivots e
  Motor de Lote, migrado de Configurações. Estudos dos Pivots deixou de ser
  superfície reservada: guarda estudos por instrumento e período, com CRUD de
  pivots H1/H4 e estatística descritiva derivada (`S.pivotStudies`). O Painel Operacional é o próprio `#execWidgetGrid`: clearance
  compacto com quatro fatos, Grade e monitor LIFO, com indicadores
  complementares e ATR/VRM em disclosure. Nenhum nó foi movido, os 67 ids
  internos e a ordem normativa foram preservados, e os quatro widgets continuam
  filhos diretos da grade. A troca de workspace é `hidden` + `inert`, sem
  desmontar DOM e sem persistir nada.
- Contas: leitura primária em dez colunas, credenciais consolidadas em chip e
  editor completo expansível por conta. As duas tabelas rolam internamente no
  mobile; adicionar uma conta abre o editor e leva o foco ao nome.
- Contabilidade: quatro indicadores no topo, Real vs Projetado e Fechamento
  Diário em razão 3:2, lançamentos em largura total e funções secundárias
  preservadas em disclosures.
- Planejamento FX: o estado vazio é um cartão central de 936 px com formulário
  linear. Os quatro modos agora são selecionados exclusivamente pela segunda
  faixa estrutural do header; as tabs duplicadas saíram do conteúdo sem remover
  renderizadores ou funcionalidades.
- A faixa hierárquica é única e compartilhada (`#navSubShell`), hospedando o
  painel de Planejamento e o do Execution Board; só um módulo fica aberto por
  vez e o aberto é identificado por `aria-expanded` no próprio acionador. Ela
  abre transitoriamente por hover e fica fixada por clique/Enter/Espaço. Enquanto fixada, não fecha por saída do ponteiro, resize,
  novo clique no acionador ou seleção interna; clique externo e Escape fecham.
  Seu terceiro tom é distinto do header e do contexto em claro/escuro.
- A política PWA não permite mais um cliente utilizável com HTML novo e scripts
  cacheados do build anterior. Enquanto o worker novo está em `waiting`, o
  controller antigo entrega seu próprio `index.html`; a troca só ocorre após o
  fechamento de todos os clientes antigos.
- Estudos NoCoda: workspace do Execution Board que guarda três âncoras por
  instrumento e deriva o range −1→0 e o da subdivisão 0,125. Os instrumentos vêm
  de `instrumentCatalog()`, derivado de `S.instruments` — não há catálogo
  próprio. A identidade é `instrumentId()`, o `name` normalizado que já era a
  chave de facto; **nenhum campo novo entrou no catálogo**. O agregado
  `S.nocoda` guarda somente causas; geometria nunca persiste. Contrato em
  `docs/architecture/NOCODA-STUDIES.md`.
- Fronteira de confiança da importação: `canonicalizeStructuralMetadata()` agora
  reconstrói também a **Matriz Quadrifásica** a partir de `DEFAULTS`, além das
  chaves estruturais das fases e dos tickers. Um backup adulterado deixa de
  definir fase vigente, teto de risco e teto de alavancagem.
- `S.params.inicio` passou a ser escapado no resumo do onboarding — era o único
  campo do template sem `esc()` e constituía vetor de XSS armazenado.
- A Zona de Perigo propaga a exclusão para as demais abas pelo canal da
  Finalização de Sessão, com tipo e handler próprios: ela preserva preferências
  auxiliares e cópias de recuperação, ao contrário da finalização.
- `build-id.js` e `dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html` foram
  regenerados somente por `tools/rebuild_monolith.py`.

## Escopo e autoridade

- N1 + N0-D, autoridade A2: correção dos três achados `Medium` sustentados pela
  auditoria de segurança, testes de regressão e reconciliação documental.
- **Nenhum parâmetro normativo foi alterado.** A correção da matriz não
  introduz, muda ou remove percentual, fator ou limite: ela faz a fonte oficial
  (`DEFAULTS`, que expressa o Estatuto) prevalecer sobre o arquivo importado,
  aplicando ao caso a doutrina que a própria função já enunciava para fases e
  tickers. É restauração de aderência, não mudança de norma.
- Schema, `schemaVersion`, chaves de storage e dados do operador intocados.
  Ordens, preços, tetos por instrumento, banimentos e saldos não são alcançados
  pela canonicalização.
- Nenhum dado real, backup, token ou credencial entrou no worktree ou nas
  evidências. Nenhuma dependência, endpoint ou integração de rede nova.
- Git/publicação: branch, implementação, commit e merge autorizados e
  executados. Push e deploy ficam com o gestor.

## Evidência deste candidato

| Verificação | Resultado | Escopo/observação |
|---|---|---|
| `python3 tools/import_xss_security_test.py` | PASS | Estendido: fixture passou a incluir `params.inicio` com payload e matriz adulterada (`ddmax:0.99`, `alav:99`); a sonda desenha `renderConfigOnboarding()` e compara `S.matrix` com `DEFAULTS.matrix` **dentro da página**, para não criar segunda cópia da tabela normativa no teste. Antes do rebuild o teste REPROVOU no alvo portátil, provando que a asserção não é vazia. |
| `python3 tools/storage_governance_test.py` | PASS | Seção 9 nova: duas abas no mesmo contexto, marca de operador, limpeza numa e verificação de que a outra zera **e que a gravação dela não ressuscita a base** — que era exatamente o defeito. |
| `python3 tools/validate_project.py` | PASS | 65 scripts, 391 IDs estáticos, zero duplicados, portátil reconstruído. |
| `python3 tools/quality_gate.py --tier full` | PASS 24/24 | Rodado SOBRE O MERGE, não só nas branches: duas branches verdes isoladas podem compor um resultado quebrado. Relatório `tools/.artifacts/quality-20260814T143149-full.json`. |
| `python3 tools/pivot_studies_test.py` | PASS | Novo, no tier `standard`. Submetido a teste de mutação com dez defeitos plantados no produto — os dez foram acusados, provando que as asserções não são vazias. |
| Estabilidade do harness | PARCIAL | Dois dos três testes intermitentes tiveram a causa **provada e corrigida** (ver abaixo). `nocoda_test.py` segue sem mecanismo identificado: falhou duas vezes em rodadas reais do `--tier full`, e não reproduziu em 19 execuções dirigidas. |
| Navegador real | NOT_RUN | Nenhuma das telas recentes foi inspecionada por um humano. |
| `git diff --check` | PASS | Dentro do gate. |
| Build reproduzível | PASS dentro do full | `build-id.js` e portátil derivam das fontes oficiais. |

## Caça a bugs por execução real — 2026-08-14

Cinco sondas independentes exercitaram o app em navegador e devolveram 27
achados brutos; a verificação adversarial foi limitada a **dois por dimensão**,
de modo que **17 nunca foram verificados**. Dos 10 verificados, 8 sobreviveram e
foram corrigidos, mais 1 achado por releitura do código dos Pivots. Detalhe de
cada um no `CHANGELOG.md`.

**Não corrigido, deliberadamente.** O achado de que Finalizar Sessão apagaria os
Tickets com uma segunda aba aberta **não reproduziu**: a aba remota grava o
documento já com o Ticket, com ou sem correção — medido instrumentando
`localStorage.setItem` na aba remota, que registra uma única escrita contendo o
Ticket nos dois casos. Uma correção chegou a ser escrita e foi **removida** ao
falhar no teste de mutação. O verificador alegou 4 reproduções; a divergência
fica registrada em vez de virar código por palpite.

**Defeito introduzido e pego pelo gate.** A primeira versão do gancho que repinta
o workspace guardava com `typeof execGetView==='function'`. A declaração de
função é içada, mas o `let execView` que ela lê fica na zona morta temporal na
primeira execução — `13-exec-views.js` é o script 61 e `boot()` é o 34 — e o boot
inteiro estourava. Seis checks caíram. A guarda passou a ser o objeto
`window.JPWExec`, que só existe depois de o módulo avaliar.

**Disciplina aplicada a toda asserção nova:** a correção é revertida e a suíte
tem de acusar. Duas asserções vazias minhas foram descobertas assim — uma
chamava função local a outro escopo, outra falhava na assertiva errada.

## Determinismo do harness

Dois testes falhavam de forma intermitente por **corrida de ordem no próprio
teste**, nunca por defeito de produto. Os dois mecanismos foram provados
construindo a falha de propósito, e não esperando ela acontecer:

- `storage_governance_test.py` §9 abria a segunda aba **antes** de a primeira
  gravar a marca do operador. Enquanto isso a segunda mantinha o `S` anterior em
  memória, e qualquer gravação dela reescrevia a chave com o valor velho.
  Demonstrado: com a ordem antiga, um `save()` na segunda aba derruba a chave de
  `123456` para `10000`, e o reload seguinte lê `10000`. Corrigido gravando
  primeiro, confirmando a marca **na chave** e só então abrindo a segunda aba —
  as duas continuam vivas e simultâneas quando a limpeza acontece.
- `fx_planning_test.py` redimensionava a viewport de 1390 para 1440 e abria a
  faixa contextual em seguida. O handler de `resize`
  (`40-app/11-operational-shell.js`) fecha a faixa **transitória**; quando o
  evento era processado depois da abertura, fechava o que acabara de abrir e o
  teste acusava focus trap inexistente. Demonstrado: disparar `resize` com a
  faixa aberta leva `aria-expanded` de `true` para `false`. Corrigido esperando
  o evento ser efetivamente processado antes de abrir.

`exec_submenu_test.py` tem o mesmo par viewport/faixa, mas **não** é vulnerável:
ali o clique fixa a faixa, e faixa fixada sobrevive ao `resize` por contrato.

Hipóteses testadas e **descartadas** para os três casos — registradas para não
serem refeitas: a tempestade de repintura que `updateFxRates()` dispara depois do
`await` não fecha a faixa e não altera nenhuma das chaves comparadas
(`params`, `phases`, `ledger`, `instruments`, `accounts`, `fxPlanning`); com a
rede stubada nenhum par é atualizado, então não há `save()` nem escrita em
`S.instruments`; e nenhuma deriva de estado foi observada em 7 s de boot ocioso.

`nocoda_test.py:644` (`antes == depois`) permanece **sem mecanismo
identificado**. Falhou duas vezes em rodadas reais do `--tier full` e não
reproduziu em 19 execuções dirigidas: 3 isoladas, 8 sob 12 processos de CPU,
4 sob três suítes Playwright concorrentes e 4 sob 20 processos. Não recebeu
mudança — corrigir por palpite seria pior que deixar registrado.

Relatórios locais ficam em `tools/.artifacts/` e são ignorados pelo Git. Usar
somente o artefato cuja árvore corresponda ao estado examinado.

## Impacto agêntico e reconciliação

`AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED`

`BASIS:` o changeset cria um contrato arquitetural reutilizável de navegação,
altera o shell descrito no mapa do código e muda a representação operacional
consumida por preflight, skills e agentes. Portanto a camada agêntica é
alcançada mesmo sem alterar agente, skill ou routing.

Naturezas do changeset:

- **MATERIAL:** runtime visual e interação hierárquica de navegação.
- **RECONCILIAÇÃO:** contrato arquitetural, contexto, changelog e handoff.

| Categoria | Impacto | Ação local | Evidência/estado |
|---|---|---|---|
| `AGENTS.md`, `CLAUDE.md` e autoridade | AFFECTED | NOT_REQUIRED | As regras existentes já exigem preflight, escopo, browser real, gate e reconciliação; nenhuma instrução contradiz o contrato novo. |
| Skills e routing | AFFECTED | NOT_REQUIRED | `jpw-browser-verification`, `jpw-test-triage`, `jpw-post-change-audit` e `agentic-evolution-governance` já cobrem o fluxo e herdam o contexto canônico. |
| Bootstrap/preflight e manifest | AFFECTED | REQUIRED | Manifest preserva lista/ordem e atualiza somente hashes dos scripts de UI modificados. |
| Contexto operacional | AFFECTED | REQUIRED | `ACTIVE-TASK`, este `CURRENT-STATE` e `SESSION_HANDOFF` representam o candidato. |
| Arquitetura/contratos de interface | AFFECTED | REQUIRED | `NAVIGATION-HIERARCHY.md`, `CONTEXT-MAP.md` e `CODE-MAP.md` registram o padrão. |
| Gates e evidência | AFFECTED | REQUIRED | Teste focal cobre os estados transitório/fixado, estrutura, acessibilidade e mobile. |
| Changelog e inventário | AFFECTED | REQUIRED | Entrada Unreleased e `PROJECT-FILES.txt` registram o novo contrato. |
| Norma, schema e ADRs N3 | NOT_AFFECTED | NOT_REQUIRED | Nenhuma regra financeira, estado persistido ou decisão normativa mudou. |
| Índice/vetor/memória de projeto | NOT_AFFECTED | NOT_REQUIRED | `INDEX NOT REQUIRED`: o projeto não usa índice/vetor derivado para esses documentos. |

Resultado: `SYSTEM RECONCILED` para o blast radius estrito deste changeset. Não
há propagação multi-projeto nem reindexação a executar. Permanecem drifts
documentais preexistentes em `ARCHITECTURE.md` e `SECURITY-MODEL.md` (contagens
anteriores de scripts) e na tabela de superfície de `FX-PLANNING.md`; esses
arquivos não foram autorizados nesta tarefa e não descrevem o novo lifecycle
nem a nova composição visual.

## Contratos N2 vigentes e inalterados

- A chave financeira principal continua `jpwealth_v9_state`; estados antigos
  passam por `migrate()` e não são substituídos silenciosamente por `DEFAULTS`.
- `investorPassword` permanece apenas em memória da sessão.
- Preferência Galton continua isolada em `jpwealth_galton_preferences_v1`.
- O agregado aditivo `S.fxPlanning` e sua auditoria permanecem inalterados;
  derivados não são persistidos e campos desconhecidos são preservados.
- O service worker não limpa `localStorage`, não força takeover e não remove
  caches de outras aplicações.

## Pendências normativas bloqueantes

Não corrigir silenciosamente. Cada item exige decisão/confirmação N3 e branch própria:

1. Perfis conservadores no código usam fatores revogados (66/50/33) em conflito com a tabela V10 (53/40/27).
2. `compute()` deriva drawdown do risco programado e perdas realizadas, não da equity oficial ao vivo.
3. Ordem Gênese não aplica de forma combinada o teto de risco e o de alavancagem.
4. Stop abaixo de 2 ATR é classificado, mas não bloqueado.
5. Downgrade não aplica integralmente histerese de 0,50 ponto percentual e confirmação H4.
6. Gatilho compulsório de poda LIFO em +1,00 ponto percentual não está implementado.
7. Fase 4 permite inclusão operacional sem todo o rito de salvaguarda previsto.
8. Quarentena/guilhotina depende de formalização manual e não de uma fonte autoritativa de equity.
9. Fator padrão do Stop Raiz-N aparece como 1,8, enquanto a norma atual indica 1,25.
10. Projeções MEI por perfil precisam de decisão sobre memória de cálculo e aderência normativa.

## Dívida e riscos residuais

- A primeira atualização partindo de um worker publicado antes da nova política
  ainda obedece ao código antigo já instalado; fechar todas as abas/clientes da
  origem conclui essa transição. Não limpar storage nem dados financeiros.
- A verificação visual manual usou o estado vazio; os quatro modos com plano e
  a remoção das tabs duplicadas são cobertos por `fx_planning_test.py`, sem dados
  reais.
- `openOnboardingModal()` continua concentrando aproximadamente duas mil linhas;
  o escopo global legado e a CSP não documentada permanecem dívidas anteriores.
- A cobertura automatizada continua mais forte nos fluxos recentes do que no
  núcleo financeiro legado.

## Regra de atualização

Quem alterar fonte, teste, manifest, worker ou gerado depois deste checkpoint
deve repetir as verificações afetadas. Não remover uma falha porque deixou de
aparecer em um teste; registrar causa, comando, candidato e evidência.
