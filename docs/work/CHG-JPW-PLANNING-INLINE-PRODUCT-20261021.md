# CHG-JPW-PLANNING-INLINE-PRODUCT-20261021

Authorization originates in the current approved human plan; this record grants none.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "status": "approved",
  "target": {
    "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS",
    "branch": "codex/planejamento-patrimonial-20261020",
    "baseline_sha": "ea15afc9c6a9c30cc69c5b98a8b85c85211ffb34",
    "candidate_build": "2ddbac03d67141d0"
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
    "approvedplan",
    "RED/GREEN/counterproofs",
    "oldprotections preserved exceptexplicitobsoletecontracts",
    "currentFULL96",
    "independentreview",
    "humanacceptance separate"
  ],
  "approved_tests": [
    "focalnew/existing",
    "quality_gate.py --tier full"
  ],
  "rollback": {
    "source": [
      "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/.superpowers/sdd/2026-10-21-planning-monthly-inline/candidate-2dd-before.tar.gz",
      "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/.superpowers/sdd/2026-10-21-planning-monthly-inline/baseline.json"
    ],
    "application_state": [
      "no financial migration; new auxiliary preference only"
    ],
    "data": [
      "real data untouched"
    ],
    "environment": [
      "no installs"
    ],
    "verification": [
      "compare baseline hashes"
    ]
  },
  "approved_by": "Human PLEASE IMPLEMENT THIS PLAN: Preenchimento mensal — compacto, editável e intuitivo, this conversation",
  "approved_at": "2026-10-22T01:17:47.924047+00:00",
  "expires_on": [
    "material root/branch/HEAD/scope drift"
  ],
  "change_id": "CHG-JPW-PLANNING-INLINE-PRODUCT-20261021",
  "risk_level": "N2",
  "authority_required": "A3",
  "objective": "Inline monthly UI and pure result-input preview; two isolated browser preferences with precise cleanup; no financial schema/writer/formula change.",
  "scope": {
    "allowed_files": [
      "src/js/30-accounting/06-planning/02-state.js",
      "src/js/30-accounting/06-planning/03-ui.js",
      "src/styles/app.css",
      "src/js/40-app/07-finalize-session.js",
      "docs/architecture/PLANNING.md",
      "README.md",
      "CHANGELOG.md",
      "SESSION_HANDOFF.md",
      "docs/governance/CURRENT-STATE.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/validation/planning-monthly-inline-20261021/",
      "docs/superpowers/plans/2026-10-21-planning-monthly-inline.md",
      "src/js/40-app/01-navigation.js"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "skills/",
      "docs/normative/",
      "src/js/30-accounting/06-planning/01-engine.js",
      "tools/quality_gate.py"
    ],
    "allowed_actions": [
      "implement exacthumanplan",
      "test/build/review",
      "bounded factualdocumentation"
    ],
    "forbidden_actions": [
      "commit",
      "merge",
      "push",
      "deploy",
      "branch/worktree creation",
      "install dependencies",
      "global memory/config change",
      "real-data access",
      "test weakening"
    ],
    "regressions_forbidden": [
      "financial writers and schema unchanged",
      "allpreviousdata/history preserved",
      "old96gatechecks/206visualIDs retained"
    ]
  }
}
```

Product and test control plane have separate contracts. Source2dd baseline is verified and recoverable; no Git operation or publication. Adaptation only for explicitly substituted presentation: activate cell before editing, explicitSave replacingblur, YearAll. Numeric values, financial confirmations, geometric tolerances and unrelatedjourneys remain. Factual context headers may link current receipts without changing authority/instructions.

Bounded navigation integration required by the approved no-hidden-draft criterion: existingnavhas Forex guards but none for Planning. Permit only optional Planning ui.guardNavigation hook in navApply, preserving availability ordering, accepted-navigation notifications, other guards and Settings behavior. No route/catalog redesign.
