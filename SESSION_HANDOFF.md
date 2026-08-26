# Session Handoff — NAV-06A · Documentation Reconciliation

- Data: 2026-08-26
- Branch: `codex/navigation-ia`
- `BASE_SHA`/`HEAD`: `2c1e0a441d77e01c8c9acaf0506da333254c8196`
- Estado: NAV-01, NAV-02 e NAV-03 concluídos e commitados na branch Navigation;
  candidato NAV-06A reconcilia apenas a documentação operacional
- Release readiness: runtime aprovado; documentação reconciliada no candidato;
  merge continua sujeito a autorização humana separada
- Git/publicação: commit NAV-06A, push, merge e deploy não autorizados nem executados

## Target, candidato e publicação

- **TARGET CANÔNICO:** cinco primários — Dashboard, Forex, Finanças Pessoais,
  Research e Alladin.
- **CHECKPOINT NAV-01:** commit `e2c34bb4c4ac0c0f7a2746ca4687c6a61f64f06d`.
- **CHECKPOINT NAV-02:** commit `9b5ea298953b3c8bb270864151a88e5c69419e61`;
  Forex possui exatamente seis filhos e terceiro nível
  contextual em Operação, Apuração e Planejamento, sobre as telas existentes.
- **CHECKPOINT NAV-03:** commit `2c1e0a441d77e01c8c9acaf0506da333254c8196`;
  Research possui cinco filhos; Forex contém Calendário, NoCoda e Pivots,
  enquanto Ações, Stocks, REITs e Others abrem diretamente.

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
  aprovada e não acopla ao domínio Alladin; o desenvolvimento funcional segue
  pausado no worktree isolado.
- `tools/research_navigation_test.py` está registrado no tier standard/full;
  o manifest e o precache contêm 76 scripts.
- Galton segue em Configurações sem alteração funcional ou de lifecycle.

## Evidência e próxima ação controlada

Full final **43/43 PASS** no commit `2c1e0a4`, com browser desktop/mobile e ciclo
PWA PASS, incluindo upgrade do service worker e build reproduzível
`aaa2262ae6fb0610`. `main` local e `origin/main` permanecem em
`1eddd29ee73d3e8fbc1713e073a0c22ce71350ab`; Navigation está três commits à
frente e zero atrás. Alladin permanece em `1eddd29e`, com os mesmos 12 arquivos
modificados e três não rastreados. Próximo gate humano: decidir o commit doc-only
NAV-06A; push, merge e deploy continuam não autorizados.
