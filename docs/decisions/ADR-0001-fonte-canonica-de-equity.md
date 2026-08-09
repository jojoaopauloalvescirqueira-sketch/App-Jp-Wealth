# ADR-0001 — Fonte canônica de equity para o drawdown operacional

- Data: 2026-08-09
- Status: **PROPOSTO**
- Responsavel pela aprovacao: gestor (A4)
- Nivel: N3
- Fonte normativa relacionada: Estatuto Unificado, Título de Risco — fórmula DDC (p.7)

## Contexto

O drawdown rege a Matriz Quadrifásica, a histerese de retorno, a guilhotina e a
quarentena. A fonte do valor de equity determina todos esses gatilhos.

## Norma vigente (citação direta, Estatuto p.7)

> DD(t) = max( 0 ; ( Saldo_Inicial_Ciclo − Equity(t) ) / Saldo_Inicial_Ciclo )
> Equity(t) = patrimônio flutuante da conta (saldo + resultado aberto), **tick a tick**
> §1º — O DD é medido sobre **equity flutuante, em base contínua**, tendo como
> referência exclusiva o Saldo Inicial do Ciclo (regime DDC).

## Implementação atual

`src/js/10-domain/02-risk-calculations.js:2-35` — `ddDollar` = soma de risco
programado das ordens abertas + perdas realizadas. Não existe leitura de equity
flutuante: uma queda de patrimônio sem ordens registradas não altera o DD.

## Divergência

A norma exige equity tick a tick; o app é manual e não tem feed de conta. O código
usa um *proxy* (risco programado + perdas), que pode subestimar ou superestimar o
DD real — fase, alarmes e guilhotina podem divergir da perda patrimonial efetiva.

## Opções

**A — Proxy declarado (formalizar o status quo).** O DD programático é adotado como
medida operacional oficial DENTRO do terminal, com rótulo explícito de proxy; a
verificação tick a tick permanece responsabilidade do operador na plataforma.
Impacto: nenhuma mudança de código além de rotulagem; a divergência com a letra da
norma é aceita e documentada. Risco: gatilhos automáticos continuam cegos a gaps.

**B — Equity manual como fonte oficial.** Novo campo de equity corrente informado
pelo operador (com carimbo de hora e obrigatoriedade de atualização em janelas
definidas); DD passa a usar `max(proxy, equity informada)`. Impacto: mudança N3 em
`02-risk-calculations` + N2 de schema; cadência e contingência precisam de regra.
Risco: dado manual atrasado vira falso conforto.

**C — Feed automático (futuro MT5/bridge).** Equity real importada de integração
externa. Impacto: depende de arquitetura inexistente (ver política de segredos em
`docs/architecture/DB-STORAGE-GOVERNANCE.md`); não disponível neste ciclo.

## Impacto em cascata

- DD/fases: ADR-0005 (histerese) e ADR-0008 (quarentena) dependem DESTA decisão.
- Dashboards: rótulo do DD muda conforme a opção.
- Testes: exemplos estatutários de fronteira precisam ser calculados após a escolha.
- Backups: opção B adiciona campos; A e C não alteram schema local imediato.

## Riscos

Decidir B sem disciplina de atualização cria ilusão de precisão; manter A sem
rótulo perpetua a ambiguidade atual, que é o pior estado.

## Recomendação técnica (não autoritativa)

Opção A imediatamente (rotular o proxy) + trilha para C quando houver integração,
tratando B como intermediário opcional se o gestor exigir equity manual.

## Decisão do gestor

**PENDENTE**
