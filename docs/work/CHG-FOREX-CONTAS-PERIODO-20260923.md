# CHG-FOREX-CONTAS-PERIODO-20260923

```yaml
schema: jp-harness/chg/v1
change_id: CHG-FOREX-CONTAS-PERIODO-20260923
status: approved
objective: Centralizar cadastro e gestão de contas CFDs e períodos, com wizard e contexto explícito na Board.
risk_level: N2
authority_required: A3
target:
  root: /Users/joaopauloalves/.codex/forex-contas-periodo/20260923/product
  branch: codex/forex-contas-periodo-20260923
  baseline_sha: 7f2d6b63384b9c459ca3d1a9743269ad6940ec3f
scope:
  allowed_files:
    - index.html
    - src/styles/app.css
    - src/js/00-core/01-risk-profiles.js
    - src/js/00-core/04-persistence.js
    - src/js/00-core/07-workspace-backup.js
    - src/js/10-domain/00-forex-state.js
    - src/js/10-domain/02-risk-calculations.js
    - src/js/10-domain/04-stop-statistics.js
    - src/js/20-ui/01-header-readout.js
    - src/js/20-ui/08-input-bindings.js
    - src/js/20-ui/26-forex-engine-views.js
    - src/js/20-ui/28-fx-consolidated.js
    - src/js/20-ui/30-execution-board.js
    - src/js/20-ui/31-forex-accounts.js
    - src/js/40-app/01-navigation.js
    - src/js/40-app/04-onboarding.js
    - src/js/40-app/11-operational-shell.js
    - src/js/20-ui/13-exec-views.js
    - src/js/40-app/24-fx-consolidated-import.js
    - src/js/manifest.json
    - sw.js
    - tools/*account*test*
    - tools/forex_account_profile_test.py
    - tools/*navigation*test*
    - tools/fx_import_operation_test.py
    - tools/fx_planning_test.py
    - tools/fx_consolidated_ui_test.py
    - tools/forex_execution*test.py
    - tools/exec_submenu_test.py
    - tools/contextual_sidebar_test.py
    - tools/complete_backup_test.py
    - tools/forex_accounts_workspace_test.py
    - docs/work/CHG-FOREX-CONTAS-PERIODO-20260923.md
    - docs/work/ACTIVE-TASK.md
    - docs/architecture/FOREX-EXECUTION-BOARD.md
    - docs/architecture/FOREX-CONSOLIDATED.md
    - docs/architecture/STATE-SCHEMA.md
    - docs/architecture/COMPLETE-BACKUP.md
  forbidden_files: [AGENTS.md, docs/normative, .github, tools/quality_gate.py, tools/test_infra, skills]
  allowed_actions: [isolated_worktree, bounded_edit, synthetic_tests, local_review_server, independent_audit]
  forbidden_actions: [commit, push, PR, merge, deploy, real_data_access]
  regressions_forbidden: [identity_reassignment, implicit_context_switch, retroactive_profile, risk_formula_change, silent_fallback, lost_draft, lost_history]
derived_artifacts:
  allowed: [build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html]
  generation_commands: [python3 tools/rebuild_monolith.py]
  manual_edit: forbidden
external_side_effects:
  network: allowed
  allowed_targets: [git_remote_read_only, loopback_synthetic_review]
  temporary_artifacts: allowed
  cleanup_required: true
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: approved
toolchain:
  dependency_changes: []
  allowed_processes: [python3, node, existing_playwright_browser, loopback_http_server]
acceptance_criteria:
  - Single management destination in all four layouts; aliases preserved.
  - Registration and profile saved once with durable acknowledgement.
  - Examining B does not change operational A; context pair accepted atomically after draft guard.
  - Five-step wizard; no credentials; cancel and failure preserve unconfirmed draft.
  - Profile changes apply only to explicitly created next period; snapshots are not backfilled.
  - Current risk engine remains live; pending P30 remains blocked.
  - Board retains context and management link, no registration/period management.
  - Import, backup, history, previous-version read/write preserve optional additions.
approved_tests:
  - fx_account_registration_test.py; fx_account_setup_test.py; new accounts workspace focal
  - navigation four layouts, aliases/order, draft protection; Settings/Notes/header focus regression
  - Forex identity/history/state/persistence and complete_backup_test.py
  - validate_project.py; rebuild_monolith.py; build_reproducibility_test.py; PWA/offline
  - quality_gate.py --tier full with documented opt-in apparatus and separate trace result
rollback:
  source: [baseline tree and exact candidate diff preserved externally]
  application_state: [restore only scoped code; no reset/stash]
  data: [preserve optional fields, previous-version read and write tested with synthetic fixture, no real migration]
  environment: [stop only owned temporary test processes]
  verification: [hashes, clean main, isolated candidate, compatible backup roundtrip]
approved_by: user explicit attached request 0329e509-a992-4131-b4f7-a0696fb6fc37
approved_at: 2026-09-23
expires_on: [material_drift, new_normative_rule, scope_expansion]
```

## Brief / compreensão e invariantes
JP Wealth registra e avalia contexto financeiro; esta mudança organiza responsabilidades, não homologa execução. A main já compartilha S.accounts entre interfaces, porém há editores diretos e preparação duplicada. O novo destino e wizard reutilizam os comandos de registro/setup; observações, ledger e importação continuam entidades distintas. Perfil cadastral será documental e versionado; regra vigente não será congelada pelo snapshot. A decisão humana determina vigência apenas em período posterior explicitamente confirmado. Alterações globais do onboarding, cálculos e normas são proibidas.

Fontes lidas: AGENTS, README, CONTEXT-MAP, FOREX-V11-ENGINE, FOREX-EXECUTION-BOARD, FOREX-CONSOLIDATED, STATE-SCHEMA, COMPLETE-BACKUP, DB-STORAGE-GOVERNANCE, DATA-RECOVERY, SECURITY-MODEL e skills roteadas, confrontadas com main atual. Anexo P30 permanece PENDING, fatores históricos revogados. Preflight audit/edit PASS. Aviso de contexto histórico confrontado com código: nenhum pressuposto de que o candidate onboarding foi integrado; seus comandos centrais já são idênticos à main, UI pendente será preservada.

## Dependências e testes antes da alteração
Base limpa e remoto confirmados em 7f2d6b6. Testar cancelamento, gravação recusada/UNKNOWN, duplicata, clique repetido, identidade e par de contexto, respostas tardias, perfil sem fallback, período posterior e legado sem snapshot, preservação do motor com entradas equivalentes e risco vivo após nova observação. Testes de expectativa visual afetada serão adaptados à decisão aprovada, sem enfraquecer invariantes. Auditoria independente N2 no candidate congelado; nenhuma aprovação humana inferida.

Harness fonte atual: `/Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/2 - TRABALHO/99B - SOFTWARE DEV/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md`; SHA256 `c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8`.

## Reconciliação dos consumidores de navegação
O full do candidate r4 confirmou duas expectativas antigas da ordem Forex em navigation_ia_test.py e fx_planning_test.py. A busca delimitada encontrou a mesma lista em forex_navigation_journey_test.py e fx_consolidated_ui_test.py. Estes consumidores serão alinhados somente à ordem diretamente aprovada, mantendo os oráculos financeiros e de proteção. O mapa explicita os dois arquivos de testes adicionais antes da escrita; não amplia funcionalidades de Planejamento/Consolidado nem modifica o gate. Recibo full bruto permanece preservado, seguido de revalidação dos quatro consumidores e hashes do conjunto final.
