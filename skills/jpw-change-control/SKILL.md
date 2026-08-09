---
name: jpw-change-control
description: Implement bounded JP Wealth changes with explicit risk level, invariants, tests, rollback, minimal diff, and separate Git authorization. Use for every code, test, configuration, or governance edit.
---

# JP Wealth Change Control

## Contract first

Write or update `docs/work/ACTIVE-TASK.md` with objective, exclusions, N-level, authority, allowed files, invariants, tests and rollback. If the requested work crosses from N0/N1 into N2/N3, stop for a new authorization.

## Edit

- Preserve unrelated and user-authored changes.
- Prefer the smallest root-cause patch.
- Do not combine formatting, renaming or architecture cleanup with behavior.
- Do not edit generated `dist/` directly; use `tools/rebuild_monolith.py` when applicable.
- Do not change classic-script order without manifest validation.
- Add a regression test when practical; do not weaken a valid contract.

## Verify

Run the focused test during iteration and the required tier from `QUALITY-GATES.md` on the final candidate. Review:

```bash
git diff --check
git diff --stat
git diff
```

Explain files, functions, rules, data impact, visual impact, tests and residual risk. Commit, push, merge and deploy remain separate human gates.
