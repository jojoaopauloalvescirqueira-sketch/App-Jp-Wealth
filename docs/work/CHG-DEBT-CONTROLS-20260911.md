# CHG-DEBT-CONTROLS-20260911 — seleção explícita de contrato

N3/A4 de control plane, separado do reparo de produto. A falha V4 histórica por
root mismatch permanece no modo histórico. O novo modo verifica uma fonte
explicitamente indicada e não decide autoridade humana por existência de campos.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-DEBT-CONTROLS-20260911",
  "status": "approved",
  "objective": "Reparar seleção do contrato estrutural vigente, preservando o diagnóstico histórico e todos os controles; sem alterar o gate do produto.",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/Users/joaopauloalves/.codex/reliability-campaigns/20260911/product",
    "branch": "codex/debt-resolution-20260911",
    "baseline_sha": "fcbb25767073a4ab08a9f0ac2ac16069a3008bfe"
  },
  "scope": {
    "allowed_files": [
      "tools/agent_instruction_structure_test.py",
      "docs/work/CHG-DEBT-CONTROLS-20260911.md",
      "docs/work/ACTIVE-TASK.md"
    ],
    "forbidden_files": [
      "produto, normas, Harness, CI, configurações globais, outras skills e qualquer caminho fora da allowlist"
    ],
    "allowed_actions": [
      "seleção explícita de contrato local, mantendo fallback histórico inalterado",
      "testes estruturais positivos e negativos em fixtures sintéticas isoladas, auditoria focal e FULL vigente"
    ],
    "forbidden_actions": [
      "enfraquecer root, branch, baseline ou allowlist",
      "reescrever contratos históricos",
      "instalações globais, credenciais, APIs financeiras, Graphify",
      "commit do produto, push, PR, merge, deploy"
    ],
    "regressions_forbidden": [
      "contrato histórico tratado como autoridade vigente",
      "aceitar escape de caminho ou symlink",
      "classificar resultado histórico falho como PASS",
      "mudar checks do produto para aceitar defeito"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "../evidence/debt-resolution-20260911/control-*"
    ],
    "generation_commands": [
      "python3 -B tools/agent_instruction_structure_test.py --root . --contract docs/work/CHG-DEBT-CONTROLS-20260911.md"
    ],
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
      "Python existente",
      "Git somente em fixture própria sem remoto e hooks externos"
    ]
  },
  "acceptance_criteria": [
    "Modo explícito seleciona apenas docs/work/*.md canônico sem symlink e mostra identidade do contrato",
    "Preservar todos os campos, validações, ancestralidade, fontes e negativos existentes",
    "Modo explícito exige branch vigente e status approved; fallback conserva resultado histórico",
    "Auditoria focal e vínculo com candidate; nenhum PASS de runtime inferido"
  ],
  "approved_tests": [
    "Self-test existente ampliado com negativos de caminho, arquivo, raiz, branch e estado",
    "execução real do modo explícito e contraprova do modo histórico",
    "FULL existente independente, sem alterar ferramentas ou workflow para passar"
  ],
  "rollback": {
    "source": [
      "baseline.tar e diff próprio em ../evidence/debt-resolution-20260911; recuperar somente este delta em cópia"
    ],
    "application_state": [
      "nenhuma alteração de estado do aplicativo"
    ],
    "data": [
      "fixtures sintéticas, sem dados reais"
    ],
    "environment": [
      "preservar stash, outras worktrees e evidências"
    ],
    "verification": [
      "hashes, negativos e comparação antes/depois"
    ]
  },
  "approved_by": "proprietário: pedido vigente resolva todas as dívidas abertas; implementação técnica delimitada, não aceite nem publicação",
  "approved_at": "2026-09-11T21:02:18.565131+00:00",
  "expires_on": [
    "mudança de autoridade, raiz, baseline, conflito ou expansão de allowlist"
  ]
}
```

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-DEBT-CONTROLS-20260911",
  "status": "approved",
  "root": "/Users/joaopauloalves/.codex/reliability-campaigns/20260911/product",
  "mode": "SEQUENCIAL",
  "approved_branch": "codex/debt-resolution-20260911",
  "create": [
    "docs/work/CHG-DEBT-CONTROLS-20260911.md"
  ],
  "modify": [
    "tools/agent_instruction_structure_test.py",
    "docs/work/ACTIVE-TASK.md"
  ],
  "merge": [],
  "preserve": [
    "histórico V4 e todas as restrições existentes",
    "checkpoint e evidências originais"
  ],
  "do_not_touch": [
    "AGENTS.md",
    "CLAUDE.md",
    "src",
    "dist",
    ".github",
    "docs/normative",
    "skills"
  ],
  "archive_requires_confirmation": [],
  "source_of_truth": {
    "autoridade": "pedido humano vigente; contrato não amplia permissões",
    "engenharia": "AGENTS.md e Harness v2.0 c1b5ca9d...800c8",
    "histórico": "V4 inline permanece fonte apenas do modo histórico"
  },
  "information_promotion": [
    {
      "from": "diagnóstico estrutural focal",
      "to": "docs/work/CHG-DEBT-CONTROLS-20260911.md",
      "reason": "delimitar seleção de fonte atual sem reescrever a história"
    }
  ],
  "expiration_rules": [
    {
      "artifact": "docs/work/CHG-DEBT-CONTROLS-20260911.md",
      "event": "mudança material de inputs ou escopo"
    }
  ],
  "privacy_actions": [
    "somente fixtures sintéticas; sem credenciais"
  ],
  "acceptance_criteria": [
    "Modo explícito seleciona apenas docs/work/*.md canônico sem symlink e mostra identidade do contrato",
    "Preservar todos os campos, validações, ancestralidade, fontes e negativos existentes",
    "Modo explícito exige branch vigente e status approved; fallback conserva resultado histórico",
    "Auditoria focal e vínculo com candidate; nenhum PASS de runtime inferido"
  ],
  "approved_by": "proprietário: pedido vigente resolva todas as dívidas abertas; implementação técnica delimitada, não aceite nem publicação",
  "approved_at": "2026-09-11T21:02:18.565131+00:00",
  "expires_on": [
    "mudança de autoridade, raiz, baseline, conflito ou expansão de allowlist"
  ]
}
```

## Matriz antes/depois

| Controle | Antes | Depois |
|---|---|---|
| Fonte | somente contratos inline históricos | mesma fonte por padrão; alternativa explícita validada e identificada |
| Raiz | root literal igual ao checkout | preservado integralmente nos dois modos |
| Branch | notice no histórico | histórico igual; modo explícito exige branch contratada |
| Baseline/allowlist/tipos | validação existente | preservada, com negativos adicionais |
| Import e referências | validação existente | preservada sem leitura ampla |
| Aprovação | campos estruturados, sem autenticação | mesma limitação explícita; fonte atual deve estar approved |
| CI/produto | FULL independente | nenhum check/expectativa/CI alterado |

Validação planejada: negativos definidos acima, execução explícita, raw histórico,
auditoria independente. FULL do produto não comprova instruções. Sem integração.
