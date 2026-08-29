# Tarefa ativa — Logo JP Wealth como acesso ao Dashboard

- Data: 2026-08-29
- Branch: `codex/logo-link-dashboard-merge`
- Worktree: `/private/tmp/jpw-logo-merge.Y5Ip0p/repo` (temporário, limpo)
- `BASE_SHA`: `c8c31908e2bccbdb3a62e45c1b0ec4f6384cad9b`
- Classificação: **N1** — navegação de interface, sem regra financeira nem persistência
- Autoridade: **A2** — implementação delimitada, autorizada pelo gestor;
  commit e merge por fast-forward autorizados. **Push e deploy NÃO autorizados.**

## Objetivo

A logo do cabeçalho passa a ser o caminho de volta ao Dashboard — o gesto que
todo usuário de aplicação web já espera do canto superior esquerdo. Deve
funcionar por clique e por teclado, com nome acessível explícito.

## Exclusões

Nenhuma alteração de estado, storage ou persistência. Nenhuma segunda
implementação de navegação: o mesmo `navigateToScreen()` dos primários. Nenhuma
mudança visual na aparência atual da marca. Nada do domínio Alladin/ledger.

## Arquivos permitidos

`index.html` · `src/styles/app.css` · `src/js/40-app/01-navigation.js` ·
`tools/navigation_ia_test.py` · `src/js/manifest.json` ·
`docs/architecture/NAVIGATION-HIERARCHY.md` · `docs/work/ACTIVE-TASK.md` ·
`CHANGELOG.md` · `docs/audit/` · artefatos regenerados pelo gerador oficial
(`build-id.js`, `dist/…PORTABLE.html`).

## Invariantes

- a rota canônica é `dashboard`; a tela física de destino é `dash`;
- navegação continua sendo UI pura: zero escrita em storage, zero `save()`;
- a aparência da marca não muda — o botão não pode parecer um botão;
- alvo de toque com no mínimo 44 px de altura;
- o foco visível vem do sistema de estilos existente, não de regra nova;
- a ordem dos scripts clássicos não muda.

## Testes

`tools/navigation_ia_test.py` ganha caracterização do novo controle; tier
`standard` no candidato isolado; `validate_project`; verificação real em
navegador (desktop e mobile, tema claro e escuro, foco, overflow, console);
`fast` no candidato final.

## Rollback

Um único commit funcional; reverter é `git revert` dele. O worktree temporário
é descartável e o checkout original, com trabalho não commitado de terceiros,
não é tocado.
