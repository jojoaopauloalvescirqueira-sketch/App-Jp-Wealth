# Complemento semântico TRD — Partes 2 e 3

Data: 2026-10-15. Fonte: MQL5 Programming for Traders, PDF de 2047 páginas; SHA-256 9ff6c55090527afa0efce722d67760805ee335fc64dad3c83638a89e6c79a145.

## Escopo efetivamente realizado

Leitura textual contínua e integral das páginas físicas 42–280, com p281 de transição: Partes 2 e 3 e todos os seus 122 registros de outline, incluindo ramos. Lotes reais 42–63 (trecho truncado recuperado48–55 e47),64–73,74–87 (80–81 recuperados),88–99,100–112,113–124,125–136,137–148,149–159,160–169,170–180,181–191,192–201,202–213,214–224,225–236,237–248,249–259,260–270,271–281.

Não foi confundida extração com leitura; este complemento não declara o livro integralmente lido. Código foi lido e analisado estaticamente, sem compilação/execução; imagens e diagramas incorporados não foram auditados visualmente. Intervalos de outline às vezes terminam antes da continuação real: a leitura incluiu a próxima página e registros declaram isso. Branches resumem filhos e não representam páginas adicionais independentes.

## Relação com o produto

As notas engineering-notes.md e seu registro de limitações foram consultados para preservar o escopo: Monitor é EA de eventos que não negocia; nenhuma ML/Python/OpenCL/DLL ou implementação nova é inferida destes fundamentos. Aplicações abaixo são critérios analíticos/propostas potenciais, nunca alterações comprovadas de Stoikus. Nenhum capítulo, código produtivo, harness ou teste foi modificado.

## Contratos e exemplos por ID

### TRD-0015 — Part 2. Programming fundamentals

- Fonte: [TRD, Part 2. Programming fundamentals, p.PDF 42–165].
- read_scope: `FULL_PART_TEXT`.
- Interpretação/aplicação: Parte2 integral lida: fundamentos, estado, operadores, conversões, controle, funções e preprocessor. Aplicação Stoikus: fidelidade numérica, fronteiras de estado, término cooperativo, interfaces e identidade da compilação.

### TRD-0016 — 2.1 Identifiers

- Fonte: [TRD, 2.1 Identifiers, p.PDF 43–44].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: Identificadores ASCII até 63 caracteres; primeiro não numérico; palavras reservadas proibidas. Nomes claros reduzem colisão no módulo.
- Detalhe: Exemplos ProfitFactor/profit_factor; convenção não altera execução.

### TRD-0017 — 2.2 Built-in data types

- Fonte: [TRD, 2.2 Built-in data types, p.PDF 44–64].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: Tipo limita operações, alcance e representação; ampliar alcance não preserva necessariamente precisão.
- Detalhe: Tabelas de tamanho lidas; subtipos abaixo; p64 também lida para final.

### TRD-0018 — 2.2.1 Integers

- Fonte: [TRD, 2.2.1 Integers, p.PDF 46–50].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: Inteiros assinados e não assinados reinterpretam bits e truncam ao estreitar; tickets exigem ulong compatível.
- Detalhe: TypeInt: uint -1 vira UINT_MAX; int de 10 bilhões vira 1410065408; constantes MIN/MAX evitam magic numbers.

### TRD-0019 — 2.2.2 Floating-point numbers

- Fonte: [TRD, 2.2.2 Floating-point numbers, p.PDF 50–53].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: double tem mantissa de 53 bits; acima de 2^53 não há representação de todos os inteiros consecutivos. Não transportar ticket arbitrário por double.
- Detalhe: TypeFloat: LONG_MAX perde unidades; float 999999975 vira 1e9; MathIsValidNumber deve filtrar não finitos.
- Detalhe: Erros editoriais: p50 descreve 4.29e9 como 4 million; p51 fala potência de 10 na representação binária do expoente. Não reproduzir isso no manual.

### TRD-0020 — 2.2.3 Character types

- Fonte: [TRD, 2.2.3 Character types, p.PDF 53–54].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: Caracteres são códigos inteiros; uchar bytes externos e ushort caracteres de strings exigem conversão de encoding explícita.
- Detalhe: TypeChar: libra 163 em char produz -93 com aviso; escapes hex/octal podem representar mesmo código 92.

### TRD-0021 — 2.2.4 String type

- Fonte: [TRD, 2.2.4 String type, p.PDF 54–55].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: string é sequência ushort com gestão interna; NULL e vazio podem diferir; texto numérico não é valor numérico.
- Detalhe: TypeString: literais adjacentes concatenam; omitir espaços une palavras; não há endereços de memória acessíveis como C++.

### TRD-0022 — 2.2.5 Logic (Boolean) type

- Fonte: [TRD, 2.2.5 Logic (Boolean) type, p.PDF 55–56].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: bool aceita zero=false e qualquer não zero=true; conversão inversa produz 0/1.
- Detalhe: TypeBool: 100 torna true. Aplicação: status e contagem não podem compartilhar semântica só por conversão implícita.

### TRD-0023 — 2.2.6 Date and time

- Fonte: [TRD, 2.2.6 Date and time, p.PDF 56–57].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: datetime guarda segundos desde 1970 e não contém identificação de fuso; literais inválidos podem normalizar com aviso.
- Detalhe: TypeDateTime p57: 30 fevereiro vira 2 março e mês22 avança ano; hora sem data incorpora data de compilação.

### TRD-0024 — 2.2.7 Color

- Fonte: [TRD, 2.2.7 Color, p.PDF 57–58].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: color representa 0x00BBGGRR; não confundir com ARGB de canvas.
- Detalhe: TypeColor usa clrYellow/C literal/hex; relevante apenas interface, não estado de risco.

### TRD-0025 — 2.2.8 Enumerations

- Fonte: [TRD, 2.2.8 Enumerations, p.PDF 58–61].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: Enums são domínios tipados mas representados por int; compartilhar número não compartilha significado.
- Detalhe: MONDAY pode converter para ORDER_TYPE_SELL com aviso; valor inexistente é erro. Warnings precisam revisão, não cast automático para silenciar.

### TRD-0026 — 2.2.9 Custom enumerations

- Fonte: [TRD, 2.2.9 Custom enumerations, p.PDF 61–64].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: Enum customizado usa constantes compiláveis, incremento a partir do último explícito e resolução por Enum::elemento.
- Detalhe: RISK::LOW=-1 e INCOME::LOW=1; const int zero não serve como expressão de enum no exemplo; enum anônimo MILLION serve.

### TRD-0027 — 2.2.10 Void type

- Fonte: [TRD, 2.2.10 Void type, p.PDF 64–65].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: void descreve ausência de valor/argumentos, não variável ordinária.
- Detalhe: Uso como referência genérica a objeto exige Parte3 ainda pendente.

### TRD-0028 — 2.3 Variables

- Fonte: [TRD, 2.3 Variables, p.PDF 64–81].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: Separar declaração, definição, contexto, duração, inicialização e exposição de parâmetros.
- Detalhe: Nenhuma equivalência entre global da linguagem e global do terminal.

### TRD-0029 — 2.3.1 Declaration and definition of variables

- Fonte: [TRD, 2.3.1 Declaration and definition of variables, p.PDF 65–66].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: Declaração descreve atributos; definição fornece implementação/alocação; extern é exceção para variáveis.
- Detalhe: int i,j,k define múltiplas variáveis; posição muda alcance/duração.

### TRD-0030 — 2.3.2 Context, scope, and lifetime of variables

- Fonte: [TRD, 2.3.2 Context, scope, and lifetime of variables, p.PDF 66–68].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: Global vive no programa; local vive no bloco e só fica visível após declaração; blocos aninhados evitam reutilização indevida.
- Detalhe: p separado em dois blocos é duas variáveis; referências fora do bloco são undeclared identifier. Final p68 lido.

### TRD-0031 — 2.3.3 Initialization

- Fonte: [TRD, 2.3.3 Initialization, p.PDF 68–74].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: Globais e estáticas zeram implicitamente; locais numéricas sem inicialização são indeterminadas; shadowing altera variável tocada.
- Detalhe: VariableScopes e walkthrough debugger p70–73 lidos textualmente; capturas não inspecionadas. int j=j do exemplo lê global para inicializar local; não recomendar padrão.

### TRD-0032 — 2.3.4 Static variables

- Fonte: [TRD, 2.3.4 Static variables, p.PDF 74–76].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: static local preserva valor entre chamadas mantendo visibilidade local; não sobrevive descarregamento/reinicialização do programa.
- Detalhe: Greeting contador e messages estáticos; static global não limita unidade como em C++.
- Detalhe: Ressalva própria: garantia counter++%3 do exemplo pressupõe contador não negativo/sem overflow; livro não resolve wrap de int.

### TRD-0033 — 2.3.5 Constant variables

- Fonte: [TRD, 2.3.5 Constant variables, p.PDF 76–77].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: const proíbe escrita após inicialização e combina com static; não prova que valor seja expressão em tempo de compilação.
- Detalhe: Alterar messages[0] gera constant cannot be modified.

### TRD-0034 — 2.3.6 Input variables

- Fonte: [TRD, 2.3.6 Input variables, p.PDF 77–78].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: input é global somente leitura no código; tipos simples/enums; arrays/objetos não entram; sinput exclui otimização.
- Detalhe: p78 continuação lida: representação identifier=value limitada a255 caracteres; strings podem truncar no tester; group organiza UI.

### TRD-0035 — 2.3.7 External variables

- Fonte: [TRD, 2.3.7 External variables, p.PDF 78–81].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: extern global declara um mesmo objeto que deve ter definição; nomes iguais podem unificar estado indevidamente.
- Detalhe: ExternMain/Header1/Header2/Common: sem definição unresolved extern; tipos divergentes erro; inicialização extern proibida; include comum alternativa. Continuação p81 lida.

### TRD-0036 — 2.4 Arrays

- Fonte: [TRD, 2.4 Arrays, p.PDF 81–88].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: Arrays têm dimensão, capacidade e localização de memória diferentes do tempo de vida static.
- Detalhe: Próximo p88 ainda necessário para final da impressão de enums; núcleo dos contratos 82–87 lido.

### TRD-0037 — 2.4.1 Array characteristics

- Fonte: [TRD, 2.4.1 Array characteristics, p.PDF 82–83].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: Até quatro dimensões e total até INT_MAX; linearização exige stride correto.
- Detalhe: Exemplo 1000x4x10=40000; index=Y*N+X. Em Stoikus validar limites antes de indexar.

### TRD-0038 — 2.4.2 Description of arrays

- Fonte: [TRD, 2.4.2 Description of arrays, p.PDF 83–85].
- read_scope: `FULL_SECTION_TEXT`.
- Interpretação/aplicação: Dinâmico omite primeira dimensão e requer ArrayResize; lista inicializadora infere tamanho; omissos zeram.
- Detalhe: p85 continuação lida: vírgula ausente entre literais de strings funde entradas silenciosamente; arrays locais grandes podem esgotar stack; static/dinâmicos usam heap.

### TRD-0039 — 2.4.3 Using arrays

- Fonte: [TRD, 2.4.3 Using arrays, p.PDF 85–88].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Índices0..n-1; acesso fora dos limites termina programa. ArrayPrint imprime enums numericamente; EnumToString serve separadamente. Exemplos locais sem inicialização mostram valores indeterminados.
- Detalhe: Arrays.mq5 demonstra lixo local não inicializado, matrizes transpostas, enum impresso numericamente. Falta continuação p88.

### TRD-0040 — 2.5 Expressions

- Fonte: [TRD, 2.5 Expressions, p.PDF 88–108].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Expressões combinam operações com precedência e associatividade; efeitos laterais exigem ordem explícita. Aplicação Stoikus: separar captura, cálculo e avanço de cursor.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0041 — 2.5.1 Basic concepts

- Fonte: [TRD, 2.5.1 Basic concepts, p.PDF 88–90].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Precedência não define ordem de avaliação dos operandos. a[++i]-a[++i] pode mudar com compilador; funções em mesma expressão não devem alterar estado compartilhado.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0042 — 2.5.2 Assignment operation

- Fonte: [TRD, 2.5.2 Assignment operation, p.PDF 90–92].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Atribuição exige LValue não const e associa da direita para esquerda. ExprAssign demonstra falhas em literal, soma, Symbol() e const; usar == para comparar.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0043 — 2.5.3 Arithmetic operations

- Fonte: [TRD, 2.5.3 Arithmetic operations, p.PDF 92–94].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Divisão de inteiros trunca antes de atribuir a double. 24/7 produz3 mesmo no destino double; converter operando antes. % de dividendo negativo é negativo. Não usar modulo como proteção universal de índice.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0044 — 2.5.4 Increment and decrement

- Fonte: [TRD, 2.5.4 Increment and decrement, p.PDF 94–95].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Prefixo devolve novo valor e postfix antigo. ExprIncDec altera array e cursor na mesma expressão; para continuidade auditável dividir operações, não copiar idiom como garantia entre versões.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0045 — 2.5.5 Comparison operations

- Fonte: [TRD, 2.5.5 Comparison operations, p.PDF 95–97].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Comparação encadeada x<y<z avalia bool contra z; faixa requer &&. Reais pedem tolerância adequada à escala. isEqual do livro usa <eps: x=y=0 falha; mesmo valores subnormais podem zerar eps. Não adotar como política financeira universal.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0046 — 2.5.6 Logical operations

- Fonte: [TRD, 2.5.6 Logical operations, p.PDF 97–98].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: &&/|| avaliam da esquerda para direita e curto-circuitam; guardas antes do acesso. Exemplo index<ArraySize sozinho não exclui índice negativo: Stoikus precisa >=0 também.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0047 — 2.5.7 Bitwise operations

- Fonte: [TRD, 2.5.7 Bitwise operations, p.PDF 98–100].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Máscaras &,|,^,~ não equivalem a lógica &&/||. Shift descarta bits; right shift de assinado replica sinal e de unsigned zera. Validar faixa do deslocamento e tipo efetivo após promoção.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0048 — 2.5.8 Modification operations

- Fonte: [TRD, 2.5.8 Modification operations, p.PDF 100–102].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Atribuição composta calcula LHS uma vez; expansão ingênua e1=e1@e2 pode repetir ++. ExprModification compara arrays divergentes; flags usam OR para set e AND com complemento para clear.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0049 — 2.5.9 Conditional ternary operator

- Fonte: [TRD, 2.5.9 Conditional ternary operator, p.PDF 102–104].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Ternário avalia somente ramo escolhido, devolve RValue e é associativo à direita. ExprConditional mostra soma de ternários sem parênteses produz resultado1 em vez9; limitar nesting.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0050 — 2.5.10 Comma

- Fonte: [TRD, 2.5.10 Comma, p.PDF 104–106].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Vírgula sequencia esquerda->direita e retorna último; em MQL5 uso restrito a cabeçalho for, não generalizar C++.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0051 — 2.5.11 Special operators sizeof and typename

- Fonte: [TRD, 2.5.11 Special operators sizeof and typename, p.PDF 104–106].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: sizeof é compilação e não avalia expressão. Retorna metadados12 para string e52 para array dinâmico no exemplo, não conteúdo nem capacidade; usar StringLen/ArraySize. typename pode incluir categoria e const.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0052 — 2.5.12 Grouping with parentheses

- Fonte: [TRD, 2.5.12 Grouping with parentheses, p.PDF 106–108].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Parênteses corrigem intenção, não apenas removem warning: ExprParentheses evolui8->256->2560; expressões longas merecem decomposição.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0053 — 2.5.13 Priorities of operations

- Fonte: [TRD, 2.5.13 Priorities of operations, p.PDF 106–108].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Tabela completa de precedência lida até p108; :: e índice precedem unários; comparação precede bitwise; && antes||; ternário antes atribuição antes vírgula. Não usar tabela como prova de ordem de operandos.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0054 — 2.6 Type conversion

- Fonte: [TRD, 2.6 Type conversion, p.PDF 108–113].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Conversão pode acontecer em cada subexpressão, argumento, retorno e atribuição. Introdução p108 diz divisão inteira convertida para real, mas exemplo p93 prova truncamento anterior; seguir contrato específico.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0055 — 2.6.1. Implicit type conversion

- Fonte: [TRD, 2.6.1. Implicit type conversion, p.PDF 109–110].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Conversão implícita trunca reais, pode perder precisão inteiro->double e string->número para no primeiro caractere inválido. datetime="2021.12..." vira2021 segundos, não data. string->bool proibida.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0056 — 2.6.2. Arithmetic type conversions

- Fonte: [TRD, 2.6.2. Arithmetic type conversions, p.PDF 110–112].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Tipo do destino não amplia cálculo intermediário: 1e9 literal int multiplicado por si transborda antes de virar long. signed+unsigned pode tornar -38 em4294967258; char variável transborda sem aviso. Loop unsigned >=0 é infinito.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0057 — 2.6.3. Explicit type conversion

- Fonte: [TRD, 2.6.3. Explicit type conversion, p.PDF 112–113].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Cast (target)expr ou target(expr) muda etapa escolhida. Converter x antes de x/y preserva fração; cast após divisão não recupera. Livro recomenda não mascarar warning sem fundamento.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0058 — 2.7 Statements

- Fonte: [TRD, 2.7 Statements, p.PDF 113–137].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Controle organiza execução por loops, seleção e saltos; ausência de erro compilado não demonstra fluxo pretendido. Aplicação: callbacks precisam caminhos limitados e limpeza previsível.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0059 — 2.7.1 Compound statements (blocks of code)

- Fonte: [TRD, 2.7.1 Compound statements (blocks of code), p.PDF 114–118].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Bloco cria escopo e não requer ; ao final. Chaves em if/loops evitam associação visual enganosa.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0060 — 2.7.2 Declaration/definition statements

- Fonte: [TRD, 2.7.2 Declaration/definition statements, p.PDF 114–118].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Definição local cria em ordem e destrói inversa; static uma vez; global antes de entrada. StmtDeclaration rastreia Init(-1),Init(-2),Init(1),Init(0),Init(2). Inicializador global exige declaração antecipada de função. Nenhuma função dentro de função.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0061 — 2.7.3 Simple statements (expressions)

- Fonte: [TRD, 2.7.3 Simple statements (expressions), p.PDF 118–119].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Expression statement requer ;. i+j isolado não tem efeito e recebe warning; Print fora de função causa cascata de erros. Examinar causa primária em vez de cada diagnóstico como bug independente.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0062 — 2.7.4 Overview of control statements

- Fonte: [TRD, 2.7.4 Overview of control statements, p.PDF 119–120].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: for/while/do repetem; if/switch selecionam; break/continue/return saltam. MQL5 não tem goto. Nesting limitado editorialmente, não restrição da linguagem.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0063 — 2.7.5 For loop

- Fonte: [TRD, 2.7.5 For loop, p.PDF 120–124].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: for inicializa uma vez, testa antes, pós-expressão após corpo. Sem condição pode rodar para sempre; cooperar com IsStopped. Sem Sleep ocupa núcleo. Preferir contador inteiro a acumular double .01. Exemplo somatório assume alcançar100 antes de esgotar array: não reutilizar sem limite de tamanho.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0064 — 2.7.6 While loop

- Fonte: [TRD, 2.7.6 While loop, p.PDF 124–126].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: while testa antes e pode executar zero vezes; não declara variável no cabeçalho. uint decrementado nunca fica<0; ausência de warning não impede hang. Serviço duradouro pode usar while+IsStopped, indicador não deve bloquear callback.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0065 — 2.7.7 Do loop

- Fonte: [TRD, 2.7.7 Do loop, p.PDF 126–129].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: do executa pelo menos uma vez e exige ; após condição. Exemplo multiplica por sqrt2 até100; validar pré-condições fora quando array vazio não permite primeira iteração.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0066 — 2.7.8 If selection

- Fonte: [TRD, 2.7.8 If selection, p.PDF 126–129].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: else associa ao if livre mais próximo, não indentação. StmtSelectionIf mode10/20 muda factor sem erro. Atribuição x=y+1 em condição também altera estado; warning expression not boolean é relevante.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0067 — 2.7.9 Switch selection

- Fonte: [TRD, 2.7.9 Switch selection, p.PDF 129–132].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: switch escolhe valor inteiro, cases únicos constantes, fallthrough sem break. StmtSelectionSwitch i2 executa bloco3/4 e factor8. Variável em case exige bloco próprio. Default ausente pode ignorar valor novo silenciosamente.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0068 — 2.7.10 Break jump

- Fonte: [TRD, 2.7.10 Break jump, p.PDF 132–135].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: break sai somente de loop/switch mais interno. Busca de duplicata continua laço externo e encontra U em vez primeiro l; usar estado explícito ou return para sair de toda operação. Exemplo while(++count<100) executa99 vezes, não100.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0069 — 2.7.11 Continue jump

- Fonte: [TRD, 2.7.11 Continue jump, p.PDF 135–136].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: continue avança pós-expressão de for e testa condição; em while/do salta para teste. StmtJumpContinue soma positivos=33. Cuidado com avanço de cursor apenas no corpo antes de continue.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0070 — 2.7.12 Return jump

- Fonte: [TRD, 2.7.12 Return jump, p.PDF 136–137].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: return encerra função inteira e ignora código após loops. Busca de duplicata para imediatamente, mas limpeza e publicação posteriores também serão omitidas; desenhar recursos para liberação garantida.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0071 — 2.7.13 Empty statement

- Fonte: [TRD, 2.7.13 Empty statement, p.PDF 136–137].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Statement vazio ; pode ser corpo intencional. StmtNull busca espaço no cabeçalho; ; acidental desliga corpo do loop sem erro formal. Comentário necessário quando intencional.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0072 — 2.8 Functions

- Fonte: [TRD, 2.8 Functions, p.PDF 137–153].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Funções definem interfaces, passagem de dados, retorno e código reutilizável. Entradas do terminal são callbacks por tipo de programa, não qualquer nome On*. Nenhuma execução nativa feita.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0073 — 2.8.1 Function definition

- Fonte: [TRD, 2.8.1 Function definition, p.PDF 138–139].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Definição exige tipo/nome/parâmetros/corpo; parâmetros são locais. Fibo iterativo usa acumuladores e retorna89 para n10 com convenção f0=f1=1; falta validação de n negativo/overflow no exemplo didático.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0074 — 2.8.2 Function call

- Fonte: [TRD, 2.8.2 Function call, p.PDF 139–140].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Chamada empilha retorno e variáveis; execução do chamador retoma após função. Valor pode entrar em expressão sem variável intermediária; stack cresce com profundidade.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0075 — 2.8.3 Parameters and arguments

- Fonte: [TRD, 2.8.3 Parameters and arguments, p.PDF 140–141].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Quantidade/posição/tipos devem corresponder; ordem de avaliação dos argumentos é indeterminada. Const/cast não corrige side effects entre argumentos. OnDeinit pode omitir nome do argumento mantendo assinatura.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0076 — 2.8.4 Value parameters and reference parameters

- Fonte: [TRD, 2.8.4 Value parameters and reference parameters, p.PDF 141–144].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Valor copia, referência alias exige LValue; const reference comunica leitura. Arrays sempre referência com primeira dimensão aberta; demais dimensões precisam coincidir. ArrayResize não redimensiona array fixo mascarado como parâmetro dinâmico. Transpose2x2 troca elementos reais do chamador.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0077 — 2.8.5 Optional parameters

- Fonte: [TRD, 2.8.5 Optional parameters, p.PDF 144–145].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Defaults só em sufixo do conjunto de parâmetros; omissão da direita para esquerda. Largest usa -DBL_MAX para opcionais; varargs personalizados ... não existem, diferente Print nativo até64 argumentos.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0078 — 2.8.6 Return values

- Fonte: [TRD, 2.8.6 Return values, p.PDF 145–146].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Nonvoid precisa retorno em todos caminhos e tipo compatível; void só return vazio. Arrays devem sair por referência; funções MQL5 não retornam referências. Early return evita resto do callback, não apenas loop.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0079 — 2.8.7 Function declaration

- Fonte: [TRD, 2.8.7 Function declaration, p.PDF 146–147].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Declaração termina com ; sem corpo e exige definição compatível quando usada. Forward Init resolve inicialização global anterior à implementação; declaração não usada pode desaparecer do binário.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0080 — 2.8.8 Recursion

- Fonte: [TRD, 2.8.8 Recursion, p.PDF 147–148].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Recursão exige base e limite de recursos; FiboEndless compila sem warning e falha em runtime com Stack overflow. Recursão indireta também acumula frames; não confundir compilação com segurança operacional.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0081 — 2.8.9 Function overloading

- Fonte: [TRD, 2.8.9 Function overloading, p.PDF 148–150].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Sobrecarga depende parâmetros, não só retorno. sum(1,3.14) é ambígua; arrays[][2]/[][3] distinguem. const em valor não distingue, const em referência pode distinguir. Defaults podem introduzir ambiguidades.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0082 — 2.8.10 Function pointers (typedef)

- Fonte: [TRD, 2.8.10 Function pointers (typedef), p.PDF 150–153].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: typedef define ponteiro de função MQL5, não alias arbitrário C++. Calc global/local sem inicialização zera; checar NULL antes de chamar ou Invalid function pointer call. Callbacks MyCallback só suportam função customizada, não API nativa; código de progresso não é agendamento concorrente.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0083 — 2.8.11 Inlining

- Fonte: [TRD, 2.8.11 Inlining, p.PDF 153–154].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Inlining automático pode eliminar overhead; inline reservado não força geração. Profiling pode desabilitar. Não prometer ganho nem equivalência de medição entre binários de profiling/release.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0084 — 2.9 Preprocessor

- Fonte: [TRD, 2.9 Preprocessor, p.PDF 153–166].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Preprocessor transforma texto antes de compile; inclui arquivos, macros e condicionais. Efeito depende ordem de diretivas, não escopo lexical de funções. Relevante manifesto exato de build.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0085 — 2.9.1 Including source files (#include)

- Fonte: [TRD, 2.9.1 Including source files (#include), p.PDF 154–155].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: include copia texto no ponto de uso. <> busca MQL5/Include, aspas diretório do arquivo atual; nested includes e .txt podem inicializar array. Arquivo ausente falha build; imagem binária não é include de código.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0086 — 2.9.2 Overview of macro substitution directives

- Fonte: [TRD, 2.9.2 Overview of macro substitution directives, p.PDF 155–156].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Macro substitui token e reexpande; nomes podem colidir com variáveis/funções. Macros antecedem templates. Autorreferência resulta identificador desconhecido, não recursão útil.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0087 — 2.9.3 Simple form of #define

- Fonte: [TRD, 2.9.3 Simple form of #define, p.PDF 156–158].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: define simples pode ser flag vazia, constante textual ou fragmento. const int não substitui macro em dimensão fixa no exemplo. OnStart wrapper renomeia fonte posterior, alterando entrada: manifesto precisa incluir headers e macros.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0088 — 2.9.4 Form of #define as a pseudo-function

- Fonte: [TRD, 2.9.4 Form of #define as a pseudo-function, p.PDF 158–161].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Macro parametrizada exige ( sem espaço após nome e reavalia argumento por ocorrência. MAX(++x,...) pode duplicar efeito; MUL sem parênteses dá11 em vez21. ABS(INC(x)) expande três incrementos. Preferir função quando semântica é cálculo.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0089 — 2.9.5 Special operators '#' and '##' inside #define definitions

- Fonte: [TRD, 2.9.5 Special operators '#' and '##' inside #define definitions, p.PDF 161–162].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: # transforma parâmetro em string e ## cola tokens; macro resultante da colagem pode reexpandir. PRT mostra expressão+resultado; VAR gera var3 e for_each gera max_i. Não presumir que texto de log identifica build.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0090 — 2.9.6 Cancelling macro substitution (#undef)

- Fonte: [TRD, 2.9.6 Cancelling macro substitution (#undef), p.PDF 162–163].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: undef remove regra futura e permite redefinir explicitamente; não remove macro predefinida. Estado de macro influencia headers seguintes.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0091 — 2.9.7 Predefined preprocessor constants

- Fonte: [TRD, 2.9.7 Predefined preprocessor constants, p.PDF 162–163].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: DATE/DATETIME/FILE/PATH/LINE/FUNCSIG/MQLBUILD e DEBUG/RELEASE são contexto de compilação. RANDOM/COUNTER podem mudar expansão; data compilada não é relógio runtime nem hash do conjunto.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0092 — 2.9.8 Conditional compilation (#ifdef/#ifndef/#else/#endif)

- Fonte: [TRD, 2.9.8 Conditional compilation (#ifdef/#ifndef/#else/#endif), p.PDF 163–164].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: ifdef/ifndef escolhem presença de macro, não valor numérico de flag; else/endif podem aninhar. DEMO ausente inclui cálculo. Binários com mesmas fontes-base e flags distintas não são mesma evidência.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0093 — 2.9.9 General program properties (#property)

- Fonte: [TRD, 2.9.9 General program properties (#property), p.PDF 164–166].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: property configura metadados e stack; só atua no mq5 principal, é ignorado em includes. stacksize recomenda e compilador amplia até64MB; análise fixa não cobre crescimento recursivo. script_show_inputs controla diálogo. versão textual não prova bytes ou execução.
- Detalhe: Leitura integral textual do intervalo, inclusive continuações recuperadas; sem execução e sem auditoria visual de figuras.

### TRD-0094 — Part 3. Object Oriented Programming

- Fonte: [TRD, Part 3. Object Oriented Programming, p.PDF 166–281].
- read_scope: `FULL_PART_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Parte3 integral textual: estruturas/unions, ciclo de vida, encapsulamento/herança/polimorfismo, ponteiros/const e templates. Aplicação Stoikus: contratos de snapshots, propriedade de recursos e instanciação verificável de bibliotecas; nenhuma migração OOP proposta como requisito.

### TRD-0095 — 3.1 Structures and unions

- Fonte: [TRD, 3.1 Structures and unions, p.PDF 166–180].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Struct agrupa dados por domínio e suporta métodos/constructors, acesso e herança; não possui ponteiros nem virtual functions como class. Escolha depende invariantes, não estética.

### TRD-0096 — 3.1.1 Definition of structures

- Fonte: [TRD, 3.1.1 Definition of structures, p.PDF 167–169].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Settings concentra parâmetros; Result retorna múltiplos campos. Struct parâmetro exige referência; agregado permite omitir campos e zerar restantes, somente durante inicialização. r={} é inicialização e não atribuição posterior.

### TRD-0097 — 3.1.2 Functions (methods) in structures

- Fonte: [TRD, 3.1.2 Functions (methods) in structures, p.PDF 169–170].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Print não recebe struct como valor; &r também não serve porque ponteiro só class. Result.print imprime campos e coeficientes explicitamente. Adaptar log para esquema estável, não dump binário.

### TRD-0098 — 3.1.3 Copying structures

- Fonte: [TRD, 3.1.3 Copying structures, p.PDF 170–171].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Atribuição copia todos campos de struct de mesmo tipo; layouts iguais em tipos diferentes não dão equivalência. snapshot estruturado mantém identidade de tipo, não aceitar só sizeof igual.

### TRD-0099 — 3.1.4 Constructors and destructors

- Fonte: [TRD, 3.1.4 Constructors and destructors, p.PDF 171–174].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Constructor explícito elimina aggregate initialization; strings/dynamic arrays geridos automaticamente, números não são zerados só por existir default constructor. Result contadores separados por método; retorno gera temporário no exemplo e total4construções/4destruições. Quantidade de temporários pode mudar com compilador.

### TRD-0100 — 3.1.5 Packing structures in memory and interacting with DLLs

- Fonte: [TRD, 3.1.5 Packing structures in memory and interacting with DLLs, p.PDF 174–175].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Struct é pack1 por padrão; pack1/2/4/8/16 altera alinhamento. offsetof(Result,status)=36; DLL exige layout compatível e não admite strings/dynamic arrays/classes/pointers na struct de intercâmbio. Não habilita DLL no produto.

### TRD-0101 — 3.1.6 Structure layout and inheritance

- Fonte: [TRD, 3.1.6 Structure layout and inheritance, p.PDF 175–177].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Composição aninha campo e acesso m.data.X; herança incorpora base e permite copiar parte comum nas duas direções. Campo extra do derivado fica intacto ao copiar base para derivado; derivado->base corta extras. Base const exige initialization list e constructor base paramétrico explícito.

### TRD-0102 — 3.1.7 Access rights

- Fonte: [TRD, 3.1.7 Access rights, p.PDF 177–178].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Struct default public; protected para implementação/descendentes e private apenas contexto do tipo. getStatus expõe leitura sem permitir atribuição externa; controle de acesso não é controle de autorização comercial.

### TRD-0103 — 3.1.8 Unions

- Fonte: [TRD, 3.1.8 Unions, p.PDF 178–180].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Union sobrepõe campos em offset0 e tamanho máximo. ulong2double preserva bits onde cast numérico perde2^53+1. Só tipos simples elegíveis; não transportar esse double por aritmética/formatação como se fosse número, pois padrão de bits pode representar não finito. Isto não autoriza empacotar tickets em globals existentes.

### TRD-0104 — 3.2 Classes and interfaces

- Fonte: [TRD, 3.2 Classes and interfaces, p.PDF 180–251].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Classes definem dados/invariantes/interface e propriedade; leitura integral dos22filhos com exemplos Shapes, ThisCallback, Matrix, CounterConstPtr e FinalDelete. Não executar esses exemplos foi decisão de escopo.

### TRD-0105 — 3.2.1 OOP fundamentals: Abstraction

- Fonte: [TRD, 3.2.1 OOP fundamentals: Abstraction, p.PDF 180–181].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Abstração parte de interface necessária ao cliente e permite trocar implementação; campos internos não devem definir API pública por conveniência. Stoikus pode tratar snapshot consistente como contrato e separar forma de aquisição.

### TRD-0106 — 3.2.2 OOP fundamentals: Encapsulation

- Fonte: [TRD, 3.2.2 OOP fundamentals: Encapsulation, p.PDF 181–182].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Encapsulação restringe mutação acidental; class default private e public é superfície externa. Não substitui validação temporal/financeira.

### TRD-0107 — 3.2.3 OOP fundamentals: Inheritance

- Fonte: [TRD, 3.2.3 OOP fundamentals: Inheritance, p.PDF 182–183].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Herança representa is-a; derivado pode substituir base; herança não pode formar ciclos. Reuso sozinho não prova relação semântica correta; favorecer composição para runtimes independentes se houver proposta futura.

### TRD-0108 — 3.2.4 OOP fundamentals: Polymorphism

- Fonte: [TRD, 3.2.4 OOP fundamentals: Polymorphism, p.PDF 183–184].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Polimorfismo executa mesmo contrato draw em formas diferentes; exige despacho dinâmico correto, não apenas métodos homônimos. Aplicação potencial adapters testáveis, não mudança autorizada.

### TRD-0109 — 3.2.5 OOP fundamentals: Composition (design)

- Fonte: [TRD, 3.2.5 OOP fundamentals: Composition (design), p.PDF 183–184].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Composição possui e destrói partes; agregação guarda referências a entidades independentes; associação usa outro objeto. DRY/SRP/OCP guiam responsabilidades. Stoikus: declarar dono de handle/recurso para evitar double delete e uso após liberação.

### TRD-0110 — 3.2.6 Class definition

- Fonte: [TRD, 3.2.6 Class definition, p.PDF 184–187].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Class cria contexto com fields/methods privados por padrão; Print(s) falha e Print(&s) imprime descritor, não conteúdo. toString explícito é necessário. Números de descritores são diagnósticos locais, não identidade durável entre sessões.

### TRD-0111 — 3.2.7 Access rights

- Fonte: [TRD, 3.2.7 Access rights, p.PDF 187–188].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: public/protected/private afetam membros posteriores. const no método restringe mutação dos campos; sem friend em MQL5. Objeto local pode receber mesma memória em relançamentos e parecer zerado por acaso; inicializar sempre campos numéricos.

### TRD-0112 — 3.2.8 Constructors: default, parametric, and copying

- Fonte: [TRD, 3.2.8 Constructors: default, parametric, and copying, p.PDF 188–194].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Default constructor precisa realmente zero parâmetros em MQL5, não todos parâmetros opcionais. Initialization list necessária para const/membros sem default; ordem real é declaração de fields, não ordem escrita da lista. Copy constructor difere de atribuição e é essencial para duplicar class com const; sem ele sintaxe= pode default+copy.

### TRD-0113 — 3.2.9 Destructors

- Fonte: [TRD, 3.2.9 Destructors, p.PDF 194–195].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Destructor sempre virtual em MQL5; automática liberação dos campos geridos não inclui todo recurso externo. Global constrói antes de entrada e destrói ao unload; local no bloco. Referência a objeto não cria cópia nem prolonga lifetime. Aplicação: retorno antecipado só dá limpeza automática para donos adequados.

### TRD-0114 — 3.2.10 Self-reference: this

- Fonte: [TRD, 3.2.10 Self-reference: this, p.PDF 195–198].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: this é referência ao objeto atual, &this seu descritor; resolve shadowing e permite fluência retornando ponteiro do objeto existente. Exemplo parâmetro backgroundColor oculta field e gera conversão para string; usar nomes distintos. Não retornar ponteiro de variável local.

### TRD-0115 — 3.2.11 Inheritance

- Fonte: [TRD, 3.2.11 Inheritance, p.PDF 198–203].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: MQL5 só uma base e não permite class<->struct. Modificador de herança transforma visibilidade; constructors base precedem corpo derivado e destructors ordem reversa. Shape guarda typename recebido pelo constructor derivado. Copy derivado->base fatia extras; direção inversa exige semântica explícita.

### TRD-0116 — 3.2.12 Dynamic creation of objects: new and delete

- Fonte: [TRD, 3.2.12 Dynamic creation of objects: new and delete, p.PDF 203–205].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: new cria e devolve descritor; declarar ponteiro só não cria objeto. delete deve consumir somente POINTER_DYNAMIC; CheckPointer distingue automatic/dynamic/invalid. Reutilizar ponteiro após delete aborta programa. FREE macro não zera aliases nem prova ownership exclusivo.

### TRD-0117 — 3.2.13 Pointers

- Fonte: [TRD, 3.2.13 Pointers, p.PDF 205–211].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Ponteiros são descritores sem aritmética de endereço; & e GetPointer obtêm mesmo objeto. Manager/Element usam forward declaration e callback; callback roda na mesma execução, não thread nova. Array de Shape* permite heterogeneidade com dono de cada new. Defeito analítico: random(range)=rand()/32767*range pode retornar range quando rand==32767; random(NUMBER_OF_SHAPES) pode cair default NULL e subsequente shapes[i].toString falhar. Não copiar sem guarda.

### TRD-0118 — 3.2.14 Virtual methods (virtual and override)

- Fonte: [TRD, 3.2.14 Virtual methods (virtual and override), p.PDF 211–220].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Virtual inicia despacho pelo tipo estático da API e escolhe override da instância; override denuncia assinatura divergente, inclusive const. OverrideVsOverload Base/Derived/Concrete/Special mostra process(int) não sobrepõe process(float). Evitar chamada virtual em constructor/destructor, mesmo indireta. Defeito do exemplo covariante p215: Rectangle::setColor dentro do próprio Rectangle::setColor chama a si, apesar comentário original; base pretendida seria Shape::setColor. Tratar estaticamente, não alegar crash observado.

### TRD-0119 — 3.2.15 Static members

- Fonte: [TRD, 3.2.15 Static members, p.PDF 220–222].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Static field pertence uma vez à classe, requer definição fora com :: e pode compartilhar contagem entre todos derivados. Static method não tem this nem acesso direto a field da instância e não é virtual. Counter do exemplo totaliza criações, não objetos vivos.

### TRD-0120 — 3.2.16 Nested types, namespaces, and the context operator '::'

- Fonte: [TRD, 3.2.16 Nested types, namespaces, and the context operator '::', p.PDF 222–226].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Tipos aninhados seguem acesso; namespace pode reabrir e conteúdo é público. Fully qualified Drawing::Shape::Pair evita colisão; ::Print seleciona função global quando método Print mais próximo oculta logs. Erro editorial p223 usa Drawing::Shape::Rect embora tipo definido Pair. Contradição local: p118 sugere tipos só globais, p222 permite dentro de função; confirmar REF/compilação se dependente, não ensinar limitação ampla.

### TRD-0121 — 3.2.17 Splitting class declaration and definition

- Fonte: [TRD, 3.2.17 Splitting class declaration and definition, p.PDF 226–229].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Separar declaration/interface e definition com Class::method exige assinatura/const idênticos. Initialization list só na definição. Forward declaration resolve referência circular entre Manager/Element. Header ainda pode expor layout; interface abstrata evita depender organização privada.

### TRD-0122 — 3.2.18 Abstract classes and interfaces

- Fonte: [TRD, 3.2.18 Abstract classes and interfaces , p.PDF 229–231].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Pure virtual=0 torna class abstrata; interface tem métodos public virtual sem implementação. Drawables podem ser Shapes/Text/coleções mantendo API; covariância especializa retorno. Pure virtual function call pode ser fatal em runtime; interface compilada não prova implementação nativa íntegra.

### TRD-0123 — 3.2.19 Operator overloading

- Fonte: [TRD, 3.2.19 Operator overloading, p.PDF 231–242].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Operator overload preserva aridade/precedência; proibidos :: () . unary& ?: vírgula e casts/new/delete. Fibo prefix retorna &this e postfix cópia anterior; ponteiro=ponteiro reatribui descritor sem chamar operator=. Matrix usa temp para cálculo e wrappers [] de int/uint para escrita/leitura. Lacunas concretas do exemplo: sem validação de tamanhos/resize/índices, += assume dimensões compatíveis; *= só comenta precondição columns==other.rows; == compara array e não shape, e é igualdade exata. MatrixRow/MatrixElement retêm ponteiros para proxies: armazenar além lifetime da expressão pode invalidar. Não adotar como biblioteca financeira pronta.

### TRD-0124 — 3.2.20 Object type сasting: dynamic_cast and pointer void *

- Fonte: [TRD, 3.2.20 Object type сasting: dynamic_cast and pointer void *, p.PDF 242–246].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Objeto compatível pode copiar parte base e perder extras; const elimina copy implícito. Pointer upcast é natural; downcast incompatível pode fatal Incorrect casting of pointers. dynamic_cast devolve NULL para incompatível, permitindo erro controlado. void* perde tipagem e exige casts/guardas; forward declaration é preferível ao usar void* só para evitar dependência.

### TRD-0125 — 3.2.21 Pointers, references, and const

- Fonte: [TRD, 3.2.21 Pointers, references, and const, p.PDF 246–250].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Referências só parâmetros e não podem ter default; objetos exigem ref e ponteiros apenas classes. Class*& permite trocar ponteiro do chamador. const Class* protege objeto e Class*const protege descritor; const dos dois protege ambos. CounterConstPtr demonstra clone novo que precisa delete e cast que remove const, não recomendado. Texto p247 diz nonconst pointer aceita qualquer argumento, mas p249 o rejeita const->nonconst: preservar restrição demonstrada, não frase ampla.

### TRD-0126 — 3.2.22 Inheritance management: final and delete

- Fonte: [TRD, 3.2.22 Inheritance management: final and delete, p.PDF 250–251].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: final impede herança e pode permitir otimização; =delete desativa método não virtual/constructors/copy que não se deve usar. Método virtual da base não pode ser removido. Base* ainda chama Base.method quando Derived.method é deletado (exemplo p251); isto não é remoção universal do contrato.

### TRD-0127 — 3.3 Templates

- Fonte: [TRD, 3.3 Templates, p.PDF 251–281].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Templates geram código apenas quando instanciados para combinação de tipos. Não suportam todo C++: sem valores/defaults/variádicos/especialização geral de objetos/template-template. Aplicação: compilar instanciações relevantes em harness futuro, não inferir validação de template ocioso.

### TRD-0128 — 3.3.1 Template header

- Fonte: [TRD, 3.3.1 Template header, p.PDF 252–253].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Header template<typename T,...> aceita1..64tipos; typename é marcador de parâmetro, diferente operador typename de string. Parâmetro pode compor T*, T&, const T, arrays, nested types, new T e sizeof(T), sujeito restrições de classe vs estrutura.

### TRD-0129 — 3.3.2 General template operation principles

- Fonte: [TRD, 3.3.2 General template operation principles, p.PDF 253–255].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Max<T> gera versão só quando chamado; template não usado pode conter sintaxe inválida sem impedir build. Inferência só argumentos de função/método, não retorno; mixed double/datetime ambíguo, tipo explícito resolve com conversões. Uma instância por combinação, reutilizada em chamadas.

### TRD-0130 — 3.3.3 Templates vs preprocessor macros

- Fonte: [TRD, 3.3.3 Templates vs preprocessor macros, p.PDF 255–256].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Template é tipado e contextual, macro é texto sem contexto; macro pode duplicar efeitos e dificulta debug por linha. Macros EVENT_MAP são úteis para fragmentos sintáticos, não automaticamente superiores/inferiores para todo caso.

### TRD-0131 — 3.3.4 Features of built-in and object types in templates

- Fonte: [TRD, 3.3.4 Features of built-in and object types in templates, p.PDF 256–260].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Genericidade precisa distinguir valor/ref/class pointer. Max por valor falha struct; ref falha literais; overload const-ref+valor resolve caso mostrado, terceiro argumento discrimina delegação para evitar recursão. Operador> necessário em Dummy; overload T* é mais específico que T=Data*. Data.x no exemplo não inicializado: não interpretar retorno como comparação significativa sem preencher.

### TRD-0132 — 3.3.5 Function templates

- Fonte: [TRD, 3.3.5 Function templates, p.PDF 260–265].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Swap exige copy/assignment; const field pode eliminar copy implícito. QuickSort exige > e faz recursão, sem garantia de stack bounded; default end=start+ArraySize-1 fica incorreto se start nãozero com end omitido, pode acessar além do array. createInstance sem argumentos exige T explícito; quando explícitos, todos template args devem ser fornecidos. overload concreto pode conflitar só em retorno com MyCast gerado.

### TRD-0133 — 3.3.6 Object type templates

- Fonte: [TRD, 3.3.6 Object type templates, p.PDF 265–270].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Class/struct/union template exige tipos explícitos ao instanciar ou herdar. AutoPtr é dono transferível e destructor deleta dinâmico; copy constructor esvazia fonte e generator mostra dois temporários, sem compartilhar ownership. Não tratar como shared_ptr. Defeito potencial: operator=(T*n) free(ptr) antes atribuição não trata n==ptr, invalidando self assignment por ponteiro. Cópia/atribuição implícita não é contrato geral seguro de dono; biblioteca requer auditoria antes adoção. AutoPtr<string> inválido porque não há string*.

### TRD-0134 — 3.3.7 Method templates

- Fonte: [TRD, 3.3.7 Method templates, p.PDF 270–276].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Method template instancia sob demanda e não pode ser virtual; class template pode ter virtual. SimpleArray usa << por const-ref para objetos, overload U por valor para literais e overload P* com consumo de new e cópia. Contrato de ownership não deve ser implícito. expand ignora falha ArrayResize; indices sem validação; casts podem perder precisão; [] retorna cópia de AutoPtr que transfere posse: ler não é necessariamente operação sem efeito. Singleton static é separado por tipo T; não singleton entre programas/terminais.

### TRD-0135 — 3.3.8 Nested templates

- Fonte: [TRD, 3.3.8 Nested templates, p.PDF 276–277].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: Converter<T1,T2> usa union template aninhado e overload[] nas duas direções; exemplo double/ulong roundtrip2^53+1 por bits. Genericidade não garante tamanhos iguais/tipos elegíveis, nem transporte textual; aliases idênticos conflitam overloads e tipos menores podem deixar bytes não definidos.

### TRD-0136 — 3.3.9 Absent template specialization

- Fonte: [TRD, 3.3.9 Absent template specialization, p.PDF 277–281].
- read_scope: `FULL_SECTION_TEXT_AND_STATIC_EXAMPLE_ANALYSIS`.
- Interpretação/aplicação: MQL5 não oferece especialização geral como C++; função template<> concreta é equivalente a overload e não pode coexistir com duplicata. Herança Base2<T,string> fixa parte de tipos, não especialização real. Biblioteca EX5 fechada deve instanciar antecipadamente todos tipos suportados; presença de definição genérica não garante binário exportado para combinação futura.

## Pontos para integração editorial e validação futura

1. Não copiar exemplos como componentes prontos. Foram encontrados riscos concretos em isEqual(0,0), guardas de índice, contador unsigned, random(range), covariância setColor, QuickSort(start), Matrix sem precondições e AutoPtr em self assignment. São conclusões estáticas do trecho citado, não falhas observadas no terminal.
2. O livro tem lapsos editoriais: p50,51,108,118/222,215,223,249. Usar os contratos específicos e confirmar detalhes dependentes da versão em REF/MetaEditor, preservando divergência se não verificada.
3. Double não serve de identidade numérica arbitrária para ulong. Union preserva bits, mas não constitui contrato seguro de persistência/transporte de valor em globals; não propor migração do protocolo do produto a partir do exemplo.
4. Para futura entrega DOCX/PDF, carregar este material como notas de pesquisa, não repetir122minicapítulos; manter paginação física e indicação de análise estática. Nenhum arquivo DOCX foi tocado por este pesquisador.
5. Leitura pendente fora da atribuição: Parte1 p15–41; Parte4 p282–610; Parte5 p611–1048; Parte6 p1049–1561; Parte7 p1562–2045; conclusão p2046–2047. A raiz pode integrar evidência própria dos demais pesquisadores sem converter openings em cobertura integral.

## Fechamento de cobertura atribuída

Partes2+3: 122/122 registros analisados; 239/239 páginas físicas lidas textualmente, inclusive exemplos. Pendências dentro das Partes2+3: nenhuma leitura textual restante. Figuras: não auditadas visualmente. NativeMT5: NOT_RUN. Total TRD581: não concluído por este complemento.
