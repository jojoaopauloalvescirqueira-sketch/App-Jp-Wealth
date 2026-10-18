# Task5 — evidence and coverage ledger, 2026-10-15

All phase status is **conforme calendário**, for the named cash scope. Local compilation span is2026-10-15–2026-12-31 inclusive. A coverage interval defines the interval represented by data, including explicit unknowns; it does not assert that every minute was verified as open/closed. Outside that span the engine returns unknown and no next transition. Normal build never advances the calendar year by itself.

The four preserved research packets record actual primary-source reading, publication dates where available, collection/review date2026-10-15, and limits. Sources without a reported publication date retain `publishedAt:null`. Future grade effective dates are in `rules.json.schedule.validFrom`, not inferred from publication or collection. `Source.verifiedAt` records the review of the evidence/pointer, including a failed-body record explicitly named pending; it must not be read as successful retrieval of every linked body. Only the retained KRX response has a new source-byte hash. No research-note hash is misrepresented as an official source hash.

| ID / scope | Calendar / grade applied | Remaining unknown material |
|---|---|---|
| b3 / ações à vista e fracionário | OC005 to02Nov; OC050 from03Nov, own2026 closures | after17–19 or18–20 depends on applicable expiries, not merely monthly equity options |
| nyse / TapeA | own2026 calendar; core09:30–16,13 on27Nov/24Dec | no after copied from Arca or Nasdaq; live cross/halt not observed |
| nasdaq / Stock Market cash | own calendar; premarket04–09:30 and after16–20 are extended trading | after13 on short days; conditional overnight from announced06Dec cannot become confirmed by date alone |
| tsx / cash | own calendar;07 pre,09:30–16 core,16:15–17 extended | conditional PME16–16:10; short day after13 on24Dec |
| lse / SETS-L1 SET1 | production parameters27Jul; call07:50–08+30s, continuous to16:30; EDSP third Fridays16Oct/20Nov/18Dec10:10–10:15+30s | closing AVD/CPX dependent on actual uncross; other SETS groups/cycles out of scope |
| xetra / DAX cash | own calendar; early retail08–08:55 is restricted; known minimum call intervals08:55–09,13–13:02(05 on settlement days),17:30–17:35 | primary chart says random/minimum, no verified upper bound. No made-up +30/+45s/5min maximum: after opening minimum to13 and after intraday minimum to17:30 remains unknown. TAC/late after17:35 also unknown.30Dec special hours pending |
| euronext-paris / continuous groups11/12/14/16/17/21/22 | own calendar; appendix takes effect19Oct, opening random09–09:00:30 |15–18Oct grade pending, preopen start not extracted, random closing/TAL handover after17:35,24/31Dec short hours. DU13/23 out of scope |
| jpx / TSE domestic cash | own2026 annual; lunch11:30–12:30, Zaraba ends15:25, preclose to15:30 | instantaneous15:30 Itayose is not a fabricated duration of green |
| hkex / ordinary CAS shares | own2026 annual,19Oct/25Dec closed;24/31Dec half; lunch12–13 | no extended-morning eligibility generalized; random CAS last two minutes kept as window |
| sse / mainboard cash | Chinese2026 annual, no closures remaining after07Oct; lunch11:30–13 |09:25–09:30 order/buffer detail not revalidated, explicitly unknown; STAR after out of scope |
| szse / cash | venue retained and identified | whole group unknown: its own annual body not obtained. SSE annual is not substituted |
| nse / CAS and non-CAS | own cash annual; current cash groups retained through07Nov as recommended by reviewed packet;20Oct closed |08Nov Muhurat time pending; after07Nov current schedule deliberately not extrapolated while15Oct SEBI annex/vigency unavailable. Confirmed annual holidays still closed. Non-CAS post15:30 unreviewed |
| bse / cash | venue retained separately from NSE | whole group unknown: operational CAS and annual bodies HTTP403; February preparation does not prove implementation |
| krx / KOSPI cash | general rules body finally obtained Task5 | whole group unknown: operational annual and special19Nov not verified; KOSDAQ obligations calendar is not a substitute |
| saudi / main cash | official indexed2026 annual reviewed, no remaining holidays; Sunday–Thursday; random opening/closing30s | annual direct-body fetch unavailable, evidence is indexed official body; other negotiated deals out of scope |
| asx / cash | current OSPA random earliest09:59:45, continuous safely from10; CSPA16:10–16:11; post16:11–16:21:30; own2026 annual | post-adjust phases16:21:30–19 not revalidated; after14:10 on24/31Dec unknown; no shifted closing times guessed |

## Additional primary attempts in this execution

`task5-fetch-results.json` is the actual escalated HTTP receipt. BSE cash and annual403, SZSE annual timeout, SEBI annex TLS handshake timeout. KRX general KOSPI rules HTTP200/4654bytes were saved and read (including its holiday rules,09–15:30 envelope and other session table). This improves rule-body provenance; it does not resolve annual or special-session coverage.

Web search/open retried canonical SZSE notice both with and without `/general/`, official BSE cash, KRX-special Korean search, Xetra30Dec2026, Euronext end-year2026. No useful new annual/special body resolved those gaps. Euronext calendar still links end-year2025 while announcing future2026 appendix. Xetra circular052/25 was read again: +15/+30/+45 seconds are group-dependent offsets, not proof of a universal random maximum; conservative unknowns were used.

A primary B3 monthly options-expiry page was located and its indexed table read:16Oct,19Nov,18Dec equity options,18Nov/16Dec Ibovespa options. It does not enumerate all weekly/daily/index/futures conditions of after-grade applicability, so the already validated B3 ambiguity remains. URL: https://www.b3.com.br/main.jsp?doui_processActionId=setLocaleProcessAction&locale=pt_BR&lumA=1&lumII=8A80CB81633FBF0B016340EBEC880DCF&lumPageId=8A6882694E91F2D4014E92D6BA5C158F . No third-party calendar supplied any production rule.

## Meaning of the acceptance result

Sixteen venue identities and their scoped groups are implemented. Full verified trading coverage of all sixteen is **not claimed**. BSE/SZSE/KRX deliberately remain unknown, and partial intraday/future exceptions above remain explicit. Browser/UI acceptance, full project gates and human acceptance belong to the parent integration task and are not proved by these data tests.

## Focal correction after independent review, round1

Nasdaq recurring Sundays13/20/27Dec now explicitly preserve unknown21:00–24:00 local America/New_York, matching the pending overnight announcement already applied on06Dec. Before21:00 remains weekly closed; Monday premarket/core keep their separate schedules. No Sunday core is enabled. The correction consumes the primary Nasdaq evidence preserved by the independent reviewer in `.superpowers/sdd/PLANO-AISOL/task5-review-nasdaq-evidence.md`: DN2026-3 and DN2026-8 bodies read, Hub23/5 indexed official text read, direct Hub fetch timeout. These describe Sunday21:00 recurrence but do not confirm future activation. Existing source reference nasdaq-overnight-announcement remains the production evidence pointer.
