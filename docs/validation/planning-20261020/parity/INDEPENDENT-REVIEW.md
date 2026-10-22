# Independent Planning parity review — 2026-10-20

Result: **PASS for the bounded source/browser and integrity comparisons below, with explicit limitations. No open P1 or P2 defect was found in this reviewed scope on the frozen candidate.** This is not Google runtime certification, human acceptance, publication approval, or a claim that every spreadsheet behavior was exercised here.

The reviewer changed only synthetic harnesses and receipts in this ignored `critic/` folder. No product source, owner data, Git state, external file, Google document, account permission or publication was changed by this reviewer.

## Exact candidate

Root: `/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS`.

Branch observed: `codex/planejamento-patrimonial-20261020`; base observed: `ea15afc9c6a9`. The initial audit preflight reported the preexisting 97-file delta and five manifest hash mismatches; this reviewer preserved the delta. The parent completed the official rebuild before the final freeze.

The four final complete harnesses and the separate cold-load probe all recorded these same hashes before and after execution:

| File | SHA-256 |
|---|---|
| `src/js/30-accounting/06-planning/01-engine.js` | `d698bf884e8dce907c255f20170f76e5919938cde755f575847f63ce7dbba5b2` |
| `src/js/30-accounting/06-planning/02-state.js` | `138b90185a9abaaef50f5cc83d86362592d5a8319ff471094a17f7ec223948f3` |
| `src/js/30-accounting/06-planning/03-ui.js` | `cf9542886f403e6bc6e5285cb066a2163bd3f1dc197f9bc5c3d2d6e081e82efa` |
| `src/styles/app.css` | `54067c089da590f8277f295b96e1ff5868ca96feaf6606414df3125ed01d3554` |
| `src/js/40-app/01-navigation.js` | `916bd1b5817b9859301c9972bde8def6823341d60608df0b76ce24f0f32e48ef` |

Build identifier read from the generated source: `8fc662bba73ffecf`.

## What was compared

The reference was the actual `STOIKUS_HTML_MULTI_` literal in `/private/tmp/stoikus-horizonte-consolidado-20261019/Formulario.verified.gs:519`, not a rewritten approximation. The harness asserts that its decoded HTML equals `../native-form-source.html` byte for byte. The decoded HTML hash is `cc79e59df3814f6e4d1cb91ea82c4e934fecef96a63fbe2557dc7decb2a31d4a`.

The original HTML/JS ran in Chromium with minimal synthetic `google.script.run` callbacks for configuration, quote reads and save success. The candidate ran its real DOM, commands and confirmed local document writer in fresh isolated browser contexts. All inputs, accounts, facts and quotes were synthetic. Browser fixtures blocked unknown external requests. The original Google save callback was simulated; the site's actual local save path was exercised.

Other source inspection used `Formulario.verified.gs` monthly prompts and normalization, `Reinicio.gs` reset planning, and the full inventory supplied at `../SCRIPT-INVENTORY.json`. This reviewer did not independently execute all ten Apps Script files or the complete Consolidado matrix; those checks belong to the parent's wider evidence, not to this report's PASS claim.

## Final evidence

- `form-source-compare.json`: actual original HTML versus actual candidate form. Current-cost prediction works with desired income blank. With USD1,000 initial capital, USD100 monthly contribution and Base profile from October 2026, both forms predict the USD150 current goal at month24 and USD300 desired income at month40; both show USD10,000 required capital. Review creates no account; back retains the typed answer; final deliberate confirmation creates exactly one candidate account. Both browser journeys recorded zero page errors.
- `fx-edit-review.json`: synthetic saved desired income of BRL10,000 at quote5 remains USD2,000 and displays quote5 before an explicit refresh, despite current quote10. Explicitly refreshing only desired income changes it to USD1,000, with required capital USD33,333.34 and duration74 months / November2032, matching the actual original form. Confirmation preserves the new quote10/USD1,000 snapshot. The independent current-cost snapshot remains quote5/USD1,000. The refresh-intent flag is not persisted.
- `stop-draft-review.json`: choosing a stop and then changing initial capital invalidates it. Closing/reopening cannot resurrect it through serialized draft fields; the review contains no stop, and the saved plan has `stopAfter=null`. No account is created before confirmation.
- `state-browser-review.json`: real DOM monthly result, contribution, withdrawal and closure; full reset; reconfiguration; and stale-review conflict. Scope changes and cancellation write no financial document. The reset preview names both affected accounts and displays the combined counts. Full reset uses one confirmed write and archives both complete prior plans. Reconfiguration retains every prior archive and reuses the reserved first active account identity only after confirmation. A stale reviewed new account is refused before a write after another synthetic edit. Monthly questionnaires and reviews do not write; each confirmed fact writes once. The actual monthly DOM journey verifies USD50 initial + USD3 result + USD10 contribution - USD2 withdrawal = USD61 confirmed balance.
- `startup-probe.json`: four separate concurrent cold Chromium loads of the frozen candidate. All observed `S=object`, `JPWPlanning.ui=object`, successful navigation, no page errors, no failed requests and no HTTP error responses.

The reproducible commands are the five Python harness files in this folder, run with `/private/tmp/jpw-pf-default-frozen-runtime-20261017/bin/python3`. The final executions are recorded in `final-form.log`, `final-fx.log`, `final-stop.log`, `final-state.log` and `final-startup.log`. Every final execution exited0. Assertions were added for regressions; no product test was weakened by this reviewer.

## Findings fixed and independently retested

1. **P2 — explicit BRL refresh retained the previous conversion.** Existing BRL10,000 at5 stayed USD2,000 even after requesting quote10, while the original yielded USD1,000. The fixed UI captures per-goal quote intent, and the state layer revalidates it against the current public quote. Final source/browser conversion, capital, duration and saved snapshot all agree. Current locations: `03-ui.js:183` and `02-state.js:90`.
2. **P2 — invalidated contribution stop returned from a closed draft.** Changing capital showed the invalidation warning, but stale serialized stop fields resurrected the previous date on reopening and zeroed projections after final confirmation. Those fields are now removed on invalidation. Final regression confirms no restored stop or zero override. Current location: `03-ui.js:304`; original behavior: extracted source JS `stopInvalidar`, line209.
3. **P2 — reset counts stayed on one account after selecting all accounts.** The combined result count and target names now refresh with the scope. Final real browser verification covers the displayed preview and the archived records. Current location: `03-ui.js:369`; original reference: `Reinicio.gs` reset `carregar` callback.
4. Review copy gaps reported earlier were repaired: converted USD amounts, BRL-to-USD desired-income equivalence, and duration/month in the review now carry the source information used in these cases.

## Failed attempt retained separately

One earlier pre-freeze attempt, launched concurrently with three other fresh browser harness processes, failed on `ReferenceError: S is not defined` during navigation. It remains **TEST_HARNESS_FAIL** in `transient-startup-failure.json`; it is not rewritten as PASS. The awaited bootstrap predicate does not assert state/API readiness. That predicate limitation is demonstrated, but the precise cause of the missing `S` in that attempt was not established. No full before/after receipt came from that failed attempt. The later frozen sequential retakes and four-browser probe are separate passing evidence; they do not erase it.

## Limits and platform differences

- **Authenticated Google UI, Apps Script execution, Google save/rollback, protected ranges, document locks, editor identity, owner-processing queue and triggers: NOT_RUN.** The source snapshot lacks `appsscript.json` and a live script-content connection; installed trigger/permission equivalence was not established.
- The approved independent site persists through its confirmed local document writer. The original performs Google spreadsheet operations and protected owner/editor processing. These are different execution and authorization systems.
- The approved site uses the Frankfurter/BCE daily USD/BRL reference. The original reads its spreadsheet quote from `Apoio!BG18`, with spreadsheet-specific FX behavior. Synthetic equal-rate comparisons prove conversion behavior, not live provider-price equality. USD/offline operation is intentional; it does not certify the original Google dependency.
- Browser print/report generation is a platform adaptation. This review did not execute `Code.gs` against Google or certify a pixel-identical native PDF/export path.
- The original HTML and the candidate are recognizable. Genuine blind A/B judging was not possible and was not claimed. No human comprehension study, owner acceptance or device-specific visual acceptance was performed. **Human acceptance: NOT_RUN.**
- No Git integration, deployment, live publication, cloud synchronization or owner-data migration was performed or certified.

Review completed at approximately 2026-10-20 19:16 UTC. This report supports the bounded source/browser and data-integrity conclusions above; the parent remains responsible for the complete requested scope and its required gates.

## R3 presentation-only appendix — final build 99c61f6fd77ec332

**R3 result: PASS for the reviewed CSS delta, form interaction and final geometry evidence.** The financial review above remains tied to its original `8fc662bba73ffecf` receipts. Those receipts and the separate `S undefined` failed-attempt record remain unchanged. This appendix does not replace them or claim that the full financial review was rerun.

The final CSS hash is `152b9dbc0ee67b21f2a6d398966adb009edbabf8eefca4c84e5804968809b582`. The entire previously reviewed CSS with hash `54067c089da590f8277f295b96e1ff5868ca96feaf6606414df3125ed01d3554` is retained byte for byte as the prefix; the delta appends 354 bytes. Its rules are restricted to `#planning` inside `@media(max-width:700px)`: allow tab text to fit, let the table/chart selector labels wrap, and give metric cards enough minimum width to stack when necessary. No content is hidden or truncated by this added delta. The exact comparison is in `r3/css-scope-review.patch` and `r3/css-scope-review.json`.

The engine, state, UI-controller and navigation hashes are still respectively `d698bf884e8dce907c255f20170f76e5919938cde755f575847f63ce7dbba5b2`, `138b90185a9abaaef50f5cc83d86362592d5a8319ff471094a17f7ec223948f3`, `cf9542886f403e6bc6e5285cb066a2163bd3f1dc197f9bc5c3d2d6e081e82efa` and `916bd1b5817b9859301c9972bde8def6823341d60608df0b76ce24f0f32e48ef`. This was independently checked against the original financial-review fingerprint. Before/after hashes in the R3 source-form and money-geometry receipts are stable.

### Failed intermediate CSS retained

The first R3 CSS candidate, `f8ccde58...` / build `7f44bb11e4010180`, still failed eight mobile matrix cases: shell scroll width 352 versus client width 350. Its tab/label fix had not addressed the projected-money text. Independent diagnosis showed the projection number had 168px scroll width inside a 140px column, extending to x372 beyond the shell's x370 edge. Hiding only the metric group in the disposable browser changed 352→350; hiding the charts did not. No product file was changed during that diagnosis. The failure was not approved or reclassified. Its evidence remains in `r3/mobile-overflow-probe.f8ccde58.json`, `r3/mobile-consolidated-before.f8ccde58.png` and the builder's `../layout/layout-results-final-attempt1.json`.

The final CSS stacks those mobile metric cards and wraps the real-chart selector label. The independent probe then measured 350/350 with no remaining overflowing non-table element. The original one-pixel test allowance was not increased.

### Final R3 checks

- The reviewer reran the exact original-HTML/source form comparison against the real candidate DOM at 1440×1000 and 390×844. Both final runs exited 0, recorded no page errors and preserved the source's independent goal predictions, profile choice, review/back answers and deliberate final confirmation. They use separate `r3/desktop/` and `r3/mobile/` receipts, so the earlier review receipts were preserved.
- The reviewer independently exercised long monetary values at desktop and mobile widths. The actual text ranges were fully inside the Planning surface, with no overlapping metric values and no outer horizontal overflow. Mobile was 350/350; desktop was 1124/1124. Full viewport screenshots `r3/consolidated-1440.png` and `r3/consolidated-390.png` were visually inspected; `r3/long-money-visual-review.json` contains the ranges and hashes.
- One existing desktop presentation limitation remains explicit: a very long projected value can paint beyond its own narrow grid column. In the reviewed fixture its text ended at x1401.42, inside the module's x1408 edge, with no clipping or overlap with another metric. The full viewport shows the complete value. The element-only metrics screenshot clips at the element capture boundary and must not be mistaken for a clipped user viewport. The appended mobile CSS does not alter that desktop rule.
- The reviewer read the builder's final `../layout/layout-results.json`: **24/24 PASS**, covering four navigation layouts, two themes, desktop 1440, mobile 390 and native browser 200% zoom; plus **8/8 full long-value mobile cases**. Its eight source hashes match the frozen candidate and its source-before/after check is true. The recorded test hash `0cd593442e4f3e2d0f9d5cf1ab024573dcb9d89f491c91b5101bf59ab1d1029d` matches the actual saved test. This reviewer inspected that receipt and test; the builder executed the 24-case matrix.
- Native browser zoom is evidenced by outer 1440 / inner 720 with CSS zoom 1, not by a CSS-scale substitute. The reviewer viewed `../layout/submenu-dark-390.png` and `../layout/native-200-dark.png`, as well as the independent desktop/mobile form and Consolidado captures. The final forms remain operable; mobile tab names wrap inside their buttons.

No open P1/P2 remains in this bounded R3 presentation review. Google authentication/runtime, human acceptance, Safari, physical touch and screen-reader acceptance remain NOT_RUN. The earlier platform/provider limits still apply. This appendix does not certify deployment or the parent's pending FULL gate.

## R4 tab-word readability appendix — final build d93561c064cf5f40

**R4 result: PASS for the narrow CSS/tab readability and interaction review.** All earlier reports, receipts and failures remain historical evidence. The R3 geometry gate checked button boxes but did not detect words split over several lines; R4 adds a direct per-word check rather than treating that earlier geometric PASS as proof of complete-word readability.

The frozen CSS is `66472afaa93c579abef8acf24c818ada79d78b541debda74b4ffd09bb94acf25`. The exact diff from R3's `152b9dbc...` baseline is in `r4/css-diff.patch`: inside the existing Planning-only mobile media query, the tab list becomes a two-column grid and tab `overflow-wrap` changes from `anywhere` to `normal`. No other style block changes. The four protected engine/state/UI-controller/navigation files still have the exact hashes recorded in the original financial review; `r4/tabs-review.json` records their independent comparison and stable before/after hashes. Financial harnesses were not rerun for this CSS-only change.

The independent reviewer exercised desktop 1440/light and mobile 390/light and 390/dark in fresh synthetic contexts with one explicitly initialized fixture plan. The four labels remain exactly “Comece aqui”, “Consolidado”, “Preenchimento mensal” and “Referência”. Each whole word occupies one DOM Range rectangle, both initially and when its tab is selected. Mobile has two rows of tabs, each button at least 44px high, with every measured word inside its button. Clicking every tab updates its selected state and the linked panel label. ArrowRight and ArrowLeft move selection and focus correctly. Switching the tabs leaves the fixture's financial aggregate unchanged and records no browser page errors. The complete receipt is `r4/tabs-review.json`.

The reviewer viewed `r4/tabs-390-light.png`, `r4/tabs-390-dark.png` and `r4/planning-1440-light.png`. The mobile captures show intact words in two columns; the desktop tab row retains its previous layout. This is agent visual inspection and DOM evidence, not a claim of owner acceptance.

The builder's final `../layout/layout-results.json` was independently read: **24/24 cases PASS**, **8/8 full long-value mobile cases**, and **576/576 measured words with exactly one rectangle each**. The observed source hashes are stable and match the frozen candidate. The recorded test hash `043dc022e4e85450297db378ff46ecbf21eaf8f25e47ba4364ca4848d3626d06` matches the saved test. Native browser zoom still records outer 1440 / inner 720 with CSS zoom 1. The builder executed this complete matrix; the reviewer performed the separate tab checks above.

One initial independent R4 harness attempt omitted an initialized plan and therefore tried to measure a deliberately hidden Consolidado tab. The unchanged UI source explicitly hides those tabs when there are no active accounts (`03-ui.js:59`). That setup failure is retained in `r4/fixture-failure.json`. The harness then created its explicit synthetic fixture through the confirmed command API and kept the same complete-word assertion; the product was unchanged and the failed attempt was not reclassified as PASS.

No open P1/P2 remains in this bounded R4 CSS/tab review. The prior desktop long-number column limitation is unchanged. Google runtime/authentication, human acceptance, Safari, physical touch and screen-reader acceptance remain NOT_RUN. The parent's FULL gate and publication decisions remain separate from this review.

## Final package delta appendix — build 443c1a59f2c1f46d

**Package-delta result: PASS. The new FULL was still running at the time of this appendix and is not claimed as completed here.** The previous `d93561c064cf5f40` FULL receipt independently records 91 PASS and zero failures; that result remains attributed to d935. The final package must have its own completed FULL evidence.

README and CHANGELOG are fingerprint inputs and embedded portable downloads. Updating their release text therefore changes the generated package ID even though application behavior is unchanged. This reviewer independently proved that the final delta from d935 consists of those two documents and the resulting generated metadata/document payloads. Neither root document nor a generated product artifact was modified by this reviewer.

The proof is in `package/package-review.json`, reproduced by `package/package_review.py`:

1. The d935 baseline inventory has 397 runtime paths. Exactly 10 generated paths differ; the other 387 paths match byte for byte. The four protected Planning/navigation JavaScript files and CSS `66472afaa93c579abef8acf24c818ada79d78b541debda74b4ffd09bb94acf25` are unchanged. All 257 recorded test hashes also match d935.
2. The ordered 327-path fingerprint list was independently reconstructed from the unchanged official builder's declared tuples, manifest script/resource order, download metadata and tail inputs. It equals the published input list. Applying the official path + NUL + bytes + NUL algorithm, including the exact index build-tag normalization, yields `443c1a59f2c1f46d` from current files. Substituting only the reconstructed d935 root README/CHANGELOG bytes yields exactly `d93561c064cf5f40`. Published raw source hashes match; before/after input hashes are stable.
3. Each of the eight changed download/market payload sidecars or JSON envelopes was decoded and reconstructed with only its `buildId` restored to d935. Every reconstructed file has the exact d935 SHA-256. Thus their archive, script, catalog and notice payload contents did not change.
4. Restoring only the build ID and preview-envelope digest in `build-id.js` reproduces the exact d935 file hash `3f58d4bf0baba4cee77c6d43f0f798b1120c098484e523b66e2b4391d0c53fcc`.
5. The final portable's embedded README and CHANGELOG base64 downloads decode byte for byte to the current root documents. Restoring only those two embedded document byte sequences plus the metadata values above makes the **entire portable** hash exactly `c8c6ed65fbd8189cc5ab74453309be167630239e010f4b4a2c7bb6b518d2180b`, the recorded d935 portable hash. This demonstrates that no other HTML, executable script, CSS, asset or embedded resource changed inside that generated artifact.

The ten generated paths are `build-id.js`, the standalone portable, six download registration sidecars (daily source, native kit, native pin, preview, source and Nocuda), the preview JSON envelope, and the market-hours runtime envelope. The release-document text diff is recorded separately in `package/project-docs.diff.json`. The root release text links the canonical validation record without embedding the changing package ID.

The historical validation README named `d935-README.md` is not the old root README. The final proof instead uses `project-d935-README.md` and `project-d935-CHANGELOG.md`; their provenance is independently bound by the exact reconstructed d935 fingerprint and portable hash. The earlier incomplete comparison, before those authentic project-document bytes were available, remains in `package/package-review-before-base-docs.json` and was not promoted to PASS.

This package-only change does not invalidate the preceding financial/visual conclusions because their exact application bytes are retained. It does not extend their scope: Google authenticated execution, human acceptance and the other stated limits remain NOT_RUN. No Git integration, publication, deployment or cloud synchronization was performed or certified. The final FULL result belongs to the parent's subsequent package-specific receipt.
