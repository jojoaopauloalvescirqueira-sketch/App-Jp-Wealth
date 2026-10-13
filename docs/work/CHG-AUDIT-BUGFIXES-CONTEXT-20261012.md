# CHG/CTX — registros factuais da correção — 12/10/2026

A primeira tentativa de CHG/ACTIVE/CURRENT foi rejeitada pelo auto-review e não executou gravação. O proprietário então autorizou explicitamente os registros delimitados apresentados em PROPOSTA-CONTEXTO.md. Este contrato não cria autorização: registra a resposta humana vigente, sem alterar as regras que julgam o próprio executor. approved_at registra a hora do registro; o timestamp da resposta humana não foi exposto pelo cliente.

Objetivo: descrever escopo/branch/base e estado real deAUD01..10; atualizar contexto no encerramento por evidência, mantendo histórico anterior no Git0f24721. Produto/juiz separados: correções sob CHG-AUDIT-BUGFIXES-20261012; este registroN3 não altera AGENTS, normativas, gatesequalquer código ou teste decontrole. AutoridadeA4 específica documental; commit/push/merge/deploy não incluídos. FonteengineeringHarness SHA256b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95 e AGENTScorrentes; confrontoantes/depois por BASE_SHA.

Compreensão: o produto organiza dados financeiros e exige rastreabilidade; estes cinco documentos roteiam somente a tarefa corrente e seu handoff. Hoje apontam à integração passada; passam a registrar a correção em andamento, depois fatos finais comprovados. Agentes que lêem ACTIVE/CURRENT/handoff consomem a referência atual sem mudança em suas instruções. Dados, parâmetros, contratos financeiros e política de aprovação ficam intactos. Prova: diff integral, estado Git, estrutura do contrato e auditoria independente/full final. ClienteClaude e uso em sessões novas são NOT_RUN se indisponíveis; não alegar imposição/carregamento por existência de arquivo. Rollback: textos anteriores no Git e cópia externa. Não reindexar, propagar para outros projetos ou atualizar memória global.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-AUDIT-BUGFIXES-CONTEXT-20261012",
  "status": "approved",
  "approved_by": "Proprietario — resposta explicita nesta conversa",
  "approved_at": "2026-10-12T23:01:01.811277+00:00",
  "authorization_evidence": "corrija os bugs encontrados na auditoria; Autorizar essa branch e as correções delimitadas; Autorizar esses registros delimitados",
  "objective": "Registrar somente escopo, execução e pendências da correção autorizada; sem alterar juízes, regras, autoridade ou gates",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/99B - SOFTWARES & EAS/JP Wealth OS",
    "branch": "codex/audit-bugfixes-20261012",
    "baseline_sha": "0f247215cc20829fdba40c3b33458ee976c17ea1"
  },
  "scope": {
    "allowed_files": [
      "docs/work/CHG-AUDIT-BUGFIXES-20261012.md",
      "docs/work/CHG-AUDIT-BUGFIXES-CONTEXT-20261012.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/governance/CURRENT-STATE.md",
      "SESSION_HANDOFF.md"
    ],
    "forbidden_files": [
      "AGENTS.md",
      "CLAUDE.md",
      "docs/normative/",
      "docs/decisions/",
      "src/",
      "sw.js",
      "tools/",
      ".github/",
      "mt5/"
    ],
    "allowed_actions": [
      "Registrar brief/contrato já autorizado, branch/base e limites",
      "Registrar tarefa atual em ACTIVE/CURRENT preservando fotografia anterior no Git",
      "Registrar handoff final observado sem antecipar execução/aceite",
      "Aplicar auditoria independente factual e testes estruturais/full exigidos"
    ],
    "forbidden_actions": [
      "Commit/push/merge/publicacao ou outra operacaoGit nao solicitada",
      "Alterar percentual/formula/politica/Estatuto ou resolver conflitos FCR/FEO",
      "Alterar dados reais/schema/defaults ou normalizar historico",
      "Alterar autoridade/gates/juizes de aprovacao",
      "Refatoracao ampla ou correcoes fora dos10 IDs"
    ],
    "regressions_forbidden": [
      "Perda/truncamento de fato ou rascunho",
      "Null/invalido virar zero conhecido",
      "Excecao generica ou teste enfraquecido para passar",
      "Takeover/skipWaiting/recarga PWA forcada"
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
      "Loopback sintético",
      "GitHub configurado — somente leitura"
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
      "Python temporario Playwright ja autorizado",
      "Node bundled",
      "Chromium temporario ja autorizado",
      "git — branch autorizada e leitura"
    ]
  },
  "acceptance_criteria": [
    "Registros descrevem somente tarefa autorizada e fatos observados",
    "Nenhuma norma/autoridade/gate/juiz alterado",
    "História anterior preservada em BASE_SHA",
    "Auditória independente efullfinal; sem autoaceite ou Git/publicação"
  ],
  "approved_tests": [
    "agent_instruction_structure_test --contract docs/work/CHG-AUDIT-BUGFIXES-CONTEXT-20261012.md",
    "preflight_context_test",
    "quality_gate full final",
    "Auditoria independente factual dos registros e patch"
  ],
  "rollback": {
    "source": [
      "Backup externo dos fontes preexistentes e BASE_SHA; reverter somente patch desta tarefa mediante pedido"
    ],
    "application_state": [
      "Nenhum dado real acessado; fixtures sinteticas"
    ],
    "data": [
      "Nenhuma migracao ou reescrita historica"
    ],
    "environment": [
      "Encerrar servidores/processos descartaveis"
    ],
    "verification": [
      "Hashes e status do candidate final"
    ]
  },
  "expires_on": [
    "Mudanca material de escopo",
    "Fim da tarefa"
  ]
}
```

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-AUDIT-BUGFIXES-20261012",
  "status": "approved",
  "approved_by": "Proprietario — resposta explicita nesta conversa",
  "approved_at": "2026-10-12T23:01:01.811277+00:00",
  "authorization_evidence": "Autorizar esses registros delimitados — resposta humana explícita depois da proposta de8 arquivos",
  "root": "/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/99B - SOFTWARES & EAS/JP Wealth OS",
  "mode": "CONCORRENTE",
  "approved_branch": "codex/audit-bugfixes-20261012",
  "create": [
    "docs/work/CHG-AUDIT-BUGFIXES-20261012.md",
    "docs/work/CHG-AUDIT-BUGFIXES-CONTEXT-20261012.md"
  ],
  "modify": [
    "docs/work/ACTIVE-TASK.md",
    "docs/governance/CURRENT-STATE.md",
    "SESSION_HANDOFF.md"
  ],
  "merge": [],
  "preserve": [
    "Fotografias anteriores noGit BASE_SHA",
    "Todas as normas, instruções e autoridade/gates",
    "Fonte/report anterior histórico integral"
  ],
  "do_not_touch": [
    "AGENTS.md",
    "CLAUDE.md",
    "docs/normative/",
    "docs/decisions/",
    "src/",
    "sw.js",
    "tools/",
    ".github/",
    "mt5/"
  ],
  "source_revision": "0f247215cc20829fdba40c3b33458ee976c17ea1",
  "archive_requires_confirmation": [],
  "source_of_truth": {
    "human": "Resposta humana explícita à proposta documental delimitada nesta conversa",
    "engineering": "AGENTS e HarnessSHA256b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95",
    "product": "CHG-AUDIT-BUGFIXES-20261012"
  },
  "information_promotion": [
    {
      "from": "Evidências de execução observadas",
      "to": "Contexto da tarefa",
      "reason": "Retomada consistente sem antecipar resultado ou aceite"
    }
  ],
  "expiration_rules": [
    {
      "artifact": "Contexto operacional desta tarefa",
      "event": "Mudança material do candidate/resultado/escopo"
    }
  ],
  "privacy_actions": [
    "Dados sintéticos somente; nenhuma memória global alterada"
  ],
  "acceptance_criteria": [
    "Registros descrevem somente tarefa autorizada e fatos observados",
    "Nenhuma norma/autoridade/gate/juiz alterado",
    "História anterior preservada em BASE_SHA",
    "Auditória independente efullfinal; sem autoaceite ou Git/publicação"
  ],
  "expires_on": [
    "Mudanca material de escopo",
    "Fim da tarefa"
  ]
}
```
