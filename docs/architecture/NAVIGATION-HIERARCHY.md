# Navegação hierárquica — contrato de implementação

Este documento registra o padrão reutilizável aprovado para módulos que venham
a possuir níveis contextuais de navegação no JP Wealth. Ele descreve arquitetura
de interface, não autoriza automaticamente aplicar submenus a outros módulos.
Cada nova adoção continua exigindo tarefa e aprovação próprias.

## Estado da migração NAV-03

- **TARGET CANÔNICO:** cinco primários — Dashboard, Forex, Finanças Pessoais,
  Research e Alladin.
- **CHECKPOINT NAV-02:** `routes()` mantém exatamente os cinco primários e
  `children('forex')` contém, nesta ordem, `forex-overview`,
  `forex-preparation`, `forex-account`, `forex-operation`,
  `forex-reconciliation` e `forex-planning`.
- **CANDIDATO NAV-03:** `children('research')` contém, nesta ordem,
  `research-forex`, `research-stocks-br`, `research-stocks-global`,
  `research-reits` e `research-others`. Research/Forex contém somente
  Calendário, NoCoda e Pivots no N3; os três aliases históricos ativam esse
  owner. É o primeiro candidato potencialmente publicável, ainda sem gate de
  integração ou publicação.

Adotam a faixa contextual: **Forex** (seis filhos sobre `exec`, `check`,
`contas`, `contab` e `fxplan`) e **Finanças Pessoais** (`finpes`, cinco destinos — Visão Geral, Orçamento Mensal,
Dívidas & Crédito, Comparativo Mensal e Cenários —, superfície `window.JPWFin.ui`,
teste `tools/finpes_navigation_test.py`), além de **Research** (cinco filhos;
Forex com três destinos contextuais e superfície `window.JPWResearch.ui`).
Operação, Apuração e Planejamento
ganham terceiro nível dentro do mesmo `#execNavSubmenu`; `#fxplan` continua
físico e usa `window.JPWFx.ui`.

## Estrutura canônica

O primeiro nível representa módulos globais e permanece em `#nav`. Seu botão
real continua filho direto de `#nav`, sem wrapper, porque os estilos Classic,
Pill e Kinetic medem a geometria desses botões.

O segundo nível não é dropdown, popup, modal nem card flutuante. Ele deve:

1. existir fora de `#nav`, em uma faixa estrutural própria;
2. ficar imediatamente abaixo do header global;
3. participar do fluxo normal da página;
4. deslocar a faixa de contexto e `#appMain` ao expandir;
5. não usar posicionamento absoluto, overlay ou sombra elevada.

A ordem DOM é:

```text
header
#navSubShell
#gdContextRow
#appMain
```

## Faixa única compartilhada

Existe **uma só** faixa (`#navSubShell`), e ela hospeda o `<nav>` de cada
módulo. Só um módulo fica aberto por vez — selecionar outro módulo global é
clique externo e fecha o anterior —, então um único slot `navsub` no grid do
`<body>` é suficiente.

Duplicar o mecanismo por módulo foi avaliado e rejeitado: exigiria um segundo
slot no grid e um segundo par de atributos de raiz, e o estado de "aberto"
gravado no `<html>` acendia todos os acionadores de uma vez. O módulo aberto é
distinguido por `aria-expanded="true"` no próprio acionador, que já é a
verdade acessível.

Convenção de nomes, lida por derivação e não por registro manual:

| Elemento | Id |
|---|---|
| acionador em `#nav` | `<data-nav-surface>NavTrigger`, classe `.tab.nav-sub-trigger` |
| painel do módulo | `<data-nav-surface>NavSubmenu`, classe `.nav-sub-menu` |
| filho canônico Forex | `[data-nav-item][data-nav-child="<route>"]` |
| destino local contextual | `[data-nav-item][data-nav-local-surface][data-nav-local-view]` |
| item local legado de módulo | `[data-nav-sub-view="<chave>"]` |

As colunas de cada nível derivam da contagem de itens (`grid-auto-flow:column`).
Grupos de terceiro nível usam `data-nav-context="<child>"` e só o grupo do
filho corrente fica visível e fora de `inert`.

Um módulo novo precisa de: o par de ids acima, o `<nav>` dentro de
`#navSubShell`, e uma entrada em `NAV_SUBMENU_SURFACES`
(`40-app/11-operational-shell.js`) apontando para sua superfície de UI. Nenhum
id, classe ou atributo do controlador é específico de módulo.

## Modelo de interação

Há dois estados de abertura, mantidos somente na camada de UI:

- **transitório:** hover com ponteiro fino abre; sair completamente de `#nav` e
  da faixa agenda fechamento com tolerância de 400 ms;
- **fixado:** clique, Enter ou Espaço no acionador abre e fixa a faixa. Enquanto
  fixada, `pointerleave`, resize e novo clique no acionador não fecham.

O estado fixado fecha por:

- clique fora do acionador e da faixa;
- seleção de outro módulo global, que é um clique externo;
- Escape, preservado como saída acessível com devolução de foco.

Clicar em um filho canônico navega pelo resolver; item local chama
`JPWNavigation.navigateLocal()`. Ambos mantêm a faixa aberta. O
estado é efêmero: não entra em `S`, `localStorage`, backup, schema ou migração.
`aria-expanded`, `aria-hidden`, `inert`, roving `tabindex` e `aria-current`
devem refletir a realidade visual.

## Animação e composição visual

A faixa abre com `grid-template-rows: 0fr → 1fr`, conteúdo interno recortado e
transições leves de opacidade/posição. A duração de referência é 300 ms, usando
`--jp-ease`; `prefers-reduced-motion` remove as transições.

O fundo deve constituir um terceiro tom do sistema, distinto tanto do header
quanto da faixa de contexto. A fórmula aprovada combina tokens existentes:

```css
--nav-sub-surface:
  color-mix(in srgb, var(--jp-surface) 30%, var(--gd-surface-subtle));
```

Assim o contraste acompanha os temas claro e escuro sem introduzir uma cor
isolada. A faixa usa divisor discreto, sem borda de card ou sombra pesada.

## Navegação interna e fonte única

Os níveis contextuais chamam os mecanismos visuais existentes. Não se cria
estado paralelo: primary/child/screen/local view vêm de `JPWNavigation.current()`
e a visão efetiva das superfícies `window.JPWExec.ui`, `window.JPWFx.ui`,
`window.JPWFin.ui` e `window.JPWResearch.ui`. Operação usa `panel`/`motor`; Apuração combina `#contab` e
`exec/history`; Planejamento usa `overview`/`planning`/`actuals`/`table`.

Quando a faixa superior substitui tabs equivalentes no conteúdo, essas tabs
devem ser removidas para existir uma única fonte visível de navegação. Conteúdo,
renderizadores e lógica de domínio permanecem intactos.

## Workspaces dentro do módulo

Quando o segundo nível troca **áreas do módulo** (e não apenas a visão de um
renderizador), cada área é um filho direto da `section.screen` do módulo,
alternado por `hidden` + `inert`. Três restrições são estruturais, não
estilísticas — cada uma corresponde a uma quebra real observada no código:

1. **Nunca uma `.screen` aninhada.** `01-navigation.js` limpa `.active` de toda
   `.screen` do documento, e `13-dashboard-layout.js`, `10-dashboard-immersive.js`
   e `14-mvp-notes.js` resolvem `.screen.active` / `closest('.screen')` pelo
   primeiro nó em ordem de documento. Uma sub-`.screen` faz os três apontarem
   para o nó errado.
2. **Nunca dentro de uma `.jp-widget-grid`.** O motor de layout reparenteia
   todo `[data-layout-card]` para filho direto da grade a cada boot e lê apenas
   `:scope > [data-layout-card]`. Um wrapper ali é desfeito em silêncio e
   invalida a preferência de layout gravada daquela tela — o que transforma uma
   mudança visual em mudança N2.
3. **Nunca desmontar.** A troca é de visibilidade, não de DOM. Isso preserva
   valores digitados e ainda não confirmados, foco, disclosures abertos e o
   conteúdo que renderizadores injetam por `innerHTML`.

O `[hidden]` precisa de uma regra de especificidade de ID
(`#exec > [hidden]{display:none}`): as regras de `.jp-widget-grid` declaram
`display` e venceriam o estilo de agente de usuário.

**Montagem sob demanda.** Um workspace cujo conteúdo depende de estado vivo —
em Research, Estudos NoCoda e Estudos dos Pivots derivam seus seletores do catálogo de
instrumentos, e o Histórico lê `operationHistory` — declara um renderizador na
superfície que o possui (`RESEARCH_VIEW_RENDERERS` ou `EXEC_VIEW_RENDERERS`) e é
repintado a cada entrada, para que uma mudança feita em outra tela apareça sem
recarregar a página. A montagem vem **depois** de tirar o `hidden`: renderizar num container
oculto impediria qualquer medida e deixaria o foco em nó invisível.

**Repintura parcial dentro do workspace.** O renderizador de entrada monta a
tela; a partir dali, filtro, busca e seleção reescrevem **apenas** a região de
resultados, nunca os controles. O Histórico é o caso que estabeleceu a regra:
reescrever o cartão inteiro a cada tecla destruía o próprio `<input>` de busca —
o texto sobrevivia, porque era reimpresso do estado, mas o foco e a posição do
cursor iam junto com o nó, e o operador precisava clicar no campo de novo a cada
caractere. Duas consequências estruturais: a região repintada precisa incluir
tudo que depende da consulta (as estatísticas junto da tabela, senão os
denominadores ficam do conjunto anterior), e os ouvintes das linhas — que são
recriadas — precisam ser refeitos, enquanto os dos controles não, porque eles
sobrevivem e receberiam ouvinte duplicado a cada tecla.

Repintar não pode descartar trabalho do operador. O estado efêmero de cada
workspace (seleção, filtros, formulário aberto, rascunho não salvo) vive em
variáveis de módulo, e o render o reconstitui — sair do workspace com um
formulário preenchido e voltar devolve o formulário como estava. Descarte só
acontece por ação que troque o objeto em foco, e aí é confirmado.

**Destino inicial.** Quando o módulo define uma área de entrada, ela é aplicada
ao entrar no módulo vindo de outra tela. A detecção observa a classe `.active`
da própria `section` por `MutationObserver` — não embrulha `navigateToScreen`,
que já carrega duas camadas de wrapper. Reabrir a faixa estando já no módulo
não conta como entrada nova, porque a remoção e a recolocação de `.active`
ocorrem no mesmo bloco síncrono e chegam juntas em um único callback.

## Mobile

Hover nunca é requisito. O toque no módulo fecha a gaveta global e abre a faixa
contextual no fluxo vertical. Os itens podem empilhar, mas a faixa continua sem
overlay e sem sidebar. Um segundo toque no acionador não fecha a faixa fixada;
o usuário fecha tocando fora ou usando Escape em teclado conectado.

## Responsabilidades por arquivo

- `index.html`: acionadores globais e estrutura semântica da faixa compartilhada;
- `src/styles/app.css`: grid estrutural, animação, terceiro tom e responsividade;
- `src/js/40-app/01-navigation.js`: registry de primários/filhos, defaults,
  compatibilidade e estado semântico corrente;
- `src/js/40-app/11-operational-shell.js`: abertura transitória/fixada, foco,
  fechamento e projeção dos níveis 2/3 a partir do resolver;
- script de UI do módulo: seleção da visão, sem domínio financeiro
  (`20-ui/13-exec-views.js`, `20-ui/17-finpes-views.js` e
  `20-ui/23-research-views.js`);
- teste de navegador focado: registry/compatibilidade em
  `tools/navigation_ia_test.py`; contrato estrutural, interação e acessibilidade
  em `tools/exec_submenu_test.py`, `tools/finpes_navigation_test.py` e
  `tools/research_navigation_test.py`.

## Verificação mínima

Um submenu hierárquico só está validado quando o teste comprova:

- faixa fechada com conteúdo colapsado — o clipe interno com altura zero; a
  faixa em si conserva a `border-bottom` transparente que anima ao abrir;
- expansão deslocando fisicamente contexto e conteúdo;
- ausência de overlay, sombra flutuante e overflow horizontal;
- hover transitório com travessia segura e delay;
- clique/Enter/Espaço fixando a faixa após `pointerleave` e resize;
- clique no acionador já fixado mantendo-a aberta;
- clique interno mantendo-a aberta e clique externo fechando;
- Escape e navegação por setas/Home/End;
- `inert` e destinos ocultos fora da ordem de foco — verificado por
  comportamento (tentar focar e o foco não assentar), nunca por `tabIndex`:
  `inert` não altera essa propriedade e a medição estrutural dá falso negativo;
- estado ativo e ausência de tabs internas duplicadas;
- troca de módulo com a faixa aberta deixando um único acionador expandido;
- desktop/mobile e temas claro/escuro;
- zero `pageerror` e zero erro de console — o teste deve servir stub inerte às
  origens externas em vez de abortá-las, senão o próprio isolamento produz
  `ERR_FAILED` e esvazia a asserção;
- quando há workspaces: destino inicial ao entrar no módulo, preservação de
  estado operacional na ida e volta, e ausência de duplicação do conteúdo
  realocado.
