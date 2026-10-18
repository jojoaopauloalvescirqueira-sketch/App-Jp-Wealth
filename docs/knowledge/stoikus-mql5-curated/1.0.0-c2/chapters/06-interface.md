# 6. Interface e recursos gráficos

## 6.1 A interface participa da correção

Uma interface financeira correta precisa conservar o significado das leituras ao distribuí-las no gráfico. Um valor íntegro no núcleo pode se tornar ambíguo quando sua unidade desaparece, quando o estado ocupa outra região visual ou quando uma descrição truncada esconde o conjunto a que o valor pertence. O problema de alinhamento não se limita à aparência. Ele interfere na associação entre título, valor, origem e ação. A composição deve ajudar o usuário a reconhecer essas relações de forma consistente.

O Stoikus coloca componentes analíticos sobre um gráfico que continua sendo usado para observar preços e manipular estudos. A área disponível é disputada com candles, escalas, objetos e controles do terminal. Um painel que exige atenção permanente para informações raramente consultadas consome espaço de trabalho. O desenho atual procura responder com resumo Compacto, detalhes sob demanda e controles de movimento e recolhimento. Essas decisões são escolhas do produto; os livros oferecem mecanismos para implementá-las e avaliar seus limites.

A revisão de interface deve começar por contratos de apresentação: quais informações permanecem visíveis, quais podem ir aos detalhes e quais não podem ser truncadas. Para uma leitura monetária, valor, unidade e escopo têm prioridade. Uma explicação extensa pode ser distribuída em linhas e páginas. Se o espaço mínimo não comporta a leitura, uma ação de acesso identificada é mais honesta que um número cortado. O usuário precisa perceber que existe conteúdo a consultar e como restaurá-lo.

## 6.2 Objetos de gráfico e recursos têm responsabilidades diferentes

O catálogo oferece objetos de gráfico, propriedades e recursos de imagem. Um objeto fornece identidade, coordenadas e propriedades de interação. Um recurso fornece o conteúdo gráfico associado. Apagar um objeto não deve ser presumido como liberação automática de toda memória gerenciada pela aplicação; liberar um recurso não significa que todos os objetos que o referenciam foram removidos. O ciclo de vida precisa enumerar o que foi adquirido e a quem pertence. [REF, Object Functions, p.PDF 2895–2967; ResourceCreate, p.PDF 1154–1157.]

O código deve conservar nomes e ownership suficientes para executar a limpeza restrita. Um prefixo genérico compartilhado por instâncias pode facilitar a criação e produzir uma remoção indevida na desinicialização. A falha de inicialização é particularmente importante: o programa pode receber a rotina de encerramento sem ter adquirido todos os recursos planejados. Uma lista de aquisições confirmadas ajuda a distinguir intenção de propriedade efetiva.

A composição pode usar objetos nativos para controles e recursos bitmap para fundos ou texto desenhado. Essa combinação exige que geometria, camada e recepção de eventos sejam ensaiadas juntas. Uma imagem visualmente correta pode ficar atrás de outro objeto que intercepta o clique. Um botão pode estar ativo enquanto a figura que o identifica não foi atualizada. O teste de pixels e o teste de roteamento respondem a perguntas complementares.

## 6.3 Enfileiramento não equivale a renderização concluída

`ObjectSetInteger` informa que um comando de alteração foi enviado à fila do gráfico. Esse retorno não comprova que o usuário já viu o resultado final. A documentação descreve o comportamento assíncrono dessas operações e os custos de consultas que aguardam a fila. A aplicação deve evitar transformar cada alteração de propriedade numa sequência de verificações síncronas caras. [REF, ObjectSetInteger, p.PDF 2935–2937.]

`ChartRedraw` solicita redesenho, mas o fluxo de eventos e a categoria do programa continuam relevantes. Um teste host que registra a chamada comprova que a aplicação pediu o redesenho; não comprova composição no Windows, ordem visual ou entrega de eventos. Essa fronteira deve aparecer no relatório. É possível testar o cálculo dos retângulos no host e ainda precisar de capturas nativas para aceitar a posição real.

Uma estratégia de atualização deve reduzir trabalho redundante. Se o estado visual não mudou, recriar todos os objetos e recursos a cada timer desperdiça processamento e pode agravar cintilação e latência. Cache de geometria ou de texto é útil quando suas entradas incluem todos os fatores relevantes. Fonte, DPI, tema, conteúdo e largura são candidatos óbvios. Uma cache que ignora a troca de fonte pode devolver uma medida antiga com aparência de resultado válido.

## 6.4 Transparência exige um formato que a represente

No formato ARGB, o canal alfa controla a contribuição do pixel. `ColorToARGB` converte uma cor para essa representação e admite alfa entre zero e 255. A relação documentada entre transparência percentual e alfa permite converter uma preferência de apresentação em valor de rasterização. É necessário definir o arredondamento e testar extremos; alfa zero e alfa 255 têm significados diferentes e ambos precisam funcionar. [REF, ColorToARGB, p.PDF 1892–1893.]

Uma preferência de trinta por cento de transparência corresponde aproximadamente a alfa 179 quando se arredonda 255 multiplicado por 0,70. Essa relação não significa que todos os controles devam receber o mesmo alfa. O requisito do Stoikus aplica a transparência somente ao fundo do resumo. Textos, números, estados e ações permanecem opacos para conservar legibilidade e previsibilidade de interação. Janelas de consulta sólidas têm um papel visual distinto.

`ResourceCreate` permite construir imagem a partir de pixels. O modo `COLOR_FORMAT_ARGB_NORMALIZE` deixa o terminal tratar os componentes; `COLOR_FORMAT_ARGB_RAW` exige dados corretamente preparados no formato pré-multiplicado. Misturar esses contratos pode produzir bordas e cores inesperadas. A escolha deve corresponder à forma como o buffer foi produzido, em vez de decorrer da aparência de um único screenshot. [REF, ResourceCreate, p.PDF 1154–1157.]

A transparência também não define a área de clique. Um fundo totalmente transparente ainda pode ocupar uma região lógica reservada e conter controles opacos. O lançador NoCuda precisa receber a geometria efetivamente ocupada, independentemente do alfa. Um teste deve mover o resumo, alterar sua largura, recolhê-lo e usar transparência total, conferindo a reserva após cada ação. Derivar ocupação somente da existência de pixels visíveis perde esse contrato.

## 6.5 Falhas gráficas precisam de uma saída utilizável

Uma falha ao alocar pixels ou criar um recurso não deve deixar o usuário sem acesso às informações. O caminho alternativo precisa ter identificação visível, geometria válida e ações funcionais. Mostrar um retângulo opaco sem os textos necessários não é uma recuperação suficiente. Também não basta declarar sucesso porque a função de renderização retornou; o fallback deve manter o acesso aos valores e seus detalhes.

O erro original deve continuar disponível no diagnóstico. Uma alternativa bem-sucedida não apaga a razão pela qual a apresentação preferida falhou. O estado pode informar que está utilizando modo simplificado e oferecer orientação proporcional ao problema. A cor não deve ser a única portadora dessa informação, pois temas, contraste e condições visuais variam.

O teste de fallback deve injetar falha em uma fronteira identificada: alocação, criação, atualização ou medição. Os limites do simulador precisam ser descritos. Por exemplo, uma bancada pode recusar `ResourceCreate` de forma determinística, mas não reproduzir pressão real de memória do terminal. O teste ainda é útil para verificar o caminho de controle e a limpeza; a capacidade nativa conserva sua prova própria.

## 6.6 Tipografia e DPI exigem um sistema de unidades

As medidas da interface devem declarar se são lógicas, físicas, pontos tipográficos ou décimos de ponto. A documentação de `TextSetFont` distingue tamanhos positivos e negativos: a forma negativa expressa décimos de ponto e considera configurações de escala do sistema, enquanto a positiva usa outra relação com a medida física. A mesma função não pode ser tratada como uma simples cópia de uma API de canvas de outro ambiente. [REF, TextSetFont, p.PDF 2952–2958.]

Uma aplicação deve escolher onde ocorre a conversão de DPI e aplicá-la uma vez. Multiplicar coordenadas e depois multiplicar novamente a fonte que já foi interpretada com a escala do sistema pode produzir um painel muito maior que o previsto. O erro inverso deixa a geometria dimensionada para um texto que não cresce junto. Ensaios em 100, 125, 150 e 200 por cento ajudam a revelar inconsistências, mas o resultado depende também das fontes instaladas.

`TextGetSize` mede largura e altura nas configurações correntes de fonte. Medir com uma fonte e pintar com outra invalida o cálculo. O fluxo precisa selecionar a configuração, medir, decidir quebra ou paginação e usar a mesma configuração para desenhar. Se a seleção da fonte falhar, o fallback precisa ser explícito e suas medidas devem corresponder à fonte efetivamente usada. [REF, TextGetSize, p.PDF 2963–2967.]

A medição real importa porque contagem de caracteres não equivale a largura. Um identificador de instrumento, uma sequência de dígitos e uma frase com caracteres estreitos têm extensões diferentes. A string também não deve ser tratada como bytes UTF-8 num simulador que pretende reproduzir índices MQL5. Diferenças de codificação podem fazer uma bancada truncar caracteres de forma distinta do produto, encobrindo ou inventando defeitos.

## 6.7 Grade e hierarquia de informação

Uma grade compartilhada dá origem comum aos títulos, valores, explicações e ações. A margem deve ser calculada uma vez e reaproveitada, em vez de ser reconstruída com números próximos em cada cartão. A altura da linha precisa considerar a fonte configurada e o conteúdo que pode aparecer. A etiqueta de estado deve acompanhar seu texto; ocupar toda a largura sem necessidade aumenta o peso visual e reduz a distinção entre estado e área de entrada.

Na Conta, seis seções podem ser distribuídas em uma linha quando as medidas permitem, em duas linhas equilibradas ou por seletor compacto. Essa adaptação depende das larguras medidas, não somente de uma constante de viewport. Um título traduzido ou uma fonte configurada pode mudar o arranjo adequado. A paginação precisa conservar uma linha própria e não disputar espaço com ações como aplicar, cancelar ou preparar mensagem.

Os valores financeiros merecem uma política diferente da descrição auxiliar. Um número parcialmente visível pode mudar a leitura de uma ordem de grandeza. A solução deve reorganizar, paginar ou oferecer acesso identificado ao detalhe completo. Reduzir silenciosamente a fonte para acomodar qualquer número torna a interface imprevisível. A própria representação da indisponibilidade deve conservar o motivo e a próxima ação, sobretudo quando uma estimativa e uma leitura atual ocupam posições semelhantes.

A marca aprovada fornece identidade, mas não deve dominar a área funcional. Sua proporção precisa ser preservada ao centralizar verticalmente logo, identificação da janela e controles. O tamanho do cabeçalho deve decorrer de seus elementos, incluindo alvos de interação, e não de uma altura escolhida para esconder desalinhamentos do corpo. Esses critérios permitem julgar a composição por relações observáveis, em lugar de aprovação estética genérica.

## 6.8 Movimento e redimensionamento são pequenas transações

Um gesto possui início, atualização, conclusão e cancelamento. No início, a aplicação captura o estado necessário para restaurar a interação do gráfico. Durante o movimento, calcula uma geometria provisória. Na conclusão, valida limites e, se a ação foi efetivamente concluída, grava a preferência visual. No cancelamento, restaura a geometria e as configurações temporárias. Esse ciclo deve existir mesmo que o usuário interrompa o gesto com Esc ou que outro evento altere o contexto.

A rolagem do gráfico oferece um exemplo importante. Desativá-la durante o arraste pode ser adequado para evitar que gráfico e janela se movam juntos. Restaurar sempre para verdadeiro é incorreto se a preferência anterior era falsa. O gesto precisa conservar o valor original. Essa exigência se aplica às rotas de erro, à perda de ownership e ao encerramento, além do caminho normal de soltar o mouse.

Um redimensionamento por borda deve preservar a borda oposta conforme o contrato adotado e respeitar a área utilizável. A largura mínima não pode permitir uma janela geometricamente válida mas inutilizável para seus controles. Ao carregar uma configuração antiga pequena demais para a nova apresentação, a recuperação visual deve ser possível sem gravar automaticamente uma migração. O usuário conclui uma ação explícita antes que a nova preferência substitua a anterior.

## 6.9 Minimizar não é aplicar nem cancelar

O resumo do gráfico e a janela completa possuem estados de visibilidade independentes. Recolher o resumo para um botão Conta não precisa fechar uma consulta aberta. Minimizar uma consulta deve preservar seu rascunho em memória e os desenhos associados, enquanto o Monitor e a auditoria mantêm seus fluxos próprios. Fechar ou cancelar um diálogo pode ter outro significado e deve permanecer identificado.

Essa separação exige cuidado com funções de limpeza reaproveitadas. Uma rotina de fechar pode liberar foco, apagar objetos transitórios, descartar rascunhos ou cancelar uma consulta. Chamá-la para minimizar apenas porque ela oculta a janela pode introduzir uma alteração de comportamento. A implementação precisa definir qual parte do estado é visual, qual é sessão de edição e qual pertence ao processo de fundo.

O teste deve criar um rascunho que difere da preferência salva, minimizar, restaurar e conferir ambos os valores. Também deve iniciar uma auditoria, minimizar a consulta e observar sua continuidade dentro dos limites da bancada. Reinício do terminal é outro cenário: preservação em memória não significa persistência de rascunhos entre processos. O manual e a interface devem evitar atribuir ao minimizar uma garantia que o código não oferece.

## 6.10 Preferências visuais e avaliação da interface

Preferências visuais versionadas permitem acrescentar posição, tamanho, transparência e recolhimento sem reutilizar campos com significados antigos. O carregamento deve reconhecer versão, validar tipos e distinguir ausência de incompatibilidade. Um arquivo desconhecido ou alterado por outro proprietário não deve ser sobrescrito apenas para restaurar uma aparência padrão. A política de escrita precisa considerar staleness e resultado da persistência.

Uma pintura é leitura do estado; não deve salvar preferências como efeito colateral. Essa restrição torna reabrir, trocar tema e atualizar dados operações mais previsíveis. A escrita pertence a uma ação explícita concluída. Um erro na gravação deve conservar a possibilidade de diagnóstico e não transformar o estado exibido numa alegação de preferência duravelmente salva.

A avaliação combina três provas. A primeira verifica regras e geometria em dados sintéticos, incluindo fontes longas, valores grandes, falhas e gráficos pequenos. A segunda usa o terminal para observar rasterização, DPI, camadas, teclado e mouse. A terceira pede ao usuário que localize ações, interprete escopos e recupere janelas sem orientação do implementador. O resultado de uma dessas provas não substitui as demais.

As propostas decorrentes são um catálogo compartilhado de dimensões e unidades; contratos de interação com cancelamento verificável; observação explícita dos fallbacks; e uma matriz nativa de cenários Conta–NoCuda. O objetivo é tornar a interface uma representação fiel dos contratos do programa. As alterações produtivas correspondentes conservam seu processo de implementação e aceite, separado da elaboração deste manual.
