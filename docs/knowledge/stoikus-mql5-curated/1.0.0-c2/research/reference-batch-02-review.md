# REF lote02 — leitura textual356–658

Fonte: MQL5 Language REFERENCE.pdf, SHA-256 `9ae05ce748d23ce0de9b230fc6c7093a2af0adc3ce3544244a74e1c7d628d499`.303páginas físicas contínuas lidas. Texto de cada página, incluindo exemplos e comentários, foi exibido; hashes por página constam do JSON. Índice não foi contado como corpo. Nenhuma alteração de produto, kit ou piloto. Aplicações abaixo são propostas analíticas, não afirmações sobre implementação atual.

## Contratos transversais e limites

Nos exemplos de objetos, criar/mover/excluir usa chart_ID e nome; plano BACK, seleção SELECTABLE/SELECTED, ocultação na lista HIDDEN e prioridade de clique ZORDER são independentes. HIDDEN não significa invisível no gráfico. Muitos Create retornam true após ObjectCreate, sem checar os setters subsequentes: esse true não prova que todas as propriedades foram aplicadas. Séries de exemplo usam CopyTime/Low/High e tratam -1; a adaptação deve conferir também contagem retornada e barras válidas antes de indexar. A geração visual, Sleep e ChartRedraw dos scripts não é arquitetura aprovada para handlers do Monitor.

Todos os exemplos: **MQL_NOT_RUN**. Visuais: **NOT_CERTIFIED**. As páginas com linhas longas cortadas no próprio corpus não autorizam reconstrução silenciosa. Leitura textual integral é relativa ao corpo disponível, não atestado de fidelidade de código copiável.

## REF-0092 — Examples of Working with the Chart (PDF343–400)

Wrappers tipados consultam ChartGetInteger/Double/String e escrevem ChartSet*. A continuação começa em ChartShowOHLCSet; cobre linhas Bid/Ask/Last, separadores, grid, volumes, descrições, geometria/janelas e cores. Valores de falha são -1, clrNONE, EMPTY_VALUE ou WRONG_VALUE convertido para enum; o retorno de consulta deve permanecer separado do valor booleano consultado. SHIFT_SIZE 10–50 depende de CHART_SHIFT; FIXED_POSITION exige autoscroll falso; FIXED_MAX/MIN dependem SCALEFIX; POINTS_PER_BAR depende SCALE_PT_PER_BAR. O painel388–400 enumera propriedades, divide consulta/tipo/controle e trata OBJECT_CLICK por nome Button_index, libera estado e redesenha. Os getters maximizado/minimizado387–388 declaram long value, mas chamam sobrecarga direta sem saída e depois copiam value: não são modelo seguro. LAST_PROPERTY_NUMBER111 é limite do exemplo, não descoberta robusta de API.

Aplicação: proposta futura: adaptadores explícitos para painel/diagnóstico Stoikus, preservando propriedades do usuário; nenhuma confirmação do código atual.

Evidência: [REF, REF-0092, p.PDF 356–400]; CONTINUATION_READ_356_400_BEGINNING_PREVIOUS_BATCH.

## REF-0093 — Objects Constants (PDF401–732)

O capítulo organiza44objetos e nove grupos de constantes: tipo, propriedades, binding, corner, visibilidade, níveis Elliott, Gann, cores e Wingdings. Página401 é introdução; filhos posteriores a658 não foram lidos neste lote.

Aplicação: sem uso direto: mapa de consulta; pai parcial até732.

Evidência: [REF, REF-0093, p.PDF 401–658]; PARTIAL_SECTION.

## REF-0094 — Object Types (PDF402–687)

ENUM_OBJECT é o discriminante passado a ObjectCreate;402–403 lista tipos de geometria, anotações de preço/tempo e controles de interface. Propriedades adicionais são configuradas depois da criação. Esta leitura cobre introdução e filhos até início bitmap; não cobre toda a seção402–687.

Aplicação: proposta futura: separar objetos ligados ao mercado de controles em pixels, sem inferir adoção atual.

Evidência: [REF, REF-0094, p.PDF 402–658]; PARTIAL_SECTION.

## REF-0095 — OBJ_VLINE (PDF404–408)

OBJ_VLINE usa uma data; preço0 em ObjectCreate/ObjectMove é irrelevante ao eixo temporal. OBJPROP_RAY permite exibir a linha em todas as janelas. Exemplo valida percentual0–100, copia datas das barras visíveis, move por índices, consulta IsStopped e elimina objeto nominal.

Aplicação: proposta futura: demarcações temporais de sessão no Monitor; não constitui regra de horário JPW.

Evidência: [REF, REF-0095, p.PDF 404–408]; FULL_TEXT_READ.

## REF-0096 — OBJ_HLINE (PDF409–413)

OBJ_HLINE usa preço, com data0; helper substitui preço0 pelo Bid atual. Exemplo discretiza intervalo CHART_PRICE_MIN/MAX em1000valores, posiciona por percentual e move com ObjectMove índice0 antes da exclusão.

Aplicação: proposta futura: níveis informativos; linha visual não é ordem/stop negociado.

Evidência: [REF, REF-0096, p.PDF 409–413]; FULL_TEXT_READ.

## REF-0097 — OBJ_TREND (PDF414–420)

OBJ_TREND recebe dois pares data/preço. RAY_LEFT e RAY_RIGHT controlam prolongamentos independentemente. Helper de pontos vazios usa TimeCurrent/Bid e CopyTime de10barras para outro extremo. Exemplo move cada ponto verticalmente e ambos horizontalmente.

Aplicação: sem uso direto: técnica de anotação opcional, sem sinal ou estratégia demonstrada.

Evidência: [REF, REF-0097, p.PDF 414–420]; FULL_TEXT_READ.

## REF-0098 — OBJ_TRENDBYANGLE (PDF421–426)

OBJ_TRENDBYANGLE aceita inclinação por ângulo ou segunda âncora; ao alterar OBJPROP_ANGLE a segunda coordenada é redefinida automaticamente. Criação usa ponto auxiliar para facilitar arraste. Ambos os raios configuráveis; exemplo move primeiro ponto e gira.

Aplicação: sem uso direto: ângulo gráfico não demonstra taxa econômica de variação nem previsão.

Evidência: [REF, REF-0098, p.PDF 421–426]; FULL_TEXT_READ.

## REF-0099 — OBJ_CYCLES (PDF427–432)

OBJ_CYCLES define espaçamento entre linhas pelas datas de duas âncoras. Exemplo cria com dois pares e muda distância ao mover primeiro/segundo pontos; preço é componente da assinatura, mas o contrato do espaçamento é temporal.

Aplicação: sem uso direto: não confundir ciclos desenhados com calendário operacional normativo.

Evidência: [REF, REF-0099, p.PDF 427–432]; FULL_TEXT_READ.

## REF-0100 — OBJ_ARROWED_LINE (PDF433–438)

OBJ_ARROWED_LINE desenha segmento com seta entre dois pares data/preço. Helpers expõem cor/estilo/largura, plano, seleção, ocultação e prioridade; movimentação escolhe índice da âncora e remoção usa nome.

Aplicação: proposta futura: explicação visual de transição de estado, sem comando de negociação.

Evidência: [REF, REF-0100, p.PDF 433–438]; FULL_TEXT_READ.

## REF-0101 — OBJ_CHANNEL (PDF439–445)

OBJ_CHANNEL recebe três pares data/preço: dois formam linha base e terceiro define afastamento. Pode preencher com OBJPROP_FILL e prolongar à esquerda/direita. Exemplo move âncoras0/1no tempo e2no preço. Defaults usam preço de referência e diferença em SYMBOL_POINT.

Aplicação: sem uso direto: canal ilustrativo, não limite de risco Stoikus.

Evidência: [REF, REF-0101, p.PDF 439–445]; FULL_TEXT_READ.

## REF-0102 — OBJ_STDDEVCHANNEL (PDF446–452)

OBJ_STDDEVCHANNEL usa duas datas, com preços0; largura ajustada por OBJPROP_DEVIATION. Há FILL e raios independentes. Exemplo desloca ambas datas e expande desvio em laço; não apresenta validação estatística do canal como sinal.

Aplicação: sem uso direto: eventual estudo visual separado do cálculo normativo.

Evidência: [REF, REF-0102, p.PDF 446–452]; FULL_TEXT_READ.

## REF-0103 — OBJ_REGRESSION (PDF453–458)

OBJ_REGRESSION também delimita intervalo por duas datas e preços0; admite preenchimento/raios. O exemplo desloca início/fim conjuntamente; não fornece nesta seção contrato de inferência estatística ou garantia preditiva.

Aplicação: sem uso direto: regressão desenhada não altera programas diários.

Evidência: [REF, REF-0103, p.PDF 453–458]; FULL_TEXT_READ.

## REF-0104 — OBJ_PITCHFORK (PDF459–466)

OBJ_PITCHFORK utiliza três pares, raios e níveis configuráveis. OBJPROP_LEVELS antecede LEVELVALUE/LEVELCOLOR/LEVELSTYLE/LEVELWIDTH/LEVELTEXT indexados; texto percentual deriva100*valor. Em461 a checagem de tamanhos repete widths e omite values, embora values[i] seja lido. Exemplo move pontos e apaga.

Aplicação: sem uso direto: se reutilizar helper no futuro, validar todos os vetores e cada setter.

Evidência: [REF, REF-0104, p.PDF 459–466]; FULL_TEXT_READ.

## REF-0105 — OBJ_GANNLINE (PDF467–473)

OBJ_GANNLINE admite ângulo Gann, escala e segunda âncora; mudanças de ângulo/escala recalculam segunda coordenada. OBJPROP_SCALE é comentado como pips por barra. Permite raios e métodos separados para mudar ângulo/escala.

Aplicação: sem uso direto: unidade gráfica não substitui Point/tick-size financeiro nem regra JPW.

Evidência: [REF, REF-0105, p.PDF 467–473]; FULL_TEXT_READ.

## REF-0106 — OBJ_GANNFAN (PDF474–480)

OBJ_GANNFAN recebe duas datas e preço inicial; OBJPROP_SCALE controla inclinação e OBJPROP_DIRECTION controla tendência. Exemplo booleano documenta true descendente/false ascendente e inverte direção após movimento.

Aplicação: sem uso direto: enum Gann é direção da figura, não posição comprada/vendida.

Evidência: [REF, REF-0106, p.PDF 474–480]; FULL_TEXT_READ.

## REF-0107 — OBJ_GANNGRID (PDF481–487)

OBJ_GANNGRID repete contrato escala/direção da grade Gann e usa data/preço inicial mais segunda data. Exemplo desloca primeiro preço e segunda data, muda direção e elimina; não equivale ao CHART_SHOW_GRID do gráfico.

Aplicação: sem uso direto: não há uso atual demonstrado.

Evidência: [REF, REF-0107, p.PDF 481–487]; FULL_TEXT_READ.

## REF-0108 — OBJ_FIBO (PDF488–494)

OBJ_FIBO utiliza duas âncoras e raios independentes. Níveis recebem quantidade e propriedades indexadas; labels formatam100*values[i]. FiboLevelsSet490 valida colors/styles/widths, mas não values. Exemplo desloca os preços das âncoras e exclui.

Aplicação: sem uso direto: proporções de desenho não são metas autorizadas do Stoikus.

Evidência: [REF, REF-0108, p.PDF 488–494]; FULL_TEXT_READ.

## REF-0109 — OBJ_FIBOTIMES (PDF495–501)

OBJ_FIBOTIMES projeta zonas temporais a partir de duas âncoras; aceita quantidade/valor/cor/estilo/largura/texto por nível. Texto usa values diretamente, diferentemente do percentual de retração.497 repete widths na validação e não testa values. Default segunda data vem de3barras.

Aplicação: sem uso direto: não substitui relógio/calendário de execução.

Evidência: [REF, REF-0109, p.PDF 495–501]; FULL_TEXT_READ.

## REF-0110 — OBJ_FIBOFAN (PDF502–508)

OBJ_FIBOFAN cria leque a partir de dois pares data/preço e níveis configuráveis; funções movem âncoras por índice.504 repete validação incompleta de arrays. Exemplo muda primeiro preço e segunda data com redesenho.

Aplicação: sem uso direto: ferramenta visual sem estratégia demonstrada.

Evidência: [REF, REF-0110, p.PDF 502–508]; FULL_TEXT_READ.

## REF-0111 — OBJ_FIBOARC (PDF509–515)

OBJ_FIBOARC aceita escala OBJPROP_SCALE e OBJPROP_ELLIPSE para elipse inteira/meia; raio decorre também das âncoras. Níveis indexados como retração;511 repete widths e omite values no guard. Exemplo move âncoras.

Aplicação: sem uso direto: aplicação puramente ilustrativa.

Evidência: [REF, REF-0111, p.PDF 509–515]; FULL_TEXT_READ.

## REF-0112 — OBJ_FIBOCHANNEL (PDF516–523)

OBJ_FIBOCHANNEL usa três pares e raios independentes; níveis personalizados podem receber valores e estilos individuais.518 usa guard incompleto de arrays. Default terceiro ponto coincide com primeira data e preço da segunda; exemplo move três âncoras.

Aplicação: sem uso direto: nenhum canal adotado foi verificado.

Evidência: [REF, REF-0112, p.PDF 516–523]; FULL_TEXT_READ.

## REF-0113 — OBJ_EXPANSION (PDF524–531)

OBJ_EXPANSION é projeção Fibonacci de três pares; tem raios e níveis indexados, com texto FE percentual.526 repete guard sem values.528 cria temp dinâmico, preenche por CopyTime somente se time1 vazio e usa temp[2] se time2 vazio; combinação time1 informado/time2 ausente requer correção antes de reutilização.

Aplicação: sem uso direto: lógica de defaults do exemplo demanda revisão, NOT_RUN.

Evidência: [REF, REF-0113, p.PDF 524–531]; FULL_TEXT_READ.

## REF-0114 — OBJ_ELLIOTWAVE5 (PDF532–539)

OBJ_ELLIOTWAVE5 recebe cinco pares data/preço. OBJPROP_DRAWLINES liga/desliga conexão e OBJPROP_DEGREE recebe ENUM_ELLIOT_WAVE_DEGREE. Defaults recorrem a10datas e offsets em SYMBOL_POINT; exemplo desloca diferentes grupos de pontos. A figura não detecta ondas automaticamente.

Aplicação: sem uso direto: contagem discricionária de ondas não integra regra Stoikus.

Evidência: [REF, REF-0114, p.PDF 532–539]; FULL_TEXT_READ.

## REF-0115 — OBJ_ELLIOTWAVE3 (PDF540–546)

OBJ_ELLIOTWAVE3 recebe três pares, DEGREE e DRAWLINES análogos. Defaults usam datas0/4/8do histórico copiado e diferenças de preço em pontos; exemplo move terceiro ponto e depois primeiro/segundo.

Aplicação: sem uso direto: API apenas representa correção já especificada.

Evidência: [REF, REF-0115, p.PDF 540–546]; FULL_TEXT_READ.

## REF-0116 — OBJ_RECTANGLE (PDF547–552)

OBJ_RECTANGLE representa região por duas âncoras data/preço, com FILL opcional independente de BACK. ObjectMove atualiza cantos por índice; exemplo muda largura temporal e altura por laços separados.

Aplicação: proposta futura: destacar faixas/intervalos informativos em gráfico; não prova uso atual.

Evidência: [REF, REF-0116, p.PDF 547–552]; FULL_TEXT_READ.

## REF-0117 — OBJ_TRIANGLE (PDF553–559)

OBJ_TRIANGLE usa três pares e preenchimento por FILL; criação, movimento individual e exclusão seguem nomes. Exemplo valida percentuais e desloca três vértices; mensagem de erro de exclusão556 diz ellipse apesar de TriangleDelete.

Aplicação: sem uso direto: escolher geometria não acrescenta significado normativo.

Evidência: [REF, REF-0117, p.PDF 553–559]; FULL_TEXT_READ.

## REF-0118 — OBJ_ELLIPSE (PDF560–565)

OBJ_ELLIPSE usa três pares, largura/estilo/cor e FILL; exemplo move primeiro e segundo preços em sentidos opostos e terceira data, depois remove.

Aplicação: sem uso direto: anotação opcional.

Evidência: [REF, REF-0118, p.PDF 560–565]; FULL_TEXT_READ.

## REF-0119 — OBJ_ARROW_THUMB_UP (PDF566–571)

OBJ_ARROW_THUMB_UP é sinal de uma âncora data/preço com ENUM_ARROW_ANCHOR top/bottom. Tamanho maior que5requer OBJPROP_WIDTH via código. Exemplo muda posição e âncora relativa ao sinal, explicitando diferença entre mover mercado e mudar ponto de ancoragem.

Aplicação: proposta futura: ícone informativo de estado; não confundir thumbs-up com aprovação de operação.

Evidência: [REF, REF-0119, p.PDF 566–571]; FULL_TEXT_READ.

## REF-0120 — OBJ_ARROW_THUMB_DOWN (PDF572–577)

OBJ_ARROW_THUMB_DOWN possui mesmo contrato de âncora top/bottom e largura maior que5via código; exemplo move à direita/abaixo e muda ANCHOR_TOP. STYLE controla borda, WIDTH tamanho.

Aplicação: proposta futura: ícone de condição, sem sinal de venda implícito.

Evidência: [REF, REF-0120, p.PDF 572–577]; FULL_TEXT_READ.

## REF-0121 — OBJ_ARROW_UP (PDF578–583)

OBJ_ARROW_UP usa âncora data/preço, ANCHOR_TOP/BOTTOM e tamanho por WIDTH. Exemplo mantém data e move preço para cima, depois troca âncora e apaga; InpSelection falso contrasta com helper selecionável por default.

Aplicação: proposta futura: anotação de evento, sem direção negociável inferida.

Evidência: [REF, REF-0121, p.PDF 578–583]; FULL_TEXT_READ.

## REF-0122 — OBJ_ARROW_DOWN (PDF584–589)

OBJ_ARROW_DOWN espelha sinal para baixo; não precisa de segunda âncora nem corner em pixels. Exemplo desloca preço para baixo e depois muda ANCHOR_TOP; seleção/ocultação/prioridade continuam propriedades independentes.

Aplicação: proposta futura: marcador de diagnóstico, sem autorização de venda.

Evidência: [REF, REF-0122, p.PDF 584–589]; FULL_TEXT_READ.

## REF-0123 — OBJ_ARROW_STOP (PDF590–595)

OBJ_ARROW_STOP é desenho de placa stop com enum de âncora e largura grande via código. Exemplo move no tempo, alterna âncora e move novamente; ObjectDelete apenas elimina placa.

Aplicação: proposta futura: indicação visual de bloqueio; placa não interrompe EA nem coloca stop-loss.

Evidência: [REF, REF-0123, p.PDF 590–595]; FULL_TEXT_READ.

## REF-0124 — OBJ_ARROW_CHECK (PDF596–601)

OBJ_ARROW_CHECK é desenho check com contrato idêntico de âncora/tamanho. Exemplo muda ANCHOR_BOTTOM entre dois deslocamentos temporais. Nome e aparência não constituem resultado de validação executada.

Aplicação: proposta futura: representar estado já calculado e comprovado; nunca fabricar aprovação a partir do ícone.

Evidência: [REF, REF-0124, p.PDF 596–601]; FULL_TEXT_READ.

## REF-0125 — OBJ_ARROW_LEFT_PRICE (PDF602–606)

OBJ_ARROW_LEFT_PRICE anota preço à esquerda em uma âncora data/preço. Exemplo transforma percentual de altura em preço e move verticalmente; WIDTH define tamanho da etiqueta. Não usa o enum de âncora do grupo de setas no helper.

Aplicação: proposta futura: etiqueta de nível informativo.

Evidência: [REF, REF-0125, p.PDF 602–606]; FULL_TEXT_READ.

## REF-0126 — OBJ_ARROW_RIGHT_PRICE (PDF607–611)

OBJ_ARROW_RIGHT_PRICE é etiqueta de preço à direita, criada/movida por data/preço. Exemplo começa no percentual temporal0 e altura90, desloca preço para baixo; cada operação conserva nome.

Aplicação: proposta futura: etiqueta complementar de diagnóstico, sem ordem real.

Evidência: [REF, REF-0126, p.PDF 607–611]; FULL_TEXT_READ.

## REF-0127 — OBJ_ARROW_BUY (PDF612–616)

OBJ_ARROW_BUY é sinal gráfico; STYLE/WIDTH referem-se à linha quando selecionado. Exemplo CopyTime/Low/High nas barras visíveis, cria sinal em Low para cada barra, move a High e elimina. Não contém OrderSend.

Aplicação: proposta futura: marcar operação histórica confirmada somente depois de reconciliar dados; não demonstrado no atual.

Evidência: [REF, REF-0127, p.PDF 612–616]; FULL_TEXT_READ.

## REF-0128 — OBJ_ARROW_SELL (PDF617–621)

OBJ_ARROW_SELL também é sinal gráfico, com cor default distinta. Exemplo cria em High de cada barra, move a Low e elimina; CopyTime/Low/High verificam -1, sem conferir correspondência exata das contagens copiadas.

Aplicação: proposta futura: anotações de histórico; não confundir figura Sell com execução.

Evidência: [REF, REF-0128, p.PDF 617–621]; FULL_TEXT_READ.

## REF-0129 — OBJ_ARROW (PDF622–627)

OBJ_ARROW recebe uchar de Wingdings via OBJPROP_ARROWCODE, além de âncora e WIDTH. Exemplo cria código32 e percorre33–255, verificando interrupção/redesenhando com Sleep500. É catálogo visual, não teste de todos os ambientes de fonte.

Aplicação: proposta futura: símbolo de UI escolhido e conferido visualmente no MT5 alvo.

Evidência: [REF, REF-0129, p.PDF 622–627]; FULL_TEXT_READ.

## REF-0130 — OBJ_TEXT (PDF628–633)

OBJ_TEXT é texto ligado a uma âncora data/preço; ENUM_ANCHOR_POINT e OBJPROP_ANGLE controlam ancoragem/inclinação. TEXT/FONT/FONTSIZE configurados após criação. Exemplo anota High/Low com espaçamento por CHART_SCALE:12/6/4/2nas escalas0/1/2/3e1nas demais. Formatação fixa5casas é escolha do exemplo.

Aplicação: proposta futura: valores ligados a candles, formatados por símbolo; painel fixo exige Label.

Evidência: [REF, REF-0130, p.PDF 628–633]; FULL_TEXT_READ.

## REF-0131 — OBJ_LABEL (PDF634–641)

OBJ_LABEL ancora em pixels por XDISTANCE/YDISTANCE, corner relativo ao gráfico e ENUM_ANCHOR_POINT relativo ao texto. Criação usa data/preço0. Exemplo move em pixels e muda corners sem converter para preço, atualiza texto e verifica dimensões da janela. Helper MoveAndTextChange retorna false, mas laços638–639não testam retorno.

Aplicação: proposta futura: painel fixo de estado Stoikus, com teste de resize/DPI/cantos; uso atual não inspecionado.

Evidência: [REF, REF-0131, p.PDF 634–641]; FULL_TEXT_READ.

## REF-0132 — OBJ_BUTTON (PDF642–648)

OBJ_BUTTON é controle em pixels com corner, XSIZE/YSIZE, texto/fonte, cor de texto/fundo/borda e OBJPROP_STATE. Seleção para arrastar é separada de estado pressionado. Exemplo reduz dimensões e alterna STATE; não implementa ação comercial ou handler de consentimento.

Aplicação: proposta futura: controle de UI somente com transição explicitamente validada; desenho do botão não autoriza Supervisor.

Evidência: [REF, REF-0132, p.PDF 642–648]; FULL_TEXT_READ.

## REF-0133 — OBJ_CHART (PDF649–655)

OBJ_CHART é gráfico incorporado posicionado por pixels/corner, com símbolo/período/escala e visibilidade de escalas. Não é exibido em teste visual649. OBJPROP_CHART_ID obtém ID interno diferente do chart_ID hospedeiro usado nos setters de objeto. Exemplo exige símbolo no Market Watch e escala0–5, redimensiona e troca período paraM1.

Aplicação: sem uso direto: eventual visualização secundária exige validação no terminal real; ausência no tester não basta para diagnosticar falha.

Evidência: [REF, REF-0133, p.PDF 649–655]; FULL_TEXT_READ.

## REF-0134 — OBJ_BITMAP (PDF656–662)

Início OBJ_BITMAP656–658: imagem ligada à âncora data/preço, caminho em OBJPROP_BMPFILE; XSIZE/YSIZE delimitam região visível e XOFFSET/YOFFSET escolhem recorte. Se dimensão pedida excede fonte, comentário documenta imagem não desenhada; não é escala automática. BitmapSetImage testa retorno. Leitura termina no início de BitmapMove, antes do corpo da função.

Aplicação: proposta futura: recurso visual sujeito a arquivo/recorte; seção parcial, continuar659–662.

Evidência: [REF, REF-0134, p.PDF 656–658]; PARTIAL_SECTION.

## Fila exata

Próxima página659, continuação REF-0134 OBJ_BITMAP até662. REF-0093 Object Constants e REF-0094 Object Types permanecem pais parciais. REF-0092 foi concluída na continuação356–400;343–355pertencem ao lote anterior e não são reivindicadas aqui.

Reparo de saída: lote371–390teve truncamento na transmissão379–382; essas quatro páginas foram exibidas integralmente novamente. Não restou lacuna de páginas no intervalo356–658.
