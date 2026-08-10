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
7. Close the agentic dimension with an explicit verdict, never left implicit:

   `AGENTIC IMPACT CHECK: NO AGENTIC IMPACT` or `AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED`

   followed by `BASIS: <evidence>`. The BASIS is mandatory for both verdicts and must state
   what was examined and why it settles the question — "seems unaffected", "small change",
   "no errors", "no preflight warning" or a bare file list are not evidence. The question
   spans representations the agentic layer consumes: agents, skills, routing, registries,
   operational context, contracts, architecture and canonical documentation read by agents
   or skills. That is the analysis universe, not a list of files to edit.

   The preflight material-freshness signal answers a different question — whether paths
   changed after the source revision — and never substitutes for this judgement.

   If AGENTIC IMPACT DETECTED, run `skills/agentic-evolution-governance/SKILL.md` in IMPACT
   mode before treating the agentic dimension as closed; that skill defines how to assess
   and reconcile. Then update `CURRENT-STATE.md`, `ACTIVE-TASK.md`, audit, changelog, handoff
   and any other affected representation as applicable.

## Handoff

Report findings before summary. Include exact commands and classifications, changed functions/contracts, untested areas, residual risk and the next human gate. Do not call the candidate ready if a required `PRODUCT_FAIL`, `ENVIRONMENT_ERROR` or `NOT_RUN` remains unexplained. Never commit, push, merge or deploy without separate authorization.
