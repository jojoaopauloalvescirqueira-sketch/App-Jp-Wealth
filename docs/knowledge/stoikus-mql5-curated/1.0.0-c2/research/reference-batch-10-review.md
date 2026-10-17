# REF — lote 10, entrega parcial honesta

Leitura semântica real do texto integral extraído de **PDF2941–3042 (102 páginas)** em oito respostas sequenciais, cada uma <=30.000 caracteres e max_output_tokens20000, sem truncamento. A preparação de arquivos para PDF3043–3238 não é leitura. **Restam PDF3043–3238 (196 páginas)**. Motivo: preservação de evidência e limite de contexto para leitura integral de 298 páginas nesta execução. Nenhuma parte restante é promovida a leitura pelo catálogo.

Livro MetaQuotes MQL5 Language REFERENCE, PDF7284p. Hash original PDF `9ae05ce748d23ce0de9b230fc6c7093a2af0adc3ce3544244a74e1c7d628d499`. Ledger adjacente registra hashes textuais originais e recalculados, linhas JSONL e faixas. Páginas físicas e número impresso coincidem nos cabeçalhos observados deste intervalo, sem auditoria visual. Linhas longas de código estão lateralmente cortadas na extração; não se inventaram complementos. Imagens, layout e execução nativa não conferidos. Todos os exemplos **MQL_NOT_RUN**. Sem mudanças em produto, Git, manual ou harness.

Aplicações abaixo são inferências de projeto a partir do BRIEF (Monitor orientado a eventos, sem negociação), não prova de APIs usadas atualmente. Indicadores não passam a compor regra financeira JPW por existirem na plataforma.

## Achados materiais

- Getters de objeto sincronizam fila do chart: evitar polling redundante de muitos objetos em callbacks sensíveis a latência. Sobrecargas bool+out permitem distinguir falha de valor válido.
- Exemplos não são especificações de robustez. ObjectGetString reproduz demo de getter inteiro; iCustom demonstra fluxo que não barra handle inválido nem falha de cópia. Diversas demos CopyBuffer verificam apenas <0 e não quantidade igual à solicitada.
- Handle válido não implica dados prontos. Inicialização, BarsCalculated, cópia e publicação de snapshot são fases distintas. Cópias multibuffer exigem sucesso conjunto antes de usar sinal.
- Shifts gráficos e start_pos negativos em Alligator/AMA/Bands exigem alinhamento explícito; não representam informação futura disponível.
- Fontes em tamanho negativo seguem escala do SO; medidas reais via TextGetSize são necessárias para layout do painel.

## Notas por ID lido

### REF-0001 — MQL5 Reference · [REF, MQL5 Reference, p.PDF 2941–3042]

Contêiner global; somente PDF2941–3042 recebeu leitura semântica nesta execução. Não duplica cobertura dos descendentes.

Relevância conceitual à interface/telemetria do Monitor; uso concreto no código Stoikus não auditado. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0941 — Object Functions · [REF, Object Functions, p.PDF 2941–2967]

Trecho final de Object Functions: getters tipados, desenho de fonte/texto e dimensões. Somente PDF2941–2967 lido deste contêiner.

Relevância conceitual à interface/telemetria do Monitor; uso concreto no código Stoikus não auditado. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0954 — ObjectGetDouble · [REF, ObjectGetDouble, p.PDF 2941–2945]

Duas sobrecargas: retorno double direto ou bool com double por referência; modificador identifica nível/âncora. Chamada síncrona aguarda todos os comandos previamente enfileirados no chart. Exemplo Fibo lê LEVELVALUE, âncoras PRICE0/1, calcula min+range*value e atualiza LEVELTEXT; extremos copiados com CopySeries. Fórmula do exemplo não substitui orientação/semântica financeira de níveis.

Relevância conceitual à interface/telemetria do Monitor; uso concreto no código Stoikus não auditado. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0955 — ObjectGetInteger · [REF, ObjectGetInteger, p.PDF 2946–2948]

Retorna long para propriedades datetime/int/color/bool/char ou bool com saída long&. Modificador de nível base zero. Sincroniza fila do chart. Exemplo distingue OBJPROP_CREATETIME de OBJPROP_TIME, converte long para datetime, remove objeto após Sleep; timestamp de criação e posição temporal não são o mesmo dado.

Relevância conceitual à interface/telemetria do Monitor; uso concreto no código Stoikus não auditado. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0956 — ObjectGetString · [REF, ObjectGetString, p.PDF 2949–2951]

Retorno string direto ou bool com string&; propriedade deve pertencer a ENUM_OBJECT_PROPERTY_STRING. Sincroniza fila. Renomear objeto gera exclusão do nome antigo e criação do novo, ambos tratáveis por OnChartEvent. Exemplo impresso reutiliza ObjectGetInteger e não demonstra chamada ObjectGetString; esta discrepância foi observada no texto, sem confirmação visual.

Relevância conceitual à interface/telemetria do Monitor; uso concreto no código Stoikus não auditado. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0957 — TextSetFont · [REF, TextSetFont, p.PDF 2952–2958]

TextSetFont padrão Arial -120; tamanho negativo em décimos de ponto lógico segue escala do SO; positivo corresponde a glyph pixels e não é recomendado junto de OBJ_LABEL. Para harmonizar com OBJ_LABEL multiplicar seu tamanho por -10. Orientação em 0,1 grau; 450 equivale45°. Fonte :: vem de recurso EX5; extensão indica arquivo; caminho absoluto relativo a MQL5 ou, de outro modo, relativo ao EX5 chamador. Retorno bool e erros4003/4001. Demo percorre nomes/estilos/pesos, atualiza recurso bitmap e restaura CHART_SHOW.

Relevância conceitual à interface/telemetria do Monitor; uso concreto no código Stoikus não auditado. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0958 — TextOut · [REF, TextOut, p.PDF 2959–2962]

TextOut grava somente uma linha em buffer uint de pixels destinado a recurso gráfico. Coordenadas são de uma das nove âncoras compostas TA_LEFT/CENTER/RIGHT e TA_TOP/VCENTER/BOTTOM, com cor/formato explícitos. Demo relógio mede texto, gira fontes, recria recurso e faz ChartRedraw em loop IsStopped com Sleep10; é script ilustrativo, não arquitetura recomendada para Monitor.

Relevância conceitual à interface/telemetria do Monitor; uso concreto no código Stoikus não auditado. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0959 — TextGetSize · [REF, TextGetSize, p.PDF 2963–2967]

TextGetSize retorna bool e largura/altura em pixels segundo fonte corrente; erro4001 possível. Exemplo separa palavras por espaço, mede espaço e cada palavra, posiciona sucessivamente por width+space_w, usa recurso bitmap e o libera. Layout depende de fonte e escala efetivas, não de número de caracteres.

Relevância conceitual à interface/telemetria do Monitor; uso concreto no código Stoikus não auditado. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0960 — Technical Indicators · [REF, Technical Indicators, p.PDF 2968–3042]

Introdução PDF2968–2970 e exemplos até3042 lidos. Funções retornam handles de instâncias no cache global; parâmetros iguais podem reutilizar cópia. Repetir mesma função/parâmetros no mesmo programa não aumenta múltiplas vezes contador. Criar em OnInit/construtor e liberar com IndicatorRelease; dados não estão imediatamente prontos. Custom pode ter512 buffers. NULL/0 selecionam símbolo/período corrente. Demonstrações aqui usam BarsCalculated, prev_calculated e CopyBuffer incremental; verificar apenas retorno<0 não demonstra cópia integral.

Proposta de pesquisa/validação de indicadores; sem adoção atual comprovada, sem sinal ou negociação autorizados. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0961 — iAC · [REF, iAC, p.PDF 2971–2975]

iAC: Accelerator, somente symbol/timeframe; contrato diz um buffer de valores, demo possui também buffer de cor e lê CopyBuffer índice1. Demo usa IND_AC ou iAC, BarsCalculated e cópia incremental, libera no OnDeinit. Distinguir número de buffers de cálculo anunciado de buffer de cor acessado no exemplo; validar nativamente antes de generalizar.

Proposta de pesquisa/validação de indicadores; sem adoção atual comprovada, sem sinal ou negociação autorizados. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0962 — iAD · [REF, iAD, p.PDF 2976–2980]

iAD: Accumulation/Distribution, um buffer, escolhe ENUM_APPLIED_VOLUME. Alternativa IndicatorCreate usa IND_AD com MqlParam TYPE_INT para volume. Demo dá INIT_FAILED para INVALID_HANDLE e libera handle; volume de ticks/real exige seleção e disponibilidade explícitas.

Proposta de pesquisa/validação de indicadores; sem adoção atual comprovada, sem sinal ou negociação autorizados. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0963 — iADX · [REF, iADX, p.PDF 2981–2985]

iADX: adx_period e três buffers0 MAIN_LINE,1 PLUSDI_LINE,2 MINUSDI_LINE. Demo mapeia três buffers e faz três CopyBuffer; falha intermediária pode deixar arrays em estágios diferentes. Proposta de snapshot só após sucesso/quantidade de todos.

Proposta de pesquisa/validação de indicadores; sem adoção atual comprovada, sem sinal ou negociação autorizados. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0964 — iADXWilder · [REF, iADXWilder, p.PDF 2986–2990]

iADXWilder mantém mesma assinatura e índices0/1/2 do ADX, mas é implementação Welles Wilder; usa IND_ADXW no caminho universal. Não assumir equivalência numérica a iADX porque nomes/assinaturas se parecem. Demo segue BarsCalculated e cópias separadas.

Proposta de pesquisa/validação de indicadores; sem adoção atual comprovada, sem sinal ou negociação autorizados. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0965 — iAlligator · [REF, iAlligator, p.PDF 2991–2997]

iAlligator recebe períodos e shifts separados para mandíbula/dentes/lábios, método MA e preço ou handle de outro indicador. Buffers0 JAW,1 TEETH,2 LIPS. Demo aplica PLOT_SHIFT e CopyBuffer com -j_shift/-t_shift/-l_shift; deslocamento gráfico e índice temporal precisam alinhar, sem inferir dado futuro.

Proposta de pesquisa/validação de indicadores; sem adoção atual comprovada, sem sinal ou negociação autorizados. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0966 — iAMA · [REF, iAMA, p.PDF 2998–3002]

iAMA: um buffer; ama_period mede coeficiente de eficiência, fast/slow períodos controlam suavização, ama_shift desloca desenho, applied_price admite handle. IndicatorCreate IND_AMA usa cinco parâmetros tipados. Demo aplica PLOT_SHIFT e CopyBuffer start=-a_shift; string de short_name contém d literal no texto extraído, indício editorial a confirmar.

Proposta de pesquisa/validação de indicadores; sem adoção atual comprovada, sem sinal ou negociação autorizados. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0967 — iAO · [REF, iAO, p.PDF 3003–3007]

iAO: Awesome Oscillator com symbol/timeframe; contrato anuncia um buffer e demo lê valores0 e cores1 em DRAW_COLOR_HISTOGRAM. IND_AO é alternativa universal. Prontidão BarsCalculated e liberação não tornam garantida cópia completa: demo testa <0 para cada CopyBuffer.

Proposta de pesquisa/validação de indicadores; sem adoção atual comprovada, sem sinal ou negociação autorizados. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0968 — iATR · [REF, iATR, p.PDF 3008–3012]

iATR: um buffer de Average True Range, ma_period de média, IND_ATR com um parâmetro TYPE_INT. Demo usa BarsCalculated, recalcula integral quando histórico muda e incremental caso contrário; volatilidade em preço não constitui valor monetário/risco JPW sem conversão e regras autorizadas.

Proposta de pesquisa/validação de indicadores; sem adoção atual comprovada, sem sinal ou negociação autorizados. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0969 — iBearsPower · [REF, iBearsPower, p.PDF 3013–3017]

iBearsPower: um buffer, ma_period, IND_BEARS com um TYPE_INT. Demo representa DRAW_HISTOGRAM e copia buffer0. A declaração da assinatura no texto apresenta vírgula antes de fechamento; não reutilizar código extraído sem conferência/compilação.

Proposta de pesquisa/validação de indicadores; sem adoção atual comprovada, sem sinal ou negociação autorizados. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0970 — iBands · [REF, iBands, p.PDF 3018–3023]

iBands: bands_period, bands_shift, deviation double, preço ou handle. Buffers do handle0 BASE_LINE,1 UPPER_BAND,2 LOWER_BAND; demo mapeia saída gráfica Upper/Lower/Middle diferentemente e passa Middle primeiro ao helper, que copia corretamente índice0. IND_BANDS tem4 parâmetros, deviation TYPE_DOUBLE. Não confundir índice do plot local com índice da fonte.

Proposta de pesquisa/validação de indicadores; sem adoção atual comprovada, sem sinal ou negociação autorizados. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0971 — iBullsPower · [REF, iBullsPower, p.PDF 3024–3028]

iBullsPower: um buffer, ma_period, caminho universal IND_BULLS e TYPE_INT. Demo copia índice0 incremental e libera. Assinatura impressa extraída contém vírgula antes do fechamento como BearsPower; leitura da fonte não comprova compilabilidade.

Proposta de pesquisa/validação de indicadores; sem adoção atual comprovada, sem sinal ou negociação autorizados. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0972 — iCCI · [REF, iCCI, p.PDF 3029–3033]

iCCI: um buffer, ma_period e preço ou handle; IND_CCI com dois TYPE_INT. Demo PRICE_TYPICAL, níveis visuais -100/+100, BarsCalculated e CopyBuffer0. Níveis do gráfico demonstrativo não são limiares de operação autorizados para Stoikus.

Proposta de pesquisa/validação de indicadores; sem adoção atual comprovada, sem sinal ou negociação autorizados. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0973 — iChaikin · [REF, iChaikin, p.PDF 3034–3038]

iChaikin: um buffer, fast/slow MA, ENUM_MA_METHOD e ENUM_APPLIED_VOLUME; IND_CHAIKIN com quatro TYPE_INT. Demo usa3/10, MODE_EMA, VOLUME_TICK; são defaults ilustrativos, não parâmetros normativos nem evidência de rentabilidade.

Proposta de pesquisa/validação de indicadores; sem adoção atual comprovada, sem sinal ou negociação autorizados. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

### REF-0974 — iCustom · [REF, iCustom, p.PDF 3039–3042]

iCustom exige EX5 e tipos/ordem exatos de inputs; ausência usa defaults. Caminho iniciado por barra reversa procura raiz MQL5; demais procuram pasta do chamador e depois MQL5/Indicators; ausência4802/INVALID_HANDLE. Separadores literais precisam escape duplo. Nome constante permite descoberta automática pelo tester; nome dinâmico/IndicatorCreate requer #property tester_indicator. Preço/handle para OnCalculate de primeira forma é último argumento após inputs. Demo retorna INIT_SUCCEEDED sem bloquear INVALID_HANDLE e retorna rates_total mesmo quando CopyBuffer falha: não copiar tratamento de falhas para produção.

Proposta de pesquisa/validação de indicadores; sem adoção atual comprovada, sem sinal ou negociação autorizados. MQL_NOT_RUN; testar erro, prontidão, quantidade copiada, alinhamento temporal e cleanup em MT5 isolado antes de alegação operacional.

## Pendência explícita

REF-0975 iDEMA em PDF3043 inicia a retomada. Todos os IDs seguintes até REF-1033 Working with databases (página3238 apenas no intervalo solicitado) constam no ledger como not_read. Não há conclusão semântica sobre indicadores posteriores, otimização, eventos, OpenCL ou bancos nesta entrega parcial.
