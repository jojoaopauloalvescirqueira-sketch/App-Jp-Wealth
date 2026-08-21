# Alladin — contrato do domínio

Sistema Patrimonial e Consolidador de Investimentos do JP Wealth. Domínio
próprio, sucessor do roadmap `INV-*` e renomeado pela spec canônica
**JPW-ALLADIN-SPEC V1.2.1**, que vive no vault de arquitetura, fora deste
repositório. Este documento é o contrato do que EXISTE no código — não do que
a spec planeja.

> [!important] O que o Alladin ainda NÃO é
> Duas camadas estão entregues: infraestrutura (ALD-01 C1) e modelo cadastral
> (ALD-02 C2). O domínio sabe **o que existe**; ainda não sabe **o que
> aconteceu** nem **quanto vale**. Não há transação, holding, posição,
> valuation, cost basis, performance, benchmark, UI nem integração com Trading,
> Finanças Pessoais ou Planejamento FX. Nenhum número patrimonial é calculado
> em lugar algum.

## Fronteiras

- **Finanças Pessoais** responde "como o dinheiro entrou e saiu da vida
  financeira"; **Alladin** responde "o que possuo, onde está, quanto vale";
  **Trading** responde "o que está acontecendo na operação". Um conceito
  econômico tem uma única fonte canônica (ALD-I32).
- Alladin **não cria segundo ledger Forex** (ALD-I01): Trading é fonte
  operacional, Alladin seria consumidor de projeção patrimonial — contrato
  ainda não definido (HD-1).
- Decisões de fronteira **pendentes de decisão humana**, deliberadamente não
  resolvidas pelo código: **HD-1** publicador Trading→Alladin · **HD-2** dívida
  do PF ↔ passivo patrimonial (PF = fluxo; Alladin = obrigação patrimonial;
  ligados por referência, jamais duplicados) · **HD-3** fronteira do
  Planejamento FX (`PLANNED ≠ EXECUTED ≠ OWNED`) · **cost basis** (pendência #1
  da spec, decisão N3 do ALD-04).

## Persistência — agregado `S.alladin` (schema v2)

```json
{"schemaVersion":2, "reportingCurrency":"BRL",
 "instruments":[], "assets":[], "accounts":[], "cashAccounts":[]}
```

- `reportingCurrency` é **configuração de apresentação** (ALD-I18): mudá-la
  nunca reescreve registro algum. Nenhuma conversão cambial existe ainda.
- **Derivados jamais persistem** (ALD-I27): saldo de cash account, holdings,
  posições e patrimônio são estado derivado de fases futuras.
- Guarda estrutural de boot: `alladinNormalizeState()` em `00-core/04-persistence.js`
  — reparo de FORMA apenas; conteúdo de registro jamais é tocado.
- **Migração v1 → v2** (ALD-02 C2): apenas o carimbo da versão. O v1 do C1
  declarava só o envelope e nasceu sem registros; o v2 acrescenta o contrato de
  conteúdo cadastral. Envelope corrompido volta à versão mais baixa e percorre
  a cadeia — carimbar a mais alta pularia transformações futuras.
- **Fail-closed** (`READ_ONLY_FUTURE_SCHEMA`): `schemaVersion` armazenada maior
  que a suportada — inteiro ou string de dígitos, a grafia provável de backup
  editado — deixa o agregado **byte-intacto**, recusa todo ato e expõe a
  incompatibilidade em `JPWAlladin.compat()`. Integridade > disponibilidade.
- O agregado viaja no backup normal; o envelope `jpwealth_full_backup` não muda.

## Dinheiro — schema extensível ≠ runtime universal

`{amount, currency}` com `amount` **inteiro na unidade mínima** da moeda
(ALD-I19); não existe montante sem moeda (ALD-I16). O **schema** aceita
qualquer código ISO 4217 — adicionar moeda futura jamais exige migration. O que
é limitado é o **suporte de runtime** (`ALD_RUNTIME_CURRENCIES`: BRL, USD),
estendido por dado. Moeda fora do suporte deixa o registro **válido e intacto**,
apenas ilegível (`—`) — nunca reinterpretada. Parse e formatação por aritmética
de string, sem ponto flutuante no caminho. Proporções em pontos-base
(`0..10000`), nunca float.

## Write gate — `aldMutate` é transacional

Todo ato mutável passa por `aldMutate(acao, fn, meta)`:

```text
bloqueio de módulo? → recusa
snapshot do agregado
fn(S.alladin)  — valida ANTES de mutar; ato recusado não toca em nada
save()
  true  → commit
  false → RESTAURA agregado e changeLog
```

Sem a restauração, um ato declarado não persistido (modo de recuperação A-005,
quota estourada, portão fechado) deixaria registro fantasma que o próximo
`save()` de qualquer origem gravaria. `save()===false` é prova de não-escrita.

`dgLogChange` recebe os atos como **log operacional NÃO-canônico** (HD-6):
não é o Audit Trail do Alladin e não satisfaz `ALD-I26`, que fica para o
ALD-07. Rótulo genérico por privacidade — ação e recordId, nunca nome ou valor.

## Entidades (ALD-02 C2)

```text
Instrument { instrumentId, name, symbol, exchange?, country?, currency,
             assetClass, instrumentFamily, externalIdentifiers{},
             symbolHistory[], recordStatus, createdAt }

Asset      { assetId, name, nature, category?, subcategory?, strategicPurpose?,
             strategicGroup?, tags[], recordMode, owners[], location?,
             acquisitionDate?, recordStatus, lifecycleStatus, createdAt }

Account    { accountId, name, institution, accountType, recordStatus, createdAt }

CashAccount{ cashAccountId, accountId → Account, currency, recordStatus, createdAt }
```

- **Asset Registry × Instrument Master são separados**: bem físico nunca é
  instrumento (`PHYSICAL_ASSET` não é família de instrumento). `instrumentId` é
  canônico e imutável — ticker e provider-id jamais são chave (ALD-I09/I10).
- **Account É a custódia financeira** (DC-1), tipificada por `accountType`;
  custódia física vive em `Asset.location`. Não existe entidade `Custody`.
- **CashAccount** é entidade de primeira classe, uma moeda por conta, **sem
  campo de saldo** — saldo é derivação do Cash Ledger, que nasce no ALD-03.
- **`owners[{name, shareBp, isSelf?}]`** é a realização v1 do Ownership
  Registry (fonte única, ALD-I32): `Σ shareBp ≤ 10000` (acima recusa); soma
  menor é legítima **com aviso** — jamais normalizar em silêncio; **no máximo
  um `isSelf`**, que é o que torna o valor proporcional do operador computável
  sem inferência; `isSelf` é booleano estrito.
- **Dois eixos de estado**: `recordStatus` (técnico/cadastral, ACTIVE↔INACTIVE,
  transições entregues) × `lifecycleStatus` do Asset (patrimonial —
  ACTIVE|SOLD|DISPOSED|DONATED|LOST|WRITTEN_OFF; **nenhuma transição no C2**,
  porque mudar um bem para SOLD é evento econômico do ledger físico).
- **Sem exclusão**: registro cadastral poderá ser referenciado por transações
  futuras. A política de exclusão nasce com o ledger.

## Regimes de classificação

| Regime | Campos | Regra |
|---|---|---|
| **Fechado** | `instrumentFamily` (8 famílias), `recordMode`, `recordStatus`, `lifecycleStatus` | mandato normativo ou função estrutural; valor fora **recusa** |
| **Starter** | `accountType`, `nature`, `strategicPurpose`, `assetClass` | valores semeados e oferecidos; **valor novo é aceito** com validação de forma — taxonomia patrimonial é evolutiva |
| **Livre** | `category`, `subcategory`, `strategicGroup`, `tags` | texto do operador |

## Invariantes vivos no runtime

- **DC-3 — dinheiro líquido nunca é Asset**: nenhuma `nature` pode representar
  caixa (`ALD_NATURE_DE_CAIXA_PROIBIDA`). Carteira e Cofre nascem como Account
  de tipo `OTHER`. Duas representações do mesmo real seriam duplicação
  semântica antes de virar duplicação de valor.
- **DC-4 — duplicidade avisa, nunca bloqueia**: o registro nasce e o operador
  decide. Cripto **exige** `network`, que integra a chave de identidade
  (USDT Ethereum ≠ USDT Tron). `network` é qualificador, não identificador.
- **DC-5 — `symbolHistory` é append-only**: editar `symbol` empurra o anterior;
  `symbolHistory` ilegível **recusa a edição** em vez de ser destruído — não
  compreender um campo não autoriza apagá-lo.
- **Integridade referencial hierárquica**, não simétrica: cash account ativa
  exige conta pai ativa; conta ativa **não** exige que todas as suas cash
  accounts permaneçam ativas (aposentar uma moeda não mata a conta).
- **Identidade e carimbo são imutáveis**: tentar editar `instrumentId`,
  `createdAt`, `recordStatus`, `symbolHistory` ou a moeda do instrumento é
  **recusado explicitamente**, nunca descartado em silêncio.

## Superfície pública

`window.JPWAlladin` = `{compat, writeBlockReason, money{parse,format,supported,
runtimeCurrencies}, id, catalogos, cadastro{addInstrument, editInstrument,
addAsset, editAsset, addAccount, editAccount, addCashAccount, editCashAccount,
setRecordStatus}}`. **Não é UI** (a UI é do C3): é a superfície pela qual os
testes e a aceitação humana por console exercitam o domínio.

## Testes

| Suíte | Cobertura |
|---|---|
| `tools/alladin_unit_test.py` | U1–U21 em **Chromium isolado** — sem app, sem DOM de produção, sem estado real, sem rede (contada e assertada). Moeda, IDs, gate, owners/`isSelf`, regimes, cripto, `symbolHistory`, falha parcial em validação e em persistência recusada, integridade referencial, varredura tabular dos ramos de validação |
| `tools/alladin_foundation_test.py` | Integração no app real — migração v1→v2, round-trip byte-idêntico com as quatro coleções povoadas, fail-closed, **rollback duplo** (build pré-Alladin, que preserva por ignorância; e build do C1, que preserva por fail-closed), reload real, falha parcial, XSS e privacidade do log, round-trip de backup |

Ambas no tier `standard` (30; `full` 41).

## Entregas

| Entrega | Candidate | Merge |
|---|---|---|
| ALD-01 C1 — Foundation Infrastructure | `fe616a7c…` | `c6c1aa3` |
| ALD-02 C2 — Modelo Cadastral | `66ebf840…` | `29aca32` |

## Próximas fases (nenhuma iniciada)

`ALD-03` transações, eventos, holdings e posições — onde nascem cost basis,
`flowScope INTERNAL|EXTERNAL` e o par atômico papel↔caixa · `ALD-04` valuation
e performance · `C3` UI mínima, sob a navegação primária aprovada
(`01 Dashboard · 02 Forex · 03 Finanças Pessoais · 04 Research · 05 Alladin`) ·
`ALD-07` Data Quality e Audit Trail canônico.
