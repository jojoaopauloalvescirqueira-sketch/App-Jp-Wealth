# CHG-JPW-NOTIFICATION-ACTIONS-PRODUCT-20261022

The human request is the authority; this record grants none.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-NOTIFICATION-ACTIONS-PRODUCT-20261022",
  "status": "approved",
  "objective": "Implement the human-approved actionable notifications plan; presentation and readonly context only",
  "risk_level": "N1",
  "authority_required": "A2",
  "target": {
    "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS",
    "branch": "codex/notificacoes-acoes-20261022",
    "baseline_sha": "d517be0748f886085b3029c809bd68046e5c0f77",
    "preexisting_manifest": ".superpowers/sdd/2026-10-22-notification-actions/baseline.json"
  },
  "scope": {
    "allowed_files": [
      "src/js/40-app/18-notification-center.js",
      "src/js/10-domain/18-execution-board-model.js",
      "src/js/40-app/07-finalize-session.js",
      "src/js/30-accounting/06-planning/02-state.js",
      "src/js/30-accounting/06-planning/03-ui.js",
      "src/styles/app.css",
      "index.html",
      "docs/architecture/NOTIFICATION-CENTER.md",
      "docs/architecture/PLANNING.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/BRIEF-NOTIFICATION-ACTIONS-20261022.md",
      "docs/superpowers/plans/2026-10-22-notification-actions.md",
      "docs/validation/notification-actions-20261022/"
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

`index.html` é a fonte HTML canônica lida pelo builder (não um output reescrito por ele); sua marcação de notificações integra o escopo de apresentação. Portátil/sidecars/build-id permanecem exclusivamente gerados.

Finalização: somente hook opcional isolado de descarte da central em sessionResetAuxiliarySurfaces; nenhuma condição, escritor ou ordem transacional é alterada.

Proveniência de cotação: query aditiva readonly priceReferences no modelo de apresentação da Board, reusando prepareInstrument. Nenhuma precedência, cálculo, engine ou escritor alterado; evita construir história/grades para observar a referência efetivamente usada.
