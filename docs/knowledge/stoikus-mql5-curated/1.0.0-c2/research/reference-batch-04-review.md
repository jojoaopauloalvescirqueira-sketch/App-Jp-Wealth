# REF — leitura semântica batch 04 (PDF físico 895–1194)

Leitura real de todo o texto extraído destas 300 páginas, incluindo exemplos e saídas impressas. Fonte primária local: MQL5 Language REFERENCE.pdf, MetaQuotes, edição de metadados 2026-05-02, SHA-256 `9ae05ce748d23ce0de9b230fc6c7093a2af0adc3ce3544244a74e1c7d628d499`. As páginas físicas coincidem com números visíveis neste intervalo. Não é tradução integral nem auditoria visual. Exemplos: **NOT_RUN**; MT5, compilação EX5, operação de conta e benchmark nativos não executados.

O contexto atual Stoikus é o recebido em BRIEF.md: Monitor EA observacional, não negocia; Supervisor opcional sem autorização para armar. As aplicações indicadas são implicações técnicas ou propostas para manual/harness, não prova de que o produto implementa cada mecanismo. Nenhuma fórmula, regra JPW, limite, horário, estratégia ou recurso de negociação foi criado ou alterado. Nenhum produto/kit/piloto foi tocado.

A leitura normalizou apenas espaços na apresentação de alguns lotes; preservou o corpus original. Truncamentos de saída da ferramenta foram reparados por releitura menor: 903–916, 932–938, 962–967 e 895–902/917. Há linhas de código/comentários já cortadas à direita no próprio texto do PDF e palavras partidas/tabelas estreitas, especialmente 903–914; os contratos foram lidos, mas os exemplos não são fontes prontas para compilar. Figuras, screenshots e curvas não foram auditadas automaticamente.

## Notas por seção

### REF-0160 — Testing Statistics

[REF, REF-0160, p.PDF 895–896] (CONTINUATION_COMPLETED). Continuação: drawdown relativo máximo percentual e valor monetário naquele instante são estatísticas distintas. Profit factor sem perda bruta retorna DBL_MAX; recovery relaciona lucro a drawdown de saldo. Contagens de deals e trades não são intercambiáveis. Aplicação proposta ao harness; não define limite JPW.

### REF-0161 — Trade Constants

[REF, REF-0161, p.PDF 897–941] (READ_FULL_TEXT). Agrupador de constantes de histórico, ordens, posições, deals, operações, transações, DOM e sinais; contratos nos filhos.

### REF-0162 — History Database Properties

[REF, REF-0162, p.PDF 898–898] (READ_FULL_TEXT). SeriesInfoInteger distingue primeiras datas servidor/terminal/período, última abertura, número de barras e SERIES_SYNCHRONIZED. Monitor deve tratar disponibilidade/sincronização como estado, sem pressupor histórico completo.

### REF-0163 — Order Properties

[REF, REF-0163, p.PDF 899–916] (READ_FULL_TEXT). OrderGet/HistoryOrderGet separam inteiros, doubles e strings: ticket, estado, timestamps ms, magic/reason, position IDs, volume inicial/restante, preços e IDs externos. Estados incluem parcial e pedidos em andamento. FOK exige todo volume; IOC cancela saldo; RETURN continua saldo e é proibido em Market Execution; pendentes usam RETURN. BOC só limit/stop-limit e cancela execução imediata. Consultar flags do símbolo; validade GTC/day/specified/specified-day. Futuro executor apenas; monitor pode ler sem enviar.

### REF-0164 — Position Properties

[REF, REF-0164, p.PDF 917–920] (READ_FULL_TEXT). POSITION_IDENTIFIER liga ordens/deals por toda vida; ticket pode mudar por operações de serviço e reversão netting. Em reversão netting identificador persiste e ticket muda. Tipos buy/sell; propriedades incluem volume, SL/TP, swap/lucro e origem. A frase geral uma posição por símbolo deve ser contextualizada com netting, pois o próprio bloco trata hedging; não universalizar.

### REF-0165 — Deal Properties

[REF, REF-0165, p.PDF 921–924] (READ_FULL_TEXT). Deal é execução, diferente de ordem e posição. DEAL_ENTRY IN/OUT/INOUT/OUT_BY informa efeito, DEAL_REASON origem/SL/TP/SO/rollover/corporate action. Custos separados comissão/swap/fee e lucro. BUY/SELL_CANCELED pode zerar lucro e gerar ajuste de saldo. Monitor requer reconciliação e classificação das operações de saldo; não contar qualquer deal como trade.

### REF-0166 — Trade Operation Types

[REF, REF-0166, p.PDF 925–936] (READ_FULL_TEXT). Ações DEAL/PENDING/SLTP/MODIFY/REMOVE/CLOSE_BY têm exemplos que abrem, fecham e alteram ordens. Lots, magic, offsets, stop-level+50/150 e desvio são demonstrações, nunca regra JPW. Há diferenças entre exemplos de SL/TP e preços bid/ask; não transplantar scripts. Sem uso de execução no Monitor atual.

### REF-0167 — Trade Transaction Types

[REF, REF-0167, p.PDF 937–938] (READ_FULL_TEXT). Uma solicitação pode gerar muitas transações: ORDER, DEAL, HISTORY, POSITION e REQUEST. DEAL_UPDATE/DELETE e HISTORY_UPDATE/DELETE existem. POSITION descreve mudanças sem deal, não substitui DEAL_ADD para alterações decorrentes de execução. REQUEST exige analisar request/result, não campos genéricos da transação. Relevante ao desenho de observação/reconciliação.

### REF-0168 — Trade Orders in DOM

[REF, REF-0168, p.PDF 939–939] (READ_FULL_TEXT). MarketBookGet devolve fotografia MqlBookInfo, com BUY/SELL e variantes MARKET. DOM é disponibilidade de mercado, não prova de execução nem regra de sinal Stoikus. Pesquisa futura.

### REF-0169 — Signal Properties

[REF, REF-0169, p.PDF 940–941] (READ_FULL_TEXT). Propriedades de sinais e cópia incluem saldo/equity/ROI/drawdown, publicação/atualização, broker/currency, slippage, percentual, confirmação e permissão. Nenhuma autorização para copiar sinais; sem uso direto atual.

### REF-0170 — Named Constants

[REF, REF-0170, p.PDF 942–960] (READ_FULL_TEXT). Agrupador de macros, limites numéricos, desinicialização, ponteiros e sentinelas.

### REF-0171 — Predefined Macro Substitutions

[REF, REF-0171, p.PDF 943–948] (READ_FULL_TEXT). Macros de compilação registram build, arquitetura, arquivo/caminho, função/assinatura, datas. __COUNTER__ expande após macros/templates; especializações têm valores próprios e chamadas repetidas não incrementam em runtime. __RANDOM__ é substituição de compilação. Proposta: proveniência de binário/log, com cuidado ao expor caminho local.

### REF-0172 — Mathematical Constants

[REF, REF-0172, p.PDF 949–950] (READ_FULL_TEXT). Constantes matemáticas e/pi/log/raízes evitam recálculo e documentam precisão. Sem regra financeira nova; exemplos imprimem constantes.

### REF-0173 — Numerical Type Constants

[REF, REF-0173, p.PDF 951–953] (READ_FULL_TEXT). Limites char..ulong e precisão/expoentes float/double; DBL_MIN é positivo mínimo normal, não menor número negativo. DBL_EPSILON não é tolerância monetária universal. IDs ulong não devem ser estreitados a int. Apoio ao cálculo e serialização.

### REF-0174 — Uninitialization Reason Codes

[REF, REF-0174, p.PDF 954–955] (READ_FULL_TEXT). OnDeinit recebe razões 0..9 (program/remove/recompile/chartchange/chartclose/parameters/account/template/initfailed/close). Registrar motivo ajuda distinguir reinício de falha; não presumir nova sessão comercial em toda reinit.

### REF-0175 — Checking Object Pointer

[REF, REF-0175, p.PDF 956–956] (READ_FULL_TEXT). CheckPointer distingue INVALID/DYNAMIC/AUTOMATIC. Só deletar objetos new; uso inválido encerra programa criticamente. Aplicação em futuras classes do harness.

### REF-0176 — Other Constants

[REF, REF-0176, p.PDF 957–960] (READ_FULL_TEXT). EMPTY_VALUE=DBL_MAX, INVALID_HANDLE=-1, WHOLE_ARRAY=-1, WRONG_VALUE=-1 e NULL têm contratos distintos. IS_DEBUG_MODE/IS_PROFILE_MODE são compilação, não telemetria comercial. Criptografia lista BASE64/AES/DES/hash/ZIP; presença não equivale política de segurança. Validar sentinelas antes de cálculo.

### REF-0177 — Data Structures

[REF, REF-0177, p.PDF 961–1001] (READ_FULL_TEXT). Agrupador de estruturas; separa dados de mercado, requisição/check/result/transação e calendário.

### REF-0178 — Date Type Structure

[REF, REF-0178, p.PDF 962–962] (READ_FULL_TEXT). MqlDateTime tem oito ints, semana começa domingo=0 e day_of_year inicia em zero; anos bissextos divergem desde março. Relevante a programas diários, sem deduzir timezone ou regra comercial.

### REF-0179 — Indicator Parameter Structure

[REF, REF-0179, p.PDF 963–963] (READ_FULL_TEXT). MqlParam carrega enum tipo e campo correspondente long/double/string. IND_CUSTOM exige primeiro parâmetro string com nome do indicador. Proposta futura de criação dinâmica.

### REF-0180 — History Data Structure

[REF, REF-0180, p.PDF 964–964] (READ_FULL_TEXT). MqlRates guarda time de abertura, OHLC, tick_volume, spread e real_volume; CopyRates pode falhar. Não equiparar volume tick a volume real.

### REF-0181 — Order Book Structure

[REF, REF-0181, p.PDF 965–965] (READ_FULL_TEXT). MqlBookInfo tem tipo/preço/volume e volume_real de maior precisão; DOM só existe para alguns símbolos. Sem uso obrigatório no Monitor.

### REF-0182 — Trade Request Structure

[REF, REF-0182, p.PDF 966–978] (READ_FULL_TEXT). MqlTradeRequest contém ação, magic/order/symbol, volume/preços/stoplimit/SL/TP/deviation, tipo/filling/time/expiration, comment e position/by. Obrigatoriedade depende de operação e modo: Request/Instant listam nove campos, Market/Exchange cinco; hedging exige ticket ao modificar/fechar. Zero inicialização não substitui preencher contrato. Texto SLTP diz quatro mas lista cinco campos: inconsistência editorial a sinalizar. Pesquisa de executor futuro, jamais ativação.

### REF-0183 — Request Check Result Structure

[REF, REF-0183, p.PDF 979–979] (READ_FULL_TEXT). OrderCheck produz retcode e projeções de saldo/equity/margem/free/level e comentário. Verificação prévia não é confirmação de execução nem validação normativa JPW.

### REF-0184 — Trade Request Result Structure

[REF, REF-0184, p.PDF 980–982] (READ_FULL_TEXT). MqlTradeResult guarda retcode, deal/order, volume/preço confirmados, bid/ask, comentário, request_id e retcode_external. request_id correlaciona solicitação com resultado assíncrono. request/result do handler só preenchidos para REQUEST. bool de chamada não basta para interpretar resultado comercial.

### REF-0185 — Trade Transaction Structure

[REF, REF-0185, p.PDF 983–990] (READ_FULL_TEXT). Primeiro selecionar por trans.type: campos válidos variam por ORDER/HISTORY, DEAL, POSITION, REQUEST. Chegada de transações não tem prioridade garantida. Uma requisição gera várias mudanças e snapshots devem reconciliar estado atual; eventos não equivalem transações de banco ACID. Exemplo assíncrono instala/remove pendente; apenas estudo.

### REF-0186 — Price Data Structure

[REF, REF-0186, p.PDF 991–992] (READ_FULL_TEXT). SymbolInfoTick devolve bid/ask/last/volume/time_msc/flags numa consulta; campos não alterados preservam valores anteriores. Flags dizem exatamente o que mudou; não interpretar cada tick como novo negócio.

### REF-0187 — Economic Сalendar structures

[REF, REF-0187, p.PDF 993–1001] (READ_FULL_TEXT). MqlCalendarCountry/Event/Value separam país, metadados e publicações/revisões. Valores long são multiplicados por 1e6, LONG_MIN significa ausente; getters retornam NaN ausente. Unidade/multiplicador/importância/time_mode são distintos. DATA/NOTIME/TENTATIVE não são instante exato. Proposta futura de contexto informativo, não filtro comercial autorizado.

### REF-0188 — Codes of Errors and Warnings

[REF, REF-0188, p.PDF 1002–1032] (READ_FULL_TEXT). Agrupador separa retorno servidor, warnings, compile e runtime; manter domínios de códigos distintos.

### REF-0189 — Trade Server Return Codes

[REF, REF-0189, p.PDF 1003–1005] (READ_FULL_TEXT). 10008 PLACED, 10009 DONE e 10010 DONE_PARTIAL são estados diferentes. Demais códigos incluem preço/stops/filling, timeout, conexão, limites, FIFO, long/short/close-only e hedge proibido. Não fazer retry cego; contexto do servidor e reconciliação são necessários. Sem envio no Monitor.

### REF-0190 — Compiler Warnings

[REF, REF-0190, p.PDF 1006–1008] (READ_FULL_TEXT). Warnings não impedem EX5 mas incluem variável não inicializada, truncamento, cast, signedness, handler errado e retorno ignorado. Gate proposto deve registrar e analisar; compilar com warnings não prova qualidade.

### REF-0191 — Compilation Errors

[REF, REF-0191, p.PDF 1009–1019] (READ_FULL_TEXT). Catálogo de erros 100–413 cobre sintaxe/tipos/import/resources/templates/interfaces/limites e EX5 não criado. Números são diagnóstico, não lógica comercial. Entradas antigas sobre templates coexistem com exemplos modernos: não derivar ausência de suporte atual só do catálogo.

### REF-0192 — Runtime Errors

[REF, REF-0192, p.PDF 1020–1032] (READ_FULL_TEXT). GetLastError lê _LastError; ResetLastError limpa. Catálogo 4000+ cobre runtime, charts, mercado/história, arquivos, indicadores, DOM, rede, OpenCL, DB, calendário, matrizes/ONNX e usuários. DB distingue handle/preparo/step/bind (512x) de SQLite busy/locked/readonly/constraint (560x); não implementar banco só porque códigos existem. ML/OpenCL/ONNX pesquisa futura.

### REF-0193 — Input/Output Constants

[REF, REF-0193, p.PDF 1033–1040] (READ_FULL_TEXT). Agrupador de flags de arquivos/propriedades/seek/codepages/diálogo.

### REF-0194 — File Opening Flags

[REF, REF-0194, p.PDF 1034–1035] (READ_FULL_TEXT). FILE_READ exige existente; READ|WRITE cria se ausente; WRITE trunca para zero. Compartilhamento não concede READ/WRITE. Prioridade CSV>BIN>TXT, Unicode>ANSI; padrão CSV/Unicode e BOM pode forçar Unicode. FILE_COMMON compartilha entre terminais. Essencial para futura evidência e evitar sobrescrita/perda.

### REF-0195 — File Properties

[REF, REF-0195, p.PDF 1036–1036] (READ_FULL_TEXT). FileGetInteger por handle permite todas propriedades; por nome apenas existência/datas/tamanho. Não pedir estado de handle por nome.

### REF-0196 — In-File Position

[REF, REF-0196, p.PDF 1037–1037] (READ_FULL_TEXT). FileSeek usa SEEK_SET/CUR/END e deslocamentos em bytes. Não confundir caracteres Unicode com bytes.

### REF-0197 — Use of a Codepage

[REF, REF-0197, p.PDF 1038–1038] (READ_FULL_TEXT). Conversões char/string/FileOpen usam codepage; CP_UTF8=65001, ACP depende Windows. Exportação portuguesa precisa encoding explícito e validação, não depender CP_MACCP legado.

### REF-0198 — MessageBox

[REF, REF-0198, p.PDF 1039–1040] (READ_FULL_TEXT). MessageBox retorna IDs distintos; ESC só cancela quando Cancel existe. Flags compõem botões/ícones/default. Conhecer diálogo não autoriza inserir bloqueio modal no Monitor.

### REF-0199 — MQL5 programs

[REF, REF-0199, p.PDF 1041–1096] (READ_FULL_TEXT). EX5 requer compilação nativa; EA/indicador persistem ligados ao gráfico, script executa uma vez, serviço não depende de gráfico. Máximo um EA/um script por gráfico. Não inferir instalação/teste a partir de fonte.

### REF-0200 — Program Running

[REF, REF-0200, p.PDF 1042–1048] (READ_FULL_TEXT). EA/script/serviço têm threads próprias; indicadores do mesmo símbolo compartilham thread. Eventos sequenciais e NewTick/Timer/ChartEvent podem coalescer; fila limitada descarta excessos. Chartchange de EA chama Deinit/Init sem zerar globais/statics; eventos antes do fim de Init são ignorados. Funções proibidas dependem contexto inclusive biblioteca. Monitor deve manter handlers curtos, snapshots e parada cooperativa.

### REF-0201 — Trade Permission

[REF, REF-0201, p.PDF 1049–1052] (READ_FULL_TEXT). Permissões são camadas: TERMINAL_TRADE_ALLOWED, MQL_TRADE_ALLOWED, ACCOUNT_TRADE_EXPERT e ACCOUNT_TRADE_ALLOWED. Última falsa também por desconexão/investidor/arquivo/bloqueio. AutoTrading não é disponibilidade do Monitor nem autorização normativa para Supervisor.

### REF-0202 — Client Terminal Events

[REF, REF-0202, p.PDF 1053–1055] (READ_FULL_TEXT). Init/Deinit/Start/Tick/Calculate/Timer/Trade/TradeTransaction/Tester/Chart/Book têm destinatários diferentes. Deinit limitado a 2.5s; desativar AutoTrading não interrompe OnTick nem cessa NewTick. Timer destruir na saída. BookEvent broadcast requer filtrar símbolo e equilibrar subscribe/release. Base para Monitor observacional.

### REF-0203 — Resources

[REF, REF-0203, p.PDF 1056–1067] (READ_FULL_TEXT). #resource incorpora arquivos no EX5, pesquisa relativa a MQL5 ou fonte e nomes ::; recursos de outro EX5 incluem caminho::nome. Variáveis resource não aceitam acesso :: automático. Bitmap dimensions [height][width], alpha/encoding importam. Limite estático 128MB difere ResourceCreate dinâmico 16MB. Útil para UI/embalagem proposta; sem entrega de kit.

### REF-0204 — Call of Imported Functions

[REF, REF-0204, p.PDF 1068–1069] (READ_FULL_TEXT). Imports usam early binding e thread do chamador; falha DLL/função/permissão interrompe EA até reinit. DLL exige protótipo/calling convention; arrays passam buffer físico independente AS_SERIES e tamanho explícito. Não introduzir dependência nativa no produto por esta pesquisa.

### REF-0205 — Runtime Errors

[REF, REF-0205, p.PDF 1070–1070] (READ_FULL_TEXT). Divisão por zero, índice fora e ponteiro inválido terminam imediatamente. _LastError é zerado antes OnInit, não antes de cada operação automaticamente. Proposta harness deve distinguir falha crítica de retorno de API.

### REF-0206 — Testing Trading Strategies

[REF, REF-0206, p.PDF 1071–1096] (READ_FULL_TEXT). Tester tem hipóteses próprias: OHLC/open-only são aproximações que podem criar graal artificial; open-only restringe timeframes. Ticks reais podem ser substituídos por gerados quando inconsistentes com minuto; cache 128k difere base CopyTicks. Spread histórico flutuante; globals isoladas; indicadores calculados sob demanda (visual/everytick exceptions). TimeLocal=TradeServer=GMT no tester, portanto não valida conversão real de fuso. Timer continua e amplia custo; Sleep avança tempo simulado e pode disparar stops. Multi-símbolo exige história/sincronização; data inicial pode mudar. Math mode só Init/Tester/Deinit; otimiza máximo. Agents isolados, cache não é sessão nova; arquivos adicionais tester_file e dynamic indicator tester_indicator. DLL remoto proibido. FILE_COMMON local compartilhado exige isolamento de evidências. Nada constitui teste nativo realizado.

### REF-0207 — Predefined Variables

[REF, REF-0207, p.PDF 1097–1108] (READ_FULL_TEXT). Predefinidas refletem gráfico e contexto chamador da biblioteca. Evitar usá-las como se fossem propriedades de qualquer símbolo monitorado.

### REF-0208 — _AppliedTo

[REF, REF-0208, p.PDF 1098–1099] (READ_FULL_TEXT). _AppliedTo informa origem de indicador, preços 1..7, anterior/primeiro 8/9, handles>=10. Tabela de Weighted Price apresenta texto inconsistente com HLCC/4; não copiar fórmula dessa linha como regra. Sem uso direto EA observacional.

### REF-0209 — _Digits

[REF, REF-0209, p.PDF 1100–1100] (READ_FULL_TEXT). _Digits precisão do símbolo do gráfico; para símbolo externo consultar suas próprias propriedades.

### REF-0210 — _Point

[REF, REF-0210, p.PDF 1101–1101] (READ_FULL_TEXT). _Point tamanho do ponto na moeda de cotação do símbolo atual; não é tamanho de tick nem pip universal.

### REF-0211 — _LastError

[REF, REF-0211, p.PDF 1102–1102] (READ_FULL_TEXT). _LastError guarda último erro e precisa ResetLastError para delimitar tentativa.

### REF-0212 — _Period

[REF, REF-0212, p.PDF 1103–1103] (READ_FULL_TEXT). _Period é timeframe do gráfico, não programa diário nem clock comercial.

### REF-0213 — _RandomSeed

[REF, REF-0213, p.PDF 1104–1104] (READ_FULL_TEXT). _RandomSeed muda com MathRand e é inicializado por MathSrand. Determinismo futuro exige seed registrado; não assumir aleatoriedade criptográfica.

### REF-0214 — _StopFlag

[REF, REF-0214, p.PDF 1105–1105] (READ_FULL_TEXT). _StopFlag não zero indica tentativa de parada; IsStopped permite loops cooperativos.

### REF-0215 — _Symbol

[REF, REF-0215, p.PDF 1106–1106] (READ_FULL_TEXT). _Symbol é nome do gráfico; preservar símbolo alvo explícito em monitor multi-instrumento.

### REF-0216 — _UninitReason

[REF, REF-0216, p.PDF 1107–1107] (READ_FULL_TEXT). _UninitReason guarda motivo de desinicialização; correlacionar com sessão e logs.

### REF-0217 — _IsX64

[REF, REF-0217, p.PDF 1108–1108] (READ_FULL_TEXT). _IsX64 informa terminal 32/64 bits; registrar ambiente não comprova compatibilidade/executabilidade.

### REF-0218 — Common Functions

[REF, REF-0218, p.PDF 1109–1192] (READ_FULL_TEXT). Agrupador das funções comuns; contratos específicos abaixo.

### REF-0219 — Alert

[REF, REF-0219, p.PDF 1111–1115] (READ_FULL_TEXT). Alert não retorna valor, no máximo64 argumentos e não arrays; formatos de tipos diferem. Não funciona no Tester. Exemplo MA tem deduplicação de mensagem; alerta não prova entrega nativa.

### REF-0220 — CheckPointer

[REF, REF-0220, p.PDF 1116–1117] (READ_FULL_TEXT). CheckPointer evita encerramento crítico; ! faz verificação implícita. Delete só DYNAMIC; lista demonstrativa não valida ciclo de vida do produto.

### REF-0221 — Comment

[REF, REF-0221, p.PDF 1118–1118] (READ_FULL_TEXT). Comment limita2045 caracteres e64 argumentos; arrays elemento a elemento; não executa em otimização. UI truncada não é evidência completa de estado.

### REF-0222 — CryptEncode

[REF, REF-0222, p.PDF 1119–1120] (READ_FULL_TEXT). CryptEncode transforma uchar data/key para result e retorna bytes ou0/erro. Exemplo DES é demonstração, não recomendação de segurança. Hash/serialização de evidências futura exige contrato próprio.

### REF-0223 — CryptDecode

[REF, REF-0223, p.PDF 1121–1122] (READ_FULL_TEXT). CryptDecode inversa de transformação; bytes ou0/erro. Assinatura impressa diz CryptEncode sob título Decode, inconsistência editorial. Confirmar API no ambiente antes de exemplo executável; não inventar execução.

### REF-0224 — DebugBreak

[REF, REF-0224, p.PDF 1123–1123] (READ_FULL_TEXT). DebugBreak só interrompe quando iniciado em debug; presença em fonte não produz breakpoint em release.

### REF-0225 — ExpertRemove

[REF, REF-0225, p.PDF 1124–1125] (READ_FULL_TEXT). ExpertRemove seta flag, não interrompe linha imediatamente; chama Deinit e ignora eventos futuros. Em OnInit tester vira erro de inicialização; após init resulta conclusão normal com Tester/estatísticas. Não usar como sinônimo de fechar posições.

### REF-0226 — GetPointer

[REF, REF-0226, p.PDF 1126–1129] (READ_FULL_TEXT). GetPointer só classe, não struct/tipo simples/ponteiro como argumento. Objetos automáticos têm ponteiros válidos mas não deletáveis. Aplicação futura em ownership de classes.

### REF-0227 — GetTickCount

[REF, REF-0227, p.PDF 1130–1130] (READ_FULL_TEXT). GetTickCount retorna uint ms desde boot e transborda49.7dias. Medição duração não é hora de mercado.

### REF-0228 — GetTickCount64

[REF, REF-0228, p.PDF 1131–1132] (READ_FULL_TEXT). GetTickCount64 retorna ulong ms desde boot, precisão típica10–16ms; evita wrap uint. Proposta de medição temporal de handlers, sem alegar benchmark realizado.

### REF-0229 — GetMicrosecondCount

[REF, REF-0229, p.PDF 1133–1134] (READ_FULL_TEXT). GetMicrosecondCount mede us desde início do programa; adequado duração relativa com baseline, não timestamp civil.

### REF-0230 — MessageBox

[REF, REF-0230, p.PDF 1135–1139] (READ_FULL_TEXT). MessageBox bloqueia execução esperando usuário, proibido indicador e ausente Tester. Exemplo contabiliza deals de saída e custos, explicitamente sem filtro magic; não adotar seu contador como definição de sequência JPW nem como pausa segura Monitor.

### REF-0231 — PeriodSeconds

[REF, REF-0231, p.PDF 1140–1141] (READ_FULL_TEXT). PeriodSeconds converte ENUM_TIMEFRAMES para segundos; enum não deve ser tomado como quantidade de minutos bruta. Não resolve timezone/sessões.

### REF-0232 — PlaySound

[REF, REF-0232, p.PDF 1142–1144] (READ_FULL_TEXT). PlaySound WAV retorna true se arquivo encontrado, não prova percepção; NULL para. Ausente Tester. Recursos explicam caminhos adicionais; função isolada simplifica Sounds. Validar distribuição nativa antes de afirmar alerta sonoro.

### REF-0233 — Print

[REF, REF-0233, p.PDF 1145–1146] (READ_FULL_TEXT). Print até64 parâmetros, sem arrays; doubles podem parecer arredondados e esconder erro binário. Ausente otimização salvo contexto Init descrito no capítulo Tester. Logs não substituem comparação numérica.

### REF-0234 — PrintFormat

[REF, REF-0234, p.PDF 1147–1152] (READ_FULL_TEXT). PrintFormat/printf exigem tipo/ordem/quantidade correspondentes; mismatch indefinido. I64 para long/ulong; precisão de string pode truncar, width nunca corta. Assinatura void contrasta Return Value String no texto: tratar como inconsistência editorial. Usar formato explícito para IDs/custos.

### REF-0235 — ResetLastError

[REF, REF-0235, p.PDF 1153–1153] (READ_FULL_TEXT). GetLastError não limpa _LastError; ResetLastError antes da tentativa impede atribuir erro antigo ao sucesso seguinte.

### REF-0236 — ResourceCreate

[REF, REF-0236, p.PDF 1154–1157] (READ_FULL_TEXT). ResourceCreate de arquivo ou pixels; BMP24/32/WAV, até16MB, nome/duplicação têm erros. Atualizar mesmo recurso muda dimensões/dados sem novo objeto; ARGB premultiplicado/normalizado exige formato correto. Proposta UI, não teste visual.

### REF-0237 — ResourceFree

[REF, REF-0237, p.PDF 1158–1160] (READ_FULL_TEXT). ResourceFree remove só dinâmico e requer ::; objetos existentes podem continuar exibidos, novos não podem reutilizar recurso removido. Aparência residual não prova recurso vivo.

### REF-0238 — ResourceReadImage

[REF, REF-0238, p.PDF 1161–1164] (READ_FULL_TEXT). ResourceReadImage lê pixel/dimensões e falha se2D largura insuficiente; dimensões podem voltar mesmo na falha permitindo retry. Recriação deve usar normalize/noalpha. Não confundir inspeção textual com visual.

### REF-0239 — ResourceSave

[REF, REF-0239, p.PDF 1165–1169] (READ_FULL_TEXT). ResourceSave relativo MQL5/Files sempre sobrescreve e cria diretórios intermediários. Usar caminhos de evidência únicos na proposta; não executar no produto.

### REF-0240 — SetReturnError

[REF, REF-0240, p.PDF 1170–1171] (READ_FULL_TEXT). SetReturnError só define exit code futuro do terminal; última chamada entre programas prevalece, erro crítico/TerminalClose podem sobrepor. Não é erro da operação atual nem fecha terminal.

### REF-0241 — SetUserError

[REF, REF-0241, p.PDF 1172–1172] (READ_FULL_TEXT). SetUserError(ushort) define _LastError=65536+valor; documentar domínio separado de runtime/retcode.

### REF-0242 — Sleep

[REF, REF-0242, p.PDF 1173–1174] (READ_FULL_TEXT). Sleep suspende EA/script, proibido indicador, verifica halt cada0.1s; tester avança relógio (capítulo206). Preferir eventos para observação, sem afirmar alteração atual.

### REF-0243 — TerminalClose

[REF, REF-0243, p.PDF 1175–1176] (READ_FULL_TEXT). TerminalClose apenas comanda encerramento; fechar arquivos e retornar em seguida. Seu alcance é terminal inteiro, diferente de remover EA; não chamar nesta pesquisa.

### REF-0244 — TesterHideIndicators

[REF, REF-0244, p.PDF 1177–1178] (READ_FULL_TEXT). TesterHideIndicators marca indicadores criados depois da chamada; templates EA_name/tester/default mudam visibilidade. UI tester não evidencia ausência/presença de cálculo nem estado runtime.

### REF-0245 — TesterStatistics

[REF, REF-0245, p.PDF 1179–1180] (READ_FULL_TEXT). TesterStatistics válido só OnTester/OnDeinit no tester; fora resultado indefinido. Retorna double mesmo estatística inteira. Proposta harness pode captar métricas, sem equivaler lucro de teste a aceitação.

### REF-0246 — TesterStop

[REF, REF-0246, p.PDF 1181–1182] (READ_FULL_TEXT). TesterStop termina normalmente teste e produz OnTester/estatísticas sem descarregar EA, diferente de ExpertRemove quanto custo de novo passe. Parada antecipada deve ser metadado explícito, não PASS automático.

### REF-0247 — TesterDeposit

[REF, REF-0247, p.PDF 1183–1185] (READ_FULL_TEXT). TesterDeposit emula aporte na moeda depósito, bool sucesso. Top-up de exemplo não é lucro nem política JPW; registrar fluxos para não mascarar resultado.

### REF-0248 — TesterWithdrawal

[REF, REF-0248, p.PDF 1186–1188] (READ_FULL_TEXT). TesterWithdrawal emula retirada, bool sucesso; exemplo tem inconsistência de nome sum/summ e é fragmento. Separar caixa retirado de performance, sem regra normativa.

### REF-0249 — TranslateKey

[REF, REF-0249, p.PDF 1189–1189] (READ_FULL_TEXT). TranslateKey usa idioma/teclas controle para Unicode e -1 em erro; SHIFT pode não gerar caractere. UI futura apenas.

### REF-0250 — ZeroMemory

[REF, REF-0250, p.PDF 1190–1192] (READ_FULL_TEXT). ZeroMemory por referência zera simples/arrays, string equivale NULL; complexo recursivo. Proibido classes protegidas/herdadas; não generalizar para qualquer objeto. Útil em request/result mas zero não valida semântica.

### REF-0251 — Array Functions

[REF, REF-0251, p.PDF 1193–1194] (PARTIAL_CONTINUES). Somente introdução/lista1193–1194: arrays até4dimensões, índices0..n-1, catálogo copy/compare/resize/as-series/sort e FP8/FP16. Nenhum contrato individual dessas APIs foi presumido lido; continuação começa1195.

## Limites e fila

REF-0160 foi concluído apenas por sua continuação 895–896; 892–894 pertencem à leitura anterior. REF-0251 permanece parcial: apenas introdução 1193–1194; próximo leitor inicia1195. Contratos detalhados de ArrayBsearch e demais APIs não estão cobertos por esta entrega. Sem teste de código, sem auditoria visual e sem validação de produto.
