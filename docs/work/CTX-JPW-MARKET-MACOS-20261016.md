# Registros factuais — composição macOS

```yaml
schema: jp-harness/ctx/v1
context_change_id: CTX-JPW-MARKET-MACOS-20261016
status: approved
root: /private/tmp/jpw-time-twins-20261015
approved_branch: codex/bolsas-globais-aisol-20261015
create: [docs/work/CHG-JPW-MARKET-MACOS-20261016.md, docs/work/CTX-JPW-MARKET-MACOS-20261016.md, docs/superpowers/plans/2026-10-16-market-macos.md]
modify: [docs/architecture/MARKET-HOURS.md, docs/work/ACTIVE-TASK.md, docs/governance/CURRENT-STATE.md, SESSION_HANDOFF.md, CHANGELOG.md, tools/regression-memory.json]
preserve: [prior_correct_history, complete_three_minigame_candidate, local_engineering_installation]
do_not_touch: [AGENTS.md, CLAUDE.md, skills/, docs/normative/, control_plane]
source_of_truth:
  authority: human_approval_macos_design_20261016
  implementation: src/js/40-app/31-market-hours/
  evidence: .superpowers/sdd/jpw-market-macos-20261016/
information_promotion: []
expiration_rules: [material_candidate_change_invalidates_affected_results]
privacy_actions: [synthetic_only_no_financial_data]
acceptance_criteria: [factual_scoped_records_only, preserve_history, no_norm_or_gate_change]
approved_by: user_in_conversation
approved_at: 2026-10-16
```

O pedido humano cobre registros delimitados da implementação aprovada. Este CTX registra comportamento observado, provas e pendências; não cria norma, amplia autoridade ou encerra incidentes por repetição bem-sucedida.
