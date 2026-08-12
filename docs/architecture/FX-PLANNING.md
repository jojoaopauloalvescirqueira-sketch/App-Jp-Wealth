# Planejamento FX — contrato da feature

Motor de planejamento patrimonial temporal para Forex, do domínio
Contabilidade/Patrimônio, apresentado como **tela principal própria**
(`#fxplan`, quinta entrada da rail `.tab`/`data-screen`, decisão do gestor de
2026-08-11 — os quatro modos são internos à tela, nunca abas principais).
Deriva conceitualmente da planilha histórica `Planejamento FX.xlsx` **sem
reproduzir suas inconsistências** (coluna de reserva "FUNDO (FIIS)" com 10%,
proxy de despesas como % do patrimônio, taxa única de dólar, coluna de aporte
instável, datas hardcoded). A planilha original contém anotações pessoais e
**nunca entra no repositório**; toda fixture é sintética.

## Três classes de informação — nunca se misturam

| Classe | O que é | Onde vive |
|---|---|---|
| PLANEJADO | premissas do operador (taxa, aportes, câmbio projetado) | `plan.baseline` / `plan.current` |
| REALIZADO | fechamentos mensais efetivos e ledger cambial | `plan.actuals` / `plan.contributions` |
| NORMATIVO | FCR/FEO exigidos pelo Estatuto (Arts. 13.1, 13.2, 26.2) | `reserveRequirementsCalc()` — nunca duplicado |

A interface marca cada valor com badge `REAL` ou `PREMISSA`; rentabilidade
planejada **nunca** deriva de perfis de risco (a V10 removeu projeções por
perfil; ADR-0010 pendente) e nenhum texto promete retorno.

## Três séries temporais (decisão do gestor, 2026-08-11)

- **Baseline** — premissas congeladas na aprovação do plano (`baseline.frozenAt`).
  Nunca é sobrescrito; revisões não o tocam.
- **Forecast vigente** — realizado até o último fechamento + projeção a partir
  do saldo efetivamente realizado com as premissas de `plan.current`.
- **Realizado** — histórico imutável a mudanças de premissas.

Revisar premissas move o `current` anterior para `revisions[]` (snapshot leve,
`supersededAt`); `fxForecastAtRevision()` reconstrói o forecast como era,
usando os meses com `closedAt ≤ supersededAt` (meses editados depois são
reconstrução aproximada, sinalizada na interface). Comparações suportadas:
Realizado × Baseline, Realizado × Forecast anterior, Forecast atual × Baseline.

## Convenções matemáticas (documentadas e testadas)

- **Projeção**: a rentabilidade incide sobre o saldo de ABERTURA; aportes entram
  depois do resultado — `close = open + open·rate + aportes`.
- **Realizado**: mesma álgebra do MEI-JP (`03-mei-jp.js`, Correções 4/5):
  `R_aj = (V_t − V_{t−1} − F_t)/V_{t−1}` ⇔ `profit = close − open − aportes`.
  Entrada por taxa deriva o USD; entrada por USD deriva a taxa (`derivedField`).
  Nenhuma metodologia nova de retorno com fluxo intra-mês foi criada.
- **Precedência de taxa**: override de mês > override de ano > padrão.
- **Câmbio médio de aquisição**: `Σ BRL investido ÷ Σ USD adquirido` — média
  ponderada, nunca média das cotações. Só transações `affectsFxCostBasis:true`
  (BRL→USD); créditos USD-nativos (Prop Firm) ficam fora por construção.
- **Quatro câmbios distintos, três tempos** — nenhum sobrescreve outro:

  | Conceito | Tempo | O que é | Onde vive |
  |---|---|---|---|
  | `acquisitionFxRate` | passado | taxa paga numa aquisição | aporte (persistido) |
  | `valuationFxRate` | passado | avaliação registrada de um mês fechado | fechamento (persistido) |
  | `currentUsdBrlQuote` | **presente** | referência externa corrente | `10-domain/08-usd-brl-quote.js` (cache técnico) |
  | `projectedFxRate` | futuro | premissa do operador | `plan.baseline` / `plan.current` |

  Alterar projeção nunca reescreve custo histórico, e a **premissa futura nunca
  vale como valor presente**: até `JPW-FGDEKM` o patrimônio corrente em BRL era
  convertido por `projectedFxRate`, o que apresentava uma hipótese sobre o futuro
  como fotografia do presente.

  A referência corrente vem do Frankfurter (taxas do BCE), o mesmo provedor de
  `10-domain/04-stop-statistics.js`, sem chave. É **referência diária**, não spot
  intradiário — por isso `referenceDate` (data econômica) e `fetchedAt` (quando
  consultamos) são grandezas separadas, e a interface diz "USD/BRL de referência",
  nunca "ao vivo". Sem referência disponível, o presente sai em USD; cair em
  `projectedFxRate` é proibido. O cache é técnico, fora de `S.fxPlanning` e do
  baseline.

  Conversão por tempo: mês fechado usa a `valuationFxRate` dele; o mês corrente
  sem taxa registrada usa a referência externa; projeção usa `projectedFxRate`.
  Mês passado sem taxa própria não é convertido — inventar taxa seria pior que
  omitir o ponto.
- Derivados (séries, saldos, variâncias, custo médio, resumo anual) **nunca
  persistem** — recalculados pelas funções puras a cada uso.

## Persistência — agregado `S.fxPlanning` (v1)

```json
{"schemaVersion":1, "plan":null, "auditLog":[]}
```

`plan`: `{id, name, createdAt, updatedAt, baseline, current, revisions[],
actuals{AAAA-MM}, contributions[]}`. Estruturais (`startMonth`,
`horizonMonths`, `initialBalanceUsd`) congelam com o baseline;
`initialBalanceUsd` é **parâmetro do planejamento** — não é fonte canônica da
Conta Mestre nem do patrimônio institucional. Fechamentos são contíguos desde o
início (`fxNextOpenMonth`); editar mês fechado é auditado e preserva `closedAt`.

- Guarda estrutural de boot: `fxPlanningNormalizeState()` em
  `04-persistence.js` (migrate roda antes dos módulos tardios carregarem —
  mesmo motivo de mvpNotes/dg). Só a FORMA do envelope; poda do `auditLog` em
  400 como o `dg.changeLog`.
- Normalização profunda: em CÓPIA na camada de acesso (`fxActivePlan()`);
  campos desconhecidos do estado persistido atravessam intactos
  (STATE-SCHEMA.md §3) e a versão limpa nunca é gravada de volta sem mutação.
- Toda mutação audita em `fxPlanning.auditLog`
  (`FX_PLAN_CREATED/ASSUMPTION_CHANGED/FX_MONTH_ACTUAL_RECORDED/EDITED/`
  `FX_CONTRIBUTION_RECORDED/REMOVED/FX_PLAN_DELETED`) e registra em
  `dgLogChange` — o aviso de backup pendente cobre o Planejamento FX.
- O agregado viaja no backup normal (`jpwealth_v9_state`); o envelope não muda.
  Builds antigos preservam o agregado dormente — rollback por construção.

## Reservas — fonte única

`reserveRequirementsCalc()` (`src/js/10-domain/07-reserve-requirements.js`) é a
extração pura da matemática do antigo `reserveCalc()` do onboarding (decisão 1
de 2026-08-11): FCR = 15% × capital nominal da Conta Mestre; FEO = 6 × despesas
elegíveis; campo a campo idêntica (caracterização em `fx_planning_test.py`).
Consumidores: onboarding (delegação) e `fxReservePanelData()` com fontes
canônicas — capital de `S.params.saldoIni`, despesas/constituídos declarados no
onboarding. O painel calcula e informa; nunca movimenta capital.

## Distinção deliberada de sistemas vizinhos

- **`mei.history`** registra equity mensal da conta para o modelo estatístico
  (retornos log ajustados, GBM). O Planejamento FX registra patrimônio
  consolidado do plano + aportes por origem + câmbio. **Separados no MVP por
  decisão do gestor**; nenhuma conciliação nesta fase — lançar o realizado em
  um não alimenta o outro.
- **`acctPace`/projeção diária** cobrem o período anual de gestão pelo perfil;
  o Planejamento FX é mensal e multianual por premissas do operador. Coexistem.

## Módulos (clássicos, anexados ao fim do manifest)

| Arquivo | Papel |
|---|---|
| `10-domain/07-reserve-requirements.js` | FCR/FEO — função pura compartilhada |
| `30-accounting/05-fx-planning/01-fx-model.js` | modelo, validação, premissas, revisões |
| `30-accounting/05-fx-planning/02-fx-engine.js` | séries, variâncias, custo cambial, resumo anual |
| `30-accounting/05-fx-planning/03-fx-state.js` | ponte com `S`, mutações auditadas, painel de reservas |
| `30-accounting/05-fx-planning/04-fx-charts.js` | SVGs sobre o cromo `CH` + resumos textuais |
| `30-accounting/05-fx-planning/05-fx-ui.js` | quatro modos, formulários, tabela mensal |

Superfície pública: `window.JPWFx.{model,engine,state,charts,ui}` +
`reserveRequirementsCalc` global. Motor independente de DOM.

## Interface

Tela principal `#fxplan` com o card `#fxPlanningCard` (fora da personalização
de layout nesta fase). Quatro modos internos — a chave `table` do quarto modo é
contrato de DOM e permanece, embora o rótulo seja **Histórico**:

| Modo | Chave | O que traz |
|---|---|---|
| Visão Geral | `overview` | grade 2fr/1fr: herói (patrimônio → desvio → baseline), gráfico de trajetória com janela 12m/24m/60m e alternância USD/BRL, rentabilidade mensal; na lateral, reservas com barras de cobertura e ledger cambial com a referência USD/BRL |
| Planejamento | `planning` | estruturais congelados (leitura) × revisáveis (edição), exceções sob disclosure, prévia do efeito da revisão, trilha de revisões, zona de perigo com confirmação `EXCLUIR` |
| Realizado | `actuals` | cartão de tarefa do mês aberto, fechamento mensal com prévia do derivado, ledger de aportes |
| Histórico | `table` | BASELINE × VIGENTE × desvio com coluna Mês fixa e filtro de fase, resumo anual derivado, trilha de auditoria |

**Três prévias ao vivo, nenhuma fórmula reescrita na UI.** Fechamento, revisão e
janela mostram o efeito antes de confirmar. O padrão é sempre o mesmo: montar um
candidato em memória e perguntar ao motor — `fxActualTimeline` para o
fechamento, `fxForecastTimeline` para a revisão, e a janela apenas fatia a série
já calculada. Enquanto o usuário não confirma, `plan.actuals`, `current` e
`revisions` permanecem intactos. Reimplementar a álgebra aqui seria duplicar
domínio; se uma prévia nova precisar de algo que o motor não expõe, o caminho é
parar e reportar, não recalcular na tela.

**Layout por consulta de container, não de viewport** (`#fxplan` é o container):
três estados discretos — mínimo <480, médio, máximo ≥1120 — governam escala
tipográfica, razão dos gráficos, rampa de padding e colapso das duas colunas. O
painel não conhece a janela, só o próprio container.

Invariante de hierarquia: o valor do patrimônio é ≥ 1,5× qualquer outro valor em
todo estado. A regra vive em token (`--jp-fs-data-md` redefinido por camada), não
em disputa de especificidade — a regra do tema tem especificidade maior e venceria
qualquer seletor local.

Acessibilidade: estado nunca só por cor (badges/texto, e as três séries do
gráfico também se separam pelo padrão do traço), abas com `tabpanel`,
`aria-controls`, foco roving e navegação por setas, resumo textual dos gráficos,
labels reais, controles nativos; tabelas largas rolam em `.fxp-tablewrap`.
Textos estruturais usam `.fxp-note` (a classe `.expl` é colapsada pela ajuda
contextual e fica reservada à prosa doutrinária).

## Testes

`tools/fx_planning_test.py` (tier `standard`): casos 1–20 da especificação,
Baseline × Forecast × Realizado, custo cambial ponderado, caracterização
campo a campo das reservas, round-trip de persistência com reload, base legada
sem o agregado, agregado corrompido, preservação de campos desconhecidos,
contiguidade de fechamentos, fluxo real de UI e contenção em viewport móvel.

## Fora de escopo desta fase (deliberado)

Importação do Excel; exportação CSV/relatório; múltiplos cenários; gráfico
mensal dedicado de aportes (dados presentes na tabela e no resumo anual);
registro do card no sistema de personalização de layout; retiradas no
realizado; conciliação com `mei.history`/`ledger`/`accounts[]`; qualquer
pendência N3.
