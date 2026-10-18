# Síntese crítica das fontes e aplicação ao Stoikus

Este anexo organiza conhecimento adquirido e propostas. Não é errata oficial da
MetaQuotes, não altera os livros e não identifica automaticamente defeitos no
Stoikus. Os registros individuais de pesquisa conservam os intervalos efetivamente
lidos e o fundamento de cada observação. Código discutido sem compilação ou ensaio
mantém estado **NOT_RUN**.

## O valor e o limite de um exemplo oficial

A Referência estabelece contratos de linguagem e APIs. Os livros de programação
mostram como combinar esses recursos para resolver problemas. Um exemplo pode
ilustrar corretamente uma ideia e ainda omitir recuperação, validação de entrada,
concorrência ou condições extremas. A origem oficial não transforma uma omissão
didática em política aceitável para um sistema que preserva histórico financeiro.

Por isso, o estudo utiliza dois percursos. Primeiro reconstrói o mecanismo que o
livro pretende ensinar; depois procura uma entrada ou uma sequência de eventos que
contradiga a generalização proposta. Uma contraprova matemática pode ser conclusiva
no seu domínio. Uma suspeita sobre execução MQL5 precisa de compilação e reprodução
antes de ser promovida a defeito operacional confirmado.

## Representação, intervalos e resultados aparentemente plausíveis

As partes iniciais de TRD ensinam tipos, expressões, arrays e classes. A aplicação
imediata ao Stoikus é exigir contratos para unidade, precisão, ordem e identidade.
Um identificador representado em ponto flutuante pode perder distinções; uma divisão
inteira pode eliminar a fração antes do cast; uma máscara válida pode ocultar todas
as métricas sem significar que os dados deixaram de existir.

A análise de TRD encontrou casos que ajudam a construir controles negativos. O
exemplo de distribuição de `MathRand`, em PDF402, divide 32767 por dez para formar
intervalos inteiros. Com divisor 3276, valores a partir de 32760 produzem índice dez
para um array de dez posições. Essa é uma inferência estática verificável sobre o
trecho impresso. Sua utilidade é mostrar por que se deve testar a extremidade
superior, e não apenas observar um histograma plausível de uma execução.

Para o Stoikus, a proposta é manter o cálculo normativo como autoridade separada e
testar as fronteiras dos adaptadores com unidades explícitas. O manual não importa
os valores econômicos dos exemplos e não redefine arredondamentos financeiros.

## Ownership é mais forte que um descritor válido

TRD apresenta encapsulamento e liberação de recursos; NN amplia o problema com
camadas, buffers e contexto OpenCL. Saber que um descritor é válido não prova que
a instância atual seja sua proprietária. Um callback de encerramento pode acontecer
depois de uma inicialização parcial, e uma atribuição posterior pode substituir o
recurso que a rotina pretendia liberar.

Na seção de arquivos de TRD, os leitores registraram limites do wrapper didático:
reatribuição sem fechamento do recurso anterior e sinalização de sucesso sem
conferir a quantidade efetivamente gravada. Em NN147 e160, o compartilhamento do
contexto e a restauração de estruturas exigem conferir ownership e dimensões; o
texto impresso não substitui essa prova. As notas detalhadas distinguem trechos
observados de hipóteses dependentes do programa completo.

A consequência para o Stoikus é um contrato de aquisição, transferência e limpeza
por proprietário. A falha no terceiro recurso deve preservar a possibilidade de
liberar corretamente os dois primeiros; a segunda limpeza precisa encontrar um
estado já vazio. Não é necessário criar uma classe complexa para cada handle, mas
é necessário poder demonstrar essas transições.

## Séries temporais não são apenas matrizes com muitas linhas

NN225–230 descreve sorteio de amostras, normalização do período analisado e
preenchimento de dados ausentes com zero. Esses procedimentos permitem estudar a
rede apresentada. Para um experimento prospectivo, porém, o estado futuro não
pode determinar a transformação aplicada ao passado.

O laboratório original deste pacote mostra o mecanismo de forma simples. Dividir
os valores de treino pelo máximo do próprio treino gera uma representação;
acrescentar um valor futuro extremo ao cálculo da escala gera outra. A entrada da
rede muda antes mesmo de ajustar os pesos. O resultado não prova que toda escolha
didática do livro seja inadequada para qualquer objetivo; demonstra que o contrato
temporal precisa corresponder à pergunta experimental.

O manual propõe ajuste de transformações no treino, rastreio do período do alvo,
separação temporal e reserva de avaliação que não participe da seleção. No Stoikus
observacional, a aplicação atual é a mesma disciplina de proveniência e atualidade:
barra incompleta, série parcial, ausência e zero são estados diferentes.

## Arquiteturas neurais: aprender o mecanismo e conferir o algoritmo

O livro NN percorre redes densas, convoluções, LSTM, atenção, modelos denominados
GPT, normalização e dropout, em MQL5, Python e OpenCL. A leitura integral do texto
foi dividida em lotes independentes; a inspeção visual e a reprodução executável
continuam com alcance próprio. Essa amplitude permite formular propostas melhores,
mas não autoriza copiar indiscriminadamente as implementações.

Uma afirmação em NN335 associa a comutatividade da soma ponderada à invariância de
uma camada densa à ordem de entrada. O laboratório separa as operações: com pesos
fixos diferentes, permutar apenas as entradas altera o resultado; permutar os pares
peso/entrada conserva a soma. Em NN93, correlação linear nula é discutida no contexto
de dependência. O exemplo original com uma variável e seu quadrado evidencia que
correlação de Pearson zero não estabelece independência.

As leituras de camadas registram outras questões estáticas: limites vetoriais em
OpenCL, convenção de pooling entre implementações, trajetos do gradiente recorrente,
validação de restauração e comparabilidade entre ensaios. O último lote registra
diferenças de eixos de normalização, estabilidade de softmax, manutenção de caches
durante atualização e amostragem no dropout. Essas observações são acompanhadas
de páginas e qualificações nas notas. Não se apresentam como execução observada.

A proposta para pesquisa futura é começar por componentes pequenos: forward
determinístico, gradiente por diferenças finitas, estados recorrentes e máscaras
conhecidas. Depois comparar implementações com os mesmos pesos e entradas. Só então
medir treinamento, generalização e utilidade econômica em campanhas separadas.

## Avaliação que não reaproveita indevidamente a prova

NN676 informa o ajuste de parâmetros do EA no período usado para treinamento. O
resultado posterior de NN688 mostra 36 operações, 21 vencedoras e fator de lucro
1,48. Esses números pertencem ao exemplo e não foram reproduzidos. Não estabelecem
uma taxa futura, nem fazem do limiar de saída da rede uma probabilidade calibrada.
Examinar esse período para selecionar dias da semana, como discutido em NN689,
gera uma nova decisão que exige outra avaliação posterior.

No desenvolvimento assistido por IA surge um problema equivalente: usar a melhor
tentativa para reescrever a rubrica e depois anunciar que o processo passou. O kit
congela fixtures, oráculos e critérios antes das respostas, preserva falhas e exige
um juiz separado. O piloto possui casos sintéticos curtos e uma mesma família de
modelo para construção. Portanto, mesmo uma rodada sem falhas teria alcance
local; não demonstraria superioridade geral sobre outros processos.

## Prioridades propostas

As propostas abaixo são estudos, sem implementação produtiva nesta entrega.

| Prioridade | Mudança a estudar | Benefício | Custo e dependência | Risco | Prova de aceitação |
|---|---|---|---|---|---|
| P1 | Contratos de fronteira com unidade, origem e atualidade | Detectar conversões e defaults silenciosos | Inventário dos adaptadores e regra normativa competente | Documentar sem testar | Casos negativos e oráculo independente |
| P1 | Aquisição e limpeza por proprietário | Recuperar inicialização parcial e reentrada | Mapa de recursos por componente | Liberar recurso compartilhado ou de outra geração | Falha em cada etapa e dupla limpeza |
| P1 | Recibos vinculados ao candidato | Impedir reutilização de prova de outros bytes | Manifestos e conservação de logs | Confundir hash com aprovação operacional | Fonte, dependências, EX5 e ambiente identificados |
| P2 | Orçamento por evento e reconciliação | Tornar atrasos e lacunas diagnosticáveis | Instrumentação e MT5 separado | A medição alterar timing ou expor dados | Cenário reproduzível, carga e limite medido |
| P2 | Estados acionáveis na interface | Explicar motivo e próxima ação | Fonte de estado fora da pintura | Traduzir mensagem e perder significado | Contratos visuais, teclado e ensaio nativo |
| P2 | Piloto do harness em tarefas reais autorizadas | Medir retrabalho e erros relevantes | Baseline comparável e coleta de esforço | Seleção de tarefas favoráveis | Critérios prévios, falhas, tempo e tokens |
| P3 | Pipeline neural isolado | Explorar benefício informativo | Dados versionados, baseline e protocolo temporal | Vazamento, sobreajuste e custo | Equivalência matemática e teste posterior intocado |

A sequência favorece integridade e observabilidade antes de ampliar capacidades.
Uma proposta pode ser rejeitada por não trazer benefício suficiente. O material
não recomenda implantar uma rede, armar o Supervisor ou enviar ordens como
consequência automática da leitura.
