# Tarefa ativa — integração autorizada — 2026-10-09

Data da fotografia: 2026-10-09

Source revision representada: `7b73a9731faad4d3a5e06920ff5a80cd92b715e8`

Base integrada: main 89113f8 + delta validado do site aaac928. Pedido humano: “faça merge, push, commit, limpe worktree e integre tudo”. Integração e validação em andamento; esta fotografia não comprova push ou merge remoto. Preservar GENETRIX 1.21.2 e suas limitações nativas. O estudo de futuras aplicações dos gráficos continua proposta, sem implementação. Nenhum deploy, dado pessoal ou fórmula nova.

[Contrato](../work/CHG-JPW-INTEGRATION-20261009.md)

[Histórico preservado](HISTORY-INTEGRATION-ACTIVE-TASK-20261009.md)

## Contratos da reconciliação contextual

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-INTEGRATION-CONTEXT-20261009",
  "status": "approved",
  "approved_by": "Proprietario — autorizacao explicita nesta sessao",
  "approved_at": "2026-10-10T01:34:42.461764+00:00",
  "authorization_evidence": "faça merge, push, commit, limpe worktree e integre tudo",
  "objective": "Registrar componente e descoberta focal sem alterar autoridade/juiz",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/private/tmp/jpw-onboarding-20261007",
    "branch": "codex/onboarding-first-access-20261007",
    "baseline_sha": "aaac928bc9449f0f482b80008db553919f363fdc"
  },
  "scope": {
    "allowed_files": [
      "docs/work/ACTIVE-TASK.md",
      "docs/governance/CURRENT-STATE.md",
      "docs/governance/CONTEXT-MAP.md",
      "SESSION_HANDOFF.md",
      "docs/work/CHG-JPW-INTEGRATION-20261009.md",
      "docs/work/HISTORY-INTEGRATION-ACTIVE-TASK-20261009.md",
      "docs/work/HISTORY-INTEGRATION-CURRENT-STATE-20261009.md",
      "AGENTS.md"
    ],
    "forbidden_files": [
      "docs/normative/",
      "docs/decisions/",
      "tools/quality_gate.py",
      "tools/agent_instruction_structure_test.py",
      "tools/feature_atlas_test.py",
      ".github/"
    ],
    "allowed_actions": [
      "Reconciliar apenas contexto da integracao autorizada",
      "Preservar historicos e evidencias",
      "Git commit/push/merge e limpeza de worktrees integradas",
      "Corrigir apenas o caminho relocacionado do Harness em AGENTS.md; conteudo/autoridade intactos"
    ],
    "forbidden_actions": [
      "Deploy ou publicacao do Site",
      "Dados reais ou formulas novas",
      "Alterar gates ou classificadores",
      "Implementar o estudo futuro dos graficos"
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
      "Loopback sintetico",
      "Repositorio GitHub configurado"
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
      "Chromium descartavel",
      "git",
      "gh"
    ]
  },
  "acceptance_criteria": [
    "Historico e GENETRIX 1.21.2 preservados",
    "Full e focais do delta combinados",
    "main local/remota identicas e worktrees integradas limpas"
  ],
  "approved_tests": [
    "quality_gate full/standard",
    "leverage_suite all",
    "Focais onboarding/scenario_fan/behavior",
    "agent_instruction_structure_test",
    "feature_atlas_test"
  ],
  "rollback": {
    "source": [
      "Reverter commits da integracao sem reset destrutivo"
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
  "context_change_id": "CTX-JPW-INTEGRATION-20261009",
  "status": "approved",
  "approved_by": "Proprietario — autorizacao explicita nesta sessao",
  "approved_at": "2026-10-10T01:34:42.461764+00:00",
  "authorization_evidence": "faça merge, push, commit, limpe worktree e integre tudo",
  "root": "/private/tmp/jpw-onboarding-20261007",
  "mode": "CONCORRENTE",
  "approved_branch": "codex/onboarding-first-access-20261007",
  "create": [
    "docs/work/CHG-JPW-INTEGRATION-20261009.md",
    "docs/work/HISTORY-INTEGRATION-ACTIVE-TASK-20261009.md",
    "docs/work/HISTORY-INTEGRATION-CURRENT-STATE-20261009.md"
  ],
  "modify": [
    "docs/work/ACTIVE-TASK.md",
    "docs/governance/CURRENT-STATE.md",
    "docs/governance/CONTEXT-MAP.md",
    "SESSION_HANDOFF.md",
    "AGENTS.md"
  ],
  "merge": [],
  "preserve": [
    "Snapshot das 20 alteracoes herdadas",
    "Delta validado de 119 caminhos",
    "GENETRIX 1.21.2 e suas limitacoes",
    "Classificacoes e historicos anteriores"
  ],
  "do_not_touch": [
    "docs/normative/",
    "docs/decisions/",
    "tools/quality_gate.py",
    "tools/agent_instruction_structure_test.py",
    "tools/feature_atlas_test.py",
    ".github/"
  ],
  "source_revision": "aaac928bc9449f0f482b80008db553919f363fdc",
  "archive_requires_confirmation": [],
  "source_of_truth": {
    "human": "Autorizacao Git explicita nesta sessao",
    "engineering": "AGENTS.md e Harness existente, SHA-256 b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95",
    "integration": "docs/work/CHG-JPW-INTEGRATION-20261009.md"
  },
  "information_promotion": [
    {
      "from": "Estado Git observado e bytes validados",
      "to": "Contexto desta integracao",
      "reason": "Conciliar duas linhas de trabalho ja autorizadas sem antecipar conclusao ou homologacao"
    }
  ],
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
    "Historico e GENETRIX 1.21.2 preservados",
    "Full e focais do delta combinados",
    "main local/remota identicas e worktrees integradas limpas"
  ],
  "expires_on": [
    "Fim desta tarefa",
    "Mudanca material de escopo"
  ]
}
```
