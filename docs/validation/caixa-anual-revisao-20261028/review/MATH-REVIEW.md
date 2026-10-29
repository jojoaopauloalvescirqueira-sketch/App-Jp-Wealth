# Independent annual arithmetic review — A0/A1

Candidate: HEAD 3e24f60f8cfe, branch codex/mesas-proprietarias-hedge-20261027; preflight audit PASS with 103 existing changes and contextual warning. No repository/data writes. Source hashes in source-hashes.json freeze only the inspected sources.

Original authorized source was read directly from Desktop as ZIP/OOXML; SHA-256 621a4e5bdefc467bede301b94e2c6f60aa05c78df3613cfac3908ef8d0c9084a; first sheet Todas, A2:R329. No native Excel execution or recalculation. No financial example values from the source were exported. Header formulas, daily formulas, subtotals and conditional formatting inspected. Source has 52 projected subtotals; source calendar's historical seed/date mismatch is explicitly excluded from parity.

## Conclusion

No demonstrated arithmetic defect against the approved 26/10 plan. An independently written synthetic pure-engine script ran 14 cases and all passed. This is bounded mathematical evidence, not FULL/browser/native acceptance. The implementation faithfully preserves source arithmetic where approved and intentionally changes calendar, absence semantics, identity, ledger origin and year handling.

## Preserved / approved adaptations

- Source H12 RATE(Q8,,-E6,E8), I12 RATE(O8,,-E6,E8); Q8=(M8*52)*(O8/12); source compounding D/E/F/G rows. Engine 93–105: partial target and periods use the same eligible fraction; direct roots cancel that fraction without applying a second reduction. Fractional Q and sub-cent results remain exact to normal floating-point precision.
- Source J8 RATE(K4,,-E6,E9), J12 FV(rate,M8*4,,-1)-1, K12 FV(rate,240,,-1)-1. Engine 120–125 retains eligible elapsed-day denominator and D*4/240 extrapolations, but suppresses them for unresolved gaps/mismatches. Actual zero, declaration, blank and missing opening remain distinct (106–125).
- Source K7 LOOKUP(E9,D17:D329,C17:C329), K8=K7-TODAY. Engine 127–132 retains last projected opening <= actual balance, exact sign and <14 green/14–29 amber/>29 red; negative/zero targets are not converted into an increasing curve. Colors are historical and do not represent operational safety.
- Source E4 LOOKUP(H4,G17:G329,C17:C329). Engine 128 and140 retains approximate last projected accumulated return <= partial goal, not the first crossing or interpolation.
- Civil weekdays/exclusions/year reference are approved differences, engine39–48/75–77/120. Weekly renderer109–115 sums finite actual results, preserving a recorded zero versus no result. Off-calendar facts remain actual and add no projected compounding (97–118).
- Prior opening: state34–43 re-reads last canonical ledger closing before start, or openingBook; engine69/98/104/106/117/136–140 separates original planned baseline from current actual opening. Canonical writer453–502 only recalculates DERIVED_FROM_PREVIOUS and keeps observed balances.

## Material limitations / presentation recommendations

1. **Approved arithmetic limitation, not a defect:** projected closing can differ from desired balance because Q is not the number of grid dates. Synthetic USD1000, 25%,2026,D5,M12: Q260,261dates, desired1250,final1251.073266,approx date2026-12-29. D6: Q312,261dates, final1205.227280, but targetDate2026-12-31 despite never attaining1250. UI03-ui.js92 shows desired balance and approximate date but does not display summary.projectedClosing. Recommendation: expose projected final closing and qualify goal/date status; keep formulas unless new financial authorization is given.
2. **P2 presentation concern confirmed by source plus synthetic engine result:** UI03-ui.js91 headline uses config.initialBalance with label Saldo inicial/Abertura conferida; line93 actual return is computed using summary.actualInitialBalance. Approved prior-opening correction can leave planned opening1000,actual opening1200,current1212,actual return1%. A user reading only the headline sees1000 and1% without the second opening. Recommendation: label planned opening and show actual opening/provenance when different. Engine result is correct; browser presentation not executed in this review.
3. **P2 presentation concern confirmed statically:** UI03-ui.js91 calls accumulated result Registros conferidos whenever pendingDays=0, even when engine summary.mismatches>0. Line96 separately warns reconciliation. Synthetic sole due observed closing1100/result10/opening1000: pending0,mismatch1,real rate suppressed. Recommendation: use incomplete/reconciliation label whenever mismatch/absent opening also prevents completion.
4. Product handles manually recorded daily monetary performance; deposits/withdrawals and automatic trade aggregation are explicitly absent by approved contract. The name Caixa Anual must not imply a complete cash movement ledger. Changing that scope requires a new financial/data decision.

## Evidence and limits

Executed bundled Node math-review.js: PASS14/14; result file math-review-results.json. Independent examples cover civil leap/century calendars/exclusions, fractional Q and partial roots, goal/grid mismatch, sub-cent/zero/loss/absence/declarations, gaps and observed reanchor, observed mismatch, changed prior opening, weekend actuals, thermometer sign/boundaries/below-domain, target approximate lookup, civil week partition, tiny target/overflow and annual-close timing/completeness. Canonical writer/state were source-inspected only. Source Excel calculation behavior, native rounding, browser labels, responsive layout, imports, persistence, FULL and human acceptance: NOT_RUN here.

Memory lookup only reinforced the existing A0/A1 critical-review route; current disk instructions were checked directly. Relevant memory locator MEMORY.md:413, rollout id01a131dc-6ad1-7690-a57c-e2f99a6d45de.
