# Consolidado FX — contrato e brief de implementação

```yaml
schema: jp-harness/chg/v1
change_id: CHG-FOREX-CONSOLIDATED-20260914
status: approved
objective: Consolidado FX local, MT5 e Manual separados, importação rastreável e histórico longitudinal.
risk_level: N3
authority_required: A4
target:
  root: /Users/joaopauloalves/.codex/forex-consolidated/20260914/product
  branch: codex/forex-consolidated-20260914
  baseline_sha: 01c08241ccb7bc229a05779a52f577ee55a69ae7
scope:
  allowed_files:
    - src/js/10-domain/17-fx-consolidated-model.js
    - src/js/40-app/24-fx-consolidated-import.js
    - src/js/40-app/25-fx-consolidated-pdf.js
    - src/js/20-ui/28-fx-consolidated.js
    - src/js/00-core/03-default-state.js
    - src/js/00-core/04-persistence.js
    - src/js/30-accounting/01-daily-ledger.js
    - src/js/40-app/07-finalize-session.js
    - src/js/40-app/01-navigation.js
    - src/js/40-app/09-settings-modal.js
    - src/js/20-ui/03-main-render.js
    - src/js/manifest.json
    - index.html
    - src/styles/app.css
    - sw.js
    - build-id.js
    - dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html
    - tools/fx_consolidated_model_test.py
    - tools/fx_consolidated_storage_test.py
    - tools/fx_consolidated_ui_test.py
    - tools/fx_consolidated_pdf_test.py
    - tools/fixtures/mt5-consolidated/
    - tools/navigation_ia_test.py
    - tools/navigation_local_contract_test.py
    - tools/contextual_sidebar_test.py
    - tools/finalize_session_test.py
    - tools/alladin_finalize_preservation_test.py
    - tools/finpes_finalize_preservation_test.py
    - tools/settings_modal_test.py
    - tools/fx_planning_test.py
    - tools/exec_submenu_test.py
    - tools/nocoda_test.py
    - docs/architecture/FOREX-CONSOLIDATED.md
    - docs/architecture/STATE-SCHEMA.md
    - docs/work/CHG-FOREX-CONSOLIDATED-20260914.md
    - docs/work/CHG-FOREX-CONSOLIDATED-PDF-BUILD-20260914.md
  forbidden_files: [AGENTS.md, CLAUDE.md, skills/, docs/normative/, .github/, docs/governance/, SESSION_HANDOFF.md, docs/work/ACTIVE-TASK.md]
  allowed_actions: [isolated_implementation, synthetic_tests, official_build, audit, freeze, recovery, local_review_server]
  forbidden_actions: [commit, tag, push, PR, merge, deploy, reset, stash, clean]
derived_artifacts:
  allowed: [build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html]
  generation_commands: [python3 tools/rebuild_monolith.py]
  manual_edit: forbidden
external_side_effects:
  network: allowed
  allowed_targets: [official_MetaQuotes_documentation, official_PDFjs_distribution, localhost_validation]
  temporary_artifacts: allowed
  cleanup_required: false
data:
  test_policy: synthetic_only
  approved_real_data: [read_only_user_supplied_MT5_summary_PDF_no_copy_no_upload]
  schema_change: approved
toolchain:
  dependency_changes: [local_PDFjs_only_separate_build_contract]
  allowed_processes: [existing_Python_Node_Chromium_Git_read_only_and_authorized_isolation]
acceptance_criteria:
  - MT5 and Manual never merge implicitly; account filter never selects operational account.
  - Import identity checked; repeat is idempotent; conflicts require explicit revision.
  - Missing facts never become zero or present-day historical context.
  - Both histories and account identity survive Finalizar Sessao; explicit wipe remains effective.
  - Local parsing has no external requests; original files are not stored.
  - Four MQL5-inspired tabs, themes, responsive layout and keyboard support.
approved_tests: [new_focal_model_storage_pdf_ui, existing_affected_regressions, full, reproducibility, PWA, portable, independent_audit]
rollback:
  source: [../evidence/baseline.tar, ../evidence/baseline.json, own_delta_only]
  application_state: [isolated_synthetic_profiles_only]
  data: [existing_backup_restore_protocol]
  environment: [preserve_other_worktrees_stash_and_original_candidate]
  verification: [hashes_modes_and_protected_before_receipt]
approved_by: owner_conversation
approved_at: 2026-09-14
expires_on: [material_base_drift, material_scope_expansion, conflicting_work, new_external_effect]
```

## Autoridade recebida e compreensão

O proprietário solicitou “PLEASE IMPLEMENT THIS PLAN” e depois autorizou nominalmente a branch/worktree acima. O plano aprovado inclui PDF.js local, extensão delimitada do empacotamento/validadores e preservação dos dois históricos ao Finalizar Sessão. Não inclui publicação. O contrato registra essa decisão; não concede autoridade nova.

O JP Wealth é um registro financeiro local com controle normativo Forex separado da UI. Este lote acrescenta análise descritiva por conta e origem, sem ativar parâmetros ou homologar V11. As fontes de comportamento foram examinadas em BASE_SHA: `00-forex-state.js` (conta operacional e fatos), `11-operation-lifecycle.js`/`16-operation-history.js` (snapshots confirmados), `04-persistence.js`/`01-daily-ledger.js` (escritor, backup, recusa/UNKNOWN), `07-finalize-session.js` (limpeza hoje inclui histórico e contas), `01-navigation.js` e `09-settings-modal.js` (destinos e preferências). Mapa/README/contratos pertinentes são referências, não prova de atualidade automática.

Harness efetivamente localizado: `A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md`, SHA-256 `c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8`, §§12–15, 24, 28–30, 36–48. A hierarquia Constituição → V11 → Anexo delegado → política/motor → UI permanece; estatística descritiva não altera fase, clearance, reservas ou Lucro Técnico normativo.

O risco N3 cobre integridade das estatísticas e a trilha separada de control plane; persistência/importação são N2. Provas: exemplos sintéticos pré-fixados, memória/disco/log em recusa e UNKNOWN, identidade e dedupe, ida/volta de backup, lifecycle, UI, FULL e revisão independente. Se HTML real detalhado continuar ausente, a homologação do parser para o exportador do proprietário permanece limitada; fixtures sintéticas não serão apresentadas como relatório real.

## CTX delimitado

`CTX-FOREX-CONSOLIDATED-20260914`: este brief, o contrato de build, `docs/architecture/FOREX-CONSOLIDATED.md` e duas entradas diretamente afetadas de `docs/architecture/STATE-SCHEMA.md` (novo agregado e preservação de operationHistory). O plano aprovado cobre documentação técnica diretamente afetada; esta delimitação não amplia produto ou autoridade. Não atualizar instruções, fontes gerais, histórico de outras campanhas ou grafo. AGENTIC IMPACT: o novo destino e a fronteira analítica serão documentados na arquitetura diretamente afetada; o aviso de frescor do contexto geral permanece registrado.

## Delegação e freeze

Autoria separada: modelo/parser HTML; armazenamento/lifecycle; PDF/build; UI/navegação/coordenação. Interfaces serão registradas na arquitetura antes de consumo. O coordenador é o único editor de manifest, index e derivados. Evidências ficam em `../evidence/`, fora do candidate. Baseline recuperável já capturada antes da primeira edição. Suítes novas ainda não executadas; esta aprovação não é aprovação técnica nem aceite humano do resultado.

## Revisão de validação V2

O FULL V1 preservado detectou listas fechadas de navegação/Settings anteriores
ao novo destino. A atualização acrescenta apenas Consolidado FX e o grupo Forex
nos oráculos existentes, preservando cálculos, geometria, fluxos e demais asserts.
A revisão também fecha a interpretação de operationHistory com versão futura
na UI (permanece opaco), e transporta licença/proveniência no portátil como
recursos declarados. O arquivo V1 e os achados da auditoria ficam preservados
nas evidências; V2 recebe novos build/fingerprint e validação própria.

## Revisão de validação V3 — fixture NoCoda

A regressão obrigatória expôs uma lacuna do ambiente do teste legado: após
recarga, a interceptação genérica de página não controlava o worker e foram
observadas cotações fora das fixtures. O FULL anterior permanece 54 PASS e
1 PRODUCT_FAIL; sua asserção não capturou quais campos mudaram, e a observação
posterior não reproduziu a falha. Não se atribui retroativamente sua causa.

O plano aprovado inclui regressões pertinentes e avaliação sintética controlada.
Este complemento delimita exclusivamente `tools/nocoda_test.py`: reutilizar
`browser_bootstrap_fixture`, aguardar bootstrap em goto/reload, bloquear SW
somente neste teste que não depende dele e verificar requisições desconhecidas.
As 64 asserções e a função que exige imutabilidade operacional permanecem
idênticas. Produto NoCoda, modelos, fontes de dados e gate não são alterados.
A proposta passou na base e no produto antes da incorporação, com perfil
loopback-only existente e inalterado, sem novas dependências ou permissões.

O novo FULL usa essa mesma barreira processual; testes próprios de PWA preservam
seu worker. Os registros anteriores e o pacote 1eb4adc2... continuam preservados.
Esta revisão altera apenas teste e contrato, recebe novo fingerprint e conserva
o build a6fcc188be49e7b2. Evidências: `validation-v3-scope.json`,
`nocoda-fixture-proposed.diff`, `nocoda-safe-candidate.json`,
`nocoda-safe-baseline.json` e revisão independente dos oráculos nas evidências
externas. Não é aceite humano nem autorização para integração.
