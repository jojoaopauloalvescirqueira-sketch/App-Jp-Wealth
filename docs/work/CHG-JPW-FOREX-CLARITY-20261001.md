# CHG-JPW-FOREX-CLARITY-20261001

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-FOREX-CLARITY-20261001",
  "status": "approved",
  "objective": "FOREX-CLARITY conforme plano completo aprovado",
  "risk_level": "N1",
  "authority_required": "A2",
  "approved_by": "Proprietário: PLEASE IMPLEMENT THIS PLAN: JP Wealth — navegação, leitura do Estatuto e clareza do Forex",
  "target": {
    "root": "/private/tmp/jpw-cockpit-ui-20260930",
    "branch": "codex/jpw-cockpit-ui-20260930",
    "head": "deffc5061fe2eff3d83b6f6e742fa105ac9c5b06",
    "fingerprint": "bd0894b36d0fa8ff696e9bf5f7833fc654326466999127b70e95e8d4b0e8390e"
  },
  "scope": {
    "allowed_files": [
      "src/js/20-ui/01-header-readout.js",
      "src/js/20-ui/13-exec-views.js",
      "src/js/20-ui/16-operation-history.js",
      "src/js/20-ui/26-forex-engine-views.js",
      "src/js/20-ui/28-fx-consolidated.js",
      "src/js/20-ui/30-execution-board.js",
      "src/js/20-ui/31-forex-accounts.js",
      "src/js/30-accounting/05-fx-planning/05-fx-ui.js (selectors presentation only)",
      "index.html (Forex sections only)",
      "src/styles/app.css (Forex only)",
      "tools/forex_clarity_test.py",
      "tools/forex_execution_table_test.py (approved compact/detail presentation expectations only)",
      "tools/forex_accounts_workspace_test.py (approved visible labels only)",
      "docs/architecture/FOREX-EXPERIENCE.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/CHG-JPW-FOREX-CLARITY-20261001.md",
      "docs/work/BRIEF-JPW-SITE-CLARITY-20261001.md",
      "docs/governance/CURRENT-STATE.md (focal appended report only)",
      "src/js/40-app/13-dashboard-layout.js (swap order of orders/references defaults only; preserve v6 saved preferences)"
    ],
    "forbidden_files": [
      "src/js/00-core/**",
      "src/js/10-domain/**",
      "docs/normative/**",
      "mt5/**",
      "downloads/**",
      "AGENTS.md",
      "skills/**",
      "tools/quality_gate.py",
      "tools/validate_project.py",
      ".github/**"
    ],
    "allowed_actions": [
      "bounded_edit",
      "functional_regression_tests",
      "synthetic_browser_tests",
      "official_generation",
      "independent_audit"
    ],
    "forbidden_actions": [
      "commit",
      "push",
      "merge",
      "publish",
      "real_account_reads",
      "install_dependencies"
    ],
    "regressions_forbidden": [
      "schema/calculations/records/consent unchanged",
      "preserve user work/drafts/preferences",
      "no gate weakening"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "src/js/manifest.json",
      "build-id.js",
      "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
      "src/vendor/pdfjs/runtime-assets.js",
      "src/vendor/normative/statute-payload.js"
    ],
    "generation_commands": [
      "python3 tools/rebuild_monolith.py"
    ],
    "manual_edit": "forbidden for generated artifacts"
  },
  "data": {
    "test_policy": "synthetic_only",
    "schema_change": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "isolated localhost",
      "official documentation read-only"
    ],
    "temporary_artifacts": "allowed",
    "cleanup_required": true
  },
  "acceptance_criteria": [
    "Panorama and next action first",
    "same operational context across all Forex routes",
    "Compact order table with details/full audit view and mobile cards",
    "same calculations, identity, drafts, command handlers and explicit apply"
  ],
  "approved_tests": [
    "focused functional tests",
    "MT5 host regression",
    "standard",
    "raw full",
    "independent design/integrity audit"
  ],
  "rollback": {
    "source": [
      "/Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-navigation-normative-forex-20261001/baseline.tar.gz"
    ],
    "verification": [
      "restore only candidate delta, preserve previous dirty work",
      "protected hashes identical"
    ]
  },
  "harness": {
    "path": "/Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/2 - TRABALHO/6C - SOFTWARE/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md",
    "sha256": "b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95"
  },
  "inherited_limit": "SOURCE REVISION UNKNOWN remains explicit",
  "scope_discovery": "Default order controls approved order-before-references presentation; no preference schema or migration."
}
```

## Expectativas funcionais aprovadas

A aprovação da tabela compacta muda a sequência de foco: HASH passa ao detalhe, e cálculos de prévia ficam em seção expansível. Os rótulos de conta/Operação também foram aprovados em português. Os focais anteriores poderão ajustar somente essas expectativas visuais/de navegação para continuar verificando os mesmos valores, HASH completo, cancelamento, versões, guards e ausência de writes. Gates, fixtures de rede, deadlines, thresholds e classificações permanecem intactos; execuções brutas anteriores ficam registradas.
