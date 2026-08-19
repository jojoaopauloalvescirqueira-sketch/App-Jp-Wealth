# Changelog

## [Unreleased]

### Finanças Pessoais — Visão Geral (PF-06) — 2026-08-19

Branch `feature/personal-finance-overview-v2`. Em desenvolvimento — não integrada.

Consolidado derivado, nunca segunda fonte de verdade: quatro cards (mês atual,
dívida & crédito, vs mês anterior e pendências) que consomem exclusivamente
pfCompMetrics, pfTotalAllocated/pfUnallocatedSurplus, pfCreditKPIs,
pfCompCompare/pfCompBaselines e pfPendingBefore. Mês virtual declara-se não
registrado (a completude vácua de pfMonthSummary(null) jamais fabrica sobra);
sobra parcial não exibe valor; crédito é posição vigente rotulada; sentinela
de leitura em recusa integral (zero R$ sob unidade desconhecida). Zero
persistência nova, schema v1 intacto, render jamais escreve. Fora da V1 por
decisão de gate: projeção virtual monetária, mini-série, cenários, score —
e Patrimônio/Inventário, que deixaram de pertencer a Finanças Pessoais e
passam a ter domínio e roadmap próprios (INV-*).

### Finanças Pessoais — Cenários (PF-05) — 2026-08-19

Branch `feature/personal-finance-scenarios`. **Integrada** — candidate
`aa0baa1`, merge `--no-ff` `46dcbe6` em `main`, publicado em `origin/main`
(2026-08-19).

Hipóteses financeiras independentes, agrupadas por horizonte (HOJE ou YYYY-MM):
composição própria de receitas/despesas com valores obrigatórios, sobra e
cascata derivadas (último saldo ≡ surplus), cópia unidirecional a partir de mês
registrado (planejado, sem canceladas; fonte incompleta bloqueia nomeando as
faltas; ids novos; baselineFrom é proveniência, nunca vínculo vivo). Cenário
jamais escreve em months; mês editado jamais reescreve cenário.

Correção do Human Acceptance: sentinela de LEITURA — sob unidade monetária
desconhecida a tela permanece legível estruturalmente mas não interpreta
montante algum como BRL (totais, cascata e campos viram "—"); affordances
mutáveis desabilitadas por consistência (a segurança segue no write gate).
Round-trip `XX_UNIT → BRL_CENTS` restaura os valores exatamente.

### Finanças Pessoais — Comparativo Mensal (PF-04) — 2026-08-18

Branch `feature/personal-finance-monthly-comparison`. **Integrada** — candidate
`e2509d7`, merge `--no-ff` `bc6752a` em `main`, publicado em `origin/main`
(2026-08-19).

READ → DERIVE → COMPARE: consome os consolidadores canônicos do PF-02/PF-03 e
jamais recalcula o domínio. Comparação M−1 e M−12 estritamente de calendário;
soma parcial nunca vira baseline; sobra sem percentual; comprometimento em
pontos percentuais; baseline zero nega percentual e mantém delta; série de 12
meses com lacunas honestas; crédito vigente fora de leitura histórica;
patrimônio declarado pendente até o Inventário. Nada persiste.

### Finanças Pessoais — Dívidas & Crédito (PF-03) — 2026-08-18 (integrada, merge `73bdaab`)

Identidade temporal da dívida (startMonth/closedMonth) separada da observação
mensal (debtSnapshots); sem carry-forward; contrato não orfana história;
observação removível deliberadamente; "última observação" estritamente
anterior; limites de crédito como estado vigente com KPIs por cobertura e
estouro sem clamp; razão dívida/limite distinta de utilização.

### Finanças Pessoais — Orçamento Mensal (PF-02) — 2026-08-18 (integrada, merge `f6a7ffe`)

Write gate canônico (pfMutate); materialização por ato; receitas com
recorrência; despesas com dois canais; sobra realizada gateada por completude;
destino do excedente sem fabricação; pendências por status puro.

### Finanças Pessoais — Fundação (PF-01) — 2026-08-18

Branch `feature/personal-finance-foundation`. **Integrada** — candidate
`49027c2`, merge `--no-ff` `59a9681` em `main`, publicado em `origin/main`
(2026-08-18).

Nasce o domínio de Finanças Pessoais: agregado `S.personalFinance` com schema
v1 congelado (`moneyUnit BRL_CENTS` — inteiros em centavos, null ≠ 0),
normalizador que repara forma e jamais conteúdo, política monetária canônica
(`parseBRLCents`/`formatBRLCents`, sem ponto flutuante no caminho), sentinela
de unidade desconhecida (módulo em modo leitura, estado intacto), sobrevivência
integral a Finalizar Sessão (herança explícita — sem ela, uma ação existente
destruiria o módulo), round-trip de backup provado em contexto isolado, e o
menu `06 · Finanças Pessoais` com seis destinos skeleton. Nenhuma
funcionalidade de PF-02+ foi antecipada. Contrato: `docs/architecture/PERSONAL-FINANCE.md`.

### Operação Única — Histórico e Finalização formal — 2026-08-17

Branch `feature/exec-operation-history` (`c9fd11e → 17214ba`). **Integrada** —
candidate final `27a87cf` (rodadas corretivas posteriores a `17214ba`), merge
`--no-ff` `9ac5a8a` em `main`, publicado em `origin/main` (2026-08-18).

A Operação Única existia como conceito espalhado pelas grades: um conjunto de
ordens que o operador sabia pertencerem à mesma tese, sem nada no estado que o
afirmasse. Fechar a última ordem apagava a operação da tela sem deixar registro,
e a fase máxima atingida — informação que só existe enquanto a operação vive —
se perdia junto.

Passou a ser entidade persistida, com encerramento formal e memória
institucional consultável.

**Distinção central.** Fechar a última ordem **não** finaliza a Operação. O Art.
4.4 do Estatuto já dizia isso textualmente — "zeragem tática sem confirmação de
encerramento não extingue a Operação" — e prescreve dupla confirmação por
registro escrito `FECHADO`, que é o protocolo da revisão implementada.

**Três camadas.** Fundação (`activeOperation` persistida, com proveniência de
abertura e captura prospectiva da fase máxima), finalização transacional
(`candidato → validar → trocar → save() → rollback`, com o desfecho de exceção
decidido pela leitura do disco, não pela pilha) e Histórico somente leitura, com
denominadores explícitos em toda estatística.

**Nada de dado inventado.** Abertura de operação legada é informada pelo
operador com proveniência `manual_legacy`; desconhecido nunca vira zero, agora
ou falso; conflito de instrumento ou direção bloqueia a finalização em vez de o
sistema escolher por conta própria.

#### Série corretiva

Revisão adversarial por 24 agentes acusou um BLOCKER de fiação e sete defeitos
materiais. Cada correção em commit próprio, com campanha de mutação individual.

- **`1a0c40c`** — a auditoria de governança era registrada **depois** de
  `save()`, existindo só na memória da sessão e morrendo no reload. Passou a
  nascer dentro do candidato: uma persistência lógica, e o `recordId` é o
  `operationId` real em vez do identificador vazio do log legado.
- **`ba3be3a`** — a revisão era construída uma vez, na abertura do modal, com
  `defenseCount:0` cravado. O operador aprovava um registro e outro ia ao disco.
  A revisão passou a ser repintada a cada entrada manual, com o mesmo objeto que
  `finalizeOperation` recebe. `closedAt` é carimbado na confirmação, e a tela diz
  isso por extenso em vez de exibir um horário que será outro.
- **`a21dcd8`** — abertura informada no futuro produzia registro imutável
  afirmando que a operação foi aberta depois de encerrada, e o único sinal era
  uma duração exibida como `—`, o mesmo traço de "dado indisponível". Passou a
  ser recusa: `openedAt <= closedAt`, sem correção automática, sem conversão para
  `null`, sem `Date.now()` disfarçado.
- **`bfc2b59`** — a busca do Histórico reescrevia o cartão inteiro a cada tecla e
  destruía o próprio campo. Repintura passou a ser parcial.
- **`f64cea2`** — a guarda de exclusividade procurava referência só entre ordens
  `Aberta`. Com a Gênese fechada e a operação viva, liberava outro instrumento e
  outra direção, e o estado resultante era irreparável pela interface. Passou a
  usar a mesma noção de pertencimento do domínio.
- **`be43dde`** — `maxAccountPhaseIntegrity` era binária sobre realidade
  ternária: operação cuja fase jamais foi capturada era persistida como
  `observed`. Ganhou `unobserved`. E `compute()` devolvendo fase ausente da
  matriz deixou de passar por "não aplicável" e virou defeito nomeado.
- **`17214ba`** — as citações `Art. 3.5`/`3.6` apontavam para artigos
  inexistentes. Corrigidas para `4.2`, `4.4` e `5.1`, conferidas contra a Norma
  Vigente.
- **`e7313aa`** — a sonda que decide o destino de uma finalização devolvia
  booleano, e um `catch(_){ return false; }` transformava leitura impossível em
  prova de ausência. `setItem` gravava, uma exceção posterior interrompia o
  fluxo, a leitura de volta falhava, o sistema concluía "não gravou", a memória
  voltava para a operação ativa e o `save()` seguinte apagava do disco uma
  finalização que estava lá. Passou a haver três desfechos — `CONFIRMED`,
  `NOT_PERSISTED` e `UNKNOWN` —, com a confirmação exigindo `operationId` **e**
  `finalizedAt`, porque uma tentativa anterior da mesma operação daria como
  persistida uma gravação que não foi esta. No `UNKNOWN` nada é revertido, nada
  é declarado, e uma barreira própria — separada do portão genérico e sem função
  pública de liberação — veta toda gravação futura.

`be43dde` e `e7313aa` são itens distintos. O primeiro foi commitado sob o rótulo
do segundo por perda de contexto, e a correção de rótulo está registrada no
`CURRENT-STATE.md`.

#### Segunda rodada: três defeitos de afirmação histórica

Auditoria adversarial de nove lentes devolveu `AUDIT_FAIL` com 13 achados
invalidantes, que colapsavam em três defeitos — todos gravando afirmação falsa em
registro imutável.

- **`e6f653d`** — `operationTouchAccountPhase()` rodava dentro de `save()`, e
  `save()` é chamado a cada **tecla** nos campos numéricos da grade. Digitar
  "1.09" passa por "1", cujo risco eleva a Fase da Conta; a captura é monotônica,
  então o pico virava `maxAccountPhaseReached` e ia ao disco com integridade
  `observed`. Medido: fase real 2, digitar "1" levava o máximo a 3, e terminar o
  número não o trazia de volta. A captura saiu de `save()` e passou a ocorrer só
  em atos semanticamente confirmados.
- **`58be507`** — `handleStopLimitBreach` destrava fase e carimba o evento via
  `operationStampTransition`, que lê `S.activeOperation`; o nascimento da entidade
  estava **depois** dele, então o destravamento provocado pela própria Gênese saía
  com `operationId: null`, era descartado, e o registro afirmava "Fase máxima da
  Grade: FASE 1" para uma operação que viveu inteira na FASE 2. A ordem causal
  passou a ser: guardas rejeitadoras → nascimento → efeitos operation-scoped.
- **`13b9811`** — apagar as linhas esvaziava a operação fora dos atos formais;
  `activeOperation` sobrevivia órfã e a tese seguinte herdava identidade, abertura
  e proveniência. Medido: registro GBPUSD gravado como aberto em 1º de agosto, com
  `genesis_transition`, sob o `operationId` da operação anterior.
- **`d161207`** — interação entre as duas correções acima: a captura rodava antes
  do fail-safe, então ia para a entidade que seria descartada e a recém-nascida
  saía sem observação do próprio instante de nascimento.

#### Terceira rodada: as regressões da correção C

A auditoria dirigida a C, B e A encontrou três caminhos em que a captura, retirada
de `save()`, não havia sido reposta. Um quarto foi reclassificado por decisão
humana.

- **`ffa637a`** + **`c2b17c5`** — `handleStopLimitBreach` nunca reverte o stop.
  Nas saídas sem confirmação — frase recusada, limite da Gênese, defesa final da
  Fase 4, limite absoluto — o valor permanece e é persistido, e a conta passa a
  operar acima do teto da fase sem que nada observe.
- **`356fe37`** — devolver o Status a `—` caía no ramo genérico do `<select>`:
  nada limpava `activeOperation` e o carimbo `openedAt` ficava na linha, então
  reabrir a mesma linha pulava o fail-safe e a tese nova herdava a identidade.
  Passou a ser retirada explícita da ordem do ciclo, com a mesma semântica do
  abandono por exclusão.
- **`d328e2b`** + **`b5b5766`** — a captura que C pusera dentro de
  `finalizeOperation` rodava depois de o operador aprovar a revisão, enquanto
  `repintarRevisao` monta o record sem capturar: numa operação adotada de legado a
  revisão mostrava `—`/`unobserved` e o registro saía com valor/`observed`. A
  captura foi para um checkpoint explícito, antes de qualquer record existir.
- **`ca301de`** — trocar o instrumento muda `orderRisk()` tanto quanto mudar o
  lote. A troca aceita é persistida pela saída terminal do laço de `<select>`, que
  ficou sem captura. Medido com saldo 40.000: `USDJPY` → `EURUSD` leva o risco de
  15,44 para 2.500 USD, drawdown de 6,25% contra teto de 4%, e o máximo
  permanecia zero; estreitado o stop depois, a captura do `<input>` observava a
  fase já recuada e a monotonicidade selava a subestimação.

O princípio ficou completo: **valor transitório não captura; valor rejeitado e
revertido não captura; valor que sobrevive à guarda e é persistido captura.**
`operationTouchAccountPhase` nunca voltou para `save()`.

#### Evidência

92 experimentos de mutação ao longo das três rodadas, todos acusados por asserção
própria ou registrados como no-op provado — nenhum aceito por `TypeError`. Treze
precisaram de correção antes de valer como evidência, e cinco sobreviventes ficaram
registradas como redundância funcional, não como lacuna.

Gate `standard` 17/17 em cada commit e tier `full` **28/28** sobre o candidato
`ca301de`, ambos lidos integralmente, com o artefato do `full` registrando
`head: ca301ded4c3c`.

A lente de auditoria independente `R4` **não foi executada** e foi **dispensada
por waiver explícito** do responsável:

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

`waiver ≠ AUDIT_PASS` — a lente não passou, foi dispensada. Base objetiva:
testes de interface do R4 3/3, mutação com 2 acusadas e 1 no-op provado,
`standard` 17/17, `full` 28/28 sobre `ca301de`, e a lente de interação `R4×C`
concluída com zero achados.

Desenvolvimento do Histórico **encerrado**; o próximo gate é a aceitação humana.

Categoria de teste nova: `operation_wiring_test.py`, evento real de DOM
atravessando domínio, estado e disco. Criada porque o BLOCKER passou por testes
unitários verdes — o gancho estava num laço morto sobre `<input>` enquanto o
campo Status é um `<select>`.

### Quality Gate de CI restaurado — 2026-08-17

O repositório passa a ter integração contínua. Até aqui `.github/` continha
apenas `pull_request_template.md`, e **nenhum commit da história havia criado
`.github/workflows/`** — exceto um, esquecido.

- **Recuperado de uma branch abandonada, não escrito do zero.** O arquivo veio
  de `045c264` (2026-08-10), preservado na tag `archived/governanca-multiagente`.
  Não fora superado: em 92 commits posteriores a `main` nunca escreveu
  equivalente nem registrou decisão de dispensar CI. Ficou invisível atrás de um
  nome enganoso — a branch chamava-se `audit/governanca-multiagente` para um
  commit "Create quality-gate.yml" feito pelo editor web do GitHub.
- **Um defeito corrigido antes de restaurar.** O passo de setup declarava
  `cache: pip` sem `cache-dependency-path`. O cache do `setup-python` procura
  `requirements.txt` ou `pyproject.toml`, e este repositório não tem nenhum dos
  dois — a única lista é `requirements-dev.txt`. O workflow morreria na segunda
  etapa, antes de rodar teste algum. Restaurar CI quebrado não restaura CI.
- **Gatilho alinhado ao fluxo real.** O original só disparava em `pull_request`
  e `workflow_dispatch`, mas o trabalho aqui é feito em branch, mesclado
  **localmente** e publicado direto em `main` — nenhuma integração desta série
  passou por PR. Sem `push: branches: [main]` o gate ficaria instalado e mudo.
  `pull_request` foi preservado para o caso de PRs voltarem a ser usados.
- **Tier por gatilho:** `push` e `pull_request` caem em `standard`, que é o que
  o `CHANGE-PROCESS.md` exige para N0-V e N1; `full` fica acessível por
  acionamento manual, para candidato de release e mudanças N2/N3.
- **Compatibilidade auditada contra o estado atual:** a única dependência
  externa dos testes é `playwright`, já pinada em `requirements-dev.txt`; o gate
  dispara subprocessos por `sys.executable`, então o Python do `setup-python` é
  o mesmo que roda os testes; e `playwright install --with-deps chromium` basta,
  porque **Node.js não é requisito** — `validate_project.py` cai para o Chromium
  do Playwright para validar sintaxe JavaScript.
- **Não verificado:** os dois SHAs de action pinados
  (`actions/checkout@11bd719`, `actions/setup-python@a26af69`) não puderam ser
  conferidos contra o remoto — a máquina de trabalho não tem credencial de rede
  para a API do GitHub. A pinagem por SHA é a postura correta de supply chain e
  foi preservada intacta, mas se a primeira execução falhar, é o primeiro
  suspeito: o gate em si roda 13/13 localmente.

### Calendário Econômico no Execution Board — 2026-08-17

Terceiro destino do submenu, entre Painel Operacional e as ferramentas de
estudo. **Um domínio, duas instâncias visuais** — o overlay `#ecalOverlay`
continua existindo com seus dois pontos de entrada intocados.

A premissa de origem da tarefa era que o calendário "pertencia ao Dashboard" e
precisava ser extraído. A auditoria mostrou outra coisa: o que vive no Dashboard
é o widget de **Notícias**; o calendário já era superfície global, e já
consumia o cache do widget sem fetch, cache ou sanitização próprios. O trabalho
real não era criar fonte única — era **quebrar uma dependência de ciclo de vida**
e dar ao calendário casa canônica.

- **A dependência invertida, eliminada.** `initFfNews()` abria com
  `if(!card) return` sobre o card do Dashboard, e esse `return` matava os dois
  `setInterval`, o listener `online` e o fetch inicial. O ciclo de vida do dado
  era refém da presença física de um nó do Dashboard. Separado em
  `initFfNewsWidget()` (view) e `initFfNewsDomain()` (cache, rede, timers).
  Segundo acoplamento no mesmo eixo: `ffNewsRender()` saía cedo sem os nós do
  widget e engolia junto a repintura do calendário — o fan-out virou
  `ffNewsRenderAll()`.
- **Render parametrizado por raiz.** `ecalRenderRoot(root, filter)` resolve os
  nós por `data-ecal-role` dentro da raiz recebida. O overlay preserva os 9 ids;
  o workspace não tem id interno algum. Reusar o markup produziria ids
  duplicados — e, pior que DOM inválido, `#exec` precede o overlay no documento,
  então `getElementById` devolveria os nós errados e o modal ficaria sem render.
- **Filtro é estado de apresentação, não de domínio.** Os eventos são
  compartilhados; o recorte de moeda de cada superfície não. O overlay reabre em
  Todas; o workspace preserva a escolha na sessão.
- **Bind invertido.** O widget passou a ser dono do próprio botão `⋯` e chama
  `window.JPWEcal.openMenu()`; antes o calendário buscava `#gdNewsMoreBtn` dentro
  do card. O chip de moeda deixou de usar `.gd-news-cur`, classe namespaced sob
  o shell do Dashboard, e ganhou `.ecal-cur` com as mesmas declarações.
- **Achados da revisão adversarial do próprio diff, corrigidos:** a repintura do
  workspace em subárvore invisível a cada minuto (faltava checar `.screen.active`
  — `hidden` não é limpo ao sair do módulo); a região `aria-live` reescrita a
  cada tique, que fazia o leitor de tela reanunciar o mesmo rótulo; e uma
  varredura do teste que continuou literal depois de o commit anterior afirmar
  tê-la corrigido.
- **`06-boot.js` não foi tocado**, deliberadamente: o gancho que repinta o
  workspace visível existe porque NoCoda e Pivots derivam de `S`. O calendário lê
  `localStorage` — incluí-lo implicaria dependência inexistente.
- **Inalterados:** fornecedor, URL, frequência, TTL, formato do cache, política
  de timezone, classificação de impacto e semântica dos eventos.
- **Verificação — automação:** `quality_gate.py --tier standard` executado e
  aprovado, **13/13 PASS**, zero `FAIL`, zero `NOT_RUN`, zero
  `ENVIRONMENT_ERROR` (`tools/.artifacts/quality-20260817T151725-standard.json`).
  Node.js não era requisito: `validate_project.py` cai para o Chromium do
  Playwright, e o tier foi rodado a partir de uma venv isolada com
  `playwright==1.60.0`, o pino do `requirements-dev.txt`.
  `run_economic_calendar()` **foi executado e passou**.

  > Correção de registro: até a reconciliação de 2026-08-17 esta entrada
  > afirmava que "nada foi executado em navegador" e que o teste novo "vale como
  > especificação, não como evidência". Era verdade quando escrita — o ambiente
  > não tinha Playwright — e deixou de ser assim que o tier rodou. Fica anotado
  > em vez de reescrito em silêncio.

- **Verificação — mutação:** o teste novo foi submetido a quatro defeitos
  plantados no produto e **acusou os quatro**, provando que as asserções não são
  vazias: (1) `window.JPWEcalUI={render:ecalRender}`, que faria o workspace
  desenhar na raiz do overlay — o cenário exato que a revisão adversarial
  apontara como invisível ao gate; (2) o chip de moeda voltando a
  `.gd-news-cur`; (3) `id="ecalBody"` no corpo do workspace, colidindo com o
  overlay; (4) o filtro deixando de recortar por moeda. Controle após restaurar:
  PASS.
- **Verificação — visual:** `INSPEÇÃO VISUAL HUMANA NÃO REALIZADA`. Foi coletada
  **evidência automatizada por captura de tela** das cinco superfícies
  (card do Dashboard, workspace do Execution Board, overlay pelo menu `⋯`, tema
  claro e mobile a 390 px), com medição em runtime de zero id duplicado e zero
  overflow horizontal. Isso é a mesma classe de evidência do gate — Chromium
  dirigido por automação — e **não substitui o julgamento visual de um humano**,
  que segue pendente. Um `PASS` visual só pode ser registrado aqui depois que o
  gestor inspecionar e informar as superfícies conferidas.
- **Ambiente:** o registro do service worker falha no navegador embutido usado na
  captura (`sw.js` é servido em HTTP 200, mas `register()` recusa). É restrição
  do sandbox: `sw.js` não foi tocado por nenhum commit desta tarefa. O ciclo do
  worker é coberto pelo tier `full`, que **não** foi executado.

### Reconciliação de contagens defasadas e do padrão ARIA do FX — 2026-08-17

Drift documental acumulado pela série de submenus: cada tarefa reconciliou os
arquivos do próprio escopo e deixou para trás números que outras páginas ainda
declaravam. Nada de runtime, teste, manifest, worker ou gerado foi tocado.

- **Contagem de scripts corrigida em três páginas.** `ARCHITECTURE.md` declarava
  53 e `CODE-MAP.md`/`README.md` declaravam 60; o manifest tem 65 desde a
  integração dos Estudos dos Pivots. Conferido de forma independente: 65 em
  `src/js/manifest.json`, os mesmos 65 no precache de `sw.js` e a ordem do
  `index.html` idêntica à do manifest. A fotografia do `CODE-MAP.md` passou de
  `478a558`/`55d2267` para `7a93602`/`a188f29`/`f1c1f36`.
- **Contagem por tier corrigida.** `README.md` e `QUALITY-GATES.md` declaravam
  `standard` 9 e `full` 19; os valores reais, lidos de `TIERS` em
  `tools/quality_gate.py`, são 13 e 24. As suítes `exec-submenu`, `nocoda`,
  `pivot-studies` e `order-guards` entraram no `standard` sem que a tabela fosse
  reconciliada — e o `CURRENT-STATE.md` já registrava `PASS 24/24`, de modo que
  a documentação contradizia a própria evidência do gate.
- **Padrão ARIA do Planejamento FX corrigido.** `FX-PLANNING.md` afirmava que os
  quatro modos usavam `tabpanel`, `aria-controls`, foco roving e navegação por
  setas. Não usam desde que a faixa estrutural compartilhada assumiu a seleção:
  os modos vivem em botões `data-nav-sub-view` de `#fxplanNavSubmenu` e o
  conteúdo é `role="region"` com `aria-label` próprio. Verificado — a string
  `tabpanel` não aparece em `src/js/` nem no `index.html`. Era o único ponto em
  que a documentação descrevia uma **superfície de acessibilidade inexistente**.
- **Deixado intacto por serem históricos corretos:** "46 scripts" do baseline
  `d9510dbb55f0`, "53 scripts" do candidato `codex/galton-board` e "63 scripts"
  na evidência da `ACTIVE-TASK` descrevem o estado da época, não o vigente.
- **Verificação:** `quality_gate.py --tier fast` PASS 3/4 e `git diff --check`
  PASS. O check `structure` (`validate_project.py`) retornou `ENVIRONMENT_ERROR`
  — Node.js e Playwright ausentes na máquina —, e por isso os tiers `standard` e
  `full` ficaram `NOT_RUN`. A mudança não alcança runtime.

### Correções da caça a bugs por execução real — 2026-08-14

Oito achados confirmados por execução em navegador e reproduzidos de forma
independente por um segundo verificador, mais um que eu mesmo achei relendo o
código dos Pivots. **Um deles não sobreviveu à minha própria tentativa de
reprodução e por isso NÃO virou código** — está registrado abaixo.

**Segurança**

- **XSS armazenado no Mapa de Liquidez do questionário de início.**
  `S.onboarding.fcrLiquidity` e `feoLiquidity` chegavam a `innerHTML` sem
  `esc()`, enquanto todos os vizinhos do mesmo painel já escapavam. Pela
  interface são `<select>` de opções fixas, mas `migrate()` não normaliza campo
  algum de `S.onboarding` — o vetor é o backup, que o projeto trata como arquivo
  externo hostil. Verificado: um payload usando só APIs do app alterava o MDD
  estatutário e destravava as quatro fases.

**Integridade do estado**

- **Backup com agregado de forma errada era gravado antes de quebrar.**
  `checklist`, `accounts` ou `instruments` vindos como objeto atravessavam
  validação e migração sem lançar; `S=imported` e a gravação aconteciam **antes**
  de `boot()`, que só então estourava. Quando o erro aparecia a base original já
  não existia, e como `migrate()` não lançara o modo de recuperação A-005 não
  entrava: sem cópia, sem bloqueio, sem aviso, tela em branco. Agora a recusa
  acontece antes de tocar em qualquer coisa.
- **`migrate()` não repunha sub-chaves de `S.params`.** O laço genérico só cobre
  o primeiro nível. Sem `saldoIni`, `compute()` fazia `dd=0` e `tetoRisco=NaN`, e
  o veredito caía no ramo mais permissivo — o terminal exibia "FASE 1 —
  OPERACIONAL NORMAL / COERENTE" com risco aberto real de US$ 5.000. Limiares
  normativos ausentes voltam de `DEFAULTS`; **saldo e data não são inventados** —
  na falta do denominador o estado é tratado como corrompido e roteado para a
  recuperação, que preserva a base.
- **Importação de backup não atravessava as abas.** Era o único fluxo que
  substitui o documento inteiro sem avisar as demais: a primeira gravação da aba
  antiga ressuscitava a base anterior por cima do que o operador acabara de
  restaurar. Passa a difundir pelo mesmo canal da Zona de Perigo e da
  Finalização, com semântica própria — a aba remota recarrega em vez de zerar.

**Limite estatutário**

- **Troca de par na grade escapava do teto de risco da fase.** O ramo de
  `<input>` aplicava `checkPhaseCap()` a lote, entrada e stop; a troca de
  instrumento não passava por ela, e o risco em USD muda por fator de até duas
  ordens de grandeza com a moeda de cotação. **Nenhum parâmetro normativo mudou**
  — aplica-se a checagem que já existia, com os mesmos limites, a um caminho que
  estava sem ela.

**Estudos dos Pivots**

- **Workspace montado sob demanda não repintava quando `S` era substituído.**
  Quem estivesse com Estudos NoCoda ou Estudos dos Pivots aberto durante uma
  importação continuava vendo — e clicando — um estudo que a importação acabara
  de eliminar, com os três caminhos de ação morrendo em `return` silencioso.
  `boot()` passa a repintar o workspace visível, e as ações avisam em vez de não
  fazer nada.
- **Criar estudo descartava o rascunho de pivot sem perguntar**, ao contrário de
  todos os outros caminhos que trocam o foco.
- **Pivot sem cálculo possível ficava preso.** Vindo de backup, era contado no
  total ("1 de 3") mas não aparecia em filtro nenhum, sem editar e sem excluir —
  preservar sem dar acesso é pior que apagar. Agora aparece em linha degradada,
  com o motivo e as duas ações.

**Não corrigido, e por quê**

- O achado de que **Finalizar Sessão apagaria os Tickets** com uma segunda aba
  aberta **não reproduziu aqui**: a aba remota grava o documento já com o Ticket,
  com ou sem correção. Uma correção chegou a ser escrita e foi **removida** ao
  não passar no teste de mutação. Fica registrado em `CURRENT-STATE.md`.
- Dos 27 achados brutos da caça, **17 nunca foram verificados** — a verificação
  adversarial foi limitada a dois por dimensão. Os 8 confirmados vieram desse
  subconjunto.

**Defeito introduzido e pego pelo gate:** a primeira versão do gancho de repintura
guardava com `typeof execGetView==='function'`. A declaração de função é içada,
mas o `let execView` que ela lê fica na zona morta temporal na primeira execução
— o boot inteiro estourava. A guarda passou a ser o objeto `window.JPWExec`, que
só existe depois de o módulo avaliar.

**Testes:** dois arquivos novos no tier `standard` —
`tools/order_guards_test.py` (guarda estatutária, com caso de controle que
falharia se a guarda recusasse tudo) e `tools/state_integrity_test.py` (backup
hostil, backfill de params, importação entre abas). `pivot_studies_test.py` e
`import_xss_security_test.py` foram estendidos. Todas as asserções novas passaram
por teste de mutação: a correção é revertida e a suíte tem de acusar. Gate
`--tier full` PASS 24/24.

### Estudos dos Pivots — MVP — 2026-08-14

Quarto destino do Execution Board deixa de ser superfície reservada e recebe
função: memória empírica dos maiores pivots H1/H4 que o operador identificou no
gráfico. O software não detecta pivots — ele estrutura, calcula, compara,
organiza e preserva o que foi observado.

- **Navegação sem obra nova.** O item, o container `#execPivots` e o registro em
  `EXEC_VIEWS` já existiam desde a reestruturação do módulo. Só a descrição do
  item mudou e o placeholder saiu. Nenhum controlador, dropdown ou sistema de
  hover foi criado.
- **Instrumentos da fonte canônica.** `instrumentCatalog()`, a mesma que o Motor
  de Lote e os Estudos NoCoda consomem. Não existe lista própria, e o teste falha
  se um símbolo aparecer nos arquivos da feature. O seletor oferece o catálogo
  operável mais os instrumentos que já têm estudo, para que remoção no Motor de
  Lote não torne memória técnica inalcançável.
- **Estudo histórico, não vigente.** Diferente do NoCoda, `S.pivotStudies` é
  LISTA: vários estudos do mesmo instrumento coexistem por período e nenhum
  sobrescreve o outro. Período sobreposto avisa e não proíbe.
- **Só causas persistem.** Timeframe, extremos de tempo e preço, correção
  informada e observação. Direção, range, amplitude percentual, duração, veredito
  do critério, ranking e toda a estatística são derivados a cada leitura — há
  teste que falha se um derivado for gravado.
- **Critério de correção em ponto único.** `PIVOT_MAX_CORRECTION_PCT = 61.8`,
  limite invalidante (`< 61,8` atende). A interface lê a constante e não repete o
  número. É **critério informado, não verificado**: o app não tem OHLC e não
  afirma ter conferido o histórico do mercado.
- **Nada é destruído por classificação.** Pivot que passa a exceder o limite é
  reclassificado e marcado, nunca apagado; filtro, troca de timeframe, de
  instrumento ou de período não removem registro. A única exclusão é explícita e
  confirmada.
- **Estatística descritiva com viés declarado.** `n` sempre acompanha as medidas
  centrais; `n = 0` mostra "Sem dados" e nunca `0%`. A tela declara que a amostra
  é selecionada pelo operador, e o teste varre o texto renderizado atrás de
  linguagem de probabilidade, expectativa ou previsão.
- **Convenção temporal reusada.** O parser de carimbo MT5 dos Estudos NoCoda é
  chamado, não duplicado — dois parsers do mesmo dado seriam duas verdades.
- **Dois defeitos achados na revisão adversarial do próprio candidato e
  corrigidos antes da entrega:**
  - o critério de correção era unilateral (`< 61,8`) e não conferia o domínio
    0–100%. Pelo formulário não havia como explorá-lo, mas um **backup
    adulterado** — o mesmo vetor dos três achados `Medium` da auditoria — com
    `maxCorrectionPct: -500` atravessava a normalização (que de propósito não
    apaga registro), entrava na amostra **principal** como "atende ao critério" e
    envenenava a mediana das correções. O domínio passou para o núcleo; o
    registro segue gravado, agora rotulado "correção fora de 0–100%".
  - trocar de estudo ou de instrumento com o formulário de pivot aberto e
    **limpo** não o fechava: ele continuava apontando para um pivot de outro
    estudo, e o `Salvar` seguinte não achava o alvo e retornava em silêncio — o
    operador digitava, clicava e nada acontecia. Agora a troca fecha o
    formulário, e salvar com alvo inexistente produz mensagem explícita.
- **Testes:** `tools/pivot_studies_test.py` no tier `standard`. A suíte foi
  submetida a teste de mutação com dez defeitos plantados no produto (critério
  inclusivo, mediana sem caso par, ordenação lexicográfica, amplitude no
  denominador errado, duração aceitando instantes iguais, preço igual virando
  baixa, derivado persistido, filtro que não filtra, critério unilateral e
  formulário sobrevivendo à troca de estudo) — os dez foram acusados.
- **Reconciliação:** contrato em `docs/architecture/PIVOT-STUDIES.md`; agregado
  em `STATE-SCHEMA.md`; scripts 63 → 65 em manifest, `sw.js`, HTML e portátil.
  Aproveitou-se para corrigir duas defasagens de inventário anteriores —
  `SECURITY-MODEL.md` ainda declarava 53 scripts no precache em uma segunda
  ocorrência, e `NOCODA-STUDIES.md` nunca entrara em `PROJECT-FILES.txt`.

### Correções de segurança da auditoria — 2026-08-13

Os três achados `Medium` que sobreviveram à verificação adversarial. Todos
compartilhavam o mesmo vetor: um backup adulterado — inclusive o próprio backup
do operador alterado numa pasta sincronizada, que é o cenário realista.

- **Matriz Quadrifásica deixou de ser aceita do arquivo.** `S.matrix` é catálogo
  normativo fechado, mas `migrate()` validava só a forma: um backup com
  `ddmax:0.99`/`alav:99` atravessava e passava a definir fase vigente, teto de
  risco e teto de alavancagem, com o terminal exibindo "COERENTE" sob exposição
  muito além do limite estatutário. Agora `canonicalizeStructuralMetadata()` a
  reconstrói de `DEFAULTS`, pela mesma doutrina já aplicada às fases e aos
  tickers. **Nenhum valor normativo mudou** — a fonte oficial passou a
  prevalecer sobre o arquivo.
- **XSS armazenado em `S.params.inicio` corrigido.** O campo chegava a
  `innerHTML` sem escape no resumo do onboarding, enquanto todos os vizinhos
  usavam `esc()`. A varredura do template confirmou que era a única omissão.
- **Zona de Perigo passou a atravessar as abas.** A limpeza total invalidava a
  geração de persistência só da própria aba; outra aba mantinha o estado em
  memória e a primeira gravação dela ressuscitava a base inteira. Reutiliza o
  canal da Finalização de Sessão com tipo e handler próprios, porque a semântica
  difere: a Zona de Perigo preserva preferências auxiliares e cópias de
  recuperação, e o texto que o operador confirma promete exatamente isso.
- **Reconciliação:** `SECURITY-MODEL.md` registra os três em "Riscos resolvidos"
  e teve corrigida a contagem de scripts do precache, que estava em 53 (real: 63).

### Motor de Lote migrado para o Execution Board — 2026-08-13

- **`Configurações → Operação → Motor de Lote` virou `Execution Board → Motor de
  Lote`**, quinto destino do submenu. O acesso antigo foi removido: não existe
  mais caminho duplicado.
- **Nenhuma reimplementação.** É o mesmo `#motorWidgetGrid`, movido de dentro da
  `section#motor` para dentro de `section#exec` — nenhum nó recriado, nenhum id
  alterado, nenhum listener refeito. `renderMotor()`, os cálculos, os tetos, o
  câmbio e a persistência ficaram intocados.
- **Persistência sem mudança alguma:** `S.instruments`, `S.expAlvo` e
  `ins.unlocked` continuam idênticos. Nenhum schema, migração ou dado tocado.
- **Cinco estruturas da Central saíram juntas** — `children` do grupo Operação,
  `SETTINGS_LEAVES`, o painel, o mapa de transporte de DOM e um ramo de gatilho
  de câmbio. A remoção do transporte era obrigatória:
  `restoreLegacySettingsNodes()` reanexava o grid à `section#motor` a cada
  fechamento da Central e o arrancaria de dentro do Execution Board.
- **Código morto removido:** o gatilho de câmbio "1× por sessão" da Central
  nunca disparava — `06-boot.js` já o executa no boot, carrega antes e a flag
  nunca é resetada. O comentário obsoleto em `01-navigation.js` foi corrigido.
- **Atributos vestigiais removidos** dos dois cards do Motor: `data-layout-card`
  não estava registrado no motor de layout, mas faria a regra
  `html[data-layout-editing] .screen.active [data-layout-card] > *` congelar o
  botão de câmbio, o input de exposição-alvo e as tabelas durante uma sessão de
  personalização do Execution Board.
- **Ação Rápida do Dashboard preservada** por `SCREEN_TO_MODULE_VIEW`, irmão do
  mapa que ele substitui. Sem ele, `navigateToScreen('motor')` limparia todas as
  telas ativas e sairia sem ativar nenhuma, deixando o app sem tela visível.
- **Estudos NoCoda inalterado:** continua consumindo `instrumentCatalog()`,
  derivado de `S.instruments`. O Motor sempre foi outro consumidor da mesma
  fonte, não a fonte — por isso movê-lo não afeta o NoCoda.

### Estudos NoCoda — MVP — 2026-08-13

- **Novo destino `Execution Board → Estudos NoCoda`**, terceiro item do submenu,
  entre Painel Operacional e Estudos dos Pivots. Usa a faixa contextual genérica
  já existente; nenhum controlador paralelo foi criado.
- **Memória técnica por instrumento:** três âncoras (data/hora + preço) que
  reconstroem a geometria do Fibo Channel, com dois resultados derivados ao
  vivo — range entre os níveis −1 e 0, e range da subdivisão de 0,125.
- **Núcleo matemático isolado** em `src/js/10-domain/09-nocoda-geometry.js`:
  puro, determinístico, sem DOM, sem `S` e sem `localStorage`. O range é medido
  projetando a linha 0 até a terceira âncora — nunca por `abs(P3−P1)` ou
  `abs(P3−P2)`, que ignoram a inclinação. Níveis por índice inteiro, sem
  acumular `0,125` em laço.
- **Fonte canônica preservada:** os instrumentos vêm de `instrumentCatalog()`,
  derivado de `S.instruments`. Não há lista, símbolo ou metadado de instrumento
  escrito no NoCoda, e o teste falha se aparecer.
- **`instrumentId()` formaliza a identidade que já existia** — o `name`
  normalizado, extraído de dentro de `instFor()` para uma função única. Nenhum
  campo novo no catálogo, nenhuma migração de dado, nenhuma segunda identidade.
- **Agregado aditivo `S.nocoda`** com guarda estrutural `nocodaNormalizeState()`
  em `migrate()`. Persiste apenas causas — âncoras e `updatedAt`; toda geometria
  é recalculada. Estudo de instrumento removido da lista operacional é
  **preservado**. Estado anterior à feature continua carregando.
- **Calcular não é salvar:** a prévia atualiza a cada tecla, a persistência só
  ocorre no clique explícito, e trocar de instrumento com alterações pendentes
  pede confirmação antes de descartar.
- **Nada disto autoriza operação:** navegar ou salvar um estudo não altera fase,
  clearance, risco, alavancagem, ordem, LIFO, quarentena ou contabilidade —
  verificado por teste de não regressão que compara os domínios operacionais
  antes e depois.
- **Teste novo** `tools/nocoda_test.py`, no tier `standard`, com a fixture
  canônica da especificação e as invariantes de sinal e de nível.

### Segundo nível do Execution Board e generalização da faixa — 2026-08-13

- **Execution Board ganhou segundo nível** com três destinos, nesta ordem:
  **Visão Geral** (superfície estrutural nova, sem indicador, cálculo ou
  resumo financeiro), **Painel Operacional** e **Estudos dos Pivots**
  (superfície reservada, também sem conteúdo funcional).
- **O Painel Operacional é o `#execWidgetGrid` de sempre.** Nenhum nó foi
  movido, nenhum dos 67 ids internos mudou, os quatro widgets continuam filhos
  diretos da grade e a preferência de layout gravada não foi tocada. A
  realocação é de hierarquia de navegação, não de conteúdo — não houve
  duplicação de HTML, controlador, estado, listener ou renderizador.
- **Troca por `hidden` + `inert`, sem desmontar:** alternar workspace preserva
  valores digitados, foco, disclosures abertos e o DOM injetado pelos
  renderizadores. Nenhum estado de ordem, fase, risco ou LIFO foi criado,
  alterado ou removido; nada do segundo nível é persistido.
- **Visão Geral é o destino inicial do módulo**, aplicada ao entrar vindo de
  outra tela por observação da classe `.active` — reabrir a faixa estando já no
  Execution Board não tira o operador do Painel Operacional.
- **Faixa do segundo nível generalizada e compartilhada:** `#fxNavSubmenuShell`
  e o prefixo `.fx-nav-*` deram lugar a `#navSubShell` e `.nav-sub-*`, com o
  controlador dirigido por registro em vez dos dez ganchos cravados em `fx`.
  O módulo aberto passou a ser distinguido por `aria-expanded` no próprio
  acionador; o atributo global anterior acendia todos de uma vez. Planejamento
  migrou para o mesmo motor sem mudança de comportamento.
- **Teste novo** `tools/exec_submenu_test.py`, registrado no tier `standard`:
  estrutura em fluxo, deslocamento, destino inicial, equivalência do painel,
  preservação de estado, teclado, `inert` verificado por comportamento, hover e
  fixação, troca de módulo, não regressão das cinco abas, temas e mobile.

### Navegação hierárquica de Planejamento — integrada localmente em 2026-08-13 (`478a558`, merge `55d2267`)

- **Planejamento ganhou um segundo nível estrutural** com Visão Geral,
  Planejamento FX, Realizado e Histórico. A faixa fica entre o header global e
  o contexto, participa do fluxo e desloca o conteúdo em 300 ms; não é popup,
  overlay, card ou sidebar.
- **Uma única fonte visível de navegação:** as tabs equivalentes foram removidas
  do conteúdo, preservando os quatro renderizadores e usando somente
  `window.JPWFx.ui.selectView()` para a seleção visual.
- **Hover transitório e clique fixado:** hover fino abre e fecha após tolerância
  de 400 ms; clique, Enter ou Espaço fixam a faixa. Pointerleave, resize, novo
  clique no acionador e seleção de item não fecham; clique externo ou Escape
  encerram o estado.
- **Terceiro tom próprio:** o fundo combina tokens do header e do contexto,
  produzindo contraste intermediário coerente nos temas claro e escuro.
- **Mobile em fluxo:** tocar em Planejamento fecha a gaveta global e expande os
  destinos empilhados sem overlay nem overflow horizontal.
- **Sem mudança financeira ou persistida.** Nenhum cálculo, estado, schema,
  chave de storage, backup ou componente de domínio foi alterado.
- O padrão reutilizável foi registrado em
  `docs/architecture/NAVIGATION-HIERARCHY.md` e ligado ao mapa de contexto.
- **Validação:** teste focal PASS, `quality_gate.py --tier full` PASS 19/19,
  portátil reproduzível e Build ID `4d9b36661c689c26`.

### Fidelidade integral ao Claude Design e upgrade PWA coerente — candidato de 2026-08-13 (branch `feature/claude-design-fidelity`)

- **As cinco telas foram reconciliadas com o protótipo** no mesmo shell
  horizontal, com navegação clássica por sublinhado e gaveta vertical no mobile.
  Dashboard passou a aviso/cockpit full-width, quatro cards P2 e análise 3:2;
  drawdown e comparação mensal permanecem acessíveis dentro do disclosure de
  metodologia.
- **Execution Board** passou a clearance compacto com quatro fatos, Grade e
  monitor LIFO 2×2. Stop Estatístico, indicadores complementares e ATR/VRM
  continuam editáveis/acessíveis em disclosures; nenhum ID ou cálculo foi
  removido.
- **Contas** ganhou leitura primária de dez colunas, chip de credenciais e
  editor completo expansível. Adicionar conta abre o editor e foca o nome; as
  duas tabelas rolam dentro dos próprios cards em 390 px, sem contaminar a
  largura do documento.
- **Contabilidade** agora apresenta quatro indicadores no topo, Real vs
  Projetado e Fechamento em 3:2 e lançamentos full-width. **Planejamento FX**
  usa cartão central de 936 px e formulário vazio linear; os quatro modos
  existentes permanecem inalterados quando há plano.
- **Upgrade PWA corrigido na raiz.** Um cliente controlado pelo worker anterior
  recebe o `index.html` do cache anterior e permanece integralmente naquele
  build enquanto o worker novo espera. Após fechar todos os clientes, a próxima
  abertura recebe o build novo coerente online e offline; nenhuma limpeza de
  storage nem takeover forçado foi introduzido.
- **Responsividade e temas verificados em navegador real** nas cinco telas em
  1440×900 e 390×844, claro/escuro, com uma única tela ativa, menu mobile
  vertical, zero overflow horizontal e console limpo nos fluxos exercitados.
- **Sem mudança normativa ou de persistência.** Fórmulas, constantes, perfis,
  fases, DD/MDD, lote, LIFO, stops, quarentena, contabilidade, MEI-JP,
  Planejamento FX, `DEFAULTS`, `migrate()` e chaves de storage permanecem
  inalterados.
- **Validação:** `quality_gate.py --tier full` PASS 19/19, build reproduzível,
  teste de upgrade PWA aprovado e portátil reconstruído oficialmente. Build ID
  `54a60f3e45fdd76c`.
- **AGENTIC IMPACT DETECTED.** Lifecycle PWA, teste/gates e contexto visual são
  consumidos por agentes e skills; arquitetura, contexto, changelog e handoff
  foram reconciliados. Agentes/routing herdaram as fontes e não exigiram edição;
  `INDEX NOT REQUIRED`, `SYSTEM RECONCILED`.

- **Fase 2C · reconciliação das cinco telas com o protótipo.** Execution Board:
  9→6 cards (Postura, Termômetros e Coerência absorvidos pelos quatro fatos do
  cockpit, que ganhou Drawdown e passou a levar os tetos no rótulo, como o
  protótipo); os seis tiles informativos do LIFO desceram para "Leitura
  patrimonial e arquivados ▾", ficando à vista os quatro consolidados P1.
  Contas: as colunas derivadas (Correção, Normalização V10, Fator de Perfil)
  saíram da leitura primária com o cálculo preservado no `title` da célula de
  Lote vs Mestre, e as três credenciais viraram um chip único ("3 pendentes").
  Contabilidade: Simulação Patrimonial e Projeção Diária em `▾`. Planejamento
  FX: as três camadas em "Como as três camadas funcionam ▾".
- **Layout de grade alinhado ao protótipo.** As quatro telas tinham todos os
  cards travados em `full`, o que empilhava tudo em largura cheia por mais
  disclosure que se acrescentasse — era a causa real de "não estar parecido".
  Ampliada a política de tamanho dos cards que o design põe lado a lado e
  ajustados os defaults: Contabilidade passou a dois pares (Período|Ritmo e
  Real vs Projetado|Fechamento), de 2038px para 1263px; Contas foi de três
  cards para **dois**, com a Nota de Governança virando `governança ▾` no
  cabeçalho do Parque; Planejamento FX virou cartão único de **936px centrado**,
  medida idêntica à do protótipo; Execution Board passou a Clearance → Grade →
  Consolidado, a ordem do design. Ampliar `allowed-sizes` não invalida
  preferência salva, então nada disso exigiu migração.
- **Stop Estatístico com o método em disclosure.** O bloco §9 do Execution Board
  reduziu-se ao que o protótipo mostra: os vereditos (Múltiplo de ATR, Raiz-N
  √30 e √55, Síntese §9.5) ficam à vista e os campos de método — ATR(55)%,
  Fator F e Stop Técnico — descem para `método ▾`, seguindo editáveis e no
  mesmo lugar do DOM. O card caiu de 1196px para 1000px.
- **`exec-vrm` foi PRESERVADO contra o protótipo.** Ele hospeda `iAtr55` e
  `iAtr660` — inputs editáveis vinculados sem guarda em `08-input-bindings.js` e
  escritos por `04-stop-statistics.js`. Removê-lo quebraria os dois e eliminaria
  a única entrada dos ATRs, que alimentam o VRM e a classificação de regime. O
  §3.4 manda sair "gauges/termômetros", não os inputs.
- **Migração v5 → v6** para a tela `exec`, na mesma cadeia das anteriores.
  Corrigido no caminho um defeito que teria sido silencioso e grave: o envelope
  promovido nascia com `version: 5` enquanto o normalizador exigia 6 — era
  rejeitado e **todas as telas caíam no padrão**, descartando a personalização
  que a migração acabara de preservar. Verificado em base zerada: reordenação do
  Execution Board e `news-high-impact` na sidebar sobrevivem à promoção.

### Limpeza do Dashboard e reconciliação com o protótipo — candidato de 2026-08-13 (branch `feature/dashboard-cockpit-p1`; JPW-789ABC-B2, Fases 2B e 2C)

- **Cinco componentes redundantes saíram do Dashboard** — faixa de métricas,
  Coerência de Alavancagem, Termômetros, Postura e Perfil e Contexto. O mesmo
  fato chegava a aparecer cinco vezes; agora cada um tem uma representação
  primária. De 10 cards para **6**; a altura do Dashboard caiu para 923px.
- **Migração de preferência v4 → v5**, única e não destrutiva: remove os cinco
  ids extintos, coage `operational-clearance` de `large` para `full` (em duas
  colunas as células cairiam para ~98px e truncariam dado financeiro) e
  renumera, preservando zona e tamanho dos sobreviventes. Sem ela, o validador
  reprovaria por três caminhos independentes e descartaria **toda** a
  personalização da tela, não apenas os removidos. Verificado com snapshot v4
  de 11 widgets e três personalizações — todas preservadas.
- **Corrigida uma inversão na cadeia da v2**: `dashLayoutValidateV2Legacy`
  validava ANTES de migrar; com 11 widgets contra 6 esperados reprovaria sempre
  e a v2 cairia no padrão em silêncio.
- **A camada causal do veredito foi recuperada.** `#mcClearanceReasons` já era
  calculado por `getOperationalClearance` mas vivia fora do cockpit, num
  `.jp-section` invisível — ninguém nunca o viu. Agora fica entre subtítulo e
  fatos, oculto quando não há violação e, quando há, nomeando o fato,
  quantificando e apontando o remédio ("podar $120 via LIFO"). Substitui com
  vantagem os rótulos binários da Postura ("Risco Controlado").
- **Fase 2C — reconciliação com o protótipo aprovado.** Auditoria das cinco
  telas contra `JP Wealth - Redesign.dc.html` revelou que o cockpit fora
  construído a partir do handoff textual, não do protótipo. Corrigido, com as
  medidas tiradas do próprio arquivo: grid de **duas colunas** (527|738 no
  protótipo, proporcional aqui), veredito de 58px para **34px**, células de
  fato como **cards** (fundo `panel-2`, borda `line`, radius 10, padding 14/16),
  barra de 5px, valor colorido pelo estado, **duas ações** e os rótulos do
  design (`Fase da Conta`, `Drawdown Operacional`, `Alavancagem Carregada`).
- **Informação recuperada nas metas**, que o protótipo tinha e o App perdera:
  `postura ofensiva` (que morreu com a faixa de Postura), `alarme em 13,00% ·
  guilhotina 15,00%` (os dois limiares, não só o teto) e `margem $80`.
- Nenhuma constante, fórmula, fase, teto ou parâmetro normativo foi tocado;
  `jpwealth_v9_state` e o formato de backup seguem inalterados. Preservados por
  verificação: `gaugeDD`/`gaugeAlav`/`objectiveCard` do Execution Board,
  `11-phase-posture.js` (alimenta `renderObjective`), `#dDDmax` (usado pelo
  `smoke_test.py`) e o CSS de `mc-metric-strip`/`mc-mini-card`, ainda em uso.
- **Pendente:** o protótipo cobre cinco telas e só o Dashboard foi reconciliado.
  Execution Board, Contas, Contabilidade e FX seguem no desenho legado — e
  nenhuma delas tem a camada P3 (`<details>`) que o protótipo usa como
  mecanismo central. Registrado para os blocos seguintes.
- **AGENTIC IMPACT: nenhum.** Nenhuma skill, agente, router ou documento de
  governança referencia os componentes removidos.

### Cockpit operacional e VRM compacto — candidato de 2026-08-13 (branch `feature/dashboard-cockpit-p1`; JPW-789ABC-B2, Fases 2A e 2A.5)

- **O card de Clearance virou o cockpit operacional.** Passou a `full` (4
  colunas) e ganhou os quatro fatos que antes viviam espalhados pelo Dashboard:
  **fase · drawdown · risco aberto · alavancagem**. Cada um é uma célula com
  rótulo, valor, escala e contexto — sem gauge, sem dial, sem termômetro. A
  linha de texto anterior (Fase/Risco/Alavancagem) foi absorvida, preservando o
  mesmo destino de clique (`data-dash-scroll="governanca"`) e o chevron.
- **O valor carrega só o número corrente** (`FASE 1`, `3,20%`, `$320`,
  `1,62x` — máx. ~7 caracteres); teto e contexto descem para a meta em 9,5px.
  A regra existe por medição: foi a concatenação `$320 / $400` dentro do valor
  que truncou a 960px na faixa de métricas.
- **Espelho de leitura, sem cálculo novo.** Toda fórmula é reuso literal da
  vigente: `ddCeil` e as faixas de `c.mScaled` vêm do `gdGaugeDD`;
  `riscoTotal/tetoRisco` da `gRiscoBar`; `alavCar/4` com tick do teto em
  `tetoAlav/4` do `gdGaugeAlav`. As cores seguem as regras já em vigor — `--f3`
  para risco acima do teto, `--f2` para alavancagem acima do teto.
- **Estouro nunca transborda.** A barra satura em 100% e a exceção é dita por
  cor **e** por texto (`ACIMA DO TETO`, `NO LIMITE ATIVO`). Teto zero — conta
  sem parâmetro — mostra trilho vazio e `sem parâmetro de teto`, nunca divisão
  por zero nem barra cheia falsa. Verificado nos sete estados extremos.
- **VRM compacto (Fase 2A.5).** O dial cônico saiu: era a terceira geometria de
  leitura da mesma grandeza. No lugar, a **mesma** barra do cockpit
  (`.mc-fact-track/-fill/-mark` reusados, sem CSS paralelo) na **mesma** escala
  que o dial já usava — `vrmHV × 1,15` — com os dois limites de regime marcados
  (`vrmN` e `vrmHV`, de `02-risk-calculations.js:47`). O card virou `medium` e
  divide a linha com o Status do Sistema. ATR(55) e ATR(660) desceram para
  `<details>` nativo — P3, leitura informativa. Valor, regime e limites
  permanecem visíveis sem interação.
- **Reordenação do Dashboard.** O par P2 (Status do Sistema + VRM) subiu para a
  linha logo abaixo do cockpit. Não reintroduz a inversão que o Bloco 1
  corrigiu: os quatro fatos P1 mudaram de dono e agora vivem no cockpit, então a
  faixa de métricas, os termômetros, a coerência e a postura passaram a ser
  duplicatas aguardando remoção, e desceram para o bloco de legado.
- **Nada foi removido.** Faixa de métricas, Coerência de Alavancagem,
  Termômetros, Postura e Perfil e Contexto seguem na tela, de propósito: esta
  etapa valida a equivalência dos números lado a lado antes da remoção
  definitiva na Fase 2B. A redundância aumenta temporariamente — é o custo da
  verificação.
- **Correção visual de fechamento (P1 da revisão).** O VRM esticava até a
  altura da linha (232px) com o conteúdo terminando aos 165px, deixando 45px de
  vazio no rodapé enquanto o Status ao lado usava toda a altura. O disclosure
  passou a ancorar na base (`margin-top:auto`), com o card em coluna flex — o
  **pré-requisito** sem o qual aquele `auto` seria inerte num card `display:block`.
  É a mesma estrutura que o Status já usava. Auditoria A/B dos cinco filhos:
  apenas o disclosure mudou de posição; os outros quatro mantiveram topo,
  altura e margens idênticos.
- Nenhuma constante financeira, fórmula, fase, teto, perfil ou parâmetro
  normativo foi tocado. `jpwealth_v9_state` e o formato de backup permanecem
  inalterados; a preferência de layout continua em **v4**, sem migração —
  quem já personalizou mantém a escolha até a Fase 2B, e o VRM em `compact`
  legado foi verificado sem truncamento nem overflow.
- **Limitação conhecida:** `.gd-vrm-main` e `.gd-vrm-dial` ficaram sem uso no
  CSS. A limpeza foi deliberadamente adiada para a Fase 2B, que produzirá
  órfãos de cinco cards de uma vez — uma limpeza única é mais auditável que
  duas parciais.
- **AGENTIC IMPACT: nenhum.** Nenhuma skill, agente, router, `AGENTS.md`,
  `CLAUDE.md` ou documento de `docs/governance/` referencia o cockpit ou o VRM.
  As âncoras `[data-layout-card]` de todos os cards foram preservadas.

### Status do Sistema — candidato de 2026-08-12 (branch `feature/system-status-panel`; JPW-789ABC)

- **O painel institucional decorativo virou estado operacional.** Aquele bloco
  era `aria-hidden`, sem texto, sem controle, um `repeating-linear-gradient` em
  135° ocupando `large` (2×2 ⇒ ~444×619 em viewport 1440) como **segundo**
  elemento da coluna principal — e, no mobile, o segundo da tela inteira, antes
  dos dados de risco. No lugar dele, quatro linhas de estado que já existiam no
  sistema e não tinham casa no Dashboard: **persistência · backup · frescor das
  cotações · governança do período**.
- **Espelho de leitura, não fonte nova.** `renderSystemStatus()` só lê:
  `jpWealthPersistenceFailure`/`jpWealthPersistenceIsBlocked()` (A-001),
  `S.dataGovernance.backup.lastConfirmedAt`, `S.instruments[].updated` via o
  **mesmo** `staleInfo()` do Stop Estatístico (limiares ≤3 / ≤20 / 21+ seguem com
  dono único, não foram reimplementados) e `getOnboardingCompletionState()` — a
  mesma severidade do banner de onboarding, para as duas superfícies nunca
  discordarem. Nenhum cálculo novo, nenhum estado paralelo, nenhuma escrita.
  "Revisar ›" reusa `openFirstIncompleteOnboarding()`.
- **A cor nunca é o único canal (WCAG 1.4.1).** O ponto é decorativo e o estado
  está sempre escrito no rótulo — "Backup confirmado" vs "Backup não
  confirmado". As quatro linhas com rótulo são CRITICAL OPERATIONAL: comprimem
  meta, rodapé e subtítulo, mas nunca somem, em nenhuma largura.
- **Rebalanceamento do cockpit.** Encolher o painel de `large` para `medium`
  expôs **263–386px de vazio** ao lado do Clearance, que segue em 2×2. A faixa
  de métricas (P1) subiu para a linha 1 da coluna direita e o Status (P2) desceu
  para a linha 2: o vazio fecha em **zero** e a ordem de leitura deixa de ser
  P1 › P2 › P1 — o Status partia o par P1 ao meio — para ser **P1 › P1 › P2**.
  Abaixo de 1280px o Clearance passa a ocupar as quatro colunas: a 2 colunas ele
  cresce em altura (546px a 1180, 648px a 960) e arrastava o Status para 0,79 de
  proporção, mais alto que largo. Só `span`, nunca `order` — ordem visual segue a
  do DOM (WCAG 1.3.2, mesma razão pela qual a grade não usa `dense`).
- **Migração de preferência v3 → v4, única e não destrutiva.** `large` deixou de
  ser permitido para o painel e `full` deixou de ser o padrão da faixa; sem
  migrar, `dashLayoutValidateScreenWidgets` devolveria `null` para a **tela
  inteira** e jogaria fora toda a personalização do Dashboard. A coerção de
  `large` fica permanente no validador (é tamanho proibido, não atropela
  escolha); a de `full` acontece **uma vez**, na promoção de envelope — `full`
  continua legal para a faixa, e coagi-lo a cada carga o tornaria impossível de
  salvar, já que `dashLayoutFinish()` também valida antes de gravar. Verificado:
  personalização preservada na promoção, e escolher `full` depois dela persiste.
- **Três defeitos corrigidos no caminho**, todos expostos pela mudança e
  confirmados por medição: (a) o `min-height` do componente nascia morto — o
  reset `[data-layout-card]{min-height:0}` pontua (0,3,1) e vencia um seletor de
  classe; (b) os limiares de `@container` disparavam 44px cedo demais, porque
  `inline-size` consulta o *content box* e os números da spec são do *card* — o
  card de 264px do mobile, acima do mínimo de 240, já caía em modo chip; (c) a
  regra de 2 colunas da faixa em `medium` pontuava (0,2,1) e perdia para
  `html[data-ui-version="tesla-inspired"] #mcMetricStrip` (1,1,1), da camada
  Tesla — inócuo enquanto a faixa era `full`, mas ao promovê-la para `medium`
  passava a truncar dado P1 ("FASE 1" → "FASE…", "$320 / $400" → "$320…").
- **Limitação conhecida:** na faixa estreita (≤1279px) a caixa do valor tem
  ~100px e os números quebram em linha em vez de truncar; um token único acima
  de ~10 caracteres (`$1.234.567`) ainda corta. Inalcançável na conta atual
  (teto de risco $400) — registrado como pendência, não corrigido aqui.
- Nenhuma constante financeira, fórmula, fase, teto, perfil ou parâmetro
  normativo foi tocado. `jpwealth_v9_state` e o formato de backup permanecem
  inalterados; `save()` não foi modificado (o carimbo `hh:mm:ss` da linha de
  persistência exigiria mudança N2 e ficou de fora).
- **AGENTIC IMPACT: nenhum.** Nenhuma skill, agente, router, `AGENTS.md`,
  `CLAUDE.md` ou documento de `docs/governance/` referencia o painel
  institucional. A âncora `[data-layout-card="institutional-panel"]` foi
  **preservada** de propósito: é o contrato de relocação e a chave das
  preferências de layout já gravadas; só o rótulo humano e o tamanho mudaram.

### Tickets MVP — candidato de 2026-08-12 (branch `feature/tickets-mvp`; JPW-NPQRST, JPW-QRNPKM, JPW-785634)

- **JPW-NPQRST — menu de ações do ticket.** Cada card ganhou um `⋯` que abre um
  popup moderno com as ações reais do ticket: **Copiar referência · Concluir
  ticket · Exportar como Markdown · Excluir ticket**. Reutiliza a infraestrutura
  do modal de criação (overlay local à gaveta, focus trap, Escape, clique fora)
  — `.mvpn-sheet-overlay`/`.mvpn-sheet-box` passaram a ser as regras
  compartilhadas pelas duas superfícies, sem terceira arquitetura de popup. O
  ícone de cópia do card virou o primeiro item do menu; nenhuma ação sumiu.
- **Concluir com confirmação.** Selecionar "Concluir ticket" não altera nada:
  abre confirmação e só então grava, pelo mecanismo oficial (`mvpNotesUpdate`),
  que já carimba `completedAt` e preserva os demais campos. Cancelar não escreve
  — verificado por comparação byte a byte do estado. Ticket já concluído não
  recebe a ação (nada de "Reabrir" nesta tarefa). Rascunho sujo do mesmo ticket
  bloqueia a conclusão, mesma regra da exportação.
- **JPW-QRNPKM — críticos no topo.** `priority === 'critical'` ganha precedência
  em `mvpNotesGrouped()` e na seleção em massa. É ordenação **derivada**: nada é
  gravado, nenhuma posição persistida, nenhuma data tocada. Dentro de cada grupo
  o critério que sempre valeu (ordem natural por título) permanece intacto, e a
  precedência é aplicada depois do recorte e da separação ativas/concluídas —
  um crítico concluído sobe entre as concluídas, nunca volta ao backlog ativo.
  Não havia ordenação escolhida pelo usuário a preservar: o módulo só tem ordem
  de sistema.
- **JPW-785634 — o módulo passa a se chamar Tickets.** Renomeação **apenas de
  apresentação**, em `index.html` e em quatro módulos (`14-mvp-notes.js`,
  `07-finalize-session.js`, `05-wipe-all.js`, `09-settings-modal.js`).
  Preservados sem tocar: a chave `jpwealth_v9_state`, o agregado `S.mvpNotes`,
  `schemaVersion 5`, todos os IDs, os nomes de função e arquivo, o formato de
  backup e os contratos de importação/exportação. Nenhuma migração. A busca da
  Central ganhou "Tickets" **mantendo** "Notas do MVP"/"notas" como alias, para
  quem procurar pelo nome antigo continuar achando o cartão.
- Não foram tocadas as ocorrências de "notas" que significam *anotações* fora do
  módulo (`01-daily-ledger.js`, `04-persistence.js`: "anote manualmente os
  registros — ordens, fechamentos e notas").
- Corrigido no caminho: o menu não devolvia o foco ao `⋯` quando fechado por
  clique no backdrop — clicar em elemento não focável leva o `activeElement`
  para `<body>`, e a guarda anterior só devolvia o foco se ele estivesse *dentro*
  do overlay.
- **AGENTIC IMPACT: nenhum.** Nenhuma skill, agente, router, `AGENTS.md`,
  `CLAUDE.md` ou documento de `docs/governance/` depende semanticamente do nome
  "Notas". `docs/architecture/CODE-MAP.md` foi atualizado por ser descrição de
  superfície.

### Notas do MVP · exportar e copiar em massa — candidato de 2026-08-12 (branch `feature/mvp-notes-bulk-export-copy`, JPW-436587)

- Duas ações novas na barra da lista, operando sobre o **recorte visível**
  (pasta ativa + filtros + busca), não sobre a pasta bruta: **Copiar N** leva o
  lote para a área de transferência como Trace References; **Exportar N** gera
  um documento Markdown único. O número no rótulo é o que será levado.
- O recorte é `mvpNotesFiltered()` — o mesmo que pinta a lista. "Copiar as notas
  abertas da pasta X" é um caso particular disso (filtro de status dentro da
  pasta), então não existe segundo mecanismo de seleção a manter em sincronia.
- **Critério:** leva o backlog ativo, excluindo Concluída e Descartada. A visão
  "Concluído" é exceção declarada — ali o recorte É o histórico concluído, e
  aplicar a exclusão devolveria sempre zero. A confirmação da exportação declara
  os dois números ("mostra 5 notas · exportar as 3 ativas"), então a diferença
  entre visível e levado nunca é silenciosa.
- **Preâmbulo de governança no lote copiado.** Cada Trace Reference termina com
  uma instrução dependente da política de IA da nota; concatenar notas de
  políticas diferentes produziria instruções contraditórias em sequência. O lote
  abre declarando a composição (`1 autorizada · 1 somente análise · 1 bloqueada`)
  e a regra de leitura: nenhuma autorização se estende de uma nota a outra. Os
  blocos individuais seguem íntegros — nada foi removido.
- **Leitura pura, verificada por teste:** `S.mvpNotes` byte a byte idêntico antes
  e depois das duas ações. Sem `save()`, sem `dgLogChange`, sem rede (também
  coberto por teste). Não é backup e não se confunde com um: o backup completo
  da base mantém governança própria de sequência e trilha.
- Markdown reutiliza `mvpNotesMarkdown()` literalmente por nota, incluindo o
  front matter, com delimitador em comentário HTML (`<!-- jpwealth:note … -->`)
  — invisível no render e inequívoco para dividir o arquivo de volta. Nome de
  pasta hostil (`a --> <b> c`) é neutralizado antes de entrar no comentário.
- O download reutiliza `dgDownloadViaAnchor()`, o helper endurecido do projeto,
  em vez de repetir a âncora inline como faz a exportação individual.
- Corrigido no caminho: a regra do tema
  `html[data-ui-version="tesla-inspired"] :is(…, .modal-btn.cancel, …)` vale
  **(0,3,1)** — o `:is()` herda a alternativa de duas classes —, então prefixar
  com o tema apenas EMPATA e perde por ordem de origem. Os botões saíam com 42px
  de altura e 20px de padding, espremendo o rótulo da visão até "INTER…".
  Resolvido com `#mvpNotesBulkActions` (1,1,0), mesmo recurso já usado em
  `.mvp-notes-toolbar #mvpNotesNewBtn`. `.mvp-notes-toolbar` passou de
  `align-items:baseline` para `center`.

### Notas do MVP · configuração inicial da nota — candidato de 2026-08-12 (branch `feature/mvp-notes-creation-modal`, JPW-CBA987)

- Criar uma nota passa a abrir o modal **"Nova Nota"** antes do editor: tipo,
  prioridade, status inicial, pasta e permissão de IA são decididos na origem,
  em vez de permanecerem no padrão até alguém abrir o inspector. O editor abre
  em seguida, sem nova aba nem nova tela.
- O modal vive **dentro** de `#mvpNotesDrawer`, não no `#modalOverlay` global:
  aquele é irmão anterior da gaveta com o mesmo `z-index` (200), então
  renderizaria por baixo dela, e o focus trap do módulo o tornaria inalcançável
  por teclado. Nenhum token de camada compartilhado foi tocado — o questionário
  de transição de fase e o onboarding seguem intactos.
- Os cinco selects são preenchidos a partir dos **mesmos enums canônicos** que o
  inspector já usava (`MVP_NOTES_TYPES/PRIORITIES/STATUSES/AI_POLICIES` e
  `folders[]`). Nenhuma categoria nova, nenhum sistema de pastas paralelo.
- **Schema intocado (v5).** Os metadados continuam em campos planos do item; não
  há agregado `metadata:{}` nem migração. Backup, importação, exportação em
  Markdown e Trace Reference seguem lendo exatamente os mesmos campos, e notas
  antigas abrem, editam e exportam sem alteração.
- Cancelar, `Escape` e clique fora não criam nota nem tocam o estado — a nota
  continua nascendo apenas em `mvpNotesSaveDraft()`, com a primeira linha como
  título. Escolher metadados no modal não marca o rascunho como não salvo.
- Acessibilidade: enquanto aberto, o modal toma o focus trap da gaveta
  (`mvpNotesTrapFocus` passa a usar `#mvpNotesNewBox` como raiz), `Escape` fecha
  só a camada mais interna e o foco volta ao botão "+". Em ≤920px vira coluna
  única com alvos de 44px.
- Correção descoberta na verificação: `.mvp-notes-head` é um `<header>` e herda
  `z-index:40` da regra global do arquivo — com `z-index:4` o modal renderizava
  por baixo do cabeçalho da gaveta, que permanecia clicável. Elevado a 50,
  contido no contexto de empilhamento do próprio drawer (`position:fixed`).

### Planejamento FX — candidato de 2026-08-11 (branch `feature/fx-planning`)

- Nova área **Planejamento FX** na tela Contabilidade: motor de planejamento
  patrimonial temporal para Forex com três camadas separadas — planejado
  (premissas), realizado (histórico contábil) e normativo (reservas do
  Estatuto) — e três séries: baseline congelado, forecast vigente (rolling
  forecast a partir do último fechamento real) e realizado imutável.
- Convenções documentadas e testadas: rentabilidade sobre o saldo de abertura
  com aportes após o resultado; realizado com a mesma álgebra do MEI-JP
  (`R_aj = (V_t − V_{t−1} − F_t)/V_{t−1}`); precedência de overrides
  mês > ano > padrão; horizonte livre (1–600 meses) com meses gerados
  programaticamente.
- Ledger cambial de aportes com custo médio ponderado
  (`Σ BRL ÷ Σ USD`); entradas USD-nativas (`affectsFxCostBasis:false`) nunca
  contaminam o custo; aquisição, valuation e projeção cambial são conceitos
  separados.
- A matemática FCR/FEO foi extraída de `reserveCalc()` (onboarding) para a
  função pura compartilhada `reserveRequirementsCalc()`
  (`src/js/10-domain/07-reserve-requirements.js`), com caracterização campo a
  campo; onboarding e Planejamento FX consomem a mesma fonte — nenhuma
  constante normativa duplicada, nenhum artigo alterado.
- Novo agregado aditivo `S.fxPlanning` (schemaVersion 1) em
  `jpwealth_v9_state`: guarda estrutural em `migrate()`, normalização profunda
  em cópia na camada de acesso, campos desconhecidos preservados, trilha
  própria de auditoria (podada em 400) e integração com o changeLog da
  governança de backup. Backup antigo carrega sem perda; builds antigos
  preservam o agregado dormente.
- **Tela principal própria**: o Planejamento FX é a quinta área da navegação
  (`#fxplan`, mesma mecânica `.tab`/`data-screen` da rail, pílula, menu móvel e
  teclado das demais telas), por decisão do gestor pós-revisão — a
  Contabilidade voltou ao estado estrutural anterior, sem restos da feature. O
  contrato do smoke test passou de quatro para cinco telas operacionais.
- Interface em quatro modos internos (Visão Geral, Planejamento, Realizado, Tabela) com
  badges REAL/PREMISSA, gráfico baseline × projeção × realizado com transição
  histórico⇥projeção e alternância USD/BRL, barras de rentabilidade, painel de
  reservas com déficits, tabela mensal BASELINE × VIGENTE e resumo anual
  derivado das datas. Resumos textuais acompanham os SVGs.
- O manifest passou de 53 para 59 scripts (mesmo padrão de anexação do Galton);
  `fx_planning_test.py` entrou no tier `standard` (agora 8; `full` 18).
- A feature deriva conceitualmente da planilha `Planejamento FX.xlsx`, mas as
  inconsistências históricas do Excel (FUNDO FIIS ≠ FCR, reserva como % do
  patrimônio, coluna de aporte instável, taxa única de dólar, blocos anuais
  manuais) foram deliberadamente NÃO reproduzidas; fixtures são sintéticas.

### Galton Board — candidato local de 2026-08-11

- Adicionado `Configurações > Laboratório de Probabilidade > Galton Board`, com
  física rígida 2D real, placa triangular, Canvas HiDPI, controles acessíveis,
  histograma empírico, estatísticas e referência binomial condicional.
- Física separada do render por passo fixo de `1/120 s`; seed determinística atua
  somente no jitter de soltura e na tolerância fixa dos pinos. Corpos assentados são
  contabilizados uma vez, removidos e conservados apenas como agregados.
- Planck.js `1.5.0` foi vendorizado sob licença MIT, sem CDN ou dependência transitiva
  de runtime. Proveniência, integridade publicada e SHA-256 local ficam em
  `src/vendor/planck/README.md`; o validador fixa o hash do artefato.
- Criada a chave auxiliar `jpwealth_galton_preferences_v1` para preferências úteis.
  Ela não altera o schema financeiro, não persiste resultados e integra a limpeza de
  `Finalizar sessão` sem usar `localStorage.clear()`.
- O manifest passou de 46 para 53 scripts; o validador agora exige equivalência entre
  todos os scripts do manifest e o precache do service worker.
- Corrigidas duas falhas de baseline diretamente relacionadas à integração: o PWA
  não precacheava `12-nav-style.js` nem `17-economic-calendar.js`, e o modal de
  Configurações era recortado em `390 x 844` por uma regra tardia de padding.
- Adicionados `tools/galton_board_test.py` ao tier `standard` e o benchmark explícito
  de 10.000 bolas em `tools/galton_board_benchmark.py`. O core registrou 10.000
  assentamentos, zero expirações, um corpo estático final e pico de 240 corpos ativos;
  tempo e comparação binomial permanecem diagnósticos, sem gate ou fitting.
- Preferências ilegíveis, incompatíveis, de schema futuro ou com `localStorage`
  indisponível permanecem preservadas/bloqueadas em memória; a interface só volta a
  gravar após restauração explícita. O wipe entre abas invalida controladores montados
  para que a chave removida não seja recriada.
- A emissão com colisão bola-bola aguarda espaço físico no funil, evitando corpos
  sobrepostos. Configurações relacionam jitter/tolerância ao raio e ao clearance;
  vencimentos físicos remanescentes são comunicados e excluídos do histograma.
- A descoberta de nova versão PWA ocorre pelo bootstrap do próprio aplicativo, sem
  takeover: o worker espera todas as abas antigas fecharem e então o build novo abre
  online/offline. Manifest e precache incluem os 53 scripts.
- `build-id.js` e o HTML portátil foram atualizados pelo gerador oficial para o Build
  ID `dbca7e887edd287b`; o portátil tem SHA-256
  `038f9bf948aca9cec41bed34af4f130865f57c327b5f975216ea411f929bb416`.
- Suites focadas Galton, Settings, Finalizar sessão, upgrade PWA e reproducibilidade
  do build passaram no candidato consolidado. O gate `full` fechou `PASS 17/17`, sem
  falha de produto, harness, ambiente, baseline ou verificação omitida.
- Nenhuma regra N3, fórmula financeira, perfil, fase, limite, LIFO, DD ou
  contabilidade foi alterada. Commit, push, merge e publicação não foram executados.

### Em revisao
- Adicionados contexto em camadas, niveis de autoridade/risco, stop conditions, roteamento de skills e gates de evidencia para agentes.
- Criadas oito skills locais JP Wealth, templates de tarefa/auditoria/ADR e uma fotografia auditavel do estado atual.
- Adicionados preflight somente leitura, orquestrador de qualidade e fallback Chromium para validacao JavaScript quando Node nao estiver disponivel.
- Atualizadas expectativas comprovadamente obsoletas do harness para a navegacao, cabecalho, Central de Configuracoes e termo de Base de Dados atuais.
- Corrigidos `hidden`, alvos de toque, sobreposicao do inspetor e menu contextual das Notas; suite completa de Notas voltou a passar em desktop, mobile e portatil.
- Completado o precache do PWA e impedido que o HTML portatil tente registrar um service worker externo inexistente.
- Mensagem de falha de exportacao agora orienta contingencia manual para preservar os registros recentes.
- As correções N2 posteriores levaram o baseline `d9510dbb55f0` a `standard` 6/6 e o
  ciclo anterior a `full` 16/16; resultados antigos não provam o candidato Galton.
- Nenhuma fórmula financeira ou schema principal foi alterado nesse ciclo de
  governança; a feature atual adiciona somente a chave auxiliar isolada descrita
  acima.

## [9.1-db-storage-governance.1] — 2026-08-08

### Governança de armazenamento da base (JPW-HJFGDE)
- Adicionado o agregado `S.dataGovernance` (termo de responsabilidade, metadados da pasta padrão, sequência de exportação, backup confirmado e auditoria resumida), com migração sem perda para bases antigas e envelope do backup inalterado.
- Exportação da base reescrita como orquestração assíncrona: nomenclatura progressiva `JP_WEALTH_DB_NNNNNN_AAAA-MM-DD_HHmm.json`, sequência incrementada somente após sucesso confirmado, proteção física contra sobrescrita e diálogo explícito quando a pasta configurada está inacessível — nunca fallback silencioso para Downloads.
- Pasta padrão de exportação via File System Access API (Chrome/Edge desktop): handle persistido em IndexedDB, reautorização ao expirar, reassociação explícita após importação em outro dispositivo; navegadores sem suporte usam o download tradicional com a mesma nomenclatura e a interface declara a limitação.
- Nova etapa 07 "Base de Dados" no questionário de início: termo de responsabilidade obrigatório (sem ele a configuração não conclui) e configuração opcional da pasta.
- Central de Configurações ganhou o cartão "Armazenamento da Base": status da pasta, verificação de acesso, última exportação, próxima sequência, último backup confirmado e alterações desde então; aviso discreto após 30 dias sem backup confirmado.
- Estado sem base (limpeza total, Finalizar Sessão) passa a abrir sempre a tela inicial canônica `DEFAULT_START_ROUTE` e remove a autorização local da pasta junto com a base.
- Testes permanentes em `tools/storage_governance_test.py`; arquitetura documentada em `docs/architecture/DB-STORAGE-GOVERNANCE.md`.

## [9.1-settings-modal.1] — 2026-08-04

### Central de Configurações
- Transformada a antiga tela de Configurações em uma central modal dedicada, aberta pela engrenagem do cabeçalho sem trocar a tela operacional ao fundo.
- Reorganizados os controles existentes em Sobre, Aparência, Interface, Editor, Educacional, Estatuto Operacional, Parâmetros e Calibração e Backup e Recuperação, preservando os mesmos nós, listeners e persistência.
- Adicionada uma base educacional local, curta e pesquisável sobre Forex, glossário e perguntas frequentes; ela não contém sinais, previsões ou recomendações operacionais.
- Dados do Período agora são acessados por resumo seguro em Parâmetros e Calibração, com retorno ao onboarding existente em modo de edição.
- A central não grava em `S`, não altera o checkpoint de Finalizar Sessão e mantém a coordenação de foco ao abrir subdiálogos legados.
- Incluídos os módulos da central no precache existente do PWA, sem alterar sua estratégia de atualização.

## [9.1-header-actions.1] — 2026-08-04

### Navegação do cabeçalho
- Movidos os acessos de Configurações e Finalizar sessão para ações icônicas compactas no canto superior direito do cabeçalho.
- Mantida a numeração das áreas operacionais restantes e reutilizados os fluxos existentes de navegação e Finalizar Sessão.
- Nenhuma regra financeira, persistência, backup, limpeza ou comportamento interno de Finalizar Sessão foi alterado.

## [9.1-finalize-session.1] — 2026-08-03

### Privacidade e encerramento local
- Adicionado o fluxo modal `Finalizar sessão`, com checkpoint determinístico, exportação confirmada e confirmação textual `APAGAR TUDO`.
- Removidas somente as chaves locais do JP Wealth identificadas na auditoria, incluindo cópias corrompidas e preferências auxiliares; chaves de outras aplicações são preservadas.
- Criado estado em memória genuinamente vazio após a exclusão, sem nomes, contas, ordens, lançamentos ou credenciais anteriores.
- Mantido o formato do backup completo, a política existente de senhas de investidor e o comportamento do reset administrativo `Limpar todos os dados`.
- O fingerprint passou a incluir preço e data dos instrumentos; falsos positivos de atualização cambial são aceitos deliberadamente para priorizar a preservação de dados.
- Adicionado gate de persistência com geração de sessão, coordenação entre abas e proteção contra callbacks assíncronos após a exclusão.
- A limpeza de caches do service worker agora é limitada ao prefixo `jp-wealth-`.
- Nenhuma regra financeira, cálculo, perfil, matriz ou contabilidade foi alterada.

## [9.1-empty-state.1] — 2026-08-03

### Estado inicial e onboarding
- Removida a série demonstrativa de 2026 do acompanhamento mensal quando não existem fechamentos no ledger.
- Retorno acumulado e DD máximo permanecem vazios (`—`) até o primeiro fechamento diário; com ledger real, o cálculo existente é preservado.
- Substituídos os placeholders pessoais do onboarding por `Preencher nome` e reforçada a validação obrigatória dos nomes.
- Verificados inicialização sem estado salvo e os dois fluxos de limpeza sem alterar regras financeiras ou dados salvos existentes.

## [9.1-icons.1] — 2026-08-03

### PWA e identidade visual
- Criada biblioteca local com os temas `flat-knight`, `relief-knight` e `marble-knight`.
- Criado um manifesto PWA independente por tema, mantendo nome, modo e escopo do app.
- Adicionado service worker com precache versionado de scripts, manifestos e ícones.
- Adicionada seção `Ícone do app` em Configurações e modal acessível de escolha.
- Registrada a limitação real do Safari/iOS: trocar o ícone exige remover e adicionar novamente o atalho.
- Corrigido o binding antecipado de `wipeAllData` no boot e tornado o runner de smoke compatível com Chromium no macOS/Linux.
- Nenhuma regra financeira, persistência principal ou dado operacional foi alterado.

## [9.1-structured.1] — 2026-08-03

### Estrutura
- Preservado o HTML monolítico original e seu hash SHA-256.
- CSS extraído para `src/styles/app.css`.
- JavaScript separado pelas seções já existentes no código, sem reescrita de lógica.
- Criado `src/js/manifest.json` para fixar a ordem de execução.
- Criadas documentação de arquitetura, governança, recuperação e testes.
- Incluídos Estatuto e organograma em `docs/normative/`.
- Criados scripts de validação, smoke test e reconstrução do HTML portátil.

### Regras financeiras
- Nenhuma regra, constante ou fórmula financeira foi deliberadamente alterada nesta etapa.
