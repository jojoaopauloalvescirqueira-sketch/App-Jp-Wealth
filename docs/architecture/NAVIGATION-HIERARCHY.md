# Navegação hierárquica — contrato de implementação

Contrato de apresentação do primeiro incremento da lateral contextual,
CHG-CONTEXTUAL-SIDEBAR-20260909, autorizado pelo proprietário. Substitui neste
escopo a faixa horizontal e sua abertura por hover. Não altera o resolver,
as regras de domínio nem autoriza adoções futuras ou integração.

## Destinos preservados

Há cinco primários, nesta ordem: Dashboard, Forex, Finanças Pessoais, Research
e Alladin. `JPWNavigation.routes()` mantém seus IDs `dashboard`,
`forex-overview`, `personal-finance`, `research-forex` e `alladin`.

- Forex mantém seis filhos: `forex-overview`, `forex-preparation`,
  `forex-account`, `forex-operation`, `forex-reconciliation`, `forex-planning`.
- Finanças Pessoais mantém Visão Geral, Orçamento Mensal, Dívidas & Crédito,
  Comparativo Mensal e Cenários, pela superfície `window.JPWFin.ui`.
- Research mantém `research-forex`, `research-stocks-br`,
  `research-stocks-global`, `research-reits` e `research-others`.
- Os níveis locais de Operação, Apuração, Planejamento e Research/Forex
  continuam nas superfícies existentes. Calendário, NoCoda e Pivots mantêm
  seus aliases e owner Research/Forex.
- Alladin preserva suas abas internas e o próprio ciclo de renderização.

Preparação operacional e a ação `tool-check` da Central continuam identidades
distintas. Os aliases legados, defaults e a recusa atômica de destino inválido
permanecem responsabilidade de `01-navigation.js`. Não há router novo, URL
persistida ou restauração inédita de rota ao recarregar.

## Estrutura canônica

`#appSidebar` contém a única navegação global `#nav`. Os cinco botões reais
continuam filhos diretos de `#nav`, preservando seletores e medições dos estilos.
A seleção de módulo e a expansão de seus subdestinos são botões separados.
Apenas o módulo ativo expõe um expansor; escolher um primário abre seus filhos,
inclusive quando esse primário já estava ativo e recolhido.

Há um único `#navSubShell`, movido dentro de `#nav` para depois do expansor
ativo. Contém os painéis N2 existentes, sem clonagem. No desktop, sua expansão
ocupa espaço na lateral, sem deslocar verticalmente o conteúdo principal.
Apenas um painel N2 pode estar visível e fora de `inert`.

Os grupos `.nav-sub-contexts` N3 são movidos uma vez para `#navLocalSlot`,
na área de trabalho. A lateral tem no máximo dois níveis. Recolher o N2 não
esconde o contexto local do destino atual. Alladin mantém suas abas no conteúdo.

```text
body > header: marca, menu mobile e ações globais
#appSidebar: #nav (primários + expansores + #navSubShell), #railToggle
#gdContextRow: avisos e informações globais existentes
#appMain:
  #shellPageHeader: #shellLocation + #navLocalSlot
  telas físicas existentes (sem .screen nova ou aninhada)
#gdFooter
```

O cabeçalho de localização deriva módulo, filho e visão das superfícies
existentes; não cria uma segunda fonte de estado. Dashboard mantém os resumos
superiores e Sistema/Atalhos abaixo. As peças operacionais realocadas continuam
em Forex; este incremento não altera essa projeção.

| Elemento | Contrato |
|---|---|
| primário | `.tab[data-route]`, filho direto de `#nav` |
| expansor | `[data-nav-expand="<surface>"]`, único dono de `aria-expanded` |
| painel N2 | `<surface>NavSubmenu`, `.nav-sub-menu` |
| filho canônico | `[data-nav-item][data-nav-child="<route>"]` |
| contexto N3 | `<surface>NavContexts` em `#navLocalSlot` |
| destino local | `[data-nav-item][data-nav-local-surface][data-nav-local-view]` |
| visão local legada | `[data-nav-sub-view="<chave>"]` |

## A marca como acesso ao Dashboard

A logo do cabeçalho é o caminho de volta ao Dashboard — a convenção que todo
usuário de aplicação web já traz de fora. É um `<button type="button">` de
verdade, `#brandHomeBtn`, com `data-route="dashboard"`, e **entra no mesmo
seletor de fiação dos primários**:

```js
document.querySelectorAll('#nav > .tab[data-route], .brand-home[data-route]')
```

Não há segunda implementação de navegação. Uma segunda seria uma segunda
verdade sobre o que "ir para o dashboard" significa, e as duas divergiriam na
primeira mudança de rota.

Ser um `<button>` real dá Enter e Espaço de graça, sem nenhum listener de
teclado próprio. O nome acessível descreve o **destino** — `aria-label="Ir para
o Dashboard"` —, não a imagem: por isso a logo é decorativa (`alt=""`) e o
wordmark sai da árvore de acessibilidade, evitando que o leitor de tela anuncie
"JP Wealth JP WEALTH V9.1" antes de dizer para onde o controle leva.

Visualmente nada muda: `.brand-home` devolve ao user-agent o fundo, a borda, a
fonte e o alinhamento que ele impõe a botões, acrescentando apenas o que o gesto
exige — `cursor:pointer` e alvo de toque de 44 px. O foco visível continua vindo
do sistema de estilos existente.

Como toda navegação, o gesto é **UI pura**: não escreve em `S`, não persiste
rota e não toca storage.

## Interação e acessibilidade

Os estados de abertura são efêmeros e exclusivos da UI; não entram em `S`,
backup ou storage. O expansor alterna apenas o grupo do módulo atual, sem
navegar, salvar ou inicializar outro módulo. Hover nunca abre ou fecha grupo.
Um clique fora não recolhe a navegação lateral. Selecionar outro módulo muda o
grupo; escolher Dashboard ou Alladin remove o N2 lateral.

Filhos canônicos chamam o resolver; destinos locais chamam
`JPWNavigation.navigateLocal()`. `aria-current`, `hidden`, `inert` e foco
acompanham o destino efetivo. N2 e N3 têm pontos de Tab e navegação por
setas/Home/End separados. No expansor, seta para baixo abre e foca o item
atual; seta para cima abre e foca o último. Escape no N2 desktop recolhe o
grupo e devolve foco ao expansor. Selecionar destino leva o foco ao conteúdo
usando `JPWNavigation.focusCurrentScreen()`.

## Compatibilidade das preferências de apresentação

Valores, chaves e controles existentes são preservados, sem schema novo.
Leitura, navegação e recarga não regravam nem removem preferências. Somente
os controles explícitos salvam a chave correspondente. Falha de gravação
mantém a escolha anterior e anuncia a indisponibilidade.

| Preferência | Apresentação |
|---|---|
| `jpw_rail=expanded` ou ausente | lateral desktop com rótulos e grupo contextual |
| `jpw_rail=collapsed` | lateral compacta desktop e controle para expandir |
| `jpw_nav=classic` | seleção com borda e realce discreto |
| `jpw_nav=pill` | destaque arredondado estável |
| `jpw_nav=kinetic` | indicador com transição e resposta ao ponteiro fino |

Valores desconhecidos mantêm o comportamento defensivo de leitura existente,
sem normalizar a chave gravada ou aceitá-la como valor válido. A preferência
compacta não elimina rotas: o usuário pode selecionar os primários e expandir
explicitamente a lateral para acessar filhos. Os botões compactos preservam
nomes acessíveis e títulos. Mobile mostra todos os rótulos independentemente
de `jpw_rail`, sem gravar por mudança de viewport. Os três estilos usam os
tokens claro/escuro existentes; reduced motion desativa transições.

O envelope v6 de layout e as identidades lógicas Dashboard/Forex permanecem
intactos. Esta camada não lê, projeta nem regrava personalizações dos widgets.

## Navegação interna e fonte única

O shell usa `JPWNavigation.current()` e as superfícies `window.JPWExec.ui`,
`window.JPWFx.ui`, `window.JPWFin.ui` e `window.JPWResearch.ui`. Operação usa
`panel`/`motor`; Apuração combina `#contab` e `exec/history`; Planejamento usa
`overview`/`planning`/`actuals`/`table`. Seleção de aba Alladin é observada para
a localização, sem leitura financeira ou alteração de seu renderizador.

N2/N3 são nós existentes realocados, sem tabs equivalentes duplicadas. Nenhum
interior de módulo é redesenhado. A política de DOM, rascunhos e renderização
continua pertencendo a cada módulo; não se impõe uma política universal.

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
3. **Preservar o ciclo de vida do workspace.** Nos workspaces Forex e Research aqui descritos, a troca é de visibilidade, não de DOM. Isso preserva
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
que já carrega duas camadas de wrapper. Reabrir os subdestinos estando já no módulo
não conta como entrada nova, porque a remoção e a recolocação de `.active`
ocorrem no mesmo bloco síncrono e chegam juntas em um único callback.

Alladin conserva o descarte de conteúdo inativo e a seleção de aba em sessão
já implementados. Preservação de rascunho e foco deve ser comparada ao ciclo
real da baseline, sem aplicar por analogia a política de outro módulo.

## Mobile

Até 900 px, a lateral vira gaveta modal, aberta pelo botão do cabeçalho.
Mantém rótulos completos e os mesmos destinos. N3 continua no conteúdo.
A gaveta usa nome acessível, `aria-modal`, foco inicial no módulo ativo,
contenção de Tab e fundo `inert`. Fechar por Escape, botão ou backdrop
restaura o foco ao acionador. Selecionar um destino fecha a gaveta e foca
conteúdo. Ao voltar ao desktop, restaura o estado anterior de `inert` e
scroll, sem persistir a abertura da gaveta nem a adaptação de viewport.

## Responsabilidades por arquivo

- `index.html`: primários, expansores, lateral e localização semântica.
- `src/styles/app.css`: grade, estilos existentes adaptados e responsividade.
- `src/js/40-app/01-navigation.js`: registry, aliases e estado corrente, preservados.
- `src/js/40-app/11-operational-shell.js`: projeção N2/N3, expansão, gaveta e foco.
- `src/js/40-app/12-global-dashboard.js`: montagem de `#nav` no slot lateral.
- `src/js/20-ui/02-sidebar.js` e `12-nav-style.js`: controles de apresentação.
- Adaptadores de módulo: seleção e ciclo de vida existentes, preservados.

## Verificação mínima

- Cinco primários, filhos, visões locais e aliases acessíveis; destino inválido
  recusado sem mudança de estado ou storage.
- Expansão e seleção separadas, ausência de hover obrigatório e de nav duplicada.
- N2 lateral sem deslocamento vertical do conteúdo; N3 local sem duplicação.
- Teclado, foco visível, Escape, contenção mobile e retorno de foco.
- Painéis ocultos `hidden/inert`, com tentativa real de foco recusada.
- Módulo corrente, localização e ausência de inicialização duplicada.
- Preferências antigas, ausentes e inválidas; bytes preservados em navegação
  repetida e recarga; controles explícitos, quota e leitura indisponível.
- Rascunhos, alertas e comportamento operacional comparados à baseline com
  dados sintéticos; regressão v6 e Dashboard → Forex integrada.
- Desktop/mobile, claro/escuro, reflow, texto longo e reduced motion; sem
  overflow do shell ou foco encoberto.
- Zero `pageerror` e erro de console nos cenários isolados. Origens externas
  recebem stubs inertes para que o isolamento não fabrique falhas de rede.

As evidências focais estão em `tools/navigation_ia_test.py`,
`tools/exec_submenu_test.py`, `tools/finpes_navigation_test.py`,
`tools/research_navigation_test.py` e `tools/contextual_sidebar_test.py`.
`tools/dashboard_forex_relocation_test.py` mantém a regressão específica v6.
Os gates existentes permanecem inalterados; execução e auditoria são
registradas no candidate efetivamente testado, sem presumir aprovação pelo
contrato. Este documento não autoriza commit, integração ou publicação.
