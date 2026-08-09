# ADR-0009 — Fator do Stop Raiz-N: 1,8 no código vs 1,25 na norma

- Data: 2026-08-09
- Status: **PROPOSTO**
- Responsavel pela aprovacao: gestor (A4)
- Nivel: N3
- Fonte normativa relacionada: Estatuto p.12 (Stop Estatístico)

## Norma vigente (citação direta, p.12)

> N = horizonte projetado da operação, em candles H4 (padrão: 55)
> F = fator de segurança (**padrão: 1,25 — sujeito a ratificação, Anexo C**)

## Implementação atual

Padrão 1,8 em TRÊS caminhos: `src/js/00-core/03-default-state.js:67`,
`src/js/00-core/04-persistence.js:608`, `src/js/10-domain/04-stop-statistics.js:28-56`.

## Divergência

O stop estatístico recomendado muda materialmente (1,8 → 1,25 estreita o stop
mínimo estatístico). ATENÇÃO: o próprio Estatuto marca 1,25 como "sujeito a
ratificação (Anexo C)" — o gestor precisa declarar se a ratificação ocorreu.

## Opções

**A — Migrar padrão para 1,25** (consolidando em fonte única; valores escolhidos
manualmente pelo operador são preservados). **B — Manter 1,8 até a ratificação do
Anexo C ser confirmada.**

## Evidência ainda necessária

Status do Anexo C — só o gestor pode afirmá-lo.

## Recomendação técnica (não autoritativa)

Nenhuma migração antes da confirmação do Anexo C; preparar a consolidação em fonte
única desde já (os três caminhos duplicados são dívida independente da escolha).

## Decisão do gestor

**PENDENTE**
