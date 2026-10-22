# Planning — independent usage review of candidate 7e8cc9b03b5dca40

The exercised user journeys work on this candidate: starting/configuring and canceling, choosing among accounts, reading projections and goals, registering and correcting monthly facts, closing/reopening, archive/reset, backup and reload. No additional product defect was demonstrated by this exploration. This is scoped evidence, not universal absence of defects or human acceptance.

One permanent test expectation is obsolete under the approved stale-draft recovery contract. The original three-tabs run is retained unchanged: 9 cases PASS, stale-choice reports TEST_HARNESS_FAIL after trying to click a deliberately disabled button. Its runner labels the aggregate PRODUCT_FAIL; that label does not identify a demonstrated product defect. A separate actual recovery probe confirms the new explicit review path works. Root owns the narrow test adaptation and its subsequent verification; this report does not claim it ran that adapted test.

## Authority, candidate and execution boundary

Read first: task brief and approved 22 October plan; then AGENTS, PLANNING, local jp-ai-engineering, preflight, change-control, critical-review and browser-verification skills. Audit preflight passed on branch codex/planejamento-patrimonial-20261020, HEAD ea15afc9c6a9, 133 existing changed entries. Existing modifications were preserved.

Only this exploration directory was written by this explorer. No product, documentation, tests, real operator data, user browser profile, Git operation, package installation or external network request was used. Python is the existing task runtime; Chrome for Testing is the existing chromium-1223 executable. Each browser context has isolated synthetic state and bootstrap fixtures that abort unrecognized external requests. HTTP fixtures use ephemeral localhost ports. No FULL was run here.

`focal-commands.json`, `broad-command.json`, `practical-receipt.json` and `stale-receipt.json` record actual commands/times or case evidence and before/after hashes. Product sources, CSS, build-id, index and portable artifact are unchanged across focal and broad execution. The two exploratory probes separately verify their source/build fingerprints before and after. Build identity is 7e8cc9b03b5dca40.

## Actual user tasks and outcomes

| User task | Expected behavior and actual observation | Outcome / evidence |
|---|---|---|
| Enter Planning, read guidance, configure first account | Only three public pages; start gate before first confirmation; native questions/profile selection; preview and back do not write; deliberate confirm creates one account. Observed. | PASS, parity/all, 132 logged assertions across all parity journeys |
| Several accounts, create/edit/cancel | Choice begins unselected, edit requires explicit account, selected account draft restored, cancel does not change All-account filter or saved facts; confirm changes only intended second account. Observed. | PASS, three-tabs cases choice/choice-save/single |
| No current FX quote | BRL forecasts explicitly say quote pending; no false zero and no account creation; unchanged BRL goal can retain its original snapshot offline. Observed. | PASS, three-tabs pending-quote and broad-ui offline metadata cases |
| Read All/accounts, year, tables and graphs | Projection year and chart period remain independent; all 120 months retained. Additional practical probe selects all 5 table modes, all 4 realized modes, and every available period for All and both accounts. No aggregate write. Projection chart raster 901×275, 196–198 distinct colors, 4 paths with actual geometry. | PASS, parity consolidated/monthly; practical case all-account-selector-and-real-chart-roundtrip |
| Understand multi-account income goals | Help explains account scope and personal goals; no aggregate financial write. | PASS, practical multi-account-goals-help |
| Register result, contribution and withdrawal | Cancel retains draft, reopened draft keeps exact USD input; backup includes readable draft without token; explicit result/contribution confirm followed by flow confirmation closes the month. Independent expected balance 125 observed. Withdrawal BRL remains optional. | PASS, broad-ui.log |
| Reopen and correct | Reason required; reopening invalidates closure; contribution correction preserves original value by ID; zero-dollar correction is rejected without altering facts/history. | PASS, broad-ui.log |
| Edit future assumptions | Explicit zero and blank remain distinct; blank rate stays provisional, blank contribution remains visually blank and calculates zero without ledger entry; edits save deliberately. | PASS, broad-ui.log |
| Use Stoikus and history | Operational menu entries remain reachable; retired actions absent; empty reset history is readable and writes nothing. | PASS, three-tabs public and practical empty-reset-history |
| Reset a selected account / review all-account reset | Account reset requires exact phrase plus separate unchecked understanding; archives old plan, clears effective facts and preserves financial reference. Changing reset scope updates counts and clears old confirmation; cancel preserves facts. | PASS, broad-ui and parity reset-counts |
| Open Notes from monthly | Click, Enter and Space open Notes, close returns focus to launcher; Planning financial snapshot unchanged. | PASS, practical notes-from-monthly |
| Navigate away, backup, preserve session and reload | Dashboard roundtrip changes no Planning facts; actual backup serializer contains exact aggregate; session preservation functions carry the exact aggregate; real page reload retains both active accounts and confirmed facts. | PASS, practical shell-away-return/actual-backup-serialization/session-preservation-contract/reload-active-accounts |
| Dialog proportions and keyboard/mobile access | Five permanent centering/money/header/pending-copy/stop-legend regressions pass; existing broad UI covers mobile preview focus/scroll and 390px surfaces. | PASS, proportions-regressions 5/5 and broad-ui 136 logged assertions |

Assertion totals are execution detail, not a measure of complete coverage. Parity is 9 user journeys. The practical probe contains 9 named cases; stale recovery has 3. Source reads and synthetic setup commands are not represented as user UI interactions.

## Stale draft: protective refusal and usable recovery

Reproduction: create two synthetic accounts; open second account through the form chooser; type “Rascunho antigo”; Escape; externally update that same synthetic account; reopen original draft. Expected approved behavior is to preserve draft and reject old consent, requiring explicit Update review. Observed: original baseReference retained, text preserved, Revisar alterações disabled, explanatory banner and Atualizar revisão visible. Screenshot `stale-review-required.png` was visually inspected: warning, recovery control and disabled review are legible.

The original test at `tools/planning_three_tabs_test.py:194` tried to click disabled Revisar alterações twice. Playwright timed out after 30 seconds. First-run receipt and trace remain in `three-tabs.json` and `three-tabs.log`. Classification: **TEST_HARNESS_FAIL** caused by an approved deliberate change of interaction, rather than failed financial protection or poor recovery.

Counter-evidence against a recovery defect: `stale_probe.py` actually clicks Atualizar revisão, confirms the draft text remains unchanged and the financial snapshot is byte identical, clicks review with zero writes, then deliberately confirms. Only the intended second account changes; the first remains byte identical. `stale-receipt.json` is PASS with all 3 cases and unchanged source/build hashes. No authorization is silently refreshed.

## Probe correction and evidence integrity

The first practical probe included an unjustified assertion that the collapsed All-account page body must contain the literal word “metas.” It failed after the selector/chart case; the initial transcript is retained as `practical.log`. That word is not a required visible contract. The probe was corrected only inside this exploration directory to exercise actual goal help and assert visible dialog plus unchanged facts. Completed evidence is `practical-2.log` and `practical-receipt.json`. This probe error is TEST_HARNESS_FAIL, not a product finding.

## Limits and disposition

New same-window guided closure matrix, distribution/portable/offline/PDF and final FULL belong to root's separate execution. This explorer reused existing close/reopen journeys but does not substitute them for the new closure matrix. Native zoom, the full visual matrix, Safari, assistive technology, physical touch, real user data, cloud sync, deployment and user acceptance were NOT_RUN here. Session preservation was checked through actual functions and serialized output; the finalization UI was not clicked by this explorer. Notes opening/focus boundary was covered, not note editing semantics. The unrelated historical PDF footer remains open debt and was not closed by these runs.

Recommended action: retain the protective stale-draft behavior; adapt only the outdated test interaction under the separate test CHG, preserving original case identity and no-overwrite invariants. Use root's final frozen FULL and independent review before claiming technical readiness. Human acceptance remains separate.
