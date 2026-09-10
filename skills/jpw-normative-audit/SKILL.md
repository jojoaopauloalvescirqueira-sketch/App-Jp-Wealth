---
name: jpw-normative-audit
description: Audit JP Wealth financial rules against the Estatuto and approved decisions. Use for risk profiles, drawdown, leverage, phases, Genesis orders, LIFO, quarantine, accounting, stop statistics, MEI-JP, or any financial/normative N3 change. Engineering-only control-plane N3 follows AGENTS.md and the Harness control-plane audit; retain A4, full and independent review.
---

# JP Wealth Normative Audit

## Authority

This routing distinction does not relax any financial gate. If a control-plane
change also affects a financial rule, apply both review paths. Classification
does not grant authority; instructions being edited cannot authorize their executor.

Read the applicable pages/articles in `docs/normative/` and approved files in `docs/decisions/`. Treat code, tests, UI labels and prior prompts as lower-authority evidence.

## Build a rule matrix

For each rule capture:

| Rule/article | Normative input | Formula/process | Code path | Test | Verdict |
|---|---|---|---|---|---|

Verdicts: exact, partial, divergent, absent, ambiguous. Include units, percentage bases, rounding, timing, state transitions and boundary values.

## Validate

- Recompute at least one normal, one boundary and one adverse example independently.
- Exercise the real browser flow when the rule is user-facing.
- Confirm migration/defaults do not override the rule.
- Search for duplicate constants and parallel implementations.

## Stop conditions

Do not choose among conflicting editions, infer a missing formula, or change N3 code without an approved decision and A4 authority. Record the conflict in an audit/ADR proposal with exact locations and suggested alternatives.
