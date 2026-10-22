# Independent product review — bounded Planning controls delta

Result: **PASS for the finite product review below**, build `a9713063cd241820`. No remaining material product finding was demonstrated in the reviewed delta. This is not FULL, native acceptance, human visual acceptance, financial-rule homologation, commit, integration or publication approval.

## Candidate and scope

Repository: `/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS`; branch `codex/planejamento-patrimonial-20261020`; HEAD `ea15afc9c6a9` with preexisting work preserved. Audit preflight PASS with dirty-tree warning. Only UI/CSS delta versus preserved `candidate-0dc016-before.tar.gz` was reviewed; HEAD diff was not used as the baseline. Full bounded source diff: `source-diff.patch`.

- `src/js/30-accounting/06-planning/03-ui.js`: `8631ce88f133740f18b05ce6425b9413b93763d45ef48babd5df33de0e6c6664`
- `src/styles/app.css`: `1f3229bcfa93d903f6a10535d425cfee666d2277412ee246d71a50cc79ec3af2`

These hashes were unchanged before/after the final probe. `build-id.js` was fetched from the same local HTTP origin and matched the expected final build. Fresh Chromium contexts used only synthetic bootstrap fixtures and no owner browser profile. Scripts and receipts are local ignored audit artifacts; no product, versioned test, dependency, financial, profile or Git mutation was performed by this reviewer.

Criteria came from the human-approved `docs/superpowers/plans/2026-10-21-planning-controls-visual-quality.md`, not solely the implementation. Applicable root AGENTS, JP Engenharia and validation reference, local browser/test-triage/critical-review guidance and current UI visual contract were read. The relocated current Harness in `2 - TRABALHO/99 - PROMPT/9 - SOFTWARE/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md` was consulted for §§46–49.

## Observed final browser evidence

Command (with the task's explicit Chromium executable in `JP_WEALTH_CHROMIUM`):

`/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 .superpowers/sdd/planning-controls-visual-quality-20261021/product-review/probe.py`

`receipt.json`: **8/8 PASS**, no pageerrors.

1. Exact native Tab continuation, from first/middle/last menu actions: forward to `pl-tab-start`, reverse to the header PDF button. Menu closed in all six cases.
2. Twenty-five open/Escape cycles: relevant listener count returned to baseline19 every time; open count25; navigating away returned to19. Navigation closes the menu. This is a finite retention check, not a heap/GC proof.
3. Selecting Create closes the menu, opens the account form and Escape closes it. Dialog focus returns to the menu trigger.
4. ArrowUp from the trigger focuses the last enabled action; ArrowDown focuses the first.
5. Four viewports: 320×480, 390×320, 1440×480 and1440×900. Thirteen actions in the five approved groups/order, measured actual text inset at left, width≤320, gutters≥12, no trigger overlap, last action fully reachable by End/scroll.
6. Opening at desktop then resizing to320×480 remains positioned correctly; a controlled synthetic anchor position near the lower edge selects placement above. Synthetic anchor geometry is identified separately from normal layouts.
7. Synthetic form values12345/321 survive Profiles open/Escape, form close and reopen. No unconfirmed persistence-writer or Planning-command calls.
8. Actual CDP page scale2 changes visualViewport; the menu remains inside its visible bounds/gutters without pageerror. This is pinch/visualViewport evidence, **not native browser zoom200%**.

Independent capture/geometry command:

`/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3 .superpowers/sdd/planning-controls-visual-quality-20261021/product-review/capture-final.py`

`capture-receipt.json`: **3/3 PASS**, fresh contexts at320×700 light,390×844 light and1440×1000 dark. This second script independently declares the approved group/action list, measures native text Range against the declared left inset, checks menu bounds/no trigger coverage, measures close SVG ink center in the44×44 target, and measures the mobile forecast-jump text center. Applicable center deviations≤2px. No pageerrors.

Four screenshots were visually opened by this reviewer: `final-menu-320-light.png`, `final-menu-1440-dark.png`, `final-form-390-light.png`, `final-form-1440-dark.png`. They show coherent vertical groups, intentionally scrollable long menus, left text, symmetric close icon and aligned form controls. Additional normal-size and final-action screenshots remain beside them. Captures are evidence of these sampled states only.

## Source findings and protections

The bounded backup-to-final diff preserves existing action IDs and dispatch, dialogs/confirmation semantics, account data, questions, calculation sources, command payloads and draft storage. The menu change introduces grouped rendering, keyboard/placement and cleanup; close buttons reuse a symmetric SVG; CSS remains scoped to Planning. No financial computation, policy, profile, schema or persistence-path change was identified in this delta.

Observed draft/no-write behavior substantiates the relevant unconfirmed-interaction invariant. Creation/edit/multiple-account financial milestones, all13 command destinations and broader financial correctness were not reexecuted independently here; the builder's focal suites remain separately attributable evidence. This reviewer did not run FULL.

The lifecycle source cleans up on menu close, mount replacement, rendering/view switch, dialog opening and deactivation. Listener cleanup and real navigation were observed; all possible detach/DOM-replacement paths were not exhaustively simulated. No additional code-quality blocker was found in this bounded source review.

## Historical attempts retained

The first4d8 candidate probe is retained under `historical-4d8ccb4c0c3df656/`: it independently reproduced centered menu text and therefore was **PRODUCT_FAIL** for that historical candidate. Parent/builder separately diagnosed and fixed the Window/VisualViewport event-target issue; this reviewer attributes that diagnosis rather than claiming its original reproduction. Both final fixes were source-reviewed and the relevant final events executed with zero pageerrors.

`receipt-initial-probe-a971.json` preserves two raw exploratory assertions initially labelled PRODUCT_FAIL by the generic recorder. Their actual classification is **TEST_HARNESS_FAIL**: the synthetic margin moved the anchor completely offscreen, where product closure is correct; failure then skipped margin cleanup and contaminated the next viewport probe. No product change was made for these assertions. Corrected bounded anchor setup and a fresh run pass in `receipt.json`. Raw evidence is preserved and is not a second product defect.

## Limits

This review provides finite source/browser checks, independent from the builder. It does not substitute the permanent final matrix, all layouts, reduced-motion preference behavior beyond the chosen context setting, native200% browser zoom, full financial characterization, HTTP/offline/file/portable suites, FULL or owner acceptance. Those remain separately evidenced by their responsible executor. Human visual testing and acceptance are pending.
