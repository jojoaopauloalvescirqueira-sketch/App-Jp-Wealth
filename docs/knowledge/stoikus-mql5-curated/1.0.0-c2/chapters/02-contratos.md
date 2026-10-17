# 2. Tipos, unidades e contratos: transformar uma intenção em comportamento verificável

Um contrato técnico conecta quatro coisas: o significado de uma entrada, sua representação computacional, as condições necessárias para usá-la e a evidência exigida para aceitar a saída. No contexto do Stoikus, a primeira precaução é distinguir o número calculado pelo monitor, a regra normativa que dá significado a esse número e uma eventual decisão do operador. Uma variável `double limite` não informa se contém dinheiro, porcentagem, pontos ou uma razão. O compilador verifica o tipo da linguagem; o projeto precisa verificar a unidade e a origem do valor.

Considere uma função que recebe patrimônio e percentual para calcular um limite monetário. Ela precisa definir se o percentual chega como `2.0` ou `0.02`, qual moeda caracteriza o patrimônio e o que acontece quando os dados estão indisponíveis. Os dois primeiros valores são representáveis pelo mesmo tipo. Uma discrepância de convenção multiplica o resultado por cem sem necessariamente produzir erro de compilação. Por isso, nomes como `percentual_0_100` e `fracao_0_1`, validação na fronteira e uma única conversão documentada têm valor maior que comentários genéricos sobre precisão.

## 2.1 Representação numérica e significado econômico

MQL5 oferece inteiros de diferentes larguras e tipos de ponto flutuante. A referência documenta `int` como inteiro de quatro bytes e `long` e `ulong` como inteiros de oito bytes. Os intervalos e o sinal fazem parte do contrato. Armazenar um identificador em `double` porque ele parece um número mistura identidade e grandeza: a representação binária de ponto flutuante tem precisão finita, enquanto o identificador precisa de igualdade exata. Uma contagem, um horário e um identificador também não devem compartilhar operações apenas porque há conversões possíveis entre suas representações. [REF, Data Types/Integer Types, p. PDF 84; TRD, 2.2, p. PDF 45–47]

`double` ocupa oito bytes e `float` quatro, com representações IEEE 754 e precisões diferentes. Em um vetor de milhões de elementos, essa diferença afeta memória, transferência e desempenho. Em cálculo financeiro, afeta os erros de arredondamento. A escolha precisa seguir a tolerância do problema, e não a crença de que uma impressão com duas casas torna o cálculo decimal exato. Um resultado exibido como `1.10` continua sendo um número binário aproximado. Também não é correto chamar qualquer diferença abaixo de um centavo de irrelevante: a unidade da variável e sua função determinam a tolerância. [REF, Real Types, p. PDF 98–99]

Uma comparação numérica geral pode empregar uma tolerância absoluta e outra relativa:

$$
|a-b|\leq \varepsilon_a+\varepsilon_r\max(|a|,|b|).
$$

A tolerância absoluta protege a vizinhança de zero; a relativa acompanha a escala. Essa expressão é uma proposta de verificação numérica, não uma regra de arredondamento financeiro do Stoikus. Antes de aplicá-la a um limite normativo, é preciso saber se a regra exige truncamento, arredondamento ou comparação exata em unidades monetárias discretas. Converter dinheiro em inteiros de centavos pode ser útil em um domínio definido, mas exige contrato para moedas, escalas e conversões. Não elimina automaticamente problemas de cotação ou conversão cambial.

Os estados inválidos merecem representação própria. Zero pode significar saldo legítimo, quantidade vazia ou cálculo impossível que acabou recebendo um valor padrão. Quando essas situações são indistinguíveis, o fluxo posterior assume uma autorização que nunca ocorreu. Uma interface pode retornar sucesso ou falha e preencher a saída apenas no sucesso; outra pode devolver uma estrutura com estado, valor e motivo. A decisão essencial é que o consumidor consiga distinguir ausência de dado de dado igual a zero.

## 2.2 Conversões e fronteiras que realmente precisam de validação

Um cast explicita uma conversão; não prova que ela preserva a intenção. Antes de reduzir largura, remover sinal ou transformar uma grandeza real em inteira, deve-se verificar intervalo e política de perda da parte fracionária. Uma divisão entre inteiros merece atenção: converter apenas o resultado não restaura uma fração já descartada durante a avaliação. Em expressões de razão, a promoção deve ocorrer antes da divisão e o denominador precisa ter significado e domínio válidos. Estes são critérios de revisão derivados dos contratos de representação, a aplicar de acordo com as regras de conversão documentadas pela linguagem.

A fronteira pode ser um arquivo, um parâmetro de entrada, uma resposta de API ou um objeto reconstruído de armazenamento. Validar apenas o controle visual não protege as demais rotas. A validação deve ocorrer onde o dado externo se torna dado de domínio e, a partir dali, estabelecer invariantes claros. Uma sequência plausível é verificar presença, tipo interpretável, finitude, intervalo e coerência entre campos. Um percentual finito no intervalo permitido ainda pode ser incompatível com uma configuração cujo outro limite seja menor.

Não se deve corrigir silenciosamente um arquivo incompatível apenas para satisfazer um tipo esperado. Em um sistema auditável, rejeitar o estado com motivo explícito preserva a possibilidade de diagnóstico. Aplicar um valor padrão pode ser correto para um campo opcional ausente, desde que a versão do esquema e a política de migração autorizem essa interpretação. Campo ausente, valor inválido e versão desconhecida são condições distintas.

O exemplo abaixo é original, sintético e não integra o código produtivo. Seu propósito é mostrar a separação entre sucesso e valor; os intervalos econômicos foram escolhidos para a demonstração, sem atribuí-los às regras JP Wealth.

```mql5
bool LimiteDemonstrativo(const double patrimonio,
                        const double percentual_0_100,
                        double &valor_monetario)
  {
   if(!MathIsValidNumber(patrimonio) ||
      !MathIsValidNumber(percentual_0_100))
      return false;
   if(patrimonio < 0.0 || percentual_0_100 < 0.0 ||
      percentual_0_100 > 100.0)
      return false;
   double candidato = patrimonio * (percentual_0_100 / 100.0);
   if(!MathIsValidNumber(candidato))
      return false;
   valor_monetario = candidato;
   return true;
  }
```

A função `MathIsValidNumber` rejeita NaN e infinitos conforme seu contrato documentado. [REF, MathIsValidNumber, p. PDF 1986]

O chamador precisa conferir o retorno. A saída permanece sem alteração na falha, o que deve constar do contrato. Em outro desenho, zerá-la na entrada pode ser uma escolha legítima, mas aumenta o risco de o chamador ignorar o estado e consumir zero. Nenhuma dessas políticas substitui uma revisão das chamadas. Este exemplo não recebeu compilação nativa nesta entrega.

## 2.3 Arrays: tamanho, conteúdo e ordem são propriedades independentes

Um array organiza elementos do mesmo tipo, mas seu tamanho não descreve sozinho a informação armazenada. O programador precisa conhecer quantos elementos foram efetivamente preenchidos, a ordem temporal e o significado de cada posição. O livro de programação distingue número de elementos e consumo de memória; também apresenta arrays fixos e dinâmicos e as dimensões admitidas. Quando há strings ou objetos associados, estimar memória apenas pela multiplicação de elementos por tamanho do tipo pode ser insuficiente. [TRD, 2.4, p. PDF 82–84]

Uma função que espera uma janela de observações deve aceitar somente a quantidade realmente disponível. Reservar espaço para cem barras não prova que cem barras válidas foram copiadas. Um resultado parcial precisa ter destino definido: rejeitar, aguardar dados ou reduzir a janela por uma política explícita. Completar o restante com zeros pode criar padrões artificiais, inclusive para modelos estatísticos. O mesmo cuidado vale para timestamps: duas séries de igual comprimento podem representar horários diferentes.

A ordem temporal é parte do contrato. Índice zero pode ser adotado como observação mais recente ou mais antiga conforme a estrutura e sua configuração. O adaptador deve estabelecer uma convenção, e a função matemática deve recebê-la de forma inequívoca. Para uma média de janela sem pesos, inverter a ordem pode preservar o resultado e ocultar o erro. Para um retorno defasado, uma convolução ou uma LSTM, a inversão altera o problema. Um teste útil usa uma sequência curta assimétrica e timestamps conhecidos; uma sequência constante não detecta esse defeito.

Redimensionamento frequente também pertence à análise. A política de capacidade afeta tempo e memória; a política de inicialização afeta a validade semântica. O capítulo não presume que variáveis locais ou campos numéricos tenham recebido automaticamente o estado de domínio desejado. O livro demonstra que determinados campos numéricos de estruturas sem inicialização explícita não devem ser tratados como prontos para consumo. Um construtor ou inicializador precisa deixar cada instância em um estado permitido, inclusive quando ainda não há dados. [TRD, 3.1, p. PDF 167–173]

## 2.4 Estruturas, classes e propriedade de recursos

Uma estrutura pode transportar valores relacionados: valor, timestamp, unidade e estado de validação. Uma classe é útil quando precisa defender invariantes por meio de métodos e controlar alterações. O critério é responsabilidade, não uma preferência estética por orientação a objetos. O livro distingue o uso de estruturas como agrupamento de dados e de classes para restringir acesso e manter regras. Os detalhes de layout também importam quando há serialização binária ou integração externa: não se deve presumir equivalência de disposição com uma estrutura C++ sem conferir o contrato de ambos os lados. [TRD, 3.1, p. PDF 167–174; REF, Structures, Classes and Interfaces, p. PDF 108]

Em MQL5, um ponteiro de objeto é um descritor, e não um endereço de memória arbitrário como em C++. A referência destaca essa diferença. Isso impede transportar automaticamente intuições sobre aritmética de ponteiros e acesso bruto à memória. Um descritor pode referir-se a objeto automático ou criado dinamicamente; a estratégia de destruição depende dessa origem. `CheckPointer` ajuda a identificar a categoria, mas não decide quem é o proprietário lógico do objeto. [REF, Object Pointers, p. PDF 159–160; TRD, 3.2.13, p. PDF 205]

O contrato de propriedade deve responder quem cria, quem utiliza, quem libera e o que acontece durante uma inicialização parcial. Se uma rotina aloca três recursos e falha no terceiro, os dois primeiros continuam exigindo tratamento. No caso de uma rede com camadas, buffers e contexto OpenCL, a questão deixa de ser apenas memória: alguns objetos compartilham o mesmo contexto, e uma destruição prematura invalida dependentes. A ordem de liberação deve acompanhar o grafo de dependências.

`const` comunica e restringe modificações na interface apropriada. O livro recomenda preservar essa informação ao longo da cadeia de chamadas, em vez de removê-la até que o código compile. Objetos e arrays exigem atenção à passagem por referência; parâmetros simples podem ser passados por valor ou referência. Uma assinatura aparentemente pequena pode conceder ao chamado capacidade de modificar o estado do chamador. A revisão deve comparar essa capacidade com a responsabilidade efetiva da função. [REF, References, p. PDF 163–164; TRD, 2.8.4, p. PDF 141–143; TRD, 3.2.21, p. PDF 246–248]

## 2.5 Critério de aceitação aplicado

Um contrato útil produz verificações concretas: limites inferiores e superiores, valores fora do domínio, falta de dados, quantidade parcial, ordem temporal invertida, repetição de inicialização e falha após alocação parcial. Cada caso deve ter saída e motivo esperados. A aprovação não deve depender apenas de uma captura visual com números plausíveis.

Para o Stoikus, essa disciplina serve para avaliar futuras mudanças sem alterar regras financeiras nesta pesquisa. Um teste sintético de tipos ou arrays prova uma propriedade localizada; não prova a conformidade normativa de toda a aplicação. Uma análise host também não substitui compilação no MetaEditor, execução no terminal e aceitação do proprietário. O contrato deve registrar qual dessas camadas foi efetivamente observada. Essa distinção permite reutilizar a evidência sem ampliá-la indevidamente.

Há uma distinção operacional importante entre trocar a direção de indexação e reorganizar fisicamente os elementos. `ArraySetAsSeries` altera a convenção de acesso de arrays dinâmicos unidimensionais; a documentação exclui arrays estáticos e multidimensionais dessa opção. Assim, duas rotinas que compartilham um array podem discordar sobre a interpretação dos índices mesmo sem movimentação dos dados. A fronteira deve conferir a direção ou percorrer explicitamente a sequência pretendida. [REF, ArraySetAsSeries, p. PDF 1263; REF, Indexing Direction, p. PDF 2201–2202; TRD, 4.3.8, p. PDF 378–379]

A referência também demonstra a diferença entre divisão inteira e divisão promovida antes da operação. Um cast aplicado ao resultado de `3/2` não devolve o valor `1.5`; é necessário tornar real um operando antes da divisão. Para descritores de classes, uma conversão forçada incompatível pode provocar erro crítico; `dynamic_cast` oferece verificação em execução e pode retornar `NULL`, que precisa ser tratado. Esses mecanismos resolvem problemas distintos: um trata representação numérica, o outro trata compatibilidade na hierarquia de objetos. Revisões devem nomear qual propriedade está sendo verificada, em vez de recomendar genericamente “adicionar casts”. [REF, Typecasting, p. PDF 144–147]
