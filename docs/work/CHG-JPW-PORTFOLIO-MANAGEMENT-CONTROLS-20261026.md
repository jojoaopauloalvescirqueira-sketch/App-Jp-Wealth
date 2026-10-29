# CHG-JPW-PORTFOLIO-MANAGEMENT-CONTROLS-20261026

```json
{
  "schema": "jp-harness/chg/v1",
  "status": "approved",
  "change_id": "CHG-JPW-PORTFOLIO-MANAGEMENT-CONTROLS-20261026",
  "objective": "Permanent behavioral regressions and scoped update of deliberately superseded navigation expectations, without weakening protections",
  "risk_level": "N3",
  "authority_required": "A4",
  "approved_by": "human user",
  "approved_at": "2026-10-26",
  "target": {
    "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS",
    "branch": "codex/portfolio-gerenciamento-20261026",
    "baseline_sha": "3e24f60f8cfe87f79335f40e95a0927379a9f834"
  },
  "scope": {
    "allowed_files": [
      "tools/*test*",
      "tools/quality_gate.py",
      "tools/regression-memory.json",
      "docs/work/*PORTFOLIO-MANAGEMENT*",
      "docs/validation/portfolio-management-20261026/"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "skills/",
      "financial normative sources"
    ],
    "allowed_actions": [
      "new permanent regression cases",
      "replace only approved obsolete menu expectations",
      "register focused cases in accumulated gates",
      "counterproofs and independent review"
    ],
    "forbidden_actions": [
      "skip old protections",
      "weaken tolerances/timeouts",
      "commit",
      "merge",
      "push"
    ]
  },
  "data": {
    "test_policy": "synthetic_only",
    "approved_real_data": [],
    "schema_change": "approved",
    "schema_change_detail": "optional managementAnnual v1; preserve old backups, no implicit migration"
  },
  "rollback": {
    "source": [
      "baseline Git scoped reverse delta only"
    ],
    "data": [
      "no real data imported; old records preserved"
    ]
  },
  "acceptance_criteria": [
    "Approved user plan in conversation; annual engine parity and deliberate calendar adaptations",
    "Existing ledger canonical; management selection independent; no policy changes",
    "New full evidence and human visual review separate"
  ],
  "approval": "Human PLEASE IMPLEMENT THIS PLAN plus branch approval call_b5645be77c86439dab31681dce70fcfb",
  "approved_tests": [
    "synthetic focal engine/state/UI/navigation/backup and compatibility tests described in the approved human plan",
    "counterproofs and independent review for deliberately changed verifiers",
    "four layouts, themes, 320–1440, native200 and HTTP/offline/file/portable",
    "quality_gate.py --tier full on the stable final candidate"
  ],
  "derived_artifacts": {
    "allowed": [
      "build-id.js",
      "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
      "src/js/manifest.json",
      "src/vendor/* official build envelopes"
    ],
    "generation_commands": [
      "python3 tools/rebuild_monolith.py --refresh-manifest"
    ],
    "manual_edit": "forbidden"
  }
}
```
