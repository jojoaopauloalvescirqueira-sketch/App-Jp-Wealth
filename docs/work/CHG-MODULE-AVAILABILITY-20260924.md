# CHG-MODULE-AVAILABILITY-20260924

```yaml
schema: jp-harness/chg/v1
change_id: CHG-MODULE-AVAILABILITY-20260924
status: approved
objective: Disponibilidade reversível por módulo, Alladin congelado por padrão, dados preservados e gestão única no Editor.
risk_level: N2
authority_required: A3
target:
  root: /Users/joaopauloalves/.codex/module-availability/20260924/product
  branch: codex/module-availability-20260924
  baseline_sha: ad5c23e7884be108ceaf35acd26fb1c3b28b57db
scope:
  allowed_files:
    - src/js/00-core/08-module-availability.js
    - src/js/00-core/07-workspace-backup.js
    - src/js/20-ui/32-module-availability.js
    - src/js/20-ui/33-module-work.js
    - src/js/20-ui/12-nav-style.js
    - src/js/20-ui/13-exec-views.js
    - src/js/20-ui/14-nocoda-studies.js
    - src/js/20-ui/15-pivot-studies.js
    - src/js/20-ui/18-finpes-budget.js
    - src/js/20-ui/19-finpes-debts.js
    - src/js/20-ui/21-finpes-scenarios.js
    - src/js/20-ui/23-research-views.js
    - src/js/20-ui/24-alladin-views.js
    - src/js/20-ui/25-dash-macro.js
    - src/js/20-ui/28-fx-consolidated.js
    - src/js/20-ui/30-execution-board.js
    - src/js/20-ui/31-forex-accounts.js
    - src/js/30-accounting/01-daily-ledger.js
    - src/js/40-app/01-navigation.js
    - src/js/40-app/04-onboarding.js
    - src/js/40-app/06-boot.js
    - src/js/40-app/07-finalize-session.js
    - src/js/40-app/09-settings-modal.js
    - src/js/40-app/11-operational-shell.js
    - src/js/40-app/18-notification-center.js
    - index.html
    - src/styles/app.css
    - src/js/manifest.json
    - sw.js
    - tools/module_availability_test.py
    - tools/module_availability_core_test.py
    - tools/module_availability_backup_test.py
    - tools/module_availability_work_test.py
    - tools/*navigation*test.py
    - tools/alladin*test.py
    - tools/dashboard_macro_test.py
    - tools/contextual_sidebar_test.py
    - tools/header_focus_return_test.py
    - tools/notification_center_test.py
    - tools/complete_backup_test.py
    - tools/smoke_test.py
    - tools/galton_board_test.py
    - tools/fx_planning_test.py
    - tools/exec_submenu_test.py
    - docs/work/CHG-MODULE-AVAILABILITY-20260924.md
    - docs/work/ACTIVE-TASK.md
    - docs/decisions/2026-09-24-alladin-congelado.md
    - docs/architecture/MODULE-AVAILABILITY.md
    - docs/architecture/NAVIGATION-HIERARCHY.md
    - docs/architecture/COMPLETE-BACKUP.md
    - docs/architecture/ALLADIN.md
    - docs/governance/CURRENT-STATE.md
  forbidden_files: [AGENTS.md, CLAUDE.md, skills, docs/normative, .github, tools/quality_gate.py, tools/test_infra, tools/serve.py, tools/launch_local.py, src/js/10-domain]
  allowed_actions: [isolated_worktree, bounded_edit, synthetic_tests, local_review_server, independent_audit]
  forbidden_actions: [commit, push, PR, merge, deploy, real_data_access, dependency_install, infrastructure_change]
  regressions_forbidden: [lost_draft, financial_write_by_freeze, ledger_change, altered_consolidated_values, script_removal_or_reorder, implicit_context_switch, preference_normalization]
derived_artifacts:
  allowed: [build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html, src/vendor/pdfjs/runtime-assets.js]
  generation_commands: [python3 tools/rebuild_monolith.py]
  manual_edit: forbidden
external_side_effects:
  network: allowed
  allowed_targets: [git_remote_read_only, loopback_synthetic_tests_and_review]
  temporary_artifacts: allowed
  cleanup_required: true
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: approved_optional_workspace_preference_only
toolchain:
  dependency_changes: []
  allowed_processes: [python3, node, existing_browser, existing_local_server]
acceptance_criteria:
  - Alladin frozen default, absent operationally in four layouts, administrable and reversible.
  - Shared policy before navigation and notification context effects; six order IDs preserved.
  - Freeze refuses local pending work; remote freeze suspends and preserves work and ongoing confirmations.
  - Explicit confirmed writes only; invalid/future storage retained; conflicts and unknown results visible.
  - Complete backup preserves financial data, supports old/partial/null and explicit corrupted-preference recovery.
  - Active modules, shared summaries, session lifecycle, focus and support surfaces preserved.
approved_tests:
  - module availability core/browser/work/backup synthetic focals, four layouts/themes/mobile
  - navigation layout/order/IA/local, notifications, Settings and focus regression
  - Alladin internal fixtures explicitly active; preservation and summaries remain tested frozen
  - complete backup/recovery/session/active-module focals
  - quality_gate.py --tier full; validate_project.py; reproducibility; PWA offline
rollback:
  source: [external baseline.json and scoped candidate diff]
  application_state: [explicit unfreeze; older code ignores availability and may reject new backup key]
  data: [keep old and new synthetic backups, never delete preference to open older build]
  environment: [stop only task-owned test processes]
  verification: [baseline reads unchanged data, current roundtrip, exact hashes]
approved_by: user explicit attachment c6cedacc-8a51-4f3c-a9d1-20e5399b56ff
approved_at: 2026-09-24
expires_on: [material_target_drift, scope_expansion, higher_authority_required]
```

## Brief de compreensão / fontes
JP Wealth é um aplicativo financeiro local; esta entrega governa disponibilidade da apresentação, não autenticidade, elegibilidade financeira ou qualidade de módulos. Navegação compartilha nós nos quatro layouts; Editor é conteúdo movido para a Central de Configurações, sem clone. O catálogo de seis IDs permanece íntegro. Alladin possui domínio e leitores usados por Dashboard/Notificações; seus scripts não podem ser removidos. Seu modal guarda trabalho em RAM e não tem guarda geral; closing/reset não serve como congelamento. A preferência será auxiliar, fora de S, pela allowlist do workspace; dados e cálculos permanecem integralmente no domínio atual.

Base/relativa leitura: todos os fontes citados pertencem a ad5c23e e seus hashes estão em ../evidence/baseline.json. AGENTS/README/CONTEXT-MAP/PROJECT-CONTEXT/CURRENT-STATE; NAVIGATION-HIERARCHY, COMPLETE-BACKUP, STATE-SCHEMA, DB-STORAGE-GOVERNANCE, DATA-RECOVERY e SECURITY-MODEL; inspeção dos consumidores no plano. Harness real (caminho movido, sem alterar fonte): /Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/3 - SOFTWARE & EAS/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md; SHA256 c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8, §§12–14,36–48. Preflight audit/edit PASS; aviso histórico de frescor não reinterpretado como autorização ou falha de produto.

## Testes definidos antes da implementação
Default sem escrita; fixtures active/frozen por quatro IDs; unknown IDs/enums/future version; leitura/Quota/recusa silenciosa/unknown/conflito; cancel e local pending; cross-tab e confirmação já iniciada; zero mudança financeira por disponibilidade; nós e ordem preservados; atalhos antes de efeitos; Editor único; draft providers; backup antigo/null/invalid/recovery/raw text; partial resume; rollback com arquivos antigo/novo preservados; ciclo ativo/congelado sem listeners duplicados; mobile/desktop quatro layouts e claro/escuro, foco/teclado. Focais novos antes do full; nenhuma expectativa válida removida. Evidências fora do produto.

## Impacto agêntico delimitado
Mudança material de produto e registro de decisão já aprovada: contrato MODULE-AVAILABILITY e ADR novos; NAVIGATION-HIERARCHY/COMPLETE-BACKUP/ALLADIN/CURRENT-STATE/ACTIVE-TASK afetados com ação local focal. Fontes de autoridade, skills, routers de agentes e gates são consumidores das referências existentes, sem alteração local; histórico preservado. Índice/grafo não atualizado (fora do escopo); leitura direta dos arquivos é a fonte de trabalho. Não declarar integração ou aceite.

## Refinamento r2 decorrente da auditoria
A inspeção independente identificou os acionadores compartilhados fxOpenChecklist (20-ui/13) e openOnboardingModal (40-app/04), e o grid paramsWidgetGrid transportado para Settings. O alcance aprovado de proteção de acessos alternativos cobre seus guards de apresentação antes de qualquer montagem/efeito; não modifica o conteúdo, submissão financeira ou bootstrap. Os dois arquivos adicionais recebem somente a verificação de disponibilidade na entrada. O adaptador 33 passa a reconhecer o grid estável e o modal legado aberto.

O full r1 é preservado integralmente: 49 PASS / 8 PRODUCT_FAIL. Quatro falhas demonstradas exigiam Alladin ativo sem declará-lo nas fixtures (smoke/Galton/Planning/Exec Submenu); suas asserções permanecem e as fixtures ficam explicitamente ativas. A suspeita estática de credencial era o termo inglês em um comentário novo do controlador; a mesma afirmação foi escrita em português, sem alterar o teste nem seu detector. Três falhas de inicialização ($, renderOnboardingIncompleteBanner e dependências ausentes) continuam indeterminadas e não são convertidas em PASS. Não se modifica aparato ou gate.
