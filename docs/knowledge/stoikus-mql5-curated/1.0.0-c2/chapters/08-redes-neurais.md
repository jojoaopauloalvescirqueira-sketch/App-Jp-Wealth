# 8. Redes neurais e integração: pesquisa separada do monitor

O Stoikus examinado neste trabalho não contém uma rede neural operacional. Seu monitor orientado a eventos não executa negociações, e os mecanismos matemáticos discutidos neste capítulo são pesquisa para formação técnica. Introduzir aprendizado estatístico, inferência ou treinamento exigiria um projeto próprio e autorização específica. A finalidade atual é compreender os mecanismos, seus custos e os critérios pelos quais uma proposta futura poderia ser avaliada.

Também há dois usos distintos de inteligência artificial. Um assistente programador produz texto e código a partir de instruções e contexto; sua contribuição precisa de revisão, compilação e testes. Um modelo estatístico dentro de um EA transforma dados numéricos em estimativas usando parâmetros treinados. A existência do primeiro não implica a existência do segundo. Uma explicação convincente de código não constitui evidência de capacidade preditiva, assim como uma curva de treinamento não demonstra correção do software que executa o modelo.

## 8.1 Do neurônio à função de perda

Um neurônio calcula uma combinação afim e aplica uma função de ativação. Para uma camada com entradas representadas por linhas de uma matriz, adotaremos a convenção:

$$
Z=XW+b,\qquad H=\phi(Z).
$$

Se `X` tem forma `B × d`, `W` deve ter forma `d × m`, e `H` terá forma `B × m`. O viés `b` precisa ser aplicado a cada linha. Outras convenções de transposição são possíveis; misturá-las entre treinamento e inferência produz erros que às vezes preservam as dimensões. A camada densa do livro organiza entradas, pesos, vieses, saídas e gradientes de forma explícita e explora a multiplicação matricial como mecanismo computacional. [NN, 1.1, p. PDF 8–12; NN, 3.6.1, p. PDF 139–142]

Sem ativações não lineares entre camadas, a composição de mapas afins continua sendo um mapa afim. Aumentar o número de camadas, nesse caso, não cria a capacidade expressiva normalmente associada a redes profundas. Sigmoide e tangente hiperbólica limitam a faixa de saída, mas podem apresentar derivadas pequenas nas regiões de saturação. ReLU e suas variantes têm outros compromissos, incluindo regiões de gradiente nulo. A escolha precisa acompanhar a tarefa e a escala dos dados; nenhuma ativação é universalmente superior. O degrau do neurônio lógico ilustra reconhecimento por limiar, mas sua derivada não fornece o mecanismo usual de treinamento por gradiente. [NN, 1.2, p. PDF 12–23]

O treinamento supervisionado ajusta parâmetros para aproximar alvos conhecidos. Para regressão, uma função ilustrativa é o erro quadrático médio:

$$
L_{MSE}=\frac{1}{N}\sum_{i=1}^{N}(\hat y_i-y_i)^2.
$$

O quadrado aumenta o peso relativo de erros grandes. Isso pode ser desejável para penalizar grandes desvios ou prejudicial quando há observações extremas sem significado para a tarefa. Para classificação, a entropia cruzada exige interpretar as saídas como distribuição compatível com os alvos e tratar estabilidade numérica. Um número no intervalo de zero a um não é automaticamente uma probabilidade calibrada. Tampouco a métrica `accuracy` de um framework tem significado financeiro apenas por estar disponível. [NN, 1.4.1, p. PDF 28–33]

A retropropagação aplica a regra da cadeia ao grafo de operações. Para uma camada densa, se `G` representa a derivada da perda em relação a `Z`, os gradientes seguem a estrutura `XᵀG` para os pesos e `GWᵀ` para as entradas. O viés acumula contribuições das linhas do lote. É necessário decidir onde ocorre a divisão pelo tamanho do lote; dividi-la duas vezes reduz a atualização indevidamente. Ativações intermediárias devem permanecer disponíveis até o cálculo de suas derivadas. O livro separa passagem direta, distribuição dos gradientes, acumulação e atualização de pesos, uma distinção útil para localizar defeitos. [NN, 1.4.2, p. PDF 33–37; NN, 3.4.3, p. PDF 107–125]

A atualização elementar de descida de gradiente é:

$$
\theta_{k+1}=\theta_k-\eta\nabla_{\theta}L(\theta_k).
$$

A taxa `η` controla o tamanho do passo. Momentum e métodos adaptativos acrescentam estado ao otimizador, portanto interromper e retomar o treinamento pode exigir mais que salvar pesos. Não se deve atribuir a Adam a capacidade de garantir um ótimo global. A inicialização também interfere na dinâmica: pesos iguais podem preservar simetrias entre neurônios; escalas excessivas ou pequenas podem prejudicar a propagação. A seleção precisa considerar ativação, profundidade e precisão, em vez de copiar uma constante de outro experimento. [NN, 1.3, p. PDF 23–26; NN, 1.4.3, p. PDF 38–47]

## 8.2 Convolução temporal: compartilhar parâmetros sem acessar o futuro

Uma convolução temporal usa filtros locais que compartilham pesos ao longo da sequência. Em uma convenção causal de uma dimensão, uma saída pode ser escrita como:

$$
y_{t,o}=b_o+\sum_{j=0}^{K-1}\sum_{c=1}^{C}w_{j,c,o}x_{t-j,c}.
$$

O índice `t-j` torna explícito que não usamos entradas posteriores a `t`. Em bibliotecas, operações chamadas convolução frequentemente correspondem à correlação cruzada sem inversão do filtro; o contrato relevante é o mapeamento efetivo dos índices. O livro apresenta filtros, deslocamento, redução de dimensão e implementação em MQL5, OpenCL e Python. Seu exemplo Python distingue opções de preenchimento, inclusive `causal`. [NN, 4.1.1, p. PDF 264–265; NN, 4.1.4, p. PDF 307–308]

Para entrada de comprimento `T`, preenchimento simétrico `P`, dilatação `D`, filtro `K` e passo `S`, a fórmula convencional do comprimento de saída é:

$$
T_{out}=\left\lfloor\frac{T+2P-D(K-1)-1}{S}\right\rfloor+1.
$$

O preenchimento causal é assimétrico e deve ser conferido separadamente. Uma implementação precisa testar janelas menores que o filtro, restos de divisão e bordas. Pooling reduz resolução e pode descartar informações sobre a posição exata de um evento. Em séries financeiras, essa perda pode ser decisiva: reconhecer uma forma em qualquer ponto da janela não equivale a saber se ela ocorreu na última barra fechada.

O compartilhamento de parâmetros reduz o custo em comparação com conectar todas as posições independentemente. Entretanto, não prova que o padrão seja estável entre regimes ou instrumentos. A mesma arquitetura pode aprender artefatos de normalização, preenchimento ou sessão de mercado. O ganho computacional deve ser medido junto com validade temporal e desempenho fora da amostra. A implementação paralela do livro distribui posições e filtros em dimensões do espaço de execução, o que também exige rigor no cálculo dos deslocamentos dos buffers. [NN, 4.1.2–4.1.3, p. PDF 266–306]

## 8.3 Recorrência e LSTM: memória com estado explícito

Uma rede recorrente combina observação corrente e estado anterior. Ao desenrolar a sequência no tempo, a retropropagação atravessa diversas aplicações dos mesmos parâmetros. Produtos sucessivos de derivadas podem tornar gradientes muito pequenos ou muito grandes. A LSTM introduz portas e um caminho de estado celular para controlar a retenção e a atualização de informação; isso atenua alguns problemas, mas não garante aprendizado de qualquer dependência longa. [NN, 4.2.1, p. PDF 335–338]

Com `u_t` representando a concatenação de `x_t` e `h_{t-1}`, uma formulação usual é:

$$
f_t=\sigma(W_fu_t+b_f),\qquad i_t=\sigma(W_iu_t+b_i),\qquad o_t=\sigma(W_ou_t+b_o).
$$

$$
g_t=\tanh(W_gu_t+b_g),\qquad c_t=f_t\odot c_{t-1}+i_t\odot g_t,\qquad h_t=o_t\odot\tanh(c_t).
$$

O símbolo `⊙` indica multiplicação elemento a elemento. A porta de esquecimento controla a contribuição do estado anterior; a porta de entrada controla a nova informação; a porta de saída controla quanto do estado celular aparece no estado oculto. A implementação precisa preservar os valores necessários às derivadas em cada instante. O livro utiliza pilhas para dados cronológicos e detalha as passagens direta e reversa, além da persistência do bloco. [NN, 4.2.2.1–4.2.2.3, p. PDF 350–371]

O estado é parte da interface. É preciso definir quando ele inicia, se atravessa janelas, o que ocorre após lacuna de dados e como se comporta numa troca de símbolo. Misturar o final do treino com o começo do teste através de um estado oculto não documentado altera o experimento. Em outro contexto, uma passagem de aquecimento usando apenas dados passados pode ser legítima, desde que seja registrada e reproduzível. Salvar pesos não significa salvar a continuidade temporal necessária à operação. A discussão do livro sobre reconstrução após carregamento reconhece que intervalos entre salvamento e uso podem invalidar o histórico transitório. [NN, 4.2.2.3, p. PDF 369]

Uma comparação entre LSTM MQL5 e Python precisa alinhar ordenação de portas, formas, ativação, política de estado e opções de retorno. `return_sequences=False` produz uma representação final da sequência, ao passo que retornar todos os passos permite tarefas diferentes. Nomes semelhantes de camadas não demonstram equivalência. A validação deve comparar saídas de um modelo pequeno com pesos conhecidos, antes de comparar curvas produzidas por treinamentos independentes. [NN, 4.2.3–4.2.5, p. PDF 372–400]

## 8.4 Atenção: relações entre posições e obrigação de causalidade

A atenção constrói consultas, chaves e valores a partir das representações de entrada. Na atenção por produto escalar escalado:

$$
Q=XW_Q,\quad K=XW_K,\quad V=XW_V,\qquad A=\operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}+M\right),\qquad H=AV.
$$

A softmax é aplicada por linha. `M` representa uma máscara: posições proibidas recebem um valor que elimina sua contribuição após a normalização. Em previsão temporal causal, permitir que uma posição consulte observações futuras constitui vazamento. O escopo da previsão importa: uma janela inteiramente passada pode ser processada de forma bidirecional para gerar uma única previsão posterior; isso é diferente de afirmar que cada posição interna representa uma previsão realizável naquele instante. [NN, 5.1.1–5.1.2.1, p. PDF 403–422]

Múltiplas cabeças aplicam projeções diferentes e combinam seus resultados. Na parametrização do livro, mantendo a largura por cabeça, aumentar o número de cabeças aumenta parâmetros e buffers. Isso não é uma consequência universal de multi-head: quando a largura total é fixa e repartida entre as cabeças, a quantidade de parâmetros das projeções pode permanecer constante. Os scores explicitamente materializados ainda podem ocupar mais memória conforme o número de cabeças. Na atenção densa, a matriz de relações cresce quadraticamente com o comprimento da sequência. Dobrar a janela pode quadruplicar essa parcela de armazenamento e computação. A divisão em cabeças não elimina esse crescimento. O livro trata organização matricial, buffers, retropropagação, serialização e reaproveitamento de kernels. [NN, 5.2.1–5.2.3, p. PDF 461–498, especialmente p.462]

Atenção isolada precisa de alguma forma de representar ordem quando a tarefa depende dela. Posições, defasagens ou características temporais devem fazer parte do desenho; não se pode presumir que os pesos distingam ordens apenas porque as linhas chegaram em sequência. Blocos também podem incluir conexões residuais, normalização e redes de transformação de características. Cada caminho adicional precisa participar do gradiente, inclusive quando dois ramos se somam. A passagem reversa descrita para o bloco GPT explicita esse acúmulo. [NN, 5.3.2.2, p. PDF 534–542]

O termo GPT no livro descreve uma arquitetura de pesquisa implementada para sequências numéricas. Não significa que o EA está conversando com um serviço de linguagem, tampouco que modelos gigantes possam ser transferidos diretamente ao terminal. O capítulo 5.3 deve ser interpretado como exploração arquitetural; sua utilidade para o Stoikus permanece uma hipótese sem implementação. Comparações do livro são experimentos daquele conjunto de dados, com suas escolhas de alvos e infraestrutura. [NN, 5.3.1, p. PDF 517; NN, 5.3.4, p. PDF 559–569]

## 8.5 Normalização, regularização e modos de execução

Normalizar entradas exige persistir os parâmetros calculados no treino e aplicá-los no uso. Uma média estimada com dados posteriores ao corte temporal incorpora informação indisponível. Batch normalization e layer normalization também não são sinônimos: normalizam sobre eixos e conjuntos distintos. Na forma básica da normalização por lote:

$$
\hat x_i=\frac{x_i-\mu_B}{\sqrt{\sigma_B^2+\varepsilon}},\qquad y_i=\gamma\hat x_i+\beta.
$$

`γ` e `β` são parâmetros aprendidos; `ε` evita singularidade. A política de estatísticas no treino e na inferência precisa ser documentada. O livro desenvolve cálculo, derivadas, armazenamento e versões paralelas; essas implementações específicas devem ser comparadas pelo comportamento, sem presumir equivalência automática com a camada homônima de outro framework. [NN, 3.9, p. PDF 222–223; NN, 6.1.1–6.1.4, p. PDF 572–607]

Regularização acrescenta uma preferência ao objetivo. L2 penaliza a soma dos quadrados dos pesos; L1 penaliza valores absolutos e pode favorecer soluções esparsas. Nenhuma delas elimina ruído de forma garantida. Dropout aplica uma máscara aleatória durante o treino. Na convenção de dropout invertido, para probabilidade de remoção `p`, multiplicamos a ativação por uma variável Bernoulli de retenção e dividimos por `1-p`; na inferência ordinária, o caminho é determinístico. A máscara deve ser reutilizada corretamente na retropropagação daquela passagem. [NN, 1.5.1–1.5.2, p. PDF 48–51; NN, 6.2.1.1–6.2.1.2, p. PDF 629–632]

A amostragem Bernoulli descreve a decisão de retenção; uma distribuição normal de números brutos não deve ser confundida com a distribuição binária da máscara. O livro contém formulações expositivas que exigem esse cuidado, assim como observações experimentais sobre combinar normalização e dropout. Uma piora observada em seu conjunto de modelos não é um teorema que proíba toda combinação. Testar ablações controladas permite distinguir efeito da arquitetura, hiperparâmetros e dados. [NN, 6.2.3–6.2.4, p. PDF 641–650]

## 8.6 MQL5, Python, OpenCL e ONNX: responsabilidades diferentes

MQL5 permite implementar a aritmética e o ciclo do modelo diretamente, com responsabilidade sobre buffers, gradientes e persistência. Python oferece um ecossistema de preparação e treinamento, mas a velocidade de uma aplicação depende das bibliotecas e kernels efetivamente utilizados; a oposição simplista entre linguagem interpretada lenta e compilada rápida não decide o desempenho de multiplicações matriciais. A integração com o terminal também precisa ter seu ambiente operacional validado. [NN, 2.4, p. PDF 82–83; NN, 3.5, p. PDF 130–137]

OpenCL distribui operações entre unidades de processamento. O host prepara contexto, programa, kernels e buffers; o dispositivo executa os trabalhos. Transferências, compilação e sincronização podem dominar uma tarefa pequena. A comparação inicial do livro exclui custos de preparação da medição principal e declara essa limitação. Assim, seus números não podem ser reutilizados como previsão de latência total em outra máquina. É necessário medir execução fria, execução aquecida, memória, transferência e erro numérico. [NN, 2.3, p. PDF 72–82; NN, 3.7, p. PDF 169–217]

ONNX oferece uma rota de intercâmbio de modelos para inferência. A documentação MQL5 descreve criação de sessão, inspeção de entradas e saídas, configuração de formas, execução e liberação. A conversão bem-sucedida de um arquivo não prova equivalência numérica. Um conjunto de vetores de referência precisa comparar saídas do treinamento e do runtime, com tolerâncias justificadas. [Documentação oficial ONNX](https://www.mql5.com/en/docs/onnx).

`OnnxRun` retorna sucesso ou falha e permite recuperar o erro. Flags, operadores e comportamento devem ser conferidos no build alvo; a página atual distingue opções de registro e conversão. Não se presume que todo modelo, dispositivo ou ambiente tenha suporte equivalente. Essas são condições de uma futura experiência, sem execução ONNX nesta entrega. [Documentação oficial OnnxRun](https://www.mql5.com/en/docs/onnx/onnxrun).

Um artefato de pesquisa utilizável precisa incluir pesos, esquema de características, ordem das colunas, formas, unidades, normalização, versões e hash. O carregamento deve recusar incompatibilidades. Mesmo um modelo numericamente correto continua sujeito a falha estatística e mudança de regime. Seu lugar inicial seria um ambiente de pesquisa isolado, com resultados informativos e sem autorização implícita de negociação.
