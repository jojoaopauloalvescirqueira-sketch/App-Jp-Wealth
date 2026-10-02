# CHG-JPW-NORMATIVE-READER-20261001

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-NORMATIVE-READER-20261001",
  "status": "approved",
  "objective": "NORMATIVE-READER conforme plano completo aprovado",
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
      "src/js/20-ui/34-normative-reader.js",
      "src/js/20-ui/31-tools-services.js (normative view lifecycle only)",
      "src/js/40-app/01-navigation.js (tools-normative route only)",
      "index.html (tools-normative and viewer root only)",
      "src/styles/app.css (reader only)",
      "tools/rebuild_monolith.py (canonical PDF and existing portable image payload generation only)",
      "src/js/40-app/06-app-icons.js (resolve existing images from generated portable payload only)",
      "sw.js (new asset precache only; no lifecycle change)",
      "tools/normative_reader_test.py",
      "docs/architecture/NORMATIVE-READER.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/CHG-JPW-NORMATIVE-READER-20261001.md",
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
    "V11 original size and SHA verified before display",
    "Local PDF.js, isolated worker, no remote OCR",
    "page/search/copy/original download and visible errors",
    "HTTP/PWA/file/portable; unchanged consent and Forex import"
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

## Dependência necessária do fluxo portátil

O focal do novo leitor abriu o PDF, pesquisou e baixou os bytes corretos, mas o boot do HTML portátil standalone produz cinco ERR_FILE_NOT_FOUND por imagens da marca já presentes na base. A prova original permanece em `pdf/portable-trace.jsonl`; não é reclassificada. Para cumprir o ambiente portátil aprovado, o gerador embute somente os PNG existentes explicitamente enumerados. `06-app-icons.js` resolve esses bytes apenas no portátil; paths, opções primary/secondary, preferência, cache-bust HTTP, manifestos e lifecycle PWA permanecem. Nenhum asset novo, alteração financeira ou flexibilização de teste.
