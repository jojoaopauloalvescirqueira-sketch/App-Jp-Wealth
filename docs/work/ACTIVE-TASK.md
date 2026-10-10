# Tarefa ativa — JPW Scenario Fan

Pedido humano corrente: refinar a semelhança visual com a referência renderizada, mantendo o plano completo de trajetórias patrimoniais e identidade visual já implementado.

Produto: [N1/A2](CHG-JPW-SCENARIO-FAN-UI-20261008.md). Descoberta para agentes: [N3/A4 separado](CHG-JPW-SCENARIO-FAN-CONTROL-20261008.md). Skill: [N3/A4 separado](CHG-JPW-SCENARIO-FAN-SKILL-20261008.md). Provas: [contrato focal](CHG-JPW-SCENARIO-FAN-TESTS-20261008.md). Base `1591f527ada923d4`; 104 deltas conhecidos preservados. CHGs do refinamento visual e catálogo informativo fora dos fontes em `reference-revision/CHG.json` e `CHG-CATALOG.json`. Não houve novas permissões, consumidores ou alteração das fences aprovadas.

Revisão visual corrente concluída no candidate local `363e2e7b56a86ced`. 57/57 PASS no full bruto; 46/46 PASS no subconjunto STANDARD da mesma execução FULL (não execução CLI separada). Renderer/CSS exatos passaram focal 16/16, regressão gráfica mensal 8/8 e contraprova independente 8/8 mais preservação de cursor. HTTP, file, portátil e PWA offline passaram 4/4 na distribuição corrigida; zoom nativo Chrome 200% e demonstração em 1440/390/320 px também conferidos. Integridade independente verificou manifesto, 102 scripts, quatro assets e réplica fiel de 899 caminhos. Evidências externas em `/private/tmp/jpw-scenario-fan-20261008/reference-revision`.

Histórico preservado: a entrega inicial `ffa80ce18f1e7e5d` passou seu escopo técnico, mas o proprietário rejeitou a semelhança visual. A build intermediária `4cded3c51310acf0` teve 54 PASS e 3 PRODUCT_FAIL brutos: preflight/structure por hash declarado antigo e pivot-studies por erro de inicialização. O manifesto foi corrigido mecanicamente, seguido dos geradores e validadores oficiais. Três replays iguais de Pivôs passaram, sem esclarecer a causa inicial; o recibo anterior permanece inalterado. Gates parciais interrompidos e erros dos probes externos também foram preservados, sem inferir PASS.

O refinamento aproxima a anatomia do PriceTargetFan mantendo dados mensais exatos, lacunas, consulta acessível e fallback estreito. No produto nenhum cenário é escolhido automaticamente; somente a demonstração fictícia começa com duas hipóteses. Fórmulas, writers, schemas, MT5, julgadores e autoridade permanecem iguais à base desta campanha. Aceite estético humano, integração e publicação são separados e pendentes. Safari, tecnologia assistiva nativa, toque físico, hospedagem operacional e MT5 nativo NOT_RUN. Notas de encerramento são o único delta documental posterior ao gate; runtime preservado.

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

[Historico anterior](HISTORY-ACTIVE-SCENARIO-FAN-BASELINE-20261008.md), sem autoridade corrente.
