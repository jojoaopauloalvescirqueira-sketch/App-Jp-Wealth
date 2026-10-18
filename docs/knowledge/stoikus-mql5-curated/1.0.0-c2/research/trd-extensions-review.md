# TRD — recursos, símbolos próprios e calendário: revisão semântica

Leitor: `trd_extensions_research`. Fonte efetivamente recebida e lida: corpo textual completo de [TRD, Parte 7, p. PDF 1562–1774], 213 páginas físicas únicas. O início da Parte 7, recursos e símbolos próprios foram lidos por inteiro; calendário inclui sua conclusão na p.1774. Criptografia foi apenas introduzida nessa página. Nenhuma reivindicação sobre p.1775–2047. O índice possui intervalos sobrepostos e títulos que começam antes da transição real; a contagem usa páginas únicas, não a soma das seções. Lotes iniciais1562–1580 tiveram truncamento da resposta; a faixa omitida1567–1572 foi recebida novamente, completa. Todos os demais lotes foram recebidos sem truncamento de ferramenta.

A evidência é leitura do texto extraído, inclusive exemplos, comentários e resultados publicados no livro. Não houve inspeção visual das figuras, execução MQL, compilação EX5 ou reprodução dos resultados do autor: **NOT_RUN**. Alguns exemplos têm linhas visualmente cortadas na edição/extração (p.ex.1642,1657,1741); não se deve copiar essas listagens como arquivos compiláveis. O texto remete a fontes anexas que não foram abertas por este leitor. Extração não é análise; o inventário com hashes registra a identidade do texto efetivamente lido, não prova execução.

## Limites da aplicação

**Contrato da plataforma** abaixo significa comportamento descrito no livro fornecido, nessa edição; não é uma verificação atual do terminal instalado. **Observado no código Stoikus:** este leitor não inspecionou fontes do produto e não afirma presença ou ausência de APIs. O BRIEF informa Monitor orientado a eventos e sem negociação, core1.23.0/MQL1.230/calc1.9.0 e Supervisor opcional sem autorização de armar; esses dados são contexto recebido, não achado de código deste lote. **Regra JPW:** nenhuma política normativa de calendário, parâmetros de margem, símbolos sintéticos, negociação ou segurança é derivável dessas páginas. **Proposta** significa possibilidade futura, jamais edição autorizada ou funcionalidade já instalada. Nenhum arquivo produtivo, kit ou piloto foi alterado.

## 7.1 — recursos (PDF1562–1624, transição)

A abertura (1562) distingue arquivos incorporados na compilação, dados de execução e capacidades de integração; o próprio livro declara OpenCL e DirectX fora do escopo aprofundado. Isso impede usar uma menção introdutória como estudo integral dessas tecnologias. Recursos podem simplificar distribuição, porém a conveniência de um EX5 autossuficiente não demonstra fidelidade, compatibilidade nem política de atualização dos dados incorporados.

### 7.1.1 — diretiva resource (1563–1564)

O caminho inicial com barra invertida parte de MQL5; sem ela, a referência é relativa ao arquivo de fonte que contém a diretiva, inclusive quando esse arquivo é MQH. Strings usam barras invertidas duplicadas; caminhos com subida e unidade são proibidos. O livro estabelece63 caracteres para caminho literal,128MB para recurso estático e compressão de incorporação. A referência em execução usa `::` e remove a barra inicial. BMP/WAV atendem à forma simples, enquanto outras modalidades são tratadas adiante. Aplicação conceitual Stoikus: qualquer futura incorporação de ícones ou modelos deve registrar o hash e a versão do insumo no momento da compilação, porque mudar o arquivo externo depois não muda o EX5. Isso é proposta de rastreabilidade, não exigência normativa JPW. Experimento futuro de distribuição sem arquivo auxiliar: NOT_RUN.

### 7.1.2 — compartilhamento entre programas (1564–1565)

Recursos são endereçados com qualificação do EX5 proprietário e nome interno; o proprietário não precisa estar executando para permitir leitura dos recursos incorporados. Caminho absoluto aqui significa relativo à raiz MQL5, e caminho curto depende do diretório do consumidor. Recursos dinâmicos permitem comunicação em memória entre programas. Conhecimento aplicável: nomes e resolução de caminhos pertencem ao contrato de interface. Proposta futura: prefixo por componente, versão do protocolo e instância, em vez de tratar disponibilidade pelo nome como autenticidade ou integridade. Não há evidência de uso pelo Stoikus.

### 7.1.3 — variáveis de recurso (1565–1569)

A forma `as` produz variáveis constantes; imagens podem ser arrays1D ou2D com mesma memória, mas indexação diferente. Texto é convertido em Unicode com reconhecimento de BOM/encoding. Pixel uint ARGB usa ordem diferente do tipo color; conversão explícita evita cores trocadas. Recursos vinculados a variável deixam de ser acessíveis pelo nome `::` e não são compartilháveis externamente. O exemplo BmpOwner/BmpUser comprova a distinção na narrativa do livro: o segundo bitmap dá objeto vazio/vermelho quando acessado externamente. Variável não utilizada pode ser removida pelo compilador, com ressalva para imagens. Aplicação conceitual: selecionar representação conforme finalidade; não prometer acesso compartilhado de uma variável incorporada. NOT_RUN para BOM, transparência e visibilidade entre EX5.

### 7.1.4 — indicadores incorporados (1569–1575)

Um EX5 de indicador pode ser incorporado e passado a iCustom. O caso especial é indicador que cria cópia de si: somente o nome simples falha quando o código está dentro de outro EX5. O exemplo primeiro falha4802 e depois usa MQL_PROGRAM_PATH, extraindo a parte MQL5 e preservando a qualificação de recurso. Há condição explícita que impede reprodução infinita; a descarga de cópias não é imediata, de modo que reinícios próximos podem reutilizar instâncias. DeltaPrice ilustra diferenciação de séries por cópias recursivas finitas, não estratégia financeira aprovada. Proposta futura: ensaio de empacotamento em terminal limpo, criação/erro/liberação de handles e reinício depois da descarga. Sem aplicação imediata à negociação do Monitor. Todos esses ensaios NOT_RUN.

### 7.1.5 — ResourceCreate (1576–1580)

Uma sobrecarga carrega arquivo/recurso; outra recebe pixels, dimensões, offsets, stride e modo de cor. O prefixo `::` é opcional na criação, não em todas as operações posteriores. Nomes longos, tipos não suportados, duplicação estático/dinâmico e ausência têm códigos próprios. A segunda forma atualiza recurso próprio de mesmo nome em vez de sempre recriar. Nomes por ChartID evitam colisão entre instâncias. ARGB_NORMALIZE pré-multiplica canais RGB por alpha; RAW não o faz, XRGB ignora alpha. Para dados arbitrários, XRGB evita transformação destrutiva. O limite dinâmico descrito é INT_MAX bytes, diferente de128MB estáticos. Proposta Stoikus de baixo acoplamento: gestão explícita de propriedade, limites de alocação e modo de cor em eventual painel. Nenhuma otimização mensurada; NOT_RUN.

### 7.1.6 — ResourceFree (1581)

O recurso dinâmico permanece até fechar o terminal se não for liberado. Só o proprietário pode liberá-lo; a operação exige nome com `::`. Objetos existentes podem conservar a imagem após liberação, enquanto novos objetos já não a encontram. Portanto imagem visível não prova recurso ainda disponível nem prova ausência de vazamento. Aplicação conceitual imediata à revisão: ciclos de vida de objeto e recurso são distintos. Proposta futura de inspeção de memória em reinicializações repetidas; NOT_RUN.

### 7.1.7 — ResourceReadImage e Reservoir (1581–1592)

A leitura serve a imagem e dados arbitrários; buffers insuficientes podem falhar5052. O exemplo de três execuções separa criação dos recursos, criação do objeto e limpeza. Reservoir serializa tipos simples em bytes, depois uint, grava tamanho antes de cada bloco e usa strings UTF8 separadamente. Objetos e arrays dinâmicos como valores internos não são serializáveis por simples cópia da representação. O próprio código contém TODO de overflow em tamanho; verificar apenas divisibilidade por sizeof não equivale a validar o tipo ou a integridade do protocolo. O texto propõe passar o nome do recurso em sparam para contornar o tamanho de eventos customizados. Proposta futura: protocolo versionado com comprimento máximo, tipo, sequência, produtor e validação de limites antes de leitura. Não promover esse armazenamento volátil a banco durável JPW. NOT_RUN para roundtrip, buffer truncado, concorrência e recuperação.

### 7.1.8 — ResourceSave e rasterização (1592–1603)

ResourceSave exporta imagem BMP em MQL5/Files, cria diretórios intermediários e sobrescreve destino existente. Não é exportador geral de dados de recursos. A interface Drawing desacopla formas de backend; MyDrawing possui canvas, objetos, recursos e destrutor, desenha pixels/linhas/retângulos e atualiza recurso seguido de ChartRedraw. A demonstração compara sobreposição simples, complemento, XOR, soma e OR, sem torná-los equivalentes em significado visual. Conhecimento útil para um futuro painel: estado visual é derivado; não substituir valores numéricos auditáveis por pixels. As fórmulas demonstrativas de figuras e acesso linear não foram auditadas como biblioteca segura. Sem aplicação imediata ao cálculo Stoikus. NOT_RUN para exportação e diferença visual.

### 7.1.9 — fontes e texto (1603–1616)

TextSetFont seleciona fonte Windows ou TTF incorporada; tamanho positivo é pixel e negativo é décimo de ponto. Orientação é décimo de grau. Uma configuração afeta TextOut subsequente até mudança. TextGetSize mede texto horizontal mesmo quando haverá rotação, cabendo ao programa calcular retângulo final. TextOut opera sobre buffer e exige republicação com ResourceCreate; âncora não é alinhamento. O exemplo alterna dimensões em90 graus e outros usam âncoras e ângulos aleatórios. O editor SimpleDrawing mostra seleção, arraste, Ctrl para dimensão e nomes ChartID. Proposta futura de UI: fontes/acentos/DPI e clipping precisam ensaio visual nativo; não há evidência desses ensaios. Rotacionar rótulos não tem aplicação operacional imediata. NOT_RUN.

### 7.1.10 — perfil de volume por barra (1616–1624)

DeltaVolumeProfile é indicador sem buffers, acionado por clique: converte XY em tempo/preço, lê ticks do intervalo fechado pela última milissegunda anterior à próxima barra e desenha OBJ_BITMAP ancorado em preço/tempo. Níveis são bins de pixels, logo sua agregação depende da escala. Volume real usa flags BUY/SELL; fallback por movimento Bid/Ask é estimativa, não fluxo verdadeiro. O exemplo tenta novamente até5 vezes para histórico indisponível e redesenha quando muda o gráfico. O destrutor contém TODO de limpeza de recursos. Divisões pelo range e máximo e índices merecem tratamento de barra plana/ausência de volume antes de reutilização; isto é observação da listagem do livro, não bug confirmado Stoikus. Proposta futura somente analítica; nenhum sinal ou filtro JPW é autorizado por uma visualização. NOT_RUN.

## 7.2 — símbolos próprios (1624–1689, conclusão)

Símbolos locais servem a séries sintéticas e ensaios, mas não existem no servidor da corretora. Representar Renko, range ou volume em M1 impõe tempo artificial. Esse limite não se resolve escolhendo um nome de símbolo; a separação entre relógio do dado, sinal e execução é central. Não há autorização para incorporar um desses geradores no Monitor.

### 7.2.1 — criação e exclusão (1625–1628)

Nome é único na hierarquia inteira, limitado31 caracteres; path tem127 incluindo prefixo, separadores e nome. Origin transfere propriedades, não barras/ticks, não seleciona automaticamente no Market Watch e pode deixar defaults quando inválido. SYMBOL_PATH inclui o nome original: copiá-lo sem remover o último elemento cria grupo adicional. Exclusão exige ausência de gráficos e seleção, inclusive implícita; histórico pode demorar a desaparecer. Proposta futura: nomes descartáveis por sessão e limpeza verificável em ambiente de pesquisa. Não executar exclusão como rotina de produto. NOT_RUN.

### 7.2.2 — propriedades (1628–1629)

CustomSymbolSetInteger/Double/String diferem por tipo; campos somente leitura e valores inválidos possuem erros próprios. Alterar modo de gráfico, dígitos, point, tick size/value ou fórmula pode apagar histórico minuto e tick. Propriedades têm dependências e ordem: digits influencia point; Forex default deduz moedas a partir do nome; mudar modo de cálculo antes de moedas evita pseudo-códigos. Aplicação conceitual: copiar especificação exige comparação final campo a campo e nova validação do histórico, não confiar apenas no sucesso de criação. Não redefinir condições de corretora como regra JPW. NOT_RUN.

### 7.2.3 — margem (1629–1630)

CustomSymbolSetMarginRate configura taxa inicial e manutenção por tipo/direção, combinadas com modo de cálculo e propriedades de margem. Emular servidor indisponível é proposta de ambiente, não equivalência comprovada com a corretora. Futuro teste de risco exigiria manifesto da especificação e cálculos comparados com referências nativas. Regra JPW de risco permanece externa ao livro. NOT_RUN.

### 7.2.4 — sessões (1630)

Sessões começam no índice0 e só podem ser adicionadas sequencialmente. Horários em segundos admitem atravessar meia-noite até dois dias; from deve anteceder to. Zeros removem sessão e renumeram as seguintes. Negociação deve caber nas sessões de cotação. Proposta futura: casos fronteira à meia-noite e timezone; não adotar janela operacional inferida desses exemplos. NOT_RUN.

### 7.2.5 — barras (1630–1639)

Update faz upsert por timestamp, conservando barras omitidas; Replace apaga o intervalo inclusivo e insere apenas dados do intervalo. Ambos recebem M1 válido, sem segundos, e os períodos superiores são derivados. Delete recebe intervalo inclusivo. O exemplo de random walk/ruído fixa seed para reprodutibilidade, recria símbolo e limpa explicitamente histórico para não misturar dados antigos após exclusão atrasada. CopyRates sofre limite de barras do terminal. Dados de barras sem ticks reais mudam a modelagem do tester. Proposta futura: datasets sintéticos com seed, origem, intervalo e condições preservados, sem converter resultados de ruído em aprovação financeira. NOT_RUN.

### 7.2.6 — ticks, replay e negociação virtual (1639–1666)

CustomTicksAdd exige seleção Market Watch e ordem temporal não decrescente; alimenta eventos, enquanto Replace grava direto no banco. Mais de256 ticks em Add muda o caminho de processamento: apenas os128 finais passam pelo Market Watch. time_msc prevalece sobre time; ambos zero usam hora corrente. volume_real prevalece e flags de direção BUY/SELL não são acrescentadas no histórico próprio. Replace é inclusivo em milissegundos; desordem pode retornar-1 com erro0 depois de dias anteriores já aplicados, sem atomicidade integral. Deletar ticks remove barras correspondentes, mas deletar barras não remove ticks.

O primeiro experimento filtra ticks por sequências, spread/flutter ou fractais. Resultados de tempo/memória/profit são do autor e dependem de estratégia, instrumento e histórico; não comprovam aceleração segura do Stoikus. Fractais usam vizinhos futuros dentro de lote: sua utilização como transformação offline não pode ser confundida com um filtro causal online. Redução pode alterar disparos, número de trades e drawdown, mesmo preservando aparência da curva.

O segundo exemplo CustomTester reproduz histórico por timer e CustomTicksAdd, permitindo interação normal de gráficos. Ele verifica tick size/value após criação e pode corrigi-los. KeyboardSpy transfere teclas do gráfico dependente; o livro descreve limitações de leitura de modificadores em indicadores criados por código. CustomTrade substitui funções via macros, armazena ordens/deals/posições em arrays e usa hora do símbolo virtual em vez de TimeCurrent. O autor declara cálculos simplificados, modos ausentes e validação incompleta; swaps e comissões não entram no relatório demonstrado. Logo não é uma prova de execução, nem substituto completo do Strategy Tester, nem motor de risco JPW. Proposta futura de replay isolado para ergonomia visual, com rótulo de simulação e relógio explícito. NOT_RUN para todos os três grupos de ensaios; nenhum replay foi instalado.

### 7.2.7 — livro de ofertas (1666–1672)

CustomBookAdd substitui o snapshot inteiro, requer preços/volumes positivos e respeita profundidade configurada. Consumidores assinam MarketBookAdd e leem MarketBookGet. Atualizar book não atualiza Bid/Ask: ticks precisam de outra operação. O livro relata assinatura implícita/lock que pode impedir ocultar/deletar símbolo até MarketBookRelease. PseudoMarketBook inventa níveis a partir de movimentos de cotações e hipóteses sobre realização de lucro; é dado sintético, não liquidez observada. Proposta futura: fixture formal para testes de parsing/eventos, sempre marcada como sintética; sem aplicação atual como fonte de pressão de mercado. NOT_RUN.

### 7.2.8 — sinal, símbolo real e relógio (1672–1689)

EqualVolumeBars implementa ticks/volume real/range com barras M1 artificiais. Dados históricos são processados em lotes; online há ticks para gerar eventos e ajuste do contador da barra. Barras rápidas podem avançar ao futuro, barras lentas comprimem vários minutos e timestamp original se perde. O exemplo não gera ticks históricos na versão apresentada, portanto selecionar modo de ticks não restaura informação ausente. O autor propõe tanto adaptar chamadas de negociação com CustomOrder/macro quanto deixar EA no símbolo real e obter indicadores do símbolo de sinal. Origin não é vínculo operacional automático; SYMBOL_BASIS não garante convenção compartilhada.

A adaptação de request pode trocar também Bid/Ask no tester para conter dessincronização; isso é artifício, não prova de correspondência histórica. Renko/PAF de reversão podem embutir informação futura no open, e mesmo usar indicadores de barras fechadas não elimina o preço de execução irreal da barra0. O livro recomenda validar em conjunto com execução do símbolo real. Sua heurística de tomar a alternativa menos lucrativa não substitui prova causal e econômica. Proposta futura: separar explicitamente event_time, synthetic_bar_time, signal_time e execution_time, mantendo ticks originais e comparação contra referência causal. Para Stoikus, o valor imediato é critério de revisão de evidência; nenhuma negociação foi adicionada. NOT_RUN.

## 7.3 — calendário econômico (1689–1774)

A API usa hora do servidor com timezone/DST atuais, não simplesmente UTC. Não funciona diretamente no tester (4014, conforme livro). O recurso operacionalmente mais relevante é conhecer janelas de risco e informar o operador; o exemplo que negocia notícias é material didático e não nova função do Monitor.

### 7.3.1 — entidades e ausências (1689–1696)

País, tipo de evento e ocorrência são três entidades relacionadas por IDs distintos. Ocorrência contém hora, período de referência, revisão, actual/previous/revised/forecast e impacto. Ausência é LONG_MIN; valores existentes estão em milionésimos. Get converte para double ou NaN, mas unidade, multiplier e digits do tipo continuam relevantes. Não confundir período econômico com momento de publicação. Impacto é interpretação potencial após comparação, podendo ser ambígua e não garantir reação do preço. change_id cresce com alterações, mas não fornece horário nem conteúdo histórico das alterações. Proposta futura: schema com ID de entidade, unidade, ausência e proveniência, sem substituir desconhecido por zero. NOT_RUN.

### 7.3.2 — países (1696–1698)

CalendarCountries preenche array; buffers fixos insuficientes podem produzir dados parciais e5400, timeout5401. CalendarCountryById retorna false/no-data se ID não existe. WW/ALL representa global e EU/EUR abrange relações que não equivalem a um país único. Contagens do exemplo são snapshot do livro, não inventário atual. Proposta: evitar listas congeladas de países como requisito de cobertura; testar ausência e erro separadamente. NOT_RUN.

### 7.3.3 — tipos por país/moeda (1698–1702)

CalendarEventByCountry/ByCurrency consultam metadados, não ocorrências. Vazio desliga filtro; moeda inválida pode retornar0 sem erro. Arrays fixos podem conter apenas parte. O padrão numérico de IDs explicado pelo autor não deve virar parser obrigatório de país/fonte quando há campos relacionais próprios e exceção global. Proposta futura: cachear metadados por ID, atualizar e registrar idioma do terminal; não deduzir impacto pela string traduzida. NOT_RUN.

### 7.3.4 — tipo por ID (1702)

CalendarEventById resolve event_id em descrição, importância, país e demais atributos; não confundir ID de ocorrência com ID de tipo. Útil ao rastreamento de uma eventual observação de notícias, sem nova política financeira. Erro de resolução deve permanecer explícito. NOT_RUN.

### 7.3.5 — ocorrências por país/moeda (1702–1706)

CalendarValueHistory usa intervalo **from inclusivo/to exclusivo**, diferente dos intervalos inclusivos de séries próprias. to0 inclui futuros; ambos0 consultam toda base disponível. País e moeda simultâneos são AND. Ordem retornada pode não ser cronológica; consumidor deve ordenar, mesmo em consulta única. MqlCalendarRecord enriquece ocorrências com metadados para impressão, sem alterar a entidade original. Proposta de interface: separar campo bruto, conversão e rótulo; distinguir nenhum evento de sincronização/timeout/resultado parcial. NOT_RUN.

### 7.3.6 — ocorrências por tipo (1706–1709)

CalendarValueHistoryByEvent consulta um tipo e intervalo. Tipo existente pode não ter ocorrência na janela e produzir0/erro0; a estatística do exemplo exclui esses tipos por testar o retorno como booleano. Proposta futura: não reportar falha de conectividade a partir de lista vazia; contar total solicitado, obtido e erro. Nenhuma seleção de evento foi autorizada por frequência histórica. NOT_RUN.

### 7.3.7 — acompanhamento por ocorrência (1709–1712)

Não há OnCalendar; polling é responsabilidade do programa. CalendarValueById atualiza estado da ocorrência. O exemplo acompanha um indicador futuro e para após actual surgir. A narrativa chama-o mais próximo, mas o laço pega o primeiro compatível; como a API não garante ordem, uma adaptação deve ordenar ou calcular mínimo. Hora programada pode diferir da publicação real, e esse instante não é recuperável no histórico. Proposta: timer limitado, status de atraso e registro do instante observado, sem confundi-lo com instante exato de disponibilização na origem. NOT_RUN.

### 7.3.8 — mudanças por país/moeda (1713–1722)

CalendarValueLast recebe change_id por referência; zero inicializa cursor e retorna0 sem registros. Zero também significa nenhuma mudança, portanto erro exige inspeção separada. IDs crescem mas podem saltar; não são contadores contíguos. Só o último estado de cada ocorrência existe na API. CalendarChangeSaver registra horário observado e IDs em arquivo; não grava versões integrais dos valores, por isso sozinho não reconstrói todas as revisões. O protocolo empacota número de registros em bits altos e exige validação de comprimento/contagem/arquivo antes de uso real, omitida no exemplo. ChangeFileReader reproduz IDs por relógio virtual, com granularidade dependente do passo. Proposta futura: capturar snapshots completos, sequência, timestamps do servidor e observador, versão de schema e lacunas de coleta. Nenhum coletor ativado; NOT_RUN.

### 7.3.9 — mudanças por tipo (1723)

CalendarValueLastByEvent mantém semântica de cursor mas restringe um event_id. Zero inicializa, não é perda de dados comprovada nem erro. Cursor de um contexto não deve avançar indevidamente o de outro ao agregar consultas; qualquer implementação multi-filtro precisa verificar contrato efetivo de cada cursor. Proposta futura de adapter com estado explícito por consulta. NOT_RUN.

### 7.3.10 — CalendarFilter e monitor (1723–1742)

Classe do livro, não API nativa: distingue contexto inicial imutável, seletores e resultados. Strings de2/3 caracteres sem wildcard são interpretadas como país/moeda, demais como nome/fonte; isso explica necessidade de `*GDP*`. Só um eixo entre países/moedas comporta múltiplos no algoritmo apresentado, o outro usa primeiro valor; condições incoerentes não viram união automática. Strings são indexadas em cache e campos numéricos usam long; constantes em milionésimos precisam permanecer coerentes. select acumula, filtra e ordena em algumas condições; como consulta única também pode vir desordenada, a adaptação não deveria depender apenas de count>1 para ordenar. `LESS` no trecho abreviado nega greater, incluindo igualdade, potencial divergência do nome: requer exame do fonte integral antes de adoção.

format produz linhas legíveis e delimiter separa passado/futuro, enquanto limit remove os mais distantes. update mantém cursor para alterações recentes. CalendarMonitor lê moedas base/lucro do gráfico, filtra importância mínima e redesenha tabela em timer; uma moeda do ticker não garante cobertura suficiente de todos seus fatores macroeconômicos. Há linha visivelmente corrompida no texto de1741, impeditiva de compilação literal. Proposta futura: adapter tipado em vez de sintaxe ambígua por tamanho da string, ordenação universal, deduplicação por ocorrência e status de cobertura. Política de bloquear operação por notícia requer fonte normativa JPW e autorização específica. NOT_RUN.

### 7.3.11 — cache e tester (1742–1764)

Cache representa instanteX: não permite testar validamente além da captura e deve esconder actual antes de sua disponibilidade. DST atual é aplicado na extração inclusive ao passado; a amostra omite correção histórica. Países/tipos contêm strings e precisam serialização de dicionário além das estruturas simples; header identifica versão, mas não é validação completa de comprimentos, limites ou integridade. Arrays por IDs e por tempo permitem hashing/busca binária; o exemplo de find acessa índice sem demonstrar guarda contra célula vazia, e a ordem de guarda do while temporal merece revisão de limites. São pontos da listagem didática, não bugs do produto.

CalendarCache substitui change_id pela hora simulada e libera notícias pela hora programada: isso não reproduz alterações reais, forecasts revisados ou atraso de publicação. O histórico de IDs coletado anteriormente poderia ajudar, mas precisaria snapshots para fidelidade integral. CalendarFilterCached mantém interface e redireciona chamadas. tester_file transfere cache a agentes; nome alterado exige recompilação ou compartilhamento local, que não atende agente remoto. O exemplo falha inicialização do tester sem arquivo; online pode gerar cache e pedir reinício. Proposta futura: manifesto com hash, capturaX, intervalo, broker/timezone/DST, schema, versões de registros e função explícita de disponibilidade temporal, mais testes de leitura truncada e limites. NOT_RUN; não existe prova de cache produzido ou reaberto neste trabalho.

### 7.3.12 — negociação de notícias (1765–1774)

O EA didático usa indicador quantitativo de alta importância, moedas do par, forecast e impacto; soma direções invertendo sinal para moeda cotada, permite várias posições em hedging, atribui o último event_id ao magic e faz trailing em OnTick. Agregar eventos e atribuir apenas o último ao magic perde atribuição causal completa; comentário com lista ajuda, mas não resolve análise estatística automaticamente. O OnTester agrupa resultado por magic e soma profit/swap/commission nos deals selecionados de saída; validar comissões de entrada e divisão parcial seria necessário antes de chamar isso contabilidade integral.

Os resultados publicados pelo autor não mostram garantia de lucro, NFP/GDP não são sinais universalmente bons e seleção posterior do evento mais lucrativo traz viés de seleção. Impacto esperado não é retorno previsto, e atraso de notícia/DST/cache afeta teste. A ausência do cache provoca fallback online no exemplo, comportamento que nunca deve ser transplantado silenciosamente para um candidato sem contrato de modo. Para Stoikus este tópico é conhecimento de fronteira; negociar notícias, aumentar posições ou usar defaults de500 pontos/25 posições não é aplicação autorizada nem regra JPW. Proposta de pesquisa exclusivamente futura e isolada; todos os experimentos NOT_RUN.

## 7.4 — abertura de criptografia (1774)

Somente introdução sobre segurança da informação foi lida. Nenhuma API, algoritmo, garantia de autenticidade ou prática de armazenamento de segredo foi analisada neste lote. A fila começa1775; não extrapolar a abertura como capítulo concluído.

## Filas e critérios de integração

1. Leitura restante desta Parte7: PDF1775–2045; páginas finais2046–2047 também não lidas por este leitor. A fila não implica lacuna de outros leitores; o coordenador deverá unir evidências por página.
2. Conferência visual: figuras, tabelas com colunas cortadas e listagens que dependem dos fontes anexos permanecem NOT_INSPECTED; o corpo textual correspondente foi lido.
3. Confronto com fontes Stoikus: NOT_REVIEWED neste lote. Só depois localizar chamadas/ausências reais para promover “aplicação conceitual” a diagnóstico de implementação.
4. Toda demonstração do autor é evidência documental; reprodução local, compilação e ensaio nativo são NOT_RUN. Nenhum tempo/memória/PF/drawdown citado deve ser anexado como recibo local.
5. Prioridade de eventual pesquisa: contratos de disponibilidade temporal do calendário e de relógio sintético, depois gestão de recursos e schemas; não há proposta de habilitar trading, ML ou novos executores.
