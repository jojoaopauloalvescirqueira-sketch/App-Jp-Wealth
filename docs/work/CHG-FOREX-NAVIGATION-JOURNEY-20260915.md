# FOREX-NAV-JOURNEY-01 — contrato e compreensão

```yaml
{
  "schema": "jp-harness/chg/v1",
  "change_id": "CHG-FOREX-NAVIGATION-JOURNEY-20260915",
  "status": "approved",
  "objective": "Seis destinos por jornada; contexto operacional no Consolidado e checklist único em janela de Operação/Settings.",
  "risk_level": "N1",
  "authority_required": "A2",
  "target": {
    "root": "/Users/joaopauloalves/.codex/forex-navigation/20260915/product",
    "branch": "codex/forex-navigation-journey-20260915",
    "baseline_sha": "b2f0e54993ff79f7eaab62eba5b37510af43013c"
  },
  "scope": {
    "allowed_files": [
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/index.html",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/src/styles/app.css",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/src/js/40-app/01-navigation.js",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/src/js/20-ui/13-exec-views.js",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/src/js/20-ui/26-forex-engine-views.js",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/src/js/20-ui/28-fx-consolidated.js",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/src/js/40-app/09-settings-modal.js",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/src/js/40-app/11-operational-shell.js",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/src/js/40-app/13-dashboard-layout.js",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/src/js/manifest.json",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/build-id.js",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/docs/architecture/NAVIGATION-HIERARCHY.md",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/docs/architecture/FOREX-CONSOLIDATED.md",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/docs/architecture/CODE-MAP.md",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/docs/work/ACTIVE-TASK.md",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/docs/work/CHG-FOREX-NAVIGATION-JOURNEY-20260915.md",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/tools/forex_navigation_journey_test.py",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/tools/navigation_ia_test.py",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/tools/navigation_local_contract_test.py",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/tools/exec_submenu_test.py",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/tools/navigation_layout_choice_test.py",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/tools/navigation_order_test.py",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/tools/dashboard_macro_test.py",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/tools/dashboard_forex_relocation_test.py",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/tools/settings_modal_test.py",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/src/js/20-ui/25-dash-macro.js",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/src/js/40-app/17-economic-calendar.js",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/tools/fx_consolidated_ui_test.py",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/tools/research_navigation_test.py",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/tools/smoke_test.py",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/tools/fx_planning_test.py",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/tools/operation_history_test.py",
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/product/tools/exec_three_column_test.py"
    ],
    "allowed_actions": [
      "edição delimitada",
      "testes sintéticos",
      "derivados oficiais",
      "auditoria independente",
      "recovery e comparação visual"
    ],
    "forbidden_actions": [
      "staging",
      "commit do produto",
      "push",
      "PR",
      "merge",
      "deploy",
      "reset",
      "stash",
      "mudança financeira/persistência/importador/gates/CI"
    ]
  },
  "acceptance_criteria": [
    "Seis destinos e aliases preservados",
    "Contas analítica e operacional independentes",
    "Nós/respostas/rascunhos únicos e preservados",
    "Preferências sem regravação por navegação",
    "Foco, mobile, temas e modais válidos"
  ],
  "approved_tests": [
    "focal novo e regressões da proposta",
    "standard/FULL vigente, reprodutibilidade, PWA e portátil"
  ],
  "derived_artifacts": {
    "allowed": [
      "build-id.js",
      "dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html"
    ],
    "generation_commands": [
      "python3 tools/rebuild_monolith.py"
    ],
    "manual_edit": "forbidden"
  },
  "data": {
    "test_policy": "synthetic_only",
    "schema_change": "forbidden"
  },
  "rollback": {
    "source": [
      "/Users/joaopauloalves/.codex/forex-navigation/20260915/evidence/baseline-recovery.tar.gz"
    ],
    "verification": [
      "351 hashes/modos da base experimental",
      "restaurar somente delta próprio no destino autorizado, nunca outra worktree"
    ]
  },
  "approved_by": "proprietário; PLEASE IMPLEMENT THIS PLAN e seleciono A para PROPOSAL.md",
  "approved_at": "2026-09-15",
  "expires_on": [
    "drift material",
    "ampliação de escopo/risco",
    "mudança de raiz/branch"
  ]
}
```

```yaml
{
  "schema": "jp-harness/ctx/v1",
  "context_change_id": "CTX-FOREX-NAVIGATION-JOURNEY-20260915",
  "status": "approved",
  "root": "/Users/joaopauloalves/.codex/forex-navigation/20260915/product",
  "mode": "CONCORRENTE",
  "approved_branch": "codex/forex-navigation-journey-20260915",
  "create": [
    "docs/work/CHG-FOREX-NAVIGATION-JOURNEY-20260915.md"
  ],
  "modify": [
    "docs/work/ACTIVE-TASK.md",
    "docs/architecture/NAVIGATION-HIERARCHY.md",
    "docs/architecture/FOREX-CONSOLIDATED.md",
    "docs/architecture/CODE-MAP.md"
  ],
  "preserve": [
    "histórico integral de ACTIVE-TASK",
    "candidate cadastral original e 13 deltas herdados",
    "main, stash, evidências e demais worktrees"
  ],
  "do_not_touch": [
    "CURRENT-STATE",
    "SESSION_HANDOFF",
    "normas",
    "AGENTS",
    "Harness",
    "skills",
    "CI/gates"
  ],
  "approved_by": "proprietário; PLEASE IMPLEMENT THIS PLAN e seleciono A para PROPOSAL.md",
  "approved_at": "2026-09-15"
}
```

## Brief

JP Wealth organiza análise, planejamento e registro financeiro local. Este lote reduz a distância entre orientação e execução: Consolidado passa a entrada; contexto operacional usa exclusivamente o read model V11 existente; checklist torna-se ação contextual de Operação. Não altera elegibilidade, fontes MT5/Manual, cadastro ou gravação do checklist.

Base Git b2f0e549 e base experimental 351 inputs/build 47b00f20c4f61490 são distintas. A base experimental tem fingerprint 0ecf280ee9b527a3d8ff0ce6dba6959a64f022ae29f65704ecbc38279c3b2363 e 13 caminhos herdados, reproduzidos por autorização expressa; isso não integra nem aceita o cadastro. Identidade/recuperação e autorização em ../evidence/isolation-authorization.json e baseline-candidate.json.

Fontes verificadas: AGENTS; Harness mestre SHA c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8 §§12–14/24/31/36–49; X1 IMPLEMENTAR por leitura explícita; NAVIGATION-HIERARCHY; 01-navigation (registro e consumidores), 13-exec-views (hidden/inert), 26-forex-engine-views (read model), 28-fx-consolidated (seleção/importação), 09-settings-modal (movimentação dos grids/subdiálogos), 13-dashboard-layout (preferências v6). README/CURRENT-STATE/CONTEXT-MAP contêm fotografias históricas, não a identidade atual nem autorização de curadoria geral.

Riscos: confundir conta analisada com operacional, perder widgets/rascunhos ao mover DOM, duplicar checklist, deixar foco em área inerte ou regravar preferências. Prova: asserts sobre DOM real, snapshots de estado/disco, contagem de nós/chamadas, navegação e modal via teclado, fixtures de contas distintas, filtros e layout legado. Expectativas antigas de oito destinos serão substituídas somente onde o comportamento novo foi expressamente aprovado; guardas financeiras e de persistência permanecem intactas. Ganho de usabilidade depende da revisão humana posterior.

## Evidências e limites

Evidências em /Users/joaopauloalves/.codex/forex-navigation/20260915/evidence. Será entregue candidate identificado, delta próprio separado do herdado, gates reais, auditoria independente, recovery e comparador. Nenhum aceite humano, integração ou homologação financeira antecipados. OPEN-05/V11/FCR/FEO, A12 parcial, AUD-05/P2 e dívidas anteriores permanecem fora do escopo.

## Consumidores diretos identificados na execução

O plano aprovado inclui atualizar atalhos e localização. 25-dash-macro.js contém o CTA Abrir Forex e os textos Conta/Preparação; 17-economic-calendar.js contém a orientação textual Forex → Visão Geral. Seu delta limita-se a destinos/rótulos dessa jornada. fx_consolidated_ui_test.py conserva os asserts de importação; somente o assert inicial da ordem do submenu acompanha a ordem nova expressamente aprovada. Esses consumidores adicionais concretizam o escopo funcional recebido, sem mudar fórmulas, parsers, fixtures ou gates.

## Consumidores obrigatórios identificados na validação

`tools/research_navigation_test.py` e `tools/smoke_test.py` também declaram a rota primária Forex/ownership da antiga overview. Antes de sua edição, ficam delimitadas somente essas expectativas de navegação deliberadamente alteradas. Nenhum gate, cálculo, proteção ou fixture financeira será modificado. A regressão `dashboard_forex_relocation_test.py` falhou no mesmo oráculo financeiro na baseline; sua expectativa permanece intacta e o layout v6 será exercitado independentemente no novo focal.

## Revisão após a auditoria V1

O achado FJ-AUD-01 (P2) exige retirar o proprietário de layout inexistente `check`, mantendo o checklist como modal não editável e o rascunho do Editor no host válido. V1 e seus resultados permanecem preservados. Antes da edição, incluem-se os consumidores `fx_planning_test.py`, `operation_history_test.py` e `exec_three_column_test.py`: somente rotas/ordem de menu e entrada real no Histórico/Operação serão adaptadas. Asserções financeiras, foco/cursor, geometria, preferências e gates permanecem. O focal novo cobrirá Editor com rascunho → checklist → Fechar → Cancelar/Concluir. A V2 terá identidade, FULL e revisão focal próprios.
