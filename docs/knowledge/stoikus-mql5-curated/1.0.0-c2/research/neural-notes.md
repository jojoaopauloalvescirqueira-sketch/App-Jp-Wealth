# Notas de consulta neural e fundamentos

## Método e limites

Consulta textual efetiva por amostras, não leitura integral das690p. Cada folha do índice foi inspecionada nos trechos abaixo. As faixas declaradas são intervalos de seção no índice, não páginas lidas integralmente. Pais agregam filhos sem inflar cobertura. Fórmulas e figuras não foram auditadas visualmente nesta subtarefa. Código do livro não foi compilado nem reproduzido. Metadados de extração não são evidência de leitura.

Amostras iniciais em pypdf foram complementadas por Poppler layout. Para folhas até217, consulta sistemática aos caracteres500:1350 da página min(início+1,fim); folhas posteriores: caracteres0:1350 até400,0:1150 até569 e0:1450 depois. Houve consultas adicionais mais longas nos fundamentos; o registro conservador abaixo inclui somente a amostra sistemática comum.

## NN-0001 — Neural Networks for Algorithmic Trading with MQL5

Intervalo da seção no índice: PDF 5–690. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0002 — Introduction

Intervalo da seção no índice: PDF 6–6. Estado: partial_textual_consultation.

Introdução apresenta escopo e definição de IA; não é prova de capacidade financeira.

Amostra consultada: PDF 6, caracteres 500–1350; início do trecho: `puters, which, thanks to developed algorithms, allow us to move from simple calculations to solving other more intellectual tasks. Next, artificial intelligence algorithms emer`.

## NN-0003 — 1. Basic principles of artificial intelligence construction

Intervalo da seção no índice: PDF 7–56. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0004 — 1.1 Neuron and principles of building neural networks

Intervalo da seção no índice: PDF 8–11. Estado: partial_textual_consultation.

Ativações suaves e representação de neurônio; síntese diferencia limiar lógico e função treinável.

Amostra consultada: PDF 9, caracteres 500–1350; início do trecho: `ious sigmoid functions have been widely used as neuron activation functions. In this version, a smoother graph of the mathematical model of the neuron is obtained.`.

## NN-0005 — 1.2 Activation functions

Intervalo da seção no índice: PDF 12–22. Estado: partial_textual_consultation.

Derivada do degrau nula ou indefinida limita treinamento usual; não extrapolar para toda técnica de aprendizagem.

Amostra consultada: PDF 13, caracteres 500–1350; início do trecho: `the neural network. The fact is that neural network training algorithms use the first-order derivative. However, the derivative of the function under consideration is always zer`.

## NN-0006 — 1.3 Weight initialization methods in neural networks

Intervalo da seção no índice: PDF 23–25. Estado: partial_textual_consultation.

Inicialização constante preserva simetrias; avaliar escala e ativação, sem afirmar garantia de ótimo.

Amostra consultada: PDF 24, caracteres 500–1350; início do trecho: `r work with this dataset in the same way. Within the framework of a single neuron, according to the laws of mathematics, the constant can be factored out in the formula for c`.

## NN-0007 — 1.4 Neural network training

Intervalo da seção no índice: PDF 26–47. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0008 — 1.4.1 Loss functions

Intervalo da seção no índice: PDF 28–32. Estado: partial_textual_consultation.

MAE e checagem de tamanhos no exemplo; código extraído contém grafias suspeitas e não foi copiado.

Amostra consultada: PDF 29, caracteres 500–1350; início do trecho: `s, the function must receive two data vectors: calculated and reference values. This data will be passed as parameters to the function. At the beginning of the method, we`.

## NN-0009 — 1.4.2 Error gradient backpropagation method

Intervalo da seção no índice: PDF 33–37. Estado: partial_textual_consultation.

Passagem direta retém intermediários para regra da cadeia; separar distribuição e atualização.

Amostra consultada: PDF 34, caracteres 500–1350; início do trecho: `nge at each point on the loss function graph. Therefore, we will reduce the loss function gradually, getting closer and closer to the minimum with each iteration. At firs`.

## NN-0010 — 1.4.3 Methods for optimizing neural networks

Intervalo da seção no índice: PDF 38–47. Estado: partial_textual_consultation.

Taxa de aprendizagem e derivadas locais controlam atualização; otimizador não garante ótimo global.

Amostra consultada: PDF 39, caracteres 500–1350; início do trecho: `the neuron only by choosing the optimal values of the weights. The rate of change of the neuron's output value when changing a particular weight is equal to the partial`.

## NN-0011 — 1.5 Techniques for improving the convergence of neural networks

Intervalo da seção no índice: PDF 48–55. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0012 — 1.5.1 Regularization

Intervalo da seção no índice: PDF 48–49. Estado: partial_textual_consultation.

Penalidade L1 e seleção de características; rejeitada generalização de eliminação completa do ruído.

Amostra consultada: PDF 49, caracteres 500–1350; início do trecho: `ghts as close to zero as possible. The partial derivative of such a loss function will take the form: Here, we don't explicitly calculate the derivative of the loss f`.

## NN-0013 — 1.5.2 Dropout

Intervalo da seção no índice: PDF 50–51. Estado: partial_textual_consultation.

Probabilidade de retenção q=1-P; formulação normal versus máscara Bernoulli merece correção conceitual.

Amostra consultada: PDF 51, caracteres 500–1350; início do trecho: `rceptron with two hidden layers Describing the proposed solution from a mathematical point of view, we can say that each individual neuron is excluded from the process with`.

## NN-0014 — 1.5.3 Normalization

Intervalo da seção no índice: PDF 52–55. Estado: partial_textual_consultation.

Motivação por mudanças de distribuição interna; síntese não trata essa explicação como garantia universal.

Amostra consultada: PDF 53, caracteres 500–1350; início do trecho: `'Hidden pattern' in the diagram). However, by changing the parameters of the first hidden layer, we have already altered the data array. In other words, we are adjusting the`.

## NN-0015 — 1.6 Artificial intelligence in trading

Intervalo da seção no índice: PDF 56–56. Estado: partial_textual_consultation.

Aplicações de terminal e automação; distinguir possibilidades da plataforma do produto atual.

Amostra consultada: PDF 56, caracteres 500–1350; início do trecho: `computer technologies nowadays. Primarily, thanks to the internet and computers, traders no longer need to be physically present on the trading floor. The trading terminal so`.

## NN-0016 — 2. MetaTrader 5 features for algorithmic trading

Intervalo da seção no índice: PDF 57–83. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0017 — 2.1 Program types and their construction features

Intervalo da seção no índice: PDF 60–66. Estado: partial_textual_consultation.

Tipos de programa e eventos de EA; capacidade de negociar não implica que todo EA negocie.

Amostra consultada: PDF 61, caracteres 500–1350; início do trecho: `them. It also offers an opportunity to write your own technical analysis indicators, scripts, services, and libraries of included functions. Each program type is designed t`.

## NN-0018 — 2.2 Statistical analysis and fuzzy logic tools

Intervalo da seção no índice: PDF 67–71. Estado: partial_textual_consultation.

Conjuntos fuzzy e funções de pertinência; pertinência não equivale automaticamente a probabilidade.

Amostra consultada: PDF 68, caracteres 500–1350; início do trecho: `tor can change significantly depending on the size of this deviation. The application of fuzzy logic allows us to solve this problem by introducing "fuzzy" set boundaries.`.

## NN-0019 — 2.3 OpenCL: Parallel computations in MQL5

Intervalo da seção no índice: PDF 72–81. Estado: partial_textual_consultation.

Host, dispositivo e kernels; transferências e precisão devem integrar custo.

Amostra consultada: PDF 73, caracteres 500–1350; início do trecho: `lar device. An important feature of the GPU is vector computing. Each microprocessor consists of several computing modules. They can all execute the same instruction. At the s`.

## NN-0020 — 2.4 Integration with Python

Intervalo da seção no índice: PDF 82–83. Estado: partial_textual_consultation.

Bibliotecas e conexão terminal/Python; ambiente nativo precisa de validação própria.

Amostra consultada: PDF 83, caracteres 500–1350; início do trecho: `ful functions. There are tools for working with text, and for writing network applications. Additional functionality can be implemented using a wide range of third-party librar`.

## NN-0021 — 3. Building the first neural network model in MQL5

Intervalo da seção no índice: PDF 84–261. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0022 — 3.1 Problem statement

Intervalo da seção no índice: PDF 85–86. Estado: partial_textual_consultation.

ZigZag fornece extremos retrospectivos para alvos; impedir informação futura nos atributos.

Amostra consultada: PDF 86, caracteres 500–1350; início do trecho: `minimum distance between neighboring extrema in candlesticks. In our case, we can use ZigZag to find extrema and specify training targets for our neural network. By applying t`.

## NN-0023 — 3.2 File arrangement structure

Intervalo da seção no índice: PDF 87–99. Estado: partial_textual_consultation.

Índice colide com3.3 em87–99; amostra88 trata seleção, não valida integralmente arranjo de arquivos.

Amostra consultada: PDF 88, caracteres 500–1350; início do trecho: `tween them or that both variables are dependent on a common underlying factor. Consequently, the use of correlated variables combines the two mentioned problems and their conse`.

## NN-0024 — 3.3 Choosing the input data

Intervalo da seção no índice: PDF 87–99. Estado: partial_textual_consultation.

Seleção e correlação de indicadores; estimar transformações somente em treino.

Amostra consultada: PDF 88, caracteres 500–1350; início do trecho: `tween them or that both variables are dependent on a common underlying factor. Consequently, the use of correlated variables combines the two mentioned problems and their conse`.

## NN-0025 — 3.4 Creating the framework for the future MQL5 program

Intervalo da seção no índice: PDF 100–129. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0026 — 3.4.1 Defining constants

Intervalo da seção no índice: PDF 101–103. Estado: partial_textual_consultation.

Identificadores de classes e camadas, buffers e descritores; interfaces explícitas favorecem persistência.

Amostra consultada: PDF 102, caracteres 500–1350; início do trecho: `stage, we don't know the number of layers in the neural network or the number of neurons in each layer. Therefore, we assume that there will be a dynamic array for storing poi`.

## NN-0027 — 3.4.2 Mechanism for describing the structure of the future neural network

Intervalo da seção no índice: PDF 104–106. Estado: partial_textual_consultation.

Mesma ativação por camada é escolha do autor, não exigência universal da linguagem.

Amostra consultada: PDF 105, caracteres 500–1350; início do trecho: `. Then there is another question: will all neurons in the same layer use the same activation function? Or will there be options to use different activation features within a s`.

## NN-0028 — 3.4.3 Neural network base class and organization of forward and backward pass processes

Intervalo da seção no índice: PDF 107–125. Estado: partial_textual_consultation.

CNet mantém parâmetros, resultados e fluxo; estados devem ser separados por responsabilidade.

Amostra consultada: PDF 108, caracteres 500–1350; início do trecho: `case, the user specifies once, and we will need them at each iteration. So we need to store them somewhere. Let's add a method for specifying learning parameters (SetLearningRate`.

## NN-0029 — 3.4.4 Dynamic storage array of neural layers

Intervalo da seção no índice: PDF 126–129. Estado: partial_textual_consultation.

CArrayObj e criação de camadas na carga; validação de índices, handles e propriedade.

Amostra consultada: PDF 127, caracteres 500–1350; início do trecho: `m_iFileHandle = file_handle; return CArrayObj::Load(file_handle); } Now let's look directly at the method of creating a new neural layer in a dynamic array. In`.

## NN-0030 — 3.5 Description of a Python script structure

Intervalo da seção no índice: PDF 130–137. Estado: partial_textual_consultation.

Pandas organiza tabela e dados faltantes; schema e versões precisam acompanhar artefato.

Amostra consultada: PDF 131, caracteres 500–1350; início do trecho: `object is created in the Pandas library. It is designed to work with indexed arrays of two-dimensional data. In addition, the library provides: · Tools for data exchan`.

## NN-0031 — 3.6 Fully connected neural layer

Intervalo da seção no índice: PDF 138–168. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0032 — 3.6.1 Architecture and implementation principles

Intervalo da seção no índice: PDF 139–141. Estado: partial_textual_consultation.

Pesos incluem viés e buffers de gradiente; convenção de forma deve ser consistente.

Amostra consultada: PDF 140, caracteres 500–1350; início do trecho: `l to the number of neurons in our layer. We will also need an array to store the weights. This will be a matrix, where the size of the first dimension is equal to the number`.

## NN-0033 — 3.6.2 Creating a neural layer using MQL5 tools

Intervalo da seção no índice: PDF 142–160. Estado: partial_textual_consultation.

Construtor e destrutor alocam/liberam buffers; falha parcial exige política de propriedade.

Amostra consultada: PDF 143, caracteres 500–1350; início do trecho: `n choose your preferred optimization method and activation function. We will leave the pointer to the class working with OpenCL empty and create instances for all other classes`.

## NN-0034 — 3.6.3 Activation function class

Intervalo da seção no índice: PDF 161–168. Estado: partial_textual_consultation.

Hierarquia de ativações permite polimorfismo; operação direta e derivada devem corresponder.

Amostra consultada: PDF 162, caracteres 500–1350; início do trecho: `y creating a new class that inherits from a certain base class. In this way, by overriding a couple of methods responsible for the direct calculation of the function and its deri`.

## NN-0035 — 3.7 Organizing parallel computing using OpenCL

Intervalo da seção no índice: PDF 169–217. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0036 — 3.7.1 Creating an OpenCL program

Intervalo da seção no índice: PDF 170–185. Estado: partial_textual_consultation.

Buffer linear e deslocamento por neurônio; garantir bordas antes de paralelizar.

Amostra consultada: PDF 171, caracteres 500–1350; início do trecho: `ntial output exceeding the array limits. As we discussed earlier, the number of threads will correspond to the number of neurons in the layer. Therefore, at the beginning of t`.

## NN-0037 — 3.7.2 Implementing functionality on the main program side

Intervalo da seção no índice: PDF 186–217. Estado: partial_textual_consultation.

Índices nomeados de argumentos dos kernels; conferir ordem e tipo na interface host.

Amostra consultada: PDF 187, caracteres 500–1350; início do trecho: `18 #define def_k_AdaDeltaUpdate 19 #define def_k_AdamUpdate 20 To specify parameters when calling kernels, we can also use in`.

## NN-0038 — 3.8 Implementing the perceptron model in Python

Intervalo da seção no índice: PDF 218–221. Estado: partial_textual_consultation.

Dense e configurações antes do primeiro acesso; treinamento independente não prova equivalência.

Amostra consultada: PDF 219, caracteres 0–1350; início do trecho: `3. Building the first neural network model in MQL5 Please note that you cannot change the settings after the first access to the layer. In addition to the above parameters`.

## NN-0039 — 3.9 Creating training and testing samples

Intervalo da seção no índice: PDF 222–229. Estado: partial_textual_consultation.

Normalização precisa persistir parâmetros; impedir estimativa em dados futuros.

Amostra consultada: PDF 223, caracteres 0–1350; início do trecho: `3. Building the first neural network model in MQL5 operation of the neural network. Therefore, in practice, it will be necessary to store the normalization parameters and u`.

## NN-0040 — 3.10 Gradient distribution verification

Intervalo da seção no índice: PDF 230–239. Estado: partial_textual_consultation.

Derivada empírica versus analítica; diferenças finitas exigem escala e determinismo.

Amostra consultada: PDF 231, caracteres 0–1350; início do trecho: `3. Building the first neural network model in MQL5 before we proceed directly to training the neural network, we need to check the correctness of the error gradient distr`.

## NN-0041 — 3.11 Comparative testing of implementations

Intervalo da seção no índice: PDF 240–261. Estado: partial_textual_consultation.

Parâmetros de comparação incluem lote, taxa e épocas; alinhar antes de atribuir ganho ao runtime.

Amostra consultada: PDF 241, caracteres 0–1350; início do trecho: `3. Building the first neural network model in MQL5 · Learning rate. · The number of hidden layers. · The number of neurons in a single hidden layer. · Th`.

## NN-0042 — 4. Basic types of neural layers

Intervalo da seção no índice: PDF 262–400. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0043 — 4.1 Convolutional neural networks

Intervalo da seção no índice: PDF 263–333. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0044 — 4.1.1 Description of architecture and implementation principles

Intervalo da seção no índice: PDF 264–265. Estado: partial_textual_consultation.

Filtro local, passo e compartilhamento; distinguir convenção de convolução e correlação cruzada.

Amostra consultada: PDF 265, caracteres 0–1350; início do trecho: `4. Basic types of neural layers The Convolution layer is responsible for recognizing objects in the source data set. In this layer, sequential operations of mathematical`.

## NN-0045 — 4.1.2 Construction using MQL5

Intervalo da seção no índice: PDF 266–286. Estado: partial_textual_consultation.

Pooling possui janela, passo e filtros; perda de posição deve ser avaliada na tarefa.

Amostra consultada: PDF 267, caracteres 0–1350; início do trecho: `4. Basic types of neural layers Pooling layer We begin the implementation of the algorithm by constructing a pooling layer. To do this, we will create a class CNeuron`.

## NN-0046 — 4.1.3 Organizing parallel computing in convolutional networks using OpenCL

Intervalo da seção no índice: PDF 287–306. Estado: partial_textual_consultation.

Execução bidimensional por saída e filtro; deslocamentos de buffer são parte do contrato.

Amostra consultada: PDF 288, caracteres 0–1350; início do trecho: `4. Basic types of neural layers In the kernel parameters, we specify the window size for analyzing the initial data (window), the step for moving the window (step), the n`.

## NN-0047 — 4.1.4 Implementing a convolutional model in Python

Intervalo da seção no índice: PDF 307–313. Estado: partial_textual_consultation.

Conv1D e padding causal; dimensão de atributos não equivale à dimensão temporal.

Amostra consultada: PDF 308, caracteres 0–1350; início do trecho: `4. Basic types of neural layers convolution window as the number of elements, while here, the convolution window determines the number of elements in the second dimension`.

## NN-0048 — 4.1.5 Practical testing of convolutional models

Intervalo da seção no índice: PDF 314–333. Estado: partial_textual_consultation.

Reaplicação de teste de gradiente; erro por aproximação numérica não desqualifica derivada analítica exata.

Amostra consultada: PDF 315, caracteres 0–1350; início do trecho: `4. Basic types of neural layers In geometry terms, the gradient is the slope of the tangent to the graph of the function at the current point Of course, we are d`.

## NN-0049 — 4.2 Recurrent neural networks

Intervalo da seção no índice: PDF 334–400. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0050 — 4.2.1 Description of architecture and implementation principles

Intervalo da seção no índice: PDF 335–338. Estado: partial_textual_consultation.

Desenrolamento temporal compartilha pesos; atenuação de gradientes motiva LSTM.

Amostra consultada: PDF 336, caracteres 0–1350; início do trecho: `4. Basic types of neural layers Recurrent neuron pattern Training recurrent neural networks is done using the well-known method`.

## NN-0051 — 4.2.2. Building an LSTM block in MQL5

Intervalo da seção no índice: PDF 339–371. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0052 — 4.2.2.1 Feed-forward method

Intervalo da seção no índice: PDF 350–358. Estado: partial_textual_consultation.

Pilhas de entradas e estado oculto suportam treino; memória transitória tem custo.

Amostra consultada: PDF 351, caracteres 0–1350; início do trecho: `4. Basic types of neural layers Next, we have to prepare the initial data for the correct operation of the internal layers. This procedure is not as simple as it may seem`.

## NN-0053 — 4.2.2.2 Backpropagation methods

Intervalo da seção no índice: PDF 359–367. Estado: partial_textual_consultation.

Gradiente usa memória e saídas das portas; profundidade temporal limita histórico retropropagado.

Amostra consultada: PDF 360, caracteres 0–1350; início do trecho: `4. Basic types of neural layers Therefore, the next step is to check for the presence of information in the memory stacks and hidden states. In addition, the stack fillin`.

## NN-0054 — 4.2.2.3 Saving and restoring the LSTM block

Intervalo da seção no índice: PDF 368–371. Estado: partial_textual_consultation.

Persistir conteúdo, não descritores; lacunas após carga afetam estado temporal.

Amostra consultada: PDF 369, caracteres 0–1350; início do trecho: `4. Basic types of neural layers virtual bool Save(const int file_handle) override; virtual bool Load(const int file_handle) override;`.

## NN-0055 — 4.2.3 Organizing parallel computing in the LSTM block

Intervalo da seção no índice: PDF 372–380. Estado: partial_textual_consultation.

Kernels LSTM recebem múltiplos buffers de portas e estado; fronteira host/device precisa de schema.

Amostra consultada: PDF 373, caracteres 0–1350; início do trecho: `4. Basic types of neural layers 4.2.3.1 Making additions to the OpenCL program The first item we indicate is the program of the operations being performed. This means th`.

## NN-0056 — 4.2.4 Implementing recurrent models in Python

Intervalo da seção no índice: PDF 381–388. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0057 — 4.2.4.1 Building a test recurrent model in Python

Intervalo da seção no índice: PDF 384–388. Estado: partial_textual_consultation.

return_sequences=False altera forma da saída; comparar modelos com contratos equivalentes.

Amostra consultada: PDF 385, caracteres 0–1350; início do trecho: `4. Basic types of neural layers keras.layers.LSTM(40, return_sequences=False, kernel_regularizer=keras.regular`.

## NN-0058 — 4.2.5 Comparative testing of recurrent models

Intervalo da seção no índice: PDF 389–400. Estado: partial_textual_consultation.

Acesso aos pesos internos e composição de camadas limitam comparação superficial.

Amostra consultada: PDF 390, caracteres 0–1350; início do trecho: `4. Basic types of neural layers if(!(descr = new CLayerDescription())) { PrintFormat("Error creating CLayerDescription: %d", GetLastError());`.

## NN-0059 — 5. Attention mechanisms

Intervalo da seção no índice: PDF 401–569. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0060 — 5.1 Self-Attention

Intervalo da seção no índice: PDF 403–458. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0061 — 5.1.1 Description of architecture and implementation principles

Intervalo da seção no índice: PDF 403–405. Estado: partial_textual_consultation.

Encoder e decoder combinam atenção e feed-forward; arquitetura não implica causalidade automática.

Amostra consultada: PDF 404, caracteres 0–1150; início do trecho: `5. Attention mechanisms Transformer architecture Each Encoder layer contains two internal layers: Self-Attention and Feed Forward`.

## NN-0062 — 5.1.2 Building Self-Attention with MQL5 tools

Intervalo da seção no índice: PDF 406–433. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0063 — 5.1.2.1 Self-Attention feed-forward method

Intervalo da seção no índice: PDF 416–422. Estado: partial_textual_consultation.

Score é produto query/key e softmax por linha; máscara deve excluir informação proibida.

Amostra consultada: PDF 417, caracteres 0–1150; início do trecho: `5. Attention mechanisms MATRIX keys = m_cKeys.GetOutputs().m_mMatrix; After completing the preparatory work, we need to "roll up our sleeves" and build a new p`.

## NN-0064 — 5.1.2.2 Self-Attention backpropagation methods

Intervalo da seção no índice: PDF 423–430. Estado: partial_textual_consultation.

Derivada da normalização participa do gradiente; não omitir transformações auxiliares.

Amostra consultada: PDF 424, caracteres 0–1150; início do trecho: `5. Attention mechanisms What is the normalization process? This is the process of changing the statistical variables in a sampling and bringing it closer to some specifie`.

## NN-0065 — 5.1.2.3 File operations

Intervalo da seção no índice: PDF 431–433. Estado: partial_textual_consultation.

Interface Save/Load e identidade da camada; consulta do trecho não valida formato inteiro.

Amostra consultada: PDF 432, caracteres 0–1150; início do trecho: `5. Attention mechanisms //--- virtual bool NormlizeBuffer(CBufferType *buffer, CBufferType *std,`.

## NN-0066 — 5.1.3 Organizing parallel computing in the attention block

Intervalo da seção no índice: PDF 434–455. Estado: partial_textual_consultation.

Kernels adicionais paralelizam passos; custo inclui buffers e transferências.

Amostra consultada: PDF 435, caracteres 0–1150; início do trecho: `5. Attention mechanisms directions. It's also important to note that each element of the sequence, described by a value vector, is processed using shared weight matrices,`.

## NN-0067 — 5.1.4 Testing the attention mechanism

Intervalo da seção no índice: PDF 456–458. Estado: partial_textual_consultation.

Campos reutilizados descrevem sequência e atributos; nomes pouco específicos exigem contrato.

Amostra consultada: PDF 457, caracteres 0–1150; início do trecho: `5. Attention mechanisms the result of the operation based on the obtained pointer to the object. Next, we need to provide descriptions for the created neural layer. I`.

## NN-0068 — 5.2 Multi-Head attention

Intervalo da seção no índice: PDF 459–515. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0069 — 5.2.1 Description of the Multi-Head Self-Attention architecture

Intervalo da seção no índice: PDF 461–463. Estado: partial_textual_consultation.

Concatenação das matrizes de cabeças; conferir formas e projeções compartilhadas.

Amostra consultada: PDF 462, caracteres 0–1150; início do trecho: `5. Attention mechanisms the query and key tensors. Let's use nI for the size of the source data vector and nK for the size of the key vector. Then the tensors will have the`.

## NN-0070 — 5.2.2 Building Multi-Head Self-Attention in MQL5

Intervalo da seção no índice: PDF 464–487. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0071 — 5.2.2.1 Multi-Head Self-Attention feed-forward method

Intervalo da seção no índice: PDF 474–478. Estado: partial_textual_consultation.

Arrays de matrizes simulam dimensão de cabeças; cuidado com layout e índices.

Amostra consultada: PDF 475, caracteres 0–1150; início do trecho: `5. Attention mechanisms Matrix operations allow us to operate only with two-dimensional matrices. One of the dimensions used will be a vector describing one element of the`.

## NN-0072 — 5.2.2.2 Multi-Head Self-Attention backpropagation methods

Intervalo da seção no índice: PDF 479–485. Estado: partial_textual_consultation.

Normalização e blocos FF propagam gradientes em ordem reversa.

Amostra consultada: PDF 480, caracteres 0–1150; início do trecho: `5. Attention mechanisms { //--- check the relevance of all objects if(!m_cOutputs || !m_cGradients || m_cOutputs.Total() != m_cGradients.Total(`.

## NN-0073 — 5.2.2.3 File operations

Intervalo da seção no índice: PDF 486–487. Estado: partial_textual_consultation.

Save encadeia classe-base, número de cabeças e projeção; versão e ordem são essenciais.

Amostra consultada: PDF 487, caracteres 0–1150; início do trecho: `5. Attention mechanisms In the parameters, the CNeuronMHAttention::Save method gets the handle of the file to which it will write the data. In the body of the method, we im`.

## NN-0074 — 5.2.3 Organizing parallel computing for Multi-Head Self-Attention

Intervalo da seção no índice: PDF 488–498. Estado: partial_textual_consultation.

Reuso de kernels reduz duplicação; trabalho paralelo depende de dimensões de execução.

Amostra consultada: PDF 489, caracteres 0–1150; início do trecho: `5. Attention mechanisms As usual, we start by creating an OpenCL program. Do we really need to create a new program? Why do we need to create new kernels? The answer is obv`.

## NN-0075 — 5.2.4 Building Multi-Head Self-Attention in Python

Intervalo da seção no índice: PDF 499–510. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0076 — 5.2.4.1 Creating a new neural layer class

Intervalo da seção no índice: PDF 502–506. Estado: partial_textual_consultation.

Classe Python inclui Dense e LayerNormalization; nome igual não prova igualdade com MQL5.

Amostra consultada: PDF 503, caracteres 0–1150; início do trecho: `5. Attention mechanisms def __init__(self,key_size, heads, **kwargs): super(MHAttention, self).__init__(**kwargs) self.m_iHeads = heads`.

## NN-0077 — 5.2.4.2 Creating a script to test Multi-Head Self-Attention

Intervalo da seção no índice: PDF 507–510. Estado: partial_textual_consultation.

Reshape e Flatten conectam atenção e densas; conferir ordem temporal preservada.

Amostra consultada: PDF 508, caracteres 0–1150; início do trecho: `5. Attention mechanisms model5 = keras.Sequential([keras.layers.InputLayer(input_shape=inputs), # Reformat the tensor into 3-dimensional. Specify 2 dimensions`.

## NN-0078 — 5.2.5 Comparative testing of Attention models

Intervalo da seção no índice: PDF 511–515. Estado: partial_textual_consultation.

Campo step é reutilizado como número de cabeças; contrato semântico deve ser explícito.

Amostra consultada: PDF 512, caracteres 0–1150; início do trecho: `5. Attention mechanisms the testing script will not require major changes, and all changes will affect only the block for declaring a new layer. Our first change is, of`.

## NN-0079 — 5.3 GPT architecture

Intervalo da seção no índice: PDF 516–569. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0080 — 5.3.1 Description of the architecture

Intervalo da seção no índice: PDF 517–517. Estado: partial_textual_consultation.

GPT descrito como decoder; exemplo numérico não é serviço assistente de linguagem.

Amostra consultada: PDF 517, caracteres 0–1150; início do trecho: `5. Attention mechanisms perform different language tasks. The limitation lies in the language of the source dataset for unsupervised learning. As practical experience ha`.

## NN-0081 — 5.3.2 Building a GPT model in MQL5

Intervalo da seção no índice: PDF 518–546. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0082 — 5.3.2.1 GPT feed-forward method

Intervalo da seção no índice: PDF 529–533. Estado: partial_textual_consultation.

Percurso de camadas internas e escolha do dispositivo; verificar equivalência por operações.

Amostra consultada: PDF 530, caracteres 0–1150; início do trecho: `5. Attention mechanisms corresponding to the current internal neural layer. We check the validity of the extracted pointer and then execute the feed-forward method of the c`.

## NN-0083 — 5.3.2.2 GPT backpropagation methods

Intervalo da seção no índice: PDF 534–542. Estado: partial_textual_consultation.

Ramos residuais somam gradientes; omitir um ramo altera treinamento.

Amostra consultada: PDF 535, caracteres 0–1150; início do trecho: `5. Attention mechanisms After this, we sequentially call the error gradient distribution methods for the internal layers of the Feed Forward block. We also call the methods`.

## NN-0084 — 5.3.2.3 File operations

Intervalo da seção no índice: PDF 543–546. Estado: partial_textual_consultation.

Métodos, getters e Save/Load; schema precisa acompanhar profundidade e unidades.

Amostra consultada: PDF 544, caracteres 0–1150; início do trecho: `5. Attention mechanisms //--- virtual bool Init(const CLayerDescription *desc) override; virtual bool SetOpenCL(CMyOpenCL *opencl) over`.

## NN-0085 — 5.3.3 Organizing parallel computing in the GPT model

Intervalo da seção no índice: PDF 547–558. Estado: partial_textual_consultation.

Kernel GPT tem organização distinta; universalizar kernel nem sempre reduz complexidade.

Amostra consultada: PDF 548, caracteres 0–1150; início do trecho: `5. Attention mechanisms have two such blocks: one in the feed-forward part, and the second, mirrored to the first, included in the error gradient propagation method when pe`.

## NN-0086 — 5.3.4 Comparative testing of implementations

Intervalo da seção no índice: PDF 559–569. Estado: partial_textual_consultation.

Mesmos parâmetros herdados não asseguram mesma tarefa; comparar tamanhos e exemplos.

Amostra consultada: PDF 560, caracteres 0–1150; início do trecho: `5. Attention mechanisms input double LearningRate = 0.00003; // Number of hidden layers input int HiddenLayers = 3; // Number of neurons in`.

## NN-0087 — 6. Architectural solutions for improving model convergence

Intervalo da seção no índice: PDF 570–650. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0088 — 6.1 Batch normalization

Intervalo da seção no índice: PDF 571–622. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0089 — 6.1.1 Principles of batch normalization implementation

Intervalo da seção no índice: PDF 572–574. Estado: partial_textual_consultation.

Normalização usa média, variância,epsilon e escala treinável; custo adicional de estado.

Amostra consultada: PDF 573, caracteres 0–1450; início do trecho: `6. Architectural solutions for improving model convergence where: · μB = arithmetic mean of the dataset · m = dataset size (batch) Then we calculate the variance`.

## NN-0090 — 6.1.2 Building a batch normalization class in MQL5

Intervalo da seção no índice: PDF 575–587. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0091 — 6.1.2.1 Batch normalization feed-forward methods

Intervalo da seção no índice: PDF 578–580. Estado: partial_textual_consultation.

Lote<=1 possui caminho especial; comportamento deve ser testado separadamente.

Amostra consultada: PDF 579, caracteres 0–1450; início do trecho: `6. Architectural solutions for improving model convergence //--- check the size of the normalization batch if(m_iBatchSize <= 1) { m_cOutput`.

## NN-0092 — 6.1.2.2 Batch normalization backpropagation methods

Intervalo da seção no índice: PDF 581–585. Estado: partial_textual_consultation.

Gradiente atravessa ativação e normalização; conferir fatores de escala.

Amostra consultada: PDF 582, caracteres 0–1450; início do trecho: `6. Architectural solutions for improving model convergence should simply call the appropriate method of this class and provide a pointer to the error gradient buffer of our`.

## NN-0093 — 6.1.2.3 File operations

Intervalo da seção no índice: PDF 586–587. Estado: partial_textual_consultation.

Persistência encadeada salva tamanho de lote e estado herdado; checar leituras e escritas.

Amostra consultada: PDF 587, caracteres 0–1450; início do trecho: `6. Architectural solutions for improving model convergence if(!CNeuronBase::Save(file_handle)) return false; It is very convenient to use the method of`.

## NN-0094 — 6.1.3 Organizing multi-threaded computations in the batch normalization class

Intervalo da seção no índice: PDF 588–597. Estado: partial_textual_consultation.

TYPE4 e vetorização dependem de hardware; não adotar promessa genérica de um ciclo.

Amostra consultada: PDF 589, caracteres 0–1450; início do trecho: `6. Architectural solutions for improving model convergence int total) { The last parameter is necessary because we us`.

## NN-0095 — 6.1.4 Implementing batch normalization in Python

Intervalo da seção no índice: PDF 598–607. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0096 — 6.1.4.1 Creating a script to test batch normalization

Intervalo da seção no índice: PDF 601–607. Estado: partial_textual_consultation.

Duas bases normalizada/não normalizada e separação dos dois alvos; preservar schema.

Amostra consultada: PDF 602, caracteres 0–1450; início do trecho: `6. Architectural solutions for improving model convergence skipinitialspace=True, encoding='utf-8',`.

## NN-0097 — 6.1.5 Comparative testing of models using batch normalization

Intervalo da seção no índice: PDF 608–622. Estado: partial_textual_consultation.

Comparação insere normalização antes da camada; ablação precisa controlar demais fatores.

Amostra consultada: PDF 609, caracteres 0–1450; início do trecho: `6. Architectural solutions for improving model convergence To test the approach, we will create a script that uses one fully connected hidden layer and a fully connected la`.

## NN-0098 — 6.2 Dropout

Intervalo da seção no índice: PDF 623–650. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0099 — 6.2.1 Building Dropout in MQL5

Intervalo da seção no índice: PDF 625–634. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0100 — 6.2.1.1 Feed-forward method

Intervalo da seção no índice: PDF 629–630. Estado: partial_textual_consultation.

Modo operação copia entrada, treino aplica máscara; não deixar aleatoriedade de treino em inferência.

Amostra consultada: PDF 630, caracteres 0–1450; início do trecho: `6. Architectural solutions for improving model convergence After generating the masking vector, we only need to apply it to the initial data. To do this, we multiply two bu`.

## NN-0101 — 6.2.1.2 Backpropagation methods for Dropout

Intervalo da seção no índice: PDF 631–632. Estado: partial_textual_consultation.

Retropropagação reaplica máscara da passagem; não amostrar outra máscara.

Amostra consultada: PDF 632, caracteres 0–1450; início do trecho: `6. Architectural solutions for improving model convergence In the implementation block using MQL5, we check the class operating mode. During operational use mode, we simply`.

## NN-0102 — 6.2.1.3 File operations

Intervalo da seção no índice: PDF 633–634. Estado: partial_textual_consultation.

Persistir probabilidade e carregar na mesma ordem; validar domínio após carga.

Amostra consultada: PDF 634, caracteres 0–1450; início do trecho: `6. Architectural solutions for improving model convergence //--- call the method of the parent class if(!CNeuronBase::Save(file_handle)) return false;`.

## NN-0103 — 6.2.2 Organizing multi-threaded operations in Dropout

Intervalo da seção no índice: PDF 635–640. Estado: partial_textual_consultation.

MaskMult realiza produto elemento a elemento; máscara e saída devem ter mesma forma.

Amostra consultada: PDF 636, caracteres 0–1450; início do trecho: `6. Architectural solutions for improving model convergence In the body of the kernel, we define the ID of the current thread and transfer the necessary data from the buffer`.

## NN-0104 — 6.2.3 Implementing Dropout in Python

Intervalo da seção no índice: PDF 641–645. Estado: partial_textual_consultation.

Experiência combina BN e dropout; observação negativa não é proibição universal.

Amostra consultada: PDF 642, caracteres 0–1450; início do trecho: `6. Architectural solutions for improving model convergence metrics=['accuracy']) model1do.summary() Please note that in all Dropout layers, we will`.

## NN-0105 — 6.2.4 Comparative testing of models with Dropout

Intervalo da seção no índice: PDF 646–650. Estado: partial_textual_consultation.

Poucas características e coadaptação são explicações hipotéticas; não provar causalidade só pelo gráfico.

Amostra consultada: PDF 647, caracteres 0–1450; início do trecho: `6. Architectural solutions for improving model convergence Comparative model testing with Dropout`.

## NN-0106 — 7. Testing trading capabilities of the model

Intervalo da seção no índice: PDF 651–689. Estado: structural_via_children_not_read_in_full.

Agregador do índice; consultar notas dos descendentes. Sem declaração de leitura integral.

## NN-0107 — 7.1 Introduction to MetaTrader 5 Strategy Tester

Intervalo da seção no índice: PDF 652–653. Estado: partial_textual_consultation.

Tester possui cálculo e simulação de atrasos; configuração concreta limita conclusão.

Amostra consultada: PDF 653, caracteres 0–1450; início do trecho: `7. Testing trading capabilities of the model The capabilities of the tester are not limited to just testing. It can also be used to solve mass optimization tasks. In the`.

## NN-0108 — 7.2 Developing an Expert Advisor template using MQL5

Intervalo da seção no índice: PDF 654–660. Estado: partial_textual_consultation.

EA carrega modelo já treinado; não confundir inferência com treinamento no EA.

Amostra consultada: PDF 655, caracteres 0–1450; início do trecho: `7. Testing trading capabilities of the model input double ProfitMultiply = 0.8; input int MinTarget=100; input int`.

## NN-0109 — 7.3 Creating a model for testing

Intervalo da seção no índice: PDF 661–674. Estado: partial_textual_consultation.

Script especifica arquitetura e parâmetros e salva histórico; pesos e schema exigem rastreabilidade.

Amostra consultada: PDF 662, caracteres 0–1450; início do trecho: `7. Testing trading capabilities of the model // Number of input layer neurons per 1 bar input int NeuronsToBar = 4; // Use OpenCL input bool UseO`.

## NN-0110 — 7.4 Determining Expert Advisor parameters

Intervalo da seção no índice: PDF 675–685. Estado: partial_textual_consultation.

Autor reutiliza2015–2020 de treino para otimizar EA; reconhecer dependência do ajuste.

Amostra consultada: PDF 676, caracteres 0–1450; início do trecho: `7. Testing trading capabilities of the model The best tool to do this is the MetaTrader 5 strategy tester. In the terminal, press Ctrl + R and navigate to the tester. In`.

## NN-0111 — 7.5 Testing the model on new data

Intervalo da seção no índice: PDF 686–689. Estado: partial_textual_consultation.

Resultado positivo anual apresentado; não infere rentabilidade em outros períodos ou com custos distintos.

Amostra consultada: PDF 687, caracteres 0–1450; início do trecho: `7. Testing trading capabilities of the model Forward testing of the model During the testing period, the Expert Advisor made`.

## NN-0112 — Conclusion

Intervalo da seção no índice: PDF 690–690. Estado: partial_textual_consultation.

Conclusões amplas do autor excedem a generalização demonstrada; manual preserva como observações limitadas.

Amostra consultada: PDF 690, caracteres 0–1450; início do trecho: `7. Testing trading capabilities of the model 1. During technical analysis, it's possible to identify certain patterns that can generate quite stable signals for ex`.

## Fundamentos REF/TRD consultados

REF:84,98–101,108,144–147,159–160,163–164,1263,2201–2202 (trechos iniciais850–1200caracteres; consultas adicionais iniciais, sem leitura integral de todas essas páginas). Tipos e larguras; representaçãoIEEE754; comparação aproximada; divisão inteira; casts de descritores; const e referências; AS_SERIES e ordem temporal.

TRD:44–47,81–87,141–143,166–174,205–210,242–249,339–340,378–379 (trechos iniciais850–1200caracteres). Estruturas protegem significado; classes protegem invariantes; CheckPointer distingue objetos automáticos/dinâmicos; ArrayResize com reserva altera custo, não conteúdo válido. Cobertura parcial e deliberada; demais seções são do trabalho do integrador.

## Fontes do produto e complementos

STOIKUS_USO_DIARIO.md: consultados início e trechos finais exibidos (saída truncada). Confirma quatro programas, Monitor sem ordens, Supervisor separado, cálculo1.9.0 eNOT_RUN. Nenhuma alteração produtiva.

Consulta web oficial2026-10-15: https://www.mql5.com/en/docs/onnx e https://www.mql5.com/en/docs/onnx/onnxrun. Inspeção de sessão, formas, execução, retorno e flags. Documentação online é complemento; não se presume build/dispositivo suportado. Menos200palavras derivadas de cada página no manual.

## Fórmulas e figuras a conferir pelo integrador

Conferência visual prioritária: NN8(neurônio),30–33(perdas),335–338(LSTM),403–405(atenção),572–574(normalização), e231–233(diferença finita). Equações do manual são reexpressões matemáticas, não transcrição verificada de imagens. Figuras recomendadas: fluxo treino/validação/teste com ajuste só no treino; célulaLSTM com c/h; matriz atenção causal. São propostas, não arquivos desenhados nesta subtarefa.

## Rodada ampliada de consulta

Todas as folhas receberam amostra de início, meio e fim, com as janelas abaixo. Páginas222–239 e87 foram recuperadas e lidas integralmente em texto; não houve inspeção visual. Amostragem de várias posições melhora a análise dos contratos e conclusões, mas ainda não permite declarar leitura integral de todas as seções nem validação linha a linha do código.

- NN-0002: meio PDF6 caracteres0–550; fim PDF6 últimos1000caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0004: meio PDF9 caracteres0–550; fim PDF11 últimos1000caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0005: meio PDF17 caracteres0–550; fim PDF22 últimos1000caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0006: meio PDF24 caracteres0–550; fim PDF25 últimos1000caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0008: meio PDF30 caracteres0–550; fim PDF32 últimos1000caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0009: meio PDF35 caracteres0–550; fim PDF37 últimos1000caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0010: meio PDF42 caracteres0–550; fim PDF47 últimos1000caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0012: meio PDF48 caracteres0–550; fim PDF49 últimos1000caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0013: meio PDF50 caracteres0–550; fim PDF51 últimos1000caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0014: meio PDF53 caracteres0–550; fim PDF55 últimos1000caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0015: meio PDF56 caracteres0–550; fim PDF56 últimos1000caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0017: meio PDF63 caracteres0–550; fim PDF66 últimos1000caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0018: meio PDF69 caracteres0–550; fim PDF71 últimos1000caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0019: meio PDF76 caracteres0–550; fim PDF81 últimos1000caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0020: meio PDF82 caracteres0–550; fim PDF83 últimos1000caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0022: meio PDF85 caracteres0–550; fim PDF86 últimos1000caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0023: meio PDF93 caracteres0–600; fim PDF99 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0024: meio PDF93 caracteres0–600; fim PDF99 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0026: meio PDF102 caracteres0–600; fim PDF103 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0027: meio PDF105 caracteres0–600; fim PDF106 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0028: meio PDF116 caracteres0–600; fim PDF125 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0029: meio PDF127 caracteres0–600; fim PDF129 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0030: meio PDF133 caracteres0–600; fim PDF137 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0032: meio PDF140 caracteres0–600; fim PDF141 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0033: meio PDF151 caracteres0–600; fim PDF160 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0034: meio PDF164 caracteres0–600; fim PDF168 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0036: meio PDF177 caracteres0–600; fim PDF185 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0037: meio PDF201 caracteres0–600; fim PDF217 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0038: meio PDF219 caracteres0–750; fim PDF221 últimos550caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0039: meio PDF225 caracteres0–600; fim PDF229 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0040: meio PDF234 caracteres0–600; fim PDF239 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0041: meio PDF250 caracteres0–750; fim PDF261 últimos550caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0044: meio PDF264 caracteres0–600; fim PDF265 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0045: meio PDF276 caracteres0–600; fim PDF286 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0046: meio PDF296 caracteres0–600; fim PDF306 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0047: meio PDF310 caracteres0–600; fim PDF313 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0048: meio PDF323 caracteres0–600; fim PDF333 últimos620caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0050: meio PDF336 caracteres0–600; fim PDF338 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0052: meio PDF354 caracteres0–600; fim PDF358 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0053: meio PDF363 caracteres0–600; fim PDF367 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0054: meio PDF369 caracteres0–600; fim PDF371 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0055: meio PDF376 caracteres0–600; fim PDF380 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0057: meio PDF386 caracteres0–600; fim PDF388 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0058: meio PDF394 caracteres0–600; fim PDF400 últimos442caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0061: meio PDF404 caracteres0–600; fim PDF405 últimos950caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0063: meio PDF419 caracteres0–600; fim PDF422 últimos950caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0064: meio PDF426 caracteres0–600; fim PDF430 últimos950caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0065: meio PDF432 caracteres0–600; fim PDF433 últimos950caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0066: meio PDF444 caracteres0–600; fim PDF455 últimos950caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0067: meio PDF457 caracteres0–600; fim PDF458 últimos950caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0069: meio PDF462 caracteres0–600; fim PDF463 últimos950caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0071: meio PDF476 caracteres0–600; fim PDF478 últimos832caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0072: meio PDF482 caracteres0–600; fim PDF485 últimos950caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0073: meio PDF486 caracteres0–600; fim PDF487 últimos950caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0074: meio PDF493 caracteres0–600; fim PDF498 últimos950caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0076: meio PDF504 caracteres0–600; fim PDF506 últimos411caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0077: meio PDF508 caracteres0–600; fim PDF510 últimos950caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0078: meio PDF513 caracteres0–600; fim PDF515 últimos273caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0080: meio PDF517 caracteres0–600; fim PDF517 últimos950caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0082: meio PDF531 caracteres0–600; fim PDF533 últimos950caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0083: meio PDF538 caracteres0–600; fim PDF542 últimos832caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0084: meio PDF544 caracteres0–600; fim PDF546 últimos950caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0085: meio PDF552 caracteres0–600; fim PDF558 últimos950caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0086: meio PDF564 caracteres0–600; fim PDF569 últimos950caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0089: meio PDF573 caracteres0–650; fim PDF574 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0091: meio PDF579 caracteres0–650; fim PDF580 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0092: meio PDF583 caracteres0–650; fim PDF585 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0093: meio PDF586 caracteres0–650; fim PDF587 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0094: meio PDF592 caracteres0–650; fim PDF597 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0096: meio PDF604 caracteres0–650; fim PDF607 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0097: meio PDF615 caracteres0–650; fim PDF622 últimos664caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0100: meio PDF629 caracteres0–650; fim PDF630 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0101: meio PDF631 caracteres0–650; fim PDF632 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0102: meio PDF633 caracteres0–650; fim PDF634 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0103: meio PDF637 caracteres0–650; fim PDF640 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0104: meio PDF643 caracteres0–650; fim PDF645 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0105: meio PDF648 caracteres0–650; fim PDF650 últimos307caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0107: meio PDF652 caracteres0–650; fim PDF653 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0108: meio PDF657 caracteres0–650; fim PDF660 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0109: meio PDF667 caracteres0–650; fim PDF674 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0110: meio PDF680 caracteres0–650; fim PDF685 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0111: meio PDF687 caracteres0–650; fim PDF689 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.
- NN-0112: meio PDF690 caracteres0–650; fim PDF690 últimos1050caracteres. Consulta adicional parcial; não cobre todo código ou figura.

## Achados adicionais e limites

- PDF87: Seção3.2 efetivamente em87; marcação do índice a estende até99 porque3.3 começa na mesma página. Consultada87 integralmente. Não duplicar87–99 como duas leituras.
- PDF222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239: Consulta textual integral222–239 após recuperar trechos truncados. 3.9 promove sorteio e normalização pré-split;3.10 mantém referência,perturba±delta e agrega diferenças. Norma relativa proposta no manual evita cancelamento de diferenças assinadas.
- PDF47,185: ExemplosAdam exibem correçãoM/(1-beta1),V/(1-beta2),sem potência temporal visível. Necessita conferência do algoritmo completo antes de tratar comoAdam canônico; não reproduzido nem diagnosticado como bug produtivo.
- PDF265: Trecho final chama retropropagação de unsupervised. Manual corrige implicitamente: retropropagação é diferenciação de um objetivo, não categoria exclusiva de supervisão.
- PDF251,256,258,260: CPU vence rede pequena; modelos e validação/teste divergem por composição de dados; autor reconhecehiperparâmetrosnãoajustados. Curvas semelhantes não provam equivalência de implementação.
- PDF325,326,327,328,330,331,332,333: Reordenação de matriz altera operaçãoCNN; experimentoinicialpiora,combinação melhora;MSE eAccuracypreferemmodelosdistintos e diferençaspequenas.
- PDF394,395,396,397,398,399,400: ComparaçãoCNN/LSTM altera ordem de amostragem e capacidade;LSTMsembloco denso melhora inicial;autor398limita a conclusãoà tarefa,399resultadospróximos.
- PDF514,568,569: Número de cabeças implica tradeoff de recursos;GPTusa cache deKeV, ampliar pilha altera temporários, não necessariamente pesos. Isto não elimina custo da atenção densa.
- PDF614,616,618,619,620,621,622: BNexperimentada entrada/intermediárias;testes próximos,autor619reportadiferença<=5e-3;621taxaaumentada10vezes éresultadoespecífico,não recomendação universal.
- PDF646,648,649,650: Dropoutpiora métricasdeteste;649autoradmite explicaçãohipotéticaeinsuficiência de informação. RejeitarproibiçãouniversalBN+dropout.
- PDF674,675,676,680,685,686,687,688,689,690: Treino longo~2diasé relato doautor/hardware;otimização95passesvs>100k combinaçõesnão provaótimo;36trades/21vencedorasem2021;filtrardiasapósforwardretornaaoajuste.

## Introduções diretas de seções agregadoras

- NN-0051: PDF339,344,349 caracteres0–850. Initadapta portas eprofundidade mínima2;decisão de fallback precisa decontrato. Consulta parcial adicional aos filhos.
- NN-0056: PDF381,382,383 caracteres0–850. ParâmetrosKeras eautoseleção deimplementação sujeitosaambiente;semprova nativa. Consulta parcial adicional aos filhos.
- NN-0062: PDF406,410,415 caracteres0–850. Valida count/window/window_out e usa normalização sequencial; eixos concretos diferem de interpretações genéricas. Consulta parcial adicional aos filhos.
- NN-0068: PDF459,460 caracteres0–850. Cabeças concatenadas e projeçãoW0;não garante relaçãocausal. Consulta parcial adicional aos filhos.
- NN-0070: PDF464,469,473 caracteres0–850. TransposedOutput alinha posições emlinhas;Initcontexto deveabrangerW0. Consulta parcial adicional aos filhos.
- NN-0075: PDF499,500,501 caracteres0–850. CustomLayersepara __init__,build,call;formadeentrada afeta pesos. Consulta parcial adicional aos filhos.
- NN-0081: PDF518,523,528 caracteres0–850. CacheKeVporcamada,Initforms e contexto propagado por coleções. Consulta parcial adicional aos filhos.
- NN-0090: PDF575,576,577 caracteres0–850. BNpreserva quantidade,treina escala/deslocamento,inicializa gamma1/beta0. Consulta parcial adicional aos filhos.
- NN-0095: PDF598,599,600 caracteres0–850. Inferênciausamédiasmóveis dotreino e trainablealterado exige recompilação domodelo. Consulta parcial adicional aos filhos.
- NN-0098: PDF623,624 caracteres0–850. DescriçãoamostragemDropout e coadaptação; vantagensnãouniversais. Consulta parcial adicional aos filhos.
- NN-0099: PDF625,626,627,628 caracteres0–850. Dropoutsem pesoscria máscara epropaga flagTrainMode porcamadas. Consulta parcial adicional aos filhos.


Consulta suplementar: REF, MathIsValidNumber, PDF 1986, texto integral. Assinatura bool(double); retorna falso para NaN e infinitos. Acrescentada referência junto ao exemplo sintético do capítulo 2.
