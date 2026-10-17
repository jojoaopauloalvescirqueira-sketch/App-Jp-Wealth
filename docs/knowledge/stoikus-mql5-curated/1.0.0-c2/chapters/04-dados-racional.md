# 4. Dados e racional financeiro

## 4.1 Uma medida começa pela pergunta

A confiabilidade de uma métrica depende da correspondência entre a pergunta, os dados observados e a interpretação do resultado. Um programa pode calcular uma divisão corretamente e ainda responder a outra pergunta. Alavancagem da conta, risco até o stop e variação do patrimônio usam denominadores, conjuntos de posições e referências temporais diferentes. A engenharia precisa carregar essas distinções desde a aquisição até a tela e o relatório. Uma legenda acrescentada no final não recupera a proveniência que se perdeu durante o cálculo.

No Stoikus, o núcleo de alavancagem separa conta, posição, instrumento, cotação e rota de conversão. A amostra aceita acrescenta contexto, unidade, qualidade, origem e validade. Essa composição oferece uma base concreta para o racional do programa: uma leitura financeira deve ser uma afirmação verificável sobre um conjunto identificado, em determinada unidade e sob condições declaradas. O valor numérico é apenas uma parte da afirmação. O contrato da plataforma informa como obter propriedades; a aplicação decide quais propriedades bastam para sustentar a leitura pretendida. [REF, Account Information, p.PDF 2058–2062; código observado: `JPW_Alavancagem_Core.mqh` e `JPW_Alavancagem_Samples.mqh`.]

A primeira especificação de uma métrica deve responder: qual conjunto está sendo medido, qual instante interessa, qual moeda representa os valores, como tratar entradas ausentes e em que condição o resultado deixa de ser utilizável. Essas respostas orientam os testes antes da implementação. Para exposição da conta, o conjunto deve ser completo para o escopo assumido. Para risco de um grupo, a seleção por símbolo e direção precisa estar estabelecida. Para um estudo gráfico, a identidade das âncoras e da fonte é parte do dado. Compartilhar um gráfico não torna esses três conjuntos equivalentes.

## 4.2 APIs retornam valores e condições de uso

`AccountInfoDouble` fornece propriedades como saldo, patrimônio e lucro. `SymbolInfoDouble` tem uma forma que retorna diretamente o número e outra que devolve sucesso e escreve numa referência. Esta segunda forma ajuda a distinguir falha da consulta de um número legitimamente igual a zero. O catálogo também recomenda `SymbolInfoTick` para obter informações do último tick em uma estrutura, evitando compor Bid, Ask e tempo a partir de chamadas independentes. Ainda assim, sucesso da API não comprova que a cotação atende à atualidade exigida pela aplicação. [REF, AccountInfoDouble, p.PDF 2059; SymbolInfoDouble, p.PDF 2147–2148; SymbolInfoTick, p.PDF 2155.]

Há duas validações diferentes. A validação estrutural pergunta se a chamada retornou, se os campos existem e se o número é finito. A validação econômica pergunta se os dados representam a mesma conta, o mesmo instrumento, a unidade correta e um momento aceitável. Um retorno verdadeiro com cotação antiga satisfaz a primeira e pode violar a segunda. Por isso, esconder todos os retornos atrás de uma função que entrega somente `double` tende a reduzir a capacidade de diagnosticar falhas.

Um adaptador adequado pode produzir um registro com valor, disponibilidade, motivo e referência de coleta. O núcleo recebe registros já interpretados, sem fazer consultas durante a pintura da interface. A cadeia fica explícita: aquisição no terminal, validação do contexto, cálculo, aceitação da amostra e apresentação. Cada fronteira pode ser ensaiada com dados sintéticos. Uma falha em obter a moeda de lucro não deve se converter em taxa de conversão igual a um. Essa taxa precisaria de justificativa independente.

## 4.3 Identidade antes e depois da coleta

O terminal é um sistema em atividade. Enquanto um programa percorre posições, a conta pode mudar, um negócio pode ocorrer ou a composição pode ser alterada. Uma coleção de chamadas bem-sucedidas pode representar instantes incompatíveis. A técnica de ler identidade antes, coletar dados e conferir identidade depois reduz esse risco. O Stoikus compara conta e composição, e o fluxo de stops verifica também um digest da composição. Essas verificações não criam uma transação atômica no servidor; estabelecem condições locais para recusar uma fotografia evidentemente inconsistente. [Código observado: `JPW_Alavancagem_Core.mqh`, funções de igualdade; `JPW_Alavancagem_Coordinator.mqh`, coleta de stops.]

É importante escrever o alcance da garantia. Uma dupla leitura pode detectar mudança, mas não provar ausência de todas as mudanças intermediárias. Para operações que exigem reconstrução auditável, identificadores, geração e reconciliação do histórico oferecem informações adicionais. O desenho deve tratar atualizações concorrentes como uma condição esperada do ambiente. Repetir a aquisição em outra fatia do timer pode ser a resposta correta, desde que a tela informe espera e não mantenha uma fotografia antiga apresentada como atual.

Um teste de contexto deve simular alteração entre as leituras, e não apenas verificar a igualdade de duas estruturas estáticas. Outro teste precisa conservar o mesmo login e mudar o servidor ou a moeda. O número da conta isolado não é uma identidade suficiente para todas as situações. Também é necessário verificar que rascunhos, seleções e confirmações antigas não atravessem a troca de contexto. Essa regra protege tanto cálculos quanto ações de interface.

## 4.4 Ausência e zero têm significados diferentes

Um inventário confirmado sem posições pode sustentar exposição igual a zero. Um inventário que não pôde ser lido não sustenta essa conclusão. A diferença deve estar representada no tipo de retorno e no fluxo de controle. Inicializar acumuladores em zero é útil para o algoritmo; publicar esse zero após uma falha é uma decisão semântica adicional. A inicialização não fornece evidência de que o conjunto foi examinado integralmente.

O tipo `JPWMetricSample` conserva `has_value`, `value_kind`, qualidade e motivo. A invalidação limpa a disponibilidade, embora também zere o campo numérico interno. Um consumidor deve consultar os campos de validade antes do valor. Ler apenas `numeric_value` transforma um detalhe defensivo de inicialização numa falsa observação financeira. O exemplo mostra por que interfaces tipadas são mais fortes que convenções transmitidas somente em comentários. [Código observado: `JPW_Alavancagem_Samples.mqh`.]

A mesma disciplina se aplica a sentinelas. O núcleo de stops usa um valor negativo específico para indicar que o risco adicional não está completo. Esse contrato local exige interpretação antes da exibição; não permite que um consumidor some o sentinela ao dinheiro conhecido. Uma evolução de interface pode introduzir um campo de disponibilidade explícito, mas isso seria uma proposta de alteração contratual a avaliar, não uma correção silenciosa realizada por este manual. A compatibilidade precisa considerar todos os leitores existentes.

## 4.5 Unidades monetárias e escala contratual

A unidade da conta e a unidade do contrato são problemas distintos. O código observado reconhece USC como unidade contábil centesimal associada a USD e mantém um mecanismo separado para verificar escala contratual. Não é correto concluir que todo contrato de uma conta em centavos tem tamanho reduzido por cem. Também não é correto dividir somente um dos termos de uma razão por cem. Essas decisões podem produzir números plausíveis enquanto alteram o resultado em duas ordens de grandeza. [Código observado: `JPWAccountUnits`, `JPWVerifyScale` e `JPWClassify`, em `JPW_Alavancagem_Core.mqh`.]

Considere um exemplo dimensional, sem afirmar configuração de corretora: exposição de 1.400.000 unidades centesimais e patrimônio de 200.000 na mesma unidade produzem razão 7. Converter ambos para unidades monetárias principais preserva a razão. Converter apenas o patrimônio produz 700. O erro está na mistura de unidades, não na precisão da divisão. O caso de teste deve registrar a unidade de cada entrada para que o oráculo possa detectar a mistura.

Uma taxa de conversão também carrega direção, instrumento e momento. Converter de moeda-base para moeda de lucro não equivale a percorrer a rota inversa usando o mesmo preço. O núcleo do produto representa rotas, direções e instrumentos intermediários. Para cada rota suportada, a especificação precisa dizer como seleciona Bid ou Ask, quais moedas admite e como recusa uma conversão sem prova suficiente. O catálogo da plataforma descreve propriedades; a política de avaliação conservadora e o conjunto de contratos aceitos pertencem ao produto e devem ser identificados como tal.

A verificação por cenários nativos pode auxiliar a confirmar uma escala, mas também precisa de entradas adequadas. O código exige múltiplas observações com sinais e magnitudes distintas e rejeita casos pequenos demais para discriminar candidatos. Uma comparação que sempre cai dentro do arredondamento monetário não prova a escala. É útil conservar as entradas hipotéticas, a saída nativa e a regra de tolerância, permitindo que outro avaliador reproduza a decisão sem acesso à interface do autor.

## 4.6 Alavancagem e agregação

Uma razão de exposição precisa preservar o significado do numerador e do denominador. No caso estudado, a leitura de alavancagem considera exposição da conta e patrimônio sob os contratos suportados pelo núcleo. O programador deve evitar substituir essa leitura pela alavancagem contratada informada pela corretora. São conceitos diferentes, mesmo quando ambos aparecem acompanhados do símbolo de multiplicação. A interface deve nomear o conceito calculado e fornecer sua origem.

Na agregação, a quantidade de linhas aceitas é tão importante quanto a soma. Se uma posição necessária não puder ser avaliada, somar somente as conhecidas cria um total parcial. Esse total pode ser útil em uma ferramenta exploratória, desde que seja apresentado como parcial e que esse modo tenha um contrato próprio. Não pode assumir automaticamente o lugar de um total completo da conta. A disposição de mostrar um número não deve governar a classificação da evidência.

A estabilidade numérica também exige atenção. `MathIsValidNumber` rejeita NaN e infinitos, mas não comprova adequação econômica. Um denominador finito igual a zero continua inválido para uma razão cujo contrato exige patrimônio positivo. Uma soma pode exceder a faixa representável mesmo quando os termos individuais são finitos. Convém validar resultados intermediários e finais, preservando o motivo da recusa. [REF, MathIsValidNumber, p.PDF 1986.]

## 4.7 Risco até o stop e limites do modelo

`OrderCalcProfit` estima resultado para a conta atual e devolve dinheiro na moeda da conta. O núcleo observado converte resultado assinado em perda não negativa: lucro hipotético positivo no stop não se torna risco negativo. Essa transformação serve à leitura informativa implementada; não representa garantia de execução naquele preço. O cálculo declarado não inclui todos os efeitos de gaps, slippage e custos futuros. [REF, OrderCalcProfit, p.PDF 2447–2449; código observado: `JPWStopRiskLossFromProfit`.]

O agregado atual seleciona grupo por símbolo e direção, distingue posições de reservas pendentes e exige saldo positivo. Também recusa modos netting/exchange quando a separação das ordens de origem necessária ao modelo não é demonstrável. Essa recusa não afirma que o MetaTrader não suporte tais contas; delimita a capacidade do modelo do Stoikus. Uma proposta de suporte adicional teria de redefinir a atribuição e ensaiar reconciliação própria. Apagar a recusa sem construir essa prova ampliaria o produto por acidente.

A interpretação de risco deve separar três referências: perda desde a entrada até o stop, movimento adicional desde o mercado atual até o stop e percentual sobre o saldo. Um valor adicional indisponível não necessariamente invalida outro valor cuja origem já esteja comprovada, mas essa independência precisa estar expressa no contrato. Na tela, mostrar o percentual sem o denominador e o grupo induz o leitor a atribuí-lo à conta inteira. Por isso, a preservação do escopo faz parte da correção do software.

## 4.8 Séries, buffers e fotografias incompletas

A solicitação de uma série não garante que todo o intervalo já esteja disponível. `CopyRates` e `CopyBuffer` retornam quantidade efetivamente copiada ou erro, e podem iniciar obtenção ou construção de dados. Um programa que pediu cem observações e recebeu vinte precisa decidir se vinte atendem ao requisito. Não basta testar retorno maior que zero quando a fórmula exige a janela completa. [REF, CopyBuffer, p.PDF 2226–2230; CopyRates, p.PDF 2231–2234.]

Há ainda a distinção entre ordem física e indexação lógica. O catálogo informa que os dados copiados são organizados fisicamente com o elemento mais antigo primeiro, independentemente da propriedade de série do array receptor. A forma de indexar usada pelo algoritmo deve ser conferida explicitamente. Um teste pequeno com três tempos conhecidos costuma revelar uma inversão que passaria despercebida numa grande amostra de preços semelhantes.

Para pesquisa, a barra atual merece tratamento específico. Seu fechamento ainda pode mudar. Um experimento treinado com preços finais de uma barra que, no instante da decisão, estava aberta pode incorporar informação indisponível naquele momento. O problema não é resolvido por usar a mesma função no treino e no teste; é necessário reproduzir o instante de disponibilidade. O capítulo de avaliação aprofunda essa relação entre API de séries e desenho experimental.

## 4.9 Relógios e validade

Tempo do servidor, hora civil de observação e contador monotônico cumprem funções diferentes. `TimeCurrent` representa o último tempo de servidor conhecido associado às cotações; fora de `OnTick`, pode corresponder à última cotação de um dos símbolos disponíveis no Market Watch. Não deve ser tratado automaticamente como relógio de parede que avança em todas as condições. No Strategy Tester, seu comportamento é simulado a partir dos dados históricos. [REF, TimeCurrent, p.PDF 2045–2046.]

Contadores monotônicos ajudam a medir duração e validade numa sessão. Eles não identificam uma sessão após reinício, não substituem a hora de execução do servidor e não devem ser comparados cegamente entre máquinas. A amostra do Stoikus conserva tempos com papéis diferentes e uma janela local de aceitação. O intervalo de trinta segundos presente no código é um comportamento observado desta revisão, não uma recomendação universal derivada dos livros. Alterá-lo requer avaliar a política do produto e suas regressões.

A pergunta de teste é concreta: o que acontece se o relógio civil recuar, se não houver novos ticks, se o terminal reiniciar ou se uma amostra pertencer a outra geração? Cada situação exige recusa ou transição coerente com o contrato. Uma aparência de atualidade construída apenas pela hora em que o painel foi pintado é enganosa. Pintura recente pode estar mostrando dados antigos.

## 4.10 Oráculos e propostas de evolução

Os testes financeiros devem utilizar referências independentes da função avaliada. Para uma razão simples, inteiros de precisão arbitrária ou `Fraction` podem fornecer uma comparação exata no laboratório. Para valores monetários decimais, `Decimal` ajuda a distinguir política de apresentação de arredondamento do núcleo. Nenhuma dessas ferramentas comprova sozinha o comportamento de `OrderCalcProfit` no terminal; elas avaliam relações matemáticas e contratos definidos para a bancada.

Um conjunto mínimo deve incluir inventário vazio confirmado, inventário incompleto, patrimônio zero e negativo, conversão ausente, conta centesimal, resultado no limite, valor logo acima do limite e troca de contexto durante a coleta. A sequência das verificações também importa: validar faixa depois de um cast pode perder a informação que provaria o erro. Esperados devem ser congelados antes do reparo e mantidos separados dos resultados observados.

Como evolução documental, recomenda-se um catálogo de métricas contendo conjunto, unidade, denominador, qualidade, atualidade e condições de recusa. Como evolução de testes, recomenda-se ligar cada contrato a casos de fronteira e a um oráculo identificado. Como alteração futura de produto, tipos monetários mais explícitos podem reduzir misturas de unidade; sua adoção dependerá de compatibilidade e prova de que os consumidores existentes continuam interpretando os resultados corretamente. Estas propostas organizam o desenvolvimento sem modificar as fórmulas atuais.
