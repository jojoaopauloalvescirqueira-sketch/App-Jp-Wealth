# CHG-JPW-NOTIFICATION-ACTIONS-TESTS-20261022

The human request is the authority; this record grants none.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-NOTIFICATION-ACTIONS-TESTS-20261022",
  "status": "approved",
  "objective": "Implement the human-approved actionable notifications plan; deliberate replacement of unread/activity/calendar expectations, permanent cases and counterproofs, independent review",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS",
    "branch": "codex/notificacoes-acoes-20261022",
    "baseline_sha": "d517be0748f886085b3029c809bd68046e5c0f77",
    "preexisting_manifest": ".superpowers/sdd/2026-10-22-notification-actions/baseline.json"
  },
  "scope": {
    "allowed_files": [
      "tools/notification_center_test.py",
      "tools/notification_visual_quality_test.py",
      "tools/module_availability_test.py",
      "tools/notification_efficiency_test.py",
      "tools/planning_state_test.js",
      "tools/ui_visual_quality_test.py",
      "tools/regression-memory.json"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "skills/",
      "docs/normative/",
      "src/js/30-accounting/06-planning/01-engine.js",
      "src/js/10-domain/00-forex-engine.js",
      "src/js/00-core/00-forex-policy.js",
      "tools/quality_gate.py",
      ".github/"
    ],
    "allowed_actions": [
      "bounded approved implementation",
      "synthetic browser and command tests",
      "factual scoped records",
      "independent review"
    ],
    "forbidden_actions": [
      "commit",
      "merge",
      "push",
      "publication",
      "financial migration",
      "new dependencies",
      "global memory configuration or mutation"
    ],
    "regressions_forbidden": [
      "financial writers and formulas",
      "real data",
      "backup schema",
      "existing unrelated checks"
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
  "data": {
    "test_policy": "synthetic_only",
    "schema_change": "forbidden"
  },
  "acceptance_criteria": [
    "active actionable count independent of reading",
    "structured context and stable identity",
    "no readonly writes/network",
    "planning explicit zero and dependency cases",
    "frozen operational suppression and global integrity preservation",
    "fresh final frozen full",
    "independent review",
    "human visual acceptance separate"
  ],
  "approved_tests": [
    "notification focal and efficiency tests",
    "planning state and affected integration",
    "ui visual quality matrix",
    "quality_gate.py --tier full"
  ],
  "rollback": {
    "source": [
      "restore only this task delta from baseline-recoverable.tar.gz, preserving preexisting work"
    ],
    "generated": [
      "official rebuild after restoring own source delta"
    ]
  },
  "approval": {
    "approver": "human user",
    "evidence": "PLEASE IMPLEMENT THIS PLAN: Notificações — central de ações relevantes; explicit branch reply Autorizar essa branch e preservar as alterações",
    "limits": "no Git integration/publication; no authority created by this record"
  }
}
```

Disponibilidade: substituir somente a expectativa antiga de manter itens operacionais de módulo congelado; conservar guardas de efeitos/navegação/suspensão. Verificador visual: casos aditivos da central na entrada existente, sem remover casos anteriores.
