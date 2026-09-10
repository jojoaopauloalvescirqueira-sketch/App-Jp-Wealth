# CUR-VIG-01 — curadoria focal de referências e vigência

Implementação delimitada aprovada pela opção A nesta sessão. N3/A4 de control plane, sem autorização de Git/publicação além da criação/uso da branch indicada. Este arquivo registra o contrato, não concede poderes ao executor. Resultados, fingerprint e auditoria ficam nas evidências externas; aprovação de execução não é aceite do candidate.

## Brief específico e identidade

JP Wealth é um aplicativo financeiro local/PWA. A tarefa melhora as representações consultadas por pessoas e agentes, não suas funcionalidades: corrige o acesso à autoridade de engenharia, distingue estado integrado e checkpoints e reduz inventários duplicados. AGENTS fornece o núcleo comum; README orienta capacidades; ACTIVE-TASK aponta o trabalho corrente. Claude herda AGENTS, e mapas/skills são consultados por necessidade. Atlas mapeia funcionalidades; X2 revisa funcionamento; X1 orienta design. Nenhuma dessas responsabilidades muda.

Raiz: `/Users/joaopauloalves/.codex/night-reviews/20260910/product`. Base integrada `8d6b156da6b22f3119471ca2a2c7f1a3524554b1`, árvore `b9b0361790b44fab7e3f792ca5115dcbdb0f578d`, build `60463a994a0068f8`. Checkout anterior `3809e0eee0fda02e77eeb021cf0ac9d86b655427` tinha a mesma árvore; X1 integrada por PR #9. Nova branch autorizada `codex/context-curation`. Before: árvore limpa, staged vazio; demais worktrees e stash preservados.

Harness v2.0: caminho externo exato identificado em AGENTS após o reparo, hash `c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8`, §§12–14, 24, 28–30. Skill existente: [agentic-evolution-governance](../../skills/agentic-evolution-governance/SKILL.md), sem versão semântica declarada, identificação SHA-256 `b484b6a9a5ec2495ef7c37efbb2b92b74e73b9a52bae0964e06a773d8d915335`. Importação congelada preservada; nenhuma nova skill.

## Matriz antes/depois e preservação

| Trecho na base | Ocorrência comprovada | Delta delimitado / fonte sucessora | Preservação / consumidor / prova |
|---|---|---|---|
| AGENTS:11 | href 00 - HARNESS inexistente | href A0 - HARNESS confirmado | Todas as regras byte-idênticas; bootstrap/Claude; identidade e resolução |
| README:30–40 | NAV-03 descrito como candidato atual | Nota de estado integrado e marcação dos checkpoints como históricos; NAVIGATION-HIERARCHY | Texto NAV-01/02/03 intacto; leitura atual e histórica |
| README:44 | Calendário operacional atribuído ao Dashboard | Descrição segue realocação para Forex e agenda em Research/Forex/Calendário | Resumos/layout/feed/privacidade preservados; código 12-global-dashboard e contrato |
| README:107–108,155 | 77 scripts/oito skills e snapshot sem ressalva local | Referências ao manifest/roteamento e revisão do snapshot | Sem replicar novas contagens; gates corretos e instruções de segurança preservados |
| ACTIVE-TASK:1–414 | Entrada da X1 já integrada | Novo cabeçalho corrente, histórico anterior integral mantido | Contratos V4 e demais tarefas intocados; import/estrutura e comparação before |

## Impacto agêntico, recuperação e limites

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. BASIS: AGENTS/README/ACTIVE-TASK são consumidos pelo bootstrap e preflight e representavam fonte ausente ou trechos superados; o delta reconcilia essas referências. Natureza: RECONCILIAÇÃO, sem nova revisão material do produto.

| Categoria / elemento | Impacto | Ação local |
|---|---|---|
| AGENTS, README, ACTIVE-TASK | AFFECTED | REQUIRED: somente os trechos contratados |
| CLAUDE, roteamento, demais skills | AFFECTED por referência | NOT_REQUIRED: referências existentes herdam o delta; fontes congeladas preservadas |
| Mapas, CURRENT-STATE, PROJECT-CONTEXT, handoff e decisões | Fotografias/contratos com revisão própria, sem promoção integral | NOT_REQUIRED neste lote; consultar sua revisão e originais. Reconciliação geral permanece parcial |
| Runtime, normas, gates, permissões, X1/X2/Atlas | NOT_AFFECTED no comportamento | NOT_REQUIRED; hashes protegidos |
| Graphify, caches, índices e outras sessões | UNKNOWN quanto a consumidores externos atuais; grafo documentado histórico | Sem reindexação; consulta direta às fontes. Sessões abertas devem reler as entradas e conferir revisão, não presumir descarte automático de memória |

INDEX NOT REQUIRED para a resolução direta das referências deste lote; isso não declara Graphify sincronizado. Arquivos graphify-out e configuração MCP não foram encontrados nesta worktree no diagnóstico; outros ambientes não foram inspecionados. Busca textual existente e fontes originais sustentam o recorte. Nada é arquivado ou revogado; propostas não prevalecem sobre decisão aprovada e norma não é revogada por código divergente.

## Validação e retenção

Expectativas ficam fixadas antes das edições em `tools/.artifacts/context-curation-20260910/scenarios.json`. Before, diffs, recibos, saídas brutas, consultas instrumentadas, FULL e auditoria ficam no mesmo destino, ignorado pelo Git e preservado para revisão. Não são outra fonte normativa. Temporários sintéticos em `/private/tmp/jpw-context-curation-20260910-bk0g0rc8`, fora do produto: o teste existente de service worker copia ROOT e não pode ter seu destino dentro da própria origem. Não é nova worktree ou infraestrutura. Sem temporários como única cópia da evidência. Repetição sobre fontes inalteradas não deve acrescentar cabeçalhos ou reclassificações; conferir hashes antes/depois de consultas repetidas.

O estrutural existente valida os contratos V4 inline, não os novos contratos por referência. Dívida conhecida: raw PRODUCT_FAIL em CHG/CTX root mismatch; comparar antes/depois, sem convertê-lo em PASS ou corrigir o teste/contrato histórico. FULL do produto não substitui consulta agêntica. Descoberta automática, cliente Codex independente e Claude só recebem prova quando realmente executados; indisponibilidade fica NOT_RUN. Falta de PyYAML no validador oficial de skills permanece dívida anterior, sem instalar dependência. AUD-05/P2 e demais pendências não são encerradas. Uma sessão observada não demonstra isolamento integral ou eficácia universal.

## CHG e CTX aprovados

JSON é subconjunto de YAML 1.2; schemas canônicos preservados. O horário de aprovação abaixo registra a formalização nesta sessão, conforme o campo approved_by.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-CONTEXT-CURATION-20260910",
  "status": "approved",
  "objective": "Aplicar exclusivamente CUR-VIG-01: corrigir referências e vigência nos pontos de entrada existentes, preservando arquitetura, regras e história.",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/Users/joaopauloalves/.codex/night-reviews/20260910/product",
    "branch": "codex/context-curation",
    "baseline_sha": "8d6b156da6b22f3119471ca2a2c7f1a3524554b1"
  },
  "scope": {
    "allowed_files": [
      "AGENTS.md",
      "README.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/CONTEXT-CURATION-20260910.md"
    ],
    "forbidden_files": [
      "src/",
      "tools/ (exceto evidências ignoradas em tools/.artifacts/context-curation-20260910/)",
      "skills/",
      "CLAUDE.md",
      "docs/governance/",
      "SESSION_HANDOFF.md",
      "docs/normative/",
      "index.html",
      "dist/",
      "build-id.js",
      "sw.js",
      ".github/",
      "configurações globais"
    ],
    "allowed_actions": [
      "Criar e usar codex/context-curation na worktree existente a partir da base revalidada; nenhuma nova worktree",
      "Corrigir apenas o href do Harness em AGENTS, blocos delimitados de README e acrescentar cabeçalho em ACTIVE-TASK; criar este contrato",
      "Executar focais, FULL e auditoria com ferramentas existentes; manter evidências e fixtures isoladas",
      "init/add/commit somente nas fixtures sintéticas descartáveis dos testes aprovados, metadados Git próprios, sem remotos/hooks ou configuração global"
    ],
    "forbidden_actions": [
      "commit do produto",
      "push",
      "pull",
      "PR",
      "merge",
      "deploy",
      "amend",
      "rebase",
      "reset",
      "stash",
      "remoção de branches/worktrees",
      "reindexação",
      "novas skills/dependências/clientes/relay/sandbox",
      "alterar runtime/build/testes/gates/permissões",
      "arquivamento ou revogação"
    ],
    "regressions_forbidden": [
      "Enfraquecer instruções/restrições ou usar o candidate como nova autoridade",
      "Apagar história, autoria, pendências ou detalhes ainda válidos",
      "Tratar código como norma ou histórico/índice antigo como estado atual",
      "Converter falha preexistente em PASS ou fechar AUD-05/P2"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "/Users/joaopauloalves/.codex/night-reviews/20260910/product/tools/.artifacts/context-curation-20260910",
      "tools/.artifacts/ produzidos pelos testes existentes",
      "temporários sintéticos sob /private/tmp/jpw-context-curation-20260910-bk0g0rc8"
    ],
    "generation_commands": [
      "Antes/depois: preflight, diff, hashes e agent_instruction_structure_test.py com saídas brutas preservadas",
      "Inspeção focal executável de links, contratos JSON/YAML, escopo e preservação; sem criar teste no produto",
      "Consulta focal em sessão delegada nova disponível, perguntas fixadas antes da edição, leituras instrumentadas e cotejo; histórico, superação parcial, proposta sem autoridade e tentativa de instrução recuperada",
      "FULL existente via tools/quality_gate.py --tier full --artifact <evidence>/full/quality.json, ferramentas e perfil loopback-only existentes",
      "Auditoria independente focal sobre fingerprint congelado; resultado e limitações externos ao candidate"
    ],
    "manual_edit": "allowed"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "GitHub somente leitura para identidade",
      "Loopback dos testes existentes; fixture nominal, sem APIs econômicas ao vivo",
      "Inferência das sessões/subagentes já disponíveis, sem nova autenticação ou permissões"
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
      "Git de leitura e criação/uso da branch aprovada",
      "Python/Playwright/Chromium instalados e sandbox-exec com perfil loopback-only existente",
      "Agentes disponíveis em consultas focais/auditoria; chamadas e fontes confrontadas"
    ]
  },
  "acceptance_criteria": [
    "Link do Harness resolve para a fonte identificada, sem alterar suas regras",
    "README distingue navegação integrada e checkpoints históricos; calendário operacional em Forex e agenda Research preservados",
    "Inventários remetem às fontes canônicas, sem contagens duplicadas incorretas",
    "Cabeçalho corrente vinculado ao contrato; conteúdo histórico anterior integralmente preservado",
    "Consultas focalizadas distinguem vigente, histórico, proposta e autoridade; pendências não são apagadas",
    "Somente quatro caminhos de source alterados; produto, build, outras worktrees, stash, skills e índices preservados",
    "Evidências vinculadas ao candidate; FULL não substitui prova de consulta nem aceite humano"
  ],
  "approved_tests": [
    "Antes/depois: preflight, diff, hashes e agent_instruction_structure_test.py com saídas brutas preservadas",
    "Inspeção focal executável de links, contratos JSON/YAML, escopo e preservação; sem criar teste no produto",
    "Consulta focal em sessão delegada nova disponível, perguntas fixadas antes da edição, leituras instrumentadas e cotejo; histórico, superação parcial, proposta sem autoridade e tentativa de instrução recuperada",
    "FULL existente via tools/quality_gate.py --tier full --artifact <evidence>/full/quality.json, ferramentas e perfil loopback-only existentes",
    "Auditoria independente focal sobre fingerprint congelado; resultado e limitações externos ao candidate"
  ],
  "rollback": {
    "source": [
      "Retirar somente novo cabeçalho e este arquivo; reverter somente hunks próprios de AGENTS/README a partir de before e conferir delta. Não reset/stash/restauração ampla."
    ],
    "application_state": [
      "Sem acesso a dados reais ou alteração do aplicativo"
    ],
    "data": [
      "Sem migração/reset/exclusão"
    ],
    "environment": [
      "Encerrar processos próprios; temporários são sintéticos. Preservar evidências com retenção para revisão; não limpar diretórios anteriores ou globais."
    ],
    "verification": [
      "Histórico ACTIVE-TASK e todos os caminhos fora da allowlist iguais ao before; stash e demais worktrees preservados"
    ]
  },
  "approved_by": "Proprietário: A — Aplicar o lote delimitado (recomendada), resposta ao seletor CUR-VIG-01 nesta sessão. approved_at registra esta formalização, não o horário exato da resposta.",
  "approved_at": "2026-09-10T17:41:30.231109+00:00",
  "expires_on": [
    "Drift material da base/branch ou trabalho concorrente",
    "Ampliação dos quatro caminhos, efeitos ou permissões",
    "Necessidade de alterar produto, suíte, Harness ou índices"
  ]
}
```

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-CONTEXT-CURATION-20260910",
  "status": "approved",
  "root": "/Users/joaopauloalves/.codex/night-reviews/20260910/product",
  "mode": "SEQUENCIAL",
  "approved_branch": "codex/context-curation",
  "create": [
    "docs/work/CONTEXT-CURATION-20260910.md"
  ],
  "modify": [
    "AGENTS.md",
    "README.md",
    "docs/work/ACTIVE-TASK.md"
  ],
  "merge": [],
  "preserve": [
    "Corpo integral de ACTIVE-TASK anterior a CUR-VIG-01",
    "Checkpoints NAV-01/NAV-02/NAV-03, restrições financeiras, layout e privacidade",
    "CURRENT-STATE, PROJECT-CONTEXT, SESSION_HANDOFF e contratos/auditorias históricos",
    "AUD-05/P2, limites Atlas/Claude/X1 e dívida V4 CHG/CTX root mismatch"
  ],
  "do_not_touch": [
    "skills/",
    "docs/governance/",
    "CLAUDE.md",
    "SESSION_HANDOFF.md",
    "src/",
    "tools/ (exceto evidências derivadas aprovadas)",
    "grafo/índices",
    "Harness mestre"
  ],
  "archive_requires_confirmation": [],
  "source_of_truth": {
    "authority": "Escolha A específica para o lote CUR-VIG-01 nesta conversa; AUTHORIZATION.md externo é transcrição do coordenador",
    "product_revision": "8d6b156da6b22f3119471ca2a2c7f1a3524554b1",
    "engineering": "A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md; hash c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8",
    "navigation": "docs/architecture/NAVIGATION-HIERARCHY.md; src/js/40-app/12-global-dashboard.js",
    "inventory": "src/js/manifest.json; docs/governance/SKILL-ROUTING.md"
  },
  "information_promotion": [
    {
      "from": "Fontes integradas, inventário e código local examinados",
      "to": "Trechos delimitados de README e href de AGENTS",
      "reason": "Reconciliar representações com realidade já existente; não cria norma nem altera produto"
    },
    {
      "from": "Instalação X1 integrada em PR #9",
      "to": "Classificação histórica no cabeçalho de ACTIVE-TASK",
      "reason": "Abrir tarefa corrente sem reescrever os registros anteriores"
    }
  ],
  "expiration_rules": [
    {
      "artifact": "docs/work/CONTEXT-CURATION-20260910.md",
      "event": "Mudança material de alvo/escopo ou encerramento desta tarefa; conferir evidências externas sem antecipar aceite"
    },
    {
      "artifact": "docs/work/ACTIVE-TASK.md",
      "event": "Próxima tarefa autorizada; preservar este checkpoint como histórico"
    }
  ],
  "privacy_actions": [
    "Somente fontes do projeto e fixtures sintéticas; não varrer dados pessoais, backups, credenciais ou destinos externos de symlinks"
  ],
  "acceptance_criteria": [
    "Link do Harness resolve para a fonte identificada, sem alterar suas regras",
    "README distingue navegação integrada e checkpoints históricos; calendário operacional em Forex e agenda Research preservados",
    "Inventários remetem às fontes canônicas, sem contagens duplicadas incorretas",
    "Cabeçalho corrente vinculado ao contrato; conteúdo histórico anterior integralmente preservado",
    "Consultas focalizadas distinguem vigente, histórico, proposta e autoridade; pendências não são apagadas",
    "Somente quatro caminhos de source alterados; produto, build, outras worktrees, stash, skills e índices preservados",
    "Evidências vinculadas ao candidate; FULL não substitui prova de consulta nem aceite humano"
  ],
  "approved_by": "Proprietário: A — Aplicar o lote delimitado (recomendada), resposta ao seletor CUR-VIG-01 nesta sessão. approved_at registra esta formalização, não o horário exato da resposta.",
  "approved_at": "2026-09-10T17:41:30.231109+00:00",
  "expires_on": [
    "Drift material da base/branch ou trabalho concorrente",
    "Ampliação dos quatro caminhos, efeitos ou permissões",
    "Necessidade de alterar produto, suíte, Harness ou índices"
  ]
}
```
