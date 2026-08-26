# Tarefa ativa — NAV-06A · Documentation Reconciliation

- Data de abertura: 2026-08-26
- `BASE_SHA`: `2c1e0a441d77e01c8c9acaf0506da333254c8196`
- Branch: `codex/navigation-ia`
- Worktree: `JP Wealth OS Navigation IA`
- Classificação: **N0-D**, documentação e governança sem mudança de runtime
- Autoridade: **A2**, reconciliação delimitada aprovada
- Estado: candidato NAV-06A reconciliado; aguarda gate humano de commit
- Git/publicação: NAV-01/02/03 commitados; commit NAV-06A, push, merge e deploy
  **não autorizados**

## Objetivo

Reconciliar o contexto operacional com o Git real após os três checkpoints da
migração de navegação:

1. NAV-01: `e2c34bb4c4ac0c0f7a2746ca4687c6a61f64f06d` — commitado;
2. NAV-02: `9b5ea298953b3c8bb270864151a88e5c69419e61` — commitado;
3. NAV-03: `2c1e0a441d77e01c8c9acaf0506da333254c8196` — commitado.

`main` local e `origin/main` permanecem em
`1eddd29ee73d3e8fbc1713e073a0c22ce71350ab`; Navigation está três commits à
frente e zero atrás. Merge, push e deploy não foram executados nem autorizados.

## Escopo autorizado — exatamente quatro arquivos

1. `SESSION_HANDOFF.md`;
2. este `docs/work/ACTIVE-TASK.md`;
3. `docs/governance/CURRENT-STATE.md`;
4. `CHANGELOG.md`.

Qualquer quinto arquivo exige parada e nova autorização.

## Exclusões e invariantes

- nenhum byte de runtime, HTML, CSS, JavaScript, manifest, worker, teste, gate,
  build ID ou portátil muda;
- nenhuma regra financeira, schema, storage, persistência ou dado muda;
- Dashboard, Forex, Finanças Pessoais, Research e o placeholder Alladin mantêm
  o estado validado no commit `2c1e0a4`;
- Galton permanece em Configurações;
- o desenvolvimento funcional Alladin permanece pausado e seu worktree não é tocado;
- o histórico factual não é reescrito: somente afirmações operacionais presentes
  são alinhadas ao Git atual.

## Verificação do candidato documental

- `git diff --check`;
- exatamente quatro arquivos alterados e nenhum quinto;
- revisão integral do diff, exclusivamente factual/documental;
- busca por afirmações obsoletas de commit pendente ou não executado nos
  checkpoints NAV-01/02/03;
- nenhuma afirmação de merge, push ou deploy executado;
- Alladin em `1eddd29e`, com 12 modificados e três não rastreados, sem drift.

O full **43/43 PASS**, browser e PWA do commit `2c1e0a4` permanecem válidos:
nenhum input de produto, teste, manifest, worker, build ou gerado foi alterado.

## Rollback

Antes de commit, rollback é a reversão manual e delimitada somente das edições
documentais NAV-06A, preservando o commit `2c1e0a4` e qualquer trabalho externo.
Não usar `reset`, `clean`, `stash` ou reescrita de histórico. Commit, merge,
push e deploy seguem gates humanos separados.
