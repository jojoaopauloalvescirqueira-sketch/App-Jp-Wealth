# REF — leitura semântica complementar10b

Escopo: páginas PDF físicas3043–3238,196/196 páginas do texto extraído lidas semanticamente. Quinze saídas completas (limitadas a 30000 caracteres; max_output_tokens20000), sem truncamento da ferramenta, verificadas contra o corpus. O lote 10 anterior permanece intacto e cobre 2941–3042. A união cobre 2941–3238; não se reivindica o restante do livro.

Fonte: corpus-fast/REF/pages.jsonl. Hashes originais de cada página, hashes das linhasJSONL, do corpus, índice e fontePDF preservados no ledger adjunto. A contagem deste recorte é196 páginas únicas; páginas de ramos e filhos não são somadas duas vezes.

Limites: leitura textual integral não equivale a auditoria visual. A fórmula gráfica dePi(p3232) não foi inferida. Linhas longas de código/comentários na extração já chegam cortadas àdireita; nenhum exemplo foi compilado/executado, todosNOT_RUN. Propostas abaixo são pesquisa, sem confirmar implementação noStoikus ou alterar normaJPW,Monitor,Supervisor,produto,manual,harness,Git ouinstruções.

Padrão recorrente dos exemplos de indicadores: OnInit liga buffers, normaliza símbolo e cria handle; INVALID_HANDLE encerra init. OnCalculate verifica BarsCalculated>0, recopia histórico quando primeiro cálculo,quantidadecalculada mudou oumaisdeumabarrachegou; em atualização incremental copia rates_total−prev_calculated+1 para incluir a barra emformação. Falha deCopyBuffer retorna0; sucesso atualiza bars_calculated e devolve rates_total. OnDeinit libera handle e limpaComment. O código de exemplo costuma apenas testar CopyBuffer<0: como proposta defensiva, um consumidor de quantidade fixa deve também verificar contagem recebida; isso não foi ensaiado nativamente.

Aplicações prioritárias para síntese: handles não são valores; buffers numéricos e decores têmidentidades distintas; deslocamento gráfico não garante alinhamento temporal; timers coalescem eventos e não são relógios decontagem garantida; EventChartCustom confirma enfileiramento, não processamento; benchmarksOpenCL impressos noPDF não são mediçõesStoikus; SQLite ainda é apenas abertura de capítulo neste recorte.

## REF-0001 — MQL5 Reference

Catálogo: PDF74–7284; texto efetivamente lido neste lote: PDF 3043–3238. Status: PARTIAL_SECTION_EXACT_PAGES_ONLY.

Recorte da referência geral: indicadores técnicos, frames de otimização, timers/eventos, ciclo OpenCL e abertura da introdução SQLite. Este registro cobre somente3043–3238, sem afirmar leitura integral do livro.

Usar estas páginas como fonte de contratos de plataforma; não como prova do comportamento implementado do Stoikus.

Fonte: [REF, MQL5 Reference, p.PDF 3043–3238]. Exemplos NOT_RUN; visual não inferido.

## REF-0960 — Technical Indicators

Catálogo: PDF2968–3174; texto efetivamente lido neste lote: PDF 3043–3174. Status: PARTIAL_SECTION_EXACT_PAGES_ONLY.

Ramo Technical Indicators parcialmente neste recorte(3043–3174). As 25 funções lidas criam handles; os exemplos verificam INVALID_HANDLE, consultam BarsCalculated, copiam buffers e liberam IndicatorRelease. O retorno inteiro não é a própria série calculada.

Proposta: encapsular identidade símbolo/timeframe/parâmetros, prontidão e validade dos dados; referências a indicadores não acrescentam sinais ao Monitor nem alteram critérios JPW.

Fonte: [REF, Technical Indicators, p.PDF 3043–3174]. Exemplos NOT_RUN; visual não inferido.

## REF-0975 — iDEMA

Catálogo: PDF 3043–3047; texto efetivamente lido neste lote: PDF 3043–3047. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iDEMA: um buffer, período de média, ma_shift e preço aplicado ou handle de outro indicador. Alternativa IndicatorCreate com IND_DEMA e3MqlParam inteiros. Exemplo ajusta PLOT_SHIFT e CopyBuffer(0,-shift,...).

Proposta: qualquer uso de DEMA deve registrar deslocamento separadamente do índice da barra; nenhum sinal DEMA do produto foi comprovado.

Fonte: [REF, iDEMA, p.PDF 3043–3047]. Exemplos NOT_RUN; visual não inferido.

## REF-0976 — iDeMarker

Catálogo: PDF3048–3052; texto efetivamente lido neste lote: PDF3048–3052. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iDeMarker: símbolo/timeframe/período, um buffer; exemplo usa14barras e níveis gráficos0.3/0.7. Criação genérica IND_DEMARKER recebe um parâmetro; cópia do buffer0 começa em0.

Os níveis demonstrativos não são norma JPW nem gatilho autorizado. Proposta de telemetria distinguir valor ausente de valor baixo.

Fonte: [REF, iDeMarker, p.PDF 3048–3052]. Exemplos NOT_RUN; visual não inferido.

## REF-0977 — iEnvelopes

Catálogo: PDF3053–3058; texto efetivamente lido neste lote: PDF3053–3058. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iEnvelopes: período, deslocamento, métodoMA, preço/handle e deviation em porcentagem. Buffers0UPPER_LINE e1LOWER_LINE; não há buffer central documentado neste contrato. MqlParam final TYPE_DOUBLE; cópias compensam -ma_shift em ambos.

Proposta: nomear unidade percentual, evitando confundir deviation0.1 com pontos monetários, ticks ou fração; guardar ambas linhas como mesma amostra temporal.

Fonte: [REF, iEnvelopes, p.PDF 3053–3058]. Exemplos NOT_RUN; visual não inferido.

## REF-0978 — iForce

Catálogo: PDF3059–3063; texto efetivamente lido neste lote: PDF3059–3063. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iForce retorna um buffer e recebe períodoMA, método de suavização e ENUM_APPLIED_VOLUME. Exemplo13/MODE_SMA/VOLUME_TICK; criação IND_FORCE com3inteiros e cópia buffer0.

Proposta: tornar explícita a origem tick/real do volume em qualquer pesquisa; força não comprova fluxo financeiro negociado.

Fonte: [REF, iForce, p.PDF 3059–3063]. Exemplos NOT_RUN; visual não inferido.

## REF-0979 — iFractals

Catálogo: PDF3064–3068; texto efetivamente lido neste lote: PDF3064–3068. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iFractals recebe somente símbolo/timeframe e oferece0UPPER_LINE,1LOWER_LINE. Exemplo liga dois buffers, DRAW_ARROW com217/218 e criação IND_FRACTALS sem lista de parâmetros. Há propriedades1buffer/1plot repetidas antes de2/2 no texto fonte.

Proposta: tratar linhas como dois canais; o trecho não estabelece estabilidade/confirmabilidade de fractais recentes, portanto não inferir ausência de repaint ou disponibilidade imediata.

Fonte: [REF, iFractals, p.PDF 3064–3068]. Exemplos NOT_RUN; visual não inferido.

## REF-0980 — iFrAMA

Catálogo: PDF3069–3073; texto efetivamente lido neste lote: PDF3069–3073. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iFrAMA: Fractal Adaptive Moving Average, um buffer; período, shift e preço/handle. IND_FRAMA usa3inteiros, PLOT_SHIFT e cópia em -shift.

Proposta: selecionar FrAMA exigiria pesquisa própria; nome adaptativo não implica superioridade nem presença no Stoikus.

Fonte: [REF, iFrAMA, p.PDF 3069–3073]. Exemplos NOT_RUN; visual não inferido.

## REF-0981 — iGator

Catálogo: PDF3074–3080; texto efetivamente lido neste lote: PDF3074–3080. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iGator mede diferenças das linhasAlligator azul/vermelha no histograma superior e vermelha/verde no inferior. Buffer0superior,1cor superior,2inferior,3cor inferior. Parâmetros de períodos/shifts de jaw/teeth/lips, método e preço. Shifts das linhas base não movem diretamente o histograma; exemplo usa min(jaw_shift,teeth_shift) para os dois plots e CopyBuffer com negativo desse shift.

Proposta: separar valor de índice de cor e alinhamento visual de alinhamento temporal. Não usar buffer1como série inferior; não inferir deslocamento pela aparência.

Fonte: [REF, iGator, p.PDF 3074–3080]. Exemplos NOT_RUN; visual não inferido.

## REF-0982 — iIchimoku

Catálogo: PDF3081–3087; texto efetivamente lido neste lote: PDF3081–3087. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iIchimoku recebe tenkan,kijun,senkouB. Buffers0Tenkan,1Kijun,2SenkouA,3SenkouB,4Chikou. Exemplo9/26/52; DRAW_FILLING reúne2buffers em umplot, total5buffers/4plots. PLOT_SHIFT da nuvem=kijun; cópiaSenkou usa -kijun, Chikou já vem armazenado deslocado e é copiado em0.

Proposta: testar explicitamente identidade temporal das linhas antes de compará-las ao preço; projetar linha no futuro não é evidência de informação futura disponível.

Fonte: [REF, iIchimoku, p.PDF 3081–3087]. Exemplos NOT_RUN; visual não inferido.

## REF-0983 — iBWMFI

Catálogo: PDF3088–3092; texto efetivamente lido neste lote: PDF3088–3092. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iBWMFI é Market Facilitation Index de BillWilliams, recebe ENUM_APPLIED_VOLUME. Prosa diz um buffer; exemplo declara2: valores0e índice de cores1, DRAW_COLOR_HISTOGRAM em4cores. IND_BWMFI recebe o volume como um inteiro.

Proposta: diferenciar BWMFI de MoneyFlowIndex(iMFI). Preservar ressalva entre buffer numérico único e buffer auxiliar de cor; não apagar essa nuance ao resumir.

Fonte: [REF, iBWMFI, p.PDF 3088–3092]. Exemplos NOT_RUN; visual não inferido.

## REF-0984 — iMomentum

Catálogo: PDF3093–3097; texto efetivamente lido neste lote: PDF3093–3097. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iMomentum: um buffer, mom_period e preço/handle. Exemplo14/PRICE_CLOSE, IND_MOMENTUM com2inteiros e buffer0sem shift.

Proposta: registrar parametrização com o valor; trecho não define regra de compra/venda nem limiar JPW.

Fonte: [REF, iMomentum, p.PDF 3093–3097]. Exemplos NOT_RUN; visual não inferido.

## REF-0985 — iMFI

Catálogo: PDF3098–3102; texto efetivamente lido neste lote: PDF3098–3102. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iMFI é Money Flow Index, período e tipo de volume. Exemplo um buffer, níveis20/80,14eVOLUME_TICK; IND_MFI com2inteiros.

Proposta: níveis20/80 são apresentação do exemplo, não aceite de estratégia; registrar tipo de volume para reproduzir a pesquisa.

Fonte: [REF, iMFI, p.PDF 3098–3102]. Exemplos NOT_RUN; visual não inferido.

## REF-0986 — iMA

Catálogo: PDF3103–3107; texto efetivamente lido neste lote: PDF3103–3107. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iMA: um buffer, período, shift, método e preço/handle. IND_MA recebe4MqlParam inteiros. Exemplo cria uma vez emOnInit, PLOT_SHIFT=ma_shift e CopyBuffer0começa em-ma_shift.

Proposta: demonstrar no manual que iMA retorna handle e não média pronta. O ciclo de vida e prontidão são reutilizáveis; não inferir que toda média do Stoikus use esta API.

Fonte: [REF, iMA, p.PDF 3103–3107]. Exemplos NOT_RUN; visual não inferido.

## REF-0987 — iOsMA

Catálogo: PDF3108–3112; texto efetivamente lido neste lote: PDF3108–3112. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iOsMA mostra diferença entre MACD e sua linha de sinal, com um buffer. RecebeEMA rápida/lenta, período de sinal e preço/handle; exemplo12/26/9 e DRAW_HISTOGRAM. Fonte observa que outros sistemas o chamam MACD histogram.

Proposta: em importação de pesquisas, comparar definição e buffers, pois o rótulo histogramaMACD é ambíguo entre plataformas.

Fonte: [REF, iOsMA, p.PDF 3108–3112]. Exemplos NOT_RUN; visual não inferido.

## REF-0988 — iMACD

Catálogo: PDF3113–3118; texto efetivamente lido neste lote: PDF3113–3118. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iMACD tem0MAIN_LINE e1SIGNAL_LINE e os mesmos quatro parâmetros principais doOsMA. No terminal aparece como histograma principal mais linha de sinal; em sistemas que chamamOsMA deMACDHistogram, oMACD é duas linhas. Exemplo copia separadamente0/1e usa IND_MACD.

Proposta: não identificar iMACD0com iOsMA0; avaliar diferenças por definição, não aparência. Nenhuma lucratividade é demonstrada.

Fonte: [REF, iMACD, p.PDF 3113–3118]. Exemplos NOT_RUN; visual não inferido.

## REF-0989 — iOBV

Catálogo: PDF3119–3123; texto efetivamente lido neste lote: PDF3119–3123. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iOBV: OnBalanceVolume de um buffer, símbolo/timeframe e ENUM_APPLIED_VOLUME. ExemploVOLUME_TICK e IND_OBV com umMqlParam.

Proposta: tratar escala cumulativa e tipo de volume como metadados de pesquisa; a seção não demonstra equivalência entre corretoras.

Fonte: [REF, iOBV, p.PDF 3119–3123]. Exemplos NOT_RUN; visual não inferido.

## REF-0990 — iSAR

Catálogo: PDF3124–3128; texto efetivamente lido neste lote: PDF3124–3128. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iSAR: um buffer; step e maximum são double, usualmente0.02/0.2. Exemplo IND_SAR com2TYPE_DOUBLE, DRAW_ARROW código159e cópia0sem shift.

O nome StopAndReverse não executa ordem nem configura stop. Uso como trailing doSupervisor seria proposta separada e não autorizado por esta leitura.

Fonte: [REF, iSAR, p.PDF 3124–3128]. Exemplos NOT_RUN; visual não inferido.

## REF-0991 — iRSI

Catálogo: PDF3129–3133; texto efetivamente lido neste lote: PDF3129–3133. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iRSI: um buffer; período e preço/handle. Exemplo14/PRICE_CLOSE, janela0–100, níveis70/30 e IND_RSI com2inteiros.

Proposta: preservar a diferença entre níveis de visualização e critérios de negócio. O trecho não autoriza trocar critérios doMonitor porRSI.

Fonte: [REF, iRSI, p.PDF 3129–3133]. Exemplos NOT_RUN; visual não inferido.

## REF-0992 — iRVI

Catálogo: PDF3134–3138; texto efetivamente lido neste lote: PDF3134–3138. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iRVI: RelativeVigorIndex recebe período de cálculo e fornece0MAIN_LINE/1SIGNAL_LINE. Exemplo10, IND_RVI com um inteiro e duas cópias. StringFormat do exemplo contém mais especificadores que valores aparentes.

Proposta: manter assinatura e buffer como contrato; reconstruir exemplos originais verificáveis em vez de copiar código dePDF com inconsistências editoriais.

Fonte: [REF, iRVI, p.PDF 3134–3138]. Exemplos NOT_RUN; visual não inferido.

## REF-0993 — iStdDev

Catálogo: PDF3139–3143; texto efetivamente lido neste lote: PDF3139–3143. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iStdDev: um buffer, período, shift, métodoMA, preço/handle. Exemplo20/MODE_SMA, IND_STDDEV com4inteiros e cópia buffer0em-shift.

Proposta: volatilidade de indicador é distinta do limite normativo de risco ou exposição. Seria preciso declarar janela e unidade antes de usar em estudo.

Fonte: [REF, iStdDev, p.PDF 3139–3143]. Exemplos NOT_RUN; visual não inferido.

## REF-0994 — iStochastic

Catálogo: PDF3144–3149; texto efetivamente lido neste lote: PDF3144–3149. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iStochastic: Kperiod,Dperiod,slowing,métodoMA e ENUM_STO_PRICE; não é ENUM_APPLIED_PRICE. Buffers0MAIN_LINE e1SIGNAL_LINE. Exemplo5/3/3,STO_LOWHIGH;5MqlParam. Janela0–100 mas níveis textuais-100/100 no exemplo, uma inconsistência a preservar.

Proposta: testar configuração e limites em um candidato compilável; não promover níveis do exemplo a norma nem aceitar preço de outro enum por conversão silenciosa.

Fonte: [REF, iStochastic, p.PDF 3144–3149]. Exemplos NOT_RUN; visual não inferido.

## REF-0995 — iTEMA

Catálogo: PDF3150–3154; texto efetivamente lido neste lote: PDF3150–3154. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iTEMA: TripleExponentialMovingAverage de um buffer, período/shift/preço ou handle. IND_TEMA recebe3inteiros; exemploPLOT_SHIFT e CopyBuffer em-shift.

Proposta: distinguir a médiaTEMA do osciladorTriX; parametrizações semelhantes não fazem deles canais intercambiáveis.

Fonte: [REF, iTEMA, p.PDF 3150–3154]. Exemplos NOT_RUN; visual não inferido.

## REF-0996 — iTriX

Catálogo: PDF3155–3159; texto efetivamente lido neste lote: PDF3155–3159. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iTriX: oscilador TripleExponentialMovingAverages, um buffer; período e preço/handle, sem argumento ma_shift. IND_TRIX com2inteiros, exemplo14e buffer0.

Proposta: não inventar parâmetro de deslocamento por analogia aoTEMA; não afirmar adoção peloStoikus.

Fonte: [REF, iTriX, p.PDF 3155–3159]. Exemplos NOT_RUN; visual não inferido.

## REF-0997 — iWPR

Catálogo: PDF3160–3164; texto efetivamente lido neste lote: PDF3160–3164. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iWPR: LarryWilliamsPercentRange de um buffer, calc_period; exemplo14, intervalo gráfico-100a0e níveis-20/-80. IND_WPR recebe um inteiro.

Proposta: manter sinal e escala negativos ao comparar estudos; não transplantar limiares70/30deRSI.

Fonte: [REF, iWPR, p.PDF 3160–3164]. Exemplos NOT_RUN; visual não inferido.

## REF-0998 — iVIDyA

Catálogo: PDF3165–3169; texto efetivamente lido neste lote: PDF3165–3169. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iVIDyA: média dinâmica de um buffer; cmo_period controlaChandeMomentum e ema_period o fator de suavização, mais shift e preço/handle. IND_VIDYA usa4inteiros; exemplo15/12, cópia0em-shift.

Proposta: identificar os dois períodos por função, evitando uma configuração genérica de períodoMA que perca informação.

Fonte: [REF, iVIDyA, p.PDF 3165–3169]. Exemplos NOT_RUN; visual não inferido.

## REF-0999 — iVolumes

Catálogo: PDF3170–3174; texto efetivamente lido neste lote: PDF3170–3174. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

iVolumes recebe volume aplicado e retorna handle. Prosa diz um buffer; exemplo define2, valores0e cores1, verdes/vermelhas, viaIND_VOLUMES com um inteiro.

Proposta: não interpretar cor como volume nem assumir volume real quando padrão éVOLUME_TICK. O cabeçalho simplificado não elimina buffer de cor.

Fonte: [REF, iVolumes, p.PDF 3170–3174]. Exemplos NOT_RUN; visual não inferido.

## REF-1000 — Working with Optimization Results

Catálogo: PDF3175–3186; texto efetivamente lido neste lote: PDF3175–3186. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

Frames permitem transmitir dados simples/estruturas sem strings, objetos de classe ou arrays dinâmicos entre agentes e terminal. Recepção geraTesterPass; frames gravados emEA.MQD emMQL5/Files/Tester, na ordem de chegada. Fonte não limita quantidade de frames; CloudNetwork limita escrita em disco eRAM a4GBcada e pode cobrar tempo mesmo sem resultado.

Proposta de pesquisa/harness: incluir pass, parâmetros e versão de esquema para ordenar e reproduzir; chegada não é ordem de passes. Essas condições da fonte não verificam disponibilidade atual deinfra nem pilotoStoikus.

Fonte: [REF, Working with Optimization Results, p.PDF 3175–3186]. Exemplos NOT_RUN; visual não inferido.

## REF-1001 — FrameFirst

Catálogo: PDF3177–3177; texto efetivamente lido neste lote: PDF3177–3177. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

FrameFirst move cursor ao início e limpa filtro. Retorna bool; falha consultável viaGetLastError.

Proposta: iniciar consolidação completa com reset explícito, evitando herdar filtro de consulta anterior.

Fonte: [REF, FrameFirst, p.PDF 3177–3177]. Exemplos NOT_RUN; visual não inferido.

## REF-1002 — FrameFilter

Catálogo: PDF3178–3178; texto efetivamente lido neste lote: PDF3178–3178. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

FrameFilter(name,id) define filtro e reinicia cursor. name vazio filtra sóid; id=ULONG_MAX filtra sótexto; combinação vazio/ULONG_MAX equivaleFrameFirst.

Proposta: separar rótulo de família e id de esquema/caso em frames de pesquisa; documentar os sentinelas para não perder registros.

Fonte: [REF, FrameFilter, p.PDF 3178–3178]. Exemplos NOT_RUN; visual não inferido.

## REF-1003 — FrameNext

Catálogo: PDF3179–3179; texto efetivamente lido neste lote: PDF3179–3179. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

FrameNext tem variante com pass/name/id/value e outra com data[] adicional; lê um frame e avança. Aplicação deve interpretar corretamente tipo/conteúdo do array.

Proposta: conferir esquema, comprimento e identidade do pass antes de agregar dados; true não comprova significado do payload.

Fonte: [REF, FrameNext, p.PDF 3179–3179]. Exemplos NOT_RUN; visual não inferido.

## REF-1004 — FrameInputs

Catálogo: PDF3180–3180; texto efetivamente lido neste lote: PDF3180–3180. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

FrameInputs(pass,parameters[],parameters_count) devolve strings parameterN=valueN e contagem para o pass indicado.

Proposta: ligar parâmetros à evidência de cada caso e conservar pass original; não inferir configuração pela posição de chegada do frame.

Fonte: [REF, FrameInputs, p.PDF 3180–3180]. Exemplos NOT_RUN; visual não inferido.

## REF-1005 — FrameAdd

Catálogo: PDF3181–3181; texto efetivamente lido neste lote: PDF3181–3181. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

FrameAdd oferece overload arquivo e array passado por referência; name/id filtráveis e value numérico para resultado único semelhanteOnTester. Arquivo deve estar emMQL5/Files. Bool maisGetLastError.

Proposta: preferir payload simples em memória para coleta de pesquisa quando adequado; validar retorno e não confundir frame criado com aprovação de estratégia.

Fonte: [REF, FrameAdd, p.PDF 3181–3181]. Exemplos NOT_RUN; visual não inferido.

## REF-1006 — ParameterGetRange

Catálogo: PDF3182–3184; texto efetivamente lido neste lote: PDF3182–3184. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

ParameterGetRange devolve enable,value,start,step,stop por referência; overload long para inteiros/bool/enums e double para reais. Chamável apenasOnTesterInit,OnTesterPass,OnTesterDeinit. OnTesterInit pode usarresultado para redefinir otimização viaSetRange.

Proposta: registrar faixas efetivas, pois configurações visuais podem ser substituídas; fora dos handlers permitidos seria violação de contrato.

Fonte: [REF, ParameterGetRange, p.PDF 3182–3184]. Exemplos NOT_RUN; visual não inferido.

## REF-1007 — ParameterSetRange

Catálogo: PDF3185–3186; texto efetivamente lido neste lote: PDF3185–3186. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

ParameterSetRange altera enable,valor,início,passo,fim, com overload long/double. SomenteOnTesterInit ao lançar otimização; pode excluir parâmetro independentemente daUI e incluir variável sinput.

Proposta: qualquer estudo deve salvar faixas após política aplicada; não alterar parâmetros de produção como consequência automática da otimização.

Fonte: [REF, ParameterSetRange, p.PDF 3185–3186]. Exemplos NOT_RUN; visual não inferido.

## REF-1008 — Working with Events

Catálogo: PDF3187–3196; texto efetivamente lido neste lote: PDF3187–3196. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

Grupo reúne geradoresTimer, desligamento e evento customizado; handlers de eventos predefinidos são funções separadas.

Aplicação conceitual aoMonitor orientado aeventos: organizar ciclo, filas e comunicação sem alegar inspeção/alteração da implementação.

Fonte: [REF, Working with Events, p.PDF 3187–3196]. Exemplos NOT_RUN; visual não inferido.

## REF-1009 — EventSetMillisecondTimer

Catálogo: PDF3188–3188; texto efetivamente lido neste lote: PDF3188–3188. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

EventSetMillisecondTimer recebe intervalo subsegundo e retorna bool. Timer real não gera mais de uma vez a cada10–16ms por limitação dehardware; reduzir período aumenta tempo de teste. Só umtimer por programa; se eventoTimer já está na fila ou processando, novoTimer não é adicionado.

Proposta: medir tempo decorrido por timestamps e tolerâncias, nunca contar chamadasOnTimer como relógio garantido; handlers curtos e teste de atraso seriam exigidos paraMonitor.

Fonte: [REF, EventSetMillisecondTimer, p.PDF 3188–3188]. Exemplos NOT_RUN; visual não inferido.

## REF-1010 — EventSetTimer

Catálogo: PDF3189–3189; texto efetivamente lido neste lote: PDF3189–3189. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

EventSetTimer(seconds) normalmente emOnInit/construtor; OnTimer processa. CadaEA/indicador tem timer próprio, no máximo um por programa. EventoTimer pendente/processando causa descarte do novo evento; parada destrói timer não desligado.

Proposta: alertas e agendamentos dos quatro programas devem reconciliar estado atual após atraso; periodicidade configurada não garante contagem nem execução pontual.

Fonte: [REF, EventSetTimer, p.PDF 3189–3189]. Exemplos NOT_RUN; visual não inferido.

## REF-1011 — EventKillTimer

Catálogo: PDF3190–3190; texto efetivamente lido neste lote: PDF3190–3190. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

EventKillTimer não retorna valor e interrompe geraçãoTimer. NormalmenteOnDeinit se iniciadoOnInit, oudestrutor se criado no construtor; parada do programa também odestrói.

Proposta: parear explicitamente criação e desligamento para ciclo devida legível e ensaiar reanexação; ausência de retorno não prova que restante da limpeza ocorreu.

Fonte: [REF, EventKillTimer, p.PDF 3190–3190]. Exemplos NOT_RUN; visual não inferido.

## REF-1012 — EventChartCustom

Catálogo: PDF3191–3196; texto efetivamente lido neste lote: PDF3191–3196. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

EventChartCustom envia para chart_id(0atual), acrescentaCHARTEVENT_CUSTOM ao ushortcustom_event_id e transportalong,double,string; sparam acima63caracteres é truncado. true confirma somente inclusão na fila receptora. Tabela distingue teclas,repetição,mouseXY/máscaras,criação/remoção opcionais,clique/drag/endedit/alteração. Exemplo botão alternaID+1/+999e broadcast percorreChartFirst/Next limitadoCHARTS_MAX.

Proposta: protocolo entre componentes deve caber em63chars ou referenciar registro, validarId/remetente/esquema e confirmar processamento separadamente. Enfileirar não armaSupervisor nem garante processamento/aceite; nenhuma integração foi implementada.

Fonte: [REF, EventChartCustom, p.PDF 3191–3196]. Exemplos NOT_RUN; visual não inferido.

## REF-1013 — Working with OpenCL

Catálogo: PDF3197–3237; texto efetivamente lido neste lote: PDF3197–3237. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

OpenCL suporta classe de cálculos paralelos emdispositivos compatíveis; fonte cita1.1+. double pode exigir pragma cl_khr_fp64 eGPU compatível; pragma não cria capacidade inexistente. ErroOpenCL é obtido porCLGetInfoInteger(0,CL_LAST_ERROR), descrição porCLGetInfoString(código ouCL_LAST_ERROR,CL_ERROR_DESCRIPTION,...). RecomendaCL separado como recurso.

OpenCL é pesquisa futura, não componente atual declarado doStoikus. Proposta: avaliar capacidade, precisão, custo de transferências ebaselineCPU antes de qualquer adoção; todos exemplos lidos NOT_RUN.

Fonte: [REF, Working with OpenCL, p.PDF 3197–3237]. Exemplos NOT_RUN; visual não inferido.

## REF-1014 — CLHandleType

Catálogo: PDF3199–3199; texto efetivamente lido neste lote: PDF3199–3199. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

CLHandleType retorna enumINVALID,CONTEXT,PROGRAM,KERNEL,BUFFER parahandleOpenCL.

Proposta: diagnosticar confusão entre handles sem tratar todos inteiros como identificadores intercambiáveis.

Fonte: [REF, CLHandleType, p.PDF 3199–3199]. Exemplos NOT_RUN; visual não inferido.

## REF-1015 — CLGetInfoInteger

Catálogo: PDF3200–3202; texto efetivamente lido neste lote: PDF3200–3202. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

CLGetInfoInteger retorna long ou-1erro, dispositivos numerados desde0; CL_DEVICE_COUNT ignora handle. Propriedades incluem tipo/vendor/unidades/clock/memórias,tamanho de buffer/grupo/local/private e últimoerro. Enum tiposCPU,GPU,ACCELERATOR,DEFAULT,CUSTOM; exemplo criaGPUcontexto, imprime e libera.

Proposta: guardar capacidades reais do ambiente e dimensionar trabalho pelo dispositivo/kernel; nomeGPU não é evidência de desempenho nem suporte double.

Fonte: [REF, CLGetInfoInteger, p.PDF 3200–3202]. Exemplos NOT_RUN; visual não inferido.

## REF-1016 — CLGetInfoString

Catálogo: PDF3203–3205; texto efetivamente lido neste lote: PDF3203–3205. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

CLGetInfoString retorna bool e string porreferência para plataforma, versão,perfil,extensões,dispositivo,driver,OpenCLC,kernels e descrição deerro. Exemplo consulta várias propriedades e libera contexto.

Proposta: anexar metadados driver/versões ao resultado de pesquisa para comparar ambientes; descrição doúltimoerro deve ser capturada antes de outras chamadas alterarem diagnóstico.

Fonte: [REF, CLGetInfoString, p.PDF 3203–3205]. Exemplos NOT_RUN; visual não inferido.

## REF-1017 — CLContextCreate

Catálogo: PDF3206–3206; texto efetivamente lido neste lote: PDF3206–3206. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

CLContextCreate(device=CL_USE_ANY) aceita índice, ANY,CPU_ONLY,GPU_ONLY,GPU_DOUBLE_ONLY; retorna handle ou-1.

Proposta: política de seleção deve ser explícita; fallbackCPU sobANY não deve ser reportado como aceleraçãoGPU comprovada.

Fonte: [REF, CLContextCreate, p.PDF 3206–3206]. Exemplos NOT_RUN; visual não inferido.

## REF-1018 — CLContextFree

Catálogo: PDF3207–3207; texto efetivamente lido neste lote: PDF3207–3207. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

CLContextFree(context) remove contexto, sem retorno; _LastError muda emerro interno.

Proposta: liberar contexto após dependentes emtodas saídas de pesquisacandidata; não confirmar liberação pelo retorno inexistente.

Fonte: [REF, CLContextFree, p.PDF 3207–3207]. Exemplos NOT_RUN; visual não inferido.

## REF-1019 — CLGetDeviceInfo

Catálogo: PDF3208–3212; texto efetivamente lido neste lote: PDF3208–3212. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

CLGetDeviceInfo recebe índice/contexto,property_id,uchar[] esaída size. Tabela0x1000–0x104B cobre tipo,larguras vetoriais,dimensões/grupos,memória,imagens,alinhamento,FP,endianness,compilador,versão,partição,interoperabilidade. Exemplo percorredispositivos e convertebuffer dofabricante emstring. Texto de size naassinatura conflita comdescrição; descrição indica tamanho recebido.

Proposta: preferir APIs tipadas para propriedades usuais; quando usar bytes validar tamanho/tipo e não copiar comentário deoffset. Exemplo não libera todoscontextos no laço, portanto não é modelo completo de limpeza.

Fonte: [REF, CLGetDeviceInfo, p.PDF 3208–3212]. Exemplos NOT_RUN; visual não inferido.

## REF-1020 — CLProgramCreate

Catálogo: PDF3213–3217; texto efetivamente lido neste lote: PDF3213–3217. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

CLProgramCreate compila string fonte emcontexto; overload devolvebuild_log. Retorna handle/-1; errosinvalidhandle,param,memory,programcreate. ExemploCPU/GPU dobra5arrays de100doubles, envia,executa,lê, compara erro absoluto agregado e libera buffer/kernel/program/contexto. Kernel usa get_global_id eoffset id*N.

Proposta: conservarlog compilador e verificar cada operação; guardafonte id>total_arrays não protegeid==total_arrays se grade aumentar, embora grade doexemplo tenhaTOTAL_ARRAYS itens. Não importar exemplo sem revisão delimites; nenhum resultado foi executado.

Fonte: [REF, CLProgramCreate, p.PDF 3213–3217]. Exemplos NOT_RUN; visual não inferido.

## REF-1021 — CLProgramFree

Catálogo: PDF3218–3218; texto efetivamente lido neste lote: PDF3218–3218. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

CLProgramFree removeprograma, void, erro interno em_LastError.

Proposta: liberar depois doskernelsdependentes e antes docontexto emtodas falhas.

Fonte: [REF, CLProgramFree, p.PDF 3218–3218]. Exemplos NOT_RUN; visual não inferido.

## REF-1022 — CLKernelCreate

Catálogo: PDF3219–3219; texto efetivamente lido neste lote: PDF3219–3219. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

CLKernelCreate(program,kernel_name) encontra função deentrada, retorna handle/-1. Nomeacima127caracteres geraERR_OPENCL_TOO_LONG_KERNEL_NAME; demaisfalhasinvalidhandle,param,criação.

Proposta: fixar/registrar nome deentrada e separar erro decompilação deerro decriação dokernel.

Fonte: [REF, CLKernelCreate, p.PDF 3219–3219]. Exemplos NOT_RUN; visual não inferido.

## REF-1023 — CLKernelFree

Catálogo: PDF3220–3220; texto efetivamente lido neste lote: PDF3220–3220. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

CLKernelFree(kernel) removefunção deentrada; void eerro interno consultável. Descrição deparâmetro chama kernel_name apesar daassinaturakernel.

Proposta: seguirassinatura tipada everificarciclo devida, sem inventar argumento textual para liberação.

Fonte: [REF, CLKernelFree, p.PDF 3220–3220]. Exemplos NOT_RUN; visual não inferido.

## REF-1024 — CLSetKernelArg

Catálogo: PDF3221–3221; texto efetivamente lido neste lote: PDF3221–3221. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

CLSetKernelArg vincula valor escalar àposição arg_index iniciada em0; bool; errosparam/handle/kernelparameter.

Proposta: espelhar tipo/tamanho/ordem deassinaturaOpenCLC evalidar cadaretornopara evitar execução comargumentos incompletos.

Fonte: [REF, CLSetKernelArg, p.PDF 3221–3221]. Exemplos NOT_RUN; visual não inferido.

## REF-1025 — CLSetKernelArgMem

Catálogo: PDF3222–3222; texto efetivamente lido neste lote: PDF3222–3222. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

CLSetKernelArgMem vincula handle debufferOpenCL comoargumento deumkernel; posição inicia em0e retorno ébool.

Proposta: distinguir passagem dehandle memória doconteúdo escalar; guardar vínculo buffer/kernel atéexecução/leitura completas.

Fonte: [REF, CLSetKernelArgMem, p.PDF 3222–3222]. Exemplos NOT_RUN; visual não inferido.

## REF-1026 — CLSetKernelArgMemLocal

Catálogo: PDF3223–3223; texto efetivamente lido neste lote: PDF3223–3223. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

CLSetKernelArgMemLocal reserva argumento debufferlocal por local_mem_size embytes, não pornúmero deelementos; retorna bool.

Proposta: calcular bytes comtipo ecompararcapacidade localdogrupo/dispositivo; não confundirlocal comglobalbuffer.

Fonte: [REF, CLSetKernelArgMemLocal, p.PDF 3223–3223]. Exemplos NOT_RUN; visual não inferido.

## REF-1027 — CLBufferCreate

Catálogo: PDF3224–3224; texto efetivamente lido neste lote: PDF3224–3224. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

CLBufferCreate(context,uintsize,flags) aloca bytes; flagsREAD_WRITE,WRITE_ONLY,READ_ONLY,ALLOC_HOST_PTR. Retorna handle/-1; erroscontexto,memória,buffercreate.

Proposta: dimensionar elementos×sizeof comverificação deoverflow/capacidade ealinharflags aouso dokernel; alocação não inicia dados válidos automaticamente.

Fonte: [REF, CLBufferCreate, p.PDF 3224–3224]. Exemplos NOT_RUN; visual não inferido.

## REF-1028 — CLBufferFree

Catálogo: PDF3225–3225; texto efetivamente lido neste lote: PDF3225–3225. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

CLBufferFree(buffer) removebuffer, semretorno e_LastError emerrointerno.

Proposta: liberar cadabuffer adquirido emfalha parcial efluxonormal, antesdekernel/program/contexto conforme cicloexemplificado.

Fonte: [REF, CLBufferFree, p.PDF 3225–3225]. Exemplos NOT_RUN; visual não inferido.

## REF-1029 — CLBufferWrite

Catálogo: PDF3226–3230; texto efetivamente lido neste lote: PDF3226–3230. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

CLBufferWrite array: buffer_offset embytes,data_offset emelementos,data_count elementos; retornaquantidade,0erro. AS_SERIES afetaíndice1D; multidimensionaléachatado eoffset contaelementos totais. Overloadsmatrix/vector descritos comboolsucesso apesarassinaturaextraída uint; parâmetrosmat/vec têmcomentáriodereadindesejado. Exemplo M3000×K2000 porK×N3000compara laço,MatMul,OpenCLfloat; grade2D(M,N),3buffers evínculos.

Proposta: não misturar unidades deoffset; verificarquantidade esperadaou contrato sobrecarga. Tempos54750/4578/922ms ezero diferenças a1e-12 são comentários dafonte, não benchmarklocal nemgarantiaGPU. MediçãoOpenCL apresentada omite setup ewrite anteriores, portanto comparaçãofimafim exige outra instrumentação.

Fonte: [REF, CLBufferWrite, p.PDF 3226–3230]. Exemplos NOT_RUN; visual não inferido.

## REF-1030 — CLBufferRead

Catálogo: PDF3231–3234; texto efetivamente lido neste lote: PDF3231–3234. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

CLBufferRead array devolvecontagem,0erro, offsetbufferbytes eoffsetarrayelementos. Matriz pode manterdimensionamento ou receber rows/cols juntos, -1mantém; vetor size-1mantém. AS_SERIES1Deachatamento multidimensional tambémimportam. ExemploPi integra1e9passos,40000tarefas×25000somas, vetor.Sum×step;99.98ms écomentárioda fonte. Equação gráfica dap3232não aparececompleta notexto.

Proposta: validar contagem/dimensões eprecisão contraCPU antesdeconsumir; não inferir fórmula visual daextração nem declararruntimePi. Assinaturasextraídasconst/size-1euintvsboolprecisam confirmação no compiladorcandidadonativo antesdeusar.

Fonte: [REF, CLBufferRead, p.PDF 3231–3234]. Exemplos NOT_RUN; visual não inferido.

## REF-1031 — CLExecute

Catálogo: PDF3235–3236; texto efetivamente lido neste lote: PDF3235–3236. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

CLExecute oferece kernelúnico,grade global comdimensão/offset/tamanho evariante comgrade local. Exemplo3D40×100×320=1280000tarefas; local10×10×10divide cadadimensão semresto. Retornabool.

Proposta: validar dimensões,divisibilidade,capacidade eguardasdekernel; true da chamada não substitui status/resultadovalidado.

Fonte: [REF, CLExecute, p.PDF 3235–3236]. Exemplos NOT_RUN; visual não inferido.

## REF-1032 — CLExecutionStatus

Catálogo: PDF3237–3237; texto efetivamente lido neste lote: PDF3237–3237. Status: SEMANTIC_FULL_EXTRACTED_TEXT.

CLExecutionStatus(kernel) retorna0COMPLETE,1RUNNING,2SUBMITTED,3QUEUED e-1erro da consulta.

Proposta: distinguir submissão,execuçãoeconclusão; não tratar qualquervalornão-negativo como dadofinalpronto. Polling nãodeve bloquearMonitor.

Fonte: [REF, CLExecutionStatus, p.PDF 3237–3237]. Exemplos NOT_RUN; visual não inferido.

## REF-1033 — Working with databases

Catálogo: PDF 3238–3317; texto efetivamente lido neste lote: PDF 3238–3238. Status: PARTIAL_SECTION_EXACT_PAGES_ONLY.

Somenteintroduçãop3238lida, restante3239–3317fora dorecorte. SQLite emarquivoúnico, usosincluemhistórico,resultadosteste/otimização,intercâmbio,configuração/estado. DatabaseReadBind lê campos emestrutura; MEMORY éprivadoàaplicação enãocompartilhado; inserções/alterações emdisco devemagrupartransaçõesBegin/Commit/Rollback. Lista inicial atéDatabaseBind.

Proposta futura dearquivopesquisa; não afirmaSQLiteprodutivoStoikus. A promessa deaceleração emcentenasvezes éda fonte, não medição. ContratosAPIespecíficos nãoforamestudados nestapágina eprecisamcontinuação.

Fonte: [REF, Working with databases, p.PDF 3238–3238]. Exemplos NOT_RUN; visual não inferido.

## Integridade e continuidade

Cobertura196 páginas únicas, 61 IDs/títulos cruzados incluindo ramos. Nenhuma página restante no intervalo3043–3238. Ledger: reference-batch-10b-coverage.json. Os ramosREF-0001,REF-0960eREF-1033são explicitamente parciais como seções globais; REF-1000,REF-1008eREF-1013eosfilhosdesteintervalotêmtexto integral coberto. A introduçãoSQLite continua dap3239emoutrolote.
