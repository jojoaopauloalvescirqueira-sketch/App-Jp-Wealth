# Tarefa ativa — NAV-02 · Forex Consolidation

- Data de abertura: 2026-08-26
- `BASE_SHA`: `e2c34bb4c4ac0c0f7a2746ca4687c6a61f64f06d`
- Branch: `codex/navigation-ia`
- Worktree: `JP Wealth OS Navigation IA`
- Classificação: **N1**
- Autoridade: **A2**, implementação delimitada aprovada
- Estado: candidato NAV-02 implementado e validado; aguarda decisão humana
- Git/publicação: **commit, push, merge e deploy não autorizados**

## Objetivo e contrato congelado

Consolidar sob o primário Forex exatamente seis filhos sem criar
`section#forex`, duplicar telas ou renomear os IDs físicos `execNavTrigger` e
`execNavSubmenu`:

1. `forex-overview` → `#exec` / `overview`;
2. `forex-preparation` → `#check`;
3. `forex-account` → `#contas`;
4. `forex-operation` → `#exec` / `panel`;
5. `forex-reconciliation` → `#contab`;
6. `forex-planning` → `#fxplan` / `overview`.

`JPWNavigation.routes()` continua expondo exatamente os cinco primários e
`JPWNavigation.children('forex')` expõe exatamente os seis filhos acima, nessa
ordem. O terceiro nível é contextual e reutiliza as superfícies existentes:
Operação (`panel`, `motor`), Apuração (Contabilidade, `history`) e Planejamento
(`overview`, `planning`, `actuals`, `table`).

Compatibilidade aprovada: `motor` pertence a Operação e abre `exec/motor`;
`history` pertence a Apuração e abre `exec/history`; `fxplan` pertence a
Planejamento e preserva a visão corrente. O target legado `check` passa a
Preparação; `tool-check` permanece ação explícita da Central de Configurações.
`ecal`, `nocoda` e `pivots` continuam tecnicamente funcionais, sem filho Forex
falsamente ativo e sem atalhos provisórios até o NAV-03.

## Exclusões e invariantes

- não iniciar NAV-03 nem criar destinos de Research;
- não criar `section#forex`, telas, workspaces ou estado de navegação paralelos;
- não renomear `execNavTrigger`, `execNavSubmenu` ou IDs físicos funcionais;
- alvo inválido falha fechado antes de qualquer efeito observável;
- navegação não cria chave, não escreve em storage/S e não chama `save()`;
- nenhuma regra financeira, schema, migração, fórmula ou persistência muda;
- navegação Alladin não lê/chama/muta `S.alladin` ou `JPWAlladin`;
- o worktree Alladin original permanece sem drift;
- NAV-02 não é publicável; NAV-03 é o primeiro candidato potencialmente publicável.

## Blast radius autorizado — exatamente 23 arquivos

- Runtime/UI (4): `index.html`, `src/styles/app.css`,
  `src/js/40-app/01-navigation.js`, `src/js/40-app/11-operational-shell.js`.
- Testes (6): `tools/navigation_ia_test.py`, `tools/exec_submenu_test.py`,
  `tools/fx_planning_test.py`, `tools/settings_modal_test.py`,
  `tools/nocoda_test.py`, `tools/pivot_studies_test.py`.
- Manifest/gerados (3): `src/js/manifest.json`, `build-id.js`,
  `dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html`.
- Governança/documentação (10): `CHANGELOG.md`, `README.md`,
  `SESSION_HANDOFF.md`, `docs/architecture/ARCHITECTURE.md`,
  `docs/architecture/CODE-MAP.md`, `docs/architecture/FX-PLANNING.md`,
  `docs/architecture/NAVIGATION-HIERARCHY.md`,
  `docs/governance/CURRENT-STATE.md`, `docs/governance/QUALITY-GATES.md` e
  este `docs/work/ACTIVE-TASK.md`.

Qualquer 24º arquivo exige parada e nova autorização.

## Verificação concluída

- NAV2-A a NAV2-J: PASS;
- focais Navigation IA, Exec submenu, FX Planning, Settings, NoCoda e Pivots: PASS;
- build oficial `3d51c530db465831`; `validate_project.py`: PASS, 75 scripts e 409 IDs;
- tier `fast`: 4/4 PASS; tier `full`: 42/42 PASS;
- browser pós-full: desktop/mobile 390×844, claro/escuro, teclado, níveis 2/3,
  zero overflow e targets móveis ≥44 px: PASS;
- zero novas chaves e zero escrita causada por navegação: PASS.

## Rollback

Antes de commit, rollback é a reversão manual e delimitada dos arquivos do
NAV-02 para `BASE_SHA`, preservando qualquer trabalho externo. Não usar
`reset`, `clean`, `stash` ou reescrita de histórico. Commit e publicação seguem
gates humanos separados.
