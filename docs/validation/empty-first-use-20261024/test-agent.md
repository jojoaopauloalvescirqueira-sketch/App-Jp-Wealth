# Empty first use — focal permanent

File: `tools/empty_first_use_test.py`
SHA-256: `1b9d746c1088f1c6de23c3c8c2873969afb0c75764692535541ea1bfe7510e57`

- Clean first boot never seeds S, localStorage, sessionStorage, or bootstrap state. Welcome is observed and closed with the actual button. Public requests aborted; local assets served unchanged with backlog256.
- Original RED:4seedaccounts;15preansweredchecklistanswers; additional RED:explicit new registration fabricated0balance before observation. Historical artifacts retained.
- Final GREEN:15/15 in `tests-green-final.json`. Covers boot, null/missing/zero, real navigation, reload/checkpoint, unanswered/partial/complete/N0checklist, accountcancel, deliberateUIregistration/reload,2tabconflict/draft, importvalidation, oldfacts+explicit0preservation/newbackuproundtrip, catalogs/prohibitions, malformed/JSONrecovery.
- Source counterproofs6/6 rejected with expected PRODUCT_FAIL and no localassetfailure/pageerror. Interception modifies only the actual HTTPsource response in disposable browser contexts, before boot. Same input and focal entrypoint. Details `tests-summary.json`.
- File frozen; no runtime/product/existingtests/runner/manifest edits by this agent. No dependency installation, Gitmutation, realdataread/write.

## Run

`.superpowers/sdd/2026-10-21-planning-monthly-inline/runtime/bin/python3 tools/empty_first_use_test.py --out /private/tmp/jpw-empty-first-use-20261024/tests-green-final.json`

Use a new output path; previous evidence is never overwritten. Counterproof adds `--only EMPTY-... --mutant <name>`. Available mutations in script `MUTANTS`.

## Limits

Headless modularHTTP only. Fourlayouts/themes/mobile/nativezoom/distributions/fullgate remain with parent. No livequoteacceptance, no humanvisualacceptance. Harness incidents preserved separately in summary, never counted as productRED.

## Independent-review P2 fixed — supersedes previous script freeze

Final script SHA-256: `afb8e0d97a8e9ef766d83640e79f751b4422f8bf60f8021a45b8b92bb351fc65`. Only aggregate taxonomy/counters/report changed; no behavioral oracle or timeout changes. `aggregate_cases` precedence: PRODUCT_FAIL, then ENVIRONMENT_ERROR, then TEST_HARNESS_FAIL; no selected cases is TEST_HARNESS_FAIL. Seven aggregation combinations PASS. Physical `--only nonexistent` returns TEST_HARNESS_FAIL and exit1, receipt `tests-taxonomy-exit-receipt.json`.

Fresh final GREEN15/15: `tests-green-taxonomy-final.json`; six fresh source counterproofs rejected with expected PRODUCT_FAIL/exit1. Same script and measured source hashes across all seven runs. Full inventory `tests-summary-taxonomy-final.json`; localized fix `tests-taxonomy-fix.diff`. Earlier artifacts preserved as historical.

## Visual classification regression — supersedes preceding freeze

Final script SHA-256: `3e2add32b49bac7d3c828e3fb4c7b4fac9c826ca24febcdf137779836ba4c986`. Added EMPTY-VISUAL-01 and CSS provenance; no earlier oracle or taxonomy removed. RED `tests-red-visual-01.json` proved text298px/client109px/nowrapellipsis at320. Product CSS owned by parent. GREEN `tests-green-visual-final.json`:16/16, with16states(320/390 x4layouts x2themes), full text ranges inside box2px, nooverflow, close44accessible, nofinancialmutation. Captures `tests-green-visual-final-artifacts/EMPTY-VISUAL-01-*.png`. Seven source counterproofs rejected including reintroduced CSSnowrap/ellipsis; same script and measured source hashes across all eight runs. Final manifest `tests-summary-visual-final.json`. Seven taxonomy combinations rerun unchanged. Native zoom/distribution/full gate remain with parent.
