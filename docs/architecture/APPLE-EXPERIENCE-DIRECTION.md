# Apple → JP Wealth — completion pass

X1 permanece filosofia canônica; Apple HIG e WCAG2.2 orientam a adaptação web.
Usamos os materiais já examinados e os dois boards Sketch como referência óptica,
sem copiar telas, marcas ou distribuir SF Symbols. V2 é histórico abaixo.

## Decisões materiais e evidência

| Problema | Referência Apple | Adaptação JP Wealth / implementação | Evidência prevista no pacote |
|---|---|---|---|
| Dashboard como coleção de cards | Layout, visual hierarchy, charting data | Quatro capítulos, fatos antes de registro, índice de âncoras, mesmos atalhos; dmCard e CSS | 40 comparações + apple_experience_test |
| Forex mistura preparo e estado | Layout, feedback, buttons | Estado e ações com quatro fatos contínuos; VRM/agenda de apoio, bloqueios presentes | Capturas + regressão de rotas/contraste |
| Orçamento fragmentado e labels móveis ausentes | Forms, grouping, accessibility | Resumo planejado/realizado, receitas/despesas em sequência; labels e verbos ao lado do registro | PF/recorrência/readonly + captura povoada |
| NoCoda só entradas sem figura | Charting data, disclosure | Bancada com geometria canônica e âncoras; no celular entrada antes de prévia; texto técnico em details | Focal liga SVG às âncoras, dados/persistência iguais |
| Pivots não compara visualmente amostras | Charting data, selection | Biblioteca e barras de medianas H1/H4, n explícito; sem dados não vira zero | Focal canônico + estudos/notas |
| Lab esconde objeto atrás de métricas | Layout, motion, direct manipulation | Executar antes de canvas; análise ao lado/abaixo; parâmetros existentes e A13 preservados | Capturas ativas/pausadas e A13 |
| Alladin não distingue objeto de fato | Tables, content hierarchy | Cabeçalho por entidade, CTA próximo, linhas rotuladas móveis, tinta neutra; qualidade visível | 7 vistas/CRUD/ledger/readonly, busca |
| Tickets compete com escrita | Split views, content clarity | Coleções compactas e página de escrita; vazio com próximo ato; callbacks originais | Estados povoados + persistência/teclado |
| Settings reúne categorias sem intenção | Settings, search, grouping | Preferências/dados e método/apoio; mesmas categorias/busca, ações perigosas preservadas | Matriz, busca/Editor/backup e foco |
| Símbolos/cores ambíguos | SF Symbols optical/semantic guidance; WCAG contrast | SVGs originais; verbos PF; remove setas decorativas; ícone de mais/refresh; texto escuro no azul claro dark | Inventário20grupos, contraste e interação |

Referências oficiais já consultadas: [layout](https://developer.apple.com/design/human-interface-guidelines/layout),
[charting data](https://developer.apple.com/design/human-interface-guidelines/charting-data),
[buttons](https://developer.apple.com/design/human-interface-guidelines/buttons),
[accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility),
[SF Symbols](https://developer.apple.com/sf-symbols/),
[WCAG2.2](https://www.w3.org/TR/WCAG22/).
Conteúdos e datas de consulta: `evidence/apple-source-index.json` externo.

## Oportunidades de visualização — decisão atual

| Área / pergunta | Dado e fonte canônica | Decisão |
|---|---|---|
| Dashboard: onde agir? | Quatro read-models / compute e clearance | MANTER barras de limite e fatos; REJEITAR mini-séries duplicadas sem ganho sobre resumo/atalho |
| Forex: como evoluiu saldo efetivado? | Série ledger / gráfico existente | MANTER linha/inspector existente; FUTURO equity flutuante por falta de série/contrato |
| PF: evolução mensal e comparação? | pfCompSeries e agregado BRL_CENTS existentes | MANTER gráfico de comparação; resumo explícito antes de lançar. REJEITAR pizza com receitas/despesas incompletas |
| NoCoda: posição relativa das três âncoras? | geometry.levelPrice e compute | IMPLEMENTADO SVG linhas0/−1, âncoras e legenda; sem cotação/valor de mercado |
| Pivots: como diferem H1/H4? | stats().timeframes median/n | IMPLEMENTADAS barras relativas de medianas, n e Sem dados; tabela mantém precisão |
| Calendário: próximo evento? | Semana/filtros do pipeline atual | REJEITAR gráfico; lista temporal comunica ordem e detalhes com menos esforço |
| Lab: como emerge distribuição? | Engine/estatísticas Galton | MANTER histograma2D e métricas existentes; palco antes da análise |
| Alladin: patrimônio ou distribuição monetária? | Cadastro, ledger, saldo por moeda e quantidades | FUTURO: valuation/conversão/custo ausentes. Não somar moedas/unidades; tabela por identidade preservada |
| Tickets: como retomar escrita? | Coleção, conteúdo e estado de salvamento | REJEITAR gráfico, não responde à tarefa |
| Settings: como configurar? | Preferências/armazenamento existentes | REJEITAR gráficos decorativos; busca/grupos/fatos suficientes |

## Comparação espacial concreta

`evidence/completion/lab-spatial-comparison.html` e PNG comparam os mesmos bins
ilustrativos em2D e projeção oblíqua. 3D REJEITADO: profundidade não acrescenta
variável, cria oclusão/perspectiva e exige câmera, foco alternativo e mais recursos.
É conceito visual externo, não motor3D implementado, benchmark ou pesquisa humana.
O Lab continua2D, com preferências persistidas e simulação transitória em RAM.

## Preservação e estado

Resultados finais e classificação A/B/C são externos, ligados ao manifesto final;
testes verdes sozinhos não aprovam design. Esta fonte não antecipa aceite.
Nenhuma regra financeira, schema, persistência, ordem A10, faixa A11, cópia A12
parcial ou continuidade A13 foi alterada. OPEN-05/V11 e AUD-05/P2 seguem abertos.

## Histórico — direção V2 (decisões e conclusões daquela revisão)

# JP Wealth — direção de experiência Apple-guided

Candidate local sobre `fafb228316cbcad8091ebc4632443a51687ace43`, 2026-09-12.
Contrato: [CHG/CTX](../work/CHG-APPLE-EXPERIENCE-REDESIGN-20260912.md).
X1 continua canônica; esta página registra somente decisões do produto.
Não é licença de ativos, especificação Apple, homologação financeira ou aceite.

## Direção e rastreabilidade

| Problema observado | APPLE | ADAPTAÇÃO JP WEALTH / mudança | Evidência pretendida |
|---|---|---|---|
| Ações globais só por símbolos; encerramento parecia perfil | [Buttons](https://developer.apple.com/design/human-interface-guidelines/buttons), [SF Symbols](https://developer.apple.com/design/human-interface-guidelines/sf-symbols) | Rótulos Configurações, Tickets, Finalizar sessão; símbolo original de saída; mesmos handlers e proteções | teclado, retorno de foco, 320px |
| Ícones dos módulos pouco distintos | [Sidebars](https://developer.apple.com/design/human-interface-guidelines/sidebars) | Cinco SVGs originais em sprite local; grade, pesquisa, tendência, casa e pasta; texto permanente; mesmas preferências | geometria, labels, navegação repetida |
| Camadas de conteúdo/controle indistintas e contraste frágil | [Materials](https://developer.apple.com/design/human-interface-guidelines/materials), [Color](https://developer.apple.com/design/human-interface-guidelines/color) | Neutros azulados, conteúdo opaco, shell quase opaco, bordas semânticas; contraste aumentado e redução de transparência | temas, medições de contraste e inspeção |
| Densidades e formatos de controles distintos | [Layout](https://developer.apple.com/design/human-interface-guidelines/layout), [Typography](https://developer.apple.com/design/human-interface-guidelines/typography) | Tokens existentes preservados por nome; superfícies 16px, controles 9px, texto de sistema; alinhamento e espaçamento por tarefa | formulários, texto longo, reflow |
| Cartões do Dashboard esticados sem informação | [Layout](https://developer.apple.com/design/human-interface-guidelines/layout) | Cartões alinhados no início, medidas/tabulares claras, atalhos agrupados; retirar setas diagonais redundantes | mesmos fatos e destinos, comparação visual |
| Cadastro de caixa confundível com saldos/ledger | [Grouping in layout](https://developer.apple.com/design/human-interface-guidelines/layout) | Alladin separa grupos rotulados Cadastros / Movimentação e leitura; sete botões e IDs preservados | sete destinos, leitura e ausência de gravação |
| Experiência de escrita compete com chrome | [Modality](https://developer.apple.com/design/human-interface-guidelines/modality) | Notas com superfície de leitura e empty state legível; mantém drawer, rascunhos, retry, resize e fechamento | regressões de notas e foco |
| Componentes de Research/Forex não têm a mesma densidade | [Charting data](https://developer.apple.com/design/human-interface-guidelines/charting-data) | Organização visual de calendário, formulários e estatísticas; contexto somente Forex; Lab educacional sem destaque de lucro | A10/A11/A13, filtros e ciclo Lab |

As medidas em CSS px são decisões web do projeto; não são medidas obrigatórias
Apple em pontos. Estados financeiros e cores de fase conservam seus papéis.
Ações destrutivas continuam protegidas. Rótulo melhor não muda a operação.

## Fontes e licença

Pesquisa oficial em 2026-09-12: JSON DocC de 26 temas HIG, índice e hashes externos
em `../evidence/apple-source-index.json` na raiz da campanha. Texto original não
foi duplicado neste repositório. Kit [macOS27](https://www.sketch.com/s/57153a31-3379-4737-8ac6-dbfd6525f052)
e [iOS27](https://www.sketch.com/s/04c24d8b-38fb-4afb-8836-36617e022f02/symbols)
observados no Chromium: anatomia, estados e variações. Catálogo oficial:
[Apple Design Resources](https://developer.apple.com/design/resources/).

Não distribuímos fontes, símbolos ou templates Apple. Stack de sistema existente
usa fontes locais disponíveis; símbolos adicionados são desenhos originais.
[Termos de fontes](https://developer.apple.com/fonts/) não foram tratados como
permissão genérica de distribuição web. O material CSS não é Liquid Glass nativo.
[WCAG 2.2](https://www.w3.org/TR/WCAG22/) complementa a HIG; nenhum certificado
integral é inferido das verificações focais.

## Graph opportunity map

| Pergunta | Dados existentes / fonte | Visualização e benefício | Risco / decisão |
|---|---|---|---|
| Como mudou meu orçamento? | pfCompSeries, 12 competências em 20-ui/20-finpes-comparison.js | Linha existente + seletor + tabela; mantém lacunas e BRL_CENTS | MANTER, não interpolar ausência; nenhuma nova série |
| Qual saldo foi efetivado ao longo do período? | série existente em 20-ui/07-chart-crosshair-tooltip.js / renderDashCharts | Linha e inspector de ponto já entregues | MANTER; não equity flutuante; não novo cálculo |
| Quanto risco aberto há frente ao limite? | read-model Dashboard/clearance | Números e barra existente | MANTER; não usar nova perspectiva ou escala financeira |
| Qual evento chega primeiro? | ecalEvents / semana da fonte | Lista cronológica com filtros e estado da fonte | NÃO IMPLEMENTAR gráfico: lista responde melhor |
| Qual patrimônio consolidado possuo? | Alladin não tem valuation/cost basis | Nenhum gráfico de composição confiável | NÃO IMPLEMENTAR: quantidades não são moedas; agregação ausente |
| Quantas posições existem por conta/instrumento? | leitura.posicoes | Tabela por identidade/moeda/quantidade | MANTER tabela; não somar unidades diferentes |
| Como emerge uma distribuição? | estatísticas e física Galton existentes | Histograma e placa2D, detalhes DOM | MANTER com apresentação coerente; nenhuma matemática nova |
| Como comparar estudos NoCoda/Pivots? | estudo selecionado e geometria atual | Representação do estudo existente e tabelas | MANTER; sem métrica econômica inferida |

IMPLEMENTAR nesta campanha: refinamento da apresentação compartilhada; nenhuma
nova série, composição ou tipo de gráfico foi justificado. Isso não é capacidade
analítica nova. Gráficos anteriores permanecem testáveis por suas suítes.

## 3D opportunity map

| Hipótese | 3D × 2D × tabela | Decisão |
|---|---|---|
| Galton com profundidade | Física atual é2D; profundidade não tem variável independente. Projeção pode ocultar pinos/bolas; placa2D mostra trajetória e tabela mostra contagem exata | NÃO IMPLEMENTAR, sem engine/ativos novos |
| Gráfico financeiro espacial | Perspectiva dificulta comparação sem acrescentar dado | NÃO IMPLEMENTAR |
| Superfície multivariada educacional | Não existe modelo/série canônica correspondente | NÃO IMPLEMENTAR: novo domínio fora de escopo |

Comparação acima é análise de informação disponível, não experimento humano que
prove superioridade universal de2D. Nenhum protótipo3D ou ganho de desempenho é
alegado. Mantemos matemática, lifecycle e preferências do laboratório.

## Limites preservados

A12 parcial, OPEN-05/V11/FCR/FEO, AUD-05/P2 e demais dívidas continuam separadas.
Inspeção de telas não prova todos os caminhos, AT, outros browsers ou usabilidade
humana. Resultados e fingerprint finais pertencem ao relatório externo após
validação e auditoria. Contexto/estado não conferem autorização de integração.

## Inventário e decisões de iconografia

Inventário bruto rastreável externo: `icon-inventory-raw.json`, com caminho/linha;
a busca contém também comentários e não representa uma contagem de ícones únicos.

| Família / consumidores | Decisão e motivo |
|---|---|
| Sprite `index.html`, `.jp-icon`, ícones de Configurações | Manter desenhos locais existentes, grid24/currentColor e nomes dos controles; acrescentar cinco símbolos originais distintos para módulos |
| Cabeçalho: engrenagem, Tickets, encerramento | Texto permanente e saída em vez de pessoa para encerrar. `Tickets`/`Abrir tickets` preservados pelo contrato; nenhuma migração ou renomeação da funcionalidade |
| Disclosure da lateral e voltar/avançar de Settings | Manter chevrons por expansão/histórico, nunca como condição de descoberta por hover |
| Atalhos `dmLink` versus CTA do Dashboard | Remover ↗ decorativa; manter → na ação que efetivamente navega |
| Meses PF, calendário, ordenação no Editor | Manter direção e labels; setas alteram período ou ordem, não são decoração |
| Intervalos NoCoda/Pivots e ordem LIFO | Preservar símbolos em texto que expressam intervalo ou sequência; não são botões |
| Notas: pasta, novo, copiar, exportar, menu e fechar | Manter ações/menus, nomes, confirmação, teclado e foco; superfície de escrita recebe refinamento, não outro sistema de ícones |
| Gráficos/crosshair e Lab | Preservar seleção, direção, valores DOM e informação. Sem desenho Apple distribuído nem animação decorativa |

A geometria da lateral é limitada explicitamente para não herdar a largura fluida
reservada aos gráficos SVG. O estado selecionado mantém texto, fundo e borda;
cores de risco não substituem o veredito textual.

## Conferência por tarefa

| Superfície | Tarefa / informação prioritária | Tratamento e limite |
|---|---|---|
| Dashboard | Orientar risco, orçamento, estudo e patrimônio | Fatos e CTA antes de atalhos; vazio continua explícito; não medir usabilidade por screenshot |
| Forex | Preparar, operar, apurar e planejar | Prontidão antes de ferramentas; faixa contextual e bloqueios preservados; não recolher advertências |
| PF | Distinguir mês, planejado, realizado e cenários | Cabeçalhos e formulários compartilham ritmo; séries/tabela existentes permanecem; campos e cancelamento testados separadamente |
| Research | Calendário e estudos, com placeholders honestos | Não criar conteúdo em Ações/Stocks/REITs/Outros indisponíveis; tabelas e filtros têm hierarquia própria |
| Laboratório | Experimentar distribuição | Controles antes da placa, métricas legíveis, pausa em memória preservada; sem novo lifecycle |
| Alladin | Cadastrar entidades e consultar fatos | Grupos rotulados; histórico, quantidade, qualidade e indisponibilidade não viram valuation |
| Tickets/Notas | Escrever e recuperar | Mesmo drawer, seleções, avisos e menus; não converter gravação recusada em sucesso |
| Configurações/Editor/Backup | Encontrar preferência ou ação de dados | Busca e categorias existentes; espaço de pesquisa adequado em320px; diálogos de confirmação/persistência preservados |

Não foi introduzida nova modalidade. Modais de tarefa e confirmações financeiras
existentes conservam sua fronteira e seus testes; a revisão não remove alerts de
erro de domínio para obter uma interface silenciosa. Não há medição de redução de
passos: os fluxos preservados continuam com seus passos; a mudança torna ações e
grupos explícitos. Ganho de compreensão depende da revisão humana.
