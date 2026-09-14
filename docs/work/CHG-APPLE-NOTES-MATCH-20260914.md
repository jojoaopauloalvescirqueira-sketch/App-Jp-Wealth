# APPLE-NOTES-MATCH-01 — apresentação e preferências locais de Notas

## Brief anterior à escrita
Notas é um registro local de tarefas/observações, não um chat, nuvem ou fonte normativa. A seleção pasta → nota → editor, primeira linha como título e gravação explícita permanecem. Consumidores: launcher móvel, Configurações, busca/filtros, menus, inspector, exportação, save/retry/UNKNOWN, banners de recuperação, backup de S.mvpNotes e Finalizar Sessão. A captura Apple Notes é referência geométrica apenas; seu conteúdo pessoal não entra em fixtures/evidências. Núcleo AGENTS/CLAUDE, mapas e contratos vigentes confrontados com a fonte em 9ca32073; cabeçalhos históricos não são a revisão atual. Harness SHA256 c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8; X1 fonte fcc11d3eab563f3464e84e5b8886ddb9ee4784cff75530702f07776d19e0dff7. X2 fará revisão focal independente.

A autorização é o prompt /goal fornecido em 2026-09-14, incluindo branch e uma worktree. N2/A3: aparência em preferência auxiliar local com confirmação, sem schema financeiro nem mudança de formato do conteúdo. Autoridade Git limitada à branch/worktree já criadas. Preflight audit/edit PASS antes de escrita, árvore limpa, 316 inputs. Ancestry integrada e CI anterior conferidos; nenhum teste anterior aprova o novo delta.

```yaml
schema: jp-harness/chg/v1
change_id: CHG-APPLE-NOTES-MATCH-20260914
status: approved
objective: Redesenhar exclusivamente apresentação de Notas e suas preferências visuais reversíveis
risk_level: N2
authority_required: A3
target:
  root: /Users/joaopauloalves/.codex/apple-notes-match/20260914/product
  branch: codex/apple-notes-match-20260914
  baseline_sha: 9ca32073e1fa032318b7e6e6eb50b5f693efe2d9
scope:
  allowed_files:
    - index.html
    - src/styles/app.css
    - src/js/40-app/14-mvp-notes.js
    - src/js/40-app/09-settings-modal.js
    - src/js/40-app/07-finalize-session.js
    - src/js/manifest.json
    - tools/apple_notes_match_test.py
    - tools/mvp_notes_test.py
    - tools/notes_experience_test.py
    - build-id.js
    - dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html
    - docs/work/ACTIVE-TASK.md
    - docs/work/CHG-APPLE-NOTES-MATCH-20260914.md
    - docs/architecture/CODE-MAP.md
    - README.md
  forbidden_files: [AGENTS.md, CLAUDE.md, skills, .github, src/js/00-core/03-default-state.js, src/js/00-core/04-persistence.js]
  allowed_actions: [edit-scoped, synthetic-tests, official-build, independent-audit, freeze, recovery]
  forbidden_actions: [staging, commit, tag, push, PR, merge, deploy, reset, stash]
  regressions_forbidden: [financial-change, notes-content-change, autosave, draft-loss, width-reset-on-read, duplicate-editor, cloud]
derived_artifacts:
  allowed: [build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html]
  generation_commands: [python3 tools/rebuild_monolith.py]
  manual_edit: forbidden
external_side_effects:
  network: allowed
  allowed_targets: [loopback-synthetic-only]
  temporary_artifacts: allowed
  cleanup_required: false
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: forbidden
toolchain:
  dependency_changes: []
  allowed_processes: [existing-python, existing-chromium, existing-build-and-gates]
acceptance_criteria: [three-unequal-panes, contextual-toolbars, dominant-editor, preserved-widths-and-content, mobile-stages, reversible-visual-preferences, explicit-save-readback-retry, frozen-recovery]
approved_tests: [apple_notes_match_test, notes_experience_test, notes_launcher_test, studies_notes_persistence_contract_test, mvp_notes_test, settings_modal_test, finalize_session_test, quality_gate-full, build_reproducibility, service_worker_upgrade]
rollback:
  source: [verified-baseline-tar-and-manifest, own-delta-only]
  application_state: [isolated-synthetic-storage-only]
  data: [no-real-data-access]
  environment: [close-own-review-processes]
  verification: [hash-mode-input-comparison]
approved_by: owner-current-goal
approved_at: 2026-09-14
expires_on: [material-base-drift, unrelated-work, scope-expansion, financial-or-schema-change]
```

## Contrato de apresentação e compatibilidade
Referência aproximada 16,8/26,2/57% e toolbar 50–56px; três zonas por coluna, lista contínua, editor aberto, materiais distintos e SVGs originais. Sem botões de recursos inexistentes. Preservar ordem natural/criticidade e dados reais de data; não inventar agrupamento cronológico. As larguras válidas existentes prevalecem sobre a proporção estimada: drawer padrão canônico 980, pastas190, lista300, mínimo do editor320. Não regravar clamp nem mudar os defaults canônicos para estética.

Aparência em chave auxiliar jpwealth_notes_appearance_v1, separada de S e launcher: theme(app/light/dark), density(comfortable/compact), preview(show/hide), sidebar(show/hide desktop), reading(full/comfortable), text(standard/large/larger). Preview em RAM, Cancelar/sair retorna confirmado, Salvar sob lock existente com conferência raw/epoch/read-back; recusa mantém draft para retry, UNKNOWN/conflito bloqueiam até releitura explícita. Extensões de envelope compatível preservadas. Abrir/navegar não grava. Reset de aparência só prepara defaults para Salvar; restaurar larguras é comando separado pelo mvpNotesMutate existente, só três valores. Finalizar usa catálogo auxiliar existente para limpar só preferência auxiliar quando contrato existente manda; notas/pastas continuam preservadas. Sem infraestrutura de persistência compartilhada nova.

## CTX restrito
```yaml
schema: jp-harness/ctx/v1
context_change_id: CTX-APPLE-NOTES-MATCH-20260914
status: approved
root: /Users/joaopauloalves/.codex/apple-notes-match/20260914/product
mode: SEQUENCIAL
approved_branch: codex/apple-notes-match-20260914
create: [docs/work/CHG-APPLE-NOTES-MATCH-20260914.md]
modify: [docs/work/ACTIVE-TASK.md, docs/architecture/CODE-MAP.md, README.md]
merge: []
preserve: [historical-contracts, prior-evidence, main, stash, other-worktrees]
do_not_touch: [AGENTS.md, CLAUDE.md, skills, SESSION_HANDOFF.md, docs/governance/CURRENT-STATE.md, graph, indexes]
archive_requires_confirmation: []
source_of_truth:
  notes: src/js/40-app/14-mvp-notes.js
  settings: src/js/40-app/09-settings-modal.js
information_promotion:
  - from: inspected-and-tested-candidate
    to: scoped-Notes-descriptions
    reason: describe actual presentation and limits without anticipating acceptance
expiration_rules:
  - artifact: candidate-evidence
    event: affected-input-change
privacy_actions: [synthetic-only, no-copy-of-personal-reference-content]
acceptance_criteria: [Notes-only-descriptions, historical-records-preserved, no-human-acceptance-presumed]
approved_by: owner-current-goal
approved_at: 2026-09-14
expires_on: [material-scope-change, branch-or-root-change]
```

## Testes prévios, sequência e recuperação
Oráculos fixados antes do patch: mesma nota/rascunho/cursor/dados antes/depois de preview; zero escrita ao abrir/navegar/cancelar; save de aparência confirmado só por releitura, retry único após recusa, desfecho UNKNOWN bloqueado, raw inválido não normalizado; larguras legadas preservadas. Nova interface ausente na baseline deve ser BASELINE_FAIL, não regressão de domínio. Baseline executa focais funcionais existentes com fixtures nominais e snapshot Git sem dados ignorados.

Executar focais do delta primeiro (320/390/768/1024/1440, claro/escuro, longo/vazio/busca, teclado/foco, mobile, resize e tema local cruzado), Notes/save/retry e regressão próxima, depois FULL cumulativo e build/PWA existentes. Zoom nativo200% e reduced-motion examinados no Chromium disponível. Scripts de teste existentes só mudam caso expectativa de apresentação deliberadamente substituída tenha evidência, jamais para relaxar dado/segurança. Congelar revisão antes de auditoria funcional/visual/customização, preservar tentativas e refazer somente controles afetados em mudança. Recovery de todos inputs com hashes/modos. Evidências novas em ../evidence; baseline.tar/json preservam o anterior. Não reconstruir fonte histórica nem tratar aprovação visual do agente como aceite humano. Leitor de tela, outros browsers e dívidas A12/OPEN-05/V11/FCR/FEO/AUD-05/P2 ficam fora do lote.
