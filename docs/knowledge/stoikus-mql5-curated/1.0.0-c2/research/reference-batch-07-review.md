# REF — revisão semântica, lote 07 (PDF 1948–2289)

Leitura integral real do corpo textual de 342 páginas físicas, em 24 lotes de até 29.000 caracteres (656.100 com marcadores; sem truncamento na saída das ferramentas). A extração preservada possui linhas longas cortadas e áreas “Result” sem conteúdo textual; esta leitura não afirma conferência visual dessas imagens, tabelas como imagem, fórmulas com sobrescritos ou linhas além da borda. Exemplos: **MQL_NOT_RUN**. Não houve compilação MT5/EX5, instalação, piloto ou alteração de produto/kit. Página1947 foi relida para continuidade; é somente contexto e não integra as342 páginas deste lote.

## Separação entre documento, código observado e proposta

O contrato da plataforma é documentado em cada entrada abaixo. A conexão atual foi verificada por leitura estática de trechos no checkout `/private/tmp/jpw-stoikus-continuity-20261014`, sem executar MQL: `mt5/jpw-alavancagem-atual/MQL5/Experts/JPWealth/JPW_Stoikus_Monitor.mq5:200` inicializa timer1s com falha explícita; linha216 remove timer,217–224 encaminha sinal transacional e226 inicia ciclo com GetTickCount64. Não há necessidade de OnTick para este monitor. Desabilitar AutoTrading não impede monitoramento, mas isso não autoriza armar Supervisor.

`MQL5/Include/JPWealth/JPW_Stoikus_Observer_Runtime.mqh:473–510`, função JPWObserverATRAtDeal, recebe timestamp do deal em milissegundos, converte para segundos, procura shiftH4, exige SERIES_SYNCHRONIZED, mínimo shift+56 emBars eBarsCalculated, cópias ==1, barra encerrada até a execução, mesmo timestamp antes/depois deCopyBuffer, valor diferenteEMPTY_VALUE e finito positivo; libera handle. É evidência estática de intenção causal, sem prova nativa. `JPW_Alavancagem_RaizN_Live.mqh:105–139` lê aberturas0/1 eATRshift1 com56 barras/calculadas. São contextos distintos: última barra fechada agora não substitui barra concluída no instante de um deal antigo.

No calendário,DOM,ticks históricos,otimização e funções matemáticas especializadas, não foi comprovado uso atual por esta inspeção limitada; as aplicações indicadas são propostas futuras ou conhecimento sem uso específico confirmado. A ausência de chamada em um trecho não demonstra ausência global. Resultados e números impressos nos exemplos são bibliografia, não telemetria atual nem regrasJPW.

## Causalidade, unidades e falhas que a síntese deve preservar

Um callback não é um tick, uma solicitação não é um deal, e horário de abertura não certifica fechamento. As filas são serializadas e limitadas; Tick/Timer podem coalescer,Book tem contrato específico de enfileirar eTransaction pode perder eventos por supersessão na fila1024. A proposta de reconciliação deve tratar eventos como indícios, consultar fonte autoritativa e manter handlers curtos, sem prometer replay perfeito a partir de callbacks.

Segundos datetime, milissegundos deMqlTick e contador monotônico não devem ser somados sem conversão. TimeCurrent pode estagnar sem cotações eTimeTradeServer é estimativa dependentePC; tester iguala relógios que em operação real divergem. Sessões fornecem segundos desde meia-noite e ignoram data, não horas absolutas nem quatro programas normativosJPW. Point/Digits não equivalem a pip,ticksize,tickvalue ou dinheiro da conta. Tickvolume e realvolume são séries diferentes.

Handle válido não implica cálculo pronto; sincronização de símbolo não implica série pronta; countpositivo não implica cópia completa. Arrays copiados colocam o elemento mais antigo no começo físico mesmo com AS_SERIES; buffers deindicador têm capacidade gerida terminal. EMPTY_VALUE pode ser finito: MathIsValidNumber sozinho não resolve disponibilidade nem unidade. Calendário usa LONG_MIN antes de divisão por1e6, além de unidade/multiplicador do metadado. Atualização revisada de calendário não pode ser usada retrospectivamente como se conhecida na publicação inicial.

## Anomalias bibliográficas e limites qualificados

A extração mostra títuloMathLog paraMathLog10(p1957), INF sem sinal para logs emzero enquanto saída mostra-inf(p1953–1958), parâmetro new_capacity noStringSetLength(p2031), “cópia” noStringSetCharacter apesar debool/string&(p2035), pos noStringSplit(p2037), TerminalInfoDouble com exemploTerminalInfoInteger(p2069), marcação[in] emsaídas deMarginRate/MarketBookGet(p2153/2164). Não foram corrigidas fontes.

MathTan traz “263”(p1983), potencial perda de2^63 emsobrescrito; sem inspeção visual o limite não deve ser citado como263. MathExpm1 dizunderflow0(p1987), mas a expressão exp(x)-1 tende a-1 para x muito negativo: registrar como inconsistência a confirmar nativamente, não comportamento medido. Gráficos repetem chamadaCurvePlot(y_array,color) e assinatura visível comx_array,y_array,color, além de linhas cortadas: não são programas prontos para copiar. MathArctanh sample começa em-1 apesar de domínio aberto(p2000).

As assinaturas extraídasOnTradeTransaction()/OnChartEvent() abrem/fecham parênteses antes dos argumentos(p2106/2115); os exemplos posteriores esclarecem sintaxe. Quantidade de IDs custom diz65535 embora offset0..65535 inclua65536(p2115–2116); sampleid>CHARTEVENT_CUSTOM omite0(p2120). O agrupamento transacional por lacuna1s(p2108) é heurística, não identidade causal, e o sample consultaresult fora do tipoREQUEST. OnTimer soma1porcallback(p2100), contrariando uso como relógio confiável sob coalescência.

CalendarValueHistoryByEvent/History exemplos usamintcomo bool(p2181/2184): -1erro pode entrar no ramo desucesso. Reduzir arrays e acessarevents[6] sem contagemvalidada não é seguro; seleçãoNonfarm porsubstring(p2188) é ambígua. Erros persistem semReset(p2189/2193). PaísISO é descrição simplificada: aparecemWW0 eEU999(p2174), não somente paísesISO.

O loader histórico(p2206) tem “{f”, nomenclaturaMQL5InfoInteger antiga e espera ativa; prosa recomenda modelo deeventos paraEA/indicadores(p2205). Referência2GB32bit(p2205) é contextual, não limite universalatual. ExemploBars não recalcula variávelbars após espera(p2216). ExemplosCopyTickVolume eCopySeries acessam arrays sem garantir contagem suficiente(p2258/2238). CopyTicks sample usaMathMax(100,ticks)(p2269), permitindoíndicealémdocopiado se menos100, e formataBid usando tick.ask(p2270); comentários primeiro/último não devem superar contrato índice0maisantigo. iHighest pesquisaMODE_CLOSE maslêHigh(p2282), iLowest pesquisaREAL_VOLUME maslêLow(p2285). ExemploiBarShift declara2002.04.25 mas saída2018.06.10(p2275–2277); não é reprodução idêntica. Todas essas constatações são estáticas e limitadas ao texto extraído.

## Cobertura por ID/seção

Pais descritivos não representam segunda leitura dos filhos; escopos parciais são explícitos. A referência física exata acompanha cada seção.

### REF-0588 — Math Functions

[REF, Math Functions, p.PDF 1948–2014] · partial_parent. Continuação do capítulo REF-0588 iniciada no lote06; aqui MathExp..MathSwap. Domínio e finitude não estabelecem unidade, fórmulaJPW ou execução. Página1947 relida apenas contexto (final gráfico/screenshot da seção anterior), não duplicada na lista342.

### REF-0597 — MathExp

[REF, MathExp, p.PDF 1948–1950] · full_section. Calcula exp(x); overflow produz INF e underflow 0. Proposta: validar domínio e finitude antes de usar crescimento; nenhum uso específico confirmado.

### REF-0598 — MathFloor

[REF, MathFloor, p.PDF 1951–1952] · full_section. Maior inteiro <=x, retorno double; arredondamento para baixo difere de truncar negativos. Proposta: discretização apenas com unidade e política declaradas.

### REF-0599 — MathLog

[REF, MathLog, p.PDF 1953–1956] · full_section. Logaritmo natural; negativos NaN e zero não finito. Prosa INF versus exemplo -inf exige qualificação de sinal, não aceitação silenciosa.

### REF-0600 — MathLog10

[REF, MathLog10, p.PDF 1957–1960] · full_section. Logaritmo decimal; negativos NaN, zero não finito. Título impresso extraído MathLog em p1957 é incompatível com assinatura MathLog10.

### REF-0601 — MathMax

[REF, MathMax, p.PDF 1961–1962] · full_section. Máximo de dois; aceita inteiros sem cast e promove tipos diferentes ao maior. Não substitui validação de NaN nem limite máximo de lote.

### REF-0602 — MathMin

[REF, MathMin, p.PDF 1963–1964] · full_section. Mínimo de dois com preservação/promoção de tipos inteiros. Exemplo limita barras pela disponibilidade, mas disponibilidade muda assincronamente.

### REF-0603 — MathMod

[REF, MathMod, p.PDF 1965–1965] · full_section. Resto real com sinal do dividendo e módulo menor que divisor; proposta: rejeitar divisor zero e não confundir com módulo matemático sempre positivo.

### REF-0604 — MathPow

[REF, MathPow, p.PDF 1966–1969] · full_section. Base elevada a expoente; proposta: validar base/domínio e finitude no resultado. Exemplo gráfico não define fórmula normativa de risco.

### REF-0605 — MathRand

[REF, MathRand, p.PDF 1970–1970] · full_section. Inteiro pseudoaleatório 0..32767; requer inicialização. Proposta apenas em experimentos reproduzíveis, sem uso de geração de sinal confirmado.

### REF-0606 — MathRound

[REF, MathRound, p.PDF 1971–1972] · full_section. Inteiro mais próximo representado como double; exemplo 0.5=>1. Não prova normalização ao SYMBOL_VOLUME_STEP ou tick size.

### REF-0607 — MathSin

[REF, MathSin, p.PDF 1973–1975] · full_section. Seno com argumento em radianos e resultado [-1,1]; sem uso atual específico confirmado, possível estudo matemático.

### REF-0608 — MathSqrt

[REF, MathSqrt, p.PDF 1976–1979] · full_section. Raiz quadrada; negativo retorna NaN. Finitude deve ser checada além de domínio; sem adoção específica inferida.

### REF-0609 — MathSrand

[REF, MathSrand, p.PDF 1980–1982] · full_section. Mesma seed reproduz sequência; inicializar uma vez OnInit, não por tick. GetTickCount tem wrap em ~49 dias; TimeCurrent pode estagnar no fim de semana. Seed fixa proposta para laboratório.

### REF-0610 — MathTan

[REF, MathTan, p.PDF 1983–1985] · full_section. Tangente de ângulo em radianos; texto extraído 263 pode ter perdido sobrescrito 2^63, não usar literal263 como limite comprovado. Sem uso atual confirmado.

### REF-0611 — MathIsValidNumber

[REF, MathIsValidNumber, p.PDF 1986–1986] · full_section. Rejeita NaN e +/-INF; observado em JPW_SignalCopy_Core.mqh:54–55 e JPW_Alavancagem_StopRisk_Core.mqh:69–71. É condição necessária, não prova de valor positivo, disponível ou da unidade certa.

### REF-0612 — MathExpm1

[REF, MathExpm1, p.PDF 1987–1989] · full_section. exp(x)-1 mais preciso perto de zero; prosa underflow0 merece confronto com limite matemático -1, sem ensaio nativo. Proposta futura de estabilidade numérica.

### REF-0613 — MathLog1p

[REF, MathLog1p, p.PDF 1990–1993] · full_section. log(1+x) mais preciso perto de zero; x<-1 NaN, x=-1 não finito. Proposta futura de retornos logarítmicos com domínio explícito.

### REF-0614 — MathArccosh

[REF, MathArccosh, p.PDF 1994–1996] · full_section. Inversa hiperbólica cosh, domínio x>=1 e NaN abaixo. Sem uso atual confirmado.

### REF-0615 — MathArcsinh

[REF, MathArcsinh, p.PDF 1997–1999] · full_section. Inversa hiperbólica sinh para reais. Sem uso atual confirmado; exemplos de grade não comprovam extremos descritos nos comentários.

### REF-0616 — MathArctanh

[REF, MathArctanh, p.PDF 2000–2002] · full_section. Domínio aberto (-1,1); exemplo inicia -1 e continua além de1, portanto não serve como amostra apenas válida. Sem uso atual confirmado.

### REF-0617 — MathCosh

[REF, MathCosh, p.PDF 2003–2005] · full_section. Cosseno hiperbólico >=1; resultado pode exigir guarda de finitude. Sem uso atual confirmado.

### REF-0618 — MathSinh

[REF, MathSinh, p.PDF 2006–2008] · full_section. Seno hiperbólico; sem uso atual confirmado, proposta de estudo numérico.

### REF-0619 — MathTanh

[REF, MathTanh, p.PDF 2009–2011] · full_section. Tangente hiperbólica em [-1,1]; sem uso atual confirmado, eventual transformação futura não autoriza ML no produto.

### REF-0620 — MathSwap

[REF, MathSwap, p.PDF 2012–2014] · full_section. Inverte bytes de ushort,uint,ulong para representação binária/protocolo; não troca dígitos. Conversor binário do exemplo precisa caso zero; sem uso atual confirmado.

### REF-0621 — String Functions

[REF, String Functions, p.PDF 2015–2043] · full_section. Índice descritivo seguido por19APIs; separar capacidade,comprimento,mutação por referência e códigos de erro. Propostas de parsing/log, sem inventar adoção porAPI.

### REF-0622 — StringAdd

[REF, StringAdd, p.PDF 2016–2017] · full_section. Concatena por referência, bool de sucesso; GetLastError se falso. Proposta: montagem de mensagens com falha explícita; benchmark comparativo impresso não mede Stoikus.

### REF-0623 — StringBufferLen

[REF, StringBufferLen, p.PDF 2018–2018] · full_section. Capacidade alocada difere de comprimento; 0 para constante e -1 para string terminal, modificação pode ser indeterminada. Sem uso específico confirmado.

### REF-0624 — StringCompare

[REF, StringCompare, p.PDF 2019–2020] · full_section. Retorna -1/0/1, modo sensível default e ordenação por codepage; normalização textual não é identidade financeira. Sem uso específico confirmado.

### REF-0625 — StringConcatenate

[REF, StringConcatenate, p.PDF 2021–2022] · full_section. Forma string e retorna comprimento, converte simples como Print/Comment. Contagem 2..64 na abertura versus 2..63 argumentN exige distinguir argumento de saída.

### REF-0626 — StringFill

[REF, StringFill, p.PDF 2023–2023] · full_section. Preenche in-place, bool; preencher zero esvazia comprimento mantendo buffer. Proposta somente apresentação/buffer.

### REF-0627 — StringFind

[REF, StringFind, p.PDF 2024–2026] · full_section. Retorna posição inicial ou -1 ausente; moeda encontrada no nome não prova moeda-base nem moeda de lucro. Proposta preferir propriedades de símbolo.

### REF-0628 — StringGetCharacter

[REF, StringGetCharacter, p.PDF 2027–2028] · full_section. ushort do caractere em 0..len-1; 0 em erro, consultar erro. Não é índice de byte UTF-8.

### REF-0629 — StringInit

[REF, StringInit, p.PDF 2029–2029] · full_section. new_len0 desinicializa; positivo com caractere0 aloca buffer zerado mas comprimento lógico0. Sem uso específico confirmado.

### REF-0630 — StringLen

[REF, StringLen, p.PDF 2030–2030] · full_section. Comprimento sem zero final, diferente de capacidade. Proposta validar entrada textual antes de indexar.

### REF-0631 — StringSetLength

[REF, StringSetLength, p.PDF 2031–2031] · full_section. Muda comprimento em caracteres sem mudar buffer; encurtar descarta sufixo. Prosa chama parâmetro new_capacity, assinatura new_length.

### REF-0632 — StringReplace

[REF, StringReplace, p.PDF 2032–2032] · full_section. Número de substituições, zero sem ocorrência e -1 erro; entradas vazias/memória podem falhar. Proposta evitar tratar zero como erro.

### REF-0633 — StringReserve

[REF, StringReserve, p.PDF 2033–2034] · full_section. Reserva capacidade sem mudar conteúdo; dimensão menor que comprimento não reduz buffer. Exemplo mede microssegundos mas imprime msc; números não são benchmark atual.

### REF-0634 — StringSetCharacter

[REF, StringSetCharacter, p.PDF 2035–2036] · full_section. bool e string& mutável apesar de prosa dizer cópia; pos==len acrescenta, código0 corta sem reduzir capacidade.

### REF-0635 — StringSplit

[REF, StringSplit, p.PDF 2037–2038] · full_section. Separador único ushort; retorna0 entrada vazia,1 sem separador,-1 erro. Parâmetro proseado pos diverge separator. Proposta parser com campos e contagem validados.

### REF-0636 — StringSubstr

[REF, StringSubstr, p.PDF 2039–2039] · full_section. Copia trecho; length=-1 até fim, vazio se impossível. Exemplo moeda por posições0/3 assume símbolo de6 caracteres, inadequado como regra geral de corretora.

### REF-0637 — StringToLower

[REF, StringToLower, p.PDF 2040–2040] · full_section. Transforma por referência, bool; uso futuro em busca não deve alterar identificador canônico.

### REF-0638 — StringToUpper

[REF, StringToUpper, p.PDF 2041–2041] · full_section. Transforma por referência, bool; texto normalizado não substitui nomes exatos de símbolos.

### REF-0639 — StringTrimLeft

[REF, StringTrimLeft, p.PDF 2042–2042] · full_section. Remove espaços,tabs,quebras à esquerda in-place; retorna quantidade removida.

### REF-0640 — StringTrimRight

[REF, StringTrimRight, p.PDF 2043–2043] · full_section. Remove espaços,tabs,quebras à direita in-place; retorna quantidade removida.

### REF-0641 — Date and Time

[REF, Date and Time, p.PDF 2044–2057] · full_section. datetime segundosdesde1970; relógios servidor recebido/estimado/local/GMT têm causas diferentes. Duração deve usar contador monotônico, fuso de calendário exige conversão explícita.

### REF-0642 — TimeCurrent

[REF, TimeCurrent, p.PDF 2045–2046] · full_section. Hora servidor da última cotação; OnTick refere tick tratado, outros handlers última cotação de qualquer símbolo MarketWatch. Não relógio contínuo nem monotônico; tester simulado.

### REF-0643 — TimeTradeServer

[REF, TimeTradeServer, p.PDF 2047–2048] · full_section. Hora servidor estimada pelo terminal, depende relógio PC. Tester sempre TimeCurrent; não é evidência de horário recebido do servidor a cada chamada.

### REF-0644 — TimeLocal

[REF, TimeLocal, p.PDF 2049–2050] · full_section. Relógio local PC; tester igual TimeCurrent. Proposta: separar timestamp humano de duração monotônica.

### REF-0645 — TimeGMT

[REF, TimeGMT, p.PDF 2051–2052] · full_section. GMT calculado a partir PC e DST; tester igual TimeTradeServer. Não deduzir fuso servidor por teste histórico.

### REF-0646 — TimeDaylightSavings

[REF, TimeDaylightSavings, p.PDF 2053–2053] · full_section. Correção DST local em segundos, padrão0 e exemplo verão-3600; depende configuraçõesPC, não calendário de mercado.

### REF-0647 — TimeGMTOffset

[REF, TimeGMTOffset, p.PDF 2054–2054] · full_section. Diferença em segundos GMT-Local, não inverso; exemplo -25200 para local GMT+7. Proposta explicitar sinal no transporte.

### REF-0648 — TimeToStruct

[REF, TimeToStruct, p.PDF 2055–2055] · full_section. Converte segundos desde1970 em MqlDateTime, bool; erro consultável. Proposta validar resultado antes de usar campos.

### REF-0649 — StructToTime

[REF, StructToTime, p.PDF 2056–2057] · full_section. Converte campos em segundos e normaliza datas:2024.02.31=>2024.03.02 no exemplo. Não é validação estrita de input; fazer roundtrip se necessário.

### REF-0650 — Account Information

[REF, Account Information, p.PDF 2058–2062] · full_section. Três famílias tipadas; identidade,moeda,flags e métricas não são intercambiáveis. Valores de conta não definem regra normativa ou autorização de negociação.

### REF-0651 — AccountInfoDouble

[REF, AccountInfoDouble, p.PDF 2059–2059] · full_section. Lê propriedade enum double de conta:balance/equity/profit/margin. Valores de dinheiro/percentuais têm semânticas diferentes; proposta não intercambiá-los.

### REF-0652 — AccountInfoInteger

[REF, AccountInfoInteger, p.PDF 2060–2061] · full_section. Retorno long para propriedades bool/int/long; conta permitir trade e EA permitido são flags distintas. Permissão plataforma não autoriza armar Supervisor.

### REF-0653 — AccountInfoString

[REF, AccountInfoString, p.PDF 2062–2062] · full_section. Propriedades string como moeda depósito,broker,servidor; proposta registrar identidade e moeda junto às métricas, sem inferir da cotação.

### REF-0654 — Checkup

[REF, Checkup, p.PDF 2063–2076] · full_section. Estado do programa/terminal e diagnóstico deerro; getters não provam que candidato compilou/executou. Tipo de programa altera Symbol/Period.

### REF-0655 — GetLastError

[REF, GetLastError, p.PDF 2064–2064] · full_section. Consulta _LastError sem zerar. ResetLastError antes da operação e leitura logo após falha evita atribuir erro antigo à chamada atual.

### REF-0656 — IsStopped

[REF, IsStopped, p.PDF 2065–2065] · full_section. Flag de parada deve encerrar prontamente; encerramento externo após3s se ignorado. Loops de estudo precisam cooperar, não bloquear monitor.

### REF-0657 — UninitializeReason

[REF, UninitializeReason, p.PDF 2066–2067] · full_section. Lê motivo formado antes de OnDeinit; guardar contexto do encerramento. Recompilação/troca de conta/input são causas distintas.

### REF-0658 — TerminalInfoInteger

[REF, TerminalInfoInteger, p.PDF 2068–2068] · full_section. int de ambiente terminal; exemplo build/x64. Build impresso4330 é exemplo histórico, não versão instalada comprovada.

### REF-0659 — TerminalInfoDouble

[REF, TerminalInfoDouble, p.PDF 2069–2069] · full_section. double de ambiente; exemplo p2069 usa TerminalInfoInteger build/x64 e não demonstra API titular. Sem medição nativa.

### REF-0660 — TerminalInfoString

[REF, TerminalInfoString, p.PDF 2070–2070] · full_section. Strings ambiente incluindo instalação,dados,common; exemplos Windows não são caminhos observados neste Mac.

### REF-0661 — MQLInfoInteger

[REF, MQLInfoInteger, p.PDF 2071–2071] · full_section. Propriedade programa em int; exemplo memória em MB. Limites impressos não medem candidato atual.

### REF-0662 — MQLInfoString

[REF, MQLInfoString, p.PDF 2072–2072] · full_section. Nome/caminho do programa executado; arquivo-fonte presente não comprova esse caminho EX5 nem execução.

### REF-0663 — Symbol

[REF, Symbol, p.PDF 2073–2073] · full_section. Símbolo do gráfico/_Symbol; serviços retornam vazio. Proposta aceitar símbolo explícito em componentes multissímbolo.

### REF-0664 — Period

[REF, Period, p.PDF 2074–2074] · full_section. ENUM_TIMEFRAMES do gráfico/_Period, serviços0; H4=16388 no exemplo, não240 minutos. Usar PeriodSeconds para duração.

### REF-0665 — Digits

[REF, Digits, p.PDF 2075–2075] · full_section. Casas decimais da cotação do gráfico; não confundir precisão de exibição com tick negociável.

### REF-0666 — Point

[REF, Point, p.PDF 2076–2076] · full_section. Tamanho de point em moeda cotada; não é pip universal, tickvalue monetário nem risco da conta.

### REF-0667 — Event Handling

[REF, Event Handling, p.PDF 2077–2137] · full_section. Eventos porassinatura exata e fila limitada serial; coalescênciaTick/Timer versusBook enfileirado eTransaction1024. Não contarcallbacks para contarmercado, nem requisições para contardeals.

### REF-0668 — OnStart

[REF, OnStart, p.PDF 2079–2081] · full_section. Scripts/serviços recebem somente Start; int recomendado retorna código no Diário. Não transplantar loop de script a handlerEA.

### REF-0669 — OnInit

[REF, OnInit, p.PDF 2082–2084] · full_section. int recomendado;0 sucesso, falha descarregaEA mas indicador fica inoperante. INIT_PARAMETERS_INCORRECT afeta busca genética, INIT_AGENT_NOT_SUITABLE exclui agente. Monitor:200–214 valida timer e retorna código.

### REF-0670 — OnDeinit

[REF, OnDeinit, p.PDF 2085–2087] · full_section. void(const int reason), razões0..9; Monitor:216 mata timer e desanexa. Troca de conta não equivale a parada normal.

### REF-0671 — OnTick

[REF, OnTick, p.PDF 2088–2093] · full_section. ApenasEA/símbolo gráfico; novos ticks coalescem, AutoTradingoff não interrompe monitoramento. ATR sample usa barra1 e ATR2, mas Copy!=-1 não exige1 e OrderSendbool não prova execução. Monitor atual opera Timer/Transaction, não precisa Tick.

### REF-0672 — OnCalculate

[REF, OnCalculate, p.PDF 2094–2097] · full_section. Duas assinaturas mutuamente exclusivas; prev_calculated recebe retorno anterior e zera se histórico muda. Explicitamente fixar direção; begin indica dados significativos. Exemplo Momentum não protege denominador zero.

### REF-0673 — OnTimer

[REF, OnTimer, p.PDF 2098–2100] · full_section. Um timer por programa; criarInit/removerDeinit, eventos coalescem, limite real10–16ms. Monitor:207/216/226 usa1s e GetTickCount64, não contar callbacks como relógio. Exemplo estimador+1 deriva sob perda.

### REF-0674 — OnTrade

[REF, OnTrade, p.PDF 2101–2105] · full_section. Alterações de ordens,posições,deals,histórico; HistorySelect antes de consultar histórico. Uma requisição pode produzir vários eventos, chamada após transações correspondentes.

### REF-0675 — OnTradeTransaction

[REF, OnTradeTransaction, p.PDF 2106–2111] · full_section. request/result válidos só TRADE_TRANSACTION_REQUEST; ordem de chegada não garantida, estado muda durante handler, fila1024 sujeita supersessão. Monitor:217–224 apenas sinaliza Runtime/Accountant; reconciliação pesada posterior, causalidade preservada sem 1:1.

### REF-0676 — OnBookEvent

[REF, OnBookEvent, p.PDF 2112–2114] · full_section. Broadcast no gráfico; filtrar símbolo recebido e manter pares de Add/Release próprios. Eventos sempre enfileirados mesmo handler ativo; não extrapolar coalescênciaTick. Sem adoção atual confirmada.

### REF-0677 — OnChartEvent

[REF, OnChartEvent, p.PDF 2115–2121] · full_section. id determina lparam/dparam/sparam; renderGUI pode vir depois do handler e propriedade visível atrasar. Offsets0..65535 incluem65536 valores apesar de prosa65535; exemplo id>custom omiteoffset0. UsoUI futuro específico não confirmado.

### REF-0678 — OnTester

[REF, OnTester, p.PDF 2122–2128] · full_section. double custommax ordenado decrescente na genética; critério de regressão lucro/erro não é prova de segurança, lucro do sample ignora comissões/swap. Sem otimização executada nem regraJPW derivada.

### REF-0679 — OnTesterInit

[REF, OnTesterInit, p.PDF 2129–2135] · full_section. Contexto gráfico separado para otimização, recebeTester eventos em vez deInit/Tick; int0 permite iniciar, nãozero cancela, tempo limitado. Não é inicialização produtiva comprovada.

### REF-0680 — OnTesterDeinit

[REF, OnTesterDeinit, p.PDF 2136–2136] · full_section. Finaliza otimização; drenar FrameNext para quadros atrasados, pois frames podem chegar agrupados.

### REF-0681 — OnTesterPass

[REF, OnTesterPass, p.PDF 2137–2137] · full_section. Processa chegada de frame enviado viaFrameAdd/OnTester; não assumir todos chegam antes deDeinit. Sem teste nativo.

### REF-0682 — Market Info

[REF, Market Info, p.PDF 2138–2164] · full_section. Existência,seleção,sincronização,últimotick,sessões eDOM são camadas distintas. Consulta de snapshotnão prova disponibilidadedehistória oupermissãoprodutiva.

### REF-0683 — SymbolsTotal

[REF, SymbolsTotal, p.PDF 2139–2139] · full_section. Contagem selected=true MarketWatch versusfalse catálogo total; índices devem usar mesmo universo. Sem catálogo atual consultado.

### REF-0684 — SymbolExist

[REF, SymbolExist, p.PDF 2140–2141] · full_section. bool existência em standard/custom; is_custom só definido em sucesso. Não comprova seleção,sincronização ou negociação permitida.

### REF-0685 — SymbolName

[REF, SymbolName, p.PDF 2142–2143] · full_section. Nome por posição e universo selected; proposta guardar nome canônico, não posição transitória.

### REF-0686 — SymbolSelect

[REF, SymbolSelect, p.PDF 2144–2145] · full_section. Muda MarketWatch bool; remoção vedada com gráfico aberto/posição. Proposta carregamento explícito, sem execução dessas mutações nesta pesquisa.

### REF-0687 — SymbolIsSynchronized

[REF, SymbolIsSynchronized, p.PDF 2146–2146] · full_section. Flag sincronização símbolo-servidor; não substitui prontidão da série/indicador específica.

### REF-0688 — SymbolInfoDouble

[REF, SymbolInfoDouble, p.PDF 2147–2148] · full_section. Valor direto ou bool+out; erros5040/4301/4302/4303. Antes da primeira cotação preço pode ser indeterminado; preferir SymbolInfoTick para snapshot.

### REF-0689 — SymbolInfoInteger

[REF, SymbolInfoInteger, p.PDF 2149–2150] · full_section. long direto ou bool+out; enum deve corresponder tipo, mesmas falhas de símbolo/seleção/propriedade. Spread inteiro em points, não dinheiro.

### REF-0690 — SymbolInfoString

[REF, SymbolInfoString, p.PDF 2151–2152] · full_section. Direto ou bool+out; moedas base,lucro,margem devem vir de metadados, não StringSubstr do nome. Preferir confirmação bool quando vazio ambíguo.

### REF-0691 — SymbolInfoMarginRate

[REF, SymbolInfoMarginRate, p.PDF 2153–2154] · full_section. Coeficientes initial/maintenance por tipo/direção; multiplicam margem de1lote, não valor monetário isolado. initial marcado[in] apesar de variável de recepção.

### REF-0692 — SymbolInfoTick

[REF, SymbolInfoTick, p.PDF 2155–2155] · full_section. bool preenche MqlTick com preços e tempo último update num único snapshot; time segundos/time_msc milissegundos, flags descrevem mudança, não preenchimento atual.

### REF-0693 — SymbolInfoSessionQuote

[REF, SymbolInfoSessionQuote, p.PDF 2156–2157] · full_section. Sessão de cotação por dia e índice0; from/to segundos desde00h, data ignorada. Cotação não implica janela de negociação nem programa diárioJPW.

### REF-0694 — SymbolInfoSessionTrade

[REF, SymbolInfoSessionTrade, p.PDF 2158–2159] · full_section. Sessão de negociação por dia/índice0, distinta deQuote; tratar virada de meia-noite e múltiplas sessões. Calendário semanal não prova exceções feriados.

### REF-0695 — MarketBookAdd

[REF, MarketBookAdd, p.PDF 2160–2161] · full_section. Abre/subscreveDOM, bool; parear só sucessos próprios comRelease. Nota assinatura semconst diverge seçãoOnBookEvent; seguir assinatura formal do handler. Sem adoção atual confirmada.

### REF-0696 — MarketBookRelease

[REF, MarketBookRelease, p.PDF 2162–2163] · full_section. Cancela subscrição própria emDeinit/destrutor; boolfalha requer registro, evitar decrementar contador de terceiros.

### REF-0697 — MarketBookGet

[REF, MarketBookGet, p.PDF 2164–2164] · full_section. bool e arrayMqlBookInfo, requerAdd, terminal aloca dinâmico. [in] do array é incongruente com saída; snapshot atual não histórico de todas as mudanças.

### REF-0698 — Economic Calendar

[REF, Economic Calendar, p.PDF 2165–2195] · full_section. Metadados,event_id,value_id,change_iddistintos; hora servidor, sentinelLONG_MIN e escala1e6. Uso futuroproposto semadoçãoobservada; revisão posterior não é informação disponível na decisão histórica.

### REF-0699 — CalendarCountryById

[REF, CalendarCountryById, p.PDF 2166–2167] · full_section. bool descrição por ID, erros4001/5402/5401; exemploEU999/Worldwide0 são entidades do calendário, não garantir que cada ID seja país ISO puro. Proposta futura.

### REF-0700 — CalendarEventById

[REF, CalendarEventById, p.PDF 2168–2170] · full_section. bool metadados:unit,digits,multiplier,importance,frequency,time_mode efonte; descrição5402 country not found parece herdada. Metadado não previsão causal de preço. Proposta futura.

### REF-0701 — CalendarValueById

[REF, CalendarValueById, p.PDF 2171–2173] · full_section. bool valor por value_id distinto event_id; LONG_MIN significa ausente e deve ser testado antes de dividir por1e6. Separar revisão,período ehorapublicação. Proposta futura.

### REF-0702 — CalendarCountries

[REF, CalendarCountries, p.PDF 2174–2175] · full_section. Número de descrições, falhas/5400 capacidade; retorna entidadesWW/EU também. Lista impressa histórica não disponibilidade consultada. Proposta futura.

### REF-0703 — CalendarEventByCountry

[REF, CalendarEventByCountry, p.PDF 2176–2177] · full_section. Countrycodealpha2 earraymetadados; não são valores publicados. IDs e ordenação do exemplo não constantes de negócio. Proposta futura.

### REF-0704 — CalendarEventByCurrency

[REF, CalendarEventByCurrency, p.PDF 2178–2179] · full_section. Eventos por moeda;EUR pode abranger países. Número retornado e errosmemória/timeout devem ser diferenciados de nenhum evento. Proposta futura.

### REF-0705 — CalendarValueHistoryByEvent

[REF, CalendarValueHistoryByEvent, p.PDF 2180–2182] · full_section. Contagem ou-1; intervalo servidor, to0 inclui eventos futuros; LONG_MIN/1e6. Sample testa intcomo bool (-1verdadeiro), acessaevents[6] e reduzarrays sem garantias; não copiar. Proposta futura com versões disponíveis no instante.

### REF-0706 — CalendarValueHistory

[REF, CalendarValueHistory, p.PDF 2183–2185] · full_section. Contagem ou-1; filtrospaís e moeda emAND,NULL/vazio semfiltro; to0incluifuturos,5400parcial. Dados revisados atuais não backtest point-in-time. Proposta futura.

### REF-0707 — CalendarValueLastByEvent

[REF, CalendarValueLastByEvent, p.PDF 2186–2190] · full_section. change_idin/out;0 inicial retorna0 e atualizacursor, não histórico. Persistir cursor só com lote íntegro e filtro consistente; sample buscaNonfarm por substringe não garanteevento correto. Proposta futura.

### REF-0708 — CalendarValueLast

[REF, CalendarValueLast, p.PDF 2191–2195] · full_section. Cursor incremental com filtrosAND;0baseline não novidade; LONG_MIN antes1e6 e fuso servidor. Sample usaerroantigosemReset, precisa distinguir0normal/timeouterro. Proposta futura.

### REF-0709 — Timeseries and Indicators Access

[REF, Timeseries and Indicators Access, p.PDF 2196–2289] · partial_parent. Continua além2289 (até2297): aqui introduçãoeREF0710..0739. Barra0inacabada; físicaoldestfirst versusdireçãológica; prontidãoéassíncrona. Handle,contagem,sentinel,finitude,einstantedeconclusãosãoguardasdiferentes.

### REF-0710 — Indexing Direction in Arrays, Buffers and Timeseries

[REF, Indexing Direction in Arrays, Buffers and Timeseries, p.PDF 2201–2203] · full_section. AS_SERIES muda acesso lógico, não memória; estáticos não revertem. Buffers geridos terminal; ArrayIsSeries não é ArrayGetAsSeries. Barra0 incompleta, não fechar dado por rótulo temporal.

### REF-0711 — Organizing Data Access

[REF, Organizing Data Access, p.PDF 2204–2212] · full_section. Servidor entregaM1/HCC porano; HC por timeframe sobdemanda, Maxbars não garante prontidão nemquantidadeexata, reinício após alterar. EAs/indicadores devem retornar e tentar em evento posterior; scriptloader não modelo do monitor. Texto antigo2GB32bit não limite universal atual.

### REF-0712 — SeriesInfoInteger

[REF, SeriesInfoInteger, p.PDF 2213–2214] · full_section. long direto ou bool+out por símbolo/período/enum; SERIES_SYNCHRONIZED e FIRSTDATE são estados distintos. Observado Observer_Runtime:489–500 antes de ATRhistórico, requer contagem e cópia exata adicionais.

### REF-0713 — Bars

[REF, Bars, p.PDF 2215–2217] · full_section. Conta barras prontas;0 pode ser série nãoformada/sincronizada, não ausência econômica. Intervalo seleciona abertura; exemploW1 semabertura=>0. Código p2216 imprimebarsantigo após sincronizar semrecálculo.

### REF-0714 — BarsCalculated

[REF, BarsCalculated, p.PDF 2218–2219] · full_section. Contagem calculada do handle ou-1. Handle válido não garante dados; Observer_Runtime:496 exige shift+56, RaizN_Live:117/138 exige56. Script dorme50ms mas não modelo handler produtivo.

### REF-0715 — IndicatorCreate

[REF, IndicatorCreate, p.PDF 2220–2221] · full_section. Handle viaMqlParam tipados até64; INVALID_HANDLE falha, IND_CUSTOM primeiroTYPE_STRINGcaminhoEX5; tester_indicator necessário para nome dinâmico/IndicatorCreate. Sem criação atual por essaAPIconfirmada.

### REF-0716 — IndicatorParameters

[REF, IndicatorParameters, p.PDF 2222–2223] · full_section. Intnúmero de inputs e arrays tipos/valores porhandle,-1erro. Proposta diagnóstico reproduzível sem concluir que indicador está pronto apenas pelos parâmetros.

### REF-0717 — IndicatorRelease

[REF, IndicatorRelease, p.PDF 2224–2225] · full_section. Removehandle imediatamente, blococálculo depois se semusuários; não executada no tester. Observado Observer_Runtime:508 após leitura; teste histórico não prova memória liberada real.

### REF-0718 — CopyBuffer

[REF, CopyBuffer, p.PDF 2226–2230] · full_section. Countcopiado ou-1; posição0 atual,memória oldestfirst independenteAS_SERIES; prontidãoassíncrona/timeout pode parcial. Observer_Runtime:499 eRaizN_Live:128 exigem==1; EMPTY_VALUE pode ser finito, requer guarda separada.

### REF-0719 — CopyRates

[REF, CopyRates, p.PDF 2231–2234] · full_section. MqlRates sincroniza campos da barra;3formas posição+count,data+count,intervalo; retornocount/-1; datacount selecionaabertura<=data, intervaloaberturasdentro. Proposta não aceitar cópia parcial como completude.

### REF-0720 — CopySeries

[REF, CopySeries, p.PDF 2235–2238] · full_section. Campos selecionados sincronizados na mesma chamada; arrays ordemMqlRates(time,open,high,low,close,tick_volume,spread,real_volume), ordemmaskirrelevante. Conversãofloat pode perderprecisão. Sem uso atual confirmado.

### REF-0721 — CopyTime

[REF, CopyTime, p.PDF 2239–2241] · full_section. datetime aberturas emsegundos;3formas,oldestfirstmemória,0fonteatual; prontidão/máxbarras/partial. Observer_Runtime:491/497/500 revalida abertura antes/depoisCopyBuffer contra virada causal.

### REF-0722 — CopyOpen

[REF, CopyOpen, p.PDF 2242–2244] · full_section. doubleabertura;3formas de cópia e count/-1, oldestfirstmemória. Abertura atual pode existir com fechamento em formação; timestamp não transforma OHLC0 em final.

### REF-0723 — CopyHigh

[REF, CopyHigh, p.PDF 2245–2248] · full_section. doublemáxima; cópia barra0 mutável. Sample copia todohistórico por tick para índice segundo, não modelo eficiente; validar index>=0 e count suficiente.

### REF-0724 — CopyLow

[REF, CopyLow, p.PDF 2249–2251] · full_section. doublemínima; mesma cópiaassíncrona/intervaloabertura,0atualmutável. Proposta coorte temporal consistente comHigh, não chamadas separadas sem checagem.

### REF-0725 — CopyClose

[REF, CopyClose, p.PDF 2252–2254] · full_section. doublefechamento; barra0 é último preço ainda mutável, não fechamento definitivo. Se regra requerconcluída,shift1 e prova de abertura são necessários.

### REF-0726 — CopyTickVolume

[REF, CopyTickVolume, p.PDF 2255–2258] · full_section. longcontagemticks, não volume negociado; copycount/-1. Sample p2258 usa prices semguardarerro e lê timeseries[0] sem==1; não reproduzir. Sem uso atual específico confirmado.

### REF-0727 — CopyRealVolume

[REF, CopyRealVolume, p.PDF 2259–2261] · full_section. longvolume de trades, semanticamente distinto tickvolume; disponibilidade depende mercado/feed,0não prova dado real disponível. Mesmas3formas/partial.

### REF-0728 — CopySpread

[REF, CopySpread, p.PDF 2262–2265] · full_section. intspreadhistórico empoints; barra0 mutável, não moeda da conta. Sample atual calcula(Ask-Bid)/Point sem snapshot conjunto nem guardaPoint0. Proposta snapshot e unidade explícita.

### REF-0729 — CopyTicks

[REF, CopyTicks, p.PDF 2266–2271] · full_section. Ticks emordemcronológica, índice0maisantigo; frommilissegundosdesde1970,count0defaultrecentesaté2000. INFO/TRADE flagsselecionammudanças, demais camposcarregamúltimovalor. EA podeesperar45s e retornarparcial; OnTick não cada tick. Proposta futura paginada por cursor com desempate.

### REF-0730 — CopyTicksRange

[REF, CopyTicksRange, p.PDF 2272–2273] · full_section. Intervalomilissegundos inclusivofrom<=time<=to;0defaultscomeço/fimhistória. Bufferpequeno4407/timeouts podem retornarparcial; memória insuficiente. Proposta dividir[diainício,próximoinício-1ms] para não duplicar limite.

### REF-0731 — iBars

[REF, iBars, p.PDF 2274–2274] · full_section. Contagem disponível limitadaMaxbars, não prova história integral servidor. Proposta metadata da cobertura antes de cálculo.

### REF-0732 — iBarShift

[REF, iBarShift, p.PDF 2275–2277] · full_section. Índicebar por tempo; exactfalse aceita bar mais próximo anterior se gap, exacttrue-1. Observado Observer_Runtime:486 seguido revalidação barfechado. Não identificar ausência com barra anterior silenciosamente.

### REF-0733 — iClose

[REF, iClose, p.PDF 2278–2279] · full_section. doubleclose por shift;0erro, requisita série cada chamada semcachelocal. Shift0incompleto; preferir snapshotcopiado para várioscampos.

### REF-0734 — iHigh

[REF, iHigh, p.PDF 2280–2281] · full_section. doublehigh por shift;0erro e requisição cada chamada, semcachelocal. High0 muda até fechamento.

### REF-0735 — iHighest

[REF, iHighest, p.PDF 2282–2282] · full_section. Retorna índice relativo àbarraatual, não preço; count20start4=>4..23, startnegativo vira0. Sample pesquisaMODE_CLOSE mas lêHigh[index], inconsistência semântica. Proposta consultar mesma série buscada.

### REF-0736 — iLow

[REF, iLow, p.PDF 2283–2284] · full_section. doublelow por shift,0erro e requisição semcachelocal; não preencher falha com0 legítimo nem usarshiftnegativo.

### REF-0737 — iLowest

[REF, iLowest, p.PDF 2285–2285] · full_section. Retornaíndice ou-1; count15start10=>10..24. Sample pesquisaMODE_REAL_VOLUME mas lêLow[index], não volume mínimo; não derivar regraJPW.

### REF-0738 — iOpen

[REF, iOpen, p.PDF 2286–2287] · full_section. doubleopen porshift;0erro,sérieacessada todachamada. Metadata de barra correta ainda necessária para regras de tempo.

### REF-0739 — iTime

[REF, iTime, p.PDF 2288–2289] · full_section. datetimeabertura porshift,0erro,semcachelocal. Sample2018domingo mapeiaparasextacomexactfalse; código deve verificar índice antes deiTime. Observado causalidadehistorical emRuntime.

## Integridade e rastreio

O JSON pareado contém a lista exata de342páginas, hash original de cada texto e recomputação igual, hash doPDF doíndice, hashes dos arquivosindex/pagesJSONL e hash de cada lote emitido. Isso comprova identidade do corpus lido, não fidelidade visual integral doPDF. REF-0709 continua no próximo lote a partir de2290; APIs posteriores àiTime não foram abrangidas aqui.
