# Independent A0 review — bound_value optimization

Verdict: GO for the approved bounded candidate, subject to the separately required synthetic positive/negative executions and full gate. No concrete blocker found in the scoped callers. This is source review, not a passing test receipt or a performance measurement.

## Scope and exact delta

Compared the whole current `tools/planning_compact_table_test.py` with the supplied original using `diff -u`; the sole delta is the body of `bound_value`, identical to DIAGNOSTIC-PROPOSAL.patch. Read the dedicated approved CHG. No application source, gate, required ID list, geometric tolerance, or timeout is changed by this delta. No repository edits, tests, browsers or Git operations performed in this review.

## Oracles preserved

- Ordinary path: prior `locator.inner_text()` and new browser `el.innerText` read the actual matched element's rendered-text property. The code does not substitute `textContent` for this path.
- Stripped rate path: both clone the matched element deeply, remove only descendants matching `.pl-rate-label`, and read the clone's `textContent`. Neither reads an unrelated container or removes another class.
- Uniqueness: the old count must equal one; the new evaluated result-array length must equal one. Zero and multiple matches fail before indexing. This remains scoped to the locator passed by each field/month/subtotal caller. No `.first()` or whole-page text fallback was introduced.
- Visibility: the same Playwright `locator.is_visible()` remains mandatory after the uniqueness check, including strict locator resolution. Reading a hidden node first cannot by itself pass because a still-hidden matched element is rejected.
- Values: scalar/list candidate handling, whitespace/NBSP normalization, exact membership comparison, diagnostics identifying field and identity, and returned expected/actual shape are unchanged. Wrong named values cannot be rescued by equal values elsewhere.
- Existing counterproof definitions and call paths remain byte-for-byte outside the changed function: overflow, duplicate controls, wrong year, false finalization, future metadata and visible values, cost values, subtotal amount, and missing current row. This review does not claim those cases have executed on the candidate.

## Temporal reads and limits

The ordering changes from count → visibility → text to count+text in one browser evaluation → visibility. It is not an atomic observation of visibility and content. A value or matched node replaced between the evaluation and `is_visible()` could associate an older text snapshot with a later visible element; the previous implementation also used separate locator resolutions, although its text read occurred later. Therefore unconditional equivalence under arbitrary concurrent DOM mutation is not claimed.

The scoped callers operate on synthetic seeded read-model values after selection/settling or synchronous detail expansion. `planning.settle` waits two animation frames. Counterproof mutations complete through awaited browser calls before the oracle, and restoration happens after it. The inspected Planning UI's resize observer repositions presentation; this review found no value-changing mutation intentionally scheduled between these two reads in these callers. Thus the temporal difference is a bounded residual risk, not an evidenced regression requiring a block here. If future callers intentionally exercise concurrent value rerenders, that scenario needs a fresh observation contract rather than relying on either implementation's nonatomic sequence.

The pending synthetic validation should include both text branches, hidden/missing/duplicate/wrong-container values, wrong scalar/list candidates, label removal, NBSP/whitespace, and retained existing counterproofs. Runtime and full results belong in separate receipts; no throughput claim follows from this A0 review.

## Fingerprints

- Original: `4fb30ff95b9911e453e719591a08ec7a15babe430e35890ddf878a131250da52`
- Current reviewed candidate: `0ae1b0ef88af5b7ebb9c6200d8593f6b9bba9e9ceb9f98a5d5da1303df25643b`
- Proposal patch: `ee61a5ff50c0e201f6201a73113b447ffe90745b83d1c257d5e2c2aefa51a72d`
