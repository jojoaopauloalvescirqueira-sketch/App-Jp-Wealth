# CHG-JPW-DANTE-CONTROLS-20261024

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
  "change_id": "CHG-JPW-DANTE-CONTROLS-20261024",
  "objective": "Preserve guide/profile protections and add Dante proofs with narrow persona routing",
  "risk_level": "N3",
  "authority_required": "A4",
  "scope": {
    "allowed_files": [
      "AGENTS.md: narrow Dante content routing only",
      "tools/learning_*test.*",
      "tools/build_reproducibility_test.py: include new explicit asset in synthetic copy only",
      "tools/empty_first_use_test.py: default avatar visual assertion only",
      "tools/header_profile_test.py",
      "tools/profile_gallery_test.py",
      "tools/finalize_session_test.py: replace only the two obsolete no-image assertions with explicit Dante fallback and stronger identity privacy assertions",
      "tools/navigation_ia_test.py: await the shell's existing scheduled frame before its unchanged mobile-focus assertions",
      "tools/dante_*test.*",
      "tools/ui_visual_quality_test.py: add Dante cases retaining existing",
      "tools/regression-memory.json",
      "docs/work/CHG-JPW-DANTE-*-20261024.md",
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

Execution clarification after the first full run: the approved replacement of default initials also reaches the existing session-finalization profile tests. The two `img == 0` expectations are deliberately superseded by the new visual fallback, while saved personal profile, anonymous UI/memory, disabled controls, stale readers and reload assertions remain protected. The filename omission in the initial inventory is reconciled here within that same approved behavior, not as authority to change session cleanup or financial logic. The proposed test delta received independent review and 24 counterproof executions (six violations at four checkpoints). The unrelated calendar lifecycle defect remains outside this contract and has a separate unapplied proposal.

The approved keyboard/focus verification also requires observing the shell after its already scheduled animation frame. The navigation test receives one native-frame rendezvous, preserving all geometric, focus, drawer, error and target assertions; no runtime behavior, tolerance, retry or sleep is introduced. The five-context characterization and missing-focus counterproof received independent review. This is a test synchronization repair under the existing verification scope, not a change of navigation requirements or authority.
