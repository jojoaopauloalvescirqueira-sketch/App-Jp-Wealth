# Integração das pendências JP Wealth — 18/10/2026

[Contrato e limites](CHG-JPW-CONSOLIDACAO-INTEGRAL-20261018.md). F01, site e instalador têm provas focais; o conjunto exige gate novo. A autorização provém das mensagens do proprietário. Publicação de site/EXE, runtime MT5 e aceite humano permanecem separados.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-CONSOLIDACAO-INTEGRAL-CONTEXT-20261018",
  "status": "approved",
  "objective": "Reconciliar contexto factual de site, F01 e instalador com preservação histórica e provas próprias",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/private/tmp/jpw-stoikus-installer-20261014",
    "branch": "codex/stoikus-installer-20261014",
    "baseline_sha": "bf0b1e8a882c9cdf880129f68f7c111e06e6f0c4"
  },
  "scope": {
    "allowed_files": [
      "docs/work/ACTIVE-TASK.md",
      "docs/governance/CURRENT-STATE.md",
      "docs/governance/CONTEXT-MAP.md",
      "SESSION_HANDOFF.md",
      "docs/work/CHG-JPW-CONSOLIDACAO-INTEGRAL-20261018.md",
      "docs/work/HISTORY-CONSOLIDATION-INSTALLER-ACTIVE-TASK-20261018.md",
      "docs/work/HISTORY-CONSOLIDATION-INSTALLER-CURRENT-STATE-20261018.md",
      "docs/work/HISTORY-CONSOLIDATION-INSTALLER-SESSION_HANDOFF-20261018.md",
      "docs/work/HISTORY-CONSOLIDATION-SITE-ACTIVE-TASK-20261018.md",
      "docs/work/HISTORY-CONSOLIDATION-SITE-CURRENT-STATE-20261018.md",
      "docs/work/HISTORY-CONSOLIDATION-SITE-SESSION_HANDOFF-20261018.md",
      "docs/work/HISTORY-CONSOLIDATION-SECURITY-ACTIVE-TASK-20261018.md",
      "docs/work/HISTORY-CONSOLIDATION-SECURITY-CURRENT-STATE-20261018.md",
      "docs/work/HISTORY-CONSOLIDATION-SECURITY-SESSION_HANDOFF-20261018.md"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "CLAUDE.md",
      "tools/quality_gate.py",
      "tools/agent_instruction_structure_test.py",
      "docs/normative/",
      "docs/decisions/"
    ],
    "allowed_actions": [
      "Reconciliar somente representações factuais da integração autorizada",
      "Conservar integralmente as fotografias de cada trilha"
    ],
    "forbidden_actions": [
      "Criar autoridade, mudar critérios ou apresentar estados pendentes como aprovados",
      "Publicar site, EXE ou dados privados"
    ],
    "regressions_forbidden": [
      "Apagar histórico ou alterar a edição documental curada",
      "Confundir gate host com execução Windows/MT5"
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
    "cleanup_required": false
  },
  "data": {
    "test_policy": "synthetic_only",
    "approved_real_data": [],
    "schema_change": "forbidden"
  },
  "toolchain": {
    "dependency_changes": [],
    "allowed_processes": [
      "Python padrão",
      "Git leitura"
    ]
  },
  "acceptance_criteria": [
    "Contexto atual identifica versão e limites, histórico preservado",
    "Estrutura CHG/CTX e referências válidas"
  ],
  "approved_tests": [
    "python3 tools/agent_instruction_structure_test.py",
    "python3 tools/quality_gate.py --tier full",
    "python3 tools/leverage_suite.py --scope host"
  ],
  "rollback": {
    "source": [
      "Restaurar documentos da fotografia preservada"
    ],
    "application_state": [
      "Nenhuma escrita em dados do aplicativo"
    ],
    "data": [
      "Preservar originais e backups"
    ],
    "environment": [
      "Nenhuma mudança global"
    ],
    "verification": [
      "Conferir hashes originais"
    ]
  },
  "expires_on": [
    "Ampliação de escopo ou mudança material sem revalidação"
  ],
  "approved_by": "Proprietário: pedido direto de resolver todas as pendências, commit, push, merge e limpeza; atualização do instalador e patch visual especificamente autorizados",
  "approved_at": "2026-10-18T17:32:50.482185+00:00",
  "authorization_evidence": "Atualizar e concluir também o instalador antes da limpeza final; registro do aceite, não timestamp original da fala",
  "approval_timestamp_note": "Horário de registro; não é timestamp recuperado da mensagem humana"
}
```

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-JPW-CONSOLIDACAO-INTEGRAL-20261018",
  "status": "approved",
  "root": "/private/tmp/jpw-stoikus-installer-20261014",
  "mode": "CONCORRENTE",
  "approved_branch": "codex/stoikus-installer-20261014",
  "create": [
    "docs/work/CHG-JPW-CONSOLIDACAO-INTEGRAL-20261018.md",
    "docs/work/HISTORY-CONSOLIDATION-INSTALLER-ACTIVE-TASK-20261018.md",
    "docs/work/HISTORY-CONSOLIDATION-INSTALLER-CURRENT-STATE-20261018.md",
    "docs/work/HISTORY-CONSOLIDATION-INSTALLER-SESSION_HANDOFF-20261018.md",
    "docs/work/HISTORY-CONSOLIDATION-SITE-ACTIVE-TASK-20261018.md",
    "docs/work/HISTORY-CONSOLIDATION-SITE-CURRENT-STATE-20261018.md",
    "docs/work/HISTORY-CONSOLIDATION-SITE-SESSION_HANDOFF-20261018.md",
    "docs/work/HISTORY-CONSOLIDATION-SECURITY-ACTIVE-TASK-20261018.md",
    "docs/work/HISTORY-CONSOLIDATION-SECURITY-CURRENT-STATE-20261018.md",
    "docs/work/HISTORY-CONSOLIDATION-SECURITY-SESSION_HANDOFF-20261018.md"
  ],
  "modify": [
    "docs/work/ACTIVE-TASK.md",
    "docs/governance/CURRENT-STATE.md",
    "docs/governance/CONTEXT-MAP.md",
    "SESSION_HANDOFF.md"
  ],
  "merge": [],
  "preserve": [
    "Todos os originais e recibos; novos snapshots privados das três trilhas",
    "Fontes MQL e pacotes históricos; edição curada C2 e oráculos financeiros"
  ],
  "do_not_touch": [
    "AGENTS.md",
    "CLAUDE.md",
    "tools/quality_gate.py",
    "tools/agent_instruction_structure_test.py",
    "docs/normative/",
    "docs/decisions/"
  ],
  "archive_requires_confirmation": [],
  "source_of_truth": {
    "human": "Pedidos diretos desta conversa; documentos não concedem autoridade",
    "baseline": "bf0b1e8a882c9cdf880129f68f7c111e06e6f0c4",
    "product": "docs/work/CHG-JPW-CONSOLIDACAO-INTEGRAL-20261018.md"
  },
  "information_promotion": [
    {
      "from": "Deltas revisados e provas individuais",
      "to": "Contexto da combinação",
      "reason": "Distinguir provas focais e gate novo do conjunto"
    }
  ],
  "expiration_rules": [
    {
      "artifact": "Provas do conjunto",
      "event": "Mudança material de qualquer input correspondente"
    }
  ],
  "privacy_actions": [
    "Somente fixtures sintéticas; nenhum dado de conta"
  ],
  "acceptance_criteria": [
    "Referências válidas e limites explícitos"
  ],
  "expires_on": [
    "Ampliação de escopo ou mudança material sem revalidação"
  ],
  "approved_by": "Proprietário: pedido direto de resolver todas as pendências, commit, push, merge e limpeza; atualização do instalador e patch visual especificamente autorizados",
  "approved_at": "2026-10-18T17:32:50.482185+00:00",
  "approval_timestamp_note": "Horário de registro; não é timestamp recuperado da mensagem humana"
}
```
