# CHG-JPW-COCKPIT-STOP-RISK-20260929 — produto 1.9.0

```yaml
schema: jp-harness/chg/v1
change_id: CHG-JPW-COCKPIT-STOP-RISK-20260929
status: approved
objective: mostrar o risco informativo dos stops por operacao no indicador e em tabela auditavel no cockpit
risk_level: N3
authority_required: A4
target:
  root: /private/tmp/jpw-alavancagem-atual-20260926
  branch: codex/jpw-alavancagem-atual-20260926
  baseline_sha: f5145b25e86af6b4ccbfef847cba0d84d74e7c8a
scope:
  allowed_files:
    - mt5/jpw-alavancagem-atual/MQL5/**
    - mt5/jpw-alavancagem-atual/README.md
    - downloads/jpw-alavancagem-atual/**
    - index.html
    - src/js/20-ui/31-tools-services.js
    - src/js/40-app/01-navigation.js
    - src/js/manifest.json
    - src/styles/app.css
    - build-id.js
    - sw.js
    - dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html
    - tools/build_leverage_package.py
    - tools/leverage_*_test.py
    - docs/work/ACTIVE-TASK.md
    - docs/work/BRIEF-JPW-COCKPIT-STOP-RISK-20260929.md
    - docs/work/CHG-JPW-COCKPIT-STOP-RISK-20260929.md
  forbidden_files:
    - mt5/jpw-alavancagem-atual/AGENTS.md
    - AGENTS.md
    - docs/normative/**
    - docs/governance/**
  allowed_actions: [edit_scoped, generate_official_artifacts, test_synthetic, audit_independently]
  forbidden_actions: [commit, push, merge, deploy, install_operational_mt5, trade, use_real_account]
  regressions_forbidden: [change_existing_financial_formulas, mutate_mdd_genesis_usc_raizn_records, display_partial_as_total, equate_balance_pct_to_statutory_reference]
derived_artifacts:
  allowed: [source_zip, portable_html, offline_cache, validation_receipts]
  generation_commands: [python3 tools/build_leverage_package.py, python3 tools/rebuild_monolith.py]
  manual_edit: forbidden
external_side_effects:
  network: forbidden
  allowed_targets: []
  temporary_artifacts: allowed
  cleanup_required: false
data:
  test_policy: synthetic_only
  approved_real_data: []
  schema_change: approved
toolchain:
  dependency_changes: []
  allowed_processes: [python3, MetaEditor_in_isolated_MT5_only]
acceptance_criteria:
  - hedging risk from execution price to valid current SL with floor zero on remaining volume
  - pending enlarging orders reserved separately; missing or unsupported input makes consolidated value unavailable
  - current balance percentage explicitly informational and account currency consistent including USC
  - exact symbol and side operation selection; chronology inferred rather than certified thesis or Genesis
  - netting operation total unavailable; no invented per-order attribution
  - indicator reads validated EA sample only; stale or mismatched sample is N/A on chart
  - six-metric preference migration and Stops tab preserve five existing metrics
approved_tests: [focused_mql_core_and_store, focused_cockpit_and_site, package_integrity, quality_gate_full_raw, independent_product_audit, native_isolated_if_available]
rollback:
  source: [restore_preserved_r14_snapshot]
  application_state: [leave_existing_mdd_genesis_usc_raizn_records_untouched]
  data: [do_not_delete_user_records]
  environment: [no_operational_install]
  verification: [compare_r14_hashes_and_validate_manifest]
approved_by: Proprietario; pedido PLEASE IMPLEMENT THIS PLAN para JPW Cockpit 1.9.0
approved_at: 2026-09-29
expires_on:
  - root_or_branch_change
  - material_scope_or_authority_change
  - material_baseline_drift
  - new_higher_authority_conflict
```

## Base, autoridade e limite

Candidate 1.8.0/r14 preservado externamente: 83/83 hashes conferidos antes da escrita; fingerprint `37c3da2485d100601039dfd36a364c1c28dbf0e2212ac6878538201a7b0dd977`. O full anterior é histórico, `49 PASS / 8 PRODUCT_FAIL`; validação nativa `NOT_RUN`. A árvore suja é o r14 esperado. O preflight audit passou; edit bloqueou genericamente pela árvore com 42 alterações, reconciliada com o snapshot, sem limpeza ou reset.

Fontes: Estatuto V11 `docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf` SHA-256 `2dab6166bb8513cd9beb7fe39c574971af086ebae66683d99c0e6fac69eb6769`, Arts. 4.2–4.3 e 8.4 §§1º–2º, 9º e 15–17; Anexo `docs/normative/ANEXO_PARAMETRICO_CANONICO.md` SHA-256 `6240b6330a35fd488f16d4191129eeb01aff8f7a4707158c043afb37d91cdc23`, D-01/D-08 e P-07/P-19 pendentes. Harness externo encontrado no caminho atual `2 - TRABALHO/99A -   SOFTWARE DEV/99 - PROMPTS SOFTWARE DEV/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md`, SHA-256 `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`.

O valor no gráfico é apenas a soma do risco das posições abertas e da reserva das pendentes ampliadoras atribuídas. `OrderCalcProfit` no EA calcula a perda hipotética em moeda da conta. O percentual usa `ACCOUNT_BALANCE` atual como solicitado e será rotulado informativo; o risco estatutário usa Saldo Inicial de Referência e a alavancagem estatutária do Art. 4.5 §8 usa a menor base entre esse saldo e o equity corrente. Risco Comprometido também considera outras parcelas e não é calculado por esta linha. Gaps, deslizamento, custos e perdas realizadas ficam fora. O terminal não prova mesma tese nem a flag GÊNESE; idade só ordena linhas inferidas. P-07/P-19 não autorizam contagem fixa ou Defesa.

Produto corrigido congelado em `outputs/jpw-cockpit-v190-20260929/product-r2/PRODUCT_FREEZE.json`, fingerprint SHA-256 `4331914a5594134afac8ce8641e75cd4a05622180ce92e6d437adb7043f0ed6c` (45 arquivos). O r1 anterior foi preservado e supersedido após auditoria identificar reuso indevido de Gênese encerrada, leitura `Current` congelada, controles órfãos, lease de sessão insuficiente e filtro de schema SQLite ambíguo. O r2 mantém `N/A` para atribuição não comprovada e limita a cadência completa a 30 s e a checagem Stop risk a 5 s, ainda sujeitos ao despacho real do terminal.

O acréscimo documental de cadência em `index.html` e `README.md`, sem mudança nos outros 43 arquivos, foi congelado em `outputs/jpw-cockpit-v190-20260929/product-r3/PRODUCT_FREEZE.json`, fingerprint SHA-256 `ae48fd5eb46d79f13b9c7247fc805090687cf1fe86462c8242479a78cab99912`. O parecer técnico sobre os bytes MQL do r2 continua aplicável; o pacote final e o gate têm recibos próprios.

## Sequência de separação

Congelar e auditar o delta de produto antes da edição do guia local para IAs. O guia tem CHG separado `CHG-JPW-COCKPIT-STOP-RISK-AI-GUIDE-20260929`. Após a inclusão do guia, regenerar o ZIP e congelar candidate final. Gate N3/A4, auditoria independente, validação nativa e aceite humano permanecem separados; este CHG não se autopromove.
