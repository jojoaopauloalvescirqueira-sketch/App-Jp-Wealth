# REF — leitura semântica própria, lote 03, PDF 659–894

## Escopo e evidência

Foram lidos integralmente os corpos textuais extraídos das 236 páginas físicas PDF 659–894 de `corpus-fast/REF/pages.jsonl`, inclusive código, comentários e tabelas, não somente o índice. A leitura foi sequencial em lotes. A saída inicial de 659–680 teve corte intermediário reparado pela releitura integral de 666–671; a saída de 696–715 teve corte intermediário reparado por 704–706. Os demais lotes foram exibidos completos. A partir de 704–706/716–732 usou-se também apresentação com espaços normalizados para tornar legíveis tabelas muito fragmentadas; nenhum corpo textual foi resumido pelo script. Os hashes no JSON são os hashes originais dos registros, anteriores a essa apresentação.

Este agente não leu nem reivindica PDF 1–658. REF-0134 é somente continuação própria 659–662 de uma seção iniciada em 656. REF-0155 é ramo descritivo 754–896 e continua além do lote; REF-0160, iniciado892, está parcial até894, no meio da descrição de STAT_EQUITYDD_PERCENT. A fila começa em895. Extração não equivale a conferência visual: figuras, cores e glifos Wingdings não foram automaticamente validados. PDF720 contém essencialmente cabeçalho/rodapé extraídos, com figura referida na719. MQL_NOT_RUN: nada compilado, executado em MT5 ou validado como EX5.

A aplicação ao Stoikus abaixo distingue contrato da plataforma e proposta de uso. O contexto recebido informa UI/Monitor EA orientado a eventos e sem negociação; este lote não inspecionou novamente código produtivo, portanto não comprova quais constantes já são usadas. “Aplicação ao Monitor/UI” significa pertinência concreta ao componente atual, com implementação a verificar; novas funcionalidades estão explicitamente propostas. Nada de produto, kit ou piloto foi alterado.

## Registro por seção

### REF-0134 — OBJ_BITMAP, continuação PDF659–662

Os auxiliares movem a âncora tempo/preço com ObjectMove, substituindo tempo/valor zero por TimeCurrent/Bid; recortam a área visível por XSIZE/YSIZE e deslocam seu canto por XOFFSET/YOFFSET. Cada auxiliar reseta erro, verifica retorno e devolve bool; a preparação copia tempos e closes, ajusta espaçamento por escala do gráfico e demonstra criação/redesenho/remoção com pausas. Ao Monitor/UI, um bitmap preso à cotação não acompanha o mesmo sistema de coordenadas de um painel fixo; eventual ícone de estado fixo deve considerar Bitmap Label. Não foi comprovado uso atual de bitmap. Suspeita concreta de exemplo: PDF662 chama BitmapDelete duas vezes com o mesmo nome e comenta remoção de “Sell signs”, embora desenhe bitmaps; também diz High/Low usando close. Tratar como provável cópia editorial, sem reproduzir automaticamente.

### REF-0135 — OBJ_BITMAP_LABEL, PDF663–669

A âncora é em pixels, com canto do gráfico e ponto interno selecionáveis. BMPFILE modificador0 contém imagem ON e1 OFF; STATE distingue pressionado/solto. O exemplo configura tamanho e deslocamento da janela de recorte, posição, seleção, lista e prioridade de clique, depois reduz área visível, desloca e remove. Seus comentários dizem que tamanho maior que a imagem impede desenho. Aplicação ao painel atual: separar estado visual de autorização operacional; um botão pressionado não é prova de comando executado. Ícones novos ou recortes de sprites são proposta futura. Suspeita de limites: algumas linhas de código extraído terminam antes de fechamento/parâmetros completos, especialmente667–668; não considerar cópia compilável nem concluir erro da linguagem sem olhar o PDF original.

### REF-0136 — OBJ_EDIT, PDF670–676

Edit usa pixels relativos a canto, largura/altura, texto/fonte, alinhamento e READONLY; cores de texto, fundo e borda são propriedades separadas. Os auxiliares movem, redimensionam, gravam, leem via overload bool de ObjectGetString e removem. O script anima largura/texto e consulta tamanho da janela. Aplicação ao UI: readonly protege edição direta do controle, mas validação de texto recebido e conversão de valores continuam dever da aplicação; não inferir contrato numérico pelo aspecto do campo. Uso de editores adicionais é proposta. O exemplo com Sleep pertence ao script demonstrativo e não constitui recomendação de bloqueio no Monitor.

### REF-0137 — OBJ_EVENT, PDF677–681

OBJ_EVENT é anotação gráfica ancorada em tempo, cujo texto aparece ao passar mouse. O exemplo cria no horário fornecido/atual, troca texto, move e remove; valida percentual0–100 e usa CopyTime para relacioná-lo aos bares visíveis. Aplicação possível: marcador de observação histórica do Monitor, proposta ainda não comprovada. Não confundir OBJ_EVENT com fila de eventos do EA nem com negócio de negociação. Comentário final “delete channel” não corresponde ao tipo Event, provável cópia editorial.

### REF-0138 — OBJ_RECTANGLE_LABEL, PDF682–687

Objeto explicitamente destinado ao desenho de interfaces; posição e dimensões são em pixels relativos ao canto. BGCOLOR e BORDER_TYPE são independentes, com FLAT, RAISED e SUNKEN; cor/estilo/espessura de borda são configurados para modo plano. Exemplo redimensiona e alterna borda, com verificação de parada. Aplicação ao painel atual: fundo de agrupamento e indicadores visuais coerentes com redimensionamento; aparência elevada/afundada não deve substituir texto de estado do Monitor. Sem alteração nem demonstração de uso no código atual.

### REF-0139 — Object Properties, PDF688–715

Contrato central: setters, ObjectCreate e ObjectMove enviam comandos à fila do gráfico; sucesso da chamada não assegura atualização visual imediata. ChartRedraw força atualização; novas cotações/redimensionamento também disparam atualização. O Monitor deve distinguir estado do modelo, aceitação do comando gráfico e tela efetivamente atualizada, sem interpretar ausência momentânea de repaint como falha de cálculo.

As propriedades são tipadas por setters/getters Integer, Double, String. Modificadores têm significado específico: número da âncora em TIME/PRICE, índice do nível nas propriedades LEVEL*, estado0/1 em BMPFILE. TYPE/CREATETIME e CHART_ID são leitura; TIMEFRAMES é máscara. SELECTABLE difere de SELECTED; HIDDEN oculta da lista e protege contra Delete Last, não equivale a invisibilidade no gráfico. ZORDER resolve prioridade de clique entre objetos sobrepostos, não prova regra de empilhamento visual. READONLY pertence a Edit. LABEL recebe tamanho após renderização; obter dimensões antes disso não valida layout. ANGLE não definido em objetos criados por programa pode ser EMPTY_VALUE. TOOLTIP vazio não é a mesma coisa que a sequência newline usada para desativá-lo.

OBJ_CHART embutido tem restrições: ChartClose e ChartSetSymbolPeriod não operam como num gráfico normal; CHART_SCALE/BRING_TO_TOP/SHOW_DATE_SCALE/SHOW_PRICE_SCALE são ineficazes nessa via. Recorte de imagem é XSIZE/YSIZE com origem XOFFSET/YOFFSET dentro da imagem. BUTTON/RECTANGLE_LABEL/EDIT/CHART têm ponto fixo superior esquerdo. Aplicação ao UI atual: usar propriedade certa para coordenada, visibilidade e texto, manter nomes/erros rastreáveis; novos gráficos embutidos são proposta. Suspeita bibliográfica: tabela688 e repetições716/721 chamam dimensões de Bitmap/Bitmap Label “read only”, mas exemplos e explicação709 mandam escrever XSIZE/YSIZE para recorte. Registrar tensão de apresentação; distinguir dimensão física da imagem e área visível, sem inventar correção definitiva. Exemplo714–715 usa ângulo negativo para rotação horária, consistente com convenção anti-horária positiva.

### REF-0140 — Methods of Object Binding, PDF716–720

Text/Label/Bitmap/Bitmap Label admitem nove ANCHOR_POINT; canto do gráfico e âncora dentro do objeto são conceitos diferentes. BUTTON/RECTANGLE_LABEL/EDIT/CHART conservam âncora superior esquerda. Arrow possui TOP/BOTTOM; exemplo usa fractais e escolhe âncora para não cobrir a barra. A cópia de buffers/tempos trata erro e limita quantidade de setas. Aplicação ao UI: alinhamento deve ser calculado pelo tipo do objeto, especialmente labels versus controles de tamanho fixo. Marcadores por fractais são somente demonstração da fonte, sem uso atual atribuído ou proposta de estratégia. Figura720 não conferida.

### REF-0141 — Chart Corner, PDF721–723

BASE_CORNER contém quatro origens: esquerda/direita, superior/inferior. XDISTANCE/YDISTANCE são distâncias em pixels desde o canto escolhido; ANCHOR especifica qual ponto do label recebe tais coordenadas. O exemplo cria quatro labels com correspondência entre canto e âncora. Aplicação concreta: painel ancorado à direita/rodapé precisa conservar essas duas escolhas ao recalcular layout; dimensões reais da janela importam. Não se verificou comportamento com DPI/redimensionamento em MT5.

### REF-0142 — Visibility of Objects, PDF724–726

OBJPROP_TIMEFRAMES recebe flags OBJ_PERIOD_* combinadas por OR; NO_PERIODS=0 e ALL_PERIODS=0x001fffff. Valores de máscara não são os valores de ENUM_TIMEFRAMES. Exemplo desenha máximas/mínimas anteriores em M10/H4. Aplicação ao Monitor: persistência de um painel entre períodos deve ser explícita, separada de HIDDEN. Suspeita de robustez do exemplo: pede dois preços mas testa somente contagem>0 antes de chamar o índice0 “dia anterior”; cópia parcial de um elemento requer revisão semântica. Não transformar exemplo em validação de dados históricos do produto.

### REF-0143 — Levels of Elliott Wave, PDF727

OBJ_ELLIOTWAVE5/3 recebem DEGREE entre Grand Supercycle e Subminuette; DRAWLINES controla conexões. Exemplo percorre objetos, identifica tipos e altera aparência. É classificação de marcação visual, sem contrato de previsão. Sem uso atual identificado no Monitor; eventual ferramenta de anotação é futura e não autorizada aqui.

### REF-0144 — Gann Objects, PDF728–729

GANN_UP_TREND/DOWN_TREND indicam direção para fan/grid. SCALE usa pips/bar e exemplo situa duas âncoras com limites/tempos visíveis. Escala geométrica depende do contexto e não representa regra financeira JPW. Sem uso atual identificado; apenas referência para eventual anotação. Linha Print extraída729 está cortada, não validada como código executável.

### REF-0145 — Web Colors, PDF730–731

Catálogo de constantes color e escolha por ObjectSetInteger para objetos, PlotIndexSetInteger para indicadores. Exemplo define três plots e cores. Aplicação ao painel: centralizar paleta sem presumir que cor substitui estado textual; adaptação ao tema aparece adiante. A tabela de cores foi lida textualmente, mas amostras visuais e contraste não foram conferidos.

### REF-0146 — Wingdings, PDF732

OBJ_ARROW recebe glifo por ARROWCODE; exemplo usa241, copia close e ancora em tempo/preço. Útil para marcador visual futuro, mas não se infere significado do número sem figura/fonte instalada. O quadro de glifos é visual e não foi conferido; catálogo textual não basta para prometer ícone específico.

### REF-0147 — Indicator Constants, PDF733–753 (ramo)

O capítulo agrupa preço/volume, suavização, linhas/buffers, desenho, propriedades, tipos e dados de parâmetros. É ramo com filhos efetivamente lidos abaixo; não somar outra vez suas páginas como leitura independente. A introdução fala em cinco grupos, mas lista sete: suspeita editorial simples. Não comprova presença de indicadores no Monitor.

### REF-0148 — Price Constants, PDF734–736

Sete bases: close/open/high/low, median=(H+L)/2, typical=(H+L+C)/3 e weighted=(H+L+2C)/4. VOLUME_TICK e REAL são diferentes; Stochastic admite Low/High ou Close/Close. Quando parâmetro aceita applied_price, pode receber handle e usar buffer0 do indicador de entrada. Exemplo suaviza RSI com iMA sobre handleRSI. Aplicação futura: manter no contrato base de preço, volume, símbolo/período e buffer, em vez de tratar toda série como close. Suspeita de engenharia no exemplo736: iMA é criado dentro de OnCalculate; exigir avaliação de ciclo de vida/validação do handle em implementação própria, sem afirmar vazamento medido.

### REF-0149 — Smoothing Methods, PDF737

SMA, EMA, SMMA e LWMA são opções distintas. Exemplo Alligator cria três handles SMMA em PRICE_MEDIAN com períodos diferentes. Seleção é parâmetro da plataforma, não recomendação de sinal. Nenhum uso atual confirmado; referência para extensão analítica futura.

### REF-0150 — Indicators Lines, PDF738–739

Buffers começam em0; MAIN/SIGNAL=0/1 para MACD/RVI/Stochastic; ADX usa0/1/2; Bands base/upper/lower=0/1/2; Envelopes/Fractals upper/lower=0/1; Gator lower histogram é2, não1; Alligator jaw/teeth/lips0/1/2; Ichimoku0–4. Aplicação futura: testes precisam conferir buffer por indicador e não reaproveitar índice genérico. Não atribuir integração atual ao Monitor.

### REF-0151 — Drawing Styles, PDF740–744

Dezoito desenhos precisam de1–4 buffers DATA e estilos COLOR de mais um COLOR_INDEX colocado após os buffers de dados; BARS/CANDLES requerem quatro. DRAW_NONE ainda consome um buffer. Plot properties distinguem arrowcode/arrowshift, início sem desenho, shift em barras, visibilidade DataWindow, estilo/espessura, quantidade/índice de cor e EMPTY_VALUE. Labels de plots compostos usam separador ponto e vírgula. Estilos tracejados são válidos para espessura0/1 segundo texto. Aplicação futura: um indicador de telemetria deve separar ausência de valor de zero válido; não confundir deslocamento visual com horário dos dados. Exemplo744 nomeia “Moving Average” mas copia close diretamente: descrição ilustrativa não prova cálculo de média.

### REF-0152 — Custom Indicator Properties, PDF745–750

SetIndexBuffer declara DATA, COLOR_INDEX ou CALCULATIONS. Propriedades integer incluem dígitos, altura, níveis, cor/estilo/espessura e mínimos/máximos fixos; doubles contêm limites/valores de níveis; strings shortname e textos de níveis. Exemplo usa quatro buffers, dois apenas para cálculo, níveis20/80 e PLOT_EMPTY_VALUE0. Aplicação futura: dado auxiliar não se torna série pública apenas por existir; zero como vazio pode esconder zero matematicamente válido. O texto afirma número ilimitado de buffers; é declaração da fonte, não benchmark local de memória nem promessa operacional.

### REF-0153 — Indicator Types, PDF751–752

Funções i* e IndicatorCreate são duas vias equivalentes para criar handles. IND_CUSTOM exige primeiro MqlParam TYPE_STRING contendo nome do indicador; enum inclui os tipos internos. Aplicação futura: fábrica uniforme deve conservar contrato do indicador e parâmetros, sem usar enum como garantia de prontidão dos dados.

### REF-0154 — Data Type Identifiers, PDF753

MqlParam.type descreve cada argumento; enum inclui booleanos, inteiros de larguras/sinais diferentes, datetime/color, float/double/string. Tipo e ordem precisam corresponder estritamente à assinatura. Aplicação futura: serialização de configuração deve manter ambos; não presumir que ordem de um objeto genérico de UI vale como ordem da API.

### REF-0155 — Environment State, PDF754–894 (ramo parcial até896)

Ramo de propriedades de terminal, programa, símbolo, conta e tester. Todos os filhos iniciados neste lote foram lidos nas páginas abaixo; Testing Statistics permanece parcial. Propriedade da plataforma é observação de ambiente, não norma JPW nem autorização para armar Supervisor.

### REF-0156 — Client Terminal Properties, PDF755–764

TerminalInfoInteger cobre conexão, permissões DLL/trade/email/FTP/push, build, limite de barras, núcleos, memória/disco em MB, OpenCL, coordenadas da tela virtual e DPI. Ping é microsegundos, não milissegundos. Estado de tecla segue GetKeyState, não mero bool. TerminalInfoDouble traz saldo community e retransmissão TCP/IP global da máquina; esta não mede especificamente terminal↔servidor e é obtida do SO uma vez por minuto. TerminalInfoString distingue instalação, dados e pasta comum, além de CPU/OS/idioma e tema Light/Dark. Operações de arquivo se restringem às áreas permitidas, não a qualquer caminho retornado.

O cálculo de escala toma96DPI como base e a seção lista THEME_COLOR_* para janelas, textos, botões, seleção, Journal, negociação, DOM, ticks, tester e profiler. Aplicação ao UI atual: diagnosticar build/DPI e respeitar tema sem equiparar cor positiva a autorização; diagnóstico de conectividade deve mostrar unidade e origem. Telemetria nova e tema dinâmico são propostas, não verificações de implementação. Suspeitas: introdução755 menciona duas funções, mas758 apresenta famíliaDouble; exemplo758 usa button_width embora declare base_width, provável inconsistência do snippet. Valores de tema recentes dependem de build e não foram compilados localmente.

### REF-0157 — Running MQL5 Program Properties, PDF765–768

MQLInfo mede handles de objetos ativos e memória em MB; permissões DLL/trade/signals do programa são separadas das do terminal e da conta. Flags distinguem debugger, profiler, tester, forward, optimization, visual e coleta de frames; licença refere-se ao EX5 que faz a consulta. Tipos incluem SCRIPT, EXPERT, INDICATOR e SERVICE; STARTED_FROM_CONFIG indica inicialização pela configuração. Aplicação ao Monitor: registrar contexto evita confundir execução em tester com sessão real, e consumo de handles é diagnóstico, sem limiar inferido. Não habilita negociação. Exemplo final parece terminar com switch/corpo incompletos na extração768; qualificar como trecho da fonte/extração, sem declarar prova de compilação.

### REF-0158 — Symbol Properties, PDF769–881

Três getters tipados consultam metadados e estado. SUBSCRIPTION_DELAY exige símbolo selecionado; caso contrário há ERR_MARKET_NOT_SELECTED4302. EXISTS, SELECT e VISIBLE são diferentes: cruzamentos para conversão de margem/lucro podem ser selecionados automaticamente e invisíveis. CUSTOM, setor/indústria e modo de barras Bid/Last não garantem que um instrumento possa ser negociado. TIME_MSC é milissegundos desde epoch; SPREAD/STOPS_LEVEL/FREEZE_LEVEL são em pontos. BOOKDEPTH0 indica ausência da fila. VOLUME inteiro de último negócio difere de VOLUME_REAL; ambos diferem do volume de lote permitido.

POINT, TICK_SIZE, TICK_VALUE_PROFIT/LOSS e CONTRACT_SIZE têm papéis distintos. VOLUME_MIN/MAX/STEP controlam discretização; VOLUME_LIMIT restringe agregado de posição aberta e pendentes por direção, não apenas tamanho de cada ordem. Exemplo5lotes admite Buy5 e SellLimit5, mas não outro BuyLimit. Swap long/short depende de modo e moeda; razões por dia0/1/3 e rollovertriplo não autorizam assumir quarta-feira para todos. INITIAL em moeda de margem é por lote; MAINTENANCE0 recorre ao inicial. Hedged margin depende do broker: base absoluta se initial definido, contractsize se não; método maior perna ignora MARGIN_HEDGED, calcula cada direção com preços/taxas ponderados e toma a maior margem.

Sessão contém volume/turnover/openinterest, ordens atuais, open/close/média ponderada/settlement/limites. Opções têm strike, theoretical, delta/theta/gamma/vega/rho/omega/sensitivity; leitura destes campos é metadado, não modelo de previsão implementado. Strings distinguem base/profit/margin currencies, descrição, bolsa, banco, país/setor/indústria, basis, ISIN/página/caminho. Fórmulas de símbolos custom requerem aspas em nomes com dígito inicial/caracteres especiais; exemplo Euro index combina potências. Não alterar fórmulas JPW com base nesse catálogo.

Expiration é máscara GTC1/DAY2/SPECIFIED4/SPECIFIED_DAY8, testada com AND. GTC comporta ordens/stops eternos, DAILY que apaga pendentes e SL/TP, e DAILY_EXCLUDING_STOPS que preserva SL/TP. Filling: FOK executa integral ou nada, podendo combinar ofertas; IOC executa disponível e cancela saldo; BOC só permanece passivo no book e cancela se executável imediatamente, admitindo limit/stoplimit permitidos. RETURN mantém processamento do saldo e não tem flag SYMBOL_FILLING_RETURN. É vedado para execução imediata Market; Instant/Request aceitam FOK/IOC independentemente de flags e Return; Exchange usa flags para FOK/IOC e admite Return. Para pendentes o texto prescreve Return independentemente do modo, pois não executam ao envio. Não confundir flags SYMBOL_FILLING_* com enum ORDER_FILLING_*; preencher request requer conversão deliberada, não cast presumido. O texto diz que ausência de filling seleciona Return; não usar essa frase para legitimar request inválido em Market.

Modos Request/Instant/Market/Exchange tratam obtenção de preço/requote/consentimento de forma diferente. ORDER_MODE permite market, limit, stop, stoplimit, SL, TP e CloseBy; CloseBy depende de hedging. TRADE_MODE distingue disabled/longonly/shortonly/closeonly/full. Modos de cálculo têm fórmulas diferentes para Forex com/sem alavancagem, Futures, CFD, CFDIndex, CFDLeverage, ações de bolsa/MOEX, futuros de bolsa/FORTS, bonds e collateral. FORTS introduz desconto relativo a settlement e preço ponderado; collateral não tem lucro/margem de negociação, mas marketvalue afeta assets/equity/free margin. Logo fórmula simples universal não representa contrato da plataforma, nem afirmação de que código atual esteja errado. American/European e Call/Put são propriedades da opção. Setor e extensa enumeração industrial até Utilities são classificação, não exposição efetivamente suportada pelo Monitor.

Aplicação atual ao Monitor/UI: checar frescor/unidades da cotação, distinguir preço de exibição e preço executável, mostrar saldo/risco com moeda correta e respeitar tipos e disponibilidade. Consulta destes contratos pode alimentar diagnósticos sem negociar. Normalização de lote, construtor de ordens, estratégias, opções, book e supervisão ativa são propostas futuras dependentes de escopo/autorização, sem código ou execução neste lote.

Suspeitas qualificadas: exemplo PDF858 de CloseBy testa `(SYMBOL_ORDER_TP & symbol_order_mode)==SYMBOL_ORDER_CLOSEBY`, em vez de mascarar CLOSEBY; provável erro de exemplo. Fórmulas bonds868–870 trazem `open_price * /100` e expressão intitulada Profit sem subtração do custo/open_price; não transportar como cálculo validado, conferir original/API contextual antes de usar. Texto de setores possui grafias atípicas nos identificadores (TRAINIG, SPEALITY, STUFFING, MORTAGE etc.); não “corrigir” identificadores por intuição. Tabelas769–849 e862–868 fragmentam palavras/letras por muitas páginas: foi lido o corpo disponível, mas não houve confirmação visual da diagramação nem restauração de identificadores como código.

### REF-0159 — Account Properties, PDF882–891

AccountInfoInteger/Double/String separam login long, trade mode, leverage, limite de pendentes, permissões da conta/EA, modo de margem, dígitos da moeda e regras FIFO/hedge. FIFO true exige fechar posições por símbolo na ordem de abertura; fora de hedging é false. Saldo, crédito, lucro corrente, equity, margem usada/livre, marginlevel, call/stopout, initial/maintenance, assets/liabilities e comissão bloqueada não são intercambiáveis. CALL/SO podem ser percentuais ou dinheiro segundo SO_MODE. Trade mode é demo/contest/real; margem pode ser netting (uma posição/símbolo), exchange ou hedging (várias posições e margemhedged). Exemplo imprime conta e unidades de stopout.

Aplicação ao Monitor atual: evitar misturar patrimônio normativo, balance e equity; usar moeda/dígitos e unidade de stopout; detectar netting/hedging antes de interpretar contagem/risco. Saber que o programa tem permissão de negociar não o autoriza a negociar. Novas ações de fechamento são propostas fora do escopo. Suspeita editorial889: RETAIL_HEDGING descrito como “exchange markets”, formulação excessivamente específica para uma enum que distingue accountingmode; não basear inferência de mercado nessa frase. Linhas longas890 estão truncadas na extração original, sem prova de compilação.

### REF-0160 — Testing Statistics, PDF892–894, parcial

TesterStatistics retorna double até para métricas internamente int; valores monetários são na moeda de depósito salvo indicação. NET profit soma grossprofit não negativo e grossloss não positivo. Estatística distingue maior soma de uma sequência vencedora/perdedora da soma da sequência com maior quantidade de trades; quantidade e valor são campos diferentes. BALANCE_DD é maior drawdown monetário; BALANCEDD_PERCENT é percentual no mesmo instante desse máximo monetário. BALANCE_DDREL_PERCENT é máximo percentual, e BALANCE_DD_RELATIVE é dinheiro nesse outro instante. Não presumir que os máximos coincidam. EQUITYMIN e EQUITY_DD são série equity distinta da balance; descrição EQUITYDD_PERCENT segue além894.

Aplicação futura à avaliação de EA negociador: guardar unidade, série e definição exata em relatórios para não confundir máximos. Monitor sem negociação e harness/piloto não ganham aprovação por ter acesso ao catálogo de estatísticas. Nenhum backtest foi feito. Fila explícita: PDF895–896 para concluir esta seção e ramo Environment State; não antecipar métricas não lidas neste lote.

## Limites e fila de consolidação

Cobertura própria exata:659–894,236 páginas, sem lacuna. A leitura textual não valida imagens, tabelas renderizadas, links externos, sintaxe de trechos cortados ou correção de fórmulas suspeitas. Estas são suspeitas bibliográficas/robustez observadas, não bugs produtivos confirmados. A consolidação pode usar cada seção com as citações físicas acima e deve manter REF-0134 como continuação e REF-0160 como parcial. Prosseguir em895, sem refazer/reivindicar1–658. Nenhum produto, kit, piloto, Git ou publicação modificado.
