# Correções de produto registradas — candidate local

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
change_id: CHG-JPW-PRODUCT-FAIL-REPAIR-20260930
objective: Correct reproduced product failures across the recorded JPW candidate without changing financial rules or user records.
risk_level: N1
authority_required: A2
scope:
  allowed_files: [src/js/40-app/01-navigation.js, src/js/40-app/11-operational-shell.js, src/js/20-ui/26-forex-engine-views.js, src/js/30-research/**, src/styles/app.css, docs/work/CHG-JPW-PRODUCT-FAIL-REPAIR-20260930.md]
  forbidden_files: [AGENTS.md, skills/**, docs/normative/**, docs/decisions/**, src/js/00-core/00-forex-policy.js, src/js/10-domain/00-forex-engine.js, src/js/00-core/04-persistence.js, mt5/**, tools/quality_gate.py]
  allowed_actions: [minimal_reproduced_ui_fix, regenerate_official_artifacts, run_synthetic_tests, independent_audit]
  forbidden_actions: [financial_rule_change, real_data_migration, commit, push, merge, deploy, operational_mt5_install]
  regressions_forbidden: [change_metric_formulas, overwrite_preexisting_delta, hide_failures, modify_financial_records]
acceptance_criteria:
  - Reproduced product defects receive bounded root-cause corrections and real-browser verification.
  - Historical failure IDs have current outcomes traced without editing prior receipts.
  - Same financial formulas, records, and NoCuda geometry remain unchanged.
approved_tests: [focused_reproductions, quality_gate_full_raw, mt5_host_suite, independent_product_audit]
```

## Resultado da investigação de produto

As falhas atuais de Galton e submenu não justificaram alterações do runtime: suas reproduções localizaram perda de scripts HTTP e os percursos completos passaram com os mesmos bytes. O produto continua idêntico à baseline 1.11.0. As correções efetivas estão nas trilhas separadas de infraestrutura de testes e contexto operacional. Não há interpretação financeira nova nem modificação de registros. O full final e o inventário de resultados atuais ficam nos recibos externos, preservando as classificações históricas.
