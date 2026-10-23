# CHG-JPW-CALENDAR-AGENDA-TESTS-20261023

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
  "change_id": "CHG-JPW-CALENDAR-AGENDA-TESTS-20261023",
  "objective": "Add calendar/agenda coverage; reconcile approved monthly/weekly, header, exact three-module startup/precache and gate-catalog expectations while retaining historical checks, credential detection and independent counterproofs",
  "risk_level": "N3",
  "authority_required": "A4",
  "scope": {
    "allowed_files": [
      "tools/personal_agenda_test.js",
      "tools/monthly_economic_feed_test.py",
      "tools/calendar_agenda_test.py",
      "tools/calendar_recovery_test.py",
      "tools/calendar_distribution_test.py",
      "tools/calendar_visual_quality_test.py",
      "tools/ui_visual_quality_test.py",
      "tools/quality_gate.py",
      "tools/header_profile_test.py",
      "tools/smoke_test.py",
      "tools/usd_brl_quote_test.py",
      "tools/nocuda_tools_test.py",
      "tools/learning_guide_test.py",
      "tools/notes_launcher_test.py",
      "tools/finalize_session_test.py",
      "tools/research_navigation_test.py",
      "tools/exec_submenu_test.py",
      "tools/ff_news_cache_test.py",
      "tools/apple_experience_test.py",
      "tools/regression-memory.json"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "skills/",
      "docs/normative/",
      ".github/"
    ],
    "allowed_actions": [
      "additive tests and gate integration",
      "replace approved obsolete expectations retaining historical evidence",
      "independent verifier review and counterproofs"
    ],
    "forbidden_actions": [
      "weaken valid protections",
      "skip checks for green",
      "change timeout to hide failure",
      "close historical incidents automatically"
    ]
  }
}
```
