# CHG-JPW-EMPTY-FIRST-USE-PRODUCT-20261024

Records human authorization; grants none.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "status": "approved",
  "target": {
    "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS",
    "branch": "codex/primeiro-acesso-vazio-20261024",
    "baseline_sha": "a4bf278cd4dc38bbaa5b905ed17a79e33684fb67"
  },
  "approved_by": "human user",
  "approved_at": "2026-10-24",
  "approval": {
    "evidence": "PLEASE IMPLEMENT THIS PLAN: JP Wealth — primeiro acesso realmente vazio; Autorizar essa branch e preservar todas as alterações",
    "limits": "Only approved plan, preserve existing candidate and saved data; no commit/merge/push/publication/dependencies/formula changes."
  },
  "rollback": {
    "source": "/private/tmp/jpw-empty-first-use-20261024/baseline.json; baseline-pending.zip; baseline-sources; reverse own delta only"
  },
  "harness_source": {
    "sha256": "b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95",
    "sections": "12-14,19,24,28-30,36-49"
  },
  "approved_tests": [
    "empty_first_use_test.py",
    "affected accumulated focals",
    "quality_gate.py --tier full"
  ],
  "acceptance_criteria": [
    "No pre-created user facts/answers on clean first use",
    "Explicit null differs from zero and malformed/missing input",
    "Saved bases/history/guards preserved",
    "Current RED/GREEN, counterproofs, independent review and full gate"
  ],
  "data": {
    "test_policy": "synthetic_only",
    "schema_change": "explicit null accepted for documented absent values; no automatic data deletion"
  },
  "forbidden_actions": [
    "commit",
    "merge",
    "push",
    "publication",
    "real-data mutation",
    "global-memory mutation",
    "dependency installation"
  ],
  "change_id": "CHG-JPW-EMPTY-FIRST-USE-PRODUCT-20261024",
  "objective": "Empty initial facts and unanswered checklist with preserved legacy saved data",
  "risk_level": "N2",
  "authority_required": "A3",
  "scope": {
    "allowed_files": [
      "src/js/00-core/03-default-state.js",
      "src/js/00-core/04-persistence.js",
      "src/js/00-core/05-helpers.js",
      "src/js/00-core/01-risk-profiles.js",
      "src/js/10-domain/04-stop-statistics.js",
      "src/js/20-ui/03-main-render.js",
      "src/js/20-ui/07-chart-crosshair-tooltip.js",
      "src/js/20-ui/08-input-bindings.js",
      "src/js/20-ui/31-forex-accounts.js",
      "src/js/20-ui/28-fx-consolidated.js",
      "src/js/40-app/04-onboarding.js",
      "src/js/40-app/05-wipe-all.js",
      "src/js/40-app/07-finalize-session.js",
      "docs/architecture/STATE-SCHEMA.md",
      "docs/recovery/DATA-RECOVERY.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/BRIEF-EMPTY-FIRST-USE-20261024.md",
      "docs/work/CHG-JPW-EMPTY-FIRST-USE-PRODUCT-20261024.md",
      "docs/work/CHG-JPW-EMPTY-FIRST-USE-TESTS-20261024.md",
      "docs/superpowers/plans/2026-10-24-empty-first-use.md",
      "docs/validation/empty-first-use-20261024/",
      "src/js/40-app/24-fx-consolidated-import.js",
      "src/styles/app.css"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "skills/",
      "docs/normative/",
      "src/js/00-core/00-forex-policy.js",
      "src/js/10-domain/00-forex-engine.js"
    ]
  },
  "derived_artifacts": {
    "manual_edit": "forbidden",
    "generation_commands": [
      "python3 tools/rebuild_monolith.py --refresh-manifest"
    ],
    "allowed": [
      "build-id.js",
      "src/js/manifest.json",
      "dist/",
      "src/vendor/downloads/",
      "src/vendor/market-hours/runtime-payload.js"
    ]
  },
  "bounded_consumer_reconciliation": "The approved null-for-uninformed-balances contract also applies to the new/re-registered account initializer (sini/satu). Existing saved values are untouched; no formula or observation command changes. Identified during creation regression; RED required before patch.",
  "bounded_visual_reconciliation": "Mobile visual inspection confirmed new unanswered status text clipped by inherited nowrap/ellipsis at320/390. Add only local #chClass wrapping; preserve all other CSS and calendar changes. Real RED and permanent counterproof required."
}
```
