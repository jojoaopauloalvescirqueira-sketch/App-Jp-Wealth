# CHG-JPW-COCKPIT-STOP-RISK-AI-GUIDE-20260929 — guia local para IAs

```yaml
schema: jp-harness/chg/v1
change_id: CHG-JPW-COCKPIT-STOP-RISK-AI-GUIDE-20260929
status: approved
objective: atualizar o guia local subordinado para manutencao e auditoria do risco dos stops
risk_level: N3
authority_required: A4
target:
  root: /private/tmp/jpw-alavancagem-atual-20260926
  branch: codex/jpw-alavancagem-atual-20260926
  baseline_sha: f5145b25e86af6b4ccbfef847cba0d84d74e7c8a
scope:
  allowed_files:
    - mt5/jpw-alavancagem-atual/AGENTS.md
    - docs/work/CHG-JPW-COCKPIT-STOP-RISK-AI-GUIDE-20260929.md
    - docs/work/ACTIVE-TASK.md
    - downloads/jpw-alavancagem-atual/manifest.json
    - downloads/jpw-alavancagem-atual/JPW_Alavancagem_Atual_Fontes_v1.9.0.zip
  forbidden_files: [AGENTS.md, docs/normative/**, docs/governance/**, external_canonical_harness]
  allowed_actions: [edit_local_guide_after_product_freeze, regenerate_source_zip, focused_structural_test, independent_guide_audit]
  forbidden_actions: [commit, push, merge, deploy, install_operational_mt5, trade]
  regressions_forbidden: [guide_self_authorization, reclassify_product_fail, change_financial_rules, grant_statutory_homologation]
derived_artifacts:
  allowed: [source_zip, validation_receipts]
  generation_commands: [python3 tools/build_leverage_package.py]
  manual_edit: forbidden
external_side_effects:
  network: forbidden
  allowed_targets: []
  temporary_artifacts: allowed
  cleanup_required: false
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: forbidden
toolchain:
  dependency_changes: []
  allowed_processes: [python3]
acceptance_criteria:
  - guide_subordinate_to_root_instructions_statute_and_external_harness
  - map_sources_units_states_identity_hedging_netting_pending_and_failure_modes
  - map_validation_rollback_and_source_site_manifest_zip_coherence
  - no_claim_of_p21_homologation_or_mt5_certified_thesis
approved_tests: [structural_guide_check, zip_hash_coherence, independent_control_plane_audit]
rollback:
  source: [restore_verified_r14_guide_manifest_and_zip_then_regenerate_derived_artifacts]
  application_state: [none]
  data: [none]
  environment: [none]
  verification: [compare_product_freeze_and_final_guide_delta]
approved_by: Proprietario; pedido PLEASE IMPLEMENT THIS PLAN para JPW Cockpit 1.9.0
approved_at: 2026-09-29
expires_on: [material_scope_change, authority_conflict, baseline_drift]
```

Este CHG não cobre a implementação do cálculo ou da UI, descrita no CHG de produto. A escrita de `mt5/jpw-alavancagem-atual/AGENTS.md` ocorre somente depois do congelamento do delta de produto; o guia é avaliado como control plane N3/A4 próprio. A presença do guia no ZIP não o transforma em instrução do terminal nem em autorização para alterar dados reais, política ou mecanismos de auditoria.

O primeiro produto foi congelado antes da escrita deste guia em `outputs/jpw-cockpit-v190-20260929/product-r1/PRODUCT_FREEZE.json`, fingerprint SHA-256 `962a757abb625b44dc3f4ccc4a9beabf641129f99625e721623252f6011b1627` (45 arquivos). A auditoria independente encontrou defeitos no produto; o r1 foi supersedido pelo congelamento corrigido `outputs/jpw-cockpit-v190-20260929/product-r2/PRODUCT_FREEZE.json`, fingerprint SHA-256 `4331914a5594134afac8ce8641e75cd4a05622180ce92e6d437adb7043f0ed6c` (45 arquivos). O guia foi reconciliado depois do r2, sem integrar regras financeiras novas.

O rollback do guia toma como base verificável `outputs/jpw-cockpit-v180-20260929/final-r14/candidate/`: `AGENTS.md` SHA-256 `3d632eafb7ac85076f19e3e3a787e4a4184eb76eeb72adfc02e5019fcf6fd558`, manifesto SHA-256 `0f4fd1905b0cdd531425e31459d787ed7643704379dfd07b20174caf11276ce8` e ZIP v1.8.0 SHA-256 `2c0e608ed04ce98722ed58bbf087b42437cc89085561e7d9935bdc1eb554cea1`. O guia já existia nessa base: restaure-o, não o remova. Regere derivados pelos geradores oficiais e confira os hashes.

Após a edição do guia, a documentação de cadência foi esclarecida em `index.html` e `README.md`. Esse delta documental foi congelado como product-r3, fingerprint `ae48fd5eb46d79f13b9c7247fc805090687cf1fe86462c8242479a78cab99912`; os 43 arquivos restantes do product-r2, inclusive todos os MQL, permaneceram idênticos.
