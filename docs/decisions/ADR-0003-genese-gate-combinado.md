# ADR-0003 — Ordem Gênese: gate combinado de risco e alavancagem

- Data: 2026-08-09
- Status: **PROPOSTO**
- Responsavel pela aprovacao: gestor (A4)
- Nivel: N3
- Fonte normativa relacionada: Estatuto, Títulos 8–9 (estrutura escalonada) — artigo exato a confirmar

## Implementação atual

`src/js/10-domain/03-phase-transitions.js:289-316` — `checkPhaseCap()` bloqueia o
risco financeiro da Gênese, mas não avalia o teto de alavancagem/nocional da mesma
ordem no mesmo ato.

## Divergência

Uma ordem pode respeitar o risco em $ e violar a exposição máxima por alavancagem.

## Opções

**A — Gate atômico**: um único veto que avalia ambos os tetos sobre o saldo inicial
antes de aceitar a ordem. **B — Gate sequencial documentado** (risco primeiro,
alavancagem como aviso).

## Evidência ainda necessária

INFORMAÇÃO INSUFICIENTE sobre o texto exato do artigo que combina os tetos —
localizar no Estatuto a redação da restrição conjunta antes de aprovar.

## Recomendação técnica (não autoritativa)

Opção A, pendente da citação exata.

## Decisão do gestor

**PENDENTE**
