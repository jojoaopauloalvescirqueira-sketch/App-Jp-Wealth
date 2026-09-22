# CHG-LIQUID-GLASS-NAVIGATION-20260921

## Contrato autorizado

- **Objetivo:** acrescentar `Liquid Glass` como terceira composição de navegação,
  mantendo `Menu lateral` como padrão e preservando `Barra superior`.
- **Classe:** N2, porque `jpw_nav_glass_tint` integra o bloco `workspace` do
  Backup Completo schemaVersion 1.
- **Autoridade:** plano aprovado pelo proprietário em 2026-09-21, incluindo a
  worktree/branch isolada e a implementação. Commit, push, merge, publicação e
  aceite visual continuam gates humanos separados.
- **Base:** `4ba8d61af363f3130518b0dcbf3e6d2ae876bf77` (`main` oficial).
- **Branch/worktree:** `codex/liquid-glass-navigation-20260921` em
  `/Users/joaopauloalves/.codex/liquid-glass-navigation/20260921/product`.

## Escopo permitido

- contratos e montagem da navegação em `index.html`, `src/styles/app.css`,
  `20-ui/12-nav-style.js`, `40-app/11-operational-shell.js` e
  `40-app/12-global-dashboard.js`;
- allowlist e validação de `jpw_nav_glass_tint` em
  `00-core/07-workspace-backup.js`;
- testes focais de layouts/backup e correção do servidor de fixture que causava
  resets sob o carregamento paralelo do Chrome;
- documentação diretamente afetada, manifesto/build e portátil apenas pelo
  gerador oficial.

Ficam excluídos domínio financeiro, fórmulas, rotas, schemas financeiros,
ordem de scripts, dados reais, candidatos de outras worktrees e as 34 mudanças
documentais da árvore principal.

## Invariantes

1. `jpw_nav_layout` aceita somente `sidebar`, `topbar` e `glass`; ausência,
   leitura indisponível ou valor inválido exibem `sidebar` sem escrever.
2. Os três layouts usam os mesmos nós, IDs, rotas, ordem e listeners. Trocar a
   composição não reinicializa módulos nem altera rascunhos ou `S`.
3. `jpw_nav_glass_tint` é string inteira canônica `0..100`; ausência ou valor
   inválido usa 60 sem normalizar o armazenamento. `input` só produz prévia;
   `change` confirma por releitura. Falha restaura a última confirmação.
4. O estilo Kinetic/Pill/Clássico fica apenas indisponível enquanto Glass está
   ativo; `jpw_nav` permanece intacto e volta a valer nas composições antigas.
5. O Glass compacto é não modal: sem backdrop, `inert` no conteúdo, trap de
   foco ou bloqueio de rolagem. Escape, clique externo e destino final fecham o
   painel e aplicam o retorno de foco adequado.
6. `prefers-reduced-transparency`, `prefers-reduced-motion`, alto contraste e
   ausência de `backdrop-filter` recebem fallbacks locais, sem regravar a escolha.
7. Backup Completo mantém `workspace.schemaVersion:1`; backup antigo sem a
   chave preserva a preferência de destino e valor importado inválido é recusado
   antes de qualquer escrita.

## Recuperação

O rollback é remover o valor `glass`/controle visual, retirar a chave da
allowlist e regenerar os artefatos. Nenhuma migração de `S` é necessária. Uma
preferência `glass` aberta por uma versão anterior cai no fallback lateral já
existente e preserva o raw; um backup que contenha a chave deve ser importado em
build que conheça este contrato.

## Baseline do Chrome do sistema

O primeiro focal reproduziu falhas de recurso (`ERR_CONNECTION_RESET`) em
arquivos diferentes. A causa foi o servidor HTTP da fixture com fila curta para
o carregamento paralelo de 94 scripts. `BrowserFixtureServer` amplia somente a
fila e usa threads daemon; as asserções de console, pageerror e requestfailed
continuam integrais. O `src` inicial da marca recebeu o mesmo cache-buster que
`applyAppIconChoice`, eliminando a requisição que o próprio boot cancelava.

## Candidate verificado e congelado

Fotografia final local de 2026-09-22:

- build modular e portátil idênticos: `6739a2a96e21d863`;
- `navigation_layout_choice_test.py --capture`: PASS em preferências, falhas,
  transparência, lifecycle, N1/N2/N3, Notes, portátil e 140 casos visuais em
  1440/1280/1024/390/320 CSS px, temas claro/escuro;
- `complete_backup_test.py`: PASS no round-trip, backup v1 antigo sem a chave,
  rejeição integral do valor inválido, falha parcial e retomada;
- `validate_project.py`: PASS, 94 arquivos JS, 562 IDs estáticos e portátil
  reconstruído pelo gerador oficial;
- `quality_gate.py --tier full`: 57 PASS, 0 falhas de produto, harness,
  ambiente ou baseline; o gate inclui reprodutibilidade do build, atualização
  do service worker e consultas PWA online/offline;
- `git diff --check` e auditoria final de segurança/persistência: PASS.

O teste legado `contextual_sidebar_test.py`, fora do gate completo atual, mantém
duas divergências já presentes no commit-base `4ba8d61`: a geometria Apple01 da
rota ativa não corresponde à expectativa Classic antiga e o cenário lifecycle
retorna os mesmos estados bloqueados no base e neste candidate. O teste e o
comportamento foram preservados, sem flexibilização de asserções.

O candidate está pronto para revisão visual manual. Esta fotografia não declara
commit, push, merge, publicação nem aceite humano.
