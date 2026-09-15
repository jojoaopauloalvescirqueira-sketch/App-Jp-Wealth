# NAV-REF-01 — fechamento de contexto local

Registro delimitado em: 2026-09-10. Escopo: somente o fechamento do NAV-REF-01; não é fotografia global do projeto.

## Contrato, autoridade e compreensão

JP Wealth é software financeiro local/PWA. Esta tarefa ajuda agentes a retomar a versão integrada correta, sem reabrir a navegação nem alterar regras ou dados. As fontes operacionais M1/M3/M4 ainda apresentam fotografias anteriores; cabeçalhos focais apontarão para este registro, mantendo integralmente o passado.

N0-D/A2: atualização factual, sem mudar instruções, autoridade, roteamento, schemas de contrato ou gates. A autorização Git específica permite a branch documental e FF da main ao merge exato se necessário; não concede publicação. Harness mestre aplicado, SHA-256 `c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8`, §§23–25 e 31.1; AGENTS, CHANGE-PROCESS, QUALITY-GATES e skills preflight/change-control/agentic-evolution-governance/post-change-audit. Este contrato registra a decisão humana recebida, sem criar permissões.

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-NAV-REF-01-CONTEXT-CLOSE-20260910",
  "status": "approved",
  "objective": "Registrar somente o fechamento integrado de NAV-REF-01 nas fontes operacionais existentes; delta documental local para revisão.",
  "risk_level": "N0-D",
  "authority_required": "A2",
  "target": {
    "root": "/Users/joaopauloalves/.codex/night-reviews/20260910/product",
    "branch": "codex/nav-ref-context",
    "baseline_sha": "e770e1b66a87e93f52f40eab83479d7a26be2cd4"
  },
  "scope": {
    "allowed_files": [
      "/Users/joaopauloalves/.codex/night-reviews/20260910/product/docs/governance/CURRENT-STATE.md",
      "/Users/joaopauloalves/.codex/night-reviews/20260910/product/docs/work/ACTIVE-TASK.md",
      "/Users/joaopauloalves/.codex/night-reviews/20260910/product/SESSION_HANDOFF.md",
      "/Users/joaopauloalves/.codex/night-reviews/20260910/product/docs/work/NAV-REF-01-CONTEXT-CLOSE.md"
    ],
    "forbidden_actions": [
      "staging",
      "product commit",
      "tag",
      "push",
      "PR",
      "remote merge",
      "deploy",
      "product edits",
      "rebuild",
      "reset",
      "stash",
      "clean",
      "rebase",
      "other worktree synchronization"
    ]
  },
  "approved_tests": [
    "read-only preflight audit/edit",
    "diff and exact allowed-path checks",
    "focal historical suffix/link/identity/freshness checks",
    "product hashes against integrated base",
    "focal documentary review"
  ],
  "rollback": "Somente os três cabeçalhos novos e este arquivo novo, após comparar o delta; originais em tools/.artifacts/nav-ref-context-close-20260910/baseline/. Não executar rollback automático ou Git destrutivo.",
  "approved_by": "Proprietário, pedido JP WEALTH — BASE LOCAL E CONTEXTO APÓS NAV-REF-01 nesta sessão",
  "separate_git_authority": "Criar/usar somente codex/nav-ref-context; FF local da main ao merge exato se necessário. Main já estava no merge; nenhum FF/fetch executado. Sem staging/commit/publicação.",
  "acceptance": "Execução autorizada; resultado documental ainda sujeito a revisão e aceite humano."
}
```

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-NAV-REF-01-CONTEXT-CLOSE-20260910",
  "status": "approved",
  "root": "/Users/joaopauloalves/.codex/night-reviews/20260910/product",
  "mode": "SEQUENCIAL",
  "approved_branch": "codex/nav-ref-context",
  "create": [
    "/Users/joaopauloalves/.codex/night-reviews/20260910/product/docs/work/NAV-REF-01-CONTEXT-CLOSE.md"
  ],
  "modify": [
    "/Users/joaopauloalves/.codex/night-reviews/20260910/product/docs/governance/CURRENT-STATE.md",
    "/Users/joaopauloalves/.codex/night-reviews/20260910/product/docs/work/ACTIVE-TASK.md",
    "/Users/joaopauloalves/.codex/night-reviews/20260910/product/SESSION_HANDOFF.md"
  ],
  "preserve": [
    "Histórico integral das três fontes",
    "Source revision, last_verified e data da fotografia globais",
    "CHG-NAV-LOCAL-PROJECTION-20260910.md, aceites, auditoria, checkpoint e recuperação NAV-REF-01",
    "stash e outras tarefas"
  ],
  "do_not_touch": [
    "AGENTS.md",
    "CLAUDE.md",
    "src/",
    "index.html",
    "build-id.js",
    "dist/",
    "tools/ (exceto novos recibos em evidence_output_only)",
    "skills/",
    ".github/",
    "docs/normative/",
    "docs/governance/CONTEXT-MAP.md"
  ],
  "evidence_output_only": "/Users/joaopauloalves/.codex/night-reviews/20260910/product/tools/.artifacts/nav-ref-context-close-20260910/",
  "source_of_truth": {
    "integração": "PR #11, Git remoto e tools/.artifacts/nav-local-projection-20260910/integration-final.json",
    "fechamento delimitado": "docs/work/NAV-REF-01-CONTEXT-CLOSE.md"
  },
  "information_promotion": [
    {
      "from": "tools/.artifacts/nav-local-projection-20260910/integration-final.json",
      "to": [
        "/Users/joaopauloalves/.codex/night-reviews/20260910/product/docs/governance/CURRENT-STATE.md",
        "/Users/joaopauloalves/.codex/night-reviews/20260910/product/docs/work/ACTIVE-TASK.md",
        "/Users/joaopauloalves/.codex/night-reviews/20260910/product/SESSION_HANDOFF.md"
      ],
      "reason": "Fechamento confirmado, com distinção entre integração remota, base local e delta documental ainda não integrado."
    }
  ],
  "expiration_rules": [
    {
      "artifact": "cabeçalhos delimitados desta tarefa",
      "event": "divergência de revisão, branch, arquivos permitidos ou estado Git"
    }
  ],
  "privacy_actions": [
    "Não copiar dados reais, credenciais ou conteúdo de backups financeiros"
  ],
  "approved_by": "Proprietário, pedido JP WEALTH — BASE LOCAL E CONTEXTO APÓS NAV-REF-01 nesta sessão",
  "acceptance_criteria": [
    "HEAD e produto iguais ao merge autorizado",
    "somente quatro documentos",
    "história/metadados globais preservados",
    "evidências anteriores com origem mantida",
    "nenhum aceite antecipado"
  ]
}
```

## Fatos promovidos e fontes

- NAV-REF-01 integrado pelo [PR #11](https://github.com/jojoaopauloalvescirqueira-sketch/App-Jp-Wealth/pull/11). Finalidade: separar a decisão dos destinos dos efeitos de `navNavigateLocal`, preservando o comportamento examinado.
- Commit candidato: `ca5cb962b85385468ab9703a346960c1819435a5`; merge: `e770e1b66a87e93f52f40eab83479d7a26be2cd4`; build: `f4adcd1cc131c623`.
- Fingerprint do pacote NAV-REF-01, não commit Git: `38f12ee29eb4387b942385ae3309ef1335c4850d8fc76fb79b7288acc9fb8255`.
- [FULL remoto 34549663941](https://github.com/jojoaopauloalvescirqueira-sketch/App-Jp-Wealth/actions/runs/34549663941): **55/55 PASS**, checkout `ca5cb962…`.
- [Standard do PR 34549729240](https://github.com/jojoaopauloalvescirqueira-sketch/App-Jp-Wealth/actions/runs/34549729240): **44/44 PASS**, checkout virtual `8dd0868b968c6388781bc28f3e5fdb16284033e5`, tree idêntica ao candidate.
- [Standard pós-merge 34550738795](https://github.com/jojoaopauloalvescirqueira-sketch/App-Jp-Wealth/actions/runs/34550738795): **44/44 PASS**, checkout `e770e1b…`.

São resultados existentes da integração, reaproveitados por leitura dos recibos/logs; nenhum desses testes foi executado novamente nesta tarefa documental. O `AUDIT_PASS`, aceite e confirmação manual também pertencem ao NAV-REF-01, não ao novo delta documental.

A pasta principal foi identificada no cadastro Git: `/Users/joaopauloalves/Library/Mobile Documents/iCloud~md~obsidian/Documents/1 - ARETÊ/4 - TRABALHO/4G - SOFTWARE/JP Wealth OS`. Já estava limpa na branch `main`, no merge `e770e1b…`, sem operação Git em andamento. Nenhum fetch ou FF foi necessário/executado nesta tarefa; não se atribui ao executor a sincronização anterior.

A worktree `/Users/joaopauloalves/.codex/night-reviews/20260910/product` passou da branch preservada `codex/nav-local-projection` em `ca5cb962…` para a nova `codex/nav-ref-context`, baseada em `e770e1b…`. Produto integrado remoto e pasta principal conferidos; **delta documental apenas local, sem staging, commit ou integração**. Não há novo lote de produto autorizado.

## Preservação, impacto e validação

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. Natureza: reconciliação factual; nenhuma nova revisão material do produto. CURRENT-STATE (M1), ACTIVE-TASK (M3) e HANDOFF (M4) precisam dos cabeçalhos; agentes/preflight e skills que consultam essas fontes herdam o registro por referência, sem editar suas regras. Mapas/roteamento/registries permanecem nas mesmas rotas. Contratos/auditorias anteriores são histórico preservado. Arquitetura e fontes financeiras não recebem mudança; índices/grafo não foram consultados ou atualizados; memória operacional não foi alterada: INDEX BLOCKED pelo escopo, frescor global não demonstrado. Não declarar reconciliação global.

Conferência focal prevista: hashes de produto e build contra o merge; diff limitado aos quatro documentos; histórico anterior como sufixo byte-idêntico; links e identidades; metadados globais e resultado do parser de frescor inalterados; main, branch anterior, checkpoint e stash preservados. Revisão documental posterior ao freeze; aceite humano pendente. Resultados e identidade do novo delta em `tools/.artifacts/nav-ref-context-close-20260910/`.

O fast padrão é NOT_RUN neste alcance: `tools/validate_project.py:192` executa o gerador e regrava derivados, vedado pelo pedido. `tools/preflight_context_test.py` também cria commits em fixtures sintéticas; não será executado como se fosse apenas leitura. Não há modo suportado sem rebuild no validador. Verificações focais e preflight não serão apresentados como fast integral PASS. Nenhum gate é dispensado ou alterado por este registro; a limitação permanece para revisão humana.

Recuperação do NAV-REF-01: [relatório de integração](../../tools/.artifacts/nav-local-projection-20260910/INTEGRATION-REPORT.md), [manifesto](../../tools/.artifacts/nav-local-projection-20260910/candidate.json), [baseline](../../tools/.artifacts/nav-local-projection-20260910/baseline.tar), [pacote](../../tools/.artifacts/nav-local-projection-20260910/candidate-files.tar), [diff](../../tools/.artifacts/nav-local-projection-20260910/candidate.diff) e [prova de recuperação](../../tools/.artifacts/nav-local-projection-20260910/recovery-proof.json). Evidências ignoradas são locais; os links dependem desta instalação. Rollback documental limita-se aos novos cabeçalhos e a este arquivo, comparados à base preservada; não foi executado.

Permanecem AUD-05/P2, falha estrutural V4 CHG/CTX root mismatch (resultado bruto preservado), limitações de PyYAML, Claude, descoberta automática e indexação, motor financeiro legado/FCR/FEO e demais dívidas anteriores. Nada foi convertido em PASS por este fechamento. As datas e a revisão global das fotografias antigas não avançam; somente o recorte NAV-REF-01 foi conferido.
