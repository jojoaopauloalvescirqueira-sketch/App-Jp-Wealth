# ADR-0006 — Gatilho compulsório de poda LIFO (+1,00pp)

- Data: 2026-08-09
- Status: **PROPOSTO**
- Responsavel pela aprovacao: gestor (A4)
- Nivel: N3
- Fonte normativa relacionada: Estatuto, Protocolo de Desalavancagem Tática (p.7-8) — parágrafo exato a confirmar

## Implementação atual

`src/js/10-domain/02-risk-calculations.js:58-67` — existe sugestão textual de poda
quando já há excesso; não existe o EVENTO compulsório de +1,00pp com ordem de poda,
idempotência e registro de auditoria.

## Divergência

Redução obrigatória depende de ação discricionária tardia do operador.

## Opções

**A — Evento automático de recomendação vinculante** (alerta bloqueante com registro
LIFO calculado; execução continua manual — o app não opera contas).
**B — Alerta simples não bloqueante.**

## Evidência ainda necessária

INFORMAÇÃO INSUFICIENTE: preciso da redação exata do gatilho de +1,00pp no
Protocolo antes de desenhar o evento (li o §3º da histerese; o parágrafo do gatilho
compulsório precisa ser citado por extenso na aprovação).

## Recomendação técnica (não autoritativa)

Opção A após citação confirmada, com dependência de ADR-0001 para a régua do DD.

## Decisão do gestor

**PENDENTE**
