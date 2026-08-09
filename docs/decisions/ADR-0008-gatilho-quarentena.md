# ADR-0008 — Gatilho autoritativo de quarentena/guilhotina

- Data: 2026-08-09
- Status: **PROPOSTO**
- Responsavel pela aprovacao: gestor (A4)
- Nivel: N3
- Fonte normativa relacionada: Estatuto, Art. 3.10 e correlatos (quarentena aparece nas p.10, 14-18)

## Implementação atual

`src/js/10-domain/01-risk-instruments.js:176-178` — `quarantineActive()` só
verifica datas já formalizadas manualmente em `S.quarantine`.

## Divergência

A quarentena depende de o operador formalizar o evento; não deriva da condição
autoritativa (MDD real atingido).

## Dependência

**Bloqueado por ADR-0001** — o disparo automático pressupõe uma fonte de equity/DD
oficial. Sem ela, qualquer gatilho automático dispararia sobre o proxy.

## Opções

**A — Disparo automático sobre a fonte canônica** (pós-ADR-0001, com persistência
idempotente). **B — Manter formalização manual + alerta vinculante quando o proxy
cruzar o limite.**

## Recomendação técnica (não autoritativa)

B imediatamente (alerta), A quando ADR-0001 definir a régua.

## Decisão do gestor

**PENDENTE**
