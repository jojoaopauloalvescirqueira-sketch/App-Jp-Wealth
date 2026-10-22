# CHG-JPW-PLANNING-CLOSE-PRODUCT-20261022

Authorization is the current human approved plan; this record grants none.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-PLANNING-CLOSE-PRODUCT-20261022",
  "status": "approved",
  "objective": "Guided two-command month closure and explicit stale-draft review; read-only structured preview. Existing financial rules/writers/schema unchanged.",
  "risk_level": "N1",
  "authority_required": "A2",
  "target": {
    "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS",
    "branch": "codex/planejamento-patrimonial-20261020",
    "baseline_sha": "ea15afc9c6a9c30cc69c5b98a8b85c85211ffb34",
    "candidate_build": "e08c12101146ae7b"
  },
  "scope": {
    "allowed_files": [
      "src/js/30-accounting/06-planning/02-state.js",
      "src/js/30-accounting/06-planning/03-ui.js",
      "src/styles/app.css",
      "docs/architecture/PLANNING.md",
      "README.md",
      "CHANGELOG.md",
      "SESSION_HANDOFF.md",
      "docs/governance/CURRENT-STATE.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/superpowers/plans/2026-10-22-planning-monthly-close.md",
      "docs/validation/planning-monthly-close-20261022/"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "skills/",
      "docs/normative/",
      "src/js/30-accounting/06-planning/01-engine.js",
      "tools/quality_gate.py",
      ".github/"
    ],
    "allowed_actions": [
      "bounded approved implementation",
      "synthetic tests",
      "factual records",
      "independent review"
    ],
    "forbidden_actions": [
      "commit",
      "push",
      "merge",
      "deploy",
      "financial migration",
      "global memory modification"
    ],
    "regressions_forbidden": [
      "old240 criteria and96 runner identities",
      "financial writer/contracts",
      "backup compatibility"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "index.html",
      "build-id.js",
      "sw.js",
      "src/js/manifest.json",
      "dist/",
      "src/vendor/downloads/",
      "src/vendor/market-hours/runtime-payload.js"
    ],
    "generation_commands": [
      "python3 tools/rebuild_monolith.py --refresh-manifest"
    ],
    "manual_edit": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "localhost"
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
      "existingPython",
      "existingNode",
      "existingChromium",
      "officialBuilder"
    ]
  },
  "acceptance_criteria": [
    "approved closure plan",
    "RED/GREEN and counterproofs",
    "preserve existing protections",
    "fresh frozen full",
    "independent review",
    "human visual acceptance separate"
  ],
  "approved_tests": [
    "focal existing and new",
    "quality_gate.py --tier full"
  ],
  "rollback": {
    "source": [
      "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/.superpowers/sdd/2026-10-22-planning-monthly-close/candidate-e08c-before.tar.gz",
      "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/.superpowers/sdd/2026-10-22-planning-monthly-close/baseline.json"
    ],
    "application_state": [
      "no migration"
    ],
    "data": [
      "real data untouched"
    ],
    "environment": [
      "no dependency changes"
    ],
    "verification": [
      "baseline hash comparison"
    ]
  },
  "approved_by": "Human PLEASE IMPLEMENT THIS PLAN: Planejamento — revisão de uso e correção do fechamento mensal, current conversation",
  "approved_at": "2026-10-22T13:10:49.805997+00:00",
  "expires_on": [
    "material root/branch/HEAD/scope drift"
  ]
}
```
