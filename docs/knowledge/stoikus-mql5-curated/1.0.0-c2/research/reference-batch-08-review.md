# REF — revisão semântica do lote 08

Leitura real do texto integral extraído das páginas físicas PDF **2290–2611 (322 páginas)**, feita nesta sessão em 23 lotes de até 30.000 caracteres, sem truncamento dos retornos. A página 2289 foi lida adicionalmente para a fronteira de iBarShift; não se reivindica leitura das páginas anteriores. Todos os exemplos/documentação de código estão **MQL_NOT_RUN**. Não houve compilação MetaEditor, execução MT5/EX5, teste de corretora, piloto, ativação, edição de produto, kit ou Git.

Fonte: corpus-fast/REF/pages.jsonl e index.json; livro *MQL5 Language REFERENCE*, MetaQuotes, PDF de 7284 páginas, SHA-256 `9ae05ce748d23ce0de9b230fc6c7093a2af0adc3ce3544244a74e1c7d628d499`. O ledger JSON adjacente contém a lista exata lida, hashes textuais originais por página, hash de linha JSONL, filas de leitura e cobertura dos IDs. Hash de texto garante vínculo ao corpus, não fidelidade visual do PDF. A leitura semântica inclui código, comentários, retornos e exemplos impressos; não equivale a auditoria automática das imagens/layout. Linhas longas de exemplos já aparecem cortadas lateralmente na extração; não se inventou seu complemento. As anomalias abaixo são achados do texto extraído e precisam comparação visual/original e compilação para confirmação editorial definitiva.

A atribuição “atual” significa relevância conceitual à arquitetura informada no BRIEF: Monitor event-driven que não negocia, core1.23.0/MQL1.230/calc1.9.0. Este lote não examinou implementações do Stoikus para provar chamadas presentes. Recursos futuros permanecem propostas; nenhuma regra de API substitui regra financeira JPW.

## Fronteiras

- Continuação anterior, PDF2289: exemplo iBarShift procura domingo inexistente; exact=false encontra sexta (índice64), exact=true retorna-1. Helper DayOfWeek usa TimeToStruct. Não generalizar deslocamento64 a outros feeds/calendários.
- REF-0709 é capítulo-contêiner2196–2297: só seu trecho2290–2297 lido neste lote; não somar páginas dos filhos novamente.
- REF-0854 começa em2611 e termina2614: aqui foram lidos contrato/notas e início do exemplo em2611; continuação2612–2614 pertence ao próximo lote. REF-0840 é contêiner2560–2623 e está parcialmente coberto aqui.

## Contratos, aplicação e exigência de prova

### REF-0709 — Timeseries and Indicators Access · [REF, Timeseries and Indicators Access, p.PDF 2290–2297]

Contêiner de Timeseries and Indicators Access; cobertura local somente das quatro funções finais de consulta por barra.

Aplicação conceitual atual: consumo confiável de dados do Monitor; uso exato de cada API não foi auditado neste lote. Provar símbolo/período/shift, disponibilidade e erro; testar zero válido versus falha, primeira consulta e série não pronta. Não transformar volume de ticks em volume financeiro.

### REF-0740 — iTickVolume · [REF, iTickVolume, p.PDF 2290–2291]

iTickVolume retorna volume de ticks por shift; zero pode indicar erro; pede série em toda chamada, sem cache local. Exemplo usa iVolume, não a função titulada.

Aplicação conceitual atual: consumo confiável de dados do Monitor; uso exato de cada API não foi auditado neste lote. Provar símbolo/período/shift, disponibilidade e erro; testar zero válido versus falha, primeira consulta e série não pronta. Não transformar volume de ticks em volume financeiro.

### REF-0741 — iRealVolume · [REF, iRealVolume, p.PDF 2292–2293]

iRealVolume retorna volume real; disponibilidade depende da série, zero exige GetLastError; cada chamada solicita dados. Exemplo imprime iVolume, logo não demonstra volume real.

Aplicação conceitual atual: consumo confiável de dados do Monitor; uso exato de cada API não foi auditado neste lote. Provar símbolo/período/shift, disponibilidade e erro; testar zero válido versus falha, primeira consulta e série não pronta. Não transformar volume de ticks em volume financeiro.

### REF-0742 — iVolume · [REF, iVolume, p.PDF 2294–2295]

iVolume é volume de ticks, não financeiro nem real; NULL/0 usam símbolo/período corrente; consulta por shift regressivo sem cache.

Aplicação conceitual atual: consumo confiável de dados do Monitor; uso exato de cada API não foi auditado neste lote. Provar símbolo/período/shift, disponibilidade e erro; testar zero válido versus falha, primeira consulta e série não pronta. Não transformar volume de ticks em volume financeiro.

### REF-0743 — iSpread · [REF, iSpread, p.PDF 2296–2297]

iSpread retorna spread da barra por shift; zero exige distinguir erro; consulta individual pode preparar série e demorar. Exemplo reutilizado não demonstra spread.

Aplicação conceitual atual: consumo confiável de dados do Monitor; uso exato de cada API não foi auditado neste lote. Provar símbolo/período/shift, disponibilidade e erro; testar zero válido versus falha, primeira consulta e série não pronta. Não transformar volume de ticks em volume financeiro.

### REF-0744 — Custom Symbols · [REF, Custom Symbols, p.PDF 2298–2373]

Capítulo agrega criação e mutação local de símbolos; uma especificação customizada não prova equivalência ao instrumento negociado da corretora.

Proposta futura de fixtures isoladas/replay; sem uso produtivo atual comprovado ou autorização de mutação. Provar especificação, origem, ordenação, intervalos e hashes antes/depois; testar parcial, buracos e efeitos destrutivos em símbolo descartável. Resultado sintético não prova feed de corretora.

### REF-0745 — CustomSymbolCreate · [REF, CustomSymbolCreate, p.PDF 2299–2301]

Nome único global, máximo31 caracteres; grupos sob Custom, caminho127; origem inexistente cria vazio e registra4301. SYMBOL_PATH inclui nome final, deve ser recortado antes de reuso.

Proposta futura de fixtures isoladas/replay; sem uso produtivo atual comprovado ou autorização de mutação. Provar especificação, origem, ordenação, intervalos e hashes antes/depois; testar parcial, buracos e efeitos destrutivos em símbolo descartável. Resultado sintético não prova feed de corretora.

### REF-0746 — CustomSymbolDelete · [REF, CustomSymbolDelete, p.PDF 2302–2303]

Delete falha para símbolo no Market Watch ou com gráfico aberto. Parâmetro descritivo diz não coincidir com símbolo existente, inconsistência com a finalidade de excluir existente.

Proposta futura de fixtures isoladas/replay; sem uso produtivo atual comprovado ou autorização de mutação. Provar especificação, origem, ordenação, intervalos e hashes antes/depois; testar parcial, buracos e efeitos destrutivos em símbolo descartável. Resultado sintético não prova feed de corretora.

### REF-0747 — CustomSymbolSetInteger · [REF, CustomSymbolSetInteger, p.PDF 2304–2307]

SetInteger altera propriedades long; mudar CHART_MODE ou DIGITS apaga histórico minuto/tick e terminal tenta reconstruí-lo. Helpers de exemplo ocultam símbolo antes de exclusão.

Proposta futura de fixtures isoladas/replay; sem uso produtivo atual comprovado ou autorização de mutação. Provar especificação, origem, ordenação, intervalos e hashes antes/depois; testar parcial, buracos e efeitos destrutivos em símbolo descartável. Resultado sintético não prova feed de corretora.

### REF-0748 — CustomSymbolSetDouble · [REF, CustomSymbolSetDouble, p.PDF 2308–2311]

SetDouble altera propriedades reais; POINT, TRADE_TICK_SIZE, TRADE_TICK_VALUE podem eliminar histórico minuto/tick. Exemplo altera limites/passo de volume e consulta de volta.

Proposta futura de fixtures isoladas/replay; sem uso produtivo atual comprovado ou autorização de mutação. Provar especificação, origem, ordenação, intervalos e hashes antes/depois; testar parcial, buracos e efeitos destrutivos em símbolo descartável. Resultado sintético não prova feed de corretora.

### REF-0749 — CustomSymbolSetString · [REF, CustomSymbolSetString, p.PDF 2312–2315]

SetString altera strings; mudar SYMBOL_FORMULA elimina histórico e tenta recomputação. Exemplo 1/origem é demonstração de mutação, não regra financeira JPW.

Proposta futura de fixtures isoladas/replay; sem uso produtivo atual comprovado ou autorização de mutação. Provar especificação, origem, ordenação, intervalos e hashes antes/depois; testar parcial, buracos e efeitos destrutivos em símbolo descartável. Resultado sintético não prova feed de corretora.

### REF-0750 — CustomSymbolSetMarginRate · [REF, CustomSymbolSetMarginRate, p.PDF 2316–2320]

SetMarginRate define fatores inicial/manutenção por tipo/direção; produto com margem-base representa reserva, não orçamento de risco. Exemplo consulta Buy/Sell antes/depois.

Proposta futura de fixtures isoladas/replay; sem uso produtivo atual comprovado ou autorização de mutação. Provar especificação, origem, ordenação, intervalos e hashes antes/depois; testar parcial, buracos e efeitos destrutivos em símbolo descartável. Resultado sintético não prova feed de corretora.

### REF-0751 — CustomSymbolSetSessionQuote · [REF, CustomSymbolSetSessionQuote, p.PDF 2321–2325]

Sessões de cotação usam segundos desde00h ignorando data; índices consecutivos; from=to=0 remove sessão e renumera seguintes; índice sem anterior falha.

Proposta futura de fixtures isoladas/replay; sem uso produtivo atual comprovado ou autorização de mutação. Provar especificação, origem, ordenação, intervalos e hashes antes/depois; testar parcial, buracos e efeitos destrutivos em símbolo descartável. Resultado sintético não prova feed de corretora.

### REF-0752 — CustomSymbolSetSessionTrade · [REF, CustomSymbolSetSessionTrade, p.PDF 2326–2330]

Contrato de sessões de negociação repete índices contíguos e remoção por0/0. Exemplo extraído chama SetSessionQuote/SessionQuotePrint apesar do título Trade; não copiá-lo como prova.

Proposta futura de fixtures isoladas/replay; sem uso produtivo atual comprovado ou autorização de mutação. Provar especificação, origem, ordenação, intervalos e hashes antes/depois; testar parcial, buracos e efeitos destrutivos em símbolo descartável. Resultado sintético não prova feed de corretora.

### REF-0753 — CustomRatesDelete · [REF, CustomRatesDelete, p.PDF 2331–2335]

RatesDelete remove barras no intervalo datetime inclusivo descrito entre primeira/última; retorna quantidade ou-1. Exemplo copia M1, remove duas penúltimas e relê para conferir.

Proposta futura de fixtures isoladas/replay; sem uso produtivo atual comprovado ou autorização de mutação. Provar especificação, origem, ordenação, intervalos e hashes antes/depois; testar parcial, buracos e efeitos destrutivos em símbolo descartável. Resultado sintético não prova feed de corretora.

### REF-0754 — CustomRatesReplace · [REF, CustomRatesReplace, p.PDF 2336–2340]

RatesReplace substitui integralmente intervalo, ignora entradas fora dele e preserva exterior; requer OHLC correto e tempos M1. Exemplo chama CustomRatesUpdate, portanto não ilustra contrato Replace.

Proposta futura de fixtures isoladas/replay; sem uso produtivo atual comprovado ou autorização de mutação. Provar especificação, origem, ordenação, intervalos e hashes antes/depois; testar parcial, buracos e efeitos destrutivos em símbolo descartável. Resultado sintético não prova feed de corretora.

### REF-0755 — CustomRatesUpdate · [REF, CustomRatesUpdate, p.PDF 2341–2345]

RatesUpdate insere ausentes/substitui coincidentes, preserva outras barras; MqlRates M1/OHLC válidos. Exemplo inverte high/low separadamente sem trocar extremos: resultado exibido high<low, inconsistente.

Proposta futura de fixtures isoladas/replay; sem uso produtivo atual comprovado ou autorização de mutação. Provar especificação, origem, ordenação, intervalos e hashes antes/depois; testar parcial, buracos e efeitos destrutivos em símbolo descartável. Resultado sintético não prova feed de corretora.

### REF-0756 — CustomTicksAdd · [REF, CustomTicksAdd, p.PDF 2346–2353]

TicksAdd exige Market Watch e ordem não decrescente time_msc. >256ticks: parte inicial direto na base, últimos128 via Market Watch. Normaliza tempos, gera flags por campos positivos, não conserva BUY/SELL.

Proposta futura de fixtures isoladas/replay; sem uso produtivo atual comprovado ou autorização de mutação. Provar especificação, origem, ordenação, intervalos e hashes antes/depois; testar parcial, buracos e efeitos destrutivos em símbolo descartável. Resultado sintético não prova feed de corretora.

### REF-0757 — CustomTicksDelete · [REF, CustomTicksDelete, p.PDF 2354–2361]

TicksDelete usa milissegundos desde1970, retorna contagem/-1; limites temporais podem abranger vários ticks no mesmo instante, não identificar exatamente dez por índice.

Proposta futura de fixtures isoladas/replay; sem uso produtivo atual comprovado ou autorização de mutação. Provar especificação, origem, ordenação, intervalos e hashes antes/depois; testar parcial, buracos e efeitos destrutivos em símbolo descartável. Resultado sintético não prova feed de corretora.

### REF-0758 — CustomTicksReplace · [REF, CustomTicksReplace, p.PDF 2362–2370]

TicksReplace trabalha direto na base, não ordena; processa dia a dia, falha deixa dias anteriores trocados e dia defeituoso/seguintes intactos. Ausências no intervalo viram buracos/deleção.

Proposta futura de fixtures isoladas/replay; sem uso produtivo atual comprovado ou autorização de mutação. Provar especificação, origem, ordenação, intervalos e hashes antes/depois; testar parcial, buracos e efeitos destrutivos em símbolo descartável. Resultado sintético não prova feed de corretora.

### REF-0759 — CustomBookAdd · [REF, CustomBookAdd, p.PDF 2371–2373]

BookAdd exige DOM aberto/subscrito, troca estado integral, não muda Bid/Ask; ticks precisam envio separado. Ordena preços, limita profundidade, volume_real positivo prevalece; texto sobre negativos requer cuidado.

Proposta futura de fixtures isoladas/replay; sem uso produtivo atual comprovado ou autorização de mutação. Provar especificação, origem, ordenação, intervalos e hashes antes/depois; testar parcial, buracos e efeitos destrutivos em símbolo descartável. Resultado sintético não prova feed de corretora.

### REF-0760 — Chart Operations · [REF, Chart Operations, p.PDF 2374–2440]

Setters do gráfico entram em fila; retorno verdadeiro confirma enfileiramento, não aparência. Redraw força atualização; getters síncronos aguardam comandos anteriores.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0761 — ChartApplyTemplate · [REF, ChartApplyTemplate, p.PDF 2376–2378]

ApplyTemplate enfileira; template aplicado no gráfico do próprio EA descarrega-o. Permissão efetiva nunca ampliada; procura relativa MQL5/EX5/Templates; .tpl não é recurso EX5.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0762 — ChartSaveTemplate · [REF, ChartSaveTemplate, p.PDF 2379–2383]

SaveTemplate salva em data_folder/Profiles/Templates e sobrescreve mesmo nome, adiciona .tpl. Exemplo prepara Zigzag com BarsCalculated, CopyBuffer e tempos antes de canal/template, sem provar prontidão nativa aqui.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0763 — ChartWindowFind · [REF, ChartWindowFind, p.PDF 2384–2385]

WindowFind busca shortname, não arquivo; variante sem args só indicador, retorna-1 para EA/script. Shortname deve discriminar parâmetros para evitar ambiguidades.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0764 — ChartTimePriceToXY · [REF, ChartTimePriceToXY, p.PDF 2386–2387]

TimePriceToXY recebe subjanela/tempo/preço e devolve pixels da origem superior esquerda do gráfico principal; bool decide validade, exemplo exige uma barra copiada.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0765 — ChartXYToTimePrice · [REF, ChartXYToTimePrice, p.PDF 2388–2389]

XYToTimePrice devolve subjanela,datetime/preço por referência; exemplo click faz ida/volta e desenha cruz. Conversão de pixels não valida valor de mercado.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0766 — ChartOpen · [REF, ChartOpen, p.PDF 2390–2391]

ChartOpen retorna long ID ou0; máximo CHARTS_MAX; NULL/0 significam símbolo/período corrente. Exemplo registra ID, não autoriza abrir gráficos do proprietário.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0767 — ChartFirst · [REF, ChartFirst, p.PDF 2392–2392]

ChartFirst devolve primeiro ID, não índice de posição; exemplo consulta símbolo/período para identidade observável.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0768 — ChartNext · [REF, ChartNext, p.PDF 2393–2393]

ChartNext retorna-1 no fim; parâmetro0 significa primeiro gráfico, exceção à convenção de gráfico corrente. Percurso precisa limite e atualização do ID.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0769 — ChartClose · [REF, ChartClose, p.PDF 2394–2395]

ChartClose fecha ID,0 atual, bool confirma sucesso; exemplo abre gráfico temporário e fecha após espera.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0770 — ChartSymbol · [REF, ChartSymbol, p.PDF 2396–2396]

ChartSymbol retorna string vazia para gráfico inexistente; identidade do gráfico deve ser validada antes do uso.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0771 — ChartPeriod · [REF, ChartPeriod, p.PDF 2397–2397]

ChartPeriod retorna ENUM_TIMEFRAMES ou0 se gráfico inexistente; não confundir sentinel de falha com parâmetro PERIOD_CURRENT.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0772 — ChartRedraw · [REF, ChartRedraw, p.PDF 2398–2400]

Redraw força redesenho após propriedades; exemplo alterna cores de retângulo com Sleep. Esperas da demonstração não definem SLA do monitor.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0773 — ChartSetDouble · [REF, ChartSetDouble, p.PDF 2401–2402]

SetDouble enfileira propriedade gravável double; lote de alterações seguido de um Redraw evita sincronizações redundantes; conferir por GetDouble.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0774 — ChartSetInteger · [REF, ChartSetInteger, p.PDF 2403–2404]

SetInteger aceita long para datetime/int/color/bool/char e opcional subjanela; ativar eventos do mouse exige fila processada; exemplo Redraw após CHART_EVENT_MOUSE_MOVE.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0775 — ChartSetString · [REF, ChartSetString, p.PDF 2405–2406]

SetString enfileira string, limite2045 e excesso truncado; CHART_COMMENT pode substituir Comment. Nota do texto que lista SetString como getter é inconsistente com contrato assíncrono.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0776 — ChartGetDouble · [REF, ChartGetDouble, p.PDF 2407–2408]

GetDouble possui retorno direto ou bool+out; é síncrono e aguarda fila precedente. Variante bool distingue falha de preço mínimo/máximo zero.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0777 — ChartGetInteger · [REF, ChartGetInteger, p.PDF 2409–2410]

GetInteger retorna long ou bool+out, síncrono; subjanela default0. Exemplo dimensões em pixels implica layout dependente da janela.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0778 — ChartGetString · [REF, ChartGetString, p.PDF 2411–2412]

GetString retorna string ou bool+out, lê CHART_COMMENT e aguarda fila; comentário de tela não substitui registro persistente.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0779 — ChartNavigate · [REF, ChartNavigate, p.PDF 2413–2415]

Navigate desloca barras: positivo direita/fim, negativo esquerda/início; BEGIN/END+zero ancoram extremos. Exemplo desliga autoscroll, relê FIRST_VISIBLE_BAR.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0780 — ChartID · [REF, ChartID, p.PDF 2416–2417]

ChartID fornece long do gráfico atual; exemplo enumera lista usando First/Next com CHARTS_MAX, não substitui o contrato do identificador.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0781 — ChartIndicatorAdd · [REF, ChartIndicatorAdd, p.PDF 2418–2421]

IndicatorAdd exige símbolo/timeframe iguais, erro4114 em divergência. Nova subjanela=WINDOWS_TOTAL, maior falha. Indicador em escala errada pode estar invisível sem erro; AddIndicator exemplo retorna true mesmo após falha final.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0782 — ChartIndicatorDelete · [REF, ChartIndicatorDelete, p.PDF 2422–2424]

IndicatorDelete identifica shortname, primeiro homônimo; apaga dependentes no gráfico. Remover do gráfico não libera cálculo: IndicatorRelease separado.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0783 — ChartIndicatorGet · [REF, ChartIndicatorGet, p.PDF 2425–2426]

IndicatorGet retorna handle/INVALID_HANDLE e aumenta contador de uso; liberar explicitamente no mesmo programa com IndicatorRelease. Outro programa não recupera corretamente handle abandonado.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0784 — ChartIndicatorName · [REF, ChartIndicatorName, p.PDF 2427–2428]

IndicatorName retorna shortname por índice base0 na subjanela; nome de arquivo e nome curto não equivalem. Enumeração deve conservar janela e índice.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0785 — ChartIndicatorsTotal · [REF, ChartIndicatorsTotal, p.PDF 2429–2430]

IndicatorsTotal conta por subjanela; obter WINDOWS_TOTAL e percorrer todas, pois total de uma janela não é total do gráfico.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0786 — ChartWindowOnDropped · [REF, ChartWindowOnDropped, p.PDF 2431–2431]

WindowOnDropped retorna índice da subjanela onde EA/script foi arrastado,0 principal; informação da interação inicial, não seleção operacional.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0787 — ChartPriceOnDropped · [REF, ChartPriceOnDropped, p.PDF 2432–2432]

PriceOnDropped retorna coordenada de preço da soltura; preço de gesto não equivale a cotação executável.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0788 — ChartTimeOnDropped · [REF, ChartTimeOnDropped, p.PDF 2433–2433]

TimeOnDropped retorna datetime da coordenada de soltura; não confundir com instante servidor da execução do script.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0789 — ChartXOnDropped · [REF, ChartXOnDropped, p.PDF 2434–2434]

XOnDropped retorna pixel X crescente esquerda→direita; contexto de posicionamento visual apenas.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0790 — ChartYOnDropped · [REF, ChartYOnDropped, p.PDF 2435–2435]

YOnDropped retorna pixel Y crescente cima→baixo; demonstração imprime par X/Y, sem garantia entre resoluções.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0791 — ChartSetSymbolPeriod · [REF, ChartSetSymbolPeriod, p.PDF 2436–2437]

SetSymbolPeriod enfileira e mudança reinicializa EA; mesmo símbolo/período pode refrescar e recalcular indicadores sem ticks, inclusive fins de semana.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0792 — ChartScreenShot · [REF, ChartScreenShot, p.PDF 2438–2440]

ScreenShot salva GIF/PNG/BMP em Files, nome≤63; width/height/ALIGN definem recorte, Navigate prepara posição. Bool não comprova legibilidade ou auditoria visual.

Conhecimento aplicável ao painel do Monitor; nenhuma chamada específica do produto foi confirmada por inspeção de código neste lote. Provar fila processada, getter de retorno bool, identidade do gráfico, lifecycle e liberação dos handles. Validar captura/render nativa separadamente: screenshot produzido não é screenshot auditado.

### REF-0793 — Trade Functions · [REF, Trade Functions, p.PDF 2441–2546]

Order é instrução, deal execução e position obrigação agregada; uma ordem pode gerar vários deals. Contas netting/hedging exigem modelos distintos; famílias de consulta separadas de envio.

Sem uso autorizado no Monitor event-driven que não negocia. Cálculos/precheck são conhecimento; envio fica fora do escopo atual. Qualquer futura execução requer autorização separada, conta demo, retcodes, request_id e reconciliação de eventos/deals. MQL_NOT_RUN. API não define limites financeiros JPW.

### REF-0794 — OrderCalcMargin · [REF, OrderCalcMargin, p.PDF 2443–2446]

CalcMargin estima em moeda da conta no ambiente atual como se não houvesse ordens pendentes/posições; bool+out/error. Não é margem incremental real de carteira nem limite JPW.

Sem uso autorizado no Monitor event-driven que não negocia. Cálculos/precheck são conhecimento; envio fica fora do escopo atual. Qualquer futura execução requer autorização separada, conta demo, retcodes, request_id e reconciliação de eventos/deals. MQL_NOT_RUN. API não define limites financeiros JPW.

### REF-0795 — OrderCalcProfit · [REF, OrderCalcProfit, p.PDF 2447–2449]

CalcProfit aceita BUY/SELL,volume,preços, retorna estimativa em moeda da conta; muda com ambiente. Não estabelece soma contábil líquida, risco permitido ou garantia de execução.

Sem uso autorizado no Monitor event-driven que não negocia. Cálculos/precheck são conhecimento; envio fica fora do escopo atual. Qualquer futura execução requer autorização separada, conta demo, retcodes, request_id e reconciliação de eventos/deals. MQL_NOT_RUN. API não define limites financeiros JPW.

### REF-0796 — OrderCheck · [REF, OrderCheck, p.PDF 2450–2453]

OrderCheck preenche MqlTradeCheckResult; true de verificação básica não garante execução. Exemplo passa check com mercado fechado e Send falha10018, separação essencial.

Sem uso autorizado no Monitor event-driven que não negocia. Cálculos/precheck são conhecimento; envio fica fora do escopo atual. Qualquer futura execução requer autorização separada, conta demo, retcodes, request_id e reconciliação de eventos/deals. MQL_NOT_RUN. API não define limites financeiros JPW.

### REF-0797 — OrderSend · [REF, OrderSend, p.PDF 2454–2458]

OrderSend true indica aceitação básica/colocação no sistema, não deals concluídos; examinar retcode/retcode_external e OnTradeTransaction várias vezes por pedido. Não incorporar envio ao Monitor.

Sem uso autorizado no Monitor event-driven que não negocia. Cálculos/precheck são conhecimento; envio fica fora do escopo atual. Qualquer futura execução requer autorização separada, conta demo, retcodes, request_id e reconciliação de eventos/deals. MQL_NOT_RUN. API não define limites financeiros JPW.

### REF-0798 — OrderSendAsync · [REF, OrderSendAsync, p.PDF 2459–2469]

Async true indica envio, nem chegada/aceitação garantidas;10008 inicial e resposta posterior/eventos. Exemplo botões Buy/Sell usa volume fixo0.1 embora receba volume, log pode divergir.

Sem uso autorizado no Monitor event-driven que não negocia. Cálculos/precheck são conhecimento; envio fica fora do escopo atual. Qualquer futura execução requer autorização separada, conta demo, retcodes, request_id e reconciliação de eventos/deals. MQL_NOT_RUN. API não define limites financeiros JPW.

### REF-0799 — PositionsTotal · [REF, PositionsTotal, p.PDF 2470–2470]

PositionsTotal conta posições abertas: netting/exchange uma por símbolo, hedging várias; pendentes não são posições.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0800 — PositionGetSymbol · [REF, PositionGetSymbol, p.PDF 2471–2472]

PositionGetSymbol(index) retorna símbolo e seleciona posição automaticamente; vazio falha. Símbolo não é identidade única na conta hedging.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0801 — PositionSelect · [REF, PositionSelect, p.PDF 2473–2474]

PositionSelect(symbol) no hedging escolhe menor ticket; copia snapshot para ambiente e getters podem ler posição já extinta/alterada. Reselecionar imediatamente antes de leitura.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0802 — PositionSelectByTicket · [REF, PositionSelectByTicket, p.PDF 2475–2476]

SelectByTicket seleciona por ulong ticket e também copia snapshot; freshness exige nova seleção. Exemplo presume posição da ordem recém-aberta, não regra universal de identidade persistente.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0803 — PositionGetDouble · [REF, PositionGetDouble, p.PDF 2477–2479]

GetDouble requer posição selecionada; valor direto0 em falha, bool+out distingue zero válido. Exemplo apresenta volume/preços/SL/TP/swap/profit, não fórmula normativa líquida.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0804 — PositionGetInteger · [REF, PositionGetInteger, p.PDF 2480–2481]

GetInteger exige seleção e devolve long ou bool+out; tempos em segundos e milissegundos distintos; POSITION_IDENTIFIER serve ligação histórica, não índice.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0805 — PositionGetString · [REF, PositionGetString, p.PDF 2482–2484]

GetString exige seleção; vazio pode ser falha ou comentário/external ID vazio; variante bool preserva distinção. Enumeração por ticket evita confusão de símbolos duplicados.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0806 — PositionGetTicket · [REF, PositionGetTicket, p.PDF 2485–2486]

GetTicket(index base0) retorna ulong ou0 e seleciona; índice da lista não persiste. Exemplo compara POSITION_TYPE a POSITION_TYPE, provável erro de constante de comparação no texto.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0807 — OrdersTotal · [REF, OrdersTotal, p.PDF 2487–2487]

OrdersTotal conta ordens correntes, não posições/deals; pendentes mantêm semântica própria mesmo quando Toolbox exibe ambas categorias.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0808 — OrderGetTicket · [REF, OrderGetTicket, p.PDF 2488–2489]

OrderGetTicket(index) retorna0 falha e copia dados/seleciona; leitura posterior pode ser stale após execução/cancelamento/mutação. Reconsultar antes de consumo.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0809 — OrderSelect · [REF, OrderSelect, p.PDF 2490–2493]

OrderSelect(ticket) retorna bool e copia snapshot; getters não consultam automaticamente servidor. Exemplo envia pendente antes de selecionar, não é exemplo seguro para Monitor read-only.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0810 — OrderGetDouble · [REF, OrderGetDouble, p.PDF 2494–2497]

OrderGetDouble exige seleção atual; volume inicial e corrente distinguem execução residual; preço0/SL0/TP0 podem ser dados legítimos, bool+out evita inferência de erro.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0811 — OrderGetInteger · [REF, OrderGetInteger, p.PDF 2498–2503]

OrderGetInteger retorna long/bool+out; ticket,magic,position IDs,tipos,razão,tempos setup/done e unidades msc são distintos. Exemplos traduzem enums, não classificam programa JPW.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0812 — OrderGetString · [REF, OrderGetString, p.PDF 2504–2506]

OrderGetString exige seleção; comentário,símbolo,ID externo não devem ser usados como ticket/autoridade; preservar falha de consulta separada de vazio legítimo.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0813 — HistorySelect · [REF, HistorySelect, p.PDF 2507–2508]

HistorySelect usa intervalo de tempo do servidor, cria listas separadas de ordens/deals. HistoryOrderSelect/HistoryDealSelect por ticket reinicializam respectivas listas para um item: não usar dentro da enumeração sem estratégia.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0814 — HistorySelectByPosition · [REF, HistorySelectByPosition, p.PDF 2509–2512]

HistorySelectByPosition usa POSITION_IDENTIFIER, não ticket corrente; cria duas listas ligadas à posição. Copiar IDs antes de seleção por posição protege enumeração externa; exemplo faz lista temporária.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0815 — HistoryOrderSelect · [REF, HistoryOrderSelect, p.PDF 2513–2515]

HistoryOrderSelect(ticket) limpa lista e fica com única ordem quando sucesso; para percorrer resultado HistorySelect usar HistoryOrderGetTicket. Não confundir histórico com pendente atual.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0816 — HistoryOrdersTotal · [REF, HistoryOrdersTotal, p.PDF 2516–2516]

HistoryOrdersTotal exige HistorySelect/ByPosition prévio; tamanho representa lista selecionada no programa, não todo histórico global inevitavelmente.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0817 — HistoryOrderGetTicket · [REF, HistoryOrderGetTicket, p.PDF 2517–2518]

HistoryOrderGetTicket(index) exige lista histórica, retorna0 falha; exemplo traz setup/done e posição vinculada, delimitando ciclo de ordem.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0818 — HistoryOrderGetDouble · [REF, HistoryOrderGetDouble, p.PDF 2519–2522]

HistoryOrderGetDouble recebe ticket explícito e propriedade; variantes direto/bool+out. Volume residual e preço de ordem não equivalem a lucro de deal.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0819 — HistoryOrderGetInteger · [REF, HistoryOrderGetInteger, p.PDF 2523–2525]

HistoryOrderGetInteger ticket explícito, enums de ordem e long; exemplo busca semana e retorna-1 em ulong, sentinel perigoso se tratado como ticket válido.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0820 — HistoryOrderGetString · [REF, HistoryOrderGetString, p.PDF 2526–2528]

HistoryOrderGetString ticket explícito; comentário,símbolo,external ID de ordem; não assumir que comentário TP atribua sozinho resultado ou ownership.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0821 — HistoryDealSelect · [REF, HistoryDealSelect, p.PDF 2529–2531]

HistoryDealSelect(ticket) substitui lista de deals por único; OnTradeTransaction DEAL_ADD pode motivar consulta. Exemplo recebe deal_ticket mas lê ExtTicket global, inconsistente para eventos novos.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0822 — HistoryDealsTotal · [REF, HistoryDealsTotal, p.PDF 2532–2532]

HistoryDealsTotal exige HistorySelect/ByPosition; total de deals não é número de trades fechados nem de ordens.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0823 — HistoryDealGetTicket · [REF, HistoryDealGetTicket, p.PDF 2533–2534]

HistoryDealGetTicket(index) seleciona deal e devolve ulong/0; pedidos de histórico precedem iteração. Tipos balance/credit/charge etc não são compras/vendas.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0824 — HistoryDealGetDouble · [REF, HistoryDealGetDouble, p.PDF 2535–2539]

HistoryDealGetDouble ticket explícito fornece volume,preço,commission,swap,profit,fee,SL/TP separadamente; qualquer composição diária/líquida precisa regra JPW e prova contábil adicional.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0825 — HistoryDealGetInteger · [REF, HistoryDealGetInteger, p.PDF 2540–2542]

HistoryDealGetInteger ticket explícito fornece tempo/type/entry/order/position IDs etc; exemplo recorta7dias e retorna-1 em ulong. Não assumir último índice como ordenação normativa de negócio.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0826 — HistoryDealGetString · [REF, HistoryDealGetString, p.PDF 2543–2546]

HistoryDealGetString consulta símbolo,comentário,external ID pelo ticket; conteúdo textual não garante origem/pertencimento, nem reúne automaticamente custos/deals relacionados.

Aplicação conceitual atual ao monitoramento/reconciliação de conta e histórico; presença de cada função no código não foi auditada aqui. Provar seleção recente, modo netting/hedging, tickets versus identifier, janela em tempo servidor, falhas versus vazio/zero e preservação de listas. Casos parciais/reversões/custos precisam regra contábil explicitamente aprovada.

### REF-0827 — Trade Signals · [REF, Trade Signals, p.PDF 2547–2559]

Capítulo trata serviço de cópia de sinais, incluindo ações que alteram assinatura/configuração; não é mecanismo de alertas do Monitor.

Sem uso no Stoikus atual; cópia de sinais não é alerta do Monitor. Nenhuma assinatura/configuração alterada. Se pesquisado no futuro, provar seleção de catálogo, permissões e efeitos de escrita. Métricas e exemplos de filtro não constituem recomendação financeira.

### REF-0828 — SignalBaseGetDouble · [REF, SignalBaseGetDouble, p.PDF 2548–2548]

SignalBaseGetDouble lê propriedade real de sinal previamente selecionado; sem seleção correta não atribuir números a outro provedor.

Sem uso no Stoikus atual; cópia de sinais não é alerta do Monitor. Nenhuma assinatura/configuração alterada. Se pesquisado no futuro, provar seleção de catálogo, permissões e efeitos de escrita. Métricas e exemplos de filtro não constituem recomendação financeira.

### REF-0829 — SignalBaseGetInteger · [REF, SignalBaseGetInteger, p.PDF 2549–2549]

SignalBaseGetInteger lê propriedade inteira do sinal selecionado, incluindo ID/pips/subscribers nos exemplos; pips não validam rentabilidade adequada JPW.

Sem uso no Stoikus atual; cópia de sinais não é alerta do Monitor. Nenhuma assinatura/configuração alterada. Se pesquisado no futuro, provar seleção de catálogo, permissões e efeitos de escrita. Métricas e exemplos de filtro não constituem recomendação financeira.

### REF-0830 — SignalBaseGetString · [REF, SignalBaseGetString, p.PDF 2550–2550]

SignalBaseGetString lê nome/moeda/outros campos do sinal selecionado, por enum apropriado; metadado não é autorização para copiar.

Sem uso no Stoikus atual; cópia de sinais não é alerta do Monitor. Nenhuma assinatura/configuração alterada. Se pesquisado no futuro, provar seleção de catálogo, permissões e efeitos de escrita. Métricas e exemplos de filtro não constituem recomendação financeira.

### REF-0831 — SignalBaseSelect · [REF, SignalBaseSelect, p.PDF 2551–2551]

SignalBaseSelect usa índice, bool/error; exemplo filtra gratuitos com pips positivos/subscritores, somente demonstração e não recomendação de provedor.

Sem uso no Stoikus atual; cópia de sinais não é alerta do Monitor. Nenhuma assinatura/configuração alterada. Se pesquisado no futuro, provar seleção de catálogo, permissões e efeitos de escrita. Métricas e exemplos de filtro não constituem recomendação financeira.

### REF-0832 — SignalBaseTotal · [REF, SignalBaseTotal, p.PDF 2552–2552]

SignalBaseTotal conta sinais disponíveis naquele terminal; disponibilidade é contextual e pode mudar.

Sem uso no Stoikus atual; cópia de sinais não é alerta do Monitor. Nenhuma assinatura/configuração alterada. Se pesquisado no futuro, provar seleção de catálogo, permissões e efeitos de escrita. Métricas e exemplos de filtro não constituem recomendação financeira.

### REF-0833 — SignalInfoGetDouble · [REF, SignalInfoGetDouble, p.PDF 2553–2553]

SignalInfoGetDouble lê configurações reais de cópia, família diferente de catálogo SignalBase; não confundir configuração com desempenho.

Sem uso no Stoikus atual; cópia de sinais não é alerta do Monitor. Nenhuma assinatura/configuração alterada. Se pesquisado no futuro, provar seleção de catálogo, permissões e efeitos de escrita. Métricas e exemplos de filtro não constituem recomendação financeira.

### REF-0834 — SignalInfoGetInteger · [REF, SignalInfoGetInteger, p.PDF 2554–2554]

SignalInfoGetInteger lê configuração inteira de cópia; consulta não implica assinatura ativa nem aprovação JPW.

Sem uso no Stoikus atual; cópia de sinais não é alerta do Monitor. Nenhuma assinatura/configuração alterada. Se pesquisado no futuro, provar seleção de catálogo, permissões e efeitos de escrita. Métricas e exemplos de filtro não constituem recomendação financeira.

### REF-0835 — SignalInfoGetString · [REF, SignalInfoGetString, p.PDF 2555–2555]

SignalInfoGetString lê configuração string de cópia; valor sozinho não comprova integração existente.

Sem uso no Stoikus atual; cópia de sinais não é alerta do Monitor. Nenhuma assinatura/configuração alterada. Se pesquisado no futuro, provar seleção de catálogo, permissões e efeitos de escrita. Métricas e exemplos de filtro não constituem recomendação financeira.

### REF-0836 — SignalInfoSetDouble · [REF, SignalInfoSetDouble, p.PDF 2556–2556]

SignalInfoSetDouble muda configuração real de cópia, bool/error; não pertence a monitoramento passivo.

Sem uso no Stoikus atual; cópia de sinais não é alerta do Monitor. Nenhuma assinatura/configuração alterada. Se pesquisado no futuro, provar seleção de catálogo, permissões e efeitos de escrita. Métricas e exemplos de filtro não constituem recomendação financeira.

### REF-0837 — SignalInfoSetInteger · [REF, SignalInfoSetInteger, p.PDF 2557–2557]

SignalInfoSetInteger muda configuração inteira de cópia, bool/error; precisa projeto futuro específico, não habilitação implícita.

Sem uso no Stoikus atual; cópia de sinais não é alerta do Monitor. Nenhuma assinatura/configuração alterada. Se pesquisado no futuro, provar seleção de catálogo, permissões e efeitos de escrita. Métricas e exemplos de filtro não constituem recomendação financeira.

### REF-0838 — SignalSubscribe · [REF, SignalSubscribe, p.PDF 2558–2558]

SignalSubscribe usa signal_id long, bool/error e cria assinatura; não executar como parte desta pesquisa.

Sem uso no Stoikus atual; cópia de sinais não é alerta do Monitor. Nenhuma assinatura/configuração alterada. Se pesquisado no futuro, provar seleção de catálogo, permissões e efeitos de escrita. Métricas e exemplos de filtro não constituem recomendação financeira.

### REF-0839 — SignalUnSubscribe · [REF, SignalUnSubscribe, p.PDF 2559–2559]

SignalUnsubscribe cancela assinatura, bool/error; ação externa distinta de desligar alerta local.

Sem uso no Stoikus atual; cópia de sinais não é alerta do Monitor. Nenhuma assinatura/configuração alterada. Se pesquisado no futuro, provar seleção de catálogo, permissões e efeitos de escrita. Métricas e exemplos de filtro não constituem recomendação financeira.

### REF-0840 — Network Functions · [REF, Network Functions, p.PDF 2560–2611]

Sockets/WebRequest exigem endereço permitido adicionado pelo usuário no terminal, impossível programaticamente; capítulo também lista FTP/mail/push, cujos contratos completos ficam após2611.

Proposta futura, sem integração de sockets comprovada no produto neste lote. Nenhuma conexão ou endpoint criado. Provar allowlist manual, tipo de programa, ownership/close de handles, timeouts, framing, escrita/leitura parciais, TLS e desconexão. Compilar e executar testes nativos isolados antes de qualquer alegação operacional.

### REF-0841 — SocketCreate · [REF, SocketCreate, p.PDF 2562–2564]

SocketCreate só SOCKET_DEFAULT, handle/INVALID_HANDLE, limite128 por programa; liberar SocketClose. Apenas EA/scripts, indicador4014; amostra HTTP repetida não é protocolo robusto completo.

Proposta futura, sem integração de sockets comprovada no produto neste lote. Nenhuma conexão ou endpoint criado. Provar allowlist manual, tipo de programa, ownership/close de handles, timeouts, framing, escrita/leitura parciais, TLS e desconexão. Compilar e executar testes nativos isolados antes de qualquer alegação operacional.

### REF-0842 — SocketClose · [REF, SocketClose, p.PDF 2565–2567]

SocketClose encerra conexão e libera socket; bool/error5270 para handle errado. Encerramento precisa cobrir todos caminhos de erro na proposta futura.

Proposta futura, sem integração de sockets comprovada no produto neste lote. Nenhuma conexão ou endpoint criado. Provar allowlist manual, tipo de programa, ownership/close de handles, timeouts, framing, escrita/leitura parciais, TLS e desconexão. Compilar e executar testes nativos isolados antes de qualquer alegação operacional.

### REF-0843 — SocketConnect · [REF, SocketConnect, p.PDF 2568–2571]

SocketConnect recebe domínio/IP,porta e timeout_ms; exige allowlist,5272 na falha. Não adicionar endpoint automaticamente nem confundir conectado com dados atuais.

Proposta futura, sem integração de sockets comprovada no produto neste lote. Nenhuma conexão ou endpoint criado. Provar allowlist manual, tipo de programa, ownership/close de handles, timeouts, framing, escrita/leitura parciais, TLS e desconexão. Compilar e executar testes nativos isolados antes de qualquer alegação operacional.

### REF-0844 — SocketIsConnected · [REF, SocketIsConnected, p.PDF 2572–2575]

SocketIsConnected consulta estado atual, false não resume causa; exemplo consulta após Close, onde handle fechado pode ativar erro. Estado não comprova sucesso de entrega.

Proposta futura, sem integração de sockets comprovada no produto neste lote. Nenhuma conexão ou endpoint criado. Provar allowlist manual, tipo de programa, ownership/close de handles, timeouts, framing, escrita/leitura parciais, TLS e desconexão. Compilar e executar testes nativos isolados antes de qualquer alegação operacional.

### REF-0845 — SocketIsReadable · [REF, SocketIsReadable, p.PDF 2576–2578]

SocketIsReadable retorna bytes disponíveis ou0 em erro; zero exige GetLastError, não só vazio. Sem dados SocketRead pode bloquear até timeout; erro de sistema desconecta.

Proposta futura, sem integração de sockets comprovada no produto neste lote. Nenhuma conexão ou endpoint criado. Provar allowlist manual, tipo de programa, ownership/close de handles, timeouts, framing, escrita/leitura parciais, TLS e desconexão. Compilar e executar testes nativos isolados antes de qualquer alegação operacional.

### REF-0846 — SocketIsWritable · [REF, SocketIsWritable, p.PDF 2579–2582]

SocketIsWritable retorna capacidade atual, não confirmação de entrega; erro de sistema desconecta. Consulta prévia não remove necessidade de conferir bytes enviados.

Proposta futura, sem integração de sockets comprovada no produto neste lote. Nenhuma conexão ou endpoint criado. Provar allowlist manual, tipo de programa, ownership/close de handles, timeouts, framing, escrita/leitura parciais, TLS e desconexão. Compilar e executar testes nativos isolados antes de qualquer alegação operacional.

### REF-0847 — SocketTimeouts · [REF, SocketTimeouts, p.PDF 2583–2584]

SocketTimeouts configura timeouts do objeto SO para leitura/envio; diferente do timeout de uma operação SocketRead; bool/error, apenas EA/scripts.

Proposta futura, sem integração de sockets comprovada no produto neste lote. Nenhuma conexão ou endpoint criado. Provar allowlist manual, tipo de programa, ownership/close de handles, timeouts, framing, escrita/leitura parciais, TLS e desconexão. Compilar e executar testes nativos isolados antes de qualquer alegação operacional.

### REF-0848 — SocketRead · [REF, SocketRead, p.PDF 2585–2588]

SocketRead devolve bytes/-1, buffer/maxlen≤INT_MAX; excesso fica para próxima chamada, timeout pode atrasar programa. Erro5273/desconexão não deve virar payload vazio válido.

Proposta futura, sem integração de sockets comprovada no produto neste lote. Nenhuma conexão ou endpoint criado. Provar allowlist manual, tipo de programa, ownership/close de handles, timeouts, framing, escrita/leitura parciais, TLS e desconexão. Compilar e executar testes nativos isolados antes de qualquer alegação operacional.

### REF-0849 — SocketSend · [REF, SocketSend, p.PDF 2589–2592]

SocketSend devolve quantidade escrita/-1, não necessariamente entrega completa da mensagem; exemplos comparam len. Aplicação futura precisa tratar parcial e framing.

Proposta futura, sem integração de sockets comprovada no produto neste lote. Nenhuma conexão ou endpoint criado. Provar allowlist manual, tipo de programa, ownership/close de handles, timeouts, framing, escrita/leitura parciais, TLS e desconexão. Compilar e executar testes nativos isolados antes de qualquer alegação operacional.

### REF-0850 — SocketTlsHandshake · [REF, SocketTlsHandshake, p.PDF 2593–2597]

TlsHandshake requer TCP prévio e host string, falha5274; porta443 dispensa chamada explícita segundo REF. Exemplo passa InpTimeout não definido como host, inconsistência textual/compilação potencial.

Proposta futura, sem integração de sockets comprovada no produto neste lote. Nenhuma conexão ou endpoint criado. Provar allowlist manual, tipo de programa, ownership/close de handles, timeouts, framing, escrita/leitura parciais, TLS e desconexão. Compilar e executar testes nativos isolados antes de qualquer alegação operacional.

### REF-0851 — SocketTlsCertificate · [REF, SocketTlsCertificate, p.PDF 2598–2601]

TlsCertificate retorna subject/issuer/serial/thumbprint/expiration após TLS; thumbprint é SHA1 do certificado. Parâmetros por referência descritos [in] apesar de extração de dados; metadados não são política de confiança completa.

Proposta futura, sem integração de sockets comprovada no produto neste lote. Nenhuma conexão ou endpoint criado. Provar allowlist manual, tipo de programa, ownership/close de handles, timeouts, framing, escrita/leitura parciais, TLS e desconexão. Compilar e executar testes nativos isolados antes de qualquer alegação operacional.

### REF-0852 — SocketTlsRead · [REF, SocketTlsRead, p.PDF 2602–2605]

TlsRead aguarda quantidade pedida ou timeout do socket; retorna bytes/-1 e limita INT_MAX. Separar bloqueio de transporte do ciclo de monitoramento.

Proposta futura, sem integração de sockets comprovada no produto neste lote. Nenhuma conexão ou endpoint criado. Provar allowlist manual, tipo de programa, ownership/close de handles, timeouts, framing, escrita/leitura parciais, TLS e desconexão. Compilar e executar testes nativos isolados antes de qualquer alegação operacional.

### REF-0853 — SocketTlsReadAvailable · [REF, SocketTlsReadAvailable, p.PDF 2606–2610]

TlsReadAvailable lê disponíveis até maxlen e mantém restante; exemplo acumula ArrayCopy sem limitar a len efetivamente recebida e mistura GetTickCount64/GetTickCount no laço. Exige revisão antes de reutilização.

Proposta futura, sem integração de sockets comprovada no produto neste lote. Nenhuma conexão ou endpoint criado. Provar allowlist manual, tipo de programa, ownership/close de handles, timeouts, framing, escrita/leitura parciais, TLS e desconexão. Compilar e executar testes nativos isolados antes de qualquer alegação operacional.

### REF-0854 — SocketTlsSend · [REF, SocketTlsSend, p.PDF 2611–2611]

TlsSend contrato lido em2611: buffer uchar const, retorna bytes/-1, erro5273/desconexão, só EA/scripts. Exemplo começa aqui e continua2612–2614, não lido neste lote.

Proposta futura, sem integração de sockets comprovada no produto neste lote. Nenhuma conexão ou endpoint criado. Provar allowlist manual, tipo de programa, ownership/close de handles, timeouts, framing, escrita/leitura parciais, TLS e desconexão. Compilar e executar testes nativos isolados antes de qualquer alegação operacional.

## Síntese técnica aplicada

O Monitor deve separar a obtenção de um retrato consistente da interpretação financeira desse retrato. PositionSelect e OrderSelect copiam dados; getters não tornam o retrato atual por si. Em hedging, selecionar apenas por símbolo deixa outras posições fora da observação. No histórico, o recorte usa tempo servidor e constrói duas listas locais; uma consulta singular por ticket pode destruir a lista que um laço ainda percorre. A proposta metodológica é capturar IDs/tickets, declarar janela/seleção e registrar falhas antes de construir qualquer subtotal. Isto é orientação derivada dos contratos, não mudança implementada.

A referência distingue várias confirmações que não podem ser fundidas: enfileirar alteração de gráfico não prova aparência; OrderCheck não garante envio; OrderSend true não prova deal; OrderSendAsync true não garante chegada ao servidor; socket gravável não prova entrega; bytes recebidos não provam mensagem completa. Aplicações futuras devem ter evidência adequada à camada e não reaproveitar um bool de transporte como aprovação financeira.

Custom symbols servem como proposta de cenários reproduzíveis, mas seus setters e funções Replace podem apagar histórico, deixar alterações parciais ou criar buracos. A documentação oferece exemplos instrutivos com inconsistências: Trade/Quote trocados, Replace demonstrado por Update, inversão de extremos, impressão Bid usando Ask, parâmetro global usado no lugar de ticket recebido. Nenhum deles é benchmark validado ou implementação pronta. Para fixture de preço inverso, exigir OHLC consistente e relações de cotação formalmente definidas, não copiar a inversão ingênua.

Campos DEAL_PROFIT, DEAL_COMMISSION, DEAL_SWAP e DEAL_FEE são entradas separadas. O contrato de leitura não determina escopo diário, denominador, capital-base, tratamento de depósito/crédito, custos, reversão, ownership ou classificação dos quatro programas JPW. Esses itens dependem de norma e reconciliação explícitas, inclusive quando a obtenção via API foi tecnicamente correta.

## Anomalias prioritárias e limites qualificados

1. PDF2327–2330, SetSessionTrade: chamadas Quote e helper de nome diferente do definido; contrastar com PDF2326 antes de reaproveitar.
2. PDF2338–2339, RatesReplace: usa Update e imprime Update. O exemplo não prova substituição integral com exclusão de lacunas.
3. PDF2343–2344: inversão high=1/high e low=1/low gera high menor que low; tabela exibida confirma inversão de extremos no texto.
4. PDF2352/2361/2370: descritor imprime campo tick.ask ao rotular Bid; saídas não são oráculo de integridade bid/ask.
5. PDF2401/2404/2405: notas listam ChartSetString entre getters síncronos; contratos específicos GetString/SetString resolvem distinção.
6. PDF2420: helper AddIndicator retorna true mesmo se ChartIndicatorAdd final falhar; sucesso do helper não prova inclusão.
7. PDF2465–2466: BuyAsync/SellAsync recebem volume mas usam0.1 fixo; log de0.01 na amostra não representa volume enviado.
8. PDF2478/2483/2485: comparação POSITION_TYPE==POSITION_TYPE no texto, em vez de discriminador BUY/SELL; não usar saída como teste de direção.
9. PDF2530: helper seleciona deal_ticket mas consulta ExtTicket global; no evento pode descrever deal diferente.
10. PDF2594: SocketTlsHandshake(socket,InpTimeout) conflita com host string do contrato e não há declaração local mostrada desse input; suspeita de exemplo inválido, não teste executado.
11. PDF2610: ArrayCopy copia block inteiro sem count=len e condição mistura relógio32/64bits; modelo de acumulação requer revisão para não anexar resíduos nem errar timeout. A presença de comentários “...” confirma que parser HTTP/framing não está completo.
12. PDF2371 descreve volumes de forma verbalmente ambígua sobre negativos, mas os exemplos permitem um negativo quando outro é positivo; testar combinações e prioridade volume_real antes de formalizar validação.

Esses pontos são suspeitas localizadas no material extraído. Não se atribuem como bugs confirmados do terminal ou do Stoikus. Não houve inspeção visual das páginas, nem execução dos exemplos. Dados/certificados/logs de2024 no livro são ilustrações históricas, não conectividade ou validade de certificado atuais.
