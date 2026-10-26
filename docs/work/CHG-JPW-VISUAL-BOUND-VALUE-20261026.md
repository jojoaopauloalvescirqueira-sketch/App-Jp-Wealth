# CHG-JPW-VISUAL-BOUND-VALUE-20261026

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
      "/private/tmp/jpw-remove-nocuda-20261026/planning-compact-before-bound-value.py"
    ],
    "data": [
      "no real data changes"
    ],
    "verification": [
      "compare baseline525 files excluding authorized delta"
    ]
  },
  "change_id": "CHG-JPW-VISUAL-BOUND-VALUE-20261026",
  "objective": "Group value reads inside bound_value without changing existing visual or financial assertions",
  "risk_level": "N3",
  "authority_required": "A4",
  "scope": {
    "allowed_files": [
      "tools/planning_compact_table_test.py: bound_value only",
      "docs/work/CHG-JPW-VISUAL-BOUND-VALUE-20261026.md",
      "docs/validation/remove-nocuda-20261026/"
    ],
    "forbidden_files": [
      "normative files",
      "AGENTS.md",
      "skills/",
      "real user data",
      "MT5 Stoikus sources",
      "tools/quality_gate.py",
      "tools/ui_visual_quality_test.py",
      "application runtime sources"
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
    "same413requiredcases and2pxcriteria",
    "same900secondgate",
    "preserve visible unique container, named scope, bothtextpaths, all comparisons",
    "positive equivalence and negative-oracle tests",
    "independent review and official full before Gitintegration"
  ],
  "approved_tests": [
    "synthetic positive equivalence and negative oracles",
    "tools/ui_visual_quality_test.py --case compact-regressions",
    "tools/quality_gate.py --tier full"
  ],
  "approval": "Human explicit reply call_4f33cb2f7f58429da833b2b2201a88c2: Autorizar otimização delimitada e validação",
  "baseline_test_sha256": "4fb30ff95b9911e453e719591a08ec7a15babe430e35890ddf878a131250da52",
  "proposal_patch_sha256": "ee61a5ff50c0e201f6201a73113b447ffe90745b83d1c257d5e2c2aefa51a72d"
}
```
