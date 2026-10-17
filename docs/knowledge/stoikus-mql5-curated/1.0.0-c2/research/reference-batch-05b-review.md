# REF — lote05b: continuação independente PDF1391–1586

Leitura semântica integral do corpo textual das196 páginas realizada nesta rodada em12 lotes de no máximo29000 caracteres, sem truncamento dos outputs de corpo. Notas batch05 foram consultadas apenas para localizar fronteira; não reivindico sua leitura anterior1195–1390. Todas as páginas são físicas PDF. Exemplos MQL/Python: NOT_RUN. Visuais e fórmulas renderizadas não foram automaticamente verificados; texto extraído possui linhas longas cortadas na origem. Sem alteração de produto, kit, piloto ou arquivos batch05.

Aplicabilidade geral: este intervalo é referência matemática e pesquisa futura. Nenhum uso atual dessas APIs no Stoikus foi confirmado nesta rodada. Propostas abaixo não autorizam ML ou substituição de cálculo financeiro.

## REF-0001 — MQL5 Reference (PDF74–7284; lido 1391–1586)

Contêiner da referência: somente a interseção1391–1586 foi lida nesta rodada; não implica leitura integral do livro.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0277 — Matrix and Vector Methods (PDF1287–1878; lido 1391–1586)

Matrizes/vetores: esta continuação cobre produtos, decomposições, estatística, classificação estrutural, sistemas e ML/OpenBLAS. Capítulo continua até1878; não declarar conclusão global.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0328 — Products (PDF1385–1419; lido 1391–1419)

Continuação de Products: produtos escalar, interno, externo, Kronecker, correlação/covariância e convolução têm formas e semânticas diferentes; não são operações intercambiáveis.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0330 — GeMM (PDF1391–1394; lido 1391–1394)

GeMM calcula C←alpha AB+beta C no objeto existente; pré-alocação evita realocação para tamanhos iguais. Primeira chamada aloca/zera quando necessário. Quatro sobrecargas, vetor×vetor produz matriz, diferente de MatMul escalar; flags transposição A/B/C e bool de sucesso. Validar formas e flags antes de reuso.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0331 — Power (PDF1395–1397; lido 1395–1397)

Power exige matriz quadrada, expoente inteiro positivo/zero/negativo; zero identidade, negativo inverte. Saída MQL Power(-3) impressa conflita com saída Python e com álgebra do exemplo; não tomar resultado publicado como oráculo.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0332 — Dot (PDF1398–1399; lido 1398–1399)

Dot de vetores retorna escalar; exemplo soma produtos apenas quando tamanhos iguais, mas esse fallback zero é do algoritmo ilustrativo, não contrato documentado de erro da API. Dot matricial corresponde a MatMul.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0333 — Kron (PDF1400–1401; lido 1400–1401)

Kron retorna matriz para combinações matriz/vetor; produto em blocos, forma de matrizes MxN e PxQ vira MPxNQ. Controlar explosão de memória.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0334 — Inner (PDF1402–1403; lido 1402–1403)

Inner contrai linhas de duas matrizes com mesmo número de colunas: saída rows(A)×rows(B); equivalente a produtos Dot entre linhas. Não confundir com AB.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0335 — Outer (PDF1404–1406; lido 1404–1406)

Outer achata elementos das matrizes em ordem de linhas e produz matriz total(A)×total(B); vetores produzem grade de produtos. Kron de vetores no exemplo fica uma linha, diferente da forma Outer.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0336 — CorrCoef (PDF1407–1410; lido 1407–1410)

CorrCoef calcula Pearson, rowvar=true considera linhas como variáveis. Rounding pode impedir Hermiticidade/diagonal1/limite absoluto1; clipping não resolve bem complexos. Exemplo Python usa0.2 onde MQL usa2.0, logo saídas não são fixtures equivalentes.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0337 — Cov (PDF1411–1413; lido 1411–1413)

Cov usa rowvar e divisor N-ddof, ddof padrão1. Vetor×vetor retorna matriz2x2. Exemplo centraliza observações e força simetria; política de amostra não deve ser inferida de Std/Var que têm outro padrão.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0338 — Correlate (PDF1414–1416; lido 1414–1416)

Correlate retorna correlação cruzada, FULL tamanho m+n-1, SAME max(m,n), VALID max-min+1; exemplo inverte segundo vetor e trocar operandos reverte sequência. Isso não é Pearson.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0339 — Convolve (PDF1417–1419; lido 1417–1419)

Convolve retorna convolução linear discreta; modos FULL/SAME/VALID e janelas do exemplo. Parâmetro const v é descrito [out], aparente erro documental; tratar como entrada e confirmar em compilação futura.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0340 — Transformations (PDF1420–1434; lido 1420–1434)

Transformações decompõem para sistemas, inversão, determinantes, autovalores e mínimos quadrados; escolher conforme propriedades da matriz.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0341 — Cholesky (PDF1421–1421; lido 1421–1421)

Cholesky bool e saída L; exige Hermitiana positiva definida, usa só triângulo inferior/diagonal e não verifica Hermiticidade. Reconstrução L L^H, não transposta simples para complexo.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0342 — Eig (PDF1422–1424; lido 1422–1424)

Eig retorna autovetores verticais e autovalores; overload complexo obtém solução completa. Texto diz parar com4019 ao encontrar complexo, mas exemplo mostra res=true e apenas uma solução real: verificar bool, erro e completude.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0343 — EigVals (PDF1425–1425; lido 1425–1425)

EigVals calcula somente autovalores, bool; não computa autovetores. A descrição remete a Eig, sem aqui demonstrar todos casos complexos.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0344 — LU (PDF1426–1427; lido 1426–1427)

LU entrega L e U, bool; exemplo valida A=L U. Não pressupor permutação nesta API.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0345 — LUP (PDF1428–1429; lido 1428–1429)

LUP usa pivotamento parcial por linhas, saídas L/U/P e relação P A=L U; fixture deve validar permutação também.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0346 — QR (PDF1430–1431; lido 1430–1431)

QR promete Q com colunas ortonormais e R triangular, bool. Descrição menciona mode complete e stack>2D ausentes da assinatura; saída R do exemplo não parece triangular. Requer teste nativo antes de escolher contrato adicional.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0347 — SVD (PDF1432–1434; lido 1432–1434)

SVD entrega U,V e valores singulares, bool; exemplo reconstrói U diag(S) V^T e verifica ortogonalidade com tolerância1e-9. Não confundir V com VT das APIs OpenBLAS.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0348 — Statistics (PDF1435–1463; lido 1435–1463)

Estatística oferece redução global/por eixo e cumulativos; exemplo estabelece axis0 reduz por coluna, axis1 por linha, evitando ambiguidade dos rótulos horizontal/vertical.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0349 — ArgMax (PDF1436–1436; lido 1436–1436)

ArgMax retorna ulong global indexado por Flat, ou vetor de índices por eixo; exemplo global5 corresponde ao valor12.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0350 — ArgMin (PDF1437–1437; lido 1437–1437)

ArgMin retorna ulong global ou vetor por eixo; exemplo global3 corresponde ao valor1. Índice não é valor.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0351 — Max (PDF1438–1438; lido 1438–1438)

Max global retorna escalar, eixo retorna vetor; exemplo axis0=[10,11,12], axis1=[10,12,6,11].

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0352 — Min (PDF1439–1439; lido 1439–1439)

Min global escalar ou vetor por eixo; preservar esquema das colunas e não trocar valor mínimo por índice.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0353 — Ptp (PDF1440–1440; lido 1440–1440)

Ptp é Max-Min, amplitude, com escalar global ou vetor por eixo; não é desvio padrão.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0354 — Sum (PDF1441–1441; lido 1441–1441)

Sum reduz globalmente ou por eixo; exemplo total78. Precisão e tipo de dados continuam parte do contrato de aplicação.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0355 — Prod (PDF1442–1443; lido 1442–1443)

Prod usa multiplicador inicial padrão1, global ou por eixo; exemplo initial0.1 escala cada produto. Considerar overflow/underflow.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0356 — CumSum (PDF1444–1445; lido 1444–1445)

CumSum sem eixo achata em vetor; com eixo retorna matriz de acumulados por coluna/linha. Ordem altera significado temporal.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0357 — CumProd (PDF1446–1447; lido 1446–1447)

CumProd sem eixo achata em vetor e com eixo mantém matriz; exemplo explicita axis0 sobre linhas por coluna e axis1 sobre colunas por linha.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0358 — Percentile (PDF1448–1449; lido 1448–1449)

Percentile aceita inteiro0..100 inclusivo, algoritmo linear e sequência ordenada requerida no texto. Não assumir que API ordena implicitamente; verificar futuramente com entrada embaralhada.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0359 — Quantile (PDF1450–1451; lido 1450–1451)

Quantile aceita double0..1 inclusivo, linear, sequência ordenada requerida. Quantile0.5 corresponde ao percentil50.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0360 — Median (PDF1452–1453; lido 1452–1453)

Median equivale Quantile0.5/Percentile50; texto exige ordenação. Caso par no exemplo dá6.5 global.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0361 — Mean (PDF1454–1454; lido 1454–1454)

Mean média aritmética global ou por eixo, não ponderada.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0362 — Average (PDF1455–1456; lido 1455–1456)

Average associa pesos à matriz/vetor e aceita eixo; pesos unitários reproduzem Mean. Casos soma de pesos zero/formas inválidas não demonstrados, exigem fixture.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0363 — Std (PDF1457–1458; lido 1457–1458)

Std usa sqrt da soma dos desvios quadráticos dividida por N-ddof, padrão ddof0 populacional; não importar padrão1 de Cov.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0364 — Var (PDF1459–1460; lido 1459–1460)

Var usa média dos desvios quadráticos e N-ddof, padrão0; ddof1 corresponde à amostra. Validar N>ddof na aplicação futura.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0365 — LinearRegression (PDF1461–1463; lido 1461–1463)

LinearRegression retorna valores ajustados y=ax+b, não apenas coeficientes; matriz aceita AXIS_NONE/HORZ/VERT. NONE achata todos elementos. Exemplo gráfico copia100 fechamentos desdebarra1; não prova sinal operacional.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0366 — Features (PDF1464–1481; lido 1464–1481)

Features descreve dimensões, normas, condicionamento, determinante, posto, traço e espectro: diagnósticos matemáticos, não qualidade de decisão financeira.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0367 — Rows (PDF1465–1465; lido 1465–1465)

Rows retorna ulong com número de linhas; exemplo Reshape3x4 retorna3.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0368 — Cols (PDF1466–1466; lido 1466–1466)

Cols retorna ulong com número de colunas; exemplo3x4 retorna4.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0369 — Size (PDF1467–1467; lido 1467–1467)

Size retorna ulong do vetor; linha extraída de matriz3x4 possui4 elementos.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0370 — Norm (PDF1468–1470; lido 1468–1470)

Norm distingue vetor INF/-INF/P e matriz Frobenius, nuclear, P1/P2 e variantes; P0 conta não zeros. Texto de direção/spectral deve ser checado; rótulo P2 no primeiro Print chama Frobenius. Verificar fórmula/enum, não rótulo.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0371 — Cond (PDF1471–1473; lido 1471–1473)

Cond retorna número de condição possivelmente infinito; norma vezes norma da pseudoinversa permite retangulares/singulares segundo texto, exceção espectral. Algoritmo ilustrativo retorna0 se menor raiz0, não copiar como regra de saúde numérica.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0372 — Det (PDF1474–1475; lido 1474–1475)

Det retorna determinante de quadrada, via regra2/3 e eliminação Gauss; linhas/colunas dependentes dão0. Título invertível não autoriza supor que qualquer entrada é válida.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0373 — SLogDet (PDF1476–1476; lido 1476–1476)

SLogDet pretende evitar overflow usando log de produto; assinatura double com sign por referência. Return Value diz número representando sinal e nota diz sinal par positivo, contradiz exemplo NumPy(-1,log2). Contrato exato de retorno/sinal deve ser confirmado nativamente.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0374 — Rank (PDF1477–1479; lido 1477–1479)

Rank retorna int por método Gauss; máximo de linhas/colunas independentes. Exemplos identidade4, identidade com zero3, Ones1x4 posto1, zeros posto0; tolerância numérica não exposta.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0375 — Trace (PDF1480–1480; lido 1480–1480)

Trace soma diagonal principal; exemplo0..8 em3x3 dá12, e nota relaciona soma de autovalores.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0376 — Spectrum (PDF1481–1481; lido 1481–1481)

Spectrum é conjunto de autovalores de A^T A; não confundir com autovalores de A nem singular values sem raiz. Exemplo usado em condição espectral.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0377 — Matrix Classification (PDF1482–1494; lido 1482–1494)

Classificadores estruturais bool não demonstram tolerância; testar ruído numérico antes de usá-los para selecionar algoritmo.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0378 — IsSymmetric (PDF1483–1483; lido 1483–1483)

IsSymmetric testa quadrada simétrica; zero e diagonal são simétricas.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0379 — IsHermitian (PDF1484–1484; lido 1484–1484)

IsHermitian testa conjugação simétrica; diagonal complexa só Hermitiana se parte imaginária diagonal0. Em matriz real equivale à simetria.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0380 — IsUpperTriangular (PDF1485–1485; lido 1485–1485)

IsUpperTriangular exige quadrada e zeros abaixo da diagonal; zero/diagonal também aceitas. Nem toda bidiagonal inferior é superior: a frase genérica bidiagonal merece qualificação.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0381 — IsLowerTriangular (PDF1486–1486; lido 1486–1486)

IsLowerTriangular exige zeros acima da diagonal; classificar orientação da bidiagonal antes de inferir triangularidade.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0382 — IsTrapezoidal (PDF1487–1487; lido 1487–1487)

IsTrapezoidal trata retangular não quadrada com parâmetro bool is_upper; anotado [out] embora assinatura por valor. Texto distingue m<n superior e m>n inferior; confirmar semântica do argumento.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0383 — IsUpperHessenberg (PDF1488–1488; lido 1488–1488)

IsUpperHessenberg zeros abaixo da subdiagonal; tridiagonal e triangular superior são casos incluídos.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0384 — IsLowerHessenberg (PDF1489–1489; lido 1489–1489)

IsLowerHessenberg zeros acima da superdiagonal; tridiagonal e triangular inferior incluídas.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0385 — IsTridiagonal (PDF1490–1490; lido 1490–1490)

IsTridiagonal zeros fora diagonal principal e adjacentes; bidiagonal superior/inferior incluída.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0386 — IsUpperBidiagonal (PDF1491–1491; lido 1491–1491)

IsUpperBidiagonal zeros abaixo principal e acima superdiagonal; diagonal incluída.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0387 — IsLowerBidiagonal (PDF1492–1492; lido 1492–1492)

IsLowerBidiagonal zeros abaixo subdiagonal e acima principal; diagonal incluída.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0388 — IsDiagonal (PDF1493–1493; lido 1493–1493)

IsDiagonal quadrada com zeros fora principal; matriz zero incluída.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0389 — IsScalar (PDF1494–1494; lido 1494–1494)

IsScalar diagonal com todos valores da principal iguais; zero e identidade quadradas incluídas.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0390 — Solutions (PDF1495–1500; lido 1495–1500)

Solutions separa solução direta, mínimos quadrados, inversa e pseudoinversa; escolher por forma e singularidade.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0391 — Solve (PDF1496–1496; lido 1496–1496)

Solve retorna vetor x para Ax=b. Nota afirma sem solução para dependência/linha zero, mas matematicamente pode haver infinitas soluções; interpretar como limitação do solucionador único, não teorema geral. Validar residual.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0392 — LstSq (PDF1497–1497; lido 1497–1497)

LstSq aceita não quadradas/degeneradas; Ax=b exato só para sistema consistente. Exemplo3x2 retorna[5,-4]. Residual é critério essencial fora do exemplo exato.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0393 — Inv (PDF1498–1499; lido 1498–1499)

Inv usa Jordan-Gauss para quadrada não degenerada; verificar A Inv(A)≈I com tolerância. Benchmark publicado NOT_RUN, sem promessa de desempenho local.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0394 — PInv (PDF1500–1500; lido 1500–1500)

PInv Moore-Penrose permite retangular; exemplo valida A A+ A≈A por10 dígitos. Isso é uma identidade de teste, não prova de todas condições Moore-Penrose.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0395 — Machine learning (PDF1501–1537; lido 1501–1537)

ML explica ativação/derivada/perda/backprop. Exemplo20000 épocas, treino1000/teste10 para(a+b+c)^2/(a²+b²+c²), mas código X1 repete Col(1), implementando a+2b; divergência crítica. Nenhuma execução ou adoção Stoikus.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0396 — Activation (PDF1506–1509; lido 1506–1509)

Activation escreve saída e retorna bool; matriz aceita eixo/parâmetros extras. Defaults ELUalpha1, LINEARalpha1/beta0, LRELUalpha0.3, SWISHbeta1, TRELUtheta1; PRELU vetor aprendido. ReLU parametrizada tem formulação pouco usual: validar fronteiras.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0397 — Derivative (PDF1510–1511; lido 1510–1511)

Derivative escreve derivadas da ativação, bool, mesmos parâmetros extras e eixo; é insumo de backprop, não a própria ativação.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0398 — Loss (PDF1512–1513; lido 1512–1513)

Loss retorna double para previsão.Loss(verdade,enum), Huber aceita delta padrão1; quadrática abaixo delta e linear acima. Cabeçalho do capítulo fala escrever vetor, mas assinatura concreta é escalar.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0399 — LossGradient (PDF1514–1515; lido 1514–1515)

LossGradient retorna vetor/matriz de derivadas parciais em relação à previsão; eixos afetam normalização (exemplo MAE1/12 global,1/3 e1/4 por eixo).

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0400 — RegressionMetric (PDF1516–1517; lido 1516–1517)

RegressionMetric compara previsão com verdade e oferece MAE/MSE/RMSE/R2/MAPE/MSPE/RMSLE. Para dados do exemplo MAE=.5 e MSE=.375 por cálculo, mas saída publicada inverte rótulos(.375/.5); não copiar como oracle.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0401 — ConfusionMatrix (PDF1518–1519; lido 1518–1519)

ConfusionMatrix aplicado a y_pred com y_true; linhas verdadeiro, colunas previsto, binária[[TN,FP],[FN,TP]]. Label específico faz one-vs-rest2x2; tamanhos iguais.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0402 — ConfusionMatrixMultilabel (PDF1520–1521; lido 1520–1521)

ConfusionMatrixMultiLabel retorna quantidade uint ou0 falha; preenche array de matrizes2x2. Estático deve comportar número de classes, capacidade12 do exemplo não equivale a quantidade10.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0403 — ClassificationMetric (PDF1522–1525; lido 1522–1525)

ClassificationMetric é y_pred sobre y_true; exclui TOP_K/AP/ROC_AUC. NONE por classe; BINARY só binária; MICRO agrega contagens, MACRO média sem pesos, WEIGHTED pondera suporte e F-score pode ficar fora precisão/recall.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0404 — ClassificationScore (PDF1526–1529; lido 1526–1529)

ClassificationScore inverte receptor: y_true.ClassificationScore(scores,...). Linhas=samples, colunas=probabilidades/classes; TOP_K usa K, AP/AUC usam média. Binária aceita Nx1 positivos ou Nx2 negativo/positivo.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0405 — PrecisionRecall (PDF1530–1533; lido 1530–1533)

PrecisionRecall receptor verdade, bool e saídas precision/recall/thresholds. Somente NONE/BINARY/MICRO; limiares ordenados decrescentes. Tipografia ENUM_ENUM_AVERAGE_MODE e descrição de dimensões micro merecem confirmação. MNIST99% é exemplo, não prova local.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0406 — ReceiverOperatingCharacteristic (PDF1534–1537; lido 1534–1537)

ROC receptor verdade, bool, FPR/TPR/thresholds, médias NONE/BINARY/MICRO. Curva TPR×FPR; código altera primeiro limiar por+0.001 para plot e não deve alterar evidência bruta. AUC.99991 publicado NOT_RUN; figuras não verificadas.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0407 — OpenBLAS (PDF1538–1878; lido 1538–1586)

OpenBLAS integrado oferece BLAS/LAPACK, otimização e multithreading descritos genericamente; não prova velocidade ou paralelismo concreto no Stoikus. Tabela inicial chama BidiagDC BDSVDX mas seção própria corrige BDSDC.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0408 — Singular Value Decomposition (PDF1541–1567; lido 1541–1567)

SVD OpenBLAS oferece algoritmos DC,QR,pivot,bisseção,Jacobi e bidiagonais. Seleção depende de forma, precisão desejada, subset e custo, não só afirmação DC mais rápido.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0409 — SingularValueDecompositionDC (PDF1542–1543; lido 1542–1543)

SVD DC/GESDD bool, jobz N só valores/A vetores completos/S truncados. Saída VT já transposta; complexos entregam valores singulares reais.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0410 — SingularValueDecompositionQR (PDF1544–1545; lido 1544–1545)

SVD QR/GESVD controla jobu/jobv separadamente N/A/S, sempre valores. Assinatura complexa impressa sem referências contradiz saídas descritas: confirmar compilador.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0411 — SingularValueDecompositionQRPivot (PDF1546–1549; lido 1546–1549)

QRPivot/GESVDQ exige rows>=cols; joba acurácia/truncamento, jobp ordenação de linhas, jobr transposiçãoR, jobu/jobv vetores. Se jobu=R e ambos calculados jobv=R. Guardar escolhas e posto numérico.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0412 — SingularValueDecompositionBisection (PDF1550–1552; lido 1550–1552)

Bisection/GESVDX permite subset A todo/V intervalo(VL,VU]/I índices inclusivos, exemplo0..2 três valores; jobv N/U/V/UV seleciona vetores. lower/upper significado depende do enum.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0413 — SingularValueDecompositionJacobiHigh (PDF1553–1557; lido 1553–1557)

JacobiHigh/GEJSV exige rows>=cols e entrega V não VT, work_results com escalas/condições/entropias; joba precisão, jobr range, jobt transposição por entropia, jobp perturbação. Texto tem razões work1/work2 conflitantes: não aplicar escala sem teste.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0414 — SingularValueDecompositionJacobiLow (PDF1558–1560; lido 1558–1560)

JacobiLow/GESVJ exige rows>=cols; ctol só jobuC, mv só jobvA; V não transposta, singular real=scale*S se scale diferente1. Assinatura mostra enums JH mas parâmetros JL; diz7 estatísticas porém enumera6. Validar tipos/comprimento nativamente.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0415 — SingularValueDecompositionBidiagDC (PDF1561–1562; lido 1561–1562)

BidiagDC/BDSDC matriz bidiagonal quadrada real; jobz V valores+vetores/N só valores; U/VT saídas. Nota cita range ausente da assinatura.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0416 — SingularValueDecompositionBidiagBisect (PDF1563–1565; lido 1563–1565)

BidiagBisect/BDSVDX real bidiagonal quadrada, jobz e range A/V/I, V semiaberto(VL,VU], I inclusivo. Não aplicar a matriz geral sem redução.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0417 — SingularValueDecompositionBidiagQR (PDF1566–1567; lido 1566–1567)

BidiagQR/BDSQR recebe Q/PT de ReflectBidiagonalToQP após ReduceToBidiagonal; entradas vazias omitem vetores respectivos. Retorna fatores já compostos UQ e P^T VT da matriz geral, não apenas bidiagonal.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0418 — Eigen Values (PDF1568–1655; lido 1568–1586)

Eigen Values apresenta famílias gerais/simétricas/Hermitianas/tridiagonais e generalizadas; esta rodada lê introdução1568–1571 e filhos até1586, não conclui família até1655.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0419 — General Matrices (PDF1572–1604; lido 1572–1586)

General Matrices distingue GEEV/GEEVX/GEES, par GGEV/GGEVX/GGES e versões blocadas; Schur/Hessenberg/triangulares são estágios próprios. Leitura deste pai só1572–1586, restante até1604 pendente.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0420 — EigenSolver (PDF1574–1575; lido 1574–1575)

EigenSolver/GEEV bool, eigenvalues complexos mesmo entrada real, jobv N/L/R/LR. Nota4019 para solução complexa exige interpretar erro e conteúdo sem descartar parte imaginária válida.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0421 — EigenSolverX (PDF1576–1579; lido 1576–1579)

EigenSolverX/GEEVX acrescenta balance N/P/S/B e sense N/E/V/B; retorna Schur, ilo/ihi, scale, norma1 e recíprocos condição. Saídas opcionais não são válidas se computation correspondente não pedida.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0422 — EigenSolverSchur (PDF1580–1581; lido 1580–1581)

EigenSolverSchur/GEES bool, autovalores complexos, matriz Schur e vetores opcionais por N/V; distingue Schur vectors de eigenvectors. Real pode exigir bloco quasi-triangular apesar rótulo triangular.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0423 — EigenSolver2 (PDF1582–1584; lido 1582–1584)

EigenSolver2/GGEV exige par quadrado mesmo tamanho; entrega alpha,beta e vetores. Lambda=alpha/beta, beta0 e ambos0 têm interpretação: não dividir cegamente. Residual A v=lambda B v ou forma homogênea.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## REF-0424 — EigenSolver2X (PDF1585–1589; lido 1585–1586)

PARCIAL: lidas1585–1586, incluindo objetivo GGEVX e assinaturas double/float/complex/complexf incompleta. Par mesmo tamanho; controles balance/jobv/sense e saídas alpha,beta,Schur1/2,ilo/ihi,lscale/rscale,normas,rconde/rcondv. Descrições detalhadas1587–1589 continuam em fila; não declarar contrato completo.

Aplicação Stoikus: Proposta futura/sem uso atual confirmado. Nenhuma incorporação ao monitor event driven; nenhuma regra JPW derivada destas APIs.

## Continuidade

Próxima página1587; EigenSolver2X termina1589 e permanece parcialmente pendente. Pais REF0001/0277/0407/0418/0419 não são leituras globais concluídas. Lacunas visuais exigem inspeção PDF separada; divergências de API exigem harness nativo, não execução inferida.
