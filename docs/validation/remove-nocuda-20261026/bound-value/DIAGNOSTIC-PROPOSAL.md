# A0 diagnostic proposal — compact monthly value reads

Status: source-supported optimization hypothesis, not an implemented fix or a proven explanation of the entire visual timeout. No tests, browser actions, repository writes or process signals were performed for this diagnosis.

## Evidence and bound

The previous FULL reached the unchanged 900-second visual deadline (900.033s); its last printed case was compact-native200-submenu-dark, without the final nine completion receipts. The earlier complete UI run passed 413 cases in 835.103s. Neither run isolates a particular source of slowdown. The parent reports approximately 94 seconds in compact-month-details-complete in the current timed run. Its raw.log independently confirms that case passed, but does not itself contain timestamps; that duration remains parent-observed until the timing receipt is written.

Source inspection establishes a concrete repetitive transport cost in tools/planning_compact_table_test.py. complete_details (lines 414 onward) intentionally traverses all 120 monthly rows twice, once in each responsive mode, by calling detail_values. Every row calls month_field_values (279–311), which checks at least 13 individual bound containers through bound_value (261–270). A successful bound_value performs three browser round trips: locator.count(), locator.is_visible(), then locator.inner_text() or the clone/remove-label evaluate. That is at least 3,120 bound-value invocations / 9,360 round trips for the two monthly traversals alone. Historical rows and subtotal checks add more. These are static lower bounds, not profiler measurements or a claim that all 94 seconds belong to RPC overhead.

## Minimal candidate

Confine the first candidate to bound_value, keeping its signature, return payload, expected candidates, normalized comparison and all callers unchanged. Read the matched set with locator.evaluate_all, returning one value per matched element using exactly el.innerText for the ordinary branch, or the existing clone/remove .pl-rate-label/textContent algorithm for the special branch. Assert the returned set has exactly one element, then retain the existing locator.is_visible() check using Playwright's own visibility semantics. Compare the observed string against the same candidates and emit the same expected/actual record.

This combines the cardinality and text reads into one browser operation while keeping visibility as a separate original oracle. It saves one round trip per successful bound-value invocation (at least 3,120 in complete_details). It does not introduce a homemade visibility predicate, broad text search, first-match acceptance, financial calculation, cached DOM across interactions, or reduced month/mode coverage. Preserve useful failure details for zero, duplicate, hidden and incorrect-value containers.

The existing controls_geometry implementation in tools/ui_visual_quality_test.py (267–310) is a reference for consolidating reads of one post-interaction DOM while retaining assertions. It should not be edited for this candidate: its explicit scroll, two-frame settle, geometry and ancestry contract are separately protected.

## Safety reasoning and required counterproof

The test currently performs immediate count and visibility checks before reading text, so absence/duplicates already fail rather than rely on a long text-read retry. evaluate_all must retain all matched elements; no first() or filtering hidden duplicates. Keep the locator.is_visible call, so hidden, zero-size and visibility semantics stay owned by Playwright. Ordinary text must remain innerText, never textContent; the rate-label-removal branch must keep its existing clone semantics. Retain per-container identity: a matching value in another cell must never satisfy the named field. Fetch fresh observations for each invocation; no cache survives a mutation, click, viewport change or financial update.

Before adoption, compare old and candidate observed payloads on the same settled synthetic page for ordinary/FX/rate-label fields in both layouts, and prove both reject missing containers, duplicate containers (including a hidden duplicate), hidden/zero-size containers, wrong named-field values despite a correct value elsewhere, and incorrect rate-label-stripped values. Preserve the existing compact negatives for duplicate control, future blank/zero/value, costs, phase subtotal, overflow and current-year behavior. The current guard's real writer/delegate probe and financial snapshot comparisons remain untouched. Verification should also establish the intended reduction in RPC count, rather than infer it from a single wall-clock run.

## Scope and decision

Do not remove complete_details' 120-month checks in either mode, subtotal field binding, unique_controls, currency grouping, actual detail clicks, viewport transitions, or assertions merely because other checks overlap. Although detail_values and month_field_values also repeat pure FX formatting evaluations, leave those out of the first candidate to keep the change attributable and reviewable.

No expected speedup in seconds is established. This is a bounded candidate for a separate controlled harness change only after authorization; the parent should finish its existing diagnostic run and preserve its raw result. A successful small comparison would justify independent candidate review and a measured unchanged 413-case suite, followed by a fresh complete official FULL. Keep all 413 IDs, negative oracles, native zoom, 2px tolerance and the 900-second gate. A current diagnostic PASS would not retroactively make the prior FULL green. Commit/merge/push remain subject to the approved gate.

## Exact scratch candidate for authorization

DIAGNOSTIC-PROPOSAL.patch contains the single-function change described above. The repository remains unmodified. No candidate was executed or applied.

Original source SHA-256: `4fb30ff95b9911e453e719591a08ec7a15babe430e35890ddf878a131250da52`

Proposed source SHA-256: `0ae1b0ef88af5b7ebb9c6200d8593f6b9bba9e9ceb9f98a5d5da1303df25643b`

Patch SHA-256: `ee61a5ff50c0e201f6201a73113b447ffe90745b83d1c257d5e2c2aefa51a72d`

The original assertion remains a cardinality-equals-one conjunction with the original locator.is_visible; cardinality comes from the complete returned list. The string comparison, normalized function, expected candidates and returned record are byte-for-byte unchanged. Only positive uniqueness leads to observed[0]. The patch performs no browser actions or writes to app state. Implementation and execution of this judge change await explicit A4 approval.
