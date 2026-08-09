# ADR-0004 — Stop abaixo de 2 ATR: bloquear ou exigir ciência formal

- Data: 2026-08-09
- Status: **PROPOSTO**
- Responsavel pela aprovacao: gestor (A4)
- Nivel: N3
- Fonte normativa relacionada: Estatuto p.12 (Estrutura de Vulnerabilidade Elevada)

## Norma vigente (citação direta, p.12)

> §1º — Se o Stop Técnico for inferior ao Stop Estatístico, a operação é
> classificada como **Estrutura de Vulnerabilidade Elevada**, e todas as decisões
> de gestão priorizarão redução de risco.

## Implementação atual

`src/js/10-domain/04-stop-statistics.js:15-23` — `atrStrat()` devolve o rótulo;
nenhum veto nem rito de ciência formal na gravação da ordem.

## Divergência

A norma manda "priorizar redução de risco" — não diz explicitamente "bloquear".
Classificar sem nenhuma consequência operacional, porém, torna a cláusula inócua.

## Opções

**A — Veto duro** abaixo do limiar. **B — Ciência formal** (confirmação explícita
registrada em changeLog, ordem marcada). **C — Status quo rotulado**.

## Evidência ainda necessária

Definição do gestor sobre o que "priorizarão redução de risco" exige na prática.
Testar fronteiras 1x, 2x, 3,5x, 5x e 7x ATR após a decisão.

## Recomendação técnica (não autoritativa)

Opção B — preserva agência do operador e cria trilha auditável.

## Decisão do gestor

**PENDENTE**
