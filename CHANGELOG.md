# Changelog

## [Unreleased]

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
