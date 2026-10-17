# REF3769–4103 — leitura semântica batch12b

Leitura integral da camada textual de335 páginas físicas. Complementa e preserva `reference-batch-12-review.md`/coverage parcial161p; não altera seus registros históricos. Não presume leitura das páginas fora desta faixa.

Lotes10–23 de `/private/tmp/ref12` expostos integralmente em14 chamadas individuais, max_output_tokens20000, cada lote<=30000caracteres; nenhuma resposta truncada. Texto contém linhas horizontalmente cortadas na própria extração; não reconstruídas. Fórmulas gráficas e curvas ausentes não inspecionadas nem inferidas. **MQL_NOT_RUN**: MetaEditor/MT5/EX5/StrategyTester não executados. Produto, manual, harness e Git não alterados. Aplicações são propostas de pesquisa, não fatos de implementação nem regras JPW.

## Síntese aplicada

Operações vetoriais separam source const/result[] e mutação no lugar; preservar amostras e checar bool precede qualquer proposta. Diferenças têm orientação x[i+lag]-x[i]; produtos cumulativos operam fatores, não retornos percentuais implicitamente. Quantis, curtose, variância e correlações não especificam todas as convenções estatísticas nesta faixa: registrar janela, dados válidos e referências independentes antes de inferência.

Fuzzy modela pertinência e regras; pesos e formatos de pertinência são escolhas do modelador. Sugeno usa funções lineares e termo livre opcional; Mamdani exige decisões sobre agregação/implicação/desfuzzificação. Esta documentação sustenta um anexo de pesquisa futura, sem substituir regras determinísticas do Stoikus. CList* e retornos de parse não estabelecem, sozinhos, propriedade de memória ou validade de configuração.

OpenCL exige cadeia de inicialização, contagens, buffers, kernels, argumentos, execução, leitura e descarregamento. Os offsets possuem unidades distintas: BufferRead/Write usam bytes no buffer e índices no array; BufferFromArray descreve offset do array em bytes. Confirmar header e testar antes de usar. Hardware, suporte double, transferência e dimensão de grupo fazem parte do experimento, sem promessa de aceleração.

CObject.Compare/Save/Load são stubs de sucesso aparente e exigem implementação derivada. Coleções distinguem dados ativos/capacidade, Clear/Shutdown, e busca ordenada/linear. At usa sentinela que também é valor válido. Exemplos Save/Load apresentam guardas!=NULL invertidas; Type de Short/Int repete82; ToNormalMF e assinaturas fuzzy têm inconsistências editoriais. Estes trechos não podem ser apresentados como código compilado.

## Notas por ID

### REF-0001 — MQL5 Reference

Catálogo PDF74–7284; interseção lida 3769–4103; PARTIAL_FULL_TEXT_READ.

Contêiner geral: somente a interseção3769–4103 foi lida aqui; não prova leitura do livro inteiro. [REF, MQL5 Reference, p.PDF 3769–4103]

### REF-1136 — Standard Library

Catálogo PDF3484–7007; interseção lida 3769–4103; PARTIAL_FULL_TEXT_READ.

Biblioteca padrão: interseção matemática, fuzzy, OpenCL, CObject e coleções lida; demais páginas fora do escopo. [REF, Standard Library, p.PDF 3769–4103]

### REF-1137 — Mathematics

Catálogo PDF3485–3935; interseção lida 3769–3935; PARTIAL_FULL_TEXT_READ.

Interseção3769–3935: subfunções estatísticas e fuzzy; catálogo pai inclui páginas anteriores não cobertas aqui. [REF, Mathematics, p.PDF 3769–3935]

### REF-1138 — Statistics

Catálogo PDF3486–3843; interseção lida 3769–3843; PARTIAL_FULL_TEXT_READ.

Interseção3769–3843: operações vetoriais, estatísticas descritivas, correlações e distribuições empíricas; não estabelece aderência de mercado. [REF, Statistics, p.PDF 3769–3843]

### REF-1274 — Subfunctions

Catálogo PDF3748–3843; interseção lida 3769–3843; PARTIAL_FULL_TEXT_READ.

Subfunções3769–3843: preservar distinção entre transformações no lugar, saídas separadas e estatísticas escalares; início3748–3768 pertence a outro registro. [REF, Subfunctions, p.PDF 3769–3843]

### REF-1289 — MathBinomialCoefficientLog

Catálogo PDF3769–3769; interseção lida 3769–3769; FULL_TEXT_READ.

Log(C(n,k)) em overloads int e double; retorna double. Não documenta domínio/erro nesta página: proposta combinatória em escala log deve validar entradas. [REF, MathBinomialCoefficientLog, p.PDF 3769–3769]

### REF-1290 — MathHypergeometric2F2

Catálogo PDF3770–3770; interseção lida 3770–3770; FULL_TEXT_READ.

Hypergeometric_2F2(a,b,c,d,z) calculada por Taylor; retorna double. Função especial, não distribuição hipergeométrica; sem uso atual demonstrado. [REF, MathHypergeometric2F2, p.PDF 3770–3770]

### REF-1291 — MathSequence

Catálogo PDF3771–3771; interseção lida 3771–3771; FULL_TEXT_READ.

Sequência from/to/step, arrays int ou double e retorno bool; proposta para grades sintéticas com passo e extremos verificados. [REF, MathSequence, p.PDF 3771–3771]

### REF-1292 — MathSequenceByCount

Catálogo PDF3772–3772; interseção lida 3772–3772; FULL_TEXT_READ.

Sequência from/to/count, arrays int ou double, bool; count define quantidade, não passo. Proposta de amostras determinísticas; conferir discretização inteira. [REF, MathSequenceByCount, p.PDF 3772–3772]

### REF-1293 — MathReplicate

Catálogo PDF3773–3773; interseção lida 3773–3773; FULL_TEXT_READ.

Repete array int/double count vezes em result[]; bool. Proposta de fixtures, sem presumir amostras independentes por replicação. [REF, MathReplicate, p.PDF 3773–3773]

### REF-1294 — MathReverse

Catálogo PDF3774–3774; interseção lida 3774–3774; FULL_TEXT_READ.

Inverte ordem int/double com saída separada ou no lugar; bool. Proposta: explicitar orientação temporal e preservar fonte. [REF, MathReverse, p.PDF 3774–3774]

### REF-1295 — MathIdentical

Catálogo PDF3775–3775; interseção lida 3775–3775; FULL_TEXT_READ.

Compara todos os elementos int/double e retorna bool de igualdade. Igualdade exata não é tolerância numérica para cálculos. [REF, MathIdentical, p.PDF 3775–3775]

### REF-1296 — MathUnique

Catálogo PDF3776–3776; interseção lida 3776–3776; FULL_TEXT_READ.

Produz apenas valores únicos int/double em result[], bool. Proposta: deduplicação exige preservar frequência e ordem necessárias ao diagnóstico. [REF, MathUnique, p.PDF 3776–3776]

### REF-1297 — MathQuickSortAscending

Catálogo PDF3777–3777; interseção lida 3777–3777; FULL_TEXT_READ.

QuickSort crescente altera array double e indices int simultaneamente entre first/last; void. Proposta: preservar índices de origem ao ordenar. [REF, MathQuickSortAscending, p.PDF 3777–3777]

### REF-1298 — MathQuickSortDescending

Catálogo PDF3778–3778; interseção lida 3778–3778; FULL_TEXT_READ.

QuickSort decrescente altera valores e índices no intervalo; void. Proposta de ranking, sem presumir estabilidade nos empates. [REF, MathQuickSortDescending, p.PDF 3778–3778]

### REF-1299 — MathQuickSort

Catálogo PDF3779–3779; interseção lida 3779–3779; FULL_TEXT_READ.

QuickSort conjunto valores/índices; mode>0 crescente, demais decrescente; void. Validar limites first/last. [REF, MathQuickSort, p.PDF 3779–3779]

### REF-1300 — MathOrder

Catálogo PDF3780–3780; interseção lida 3780–3780; FULL_TEXT_READ.

MathOrder produz permutação inteira de índices segundo valores int/double ordenados; bool. Permite ordenar referências sem trocar identidade dos registros. [REF, MathOrder, p.PDF 3780–3780]

### REF-1301 — MathBitwiseNot

Catálogo PDF3781–3781; interseção lida 3781–3781; FULL_TEXT_READ.

NOT bit a bit de cada inteiro; result[] e bool, variantes unárias também no lugar. Proposta para flags precisa de largura/sinal e limites n verificados; não é cálculo financeiro. [REF, MathBitwiseNot, p.PDF 3781–3781]

### REF-1302 — MathBitwiseAnd

Catálogo PDF3782–3782; interseção lida 3782–3782; FULL_TEXT_READ.

AND bit a bit de dois arrays inteiros; result[] e bool, variantes unárias também no lugar. Proposta para flags precisa de largura/sinal e limites n verificados; não é cálculo financeiro. [REF, MathBitwiseAnd, p.PDF 3782–3782]

### REF-1303 — MathBitwiseOr

Catálogo PDF3783–3783; interseção lida 3783–3783; FULL_TEXT_READ.

OR bit a bit de dois arrays inteiros; result[] e bool, variantes unárias também no lugar. Proposta para flags precisa de largura/sinal e limites n verificados; não é cálculo financeiro. [REF, MathBitwiseOr, p.PDF 3783–3783]

### REF-1304 — MathBitwiseXor

Catálogo PDF3784–3784; interseção lida 3784–3784; FULL_TEXT_READ.

XOR bit a bit de dois arrays inteiros; result[] e bool, variantes unárias também no lugar. Proposta para flags precisa de largura/sinal e limites n verificados; não é cálculo financeiro. [REF, MathBitwiseXor, p.PDF 3784–3784]

### REF-1305 — MathBitwiseShiftL

Catálogo PDF3785–3785; interseção lida 3785–3785; FULL_TEXT_READ.

deslocamento à esquerda n bits em inteiros; result[] e bool, variantes unárias também no lugar. Proposta para flags precisa de largura/sinal e limites n verificados; não é cálculo financeiro. [REF, MathBitwiseShiftL, p.PDF 3785–3785]

### REF-1306 — MathBitwiseShiftR

Catálogo PDF3786–3786; interseção lida 3786–3786; FULL_TEXT_READ.

deslocamento à direita n bits em inteiros; result[] e bool, variantes unárias também no lugar. Proposta para flags precisa de largura/sinal e limites n verificados; não é cálculo financeiro. [REF, MathBitwiseShiftR, p.PDF 3786–3786]

### REF-1307 — MathCumulativeSum

Catálogo PDF3787–3787; interseção lida 3787–3787; FULL_TEXT_READ.

Somas cumulativas double; saída separada ou no lugar, bool. Proposta: curva acumulada depende da ordem cronológica e da unidade. [REF, MathCumulativeSum, p.PDF 3787–3787]

### REF-1308 — MathCumulativeProduct

Catálogo PDF3788–3788; interseção lida 3788–3788; FULL_TEXT_READ.

Produtos cumulativos double, saída separada ou no lugar, bool. Proposta: composição de fatores somente com convenção de retorno definida. [REF, MathCumulativeProduct, p.PDF 3788–3788]

### REF-1309 — MathCumulativeMin

Catálogo PDF3789–3789; interseção lida 3789–3789; FULL_TEXT_READ.

Mínimos cumulativos double, saída separada ou no lugar, bool. Proposta de extremos de janela, não limite normativo. [REF, MathCumulativeMin, p.PDF 3789–3789]

### REF-1310 — MathCumulativeMax

Catálogo PDF3790–3790; interseção lida 3790–3790; FULL_TEXT_READ.

Máximos cumulativos double, saída separada ou no lugar, bool. Proposta de picos históricos; não prova recuperação ou controle de risco. [REF, MathCumulativeMax, p.PDF 3790–3790]

### REF-1311 — MathSin

Catálogo PDF3791–3791; interseção lida 3791–3791; FULL_TEXT_READ.

Transforma cada elemento double por sin(x); bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathSin, p.PDF 3791–3791]

### REF-1312 — MathCos

Catálogo PDF3792–3792; interseção lida 3792–3792; FULL_TEXT_READ.

Transforma cada elemento double por cos(x); bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathCos, p.PDF 3792–3792]

### REF-1313 — MathTan

Catálogo PDF3793–3793; interseção lida 3793–3793; FULL_TEXT_READ.

Transforma cada elemento double por tan(x); bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathTan, p.PDF 3793–3793]

### REF-1314 — MathArcsin

Catálogo PDF3794–3794; interseção lida 3794–3794; FULL_TEXT_READ.

Transforma cada elemento double por arcsin(x); bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathArcsin, p.PDF 3794–3794]

### REF-1315 — MathArccos

Catálogo PDF3795–3795; interseção lida 3795–3795; FULL_TEXT_READ.

Transforma cada elemento double por arccos(x); bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathArccos, p.PDF 3795–3795]

### REF-1316 — MathArctan

Catálogo PDF3796–3796; interseção lida 3796–3796; FULL_TEXT_READ.

Transforma cada elemento double por arctan(x); bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathArctan, p.PDF 3796–3796]

### REF-1317 — MathSinPi

Catálogo PDF3797–3797; interseção lida 3797–3797; FULL_TEXT_READ.

Transforma cada elemento double por sin(pi*x); bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathSinPi, p.PDF 3797–3797]

### REF-1318 — MathCosPi

Catálogo PDF3798–3798; interseção lida 3798–3798; FULL_TEXT_READ.

Transforma cada elemento double por cos(pi*x); bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathCosPi, p.PDF 3798–3798]

### REF-1319 — MathTanPi

Catálogo PDF3799–3799; interseção lida 3799–3799; FULL_TEXT_READ.

Transforma cada elemento double por tan(pi*x); bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathTanPi, p.PDF 3799–3799]

### REF-1320 — MathAbs

Catálogo PDF3800–3800; interseção lida 3800–3800; FULL_TEXT_READ.

Transforma cada elemento double por abs(x); bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathAbs, p.PDF 3800–3800]

### REF-1321 — MathCeil

Catálogo PDF3801–3801; interseção lida 3801–3801; FULL_TEXT_READ.

Transforma cada elemento double por inteiro superior ceil; bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathCeil, p.PDF 3801–3801]

### REF-1322 — MathFloor

Catálogo PDF3802–3802; interseção lida 3802–3802; FULL_TEXT_READ.

Transforma cada elemento double por inteiro inferior floor; bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathFloor, p.PDF 3802–3802]

### REF-1323 — MathSqrt

Catálogo PDF3803–3803; interseção lida 3803–3803; FULL_TEXT_READ.

Transforma cada elemento double por raiz quadrada; bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathSqrt, p.PDF 3803–3803]

### REF-1324 — MathExp

Catálogo PDF3804–3804; interseção lida 3804–3804; FULL_TEXT_READ.

Transforma cada elemento double por exp(x); bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathExp, p.PDF 3804–3804]

### REF-1325 — MathPow

Catálogo PDF3805–3805; interseção lida 3805–3805; FULL_TEXT_READ.

Potência x^power em arrays double, expoente comum double, saída separada ou no lugar; bool. Validar domínio e finitude antes de uso. [REF, MathPow, p.PDF 3805–3805]

### REF-1326 — MathLog

Catálogo PDF3806–3806; interseção lida 3806–3806; FULL_TEXT_READ.

Log natural ou base explicitada, arrays double com saída separada ou no lugar; bool. Não inferir domínio ou tratamento de base inválida desta página. [REF, MathLog, p.PDF 3806–3806]

### REF-1327 — MathLog2

Catálogo PDF3807–3807; interseção lida 3807–3807; FULL_TEXT_READ.

Transforma cada elemento double por log base2; bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathLog2, p.PDF 3807–3807]

### REF-1328 — MathLog10

Catálogo PDF3808–3808; interseção lida 3808–3808; FULL_TEXT_READ.

Transforma cada elemento double por log base10; bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathLog10, p.PDF 3808–3808]

### REF-1329 — MathLog1p

Catálogo PDF3809–3809; interseção lida 3809–3809; FULL_TEXT_READ.

Transforma cada elemento double por log(1+x); bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathLog1p, p.PDF 3809–3809]

### REF-1330 — MathDifference

Catálogo PDF3810–3811; interseção lida 3810–3811; FULL_TEXT_READ.

Diferença y[i]=x[i+lag]-x[i], int/double; overload differences repete operação; bool/result[]. Orientação e encurtamento da série precisam de teste antes de calcular variações. [REF, MathDifference, p.PDF 3810–3811]

### REF-1331 — MathSample

Catálogo PDF3812–3814; interseção lida 3812–3814; FULL_TEXT_READ.

Amostragem int/double com count, probabilidade opcional e replace opcional; replace=true repõe elemento à sequência. Bool/result[]; proposal bootstrap exige semente e política de probabilidades, não presentes neste contrato. [REF, MathSample, p.PDF 3812–3814]

### REF-1332 — MathTukeySummary

Catálogo PDF3815–3815; interseção lida 3815–3815; FULL_TEXT_READ.

Resumo Tukey em cinco saídas: mínimo, lower_hinge, mediana, upper_hinge, máximo; removeNAN explícito; bool. Proposta diagnóstica deve registrar descarte de NaN. [REF, MathTukeySummary, p.PDF 3815–3815]

### REF-1333 — MathRange

Catálogo PDF3816–3816; interseção lida 3816–3816; FULL_TEXT_READ.

MathRange retorna mínimo e máximo por referência, bool; não confundir com amplitude max-min. [REF, MathRange, p.PDF 3816–3816]

### REF-1334 — MathMin

Catálogo PDF3817–3817; interseção lida 3817–3817; FULL_TEXT_READ.

Retorna double de mínimo dos elementos double const. Proposta de diagnóstico precisa de janela/unidade e tratamento de vazio/NaN, não documentados aqui; não constitui norma JPW. [REF, MathMin, p.PDF 3817–3817]

### REF-1335 — MathMax

Catálogo PDF3818–3818; interseção lida 3818–3818; FULL_TEXT_READ.

Retorna double de máximo dos elementos double const. Proposta de diagnóstico precisa de janela/unidade e tratamento de vazio/NaN, não documentados aqui; não constitui norma JPW. [REF, MathMax, p.PDF 3818–3818]

### REF-1336 — MathSum

Catálogo PDF3819–3819; interseção lida 3819–3819; FULL_TEXT_READ.

Retorna double de soma dos elementos double const. Proposta de diagnóstico precisa de janela/unidade e tratamento de vazio/NaN, não documentados aqui; não constitui norma JPW. [REF, MathSum, p.PDF 3819–3819]

### REF-1337 — MathProduct

Catálogo PDF3820–3820; interseção lida 3820–3820; FULL_TEXT_READ.

Retorna double de produto dos elementos double const. Proposta de diagnóstico precisa de janela/unidade e tratamento de vazio/NaN, não documentados aqui; não constitui norma JPW. [REF, MathProduct, p.PDF 3820–3820]

### REF-1338 — MathStandardDeviation

Catálogo PDF3821–3821; interseção lida 3821–3821; FULL_TEXT_READ.

Retorna double de desvio padrão dos elementos double const. Proposta de diagnóstico precisa de janela/unidade e tratamento de vazio/NaN, não documentados aqui; não constitui norma JPW. [REF, MathStandardDeviation, p.PDF 3821–3821]

### REF-1339 — MathAverageDeviation

Catálogo PDF3822–3822; interseção lida 3822–3822; FULL_TEXT_READ.

Retorna double de desvio absoluto médio dos elementos double const. Proposta de diagnóstico precisa de janela/unidade e tratamento de vazio/NaN, não documentados aqui; não constitui norma JPW. [REF, MathAverageDeviation, p.PDF 3822–3822]

### REF-1340 — MathMedian

Catálogo PDF3823–3823; interseção lida 3823–3823; FULL_TEXT_READ.

MathMedian recebe array double por referência não const e retorna double. Proposta: usar cópia para não presumir imutabilidade. [REF, MathMedian, p.PDF 3823–3823]

### REF-1341 — MathMean

Catálogo PDF3824–3824; interseção lida 3824–3824; FULL_TEXT_READ.

Retorna double de média dos elementos double const. Proposta de diagnóstico precisa de janela/unidade e tratamento de vazio/NaN, não documentados aqui; não constitui norma JPW. [REF, MathMean, p.PDF 3824–3824]

### REF-1342 — MathVariance

Catálogo PDF3825–3825; interseção lida 3825–3825; FULL_TEXT_READ.

MathVariance descreve variância/segundo momento, retorna double; não especifica divisor amostral/populacional aqui. Testar antes de comparação externa. [REF, MathVariance, p.PDF 3825–3825]

### REF-1343 — MathSkewness

Catálogo PDF3826–3826; interseção lida 3826–3826; FULL_TEXT_READ.

MathSkewness descreve terceiro momento, retorna double; fórmula/correção não explicitadas. Proposta descritiva, sem inferência de normalidade. [REF, MathSkewness, p.PDF 3826–3826]

### REF-1344 — MathKurtosis

Catálogo PDF3827–3827; interseção lida 3827–3827; FULL_TEXT_READ.

MathKurtosis descreve quarto momento, retorna double; excesso versus curtose não explicitado. Não impor convenção a partir do nome. [REF, MathKurtosis, p.PDF 3827–3827]

### REF-1345 — MathExpm1

Catálogo PDF3828–3828; interseção lida 3828–3828; FULL_TEXT_READ.

Transforma cada elemento double por exp(x)-1; bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathExpm1, p.PDF 3828–3828]

### REF-1346 — MathSinh

Catálogo PDF3829–3829; interseção lida 3829–3829; FULL_TEXT_READ.

Transforma cada elemento double por sinh(x); bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathSinh, p.PDF 3829–3829]

### REF-1347 — MathCosh

Catálogo PDF3830–3830; interseção lida 3830–3830; FULL_TEXT_READ.

Transforma cada elemento double por cosh(x); bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathCosh, p.PDF 3830–3830]

### REF-1348 — MathTanh

Catálogo PDF3831–3831; interseção lida 3831–3831; FULL_TEXT_READ.

Transforma cada elemento double por tanh(x); bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathTanh, p.PDF 3831–3831]

### REF-1349 — MathArcsinh

Catálogo PDF3832–3832; interseção lida 3832–3832; FULL_TEXT_READ.

Transforma cada elemento double por arcsinh(x); bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathArcsinh, p.PDF 3832–3832]

### REF-1350 — MathArccosh

Catálogo PDF3833–3833; interseção lida 3833–3833; FULL_TEXT_READ.

Transforma cada elemento double por arccosh(x); bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathArccosh, p.PDF 3833–3833]

### REF-1351 — MathArctanh

Catálogo PDF3834–3834; interseção lida 3834–3834; FULL_TEXT_READ.

Transforma cada elemento double por arctanh(x); bool, saída separada ou alteração no lugar. Proposta matemática futura: preservar amostra e validar domínio/finitude; página não especifica erros numéricos. [REF, MathArctanh, p.PDF 3834–3834]

### REF-1352 — MathSignif

Catálogo PDF3835–3836; interseção lida 3835–3836; FULL_TEXT_READ.

MathSignif arredonda dígitos de mantissa; scalar e arrays. Texto também chama digits casas decimais: conferir implementação, sem confundir com MathRound monetário. [REF, MathSignif, p.PDF 3835–3836]

### REF-1353 — MathRank

Catálogo PDF3837–3837; interseção lida 3837–3837; FULL_TEXT_READ.

Rank de valores int/double em rank[] double, bool. Não documenta desempate aqui; proposta de correlação deve testar empates. [REF, MathRank, p.PDF 3837–3837]

### REF-1354 — MathCorrelationPearson

Catálogo PDF3838–3838; interseção lida 3838–3838; FULL_TEXT_READ.

Correlação Pearson entre dois arrays int/double, bool e r por referência. Proposta exige alinhamento temporal e variação não nula; correlação não causalidade. [REF, MathCorrelationPearson, p.PDF 3838–3838]

### REF-1355 — MathCorrelationSpearman

Catálogo PDF3839–3839; interseção lida 3839–3839; FULL_TEXT_READ.

Correlação Spearman, bool e r por referência em pares int/double. Proposta exige política de empates e amostras alinhadas. [REF, MathCorrelationSpearman, p.PDF 3839–3839]

### REF-1356 — MathCorrelationKendall

Catálogo PDF3840–3840; interseção lida 3840–3840; FULL_TEXT_READ.

Correlação Kendall, bool e tau por referência. Não especifica variante tau no texto; validar convenção antes de confronto externo. [REF, MathCorrelationKendall, p.PDF 3840–3840]

### REF-1357 — MathQuantile

Catálogo PDF3841–3841; interseção lida 3841–3841; FULL_TEXT_READ.

Quantis amostrais por probs[], saída quantile[], fórmula interpolada(1-gamma)*x[j]+gamma*x[j+1]; bool. Convenção completa de j/gamma não dada; proposta exige fixtures independentes. [REF, MathQuantile, p.PDF 3841–3841]

### REF-1358 — MathProbabilityDensityEmpirical

Catálogo PDF3842–3842; interseção lida 3842–3842; FULL_TEXT_READ.

Densidade empírica gera count pares(x,pdf) de array double, bool. Resolução count faz parte da evidência; densidade não é probabilidade pontual. [REF, MathProbabilityDensityEmpirical, p.PDF 3842–3842]

### REF-1359 — MathCumulativeDistributionEmpirical

Catálogo PDF3843–3843; interseção lida 3843–3843; FULL_TEXT_READ.

Acumulada empírica gera count pares(x,cdf) de array double, bool. Proposta de diagnóstico preserva amostra e resolução; não substitui teste de aderência. [REF, MathCumulativeDistributionEmpirical, p.PDF 3843–3843]

### REF-1360 — Fuzzy Logic

Catálogo PDF3844–3935; interseção lida 3844–3935; FULL_TEXT_READ.

Fuzzy3844–3935: entradas/saídas, base if/then e inferência Mamdani/Sugeno; pesos[0,1]. A descrição reconhece subjetividade. Apenas pesquisa futura: não há uso atual Stoikus comprovado e regras JPW determinísticas não são substituídas. [REF, Fuzzy Logic, p.PDF 3844–3935]

### REF-1361 — Membership functions

Catálogo PDF3845–3904; interseção lida 3845–3904; FULL_TEXT_READ.

Catálogo e contratos de pertinência constantes, compostas, gaussianas, sigmoides e funções por trechos. Grau em[0,1] é saída; texto usa termo domain de modo impreciso e diz monotonia em geral apesar de curvas não monotônicas. Não inferir gráficos ausentes. [REF, Membership functions, p.PDF 3845–3904]

### REF-1362 — CConstantMembershipFunction

Catálogo PDF3847–3849; interseção lida 3847–3849; FULL_TEXT_READ.

Pertinência constante y(x)=c, mesmo grau em todo x; exemplo0.2/0.5/0.8 e gráficos CGraphic. Só proposta de baseline fuzzy. [REF, CConstantMembershipFunction, p.PDF 3847–3849]

### REF-1363 — GetValue

Catálogo PDF3849–3849; interseção lida 3849–3849; FULL_TEXT_READ.

GetValue(x) retorna grau de pertinência double. Pertence a REF-1362; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, GetValue, p.PDF 3849–3849]

### REF-1364 — CCompositeMembershipFunction

Catálogo PDF3850–3853; interseção lida 3850–3853; FULL_TEXT_READ.

Composição de duas ou mais pertinências; operadores MinMF/MaxMF/ProdMF/SumMF, lista CList*. Exemplo produto sigmoid×pi; verificar faixa da soma antes de adoção. [REF, CCompositeMembershipFunction, p.PDF 3850–3853]

### REF-1365 — CompositionType

Catálogo PDF3852–3853; interseção lida 3852–3853; FULL_TEXT_READ.

CompositionType recebe MfCompositionType e define mínimo, máximo, produto ou soma. Proposta futura deve registrar operador; não equiparar união fuzzy a soma sem validação. [REF, CompositionType, p.PDF 3852–3853]

### REF-1366 — MembershipFunctions

Catálogo PDF3852–3853; interseção lida 3852–3853; FULL_TEXT_READ.

MembershipFunctions retorna CList* da composição. Proposta futura exige contratos de propriedade/vida útil, não explicitados aqui. [REF, MembershipFunctions, p.PDF 3852–3853]

### REF-1367 — GetValue

Catálogo PDF3852–3853; interseção lida 3852–3853; FULL_TEXT_READ.

GetValue(x) retorna double de pertinência composta; protótipo omite tipo de x, conferir header. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, GetValue, p.PDF 3852–3853]

### REF-1368 — CDifferencTwoSigmoidalMembershipFunction

Catálogo PDF3854–3858; interseção lida 3854–3858; FULL_TEXT_READ.

Diferença de duas sigmoides: A1/A2 inclinações, C1/C2 inflexões; GetValue. Exemplo de traçado não prova saturação nem faixa para parâmetros arbitrários. [REF, CDifferencTwoSigmoidalMembershipFunction, p.PDF 3854–3858]

### REF-1369 — A1

Catálogo PDF3856–3856; interseção lida 3856–3856; FULL_TEXT_READ.

A1: getter double e setter const double para primeira inclinação. Pertence a REF-1368; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, A1, p.PDF 3856–3856]

### REF-1370 — A2

Catálogo PDF3856–3856; interseção lida 3856–3856; FULL_TEXT_READ.

A2: getter double e setter const double para segunda inclinação. Pertence a REF-1368; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, A2, p.PDF 3856–3856]

### REF-1371 — C1

Catálogo PDF3857–3857; interseção lida 3857–3857; FULL_TEXT_READ.

C1: getter double e setter const double para primeira inflexão. Pertence a REF-1368; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, C1, p.PDF 3857–3857]

### REF-1372 — C2

Catálogo PDF3857–3857; interseção lida 3857–3857; FULL_TEXT_READ.

C2: getter double e setter const double para segunda inflexão. Pertence a REF-1368; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, C2, p.PDF 3857–3857]

### REF-1373 — GetValue

Catálogo PDF3858–3858; interseção lida 3858–3858; FULL_TEXT_READ.

GetValue(x) retorna grau de pertinência double. Pertence a REF-1368; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, GetValue, p.PDF 3858–3858]

### REF-1374 — CGeneralizedBellShapedMembershipFunction

Catálogo PDF3859–3862; interseção lida 3859–3862; FULL_TEXT_READ.

Sino generalizado suave e não nulo no domínio: A concentração, B inclinação, C coordenada de máximo; GetValue. Proposta de pertinência futura, não distribuição estatística ajustada. [REF, CGeneralizedBellShapedMembershipFunction, p.PDF 3859–3862]

### REF-1375 — A

Catálogo PDF3861–3861; interseção lida 3861–3861; FULL_TEXT_READ.

A: getter double e setter const double para concentração. Pertence a REF-1374; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, A, p.PDF 3861–3861]

### REF-1376 — B

Catálogo PDF3861–3861; interseção lida 3861–3861; FULL_TEXT_READ.

B: getter double e setter const double para inclinação. Pertence a REF-1374; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, B, p.PDF 3861–3861]

### REF-1377 — C

Catálogo PDF3862–3862; interseção lida 3862–3862; FULL_TEXT_READ.

C: getter double e setter const double para coordenada de máximo. Pertence a REF-1374; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, C, p.PDF 3862–3862]

### REF-1378 — GetValue

Catálogo PDF3862–3862; interseção lida 3862–3862; FULL_TEXT_READ.

GetValue(x) retorna grau de pertinência double. Pertence a REF-1374; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, GetValue, p.PDF 3862–3862]

### REF-1379 — CNormalCombinationMembershipFunction

Catálogo PDF3863–3867; interseção lida 3863–3867; FULL_TEXT_READ.

Combinação gaussiana de dois lados assimétrica, B1/B2 centros e Sigma1/Sigma2 curvaturas; exemplo4parâmetros. Proposta exige validar sigmas e extremos. [REF, CNormalCombinationMembershipFunction, p.PDF 3863–3867]

### REF-1380 — B1

Catálogo PDF3865–3865; interseção lida 3865–3865; FULL_TEXT_READ.

B1: getter double e setter const double para primeiro centro. Pertence a REF-1379; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, B1, p.PDF 3865–3865]

### REF-1381 — B2

Catálogo PDF3865–3865; interseção lida 3865–3865; FULL_TEXT_READ.

B2: getter double e setter const double para segundo centro. Pertence a REF-1379; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, B2, p.PDF 3865–3865]

### REF-1382 — Sigma1

Catálogo PDF3866–3866; interseção lida 3866–3866; FULL_TEXT_READ.

Sigma1: getter double e setter const double para primeira curvatura. Pertence a REF-1379; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, Sigma1, p.PDF 3866–3866]

### REF-1383 — Sigma2

Catálogo PDF3866–3866; interseção lida 3866–3866; FULL_TEXT_READ.

Sigma2: getter double e setter const double para segunda curvatura. Pertence a REF-1379; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, Sigma2, p.PDF 3866–3866]

### REF-1384 — GetValue

Catálogo PDF3867–3867; interseção lida 3867–3867; FULL_TEXT_READ.

GetValue(x) retorna grau de pertinência double. Pertence a REF-1379; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, GetValue, p.PDF 3867–3867]

### REF-1385 — CNormalMembershipFunction

Catálogo PDF3868–3871; interseção lida 3868–3871; FULL_TEXT_READ.

Gaussiana simétrica com B centro/Sigma curvatura; exemplo Sigma0.5 tem legenda[5,0.0], inconsistência editorial. Proposta futura exige conferir valores reais. [REF, CNormalMembershipFunction, p.PDF 3868–3871]

### REF-1386 — B

Catálogo PDF3870–3870; interseção lida 3870–3870; FULL_TEXT_READ.

B: getter double e setter const double para centro. Pertence a REF-1385; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, B, p.PDF 3870–3870]

### REF-1387 — Sigma

Catálogo PDF3870–3870; interseção lida 3870–3870; FULL_TEXT_READ.

Sigma: getter double e setter const double para curvatura. Pertence a REF-1385; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, Sigma, p.PDF 3870–3870]

### REF-1388 — GetValue

Catálogo PDF3871–3871; interseção lida 3871–3871; FULL_TEXT_READ.

GetValue(x) retorna grau de pertinência double. Pertence a REF-1385; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, GetValue, p.PDF 3871–3871]

### REF-1389 — CP_ShapedMembershipFunction

Catálogo PDF3872–3876; interseção lida 3872–3876; FULL_TEXT_READ.

Pi curvilínea: A início, B/C núcleo, D fim; transições suaves assimétricas. Proposta futura: validar ordenação dos quatro parâmetros. [REF, CP_ShapedMembershipFunction, p.PDF 3872–3876]

### REF-1390 — A

Catálogo PDF3874–3874; interseção lida 3874–3874; FULL_TEXT_READ.

A: getter double e setter const double para início. Pertence a REF-1389; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, A, p.PDF 3874–3874]

### REF-1391 — B

Catálogo PDF3874–3874; interseção lida 3874–3874; FULL_TEXT_READ.

B: getter double e setter const double para primeiro núcleo. Pertence a REF-1389; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, B, p.PDF 3874–3874]

### REF-1392 — C

Catálogo PDF3875–3876; interseção lida 3875–3876; FULL_TEXT_READ.

C: getter double e setter const double para segundo núcleo. Pertence a REF-1389; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, C, p.PDF 3875–3876]

### REF-1393 — D

Catálogo PDF3875–3876; interseção lida 3875–3876; FULL_TEXT_READ.

D: getter double e setter const double para fim. Pertence a REF-1389; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, D, p.PDF 3875–3876]

### REF-1394 — GetValue

Catálogo PDF3875–3876; interseção lida 3875–3876; FULL_TEXT_READ.

GetValue(x) retorna grau de pertinência double. Pertence a REF-1389; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, GetValue, p.PDF 3875–3876]

### REF-1395 — CProductTwoSigmoidalMembershipFunctions

Catálogo PDF3877–3881; interseção lida 3877–3881; FULL_TEXT_READ.

Produto de duas sigmoides: A1/A2 inclinações e C1/C2 inflexões. Singular/plural de classe varia no texto; confirmar header antes de compilar. [REF, CProductTwoSigmoidalMembershipFunctions, p.PDF 3877–3881]

### REF-1396 — A1

Catálogo PDF3879–3879; interseção lida 3879–3879; FULL_TEXT_READ.

A1: getter double e setter const double para primeira inclinação. Pertence a REF-1395; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, A1, p.PDF 3879–3879]

### REF-1397 — A2

Catálogo PDF3879–3879; interseção lida 3879–3879; FULL_TEXT_READ.

A2: getter double e setter const double para segunda inclinação. Pertence a REF-1395; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, A2, p.PDF 3879–3879]

### REF-1398 — C1

Catálogo PDF3880–3880; interseção lida 3880–3880; FULL_TEXT_READ.

C1: getter double e setter const double para primeira inflexão. Pertence a REF-1395; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, C1, p.PDF 3880–3880]

### REF-1399 — C2

Catálogo PDF3880–3880; interseção lida 3880–3880; FULL_TEXT_READ.

C2: getter double e setter const double para segunda inflexão. Pertence a REF-1395; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, C2, p.PDF 3880–3880]

### REF-1400 — GetValue

Catálogo PDF3881–3881; interseção lida 3881–3881; FULL_TEXT_READ.

GetValue(x) retorna grau de pertinência double. Pertence a REF-1395; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, GetValue, p.PDF 3881–3881]

### REF-1401 — CS_ShapedMembershipFunction

Catálogo PDF3882–3885; interseção lida 3882–3885; FULL_TEXT_READ.

S não decrescente0→1 entre A/B, saturação para termo muito alto. Exemplo inclui A=2/B=1; não presumir validação automática de limites. [REF, CS_ShapedMembershipFunction, p.PDF 3882–3885]

### REF-1402 — A

Catálogo PDF3884–3884; interseção lida 3884–3884; FULL_TEXT_READ.

A: getter double e setter const double para início de aumento. Pertence a REF-1401; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, A, p.PDF 3884–3884]

### REF-1403 — B

Catálogo PDF3884–3884; interseção lida 3884–3884; FULL_TEXT_READ.

B: getter double e setter const double para núcleo. Pertence a REF-1401; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, B, p.PDF 3884–3884]

### REF-1404 — GetValue

Catálogo PDF3885–3885; interseção lida 3885–3885; FULL_TEXT_READ.

GetValue(x) retorna grau de pertinência double. Pertence a REF-1401; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, GetValue, p.PDF 3885–3885]

### REF-1405 — CSigmoidalMembershipFunction

Catálogo PDF3886–3889; interseção lida 3886–3889; FULL_TEXT_READ.

Sigmoide com A inclinação e C inflexão; exemplo A=-2,1,2 mostra que sinal deve ser considerado. Proposta futura de pertinência monotônica. [REF, CSigmoidalMembershipFunction, p.PDF 3886–3889]

### REF-1406 — A

Catálogo PDF3888–3888; interseção lida 3888–3888; FULL_TEXT_READ.

A: getter double e setter const double para inclinação. Pertence a REF-1405; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, A, p.PDF 3888–3888]

### REF-1407 — C

Catálogo PDF3888–3888; interseção lida 3888–3888; FULL_TEXT_READ.

C: getter double e setter const double para inflexão. Pertence a REF-1405; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, C, p.PDF 3888–3888]

### REF-1408 — GetValue

Catálogo PDF3889–3889; interseção lida 3889–3889; FULL_TEXT_READ.

GetValue(x) retorna grau de pertinência double. Pertence a REF-1405; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, GetValue, p.PDF 3889–3889]

### REF-1409 — CTrapezoidMembershipFunction

Catálogo PDF3890–3894; interseção lida 3890–3894; FULL_TEXT_READ.

Trapézio linear por trechos X1…X4 com núcleo intervalar; generaliza triângulo. Exemplo func2 constrói(0,3,7,10), legenda mostra(0,5,7,10). Proposta exige validar fonte, não legenda. [REF, CTrapezoidMembershipFunction, p.PDF 3890–3894]

### REF-1410 — X1

Catálogo PDF3892–3892; interseção lida 3892–3892; FULL_TEXT_READ.

X1: getter double e setter const double para primeira coordenada X. Pertence a REF-1409; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, X1, p.PDF 3892–3892]

### REF-1411 — X2

Catálogo PDF3892–3892; interseção lida 3892–3892; FULL_TEXT_READ.

X2: getter double e setter const double para segunda coordenada X. Pertence a REF-1409; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, X2, p.PDF 3892–3892]

### REF-1412 — X3

Catálogo PDF3893–3893; interseção lida 3893–3893; FULL_TEXT_READ.

X3: getter double e setter const double para terceira coordenada X. Pertence a REF-1409; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, X3, p.PDF 3893–3893]

### REF-1413 — X4

Catálogo PDF3893–3893; interseção lida 3893–3893; FULL_TEXT_READ.

X4: getter double e setter const double para quarta coordenada X. Pertence a REF-1409; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, X4, p.PDF 3893–3893]

### REF-1414 — GetValue

Catálogo PDF3894–3894; interseção lida 3894–3894; FULL_TEXT_READ.

GetValue(x) retorna grau de pertinência double. Pertence a REF-1409; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, GetValue, p.PDF 3894–3894]

### REF-1415 — CTriangularMembershipFunction

Catálogo PDF3895–3899; interseção lida 3895–3899; FULL_TEXT_READ.

Triângulo X1/X2/X3, exemplo com vértices coincidentes(8,8,10); ToNormalMF retorna ponteiro gaussiano. Proposta futura não presume equivalência exata entre curvas. [REF, CTriangularMembershipFunction, p.PDF 3895–3899]

### REF-1416 — X1

Catálogo PDF3897–3897; interseção lida 3897–3897; FULL_TEXT_READ.

X1: getter double e setter const double para primeira coordenada X. Pertence a REF-1415; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, X1, p.PDF 3897–3897]

### REF-1417 — X2

Catálogo PDF3897–3897; interseção lida 3897–3897; FULL_TEXT_READ.

X2: getter double e setter const double para segunda coordenada X. Pertence a REF-1415; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, X2, p.PDF 3897–3897]

### REF-1418 — X3

Catálogo PDF3898–3899; interseção lida 3898–3899; FULL_TEXT_READ.

X3: getter double e setter const double para terceira coordenada X. Pertence a REF-1415; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, X3, p.PDF 3898–3899]

### REF-1419 — ToNormalMF

Catálogo PDF3898–3899; interseção lida 3898–3899; FULL_TEXT_READ.

ToNormalMF retorna CNormalMembershipFunction*. Conversão não documenta erro de aproximação nem responsabilidade de delete nesta página. [REF, ToNormalMF, p.PDF 3898–3899]

### REF-1420 — GetValue

Catálogo PDF3898–3899; interseção lida 3898–3899; FULL_TEXT_READ.

GetValue(x) retorna grau de pertinência double. Pertence a REF-1415; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, GetValue, p.PDF 3898–3899]

### REF-1421 — CZ_ShapedMembershipFunction

Catálogo PDF3900–3903; interseção lida 3900–3903; FULL_TEXT_READ.

Z não crescente1→0 no intervalo A/B, saturação para muito baixo. Exemplo A=2/B=1 também aparece; limites precisam de verificação. [REF, CZ_ShapedMembershipFunction, p.PDF 3900–3903]

### REF-1422 — A

Catálogo PDF3902–3902; interseção lida 3902–3902; FULL_TEXT_READ.

A: getter double e setter const double para início de redução. Pertence a REF-1421; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, A, p.PDF 3902–3902]

### REF-1423 — B

Catálogo PDF3902–3902; interseção lida 3902–3902; FULL_TEXT_READ.

B: getter double e setter const double para fim de redução. Pertence a REF-1421; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, B, p.PDF 3902–3902]

### REF-1424 — GetValue

Catálogo PDF3903–3903; interseção lida 3903–3903; FULL_TEXT_READ.

GetValue(x) retorna grau de pertinência double. Pertence a REF-1421; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, GetValue, p.PDF 3903–3903]

### REF-1425 — IMembershipFunction

Catálogo PDF3904–3904; interseção lida 3904–3904; FULL_TEXT_READ.

Interface básica de pertinência, herda CObject e expõe GetValue. Declaration copiada de CZ_Shaped… é inconsistente; consultar header antes de exemplo. [REF, IMembershipFunction, p.PDF 3904–3904]

### REF-1426 — GetValue

Catálogo PDF3904–3904; interseção lida 3904–3904; FULL_TEXT_READ.

GetValue(x) retorna grau de pertinência double. Pertence a REF-1425; proposta fuzzy futura exige parâmetros rastreáveis e validação independente; não é regra Stoikus atual. [REF, GetValue, p.PDF 3904–3904]

### REF-1427 — Fuzzy systems rules

Catálogo PDF3905–3917; interseção lida 3905–3917; FULL_TEXT_READ.

Regras fuzzy vinculam condição e conclusão; CMamdaniFuzzyRule/CSugenoFuzzyRule, condição simples e composta e base genérica. Não usar como política JPW vigente. [REF, Fuzzy systems rules, p.PDF 3905–3917]

### REF-1428 — CMamdaniFuzzyRule

Catálogo PDF3906–3907; interseção lida 3906–3907; FULL_TEXT_READ.

Mamdani conclui por termo fuzzy e possui Weight double; conclusão CSingleCondition*. Fórmula gráfica ausente não foi reconstruída. [REF, CMamdaniFuzzyRule, p.PDF 3906–3907]

### REF-1429 — Conclusion

Catálogo PDF3906–3906; interseção lida 3906–3906; FULL_TEXT_READ.

Obtém/define ponteiro da conclusão; texto contém grafia CSingleConditon, conferir header. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Conclusion, p.PDF 3906–3906]

### REF-1430 — Weight

Catálogo PDF3907–3907; interseção lida 3907–3907; FULL_TEXT_READ.

Obtém/define peso double da regra Mamdani; faixa[0,1] vem da descrição geral. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Weight, p.PDF 3907–3907]

### REF-1431 — CSugenoFuzzyRule

Catálogo PDF3908–3909; interseção lida 3908–3909; FULL_TEXT_READ.

Sugeno conclui por combinação linear das entradas; Conclusion ponteiro. Texto diz input onde contexto trata output; conferir tipos grafados CSingleConditon. [REF, CSugenoFuzzyRule, p.PDF 3908–3909]

### REF-1432 — Conclusion

Catálogo PDF3908–3909; interseção lida 3908–3909; FULL_TEXT_READ.

Obtém/define ponteiro da conclusão; texto contém grafia CSingleConditon, conferir header. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Conclusion, p.PDF 3908–3909]

### REF-1433 — CSingleCondition

Catálogo PDF3910–3912; interseção lida 3910–3912; FULL_TEXT_READ.

Condição simples liga variável/termo e negação opcional; ponteiros INamedVariable e INamedValue. Proposta futura exige validar correspondência dos termos. [REF, CSingleCondition, p.PDF 3910–3912]

### REF-1434 — Not

Catálogo PDF3910–3910; interseção lida 3910–3910; FULL_TEXT_READ.

Obtém bool/define flag de negação da condição ou conjunto. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Not, p.PDF 3910–3910]

### REF-1435 — Term

Catálogo PDF3911–3912; interseção lida 3911–3912; FULL_TEXT_READ.

Obtém INamedValue*/define por referência ao ponteiro do termo. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Term, p.PDF 3911–3912]

### REF-1436 — Var

Catálogo PDF3911–3912; interseção lida 3911–3912; FULL_TEXT_READ.

Obtém INamedVariable*/define por referência ao ponteiro da variável. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Var, p.PDF 3911–3912]

### REF-1437 — CConditions

Catálogo PDF3913–3914; interseção lida 3913–3914; FULL_TEXT_READ.

Conjunto de condições CList*, Not e Op(and/or); negação do conjunto difere de negar item. Proposta futura deve testar ambas. [REF, CConditions, p.PDF 3913–3914]

### REF-1438 — ConditionsList

Catálogo PDF3913–3913; interseção lida 3913–3913; FULL_TEXT_READ.

Retorna CList* de todas as condições. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, ConditionsList, p.PDF 3913–3913]

### REF-1439 — Not

Catálogo PDF3914–3914; interseção lida 3914–3914; FULL_TEXT_READ.

Obtém bool/define flag de negação da condição ou conjunto. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Not, p.PDF 3914–3914]

### REF-1440 — Op

Catálogo PDF3914–3914; interseção lida 3914–3914; FULL_TEXT_READ.

Obtém/define OperatorType, and ou or. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Op, p.PDF 3914–3914]

### REF-1441 — CGenericFuzzyRule

Catálogo PDF3915–3917; interseção lida 3915–3917; FULL_TEXT_READ.

Base CGenericFuzzyRule: Conclusion, Condition e CreateCondition(var,term[,not[,hedge]]). Protótipos têm grafias CConditons/CSingleConditon e vírgulas; não copiar como compilados. [REF, CGenericFuzzyRule, p.PDF 3915–3917]

### REF-1442 — Conclusion

Catálogo PDF3915–3915; interseção lida 3915–3915; FULL_TEXT_READ.

Obtém/define ponteiro da conclusão; texto contém grafia CSingleConditon, conferir header. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Conclusion, p.PDF 3915–3915]

### REF-1443 — Condition

Catálogo PDF3916–3917; interseção lida 3916–3917; FULL_TEXT_READ.

Obtém/define conjunto de condições do antecedente; ponteiro CConditions com grafia inconsistente no protótipo. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Condition, p.PDF 3916–3917]

### REF-1444 — CreateCondition

Catálogo PDF3916–3917; interseção lida 3916–3917; FULL_TEXT_READ.

Cria CFuzzyCondition* de variável/termo, negação opcional e HedgeType opcional. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, CreateCondition, p.PDF 3916–3917]

### REF-1445 — Fuzzy systems variables

Catálogo PDF3918–3924; interseção lida 3918–3924; FULL_TEXT_READ.

Variáveis linguísticas usam palavras/termos; CFuzzyVariable e CSugenoVariable têm representações de saída distintas. Apenas pesquisa futura. [REF, Fuzzy systems variables, p.PDF 3918–3924]

### REF-1446 — CFuzzyVariable

Catálogo PDF3919–3922; interseção lida 3919–3922; FULL_TEXT_READ.

CFuzzyVariable tem nome, Min/Max e termos; AddTerm/GetTermByName e listas Terms/Values. Min setter rotulado Max no texto: validar API real. [REF, CFuzzyVariable, p.PDF 3919–3922]

### REF-1447 — AddTerm

Catálogo PDF3920–3920; interseção lida 3920–3920; FULL_TEXT_READ.

Adiciona CFuzzyTerm por referência ao ponteiro. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, AddTerm, p.PDF 3920–3920]

### REF-1448 — GetTermByName

Catálogo PDF3920–3920; interseção lida 3920–3920; FULL_TEXT_READ.

Busca CFuzzyTerm* pelo nome string. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, GetTermByName, p.PDF 3920–3920]

### REF-1449 — Max

Catálogo PDF3920–3920; interseção lida 3920–3920; FULL_TEXT_READ.

Obtém/define limite máximo double da variável. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Max, p.PDF 3920–3920]

### REF-1450 — Min

Catálogo PDF3921–3922; interseção lida 3921–3922; FULL_TEXT_READ.

Obtém/define limite mínimo double; título do setter traz Max indevidamente. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Min, p.PDF 3921–3922]

### REF-1451 — Terms

Catálogo PDF3921–3922; interseção lida 3921–3922; FULL_TEXT_READ.

Obtém/define CList* de termos, setter por referência. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Terms, p.PDF 3921–3922]

### REF-1452 — Values

Catálogo PDF3921–3922; interseção lida 3921–3922; FULL_TEXT_READ.

Retorna CList* de termos em CFuzzyVariable ou funções em CSugenoVariable. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Values, p.PDF 3921–3922]

### REF-1453 — CSugenoVariable

Catálogo PDF3923–3924; interseção lida 3923–3924; FULL_TEXT_READ.

CSugenoVariable contém funções lineares em vez de termos fuzzy; Functions/Values retornam CList*, GetFuncByName retorna ISugenoFunction*. Proposta futura exige nomes únicos e checagem de resultado. [REF, CSugenoVariable, p.PDF 3923–3924]

### REF-1454 — Functions

Catálogo PDF3923–3923; interseção lida 3923–3923; FULL_TEXT_READ.

Retorna CList* de funções lineares Sugeno. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Functions, p.PDF 3923–3923]

### REF-1455 — GetFuncByName

Catálogo PDF3924–3924; interseção lida 3924–3924; FULL_TEXT_READ.

Busca ISugenoFunction* pelo nome string. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, GetFuncByName, p.PDF 3924–3924]

### REF-1456 — Values

Catálogo PDF3924–3924; interseção lida 3924–3924; FULL_TEXT_READ.

Retorna CList* de termos em CFuzzyVariable ou funções em CSugenoVariable. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Values, p.PDF 3924–3924]

### REF-1457 — Fuzzy terms

Catálogo PDF3925–3926; interseção lida 3925–3926; FULL_TEXT_READ.

CFuzzyTerm é nome mais função de pertinência; herda CNamedValueImpl. Não confundir nome descritivo com unidade/limite normativo. [REF, Fuzzy terms, p.PDF 3925–3926]

### REF-1458 — MembershipFunction

Catálogo PDF3926–3926; interseção lida 3926–3926; FULL_TEXT_READ.

Retorna IMembershipFunction* do termo. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, MembershipFunction, p.PDF 3926–3926]

### REF-1459 — Fuzzy systems

Catálogo PDF3927–3935; interseção lida 3927–3935; FULL_TEXT_READ.

Modelo fuzzy define entradas/saídas, base e método; pesos[0,1]. Somente proposta de pesquisa sujeita a calibração e validação separada. [REF, Fuzzy systems, p.PDF 3927–3935]

### REF-1460 — Mamdani system

Catálogo PDF3928–3931; interseção lida 3928–3931; FULL_TEXT_READ.

Mamdani fornece agregação, implicação, desfuzzificação, regras parseadas ou vazias e cálculo em listas; outputs fuzzy. Não há método selecionado ou execução nesta leitura. [REF, Mamdani system, p.PDF 3928–3931]

### REF-1461 — AggregationMethod

Catálogo PDF3928–3928; interseção lida 3928–3928; FULL_TEXT_READ.

Define enum AggregationMethod da agregação Mamdani. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, AggregationMethod, p.PDF 3928–3928]

### REF-1462 — Calculate

Catálogo PDF3929–3929; interseção lida 3929–3929; FULL_TEXT_READ.

Calcula inferência recebendo lista de entradas e devolvendo CList*; Sugeno usa referência ao ponteiro. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Calculate, p.PDF 3929–3929]

### REF-1463 — DefuzzificationMethod

Catálogo PDF3929–3929; interseção lida 3929–3929; FULL_TEXT_READ.

Define enum do método de desfuzzificação Mamdani. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, DefuzzificationMethod, p.PDF 3929–3929]

### REF-1464 — EmptyRule

Catálogo PDF3929–3929; interseção lida 3929–3929; FULL_TEXT_READ.

Retorna nova regra vazia Mamdani/Sugeno baseada no sistema atual. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, EmptyRule, p.PDF 3929–3929]

### REF-1465 — ImplicationMethod

Catálogo PDF3929–3929; interseção lida 3929–3929; FULL_TEXT_READ.

Define enum de implicação Mamdani. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, ImplicationMethod, p.PDF 3929–3929]

### REF-1466 — Output

Catálogo PDF3930–3931; interseção lida 3930–3931; FULL_TEXT_READ.

Retorna CList* das variáveis de saída. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Output, p.PDF 3930–3931]

### REF-1467 — OutputByName

Catálogo PDF3930–3931; interseção lida 3930–3931; FULL_TEXT_READ.

Busca CFuzzyVariable* em Mamdani ou CSugenoVariable* em Sugeno por nome. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, OutputByName, p.PDF 3930–3931]

### REF-1468 — ParseRule

Catálogo PDF3930–3931; interseção lida 3930–3931; FULL_TEXT_READ.

Converte string em ponteiro da regra Mamdani/Sugeno. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, ParseRule, p.PDF 3930–3931]

### REF-1469 — Rules

Catálogo PDF3930–3931; interseção lida 3930–3931; FULL_TEXT_READ.

Retorna CList* da base de regras. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Rules, p.PDF 3930–3931]

### REF-1470 — Sugeno system

Catálogo PDF3932–3935; interseção lida 3932–3935; FULL_TEXT_READ.

Sugeno outputs lineares, Calculate CList*, criação por coeficientes ou pares variável/coeficiente; nota explicita W simbólico, não expressão literal. [REF, Sugeno system, p.PDF 3932–3935]

### REF-1471 — Calculate

Catálogo PDF3932–3932; interseção lida 3932–3932; FULL_TEXT_READ.

Calcula inferência recebendo lista de entradas e devolvendo CList*; Sugeno usa referência ao ponteiro. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Calculate, p.PDF 3932–3932]

### REF-1472 — CreateSugenoFunction

Catálogo PDF3933–3933; interseção lida 3933–3933; FULL_TEXT_READ.

CreateSugenoFunction(name,coeffs[]) aceita n coeficientes para n entradas com termo livre0, ou n+1 com último termo livre; overload lista+constValue. Validar ordem antes de proposta. [REF, CreateSugenoFunction, p.PDF 3933–3933]

### REF-1473 — EmptyRule

Catálogo PDF3934–3934; interseção lida 3934–3934; FULL_TEXT_READ.

Retorna nova regra vazia Mamdani/Sugeno baseada no sistema atual. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, EmptyRule, p.PDF 3934–3934]

### REF-1474 — Output

Catálogo PDF3934–3934; interseção lida 3934–3934; FULL_TEXT_READ.

Retorna CList* das variáveis de saída. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Output, p.PDF 3934–3934]

### REF-1475 — OutputByName

Catálogo PDF3934–3934; interseção lida 3934–3934; FULL_TEXT_READ.

Busca CFuzzyVariable* em Mamdani ou CSugenoVariable* em Sugeno por nome. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, OutputByName, p.PDF 3934–3934]

### REF-1476 — ParseRule

Catálogo PDF3934–3934; interseção lida 3934–3934; FULL_TEXT_READ.

Converte string em ponteiro da regra Mamdani/Sugeno. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, ParseRule, p.PDF 3934–3934]

### REF-1477 — Rules

Catálogo PDF3935–3935; interseção lida 3935–3935; FULL_TEXT_READ.

Retorna CList* da base de regras. Proposta futura: verificar ponteiros, nomes, propriedade e resultado; não há uso atual ou execução demonstrados. [REF, Rules, p.PDF 3935–3935]

### REF-1478 — OpenCL

Catálogo PDF3936–3957; interseção lida 3936–3957; FULL_TEXT_READ.

COpenCL wrapper pode acelerar alguns cálculos; exemplos matriz, bitonic sort, FFT e wavelet; recomenda CL separado como recurso. Apenas pesquisa futura: velocidade/GPU do Stoikus não comprovadas. [REF, OpenCL, p.PDF 3936–3957]

### REF-1479 — BufferCreate

Catálogo PDF3938–3938; interseção lida 3938–3938; FULL_TEXT_READ.

BufferCreate(index,size_in_bytes,flags) retorna bool; tamanho é bytes. Proposta OpenCL futura: verificar retornos/capacidade e liberar recursos; sem GPU ou ganho de desempenho comprovados. [REF, BufferCreate, p.PDF 3938–3938]

### REF-1480 — BufferFree

Catálogo PDF3939–3939; interseção lida 3939–3939; FULL_TEXT_READ.

BufferFree(index) elimina buffer, bool. Proposta OpenCL futura: verificar retornos/capacidade e liberar recursos; sem GPU ou ganho de desempenho comprovados. [REF, BufferFree, p.PDF 3939–3939]

### REF-1481 — BufferFromArray

Catálogo PDF3940–3940; interseção lida 3940–3940; FULL_TEXT_READ.

BufferFromArray<T> cria buffer de data[]; data_array_offset descrito em bytes e count em elementos, flags explícitos. Proposta OpenCL futura: verificar retornos/capacidade e liberar recursos; sem GPU ou ganho de desempenho comprovados. [REF, BufferFromArray, p.PDF 3940–3940]

### REF-1482 — BufferRead

Catálogo PDF3941–3941; interseção lida 3941–3941; FULL_TEXT_READ.

BufferRead<T>: cl_buffer_offset em bytes; data_array_offset em índice de elemento; count em valores. Proposta OpenCL futura: verificar retornos/capacidade e liberar recursos; sem GPU ou ganho de desempenho comprovados. [REF, BufferRead, p.PDF 3941–3941]

### REF-1483 — BufferWrite

Catálogo PDF3942–3942; interseção lida 3942–3942; FULL_TEXT_READ.

BufferWrite<T>: offset de buffer em bytes versus offset de array em índice de elemento; count em valores. Proposta OpenCL futura: verificar retornos/capacidade e liberar recursos; sem GPU ou ganho de desempenho comprovados. [REF, BufferWrite, p.PDF 3942–3942]

### REF-1484 — Execute

Catálogo PDF3943–3943; interseção lida 3943–3943; FULL_TEXT_READ.

Execute recebe kernel_index, work_dim, offsets/tamanhos uint[] e opcional local_work_size[]; retorna bool. Proposta OpenCL futura: verificar retornos/capacidade e liberar recursos; sem GPU ou ganho de desempenho comprovados. [REF, Execute, p.PDF 3943–3943]

### REF-1485 — GetContext

Catálogo PDF3944–3944; interseção lida 3944–3944; FULL_TEXT_READ.

GetContext retorna handle int do contexto. Proposta OpenCL futura: verificar retornos/capacidade e liberar recursos; sem GPU ou ganho de desempenho comprovados. [REF, GetContext, p.PDF 3944–3944]

### REF-1486 — GetKernel

Catálogo PDF3945–3945; interseção lida 3945–3945; FULL_TEXT_READ.

GetKernel(index) retorna handle int do kernel. Proposta OpenCL futura: verificar retornos/capacidade e liberar recursos; sem GPU ou ganho de desempenho comprovados. [REF, GetKernel, p.PDF 3945–3945]

### REF-1487 — GetKernelName

Catálogo PDF3946–3946; interseção lida 3946–3946; FULL_TEXT_READ.

GetKernelName(index) retorna nome string do kernel. Proposta OpenCL futura: verificar retornos/capacidade e liberar recursos; sem GPU ou ganho de desempenho comprovados. [REF, GetKernelName, p.PDF 3946–3946]

### REF-1488 — GetProgram

Catálogo PDF3947–3947; interseção lida 3947–3947; FULL_TEXT_READ.

GetProgram retorna handle int do programa. Proposta OpenCL futura: verificar retornos/capacidade e liberar recursos; sem GPU ou ganho de desempenho comprovados. [REF, GetProgram, p.PDF 3947–3947]

### REF-1489 — Initialize

Catálogo PDF3948–3948; interseção lida 3948–3948; FULL_TEXT_READ.

Initialize(program string,show_log=true) retorna bool; descrição chama string de handle, conferir header. Proposta OpenCL futura: verificar retornos/capacidade e liberar recursos; sem GPU ou ganho de desempenho comprovados. [REF, Initialize, p.PDF 3948–3948]

### REF-1490 — KernelCreate

Catálogo PDF3949–3949; interseção lida 3949–3949; FULL_TEXT_READ.

KernelCreate(index,name) cria ponto de entrada, bool. Proposta OpenCL futura: verificar retornos/capacidade e liberar recursos; sem GPU ou ganho de desempenho comprovados. [REF, KernelCreate, p.PDF 3949–3949]

### REF-1491 — KernelFree

Catálogo PDF3950–3950; interseção lida 3950–3950; FULL_TEXT_READ.

KernelFree(index) remove função de entrada, bool. Proposta OpenCL futura: verificar retornos/capacidade e liberar recursos; sem GPU ou ganho de desempenho comprovados. [REF, KernelFree, p.PDF 3950–3950]

### REF-1492 — SetArgument

Catálogo PDF3951–3951; interseção lida 3951–3951; FULL_TEXT_READ.

SetArgument<T>(kernel,arg,value) vincula parâmetro escalar; bool. Proposta OpenCL futura: verificar retornos/capacidade e liberar recursos; sem GPU ou ganho de desempenho comprovados. [REF, SetArgument, p.PDF 3951–3951]

### REF-1493 — SetArgumentBuffer

Catálogo PDF3952–3952; interseção lida 3952–3952; FULL_TEXT_READ.

SetArgumentBuffer(kernel,arg,buffer) vincula buffer por índice; bool. Proposta OpenCL futura: verificar retornos/capacidade e liberar recursos; sem GPU ou ganho de desempenho comprovados. [REF, SetArgumentBuffer, p.PDF 3952–3952]

### REF-1494 — SetArgumentLocalMemory

Catálogo PDF3953–3953; interseção lida 3953–3953; FULL_TEXT_READ.

SetArgumentLocalMemory(kernel,arg,size) reserva argumento em memória local; bool. Proposta OpenCL futura: verificar retornos/capacidade e liberar recursos; sem GPU ou ganho de desempenho comprovados. [REF, SetArgumentLocalMemory, p.PDF 3953–3953]

### REF-1495 — SetBuffersCount

Catálogo PDF3954–3954; interseção lida 3954–3954; FULL_TEXT_READ.

SetBuffersCount(total) define quantidade de buffers, bool. Proposta OpenCL futura: verificar retornos/capacidade e liberar recursos; sem GPU ou ganho de desempenho comprovados. [REF, SetBuffersCount, p.PDF 3954–3954]

### REF-1496 — SetKernelsCount

Catálogo PDF3955–3955; interseção lida 3955–3955; FULL_TEXT_READ.

SetKernelsCount(total) define quantidade de kernels, bool. Proposta OpenCL futura: verificar retornos/capacidade e liberar recursos; sem GPU ou ganho de desempenho comprovados. [REF, SetKernelsCount, p.PDF 3955–3955]

### REF-1497 — Shutdown

Catálogo PDF3956–3956; interseção lida 3956–3956; FULL_TEXT_READ.

Shutdown descarrega programa, void. Proposta OpenCL futura: verificar retornos/capacidade e liberar recursos; sem GPU ou ganho de desempenho comprovados. [REF, Shutdown, p.PDF 3956–3956]

### REF-1498 — SupportDouble

Catálogo PDF3957–3957; interseção lida 3957–3957; FULL_TEXT_READ.

SupportDouble retorna bool; prosa diz floating point genérico apesar do nome. Não presumir float64 pelo texto genérico sem verificar dispositivo. Proposta OpenCL futura: verificar retornos/capacidade e liberar recursos; sem GPU ou ganho de desempenho comprovados. [REF, SupportDouble, p.PDF 3957–3957]

### REF-1499 — Basic Class CObject

Catálogo PDF3958–3969; interseção lida 3958–3969; FULL_TEXT_READ.

CObject é base com links Prev/Next e métodos virtuais. Compare sempre0, Save/Load sempre true sem ação na base: sucesso não comprova persistência. [REF, Basic Class CObject, p.PDF 3958–3969]

### REF-1500 — Prev

Catálogo PDF3959–3959; interseção lida 3959–3959; FULL_TEXT_READ.

Prev getter: retorna CObject* adjacente, NULL na extremidade. Proposta de lista requer links recíprocos e vida útil coerentes; exemplos deletam ambos os objetos explicitamente. [REF, Prev, p.PDF 3959–3959]

### REF-1501 — Prev

Catálogo PDF3960–3960; interseção lida 3960–3960; FULL_TEXT_READ.

Prev setter: define ponteiro CObject* adjacente, void. Proposta de lista requer links recíprocos e vida útil coerentes; exemplos deletam ambos os objetos explicitamente. [REF, Prev, p.PDF 3960–3960]

### REF-1502 — Next

Catálogo PDF3961–3961; interseção lida 3961–3961; FULL_TEXT_READ.

Next getter: retorna CObject* adjacente, NULL na extremidade. Proposta de lista requer links recíprocos e vida útil coerentes; exemplos deletam ambos os objetos explicitamente. [REF, Next, p.PDF 3961–3961]

### REF-1503 — Next

Catálogo PDF3962–3962; interseção lida 3962–3962; FULL_TEXT_READ.

Next setter: define ponteiro CObject* adjacente, void. Proposta de lista requer links recíprocos e vida útil coerentes; exemplos deletam ambos os objetos explicitamente. [REF, Next, p.PDF 3962–3962]

### REF-1504 — Compare

Catálogo PDF3963–3964; interseção lida 3963–3964; FULL_TEXT_READ.

Compare retorna -1/0/1 para menor/igual/maior; implementação base sempre0. Proposta de registros precisa override e comparação por modo coerente. [REF, Compare, p.PDF 3963–3964]

### REF-1505 — Save

Catálogo PDF3965–3966; interseção lida 3965–3966; FULL_TEXT_READ.

Save recebe handle binário e bool; base sempre true e nada grava. Exemplo testa object!=NULL como erro; não reutilizar literalmente. [REF, Save, p.PDF 3965–3966]

### REF-1506 — Load

Catálogo PDF3967–3968; interseção lida 3967–3968; FULL_TEXT_READ.

Load recebe handle binário e bool; base sempre true e nada lê. Exemplo repete checagem!=NULL invertida. Proposta exige override/validação de arquivo. [REF, Load, p.PDF 3967–3968]

### REF-1507 — Type

Catálogo PDF3969–3969; interseção lida 3969–3969; FULL_TEXT_READ.

CObject.Type virtual retorna0 na base. Exemplo aloca objeto duas vezes; evitar copiar vazamento/assumir identidade única. [REF, Type, p.PDF 3969–3969]

### REF-1508 — Data Collections

Catálogo PDF3970–4368; interseção lida 3970–4103; PARTIAL_FULL_TEXT_READ.

Coleções3970–4103 lidas nesta interseção: CArray/Char/Short/Int e início Long; restante até4368 não coberto. [REF, Data Collections, p.PDF 3970–4103]

### REF-1509 — CArray

Catálogo PDF3971–3983; interseção lida 3971–3983; FULL_TEXT_READ.

CArray base administra capacidade, ordenação e arquivos. Total, Available e Max são grandezas distintas; Clear preserva alocação. Proposta para buffers requer limites e testes de falha. [REF, CArray, p.PDF 3971–3983]

### REF-1510 — Step

Catálogo PDF3973–3973; interseção lida 3973–3973; FULL_TEXT_READ.

Step() retorna incremento de alocação int. Proposta: medir realocação antes de escolher crescimento. [REF, Step, p.PDF 3973–3973]

### REF-1511 — Step

Catálogo PDF3974–3974; interseção lida 3974–3974; FULL_TEXT_READ.

Step(int) rejeita<=0 com false; define incremento. Proposta para buffers não confundir passo de memória com passo temporal. [REF, Step, p.PDF 3974–3974]

### REF-1512 — Total

Catálogo PDF3975–3975; interseção lida 3975–3975; FULL_TEXT_READ.

Total() retorna número de elementos ativos int. Iteração proposta deve respeitar Total e não capacidade. [REF, Total, p.PDF 3975–3975]

### REF-1513 — Available

Catálogo PDF3976–3976; interseção lida 3976–3976; FULL_TEXT_READ.

Available() retorna lugares livres sem nova alocação. Não representa dados válidos. [REF, Available, p.PDF 3976–3976]

### REF-1514 — Max

Catálogo PDF3977–3977; interseção lida 3977–3977; FULL_TEXT_READ.

Max() retorna tamanho máximo atual sem realocação. Não é limite universal de plataforma. [REF, Max, p.PDF 3977–3977]

### REF-1515 — IsSorted

Catálogo PDF3978–3978; interseção lida 3978–3978; FULL_TEXT_READ.

IsSorted(mode) verifica flag do modo; Sort ativa, add/insert resetam exceto InsertSort. Proposta: não fazer busca ordenada após mutação comum. [REF, IsSorted, p.PDF 3978–3978]

### REF-1516 — SortMode

Catálogo PDF3979–3979; interseção lida 3979–3979; FULL_TEXT_READ.

SortMode() retorna modo de ordenação int. Proposta registra critério para comparações coerentes. [REF, SortMode, p.PDF 3979–3979]

### REF-1517 — Clear

Catálogo PDF3980–3980; interseção lida 3980–3980; FULL_TEXT_READ.

Clear() elimina elementos sem liberar memória. Proposta reutiliza buffer mas precisa Shutdown para liberar capacidade. [REF, Clear, p.PDF 3980–3980]

### REF-1518 — Sort

Catálogo PDF3981–3981; interseção lida 3981–3981; FULL_TEXT_READ.

Sort é sempre crescente; mode ignorado em primitivas e comparação multivariada exige implementação em objetos. Não obter decrescente mudando mode de primitivas. [REF, Sort, p.PDF 3981–3981]

### REF-1519 — Save

Catálogo PDF3982–3982; interseção lida 3982–3982; FULL_TEXT_READ.

CArray.Save virtual com handle binário/bool; exemplo trata array!=NULL como erro. Proposta exige conferir implementação derivada e conteúdo, não só bool. [REF, Save, p.PDF 3982–3982]

### REF-1520 — Load

Catálogo PDF3983–3983; interseção lida 3983–3983; FULL_TEXT_READ.

CArray.Load virtual com handle binário/bool; exemplo checa!=NULL como erro. Proposta exige roundtrip e validação de estado carregado. [REF, Load, p.PDF 3983–3983]

### REF-1521 — CArrayChar

Catálogo PDF3984–4020; interseção lida 3984–4020; FULL_TEXT_READ.

CArrayChar armazena char/uchar com mutação, buscas, persistência; Type documentado77. Proposta para bytes deve conferir signedness e não usar para preço. [REF, CArrayChar, p.PDF 3984–4020]

### REF-1522 — Reserve

Catálogo PDF3986–3986; interseção lida 3986–3986; FULL_TEXT_READ.

CArrayChar.Reserve: Reserva quantidade adicional size; false para<=0 ou falha; crescimento em Step ou padrão16. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Reserve, p.PDF 3986–3986]

### REF-1523 — Resize

Catálogo PDF3987–3987; interseção lida 3987–3987; FULL_TEXT_READ.

CArrayChar.Resize: Reduz tamanho para size>=0; perde elementos à direita; alocação ajustada por Step/padrão16. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Resize, p.PDF 3987–3987]

### REF-1524 — Shutdown

Catálogo PDF3988–3988; interseção lida 3988–3988; FULL_TEXT_READ.

CArrayChar.Shutdown: Limpa e libera totalmente memória; bool, distinto de Clear. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Shutdown, p.PDF 3988–3988]

### REF-1525 — Add

Catálogo PDF3989–3989; interseção lida 3989–3989; FULL_TEXT_READ.

CArrayChar.Add: Acrescenta um elemento ao fim; bool. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Add, p.PDF 3989–3989]

### REF-1526 — AddArray

Catálogo PDF3990–3990; interseção lida 3990–3990; FULL_TEXT_READ.

CArrayChar.AddArray: Acrescenta todos os elementos de array nativo const ou instância const por ponteiro; bool, não alias de propriedade. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, AddArray, p.PDF 3990–3990]

### REF-1527 — AddArray

Catálogo PDF3991–3992; interseção lida 3991–3992; FULL_TEXT_READ.

CArrayChar.AddArray: Acrescenta todos os elementos de array nativo const ou instância const por ponteiro; bool, não alias de propriedade. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, AddArray, p.PDF 3991–3992]

### REF-1528 — Insert

Catálogo PDF3993–3993; interseção lida 3993–3993; FULL_TEXT_READ.

CArrayChar.Insert: Insere(element,pos), bool; deslocamento afeta índices de origem. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Insert, p.PDF 3993–3993]

### REF-1529 — InsertArray

Catálogo PDF3994–3994; interseção lida 3994–3994; FULL_TEXT_READ.

CArrayChar.InsertArray: Insere fonte nativa ou ponteiro em pos, bool; não confundir com substituição. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, InsertArray, p.PDF 3994–3994]

### REF-1530 — InsertArray

Catálogo PDF3995–3996; interseção lida 3995–3996; FULL_TEXT_READ.

CArrayChar.InsertArray: Insere fonte nativa ou ponteiro em pos, bool; não confundir com substituição. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, InsertArray, p.PDF 3995–3996]

### REF-1531 — AssignArray

Catálogo PDF3997–3997; interseção lida 3997–3997; FULL_TEXT_READ.

CArrayChar.AssignArray: Copia elementos da fonte nativa const ou objeto const; bool; fonte continua com vida independente nos exemplos. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, AssignArray, p.PDF 3997–3997]

### REF-1532 — AssignArray

Catálogo PDF3998–3999; interseção lida 3998–3999; FULL_TEXT_READ.

CArrayChar.AssignArray: Copia elementos da fonte nativa const ou objeto const; bool; fonte continua com vida independente nos exemplos. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, AssignArray, p.PDF 3998–3999]

### REF-1533 — Update

Catálogo PDF4000–4000; interseção lida 4000–4000; FULL_TEXT_READ.

CArrayChar.Update: Substitui(pos,element), bool; validar posição e estado de ordenação. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Update, p.PDF 4000–4000]

### REF-1534 — Shift

Catálogo PDF4001–4001; interseção lida 4001–4001; FULL_TEXT_READ.

CArrayChar.Shift: Move elemento em pos por shift positivo/negativo; bool; não é deslocamento de todos os valores. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Shift, p.PDF 4001–4001]

### REF-1535 — Delete

Catálogo PDF4002–4002; interseção lida 4002–4002; FULL_TEXT_READ.

CArrayChar.Delete: Remove posição pos, bool; índices posteriores mudam. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Delete, p.PDF 4002–4002]

### REF-1536 — DeleteRange

Catálogo PDF4003–4003; interseção lida 4003–4003; FULL_TEXT_READ.

CArrayChar.DeleteRange: Remove grupo entre from e to, bool; proposta deve testar extremos/inclusão antes de implementação. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, DeleteRange, p.PDF 4003–4003]

### REF-1537 — At

Catálogo PDF4004–4005; interseção lida 4004–4005; FULL_TEXT_READ.

CArrayChar.At: Retorna valor em pos ou sentinela CHAR_MAX com ERR_OUT_OF_RANGE; sentinela também pode ser dado válido, exigir GetLastError. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, At, p.PDF 4004–4005]

### REF-1538 — CompareArray

Catálogo PDF4006–4006; interseção lida 4006–4006; FULL_TEXT_READ.

CArrayChar.CompareArray: Retorna bool de igualdade com fonte nativa const ou objeto const; não é comparador -1/0/1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, CompareArray, p.PDF 4006–4006]

### REF-1539 — CompareArray

Catálogo PDF4007–4007; interseção lida 4007–4007; FULL_TEXT_READ.

CArrayChar.CompareArray: Retorna bool de igualdade com fonte nativa const ou objeto const; não é comparador -1/0/1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, CompareArray, p.PDF 4007–4007]

### REF-1540 — InsertSort

Catálogo PDF4008–4008; interseção lida 4008–4008; FULL_TEXT_READ.

CArrayChar.InsertSort: Insere um elemento mantendo array ordenado, bool; exemplo chama Sort antes. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, InsertSort, p.PDF 4008–4008]

### REF-1541 — Search

Catálogo PDF4009–4009; interseção lida 4009–4009; FULL_TEXT_READ.

CArrayChar.Search: Busca igualdade em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Search, p.PDF 4009–4009]

### REF-1542 — SearchGreat

Catálogo PDF4010–4010; interseção lida 4010–4010; FULL_TEXT_READ.

CArrayChar.SearchGreat: Busca valor estritamente maior em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchGreat, p.PDF 4010–4010]

### REF-1543 — SearchLess

Catálogo PDF4011–4011; interseção lida 4011–4011; FULL_TEXT_READ.

CArrayChar.SearchLess: Busca valor estritamente menor em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchLess, p.PDF 4011–4011]

### REF-1544 — SearchGreatOrEqual

Catálogo PDF4012–4012; interseção lida 4012–4012; FULL_TEXT_READ.

CArrayChar.SearchGreatOrEqual: Busca maior ou igual em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchGreatOrEqual, p.PDF 4012–4012]

### REF-1545 — SearchLessOrEqual

Catálogo PDF4013–4013; interseção lida 4013–4013; FULL_TEXT_READ.

CArrayChar.SearchLessOrEqual: Busca menor ou igual em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchLessOrEqual, p.PDF 4013–4013]

### REF-1546 — SearchFirst

Catálogo PDF4014–4014; interseção lida 4014–4014; FULL_TEXT_READ.

CArrayChar.SearchFirst: Busca primeira ocorrência igual em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchFirst, p.PDF 4014–4014]

### REF-1547 — SearchLast

Catálogo PDF4015–4015; interseção lida 4015–4015; FULL_TEXT_READ.

CArrayChar.SearchLast: Busca última ocorrência igual em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchLast, p.PDF 4015–4015]

### REF-1548 — SearchLinear

Catálogo PDF4016–4016; interseção lida 4016–4016; FULL_TEXT_READ.

CArrayChar.SearchLinear: Busca sequencial em array não ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchLinear, p.PDF 4016–4016]

### REF-1549 — Save

Catálogo PDF4017–4017; interseção lida 4017–4017; FULL_TEXT_READ.

CArrayChar.Save: Persiste em handle binário aberto; bool. Exemplo tem guarda array!=NULL como erro, não copiar sem correção/verificação. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Save, p.PDF 4017–4017]

### REF-1550 — Load

Catálogo PDF4018–4019; interseção lida 4018–4019; FULL_TEXT_READ.

CArrayChar.Load: Carrega de handle binário aberto; bool. Exemplo tem guarda array!=NULL como erro; validar integridade antes de uso. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Load, p.PDF 4018–4019]

### REF-1551 — Type

Catálogo PDF4020–4020; interseção lida 4020–4020; FULL_TEXT_READ.

CArrayChar.Type: Retorna identificador virtual de tipo; documento mostra77 para Char e82 para Short/Int, insuficiente para discriminar ambos sem conferir header. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Type, p.PDF 4020–4020]

### REF-1552 — CArrayShort

Catálogo PDF4021–4059; interseção lida 4021–4059; FULL_TEXT_READ.

CArrayShort armazena short/ushort, mesmas famílias operacionais; Type documentado82. Proposta para códigos exige faixa e conversões explícitas. [REF, CArrayShort, p.PDF 4021–4059]

### REF-1553 — Reserve

Catálogo PDF4024–4024; interseção lida 4024–4024; FULL_TEXT_READ.

CArrayShort.Reserve: Reserva quantidade adicional size; false para<=0 ou falha; crescimento em Step ou padrão16. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Reserve, p.PDF 4024–4024]

### REF-1554 — Resize

Catálogo PDF4025–4025; interseção lida 4025–4025; FULL_TEXT_READ.

CArrayShort.Resize: Reduz tamanho para size>=0; perde elementos à direita; alocação ajustada por Step/padrão16. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Resize, p.PDF 4025–4025]

### REF-1555 — Shutdown

Catálogo PDF4026–4026; interseção lida 4026–4026; FULL_TEXT_READ.

CArrayShort.Shutdown: Limpa e libera totalmente memória; bool, distinto de Clear. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Shutdown, p.PDF 4026–4026]

### REF-1556 — Add

Catálogo PDF4027–4027; interseção lida 4027–4027; FULL_TEXT_READ.

CArrayShort.Add: Acrescenta um elemento ao fim; bool. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Add, p.PDF 4027–4027]

### REF-1557 — AddArray

Catálogo PDF4028–4028; interseção lida 4028–4028; FULL_TEXT_READ.

CArrayShort.AddArray: Acrescenta todos os elementos de array nativo const ou instância const por ponteiro; bool, não alias de propriedade. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, AddArray, p.PDF 4028–4028]

### REF-1558 — AddArray

Catálogo PDF4029–4030; interseção lida 4029–4030; FULL_TEXT_READ.

CArrayShort.AddArray: Acrescenta todos os elementos de array nativo const ou instância const por ponteiro; bool, não alias de propriedade. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, AddArray, p.PDF 4029–4030]

### REF-1559 — Insert

Catálogo PDF4031–4031; interseção lida 4031–4031; FULL_TEXT_READ.

CArrayShort.Insert: Insere(element,pos), bool; deslocamento afeta índices de origem. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Insert, p.PDF 4031–4031]

### REF-1560 — InsertArray

Catálogo PDF4032–4032; interseção lida 4032–4032; FULL_TEXT_READ.

CArrayShort.InsertArray: Insere fonte nativa ou ponteiro em pos, bool; não confundir com substituição. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, InsertArray, p.PDF 4032–4032]

### REF-1561 — InsertArray

Catálogo PDF4033–4034; interseção lida 4033–4034; FULL_TEXT_READ.

CArrayShort.InsertArray: Insere fonte nativa ou ponteiro em pos, bool; não confundir com substituição. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, InsertArray, p.PDF 4033–4034]

### REF-1562 — AssignArray

Catálogo PDF4035–4035; interseção lida 4035–4035; FULL_TEXT_READ.

CArrayShort.AssignArray: Copia elementos da fonte nativa const ou objeto const; bool; fonte continua com vida independente nos exemplos. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, AssignArray, p.PDF 4035–4035]

### REF-1563 — AssignArray

Catálogo PDF4036–4037; interseção lida 4036–4037; FULL_TEXT_READ.

CArrayShort.AssignArray: Copia elementos da fonte nativa const ou objeto const; bool; fonte continua com vida independente nos exemplos. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, AssignArray, p.PDF 4036–4037]

### REF-1564 — Update

Catálogo PDF4038–4038; interseção lida 4038–4038; FULL_TEXT_READ.

CArrayShort.Update: Substitui(pos,element), bool; validar posição e estado de ordenação. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Update, p.PDF 4038–4038]

### REF-1565 — Shift

Catálogo PDF4039–4039; interseção lida 4039–4039; FULL_TEXT_READ.

CArrayShort.Shift: Move elemento em pos por shift positivo/negativo; bool; não é deslocamento de todos os valores. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Shift, p.PDF 4039–4039]

### REF-1566 — Delete

Catálogo PDF4040–4040; interseção lida 4040–4040; FULL_TEXT_READ.

CArrayShort.Delete: Remove posição pos, bool; índices posteriores mudam. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Delete, p.PDF 4040–4040]

### REF-1567 — DeleteRange

Catálogo PDF4041–4041; interseção lida 4041–4041; FULL_TEXT_READ.

CArrayShort.DeleteRange: Remove grupo entre from e to, bool; proposta deve testar extremos/inclusão antes de implementação. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, DeleteRange, p.PDF 4041–4041]

### REF-1568 — At

Catálogo PDF4042–4043; interseção lida 4042–4043; FULL_TEXT_READ.

CArrayShort.At: Retorna valor em pos ou sentinela SHORT_MAX com ERR_OUT_OF_RANGE; sentinela também pode ser dado válido, exigir GetLastError. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, At, p.PDF 4042–4043]

### REF-1569 — CompareArray

Catálogo PDF4044–4044; interseção lida 4044–4044; FULL_TEXT_READ.

CArrayShort.CompareArray: Retorna bool de igualdade com fonte nativa const ou objeto const; não é comparador -1/0/1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, CompareArray, p.PDF 4044–4044]

### REF-1570 — CompareArray

Catálogo PDF4045–4045; interseção lida 4045–4045; FULL_TEXT_READ.

CArrayShort.CompareArray: Retorna bool de igualdade com fonte nativa const ou objeto const; não é comparador -1/0/1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, CompareArray, p.PDF 4045–4045]

### REF-1571 — InsertSort

Catálogo PDF4046–4046; interseção lida 4046–4046; FULL_TEXT_READ.

CArrayShort.InsertSort: Insere um elemento mantendo array ordenado, bool; exemplo chama Sort antes. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, InsertSort, p.PDF 4046–4046]

### REF-1572 — Search

Catálogo PDF4047–4047; interseção lida 4047–4047; FULL_TEXT_READ.

CArrayShort.Search: Busca igualdade em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Search, p.PDF 4047–4047]

### REF-1573 — SearchGreat

Catálogo PDF4048–4048; interseção lida 4048–4048; FULL_TEXT_READ.

CArrayShort.SearchGreat: Busca valor estritamente maior em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchGreat, p.PDF 4048–4048]

### REF-1574 — SearchLess

Catálogo PDF4049–4049; interseção lida 4049–4049; FULL_TEXT_READ.

CArrayShort.SearchLess: Busca valor estritamente menor em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchLess, p.PDF 4049–4049]

### REF-1575 — SearchGreatOrEqual

Catálogo PDF4050–4050; interseção lida 4050–4050; FULL_TEXT_READ.

CArrayShort.SearchGreatOrEqual: Busca maior ou igual em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchGreatOrEqual, p.PDF 4050–4050]

### REF-1576 — SearchLessOrEqual

Catálogo PDF4051–4051; interseção lida 4051–4051; FULL_TEXT_READ.

CArrayShort.SearchLessOrEqual: Busca menor ou igual em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchLessOrEqual, p.PDF 4051–4051]

### REF-1577 — SearchFirst

Catálogo PDF4052–4052; interseção lida 4052–4052; FULL_TEXT_READ.

CArrayShort.SearchFirst: Busca primeira ocorrência igual em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchFirst, p.PDF 4052–4052]

### REF-1578 — SearchLast

Catálogo PDF4053–4053; interseção lida 4053–4053; FULL_TEXT_READ.

CArrayShort.SearchLast: Busca última ocorrência igual em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchLast, p.PDF 4053–4053]

### REF-1579 — SearchLinear

Catálogo PDF4054–4054; interseção lida 4054–4054; FULL_TEXT_READ.

CArrayShort.SearchLinear: Busca sequencial em array não ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchLinear, p.PDF 4054–4054]

### REF-1580 — Save

Catálogo PDF4055–4056; interseção lida 4055–4056; FULL_TEXT_READ.

CArrayShort.Save: Persiste em handle binário aberto; bool. Exemplo tem guarda array!=NULL como erro, não copiar sem correção/verificação. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Save, p.PDF 4055–4056]

### REF-1581 — Load

Catálogo PDF4057–4058; interseção lida 4057–4058; FULL_TEXT_READ.

CArrayShort.Load: Carrega de handle binário aberto; bool. Exemplo tem guarda array!=NULL como erro; validar integridade antes de uso. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Load, p.PDF 4057–4058]

### REF-1582 — Type

Catálogo PDF4059–4059; interseção lida 4059–4059; FULL_TEXT_READ.

CArrayShort.Type: Retorna identificador virtual de tipo; documento mostra77 para Char e82 para Short/Int, insuficiente para discriminar ambos sem conferir header. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Type, p.PDF 4059–4059]

### REF-1583 — CArrayInt

Catálogo PDF4060–4098; interseção lida 4060–4098; FULL_TEXT_READ.

CArrayInt armazena int/uint; CSpreadBuffer descendente listado; Type documentado82 coincide com Short neste texto. Não usar número como discriminador único sem conferir headers. [REF, CArrayInt, p.PDF 4060–4098]

### REF-1584 — Reserve

Catálogo PDF4063–4063; interseção lida 4063–4063; FULL_TEXT_READ.

CArrayInt.Reserve: Reserva quantidade adicional size; false para<=0 ou falha; crescimento em Step ou padrão16. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Reserve, p.PDF 4063–4063]

### REF-1585 — Resize

Catálogo PDF4064–4064; interseção lida 4064–4064; FULL_TEXT_READ.

CArrayInt.Resize: Reduz tamanho para size>=0; perde elementos à direita; alocação ajustada por Step/padrão16. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Resize, p.PDF 4064–4064]

### REF-1586 — Shutdown

Catálogo PDF4065–4065; interseção lida 4065–4065; FULL_TEXT_READ.

CArrayInt.Shutdown: Limpa e libera totalmente memória; bool, distinto de Clear. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Shutdown, p.PDF 4065–4065]

### REF-1587 — Add

Catálogo PDF4066–4066; interseção lida 4066–4066; FULL_TEXT_READ.

CArrayInt.Add: Acrescenta um elemento ao fim; bool. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Add, p.PDF 4066–4066]

### REF-1588 — AddArray

Catálogo PDF4067–4067; interseção lida 4067–4067; FULL_TEXT_READ.

CArrayInt.AddArray: Acrescenta todos os elementos de array nativo const ou instância const por ponteiro; bool, não alias de propriedade. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, AddArray, p.PDF 4067–4067]

### REF-1589 — AddArray

Catálogo PDF4068–4069; interseção lida 4068–4069; FULL_TEXT_READ.

CArrayInt.AddArray: Acrescenta todos os elementos de array nativo const ou instância const por ponteiro; bool, não alias de propriedade. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, AddArray, p.PDF 4068–4069]

### REF-1590 — Insert

Catálogo PDF4070–4070; interseção lida 4070–4070; FULL_TEXT_READ.

CArrayInt.Insert: Insere(element,pos), bool; deslocamento afeta índices de origem. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Insert, p.PDF 4070–4070]

### REF-1591 — InsertArray

Catálogo PDF4071–4071; interseção lida 4071–4071; FULL_TEXT_READ.

CArrayInt.InsertArray: Insere fonte nativa ou ponteiro em pos, bool; não confundir com substituição. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, InsertArray, p.PDF 4071–4071]

### REF-1592 — InsertArray

Catálogo PDF4072–4073; interseção lida 4072–4073; FULL_TEXT_READ.

CArrayInt.InsertArray: Insere fonte nativa ou ponteiro em pos, bool; não confundir com substituição. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, InsertArray, p.PDF 4072–4073]

### REF-1593 — AssignArray

Catálogo PDF4074–4074; interseção lida 4074–4074; FULL_TEXT_READ.

CArrayInt.AssignArray: Copia elementos da fonte nativa const ou objeto const; bool; fonte continua com vida independente nos exemplos. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, AssignArray, p.PDF 4074–4074]

### REF-1594 — AssignArray

Catálogo PDF4075–4076; interseção lida 4075–4076; FULL_TEXT_READ.

CArrayInt.AssignArray: Copia elementos da fonte nativa const ou objeto const; bool; fonte continua com vida independente nos exemplos. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, AssignArray, p.PDF 4075–4076]

### REF-1595 — Update

Catálogo PDF4077–4077; interseção lida 4077–4077; FULL_TEXT_READ.

CArrayInt.Update: Substitui(pos,element), bool; validar posição e estado de ordenação. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Update, p.PDF 4077–4077]

### REF-1596 — Shift

Catálogo PDF4078–4078; interseção lida 4078–4078; FULL_TEXT_READ.

CArrayInt.Shift: Move elemento em pos por shift positivo/negativo; bool; não é deslocamento de todos os valores. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Shift, p.PDF 4078–4078]

### REF-1597 — Delete

Catálogo PDF4079–4079; interseção lida 4079–4079; FULL_TEXT_READ.

CArrayInt.Delete: Remove posição pos, bool; índices posteriores mudam. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Delete, p.PDF 4079–4079]

### REF-1598 — DeleteRange

Catálogo PDF4080–4080; interseção lida 4080–4080; FULL_TEXT_READ.

CArrayInt.DeleteRange: Remove grupo entre from e to, bool; proposta deve testar extremos/inclusão antes de implementação. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, DeleteRange, p.PDF 4080–4080]

### REF-1599 — At

Catálogo PDF4081–4082; interseção lida 4081–4082; FULL_TEXT_READ.

CArrayInt.At: Retorna valor em pos ou sentinela INT_MAX com ERR_OUT_OF_RANGE; sentinela também pode ser dado válido, exigir GetLastError. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, At, p.PDF 4081–4082]

### REF-1600 — CompareArray

Catálogo PDF4083–4083; interseção lida 4083–4083; FULL_TEXT_READ.

CArrayInt.CompareArray: Retorna bool de igualdade com fonte nativa const ou objeto const; não é comparador -1/0/1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, CompareArray, p.PDF 4083–4083]

### REF-1601 — CompareArray

Catálogo PDF4084–4084; interseção lida 4084–4084; FULL_TEXT_READ.

CArrayInt.CompareArray: Retorna bool de igualdade com fonte nativa const ou objeto const; não é comparador -1/0/1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, CompareArray, p.PDF 4084–4084]

### REF-1602 — InsertSort

Catálogo PDF4085–4085; interseção lida 4085–4085; FULL_TEXT_READ.

CArrayInt.InsertSort: Insere um elemento mantendo array ordenado, bool; exemplo chama Sort antes. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, InsertSort, p.PDF 4085–4085]

### REF-1603 — Search

Catálogo PDF4086–4086; interseção lida 4086–4086; FULL_TEXT_READ.

CArrayInt.Search: Busca igualdade em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Search, p.PDF 4086–4086]

### REF-1604 — SearchGreat

Catálogo PDF4087–4087; interseção lida 4087–4087; FULL_TEXT_READ.

CArrayInt.SearchGreat: Busca valor estritamente maior em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchGreat, p.PDF 4087–4087]

### REF-1605 — SearchLess

Catálogo PDF4088–4088; interseção lida 4088–4088; FULL_TEXT_READ.

CArrayInt.SearchLess: Busca valor estritamente menor em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchLess, p.PDF 4088–4088]

### REF-1606 — SearchGreatOrEqual

Catálogo PDF4089–4089; interseção lida 4089–4089; FULL_TEXT_READ.

CArrayInt.SearchGreatOrEqual: Busca maior ou igual em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchGreatOrEqual, p.PDF 4089–4089]

### REF-1607 — SearchLessOrEqual

Catálogo PDF4090–4090; interseção lida 4090–4090; FULL_TEXT_READ.

CArrayInt.SearchLessOrEqual: Busca menor ou igual em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchLessOrEqual, p.PDF 4090–4090]

### REF-1608 — SearchFirst

Catálogo PDF4091–4091; interseção lida 4091–4091; FULL_TEXT_READ.

CArrayInt.SearchFirst: Busca primeira ocorrência igual em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchFirst, p.PDF 4091–4091]

### REF-1609 — SearchLast

Catálogo PDF4092–4092; interseção lida 4092–4092; FULL_TEXT_READ.

CArrayInt.SearchLast: Busca última ocorrência igual em array ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchLast, p.PDF 4092–4092]

### REF-1610 — SearchLinear

Catálogo PDF4093–4093; interseção lida 4093–4093; FULL_TEXT_READ.

CArrayInt.SearchLinear: Busca sequencial em array não ordenado; índice ou -1. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, SearchLinear, p.PDF 4093–4093]

### REF-1611 — Save

Catálogo PDF4094–4095; interseção lida 4094–4095; FULL_TEXT_READ.

CArrayInt.Save: Persiste em handle binário aberto; bool. Exemplo tem guarda array!=NULL como erro, não copiar sem correção/verificação. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Save, p.PDF 4094–4095]

### REF-1612 — Load

Catálogo PDF4096–4097; interseção lida 4096–4097; FULL_TEXT_READ.

CArrayInt.Load: Carrega de handle binário aberto; bool. Exemplo tem guarda array!=NULL como erro; validar integridade antes de uso. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Load, p.PDF 4096–4097]

### REF-1613 — Type

Catálogo PDF4098–4098; interseção lida 4098–4098; FULL_TEXT_READ.

CArrayInt.Type: Retorna identificador virtual de tipo; documento mostra77 para Char e82 para Short/Int, insuficiente para discriminar ambos sem conferir header. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Type, p.PDF 4098–4098]

### REF-1614 — CArrayLong

Catálogo PDF4099–4137; interseção lida 4099–4103; PARTIAL_FULL_TEXT_READ.

Somente4099–4103 de CArrayLong: long/ulong, descendentes volume/tempo, catálogo e Reserve/Resize lidos. Métodos detalhados posteriores não lidos; apropriado pesquisar inteiros largos sem truncar timestamps/tickets. [REF, CArrayLong, p.PDF 4099–4103]

### REF-1615 — Reserve

Catálogo PDF4102–4102; interseção lida 4102–4102; FULL_TEXT_READ.

CArrayLong.Reserve: Reserva quantidade adicional size; false para<=0 ou falha; crescimento em Step ou padrão16. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Reserve, p.PDF 4102–4102]

### REF-1616 — Resize

Catálogo PDF4103–4103; interseção lida 4103–4103; FULL_TEXT_READ.

CArrayLong.Resize: Reduz tamanho para size>=0; perde elementos à direita; alocação ajustada por Step/padrão16. Proposta de buffer Stoikus exige tipo/faixa e retorno checados; uso atual não demonstrado por esta leitura. [REF, Resize, p.PDF 4103–4103]
