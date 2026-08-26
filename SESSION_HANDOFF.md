# Session Handoff — NAV-02 · Forex Consolidation

- Data: 2026-08-26
- Branch: `codex/navigation-ia`
- `BASE_SHA`: `e2c34bb4c4ac0c0f7a2746ca4687c6a61f64f06d`
- Estado: NAV-02 implementado, reconciliado e validado; aguarda decisão humana
- Publicabilidade: **não** — NAV-03 é o primeiro candidato potencialmente publicável
- Git: commit/push/merge/deploy não autorizados nem executados

## Target, candidato e publicação

- **TARGET CANÔNICO:** cinco primários — Dashboard, Forex, Finanças Pessoais,
  Research e Alladin.
- **CANDIDATO NAV-02:** Forex possui exatamente seis filhos e terceiro nível
  contextual em Operação, Apuração e Planejamento, sobre as telas existentes.
- **ESTADO PUBLICÁVEL:** NAV-03 migra Calendário, NoCoda e Pivots para Research.

## Implementação presente

- `window.JPWNavigation` separa cinco primários, seis filhos Forex e aliases.
- `current()` registra `primary`, `child`, `screen` e `localView`; não persiste.
- `navigateToScreen()` continua aceitando IDs físicos legados.
- `execNavTrigger` e `execNavSubmenu` foram preservados; nenhuma `section#forex`.
- `motor` marca Operação, `history` marca Apuração e `fxplan` marca Planejamento;
  `check` abre Preparação e `tool-check`, Settings.
- Calendário, NoCoda e Pivots permanecem funcionais com `child:null` até NAV-03.
- `section#research` é estática; `section#alladin` usa exatamente a mensagem
  aprovada e não acopla ao domínio Alladin.
- o quality gate inclui `tools/navigation_ia_test.py` no tier standard/full.

## Evidência e próxima ação controlada

Build `3d51c530db465831`; seis focais, `validate_project`, fast 4/4, full 42/42
e browser pós-full PASS. O browser cobriu desktop/mobile 390×844, claro/escuro,
teclado, níveis 2/3, overflow e targets ≥44 px. Emitir `NAV-02 — CANDIDATE
REPORT` e parar. Commit, push, merge, deploy e início do NAV-03 não estão autorizados.
