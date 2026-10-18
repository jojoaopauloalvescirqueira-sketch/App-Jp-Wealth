# Bolsas Globais — composição macOS

```yaml
schema: jp-harness/chg/v1
change_id: CHG-JPW-MARKET-MACOS-20261016
status: approved
objective: Implementar a composição macOS Mapas aprovada pelo proprietário, preservando a consulta honesta de calendários.
risk_level: N1
authority_required: A2
target:
  root: /private/tmp/jpw-time-twins-20261015
  branch: codex/bolsas-globais-aisol-20261015
  baseline_sha: 2b22175a4f3f47b1f289deca65366c4dc0445dca
scope:
  allowed_files: ["src/js/40-app/31-market-hours/03-view.js", "src/js/40-app/31-market-hours/04-controller.js", "src/styles/app.css", "tools/market_hours_macos_test.py", "tools/market_hours_redesign_test.py", "tools/market_hours_integration_test.py", "tools/market_hours_browser_test.py", "tools/market_hours_performance_test.py", "docs/architecture/MARKET-HOURS.md", "docs/superpowers/plans/2026-10-16-market-macos.md", "docs/work/CHG-JPW-MARKET-MACOS-20261016.md", "docs/work/CTX-JPW-MARKET-MACOS-20261016.md", "docs/work/ACTIVE-TASK.md", "docs/governance/CURRENT-STATE.md", "SESSION_HANDOFF.md", "CHANGELOG.md", "tools/regression-memory.json"]
  forbidden_files: [AGENTS.md, CLAUDE.md, skills/, .github/, docs/normative/, mt5/, tools/quality_gate.py, tools/agent_preflight.py, src/js/10-domain/, src/data/market-hours/, src/vendor/aisol-dot-globe/, src/js/40-app/31-market-hours/01-sessions.js]
  allowed_actions: [bounded_product_edits, synthetic_tests, independent_review, local_preview, official_generation, factual_context_records]
  forbidden_actions: [commit, push, merge, deploy, new_branch, new_worktree, destructive_git, dependency_changes, financial_writes, schema_changes]
derived_artifacts:
  allowed: [build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html, src/js/manifest.json, src/vendor/downloads/, src/vendor/market-hours/runtime-payload.js]
  generation_commands: [python3 tools/rebuild_monolith.py --refresh-manifest]
  manual_edit: forbidden
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: forbidden
acceptance_criteria: [integrated_list_inspector, whole_row_selection_once, actual_container_responsiveness, immediate_selected_facts, preserved_query_focus_scroll, lazy_paused_singleton_map, honest_calendar_states, no_financial_changes, distributions_preserved]
approved_tests: [market_hours_focals, affected_navigation_and_guide_regressions, validate_project, build_reproducibility, quality_gate_full]
rollback:
  source: [.superpowers/sdd/jpw-market-macos-20261016/baseline.tar.gz, .superpowers/sdd/jpw-market-macos-20261016/baseline-map.json]
  application_state: [no_user_state_writes]
  verification: [baseline_hash_comparison]
approved_by: user_in_conversation
approved_at: 2026-10-16
expires_on: [material_scope_or_branch_change, sensitive_data_or_financial_or_control_plane_change]
```

## Compreensão e autoridade

O usuário aprovou expressamente implementar e melhorar após a proposta macOS de16/10. Reutiliza-se a branch isolada autorizada e o candidato completo, sem operaçãoGit. JPWealth organiza trabalho financeiro local; este módulo somente informa sessões de ações por calendários confirmados. View organiza consulta, controller cuida de visibilidade/renderer e engine permanece intacto. A mudança aproxima seleção/consequência, reduz ruído e considera largura do host, mantendo incertezas, busca e seleção. HostFerramentas, navegação e distribuições são consumidores pertinentes; contas, escritores, calendários, jogos, backup e instruções permanecem preservados.

Fontes: AGENTS/README/CONTEXT-MAP, contrato MARKET-HOURS e proposta /private/tmp/jpw-market-macos-study-20261016/PROPOSTA.md lidos. MASTER canônico no vault2, SHA256b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95, preservado. Fotografias1129arquivos/77pendências e backup no workspace. Preflight edit sem --allow-dirty bloqueou corretamente a árvore pendente; confirmação prévia de autoria/escopo e repetição --allow-dirty PASS, sem limpeza. Aviso histórico de225caminhos permanece; este registro reconcilia somente a área visual com o candidato observado, não toda a documentação histórica.

Plano em docs/superpowers/plans/2026-10-16-market-macos.md. Trabalho de origem e fontes protegidas serão comparados por hashes. Critérios e evidências devem distinguir teste automatizado, avaliação heurística e aceite humano. Falhas anteriores da suíte continuam abertas; não alterar juízes para aprovar o delta.

## Resultado factual da implementação

Buildaf389c3e93393b08; candidate1133arquivos, mapaSHAb26f108cf2e95cc30688304d156156496fb92b2c8b8472cd54e1b110bf7eab8c. Focais e quatro distribuições PASS; FULL atual 81 PASS / 0 falhas: nenhuma falha nesta execução; incidentes históricos continuam abertos, sem declaração de correção causal. BrutoSHA6ec688596a18135e8e1e1d676e5bd337277e611ed19b5b9b325cec606bb7ac61, report em tools/.artifacts/market-hours/macos-20261016/REPORT.md. Sem mudança dos blocos de contrato ou autoridade. Histórico e limites preservados; mapas de teste/entrega separados. Sem operaçãoGit/publicação.
