# 9. Avaliação: correção matemática, validade temporal e utilidade observável

Avaliar um modelo exige separar perguntas que produzem evidências diferentes. A implementação calcula a função que se propõe a calcular? Os parâmetros aprendem alguma relação que persiste em dados posteriores? A política que consome essas estimativas melhora um resultado de interesse após custos? O sistema continua seguro e previsível quando faltam dados ou recursos? Um único relatório de lucro não responde a todas essas perguntas. No Stoikus atual, a avaliação de aprendizado de máquina permanece prospectiva; nenhuma estratégia neural foi instalada, treinada ou aprovada nesta entrega.

## 9.1 Verificação local antes do experimento econômico

Comece com operações pequenas cujo resultado possa ser obtido independentemente. Uma camada densa com dois atributos e dois neurônios permite conferir entradas, pesos, vieses e ativação. Uma convolução com sequência assimétrica revela inversões; uma LSTM curta permite observar como o estado muda entre passos; uma máscara de atenção conhecida revela se uma posição proibida influencia a saída. A utilidade desses casos é isolar hipóteses. Uma rede grande com entrada aleatória produz muitos números e pouca capacidade de diagnóstico.

Para a retropropagação, a verificação por diferenças finitas compara uma derivada implementada com a alteração efetiva da perda ao perturbar um parâmetro. O livro apresenta essa comparação como etapa anterior ao treinamento e retoma a abordagem nas arquiteturas seguintes. Uma aproximação central é:

$$
g_j^{num}=\frac{L(\theta+\epsilon e_j)-L(\theta-\epsilon e_j)}{2\epsilon}.
$$

O vetor `e_j` seleciona uma coordenada. Uma medida relativa para comparar o gradiente numérico e o analítico é:

$$
E=\frac{\|g^{num}-g^{ana}\|_2}{\max(\delta,\|g^{num}\|_2+\|g^{ana}\|_2)}.
$$

`δ` protege o denominador em gradientes próximos de zero. Não há um limiar universal: escala, precisão, tamanho de `ε` e função analisada afetam o erro. Perturbações pequenas demais sofrem cancelamento; grandes demais perdem a aproximação local. Use diferentes escalas e um caso determinístico. Desative dropout ou congele a máscara; preserve os mesmos dados e estados. Evite interpretar uma divergência em um ponto não diferenciável como prova automática de erro. [NN, 3.10, p. PDF 230–239; NN, 4.1.5, p. PDF 314–315]

A diferença finita tem custo elevado quando aplicada a todos os parâmetros. Em modelos maiores, amostrar coordenadas de cada bloco pode localizar problemas, mas a cobertura deve ser registrada. Conferir apenas a última camada não valida gradientes em recorrência, normalização e ramos residuais. Cada atualização precisa respeitar o mesmo objetivo: se a perda inclui regularização, a verificação deve incluí-la, ou comparar somente a parcela correspondente de ambos os lados.

Uma prova adicional útil é a capacidade de ajustar um conjunto minúsculo e fixo. Se o modelo não consegue reduzir a perda nesse cenário, pode haver erro de dados, gradiente ou otimização. Conseguir memorizar o conjunto, porém, não demonstra generalização. Essa distinção impede transformar um teste de engenharia em alegação de capacidade preditiva.

## 9.2 O relógio dos dados é parte da definição do alvo

Para cada observação, registre o instante dos atributos, o instante em que eles ficaram disponíveis e o período usado pelo alvo. Uma barra em formação não possui seu fechamento definitivo. Um indicador que recalcula extremos com observações futuras pode fornecer um rótulo retrospectivo legítimo, mas não uma característica disponível naquele momento. O livro usa ZigZag para formular direção e distância ao próximo extremo. Essa definição precisa de atenção especial: um alvo retrospectivo não pode retornar ao vetor de entrada através de indicadores, seleção de atributos ou alinhamento incorreto. [NN, 3.1, p. PDF 85–87]

A validade do alvo também depende da disponibilidade econômica. Prever um extremo que só será confirmado depois exige explicitar o horizonte e a regra de confirmação. Alvos de duração variável podem atravessar o corte entre treino e teste. Remover apenas as linhas cujo timestamp inicial está depois do corte não resolve isso: os resultados das últimas linhas de treino podem depender do período reservado para teste. Uma política de exclusão deve usar o intervalo completo de informação de cada rótulo.

Outra fonte de vazamento é a preparação dos dados. Normalizadores, seleção de atributos, imputadores e limiares também aprendem com a amostra. Devem ser ajustados no trecho de treino e aplicados aos trechos posteriores sem incorporar suas respostas. O livro reconhece a necessidade de preservar parâmetros de normalização para uso prático. A síntese deste manual acrescenta a exigência de separar temporalmente o ajuste dessas transformações. [NN, 3.9, p. PDF 222–229]

Uma tabela de dados confiável deve permitir reconstruir o caminho de uma linha: símbolo, corretora ou origem, timezone, timeframe, timestamp da barra, período de cálculo das características, alvo, motivo de exclusão e versão de preparação. Duplicatas precisam ser verificadas antes da divisão; linhas idênticas em lados diferentes podem facilitar memorização e inflar métricas. Dados corrigidos posteriormente também podem divergir do que estava disponível em tempo real. O relatório precisa dizer qual versão foi usada.

## 9.3 Divisão cronológica e experimento reproduzível

Para uma primeira avaliação, separe treino, validação e teste em blocos cronológicos. O treino ajusta parâmetros, a validação orienta hiperparâmetros e parada, e o teste final mede uma escolha congelada. Se o pesquisador consulta repetidamente o teste para trocar arquitetura, ele passa a funcionar como validação. Reservar um bloco com outro nome não muda essa função. A solução exige disciplina experimental e registro das tentativas, não apenas uma razão de divisão como 70/15/15.

Janelas móveis sobrepostas merecem tratamento próprio. Compartilhar observações passadas entre exemplos consecutivos pode refletir o uso real e não constitui automaticamente vazamento. O problema surge quando informação de alvos, transformações ou resultados futuros atravessa a fronteira experimental. Uma zona de exclusão em torno do corte deve ser dimensionada pelo horizonte do alvo e pelo fluxo de informação. Um intervalo arbitrário de uma barra pode ser insuficiente para rótulos que dependem de extremos confirmados muito depois.

A avaliação em avanço temporal, ou walk-forward, repete ajustes usando apenas o passado disponível em cada ponto. É preciso definir se a janela de treino cresce ou se desloca, a frequência de reajuste e a duração dos testes seguintes. Essas escolhas alteram o sistema avaliado. Retreinar a cada mês no experimento e congelar o modelo por um ano na operação significa testar outro procedimento. Cada rodada deve preservar parâmetros, características, normalização, dados e métricas, permitindo reconstruir a sequência de decisões.

O livro apresenta treinamento, escolha de parâmetros do EA e posterior aplicação em dados novos. Na seção 7.4, declara reutilizar o período de treinamento para determinar parâmetros do EA. Isso permite estudar o exemplo, mas cria uma dependência entre modelo, política e amostra de ajuste que precisa ser reconhecida ao interpretar o resultado. A etapa posterior em dados novos é relevante, sem transformar o conjunto dos exemplos em garantia universal de rentabilidade. [NN, 7.3–7.5, p. PDF 661–689; especialmente 7.4, p. PDF 676]

## 9.4 Baselines e métricas que correspondem à pergunta

Uma comparação precisa de baselines que usem a mesma informação e o mesmo protocolo temporal. Para regressão, a previsão constante estimada no treino e uma previsão simples de persistência podem revelar quanto da perda resulta da escala do alvo. Para classificação, a classe majoritária e uma regra simples fornecem referências. Um modelo linear regularizado ajuda a verificar se a complexidade neural oferece ganho além de uma relação de baixa capacidade. Um baseline sem atividade é relevante para uma política econômica: evita custos e exposição, ainda que não seja uma previsão.

Não escolha o baseline depois de observar qual será mais fácil vencer. Congele-o junto com o critério de aceitação. O modelo complexo deve justificar memória, tempo, manutenção e incerteza adicionais. Se a melhoria depende de uma única semente ou de um único regime, o ganho não está suficientemente caracterizado. Repetir treinamentos com sementes diferentes ajuda a medir variabilidade do processo; essas repetições não multiplicam o número de histórias de mercado independentes.

Na classificação desbalanceada, acurácia pode ser alta mesmo sem identificar a classe importante. A matriz de confusão mostra os tipos de erro; precisão e revocação dependem de um limiar; a calibração examina se frequências observadas acompanham probabilidades previstas. Na regressão, MAE e RMSE expressam sensibilidades diferentes a erros grandes. Sempre apresente unidade, escala do alvo e tamanho da amostra. Uma redução de perda sem intervalo temporal e referência comparável é difícil de interpretar.

Na avaliação econômica, conte spread, comissão, financiamento, derrapagem e restrições de execução aplicáveis. O resultado líquido pode ser representado genericamente como:

$$
R_{liq}=R_{bruto}-C_{spread}-C_{comissao}-C_{financiamento}-C_{execucao}.
$$

Essa decomposição exige consistência: se o resultado bruto já foi calculado com preços executáveis de compra e venda, subtrair novamente o spread pode contar o mesmo custo duas vezes. O modelo de custos deve dizer o que está embutido em cada parcela. Atributos preditivos e regras de execução também devem usar o mesmo relógio; decidir com o fechamento e executar retroativamente nesse mesmo preço exige uma justificativa que geralmente não existe.

## 9.5 Tester, desempenho e comparação de implementações

O Strategy Tester pode examinar comportamento histórico sob condições configuradas; seus resultados dependem de dados, modo de modelagem, regras do EA e custos. A apresentação visual ajuda a investigar operações, mas não substitui reconciliação de entradas e saídas. O livro distingue recursos de teste e modos de cálculo e discute atrasos simulados. É necessário registrar a configuração concreta, em vez de usar a palavra backtest como descrição suficiente. [NN, 7.1, p. PDF 652–653]

Comparar MQL5, Python e OpenCL requer duas campanhas. A primeira procura equivalência: mesmos pesos, entrada, estado e tolerância. A segunda mede treinamento ou inferência sob uma carga definida. Se cada versão usa inicialização, otimizador ou camadas diferentes, a comparação avalia sistemas diferentes; não identifica isoladamente a velocidade da linguagem ou do hardware. O livro oferece experiências comparativas em cada família de arquitetura, que devem ser lidas com essa limitação. [NN, 3.11, p. PDF 240–261; NN, 5.2.5, p. PDF 511–515; NN, 6.1.5, p. PDF 608–622]

Uma medição útil informa hardware, precisão, formas dos tensores, lote, número de repetições, aquecimento, alocação e transferência. Inclua latência mediana e dispersão ou percentis, além do tempo total. A média pode ocultar pausas que importam para um programa orientado a eventos. O custo de memória deve considerar pesos, estados do otimizador, ativações e buffers intermediários. Aumentar a janela da atenção afeta uma parcela quadrática; aumentar o lote também pode deslocar o gargalo de computação para memória.

## 9.6 Decisão e limites de conclusão

O relatório final deve permitir distinguir implementação correta, redução de perda, generalização temporal e utilidade econômica. Um experimento pode passar na primeira camada e falhar nas demais; isso continua sendo um resultado informativo. Registre também resultados negativos e tentativas descartadas. Mostrar apenas a melhor curva entre muitas tentativas reduz a capacidade de avaliar a evidência.

O livro termina com conclusões favoráveis ao uso de redes e apresenta um resultado positivo em dados posteriores. Este manual não adota suas afirmações como promessa para outros instrumentos ou períodos. Os exemplos foram consultados como fonte de mecanismos e desenho experimental; não foram reproduzidos neste ambiente. Um gráfico publicado pelo autor não substitui um ensaio novo, e a expectativa de que gestão monetária adicional melhorará o resultado continua sendo hipótese. [NN, 7.5 e Conclusion, p. PDF 687–690]

Para o Stoikus, uma eventual proposta deveria primeiro demonstrar benefício informativo em pesquisa isolada, sem mudar a autoridade do monitor ou do operador. A passagem para operação exigiria outro escopo, evidências nativas e critérios definidos pelo proprietário. Nesta entrega, fórmulas, arquitetura e protocolo constituem material de estudo. Não houve treinamento, execução de negociação, compilação MT5 ou aprovação de um modelo neural.

Uma diferença metodológica com a fonte merece registro explícito. Na preparação inicial, o livro recomenda sorteio dos exemplos e desencoraja blocos consecutivos; calcula escalas MACD no período analisado antes da separação e usa preenchimento zero para índices sem dados. Essas decisões são compreensíveis como simplificações de comparação didática, mas não constituem o protocolo prospectivo adotado neste manual. Para previsão temporal, a separação cronológica e o ajuste das transformações somente no treino procuram reproduzir a disponibilidade real da informação. Preenchimento zero precisa de avaliação própria: mesmo que seu produto com um peso seja zero, sua presença altera a representação e não garante ausência de viés. [NN, 3.9, p. PDF 225–230]

O exemplo final relata 36 posições em 2021, com 21 vencedoras e fator de lucro de 1,48. Uma amostra dessa dimensão e desse único período não estabelece a taxa de acerto futura. O limiar numérico de entrada também não prova calibração probabilística. A sugestão posterior de operar apenas em determinados dias, obtida examinando esse período, constitui uma nova seleção de política; ela precisa de outra avaliação posterior antes de qualquer conclusão. Esse detalhe ilustra por que uma etapa inicialmente reservada pode perder sua independência quando passa a orientar mudanças. [NN, 7.5, p. PDF 688–689]

Até o desempenho computacional muda de interpretação conforme o ensaio. O livro relata vitória de OpenCL na multiplicação inicial, mas descreve vitória da CPU em uma rede pequena devido à transferência de dados. Esses dois resultados são compatíveis: workloads diferentes têm relações diferentes entre aritmética e overhead. A comparação prospectiva deve especificar essa relação e incluir o custo que interessa à operação. [NN, 2.3, p. PDF 82; NN, 3.11, p. PDF 251]
