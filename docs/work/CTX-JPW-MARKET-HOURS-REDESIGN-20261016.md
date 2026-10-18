# Contexto factual — redesign Bolsas Globais

```yaml
schema: jp-harness/ctx/v1
context_change_id: CTX-JPW-MARKET-HOURS-REDESIGN-20261016
status: approved
root: /private/tmp/jpw-time-twins-20261015
approved_branch: codex/bolsas-globais-aisol-20261015
create: [docs/work/CHG-JPW-MARKET-HOURS-REDESIGN-20261016.md, docs/work/CTX-JPW-MARKET-HOURS-REDESIGN-20261016.md]
modify: [docs/architecture/MARKET-HOURS.md, docs/architecture/NAVIGATION-HIERARCHY.md, docs/architecture/PWA-UPDATE-LIFECYCLE.md, docs/work/ACTIVE-TASK.md, docs/governance/CURRENT-STATE.md, SESSION_HANDOFF.md, CHANGELOG.md]
preserve: [prior_correct_history, complete_three_minigame_candidate]
do_not_touch: [AGENTS.md, CLAUDE.md, skills/, docs/normative/, control_plane]
source_of_truth:
  authority: human_approved_redesign_plan_20261016
  implementation: src/js/40-app/31-market-hours/
  evidence: .superpowers/sdd/jpw-market-redesign-20261016/
information_promotion: []
expiration_rules: [new_material_candidate_invalidates_old_results]
privacy_actions: [synthetic_only_no_financial_data]
acceptance_criteria: [factual_scoped_records_only, preserve_history, no_norm_or_gate_change]
approved_by: user_in_conversation
approved_at: 2026-10-16
```

O plano humano autoriza atualizar documentação e artefatos desta área. Este CTX limita os registros ao comportamento efetivamente implementado, evidências e pendências. Preserva fontes e histórico anteriores; não altera norma, autoridade ou gates. Entrega técnica e compreensão/aceite humano permanecem estados distintos.
