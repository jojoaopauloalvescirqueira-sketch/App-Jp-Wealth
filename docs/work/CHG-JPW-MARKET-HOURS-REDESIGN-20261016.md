# Bolsas Globais — redesign consulta primeiro

```yaml
schema: jp-harness/chg/v1
change_id: CHG-JPW-MARKET-HOURS-REDESIGN-20261016
status: approved
objective: Implementar o plano humano consulta primeiro, com abertas no início, estados claros e mapa expansível no celular.
risk_level: N1
authority_required: A2
target:
  root: /private/tmp/jpw-time-twins-20261015
  branch: codex/bolsas-globais-aisol-20261015
  baseline_sha: 2b22175a4f3f47b1f289deca65366c4dc0445dca
scope:
  allowed_files: [src/js/40-app/31-market-hours/01-sessions.js, src/js/40-app/31-market-hours/03-view.js, src/js/40-app/31-market-hours/04-controller.js, src/styles/app.css, src/js/40-app/26-learning-catalog.js, src/js/manifest.json, tools/market_hours_unit_test.js, tools/market_hours_browser_test.py, tools/market_hours_redesign_test.py, tools/market_hours_integration_test.py, tools/market_hours_performance_test.py, docs/architecture/MARKET-HOURS.md, docs/architecture/NAVIGATION-HIERARCHY.md, docs/architecture/PWA-UPDATE-LIFECYCLE.md, docs/work/CHG-JPW-MARKET-HOURS-REDESIGN-20261016.md, docs/work/CTX-JPW-MARKET-HOURS-REDESIGN-20261016.md, docs/work/ACTIVE-TASK.md, docs/governance/CURRENT-STATE.md, SESSION_HANDOFF.md, CHANGELOG.md]
  forbidden_files: [AGENTS.md, CLAUDE.md, skills/, .github/, docs/normative/, mt5/, tools/quality_gate.py, tools/agent_preflight.py, src/js/00-core/00-forex-policy.js, src/js/10-domain/, src/data/market-hours/, src/vendor/aisol-dot-globe/]
  allowed_actions: [bounded_product_edits, synthetic_tests, independent_review, local_preview, official_generation, factual_context_records]
  forbidden_actions: [commit, push, merge, deploy, new_branch, new_worktree, destructive_git, dependency_changes, financial_writes, schema_changes]
derived_artifacts:
  allowed: [build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html, src/vendor/downloads/, src/vendor/market-hours/runtime-payload.js]
  generation_commands: [python3 tools/rebuild_monolith.py --refresh-manifest]
  manual_edit: forbidden
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: forbidden
acceptance_criteria: [shared_open_predicate_count_filter_parity, honest_unknown_and_transition_labels, grouped_list_first, initial_b3_selection, preserved_focus_search_scroll, mobile_map_collapsed_and_paused, progressive_details, distributions_preserved, no_financial_changes]
approved_tests: [market_hours_focals, affected_navigation_and_guide_regressions, validate_project, build_reproducibility, leverage_suite_test, quality_gate_full]
rollback:
  source: [.superpowers/sdd/jpw-market-redesign-20261016/baseline.tar.gz, .superpowers/sdd/jpw-market-redesign-20261016/baseline-map.json]
  application_state: [no_user_state_writes]
  verification: [baseline_hash_comparison]
approved_by: user_in_conversation
approved_at: 2026-10-16
expires_on: [material_scope_or_branch_change, sensitive_data_or_financial_or_control_plane_change]
```

## Autoridade e compreensão

O proprietário pediu “PLEASE IMPLEMENT THIS PLAN” para o redesign integral desta área. A autorização específica anterior da branch permanece nesta mesma implementação, preservando o candidato completo. Este registro descreve o pedido; não concede autoridade. Sem commit, merge, push ou publicação.

JP Wealth existe para organizar atividades financeiras locais com integridade dos dados. Bolsas Globais é uma consulta informativa de calendários de ações: o motor puro resolve grupos/sessões, a apresentação organiza resultados e o controlador cuida de visibilidade e carregamento do globo. Hoje o mapa precede a consulta móvel, o detalhe fica distante e o filtro de fase não coincide com o conceito de aberta. Depois, a lista e seus estados devem responder primeiro à consulta, mantendo a incerteza explícita. Navegação, guia, host Ferramentas, acessibilidade e distribuições são consumidores pertinentes. Não alterar calendários, regras financeiras, contas, writers, progresso dos jogos, backup ou ciclo conservador do PWA.

Núcleo AGENTS, README, CONTEXT-MAP, contrato MARKET-HOURS, navegação e PWA consultados. MASTER canônico localizado no vault de trabalho em `99 - Prompts&Skills/9 - SOFTWARE/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md`, SHA256 `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`, §§12–14,24,36–53 pertinentes. O caminho antigo no AGENTS não foi alterado. Princípios de hierarquia, exposição progressiva e estados acessíveis do plano aprovado são aplicados somente à superfície local, preservando tokens globais e identidade do produto.

## Baseline e provas previstas

Raiz isolada existente e branch/HEAD conferidos. Preflight audit e edit --allow-dirty PASS, preservando aviso histórico de frescor. Mapa inicial de1102arquivos SHA256 `26ba26079af80638b2de3e04957349de1cb5cbc13785c407dd7a17a7da41bdda`; backup integral SHA256 `9c0e90da3ba1554a7fda8b0875bc0caf5b88e1cec82800c9c09bfa136dcae31e`. Nenhuma remoção ou limpeza automática. Fotografias históricas não aprovam estes bytes novos.

Plano e ledger em `.superpowers/sdd/jpw-market-redesign-20261016/`. Testes por comportamento: predicado e snapshots preservados; filtros/agrupamentos/unknown/transições; seleção/foco/scroll; pausa e singleton; matriz responsiva; dados sintéticos intactos; HTTP/file/PWAoffline/portátil; revisão independente; geração oficial e gate completo. Congelar identidade do candidato final, registrar comandos/resultados e preservar falhas anteriores. Teste humano, Safari, leitor de tela e toque físico permanecem NOT_RUN até execução própria.
