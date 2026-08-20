# Finanças Pessoais — contrato do domínio

Schema v1 **congelado** pelo operador em 2026-08-18 (PF-01). Este documento é a
autoridade normativa do agregado `S.personalFinance`. Qualquer necessidade de
alteração estrutural descoberta daqui em diante **não** modifica o schema
silenciosamente: PARAR, reportar e propor migração formal `schemaVersion 1 → 2`.

## Fronteiras

Domínio **fechado**: não cruza contas de trading, Execution Board, Estatuto,
risco operacional, Contabilidade de trading nem Planejamento FX. Renda vinda de
FX/trading é, nesta fase, um registro de receita pessoal como outro qualquer —
nenhuma integração automática sem contrato futuro específico.

## Política monetária — `BRL_CENTS`

- Todos os montantes do agregado são **inteiros em centavos de BRL**
  (`R$ 1.420,50 → 142050`). `null` = não informado; `0` = zero explicitamente
  declarado. **Ausência ≠ zero** é invariante normativa.
- Fonte única: `parseBRLCents()` / `formatBRLCents()`
  (`src/js/10-domain/12-personal-finance.js`). O parser não usa ponto
  flutuante; o formatador fatia o inteiro como string. Parsers espalhados pela
  UI são defeito de revisão.
- `moneyUnit` é **invariante, não preferência**. Unidade inesperada jamais é
  reinterpretada, convertida ou sobrescrita: o agregado permanece intacto e o
  módulo entra em `READ_ONLY_UNSUPPORTED_MONEY_UNIT` (banner
  `#finpesUnitNotice`; guarda `pfWriteBlockReason()`), sem bloquear o restante
  do JP Wealth.
- Campos de **entrada** são `≥ 0 ou null` (a direção é do campo, não do
  sinal). Derivados podem ser negativos (`projectedSurplus`, `realizedSurplus`,
  `unallocatedSurplus`, `available`). `used > totalLimit` é legítimo:
  utilização > 100% gera alerta, nunca clamp.

## Schema v1 (congelado)

```js
personalFinance: {
  schemaVersion: 1,
  moneyUnit: 'BRL_CENTS',
  months: {},          // 'YYYY-MM' → registro mensal; ausente = mês VIRTUAL
  recurringIncome: [], // { id:'pfr_', name, amount, periodicity:'MENSAL',
                       //   startMonth, endMonth:null|'YYYY-MM', active }
  debts: [],           // IDENTIDADE TEMPORAL — { id:'pfd_', creditor, type,
                       //   description, originalAmount, installmentAmount,
                       //   installmentsTotal, startMonth, closedMonth:null|'YYYY-MM' }
                       //   SEM campo status (ATIVA/QUITADA é derivado);
                       //   inexcluível se houver snapshot em qualquer mês
  creditLines: [],     // { id:'pfc_', institution, instrument, type, totalLimit, used }
  scenarios: [],       // { id:'pfs_', name, horizon:null|'YYYY-MM', kind,
                       //   incomes:[{id,name,amount}], expenses:[{id,name,amount}],
                       //   baselineFrom:null|'YYYY-MM', createdAt }
}

// months['YYYY-MM']
{
  createdAt,
  incomes:       [{ id:'pfi_', name, projectedAmount, receivedAmount,
                    status:'PROJETADA'|'RECEBIDA'|'CANCELADA', ruleId:null|'pfr_' }],
  expenses:      [{ id:'pfe_', name, installments:null|{total,paid},
                    targetAmount, expectedAmount, executedCash, executedCard,
                    status:'PENDENTE'|'PAGO'|'CANCELADO' }],
  debtSnapshots: [{ debtId, balance, installmentsPaid|null }],  // máx. 1 por dívida/mês
  allocations:   [{ id:'pfa_', label, amount }],
  notes:         [{ id:'pfn_', text, status:'PENDENTE'|'RESOLVIDO', createdAt }],
}
```

Derivados **nunca** persistem: totais, coberturas, sobras, ratios, disponível,
utilização, rótulo ATIVA/QUITADA, relevância de dívida, patrimônio.

## Contratos centrais

- **Mês virtual ≠ histórico.** Mês ausente de `months` é projeção derivada das
  regras recorrentes; não integra realizado nem Comparativo. O mês nasce no
  **primeiro ato de edição** (materialização) — nunca por cópia do anterior,
  nunca durante render/navegação.
- **Nunca automático, sempre deliberado.** Mês materializado não é reescrito
  por automação alguma (recorrência posterior não o alcança); edição humana
  deliberada é permitida em qualquer época — inclusive resolver pendência de
  mês passado. Não existe "Fechar mês" na V1.
- **Status operacional ≠ completude financeira.** Completude do realizado é
  ancorada em VALOR explícito: receita conhecida ⇔ `receivedAmount !== null`;
  despesa conhecida ⇔ `executedCash !== null` **e** `executedCard !== null`.
  Guardas: RECEBIDA exige recebido explícito; PAGO exige os dois canais
  explícitos (0 válido). Soma parcial jamais se apresenta como total:
  `realizedSurplus` e `incomeExpenseRatio` só existem com cobertura completa.
- **CANCELADO(A) sai do planejado; o realizado permanece.** Fato financeiro não
  se apaga porque a expectativa restante morreu.
- **Dívida: identidade ≠ observação.** A identidade é temporal
  (`startMonth`/`closedMonth`); o saldo vive em `debtSnapshots` do mês.
  Relevância no mês M: `startMonth ≤ M ≤ (closedMonth ?? ∞)`. Estado atual
  jamais reinterpreta o passado. Mês sem snapshot: a dívida não conta naquele
  mês (cobertura parcial explícita) — arrastar saldo antigo seria fabricar
  observação.
- **Cenários não alteram meses reais.** `baselineFrom` copia deliberadamente;
  a escrita é unidirecional.

## Persistência e sobrevivência

- Guarda estrutural de boot: `personalFinanceNormalizeState()`
  (`00-core/04-persistence.js`) — **repara forma, jamais conteúdo**: null não
  vira 0, valor inválido não é "consertado", campo desconhecido atravessa,
  `schemaVersion` futura é preservada. Nunca lança.
- Gravação: mutar `S` → `dgLogChange('personalFinance', …)` → `save()`.
  Rótulos do changeLog são genéricos (ação + recordId), sem valores nem nomes.
- **Finalizar Sessão preserva o agregado integralmente** (herança explícita em
  `emptyJPWealthState()`); memória longitudinal, como as notas. Risco residual:
  versões do app anteriores a PF-01 zeram o agregado nesse fluxo.
- Backup: inclusão automática no envelope normativo; round-trip provado em
  contexto isolado com storage virgem (`tools/finpes_backup_roundtrip_test.py`).
- Fixture sintética canônica: `tools/fixtures/personal_finance_v1.json`.

## Plano e classificação

**V1 entregue e integrada** (todas em `main`, publicadas em `origin/main`):
PF-01 Fundação (N2, merge `59a9681`) → PF-02 Orçamento Mensal (N3, `f6a7ffe`) →
PF-03 Dívidas & Crédito (N3, `73bdaab`) → PF-04 Comparativo (N3, `bc6752a`) →
PF-05 Cenários (**N3**, `46dcbe6`) → PF-06 Visão Geral (N1 condicionado a só
compor valores canônicos; conduzido proceduralmente como N3, `1a13a91`) →
PF-CLOSE-01 fronteira do domínio (`ff4cf3d`).

O domínio tem **cinco destinos**: Visão Geral, Orçamento Mensal, Dívidas &
Crédito, Comparativo Mensal e Cenários.

> [!important] Inventário e Patrimônio não pertencem a Finanças Pessoais
> Até 2026-08-19 este plano encadeava "PF-07 Inventário → PF-08 integrações
> patrimoniais (+ `inventoryAssetRef`, bump 1→2)". Decisão de produto posterior
> retirou Inventário/Patrimônio deste domínio: passam a ser **domínio próprio,
> com roadmap independente `INV-*`**. `PF-07` e `PF-08` não existem. O bump de
> schema 1→2 que estava reservado ao `inventoryAssetRef` fica **sem reserva** —
> qualquer migração futura volta a exigir PARAR, reportar e propor migração
> formal, como manda o congelamento do schema v1. `PF-CLOSE-01` (merge
> `ff4cf3d`) removeu do runtime o submenu, o workspace e os dois placeholders
> que anunciavam esse futuro; a fronteira é protegida por teste.
>
> Resíduo conhecido, ainda não corrigido: o comentário em
> `src/js/10-domain/12-personal-finance.js:493` ("Sem `inventoryAssetRef`:
> adiado para PF-08 por decisão do congelamento") permanece no código. É
> comentário, não contrato executável, e sua correção exige tocar arquivo de
> domínio — fica reservada a gate próprio.

FUTURE (fora da V1, sem data): Cartão & Parcelamentos (então `executedCard`
torna-se derivado e o input congela — uma verdade só); importação histórica do
Excel.
