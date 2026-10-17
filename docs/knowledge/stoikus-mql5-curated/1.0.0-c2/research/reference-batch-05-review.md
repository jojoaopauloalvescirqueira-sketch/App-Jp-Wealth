# REF — lote05: leitura semântica e ledger

Estado: EM ANDAMENTO. Texto integral PDF1195–1390 lido; PDF1391–1586 em fila. Não equivale a leitura das figuras. Exemplos: NOT_RUN. Sem mudança de produto/kit/piloto.

Aplicações abaixo são propostas de engenharia para monitor event driven, não confirmação de chamadas presentes no código atual; nenhuma regra financeira JPW deriva dos exemplos da referência.

## REF-0251 — Array Functions (PDF1193–1286)

Continuação do capítulo: leitura deste lote começa em 1195; introdução1193–1194 pertence ao lote anterior. Contratos de arrays distinguem tamanho lógico, reserva, propriedade do terminal e sentido de indexação.

## REF-0252 — ArrayBsearch (PDF1195–1198)

Busca binária exige array numérico crescente; percorre dimensão zero e retorna índice do valor mais próximo quando não encontra igualdade. Proposta de teste: nunca tratar índice encontrado como confirmação de existência; comparar valor e validar array não vazio. Exemplo RSI ordena cópia e estima proporções; não estabelece regra financeira Stoikus.

## REF-0253 — ArrayCopy (PDF1199–1203)

Copia da esquerda para direita, ajustando início para séries; count negativo ou maior que restante copia restante; retorna quantidade copiada. Conversão entre numéricos possível; strings só para strings, estruturas só mesmo tipo e sem objetos que exijam inicialização. Destino dinâmico pode crescer, não encolhe automaticamente. Exemplo candles colore extremos com janela de confirmação e usa prev_calculated. Aplicação proposta: validar contagem e orientação antes de consumir snapshots.

## REF-0254 — ArrayCompare (PDF1204–1206)

Comparação lexicográfica de tipos iguais: -1/0/1, erro -2 para incompatibilidade ou intervalo inválido. WHOLE_ARRAY inclui diferença de tamanho mesmo se um array for prefixo fiel. Estruturas complexas com strings/arrays/classes excluídas. Aplicação proposta: comparadores de fixture devem separar erro de resultado menor, e igualdade exata de tolerância numérica.

## REF-0255 — ArrayFree (PDF1207–1215)

Libera buffer dinâmico e zera dimensão zero, sem retorno; buffers de indicador são geridos pelo terminal. Exemplo de diálogo monitora memória física/disponível/usada, muda tipo de array após liberar e recua tamanho quando falha alocação. Proposta: liberar caches descartáveis em ciclo de vida explícito, sem assumir controle sobre buffer vinculado.

## REF-0256 — ArrayGetAsSeries (PDF1216–1218)

Consulta flag AS_SERIES, diferente de pertencer a série temporal. OnCalculate não garante sentido esperado. Exemplo normaliza first/second/buffer para indexação direta e recalcula último elemento. Proposta aplicada ao monitor: declarar orientação no contrato de entrada, sem inferir por origem.

## REF-0257 — ArrayInitialize (PDF1219–1220)

Inicializa elementos numéricos atuais e retorna quantidade; não inicializa reserva. Crescimento dentro da reserva produz valores indefinidos, mesmo após preenchimento anterior com EMPTY_VALUE. Proposta: inicializar somente novo segmento e testar limites de expansão.

## REF-0258 — ArrayFill (PDF1221–1222)

Preenche intervalo de tipo simples, sempre indexação física direta, ignora AS_SERIES; multidimensional tratado linearmente (2x4, start5/count2 alcança [1][1] e [1][2]). Sem retorno. Proposta: não transportar índices de série diretamente para ArrayFill sem tradução.

## REF-0259 — ArrayIsDynamic (PDF1223–1224)

ArrayIsDynamic informa natureza dinâmica, não autorização para controlar buffer de indicador. Exemplo tenta ArrayFree em dinâmico, estático e buffer vinculado e registra tamanhos. Proposta: separar propriedade/capacidade de redimensionamento de mera declaração dinâmica.

## REF-0260 — ArrayIsSeries (PDF1225–1226)

ArrayIsSeries consulta pertencimento a série temporal; ordem de acesso deve ser consultada por ArrayGetAsSeries. Exemplo detecta open em OnCalculate. Proposta: não usar IsSeries como substituto do teste de orientação.

## REF-0261 — ArrayMaximum (PDF1227–1237)

Máximo retorna índice considerando AS_SERIES, -1 em falha; só pesquisa primeira dimensão mesmo para multidimensionais. Exemplo grande compõe candles de período superior com 16 buffers e oito plots, CopyTime, alternância de preenchimento e limpeza, atualizando candle em formação. Proposta: validar índice -1 antes de acessar valor; exemplo visual não é sinal operacional.

## REF-0262 — ArrayMinimum (PDF1238–1248)

Mínimo tem contrato análogo a máximo: primeira dimensão, start/count e AS_SERIES, falha -1. Exemplo integral repete composição de candles superiores; period checks exigem período maior, múltiplo e pelo menos3x para faixa intradiária, semanas/meses tratados à parte. Proposta: fixture com mínimo interior, borda, intervalo vazio e ambas orientações; não importar regras do exemplo como norma JPW.

## REF-0263 — ArrayPrint (PDF1249–1251)

ArrayPrint aceita tipos/estruturas simples, sem retorno; padrão imprime cabeçalho/índice/alinhamento e limita aos primeiros100+últimos100 elementos. Campos array e ponteiros são omitidos. Datas têm flags próprias. Proposta de evidência: log padrão não prova integridade do array nem estrutura; serialização específica necessária para evidência completa.

## REF-0264 — ArrayRange (PDF1252–1252)

ArrayRange devolve extensão de dimensão selecionada, índices de dimensão começam em0. Exemplo quatro dimensões10x5x2x4. Proposta: distinguir extensão de dimensão e total, evitando assumir que ArraySize seja número de linhas.

## REF-0265 — ArrayResize (PDF1253–1255)

Redimensiona primeira dimensão de array dinâmico; sucesso retorna total de elementos, falha -1 preserva array. Estático/série/buffer não realocam; se new_size<=ArraySize podem retornar new_size sem mudar tamanho. Limite total2147483647. Reserva só atua na alocação física e reduz realocações, sem inicializar novos elementos. Benchmark publicado é exemplo NOT_RUN, sem promessa de tempo no Stoikus.

## REF-0266 — ArrayInsert (PDF1256–1258)

Insere elementos independentes da origem; bool e GetLastError:5052 limites/origem vazia,5056 buffer indicador,4006 autocópia/tipos/objetos,4005 nãoPOD. Destino fixo não cresce; descrição afirma deslocamento/queda da cauda, mas resultado impresso do exemplo mostra substituição em4..6 preservando7..9. Divergência documental deve ser resolvida em harness nativo antes de depender; não escolher silenciosamente. Proposta: testar destino fixo/dinâmico, autocópia e objetos.

## REF-0267 — ArrayRemove (PDF1259–1260)

Remove intervalo; dinâmicos gerem tamanho, fixos mantêm tamanho e copiam cauda fisicamente, deixando valores duplicados no fim (0..9, remove4,2=>0,1,2,3,6,7,8,9,8,9). Buffers de indicador proibidos5056; limites5052/4003; estruturas/classes com destrutor4005/4006 por risco de dupla destruição. Proposta: política explícita de tamanho lógico em buffers fixos.

## REF-0268 — ArrayReverse (PDF1261–1262)

Reverte fisicamente intervalo, retorna bool; difere de SetAsSeries que apenas muda endereçamento lógico. Exemplo reverte4..6=>6,5,4. Proposta: nunca aplicar ambos inadvertidamente e inverter temporalidade duas vezes.

## REF-0269 — ArraySetAsSeries (PDF1263–1265)

Define AS_SERIES só em arrays dinâmicos unidimensionais, não em estáticos/multidimensionais; bool de sucesso. Exemplo vincula buffer antes de definir flag e usa time[0] para detectar nova barra. Proposta: validação explícita de retorno e vínculo temporal para monitor.

## REF-0270 — ArraySize (PDF1266–1267)

ArraySize é total de elementos; coincide com ArrayRange(a,0) somente em1D. Reserva não integra tamanho lógico. Exemplo multidimensional deriva dimensão zero pelo produto das outras. Proposta: validar capacidade vs número de registros e tamanho após expansão.

## REF-0271 — ArraySort (PDF1268–1272)

Ordena dimensão zero crescente independentemente de AS_SERIES; bool. Exemplo calcula limiares percentuais de tick volume em cópia ordenada de um mês, trata mês anterior com dia<=28, exige percentuais0<=p<50 e recalcula limites ao crescer histórico. Proposta: ordenar cópia para preservar correspondência tempo/preço; limiares exemplares não são norma ou funcionalidade existente.

## REF-0272 — ArraySwap (PDF1273–1274)

Troca conteúdo de arrays dinâmicos de mesmo tipo e mesmas dimensões exceto primeira; inteiros ignoram sinal(char/uchar). Falha bool/ERR_INVALID_ARRAY. Exemplo move tabela OHLCV para destino vazio e verifica origem vazia. Proposta: swap para substituir snapshot completo após validar construção, sem publicação parcial.

## REF-0273 — ArrayToFP16 (PDF1275–1277)

Converte float/double para ushort que armazena formato FLOAT16/BFLOAT16; bool, enum seleciona formato. Formatos usados em MQL5 para ONNX e OnnxRun; não é conversão numérica ushort comum. Proposta futura apenas: testar quantização/erro antes de modelo, nunca reduzir precisão de dinheiro/regra normativa.

## REF-0274 — ArrayToFP8 (PDF1278–1280)

Converte float/double para uchar codificado FP8 conforme ENUM_FLOAT8_FORMAT; bool. Exemplo prepara3x5 e compara reconversão com saída ONNX_NO_CONVERSION. Proposta futura apenas, sem ML no Stoikus atual; testar saturação/faixa e preservar formato junto aos bytes.

## REF-0275 — ArrayFromFP16 (PDF1281–1283)

Reconverte ushort FLOAT16/BFLOAT16 para float/double usando mesmo enum; bool. Exemplo inspeciona representação e soma erro absoluto após execução ONNX; resultado publicado não foi executado nesta pesquisa. Proposta futura: metadado de formato e tolerância explícita, sem usar para contabilidade.

## REF-0276 — ArrayFromFP8 (PDF1284–1286)

Reconverte uchar FP8 para float/double com formato enumerado, bool. Saída compacta ONNX requer interpretação correta; exemplar compara valores reconvertidos e modelo e chama OnnxRelease em erros. Proposta futura/sem uso direto atual: validar forma, formato e erro numérico em fixtures nativas.

## REF-0277 — Matrix and Vector Methods (PDF1287–1878)

Introdução1287–1293 lida: matriz2D/vetor1D double/float/complex, dimensão dinâmica; vetor não carrega orientação horizontal/vertical, determinada pela operação. Passagem DLL é ponteiro de buffer e exige passar tamanhos. Advertência antiga sobre complex não pode anular métodos complex posteriores sem teste. Continuação do capítulo após1335 pendente. Aplicação: referência para pesquisa futura, sem alegar matriz/ML no núcleo atual.

## REF-0278 — Matrix and Vector Types (PDF1294–1299)

Tipos matrix/matrixf/matrixc e vector/vectorf/vectorc; templates matrix<double>/matrix<float> equivalentes. Inicializadores estáticos separados de métodos de objeto. Proposta futura: tipo e precisão fazem parte do esquema de dados, não substituíveis implicitamente.

## REF-0279 — Enumerations (PDF1295–1299)

Enums de averaging(NONE/BINARY/MICRO/MACRO/WEIGHTED), normas, convolução FULL/SAME/VALID, regressão(MAE/MSE/RMSE/R2/MAPE/MSPE/RMSLE/SMAPE/MAXE/MEDE/MPD/MGD/EXPV), classificação, perdas e ativações; eixo AXIS_NONE reduz todos elementos, HORZ/VERT explícitos; ordenação ASC/DESC. Nota: tabela LOSS_MSE descreve root mean square apesar do identificadorMSE; exigir confirmação antes de fixar definição matemática. Aplicação futura apenas; métricas não equivalem a qualidade financeira ou conformidade.

## REF-0280 — Initialization (PDF1300–1329)

Declaração sem dimensões não aloca; declaração com dimensões aloca sem inicializar. Sequência inicializadora determina forma; callback pode preencher após alocação, parâmetros variáveis permitidos. Métodos estáticos criam objetos, Init/Fill alteram existentes. Proposta: inicializar explicitamente fixtures e não ler memória apenas alocada.

## REF-0281 — Assign (PDF1303–1304)

Assign copia matriz/vetor/array com cast automático e ajusta tamanho ao da origem, bool de sucesso; Copy não aceita array da mesma maneira. Exemplo contém Print de a sob título c, portanto saída textual ilustrativa não prova cópia errada. Proposta: assert de valores reais e forma em vez de confiar no rótulo do log.

## REF-0282 — CopyIndicatorBuffer (PDF1305–1306)

CopyIndicatorBuffer bool em três variantes posição/quantidade, data/quantidade e intervalo; start0 é barra atual mas memória física recebe mais antigo primeiro. Pré-alocar para quantidade fixa; vetor intermediário para cópia parcial. Indicador retorna false imediatamente e inicia construção/download; EA/script podem aguardar timeout. Texto menciona amount apesar de assinatura bool: verificar Size e disponibilidade, não usar bool como contagem. Proposta: recuperação assíncrona com estado pending no monitor.

## REF-0283 — CopyRates (PDF1307–1311)

CopyRates de matriz/vetor retorna bool, mais antigo no começo; vetor aceita só uma série, matriz combina máscaras em ordem fixaOPEN/HIGH/LOW/CLOSE/TIME/VOLUME/SPREAD. COPY_RATES_VERTICAL muda orientação de séries para colunas e registros para linhas. Dados fora servidor/MAXBARS falham; requisição por data usa aberturas<=data, intervalo exige abertura dentro dele (sem barra semanal se abertura fora). TIME em float perde cerca100s porque inteiros>2^24 inexatos. Proposta: conservar datetime/long/double apropriado e validar completude, barra0 incompleta explicitamente.

## REF-0284 — CopyTicks (PDF1312–1314)

CopyTicks retorna bool, índice0 mais antigo, from_msc em milissegundos,0 busca últimos count; omissão limita2000. Primeira chamada sincroniza base, indicador não espera; EA/script pode esperar45s. OnTick é aviso de mudança e pode representar lote, não garante callback por tick. Cache4096 ou65536 com MarketDepth. Tabela desta edição parece descrever INFO/TRADE/ALL de forma deslocada (INFO=all,TRADE=Bid/Ask,ALL=Last/volume), além de menção High/Low inadequada; não propagar sem conferir documentação nativa/harness. Proposta: capturar cursor/flags para monitor sem supor cobertura por OnTick.

## REF-0285 — CopyTicksRange (PDF1315–1316)

CopyTicksRange usa limites inclusivos >=from_msc e <=to_msc, mais antigo primeiro, flags do tick indicam campo alterado. Vetor uma seleção; erros timeout, buffer pequeno e memória insuficiente podem coexistir com dados parciais descritos no texto. Proposta: paginação por milissegundo com cuidado com múltiplos ticks no mesmo instante, diagnosticar completude sem transformar timeout em ausência de ticks.

## REF-0286 — Eye (PDF1317–1318)

Eye estático cria zeros e uns na diagonal k; positivo acima, negativo abaixo, rows/cols independentes. Proposta futura: construir fixtures retangulares/diagonal deslocada; sem uso direto no monitor atual.

## REF-0287 — Identity (PDF1319–1320)

Identity tem construtor estático rows/cols e método in-place sem retorno; exemplos retangulares3x5 confirmam diagonal de uns apesar da frase posterior chamar quadrada. Proposta futura: testar forma além da diagonal, não exigir quadratura por descrição genérica.

## REF-0288 — Ones (PDF1321–1321)

Ones cria nova matriz rows/cols ou vetor size com todos1. Proposta futura: fixtures de dimensão e baseline de redução; sem função financeira atual.

## REF-0289 — Zeros (PDF1322–1322)

Zeros cria nova matriz/vetor totalmente zero de forma solicitada. Proposta futura: inicialização explícita que evita tratar memória alocada como zerada.

## REF-0290 — Full (PDF1323–1323)

Full cria matriz/vetor novo preenchido por valor, distingue-se de Fill in-place. Proposta futura: usar sentinelas controladas em teste, sem confundir zero com ausência.

## REF-0291 — Tri (PDF1324–1324)

Tri cria matriz com uns na diagonal k e abaixo, zeros acima; k<0 desloca abaixo e k>0 acima; aceita retangular. Proposta futura: fixture para máscaras triangulares, sem autorização de mudança no produto.

## REF-0292 — Init (PDF1325–1326)

Init dimensiona matriz/vetor e aceita callback opcional com argumentos adicionais; void. Exemplo callback percorre rows/cols ou Size e mostra acúmulo de erro float/double em progressão0.1. Proposta futura: comparação por tolerância adequada, sem confundir render decimal com erro de implementação.

## REF-0293 — Fill (PDF1327–1327)

Fill modifica matriz/vetor existente com valor e retorna void. Proposta futura: inicialização explícita de scratch buffer; tamanho precisa existir antes do preenchimento.

## REF-0294 — Random (PDF1328–1329)

Random possui fábrica estática e método in-place, distribuição uniforme em[min,max] descrita sem prova de inclusão das bordas; padrões0..1. Assinaturas matriz usam float para limites e vetor double. Proposta futura: fixtures aleatórias com registro de dados/gerador, não assumir reprodutibilidade nem usar para sinais do Stoikus.

## REF-0295 — Manipulations (PDF1330–1380)

Manipulações1330–1331 lidas como visão de conjunto: forma, partes, cópias, ordenação, tolerâncias e NaNs são operações distintas; filhos após1335 pendentes. Aplicação futura: pipeline deve registrar transformações e preservar fonte.

## REF-0296 — HasNan (PDF1332–1332)

HasNan retorna contagem ulong, não bool. Compare/CompareByDigits consideram NaNs em posições correspondentes iguais embora comparação escalar NaN!=NaN. Proposta crítica: checar NaNs antes de aceitar igualdade numérica de fixture.

## REF-0297 — ReplaceNan (PDF1333–1333)

ReplaceNan substitui NaNs in-place e retorna quantidade; overloads float/double em matriz/vetor. Proposta futura: imputação deve ser política explícita e contagem auditada, não converter falha numérica em zero silenciosamente.

## REF-0298 — ReplaceToZero (PDF1334–1335)

ReplaceToZero substitui se abs(valor)<=abs_tol, para complex usa módulo; retorna contagem. Exemplo A@Inv(A) limpa resíduos1e-5 mas diagonal ainda aproxima1. Proposta futura: limpeza cosmética não prova inversão exata e não deve apagar resíduo significativo de regra financeira.

## REF-0299 — NormalizeDouble (PDF1336–1337)

NormalizeDouble retorna matriz/vetor arredondado com0–11 casas decimais; partes real/imaginária separadas. Exemplo arredonda A@Inv(A) para identidade visual. Proposta futura: arredondamento é transformação de dados, não prova de erro zero nem norma monetária.

## REF-0300 — Transpose (PDF1338–1339)

Transpose retorna matriz com eixos permutados; exemplo2x3=>3x2 e algoritmo indexa c[i][j]=a[j][i]. Proposta futura: registrar orientação de features e amostras antes/depois; sem uso direto atual.

## REF-0301 — TransposeConjugate (PDF1340–1340)

TransposeConjugate troca índices e inverte sinal da parte imaginária; algoritmo cria nova matriz cols x rows. Nota sobre Conjugate em reais devolver cópia deve ser distinguida da transposição. Proposta futura: testar matriz complexa não simétrica, não apenas real.

## REF-0302 — TriL (PDF1341–1341)

TriL retorna cópia preservando valores na região inferior e zerando acima da diagonal k. Exemplo k=-1 mantém4,7,8 etc.; frase de retorno que diz preencher com uns é incompatível com descrição/exemplo e parece resíduo de Tri. Proposta futura: preservar valores e testar diagonal deslocada nativamente.

## REF-0303 — TriU (PDF1342–1342)

TriU retorna cópia preservando parte superior e zerando abaixo da diagonal k, negativos incluem subdiagonais. Exemplo retangular4x3 k=-1 preserva8 e12 na parte inferior próxima à diagonal. Proposta futura: testar retangulares e offset; sem uso direto atual.

## REF-0304 — Diag (PDF1343–1344)

Diag tem leitura de diagonal para vetor e escrita de vetor na diagonal. Matriz sem alocação nasce zerada com forma compatível, incluindo offset; existente não muda dimensões nem valores fora do segmento escrito. Proposta futura: diferenciar construção e atualização parcial para não supor limpeza do resto.

## REF-0305 — Row (PDF1345–1346)

Row lê vetor da linha ou escreve vetor. Sem dimensões cria matriz zerada com nrow+1 linhas; existente mantém forma e valores além do vetor. Exemplo escreve3 valores em linha de5 e preserva dois7. Proposta futura: validar comprimento/índice e preservar schema de amostras.

## REF-0306 — Col (PDF1347–1348)

Col lê/escreve coluna; sem alocação cria zero com ncol+1 colunas e tamanho do vetor em linhas. Existente conserva demais células, inclusive trecho da coluna além do vetor. Proposta futura: teste de atualização parcial e formas retangulares; sem uso direto atual.

## REF-0307 — Copy (PDF1349–1350)

Copy é método bool de destino que copia matriz/vetor, não aceita array com cast como Assign. Exemplo compara Copy e inicialização por atribuição; exemplo Python b=a não demonstra propriedade de cópia MQL. Proposta futura: testar independência após mutação da origem e verificar retorno.

## REF-0308 — Conjugate (PDF1351–1351)

Conjugate retorna matriz/vetor com sinal imaginário trocado; real retorna cópia inalterada. Algoritmo preserva real e nega imag. Proposta futura: reconstrução complexa e teste conjugate duas vezes; sem uso no monitor atual.

## REF-0309 — Concat (PDF1352–1353)

Concat sem eixo achata matrizes sucessivamente em vetor; com axis0 empilha linhas, axis1 agrega colunas e exige dimensão compatível. Assinatura impressa usa matrix::Split na variante com eixo, enquanto exemplos chamam Concat; anomalia a confirmar no compilador. Proposta futura: teste de shape em vez de confiar em nome horizontal/vertical.

## REF-0310 — Compare (PDF1354–1355)

Compare retorna número de elementos diferentes por epsilon, não -1/1 lexicográfico. Operadores==/!= são exatos; para complex calcula distância euclidiana entre números. Proposta: comparador de fixture deve também rejeitar NaN e escolher tolerância pelo domínio, sem esconder falha financeira.

## REF-0311 — CompareByDigits (PDF1356–1357)

CompareByDigits retorna contagem de divergências por algarismos significativos; útil quando magnitudes variam1e-20..1e20. Exemplo oposição de sinais em termos minúsculos é invisível ao epsilon mas detectada por dígitos. Proposta: distinguir precisão relativa de casas decimais fixas.

## REF-0312 — CompareEqual (PDF1358–1360)

CompareEqual achata por linhas e compara até primeira diferença: -1/0/1. NaNs correspondentes iguais, sinal deNaN ignorado e NaN menor que numérico. Exemplo ainda discrimina matrizA/B não inicializada(-2/+2) e tamanhos(-3/+3); assinatura ulong conflita com negativos e exemplo int. Proposta futura: confirmar tipo/retornos nativos e não aceitar igualdade como validade numérica.

## REF-0313 — Flat (PDF1361–1362)

Flat lê por índice linear ou escreve com bool, ordem por linhas;3x3 Flat4 equivale[1][1]. Exemplo ArgMax seguido de Flat para ler e zerar maior. Proposta futura: validar limite rows*cols e mapear índice para evidência de célula.

## REF-0314 — Clip (PDF1363–1363)

Clip altera in-place cada valor para intervalo[min,max], retorna bool e não cria cópia. Proposta futura: preservar original e registrar contagem/razão de saturações; clipping não substitui validação de dados de mercado.

## REF-0315 — Reshape (PDF1364–1365)

Reshape void altera in-place forma em ordem linear e permite mudar total; novos elementos indefinidos. Exemplo3x5 contém valores arbitrários extras, não contrato de zero. Proposta futura: proibir leitura antes de inicializar faixa nova e testar perda por redução.

## REF-0316 — Resize (PDF1366–1367)

Resize bool in-place preserva dados por linha, diferentemente de Reshape linear; reduzindo colunas trunca cada linha, crescendo linhas/colunas cria valores indefinidos; reserve em itens. Descrição inicial que diz retornar nova matriz conflita com assinatura/nota. Proposta futura: verificar bool e preencher novos segmentos explicitamente.

## REF-0317 — Set (PDF1368–1369)

Set(index,value) de vetor é equivalente a atribuição por colchetes e retorna bool. Exemplo duas callbacks preenchem potências de2 por métodos distintos. Proposta futura: validar retorno/limites, sem inferir alteração de dimensão porSet.

## REF-0318 — SwapRows (PDF1370–1370)

SwapRows troca linhas por índices e bool; exemplo demonstra equivalência a multiplicação por matriz de permutação à esquerda. Proposta futura: preservar vínculo entre amostra e metadados ao permutar linhas.

## REF-0319 — SwapCols (PDF1371–1371)

SwapCols troca colunas por índices e bool; equivalente a permutação à direita. Assinatura chama parâmetros row1/row2, descrição é coluna. Proposta futura: schema de features deve acompanhar permutação, sem trocar colunas monetárias por preço silenciosamente.

## REF-0320 — Split (PDF1372–1373)

Split com número de partes exige divisibilidade de rows(axis0) ou cols(axis1). Array de tamanhos aceita partes diferentes e sobra final se tamanhos terminam. Assinatura da variantearray é void mas exemplo atribui resultado a bool; confirmar compilação. Proposta futura: testar sobra e soma das formas antes de reconstruir dados.

## REF-0321 — Hsplit (PDF1374–1375)

Hsplit equivale Split axis0 e divide linhas (nomenclatura difere de expectativas NumPy); count exige divisibilidade, tamanhos explícitos podem consumir só restante. Exemplo5linhas/2falha4003, /5sucesso. Proposta futura: afirmar shapes no harness para evitar transposição implícita.

## REF-0322 — Vsplit (PDF1376–1377)

Vsplit equivale Split axis1 e divide colunas, exige divisibilidade para count; array{2,3} em6colunas produz2,3,1. Proposta futura: testar resto e reconstrução ordenada, sem uso direto atual.

## REF-0323 — ArgSort (PDF1378–1378)

ArgSort retorna vetor/matriz de índices da ordenação indireta; padrão crescente, comparator opcional com contexto, eixo0/1. Assinaturas impressas chamamSort embora título ArgSort e retorno índices: não copiar cegamente. Proposta futura: aplicar permutação única a séries alinhadas, preservando timestamp.

## REF-0324 — Sort (PDF1379–1380)

Sort void altera in-place; aceita ASC/DESC ou comparador int(x1,x2[,context]) e contexto opcional. Exemplo declara vetor sem inicializar valores antes de ordenar, portanto não é fixture determinística válida. Proposta futura: definir dados conhecidos, testar estabilidade apenas se garantida separadamente.

## REF-0325 — Operations (PDF1381–1384)

Operações matemáticas distinguem aritmética elemento a elemento e funções vetorizadas; exemplo calcula desvio padrão populacional dividindo soma quadrática porSize e comparaStd. Proposta futura: não transportar denominadorN para norma financeira sem definição própria.

## REF-0326 — Mathematical operations (PDF1383–1383)

+,-,*,/ entre matrizes/vetores de mesmo tipo e dimensões são elemento a elemento; escalar apropriado pode operar em todos elementos, com+=,/=in-place. * é Hadamard, não produto matricial. Proposta crítica futura: distinguir @/MatMul de multiplicação de componentes.

## REF-0327 — Mathematical functions (PDF1384–1384)

MathAbs/trig/exponenciais/logs/arredondamentos/hiperbólicas operam elemento a elemento; MathMod/MathPow aceitam segundo escalar ou matriz/vetor compatível. Proposta futura: checar domínio matemático e NaNs antes da comparação, por exemplo raiz/log inválidos.

## REF-0328 — Products (PDF1385–1419)

Produtos agrupam MatMul/GeMM/Power/Dot/Kron/Inner/Outer/CorrCoef/Cov/Correlate/Convolve. Leitura introdutória1385 concluída; filhos além1390 pendentes. Proposta futura: selecionar operação pela definição e dimensionalidade, sem alegar analytics existente.

## REF-0329 — MatMul (PDF1386–1390)

MatMul: MxK comKxN=>MxN, vetorK à esquerda deKxN=>N, MxK com vetorK=>M, dois vetores iguais=>escalar Dot. Não comutativo. Nota genérica que vetor deve casar cols conflita com caso vetoràesquerda e exemplo3x5; seguir contratos por sobrecarga e validar nativamente. Proposta futura: fixtures retangulares e operandos invertidos; nenhum uso direto confirmado no núcleo atual.

## REF-0330 — GeMM (PDF1391–1394)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0331 — Power (PDF1395–1397)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0332 — Dot (PDF1398–1399)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0333 — Kron (PDF1400–1401)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0334 — Inner (PDF1402–1403)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0335 — Outer (PDF1404–1406)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0336 — CorrCoef (PDF1407–1410)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0337 — Cov (PDF1411–1413)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0338 — Correlate (PDF1414–1416)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0339 — Convolve (PDF1417–1419)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0340 — Transformations (PDF1420–1434)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0341 — Cholesky (PDF1421–1421)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0342 — Eig (PDF1422–1424)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0343 — EigVals (PDF1425–1425)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0344 — LU (PDF1426–1427)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0345 — LUP (PDF1428–1429)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0346 — QR (PDF1430–1431)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0347 — SVD (PDF1432–1434)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0348 — Statistics (PDF1435–1463)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0349 — ArgMax (PDF1436–1436)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0350 — ArgMin (PDF1437–1437)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0351 — Max (PDF1438–1438)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0352 — Min (PDF1439–1439)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0353 — Ptp (PDF1440–1440)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0354 — Sum (PDF1441–1441)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0355 — Prod (PDF1442–1443)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0356 — CumSum (PDF1444–1445)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0357 — CumProd (PDF1446–1447)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0358 — Percentile (PDF1448–1449)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0359 — Quantile (PDF1450–1451)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0360 — Median (PDF1452–1453)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0361 — Mean (PDF1454–1454)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0362 — Average (PDF1455–1456)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0363 — Std (PDF1457–1458)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0364 — Var (PDF1459–1460)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0365 — LinearRegression (PDF1461–1463)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0366 — Features (PDF1464–1481)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0367 — Rows (PDF1465–1465)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0368 — Cols (PDF1466–1466)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0369 — Size (PDF1467–1467)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0370 — Norm (PDF1468–1470)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0371 — Cond (PDF1471–1473)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0372 — Det (PDF1474–1475)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0373 — SLogDet (PDF1476–1476)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0374 — Rank (PDF1477–1479)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0375 — Trace (PDF1480–1480)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0376 — Spectrum (PDF1481–1481)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0377 — Matrix Classification (PDF1482–1494)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0378 — IsSymmetric (PDF1483–1483)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0379 — IsHermitian (PDF1484–1484)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0380 — IsUpperTriangular (PDF1485–1485)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0381 — IsLowerTriangular (PDF1486–1486)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0382 — IsTrapezoidal (PDF1487–1487)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0383 — IsUpperHessenberg (PDF1488–1488)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0384 — IsLowerHessenberg (PDF1489–1489)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0385 — IsTridiagonal (PDF1490–1490)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0386 — IsUpperBidiagonal (PDF1491–1491)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0387 — IsLowerBidiagonal (PDF1492–1492)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0388 — IsDiagonal (PDF1493–1493)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0389 — IsScalar (PDF1494–1494)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0390 — Solutions (PDF1495–1500)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0391 — Solve (PDF1496–1496)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0392 — LstSq (PDF1497–1497)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0393 — Inv (PDF1498–1499)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0394 — PInv (PDF1500–1500)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0395 — Machine learning (PDF1501–1537)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0396 — Activation (PDF1506–1509)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0397 — Derivative (PDF1510–1511)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0398 — Loss (PDF1512–1513)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0399 — LossGradient (PDF1514–1515)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0400 — RegressionMetric (PDF1516–1517)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0401 — ConfusionMatrix (PDF1518–1519)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0402 — ConfusionMatrixMultilabel (PDF1520–1521)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0403 — ClassificationMetric (PDF1522–1525)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0404 — ClassificationScore (PDF1526–1529)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0405 — PrecisionRecall (PDF1530–1533)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0406 — ReceiverOperatingCharacteristic (PDF1534–1537)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0407 — OpenBLAS (PDF1538–1878)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0408 — Singular Value Decomposition (PDF1541–1567)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0409 — SingularValueDecompositionDC (PDF1542–1543)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0410 — SingularValueDecompositionQR (PDF1544–1545)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0411 — SingularValueDecompositionQRPivot (PDF1546–1549)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0412 — SingularValueDecompositionBisection (PDF1550–1552)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0413 — SingularValueDecompositionJacobiHigh (PDF1553–1557)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0414 — SingularValueDecompositionJacobiLow (PDF1558–1560)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0415 — SingularValueDecompositionBidiagDC (PDF1561–1562)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0416 — SingularValueDecompositionBidiagBisect (PDF1563–1565)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0417 — SingularValueDecompositionBidiagQR (PDF1566–1567)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0418 — Eigen Values (PDF1568–1655)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0419 — General Matrices (PDF1572–1604)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0420 — EigenSolver (PDF1574–1575)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0421 — EigenSolverX (PDF1576–1579)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0422 — EigenSolverSchur (PDF1580–1581)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0423 — EigenSolver2 (PDF1582–1584)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## REF-0424 — EigenSolver2X (PDF1585–1589)

PENDENTE: leitura semântica ainda não realizada; índice não conta como leitura.

## Limites e continuidade

Corpus textual lido; visuais não conferidos automaticamente.
Exemplos NOT_RUN; sem compilação/MT5/EX5/piloto.
Truncamento inicial1204–1215 reparado por releitura integral.
Algumas linhas longas do código já cortadas no texto extraído; não reivindica fidelidade visual nem compilabilidade integral.

Próxima página obrigatória: 1391. A lista exata e hashes por página estão no JSON. Fila não pode ser promovida por extração, índice ou notas por rótulo.