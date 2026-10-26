# CHG-JPW-REMOVE-NOCUDA-CONTROLS-20261026

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
  "change_id": "CHG-JPW-REMOVE-NOCUDA-CONTROLS-20261026",
  "objective": "Replace explicitly retired behavior assertions with retirement checks; preserve shared download protections",
  "risk_level": "N3",
  "authority_required": "A4",
  "scope": {
    "allowed_files": [
      "tools/nocuda_tools_test.py",
      "tools/saving_draft_recovery_test.py: retired drawing becomes read-copy-only",
      "tools/time_twins_browser_test.py: replace retired draft fixture with Research",
      "tools/capital_currents_browser_test.py: replace retired draft fixture with Research",
      "tools/planning_proportions_test.py: remove exclusively retired fingerprint files",
      "tools/minigames_test.py: remove obsolete submenu member",
      "tools/nocuda_transfer_test.js: replace with retirement assertions if still consumed",
      "tools/download_assets_test.js",
      "tools/download_assets_browser_test.py",
      "tools/build_reproducibility_test.py",
      "tools/navigation_ia_test.py",
      "tools/learning_guide_test.py",
      "tools/learning_controller_test.mjs",
      "tools/learning_foundation_test.mjs",
      "tools/dante_catalog_test.mjs",
      "tools/dante_guide_test.py",
      "tools/ui_visual_quality_test.py: only obsolete source input if necessary",
      "tools/quality_gate.py: replace nocuda-tools entry only; preserve all other IDs/criteria/timeouts",
      "tools/regression-memory.json: additive factual retirement records",
      "docs/work/CHG-JPW-REMOVE-NOCUDA-CONTROLS-20261026.md",
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
