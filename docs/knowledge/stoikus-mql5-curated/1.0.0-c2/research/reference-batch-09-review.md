# REF — revisão semântica do lote 09

Leitura real do corpo textual extraído das páginas físicas PDF **2612–2940**, inclusive: 329 páginas, 23 lotes menores que 30.000 caracteres, recebidos integralmente por chamadas com orçamento de 20.000 tokens. A extração não foi tomada como leitura; o trabalhador recebeu e examinou o conteúdo de cada lote, incluindo exemplos. Os hashes e a lista exata de páginas estão em `reference-batch-09-coverage.json`. A paginação impressa extraída coincide com a física neste intervalo; as citações abaixo usam a física. Não houve auditoria das imagens ou reprodução visual de gráficos e tabelas. Linhas longas aparentemente cortadas na extração permanecem uma limitação; nada foi completado por suposição.

**MQL_NOT_RUN** para todos os exemplos: nenhum compilador, MT5, Strategy Tester ou EX5 foi executado. Nenhuma alteração no produto, kit ou piloto. As relações com Stoikus são propostas técnicas, salvo a descrição arquitetural do BRIEF: monitor orientado por eventos, sem negociar, quatro programas diários e Supervisor opcional. Esta leitura não examinou o código atual e não demonstra que ele usa qualquer API abaixo. Exemplos MACD, RSI, médias, canais, ticks ou Fibonacci não fundamentam regras financeiras JP Wealth.

## Síntese aplicada

Para persistência, a fronteira essencial é separar formato, integridade e publicação. `FILE_COMMON` muda o domínio de compartilhamento entre terminais; não concede propriedade exclusiva. `FileFlush` escreve buffers e pode custar desempenho, mas estas páginas não prometem transação entre arquivos. `FileMove` não documenta aqui atomicidade de publicação. `FileLoad` pode retornar sucesso após descartar uma cauda que não completa um elemento. Portanto, um eventual protocolo Stoikus deve validar tamanho, contagem, versão, domínio, identidade do escritor e integridade por meios próprios; são requisitos propostos, não garantias oferecidas por essas funções.

Para coordenação, variáveis globais do terminal são compartilhadas entre programas e expiram após quatro semanas sem acesso. Acesso de leitura renova a atividade. Um CAS de `GlobalVariableSetOnCondition` é atômico para uma variável existente; isso não transforma um fluxo `Check` seguido de `Set` numa criação atômica, não fornece justiça entre concorrentes nem resolve queda do proprietário. Namespace, inicialização, recuperação e eventual lease exigem desenho próprio. Nenhuma política financeira pode ser derivada do exemplo de mutex.

Para a interface, retorno `true` de criar, mover, apagar individualmente ou definir propriedade de objeto representa **comando aceito na fila**, não execução nem visibilidade confirmadas. Consultas síncronas aguardam comandos anteriores e podem custar caro. Uma proposta adequada ao monitor é manter identidade e propriedade dos próprios objetos, agrupar alterações, redesenhar quando necessário e reservar verificações síncronas para pontos de controle. Não se deve usar cor, existência de uma linha ou confirmação de enfileiramento como estado financeiro autoritativo.

Indicadores personalizados constituem outro tipo de programa. O lote explica buffers, aparência e `OnCalculate`; isso não autoriza transformar o EA monitor em indicador ou adicionar sinais. O uso futuro seria uma visualização auxiliar separada, com cálculo, índices, valores vazios e aquecimento explícitos. Não há necessidade atual demonstrada de acrescentar os 18 estilos ao produto.

## Rede — continuação do capítulo iniciado antes do lote

### REF-0840 — Network Functions — continuação PDF 2612–2623

O capítulo começou em 2560, fora desta atribuição. Aqui foram lidos o restante do exemplo TLS e os quatro últimos serviços de rede. A leitura não reivindica as páginas 2560–2611.

### REF-0854 — SocketTlsSend — continuação PDF 2612–2614

O exemplo cria e conecta socket, solicita metadados do certificado, monta GET HTTP, exige quantidade enviada igual ao tamanho e recebe TLS até encontrar o fim do cabeçalho ou vencer o prazo. O socket é fechado em saídas mostradas. A assinatura e o contrato principal estão em 2611, não relida neste lote. Aplicação proposta: distinguir bytes enviados, resposta interpretável e liberação do recurso; nenhum uso atual comprovado. O `MathSwap` em “See also” é uma associação editorial estranha, sem efeito produtivo demonstrado. [REF, SocketTlsSend, p.PDF 2612–2614]

### REF-0855 — WebRequest — PDF 2615–2617

Duas sobrecargas: formulário simples com tamanho explícito ou cabeçalhos personalizados separados por CRLF. Retorna código HTTP ou -1 em erro. Exige URL permitida no terminal; o protocolo seleciona 80/443. É síncrona, só para EAs e scripts; indicador recebe 4014, e não executa no Strategy Tester. Proposta futura: integração externa com timeout e tratamento separado de erro de transporte e resposta HTTP, sem bloquear tarefas críticas. Não há uso atual demonstrado. [REF, WebRequest, p.PDF 2615–2617]

### REF-0856 — SendFTP — PDF 2618–2619

Envia arquivo de `MQL5\Files` ou subpasta ao FTP configurado, podendo especificar diretório remoto. Falha retorna false; configuração e permissão são pré-condições, e não funciona no Tester. Sem uso direto demonstrado; qualquer exportação futura precisaria de confirmação própria, sem confundir envio com preservação local. [REF, SendFTP, p.PDF 2618–2619]

### REF-0857 — SendMail — PDF 2620–2621

Assunto e corpo seguem configurações do terminal. `true` significa entrada na fila de envio, não entrega ou leitura pelo destinatário. Não funciona no Tester. Proposta apenas: alertas com observabilidade da fila; não foi autorizado enviar mensagens. [REF, SendMail, p.PDF 2620–2621]

### REF-0858 — SendNotification — PDF 2622–2623

Texto de até 255 caracteres, IDs móveis configurados, no máximo duas chamadas por segundo e dez por minuto; monitoramento dinâmico pode desabilitar o serviço por excesso. Erros listados 4515–4518; indisponível no Tester. Aplicação proposta: agregação e limitação de alertas, com retorno distinguido de recepção humana. Sem integração atual comprovada. [REF, SendNotification, p.PDF 2622–2623]

## Variáveis globais do terminal

### REF-0859 — Global Variables of the Terminal — PDF 2624–2650

A abertura, lida na 2624, separa estas variáveis das globais da linguagem, documenta compartilhamento entre programas e retenção por quatro semanas desde último acesso. O restante foi lido nas seções seguintes, sem dupla contagem. Proposta: coordenar componentes somente com namespace e protocolo explícitos; isto não é um banco financeiro completo. [REF, Global Variables of the Terminal, p.PDF 2624–2650]

### REF-0860 — GlobalVariableCheck — PDF 2625

Retorna existência em bool. A existência pode mudar entre chamadas concorrentes; o teste não concede propriedade. Proposta: diagnóstico e pré-condições, sem substituir CAS. O exemplo apenas imprime presença/ausência. [REF, GlobalVariableCheck, p.PDF 2625]

### REF-0861 — GlobalVariableTime — PDF 2626–2629

Retorna último acesso; obter valor por `Get` e verificar por `Check` também altera a atividade. O exemplo cria cinco variáveis com pausas, imprime tempos, lê valores e limpa seu prefixo. Proposta: não interpretar esse horário como último evento financeiro ou último heartbeat do escritor, pois leitores também interferem. [REF, GlobalVariableTime, p.PDF 2626–2629]

### REF-0862 — GlobalVariableDel — PDF 2630–2631

Apaga uma variável por nome e retorna bool; `GetLastError` esclarece falha. O exemplo verifica antes e depois. Proposta: limpar somente nomes próprios e coordenar ciclo de vida; não elimina concorrência pelo simples teste prévio. [REF, GlobalVariableDel, p.PDF 2630–2631]

### REF-0863 — GlobalVariableGet — PDF 2632–2634

Há retorno direto double e sobrecarga bool com saída por referência. Zero é valor legítimo e também retorno de erro da forma direta; deve-se separar status e valor, preferindo a segunda forma para contratos claros. Exemplos mostram 1,23, zero e conversões bool/long. Proposta relevante à leitura de estado, sem presumir implementação atual. [REF, GlobalVariableGet, p.PDF 2632–2634]

### REF-0864 — GlobalVariableName — PDF 2635–2636

Consulta nome por índice desde zero até menos que `GlobalVariablesTotal`. O exemplo enumera 21 nomes e mostra ordenação que não deve ser confundida com sequência numérica de sufixos. Proposta: nome estável próprio para identidade, índice apenas para enumeração. [REF, GlobalVariableName, p.PDF 2635–2636]

### REF-0865 — GlobalVariableSet — PDF 2637–2638

Cria a variável ausente e atribui double; retorna horário da última modificação ou zero em erro. Nome tem até 63 caracteres; retenção mantém a regra de quatro semanas. Proposta: representação e namespace devem ser definidos antes de persistir IDs ou estado; cast numérico não garante preservação arbitrária de long. [REF, GlobalVariableSet, p.PDF 2637–2638]

### REF-0866 — GlobalVariablesFlush — PDF 2639

Retorno void; força salvar todas as globais no disco, reduzindo exposição a falha abrupta antes do encerramento normal. Não documenta transação multivariável ou confirmação individual. Proposta de checkpoint futuro, sem promessa de atomicidade financeira. [REF, GlobalVariablesFlush, p.PDF 2639]

### REF-0867 — GlobalVariableTemp — PDF 2640–2641

Cria temporária ausente; ela dura somente a sessão do terminal e não é escrita por Flush. Exemplo diferencia primeiro início/reinício do terminal de reinícios do programa. Proposta: sinalização transitória, nunca tratá-la como histórico durável. [REF, GlobalVariableTemp, p.PDF 2640–2641]

### REF-0868 — GlobalVariableSetOnCondition — PDF 2642–2647

Atualiza uma global existente somente se o valor atual igualar `check_value`; ausente produz 4501 e false. A comparação que não coincide também retorna false. O acesso condicional é atômico e serve de primitiva para mutex. Exemplo guarda ID via união long/double, disputa por tick, libera se proprietário e permite ao mesmo EA readquirir quando recebe primeiro tick; não oferece justiça. Proposta: documentar bootstrap, propriedade, queda e recuperação separadamente; `Check`+`Set` e CAS são contratos diferentes. [REF, GlobalVariableSetOnCondition, p.PDF 2642–2647]

### REF-0869 — GlobalVariablesDeleteAll — PDF 2648–2649

Filtra prefixo e modificação anterior à data; ambos os critérios se combinam. Prefixo nulo/vazio e data zero apagam todas as globais. Retorna quantidade. Proposta: limpeza restrita a namespace próprio; nenhuma limpeza foi executada. Data de modificação aqui não deve ser equiparada automaticamente ao último acesso de Time. [REF, GlobalVariablesDeleteAll, p.PDF 2648–2649]

### REF-0870 — GlobalVariablesTotal — PDF 2650

Retorna total do terminal, incluindo variáveis alheias. Proposta: diagnóstico e enumeração filtrada; não usar total como quantidade de instâncias Stoikus ou proprietário válido. [REF, GlobalVariablesTotal, p.PDF 2650]

## Arquivos

### REF-0871 — File Functions — PDF 2651–2762

Abertura lida em 2651–2653: sandbox local `MQL5\Files` e pasta comum entre terminais, caminhos obtidos por TerminalInfoString, subpastas criadas ao abrir para escrever e suporte específico a named pipes. Não autoriza trabalhar em qualquer diretório do sistema. As subseções abaixo cobrem todo o restante, incluindo exemplos. Aplicação proposta: contrato explícito de pasta, proprietário, codificação e esquema. [REF, File Functions, p.PDF 2651–2762]

### REF-0872 — FileSelectDialog — PDF 2654–2655

Diretório inicial relativo ao sandbox, filtros e flags para abrir/escrever, selecionar pasta/múltiplos, exigir existência e pasta comum. Retorna contagem, zero se cancelado, negativo em erro. No teste não visual, default_filename pode ser copiado e produzir 1 sem seleção humana. Não disponível em indicadores porque bloqueia a thread compartilhada. Proposta para utilitário manual futuro; uma resposta do Tester não prova consentimento humano. [REF, FileSelectDialog, p.PDF 2654–2655]

### REF-0873 — FileFindFirst — PDF 2656–2657

Retorna long de busca ou INVALID_HANDLE. Filtro pode conter subpastas, mas saída traz apenas basename; o exemplo recompõe diretório para distinguir arquivo de pasta. FILE_COMMON escolhe área. Proposta: preservar caminho e domínio separadamente e fechar busca em todos os finais. [REF, FileFindFirst, p.PDF 2656–2657]

### REF-0874 — FileFindNext — PDF 2658–2659

Continua busca por handle, retorna bool e basename de arquivo ou subdiretório. Proposta: não perder o prefixo de caminho nem tratar qualquer item como arquivo regular; enumeração não valida conteúdo. [REF, FileFindNext, p.PDF 2658–2659]

### REF-0875 — FileFindClose — PDF 2660–2661

Void, libera handle da busca e recursos do sistema. O exemplo executa após o laço. Proposta: gestão de recurso distinta de FileClose, inclusive nos erros do processamento. [REF, FileFindClose, p.PDF 2660–2661]

### REF-0876 — FileIsExist — PDF 2662–2664

Bool de existência na área local ou comum; diretório retorna false com 5018. O exemplo apaga arquivos por data de criação e verifica remanescentes, somente como demonstração. Proposta: não confundir existência com validade e não importar essa política de exclusão para Stoikus. [REF, FileIsExist, p.PDF 2662–2664]

### REF-0877 — FileOpen — PDF 2665–2667

Retorna handle int ou INVALID_HANDLE. Flags definem leitura/escrita, BIN/CSV/TXT, ANSI/Unicode, compartilhamento e Common. CSV usa TAB por padrão; TXT ignora separador, e separador zero evita inserção. Codepage especificada requer FILE_ANSI; sem ANSI lê Unicode. Sandbox do agente de teste difere do terminal. Named pipes exigem nome escapado e Flush/Seek entre operações sequenciais de ler/escrever. O exemplo contrasta caminho absoluto incorreto e relativo correto. Proposta central para qualquer banco de arquivos futuro; flags de compartilhamento não são protocolo de exclusão mútua. [REF, FileOpen, p.PDF 2665–2667]

### REF-0878 — FileClose — PDF 2668

Fecha handle previamente aberto, retorno void; exemplo lê texto até EOF e fecha. Proposta: liberar após sucesso e em erros; não reutilizar identificador fechado. [REF, FileClose, p.PDF 2668]

### REF-0879 — FileCopy — PDF 2669–2671

Origem local/comum escolhida por common_flag; destino usa apenas REWRITE e/ou COMMON, ignorando outras flags. Sem REWRITE, destino existente impede cópia. Proposta: conservar originais por padrão e verificar destino; a página não afirma atomicidade da publicação. [REF, FileCopy, p.PDF 2669–2671]

### REF-0880 — FileDelete — PDF 2672–2673

Apaga nome na área local ou comum, false em falha. Exemplo percorre arquivos antigos e depois testa existência. Sem uso direto autorizado; proposta futura exigiria política própria e registro das exclusões. [REF, FileDelete, p.PDF 2672–2673]

### REF-0881 — FileMove — PDF 2674–2675

Move/renomeia com área de origem e flags de destino REWRITE/COMMON; sem REWRITE preserva destino existente. Exemplo confirma presença no destino e ausência na origem. Proposta: esses testes são pós-condições úteis, mas não justificam chamar a operação de transação atômica e durável. [REF, FileMove, p.PDF 2674–2675]

### REF-0882 — FileFlush — PDF 2676–2677

Void, força dados pendentes ao disco; Close também força pendências. Deve ser chamado entre operações de leitura e escrita; uso frequente afeta velocidade. Exemplo agrupa em 128 iterações. Proposta: checkpoints medidos, sem copiar essa periodicidade como norma JPW. [REF, FileFlush, p.PDF 2676–2677]

### REF-0883 — FileGetInteger — PDF 2678–2680

Por handle ou nome; por nome somente existência, datas e tamanho. Erro retorna -1; consulta de pasta pode produzir 5018 com valor correto. Sempre altera LastError, zerando em sucesso. Proposta: verificar valor e erro conforme contrato, usando metadados como diagnóstico e não como hash de integridade. [REF, FileGetInteger, p.PDF 2678–2680]

### REF-0884 — FileIsEnding — PDF 2681–2682

Detecta EOF após leitura ou movimentação; a nota explica tentativa de ler próxima string. Exemplo percorre TXT. Proposta: usar término com leitura validada e contagens esperadas, evitando inferir que arquivo é íntegro só porque EOF foi alcançado. [REF, FileIsEnding, p.PDF 2681–2682]

### REF-0885 — FileIsLineEnding — PDF 2683–2687

Reconhece CRLF em TXT/CSV. Exemplo RSI separa linhas, intercala FileReadNumber/Datetime em ReadData, monta arrays e renderiza barras coloridas, com largura por escala no ChartEvent. Proposta: separar fim de linha de EOF e não tomar essa leitura como suporte genérico a todo CSV. [REF, FileIsLineEnding, p.PDF 2683–2687]

### REF-0886 — FileReadArray — PDF 2688–2689

BIN para arrays sem strings ou estruturas contendo strings/arrays dinâmicos; retorna número de elementos e pode aumentar destino. `start` indica posição no array de destino; a descrição isolada “read from array” é imprecisa frente à assinatura e comentário. Proposta: conferir contagem e esquema em vez de confiar no tamanho alocado. [REF, FileReadArray, p.PDF 2688–2689]

### REF-0887 — FileReadBool — PDF 2690–2692

CSV até separador/EOL e conversão true/false/0/1, com não zero lógico verdadeiro. Exemplo carrega tempos e sinais MACD para setas. Proposta: validação estrita dos tokens pertence ao formato aplicativo; a conversão não prova que a entrada atende ao esquema. Sem sinal financeiro atual derivado. [REF, FileReadBool, p.PDF 2690–2692]

### REF-0888 — FileReadDatetime — PDF 2693–2695

Converte CSV com data e hora, só data ou só hora em datetime. Exemplo repete desenho de sinais. Proposta: política de timezone, calendário e pregão deve vir de requisito próprio, não desses formatos. [REF, FileReadDatetime, p.PDF 2693–2695]

### REF-0889 — FileReadDouble — PDF 2696–2698

Lê double do BIN na posição atual; erro exige GetLastError. Exemplo usa double para contagem, tempos e valores de MA antes de plotar. Proposta: validar contagens, limites e layout; não adotar conversões indiscriminadas como formato financeiro. [REF, FileReadDouble, p.PDF 2696–2698]

### REF-0890 — FileReadFloat — PDF 2699–2701

Lê float do BIN; promoção posterior a double não recupera precisão perdida. Exemplo intercala data em double e fechamento em float e colore a linha. Proposta: precisão escolhida explicitamente. A referência `buff[i-1]` em laço iniciado em zero é uma possível anomalia do exemplo, não bug do Stoikus nem erro executado aqui. [REF, FileReadFloat, p.PDF 2699–2701]

### REF-0891 — FileReadInteger — PDF 2702–2705

Lê até quatro bytes, com constantes 1/2/4. Retorna int; com menos de quatro bytes o resultado é positivo, e o sinal exige cast char/short; três bytes não têm tipo básico correspondente. O ponteiro avança pelos bytes lidos. Exemplo usa comprimento seguido de caracteres de datetime. Proposta: validar comprimento e truncamento antes de alocar ou ler. [REF, FileReadInteger, p.PDF 2702–2705]

### REF-0892 — FileReadLong — PDF 2706–2708

Inteiro long de oito bytes do BIN. Exemplo lê contagem, datetime e volume e só converte para double na visualização. Proposta: preservar representação inteira onde aplicável e limitar contagem antes de alocar; sem regra financeira inferida do volume. [REF, FileReadLong, p.PDF 2706–2708]

### REF-0893 — FileReadNumber — PDF 2709–2713

CSV até delimitador/EOL, convertido em double. Exemplo RSI percorre linhas e datas, separa grupos e colore OHLC. Proposta: separar parser e validação de domínio; valor convertido não prova campo válido, delimitador correto ou versão do arquivo. [REF, FileReadNumber, p.PDF 2709–2713]

### REF-0894 — FileReadString — PDF 2714–2715

BIN exige comprimento; TXT lê até CRLF e CSV até delimitador/EOL. ANSI é convertido para Unicode. Exemplo lê tamanho int e depois string. Proposta: armazenar comprimento em caracteres/bytes de modo inequívoco e limitar entrada. [REF, FileReadString, p.PDF 2714–2715]

### REF-0895 — FileReadStruct — PDF 2716–2719

Estrutura sem strings, arrays dinâmicos ou funções virtuais; size omitido ou acima do tamanho usa a estrutura inteira. Retorna bytes lidos e desloca ponteiro nessa medida. Exemplo lê OHLC/data de Common para candles. Proposta: conferir bytes, layout e versão; uma estrutura parcialmente lida não deve se tornar snapshot aceito. [REF, FileReadStruct, p.PDF 2716–2719]

### REF-0896 — FileSeek — PDF 2720–2722

Offset long em bytes relativo à origem. Deslocamento antes do início fixa zero; além do fim, escrita posterior ocorre na posição e o intervalo recebe valores indefinidos. Exemplo indexa começos de linhas considerando codificação. Proposta: validar limites e não confundir posição em bytes com índice de caractere. [REF, FileSeek, p.PDF 2720–2722]

### REF-0897 — FileSize — PDF 2723–2724

Assinatura retorna ulong e tamanho em bytes; o parágrafo “Return Value” diz int, discrepância bibliográfica explícita. Exemplo separa arquivos grandes/pequenos e move após fechar. Proposta: usar tipo da assinatura e validar tamanho esperado; a operação por tamanho não é política de retenção Stoikus. [REF, FileSize, p.PDF 2723–2724]

### REF-0898 — FileTell — PDF 2725–2727

Retorna ulong da posição em bytes desde o começo. Exemplo lê linhas para construir posições e sorteia uma. Proposta: offsets próprios do encoding e validação por tamanho, sem tratá-los como numeração de registros. [REF, FileTell, p.PDF 2725–2727]

### REF-0899 — FileWrite — PDF 2728–2730

Até 63 parâmetros, separador automático salvo zero, CRLF final; retorno em bytes. Double usa 16 casas e pode sair científico; float usa cinco; DoubleToString fixa formato. Bool e datetime têm representações textuais. Exemplo grava sinais MACD. Proposta: formato canônico explícito para intercâmbio e testes de ida/volta, sem importar os sinais. [REF, FileWrite, p.PDF 2728–2730]

### REF-0900 — FileWriteArray — PDF 2731–2733

BIN para números/estruturas simples, start/count em elementos, retorno em itens. Nota também descreve strings para TXT com CRLF conforme ANSI/Unicode. Exemplo acumula 20 ticks, busca fim e escreve restantes no deinit. Proposta: diferenciar elementos de bytes e definir política de falha para lote pendente; o exemplo não prova persistência após crash. [REF, FileWriteArray, p.PDF 2731–2733]

### REF-0901 — FileWriteDouble — PDF 2734–2736

Escreve double BIN, oito bytes em sucesso e igual avanço do ponteiro. Exemplo MA inclui contagem e tempo convertidos. Proposta: verificar retorno esperado e documentar representação, sem depender de extensão `.csv` para identificar conteúdo binário. [REF, FileWriteDouble, p.PDF 2734–2736]

### REF-0902 — FileWriteFloat — PDF 2737–2738

Escreve quatro bytes de float e avança quatro. Exemplo converte fechamento double para float, intercalado com timestamp double. Proposta: formato e tolerância de precisão devem preceder redução de espaço; não usar por economia sem critério. [REF, FileWriteFloat, p.PDF 2737–2738]

### REF-0903 — FileWriteInteger — PDF 2739–2741

Até quatro bytes com 1/2/4 documentados, retorno em bytes. Exemplo grava tamanho e caracteres de data quando muda direção dos fechamentos. Proposta: contrato de largura e signedness pareado à leitura, com validação de tamanho; direção no exemplo não cria regra Stoikus. [REF, FileWriteInteger, p.PDF 2739–2741]

### REF-0904 — FileWriteLong — PDF 2742–2743

Long BIN, oito bytes em sucesso. Exemplo grava contagem, tempos e tick volumes. Proposta: escrita inteira com contagem verificada e esquema versionado; sem interpretação normativa do volume. [REF, FileWriteLong, p.PDF 2742–2743]

### REF-0905 — FileWriteString — PDF 2744–2746

BIN permite comprimento parcial, sem terminador por padrão, e preenchimento com zeros se comprimento maior; CSV/TXT ignoram length e gravam tudo. LF desacompanhado de CR ganha CR em texto. Unicode dobra bytes por caractere no contrato descrito. Exemplo monta grupos RSI manualmente. Proposta: definir encoding e delimitadores; não presumir quoting CSV universal ou comprimento igual a bytes. [REF, FileWriteString, p.PDF 2744–2746]

### REF-0906 — FileWriteStruct — PDF 2747–2749

Estrutura simples sem strings/arrays dinâmicos/virtuais; size acima do tamanho é limitado ao total. Retorno bytes, exemplo conta tamanho de cinco campos de oito bytes OHLC/data. Proposta: verificar bytes e compatibilidade de layout em vez de usar soma de campos como garantia universal de ABI. [REF, FileWriteStruct, p.PDF 2747–2749]

### REF-0907 — FileLoad — PDF 2750–2751

Lê BIN inteiro em array numérico/estruturas simples e retorna long em elementos ou -1. Lê apenas múltiplo de sizeof(element): arquivo de dez bytes para double lê oito, ignora dois e retorna 1. Proposta importante: rejeitar cauda e tamanho inesperados por validação própria antes de aceitar arquivo; sucesso do Load não significa integridade. [REF, FileLoad, p.PDF 2750–2751]

### REF-0908 — FileSave — PDF 2752–2753

Salva todos os elementos numéricos ou de estruturas simples em BIN, bool, área local/agente/Common. Exemplo copia ticks, salva, limpa array e recarrega. Proposta: round trip não substitui checksum, schema ou protocolo de publicação. O `u//---` extraído é anomalia textual candidata, sem execução. [REF, FileSave, p.PDF 2752–2753]

### REF-0909 — FolderCreate — PDF 2754–2756

Cria pasta relativa no Files local/comum, bool. Exemplo cria hierarquia e imprime caminhos. Proposta: namespace por aplicação/instância e validação de nomes; mensagens de caminho no exemplo não ampliam o sandbox. [REF, FolderCreate, p.PDF 2754–2756]

### REF-0910 — FolderDelete — PDF 2757–2759

Exige pasta sem qualquer arquivo ou subpasta. Exemplo compara vazia e não vazia, com diálogo manual. Sem uso direto autorizado; proposta de manutenção futura nunca deve pressupor que remoção de pasta implica limpeza dos dados. [REF, FolderDelete, p.PDF 2757–2759]

### REF-0911 — FolderClean — PDF 2760–2762

Remove irreversivelmente todos os arquivos e subdiretórios do alvo, local/comum. Exemplo cria arquivos, conta via busca e pede confirmação antes de limpar. Sem uso direto autorizado; para Stoikus, qualquer proposta precisaria de namespace e política de retenção externa a esta API. [REF, FolderClean, p.PDF 2760–2762]

## Indicadores personalizados e estilos

### REF-0912 — Custom Indicators — PDF 2763–2894

Abertura 2763–2765 lida: APIs de criação são de indicadores, não EAs/scripts. `OnCalculate` concentra cálculo; prev_calculated é retorno anterior, inicia/resetta em zero quando série muda; begin informa aquecimento do indicador anterior. Exemplo Accelerator propaga 37 valores iniciais via PLOT_DRAW_BEGIN. Aplicação proposta: visualização auxiliar separada, sem alterar função do EA monitor. [REF, Custom Indicators, p.PDF 2763–2894]

### REF-0913 — Indicator Styles in Examples — PDF 2766–2868

Abertura 2766–2776 enumera sete famílias, 18 estilos e buffers de valor/cor. Buffers double dinâmicos são associados com SetIndexBuffer e dimensionados pelo terminal; comuns exigem gestão própria. Até 512 buffers; cores até 64. Número de buffers/plots só por diretiva; índices de funções começam em zero. O texto afirma que buffers de cor e cálculo não são obtidos por CopyBuffer. Proposta: publicar dado de integração em INDICATOR_DATA, mantendo aparência como apresentação. Subseções lidas integralmente abaixo. [REF, Indicator Styles in Examples, p.PDF 2766–2868]

### REF-0914 — DRAW_NONE — PDF 2777–2779

Um buffer, valores no Data Window sem desenho. Exemplo numera barras como timeseries e recalcula ao surgir barra. Sem uso direto atual; proposta para diagnóstico auxiliar que não polui gráfico. [REF, DRAW_NONE, p.PDF 2777–2779]

### REF-0915 — DRAW_LINE — PDF 2780–2783

Um buffer e cor/estilo/largura configuráveis por diretiva ou função. Exemplo usa closes e randomiza aparência a cada N ticks. Proposta visual futura: aparência determinística por estado documentado, sem copiar aleatoriedade para monitor. [REF, DRAW_LINE, p.PDF 2780–2783]

### REF-0916 — DRAW_SECTION — PDF 2784–2787

Um buffer conecta valores não vazios ignorando vazios; preencher explicitamente entradas e PLOT_EMPTY_VALUE. Exemplo alterna extremos High/Low com intervalo validado e cálculo desde prev_calculated-1. Proposta: distinguir ausência de dado de zero verdadeiro. [REF, DRAW_SECTION, p.PDF 2784–2787]

### REF-0917 — DRAW_HISTOGRAM — PDF 2788–2791

Um buffer, coluna de zero até valor, usualmente janela separada; zero como não desenhável no exemplo seno. Atualização incremental e randomização só demonstram apresentação. Sem uso direto atual; eventual métrica visual precisa definir referência zero própria. [REF, DRAW_HISTOGRAM, p.PDF 2788–2791]

### REF-0918 — DRAW_HISTOGRAM2 — PDF 2792–2795

Dois buffers delimitam segmento vertical; pode usar janela principal ou separada. Buffers não são inicializados automaticamente em zero e entradas vazias devem ser escritas. Exemplo Open/Close omite dia sorteado. Proposta: inicialização completa e vazio inequívoco, sem critério financeiro derivado do dia. [REF, DRAW_HISTOGRAM2, p.PDF 2792–2795]

### REF-0919 — DRAW_ARROW — PDF 2796–2800

Um buffer, símbolo Wingdings, código padrão 159; PLOT_ARROW_SHIFT é pixel, negativo sobe e positivo desce sem mudar valor. Vazios não desenham/não aparecem no Data Window. Exemplo sinaliza comparação de closes e altera aparência; start é calculado mas laço inicia 1. Proposta: sinalização visual não deve alterar número de negócio subjacente; sem adotar sinal do exemplo. [REF, DRAW_ARROW, p.PDF 2796–2800]

### REF-0920 — DRAW_ZIGZAG — PDF 2801–2805

Dois buffers permitem inclusive segmento vertical na mesma barra; liga não vazios alternando buffers e nenhum pode ficar inteiramente vazio. Exemplo serra High/Low omite dia. Sem uso direto demonstrado; proposta apenas para trajetória gráfica auxiliar. [REF, DRAW_ZIGZAG, p.PDF 2801–2805]

### REF-0921 — DRAW_FILLING — PDF 2806–2810

Dois buffers e duas cores conforme qual valor é maior. Ambos zero excluem área, enquanto valores configurados como vazios podem conectar áreas; se vazio for zero, as lacunas também podem ser preenchidas. Exemplo canal de duas MAs com CopyBuffer integral/incremental. Proposta: testar explicitamente lacunas e não inferir tendência ou autorização por preenchimento. [REF, DRAW_FILLING, p.PDF 2806–2810]

### REF-0922 — DRAW_BARS — PDF 2811–2816

Quatro buffers consecutivos Open/High/Low/Close; todos precisam ter valor não vazio por barra. Exemplo escolhe símbolo, tenta CopyRates e alinha ao fim dos buffers após inicializá-los. Sem necessidade atual demonstrada; eventual visualização multissímbolo exige alinhamento temporal próprio, limites e disponibilidade de dados. O Sleep em indicador é tratado nas anomalias abaixo. [REF, DRAW_BARS, p.PDF 2811–2816]

### REF-0923 — DRAW_CANDLES — PDF 2817–2822

Quatro buffers OHLC; uma cor é uniforme, duas separam contorno/corpo, três separam contorno, corpo de alta e de baixa. Modificadores 0/1/2 controlam essas cores. Exemplo multissímbolo usa CopyRates, preenchimento e tentativas. Proposta: legenda e ausência de dados explícitas, sem equiparar cor a regra financeira. [REF, DRAW_CANDLES, p.PDF 2817–2822]

### REF-0924 — DRAW_COLOR_LINE — PDF 2823–2827

Dois buffers: valor e índice de cor, até 64 cores. Alterar a paleta recolore segmentos sem alterar índices do buffer. Exemplo divide em blocos de Length, muda paleta/estilo. Proposta: separar valor de exibição e mapa de estado visual; sem uso direto atual. [REF, DRAW_COLOR_LINE, p.PDF 2823–2827]

### REF-0925 — DRAW_COLOR_SECTION — PDF 2828–2833

Dois buffers, segmento recebe cor pelo índice na barra final e só valores não vazios formam trechos. Exemplo intervalos e paleta; extração mostra variável local sombreando color_sections e um else duplicado. Proposta: exemplos precisam de revisão antes de reutilização; nenhum bug do produto é deduzido. [REF, DRAW_COLOR_SECTION, p.PDF 2828–2833]

### REF-0926 — DRAW_COLOR_HISTOGRAM — PDF 2834–2838

Dois buffers total: valor desde zero e índice de cor; até 64. Exemplo seno colore por ciclos, valida período maior que um e atualiza incrementalmente. Sem uso atual; proposta de gráfico auxiliar exige significado de zero, paleta e dados válidos. [REF, DRAW_COLOR_HISTOGRAM, p.PDF 2834–2838]

### REF-0927 — DRAW_COLOR_HISTOGRAM2 — PDF 2839–2843

Três buffers: dois extremos e cor, inicialização explícita dos vazios. Exemplo High/Low com cor por dia da semana; texto também fala Open/Close em descrição e cinco cores, enquanto color_sections recebe oito. Proposta: validar paleta, índice e significado; inconsistências do exemplo não viram regra Stoikus. [REF, DRAW_COLOR_HISTOGRAM2, p.PDF 2839–2843]

### REF-0928 — DRAW_COLOR_ARROW — PDF 2844–2849

Dois buffers, valor e índice de cor. Conserva Wingdings 159, deslocamento pixel com sinal e exigência de preencher vazios; mudança de cor não muda preço. Exemplo closes e cores por número da barra, randomização N ticks. Sem uso direto; proposta: ícone complementar a texto e estado autoritativo. [REF, DRAW_COLOR_ARROW, p.PDF 2844–2849]

### REF-0929 — DRAW_COLOR_ZIGZAG — PDF 2850–2854

Três buffers, dois extremos e índice por segmento. Exemplo alterna High/Low, colore pelo dia do ano módulo paleta e muda cores. Sem uso direto atual; proposta só de apresentação, não sinal financeiro. [REF, DRAW_COLOR_ZIGZAG, p.PDF 2850–2854]

### REF-0930 — DRAW_COLOR_BARS — PDF 2855–2861

Cinco buffers consecutivos OHLC e cor; quatro preços válidos necessários. Exemplo escolhe símbolo, copia rates, esvazia buffers e colore por módulo. Proposta: validar disponibilidade, limites e sequência de buffer antes de oferecer visualização futura. [REF, DRAW_COLOR_BARS, p.PDF 2855–2861]

### REF-0931 — DRAW_COLOR_CANDLES — PDF 2862–2868

Cinco buffers OHLC e cor, todos os preços não vazios por candle. Exemplo recebe buffers por referência, alinha rates, paleta e símbolo sorteado. Sem uso direto atual; futura ferramenta de visualização deve ser separada do monitor, com sincronismo temporal demonstrado. [REF, DRAW_COLOR_CANDLES, p.PDF 2862–2868]

### REF-0932 — Connection between Indicator Properties and Functions — PDF 2869–2871

Mapeia diretivas e setters. Níveis e plots começam em 1 nas diretivas, em 0 nas funções. Janela, buffers e plots só por diretiva; applied_price também não tem setter equivalente, para OnCalculate curto. Proposta: evitar erros de índice e de confundir propriedade global do indicador com propriedade de plot. [REF, Connection between Indicator Properties and Functions, p.PDF 2869–2871]

### REF-0933 — SetIndexBuffer — PDF 2872–2874

Associa double dinâmico unidimensional; índice menor que indicator_buffers. DATA, COLOR_INDEX e CALCULATIONS têm papéis distintos. Binding volta indexação comum mesmo se AS_SERIES já estivesse ativo; ajustar depois. Tamanho passa ao terminal, não ArrayResize. Exemplo mostra índice zero virar antigo ou atual conforme direção. Proposta: contrato de orientação explícito para qualquer indicador auxiliar. [REF, SetIndexBuffer, p.PDF 2872–2874]

### REF-0934 — IndicatorSetDouble — PDF 2875–2878

Bool, propriedade double, com modificador de nível opcional desde zero. Exemplo inverte limites/níveis a cada dez ticks. Proposta apenas visual: níveis e limites de eixo não são limites financeiros JPW; retorno deve ser conferido no uso futuro. [REF, IndicatorSetDouble, p.PDF 2875–2878]

### REF-0935 — IndicatorSetInteger — PDF 2879–2882

Bool para propriedades int/color, com modificador de nível; índice zero para primeiro. Exemplo muda cor, largura e estilo de três horizontais por contadores. Proposta: aparência verificável e determinística; sem uso direto no EA. O index=5 isolado não é relatado como acesso fora de faixa confirmado porque condições posteriores podem sobrescrevê-lo. [REF, IndicatorSetInteger, p.PDF 2879–2882]

### REF-0936 — IndicatorSetString — PDF 2883–2885

Bool para nome curto ou texto de nível, modificador zero para primeiro nível. Exemplo nomeia três níveis. Proposta: nomes estáveis e legendas claras em ferramenta auxiliar, não evidência de alteração do estado de cálculo. [REF, IndicatorSetString, p.PDF 2883–2885]

### REF-0937 — PlotIndexSetDouble — PDF 2886

Bool para propriedade double de um plot por índice, como PLOT_EMPTY_VALUE apresentado nos estilos. Proposta: vazio deve ser definido conforme domínio do valor e não sempre zero. [REF, PlotIndexSetDouble, p.PDF 2886]

### REF-0938 — PlotIndexSetInteger — PDF 2887–2890

Bool para int/char/bool/color, sobrecarga com modificador de índice de cor. Exemplo linha de três cores e três esquemas a cada cinco ticks, com retorno zero de OnCalculate se CopyBuffer falha. Proposta: confirmar disponibilidade dos dados antes de avançar cálculo; aparência é estado de plot. [REF, PlotIndexSetInteger, p.PDF 2887–2890]

### REF-0939 — PlotIndexSetString — PDF 2891

Bool para propriedade string do plot, por índice e identificador. Proposta: labels de múltiplos valores devem corresponder aos buffers e unidades; não altera dados. [REF, PlotIndexSetString, p.PDF 2891]

### REF-0940 — PlotIndexGetInteger — PDF 2892–2894

Getter int com modificador de cor opcional; nota explica extrair desenho e copiar propriedades junto a SetInteger. A primeira frase diz “sets”, incompatível com nome/assinatura/nota: anomalia bibliográfica. Exemplo define seis cores e colore candles por dia. Proposta: ler de volta configuração para diagnóstico, sem assumir que seis índices cobrem sábado de índice 6. [REF, PlotIndexGetInteger, p.PDF 2892–2894]

## Objetos gráficos — capítulo continua depois do lote

### REF-0941 — Object Functions — início PDF 2895–2940

Capítulo vai até 2967; este lote lê abertura 2895–2896 e filhos até SetString. Operações de escrita enviam comandos à fila comum; mudanças visuais acontecem ao processar eventos e ChartRedraw força redesenho. Nome único em todo chart, incluindo subwindows; renomear gera exclusão antiga e criação nova. Proposta relevante à UI: ownership por namespace e separação entre estado calculado, comandos aceitos e estado visual observado. Não se reivindica leitura de 2941–2967. [REF, Object Functions, p.PDF 2895–2940]

### REF-0942 — ObjectCreate — PDF 2897–2902

True significa enfileiramento assíncrono; resultado de execução ainda desconhecido. Objeto existente provoca tentativa de mudar coordenadas. Nome até 63, subwindow precisa existir, até 30 anchors por expansão futura e limites de parâmetros; quantidade exigida depende do tipo. Tabela diferencia linhas/figuras por tempo/preço e labels/botões/edit/bitmap-label/rectangle-label por distância em pixels. Consultas posteriores são síncronas e caras. Proposta: identidade própria e verificação em pontos definidos, sem criar objetos indefinidamente. [REF, ObjectCreate, p.PDF 2897–2902]

### REF-0943 — ObjectName — PDF 2903–2905

Nome por posição filtrada por subwindow e tipo; -1 inclui todos, zero janela principal. Síncrona: espera comandos anteriores. Exemplo enumera janelas e exclui do relatório prefixo autotrade. Proposta: não usar índice enumerado como identidade e não confundir filtro didático com propriedade Stoikus. [REF, ObjectName, p.PDF 2903–2905]

### REF-0944 — ObjectDelete — PDF 2906–2907

Bool assíncrono de aceitação na fila; consultar depois pode confirmar execução com custo. Exemplo percorre ao contrário e apaga alternados, poupando autotrade; a mensagem “removed” do exemplo é mais forte que o contrato de retorno. Proposta: apagar só objetos próprios e distinguir solicitado de confirmado. [REF, ObjectDelete, p.PDF 2906–2907]

### REF-0945 — ObjectsDeleteAll — PDF 2908–2910

Síncrona e retorna quantidade; filtros por janela/tipo e sobrecarga por prefixo. `name` e `name*` equivalem; prefixo vazio abrange todos os nomes. Espera fila prévia, potencialmente demorado. Exemplo separa remoção de tipos de setas da remoção por prefixo autotrade. Proposta: namespace exato para cleanup próprio, sem exclusão global no produto. [REF, ObjectsDeleteAll, p.PDF 2908–2910]

### REF-0946 — ObjectFind — PDF 2911–2913

Síncrona, retorna índice da janela ou negativo se ausente. **Zero é sucesso na janela principal**, portanto teste bool direto seria inadequado. Exemplo distingue 4202 de outras falhas, cria, redesenha e verifica novamente. Proposta: validação de presença separada de identidade/tipo/propriedades esperadas. [REF, ObjectFind, p.PDF 2911–2913]

### REF-0947 — ObjectGetTimeByValue — PDF 2914–2918

Síncrona; obtém datetime correspondente a preço em uma linha do objeto. Só tipos listados: trend, angle, Gann, channel com duas linhas, regression/stddev com três e arrowed line. Exemplo constrói canal a partir de barras visíveis e consulta preços em passos de 100 pontos. Proposta futura apenas geométrica; não extrair previsão, risco ou critério financeiro dessa interpolação. [REF, ObjectGetTimeByValue, p.PDF 2914–2918]

### REF-0948 — ObjectGetValueByTime — PDF 2919–2923

Síncrona; double do preço para horário, com line_id nos mesmos tipos. Exemplo percorre barras visíveis, consulta duas linhas e remove canal após pausa. Proposta apenas de desenho/inspeção; valor gráfico não é cotação executável ou fonte normativa. [REF, ObjectGetValueByTime, p.PDF 2919–2923]

### REF-0949 — ObjectMove — PDF 2924–2928

Move anchor por índice, tempo/preço, retornando somente aceitação assíncrona. Confirmação por getter síncrono custa fila. Exemplo reproduz ticks com flags Bid/Ask, solicita grande histórico, três tentativas de sincronização e redesenha com pausas; helper Move usa setters. Proposta: agrupar UI e limitar frequência; resultados e tempos impressos do livro não são benchmark Stoikus. [REF, ObjectMove, p.PDF 2924–2928]

### REF-0950 — ObjectsTotal — PDF 2929–2930

Contagem síncrona filtrada por janela e tipo, -1 todos; exemplo relata janelas, incluindo labels de negociações. Proposta: não tratar contagem total como inventário dos objetos próprios nem chamar por objeto/tick sem medir custo. [REF, ObjectsTotal, p.PDF 2929–2930]

### REF-0951 — ObjectSetDouble — PDF 2931–2934

Enum de propriedades double, modificador de nível desde zero para Fibonacci/pitchfork. True confirma envio do comando, execução assíncrona; ler depois é síncrono. Exemplo adiciona nível, texto e faz readback de quantidade/valores. Proposta: verificar propriedades relevantes em checkpoint; nível Fibonacci de exemplo não fundamenta cálculo financeiro. [REF, ObjectSetDouble, p.PDF 2931–2934]

### REF-0952 — ObjectSetInteger — PDF 2935–2937

Recebe long para propriedades datetime/int/color/bool/char, com modificador opcional. Mesma aceitação assíncrona e custo de leitura posterior. Exemplo cria tabela de 140 objetos edit, definindo posições, dimensões, cores e texto. Proposta: evitar proliferação sem ownership; geometria em pixels não é coordenada de mercado. [REF, ObjectSetInteger, p.PDF 2935–2937]

### REF-0953 — ObjectSetString — PDF 2938–2940

Propriedade string com modificador opcional, bool de comando aceito. Renomear gera par delete/create. Exemplo habilita descrições, cria HLine no Bid, escreve descrição, lê de volta, remove e restaura flag no caminho feliz. Proposta: gerir nomes, textos e restauração também nos caminhos de erro; descrição visual não é estado financeiro. O lote termina junto à seção. [REF, ObjectSetString, p.PDF 2938–2940]

## Limites e anomalias bibliográficas qualificadas

Não houve tradução integral nem reprodução de exemplos no produto. A leitura semântica abrange texto extraído, não imagens. Várias linhas de exemplos aparecem cortadas à direita no corpus, títulos e enumerações têm espaçamento irregular, tabelas se fragmentam por página. Isso limita compilabilidade da transcrição, não autoriza diagnosticar o software real.

Discrepâncias concretas: FileSize (2723) usa ulong na assinatura e int na descrição; PlotIndexGetInteger (2892) começa com “sets” mas explica extração; ColorSection (2830–2831) contém sombreamento de variável e else adicional no texto extraído; FileSave (2752) apresenta `u//---`; ColorHistogram2 (2840–2841) declara cinco cores e usa oito no contador. Precisam de conferência do PDF visual e compilação isolada antes de afirmar erro da fonte. A comparação buff[i-1] no exemplo ReadFloat (2701) exige análise de limites antes de reutilizar. Não são achados de bug produtivo.

Os exemplos DRAW_BARS/CANDLES e variantes coloridas contêm Sleep nas rotinas de indicador (2814, 2821, 2858, 2866), enquanto a própria referência neste lote lembra que Sleep não pode ser usado em indicadores (2758). Essa tensão deve ser sinalizada ao autor do manual; não foi executada para confirmar comportamento. Também não se deve alegar acesso styles[5] confirmado em 2882: embora exista atribuição 5, os if subsequentes sobrescrevem em múltiplos de dez, exigindo análise do fluxo antes de concluir.

Conferência de cobertura: todas as seções iniciadas entre 2612 e 2940 e a continuação REF-0854 foram anotadas, com capítulos contêineres marcados por abertura/filhos e limites fora do lote explícitos. Original preservado; somente os três arquivos próprios de pesquisa/relatório foram destinados à entrega.
