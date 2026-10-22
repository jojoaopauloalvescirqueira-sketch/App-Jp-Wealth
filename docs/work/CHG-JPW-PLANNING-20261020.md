---
schema: jp-harness/chg/v1
change_id: CHG-JPW-PLANNING-20261020
status: approved
objective: Substituir Planejamento patrimonial legado por menu independente fiel aos cálculos e fluxos da planilha aprovada.
risk_level: N3
authority_required: A4
target:
  root: JP Wealth OS
  branch: codex/planejamento-patrimonial-20261020
  baseline_sha: ea15afc9c6a9c30cc69c5b98a8b85c85211ffb34
scope:
  allowed_files: [src/js/30-accounting/06-planning/**, src/js/30-accounting/05-fx-planning/**, src/js/30-accounting/02-accounting-engine.js, src/js/10-domain/08-usd-brl-quote.js, src/js/00-core/04-persistence.js, src/js/00-core/07-workspace-backup.js, src/js/00-core/08-module-availability.js, src/js/20-ui/25-dash-macro.js, src/js/20-ui/32-module-availability.js, src/js/20-ui/33-module-work.js, src/js/40-app/01-navigation.js, src/js/20-ui/03-main-render.js, src/js/20-ui/12-nav-style.js, src/js/40-app/06-boot.js, src/js/40-app/18-notification-center.js, src/js/30-accounting/01-daily-ledger.js, src/js/20-ui/26-forex-engine-views.js, src/styles/planning.css, src/js/40-app/07-finalize-session.js, src/js/40-app/11-operational-shell.js, src/js/40-app/12-global-dashboard.js, src/js/40-app/26-learning-catalog.js, src/js/manifest.json, sw.js, src/styles/app.css, index.html, tools/planning*, tools/smoke_test.py, tools/finpes_navigation_test.py, tools/fx_consolidated_ui_test.py, tools/contextual_sidebar_test.py, tools/forex_task_design_test.py, tools/forex_v11_journey_test.py, tools/visual_proportion_test.py, tools/fx_planning_test.py, tools/fx_monthly*, tools/scenario_fan_test.py, tools/financial_projection_audit_test.py, tools/behavior_finance_regression_test.py, tools/exec_submenu_test.py, tools/research_navigation_test.py, tools/forex_navigation*, tools/navigation*, tools/dashboard_macro_test.py, tools/module_availability*, tools/forex_v11_ledger_planning_test.py, tools/finalize_session_test.py, tools/usd_brl_quote_test.py, tools/forex_persistence_contract_test.py, tools/saving_draft_recovery_test.py, tools/forex_clarity_test.py, tools/presentation_refactor_contract_test.py, tools/learning_foundation_test.mjs, docs/validation/planning-20261020/**, tools/learning_guide_test.py, tools/quality_gate.py, tools/regression-memory.json, docs/architecture/PLANNING.md, docs/architecture/FX-PLANNING.md, docs/architecture/PLANNING-MONTHLY.md, docs/architecture/NAVIGATION-HIERARCHY.md, docs/architecture/STATE-SCHEMA.md, docs/architecture/CODE-MAP.md, docs/architecture/ARCHITECTURE.md, docs/governance/PROJECT-CONTEXT.md, docs/governance/CONTEXT-MAP.md, docs/governance/CURRENT-STATE.md, docs/work/ACTIVE-TASK.md, docs/work/CHG-JPW-PLANNING-20261020.md, docs/superpowers/plans/2026-10-20-planning.md, docs/decisions/2026-10-20-planning-reference.md, README.md, CHANGELOG.md, SESSION_HANDOFF.md]
  forbidden_files: [AGENTS.md, skills/**, .github/**, docs/normative/**, mt5/**, downloads/**]
  allowed_actions: [implementar plano aprovado, adicionar testes do produto, substituir proteções do contrato retirado por cobertura correspondente documentada, reconstruir artefatos oficiais, criar branch especificamente autorizada, registrar fatos e contratos afetados]
  forbidden_actions: [commit, push, pull, merge, deploy, reset, stash, rebase, excluir dados reais, migrar dados antigos automaticamente]
derived_artifacts:
  allowed: [build-id.js, dist/**, src/vendor/downloads/*-payload.js, src/vendor/downloads/*-payload.json, src/vendor/market-hours/runtime-payload.js]
  generation_commands: [python3 tools/rebuild_monolith.py --refresh-manifest]
  manual_edit: forbidden
external_side_effects:
  network: allowed
  allowed_targets: [Google Sheets de referência somente leitura, documentação oficial, câmbio público, localhost]
  temporary_artifacts: allowed
  cleanup_required: false
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: approved
acceptance_criteria: [paridade com insumos iguais, histórico preservado, navegação independente, zero escrita financeira fora do agregado, writer confirmado, matriz offline/portátil, auditoria independente, gate completo]
approved_tests: [focais de planejamento, navegação e disponibilidade, backup e finalização, distribuições, reprodutibilidade, quality_gate.py --tier full, suíte host afetada]
rollback:
  source: [baseline recuperável em .superpowers/sdd/planning-20261020/baseline.tar.gz; restauração pontual do próprio delta somente se autorizada]
  application_state: [legado fxPlanning preservado; novo agregado opcional e versionado]
  data: [nenhum perfil de uso será aberto; fixtures sintéticas]
approved_by: proprietário, em autorização conversacional do plano e da branch
approved_at: 2026-10-20
---

# Contrato da implementação

O plano integral aprovado é registrado em `docs/superpowers/plans/2026-10-20-planning.md`. Esta autorização cobre apenas a simulação patrimonial e os comandos descritos; perfis hipotéticos não alteram a política Forex V11. Mantêm-se conflitos normativos e incidentes históricos abertos. Testes novos registram regras; o gate não é enfraquecido para obter PASS.

Base: árvore limpa, 1576 entradas rastreadas; main local e GitHub conferidas em ea15afc. O checkout anterior estava em 0f24721 e não é base de implementação. Branch criada após autorização específica. Baseline de fontes/links recuperável no diretório ignorado da tarefa.

## Compreensão e fronteira

1. JP Wealth organiza dados financeiros locais. A tarefa substitui uma projeção global acoplada ao Forex por planejamento de várias contas, com resultados, aportes, saques e referências separados.
2. `30-accounting/05-fx-planning` contém hoje modelo/motor/state/UI; Contabilidade e Dashboard o consultam. `06-planning` abrigará o novo domínio, comandos e apresentação. O adaptador de Reservas V11 é preservado, não recalculado.
3. `forex-planning` atualmente é filho de Forex e apresenta motor próprio. Depois, `planning` será menu principal, com Consolidado, Mensal, Referência e Contas. Aliases antigos resolverão para ele, sem depender da disponibilidade Forex.
4. Afetados: rotas, consumidores, agregado opcional, backup, writers, rascunhos, fechamento de sessão, distribuição e documentação. Fonte da matemática: planilha original 1Wo1Qwvfd7okSClnCwKateirerP77Z0fWGHmg51wG2EA; Apps Script original verificado de 19/10, não modelo de cliente.
5. Preservar literalmente `S.fxPlanning`, unknown fields, Forex/PF/Alladin, segredos, três minigames, Bolsas Globais e ciclo conservador PWA. Não importar dados reais; primeiro uso vazio. Correções não podem deixar fechamento obsoleto; essa proteção e a fonte cambial escolhida são diferenças expressas em relação à referência.
6. Provar por oráculos sintéticos independentes, RED/GREEN, fluxo de UI real, ida/volta e falhas de storage, matriz de distribuições e full. Aprovação numérica/automatizada e aceite humano são estados separados.

Fontes lidas: AGENTS e README/CONTEXT-MAP/PROJECT-CONTEXT da base; contratos FX-PLANNING, PLANNING-MONTHLY, STATE-SCHEMA, armazenamento/recuperação/segurança; Harness externo em `2 - TRABALHO/99 - PROMPT/9 - SOFTWARE/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md`, caminho resolvido após mudança do acervo. Recebido pelo proprietário: plano e decisões de independência/câmbio, depois autorização da implementação e branch. ai-memory fornece skills, mas seus métodos de consulta não estão expostos nesta sessão; nenhuma consulta/escrita de wiki é alegada.

## Estado de execução

### Correção funcional solicitada pelo proprietário

Após a apresentação do build ff0f078f, o proprietário exigiu reprodução da dinâmica original: Comece aqui, perguntas e opções do formulário, revisão/liberação, Consolidado com todos os seletores e comparativos e Preenchimento mensal com seus botões/campos. O pedido autoriza esta correção na branch já autorizada. Substitui a escolha anterior de interface adaptada; não autoriza importar valores reais, alterar a planilha ou executar Git/publicação. Câmbio diário do site e preservação de dados/rascunhos permanecem. A análise abrange os dez arquivos finais Apps Script, incluindo o apêndice Horizonte, sem alegar acesso vivo ao projeto Apps Script ou execução autenticada que não ocorreram. Backup verificado do candidato anterior e RED da nova jornada estão no diretório ignorado `planning-parity-20261020`. O resultado anterior 88/88 não aprova o novo delta.

Preparação e baseline: PASS. Implementação, testes financeiros, browser, full, host e aceite humano: NOT_RUN neste registro inicial. Nenhuma evidência de execução antiga é reaproveitada como PASS atual.

Nota de execução: o builder lê `sw.js` como fonte do fingerprint e não o gera. Sua lista declarativa de precache é atualizada com os novos caminhos antes da reconstrução; build-id e portátil continuam gerados exclusivamente pelo builder. Classificação inicial de sw.js como artefato derivado foi corrigida por inspeção do gerador, sem ampliar o produto autorizado.


## Verificação final da correção — build d93561c064cf5f40

FULL91/91 PASS e inputs397/257/runner estáveis. Matriz24/24, valores longos8/8, palavras576/576, revisão independente R4 sem P1/P2 aberto no escopo; 17 casos puros permanentes e sete confrontos com funções originais. [Relatório](../validation/planning-20261020/parity/README.md). Sem alteração de AGENTS/skills/CI/norma/autoridade;213 protegidos e oito links preservados. AGENTIC IMPACT DETECTED: contratos e contexto afetados reconciliados apenas dentro da allowlist; seis regressões factuais acrescentadas, nenhuma memória global/wiki ou grafo externo alterado. Aprovação automática não é aceite humano/Google autenticado. Git/publicação não executados. Tentativa FULL inicial e falhas/harnesses mantidos com suas classificações originais.


## Verificação do pacote final — build 443c1a59f2c1f46d

FULL91/91 PASS em nova execução;327 inputs oficiais ordenados, inventário separado de397 caminhos de runtime/recursos,257 testes e runner estáveis. Matriz desta execução24/8/576. O FULLd935 permanece histórico; a deriva pós-FULL causada pela atualização dos documentos da raiz foi registrada, corrigida por freeze/reconstrução e seguida de novo FULL. Oráculos de referência:17 permanentes+7 confrontos originais, total24, com hash do motor preservado; revisões R4 e PACKAGE mantêm suas próprias atribuições. Os397 caminhos não substituem os327 inputs do fingerprint. README/CHANGELOG da raiz congelados antes da reconstrução; registros pós-gate somente fora dos327. [Relatório e deriva de ordem](../validation/planning-20261020/parity/README.md). Google autenticado, permissões/triggers, Safari, leitor de tela, toque físico, compreensão e aceite humano permanecem NOT_RUN. Fontes Apps Script analisadas e execução Google são provas distintas.
