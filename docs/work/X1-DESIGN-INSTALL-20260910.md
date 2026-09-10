# X1 — instalação permanente delimitada

Instalação N3/A4 expressamente autorizada pela opção A do pacote delimitado. Branch criada na base integrada e pacote aplicado; validações e auditoria ainda devem ser conferidas nas evidências externas. A aprovação do pacote não é aceite técnico do candidate. Não reaproveita autorização de integração da revisão noturna.

## Brief e fontes

JP Wealth organiza finanças e risco em aplicativo local/PWA. Esta entrega modifica somente os procedimentos consumidos pelos agentes: a X1 deve orientar design conforme finalidade/contratos e evidência, sem modificar o produto. Runtime, fontes financeiras, persistência e preferências não entram no delta. Atlas localiza features/consumidores; X2 mantém crítica técnica; X1 acrescenta filosofia e experiência.

Base integrada: `f4b629c7e8b1131ba12bedb4f4896542adf46644`; build `60463a994a0068f8`; árvore `231be8cec184812f527cd60f780913710d2158a3`. Worktree disponível em `/Users/joaopauloalves/.codex/night-reviews/20260910/product`, inicialmente limpa em `codex/night-review-20260910`/`f41c1ed88f09253a34a19185f623ff4dfd8c2601`, mesma árvore. PR #8 já mesclado. Original local main e stash preservados.

Fonte X1: v1.0, base de pesquisa 09/09/2026; SHA-256 `fcc11d3eab563f3464e84e5b8886ddb9ee4784cff75530702f07776d19e0dff7`. Texto integral recebido em `/Users/joaopauloalves/.codex/attachments/e7cef4df-7bd6-484a-838d-1aa79b785010/pasted-text.txt`, destinado à referência única da skill. O prompt não é norma Apple. Auditoria de compatibilidade reutilizada de `/Users/joaopauloalves/.codex/design-reviews/20260910-x1/REPORT.md`, sem repetir revisão do produto nem encerrar X1-01 a X1-04.

Harness real: arquivo `A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md`, SHA-256 `c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8`; AGENTS aponta nome antigo, não editado aqui. Contexto é carregado por finalidade conforme mapas existentes, não por varredura geral.

## Preservação e validação

| Restrição/necessidade | Destino no pacote | Evidência planejada |
|---|---|---|
| Sete modos e autoridade delimitada | Fonte integral + tabela operacional SKILL | Comparação hash e revisão semântica independente |
| Fonte única e leitura progressiva | references/design-philosophy.md e roteamento por seção | Links resolvidos dentro da raiz; uso focal com fontes/calls |
| Preservar Atlas/X2/Harness | Bloco de responsabilidades; mapas apenas aditivos | Diff integral, hashes das outras skills/instruções |
| Não corrigir interface/dados | CHG/CTX e contrato ativo específico | Runtime/build byte-idênticos |
| Não confundir instalação com execução/publicação | Entrada/relato em quatro estados | Prova explícita de leitura/aplicação; automático/Claude separados |

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. BASIS: a nova skill altera procedimento local descobrível e rotas. Reconciliação autorizável limitada aos três documentos de conexão e contrato próprio; não promove atualização geral de CURRENT-STATE/índices. A avaliação IMPACT final deve distinguir alteração aplicada, conexão e uso realmente observado.

Limites prévios das ferramentas: Python padrão e venv de testes não têm PyYAML; quick_validate depende dele. Não instalar nem simular esse módulo. O teste estrutural existente foi criado para o núcleo V4 e lê os contratos históricos embutidos em ACTIVE-TASK; seu PASS não valida os novos contratos por referência, nem descoberta/carregamento X1. Não mudar esse teste para obter aprovação. Informar resultados e limites separados.

Prova de uso prevista: invocação explícita em subagente novo disponível, com tarefa sintética consultiva curta, acesso por caminhos e referências originais, sem entregar a resposta de referência nem o diagnóstico ao avaliador. Examinar tool calls, trechos consultados e resposta; não atribuir execução pessoal a evidência herdada. Cliente novo/Claude indisponíveis ficam NOT_RUN. Não construir sandbox/relay ou lançar cliente com permissões novas.

Depois dos focais e freeze, executar FULL existente com barreira loopback-only e fixtures nominais já adotadas; permitir somente os temporários da suíte. FULL não substitui validação agêntica. Auditoria independente focal no mesmo fingerprint; alteração após freeze invalida as evidências afetadas. Sem aprovação prévia de resultado ou alegação de interface corrigida.

## Contratos autorizados

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-X1-DESIGN-INSTALL-20260910",
  "status": "approved",
  "objective": "Instalar permanentemente a X1 no projeto em modo ADOTAR_FILOSOFIA, sem alterar a interface.",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/Users/joaopauloalves/.codex/night-reviews/20260910/product",
    "branch": "codex/x1-design-skill",
    "baseline_sha": "f4b629c7e8b1131ba12bedb4f4896542adf46644"
  },
  "scope": {
    "allowed_files": [
      "skills/jpw-design/SKILL.md",
      "skills/jpw-design/references/design-philosophy.md",
      ".agents/skills/jpw-design",
      ".claude/skills/jpw-design",
      "docs/governance/SKILL-ROUTING.md",
      "docs/governance/CONTEXT-MAP.md",
      "docs/work/ACTIVE-TASK.md",
      "docs/work/X1-DESIGN-INSTALL-20260910.md"
    ],
    "forbidden_files": [
      "src/",
      "index.html",
      "build-id.js",
      "dist/",
      "sw.js",
      "docs/normative/",
      "AGENTS.md",
      "CLAUDE.md",
      "outras skills",
      "tools/",
      ".github/",
      "configurações globais"
    ],
    "allowed_actions": [
      "Criar e usar codex/x1-design-skill a partir da main integrada revalidada, na worktree limpa existente; sem nova worktree",
      "Aplicar somente os oito caminhos descritos após aprovação específica",
      "Executar uso focal consultivo e auditoria por agentes disponíveis, mantendo evidências externas",
      "Executar validadores/gates existentes e suas fixtures sintéticas descartáveis; init/add/commit somente nessas fixtures próprias e sem remotos/hooks"
    ],
    "forbidden_actions": [
      "Corrigir X1-01 a X1-04",
      "commit no produto",
      "push",
      "PR",
      "merge",
      "deploy",
      "amend",
      "rebase",
      "reset",
      "stash",
      "reindexação",
      "dependências novas",
      "cliente/relay/sandbox novo",
      "alterar permissões",
      "dados reais"
    ],
    "regressions_forbidden": [
      "Ampliar autoridade por modo da skill",
      "Duplicar a filosofia em agentes",
      "Substituir obrigações Atlas/X2/Harness",
      "Tratar histórico/arquivo/link como validação atual"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "/Users/joaopauloalves/.codex/skill-installations/x1-20260910/evidence",
      "tools/.artifacts/",
      "temporários sintéticos dos testes existentes sob TMPDIR dedicado"
    ],
    "generation_commands": [
      "Validadores e observações focais existentes; comandos registrados com saídas",
      "tools/quality_gate.py --tier full --artifact <evidence>/quality.json pelo perfil loopback-only já existente",
      "Build-reproducibility somente em cópias temporárias que a própria suíte existente cria; nenhum rebuild da árvore do produto"
    ],
    "manual_edit": "allowed"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "Consulta GitHub somente leitura para revalidar identidade/base",
      "Loopback e respostas sintéticas do helper existente para testes",
      "Inferência da sessão/subagentes já disponíveis; nenhuma nova autenticação/relay"
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
      "Git local para branch aprovada e leituras",
      "Python/Playwright/Chromium já existentes e barreira loopback-only preservada",
      "Agentes disponíveis com contexto focal e captura de chamadas",
      "Validadores locais disponíveis, sem instalação ou alteração"
    ]
  },
  "acceptance_criteria": [
    "Pacote nos oito caminhos, formato e referências conferidos",
    "Filosofia autoral v1.0 preservada e subordinada às regras locais",
    "Invocação explícita observada no ambiente disponível",
    "Aplicação consultiva curta rastreável distingue recomendação de autorização",
    "Runtime/CSS/interface/cálculos/dados/build/artefatos byte-idênticos",
    "Relato separa instalação, uso, descoberta automática e main"
  ],
  "approved_tests": [
    "Hash da fonte, links locais sem escape, diferenças e preservação de arquivos protegidos",
    "quick_validate.py oficial se ambiente existente suportar; indisponibilidade preservada, sem instalar",
    "Validação de formato YAML com parser já existente se disponível, identificada separadamente",
    "agent_instruction_structure_test.py para o núcleo legado; escopo limitado não valida CHG X1 por referência",
    "Uso explícito focal em sessão/subagente novo sem resposta esperada no contexto; confronto com tool calls/saídas",
    "FULL existente sobre pacote final congelado; não substitui teste da skill",
    "Auditoria independente focal com matriz de preservação e IMPACT agêntico"
  ],
  "rollback": {
    "source": [
      "Remover somente novos arquivos/links X1 e retirar só blocos próprios dos três documentos, comparando hashes/before externo",
      "Preservar branch e conteúdo de outras tarefas; não resetar nem stashear"
    ],
    "application_state": [
      "Nenhum dado real acessado ou alterado"
    ],
    "data": [
      "Sem migração/reset"
    ],
    "environment": [
      "Encerrar somente processos próprios e preservar evidências; sem alterar configurações globais"
    ],
    "verification": [
      "Diff restante e hashes protegidos iguais ao estado prévio"
    ]
  },
  "approved_by": "Proprietário — A: aprovar instalação delimitada de oito caminhos em codex/x1-design-skill, com uso focal, FULL e auditoria; sem integração/deploy.",
  "approved_at": "2026-09-10T15:08:22.769498+00:00",
  "expires_on": [
    "Drift material da base ou trabalho concorrente",
    "Ampliação dos arquivos/efeitos/permissões",
    "Necessidade de alterar produto, suíte, Harness ou instalar dependência"
  ]
}
```

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-X1-DESIGN-INSTALL-20260910",
  "status": "approved",
  "mode": "SEQUENCIAL",
  "root": "/Users/joaopauloalves/.codex/night-reviews/20260910/product",
  "approved_branch": "codex/x1-design-skill",
  "source_of_truth": {
    "authority": "Pedido ADOTAR_FILOSOFIA e opção A recebida para PROPOSAL.md / pacote 91edda42032a044f7651a3a926ae8b0a9ff9116b36cbecd3061d87fb5f6feb37",
    "source_prompt_sha256": "fcc11d3eab563f3464e84e5b8886ddb9ee4784cff75530702f07776d19e0dff7",
    "product_revision": "f4b629c7e8b1131ba12bedb4f4896542adf46644"
  },
  "create": [
    "docs/work/X1-DESIGN-INSTALL-20260910.md"
  ],
  "modify": [
    "docs/governance/SKILL-ROUTING.md",
    "docs/governance/CONTEXT-MAP.md",
    "docs/work/ACTIVE-TASK.md"
  ],
  "merge": [],
  "preserve": [
    "Todo conteúdo anterior dos mapas/ACTIVE-TASK",
    "Atlas/X2/V4 e suas pendências",
    "Audit inicial X1-01 a X1-04 abertos"
  ],
  "do_not_touch": [
    "AGENTS.md",
    "CLAUDE.md",
    "docs/governance/CURRENT-STATE.md",
    "docs/governance/PROJECT-CONTEXT.md",
    "SESSION_HANDOFF.md",
    "src/",
    "outras skills",
    "grafo/índices"
  ],
  "information_promotion": [
    {
      "from": "Texto X1 v1.0 fornecido",
      "to": "Fonte canônica local e entrada operacional",
      "reason": "Instalação solicitada; não cria autorização geral de edição"
    }
  ],
  "expiration_rules": [
    {
      "artifact": "docs/work/X1-DESIGN-INSTALL-20260910.md",
      "event": "Fim desta tarefa ou drift material; status deve ser conferido sem antecipar aceite/integração"
    }
  ],
  "archive_requires_confirmation": [],
  "privacy_actions": [
    "Somente prompt fornecido, contratos e fixtures sintéticas; sem credenciais/dados reais"
  ],
  "acceptance_criteria": [
    "Conexões focais coerentes, preservação das regras e distinção de instalação/uso/descoberta/main"
  ],
  "approved_by": "Proprietário — A: aprovar instalação delimitada de oito caminhos em codex/x1-design-skill, com uso focal, FULL e auditoria; sem integração/deploy.",
  "approved_at": "2026-09-10T15:08:22.769498+00:00",
  "expires_on": [
    "Drift material da base ou trabalho concorrente",
    "Ampliação dos arquivos/efeitos/permissões",
    "Necessidade de alterar produto, suíte, Harness ou instalar dependência"
  ]
}
```
