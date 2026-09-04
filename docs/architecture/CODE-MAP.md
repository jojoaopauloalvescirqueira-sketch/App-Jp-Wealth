# Mapa do código

Fotografia do candidato interno NAV-03 sobre `9b5ea298` em 2026-08-26:
`src/js/manifest.json` contém 77 scripts clássicos. O manifest é a fonte única
para ordem e hashes; esta página é um mapa humano e deve ser reconciliada quando
a lista material mudar.

## Ordem de execução

| Ordem | Arquivo | Responsabilidade |
|---:|---|---|
| 1 | `src/js/00-core/01-risk-profiles.js` | Perfis de risco V10.0, fonte única |
| 2 | `src/js/00-core/02-platforms.js` | Plataformas, fonte central para contas |
| 3 | `src/js/00-core/03-default-state.js` | Estado inicial |
| 4 | `src/js/00-core/04-persistence.js` | Persistência principal e migração |
| 5 | `src/js/00-core/05-helpers.js` | Helpers globais legados |
| 6 | `src/js/00-core/06-storage-fs.js` | File System Access e IndexedDB do handle |
| 7 | `src/js/10-domain/01-risk-instruments.js` | Risco por instrumento |
| 8 | `src/js/10-domain/02-risk-calculations.js` | Cálculos financeiros |
| 9 | `src/js/20-ui/01-header-readout.js` | Leitura de estado no cabeçalho |
| 10 | `src/js/20-ui/02-sidebar.js` | Colapso da barra lateral |
| 11 | `src/js/20-ui/03-main-render.js` | Render principal |
| 12 | `src/js/20-ui/04-operational-clearance.js` | Veredito executivo operacional |
| 13 | `src/js/20-ui/05-execution-clearance.js` | Veredito antes dos JP Wealth Gauge |
| 14 | `src/js/10-domain/03-phase-transitions.js` | Questionários de transição de fase |
| 15 | `src/js/10-domain/04-stop-statistics.js` | Stop estatístico, ATR e Raiz-N |
| 16 | `src/js/20-ui/06-chart-terminal-chrome.js` | Cromo padrão dos gráficos |
| 17 | `src/js/20-ui/07-chart-crosshair-tooltip.js` | Crosshair e tooltip dos gráficos |
| 18 | `src/js/20-ui/08-input-bindings.js` | Bindings de inputs |
| 19 | `src/js/30-accounting/01-daily-ledger.js` | Fechamento diário e log de auditoria |
| 20 | `src/js/10-domain/05-brokers-prop-firms.js` | Corretoras e prop firms, fonte central |
| 21 | `src/js/30-accounting/02-accounting-engine.js` | Motor da contabilidade |
| 22 | `src/js/30-accounting/03-mei-jp.js` | Modelo estatístico MEI-JP |
| 23 | `src/js/30-accounting/04-patrimonial-simulation.js` | Simulação patrimonial por perfil |
| 24 | `src/js/40-app/01-navigation.js` | Resolver semântico: cinco primários, seis filhos Forex, cinco filhos Research e compatibilidade física com owner/child/local view |
| 25 | `src/js/40-app/02-reset.js` | Reset administrativo |
| 26 | `src/js/40-app/03-theme.js` | Tema claro/escuro |
| 27 | `src/js/20-ui/09-contextual-help.js` | Ajuda de campo sob demanda |
| 28 | `src/js/20-ui/10-font-scale.js` | Escala tipográfica |
| 29 | `src/js/10-domain/06-quarantine.js` | Quarentena reversível |
| 30 | `src/js/20-ui/11-phase-posture.js` | Postura ofensiva/defensiva por fase |
| 31 | `src/js/20-ui/12-nav-style.js` | Preferência visual da navegação |
| 32 | `src/js/40-app/04-onboarding.js` | Questionário de início de período |
| 33 | `src/js/40-app/05-wipe-all.js` | Limpeza total com confirmação |
| 34 | `src/js/40-app/06-app-icons.js` | Preferência de ícone PWA |
| 35 | `src/js/40-app/07-finalize-session.js` | Finalização e privacidade local |
| 36 | `src/js/40-app/06-boot.js` | Boot do aplicativo |
| 37 | `src/js/40-app/08-educational-content.js` | Base educacional local |
| 38 | `src/js/40-app/09-settings-modal.js` | Central modal de Configurações |
| 39 | `src/js/40-app/10-dashboard-immersive.js` | Dashboard imersivo |
| 40 | `src/js/40-app/11-operational-shell.js` | Shell operacional: gaveta móvel e faixa compartilhada dos níveis contextuais, derivada do resolver |
| 41 | `src/js/40-app/12-global-dashboard.js` | Shell compartilhado do Dashboard |
| 42 | `src/js/40-app/13-dashboard-layout.js` | Personalização compartilhada de telas |
| 43 | `src/js/40-app/14-mvp-notes.js` | Tickets (apresentado como "Tickets"; arquivo e identificadores internos preservados) |
| 44 | `src/js/40-app/15-ff-news.js` | Notícias de alto impacto: **domínio** (cache, fetch, timers, `online`) + view do widget do Dashboard, inicializados em separado |
| 45 | `src/js/40-app/16-storage-governance.js` | UI da governança de armazenamento |
| 46 | `src/js/40-app/17-economic-calendar.js` | Calendário econômico semanal: render parametrizado por raiz (`data-ecal-role`), servindo o overlay `#ecalOverlay` e o workspace `#execEcal` — duas instâncias visuais, um domínio |
| 47 | `src/vendor/planck/planck-1.5.0.min.js` | Planck.js 1.5.0 vendorizado, MIT |
| 48 | `src/js/40-app/18-galton-board/01-config.js` | Configuração, presets e geometria do Galton Board |
| 49 | `src/js/40-app/18-galton-board/02-rng.js` | PRNG determinístico |
| 50 | `src/js/40-app/18-galton-board/03-statistics.js` | Estatística e referência binomial |
| 51 | `src/js/40-app/18-galton-board/04-physics.js` | Motor físico Planck |
| 52 | `src/js/40-app/18-galton-board/05-renderer.js` | Canvas responsivo HiDPI |
| 53 | `src/js/40-app/18-galton-board/06-controller.js` | DOM, lifecycle e preferências isoladas |
| 54 | `src/js/10-domain/07-reserve-requirements.js` | FCR/FEO — função pura compartilhada (Arts. 13.1/13.2) |
| 55 | `src/js/10-domain/08-usd-brl-quote.js` | Cotação USD/BRL, cache e fallback controlado |
| 56 | `src/js/30-accounting/05-fx-planning/01-fx-model.js` | Planejamento FX: modelo de domínio e validação |
| 57 | `src/js/30-accounting/05-fx-planning/02-fx-engine.js` | Planejamento FX: motor matemático puro |
| 58 | `src/js/30-accounting/05-fx-planning/03-fx-state.js` | Planejamento FX: estado e mutações auditadas |
| 59 | `src/js/30-accounting/05-fx-planning/04-fx-charts.js` | Planejamento FX: gráficos SVG sobre o cromo CH |
| 60 | `src/js/30-accounting/05-fx-planning/05-fx-ui.js` | Planejamento FX: interface em quatro modos |
| 61 | `src/js/20-ui/13-exec-views.js` | Execution Board: quatro workspaces canônicos (Visão Geral, Painel Operacional, Motor de Lote, Histórico) e shims analíticos para Research |
| 62 | `src/js/10-domain/09-nocoda-geometry.js` | NoCoda: geometria do canal — núcleo puro, sem DOM nem persistência |
| 63 | `src/js/20-ui/14-nocoda-studies.js` | NoCoda: workspace de estudos (seletor, âncoras, resultados derivados) |
| 64 | `src/js/10-domain/10-pivot-studies.js` | Pivots: derivação, validação, estatística descritiva e ordenação — núcleo puro |
| 65 | `src/js/20-ui/15-pivot-studies.js` | Pivots: workspace de estudos (estudos por período, CRUD de pivots, resumo, filtros) |
| 66 | `src/js/10-domain/11-operation-lifecycle.js` | Operação Única: ciclo de vida, snapshot histórico, finalização transacional e superfície de revisão |
| 67 | `src/js/20-ui/16-operation-history.js` | Histórico: workspace somente leitura das operações finalizadas |
| 68 | `src/js/10-domain/12-personal-finance.js` | Finanças Pessoais: núcleo do agregado `S.personalFinance` — schema v1 congelado, BRL_CENTS, write gate, materialização de mês, dívida temporal, comparativo e cenários |
| 69 | `src/js/20-ui/17-finpes-views.js` | Finanças Pessoais: troca dos cinco workspaces por hidden+inert e face do sentinela de unidade monetária |
| 70 | `src/js/20-ui/18-finpes-budget.js` | Orçamento Mensal: receitas, despesas, resumo do mês, destino do excedente e informações importantes |
| 71 | `src/js/20-ui/19-finpes-debts.js` | Dívidas & Crédito: identidade temporal da dívida, observações por competência e limites de crédito vigentes |
| 72 | `src/js/20-ui/20-finpes-comparison.js` | Comparativo Mensal: M−1 e M−12 com estados COMPLETE/PARTIAL/UNAVAILABLE e série de 12 meses com lacunas honestas |
| 73 | `src/js/20-ui/21-finpes-scenarios.js` | Cenários: hipóteses independentes agrupadas por horizonte, com cascata e cópia unidirecional de mês registrado |
| 74 | `src/js/20-ui/22-finpes-overview.js` | Visão Geral: consolidado derivado de quatro cards — mês atual, dívida & crédito, vs mês anterior e pendências |
| 75 | `src/js/10-domain/13-alladin.js` | **Alladin**: infraestrutura (moeda em unidade mínima, IDs, write gate transacional, fail-closed de schema v6), modelo cadastral (Instrument, Asset, Account, CashAccount), **ledger econômico** — `DEPOSIT`/`WITHDRAWAL`/`TRANSFER`/`REVERSAL`/`BUY`/`SELL`/`FEE`/`TAX`/`ADJUSTMENT_CREDIT`/`ADJUSTMENT_DEBIT`, saldo de caixa derivado e fail-closed, consistência do par reversal↔original na leitura, completude do `ALD_CASH_DELTA` (ausência de delta é BLOCKING, nunca zero implícito) — e **Position Quantity Engine** (ALD-04 S1): `leitura.posicoes()` derivada por instrumentId+accountId, aritmética decimal exata em BigInt; sem holding persistido/consolidado, cost basis, valuation, P&L/performance |
| 76 | `src/js/20-ui/23-research-views.js` | Research: ownership e troca efêmera de Calendário, NoCoda, Pivots e quatro empty states |
| 77 | `src/js/20-ui/24-alladin-views.js` | **Alladin C3 + ALD-05 S1**: superfície cadastral — leitura desacoplada pelo read-model, CRUD das quatro entidades no modal próprio, `recordStatus`, write gate, DC-4 e integridade da edição — **e a superfície econômica**: Lançamentos (leitura, **criação** — modal único dos nove tipos, uma chamada a `ledger.addTransaction` por submit, dinheiro só por `money.parse`, `quantity` verbatim, CTA ausente sob BLOCKING — **e estorno**: coluna Ações com elegibilidade visual por linha e uma chamada a `ledger.reverseTransaction`, com o original em read-only e a economia copiada pelo domínio), Saldos e Posições projetando `transactions()`/`saldoDeCaixa()`/`posicoes()` sem aritmética própria (dinheiro por `money.format`, `quantity` verbatim), com BLOCKING que nunca vira zero, vazio ou tela normal, e sentinela de integridade para o ledger (`posicoes()` + `compat()`, já que `transactions()` não tem envelope) |

## Laboratório de Probabilidade

O caminho de interface é `Configurações > Laboratório de Probabilidade > Galton
Board`. Os seis módulos publicam apenas `window.JPWGalton` e permanecem separados do
estado financeiro `S`. A física usa passo fixo de `1/120 s`; uma placa com `N` linhas
tem `N + 1` compartimentos. O detalhe do contrato está em `GALTON-BOARD.md`.

## Planejamento FX

Tela física própria `#fxplan`, filha canônica `forex-planning` no NAV-02 e
preservada também pela compatibilidade `JPWNavigation.resolve('fxplan')`. A
rota canônica entra em `overview`; o alias preserva a visão corrente. O card
`#fxPlanningCard` continua fora da personalização de layout nesta fase. Os seis módulos publicam
`window.JPWFx` + `reserveRequirementsCalc`; o módulo de cotação publica
`window.JPWMarket.usdBrl`, e o agregado do plano persiste em `S.fxPlanning`.
A extração de `reserveCalc()` do onboarding para a função pura
compartilhada foi autorizada em 2026-08-11; contrato completo em
`FX-PLANNING.md`.

Forex, Finanças Pessoais e Research usam a faixa hierárquica compartilhada:
cada acionador permanece filho direto de `#nav`, enquanto a faixa única
`#navSubShell` vive no fluxo entre header e contexto. Forex tem seis filhos e
terceiro nível contextual para Operação, Apuração e Planejamento; os quatro
modos do último reutilizam `window.JPWFx.ui` sem tabs internas duplicadas.

No Execution Board restam `#execOverview`, `#execWidgetGrid`,
`#motorWidgetGrid` e `#execHistory`. Research contém os mesmos nós
`#execEcal`, `#execNocoda` e `#execPivots`, sem clone ou rename, além dos empty
states de Ações, Stocks, REITs e Others; todos são alternados por `hidden` +
`inert`. NoCoda e Pivots são repintados a cada entrada e após `boot()` quando
visíveis, porque dependem do estado vivo.

O Motor de Lote migrou de `Configurações → Operação` para o módulo em
2026-08-13: é o mesmo `#motorWidgetGrid`, sem nó recriado e sem id alterado. A
`section#motor` hospedeira e o transporte de DOM da Central foram removidos
juntos — `restoreLegacySettingsNodes()` reanexava o grid a ela a cada
fechamento e o arrancaria de dentro de `#exec`. Os dois cards perderam
`data-layout-card`, que era vestigial e faria a regra de edição de layout
escopada por tela congelar seus controles. As restrições estruturais dessa realocação — nunca `.screen`
aninhada, nunca dentro da `.jp-widget-grid`, nunca desmontar — e o contrato
reutilizável completo estão em `NAVIGATION-HIERARCHY.md`.

## Entrypoints, PWA e artefatos derivados

- `index.html` compõe o DOM e carrega os 77 scripts na ordem do manifest.
- `src/styles/app.css` contém o design system e as regras do laboratório.
- `sw.js` deve precachear todo caminho declarado no manifest; `validate_project.py`
  trata a equivalência como invariante. Navegações controladas pelo worker
  anterior recebem o `index.html` do cache anterior; o worker novo permanece em
  `waiting` até o fechamento dos clientes, conforme `PWA-UPDATE-LIFECYCLE.md`.
- `tools/rebuild_monolith.py` é o único gerador de `build-id.js` e
  `dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html`; os derivados nunca são editados
  manualmente.
- `tools/galton_board_test.py` cobre a feature em navegador real e
  `tools/galton_board_benchmark.py` executa o cenário longo de 10.000 bolas.
