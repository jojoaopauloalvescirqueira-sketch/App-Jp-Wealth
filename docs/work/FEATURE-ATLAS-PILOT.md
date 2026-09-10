> Registro histórico do piloto isolado, preservado. Transferência à árvore real agora autorizada pelo [registro de integração com pendências](ATLAS-V4-INTEGRATION-20260910.md). Os resultados e limites históricos abaixo não são alterados retroativamente.

# JP Feature Atlas — piloto isolado

**N3 / A4 delimitada. Implementação autorizada; aceite ainda não concedido.**

A V4 é base experimental não aceita; AUD-05/P2 permanece aberto. O snapshot reproduz HEAD 484228189cc3f5f4c297f29f88f2b2ed541a3afd mais os 15 arquivos V4 do fingerprint 5ca9e046a4c75a5bfe3da9b5d1f11b259d88cdd33ee4a56372601c99e2035642. As 11 omissões da árvore são documentadas em evidence/snapshot.json, fora do candidate. Git contém somente sete snapshots existentes exigidos pelos testes, sem origin ou compartilhamento. A branch é uma identidade reproduzida da fixture, não nova branch do projeto.

## Compreensão específica

JP Wealth prioriza integridade e rastreabilidade no software financeiro. Este delta melhora a descrição e consulta, sem homologar o motor legado. Calendário é informação compartilhada em Forex/Research/Dashboard; Alladin registra fatos append-only e deriva caixa/quantidade; NoCoda mantém estudos manuais vinculados ao catálogo também consumido por ordens, Motor e Pivots. Hoje mapas e código exigem investigação dispersa; depois, três fichas acrescentarão finalidade, caminhos de falha e relações com retorno obrigatório às fontes. Dados, fórmulas, preferências e gates do aplicativo ficam idênticos. A prova compara A/B e fatos do navegador com oráculos independentes; presença de arquivo ou full do produto não demonstra entendimento.

## Proveniência externa do Harness

Fonte reencontrada como `A0 - HARNESS - JP Wealth MASTER SPECIFICATION.md`, no acervo de desenvolvimento. SHA256 integral c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8; primeiros 52054 bytes = Core d894384c88f414ace7b593c9dd88d299b882c5d78c7b3e144859d210aef2a770. O link antigo de AGENTS continua histórico e não foi corrigido. O apêndice propositivo não é nova autoridade.

## CHG

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-FEATURE-ATLAS-PILOT-20260909",
  "status": "approved",
  "objective": "Prepare and evaluate the bounded JP Feature Atlas pilot exclusively in an isolated copy; no installation or integration into original.",
  "risk_level": "N3",
  "authority_required": "A4",
  "target": {
    "root": "/private/tmp/jpw-feature-atlas-_jdnswjt/candidate",
    "branch": "codex/agent-context-coherence",
    "baseline_sha": "484228189cc3f5f4c297f29f88f2b2ed541a3afd"
  },
  "scope": {
    "allowed_files": [
      "docs/architecture/FEATURE-ATLAS.md",
      "skills/jpw-feature-atlas/SKILL.md",
      ".agents/skills/jpw-feature-atlas",
      ".claude/skills/jpw-feature-atlas",
      "docs/work/FEATURE-ATLAS-PILOT.md",
      "tools/feature_atlas_test.py",
      "docs/governance/SKILL-ROUTING.md",
      "docs/governance/CONTEXT-MAP.md",
      "docs/work/ACTIVE-TASK.md"
    ],
    "forbidden_files": [
      "All original tree and V4 evidence",
      "Any candidate product source, financial norms, existing tests, CI, Harness master and frozen imported skills"
    ],
    "allowed_actions": [
      "Reproduce selected HEAD source files plus all 15 V4 modifications; private existing Git objects only",
      "Write the allowlist inside isolated candidate; relative native skill links resolve inside each copy",
      "Create synthetic control/measurement fixtures and evidence under /private/tmp/jpw-feature-atlas-_jdnswjt",
      "Run controlled-browser behavior, fresh read-only existing Codex sessions, focused test, existing full subject to pending fixture-commit clarification, independent audit"
    ],
    "forbidden_actions": [
      "commit in original or Atlas candidate",
      "push",
      "PR",
      "merge",
      "deploy",
      "install or transfer into original",
      "global settings or permission changes",
      "Graphify write/query/reindex",
      "embeddings",
      "new dependencies/services",
      "read real operational data or secrets"
    ],
    "regressions_forbidden": [
      "V4 acceptance or closure of AUD-05/P2 by this pilot",
      "Product or runtime modifications",
      "Authority amplification from candidate instructions",
      "Discard previous failures or relabel incomplete evidence as PASS"
    ]
  },
  "derived_artifacts": {
    "allowed": [
      "/private/tmp/jpw-feature-atlas-_jdnswjt/evidence",
      "/private/tmp/jpw-feature-atlas-_jdnswjt/control",
      "/private/tmp/jpw-feature-atlas-_jdnswjt/runtime",
      "Isolated comparison and browser fixtures under /private/tmp/jpw-feature-atlas-_jdnswjt",
      "Existing generator outputs in isolated copies, byte-equal after gates"
    ],
    "generation_commands": [
      "Existing tools/quality_gate.py --tier full --artifact <pilot>/evidence/quality-full.json",
      "Existing rebuild called only by unchanged gate",
      "tools/feature_atlas_test.py on candidate and synthetic negative fixtures",
      "control runners for sandbox, comparison and provenance"
    ],
    "manual_edit": "forbidden"
  },
  "external_side_effects": {
    "network": "allowed",
    "allowed_targets": [
      "Loopback for browser product tests; external network denied by tested process profile",
      "Existing authenticated Codex service for authorized read-only evaluation sessions; no economic APIs"
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
      "Existing Python/Node/Playwright/Chromium, Git reading/importing existing objects, local sandbox-exec",
      "Existing Codex client in ephemeral read-only sessions",
      "Claude only if already available; otherwise NOT_RUN"
    ]
  },
  "acceptance_criteria": [
    "Three feature records explain A–H with original references, typed relations and separate availability/evidence/freshness.",
    "Partial inventory and absent capabilities remain explicit.",
    "Native discovery and actual use demonstrated in available fresh sessions, not file presence alone.",
    "Reference questions fixed before records; A/B same V4 experimental base, separate sessions and retained heldout.",
    "Claims of execution matched to captured commands/results; missing evidence or false claim does not PASS.",
    "Focused validation, existing full and independent audit tied to frozen candidate; original unchanged."
  ],
  "approved_tests": [
    "Independent reference questions Q1–Q9 before feature authoring, heldout Q3/Q4/Q9",
    "Focused record/link/hash/typed-relation validation including synthetic counterexamples",
    "Controlled browser: calendar, Alladin create/reverse/write refusal, NoCoda/shared catalog",
    "A/B experimental read-only sessions, same model/budget/base, separate sessions",
    "Existing full without modifications, with synthetic-commit interpretation pending owner response",
    "Independent focal audit of candidate and evidence"
  ],
  "rollback": {
    "source": [
      "No rollback in original: it is never modified. Remove only explicitly created Atlas delta from isolated copy if requested."
    ],
    "application_state": [
      "Synthetic browser contexts only; never open operator profile."
    ],
    "data": [
      "No real data, migrations, resets or backups."
    ],
    "environment": [
      "Terminate only own processes. Preserve original and failed evidence. Retained temporary pilot may be deleted only with authorized cleanup."
    ],
    "verification": [
      "Compare original tracked/V4 hashes, evidence hashes, branch/HEAD/main/stash/worktrees and graph; compare product candidate to base."
    ]
  },
  "approved_by": "Owner: explicit latest authorization exclusively for isolated JP Feature Atlas pilot; not prior coherence Option A",
  "approved_at": "2026-09-09T21:40:50.852975-03:00",
  "expires_on": [
    "Original or V4 snapshot drift",
    "Need to expand files, permissions or effects",
    "Failure of isolation",
    "Access to real data or credentials",
    "Material change after freeze"
  ]
}
```

## CTX

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-FEATURE-ATLAS-PILOT-20260909",
  "status": "approved",
  "root": "/private/tmp/jpw-feature-atlas-_jdnswjt/candidate",
  "mode": "SEQUENCIAL",
  "approved_branch": "codex/agent-context-coherence",
  "create": [
    "docs/architecture/FEATURE-ATLAS.md",
    "skills/jpw-feature-atlas/SKILL.md",
    ".agents/skills/jpw-feature-atlas",
    ".claude/skills/jpw-feature-atlas",
    "docs/work/FEATURE-ATLAS-PILOT.md",
    "tools/feature_atlas_test.py"
  ],
  "modify": [
    "docs/governance/SKILL-ROUTING.md",
    "docs/governance/CONTEXT-MAP.md",
    "docs/work/ACTIVE-TASK.md"
  ],
  "merge": [],
  "preserve": [
    "Entire original and stash",
    "Experimental V4 before Atlas in base-v4",
    "AUD-05/P2 and all existing evidence",
    "All product bytes and existing gates"
  ],
  "do_not_touch": [
    "Original project",
    "Master Harness",
    "Graphify",
    "Global config",
    "Financial norms and data"
  ],
  "archive_requires_confirmation": [],
  "source_of_truth": {
    "authority": "Latest owner message; this contract records but does not grant more authority",
    "engineering": "Original Master Core SHA256 d894384c88f414ace7b593c9dd88d299b882c5d78c7b3e144859d210aef2a770; local N3/A4 retained",
    "product": "484228189cc3f5f4c297f29f88f2b2ed541a3afd",
    "experimental_instructions": "5ca9e046a4c75a5bfe3da9b5d1f11b259d88cdd33ee4a56372601c99e2035642 (not accepted; AUD-05/P2 open)",
    "atlas": "docs/architecture/FEATURE-ATLAS.md; descriptive, not normative",
    "procedure": "skills/jpw-feature-atlas/SKILL.md; native links share this exact file"
  },
  "information_promotion": [
    {
      "from": "Original inspected source plus independently recorded synthetic runs",
      "to": "FEATURE-ATLAS records and evidence register",
      "reason": "Describe only examined behaviors; no inference of implementation from plans or tests of another candidate"
    }
  ],
  "expiration_rules": [
    {
      "artifact": "Each feature source hash",
      "event": "Changed source/hash or material consumer change requires direct verification; no automatic rewriting."
    }
  ],
  "privacy_actions": [
    "Source allowlist; no original Git config, operator profile, secrets, backups or prior Graphify corpus",
    "Question, source and command provenance retained only in isolated evidence",
    "No model prompts include reference answers or sibling session results"
  ],
  "acceptance_criteria": [
    "Three feature records explain A–H with original references, typed relations and separate availability/evidence/freshness.",
    "Partial inventory and absent capabilities remain explicit.",
    "Native discovery and actual use demonstrated in available fresh sessions, not file presence alone.",
    "Reference questions fixed before records; A/B same V4 experimental base, separate sessions and retained heldout.",
    "Claims of execution matched to captured commands/results; missing evidence or false claim does not PASS.",
    "Focused validation, existing full and independent audit tied to frozen candidate; original unchanged."
  ],
  "approved_by": "Owner: explicit latest authorization exclusively for isolated JP Feature Atlas pilot; not prior coherence Option A",
  "approved_at": "2026-09-09T21:40:50.852975-03:00",
  "expires_on": [
    "Original or V4 snapshot drift",
    "Need to expand files, permissions or effects",
    "Failure of isolation",
    "Access to real data or credentials",
    "Material change after freeze"
  ]
}
```

## Comparação antes/depois

| Área | Antes | Delta | Preservação |
|---|---|---|---|
| AGENTS / CLAUDE / Harness | V4 experimental | Nenhum | Regras e autoridade byte-idênticas |
| Roteamento/contexto | Fontes por domínio | Referência focal ao Atlas | Restrições existentes permanecem; fonte original prevalece |
| Atlas | Ausente | Inventário parcial e três fichas | Não substitui norma, estado geral ou contratos |
| Skill | Ausente | Procedimento central e dois links locais | Sem agente autônomo, instalação global ou novos poderes |
| Tarefa | Contrato de coerência | Tarefa sintética deste piloto | Original e cópia base V4 preservados |
| Produto, CI e grafo | Snapshot examinado | Nenhum | Hashes conferidos |

## Plano de avaliação previamente fixado

Q1–Q9 definidos por revisor que não escreverá as fichas; Q3/Q4/Q9 reservados. Três lotes (dois desenvolvimento, um heldout), em duas condições A/B independentes, uma execução por lote/condição; mesma versão de modelo, esforço, permissões, tempo máximo de 420s e limite solicitado de 10 comandos de leitura por lote. Não repetir para procurar PASS. Registrar orçamento real observado, custo/latência e limites do controle de tokens. A/B usam exatamente os mesmos arquivos V4/produto e tarefa sintética de consulta; B acrescenta somente pacote Atlas. Nem gabarito nem saída de outra sessão entram nos prompts.

Critérios: todas as afirmações críticas de domínio/autoridade e de execução devem ter suporte; uma afirmação sem suporte não passa. Descoberta nativa deve ser observada no ambiente e seu uso acompanhado por acesso às fontes e resposta correta. Melhora exige ganho observado em correção/recuperação ou redução de consultas/tempo/consumo sem perda de fidelidade; uma execução por condição não estabelece causalidade geral. Conferir retenção de falhas, origem herdada versus executada e registros incompletos.

## Limites e manutenção

Índice antigo não é usado nem atualizado. Claude indisponível = NOT_RUN. Escrita sintética é somente em fixtures de navegador; testes existentes podem reconstruir derivados e criar outras cópias temporárias dentro do piloto. FULL aguarda esclarecimento apenas sobre seus commits sintéticos internos. Autorizar piloto não autoriza corrigir defeitos ou fechar P2. Evidências e resultado final ficam fora do candidate após freeze.
