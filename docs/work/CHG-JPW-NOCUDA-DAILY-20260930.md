# CHG-JPW-NOCUDA-DAILY-20260930

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-NOCUDA-DAILY-20260930",
  "status": "approved",
  "objective": "JPW NoCuda 1.12.0: desenho sequencial pelo Close, seleção de níveis e projeção diária H1 em horário do servidor",
  "risk_level": "N1",
  "authority_required": "A2",
  "target": {
    "root": "/private/tmp/jpw-cockpit-ui-20260930",
    "branch": "codex/jpw-cockpit-ui-20260930",
    "baseline_sha": "deffc5061fe2eff3d83b6f6e742fa105ac9c5b06"
  },
  "scope": {
    "allowed_files": [
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_*.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_NoCuda_*_Tests.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Version.mqh",
      "mt5/jpw-alavancagem-atual/README.md",
      "downloads/jpw-alavancagem-atual/manifest.json",
      "index.html",
      "tools/jpw_nocuda_*_test.py",
      "tools/leverage_package_test.py",
      "tools/leverage_page_test.py",
      "docs/architecture/JPW-NOCUDA-CHANNELS.md",
      "docs/work/CHG-JPW-NOCUDA-DAILY-20260930.md",
      "docs/work/BRIEF-JPW-NOCUDA-DAILY-20260930.md",
      "docs/work/ACTIVE-TASK.md"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "mt5/jpw-alavancagem-atual/AGENTS.md",
      "skills/**",
      "docs/normative/**",
      "tools/quality_gate.py",
      "tools/agent_instruction_structure_test.py",
      "downloads/nocuda/**",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_*",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_NoCuda_Store.mqh"
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
      "operational_MT5_install",
      "trade",
      "read_real_account"
    ],
    "regressions_forbidden": [
      "financial formulas or schemas changed",
      "study revisions written on tick/redraw/query",
      "free-price anchors or implicit migration",
      "future calendar presented as observed",
      "gate weakened"
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
      "loopback tests",
      "official public documentation"
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
      "C++ host shim",
      "existing Chromium/Playwright",
      "isolated MetaEditor only if available"
    ]
  },
  "acceptance_criteria": [
    "00h/12h/24h, mean of endpoints and min/max range remain separate and unrounded until display",
    "future only H1, max30civil days with7days bracket margin, recurring sessions Estimated",
    "common fractional ordinal resolver, no last-bar fallback for future",
    "sequential closed-candle ABC and explicit confirm/cancel",
    "line selection ignores foreign controls; optional marker roundtrip is conservative",
    "existing financial files, study schema and native NOT_RUN boundaries preserved"
  ],
  "approved_tests": [
    "NoCuda core/store/integration/projection focal",
    "Cockpit regressions and package/site",
    "full raw unchanged gate",
    "independent audit",
    "native isolated when available"
  ],
  "rollback": {
    "source": [
      "external baseline archive and patch; restore only bounded delta"
    ],
    "application_state": [
      "remove only new owned transient projection objects"
    ],
    "data": [
      "preserve all studies and financial records"
    ],
    "environment": [
      "no operational installation"
    ],
    "verification": [
      "compare baseline hashes and source ZIP"
    ]
  },
  "approved_by": "Proprietário: PLEASE IMPLEMENT THIS PLAN JPW NoCuda — desenho mais direto e projeção diária da linha",
  "approved_at": "2026-09-30T21:36:16.949529+00:00",
  "expires_on": [
    "root/branch changes",
    "scope expands into financial rules or persistence schema",
    "material source conflict"
  ]
}
```

Este registro delimita a implementação pedida; não concede autorização por si nem altera o Harness. O delta de testes é regressão de produto, sem alterar gates, timeout ou classificação. Os registros anteriores do contexto permanecem históricos.
