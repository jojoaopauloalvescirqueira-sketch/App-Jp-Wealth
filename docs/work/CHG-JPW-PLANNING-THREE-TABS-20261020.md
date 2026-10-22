---
schema: jp-harness/chg/v1
change_id: CHG-JPW-PLANNING-THREE-TABS-20261020
status: approved
objective: Corrigir a experiência pública para três abas da planilha atual, formulário acessível, ordem do menu e Notas globais.
risk_level: N1
authority_required: A2
target:
  root: JP Wealth OS
  branch: codex/planejamento-patrimonial-20261020
  baseline_sha: ea15afc9c6a9c30cc69c5b98a8b85c85211ffb34
scope:
  allowed_files: [src/js/40-app/01-navigation.js, src/js/30-accounting/06-planning/03-ui.js, src/js/20-ui/12-nav-style.js, src/js/40-app/14-mvp-notes.js, src/js/40-app/26-learning-catalog.js, src/styles/app.css, src/js/manifest.json, index.html, tools/planning*_test.js, tools/planning*_test.py, tools/*navigation*_test.py, tools/notes_launcher_test.py, tools/notes_global_launcher_test.py, tools/forex_task_design_test.py, tools/presentation_refactor_contract_test.py, tools/quality_gate.py, tools/regression-memory.json, docs/architecture/PLANNING.md, docs/architecture/PLANNING-MONTHLY.md, docs/architecture/NAVIGATION-HIERARCHY.md, docs/architecture/CODE-MAP.md, docs/architecture/ARCHITECTURE.md, docs/governance/PROJECT-CONTEXT.md, docs/governance/CONTEXT-MAP.md, docs/governance/CURRENT-STATE.md, docs/work/ACTIVE-TASK.md, docs/work/CHG-JPW-PLANNING-THREE-TABS-20261020.md, docs/superpowers/plans/2026-10-20-planning-three-tabs.md, docs/validation/planning-three-tabs-20261020/**, README.md, CHANGELOG.md, SESSION_HANDOFF.md]
  forbidden_files: [AGENTS.md, skills/**, .github/**, docs/normative/**, mt5/**, downloads/**, src/js/30-accounting/06-planning/01-engine.js, src/js/30-accounting/06-planning/02-state.js]
  allowed_actions: [implementar plano humano aprovado, acrescentar regressões permanentes, substituir expectativas públicas revogadas por três abas e Notas globais com evidência, reconstruir oficialmente, atualizar contratos e registros factuais delimitados]
  forbidden_actions: [commit, push, pull, merge, deploy, reset, stash, rebase, criar branch ou worktree, alterar fórmulas financeiras, migrar dados reais, redefinir preferências pessoais, editar control plane]
derived_artifacts:
  allowed: [build-id.js, dist/**, src/vendor/downloads/*-payload.js, src/vendor/downloads/*-payload.json, src/vendor/market-hours/runtime-payload.js]
  generation_commands: [python3 tools/rebuild_monolith.py --refresh-manifest]
  manual_edit: forbidden
external_side_effects:
  network: allowed
  allowed_targets: [planilha original somente leitura, localhost, fonte pública de câmbio já existente]
  temporary_artifacts: allowed
  cleanup_required: false
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: forbidden
acceptance_criteria: [três abas públicas, formulário sempre acessível, dois marcos visíveis antes de gravar, sem blocos ocultos históricos, ordem editável após Research, Notas globais com modais, dados e motores preservados, comparação independente, distribuição e FULL do pacote final]
approved_tests: [focais permanentes de Planejamento, Notas e navegação, regressões financeiras existentes, distribuições, reprodutibilidade, quality_gate.py --tier full]
rollback:
  source: [.superpowers/sdd/planning-three-tabs-20261020/candidate-443c-before.tar.gz e baseline.json]
  application_state: [sem migração ou exclusão; engine e state preservados; dados legados no Backup Completo]
  data: [fixtures sintéticas, sem perfil pessoal do navegador]
approved_by: proprietário no pedido PLEASE IMPLEMENT THIS PLAN e nas escolhas materiais da conversa
approved_at: 2026-10-20
---

# Brief da correção

Base de Git ea15afc com o candidato completo443c1a59f2c1f46d e trabalho pendente preservado. Fingerprint anterior327, inventário runtime397, testes257 e runner foram conferidos antes desta edição; backup recuperável de1629 arquivos e oito links. A autorização vigente reutiliza a branch e não concede ações Git/publicação.

JP Wealth preserva registros financeiros locais. Esta tarefa corrige apresentação/acesso, sem reinterpretar a matemática da simulação nem a norma Forex. Planejamento usa UI em06-planning; o motor puro e o escritor confirmado não podem mudar. Efeitos compartilhados ficam limitados à ordem visual e ao launcher de Notas.

O metadata vivo da planilha1Wo1Qwvfd7okSClnCwKateirerP77Z0fWGHmg51wG2EA, relido antes da edição, confirma somente Comece aqui412953685, Consolidado1976101601 e Preenchimento mensal1335698432 visíveis; Referência1976101612 está hidden=true. A fotografia anterior de quatro abas continua historicamente verdadeira. ApresentacaoConsolidado.gs79–83 remove o gráfico de objetivos e oculta84–154;71–77 oculta255–270. Readback apenas de rótulos associa a comparação de aportes ao primeiro bloco; indicadores no topo13 permanecem visíveis.

Decisões humanas: menu Stoikus operacional separado; Notas visíveis em todas as áreas quando Mostrar está habilitado, temporariamente ocultas em modais; ordem padrão editável, sem sobrescrever ordens personalizadas. Formulário conserva perguntas e matemática, mas abre escolha explícita em vez de redirecionar quando há múltiplas contas sem seleção. Fonte cambial do site e impressão local permanecem diferenças aprovadas.

Proteções: motores/state, três minigames, Bolsas Globais, normas, downloads, dados/histórico, preferências e protocolos de confirmação preservados. Testes de quatro abas, ordem anterior e ocultação Forex são contratos de produto superados pelo plano humano, não justificativa para enfraquecer testes financeiros ou gates. Cada diferença corrigida terá RED/GREEN identificável, com evidência bruta e bytes.

Bootstrap e procedimento: AGENTS, JP Engenharia local1.3.0 congelado, preflight/change-control, diagnóstico/validação, Superpowers TDD/SDD e plano aprovado. Nenhuma instalação nem alteração de instruções é necessária. Ao finalizar, reconstruir depois de concluir documentos que compõem o fingerprint; congelar todos os inputs oficiais antes do FULL e escrever recibos finais somente fora deles.

A inspeção do resolvedor mostrou que sua lista pública ainda inclui reference e accounts é mapeado para start. A apresentação de três abas e os aliases para Consolidado, explicitamente aprovados no plano, também exigem o delta delimitado em40-app/01-navigation.js; mesma classificação N1, sem mudança de autoridade, dados ou guardas.

Manifesto: o gerador oficial --refresh-manifest atualiza hashes dos scripts clássicos existentes; src/js/manifest.json é input autorizado somente para esta reconstrução. Nenhum script/dependência novo foi introduzido nem a ordem clássica alterada.
