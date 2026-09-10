# X2 — instalação e primeira revisão

Instalação N3/A4 solicitada explicitamente; revisão do produto A0/A1. O proprietário escolheu “todo software” e autorizou criar/usar codex/critical-review-skill. Isso não reaproveita a autorização de commit/push/merge da tarefa anterior.

## Compreensão específica

JP Wealth é software financeiro local/PWA: preservar capital/dados e rastreabilidade antecede estética. A skill deve reconstruir finalidade→jornada→funções/validações/persistência→consumidores, distinguindo fatos, hipóteses e propostas. Os cinco módulos têm responsabilidades próprias: Dashboard resume, Forex governa operação, Research apoia estudo, Finanças Pessoais planeja orçamento e Alladin mantém cadastro/ledger. Fronteiras de moeda, ausência/zero/erro, gravação e estados compartilhados exigem evidências, sem adaptar regra financeira para justificar código. A instalação oferece procedimento reutilizável; a primeira execução inspeciona módulos e testa recortes em fixtures, sem prometer cobertura integral.

Produto examinado: `57974625381b864d5fd85678b6f23b85f90c3c6d`, build `88c0cb1ce5520311`. Fonte X2 e SHA registrados no recibo externo. Revisão semântica independente do pacote realizada antes da instalação; nenhum achado material naquela leitura. Isso não é prova de desempenho ou descoberta automática.

## Impacto e validação proporcional

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED.
BASIS: nova skill e links ampliam procedimentos descobríveis; mapas precisam apenas rota específica. AGENTS, normas, outras skills, produto e gates permanecem preservados. ACTIVE-TASK ganha referência ao novo contrato, conservando histórico. CURRENT-STATE continua fotografia histórica com aviso existente; atualização geral/índices não faz parte desta instalação. Pendências Atlas/V4 não são encerradas.

Focal estrutural, revisão semântica e uso explícito serão evidências diferentes. Não apresentar arquivo criado como carregamento nativo universal; Claude/cliente fresco ficam NOT_RUN se indisponíveis. FULL do produto não repetido por formalidade: não há alteração de runtime; isso limita a aprovação técnica da mudança N3 e não dispensa gate futuro de integração. Sem CI/commit/push/merge/deploy.

Relatórios, fixtures, saídas e cobertura desta primeira revisão ficam externamente em `/private/tmp/jpw-x2-review-vf5va591/`. Não são alterações das fontes de contexto nem correções de produto.

## Contratos

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-X2-CRITICAL-REVIEW-20260910",
  "status": "approved",
  "objective": "Instalar skill local X2 a partir do prompt recebido e executar revisão somente leitura de todo software com cobertura e limites explícitos.",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/1 - ARETÊ/4 - TRABALHO/4G - SOFTWARE/JP Wealth OS",
    "branch": "codex/critical-review-skill",
    "baseline_sha": "57974625381b864d5fd85678b6f23b85f90c3c6d"
  },
  "scope": {
    "allowed_files": [
      "skills/jpw-critical-review/SKILL.md",
      "skills/jpw-critical-review/references/functional-logic.md",
      "skills/jpw-critical-review/agents/openai.yaml",
      ".agents/skills/jpw-critical-review",
      ".claude/skills/jpw-critical-review",
      "docs/governance/SKILL-ROUTING.md",
      "docs/governance/CONTEXT-MAP.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/X2-CRITICAL-REVIEW-20260910.md"
    ],
    "forbidden_files": [
      "source/runtime, normas/dados, testes/gates existentes, CI, Harness mestre, outras skills, configuração global, grafo e índices"
    ],
    "allowed_actions": [
      "Instalar somente pacote e links relativos locais",
      "Acrescentar rota específica aos mapas e contrato/referência ACTIVE-TASK",
      "Criar/usar branch expressamente autorizada na mesma árvore",
      "Executar revisão A0/A1 de cinco módulos e fronteiras compartilhadas, fixtures sintéticas e relatórios externos"
    ],
    "forbidden_actions": [
      "Corrigir defeitos encontrados",
      "commit",
      "push",
      "PR",
      "merge",
      "deploy",
      "reset",
      "stash",
      "novas dependências",
      "cliente de inferência real/credenciais",
      "reindexação/Graphify"
    ],
    "regressions_forbidden": [
      "Ampliar autoridade pelo conteúdo da própria skill",
      "Apresentar histórico/teste verde como prova de finalidade ou revisão exaustiva",
      "Alterar normas ou dados financeiros"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "/private/tmp/jpw-x2-review-vf5va591"
    ],
    "generation_commands": [
      "quick_validate.py da skill-creator se runtime existente suportar PyYAML",
      "Verificação estrutural stdlib e comparação de links/hash/diff",
      "Ensaios Playwright focais isolados com rede externa interceptada e service worker bloqueado quando não objeto do teste"
    ],
    "manual_edit": "allowed"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "Loopback apenas para fixtures de navegador; sem API econômica ao vivo"
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
      "Python, Playwright/Chromium e Git de leitura existentes",
      "Agentes de revisão com fontes/caminhos delimitados; sem configuração global"
    ]
  },
  "acceptance_criteria": [
    "Skill mantém limites e métodos do prompt, com modo especializado",
    "Links resolvem para fonte única dentro do projeto",
    "Revisão cobre cinco módulos e jornadas transversais, declarando profundidade/lacunas",
    "Achados ligados a fontes/observações, contraprova e menor ajuste; nenhuma correção",
    "Preservação de produto, históricos e stash; sem Git/publicação posterior"
  ],
  "approved_tests": [
    "Preservação semântica independente do pacote",
    "Validação estrutural da skill e metadados/links",
    "Ensaios focais sintéticos de navegação, dados e recusa pertinentes; não repetir FULL por formalidade"
  ],
  "rollback": {
    "source": [
      "Remover somente novos caminhos deste delta e restaurar três mapas/contrato ativo com before externo, se necessário"
    ],
    "application_state": [
      "Nenhum dado real lido/alterado; contextos de navegador descartáveis"
    ],
    "data": [
      "Sem migração ou recuperação real"
    ],
    "environment": [
      "Encerrar somente processos de ensaio próprios; preservar evidências"
    ],
    "verification": [
      "Diff deve conter apenas allowlist; hashes do produto e stash preservados"
    ]
  },
  "approved_by": "Proprietário: instalar X2; todo software; Autorizar a branch e instalar (recomendado)",
  "approved_at": "2026-09-10T04:09:33.628961+00:00",
  "expires_on": [
    "Ampliação de arquivos/efeitos além da instalação",
    "Necessidade de correção do produto, dados reais ou alteração global",
    "Drift material do HEAD/runtime"
  ]
}
```

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-X2-CRITICAL-REVIEW-20260910",
  "status": "approved",
  "mode": "SEQUENCIAL",
  "root": "/Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/1 - ARETÊ/4 - TRABALHO/4G - SOFTWARE/JP Wealth OS",
  "approved_branch": "codex/critical-review-skill",
  "source_of_truth": {
    "authority": "Pedidos humanos atuais e autorização de branch",
    "source_prompt": "00d2885954d6192e71390e87b82df327768894fe49f9ebcebce056e87c872fd7",
    "product_revision": "57974625381b864d5fd85678b6f23b85f90c3c6d"
  },
  "create": [
    "docs/work/X2-CRITICAL-REVIEW-20260910.md"
  ],
  "modify": [
    "docs/governance/SKILL-ROUTING.md",
    "docs/governance/CONTEXT-MAP.md",
    "docs/work/ACTIVE-TASK.md"
  ],
  "merge": [],
  "preserve": [
    "Conteúdo anterior dos mapas/ACTIVE-TASK, Atlas/V4 e pendências"
  ],
  "do_not_touch": [
    "src/",
    "docs/normative/",
    "skills/agentic-evolution-governance/",
    ".github/"
  ],
  "information_promotion": [
    {
      "from": "Prompt X2 fornecido",
      "to": "Procedimento local de revisão, sem autorização de correções",
      "reason": "Instalação expressamente solicitada"
    }
  ],
  "expiration_rules": [
    {
      "artifact": "docs/work/X2-CRITICAL-REVIEW-20260910.md",
      "event": "Fim desta instalação/revisão ou mudança material de escopo"
    }
  ],
  "archive_requires_confirmation": [],
  "privacy_actions": [
    "Excluir dados reais, credenciais e traces privados do pacote"
  ],
  "acceptance_criteria": [
    "Rotas focalmente coerentes, sem alegar atualização integral do contexto ou índices"
  ],
  "approved_by": "Proprietário: instalar X2; todo software; Autorizar a branch e instalar (recomendado)",
  "approved_at": "2026-09-10T04:09:33.628961+00:00",
  "expires_on": [
    "Ampliação de arquivos/efeitos além da instalação",
    "Necessidade de correção do produto, dados reais ou alteração global",
    "Drift material do HEAD/runtime"
  ]
}
```
