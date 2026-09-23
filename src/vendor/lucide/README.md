# Lucide — recorte estático do shell JP Wealth

Onze SVGs originais do repositório oficial `lucide-icons/lucide`, fixados no commit
`f06ac67e33d645c40b8ce19a0419c85c5d7dd751` (22/09/2026). A versão identificada é o
commit: não há pacote instalado nem versão de release presumida.

## Origem e licença

`icons/*.svg` e `LICENSE` foram obtidos de URLs `raw.githubusercontent.com`
fixadas nesse commit e preservados byte a byte. `PROVENANCE.json` registra URL,
SHA-256, SHA-1 de blob Git, tamanho, função e consumidor de cada arquivo.
Os SVGs de origem não contêm cabeçalho de licença individual; não adicionamos
cabeçalhos que alterariam os bytes originais. O `LICENSE` integral os acompanha.

A licença principal é ISC, de Lucide Icons and Contributors (2026). O mesmo
arquivo contém a licença MIT de Cole Bemis para os ícones derivados de Feather.
Neste recorte, a lista oficial inclui `chevron-left`, `log-out`, `search` e `x`.
Não remover nenhum dos avisos. A cópia inline do aviso integral acompanha o
sprite em `index.html` para continuar presente no HTML portátil independente.

## Consumidores delimitados

| Função | Ícone | Consumidor |
|---|---|---|
| Notificações | `bell` | `#headerNotificationsBtn` |
| Configurações | `settings` | `#headerConfigBtn` |
| Finalizar sessão | `log-out` | `#finalizeSessionBtn` |
| Dashboard | `layout-dashboard` | `#nav > button[data-primary="dashboard"]` |
| Research | `search` | `#researchNavTrigger` |
| Forex | `chart-no-axes-combined` | `#execNavTrigger` |
| Finanças Pessoais | `house` | `#finpesNavTrigger` |
| Alladin | `briefcase-business` | `#nav > button[data-primary="alladin"]` |
| Ferramentas e Serviços | `sliders-horizontal` | `#toolsNavTrigger` |
| Fechar navegação lateral | `x` | `#sidebarClose` |
| Voltar um nível de navegação | `chevron-left` | `#submenuNavBack` |

Os IDs de símbolos são `shell-icon-<nome>`, dedicados ao shell. Não substituir
símbolos compartilhados de módulos internos. A existência do arquivo fonte não
comprova o consumidor: a integração é conferida no DOM do candidate.

## Apresentação e execução

- Geometria e `viewBox="0 0 24 24"` preservados. O original tem stroke 2; a
  apresentação do shell usa `stroke: currentColor`, espessura 1,75 e caixa de
  20 CSS px. Essa é uma adaptação de apresentação, não desenho original Apple
  ou criação autoral do JP Wealth.
- As formas são inseridas em símbolos no sprite existente de `index.html` e
  consumidas por `<use href="#shell-icon-...">`. Não requisitar os SVGs raw em
  runtime, não carregar CDN e não acrescentar scripts, pacote ou fonte.
- O gerador oficial leva o sprite e o aviso de licença ao portátil. Os arquivos
  raw são fontes rastreáveis; não exigem novas entradas de service worker.
- Preservar marca e avatar. O menu de duas linhas CSS, glyph do rail, setas de
  disclosure e transformações controladas pelo runtime são recursos existentes,
  não Lucide. Preservar a visibilidade própria de cada layout.
- Os ícones são decorativos quando o botão já possui nome acessível. Manter
  nomes, foco e ações nos controles existentes; não transferi-los ao SVG.

Os onze arquivos foram analisados como XML com listas permitidas de elementos e
atributos: sem scripts, foreignObject, referências externas, entidades, atributos
de evento, fontes ou imagens incorporadas. A análise de assets não substitui a
verificação do DOM, da visibilidade ou do comportamento no produto.
