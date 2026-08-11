# Session Handoff - Planejamento FX, candidato validado localmente

- Data: 2026-08-11
- Branch: `feature/fx-planning` (criada de `main@8bb5f371` com autorização)
- `BASE_SHA` e HEAD: `8bb5f3714673`
- Árvore: candidato material não commitado (20 modificados + 4 caminhos novos)
- Manifest: 59 scripts, hashes reconciliados
- Build ID: `aa658d200db90b27`
- Publicação: nenhuma; commit, push, merge e deploy não autorizados

O estado Git e o runtime devem ser confirmados por `git status` e preflight.
Esta nota representa o candidato local gerado e testado; expira se fonte,
manifest, fixture, testes ou gerados mudarem.

## Implementado no candidato

- **Planejamento FX** (tela principal própria `#fxplan`, quinta entrada da
  rail; a Contabilidade voltou ao estado anterior): planejado ×
  realizado × normativo; baseline congelado, forecast vigente (rolling forecast
  do último fechamento real) e realizado imutável; revisões de premissas
  preservadas com reconstrução do forecast anterior.
- Motor puro `window.JPWFx.engine` (retorno sobre abertura, aportes após o
  resultado; realizado com a álgebra do MEI; overrides mês > ano > padrão;
  horizonte 1–600; custo cambial ponderado com `affectsFxCostBasis`).
- Agregado aditivo `S.fxPlanning` com guarda estrutural em `migrate()`,
  normalização profunda em cópia, preservação de campos desconhecidos,
  auditoria própria + `dgLogChange`.
- `reserveRequirementsCalc()` extraído do onboarding (decisão 1 do gestor) em
  `10-domain/07-reserve-requirements.js`; onboarding delega; caracterização
  campo a campo em teste.
- UI em quatro modos com badges REAL/PREMISSA, gráfico com transição
  histórico⇥projeção e USD/BRL, barras de rentabilidade, painel de reservas,
  tabela BASELINE × VIGENTE e resumo anual derivado; `.fxp-note` para textos
  estruturais (a `.expl` é colapsada pela ajuda contextual).
- Decisões vinculantes do gestor (2026-08-11) registradas em
  `docs/work/ACTIVE-TASK.md`; contrato da feature em
  `docs/architecture/FX-PLANNING.md`.

## Evidência

| Verificação | Resultado |
|---|---|
| `python3 tools/validate_project.py` | PASS — 59 scripts, precache equivalente, portátil reconstruído |
| `python3 -u tools/fx_planning_test.py` | PASS — motor, reservas, persistência, UI, navegação 5 telas/teclado/refresh/resíduos, mobile |
| `python3 tools/quality_gate.py --tier full` | PASS 18/18 — artefato `quality-20260811T183717-full.json` (pós-promoção a tela principal) |
| `git diff --check` | PASS |
| Chromium real | PASS — screenshots dos 4 modos entregues ao gestor |

## Próximas ações

1. Teste manual do gestor no navegador (`python3 tools/serve.py` → quinta tela
   **Planejamento FX** na navegação principal).
2. Autorizações separadas para commit e, depois, push/merge.
3. Push da reconciliação Galton (`main@8bb5f371` está 1 commit à frente de
   `origin/main`) também aguarda autorização.
4. Fase 2 registrada em `FX-PLANNING.md` (fora de escopo): layout
  personalizável do card, gráfico de aportes, cenários, importação do Excel,
  conciliação MEI.

## Limites e rollback

Nenhuma pendência N3 tocada; nenhum dado real em fixture. Rollback: reverter os
arquivos do contrato para `8bb5f3714673`; o agregado `fxPlanning` eventualmente
gravado em bases locais fica dormente e preservado pela `migrate()` de builds
anteriores. Não usar reset destrutivo.
