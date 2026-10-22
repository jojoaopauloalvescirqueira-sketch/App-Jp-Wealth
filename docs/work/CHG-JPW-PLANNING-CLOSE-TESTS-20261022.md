# CHG-JPW-PLANNING-CLOSE-TESTS-20261022

Authorization is the current human approved plan; this record grants none.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-PLANNING-CLOSE-TESTS-20261022",
  "status": "approved",
  "objective": "Add permanent RED/GREEN browser and query cases, counterproofs and default visual integration without removing240 cases or changing96 ordered runner checks.",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS",
    "branch": "codex/planejamento-patrimonial-20261020",
    "baseline_sha": "ea15afc9c6a9c30cc69c5b98a8b85c85211ffb34",
    "candidate_build": "e08c12101146ae7b"
  },
  "scope": {
    "allowed_files": [
      "tools/planning_monthly_close_test.py",
      "tools/planning_three_tabs_test.py",
      "tools/planning_state_test.js",
      "tools/ui_visual_quality_test.py",
      "tools/regression-memory.json"
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

## Deliberate contract substitution — stale-choice

Approved shared-modal explicitreview now blocks before submission. The old test clicked a disabled button and timed out; its original failing receipt is preserved in exploration/. Only stale_choice_case is adapted: original ID and baseReference retention remain, disabled+warning and synthetic direct-submit rejection replace blind doubleclick; same no-overwrite assertion remains; added explicit-refresh/retained-name/zero-write/new-review assertions. All other nine cases and runner remain byte-identical. This follows the current approved plan, not a weaker financial rule. Independent review required.
