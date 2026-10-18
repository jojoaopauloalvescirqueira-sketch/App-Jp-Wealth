# Bolsas Globais — próximas aberturas e meio-dia

```yaml
schema: jp-harness/chg/v1
change_id: CHG-JPW-MARKET-NOON-20261016
status: approved
objective: Implementar próximas sessões confirmadas e orientação aproximada de meio-dia conforme plano humano integral de16/10.
risk_level: N1
authority_required: A2
target:
  root: /private/tmp/jpw-time-twins-20261015
  branch: codex/bolsas-globais-aisol-20261015
  baseline_sha: 2b22175a4f3f47b1f289deca65366c4dc0445dca
scope:
  allowed_files: [src/js/40-app/31-market-hours/01-sessions.js, src/js/40-app/31-market-hours/03-view.js, src/js/40-app/31-market-hours/04-controller.js, src/js/40-app/31-market-hours/aisol/entry.js, src/styles/app.css, tools/market_hours_unit_test.js, tools/market_hours_upcoming_test.py, tools/market_hours_noon_test.py, tools/market_globe_test.py, tools/market_hours_macos_test.py, tools/market_hours_redesign_test.py, tools/market_hours_browser_test.py, tools/market_hours_integration_test.py, tools/market_hours_performance_test.py, docs/architecture/MARKET-HOURS.md, docs/superpowers/plans/2026-10-16-market-noon.md, docs/work/CHG-JPW-MARKET-NOON-20261016.md, docs/work/CTX-JPW-MARKET-NOON-20261016.md, docs/work/ACTIVE-TASK.md, docs/governance/CURRENT-STATE.md, SESSION_HANDOFF.md, CHANGELOG.md, tools/regression-memory.json]
  forbidden_files: [AGENTS.md, CLAUDE.md, skills/, .github/, docs/normative/, mt5/, tools/quality_gate.py, tools/agent_preflight.py, src/js/10-domain/, src/data/market-hours/, src/js/40-app/31-market-hours/aisol/engine.js]
  allowed_actions: [bounded_product_edits, synthetic_tests, independent_review, local_preview, official_generation, factual_context_records]
  forbidden_actions: [commit, push, merge, deploy, new_branch, new_worktree, destructive_git, dependency_changes, financial_writes, persisted_schema_changes]
derived_artifacts:
  allowed: [build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html, src/js/manifest.json, src/vendor/downloads/, src/vendor/market-hours/runtime-payload.js, src/vendor/aisol-dot-globe/aisol-globe.iife.js, src/vendor/aisol-dot-globe/build-meta.json, src/vendor/aisol-dot-globe/build-receipt.json]
  generation_commands: [python3 tools/build_market_globe.py --three-root /private/tmp/jpw-globe-build/node_modules/three --esbuild-bin /private/tmp/jpw-globe-build/node_modules/.bin/esbuild, python3 tools/rebuild_monolith.py --refresh-manifest]
  manual_edit: forbidden
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: forbidden
acceptance_criteria: [open_default_and_first, distinct_upcoming_24h, indexed_confirmed_open_windows, uncertainty_barriers, stable_row_migration, noon_reference, accepted_interactions_and_10s_deadline, hidden_zero_work, lifecycle_and_fallback, no_financial_changes, distributions_preserved]
approved_tests: [market_hours_focals, market_globe_focals, native_zoom, distributions, validate_project, build_reproducibility, quality_gate_full]
rollback:
  source: [.superpowers/sdd/jpw-market-noon-20261016/baseline.tar.gz, .superpowers/sdd/jpw-market-noon-20261016/baseline-map.json]
  application_state: [no_user_state_writes]
  verification: [baseline_hash_comparison]
approved_by: user_in_conversation
approved_at: 2026-10-16
expires_on: [material_scope_or_branch_change, sensitive_data_or_financial_or_control_plane_change]
```

O plano humano integral autoriza engine de calendário e adapter neste delta; os limites do CHG visual anterior não se transferem para este escopo novo. Preservam-se o catálogo compilado, engine Aisol original, licenças, controles financeiros, três jogos e import JP Engenharia congelado. Adição somente ao snapshot efêmero, sem persistência. Preflight edit --allow-dirty PASS com81pendências e aviso histórico225caminhos; não equivale a reconciliação global. Baseline1133arquivos/8links e arquivo recuperável no workspace. MASTER e instruções permanecem intactos. Histórico de incidentes não se encerra por aprovação de nova execução. Aceite humano e publicação não são parte dos testes.

## Resultado factual

Builde3a3e248e50edc96;27comandos focais exit0, FULL atual81PASS/0outros resultados/81IDs. BrutoSHAc492b67879453ac06e173fd258d031b8f6b7e1d1219b21074b89963e73b03cad, mapa testado1138/8links SHA515422312dd9448028dcd692ba26181f029cfc68ea8d1e554be0b0b05120f9c4. Revisões independentes semP1/P2 aberto após rodada1. Histórico obrigatório permaneceNOT_APPROVED sem reparo causal demonstrado. Relatório e limites em tools/.artifacts/market-hours/noon-openings-20261016/REPORT.md. Nenhum bloco de autoridade alterado, nenhuma operaçãoGit/publicação.
