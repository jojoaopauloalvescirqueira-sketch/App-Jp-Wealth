# JPW Planning monthly — approved product delta

Authority: the owner explicitly requested implementation of the complete monthly planning plan on 2026-10-06. Local candidate only; no commit, integration, publication, MT5 changes or workbook edits.

Base: candidate ca8e03474778e02f, HEAD ac3a2faffeb3, 47 pre-existing Git status entries. The original candidate is preserved; baseline file hashes and status are stored outside this candidate in the delivery directory.

N1/A2 presentation: a monthly editable board, explicit drafts, save/cancel, keyboard, responsive rows, blue finalized months and table as the canonical initial view. Existing route IDs and commands remain available.

N2/A3 data contract: planningRevision 3 with compatible reads of revision 2; explicit absence of forecast and explicit reopening/reconciliation. No new normative parameters or return formulas. Absence must not become zero, recurring assumptions must preserve monthly exceptions, confirmed actuals must not become forecasts after reopening.

Financial invariants: profit = opening × original rate (or original nominal result); closing = opening + profit + actual/planned contributions. Contributions enter after profit. Baseline and historical snapshots remain intact, original input and provenance preserved. The ledger is the sole source of realized contributions.

All mutation paths must enforce finalized protection. Reopening requires a reason, preserves the original, and marks downstream confirmed actuals for chronological reconciliation. User confirmation is necessary before an edited realized month becomes finalized again.

Verification: characterize old behavior; new domain/board tests; existing planning, accounting and persistence checks; standard and raw full gates; independent financial and interaction audits. Raw failures remain separately classified. No judge weakening is authorized.

Rollback: resume the preserved base and its matching storage backup. Revision-3 data is never downgraded silently or deleted; export a complete backup before returning to a client that only reads revision 2.

Acceptance remains candidate-specific. Tests do not constitute owner acceptance or global financial approval.
