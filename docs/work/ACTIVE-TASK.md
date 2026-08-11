# Tarefa ativa — Planejamento FX (motor de planejamento patrimonial temporal)

- Data de abertura: 2026-08-11
- `BASE_SHA`: `8bb5f3714673` (`main` com a reconciliação Galton commitada)
- Branch autorizada: `feature/fx-planning`
- Nível: N2 delimitado (agregado `S.fxPlanning` + ponto de migração) + N1 (UI,
  navegação, gráficos, acessibilidade) + N0-D (testes e documentação)
- Autoridade: A2 para o escopo N1; A3 delimitada ao agregado `S.fxPlanning` e às
  alterações estritamente necessárias de persistência/migração; extração da
  matemática de `reserveCalc()` para função pura compartilhada expressamente
  autorizada pelo gestor (decisão 1 de 2026-08-11). N3/A4 fora do escopo.
- Git: criação da branch autorizada e executada. Commit, push, merge e deploy
  permanecem pendentes de autorização separada.
- Tarefa anterior (Galton Board): concluída, integrada em `fb33ceb` e
  reconciliada em `8bb5f37`; registro histórico preservado no Git.

O estado Git corrente (branch, HEAD e árvore) deve ser confirmado pelo preflight.
Este contrato não substitui fatos mutáveis do disco.

## Objetivo

Implementar a feature **Planejamento FX** no domínio Contabilidade/Patrimônio
(tela `contab`): motor de planejamento patrimonial temporal para Forex derivado
conceitualmente da planilha histórica `Planejamento FX.xlsx`, sem conversão
célula-a-célula, separando rigorosamente três classes de informação —
**Planejado**, **Realizado** e **Normativo** — e três séries temporais —
**Baseline (plano original)**, **Forecast vigente (rolling forecast)** e
**Realizado (histórico)**.

## Decisões do gestor (2026-08-11, vinculantes)

1. **FCR/FEO**: não usar `S.onboarding.reserve*` como fonte normativa permanente
   (são snapshots derivados). Extrair a matemática de `reserveCalc()`
   (`04-onboarding.js:287`) para função pura compartilhada consumindo as fontes
   canônicas (capital nominal: `S.params.saldoIni`; despesas elegíveis:
   `S.onboarding.reserveMonthlyExpenses`). Onboarding e Planejamento FX consomem
   a mesma função. Constantes normativas não duplicadas.
2. **`mei.history`**: separado no MVP. Diferença semântica MEI × Planejamento FX
   documentada explicitamente. Nenhuma conciliação nesta fase.
3. **Patrimônio inicial do plano**: self-contained, nomeado e documentado como
   *parâmetro do planejamento* — nunca fonte canônica da Conta Mestre nem do
   patrimônio institucional.
4. **Convenção da projeção**: rentabilidade planejada incide sobre o saldo de
   abertura do mês; aportes entram depois do resultado. Documentada em código,
   testes e interface. Para o **Realizado**, não inventar metodologia nova de
   rentabilidade com fluxos intra-período: preservar a metodologia financeira já
   utilizada pelo sistema (MEI-JP), evitando métrica enganosa por divisão
   simplista.
5. **Branch**: `feature/fx-planning`.
6. **Navegação (revisão pós-candidato, 2026-08-11)**: o Planejamento FX é
   **tela principal própria** — quinta entrada da rail (`#fxplan`), mesma
   mecânica `.tab`/`data-screen` das quatro telas atuais, sem navegação
   paralela; os quatro modos são internos à tela. A Contabilidade volta ao
   estado estrutural anterior. Motor, modelo Baseline × Forecast × Realizado,
   persistência `S.fxPlanning` e regras FCR/FEO permanecem intocados.

## Requisito adicional — Baseline × Forecast × Realizado

- O rolling forecast **não destrói** o planejamento original.
- `baseline` = premissas originalmente aprovadas, congeladas na aprovação do
  plano; nunca sobrescrito silenciosamente.
- `forecast vigente` = recalculado a partir do último fechamento realizado,
  mantendo as premissas futuras vigentes.
- `realizado` = histórico imutável a mudanças posteriores de premissas.
- Comparações exigidas: Realizado × Baseline; Realizado × Forecast anterior;
  Forecast atual × Baseline. Revisões de premissas guardadas como snapshots
  leves (`assumptionRevisions`), sem versionamento complexo de séries.

## Ordem de implementação obrigatória

1. Modelo de domínio; 2. motor matemático puro; 3. testes; 4. normalização/
persistência; 5. somente depois UI e gráficos. Não começar pela interface.

## Arquivos permitidos

- `src/js/10-domain/07-reserve-requirements.js` (novo — função pura FCR/FEO);
- `src/js/30-accounting/05-fx-planning/**` (novos módulos da feature);
- `src/js/40-app/04-onboarding.js` — somente delegação de `reserveCalc()` à
  função compartilhada, sem mudança de comportamento;
- `src/js/00-core/03-default-state.js` — agregado `fxPlanning` em `DEFAULTS`;
- `src/js/00-core/04-persistence.js` — chamada ao normalizador em `migrate()`;
- `index.html` (seção na tela `contab`) e `src/styles/app.css`;
- `src/js/manifest.json`, `sw.js`, `build-id.js` e `dist/**` somente pela
  integração/rebuild oficial (`tools/rebuild_monolith.py`);
- `tools/fx_planning_test.py` e fixtures sintéticas em `data/samples/`;
- `tools/smoke_test.py` — somente o contrato de contagem de telas (4 → 5),
  exigido pela decisão 6;
- `tests/README.md` e documentação afetada: `docs/architecture/**`,
  `docs/governance/**`, `CHANGELOG.md`, `PROJECT-FILES.txt`, `README.md`,
  `SESSION_HANDOFF.md`.

Qualquer outro caminho exige nova avaliação antes de editar.

## Invariantes

- Nenhuma das dez pendências N3 é tocada; nenhuma fórmula, perfil, fase, limite,
  MDD, LIFO, stop, quarentena ou artigo do Estatuto muda.
- A extração de `reserveRequirements()` preserva bit a bit os resultados atuais
  do onboarding (teste de caracterização antes/depois).
- O módulo exibe FCR/FEO calculados pela função compartilhada e valores
  constituídos declarados na fonte existente; não cria segunda fonte de verdade,
  não executa transferências, não redistribui capital.
- Agregado `S.fxPlanning` é aditivo: `migrate()` o introduz sem alterar campo
  existente; campos desconhecidos preservados; sem `localStorage.clear()`;
  builds antigos preservam o agregado dormente (rollback por construção).
- Valores derivados (saldos, séries, variâncias, câmbio médio, resumo anual)
  nunca são persistidos — sempre recalculados pelo motor puro.
- Câmbio: `câmbioMédio = Σ BRL investido / Σ USD adquirido`; transações com
  `affectsFxCostBasis:false` (entradas USD-nativas, ex.: Prop Firm) nunca
  alteram o custo médio; `acquisitionFxRate`, `valuationFxRate` e
  `projectedFxRate` são conceitos separados; alterar projeção nunca reescreve
  custo histórico.
- Terminologia: "premissa/projeção/simulação"; nunca promessa de retorno, sinal
  ou previsão de mercado. Rentabilidade planejada nunca deriva de perfis de
  risco.
- Motor de cálculo independente de DOM; scripts novos anexados ao fim do
  manifest sem reordenar o legado; precache equivalente ao manifest.
- Nenhum dado pessoal real em fixtures — a planilha original contém anotações
  privadas; toda fixture é sintética.
- Sem dependência nova de runtime, CDN ou rede externa.

## Critérios de aceite

1. Criar plano com nome, mês inicial, saldo inicial (parâmetro do plano),
   horizonte livre e rentabilidade padrão gera todos os meses `YYYY-MM`
   programaticamente.
2. Projeção composta matematicamente correta (casos 1–20 da especificação da
   tarefa, incluindo horizonte 120 meses sem drift relevante).
3. Overrides de rentabilidade com precedência mês > ano > padrão, visíveis.
4. Aportes planejados (pessoal × prop firm separados) alteram a trajetória
   corretamente; realizados registrados separadamente.
5. Fechamento de mês: realizado vira histórico; baseline preservado; forecast
   futuro parte do saldo efetivamente realizado; premissas alteradas depois não
   reescrevem realizado nem baseline.
6. Entrada de realizado por taxa OU por valor USD, com o campo derivado
   claramente identificado e sem divergência silenciosa entre %, $ e saldo.
7. Custo médio do dólar ponderado correto (caso de referência:
   10.000/5,00 + 10.000/6,00 → ≈ 5,454545 R$/USD); Prop Firm USD-nativo não
   contamina o custo.
8. FCR/FEO exibidos a partir da função compartilhada (mínimo exigido, atual,
   cobertura, déficit, meses FEO), com os mesmos resultados do onboarding.
9. Resumo anual derivado automaticamente das datas; sem blocos hardcoded.
10. Gráfico principal Planejado × Realizado com transição visual
    histórico→projeção no último mês realizado, USD/BRL alternável usando a
    taxa correta de cada contexto.
11. Refresh/reabertura preserva dados; round-trip de backup preserva o
    agregado; base anterior sem o agregado carrega sem perda.
12. Testes existentes continuam passando; tier `full` PASS no candidato final.
13. UI integrada ao design system (tokens, `.dtable`, toolkit `CH`, numerais
    tabulares), acessível (não só cor; teclado; labels; resumo textual dos
    gráficos) e responsiva (desktop analítico, mobile resumo+detalhe).
14. Nenhum cálculo financeiro relevante existe apenas no DOM/renderizador.

## Fora de escopo (deliberado)

Importação do Excel; exportação CSV/relatório; múltiplos cenários
(Conservador/Base/Expansão); versionamento ilimitado de forecasts; conciliação
com `mei.history`, `ledger` ou `accounts[]`; previsão de mercado; automação de
aportes/transferências; pendências N3; refatorações não necessárias.

## Plano de rollback

Reverter os arquivos listados para `BASE_SHA` na branch; nenhum reset
destrutivo; o agregado `fxPlanning` eventualmente gravado em bases locais fica
dormente e preservado por `migrate()` de builds anteriores.

## Baseline

- Preflight `--mode edit`: PASS em `8bb5f3714673`, árvore limpa, 53 scripts.
- Gate `full` 17/17 PASS na árvore `fb33ceb` (idêntica a `8bb5f37` exceto os
  três documentos de governança reconciliados).

## Resultado do candidato (2026-08-11)

- Implementação concluída na ordem obrigatória (domínio → motor → testes →
  persistência → UI) na branch `feature/fx-planning`, base `8bb5f3714673`,
  candidato não commitado. Build oficial regenerado: `aa658d200db90b27`.
- Decisão 6 aplicada: Planejamento FX promovido a **tela principal própria**
  (`#fxplan`, quinta `.tab` da rail); Contabilidade restaurada sem resíduos;
  smoke test passou ao contrato de cinco telas; faixa 901–1160px exibe
  pílulas numeradas para os cinco rótulos caberem no cabeçalho (defeito de
  overflow detectado pelo gate e corrigido; gate full reexecutado:
  PASS 18/18, artefato `quality-20260811T183717-full.json`). Motor, séries,
  persistência e reservas intocados nesta etapa.
- Manifest: 53 → 59 scripts (6 novos anexados ao fim, legado não reordenado);
  precache equivalente; `validate_project.py` PASS.
- `reserveCalc()` do onboarding delega à função pura compartilhada; a suíte
  caracteriza campo a campo os 16 retornos em 4 cenários (normal, mínimos
  exatos, déficit duplo, bordas zero) — comportamento preservado.
- `tools/fx_planning_test.py` no tier `standard`: casos 1–20, Baseline ×
  Forecast × Realizado (baseline intacto após revisão; forecast anterior
  reconstruído; realizado imutável), custo cambial ponderado com exclusão de
  USD-nativo, metodologia MEI no realizado, round-trip/base legada/agregado
  corrompido/campos desconhecidos/contiguidade, fluxo real de UI e viewport
  móvel sem scroll horizontal. PASS.
- `python3 tools/quality_gate.py --tier full`: **PASS 18/18**, zero
  `PRODUCT_FAIL`/`TEST_HARNESS_FAIL`/`ENVIRONMENT_ERROR`/`BASELINE_FAIL`/
  `NOT_RUN`; artefatos `quality-20260811T181240-full.json` (card na
  Contabilidade) e `quality-20260811T183717-full.json` (tela principal).
- Verificação visual em Chromium real (screenshots dos 4 modos entregues ao
  gestor); valores da tela conferidos manualmente contra o motor.
- Nenhuma pendência N3 tocada; nenhum dado real ou credencial em fixture.
- Pendentes: teste manual do gestor e autorizações separadas de commit/push/
  merge. Recortes deliberados registrados em `FX-PLANNING.md` (fora de escopo).
