# Independent menu-width stimulus review

**GO for the authorized focal and a fresh complete FULL; not final approval.** No material defect or weakened protection was identified in the exact applied patch. No tests, browsers, process signals or repository edits were performed by this review.

## Exact implementation and unchanged contract

Actual tools/ui_visual_quality_test.py bytes equal menu-width-proposal/ui_visual_quality_test.candidate.py (SHA-256 `ea5324e785181d8a1ef172b186980521ea591e7f089d7325cee9d00db4e1add0`). The diff against menu-width-before.py contains only wrapping_menu's deliberate stimulus: replace width:322px!important with min-width:322px!important, read actual bounding width and assert exactly322 before invoking the original rejected(menu_geometry) oracle. The proposal hash matches the approved CHG.

The stimulus assertion is outside rejected(), so a failure to inject322 cannot masquerade as successful rejection by the geometry oracle. menu_geometry, required_ids, validate_coverage, record and main are AST-identical to the preceding verifier. The actual width threshold remains max320+EPSILON, EPSILON0.25; the general tolerance remains2px. Gate SHA-256 remains074fd1d63154b50a1eefcbc3feac4c9f41e1d6356615bc089e04b5adffb2cd2a, including900-second timeout. The prior receipt has413 unique required IDs and all modules contributing those IDs are unchanged in the frozen-input comparison.

## Mechanism, restoration and boundaries

src/js/30-accounting/06-planning/03-ui.js:92 overwrites menu.style.width with at most320; lines103–106 attach the existing positioning observer to body subtree childList and selected attributes. The controlled actual-DOM proof records the old width stimulus reverting from322 to320 after a childList event and therefore being accepted. The candidate retains322 under that same observer and is rejected by the unchanged width-limit assertion. This establishes a concrete mechanism, not the unique historical timing trigger.

The prior original style string is still captured before mutation and restored unchanged by the existing finally block, including if the new stimulus assertion fails. No min-width is left by this patch once finally returns. The independent controlled proof also records a valid positive before, valid positive after restoration and unchanged financial snapshot. The app observer remains active. No financial model, application runtime source or gate changes were found relative to the preceding frozen inputs; JSON lists every frozen-input difference explicitly.

## Validation and history

The preceding actual UI receipt is PRODUCT_FAIL with413 cases executed,412PASS and only counterproof-menu-width failed, with the error that the deliberate violation was accepted. That is preserved historical evidence. The enclosing FULL was interrupted, so it does not establish102 completed checks. Its current command JSON records exit:null; use interrupted/incomplete unless a separate raw terminal receipt substantiates130.

The root is running the actual counterproof focal. This A0 review does not predeclare that focal PASS. Require successful existing positives and negatives, restored style/financial preservation evidence, then a fresh entire official FULL with all102 checks and413 UI cases passing. No cross-round aggregation, increased timeout, relaxed criteria or case omission. The dedicated CHG records human approval call_889e53bc46224663bae70e344c8cf821 for this exact stimulus-only change; final commit/merge/push still depend on their separate user authorization and the required gate.
