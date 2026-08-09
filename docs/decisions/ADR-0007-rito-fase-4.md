# ADR-0007 — Rito de salvaguarda da Fase 4

- Data: 2026-08-09
- Status: **PROPOSTO**
- Responsavel pela aprovacao: gestor (A4)
- Nivel: N3
- Fonte normativa relacionada: Estatuto, artigos da Fase 4 — redação a confirmar

## Implementação atual

`src/js/10-domain/03-phase-transitions.js:289-316` + grade ativa — o gate confere
teto por ordem/consolidado, mas não modela pedido formal, veto, executor distinto
e unicidade da defesa.

## Divergência

Exposição nova pode entrar na fase mais crítica sem o rito completo.

## Opções

**A — Modelar o rito como máquina de estados auditável** (pedido → veto/aprovação →
execução única) antes de liberar escrita. **B — Checklist bloqueante simples.**

## Evidência ainda necessária

INFORMAÇÃO INSUFICIENTE: transcrever os passos do rito diretamente do Estatuto.
O desenho depende de quem assina cada papel no organograma real.

## Recomendação técnica (não autoritativa)

Não iniciar código antes de o gestor validar o fluxo de papéis.

## Decisão do gestor

**PENDENTE**
