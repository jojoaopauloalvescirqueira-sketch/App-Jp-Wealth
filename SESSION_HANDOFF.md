# Session Handoff — Alladin · ADJUSTMENT publicado (ALD-03-S4)

- Data: 2026-08-31
- **`main` == `origin/main` == `a88b4509ee1651dc9a9b1676ea20d55f1872f131`**
- Worktree em `main`, sem trabalho pendente · CI #45 verde

## Onde o projeto está

| Entrega | Commit | Estado |
|---|---|---|
| Registro do hardening | `eb3fd6f` | publicado · CI #42 verde |
| ALD-03 S3 — FEE/TAX standalone | `9287889` | publicado · CI #43 verde |
| Reconciliação documental do S3 | `451b01b` | publicado · CI #44 verde |
| **ALD-03 S4 — ADJUSTMENT** | `a88b450` | **publicado · CI #45 verde** |

**ALD-03-S4 publicado e CI-confirmado.** O ledger registra **diferença de caixa
sem contraparte econômica identificável**. `ADJUSTMENT_CREDIT` soma `+amount` e
`ADJUSTMENT_DEBIT` subtrai `−amount`; `amount` é **magnitude positiva**, nunca
assinado, e a **direção vem exclusivamente do `eventType`** — não existe campo
`direction`. São **dois tipos** justamente para que a direção fique protegida
pelo mesmo código que protege o resto: o espelho do par compara
`reversedEventType` e a reversão resolve o efeito pelo tipo do **original**.

**`reason` é obrigatório e é campo próprio**; **`note` segue opcional e
distinto**. O ajuste é o único evento cujo valor não pode ser conferido contra
nada — sem original de onde herdar, sem contraparte com que comparar — então a
justificativa é parte da **forma** do registro, não da conveniência do autor.

**`flowScope` ausente**, **zero efeito em posição**, **sem vínculo a
transação**, **reversal pela mecânica existente**. `ADJUSTMENT` **não é external
flow** e **não é economic gain/loss**; **nenhuma matemática de performance** e
**nenhum Reconciliation Engine** foram implementados — a fronteira ficou
documentada para que o Performance Book futuro **segregue** o ajuste em vez de
absorvê-lo em silêncio no residual.

**Hardening — completude do cash delta.** `aldTxEfeito` não pode mais assumir
delta 0 silenciosamente: `eventType` cash-affecting sem semântica explícita em
`ALD_CASH_DELTA` vira **BLOCKING** com `ALD_CASH_DELTA_AUSENTE`, diagnóstico
distinto do reversal órfão. Isso **elimina a classe "saldo plausível e falso por
evento ignorado"** — a única falha do módulo que produzia número confiável e
errado em vez de recusa.

**`schemaVersion` 5 → 6 é identity migration**: carimbo puro, zero transformação
econômica, ledger povoado preservado. **v6 lendo v5 migra**; **v5 lendo v6
responde `READ_ONLY_FUTURE_SCHEMA`** e **para de escrever** — antes do carimbo o
build antigo tratava um `ADJUSTMENT` válido como corrupção **e continuava
escrevendo por cima**.

Fingerprint `f14c43c7…` · mutations **MA-1..MA-7 DEAD** · `fast` 4/4,
`standard` 39/39, `full` 50/50 locais, **non-PASS 0**. **CI #45**: job `quality`
**SUCCESS**. O 39/39 é consistente com o contrato de saída do gate (exit 0 exige
**todas** as verificações PASS); **o log bruto não foi obtido (HTTP 403)** e
isso fica registrado como dedução, não como leitura.

## Dívidas e decisões futuras

- **Cost-basis N3** — necessário antes do ALD-04-S2 se *specific identification*
  entrar em escopo; se for custo médio, nada muda.
- **Escala decimal por moeda** — antes de JPY/BTC ou valuation.
- **Transferência in-kind** e **corporate actions** — exigirão `accountId`
  first-class; trades já persistidos não migram.
- **QA-D2** — assert do Galton sob carga do tier; causa não fechada.
- **Dívida textual** — comentário "SOMENTE LEITURA" em `index.html`.
- **Dívida de nome** — `ALD_CAMPO_NAO_PERMITIDO_EM_DESPESA` é usado **também**
  pela família só-caixa: o código diz "DESPESA" para um ajuste.
- **`ALD_REASON_NAO_PERMITIDO`** — aceito como *tightening* do write contract:
  `reason` em tipo não-ADJUSTMENT é **recusado** em vez de descartado em
  silêncio. Não há regressão de leitura — v5 e v6 leem registros históricos com
  `reason` extra normalmente.

## Próxima decisão — gate humano

`ALD-04-S2` ou `QA-D2`.
**Nenhuma autorizada por este documento.**

# Histórico

## Fotografia anterior — FEE/TAX publicado (ALD-03-S3) (2026-08-31)

- Data: 2026-08-31
- **`main` == `origin/main` == `928788966f05ecc50f294a1c4b936eb68f43e6b2`**
- Worktree em `main`, sem trabalho pendente · CI #43 verde (décimo consecutivo)

## Onde o projeto está

| Entrega | Commit | Estado |
|---|---|---|
| ALLADIN FULL HARDENING | `3f2716d` | publicado · CI #41 verde |
| Registro do hardening | `eb3fd6f` | publicado · CI #42 verde |
| **ALD-03 S3 — FEE/TAX standalone** | `9287889` | **publicado · CI #43 verde** |

**ALD-03-S3 publicado e CI-confirmado.** O ledger registra despesa sem
contraparte de trade: `FEE` e `TAX` são só-caixa (`−amount`), **não movem
posição**, **não têm `flowScope`** (taxa reduz retorno; não é retirada de
capital), derivam a moeda da CashAccount, revertem pela mecânica existente e
**não têm vínculo a trade**. Os `fees`/`taxes` de BUY/SELL seguem **embutidos e
economicamente inalterados** — a ausência de vínculo torna a dupla contagem
irrepresentável, sem nenhuma heurística econômica.

`schemaVersion` **4 → 5** é **identity migration**: carimbo puro, zero
transformação econômica, ledger povoado preservado. Serve para que um build v4
diante de dado v5 responda `READ_ONLY_FUTURE_SCHEMA` em vez de tratar um `FEE`
válido como corrupção. Mutation 8/8, `full` local 50/50, CI `PASS=39` com os
demais contadores zerados.

**ADJUSTMENT continua fora** — S4 própria, com direção e semântica ainda por
decidir.

## Dívidas e decisões futuras

- **Cost-basis N3** — necessário antes do ALD-04-S2 se *specific identification*
  entrar em escopo; se for custo médio, nada muda.
- **Escala decimal por moeda** — antes de JPY/BTC ou valuation.
- **Transferência in-kind / corporate actions** — exigirão `accountId`
  first-class; trades já persistidos não migram.
- **QA-D2** — assert do Galton sob carga do tier; causa não fechada.
- **Dívida textual** — comentário "SOMENTE LEITURA" em `index.html`.

## Nota de processo

Classificar uma descoberta como **MATERIAL DISCOVERY implica PARAR antes de
editar e solicitar amendment** — mesmo quando o arquivo está dentro do blast
autorizado. Foi o que se aplicou nesta closure: o bump de schema alcançou
`CONTEXT-MAP`, `CODE-MAP` e `README`, e o blast foi ampliado por decisão humana,
não por iniciativa da implementação.

## Próxima decisão — gate humano

`ALD-03-S4` (ADJUSTMENT), `ALD-04-S2` ou `QA-D2`.
**Nenhuma autorizada por este documento.**


## Fotografia anterior — FULL HARDENING concluído (2026-08-31)

- Data: 2026-08-31
- **`main` == `origin/main` == `3f2716da80f2d7367e61e535b3651426b8631e01`**
- Worktree em `main`, sem trabalho pendente · CI #41 verde (oitavo consecutivo)

## Onde o projeto está

| Entrega | Commit | Estado |
|---|---|---|
| QA-D1 — isolamento do harness × Service Worker | `b7ada80` | publicado · CI #39 verde |
| Registro documental do QA-D1 | `5a4bd68` | publicado · CI #40 verde |
| **ALLADIN FULL HARDENING** | `3f2716d` | **publicado · CI #41 verde** |

**Hardening concluído.** A auditoria adversarial fechou um cluster P0/P1: read
models e write gate confiavam em invariantes write-only, e um agregado
persistido adulterado produzia número plausível e falso — porque `aldFindIn`
resolve id por **first-match** na leitura *e* na escrita.
`aldIntegridadeEstrutural` agora protege `saldoDeCaixa`, `posicoes` e
**`aldMutate`** (recusa antes de mutar), validando unicidade dos cinco IDs
canônicos, `dedupeKey` única, ≤1 reversal por original, pareamento
status⟺reversal, container `transactions` fail-closed e future-schema no saldo.
Fatos legítimos idênticos seguem somando. Isolamento de SW propagado às suítes
de app real. Mutation 10/10, `full` 50/50, CI `PASS=39` com os demais
contadores zerados.

**Nenhum P0/P1 conhecido restante dentro dos vetores auditados** — fronteira do
que foi exercitado, não prova de ausência.

## Dívidas e decisões futuras

- **Escala decimal por moeda** — antes de JPY/BTC ou valuation.
- **Transferência in-kind / corporate actions** — exigirão `accountId`
  first-class; os trades já persistidos não migram.
- **Cost-basis N3** — só *specific identification* exigiria lot-ref no `SELL`,
  e a decisão precisa vir antes que vendas acumulem.
- **QA-D2** — assert do Galton sob carga do tier; causa não fechada.
- **Dívida textual** — comentário "SOMENTE LEITURA" em `index.html`.

## Próxima decisão — gate humano

1. **ALD-03-S3** — recomendado (aditivo, desbloqueado);
2. **ALD-04-S2** — depende da decisão N3 de cost basis;
3. **QA-D2**.

**Nenhuma autorizada por este documento.**

## Fotografia anterior — QA-D1 resolvido (2026-08-31)

- Data: 2026-08-31
- **`main` == `origin/main` == `b7ada805f95ec44501804546ea8389d567bc80bb`**
- Worktree em `main`, sem trabalho pendente · CI #39 verde (sexto consecutivo)

## Onde o projeto está

| Entrega | Commit | Estado |
|---|---|---|
| ALD-04 S1 — Position Quantity Engine | `29bb6ff` | publicado · CI #37 verde |
| Reconciliação pós-ALD-04-S1 | `ad5a696` | publicado · CI #38 verde |
| **QA-D1 — isolamento do harness × Service Worker** | `b7ada80` | **publicado · CI #39 verde** |

**QA-D1 está RESOLVIDA — era HARNESS BUG.** O `page.route` não intercepta
fetches servidos por Service Worker; pós-reload, o `updateFxRates` do boot
buscava cotação real por fora do stub e salvava dentro da janela do caso N. O
harness agora bloqueia SW no contexto (`service_workers="block"`); o produto
ficou intacto e a sensibilidade do caso N foi provada por mutação real.

## Dívidas vivas

- **QA-D2** — assert do Galton sob carga do tier; causa não fechada.
- **Dívida textual** — comentário de `section#alladin` em `index.html` ainda
  diz "SOMENTE LEITURA".

## Próxima decisão — gate humano

Continuidade do **ALD-04**, **ALD-03-S3** ou **QA-D2**.
**Nenhuma autorizada por este documento.**

## Fotografia anterior — Position Engine publicado (2026-08-31)

- Data: 2026-08-31
- **`main` == `origin/main` == `29bb6ff722964dfd283558fc5bd73590a5a5b69b`**
- Worktree em `main`, sem trabalho pendente de nenhuma frente

## Onde o projeto está

| Entrega | Commit | Estado |
|---|---|---|
| ALD-03 S2 — BUY/SELL | `cc4714e` | publicado · CI #35 verde |
| Reconciliação pós-S2 | `31399ca` | publicado · CI #36 verde |
| **ALD-04 S1 — Position Quantity Engine** | `29bb6ff` | **publicado · CI #37 verde** |

O Alladin responde três perguntas — o que existe (cadastro), o que aconteceu
(ledger de caixa e trades) e **quanto papel há**: `leitura.posicoes()` deriva a
posição por quantidade do ledger a cada leitura, com identidade
`instrumentId + accountId`, aritmética decimal exata em BigInt, zero fora da
coleção, negativa fiel sem semântica de short, fail-closed global e
`schemaVersion` ainda **4** (nada novo persistido). Não existem: holding
persistido/consolidado, cost basis, valuation, P&L, performance, UI de
posições. Contrato em `docs/architecture/ALLADIN.md`.

## Dívidas abertas

- **QA-D1** — disparou uma vez no primeiro `full` local do ALD-04-S1; passou
  isolada; `full` seguinte 50/50; não reproduziu no CI #37. **Continua
  aberta**, sem classificação definitiva.
- **QA-D2** — assert do Galton sob carga do tier; causa não fechada.
- **Dívida textual** — comentário de `section#alladin` em `index.html` ainda
  diz "SOMENTE LEITURA".

## Próxima decisão — gate humano

- continuidade do **ALD-04**;
- **ALD-03-S3** (FEE/TAX/ADJUSTMENT standalone);
- ou dívida técnica como **QA-D1**.

**Nenhuma autorizada por este documento.**

## Fotografia anterior — BUY/SELL publicado (2026-08-30)

- Data: 2026-08-30
- **`main` == `origin/main` == `cc4714e4513016af636b17ca7948c2755f50ef03`**
- Worktree em `main`, sem trabalho pendente de nenhuma frente

## Onde o projeto está

| Entrega | Commit | Estado |
|---|---|---|
| ALD-03 S1 — Cash Ledger | `5a6f7c3` | publicado |
| Reconciliação de governança | `93f6e78` | publicado |
| CI-ENV-01-FIX — fetch-depth + NOT_RUN | `4057a39` | publicado · CI #34 verde |
| **ALD-03 S2 — BUY/SELL** | `cc4714e` | **publicado · CI #35 verde** |

O ledger registra dinheiro **e** papel: um trade é UM registro de duas pernas
(caixa e `±quantity`), `fees`/`taxes` embutidos com impacto único (ALD-I36),
`flowScope` ausente em trades por contrato, consistência do par
reversal↔original julgada também na leitura, e guardas de inteiro seguro nos
dois sentidos e a cada soma do saldo. `schemaVersion` **4** tranca o build v3
(barreira provada por mixed-build contra o código real de `4057a39`). O
contrato completo vive em `docs/architecture/ALLADIN.md`; a fotografia, em
`docs/governance/CURRENT-STATE.md`.

O CI deixou de ser vermelho estrutural: a causa (clone raso engolindo os SHAs
históricos das suítes) foi reproduzida, corrigida na raiz e convertida em
política — caso sem histórico termina em `NOT_RUN`, nunca em PASS silencioso.
Runs #34 e #35 verdes com `NOT_RUN=0`.

## Dívidas abertas

- **QA-D1** — `alladin_ui_readonly_test.py` caso N × `updateFxRates` (causa
  provada, correção não feita).
- **QA-D2** — assert do Galton sob carga do tier (causa não fechada).
- **Dívida textual** — comentário de `section#alladin` em `index.html` ainda
  diz "SOMENTE LEITURA" (texto do C3-S1).

## Próxima decisão de arquitetura

Gate humano, em aberto — **nenhuma das duas autorizada**:

- **ALD-03-S3** — `FEE`/`TAX`/`ADJUSTMENT` standalone, com DHs próprios ainda
  não decididos (direção do ADJUSTMENT; flowScope de FEE); ou
- **progressão para ALD-04** (Position Engine) conforme planejamento aprovado —
  que exigirá fechar o contrato de aritmética decimal de `quantity`.

## Fotografia anterior — Cash Ledger publicado (2026-08-29)

- Data: 2026-08-29
- **`main` == `origin/main` == `5a6f7c3af23cc4e901d3c49236d98184c6b570ea`**
- Worktree em `main`, sem trabalho pendente de nenhuma frente

## Onde o projeto está

| Entrega | Commit | Estado |
|---|---|---|
| Alladin C3 — cadastro patrimonial | `39acdc6` | concluído e integrado |
| Endurecimento pré-ledger (D-1, D-2) | `c8c3190` | publicado |
| Marca do cabeçalho abre o Dashboard | `982fb7e` | publicado |
| **ALD-03 S1 — Cash Ledger** | `5a6f7c3` | **publicado** |

O Alladin deixou de responder apenas *"o que existe"* e passou a registrar *"o
que aconteceu"* com o dinheiro: `DEPOSIT`, `WITHDRAWAL`, `TRANSFER` e `REVERSAL`,
com saldo **sempre derivado** — nunca campo — e `schemaVersion 3` como barreira
de escrita para builds anteriores. O contrato completo está em
`docs/architecture/ALLADIN.md`; a fotografia do estado, em
`docs/governance/CURRENT-STATE.md`.

## Dívidas abertas — nenhuma resolvida

- **QA-D1** — `alladin_ui_readonly_test.py`, caso N: compara o documento inteiro
  enquanto `updateFxRates` escreve nele por conta própria. Causa raiz provada
  (relógio ativo: 1 em 6 acusa; neutralizado: nenhuma), correção não feita.
- **QA-D2** — `finalize_session_test.py`: assert do Galton sob carga do tier;
  passa isolado e na baseline; causa não fechada.
- **`session-epoch-protocol` / `ENVIRONMENT_ERROR`** — recorrente nos runs #28 a
  #32 do CI, sempre a mesma suíte, sempre no runner, nunca localmente. É o único
  motivo de a `main` estar vermelha há cinco publicações seguidas; **nenhuma
  delas teve `PRODUCT_FAIL` ou `TEST_HARNESS_FAIL`**.
- **Dívida textual** — o comentário que apresenta `section#alladin` em
  `index.html` ainda diz "SOMENTE LEITURA", texto do C3-S1.

## Próxima fronteira

**ALD-03-S2** — `BUY`/`SELL`, `FEE`, `ADJUSTMENT` e o par atômico papel↔caixa,
deliberadamente fora do S1. Não autorizado. As seis decisões `DH-03-*` já estão
congeladas como contrato e não se reabrem.

---

## Sessão N1 da logo — candidato SUPERSEDIDO, não publicado

Uma sessão anterior implementou a marca-como-link em worktree que continha, ao
mesmo tempo, trabalho não commitado do Alladin. **Aquele candidato nunca foi
publicado**: a implementação definitiva foi refeita do zero sobre base limpa e
entrou em `982fb7e`. O registro fica porque duas coisas nele foram corretas e
continuam valendo — o agente identificou a contaminação do worktree e **se
recusou a atribuir a si alterações alheias**, e a QA daquela sessão produziu o
achado sobre cache de service worker que hoje vive em
`docs/governance/QUALITY-GATES.md`.

Uma correção necessária àquele registro: ele reportava `standard 38/38` a partir
de `tools/.artifacts/quality-20260829T163558-standard.json`. **Essa medição não
é evidência isolada da logo** — foi feita sobre árvore que continha as suítes do
Alladin ainda não commitadas. A evidência válida da implementação publicada foi
obtida depois, em worktree limpo: `standard` **37/37**. O número `38` só passou a
valer para a árvore atual quando o Cash Ledger foi publicado, por outra razão.

## Contexto anterior — Alladin C3 concluído e integrado

## O que está entregue

O Alladin tem domínio (ALD-01 C1 e ALD-02 C2) e **superfície de cadastro
completa** (C3): Instrument, Asset, Account e CashAccount com leitura, criação,
edição e ciclo `recordStatus`, todos pela interface real. Toda mutação atravessa
`JPWAlladin.cadastro`/`setRecordStatus`; a UI não escreve em `S`, não chama
`save()` e não toca `localStorage`.

| Fatia | Checkpoint | Entrega |
|---|---|---|
| C3-PRE | `1501d46` | preservação na finalização e protocolo de geração da base (a mensagem do commit não descreve o conteúdo) |
| — | `dc8a3ec` | reconciliação com a `main` da Navigation |
| C3-PRE-PERSISTENCE | `c2819af` | serialização cross-tab dos escritores do documento |
| C3-S1 | `94c383e` | superfície cadastral somente-leitura |
| C3-S2 PRE-WRITE | `d9bd71b` | salvaguardas de escrita da sessão |
| C3-S2-A | `e5d6f36` | Account e CashAccount |
| C3-S2-B | `a725302` | Instrument e Asset |
| C3-S2-C | `f5124f4` | integridade da edição cadastral |

## Fronteira

O C3 responde **"o que existe?"**. O `ALD-03` responderá **"o que aconteceu
economicamente?"** — transações, eventos, posições, saldos, valuations,
patrimônio e performance. Nada disso existe hoje, nem como zero.

```text
CADASTRO + EVENTOS + VALUATIONS = ESTADO PATRIMONIAL DERIVADO
```

## Evidência

`validate_project` PASS com 77 scripts e 428 IDs; `fast` 4/4, `standard` 37/37 e
`full` **48/48 PASS**. O ciclo do C3 acumulou, nas suas fatias, mutação real com
sobreviventes investigados e mutantes equivalentes reportados como tais — nunca
convertidos em score.

## Dívidas de harness abertas

- **QA-D1** — `alladin_ui_readonly_test.py`, caso N: compara o documento inteiro
  enquanto `updateFxRates` escreve nele por conta própria. Prova determinística:
  com o relógio de cotação ativo, 1 de 6 execuções acusa; neutralizado, nenhuma;
  e a escrita aparece **também no controle que não toca no Alladin**.
- **QA-D2** — `finalize_session_test.py`: assert do Galton (`currentSpeed`)
  falha sob carga do tier; passa isolado e na baseline; causa não fechada.

Nenhuma das duas é regressão de produto. Corrigi-las é slice de harness próprio.

## Dívida textual não-executável

O comentário de `index.html` que introduz `section#alladin` ainda diz "SOMENTE
LEITURA", texto do C3-S1. `index.html` é arquivo de produto e o Closure é
`PRODUCT = 0`, então **não foi tocado** — registrado para o próximo slice que
legitimamente abrir esse arquivo.

## CI do push da `main` — vermelho por ambiente, registrado e aberto

Run #28 (`Quality Gate`, tier `standard`, commit `39acdc6`):
`PASS=36 · PRODUCT_FAIL=0 · TEST_HARNESS_FAIL=0 · ENVIRONMENT_ERROR=1 ·
BASELINE_FAIL=0 · NOT_RUN=0`. A única falha foi **`session-epoch-protocol`**,
que o próprio quality gate classificou como **ENVIRONMENT_ERROR**. O runner
estava correto (checkout `39acdc6`, Python 3.12.14, Playwright 1.60.0, Chromium
instalado) e a falha surgiu após dezenas de suítes verdes. As quatro suítes do
Alladin passaram e **QA-D1 não disparou**.

Não chamar esse CI de verde, não tratar o erro como resolvido e não atribuí-lo
ao Alladin. Ele permanece **aberto**, ao lado de QA-D1 e QA-D2.

`SYSTEM RECONCILED = SIM`. Não há gate humano pendente deste ciclo: commit,
push e integração foram executados. A próxima fronteira é a abertura do
**ALD-03**, ainda não autorizada.
