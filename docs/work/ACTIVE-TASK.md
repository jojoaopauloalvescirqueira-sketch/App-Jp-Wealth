# Tarefa ativa — DASH-MACRO-01 · Visão Executiva Macro do Dashboard

- Data: 2026-09-04
- Branch: `feature/dashboard-macro-overview`
- `BASE_SHA`: `c9104b1`
- Classificação: **N1** (funcional não normativo) + **N0-V** (visual)
- Autoridade: **A2** — implementação delimitada, autorizada pelo gestor.
  **Commit, push, merge e deploy NÃO autorizados.**

## Objetivo

O Dashboard deixa de ser um resumo de Forex e passa a ser o panorama dos quatro
módulos globais — Forex, Finanças Pessoais, Research e Alladin —, cada um com um
resumo útil da própria área e acesso ao respectivo módulo.

## Arquitetura

Camada fixa `#dashMacro`, irmã de `#gdDashGrid` e **fora** dele. Não carrega
`[data-layout-card]`. O motor de layout enumera apenas
`:scope > [data-layout-card]` dentro de `#gdDashMain`, então a camada é invisível
para ele: preferência salva permanece válida, nenhum id persistido muda, nenhuma
migração. É o que mantém a mudança em N1.

## Fontes canônicas (uma por card, sem segunda implementação)

| Card | Fonte | Rota |
|---|---|---|
| Forex | `compute()` → `getOperationalClearance(c)` | `forex-overview` |
| Finanças Pessoais | `pfCompMetrics(pfCurrentMonthKey())` + `pfPendingBefore` | `personal-finance` |
| Research | `S.nocoda.studies`, `S.pivotStudies.studies`, `ecalEvents()` | `research-forex` |
| Alladin | `JPWAlladin.compat()` → `leitura.posicoes()` | `alladin` |

## Invariantes

- `PARTIAL` ≠ total conhecido · `UNAVAILABLE` ≠ R$ 0 · `BLOCKING` ≠ 0 posições
- cache nulo do calendário ≠ 0 eventos
- render jamais escreve; navegar jamais escreve
- `#gdDashMain` conserva exatamente os mesmos `[data-layout-card]`
- falha de um domínio não derruba os outros três
- nenhum rótulo novo de "Equity" — ADR-0001 permanece pendente
- `#execOverview` preservado, inclusive o comentário de finalidade

## Teto de chamadas pesadas por render

`compute()` ≤1 · `pfCompMetrics()` ≤1 · `leitura.posicoes()` ≤1 ·
`saldoDeCaixa()` = 0 · `acctPace()` = 0 · `acctProjection()` = 0 ·
`fxOverviewLive()` = 0

## Arquivos autorizados

`index.html` · `src/styles/app.css` · `src/js/20-ui/25-dash-macro.js` ·
`src/js/manifest.json` · `sw.js` · `tools/dashboard_macro_test.py` ·
`tools/quality_gate.py` · `docs/governance/QUALITY-GATES.md` · `CHANGELOG.md` ·
`docs/work/ACTIVE-TASK.md` · derivados pelo gerador oficial (`build-id.js`,
`dist/…PORTABLE.html`).

## Testes

Suíte nova `tools/dashboard_macro_test.py`, registrada no tier `standard`.
Gate `standard` executado: **43/43 PASS**, 0 PRODUCT_FAIL, 0 TEST_HARNESS_FAIL,
0 ENVIRONMENT_ERROR, 0 NOT_RUN.

## Rollback

Sem commit. Descartar apenas os caminhos de `DASH-MACRO-01` e remover os dois
arquivos novos. **`Norma Vigente/` não é tocada em nenhuma hipótese.** A branch
volta a `c9104b1`.
