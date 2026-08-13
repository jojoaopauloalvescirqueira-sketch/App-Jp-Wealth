# Navegação hierárquica — contrato de implementação

Este documento registra o padrão reutilizável aprovado para módulos que venham
a possuir um segundo nível de navegação no JP Wealth. Ele descreve arquitetura
de interface, não autoriza automaticamente aplicar submenus a outros módulos.
Cada nova adoção continua exigindo tarefa e aprovação próprias.

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

No protótipo de Planejamento, a ordem DOM é:

```text
header
#fxNavSubmenuShell
#gdContextRow
#appMain
```

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
--fx-nav-surface:
  color-mix(in srgb, var(--jp-surface) 30%, var(--gd-surface-subtle));
```

Assim o contraste acompanha os temas claro e escuro sem introduzir uma cor
isolada. A faixa usa divisor discreto, sem borda de card ou sombra pesada.

## Navegação interna e fonte única

O segundo nível deve chamar o mecanismo visual já existente do módulo. Não se
cria estado paralelo para conteúdo ativo. No Planejamento FX, as chaves
`overview`, `planning`, `actuals` e `table` são encaminhadas para
`window.JPWFx.ui.selectView()`.

Quando a faixa superior substitui tabs equivalentes no conteúdo, essas tabs
devem ser removidas para existir uma única fonte visível de navegação. Conteúdo,
renderizadores e lógica de domínio permanecem intactos.

## Mobile

Hover nunca é requisito. O toque no módulo fecha a gaveta global e abre a faixa
contextual no fluxo vertical. Os itens podem empilhar, mas a faixa continua sem
overlay e sem sidebar. Um segundo toque no acionador não fecha a faixa fixada;
o usuário fecha tocando fora ou usando Escape em teclado conectado.

## Responsabilidades por arquivo

- `index.html`: acionador global e estrutura semântica da faixa;
- `src/styles/app.css`: grid estrutural, animação, terceiro tom e responsividade;
- `src/js/40-app/11-operational-shell.js`: abertura transitória/fixada, foco e
  fechamento;
- script de UI do módulo: seleção da visão já existente, sem domínio financeiro;
- teste de navegador focado: contrato estrutural, interação e acessibilidade.

## Verificação mínima

Um submenu hierárquico só está validado quando o teste comprova:

- faixa fechada com altura efetiva zero;
- expansão deslocando fisicamente contexto e conteúdo;
- ausência de overlay, sombra flutuante e overflow horizontal;
- hover transitório com travessia segura e delay;
- clique/Enter/Espaço fixando a faixa após `pointerleave` e resize;
- clique no acionador já fixado mantendo-a aberta;
- clique interno mantendo-a aberta e clique externo fechando;
- Escape e navegação por setas/Home/End;
- `inert` e destinos ocultos fora da ordem de foco;
- estado ativo e ausência de tabs internas duplicadas;
- desktop/mobile e temas claro/escuro;
- zero `pageerror` e zero erro de console.
