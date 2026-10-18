# Leitura semântica REF — lote 15b

Escopo integral: páginas físicas PDF 6181–6659 (479 páginas) do texto extraído. Todos os 14 lotes foram expostos integralmente ao leitor, cada um com menos de 28.000 caracteres e max_output_tokens=20000; nenhum texto de página foi truncado. Catálogo JSON inicial truncou e foi reparado por exposição compacta integral. Leitura de texto não é revisão das figuras: NOT_PERFORMED_NO_VISUAL_INFERENCE. MQL_NOT_RUN. Não foram alterados produto, manual, harness ou Git. Ramos ancestrais e CBmpButton têm cobertura limitada à interseção.

As notas distinguem contrato da biblioteca de proposta de aplicação; nenhuma proposta confirma adoção no Stoikus. Os exemplos impressos contêm inconsistências relevantes: MemoryAvailable/MemoryTotal, DiskSpace/MDiskSpace, assinaturas de eventos, ReverseShort com corpo de ReverseLong, CheckClose monetário e divergência RSI. Conferir cabeçalhos instalados é etapa futura, não realizada. Classes Check de CExpert podem executar operações; callbacks vazios podem retornar true; OR em CloseAll/DeleteOrders não comprova êxito integral. Estes pontos impedem tratar API como política normativa ou teste de produto.

## REF-0001 — MQL5 Reference

[REF, Standard Library / MQL5 Reference, p.PDF 6181–6659]. Ramo ancestral parcialmente coberto: apenas interseção PDF 6181–6659. Esta leitura acompanha propriedades finais de terminal, estratégias e controles; não declara leitura das páginas externas ao lote.

## REF-1136 — Standard Library

[REF, Standard Library / Standard Library, p.PDF 6181–6659]. Ramo ancestral parcialmente coberto: apenas interseção PDF 6181–6659. Esta leitura acompanha propriedades finais de terminal, estratégias e controles; não declara leitura das páginas externas ao lote.

## REF-3147 — Trade Classes

[REF, Standard Library / Trade Classes, p.PDF 6181–6193]. Ramo ancestral parcialmente coberto: apenas interseção PDF 6181–6193. Esta leitura acompanha propriedades finais de terminal, estratégias e controles; não declara leitura das páginas externas ao lote.

## REF-3440 — CTerminalInfo

[REF, Standard Library / CTerminalInfo, p.PDF 6181–6193]. Ramo ancestral parcialmente coberto: apenas interseção PDF 6181–6193. Esta leitura acompanha propriedades finais de terminal, estratégias e controles; não declara leitura das páginas externas ao lote.

## REF-3452 — MemoryAvailable

[REF, Standard Library / MemoryAvailable, p.PDF 6181–6181]. Memória livre é informada em MB; há divergência entre título MemoryAvailable, assinatura MemoryTotal e propriedade MEMORY_TOTAL. Validar cabeçalho instalado antes de usar como limite de recursos.

## REF-3453 — MemoryUsed

[REF, Standard Library / MemoryUsed, p.PDF 6182–6182]. Memória usada pelo terminal/agente é medida em MB, útil em diagnóstico; não mede a memória isolada do Stoikus.

## REF-3454 — IsX64

[REF, Standard Library / IsX64, p.PDF 6183–6183]. IsX64 distingue a versão de 64 bits; registrar ambiente não comprova compatibilidade de um componente.

## REF-3455 — OpenCLSupport

[REF, Standard Library / OpenCLSupport, p.PDF 6184–6184]. Versão OpenCL usa codificação hexadecimal, como 0x00010002; zero indica ausência. Apenas pesquisa futura, sem ativação no Stoikus.

## REF-3456 — DiskSpace

[REF, Standard Library / DiskSpace, p.PDF 6185–6185]. Espaço livre refere-se à pasta MQL5\Files do terminal/agente, em MB; título DiskSpace e assinatura MDiskSpace divergem.

## REF-3457 — Language

[REF, Standard Library / Language, p.PDF 6186–6186]. Language retorna idioma do terminal; proposta de diagnóstico de localização, sem inferir idioma das regras.

## REF-3458 — Name

[REF, Standard Library / Name, p.PDF 6187–6187]. Name identifica nome do terminal; pode integrar recibo de ambiente.

## REF-3459 — Company

[REF, Standard Library / Company, p.PDF 6188–6188]. Company identifica empresa do terminal; não substitui identificação da conta/corretora.

## REF-3460 — Path

[REF, Standard Library / Path, p.PDF 6189–6189]. Path identifica instalação; distinguir da pasta de dados ao localizar artefatos.

## REF-3461 — DataPath

[REF, Standard Library / DataPath, p.PDF 6190–6190]. DataPath identifica diretório de dados específico do terminal; importante para instalação futura verificável.

## REF-3462 — CommonDataPath

[REF, Standard Library / CommonDataPath, p.PDF 6191–6191]. CommonDataPath identifica dados compartilhados entre terminais; compartilhamento exige evitar colisões de recibos.

## REF-3463 — InfoInteger

[REF, Standard Library / InfoInteger, p.PDF 6192–6192]. InfoInteger oferece acesso genérico a propriedades inteiras de ambiente; a assinatura impressa usa TerminalInfoInteger, exigindo conferir API instalada.

## REF-3464 — InfoString

[REF, Standard Library / InfoString, p.PDF 6193–6193]. InfoString oferece acesso a propriedades textuais; assinatura impressa usa TerminalInfoString, sem prova de chamada executada.

## REF-3465 — Strategy Modules

[REF, Standard Library / Strategy Modules, p.PDF 6194–6492]. Strategy Modules organiza sinal, trailing e gestão monetária em Include\Expert; arquitetura de estratégias executoras, não prova de que Stoikus a utiliza.

## REF-3466 — Base classes for Expert Advisors

[REF, Standard Library / Base classes for Expert Advisors, p.PDF 6197–6366]. Classes-base separam dados comuns, executor CExpert, sinais, trailing e money; interfaces são reaproveitáveis como estudo sem ativar negociação.

## REF-3467 — CExpertBase

[REF, Standard Library / CExpertBase, p.PDF 6198–6230]. CExpertBase concentra símbolo/período/magic, dependências de séries e fases de inicialização; separar configuração, validação e prontidão.

## REF-3468 — InitPhase

[REF, Standard Library / InitPhase, p.PDF 6200–6200]. Inicialização tem fases: Init, configuração, validação, InitIndicators e conclusão; métodos permitidos mudam por fase. Proposta de ciclo explícito evita usar série antes de pronta.

## REF-3469 — TrendType

[REF, Standard Library / TrendType, p.PDF 6201–6201]. TrendType recebe M_TYPE_TREND e altera configuração de tendência; não equivale a uma regra normativa JPW.

## REF-3470 — UsedSeries

[REF, Standard Library / UsedSeries, p.PDF 6202–6202]. UsedSeries é máscara dos bits 0–7: Open, High, Low, Close, Spread, Time, TickVolume e RealVolume. Dependências devem ser declaradas.

## REF-3471 — EveryTick

[REF, Standard Library / EveryTick, p.PDF 6203–6203]. EveryTick=true processa cada alteração de preço; false restringe ao novo candle de símbolo/período. A cadência precisa constar do experimento.

## REF-3472 — Open

[REF, Standard Library / Open, p.PDF 6204–6204]. Open acessa elemento por índice; série não usada ou índice fora da faixa retorna EMPTY_VALUE. Proposta Stoikus: rejeitar sentinel e registrar contexto, sem tratá-lo como cotação ou volume válido.

## REF-3473 — High

[REF, Standard Library / High, p.PDF 6205–6205]. High acessa elemento por índice; série não usada ou índice fora da faixa retorna EMPTY_VALUE. Proposta Stoikus: rejeitar sentinel e registrar contexto, sem tratá-lo como cotação ou volume válido.

## REF-3474 — Low

[REF, Standard Library / Low, p.PDF 6206–6206]. Low acessa elemento por índice; série não usada ou índice fora da faixa retorna EMPTY_VALUE. Proposta Stoikus: rejeitar sentinel e registrar contexto, sem tratá-lo como cotação ou volume válido.

## REF-3475 — Close

[REF, Standard Library / Close, p.PDF 6207–6207]. Close acessa elemento por índice; série não usada ou índice fora da faixa retorna EMPTY_VALUE. Proposta Stoikus: rejeitar sentinel e registrar contexto, sem tratá-lo como cotação ou volume válido.

## REF-3476 — Spread

[REF, Standard Library / Spread, p.PDF 6208–6208]. Spread acessa elemento por índice; série não usada ou índice fora da faixa retorna EMPTY_VALUE. Proposta Stoikus: rejeitar sentinel e registrar contexto, sem tratá-lo como cotação ou volume válido.

## REF-3477 — Time

[REF, Standard Library / Time, p.PDF 6209–6209]. Time acessa elemento por índice; série não usada ou índice fora da faixa retorna EMPTY_VALUE. Proposta Stoikus: rejeitar sentinel e registrar contexto, sem tratá-lo como cotação ou volume válido.

## REF-3478 — TickVolume

[REF, Standard Library / TickVolume, p.PDF 6210–6210]. TickVolume acessa elemento por índice; série não usada ou índice fora da faixa retorna EMPTY_VALUE. Proposta Stoikus: rejeitar sentinel e registrar contexto, sem tratá-lo como cotação ou volume válido.

## REF-3479 — RealVolume

[REF, Standard Library / RealVolume, p.PDF 6211–6211]. RealVolume acessa elemento por índice; série não usada ou índice fora da faixa retorna EMPTY_VALUE. Proposta Stoikus: rejeitar sentinel e registrar contexto, sem tratá-lo como cotação ou volume válido.

## REF-3480 — Init

[REF, Standard Library / Init, p.PDF 6212–6212]. Init recebe CSymbolInfo, timeframe e peso convencional do ponto 2/4 dígitos; validar cada retorno antes da próxima fase.

## REF-3481 — Symbol

[REF, Standard Library / Symbol, p.PDF 6213–6213]. Symbol altera símbolo quando distinto do inicial; não herdar inadvertidamente o gráfico atual.

## REF-3482 — Period

[REF, Standard Library / Period, p.PDF 6214–6214]. Period altera timeframe quando distinto do inicial; registrar unidade temporal no diagnóstico.

## REF-3483 — Magic

[REF, Standard Library / Magic, p.PDF 6215–6215]. Magic define identificador ulong do EA; identificação não é autorização de gestão.

## REF-3484 — ValidationSettings

[REF, Standard Library / ValidationSettings, p.PDF 6216–6216]. ValidationSettings retorna sucesso/falha da configuração; um booleano positivo não valida regra financeira.

## REF-3485 — SetPriceSeries

[REF, Standard Library / SetPriceSeries, p.PDF 6217–6217]. SetPriceSeries injeta ponteiros para Open/High/Low/Close externos; preservar validade dos objetos e contexto de símbolo/período.

## REF-3486 — SetOtherSeries

[REF, Standard Library / SetOtherSeries, p.PDF 6218–6218]. SetOtherSeries injeta Spread/Time/TickVolume/RealVolume; a nota impressa repete indevidamente texto de séries de preço.

## REF-3487 — InitIndicators

[REF, Standard Library / InitIndicators, p.PDF 6219–6219]. InitIndicators inicializa indicadores/séries; séries próprias são necessárias para símbolo ou período diferentes do inicial.

## REF-3488 — InitOpen

[REF, Standard Library / InitOpen, p.PDF 6220–6220]. InitOpen inicializa série específica quando necessária em símbolo/período diferente do inicial, usando coleção CIndicators. Tratar false e não processar dependência incompleta.

## REF-3489 — InitHigh

[REF, Standard Library / InitHigh, p.PDF 6221–6221]. InitHigh inicializa série específica quando necessária em símbolo/período diferente do inicial, usando coleção CIndicators. Tratar false e não processar dependência incompleta.

## REF-3490 — InitLow

[REF, Standard Library / InitLow, p.PDF 6222–6222]. InitLow inicializa série específica quando necessária em símbolo/período diferente do inicial, usando coleção CIndicators. Tratar false e não processar dependência incompleta.

## REF-3491 — InitClose

[REF, Standard Library / InitClose, p.PDF 6223–6223]. InitClose inicializa série específica quando necessária em símbolo/período diferente do inicial, usando coleção CIndicators. Tratar false e não processar dependência incompleta.

## REF-3492 — InitSpread

[REF, Standard Library / InitSpread, p.PDF 6224–6224]. InitSpread inicializa série específica quando necessária em símbolo/período diferente do inicial, usando coleção CIndicators. Tratar false e não processar dependência incompleta.

## REF-3493 — InitTime

[REF, Standard Library / InitTime, p.PDF 6225–6225]. InitTime inicializa série específica quando necessária em símbolo/período diferente do inicial, usando coleção CIndicators. Tratar false e não processar dependência incompleta.

## REF-3494 — InitTickVolume

[REF, Standard Library / InitTickVolume, p.PDF 6226–6226]. InitTickVolume inicializa série específica quando necessária em símbolo/período diferente do inicial, usando coleção CIndicators. Tratar false e não processar dependência incompleta.

## REF-3495 — InitRealVolume

[REF, Standard Library / InitRealVolume, p.PDF 6227–6227]. InitRealVolume inicializa série específica quando necessária em símbolo/período diferente do inicial, usando coleção CIndicators. Tratar false e não processar dependência incompleta.

## REF-3496 — PriceLevelUnit

[REF, Standard Library / PriceLevelUnit, p.PDF 6228–6228]. PriceLevelUnit retorna o peso convencional do ponto 2/4 dígitos; não confundir com tick monetário.

## REF-3497 — StartIndex

[REF, Standard Library / StartIndex, p.PDF 6229–6229]. StartIndex escolhe 0 para candle atual ou 1 para último completo; fixar opção para evitar mistura entre intrabar e fechamento.

## REF-3498 — CompareMagic

[REF, Standard Library / CompareMagic, p.PDF 6230–6230]. CompareMagic compara o identificador ulong e retorna correspondência; combinar com símbolo e modo da conta.

## REF-3499 — CExpert

[REF, Standard Library / CExpert, p.PDF 6231–6320]. CExpert contém algoritmo executor virtual e associa posição a símbolo/magic, com distinção hedging; não substituir monitor por esta base sem projeto autorizado.

## REF-3500 — Init

[REF, Standard Library / Init, p.PDF 6236–6236]. CExpert::Init recebe símbolo, timeframe, every_tick e magic; assinatura bool contrasta com retorno textual None. Conferir cabeçalho real.

## REF-3501 — Magic

[REF, Standard Library / Magic, p.PDF 6237–6237]. Magic propaga novo ID a trade, signal, money e trailing existentes antes de alterar base; alteração deve manter rastreabilidade.

## REF-3502 — InitSignal

[REF, Standard Library / InitSignal, p.PDF 6238–6238]. InitSignal(NULL) usa base de sinais sem lógica própria; inicialização não cria estratégia válida.

## REF-3503 — InitTrailing

[REF, Standard Library / InitTrailing, p.PDF 6239–6239]. InitTrailing(NULL) usa base que não faz trailing; omissão não equivale a proteção ativa.

## REF-3504 — InitMoney

[REF, Standard Library / InitMoney, p.PDF 6240–6240]. InitMoney(NULL) usa lote mínimo; ausência de gestão não significa risco zero.

## REF-3505 — InitTrade

[REF, Standard Library / InitTrade, p.PDF 6241–6241]. InitTrade recebe magic e objeto CExpertTrade opcional; é fronteira executora e não deve ser ligada ao monitor Stoikus.

## REF-3506 — Deinit

[REF, Standard Library / Deinit, p.PDF 6242–6242]. Deinit encerra instância; proposta exige limpeza independente de sucesso parcial de inicialização.

## REF-3507 — OnTickProcess

[REF, Standard Library / OnTickProcess, p.PDF 6243–6243]. OnTickProcess configura tratamento do evento correspondente; padrão true para tick. Proposta: habilitar deliberadamente e encaminhar eventos; flag não garante recebimento.

## REF-3508 — OnTradeProcess

[REF, Standard Library / OnTradeProcess, p.PDF 6244–6244]. OnTradeProcess configura tratamento do evento correspondente; padrão false para este evento. Proposta: habilitar deliberadamente e encaminhar eventos; flag não garante recebimento.

## REF-3509 — OnTimerProcess

[REF, Standard Library / OnTimerProcess, p.PDF 6245–6245]. OnTimerProcess configura tratamento do evento correspondente; padrão false para este evento. Proposta: habilitar deliberadamente e encaminhar eventos; flag não garante recebimento.

## REF-3510 — OnChartEventProcess

[REF, Standard Library / OnChartEventProcess, p.PDF 6246–6246]. OnChartEventProcess configura tratamento do evento correspondente; padrão false para este evento. Proposta: habilitar deliberadamente e encaminhar eventos; flag não garante recebimento.

## REF-3511 — OnBookEventProcess

[REF, Standard Library / OnBookEventProcess, p.PDF 6247–6247]. OnBookEventProcess configura tratamento do evento correspondente; padrão false para este evento. Proposta: habilitar deliberadamente e encaminhar eventos; flag não garante recebimento. Assinatura impressa repete OnChartEventProcess.

## REF-3512 — MaxOrders

[REF, Standard Library / MaxOrders, p.PDF 6248–6248]. MaxOrders tem getter/setter e padrão 1; quantidade de ordens não expressa orçamento financeiro.

## REF-3513 — Signal

[REF, Standard Library / Signal, p.PDF 6249–6249]. Signal retorna ponteiro para objeto de sinais; consumidor deve verificar validade.

## REF-3514 — ValidationSettings

[REF, Standard Library / ValidationSettings, p.PDF 6250–6250]. ValidationSettings valida também objetos auxiliares; não confundir com aceite operacional.

## REF-3515 — InitIndicators

[REF, Standard Library / InitIndicators, p.PDF 6251–6251]. InitIndicators inicializa dependências de todos auxiliares; séries de outro contexto são explicitamente inicializadas.

## REF-3516 — OnTick

[REF, Standard Library / OnTick, p.PDF 6252–6252]. OnTick é handler virtual do evento; não retorna valor. Aplicação: arquitetura por eventos deve manter monitoramento separado de envio de ordens.

## REF-3517 — OnTrade

[REF, Standard Library / OnTrade, p.PDF 6253–6253]. OnTrade é handler virtual do evento; não retorna valor. Aplicação: arquitetura por eventos deve manter monitoramento separado de envio de ordens.

## REF-3518 — OnTimer

[REF, Standard Library / OnTimer, p.PDF 6254–6254]. OnTimer é handler virtual do evento; não retorna valor. Aplicação: arquitetura por eventos deve manter monitoramento separado de envio de ordens.

## REF-3519 — OnChartEvent

[REF, Standard Library / OnChartEvent, p.PDF 6255–6255]. OnChartEvent é handler virtual do evento; recebe id e parâmetros long/double/string. Aplicação: arquitetura por eventos deve manter monitoramento separado de envio de ordens.

## REF-3520 — OnBookEvent

[REF, Standard Library / OnBookEvent, p.PDF 6256–6256]. OnBookEvent é handler virtual do evento; recebe símbolo. Aplicação: arquitetura por eventos deve manter monitoramento separado de envio de ordens.

## REF-3521 — InitParameters

[REF, Standard Library / InitParameters, p.PDF 6257–6257]. InitParameters da base não faz nada e sempre retorna true; é necessário override para parâmetros reais.

## REF-3522 — DeinitTrade

[REF, Standard Library / DeinitTrade, p.PDF 6258–6258]. DeinitTrade desinicializa o objeto auxiliar correspondente e não retorna valor. Proposta: liberar recursos também após inicialização parcial.

## REF-3523 — DeinitSignal

[REF, Standard Library / DeinitSignal, p.PDF 6259–6259]. DeinitSignal desinicializa o objeto auxiliar correspondente e não retorna valor. Proposta: liberar recursos também após inicialização parcial.

## REF-3524 — DeinitTrailing

[REF, Standard Library / DeinitTrailing, p.PDF 6260–6260]. DeinitTrailing desinicializa o objeto auxiliar correspondente e não retorna valor. Proposta: liberar recursos também após inicialização parcial.

## REF-3525 — DeinitMoney

[REF, Standard Library / DeinitMoney, p.PDF 6261–6261]. DeinitMoney desinicializa o objeto auxiliar correspondente e não retorna valor. Proposta: liberar recursos também após inicialização parcial.

## REF-3526 — DeinitIndicators

[REF, Standard Library / DeinitIndicators, p.PDF 6262–6262]. DeinitIndicators encerra indicadores/séries de todos auxiliares; evitar recursos órfãos.

## REF-3527 — Refresh

[REF, Standard Library / Refresh, p.PDF 6263–6263]. Refresh primeiro atualiza cotações, filtra timeframes e atualiza indicadores. false pode indicar ausência de processamento, não apenas falha.

## REF-3528 — Processing

[REF, Standard Library / Processing, p.PDF 6264–6265]. Processing prioriza reversão, fechamento e trailing de posição, depois exclusão/trailing de pendentes e abertura. É algoritmo executor; Stoikus monitor não deve chamá-lo como atualização neutra.

## REF-3529 — SelectPosition

[REF, Standard Library / SelectPosition, p.PDF 6266–6266]. SelectPosition usa símbolo+magic em hedging e símbolo em outros modos. Texto declara void, implementação bool; testar contrato real antes de adaptar.

## REF-3530 — CheckOpen

[REF, Standard Library / CheckOpen, p.PDF 6267–6267]. CheckOpen tenta long antes de short e pode executar operação; nome Check não significa consulta sem efeitos.

## REF-3531 — CheckOpenLong

[REF, Standard Library / CheckOpenLong, p.PDF 6268–6268]. CheckOpenLong consulta sinal, ajusta expiração e chama OpenLong; bool indica operação processada.

## REF-3532 — CheckOpenShort

[REF, Standard Library / CheckOpenShort, p.PDF 6269–6269]. CheckOpenShort consulta sinal, ajusta expiração e chama OpenShort; é caminho executor.

## REF-3533 — OpenLong

[REF, Standard Library / OpenLong, p.PDF 6270–6270]. OpenLong rejeita EMPTY_VALUE e lote zero, obtém lote e chama Buy; não basta copiar guardas para autorizar operações.

## REF-3534 — OpenShort

[REF, Standard Library / OpenShort, p.PDF 6271–6271]. OpenShort rejeita EMPTY_VALUE e lote zero, obtém lote e chama Sell; fronteira ausente do monitor autorizado.

## REF-3535 — CheckReverse

[REF, Standard Library / CheckReverse, p.PDF 6272–6272]. CheckReverse despacha pelo tipo da posição selecionada; pode executar reversão.

## REF-3536 — CheckReverseLong

[REF, Standard Library / CheckReverseLong, p.PDF 6273–6273]. CheckReverseLong obtém preço/SL/TP/expiração do sinal e chama ReverseLong; não é verificação pura.

## REF-3537 — CheckReverseShort

[REF, Standard Library / CheckReverseShort, p.PDF 6274–6274]. CheckReverseShort implementado separadamente, mas assinatura impressa diz CheckReverseLong; conferir fonte instalada.

## REF-3538 — ReverseLong

[REF, Standard Library / ReverseLong, p.PDF 6275–6276]. Reversão long calcula lote e, em hedging, fecha ticket antes de vender volume restante. Duas operações podem falhar em etapas distintas.

## REF-3539 — ReverseShort

[REF, Standard Library / ReverseShort, p.PDF 6277–6278]. Descrição de ReverseShort prevê Buy e fechamento prévio em hedging, mas exemplo na p.6278 repete ReverseLong e Sell. Não copiar exemplo contraditório.

## REF-3540 — CheckClose

[REF, Standard Library / CheckClose, p.PDF 6279–6279]. CheckClose consulta gestão monetária antes de sinal e pode fechar posição e excluir ordens; retorno agregado não prova sucesso de cada etapa.

## REF-3541 — CheckCloseLong

[REF, Standard Library / CheckCloseLong, p.PDF 6280–6280]. CheckCloseLong consulta sinal e encaminha fechamento do lado correspondente; pode enviar operação. Não usar como consulta neutra no monitor.

## REF-3542 — CheckCloseShort

[REF, Standard Library / CheckCloseShort, p.PDF 6281–6281]. CheckCloseShort consulta sinal e encaminha fechamento do lado correspondente; pode enviar operação. Não usar como consulta neutra no monitor.

## REF-3543 — CloseAll

[REF, Standard Library / CloseAll, p.PDF 6282–6282]. CloseAll diferencia fechamento por ticket em hedging de operação oposta em netting; combina resultado com DeleteOrders por OR, que pode mascarar falha parcial.

## REF-3544 — Close

[REF, Standard Library / Close, p.PDF 6283–6283]. Close chama PositionClose por símbolo; em hedging identificar explicitamente o ticket antes de qualquer proposta executora.

## REF-3545 — CloseLong

[REF, Standard Library / CloseLong, p.PDF 6284–6284]. CloseLong usa ticket em hedging e Sell do volume atual em netting; rejeita EMPTY_VALUE.

## REF-3546 — CloseShort

[REF, Standard Library / CloseShort, p.PDF 6285–6285]. CloseShort usa ticket em hedging e Buy do volume atual em netting; rejeita EMPTY_VALUE.

## REF-3547 — CheckTrailingStop

[REF, Standard Library / CheckTrailingStop, p.PDF 6286–6286]. CheckTrailingStop despacha pelo lado da posição selecionada e pode modificar proteção.

## REF-3548 — CheckTrailingStopLong

[REF, Standard Library / CheckTrailingStopLong, p.PDF 6287–6287]. CheckTrailingStopLong substitui SL/TP EMPTY_VALUE pelos existentes antes de modificar; preservar componente não alterado.

## REF-3549 — CheckTrailingStopShort

[REF, Standard Library / CheckTrailingStopShort, p.PDF 6288–6288]. CheckTrailingStopShort preserva SL/TP existentes quando sugestão usa EMPTY_VALUE; não interpretar sentinel como preço.

## REF-3550 — TrailingStopLong

[REF, Standard Library / TrailingStopLong, p.PDF 6289–6289]. TrailingStopLong chama PositionModify por símbolo com SL/TP; exige auditoria própria de identidade em hedging.

## REF-3551 — TrailingStopShort

[REF, Standard Library / TrailingStopShort, p.PDF 6290–6290]. TrailingStopShort chama PositionModify; assinatura impressa nomeia Long, implementação Short. Não transformar erro editorial em API.

## REF-3552 — CheckTrailingOrderLong

[REF, Standard Library / CheckTrailingOrderLong, p.PDF 6291–6291]. CheckTrailingOrderLong consulta sinal e calcula delta entre preço atual da ordem e proposta.

## REF-3553 — CheckTrailingOrderShort

[REF, Standard Library / CheckTrailingOrderShort, p.PDF 6292–6292]. CheckTrailingOrderShort consulta sinal e calcula delta para modificar pendente; pode produzir efeito.

## REF-3554 — TrailingOrderLong

[REF, Standard Library / TrailingOrderLong, p.PDF 6293–6293]. TrailingOrderLong desloca preço, SL e TP pelo mesmo delta e preserva validade/expiração; verificar zero de proteção antes de reutilizar.

## REF-3555 — TrailingOrderShort

[REF, Standard Library / TrailingOrderShort, p.PDF 6294–6294]. TrailingOrderShort desloca preço, SL e TP com delta e preserva tipo temporal/expiração; não é atualização visual.

## REF-3556 — CheckDeleteOrderLong

[REF, Standard Library / CheckDeleteOrderLong, p.PDF 6295–6295]. CheckDeleteOrderLong exclui por expiração local vencida ou sinal de saída; dependência do relógio é explícita.

## REF-3557 — CheckDeleteOrderShort

[REF, Standard Library / CheckDeleteOrderShort, p.PDF 6296–6296]. CheckDeleteOrderShort exclui por expiração local ou condição de fechamento short; bool representa operação.

## REF-3558 — DeleteOrders

[REF, Standard Library / DeleteOrders, p.PDF 6297–6297]. DeleteOrders percorre ordens em ordem inversa e filtra apenas símbolo no exemplo, agregando resultados por OR. Não comprova isolamento por magic nem exclusão integral.

## REF-3559 — DeleteOrder

[REF, Standard Library / DeleteOrder, p.PDF 6298–6298]. DeleteOrder chama OrderDelete pelo ticket da ordem selecionada. Escopo executor; verificar propriedade e resultado servidor antes de qualquer adaptação futura.

## REF-3560 — DeleteOrderLong

[REF, Standard Library / DeleteOrderLong, p.PDF 6299–6299]. DeleteOrderLong chama OrderDelete pelo ticket da ordem selecionada. Escopo executor; verificar propriedade e resultado servidor antes de qualquer adaptação futura.

## REF-3561 — DeleteOrderShort

[REF, Standard Library / DeleteOrderShort, p.PDF 6300–6300]. DeleteOrderShort chama OrderDelete pelo ticket da ordem selecionada. Escopo executor; verificar propriedade e resultado servidor antes de qualquer adaptação futura.

## REF-3562 — LotOpenLong

[REF, Standard Library / LotOpenLong, p.PDF 6301–6301]. LotOpenLong delega ao gestor monetário com preço e SL; volume calculado não valida autorização.

## REF-3563 — LotOpenShort

[REF, Standard Library / LotOpenShort, p.PDF 6302–6302]. LotOpenShort delega cálculo ao gestor com preço e SL; distinguir lote de risco monetário.

## REF-3564 — LotReverse

[REF, Standard Library / LotReverse, p.PDF 6303–6303]. LotReverse delega ao gestor com posição e SL; em hedging há ajuste posterior pelo volume existente.

## REF-3565 — PrepareHistoryDate

[REF, Standard Library / PrepareHistoryDate, p.PDF 6304–6304]. PrepareHistoryDate limita acompanhamento ao início do mês, com pelo menos um dia; não serve como histórico integral do livro financeiro.

## REF-3566 — HistoryPoint

[REF, Standard Library / HistoryPoint, p.PDF 6305–6305]. HistoryPoint salva contagens de posições, ordens, negócios e ordens históricas; parâmetro evita recursão.

## REF-3567 — CheckTradeState

[REF, Standard Library / CheckTradeState, p.PDF 6306–6306]. CheckTradeState compara contagens com checkpoint e chama handlers; contagem não conserva todos detalhes de transações.

## REF-3568 — WaitEvent

[REF, Standard Library / WaitEvent, p.PDF 6307–6307]. WaitEvent adiciona máscara de eventos esperados; não é bloqueio síncrono de confirmação pelo servidor.

## REF-3569 — NoWaitEvent

[REF, Standard Library / NoWaitEvent, p.PDF 6308–6308]. NoWaitEvent remove flags de espera; não desfaz operação de mercado.

## REF-3570 — TradeEventPositionStopTake

[REF, Standard Library / TradeEventPositionStopTake, p.PDF 6309–6309]. TradeEventPositionStopTake é callback virtual da alteração de estado indicada pelo nome; base não faz nada e retorna true. Proposta: recibo deve registrar fatos reais, pois retorno do stub não demonstra evento tratado funcionalmente.

## REF-3571 — TradeEventOrderTriggered

[REF, Standard Library / TradeEventOrderTriggered, p.PDF 6310–6310]. TradeEventOrderTriggered é callback virtual da alteração de estado indicada pelo nome; base não faz nada e retorna true. Proposta: recibo deve registrar fatos reais, pois retorno do stub não demonstra evento tratado funcionalmente.

## REF-3572 — TradeEventPositionOpened

[REF, Standard Library / TradeEventPositionOpened, p.PDF 6311–6311]. TradeEventPositionOpened é callback virtual da alteração de estado indicada pelo nome; base não faz nada e retorna true. Proposta: recibo deve registrar fatos reais, pois retorno do stub não demonstra evento tratado funcionalmente.

## REF-3573 — TradeEventPositionVolumeChanged

[REF, Standard Library / TradeEventPositionVolumeChanged, p.PDF 6312–6312]. TradeEventPositionVolumeChanged é callback virtual da alteração de estado indicada pelo nome; base não faz nada e retorna true. Proposta: recibo deve registrar fatos reais, pois retorno do stub não demonstra evento tratado funcionalmente.

## REF-3574 — TradeEventPositionModified

[REF, Standard Library / TradeEventPositionModified, p.PDF 6313–6313]. TradeEventPositionModified é callback virtual da alteração de estado indicada pelo nome; base não faz nada e retorna true. Proposta: recibo deve registrar fatos reais, pois retorno do stub não demonstra evento tratado funcionalmente.

## REF-3575 — TradeEventPositionClosed

[REF, Standard Library / TradeEventPositionClosed, p.PDF 6314–6314]. TradeEventPositionClosed é callback virtual da alteração de estado indicada pelo nome; base não faz nada e retorna true. Proposta: recibo deve registrar fatos reais, pois retorno do stub não demonstra evento tratado funcionalmente.

## REF-3576 — TradeEventOrderPlaced

[REF, Standard Library / TradeEventOrderPlaced, p.PDF 6315–6315]. TradeEventOrderPlaced é callback virtual da alteração de estado indicada pelo nome; base não faz nada e retorna true. Proposta: recibo deve registrar fatos reais, pois retorno do stub não demonstra evento tratado funcionalmente.

## REF-3577 — TradeEventOrderModified

[REF, Standard Library / TradeEventOrderModified, p.PDF 6316–6316]. TradeEventOrderModified é callback virtual da alteração de estado indicada pelo nome; base não faz nada e retorna true. Proposta: recibo deve registrar fatos reais, pois retorno do stub não demonstra evento tratado funcionalmente.

## REF-3578 — TradeEventOrderDeleted

[REF, Standard Library / TradeEventOrderDeleted, p.PDF 6317–6317]. TradeEventOrderDeleted é callback virtual da alteração de estado indicada pelo nome; base não faz nada e retorna true. Proposta: recibo deve registrar fatos reais, pois retorno do stub não demonstra evento tratado funcionalmente.

## REF-3579 — TradeEventNotIdentified

[REF, Standard Library / TradeEventNotIdentified, p.PDF 6318–6318]. TradeEventNotIdentified reconhece dificuldade de classificar vários eventos que chegam juntos; manter reconciliação em vez de inventar causalidade.

## REF-3580 — TimeframeAdd

[REF, Standard Library / TimeframeAdd, p.PDF 6319–6319]. TimeframeAdd registra timeframe acompanhado; proposta permite cadência explícita por contexto.

## REF-3581 — TimeframesFlags

[REF, Standard Library / TimeframesFlags, p.PDF 6320–6320]. TimeframesFlags produz máscara dos períodos com novo candle a partir de MqlDateTime.

## REF-3582 — CExpertSignal

[REF, Standard Library / CExpertSignal, p.PDF 6321–6355]. CExpertSignal define composição e interfaces de condição/parâmetros; base não produz entrada, mas documenta reversão. Força não é probabilidade calibrada.

## REF-3583 — BasePrice

[REF, Standard Library / BasePrice, p.PDF 6324–6324]. BasePrice define referência para preços do sinal; documentar origem e unidade.

## REF-3584 — UsedSeries

[REF, Standard Library / UsedSeries, p.PDF 6325–6325]. UsedSeries retorna máscara somente se símbolo/período coincidem com contexto de trabalho; caso contrário retorna zero.

## REF-3585 — Weight

[REF, Standard Library / Weight, p.PDF 6326–6326]. Weight define peso do módulo; contrato da página apenas seta valor sem retorno. Proposta: persistir configuração de composição explicitamente; não presumir validação ou qualidade de sinal.

## REF-3586 — PatternsUsage

[REF, Standard Library / PatternsUsage, p.PDF 6327–6327]. PatternsUsage define máscara/configuração de padrões usados; contrato da página apenas seta valor sem retorno. Proposta: persistir configuração de composição explicitamente; não presumir validação ou qualidade de sinal.

## REF-3587 — General

[REF, Standard Library / General, p.PDF 6328–6328]. General define parâmetro General; contrato da página apenas seta valor sem retorno. Proposta: persistir configuração de composição explicitamente; não presumir validação ou qualidade de sinal.

## REF-3588 — Ignore

[REF, Standard Library / Ignore, p.PDF 6329–6329]. Ignore define máscara Ignore; contrato da página apenas seta valor sem retorno. Proposta: persistir configuração de composição explicitamente; não presumir validação ou qualidade de sinal.

## REF-3589 — Invert

[REF, Standard Library / Invert, p.PDF 6330–6330]. Invert define máscara Invert; contrato da página apenas seta valor sem retorno. Proposta: persistir configuração de composição explicitamente; não presumir validação ou qualidade de sinal.

## REF-3590 — ThresholdOpen

[REF, Standard Library / ThresholdOpen, p.PDF 6331–6331]. ThresholdOpen varia 0–100 e controla votação para abrir; força de sinal não é probabilidade calibrada.

## REF-3591 — ThresholdClose

[REF, Standard Library / ThresholdClose, p.PDF 6332–6332]. ThresholdClose varia 0–100 e controla votação para sair; assinatura impressa repete ThresholdOpen.

## REF-3592 — PriceLevel

[REF, Standard Library / PriceLevel, p.PDF 6333–6333]. PriceLevel é distância na unidade PriceLevelUnit relativa ao preço base, não preço absoluto.

## REF-3593 — StopLevel

[REF, Standard Library / StopLevel, p.PDF 6334–6334]. StopLevel é distância relativa à entrada em unidade de preço da classe; não é regra de perda diária.

## REF-3594 — TakeLevel

[REF, Standard Library / TakeLevel, p.PDF 6335–6335]. TakeLevel é distância do TP relativa à entrada; separar configuração de plataforma de política JPW.

## REF-3595 — Expiration

[REF, Standard Library / Expiration, p.PDF 6336–6336]. Expiration é expressa em candles para pendentes; não interpretar como segundos.

## REF-3596 — Magic

[REF, Standard Library / Magic, p.PDF 6337–6337]. Magic do sinal é documentado como int, enquanto base usa ulong; conferir tipo instalado antes de converter IDs.

## REF-3597 — ValidationSettings

[REF, Standard Library / ValidationSettings, p.PDF 6338–6338]. ValidationSettings retorna validade do objeto; não prova qualidade preditiva.

## REF-3598 — InitIndicators

[REF, Standard Library / InitIndicators, p.PDF 6339–6339]. InitIndicators recebe coleção e prepara contexto alternativo de símbolo/período.

## REF-3599 — AddFilter

[REF, Standard Library / AddFilter, p.PDF 6340–6340]. AddFilter adiciona CExpertSignal à composição; texto nomeia parâmetro indicators em vez de filter.

## REF-3600 — CheckOpenLong

[REF, Standard Library / CheckOpenLong, p.PDF 6341–6341]. CheckOpenLong verifica condição do lado e ação indicados; preço/SL/TP/expiração passam por referência. Aqui true expressa condição/parâmetro válido, distinto do Check de CExpert que pode executar. Aplicação futura deve preservar essa separação.

## REF-3601 — CheckOpenShort

[REF, Standard Library / CheckOpenShort, p.PDF 6342–6342]. CheckOpenShort verifica condição do lado e ação indicados; preço/SL/TP/expiração passam por referência. Aqui true expressa condição/parâmetro válido, distinto do Check de CExpert que pode executar. Aplicação futura deve preservar essa separação.

## REF-3602 — OpenLongParams

[REF, Standard Library / OpenLongParams, p.PDF 6343–6343]. OpenLongParams define parâmetros do lado e ação indicados; preço/SL/TP/expiração passam por referência. Aqui true expressa condição/parâmetro válido, distinto do Check de CExpert que pode executar. Aplicação futura deve preservar essa separação.

## REF-3603 — OpenShortParams

[REF, Standard Library / OpenShortParams, p.PDF 6344–6344]. OpenShortParams define parâmetros do lado e ação indicados; preço/SL/TP/expiração passam por referência. Aqui true expressa condição/parâmetro válido, distinto do Check de CExpert que pode executar. Aplicação futura deve preservar essa separação.

## REF-3604 — CheckCloseLong

[REF, Standard Library / CheckCloseLong, p.PDF 6345–6345]. CheckCloseLong verifica condição do lado e ação indicados; preço de fechamento passa por referência. Aqui true expressa condição/parâmetro válido, distinto do Check de CExpert que pode executar. Aplicação futura deve preservar essa separação.

## REF-3605 — CheckCloseShort

[REF, Standard Library / CheckCloseShort, p.PDF 6346–6346]. CheckCloseShort verifica condição do lado e ação indicados; preço de fechamento passa por referência. Aqui true expressa condição/parâmetro válido, distinto do Check de CExpert que pode executar. Aplicação futura deve preservar essa separação.

## REF-3606 — CloseLongParams

[REF, Standard Library / CloseLongParams, p.PDF 6347–6347]. CloseLongParams define parâmetros do lado e ação indicados; preço de fechamento passa por referência. Aqui true expressa condição/parâmetro válido, distinto do Check de CExpert que pode executar. Aplicação futura deve preservar essa separação.

## REF-3607 — CloseShortParams

[REF, Standard Library / CloseShortParams, p.PDF 6348–6348]. CloseShortParams define parâmetros do lado e ação indicados; preço de fechamento passa por referência. Aqui true expressa condição/parâmetro válido, distinto do Check de CExpert que pode executar. Aplicação futura deve preservar essa separação.

## REF-3608 — CheckReverseLong

[REF, Standard Library / CheckReverseLong, p.PDF 6349–6349]. CheckReverseLong verifica condição do lado e ação indicados; preço/SL/TP/expiração passam por referência. Aqui true expressa condição/parâmetro válido, distinto do Check de CExpert que pode executar. Aplicação futura deve preservar essa separação.

## REF-3609 — CheckReverseShort

[REF, Standard Library / CheckReverseShort, p.PDF 6350–6350]. CheckReverseShort verifica condição do lado e ação indicados; preço/SL/TP/expiração passam por referência. Aqui true expressa condição/parâmetro válido, distinto do Check de CExpert que pode executar. Aplicação futura deve preservar essa separação.

## REF-3610 — CheckTrailingOrderLong

[REF, Standard Library / CheckTrailingOrderLong, p.PDF 6351–6351]. CheckTrailingOrderLong verifica condição do lado e ação indicados; preço passa por referência; trailing recebe COrderInfo. Aqui true expressa condição/parâmetro válido, distinto do Check de CExpert que pode executar. Aplicação futura deve preservar essa separação.

## REF-3611 — CheckTrailingOrderShort

[REF, Standard Library / CheckTrailingOrderShort, p.PDF 6352–6352]. CheckTrailingOrderShort verifica condição do lado e ação indicados; preço passa por referência; trailing recebe COrderInfo. Aqui true expressa condição/parâmetro válido, distinto do Check de CExpert que pode executar. Aplicação futura deve preservar essa separação.

## REF-3612 — LongCondition

[REF, Standard Library / LongCondition, p.PDF 6353–6353]. LongCondition retorna força 1–100 ou zero; implementação base sempre zero.

## REF-3613 — ShortCondition

[REF, Standard Library / ShortCondition, p.PDF 6354–6354]. ShortCondition retorna força 1–100 ou zero; implementação base sempre zero.

## REF-3614 — Direction

[REF, Standard Library / Direction, p.PDF 6355–6355]. Direction combina filtros e retorna direção assinada; magnitude representa força, não probabilidade de lucro.

## REF-3615 — CExpertTrailing

[REF, Standard Library / CExpertTrailing, p.PDF 6356–6359]. CExpertTrailing fornece interface sem trailing ativo; descendentes propõem SL/TP e executor envia alteração.

## REF-3616 — CheckTrailingStopLong

[REF, Standard Library / CheckTrailingStopLong, p.PDF 6358–6358]. CheckTrailingStopLong recebe posição e referências SL/TP, mas base sempre false. Não inferir proteção ativa a partir da interface.

## REF-3617 — CheckTrailingStopShort

[REF, Standard Library / CheckTrailingStopShort, p.PDF 6359–6359]. CheckTrailingStopShort recebe posição e referências SL/TP, mas base sempre false. Não inferir proteção ativa a partir da interface.

## REF-3618 — CExpertMoney

[REF, Standard Library / CExpertMoney, p.PDF 6360–6366]. CExpertMoney fornece interface de volume/risco; declaração e hierarquia divergem no texto. Percent sozinho não define política de risco.

## REF-3619 — Percent

[REF, Standard Library / Percent, p.PDF 6361–6361]. Percent define percentual de risco do gestor; significado concreto varia por descendente, margem e risco não são intercambiáveis.

## REF-3620 — ValidationSettings

[REF, Standard Library / ValidationSettings, p.PDF 6362–6362]. ValidationSettings da base monetária sempre true; exige validação adicional por política.

## REF-3621 — CheckOpenLong

[REF, Standard Library / CheckOpenLong, p.PDF 6363–6363]. CheckOpenLong retorna volume para o lado correspondente a partir de preço e SL. Contrato monetário não comprova execução nem regra JPW.

## REF-3622 — CheckOpenShort

[REF, Standard Library / CheckOpenShort, p.PDF 6364–6364]. CheckOpenShort retorna volume para o lado correspondente a partir de preço e SL. Contrato monetário não comprova execução nem regra JPW.

## REF-3623 — CheckReverse

[REF, Standard Library / CheckReverse, p.PDF 6365–6365]. CheckReverse monetário retorna volume com base na posição e SL; conferir limites independentes do modelo.

## REF-3624 — CheckClose

[REF, Standard Library / CheckClose, p.PDF 6366–6366]. CheckClose é declarado double sem argumentos, mas descrição fala em bool e chamador anterior passa posição; inconsistência documental impede copiar contrato.

## REF-3625 — Modules of Trade Signals

[REF, Standard Library / Modules of Trade Signals, p.PDF 6367–6441]. Até 64 módulos votam com previsões -100..100 e pesos 0..1. Resultado é média aritmética dos produtos, dividida pelo número de módulos: exemplos dão -12 e -30, não média normalizada pela soma dos pesos. Thresholds de entrada/saída são 0..100.

## REF-3626 — Signals of the Indicator Accelerator Oscillator

[REF, Standard Library / Signals of the Indicator Accelerator Oscillator, p.PDF 6370–6372]. AC combina posição perante zero e crescimento/queda em múltiplos candles; força e ausência de objeção são conceitos distintos. Aplicação: somente catálogo de hipóteses para estudo; não é sinal implementado nem evidência de desempenho do Stoikus. Candle analisado muda entre índice 0 e 1 conforme cadência.

## REF-3627 — Signals of the Indicator Adaptive Moving Average

[REF, Standard Library / Signals of the Indicator Adaptive Moving Average, p.PDF 6373–6376]. AMA distingue rompimento falho, cruzamento e sombra atravessando média conforme inclinação; depende de período, shift, método e preço aplicado. Aplicação: somente catálogo de hipóteses para estudo; não é sinal implementado nem evidência de desempenho do Stoikus. Candle analisado muda entre índice 0 e 1 conforme cadência.

## REF-3628 — Signals of the Indicator Awesome Oscillator

[REF, Standard Library / Signals of the Indicator Awesome Oscillator, p.PDF 6377–6380]. AO admite saucer, cruzamento do zero e divergência confinada ao lado do zero; slope atual expressa ausência de objeção. Aplicação: somente catálogo de hipóteses para estudo; não é sinal implementado nem evidência de desempenho do Stoikus. Candle analisado muda entre índice 0 e 1 conforme cadência.

## REF-3629 — Signals of the Oscillator Bears Power

[REF, Standard Library / Signals of the Oscillator Bears Power, p.PDF 6381–6382]. Bears Power gera apenas compras por reversão abaixo de zero ou divergência; não gera sinais vendedores. Aplicação: somente catálogo de hipóteses para estudo; não é sinal implementado nem evidência de desempenho do Stoikus. Candle analisado muda entre índice 0 e 1 conforme cadência.

## REF-3630 — Signals of the Oscillator Bulls Power

[REF, Standard Library / Signals of the Oscillator Bulls Power, p.PDF 6383–6384]. Bulls Power gera apenas vendas por reversão acima de zero ou divergência; não gera sinais compradores. Aplicação: somente catálogo de hipóteses para estudo; não é sinal implementado nem evidência de desempenho do Stoikus. Candle analisado muda entre índice 0 e 1 conforme cadência.

## REF-3631 — Signals of the Oscillator Commodity Channel Index

[REF, Standard Library / Signals of the Oscillator Commodity Channel Index, p.PDF 6385–6388]. CCI combina reversão além de ±100, divergência e divergência dupla de três extremos; preço aplicado e período são parâmetros. Aplicação: somente catálogo de hipóteses para estudo; não é sinal implementado nem evidência de desempenho do Stoikus. Candle analisado muda entre índice 0 e 1 conforme cadência.

## REF-3632 — Signals of the Oscillator DeMarker

[REF, Standard Library / Signals of the Oscillator DeMarker, p.PDF 6389–6392]. DeMarker combina reversão além de 0,3/0,7 e divergências simples/duplas; ausência de objeção segue inclinação. Aplicação: somente catálogo de hipóteses para estudo; não é sinal implementado nem evidência de desempenho do Stoikus. Candle analisado muda entre índice 0 e 1 conforme cadência.

## REF-3633 — Signals of the Indicator Double Exponential Moving Average

[REF, Standard Library / Signals of the Indicator Double Exponential Moving Average, p.PDF 6393–6396]. DEMA usa inclinação e cruzamentos/sombras para distinguir rompimento falho, cruzamento forte e retorno à linha. Aplicação: somente catálogo de hipóteses para estudo; não é sinal implementado nem evidência de desempenho do Stoikus. Candle analisado muda entre índice 0 e 1 conforme cadência.

## REF-3634 — Signals of the Indicator Envelopes

[REF, Standard Library / Signals of the Indicator Envelopes, p.PDF 6397–6399]. Envelopes combina proximidade de uma borda e rompimento da oposta; desvio é percentual da média e não pontos. Aplicação: somente catálogo de hipóteses para estudo; não é sinal implementado nem evidência de desempenho do Stoikus. Candle analisado muda entre índice 0 e 1 conforme cadência.

## REF-3635 — Signals of the Indicator Fractal Adaptive Moving Average

[REF, Standard Library / Signals of the Indicator Fractal Adaptive Moving Average, p.PDF 6400–6403]. FrAMA apresenta modelos de cruzamento, rompimento falho e sombra, condicionados à inclinação da média. Aplicação: somente catálogo de hipóteses para estudo; não é sinal implementado nem evidência de desempenho do Stoikus. Candle analisado muda entre índice 0 e 1 conforme cadência.

## REF-3636 — Signals of the Intraday Time Filter

[REF, Standard Library / Signals of the Intraday Time Filter, p.PDF 6404–6405]. Filtro intradiário não gera compra/venda: apenas permite horários/dias; máscaras de exclusão têm prioridade sobre permissões. Não substitui calendário/servidor/fuso JPW.

## REF-3637 — Signals of the Oscillator MACD

[REF, Standard Library / Signals of the Oscillator MACD, p.PDF 6406–6411]. MACD inclui reversão, cruzamento principal/sinal, cruzamento de zero e divergências simples/duplas; parametriza EMAs rápida/lenta e suavização. Aplicação: somente catálogo de hipóteses para estudo; não é sinal implementado nem evidência de desempenho do Stoikus. Candle analisado muda entre índice 0 e 1 conforme cadência.

## REF-3638 — Signals of the Indicator Moving Average

[REF, Standard Library / Signals of the Indicator Moving Average, p.PDF 6412–6415]. MA distingue três padrões pelo preço OHLC e inclinação; parâmetros de método, período, shift e aplicado precisam acompanhar o experimento. Aplicação: somente catálogo de hipóteses para estudo; não é sinal implementado nem evidência de desempenho do Stoikus. Candle analisado muda entre índice 0 e 1 conforme cadência.

## REF-3639 — Signals of the Indicator Parabolic SAR

[REF, Standard Library / Signals of the Indicator Parabolic SAR, p.PDF 6416–6417]. PSAR sinaliza mudança de lado em relação ao preço entre candle analisado e anterior; Step e Maximum regulam indicador. Aplicação: somente catálogo de hipóteses para estudo; não é sinal implementado nem evidência de desempenho do Stoikus. Candle analisado muda entre índice 0 e 1 conforme cadência.

## REF-3640 — Signals of the Oscillator Relative Strength Index

[REF, Standard Library / Signals of the Oscillator Relative Strength Index, p.PDF 6418–6423]. RSI combina reversão em 30/70, failed swing, divergências e cabeça/ombros no oscilador; divergência de compra contém ambiguidade textual na p.6419. Aplicação: somente catálogo de hipóteses para estudo; não é sinal implementado nem evidência de desempenho do Stoikus. Candle analisado muda entre índice 0 e 1 conforme cadência.

## REF-3641 — Signals of the Oscillator Relative Vigor Index

[REF, Standard Library / Signals of the Oscillator Relative Vigor Index, p.PDF 6424–6425]. RVI usa cruzamento de linhas principal/sinal para ambos lados; inclinação sinaliza ausência de objeção. Aplicação: somente catálogo de hipóteses para estudo; não é sinal implementado nem evidência de desempenho do Stoikus. Candle analisado muda entre índice 0 e 1 conforme cadência.

## REF-3642 — Signals of the Oscillator Stochastic

[REF, Standard Library / Signals of the Oscillator Stochastic, p.PDF 6426–6430]. Stochastic admite reversão, cruzamento principal/sinal e divergências simples/duplas; K, D, slowing e aplicado são parâmetros. Aplicação: somente catálogo de hipóteses para estudo; não é sinal implementado nem evidência de desempenho do Stoikus. Candle analisado muda entre índice 0 e 1 conforme cadência.

## REF-3643 — Signals of the Oscillator Triple Exponential Average

[REF, Standard Library / Signals of the Oscillator Triple Exponential Average, p.PDF 6431–6434]. TRIX combina reversão, zero e divergência; parâmetros são período, aplicado e peso. Aplicação: somente catálogo de hipóteses para estudo; não é sinal implementado nem evidência de desempenho do Stoikus. Candle analisado muda entre índice 0 e 1 conforme cadência.

## REF-3644 — Signals of the Indicator Triple Exponential Moving Average

[REF, Standard Library / Signals of the Indicator Triple Exponential Moving Average, p.PDF 6435–6438]. TEMA usa cruzamentos e sombras em torno da média condicionados pela inclinação; não é o oscilador TRIX. Aplicação: somente catálogo de hipóteses para estudo; não é sinal implementado nem evidência de desempenho do Stoikus. Candle analisado muda entre índice 0 e 1 conforme cadência.

## REF-3645 — Signals of the Oscillator Williams Percent Range

[REF, Standard Library / Signals of the Oscillator Williams Percent Range, p.PDF 6439–6441]. WPR usa reversão além de -80/-20 e divergência; escala negativa exige cautela com linguagem de máximo/mínimo na p.6441. Aplicação: somente catálogo de hipóteses para estudo; não é sinal implementado nem evidência de desempenho do Stoikus. Candle analisado muda entre índice 0 e 1 conforme cadência.

## REF-3646 — Trailing Stop Classes

[REF, Standard Library / Trailing Stop Classes, p.PDF 6442–6469]. Família trailing oferece distância fixa, MA, nenhum e PSAR; comparar proposta de nível com operação real de modificar.

## REF-3647 — CTrailingFixedPips

[REF, Standard Library / CTrailingFixedPips, p.PDF 6443–6449]. FixedPips sugere SL por distância favorável com base no SL existente ou entrada; every_tick=false limita lógica ao novo candle, mantendo TP no servidor entre candles.

## REF-3648 — StopLevel

[REF, Standard Library / StopLevel, p.PDF 6445–6445]. StopLevel do trailing usa pontos convencionais 2/4 dígitos e zero desliga trailing; distinto de SL absoluto.

## REF-3649 — ProfitLevel

[REF, Standard Library / ProfitLevel, p.PDF 6446–6446]. ProfitLevel configura distância de TP em pontos convencionais; nota diz zero desliga trailing, mas algoritmo geral condiciona primeiro ao StopLevel. Confirmar código antes de concluir.

## REF-3650 — ValidationSettings

[REF, Standard Library / ValidationSettings, p.PDF 6447–6447]. Validação aceita zero ou distância superior ao mínimo para stops; condição de mercado ainda requer verificação em execução.

## REF-3651 — CheckTrailingStopLong

[REF, Standard Library / CheckTrailingStopLong, p.PDF 6448–6448]. Long compara Bid com base SL existente ou entrada mais distância; sugere SL e eventualmente TP, sem enviar por si só.

## REF-3652 — CheckTrailingStopShort

[REF, Standard Library / CheckTrailingStopShort, p.PDF 6449–6449]. Short compara Ask com base SL existente ou entrada menos distância; respeitar diferença Bid/Ask.

## REF-3653 — CTrailingMA

[REF, Standard Library / CTrailingMA, p.PDF 6450–6459]. TrailingMA usa média do último candle completo e só melhora SL dentro do limite permitido; é política de estratégia futura, não regra vigente do monitor.

## REF-3654 — Period

[REF, Standard Library / Period, p.PDF 6452–6452]. Period define período da média móvel; proposta de experimento deve registrar configuração e contexto antes de InitIndicators, sem ativação de trailing no Stoikus.

## REF-3655 — Shift

[REF, Standard Library / Shift, p.PDF 6453–6453]. Shift define deslocamento da média em candles; proposta de experimento deve registrar configuração e contexto antes de InitIndicators, sem ativação de trailing no Stoikus.

## REF-3656 — Method

[REF, Standard Library / Method, p.PDF 6454–6454]. Method define método ENUM_MA_METHOD; proposta de experimento deve registrar configuração e contexto antes de InitIndicators, sem ativação de trailing no Stoikus.

## REF-3657 — Applied

[REF, Standard Library / Applied, p.PDF 6455–6455]. Applied define preço ENUM_APPLIED_PRICE; proposta de experimento deve registrar configuração e contexto antes de InitIndicators, sem ativação de trailing no Stoikus.

## REF-3658 — InitIndicators

[REF, Standard Library / InitIndicators, p.PDF 6456–6456]. InitIndicators cria dependências na coleção de indicadores/séries do CExpert; false impede tratar trailing como pronto.

## REF-3659 — ValidationSettings

[REF, Standard Library / ValidationSettings, p.PDF 6457–6457]. Validação da média exige período positivo; não verifica eficiência econômica.

## REF-3660 — CheckTrailingStopLong

[REF, Standard Library / CheckTrailingStopLong, p.PDF 6458–6458]. Trailing MA long usa média do candle completo anterior, melhora SL/base e respeita máximo permitido próximo ao preço.

## REF-3661 — CheckTrailingStopShort

[REF, Standard Library / CheckTrailingStopShort, p.PDF 6459–6459]. Trailing MA short usa candle completo anterior, reduz SL/base e respeita mínimo permitido.

## REF-3662 — CTrailingNone

[REF, Standard Library / CTrailingNone, p.PDF 6460–6462]. TrailingNone é stub explícito, condições sempre falsas; desativar trailing não cria proteção alternativa.

## REF-3663 — CheckTrailingStopLong

[REF, Standard Library / CheckTrailingStopLong, p.PDF 6461–6461]. TrailingNone long sempre false, sem proposta de proteção dinâmica.

## REF-3664 — CheckTrailingStopShort

[REF, Standard Library / CheckTrailingStopShort, p.PDF 6462–6462]. TrailingNone short sempre false; ausência de trailing é opção explícita.

## REF-3665 — CTrailingPSAR

[REF, Standard Library / CTrailingPSAR, p.PDF 6463–6469]. TrailingPSAR usa indicador do candle completo anterior para sugerir melhoria de SL dentro da distância mínima.

## REF-3666 — Step

[REF, Standard Library / Step, p.PDF 6465–6465]. Step define passo do PSAR; proposta de experimento deve registrar configuração e contexto antes de InitIndicators, sem ativação de trailing no Stoikus.

## REF-3667 — Maximum

[REF, Standard Library / Maximum, p.PDF 6466–6466]. Maximum define máximo do PSAR; proposta de experimento deve registrar configuração e contexto antes de InitIndicators, sem ativação de trailing no Stoikus.

## REF-3668 — InitIndicators

[REF, Standard Library / InitIndicators, p.PDF 6467–6467]. InitIndicators cria dependências na coleção de indicadores/séries do CExpert; false impede tratar trailing como pronto.

## REF-3669 — CheckTrailingStopLong

[REF, Standard Library / CheckTrailingStopLong, p.PDF 6468–6468]. Trailing PSAR long usa valor do candle completo anterior, só sugere SL melhor que base e dentro da distância permitida.

## REF-3670 — CheckTrailingStopShort

[REF, Standard Library / CheckTrailingStopShort, p.PDF 6469–6469]. Trailing PSAR short usa candle completo anterior e condição simétrica de melhoria e limite.

## REF-3671 — Money Management Classes

[REF, Standard Library / Money Management Classes, p.PDF 6470–6492]. Money separa lote fixo, margem fixa, risco fixo, mínimo e tamanho condicionado ao histórico; são políticas diferentes e não equivalentes ao orçamento JPW.

## REF-3672 — CMoneyFixedLot

[REF, Standard Library / CMoneyFixedLot, p.PDF 6471–6476]. FixedLot usa volume constante validado por faixa e passo; risco muda conforme instrumento e stop.

## REF-3673 — Lots

[REF, Standard Library / Lots, p.PDF 6473–6473]. Lots fixa volume em lotes; valor constante não mantém risco constante entre instrumentos e stops.

## REF-3674 — ValidationSettings

[REF, Standard Library / ValidationSettings, p.PDF 6474–6474]. Validação do lote fixo verifica mínimo/máximo e múltiplo do passo; não é validação de perda máxima.

## REF-3675 — CheckOpenLong

[REF, Standard Library / CheckOpenLong, p.PDF 6475–6475]. Lote long fixo é retornado sem usar risco do SL como dimensionamento.

## REF-3676 — CheckOpenShort

[REF, Standard Library / CheckOpenShort, p.PDF 6476–6476]. Lote short fixo é retornado; distinguir de FixedRisk.

## REF-3677 — CMoneyFixedMargin

[REF, Standard Library / CMoneyFixedMargin, p.PDF 6477–6479]. FixedMargin calcula volume por margem percentual; não equivale a percentual de perda.

## REF-3678 — CheckOpenLong

[REF, Standard Library / CheckOpenLong, p.PDF 6478–6478]. FixedMargin long usa percentual da base como margem predefinida; margem não é perda no SL.

## REF-3679 — CheckOpenShort

[REF, Standard Library / CheckOpenShort, p.PDF 6479–6479]. FixedMargin short retorna volume por margem e Percent; não impor interpretação de risco monetário.

## REF-3680 — CMoneyFixedRisk

[REF, Standard Library / CMoneyFixedRisk, p.PDF 6480–6482]. FixedRisk calcula por percentual de risco; não demonstra equivalência aos cálculos Stoikus e custos precisam auditoria.

## REF-3681 — CheckOpenLong

[REF, Standard Library / CheckOpenLong, p.PDF 6481–6481]. FixedRisk long dimensiona volume pelo risco percentual predefinido; fórmula e custos precisam validação separada antes de proposta JPW.

## REF-3682 — CheckOpenShort

[REF, Standard Library / CheckOpenShort, p.PDF 6482–6482]. FixedRisk short usa risco percentual predefinido; não prova equivalência ao cálculo Stoikus.

## REF-3683 — CMoneyNone

[REF, Standard Library / CMoneyNone, p.PDF 6483–6486]. MoneyNone usa lote mínimo e validação permissiva; o nome não significa ausência de exposição.

## REF-3684 — ValidationSettings

[REF, Standard Library / ValidationSettings, p.PDF 6484–6484]. MoneyNone valida sempre true; não significa risco aceitável.

## REF-3685 — CheckOpenLong

[REF, Standard Library / CheckOpenLong, p.PDF 6485–6485]. MoneyNone long usa lote mínimo permitido, ainda com exposição financeira.

## REF-3686 — CheckOpenShort

[REF, Standard Library / CheckOpenShort, p.PDF 6486–6486]. MoneyNone short usa lote mínimo, sem orçamento monetário.

## REF-3687 — CMoneySizeOptimized

[REF, Standard Library / CMoneySizeOptimized, p.PDF 6487–6492]. SizeOptimized ajusta lote pelos negócios anteriores e fator de redução após perdas; mecanismo depende de janela histórica e exige pesquisa independente.

## REF-3688 — DecreaseFactor

[REF, Standard Library / DecreaseFactor, p.PDF 6489–6489]. DecreaseFactor reduz volume após perdas consecutivas; é mecanismo adaptativo e não regra aprovada JPW.

## REF-3689 — ValidationSettings

[REF, Standard Library / ValidationSettings, p.PDF 6490–6490]. Validação rejeita fator negativo; zero é permitido pela descrição.

## REF-3690 — CheckOpenLong

[REF, Standard Library / CheckOpenLong, p.PDF 6491–6491]. SizeOptimized long considera negócios anteriores; histórico parcial pode afetar dimensionamento.

## REF-3691 — CheckOpenShort

[REF, Standard Library / CheckOpenShort, p.PDF 6492–6492]. SizeOptimized short considera negócios anteriores, apesar de retorno textual dizer long; verificar fonte antes de implementar.

## REF-3692 — Panels and Dialogs

[REF, Standard Library / Panels and Dialogs, p.PDF 6493–6659]. Controls em MQL5\Include\Controls reúne geometria, data/hora, controles e diálogos; possível referência para UI futura, sem prova visual.

## REF-3693 — CRect

[REF, Standard Library / CRect, p.PDF 6495–6506]. CRect representa retângulo por cantos cartesianos; oferece deslocamento absoluto/relativo e contenção inclusiva nas bordas.

## REF-3694 — Left

[REF, Standard Library / Left, p.PDF 6496–6496]. Left consulta/define X do canto superior esquerdo. Aplicação proposta: geometria de painel deve ter contexto de coordenadas explícito; retorno/assinatura documentais precisam cabeçalho instalado quando divergirem, sem inferir renderização.

## REF-3695 — Top

[REF, Standard Library / Top, p.PDF 6497–6497]. Top consulta/define Y do canto superior esquerdo. Aplicação proposta: geometria de painel deve ter contexto de coordenadas explícito; retorno/assinatura documentais precisam cabeçalho instalado quando divergirem, sem inferir renderização.

## REF-3696 — Right

[REF, Standard Library / Right, p.PDF 6498–6498]. Right consulta/define X do canto inferior direito. Aplicação proposta: geometria de painel deve ter contexto de coordenadas explícito; retorno/assinatura documentais precisam cabeçalho instalado quando divergirem, sem inferir renderização.

## REF-3697 — Bottom

[REF, Standard Library / Bottom, p.PDF 6499–6499]. Bottom consulta/define Y do canto inferior direito. Aplicação proposta: geometria de painel deve ter contexto de coordenadas explícito; retorno/assinatura documentais precisam cabeçalho instalado quando divergirem, sem inferir renderização.

## REF-3698 — Width

[REF, Standard Library / Width, p.PDF 6500–6500]. Width consulta/define largura. Aplicação proposta: geometria de painel deve ter contexto de coordenadas explícito; retorno/assinatura documentais precisam cabeçalho instalado quando divergirem, sem inferir renderização.

## REF-3699 — Height

[REF, Standard Library / Height, p.PDF 6501–6501]. Height consulta/define altura. Aplicação proposta: geometria de painel deve ter contexto de coordenadas explícito; retorno/assinatura documentais precisam cabeçalho instalado quando divergirem, sem inferir renderização.

## REF-3700 — SetBound

[REF, Standard Library / SetBound, p.PDF 6502–6502]. SetBound define limites por outro CRect ou quatro coordenadas. Aplicação proposta: geometria de painel deve ter contexto de coordenadas explícito; retorno/assinatura documentais precisam cabeçalho instalado quando divergirem, sem inferir renderização.

## REF-3701 — Move

[REF, Standard Library / Move, p.PDF 6503–6503]. Move desloca para coordenadas absolutas. Aplicação proposta: geometria de painel deve ter contexto de coordenadas explícito; retorno/assinatura documentais precisam cabeçalho instalado quando divergirem, sem inferir renderização.

## REF-3702 — Shift

[REF, Standard Library / Shift, p.PDF 6504–6504]. Shift aplica delta relativo de X/Y. Aplicação proposta: geometria de painel deve ter contexto de coordenadas explícito; retorno/assinatura documentais precisam cabeçalho instalado quando divergirem, sem inferir renderização.

## REF-3703 — Contains

[REF, Standard Library / Contains, p.PDF 6505–6505]. CRect::Contains inclui bordas na área; definir expectativa de hit-test nos limites.

## REF-3704 — Format

[REF, Standard Library / Format, p.PDF 6506–6506]. Format formata coordenadas com string de formato. Aplicação proposta: geometria de painel deve ter contexto de coordenadas explícito; retorno/assinatura documentais precisam cabeçalho instalado quando divergirem, sem inferir renderização.

## REF-3705 — CDateTime

[REF, Standard Library / CDateTime, p.PDF 6507–6534]. CDateTime estende MqlDateTime para nomes, componentes e aritmética calendário; não fornece calendário de pregões ou política de fuso.

## REF-3706 — MonthName

[REF, Standard Library / MonthName, p.PDF 6509–6509]. MonthName retorna nome de mês, com índice 1–12. Proposta: usar apenas na apresentação, mantendo timestamp numérico como evidência.

## REF-3707 — ShortMonthName

[REF, Standard Library / ShortMonthName, p.PDF 6510–6510]. ShortMonthName retorna nome abreviado de mês, com índice 1–12. Proposta: usar apenas na apresentação, mantendo timestamp numérico como evidência.

## REF-3708 — DayName

[REF, Standard Library / DayName, p.PDF 6511–6511]. DayName retorna nome de dia da semana, com índice 0–6. Proposta: usar apenas na apresentação, mantendo timestamp numérico como evidência.

## REF-3709 — ShortDayName

[REF, Standard Library / ShortDayName, p.PDF 6512–6512]. ShortDayName retorna nome abreviado de dia da semana, com índice 0–6. Proposta: usar apenas na apresentação, mantendo timestamp numérico como evidência.

## REF-3710 — DaysInMonth

[REF, Standard Library / DaysInMonth, p.PDF 6513–6513]. DaysInMonth fornece duração do mês no objeto; não inferir dias úteis ou pregões.

## REF-3711 — DateTime

[REF, Standard Library / DateTime, p.PDF 6514–6514]. DateTime converte consulta/definição de data e hora com datetime ou MqlDateTime. Proposta: explicitar fuso/origem do valor, não inferidos pela estrutura.

## REF-3712 — Date

[REF, Standard Library / Date, p.PDF 6515–6515]. Date define somente componente de data com datetime ou MqlDateTime. Proposta: explicitar fuso/origem do valor, não inferidos pela estrutura.

## REF-3713 — Time

[REF, Standard Library / Time, p.PDF 6516–6516]. Time define componente de hora com datetime ou MqlDateTime. Proposta: explicitar fuso/origem do valor, não inferidos pela estrutura.

## REF-3714 — Sec

[REF, Standard Library / Sec, p.PDF 6517–6517]. Sec define segundos do objeto CDateTime sem retorno. Proposta: validar conjunto calendário e limites do período financeiro antes de uso.

## REF-3715 — Min

[REF, Standard Library / Min, p.PDF 6518–6518]. Min define minutos do objeto CDateTime sem retorno. Proposta: validar conjunto calendário e limites do período financeiro antes de uso.

## REF-3716 — Hour

[REF, Standard Library / Hour, p.PDF 6519–6519]. Hour define hora do objeto CDateTime sem retorno. Proposta: validar conjunto calendário e limites do período financeiro antes de uso.

## REF-3717 — Day

[REF, Standard Library / Day, p.PDF 6520–6520]. Day define dia do mês do objeto CDateTime sem retorno. Proposta: validar conjunto calendário e limites do período financeiro antes de uso.

## REF-3718 — Mon

[REF, Standard Library / Mon, p.PDF 6521–6521]. Mon define mês do objeto CDateTime sem retorno. Proposta: validar conjunto calendário e limites do período financeiro antes de uso.

## REF-3719 — Year

[REF, Standard Library / Year, p.PDF 6522–6522]. Year define ano do objeto CDateTime sem retorno. Proposta: validar conjunto calendário e limites do período financeiro antes de uso.

## REF-3720 — SecDec

[REF, Standard Library / SecDec, p.PDF 6523–6523]. SecDec subtrai quantidade da unidade Sec, padrão delta=1. Proposta: testar virada de mês/ano em adaptação futura; esta leitura não executou aritmética.

## REF-3721 — SecInc

[REF, Standard Library / SecInc, p.PDF 6524–6524]. SecInc soma quantidade da unidade Sec, padrão delta=1. Proposta: testar virada de mês/ano em adaptação futura; esta leitura não executou aritmética.

## REF-3722 — MinDec

[REF, Standard Library / MinDec, p.PDF 6525–6525]. MinDec subtrai quantidade da unidade Min, padrão delta=1. Proposta: testar virada de mês/ano em adaptação futura; esta leitura não executou aritmética.

## REF-3723 — MinInc

[REF, Standard Library / MinInc, p.PDF 6526–6526]. MinInc soma quantidade da unidade Min, padrão delta=1. Proposta: testar virada de mês/ano em adaptação futura; esta leitura não executou aritmética.

## REF-3724 — HourDec

[REF, Standard Library / HourDec, p.PDF 6527–6527]. HourDec subtrai quantidade da unidade Hour, padrão delta=1. Proposta: testar virada de mês/ano em adaptação futura; esta leitura não executou aritmética.

## REF-3725 — HourInc

[REF, Standard Library / HourInc, p.PDF 6528–6528]. HourInc soma quantidade da unidade Hour, padrão delta=1. Proposta: testar virada de mês/ano em adaptação futura; esta leitura não executou aritmética.

## REF-3726 — DayDec

[REF, Standard Library / DayDec, p.PDF 6529–6529]. DayDec subtrai quantidade da unidade Day, padrão delta=1. Proposta: testar virada de mês/ano em adaptação futura; esta leitura não executou aritmética.

## REF-3727 — DayInc

[REF, Standard Library / DayInc, p.PDF 6530–6530]. DayInc soma quantidade da unidade Day, padrão delta=1. Proposta: testar virada de mês/ano em adaptação futura; esta leitura não executou aritmética.

## REF-3728 — MonDec

[REF, Standard Library / MonDec, p.PDF 6531–6531]. MonDec subtrai quantidade da unidade Mon, padrão delta=1. Proposta: testar virada de mês/ano em adaptação futura; esta leitura não executou aritmética.

## REF-3729 — MonInc

[REF, Standard Library / MonInc, p.PDF 6532–6532]. MonInc soma quantidade da unidade Mon, padrão delta=1. Proposta: testar virada de mês/ano em adaptação futura; esta leitura não executou aritmética.

## REF-3730 — YearDec

[REF, Standard Library / YearDec, p.PDF 6533–6533]. YearDec subtrai quantidade da unidade Year, padrão delta=1. Proposta: testar virada de mês/ano em adaptação futura; esta leitura não executou aritmética.

## REF-3731 — YearInc

[REF, Standard Library / YearInc, p.PDF 6534–6534]. YearInc soma quantidade da unidade Year, padrão delta=1. Proposta: testar virada de mês/ano em adaptação futura; esta leitura não executou aritmética.

## REF-3732 — CWnd

[REF, Standard Library / CWnd, p.PDF 6535–6599]. CWnd fornece geometria, estado e eventos básicos. Enable, Visible e Active são estados distintos; base não tem coleção real nem cria objeto gráfico por si.

## REF-3733 — Create

[REF, Standard Library / Create, p.PDF 6539–6539]. CWnd::Create base apenas salva parâmetros e retorna true; isto não comprova objeto gráfico criado.

## REF-3734 — Destroy

[REF, Standard Library / Destroy, p.PDF 6540–6540]. Destroy encerra controle ou todos filhos no container; bool precisa tratamento. Proposta: limpar UI sem tocar posições ou estado financeiro.

## REF-3735 — OnEvent

[REF, Standard Library / OnEvent, p.PDF 6541–6541]. OnEvent encaminha/processa evento gráfico id/long/double/string; bool informa processamento. Proposta: rotear para instância/filhos corretos sem operações de mercado.

## REF-3736 — OnMouseEvent

[REF, Standard Library / OnMouseEvent, p.PDF 6542–6542]. OnMouseEvent encaminha/processa movimento do mouse X/Y e flags de botões; bool informa processamento. Proposta: rotear para instância/filhos corretos sem operações de mercado.

## REF-3737 — Name

[REF, Standard Library / Name, p.PDF 6543–6543]. Name consulta nome do controle; criação exige nome único. Proposta: namespace por painel para evitar colisões.

## REF-3738 — ControlsTotal

[REF, Standard Library / ControlsTotal, p.PDF 6544–6544]. ControlsTotal da base CWnd sempre zero; coleção efetiva pertence a descendente.

## REF-3739 — Control

[REF, Standard Library / Control, p.PDF 6545–6545]. Control da base CWnd sempre NULL; validar ponteiro antes de usar.

## REF-3740 — ControlFind

[REF, Standard Library / ControlFind, p.PDF 6546–6546]. ControlFind da base retorna this se ID coincide, sem coleção; busca por ID exige conhecer tipo concreto.

## REF-3741 — Rect

[REF, Standard Library / Rect, p.PDF 6547–6547]. Rect retorna ponteiro constante para retângulo. Aplicação proposta: geometria de painel deve ter contexto de coordenadas explícito; retorno/assinatura documentais precisam cabeçalho instalado quando divergirem, sem inferir renderização.

## REF-3742 — Left

[REF, Standard Library / Left, p.PDF 6548–6548]. Left consulta/define X do canto superior esquerdo. Aplicação proposta: geometria de painel deve ter contexto de coordenadas explícito; retorno/assinatura documentais precisam cabeçalho instalado quando divergirem, sem inferir renderização.

## REF-3743 — Top

[REF, Standard Library / Top, p.PDF 6549–6549]. Top consulta/define Y do canto superior esquerdo. Aplicação proposta: geometria de painel deve ter contexto de coordenadas explícito; retorno/assinatura documentais precisam cabeçalho instalado quando divergirem, sem inferir renderização.

## REF-3744 — Right

[REF, Standard Library / Right, p.PDF 6550–6550]. Right consulta/define X do canto inferior direito. Aplicação proposta: geometria de painel deve ter contexto de coordenadas explícito; retorno/assinatura documentais precisam cabeçalho instalado quando divergirem, sem inferir renderização.

## REF-3745 — Bottom

[REF, Standard Library / Bottom, p.PDF 6551–6551]. Bottom consulta/define Y do canto inferior direito. Aplicação proposta: geometria de painel deve ter contexto de coordenadas explícito; retorno/assinatura documentais precisam cabeçalho instalado quando divergirem, sem inferir renderização.

## REF-3746 — Width

[REF, Standard Library / Width, p.PDF 6552–6552]. Width consulta/define largura. Aplicação proposta: geometria de painel deve ter contexto de coordenadas explícito; retorno/assinatura documentais precisam cabeçalho instalado quando divergirem, sem inferir renderização.

## REF-3747 — Height

[REF, Standard Library / Height, p.PDF 6553–6553]. Height consulta/define altura. Aplicação proposta: geometria de painel deve ter contexto de coordenadas explícito; retorno/assinatura documentais precisam cabeçalho instalado quando divergirem, sem inferir renderização.

## REF-3748 — Move

[REF, Standard Library / Move, p.PDF 6554–6554]. Move desloca para coordenadas absolutas. Aplicação proposta: geometria de painel deve ter contexto de coordenadas explícito; retorno/assinatura documentais precisam cabeçalho instalado quando divergirem, sem inferir renderização.

## REF-3749 — Shift

[REF, Standard Library / Shift, p.PDF 6555–6555]. Shift aplica delta relativo de X/Y. Aplicação proposta: geometria de painel deve ter contexto de coordenadas explícito; retorno/assinatura documentais precisam cabeçalho instalado quando divergirem, sem inferir renderização.

## REF-3750 — Resize

[REF, Standard Library / Resize, p.PDF 6556–6556]. Resize altera largura e altura. Aplicação proposta: geometria de painel deve ter contexto de coordenadas explícito; retorno/assinatura documentais precisam cabeçalho instalado quando divergirem, sem inferir renderização.

## REF-3751 — Contains

[REF, Standard Library / Contains, p.PDF 6557–6557]. Contains admite ponto ou outro controle e inclui bordas; não testa disponibilidade para ação.

## REF-3752 — Alignment

[REF, Standard Library / Alignment, p.PDF 6558–6558]. Alignment combina lados em flags; WIDTH=LEFT|RIGHT, HEIGHT=TOP|BOTTOM, CLIENT ambos. Offsets são fixos.

## REF-3753 — Align

[REF, Standard Library / Align, p.PDF 6559–6559]. Align aplica parâmetros previamente definidos; padrão é nenhum alinhamento.

## REF-3754 — Id

[REF, Standard Library / Id, p.PDF 6560–6560]. Id consulta/define identificador long do controle; não confundir com ticket ou magic financeiro.

## REF-3755 — IsEnabled

[REF, Standard Library / IsEnabled, p.PDF 6561–6561]. IsEnabled consulta/altera capacidade de interação do controle. Proposta: estes estados UI não armam Supervisor nem autorizam negociação.

## REF-3756 — Enable

[REF, Standard Library / Enable, p.PDF 6562–6562]. Enable permite processar eventos externos; não autoriza negociação nem arma Supervisor.

## REF-3757 — Disable

[REF, Standard Library / Disable, p.PDF 6563–6563]. Disable impede eventos externos no controle; não é bloqueio transacional do motor.

## REF-3758 — IsVisible

[REF, Standard Library / IsVisible, p.PDF 6564–6564]. IsVisible consulta/altera visibilidade do controle. Proposta: estes estados UI não armam Supervisor nem autorizam negociação.

## REF-3759 — Visible

[REF, Standard Library / Visible, p.PDF 6565–6565]. Visible consulta/altera visibilidade do controle. Proposta: estes estados UI não armam Supervisor nem autorizam negociação.

## REF-3760 — Show

[REF, Standard Library / Show, p.PDF 6566–6566]. Show consulta/altera visibilidade do controle. Proposta: estes estados UI não armam Supervisor nem autorizam negociação.

## REF-3761 — Hide

[REF, Standard Library / Hide, p.PDF 6567–6567]. Hide consulta/altera visibilidade do controle. Proposta: estes estados UI não armam Supervisor nem autorizam negociação.

## REF-3762 — IsActive

[REF, Standard Library / IsActive, p.PDF 6568–6568]. IsActive consulta/altera atividade sob cursor do controle. Proposta: estes estados UI não armam Supervisor nem autorizam negociação.

## REF-3763 — Activate

[REF, Standard Library / Activate, p.PDF 6569–6569]. Activate representa cursor sobre controle; estado UI não indica autorização operacional.

## REF-3764 — Deactivate

[REF, Standard Library / Deactivate, p.PDF 6570–6570]. Deactivate representa cursor fora; não cancela ordem ou regra.

## REF-3765 — StateFlags

[REF, Standard Library / StateFlags, p.PDF 6571–6571]. StateFlags substitui/consulta máscara de estado/propriedades do controle. Proposta: preservar bits independentes; flags UI não representam estado transacional.

## REF-3766 — StateFlagsSet

[REF, Standard Library / StateFlagsSet, p.PDF 6572–6572]. StateFlagsSet adiciona bits a máscara de estado/propriedades do controle. Proposta: preservar bits independentes; flags UI não representam estado transacional.

## REF-3767 — StateFlagsReset

[REF, Standard Library / StateFlagsReset, p.PDF 6573–6573]. StateFlagsReset limpa bits de máscara de estado/propriedades do controle. Proposta: preservar bits independentes; flags UI não representam estado transacional.

## REF-3768 — PropFlags

[REF, Standard Library / PropFlags, p.PDF 6574–6574]. PropFlags getter está impresso como void com argumento; conferir assinatura instalada em vez de copiar.

## REF-3769 — PropFlagsSet

[REF, Standard Library / PropFlagsSet, p.PDF 6575–6575]. PropFlagsSet adiciona bits a máscara de estado/propriedades do controle. Proposta: preservar bits independentes; flags UI não representam estado transacional.

## REF-3770 — PropFlagsReset

[REF, Standard Library / PropFlagsReset, p.PDF 6576–6576]. PropFlagsReset limpa bits de máscara de estado/propriedades do controle. Proposta: preservar bits independentes; flags UI não representam estado transacional.

## REF-3771 — MouseX

[REF, Standard Library / MouseX, p.PDF 6577–6577]. MouseX salva/consulta coordenada X do mouse. Proposta: limpar foco ao transitar de controle e manter coordenadas separadas de preços.

## REF-3772 — MouseY

[REF, Standard Library / MouseY, p.PDF 6578–6578]. MouseY salva/consulta coordenada Y do mouse. Proposta: limpar foco ao transitar de controle e manter coordenadas separadas de preços.

## REF-3773 — MouseFlags

[REF, Standard Library / MouseFlags, p.PDF 6579–6579]. MouseFlags salva/consulta estado dos botões do mouse. Proposta: limpar foco ao transitar de controle e manter coordenadas separadas de preços.

## REF-3774 — MouseFocusKill

[REF, Standard Library / MouseFocusKill, p.PDF 6580–6580]. MouseFocusKill limpa botões salvos e desativa controle; ID informa quem ganhou foco.

## REF-3775 — OnCreate

[REF, Standard Library / OnCreate, p.PDF 6581–6581]. OnCreate é callback virtual interno do estado/ação correspondente; base não faz nada e retorna true. Proposta: implementar efeito necessário explicitamente; sucesso do stub não valida UI.

## REF-3776 — OnDestroy

[REF, Standard Library / OnDestroy, p.PDF 6582–6582]. OnDestroy é callback virtual interno do estado/ação correspondente; base não faz nada e retorna true. Proposta: implementar efeito necessário explicitamente; sucesso do stub não valida UI.

## REF-3777 — OnMove

[REF, Standard Library / OnMove, p.PDF 6583–6583]. OnMove é callback virtual interno do estado/ação correspondente; base não faz nada e retorna true. Proposta: implementar efeito necessário explicitamente; sucesso do stub não valida UI.

## REF-3778 — OnResize

[REF, Standard Library / OnResize, p.PDF 6584–6584]. OnResize é callback virtual interno do estado/ação correspondente; base não faz nada e retorna true. Proposta: implementar efeito necessário explicitamente; sucesso do stub não valida UI.

## REF-3779 — OnEnable

[REF, Standard Library / OnEnable, p.PDF 6585–6585]. OnEnable é callback virtual interno do estado/ação correspondente; base não faz nada e retorna true. Proposta: implementar efeito necessário explicitamente; sucesso do stub não valida UI.

## REF-3780 — OnDisable

[REF, Standard Library / OnDisable, p.PDF 6586–6586]. OnDisable é callback virtual interno do estado/ação correspondente; base não faz nada e retorna true. Proposta: implementar efeito necessário explicitamente; sucesso do stub não valida UI.

## REF-3781 — OnShow

[REF, Standard Library / OnShow, p.PDF 6587–6587]. OnShow é callback virtual interno do estado/ação correspondente; base não faz nada e retorna true. Proposta: implementar efeito necessário explicitamente; sucesso do stub não valida UI.

## REF-3782 — OnHide

[REF, Standard Library / OnHide, p.PDF 6588–6588]. OnHide é callback virtual interno do estado/ação correspondente; base não faz nada e retorna true. Proposta: implementar efeito necessário explicitamente; sucesso do stub não valida UI.

## REF-3783 — OnActivate

[REF, Standard Library / OnActivate, p.PDF 6589–6589]. OnActivate é callback virtual interno do estado/ação correspondente; base não faz nada e retorna true. Proposta: implementar efeito necessário explicitamente; sucesso do stub não valida UI.

## REF-3784 — OnDeactivate

[REF, Standard Library / OnDeactivate, p.PDF 6590–6590]. OnDeactivate é callback virtual interno do estado/ação correspondente; base não faz nada e retorna true. Proposta: implementar efeito necessário explicitamente; sucesso do stub não valida UI.

## REF-3785 — OnClick

[REF, Standard Library / OnClick, p.PDF 6591–6591]. OnClick é callback de clique do mouse; retorna se evento foi processado. Proposta: manter confirmação/estado operacional independentes do evento visual.

## REF-3786 — OnChange

[REF, Standard Library / OnChange, p.PDF 6592–6592]. OnChange é callback virtual interno do estado/ação correspondente; base não faz nada e retorna true. Proposta: implementar efeito necessário explicitamente; sucesso do stub não valida UI.

## REF-3787 — OnMouseDown

[REF, Standard Library / OnMouseDown, p.PDF 6593–6593]. OnMouseDown trata pressão do botão esquerdo. Aplicação proposta: geometria/foco não devem alterar autorização do monitor; retorno booleano deve ser tratado.

## REF-3788 — OnMouseUp

[REF, Standard Library / OnMouseUp, p.PDF 6594–6594]. OnMouseUp trata liberação do botão esquerdo. Aplicação proposta: geometria/foco não devem alterar autorização do monitor; retorno booleano deve ser tratado.

## REF-3789 — OnDragStart

[REF, Standard Library / OnDragStart, p.PDF 6595–6595]. OnDragStart trata início do arrasto. Aplicação proposta: geometria/foco não devem alterar autorização do monitor; retorno booleano deve ser tratado.

## REF-3790 — OnDragProcess

[REF, Standard Library / OnDragProcess, p.PDF 6596–6596]. OnDragProcess trata arrasto com coordenadas X/Y atuais. Aplicação proposta: geometria/foco não devem alterar autorização do monitor; retorno booleano deve ser tratado.

## REF-3791 — OnDragEnd

[REF, Standard Library / OnDragEnd, p.PDF 6597–6597]. OnDragEnd trata fim do arrasto. Aplicação proposta: geometria/foco não devem alterar autorização do monitor; retorno booleano deve ser tratado.

## REF-3792 — DragObjectCreate

[REF, Standard Library / DragObjectCreate, p.PDF 6598–6598]. DragObjectCreate trata criação de objeto de arrasto. Aplicação proposta: geometria/foco não devem alterar autorização do monitor; retorno booleano deve ser tratado.

## REF-3793 — DragObjectDestroy

[REF, Standard Library / DragObjectDestroy, p.PDF 6599–6599]. DragObjectDestroy trata destruição de objeto de arrasto. Aplicação proposta: geometria/foco não devem alterar autorização do monitor; retorno booleano deve ser tratado.

## REF-3794 — CWndObj

[REF, Standard Library / CWndObj, p.PDF 6600–6621]. CWndObj vincula controles simples às propriedades de objetos gráficos e eventos; getters/setters devem tratar falhas sem confundir UI com execução.

## REF-3795 — OnEvent

[REF, Standard Library / OnEvent, p.PDF 6602–6602]. OnEvent encaminha/processa evento gráfico id/long/double/string; bool informa processamento. Proposta: rotear para instância/filhos corretos sem operações de mercado.

## REF-3796 — Text

[REF, Standard Library / Text, p.PDF 6603–6603]. Text consulta/define texto OBJPROP_TEXT no objeto gráfico, setter retorna sucesso/falha. Proposta: distinguir propriedade armazenada de confirmação visual no terminal.

## REF-3797 — Color

[REF, Standard Library / Color, p.PDF 6604–6604]. Color consulta/define cor OBJPROP_COLOR no objeto gráfico, setter retorna sucesso/falha. Proposta: distinguir propriedade armazenada de confirmação visual no terminal.

## REF-3798 — ColorBackground

[REF, Standard Library / ColorBackground, p.PDF 6605–6605]. ColorBackground consulta/define fundo OBJPROP_BGCOLOR no objeto gráfico, setter retorna sucesso/falha. Proposta: distinguir propriedade armazenada de confirmação visual no terminal.

## REF-3799 — ColorBorder

[REF, Standard Library / ColorBorder, p.PDF 6606–6606]. ColorBorder consulta/define borda OBJPROP_BORDER_COLOR no objeto gráfico, setter retorna sucesso/falha. Proposta: distinguir propriedade armazenada de confirmação visual no terminal.

## REF-3800 — Font

[REF, Standard Library / Font, p.PDF 6607–6607]. Font consulta/define nome OBJPROP_FONT no objeto gráfico, setter retorna sucesso/falha. Proposta: distinguir propriedade armazenada de confirmação visual no terminal.

## REF-3801 — FontSize

[REF, Standard Library / FontSize, p.PDF 6608–6608]. FontSize consulta/define tamanho OBJPROP_FONTSIZE no objeto gráfico, setter retorna sucesso/falha. Proposta: distinguir propriedade armazenada de confirmação visual no terminal.

## REF-3802 — ZOrder

[REF, Standard Library / ZOrder, p.PDF 6609–6609]. ZOrder consulta/define prioridade OBJPROP_ZORDER no objeto gráfico, setter retorna sucesso/falha. Proposta: distinguir propriedade armazenada de confirmação visual no terminal.

## REF-3803 — OnObjectCreate

[REF, Standard Library / OnObjectCreate, p.PDF 6610–6610]. OnObjectCreate trata CHARTEVENT_OBJECT_CREATE. Proposta: mapear evento ao objeto certo e não confundir mudança/arrasto/exclusão de gráfico com ordem financeira.

## REF-3804 — OnObjectChange

[REF, Standard Library / OnObjectChange, p.PDF 6611–6611]. OnObjectChange trata CHARTEVENT_OBJECT_CHANGE. Proposta: mapear evento ao objeto certo e não confundir mudança/arrasto/exclusão de gráfico com ordem financeira.

## REF-3805 — OnObjectDelete

[REF, Standard Library / OnObjectDelete, p.PDF 6612–6612]. OnObjectDelete trata CHARTEVENT_OBJECT_DELETE. Proposta: mapear evento ao objeto certo e não confundir mudança/arrasto/exclusão de gráfico com ordem financeira.

## REF-3806 — OnObjectDrag

[REF, Standard Library / OnObjectDrag, p.PDF 6613–6613]. OnObjectDrag trata CHARTEVENT_OBJECT_DRAG. Proposta: mapear evento ao objeto certo e não confundir mudança/arrasto/exclusão de gráfico com ordem financeira.

## REF-3807 — OnSetText

[REF, Standard Library / OnSetText, p.PDF 6614–6614]. OnSetText é callback da mudança de propriedade correspondente no controle. Base CWndObj não faz nada e retorna true. Aplicação proposta: atualizar label/objeto sem acoplar ação de mercado; renderização nativa não foi verificada.

## REF-3808 — OnSetColor

[REF, Standard Library / OnSetColor, p.PDF 6615–6615]. OnSetColor é callback da mudança de propriedade correspondente no controle. Base CWndObj não faz nada e retorna true. Aplicação proposta: atualizar label/objeto sem acoplar ação de mercado; renderização nativa não foi verificada.

## REF-3809 — OnSetColorBackground

[REF, Standard Library / OnSetColorBackground, p.PDF 6616–6616]. OnSetColorBackground é callback da mudança de propriedade correspondente no controle. Base CWndObj não faz nada e retorna true. Aplicação proposta: atualizar label/objeto sem acoplar ação de mercado; renderização nativa não foi verificada.

## REF-3810 — OnSetFont

[REF, Standard Library / OnSetFont, p.PDF 6617–6617]. OnSetFont é callback da mudança de propriedade correspondente no controle. Base CWndObj não faz nada e retorna true. Aplicação proposta: atualizar label/objeto sem acoplar ação de mercado; renderização nativa não foi verificada.

## REF-3811 — OnSetFontSize

[REF, Standard Library / OnSetFontSize, p.PDF 6618–6618]. OnSetFontSize é callback da mudança de propriedade correspondente no controle. Base CWndObj não faz nada e retorna true. Aplicação proposta: atualizar label/objeto sem acoplar ação de mercado; renderização nativa não foi verificada.

## REF-3812 — OnSetZOrder

[REF, Standard Library / OnSetZOrder, p.PDF 6619–6619]. OnSetZOrder é callback da mudança de propriedade correspondente no controle. Base CWndObj não faz nada e retorna true. Aplicação proposta: atualizar label/objeto sem acoplar ação de mercado; renderização nativa não foi verificada.

## REF-3813 — OnDestroy

[REF, Standard Library / OnDestroy, p.PDF 6620–6620]. OnDestroy callback interno do controle concreto; bool informa processamento. Proposta: manter objeto gráfico e estado lógico coerentes; esta leitura não confirma aparência ou execução.

## REF-3814 — OnChange

[REF, Standard Library / OnChange, p.PDF 6621–6621]. OnChange callback interno do controle concreto; bool informa processamento. Proposta: manter objeto gráfico e estado lógico coerentes; esta leitura não confirma aparência ou execução.

## REF-3815 — CWndContainer

[REF, Standard Library / CWndContainer, p.PDF 6622–6644]. CWndContainer agrupa filhos, propaga eventos, movimento, estados e persistência; identidade consome faixa de IDs e buscas podem retornar NULL.

## REF-3816 — Destroy

[REF, Standard Library / Destroy, p.PDF 6624–6624]. Destroy encerra controle ou todos filhos no container; bool precisa tratamento. Proposta: limpar UI sem tocar posições ou estado financeiro.

## REF-3817 — OnEvent

[REF, Standard Library / OnEvent, p.PDF 6625–6625]. OnEvent encaminha/processa evento gráfico id/long/double/string; bool informa processamento. Proposta: rotear para instância/filhos corretos sem operações de mercado.

## REF-3818 — OnMouseEvent

[REF, Standard Library / OnMouseEvent, p.PDF 6626–6626]. OnMouseEvent encaminha/processa movimento do mouse X/Y e flags de botões; bool informa processamento. Proposta: rotear para instância/filhos corretos sem operações de mercado.

## REF-3819 — ControlsTotal

[REF, Standard Library / ControlsTotal, p.PDF 6627–6627]. ControlsTotal conta filhos reais do container; usar contagem com validação de ponteiros e índices.

## REF-3820 — Control

[REF, Standard Library / Control, p.PDF 6628–6628]. Control devolve ponteiro por índice e NULL se ausente; verificar limites e nulidade.

## REF-3821 — ControlFind

[REF, Standard Library / ControlFind, p.PDF 6629–6629]. ControlFind devolve ponteiro por ID ou NULL; ID deve ser único no contexto.

## REF-3822 — Add

[REF, Standard Library / Add, p.PDF 6630–6630]. Add adiciona controle por referência no grupo; retorna sucesso/falha. Proposta: preservar ciclo de vida e não inferir destruição de objeto apenas pelo nome Delete.

## REF-3823 — Delete

[REF, Standard Library / Delete, p.PDF 6631–6631]. Delete remove controle por referência no grupo; retorna sucesso/falha. Proposta: preservar ciclo de vida e não inferir destruição de objeto apenas pelo nome Delete.

## REF-3824 — Move

[REF, Standard Library / Move, p.PDF 6632–6632]. Move move todos os filhos para posição absoluta; conferir resultado e alinhamento na UI futura, sem prova visual aqui.

## REF-3825 — Shift

[REF, Standard Library / Shift, p.PDF 6633–6633]. Shift move todos os filhos por delta relativo; conferir resultado e alinhamento na UI futura, sem prova visual aqui.

## REF-3826 — Id

[REF, Standard Library / Id, p.PDF 6634–6634]. Id do container retorna quantidade de IDs consumidos a partir da base; reservar faixa evita colisão.

## REF-3827 — Enable

[REF, Standard Library / Enable, p.PDF 6635–6635]. Enable consulta/altera capacidade de interação de todos filhos no container. Proposta: estes estados UI não armam Supervisor nem autorizam negociação.

## REF-3828 — Disable

[REF, Standard Library / Disable, p.PDF 6636–6636]. Disable consulta/altera capacidade de interação de todos filhos no container. Proposta: estes estados UI não armam Supervisor nem autorizam negociação.

## REF-3829 — Show

[REF, Standard Library / Show, p.PDF 6637–6637]. Show consulta/altera visibilidade de todos filhos no container. Proposta: estes estados UI não armam Supervisor nem autorizam negociação.

## REF-3830 — Hide

[REF, Standard Library / Hide, p.PDF 6638–6638]. Hide consulta/altera visibilidade de todos filhos no container. Proposta: estes estados UI não armam Supervisor nem autorizam negociação.

## REF-3831 — MouseFocusKill

[REF, Standard Library / MouseFocusKill, p.PDF 6639–6639]. MouseFocusKill limpa estado e desativa filhos; não muda estado operacional do monitor.

## REF-3832 — Save

[REF, Standard Library / Save, p.PDF 6640–6640]. Save exige handle de arquivo binário previamente aberto para escrita; proposta de persistência precisa schema próprio.

## REF-3833 — Load

[REF, Standard Library / Load, p.PDF 6641–6641]. Load exige handle binário previamente aberto para leitura; sucesso não autentica conteúdo nem valida parâmetros financeiros.

## REF-3834 — OnResize

[REF, Standard Library / OnResize, p.PDF 6642–6642]. OnResize callback interno do container; base não faz nada e retorna true. Proposta: comportamento de layout/foco exige implementação explícita.

## REF-3835 — OnActivate

[REF, Standard Library / OnActivate, p.PDF 6643–6643]. OnActivate callback interno do container; base não faz nada e retorna true. Proposta: comportamento de layout/foco exige implementação explícita.

## REF-3836 — OnDeactivate

[REF, Standard Library / OnDeactivate, p.PDF 6644–6644]. OnDeactivate callback interno do container; base não faz nada e retorna true. Proposta: comportamento de layout/foco exige implementação explícita.

## REF-3837 — CLabel

[REF, Standard Library / CLabel, p.PDF 6645–6658]. CLabel cria texto não editável. Exemplo cria label, define texto, adiciona ao diálogo, Run no OnInit, Destroy no OnDeinit e encaminha ChartEvent; reprodução visual não foi examinada.

## REF-3838 — Create

[REF, Standard Library / Create, p.PDF 6650–6650]. CLabel::Create recebe gráfico, nome único, subjanela e cantos em pixels; retorna sucesso. Proposta: rótulo somente leitura para diagnóstico, com QA visual ainda pendente.

## REF-3839 — OnSetText

[REF, Standard Library / OnSetText, p.PDF 6651–6651]. OnSetText é callback da mudança de propriedade correspondente no controle. Aplicação proposta: atualizar label/objeto sem acoplar ação de mercado; renderização nativa não foi verificada.

## REF-3840 — OnSetColor

[REF, Standard Library / OnSetColor, p.PDF 6652–6652]. OnSetColor é callback da mudança de propriedade correspondente no controle. Aplicação proposta: atualizar label/objeto sem acoplar ação de mercado; renderização nativa não foi verificada.

## REF-3841 — OnSetFont

[REF, Standard Library / OnSetFont, p.PDF 6653–6653]. OnSetFont é callback da mudança de propriedade correspondente no controle. Aplicação proposta: atualizar label/objeto sem acoplar ação de mercado; renderização nativa não foi verificada.

## REF-3842 — OnSetFontSize

[REF, Standard Library / OnSetFontSize, p.PDF 6654–6654]. OnSetFontSize é callback da mudança de propriedade correspondente no controle. Aplicação proposta: atualizar label/objeto sem acoplar ação de mercado; renderização nativa não foi verificada.

## REF-3843 — OnCreate

[REF, Standard Library / OnCreate, p.PDF 6655–6655]. OnCreate callback interno do controle concreto; bool informa processamento. Proposta: manter objeto gráfico e estado lógico coerentes; esta leitura não confirma aparência ou execução.

## REF-3844 — OnShow

[REF, Standard Library / OnShow, p.PDF 6656–6656]. OnShow callback interno do controle concreto; bool informa processamento. Proposta: manter objeto gráfico e estado lógico coerentes; esta leitura não confirma aparência ou execução.

## REF-3845 — OnHide

[REF, Standard Library / OnHide, p.PDF 6657–6657]. OnHide callback interno do controle concreto; bool informa processamento. Proposta: manter objeto gráfico e estado lógico coerentes; esta leitura não confirma aparência ou execução.

## REF-3846 — OnMove

[REF, Standard Library / OnMove, p.PDF 6658–6658]. OnMove callback interno do controle concreto; bool informa processamento. Proposta: manter objeto gráfico e estado lógico coerentes; esta leitura não confirma aparência ou execução.

## REF-3847 — CBmpButton

[REF, Standard Library / CBmpButton, p.PDF 6659–6659]. CBmpButton usa Bitmap label para botão com imagem; somente página inicial 6659 lida neste lote. Implementação e métodos nas páginas posteriores ficam fora do escopo.
