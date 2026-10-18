# REF — leitura semântica do lote 01 (PDF físico1–355)

Fonte: MQL5 Language REFERENCE.pdf, SHA-256 `9ae05ce748d23ce0de9b230fc6c7093a2af0adc3ce3544244a74e1c7d628d499`, edição do PDF extraída em corpus-fast/REF. BRIEF.md lido. A leitura aqui é do texto extraído exibido e interpretado pelo agente, não varredura automatizada. Páginas1–73 contêm capa/índice; normalizados apenas líderes de pontos, espaços repetidos e brancos. Corpo74–355 exibido integralmente sem normalização. Três saídas truncadas foram reparadas:57–58,137–138,231–233. Todos os hashes originais e páginas exatas constam no JSON.

Aplicações abaixo são propostas de engenharia ancoradas no contexto BRIEF, salvo o fato contextual de que o Monitor é observacional/event driven. Não foi inspecionado código atual neste lote e nenhuma API específica é certificada como já usada. ML/Python/OpenCL/ONNX, matrizes, complexos, DLL, templates e extensões de UI são pesquisa quando não há evidência atual. Exemplos da fonte: **MQL_NOT_RUN**. Imagens, tabelas gráficas/diagramas de memória e screenshots não foram certificados visualmente. Há código já cortado na borda no texto extraído; leitura integral do texto disponível não reconstitui esses caracteres.

## Notas por seção

### REF-0001 — MQL5 Reference [REF, p.PDF 74–7284]

Abertura74–76 distingue EA, indicador, script, serviço, biblioteca e include; EA pode operar, indicador calcula e serviço não exige gráfico. Aplicação: explicar por que o Monitor pode ser EA observacional sem enviar ordens; sua classe não implica permissão de negociar.

Estado: INTRODUCTION_AND_CHILDREN_PARTIAL; texto deste lote: 74–355.

### REF-0002 — Language Basics [REF, p.PDF 77–318]

Capítulo77–318 reúne sintaxe, tipos, expressões, funções, duração, preprocessamento e OOP. Aplicação: base da revisão de contratos MQL; leitura dos filhos dá conteúdo, não multiplicar páginas por sobreposição.

Estado: FULL_TEXT_READ; texto deste lote: 77–318.

### REF-0003 — Syntax [REF, p.PDF 78–82]

Sintaxe78 exclui aritmética de endereços, goto, enum anônimo e herança múltipla. Aplicação proposta: portar ideias C++ só após conferir diferenças reais do compilador.

Estado: FULL_TEXT_READ; texto deste lote: 78–82.

### REF-0004 — Comments [REF, p.PDF 79–79]

Comentários de bloco não aninham; // encerra na quebra. Aplicação proposta: documentação e desativação de trechos sem criar blocos inválidos.

Estado: FULL_TEXT_READ; texto deste lote: 79–79.

### REF-0005 — Identifiers [REF, p.PDF 80–80]

Identificadores têm até63 caracteres, letras latinas, dígitos e underscore, primeiro não numérico; caixa distingue nomes. Aplicação proposta: nomes previsíveis e ausência de colisão reservada.

Estado: FULL_TEXT_READ; texto deste lote: 80–80.

### REF-0006 — Reserved Words [REF, p.PDF 81–82]

Lista81–82 inclui tipos, acesso, armazenamento, operadores e diretivas. Aplicação: referência lexical; não tratar essa lista como inventário exaustivo de funcionalidades novas, pois capítulos posteriores apresentam interface/using/final.

Estado: FULL_TEXT_READ; texto deste lote: 81–82.

### REF-0007 — Data Types [REF, p.PDF 83–164]

83 distingue dados aritméticos, string e compostos; preço usa double, sem tipo monetário próprio. Aplicação proposta: separar unidade financeira, preço e volume no contrato, não confiar no tipo double para distinguir unidades.

Estado: FULL_TEXT_READ; texto deste lote: 83–164.

### REF-0008 — Integer Types [REF, p.PDF 84–97]

84–85 tabela de larguras e aliases C/C++; aliases são nomes alternativos. Aplicação proposta: tickets/tempos e fronteiras de serialização com largura explícita. A coluna Size in Bytes dos aliases contém8/16/32/64, aparente troca bits/bytes; conferir sizeof nativo.

Estado: FULL_TEXT_READ; texto deste lote: 84–97.

### REF-0009 — Char, Short, Int and Long Types [REF, p.PDF 86–89]

86–89 cobrem signed/unsigned, overflow de char no laço, hex e máscara binária de sessões. Aplicação proposta: contadores int e validação antes de converter negativos para unsigned; máscara de horários é exemplo, não regra JPW.

Estado: FULL_TEXT_READ; texto deste lote: 86–89.

### REF-0010 — Character Constants [REF, p.PDF 90–92]

90–92 caracteres são ushort Unicode0–65535, escapes LF/tab/CR/aspas/barra e códigos. Aplicação proposta: logs e rótulos portugueses; escape desconhecido tem resultado indefinido. O texto chama30 de valor de '0' sem explicitar hexadecimal; não ensinar30 decimal.

Estado: FULL_TEXT_READ; texto deste lote: 90–92.

### REF-0011 — Datetime Type [REF, p.PDF 93–93]

93 datetime guarda segundos desde1970 em8bytes e literais D; datas incompletas dependem compilação e geram warning. Aplicação proposta: timestamps explícitos; não deduz timezone da representação inteira.

Estado: FULL_TEXT_READ; texto deste lote: 93–93.

### REF-0012 — Color Type [REF, p.PDF 94–94]

94 color ocupa4bytes com RGB em0x00BBGGRR, distinto de ARGB. Aplicação proposta: indicadores de estado visual; evitar interpretar cores como regras normativas.

Estado: FULL_TEXT_READ; texto deste lote: 94–94.

### REF-0013 — Bool Type [REF, p.PDF 95–95]

95 bool é1byte; zero falso e qualquer outro número verdadeiro. Aplicação proposta: resultados de API exigem interpretação específica antes de virarem permissões; erro numérico não zero não significa sucesso.

Estado: FULL_TEXT_READ; texto deste lote: 95–95.

### REF-0014 — Enumerations [REF, p.PDF 96–97]

96–97 enum nomeado tem4bytes, começa0 e incrementa valor anterior quando omitido. Aplicação proposta: estados e programas diários explícitos; não inventar sequência normativa a partir de ordinal.

Estado: FULL_TEXT_READ; texto deste lote: 96–97.

### REF-0015 — Real Types (double, float) [REF, p.PDF 98–103]

98–103 explicam IEEE754, float32/double64, aproximações, comparação por diferença/tolerância e números inválidos. Aplicação proposta: cálculos e limites exigem validação MathIsValidNumber e tolerância por unidade; NormalizeDouble(diferença,8) é exemplo, não tolerância universal de dinheiro ou risco.

Estado: FULL_TEXT_READ; texto deste lote: 98–103.

### REF-0016 — Complex number (complex) [REF, p.PDF 104–104]

104 complex tem real/imag double e operações limitadas; passagem interna por valor é exceção, DLL por referência. Pesquisa futura, sem uso ML/complexo atual comprovado.

Estado: FULL_TEXT_READ; texto deste lote: 104–104.

### REF-0017 — String Type [REF, p.PDF 105–107]

105–107 string Unicode terminada em zero, literais adjacentes concatenam na compilação; métodos cobrem buffer, recorte, busca, conversão e formato. Aplicação proposta: logs/identificadores com limites explícitos; descrições de conversão na tabela têm aparentes inversões, conferir função detalhada.

Estado: FULL_TEXT_READ; texto deste lote: 105–107.

### REF-0018 — Structures, Classes and Interfaces [REF, p.PDF 108–134]

108–134 estruturas POD, cópia por tipo/linhagem, pack1/2/4/8/16 e offsetof; classes privadas por padrão, vtable, new e construtores; ordem de membros prevalece sobre lista inicializadora. Interfaces sem estado têm métodos puros; union sobrepõe memória e não aceita tipos dinâmicos. Aplicação proposta: snapshots e módulos com propriedade clara; DLL/union só pesquisa se necessário, sem alegar uso atual.

Estado: FULL_TEXT_READ; texto deste lote: 108–134.

### REF-0019 — Dynamic Array Object [REF, p.PDF 135–135]

135 arrays têm até4 dimensões, primeira pode ser dinâmica; destruição ocorre ao sair do escopo. Array estático em estrutura usa objeto temporário quando passado. Aplicação proposta: buffers limitados e conferir retorno de resize; não confundir descriptor com armazenamento redimensionável.

Estado: FULL_TEXT_READ; texto deste lote: 135–135.

### REF-0020 — Matrices and vectors [REF, p.PDF 136–142]

136–142 matrix/vector têm métodos de criação, decomposição, solução, estatística e correlação; produto exige dimensões compatíveis e distingue operações. Pesquisa futura sem integração atual; paralelos NumPy não são prova de mesma assinatura/semântica e tabelas resumidas pedem capítulo detalhado.

Estado: FULL_TEXT_READ; texto deste lote: 136–142.

### REF-0021 — Typecasting [REF, p.PDF 143–147]

143–147 truncamento real→int, promoção antes da operação e destino após resultado;3/2 perde fração mesmo atribuído a double. dynamic_cast falho retorna NULL, cast indevido pode parar programa. Aplicação proposta: preservar tickets inteiros e tornar conversões de unidade explícitas. Faixa long→double publicada não garante todos inteiros representáveis; não reproduzir como garantia.

Estado: FULL_TEXT_READ; texto deste lote: 143–147.

### REF-0022 — Void Type and NULL Constant [REF, p.PDF 148–148]

148 void indica ausência de resultado/parâmetros; NULL pode ser atribuído/comparado a tipos básicos e descritores. Aplicação proposta: distinguir ausência de dado de valor monetário zero mediante estado separado.

Estado: FULL_TEXT_READ; texto deste lote: 148–148.

### REF-0023 — User-defined Types [REF, p.PDF 149–158]

149–158 typedef de ponteiro de função exige assinatura; exemplo TAction delega botões a callbacks com NULL e encaminha eventos ao diálogo. Aplicação proposta para UI futura; não afirmar callbacks existentes. Exemplo contém linhas cortadas na própria extração e screenshots não certificados.

Estado: FULL_TEXT_READ; texto deste lote: 149–158.

### REF-0024 — Object Pointers [REF, p.PDF 159–162]

159–162 ponteiro é descritor8bytes, não endereço aritmético; CheckPointer detecta nulo/destruído e ! faz verificação implícita; ==NULL é teste mais estreito. Aplicação proposta: impedir falha crítica no Monitor por descritor inválido e esclarecer proprietário de cada objeto.

Estado: FULL_TEXT_READ; texto deste lote: 159–162.

### REF-0025 — References: Modifier & and Keyword this [REF, p.PDF 163–164]

163–164 compostos por referência, const protege entrada, arrays copiados com ArrayCopy; this referencia instância e GetPointer(this) produz descritor. Estruturas não aceitam GetPointer/new. Aplicação proposta: APIs de cálculo imutáveis e saída explícita.

Estado: FULL_TEXT_READ; texto deste lote: 163–164.

### REF-0026 — Operations and Expressions [REF, p.PDF 165–180]

165 apresenta famílias de operações e pontuação; filhos166–180 definem contrato. Aplicação: expressões normativas devem tornar precedência e unidades legíveis.

Estado: FULL_TEXT_READ; texto deste lote: 165–180.

### REF-0027 — Expressions [REF, p.PDF 166–166]

166 expressão pode ocupar várias linhas; com ponto-e-vírgula constitui comando. Aplicação proposta: separar etapas de cálculo para auditoria.

Estado: FULL_TEXT_READ; texto deste lote: 166–166.

### REF-0028 — Arithmetic Operations [REF, p.PDF 167–167]

167 prefixo/pós incremento não devem ser combinados em expressão sensível à ordem do compilador. Aplicação proposta: um efeito de estado por instrução; evitar comportamento escondido em cálculos de risco.

Estado: FULL_TEXT_READ; texto deste lote: 167–167.

### REF-0029 — Assignment Operations [REF, p.PDF 168–168]

168 atribuições compostas incluem operações numéricas/bitwise; %= conserva sinal do dividendo. Há descrição left-to-right que conflita com184/179 e seu próprio exemplo x antes de y; ensinar associatividade confirmada e passos explícitos.

Estado: FULL_TEXT_READ; texto deste lote: 168–168.

### REF-0030 — Operations of Relation [REF, p.PDF 169–169]

169 relações retornam0/1; comparação aproximada de reais usa diferença. Aplicação proposta: contratos de fronteira de risco com tolerância documentada, nunca copiar8dígitos para qualquer símbolo.

Estado: FULL_TEXT_READ; texto deste lote: 169–169.

### REF-0031 — Boolean Operations [REF, p.PDF 170–171]

170–171 &&/|| usam curto circuito. Aplicação proposta: validar existência/tamanho antes do acesso e evitar callbacks laterais cuja execução seria pulada.

Estado: FULL_TEXT_READ; texto deste lote: 170–171.

### REF-0032 — Bitwise Operations [REF, p.PDF 172–174]

172–174 bitwise só inteiros, signed right shift estende sinal, unsigned preenche0; deslocamento >=largura é indefinido. Aplicação proposta: flags documentadas com tipos unsigned e contagem de bits limitada.

Estado: FULL_TEXT_READ; texto deste lote: 172–174.

### REF-0033 — Other Operations [REF, p.PDF 175–178]

175–178 índices0..n-1 e acesso fora do array é fatal; :: resolve escopo e sizeof é compilado, array dinâmico retorna tamanho do objeto e não seu payload. Aplicação proposta: validação de limites e qualificadores nas bibliotecas; ordem de argumentos afirmação175 conflita com202/204.

Estado: FULL_TEXT_READ; texto deste lote: 175–178.

### REF-0034 — Precedence Rules [REF, p.PDF 179–180]

179–180 precedência segue C++, difere MQL4; atribuição/ternário associam à direita e vírgula à esquerda. Aplicação proposta: parênteses em fórmulas/flags sem depender de memorização.

Estado: FULL_TEXT_READ; texto deste lote: 179–180.

### REF-0035 — Operators [REF, p.PDF 181–199]

181–182 catálogo de fluxo, @, new e delete. Aplicação: estrutura do processamento observacional; nenhum comando de controle autoriza negociação.

Estado: FULL_TEXT_READ; texto deste lote: 181–199.

### REF-0036 — Compound Operator [REF, p.PDF 183–183]

183 bloco{} agrupa instruções, sem ; após fechamento do comando composto. Aplicação proposta: chaves em condições encadeadas para revisão segura.

Estado: FULL_TEXT_READ; texto deste lote: 183–183.

### REF-0037 — Expression Operator [REF, p.PDF 184–184]

184 expressão; inclui atribuição encadeada direita→esquerda e comando vazio;. Aplicação proposta: identificar ; acidental em guarda de risco.

Estado: FULL_TEXT_READ; texto deste lote: 184–184.

### REF-0038 — Return Operator [REF, p.PDF 185–185]

185 return encerra função e admite básicos/POD/descritor, restringe arrays e classes segundo prosa. Aplicação proposta: funções retornam sucesso e saída explícita; conflito com exemplos CRow/CMatrix218–221 exige compilação antes de regra absoluta.

Estado: FULL_TEXT_READ; texto deste lote: 185–185.

### REF-0039 — Conditional Operator if-else [REF, p.PDF 186–186]

186 else liga ao if anterior mais próximo sem else no mesmo bloco. Aplicação proposta: chaves em decisões de programa diário e impedimento.

Estado: FULL_TEXT_READ; texto deste lote: 186–186.

### REF-0040 — Ternary Operator ?: [REF, p.PDF 187–188]

187–188 ternário executa um ramo mas tipo resultante é decidido em compilação; string pode dominar double e mudar overload. Aplicação proposta: evitar misturar rótulo e valor numérico no mesmo ternário.

Estado: FULL_TEXT_READ; texto deste lote: 187–188.

### REF-0041 — Switch Operator [REF, p.PDF 189–190]

189–190 switch usa int/uint e casos constantes sem valores duplicados; cai nos casos seguintes até break. Aplicação proposta: default explícito para estado desconhecido e impedir fallthrough acidental.

Estado: FULL_TEXT_READ; texto deste lote: 189–190.

### REF-0042 — Loop Operator while [REF, p.PDF 191–191]

191 while testa antes, pode executar zero vezes; laço longo consulta IsStopped. Aplicação proposta: limites de trabalho para não monopolizar processamento do Monitor.

Estado: FULL_TEXT_READ; texto deste lote: 191–191.

### REF-0043 — Loop Operator for [REF, p.PDF 192–192]

192 for permite campos vazios e múltiplas expressões por vírgula; condição ausente é sempre verdadeira. Aplicação proposta: laços finitos e cancelamento cooperativo.

Estado: FULL_TEXT_READ; texto deste lote: 192–192.

### REF-0044 — Loop Operator do while [REF, p.PDF 193–193]

193 do-while executa ao menos uma vez e testa depois. Aplicação proposta: não usar quando zero elementos deve impedir primeiro acesso.

Estado: FULL_TEXT_READ; texto deste lote: 193–193.

### REF-0045 — Break Operator [REF, p.PDF 194–194]

194 break encerra loop/switch mais próximo. Aplicação proposta: documentar saídas por erro sem confundir término de função.

Estado: FULL_TEXT_READ; texto deste lote: 194–194.

### REF-0046 — Continue Operator [REF, p.PDF 195–195]

195 continue inicia próxima iteração do loop mais próximo. Aplicação proposta: filtros de dados válidos; exemplo contém inconsistência array/a e não deve ser copiado literalmente.

Estado: FULL_TEXT_READ; texto deste lote: 195–195.

### REF-0047 — Matrix product operator [REF, p.PDF 196–197]

196–197 @ implementa produto matricial, tipos iguais e dimensões conformes; vetor esquerdo linha, direito coluna, vetor×vetor escalar, precedência multiplicativa. Pesquisa futura; página104 diz operações complexas matriciais não implementadas e196 anuncia suporte, portanto validar build concreto.

Estado: FULL_TEXT_READ; texto deste lote: 196–197.

### REF-0048 — Object Create Operator new [REF, p.PDF 198–198]

198 new cria apenas classe e retorna NULL se falha; arrays de objetos crescem por ArrayResize; deve haver delete. Aplicação proposta: falha de alocação não pode liberar estado operacional.

Estado: FULL_TEXT_READ; texto deste lote: 198–198.

### REF-0049 — Object Delete Operator delete [REF, p.PDF 199–199]

199 delete chama destrutor/libera objeto e invalida descritor; exemplo redefineNULL. Aplicação proposta: limpar referências e impedir uso posterior ou dupla exclusão.

Estado: FULL_TEXT_READ; texto deste lote: 199–199.

### REF-0050 — Functions [REF, p.PDF 200–236]

200–201 protótipo deve corresponder definição, até64parâmetros, defaults constantes e todos posteriores também default. Aplicação proposta: funções pequenas e contratos estáveis, sem sobrecarregar API com defaults ambíguos.

Estado: FULL_TEXT_READ; texto deste lote: 200–236.

### REF-0051 — Function Call [REF, p.PDF 202–202]

202 funções globais não podem ser definidas dentro de outra; não se pode pular parâmetro intermediário default. Aplicação proposta: calcular argumentos em variáveis separadas, pois202 não garante ordem e204 descreve ordem inversa.

Estado: FULL_TEXT_READ; texto deste lote: 202–202.

### REF-0052 — Passing Parameters [REF, p.PDF 203–205]

203–205 valor não altera argumento, referência altera; compostos por referência e const evita mutação. Aplicação proposta: separar consulta de modificação e evitar i++ em chamadas; exemplo documenta avaliação inversa, não transformar dependência de ordem em desenho.

Estado: FULL_TEXT_READ; texto deste lote: 203–205.

### REF-0053 — Function Overloading [REF, p.PDF 206–208]

206–208 overload escolhe correspondência exata, promoção, conversão; retorno isolado não distingue sobrecarga e defaults podem esconder função de sistema. Aplicação proposta: nomes/domínios claros ou cast explícito sem apagar erro de unidade.

Estado: FULL_TEXT_READ; texto deste lote: 206–208.

### REF-0054 — Operation Overloading [REF, p.PDF 209–221]

209–221 operator sobrecarrega aritmética/indexação; implementações de CRow/CMatrix mostram cópia profunda e dimensionalidade. Pesquisa futura, sem substituição do core atual. Texto209 nega complex apesar104; !complex213 parece contrário ao teste de zero; produto220–221 usa cols1 em vez de cols2 e só demonstra matrizes quadradas, não aceitar como algoritmo geral.

Estado: FULL_TEXT_READ; texto deste lote: 209–221.

### REF-0055 — Description of External Functions [REF, p.PDF 222–223]

222–223 import exige protótipos e bibliotecas EX5 exportadas; escopo é nome da biblioteca e nomes DLL/EX5 devem diferir. Pesquisa futura sem DLL atual comprovada; tamanhos HWND antigos precisam revisão da arquitetura.

Estado: FULL_TEXT_READ; texto deste lote: 222–223.

### REF-0056 — Exporting Functions [REF, p.PDF 224–224]

224 export inclui função na tabela pública EX5 e #property library classifica módulo. Pesquisa futura: modularização binária tem contrato diferente de include fonte; não alegar biblioteca instalada.

Estado: FULL_TEXT_READ; texto deste lote: 224–224.

### REF-0057 — Event Handling Functions [REF, p.PDF 225–236]

225–236 assinaturas de eventos são exatas; init int rejeita configuração/falha/agente; OnTick só EA e não obrigatório; timer cria/destrói em Init/Deinit. TradeTransaction tem1024itens, chegada não garantida e estado muda durante handler; request/result só REQUEST; OnTrade não1:1. Indicador OnCalculate usa prev_calculated retornado e zera com história alterada, direção deve ser explícita. Aplicação proposta central: Monitor observacional event driven, handlers curtos, reconciliação por estado e nenhuma equivalência entre evento e autorização de operar; testes de otimização são pesquisa/harness, não prova do produto.

Estado: FULL_TEXT_READ; texto deste lote: 225–236.

### REF-0058 — Variables [REF, p.PDF 237–262]

237–240 variáveis declaradas antes do uso, arrays até4dimensões, estático não AsSeries, limites fatais; métodos modernos e classes de armazenamento. Aplicação proposta: inspeção de entradas e distinção de dados disponíveis/ausentes.

Estado: FULL_TEXT_READ; texto deste lote: 237–262.

### REF-0059 — Local Variables [REF, p.PDF 241–242]

241–242 locais têm escopo de bloco e shadowing; stack indicador1MB/EA8MB padrão; estáticos/dinâmicos fora stack. Aplicação proposta: evitar grandes snapshots locais e recursão, identificar nomes ocultos.

Estado: FULL_TEXT_READ; texto deste lote: 241–242.

### REF-0060 — Formal Parameters [REF, p.PDF 243–244]

243–244 parâmetros são locais, defaults trailing e referência sem default; máximo64. Aplicação proposta: const em snapshots e validação de retorno antes de usar saída.

Estado: FULL_TEXT_READ; texto deste lote: 243–244.

### REF-0061 — Static Variables [REF, p.PDF 245–246]

245–246 static local persiste entre chamadas, inicializa uma vez e zero se omitido, escopo continua local. Aplicação proposta: estado entre eventos exige reset explícito quando necessário; persistência não atravessa reinstalação/reinicialização do programa.

Estado: FULL_TEXT_READ; texto deste lote: 245–246.

### REF-0062 — Global Variables [REF, p.PDF 247–247]

247 global é pool do programa, inicializa antes Init e não é GlobalVariable do terminal. Aplicação proposta: não prometer persistência entre sessões a partir de global MQL.

Estado: FULL_TEXT_READ; texto deste lote: 247–247.

### REF-0063 — Input Variables [REF, p.PDF 248–254]

248–254 input é leitura interna, reinicializa antesInit, string valor limitado por nome (254-nome), tipos complexos/arrays proibidos; input(name) prevalece comentário; sinput exclui otimização por UI mas ParameterSetRange pode variá-lo; group agrupa. Aplicação proposta: parametrização dos programas com validação emInit, sem chamar sinput trava normativa imutável.

Estado: FULL_TEXT_READ; texto deste lote: 248–254.

### REF-0064 — Extern Variables [REF, p.PDF 255–255]

255 extern de mesmo tipo/nome entre fontes compartilha pool e só uma inicialização. Pesquisa futura/refatoração; não equivaler extern a input editável pelo usuário.

Estado: FULL_TEXT_READ; texto deste lote: 255–255.

### REF-0065 — Initialization of Variables [REF, p.PDF 256–257]

256–257 inicialização parcial zera elementos restantes, {} zera estrutura; locais sem valor explícito podem ser indefinidos. Aplicação proposta: snapshots/request inicializados e indicadores de validade; frase ampla sem inicialização conflita com zero explícito dos globais/static em245/247.

Estado: FULL_TEXT_READ; texto deste lote: 256–257.

### REF-0066 — Visibility Scope and Lifetime of Variables [REF, p.PDF 258–259]

258–259 duração e visibilidade são dimensões diferentes: localstatic vive programa mas visível bloco. Aplicação proposta: revisar pesos/acumuladores em recalculação; exemplo weightsum+= no reset ilustra risco de acumular ao recalcular, não copiar indiscriminadamente.

Estado: FULL_TEXT_READ; texto deste lote: 258–259.

### REF-0067 — Creating and Deleting Objects [REF, p.PDF 260–262]

260–262 automáticos criam em declaração e destroem reverso, globais antes função; new/delete independem declaração, vazamentos são logados na descarga. Memória de classes usa pool, arrays devolvem SO. Aplicação proposta: posse documentada, limpeza emDeinit e falha fechada de alocação; ausência de vazamento no unload não prova limpeza correta em execução longa.

Estado: FULL_TEXT_READ; texto deste lote: 260–262.

### REF-0068 — Preprocessor [REF, p.PDF 263–279]

263–264 preprocessador transforma texto antes compilação, continua linha por barra e ## junta tokens. Aplicação proposta: manifestar configuração de build e includes, sem confundir diretiva com condição em runtime.

Estado: FULL_TEXT_READ; texto deste lote: 263–279.

### REF-0069 — Macro substitution (#define) [REF, p.PDF 265–267]

265–267 macro substitui token fora strings/comentários, até8args, parênteses protegem precedência, undef cancela. Aplicação proposta: evitar argumentos com efeitos colaterais e usar função tipada quando possível.

Estado: FULL_TEXT_READ; texto deste lote: 265–267.

### REF-0070 — Program Properties (#property) [REF, p.PDF 268–273]

268–273 #property vale arquivo principal, inclui versão31chars/descrição511, buffers/plots, dependências tester e stack16MB tester. tester_no_cache não evita gravar resultado; força recalcular; indicador tester geralmente calcula sob demanda salvo flags/eventos/visual. Aplicação proposta: recibos distinguem configuração/cache/compilação de execução nova; propriedades não substituem teste nativo.

Estado: FULL_TEXT_READ; texto deste lote: 268–273.

### REF-0071 — Including Files (#include) [REF, p.PDF 274–274]

274 include<> busca diretório padrão sem atual, aspas busca diretório fonte sem padrão. Aplicação proposta: reproducibilidade e prevenção de arquivo homônimo errado no kit; sem editar kit neste lote.

Estado: FULL_TEXT_READ; texto deste lote: 274–274.

### REF-0072 — Importing Functions  (#import) [REF, p.PDF 275–277]

275–277 imports fazem early binding, compilador não valida ABI real e tipos dinâmicos são restritos; arquitetura32/64 muda protótipo e .NET admite POD/static públicos. Pesquisa futura, sem habilitar DLL ou instalar dependência.

Estado: FULL_TEXT_READ; texto deste lote: 275–277.

### REF-0073 — Conditional Compilation (#ifdef, #ifndef, #else, #endif) [REF, p.PDF 278–279]

278–279 ifdef/ifndef testa definição de macro, else/endif escolhe texto; __MQL5__,_DEBUG,_RELEASE permitem variantes. Aplicação proposta: registrar modo exato do build para repetir evidência; flag de teste não é controle de permissão em runtime.

Estado: FULL_TEXT_READ; texto deste lote: 278–279.

### REF-0074 — Object-Oriented Programming [REF, p.PDF 280–315]

280–281 introdução OOP liga estado/comportamento, abstração e reutilização por herança. Aplicação proposta: modelar contratos pequenos, não converter todo core por preferência abstrata.

Estado: FULL_TEXT_READ; texto deste lote: 280–315.

### REF-0075 — Encapsulation and Extensibility of Types [REF, p.PDF 282–284]

282–284 encapsulamento oculta implementação e expõe get/set; troca interna pode preservar API. Aplicação proposta: impedir mudança externa de estado validado, mantendo fórmula normativa separada de apresentação.

Estado: FULL_TEXT_READ; texto deste lote: 282–284.

### REF-0076 — Inheritance [REF, p.PDF 285–291]

285–291 herança única, base constrói primeiro/destrói por último; private/protected/public controlam acesso, métodos homônimos ocultam base e using recupera overloads/pode ampliar acesso. Aplicação proposta: revisar API por build e não assumir semântica de compiladores antigos.

Estado: FULL_TEXT_READ; texto deste lote: 285–291.

### REF-0077 — Polymorphism [REF, p.PDF 292–295]

292–295 polimorfismo por descritor base despacha método virtual do objeto real; verificar CheckPointer e delete só POINTER_DYNAMIC. Aplicação proposta futura: estratégias de apresentação intercambiáveis sem armar Supervisor.

Estado: FULL_TEXT_READ; texto deste lote: 292–295.

### REF-0078 — Overload [REF, p.PDF 296–296]

296 overload métodos segue correspondência por níveis descritos, mas capítulo herança289 atualiza ocultação. Aplicação proposta: qualificar base/using explicitamente e compilar caso mínimo; não confiar no resumo histórico isolado.

Estado: FULL_TEXT_READ; texto deste lote: 296–296.

### REF-0079 — Virtual Functions [REF, p.PDF 297–300]

297–300 virtual seleciona em runtime; destrutores sempre virtuais; override faz compilador rejeitar assinatura errada, final proíbe nova redefinição. Aplicação proposta: contratos de módulos eventuais com override obrigatório e testes de despacho.

Estado: FULL_TEXT_READ; texto deste lote: 297–300.

### REF-0080 — Static Members of a Class [REF, p.PDF 301–304]

301–304 static membro é compartilhado entre instâncias e inicializado globalmente; static método não tem this nem membro instância; const método protege estado. Aplicação proposta: não usar contador static como se isolado por objeto/conta; usar pureza/const nas consultas.

Estado: FULL_TEXT_READ; texto deste lote: 301–304.

### REF-0081 — Function templates [REF, p.PDF 305–308]

305–308 templates geram função por tipo, até8parâmetros, não export/virtual/import; overload especializado pode tratar caso específico. Pesquisa futura: utilitários tipados. Exemplo bool/string usa StringCompare como booleano e parece inverter 'true'; não usar como parser seguro.

Estado: FULL_TEXT_READ; texto deste lote: 305–308.

### REF-0082 — Class templates [REF, p.PDF 309–313]

309–313 templates de classe servem containers, métodos externos repetem template; acesso seguro deve distinguir erro em vez de devolver valor silencioso. Pesquisa futura/harness; exemplo TSafeArray retorna static invalid_value e pode mascarar ausência como zero; há ArraySize sem argumento e template Value suspeitos no texto.

Estado: FULL_TEXT_READ; texto deste lote: 309–313.

### REF-0083 — Abstract Classes [REF, p.PDF 314–315]

314–315 classe com método puro=0/NULL não instancia; descendente implementa todos; chamar puro no construtor dá erro crítico/resultado indefinido. Aplicação futura: fronteiras abstratas sem chamadas virtuais dependentes do descendente durante construção.

Estado: FULL_TEXT_READ; texto deste lote: 314–315.

### REF-0084 — Namespaces [REF, p.PDF 316–318]

316–318 namespace pode reabrir em arquivos e aninhar; :: global desambigua funções e include pode ser envolvido em namespace. Aplicação proposta: evitar colisões de módulos e bibliotecas; não alegar namespaces já existentes sem ver fonte.

Estado: FULL_TEXT_READ; texto deste lote: 316–318.

### REF-0085 — Constants, Enumerations and Structures [REF, p.PDF 319–1040]

319 abre agrupamento de constantes/estruturas até1040. Só introdução319 e filhos320–355 lidos neste lote; demais filhos ficam para lotes seguintes. Aplicação: organizar consulta tipada, não certificar capítulo inteiro pela introdução.

Estado: INTRODUCTION_AND_CHILDREN_PARTIAL; texto deste lote: 319–355.

### REF-0086 — Chart Constants [REF, p.PDF 320–400]

320 apresenta eventos/timeframes/propriedades/navegação/representação até400. Parte efetivamente lida320–355; finalidade: apresentação do Monitor, sem regras de risco inferidas de aparência.

Estado: INTRODUCTION_AND_CHILDREN_PARTIAL; texto deste lote: 320–355.

### REF-0087 — Types of Chart Events [REF, p.PDF 321–329]

321–329 enum eventos inclui KEYUP e mousewheel, focus necessário, TranslateKey trata teclas mortas; payload muda porid, mouse flags bits1/2/4/8/16/32/64 e wheel empacota coord/flags emlong. Aplicação proposta: UI acessível e roteamento estrito; só interação, sem armar operações. Contagem11eventos/custom65535 parece desatualizada frente tabela/range inclusivo; usar IDs e limites verificados.

Estado: FULL_TEXT_READ; texto deste lote: 321–329.

### REF-0088 — Chart Timeframes [REF, p.PDF 330–331]

330–331 timeframes nomeadosM1..MN1 com PERIOD_CURRENT ligado ao gráfico; ENUM_SERIESMODE distingue preços/volumes/spread. Aplicação proposta: timeframe explícito nos cálculos/reprodução, evitando mudança silenciosa ao trocar gráfico; não mapear ordinal para minutos.

Estado: FULL_TEXT_READ; texto deste lote: 330–331.

### REF-0089 — Chart Properties [REF, p.PDF 332–339]

332–339 propriedades porInteger/Double/String, r/o/w/o e modificador subjanela; setters enfileiram comando, não atualização visual imediata. ChartRedraw força refresh; gráfico oculto ainda desenha objetos, scrolling e controles são distintos. Aplicação proposta: painel Monitor com restauração de preferências e evidência visual separada de bool do setter; CHART_DRAG_TRADE_LEVELS/ONE_CLICK são UI e não autorização normativa.

Estado: FULL_TEXT_READ; texto deste lote: 332–339.

### REF-0090 — Positioning Constants [REF, p.PDF 340–340]

340 ChartNavigate usa BEGIN/CURRENT_POS/END e deslocamento; exemplo desliga autoscroll antes navegação. Aplicação proposta: inspeção histórica reproduzível sem confundir barra visível com série de cálculo.

Estado: FULL_TEXT_READ; texto deste lote: 340–340.

### REF-0091 — Chart Representation [REF, p.PDF 341–342]

341–342 modos BARS/CANDLES/LINE e volumes HIDE/TICK/REAL. Aplicação proposta: legenda distingue tickvolume de volume negociado; representação não altera contrato financeiro.

Estado: FULL_TEXT_READ; texto deste lote: 341–342.

### REF-0092 — Examples of Working with the Chart [REF, p.PDF 343–400]

343–355 leitura parcial de exemplos343–400: getters bool+out distinguem erro de false; ResetLastError antes consulta e GetLastError só emfalha; modo usa WRONG_VALUE e escala-1; setters indicam enfileiramento. Cobertos IS_OBJECT,BRING_TO_TOP,MOUSE_SCROLL,EVENT_MOUSE_MOVE,OBJECT_CREATE/DELETE,MODE,FOREGROUND,SHIFT,AUTOSCROLL,SCALE,SCALEFIX,1:1,POINTS_PER_BAR e getterOHLC; setterOHLC começa após corte355. Aplicação proposta: padrão de erro para UI, sem copiar painel nem comprovar runtime. Fila exata356–400.

Estado: PARTIAL_AT_BATCH_BOUNDARY; texto deste lote: 343–355.

## Crítica de fonte e limites para o manual

As divergências internas não invalidam o estudo, mas impedem copiar exemplos como especificação única. Reconciliar em capítulos detalhados e no compilador/build escolhido: ordem de avaliação175/202/204; retorno de objetos185/200 versus218–221; complex104 versus209 e suporte matricial196; inicialização245/247 versus256/260; ocultação/using289–290 versus resumo296. O valor double possui53bits de precisão significativa: a faixa publicada145–146 não deve virar promessa de exatidão para todos os tickets64bits. A porcentagem de0x55 no comentário131 é inconsistente com85/255; o número33,3% é inferência aritmética, não teste MQL. O produto CMatrix220–221 precisa colunas da saída, não cols1, para matrizes retangulares. A expressão !complex213 e parser bool308 exigem crítica antes de reaproveitar.

Não há execução MT5/EX5, instalação, kit, piloto, alteração produtiva ou aceitação humana neste lote. A fila textual do intervalo atribuído está vazia. A seção REF-0092 continua356–400, fora do intervalo atribuído; os pais REF-0001,0085,0086 permanecem parciais porque abrangem outros lotes. A próxima leitura começa no setterOHLC que continua na356.
