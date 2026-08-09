---
name: jpw-post-change-audit
description: Audit the final JP Wealth candidate after edits and before declaring completion, commit, integration, or release. Use at the end of every material change to verify scope, interactions, generated artifacts, tests, docs, and residual risk.
---

# JP Wealth Post-Change Audit

## Freeze the candidate

Record branch, `BASE_SHA`, current `HEAD`, status and complete diff. If files change afterward, rerun affected verification.

## Review

1. Map every changed file to the authorized objective.
2. Inspect surrounding code for duplicate paths, lifecycle interactions and state effects.
3. Confirm no N2/N3 behavior changed incidentally.
4. Verify manifests and generated artifacts when sources changed.
5. Run security sweep for new inputs, storage, network, CI or dependencies.
6. Run the required quality tier and focused browser flows.
7. Update `CURRENT-STATE.md`, `ACTIVE-TASK.md`, audit, changelog and handoff as applicable.

## Handoff

Report findings before summary. Include exact commands and classifications, changed functions/contracts, untested areas, residual risk and the next human gate. Do not call the candidate ready if a required `PRODUCT_FAIL`, `ENVIRONMENT_ERROR` or `NOT_RUN` remains unexplained. Never commit, push, merge or deploy without separate authorization.
