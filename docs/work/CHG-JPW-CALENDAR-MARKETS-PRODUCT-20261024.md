# CHG-JPW-CALENDAR-MARKETS-PRODUCT-20261024

Human approval is the authority; this record grants none.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "status": "approved",
  "target": {
    "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS",
    "branch": "codex/calendario-mercados-20261024",
    "baseline_sha": "a4bf278cd4dc38bbaa5b905ed17a79e33684fb67"
  },
  "approved_by": "human user",
  "approved_at": "2026-10-24",
  "approval": {
    "evidence": "PLEASE IMPLEMENT THIS PLAN: Calendário e Mercados — integração com consulta rápida; resposta explícita Autorizar essa branch e a implementação delimitada",
    "limits": "No commit, merge, push, publication, dependency additions or financial changes."
  },
  "rollback": {
    "source": "Reverse only this task delta against a4bf278, preserving other work. Official rebuild restores derived outputs. No data mutation by this change."
  },
  "harness_source": {
    "path": "A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md",
    "sha256": "b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95",
    "sections": "12-14,19,24,28-30,36-49"
  },
  "data": {
    "test_policy": "synthetic_only",
    "schema_change": "forbidden"
  },
  "acceptance_criteria": [
    "approved combined host and legacy-route compatibility",
    "single controller/catalog/snapshot, lazy full view and visible renderer",
    "calendar and now remain independent; no financial writes",
    "focus/drafts/state preservation, explicit stale/failure recovery",
    "focused current receipts, full final gate, independent review, human acceptance separate"
  ],
  "change_id": "CHG-JPW-CALENDAR-MARKETS-PRODUCT-20261024",
  "objective": "Implement approved calendar/markets presentation",
  "risk_level": "N1",
  "authority_required": "A2",
  "scope": {
    "allowed_files": [
      "index.html",
      "src/styles/app.css",
      "src/js/40-app/01-navigation.js",
      "src/js/20-ui/31-tools-services.js",
      "src/js/40-app/31-market-hours/03-view.js",
      "src/js/40-app/31-market-hours/04-controller.js",
      "src/js/40-app/26-learning-catalog.js",
      "docs/architecture/CALENDAR-AGENDA.md",
      "docs/architecture/MARKET-HOURS.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/BRIEF-CALENDAR-MARKETS-20261024.md",
      "docs/superpowers/plans/2026-10-24-calendar-markets.md",
      "docs/validation/calendar-markets-20261024/"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "skills/",
      "docs/normative/",
      "src/js/10-domain/",
      "src/js/30-accounting/",
      "tools/quality_gate.py",
      ".github/"
    ],
    "allowed_actions": [
      "bounded implementation",
      "synthetic tests",
      "scoped factual evidence"
    ],
    "forbidden_actions": [
      "commit",
      "merge",
      "push",
      "publication",
      "real-data mutation",
      "global-memory mutation"
    ]
  },
  "approved_tests": [
    "calendar_markets_test.py",
    "market_hours_integration_test.py --distributions",
    "all affected market/calendar focals",
    "quality_gate.py --tier full"
  ],
  "derived_artifacts": {
    "allowed": [
      "build-id.js",
      "src/js/manifest.json",
      "dist/",
      "sw.js fingerprint",
      "src/vendor/downloads/",
      "src/vendor/market-hours/runtime-payload.js"
    ],
    "generation_commands": [
      "python3 tools/rebuild_monolith.py --refresh-manifest"
    ],
    "manual_edit": "forbidden"
  }
}
```
