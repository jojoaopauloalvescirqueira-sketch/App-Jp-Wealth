# CHG — JPW GENETRIX / redesign do site

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-GENETRIX-SITE-REDESIGN-20261001",
  "status": "approved",
  "objective": "Reorganizar a seção MT5 em cinco áreas acessíveis, apresentação editorial, instalação guiada e detalhes progressivos; somente site",
  "risk_level": "N1",
  "authority_required": "A2",
  "approved_by": "Proprietário: PLEASE IMPLEMENT THIS PLAN, cinco áreas, entender/instalar e prévia ilustrativa confirmadas",
  "target": {
    "root": "/private/tmp/jpw-cockpit-ui-20260930",
    "branch": "codex/jpw-cockpit-ui-20260930",
    "baseline_sha": "deffc5061fe2eff3d83b6f6e742fa105ac9c5b06",
    "baseline_fingerprint": "e569127c8ac120055d4d538a04b714af3f57bbb01f40e3d408c0e97368623daa"
  },
  "scope": {
    "allowed_files": [
      "index.html (somente jpwLeveragePage)",
      "src/styles/app.css (estilos restritos à seção Genetrix)",
      "src/js/20-ui/31-tools-services.js (UI local Genetrix e atualização de metadados)",
      "src/js/manifest.json (somente digest do módulo Tools)",
      "tools/leverage_page_test.py (contratos da UX aprovada; integridade preservada)",
      "tools/genetrix_site_test.py (focal adicional se necessário)",
      "docs/work/CHG-JPW-GENETRIX-SITE-REDESIGN-20261001.md",
      "docs/work/BRIEF-JPW-GENETRIX-SITE-REDESIGN-20261001.md",
      "docs/work/ACTIVE-TASK.md"
    ],
    "forbidden_files": [
      "mt5/**",
      "downloads/** (bytes de base preservados; regeneração oficial idêntica permitida)",
      "AGENTS.md",
      "skills/**",
      "docs/normative/**",
      "docs/governance/**",
      "tools/quality_gate.py",
      "tools/leverage_suite.py",
      ".github/**",
      "sw.js",
      "tools/rebuild_monolith.py"
    ],
    "allowed_actions": [
      "bounded_edit",
      "synthetic_browser_tests",
      "official_generation",
      "independent_audit"
    ],
    "forbidden_actions": [
      "commit",
      "merge",
      "push",
      "publish",
      "read_real_account",
      "operational_MT5",
      "trade",
      "new_dependencies"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "build-id.js",
      "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
      "src/vendor/pdfjs/runtime-assets.js (geração idêntica)"
    ],
    "generation_commands": [
      "python3 tools/rebuild_monolith.py"
    ],
    "manual_edit": "forbidden"
  },
  "data": {
    "test_policy": "synthetic_only",
    "schema_change": "forbidden"
  },
  "invariants": [
    "MT5 1.16.1 sources, manifest and ZIP byte-identical",
    "all old IDs and external route tools-leverage preserved",
    "financial S and storage unchanged by navigation",
    "no new cache policy or router",
    "downloads retain size/SHA validation and unique controls",
    "native NOT_RUN and Fibonacci UNVERIFIED_NATIVE remain explicit",
    "illustration clearly fictitious; no real account data"
  ],
  "acceptance_criteria": [
    "five areas one at a time; all deep links reveal before focus",
    "essential install steps exposed, file list expandable, five folders including Images",
    "16px body, 44px controls, themes/4layouts/3203901440 and200percent",
    "hostile/unknown hash no route/write; Back/Forward/reload work",
    "HTTP/file/portable/PWA downloads and87ZIPmembers",
    "focals, MT5 regression suite, rawfull and independentUX audit"
  ],
  "approved_tests": [
    "leverage_page_test",
    "leverage_package_test",
    "genetrix_site_test if added",
    "MT5 host suite",
    "raw full",
    "independent design/a11y/scope audit"
  ],
  "rollback": {
    "source": [
      "/Users/joaopauloalves/.codex/.chatgpt-projects/g-p-6a4fc0aa51dc8191af013579f37179a3/outputs/jpw-genetrix-site-redesign-20261001/baseline-v1161.tar.gz"
    ],
    "data": [
      "no financial records or persistent preferences modified"
    ]
  },
  "harness": {
    "path": "/Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/2 - TRABALHO/6C - SOFTWARE/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md",
    "sha256": "b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95"
  },
  "design_source": {
    "path": "skills/jpw-design/references/design-philosophy.md",
    "sha256": "fcc11d3eab563f3464e84e5b8886ddb9ee4784cff75530702f07776d19e0dff7",
    "mode": "IMPLEMENTAR"
  }
}
```
