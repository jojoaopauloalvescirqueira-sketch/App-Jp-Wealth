# Tarefa ativa — NAV-03 · Research Consolidation

- Data de abertura: 2026-08-26
- `BASE_SHA`: `9b5ea298953b3c8bb270864151a88e5c69419e61`
- Branch: `codex/navigation-ia`
- Worktree: `JP Wealth OS Navigation IA`
- Classificação: **N1**
- Autoridade: **A2**, implementação delimitada aprovada
- Estado: candidato NAV-03 implementado e tecnicamente validado; aguarda gate humano
- Git/publicação: **commit, push, merge e deploy não autorizados**

## Objetivo e contrato congelado

Consolidar Research como owner visual das ferramentas analíticas existentes,
sem duplicar telas nem alterar sua lógica funcional. `routes()` mantém exatamente
os cinco primários e `children('research')` passa a expor exatamente, nesta ordem:

1. `research-forex` — Forex;
2. `research-stocks-br` — Ações;
3. `research-stocks-global` — Stocks;
4. `research-reits` — REITs;
5. `research-others` — Others.

`research-forex` abre Calendário por default e possui exatamente três destinos
contextuais: Calendário, NoCoda e Pivots. Ações abre diretamente o empty state
Brasil/B3, sem N3 artificial; Stocks, REITs e Others abrem empty states neutros.

Os aliases `ecal`, `nocoda` e `pivots` passam a ativar Research, o filho Forex e
o destino contextual correspondente. Os IDs físicos `execEcal`, `execNocoda` e
`execPivots` são preservados e movidos sem clone para `section#research`.
`JPWExec.ui` fica com exatamente `overview`, `panel`, `motor` e `history`; shims
legados podem redirecionar para Research, sem ownership ou estado Exec paralelo.

## Exclusões e invariantes

- nenhuma quarta view “Visão Geral” em Research/Forex;
- nenhum N3 para Ações, Stocks, REITs ou Others;
- empty states sem métricas, cotações, patrimônio, performance ou números fictícios;
- Galton permanece em Configurações, com lifecycle, DOM, animação, preferências,
  storage, código funcional e testes internos intactos;
- Calendário, NoCoda e Pivots mantêm fonte, cálculo, persistência, renderização de
  domínio e uma única instância DOM;
- alvo inválido falha antes de qualquer efeito observável;
- navegação não cria chave, não escreve em storage/S e não chama `save()`;
- nenhuma regra financeira, schema, migração, backup ou restore muda;
- navegação Alladin não lê/chama/muta `S.alladin` ou `JPWAlladin`;
- o worktree Alladin original permanece sem drift.

## Blast radius autorizado — máximo de 30 arquivos

- Runtime/UI (9): `index.html`, `src/styles/app.css`,
  `src/js/40-app/01-navigation.js`, `src/js/40-app/11-operational-shell.js`,
  `src/js/20-ui/13-exec-views.js`, `src/js/20-ui/23-research-views.js`,
  `src/js/40-app/15-ff-news.js`, `src/js/40-app/17-economic-calendar.js`, `sw.js`.
- Manifest/gerados (3): `src/js/manifest.json`, `build-id.js`,
  `dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html`.
- Testes (6): `tools/research_navigation_test.py`, `tools/navigation_ia_test.py`,
  `tools/exec_submenu_test.py`, `tools/nocoda_test.py`,
  `tools/pivot_studies_test.py`, `tools/quality_gate.py`.
- Governança/documentação (12): `CHANGELOG.md`, `README.md`,
  `SESSION_HANDOFF.md`, `docs/architecture/ARCHITECTURE.md`,
  `docs/architecture/CODE-MAP.md`, `docs/architecture/NAVIGATION-HIERARCHY.md`,
  `docs/architecture/NOCODA-STUDIES.md`,
  `docs/architecture/PIVOT-STUDIES.md`, `docs/architecture/GALTON-BOARD.md`,
  `docs/governance/CURRENT-STATE.md`, `docs/governance/QUALITY-GATES.md` e este arquivo.

Trinta é limite, não meta. Qualquer 31º arquivo exige parada e nova autorização.

## Verificação concluída no candidato final

- focais Research, Navigation IA, Exec/Calendário, NoCoda, Pivots e
  Settings/Galton: **PASS**;
- `validate_project.py`: **PASS**, 76 scripts e 415 IDs estáticos;
- tiers: fast **4/4 PASS**, standard **32/32 PASS** e full **43/43 PASS**;
- browser real 1440×900 e 390×844: **PASS** em claro/escuro, teclado, foco,
  N2/N3, hidden/inert, overflow, alvos móveis ≥44 px e zero erros ou requisições
  falhas introduzidas;
- PWA: **PASS** em manifesto, hashes, precache, upgrade do service worker e
  build reproduzível; build oficial `aaa2262ae6fb0610`;
- worktree Alladin reconfirmado em `1eddd29e`, com os mesmos 12 modificados e
  três não rastreados. Auditoria final de diff/fingerprint fecha o report.

## Rollback

Antes de commit, rollback é a reversão manual e delimitada dos arquivos do
NAV-03 para `BASE_SHA`, preservando qualquer trabalho externo. Remover somente
os dois arquivos novos do NAV-03 se necessário. Não usar `reset`, `clean`,
`stash` ou reescrita de histórico. Commit e publicação seguem gates humanos
separados.
