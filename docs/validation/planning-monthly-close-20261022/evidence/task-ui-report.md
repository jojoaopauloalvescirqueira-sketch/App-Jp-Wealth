# Guided closure builder report

Candidate held for root verification. Root-authorized production edits started only after the RED notice (query6 missing-blocker failures and real browser missing-recovery/stale-draft failures). Workdir CloudDocs SOFTWARES & EAS/JP Wealth OS; branch codex/planejamento-patrimonial-20261020; HEAD ea15afc9c6a9c30cc69c5b98a8b85c85211ffb34. Existing dirty baseline preserved. No Git mutations, dependencies, real data, generated build, or publication.

## Scope and result

Only product files changed by this builder: src/js/30-accounting/06-planning/02-state.js (previewFinalizeMonth ONLY), 03-ui.js, src/styles/app.css. Private task reports/deltas are supplementary evidence. Root owns tests, canonical documentation, generated artifacts and final gates.

- previewFinalizeMonth returns additive blockers with codes MISSING_RESULT, earliest PREVIOUS_UNCONFIRMED, ALREADY_FINALIZED, FUTURE_MONTH, INVALID_CONTEXT and fallback NOT_COMPUTABLE. Original validation on a clone preserves errors/status/effective row and writes nothing. Successful previews have blockers:[]; invalid context does not invent a valid month.
- Finalization dialog captures immutable account/month. Missing result starts blank, uses previewResultInput for USD/percentage, explicit preview, explicit recordResult save, then a fresh closure preview with unchecked confirmFlows and separate finalizeMonth command. No assumed zero, planned contribution, financial formula or automatic closure. Zero opening defaults to USD and disables percentage using the same query.
- Cancel after confirmed result announces: O resultado foi registrado; o mês continua aberto. Successful finalization clears this cancellation state before closing.
- Previous-pending action preserves the modal draft, resolves any inline draft, navigates to earliest pending month, selects its year and temporarily displays period Todos; explanatory text describes filter changes. No financial write occurs.
- Shared modal drafts compare current context on opening, review and command. Stale approvals are cleared while inputs and choices stay preserved. Explicit Atualizar revisão is required before a fresh preview/confirmation. Native form review and legacy flow stages are invalidated/revalidated. Refresh refuses a different session, externally changed generation, replaced plan, removed/inactive account. A writer REFUSED/CONFLICT may record its exact locally observed successor generation as recovery metadata; only the explicit refresh adopts a fresh token. UNKNOWN is remembered per draft and locks save/refresh, including reopening.
- Reset dialog no longer silently renews a reused token. Changing the target account retargets only after the old token is verified current; reset choices remain displayed for re-review and approvals are cleared.
- Finalize draft backup exports its typed closureResultValue/Unit only as existing opaque unit/value keys. Internal inputs and the outer backup/provider format remain unchanged; previews/recovery markers are not exported as command authority; imported drafts remain read-only/copy-only.
- Scoped closure layout reuses the existing dialog bounds/scroll region. Focus is restored to live controls after rendering; native success navigation focuses the selected Consolidado tab.

Hooks: data-pl-closure-context; data-pl-closure-result; closureResultValue/closureResultUnit; actions closure-preview-result, closure-save-result; data-pl-closure-result-review; data-pl-closure-review; closure-previous[data-pl-previous-month]; data-pl-draft-stale; action draft-refresh.

## Identity and financial boundary

Current source SHA-256:

- 02-state.js: 53287b45ad24bf12b2f8a6beac4b324225f24e5656e2f19492708863e2c0c6c2
- 03-ui.js: d2d40067e1ed533b881af93c8b986687a1a344f4ef5a6e1dfcde897e75f76016
- app.css: 9ea40bc9c0b357694dd3860720fb0f5ec0d6b68602093170946ff8b695145627

builder-scope-proof.json compares directly against candidate-e08c-before.tar.gz: state outside previewFinalizeMonth byte-identical; entire 01-engine.js byte-identical. execute block SHA-256 unchanged 1e9eb53d273ba5fbb776047d02b00f7f5524b569b6596cfb7582ca8bea326818; applyClosure unchanged 91691a84d17de137b643b430e4b7dd206aa142cd7b0379077a546134d7b94d36. Baseline-relative builder-*.diff files preserve the exact approved delta; no unrelated baseline rewrite.

## Checks and preserved failures

- Preflight audit PASS; edit without --allow-dirty correctly BLOCKED on known dirty worktree. Explicit coordinated continuation with --mode edit --allow-dirty PASS (132 known baseline/root changes then).
- First bare node invocation ENVIRONMENT_ERROR (node not on PATH); corrected to existing bundled Node, no installation. query-green.log is the actual corrected execution: planning_state74/74 PASS, including old68 plus new6.
- Bundled node --check for state and UI PASS. Scoped git diff --check PASS. These are source checks, not browser or FULL acceptance.
- browser-green-attempt1 (36 cases) raw PRODUCT_FAIL, source_unchanged true: original8 regressions,3 counterproofs,16 layout/theme matrix cases PASS (27 total). Zero-opening default then required product fix, implemented via query. Eight native200 margin failures were fractional viewport oracle errors: bottom416.5 on actual428.5 viewport, while innerHeight rounded428. Root corrected the oracle to actual visualViewport without relaxing the12px margin. Raw receipt retained.
- browser-green-core (5 cases): four recovery/refusal/shared-flow cases PASS; zero-opening raw PRODUCT_FAIL. Manual matching fixture proved value USD and option.disabled true; Playwright option.is_disabled falsely returned false. Root strengthened oracle to actual disabled DOM property plus native keyboard rejection. browser-zero-recheck raw failure preserved as same TEST_HARNESS_FAIL diagnosis. No product change made to hide either oracle defect.
- Root owns the current37-case run after the two diagnosed oracle repairs and backup capture case, preservation of old240/default visual criteria, official generation, full suite, distributions/PDF and independent review. Those final results were NOT_RUN by builder and must use root receipts. Do not promote partial runs to final readiness.

## Security, limits and reconciliation

All new dynamic strings use h()/textContent. No new endpoint, storage key, provider schema, writer, dependency, timer/retry or financial calculation. Unknown outcomes are never automatically retried. Focus/layout are browser-tested only within the listed synthetic cases; human visual acceptance and real operator data remain separate.

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. BASIS: additive public query diagnostics and the approved guided workflow change the operational contract represented by PLANNING.md and active task/current-state/handoff. IMPACT mode was read; root owns the approved factual reconciliation in those existing documents. No agent/router/skill/authority edits or global memory changes are needed or made.

Rollback: use only builder-*.diff or matching per-file bytes in the baseline archive to reverse this builder delta; never reset the dirty worktree. Product held unchanged for root final verification after this report. Any later production edit invalidates affected evidence and hashes.

## Final bounded geometry fix and builder verification

Root close-current37 run correctly exposed a separate real native200 horizontal geometry defect after the fractional-height oracle repair: visualViewport.width712.5, innerWidth720, old dialog x12/right708 left only4.5px of actual right gutter and center3.75px from the visible center. Raw PRODUCT_FAIL receipt retained by root. This was a real product issue and was not reclassified as an oracle issue.

Authorized closure-only correction: #planning .pl-dialog[data-pl-submit="finalize"] uses left:50% and max-width:calc(100% - 2 * var(--pl-dialog-gutter)) so its fixed containing block excludes the outer scrollbar. All other dialog rules stay unchanged. No arbitrary pixel subtraction or relaxed oracle.

Builder final command: PYTHONDONTWRITEBYTECODE=1 .superpowers/sdd/2026-10-21-planning-monthly-inline/runtime/bin/python3 tools/planning_monthly_close_test.py --out .superpowers/sdd/2026-10-22-planning-monthly-close/browser-percent-bounds. Actual exit0; PASS37/37; source_unchanged true. Includes10 behavior/backup cases,3 counterproofs,16 layout/theme geometry cases and8 real native200 cases. Prior failures remain preserved separately. This focal result does not replace root final accumulated/default visual checks, official build/FULL, independent review or human acceptance.

Product source editing STOPPED at the updated hashes above. Root may now add independent identity-safety coverage and execute final gates.
