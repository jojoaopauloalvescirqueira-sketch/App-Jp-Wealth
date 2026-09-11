# NAV-REF-01 — projeção da navegação local

## Brief e responsabilidade

JP Wealth reúne cinco áreas financeiras com identidade semântica e telas locais distintas. Este lote facilita revisar a escolha dos destinos sem tocar no motor financeiro legado. `src/js/40-app/01-navigation.js` coordena estado efêmero: entrada → validação → projeção → aplicação → sincronização. Hoje `navNavigateLocal` mistura dez ternários de identidade com efeitos. A projeção será uma função interna simples no mesmo arquivo, recebendo o descriptor validado; guardas e efeitos permanecem no fluxo original. Não criar registry, router, cache ou API pública para testes.

Consumidores: subdestinos de `src/js/40-app/11-operational-shell.js:149`, atalhos de `src/js/20-ui/25-dash-macro.js:368`, compatibilidade de `src/js/20-ui/13-exec-views.js:62`; leitura pelo submenu e cabeçalho. Foco e interiores permanecem sob seus consumidores. Os wrappers de `navigateToScreen` não mudam.

Fontes examinadas: AGENTS.md; skills preflight/change-control/test-triage/browser-verification/post-change-audit; NAVIGATION-HIERARCHY, CODE-MAP, ARCHITECTURE e CONTEXT-MAP confrontados com a base. Harness mestre SHA-256 `c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8`, §§12–16, 24, 36–48; prompt de Refatoração Orientada à Qualidade e Checkpoint Técnico fornecido pelo proprietário. Diagnóstico reaproveitado sem nova revisão geral.

HEAD inicial `1f9be1e88fb6315b87b293fc0addb32a11c3bf8e` e base `b3054e1da1a4a2f2a5ddefd8d715432d7719e636` compartilham tree `ed92b564edd33688ea8dd96c2c2ef0969ef434ba`, mas são commits distintos. Checkout inicial limpo; build anterior `60463a994a0068f8`. A branch autorizada foi criada a partir de b3054e1. Nenhum fetch necessário.

## CHG — contrato delimitado

- Schema: `jp-harness/chg/v1`.
- Identidade: `CHG-NAV-LOCAL-PROJECTION-20260910`.
- Estado: approved para implementação delimitada; não é aceite do candidate.
- Risco: N1; autoridade A2. A4 específico apenas para criar/usar a branch indicada.
- Aprovação: mensagem humana “JP WEALTH — AUTORIZAÇÃO DO NAV-REF-01 / Escolho A”, nesta sessão em 2026-09-10. Este documento não cria autoridade adicional.
- Raiz: `/Users/joaopauloalves/.codex/night-reviews/20260910/product`.
- Branch: `codex/nav-local-projection`.
- Baseline: `b3054e1da1a4a2f2a5ddefd8d715432d7719e636`.

Únicos sete caminhos editáveis:

1. `/Users/joaopauloalves/.codex/night-reviews/20260910/product/src/js/40-app/01-navigation.js`
2. `/Users/joaopauloalves/.codex/night-reviews/20260910/product/src/js/manifest.json` — somente hash da fonte de navegação.
3. `/Users/joaopauloalves/.codex/night-reviews/20260910/product/tools/navigation_local_contract_test.py`
4. `/Users/joaopauloalves/.codex/night-reviews/20260910/product/build-id.js`
5. `/Users/joaopauloalves/.codex/night-reviews/20260910/product/dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html`
6. `/Users/joaopauloalves/.codex/night-reviews/20260910/product/docs/work/ACTIVE-TASK.md` — somente novo cabeçalho, histórico integral preservado.
7. `/Users/joaopauloalves/.codex/night-reviews/20260910/product/docs/work/CHG-NAV-LOCAL-PROJECTION-20260910.md`

Derivados 4/5 exclusivamente por `python tools/rebuild_monolith.py`; proibida edição manual, alteração da lógica de build ou ordem do manifest. O build pode mudar legitimamente.

### Invariantes e critérios

- Mesmos 20 pares locais e plano integral; retornos, recusas, repetição, estado e ordem/contagem dos efeitos.
- Histórico local `exec:history`: canonical `forex-reconciliation`, screen `exec`. Apuração canônica continua screen `contab`.
- PF `mensal/dividas/comparativo/cenarios`: canonical e child nulos, source `compatibility`; overview: canonical `personal-finance`, child nulo, source `local`.
- Guardas antes da projeção; resolução dinâmica da superfície nas posições existentes. `navApply(plan,surfaceId)` e `syncActiveScreen` não mudam de posição ou argumentos. Recusa tardia ainda sincroniza a tela.
- Zero novas leituras financeiras, gravações, consultas de rede ou mudanças em dados, rascunhos, preferências e fluxo de foco.
- Ganho estrutural: decisão explícita separada dos efeitos, sem fonte de verdade concorrente. Não basta deslocar os ternários.
- Produto financeiro, persistência, layout, calendário e defeitos anteriores fora do lote.

### Testes e efeitos autorizados

1. Fixar o novo teste de contrato e suas expectativas antes de transformar a fonte. Executar a mesma versão do teste pela API existente na baseline e no candidate: 20 pares, guardas, recusas tardias, repetições, ordem/contagem, disponibilidade dinâmica e contraprova sintética.
2. Consumidores reais: navegação IA, Exec, PF, Research e atalhos Dashboard no standard; focais existentes `contextual_sidebar_test.py`, `navigation_layout_choice_test.py`, `dashboard_forex_relocation_test.py`. Avaliar foco e modos lateral/superior nos cenários existentes.
3. `tools/quality_gate.py --tier standard`, `tools/build_reproducibility_test.py`, `tools/service_worker_upgrade_test.py` e auditoria independente focal. Sem alteração de gates/expectativas, nem repetição sem hipótese.

Evidências duráveis: `/Users/joaopauloalves/.codex/night-reviews/20260910/product/tools/.artifacts/nav-local-projection-20260910/`. Temporários/perfis fora do produto, em `/private/tmp/jpw-nav-local-projection-*`. Usar Python/Playwright existentes e dados sintéticos. Rede dos testes limitada pelo perfil existente `/Users/joaopauloalves/.codex/night-reviews/20260910/evidence/loopback-only.sb`, SHA-256 `cf35cca89f2e1b677995e788c0fe365bf627c641f260a3e4ea80cbde31a0c60e`, sem APIs econômicas ao vivo. Não modificar o perfil, instalar dependências ou criar infraestrutura genérica.

Git interno de testes: somente fixtures descartáveis próprias dos testes existentes, com metadados próprios, sem remotos, hooks ativos ou ligação ao Git do produto. Nenhum commit no produto ou configuração global alterada.

### Preservação, rollback e parada

Baseline recuperável em `baseline.tar` no diretório de evidências, contendo arquivos rastreados, sem `.git`, dados reais ou caches; inventário de hashes em `before.json`. Stash e demais worktrees permanecem intactos.

Recuperação limitada ao próprio delta: comparar hashes, conferir o diff reverso com `git apply --reverse --check` antes de propor aplicação. Fontes e dois arquivos novos pertencem exclusivamente ao lote; derivados devem ser gerados oficialmente na recuperação autorizada. Não executar reset, stash, restauração ampla, exclusão de branch/worktree ou limpeza geral. Candidate e baseline devem ser preservados em bytes, além dos hashes.

Parar a parte afetada se houver drift material, trabalho desconhecido, mudança de comportamento necessária, proteção reduzida, arquivo/efeito/risco/permissão fora do lote. Sem commit, tag, push, PR, merge ou deploy. Aceite humano permanece posterior.

## CTX — contexto delimitado

- Schema: `jp-harness/ctx/v1`.
- Identidade: `CTX-NAV-LOCAL-PROJECTION-20260910`; modo SEQUENCIAL; estado approved pela mesma escolha A.
- Raiz e branch: as declaradas no CHG acima.
- Criar somente o caminho 7; modificar somente o cabeçalho do caminho 6. Os caminhos completos estão na allowlist.
- Promover somente a descrição desta tarefa local e ponte para seu checkpoint. Não antecipar PASS, aceite ou integração.
- Preservar todo o histórico de ACTIVE-TASK, Atlas, mapas, roteamento, skills, agentes, políticas e fontes gerais.

A análise de impacto abrange as representações lidas pelos agentes. Há impacto M3 limitado à tarefa e ao contrato. CODE-MAP, ARCHITECTURE, NAVIGATION-HIERARCHY e CONTEXT-MAP continuam descrevendo API/responsabilidades preservadas; nenhum símbolo público é removido. Atlas não indexa esta fonte. Divergências anteriores em hashes de outros módulos, AUD-05/P2, root mismatch V4 e indexação não são corrigidas nem homologadas neste lote.

## Checkpoint

Sequência: caracterização → transformação → focais → freeze → standard/reprodutibilidade/PWA → auditoria focal. Mudança material depois do freeze exige nova identidade e repetição apenas das validações afetadas. Recibos posteriores ficam fora dos sete inputs congelados.

Resultados, matriz de melhoria, diff, manifesto e auditoria estarão em `tools/.artifacts/nav-local-projection-20260910/REPORT.md`. Este contrato registra autorização e critérios, não resultados antecipados. Checkpoint técnico não é backup financeiro, aceite humano ou integração.

## Machine-readable contracts (YAML 1.2 / JSON)

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-NAV-LOCAL-PROJECTION-20260910",
  "status": "approved",
  "objective": "Separate local destination projection from navigation effects; preserve observed behavior.",
  "risk_level": "N1",
  "authority_required": "A2",
  "target": {
    "root": "/Users/joaopauloalves/.codex/night-reviews/20260910/product",
    "branch": "codex/nav-local-projection",
    "baseline_sha": "b3054e1da1a4a2f2a5ddefd8d715432d7719e636"
  },
  "scope": {
    "allowed_files": [
      "/Users/joaopauloalves/.codex/night-reviews/20260910/product/src/js/40-app/01-navigation.js",
      "/Users/joaopauloalves/.codex/night-reviews/20260910/product/src/js/manifest.json",
      "/Users/joaopauloalves/.codex/night-reviews/20260910/product/tools/navigation_local_contract_test.py",
      "/Users/joaopauloalves/.codex/night-reviews/20260910/product/build-id.js",
      "/Users/joaopauloalves/.codex/night-reviews/20260910/product/dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
      "/Users/joaopauloalves/.codex/night-reviews/20260910/product/docs/work/ACTIVE-TASK.md",
      "/Users/joaopauloalves/.codex/night-reviews/20260910/product/docs/work/CHG-NAV-LOCAL-PROJECTION-20260910.md"
    ],
    "forbidden_actions": [
      "product commit",
      "tag",
      "push",
      "PR",
      "merge",
      "deploy",
      "reset",
      "stash",
      "other worktrees",
      "financial rules",
      "persistence",
      "layout",
      "other files"
    ]
  },
  "acceptance_criteria": [
    "20 local pairs and effect order equivalent",
    "no public API or parallel route registry",
    "only seven paths changed",
    "recoverable checkpoint and independent audit"
  ],
  "approved_tests": [
    "navigation_local_contract_test.py on baseline and candidate",
    "contextual_sidebar_test.py",
    "navigation_layout_choice_test.py",
    "dashboard_forex_relocation_test.py",
    "quality_gate.py --tier standard",
    "build_reproducibility_test.py",
    "service_worker_upgrade_test.py"
  ],
  "rollback": "Own delta only; compare hashes and reverse patch check; baseline.tar retained; official generator for derived artifacts. No reset/stash/wide restore.",
  "approved_by": "Project owner, explicit NAV-REF-01 option A in this conversation, 2026-09-10",
  "separate_git_authority": "A4 only for create/use codex/nav-local-projection from the specified base; no product commit."
}
```

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-NAV-LOCAL-PROJECTION-20260910",
  "status": "approved",
  "root": "/Users/joaopauloalves/.codex/night-reviews/20260910/product",
  "mode": "SEQUENCIAL",
  "approved_branch": "codex/nav-local-projection",
  "create": [
    "/Users/joaopauloalves/.codex/night-reviews/20260910/product/docs/work/CHG-NAV-LOCAL-PROJECTION-20260910.md"
  ],
  "modify": [
    "/Users/joaopauloalves/.codex/night-reviews/20260910/product/docs/work/ACTIVE-TASK.md"
  ],
  "limits": "ACTIVE-TASK header only; preserve all previous bytes. No general context, agent, skill, index, policy or schema changes.",
  "approved_by": "Project owner, explicit NAV-REF-01 option A in this conversation, 2026-09-10"
}
```
