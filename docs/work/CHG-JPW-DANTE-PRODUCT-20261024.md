# CHG-JPW-DANTE-PRODUCT-20261024

Records conversational authorization; grants none.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "status": "approved",
  "target": {
    "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS",
    "branch": "codex/dante-guia-20261024",
    "baseline_sha": "a4bf278cd4dc38bbaa5b905ed17a79e33684fb67"
  },
  "approved_by": "human user",
  "approved_at": "2026-10-24",
  "approval": "PLEASE IMPLEMENT THIS PLAN: Dante — mascote e guia do JP Wealth; explicit branch authorization in conversation",
  "harness_source": {
    "sha256": "b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95",
    "sections": "12-14,19,24,28-30,36-49"
  },
  "rollback": {
    "source": "/private/tmp/jpw-dante-20261024/baseline.json and baseline-pending.zip; reverse own delta only"
  },
  "forbidden_actions": [
    "commit",
    "push",
    "merge",
    "publication",
    "dependency installation",
    "real financial data mutation",
    "global memory changes"
  ],
  "data": {
    "test_policy": "synthetic_only",
    "schema_change": "approved: guide progress v2 with mode only; no financial/profile schema change"
  },
  "acceptance_criteria": [
    "Dante default visual avatar with no profile write; custom avatar preserved",
    "Continuous optional journey and legacy API/progress preserved",
    "Typewriter 30 characters/second, reveal separate from completion, reduced motion and lifecycle cancellation",
    "No automated financial operations; current full gate, independent review, human acceptance separate"
  ],
  "approved_tests": [
    "profile, onboarding, learning foundation/controller/browser focals",
    "Dante behavioral/visual/distribution regression and counterproofs",
    "quality_gate.py --tier full"
  ],
  "change_id": "CHG-JPW-DANTE-PRODUCT-20261024",
  "objective": "Implement approved Dante plan",
  "risk_level": "N2",
  "authority_required": "A3",
  "scope": {
    "allowed_files": [
      "src/js/00-core/09-learning-progress.js",
      "src/js/40-app/09-profile-avatar-catalog.js",
      "src/js/40-app/09-settings-modal.js",
      "src/js/40-app/06-boot.js",
      "src/js/40-app/26-learning-catalog.js",
      "src/js/40-app/27-learning-view.js",
      "src/js/40-app/28-learning-guide.js",
      "src/styles/app.css",
      "assets/dante-*",
      "tools/rebuild_monolith.py: registered Dante assets only",
      "src/js/manifest.json",
      "sw.js: precache Dante image only",
      "generated build-id/index/portable/sw/payload outputs",
      "docs/branding/DANTE.md",
      "docs/architecture/LEARNING-GUIDE.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/BRIEF-DANTE-20261024.md",
      "docs/superpowers/plans/2026-10-24-dante.md",
      "docs/validation/dante-20261024/"
    ],
    "forbidden_files": [
      "skills/",
      "docs/normative/",
      ".github/",
      "financial writers and engines"
    ]
  }
}
```

Only deliberately replaced legacy expectations (default initials, 19 portraits, track-only central) may change. Preserve old safeguards and demonstrate representative counterproofs. Instruction routing is informational, restricted to mascot content and cannot grant authority.
