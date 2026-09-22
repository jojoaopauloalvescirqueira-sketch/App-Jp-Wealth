# CHG-SUBMENU-SIDEBAR-NAVIGATION-20260922

## Contrato autorizado

- **Objetivo:** acrescentar `Lateral em níveis` como quarta composição de
  navegação, mantendo `Menu lateral` como padrão e preservando `Barra superior`
  e `Liquid Glass`.
- **Classe:** N2, porque a preferência auxiliar `jpw_nav_submenu_rail` integra
  o bloco `workspace` do Backup Completo schemaVersion 1.
- **Autoridade:** plano aprovado pelo proprietário em 2026-09-22. A autorização
  cobre worktree isolada, implementação, testes, documentação e artefatos
  derivados. Commit, push, merge, publicação e aceite visual continuam gates
  separados.
- **Base:** `22bc889c7f0ece4b8b9a7d1b1ddda57d638a34da` (`main` oficial).
- **Branch/worktree:** `codex/submenu-sidebar-navigation-20260922` em
  `/Users/joaopauloalves/.codex/submenu-sidebar-navigation/20260922/product`.

## Escopo e invariantes

1. `jpw_nav_layout` passa a aceitar `sidebar`, `topbar`, `glass` e `submenu`.
   Ausência, leitura indisponível ou valor inválido continua exibindo a lateral
   padrão sem reescrever o raw.
2. Os quatro layouts compartilham nós, IDs, rotas, ordem e listeners. Abrir N2,
   N3 ou voltar na lateral em níveis não navega nem renderiza domínio.
3. A página ativa permanece com `JPWNavigation`; o shell guarda apenas nível,
   grupo, contexto, acionadores de retorno e expansão temporária em RAM.
4. Desktop usa 288 px ou rail de 72 px. `jpw_nav_submenu_rail` aceita somente
   `expanded`/`collapsed`, é independente de `jpw_rail` e confirma gravações por
   releitura. Fallbacks não normalizam armazenamento.
5. Grupo clicado no rail abre temporariamente a lateral sem gravar. Destino
   aceito ou retorno à raiz encerra a expansão; recusa do guard preserva painel,
   foco e trabalho.
6. Até 900 CSS px, `#appSidebar` é gaveta modal com backdrop, isolamento, trap de
   foco, botão Fechar e Safe Areas. Fechar/reabrir na sessão conserva o nível.
7. `jpw_nav_submenu_rail` participa do Backup Completo v1. Backup antigo sem a
   chave preserva o destino; valor importado fora do enum é recusado antes de
   qualquer escrita.
8. Estilo Kinetic/Pill/Clássico fica indisponível apenas durante `glass` ou
   `submenu`, mantendo `jpw_nav` salvo. Transparência continua exclusiva do
   Liquid Glass.

## Escopo excluído

Não há mudança de fórmulas, regras financeiras, rotas, schemas de `S`, ordem de
scripts, dependências, dados reais, Obsidian ou outras worktrees. O HTML portátil
é sempre derivado pelo gerador oficial.

## Baseline e verificação

Na base limpa, `navigation_layout_choice_test.py`, `navigation_order_test.py` e
`complete_backup_test.py` passaram. `contextual_sidebar_test.py` reproduziu sua
falha preexistente de borda visual do item Classic ativo; a asserção não foi
alterada e o candidate reproduziu a mesma falha.

O candidate de produto é o build **`e606146a740126cb`**, gerado pelo
`tools/rebuild_monolith.py`. A validação focal final aprovou:

- os quatro valores de layout, fallbacks e falhas de leitura/escrita;
- 36 alternâncias sem duplicar nós/listeners nem alterar rota, rascunho ou
  leituras financeiras;
- exploração N1/N2/N3, teclado, foco, recusa de guard, rail temporário e gaveta;
- 1440, 1280, 1024, 900, 768, 390 e 320 CSS px, temas claro/escuro, contraste e
  movimento reduzido; 1024 CSS px cobre a geometria equivalente a 200% em um
  viewport de 2048 px, sem alegar sessão de leitor de tela;
- Settings, Notas/Tickets com nível explorado, sincronização de atalho externo,
  ordem personalizada, Backup Completo, estrutura, portátil reprodutível e
  upgrade online/offline do service worker.

Artefatos visuais finais:

- `tools/.artifacts/navigation-layout-choice/submenu-root-1440-light.png`;
- `tools/.artifacts/navigation-layout-choice/submenu-n3-1440-dark.png`;
- `tools/.artifacts/navigation-layout-choice/submenu-drawer-390-light.png`.

O gate completo foi executado três vezes. Os relatórios
`quality-20260922T125445-full.json`, `quality-20260922T131446-full.json` e
`quality-20260922T132709-full.json` terminaram respectivamente em 51/57, 55/57
e 55/57 PASS. Cada falha foi de boot HTTP parcial ou timeout, com símbolos de
scripts posteriores ausentes; os casos mudaram entre as rodadas e todos
passaram quando repetidos isoladamente, sem alteração do candidate. Portanto o
produto está aprovado nos focais e nos 55 checks estáveis, mas não se declara um
gate integral verde neste host. Nenhuma asserção ou timeout foi enfraquecido.

## Agentic impact check

**AGENTIC IMPACT DETECTED.** A mudança altera representações de navegação,
preferências públicas e Backup Completo. Dentro do escopo autorizado, foram
reconciliados `NAVIGATION-HIERARCHY`, `COMPLETE-BACKUP`,
`DB-STORAGE-GOVERNANCE`, `CODE-MAP`, `ACTIVE-TASK` e `CURRENT-STATE`. Não há
mudança em `AGENTS.md`, roteamento de skills, autoridade ou regras financeiras,
schema de `S`, memória operacional ou índices; portanto não é necessária
atualização de índice para este candidate.

## Recuperação

O rollback visual é selecionar outro layout. Um rollback de código preserva a
preferência desconhecida; builds anteriores caem no fallback lateral. Backups
com `jpw_nav_submenu_rail` exigem build que reconheça essa chave.
