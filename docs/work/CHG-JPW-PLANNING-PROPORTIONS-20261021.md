---
schema: jp-harness/chg/v1
change_id: CHG-JPW-PLANNING-PROPORTIONS-20261021
status: approved
objective: Corrigir posições e proporções das janelas e formulários de Planejamento conforme plano humano aprovado.
risk_level: N1
authority_required: A2
target:
  root: JP Wealth OS
  branch: codex/planejamento-patrimonial-20261020
  baseline_sha: ea15afc9c6a9c30cc69c5b98a8b85c85211ffb34
scope:
  allowed_files: [src/js/30-accounting/06-planning/03-ui.js, src/styles/app.css, src/js/40-app/26-learning-catalog.js, src/js/manifest.json, index.html, tools/planning*_test.py, tools/planning*_test.js, tools/smoke_test.py, tools/exec_submenu_test.py, tools/quality_gate.py, tools/regression-memory.json, docs/architecture/PLANNING.md, docs/architecture/PLANNING-MONTHLY.md, docs/governance/CURRENT-STATE.md, docs/governance/CONTEXT-MAP.md, docs/governance/PROJECT-CONTEXT.md, docs/work/ACTIVE-TASK.md, docs/work/CHG-JPW-PLANNING-PROPORTIONS-20261021.md, docs/superpowers/plans/2026-10-21-planning-proportions.md, docs/validation/planning-proportions-20261021/**, README.md, CHANGELOG.md, SESSION_HANDOFF.md]
  forbidden_files: [AGENTS.md, skills/**, .github/**, docs/normative/**, mt5/**, downloads/**, src/js/30-accounting/06-planning/01-engine.js, src/js/30-accounting/06-planning/02-state.js]
  allowed_actions: [implementar plano humano aprovado, acrescentar regressões com RED e GREEN, reconciliar duas expectativas ordenadas obsoletas com provas, reconstruir oficialmente, atualizar contratos e registros factuais delimitados]
  forbidden_actions: [commit, push, pull, merge, reset, stash, rebase, deploy, criar branch ou worktree, alterar fórmulas, migrar dados reais, redefinir preferências pessoais, editar control plane]
derived_artifacts:
  allowed: [build-id.js, sw.js, dist/**, src/vendor/downloads/*-payload.js, src/vendor/downloads/*-payload.json, src/vendor/market-hours/runtime-payload.js]
  generation_commands: [python3 tools/rebuild_monolith.py --refresh-manifest]
  manual_edit: forbidden
external_side_effects:
  network: allowed
  allowed_targets: [localhost, referência original somente leitura, fonte pública cambial existente]
  temporary_artifacts: allowed
  cleanup_required: false
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: forbidden
acceptance_criteria: [janelas centralizadas, margens e larguras aprovadas, campos alinhados, fechar44px sem linha própria, previsão sem repetição, legenda legível, data no rodapé, perguntas e finanças preservadas, regressões permanentes, crítica independente, distribuições e FULL no pacote final]
approved_tests: [focais Planning e navegação, matriz de proporções, regressões financeiras e Notas, distribuições e reprodutibilidade, quality_gate.py --tier full]
rollback:
  source: [.superpowers/sdd/planning-proportions-20261021/candidate-09d53-before.tar.gz e baseline.json]
  application_state: [sem migração ou exclusão; motores e escritores preservados]
approved_by: proprietário no pedido PLEASE IMPLEMENT THIS PLAN corrente
approved_at: 2026-10-21
---

# Brief de compreensão e execução

JP Wealth organiza registros financeiros locais e simulações; esta tarefa atende a leitura e preenchimento confiável, sem alterar regras. UI06-planning monta três páginas e dialogs nativos; CSS Planning deve isolá-los do shell. A base09d53 foi verificada327/397/259/runner e preservada em1661arquivos+8links;215fontes protegidas serão idênticas. O candidato anterior é trabalho preexistente, não diff deste patch.

Hoje o resetglobal remove a centralização, labels flex separam opcional, headers móveis herdam wrap, nativeMilestone repete placeholders e stop-legend não possui geometria. Depois deverão satisfazer os critérios do plano, preservando engine/state, entradas/erros/rascunhos/tokens, confirmações, backups e consumidores.

Fontes: AGENTS, README e CONTEXT-MAP atuais; PLANNING; plano humano; JP Engenharia local1.3.0 e referências de diagnóstico/validação; Harness §§12–16 no caminho/hash registrados em source-authority.json. O caminho histórico de outro usuário foi resolvido para a fonte disponível do acervo, sem editar instruções. Skill SDD não autoriza commit/remoção/worktree nem substitui esta autorização de reutilização.

Revisão usa snapshots do delta real contra09d53, não só HEAD ea15afc. Provas de antes em /tmp jpw-planning-proportions-study e deep-proportions e recibos históricos; novo RED executável porbug. O FULL anterior foi interrompido90checks concluídos, sem recibo final e sem exit observado; suas duas falhas ordenadas e restantes provas permanecem brutas. Não há aprovação95até execução própria.
