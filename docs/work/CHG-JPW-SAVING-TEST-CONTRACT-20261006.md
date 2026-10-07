# JP Wealth — saving verification contract

N3/A4 control-plane change authorized by the owner's explicit complete implementation plan. Product contract: CHG-JPW-SAVING-INTEGRITY-20261006; UI contract: CHG-JPW-SAVING-UI-20261006.

Add targeted reproductions and regression tests for confirmed/unknown/refused writes, partial-format rejection, array roots, original hashes, ZIP, legacy review, structured drafts, migrations and unique exports. Existing gates, classifications, financial fixtures and required checks remain intact. Any intentional old expectation mismatch is reported; no weakening to approve the candidate. New probes are independent of historic full results.

Run raw existing suites and preserve attempts/timeouts. Physical folder access, browsers and hosted-origin transfer without their own runtime evidence remain NOT_RUN. Independent audit required after freeze; a passing synthetic probe does not replace native or user acceptance.

## Intentional expectations, 2026-10-06

- persistence_recovery_test: only the centralized verified writer may call localStorage.setItem for the financial key. Finalization must call that writer, not duplicate the raw write. All corruption/guards checks remain.
- finpes_backup_roundtrip_test: wait for the captured Blob after cooperative asynchronous Web Locks; exact roundtrip comparisons remain.
- finalize_session_test: wait for the export acknowledgment control before asserting the destination message; destination and explicit-user-acknowledgment checks remain. An initiated download is not file verification.

Previous unadapted failures are preserved in external receipts. These expectations follow the approved architecture, without changing financial fixtures, gate membership or failure classifications.

- complete_backup_test: legacy fixtures now describe actual pre-v2 envelopes/workspace v1. A v2 envelope whose workspace was removed is separately asserted to be refused as tampering. No integrity check is bypassed in the product.

- persistence_failure_test: refused RAM is preserved only as unconfirmed-memory chunks; confirmed state retains its last verified value. Wait for asynchronous Blob/error evidence; quota, recovery, diagnostics, serialization and no-corruption checks remain.

- persistence_failure_test, idempotent-readback counterproof: each later quota scenario (steps 6, both 6c attempts and both 6d attempts) first changes a synthetic value. A throw with exact persisted candidate bytes is CONFIRMED, not WRITE_REFUSED. Refusal, timer, error, recovery and no-corruption assertions remain unchanged; the prior raw failed attempt is preserved. No runtime edit accompanies this fixture clarification.

- persistence_failure_test: install the alert observer inside an explicit function body returning no callable value. The former assignment expression returned the alert function, which Playwright invoked with null before the async export failure; actual serialization-guidance assertions remain.
- session_write_serialization_test SH/SH2: require the explicit refused-before-write reason and typed REFUSED outcome. Document equality, zero broadcast, no partial finalization and release of the temporary block remain required. Prior raw phrase failures are preserved. SA2 captured-authoritative-disk assertions remain unchanged.

- module_availability_backup_test: consent interception follows the v2 preview; valid fixture changes recompute their checksum, while corrupt cases remain rejected. Explictly corrupt availability is exported only after recovery consent. No gate/classification changes.
- storage_governance_test historical expectations for virgin RAM exports, UUID filenames and exact file readback remain raw PRODUCT_FAIL until separately reconciled; synthetic focused proofs do not convert that result to PASS.
