# CHG-FOREX-OPERATION-ACCOUNT-CONTEXT-20260915

```yaml
schema: jp-harness/chg/v1
change_id: CHG-FOREX-OPERATION-ACCOUNT-CONTEXT-20260915
status: approved
objective: Vincular Operacao, Contabilidade, Contas e Fator de Correcao a um contexto persistido por conta e periodo; preservar dados confirmados em Finalizar Sessao.
risk_level: N2
authority_required: A3
target:
  root: /Users/joaopauloalves/.codex/forex-operation-context/20260915/product
  branch: codex/forex-operation-account-context-20260915
  baseline_sha: 8b2ef27120f6f42e273241541d76957a6910e7df
scope:
  allowed_files:
    - docs/work/CHG-FOREX-OPERATION-ACCOUNT-CONTEXT-20260915.md
    - docs/work/CHG-FOREX-OPERATION-ACCOUNTS-NAVIGATION-20260915.md
    - docs/work/ACTIVE-TASK.md
    - docs/architecture/STATE-SCHEMA.md
    - docs/architecture/NAVIGATION-HIERARCHY.md
    - docs/architecture/CODE-MAP.md
    - docs/architecture/FOREX-EXECUTION-BOARD.md
    - docs/architecture/DB-STORAGE-GOVERNANCE.md
    - docs/recovery/DATA-RECOVERY.md
    - index.html
    - src/styles/app.css
    - src/js/manifest.json
    - src/js/00-core/03-default-state.js
    - src/js/00-core/04-persistence.js
    - src/js/10-domain/00-forex-state.js
    - src/js/10-domain/01-risk-instruments.js
    - src/js/10-domain/02-risk-calculations.js
    - src/js/10-domain/03-phase-transitions.js
    - src/js/10-domain/04-stop-statistics.js
    - src/js/10-domain/11-operation-lifecycle.js
    - src/js/10-domain/18-execution-board-model.js
    - src/js/20-ui/03-main-render.js
    - src/js/20-ui/01-header-readout.js
    - src/js/20-ui/07-chart-crosshair-tooltip.js
    - src/js/20-ui/13-exec-views.js
    - src/js/20-ui/16-operation-history.js
    - src/js/20-ui/25-dash-macro.js
    - src/js/20-ui/26-forex-engine-views.js
    - src/js/20-ui/30-execution-board.js
    - src/js/30-accounting/01-daily-ledger.js
    - src/js/30-accounting/02-accounting-engine.js
    - src/js/30-accounting/04-patrimonial-simulation.js
    - src/js/30-accounting/05-fx-planning/03-fx-state.js
    - src/js/40-app/01-navigation.js
    - src/js/40-app/04-onboarding.js
    - src/js/40-app/06-boot.js
    - src/js/40-app/07-finalize-session.js
    - src/js/40-app/12-global-dashboard.js
    - src/js/40-app/13-dashboard-layout.js
    - src/js/40-app/18-notification-center.js
    - src/js/40-app/24-fx-consolidated-import.js
    - tools/forex_account_context_test.py
    - tools/forex_account_context_browser_test.py
    - tools/forex_account_context_browser_test.js
    - tools/exec_submenu_test.py
    - tools/navigation_ia_test.py
    - tools/navigation_local_contract_test.py
    - tools/forex_navigation_journey_test.py
    - tools/fx_consolidated_ui_test.py
    - tools/forex_execution_board_test.py
    - tools/order_guards_test.py
    - tools/operation_identity_test.py
    - tools/operation_finalize_test.py
    - tools/operation_history_test.py
    - tools/operation_wiring_test.py
    - tools/phases_visibility_test.py
    - tools/forex_v11_ledger_planning_test.py
    - tools/forex_v11_state_test.py
    - tools/finalize_session_test.py
    - tools/smoke_test.py
    - tools/research_navigation_test.py
    - tools/fx_planning_test.py
    - tools/dashboard_macro_test.py
    - tools/mvp_notes_test.py
    - tools/finpes_finalize_preservation_test.py
    - tools/alladin_finalize_preservation_test.py
    - tools/session_write_serialization_test.py
    - tools/persistence_failure_test.py
    - build-id.js
    - dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html
  allowed_actions: [implementacao delimitada, testes sinteticos, derivados oficiais, auditoria, freeze, recovery externo]
  forbidden_actions: [commit, push, pull, PR, merge, deploy, reset, stash, exclusao de branch, alteracao normativa, alteracao de policy ou formulas, edicao de AGENTS/skills/CI/gates]
derived_artifacts:
  allowed: [build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html]
  generation_commands: [python3 tools/rebuild_monolith.py]
  manual_edit: forbidden
data:
  test_policy: synthetic_only
  schema_change: approved
acceptance_criteria:
  - Quatro visoes locais de Operacao e quatro filhos Forex na ordem aprovada.
  - Identidade, periodos, SI, book e equity sem mistura entre contas.
  - Operacoes e fechamentos simultaneos por conta, com revisao e falha integra.
  - Legado ambiguo consultavel, sem associacao automatica.
  - Finalizar Sessao preserva todos os fatos confirmados; backup/restauracao validam o novo agregado.
approved_tests: [focais, regressao Forex/navegacao/Settings/backup, FULL vigente, PWA/portatil, browser sintetico, auditoria independente]
test_oracle_change: Os oraculos globais antigos de operation_identity, operation_finalize e operation_wiring foram preservados fora dos inputs do candidate em evidence/legacy-test-oracles antes da adaptacao. Eles chamavam S.phases/S.activeOperation e um finalizador global substituidos pelo contexto persistido por conta. Os testes vigentes exercitam writers, revisao, modal, DOM, disco, duas contas, rollback, UNKNOWN e idempotencia no caminho contextual; order_guards usa ponte sintetica somente de teste para preservar negativas historicas. Finalizar Sessao exige preservar fatos Forex confirmados e excluir desbloqueios, sem enfraquecer recovery ou Zona de Perigo. forex_navigation_journey foi ajustado para a nova hierarquia e para a identidade operacional factual mesmo quando os calculos estao indisponiveis. O oraculo grid-market-separate-from-account-phase de forex_v11_state conserva a gravacao LEGACY global, mas passa a exigir que grade/ATR sem identidade inequivoca de operacao/conta/periodo permaneçam indisponiveis na projecao contextual; a prova positiva de grade e ATR explicitamente vinculados foi adicionada ao teste de duas contas.
rollback:
  source: [candidate-operation-accounts-navigation.json, candidate-operation-accounts-navigation.diff]
  application_state: [fixture sintetica anterior]
  data: [snapshot legado imutavel e backup completo validado]
  environment: [somente delta desta worktree]
  verification: [hashes de 16 caminhos herdados, teste round-trip, diff/fingerprint do novo candidate]
approved_by: Proprietario, PLEASE IMPLEMENT THIS PLAN Forex — Operacao integrada por conta, seguido da autorizacao especifica da branch/worktree.
approved_at: 2026-09-15
```

```yaml
schema: jp-harness/ctx/v1
context_change_id: CTX-FOREX-OPERATION-ACCOUNT-CONTEXT-20260915
status: approved
mode: CONCORRENTE
create: [docs/work/CHG-FOREX-OPERATION-ACCOUNT-CONTEXT-20260915.md]
modify: [docs/work/ACTIVE-TASK.md, docs/architecture/STATE-SCHEMA.md, docs/architecture/NAVIGATION-HIERARCHY.md, docs/architecture/CODE-MAP.md, docs/architecture/FOREX-EXECUTION-BOARD.md, docs/architecture/DB-STORAGE-GOVERNANCE.md, docs/recovery/DATA-RECOVERY.md]
preserve: [candidate anterior, main, stash, demais worktrees, evidencias, recovery, parametros V11, A12 parcial, OPEN-05/V11/FCR/FEO, AUD-05/P2]
```

## Compreensao e evidencias

O JP Wealth guarda fatos locais auditaveis ao lado da elegibilidade V11. Forex cadastra identidade em `S.accounts`, observa SI/equity em `S.forex.accounts`, e hoje conserva uma operacao global em `S.activeOperation`/`S.phases` e ledger global em `S.ledger`. Esta tarefa cria contexto proprio para cada conta, sem transferir fatos ao trocar selecao. Dashboard, alertas, planejamento, backup e Finalizar Sessao sao consumidores; saldo book nunca substitui equity e PENDING nao vira zero. Fontes: `AGENTS.md`, `README.md`, `docs/governance/CONTEXT-MAP.md`, `docs/architecture/STATE-SCHEMA.md`, `docs/architecture/FOREX-EXECUTION-BOARD.md`, `docs/architecture/DB-STORAGE-GOVERNANCE.md`, `docs/normative/README.md`, `docs/normative/ANEXO_PARAMETRICO_CANONICO.md` e codigo no HEAD. Harness SHA-256 `c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8`.

Base Git `8b2ef27` e base experimental de 16 caminhos sao distintas. Build herdado `a1c01dc414a3b62b`; fingerprint de manifesto `0367b790496affbd6dadb1d07f6670e0f1252b741734e97002060f8590d639bd`; hashes/modos foram conferidos na nova worktree. O candidate anterior permanece congelado. Preflight de edicao passou com `--allow-dirty` somente para esses deltas conhecidos. Sem nova formula ou parametro: caminhos que alimentam o motor recebem revisao N3 focal, testes e auditoria. Recovery fora dos inputs; integracao/deploy separados.
