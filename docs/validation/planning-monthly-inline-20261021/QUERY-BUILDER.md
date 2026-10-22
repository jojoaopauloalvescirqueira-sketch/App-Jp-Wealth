# Task 1 — read-only monthly result input preview

Scoped implementation/spec verdict: **PASS**, pending independent review before Task 2. This is not final package readiness: generated build, browser integration, FULL and human acceptance are **NOT_RUN** by this worker and remain the root task's later gates.

## Identity, authority and understanding

- Actual repository/workdir: `/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS`.
- Branch: `codex/planejamento-patrimonial-20261020`; HEAD: `ea15afc9c6a9c30cc69c5b98a8b85c85211ffb34`.
- Authority: the root's explicit assignment of Task 1 from the approved human monthly-inline plan, with reuse of the existing dirty candidate. Root confirmed that the 125 entries at this worker's preflight were the original 122 plus the new approved plan and two CHGs. This worker did not infer authority from recovered documentation.
- Product purpose: local/PWA financial organization and planning; integrity of facts and confirmed writes takes priority over easier entry. `06-planning` owns the 120-month calculation/read models and confirmed commands; this addition only adapts the input representation of a result for an existing read-only preview.
- Before: results can be previewed through `previewFlow({kind:'result',usd})`; no query accepts percentage points. After: `previewResultInput({accountId,month,unit,value})` reads the current opening balance, converts percentage points to USD cents when requested and delegates the financial candidate to that same existing preview path.
- Existing rules/consumers: monthly opening precedes that month's end-of-month contribution/withdrawal; the engine derives realized rate as result USD/opening. UI will consume the new query; later confirmation must still use existing `recordResult` in USD with a fresh context token. No formula, writer, stored financial schema or financial rate field changed.
- Scope: only `02-state.js`, the new result-input test, one invocation in the existing state test, and own ignored task artifacts. No UI/engine/other tests/contracts/generated files, instruction files, dependency installation, real browser profile/data, global memory or Git mutation.
- Original source/test bytes are saved in `task1/02-state.js.original` and `task1/planning_state_test.js.original`; rollback is limited to this exact own delta and is not performed automatically. The root's verified recovery archive is separate, inherited evidence.

Read sources: `AGENTS.md`, required local skill entries/relevant engineering references, project/core map excerpts, `PLANNING.md`, relevant state/storage/recovery/security contract excerpts, engine/state source, existing state tests, the task brief, and source-authority record. The feature Atlas has only the older FX-planning/Scenario Fan relation; the current independent planning contract and actual source supply this task's domain context. No external financial rule was added. The root's canonical Harness relocation/hash verification is inherited evidence from `source-authority.json`, not a personal claim of this worker reading the full Harness.

## Exact implementation and adapters

`src/js/30-accounting/06-planning/02-state.js` adds `previewResultInput` and its query export only:

1. Require an input object, safe fields, exact unit `PERCENT` or `USD`, and a finite primitive number. Empty/null/string values remain invalid; zero is not coerced from absence.
2. Reuse envelope/account validation and `monthInPlan`, including current/past-only factual entries and account horizon.
3. Read a fresh opening from the unchanged engine timeline of the current account plan. Percentage input requires a finite positive opening; missing opening stays unavailable.
4. Convert percentage **points** using `Math.round(openUsd * (value / 100) * 100) / 100`. USD is passed through unchanged to the existing strict-cent rule.
5. Delegate the candidate to unchanged `previewFlow({accountId,month,kind:'result',usd})`. Preserve its result/error shape and add `openUsd`, `inputUnit`, `inputValue` to the delegated result. Preliminary input/domain errors use the existing `INVALID/errors` shape. `rate` remains the fractional rate produced by the financial engine, including the effect of rounding USD cents.

`tools/planning_monthly_result_input_test.js` adds 14 permanent synthetic cases, runnable alone and exported for the existing state entry. Its `JPW_PLANNING_STATE_SOURCE` override supports testing an isolated mutated source copy without changing the live product.

`tools/planning_state_test.js` gains exactly one registration line before its existing runner. All 54 prior case bodies, IDs, assertions and execution stay byte-identical.

The exact own-only before/after diff is `task1/task1-only.diff`. `task1/preservation.json` records actual byte comparisons: remove the new function/export and the source equals its original; remove the one registration line and the existing state test equals its original. Thus every existing writer, `previewFlow`, context/token/reset code and command implementation is byte-preserved. The engine SHA remains unchanged.

## Specification coverage

| Requirement | Permanent cases | Observed |
|---|---|---|
| 1000 × 3% = 30 USD, existing preview shape, fractional rate | PLRESULT-01 | PASS |
| 112.55 × 3% = 3.38 USD, rate 3.38/112.55 | PLRESULT-02 | PASS |
| Valid losses, explicit zero, -100% boundary; negative closing balance refused | PLRESULT-03 | PASS |
| USD zero/positive/negative cents preserved; fractional cents/overflow refused | PLRESULT-04 | PASS |
| Zero opening disables percent, including 0%; USD zero retains the existing rule | PLRESULT-05 | PASS |
| Missing/inactive account; no aggregate creation | PLRESULT-06 | PASS |
| Current month accepted; future/outside horizon/invalid month refused | PLRESULT-07 | PASS |
| Incompatible envelope preserved and refused | PLRESULT-08 | PASS |
| Empty/null/string/nonfinite/other types and invalid units refused | PLRESULT-09 | PASS |
| Repetition, returned-copy isolation, same state/history/token and no writer/storage/network calls | PLRESULT-10 | PASS |
| Fresh opening after capital change | PLRESULT-11 | PASS |
| Fresh dependent opening after prior confirmed result change | PLRESULT-12 | PASS |
| Preview independent of writer availability; later writer refusal preserves facts | PLRESULT-13 | PASS |
| Unavailable opening stays unavailable rather than becoming zero | PLRESULT-14 | PASS |

PLRESULT-13 uses a synthetic writer to isolate the new read query. The preserved 54-case state suite also executes the existing actual confirmed-writer extraction and refusal/UNKNOWN/conflict regressions; no new browser integration or multi-tab proof is claimed.

## Actual executions and receipts

Environment: Node `v24.19.0`, binary `/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node`; receipt wrapper Python `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3`. Unit tests set `JPW_NODE`, Node on `PATH`, `JP_WEALTH_CHROMIUM` to the existing Chrome-for-Testing path and `PYTHONDONTWRITEBYTECODE=1`. No installation occurred. All commands used the explicit repository workdir above. Node command exits are the subprocess exits recorded in JSON, separate from the successful receipt wrapper process.

| Execution | Actual result | Classification | Receipt/logs |
|---|---|---|---|
| `tools/agent_preflight.py --mode audit --json` | exit 0 | PASS | `task1/preflight-audit.*.log`, `task1/before.json` |
| `tools/agent_preflight.py --mode edit --allow-dirty --json` | exit 0, approved dirty reuse | PASS | `task1/preflight-edit.*.log`, `task1/before.json` |
| `node tools/planning_monthly_result_input_test.js` before product edit | exit 1; 0/14 pass, all fail the assertion that the absent query must exist | PRODUCT_FAIL, expected RED | `task1/red.receipt.json`, `task1/red.stdout.log`, `task1/red.stderr.log` |
| Same new-test command after the additive query | exit 0; 14/14 pass, empty stderr | PASS | `task1/green.receipt.json`, `task1/green.stdout.log`, `task1/green.stderr.log` |
| `node tools/planning_state_test.js` | exit 0; 68/68 pass: all 54 previous + 14 new | PASS | `task1/state-green.receipt.json`, `task1/state-green.stdout.log`, `task1/state-green.stderr.log` |
| Existing state entry with isolated wrong-percent source override | exit 1; 62/68 pass, 6 new numeric cases fail | PRODUCT_FAIL, expected counterproof | `task1/counterproof.receipt.json`, `task1/counterproof.stdout.log`, `task1/counterproof.stderr.log` |
| `node --check` on all three owned source/test files | all exit 0 | PASS | `task1/after.json`, `task1/*-syntax.*.log` |
| Scoped `git diff --check -- <three owned files>` | exit 0 | PASS within tracked diff coverage | `task1/after.json`, `task1/diff-check.*.log` |

RED used unchanged original source SHA `138b9018…`; the new test bytes and old-test registration bytes are identical between RED and GREEN. All failing attempts are retained. The full state suite's stderr is the preexisting deliberate `synthetic quota` error exercised by PLSTATE-17, whose assertions pass; it was not suppressed or relabeled as a new regression.

Counterproof changes only the ignored source copy `task1/02-state-wrong-percent.js`, replacing `/100` by `/1000` for the conversion. The same permanent test module runs through the existing state entry. PLRESULT-01 rejects this with `AssertionError: 3 !== 30`; PLRESULT-02 also checks actual numeric conversion independently. The live source was hash-checked unchanged after the counterproof. The six expected failures are not treated as a successful product execution.

Initial/final branch/status/full-diff metadata and raw outputs are preserved under `task1/`. Initial complete diff is large because it includes preexisting product/generated work; `task1-only.diff` is the readable task delta. Status changed only by the new result test and the root-owned new validation directory during this worker's interval. Some preexisting planning files are already untracked; their own changes are therefore verified by byte comparison and the saved own-only diff, not solely by `git diff`.

## SHA-256 identities

| File | Before | Tested current |
|---|---|---|
| `src/js/30-accounting/06-planning/02-state.js` | `138b90185a9abaaef50f5cc83d86362592d5a8319ff471094a17f7ec223948f3` | `989fa97a83cc3ddcfee4750074dd1416a967648a22463dd17316a59e96a84719` |
| `src/js/30-accounting/06-planning/01-engine.js` | `d698bf884e8dce907c255f20170f76e5919938cde755f575847f63ce7dbba5b2` | same, unchanged |
| `tools/planning_state_test.js` | `4a8dd009f2ec08b3b7fdba57176a22f7cfc00442f937c653d1eab4b0e9ec76fb` | `237aba7f24068fcf7cd159cd0895e3adda6d2ffe18dfeea1f3cc8218a6878de3` |
| `tools/planning_monthly_result_input_test.js` | absent | `58bbaa3d84c66e2cb2deecb386d373a89305f3125e0c00aa864748f6fd0a0273` |

Full source/test/environment/process receipts are machine-readable in `task1/before.json`, `task1/after.json` and per-execution `*.receipt.json`.

## Concerns and remaining gates

- No blocking scoped defect found. The query intentionally returns the realized fractional rate after rounding USD; for the 112.55 fixture it is `3.38/112.55`, not exactly `0.03`. Consumers should display/confirm the returned USD total and use the existing command/context guard.
- No new persistent fields, keys, migration, storage/network API, dependency or writer introduced. Input validation remains fail-closed; errors are text and no DOM is created here.
- The query export changes a public interface consumed by later UI and documentation. **AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. BASIS:** the approved plan/contracts describe the new public query; architecture/current-state/test registry/final verification records must reflect it. Their reconciliation belongs to the root's assigned scope, and this worker did not edit them or instructions.
- Independent Task 1 review: **NOT_RUN** by this builder, required before Task 2. Official rebuild/FULL/browser/HTTP/offline/file/portable/PDF/final package freeze: **NOT_RUN** by explicit Task 1 sequencing. Human acceptance and Git/publication remain separate.
