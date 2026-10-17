# TRD — leitura semântica PDF901–1048

Escopo concluído:148 páginas físicas, texto integral recebido e analisado nesta tarefa, sem reutilizar leitura deoutrosworkers. Fonte: corpus-fast/TRD/pages.jsonl. Rodapés extraídos coincidem com901–1048; referência impressa abaixo usa a numeração visível no corpo extraído, sem verificação visual doPDF original. Figuras foram recebidas como legendas/texto, não inspecionadas como imagem. Cobertura integral textual não equivale a auditoria visual.

As aplicações abaixo são inferências de engenharia para o contexto informado noBRIEF: Monitor EA orientado aeventos semnegociação, Supervisor opcional semautorização dearmar. Não foi lido código produtivo nesta tarefa; nenhuma recomendação é diagnóstico confirmado deStoikus. Nenhum produto,kit,harness,piloto,template ouMQL foi alterado. Todos exemplos ecasos nativos: **NOT_RUN**, semMT5/EX5.

## Análise por seção

### 5.7.23 (continuação) — [TRD, p.PDF 901–903; rodapé 901–903]

Fechar gráficos duplicados sem indicadores, EA, script ou objetos exige inventário ChartFirst/Next e identificação símbolo/período. ChartCloseIdle mostra a lista antes de fechar e permite Yes/No/Cancel; ChartSetInteger só enfileira, ChartRedraw precede a pergunta.

**Relação comStoikus:** Proposta futura: limpeza assistida de ambiente de ensaio, sempre fora do Monitor operacional. A leitura começa no meio da seção; não reivindica páginas anteriores.

### 5.7.24 Templates tpl — [TRD, p.PDF 903–918; rodapé 903–918]

ChartSaveTemplate pode sobrescrever arquivo; caminhos de busca de ChartApplyTemplate dependem de separador inicial, pasta EX5 e Profiles/Templates. Aplicar template enfileira comando e encerra programas do gráfico, inclusive o chamador; permissões de negociação do EA carregado são restringidas pelas do chamador e do template. O exemplo Container lê hierarquia e pares chave/valor; Selector aceita um atributo, recua cursor em ramos sem correspondência e devolve a primeira ocorrência. Escrita recursiva precisa preservar codificação/BOM e o exemplo preenche sobra ao reescrever. Periodos internos usam unidade/tamanho, incluindo D1 como24 horas.

**Relação comStoikus:** Aplicação conceitual: restauração de estação não pode ser tratada como simples alteração cosmética. Proposta futura isolada: backup/hash e ensaio de template em gráfico descartável. Formato interno sem documentação oficial completa não deve virar contrato de persistência Stoikus; não foi modificado template algum.

### 5.7.25 Screenshot — [TRD, p.PDF 918–921; rodapé 918–921]

ChartScreenShot salva GIF/PNG/BMP em MQL5/Files; nome até63 caracteres, dimensões explícitas e ALIGN_LEFT/RIGHT mudam a região capturada. Panorama soma alturas/janelas e estima largura de escala, pixels por barra e deslocamento percentual; offset recalculado em imagem larga altera resultado.

**Relação comStoikus:** Proposta futura: evidência visual anexada ao recibo, com símbolo, período, resolução e navegação registrados. Imagem não certifica cálculo, EX5 ou interação; escala60 é hipótese empírica do exemplo.

### 5.8 Introdução e5.8.1–3 tipos/coordenadas — [TRD, p.PDF 921–925; rodapé 921–925]

Objetos têm nome único por gráfico incluindo subjanela. Objetos de tempo/preço acompanham rolagem; objetos em pixels ficam ancorados ao canto. Tabelas relacionam linhas, canais, Fibonacci, Gann, Elliott, formas, setas/texto/bitmap e quantidade de pontos. Controles OBJ_LABEL, RECTANGLE_LABEL, BITMAP_LABEL, BUTTON, EDIT eCHART têm coordenadas de tela e âncora variável ou fixa.

**Relação comStoikus:** Aplicação: painel Monitor deve usar pixels; marcadores analíticos usam tempo/preço. Selecionar tipo por semântica evita painel que role junto com preços; recursos de análise técnica listados não constituem novas regras JPW.

### 5.8.4 Criar — [TRD, p.PDF 925–928; rodapé 925–928]

ObjectCreate retorna aceitação na fila e não existência comprovada; subjanela deve existir, nome até63 caracteres. Repetir nome muda coordenadas, mas não converte tipo/subjanela existente. Getters/ObjectFind drenam fila e bloqueiam. Até30 pontos são previstos, tipos descritos usam até5; regressão/desvio exigem tempo inicial anterior ao final.

**Relação comStoikus:** Aplicação: namespace por instância e verificação de tipo/subjanela no provisionamento; não depender de true como renderização pronta. Evitar getter por setter no caminho quente; validar em lote em etapa de diagnóstico.

### 5.8.5–6 Apagar/localizar — [TRD, p.PDF 928–933; rodapé 928–933]

ObjectsDeleteAll é síncrona e filtra prefixo, janela e tipo; prefixo vazio amplia a todos. ObjectDelete é assíncrona. Enumeração ObjectsTotal/ObjectName é síncrona e ordem lexicográfica sensível a caixa. Percurso reverso reduz renumeração, porém concorrência com outros programas ainda pode saltar objetos. ObjectFind retorna subjanela ou negativo, portanto0 é sucesso.

**Relação comStoikus:** Aplicação: limpeza somente de prefixo próprio não vazio e inventário de nomes antes da remoção quando necessário. Contagem de comandos aceitos não é contagem confirmada de objetos apagados. Não remover objetos manuais alheios.

### 5.8.7 Acesso/proxy/monitor/cópia/grupo — [TRD, p.PDF 934–951; rodapé 934–951]

ObjectGet/Set distinguem integer(long), double e string, propriedades somenteleitura e modificadores. Forma longa separa sucesso e valor; forma curta exige _LastError. Proxy unifica sobrecargas. Monitor captura propriedades válidas, suporta níveis, pontos e dois BMPs, codifica modificador no byte superior, compara snapshots e replica diferenças via dynamic_cast. ObjectCopy cria tipo correto e nome livre antes de restaurar. GroupEdit rastreia seleção com timer e propaga alteração de diálogo aos demais selecionados.

**Relação comStoikus:** Aplicação: allowlist explícita e pequena de propriedades de painel é mais adequada que varrer2048 constantes em produção. Proposta futura: snapshot de UI e regressão visual com r/o excluídas da restauração. O exemplo de grupo é didático e requer revisão das identidades, erros e custo antes de reutilização.

### 5.8.8 Propriedades principais — [TRD, p.PDF 952–953; rodapé 952–953]

Nome identifica objeto, tipo e criação são r/o; descrição/texto e tooltip têm papéis distintos. Criacao não persiste em chr e0 pode representar sessão anterior. Renomeação manual gera delete/create/change; programática não gera esses eventos. Tooltip newline desativa dica automática.

**Relação comStoikus:** Aplicação: identidade persistente deve ser própria, não CREATETIME nem captura exclusiva de eventos de rename. Texto de status e tooltip devem explicar a mesma unidade/estado sem derivar regra normativa de atributos gráficos.

### 5.8.9 Tempo/preço — [TRD, p.PDF 953–956; rodapé 953–956]

TIME/PRICE usam modificador do ponto. HighLowChannel atualiza em barra nova, encontra extremos e configura duas linhas; propriedades temporais ainda existem em objetos de tela mas não têm significado útil para eles.

**Relação comStoikus:** Proposta futura: marcação de intervalos auditáveis; não é cálculo de risco Stoikus. Entradas e disponibilidade de histórico precisam validação antes de iHighest/iLowest e acesso aos pontos.

### 5.8.10–11 Cantos eâncoras — [TRD, p.PDF 956–962; rodapé 956–962]

CORNER fixa origem em uma das quatro bordas da subjanela, XDISTANCE/YDISTANCE medem até âncora do objeto. Nove âncoras servem texto/bitmap; botões/edit/chart/retângulo têm topoesquerdo fixo; setas usam enumeração TOP/BOTTOM própria. Animação demonstra que manter só âncora dentro não mantém todo texto visível.

**Relação comStoikus:** Aplicação: matriz canto×âncora×tamanho no painel, incluindo subjanela e redimensionamento. Não misturar ENUM_ARROW_ANCHOR com ENUM_ANCHOR_POINT apenas por ambos serem inteiros.

### 5.8.12–13 Estado eZ-order — [TRD, p.PDF 962–966; rodapé 962–966]

HIDDEN oculta na lista de objetos, não no gráfico; SELECTABLE habilita seleção e SELECTED marca atual. ZORDER determina destinatário do mouse quando há sobreposição; ordem de criação determina sobreposição visual. Retângulos do relógio exibem prioridade e cor aleatórias para tornar a diferença observável.

**Relação comStoikus:** Aplicação: garantir que controles visíveis recebam clique esperado, testar overlays e tooltips; HIDDEN não é controle de segurança nem invisibilidade visual. Marcações de arraste exigem interação explícita, sem implicar envio de ordens.

### 5.8.14 Cores/estilo/quadro/formas — [TRD, p.PDF 966–979; rodapé 966–979]

COLOR, STYLE, WIDTH, FILL, BACK, BGCOLOR e BORDER variam por tipo; BACK difere de ZORDER, e foreground/fill podem inverter cores dos candles. Linhas largas limitam tracejado. Builders podem possuir remoção no destrutor ou apenas construir; essa escolha muda ciclo de vida. Shape factory converte pixels a tempo/preço, limita rotação e configura escala1:1 e CHART_SHOW; restaura configurações ao terminar. O texto recomenda recursos gráficos para desenho livre em vez de forçar objetos de marcação.

**Relação comStoikus:** Aplicação: manter legibilidade do preço e distinguir propriedade visual de entrada. Factories/RAII são padrões possíveis, não adoção dos exemplos. Shapes aleatórias, desenho livre e alteração de escala do gráfico são nãoaplicáveis ao Monitor atual.

### 5.8.15–17 Fonte/rotação/dimensões — [TRD, p.PDF 979–991; rodapé 979–991]

Font eFONTSIZE só alteram texto interno de tipos compatíveis, não descrições de linhas; fonte em pixels conforme exposição do livro. ANGLE gira texto em torno da âncora. XSIZE/YSIZE podem ser definidos em controles/bitmap, apenas lidos em LABEL; tipo incompatível gera4203. Label muda tamanho com conteúdo e requer renderização antes de leitura. GetMargins usa máscaras canto/âncora para margens próximas/distantes, incluindo metade no centro.

**Relação comStoikus:** Aplicação: truncamento, dimensões reais de rótulo, fonte disponível e resize precisam ensaio nativo. Evitar Sleep de animação em handler do Monitor; exemplo é script demonstrativo, não arquitetura de aplicação. Limites de janela menores que conteúdo exigem política adicional.

### 5.8.18 Visibilidade por timeframe — [TRD, p.PDF 991–994; rodapé 991–994]

TIMEFRAMES é bitmask OBJ_PERIOD_*, não valor direto de ENUM_TIMEFRAMES. OBJ_NO_PERIODS oculta em todos; OR combina flags. Exemplo enumera períodos e gera bit por posição. Centro calculado uma vez não acompanha resize; indicador com evento é necessário para reposicionar.

**Relação comStoikus:** Aplicação: esconder apresentação não desliga lógica e não prova que um componente deixou de operar. Proposta futura: tabela explícita de mapeamento e testes de todos os períodos em vez de depender implicitamente de ordem.

### 5.8.19–20 Wingdings eraios — [TRD, p.PDF 994–998; rodapé 994–998]

ARROWCODE seleciona caractere Wingdings; RAY_LEFT/RIGHT controlam extensão, RAY deVLINE alcança subjanelas. Canal desvio deve ter pontos temporais em ordem crescente. Ray também condiciona extrapolação por API.

**Relação comStoikus:** Aplicação: marcadores de status devem ter rótulo legível além do símbolo; geometria de raios é apresentação analítica, não sinal de negociação. Extrapolação de desenho não é previsão.

### 5.8.21–23 Estado pressionado eBMP/crop — [TRD, p.PDF 998–1004; rodapé 998–1004]

STATE é toggle deBUTTON eBITMAP_LABEL; sem seleção, clique alterna automaticamente. BMPFILE usa índice0 pressionado e1 solto, um só arquivo atende ambos. Caminho absoluto relativo aMQL5 e relativo aoEX5 têm resultados distintos; limite63 caracteres. X/YOFFSET recortam atlas sem redimensionar imagem; dimensões menores delimitam fragmento.

**Relação comStoikus:** Aplicação: estado visual de botão não é autorização operacional. Proposta futura: recursos empacotados e atlas testados com os dois estados, caminhos e recortes. Formatos aceitos para objeto no livro sãoBMP, mesmo que screenshot aceitePNG; não confundir APIs.

### 5.8.24–27 Edit/níveis/especializados — [TRD, p.PDF 1004–1011; rodapé 1004–1011]

OBJ_EDIT tem ALIGN eREADONLY, largura fixa e scroll horizontal; readonly impede edição e não concede validação ao conteúdo. DEVIATION positiva define largura do canal desvio. LEVELS define quantidade; VALUE/TEXT/COLOR/STYLE/WIDTH exigem índice. HighLowFibo atualiza extremos em barra nova e estiliza níveis. GannDirection, ElliottDegree/Drawlines, Scale eEllipse são específicos do objeto.

**Relação comStoikus:** Aplicação: campos de dados derivados devem expressar readonly e validar texto editável em eventos apropriados. Fibonacci/Gann/Elliott e sua matemática são nãoaplicáveis às regras correntes informadas; podem permanecer referência de API, sem recomendação de estratégia.

### 5.8.28 OBJ_CHART — [TRD, p.PDF 1011–1015; rodapé 1011–1015]

Mini gráficos pertencem à lista de charts eCHART_IS_OBJECT distingue. ID interno permite parte daAPI, mas não ChartClose nem mudança símbolo/período viaChartSetSymbolPeriod; usar propriedades próprias. Indicadores/templates podem ser adicionados; objetos não podem ser criados dentro. Mesmo oculto por timeframe, WINDOW_IS_VISIBLE retorna true.

**Relação comStoikus:** Proposta futura: painel multiframe isolado. Inventário e testes devem reconhecer mini gráficos, sem usá-los para concluir visibilidade efetiva ou como alvos de limpeza de charts normais.

### 5.8.29–30 Movimento eprojeção — [TRD, p.PDF 1015–1020; rodapé 1015–1020]

ObjectMove altera ambas coordenadas de um ponto viafila; quando só tempo importa, setter específico basta. GetValueByTime/GetTimeByValue interpolam, extrapolam apenas comray e linha selecionada em objetos suportados. Falha retorna0 e_LastError4205 no exemplo; canal regressão semray fornece zeros deliberados.

**Relação comStoikus:** Aplicação: jamais tratar0 como cotação válida sem checar erro. Proposta futura: ensaio geométrico de projeção com interior/exterior, rays e números de linha. Cálculo de UI não deve substituir fonte de mercado ou fórmula JPW.

### 5.9 e5.9.1 Handler — [TRD, p.PDF 1020–1023; rodapé 1020–1023]

Eventos chegam ao gráfico do programa, em fila e por sequência; eventos do mesmo tipo podem ser descartados se já pendentes/em processamento. Todos programas do gráfico recebem fluxo. Thread principal/renderização e threadMQL podem avançar em tempos diferentes, logo FIRST_VISIBLE_BAR pode ainda não refletir mouse. OnChartEvent requer assinatura exata e indicador/EA diretamente aplicado; não é entregue a indicador criado poriCustom/IndicatorCreate nem chamado no tester, inclusivevisual, conforme livro.

**Relação comStoikus:** Aplicação: testes de interação exigem terminal/gráfico nativo; StrategyTester não os substitui. Handler deve ser curto, idempotente e reconciliar estado atual; não usar número de callbacks como contador exato de ações.

### 5.9.2–3 Flags eredimensionamento — [TRD, p.PDF 1023–1027; rodapé 1023–1027]

Mouse move/wheel ecriação/exclusão dependem dequatro flags globais ao gráfico; persistem após saída e afetam outros programas. Exemplo salva erestaura flags. CHART_CHANGE não fornece delta: consultar propriedades. Screenshot nativo recompõe desenho e não preserva tooltip/cursor deedição; WindowSizer usa margens empíricas para capturaexterna.

**Relação comStoikus:** Aplicação: registrar alteração deflags ecuidado com restauração concorrente que sobrescreva escolha de outro componente. Ajustes54/22,+2/+1 do exemplo são empíricos, não contrato para macOS/Wine/resolução. Evidência de clique/tooltip requer captura adequada.

### 5.9.4 Teclado/TranslateKey/SubScaler — [TRD, p.PDF 1027–1036; rodapé 1027–1036]

KEYDOWN requer foco nochart; virtualkey nãoé caractere. lparam é código,dparam repetições,sparam máscara com scan/extended/estado anterior;Alt é interceptado ekeyrelease nãoé recebido nesse modelo. TranslateKey retorna short com-1 parafalha, converter cedo paraushort torna comparação >=0 inválida. TerminalInfoInteger fornece estado demodificadores. Quicknavigation intercepta espaço. SubScaler precisa ser primeiro indicador eInheritScale; ajusta limites eescala por fator validado.

**Relação comStoikus:** Aplicação: atalhos apenas auxiliares ecom fallback visível; observar foco, repetição eatalhos reservados. SubScaler é nãoaplicável atual; padrões devalidação eestado visual são reutilizáveis conceitualmente.

### 5.9.5 Mouse — [TRD, p.PDF 1036–1038; rodapé 1036–1038]

CLICK eMOVE passamXY;MOVE leva máscara emstring. WHEEL codifica shortsX/Y epresença deteclas emlparam64bits,delta emdparam múltiplos±120. Coordenadas pertencem aochart inteiro inclusivesubjanelas, exigindo conversão. Clique emobjeto também emiteCLICK geral.

**Relação comStoikus:** Aplicação: evitar ação duplicada ao processar OBJECT_CLICK eCLICK, decodificar com tipos/tamanho certos econverter para subjanela. Proposta futura: casos com wheel negativo,modificadores esubjanelas emterminalreal.

### 5.9.6 Objetos — [TRD, p.PDF 1039–1043; rodapé 1039–1043]

Nome chega emsparam;OBJECT_CLICK incluiXY,DRAG/CHANGE eENDEDIT representam ações diferentes. CREATE/DELETE precisamflags. Hitarea varia por tipo, controles emtela usam interior; maiorZORDER recebe evento, empate favorece criação posterior. Demonstração criaedit aoclicar botão, lêtextoaofim emostra tempo pósarraste. Botão comum requer resetSTATE false emhandler pois default étoggle.

**Relação comStoikus:** Aplicação: router por nome/tipo, validar input emENDEDIT eaplicar estado interno explícito; arraste apenas atualiza configuração proposta. Nenhum desses eventos autoriza armarSupervisor ou negociara partir doMonitor.

### 5.9.7 Eventoscustom eTickSpy — [TRD, p.PDF 1043–1048; rodapé 1043–1048]

EventChartCustom recebeushort0..65535 esoma CHARTEVENT_CUSTOM; true confirmafila. Protocolo define significado deparâmetros edestinoChartID. TickSpy cria indicadoresemoutrossímbolos vi aiCustom; filhos usamOnCalculate para enviar preço esímbolo,paiprocessa OnChartEvent; tick local chamaOnSymbolTick direto. OnCalculate/OnTick normais seguem símbolo do gráfico, portantoamostragem deoutrosapenas quandosímbololocalmuda podeperder atividade. OpreçopassadoéBid ouLast conformechart, nãoAsk nemtickcompleto.

**Relação comStoikus:** Proposta futura apenas: barramento multissímbolo comprotocolo/versionamento,whitelist deorigens/IDs,timestamp/sequência echecagem deestadoatual. Nãoé transporte lossless, nãoé medição delatência,nãoé ML nemnegociação. Livro mostra logs exemplificativos eadiantatema deEAs; nãohouveexecução local.

## Suspeitas estáticas e limites dos exemplos

Estas observações recaem sobre trechos extraídos do livro, não sobre o produto. Precisam confrontação com arquivos originais, compilação e ensaio; nenhuma é resultado de execução.

- p936: função recebe `chart`, mas getters de cor/âncora usam gráfico0; p939 cria `ObjectSelector s(name)` sem passar `chart` e usa inputs globais em vez dos argumentos `clr/anchor`. A generalização paraoutrochart pode consultar objeto homônimo errado.
- p938: trecho ObjectSelector guarda `host` eimplementa setter `chart(long)`, mas não mostra override getter `chart()`; herdado em p937 retornaria0. Conferir header completo antes dereutilizar proxy paraoutrochart.
- p914: `save` chama `children[i].save(h)` sem propagar oretorno. Falha deescrita deumfilho pode não serrefletida noresultado global dofragmento.
- p950: atualização daseleção só compara tamanhos; trocar objetoA porB mantendo cardinalidade pode preservar monitores antigos. Para uso real, comparar identidades enãoapenastamanho.
- p947: restaurar todas propriedades inclusive asr/o gera possibilidade deerros; distinguir allowlist writable echecagem por propriedade antes deadotar padrão.
- p1031: apagar último caractere semguardar string vazia pode solicitar comprimento negativo. Verificar comportamento nativo antes deadaptar.
- p1045: iCustom não tem handle guardado nem teste explícito INVALID_HANDLE nofragmento; gerenciamento delifetime/erros precisa revisão dofontecompleto. Isso não prova vazamento no terminal.
- p1047: filtro `id >= CHARTEVENT_CUSTOM + Message` aceita códigos superiores não pertencentes aoprotocolo único; igualdade/intervalo limitado e validação depayload são necessários emproposta futura. Evento próprio nãoautentica remetente.
- p920 e997: sinais depontuação/formatação incompleta no códigoextraído não justificam declarar erro decompilação dolivro; conferirPDF/fonte antes defixar sintaxe.

## Casos derivados para validação futura — todosNOT_RUN

1. Criar lote deobjetos, ler ao fim everificar nome/tipo/subjanela; registrar aceitação defila separada deestadofinal.
2. Limpar prefixopróprio com objetos manuais ehomônimos emoutrochart presentes; verificar isolamento epóscondição.
3. Sobrepor retângulo,botão elabel comordensvisuais eZORDER opostas; confirmar destino doclique,tooltip eausência dedupla ação porCLICK.
4. Alterar fonte/texto/resolução/canto/tamanho dejanela; verificar margens, dimensões delabel econteúdo maior queáreavisível.
5. Trocarseleção mantendo cardinalidade; conferir que monitor acompanha nomes corretos.
6. Gráfico realversustester/iCustom: documentar ausência esperada deOnChartEvent nosúltimos, sem usar isso como falha doproduto.
7. Teclas comfoco e semfoco,repetição,Shift/layout; wheel±120/±240 comsubjanela; validar decodificação epolítica derepetição.
8. Injetar eventcustom inválido ououtroID; exigir rejeição e medir quedas/reconciliação sobcarga. Multissímbolo deve preservar origem/timestamp e distinguir Bid/Last/Ask.
9. Aplicartemplate emgráficodescartável comEA sempermissão: observar reinicialização, permissões ecaminhos; não envolverSupervisoroperacional.
10. Screenshot decarta comtooltip/cursor deedit: comparar imagerecomposta ecapturaexterna, registrar limites deequivalência visual.

## Evidência de leitura

O primeiro lote901–925 sofreu truncamento interno;901–909 e919–925 chegaram completos,910–918 foram relidos completos. O lote1016–1030 sofreu truncamento pontual em1023, relida completa. Demais lotes926–940,941–955,956–970,971–985,986–1000,1001–1015,1031–1040 e1041–1048 chegaram completos. Ledger mantém lista exata148p ehashporpágina, além dehashrecalculado UTF8. Não há lacuna textual deextração entre901–1048. Seções que começam antes901 oucontinuam após1048 não são reivindicadas integralmente fora desteintervalo.
