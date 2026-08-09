# ADR-0005 — Histerese de retorno de fase (0,50pp + candle H4)

- Data: 2026-08-09
- Status: **PROPOSTO**
- Responsavel pela aprovacao: gestor (A4)
- Nivel: N3
- Fonte normativa relacionada: Estatuto p.7 §3º

## Norma vigente (citação direta, p.7 §3º)

> O retorno a uma fase menos restritiva somente ocorre quando o DD recuar para
> valor inferior ao limite da fase em pelo menos **0,50 ponto percentual**,
> sustentado pelo fechamento de ao menos **1 candle H4 completo**. A poda LIFO
> executada não é revertida.

## Implementação atual

`src/js/10-domain/03-phase-transitions.js:162-177` — basta a matemática indicar
fase inferior e as superiores estarem vazias; sem margem de 0,50pp, sem H4.

## Divergência

Oscilação de fronteira pode devolver fase menos restritiva imediatamente.

## Dependência

**Bloqueado por ADR-0001**: histerese sobre um DD cuja fonte não é canônica
apenas formaliza o erro. Decidir equity primeiro.

## Opções

**A — Implementar 0,50pp + confirmação H4 manual** (operador registra o candle).
**B — Implementar só a margem 0,50pp** e deixar H4 como rito documental.

## Recomendação técnica (não autoritativa)

Sequenciar após ADR-0001; então Opção A.

## Decisão do gestor

**PENDENTE**
