# Session Handoff — NAV-03 · Research Consolidation

- Data: 2026-08-26
- Branch: `codex/navigation-ia`
- `BASE_SHA`: `9b5ea298953b3c8bb270864151a88e5c69419e61`
- Estado: candidato NAV-03 implementado e tecnicamente validado; aguarda gate humano
- Publicabilidade: primeiro candidato estruturalmente potencial, ainda sem autorização humana
- Git: commit/push/merge/deploy não autorizados nem executados

## Target, candidato e publicação

- **TARGET CANÔNICO:** cinco primários — Dashboard, Forex, Finanças Pessoais,
  Research e Alladin.
- **CHECKPOINT NAV-02:** Forex possui exatamente seis filhos e terceiro nível
  contextual em Operação, Apuração e Planejamento, sobre as telas existentes.
- **CANDIDATO NAV-03:** Research possui cinco filhos; Forex contém Calendário,
  NoCoda e Pivots, enquanto Ações, Stocks, REITs e Others abrem diretamente.

## Implementação presente

- `window.JPWNavigation` separa cinco primários, seis filhos Forex, cinco filhos
  Research e aliases.
- `current()` registra `primary`, `child`, `screen` e `localView`; não persiste.
- `navigateToScreen()` continua aceitando IDs físicos legados.
- `execNavTrigger` e `execNavSubmenu` foram preservados; nenhuma `section#forex`.
- `motor` marca Operação, `history` marca Apuração e `fxplan` marca Planejamento;
  `check` abre Preparação e `tool-check`, Settings.
- `window.JPWResearch.ui` seleciona sete workspaces efêmeros. Os IDs físicos
  `execEcal`, `execNocoda` e `execPivots` existem uma vez, sob `#research`.
- Aliases analíticos ativam Research/Forex/N3; Exec mantém quatro views canônicas.
- `section#alladin` usa exatamente a mensagem
  aprovada e não acopla ao domínio Alladin.
- `tools/research_navigation_test.py` está registrado no tier standard/full;
  o manifest e o precache contêm 76 scripts.
- Galton segue em Configurações sem alteração funcional ou de lifecycle.

## Evidência e próxima ação controlada

Focais Research, Navigation IA, Exec/Calendário, NoCoda, Pivots e
Settings/Galton PASS. `validate_project` PASS com 76 scripts e 415 IDs; fast
4/4, standard 32/32 e full 43/43 PASS. Browser real desktop/mobile e ciclo PWA
PASS, incluindo upgrade do service worker e build reproduzível
`aaa2262ae6fb0610`. Alladin permanece em `1eddd29e`, com os mesmos 12 arquivos
modificados e três não rastreados. Emitir `NAV-03 — CANDIDATE REPORT` e parar;
commit, push, merge e deploy não estão autorizados.
