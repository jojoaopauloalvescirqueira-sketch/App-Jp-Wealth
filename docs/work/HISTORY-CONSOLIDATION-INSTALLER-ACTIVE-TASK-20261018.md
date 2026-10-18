# Instalador Stoikus R4 — 18/10/2026

Atualização 1.23.0/R5 com correção R4 da identidade do stage; cálculo 1.9.0 preservado. [Contrato R4](CHG-STOIKUS-INSTALLER-R4-20261018.md) e [recibo](../validation/stoikus-installer-1.0.0-beta.1/R4/INTEGRATION.md). Core67/67, UI18/18, payload12/12 e EXE cruzado próprio. Gate combinado/revisão independente pendentes; nativo/publicação NOT_RUN. Os dois contratos abaixo registram a reconciliação contextual R3 preservada; autorização provém do humano. O runner O2 tem trilha separada pelo executor principal.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-STOIKUS-INSTALLER-R3-CONTEXT-20261018",
  "status": "approved",
  "objective": "Reconciliar somente o contexto factual do instalador atualizado para Stoikus1.23.0/R5; resultados possuem provas próprias",
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
      "docs/work/CHG-STOIKUS-INSTALLER-R3-20261018.md"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "docs/normative/",
      "tools/quality_gate.py",
      ".github/"
    ],
    "allowed_actions": [
      "Registrar contexto, impacto e evidências factuais desta atualização aprovada"
    ],
    "forbidden_actions": [
      "Criar autoridade",
      "Modificar controles ou regras financeiras",
      "Publicar instalador"
    ],
    "regressions_forbidden": [
      "Apagar histórico",
      "Declarar NOT_RUN como PASS",
      "Alterar edição curada congelada"
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
    "python3 tools/agent_instruction_structure_test.py"
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
    "Mudança de alvo ou escopo"
  ],
  "approved_by": "Proprietário nesta conversa",
  "approved_at": "2026-10-18T16:41:27.641740+00:00",
  "authorization_evidence": "Atualizar e concluir também o instalador antes da limpeza final; registro do aceite, não timestamp original da fala"
}
```

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-STOIKUS-INSTALLER-R3-20261018",
  "status": "approved",
  "root": "/private/tmp/jpw-stoikus-installer-20261014",
  "mode": "CONCORRENTE",
  "approved_branch": "codex/stoikus-installer-20261014",
  "create": [
    "docs/work/CHG-STOIKUS-INSTALLER-R3-20261018.md"
  ],
  "modify": [
    "docs/work/ACTIVE-TASK.md",
    "docs/governance/CURRENT-STATE.md",
    "docs/governance/CONTEXT-MAP.md",
    "SESSION_HANDOFF.md"
  ],
  "merge": [],
  "preserve": [
    "Históricos de validação R1/R2",
    "Pacotes MQL e edição documental curada"
  ],
  "do_not_touch": [
    "AGENTS.md",
    "docs/normative/",
    "tools/quality_gate.py",
    ".github/"
  ],
  "archive_requires_confirmation": [],
  "source_of_truth": {
    "engineering": "AGENTS.md e Harness canônico",
    "release": "downloads/jpw-alavancagem-atual/manifest.json",
    "human": "Autorização direta nesta conversa"
  },
  "information_promotion": [
    {
      "from": "Comandos e recibos R3",
      "to": "Contexto atual",
      "reason": "Fatos verificados, sem herdar aprovação dos candidatos anteriores"
    }
  ],
  "expiration_rules": [
    {
      "artifact": "Estado focal R3",
      "event": "Mudança material de bytes ou resultados"
    }
  ],
  "privacy_actions": [
    "Somente fixtures sintéticas; nenhum dado de conta"
  ],
  "acceptance_criteria": [
    "Referências válidas e limites explícitos"
  ],
  "expires_on": [
    "Mudança de alvo ou escopo"
  ],
  "approved_by": "Proprietário nesta conversa",
  "approved_at": "2026-10-18T16:41:27.641740+00:00"
}
```

Fotografia anterior preservada em [HISTORY-BEFORE-INSTALLER-R3-docs__work__ACTIVE-TASK.md-20261018.md](HISTORY-BEFORE-INSTALLER-R3-docs__work__ACTIVE-TASK.md-20261018.md).
