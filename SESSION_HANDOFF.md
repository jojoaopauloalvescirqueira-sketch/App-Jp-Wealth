# Session Handoff — NAV-01 · candidato interno de navegação

- Data: 2026-08-25
- Branch: `codex/navigation-ia`
- `BASE_SHA`: `1eddd29ee73d3e8fbc1713e073a0c22ce71350ab`
- Estado: candidato implementado, reconciliado e validado; aguarda decisão humana
- Publicabilidade: **não** — depende de NAV-02
- Git: commit/push/merge/deploy não autorizados nem executados

## Target, candidato e publicação

- **TARGET CANÔNICO:** cinco primários — Dashboard, Forex, Finanças Pessoais,
  Research e Alladin.
- **CANDIDATO NAV-01:** registry/resolver semântico, compatibilidade física e
  placeholders estruturais mínimos.
- **ESTADO PUBLICÁVEL:** somente NAV-01 + NAV-02 é o primeiro ponto
  potencialmente publicável da nova IA.

## Implementação presente

- `window.JPWNavigation` separa rotas canônicas de aliases/compatibilidade.
- `navigateToScreen()` continua aceitando IDs físicos legados.
- o primeiro nível possui cinco botões; Forex conserva o submenu físico `exec`
  e Finanças Pessoais conserva seus cinco destinos.
- Planejamento FX permanece funcional em `#fxplan`/`window.JPWFx.ui`, acessível
  por compatibilidade e sem painel global próprio nesta etapa.
- `section#research` é estática; `section#alladin` usa exatamente a mensagem
  aprovada e não acopla ao domínio Alladin.
- o quality gate inclui `tools/navigation_ia_test.py` no tier standard/full.

## Próxima ação controlada

O candidato usa build `eba48d278c6a5b58`. A suíte NAV-01 e as quatro focais,
`validate_project.py` e o tier full (42/42) passaram; Chromium real cobriu
desktop/mobile, claro/escuro, foco/teclado e overflow. O CSS condicional foi
necessário após o teste medir alvos móveis de 40 px; o resultado mede 44 px.
O blast radius final é de 26 arquivos.

Emitir o `NAV-01 — CANDIDATE REPORT` e parar. NAV-01 permanece não publicável
isoladamente; não iniciar NAV-02 sem nova autorização humana.
