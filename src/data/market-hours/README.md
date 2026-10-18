# Public exchange session data — v1

This is public reference data, independent of financial rules, user state, storage, and backup formats. All status means **conforme calendário**; it does not confirm a live trading session, absence of halt, or actual random auction execution. Build normally consumes the frozen `calendar-v1.json`; compilation never uses the clock or network.

## Runtime contract

Load the classic script `src/js/40-app/31-market-hours/01-sessions.js` before consumers. It exposes `globalThis.JPWMarketSessions.prepare(raw)` and `.at(prepared, utcMs)`.

`prepare` validates the complete payload, copies it without changing/freezing the input, recursively freezes its own copy, and constructs private indices. Invalid input throws a readable error; it never becomes an empty/closed calendar. `at` requires the prepared object and a finite safe integer epoch millisecond (within JavaScript Date range), uses binary search per group, and returns a new snapshot. No `Date.now`, `Intl`, DOM, network, storage, or financial state is used by lookup. Reason-only boundaries do not advance the countdown: preparation indexes the next actual phase change. Unknown is a real phase and a barrier; a countdown does not skip it to promise a later opening.

`Catalog = {schemaVersion:1,tzdbVersion,sources:[Source],venues:[Venue]}`.

- `Source = {id,title,url,publishedAt,verifiedAt,sha256?}`. HTTPS URL; dates are ISO local dates. `publishedAt:null` means publication date unavailable for that page; it is never inferred from verification. The optional hash, when present, must identify the original source bytes, not a research note.
- `Venue = {id,name,city,country,region,timeZone,lat,lng,groups:[Group]}`. Preserve venue identity separately from city identity; multiple exchanges may share coordinates.
- `Group = {id,label,coverage:{fromUtc,untilUtc,verifiedAt,sourceIds},periods:[Period]}`.
- `Period = {startUtc,endUtc,phase,reason,sourceIds?,transitionWindow?}`. Periods are UTC integer milliseconds, sorted, contiguous, nonoverlapping, and cover exactly `[fromUtc,untilUtc)`. Seven group phases: `continuous/preopen/auction/break/extended/closed/unknown`.
- `transitionWindow = {earliestUtc,latestUtc,nextPhase}` describes a variable transition; its latest bound equals the period end, its first bound is within the period, and its next phase must match the following period. The window survives lookup, including when its earliest time has already passed. No exact execution instant is invented.

`Snapshot = {asOf,venues:[{id,phase,groups,coverage,reason,nextTransition}],counts}`. Each group status includes id, label, phase, reason, immutable coverage/sourceIds, nextTransition. Venue coverage is the intersection `{fromUtc,untilUtc}` of its scoped groups. Phase is `unknown` when any group is unknown, the shared phase when all agree, otherwise `mixed`. Unknown group IDs/reasons remain visible; known group phases are retained. Venue nextTransition is null while any group is unknown, and never exceeds joint coverage. Otherwise it is the earliest upcoming group phase transition, with the predicted aggregate target phase at the window's latest bound. Group transitions beyond their coverage are null. No future outside coverage is extrapolated.

Counts are `{total,continuous,preopen,auction,break,extended,closed,unknown,mixed,regularOpen}`. Eight aggregate phase counts are exclusive and sum to total. `regularOpen` counts each venue once when at least one group is continuous and no group is unknown. All consumers should use the same snapshot/asOf.

## Reviewable compilation inputs

`sources.json = {schemaVersion:1,sources:[Source]}`. `rules.json = {schemaVersion:1,tzdbVersion,fromDate,untilDate,sources:[sourceId],venues:[RuleVenue]}`. Local dates from `fromDate` through `untilDate` are inclusive. Venue metadata is the same as runtime. Group input:

```json
{
  "id":"cash", "label":"Reviewed scope", "verifiedAt":"2026-10-15",
  "sourceIds":["official-source"], "weekdays":[1,2,3,4,5],
  "schedule":[{
    "validFrom":"2026-10-15", "validUntil":"2026-12-31",
    "sourceIds":["official-source"],
    "sessions":[{"start":"09:00","end":"16:00","phase":"continuous","reason":"Regular session"}]
  }],
  "exceptions":[{"date":"2026-10-18","unknownReason":"Special session time unconfirmed","sourceIds":["official-source"]}]
}
```

An exception replaces the complete weekly session for that date and must have exactly one of `closedReason`, `unknownReason`, or nonempty `sessions`. Sunday opening exceptions therefore precede weekdays. A group-level `unknownReason` keeps the whole group unknown. Missing schedule vigency yields explicit unknown periods, including weekends where weekly closure is unconfirmed. Source-less schedules and overlapping vigencies are rejected. Sessions/gaps are materialized; gaps outside reviewed sessions are closed for the named scope. Lunch or an unconfirmed intraday window must be explicit `break`/`unknown` sessions.

Times are `HH:MM` or `HH:MM:SS`; `24:00` is allowed only as the end. Overnight sessions must be split into local-date pieces. Optional session `transitionWindow` uses `{earliest:"HH:MM:SS",latest:"HH:MM:SS",nextPhase}` and latest must equal end. An empty session list is invalid; closure must name its reason. Ambiguous/nonexistent DST wall times are rejected rather than silently resolved. Adjacent periods merge only when phase, reason and sources agree. Venue/group input order remains stable; source records and source refs use canonical ID order. JSON contains no volatile timestamp. Output is replaced only after successful full compilation.

```sh
/private/tmp/jpw-quality-audit-20261012-01a131dc/runtime/bin/python3 tools/compile_market_hours.py --sources src/data/market-hours/sources.json --rules src/data/market-hours/rules.json --out src/data/market-hours/calendar-v1.json
/Users/joaoalvescirqueira/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/market_hours_unit_test.js
```

## Timezone provenance and current catalog

The compiler opens vendored TZif bytes via `ZoneInfo.from_file`, validates every used zone's SHA256 against `zoneinfo/manifest.json`, and refuses a different requested version. This snapshot is the macOS installed base whose `/usr/share/zoneinfo/+VERSION` said **2026b**, copied on 2026-10-15. It is not an assertion of upstream 2026e availability or bit-for-bit upstream distribution. Fourteen frozen zone files cover the sixteen planned venues plus synthetic UTC fixtures. The manifest preserves individual hashes and origin; normal compilation needs no host timezone database. This timezone data is public reference material.

The compiled catalog identifies **sixteen venues**, with local2026-10-15 through2026-12-31 represented explicitly: B3, NYSE, Nasdaq, TSX, LSE, Xetra, Euronext Paris, JPX, HKEX, SSE, SZSE, NSE, BSE, KRX, Saudi Exchange and ASX. Representation includes unknown intervals and does not mean full verification. `research/` preserves the reviewed research packets with official URLs and explicit limits. The official bodies were read by the delegated source researchers, as recorded there; this implementation pass consumed their reports and did not re-fetch every document. `verifiedAt` reflects that source review, not a live market check.

B3 OC050 was published 2026-10-13, but the equity grade starts **2026-11-03**; 2026-10-26 applies to specified derivatives. The current OC005 grade remains selected through 2026-11-02. Concrete expiry dates affecting after-market sessions remain unresolved: 17:00–19:00 under OC005 and 18:00–20:00 under OC050 are explicitly unknown. Cancellation is never classified as trading. Calendar closures on 24/12 and 31/12 remain full closures. Future instructions may narrow these unknown periods using an official expiry calendar.

NYSE remains continuous during its 15:50–16:00 imbalance; 27/11 and 24/12 core ends at 13:00. No Arca or NYSE American after session is copied. JPX has lunch 11:30–12:30, Zaraba to 15:25, and an order-only preclosing auction phase 15:25–15:30. Its Itayose at exactly 15:30 and NYSE opening/closing crosses are instantaneous events; no fictitious positive-duration execution phase is inserted. The interval at/after 15:30 is closed for this scheduled scope. These are expected calendar phases; extensions and actual execution remain unobserved.

Sixteen venue identities are present; verified coverage remains partial. **BSE, SZSE and KRX remain whole-group unknown** because operational/annual evidence is missing. Paris applies its new appendix only from19Oct; NSE CAS/non-CAS remain distinct and stop schedule extrapolation after07Nov; Muhurat08Nov is explicitly unknown. Short-day detail, random transitions without a supported upper bound and pending overnight activation never become a fabricated exact phase. Nasdaq recurring Sundays13/20/27Dec21:00–24:00 also remain unknown while activation is unconfirmed, with Sunday core still closed. Xetra DAX remains unknown after random opening/intraday minimum ends until the next independently confirmed phase; no invented duration caps a random auction. See [the full coverage and provenance ledger](research/TASK5-COVERAGE.md), including the primary retrieval outcomes and remaining limits. No normal build or runtime resolves missing data from a third-party calendar or internet source.

Run `node tools/market_hours_catalog_test.js` for the sixteen-venue behavioral checks. The core synthetic/compiler suite is separate. Each group exposes the last represented local day via UTC coverage; at its end every lookup is unknown with no extrapolated next opening. Refresh the inputs deliberately before2027; compilation and normal build cannot silently renew the year.
