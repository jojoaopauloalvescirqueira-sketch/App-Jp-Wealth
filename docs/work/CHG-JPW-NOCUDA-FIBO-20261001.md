# CHG-JPW-NOCUDA-FIBO-20261001

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-NOCUDA-FIBO-20261001",
  "status": "approved",
  "objective": "JPW NoCuda 1.16.0: importar e acompanhar Fibonacci nativo, preservar geometria/registro e ampliar UI; projeção H1/H4",
  "risk_level": "N2",
  "authority_required": "A3",
  "approved_by": "proprietario: PLEASE IMPLEMENT THIS PLAN — JPW NoCuda 1.16.0 nesta conversa",
  "target": {
    "root": "/private/tmp/jpw-cockpit-ui-20260930",
    "branch": "codex/jpw-cockpit-ui-20260930",
    "baseline_sha": "deffc5061fe2eff3d83b6f6e742fa105ac9c5b06",
    "baseline_fingerprint": "653e525d0fa08a548d0ddaac4606f2962d92de4f5fb26bbc87b78aa39a259e57"
  },
  "scope": {
    "allowed_files": [
      "mt5/jpw-alavancagem-atual/MQL5/**/JPW_NoCuda*",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_UI_Focus.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Actions.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Version.mqh",
      "mt5/jpw-alavancagem-atual/README.md",
      "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/*",
      "tools/jpw_nocuda*test.py",
      "tools/build_leverage_package.py",
      "tools/leverage_details_event_test.py",
      "tools/leverage_package_test.py",
      "tools/leverage_page_test.py",
      "index.html",
      "downloads/jpw-alavancagem-atual/manifest.json",
      "docs/architecture/JPW-NOCUDA-CHANNELS.md",
      "docs/work/CHG-JPW-NOCUDA-FIBO-20261001.md",
      "docs/work/BRIEF-JPW-NOCUDA-FIBO-20261001.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/governance/CURRENT-STATE.md"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "mt5/jpw-alavancagem-atual/AGENTS.md",
      "skills/**",
      "docs/normative/**",
      "tools/quality_gate.py",
      "tools/leverage_suite.py",
      ".github/**",
      "mt5/**/JPW_Alavancagem_Core.mqh",
      "mt5/**/JPW_Alavancagem_*Store*.mqh",
      "mt5/**/JPW_Alavancagem_Observer.mq5"
    ],
    "allowed_actions": [
      "bounded_edit",
      "official_generation",
      "synthetic_tests",
      "isolated_native_lab_if_available",
      "independent_audit"
    ],
    "forbidden_actions": [
      "commit",
      "push",
      "merge",
      "publish",
      "operational_MT5",
      "trade",
      "read_real_account"
    ]
  },
  "invariants": [
    "source object anchors/levels never snap or silently normalize",
    "legacy studies/schema unchanged",
    "no writes on render/tick/zoom",
    "native parity NOT_RUN does not become PASS",
    "unproved native geometry cannot be presented as verified",
    "financial formulas and records untouched",
    "future H1/H4 Estimated and calendar checked",
    "SOURCE REVISION UNKNOWN remains honest until verified"
  ],
  "tests": [
    "production math/core host tests",
    "SQLite actual persistence and replay",
    "import/interaction replay",
    "projection H1/H4",
    "package/page focals",
    "MT5 host suite",
    "raw full",
    "native exact-byte lab or NOT_RUN",
    "frozen independent review"
  ],
  "rollback": {
    "snapshot": "/Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-nocuda-fibo-v1160-20261001/baseline-v1150.tar.gz",
    "mode": "restore only delta; regenerate derivatives; never delete legacy studies or financial records"
  },
  "derived_artifacts": {
    "generation_commands": [
      "python3 tools/build_leverage_package.py",
      "python3 tools/rebuild_monolith.py"
    ],
    "manual_edit": "forbidden"
  },
  "native_acceptance": "BLOCKED_NATIVE until exact-byte compilation/interaction/geometry receipts"
}
```
