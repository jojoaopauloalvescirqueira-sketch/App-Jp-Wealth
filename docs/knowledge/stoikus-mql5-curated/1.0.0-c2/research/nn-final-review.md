# NN — atenção, GPT, normalização e Dropout: leitura crítica final

## Proveniência e significado da cobertura

Fonte bibliográfica NN: *Neural Networks for Algorithmic Trading with MQL5.pdf*. Leitura semântica do texto completo das páginas físicas PDF401–650,84,227:252 páginas distintas. Numeração impressa visível no rodapé extraído coincide com a física nessas páginas, mas não houve auditoria visual página a página do PDF. Corpus empregado: `/private/tmp/stoikus-mql5-research-20261015/corpus-fast/NN/pages.jsonl`. O manifesto associado registra o hash e o estado de cada página efetivamente lida. Indexação e extração não contam como leitura. As figuras foram consideradas pelas legendas e explicação textual; seus pontos, curvas, fórmulas como imagens e valores não foram conferidos visualmente. Linhas cortadas na extração não foram reconstruídas por suposição. Nenhum resultado de piloto foi consultado.

São quatro tipos distintos de afirmação neste documento: **Fonte** descreve o livro; **Inferência crítica** identifica consequência ou risco a verificar; **Contrato proposto** especifica requisito de uma pesquisa futura; **Observação de contexto** reproduz o BRIEF, sem nova inspeção do código atual. Toda experiência é **NOT_RUN**. Nada aqui declara instalação, treinamento, compilação, execução EX5, aceitação humana ou autorização para negociar.

## Mapa de leitura substantiva

| Páginas PDF | Seção efetivamente lida | Núcleo de entendimento |
|---|---|---|
|84|Fim2.4; introdução3|Limites declarados: trabalho prático, não tratado matemático abrangente de IA.|
|227|3.9 Creating training and testing samples|Sorteio de20% dos índices, exportação CSV e separação no momento da escrita.|
|401|Fim4.2; abertura5|Conclusão recorrente local e motivação de atenção.|
|402–406|5;5.1;5.1.1; início5.1.2|Encoder/decoder, QKV, softmax escalado, residual e normalização.|
|407–415|5.1.2 Building Self-Attention with MQL5 tools|Composição de cinco camadas, dimensões, alias de buffers e contexto OpenCL.|
|416–422|5.1.2.1 Self-Attention feed-forward method|Layout transposto, multiplicação QK, soma ponderada, duas residuais.|
|423–430|5.1.2.2 Self-Attention backpropagation methods|Jacobiano softmax, quatro caminhos de gradiente, derivada da normalização.|
|431–434|5.1.2.3 File operations|Ordem Save/Load, tipos e recomposição dos aliases.|
|434–456|5.1.3 Organizing parallel computing in the attention block|Seis kernels, reduções locais, fronteiras de barreira, ponte host/device.|
|456–459|5.1.4 Testing the attention mechanism|Substituição de arquitetura; convergência menor nas demonstrações.|
|459–464|5.2;5.2.1|Cabeças, concatenação e projeção W0.|
|464–473|5.2.2 Building Multi-Head Self-Attention in MQL5|Inicialização recomposta, `step` como heads, layout dos scores.|
|474–478|5.2.2.1|Passagem por cabeça, concatenação, W0, normalização e FFN.|
|479–485|5.2.2.2|Gradiente W0 calculado antes de reutilizar seu buffer.|
|486–488|5.2.2.3|Persistência herdada mais heads/W0; redimensionamento scores.|
|488–499|5.2.3|Kernels compartilhados passam a duas dimensões; reparar chamadas single-head.|
|499–506|5.2.4;5.2.4.1|Camada Keras customizada, build/call e serialização.|
|507–511|5.2.4.2|Quatro arquiteturas, fit/evaluate, treinamento e avaliação.|
|511–516|5.2.5|Comparação local de convergência e consumo por cabeça.|
|516–518|5.3;5.3.1|Motivação GPT, decoder, causalidade e cache.|
|518–528|5.3.2|Bloco multicamada, memória K/V, estado e posição circular.|
|529–533|5.3.2.1|Atualiza uma entrada, consulta memória e passa residual/FFN.|
|534–542|5.3.2.2|Backprop corrente; coleções percorridas inversamente.|
|543–547|5.3.2.3|Salvar posição e coleções, recompor formatos e aquecer histórico.|
|547–559|5.3.3|Kernels GPT por cabeça, score temporário e offsets concatenados.|
|559–570|5.3.4|Teste com cinco candles por entrada,40/60 estados, warm-up e ruído.|
|570–575|6;6.1;6.1.1|BN, escala/deslocamento e alternativa EMA.|
|575–577|6.1.2|γ/β no buffer de pesos e três estatísticas por elemento.|
|578–580|6.1.2.1|Normalização online por EMA, ativação opcional, bypass batch≤1.|
|581–585|6.1.2.2|Gradiente corrente e acumulação de γ/β.|
|586–588|6.1.2.3|Persistência das estatísticas e batch.|
|588–598|6.1.3|TYPE4, tratamento da cauda, kernels de forward/gradiente.|
|598–600|6.1.4|BN Keras distingue treinamento de inferência.|
|601–608|6.1.4.1|Dados normais/brutos, modelos de1/3 camadas, avaliação.|
|608–623|6.1.5|Experimentos de entrada/intermediárias e learning-rate10×.|
|623–625|6.2|Co-adaptação, máscara e compensação1/q.|
|625–628|6.2.1|TrainMode, clamp de probabilidade e ausência de pesos.|
|629–630|6.2.1.1|Máscara de cardinalidade fixa e aplicação por produto.|
|631–632|6.2.1.2|Reutilização da máscara no gradiente.|
|633–634|6.2.1.3|Salvar probabilidade e restaurar valores derivados.|
|635–640|6.2.2|MaskMult e cópia via ativação linear em inferência.|
|641–646|6.2.3|Dropout Keras, seed/noise_shape, quatro variantes e gráficos.|
|646–650|6.2.4, parcial por fronteira atribuída|Pior teste local apesar de menor divergência treino/validação.|

Os intervalos que compartilham uma página representam títulos que começam no meio da página; não duplicam contagem. A seção6.2.4 continua depois650 e não é declarada completa neste parecer.

##1. Validade da demonstração vem antes da arquitetura

**Fonte.** O prefácio do capítulo3 explicita que o objetivo é comparar implementações práticas e oferecer conceitos básicos sem desenvolvimento matemático profundo [NN,3,introdução,p.PDF84]. Isso delimita o uso adequado: o livro é excelente roteiro de construção, porém não certificado de correção de cada derivada nem prova de vantagem financeira. O próprio fechamento GPT reconhece que modelos pequenos e treinamento breve bastam para demonstrar funcionalidade, não para uso real [NN,5.3.4,p.PDF570].

**Fonte.** A página227 escolhe índices aleatórios para teste por produto de dois MathRand, rejeita duplicatas e escreve CSV conforme flags. A janela requer várias barras anteriores. **Inferência crítica.** Divisão por linha aleatória não assegura independência temporal: padrões vizinhos podem compartilhar quase todas as entradas e intervalos de formação do alvo. A expressão produto de duas variáveis uniformes tampouco produz índice uniforme. Não inferir desses20% uma validação cronológica ou walk-forward. Sem ler a construção inteira do alvo fora desta atribuição, não se quantifica seu horizonte ou a extensão da sobreposição.

**Contrato proposto.** Um dataset de pesquisa deve guardar timestamp de disponibilidade, janela de observação, horizonte do alvo, origem e versão de cada feature. Separar treino/validação/teste cronologicamente, purgar sobreposição nas fronteiras conforme os intervalos reais e ajustar estatísticas exclusivamente no treino. Teste final fica fechado durante escolha de arquitetura. A página227 fundamenta a necessidade do cuidado, não demonstra cumprimento deste contrato.

As comparações posteriores mantêm o mesmo dataset e mudam camadas; isso ajuda a observar efeito local, mas não resolve vazamento, seleção repetida do melhor modelo ou não estacionariedade. MSE de saídas contínuas não é desvio-padrão; o livro usa por vezes esses termos de modo intercambiável. `accuracy` precisa de regra explícita: em duas saídas de regressão/tanh, um nome de métrica não garante acerto direcional nem utilidade econômica [NN,5.2.4.2,p.PDF509–511;6.1.4.1,p.PDF603].

##2. Atenção simples: operações, formas e risco numérico

**Fonte.** A atenção generalizada acumula estados do encoder e seleciona contexto condicionado pelo decoder. Self-Attention passa a relacionar elementos da mesma sequência: Q e K geram scores, divisão por√dk ajusta escala, softmax normaliza linhas e o resultado multiplica V. O encoder soma residual e normaliza; depois faz FFN e nova residual [NN,5–5.1.1,p.PDF402–406].

Na implementação, um elemento é uma barra com vetor de propriedades. As projeções compartilham pesos entre barras e são representadas por convoluções de janela/stride iguais ao tamanho desse vetor. Não é uma convolução temporal arbitrária: esse uso replica uma transformação por elemento. `count=N`, `window=d`, `window_out=dk`; V retorna dimensão d para permitir soma residual. O buffer Scores é N×N, distinto do número Nd de escalares da entrada. FFN expande4× e usa Swish, uma escolha do autor que difere da ReLU da descrição arquitetural [NN,5.1.2,p.PDF407–413].

**Inferência crítica.** Transpor a disposição dos resultados altera o significado dos índices em forward, hidden-gradient e delta-weights. Reshape compatível em quantidade não prova alinhamento semântico. O alias entre saída/gradiente externos e FF2 evita cópias, mas cria obrigação de ownership e recomposição após Load; a própria fonte alerta contra ponteiro invalidado por delete [NN,5.1.2.1,p.PDF416–422;5.1.2.3,p.PDF433–434].

O forward calcula `exp(QKᵀ/√dk)` diretamente, sem subtrair máximo por linha. Entradas grandes podem produzir Inf e posterior Inf/Inf; entradas muito negativas podem zerar denominador. Este é um risco inferido do algoritmo mostrado, não resultado de execução [NN,5.1.2.1,p.PDF418;5.1.3,p.PDF436–437]. Normalização também precisa definir eixo, epsilon e variância. O MQL descrito normaliza todo buffer, enquanto Keras usa LayerNormalization do último eixo por padrão; não considerar as duas implementações numericamente equivalentes sem mapear essas escolhas [NN,5.1.3,p.PDF438–440;5.2.4.1,p.PDF503–505].

Na reversa, o gradiente de V é Scoresᵀ·G; o de Scores é G·Vᵀ. Softmax exige jacobiano acoplado dentro da linha; Q e K recebem produtos com o tensor oposto e escala1/√dk. Quatro caminhos chegam à entrada, três projeções mais residual. Acumular em buffer diferente é necessário quando cada chamada sobrescreve o gradiente anterior [NN,5.1.2.2,p.PDF423–430]. A linha de `dSTD` p429 está cortada no corpus: este parecer não valida a fórmula completa pela extração.

**Contrato proposto.** Oracle pequeno de matrizes rotuladas por índice; checagem de dimensões e finitude em cada fronteira; invariância da soma por linha do softmax; finite differences das derivadas; comparação CPU/GPU com tolerâncias de dtype; casos constantes, extremos e dimensão1. Todos NOT_RUN.

##3. OpenCL: paralelismo exige contrato de memória

**Fonte.** O livro separa cálculo QKV/FFN já encapsulado de kernels próprios para atenção, soma, normalização e gradientes. Dados intermediários permanecem no device; transferir ao host para uma soma pode custar mais que executá-la no device. Normalização usa memória local e barreiras, com um único grupo global/local limitado por LOCAL_SIZE [NN,5.1.3,p.PDF435–456].

**Inferência crítica.** Este desenho depende de todas as threads alcançarem barreiras na mesma ordem; tamanho de grupo e índices da redução fazem parte da correção. A redução mostrada com `(count+1)/2` merece casos ímpares e pequenos, verificando limites de acesso e ausência de dupla soma. O custo quadrático de Scores permanece: acelerar não elimina N² de memória. Presença de um índice de buffer não prova conteúdo atualizado. `SumArray` p452 verifica `src.GetIndex()<0` e chama `BufferCreate` no objeto corrente; conferir intenção e objeto destinatário antes de copiar o trecho para outro projeto. As omissões e pequenos erros tipográficos de trechos impressos, como separador na criação de kernel p450, reforçam que o texto não substitui fonte compilável.

**Contrato proposto.** Cada buffer declara proprietário, tamanho, layout, dtype, contexto, última escrita e sincronização necessária. Falha ao alocar ou lançar kernel é erro rastreável, nunca autorização para consumir resultados antigos. Benchmark inclui upload, download, inicialização e aquecimento, junto com tempo do kernel. Não há medição realizada neste estudo.

##4. Multi-Head: W0 não é votação interpretável

**Fonte.** Múltiplas projeções produzem cabeças distintas; resultados são concatenados e projetados por W0 para a dimensão residual. O livro chama a combinação de compromisso entre opiniões, mas operacionalmente é uma transformação treinável. Concatenar projeções reduz número de objetos; a implementação host separa cabeças em matrizes, calcula atenção e recompõe o layout. A GPU reutiliza kernels com espaço bidimensional sequência×heads; chamadas single-head também precisam migrar para a segunda dimensão igual1 [NN,5.2.1–5.2.3,p.PDF461–499].

O parâmetro `step` passa a significar número de cabeças. Isso é economia de descrição com custo de legibilidade, explicitamente reconhecido pelo autor. Um contrato externo deveria usar nomes de domínio e impedir reinterpretar silenciosamente configuração de convolução como atenção [NN,5.2.2,p.PDF466].

O backward traz detalhe importante: W0 precisa calcular delta-weights antes de seu gradiente ser reutilizado como acumulador dos quatro caminhos. A ordem importa por mutação de buffers, mesmo que operações matemáticas independentes admitam outra ordem [NN,5.2.2.2,p.PDF483–485]. Load herdado recria Scores para uma cabeça e o filho deve ampliar novamente [NN,5.2.2.3,p.PDF487–488]. O texto declara W0 como objeto estático mas mostra teste de ponteiro e `new` p487: verificar fonte anexa e versão, sem declarar compilação por leitura.

**Fonte.** Em Keras, `build` resolve formas desconhecidas; `call` faz operações; framework fornece autodiferenciação. Registro serializável/get_config/from_config tratam restauração [NN,5.2.4,p.PDF499–506]. **Contrato proposto.** Fixar versões e provar round-trip Save→Load com entradas fixas, incluindo custom layer. O código didático não é garantia de compatibilidade com versões atuais de TensorFlow/Keras.

**Inferência crítica.** A afirmação de que recorrência impede qualquer shuffle p509 precisa de condição: rede stateful entre amostras requer ordem; uma LSTM stateless pode embaralhar janelas independentes preservando ordem dentro de cada janela. EarlyStopping monitora loss de treino, não val_loss. P511 imprime `test_acc5/test_loss5` no bloco identificado como quatro camadas, embora o evaluate armazene6 e os gráficos usem6: há erro de apresentação verificável no texto. Os gráficos de superioridade de atenção/cabeças p512–516 são resultados do autor naquele experimento, não resultado reproduzido nem lei geral. Contagem de parâmetros, sementes, ordem e orçamento precisam ser comparáveis.

##5. GPT didático: streaming, causalidade e gradiente truncado

**Fonte.** O modelo apresentado usa blocos decoder e consulta estados passados, cacheando K/V. A implementação financeira recebe estado real novo em vez de gerar token e realimentá-lo. Coleções guardam camadas; uma projeção calcula QKV concatenado, K/V guardam N estados e Scores se reduz a vetor por cabeça. A posição circular evita deslocamento de histórico [NN,5.3.1–5.3.2,p.PDF517–528].

**Inferência crítica.** Chamar esse exemplo de GPT não o torna equivalente a GPT pré-treinado. A fonte diz que treinou do zero p566, diverge da estratégia de pré-treino/fine-tuning discutida na introdução. Não há evidência de transferência de modelo de linguagem para o Stoikus. As referências históricas a GPT-3 são retrato da época do livro, não informação atual de produtos OpenAI.

A fonte reconhece que permutar posições no somatório de atenção não muda resultado e chama isso de desvantagem temporal p529. **Contrato proposto.** Uma pesquisa de séries precisa explicitar informação de ordem/idade e unidades do token. No teste, uma entrada contém cinco candles; N estados no cache não pode ser chamado automaticamente N candles distintos, pois janelas consecutivas se sobrepõem [NN,5.3.4,p.PDF559–564].

A descrição causal zera elementos futuros, porém a implementação streaming consulta todas as posições do cache, inclusive antes do preenchimento. Warm-up completo é requisito e o livro o recomenda após Load [NN,5.3.2.3,p.PDF545]. Também é preciso resetar estado em nova série, símbolo, timeframe, split ou salto temporal. Cache de teste nunca pode herdar futuro ou estado de outra sequência. No treinamento, atualizar pesos mantendo K/V antigos torna o cache potencialmente calculado com versões anteriores dos parâmetros; provar política de refresh/detach/reset é necessário. Não confundir cache eficiente na inferência com equivalência de gradientes no treino.

**Fonte.** O backward propaga V e K somente para o estado corrente, porque não guarda entradas históricas para seus pesos; assume que gradientes passados já foram considerados [NN,5.3.2.2,p.PDF536–539]. **Inferência crítica.** Isso é aproximação com dependências históricas desconectadas, não demonstração de backpropagation completo: perda corrente pode depender de K/V históricos e, portanto, de seus parâmetros. Registrar essa aproximação é indispensável antes de comparar qualidade com transformer integral.

Dois alertas de código merecem conferência: p521 cria `temp` modificado mas chama `CNeuronBase::Init(desc)`; p551 define `shift_value=window*(2*heads+h)` para gravar gradiente V concatenado, depois usa esse mesmo offset em `outputs_grad` que representa só a saída de atenção. A inferência é possível leitura fora de limites ou tensor errado; confirmar fonte executável e shapes antes de concluir. P530 repete declaração Querys em trechos narrativos: não concatenar exemplos impressos cegamente.

O treinamento usa início aleatório de trecho e depois padrões sequenciais, com warm-up ignorado na perda; atualiza com BatchSize mesmo quando fim do dataset limita iterações [NN,5.3.4,p.PDF564–565]. **Contrato proposto.** Contar efetivamente padrões que contribuíram para delta e resetar caches/gradientes deliberadamente. Menor loss, mesmo em stack60, não prova rentabilidade nem comportamento fora da amostra [NN,5.3.4,p.PDF565–570].

##6. Batch normalization: distinguir teoria, aproximação online e inferência

**Fonte.** BN padroniza features e aprende γ/β. O livro troca armazenamento de lote por EMA para média/variância, com batch interpretado como escala temporal de suavização. Guarda média, variância e valor normalizado por elemento; γ começa1 e β0; batch≤1 vira bypass [NN,6.1.1–6.1.2.1,p.PDF572–580].

**Inferência crítica.** Essa implementação online não é BN convencional de minibatch que o próprio texto descreve para Keras p598–600. MQL atualiza estatísticas em cada forward, sem modo treino/inferência explícito nessa classe. Keras usa batch corrente no treino e médias móveis congeladas na inferência. Comparações entre caminhos medem também diferença de algoritmo. A derivada p583 usa grandezas só correntes e argumenta que acumular gradientes ao longo do tempo recupera soma de batch; isso requer demonstração matemática, não decorre automaticamente quando média/variância mudam entre passos.

O caminho CPU calcula EMA sempre dividindo por batch; GPU condiciona divisão ao primeiro valor de um vetor TYPE4 e às estatísticas. GPU também substitui vetor γ inteiro por1 se primeiro γ for zero, o que poderia apagar valor zero legitimamente aprendido. CPU usa epsilon depois de sqrt em forward, enquanto outros caminhos usam dentro; escolhas alteram casos de variância pequena [NN,6.1.2.1,p.PDF579;6.1.3,p.PDF589–591]. Vetorizar quatro doubles não garante execução em um ciclo em qualquer hardware; a advertência do próprio livro para verificar especificações prevalece.

A comparação Python treina `model1` em dados normalizados e depois retreina a mesma instância em dados não normalizados; posteriormente avalia essa instância. Isso contamina o suposto baseline de treinamento do zero e impede atribuir diferenças apenas à normalização [NN,6.1.4.1,p.PDF604–607]. **Contrato proposto.** Instâncias frescas, mesmos pesos iniciais quando cabível, estatísticas sem futuro, denominadores/epsilons declarados e avaliação independente de treinamento. Congelar pesos e mudar modo de inferência são operações distintas, como a fonte explica p599.

A conclusão de menor tempo e possibilidade de learning-rate10× é contextual. Os testes finais têm diferenças pequenas de erro, segundo p619; não apresentar BN como ganho garantido nem regra JP Wealth. A afirmação de incompatibilidade com Dropout p572 deve permanecer hipótese a avaliar por arquitetura e ordem, não proibição universal.

##7. Dropout: a máscara faz parte do algoritmo

**Fonte.** O treino zera features e aplica1/q nas restantes; inferência copia entrada sem máscara; backward reutiliza exatamente a máscara do forward. A classe não tem pesos e seus métodos de atualização retornam sucesso sem trabalho. TrainMode precisa chegar a cada camada. GPU usa MaskMult para treino e ativação linear identidade para inferência, evitando copiar dados ao host [NN,6.2–6.2.2,p.PDF623–640].

**Inferência crítica.** A explicação p624 fala de distribuição normal, mas o algoritmo p629 usa produto de MathRand para escolher índices, com cardinalidade fixa `floor(total*p)` e rejeição de repetidos. Produto de uniformes concentra seleção no começo; não implementa máscaras Bernoulli independentes equiprováveis como Dropout convencional. Se ambos valores atingem32767, índice pode ser total, fora do vetor. A quantização do número de zeros também faz retenção efetiva diferir de q: aplicar1/(1-p) não preserva exatamente expectativa quando o número descartado foi arredondado. O texto p641 diz que a soma transmitida permanece igual; para máscara aleatória a compensação é expectativa, não igualdade em cada amostra.

Probabilidade é limitada a0.9 em Init mas Load p634 lê sem mostrar mesma validação; arquivo com p=1 implica divisão por zero e p inválido pode gerar contagem impossível. Além disso, gerar máscara antes de checar TrainMode pode consumir RNG/custo na inferência mesmo com saída identidade. Propagar modo aos filhos de composições, preservar mesma máscara até backward e versionar arquivo são contratos necessários. `trainable=False` não desliga Dropout, pois não há pesos para congelar [NN,6.2.3,p.PDF641].

Os testes p646–650 mostram pior erro e accuracy no teste com Dropout, mesmo quando a curva de validação sugere menos overfit. O próprio autor admite incerteza sobre causas p649. Isso ensina a não confundir regularização com melhora da tarefa: reduzir gap pode apenas empobrecer capacidade. Não inventar conclusão final da seção, que continua após650.

##8. Ponte permitida com o Stoikus e plano verificável

**Observação de contexto, BRIEF.** Stoikus atual é Monitor/EA orientado a eventos e observacional, não negocia; core1.23.0/MQL1.230/calc1.9.0, quatro programas diários; Supervisor opcional sem autorização para armar. Não há ML atual. Python/OpenCL/ONNX são pesquisa futura. Os48host+6grupos UI são recibo histórico do candidato, não prova nativa nova. Estes fatos foram fornecidos pelo coordenador; este leitor não auditou o produto nem transforma fatos da plataforma em regras normativas.

**Propostas, sem implementação.** A utilidade imediata deste estudo é melhorar especificação de dados e evidências, nunca instalar uma camada neural no Monitor. Primeiro comparar baselines simples em cópia de dados observacionais congelada; depois atenção stateless; somente depois cache streaming se justificar benefício mensurável. Uma saída experimental deve trazer model_id, dataset_hash, versão de feature, horário de corte, validade e erro, sem comandos de ordens nem autoridade para alterar limites. Decisão de pesquisa não muda programas diários nem habilita Supervisor.

| Experiência proposta | Critério antes de discutir aplicação | Estado |
|---|---|---|
|Auditar split temporal|Nenhuma feature/alvo atravessa fronteira proibida; scaler só treino|NOT_RUN|
|Oracle atenção CPU|Shapes/layouts e softmax finitos, derivações por finite differences|NOT_RUN|
|Paridade OpenCL|Mesma definição matemática, tolerâncias, contextos e caudas1/3/4/5|NOT_RUN|
|Persistência|Round-trip previsões e estado; arquivo truncado/tipo inválido rejeitado|NOT_RUN|
|Cache GPT|Reset, warm-up, lacuna temporal e cache após update documentados|NOT_RUN|
|Gradiente GPT|Comparar aproximação corrente com sequência integral em problema pequeno|NOT_RUN|
|BN online versus minibatch|Modos separados e estatísticas causalmente válidas|NOT_RUN|
|Dropout|Uniformidade de índices, limites, seed, expectativa, modo e máscara backward|NOT_RUN|
|Comparação preditiva|Instâncias frescas, múltiplas sementes, orçamento e teste fechado|NOT_RUN|
|Avaliação econômica posterior|Custos, atraso, regime e capacidade separados de MSE/accuracy|NOT_RUN|
|MT5 nativo|Compile/runtime e evidência EX5 independentes dos testes host|NOT_RUN|

A fila de leitura desta atribuição está vazia. Permanecem revisão visual das fórmulas/figuras, acesso ao código anexo e todas as experiências da tabela. O conjunto completo do livro depende dos demais leitores; nenhuma página fora84,227,401–650 foi atribuída a este registro.
