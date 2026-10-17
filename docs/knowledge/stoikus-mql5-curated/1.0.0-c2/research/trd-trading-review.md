# TRD — Parte 6: leitura semântica, observação e execução

Estado desta etapa: **513/513 páginas físicas lidas**, conforme JSON de cobertura. Intervalo contínuo:1049–1561. Leitura integral do texto extraído da Parte6; isso não equivale à inspeção visual de513 páginas nem a teste dos exemplos. Figuras apenas por legendas/texto extraído; não houve inspeção visual. Exemplos do livro e propostas: **NOT_RUN**. Nenhuma mudança no produto, kit ou piloto. Fonte PDF SHA256 `9ff6c55090527afa0efce722d67760805ee335fc64dad3c83638a89e6c79a145`. Os hashes de texto por página rastreiam exatamente o corpo consultado; não provam execução nem validação do produto.

As indicações de aplicação abaixo se referem à pertinência ao StoikusMonitor descrito no BRIEF, um EA observacional que não envia ordens. Não são constatações de implementação: esta leitura não auditou o código do produto. Uma API permitir negociar não constitui autorização do proprietário para negociar.

## 6.1 — Instrumentos e Market Watch [TRD,6.1,p.PDF1049–1134]

**Conhecimento.** Símbolos disponíveis, selecionados e visíveis são conjuntos diferentes. `SymbolsTotal(true)` inclui seleção implícita para conversões, embora `SYMBOL_VISIBLE` seja falso. O parâmetro selected deve coincidir entre contagem e enumeração. Nomes são sensíveis a maiúsculas; não se deve reconstruir propriedades cambiais a partir de um ticker com prefixos ou sufixos. `SYMBOL_CURRENCY_BASE`, `_PROFIT` e `_MARGIN` dão os contextos relevantes; diferentes contratos podem compartilhar moedas e não serem Forex. [TRD,6.1.1–3,p.PDF1050–1055;6.1.9–11,p.PDF1076–1090]

`SymbolSelect` altera Market Watch. Remover símbolos pode quebrar consumidores indiretos; restaurar recoloca no final e não restaura a ordem original. Separar inventário somente leitura de preparação explícita do ambiente. `SymbolIsSynchronized` trata o símbolo; `SERIES_SYNCHRONIZED` trata símbolo/timeframe. O primeiro pode ser verdadeiro antes de o segundo. `SymbolInfoTick` permite obter campos de um tick conjuntamente; ler Bid/Ask/tempo por chamadas isoladas pode combinar ticks diferentes. [TRD,6.1.2,p.PDF1051–1054;6.1.4–5,p.PDF1055–1060;6.1.20,p.PDF1126–1128]

Sessões de cotação e negociação diferem e seguem horário do servidor. Há múltiplas sessões por dia e fim em 24h ou além: descartar indiscriminadamente a componente de dia pode inverter uma sessão que cruza meia-noite. O livro mostra verificação simplificada; ela não demonstra cobertura de todos os cruzamentos de dia ou mudanças extraordinárias. Tipos de gráfico Bid/Last não são preços de execução intercambiáveis; Ask/Bid importam para custos e para ativação/fechamento. [TRD,6.1.6,p.PDF1061–1066;6.1.10,p.PDF1077–1083]

Digits é apresentação, Point é unidade de cotação e tick size é grade negociável. Tick value pode depender de lucro/perda e conversão. Volume mínimo, máximo, passo e limite agregado por direção são restrições distintas; limite0 é tratado no exemplo como ausência de limite. Não assumir passo decimal a partir de Digits nem converter volumes por número fixo de casas. [TRD,6.1.12–13,p.PDF1090–1096]

Modo de negociação é enumeração; modos permitidos de ordem e preenchimento são máscaras. Ter tipos de ordem habilitados não supera `SYMBOL_TRADE_MODE_DISABLED`. O broker pode alterar especificações. FOK exige todo o volume, ainda que distribuído por vários negócios; IOC cancela saldo não executado; RETURN mantém saldo, mas é proibido para Market Execution. O zero de `ORDER_FILLING_FOK` não corresponde ao bit1 de `SYMBOL_FILLING_FOK`; copiar números entre enum e máscara é erro conceitual. [TRD,6.1.14–15,p.PDF1096–1104;6.4.5,p.PDF1176–1177]

Margem depende de modo de cálculo, moedas, multiplicadores e eventual cobertura. `SYMBOL_MARGIN_HEDGED` muda de interpretação conforme margem inicial; com `SYMBOL_MARGIN_HEDGED_USE_LEG=true`, prevalece a maior margem entre lados e a propriedade de margem coberta é ignorada. `OrderCalcMargin` ignora posições e ordens existentes; não é previsão completa da margem total após uma operação. [TRD,6.1.7,p.PDF1066–1067;6.1.16,p.PDF1104–1112]

GTC não significa proteção necessariamente preservada: os modos diários podem excluir ordens e também SL/TP, ou preservar stops. Stops level e freeze level são distâncias em points e usam a referência Ask/Bid da operação. Spread flutuante é dado dinâmico. Swap exige interpretar modo, moeda, direção e rollover triplo; os modos de reabertura afetam o ciclo de vida da posição. [TRD,6.1.17–19,p.PDF1112–1126]

Descrições, setor, país e path dependem do broker e podem estar vazios. Book depth declarado não prova recebimento do book. Símbolos customizados têm série local e não podem ser negociados online pelas APIs regulares do servidor. Derivativos e títulos exigem propriedades específicas; a seção6.1.24 continua em1135, também lida. [TRD,6.1.21–24,p.PDF1128–1135]

**Aplicação.** Contextualizar cada evidência do monitor com servidor, símbolo exato, moeda/unidades, tempo da captura e validade de leitura. Distinguir indisponibilidade de propriedade de valor numérico0. A telemetria de negociação desabilitada é estado observado, não falha que autorize habilitar negociação.

**Proposta.** Manifesto de especificações capturado por sessão e associado aos snapshots; registrar símbolo selecionado/visível/custom, sincronização, tempo do último tick, point/ticksize, moedas, volume step e modos. Rejeitar cálculo com divisores nulos ou dados não prontos. Proposta ainda não implementada/testada.

**Sem aplicação atual.** Limpeza automática de Market Watch, criação de símbolos, escolha de filling para envio e alteração de SL/TP não pertencem ao monitor observacional. Não transportar as estratégias ou utilitários de manutenção do livro para o produto.

## 6.2 — Depth of Market [TRD,6.2,p.PDF1135–1155]

**Conhecimento.** Book e ticks podem vir de fornecedores distintos e eventos não são equivalentes. DOM online não tem histórico nativo garantido no servidor nem replay padrão no Tester. Usá-lo retrospectivamente requer captura/reprodução próprias. Inscrição é por símbolo e gráfico, com contador compartilhado: programas no mesmo gráfico podem receber eventos por assinatura iniciada por outro programa. MQL5 não expõe o contador; equilibrar inscrições e liberações é responsabilidade do consumidor. [TRD,6.2.1–2,p.PDF1136–1140]

`OnBookEvent` notifica mudança, sem carregar o book causal. `MarketBookGet` obtém estado no momento da consulta, potencialmente posterior; não há garantia de capturar cada estado único. Chegadas de eventos podem superar ticks; renderização pode atrasar sem significar perda da aquisição. O book pode estar vazio, conter um nível, repetições, preços desordenados, cruzamentos e lados assimétricos. O número de entradas não autoriza dividir cegamente em metades iguais. [TRD,6.2.2–4,p.PDF1138–1155]

**Aplicação.** Se DOM for usado futuramente como evidência contextual, classificá-lo como amostra observada, não fluxo completo de mercado ou prova de preço executável.

**Proposta.** Experimento separado de captura com status da assinatura, timestamp monotônico/servidor, contagem, validação de preços/tipos/volumes e limites de custo. Replay identifica origem e lacunas; não chamar tick sintético de tick oficial.

**Sem aplicação atual.** Não há requisito estabelecido no BRIEF para DOM, alertas de liquidez ou quasi-ticks no monitor. Não introduzir dependência DOM para cumprir o escopo atual.

## 6.3 — Conta [TRD,6.3,p.PDF1155–1168]

**Conhecimento.** Um terminal conecta uma conta por vez e todos os programas a compartilham. Mudança provoca reinicialização com `REASON_ACCOUNT`. Propriedades são expostas por famílias Integer/Double/String e configuradas pelo broker. Identidade inclui login, servidor e companhia; modo demo/real/contest vem de `ACCOUNT_TRADE_MODE`, não de substring no nome do servidor. Valores monetários usam moeda e precisão da conta. [TRD,6.3.1–4,p.PDF1155–1161]

Netting admite uma posição por símbolo, possivelmente originada por muitos deals; hedging admite posições independentes inclusive opostas. Exchange também usa netting, mas cálculo de margem segue suas regras. Não confundir tipo real/demo com modo de contabilização. `ACCOUNT_TRADE_ALLOWED` e `ACCOUNT_TRADE_EXPERT` são permissões diferentes; senha investidor pode impedir negociação mantendo observação. FIFO, limite de pendentes e stopout por dinheiro/percentual completam as restrições. [TRD,6.3.5–7,p.PDF1161–1168]

Balance, equity, profit, credit, margin, free margin e comissão bloqueada não são sinônimos. Comissão pode ser descontada imediatamente ou apurada depois. O livro adverte que não existe ali API universal de comissão futura; histórico dá estimativa, não garantia. Margem e stopout do broker não substituem limites normativos JPW. [TRD,6.3.7–8,p.PDF1165–1168]

**Aplicação.** Escopar estado persistente por conta+servidor; uma troca não pode herdar cursor histórico como se fosse a mesma conta. Exibir moeda e modo de contabilização. Monitor continuar observando com negociação desabilitada é compatível com a plataforma e com a finalidade do produto.

**Proposta.** Caso de reconciliação de conta trocada/desconectada e matriz netting/hedging; custos realizados e bloqueados em campos separados. Regras JPW ficam como política explicitamente versionada, sem inferência dos limites do broker.

**Sem aplicação atual.** Permissão técnica positiva não arma Supervisor nem autoriza execução. Não tentar corrigir flags de negociação da conta/terminal.

## 6.4.1–13 — Eventos e fronteira de envio [TRD,p.PDF1169–1213]

**Conhecimento.** Um EA pode ser não negociador e trabalhar por timer. `OnTick` é evento do símbolo do gráfico; programa processa eventos sequencialmente e ticks novos não são enfileirados se houver tick pendente/em processamento. Botão Algo Trading restringe envio, não impede funcionamento do EA. [TRD,6.4.1,p.PDF1170–1171;6.4.7,p.PDF1179]

Ordem é instrução, deal é execução, posição é exposição formada e modificada por deals. Uma ordem pode produzir vários deals; não usar contagem de ordens como contagem de operações financeiras. Enumeração de ações distingue envio a mercado, pendentes, modificação, remoção, SLTP e close-by. Essas últimas também são mutações de negociação. [TRD,6.4.2–6,p.PDF1172–1178]

`OrderCalcMargin` calcula caso isolado; `OrderCalcProfit` recebe buy/sell, volume e preços e devolve estimativa na moeda da conta. Exemplos alternativos do livro são didáticos, têm instrumentos não suportados e simplificações. Preservar valor raw e lote normalizado evita sugerir mínimo quando risco não o comporta. Não copiar parâmetros de risco5% como regra JPW. [TRD,6.4.7–8,p.PDF1178–1196]

`MqlTradeRequest` deve ser inicializada; campos exigidos variam por ação e execução. `magic=0` não prova operação manual, pois EAs podem usar zero. Razões de ordens/deals/posições têm maior valor de classificação de origem, ainda sem provar autorização de negócio. Ticket de posição pode mudar em operações de serviço. [TRD,6.4.9,p.PDF1196–1199]

`OrderCheck` faz verificação formal e projeção simplificada: sucesso não garante envio/executado. Ao contrário da margem isolada, projeta conta cumulativamente, mas não modela precisamente toda redução/cobertura. `OrderSend=true` não garante execução. `OrderSendAsync=true` tampouco garante aceitação no servidor; resultado exige correlação e confirmação posterior. Async não acelera processamento do servidor; no Tester funciona como Send, limitando a demonstração de concorrência. `retcode`, `retcode_external`, retorno bool e `_LastError` são camadas distintas. `request_id` correlaciona solicitação com evento, não é ticket. [TRD,6.4.10–13,p.PDF1199–1213]

**Aplicação.** A ausência de função OnTick não invalida o monitor. Seu papel é registrar resultados de ordens externas; nunca criar requests para remediar divergências. Comparar cotação, margem estimada, recebimento de solicitação e execução confirmada como fatos diferentes.

**Proposta.** Caso adversarial onde envio é aceito e negócio ainda não existe; esquema de evidência separa observado, estimado, incompleto, erro, confirmado e expirado. Exemplos de envio do livro permanecem NOT_RUN e fora do produto.

**Sem aplicação atual.** Trading API e as estratégias6.4.14–25 não foram integradas. Foram posteriormente lidas integralmente; ver complemento6.4.14–25 abaixo.

## 6.4.26–32 — Listas, propriedades e histórico [TRD,p.PDF1321–1344]

**Conhecimento.** Funções PositionGet leem posição atual, não criam/modificam posição nem retornam histórico completo. A seleção é cache local: re-selecionar antes de ler e tratar desaparecimento. `PositionSelect(symbol)` em hedging seleciona menor ticket e não todas as posições. Ticket pode mudar; `POSITION_IDENTIFIER` vincula `ORDER_POSITION_ID`/`DEAL_POSITION_ID` ao ciclo de vida. Reversão netting conserva identificador, embora ticket mude. `POSITION_TIME_UPDATE` cobre mudança de volume, não toda alteração de SLTP/swap. [TRD,6.4.26–28,p.PDF1321–1328]

Momento transitório pode mostrar zero ordens e zero posições enquanto uma ordem vira execução. O livro recomenda preservar último estado coerente e confirmar destino antes de concluir desaparecimento; contagens isoladas não formam prova de conta vazia. [TRD,6.4.26,p.PDF1323]

Deals incluem balance, crédito, comissões, dividendos, taxas e correções além de buy/sell; podem ser alterados/cancelados retroativamente. `DEAL_ENTRY_IN/OUT/INOUT/OUT_BY` expressa papel no ciclo de posição. `DEAL_PROFIT`, comissão, swap e fee devem ser interpretados separadamente. [TRD,6.4.29,p.PDF1335–1339]

`HistorySelect` usa intervalo inclusivo em tempo do servidor; para ordens seleciona por execução, não setup. True com lista vazia não é erro. `HistorySelectByPosition` ignora `ORDER_POSITION_BY_ID`, exigindo cuidado no segundo lado de close-by. `HistoryOrderSelect`/`HistoryDealSelect` reduzem seus contextos ao item selecionado, podendo destruir a enumeração do chamador. O próprio livro corrige construtor que cometia esse erro; o fallback de selecionar histórico inteiro também tem custo/efeito de contexto. [TRD,6.4.30–32,p.PDF1339–1344]

**Aplicação.** Reconstruir por identificadores e deals, preservando conta e contexto de seleção. Qualificar lista incompleta por corrida, falha de API ou horizonte; ausência não é zero econômico. Reconciliar comissões de entrada/saída e operações de saldo antes de medir resultado.

**Proposta.** Congelar lista de tickets numa coleta e tratar getter bool de sucesso separado do valor0. Snapshot deve registrar seu intervalo de coleta, não timestamp fictício de atomicidade. Detectar atualização/remoção histórica e suportar nova leitura, não apenas append por último ticket.

**Sem aplicação atual.** Não encerrar posições para restaurar consistência. Páginas1329–1334 e1345–1355 posteriormente lidas integralmente: os filtros/tuplas são mecanismos de seleção, sem garantia de snapshot global atômico.

## 6.4.33–37 — Transações, OnTrade e reconciliação [TRD,p.PDF1356–1365;1391–1428]

**Conhecimento.** Mudanças vêm de usuário, scripts/EAs e servidor; saldo e stopout também geram transações. Tipo determina campos válidos. Em `TRADE_TRANSACTION_REQUEST`, considerar request/result; nos demais tipos, esses argumentos não descrevem solicitação relevante. `request_id` reinicia por sessão do terminal. Não equivale a identificador durável. Nem abertura nem liquidação comum da posição exigem `TRADE_TRANSACTION_POSITION`. [TRD,6.4.33–34,p.PDF1356–1361]

Uma solicitação gera vários eventos cuja ordem de chegada não é garantida. Terminal continua alterando conta durante callback; objeto mencionado pode já ter mudado ou desaparecido. Fila de transações comporta1024 e callbacks longos permitem substituição de eventos antigos. Campos incompletos exigem consulta apropriada. O texto do livro menciona indicadores recebendo OnTradeTransaction em1359: **ponto pendente de confronto com REF**, não adotar como garantia do manual. [TRD,6.4.34,p.PDF1359–1365]

`OnTrade` é sinal agregado sem proporção exata com requests ou transações. Chamá-lo dispara recálculo/releitura; não prova que um deal novo específico ocorreu. `OnTradeTransaction` é seletivo, mas eventos não bastam para recuperar programa que esteve offline: lógica precisa reconstruir estado ao iniciar independentemente dos eventos perdidos. Migração ativo→histórico pode deixar ordem temporariamente indisponível online; no Tester do exemplo, ela já está em histórico no evento DELETE. [TRD,6.4.35–36,p.PDF1391–1399]

O capítulo de caching separa monitores, estado salvo, filtros e caches. Refresh re-seleciona item; diff compara propriedades antigas/atuais; existência é um estado diferente de mudança de campo. Ordem ativa e histórica precisam caches distintos para enxergar transição. Revalidar contexto histórico antes de filtro. O exemplo demonstra mesma ordem simultaneamente em caches ativo/histórico porque duas varreduras ocorreram antes/depois da transição. Ordem inversa pode temporariamente não vê-la em nenhum. MQL5 não entrega sincronização atômica da conta inteira. [TRD,6.4.37,p.PDF1399–1428]

**Aplicação.** Monitor robusto usa evento como invalidação/aceleração, com reconciliação de snapshot/histórico ao iniciar e após desconexão. Duplicidade transitória de fontes não equivale a duplicidade de operação; indisponibilidade transitória não autoriza declarar encerramento. Deduplicar por entidade, tipo, conta e versão observada, nunca simplesmente por número de callback.

**Proposta.** Callback curto registra tipo/tickets e marca coleta pendente; rotina limitada reconcilia evidência e persiste cursor só após sucesso. Testar callbacks fora de ordem, reentrada lógica, eventos repetidos, histórico corrigido, posição de ticket trocado, perda de sessão e lote de mais eventos que capacidade. O limite1024 é capacidade da plataforma, não volume seguro nem critério de aprovação do produto. Nenhuma proposta foi implementada.

**Sem aplicação atual.** A estratégia OCO e grid do livro reage enviando ordens; aproveitar apenas a lição de observação/reconstrução não autoriza copiá-las. Páginas1366–1390 posteriormente lidas integralmente: ver complemento sobre bloqueio e relay.

## 6.5 — Tester [TRD,p.PDF1449–1465;1558–1561]

**Conhecimento.** Agentes têm ambientes isolados de conta, globals e arquivos; FILE_COMMON cria exceção e potencial disputa. Logs/resultados do agente não são logs do terminal vivo. Modo real pode conter preenchimento de minutos sem ticks por geração; registrar percentual/qualidade efetiva em vez de presumir100% pelo nome selecionado. OHLC e open-only removem trajetória e podem produzir estratégias artificialmente lucrativas. Open-only mantém ticks ocultos para stops/margem etc.; ausência de OnTick intermediário não implica ausência de efeitos. [TRD,6.5.1,p.PDF1449–1458]

O detector de modo do livro infere por erros de CopyTicks e duas amostras; trata-se de técnica didática dependente de comportamento, não contrato estável que substitua configuração/relatório de execução. Timers continuam sendo simulados independentemente do modo e podem multiplicar custo:1s em H4 implica14400 callbacks por barra. TimeLocal,TimeTradeServer e TimeGMT coincidem no Tester; isso não verifica conversões reais de fuso. Sleep avança tempo simulado e pode acionar ordens/stops durante a pausa. [TRD,6.5.1–2,p.PDF1454–1459]

Sem visualização, objetos não são construídos normalmente; leituras retornam zero. Indicadores podem calcular sob demanda e o gráfico pós-teste recalcula indicadores, não sendo prova de valores usados durante execução. Templates também alteram visualização. Multissímbolo exige pré-carga e sincronização por timestamps; um tick de EURUSD não garante barra nova de GBPUSD. O exemplo com Sleep espera indefinidamente: proposta aplicada precisaria timeout/IsStopped e distinguir ausência de sessão. [TRD,6.5.3–4,p.PDF1459–1465]

Modo matemático chama apenas OnInit/OnTester/OnDeinit, sem ticks/conta/símbolos: não valida monitor event-driven. Debug/profiling recompilam com configuração própria e é preciso identificar artefato release versus debug. Profiling visual no Tester não é suportado segundo texto. Otimização suprime Print/Comment salvo inicialização; comunicação externa, WebRequest, sockets, notificações e vários recursos gráficos não funcionam no Tester. Eventos interativos de teclado/mouse/objetos não são gerados ali. [TRD,6.5.17–19,p.PDF1558–1561]

**Aplicação.** Para monitor, aprovação funcional depende da veracidade dos estados/eventos, isolamento e custos, não de curva de rentabilidade. PASS host/UI histórico não vira compile/runtime nativo. Um replay puro de dados não comprova corretagem, reconexão ou cronologia real do servidor.

**Proposta.** Recibo nativo deve informar build MT5/EX5, hashes, conta demo e modo, símbolos, especificações, período, fuso, modo e qualidade de ticks, visual/nonvisual, agente, limites e logs. Matriz de ambiente distingue Tester, terminal demo e fixtures host. Cases sobre comunicação externa ficam explicitamente fora do alcance do Tester.

**Sem aplicação atual.** Não otimizar parâmetros normativos JPW para maximizar lucro. Parte6.5.5–16 foi posteriormente lida integralmente; ver complemento sobre estatísticas, frames e relatórios. Não houve execução nativa, otimização, download de histórico nem ativação de agentes.

## Questões críticas da própria fonte e limites de transposição

1. `LESS` no trecho1088 rejeita `greater`, aceitando igualdade: validar semântica antes de adaptar o filtro.
2. Tolerância double em1086 usa `fmax(v1,v2)` sem valor absoluto: entradas negativas podem tornar tolerância negativa. Não importar como comparador universal.
3. `Convert` em1193 registra falha de par cambial mas continua retornando true, podendo conservar valor não convertido. Exigir resultado explícito por moeda antes de usar estimativas monetárias.
4. Exemplo1138 não garante todos os estados do book; exemplos1146/1154 fazem acesso de índices que exigiria pré-condições adicionais para book vazio/unilateral/curto. Essas são análises estáticas dos trechos lidos, não falhas demonstradas por execução.
5. Fonte contém logs históricos com `POSITION_COMMISSION`1401/1427. Não deduzir disponibilidade atual da propriedade; confrontar API/compilador alvo e preferir fonte contábil correta.
6. Índice delimita seções antes de terminar texto em páginas seguintes; por isso páginas efetivamente lidas são autoridade do ledger. Índice não é prova de leitura integral de seção.

## 6.4.14–25 — Execução, proteção e ordens: complemento integral [TRD,p.PDF1214–1320]

**Conhecimento.** Buy/sell usam ação DEAL; símbolo, volume, tipo e filling são essenciais, enquanto preço/deviation dependem de execução. SL/TP podem ser proibidos no pedido inicial por configuração de servidor sem propriedade antecipada que a revele. Fazer entrada e proteção em duas operações cria janela de posição aberta sem proteção se a segunda falhar. Não transformar descrição de alternativa técnica em recomendação universal. [TRD,6.4.14,p.PDF1214–1228]

O wrapper síncrono didático espera ordens/posição por polling com timeout; a própria fonte omite partes e remete ao arquivo completo. Existem caminhos em que ticket e identificador de posição diferem. Busy-wait bloqueia a thread do programa e tem custo; timeout é estado indeterminado a reconciliar, não prova de fracasso econômico nem permissão para reenviar. Normalização silenciosa de filling muda intenção: quando política específica é requisito, o livro sugere interromper em vez de corrigir. [TRD,6.4.14,p.PDF1216–1228]

SLTP modifica posição e zero remove proteção. Trailing stop é negociação porque envia modificação, mesmo sem nova entrada. O exemplo cria posição ao não encontrar nenhuma e reinicia após encerramento; portanto não é utilitário passivo de observação. Seu detectLevel usa0 como não agir e DBL_MAX como algoritmo padrão: sentinelas têm significados que não podem ser intercambiados com preço válido. [TRD,6.4.15–16,p.PDF1229–1247]

Fechamento normal exige operação contrária, posição correta e volume; fechamento parcial conserva saldo, que deve respeitar grade. Posição agregada pode exceder máximo por ordem e exigir múltiplas ordens para encerrar. Em hedging, omitir ticket pode criar exposição oposta em vez de encerrar a posição pretendida. Close-by depende de hedging e permissão do símbolo, trabalha no mínimo entre volumes e pode poupar um spread. O P/L total não deve ser contado duas vezes por dois deals: resultado é assimétrico e pode estar em apenas uma saída. Estatísticas long/short mudam se inverter os tickets, sem alterar necessariamente o total. [TRD,6.4.17–18,p.PDF1247–1265]

Pendentes distinguem preço de ativação e stoplimit; stoplimit ativado cria limite. Modificação não altera tipo/volume por escolha do cliente e zeros em sl/tp excluem proteção já existente. Remoção exige confirmação em histórico, não só falha de OrderSelect. OnDeinit de um exemplo remove ordem e mudanças de parâmetros também disparam esse ciclo; isso seria efeito operacional indevido num monitor. [TRD,6.4.19–21,p.PDF1265–1290]

Listas ativas incluem pendentes e ordens de mercado ainda não concluídas. Ordem pode ser ativa/histórica, deal existe no histórico, posição existe online; histórico de posição é reconstrução pelos deals. Ordem de enumeração não é contrato; cache de seleção fica obsoleto. `ORDER_REASON` fornece origem sem analisar comentário localizado. Estados STARTED/PLACED/PARTIAL/REQUEST_MODIFY/REQUEST_CANCEL não são execuções equivalentes. Tipo, estado, volume inicial/restante e timestamps devem acompanhar evidência. [TRD,6.4.22–24,p.PDF1290–1304]

Filtros tipados, tuplas e monitores permitem leitura/seleção comum para ordens, deals e posições, mas não eliminam erros de seleção nem tornam múltiplas consultas atômicas. O exemplo de grid assume configuração específica, tolera ou classifica transições segundo sua estratégia e modifica posições/ordens para manter invariantes. Invariantes do exemplo não são invariantes de uma conta geral. [TRD,6.4.25,p.PDF1304–1321]

**Aplicação.** O monitor deve observar SL/TP, parcial, close-by e motivos de saída para explicar exposição/custos. Sua fronteira de não execução inclui não remover pendentes, não alterar proteção e não fechar posições. Divergência de inventário produz evidência pendente, jamais ação automática de compensação.

**Proposta.** Casos de fixtures sobre: parcial com saldo; close-by de volumes diferentes; P/L em apenas um lado; ticket trocado mantendo identificador; modificação que retira SLTP; ordem em cancelamento que ainda executa; timeout seguido de confirmação tardia. Aplicar limites de tempo/custo e backoff a consultas; no futuro executor separado exigiria autorização própria e reconciliação antes de retry.

**Sem aplicação atual.** Estratégias de trailing, grid, criação/remoção em OnDeinit e tratamento de erro que habilita negociação não entram no StoikusMonitor. Todos os exemplosNOT_RUN.

## 6.4.28–35 — Complementos de tuplas, custo e bloqueio [TRD,p.PDF1329–1390]

**Conhecimento.** Tupla associa tipo esperado a propriedade; erro nessa associação não se resolve com cast silencioso. Leituras separadas de símbolos/valores requerem manter associação e não supor estabilidade da lista entre chamadas. Histórico longo tem custo: a fonte sugere cache e último momento processado, mas histórico também pode ser corrigido retroativamente e um cursor estritamente append-only não basta para toda conta. Exemplo1353 soma sóDEAL_PROFIT e declara TODO de comissões/swap/fees; não é resultado líquido universal. [TRD,6.4.28–32,p.PDF1329–1355]

Programa é monothread: dentro de OnTimer com Sleep ou sequência de envio, sua própria OnTradeTransaction só drena ao retornar. Outro programa pode receber eventos antes. Uma sequência de logs local ordenada não prova ordem de execução da conta. Relay do livro usa indicador com buffer circular e bit-preserving converter para transportar ulong sem perda por double; request_id e sincronização de tamanho/indexação são pré-condições. O livro reconhece perda potencial na virada da barra e ausência do evento de transação em indicadores no Tester. [TRD,6.4.34–35,p.PDF1366–1385]

AsyncSwitcher RAII desliga modo async no destrutor após qualquer saída; ele restaura false, não estado anterior arbitrário. Exemplo mediu20 solicitações em1030ms versus234ms; são medidas do autor naquele ambiente, sem comprovar ganho de5x em qualquer broker ou no produto. Tempos de confirmação de lote não são latência individual de cada solicitação. [TRD,6.4.35,p.PDF1386–1390]

**Aplicação.** Não usar Sleep/polling ativo no callback do monitor como forma de obter eventos da própria fila. Não medir a thread do monitor como se fosse serviço do servidor. Tickets/IDs em JSON devem preservar inteiros64-bit, especialmente caso atravessem JavaScript.

**Proposta.** Limitar custo de histórico por consulta, usar janela sobreposta e reconciliação completa sob critérios explícitos; idempotência de evidência não é idempotência de envio. Medir atraso entre tempo do evento, recebimento e publicação, com relógios distinguidos.

**Sem aplicação atual.** Relay e switches de envio são técnicas de execução do livro; não há justificativa estabelecida para adicioná-los ao monitor. Não atribuir ao produto os benchmarks do livro.

## 6.4.38–40 — Multissímbolo e Wizard [TRD,p.PDF1429–1449]

**Conhecimento.** Caches do exemplo são RAM sem persistência e perdem mudança entre sessões. EA pode atuar sobre vários símbolos, mas OnTick continua vinculado ao gráfico; o símbolo principal pode alterar resultados temporais. Monitor por timer/eventos deve indicar universo efetivamente coberto. Interfaces e composição separam sinal, estratégia, configuração e pool. Wizard template gera handlers, enquanto generate inclui lógica negociadora baseada em biblioteca. Apenas um EA por gráfico é permitido. [TRD,6.4.38–40,p.PDF1429–1449]

**Aplicação.** Separar coleta por símbolo de política normativa e UI favorece auditoria; falta de persistência não pode ser ocultada por eventos futuros. Descrição do monitor como EA não implica que precise conter estratégia de sinal.

**Proposta.** Manifesto de universo, configuração validada e persistência por conta/sessão; reinício reconstrói antes de avançar watermark. Não usar arquivo ou string de configurações não validada como prova de universo completo.

**Sem aplicação atual.** Martingale, diversificação sugerida pelo autor e geração automática de robot negociador são estudo da plataforma, não estratégia aprovada JPW. Limites de strings250/63 descritos em1442 devem ser confrontados com build alvo antes de norma de implementação.

## 6.5.5–16 — Estatísticas, otimização e evidências [TRD,p.PDF1465–1558]

**Conhecimento.** Critério de otimização seleciona candidatos; OnTester só influencia Custom max quando escolhido. Ter handler não altera automaticamente critério e API descrita não informa seleção do usuário. Métricas distinguem deals de trades de saída, DD absoluto e relativo e momento de ocorrência. Profit factor sem perdas pode usar DBL_MAX; divisões e sentinelas não são valores finitos normais de relatório. Score composto não garante previsibilidade. Forward do autor perdeu grande parte das combinações lucrativas: relatórios otimistas de treino não comprovam robustez. [TRD,6.5.5–7,p.PDF1465–1489]

Cache de otimização pode reaproveitar resultados mesmo quando critério muda; tester_no_cache desliga leitura, mas continua escrevendo resultados. Sessão fresca precisa prova de condições/cache, não só nova pasta de relatório. ParameterSetRange muda execução mas GetRange ainda pode retornar valores originais; incluir configuração efetiva nos recibos. INIT_PARAMETERS_INCORRECT pode criar buracos em populações genéticas; isso não autoriza corrigir parâmetros normativos inválidos silenciosamente. [TRD,6.5.7–8,p.PDF1482–1496]

OnTesterInit/Pass/Deinit rodam na cópia de serviço do terminal, separada dos agentes. FrameAdd só envia agente→terminal durante otimização; OnTesterPass sinaliza chegada de um ou mais frames e não cada teste concluído. Ordem de frames não é ordem de passes; pode haver frames tardios a drenar em Deinit. FrameFirst/Filter rebobinam; usá-los repetidamente sem controle duplica processamento e custo. Array/file tem tipos/encoding próprios; payload incompatível pode falhar. Atribuir pelo pass/configuração, não ordem de chegada. [TRD,6.5.9–11,p.PDF1496–1505]

Diretivas declaram arquivos, indicadores, bibliotecas e sets para agentes. Indicador com nome dinâmico exige declaração; arquivo inexistente na compilação pode ficar ausente mesmo se aparecer antes da execução. Não assumir que sucesso de compilação prova empacotamento completo. TesterHideIndicators afeta novos handles e templates podem prevalecer. Ocultar visualização não significa proteção de implementação ou evidência omitida. Depósitos/saques simulados modificam balance e exigem classificação própria para não inflar rentabilidade. TesterStop encerra passagem normalmente e chama OnTester; ele não seta IsStopped nem para toda otimização. [TRD,6.5.12–15,p.PDF1506–1515]

Exemplo grande combina indicadores, eventos custom, sincronização, estatísticas próprias, HTML/SVG e frames. Assumir sessões iguais é uma hipótese declarada no1520. Buffer labels não são universalmente descobríveis por API e acordo de interface é necessário. Relatório por símbolo/estratégia exige filtro e depósito-base explícitos; não somar depósitos iniciais repetidos de sub-relatórios como capital real. Equity exige amostragem contínua e pode perder mínimos intratick. Cálculo de balanço deve incluir custos de entrada e saída; o resumo de saídas R2 não deve ser promovido a contabilidade geral. Destrutor usado como gatilho de resultado financeiro depende da vida do objeto e não substitui confirmação do servidor. [TRD,6.5.16,p.PDF1515–1558]

**Aplicação.** O monitor será avaliado por completude, precisão, custo, isolamento e recuperação, não por score de lucro. Relatórios host, Tester e demo precisam origem explícita. Uma renderização HTML correta não valida cálculo nem dados financeiros que a alimentaram.

**Proposta.** Harness futuro fixa configuration+hashes, identifica fresh/cache, faz reconciliação de valores sem arredondamento antecipado, mede custo e drena evidências tardias. Referência contábil soma profit/swap/commission/fee e trata fluxo externo separadamente; testes incluem moeda com casas diferentes de2 e saldo sem trades.

**Sem aplicação atual.** Não executar otimização genética, martingale, depósito/saque, relay ou geração de presets para alterar política produtiva. Todas as experiências deste estudo permanecemNOT_RUN.

## Questões adicionais para revisão técnica antes de adaptar exemplos

7. Página1229 escreve hedging nas duas metades da explicação; tabela e contexto distinguem netting versus hedging. Citar tabela e esclarecer erro textual, sem inverter requisito.
8. Página1233 usa `retcode != DONE || retcode != PLACED`, condição sempre verdadeira para constantes diferentes; contradiz sucesso alegado no1236. Tratar como defeito do trecho, conferir arquivo original/REF antes de ensinar implementação.
9. Página1251 `closed()` imprime timeout mas retorna true depois; confirmação não fica garantida pelo código mostrado. Implementação aplicada deve propagar resultado indeterminado, não concluir sucesso.
10. Página1278 tenta OrderSelect ou HistoryOrderSelect e depois usa OrderGetDouble incondicionalmente; histórico requer família correta de getters. Não copiar sem revisão de contexto.
11. Página1262 acumula erro com AND sobre flag inicialmente false; o propósito declarado de detectar qualquer falha não é assegurado pela expressão mostrada.
12. Página1484 fala em R2 negativo, mas fórmula mostrada é quadrado de correlação; distinguir definição adotada e hipóteses, sem reproduzir argumento como propriedade matemática universal. Após filtrar inválidos, quantidade efetiva precisa ser validada antes de dividir.
13. Página1538 normaliza cada parcela em2 casas fixas apesar de precisão da conta variar. Exemplo não é cálculo monetário universal e depende da política de arredondamento.
14. Páginas1507/1509 têm tensão entre arquivo existente na compilação e reiniciar após criá-lo; recibo aplicado deve registrar compilação+dependências e não inferir entrega ao agente por existência atual.

## Fechamento de cobertura e continuidade

Todos os513 corpos de páginas1049–1561 foram exibidos e lidos, incluindo tabelas/código extraídos. O primeiro lote1155–1177 truncou o miolo1163–1169; esse miolo foi relido integralmente em chamada independente. Nenhuma outra saída de corpo foi truncada. Índice/extração não foram contados como leitura. Figuras não foram inspecionadas visualmente; resultados citados são resultados do autor, não reproduções. Parte7 não iniciada nesta entrega para preservar a revisão e o ledger da Parte6. A continuação, se distribuída, começa em1562; permanece não lida até consulta efetiva.
