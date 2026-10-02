# CHG-JPW-NOCUDA-CHANNELS-20260930 — indicador complementar

```yaml
schema: jp-harness/chg/v1
change_id: CHG-JPW-NOCUDA-CHANNELS-20260930
status: approved
objective: entregar JPW NoCuda Channels como indicador de desenho assistido e estudo versionado, separado do Cockpit financeiro
risk_level: N2
authority_required: A3
target:
  root: /private/tmp/jpw-cockpit-ui-20260930
  branch: codex/jpw-cockpit-ui-20260930
  baseline_sha: deffc5061fe2eff3d83b6f6e742fa105ac9c5b06
scope:
  allowed_files:
    - mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5
    - mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_*.mqh
    - mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_NoCuda_*_Tests.mq5
    - mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Version.mqh
    - mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5
    - mt5/jpw-alavancagem-atual/README.md
    - downloads/jpw-alavancagem-atual/manifest.json
    - index.html
    - src/styles/app.css
    - tools/jpw_nocuda_*_test.py
    - tools/leverage_page_test.py
    - tools/leverage_package_test.py
    - tools/leverage_panel_test.py
    - docs/work/CHG-JPW-NOCUDA-CHANNELS-20260930.md
    - docs/work/BRIEF-JPW-NOCUDA-CHANNELS-20260930.md
    - docs/architecture/JPW-NOCUDA-CHANNELS.md
  forbidden_files:
    - AGENTS.md
    - mt5/jpw-alavancagem-atual/AGENTS.md
    - docs/normative/**
    - docs/governance/**
    - downloads/nocuda/Nocuda_Tool.mq5
    - mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_*_Store.mqh
  allowed_actions: [edit_scoped, generate_official_artifacts, test_synthetic, audit_independently]
  forbidden_actions: [commit, push, merge, deploy, install_operational_mt5, trade, use_real_account]
  regressions_forbidden: [change_existing_financial_formulas, mutate_financial_records, silently_migrate_old_channels, present_channel_as_trade_signal]
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
  allowed_processes: [python3, C_plus_plus_host_test, MetaEditor_in_isolated_MT5_only]
acceptance_criteria:
  - assisted A/B/C selection snaps to completed source-candle Close and drafts never replace a confirmed revision
  - signed 65-level bar-index geometry gives article M and G results; source timeframe remains fixed when chart timeframe changes
  - SQLite stores separate immutable revisions with checksum, generation conflict refusal and corrupt/incompatible fail closed
  - UI has stable NoCuda button and Desenho, Medidas, Registro without blocking Cockpit; render/zoom/ticks never persist a financial or study revision, and explicit view choices only update chart-local preference
  - source package and site explain independent attachment and exact limitations; no unproven compiled artifact
approved_tests: [focused_geometry, focused_store, focused_site, package_integrity, cockpit_regressions, quality_gate_full_raw, independent_audit, native_isolated_if_available]
rollback:
  source: [restore preserved baseline archive and preexisting diff outside repository]
  application_state: [remove only new NoCuda chart objects on indicator removal; leave existing Cockpit objects and financial records untouched]
  data: [do not delete user studies automatically; old NoCuda_Tool drawings untouched]
  environment: [no operational installation]
  verification: [compare baseline source hashes and original archive]
approved_by: Proprietario via PLEASE IMPLEMENT THIS PLAN JPW NoCuda Channels
approved_at: 2026-09-30
expires_on:
  - target root or branch changes
  - objective, risk or scope changes materially
  - baseline drifts materially beyond recorded 20 preexisting changes
  - new higher-authority conflict appears
```

Baseline: `/Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-nocuda-channels-20260930/baseline/BASELINE.json`. At capture, 48/48 source files matched the 1.10.2 manifest. The 20 dirty paths were preserved in the archive and patch; they are preexisting 1.10.2 work, not evidence of integration or native approval. The stale source revision warning in preflight refers to general project context and is not interpreted as a fresh product gate.

The existing Cockpit indicator is in scope for `#property version` alignment only. Its financial formulas, state schemas, and observer behavior are unchanged; the shared product-version header also labels new producer metadata and presence namespaces when recompiled from this candidate.

The Cockpit panel regression's prior literal `1.10.2` assertion is updated to verify the property references the central MQL version and that the product version matches the manifest. This maintains the identity gate for the new package; it does not weaken a financial or UI assertion.

Sources: article SHA-256 `274a8921796eb9824816db9a21dd6be9299f68ae166b0b06c6346ef332fd6168`; external Harness at its current `2 - TRABALHO/99A -   SOFTWARE DEV/99 - PROMPTS SOFTWARE DEV/` path, SHA-256 `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`. The article informs geometry, not market efficacy. The 0.125 mesh and −4…+4 bounds are owner-selected conventions. No native validation is inherited.
