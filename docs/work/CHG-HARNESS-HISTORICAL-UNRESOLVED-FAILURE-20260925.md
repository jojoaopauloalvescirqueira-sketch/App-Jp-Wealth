# CHG-HARNESS-HISTORICAL-UNRESOLVED-FAILURE-20260925

```yaml
schema: jp-harness/chg/v1
change_id: CHG-HARNESS-HISTORICAL-UNRESOLVED-FAILURE-20260925
status: approved
approval_scope: local_implementation_and_independent_audit_only
objective: Define a narrow audit finding for historical non-reproducible PRODUCT_FAIL without changing raw test classification.
risk_level: N3
authority_required: A3
authority_basis: Explicit owner authorization in the 2026-09-25 request; reversible isolated control-plane work with byte backups, no production deployment or irreversible action.
target:
  root: /Users/joaopauloalves/.codex/harness-historical-unresolved-failure/20260925/product
  branch: codex/harness-historical-unresolved-failure-20260925
  baseline_sha: fcfbecba0e63aaa12fb0d7184fc43389c7592df0
external_canonical_source: /Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/1 - Suma & Estudo/99 - PROMPT/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md
scope:
  allowed_files:
    - external_canonical_source (only section 19 and directly necessary cross-reference)
    - AGENTS.md
    - docs/governance/CHANGE-PROCESS.md
    - docs/governance/IMPROVEMENT-ROADMAP.md
    - docs/templates/AUDIT-REPORT.md
    - skills/jpw-post-change-audit/SKILL.md
    - docs/work/CHG-HARNESS-HISTORICAL-UNRESOLVED-FAILURE-20260925.md
    - tools/historical_failure_audit_policy.py
    - tools/historical_failure_audit_policy_test.py
  forbidden_files:
    - tools/quality_gate.py
    - .github/workflows/quality-gate.yml
    - product candidate module-operational-visibility-20260925-r1
    - src/**
    - index.html
  allowed_actions: [read_only_inspection, bounded_control_plane_edit, synthetic_control_plane_tests, independent_N3_audit]
  forbidden_actions: [product_standard_or_full, candidate_reassessment, commit, push, PR, merge, deploy, real_data_access, gate_or_CI_bypass]
invariants:
  - Raw PRODUCT_FAIL receipt, count, exit status, historical audits and quality_gate.py remain unchanged.
  - Finding is N0/N1 noncritical only; N2/N3 and critical properties are excluded.
  - Independent auditor alone may issue at most AUDIT_PASS_WITH_DEBT after cumulative conditions; Human Acceptance and separate Git authorizations remain required.
  - Current product candidate and previous evidence remain frozen.
validation:
  - Synthetic T1-T14 plus negative controls, old/unsafe implementation regression, existing affected control-plane tests and structure/lint.
  - Diff and hash review, no product standard/full.
  - Independent adversarial N3 audit of this control-plane candidate.
rollback:
  backup_root: /Users/joaopauloalves/.codex/harness-historical-unresolved-failure/20260925/evidence/prewrite
  method: Restore exact prior bytes for the external Harness and scoped repo files, then rerun control-plane tests; stop new uses of the policy without rewriting past receipts or opinions.
  git: No commit or integration in this task; discard only this isolated worktree delta after separate authorization.
approved_by: Owner's explicit 2026-09-25 request; applies only to implementation, validation and audit of this CHG.
expires_on: [material_scope_change, source_identity_drift, irreversible_or_production_action]
```

## Baseline and before-write record

The official `main` and `origin/main` both resolved to `fcfbecba0e63aaa12fb0d7184fc43389c7592df0`. The principal worktree has unrelated untracked work and is excluded. This isolated worktree passed `agent_preflight.py --mode audit` and `--mode edit`; the historic material-freshness warning requires agentic impact assessment, not source cleanup. The product candidate is separate and must remain untouched.

The actual external Harness was identified by path, 59,261 bytes, mtime_ns `1788994689431367292`, SHA-256 `c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8`. Its initial 1,247 lines match the read-only project reference; the later appended material is a separate proposal, not active Harness policy. The `AGENTS.md` link currently points to a nonexistent old location. The external prewrite `MANIFEST.json` records this source, its byte-identical backup `master.original.md`, and backups/hashes of relevant repository files before editing.

## Behavioral contract and risk

Before: a required historical `PRODUCT_FAIL` remains a failed raw gate and the existing post-change audit instruction bars readiness while unexplained. After: a distinct auditor finding may permit `AUDIT_PASS_WITH_DEBT` under the narrowly defined cumulative conditions, while the failed raw gate remains failed. The exception is an audit judgment, not a new test result, waiver, automatic green gate or integration authorization. The default remains `BLOCKED`.

The risk is erroneous promotion of a defective product, especially if evidence is stale, causally unrelated, critical, or self-certified. Safeguards are N0/N1 noncritical restriction, source/candidate/receipt identity, independent current evidence, delta and risk review, hard negatives, independent auditor, structured debt, synthetic adversarial tests, unchanged raw classifier, freeze invalidation and separate Human Acceptance. The existing A4 default for other N3 work is not relaxed by this task-specific A3 authorization. A future truly A4 action needs its own authorization immediately before execution.

## Agentic impact

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. BASIS: this CHG changes a canonical audit norm consumed by agents and a post-change audit skill, and reconciles direct links/process/metrics. Source-of-truth, agents, skill, contracts, operational context and CI representations must be checked separately. Historical opinions and receipts are records of the past, not stale copies to rewrite. No product module, router, index or runtime contract is changed; no reindexing mechanism is known or authorized. The final independent audit will verify the current representations against this scope.

| Category | Impact | Local action | Basis |
|---|---|---|---|
| Canonical Harness | AFFECTED | REQUIRED | §19 now defines the audit finding; prewrite backup and source hash anchor the change. |
| Agent instructions | AFFECTED | REQUIRED | `AGENTS.md` linked a nonexistent location and needs the narrow promotion condition. |
| Audit skill | AFFECTED | REQUIRED | Its absolute unreadiness clause needed a reference to canonical §19.1. |
| Routing/registries | AFFECTED | NOT_REQUIRED | `SKILL-ROUTING.md` retains the general N3/A4 rule; this owner's A3 is confined to the named CHG, and no skill trigger changed. |
| Contracts and process | AFFECTED | REQUIRED | Audit report template, Change Process and metrics must distinguish raw result from audit disposition. |
| Operational context | AFFECTED | NOT_REQUIRED NOW | This is an unintegrated policy candidate, not current product state; historical records are immutable and the CHG itself represents the active task. |
| Product architecture/runtime | NOT_AFFECTED | NOT_REQUIRED | No product source, generated artifact, schema or browser entry point changed. |
| Index/vector/memory | NOT_AFFECTED | NOT_REQUIRED | No official index or reindex mechanism was identified for this source; no synthetic index is created. |

## Validation and integration boundary

The synthetic suite exercises T1–T14, plus malformed dossiers, explicit old capture gaps and independent Git/deploy authorizations. It contrasts the strict result against an intentionally permissive “one green focal” rule; negatives that fool that rule must be rejected. `tools/quality_gate.py` and `.github/workflows/quality-gate.yml` remain byte-identical to the prewrite backups. No product standard/full or candidate reassessment is authorized.

The pre-existing `agent_instruction_structure_test.py` synthetic controls pass, but its full current-context check reports `CHG/CTX root mismatch` and `CURRENT-STATE requires one full Source revision`. The same two failures occur on the untouched principal checkout; this CHG does not change that test, context or classifier. Its result remains failed, not PASS. The new suite and `preflight_context_test.py` are the focused control-plane evidence; the independent auditor must assess the historical structural-test limitation.

Read-only GitHub inspection on 2026-09-25 returned `Branch not protected` for main branch protection and `[]` for effective branch rules. The versioned Quality Gate workflow runs on push to main, pull request and manual dispatch, with the unchanged raw classifier. No required pre-integration GitHub check for this policy was observed. Record **INTEGRATION_ENFORCEMENT_GAP**: the policy's independent finding/Human Acceptance are process requirements, not a technical exception to the existing red gate or automatic branch-protection check. A future technical enforcement change requires its own CHG and authorization; do not alter CI/protection here.

Rollback remains exact byte restoration from the external prewrite backup and this worktree's scoped baseline files, followed by the synthetic control-plane suite and hash comparison. A rollback ends new use of §19.1 but never deletes prior historical receipts or audit opinions. No Git integration/publication is authorized by this CHG.

## Adversarial revision

The first frozen control-plane candidate `harness-historical-unresolved-failure-20260925-r1` is preserved externally with its fingerprint, full diff, test receipts and an independent `AUDIT_FAIL` opinion. The auditor demonstrated that `severity: "CRITICAL "` (trailing whitespace) was treated as formally eligible, and unknown severities were not rejected. That candidate remains rejected. The derived r2 narrows the validator to the five canonical severity literals, adds whitespace/unknown negative controls, and labels its CLI output explicitly as **one finding only**, never a whole-audit verdict. The raw gate, normative exception and product candidate are unchanged. r2 requires its own freeze, focused validation and fresh independent audit; r1 evidence is not rewritten.

The second frozen candidate `harness-historical-unresolved-failure-20260925-r2` and its independent `AUDIT_FAIL` are preserved externally. Its adversarial audit identified possible premature use: the canonical external Harness contains the new section while this branch is not integrated. The derived r3 adds a fail-closed activation condition to Harness §19.1 and direct consumers. The policy cannot be used until a later verifiable activation record binds this CHG's final policy hash/version and control-plane candidate fingerprint, independent N3 audit result, explicit owner Human Acceptance of that same candidate, authorized integration of repository references and explicit activation of the external Harness. This CHG's `status: approved` is authorization to implement and audit, not acceptance or effectiveness. No activation record exists in this task; real reassessment remains blocked. r3 requires a new freeze, control-plane tests and independent audit.
