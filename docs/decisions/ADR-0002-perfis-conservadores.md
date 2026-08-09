# ADR-0002 — Fatores dos perfis conservadores (53/40/27 vs 66/50/33)

- Data: 2026-08-09
- Status: **PROPOSTO**
- Responsavel pela aprovacao: gestor (A4)
- Nivel: N3
- Fonte normativa relacionada: Estatuto p.14 (tabela de fatores)

## Norma vigente (citação direta, p.14)

> Longevity 53% (revogado 66%) · High Longevity 40% (rev. 50%) · High Longevity Plus 27% (rev. 33%)
> DDR-alvo 8,0/6,0/4,0% · DD no cenário 15%: 7,95/6,00/4,05% · Alav./ordem 0,21x/0,16x/0,11x
> "Os fatores anteriores (66/50/33%) foram calibrados sobre o DDR de 12% da V8.0."
> Tetos de participação: **proposta em ratificação (Anexo C)**.

## Implementação atual

`src/js/00-core/01-risk-profiles.js:4-8` usa os fatores REVOGADOS 0,66/0,50/0,33
(MDD 9,90/7,50/4,95; alav. 0,26/0,20/0,13).

## Divergência

Todos os limites derivados por perfil conservador estão mais permissivos que a
tabela vigente. É a divergência de maior impacto direto em risco.

## Opções

**A — Migrar para 53/40/27** conforme p.14, com migração que preserva a ESCOLHA
nominal de perfil salva (o rótulo, não os números) e testes de todas as derivações.
**B — Manter 66/50/33** exige ato formal do gestor revalidando a tabela revogada.

## Evidência ainda necessária

Confirmar com o gestor o status do Anexo C (tetos "em ratificação" NÃO travam os
fatores, que o texto dá como vigentes — mas a confirmação é do gestor, não minha).

## Recomendação técnica (não autoritativa)

Opção A. A tabela nova consta como vigente no corpo do Estatuto.

## Decisão do gestor

**PENDENTE**
