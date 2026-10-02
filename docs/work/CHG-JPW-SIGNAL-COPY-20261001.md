# CHG-JPW-SIGNAL-COPY-20261001

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-SIGNAL-COPY-20261001",
  "status": "approved",
  "objective": "JPW Signal Copy 1.14.0: preparar mensagem local de um item com conferencia, dados atuais e simulacao explicita da pendente selecionada",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/private/tmp/jpw-cockpit-ui-20260930",
    "branch": "codex/jpw-cockpit-ui-20260930",
    "baseline_sha": "deffc5061fe2eff3d83b6f6e742fa105ac9c5b06",
    "baseline_fingerprint": "3c3a961a4c40d9eee33d02acd86761a65eee1a1c1e7cac56bdfba6e243c06410"
  },
  "scope": {
    "allowed_files": [
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_SignalCopy_*.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_SignalCopy_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Actions.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Presentation.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Panel.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Version.mqh",
      "mt5/jpw-alavancagem-atual/README.md",
      "index.html",
      "downloads/jpw-alavancagem-atual/manifest.json",
      "tools/jpw_signal_copy_test.py",
      "tools/jpw_signal_copy_adapter_test.py",
      "tools/jpw_signal_copy_ui_test.py",
      "tools/leverage_details_event_test.py",
      "tools/leverage_package_test.py",
      "tools/leverage_page_test.py",
      "docs/work/CHG-JPW-SIGNAL-COPY-20261001.md",
      "docs/work/BRIEF-JPW-SIGNAL-COPY-20261001.md",
      "docs/governance/CURRENT-STATE.md",
      "docs/work/ACTIVE-TASK.md"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "mt5/jpw-alavancagem-atual/AGENTS.md",
      "docs/normative/**",
      "skills/**",
      "tools/quality_gate.py",
      "tools/leverage_suite.py",
      ".github/**",
      "src/js/**",
      "src/styles/**",
      "mt5/**/JPW_Alavancagem_Core.mqh",
      "mt5/**/JPW_Alavancagem_*Store*.mqh",
      "mt5/**/JPW_Alavancagem_Observer.mq5",
      "mt5/**/JPW_NoCuda_*.mqh"
    ],
    "allowed_actions": [
      "edit_scoped",
      "official_artifact_generation",
      "synthetic_tests",
      "independent_audit"
    ],
    "forbidden_actions": [
      "commit",
      "push",
      "merge",
      "deploy",
      "read_real_account",
      "operational_MT5_install",
      "trade",
      "send_group_message"
    ],
    "regressions_forbidden": [
      "stored financial schema or formula changed",
      "draw causes financial collection/write",
      "message logged or included in public package",
      "stale catalog or TP missing from digest",
      "duplicated live exposure",
      "silent N/A fallback",
      "unverified clipboard success"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "source_zip",
      "portable_html",
      "build_id",
      "offline_cache",
      "external_evidence"
    ],
    "generation_commands": [
      "python3 tools/build_leverage_package.py",
      "python3 tools/rebuild_monolith.py"
    ],
    "manual_edit": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "loopback synthetic tests",
      "official public docs"
    ],
    "temporary_artifacts": "allowed",
    "cleanup_required": true
  },
  "data": {
    "test_policy": "synthetic_only",
    "approved_real_data": [],
    "schema_change": "forbidden"
  },
  "toolchain": {
    "dependency_changes": [],
    "allowed_processes": [
      "Python",
      "host C++ shim",
      "existing Chromium/Playwright",
      "isolated MetaEditor only if usable"
    ]
  },
  "acceptance_criteria": [
    "coherent direct catalog with SL TP type times and remaining volume",
    "roles transient inferred or user confirmed; no successor promotion",
    "whole-account leverage, single pending frozen-price/equity scenario including netting",
    "selected-symbol RootN and mandatory metrics gate",
    "frozen preview revalidated before text or file",
    "copy native NOT_RUN blocked without exact-byte proof; no Copiado claim",
    "source-only package and separate raw full/focal/native evidence"
  ],
  "approved_tests": [
    "exact core synthetic replay",
    "adapter synthetic replay",
    "UI wiring and focus",
    "existing Cockpit host suite",
    "package/page focal",
    "unchanged full",
    "independent candidate audit"
  ],
  "rollback": {
    "source": [
      "restore only Signal Copy delta from baseline-v1130.tar.gz"
    ],
    "application_state": [
      "no existing preference migrations"
    ],
    "data": [
      "no financial records changed; explicit exported files remain user owned"
    ],
    "environment": [
      "terminate owned synthetic processes"
    ],
    "verification": [
      "check baseline hashes on protected files; preserve preexisting dirty changes"
    ]
  },
  "approved_by": "proprietario: PLEASE IMPLEMENT THIS PLAN: JPW Signal Copy 1.14.0",
  "approved_at": "2026-10-01",
  "expires_on": [
    "root or branch drift",
    "financial scope or schema expands",
    "material authority conflict"
  ]
}
```

## Test apparatus continuity

The existing details event replay needs synthetic definitions for the new dispatch hooks and live-item lookup type. Its financial/visual assertions and classification policy remain intact; additional assertions check Signal Copy launch and close. This is apparatus adaptation, not a gate relaxation. The in-progress failures remain in their original receipt.

## Current-state closure

CURRENT-STATE and ACTIVE-TASK may record this approved implementation and its exact validation limits. This is task evidence, not a revision to authority, routing, agents, gates or normative instructions. The module AGENTS.md is preserved; its older component map is reported separately in the impact assessment.
