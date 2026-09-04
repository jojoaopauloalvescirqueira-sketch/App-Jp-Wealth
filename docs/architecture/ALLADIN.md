# Alladin — contrato do domínio

Sistema Patrimonial e Consolidador de Investimentos do JP Wealth. Domínio
próprio, sucessor do roadmap `INV-*` e renomeado pela spec canônica
**JPW-ALLADIN-SPEC V1.2.1**, que vive no vault de arquitetura, fora deste
repositório. Este documento é o contrato do que EXISTE no código — não do que
a spec planeja.

> [!important] O que o Alladin ainda NÃO é
> Três camadas estão entregues: infraestrutura (ALD-01 C1), modelo cadastral
> (ALD-02 C2) e a **superfície de cadastro** (C3, concluída — leitura, CRUD das
> quatro entidades, `recordStatus`, write gate, DC-4 e integridade da edição).
> O domínio sabe **o que existe**; ainda não sabe **o que aconteceu** nem
> **quanto vale**. Não há transação, holding, posição, valuation, cost basis,
> performance, benchmark nem integração com Trading, Finanças Pessoais ou
> Planejamento FX. Nenhum número patrimonial é calculado em lugar algum.

> [!note] Superado em 2026-08-31 — o parágrafo acima descreve o estado do C3
> O texto acima ficou como registro daquele momento. **O domínio já sabe "o que
> aconteceu"**: o Cash Ledger (ALD-03 S1), os trades BUY/SELL (S2), as despesas
> FEE/TAX standalone (S3), os ajustes de reconciliação (S4) e a **posição por
> quantidade derivada** (ALD-04 S1), a **superfície econômica read-only**
> (ALD-05 S1), a **criação de lançamento pela UI** (ALD-05 S2) e o **estorno pela
> UI** (ALD-05 S3) estão publicados — ver as seções próprias abaixo. **Continuam inexistentes**:
> holding persistido/consolidado, cost basis, valuation/current value, P&L,
> performance, benchmark e as integrações Trading/PF/FX.

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

## Persistência — agregado `S.alladin` (schema v6)

```json
{"schemaVersion":6, "reportingCurrency":"BRL",
 "instruments":[], "assets":[], "accounts":[], "cashAccounts":[], "transactions":[]}
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

O `changeLog` é restaurado **por conteúdo**, não por comprimento (`ALD-03-H0`).
`dgLogChange` **reatribui** o array ao podá-lo no teto de 400 entradas, e nesse
ponto exato `401 → slice → 400` devolve o mesmo comprimento de antes: restaurar
pelo tamanho seria uma restauração que não restaura — a entrada do ato recusado
sobreviveria e a mais antiga legítima seria evicta. Enquanto o Alladin foi só
cadastral o teto era inalcançável; um ledger vive **no** teto, onde esse seria o
único caminho. A suíte unitária prova o invariante nos dois regimes, abaixo e
exatamente no teto, comparando a sequência inteira — e o stub de `dgLogChange`
do harness replica a poda real, porque um stub que simplifica o mecanismo sob
teste não simplifica: cega.

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

**C3-S2-B — Instrument · Asset (formulários ricos), implementado.** Fecha o CRUD
cadastral das quatro entidades sobre o esqueleto do S2-A, sem reabrir modal,
write gate, máquina de submissão ou DC-4.

*Patch-diff.* Todo `edit` compara com o snapshot de abertura e envia **apenas os
campos alterados**. Campo não tocado não viaja, e o domínio funde o patch com o
registro **atual** — edição concorrente de outro campo sobrevive, que é a defesa
real contra modal envelhecido (nenhum merge de conflito novo foi criado). A
comparação normaliza o snapshot com a mesma higiene da leitura do formulário
(trim, dedup de tags, `isSelf` só quando verdadeiro), senão uma fixture com
espaço viraria "mudança" fantasma.

*Moeda e symbolHistory.* `currency` aparece desabilitada no edit com a razão
escrita e **nunca entra no patch**. `symbolHistory` não tem input, hidden field
nem entrada no patch: a UI envia o novo símbolo, o domínio decide se houve
mudança e mantém o histórico (DC-5), e a UI apenas relê a projeção canônica para
exibi-lo como leitura. Histórico ilegível faz o domínio recusar o edit inteiro —
a recusa é exibida honesta e o formulário permanece aberto; a rota de saída é
inativar e recadastrar, jamais "consertar" o histórico pelo formulário.

*Cripto e identificadores.* Família `CRYPTO` revela o campo **Rede (network)**,
que é a **fonte única** da chave `network` — o editor genérico recusa criar uma
segunda, em qualquer família (corrigido no S2-C; ver abaixo). Linhas de identificador totalmente vazias são omitidas (o domínio
recusa valor vazio, e omitir é a única leitura honesta de uma linha em branco);
linha meio-preenchida é ambiguidade e recusa local, com o rascunho intacto.
Chaves reservadas recebem aviso antecipado, mas o domínio segue sendo a
autoridade. O datalist sugere `isin`/`cnpj`/`ticker_provedor` sem fechar o
schema, que é aberto por contrato.

*Proprietários.* Participação é digitada em porcentagem e persistida em **basis
points por aritmética inteira de string** — `parseFloat` jamais entra no caminho:
`66,67 + 33,33` fecha exatamente 10000. Terceira casa decimal é recusada inline,
antes de qualquer submissão. `isSelf` aparece como **"Sou eu"** e só é enviado
quando verdadeiro (espelho do que o domínio persiste). O total cadastral
("Participação atribuída: N%") é exibido ao vivo — é `owners/shareBp`, nunca
valor, e o restante não atribuído jamais é representado como dinheiro.
`lifecycleStatus` é texto puro com a razão declarada: sem input, sem hidden,
fora do patch.

*Taxonomia de avisos (contrato central do slice).* Só o prefixo `DUPLICADO`
abre `COMMITTED_WARNING` com decisão *Manter*/*Inativar este registro*.
`MOEDA_FORA_DO_SUPORTE_DE_RUNTIME`, `OWNERSHIP_PARCIAL_NAO_ATRIBUIDA` e
`OWNER_NOME_DUPLICADO` são avisos **pós-sucesso**: registro válido, modal fecha,
e inativar jamais é oferecido como resposta artificial. Quando duplicidade e
informativo ocorrem no mesmo ato, a duplicidade governa a decisão e os demais
aparecem em bloco próprio ("outros avisos… que não pedem decisão"), para que
nenhum deles pareça a razão da inativação. Os códigos são humanizados **sem
perder identidade** (o código acompanha o texto) e um código desconhecido é
exibido cru — humanizar nunca descarta.

*Correção autorizada (DH-S2B-2).* O estado de decisão distingue **criação de
alteração**: dizer "o registro foi criado" numa edição era falsidade objetiva,
alcançável já no S2-A via edição de conta de caixa. Máquina, gatilho, ações e
foco no título permanecem intactos.

*Efeito colateral corrigido no caminho.* A view inativa deixou de reter DOM: um
painel renderizado antes de o write gate fechar guardava botões de mutação sem
`disabled` — obsoletos, escondidos pelo `inert` mas não corrigidos por ele.

**C3-S2-C — correções de preservação, implementado.** Slice corretivo aberto
pelo C3 Closure Gate, que recusou declarar o ciclo concluído: a auditoria
encontrou dois caminhos onde a UI **destruía dado cadastral já persistido, em
silêncio, reportando sucesso** — e neste projeto preservação vale mais que
funcionalidade. Nenhuma correção tocou o domínio.

*B-1 · a rede sobrevive à troca de família.* O campo **Rede** deixa de ser lido
apenas sob `CRYPTO`: ele permanece visível fora de cripto **enquanto tiver
valor**, a leitura é incondicional, e a chave `network` nunca vira linha
genérica em família alguma. Sair de `CRYPTO` preserva a rede; **removê-la exige
o gesto explícito de limpar o campo**, com o valor à vista. Em `CRYPTO` ela
segue obrigatória — quem esvazia recebe recusa, e nada some. Como o objeto não
mudou, `externalIdentifiers` sequer entra no patch.

*B-2 · vocabulário fechado desconhecido é preservado, não normalizado.* Um valor
de `instrumentFamily` ou `recordMode` que este build não conhece — legítimo, só
mais novo — não tinha `option` no `<select>` em modo edição, então o navegador
selecionava a primeira e o patch-diff reescrevia, em silêncio, um campo que o
operador nunca tocou; o read-model promete exatamente o contrário ("projetar não
é normalizar"). Agora o valor ganha opção própria, selecionada e rotulada com
honestidade — *"valor não reconhecido por esta versão"* —, e **não entra no
patch**. O domínio então recusa o ato, e a recusa é dita em linguagem humana:
o cadastro usa um valor que esta versão não reconhece, e para salvar é preciso
escolher um valor suportado. A mensagem **não afirma corrupção** (o dado é
legítimo) e **nada é alterado automaticamente**; o valor cru permanece à vista
enquanto o modal estiver aberto. A auditoria dos vocabulários fechados fixou o
alcance: apenas esses dois campos são editáveis por `<select>`; `recordStatus` e
`lifecycleStatus` não são editáveis, e os regimes STARTER são texto livre, que
preserva por natureza.

*B-3 · a recusa não custa o trabalho do operador.* O erro passa a ser injetado
**in-place nas quatro entidades**: Account e CashAccount re-renderizavam o
formulário e apagavam o que havia sido digitado — segunda punição por um erro
que muitas vezes nem era do operador. Vale para validação local, recusa do
domínio, write gate tardio e persistência recusada; em todos, o modal permanece
aberto, o rascunho intacto, o erro visível e nenhum aviso de sucesso.

*F-1 · rótulos fiéis ao catálogo.* O mapa de `lifecycleStatus` inventava
`TRANSFERRED`, que o domínio não define, e omitia `DONATED`, `LOST` e
`WRITTEN_OFF`, que ele define. Agora as chaves são exatamente o catálogo —
`Em uso · Vendido · Descartado · Doado · Perdido · Baixado` — e um assert
estrutural compara mapa e catálogo a cada rodada, de modo que a divergência não
volta sem quebrar teste. Valor fora do catálogo continua exibido cru.

Suíte estendida (S2-C: C1–C8 e as propriedades P1–P9) + 6 mutantes reais mortos.

Suíte `tools/alladin_ui_crud_test.py` (S2-B: I1–I12, A1–A15, WT1–WT5, R1–R8 —
somada a W1–W15/S2A-1..12) + 11 mutantes reais executados e mortos, além dos
invariantes cobertos por asserts estruturais permanentes (nenhum id,
`recordStatus`, `createdAt`, `symbolHistory` ou `lifecycleStatus` vira input em
qualquer estado; varredura econômica em todos os formulários).

## Superfície pública do domínio

`window.JPWAlladin` = `{compat, writeBlockReason, money{parse,format,supported,
runtimeCurrencies}, id, catalogos, cadastro{addInstrument, editInstrument,
addAsset, editAsset, addAccount, editAccount, addCashAccount, editCashAccount,
setRecordStatus}}`. **Não é UI** (a UI é do C3): é a superfície pela qual os
testes e a aceitação humana por console exercitam o domínio.

## Testes

| Suíte | Cobertura |
|---|---|
| `tools/alladin_ui_tx_reverse_test.py` | RV-A..RV-H — estorno pela UI: elegibilidade por linha (`—` em REVERSED/REVERSAL, `disabled` sob write gate, sem ação sob BLOCKING), modal com o original read-only e só três campos editáveis, porta única (1 `reverseTransaction`, 0 `addTransaction`), sucesso conferido contra os read-models, corrida com estorno duplicado, cancelar zero-write, double-submit inerte, submit tardio recusado, original byte-idêntico |
| `tools/alladin_ui_tx_write_test.py` | TX-A..TX-N — criação pela UI: porta única (um `addTransaction`, um `save` por submit), payload sem campos do domínio, dinheiro só por `money.parse`, `quantity` verbatim com recusa sem correção, os nove tipos pelo modal real, ajuste com `reason` próprio, transfer sem pré-filtro, double-submit inerte, cancelar zero-write, write gate na abertura e no submit tardio, BLOCKING não convida escrita, pós-sucesso comparado aos read-models |
| `tools/alladin_ui_ledger_test.py` | E1–E16 + E12b — superfície econômica read-only: sete destinos com os quatro cadastrais intactos, ordem do read-model preservada, dez `eventType` rotulados, `reason` visível, transferência com as duas pernas e caixas homônimas desambiguadas, `quantity` byte-idêntica (negativa fiel, >64 chars íntegra), **BLOCKING × EMPTY nos dois sentidos**, seis vetores de corrupção, a sentinela barrando ledger filtrado, zero `save()` |
| `tools/alladin_unit_test.py` | U1–U26 em **Chromium isolado** — sem app, sem DOM de produção, sem estado real, sem rede (contada e assertada). Moeda, IDs, gate, owners/`isSelf`, regimes, cripto, `symbolHistory`, falha parcial em validação e em persistência recusada, integridade referencial, varredura tabular dos ramos de validação; S2: `quantity` canônica e o espelho do par reversal↔original sondados direto; ALD-04: aritmética decimal BigInt (parse/alinhamento/soma/render) sondada direto |
| `tools/alladin_finalize_preservation_test.py` | C1–C13 no app real — agregado idêntico em memória **e em disco**; sessão de fato encerrada; schema futuro intacto atravessando `reload` e ainda recusando escrita; Zona de Perigo continua apagando (v2 e v3); nenhuma chave nova **nem contaminação de auxiliar**; dois ciclos pelos dois ramos de entrada; falha forçada de cópia sem apagar nada, **com ordem e persistência assertadas**; **fluxo cross-tab** preserva do estado persistido (v2 e v3), não ressuscita registro apagado e aborta bloqueado quando o disco é ilegível; cópia profunda; legado sem agregado |
| `tools/alladin_foundation_test.py` | Integração no app real — migração v1→v2, round-trip byte-idêntico com as quatro coleções povoadas, fail-closed, **rollback duplo** (build pré-Alladin, que preserva por ignorância; e build do C1, que preserva por fail-closed), reload real, falha parcial, XSS e privacidade do log, round-trip de backup; carimbo v3→v4 com ledger **povoado**; mixed-build do build v3 real sobre agregado v4 |

| `tools/alladin_ui_readonly_test.py` | C3-S1 no app real — quatro destinos locais, cadastro C2 verdadeiro, **zero escrita** e zero materialização do agregado, snapshots desacoplados do read-model, `READ_ONLY` de schema futuro sem normalizar, ausência de conteúdo econômico |
| `tools/alladin_ui_crud_test.py` | C3-S2 no app real — Account, CashAccount, Instrument e Asset criados e editados pelo modal verdadeiro, com persistência provada em memória **e** em disco; DC-4 pós-criação e a decisão explícita; status ×4 por `setRecordStatus`; write gate na abertura e no submit; patch-diff; taxonomia de avisos; e as quatro preservações do S2-C (rede, vocabulário desconhecido, rascunho e rótulos de lifecycle) |

As cinco acima, `tools/alladin_ledger_test.py` (L1–L46: Cash Ledger do S1 e a
dupla atômica BUY/SELL do S2, com a consistência do par e as guardas de inteiro
seguro), `tools/alladin_position_test.py` (P1–P22: posição derivada do ALD-04
S1 — identidade, aritmética exata, zero/negativo, adulteração e schema futuro
BLOCKING, determinismo) e o protocolo de geração da base
(`tools/session_epoch_protocol_test.py`, E1–E16) nos tiers `standard` (39) e
`full` (50); `fast` tem 4.

## Entregas

| Entrega | Checkpoint | Merge |
|---|---|---|
| ALD-01 C1 — Foundation Infrastructure | `fe616a7c…` | `c6c1aa3` |
| ALD-02 C2 — Modelo Cadastral | `66ebf840…` | `29aca32` |
| C3-PRE — preservação na finalização e protocolo de geração | `1501d46` | `39acdc6` (ff) |
| — reconciliação com a main da Navigation | `dc8a3ec` | `39acdc6` (ff) |
| C3-PRE-PERSISTENCE — serialização cross-tab da escrita | `c2819af` | `39acdc6` (ff) |
| C3-S1 — superfície cadastral somente-leitura | `94c383e` | `39acdc6` (ff) |
| C3-S2 PRE-WRITE — salvaguardas de escrita da sessão | `d9bd71b` | `39acdc6` (ff) |
| C3-S2-A — Account e CashAccount | `e5d6f36` | `39acdc6` (ff) |
| C3-S2-B — Instrument e Asset | `a725302` | `39acdc6` (ff) |
| C3-S2-C — integridade da edição cadastral | `f5124f4` | `39acdc6` (ff) |

O commit `1501d46` traz o C3-PRE e o protocolo de geração da base, apesar de a
mensagem dizer outra coisa — nota factual registrada para que a cadeia não se
perca por causa do rótulo.

> [!note] Como ler a coluna de integração
> A integração do C3 na `main` ocorreu por **fast-forward**; **não foi criado
> merge commit**. A `main` passou a apontar diretamente para `39acdc6`, e por
> isso os oito checkpoints do ciclo trazem `39acdc6 (ff)` — não existe um SHA
> de merge análogo aos de ALD-01 e ALD-02. A branch
> `fix/alladin-session-preservation` está convergida com a `main`, sem commits
> exclusivos.

## ALD-03 S1 — Cash Ledger (o primeiro fato econômico)

O Alladin passa a responder, além de "o que existe", **um pedaço** de "o que
aconteceu": entrada, saída e movimentação de dinheiro entre custódias. Nada além
disso — sem papel, sem custo, sem valor de mercado, sem performance.

```text
Transaction { transactionId 'aldtx_…' · eventType DEPOSIT|WITHDRAWAL|TRANSFER|BUY|SELL
                                                 |FEE|TAX|ADJUSTMENT_CREDIT|ADJUSTMENT_DEBIT|REVERSAL
              status POSTED|REVERSED · flowScope? INTERNAL|EXTERNAL (só eventos de fluxo)
              amount > 0 · currency · effectiveAt · recordedAt
              cashAccountId? · sourceCashAccountId? · destinationCashAccountId?
              instrumentId? · quantity? (string decimal canônica) · fees? · taxes? (trade)
              reason? (obrigatório no ajuste, proibido nos demais)
              reversalOf? · reversedEventType? · dedupeKey? · note? }
```

*Um fato, múltiplos efeitos.* A transferência é **um registro** com origem e
destino, não dois lançamentos correlacionados. Com isso, "debitou a origem e o
destino não recebeu" deixa de ser um risco a controlar e passa a ser
**irrepresentável**. E a transferência interna **não é aporte**: move dinheiro
entre custódias que já são nossas, então o patrimônio global não muda — o caso
canônico que a suíte prova somando os dois saldos antes e depois.

*`amount` é magnitude, nunca sinal.* A direção vem do `eventType`, o que torna
"um DEPOSIT de −100" impossível de escrever. Se o sinal morasse no valor, todo
leitor teria de reinterpretar a combinação sinal × tipo.

*`flowScope` é perímetro, não direção — e é condicional por família (S2).*
`EXTERNAL` cruza a fronteira do patrimônio consolidado; `INTERNAL` fica dentro
dela. É **persistido** e validado contra o `eventType`: um registro que divergir
da tabela é **dado inválido**, jamais corrigido em silêncio na leitura. BUY/SELL
**não possuem** flowScope: trocar caixa por papel é mudança de composição dentro
da mesma custódia, não fluxo de capital pelo perímetro — a **ausência** é tão
contratual quanto a presença, e um trade carimbado de fluxo é dado adulterado.
O reversal espelha a presença/ausência do original.

*Correção é reversão, não edição.* `POSTED` é economicamente imutável. Reverter
cria um fato NOVO, com data própria, que copia e inverte o que é econômico —
valor, moeda, escopo e referências vêm do original, e o chamador **não pode
informá-los**. O original recebe `status: REVERSED`, e apenas isso muda nele.
Proibidos: reverter uma reversão, reverter duas vezes, reverter sem data válida.

*O saldo é sempre derivado — e fail-closed.* Não existe `CashAccount.balance`
(ALD-I27). `saldoDeCaixa` soma os efeitos e devolve
`{available, amount, currency, quality, issues}`. O original `REVERSED`
**continua contando** e o `REVERSAL` contra-lança: a soma dá zero. Filtrar o
revertido apagaria metade do par e devolveria um número errado com cara de
certo. E **qualidade bloqueante não vira saldo parcial**: um único registro que
este build não consiga classificar torna a métrica indisponível — porque não há
como afirmar que ele não pertencia àquela conta.

*Duplicidade econômica é fail-closed.* `dedupeKey` é opcional; quando presente,
é único em todo o ledger e a repetição é **recusada**. Aqui o domínio se afasta
deliberadamente do DC-4: dois cadastros parecidos são problema de curadoria;
dois lançamentos iguais **fabricam dinheiro**.

*Conta encerrada não invalida o passado — mas o passado trava o cadastro.* A
assimetria é deliberada. Lançamento novo exige `CashAccount` ativa; inativar uma
conta **com histórico continua permitido**, o histórico segue valendo e um fato
antigo continua reversível — encerrar uma conta é ato administrativo legítimo.
Já `currency` e `accountId` tornam-se **imutáveis** assim que a conta é
referenciada por qualquer lançamento, inclusive como destino de transferência.
Não é rigor formal: trocar a moeda reinterpreta o passado, porque os registros
permanecem na moeda antiga e o saldo inteiro passa a `MOEDA_DIVERGENTE` — isto
é, história ilegível. Corrigir cadastro depois de haver movimento exige outra
conta, nunca a reescrita do significado da que existe (`ALD_CASHACCOUNT_COM_LANCAMENTOS`).

*Ordem é econômica.* A leitura ordena por `(effectiveAt, recordedAt,
transactionId)` — nunca pela ordem do array, que é acidente de inserção.

## ALD-03 S2 — BUY/SELL: a dupla atômica papel↔caixa

Um trade é **um registro com duas pernas**, no mesmo desenho do TRANSFER:

```text
BUY   papel = +quantity   caixa = −(amount + fees + taxes)
SELL  papel = −quantity   caixa = +(amount − fees − taxes)   ← pode ser 0 ou negativo
```

"Debitou o caixa e o papel não entrou" é **irrepresentável**. `amount` é o valor
bruto do trade; `fees`/`taxes` são componentes opcionais na entrada e **sempre
presentes** na forma persistida (default 0) — o impacto de caixa é derivado por
fórmula fixa, e um `FEE` avulso do mesmo fato não existe (ALD-I36: fee associado
jamais vira segundo impacto standalone). SELL com líquido negativo é legítimo:
fail-closed recusa dado **inconsistente**, não fato incomum. O exemplo canônico
da spec fecha: DEPOSIT 10000 → BUY 3000/fee 10 → saldo **6990**.

*`quantity` é string decimal canônica* — positiva, sem sinal, expoente, zeros à
esquerda ou zeros finais na fração: **uma grafia por valor**, de modo que
igualdade de valor seja igualdade de string, sem aritmética decimal neste ciclo.
O teto de 64 caracteres é proteção técnica de representação, não política de
precisão (rounding por classe segue pendente na spec §29). Nenhuma posição,
holding ou soma de quantidade nasce aqui — isso é o Position Engine (ALD-04).

*Vínculos e moeda.* BUY/SELL exigem `Instrument` existente e `ACTIVE`, e
`instrument.currency == cashAccount.currency == tx.currency` — câmbio implícito
é recusa, como no TRANSFER. A custódia do papel deriva de
`cashAccount.accountId`; não há campo próprio neste ciclo. `instrumentFamily`
**congela** na primeira referência econômica (`ALD_INSTRUMENT_COM_LANCAMENTOS`):
trocar CRYPTO→EQUITY_LIKE reinterpretaria a quantidade de todos os trades.
`currency` do instrumento já era imutável desde o C2; `symbol` segue editável
com `symbolHistory`.

*O par reversal↔original é julgado na LEITURA (MC-S2-1).* A escrita constrói o
reversal copiando a economia byte-igual — mas escrita correta não prova leitura
íntegra: um reversal adulterado depois de persistido (amount 10000→9000)
continuaria formalmente legível e o saldo sairia errado com cara de válido.
`aldReversalConsistente` confere tipo, valor, moeda, refs (presença E valor),
campos de trade e o espelho de flowScope; qualquer divergência é
`ALD_REVERSAL_INCONSISTENTE` → qualidade BLOCKING → saldo indisponível.

*Inteiro seguro nos dois sentidos (MC-S2-2).* A escrita recusa componentes cujo
delta composto saia de 2⁵³ (`ALD_EFEITO_MONETARIO_FORA_DO_INTEIRO_SEGURO`), e o
acumulador do saldo guarda **a cada soma** — um total que atravessa a região
insegura e "volta" é número corrompido com cara de são; a checagem só no fim
aprovaria exatamente esse caso.

### `schemaVersion`: barreiras de escrita, não migrações de dados

A cadeia é v1→v2→v3→v4, um passo por versão, e os dois últimos carimbos têm a
mesma natureza. **v2→v3** (S1) cria a coleção `transactions` quando ausente;
sondado empiricamente, um build v2 **preserva** o que não conhece mas **continua
escrevendo**, podendo violar amarras do ledger que ignora. **v3→v4** (S2) é
carimbo **puro** — nenhum fato transformado: o build v3 lê BUY/SELL como
ilegíveis (saldo BLOCKING, reversão recusada — fail-closed correto), mas suas
portas cadastrais ignoram o congelamento de `instrumentFamily`. Com o carimbo,
esse build cai em `READ_ONLY_FUTURE_SCHEMA`. As três portas concordam: o
**DEFAULTS nasce em v4**, a **migração** leva o legado até v4, e o **write
gate** fecha acima disso. Coleção ausente nasce vazia; existente é preservada
(provado com ledger **povoado** — a lição do M11); forma inválida **não** é
substituída por `[]` — apagar história econômica para consertar a forma seria a
pior troca possível. O mixed-build é provado contra o código **real** do build
v3 (`git archive` de `4057a39`).

## ALD-04 S1 — Position Quantity Engine (derivado, nunca persistido)

`leitura.posicoes()` deriva a posição por **quantidade** a cada leitura —
nenhum holding é persistido (ALD-I27), e reconstruir do ledger é a prova de
ALD-I13. Identidade: **`instrumentId + accountId`** — a custódia vem
exclusivamente de `cashAccount.accountId`, porque o papel vive na corretora:
duas cash accounts do mesmo Account somam UMA posição; o mesmo instrumento em
Accounts distintos são posições distintas.

```text
BUY  → +quantity      SELL → −quantity      REVERSAL → −efeito(original)
DEPOSIT/WITHDRAWAL/TRANSFER (e seus reversals) → papel zero
```

*Aritmética exata, sem float.* Inteiro escalado em `BigInt`: parse da string
canônica, alinhamento de escala, soma/subtração fechadas — não existe
arredondamento possível, então nenhuma política de rounding nasce aqui (spec
§29 segue pendente). O derivado pode ser `0` (a posição **sai** da coleção),
negativo (string assinada fiel — `'-5'` — **sem** semântica de short: bloquear
venda além da posição é decisão humana futura, não regra deste engine) e pode
exceder os 64 chars do teto de entrada — o teto é de payload, não de verdade
econômica; truncar seria inventar um número. `BigInt` jamais sai no DTO.

*Fail-closed global, espelho do saldo.* Registro ilegível, reversal
órfão/inconsistente (MC-S2-1 reusado), cadastro órfão
(caixa/conta/instrumento), moeda divergente entre trade/caixa/instrumento e
**schema futuro** (guarda explícita por `aldCompat().readOnly`, mesmo que todos
os eventos presentes sejam conhecidos) ⇒ `available:false`, `positions:[]` —
nunca posição parcial. Saída determinística: `instrumentId` ASC, depois
`accountId` ASC; a ordem física do array não vaza para o resultado.

`schemaVersion` permanece **4**: zero estado persistido novo, zero invariante
de escrita — não há o que uma barreira trancaria.

## ALD-05 S1 — superfície econômica read-only (a UI projeta, não normaliza)

Cinco slices de domínio — Cash Ledger, trades, despesas, ajustes e Position
Engine — existiam sem nenhuma forma de alcançá-las pela aplicação. `ALD-05 S1`
abre três destinos no mesmo `section#alladin`, **depois** dos quatro cadastrais:

```text
Instrumentos · Bens · Contas · Caixa │ Lançamentos · Saldos · Posições
        cadastral (sem economia)     │   econômico (read-only)
```

*A UI não tem aritmética.* Ela não soma, não subtrai, não reordena, não formata
dinheiro, não deriva direção e não recalcula quantidade. Todo número chega
pronto de um read-model congelado; dinheiro passa por `money.format` (inteiro em
unidade mínima, sem float); `quantity` é a **string canônica verbatim**. A única
lógica nova é escolher rótulo e distinguir **OK / BLOCKING / EMPTY**.

*Nenhuma direção é calculada por linha.* `amount` é magnitude e a direção mora
no `eventType`, que já está na coluna Evento. Derivar sinal por lançamento seria
reimplementar `ALD_CASH_DELTA` na apresentação — e sairia **errado** no
`TRANSFER` (∓ conforme a conta observada) e enganoso em `BUY`/`SELL` (o efeito
líquido embute `fees`/`taxes`). O efeito em caixa pertence a `saldoDeCaixa`, e é
a tela Saldos que o mostra.

*`effectiveAt` e `recordedAt` ficam ambos visíveis*, o segundo rotulado
"registrado em" — nunca em `title`/tooltip: informação de auditoria não pode
depender de mouse. Divergir entre os dois é sinal, não ruído.

*Rótulos que colidem são desambiguados.* `CashAccount` não tem nome próprio, e
duas caixas da mesma moeda sob a mesma conta produzem o mesmo rótulo — duas
linhas idênticas com saldos diferentes, e uma transferência que se lê
"BRL · XP → BRL · XP". Onde o rótulo colide, o id canônico entra.

### BLOCKING nunca vira zero — a última porta

O domínio já recusa dado inválido na leitura. A UI seria o último lugar onde a
mesma falha poderia renascer, agora como pixel: `positions:[]` sob BLOCKING e
`positions:[]` sob agregado legitimamente vazio são a **mesma estrutura de
dados**. Sem olhar `available` antes, as duas viram a mesma tela — e
*"Nenhuma posição em aberto"* sobre agregado corrompido é mentira tranquilizadora.

Sob indisponibilidade: **nenhuma tabela, nenhum número, nenhum texto de empty** —
só o aviso textual e os `issues` do domínio. Em Saldos o bloqueio é **por linha**:
conta indisponível mostra "Indisponível", jamais `R$ 0,00` por fallback. E o
inverso também é contratual: um saldo **legitimamente zero** continua exibível —
proibir todo zero apagaria um fato verdadeiro.

### Sentinela de integridade dos Lançamentos (MD-2/A)

`leitura.transactions()` **não tem envelope de qualidade**: `aldVistaCadastral`
filtra por `aldRegistroLegivel` — checagem de **forma** (objeto não-array) — e
descarta em silêncio, sem `available`, sem integridade estrutural e sem guarda de
schema futuro. Projetar essa lista direto exibiria um ledger silenciosamente
**menor** como se fosse o ledger inteiro.

Enquanto o envelope próprio não existe, a confiabilidade vem de **`posicoes()`**
— global e fail-closed pelos mesmos motivos (integridade estrutural, registro
ilegível, cadastro órfão, moeda divergente, schema futuro) — somada a
`compat()`. É guarda de **apresentação**, não regra econômica: a UI não
interpreta o veredito, apenas se recusa a desenhar.

> [!note] Fronteira conhecida do sentinela, provada em E12b
> A guarda de moeda de `aldPosicoes` compara trade × caixa × instrumento — ela
> existe onde há **papel**. Num registro **só-caixa** com moeda divergente o
> sentinela não vê, e Lançamentos segue projetando. Isso não produz número
> falso: Lançamentos exibe **fatos** (tipo, magnitude, contas); quem fica
> indigno de confiança é o **saldo**, e a tela de Saldos marca aquela linha
> Indisponível. Se um dia Lançamentos passar a exibir número derivado, esta
> fronteira deixa de bastar.

**Dívida registrada:** `transactions()` deve ganhar envelope próprio de
qualidade em slice específica. Até lá, o acoplamento acima é a guarda.

## ALD-05 S2 — criação de lançamento pela UI (a UI coleta; o domínio decide)

O painel Lançamentos ganhou o CTA **"Novo lançamento"**: um modal único para os
**nove** tipos criáveis, com seletor de tipo e campos específicos por evento —
trocar o tipo re-renderiza só o bloco específico, e o rascunho comum sobrevive.
**`REVERSAL` fica fora** (slice própria: é ação por linha, outra UX e outra
API), e **`dedupeKey` não é exposta** (decisão de gate: double-submit já é
bloqueado pela máquina de estados, e dois fatos idênticos sem dedupe são
legítimos por contrato).

*Uma chamada por submit.* `JPWAlladin.ledger.addTransaction(dados)` é a única
porta; o payload **nunca** carrega `transactionId`, `recordedAt`, `status`,
`currency`, `flowScope` ou `unitPrice` — tudo isso é do domínio. Dinheiro entra
**exclusivamente** por `money.parse` (minor units — `"1.234,56"` → `123456`;
`parseFloat` morreria no separador de milhar); `quantity` vai **verbatim** do
input, e `"1.50"` é recusada pelo domínio com texto que explica a grafia
canônica, **sem** a UI corrigir o que o operador digitou. A moeda aparece
**derivada** da conta selecionada, somente-leitura, e jamais é enviada.

*Recusa nunca vira sucesso.* Máquina de estados do C3-S2 reusada
(`EDITING→SUBMITTING→{ERROR→EDITING · SUCCESS→CLOSED}`): erro é injetado
in-place e o rascunho sobrevive; `persistido:false` continua visualmente erro;
double-submit é inerte; cancelar é zero-write byte a byte. No sucesso o modal
fecha e `alladinRender()` re-projeta — **todo dado econômico exibido volta dos
read-models**, nunca do formulário.

*O convite respeita a sentinela.* Sob BLOCKING da sentinela do ALD-05-S1 o CTA
**não é renderizado** — a UX não convida a escrever sobre agregado que a
leitura recusou. Mas a autoridade continua sendo o domínio: write gate na
abertura E no submit (um agregado que vira schema futuro **entre** abrir o
modal e salvar é recusado por `aldMutate`, sem falso sucesso). Os seletores
listam só cadastro `ACTIVE` — filtro cadastral de UX; corrida entre render e
submit é decidida pelo domínio. TRANSFER **não** pré-filtra destino por moeda:
a recusa `ALD_TRANSFER_MOEDAS_DIFERENTES` é do domínio e não é duplicada.

**MD-2 continua dívida separada**: a escrita tem guarda própria e completa em
`aldMutate`; o envelope de `transactions()` segue pendente para slice própria.

## ALD-05 S3 — estorno pela UI (a UI oferece o ato; o domínio copia a economia)

A tabela de Lançamentos ganhou a coluna **Ações**, no final, com o botão
**"Estornar"** por linha. É a única mecânica de correção que um ledger
append-only reconhece — e todo o efeito econômico do estorno é **copiado do
original pelo domínio**.

*Elegibilidade visual, não autoridade.* O botão aparece para registro legível,
`eventType !== 'REVERSAL'`, `status === 'POSTED'` e **sem estorno existente**.
Linha já estornada ou linha `REVERSAL` mostram `—`, sem botão: a coluna Status
da mesma linha já explica, e um `disabled` ali exigiria justificativa que a
linha já dá. Sob write gate o botão vem `disabled`; sob sentinela BLOCKING não
há tabela, logo não há ação. **A decisão final é sempre de
`reverseTransaction`**, que re-resolve o id e revalida tudo dentro do
`aldMutate` — corrida entre render e clique termina em recusa honesta, nunca em
ato errado.

*O modal confirma o FATO, não simula a consequência.* Ele mostra o original em
**somente leitura** — evento, `effectiveAt`, valor por `money.format`,
conta/caixa, instrumento e `quantity` fiel do read-model, `reason` original
quando houver — e **não existe input algum para campo econômico**. Deliberadamente
**não** exibe "saldo previsto", "posição prevista" ou efeito líquido: calcular
isso seria reimplementar `−ALD_CASH_DELTA[original]` na apresentação. O efeito
aparece **depois**, pelos read-models.

*Editáveis apenas os três campos que a API aceita*: `effectiveAt` do estorno
(obrigatório — a reversão é fato novo com data própria), `reason` (opcional e
**próprio**: copiá-lo do original fabricaria justificativa) e `note`.
`dedupeKey` não é exposta, como no S2.

*Uma chamada por confirmação*: `reverseTransaction(originalId, {effectiveAt,
reason?, note?})`. A UI **nunca** usa `addTransaction` para estornar, nunca
inverte `amount` ou `quantity`, nunca toca o original — quem marca
`status: 'REVERSED'` é o domínio, dentro da transação. A recusa de estorno
duplicado é inequívoca sobre o estado persistido: *"Este lançamento já possui
um estorno. Nenhum novo estorno foi criado."*

**MD-2 continua fora**: a linha fornece apenas o `transactionId`, e o domínio
re-resolve e revalida tudo — `transactions()` sem envelope não é requisito
material para esta ação.

## Integridade estrutural — na LEITURA e na ESCRITA, dado inválido nunca vira número

A doutrina do MC-S2-1 — *"escrita correta não prova leitura íntegra"* — vale
para toda invariante que só a porta de escrita impunha. Saldo e posição são
calculados sobre o que está **persistido**, e um agregado adulterado (import
forjado, edição manual, corrupção parcial) podia produzir um **número plausível
e falso** sem que `aldTxLegivel`, que só olha **um** registro, percebesse.

**Identidade ambígua — o eixo `aldFindIn`.** `aldFindIn` resolve todo id por
**first-match**, na leitura **e** na escrita. Um id canônico duplicado
(`instrumentId`, `assetId`, `accountId`, `cashAccountId`, `transactionId`) torna
a identidade ambígua: o número sai atribuído a uma referência **arbitrária**, e
um ato novo (`addTransaction`, `reverseTransaction`, edição cadastral) operaria
sobre o **registro errado**. Não é apenas leitura — é write-safety.

`aldIntegridadeEstrutural(a)` é o juiz único, sobre o **agregado inteiro**:

- **unicidade de todo id canônico** nas cinco coleções;
- **container `transactions`** deve ser array (*"0 confiante"* é falso);
- **`transactionId`/`dedupeKey`** únicos; **≤1 REVERSAL** por original;
- **par status⟺reversal** (REVERSED exige 1 reversal; POSTED, nenhum).

Três consumidores o chamam: `saldoDeCaixa` e `posicoes` **antes de agregar**
(⇒ `BLOCKING`), e o **write gate `aldMutate` antes de qualquer mutação** (⇒
`ALD_INTEGRIDADE_ESTRUTURAL`, `fn` nem roda). Assim **nenhuma escrita nova
ocorre sobre um agregado cuja identidade esteja ambígua** — e o saldo ganhou
também a guarda de **schema futuro** que só `posicoes` tinha. A discriminação
decisiva: **dois fatos econômicos legítimos idênticos** (mesmo valor, ids
distintos, sem `dedupeKey`) **continuam somando** — só a corrupção provável
(id/dedupeKey compartilhados, que a escrita nunca gera) é bloqueada, na leitura
e na escrita. Provado por `alladin_ledger_test` L30–L39 e
`alladin_position_test` P18–P21; sensibilidade por mutação (10/10, incluindo a
remoção da integração no write gate).

## ALD-03 S3 — FEE/TAX standalone (despesa sem contraparte)

Uma taxa de custódia, uma manutenção de conta ou um imposto de período **não
pertencem a transação alguma** — e até aqui não tinham como ser registrados sem
distorcer um `WITHDRAWAL`, perdendo a natureza econômica que o Performance Book
(spec §31.3) precisa separar em `fees` e `taxesRecorded`.

```text
FEE   cash = −amount    papel = nenhum    flowScope AUSENTE
TAX   cash = −amount    papel = nenhum    flowScope AUSENTE
```

*Só-caixa, sempre saída.* A direção vem do `eventType`, como em todo o ledger;
`amount` segue magnitude positiva. A moeda é derivada da `CashAccount`,
divergência é recusa, e a mecânica de reversal é a existente — sem uma linha de
exceção: o par soma zero.

*`flowScope` ausente (DH-S3-2).* Uma taxa **não é retirada de capital** — é
custo que reduz o retorno. Marcá-la `EXTERNAL` a contaria como saída de
patrimônio e distorceria Net Contributions e TWR. Mesmo argumento que excluiu
BUY/SELL: `flowScope` classifica fluxo de capital pelo perímetro, não consumo
econômico.

*Sem vínculo a trade (DH-S3-3) — e é isso que fecha o ALD-I36.* A taxa de um
trade vive nos campos `fees`/`taxes` **do próprio trade**, embutida, e continua
lá: nenhum trade persistido é decomposto, migrado ou reinterpretado. Uma despesa
standalone **não aceita** `instrumentId`, `quantity`, `fees`, `taxes`,
`flowScope`, `transactionRef` ou referências de transferência — a presença de
qualquer um é recusa na escrita (`ALD_CAMPO_NAO_PERMITIDO_EM_DESPESA`) e
ilegibilidade na leitura. Assim *"a taxa do trade X"* **não existe** como
evento: a dupla contagem fica **irrepresentável**, sem nenhuma heurística de
igualdade econômica — o domínio não tenta adivinhar se duas despesas parecidas
são o mesmo fato.

### `schemaVersion` 4 → 5: identity migration, para não chamar de corrupção o que é versão

```js
if(a.schemaVersion===4){ a.schemaVersion=5; continue; }   // um elo, carimbo puro
```

Nenhum campo criado, alterado ou removido; nenhum trade tocado. O carimbo existe
porque **`eventType` é vocabulário persistido fechado**: um agregado com FEE/TAX
é semanticamente mais novo que um build v4. Sem a versão, esse build reportaria
`ALD_TRANSACAO_ILEGIVEL` — chamaria de **corrupção** um dado **válido produzido
por versão futura**. Com v5 ele cai em `READ_ONLY_FUTURE_SCHEMA` e diz a
verdade: quem está velho é o build. Provado pelo mixed-build W2 contra o código
**real** de `eb3fd6f`, e pelo caso W, que carimba um ledger **povoado**
preservando `quantity`, `fees`, `taxes`, `amount` e `flowScope` byte a byte.

## ALD-03 S4 — ADJUSTMENT (ajuste de reconciliação)

Um extrato que não fecha por dois centavos, um crédito que o banco lançou e não
explica, um arredondamento de custódia. São diferenças de caixa **reais** e
**sem contraparte econômica identificável** — e é exatamente essa ausência que
as distingue de tudo o que veio antes.

```text
ADJUSTMENT_CREDIT   cash = +amount   papel = nenhum   flowScope AUSENTE   reason OBRIGATÓRIO
ADJUSTMENT_DEBIT    cash = −amount   papel = nenhum   flowScope AUSENTE   reason OBRIGATÓRIO
```

*Dois tipos, não um campo de direção nem um `amount` assinado (DH-S4-2).* A
direção vem do `eventType`, como em todo o ledger — e assim ela já nasce
protegida pelo mesmo código que protege o resto: o espelho do par compara
`reversedEventType`, e o efeito da reversão é resolvido a partir do tipo do
**original**. Um `direction` avulso seria um segundo lugar onde a direção mora,
e o único protegido por nada.

*`reason` é obrigatório e é campo próprio (DH-S4-3).* O ajuste é o único evento
cujo valor **não pode ser conferido contra nada**: não há original de onde
herdar, nem contraparte com que comparar. A justificativa é a única coisa que o
torna auditável, então ela é parte da **forma** do registro — ausente, `null`,
`""` ou só espaços é recusa na escrita (`ALD_REASON_OBRIGATORIO`) e
ilegibilidade na leitura. `note` continua opcional e livre: nota é comentário,
`reason` é justificativa, e uma não cobre a outra. Nos demais tipos `reason` é
**proibido por presença** (`ALD_REASON_NAO_PERMITIDO:<tipo>`) — declará-lo num
DEPOSIT afirmaria uma semântica que aquele evento não tem, e ignorá-lo em
silêncio perderia o que o autor escreveu.

*Zero efeito em posição.* `ADJUSTMENT` não entra em `ALD_PAPEL_DELTA` e não
aceita `instrumentId` nem `quantity` — não existe forma de escrever um ajuste
que mova papel. As demais proibições são as da despesa: `fees`, `taxes`,
`flowScope`, `transactionRef` e referências de transferência.

*`ADJUSTMENT` não aponta para transação original.* Se existe lançamento errado
**identificável**, o caminho correto é `REVERSAL` — e a proibição de
`transactionRef` mantém os dois caminhos impossíveis de confundir. Reverter um
ajuste é permitido pela mecânica existente, e o `reason` da reversão é
**próprio**: copiá-lo do original fabricaria justificativa para um fato novo.

> [!warning] Fronteira para o Performance Book
> `ADJUSTMENT` **não é fluxo externo** e **não é ganho/perda econômico**. Ele
> altera o saldo *observado* sem afirmar que houve aporte, retirada ou
> rendimento. Quando o Performance Book existir, ele **não pode** ser absorvido
> em silêncio pelo residual `EconomicGain = Closing − Opening − NetExternalFlow`
> — a implementação **deve** segregá-lo explicitamente. Até existir política
> aprovada para isso, nenhuma matemática de performance é inventada aqui.

### Completude do `ALD_CASH_DELTA` — o fim do zero implícito

O fallback de `aldTxEfeito` devolvia `0` para qualquer `eventType` sem entrada
na tabela de deltas. Era a única falha do módulo capaz de produzir **número
plausível e falso** em vez de recusa: um tipo legível sem semântica de caixa
geraria saldo com `quality:'OK'` simplesmente **ignorando o evento**.

```js
const f = ALD_CASH_DELTA[tx.eventType];
if(!f) return null;          // não classificável — nunca zero implícito
```

`null` é o sentinela que a função já usava para o reversal órfão, e o saldo
distingue as duas causas: `ALD_REVERSAL_ORFAO:<id>` quando falta o original,
`ALD_CASH_DELTA_AUSENTE:<id>` quando falta a semântica. Mensagem errada é pista
falsa. **Não há guarda equivalente para `ALD_PAPEL_DELTA`**: ali a ausência é
legítima — eventos só-caixa não movem papel por definição.

### `schemaVersion` 5 → 6: identity migration, pelo mesmo motivo do elo anterior

```js
if(a.schemaVersion===5){ a.schemaVersion=6; continue; }   // um elo, carimbo puro
```

Nenhum campo criado, alterado ou removido; nenhum trade tocado. Verificado
empiricamente contra o build **real** de `451b01b`: diante de um agregado v6 com
`ADJUSTMENT`, um build v5 sem o carimbo reportava `ALD_TRANSACAO_ILEGIVEL` — e
seguia **escrevendo por cima**, porque seu `writeBlockReason()` era `null`. Com
v6 ele cai em `READ_ONLY_FUTURE_SCHEMA`, fecha a escrita e diz a verdade. Provado
pelo mixed-build X2, e pelo caso X, que carimba um ledger **povoado** com trade,
fluxo e despesa preservando tudo byte a byte.

## Fronteira normativa — C3 encerra aqui, ALD-03 começa depois

**C3 — Cadastro Patrimonial** responde **"o que existe?"**: Instrument, Asset,
Account, CashAccount, ownership cadastral (`owners/shareBp`), estado cadastral
(`recordStatus`) e a integridade da edição.

**ALD-03 — Ledger Patrimonial** responderá **"o que aconteceu economicamente?"**:
transações e eventos — aportes, retiradas, compras, vendas, transferências,
rendimentos, taxas, impostos, reversões e correções.

```text
CADASTRO + EVENTOS + VALUATIONS = ESTADO PATRIMONIAL DERIVADO
```

Cadastro é identidade e estrutura; eventos são a história econômica; valuations
são valor no tempo. **Posições, saldos, patrimônio e performance são derivados**
— nenhum deles é respondido pelo C3, e nenhum é persistido (ALD-I27).

## Próximas fases (nenhuma iniciada)

`ALD-03` transações, eventos, holdings e posições — onde nascem cost basis,
`flowScope INTERNAL|EXTERNAL` e o par atômico papel↔caixa · `ALD-04` valuation
e performance · `ALD-07` Data Quality e Audit Trail canônico.

### Amarras que o ledger vai reabrir (registradas, não implementadas)

- `CashAccount.accountId` e `currency` são editáveis **porque nada depende
  deles ainda**; com lançamentos, a restrição nasce junto com o ledger.
- `Asset.lifecycleStatus` é somente-leitura; as transições virarão **eventos
  patrimoniais**, não atos cadastrais.
- **DELETE não existe** — a política nasce com o ledger, que é quem saberá se
  um registro é referenciado.
- `symbolHistory` permanece cadastral e independente do ledger.
- `owners/shareBp` é cadastral: registra **título**, não valor. Nenhum valor
  proporcional é computado enquanto não houver valuation.
