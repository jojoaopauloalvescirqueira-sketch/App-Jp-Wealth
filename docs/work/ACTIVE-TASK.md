# Tarefa ativa — Integração seletiva de branches pendentes

- Data: 2026-09-05
- Branch: `codex/integrate-pending-branches`
- `BASE_SHA`: `c9104b167944e52bb9b71a7439f1573a053704bb`
- Classificação: **N1 + N0-D** — Dashboard Macro e workflow de qualidade
- Autoridade: **A4 delimitada** — integração e commits locais autorizados pelo gestor; `push`, merge em `main`, deploy e exclusão de branches não autorizados.

## Objetivo

Integrar seletivamente os commits pendentes `3502331` e `03eda18` do Dashboard
Macro e `045c264` do workflow de qualidade, reconciliando-os com a `main` atual.

## Exclusões

- Não integrar `b2e43e8` (`chore/norma-vigente-v11`), pois altera o acervo normativo N3.
- Não integrar `feature/personal-finance-overview`, pois foi substituída pela implementação v2 já incorporada.
- Não alterar domínio financeiro, persistência, schema, credenciais ou dados reais.
- Não executar `push`, merge em `main`, deploy ou exclusão de branches/worktrees.

## Arquivos permitidos

Arquivos tocados pelos três commits autorizados, mais os artefatos gerados pelo
gerador oficial e a documentação operacional necessária para reconciliar o estado.

## Invariantes

- Nenhuma regra financeira, percentual, fórmula ou limite muda.
- Alladin e Finanças Pessoais permanecem funcional e estruturalmente intactos.
- A ordem de scripts clássicos só muda conforme o módulo Dashboard Macro autorizado.
- `dist/` e `build-id.js` são atualizados apenas pelo gerador oficial.
- O workflow não pode classificar caso omitido como `PASS`.

## Verificação

- Teste focal do Dashboard Macro.
- `python3 tools/quality_gate.py --tier full`.
- Revisão integral do diff, `git diff --check`, manifest e artefatos gerados.
- Auditoria pós-mudança e reconciliação do impacto agêntico/contextual.

## Rollback

Reverter os commits de integração na ordem inversa. A `main` permanece intocada
até autorização humana separada para o merge.
