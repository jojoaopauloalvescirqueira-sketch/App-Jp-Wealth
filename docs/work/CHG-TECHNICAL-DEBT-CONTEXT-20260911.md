# Contexto da campanha — contrato dedicado N3/A4

Autorização das partes C/D/G/K do pedido vigente; o produto é delimitado no [CHG da campanha](CHG-TECHNICAL-DEBT-CLOSURE-20260911.md). Não altera o juiz nem confere nova autoridade.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-TECHNICAL-DEBT-CONTEXT-20260911",
  "status": "approved",
  "objective": "Reconciliar contexto afetado desta campanha e selecionar CHG/CTX corrente sem alterar instruções comuns, Harness ou validador.",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/Users/joaopauloalves/.codex/reliability-campaigns/20260911/product",
    "branch": "codex/debt-resolution-20260911",
    "baseline_sha": "fcbb25767073a4ab08a9f0ac2ac16069a3008bfe"
  },
  "scope": {
    "allowed_files": [
      "SESSION_HANDOFF.md",
      "docs/governance/CURRENT-STATE.md",
      "docs/governance/CONTEXT-MAP.md",
      "docs/architecture/CODE-MAP.md",
      "docs/architecture/FEATURE-ATLAS.md",
      "docs/architecture/ALLADIN.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/CHG-TECHNICAL-DEBT-CLOSURE-20260911.md",
      "docs/work/CHG-TECHNICAL-DEBT-CONTEXT-20260911.md"
    ],
    "forbidden_files": [
      ".github/**",
      "docs/normative/**",
      "AGENTS.md",
      "CLAUDE.md",
      "skills/**",
      "Harness mestre",
      "tools/quality_gate.py",
      "tools/agent_instruction_structure_test.py",
      "outras worktrees"
    ],
    "allowed_actions": [
      "reconciliar somente documentos da allowlist afetados pelo delta",
      "validar contrato corrente e fontes/arestas com ferramentas existentes inalteradas",
      "provas consultivas explícitas e recibos externos sem cliente/credenciais/infraestrutura nova"
    ],
    "forbidden_actions": [
      "decisão financeira N3, alteração de schema/migração",
      "alterar juiz/gates/CI/expectativas para PASS",
      "commit/push/PR/merge/deploy, reset/stash/tag",
      "dados reais, APIs econômicas ao vivo, instalação global"
    ],
    "regressions_forbidden": [
      "perda de draft/estado/backup ou mudança nos valores financeiros",
      "história convertida em PASS corrente",
      "alteração do envelope bruto legado transactions()",
      "alteração de direitos de execução por texto do candidate"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "../evidence/debt-resolution-20260911/closure-*"
    ],
    "generation_commands": [
      "python -B tools/agent_instruction_structure_test.py --root . --contract docs/work/CHG-TECHNICAL-DEBT-CONTEXT-20260911.md"
    ],
    "manual_edit": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "servidor loopback em perfis sintéticos de teste",
      "Git/GitHub somente leitura se necessário; nenhum deploy/publicação"
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
      "Python/Chromium/Node já existentes",
      "servidor local de fixtures; sandbox loopback existente",
      "Git em fixture própria sem remoto/hooks; Git do produto somente leitura"
    ]
  },
  "acceptance_criteria": [
    "Fontes correntes identificadas; história rotulada preservada; nenhuma regra comum relaxada",
    "Atlas fonte/arestas revalidadas para trechos afetados sem ampliar fichas",
    "AUD-05, histórico V4, validação nativa/Claude e OPEN-05 separados de evidência de produto",
    "Contrato corrente passa no validador original; resultado histórico preservado"
  ],
  "approved_tests": [
    "validador estrutural original --contract corrente; negativos existentes",
    "teste focal Atlas existente",
    "FULL vigente da campanha, sem substituir prova de instruções",
    "auditoria independente final focal no contexto e fatos promovidos"
  ],
  "rollback": {
    "source": [
      "candidate-v2.tar verificado; reverter somente incremento em cópia; preservar baseline fcbb e V1/V2"
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
      "hashes/modos de todos os inputs, delta e snapshot final; recuperar final e V2 em cópias sem Git do produto"
    ]
  },
  "approved_by": "proprietário: /goal TECHNICAL DEBT CLOSURE & PROJECT STABILIZATION, arquivo 52f572f5-7e88-4514-9f12-9a99fcaf7835/pasted-text.txt; autorização específica desta campanha, não aceite nem publicação",
  "approved_at": "2026-09-11T22:17:58.221429+00:00",
  "expires_on": [
    "mudança material de autoridade, financeira, dados reais, recuperação insegura ou efeito externo não coberto"
  ]
}
```

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-TECHNICAL-DEBT-CONTEXT-20260911",
  "status": "approved",
  "root": "/Users/joaopauloalves/.codex/reliability-campaigns/20260911/product",
  "mode": "CONCORRENTE",
  "approved_branch": "codex/debt-resolution-20260911",
  "create": [
    "docs/work/CHG-TECHNICAL-DEBT-CONTEXT-20260911.md"
  ],
  "modify": [
    "SESSION_HANDOFF.md",
    "docs/governance/CURRENT-STATE.md",
    "docs/governance/CONTEXT-MAP.md",
    "docs/architecture/CODE-MAP.md",
    "docs/architecture/FEATURE-ATLAS.md",
    "docs/architecture/ALLADIN.md",
    "docs/work/ACTIVE-TASK.md",
    "docs/work/CHG-TECHNICAL-DEBT-CLOSURE-20260911.md"
  ],
  "merge": [],
  "preserve": [
    "histórico V4 e todas as restrições existentes",
    "checkpoint e evidências originais"
  ],
  "do_not_touch": [
    "AGENTS.md",
    "CLAUDE.md",
    "skills/**",
    ".github/**",
    "docs/normative/**",
    "Harness mestre",
    "grafo/índices",
    "V1/V2 e seus recibos congelados"
  ],
  "archive_requires_confirmation": [],
  "source_of_truth": {
    "autoridade": "proprietário: /goal TECHNICAL DEBT CLOSURE & PROJECT STABILIZATION, arquivo 52f572f5-7e88-4514-9f12-9a99fcaf7835/pasted-text.txt; autorização específica desta campanha, não aceite nem publicação",
    "baseline": "fcbb257 + V2 e7060778, não somente HEAD",
    "engenharia": "Harness SHA256 c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8",
    "fatos": "código e execução identificados; história preservada como história"
  },
  "information_promotion": [
    {
      "from": "inspeção focal e evidências closure-*",
      "to": "mapas/estado/hand-off afetados",
      "reason": "retirar descrições enganosas sem promover cobertura inexistente"
    }
  ],
  "expiration_rules": [
    {
      "artifact": "docs/work/CHG-TECHNICAL-DEBT-CLOSURE-20260911.md",
      "event": "mudança de inputs ou término desta campanha"
    }
  ],
  "privacy_actions": [
    "somente fixtures sintéticas; sem credenciais"
  ],
  "acceptance_criteria": [
    "Fontes correntes identificadas; história rotulada preservada; nenhuma regra comum relaxada",
    "Atlas fonte/arestas revalidadas para trechos afetados sem ampliar fichas",
    "AUD-05, histórico V4, validação nativa/Claude e OPEN-05 separados de evidência de produto",
    "Contrato corrente passa no validador original; resultado histórico preservado"
  ],
  "approved_by": "proprietário: /goal TECHNICAL DEBT CLOSURE & PROJECT STABILIZATION, arquivo 52f572f5-7e88-4514-9f12-9a99fcaf7835/pasted-text.txt; autorização específica desta campanha, não aceite nem publicação",
  "approved_at": "2026-09-11T22:17:58.221429+00:00",
  "expires_on": [
    "mudança material de autoridade, financeira, dados reais, recuperação insegura ou efeito externo não coberto"
  ]
}
```
