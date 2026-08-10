---
name: jpw-data-safety
description: Protect JP Wealth persisted state, backups, imports, recovery, reset flows, and credentials. Use whenever DEFAULTS, migrate, localStorage, IndexedDB, export/import, session finalization, or onboarding credentials are touched.
---

# JP Wealth Data Safety

## Before editing

Read `STATE-SCHEMA.md`, `DB-STORAGE-GOVERNANCE.md`, `DATA-RECOVERY.md` and `SECURITY-MODEL.md`. Classify as N2 unless the work is demonstrably read-only.

## Required invariants

- Keep `jpwealth_v9_state` unless an approved migration says otherwise.
- Validate input before changing gates or replacing in-memory/persisted state.
- Preserve unknown fields unless an approved migration removes them.
- Never fall back to `DEFAULTS` after parse/storage failure.
- Never use `localStorage.clear()`.
- Never store or request a master password.
- Treat `investorPassword` as a session secret: never persist, export or restore it as stored state. When it is indispensable during the current session, keep it in memory only. Any new credential or secret must clear the current security model and storage governance before being granted persistence.
- Use synthetic fixtures; never inspect or version real credentials.

## Verification matrix

Test empty state, prior schema, malformed input, quota/write failure, interrupted recovery, round-trip export/import, reload and unrelated browser keys. For destructive flows, verify double confirmation, precise key removal and resistance to stale async callbacks.

An N2 change is not ready without a recovery path, focused tests, full gate and explicit human authorization.
