# 7. Testes, depuração e força da evidência

## 7.1 Escolher a afirmação antes de escolher a ferramenta

Um teste começa com a afirmação que pretende sustentar. Uma função conserva a distinção entre zero e indisponibilidade? A auditoria retoma do cursor correto? Duas instâncias evitam publicar simultaneamente? A janela recebe cliques depois de redimensionada? O executável corresponde aos fontes examinados? Essas perguntas exigem observações diferentes. Executar uma suíte numerosa sem relacioná-la à afirmação produz confiança difícil de auditar.

Para estudar o Stoikus, convém separar cálculo determinístico, adaptação ao terminal, persistência, eventos e interação. A primeira camada pode permitir ensaios fora do terminal com dados sintéticos. As seguintes dependem de mais condições do ambiente. Um teste host que reproduz uma fórmula demonstra comportamento daquela reprodução e dos casos escolhidos; ele não comprova automaticamente compilação MQL5, seleção nativa de objetos ou entrega dos eventos da interface. A descrição da evidência deve conservar essa fronteira.

Também é necessário distinguir caracterização e aceitação. Uma caracterização registra o comportamento atual, inclusive limitações; um critério de aceitação exige o resultado previsto pelo contrato. O fato de um teste antigo esperar um resultado não transforma esse resultado em regra normativa. Quando a fonte de autoridade está ausente ou conflitante, o teste pode verificar que o sistema preserva indisponibilidade e motivo, mantendo o cálculo financeiro sem homologação.

## 7.2 Compilar o conjunto exato

MQL5 compila o módulo principal e suas inclusões em um EX5. Um recibo útil identifica fontes, dependências, recursos, versão de MetaEditor, alvo e resultado da compilação. O nome do ZIP ou a versão escrita no cabeçalho não estabelecem a identidade do conteúdo. Depois de uma alteração de cabeçalho, um EX5 anterior pode continuar presente com o mesmo nome; por isso, a relação entre fonte, execução de compilação e hash do binário precisa ser demonstrável. [TRD, sec. 5.1.1, p.PDF 614–615]

A compilação responde a uma pergunta limitada: o compilador aceitou aquela unidade sob aquelas condições? Ela não verifica que uma janela será usável, que a corretora entregará histórico suficiente ou que um identificador corresponde ao estudo que o usuário escolheu. Zero erros e avisos é evidência importante dentro do escopo, mas não equivale à execução completa da ferramenta.

No candidato consultado, `mt5/jpw-alavancagem-atual/README.md` identifica produto 1.23.0, MQL 1.230 e cálculo 1.9.0 e mantém compilação e interação MT5, instalação demo, aceite humano e Windows x64 independente como `NOT_RUN`. O histórico de compilações de outras revisões permanece histórico. Esta pesquisa não produziu EX5 nem executou MetaEditor; seus exemplos são didáticos e têm validação nativa `NOT_RUN`.

## 7.3 O tester simula um ambiente com escolhas próprias

O Strategy Tester permite reproduzir períodos históricos e controlar condições, mas o modo de geração de ticks faz parte do caso. O livro distingue ticks reais, cada tick gerado, OHLC de minuto e preços de abertura. A redução de pontos acelera a execução e modifica quais trajetórias e instantes são visíveis. Em certas situações, a simplificação pode produzir resultados artificialmente bons; escolher o modo rápido não é uma otimização neutra para todo algoritmo. [TRD, sec. 6.5.1, p.PDF 1450–1453]

Mesmo uma estratégia sem `OnTick` pode ser testada: EAs podem trabalhar por timer e outros tratadores. Isso interessa ao Monitor, cuja responsabilidade não é abrir posições. Entretanto, o teste precisa apresentar mudanças e dados que exercitem a observação, a reconciliação e a validade das publicações. Um gráfico de lucro não é um oráculo adequado para um observador não negociador. As asserções devem avaliar identidade, qualidade, completude e efeitos autorizados.

O tempo também exige cautela. No tester, funções relacionadas a tempo local, servidor e GMT assumem relações específicas descritas no livro. Um timer de um segundo pode gerar milhares de chamadas dentro de uma única barra longa, mesmo no modo de preços de abertura. A aceleração do mercado não demonstra a mesma latência de relógio real. `Sleep` avança o tempo simulado de maneira própria e pode permitir acionamento de ordens e stops durante o intervalo. [TRD, sec. 6.5.2, p.PDF 1458–1459]

As áreas de arquivos e globais são as do agente, separadas do terminal comum, salvo o uso explícito das opções pertinentes. Testes que deveriam ser independentes não devem se comunicar por nomes comuns reutilizados. O caso registra qual sandbox foi usada e como fixtures e resultados foram transferidos. O livro também observa que arquivos declarados em `tester_file` precisam existir na compilação para serem enviados posteriormente; sua presença tardia pode não produzir aviso do compilador nem corrigir o executável já formado. [TRD, sec. 6.5, p.PDF 1450; sec. 6.5.12, p.PDF 1506–1507]

## 7.4 Visualização não substitui interação no terminal

O modo visual permite examinar gráfico, indicadores e objetos que não são construídos da mesma maneira em testes sem visualização. No modo de fundo, certas consultas de objetos retornam valores que não sustentam uma conclusão sobre a interface. Além disso, indicadores mostrados no gráfico após o teste podem ser recalculados depois do período testado; a imagem final não é necessariamente o registro dos valores vistos pelo EA em cada instante. [TRD, sec. 6.5.3, p.PDF 1459–1460]

O limite é ainda mais concreto para painéis: o livro registra que eventos interativos de gráfico, objetos, teclado e mouse não são gerados para `OnChartEvent` no tester, mesmo visual. Portanto, uma janela aparecer no tester não prova que seus cliques, arrastes e campos se comportam como no terminal. O plano de validação de Conta e NoCuda deve reservar ensaio no ambiente nativo para essas interações. [TRD, sec. 6.5.19, p.PDF 1561]

Também não se comprova saída de indicador supondo que o tester executa o mesmo encerramento de uma instância anexada. A fonte descreve particularidades de `OnDeinit` e destrutores de indicadores naquele ambiente. Um teste de limpeza de objetos precisa considerar essa diferença e observar a forma real de instalação. [TRD, sec. 5.1.5, p.PDF 628; sec. 6.5.3, p.PDF 1460]

Para o Stoikus, um roteiro nativo útil percorre abrir, minimizar, restaurar, redimensionar e alternar Conta e NoCuda, preservando rascunhos e estudos conforme o contrato. Em seguida, troca período e conta, remove uma instância e verifica as demais. O resultado precisa identificar dimensões do gráfico, escala, entradas e sequência. Uma captura de tela pode complementar a prova, mas não demonstra por si só que a gravação não ocorreu ou que o clique foi recebido pelo objeto pretendido.

## 7.5 Fixtures pequenas e falhas deliberadas

Um bom conjunto de fixtures distingue valores de fronteira e situações semanticamente diferentes. Para uma publicação, existem pelo menos vazio válido, falta de arquivo, versão incompatível, geração incompleta, conta diferente e conjunto íntegro. Para um cursor, existem início, meio, fim e invalidação do contexto. Para coordenação, existem primeiro proprietário, concorrente recusado, propriedade perdida e saída de instância sem aquisição. Não basta chamar todos esses casos de erro.

Os dados devem ser sintéticos e os resultados esperados devem vir do contrato. Um exemplo didático usa quatro registros com identidades A, B, C e D e fatias de dois. A primeira chamada deve produzir progresso, mas não prontidão; a segunda conclui; uma terceira não duplica registros; mudar a identidade entre as duas primeiras invalida a conclusão anterior. O conjunto é pequeno o suficiente para conferência manual e forte o suficiente para revelar bugs de continuação e idempotência.

Injeção de falhas acrescenta pontos que o caminho feliz não visita. Falha de alocação, abertura recusada, erro na confirmação da transação e alteração concorrente precisam produzir estados verificáveis. O oráculo examina os efeitos: original preservado, nenhum sucesso falso, nenhum registro duplicado e motivo adequado. Um teste que apenas procura uma palavra no log pode passar enquanto o banco já foi alterado incorretamente.

Uma transformação determinística admite ainda propriedades além de exemplos fixos. Processar os mesmos itens em uma fatia ou em várias deve produzir resultado equivalente quando o contrato permite; repetir uma reconciliação não deve acrescentar um fato já identificado; indisponibilidade de uma entrada obrigatória não deve virar total financeiro completo. Essas propriedades são propostas de teste, não recibos de execução. A pesquisa não as apresenta como testes nativos realizados.

## 7.6 Depurar e medir a pergunta correta

O tester facilita reproduzir um intervalo, colocar breakpoints e inspecionar o fluxo. O livro distingue depuração em dados reais e históricos e observa que o executável recebe informações e opções próprias para esse trabalho. O binário de depuração ou profiling não deve ser confundido com a compilação normal de distribuição. [TRD, sec. 6.5.18, p.PDF 1560]

Para uma demora no Monitor, meça o ponto em que o trabalho se concentra. Tempo de callback, tempo de consulta SQL, quantidade processada, tempo até publicação e atraso de interação são grandezas diferentes. Uma melhoria no tempo médio pode conservar uma operação indivisível longa. Um orçamento verificado entre itens não interrompe uma chamada interna já em execução. A medição deve apresentar tamanho do histórico, distribuição dos casos e os piores episódios observados, sem prometer um teto não demonstrado.

O profiling aponta linhas e funções custosas, mas o ambiente afeta a conclusão. A fonte registra limitações de profiling visual e recomenda medir operações de gráficos e objetos no contexto pertinente. Também há APIs sem execução no tester, como comunicação externa e notificações; durante otimização, funções de impressão têm restrições. A ausência de mensagem pode ser uma propriedade do ambiente, não sucesso silencioso da funcionalidade. [TRD, sec. 6.5.18–6.5.19, p.PDF 1560–1561]

`OnTester` retorna um critério numérico de otimização e é chamado ao fim da passagem, antes da saída do EA. Sua presença não garante que o usuário selecionou o critério customizado. Maximizar esse número não substitui critérios binários de integridade e segurança. Uma falha obrigatória não pode ser compensada por lucro, velocidade ou boa pontuação visual. [TRD, sec. 6.5.7, p.PDF 1478; REF, OnTester, p.PDF 2122]

## 7.7 Harness, sessões novas e preservação do histórico

O harness histórico integrado em `mt5/jpw-alavancagem-atual/harness/` tem identidade própria. Seu `REPOSITORY_INTEGRATION.md` registra versão 1.0.0 como `CANDIDATE`, piloto R2 com 36 tentativas e resultado global `FAIL`, além de retestes restritos que não substituem a suíte completa. A proposta externa 1.0.1 continua `CANDIDATE / NOT_ADOPTED`. Este manual não ativa, corrige ou promove esse protocolo.

O contrato `harness/contracts/ENG-AC01-12.json` exige três sessões agentes novas por caso e distingue esses ensaios de três processos locais ou três respostas na mesma sessão. Ele também reconhece que contexto herdado não demonstra cegamento ou independência. A pesquisa respeita essa distinção: repetir um script pode testar estabilidade mecânica, mas não satisfaz por si só o desenho de um piloto com sessões segregadas.

Um novo harness de pesquisa permanece candidato e deve informar contrato, fixtures, referências e critérios congelados antes de executar. Cada tentativa iniciada recebe identidade e conserva entradas, saídas, erros e interrupções. Uma tentativa de ambiente inválida pode requerer repetição, porém não deve apagar evidência independente de violação já demonstrada. A classificação precisa separar execução, resultado do critério e estado do domínio; reconhecer corretamente uma lacuna pode ser comportamento aprovado enquanto o cálculo e o nativo permanecem `NOT_RUN` ou bloqueados.

O registro mínimo de uma tentativa relaciona candidato, hash dos arquivos pertinentes, caso, sessão, ambiente, comando ou ação, resultado observado e limite da conclusão. A revisão independente deve receber evidências suficientes para discordar do executor. Uma narrativa de sucesso escrita pelo mesmo agente não substitui logs nem um oráculo. Se a infraestrutura não permite sessões novas ou execução MT5, o piloto correspondente fica sem execução, com a razão registrada e sem preenchimento de resultados plausíveis.

## 7.8 Fechar uma verificação sem ampliar sua conclusão

Ao encerrar, o pesquisador identifica o que executou agora, o que apenas consultou e o que veio de recibo histórico. Leitura de fonte sustenta explicação de fluxo; compilação sustenta aceitação pelo compilador; teste sustenta os comportamentos observados naquele ambiente. Instalação e aceite humano exigem seus próprios registros. A apresentação do candidato não faz essas etapas acontecerem.

Uma entrega verificável oferece o material necessário para repetir ou contestar suas conclusões. Isso inclui lacunas: callback não exercitado, modo visual ausente, banco real não tocado, executável não produzido ou cenário sem sessão válida. Declarar essas diferenças não enfraquece uma boa evidência; delimita precisamente sua utilidade. Para este manual, pesquisa documental e exemplos originais estão entregues nos capítulos, enquanto compilação e execução nativas dos exemplos e do candidato continuam `NOT_RUN`.

Uma matriz curta pode relacionar cada alegação ao seu melhor observável. Para ausência de duplicação, compare identidades e contagens antes e depois de repetir a entrada. Para preservação, compare o conteúdo anterior e sua releitura depois da falha. Para interação, registre a sequência de ações e o efeito esperado no mesmo ambiente. Para ausência de negociação do Monitor, combine inspeção das dependências pertinentes com observação delimitada dos efeitos, sem transformar um período sem ordens em prova universal de todos os caminhos possíveis.

O critério para repetir a verificação é uma mudança que afete sua validade: outro conjunto de fontes, fixture corrigida, dependência alterada ou nova hipótese de falha. Repetir continuamente um teste já aprovado sem mudar a pergunta acrescenta pouco. Por outro lado, reutilizar o recibo depois de alterar o componente correspondente exige justificar por que a evidência ainda se aplica. A relação entre mudança e prova deve permanecer explícita.
