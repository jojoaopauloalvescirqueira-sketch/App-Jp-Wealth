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

## Ciclo de vida do agregado — encerrar sessão ≠ apagar tudo

O JP Wealth tem **dois atos destrutivos distintos**, e o Alladin responde de
forma oposta a cada um. Confundi-los foi o defeito que o ALD-C3-PRE corrigiu.

| Ato | Funções | `S.alladin` |
|---|---|---|
| **Encerramento operacional** | `finalizeJPWealthSession()` · `sessionHandleRemoteFinalization()` | **preservado**, inclusive em schema futuro |
| **Limpeza total** | `wipeAllData()` · `sessionHandleRemoteBaseWipe()` | **apagado**, inclusive em schema futuro |

Encerrar a sessão termina o período de trading — conta, ordens, fases, histórico
da operação. A limpeza total é exclusão pedida com todas as letras, confirmada
por frase digitada. Os dois broadcasts são semanticamente distintos
(`jpwealth-session-finalized` × `jpwealth-base-wiped`) e nenhum atravessa para o
handler do outro.

O patrimônio é **memória longitudinal**: não pertence a um ciclo operacional.
Um imóvel não deixa de existir porque a conta de trading foi encerrada. É o
mesmo contrato já vigente para `mvpNotes` e `personalFinance`.

O **fail-closed nunca protege contra deleção explicitamente pedida**. Um
agregado em schema futuro é somente-leitura para *atos do domínio* — isso
impede escrita mal-informada, não impede o operador de apagar o próprio dado.
Na Finalizar Sessão o agregado ilegível é copiado **como está**, sem leitura,
sem normalização e sem migração: preservar não exige compreender.

**A preservação é pré-condição do ato destrutivo, não recuperação depois dele.**
A cópia acontece **antes** de bloquear a persistência, antes de avisar as outras
abas e antes de `clearJPWealthLocalData` — que apaga o disco antes de o estado
novo ser construído. Falhando a cópia, o ato é abortado: nada apagado, nenhuma
outra aba avisada, persistência intacta e erro explícito ao operador. Por isso
`emptyJPWealthState(preservado)` aplica **só** o que o chamador entregou e nunca
consulta `S.alladin` por conta própria — um fallback interno clonaria depois do
disco já apagado, e tornaria o parâmetro indetectável.

**A fonte é o estado persistido nos DOIS fluxos** (`sessionPreserveLongitudinal`,
`JSON.parse` — nunca `S.alladin` da memória). A memória de uma aba pode ser um
retrato anterior a exclusões que o operador já confirmou em outra aba; preservar
dela faria a finalização **ressuscitar registro apagado** — e como
`setRecordStatus` só alterna `ACTIVE`/`INACTIVE`, editar o agregado é hoje o
único modo de eliminar um registro. No fluxo local a leitura acontece na
**abertura** do fluxo, antes do export (que grava via `save()` e contaminaria a
leitura); chave ausente ali é base virgem legítima e prossegue vazio. No fluxo
remoto chave ausente é disco indeterminado e **aborta**. Estado ilegível aborta
nos dois, com a aba bloqueada para gravação: nunca há fallback para a memória.

**A preservação depende da geração da base.** O ato só atua se a geração corrente
for a mesma lida no início (`jpwealth_base_epoch_v1`, ver `ARCHITECTURE.md`): a
leitura é um seqlock `epoch → documento → epoch`, e uma rotação no meio invalida o
snapshot em vez de misturar bases. Sem geração confiável o encerramento é
**recusado** — antes do export, do broadcast, do clear e de qualquer persistência
destrutiva. Isso fecha o replay em que uma finalização emitida antes de uma
limpeza total regravava patrimônio depois dela.

**C6 revisado.** O contrato "nenhuma chave nova de `localStorage`" passa a admitir
**uma** exceção nominal: `jpwealth_base_epoch_v1`, chave técnica anti-replay, sem
PII e sem conteúdo patrimonial. Qualquer outra chave nova continua reprovando.

**Limite conhecido desta garantia.** A atomicidade cobre a *cópia*, não a
*gravação final*. `persistNotesAfterSessionWipe` grava a chave principal dentro
de um `try/catch` vazio pré-existente: se essa escrita falhar (cota, disco
cheio), a sessão termina com o agregado apenas em memória e sem aviso ao
operador. O defeito é anterior a este ciclo e atinge igualmente `mvpNotes` e
`personalFinance`; está registrado como **bloqueador antes da liberação da UI do
Alladin**, junto com `sessionStateFingerprint()` sem proteção — que faz
`structuredClone(S)` e derruba a entrada do fluxo antes da guarda de preservação
— e com a revisão do texto de consentimento da tela de finalização.

## Estado do ciclo — ALD-C3-PRE-PERSISTENCE implementado

O candidato do C3-PRE + EPOCH vive em `1501d46` (nota factual: a mensagem desse
commit não descreve o conteúdo) e foi reconciliado com a main em `dc8a3ec`. O
ciclo ALD-C3-PRE-PERSISTENCE fechou os quatro bloqueadores: **B1**
write-before-clear (o documento final é gravado e confirmado por read-back antes
de qualquer limpeza; a chave principal nunca é removida pela finalização);
**B2** `sessionCommitFinalizedState` substituiu `persistNotesAfterSessionWipe` —
falha de gravação vira recusa explícita, jamais sucesso aparente; **B3** o
handler remoto valida tudo antes de bloquear e roda a mutação em try/finally —
nenhum caminho deixa a aba permanentemente somente-leitura (a proteção
anti-ressurreição é a guarda de concorrência do `save()`); **B4** rotação de
geração exige `releitura === valor` (bootstrap, que é convergência, adota o
sentinel). Decisões congeladas: DP-1 Web Locks quando disponível, fallback
DEGRADED explícito e honesto; DP-2 `wipeAllData` assíncrona com a destruição
inteira dentro do lock; DP-3 a janela síncrona residual `getItem→setItem` é
limitação formal APENAS do fallback, nunca apresentada como CAS. O backup do
ramo `changed` é gerado do documento autoritativo capturado, e a revalidação de
revisão dentro do lock aborta o commit se a base mudou durante a interação.

## C3-S1 — superfície cadastral somente-leitura

O placeholder NAV-01 evoluiu para a primeira superfície funcional do Alladin
(decisões UI-A..UI-F congeladas no gate de 2026-08-28). A tela tem **quatro
destinos locais efêmeros** — Instrumentos, Bens (`Asset`), Contas e Caixa
(`CashAccount`) — com default em Instrumentos; a seleção nunca toca `S` nem
storage, e os destinos **não** são rotas globais.

A leitura passa exclusivamente por **`JPWAlladin.leitura`**: snapshots
profundamente desacoplados (clone estrutural + congelamento recursivo) contendo
apenas os campos cadastrais que este build conhece. Ler jamais congela ou
altera o agregado real; agregado ausente devolve coleções vazias **sem
materializar nada**; schema futuro é **projetado, nunca normalizado** — campos
desconhecidos são ignorados e o agregado permanece byte-idêntico, com banner
persistente: os dados compatíveis podem ser consultados, mas não alterados
neste build.

**Proibição econômica**: nenhum saldo, quantidade, preço, valor, custo,
patrimônio, P&L, rentabilidade ou performance — nem como zero. Estados vazios
são textuais ("Nenhum instrumento cadastrado."). "Caixa" é o cadastro de
`CashAccount` (DC-3), jamais dinheiro disponível. Superfícies econômicas só
nascerão com `ALD-03`/`ALD-04`, como destinos novos.

**Zero-write como invariante**: abrir, trocar de view, renderizar e recarregar
produzem zero `save()`, zero `aldMutate`, zero materialização e `S`/disco
byte-idênticos (provado por `tools/alladin_ui_readonly_test.py` + 6 mutantes).

**Bloqueadores pré-escrita: RESOLVIDOS (gate C3-S2 PRE-WRITE, 2026-08-28).**
`sessionStateFingerprint()` passou a medir o estado persistível (clone JSON com
a mesma política de segredo do `save()`; estado não-serializável ⇒ `null` ⇒
tratamento conservador como *changed* — nenhuma exceção alcança a UI). O
consentimento da finalização declara integralmente a política de retenção
(Alladin, Finanças Pessoais e Tickets permanecem; a Zona de Perigo é o caminho
para apagar tudo) e a frase digitada passou a ser **ENCERRAR SESSÃO** — a
antiga `APAGAR TUDO` era objetivamente falsa para este ato e pertence apenas à
Zona de Perigo. Semântica congelada: *Finalizar Sessão* (frase `ENCERRAR
SESSÃO`) remove os dados operacionais e preserva a memória de longo prazo;
*Zona de Perigo* (frase `APAGAR`) é a limpeza total. Nenhum texto futuro pode
tratá-las como equivalentes.

**C3-S2-A — manutenção cadastral (Account · CashAccount · status ×4), implementado.**
Escrita via UI exclusivamente por `JPWAlladin.cadastro`/`setRecordStatus`, num
modal próprio do Alladin (padrão de acessibilidade de Settings sem acoplamento:
focus trap, Escape, retorno de foco re-resolvido por seletor, ARIA). Máquina de
estados IDLE→EDITING→SUBMITTING→{ERROR·SUCCESS·COMMITTED_WARNING}. **DC-4 é
pós-criação, fiel ao C2**: o registro nasce e persiste; o aviso exige o gesto
explícito *Manter* ou *Inativar este registro* (via `setRecordStatus`), com
Salvar/Enter/Escape/backdrop suspensos até a decisão — e o foco vai ao título
para um Enter residual não escolher por ninguém. Status é ação separada na
linha, com confirmação explícita e sem optimistic update: recusa referencial do
domínio nunca produz status falso no DOM. Referência de caixa a conta inativa é
exibida honesta ("Nome — INATIVA"), jamais trocada em silêncio. Sem conta
ativa, "Novo caixa" dá lugar à instrução de cadastrar/reativar uma conta —
criação implícita é impossível. Cancelamentos, validação e write gate: zero
write provado; a trilha de auditoria (`changeLog`) é assertada como prova de
que toda mutação atravessou o domínio. Suíte `tools/alladin_ui_crud_test.py`
(W1–W15 / S2A-1..12) + 10 mutantes mortos.

**C3-S2-B (Instrument · Asset com owners), próximo**: formulários ricos sobre o
esqueleto provado; mutantes de `symbolHistory`/`owners` reservados para lá.

## Superfície pública do domínio

`window.JPWAlladin` = `{compat, writeBlockReason, money{parse,format,supported,
runtimeCurrencies}, id, catalogos, cadastro{addInstrument, editInstrument,
addAsset, editAsset, addAccount, editAccount, addCashAccount, editCashAccount,
setRecordStatus}}`. **Não é UI** (a UI é do C3): é a superfície pela qual os
testes e a aceitação humana por console exercitam o domínio.

## Testes

| Suíte | Cobertura |
|---|---|
| `tools/alladin_unit_test.py` | U1–U21 em **Chromium isolado** — sem app, sem DOM de produção, sem estado real, sem rede (contada e assertada). Moeda, IDs, gate, owners/`isSelf`, regimes, cripto, `symbolHistory`, falha parcial em validação e em persistência recusada, integridade referencial, varredura tabular dos ramos de validação |
| `tools/alladin_finalize_preservation_test.py` | C1–C13 no app real — agregado idêntico em memória **e em disco**; sessão de fato encerrada; schema futuro intacto atravessando `reload` e ainda recusando escrita; Zona de Perigo continua apagando (v2 e v3); nenhuma chave nova **nem contaminação de auxiliar**; dois ciclos pelos dois ramos de entrada; falha forçada de cópia sem apagar nada, **com ordem e persistência assertadas**; **fluxo cross-tab** preserva do estado persistido (v2 e v3), não ressuscita registro apagado e aborta bloqueado quando o disco é ilegível; cópia profunda; legado sem agregado |
| `tools/alladin_foundation_test.py` | Integração no app real — migração v1→v2, round-trip byte-idêntico com as quatro coleções povoadas, fail-closed, **rollback duplo** (build pré-Alladin, que preserva por ignorância; e build do C1, que preserva por fail-closed), reload real, falha parcial, XSS e privacidade do log, round-trip de backup |

As três acima e o protocolo de geração da base
(`tools/session_epoch_protocol_test.py`, E1–E16) no tier `standard` (34; `full` 45).

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
