# Bolsas Globais — contrato focal de implementação

```yaml
schema: jp-harness/chg/v1
change_id: CHG-JPW-MARKET-HOURS-20261015
status: approved
objective: Integrar o Aisol com Three local e tabela sincronizada de sessões de ações, incluindo B3 e as 16 praças do plano.
risk_level: N1
authority_required: A2
target:
  root: /private/tmp/jpw-time-twins-20261015
  branch: codex/bolsas-globais-aisol-20261015
  baseline_sha: 2b22175a4f3f47b1f289deca65366c4dc0445dca
scope:
  allowed_files: [tools/capital_currents_browser_test.py, tools/learning_guide_test.py, tools/nocuda_tools_test.py, tools/market_hours_performance_test.py, tools/market_hours_build_test.py, sw.js, tools/market_hours_assets_test.py, tools/market_hours_integration_test.py, tools/market_hours_catalog_test.js, tools/minigames_test.py, tools/navigation_ia_test.py, src/js/40-app/31-market-hours/, src/vendor/aisol-dot-globe/, src/vendor/market-hours/, src/data/market-hours/, tools/build_market_globe.py, tools/compile_market_hours.py, tools/market_globe_test.py, tools/market_hours_unit_test.js, tools/market_hours_browser_test.py, index.html, src/styles/app.css, src/js/40-app/01-navigation.js, src/js/20-ui/31-tools-services.js, src/js/40-app/07-finalize-session.js, src/js/40-app/26-learning-catalog.js, src/js/manifest.json, tools/rebuild_monolith.py, tools/build_reproducibility_test.py, docs/architecture/MARKET-HOURS.md, docs/architecture/NAVIGATION-HIERARCHY.md, docs/architecture/PWA-UPDATE-LIFECYCLE.md, docs/work/CHG-JPW-MARKET-HOURS-20261015.md, docs/work/CTX-JPW-MARKET-HOURS-20261015.md, docs/work/ACTIVE-TASK.md, docs/governance/CURRENT-STATE.md, SESSION_HANDOFF.md, CHANGELOG.md]
  forbidden_files: [AGENTS.md, CLAUDE.md, skills/, .github/, docs/normative/, src/js/00-core/00-forex-policy.js, src/js/10-domain/00-forex-engine.js, tools/quality_gate.py, tools/agent_preflight.py, mt5/]
  allowed_actions: [bounded_product_edits, synthetic_tests, source_review, local_preview, isolated_vendor_build, official_generation, factual_context_records]
  forbidden_actions: [commit, push, merge, deploy, new_worktree, destructive_git]
  regressions_forbidden: [financial_rules_or_data, backup_format, drafts, current_minigames, conservative_pwa_lifecycle]
derived_artifacts:
  allowed: [build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html, src/vendor/downloads/, src/vendor/market-hours/]
  generation_commands: [python3 tools/build_market_globe.py, python3 tools/compile_market_hours.py, python3 tools/rebuild_monolith.py]
  manual_edit: forbidden
external_side_effects:
  network: allowed
  allowed_targets: [public_primary_exchange_sources, framer_public_reference, official_three_sources, official_esbuild_sources, registry_npmjs_org]
  temporary_artifacts: allowed
  cleanup_required: false
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: forbidden
toolchain:
  dependency_changes: [local_vendored_Three_candidate_0.186.1, isolated_esbuild_candidate_0.25.12]
  allowed_processes: [python_existing_runtime, node_existing_runtime, ephemeral_playwright_browser, local_http_server]
acceptance_criteria: [faithful_aisol_adapter, synchronized_table_and_globe, explicit_calendar_coverage, sixteen_venues_including_b3, no_financial_writes, lazy_local_runtime, file_portable_offline, independent_review]
approved_tests: [new_market_hours_focals, affected_navigation_and_learning_regressions, build_reproducibility, validate_project, leverage_suite_test, quality_gate_full]
rollback:
  source: [.superpowers/sdd/PLANO-AISOL/baseline.tar.gz, .superpowers/sdd/PLANO-AISOL/baseline-map.json]
  application_state: [no_user_state_writes]
  verification: [baseline_hash_comparison]
approved_by: user_in_conversation
approved_at: 2026-10-15
expires_on: [material_scope_change, incorrect_branch_or_root, new_sensitive_data, financial_or_control_plane_change]
```

## Autoridade observável e limite

O usuário escolheu adaptar o próprio Aisol, depois pediu **“implemente o plano”** e autorizou especificamente **“Autorizar essa branch e preservar o candidato completo”**. Este registro documenta essas instruções; não concede autoridade por si. Não há autorização de commit, merge, push ou publicação.

## Compreensão e baseline

JP Wealth é um aplicativo financeiro local-first, com módulos de leitura/registro e escritores específicos. Ferramentas oferece utilidades auxiliares e os três minigames, hoje sem área de sessões globais. A nova área fornece informação pública conforme calendário, não recomendação, cotação ou confirmação operacional. Motor puro e catálogo são independentes de S, contas e regras. Navegação, host Ferramentas, guia e distribuição são os consumidores compartilhados; rascunhos e seus guards são preservados.

Raiz existente e isolada foi reutilizada; ramo novo preserva as 43 pendências anteriores. O mapa de 1048 arquivos foi conferido sem diferenças antes da primeira edição. Seis symlinks de skills coincidem com HEAD. Backup recuperável e hashes em `.superpowers/sdd/PLANO-AISOL/bootstrap.json`; candidate anterior build0afa0cf4a8334f85. Preflight audit passou. Edit inicialmente bloqueou pelo dirty conhecido; após conferir escopo e autorização de preservação, `--mode edit --allow-dirty` passou, sem alterar o validador. Aviso histórico de contexto permanece registrado.

Fonte canônica de engenharia localizada no caminho atual `.../2 - TRABALHO/99 - Prompts&Skills/9 - SOFTWARE/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md`, SHA256b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95; §§12–14/24/36–48 pertinentes foram consultados. Núcleo AGENTS e contratos de navegação/PWA/manifests são fontes do delta. A divergência do antigo caminho de usuário não foi corrigida no control plane.

Princípios X1: ADOTAR hierarquia, estados honestos e continuidade; ADAPTAR o efeito Aisol aos tokens existentes; NÃO APLICÁVEL qualquer mudança financeira ou migração de framework. Evidência de testes, revisão e aceite será registrada no relatório do mesmo candidate; resultados anteriores não são transferidos.

Classificação conferida durante a execução: `sw.js` é fonte mantida da lista explícita de precache; o gerador oficial não o escreve. A edição delimitada acrescenta somente recursos da área e preserva seu ciclo conservador. As expectativas dos dois testes de navegação recebem a sexta entrada aprovada, preservando seus demais critérios.

Adaptação factual das regressões de produto já aprovadas: `learning_guide_test.py` incorpora somente os quatro módulos Market Hours nomeados, mantendo o hash dos106 scripts originais e os oráculos legados; `nocuda_tools_test.py` incorpora a sexta entrada Bolsas Globais e a passagem explícita por ela no teclado. As expectativas antigas divergiram do menu/carga aprovados; resultados brutos do full79PASS/2PRODUCT_FAIL são preservados e suas causas classificadas separadamente como TEST_HARNESS_FAIL por inventário legado. Nenhum gate, validador ou teste do Harness é alterado.

A regressão dos minigames, já prevista no plano, explicita `tools/capital_currents_browser_test.py`: a matriz de zoom CSS deve começar cada apresentação com pageScale1, sem offsets visuais adicionais; deve verificar essa condição inicialmente e antes do retorno, sem reset corretivo intermediário. Preservar48 apresentações, click original, seis pontos de hit, toque, foco, overflow e a classificação nativeZoomNOT_RUN. Diagnóstico externo confirmou que ampliação nativa extra deslocava as coordenadas da automação; um clique nativo centro−offset acionou o retorno sem mudar a interface. Preservar o PRODUCT_FAIL bruto, separado de sua triagem TEST_HARNESS_FAIL. Não altera aplicativo, critérios do produto, política, composição do gate ou Harness.

Revisão delimitada da preparação da matriz após prova adicional: o protótipo preservado c6ea43 identificou que offset visual zero antes de Voltar não é invariante válida em contexto móvel, mesmo com escala1. Manter escala1 por apresentação CSS e verificar escala antes do retorno; não impor offset zero nesse segundo ponto nem fazer reset corretivo. Após scroll normal do botão e medição estável, conservar Locator.click quando offsets são zero; com offsets não nulos, permitir um único mouse.click nativo no centro menos offsets, exigindo visível/habilitado/centro desobstruído e dentro do viewport, evento trusted no próprio Back e retorno real ao hub. Preservar todos os62 asserts originais,48 casos,hitpoints,toque,foco,overflow e snapshots. Sem force, evaluate-click, retry, ocultação de overlay ou alteração de produto. Prova controlada confirmou o mapeamento; ajuste continua N1/A2 de fixture de produto já autorizada, sem mudar gates ou Harness.
