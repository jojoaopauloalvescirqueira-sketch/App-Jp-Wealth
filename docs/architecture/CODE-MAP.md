# Notas — APPLE NOTES EXPERIENCE MATCH, 2026-09-14

Base integrada conferida: `9ca32073e1fa032318b7e6e6eb50b5f693efe2d9`. Revisão local na branch `codex/apple-notes-match-20260914`, sem integração. `index.html` e `src/styles/app.css` reorganizam os controles existentes em três zonas de toolbar/painéis. `14-mvp-notes.js` preserva CRUD/dirty/ordem/exportação/larguras e projeta aparência por atributos; preferência auxiliar `jpwealth_notes_appearance_v1` com confirmed/draft, read-back, recusa/retry e bloqueio UNKNOWN/conflito. `09-settings-modal.js` conecta prévia/cancelamento ao cartão Notas existente; `07-finalize-session.js` inclui somente a chave nova na limpeza auxiliar. Conteúdo, schemas, matemática e políticas dos tickets permanecem. Fonte e validação focal: [CHG/CTX](../work/CHG-APPLE-NOTES-MATCH-20260914.md), `tools/apple_notes_match_test.py`. As seções seguintes são registros anteriores; suas afirmações de integração/contexto não substituem a base Git agora conferida.

---

# Revisão cumulativa — unificação 2026-09-14

O candidate de unificação preserva Notas/Backup posteriores e incorpora `src/js/40-app/18-notification-center.js` como 79º script, após os 78 herdados, conforme o contrato de [Notifications](NOTIFICATION-CENTER.md). O sino usa `dgBackupStatus()` da mesma fonte de Dashboard/Settings, sem persistir inbox ou recalcular domínio. Registros abaixo mantêm contagens e decisões históricas de suas revisões. Build/identidade do pacote novo em manifesto externo; integração ainda não demonstrada.

# Notas — reconciliação local em implementação

A janela de Notas centralizada reutiliza `14-mvp-notes.js`, com launcher de posição auxiliar normalizada, mesma instância e larguras canônicas preservadas. Layout desktop/tablet/celular 3/2/1. Contrato vigente desta composição: [CHG-NIGHT-PENDING-RECONCILIATION](../work/CHG-NIGHT-PENDING-RECONCILIATION-20260914.md). Não representa integração. A Central de Notificações posterior não foi incorporada à origem309.

# Completion pass — representação de apresentação local

Base Git `fafb228316cbcad8091ebc4632443a51687ace43` mais delta local; fingerprint externo.

| Fonte | Papel alterado | Contrato preservado |
|---|---|---|
| `index.html` / `src/styles/app.css` | Composição, cabeçalhos, símbolos, ordem visual/DOM, reflow e estados | IDs, consumidores e preferências; risco mantém semântica |
| `20-ui/25-dash-macro.js` | Capítulos, primário/registro e atalhos | Mesmos read-models, chamadas e ausência/erro |
| `20-ui/18` a `22` | Resumo, registros, rótulos e ações PF | Binds, parsers, pfMutate, cálculos e ordem de leitura |
| `20-ui/14-nocoda-studies.js` | Bancada, detalhes e ncUpdatePreview | geometry.compute/validate/levelPrice canônicos; binds/save/rascunho |
| `20-ui/15-pivot-studies.js` | Biblioteca e barras H1/H4 | stats().timeframes, median/n; atos e filtros originais |
| `20-ui/24-alladin-views.js` | alladinHeading/contexto, tabela com rótulos móveis | Leitura, qualidade, ações e mutações originais |
| `40-app/09-settings-modal.js` | generalPanel e símbolos por intenção | Busca, grupos, histórico, slots e proteções |
| `40-app/14-mvp-notes.js` | Texto vazio; área de escrita por CSS | Rascunho, recusa/retry, salvamento e ciclo intactos |
| `40-app/17-economic-calendar.js` | Classes de lista temporal | Fonte, cache, filtros e atualização |
| `40-app/18-galton-board/06-controller.js:panelHTML` | Comandos, palco e análise | Código fora de panelHTML idêntico à V2; física/lifecycle A13 |
| `tools/apple_experience_test.py` | Focal de layout, contraste, navegação e gráficos | Fixtures existentes, falhas reais; não altera quality_gate |

Manifest mantém 78 scripts na ordem original, apenas hashes atualizados.
Build/portátil são gerados por `tools/rebuild_monolith.py`.
[Decisões e oportunidades](APPLE-EXPERIENCE-DIRECTION.md).

## Histórico V2 preservado

# Recorte local — APPLE01, 2026-09-12

Base `fafb228316cbcad8091ebc4632443a51687ace43` mais delta de apresentação.
`index.html` contém símbolos originais, labels e agrupamento dos destinos Alladin;
`src/styles/app.css` compõe superfícies e controles responsivos;
`src/js/20-ui/25-dash-macro.js:dmLink` conserva destino/handler e remove somente
seta diagonal decorativa. Manifest mantém ordem e atualiza hash dessa fonte;
build/portátil são gerados oficialmente. `tools/apple_experience_test.py` verifica
rótulos, geometria, contraste focal, navegação e foco com fixtures sintéticas.
Funções financeiras, lifecycle do Lab e persistência não recebem alterações.
[Direção e decisões](APPLE-EXPERIENCE-DIRECTION.md).

## Histórico preservado

# Recorte corrente — estabilização técnica local 20260911

Base Git fcbb25767073a4ab08a9f0ac2ac16069a3008bfe mais V2 e delta não commitado;
identidade final e resultados em CURRENT-STATE/manifesto externo. Mesmos78 scripts
na ordem original. Nenhuma fórmula, norma ou schema alterado.

| Fonte | Responsabilidade atual adicional | Evidência focal |
|---|---|---|
| `14-mvp-notes.js` / `index.html` | Avisos globais integram o diálogo aberto; mesmos nós restaurados; Tab/ShiftTab alcançam recuperação sem fechar rascunho; diálogos internos isolam foco | `studies_notes_persistence_contract_test.py` |
| `13-alladin.js` / `24-alladin-views.js` / `25-dash-macro.js` | `leitura.ledger()` expõe disponibilidade/qualidade/issues/fatos sem derivar posições; API bruta mantida; preview direto inválido recusado explicitamente | `alladin_ledger_read_model_test.py` |
| `18-galton-board/06-controller.js` | Construção que falha aborta listeners, desconecta observer e descarta engine/renderer antes de propagar exceção; mount só publica instância completa | `galton_board_test.py` |
| `15-ff-news.js` / `17-economic-calendar.js` / `25-dash-macro.js` | Falha de gravação/leitura do cache técnico é explícita; nenhum cache paralelo ou escrita financeira | `ff_news_cache_test.py` |
| `index.html` | Um landmark main; conteúdo de Configurações é seção rotulada no diálogo | `settings_modal_test.py` |

Caminhos abreviados acima seguem a tabela completa/manifest abaixo. As provas de
execução são externas e identificadas; descrição do código não as substitui.

---

## Histórico e mapa de localização preservados

## Recorte de responsabilidades — candidate local da campanha 20260910

Base `e770e1b66a87e93f52f40eab83479d7a26be2cd4`; build `e5caefeada66ab35`.
A lista/ordem dos 78 scripts não muda; o manifest muda somente quatro hashes.
Esta tabela acrescenta as responsabilidades internas examinadas; não atualiza
as revisões nem certifica as demais descrições históricas abaixo.

| Fonte | Separação local | Contrato preservado |
|---|---|---|
| `src/js/20-ui/18-finpes-budget.js` | `fbBindItemField` concentra protocolo dos dois bindings fi/fe | IDs/campos/atos resolvidos no evento; recusa do ato: restauração antes de `fbAtoUI`; parsing inválido: alerta antes da restauração; demais binds separados |
| `src/js/20-ui/24-alladin-views.js` | `alladinCashLabels` projeta rótulos; wrapper conserva leituras | Accounts/processamento → instruments/processamento → cashAccounts; sem filtro/status/cálculo novo |
| `src/js/40-app/09-settings-modal.js` | `settingsSelectSearchResults` seleciona entradas já contextualizadas | Filtro → dedupe título/caminho → prioridade estável → limite18; DOM/click no render |
| `src/js/30-accounting/05-fx-planning/05-fx-ui.js` | `fxpActivateOverview` concentra ativação visual | Wire/bind/refresh/controles/charts na ordem original; demais ifs independentes |

[Contrato, consumidores e plano de provas](../work/REFACTOR-CAMPAIGN-20260910.md).
Helpers internos a scripts clássicos; nenhuma nova API de domínio ou roteamento.
Equivalência focal registrada; validação final/auditoria/aceite são gates distintos.
O histórico seguinte permanece como fotografia anterior, sem reindexação.

---

# Mapa do código

Reconciliação em 2026-09-09 sobre `484228189cc3f5f4c297f29f88f2b2ed541a3afd`,
build `88c0cb1ce5520311`: `src/js/manifest.json` contém 78 scripts clássicos.
O manifest é a fonte única para ordem e hashes; a coluna abaixo representa a
posição na lista de carga, inclusive onde a entrada não possui campo `order`.
Este mapa humano deve ser reconciliado quando a lista ou seus contratos mudarem.
A revisão documental não é evidência de teste nem homologação financeira.

Para finalidade dos cinco módulos, capacidade atual e limites, leia
`../governance/PROJECT-CONTEXT.md`. Para instruções funcionais, fontes seletivas,
consumidores, riscos e testes pertinentes, use `../governance/CONTEXT-MAP.md`.
Esses mapas não substituem os contratos de domínio nem a política de `AGENTS.md`.

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
| 24 | `src/js/40-app/01-navigation.js` | Resolver semântico: cinco primários, seis filhos Forex, seis filhos Research e compatibilidade física com owner/child/local view |
| 25 | `src/js/40-app/02-reset.js` | Reset administrativo |
| 26 | `src/js/40-app/03-theme.js` | Tema claro/escuro |
| 27 | `src/js/20-ui/09-contextual-help.js` | Ajuda de campo sob demanda |
| 28 | `src/js/20-ui/10-font-scale.js` | Escala tipográfica |
| 29 | `src/js/10-domain/06-quarantine.js` | Quarentena reversível |
| 30 | `src/js/20-ui/11-phase-posture.js` | Postura ofensiva/defensiva por fase |
| 31 | `src/js/20-ui/12-nav-style.js` | Preferências visuais da navegação, incluindo ordem dos cinco primários no Editor |
| 32 | `src/js/40-app/04-onboarding.js` | Questionário de início de período |
| 33 | `src/js/40-app/05-wipe-all.js` | Limpeza total com confirmação |
| 34 | `src/js/40-app/06-app-icons.js` | Preferência de ícone PWA |
| 35 | `src/js/40-app/07-finalize-session.js` | Finalização e privacidade local |
| 36 | `src/js/40-app/06-boot.js` | Boot do aplicativo |
| 37 | `src/js/40-app/08-educational-content.js` | Base educacional local |
| 38 | `src/js/40-app/09-settings-modal.js` | Central modal de Configurações |
| 39 | `src/js/40-app/10-dashboard-immersive.js` | Dashboard imersivo |
| 40 | `src/js/40-app/11-operational-shell.js` | Shell derivado do resolver: lateral contextual padrão, composição superior opcional no Editor, mesmos nós N1/N2/N3, diálogos mobile e foco |
| 41 | `src/js/40-app/12-global-dashboard.js` | Shell compartilhado: contexto global, Status do Sistema e realocação dos componentes operacionais para Forex > Visão Geral |
| 42 | `src/js/40-app/13-dashboard-layout.js` | Personalização compartilhada de telas |
| 43 | `src/js/40-app/14-mvp-notes.js` | Notas: acesso flutuante móvel e pelas Configurações; posição em memória, tickets/dados e identificadores internos preservados |
| 44 | `src/js/40-app/15-ff-news.js` | Notícias de alto impacto: **domínio** (cache, fetch, timers, `online`) + view do widget em Forex > Visão Geral, inicializados em separado; calendário e resumo Dashboard compartilham o pipeline |
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
| 67 | `src/js/20-ui/16-operation-history.js` | Histórico e cópia textual por whitelist de operações atuais/finalizadas; sem gravação financeira |
| 68 | `src/js/10-domain/12-personal-finance.js` | Finanças Pessoais: núcleo do agregado `S.personalFinance` — schema v1 congelado, BRL_CENTS, write gate, materialização de mês, dívida temporal, comparativo e cenários |
| 69 | `src/js/20-ui/17-finpes-views.js` | Finanças Pessoais: troca dos cinco workspaces por hidden+inert e face do sentinela de unidade monetária |
| 70 | `src/js/20-ui/18-finpes-budget.js` | Orçamento Mensal: receitas, despesas, resumo do mês, destino do excedente e informações importantes |
| 71 | `src/js/20-ui/19-finpes-debts.js` | Dívidas & Crédito: identidade temporal da dívida, observações por competência e limites de crédito vigentes |
| 72 | `src/js/20-ui/20-finpes-comparison.js` | Comparativo Mensal: M−1 e M−12 com estados COMPLETE/PARTIAL/UNAVAILABLE e série de 12 meses com lacunas honestas |
| 73 | `src/js/20-ui/21-finpes-scenarios.js` | Cenários: hipóteses independentes agrupadas por horizonte, com cascata e cópia unidirecional de mês registrado |
| 74 | `src/js/20-ui/22-finpes-overview.js` | Visão Geral: consolidado derivado de quatro cards — mês atual, dívida & crédito, vs mês anterior e pendências |
| 75 | `src/js/10-domain/13-alladin.js` | **Alladin**: infraestrutura (moeda em unidade mínima, IDs, write gate transacional, fail-closed de schema v6), modelo cadastral (Instrument, Asset, Account, CashAccount), **ledger econômico** — `DEPOSIT`/`WITHDRAWAL`/`TRANSFER`/`REVERSAL`/`BUY`/`SELL`/`FEE`/`TAX`/`ADJUSTMENT_CREDIT`/`ADJUSTMENT_DEBIT`, saldo de caixa derivado e fail-closed, consistência do par reversal↔original na leitura, completude do `ALD_CASH_DELTA` (ausência de delta é BLOCKING, nunca zero implícito) — e **Position Quantity Engine** (ALD-04 S1): `leitura.posicoes()` derivada por instrumentId+accountId, aritmética decimal exata em BigInt; sem holding persistido/consolidado, cost basis, valuation, P&L/performance |
| 76 | `src/js/20-ui/23-research-views.js` | Research: Calendário, NoCoda, Pivots, Laboratório/Galton e quatro empty states |
| 77 | `src/js/20-ui/24-alladin-views.js` | **Alladin C3 + ALD-05 S1**: superfície cadastral — leitura desacoplada pelo read-model, CRUD das quatro entidades no modal próprio, `recordStatus`, write gate, DC-4 e integridade da edição — **e a superfície econômica**: Lançamentos (leitura, **criação** — modal único dos nove tipos, uma chamada a `ledger.addTransaction` por submit, dinheiro só por `money.parse`, `quantity` verbatim, CTA ausente sob BLOCKING — **e estorno**: coluna Ações com elegibilidade visual por linha e uma chamada a `ledger.reverseTransaction`, com o original em read-only e a economia copiada pelo domínio), Saldos e Posições projetando `ledger()`/`saldoDeCaixa()`/`posicoes()` sem aritmética própria (dinheiro por `money.format`, `quantity` verbatim), com BLOCKING que nunca vira zero, vazio ou tela normal, e qualidade explícita de `leitura.ledger()`; `transactions()` continua compatibilidade bruta, sem garantia de integridade |
| 78 | `src/js/20-ui/25-dash-macro.js` | Dashboard: síntese de Forex, Finanças Pessoais, Research e Alladin consumindo contratos canônicos, com estados de disponibilidade/cobertura, atualização agrupada e atalhos pelo resolver; sem escrita financeira ou materialização de mês |

## Laboratório de Probabilidade

O caminho de interface é `Research > Laboratório de Probabilidade > Galton
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

## Navegação compartilhada e contexto local

A lateral contextual é o padrão; o Editor oferece a composição superior
opcional (`jpw_nav_layout=sidebar|topbar`). O mesmo `#nav` vive em `#appSidebar`
ou `#gdTopbarNavSlot`. Os cinco acionadores primários continuam filhos diretos
de `#nav`; não há router, IDs ou listeners duplicados para a alternativa.

Forex, Finanças Pessoais e Research compartilham um único `#navSubShell`. Na
lateral, ele fica dentro de `#nav`, após o expansor ativo. Na composição
superior, volta ao fluxo antes de `#gdContextRow`. Os contextos N3 de Forex e
Research ficam em `#navLocalSlot` no modo lateral e retornam aos painéis de
navegação correspondentes no superior. Alladin mantém suas abas no conteúdo.
Forex tem seis filhos; Operação, Apuração e Planejamento conservam contextos
locais. Os quatro modos de Planejamento reutilizam `window.JPWFx.ui`.

`JPWNavigation.current()` e as superfícies de módulo determinam a localização
exibida. `jpw_nav` (estilo), `jpw_rail` (compactação) e a escolha de composição
são preferências distintas. Trocar composição não deve navegar, reinicializar
módulos ou alterar preferências v6 dos widgets; contratos completos em
`NAVIGATION-HIERARCHY.md`.

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
escopada por tela congelar seus controles. As restrições estruturais dessa
realocação — nunca `.screen` aninhada, nunca dentro da `.jp-widget-grid`,
preservar os nós operacionais — e o contrato completo estão em
`NAVIGATION-HIERARCHY.md`. Isso não impõe o mesmo lifecycle a todos os módulos:
Alladin limpa o DOM de vistas inativas e revalida os controles ao renderizar.

## Dashboard, Forex e agenda compartilhada

`dashMacroRender()` compõe os quatro resumos superiores fora de `#gdDashMain`.
Forex lê `compute()`/`getOperationalClearance()`, apuração e planejamento;
Finanças Pessoais fornece suas métricas canônicas; Research fornece estudos e
calendário; Alladin fornece compatibilidade/read-models. Ausência, parcialidade
e bloqueio são resultados a apresentar, não números a completar.

`relocateGlobalDashboardShell()` mantém os mesmos nós de onboarding,
`#mcClearanceCard`, VRM e notícias em `#fxOverviewWidgets`. O Dashboard conserva
Status do Sistema e Ações rápidas em “Sistema e atalhos”. O motor de layout
continua usando um envelope v6 e projeta os cartões entre as duas telas, sem
descartar preferências dos realocados. `renderSystemStatus()` consome estado de
persistência, backup, `staleInfo()` e conclusão do onboarding; não os recalcula.

Jornada representativa, reconstruída por leitura do código nesta revisão:

1. **Dashboard → Abrir Forex:** `initDashMacro()` delega o clique a
   `JPWNavigation.navigate('forex-overview')`.
2. **Resolver → Visão Geral:** `01-navigation.js` resolve tela `exec`, superfície
   `exec`, visão `overview`; `execSelectView()` usa os nós existentes.
3. **Widget Forex → agenda:** `initFfNewsWidget()` liga `#gdNewsMoreBtn` a
   `JPWEcal.openMenu()`; o item Calendário Econômico abre `openEconomicCalendar()`.
4. **Fonte compartilhada:** `ecalEvents()` lê `ffNewsReadCache()`;
   `ecalRenderRoot()` atende o diálogo e `#execEcal`, agora em Research.
   Abrir pode pedir revalidação por `ffNewsFetch(false)`, sem escrita financeira
   em `S`; cache técnico/rede seguem o pipeline próprio.
5. **Atualização e retorno:** `ffNewsRenderAll()` atualiza widget, agenda visível
   e resumo Dashboard. Fechar o diálogo devolve foco ao acionador; o filtro do
   workspace Research é efêmero e separado do filtro do diálogo.

O owner da rota Research, a localização do widget Forex e a fonte do cache são
responsabilidades diferentes. Alterar uma delas requer examinar os consumidores
indicados, não criar uma segunda implementação. Essa leitura não prova
interação executada: selecione os testes focais no `../governance/CONTEXT-MAP.md` e registre
seu resultado somente quando executados no candidate declarado. A orientação
de estado vazio em `17-economic-calendar.js` já aponta Forex e atualização pela agenda;
a dívida textual citada no recorte antigo foi corrigida antes desta campanha.

## Entrypoints, PWA e artefatos derivados

- `index.html` compõe o DOM e carrega os 78 scripts na ordem do manifest.
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


## Projeções A10–A13

- `12-nav-style.js`: `jpw_nav_order` validada por identidade estável, prévia e
  confirmação explícita no Editor; mesmas tabs na lateral/superior/mobile.
- `11-operational-shell.js`: `syncForexContext()` apresenta a única faixa
  `gdContextRow` apenas quando o owner ativo é Forex, usando métricas existentes.
- `16-operation-history.js`: `operationCopyProjection()` lê ordens da operação
  vigente ou snapshot histórico, usando whitelist; `operationCopyToClipboard()`
  reutiliza o mecanismo de clipboard de Notas. O botão do Consolidado é ligado
  por `renderOperationCopyAction()`; o histórico possui ação por registro.
- `23-research-views.js` e resolver: entrada própria do Laboratório, saída
  coordenada com pausa e conservação em memória da mesma instância Galton.
  `18-galton-board/06-controller.js` impede retomada automática após navegação
  ou sobreposição; `Continuar` retoma pelo mecanismo existente. Reset/finalização
  conservam sua limpeza. Configurações não é mais o destino do Laboratório.

A12 é entrega parcial. A cópia distingue entrada, andamento, posição zerada aguardando finalização e
registro formalmente finalizado. Não cria timestamps, dados finais ausentes,
resultado flutuante ou vínculo de conta com ordem. Conta mestre e saldo book
são contexto cadastral **atual**, não snapshot de entrada. Histórico usa somente
seu snapshot; não recebe perfil/conta/equity atual como dado final.
DD/fase, alavancagem, Lucro Técnico e clearance normativos permanecem
NEEDS_HUMAN_RULE diante das divergências legadas e de OPEN-05; não são
reinterpretados nem homologados por essa exportação. Copiar não chama save,
finalização, render de grades com cura, nem qualquer ação financeira.

## Projeções DESIGN & EXPERIENCE 01

Este recorte descreve o candidate local da campanha de apresentação, sem
declarar aceite humano, integração ou publicação. Fontes e responsabilidades:

| Fonte | Apresentação e fronteira preservada |
|---|---|
| `src/js/20-ui/20-finpes-comparison.js` | Curva de 12 meses, métrica/mês efêmeros e tabela completa compartilham uma leitura de `pfCompSeries`; lacunas, zeros e unidade monetária seguem o contrato PF. |
| `src/js/20-ui/25-dash-macro.js` | Acesso de cada card junto ao título, com os mesmos destinos e read-models. |
| `index.html` | `fxOverviewWidgets` precede as ferramentas de preparação em Forex > Visão Geral; IDs e ações existentes são mantidos. |
| `src/js/40-app/09-settings-modal.js` e `src/styles/app.css` | Busca responsiva; abrir resultado conserva a consulta, retira a lista de resultados e foca o conteúdo. A revelação respeita reduced-motion. |
| `src/js/20-ui/24-alladin-views.js` | Busca efêmera oculta linhas somente após o envelope integral e as relações de estorno; preserva ordem, datas, valores e distinção entre busca sem resultados, vazio e indisponibilidade. |
| `src/js/20-ui/07-chart-crosshair-tooltip.js` | `bindChartCrosshair()` acrescenta seletor nativo, setas/Home/End e toque com leitura textual; cada série usa a data do seu ponto mais próximo, sem alterar os dados fornecidos. |
| `src/js/40-app/18-galton-board/06-controller.js` | Comandos principais antes do Canvas e ajustes depois; mesmos IDs, ações, física 2D e ciclo de pausa em memória A13. |

Os focais da campanha estão em `tools/design_pf_comparison_test.py` e
`tools/design_experience_test.py`; a presença dos arquivos não declara resultado
de execução. Escopo e gates permanecem em
`docs/work/CHG-DESIGN-EXPERIENCE-01-20260912.md`. Não há nova métrica financeira,
schema, autoridade de escrita ou alteração da cópia parcial A12.

## Backup e avisos — reconciliação local

- `00-core/04-persistence.js`: `dgCommitGovernance` delimita confirmação/export metadata; `dgPersistenceStatus` e `dgBackupStatus` são projeções comuns, sem novo motor financeiro.
- `30-accounting/01-daily-ledger.js`: cobertura do clone, fases de entrega/registro local, validação proporcional de importação e preservação em recusa.
- `40-app/16-storage-governance.js` e `12-global-dashboard.js`: base ativa versus destino, freshness e estados de gravação.
- `40-app/15-ff-news.js`: `ffNewsStatusText` é compartilhado pelo widget, modal/workspace em `17-economic-calendar.js` e resumo em `20-ui/25-dash-macro.js`. Nenhuma nova consulta econômica; erro não vira “zero eventos”.
- `tools/backup_reliability_test.py`: dados sintéticos, contraprovas sobre a origem309 e round-trip real em contexto descartável. FULL do produto continua obrigatório e separado.

## FOREX-V11-CENTRAL-01 — incremento local em revisão

Registry puro em `src/js/00-core/00-forex-policy.js`; engine puro em `src/js/10-domain/00-forex-engine.js`; comandos explícitos em `src/js/10-domain/00-forex-state.js`; read-model e compatibilidade em `02-risk-calculations.js`; UI em `20-ui/26-forex-engine-views.js`. O escritor, epoch, locks e recuperação permanecem os existentes. O snapshot completo S inclui os agregados Forex/ledgerHistory e extensões de planejamento, enquanto a sessão do editor é somente RAM. Fatos, elegibilidade e dados históricos têm contratos distintos em [FOREX-V11-ENGINE](FOREX-V11-ENGINE.md). Esta descrição não concede aceite ou homologação.
