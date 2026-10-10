# Contrato dedicado de reconciliacao local

Pedido humano nesta conversa: corrige todas as falhas, implemente todas as melhorias, e refaca os testes e auditoria. Registro do reconhecimento desta autorizacao, nao aceite do candidate final.

Nao altera autoridade, juiz, parametros ou fonte financeira. Historico de ACTIVE-TASK preservado em arquivo proprio. Aceite final continua pendente.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-BEHAVIOR-CONTROL-20261008",
  "status": "approved",
  "approved_by": "Proprietario, mensagem humana corrente desta conversa",
  "approved_at": "2026-10-08T16:46:54.721855+00:00",
  "authorization_evidence": "Pedido humano nesta conversa: corrige todas as falhas, implemente todas as melhorias, e refaca os testes e auditoria. Registro do reconhecimento desta autorizacao, nao aceite do candidate final.",
  "objective": "Corrigir CTRL-01/02 e orientacoes contraditorias: contrato ativo unico CHG/CTX, historico separado, hashes do Atlas conferidos por leitura; reconciliacao local de estado e links, sem enfraquecer juiz ou alterar autoridade.",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/private/tmp/jpw-behavior-fixes-20261008/candidate",
    "branch": "codex/onboarding-first-access-20261007",
    "baseline_sha": "7f0828488b2fc0ea62dc7c421174799cda47a34a"
  },
  "scope": {
    "allowed_files": [
      "AGENTS.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/HISTORY-ACTIVE-BEHAVIOR-BASELINE-20261008.md",
      "docs/work/CHG-JPW-BEHAVIOR-CONTROL-20261008.md",
      "docs/work/CHG-JPW-BEHAVIOR-FINANCE-20261008.md",
      "docs/work/CHG-JPW-BEHAVIOR-DRAFTS-20261008.md",
      "docs/work/CHG-JPW-BEHAVIOR-TESTS-20261008.md",
      "docs/work/BRIEF-JPW-BEHAVIOR-FIXES-20261008.md",
      "docs/governance/CURRENT-STATE.md",
      "docs/architecture/FEATURE-ATLAS.md",
      "docs/architecture/DB-STORAGE-GOVERNANCE.md",
      "docs/recovery/DATA-RECOVERY.md",
      "SESSION_HANDOFF.md",
      "docs/work/HISTORY-STATE-BEHAVIOR-BASELINE-20261008.md",
      "docs/governance/SECURITY-MODEL.md",
      "docs/work/CHG-JPW-BEHAVIOR-BACKUP-20261008.md",
      "docs/work/CHG-JPW-BEHAVIOR-LAYOUT-20261008.md"
    ],
    "forbidden_files": [
      "docs/normative/",
      "docs/decisions/",
      "tools/quality_gate.py",
      "tools/agent_instruction_structure_test.py",
      "tools/feature_atlas_test.py",
      "skills/",
      ".github/",
      "src/",
      "mt5/"
    ],
    "allowed_actions": [
      "Reconciliar somente arquivos explicitamente permitidos",
      "Executar validadores unchanged e revisao independente",
      "Preservar historia e limites de evidencia"
    ],
    "forbidden_actions": [
      "Git mutation",
      "publicacao",
      "alterar gates/classificadores",
      "ampliar autoridade",
      "homologar norma",
      "Graphify/reindex externo"
    ],
    "regressions_forbidden": [
      "distorcer contrato financeiro",
      "apagar historico",
      "falsa validacao nativa",
      "dados reais"
    ]
  },
  "derived_artifacts": {
    "allowed": [],
    "generation_commands": [],
    "manual_edit": "forbidden"
  },
  "external_side_effects": {
    "network": "forbidden",
    "allowed_targets": [],
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
      "git read-only",
      "Chromium descartavel"
    ]
  },
  "acceptance_criteria": [
    "Validadores atuais verdes sem alterar juiz",
    "Fichas conferidas no codigo e hashes correntes sem alegar runtime por hash",
    "Autoridade Git/financeira e limites nativos preservados",
    "Revisao independente"
  ],
  "approved_tests": [
    "agent_instruction_structure_test",
    "feature_atlas_test",
    "preflight_context_test",
    "quality_gate standard/full"
  ],
  "rollback": {
    "source": [
      "Restaurar somente este delta do snapshot conhecido"
    ],
    "application_state": [],
    "data": [],
    "environment": [
      "Encerrar somente processos descartaveis desta tarefa"
    ],
    "verification": [
      "874 hashes origem preservados"
    ]
  },
  "expires_on": [
    "Mudanca de raiz/branch/escopo",
    "Fim desta tarefa; aceite de integracao ainda separado"
  ]
}
```

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-JPW-BEHAVIOR-CONTROL-20261008",
  "status": "approved",
  "approved_by": "Proprietario, mensagem humana corrente desta conversa",
  "approved_at": "2026-10-08T16:46:54.721855+00:00",
  "authorization_evidence": "Pedido humano nesta conversa: corrige todas as falhas, implemente todas as melhorias, e refaca os testes e auditoria. Registro do reconhecimento desta autorizacao, nao aceite do candidate final.",
  "root": "/private/tmp/jpw-behavior-fixes-20261008/candidate",
  "mode": "CONCORRENTE",
  "approved_branch": "codex/onboarding-first-access-20261007",
  "create": [
    "docs/work/HISTORY-ACTIVE-BEHAVIOR-BASELINE-20261008.md",
    "docs/work/CHG-JPW-BEHAVIOR-CONTROL-20261008.md",
    "docs/work/CHG-JPW-BEHAVIOR-FINANCE-20261008.md",
    "docs/work/CHG-JPW-BEHAVIOR-DRAFTS-20261008.md",
    "docs/work/CHG-JPW-BEHAVIOR-TESTS-20261008.md",
    "docs/work/BRIEF-JPW-BEHAVIOR-FIXES-20261008.md",
    "docs/work/HISTORY-STATE-BEHAVIOR-BASELINE-20261008.md"
  ],
  "modify": [
    "AGENTS.md",
    "docs/work/ACTIVE-TASK.md",
    "docs/governance/CURRENT-STATE.md",
    "docs/architecture/FEATURE-ATLAS.md",
    "docs/architecture/DB-STORAGE-GOVERNANCE.md",
    "docs/recovery/DATA-RECOVERY.md",
    "SESSION_HANDOFF.md",
    "docs/governance/SECURITY-MODEL.md"
  ],
  "merge": [],
  "preserve": [
    "20 deltas anteriores",
    "Normas e testes/gates estruturais",
    "Historico completo da antiga tarefa ativa",
    "Status NOT_RUN e falhas brutas anteriores"
  ],
  "do_not_touch": [
    "docs/normative/",
    "docs/decisions/",
    "tools/quality_gate.py",
    "tools/agent_instruction_structure_test.py",
    "tools/feature_atlas_test.py",
    "skills/",
    "src/",
    "mt5/",
    ".github/"
  ],
  "archive_requires_confirmation": [
    "Nenhuma remocao de worktree/branch autorizada"
  ],
  "source_of_truth": {
    "authority": "Pedido humano corrente e AGENTS",
    "engineering": "Harness canonico localizado e registrado no brief",
    "product": "Fontes reais e contratos pertinentes",
    "audit": "evidencias externas f70839305b2d7fb8"
  },
  "information_promotion": [
    {
      "from": "auditoria externa somente leitura",
      "to": "contratos e estado delimitados da correcao candidata",
      "reason": "Pedido humano explicito de correcao/teste/auditoria; nao promove candidato a main"
    }
  ],
  "expiration_rules": [
    {
      "artifact": "docs/work/ACTIVE-TASK.md",
      "event": "Mudanca de escopo/raiz/branch ou fim da tarefa"
    }
  ],
  "privacy_actions": [
    "Nenhum dado real, navegador pessoal ou credencial"
  ],
  "acceptance_criteria": [
    "Validadores atuais verdes sem alterar juiz",
    "Fichas conferidas no codigo e hashes correntes sem alegar runtime por hash",
    "Autoridade Git/financeira e limites nativos preservados",
    "Revisao independente"
  ],
  "expires_on": [
    "Mudanca de raiz/branch/escopo",
    "Fim desta tarefa; aceite de integracao ainda separado"
  ]
}
```
