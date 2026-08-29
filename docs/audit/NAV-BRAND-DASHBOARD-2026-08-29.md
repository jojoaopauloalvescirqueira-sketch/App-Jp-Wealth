# Auditoria pós-mudança — a marca abre o Dashboard

- Data: 2026-08-29
- Branch de trabalho: `codex/logo-link-dashboard-merge`
- `BASE_SHA`: `c8c31908e2bccbdb3a62e45c1b0ec4f6384cad9b`
- Classificação: **N1** — navegação de interface
- Autoridade: **A2**, com commit e merge por fast-forward autorizados;
  push e deploy **não** autorizados

## O que mudou

| Arquivo | Mudança |
|---|---|
| `index.html` | `.brand` passou de `<div>` a `<button type="button">` com `id`, `data-route`, `aria-label` e `title`; logo decorativa; wordmark fora da árvore a11y |
| `src/styles/app.css` | `.brand-home` neutraliza a aparência de botão do user-agent e acrescenta `cursor:pointer` e 44 px de alvo |
| `src/js/40-app/01-navigation.js` | o seletor de fiação passou a incluir `.brand-home[data-route]` — **uma linha**, sem nova implementação |
| `tools/navigation_ia_test.py` | caracterização do contrato completo |
| `src/js/manifest.json` | sha256 do script de navegação |
| `build-id.js`, `dist/…PORTABLE.html` | regenerados por `tools/rebuild_monolith.py` |

## Invariantes verificados

- rota canônica `dashboard` → tela física `dash`, com `aria-current` no primário;
- clique, Enter e Espaço produzem o mesmo resultado, partindo de `research-others`;
- **zero escrita em storage** — comparação de snapshot antes/depois em cada acionamento;
- alvo de 44 px e `cursor:pointer` em desktop e mobile, temas claro e escuro;
- controle contido no cabeçalho, sem overflow horizontal;
- console e `pageerror` limpos nas quatro combinações;
- aparência da marca inalterada sem foco (fundo transparente, sem borda, `appearance:none`).

## Prova de que o teste acusa

Mutante aplicado: seletor devolvido a `'#nav > .tab[data-route]'`, removendo a
fiação da marca. Resultado: **MORTO** — `[clique] nao chegou a tela fisica dash`,
com o estado permanecendo em `research`. Um teste que passasse com a fiação
removida não estaria protegendo contrato algum.

## Evidência

`validate_project` PASS — 77 scripts, 429 IDs estáticos.
`standard` **37/37**, sem `PRODUCT_FAIL`, `TEST_HARNESS_FAIL`, `ENVIRONMENT_ERROR`,
`BASELINE_FAIL` ou `NOT_RUN`.

Nota de método: uma execução anterior, feita em checkout com trabalho de outra
frente misturado, chegou a 38 verificações. Esse número **não** vale como
evidência deste candidato — o 38 incluía uma suíte alheia a esta mudança. O
número deste candidato limpo é 37.

## Risco residual

Baixo. A superfície é um controle de navegação sem estado; o pior caso de
regressão é a marca deixar de navegar, que é justamente o que o teste de
caracterização passa a impedir.
