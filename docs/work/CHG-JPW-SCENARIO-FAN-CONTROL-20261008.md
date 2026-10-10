# Reconciliacao documental delimitada

Skill tem contrato dedicado separado; juiz permanece intacto.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-SCENARIO-FAN-CONTROL-20261008",
  "status": "approved",
  "approved_by": "Proprietario — pedido humano corrente: PLEASE IMPLEMENT THIS PLAN",
  "approved_at": "2026-10-08T19:38:30.687129+00:00",
  "authorization_evidence": "Plano completo de trajetorias patrimoniais e identidade visual aprovado nesta conversa; reconhecimento da autorizacao, nao aceite do candidate final.",
  "objective": "Registrar componente e descoberta focal sem alterar autoridade/juiz",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/private/tmp/jpw-scenario-fan-20261008/candidate",
    "branch": "codex/onboarding-first-access-20261007",
    "baseline_sha": "7f0828488b2fc0ea62dc7c421174799cda47a34a"
  },
  "scope": {
    "allowed_files": [
      "docs/design/SCENARIO-FAN.md",
      "docs/governance/SKILL-ROUTING.md",
      "docs/architecture/FEATURE-ATLAS.md",
      "docs/governance/CONTEXT-MAP.md",
      "docs/governance/CURRENT-STATE.md",
      "SESSION_HANDOFF.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/CHG-JPW-SCENARIO-FAN-UI-20261008.md",
      "docs/work/CHG-JPW-SCENARIO-FAN-CONTROL-20261008.md",
      "docs/work/CHG-JPW-SCENARIO-FAN-TESTS-20261008.md",
      "docs/work/CHG-JPW-SCENARIO-FAN-SKILL-20261008.md",
      "docs/work/HISTORY-ACTIVE-SCENARIO-FAN-BASELINE-20261008.md",
      "docs/work/HISTORY-STATE-SCENARIO-FAN-BASELINE-20261008.md"
    ],
    "forbidden_files": [
      "docs/normative/",
      "docs/decisions/",
      "tools/quality_gate.py",
      "tools/validate_project.py",
      "tools/agent_instruction_structure_test.py",
      "tools/feature_atlas_test.py",
      ".github/",
      "downloads/ — alteracoes manuais",
      "src/js/30-accounting/05-fx-planning/01-fx-model.js",
      "src/js/30-accounting/05-fx-planning/02-fx-engine.js",
      "src/js/30-accounting/05-fx-planning/03-fx-state.js"
    ],
    "allowed_actions": [
      "Editar somente delta delimitado em copia isolada",
      "Testes sinteticos, revisao independente e geradores oficiais"
    ],
    "forbidden_actions": [
      "Git mutation",
      "publicacao",
      "dados reais",
      "schema/formula financeira",
      "alterar gates ou classificadores",
      "Graphify/reindexacao"
    ],
    "regressions_forbidden": [
      "Ampliar autoridade ou enfraquecer gates",
      "Falsificar validacao ou homologacao",
      "Reescrever historico"
    ]
  },
  "derived_artifacts": {
    "allowed": [],
    "generation_commands": [],
    "manual_edit": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "loopback para perfis sinteticos"
    ],
    "temporary_artifacts": "allowed",
    "cleanup_required": true
  },
  "data": {
    "test_policy": "synthetic_only",
    "approved_real_data": [],
    "schema_change": "forbidden"
  },
  "toolchain": {
    "dependency_changes": [],
    "allowed_processes": [
      "python3",
      "node",
      "Chromium descartavel",
      "git read-only"
    ]
  },
  "acceptance_criteria": [
    "Valores iguais aos produtores, lacunas preservadas, zero escrita por consulta",
    "Selecao grafica independente da edicao, ate dois cenarios",
    "Teclado/toque/temas/adaptacao e alternativas textuais",
    "Evidencia independente sem alegar homologacao ou integracao"
  ],
  "approved_tests": [
    "scenario_fan_test",
    "fx_monthly_chart_test",
    "fx_planning_test",
    "fx_planning_monthly_test",
    "quality_gate standard/full",
    "feature_atlas_test",
    "agent_instruction_structure_test"
  ],
  "rollback": {
    "source": [
      "Restaurar somente delta desta tarefa de /private/tmp/jpw-scenario-fan-20261008/baseline"
    ],
    "application_state": [],
    "data": [],
    "environment": [
      "Encerrar processos descartaveis desta tarefa"
    ],
    "verification": [
      "Hashes originais e ausencia de schema alterado"
    ]
  },
  "expires_on": [
    "Fim da tarefa",
    "Mudanca material de escopo"
  ]
}
```

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-JPW-SCENARIO-FAN-20261008",
  "status": "approved",
  "approved_by": "Proprietario — plano integral corrente",
  "approved_at": "2026-10-08T19:38:30.687129+00:00",
  "authorization_evidence": "Registrar componente e descoberta para programadores/agentes no plano aprovado.",
  "root": "/private/tmp/jpw-scenario-fan-20261008/candidate",
  "mode": "CONCORRENTE",
  "approved_branch": "codex/onboarding-first-access-20261007",
  "create": [
    "docs/design/SCENARIO-FAN.md",
    "docs/work/CHG-JPW-SCENARIO-FAN-UI-20261008.md",
    "docs/work/CHG-JPW-SCENARIO-FAN-CONTROL-20261008.md",
    "docs/work/CHG-JPW-SCENARIO-FAN-TESTS-20261008.md",
    "docs/work/HISTORY-ACTIVE-SCENARIO-FAN-BASELINE-20261008.md",
    "docs/work/HISTORY-STATE-SCENARIO-FAN-BASELINE-20261008.md",
    "docs/work/CHG-JPW-SCENARIO-FAN-SKILL-20261008.md"
  ],
  "modify": [
    "docs/governance/SKILL-ROUTING.md",
    "docs/architecture/FEATURE-ATLAS.md",
    "docs/governance/CONTEXT-MAP.md",
    "docs/governance/CURRENT-STATE.md",
    "SESSION_HANDOFF.md",
    "docs/work/ACTIVE-TASK.md"
  ],
  "merge": [],
  "preserve": [
    "104 alteracoes herdadas",
    "Historicos e classificacoes anteriores",
    "Normas, formulas, schemas, MT5 e gates"
  ],
  "do_not_touch": [
    "AGENTS.md",
    "docs/normative/",
    "docs/decisions/",
    "tools/quality_gate.py",
    "tools/agent_instruction_structure_test.py",
    "tools/feature_atlas_test.py",
    ".github/"
  ],
  "source_revision": "7f0828488b2fc0ea62dc7c421174799cda47a34a",
  "archive_requires_confirmation": [],
  "source_of_truth": {
    "human": "Plano integral aprovado nesta conversa",
    "engineering": "AGENTS.md e Harness existentes",
    "design": "docs/design/SCENARIO-FAN.md"
  },
  "information_promotion": [{"from":"Plano integral aprovado nesta conversa","to":"docs/design/SCENARIO-FAN.md","reason":"Registrar somente contrato visual e referencia de reutilizacao; nao promover resultados de testes ou autoridade"}],
  "expiration_rules": [
    {
      "artifact": "docs/governance/CURRENT-STATE.md",
      "event": "Novo delta material ou mudanca de candidate"
    }
  ],
  "privacy_actions": [
    "Somente dados sinteticos; nenhuma base real consultada"
  ],
  "acceptance_criteria": [
    "Fontes atuais ligadas sem declarar runtime por documentacao",
    "Descoberta independente do componente e limites",
    "Gates sem enfraquecimento"
  ],
  "expires_on": [
    "Fim desta tarefa",
    "Mudanca material de escopo"
  ]
}
```
