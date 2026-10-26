# CHG-JPW-REMOVE-NOCUDA-PRODUCT-20261026

```yaml
{
  "schema": "jp-harness/chg/v1",
  "status": "approved",
  "target": {
    "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS",
    "branch": "codex/remover-nocuda-tool-20261026",
    "baseline_sha": "a4bf278cd4dc38bbaa5b905ed17a79e33684fb67"
  },
  "derived_artifacts": {
    "allowed": [
      "scoped validation receipts",
      "official regenerated build artifacts"
    ],
    "manual_edit": "allowed"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "loopback test servers"
    ],
    "temporary_artifacts": "allowed",
    "cleanup_required": false
  },
  "data": {
    "test_policy": "synthetic_only",
    "approved_real_data": [],
    "schema_change": "forbidden"
  },
  "toolchain": {
    "dependency_changes": [],
    "allowed_processes": [
      "existing Python/Node/Chrome",
      "official builders",
      "read-only Git; specifically authorized branch creation"
    ]
  },
  "approved_by": "human user",
  "approved_at": "2026-10-26",
  "expires_on": [
    "material target or scope change"
  ],
  "rollback": {
    "source": [
      "/private/tmp/jpw-remove-nocuda-20261026/pending-before.zip",
      "baseline Git and scoped reverse delta only"
    ],
    "data": [
      "no real data changes"
    ],
    "verification": [
      "compare baseline525 files excluding authorized delta"
    ]
  },
  "change_id": "CHG-JPW-REMOVE-NOCUDA-PRODUCT-20261026",
  "objective": "Remove retired Nocuda Tool; preserve shared components and all preexisting changes",
  "risk_level": "N1",
  "authority_required": "A2",
  "scope": {
    "allowed_files": [
      "index.html",
      "src/styles/app.css",
      "src/js/20-ui/31-tools-services.js",
      "src/js/40-app/01-navigation.js",
      "src/js/00-core/07-workspace-backup.js: read-only retired draft reason only",
      "src/js/00-core/09-learning-progress.js",
      "src/js/40-app/26-learning-catalog.js",
      "src/js/40-app/28-learning-guide.js",
      "src/js/10-domain/16-nocuda-transfer.js: remove",
      "src/js/00-core/10-download-assets.js",
      "src/js/manifest.json",
      "tools/rebuild_monolith.py",
      "downloads/nocuda/: remove",
      "assets/nocuda-*.png: remove",
      "src/vendor/downloads/nocuda-payload.js: remove",
      "official generated files",
      "sw.js: remove exclusively retired URLs preserving lifecycle",
      "docs/architecture/: factual affected contracts only",
      "docs/work/ACTIVE-TASK.md: prepend only",
      "docs/work/CHG-JPW-REMOVE-NOCUDA-*.md",
      "docs/superpowers/plans/2026-10-26-remove-nocuda.md",
      "docs/validation/remove-nocuda-20261026/"
    ],
    "forbidden_files": [
      "normative files",
      "AGENTS.md",
      "skills/",
      "real user data",
      "MT5 Stoikus sources"
    ],
    "allowed_actions": [
      "bounded approved plan implementation",
      "synthetic tests",
      "independent review",
      "official rebuild"
    ],
    "forbidden_actions": [
      "commit",
      "merge",
      "push",
      "publish",
      "dependency changes",
      "erase history",
      "real data deletion"
    ],
    "regressions_forbidden": [
      "Research or Stoikus changes",
      "loss of financial data",
      "shared download protections weakened",
      "skip full checks"
    ]
  },
  "acceptance_criteria": [
    "Retired tool absent from runtime and distributions",
    "Old routes redirect after accepted navigation",
    "Legacy progress and draft content preserved",
    "Shared download integrity/cancellation/retry/lazy loading remain covered",
    "Independent review and full on final candidate; human acceptance separate"
  ],
  "approved_tests": [
    "focused retirement/download/navigation/guide/build tests",
    "tools/quality_gate.py --tier full"
  ],
  "approval": "Human PLEASE IMPLEMENT THIS PLAN and specific branch approval call_2a918a2423a44aa8baceab712aec311e"
}
```
