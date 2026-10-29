# CHG-JPW-HEDGE-PROP-PRODUCT-20261027

```json
{
  "schema": "jp-harness/chg/v1",
  "status": "approved",
  "change_id": "CHG-JPW-HEDGE-PROP-PRODUCT-20261027",
  "objective": "Approved Hedge Prop educational simulator; ideal endpoint math, cost impact only, no financial writers",
  "risk_level": "N3",
  "authority_required": "A4",
  "approved_by": "human user",
  "approved_at": "2026-10-27",
  "target": {
    "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS",
    "branch": "codex/mesas-proprietarias-hedge-20261027",
    "baseline_sha": "3e24f60f8cfe87f79335f40e95a0927379a9f834"
  },
  "scope": {
    "allowed_files": [
      "index.html",
      "src/js/40-app/01-navigation.js",
      "src/js/20-ui/31-tools-services.js",
      "src/js/40-app/32-prop-firms/",
      "src/js/40-app/07-finalize-session.js",
      "src/js/40-app/26-learning-catalog.js",
      "src/styles/app.css",
      "src/js/manifest.json",
      "official generated artifacts",
      "docs/architecture/HEDGE-PROP-FIRM.md",
      "docs/architecture/NAVIGATION-HIERARCHY.md",
      "docs/architecture/LEARNING-GUIDE.md",
      "docs/work/*HEDGE-PROP*",
      "docs/work/ACTIVE-TASK.md",
      "docs/superpowers/plans/2026-10-27-hedge-prop.md",
      "docs/validation/hedge-prop-20261027/"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "skills/",
      "docs/normative/",
      "mt5/",
      "real user data",
      "financial policy/state/writers"
    ],
    "allowed_actions": [
      "bounded implementation approved in user PLEASE IMPLEMENT THIS PLAN",
      "synthetic focal tests and independent review",
      "official rebuild and full quality gate"
    ],
    "forbidden_actions": [
      "commit",
      "merge",
      "push",
      "publication",
      "new dependencies",
      "financial migration",
      "real-data deletion"
    ]
  },
  "approval": "User approved exact five-section Hedge plan, including formulas/tests; branch call_f53f183420e04e6eafadbc5e4717eebc authorized exact branch and preserving pending work",
  "data": {
    "test_policy": "synthetic_only",
    "approved_real_data": [],
    "schema_change": "none"
  },
  "rollback": {
    "source": [
      "Reverse only this task delta using /private/tmp/jpw-hedge-prop-20261027/baseline-pending.tar.gz and baseline hashes; no reset/stash"
    ],
    "data": [
      "RAM-only simulation; no persistent or financial writes"
    ]
  },
  "acceptance_criteria": [
    "Two screenshot oracles, inputs blank vs zero, costs by mutually exclusive path",
    "Forex-independent Tools navigation and no financial reads/writes",
    "New full suite on frozen candidate; human acceptance separate"
  ],
  "derived_artifacts": {
    "allowed": [
      "build-id.js",
      "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
      "src/js/manifest.json",
      "sw.js",
      "src/vendor/ official build envelopes"
    ],
    "generation_commands": [
      "python3 tools/rebuild_monolith.py --refresh-manifest"
    ],
    "manual_edit": "forbidden"
  }
}
```
