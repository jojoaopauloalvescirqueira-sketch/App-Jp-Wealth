# REF3431–3607 — leitura semântica complementar11b

177 páginas físicas do PDF lidas integralmente em texto extraído; lotes13–23 de /private/tmp/ref11, todos exibidos sem truncamento de ferramenta e abaixo de30k caracteres por lote. A leitura inclui código, parâmetros, avisos, resultados documentais e rodapés; extração e índice não foram usados como substituto de leitura. O ledger JSON registra a lista exata3431…3607 e hashes originais por página.

Limites: imagens, gráficos, screenshots e equações ausentes da camada textual **não foram inspecionados visualmente**. Linhas de código já cortadas horizontalmente na extração não foram reconstruídas por suposição. Exemplos Python/MQL/ONNX: **NOT_RUN**; MetaEditor/MT5/EX5/Strategy Tester: **NOT_RUN**. Resultados51,34% e pouco acima50% pertencem ao exemplo do livro, sem validação independente ou implicação de rentabilidade. Nenhum produto, manual, harness, Git ou instrução foi alterado.

A integração Python é possível plataforma, mas não habilita trading no monitor Stoikus. ONNX e todas as aplicações estatísticas abaixo são propostas de pesquisa futura, não fatos do produto nem normas JPW. A biblioteca estatística fornece funções, não evidência de que dados reais obedecem às distribuições.

## Pontos de controle para futura síntese

- Não unir ordens, negócios e posições: history_deals_get(ticket=...) filtra DEAL_ORDER; position filtra DEAL_POSITION_ID; None é erro e não conjunto vazio.
- Contrato ONNX precisa de modelo/versionamento/hash, contagem, nomes, tipos, shapes, normalização consistente, tolerância numérica e liberação de sessão em todos os caminhos. Autoconversão não controla overflow.
- O exemplo de validação deve ser revisto antes de adoção: primeira previsão, contador zero, dados incompletos, desvio zero, temporização e falhas de inferência. Acerto direcional não cobre spread, slippage, custos, risco ou vazamento temporal.
- Estatísticas amostrais devem distinguir NaN de zero, curtose em excesso de curtose bruta, domínio de parâmetros e unidades. Não completar por memória as fórmulas não extraídas.
- A fonte contém contradições editoriais: SetShape bool versus nome/NULL; OnnxTypeInfo tensor exclusivo versus mapa/sequence; MathMoments/overloads de quantis e Lognormal com assinaturas double versus bool narrado; data_count marcado out em entradas; comentário graus de liberdade na exponencial. Exigir inspeção de headers e compilação nativa antes de código utilizável.
- Histogramas são demonstrações gráficas reescaladas pelo máximo amostral/teórico, não teste formal de aderência. As repetições de CalculateHistogramArray foram lidas: guardas cells<=1, tamanho<cells*10, largura zero; bin superior limitado a cells−1. Na exponencial os pontos usam limite inferior, diferindo dos centros das demais versões.

## Registro por ID/título

Pais são contêineres: sua cobertura é somente a interseção indicada, nunca prova de leitura do restante do capítulo.

### REF-0001 — MQL5 Reference

[REF, MQL5 Reference, p.PDF 3431–3607]. Contêiner bibliográfico; somente interseção 3431–3607 lida nesta entrega, sem reivindicar o livro completo.

### REF-1083 — Python Integration

[REF, Python Integration, p.PDF 3431–3437]. Continuação da integração Python: exemplos encerram conexão com shutdown; histórico de ordens e negócios deve permanecer distinto. Proposta Stoikus: análise externa somente de leitura, sem habilitar envio de ordens.

### REF-1113 — history_orders_get

[REF, history_orders_get, p.PDF 3431–3431]. Apenas p.3431: final do exemplo converte time_setup/time_done em datetime pandas e mostra duas ordens da mesma posição. Não reivindica leitura 3429–3430 nesta entrega; pode unir ao leitor anterior.

### REF-1114 — history_deals_total

[REF, history_deals_total, p.PDF 3432–3433]. Conta negócios entre date_from/date_to (datetime ou segundos desde1970); exemplo inicializa terminal e encerra conexão. Inteiro retornado não equivale a lucro nem número de posições. Proposta: reconciliação de quantidade, sem negociação.

### REF-1115 — history_deals_get

[REF, history_deals_get, p.PDF 3434–3437]. Consulta negócios por intervalo, ticket da ordem em DEAL_ORDER ou posição em DEAL_POSITION_ID; namedtuple e None em erro com last_error. group aplica inclusão antes de exclusão sequencial, máscaras * e !. Proposta: rastreabilidade dos fills por posição, distinguindo ausência de dados de falha.

### REF-1116 — ONNX models

[REF, ONNX models, p.PDF 3438–3483]. Visão e APIs ONNX: carregar sessão, shapes, executar, liberar, inspecionar nomes/tipos. Aplicação exclusivamente proposta futura; Stoikus não usa ML conforme brief.

### REF-1117 — ONNX Support

[REF, ONNX Support, p.PDF 3439–3440]. Formato interoperável de operadores/modelos entre ferramentas e execução no terminal; alegação de desempenho e gráfico são relato da fonte, sem medição ou leitura visual deste agente.

### REF-1118 — Format Conversion

[REF, Format Conversion, p.PDF 3441–3441]. Conversão por ONNXMLTools e wrappers de Keras/TensorFlow/scikit-learn entre outros; compatibilidade e versões citadas não foram verificadas online nem instaladas. Proposta futura requer fixar ferramenta/opset/runtime.

### REF-1119 — Automatic data type conversion

[REF, Automatic data type conversion, p.PDF 3442–3445]. Autoconversão copia dados para tensores; ONNX_NO_CONVERSION usa dados sem cópia adicional. Overflow/truncamento não é controlado. color é uint e datetime long; tipos não suportados geram5802. BFLOAT16/string aparecem como não suportados nesta seção. Proposta: contrato explícito de tipos e validação de faixa.

### REF-1120 — Creating a Model

[REF, Creating a Model, p.PDF 3446–3452]. Treinar em ferramenta externa, converter, incorporar em EA; Python pode ser configurado no MetaEditor e scripts executados com F7. Exemplo projeto ONNX.Price.Prediction exige módulos e EURUSD/conexão. Nada instalado ou executado; comandos antigos são evidência documental, não receita validada.

### REF-1121 — Running a model

[REF, Running a model, p.PDF 3453–3458]. Carregar→definir shapes→OnnxRun→OnnxRelease. Exemplo normaliza OHLC10×4 por média/desvio, usa matrixf/vectorf, desnormaliza Close; teste10000 janelas relata51,34% de direção. Proposta: testar sigma zero, ausência de barras, separação temporal e custo; percentual do livro não é resultado Stoikus.

### REF-1122 — Validation in the Strategy Tester

[REF, Validation in the Strategy Tester, p.PDF 3459–3463]. Exemplo move criação para OnInit, liberação para OnDeinit, inferência para OnTick com filtro de nova barra EURUSD/H1, compara previsão anterior com Close concluído. Resultado pouco acima50% em2022 é da fonte. Revisar primeiro valor predict e divisão por zero em predictions antes de adaptar; não comprova estratégia rentável.

### REF-1123 — OnnxCreate

[REF, OnnxCreate, p.PDF 3464–3464]. OnnxCreate recebe arquivo relativo a MQL5/Files e flags; devolve handle ou INVALID_HANDLE/GetLastError; tenta extensão.onnx caso arquivo não encontrado. Proposta: hash/versionar artefato e recusar falha.

### REF-1124 — OnnxCreateFromBuffer

[REF, OnnxCreateFromBuffer, p.PDF 3465–3465]. OnnxCreateFromBuffer recebe const uchar& e flags; handle ou INVALID_HANDLE. Permite recurso incorporado em versão futura, sem provar existência de modelo no produto.

### REF-1125 — OnnxRelease

[REF, OnnxRelease, p.PDF 3466–3466]. OnnxRelease fecha sessão criada por arquivo/buffer; bool e GetLastError na falha. Proposta: liberar também em caminhos intermediários de erro.

### REF-1126 — OnnxRun

[REF, OnnxRun, p.PDF 3467–3469]. OnnxRun variádico recebe entradas/saídas conforme contrato; bool/GetLastError. Flags de log, NO_CONVERSION, COMMON_FOLDER, CPU_ONLY, CUDA0–7 e profiling; múltiplas GPUs escolhem menor índice, índice inexistente seleção automática. Não inferir GPU usada sem receipt.

### REF-1127 — OnnxGetInputCount

[REF, OnnxGetInputCount, p.PDF 3470–3470]. Conta entradas; long, -1 em erro. Proposta: validar contagem esperada antes de inferir.

### REF-1128 — OnnxGetOutputCount

[REF, OnnxGetOutputCount, p.PDF 3471–3471]. Conta saídas; long, -1 em erro. Proposta: validar contagem esperada antes de interpretar sinal.

### REF-1129 — OnnxGetInputName

[REF, OnnxGetInputName, p.PDF 3472–3472]. Nome de entrada por índice zero-based, NULL em erro; GetLastError. Proposta: fixar nome ao contrato do modelo.

### REF-1130 — OnnxGetOutputName

[REF, OnnxGetOutputName, p.PDF 3473–3473]. Nome de saída por índice zero-based, NULL em erro; GetLastError. Proposta: impedir interpretação de saída diferente após troca de modelo.

### REF-1131 — OnnxGetInputTypeInfo

[REF, OnnxGetInputTypeInfo, p.PDF 3474–3474]. Preenche OnnxTypeInfo da entrada por índice; bool/GetLastError. Proposta: confrontar tensor e dimensão com dados preparados.

### REF-1132 — OnnxGetOutputTypeInfo

[REF, OnnxGetOutputTypeInfo, p.PDF 3475–3475]. Preenche OnnxTypeInfo da saída por índice; bool/GetLastError. Proposta: recusar tipo/shape inesperado.

### REF-1133 — OnnxSetInputShape

[REF, OnnxSetInputShape, p.PDF 3476–3476]. Define shape de entrada por índice com array de dimensões; assinatura bool mas parágrafo retorno fala nome/NULL. Inconsistência editorial registrada, requer headers/build nativos antes de código.

### REF-1134 — OnnxSetOutputShape

[REF, OnnxSetOutputShape, p.PDF 3477–3477]. Define shape de saída por índice; exemplo testa !retorno e libera handle. Mesma contradição bool versus nome/NULL; não copiar prosa como contrato compilável.

### REF-1135 — Data structures

[REF, Data structures, p.PDF 3478–3483]. OnnxTypeInfo agrega tensor/map/sequence; tensor contém data_type/dimensions. Texto contradiz entrada somente tensor com frase tipos tensor/map/sequence para entrada; não resolver por inferência. Profiling grava JSON em MQL5/Files/OnnxProfileReports com tempos/provedor/nós; FP16/FP8 conversões usam ushort/uchar e formatos explícitos. Proposta: medir latência e erro numérico, não acoplar a limites financeiros.

### REF-1136 — Standard Library

[REF, Standard Library, p.PDF 3484–3607]. Biblioteca padrão reside em Include e agrupa Math, Arrays, Generic, Files, Controls, Trade etc. Somente abertura e Math/stat até3607 lidas, sem reivindicar todas as classes.

### REF-1137 — Mathematics

[REF, Mathematics, p.PDF 3485–3607]. Abertura enumera Statistics, fuzzy Mamdani/Sugeno e ALGLIB (regressão, otimização etc.). Não implica esses métodos no Stoikus; limites desta leitura não cobrem restante3935.

### REF-1138 — Statistics

[REF, Statistics, p.PDF 3486–3607]. Cinco famílias por distribuição: densidade,CDF,quantil,pseudoaleatório,momentos; overloads para arrays. Exemplo normal calcula probabilidades por diferença deCDF, intervalo por quantis e compara amostra1M com momentos. Proposta: pesquisa offline, sem mudar regras JPW.

### REF-1139 — Statistical Characteristics

[REF, Statistical Characteristics, p.PDF 3489–3497]. Características amostrais incluem média,variância,assimetria,curtose,mediana,desvio-padrão/desvio absoluto. Não assumir distribuição a partir desses números; registrar janela e observações válidas.

### REF-1140 — MathMean

[REF, MathMean, p.PDF 3490–3490]. Média de array; NaN em erro. Parâmetros narram start/count embora assinatura mostrada tenha só array. Proposta: estatística de diagnóstico com verificação de finitude.

### REF-1141 — MathVariance

[REF, MathVariance, p.PDF 3491–3491]. Variância de array, analogia var do R; NaN em erro. Convenção exata de divisor não demonstrada nesta página; verificar implementação antes de equivalência quantitativa.

### REF-1142 — MathSkewness

[REF, MathSkewness, p.PDF 3492–3492]. Assimetria (terceiro momento), analogia skewness e1071; NaN em erro. Proposta: caracterização de amostras sem converter em limite automático.

### REF-1143 — MathKurtosis

[REF, MathKurtosis, p.PDF 3493–3493]. Curtose é excesso: kurtosis−3, normal zero; NaN em erro. Proposta: relatório deve rotular excesso de curtose para evitar diferença de3.

### REF-1144 — MathMoments

[REF, MathMoments, p.PDF 3494–3494]. Calcula quatro momentos via referências e start/count; retorno narrado bool contradiz double na assinatura. Excesso de curtose confirmado. Proposta: verificar contrato nativo e todos outputs antes de aceitar.

### REF-1145 — MathMedian

[REF, MathMedian, p.PDF 3495–3495]. Mediana de array, NaN em erro. Proposta: centro robusto para diagnóstico externo, sem pressupor mudança no cálculo produtivo.

### REF-1146 — MathStandardDeviation

[REF, MathStandardDeviation, p.PDF 3496–3496]. Desvio-padrão de array, analogia sd do R, NaN em erro. Proposta: conferir unidade e janela, sem confundir com desvio absoluto.

### REF-1147 — MathAverageDeviation

[REF, MathAverageDeviation, p.PDF 3497–3497]. Desvio absoluto médio de array, analogia aad do R, NaN em erro. Proposta: comparativo de dispersão separado de desvio-padrão.

### REF-1148 — Normal Distribution

[REF, Normal Distribution, p.PDF 3498–3509]. Normal: média/desvio e overloads escalares/arrays; exemplo1M amostras,51bins, densidade teórica versus histograma reescalado por máximos. Não é teste formal de aderência nem prova de normalidade dos retornos.

### REF-1149 — MathProbabilityDensityNormal

[REF, MathProbabilityDensityNormal, p.PDF 3502–3503]. Densidade escalar ou array; log_mode devolve log natural da densidade. Escalar NaN em erro, array bool/result. Parâmetros: mu média e sigma desvio-padrão. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1150 — MathCumulativeDistributionNormal

[REF, MathCumulativeDistributionNormal, p.PDF 3504–3505]. CDF escalar/array; tail=true significa P(X<=x), log_mode calcula log da probabilidade. Escalar NaN, array false em erro. Parâmetros: mu média e sigma desvio-padrão. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1151 — MathQuantileNormal

[REF, MathQuantileNormal, p.PDF 3506–3507]. Inverte distribuição a partir de probabilidade; tail=false usa1−p, log_mode interpreta Exp(probability). Overloads escalares/arrays; algumas assinaturas array double contradizem narrativa false. Parâmetros: mu média e sigma desvio-padrão. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1152 — MathRandomNormal

[REF, MathRandomNormal, p.PDF 3508–3508]. Gera variável pseudoaleatória ou data_count valores em result; escalar NaN em erro, array false narrado. Registrar semente, parâmetros e contagem para reprodutibilidade; não usar seed GetTickCount em prova comparativa. Parâmetros: mu média e sigma desvio-padrão. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1153 — MathMomentsNormal

[REF, MathMomentsNormal, p.PDF 3509–3509]. Obtém quatro momentos teóricos via referências e error_code; sucesso narrado true/false embora assinatura double. Não confundir momentos teóricos com estimativas amostrais. Parâmetros: mu média e sigma desvio-padrão. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1154 — Log-normal distribution

[REF, Log-normal distribution, p.PDF 3510–3521]. Lognormal: parâmetros em escala log; exemplo1M/51bins e eixoY manual. Proposta futura para variáveis positivas exige validar parametrização; não concluir que retornos Stoikus seguem essa lei.

### REF-1155 — MathProbabilityDensityLognormal

[REF, MathProbabilityDensityLognormal, p.PDF 3514–3515]. Densidade escalar ou array; log_mode devolve log natural da densidade. Escalar NaN em erro, array bool/result. Parâmetros: mu/sigma no domínio log conforme nomenclatura da fonte; não são diretamente média/desvio de X. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1156 — MathCumulativeDistributionLognormal

[REF, MathCumulativeDistributionLognormal, p.PDF 3516–3517]. CDF escalar/array; tail=true significa P(X<=x), log_mode calcula log da probabilidade. Escalar NaN, array false em erro. Parâmetros: mu/sigma no domínio log conforme nomenclatura da fonte; não são diretamente média/desvio de X. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1157 — MathQuantileLognormal

[REF, MathQuantileLognormal, p.PDF 3518–3519]. Inverte distribuição a partir de probabilidade; tail=false usa1−p, log_mode interpreta Exp(probability). Overloads escalares/arrays; algumas assinaturas array double contradizem narrativa false. Parâmetros: mu/sigma no domínio log conforme nomenclatura da fonte; não são diretamente média/desvio de X. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1158 — MathRandomLognormal

[REF, MathRandomLognormal, p.PDF 3520–3520]. Gera variável pseudoaleatória ou data_count valores em result; escalar NaN em erro, array false narrado. Registrar semente, parâmetros e contagem para reprodutibilidade; não usar seed GetTickCount em prova comparativa. Parâmetros: mu/sigma no domínio log conforme nomenclatura da fonte; não são diretamente média/desvio de X. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1159 — MathMomentsLognormal

[REF, MathMomentsLognormal, p.PDF 3521–3521]. Obtém quatro momentos teóricos via referências e error_code; sucesso narrado true/false embora assinatura double. Não confundir momentos teóricos com estimativas amostrais. Parâmetros: mu/sigma no domínio log conforme nomenclatura da fonte; não são diretamente média/desvio de X. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1160 — Beta distribution

[REF, Beta distribution, p.PDF 3522–3533]. Beta: dois shapes a,b; exemplo2,5,1M amostras e51bins. Proposta pesquisa de proporções somente após justificar suporte/modelo; não é regra JPW.

### REF-1161 — MathProbabilityDensityBeta

[REF, MathProbabilityDensityBeta, p.PDF 3526–3527]. Densidade escalar ou array; log_mode devolve log natural da densidade. Escalar NaN em erro, array bool/result. Parâmetros: a,b shapes. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1162 — MathCumulativeDistributionBeta

[REF, MathCumulativeDistributionBeta, p.PDF 3528–3529]. CDF escalar/array; tail=true significa P(X<=x), log_mode calcula log da probabilidade. Escalar NaN, array false em erro. Parâmetros: a,b shapes. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1163 — MathQuantileBeta

[REF, MathQuantileBeta, p.PDF 3530–3531]. Inverte distribuição a partir de probabilidade; tail=false usa1−p, log_mode interpreta Exp(probability). Overloads escalares/arrays; algumas assinaturas array double contradizem narrativa false. Parâmetros: a,b shapes. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1164 — MathRandomBeta

[REF, MathRandomBeta, p.PDF 3532–3532]. Gera variável pseudoaleatória ou data_count valores em result; escalar NaN em erro, array false narrado. Registrar semente, parâmetros e contagem para reprodutibilidade; não usar seed GetTickCount em prova comparativa. Parâmetros: a,b shapes. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1165 — MathMomentsBeta

[REF, MathMomentsBeta, p.PDF 3533–3533]. Obtém quatro momentos teóricos via referências e error_code; sucesso narrado true/false embora assinatura double. Não confundir momentos teóricos com estimativas amostrais. Parâmetros: a,b shapes. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1166 — Noncentral beta distribution

[REF, Noncentral beta distribution, p.PDF 3534–3545]. Beta não central acrescenta lambda; exemplo2,5,1 e53bins. Proposta: cenários estatísticos externos, sem necessidade atual demonstrada no Stoikus.

### REF-1167 — MathProbabilityDensityNoncentralBeta

[REF, MathProbabilityDensityNoncentralBeta, p.PDF 3538–3539]. Densidade escalar ou array; log_mode devolve log natural da densidade. Escalar NaN em erro, array bool/result. Parâmetros: a,b shapes e lambda não central. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1168 — MathCumulativeDistributionNoncentralBeta

[REF, MathCumulativeDistributionNoncentralBeta, p.PDF 3540–3541]. CDF escalar/array; tail=true significa P(X<=x), log_mode calcula log da probabilidade. Escalar NaN, array false em erro. Parâmetros: a,b shapes e lambda não central. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1169 — MathQuantileNoncentralBeta

[REF, MathQuantileNoncentralBeta, p.PDF 3542–3543]. Inverte distribuição a partir de probabilidade; tail=false usa1−p, log_mode interpreta Exp(probability). Overloads escalares/arrays; algumas assinaturas array double contradizem narrativa false. Parâmetros: a,b shapes e lambda não central. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1170 — MathRandomNoncentralBeta

[REF, MathRandomNoncentralBeta, p.PDF 3544–3544]. Gera variável pseudoaleatória ou data_count valores em result; escalar NaN em erro, array false narrado. Registrar semente, parâmetros e contagem para reprodutibilidade; não usar seed GetTickCount em prova comparativa. Parâmetros: a,b shapes e lambda não central. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1171 — MathMomentsNoncentralBeta

[REF, MathMomentsNoncentralBeta, p.PDF 3545–3545]. Obtém quatro momentos teóricos via referências e error_code; sucesso narrado true/false embora assinatura double. Não confundir momentos teóricos com estimativas amostrais. Parâmetros: a,b shapes e lambda não central. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1172 — Gamma distribution

[REF, Gamma distribution, p.PDF 3546–3557]. Gamma usa shape/scale; exemplo9 e0,5,1M amostras. Proposta pesquisa de valores positivos/tempos com ajuste e diagnóstico; nunca substituir fórmula produtiva sem validação.

### REF-1173 — MathProbabilityDensityGamma

[REF, MathProbabilityDensityGamma, p.PDF 3550–3551]. Densidade escalar ou array; log_mode devolve log natural da densidade. Escalar NaN em erro, array bool/result. Parâmetros: a shape e b scale, não taxa. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1174 — MathCumulativeDistributionGamma

[REF, MathCumulativeDistributionGamma, p.PDF 3552–3553]. CDF escalar/array; tail=true significa P(X<=x), log_mode calcula log da probabilidade. Escalar NaN, array false em erro. Parâmetros: a shape e b scale, não taxa. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1175 — MathQuantileGamma

[REF, MathQuantileGamma, p.PDF 3554–3555]. Inverte distribuição a partir de probabilidade; tail=false usa1−p, log_mode interpreta Exp(probability). Overloads escalares/arrays; algumas assinaturas array double contradizem narrativa false. Parâmetros: a shape e b scale, não taxa. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1176 — MathRandomGamma

[REF, MathRandomGamma, p.PDF 3556–3556]. Gera variável pseudoaleatória ou data_count valores em result; escalar NaN em erro, array false narrado. Registrar semente, parâmetros e contagem para reprodutibilidade; não usar seed GetTickCount em prova comparativa. Parâmetros: a shape e b scale, não taxa. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1177 — MathMomentsGamma

[REF, MathMomentsGamma, p.PDF 3557–3557]. Obtém quatro momentos teóricos via referências e error_code; sucesso narrado true/false embora assinatura double. Não confundir momentos teóricos com estimativas amostrais. Parâmetros: a shape e b scale, não taxa. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1178 — Chi-squared distribution

[REF, Chi-squared distribution, p.PDF 3558–3569]. Qui-quadrado parametrizado por nu graus de liberdade; exemplo nu5 e1M amostras. Proposta teste estatístico offline requer hipóteses e graus de liberdade justificados.

### REF-1179 — MathProbabilityDensityChiSquare

[REF, MathProbabilityDensityChiSquare, p.PDF 3562–3563]. Densidade escalar ou array; log_mode devolve log natural da densidade. Escalar NaN em erro, array bool/result. Parâmetros: nu graus de liberdade. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1180 — MathCumulativeDistributionChiSquare

[REF, MathCumulativeDistributionChiSquare, p.PDF 3564–3565]. CDF escalar/array; tail=true significa P(X<=x), log_mode calcula log da probabilidade. Escalar NaN, array false em erro. Parâmetros: nu graus de liberdade. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1181 — MathQuantileChiSquare

[REF, MathQuantileChiSquare, p.PDF 3566–3567]. Inverte distribuição a partir de probabilidade; tail=false usa1−p, log_mode interpreta Exp(probability). Overloads escalares/arrays; algumas assinaturas array double contradizem narrativa false. Parâmetros: nu graus de liberdade. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1182 — MathRandomChiSquare

[REF, MathRandomChiSquare, p.PDF 3568–3568]. Gera variável pseudoaleatória ou data_count valores em result; escalar NaN em erro, array false narrado. Registrar semente, parâmetros e contagem para reprodutibilidade; não usar seed GetTickCount em prova comparativa. Parâmetros: nu graus de liberdade. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1183 — MathMomentsChiSquare

[REF, MathMomentsChiSquare, p.PDF 3569–3569]. Obtém quatro momentos teóricos via referências e error_code; sucesso narrado true/false embora assinatura double. Não confundir momentos teóricos com estimativas amostrais. Parâmetros: nu graus de liberdade. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1184 — Noncentral chi-squared distribution

[REF, Noncentral chi-squared distribution, p.PDF 3570–3581]. Qui-quadrado não central: nu e sigma não central; exemplo8,1 e1M amostras, eixoX manual. Proposta pesquisa de potência/cenários, sem confundir sigma com desvio.

### REF-1185 — MathProbabilityDensityNoncentralChiSquare

[REF, MathProbabilityDensityNoncentralChiSquare, p.PDF 3574–3575]. Densidade escalar ou array; log_mode devolve log natural da densidade. Escalar NaN em erro, array bool/result. Parâmetros: nu graus de liberdade e sigma parâmetro não central, não desvio-padrão. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1186 — MathCumulativeDistributionNoncentralChiSquare

[REF, MathCumulativeDistributionNoncentralChiSquare, p.PDF 3576–3577]. CDF escalar/array; tail=true significa P(X<=x), log_mode calcula log da probabilidade. Escalar NaN, array false em erro. Parâmetros: nu graus de liberdade e sigma parâmetro não central, não desvio-padrão. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1187 — MathQuantileNoncentralChiSquare

[REF, MathQuantileNoncentralChiSquare, p.PDF 3578–3579]. Inverte distribuição a partir de probabilidade; tail=false usa1−p, log_mode interpreta Exp(probability). Overloads escalares/arrays; algumas assinaturas array double contradizem narrativa false. Parâmetros: nu graus de liberdade e sigma parâmetro não central, não desvio-padrão. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1188 — MathRandomNoncentralChiSquare

[REF, MathRandomNoncentralChiSquare, p.PDF 3580–3580]. Gera variável pseudoaleatória ou data_count valores em result; escalar NaN em erro, array false narrado. Registrar semente, parâmetros e contagem para reprodutibilidade; não usar seed GetTickCount em prova comparativa. Parâmetros: nu graus de liberdade e sigma parâmetro não central, não desvio-padrão. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1189 — MathMomentsNoncentralChiSquare

[REF, MathMomentsNoncentralChiSquare, p.PDF 3581–3581]. Obtém quatro momentos teóricos via referências e error_code; sucesso narrado true/false embora assinatura double. Não confundir momentos teóricos com estimativas amostrais. Parâmetros: nu graus de liberdade e sigma parâmetro não central, não desvio-padrão. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1190 — Exponential distribution

[REF, Exponential distribution, p.PDF 3582–3593]. Exponencial usa mu esperado; exemplo1,5 tem comentário errado graus de liberdade. Histograma usa limites inferiores min+i*width apesar comentário centros. Proposta tempos de espera só com hipótese documentada, sem assumir taxa=mu.

### REF-1191 — MathProbabilityDensityExponential

[REF, MathProbabilityDensityExponential, p.PDF 3586–3587]. Densidade escalar ou array; log_mode devolve log natural da densidade. Escalar NaN em erro, array bool/result. Parâmetros: mu valor esperado, não taxa. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1192 — MathCumulativeDistributionExponential

[REF, MathCumulativeDistributionExponential, p.PDF 3588–3589]. CDF escalar/array; tail=true significa P(X<=x), log_mode calcula log da probabilidade. Escalar NaN, array false em erro. Parâmetros: mu valor esperado, não taxa. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1193 — MathQuantileExponential

[REF, MathQuantileExponential, p.PDF 3590–3591]. Inverte distribuição a partir de probabilidade; tail=false usa1−p, log_mode interpreta Exp(probability). Overloads escalares/arrays; algumas assinaturas array double contradizem narrativa false. Parâmetros: mu valor esperado, não taxa. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1194 — MathRandomExponential

[REF, MathRandomExponential, p.PDF 3592–3592]. Gera variável pseudoaleatória ou data_count valores em result; escalar NaN em erro, array false narrado. Registrar semente, parâmetros e contagem para reprodutibilidade; não usar seed GetTickCount em prova comparativa. Parâmetros: mu valor esperado, não taxa. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1195 — MathMomentsExponential

[REF, MathMomentsExponential, p.PDF 3593–3593]. Obtém quatro momentos teóricos via referências e error_code; sucesso narrado true/false embora assinatura double. Não confundir momentos teóricos com estimativas amostrais. Parâmetros: mu valor esperado, não taxa. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1196 — F-distribution

[REF, F-distribution, p.PDF 3594–3605]. FisherF: nu1/nu2 graus de liberdade; exemplo100/100,1M amostras. Proposta comparação estatística offline requer amostras/hipóteses justificadas; sem inferir regime do mercado.

### REF-1197 — MathProbabilityDensityF

[REF, MathProbabilityDensityF, p.PDF 3598–3599]. Densidade escalar ou array; log_mode devolve log natural da densidade. Escalar NaN em erro, array bool/result. Parâmetros: nu1 e nu2 graus de liberdade. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1198 — MathCumulativeDistributionF

[REF, MathCumulativeDistributionF, p.PDF 3600–3601]. CDF escalar/array; tail=true significa P(X<=x), log_mode calcula log da probabilidade. Escalar NaN, array false em erro. Parâmetros: nu1 e nu2 graus de liberdade. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1199 — MathQuantileF

[REF, MathQuantileF, p.PDF 3602–3603]. Inverte distribuição a partir de probabilidade; tail=false usa1−p, log_mode interpreta Exp(probability). Overloads escalares/arrays; algumas assinaturas array double contradizem narrativa false. Parâmetros: nu1 e nu2 graus de liberdade. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1200 — MathRandomF

[REF, MathRandomF, p.PDF 3604–3604]. Gera variável pseudoaleatória ou data_count valores em result; escalar NaN em erro, array false narrado. Registrar semente, parâmetros e contagem para reprodutibilidade; não usar seed GetTickCount em prova comparativa. Parâmetros: nu1 e nu2 graus de liberdade. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1201 — MathMomentsF

[REF, MathMomentsF, p.PDF 3605–3605]. Obtém quatro momentos teóricos via referências e error_code; sucesso narrado true/false embora assinatura double. Não confundir momentos teóricos com estimativas amostrais. Parâmetros: nu1 e nu2 graus de liberdade. Aplicação Stoikus: somente proposta de pesquisa/diagnóstico offline; checar finitude, retorno e código de erro, sem alterar limites financeiros.

### REF-1202 — Noncentral F-distribution

[REF, Noncentral F-distribution, p.PDF 3606–3607]. Leitura parcial3606–3607: F não central usa nu1,nu2,sigma não central; lista cinco APIs e inicia exemplo com20,20,10 e1M amostras. Continuação3608–3617 não lida aqui; não reivindicar exemplos completos ou assinaturas filhas.
