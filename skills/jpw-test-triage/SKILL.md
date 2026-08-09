---
name: jpw-test-triage
description: Diagnose JP Wealth test outcomes without hiding product defects or confusing environment and harness failures. Use whenever a test is added, updated, failing, flaky, unavailable, or used as completion evidence.
---

# JP Wealth Test Triage

## Classify first

Every command receives one result from `QUALITY-GATES.md`: `PASS`, `PRODUCT_FAIL`, `TEST_HARNESS_FAIL`, `ENVIRONMENT_ERROR`, `BASELINE_FAIL`, or `NOT_RUN`.

## Triage sequence

1. Record exact command, candidate SHA/dirty diff, tool versions and output.
2. Reproduce the smallest failing case.
3. Compare the assertion with current DOM/code and the approved contract.
4. Decide whether product, harness, environment or baseline is responsible.
5. Fix only the responsible layer.
6. Re-run focused test, then the required final tier.

## Integrity rules

- Never catch an exception only to make a gate green.
- Never reduce an assertion without independent evidence that the contract changed deliberately.
- Do not label a missing browser/tool as product failure or PASS.
- Do not reuse evidence after a material input changed.
- Flaky behavior remains a failure until bounded or explained with evidence.

Report passes and failures separately; a partially green suite is not a green gate.
