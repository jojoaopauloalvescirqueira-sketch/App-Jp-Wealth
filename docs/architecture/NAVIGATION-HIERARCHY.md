# Navegação hierárquica — contrato de implementação

Este documento registra o padrão reutilizável aprovado para módulos que venham
a possuir um segundo nível de navegação no JP Wealth. Ele descreve arquitetura
de interface, não autoriza automaticamente aplicar submenus a outros módulos.
Cada nova adoção continua exigindo tarefa e aprovação próprias.

Adotam o padrão hoje: **Planejamento** (`fxplan`) e **Execution Board**
(`exec`).

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
| acionador em `#nav` | `<data-screen>NavTrigger`, classe `.tab.nav-sub-trigger` |
| painel do módulo | `<data-screen>NavSubmenu`, classe `.nav-sub-menu` |
| item de destino | `[data-nav-sub-view="<chave>"]` |

As colunas do painel derivam da contagem de itens
(`grid-auto-flow:column`), então módulos com três e com quatro destinos usam a
mesma regra sem número mágico.

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

Clicar em um item do segundo nível troca a visão e mantém a faixa aberta. O
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

O segundo nível deve chamar o mecanismo visual já existente do módulo. Não se
cria estado paralelo para conteúdo ativo. As chaves são encaminhadas para a
superfície pública do módulo — `window.JPWFx.ui` (`overview`, `planning`,
`actuals`, `table`) e `window.JPWExec.ui` (`overview`, `panel`, `nocoda`, `pivots`, `motor`) —
que expõe exatamente `selectView(chave)` e `getView()`.

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
- `src/js/40-app/11-operational-shell.js`: registro dos módulos, abertura
  transitória/fixada, foco e fechamento — genérico, sem id de módulo;
- script de UI do módulo: seleção da visão, sem domínio financeiro
  (`30-accounting/05-fx-planning/05-fx-ui.js` e `20-ui/13-exec-views.js`);
- teste de navegador focado: contrato estrutural, interação e acessibilidade
  (`tools/fx_planning_test.py` e `tools/exec_submenu_test.py`).

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
