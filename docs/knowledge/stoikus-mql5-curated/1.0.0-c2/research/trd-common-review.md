# TRD — Partes 1 e 4: caderno de leitura analítica

Estado: EM LEITURA; páginas físicas do PDF. Documento de pesquisa, sem alteração de produto. A extração/índice não constitui leitura. Só os intervalos explicitamente registrados abaixo foram lidos semanticamente. Todos os exemplos e diagnósticos estáticos: **NOT_RUN**. Não houve MT5, compilação EX5, backtest nem piloto nativo.

## Lote efetivamente lido: PDF 482–499 — globais do terminal (4.6)

Leitura do texto integral das páginas, contratos, exemplos e logs; a saída inicial foi truncada no meio, por isso 488–492 foram relidas integralmente em chamada separada. A página 482 também termina 4.5.17: `FileSelectDialog` exige três resultados (>0 escolha, ==0 cancelamento, <0 erro); testar somente zero preserva array antigo quando há erro. Isso é uma demonstração deliberada, não contrato adequado para produção.

### TRD-0194 — 4.6, PDF 482–499

Globais do terminal são armazenamento compartilhado externo ao programa, distinto de variáveis de escopo global da linguagem. Nome até 63 caracteres; valor somente `double`; qualquer programa/usuário pode ler, modificar ou apagar. Persistem via `gvariables.dat` entre sessões, salvo temporárias; expiram após quatro semanas sem leitura/escrita. Check/Time não renovam uso. Não são vinculadas a conta, perfil, símbolo ou magic. No tester são isoladas por agente/passagem e removidas ao final, portanto não fornecem comunicação entre agentes nem reproduzem automaticamente o estado do terminal real [TRD, 4.6, p.PDF 482–483]. Implicação proposta para os quatro programas Stoikus: namespace deve incluir identidade de domínio/conta/servidor e versão de esquema conforme o significado da chave, sem assumir isolamento pelo login; a identidade concreta usada pelo produto ainda precisa ser verificada no código. Não tratar esse canal como autoridade normativa nem autorização de operação. Eventos, buffers e objetos gráficos são alternativas citadas, com semânticas diferentes.

### TRD-0195 — 4.6.1, PDF 483–484 (continuação do exemplo na 485)

`GlobalVariableSet` cria/substitui e devolve `datetime` de modificação ou zero em falha; `Get(name)` devolve double e zero ambíguo, enquanto `Get(name,&value)` separa bool de payload. O exemplo `GlobalsRunCount` escolhe deliberadamente zero para ausência, converte para int e incrementa; primeiro log contém 4501, não uma leitura bem-sucedida de zero [TRD, 4.6.1, p.PDF 483–485]. Para estado de risco/latches do Stoikus, ausência, zero válido, erro e versão incompatível devem continuar distinguíveis. O contador read/modify/write desse exemplo não é atômico (demonstrado depois no próprio livro); não reutilizar como limite concorrente.

### TRD-0196 — 4.6.2, PDF 485 (continua 486)

`GlobalVariableCheck` bool e `GlobalVariableTime` datetime consultam existência/último uso sem renovar retenção. Leitura e modificação renovam. `GlobalsRunCheck` troca o nome da chave por `__FILE__`; o contador novo não é continuação do anterior [TRD, 4.6.2, p.PDF 485–486]. Heartbeat/freshness do Stoikus não pode ser inferido de `Time` sem saber quais programas leem a variável: observadores podem renovar a marca. Recomenda-se timestamp explícito do produtor como payload/protocolo, com unidade e relógio declarados, se tal requisito for aprovado.

### TRD-0197 — 4.6.3, PDF 486 (continua 487)

`Total` e `Name(index)` enumeram índices de 0 a total−1; ordem não definida. Nome inválido devolve NULL e erro. Exemplo consulta um milhão para provocar 4501 e depois imprime valores [TRD, 4.6.3, p.PDF 486–487]. Listagem tem efeito colateral de leitura se também obtém valores. Em diagnóstico do Stoikus, não usar posição na lista como ID estável, nem supor snapshot consistente sob mutações de outros programas.

### TRD-0198 — 4.6.4, PDF 487–488

`GlobalVariableDel` devolve bool; `GlobalVariablesDeleteAll(prefix=NULL,limit=0)` remove pela conjunção prefixo e data de uso anterior ao limite; filtros vazios/zero ampliam seleção. Sem parâmetros apaga todas. O exemplo usa nomes inexistentes e depois prefixo `GlobalsRun`; o retorno é contagem, zero pode significar nenhuma correspondência [TRD, 4.6.4, p.PDF 487–488]. Limpeza de chaves Stoikus deve ter namespace delimitado e escopo explícito; comando genérico não serve para reset seguro do sistema. Não foi executado nenhum reset.

### TRD-0199 — 4.6.5, PDF 488 (continua 489)

`GlobalVariableTemp(name)` cria com zero e duração da sessão; chave existente não é convertida. Não há API para consultar se é temporária e a UI não cria temporárias, embora as mostre [TRD, 4.6.5, p.PDF 488–489]. Distinguir cache/contador de sessão de estado que precisa sobreviver a reinício. Colisão com chave persistente prévia pode invalidar uma suposição de ciclo de vida; a tentativa de criação deve ser interpretada, não ignorada.

### TRD-0200 — 4.6.6, PDF 489–498 (continua 499)

O contraexemplo `AlreadyRunning` faz Check seguido de Set: duas threads passam antes da criação. Scripts/EAs/serviços possuem threads próprias; indicadores compartilham thread por símbolo+timeframe, não globalmente [TRD, 4.6.6, p.PDF 489–491]. `GlobalVariableSetOnCondition(name,value,precondition)` opera atomicamente em UMA chave existente; não cria chave, compara e troca como operação indivisível. Falha não renova data de uso se a precondição não casar. O pseudocódigo `GlobalVariableZetOnCondition` é expressamente irrealizável em MQL puro; não equivaler Check/Get/Set a CAS.

`GlobalsNoCondition` cria temporária, rejeita contador negativo, limita quantidade e introduz Delay antes de Set para expor corrida. As duas cópias admitem contador antigo zero e ambas executam, mesmo com limit=1; na saída ocorre underflow. `GlobalsWithCondition` limita retries=5 e refaz leitura quando CAS falha; admissão e decremento são ambos alterados. O exemplo de serviços facilita partida em grupo; `Add service` inicia imediatamente, portanto o tutorial manda parar instâncias antes do ensaio. O log fora de ordem não ordena a execução das primitivas: linhas de Temp false aparecem antes da linha Temp true que criou a chave [TRD, 4.6.6, p.PDF 492–499]. Esta observação serve à análise forense de logs Stoikus: ordem visual interprogramas não prova relação causal completa.

O livro diferencia tentativa única com retorno ao trabalho, retry limitado e espera indefinida com `IsStopped`+Sleep. A última pode criar deadlock quando recursos múltiplos são adquiridos em ordens diferentes [TRD, 4.6.6, p.PDF 496–497]. Para Monitor event-driven, o desenho preferível é reagendar tentativa limitada sem bloquear handler; trata-se de aplicação proposta, não confirmação de implementação.

**Limites estáticos dos exemplos (NOT_RUN):** CAS de uma chave não é transação entre todas as chaves dos quatro programas. `__FILE__` não diferencia conta nem versão. Temporária não implica posse nem lease; falha abrupta pode deixar contagem desatualizada até terminal reiniciar. Usuário pode apagar/alterar chave; o próprio livro rejeita isso como proteção forte de licença. Na admissão, `if(count == limit || retry == maxRetries)` não expressa claramente o estado de CAS bem-sucedido; contador acima de limit por interferência manual pode sair do loop e ultrapassar a checagem de igualdade. A proteção inicial só rejeita negativos. Na saída, a mensagem `Stopped copy` pode ser emitida após esgotar retries, embora nenhuma troca final tenha sucesso, pois o teste só considera `last<=0`. Esses são pontos estáticos para exemplo robusto com flag explícita `acquired/released` e tratamento de `count>=limit`; não são defeitos demonstrados no produto Stoikus. Logs do livro mostram 4501 até para falha de condição; não tomar o rótulo do log como prova de ausência sem nova consulta/erro contextual. O teste nativo precisa separar ausência, concorrência e interferência.

### TRD-0201 — 4.6.7, PDF 499

`GlobalVariablesFlush()` força gravação das persistentes, retorna void; temporárias são excluídas. Só observar alteração do arquivo quando houve mudanças ou leituras desde a última gravação (acesso muda metadata). Ajuda contra perda no encerramento anormal; não equivale a transação, confirmação de fsync verificável ou recuperação completa [TRD, 4.6.7, p.PDF 499]. Persistência e atomicidade são requisitos separados no Stoikus. Nenhum arquivo global foi inspecionado ou alterado nesta pesquisa.

## Lote efetivamente lido: PDF 500–512 — relógios (4.7)

### TRD-0202 — 4.7, PDF 500–512

As páginas distinguem coordenada absoluta `datetime`, calendários/campos `MqlDateTime` e duração em contadores. Relógio local, UTC calculado e relógio de servidor não têm mesma fonte nem comportamento [TRD, 4.7, p.PDF 500–502]. Isso exige no manual Stoikus um contrato por timestamp: origem, unidade, validade, uso e comportamento em ausência de tick; não um único helper chamado genericamente "agora".

### TRD-0203 — 4.7.1, PDF 502–504; continuação e log 505

`TimeLocal` segue sistema e DST; `TimeCurrent` é último tick entre símbolos do Market Watch, exceto em `OnTick`, onde se refere ao tick processado. Sem tick, pode ficar parado até fim de semana inteiro. `TimeTradeServer` é estimativa que avança a partir do relógio local; no tester coincide com `TimeCurrent` [TRD, 4.7.1, p.PDF 502–505]. Logo não chamar `TimeCurrent` de relógio UTC nem usar avanço como prova de conexão/cotação fresca. Monitor por timer precisa observar freshness de dados separadamente da hora de agenda.

`TimeTradeServerExact` mantém dois pares local/servidor e só atualiza offset em segundos quando diferenças sucessivas coincidem e servidor avançou. Primeira chamada devolve zero. O texto compara isso com aproximação nativa por fuso horário inteiro [TRD, 4.7.1, p.PDF 503–505]. **Limite estático NOT_RUN:** o nome Exact não certifica precisão: antes de aprender diferença estável, `shiftInSeconds` permanece zero e chamadas seguintes podem devolver hora local; desajuste/reinício do relógio local ou servidor congelado conserva offset antigo. É estimador didático que precisa validade explícita, não substituto automático para tempo de política Stoikus. A descrição específica da aproximação nativa é a do livro desta edição, a validar contra build-alvo antes de transformá-la em dependência.

### TRD-0204 — 4.7.2, PDF 505–510; conclusão 511

`TimeDaylightSavings` usa configuração SO e devolve correção local, com sinal negativo ao adiantar uma hora. Não informa DST do broker. `TimeSummer` tenta inferi-lo por distribuição das primeiras barras H1 de domingo/segunda no último ano, CopyTime, `hours[24]`, skip de 48 barras, máximos e limiar de 13 semanas. O próprio texto admite método empírico, semanas extraordinárias, `TODO` de checar semanas anteriores e exemplo real incompatível por uma hora com inferência [TRD, 4.7.2, p.PDF 505–511].

Limitações estáticas **NOT_RUN**: 365 dias não é um ano civil exato em todo caso; faltas de histórico, feriados, horário de abertura do broker e símbolos não Forex invalidam heurística. `supportDST` é declarado em `ServerTime`, mas o fragmento mostrado não o atribui, deixando falso com `{}`. O print descreve UTC com sinal de exibição, enquanto `offsetGMT` usa correção de sinal inverso para converter a UTC; documentar essa distinção para não inverter duas vezes. Sentinela `-INT_MAX` de erro não é offset válido. Não generalizar UTC±12/horas inteiras como cobertura de todos os fusos do mundo. Para Stoikus, calendário/fuso operacional e dia de risco devem vir de contrato explícito e dados verificados; esse exemplo não autoriza deduzir regras do banco/calculadora nem comportamento do produto.

### TRD-0205 — 4.7.3, PDF 511

`TimeGMT = TimeLocal + TimeGMTOffset`; fonte é SO, sem consulta externa. UTC depende de relógio e fuso locais corretos. Offset GMT é UTC−local, em segundos (UTC+2 → −7200), incorporando DST. No tester TimeLocal/TimeGMT/TimeCurrent coincidem [TRD, 4.7, p.PDF 501; 4.7.3, p.PDF 511]. Testes de agenda devem injetar relógios/fontes e incluir offset/DST divergentes; backtest padrão sozinho não exercita isso.

### TRD-0206 — 4.7.4, PDF 511; contrato na 512

`Sleep(int milliseconds)` suspende execução; recomendado em scripts/serviços, timers/OnTimer para EAs; proibido em indicadores por bloquear thread de interface. Interrupção de usuário encerra Sleep antecipadamente (checagem de parada em torno de 100ms) e código deve respeitar `IsStopped` [TRD, 4.7.4, p.PDF 511–512]. Para Monitor event-driven, espera bloqueante não é agendamento robusto. A duração requisitada não prova tempo decorrido nem entrega de evento.

### TRD-0207 — 4.7.5, PDF 512; continuação ainda pendente 513

`GetTickCount`/`GetTickCount64` contam ms desde boot; granularidade SO citada ~10–15ms. uint faz wrap em ~49,7 dias; ulong evita esse horizonte operacional. `GetMicrosecondCount` conta µs desde início do programa, não boot [TRD, 4.7.5, p.PDF 512]. Duração é diferente de tempo de calendário e não deve persistir sem identidade da sessão. Exemplo TimeCount continua na página seguinte, ainda não lida neste ponto do caderno.

## Lote efetivamente lido: PDF 513–528 — interação (4.8) e fim de 4.7.5

Complemento TRD-0207, PDF 513: `TimeCount` mede Sleep de 1s em loop até `GetTickCount() < startMs+5000`; log exemplar mostra 5460ms, não exatamente 5000. **NOT_RUN:** soma de deadline uint pode fazer wrap; exemplo não trata isso e tampouco testa `IsStopped` na condição do loop. Usar diferença corretamente tipada ou contador64 e parada explícita nos candidatos; não copiar tutorial como timeout de produção.

### TRD-0208 — 4.8, PDF 513–528

Entrada `input` pertence à inicialização; mudança de propriedades implica reinicialização (com particularidades por tipo de programa tratadas adiante). Interfaces/logs são canais distintos de protocolos de integração. Isso importa ao Stoikus: aviso visual, confirmação de leitura humana e mudança efetiva de estado não são um único evento.

### TRD-0209 — 4.8.1, PDF 514–517; continuação 518

Print/PrintFormat são enviados a Experts independentemente de ser EA/indicador/script; logs MQL5/Logs são diferentes de Logs do terminal. Exibição de alto volume omite linhas para desempenho, e gravação em disco é cacheada; View/Open pode forçar descarga. Logo screenshot e arquivo ainda não descarregado podem divergir sem provar ausência do evento [TRD, 4.8.1, p.PDF 514]. Limite de 64 argumentos; só tipos embutidos, arrays por ArrayPrint ou laço; conversões de bool, datas, enum, chars e color diferem. Double até 16 dígitos significativos, float 7 casas; saída formatada deve ser explícita em evidências numéricas.

Em otimização Print/PrintFormat ficam sem saída visível, mas argumentos ainda são avaliados [TRD, 4.8.1, p.PDF 515,518]. Não colocar mudanças de estado em expressão de log nem inferir que silenciar log elimina custo computacional. `OutputStream` ilustra operador `<<`, acumulação e autoargumento para flush; versão impressa é expressamente simplificada. Acrescenta delimitador após cada item, inclusive o último; versão completa tem regras para arrays/cores e precisão [TRD, 4.8.1, p.PDF 516–518]. O manual pode propor logs estruturados com versão, run/session ID, origem de relógio, sequencial e resultado; o livro não confirma que Stoikus os implemente.

### TRD-0210 — 4.8.2, PDF 518; contrato na 519

Alert programático é diferente da aba de alertas configurados manualmente. Abre janela não modal, som e linha de log; argumentos seguem Print. Janela fechada só reaparece por novo alerta; o livro recomenda limitar frequência [TRD, 4.8.2, p.PDF 518–519]. Para Monitor, limitar repetição por transição/estado e distinguir delivery local de reconhecimento; janela/som não garantem ciência do operador.

### TRD-0211 — 4.8.3, PDF 519–522; conclusão 523

`Comment` é um único slot por gráfico, substituído por cada chamada de qualquer programa, removido com string vazia; teto total 2045 caracteres, linhas por newline, consultável por CHART_COMMENT. Não é histórico persistente nem UI multiprodutor. `Comments` cria ring buffer de strings, cursor módulo capacity, inverte entradas de bloco e ordem de exibição para novos primeiro. `MultiComment`/`ChronoComment` encapsulam instâncias estáticas; demo limpa a cada dez iterações e adiciona detalhes a cada três [TRD, 4.8.3, p.PDF 519–523]. **NOT_RUN:** constructor mostrado não valida capacity>0 nem retorno de ArrayResize; add usa `%capacity` e indexação, então zero/negativo não é configuração segura. Buffer limita linhas, não 2045 caracteres; texto ainda pode ser truncado. `clear` zera contadores e UI; isolamento de instâncias não impede disputa pelo mesmo slot. Objetos gráficos são recomendados para colunas/cor/interação. Evitar usar Comment como prova de integridade ou canal persistente do Stoikus.

### TRD-0212 — 4.8.4, PDF 523–527

`MessageBox(message,caption=NULL,flags=0)` combina um conjunto de botões, um ícone e default por OR; retorna IDs explícitos, Cancel via ESC somente quando disponível. Caption NULL usa nome do programa. A chamada suspende o programa aguardando resposta, é proibida para indicadores e serviços; no tester retorna zero sem exibir [TRD, 4.8.4, p.PDF 523–527]. **Inconsistência editorial:** p523 chama janela de modeless; p525 descreve espera bloqueante na chamada. O manual deve privilegiar semântica concreta de suspensão. `MB_HELP`/quarto default não fornecem tecnologia de help MQL completa. Demo oferece enums para os grupos e cast do retorno. Candidato que pede confirmação precisa tratar 0 no tester/erro, IDYES, IDNO e IDCANCEL separadamente; nenhum default/retorno desconhecido pode equivaler a armar Supervisor. A pesquisa não cria esse fluxo nem autoriza armamento.

### TRD-0213 — 4.8.5, PDF 528

`PlaySound` aceita WAV em Sounds da instalação, caminho relativo, caminho MQL5 com barra inicial e recursos embutidos; novo som interrompe anterior, NULL cancela. Async: devolve controle sem esperar término. Retorno true atesta arquivo localizado, até para conteúdo não reproduzível; não atesta som audível. Não executado no tester [TRD, 4.8.5, p.PDF 528]. Distribuição como resource evita dependência de arquivo local, mas é proposta de empacotamento; teste de alerta nativo/manual deve continuar separado de bool da API.

## Lotes efetivamente lidos: PDF 529–559 e 560–573 — ambiente (4.9)

Continuação 4.8.5 na 529 foi lida: demo `new.txt` existente retorna true sem som; WAV ausente retorna false/5019; som válido retorna imediatamente. Confirma empiricamente apenas no log impresso do livro, não execução desta pesquisa.

### TRD-0214 — 4.9, PDF 529–573

Ambiente é terminal/test agent + módulo MQL; APIs separam propriedades terminal e programa, por tipo de retorno. Muitas decisões exigem combinar níveis; compartimento genérico `Integer` inclui flags/enums, portanto não interpretar todo retorno como número cardinal. Tester admite EAs e indicadores, não scripts/serviços [TRD, 4.9, p.PDF 529–530]. Harness Stoikus precisa registrar qual programa executou, modo e build; ensaio em script não prova eventos e restrições do Monitor EA.

### TRD-0215 — 4.9.1, PDF 530–533; fechamento 534

`Environment` enumera propriedades com `EnumToArray` e wrapper por API: MQL não aceita ponteiro direto para função embutida, então `Binding<E,R>` associa enum, retorno e ponteiro a wrapper MQL. `process` registra resultado e captura `_LastError` imediatamente antes de converter enum/imprimir. Ordem de avaliação de argumentos não é garantida; uma linha que mistura chamada e consulta de erro pode ler erro anterior. O próprio `EnumToString` pode sobrescrever erro [TRD, 4.9.1, p.PDF 530–533]. Número ordinal da impressão não é valor do enum. A pesquisa pode propor snapshot de ambiente como metadado do piloto, preservando limites da enumeração em 0..USHORT_MAX e mudanças futuras de plataforma. Log contém build2988 e deve ser reconhecido como exemplo histórico da fonte. `_IsX64`/TERMINAL_X64 têm origem compatibilidade; não prova de ambiente atual do usuário.

### TRD-0216 — 4.9.2, PDF 534–535 (título seguinte na mesma faixa do outline)

`TERMINAL_BUILD` é versão em execução; `__MQLBUILD__`/`__MQL5BUILD__` são compilador. Não basta um número "build" no recibo: binário e runtime podem ter origens diferentes. Exemplo de branch >=3000 demonstra feature gating, sem recomendar esse limiar para Stoikus [TRD, 4.9.2, p.PDF 534].

### TRD-0217 — 4.9.3, PDF 534–535

MQL_PROGRAM_TYPE distingue script1, EA2, indicador4, serviço5; enum não é sequência sem lacunas. Funções têm permissões por tipo (OrderCalcMargin não em indicador). MQL_LICENSE_TYPE diz respeito ao EX5 que consulta: numa biblioteca informa licença da própria biblioteca, enquanto nome programa pode se referir ao host, como explicado depois. Demo de serviço sem loop encerra imediatamente e pode ser iniciado pelo debugger [TRD, 4.9.3, p.PDF 534–535]. Licença/ativação Market descrita no livro não é norma JP Wealth nem licença inferida de Stoikus.

### TRD-0218 — 4.9.4, PDF 536–537; continuação 538

Flags debug/profiler/tester/forward/optimization/visual/frame/VPS têm combinações: forward/optimization/visual implicam tester; frame exclui tester, optimization exclui visual, profiler exclui debug. Debug/profiling recompilam especiais maiores/mais lentos; runtime MQL_DEBUG não é modo de compilação: binário debug iniciado normalmente pode ter flag runtime zero. `_DEBUG/_RELEASE` são outra dimensão [TRD, 4.9.4, p.PDF 536–538]. Validação e performance devem declarar configuração do executável e modo de execução. Receber logs de debugger não prova binário release. O exemplo script não pode exercitar tester. Nenhuma recompilação foi feita nesta pesquisa.

### TRD-0219 — 4.9.5, PDF 538–540; fechamento 541

Trading permission deve combinar terminal/programa e, adiante, regras de instrumento/sessões/conta. Permissão DLL do terminal atua como default; a individual pode ser autorizada para módulo mesmo sem default global. DLL vinculada pode impedir sequer iniciar, logo diagnóstico externo sem dependência pode ser necessário. Scripts com/sem `script_show_inputs` têm fluxos diferentes. Indicador continua proibido de funções de trading mesmo com flags true. Flags email/FTP/push expressam configuração, não entrega [TRD, 4.9.5, p.PDF 538–541].

`Permissions::isTradeEnabled(symbol,session)` é deliberadamente draft com TODO; recebe argumentos ainda não usados e retorna só AND de duas flags. Não confundir com autorização completa. No tester essas flags de trade são true conforme o texto, logo ensaio do cenário proibido exige outra estratégia. A afirmação do livro "tester does not allow ... DLL dependencies" é excessivamente geral se extrapolada para todos os agentes/modos; validar no capítulo específico REF e plataforma-alvo antes de incorporar (não assumir limite de cloud idêntico ao local). Supervisor opcional não é autorizado por flags técnicas; Monitor não opera. Separar habilitação técnica, política do produto e aprovação humana.

### TRD-0220 — 4.9.6, PDF 541–542

TERMINAL_CONNECTED é conexão ao servidor, não sincronia de símbolo/série; completar com SymbolIsSynchronized/SeriesInfoInteger(SERIES_SYNCHRONIZED). Ping em µs; flags community account/connection/MQID têm significados separados. TERMINAL_RETRANSMISSION é percentual global SO para todos aplicativos, consultado ~uma vez/min, não métrica exclusivamente MT5. Community balance pode falhar sem conexão [TRD, 4.9.6, p.PDF 541–542]. Candidato Monitor deve diferenciar rede, freshness, disponibilidade de histórico e capacidade de notificar. Não interpretar ping como SLA nem como prova de envio/recepção de alerta.

### TRD-0221 — 4.9.7, PDF 543; exemplo e análise 544

MQL_MEMORY_LIMIT usa KB; usados/total/available/physical e disco usam MB; MQL_HANDLES_USED conta objetos de classes. OPENCL_SUPPORT é versão codificada, zero ausência. Demo aloca uchar10MB e compara escopos MQL/terminal; aumento terminal pode ser menor por reservas já existentes [TRD, 4.9.7, p.PDF 543–544]. O texto diz igualdade aproximada de limite MQL e total terminal sem uniformizar unidades; manual deve converter. Valores são observações mutáveis e limites de nuvem/VPS podem ser menores. Não transformar número de cores em autorização para paralelismo ilimitado nem suporte OpenCL em uso atual do Stoikus.

### TRD-0222 — 4.9.8, PDF 544–545; continuação 546

DPI permite cm2pixels via divisão por2,54; virtual screen delimita conjunto de monitores, coordenadas podem ser negativas. Coordenadas da janela terminal podem refletir tamanho restaurado em vez de maximizado; gráfico exige API própria [TRD, 4.9.8, p.PDF 544–546]. Testes de painel precisam cobrir escala/múltiplos monitores; screenshot sozinho não garante medidas corretas em outras configurações. Exemplo não implementa UI Stoikus.

### TRD-0223 — 4.9.9, PDF 546–547

TERMINAL_PATH instalação, DATA_PATH instância, COMMONDATA_PATH compartilhado entre terminais. MQL_PROGRAM_NAME numa biblioteca retorna nome do programa principal, ao contrário de consulta de licença descrita em4.9.3. Não montar caminhos de dados a partir do executável nem usar nome como identidade universal [TRD, 4.9.9, p.PDF 546–547]. Recibo do piloto deve apontar sandbox/instância usados; não comprova instalação real só porque arquivo está no repositório.

### TRD-0224 — 4.9.10, PDF 548–557 (intervalo duplicado no outline)

Conteúdo específico 4.9.10 ocupa começo da548: MAXBARS limita exibição, não garante quantidade disponível nem representa todo histórico; SERIES_BARS_COUNT pode ser maior, dados efetivos menores. CODEPAGE reflete idioma terminal. Limite influencia RAM [TRD, 4.9.10, p.PDF 548]. A faixa548–557 é compartilhada pelo índice com4.9.11; não significa leitura dupla nem que licenciamento seja conteúdo de4.9.10. Não usar MAXBARS como prova de histórico sincronizado/completo.

### TRD-0225 — 4.9.11, PDF 548–557 (mesma faixa de TRD-0224)

`EnvSignature` concatena nome, pepper e valor de propriedades, inclui secret, SHA256 e Base64; fingerprint e token de validação são etapas diferentes. Enum/wrapper `append`, `emit`, `check`, `I_AM_DEVELOPER` e MyEnvSignature mostram ligação de processo a ambiente. Propriedades comuns (resolução/RAM) coincidem entre máquinas; tabela é distribuição ilustrativa, não unicidade comprovada. Salt randômico é sugerido, não implementado. Pepper por cliente e secret estão no binário; texto manda retirar ramo gerador de validação do produto [TRD, 4.9.11, p.PDF 548–557]. Mudança script→serviço altera hash porque MQL_PROGRAM_TYPE entrou nos dados.

**Análise estática NOT_RUN:** hash não autentica origem por si, Base64 não criptografa e fingerprint de propriedades mutáveis não é ID de hardware estável. O comentário p554 "order is not important" só vale como liberdade de escolher ordem fixa; concatenação muda hash quando ordem muda. Política precisa canonicalizar campos, separadores/escapes, encoding e versão. `append` sempre true não prova leitura bem-sucedida de propriedade; emit não testa retorno da última Base64. `StringToCharArray` pede count com StringLen em CP_UTF8: validar semântica para não truncar caracteres multibyte em caminhos/idioma não ASCII. Mais grave no snippet p556: calcula `signature` local do ambiente mas passa `Signature` input a `env.check`, enquanto no modo cliente essa constante pode ficar vazia. A divergência de capitalização não é inocente em MQL; precisa confrontar fonte anexada antes de reutilizar, e não se deve chamar logs didáticos de prova do código fragmentado. Não é uma descoberta de vulnerabilidade no Stoikus; nenhuma mudança de licenciamento foi proposta/implementada. Manual deve usar assinatura/hash para integridade/proveniência de artefatos com ameaça definida, sem transplantar esse sistema de proteção didático.

### TRD-0226 — 4.9.12, PDF 558–559

Key state retorna palavra de2bytes: bit0 estado/toggle descrito; bit0x8000 pressionada. Apenas controles enumerados; chars/funções exigem CHARTEVENT_KEYDOWN em OnChartEvent para EA/indicador. Não funciona em gráfico inativo nem em indicadores dependentes criados iCustom/IndicatorCreate, mesmo ChartIndicatorAdd. Não existe keyboard monitor permanente por essa API [TRD, 4.9.12, p.PDF 558–559]. Há inconsistência de log exemplar trocando SCRLOCK por CAPSLOCK. Não fundar comando crítico/aceite humano do Stoikus em polling de tecla fora do foco; eventos e confirmação de estado precisam contrato próprio.

### TRD-0227 — 4.9.13, PDF 560–561; tabela completa 562

IsStopped/_StopFlag devem ser observados em laços longos. Há prazo aproximado de3s para terminar antes de remoção forçada; instruções pós-loop podem não acontecer se ignora parada. Demo EnvStop busca primos, limpa Comment e imprime contagem na saída cooperativa. **NOT_RUN:** `isPrime` mostrado aceita1 (`n<1` rejeita só0/negativos; `n<=3` retorna true), logo não é um teste matemático de referência. `Sleep(10)` não substitui condição de parada. UninitializeReason/_UninitReason e parâmetro OnDeinit distinguem remoção, recompilação, símbolo/período, parâmetros, conta/reconexão, template, initfail, fechamento [TRD, 4.9.13, p.PDF 560–562]. Diferenciar reinicialização de primeira ativação, e não assumir limpeza garantida diante de crash/kill. Tabela é fonte técnica; retenção/retomada Stoikus devem ser verificadas no produto.

### TRD-0228 — 4.9.14, PDF 562–563; conclusão 564

TerminalClose envia pedido, bool true significa aceito, não processo já encerrado; código deve fechar recursos e devolver controle. SetReturnError define exitcode futuro, inclusive encerramento normal ou crítico; última definição entre programas vence. EnvClose +envrun.bat ilustra coleta %ERRORLEVEL% [TRD, 4.9.14, p.PDF 562–564]. Não usar exitcode global do terminal como único resultado de cada caso de harness; correlação por caso e recibos separados são necessários. Nenhum comando de fechamento/retorno foi executado. Para piloto candidato, teste de encerramento exige instância dedicada, sem presumir autorização para fechar terminal de trabalho.

### TRD-0229 — 4.9.15, PDF 564–565

Compilar não elimina runtime errors. Zero divide, index out of range e pointer inválido podem abortar; GetLastError não é captura de exceção nem reseta valor. Ações bem-sucedidas também não limpam erro; ResetLastError antes da ação e snapshot imediatamente depois isolam proveniência [TRD, 4.9.15, p.PDF 564–565]. PRTF(A)→ResultPrint guarda snapshot, imprime e reseta depois. **Limite estático NOT_RUN:** sequência PRTF é útil se nada entre chamadas produz erro; primeira chamada pode herdar erro preexistente, pois macro não faz reset antes de avaliar A. O texto afirma correspondência na sequência mas o contrato precisa explicitar essa precondição. Para wrapper original de manual, capturar retorno e erro em statements separados, sem avaliação múltipla/efeitos embutidos. Não misturar erro técnico com retcode operacional/trade sem contexto.

### TRD-0230 — 4.9.16, PDF 566–570; conclusão 571

SetUserError(ushort) grava65536+code; não é exceção/unwind. Exemplo Matrix customizada (distinta de matrix nativa) emite EMPTY, SINGULAR e NOT_SQUARE; construtor não consegue deixar de criar objeto, exige validade separada. inverse retorna matriz zero e flag em caso singular; zero como payload não basta. Produto A×inverse com zeros assinados mostra arredondamento, não igualdade binária [TRD, 4.9.16, p.PDF 566–571]. **NOT_RUN:** teste `fabs(det)>DBL_EPSILON` é tolerância absoluta sem escala/condicionamento; não garante estabilidade em todas matrizes. Flags globais do programa podem ser sobrescritas por impressão/conversão posterior; snapshot continua necessário. Calibrar tolerâncias por domínio, escala e objetivo em comparação de fórmula Stoikus, sem alterar fórmula normativa.

### TRD-0231 — 4.9.17, PDF 571

DebugBreak só pausa se iniciado em modo debug; execução normal e profiling ignoram. Não é mecanismo de pausa operacional, autorização humana ou fail-stop do produto [TRD, 4.9.17, p.PDF 571].

### TRD-0232 — 4.9.18, PDF 571; tabela 572

Predefinidas gerais _LastError/_StopFlag/_UninitReason/_RandomSeed/_IsX64; contexto gráfico acrescenta _Symbol/_Period/_Digits/_Point e _AppliedTo para indicadores. Propriedades do gráfico não descrevem automaticamente outro símbolo em sistema multissímbolo [TRD, 4.9.18, p.PDF 571–572]. Não usar _Digits/_Point do chart como unidade de qualquer instrumento consultado pelo Monitor.

### TRD-0233 — 4.9.19, PDF 572–573; frase final segue 574 ainda pendente

CHARTS_MAX100, clrNONE−1, EMPTY_VALUE=DBL_MAX, INVALID_HANDLE−1, NULL0, WHOLE_ARRAY−1 e WRONG_VALUE−1 têm semânticas distintas apesar de valores coincidentes. EMPTY_VALUE é vazio de buffer configurável, não NaN e não zero; não deve entrar como preço em conta numérica. WHOLE_ARRAY vai da posição atual ao final, não necessariamente desde índice0. IS_DEBUG_MODE/IS_PROFILE_MODE dependem compilação especial e podem condicionar profiling [TRD, 4.9.19, p.PDF 572–573]. Última frase de573 continua574; não declarar seção encerrada até leitura dessa continuação.

## Lote efetivamente lido: PDF 574–610 — matrizes/vetores (4.10)

A abertura da574 conclui4.9.19: debug build pode rodar sem debugger; flags de compilação e runtime continuam dimensões distintas. Assim TRD-0233 está completo quanto ao texto, incluindo continuação574.

### TRD-0234 — 4.10, PDF 574–610

API nativa de linear algebra, distinta da classe Matrix didática da4.9.16. O livro avisa que API estava em evolução e apresenta visão breve, exigindo documentação detalhada e conhecimento matemático. Isso é pesquisa futura para Stoikus, cujo contexto aprovado não contém ML; não adicionar inferência, dependência Python/OpenCL/ONNX nem alterar fórmula normativa com base nesses exemplos.

### TRD-0235 — 4.10.1, PDF 574–575; continuação576

matrix/vector suportam double(default), float, complex com sufixos f/c e notação parametrizada. Vetor não é subtipo de matriz; orientação é implícita conforme posição em produto; não há cast automático entre famílias/precisões como substituto de transferência explícita. Índices começam0; eixo e linhas/colunas devem ser declarados por operação, evitando transposição inadvertida [TRD, 4.10.1, p.PDF 574–576]. Print aceita objetos nativos, diferente de arrays comuns de4.8.1.

### TRD-0236 — 4.10.2, PDF 576–578; exemplo579

Declaração vazia não aloca dados; construtor com dimensões aloca sem inicializar. Literal infere dimensões; Eye/Tri/Identity/Ones/Zeros/Full criam padrões, Identity não estático também reconfigura. Init recebe referência de função inicializadora (não typedef pointer nem string) e argumentos extras; sem regra, novo conteúdo não é garantido. Demo Fill10→Init4×6 exibe resíduos [TRD, 4.10.2, p.PDF 576–579]. Em fixtures, sempre inicializar todas posições antes de leitura; um log com zero casual não define contrato. O snippet `vector<float> vector_v2=vector_v1` usa fonte double e contradiz comentário de mesma família; tratar como possível erro didático/extração, confrontar arquivo original antes de compilar. Os exemplos não foram compilados.

### TRD-0237 — 4.10.3, PDF 579–580; Swap581

Atribuição/Copy/Assign copiam; Assign também recebe arrays com conversão e resize, vetor→matriz de uma linha e matriz→vetor em ordem achatada. Swap troca buffers sem copiar e altera fontes/destinos; arrays devem ser dinâmicos e compatíveis com blocos de dimensões superiores [TRD, 4.10.3, p.PDF 579–581]. Ownership e ordem física importam para benchmark e protocolo. O texto afirma condição de divisibilidade com redação ambígua, mas exemplo [][2][3] aceita6/12/18: validar contrato na REF da build-alvo; não supor qualquer reshape seguro. Não usar Swap em fonte ainda necessária para comparação.

### TRD-0238 — 4.10.4, PDF 581; tabela582

CopyRates aceita faixa por posição+count, data+count ou datas; oldest fica no início. rates_mask seleciona campos, linhas seguem ordem enum, não ordem de expressão OR. Vetor admite só um campo; multi-field dá erro [TRD, 4.10.4, p.PDF 581–582]. Define contrato claro para dataset: linhas por campos, colunas por tempo. Isso é diferente de timeseries com índice0 recente e precisa teste explícito antes de comparar séries de Monitor.

### TRD-0239 — 4.10.5, PDF 582; tabela583

CopyTicks/Range recebem timestamps em ms, distintos de datetime em segundos. Flags de seleção INFO/TRADE/ALL e campos TIME_MS/BID/ASK/LAST/VOLUME/FLAGS têm papéis diferentes; matriz pode conter vários campos ordenados por enum, vetor só um [TRD, 4.10.5, p.PDF 582–583]. A repetição da assinatura matrix CopyTicksRange no texto aparenta omissão da versão vector; não usar essa lista resumida como especificação exaustiva. Mais detalhes foram remetidos à parte5.

### TRD-0240 — 4.10.6, PDF 583; exemplos584

Operadores +−*/ entre objetos iguais são elementwise; `a*b` é Hadamard, NÃO produto linear algébrico. Com escalar opera em cada elemento; in-place altera original, binário cria resultado. MathSqrt aplica elemento a elemento; MathMod/MathPow aceitam segundo operando escalar ou compatível [TRD, 4.10.6, p.PDF 583–584]. Um candidato de teste deve distinguir Hadamard/MatMul por matriz não diagonal que produza respostas diferentes; nome genérico "multiplicar" gera ambiguidade.

### TRD-0241 — 4.10.7, PDF 584–587; conclusão588

Transpose; Row/Col/Diag extração/set; TriL/U; SwapRows/Cols; Flat; Reshape/Resize; Split; Compare/CompareByDigits; Sort e Clip compõem operações de estrutura/limite. Vetor não suporta split no resumo. Reshape pode alterar quantidade e exibir valores não inicializados quando cresce (exemplo3×5), ou truncar2×4; não é somente reinterpretar shape mantendo conteúdo válido [TRD, 4.10.7, p.PDF 584–588]. Row/Col em matriz existente não inserem/empurram, apenas substituem; em vazia criam shape derivado de índice/comprimento. Clip modifica dado e não deve ocultar erro de validação de fórmula.

### TRD-0242 — 4.10.8, PDF 588–589; Outer590

MatMul obedece A[M,N]B[N,K]→C[M,K], incompatibilidade produz matriz vazia; ordem muda shape/resultado. Vetor×vetor MatMul equivale Dot; Outer faz matriz e troca de ordem troca shape. Power, Inner, Kron, CorrCoef, Cov, Correlate, Convolve são operações diferentes [TRD, 4.10.8, p.PDF 588–590]. Verificar shape e sucesso antes de usar resultado; vazio não é matriz zero nem sinal de perda zero. Correlação/covariância não representam causalidade nem autorização de estratégia.

### TRD-0243 — 4.10.9, PDF 590–591; log592

Cholesky/Eig/EigVals/LU/LUP/QR/SVD devolvem bool e outputs por referência. Exemplo SVD de matriz−4..4, decompõe U,V,singular_values e reconstrói U×Diag(S)×V.Transpose, Compare1e−9 dá0 diferenças; um singular value ~3,28e−17 ilustra posto/erro de ponto flutuante [TRD, 4.10.9, p.PDF 590–592]. Texto informal diz U*S*V, mas código aplica V transposta; manual deve manter convenção exata. Demo ignora bool de SVD; candidato deve tratar falha e comparar resíduo/escala, sem esperar igualdade bit-a-bit.

### TRD-0244 — 4.10.10, PDF 592; continuação/exemplo593

Estatísticas globais devolvem escalar; por eixo devolvem vetor. Lista inclui argmin/max, range, soma/prod/cumulativas, média/ponderada, std/var, quantis e RegressionMetric. MatrixStdPercentile usa O/C, calcula delta em pontos, arredonda e depois converte métricas a int; resize para10 só ocorre depois de criar delta [TRD, 4.10.10, p.PDF 592–593]. Não confundir dados impressos10barras com amostra1000. **NOT_RUN:** não checa CopyRates nem shape/quantidade antes de Row; `BarOffset=0` pode incluir barra corrente, e cast para int perde informação. Média/desvio não alteram regras normativas de risco. Identificar população/amostra e parâmetros por método antes de prometer equivalência numérica.

### TRD-0245 — 4.10.11, PDF 593–594; log595

Rows/Cols/Size usam ulong. Norm/Cond/Det/SLogDet(sign)/Rank/Trace/Spectrum são diagnósticos diferentes; log mostra posto4→3 quando zera elemento da identidade, Ones1×4 posto1, zeros4×1 posto0 [TRD, 4.10.11, p.PDF 593–595]. Condicionamento complementa teste de determinante absoluto; diagnóstico de falha numérica não pode ser deduzido apenas de forma quadrada. O capítulo é introdutório; nenhuma matriz de fórmula Stoikus foi alterada/testada.

### TRD-0246 — 4.10.12, PDF 595–600; conclusão601

Solve resolve AX=B, LstSq aproxima não quadradas/degeneradas; Inv quadrada não singular, PInv Moore–Penrose. MatrixForexBasket ajusta lotes sobre incrementos de preços desde primeira barra e target linear; CopyRates por símbolo, converte tick_value/tick_size, Col, Split passado/futuro, LstSq, balance e R²; Swap exporta para GraphPlot [TRD, 4.10.12, p.PDF 595–601].

**Limites explícitos da fonte:** índices iguais podem ter timestamps diferentes entre símbolos; sincronização omitida por simplicidade. Lotes negativos/fracionários são usados brutos; restrições mínimo/step não aplicadas e prejudicariam resultado real. Curva forward degrada; não é estratégia completa. **Análise estática NOT_RUN:** validar 0<=BarOffset<BarCount e amostras suficientes, CopyRates e tamanhos, tick_size não zero, erros de Split/LstSq, financiamento/spread/comissão/slippage, margem e lotes permitidos. Tick value consultado no presente não é modelo histórico completo para cada barra. Cast float na soma de balance reduz precisão desnecessariamente. Ajustar todos os símbolos ao mesmo calendário antes da álgebra; um R² alto sobre construção linear não certifica rentabilidade nem robustez de sistema. Não copiar esse sizing para calculadora JPW.

### TRD-0247 — 4.10.13, PDF 601–610

Activation/Derivative escrevem output e bool, Loss retorna escalar; funções não lineares permitem expressividade além de composição linear. Preditores/normalização/arquitetura e teste são essenciais; texto reconhece que ML não garante sucesso. BAM associa N deltas binários passados a M futuros, peso W=ΣOuter(Ai,Bi), feedback W.T com tanh até convergência/limite100. O exemplo usa Ask ticks, diferencia por Convolve{+1,−1}, Binary ±1, separa treino/teste, treina soma de Outer e testa Dot entre previsão e alvo. Contagem positiva significa maioria de acertos, não todos ticks; fórmula converte média de Dot para porcentagem. Resultado ilustrativo85,5% treino/58,5% futuro, podendo cair<50%; Sleep1s só aumenta probabilidade de ticks novos [TRD, 4.10.13, p.PDF 601–610].

**Limites estáticos NOT_RUN:** CopyTicks/Activation não são verificados no fragmento; número efetivo de ticks pode diferir do solicitado. Split de `ask2` usa TicksToLoad enquanto `ask1` usa n, inconsistente se carga parcial. TrainWeights/CheckWeights usam uint para `stop-sample+1-start`: pouca amostra pode fazer underflow e tentativa enorme de alocação; step0 divide por zero. Laço incrementa i por step mas indexa `start+i*step+j`, reaplicando start/step; só defaults start0/step1 mascaram isso. A contagem n por divisão inteira pode subalocar quando a quantidade de janelas não é múltipla de step; é preciso ceil coerente com laço. Zero pares deixa k0 e divisão average/k inválida. Faltam validação de shapes e distinção entre limite atingido e convergência. Linhas de treino/teste contíguas e sobrepostas dentro de cada conjunto são correlacionadas: 20 janelas não são20 ensaios independentes. Previsão de sinal de tick não inclui custos/lucro nem baseline; tratamento de delta zero em Binary é relevante e corpo não mostrado. Igualar todo BAM de camadas iguais a Hopfield é simplificação conceitual do livro, insuficiente como equivalência teórica geral. Matriz treinada aqui não é parte existente do Stoikus e não fundamenta alteração produtiva.

## Lote efetivamente lido: PDF 15–41 — introdução (Parte1)

### TRD-0002 — Parte1, PDF15–41

Distingue indicador, EA, script e serviço; MQL5 lembra C++ mas não é C++. Código roda no cliente, não se instala no servidor; serviço independe de gráfico. Caminhos data/install podem divergir e devem ser obtidos na instância, não presumidos [TRD, Parte1, p.PDF15–16]. Isso delimita o Monitor como EA de eventos mesmo sem trading, não serviço por rodar continuamente. Introdução serve ao contrato de ferramentas/evidência, sem ampliar fundamentos que Parte2/3 já cobrem.

### TRD-0003 —1.1, PDF16–18; fechamento19

MQ5/MQH são fontes; EX5 é executado. F7 compila principal e includes; zero erros é sucesso de compilação, warnings devem ser resolvidos, mas não equivalem a falha sintática. Navigator encontra binários nas pastas apropriadas [TRD,1.1,p.PDF16–19]. Fonte/lint/teste host não provam EX5 atualizado/carregado. Recibo candidato deve amarrar hash de fontes/includes, caminho/hash EX5, compilador e execução nativa; nenhum desses gates foi produzido por esta leitura.

### TRD-0004 —1.2, PDF19–21

Wizard cria stub de script OnStart, comentários não executam, #property codifica metadados; folders MQL5Book/p1 reduzem colisões. Arquivo vazio válido é exemplo de ferramenta, não comportamento funcional [TRD,1.2,p.PDF19–21]. Candidato Stoikus merece namespace/folder próprio e preservação de arquivos produtivos; criação por Wizard não comprova propósito ou teste.

### TRD-0005 —1.3, PDF22–23; continuação24

Bloco/função agrupam instruções; OnStart sem argumentos é entrada chamada pelo terminal e retorna imediatamente se vazio. Void indica ausência de valor retornado, não falta de efeitos; um programa sintaticamente correto pode não produzir resultado algum [TRD,1.3,p.PDF22–24]. Não transpor OnStart como loop de EA e não inferir teste aprovado só por log loaded/removed.

### TRD-0006 —1.4, PDF24–25; continuação26

HelloChart Print(Symbol()) mostra chamada aninhada e literal versus delimitador sintático. Falta de vírgula/semicolon produz mensagens às vezes posteriores/derivadas do primeiro erro. Print escreve Experts de todos tipos; log de carga/descarga é outro canal [TRD,1.4,p.PDF24–26]. Em build candidato, corrigir causa inicial e recompilar antes de interpretar cascata; logs de execução não substituem resultado semântico.

### TRD-0007 —1.5, PDF26–27

Greeting retorna string e deve respeitar tipo; return termina função. Introduz hora inteira como parâmetro. Exemplo prepara divisão em três faixas horárias convencionais, não regra de sessão de trading [TRD,1.5,p.PDF26–27]. Não importar esses intervalos0–8/8–16/16–24 como quatro programas diários JPW.

### TRD-0008 —1.6, PDF28

Tipo/nome/contexto definem variável; parâmetros pertencem à função. Identificadores não admitem espaços e não começam em número. Greeting(hour) inicialmente ignora parâmetro até etapas posteriores; stubs intermediários intencionais não são defeitos de produto [TRD,1.6,p.PDF28]. Para exemplos originais, dependência explícita por parâmetro permite testes sem inputs globais.

### TRD-0009 —1.7, PDF29–30; conclusão31

Array homogêneo de tamanhoN tem índices0..N−1; inicialização na definição difere de atribuições posteriores. Divisão inteira hour/8 indexa mensagens sob precondição hora0..23. GoodTime0 fixa0 e depois input substitui valor [TRD,1.7,p.PDF29–31]. Contrato de intervalo pertence à fronteira, não é garantido por possuir tipo int.

### TRD-0010 —1.8, PDF31–32; demonstração33

Input global com default pode ser alterado pelo usuário; EA/indicador retêm settings ao reiniciar, scripts não persistem como anexos ao gráfico. `script_show_inputs` é necessário para dialog de script, não basta ter input. GoodTime1 hora100 causa index12 e array out of range [TRD,1.8,p.PDF31–33]. Recibo de teste precisa configurações efetivamente aplicadas e nova sessão, não apenas defaults de fonte. Input não é validação de negócio.

### TRD-0011 —1.9, PDF33–36; conclusão37

Distingue erros compilação, runtime, projeto/hang e erro silencioso. Debug real usa chart online; tester só EA/indicador. Call stack/watch revela hour/8=12. Modulo24 corrige excesso positivo; valores−8 etc continuam negativos e−1..−7 truncam para índice0. Tutorial muda input para uint e rotula faixa, mas reconhece necessidade de validação real [TRD,1.9,p.PDF33–37]. **Limite estático NOT_RUN:** trocar tipo do input não transforma toda aritmética em não negativa nem valida0..23; a função ainda impressa `Greeting(int hour)` aceita chamada inválida e conversões unsigned/signed merecem checagem. Wrap/modulo são normalização permissiva, não rejeição de entrada inválida. Para risco/configuração Stoikus, não mascarar erro pela correção automática sem contrato. Função independente de input global facilita reuso/teste e é argumento central da conclusão37.

### TRD-0012 —1.10, PDF37–38; continuação39

Print, Comment e Alert têm públicos/visibilidade diferentes: status de chart e aviso com som não são log durável nem aceite humano. Versões com Comment/Alert não acompanham fontes do livro, são exercício a implementar [TRD,1.10,p.PDF37–39]. Não declarar esses arquivos verificados só porque screenshot aparece no PDF.

### TRD-0013 —1.11, PDF39–40; conclusão41

Whitespace livre só entre tokens; não dentro de identificador/número. Styler melhora legibilidade sem intenção semântica; `2 4` em vez de24 cria cascata e interpretação depende da intenção original, não apenas do compilador [TRD,1.11,p.PDF39–41]. Formatação não é correção de fórmula; diffs devem distinguir estilo de semântica e conferir artefato correto sem promover branch.

### TRD-0014 —1.12, PDF41

Miniresumo consolida evolução de stub a Greeting/input/debug. Não acrescenta API operacional. Figura de evolução existe na página; foi lido o texto extraído/legenda, sem inspeção visual da imagem. Essa limitação vale para screenshots/figuras desta pesquisa em geral: páginas completas de texto/código/tabelas extraídas foram analisadas, mas legibilidade visual e conteúdo exclusivamente embutido em imagens não foram auditados.
