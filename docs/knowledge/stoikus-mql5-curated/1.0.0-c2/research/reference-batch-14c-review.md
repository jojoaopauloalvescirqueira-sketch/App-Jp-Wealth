# REF 5271–5703 — leitura semântica complementar 14c

Livro REF, páginas físicas PDF 5271–5703, 433 páginas. Leitura integral do texto extraído, exposto em 11 lotes de até 29.409 caracteres; ledger ao lado contém páginas exatas, hashes originais e lotes. Lotes 01 e 02 relidos isoladamente para reparar truncamento de saída combinada. Catálogo filtrado relido completo em forma compacta após truncamento da primeira exposição extensa.

Esta é leitura semântica textual, não mera extração. Não houve inspeção visual de figuras, execução/compilação MQL, alteração de produto, manual, harness ou Git. MQL_NOT_RUN. Exemplos longos da própria extração têm linhas cortadas (por exemplo 5326 e 5334); o conteúdo extraído foi lido integralmente, mas não se afirma recuperação visual do texto que o corpus não contém. reference-batch-14 e 14b permanecem preservados.

## Síntese aplicada e limites

Graphics fornece infraestrutura para diagnósticos científicos: separar coordenadas reais de pixels, preservar índices/timestamps e explicitar escala, arredondamento e suavização. Curvas automáticas por Y usam índices como X, não tempo. Draw/update/redraw e criação de recursos são operações distintas, com retorno e ciclo de vida próprios. Legendas e números podem ser truncados em pixels; registros numéricos completos devem acompanhar imagens. Uma linha de tendência desenhada não comprova poder preditivo nem implementa política Stoikus. [REF, Scientific Charts, p.PDF 5271–5393]

Séries e indicadores exigem uma sequência observável: escolher símbolo/período e configuração, criar, redimensionar, atualizar, conferir quantidade calculada/disponível, validar sentinelas e só então consumir. RefreshCurrent de buffer atualiza elemento zero e retorna bool; CSeries.RefreshCurrent configura flag e tem inconsistência de assinatura no texto. Não são operações intercambiáveis. Flags de Timeframe/Refresh não são o enum Period. Valores escalares podem retornar zero ou EMPTY_VALUE; cópias retornam quantidade ou -1. Zero, cópia parcial e falha não devem virar silenciosamente leitura válida no monitor. [REF, Base classes e Timeseries, p.PDF 5394–5543]

ADX e ADXWilder têm identidades distintas; Bands/Envelopes/Ichi têm linhas e parâmetros distintos. Applied pode ser preço/handle em médias e bandas, mas em Chaikin é ENUM_APPLIED_VOLUME. Esses wrappers economizam infraestrutura, sem criar por si só estratégia, causalidade, aceitação normativa ou autorização de negociação. A seleção de barra fechada, a janela e qualquer uso de indicador seriam propostas a validar separadamente no Stoikus. [REF, Trend Indicators e Oscillators, p.PDF 5544–5703]

Erros e contradições documentais observados: MaxGrace repete nota de MinGrace; LinesEndStyle troca Get/Set; CCurve.Visible imprime setter no bloco getter; exemplos chamam LinesSmooth enquanto tabela diz LinesIsSmooth; assinaturas contêm texto editorial; CPriceSeries.BufferResize imprime void com retorno bool descrito; CSeries.RefreshCurrent imprime string com retorno None; CiRealVolume.GetData escalar imprime datetime; VIDyA.CmoPeriod/EmaPeriod recebem descrições copiadas de chart. Antes de converter essas partes em código original, consultar headers e executar validação nativa. Nenhuma correção de plataforma é presumida aqui. [REF, p.PDF 5296, 5320–5322, 5337, 5457, 5464, 5521, 5656–5657]

## Ledger dos lotes

- Lote 00: PDF 5271–5301, 29028 caracteres, exposto e lido integralmente.
- Lote 01: PDF 5302–5337, 29362 caracteres, exposto e lido integralmente.
- Lote 02: PDF 5338–5379, 29377 caracteres, exposto e lido integralmente.
- Lote 03: PDF 5380–5430, 28803 caracteres, exposto e lido integralmente.
- Lote 04: PDF 5431–5471, 27850 caracteres, exposto e lido integralmente.
- Lote 05: PDF 5472–5509, 29125 caracteres, exposto e lido integralmente.
- Lote 06: PDF 5510–5542, 29058 caracteres, exposto e lido integralmente.
- Lote 07: PDF 5543–5585, 29409 caracteres, exposto e lido integralmente.
- Lote 08: PDF 5586–5632, 29352 caracteres, exposto e lido integralmente.
- Lote 09: PDF 5633–5675, 28335 caracteres, exposto e lido integralmente.
- Lote 10: PDF 5676–5703, 18892 caracteres, exposto e lido integralmente.

## Notas por ID intersectante

Ancestrais têm somente cobertura do recorte; filhos não duplicam contagem de páginas. Aplicações abaixo são propostas de pesquisa, não descrição de implementação atual.

### REF-0001 — MQL5 Reference [REF, p.PDF 5271–5703]

Ancestral: somente o recorte 5271–5703 foi lido neste registro; não confere leitura integral às 7284 páginas. Aqui o conteúdo útil é gráficos científicos e infraestrutura de séries/indicadores.

### REF-1136 — Standard Library [REF, p.PDF 5271–5703]

Ancestral Standard Library: cobertura local limitada a Graphics e Indicators até CiDeMarker. Não extrapolar para classes de negociação ou restante da biblioteca.

### REF-2637 — Scientific Charts [REF, p.PDF 5271–5393]

Graphics reside em Include\Graphics e fornece eixos, curvas e gráficos próprios. Proposta Stoikus: diagnóstico visual de séries de monitoramento; biblioteca gráfica não acrescenta autorização de negociação.

### REF-2638 — GraphPlot [REF, p.PDF 5272–5275]

GraphPlot aceita Y (índices viram X), pares X/Y, CPoint2D e callbacks CurveFunction com from/to/step, até três curvas; retorna nome do recurso gráfico. Proposta: comparar séries experimentais; validar domínio/passo e não interpretar índices como timestamps.

### REF-2639 — CAxis [REF, p.PDF 5276–5297]

CAxis guarda parâmetros de eixos e suporta escala automática dinâmica. Proposta: fixar unidades e escalas em comparações Stoikus para evitar mudanças visuais parecerem mudanças econômicas.

### REF-2640 — AutoScale [REF, p.PDF 5278–5278]

AutoScale é flag bool get/set: true recalcula escala e false não. Proposta: desativar em comparações entre sessões quando se precisa escala constante.

### REF-2641 — Min [REF, p.PDF 5279–5279]

Min lê/define limite mínimo double do eixo. Proposta: definir piso documentado da unidade representada; não é mínimo dos dados brutos.

### REF-2642 — Max [REF, p.PDF 5280–5280]

Max lê/define limite máximo double do eixo. Proposta: manter teto comparável entre capturas; não substituir verificação numérica dos máximos.

### REF-2643 — Step [REF, p.PDF 5281–5281]

Step retorna double do passo calculado do eixo. Proposta: registrar esse passo com escalas do diagnóstico.

### REF-2644 — Name [REF, p.PDF 5282–5282]

Name lê/define rótulo string do eixo. Proposta: explicitar tempo, preço ou unidade de risco para impedir ambiguidade.

### REF-2645 — Color [REF, p.PDF 5283–5283]

Color lê/define color do eixo. Proposta: contraste de painel; nenhum efeito em cálculos.

### REF-2646 — ValuesSize [REF, p.PDF 5284–5284]

ValuesSize lê/define tamanho int dos números do eixo. Proposta: legibilidade em diagnóstico, a verificar visualmente no terminal.

### REF-2647 — ValuesWidth [REF, p.PDF 5285–5285]

ValuesWidth limita em pixels a extensão dos números; excesso é truncado e ganha pontos. Proposta: assegurar que sinais e casas relevantes continuem visíveis; não usar captura truncada como evidência de valor.

### REF-2648 — ValuesFormat [REF, p.PDF 5286–5286]

ValuesFormat lê/define string de formato numérico. Proposta: exibir precisão apropriada sem confundir arredondamento visual com valor de cálculo.

### REF-2649 — ValuesDateTimeMode [REF, p.PDF 5287–5287]

ValuesDateTimeMode guarda modo int de conversão de data, remetendo a TimeToString. Proposta: informar formato temporal consistente no monitoramento.

### REF-2650 — ValuesFunctionFormat [REF, p.PDF 5288–5289]

ValuesFunctionFormat instala callback DoubleToStringFunction. Exemplo usa índices X para localizar tempos em arrX invertido; proposta: manter sincronismo índice/tempo e limites do array, não copiar mapeamento sem conferir ordenação.

### REF-2651 — ValuesFunctionFormatCBData [REF, p.PDF 5290–5290]

ValuesFunctionFormatCBData guarda void* de objeto auxiliar do formatador. Proposta: explicitar propriedade e duração desse contexto para evitar ponteiro inválido.

### REF-2652 — NameSize [REF, p.PDF 5291–5291]

NameSize controla tamanho int da fonte do nome do eixo. Proposta: separar legenda de unidade dos valores.

### REF-2653 — ZeroLever [REF, p.PDF 5292–5292]

ZeroLever define quando expandir escala para incluir zero. Proposta: documentar inclusão de zero em gráficos de variação e risco, sem alterar os dados.

### REF-2654 — DefaultStep [REF, p.PDF 5293–5293]

DefaultStep é passo inicial double da escala. Proposta: escolher marcações compatíveis com granularidade dos dados.

### REF-2655 — MaxLabels [REF, p.PDF 5294–5294]

MaxLabels lê/define double de quantidade máxima de números no eixo (assinatura documentada). Proposta: limitar poluição visual e conferir tipo no header antes de codificar.

### REF-2656 — MinGrace [REF, p.PDF 5295–5295]

MinGrace é fração da amplitude subtraída do mínimo: 4–16, 0,1 resulta 2,8–16. Proposta: margem gráfica proporcional, distinta de tolerância financeira.

### REF-2657 — MaxGrace [REF, p.PDF 5296–5296]

MaxGrace adiciona fração da amplitude ao máximo: 4–16, 0,1 resulta 4–17,2. Nota final repete indevidamente texto de MinGrace; conferir header/execução antes de depender dela.

### REF-2658 — SelectAxisScale [REF, p.PDF 5297–5297]

SelectAxisScale executa autoescala void. Proposta: recalcular só após atualizar dados e manter evidência de escala usada.

### REF-2659 — CColorGenerator [REF, p.PDF 5298–5300]

CColorGenerator fornece paleta padrão para curvas sem cor explícita e gera nova paleta ao esgotar. Proposta: usar cores explícitas para identidade estável de séries Stoikus.

### REF-2660 — Next [REF, p.PDF 5299–5299]

Next retorna uint da próxima cor; ao esgotar paleta gera novas cores. Proposta: não tratar cor automaticamente gerada como identificador persistente.

### REF-2661 — Reset [REF, p.PDF 5300–5300]

Reset reinicia gerador void. Proposta: controlar início da sequência em diagnósticos reproduzíveis.

### REF-2662 — CCurve [REF, p.PDF 5301–5337]

CCurve herda CObject e administra coordenadas e estilo de pontos, linhas e histograma; oferece customização e tendência. Proposta: manter fonte numérica separada da representação.

### REF-2663 — Type [REF, p.PDF 5303–5303]

Type retorna ENUM_CURVE_TYPE. Proposta: registrar se saída representa pontos, linhas ou histograma ao comparar ensaios.

### REF-2664 — Name [REF, p.PDF 5304–5304]

Name retorna string da curva. Proposta: identificar série sem depender de posição ou cor.

### REF-2665 — Color [REF, p.PDF 5305–5305]

Color retorna uint da curva. Proposta: associar legenda explícita; cor não comprova identidade de dados.

### REF-2666 — XMax [REF, p.PDF 5306–5306]

XMax retorna maior argumento real da curva. Proposta: verificar domínio temporal/numérico antes de plotar.

### REF-2667 — XMin [REF, p.PDF 5307–5307]

XMin retorna menor argumento real da curva. Proposta: checar janela inicial do diagnóstico.

### REF-2668 — YMax [REF, p.PDF 5308–5308]

YMax retorna máximo real dos valores Y. Proposta: comparar com máximos numéricos independentemente da escala em pixels.

### REF-2669 — YMin [REF, p.PDF 5309–5309]

YMin retorna mínimo real dos valores Y. Proposta: detectar amplitude sem inferir dados inválidos omitidos.

### REF-2670 — Size [REF, p.PDF 5310–5310]

Size retorna int de pontos que definem curva. Proposta: confrontar tamanho da curva com amostra esperada.

### REF-2671 — PointsSize [REF, p.PDF 5311–5311]

PointsSize é dimensão linear dos pontos em pixels, int get/set. Proposta: visibilidade sem modificar resolução dos dados.

### REF-2672 — PointsFill [REF, p.PDF 5312–5312]

PointsFill bool controla preenchimento dos pontos. Proposta: distinguir visualmente categorias sem alterar série.

### REF-2673 — PointsColor [REF, p.PDF 5313–5313]

PointsColor uint controla cor de preenchimento. Proposta: legenda estável em diagnóstico.

### REF-2674 — GetX [REF, p.PDF 5314–5314]

GetX copia valores X para double[] de saída; são coordenadas reais e não pixels. Proposta: auditar domínio original separado de ScaleX.

### REF-2675 — GetY [REF, p.PDF 5315–5315]

GetY copia valores Y para double[] de saída; não são pixels. Proposta: preservar valores reais para conferência de resultados.

### REF-2676 — LinesStyle [REF, p.PDF 5316–5316]

LinesStyle controla ENUM_LINE_STYLE. Proposta: diferenciar fontes de série na imagem sem atribuir significado financeiro ao estilo.

### REF-2677 — LinesIsSmooth [REF, p.PDF 5317–5317]

LinesIsSmooth bool controla suavização de linhas. Proposta: desativar em evidência de transições discretas para evitar aparência de observações inexistentes.

### REF-2678 — LinesSmoothTension [REF, p.PDF 5318–5318]

LinesSmoothTension double deve pertencer a (0,1]. Proposta: validar parâmetro e documentar suavização apenas gráfica.

### REF-2679 — LinesSmoothStep [REF, p.PDF 5319–5319]

LinesSmoothStep define comprimento em pixels das linhas aproximantes. Proposta: separar qualidade de desenho de frequência de amostragem.

### REF-2680 — LinesEndStyle [REF, p.PDF 5320–5320]

LinesEndStyle usa ENUM_LINE_END para pontas das linhas; rótulos Get/Set estão trocados no texto. Proposta: verificar assinatura real do header antes de exemplo original.

### REF-2681 — LinesWidth [REF, p.PDF 5321–5322]

LinesWidth int controla espessura. Exemplo combina suavização, tracejado e pontas arredondadas; chama LinesSmooth embora catálogo use LinesIsSmooth. Proposta: não copiar exemplo como compilação comprovada.

### REF-2682 — HistogramWidth [REF, p.PDF 5323–5323]

HistogramWidth int é largura da coluna em pixels. Proposta: não confundir largura desenhada com duração temporal ou contagem.

### REF-2683 — CustomPlotCBData [REF, p.PDF 5324–5324]

CustomPlotCBData guarda void* para desenho customizado. Proposta: manter contexto válido por todo redraw.

### REF-2684 — CustomPlotFunction [REF, p.PDF 5325–5328]

CustomPlotFunction instala callback (texto escreve PlotFucntion); exemplo valida dynamic_cast, quantidade de candles e ponteiros, converte OHLC por ScaleY e X por ScaleX e desenha canvas. Algumas linhas longas da extração estão cortadas; não é receita compilável verificada.

### REF-2685 — PointsType [REF, p.PDF 5329–5329]

PointsType escolhe ENUM_POINT_TYPE. Proposta: legenda para categorias de diagnóstico.

### REF-2686 — StepsDimension [REF, p.PDF 5330–5330]

StepsDimension escolhe 0 (horizontal depois vertical) ou 1 (vertical depois horizontal). Proposta: declarar convenção de degrau para não sugerir momento de mudança incorreto.

### REF-2687 — TrendLineCoefficients [REF, p.PDF 5331–5331]

TrendLineCoefficients expõe coeficientes e overload escreve array de saída, embora rótulo Set. Proposta: verificar assinatura antes de ler coeficientes e não transformar linha ajustada em regra Stoikus.

### REF-2688 — TrendLineColor [REF, p.PDF 5332–5332]

TrendLineColor uint controla cor da tendência. Proposta: destacar que é ajuste gráfico auxiliar.

### REF-2689 — TrendLineVisible [REF, p.PDF 5333–5334]

TrendLineVisible bool mostra/oculta tendência; exemplo usa nuvem de pontos e ColorToARGB. Proposta: tendência visual não valida previsibilidade nem política de negociação.

### REF-2690 — Update [REF, p.PDF 5335–5336]

Update substitui coordenadas por Y (X=índices), X/Y, CPoint2D ou callback com intervalo/passo; p.5336 contém só cabeçalho/rodapé. Proposta: preservar alinhamento das séries ao atualizar.

### REF-2691 — Visible [REF, p.PDF 5337–5337]

Visible trata visibilidade; ambos blocos impressos mostram assinatura setter void(bool), inclusive o intitulado getter. Proposta: resolver divergência no header, sem inventar bool getter a partir deste texto.

### REF-2692 — CGraphic [REF, p.PDF 5338–5393]

CGraphic armazena eixos, curvas, parâmetros e renderização. Proposta: componente de diagnóstico futuro isolado do núcleo de regras e do ciclo de negociação.

### REF-2693 — Create [REF, p.PDF 5341–5341]

Create bool liga recurso gráfico a objeto por chart, nome, subwin e retângulo x1/y1/x2/y2. Proposta: nomes únicos e tratamento explícito de falha.

### REF-2694 — Destroy [REF, p.PDF 5342–5342]

Destroy remove gráfico e destrói recurso. Proposta: prever limpeza determinística ao encerrar diagnóstico.

### REF-2695 — Update [REF, p.PDF 5343–5343]

Update(redraw=true) exibe alterações. Proposta: agrupar mudanças antes de atualizar para controlar custo da UI.

### REF-2696 — ChartObjectName [REF, p.PDF 5344–5344]

ChartObjectName retorna nome do objeto vinculado. Proposta: rastrear recurso sem procurar objetos por suposição.

### REF-2697 — ResourceName [REF, p.PDF 5345–5345]

ResourceName retorna nome do recurso gráfico. Proposta: registrar vínculo recurso/objeto em diagnóstico.

### REF-2698 — XAxis [REF, p.PDF 5346–5346]

XAxis retorna CAxis*. Proposta: configurar unidade e domínio no eixo correto, verificando contexto válido.

### REF-2699 — YAxis [REF, p.PDF 5347–5347]

YAxis retorna CAxis*. Proposta: escala explícita de valores e risco no eixo vertical.

### REF-2700 — GapSize [REF, p.PDF 5348–5348]

GapSize int mede recuos entre elementos em pixels. Proposta: legibilidade, sem significado financeiro.

### REF-2701 — BackgroundColor [REF, p.PDF 5349–5349]

BackgroundColor color controla fundo. Proposta: contraste a validar no terminal.

### REF-2702 — BackgroundMain [REF, p.PDF 5350–5350]

BackgroundMain string é título principal. Proposta: incluir identificação do ensaio.

### REF-2703 — BackgroundMainSize [REF, p.PDF 5351–5351]

BackgroundMainSize int controla fonte do título. Proposta: legibilidade sem inferir layout visual desta leitura textual.

### REF-2704 — BackgroundMainColor [REF, p.PDF 5352–5352]

BackgroundMainColor color controla título. Proposta: contraste do diagnóstico.

### REF-2705 — BackgroundSub [REF, p.PDF 5353–5353]

BackgroundSub string controla subtítulo; assinatura impressa contém texto editorial Set method. Proposta: consultar header antes de implementar e usar subtítulo para contexto de janela.

### REF-2706 — BackgroundSubSize [REF, p.PDF 5354–5354]

BackgroundSubSize int controla fonte do subtítulo; segundo bloco está rotulado Get embora seja setter. Proposta: separar erro editorial do comportamento esperado.

### REF-2707 — BackgroundSubColor [REF, p.PDF 5355–5355]

BackgroundSubColor color controla subtítulo. Proposta: hierarquia visual a validar.

### REF-2708 — GridLineColor [REF, p.PDF 5356–5356]

GridLineColor color controla linhas da grade. Proposta: apoio de leitura sem encobrir pontos.

### REF-2709 — GridBackgroundColor [REF, p.PDF 5357–5357]

GridBackgroundColor color controla fundo da grade. Proposta: contraste com séries.

### REF-2710 — GridCircleRadius [REF, p.PDF 5358–5358]

GridCircleRadius int é raio em pixels dos pontos da grade. Proposta: marcações visuais não representam eventos observados.

### REF-2711 — GridCircleColor [REF, p.PDF 5359–5359]

GridCircleColor color controla pontos da grade. Proposta: distinguir grade de dados.

### REF-2712 — GridHasCircle [REF, p.PDF 5360–5360]

GridHasCircle bool mostra pontos nos nós. Proposta: desligar se houver confusão com curva de pontos.

### REF-2713 — GridAxisLineColor [REF, p.PDF 5361–5361]

GridAxisLineColor uint controla eixos reais do gráfico. Proposta: padronizar conversão de cores na camada visual.

### REF-2714 — HistoryNameWidth [REF, p.PDF 5362–5362]

HistoryNameWidth int limita legenda em pixels, truncando com pontos. Proposta: preservar identificação completa da série no registro textual.

### REF-2715 — HistoryNameSize [REF, p.PDF 5363–5363]

HistoryNameSize int controla fonte do nome da curva; assinatura traz texto editorial Set method. Proposta: conferir header, não copiar literalmente.

### REF-2716 — HistorySymbolSize [REF, p.PDF 5364–5364]

HistorySymbolSize int controla tamanho dos símbolos da legenda. Proposta: tornar tipos de curva distinguíveis.

### REF-2717 — TextAdd [REF, p.PDF 5365–5365]

TextAdd adiciona texto em coordenadas int ou CPoint, com cor e alinhamento. Proposta: anotar contexto do ensaio separado dos valores reais da curva.

### REF-2718 — LineAdd [REF, p.PDF 5366–5366]

LineAdd usa coordenadas int e cor/estilo; overload CPoint é impresso como LineAdd2. Proposta: não supor nome idêntico das sobrecargas; verificar header.

### REF-2719 — CurveAdd [REF, p.PDF 5367–5369]

CurveAdd retorna CCurve*, aceita Y, X/Y, CPoint2D ou CurveFunction; cor pode ser automática ou uint explícita e nome opcional. Proposta: séries nomeadas e cores estáveis, checando ponteiro criado.

### REF-2720 — CurvePlot [REF, p.PDF 5370–5370]

CurvePlot(index) bool desenha curva já criada. Proposta: verificar retorno e manter índice válido após remoções.

### REF-2721 — CurvePlotAll [REF, p.PDF 5371–5371]

CurvePlotAll bool desenha todas as curvas adicionadas. Proposta: separar adicionar, desenhar e Update ao relatar renderização.

### REF-2722 — CurveGetByIndex [REF, p.PDF 5372–5372]

CurveGetByIndex retorna CCurve* por índice. Proposta: validar ponteiro e não manter índice obsoleto após remoção.

### REF-2723 — CurveGetByName [REF, p.PDF 5373–5373]

CurveGetByName retorna primeira curva de nome correspondente. Proposta: nomes únicos para evitar seleção ambígua.

### REF-2724 — CurveRemoveByIndex [REF, p.PDF 5374–5374]

CurveRemoveByIndex bool remove curva. Proposta: tratar retorno e invalidar referências pertinentes.

### REF-2725 — CurveRemoveByName [REF, p.PDF 5375–5375]

CurveRemoveByName bool remove por nome. Proposta: nomes estáveis e conferência da remoção.

### REF-2726 — CurvesTotal [REF, p.PDF 5376–5376]

CurvesTotal inclui todas as curvas independentemente de desenho e visibilidade. Proposta: não contar curvas visíveis a partir desse total.

### REF-2727 — MarksToAxisAdd [REF, p.PDF 5377–5377]

MarksToAxisAdd bool recebe marcas double[], tamanho, posição e dimensão 0=X/1=Y. Proposta: marcações de limites documentadas como anotações, não como regras autorizadas.

### REF-2728 — MajorMarkSize [REF, p.PDF 5378–5378]

MajorMarkSize int controla tamanho em pixels das marcas principais. Proposta: legibilidade a verificar visualmente.

### REF-2729 — FontSet [REF, p.PDF 5379–5379]

FontSet bool recebe nome, tamanho, flags e ângulo com padrões zero. Proposta: checar retorno e fonte disponível no terminal.

### REF-2730 — FontGet [REF, p.PDF 5380–5380]

FontGet devolve nome/tamanho/flags/ângulo por referência. Proposta: registrar configuração gráfica reproduzível.

### REF-2731 — Attach [REF, p.PDF 5381–5381]

Attach bool vincula OBJ_BITMAP_LABEL existente, podendo criar recurso com largura/altura. Proposta: validar vínculo e ownership do objeto antes de Destroy.

### REF-2732 — CalculateMaxMinValues [REF, p.PDF 5382–5382]

CalculateMaxMinValues recalcula extremos de ambos os eixos. Proposta: recomputar após substituir coordenadas, sem confundir com controles financeiros.

### REF-2733 — Height [REF, p.PDF 5383–5383]

Height retorna altura int em pixels. Proposta: calcular layout responsivo do diagnóstico.

### REF-2734 — IndentDown [REF, p.PDF 5384–5384]

IndentDown int define recuo inferior em pixels. Proposta: espaço para rótulos de X.

### REF-2735 — IndentLeft [REF, p.PDF 5385–5385]

IndentLeft int define recuo esquerdo em pixels. Proposta: acomodar números de Y completos.

### REF-2736 — IndentRight [REF, p.PDF 5386–5386]

IndentRight int define recuo direito em pixels. Proposta: evitar corte de curvas e legendas.

### REF-2737 — IndentUp [REF, p.PDF 5387–5387]

IndentUp int define recuo superior em pixels. Proposta: acomodar título.

### REF-2738 — Redraw [REF, p.PDF 5388–5388]

Redraw(rescale=false) bool redesenha e opcionalmente reescala. Proposta: decidir explicitamente se comparação deve conservar escala.

### REF-2739 — ResetParameters [REF, p.PDF 5389–5389]

ResetParameters limpa parâmetros de redesenho. Proposta: não confundir com reset de dados ou estado financeiro.

### REF-2740 — ScaleX [REF, p.PDF 5390–5390]

ScaleX virtual int converte valor real double em pixels. Proposta: usar na camada de desenho customizado, preservando o valor original para auditoria.

### REF-2741 — ScaleY [REF, p.PDF 5391–5391]

ScaleY virtual int converte valor real double em pixels. Proposta: não recuperar valor de cálculo a partir de pixel arredondado.

### REF-2742 — SetDefaultParameters [REF, p.PDF 5392–5392]

SetDefaultParameters restaura padrões do gráfico. Proposta: reaplicar identidade e unidades desejadas após reset.

### REF-2743 — Width [REF, p.PDF 5393–5393]

Width retorna largura int em pixels. Proposta: calcular limites de renderização sem alterar amostra.

### REF-2744 — Indicators [REF, p.PDF 5394–5703]

Indicators situa classes em Include\Indicators: bases, séries, tendências, osciladores, volumes, Bill Williams e custom. Aqui leitura termina em CiDeMarker p.5703; demais descendentes fora deste recorte.

### REF-2745 — Base classes [REF, p.PDF 5395–5494]

Bases incluem buffers tipados, CSeries, CPriceSeries, CIndicator e CIndicators. Proposta: centralizar sincronização e estado de disponibilidade antes de consumir séries no monitor Stoikus.

### REF-2746 — CSpreadBuffer [REF, p.PDF 5396–5402]

CSpreadBuffer fornece acesso simplificado a spread histórico, com armazenamento int; apoia-se em array tipado da biblioteca. Proposta Stoikus: manter semântica de unidade e verificar atualização antes da leitura.

### REF-2747 — Size [REF, p.PDF 5398–5398]

CSpreadBuffer.Size(int) define tamanho do buffer de spread histórico; não comprova preenchimento. Proposta: dimensionar janela e atualizar antes de consumir.

### REF-2748 — SetSymbolPeriod [REF, p.PDF 5399–5399]

CSpreadBuffer.SetSymbolPeriod recebe símbolo string e ENUM_TIMEFRAMES para spread histórico. Proposta: fixar origem dos dados e não misturar séries de instrumentos/períodos distintos.

### REF-2749 — At [REF, p.PDF 5400–5400]

CSpreadBuffer.At(index) retorna int do elemento de spread histórico. Proposta: validar faixa e atualização; acesso por índice não contém sozinho prova de sincronismo.

### REF-2750 — Refresh [REF, p.PDF 5401–5401]

CSpreadBuffer.Refresh atualiza buffer de spread histórico e retorna bool; false significa que não conseguiu atualizar. Proposta: não publicar valor antigo como fresco após falha.

### REF-2751 — RefreshCurrent [REF, p.PDF 5402–5402]

CSpreadBuffer.RefreshCurrent atualiza só elemento zero e retorna bool. Proposta: separar barra corrente mutável das fechadas e tratar false sem inferir novo valor.

### REF-2752 — CTimeBuffer [REF, p.PDF 5403–5409]

CTimeBuffer fornece acesso simplificado a horário de abertura das barras, com armazenamento long; apoia-se em array tipado da biblioteca. Proposta Stoikus: manter semântica de unidade e verificar atualização antes da leitura.

### REF-2753 — Size [REF, p.PDF 5405–5405]

CTimeBuffer.Size(int) define tamanho do buffer de horário de abertura das barras; não comprova preenchimento. Proposta: dimensionar janela e atualizar antes de consumir.

### REF-2754 — SetSymbolPeriod [REF, p.PDF 5406–5406]

CTimeBuffer.SetSymbolPeriod recebe símbolo string e ENUM_TIMEFRAMES para horário de abertura das barras. Proposta: fixar origem dos dados e não misturar séries de instrumentos/períodos distintos.

### REF-2755 — At [REF, p.PDF 5407–5407]

CTimeBuffer.At(index) retorna long do elemento de horário de abertura das barras. Proposta: validar faixa e atualização; acesso por índice não contém sozinho prova de sincronismo.

### REF-2756 — Refresh [REF, p.PDF 5408–5408]

CTimeBuffer.Refresh atualiza buffer de horário de abertura das barras e retorna bool; false significa que não conseguiu atualizar. Proposta: não publicar valor antigo como fresco após falha.

### REF-2757 — RefreshCurrent [REF, p.PDF 5409–5409]

CTimeBuffer.RefreshCurrent atualiza só elemento zero e retorna bool. Proposta: separar barra corrente mutável das fechadas e tratar false sem inferir novo valor.

### REF-2758 — CTickVolumeBuffer [REF, p.PDF 5410–5416]

CTickVolumeBuffer fornece acesso simplificado a volume de ticks, com armazenamento long; apoia-se em array tipado da biblioteca. Proposta Stoikus: manter semântica de unidade e verificar atualização antes da leitura.

### REF-2759 — Size [REF, p.PDF 5412–5412]

CTickVolumeBuffer.Size(int) define tamanho do buffer de volume de ticks; não comprova preenchimento. Proposta: dimensionar janela e atualizar antes de consumir.

### REF-2760 — SetSymbolPeriod [REF, p.PDF 5413–5413]

CTickVolumeBuffer.SetSymbolPeriod recebe símbolo string e ENUM_TIMEFRAMES para volume de ticks. Proposta: fixar origem dos dados e não misturar séries de instrumentos/períodos distintos.

### REF-2761 — At [REF, p.PDF 5414–5414]

CTickVolumeBuffer.At(index) retorna long do elemento de volume de ticks. Proposta: validar faixa e atualização; acesso por índice não contém sozinho prova de sincronismo.

### REF-2762 — Refresh [REF, p.PDF 5415–5415]

CTickVolumeBuffer.Refresh atualiza buffer de volume de ticks e retorna bool; false significa que não conseguiu atualizar. Proposta: não publicar valor antigo como fresco após falha.

### REF-2763 — RefreshCurrent [REF, p.PDF 5416–5416]

CTickVolumeBuffer.RefreshCurrent atualiza só elemento zero e retorna bool. Proposta: separar barra corrente mutável das fechadas e tratar false sem inferir novo valor.

### REF-2764 — CRealVolumeBuffer [REF, p.PDF 5417–5423]

CRealVolumeBuffer fornece acesso simplificado a volume real, com armazenamento long; apoia-se em array tipado da biblioteca. Proposta Stoikus: manter semântica de unidade e verificar atualização antes da leitura.

### REF-2765 — Size [REF, p.PDF 5419–5419]

CRealVolumeBuffer.Size(int) define tamanho do buffer de volume real; não comprova preenchimento. Proposta: dimensionar janela e atualizar antes de consumir.

### REF-2766 — SetSymbolPeriod [REF, p.PDF 5420–5420]

CRealVolumeBuffer.SetSymbolPeriod recebe símbolo string e ENUM_TIMEFRAMES para volume real. Proposta: fixar origem dos dados e não misturar séries de instrumentos/períodos distintos.

### REF-2767 — At [REF, p.PDF 5421–5421]

CRealVolumeBuffer.At(index) retorna long do elemento de volume real. Proposta: validar faixa e atualização; acesso por índice não contém sozinho prova de sincronismo.

### REF-2768 — Refresh [REF, p.PDF 5422–5422]

CRealVolumeBuffer.Refresh atualiza buffer de volume real e retorna bool; false significa que não conseguiu atualizar. Proposta: não publicar valor antigo como fresco após falha.

### REF-2769 — RefreshCurrent [REF, p.PDF 5423–5423]

CRealVolumeBuffer.RefreshCurrent atualiza só elemento zero e retorna bool. Proposta: separar barra corrente mutável das fechadas e tratar false sem inferir novo valor.

### REF-2770 — CDoubleBuffer [REF, p.PDF 5424–5430]

CDoubleBuffer fornece acesso simplificado a dados double e base dos buffers OHLC/indicador, com armazenamento double; apoia-se em array tipado da biblioteca. Proposta Stoikus: manter semântica de unidade e verificar atualização antes da leitura.

### REF-2771 — Size [REF, p.PDF 5426–5426]

CDoubleBuffer.Size(int) define tamanho do buffer de dados double e base dos buffers OHLC/indicador; não comprova preenchimento. Proposta: dimensionar janela e atualizar antes de consumir.

### REF-2772 — SetSymbolPeriod [REF, p.PDF 5427–5427]

CDoubleBuffer.SetSymbolPeriod recebe símbolo string e ENUM_TIMEFRAMES para dados double e base dos buffers OHLC/indicador. Proposta: fixar origem dos dados e não misturar séries de instrumentos/períodos distintos.

### REF-2773 — At [REF, p.PDF 5428–5428]

CDoubleBuffer.At(index) retorna double do elemento de dados double e base dos buffers OHLC/indicador. Proposta: validar faixa e atualização; acesso por índice não contém sozinho prova de sincronismo.

### REF-2774 — Refresh [REF, p.PDF 5429–5429]

CDoubleBuffer.Refresh atualiza buffer de dados double e base dos buffers OHLC/indicador e retorna bool; false significa que não conseguiu atualizar. Proposta: não publicar valor antigo como fresco após falha.

### REF-2775 — RefreshCurrent [REF, p.PDF 5430–5430]

CDoubleBuffer.RefreshCurrent atualiza só elemento zero e retorna bool. Proposta: separar barra corrente mutável das fechadas e tratar false sem inferir novo valor.

### REF-2776 — COpenBuffer [REF, p.PDF 5431–5433]

COpenBuffer fornece acesso simplificado a preço de abertura, com armazenamento double; herda CDoubleBuffer. Proposta Stoikus: manter semântica de unidade e verificar atualização antes da leitura.

### REF-2777 — Refresh [REF, p.PDF 5432–5432]

COpenBuffer.Refresh atualiza buffer de preço de abertura e retorna bool; false significa que não conseguiu atualizar. Proposta: não publicar valor antigo como fresco após falha.

### REF-2778 — RefreshCurrent [REF, p.PDF 5433–5433]

COpenBuffer.RefreshCurrent atualiza só elemento zero e retorna bool. Proposta: separar barra corrente mutável das fechadas e tratar false sem inferir novo valor.

### REF-2779 — CHighBuffer [REF, p.PDF 5434–5436]

CHighBuffer fornece acesso simplificado a máxima da barra, com armazenamento double; herda CDoubleBuffer. Proposta Stoikus: manter semântica de unidade e verificar atualização antes da leitura.

### REF-2780 — Refresh [REF, p.PDF 5435–5435]

CHighBuffer.Refresh atualiza buffer de máxima da barra e retorna bool; false significa que não conseguiu atualizar. Proposta: não publicar valor antigo como fresco após falha.

### REF-2781 — RefreshCurrent [REF, p.PDF 5436–5436]

CHighBuffer.RefreshCurrent atualiza só elemento zero e retorna bool. Proposta: separar barra corrente mutável das fechadas e tratar false sem inferir novo valor.

### REF-2782 — CLowBuffer [REF, p.PDF 5437–5439]

CLowBuffer fornece acesso simplificado a mínima da barra, com armazenamento double; herda CDoubleBuffer. Proposta Stoikus: manter semântica de unidade e verificar atualização antes da leitura.

### REF-2783 — Refresh [REF, p.PDF 5438–5438]

CLowBuffer.Refresh atualiza buffer de mínima da barra e retorna bool; false significa que não conseguiu atualizar. Proposta: não publicar valor antigo como fresco após falha.

### REF-2784 — RefreshCurrent [REF, p.PDF 5439–5439]

CLowBuffer.RefreshCurrent atualiza só elemento zero e retorna bool. Proposta: separar barra corrente mutável das fechadas e tratar false sem inferir novo valor.

### REF-2785 — CCloseBuffer [REF, p.PDF 5440–5442]

CCloseBuffer fornece acesso simplificado a preço de fechamento, com armazenamento double; herda CDoubleBuffer. Proposta Stoikus: manter semântica de unidade e verificar atualização antes da leitura.

### REF-2786 — Refresh [REF, p.PDF 5441–5441]

CCloseBuffer.Refresh atualiza buffer de preço de fechamento e retorna bool; false significa que não conseguiu atualizar. Proposta: não publicar valor antigo como fresco após falha.

### REF-2787 — RefreshCurrent [REF, p.PDF 5442–5442]

CCloseBuffer.RefreshCurrent atualiza só elemento zero e retorna bool. Proposta: separar barra corrente mutável das fechadas e tratar false sem inferir novo valor.

### REF-2788 — CIndicatorBuffer [REF, p.PDF 5443–5449]

CIndicatorBuffer fornece acesso simplificado a buffer de indicador técnico, com armazenamento double; herda CDoubleBuffer. Proposta Stoikus: manter semântica de unidade e verificar atualização antes da leitura.

### REF-2789 — Offset [REF, p.PDF 5445–5445]

CIndicatorBuffer.Offset int get/set guarda deslocamento do buffer. Proposta: documentar alinhamento temporal antes de comparar linhas.

### REF-2790 — Name [REF, p.PDF 5446–5446]

CIndicatorBuffer.Name string get/set identifica buffer. Proposta: nome legível e estável em diagnóstico.

### REF-2791 — At [REF, p.PDF 5447–5447]

CIndicatorBuffer.At(index) retorna double do elemento de buffer de indicador técnico. Proposta: validar faixa e atualização; acesso por índice não contém sozinho prova de sincronismo.

### REF-2792 — Refresh [REF, p.PDF 5448–5448]

CIndicatorBuffer.Refresh atualiza todo o buffer de indicador com handle e número do buffer e retorna bool; false significa que não conseguiu atualizar. Proposta: não publicar valor antigo como fresco após falha.

### REF-2793 — RefreshCurrent [REF, p.PDF 5449–5449]

CIndicatorBuffer.RefreshCurrent atualiza só elemento zero com handle e número de buffer e retorna bool. Proposta: separar barra corrente mutável das fechadas e tratar false sem inferir novo valor.

### REF-2794 — CSeries [REF, p.PDF 5450–5461]

CSeries herda CArrayObj e expõe identidade, buffers, período e refresh para séries/indicadores. Proposta: capturar símbolo/período e quantidade disponível junto a cada diagnóstico.

### REF-2795 — Name [REF, p.PDF 5452–5452]

CSeries.Name retorna nome de série/indicador string. Proposta: compor identidade com símbolo e período, sem depender só do nome.

### REF-2796 — BuffersTotal [REF, p.PDF 5453–5453]

CSeries.BuffersTotal retorna int; série temporal tem apenas um buffer. Proposta: validar número de linha ao consumir indicador multibuffer.

### REF-2797 — Timeframe [REF, p.PDF 5454–5454]

CSeries.Timeframe retorna int de flags formadas como visibilidade de objetos. Proposta: não confundir esse bitmask com ENUM_TIMEFRAMES retornado por Period.

### REF-2798 — Symbol [REF, p.PDF 5455–5455]

CSeries.Symbol retorna string de instrumento. Proposta: validar fonte contra símbolo esperado no diagnóstico Stoikus.

### REF-2799 — Period [REF, p.PDF 5456–5456]

CSeries.Period retorna ENUM_TIMEFRAMES. Proposta: manter período concreto separado das flags de atualização.

### REF-2800 — RefreshCurrent [REF, p.PDF 5457–5457]

CSeries.RefreshCurrent(bool flag) configura atualização constante de valores correntes; texto imprime retorno string mas declara None. Proposta: não tratar como RefreshCurrent bool dos buffers; verificar header.

### REF-2801 — BufferSize [REF, p.PDF 5458–5458]

CSeries.BufferSize retorna int de dados disponíveis no buffer. Proposta: exigir janela suficiente, distinta de alocação pretendida.

### REF-2802 — BufferResize [REF, p.PDF 5459–5459]

CSeries.BufferResize(size) virtual bool define mesmo tamanho para todos os buffers. Proposta: tratar falha e conferir dados realmente disponíveis.

### REF-2803 — Refresh [REF, p.PDF 5460–5460]

CSeries.Refresh(flags) virtual void usa flags de timeframe para atualizar série/indicador. Proposta: atualizar fontes coerentes antes de análise multissérie.

### REF-2804 — PeriodDescription [REF, p.PDF 5461–5461]

CSeries.PeriodDescription(val=0) traduz timeframe; zero/omissão usa período da própria série. Proposta: rótulos explícitos no diagnóstico sem substituir enum interno.

### REF-2805 — CPriceSeries [REF, p.PDF 5462–5470]

CPriceSeries fornece acesso a preços, refresh e extremos por intervalo. Proposta: delimitar janela e sentinelas antes de usar extremos em análise; não cria regra de trading.

### REF-2806 — BufferResize [REF, p.PDF 5464–5464]

CPriceSeries.BufferResize(size) imprime virtual void, mas Return Value diz true/false. Proposta: divergência documental a resolver no header; não inventar verificação bool.

### REF-2807 — GetData [REF, p.PDF 5465–5465]

CPriceSeries.GetData(index) retorna double ou EMPTY_VALUE. Proposta: recusar sentinela antes de extremos/aritmética e verificar atualização.

### REF-2808 — Refresh [REF, p.PDF 5466–5466]

CPriceSeries.Refresh(flags=OBJ_ALL_PERIODS) virtual void atualiza série de preço. Proposta: não usar retorno como confirmação; conferir tamanho e tempos.

### REF-2809 — MinIndex [REF, p.PDF 5467–5467]

CPriceSeries.MinIndex(start,count) retorna índice mínimo ou -1. Proposta: validar janela e tratar ausência sem usar -1 como índice.

### REF-2810 — MinValue [REF, p.PDF 5468–5468]

CPriceSeries.MinValue(start,count,index&) retorna menor double ou EMPTY_VALUE e escreve índice por referência. Proposta: conferir valor e índice antes de aplicar a diagnóstico.

### REF-2811 — MaxIndex [REF, p.PDF 5469–5469]

CPriceSeries.MaxIndex(start,count) retorna índice máximo ou -1. Proposta: limites explícitos da janela e tratamento de falha.

### REF-2812 — MaxValue [REF, p.PDF 5470–5470]

CPriceSeries.MaxValue(start,count,index&) retorna maior double ou EMPTY_VALUE e índice por referência. Proposta: preservar janela e sentinela na evidência.

### REF-2813 — CIndicator [REF, p.PDF 5471–5491]

CIndicator adiciona handle, status, criação, buffers, leitura, extremos e vínculo ao chart. Proposta: separar criação, cálculo disponível, refresh e consumo; handle existente não prova dado pronto.

### REF-2814 — Handle [REF, p.PDF 5473–5473]

CIndicator.Handle retorna int identificador do indicador. Proposta: rastrear ownership; handle não prova BarsCalculated nem dado fresco.

### REF-2815 — Status [REF, p.PDF 5474–5474]

CIndicator.Status retorna string do estado de criação. Proposta: registrar contexto de falha, sem usar descrição como evidência de execução correta.

### REF-2816 — FullRelease [REF, p.PDF 5475–5475]

CIndicator.FullRelease(flag=true) configura liberação do handle. Proposta: definir proprietário e ciclo de vida, especialmente se handles forem compartilhados.

### REF-2817 — Create [REF, p.PDF 5476–5476]

CIndicator.Create(symbol,period,type,num_params,MqlParam[]) retorna bool; parâmetros e ENUM_INDICATOR explícitos. Proposta: validar tipos/contagem e tratar criação separada de cálculo.

### REF-2818 — BufferResize [REF, p.PDF 5477–5477]

CIndicator.BufferResize(size) virtual bool redimensiona todos os buffers igualmente. Proposta: exigir retorno e dados calculados antes do consumo.

### REF-2819 — BarsCalculated [REF, p.PDF 5478–5478]

CIndicator.BarsCalculated retorna quantidade calculada ou -1 por erro/dado ainda não calculado. Proposta: bloquear análise até janela suficiente e registrar estado não pronto.

### REF-2820 — GetData [REF, p.PDF 5479–5481]

CIndicator.GetData escalar exige Refresh recente e retorna valor/EMPTY_VALUE; cópias por posição, tempo+quantidade ou intervalo retornam número recebido ou -1. Proposta: distinguir falha, cópia parcial e dado válido; p.5481 só contém cabeçalho/rodapé.

### REF-2821 — Refresh [REF, p.PDF 5482–5482]

CIndicator.Refresh(flags=OBJ_ALL_PERIODS) virtual void recomendado antes de GetData. Proposta: ordem explícita refresh→verificação→consumo, sem inventar bool de sucesso.

### REF-2822 — Minimum [REF, p.PDF 5483–5483]

CIndicator.Minimum(buffer_num,start,count) retorna índice do mínimo no buffer indicado. Proposta: não misturar índice de linha com índice de barra; validar faixa.

### REF-2823 — MinValue [REF, p.PDF 5484–5484]

CIndicator.MinValue(buffer_num,start,count,index&) retorna mínimo e escreve índice. Proposta: guardar ambos com janela/fonte para auditoria.

### REF-2824 — Maximum [REF, p.PDF 5485–5485]

CIndicator.Maximum(buffer_num,start,count) retorna índice máximo. Proposta: buffer e janela explícitos, sem ampliar retrospectivamente amostra.

### REF-2825 — MaxValue [REF, p.PDF 5486–5486]

CIndicator.MaxValue(buffer_num,start,count,index&) retorna máximo e índice por referência. Proposta: preservar vínculo com o buffer correto.

### REF-2826 — MethodDescription [REF, p.PDF 5487–5487]

CIndicator.MethodDescription converte ENUM_MA_METHOD para string. Proposta: legendar método sem perder enum usado no cálculo.

### REF-2827 — PriceDescription [REF, p.PDF 5488–5488]

CIndicator.PriceDescription converte ENUM_APPLIED_PRICE para string. Proposta: documentar preço aplicado sem confundir com handle em APIs que aceitam ambos.

### REF-2828 — VolumeDescription [REF, p.PDF 5489–5489]

CIndicator.VolumeDescription converte ENUM_APPLIED_VOLUME para string. Proposta: explicitar real/tick no diagnóstico.

### REF-2829 — AddToChart [REF, p.PDF 5490–5490]

CIndicator.AddToChart(chart,subwin) retorna bool. Proposta: tratar falha de exibição separada de cálculo e de qualquer conclusão estratégica.

### REF-2830 — DeleteFromChart [REF, p.PDF 5491–5491]

CIndicator.DeleteFromChart(chart,subwin) retorna bool de remoção. Proposta: não equiparar remover visualização à liberação do handle.

### REF-2831 — CIndicators [REF, p.PDF 5492–5494]

CIndicators coleção administra instâncias, sincronização, handles e memória. Proposta: alternativa arquitetural futura para coordenar fontes; nenhuma substituição de código Stoikus foi feita.

### REF-2832 — Create [REF, p.PDF 5493–5493]

CIndicators.Create retorna CIndicator* ou NULL e recebe símbolo/período/tipo/contagem/parâmetros; declaração imprime referência params sem []. Proposta: verificar header e tratar NULL antes do uso.

### REF-2833 — Refresh [REF, p.PDF 5494–5494]

CIndicators.Refresh atualiza todas as séries/indicadores da coleção e retorna flags dos timeframes atualizados, formadas como visibilidade de objetos. Proposta: interpretar máscara, não como quantidade nem bool simples.

### REF-2834 — Timeseries classes [REF, p.PDF 5495–5543]

Classes de séries distinguem spread, horário de abertura, tick volume, volume real e OHLC. Proposta: manter tipo/unidade e mesma janela temporal, sem tratar volume tick como volume real.

### REF-2835 — CiSpread [REF, p.PDF 5496–5502]

CiSpread encapsula spread histórico e herda CSeries. Proposta Stoikus: identificar símbolo/período e checar cópia efetiva antes de analisar spread histórico; uso futuro não implementado.

### REF-2836 — Create [REF, p.PDF 5498–5498]

CiSpread.Create(symbol,period) retorna bool de criação para spread histórico. Proposta: falha impede consumo como fonte válida; criação não equivale à série atualizada.

### REF-2837 — BufferResize [REF, p.PDF 5499–5499]

CiSpread.BufferResize(int size) define janela do buffer de spread histórico; assinatura publicada void. Proposta: conferir BufferSize e número copiado, sem supor preenchimento por redimensionar.

### REF-2838 — GetData [REF, p.PDF 5500–5501]

CiSpread.GetData oferece cópia de spread histórico por posição+contagem, tempo inicial+contagem ou intervalo temporal; retorno >=0 é quantidade/sucesso e -1 é falha. Proposta: exigir quantidade solicitada e alinhar timestamps, sem aceitar cópia parcial silenciosamente. Acesso escalar documenta int ou zero; zero requer interpretação de disponibilidade, não substituição automática por dado válido.

### REF-2839 — Refresh [REF, p.PDF 5502–5502]

CiSpread.Refresh(int flags) atualiza spread histórico por flags de timeframe, sem retorno bool publicado. Proposta: conferir disponibilidade/tempo dos dados após chamada.

### REF-2840 — CiTime [REF, p.PDF 5503–5509]

CiTime encapsula horários de abertura e herda CSeries. Proposta Stoikus: identificar símbolo/período e checar cópia efetiva antes de analisar horários de abertura; uso futuro não implementado.

### REF-2841 — Create [REF, p.PDF 5505–5505]

CiTime.Create(symbol,period) retorna bool de criação para horários de abertura. Proposta: falha impede consumo como fonte válida; criação não equivale à série atualizada.

### REF-2842 — BufferResize [REF, p.PDF 5506–5506]

CiTime.BufferResize(int size) define janela do buffer de horários de abertura; assinatura publicada void. Proposta: conferir BufferSize e número copiado, sem supor preenchimento por redimensionar.

### REF-2843 — GetData [REF, p.PDF 5507–5508]

CiTime.GetData oferece cópia de horários de abertura por posição+contagem, tempo inicial+contagem ou intervalo temporal; retorno >=0 é quantidade/sucesso e -1 é falha. Proposta: exigir quantidade solicitada e alinhar timestamps, sem aceitar cópia parcial silenciosamente. Acesso escalar documenta datetime ou zero; zero requer interpretação de disponibilidade, não substituição automática por dado válido.

### REF-2844 — Refresh [REF, p.PDF 5509–5509]

CiTime.Refresh(int flags) atualiza horários de abertura por flags de timeframe, sem retorno bool publicado. Proposta: conferir disponibilidade/tempo dos dados após chamada.

### REF-2845 — CiTickVolume [REF, p.PDF 5510–5516]

CiTickVolume encapsula volume de ticks e herda CSeries. Proposta Stoikus: identificar símbolo/período e checar cópia efetiva antes de analisar volume de ticks; uso futuro não implementado.

### REF-2846 — Create [REF, p.PDF 5512–5512]

CiTickVolume.Create(symbol,period) retorna bool de criação para volume de ticks. Proposta: falha impede consumo como fonte válida; criação não equivale à série atualizada.

### REF-2847 — BufferResize [REF, p.PDF 5513–5513]

CiTickVolume.BufferResize(int size) define janela do buffer de volume de ticks; assinatura publicada void. Proposta: conferir BufferSize e número copiado, sem supor preenchimento por redimensionar.

### REF-2848 — GetData [REF, p.PDF 5514–5515]

CiTickVolume.GetData oferece cópia de volume de ticks por posição+contagem, tempo inicial+contagem ou intervalo temporal; retorno >=0 é quantidade/sucesso e -1 é falha. Proposta: exigir quantidade solicitada e alinhar timestamps, sem aceitar cópia parcial silenciosamente. Acesso escalar documenta long ou zero; zero requer interpretação de disponibilidade, não substituição automática por dado válido.

### REF-2849 — Refresh [REF, p.PDF 5516–5516]

CiTickVolume.Refresh(int flags) atualiza volume de ticks por flags de timeframe, sem retorno bool publicado. Proposta: conferir disponibilidade/tempo dos dados após chamada.

### REF-2850 — CiRealVolume [REF, p.PDF 5517–5523]

CiRealVolume encapsula volume real e herda CSeries. Proposta Stoikus: identificar símbolo/período e checar cópia efetiva antes de analisar volume real; uso futuro não implementado.

### REF-2851 — Create [REF, p.PDF 5519–5519]

CiRealVolume.Create(symbol,period) retorna bool de criação para volume real. Proposta: falha impede consumo como fonte válida; criação não equivale à série atualizada.

### REF-2852 — BufferResize [REF, p.PDF 5520–5520]

CiRealVolume.BufferResize(int size) define janela do buffer de volume real; assinatura publicada void. Proposta: conferir BufferSize e número copiado, sem supor preenchimento por redimensionar.

### REF-2853 — GetData [REF, p.PDF 5521–5522]

CiRealVolume.GetData oferece cópia de volume real por posição+contagem, tempo inicial+contagem ou intervalo temporal; retorno >=0 é quantidade/sucesso e -1 é falha. Proposta: exigir quantidade solicitada e alinhar timestamps, sem aceitar cópia parcial silenciosamente. Acesso escalar documenta long ou zero; zero requer interpretação de disponibilidade, não substituição automática por dado válido. Divergência: p.5521 imprime datetime no escalar embora classe seja volume real e cópias usem long. Resolver no header antes de codificar.

### REF-2854 — Refresh [REF, p.PDF 5523–5523]

CiRealVolume.Refresh(int flags) atualiza volume real por flags de timeframe, sem retorno bool publicado. Proposta: conferir disponibilidade/tempo dos dados após chamada.

### REF-2855 — CiOpen [REF, p.PDF 5524–5528]

CiOpen encapsula abertura OHLC e herda CPriceSeries. Proposta Stoikus: identificar símbolo/período e checar cópia efetiva antes de analisar abertura OHLC; uso futuro não implementado.

### REF-2856 — Create [REF, p.PDF 5526–5526]

CiOpen.Create(symbol,period) retorna bool de criação para abertura OHLC. Proposta: falha impede consumo como fonte válida; criação não equivale à série atualizada.

### REF-2857 — GetData [REF, p.PDF 5527–5528]

CiOpen.GetData oferece cópia de abertura OHLC por posição+contagem, tempo inicial+contagem ou intervalo temporal; retorno >=0 é quantidade/sucesso e -1 é falha. Proposta: exigir quantidade solicitada e alinhar timestamps, sem aceitar cópia parcial silenciosamente.

### REF-2858 — CiHigh [REF, p.PDF 5529–5533]

CiHigh encapsula máxima OHLC e herda CPriceSeries. Proposta Stoikus: identificar símbolo/período e checar cópia efetiva antes de analisar máxima OHLC; uso futuro não implementado.

### REF-2859 — Create [REF, p.PDF 5531–5531]

CiHigh.Create(symbol,period) retorna bool de criação para máxima OHLC. Proposta: falha impede consumo como fonte válida; criação não equivale à série atualizada.

### REF-2860 — GetData [REF, p.PDF 5532–5533]

CiHigh.GetData oferece cópia de máxima OHLC por posição+contagem, tempo inicial+contagem ou intervalo temporal; retorno >=0 é quantidade/sucesso e -1 é falha. Proposta: exigir quantidade solicitada e alinhar timestamps, sem aceitar cópia parcial silenciosamente.

### REF-2861 — CiLow [REF, p.PDF 5534–5538]

CiLow encapsula mínima OHLC e herda CPriceSeries. Proposta Stoikus: identificar símbolo/período e checar cópia efetiva antes de analisar mínima OHLC; uso futuro não implementado.

### REF-2862 — Create [REF, p.PDF 5536–5536]

CiLow.Create(symbol,period) retorna bool de criação para mínima OHLC. Proposta: falha impede consumo como fonte válida; criação não equivale à série atualizada.

### REF-2863 — GetData [REF, p.PDF 5537–5538]

CiLow.GetData oferece cópia de mínima OHLC por posição+contagem, tempo inicial+contagem ou intervalo temporal; retorno >=0 é quantidade/sucesso e -1 é falha. Proposta: exigir quantidade solicitada e alinhar timestamps, sem aceitar cópia parcial silenciosamente.

### REF-2864 — CiClose [REF, p.PDF 5539–5543]

CiClose encapsula fechamento OHLC e herda CPriceSeries. Proposta Stoikus: identificar símbolo/período e checar cópia efetiva antes de analisar fechamento OHLC; uso futuro não implementado.

### REF-2865 — Create [REF, p.PDF 5541–5541]

CiClose.Create(symbol,period) retorna bool de criação para fechamento OHLC. Proposta: falha impede consumo como fonte válida; criação não equivale à série atualizada.

### REF-2866 — GetData [REF, p.PDF 5542–5543]

CiClose.GetData oferece cópia de fechamento OHLC por posição+contagem, tempo inicial+contagem ou intervalo temporal; retorno >=0 é quantidade/sucesso e -1 é falha. Proposta: exigir quantidade solicitada e alinhar timestamps, sem aceitar cópia parcial silenciosamente.

### REF-2867 — Trend Indicators [REF, p.PDF 5544–5662]

Trend reúne ADX/ADXWilder, Bands, Envelopes, Ichimoku, MA, SAR, StdDev e médias adaptativas. Proposta: referências de infraestrutura analítica; disponibilidade de indicador não autoriza novo sinal Stoikus.

### REF-2868 — CiADX [REF, p.PDF 5545–5552]

CiADX herda CIndicator e oferece criação/configuração/acesso a Average Directional Index; parâmetros próprios: ma_period, além de símbolo/timeframe. Proposta Stoikus: fonte analítica experimental com estado e tempo explícitos, sem inferir regra estratégica ou eficácia.

### REF-2869 — MaPeriod [REF, p.PDF 5547–5547]

CiADX.MaPeriod consulta período de média definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Average Directional Index; getter não reconfigura o indicador.

### REF-2870 — Create [REF, p.PDF 5548–5548]

CiADX.Create recebe símbolo/timeframe e ma_period; retorna bool e recomenda Refresh/GetData para valores. Proposta: registrar configuração completa e falha de criação, sem assumir disponibilidade imediata.

### REF-2871 — Main [REF, p.PDF 5549–5549]

CiADX.Main(index) retorna double da linha principal, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2872 — Plus [REF, p.PDF 5550–5550]

CiADX.Plus(index) retorna double da linha +DI, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2873 — Minus [REF, p.PDF 5551–5551]

CiADX.Minus(index) retorna double da linha -DI, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2874 — Type [REF, p.PDF 5552–5552]

CiADX.Type() virtual int identifica IND_ADX. Proposta: usar identidade de indicador no diagnóstico, distinta de evidência de cálculo ou qualidade estratégica.

### REF-2875 — CiADXWilder [REF, p.PDF 5553–5560]

CiADXWilder herda CIndicator e oferece criação/configuração/acesso a ADX por Welles Wilder; parâmetros próprios: ma_period, além de símbolo/timeframe. Proposta Stoikus: fonte analítica experimental com estado e tempo explícitos, sem inferir regra estratégica ou eficácia.

### REF-2876 — MaPeriod [REF, p.PDF 5555–5555]

CiADXWilder.MaPeriod consulta período de média definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de ADX por Welles Wilder; getter não reconfigura o indicador.

### REF-2877 — Create [REF, p.PDF 5556–5556]

CiADXWilder.Create recebe símbolo/timeframe e ma_period; retorna bool e recomenda Refresh/GetData para valores. Proposta: registrar configuração completa e falha de criação, sem assumir disponibilidade imediata.

### REF-2878 — Main [REF, p.PDF 5557–5557]

CiADXWilder.Main(index) retorna double da linha principal, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2879 — Plus [REF, p.PDF 5558–5558]

CiADXWilder.Plus(index) retorna double da linha +DI, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2880 — Minus [REF, p.PDF 5559–5559]

CiADXWilder.Minus(index) retorna double da linha -DI, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2881 — Type [REF, p.PDF 5560–5560]

CiADXWilder.Type() virtual int identifica IND_ADXW. Proposta: usar identidade de indicador no diagnóstico, distinta de evidência de cálculo ou qualidade estratégica.

### REF-2882 — CiBands [REF, p.PDF 5561–5571]

CiBands herda CIndicator e oferece criação/configuração/acesso a Bollinger Bands; parâmetros próprios: ma_period, ma_shift, deviation, applied, além de símbolo/timeframe. Proposta Stoikus: fonte analítica experimental com estado e tempo explícitos, sem inferir regra estratégica ou eficácia.

### REF-2883 — MaPeriod [REF, p.PDF 5563–5563]

CiBands.MaPeriod consulta período de média definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Bollinger Bands; getter não reconfigura o indicador.

### REF-2884 — MaShift [REF, p.PDF 5564–5564]

CiBands.MaShift consulta deslocamento horizontal definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Bollinger Bands; getter não reconfigura o indicador.

### REF-2885 — Deviation [REF, p.PDF 5565–5565]

CiBands.Deviation consulta desvio definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Bollinger Bands; getter não reconfigura o indicador.

### REF-2886 — Applied [REF, p.PDF 5566–5566]

CiBands.Applied consulta preço ou handle aplicado definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Bollinger Bands; getter não reconfigura o indicador.

### REF-2887 — Create [REF, p.PDF 5567–5567]

CiBands.Create recebe símbolo/timeframe e ma_period, ma_shift, deviation, applied; retorna bool e recomenda Refresh/GetData para valores. Proposta: registrar configuração completa e falha de criação, sem assumir disponibilidade imediata.

### REF-2888 — Base [REF, p.PDF 5568–5568]

CiBands.Base(index) retorna double da linha base, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2889 — Upper [REF, p.PDF 5569–5569]

CiBands.Upper(index) retorna double da linha superior, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2890 — Lower [REF, p.PDF 5570–5570]

CiBands.Lower(index) retorna double da linha inferior, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2891 — Type [REF, p.PDF 5571–5571]

CiBands.Type() virtual int identifica IND_BANDS. Proposta: usar identidade de indicador no diagnóstico, distinta de evidência de cálculo ou qualidade estratégica.

### REF-2892 — CiEnvelopes [REF, p.PDF 5572–5582]

CiEnvelopes herda CIndicator e oferece criação/configuração/acesso a Envelopes; parâmetros próprios: ma_period, ma_shift, ma_method, applied, deviation, além de símbolo/timeframe. Proposta Stoikus: fonte analítica experimental com estado e tempo explícitos, sem inferir regra estratégica ou eficácia.

### REF-2893 — MaPeriod [REF, p.PDF 5574–5574]

CiEnvelopes.MaPeriod consulta período de média definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Envelopes; getter não reconfigura o indicador.

### REF-2894 — MaShift [REF, p.PDF 5575–5575]

CiEnvelopes.MaShift consulta deslocamento horizontal definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Envelopes; getter não reconfigura o indicador.

### REF-2895 — MaMethod [REF, p.PDF 5576–5576]

CiEnvelopes.MaMethod consulta método ENUM_MA_METHOD definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Envelopes; getter não reconfigura o indicador.

### REF-2896 — Deviation [REF, p.PDF 5577–5577]

CiEnvelopes.Deviation consulta desvio definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Envelopes; getter não reconfigura o indicador.

### REF-2897 — Applied [REF, p.PDF 5578–5578]

CiEnvelopes.Applied consulta preço ou handle aplicado definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Envelopes; getter não reconfigura o indicador.

### REF-2898 — Create [REF, p.PDF 5579–5579]

CiEnvelopes.Create recebe símbolo/timeframe e ma_period, ma_shift, ma_method, applied, deviation; retorna bool e recomenda Refresh/GetData para valores. Proposta: registrar configuração completa e falha de criação, sem assumir disponibilidade imediata.

### REF-2899 — Upper [REF, p.PDF 5580–5580]

CiEnvelopes.Upper(index) retorna double da linha superior, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2900 — Lower [REF, p.PDF 5581–5581]

CiEnvelopes.Lower(index) retorna double da linha inferior, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2901 — Type [REF, p.PDF 5582–5582]

CiEnvelopes.Type() virtual int identifica IND_ENVELOPES. Proposta: usar identidade de indicador no diagnóstico, distinta de evidência de cálculo ou qualidade estratégica.

### REF-2902 — CiIchimoku [REF, p.PDF 5583–5594]

CiIchimoku herda CIndicator e oferece criação/configuração/acesso a Ichimoku Kinko Hyo; parâmetros próprios: tenkan_sen, kijun_sen, senkou_span_b, além de símbolo/timeframe. Proposta Stoikus: fonte analítica experimental com estado e tempo explícitos, sem inferir regra estratégica ou eficácia.

### REF-2903 — TenkanSenPeriod [REF, p.PDF 5585–5585]

CiIchimoku.TenkanSenPeriod consulta período TenkanSen definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Ichimoku Kinko Hyo; getter não reconfigura o indicador.

### REF-2904 — KijunSenPeriod [REF, p.PDF 5586–5586]

CiIchimoku.KijunSenPeriod consulta período KijunSen definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Ichimoku Kinko Hyo; getter não reconfigura o indicador.

### REF-2905 — SenkouSpanBPeriod [REF, p.PDF 5587–5587]

CiIchimoku.SenkouSpanBPeriod consulta período SenkouSpanB definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Ichimoku Kinko Hyo; getter não reconfigura o indicador.

### REF-2906 — Create [REF, p.PDF 5588–5588]

CiIchimoku.Create recebe símbolo/timeframe e tenkan_sen, kijun_sen, senkou_span_b; retorna bool e recomenda Refresh/GetData para valores. Proposta: registrar configuração completa e falha de criação, sem assumir disponibilidade imediata.

### REF-2907 — TenkanSen [REF, p.PDF 5589–5589]

CiIchimoku.TenkanSen(index) retorna double da linha TenkanSen, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado. Estas páginas descrevem índice de buffer, sem justificar alinhamento causal de deslocamentos; conferir antes de comparar linhas.

### REF-2908 — KijunSen [REF, p.PDF 5590–5590]

CiIchimoku.KijunSen(index) retorna double da linha KijunSen, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado. Estas páginas descrevem índice de buffer, sem justificar alinhamento causal de deslocamentos; conferir antes de comparar linhas.

### REF-2909 — SenkouSpanA [REF, p.PDF 5591–5591]

CiIchimoku.SenkouSpanA(index) retorna double da linha SenkouSpanA, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado. Estas páginas descrevem índice de buffer, sem justificar alinhamento causal de deslocamentos; conferir antes de comparar linhas.

### REF-2910 — SenkouSpanB [REF, p.PDF 5592–5592]

CiIchimoku.SenkouSpanB(index) retorna double da linha SenkouSpanB, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado. Estas páginas descrevem índice de buffer, sem justificar alinhamento causal de deslocamentos; conferir antes de comparar linhas.

### REF-2911 — ChinkouSpan [REF, p.PDF 5593–5593]

CiIchimoku.ChinkouSpan(index) retorna double da linha ChinkouSpan, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado. Estas páginas descrevem índice de buffer, sem justificar alinhamento causal de deslocamentos; conferir antes de comparar linhas.

### REF-2912 — Type [REF, p.PDF 5594–5594]

CiIchimoku.Type() virtual int identifica IND_ICHIMOKU. Proposta: usar identidade de indicador no diagnóstico, distinta de evidência de cálculo ou qualidade estratégica.

### REF-2913 — CiMA [REF, p.PDF 5595–5603]

CiMA herda CIndicator e oferece criação/configuração/acesso a Moving Average; parâmetros próprios: ma_period, ma_shift, ma_method, applied, além de símbolo/timeframe. Proposta Stoikus: fonte analítica experimental com estado e tempo explícitos, sem inferir regra estratégica ou eficácia.

### REF-2914 — MaPeriod [REF, p.PDF 5597–5597]

CiMA.MaPeriod consulta período de média definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Moving Average; getter não reconfigura o indicador.

### REF-2915 — MaShift [REF, p.PDF 5598–5598]

CiMA.MaShift consulta deslocamento horizontal definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Moving Average; getter não reconfigura o indicador.

### REF-2916 — MaMethod [REF, p.PDF 5599–5599]

CiMA.MaMethod consulta método ENUM_MA_METHOD definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Moving Average; getter não reconfigura o indicador.

### REF-2917 — Applied [REF, p.PDF 5600–5600]

CiMA.Applied consulta preço ou handle aplicado definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Moving Average; getter não reconfigura o indicador.

### REF-2918 — Create [REF, p.PDF 5601–5601]

CiMA.Create recebe símbolo/timeframe e ma_period, ma_shift, ma_method, applied; retorna bool e recomenda Refresh/GetData para valores. Proposta: registrar configuração completa e falha de criação, sem assumir disponibilidade imediata. Texto usa nome de parâmetro string string; verificar assinatura no header antes de código original.

### REF-2919 — Main [REF, p.PDF 5602–5602]

CiMA.Main(index) retorna double da linha principal, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2920 — Type [REF, p.PDF 5603–5603]

CiMA.Type() virtual int identifica IND_MA. Proposta: usar identidade de indicador no diagnóstico, distinta de evidência de cálculo ou qualidade estratégica.

### REF-2921 — CiSAR [REF, p.PDF 5604–5610]

CiSAR herda CIndicator e oferece criação/configuração/acesso a Parabolic Stop And Reverse; parâmetros próprios: step, maximum, além de símbolo/timeframe. Proposta Stoikus: fonte analítica experimental com estado e tempo explícitos, sem inferir regra estratégica ou eficácia.

### REF-2922 — SarStep [REF, p.PDF 5606–5606]

CiSAR.SarStep consulta passo de aceleração de preço definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Parabolic Stop And Reverse; getter não reconfigura o indicador.

### REF-2923 — Maximum [REF, p.PDF 5607–5607]

CiSAR.Maximum consulta limite máximo do passo SAR definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Parabolic Stop And Reverse; getter não reconfigura o indicador.

### REF-2924 — Create [REF, p.PDF 5608–5608]

CiSAR.Create recebe símbolo/timeframe e step, maximum; retorna bool e recomenda Refresh/GetData para valores. Proposta: registrar configuração completa e falha de criação, sem assumir disponibilidade imediata.

### REF-2925 — Main [REF, p.PDF 5609–5609]

CiSAR.Main(index) retorna double da linha principal, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2926 — Type [REF, p.PDF 5610–5610]

CiSAR.Type() virtual int identifica IND_SAR. Proposta: usar identidade de indicador no diagnóstico, distinta de evidência de cálculo ou qualidade estratégica.

### REF-2927 — CiStdDev [REF, p.PDF 5611–5619]

CiStdDev herda CIndicator e oferece criação/configuração/acesso a Standard Deviation; parâmetros próprios: ma_period, ma_shift, ma_method, applied, além de símbolo/timeframe. Proposta Stoikus: fonte analítica experimental com estado e tempo explícitos, sem inferir regra estratégica ou eficácia.

### REF-2928 — MaPeriod [REF, p.PDF 5613–5613]

CiStdDev.MaPeriod consulta período de média definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Standard Deviation; getter não reconfigura o indicador.

### REF-2929 — MaShift [REF, p.PDF 5614–5614]

CiStdDev.MaShift consulta deslocamento horizontal definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Standard Deviation; getter não reconfigura o indicador.

### REF-2930 — MaMethod [REF, p.PDF 5615–5615]

CiStdDev.MaMethod consulta método ENUM_MA_METHOD definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Standard Deviation; getter não reconfigura o indicador.

### REF-2931 — Applied [REF, p.PDF 5616–5616]

CiStdDev.Applied consulta preço ou handle aplicado definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Standard Deviation; getter não reconfigura o indicador.

### REF-2932 — Create [REF, p.PDF 5617–5617]

CiStdDev.Create recebe símbolo/timeframe e ma_period, ma_shift, ma_method, applied; retorna bool e recomenda Refresh/GetData para valores. Proposta: registrar configuração completa e falha de criação, sem assumir disponibilidade imediata.

### REF-2933 — Main [REF, p.PDF 5618–5618]

CiStdDev.Main(index) retorna double da linha principal, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2934 — Type [REF, p.PDF 5619–5619]

CiStdDev.Type() virtual int identifica IND_STDDEV. Proposta: usar identidade de indicador no diagnóstico, distinta de evidência de cálculo ou qualidade estratégica.

### REF-2935 — CiDEMA [REF, p.PDF 5620–5627]

CiDEMA herda CIndicator e oferece criação/configuração/acesso a Double Exponential Moving Average; parâmetros próprios: ma_period, ind_shift, applied, além de símbolo/timeframe. Proposta Stoikus: fonte analítica experimental com estado e tempo explícitos, sem inferir regra estratégica ou eficácia.

### REF-2936 — MaPeriod [REF, p.PDF 5622–5622]

CiDEMA.MaPeriod consulta período de média definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Double Exponential Moving Average; getter não reconfigura o indicador.

### REF-2937 — IndShift [REF, p.PDF 5623–5623]

CiDEMA.IndShift consulta deslocamento horizontal definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Double Exponential Moving Average; getter não reconfigura o indicador.

### REF-2938 — Applied [REF, p.PDF 5624–5624]

CiDEMA.Applied consulta preço ou handle aplicado definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Double Exponential Moving Average; getter não reconfigura o indicador.

### REF-2939 — Create [REF, p.PDF 5625–5625]

CiDEMA.Create recebe símbolo/timeframe e ma_period, ind_shift, applied; retorna bool e recomenda Refresh/GetData para valores. Proposta: registrar configuração completa e falha de criação, sem assumir disponibilidade imediata. Texto usa nome de parâmetro string string; verificar assinatura no header antes de código original.

### REF-2940 — Main [REF, p.PDF 5626–5626]

CiDEMA.Main(index) retorna double da linha principal, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2941 — Type [REF, p.PDF 5627–5627]

CiDEMA.Type() virtual int identifica IND_DEMA. Proposta: usar identidade de indicador no diagnóstico, distinta de evidência de cálculo ou qualidade estratégica.

### REF-2942 — CiTEMA [REF, p.PDF 5628–5635]

CiTEMA herda CIndicator e oferece criação/configuração/acesso a Triple Exponential Moving Average; parâmetros próprios: ma_period, ma_shift, applied, além de símbolo/timeframe. Proposta Stoikus: fonte analítica experimental com estado e tempo explícitos, sem inferir regra estratégica ou eficácia.

### REF-2943 — MaPeriod [REF, p.PDF 5630–5630]

CiTEMA.MaPeriod consulta período de média definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Triple Exponential Moving Average; getter não reconfigura o indicador.

### REF-2944 — IndShift [REF, p.PDF 5631–5631]

CiTEMA.IndShift consulta deslocamento horizontal definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Triple Exponential Moving Average; getter não reconfigura o indicador.

### REF-2945 — Applied [REF, p.PDF 5632–5632]

CiTEMA.Applied consulta preço ou handle aplicado definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Triple Exponential Moving Average; getter não reconfigura o indicador.

### REF-2946 — Create [REF, p.PDF 5633–5633]

CiTEMA.Create recebe símbolo/timeframe e ma_period, ma_shift, applied; retorna bool e recomenda Refresh/GetData para valores. Proposta: registrar configuração completa e falha de criação, sem assumir disponibilidade imediata.

### REF-2947 — Main [REF, p.PDF 5634–5634]

CiTEMA.Main(index) retorna double da linha principal, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2948 — Type [REF, p.PDF 5635–5635]

CiTEMA.Type() virtual int identifica IND_TEMA. Proposta: usar identidade de indicador no diagnóstico, distinta de evidência de cálculo ou qualidade estratégica.

### REF-2949 — CiFrAMA [REF, p.PDF 5636–5643]

CiFrAMA herda CIndicator e oferece criação/configuração/acesso a Fractal Adaptive Moving Average; parâmetros próprios: ma_period, ma_shift, applied, além de símbolo/timeframe. Proposta Stoikus: fonte analítica experimental com estado e tempo explícitos, sem inferir regra estratégica ou eficácia.

### REF-2950 — MaPeriod [REF, p.PDF 5638–5638]

CiFrAMA.MaPeriod consulta período de média definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Fractal Adaptive Moving Average; getter não reconfigura o indicador.

### REF-2951 — IndShift [REF, p.PDF 5639–5639]

CiFrAMA.IndShift consulta deslocamento horizontal definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Fractal Adaptive Moving Average; getter não reconfigura o indicador.

### REF-2952 — Applied [REF, p.PDF 5640–5640]

CiFrAMA.Applied consulta preço ou handle aplicado definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Fractal Adaptive Moving Average; getter não reconfigura o indicador.

### REF-2953 — Create [REF, p.PDF 5641–5641]

CiFrAMA.Create recebe símbolo/timeframe e ma_period, ma_shift, applied; retorna bool e recomenda Refresh/GetData para valores. Proposta: registrar configuração completa e falha de criação, sem assumir disponibilidade imediata.

### REF-2954 — Main [REF, p.PDF 5642–5642]

CiFrAMA.Main(index) retorna double da linha principal, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2955 — Type [REF, p.PDF 5643–5643]

CiFrAMA.Type() virtual int identifica IND_FRAMA. Proposta: usar identidade de indicador no diagnóstico, distinta de evidência de cálculo ou qualidade estratégica.

### REF-2956 — CiAMA [REF, p.PDF 5644–5653]

CiAMA herda CIndicator e oferece criação/configuração/acesso a Adaptive Moving Average; parâmetros próprios: ma_period, fast_ema_period, slow_ema_period, ind_shift, applied, além de símbolo/timeframe. Proposta Stoikus: fonte analítica experimental com estado e tempo explícitos, sem inferir regra estratégica ou eficácia.

### REF-2957 — MaPeriod [REF, p.PDF 5646–5646]

CiAMA.MaPeriod consulta período de média definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Adaptive Moving Average; getter não reconfigura o indicador.

### REF-2958 — FastEmaPeriod [REF, p.PDF 5647–5647]

CiAMA.FastEmaPeriod consulta período da EMA rápida definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Adaptive Moving Average; getter não reconfigura o indicador.

### REF-2959 — SlowEmaPeriod [REF, p.PDF 5648–5648]

CiAMA.SlowEmaPeriod consulta período da EMA lenta definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Adaptive Moving Average; getter não reconfigura o indicador.

### REF-2960 — IndShift [REF, p.PDF 5649–5649]

CiAMA.IndShift consulta deslocamento horizontal definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Adaptive Moving Average; getter não reconfigura o indicador.

### REF-2961 — Applied [REF, p.PDF 5650–5650]

CiAMA.Applied consulta preço ou handle aplicado definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Adaptive Moving Average; getter não reconfigura o indicador.

### REF-2962 — Create [REF, p.PDF 5651–5651]

CiAMA.Create recebe símbolo/timeframe e ma_period, fast_ema_period, slow_ema_period, ind_shift, applied; retorna bool e recomenda Refresh/GetData para valores. Proposta: registrar configuração completa e falha de criação, sem assumir disponibilidade imediata. Texto usa nome de parâmetro string string; verificar assinatura no header antes de código original.

### REF-2963 — Main [REF, p.PDF 5652–5652]

CiAMA.Main(index) retorna double da linha principal, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2964 — Type [REF, p.PDF 5653–5653]

CiAMA.Type() virtual int identifica IND_AMA. Proposta: usar identidade de indicador no diagnóstico, distinta de evidência de cálculo ou qualidade estratégica.

### REF-2965 — CiVIDyA [REF, p.PDF 5654–5662]

CiVIDyA herda CIndicator e oferece criação/configuração/acesso a Variable Index Dynamic Average; parâmetros próprios: cmo_period, ema_period, ind_shift, applied, além de símbolo/timeframe. Proposta Stoikus: fonte analítica experimental com estado e tempo explícitos, sem inferir regra estratégica ou eficácia.

### REF-2966 — CmoPeriod [REF, p.PDF 5656–5656]

CiVIDyA.CmoPeriod consulta período de momentum definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Variable Index Dynamic Average; getter não reconfigura o indicador. Erro editorial explícito: p.5656 diz fechar gráfico; a síntese depende da tabela p.5654 e Create p.5660, não dessa descrição contraditória. Header/native continuam pendentes.

### REF-2967 — EmaPeriod [REF, p.PDF 5657–5657]

CiVIDyA.EmaPeriod consulta período de média EMA definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Variable Index Dynamic Average; getter não reconfigura o indicador. Erro editorial explícito: p.5657 diz retornar símbolo string apesar da assinatura int; a síntese depende da tabela p.5654 e Create p.5660, não dessa descrição contraditória. Header/native continuam pendentes.

### REF-2968 — IndShift [REF, p.PDF 5658–5658]

CiVIDyA.IndShift consulta deslocamento horizontal definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Variable Index Dynamic Average; getter não reconfigura o indicador.

### REF-2969 — Applied [REF, p.PDF 5659–5659]

CiVIDyA.Applied consulta preço ou handle aplicado definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Variable Index Dynamic Average; getter não reconfigura o indicador.

### REF-2970 — Create [REF, p.PDF 5660–5660]

CiVIDyA.Create recebe símbolo/timeframe e cmo_period, ema_period, ind_shift, applied; retorna bool e recomenda Refresh/GetData para valores. Proposta: registrar configuração completa e falha de criação, sem assumir disponibilidade imediata.

### REF-2971 — Main [REF, p.PDF 5661–5661]

CiVIDyA.Main(index) retorna double da linha principal, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2972 — Type [REF, p.PDF 5662–5662]

CiVIDyA.Type() virtual int identifica IND_VIDYA. Proposta: usar identidade de indicador no diagnóstico, distinta de evidência de cálculo ou qualidade estratégica.

### REF-2973 — Oscillators [REF, p.PDF 5663–5703]

Oscillators lista 15 classes; neste recorte apenas ATR, BearsPower, BullsPower, CCI, Chaikin e DeMarker foram lidos. Proposta: não atribuir leitura aos osciladores que continuam após p.5703.

### REF-2974 — CiATR [REF, p.PDF 5664–5669]

CiATR herda CIndicator e oferece criação/configuração/acesso a Average True Range; parâmetros próprios: ma_period, além de símbolo/timeframe. Proposta Stoikus: fonte analítica experimental com estado e tempo explícitos, sem inferir regra estratégica ou eficácia.

### REF-2975 — MaPeriod [REF, p.PDF 5666–5666]

CiATR.MaPeriod consulta período de média definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Average True Range; getter não reconfigura o indicador.

### REF-2976 — Create [REF, p.PDF 5667–5667]

CiATR.Create recebe símbolo/timeframe e ma_period; retorna bool e recomenda Refresh/GetData para valores. Proposta: registrar configuração completa e falha de criação, sem assumir disponibilidade imediata.

### REF-2977 — Main [REF, p.PDF 5668–5668]

CiATR.Main(index) retorna double da linha principal, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2978 — Type [REF, p.PDF 5669–5669]

CiATR.Type() virtual int identifica IND_ATR. Proposta: usar identidade de indicador no diagnóstico, distinta de evidência de cálculo ou qualidade estratégica.

### REF-2979 — CiBearsPower [REF, p.PDF 5670–5675]

CiBearsPower herda CIndicator e oferece criação/configuração/acesso a Bears Power; parâmetros próprios: ma_period, além de símbolo/timeframe. Proposta Stoikus: fonte analítica experimental com estado e tempo explícitos, sem inferir regra estratégica ou eficácia.

### REF-2980 — MaPeriod [REF, p.PDF 5672–5672]

CiBearsPower.MaPeriod consulta período de média definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Bears Power; getter não reconfigura o indicador.

### REF-2981 — Create [REF, p.PDF 5673–5673]

CiBearsPower.Create recebe símbolo/timeframe e ma_period; retorna bool e recomenda Refresh/GetData para valores. Proposta: registrar configuração completa e falha de criação, sem assumir disponibilidade imediata.

### REF-2982 — Main [REF, p.PDF 5674–5674]

CiBearsPower.Main(index) retorna double da linha principal, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2983 — Type [REF, p.PDF 5675–5675]

CiBearsPower.Type() virtual int identifica IND_BEARS. Proposta: usar identidade de indicador no diagnóstico, distinta de evidência de cálculo ou qualidade estratégica.

### REF-2984 — CiBullsPower [REF, p.PDF 5676–5681]

CiBullsPower herda CIndicator e oferece criação/configuração/acesso a Bulls Power; parâmetros próprios: ma_period, além de símbolo/timeframe. Proposta Stoikus: fonte analítica experimental com estado e tempo explícitos, sem inferir regra estratégica ou eficácia.

### REF-2985 — MaPeriod [REF, p.PDF 5678–5678]

CiBullsPower.MaPeriod consulta período de média definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Bulls Power; getter não reconfigura o indicador.

### REF-2986 — Create [REF, p.PDF 5679–5679]

CiBullsPower.Create recebe símbolo/timeframe e ma_period; retorna bool e recomenda Refresh/GetData para valores. Proposta: registrar configuração completa e falha de criação, sem assumir disponibilidade imediata.

### REF-2987 — Main [REF, p.PDF 5680–5680]

CiBullsPower.Main(index) retorna double da linha principal, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2988 — Type [REF, p.PDF 5681–5681]

CiBullsPower.Type() virtual int identifica IND_BULLS. Proposta: usar identidade de indicador no diagnóstico, distinta de evidência de cálculo ou qualidade estratégica.

### REF-2989 — CiCCI [REF, p.PDF 5682–5688]

CiCCI herda CIndicator e oferece criação/configuração/acesso a Commodity Channel Index; parâmetros próprios: ma_period, applied, além de símbolo/timeframe. Proposta Stoikus: fonte analítica experimental com estado e tempo explícitos, sem inferir regra estratégica ou eficácia.

### REF-2990 — MaPeriod [REF, p.PDF 5684–5684]

CiCCI.MaPeriod consulta período de média definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Commodity Channel Index; getter não reconfigura o indicador.

### REF-2991 — Applied [REF, p.PDF 5685–5685]

CiCCI.Applied consulta preço ou handle aplicado definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Commodity Channel Index; getter não reconfigura o indicador.

### REF-2992 — Create [REF, p.PDF 5686–5686]

CiCCI.Create recebe símbolo/timeframe e ma_period, applied; retorna bool e recomenda Refresh/GetData para valores. Proposta: registrar configuração completa e falha de criação, sem assumir disponibilidade imediata.

### REF-2993 — Main [REF, p.PDF 5687–5687]

CiCCI.Main(index) retorna double da linha principal, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-2994 — Type [REF, p.PDF 5688–5688]

CiCCI.Type() virtual int identifica IND_CCI. Proposta: usar identidade de indicador no diagnóstico, distinta de evidência de cálculo ou qualidade estratégica.

### REF-2995 — CiChaikin [REF, p.PDF 5689–5697]

CiChaikin herda CIndicator e oferece criação/configuração/acesso a Chaikin Oscillator; parâmetros próprios: fast_ma_period, slow_ma_period, ma_method, applied volume, além de símbolo/timeframe. Proposta Stoikus: fonte analítica experimental com estado e tempo explícitos, sem inferir regra estratégica ou eficácia.

### REF-2996 — FastMaPeriod [REF, p.PDF 5691–5691]

CiChaikin.FastMaPeriod consulta período da média rápida definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Chaikin Oscillator; getter não reconfigura o indicador.

### REF-2997 — SlowMaPeriod [REF, p.PDF 5692–5692]

CiChaikin.SlowMaPeriod consulta período da média lenta definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Chaikin Oscillator; getter não reconfigura o indicador.

### REF-2998 — MaMethod [REF, p.PDF 5693–5693]

CiChaikin.MaMethod consulta método ENUM_MA_METHOD definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Chaikin Oscillator; getter não reconfigura o indicador.

### REF-2999 — Applied [REF, p.PDF 5694–5694]

CiChaikin.Applied consulta tipo de volume ENUM_APPLIED_VOLUME definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de Chaikin Oscillator; getter não reconfigura o indicador.

### REF-3000 — Create [REF, p.PDF 5695–5695]

CiChaikin.Create recebe símbolo/timeframe e fast_ma_period, slow_ma_period, ma_method, applied volume; retorna bool e recomenda Refresh/GetData para valores. Proposta: registrar configuração completa e falha de criação, sem assumir disponibilidade imediata. applied é ENUM_APPLIED_VOLUME, não preço/handle; tabela introdutória tem descrição genérica incompatível.

### REF-3001 — Main [REF, p.PDF 5696–5696]

CiChaikin.Main(index) retorna double da linha principal, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-3002 — Type [REF, p.PDF 5697–5697]

CiChaikin.Type() virtual int identifica IND_CHAIKIN. Proposta: usar identidade de indicador no diagnóstico, distinta de evidência de cálculo ou qualidade estratégica.

### REF-3003 — CiDeMarker [REF, p.PDF 5698–5703]

CiDeMarker herda CIndicator e oferece criação/configuração/acesso a DeMarker; parâmetros próprios: ma_period, além de símbolo/timeframe. Proposta Stoikus: fonte analítica experimental com estado e tempo explícitos, sem inferir regra estratégica ou eficácia.

### REF-3004 — MaPeriod [REF, p.PDF 5700–5700]

CiDeMarker.MaPeriod consulta período de média definido na criação. Proposta: incluir esse parâmetro na identidade/configuração reproduzível de DeMarker; getter não reconfigura o indicador.

### REF-3005 — Create [REF, p.PDF 5701–5701]

CiDeMarker.Create recebe símbolo/timeframe e ma_period; retorna bool e recomenda Refresh/GetData para valores. Proposta: registrar configuração completa e falha de criação, sem assumir disponibilidade imediata.

### REF-3006 — Main [REF, p.PDF 5702–5702]

CiDeMarker.Main(index) retorna double da linha principal, ou EMPTY_VALUE sem dado correto. Proposta: atualizar antes, rejeitar sentinela e registrar barra/tempo; linha disponível não constitui sinal autorizado.

### REF-3007 — Type [REF, p.PDF 5703–5703]

CiDeMarker.Type() virtual int identifica IND_DEMARKER. Proposta: usar identidade de indicador no diagnóstico, distinta de evidência de cálculo ou qualidade estratégica.
