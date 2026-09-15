# Consolidado FX — extensão delimitada do empacotamento PDF

```yaml
schema: jp-harness/chg/v1
change_id: CHG-FOREX-CONSOLIDATED-PDF-BUILD-20260914
status: approved
objective: Carregar PDF.js local e offline sem converter scripts clássicos ou enfraquecer validadores.
risk_level: N3
authority_required: A4
target:
  root: /Users/joaopauloalves/.codex/forex-consolidated/20260914/product
  branch: codex/forex-consolidated-20260914
  baseline_sha: 01c08241ccb7bc229a05779a52f577ee55a69ae7
scope:
  allowed_files: [src/vendor/pdfjs/, src/js/40-app/25-fx-consolidated-pdf.js, tools/rebuild_monolith.py, tools/agent_preflight.py, tools/validate_project.py, tools/build_reproducibility_test.py, tools/fx_consolidated_pdf_test.py, src/js/manifest.json, sw.js, docs/work/CHG-FOREX-CONSOLIDATED-PDF-BUILD-20260914.md]
  forbidden_files: [AGENTS.md, CLAUDE.md, skills/, .github/, tools/quality_gate.py]
  allowed_actions: [vendor_official_pinned_pdfjs, extend_resource_validation, official_build, synthetic_tests, focal_audit]
  forbidden_actions: [weaken_existing_checks, global_install, commit, push, merge, deploy]
derived_artifacts:
  allowed: [build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html]
  generation_commands: [python3 tools/rebuild_monolith.py]
  manual_edit: forbidden
external_side_effects:
  network: allowed
  allowed_targets: [github.com/mozilla/pdf.js, registry.npmjs.org/pdfjs-dist, localhost]
  temporary_artifacts: allowed
  cleanup_required: false
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: approved
acceptance_criteria: [local_assets_only, portable_and_PWA_offline, worker_cleanup, resources_hashed, all_previous_checks_preserved]
approved_tests: [fx_consolidated_pdf_test, existing_build_reproducibility, service_worker_upgrade, full, independent_control_plane_audit]
rollback:
  source: [../evidence/baseline.tar, own_delta_only]
  verification: [original_validator_checks_preserved, no_global_changes]
approved_by: owner_plan_implementation_and_isolation_authorization
approved_at: 2026-09-14
```

Antes: manifest concatena scripts clássicos, sem loader ESM/worker. Depois: adapter clássico carrega recursos PDF declarados e validados separadamente; gerador incorpora bytes no portátil e hashes no build. Validadores devem continuar rejeitando ausência, hash incorreto, ordem/tag incorreta e recursos fora da raiz. Nenhuma alteração de tier, CI ou expectativa para mascarar falha. Prova focal adversarial e auditoria independentes do autor são obrigatórias. Candidate final ainda não produzido.

O preparo das cópias no teste existente de reprodutibilidade inclui também os
`runtimeAssets` declarados; antes ele copiava somente Git tracked e scripts
clássicos, omitindo recursos novos ainda não commitados. As comparações e
contraprovas existentes permanecem integrais. Trata-se do empacotamento de
fixtures necessário à extensão de build já aprovada.
