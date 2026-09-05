# Tarefa ativa — DASH-MACRO-01 + 02A · Visão Executiva Macro do Dashboard

- Data: 2026-09-04 (01) · 2026-09-05 (02A)
- Branch: `feature/dashboard-macro-overview`
- `BASE_SHA`: `c9104b1`
- Candidate: commit `3502331` (01 + 02A, commitado pelo gestor) + correção
  pós-commit no commit seguinte (N0-D, autorizado em 2026-09-05) em
  `tools/dashboard_macro_test.py`, `CHANGELOG.md` e `docs/work/ACTIVE-TASK.md`
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

## Revisão 02A — fatias 1–4 (HA da 01 = CHANGES_REQUESTED)

1. `#dashMacroGrid` em grade 2×2 no desktop (>1100px), uma coluna abaixo.
2. `.gd-analysis-grid` + `#dashMethodology` migram de `#dash` para
   `#execOverview` — um lugar só, nenhum `[data-layout-card]` migrado.
3. Painéis ampliados por domínio (fatos + barras contra o próprio teto).
4. `quick-actions` decomposto: Motor de Lote / Checklist / Parâmetros vão para
   `#execOverviewQuickNav`; o card do Dashboard fica com backup, armazenamento e
   Estatuto. Widget e id preservados em `#gdDashMain`.

**Fatia 5 = DASH-MACRO-02B, NÃO executada.** Mover `operational-clearance`,
`vrm` e `news-high-impact` toca `JP_WIDGET_DEFAULTS.dash` → N2 → RISK GATE
próprio (estratégia C1 aprovada só conceitualmente). Os dois CTAs "Abrir Forex"
pré-existentes (hero e `operational-clearance`) seguem no Dashboard por isso.

Regra absoluta cumprida: `13-dashboard-layout.js`, schema, version, migration
e defaults intocados (`git diff c9104b1 3502331 -- src/js/40-app/13-dashboard-layout.js` vazio).

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

Suíte `tools/dashboard_macro_test.py`, registrada no tier `standard`
(43 checks; `full` 54 — contagens em `docs/governance/QUALITY-GATES.md`).

Validação da 02A (2026-09-05, clone `~/Developer/App-Jp-Wealth`, HEAD `3502331`):

- Primeira execução do teste focado sobre o estado final: **falhou** em
  `atalhosForexNoDash` — seletor genérico `#dash [data-dash-go]` acusava os dois
  CTAs "Abrir Forex" pré-existentes na baseline (byte-idênticos em `c9104b1`).
  Classificação **TEST_HARNESS_FAIL**. Correção: seletor nominal
  (`motor`/`check`/`params`) + guarda de escopo pinando os dois CTAs.
- Teste focado após a correção: **PASS**.
- Gate `standard` sobre o estado final: **43/43 PASS**, `returncode 0` em todas
  as entradas — relatório `tools/.artifacts/quality-20260905T145839-standard.json`
  lido entrada a entrada (0 PRODUCT_FAIL, 0 TEST_HARNESS_FAIL,
  0 ENVIRONMENT_ERROR, 0 BASELINE_FAIL, 0 NOT_RUN).
- `validate_project.py` após o gate: derivados byte-idênticos ao commit.
- Navegador (Chromium): 1440px 2×2 nos temas claro e escuro pelo toggle nativo;
  1024px e 375px em uma coluna, sem scroll horizontal; `#execOverview` com
  Evolução/Ritmo, Metodologia e 3 atalhos, zero `[data-layout-card]`; SW
  registrado e ativo; zero `pageerror`, zero erro de console.
- `git diff --check` limpo. Tier `full` **não executado** (não solicitado).
- Estado: **PRONTO_PARA_REVISAO_HUMANA** — aguarda Human Acceptance visual.

## Rollback

Candidate commitado em `3502331` (12 caminhos, zero `Norma Vigente/`); a
correção pós-commit é o commit seguinte (3 arquivos, N0-D). Rollback é decisão
humana: descartar o commit da correção devolve `3502331`; descartar ambos
devolve `c9104b1`.
**`Norma Vigente/` não é tocada em nenhuma hipótese.** A branch remota
`feature/dashboard-macro-overview` (733981f) carrega merge de `b2e43e8` e deve
ser saneada antes da integração — integrar só `3502331` (+ correção) em `main`.
