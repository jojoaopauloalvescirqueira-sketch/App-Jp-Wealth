# Tarefa ativa — NAV-01 · Semantic Route Foundation

- Data de abertura: 2026-08-25
- `BASE_SHA`: `1eddd29ee73d3e8fbc1713e073a0c22ce71350ab`
- Branch: `codex/navigation-ia`
- Worktree: `JP Wealth OS Navigation IA`
- Classificação: **N1**
- Autoridade: **A2**, implementação delimitada aprovada
- Estado: candidato validado; aguarda decisão humana e não é publicável isoladamente
- Git/publicação: **commit, push, merge e deploy não autorizados**

## Contrato congelado

**TARGET CANÔNICO:** Dashboard, Forex, Finanças Pessoais, Research e Alladin.

**CANDIDATO NAV-01:** `JPWNavigation.routes()` retorna exatamente essas cinco
rotas; `resolve()` aceita também aliases e targets físicos de compatibilidade.
`navigateToScreen()` permanece a fachada legada. O primário possui cinco botões,
sem `section#forex`; apenas `section#research` e `section#alladin` são criadas.

**ESTADO PUBLICÁVEL:** depende de NAV-02. Contas, Contabilidade e Planejamento
saem do primeiro nível antes de receberem seus destinos definitivos em Forex.

## Invariantes

- alvo inválido é recusado antes de trocar tela, primário, visão local, foco ou storage;
- navegação não cria chave nem escreve em storage/S;
- IDs físicos e superfícies funcionais existentes permanecem compatíveis;
- Alladin mostra somente a mensagem aprovada, sem valor, card ou zero econômico;
- navegação Alladin não lê/chama/muta `S.alladin` ou `JPWAlladin`;
- nenhuma regra financeira, schema, migração, fórmula ou persistência muda;
- `src/styles/app.css` só pode entrar se defeito visual real for provado;
- o worktree Alladin original não pode sofrer drift.

## Blast radius autorizado

25 arquivos fixos: quatro de produto, seis testes, manifest, doze documentos e
dois gerados. `src/styles/app.css` é o 26º apenas sob evidência visual. Qualquer
27º arquivo exige parada e nova autorização.

## Verificação concluída

- rebuild oficial: `eba48d278c6a5b58`;
- suíte NAV-01 e quatro focais: PASS;
- `validate_project.py`: PASS, 75 scripts e 409 IDs;
- tier full: **42/42 PASS**, zero falhas ou verificações omitidas;
- Chromium real: desktop/mobile a 390 px, claro/escuro, foco/teclado e zero
  overflow horizontal;
- condição CSS comprovada: alvos móveis mediam 40 px; após o 26º arquivo
  autorizado, os cinco primários medem 44 px.

Emitir o Candidate Report e **parar sem iniciar NAV-02**.
