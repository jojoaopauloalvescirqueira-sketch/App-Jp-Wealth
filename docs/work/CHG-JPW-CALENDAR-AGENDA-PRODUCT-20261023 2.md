# CHG-JPW-CALENDAR-AGENDA-PRODUCT-20261023

Human approval is the authority; this record grants none.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "status": "approved",
  "target": {
    "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS",
    "branch": "codex/calendario-agenda-20261023",
    "baseline_sha": "d517be0748f886085b3029c809bd68046e5c0f77",
    "preexisting_manifest": "/private/tmp/jpw-calendar-agenda-20261023/baseline/manifest.json"
  },
  "approval": {
    "approver": "human user",
    "evidence": "PLEASE IMPLEMENT THIS PLAN: Calendário e Agenda — acesso ao lado do sino; explicit branch answer Autorizar essa branch e preservar as alterações",
    "limits": "No commit, merge, push, publication, new dependencies or financial changes."
  },
  "rollback": {
    "source": "Restore only this task delta against the recoverable pending-files.tar.gz + manifest, preserving prior Planning/Notifications changes",
    "generated": "Official rebuild after source rollback"
  },
  "acceptance_criteria": [
    "approved calendar/agenda behaviour",
    "no financial mutation from calendar reads",
    "confirmed agenda writes and recovery",
    "weekly FF preserved, monthly coverage explicit",
    "focused RED/GREEN and counterproofs",
    "full final gate, independent review, human acceptance separate"
  ],
  "change_id": "CHG-JPW-CALENDAR-AGENDA-PRODUCT-20261023",
  "objective": "Implement the approved monthly calendar, local personal agenda and permitted monthly economic data",
  "risk_level": "N2",
  "authority_required": "A3",
  "scope": {
    "allowed_files": [
      "index.html",
      "sw.js",
      "src/styles/app.css",
      "src/js/10-domain/19-personal-agenda.js",
      "src/js/40-app/16-monthly-economic-data.js",
      "src/js/40-app/19-calendar-agenda.js",
      "src/js/40-app/17-economic-calendar.js",
      "src/js/20-ui/31-tools-services.js",
      "src/js/40-app/11-operational-shell.js",
      "src/js/40-app/07-finalize-session.js",
      "src/js/40-app/06-boot.js",
      "src/js/00-core/07-workspace-backup.js",
      "src/js/30-accounting/01-daily-ledger.js",
      "src/js/40-app/26-learning-catalog.js",
      "infra/monthly-economic-feed/",
      "docs/architecture/CALENDAR-AGENDA.md",
      "docs/architecture/STATE-SCHEMA.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/BRIEF-CALENDAR-AGENDA-20261023.md",
      "docs/superpowers/plans/2026-10-23-calendar-agenda.md",
      "docs/validation/calendar-agenda-20261023/"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "skills/",
      "docs/normative/",
      "src/js/00-core/00-forex-policy.js",
      "src/js/10-domain/00-forex-engine.js",
      "src/js/30-accounting/06-planning/01-engine.js",
      "infra/ff-news-feed/",
      ".github/"
    ],
    "allowed_actions": [
      "bounded implementation",
      "synthetic tests",
      "public permitted source research",
      "factual scoped records"
    ],
    "forbidden_actions": [
      "commit",
      "push",
      "merge",
      "publication",
      "real-data changes",
      "financial migrations",
      "global-memory mutation"
    ]
  },
  "data": {
    "test_policy": "synthetic only",
    "schema_change": "Add optional personalAgenda; absent remains absent. Incompatible original data preserved. No DEFAULTS/migrate financial change. Existing full-backup envelope preserved."
  },
  "derived_artifacts": {
    "allowed": [
      "src/js/manifest.json",
      "build-id.js",
      "dist/",
      "src/vendor/downloads/",
      "src/vendor/market-hours/runtime-payload.js"
    ],
    "generation_commands": [
      "python3 tools/rebuild_monolith.py --refresh-manifest"
    ],
    "manual_edit": "forbidden except manifest source script registration; sw.js is a maintained precache source, not an output of rebuild_monolith.py. Add only the three calendar/agenda script URLs, then rebuild its dependent fingerprint/portable."
  }
}
```
