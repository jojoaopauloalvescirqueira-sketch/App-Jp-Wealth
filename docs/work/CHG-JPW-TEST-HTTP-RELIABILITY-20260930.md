# Correção da infraestrutura de testes — trilha separada do produto

```yaml
schema: jp-harness/chg/v1
status: approved
target:
  root: /private/tmp/jpw-cockpit-ui-20260930
  branch: codex/jpw-cockpit-ui-20260930
  baseline_sha: deffc5061fe2eff3d83b6f6e742fa105ac9c5b06
approved_by: Proprietario - Corrija todos os product fail que foram apresentados ou tem-se registrado
approved_at: 2026-09-30T15:00:00-03:00
external_side_effects:
  network: allowed
  allowed_targets: [loopback_synthetic_browser_fixtures]
  temporary_artifacts: allowed
  cleanup_required: true
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: forbidden
toolchain:
  dependency_changes: []
  allowed_processes: [python3, chromium, node]
derived_artifacts:
  allowed: [portable_html, build_id, local_validation_receipts]
  generation_commands: [python3 tools/rebuild_monolith.py]
  manual_edit: forbidden
rollback:
  source: [restore only repair delta from outputs/jpw-product-fail-repair-20260930/baseline.tar.gz]
  application_state: [existing product state unchanged]
  data: [no real data changes]
  environment: [stop only synthetic test servers]
  verification: [compare baseline hashes and preserved patch]
expires_on: [target_or_branch_change, material_baseline_drift, financial_rule_change]
change_id: CHG-JPW-TEST-HTTP-RELIABILITY-20260930
objective: Remove local HTTP bootstrap resource loss without weakening product assertions, timeouts or gate classification.
risk_level: N3
authority_required: A4
scope:
  allowed_files:
    - tools/browser_fixture_server.py
    - tools/browser_fixture_server_test.py
    - tools/alladin_finalize_preservation_test.py
    - tools/alladin_ui_crud_test.py
    - tools/alladin_ui_readonly_test.py
    - tools/alladin_ui_tx_reverse_test.py
    - tools/alladin_ui_tx_write_test.py
    - tools/async_generation_test.py
    - tools/exec_submenu_test.py
    - tools/exec_three_column_test.py
    - tools/finalize_session_test.py
    - tools/finpes_backup_roundtrip_test.py
    - tools/finpes_debt_credit_test.py
    - tools/finpes_finalize_preservation_test.py
    - tools/finpes_foundation_test.py
    - tools/finpes_navigation_test.py
    - tools/finpes_overview_test.py
    - tools/fx_planning_test.py
    - tools/galton_board_test.py
    - tools/import_xss_security_test.py
    - tools/investor_password_test.py
    - tools/navigation_ia_test.py
    - tools/nocoda_test.py
    - tools/operation_finalize_test.py
    - tools/operation_history_test.py
    - tools/operation_wiring_test.py
    - tools/order_guards_test.py
    - tools/persistence_failure_test.py
    - tools/persistence_recovery_test.py
    - tools/phases_visibility_test.py
    - tools/pivot_studies_test.py
    - tools/research_navigation_test.py
    - tools/service_worker_upgrade_test.py
    - tools/session_write_serialization_test.py
    - tools/smoke_test.py
    - tools/state_integrity_test.py
    - tools/storage_governance_test.py
    - tools/usd_brl_quote_test.py
    - docs/work/CHG-JPW-TEST-HTTP-RELIABILITY-20260930.md
    - docs/work/BRIEF-JPW-PRODUCT-FAIL-REPAIR-20260930.md
    - docs/work/ACTIVE-TASK.md
  forbidden_files: [AGENTS.md, skills/**, docs/normative/**, tools/quality_gate.py, .github/**]
  allowed_actions: [repair_local_http_fixture_capacity, add_negative_control_regression, run_unchanged_gates, independent_audit]
  forbidden_actions: [weaken_assertions, extend_timeouts, add_test_retries, reclassify_old_receipts, commit, push, merge, deploy]
  regressions_forbidden: [hide_missing_assets, substitute_app_source, suppress_page_errors, change_network_stubs, remove_gate_cases]
acceptance_criteria:
  - Identical candidate assets survive concurrent loopback requests with checked response hashes.
  - Baseline limited accept queue reproduces loss; corrected server admits the same bounded burst.
  - Missing resource and genuine script exception remain observable failures.
  - All product assertions and timeout values are byte-equivalent outside HTTP imports.
  - Full raw gate and independent control-plane audit are recorded after candidate freeze.
approved_tests: [fixture_positive_negative_comparison, historical_failed_suites, quality_gate_full_raw, independent_control_plane_audit]
```

A autorização humana vigente cobre corrigir todas as falhas registradas. Esta trilha aplica esse pedido à causa demonstrada do carregamento local: somente capacidade da fila HTTP. Não muda o juiz, expectativas, classificação ou receipts anteriores.

Fonte Harness: `/Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/2 - TRABALHO/99A -   SOFTWARE DEV/99 - PROMPTS SOFTWARE DEV/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md`, SHA-256 `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`, §§12–16 e 28–30. Baseline e delta preexistente preservados fora do repositório.

## Delta implementado e caracterização

O helper `tools/browser_fixture_server.py` altera somente a fila de aceitação HTTP para 128. As 36 suítes sem fila configurada importam essa subclasse; todos os bytes fora das importações são idênticos à baseline. A comparação de 32 conexões simultâneas, com o mesmo prazo, produziu 5/32 arquivos na fila anterior e 32/32 na corrigida, conferidos por hash; arquivo ausente continua HTTP 404. Auditoria independente adicional usou os mesmos 99 scripts reais em 12 contextos Chromium, preservando captura de erros e controles negativos. Nenhuma tolerância, assertiva, classificação, cenário, gate ou stub de rede foi alterado.
