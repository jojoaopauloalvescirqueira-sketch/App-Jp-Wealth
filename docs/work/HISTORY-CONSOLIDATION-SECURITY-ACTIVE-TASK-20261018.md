# Correção F01 e consolidação Git —18/10/2026

Pedido do proprietário: resolver todas as pendências, concluir commit/push/merge e limpar as worktrees após preservação. A base da branch de segurança é bf0b1e8a882c9cdf880129f68f7c111e06e6f0c4. O contrato de produto e as regressões estão em [CHG-F01](CHG-JPW-F01-SECURITY-20261016.md); a reconciliação documental abaixo tem alvo próprio e não modifica instruções ou critérios. [Fotografias anteriores](HISTORY-BEFORE-F01-ACTIVE-TASK-20261018.md) preservadas integralmente.

Invariantes: fontes e pacotes Stoikus1.23R5/cálculo1.9/C2 byte-idênticos; fórmulas e dados reais intocados; falha de contador sem escrita; versões antigas aceitas sem normalização em leitura; histórico de auditoria preservado. Testes novos31/31; demais gates atuais pendentes. Scripts de teste, oráculos e runner anteriores não são enfraquecidos.

## Contrato atual do contexto factual

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-F01-CONTEXT-20261018",
  "status": "approved",
  "objective": "Reconciliar somente contexto factual da correção F01 à main atual e registrar sua validação e integração solicitadas",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/private/tmp/jpw-seguranca-contabilidade-20261016",
    "branch": "codex/jpw-seguranca-contabilidade-20261016",
    "baseline_sha": "bf0b1e8a882c9cdf880129f68f7c111e06e6f0c4"
  },
  "scope": {
    "allowed_files": [
      "docs/work/CHG-JPW-F01-SECURITY-20261016.md",
      "docs/work/CHG-JPW-F01-CONTEXT-20261018.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/governance/CURRENT-STATE.md",
      "docs/governance/CONTEXT-MAP.md",
      "SESSION_HANDOFF.md",
      "docs/audit/F01-SECURITY-20261016.md",
      "docs/work/HISTORY-BEFORE-F01-CURRENT-STATE-20261018.md",
      "docs/work/HISTORY-BEFORE-F01-ACTIVE-TASK-20261018.md"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "CLAUDE.md",
      "tools/agent_instruction_structure_test.py",
      "tools/quality_gate.py",
      "tools/agent_preflight.py",
      "docs/normative/",
      "docs/decisions/"
    ],
    "allowed_actions": [
      "Registrar objetivo, base, fontes, testes, evidências e rollback da correção já autorizada",
      "Reconciliar contexto mantendo fotografias e falhas históricas"
    ],
    "forbidden_actions": [
      "Alterar instruções, critérios, runner ou autoridade para aprovar o próprio candidato",
      "Publicar site ou dados privados"
    ],
    "regressions_forbidden": [
      "Converter histórico ou NOT_RUN em PASS atual",
      "Apagar evidências ou modificar normas"
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
      "Python stdlib",
      "Git somente leitura para verificação do contrato"
    ]
  },
  "acceptance_criteria": [
    "Alvos e baseline coerentes com a branch atual",
    "Preservação de fontes normativas, oráculos e instruções",
    "Resultados distinguem correção, fontes, CI e runtime nativo"
  ],
  "approved_tests": [
    "python3 tools/agent_instruction_structure_test.py --contract docs/work/CHG-JPW-F01-CONTEXT-20261018.md",
    "python3 tools/quality_gate.py --tier full"
  ],
  "rollback": {
    "source": [
      "Reverter apenas o delta documental desta revisão"
    ],
    "application_state": [
      "Nenhuma alteração de dados reais"
    ],
    "data": [
      "Conservar backups e fotografias anteriores"
    ],
    "environment": [
      "Preservar worktrees até conclusão validada"
    ],
    "verification": [
      "Conferir diff e hashes do baseline"
    ]
  },
  "approved_by": "Proprietário, pedido direto de consolidar todas as pendências com commit, push e merge",
  "approved_at": "2026-10-18T16:40:33.400297+00:00",
  "approval_timestamp_note": "Horário de registro da autorização; não é timestamp recuperado da mensagem humana",
  "expires_on": [
    "Ampliação de escopo, política, normas ou dados",
    "Mudança material de candidato sem revalidação"
  ]
}
```

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-JPW-F01-CONTEXT-20261018",
  "status": "approved",
  "root": "/private/tmp/jpw-seguranca-contabilidade-20261016",
  "mode": "SEQUENCIAL",
  "approved_branch": "codex/jpw-seguranca-contabilidade-20261016",
  "create": [
    "docs/work/CHG-JPW-F01-CONTEXT-20261018.md",
    "docs/audit/F01-SECURITY-20261016.md",
    "docs/work/HISTORY-BEFORE-F01-CURRENT-STATE-20261018.md",
    "docs/work/HISTORY-BEFORE-F01-ACTIVE-TASK-20261018.md"
  ],
  "modify": [
    "docs/work/CHG-JPW-F01-SECURITY-20261016.md",
    "docs/work/ACTIVE-TASK.md",
    "docs/governance/CURRENT-STATE.md",
    "docs/governance/CONTEXT-MAP.md",
    "SESSION_HANDOFF.md"
  ],
  "merge": [],
  "preserve": [
    "Fotografias históricas e revisão independente16/10",
    "Todos os pacotes Stoikus e edição curada C2"
  ],
  "do_not_touch": [
    "docs/normative/",
    "docs/decisions/",
    "AGENTS.md",
    "CLAUDE.md",
    "tools/agent_instruction_structure_test.py",
    "tools/quality_gate.py"
  ],
  "archive_requires_confirmation": [],
  "source_of_truth": {
    "human": "Pedido atual e aprovação F01 anterior",
    "baseline": "bf0b1e8a882c9cdf880129f68f7c111e06e6f0c4",
    "product": "docs/work/CHG-JPW-F01-SECURITY-20261016.md"
  },
  "information_promotion": [
    {
      "from": "Fontes e testes atuais",
      "to": "Estado focal F01",
      "reason": "Registrar fatos verificados separadamente dos recibos históricos"
    }
  ],
  "expiration_rules": [
    {
      "artifact": "Evidências desta revisão",
      "event": "Qualquer mudança material de fonte, fixture ou gerador"
    }
  ],
  "privacy_actions": [
    "Fixtures sintéticas; preservar originais em backup privado"
  ],
  "acceptance_criteria": [
    "Contrato estrutural e contexto coerentes sem nova autoridade"
  ],
  "approved_by": "Proprietário, pedido direto de consolidar todas as pendências com commit, push e merge",
  "approved_at": "2026-10-18T16:40:33.400297+00:00",
  "expires_on": [
    "Ampliação de escopo, política, normas ou dados",
    "Mudança material de candidato sem revalidação"
  ]
}
```
