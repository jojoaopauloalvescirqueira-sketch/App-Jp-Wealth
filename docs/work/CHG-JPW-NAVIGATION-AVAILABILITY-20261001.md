# CHG-JPW-NAVIGATION-AVAILABILITY-20261001

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-NAVIGATION-AVAILABILITY-20261001",
  "status": "approved",
  "objective": "NAVIGATION-AVAILABILITY conforme plano completo aprovado",
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
      "src/js/20-ui/25-dash-macro.js",
      "src/js/20-ui/23-research-views.js",
      "src/js/20-ui/32-module-availability.js",
      "src/js/40-app/01-navigation.js",
      "src/js/40-app/09-settings-modal.js",
      "src/js/40-app/12-global-dashboard.js",
      "src/js/40-app/18-galton-board/**",
      "index.html (dashboard/research/settings/nav only)",
      "src/styles/app.css (local delta only)",
      "tools/*navigation*_test.py (approved location/visible children expectations only)",
      "tools/settings_modal_test.py (approved location only)",
      "tools/exec_submenu_test.py (approved visible Forex labels only)",
      "tools/dashboard_macro_test.py (approved frozen-module cardinality and no-domain-read expectations only)",
      "tools/galton_board_test.py (approved host/lifecycle expectations only)",
      "docs/architecture/NAVIGATION-HIERARCHY.md",
      "docs/architecture/MODULE-AVAILABILITY.md",
      "docs/architecture/GALTON-BOARD.md",
      "docs/architecture/ARCHITECTURE.md (informational component locations only)",
      "docs/architecture/CODE-MAP.md (informational component locations only)",
      "README.md (current product paths and capabilities only)",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/CHG-JPW-NAVIGATION-AVAILABILITY-20261001.md",
      "docs/work/BRIEF-JPW-SITE-CLARITY-20261001.md",
      "docs/governance/CURRENT-STATE.md (focal appended report only)"
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
    "Frozen modules excluded before dashboard domain reads",
    "Lab single instance in Settings Conhecimento, old aliases compatible, no autoplay",
    "Others absent in visible menus",
    "all layouts and global health preserved"
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
  "inherited_limit": "SOURCE REVISION UNKNOWN remains explicit"
}
```

## Reconciliação documental delimitada

O plano exige atualizar guia e coerência. Os mapas de componentes e o README ainda descrevem a localização substituída em Research. Este acréscimo cobre somente a descrição do runtime aprovado; nenhuma instrução de autoridade, gate, skill ou Harness é alterada. Registros históricos permanecem identificados como históricos.

## Correção de inventário identificada na auditoria independente

O plano aprovado exige testar ausência de cartões/links e de consultas dos módulos congelados. `tools/dashboard_macro_test.py` executou essas expectativas e acrescentou a sondagem `assert_frozen_projection`, mas sua linha havia sido omitida da enumeração inicial. A auditoria identificou e este registro corrige a omissão documental antes do congelamento final. Não se afirma que a linha constava anteriormente. Os ajustes limitam-se à cardinalidade/links coerentes com os módulos disponíveis e à verificação de zero leituras; fórmulas, fixtures financeiras, thresholds, deadlines, quality_gate e classificações não mudaram.
