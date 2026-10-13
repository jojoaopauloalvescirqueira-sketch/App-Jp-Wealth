# Tarefa ativa — correções de uso Stoikus — 2026-10-13

Data da fotografia: 2026-10-13

Source revision representada: `0f247215cc20829fdba40c3b33458ee976c17ea1`

Base Git mais o delta local autorizado em `codex/stoikus-renaming-20261012`, raiz `/private/tmp/jpw-stoikus-renaming-20261012`. O proprietário pediu corrigir a experiência de uso e escolheu o Position Sizer da EarnForex como referência Gauntlet. Produto 1.22.1 / MQL 1.221 / cálculo 1.9.0. Pacote de uso separado da engenharia, Entradas explicadas e abertura conjunta de Conta/NoCuda. Implementação local concluída: host/distribuição PASS 44/44 e site full PASS 57/57 no freeze R4, com revisões independentes de código e clareza documental/web. Nenhuma aprovação dos bytes 1.22.0 é transferida. Compilação e ciclo nativo continuam NOT_RUN.

Monitor em gráfico de apoio; Conta e NoCuda no trabalho. Fórmulas, parâmetros padrão, identidades persistidas, locks, preferências e estudos preservados. Supervisor opcional não armado; Fibonacci importado continua pendente. Compilação/execução MT5, instalação e aceite operacional: NOT_RUN até prova exata. Git e publicação separados. Baseline 1.22.0 congelada em `/private/tmp/jpw-stoikus-usability-baseline-20261013`; evidências próprias em `/private/tmp/jpw-stoikus-usability-evidence-20261013`.

[Design](../superpowers/specs/2026-10-13-stoikus-usage-design.md) · [Plano](../superpowers/plans/2026-10-13-stoikus-usage.md)


## Registro estrutural do contexto corrente

Os campos approved_at abaixo são a data do registro documental da autorização conversacional; não representam timestamp extraído das mensagens. A autorização decorre do pedido humano citado, e o teste desses campos prova apenas sua estrutura.

```yaml
{
  "status": "approved",
  "approved_by": "Proprietário nesta conversa; registro do pedido explícito de correção",
  "approved_at": "2026-10-13T15:48:45.976830+00:00",
  "authorization_evidence": "que voce corrija os meus problemas apresentados, de acordo com aquilo que é adequado",
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-STOIKUS-USAGE-CONTEXT-20261013",
  "objective": "Reconciliar apenas a documentação focal da correção de uso autorizada, preservando o histórico",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/private/tmp/jpw-stoikus-renaming-20261012",
    "branch": "codex/stoikus-renaming-20261012",
    "baseline_sha": "0f247215cc20829fdba40c3b33458ee976c17ea1"
  },
  "scope": {
    "allowed_files": [
      "docs/work/CHG-STOIKUS-USAGE-CONTEXT-20261013.md",
      "docs/work/CHG-STOIKUS-USAGE-20261013.md",
      "docs/superpowers/specs/2026-10-13-stoikus-usage-design.md",
      "docs/superpowers/plans/2026-10-13-stoikus-usage.md",
      "docs/work/HISTORY-STOIKUS-1_22_0-docs__governance__CURRENT-STATE.md",
      "docs/work/HISTORY-STOIKUS-1_22_0-docs__governance__CONTEXT-MAP.md",
      "docs/work/HISTORY-STOIKUS-1_22_0-docs__work__ACTIVE-TASK.md",
      "docs/work/HISTORY-STOIKUS-1_22_0-SESSION_HANDOFF.md",
      "docs/work/HISTORY-STOIKUS-1_22_0-README.md",
      "docs/governance/CURRENT-STATE.md",
      "docs/governance/CONTEXT-MAP.md",
      "docs/work/ACTIVE-TASK.md",
      "SESSION_HANDOFF.md"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "CLAUDE.md",
      "docs/normative/",
      "docs/decisions/",
      "tools/quality_gate.py",
      ".github/"
    ],
    "allowed_actions": [
      "Registrar pedido humano e referência escolhida",
      "Atualizar contexto focal e preservar fotografias históricas",
      "Registrar provas próprias e limites reais"
    ],
    "forbidden_actions": [
      "Criar autoridade financeira ou homologação",
      "Alterar dados/critério de qualidade",
      "Git ou publicação não autorizados",
      "Reativar instruções AGENTS revogadas"
    ],
    "regressions_forbidden": [
      "Apagar histórico",
      "Transferir aprovação de outro candidate",
      "Fingir execução nativa ou cegamento completo"
    ]
  },
  "derived_artifacts": {
    "allowed": [],
    "generation_commands": [],
    "manual_edit": "allowed"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "Fontes primárias da referência escolhida",
      "Loopback sintético"
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
      "Python",
      "Chromium descartável",
      "C++ host",
      "Node bundled",
      "Git somente leitura"
    ]
  },
  "acceptance_criteria": [
    "Estado focal correto e mesmo SHA base",
    "Históricos byte-idênticos preservados",
    "Sem conclusão nativa ou publicação simulada"
  ],
  "approved_tests": [
    "agent_instruction_structure_test.py com controles negativos",
    "preflight_context_test.py",
    "quality_gate.py --tier full"
  ],
  "rollback": {
    "source": [
      "Repor somente contexto do delta 1.22.1 pela baseline congelada"
    ],
    "application_state": [],
    "data": [],
    "environment": [
      "Encerrar apenas processos próprios de testes"
    ],
    "verification": [
      "Conferir hashes da baseline e Source revision"
    ]
  },
  "expires_on": [
    "Mudança material de escopo",
    "Troca de raiz/branch/base sem reconciliação"
  ]
}
```

```yaml
{
  "status": "approved",
  "approved_by": "Proprietário nesta conversa; registro do pedido explícito de correção",
  "approved_at": "2026-10-13T15:48:45.976830+00:00",
  "authorization_evidence": "que voce corrija os meus problemas apresentados, de acordo com aquilo que é adequado",
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-STOIKUS-USAGE-20261013",
  "root": "/private/tmp/jpw-stoikus-renaming-20261012",
  "mode": "CONCORRENTE",
  "approved_branch": "codex/stoikus-renaming-20261012",
  "create": [
    "docs/work/CHG-STOIKUS-USAGE-CONTEXT-20261013.md",
    "docs/work/CHG-STOIKUS-USAGE-20261013.md",
    "docs/superpowers/specs/2026-10-13-stoikus-usage-design.md",
    "docs/superpowers/plans/2026-10-13-stoikus-usage.md",
    "docs/work/HISTORY-STOIKUS-1_22_0-docs__governance__CURRENT-STATE.md",
    "docs/work/HISTORY-STOIKUS-1_22_0-docs__governance__CONTEXT-MAP.md",
    "docs/work/HISTORY-STOIKUS-1_22_0-docs__work__ACTIVE-TASK.md",
    "docs/work/HISTORY-STOIKUS-1_22_0-SESSION_HANDOFF.md",
    "docs/work/HISTORY-STOIKUS-1_22_0-README.md"
  ],
  "modify": [
    "docs/governance/CURRENT-STATE.md",
    "docs/governance/CONTEXT-MAP.md",
    "docs/work/ACTIVE-TASK.md",
    "SESSION_HANDOFF.md"
  ],
  "merge": [],
  "preserve": [
    "Contexto 1.22.0 copiado byte a byte",
    "Registros normativos e evidências históricas"
  ],
  "do_not_touch": [
    "AGENTS.md",
    "CLAUDE.md",
    "docs/normative/",
    "docs/decisions/",
    "tools/quality_gate.py",
    ".github/"
  ],
  "archive_requires_confirmation": [],
  "source_of_truth": {
    "human": "Pedido explícito de correção nesta conversa e seleção Position Sizer",
    "product": "mt5/jpw-alavancagem-atual/STOIKUS_USO_DIARIO.md",
    "reference": "https://www.earnforex.com/metatrader-expert-advisors/Position-Sizer/",
    "evidence": "/private/tmp/jpw-stoikus-usability-evidence-20261013"
  },
  "information_promotion": [
    {
      "from": "Diagnóstico e pedido humano",
      "to": "Estado focal da correção local",
      "reason": "Documentar somente implementação e provas efetivamente obtidas"
    }
  ],
  "expiration_rules": [
    {
      "artifact": "Recibos da revisão 1.22.1",
      "event": "Mudança de inputs testados"
    }
  ],
  "privacy_actions": [
    "Somente fixtures sintéticas; não ler dados de conta para testes"
  ],
  "acceptance_criteria": [
    "Um estado focal corrente sem herança de PASS",
    "Histórico preservado em arquivos próprios",
    "Contrato estrutural não apresentado como prova de autorização humana"
  ],
  "expires_on": [
    "Escopo/raiz/branch divergirem"
  ]
}
```

[Fotografia anterior completa, preservada](HISTORY-STOIKUS-1_22_0-docs__work__ACTIVE-TASK.md).
