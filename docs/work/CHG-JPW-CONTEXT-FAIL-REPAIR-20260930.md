# CHG/CTX — reparo da seleção estrutural do contexto atual

N3/A4 de control plane, delimitado ao contexto. A autorização registrada vem do pedido humano vigente “Corrija todos os product fail que foram apresentados ou tem-se registrado”. A correção trata os dois achados brutos já registrados — raiz histórica incompatível e várias revisões tratadas como correntes — sem conceder nova permissão, substituir fonte normativa ou alterar teste/gate. O escopo foi coordenado com o executor principal antes da escrita.

## Compreensão e causa

1. JP Wealth organiza informações e diagnóstico de risco; confiança exige distinguir fatos atuais de evidências antigas.
2. CURRENT-STATE representa a fotografia operacional local; ACTIVE-TASK aponta o trabalho corrente e conserva história. O validador estrutural verifica contrato e âncoras, não carregamento real de um cliente ou autorização humana.
3. Antes do reparo, o modo sem `--contract` selecionava a dupla inline de 2026-09-09, cuja raiz/branch continuam históricas. Quatro linhas antigas “Source revision” impediam identificar uma única base corrente. Agora a dupla vigente está no topo de ACTIVE-TASK; os payloads antigos conservam bytes e usam fences json como exemplos históricos, não contratos yaml vigentes.
4. Consumidores afetados: leitores de contexto e `agent_instruction_structure_test.py`. O novo contrato é selecionado pela opção existente; o teste não será modificado.
5. Preservar os bytes dos payloads JSON históricos, SHAs e relatos; normas, cálculos, regras de autoridade, produto e índices ficam fora do delta.
6. Evidência: execução atual default e explícita da mesma dupla, recibo histórico original preservado, hashes dos payloads antigos, proteção do produto, diff, full e auditoria independentes.

## Fontes e impacto agêntico

| Fonte lida | SHA-256 / trecho pertinente |
|---|---|
| `AGENTS.md` | `d0b77e12abb7dd7336e38c848fdcd8d4dec0142cd4c23289d2d46ef090a4b133` |
| `tools/agent_instruction_structure_test.py` | `a8faa2d62a1fbb9fc3bba05ef0c0882e847d8383931d52d2dbba38bdbb249d4a` |
| `skills/agentic-evolution-governance/SKILL.md` | `b484b6a9a5ec2495ef7c37efbb2b92b74e73b9a52bae0964e06a773d8d915335` |
| `docs/governance/CURRENT-STATE.md` | `4edd09e071b504096a45f11ba6684d08027420bde5cf97fc2828bca4b17e26f9` |
| `docs/work/ACTIVE-TASK.md` | `849b58ac3372d0ba5d59bb1398216d61c0ca086f69910ef7dc46eb65b97493f3` |
| Harness externo `/Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/2 - TRABALHO/99A -   SOFTWARE DEV/99 - PROMPTS SOFTWARE DEV/A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md` | `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`; §§10–16, 24–25, 28–30 |

O caminho do Harness hoje existente foi confirmado por conteúdo e hash; a localização antiga registrada em AGENTS está indisponível. Este delta não corrige o link de AGENTS nem altera o Harness.

| Categoria / elemento | Impacto | Ação local | Evidência / estado |
|---|---|---|---|
| Contexto operacional CURRENT-STATE / ACTIVE-TASK | AFFECTED | REQUIRED | Revisões antigas e tarefa local atual devem ter papéis distintos; reconciliação local delimitada |
| Contrato estrutural atual | AFFECTED | REQUIRED | Dupla CHG/CTX específica desta raiz/branch, sem substituir a inline passada |
| Leitores de contexto e validador | AFFECTED | NOT_REQUIRED | Herança por leitura/opção `--contract` já implementada |
| AGENTS / CLAUDE / router / skills | NOT_AFFECTED pelas regras | NOT_REQUIRED | Nenhuma autoridade, roteamento ou comportamento de carregamento muda |
| Fontes financeiras, produto e persistências | NOT_AFFECTED | NOT_REQUIRED | Fora da allowlist, comparação independente de hashes |
| Handoffs e fotografias históricas | NOT_AFFECTED | NOT_REQUIRED | Continuam históricos; não se promove aprovação antiga |
| Memória, índice e vetor | NOT_AFFECTED | NOT_REQUIRED | Nenhum mecanismo de reindexação é aplicado; INDEX NOT REQUIRED |

As duas cópias da dupla vigente em ACTIVE-TASK e neste contrato devem permanecer idênticas; a equivalência é conferida na evidência desta rodada. A reconciliação representa impacto agêntico local, sem nova revisão material do produto. Estado de validação permanece pendente até recibos específicos; “SYSTEM RECONCILED” não é uma aprovação global do projeto.

## Seleção e limites dos resultados

Atual: `python3 tools/agent_instruction_structure_test.py --root /private/tmp/jpw-cockpit-ui-20260930 --contract docs/work/CHG-JPW-CONTEXT-FAIL-REPAIR-20260930.md`.

Default atual: `python3 tools/agent_instruction_structure_test.py --root /private/tmp/jpw-cockpit-ui-20260930` seleciona a mesma dupla vigente do topo de ACTIVE-TASK. Os dois payloads JSON inline de 2026-09-09 continuam históricos sob fences json; sua raiz/branch não foi reescrita. O recibo anterior que tentou usar essa dupla histórica na nova worktree conserva PRODUCT_FAIL. A mudança seleciona um contrato corrente legítimo, não corrige retroativamente o contrato passado. O teste registra os controles sintéticos, mas sua aprovação estrutural não demonstra carregamento, compreensão, execução MT5 ou aceite humano.

## CHG atual

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-JPW-CONTEXT-FAIL-REPAIR-20260930",
  "status": "approved",
  "approved_by": "proprietário — pedido conversacional vigente “Corrija todos os product fail que foram apresentados ou tem-se registrado”; correção delimitada dos achados estruturais registrados, sem ampliação de autoridade",
  "approved_at": "2026-09-30T18:11:08.909970+00:00",
  "expires_on": [
    "raiz ou branch mudar",
    "baseline divergir materialmente",
    "necessidade de editar fora da allowlist",
    "norma, autoridade, schema, gate ou oráculo exigir mudança",
    "trabalho concorrente incompatível"
  ],
  "objective": "Corrigir seleção do contexto estrutural atual e diferenciar revisões históricas, preservando os payloads JSON históricos e os resultados brutos originais.",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/private/tmp/jpw-cockpit-ui-20260930",
    "branch": "codex/jpw-cockpit-ui-20260930",
    "baseline_sha": "deffc5061fe2eff3d83b6f6e742fa105ac9c5b06"
  },
  "scope": {
    "allowed_files": [
      "docs/work/CHG-JPW-CONTEXT-FAIL-REPAIR-20260930.md",
      "docs/governance/CURRENT-STATE.md",
      "docs/work/ACTIVE-TASK.md"
    ],
    "forbidden_files": [
      "qualquer arquivo fora de allowed_files",
      "AGENTS.md, CLAUDE.md, skills, Harness externo, normas e decisões",
      "produto, testes, gates, CI, dados e esquemas financeiros"
    ],
    "allowed_actions": [
      "criar um CHG/CTX atual explícito e restrito",
      "acrescentar fatos locais verificados e limites em CURRENT-STATE",
      "distinguir rótulos de revisões históricas sem alterar seus SHAs ou relatos",
      "referenciar o contrato atual em ACTIVE-TASK preservando seus payloads históricos",
      "executar teste estrutural existente com seleção explícita e gate full coordenado"
    ],
    "forbidden_actions": [
      "commit, push, merge, rebase, reset, stash ou publicação",
      "alterar schemas, validadores, expectativas, aprovações históricas ou política de autoridade",
      "promover resultados históricos ou NOT_RUN a PASS",
      "aplicar contrato histórico de outra raiz à worktree atual",
      "reindexar memória, índice ou vetor"
    ],
    "regressions_forbidden": [
      "produto e fórmulas mudarem neste delta",
      "payloads JSON dos contratos inline históricos perderem bytes",
      "histórico correto passar a fato atual",
      "nova política ou autorização surgir deste documento"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "relatórios, logs e hashes locais em outputs/jpw-product-fail-repair-20260930",
      "fixtures sintéticas e tools/.artifacts produzidos pelos testes existentes"
    ],
    "generation_commands": [
      "python3 tools/agent_instruction_structure_test.py --root /private/tmp/jpw-cockpit-ui-20260930 --contract docs/work/CHG-JPW-CONTEXT-FAIL-REPAIR-20260930.md",
      "python3 tools/agent_instruction_structure_test.py --root /private/tmp/jpw-cockpit-ui-20260930",
      "python3 tools/quality_gate.py --tier full --artifact <evidence>/full.json"
    ],
    "manual_edit": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "loopback dos testes existentes"
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
      "Python/Node/Chromium/Playwright já instalados",
      "Git somente leitura no produto",
      "git init e commits sintéticos nas fixtures descartáveis do teste estrutural existente"
    ]
  },
  "acceptance_criteria": [
    "teste atual explícito valida raiz, branch, base, CHG/CTX e exatamente uma revisão corrente",
    "quatro revisões históricas conservam SHAs e fatos, com rótulos históricos distintos",
    "os dois payloads JSON históricos permanecem byte a byte intactos; somente o rótulo da fence muda para json, distinguindo exemplo histórico de contrato vigente",
    "modo default e explícito atuais passam com a mesma dupla; recibo original histórico permanece falho sem correção retroativa",
    "produto e dados preservados; full e auditoria independentes separados"
  ],
  "approved_tests": [
    "teste estrutural existente: controles sintéticos, modo default atual e seleção explícita atual; recibo original histórico preservado",
    "comparação de hashes do produto e payloads JSON históricos contra baseline; equivalência da dupla atual nos dois modos",
    "git diff --check",
    "gate full existente no candidate final e auditoria independente de control plane"
  ],
  "rollback": {
    "source": [
      "restaurar somente os três caminhos deste delta a partir de BASELINE.json/baseline.tar.gz e cópias antes/depois; preservar ACTIVE-TASK preexistente/coordenação atual"
    ],
    "application_state": [
      "não ler ou alterar estado real"
    ],
    "data": [
      "não migrar, apagar ou inicializar dados"
    ],
    "environment": [
      "encerrar somente processos sintéticos próprios; preservar logs de auditoria"
    ],
    "verification": [
      "comparar hashes dos arquivos e dos payloads JSON históricos; confirmar HEAD/branch inalterados"
    ]
  }
}
```

## CTX atual

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-JPW-CONTEXT-FAIL-REPAIR-20260930",
  "status": "approved",
  "approved_by": "proprietário — pedido conversacional vigente “Corrija todos os product fail que foram apresentados ou tem-se registrado”; correção delimitada dos achados estruturais registrados, sem ampliação de autoridade",
  "approved_at": "2026-09-30T18:11:08.909970+00:00",
  "expires_on": [
    "raiz ou branch mudar",
    "baseline divergir materialmente",
    "necessidade de editar fora da allowlist",
    "norma, autoridade, schema, gate ou oráculo exigir mudança",
    "trabalho concorrente incompatível"
  ],
  "root": "/private/tmp/jpw-cockpit-ui-20260930",
  "mode": "CONCORRENTE",
  "approved_branch": "codex/jpw-cockpit-ui-20260930",
  "create": [
    "docs/work/CHG-JPW-CONTEXT-FAIL-REPAIR-20260930.md"
  ],
  "modify": [
    "docs/governance/CURRENT-STATE.md",
    "docs/work/ACTIVE-TASK.md"
  ],
  "merge": [],
  "preserve": [
    "contrato inline histórico CHG/CTX de 2026-09-09 e recibos brutos",
    "todas as narrativas e SHAs históricos",
    "delta preexistente NoCuda/Cockpit e trabalho coordenado da fixture HTTP"
  ],
  "do_not_touch": [
    "AGENTS.md",
    "CLAUDE.md",
    "skills/",
    "docs/normative/",
    "docs/decisions/",
    "src/",
    "mt5/",
    "downloads/",
    "tools/",
    ".github/"
  ],
  "archive_requires_confirmation": [],
  "source_of_truth": {
    "autorizacao": "pedido vigente do proprietário para corrigir os PRODUCT_FAIL registrados; este contrato registra o alcance, não o amplia",
    "engenharia": "AGENTS.md; Harness canônico externo hash b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95 §§10-16,24-25,28-30",
    "base_local": "Git HEAD deffc5061fe2eff3d83b6f6e742fa105ac9c5b06 + BASELINE.json e delta coordenado, não um commit dos fontes",
    "falhas": "HISTORICAL-INVENTORY.json e outputs/jpw-cockpit-v180-20260929/agent-structure.log"
  },
  "information_promotion": [
    {
      "from": "raiz/branch/HEAD e baseline local verificados na rodada atual",
      "to": "docs/governance/CURRENT-STATE.md",
      "reason": "distinguir contexto operacional atual de fotografias históricas, sem homologar produto ou runtime"
    },
    {
      "from": "docs/work/CHG-JPW-CONTEXT-FAIL-REPAIR-20260930.md",
      "to": "docs/work/ACTIVE-TASK.md",
      "reason": "seleção explícita suportada pelo validador atual; o contrato histórico mantém sua própria raiz/branch"
    }
  ],
  "expiration_rules": [
    {
      "artifact": "docs/governance/CURRENT-STATE.md",
      "event": "mudança material no Git/candidate ou no escopo/ambiente invalida esta fotografia local"
    },
    {
      "artifact": "docs/work/CHG-JPW-CONTEXT-FAIL-REPAIR-20260930.md",
      "event": "raiz, branch, allowlist, baseline ou autoridade divergir"
    }
  ],
  "privacy_actions": [
    "somente identidades de desenvolvimento e dados sintéticos",
    "sem credenciais, contas reais, registros financeiros ou memória/vetor"
  ],
  "acceptance_criteria": [
    "teste atual explícito valida raiz, branch, base, CHG/CTX e exatamente uma revisão corrente",
    "quatro revisões históricas conservam SHAs e fatos, com rótulos históricos distintos",
    "os dois payloads JSON históricos permanecem byte a byte intactos; somente o rótulo da fence muda para json, distinguindo exemplo histórico de contrato vigente",
    "modo default e explícito atuais passam com a mesma dupla; recibo original histórico permanece falho sem correção retroativa",
    "produto e dados preservados; full e auditoria independentes separados"
  ]
}
```
