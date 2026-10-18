# REF — revisão semântica do lote06 (PDF1587–1947)

Leitura real e integral do corpo textual de361 páginas físicas do PDF, em24 lotes de até28.991 caracteres. Todos os lotes foram devolvidos sem truncamento de ferramenta; não se substituiu leitura por extração, índice ou amostras. As páginas impressas observadas coincidem com as físicas neste intervalo. Fonte: MQL5 Language REFERENCE, MetaQuotes, edição do PDF2026-05-02, SHA-256 `9ae05ce748d23ce0de9b230fc6c7093a2af0adc3ce3544244a74e1c7d628d499`.

O início é continuação de EigenSolver2X (REF-0424), cujo título/abertura nas páginas1585–1586 pertencem ao lote anterior. A cobertura deste leitor começa exatamente1587. Os173 IDs REF-0424–REF-0596 têm notas abaixo. O ramo Math Functions/REF-0588 segue até2014; somente sua porção1925–1947 é coberta aqui, incluindo os filhos completos até MathCos. Os ancestrais REF-0001, REF-0277, REF-0407, REF-0418 e REF-0419 fornecem contexto hierárquico e não foram contados como novas leituras integrais de seus intervalos completos.

**Limites:** MQL_NOT_RUN em todos os exemplos e rotinas; nenhuma compilação MetaEditor, execução MT5/EX5, latência, resultado de solver ou piloto foi comprovado aqui. NOT_CERTIFIED para visuais e fidelidade de figuras; exemplos têm linhas longas cortadas na própria extração e algumas assinaturas editorialmente defeituosas. Leitura integral do texto disponível não resolve partes gráficas nem caracteres ausentes. Nada do produto, fórmulas, banco, site, instalador, kit ou piloto foi alterado.

## Síntese aplicada

O monitor Stoikus atual é dirigido por eventos, não opera trades e mantém quatro programas diários; Supervisor opcional não está autorizado a armar. Essa delimitação vem do BRIEF de coordenação, não de uma nova auditoria de chamadas do código neste lote. Assim, autoproblemas, DMD, SSA, filtro L1 e BLAS são conhecimento para pesquisa futura isolada. Nenhum resultado estatístico dessas rotinas fundamenta por si um limite JP Wealth ou sinal operacional.

As contribuições imediatamente relevantes são contratos: conversão não substitui validação; formatação não altera representação binária; datas flexíveis não definem timezone; sucesso booleano não garante bom condicionamento. Toda eventual importação deve preservar encoding, comprimento lógico, terminadores, schema e domínio. No plano numérico, escolher matriz pela estrutura, manter o original para norma/resíduo e preservar fator/pivôs/base como conjunto inseparável evita uma grande classe de erros silenciosos.

Há limitações de versão decisivas: as quatro rotinas simétricas2stage não suportam autovetores nesta edição e V causa4003. Há distinções igualmente decisivas de semântica: complexo simétrico usa transposição, Hermitiano conjugação; vetor de autovalores de matriz real pode ser complexo; AF Raw não equivale a fatores explícitos L/U; PLUQ/GESC2 aceita apenas uma RHS e escala o problema. Essas condições devem anteceder qualquer exemplo do manual.

Os exemplos de pseudoinversa e polar são construções SVD, não métodos OpenBLAS dedicados com os nomes dos títulos. O teste de singular exatamente zero é insuficiente como política para quase singularidade; afirmar P sempre definida positiva ignora posto deficiente. Essa crítica é inferência matemática da fórmula lida, sem resultado nativo inventado. DMD exige snapshots e formas coerentes; SSA devolve reconstrução mais horizonte na previsão. A hipótese de futura pesquisa temporal exige comparação independente, amostra externa e prevenção de vazamento, sem incorporação atual ao monitor.

## Registro por seção

Cada entrada cita página física: `[REF, seção/ID, p.PDF N–M]`. Agrupamentos conceituais acima não substituem o mapeamento individual abaixo. Todas as entradas: MQL_NOT_RUN; visuais NOT_CERTIFIED.

### REF-0424 — EigenSolver2X

[REF, EigenSolver2X/REF-0424, p.PDF 1587–1589]. Continuação somente PDF1587–1589: o balanceamento generalizado registra permutações e escalas separadas à esquerda e à direita (lscale/rscale), índices ilo/ihi, normas um de A/B balanceadas e condições recíprocas de valores/vetores controladas por sense E/V/B. Não confundir esses metadados com autovetores originais.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0425 — EigenSolver2Schur

[REF, EigenSolver2Schur/REF-0425, p.PDF 1590–1592]. GGES calcula Schur generalizado do par quadrado A,B de mesmo tamanho, fatores S,T e vetores Schur à esquerda/direita. Representar valores por alpha/beta preserva casos de beta zero; matrizes reais podem produzir valores complexos. Há inconsistências editoriais nas assinaturas e direção de B.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0426 — EigenSolver2Blocked

[REF, EigenSolver2Blocked/REF-0426, p.PDF 1593–1595]. GGEV3 é a versão em blocos do problema generalizado: Av=lambda Bv e uᴴA=lambda uᴴB; jobv escolhe lados. Conservar alpha e beta, inclusive beta=0, sem divisão cega; o texto alerta 4019 quando a solução real esperada é complexa.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0427 — EigenSolver2SchurBlocked

[REF, EigenSolver2SchurBlocked/REF-0427, p.PDF 1596–1598]. GGES3 fornece Schur generalizado em blocos, S/T e bases deflacionantes vsl/vsr; exige segundo membro do mesmo tamanho e saída complexa para espectro potencialmente complexo. A economia por blocos não remove os contratos de dimensões.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0428 — EigenHessenbergSchurQ

[REF, EigenHessenbergSchurQ/REF-0428, p.PDF 1599–1600]. HSEQR calcula Schur de Hessenberg e espectro. Q vazio significa decompor H; Q da redução permite reconstruir o problema anterior A=(QZ)T(QZ)ᵀ. Autovalores de matriz real ainda podem exigir vetor complexo.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0429 — EigenVectorsTriangularZ

[REF, EigenVectorsTriangularZ/REF-0429, p.PDF 1601–1602]. TREVC lê os valores diretamente dos blocos diagonais da forma Schur T e calcula vetores direitos/esquerdos; schur_z vazio omite transformação reversa, presente produz QX/QY. EIGVECTORS_N não é permitido.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0430 — EigenVectorsTriangularZBlocked

[REF, EigenVectorsTriangularZBlocked/REF-0430, p.PDF 1603–1604]. TREVC3 conserva o contrato de TREVC, com algoritmo em blocos BLAS3; a fonte o descreve mais rápido e menos preciso. A escolha exige medir resíduo e ortogonalidade, não apenas duração.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0431 — Symmetric Matrices

[REF, Symmetric Matrices/REF-0431, p.PDF 1605–1636]. A família distingue autoproblemas simétricos reais e Hermitianos complexos, algoritmos DC/QR/MRRR/bisseção, versões em dois estágios e problemas generalizados definidos. Uma metade triangular pode representar toda a matriz simétrica/Hermitiana.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0432 — EigenSymmetricDC

[REF, EigenSymmetricDC/REF-0432, p.PDF 1607–1608]. SYEVD/HEEVD usa divisão e conquista; jobv V inclui autovetores, N só valores. Valores são reais mesmo para entrada Hermitiana complexa. Entrada triangular é interpretada como matriz simétrica/Hermitiana.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0433 — EigenSymmetricQR

[REF, EigenSymmetricQR/REF-0433, p.PDF 1609–1610]. SYEV/HEEV usa QR com o mesmo controle V/N, tipos reais/complexos e interpretação simétrica da metade triangular; não é um solver para matriz triangular arbitrária.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0434 — EigenSymmetricRobust

[REF, EigenSymmetricRobust/REF-0434, p.PDF 1611–1613]. SYEVR/HEEVR usa MRRR, permite todo espectro, intervalo (lower,upper] ou índices (exemplo 0–2 gera três valores). abstol tem piso n*eps*norma(T); precisão relativa pode requerer mínimo seguro sem overflow do inverso.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0435 — EigenSymmetricBisect

[REF, EigenSymmetricBisect/REF-0435, p.PDF 1614–1616]. SYEVX/HEEVX usa bisseção e o mesmo recorte por valor/índice e tolerância. Separar seleção de subconjunto, cálculo de vetores e validação dos resíduos: abstol não altera livremente a precisão dos próprios valores além da aritmética.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0436 — EigenSymmetricDC2s

[REF, EigenSymmetricDC2s/REF-0436, p.PDF 1617–1618]. SYEVD_2STAGE/HEEVD_2STAGE reduz em dois estágios e depois usa divisão e conquista. Nesta edição EIGVALUES_V não está implementado e resulta 4003; só EIGVALUES_N é admissível apesar da descrição geral mencionar vetores.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0437 — EigenSymmetricQR2s

[REF, EigenSymmetricQR2s/REF-0437, p.PDF 1619–1620]. SYEV_2STAGE/HEEV_2STAGE usa QR com redução em dois estágios. A restrição de implementação também proíbe V com 4003; não selecionar a rotina para uma tarefa que exige autovetores.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0438 — EigenSymmetricRobust2s

[REF, EigenSymmetricRobust2s/REF-0438, p.PDF 1621–1623]. SYEVR_2STAGE/HEEVR_2STAGE combina dois estágios e MRRR com subset e abstol. O contrato efetivo desta edição suporta valores sem vetores; V dispara ERR_INVALID_PARAMETER4003.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0439 — EigenSymmetricBisect2s

[REF, EigenSymmetricBisect2s/REF-0439, p.PDF 1624–1626]. SYEVX_2STAGE/HEEVX_2STAGE combina redução em dois estágios e bisseção, subset por valor/índice. EIGVALUES_V permanece indisponível/4003; preservar essa limitação na escolha do algoritmo.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0440 — EigenSymmetric2DC

[REF, EigenSymmetric2DC/REF-0440, p.PDF 1627–1629]. SYGVD/HEGVD resolve problema generalizado simétrico definido por divisão e conquista. itype distingue Ax=lambda Bx, ABx=lambda x e BAx=lambda x; B deve ser definida positiva e retorna fator Cholesky. Se triangulares, A e B usam o mesmo lado.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0441 — EigenSymmetric2QR

[REF, EigenSymmetric2QR/REF-0441, p.PDF 1630–1632]. SYGV/HEGV implementa QR para os mesmos três itypes e requisitos de B definida positiva; saídas incluem fator triangular de B, valores e opcionalmente vetores. Não trocar ordem AB e BA sem alterar o problema.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0442 — EigenSymmetric2Bisect

[REF, EigenSymmetric2Bisect/REF-0442, p.PDF 1633–1636]. SYGVX/HEGVX acrescenta seleção por intervalo/índice e abstol ao problema generalizado simétrico definido. B definida positiva e orientação triangular comum continuam obrigatórias; jobv N evita vetores.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0443 — Tridiagonal Matrices

[REF, Tridiagonal Matrices/REF-0443, p.PDF 1637–1655]. Rotinas tridiagonais exploram estrutura simétrica e algoritmos DC/QR/MRRR/bisseção/QL. As variantes Q transportam a base da redução para recuperar vetores da matriz original; isso difere de vetores da tridiagonal.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0444 — EigenTridiagonalDC

[REF, EigenTridiagonalDC/REF-0444, p.PDF 1639–1640]. STEVD calcula valores e opcionalmente vetores por divisão e conquista de tridiagonal simétrica real double/float. jobv decide V/N; entrada geral não satisfaz o contrato.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0445 — EigenTridiagonalQR

[REF, EigenTridiagonalQR/REF-0445, p.PDF 1641–1642]. STEV oferece QR para tridiagonal simétrica double/float e V/N; não inclui a transformação Q da matriz original, ao contrário de QRQ.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0446 — EigenTridiagonalRobust

[REF, EigenTridiagonalRobust/REF-0446, p.PDF 1643–1645]. STEVR usa MRRR em tridiagonal simétrica, subset A/V/I, limites e abstol com piso de precisão. O exemplo de índices zero a dois seleciona três valores; documentar convenção na ponte para outras bibliotecas.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0447 — EigenTridiagonalBisect

[REF, EigenTridiagonalBisect/REF-0447, p.PDF 1646–1648]. STEVX faz bisseção com subset e tolerância em tridiagonal simétrica real. A validade da estrutura e os limites selecionados devem ser checados antes de comparar resultados com outra rotina.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0448 — EigenTridiagonalQL

[REF, EigenTridiagonalQL/REF-0448, p.PDF 1649–1649]. STERF calcula somente todos os autovalores por variante Pal-Walker-Kahan QL/QR; não há parâmetro ou saída de autovetores.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0449 — EigenTridiagonalDCQ

[REF, EigenTridiagonalDCQ/REF-0449, p.PDF 1650–1651]. STEDC aceita Q da redução simétrica/tridiagonal; compv N só valores, I vetores da tridiagonal, V vetores da matriz original. Não misturar o significado das bases.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0450 — EigenTridiagonalQRQ

[REF, EigenTridiagonalQRQ/REF-0450, p.PDF 1652–1653]. STEQR resolve por QR e possui os mesmos três compv N/I/V; recuperar vetores originais depende de Q correto obtido por ReflectTridiagonalToQ.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0451 — EigenTridiagonalPosDefQ

[REF, EigenTridiagonalPosDefQ/REF-0451, p.PDF 1654–1655]. PTEQR acrescenta a exigência de tridiagonal simétrica definida positiva e permite bases N/I/V. Ser simétrica e tridiagonal não basta para escolher esta rotina.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0452 — Linear Equations

[REF, Linear Equations/REF-0452, p.PDF 1656–1678]. Sistemas AX=B usam A quadrada; B vetor representa uma RHS, B matriz contém RHS nas colunas. Escolher solver pela estrutura de A: geral, triangular, simétrica/Hermitiana, definida positiva ou tridiagonal.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0453 — LinearEquationsSolution

[REF, LinearEquationsSolution/REF-0453, p.PDF 1658–1659]. GESV resolve A geral quadrada com uma ou várias RHS; X mantém as dimensões de B. O booleano deve ser verificado antes de usar X; solução existente não significa matriz bem condicionada.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0454 — LinearEquationsSolutionTriangular

[REF, LinearEquationsSolutionTriangular/REF-0454, p.PDF 1660–1661]. TRTRS resolve com A triangular e trans N/T/C; para dados reais C equivale a T. Dimensões de X coincidem com B e as colunas são problemas independentes.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0455 — InverseTriangular

[REF, InverseTriangular/REF-0455, p.PDF 1662–1662]. TRTRI produz inversa de matriz triangular superior ou inferior; resultado é matriz AI e sucesso é booleano. Inversão não substitui gratuitamente um solve direto para obter AX=B.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0456 — CondNumReciprocalTriangular

[REF, CondNumReciprocalTriangular/REF-0456, p.PDF 1663–1664]. TRCON estima rcond por norma um/infinito; rcond=0 por underflow indica singularidade à precisão de trabalho e valores pequenos sinalizam mau condicionamento. Trata-se de estimativa, não condição exata ou validação econômica.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0457 — LinearEquationsSolutionSy

[REF, LinearEquationsSolutionSy/REF-0457, p.PDF 1665–1666]. SYSV/HESV resolve matriz real simétrica ou complexa Hermitiana; metade triangular é espelhada como simétrica/Hermitiana. A palavra unitary no texto não autoriza usá-la para qualquer matriz unitária.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0458 — LinearEquationsSolutionComplexSy

[REF, LinearEquationsSolutionComplexSy/REF-0458, p.PDF 1667–1667]. SYSV complexo simétrico usa transposição sem conjugação; explicitamente não é o contrato Hermitiano. Essa distinção precisa atravessar a preparação dos dados.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0459 — LinearEquationsSolutionSyPD

[REF, LinearEquationsSolutionSyPD/REF-0459, p.PDF 1668–1669]. POSV requer A simétrica/Hermitiana definida positiva; aceita B vetor/matriz e X com mesmo tamanho. A definitude é pré-condição, não consequência de obter um resultado plausível.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0460 — LinearEquationsSolutionGeTrid

[REF, LinearEquationsSolutionGeTrid/REF-0460, p.PDF 1670–1671]. GTSV explora tridiagonal geral, inclusive não simétrica, e suporta múltiplas RHS. Não escolher a variante simétrica por aparência dos dados.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0461 — LinearEquationsSolutionSyTridPD

[REF, LinearEquationsSolutionSyTridPD/REF-0461, p.PDF 1672–1673]. PTSV exige tridiagonal simétrica/Hermitiana definida positiva e retorna X com dimensões de B; propriedades estruturais precisam existir simultaneamente.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0462 — SylvesterEquationTriangular

[REF, SylvesterEquationTriangular/REF-0462, p.PDF 1674–1676]. TRSYL resolve op(A)X ± Xop(B)=scale*C; A m×m e B n×n superiores, C/X m×n. scale<=1 evita overflow; trans T em complexo é tratado como conjugado nesta rotina, conforme nota.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0463 — SylvesterEquationTriangularBlocked

[REF, SylvesterEquationTriangularBlocked/REF-0463, p.PDF 1677–1678]. TRSYL3 usa blocos para o mesmo Sylvester escalado; a fonte anuncia até cinco vezes mais rápido com menor precisão. A nota final atribui incorretamente a X o tamanho de B: usar a equação dimensional C/X m×n e validar nativamente.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0464 — Least Squares

[REF, Least Squares/REF-0464, p.PDF 1679–1698]. Mínimos quadrados separa sistemas de posto completo (QR/LQ, WY, tall-skinny) de deficientes (SVD, DC, QR pivotado). Resíduos, posto e valores singulares têm contratos próprios; não são simples flags de uma mesma precisão.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0465 — LeastSquaresSolution

[REF, LeastSquaresSolution/REF-0465, p.PDF 1681–1683]. GELS QR/LQ assume posto completo; para trans N, B tem m linhas e X n, com mínimo quadrado se m>=n e norma mínima se m<n; transposto inverte papéis. Resíduos ficam vazios nos casos sem sobre-determinação.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0466 — LeastSquaresSolutionDC

[REF, LeastSquaresSolutionDC/REF-0466, p.PDF 1684–1686]. GELSD usa SVD por divisão e conquista para norma mínima inclusive posto deficiente; elimina S(i)<=rcond*S(1), rcond<0 usa precisão da máquina. Retorna posto/valores singulares/resíduos, mas a assinatura impressa de rank carece & apesar de [out].

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0467 — LeastSquaresSolutionSVD

[REF, LeastSquaresSolutionSVD/REF-0467, p.PDF 1687–1689]. GELSS usa SVD clássico com o mesmo corte de posto e saídas; B m×nrhs e X n×nrhs, resíduos vazios se m<=n. A razão maior/menor valor singular define condição na norma2, exigindo tratamento do menor zero.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0468 — LeastSquaresSolutionWY

[REF, LeastSquaresSolutionWY/REF-0468, p.PDF 1690–1692]. GELST usa QR/LQ com representação compacta WY para aplicar refletores Householder em blocos; exige posto completo e conserva formas B/X e regras de resíduos de GELS. WY não é sigla de uma grandeza financeira.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0469 — LeastSquaresSolutionsQRPivot

[REF, LeastSquaresSolutionsQRPivot/REF-0469, p.PDF 1693–1695]. GELSY encontra norma mínima por fatoração ortogonal completa e QR com pivôs. jpvt não zero fixa coluna à frente; vetor vazio deixa livres. Posto é o maior R11 com condição estimada<1/rcond; devolve permutações e posto, sem vetor de valores singulares.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0470 — LeastSquaresSolutionQRTallSkinny

[REF, LeastSquaresSolutionQRTallSkinny/REF-0470, p.PDF 1696–1698]. GETSLS aplica QR tall-skinny/LQ short-wide a posto completo; trans determina linhas de B/X. A assinatura não fornece resíduos, portanto obtê-los separadamente seria trabalho adicional de validação.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0471 — Orthogonal Factorizations

[REF, Orthogonal Factorizations/REF-0471, p.PDF 1699–1711]. Fatorações ortogonais de A retangular formam Q ortogonal/unitária e fator triangular/trapezoidal. Q preserva norma euclidiana, favorecendo estabilidade em mínimos quadrados e reduções espectrais; texto introdutório em russo foi lido pelo conteúdo.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0472 — FactorizationQR

[REF, FactorizationQR/REF-0472, p.PDF 1700–1701]. GEQRF produz A=QR. Com k=min(m,n), reduced usa Q m×k/R k×n; completo usa Q m×m/R m×n. Guardar essas formas para evitar multiplicações válidas em dimensões erradas.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0473 — FactorizationQRNonNeg

[REF, FactorizationQRNonNeg/REF-0473, p.PDF 1702–1703]. GEQRFP acrescenta diagonal não negativa de R ao contrato QR, com as mesmas formas reduzida/completa. A convenção de sinais pode facilitar comparação reprodutível sem alterar a matriz reconstruída.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0474 — FactorizationQRPivot

[REF, FactorizationQRPivot/REF-0474, p.PDF 1704–1705]. GEQP3 calcula AP=QR com pivoteamento de colunas, P n×n; jpvt não zero prende coluna à frente e vazio libera todas. reduced controla Q/R, sem reduzir P.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0475 — FactorizationLQ

[REF, FactorizationLQ/REF-0475, p.PDF 1706–1707]. GELQF calcula A=LQ; reduced L m×k/Q k×n, completo L m×n/Q n×n. É particularmente distinto de QR quanto à orientação da base.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0476 — FactorizationQL

[REF, FactorizationQL/REF-0476, p.PDF 1708–1709]. GEQLF calcula A=QL; reduced Q m×k/L k×n e completo Q m×m/L m×n. Ordem dos fatores e posição triangular não devem ser inferidas por analogia com LQ.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0477 — FactorizationRQ

[REF, FactorizationRQ/REF-0477, p.PDF 1710–1711]. GERQF calcula A=RQ; reduced R m×k/Q k×n, completo R m×n/Q n×n. Uma referência a L no texto de parâmetro é editorial: a saída é R.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0478 — Factorizations

[REF, Factorizations/REF-0478, p.PDF 1712–1736]. Fatorações LU/LDL/Cholesky simplificam sistemas, inversas e condições; APIs Raw preservam formato LAPACK e pivôs para cálculos subsequentes. Formatos explícitos e Raw não são intercambiáveis.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0479 — FactorizationPLU

[REF, FactorizationPLU/REF-0479, p.PDF 1714–1715]. GETRF calcula A=PLU com pivoteamento parcial de linhas, A retangular permitida; L tem diagonal unitária e pode ser trapezoidal se m>n, U se m<n.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0480 — FactorizationPLUQ

[REF, FactorizationPLUQ/REF-0480, p.PDF 1716–1717]. GETC2 faz pivoteamento completo em A quadrada: A=PLUQ, com P para linhas e Q para colunas. Conservar ambas permutações ao reconstruir ou resolver.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0481 — FactorizationPLUGeTrid

[REF, FactorizationPLUGeTrid/REF-0481, p.PDF 1718–1719]. GTTRF aplica LU com pivoteamento parcial à tridiagonal geral não simétrica; retorna P/L/U explícitos. Especialização depende da estrutura real da entrada.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0482 — FactorizationLDL

[REF, FactorizationLDL/REF-0482, p.PDF 1720–1721]. SYTRF/HETRF usa Bunch-Kaufman para simétrica/Hermitiana; D tem blocos1×1 e2×2, L/U pode ficar permutada. Não assumir D apenas diagonal nem triangular sem permutação.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0483 — FactorizationLDLComplexSy

[REF, FactorizationLDLComplexSy/REF-0483, p.PDF 1722–1722]. SYTRF complexo simétrico usa LDL com transposição sem conjugação e D em blocos; a fonte destaca a diferença de Hermitiana. L/U pode ficar permutada.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0484 — FactorizationLDLSyTridPD

[REF, FactorizationLDLSyTridPD/REF-0484, p.PDF 1723–1724]. PTTRF fatora tridiagonal simétrica/Hermitiana definida positiva em L/D (D diagonal). Esses objetos, e não uma matriz Raw genérica, alimentam os cálculos LDLSyTridPD subsequentes.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0485 — FactorizationCholesky

[REF, FactorizationCholesky/REF-0485, p.PDF 1725–1725]. POTRF fornece fator Cholesky triangular para simétrica/Hermitiana definida positiva. A nota que fala de L e D e rotinas LDL tridiagonais é inconsistente com a assinatura de um fator apenas; manter em fila de verificação.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0486 — FactorizationCholeskySyPS

[REF, FactorizationCholeskySyPS/REF-0486, p.PDF 1726–1727]. PSTRF calcula Cholesky com pivoteamento completo para semidefinida positiva: PᵀAP=LLᵀ ou UᵀU. tol<0 usa n*eps*max(diagonal A); algoritmo para quando pivô<=tol.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0487 — FactorizationPLURaw

[REF, FactorizationPLURaw/REF-0487, p.PDF 1728–1729]. GETRF Raw fornece AF empacotada, diagonal unitária de L implícita, e ipiv; solve/inverse/condição posteriores requerem A original quadrada. AF não é o próprio A original.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0488 — FactorizationPLUQRaw

[REF, FactorizationPLUQRaw/REF-0488, p.PDF 1730–1731]. GETC2 Raw acrescenta pivôs de linha ipiv e coluna jpiv ao LU empacotado; os dois vetores são necessários no solve PLUQ com escala.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0489 — FactorizationPLUGeTridRaw

[REF, FactorizationPLUGeTridRaw/REF-0489, p.PDF 1732–1733]. GTTRF Raw empacota LU de tridiagonal e ipiv, consumidos por solver/estimador PLUGeTrid. Não combinar ipiv de outra fatoração.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0490 — FactorizationLDLRaw

[REF, FactorizationLDLRaw/REF-0490, p.PDF 1734–1735]. SYTRF/HETRF Raw guarda D em blocos e L/U em AF, com ipiv descrevendo permutações e blocos. Alimenta apenas a família LDL correspondente.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0491 — FactorizationLDLComplexSyRaw

[REF, FactorizationLDLComplexSyRaw/REF-0491, p.PDF 1736–1736]. SYTRF Raw para complexo simétrico armazena AF+ipiv sem semântica Hermitiana; alimenta LDLComplexSy, não LDL Hermitiano por substituição de tipo.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0492 — Factored Calculations

[REF, Factored Calculations/REF-0492, p.PDF 1737–1780]. Cálculos fatorados reutilizam decomposições corretas e normas da matriz original. rcond é inverso estimado da condição; custo menor não autoriza aceitar instabilidade nem perder a proveniência dos fatores.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0493 — PLULinearEquationsSolution

[REF, PLULinearEquationsSolution/REF-0493, p.PDF 1741–1743]. GETRS opera sobre AF de FactorizationPLURaw e ipiv, resolve N/T/C com B vetor/múltiplas colunas e X do mesmo tamanho. Não chamar no A não fatorado.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0494 — PLUInverse

[REF, PLUInverse/REF-0494, p.PDF 1744–1744]. GETRI inverte a matriz representada por AF GETRF+ipiv. Guardar a ligação entre fatores e pivôs; uma matriz de mesmo tamanho não é substituta válida.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0495 — PLUCondNumReciprocal

[REF, PLUCondNumReciprocal/REF-0495, p.PDF 1745–1746]. GECON recebe AF LU e norma um/infinito do A original, não de AF. rcond pequeno/zero exige tratamento; a estimativa descrita usa algumas soluções auxiliares e não constitui prova de resíduo pequeno.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0496 — PLUQLinearEquationsSolution

[REF, PLUQLinearEquationsSolution/REF-0496, p.PDF 1747–1749]. GESC2 usa LU completo AF+ipiv+jpiv e resolve AX=scale*B com 0<=scale<=1 para evitar overflow. B matriz deve ter apenas uma coluna, apesar da ampla família suportar múltiplas RHS em outras rotinas.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0497 — PLUGeTridLinearEquationsSolution

[REF, PLUGeTridLinearEquationsSolution/REF-0497, p.PDF 1750–1752]. GTTRS usa AF de GTTRF+ipiv para tridiagonal e N/T/C com múltiplas RHS. X tem mesmo tamanho de B; preservar orientação da operação.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0498 — PLUGeTridCondNumReciprocal

[REF, PLUGeTridCondNumReciprocal/REF-0498, p.PDF 1753–1754]. GTCON estima rcond de tridiagonal usando AF/ipiv, opção norma e valor de norma do A original (MatrixNormGeTrid). Não calcular anorm após destruir os dados originais.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0499 — LDLLinearEquationsSolution

[REF, LDLLinearEquationsSolution/REF-0499, p.PDF 1755–1756]. SYTRS/HETRS resolve AX=B para simétrica/Hermitiana indefinida a partir de AF LDLRaw+ipiv; B vetor ou matriz, X igual dimensão. Não pressupõe positividade.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0500 — LDLInverse

[REF, LDLInverse/REF-0500, p.PDF 1757–1757]. SYTRI/HETRI inverte via AF LDLRaw e ipiv de Bunch-Kaufman; consumo do formato Raw inclui blocos e permutações.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0501 — LDLCondNumReciprocal

[REF, LDLCondNumReciprocal/REF-0501, p.PDF 1758–1759]. SYCON/HECON usa AF LDLRaw, ipiv e norma um original, devolvendo rcond estimado. Condição pequena e sucesso booleano são evidências diferentes.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0502 — LDLComplexSyLinearEquationsSolution

[REF, LDLComplexSyLinearEquationsSolution/REF-0502, p.PDF 1760–1761]. SYTRS complexo simétrico usa AF de LDLComplexSyRaw+ipiv; resultado não usa automaticamente a conjugação Hermitiana. Mantém B/X de mesmo tamanho.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0503 — LDLComplexSyInverse

[REF, LDLComplexSyInverse/REF-0503, p.PDF 1762–1762]. SYTRI inverte complexo simétrico a partir de AF+ipiv da família correta; não é a inversão Hermitiana HETRI.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0504 — LDLComplexSyCondNumReciprocal

[REF, LDLComplexSyCondNumReciprocal/REF-0504, p.PDF 1763–1763]. SYCON estima condição recíproca de complexo simétrico com AF/ipiv e norma um original. Nome da rotina de norma no prose deve ser conferido para não misturar simetria e conjugação.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0505 — LDLSyTridPDLinearEquationsSolution

[REF, LDLSyTridPDLinearEquationsSolution/REF-0505, p.PDF 1764–1765]. PTTRS é chamado sobre L de FactorizationLDLSyTridPD e recebe D separado; resolve múltiplas RHS em matriz positiva definida tridiagonal. A fonte apresenta tipo matrixcd em assinatura, deixando validação nativa pendente.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0506 — LDLSyTridPDCondNumReciprocal

[REF, LDLSyTridPDCondNumReciprocal/REF-0506, p.PDF 1766–1767]. PTCON usa L/D e norma um da tridiagonal original para rcond. Não recebe ipiv porque não se trata da fatoração LDL indefinida em blocos.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0507 — CholeskyLinearEquationsSolution

[REF, CholeskyLinearEquationsSolution/REF-0507, p.PDF 1768–1769]. POTRS resolve sistema positivo definido a partir do L Cholesky, com B vetor/matriz e X igual tamanho. Não aceita uma LDLRaw no lugar do fator.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0508 — CholeskyInverse

[REF, CholeskyInverse/REF-0508, p.PDF 1770–1770]. POTRI inverte a partir de L Cholesky. A descrição de ipiv na lista de parâmetros é espúria porque nenhuma assinatura o recebe; não copiar a lista como contrato compilável.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0509 — CholeskyCondNumReciprocal

[REF, CholeskyCondNumReciprocal/REF-0509, p.PDF 1771–1772]. POCON estima rcond com L Cholesky e norma um do A original. Deve ser associado à mesma matriz/fatoração, não à norma do próprio L.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0510 — SylvesterEquationSchur

[REF, SylvesterEquationSchur/REF-0510, p.PDF 1773–1774]. TRSYL envolvido por formas Schur e QA/QB resolve AX+XB=C para matrizes originais reduzidas. A/B devem estar canônicas (blocos reais1×1/2×2 com propriedades de sinal); X tem forma de C m×n.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0511 — SylvesterEquationSchurBlocked

[REF, SylvesterEquationSchurBlocked/REF-0511, p.PDF 1775–1776]. TRSYL3 faz a versão Schur em blocos com QA/QB e a mesma semântica; fonte anuncia até cinco vezes mais rápido e menor precisão. O exemplo russo de redução prévia também contém grafia de função a verificar.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0512 — Pseudo Inverse

[REF, Pseudo Inverse/REF-0512, p.PDF 1777–1778]. Pseudo Inverse é exemplo, não método nativo dedicado OpenBLAS: SVD A=UΣVᵀ e A+=VΣ+Uᵀ. O código só exclui singular exatamente zero e testa AA+A≈A; para quase singular seria necessário limiar fundamentado e mais identidades.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0513 — Polar Decomposition

[REF, Polar Decomposition/REF-0513, p.PDF 1779–1780]. Polar Decomposition é construção por SVD: Q=UVᵀ e P=VΣVᵀ, A=QP. O teste de ortogonalidade muda lado para retangulares; rank deficiente torna a alegação geral de P definida positiva excessiva (pode ser semidefinida).

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0514 — Reductions

[REF, Reductions/REF-0514, p.PDF 1781–1793]. Reduções preservam transformações ortogonais/unitárias como refletores e tau, e geradores posteriores materializam Q/P. Guardar o pacote completo permite ligar espectro reduzido aos vetores originais.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0515 — ReduceToBidiagonal

[REF, ReduceToBidiagonal/REF-0515, p.PDF 1782–1784]. GEBRD reduz A retangular a bidiagonal superior se m>=n, inferior se m<n. Além de B, entrega reflect_qp empacotada e tau_q/tau_p; os refletores ocupam posições que não são entradas da bidiagonal.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0516 — ReflectBidiagonalToQP

[REF, ReflectBidiagonalToQP/REF-0516, p.PDF 1785–1786]. ORGBR/UNGBR trabalha sobre reflect_qp, recebe tau_q/tau_p e produz Q e Pᵀ/Pᴴ. Para m>=n, Q m×n/PT n×n; para m<n, Q m×m/PT m×n. Não chamar sobre B puro.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0517 — ReduceSymmetricToTridiagonal

[REF, ReduceSymmetricToTridiagonal/REF-0517, p.PDF 1787–1788]. SYTRD/HETRD reduz simétrica/Hermitiana a tridiagonal e entrega reflect_q/tau_q; armazenamento e ordem dos refletores mudam entre metade superior/inferior. Triângulo fornecido representa matriz simétrica completa.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0518 — ReflectTridiagonalToQ

[REF, ReflectTridiagonalToQ/REF-0518, p.PDF 1789–1790]. ORGTR/UNGTR materializa Q dos n−1 refletores de ReduceSymmetricToTridiagonal e tau_q. Usar reflect_q original do mesmo cálculo, não apenas o tridiagonal de saída.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0519 — ReduceToHessenberg

[REF, ReduceToHessenberg/REF-0519, p.PDF 1791–1792]. GEHRD reduz matriz geral quadrada a Hessenberg superior e entrega H/reflect_q/tau_q; refletores ficam abaixo da primeira subdiagonal. A base é necessária na recuperação dos vetores originais.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0520 — ReflectHessenbergToQ

[REF, ReflectHessenbergToQ/REF-0520, p.PDF 1793–1793]. ORGHR produz Q a partir de reflect_q de ReduceToHessenberg e tau_q; Q é produto ordenado de refletores. Não confundir esse gerador com a própria redução.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0521 — Matrix Norm

[REF, Matrix Norm/REF-0521, p.PDF 1794–1809]. Família de normas distingue O (um), I (infinito), F (Frobenius) e M (máximo módulo). A versão deve respeitar estrutura de A; a saída escalar e sucesso booleano são separados.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0522 — MatrixNorm

[REF, MatrixNorm/REF-0522, p.PDF 1796–1797]. LANGE calcula O/I/F/M de matriz geral retangular, com resultado real mesmo para matriz complexa. Pode fornecer anorm antes da fatoração LU.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0523 — MatrixNormGeTrid

[REF, MatrixNormGeTrid/REF-0523, p.PDF 1798–1799]. LANGT explora tridiagonal geral para as quatro normas; é fonte apropriada de anorm para GTCON em vez de tratar AF como matriz original.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0524 — MatrixNormHessenberg

[REF, MatrixNormHessenberg/REF-0524, p.PDF 1800–1801]. LANHS calcula normas da Hessenberg superior. Valores fora da estrutura não devem ser tomados como uma matriz geral arbitrária sob esse contrato.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0525 — MatrixNormSy

[REF, MatrixNormSy/REF-0525, p.PDF 1802–1803]. LANSY/LANHE calcula normas simétrica/Hermitiana e interpreta metade triangular como toda a estrutura; a convenção de conjugação afeta a matriz representada.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0526 — MatrixNormComplexSy

[REF, MatrixNormComplexSy/REF-0526, p.PDF 1804–1805]. LANSY para complexo simétrico difere de LANHE: sem Hermitianização. Fornece O/I/F/M com valor real, respeitando simetria sem conjugação.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0527 — MatrixNormSyTrid

[REF, MatrixNormSyTrid/REF-0527, p.PDF 1806–1807]. LANST/LANHT aplica quatro normas a tridiagonal simétrica/Hermitiana; sustenta a norma original exigida pelos métodos PTCON.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0528 — MatrixNormTriangular

[REF, MatrixNormTriangular/REF-0528, p.PDF 1808–1809]. LANTR aceita triangular quadrada superior/inferior ou trapezoidal: m<n exige superior, m>n exige inferior, com a metade indicada zerada. Não é um atalho geral para matrizes retangulares densas.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0529 — Matrix Balance

[REF, Matrix Balance/REF-0529, p.PDF 1810–1822]. Balancear usa permutação/escala por similaridade para isolar espectro e reduzir disparidades de normas; recuperar vetores originais requer transformação inversa. Melhorar condicionamento não equivale a manter vetores na mesma base.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0530 — MatrixBalance

[REF, MatrixBalance/REF-0530, p.PDF 1812–1813]. GEBAL permite N/P/S/B (nenhum/permutação/escala/ambos), devolve AB, ilo/ihi e scale. scale armazena índices de permutação fora do intervalo ativo e fatores diagonais dentro dele, com ordem de trocas documentada.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0531 — EigenVectorsBackward

[REF, EigenVectorsBackward/REF-0531, p.PDF 1814–1816]. GEBAK transforma autovetores do problema balanceado de volta ao original usando job/side R ou L, ilo/ihi e scale da mesma chamada GEBAL. O receptor é matriz de vetores, não matriz de coeficientes.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0532 — ReduceToHessenbergBalan

[REF, ReduceToHessenbergBalan/REF-0532, p.PDF 1817–1818]. GEHRD balanceado usa intervalo ilo/ihi da chamada GEBAL, assumindo blocos externos já triangulares; sem balanceamento, limites1,N. Retorna H, reflect_q e tau_q para recuperar Q.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0533 — ReflectHessenbergBalancedToQ

[REF, ReflectHessenbergBalancedToQ/REF-0533, p.PDF 1819–1820]. ORGHR balanceado gera Q no intervalo ilo..ihi−1 usando reflect_q/tau_q e limites correspondentes. Metadados de outra redução alterariam a base.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0534 — EigenHessenbergBalancedSchurQ

[REF, EigenHessenbergBalancedSchurQ/REF-0534, p.PDF 1821–1822]. HSEQR balanceado usa ilo/ihi e Q opcional. Q vazio decompõe H; Q presente reconecta a matriz balanceada anterior à redução. Depois de balanceamento, vetores ainda requerem a transformação GEBAK para o original não balanceado.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0535 — Dynamic Mode Decomposition

[REF, Dynamic Mode Decomposition/REF-0535, p.PDF 1823–1836]. DMD estima operador de evolução a partir de snapshots; decomposição compacta poupa memória e a variante QR comprime dados. A descrição do operador Koopman não demonstra previsibilidade ou rentabilidade de séries de mercado.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0536 — DynamicModeDecomposition

[REF, DynamicModeDecomposition/REF-0536, p.PDF 1824–1829]. GEDMD exige X/Y do mesmo tamanho e M>=N; extrai pares Ritz numa base POD. nrnk=−1 usa corte relativo ao maior singular (recomendado), −2 é opção de pesquisa sensível, positivo limita posto; tol em[0,1). Escalas S/C/Y/N, vetores explícitos/fatorados, resíduos/refinamento/exact DMD e quatro SVDs são escolhas independentes. Assinaturas impressas quebradas pedem validação.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0537 — DynamicModeDecompositionQR

[REF, DynamicModeDecompositionQR/REF-0537, p.PDF 1830–1836]. GEDMDQ recebe F com snapshots de uma trajetória em tempos equidistantes, X nas primeiras N−1 e Y nas últimas N−1 colunas. QR comprime; saídas comprimidas devem ser elevadas por Q. jobz V/F/Q/N muda forma dos modos, e Q/R podem ser opcionais; posto máximo é N−1 e M>=N.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0538 — Singular Spectrum Analysis

[REF, Singular Spectrum Analysis/REF-0538, p.PDF 1837–1841]. SSA usa espectro, reconstrução de componentes/série e previsão; os métodos de vetor exigem janela menor que T. A regra aproximada T/2 é orientação de construção, não otimização certificada para preços.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0539 — SingularSpectrumAnalysisSpectrum

[REF, SingularSpectrumAnalysisSpectrum/REF-0539, p.PDF 1838–1838]. SingularSpectrumAnalysisSpectrum calcula contribuições de componentes pelos autovalores da covariância da série; window_length<T e aproximadamente T/2 sugerido. Não interpretar contribuição como probabilidade de um trade.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0540 — SingularSpectrumAnalysisForecast

[REF, SingularSpectrumAnalysisForecast/REF-0540, p.PDF 1839–1839]. SingularSpectrumAnalysisForecast retorna T+horizon pontos: primeiro reconstrução por component_count e depois previsão, não somente os pontos futuros. Escolher janela e componentes exige validação fora da amostra e prevenção de informação futura.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0541 — SingularSpectrumAnalysisReconstructComponents

[REF, SingularSpectrumAnalysisReconstructComponents/REF-0541, p.PDF 1840–1840]. ReconstructComponents devolve cada componente numa coluna e contribuições da covariância. Os eixos da matriz são relevantes para recompor a série corretamente.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0542 — SingularSpectrumAnalysisReconstructSeries

[REF, SingularSpectrumAnalysisReconstructSeries/REF-0542, p.PDF 1841–1841]. ReconstructSeries usa os primeiros component_count componentes e retorna série reconstruída; a lista marca component_count como [out], mas assinatura/semântica indicam entrada. Registrar esse erro editorial antes de exemplos executáveis.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0543 — L1 Trend Filter

[REF, L1 Trend Filter/REF-0543, p.PDF 1842–1844]. Filtro L1 suaviza tendência preservando quebras; lambda menor segue mais os dados e maior suaviza mais. Pode ser absoluto ou fração de lambdaMax; não constitui regra de sinal autorizada do monitor.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0544 — L1TrendFilterLambdaMax

[REF, L1TrendFilterLambdaMax/REF-0544, p.PDF 1843–1843]. L1TrendFilterLambdaMax exige ao menos três elementos, memória linear e lambda de saída ou −1 em erro. A assinatura impressa não mostra referência na saída, uma pendência nativa, não prova de chamada funcional.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0545 — L1TrendFilter

[REF, L1TrendFilter/REF-0545, p.PDF 1844–1844]. L1TrendFilter usa lambda absoluto ou relative=true em[0,1] de lambdaMax, produz vetor filtrado e memória linear. A segunda assinatura é vectorf apesar do cabeçalho complexo; evitar propagar tipo errado.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0546 — BLAS Level 2

[REF, BLAS Level 2/REF-0546, p.PDF 1845–1859]. BLAS2 reúne multiplicação matriz-vetor e atualizações rank1/rank2 com especialização geral, simétrica, Hermitiana e triangular. Toda rotina retorna booleano e requer dimensões coerentes com a operação.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0547 — BlasL2GeMV

[REF, BlasL2GeMV/REF-0547, p.PDF 1847–1848]. GEMV calcula y=alpha*op(A)*x+beta*y; N exige x n/y m e transposto x m/y n. Se Y estiver no tamanho errado, é redimensionado e zerado: beta não preserva acumulador nesse caso.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0548 — BlasL2SyMV

[REF, BlasL2SyMV/REF-0548, p.PDF 1849–1849]. SYMV real simétrico calcula alpha*A*x+beta*y; Y n deve conter dados anteriores se beta!=0, tamanho errado zera. Metade triangular é interpretada simétrica.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0549 — BlasL2HeMV

[REF, BlasL2HeMV/REF-0549, p.PDF 1850–1850]. HEMV complexo Hermitiano mantém y acumulador com mesma regra de tamanho/zeragem. Metade triangular é conjugada como Hermitiana, não simétrica complexa simples.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0550 — BlasL2TrMV

[REF, BlasL2TrMV/REF-0550, p.PDF 1851–1852]. TRMV calcula y=op(A)*x de triangular n×n, com N/T/C e sem alpha/beta. Não há acumulação beta do resultado anterior.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0551 — BlasL2GeR

[REF, BlasL2GeR/REF-0551, p.PDF 1853–1854]. GER/GERU faz AU=A+alpha*x*yᵀ, x m e y n, incluindo tipos complexos sem conjugação automática de y. A saída é matriz atualizada separada.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0552 — BlasL2GeRC

[REF, BlasL2GeRC/REF-0552, p.PDF 1855–1855]. GERC faz rank1 complexo AU=A+alpha*x*yᴴ. A diferença de GERU é a conjugação, essencial para comparar resultados.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0553 — BlasL2SyR

[REF, BlasL2SyR/REF-0553, p.PDF 1856–1856]. SYR faz AU=A+alpha*x*xᵀ para simétrica real; x n e entrada triangular pode representar simetria completa.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0554 — BlasL2HeR

[REF, BlasL2HeR/REF-0554, p.PDF 1857–1857]. HER faz AU=A+alpha*x*xᴴ para Hermitiana complexa. A fonte declara alpha complexo; compatibilidade da interface e preservação Hermitiana precisam ser verificadas nativamente antes de reproduzir.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0555 — BlasL2SyR2

[REF, BlasL2SyR2/REF-0555, p.PDF 1858–1858]. SYR2 faz atualização simétrica real alpha*x*yᵀ+alpha*y*xᵀ+A; ambos vetores n, matriz n×n. Não é produto elemento a elemento dos vetores.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0556 — BlasL2HeR2

[REF, BlasL2HeR2/REF-0556, p.PDF 1859–1859]. HER2 faz alpha*x*yᴴ+conj(alpha)*y*xᴴ+A; a conjugação do segundo alpha é explícita e preserva estrutura Hermitiana.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0557 — BLAS Level 3

[REF, BLAS Level 3/REF-0557, p.PDF 1860–1878]. BLAS3 reúne produtos matriz-matriz e rank-k/rank-2k, aproveitando operações em blocos. A escolha entre SY/HE/TR depende da estrutura e conjugação, não apenas do tipo de dado.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0558 — BlasL3GeMM

[REF, BlasL3GeMM/REF-0558, p.PDF 1862–1863]. GEMM calcula C=alpha*op(A)*op(B)+beta*C com formas m×k,k×n,m×n. C de tamanho errado é redimensionado e zerado, apagando a parcela acumulada; transb tem erro de nome na prosa, mas controla B.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0559 — BlasL3SyMM

[REF, BlasL3SyMM/REF-0559, p.PDF 1864–1865]. SYMM real escolhe A à esquerda (m×m) ou direita (n×n), B/C m×n, e acumula beta*C com zeragem se tamanho errado. A deve representar simetria, mesmo quando fornecida triangular.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0560 — BlasL3HeMM

[REF, BlasL3HeMM/REF-0560, p.PDF 1866–1867]. HEMM aplica o mesmo left/right para A Hermitiana complexa e B/C m×n. A interpretação Hermitiana de entrada triangular precisa ser compatível com os dados.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0561 — BlasL3TrMM

[REF, BlasL3TrMM/REF-0561, p.PDF 1868–1870]. TRMM calcula alpha*op(A)*B ou alpha*B*op(A) para A triangular. A descrição inicial omite B e algumas assinaturas float trazem beta sem correspondente semântico; pendência de conferência antes de copiar código.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0562 — BlasL3SyRK

[REF, BlasL3SyRK/REF-0562, p.PDF 1871–1872]. SYRK atualiza C simétrica real por alpha*AAᵀ ou alpha*AᵀA+beta*C; A n×k ou k×n e C n×n. T/C coincidem para reais.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0563 — BlasL3HeRK

[REF, BlasL3HeRK/REF-0563, p.PDF 1873–1874]. HERK é rank-k Hermitiano com AAᴴ/AᴴA; nesta fonte T e C são tratados como conjugado. Tipos de alpha/beta impressos complexos merecem verificação, dado o requisito estrutural Hermitiano.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0564 — BlasL3SyR2K

[REF, BlasL3SyR2K/REF-0564, p.PDF 1875–1876]. SYR2K usa A/B do mesmo tamanho n×k ou k×n, duas parcelas transpostas e C simétrica n×n. O fator beta refere-se à matriz C de entrada, CU recebe saída.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0565 — BlasL3HeR2K

[REF, BlasL3HeR2K/REF-0565, p.PDF 1877–1878]. HER2K é rank-2k Hermitiano para A/B complexas e C n×n. A fórmula impressa usa alpha em ambas parcelas e omite conjugação no segundo termo; não certificar preservação Hermitiana com alpha complexo arbitrário a partir dessa fórmula.

**Stoikus:** Sem uso atual confirmado. Proposta futura de pesquisa numérica isolada, com resíduos, tolerância e comparação independente; nenhuma mudança no monitor ou geração de sinais autorizada.

### REF-0566 — Conversion Functions

[REF, Conversion Functions/REF-0566, p.PDF 1879–1924]. Conversões separam representação textual, codificação, serialização POD, cores e arredondamento. A exigência de precisão decimal em preço citada aqui não prova alinhamento ao tick, volume mínimo/step ou autorização para enviar ordens.

**Stoikus:** Aplicação ao monitor atual: separar conversão, validação e precisão; uso de chamadas específicas não auditado neste lote.

### REF-0567 — CharToString

[REF, CharToString/REF-0567, p.PDF 1881–1882]. CharToString recebe uchar e retorna símbolo ANSI segundo página de código ativa; não é um conversor Unicode completo. Uso eventual em interoperabilidade deve explicitar encoding.

**Stoikus:** Sem uso atual confirmado; eventual interoperabilidade de bytes é proposta futura.

### REF-0568 — CharArrayToString

[REF, CharArrayToString/REF-0568, p.PDF 1883–1884]. CharArrayToString copia uchar com início/count e codepage (CP_ACP padrão). count=−1 termina no fim ou NUL; bytes com zero embutido podem cortar texto, e extensão não equivale a tamanho lógico.

**Stoikus:** Proposta futura para intercâmbio textual: encoding explícito e comprimento lógico; uso atual não confirmado.

### REF-0569 — CharArrayToStruct

[REF, CharArrayToStruct/REF-0569, p.PDF 1885–1888]. CharArrayToStruct copia bytes com offset para estrutura POD de tipos simples e retorna booleano; exemplo usa sizeof(MqlRates) por registro. Serialização binária depende de layout e não fornece schema/versionamento por si.

**Stoikus:** Sem uso atual confirmado; proposta futura de snapshots binários exigiria schema, tamanho e versão.

### REF-0570 — StructToCharArray

[REF, StructToCharArray/REF-0570, p.PDF 1889–1891]. StructToCharArray copia POD para uchar e expande array dinâmico quando necessário; falha se não puder expandir. O exemplo de round-trip após ZeroMemory é ilustração, não garantia de protocolo entre versões/plataformas.

**Stoikus:** Sem uso atual confirmado; proposta futura de snapshot POD com validação de layout e round-trip.

### REF-0571 — ColorToARGB

[REF, ColorToARGB/REF-0571, p.PDF 1892–1893]. ColorToARGB devolve uint com bytes A/R/G/B: alpha0 transparente e255 opaco, transparência=(1−alpha/255)*100. Exemplo de 0x55 faz contas erradas; 0x55=85 e transparência≈66,7%, não21,6%.

**Stoikus:** Aplicável à interface gráfica do monitor atual; contrato de transparência, sem alegar chamada ou visual verificado.

### REF-0572 — ColorToPRGB

[REF, ColorToPRGB/REF-0572, p.PDF 1894–1895]. ColorToPRGB premultiplica RGB por A/255 para COLOR_FORMAT_ARGB_RAW; alpha0 produz0 e255 coincide com ARGB. Usar representação errada pode criar artefatos no canvas.

**Stoikus:** Proposta futura para canvas RAW; nenhuma migração visual atual foi autorizada.

### REF-0573 — ColorToString

[REF, ColorToString/REF-0573, p.PDF 1896–1896]. ColorToString retorna R,G,B decimais0..255 ou nome predefinido quando color_name=true e há igualdade. Útil em diagnóstico/configuração visual, sem implicação de política operacional.

**Stoikus:** Aplicável a diagnósticos visuais do monitor; chamada atual não verificada.

### REF-0574 — DoubleToString

[REF, DoubleToString/REF-0574, p.PDF 1897–1897]. DoubleToString formata0..16 casas fixas ou−1..−16 científicas; outros digits usam8. Isso controla texto, não torna double decimal exato nem valida seu domínio.

**Stoikus:** Aplicável à apresentação de números do monitor atual, mantendo valor interno separado do texto; chamada atual não verificada.

### REF-0575 — EnumToString

[REF, EnumToString/REF-0575, p.PDF 1898–1899]. EnumToString aceita enum de qualquer tipo e pode definir _LastError (interno/memória/parâmetro inválido); valor sem nome pode aparecer como ENUM_TYPE::-1. Saída legível não valida enum autorizado.

**Stoikus:** Aplicável a journal legível do monitor; enum autorizado deve ser validado separadamente, chamada atual não verificada.

### REF-0576 — IntegerToString

[REF, IntegerToString/REF-0576, p.PDF 1900–1901]. IntegerToString recebe long, comprimento mínimo e símbolo de preenchimento à esquerda; nunca corta número maior que str_len. Não tratar padding como limite máximo de campo.

**Stoikus:** Aplicável a identificadores e journal do monitor; preservar long e campo sem truncamento, chamada atual não verificada.

### REF-0577 — ShortToString

[REF, ShortToString/REF-0577, p.PDF 1902–1903]. ShortToString recebe ushort de código Unicode e produz símbolo; difere do uchar ANSI. Ícones dependem da representação/fonte na interface, cuja aparência não foi certificada.

**Stoikus:** Sem uso atual confirmado; eventual iconografia Unicode é proposta futura e depende de teste visual.

### REF-0578 — ShortArrayToString

[REF, ShortArrayToString/REF-0578, p.PDF 1904–1905]. ShortArrayToString copia ushort (análogo wchar_t), início/count; count−1 termina no fim ou NUL. É a alternativa Unicode ao array de bytes com codepage.

**Stoikus:** Sem uso atual confirmado; proposta futura de intercâmbio Unicode com comprimento explícito.

### REF-0579 — TimeToString

[REF, TimeToString/REF-0579, p.PDF 1906–1908]. TimeToString formata datetime em segundos desde1970 com flags DATE/MINUTES/SECONDS; não converte timezone. O exemplo de temporizador incrementa segundos e chama o tempo restante de aproximado; não deve substituir relógio operacional de sessões.

**Stoikus:** Aplicável aos quatro programas diários do monitor como apresentação de horário; fonte de tempo e timezone exigem contrato separado, chamada atual não verificada.

### REF-0580 — NormalizeDouble

[REF, NormalizeDouble/REF-0580, p.PDF 1909–1910]. NormalizeDouble arredonda para0..8 casas, mas continua double binário e Print pode mostrar resíduos (76.67100000000001). DoubleToString controla apresentação; normalização decimal isolada não satisfaz grade de tick/volume.

**Stoikus:** Aplicável à revisão de precisão das calculadoras/monitor; não alterar fórmula nem assumir suficiência de digits para grade do instrumento.

### REF-0581 — StringToCharArray

[REF, StringToCharArray/REF-0581, p.PDF 1911–1912]. StringToCharArray converte Unicode para bytes da codepage (CP_ACP padrão), retorna quantidade copiada e count−1 inclui NUL. Array cresce se preciso, não encolhe se já maior; enviar tamanho físico pode incluir cauda antiga ou terminador.

**Stoikus:** Proposta futura para exportação/importação de evidências; sem uso atual confirmado, evitar NUL/cauda não lógica.

### REF-0582 — StringToColor

[REF, StringToColor/REF-0582, p.PDF 1913–1913]. StringToColor aceita R,G,B ou nome Web predefinido; retorno é color. É conversão de representação, não uma regra de validação de configurações críticas.

**Stoikus:** Sem uso atual confirmado; útil apenas em eventual importação de configuração visual.

### REF-0583 — StringToDouble

[REF, StringToDouble/REF-0583, p.PDF 1914–1914]. StringToDouble converte texto numérico em double; esta seção não define um contrato completo de rejeição de textos inválidos. Importação deve validar sintaxe/domínio independentemente antes de aceitar número convertido.

**Stoikus:** Aplicável ao contrato de validação de parâmetros do monitor; não usar conversão permissiva como aceitação de dado, chamada atual não verificada.

### REF-0584 — StringToInteger

[REF, StringToInteger/REF-0584, p.PDF 1915–1915]. StringToInteger retorna long; exemplo12345.54321 vira12345, cortando fração. Converter não prova que uma entrada era inteira: contadores/identificadores precisam validação prévia se frações forem proibidas.

**Stoikus:** Aplicável à validação de limites e contadores do monitor; fração silenciosamente cortada precisa rejeição se não autorizada, chamada atual não verificada.

### REF-0585 — StringToShortArray

[REF, StringToShortArray/REF-0585, p.PDF 1916–1917]. StringToShortArray copia Unicode para ushort, count−1 inclui NUL, expande mas não reduz array existente. Guardar contagem efetivamente copiada e separar encoding de capacidade.

**Stoikus:** Sem uso atual confirmado; proposta futura de encoding Unicode preservando contagem.

### REF-0586 — StringToTime

[REF, StringToTime/REF-0586, p.PDF 1918–1920]. StringToTime aceita seis formatos (pontos, barras, hífen, compacto, horas com/sem separadores) e agrupa espaços/tabs entre data/hora. Exemplos incompletos produzem datas surpreendentes/contextuais; impor formato estrito, intervalo e round-trip antes de usar em sessões/importação.

**Stoikus:** Aplicável aos calendários/sessões dos quatro programas diários: propor parser estrito e timezone explícito; uso de chamada atual não auditado.

### REF-0587 — StringFormat

[REF, StringFormat/REF-0587, p.PDF 1921–1924]. StringFormat devolve string com regras de PrintFormat, incluindo precisão variável e formatos long adequados; exemplo relata especificações do símbolo. Relatório de valores no journal não prova que sejam válidos para outro broker/conta ou que foram consultados agora.

**Stoikus:** Aplicável à evidência e diagnóstico do monitor atual; logs precisam especificadores corretos e contexto broker/símbolo, chamada atual não verificada.

### REF-0588 — Math Functions

[REF, Math Functions/REF-0588, p.PDF 1925–1947]. Math Functions indica que muitas funções escalares também aceitam matrizes/vetores elemento a elemento; MathSqrt de matriz não é raiz matricial. MathMod/MathPow aceitam segundo operando escalar ou forma correspondente.

**Stoikus:** Sem uso matricial atual confirmado; conhecimento de linguagem para revisão dos cálculos escalares atuais.

### REF-0589 — MathAbs

[REF, MathAbs/REF-0589, p.PDF 1927–1927]. MathAbs/fabs retorna módulo não negativo double. A aplicação a desvios depende de preservar sinal separadamente quando direção tiver significado no cálculo.

**Stoikus:** Aplicável aos desvios/limites escalares do monitor como contrato de módulo; não confirma uma chamada atual.

### REF-0590 — MathArccos

[REF, MathArccos/REF-0590, p.PDF 1928–1930]. MathArccos/acos usa domínio[−1,1], retorna[0,pi] radianos e NaN fora do domínio. O exemplo usa vetores e CGraphic; validar domínio antes de produzir visual ou qualquer decisão.

**Stoikus:** Sem uso atual confirmado; trigonometria de pesquisa/visualização futura, sem aplicação operacional necessária demonstrada.

### REF-0591 — MathArcsin

[REF, MathArcsin/REF-0591, p.PDF 1931–1933]. MathArcsin/asin retorna[−pi/2,pi/2], NaN fora[−1,1]. O gráfico da fonte é exemplo de interface com Escape/PgDn e limpeza, não evidência de execução nesta pesquisa.

**Stoikus:** Sem uso atual confirmado; trigonometria de pesquisa/visualização futura, sem aplicação operacional necessária demonstrada.

### REF-0592 — MathArctan

[REF, MathArctan/REF-0592, p.PDF 1934–1936]. MathArctan/atan retorna ângulo em[−pi/2,pi/2], zero para entrada0. Não resolve a ambiguidade de quadrantes que atan2 resolve.

**Stoikus:** Sem uso atual confirmado; trigonometria de pesquisa/visualização futura, sem aplicação operacional necessária demonstrada.

### REF-0593 — MathArctan2

[REF, MathArctan2/REF-0593, p.PDF 1937–1940]. MathArctan2/atan2 recebe y,x (nessa ordem), usa quadrantes e retorna[−pi,pi]; limites incluem ambos0=>0 e x<0/y0=>pi. O exemplo calcula um array de ângulos mas passa X/Y originais ao gráfico: não usar a figura como teste de atan2.

**Stoikus:** Sem uso atual confirmado; trigonometria de pesquisa/visualização futura, sem aplicação operacional necessária demonstrada.

### REF-0594 — MathClassify

[REF, MathClassify/REF-0594, p.PDF 1941–1942]. MathClassify distingue subnormal, normal, zero (inclusive negativo), infinito e NaN. Exemplo mostra que MathIsValidNumber aceita subnormal/zero e rejeita NaN/inf; classificação não estabelece domínio financeiro permitido.

**Stoikus:** Proposta futura de diagnóstico numérico defensivo antes de aceitar valor em risco/limites; classificação isolada não valida domínio financeiro.

### REF-0595 — MathCeil

[REF, MathCeil/REF-0595, p.PDF 1943–1944]. MathCeil/ceil retorna como double o menor inteiro>=val; cast para int é uma etapa distinta. O exemplo normaliza soma incremental de0,1 para evitar artefato em fronteiras; política de arredondar risco/volume precisa ser definida externamente.

**Stoikus:** Aplicável ao entendimento do arredondamento do monitor, sem determinar a política JP Wealth nem autorizar fórmula nova.

### REF-0596 — MathCos

[REF, MathCos/REF-0596, p.PDF 1945–1947]. MathCos/cos recebe radianos e retorna[−1,1], com suporte elemento a elemento mencionado no capítulo. Exemplo de curva usa lifecycle CGraphic, loop IsStopped/Sleep e limpeza; esses exemplos não são handlers autorizados do monitor.

**Stoikus:** Sem uso atual confirmado; trigonometria de pesquisa/visualização futura, sem aplicação operacional necessária demonstrada.

## Filas de verificação e limites

- **R06-Q01 — native_signature_verification**, p.PDF 1590, 1591, 1593, 1596, 1597, 1658, 1660, 1684, 1687, 1693, 1764, 1824, 1825, 1830, 1831, 1832, 1843, 1844, 1864, 1866, 1868, 1873, 1877: Assinaturas/tipos, referência de saídas, parâmetros duplicados/sem vírgula e cabeçalhos inconsistentes; verificar no MetaEditor com build registrado antes de qualquer exemplo executável.
- **R06-Q02 — version_capability**, p.PDF 1617, 1618, 1619, 1620, 1621, 1622, 1623, 1624, 1625, 1626: EIGVALUES_V não suportado nas rotinas2stage nesta edição, erro4003. Teste nativo futuro precisa confirmar build/biblioteca real.
- **R06-Q03 — source_editorial_or_formula**, p.PDF 1678, 1725, 1770, 1841, 1845, 1860, 1868, 1877: X em Sylvester tem tamanho C e não B; Cholesky nota cita LDL/D; ipiv espúrio em POTRI; component_count marcado out; HER citado HER2 no resumo; TRMM omite B; HER2K sem conjugação do segundo alpha. Não publicar como receita executada.
- **R06-Q04 — future_numeric_validation**, p.PDF 1777, 1778, 1779, 1780, 1824, 1825, 1826, 1827, 1828, 1829, 1830, 1831, 1832, 1833, 1834, 1835, 1836, 1838, 1839, 1840, 1841, 1843, 1844: Pseudoinversa com limiar em singular pequeno, identidades Moore-Penrose, polar PSD/rank, resíduos DMD e validação temporal SSA/L1 sem vazamento. Pesquisa futura, sem sinal produtivo.
- **R06-Q05 — source_example_error**, p.PDF 1892, 1893, 1894, 1895, 1937, 1938, 1939, 1940: 0x55=85; transparência correta66.7%. Exemplo atan2 calcula ângulos mas desenha X/Y originais. Corrigir síntese, preservar fonte e marcar figuras não certificadas.
- **R06-Q06 — visual_not_certified**, p.PDF todas1587–1947: Leitura cobriu texto extraído integralmente, não imagens ou fidelidade visual. Fonte tem linhas longas de código cortadas no texto; reabrir/renderizar páginas específicas antes de transcrever exemplos/formas gráficas.
- **R06-Q07 — future_interop_input_tests**, p.PDF 1883, 1885, 1889, 1911, 1916, 1918, 1919, 1920: Testar codepage Unicode/byte, terminadorNUL/cauda, POD layout/tamanho e datas inválidas/incompletas com parser estrito; não assumir conversão como validação.
- **R06-Q08 — current_contract_relevance_not_usage_proof**, p.PDF 1909, 1910, 1941, 1942, 1943, 1944: Normalização mantém representação binária; tick/volumegrid e domínio financeiro são contratos separados. Sem auditoria de chamadas atuais neste lote.

## Evidência de cobertura

O JSON acompanhante conserva a lista exata `consolidation_full_text_pages`, SHA-256 original de cada texto, caracteres/erro por página,24 lotes reais,173 notas e filas. Os hashes foram recalculados contra o texto UTF-8 e confrontados aos originais do corpus. Esse teste confirma integridade do material lido; não mede compreensão, fidelidade visual ou comportamento MQL. O último texto lido é o encerramento do exemplo MathCos na página1947; a próxima página1948 é fora deste lote.
