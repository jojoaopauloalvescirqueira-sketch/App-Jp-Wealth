# Contexto factual — Bolsas Globais

```yaml
schema: jp-harness/ctx/v1
context_change_id: CTX-JPW-MARKET-HOURS-20261015
status: approved
root: /private/tmp/jpw-time-twins-20261015
mode: SEQUENCIAL
approved_branch: codex/bolsas-globais-aisol-20261015
create: [docs/architecture/MARKET-HOURS.md, docs/work/CHG-JPW-MARKET-HOURS-20261015.md, docs/work/CTX-JPW-MARKET-HOURS-20261015.md]
modify: [docs/architecture/NAVIGATION-HIERARCHY.md, docs/architecture/PWA-UPDATE-LIFECYCLE.md, docs/work/ACTIVE-TASK.md, docs/governance/CURRENT-STATE.md, SESSION_HANDOFF.md, CHANGELOG.md]
preserve: [all_prior_correct_history, minigames_pending_delta]
do_not_touch: [AGENTS.md, CLAUDE.md, skills/, docs/normative/, control_plane]
source_of_truth:
  authority: human_conversation_implementation_and_branch_replies
  implementation: src/js/40-app/31-market-hours/
  evidence: .superpowers/sdd/PLANO-AISOL/
information_promotion: []
expiration_rules: [new_material_candidate_invalidates_old_results]
privacy_actions: [synthetic_only_no_financial_data]
acceptance_criteria: [factual_scoped_records_only, preserve_history, no_norm_or_gate_change]
approved_by: user_in_conversation
approved_at: 2026-10-15
expires_on: [material_scope_or_branch_change, sensitive_data_or_control_plane]
```

Registra o delta factual previsto no plano solicitado. Não altera instruções, norma, autoridade ou gates. O histórico dos jogos permanece histórico com seus próprios recibos.
