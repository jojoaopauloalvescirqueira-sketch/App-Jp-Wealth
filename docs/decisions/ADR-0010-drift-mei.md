# ADR-0010 — Origem do drift nas projeções MEI por perfil

- Data: 2026-08-09
- Status: **PROPOSTO**
- Responsavel pela aprovacao: gestor (A4)
- Nivel: N3
- Fonte normativa relacionada: Memória de cálculo MEI — fonte normativa a confirmar

## Implementação atual

`src/js/30-accounting/03-mei-jp.js:121-202` — `runMEIMonteCarlo()` usa
`riskProfileMonthlyTarget(cal.pr)` como drift: a META mensal do perfil vira
parâmetro estatístico da projeção.

## Divergência

Cenários podem apresentar meta como expectativa, sem memória de cálculo aprovada.
O motor matemático (Box-Muller, correção de Itô, desvio amostral) está correto —
a questão é a ORIGEM do drift e os RÓTULOS de projeção, não a matemática.

## Opções

**A — Drift = média histórica realizada** (com mínimo de amostra e rótulo).
**B — Drift = meta do perfil, com rótulo explícito de "cenário-alvo, não previsão".**
**C — Ambos lado a lado.**

## Evidência ainda necessária

INFORMAÇÃO INSUFICIENTE: não localizei no Estatuto uma memória de cálculo aprovada
para projeções MEI. Sem ela, qualquer escolha é decisão nova do gestor, não
conformidade.

## Recomendação técnica (não autoritativa)

C com rótulos honestos, se o gestor aprovar a memória de cálculo correspondente.

## Decisão do gestor

**PENDENTE**
