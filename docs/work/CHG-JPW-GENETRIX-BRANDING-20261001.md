# CHG — JPW GENETRIX 1.16.1

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-GENETRIX-BRANDING-20261001",
  "status": "approved",
  "objective": "JPW GENETRIX 1.16.1: identidade pública, nota descritiva e logo vermelha compartilhada nos cabeçalhos MT5",
  "risk_level": "N1",
  "authority_required": "A2",
  "approved_by": "proprietário: Implement the proposed plan, após escolher marca pública e nota somente no site/README",
  "target": {
    "root": "/private/tmp/jpw-cockpit-ui-20260930",
    "branch": "codex/jpw-cockpit-ui-20260930",
    "baseline_sha": "deffc5061fe2eff3d83b6f6e742fa105ac9c5b06",
    "baseline_fingerprint": "6ed724fa243d2e0ee6fe39470b55cc32c8b7756a9ae3951f251a38b364ac5818"
  },
  "scope": {
    "allowed_files": [
      "index.html",
      "mt5/jpw-alavancagem-atual/README.md",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Alavancagem_Version.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/*Presentation*",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/*UI*",
      "mt5/jpw-alavancagem-atual/MQL5/Include/JPWealth/JPW_Genetrix_Brand.mqh",
      "mt5/jpw-alavancagem-atual/MQL5/Indicators/JPWealth/*.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Alavancagem_Observer.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Consultar_MDD.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Scripts/JPWealth/JPW_Alavancagem_Verificar_USC.mq5",
      "mt5/jpw-alavancagem-atual/MQL5/Images/JPWealth/JPW_Genetrix*",
      "tools/build_leverage_package.py",
      "tools/*test.py (somente focais de apresentação/página/pacote afetados)",
      "downloads/jpw-alavancagem-atual/manifest.json",
      "docs/work/CHG-JPW-GENETRIX-BRANDING-20261001.md",
      "docs/work/BRIEF-JPW-GENETRIX-BRANDING-20261001.md",
      "docs/work/ACTIVE-TASK.md",
      "src/js/40-app/01-navigation.js (somente label público tools-leverage, IDs/rotas/aliases intactos)",
      "src/js/manifest.json (somente sha256 do label público de navegação; ordem/schema intactos)"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "mt5/jpw-alavancagem-atual/AGENTS.md",
      "skills/**",
      "docs/normative/**",
      "tools/quality_gate.py",
      "tools/leverage_suite.py",
      ".github/**",
      "**/*Core.mqh",
      "**/*Store*.mqh",
      "**/*Config*.mqh",
      "Obsidian/**"
    ],
    "allowed_actions": [
      "bounded_edit",
      "official_generation",
      "synthetic_tests",
      "independent_audit"
    ],
    "forbidden_actions": [
      "commit",
      "push",
      "merge",
      "publish",
      "operational_MT5",
      "read_real_account",
      "trade"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "downloads/jpw-alavancagem-atual/JPW_Genetrix_Fontes_v1.16.1.zip",
      "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
      "build-id.js",
      "cache conforme gerador existente"
    ],
    "generation_commands": [
      "python3 tools/build_leverage_package.py",
      "python3 tools/rebuild_monolith.py"
    ],
    "manual_edit": "forbidden"
  },
  "data": {
    "test_policy": "synthetic_only",
    "schema_change": "forbidden"
  },
  "invariants": [
    "public branding only; technical names/paths/keys remain",
    "financial calculation version 1.9.0 and formulas unchanged",
    "legacy message New Order | JP Wealth Model unchanged",
    "current Fibonacci native UNVERIFIED_NATIVE/N/A retained",
    "no runtime approval inferred from sources",
    "red logo exactly derived from website asset; no new design",
    "no Obsidian note",
    "old evidence never replaced"
  ],
  "acceptance_criteria": [
    "GENETRIX consistent site/readme/MT5 display identity",
    "shared red-logo headers in sources and package",
    "new fonts/package/hash and preserved technical filenames",
    "focals, MT5 host suite, raw full and independent audit; native NOT_RUN separately"
  ],
  "approved_tests": [
    "affected UI/page/package focals",
    "MT5 host suite",
    "raw full",
    "independent frozen audit"
  ],
  "rollback": {
    "source": [
      "/Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-genetrix-v1161-20261001/baseline-v1160.tar.gz"
    ],
    "data": [
      "no financial writes/migration; existing records retained"
    ]
  },
  "harness": {
    "path": "/Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/2 - TRABALHO/6C - SOFTWARE/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md",
    "sha256": "b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95",
    "sections": "12–19,28–30; relocated original discovered read-only"
  },
  "scope_reconciliation": "Alvo exato do rótulo de navegação identificado no runtime da página durante revisão; já pertence à renomeação pública do plano aprovado. Não altera autoridade, escopo funcional ou política de navegação."
}
```
