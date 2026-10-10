# CHG-JPW-SCENARIO-FAN-UI-20261008

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-SCENARIO-FAN-UI-20261008",
  "status": "approved",
  "approved_by": "Proprietario — pedido humano corrente: PLEASE IMPLEMENT THIS PLAN",
  "approved_at": "2026-10-08T19:38:30.687129+00:00",
  "authorization_evidence": "Plano completo de trajetorias patrimoniais e identidade visual aprovado nesta conversa; reconhecimento da autorizacao, nao aceite do candidate final.",
  "objective": "Adaptar localmente o estilo Scenario Fan no Planejamento; PLAN e ate dois cenarios salvos, baseline opcional, consulta acessivel e sem escrita financeira.",
  "risk_level": "N1",
  "authority_required": "A2",
  "target": {
    "root": "/private/tmp/jpw-scenario-fan-20261008/candidate",
    "branch": "codex/onboarding-first-access-20261007",
    "baseline_sha": "7f0828488b2fc0ea62dc7c421174799cda47a34a"
  },
  "scope": {
    "allowed_files": [
      "src/js/20-ui/08-scenario-fan.js",
      "src/js/30-accounting/05-fx-planning/04-fx-charts.js",
      "src/js/30-accounting/05-fx-planning/05-fx-ui.js",
      "src/styles/app.css",
      "src/js/manifest.json",
      "index.html",
      "sw.js",
      "CHANGELOG.md",
      "build-id.js",
      "dist/",
      "JP Wealth Software.html",
      "JP Wealth Software Portatil.html"
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
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "build-id.js",
      "dist/",
      "sw.js",
      "src/vendor/pdfjs/runtime-assets.js",
      "src/vendor/normative/statute-payload.js"
    ],
    "generation_commands": [
      "python3 tools/rebuild_monolith.py"
    ],
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
