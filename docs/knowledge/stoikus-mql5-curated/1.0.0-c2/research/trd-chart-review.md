# Leitura semântica TRD: indicadores, timers e início de gráficos

Fonte: MQL5 Programming for Traders, SHA-256 `9ff6c55090527afa0efce722d67760805ee335fc64dad3c83638a89e6c79a145`, corpus-fast/TRD/pages.jsonl. Leitura humana do agente em lotes textuais, incluindo prosa, tabelas, fórmulas, código e logs, PDF físico675–900 inclusive (226 páginas). O intervalo atribuído675–835 foi concluído; extensão836–900 concluída. **Não é revisão visual das imagens**: apenas seus textos/legendas extraídos foram lidos. Nenhum MetaEditor, MT5, EX5, exemplo, kit ou piloto foi executado: todos NOT_RUN. Nenhum arquivo do produto foi analisado nesta tarefa; aplicações abaixo são propostas, não achados do Stoikus.

O índice foi consultado para identidade/metadados e confronto de títulos depois da leitura. Seus limites podem terminar na página anterior à continuação real; as faixas abaixo seguem páginas físicas observadas. Pais5.4/5.5/5.6/5.7 são contêineres, sem dupla contagem.5.7 está parcial. O capítulo principal de objetos ainda não foi lido por este worker.

O primeiro retorno de ferramenta675–694 foi truncado no meio;680–686 foram relidos integralmente em lote próprio, cobrindo a área omitida. Todos os demais lotes retornaram sem truncamento de ferramenta. Código/logs já cortados à direita na extração original (p758,767/768,830/832,880) permanecem limitação da fonte textual; não foram transformados em exemplos compiláveis.

## Divergências e riscos da própria fonte

- **CopyBuffer:** p683 diz que buffers COLOR_INDEX/CALCULATIONS não podem ser obtidos; p772 afirma expressamente que os três modos podem ser lidos; p827 explica a leitura dos índices de cor do Gator. Conservar divergência editorial. Para manual, tratar como ponto a verificar na referência/API e teste nativo, sem afirmar bug do Stoikus.
- **Weighted:** p789 fornece `(high+low+close+close)/4`, p836 fornece `(open+high+low+close)/4`. Não reproduzir a segunda como definição confiável sem reconciliação.
- **Paleta p712:** explicação de trocar clrGreen na posição2 mostra chamada sem modifier. O contrato anterior permite modifier, e a adaptação de cores p880 usa0/1/2. Hipótese de omissão editorial, NOT_RUN.
- **Exemplos parciais:** chamadas resumidas iCustom p765 e iEnvelopes p806 omitem pathname ou símbolo/timeframe; snippets de UseWPR3 p773 possuem capitalização inconsistente Handle/handle. Não são fonte pronta para compilação.
- **Hipóteses estáticas didáticas:** WPR p709 pode referenciar i-1 em cenário degenerado inicial; delta p726 exige limitar BarCount ao tamanho e p729 admite n=0 antes de acessar n-1 em updateLastTime; parser p815 simplifica aspas/vírgulas e converte string a minúsculas. Exigem fonte completa e testes isolados. Não foram observados no Stoikus.
- **Timer dependente:** p838 afirma que indicadores criados por iCustom/IndicatorCreate não recebem OnTimer. Isso limita receitas de retry com timer quando encapsuladas como dependências. Não confundir funcionamento do exemplo anexado ao gráfico com funcionamento de dependência invisível.

## Seções e aplicação

### 5.4.1 — PDF físico 675–676

Conhecimento: Indicadores transformam séries em buffers geridos pelo terminal; podem existir sem buffers para objetos/interação. Janela e quantidades são decisões estáticas.

Aplicação: Proposta: distinguir Monitor EA existente de eventual indicador visual; não assumir necessidade de converter o programa.

Fonte: [TRD, §5.4.1, p.PDF 675–676]. Estado de exemplos: NOT_RUN.

### 5.4.2 — PDF físico 676–680

Conhecimento: OnCalculate possui duas formas mutuamente exclusivas. A reduzida aceita série arbitrária e begin; a completa recebe OHLC, volumes e spreads do gráfico. prev_calculated é o retorno anterior e pode zerar após reconstrução histórica. Close exige atualizar barra corrente; retornar rates_total comunica prontidão.

Aplicação: Proposta: explicitar estado de dados prontos e invalidação histórica em qualquer indicador futuro, sem transpor automaticamente OnCalculate ao EA.

Fonte: [TRD, §5.4.2, p.PDF 676–680]. Estado de exemplos: NOT_RUN.

### 5.4.3 — PDF físico 680–681

Conhecimento: Janela principal e separada são alternativas compiladas. Objetos permitem complementar outra área, porém não substituem buffers públicos. Apply to possui restrições conforme janela.

Aplicação: Proposta UI: escolher unidade visual e escala antes de arquitetura híbrida.

Fonte: [TRD, §5.4.3, p.PDF 680–681]. Estado de exemplos: NOT_RUN.

### 5.4.4 — PDF físico 681–682

Conhecimento: Buffers armazenam dados; plots definem representação. Candle exige quatro buffers por plot. Quantidades são constantes de compilação; auxiliares também podem ser buffers.

Aplicação: Proposta: contrato separado de dados e apresentação, sem equivaler índice do plot ao buffer.

Fonte: [TRD, §5.4.4, p.PDF 681–682]. Estado de exemplos: NOT_RUN.

### 5.4.5 — PDF físico 682–685

Conhecimento: SetIndexBuffer liga array double dinâmico persistente; terminal dimensiona depois de OnInit, não inicializa valores e controla resize. Ligação redefine indexação comum; ArraySetAsSeries deve vir depois. Tipos DATA, COLOR_INDEX e CALCULATIONS têm funções distintas.

Aplicação: Proposta ownership: vida do array deve abranger uso pelo terminal; inicializar lacunas explicitamente. Divergência CopyBuffer p683 versus p772 deve permanecer sinalizada.

Fonte: [TRD, §5.4.5, p.PDF 682–685]. Estado de exemplos: NOT_RUN.

### 5.4.6 — PDF físico 685–691

Conhecimento: PlotIndexSetInteger configura tipo, estilo, largura, cores, deslocamentos, seta, início e visibilidade. Tipos exigem números diferentes de buffers. DRAW_NONE mantém dados e exclui plot da escala. Shift horizontal em barras e seta vertical em pixels são unidades distintas.

Aplicação: Proposta UI: parâmetros tipados por unidade; falhas das chamadas verificáveis. Nenhum indicador do livro foi executado.

Fonte: [TRD, §5.4.6, p.PDF 685–691]. Estado de exemplos: NOT_RUN.

### 5.4.7 — PDF físico 691–695

Conhecimento: Mapeamento consome buffers sequenciais conforme plot: candles0 usa0–3, linha1 usa4, zigzag2 usa5–6. Ordem dos plots também define sobreposição visual.

Aplicação: Proposta: manifesto de buffers e plots evita pressupostos de índices iguais.

Fonte: [TRD, §5.4.7, p.PDF 691–695]. Estado de exemplos: NOT_RUN.

### 5.4.8 — PDF físico 695–697

Conhecimento: Diretivas fornecem defaults antes de OnInit; funções permitem mudanças posteriores. Diretivas numeram plots a partir de1 e funções a partir de0. Defaults em diretivas aparecem já no primeiro diálogo.

Aplicação: Proposta UI: defaults estáticos legíveis e tradução explícita das bases de índices.

Fonte: [TRD, §5.4.8, p.PDF 695–697]. Estado de exemplos: NOT_RUN.

### 5.4.9 — PDF físico 697–698

Conhecimento: PLOT_LABEL/indicator_labelN nomeiam plots e buffers na Data Window; múltiplos nomes usam ponto e vírgula.

Aplicação: Proposta UI: labels semânticos e unidades, sem depender do nome do arquivo.

Fonte: [TRD, §5.4.9, p.PDF 697–698]. Estado de exemplos: NOT_RUN.

### 5.4.10 — PDF físico 698–703

Conhecimento: EMPTY_VALUE é DBL_MAX por default e deve preencher memória não calculada. Fractais dependem de vizinhos dos dois lados. DRAW_SECTION/ZIGZAG conectam pontos não vazios; vazio no buffer não garante ausência de segmento sobre a barra.

Aplicação: Proposta: não confundir lacuna semântica com conexão gráfica; sinal de fractal tem latência e exemplo não é estratégia validada.

Fonte: [TRD, §5.4.10, p.PDF 698–703]. Estado de exemplos: NOT_RUN.

### 5.4.11 — PDF físico 704–710

Conhecimento: Escala, níveis, cores, textos e altura de subjanela são ajustáveis por IndicatorSet*. Não há getters equivalentes. WPR exemplifica faixa[-100,0], níveis-20/-80 e cálculo incremental. Altura fixa bloqueia ajuste manual.

Aplicação: Proposta UI: reservar altura fixa a painéis deliberados; limites ilustrativos WPR não são regra JP Wealth.

Fonte: [TRD, §5.4.11, p.PDF 704–710]. Estado de exemplos: NOT_RUN.

### 5.4.12 — PDF físico 710–711

Conhecimento: INDICATOR_DIGITS controla apresentação, não precisão do cálculo; SHORTNAME identifica instância e inclui parâmetros relevantes, até63 caracteres.

Aplicação: Proposta UI: separar arredondamento de exibição de cálculo e nomes de ownership.

Fonte: [TRD, §5.4.12, p.PDF 710–711]. Estado de exemplos: NOT_RUN.

### 5.4.13 — PDF físico 711–714

Conhecimento: Tipos DRAW_COLOR_* acrescentam buffer de índices para paleta de até64 cores, após buffers de dados. Em linha colorida, ponto mais recente define cor do segmento.

Aplicação: Proposta UI: documentar se cor descreve ponto ou segmento. Exemplo p712 de troca da terceira cor sem modifier é ambíguo; não copiar sem verificar.

Fonte: [TRD, §5.4.13, p.PDF 711–714]. Estado de exemplos: NOT_RUN.

### 5.4.14 — PDF físico 714–720

Conhecimento: PLOT_DRAW_BEGIN propaga início inválido ao begin de indicador encadeado, mas não substitui inicialização explícita para consumidores programáticos. EMA/TEMA com DBL_MAX pode gerar overflow/NaN e contaminar recorrência. STRICT/CUSTOM/NONE demonstram políticas distintas.

Aplicação: Proposta: validar dados e limites antes de recorrência, inicializar warm-up; não utilizar exemplos como evidência de execução.

Fonte: [TRD, §5.4.14, p.PDF 714–720]. Estado de exemplos: NOT_RUN.

### 5.4.15 — PDF físico 720–732

Conhecimento: Delta de volume exige CopyTicksRange e prontidão assíncrona; timer solicita nova tentativa sem bloquear. DRAW_NONE permite escala útil da delta. OnCalculate não garante cada tick; timestamp em milissegundos mais contagem de ticks empatados evita duplicação/perda no cursor.

Aplicação: Proposta: cursor com identidade temporal e multiplicidade, estado pending e flag de cancelamento lógico de refresh. Hipóteses estáticas p726/729 de limites/n=0 requerem teste isolado; não são bugs Stoikus.

Fonte: [TRD, §5.4.15, p.PDF 720–732]. Estado de exemplos: NOT_RUN.

### 5.4.16 — PDF físico 732–753

Conhecimento: Multissímbolo exige sincronização por tempo, não igualdade de índices. iBarShift exact produz lacuna explícita; QuoteRefresh diferencia histórico disponível, terminal e servidor sem bloquear indicador. Arrays membros podem possuir buffers enquanto objeto vive. Unity calcula mudança relativa de cesta com moeda comum e sentidos direto/inverso.

Aplicação: Proposta: semântica de disponibilidade por símbolo e instante; propriedade de arrays persistentes; nenhuma cesta ou fórmula do livro deve substituir cálculo normativo existente.

Fonte: [TRD, §5.4.16, p.PDF 732–753]. Estado de exemplos: NOT_RUN.

### 5.4.17 — PDF físico 754–757

Conhecimento: Barra nova pode ser detectada por tempo, contagem ou volume, cada qual com limites. Em vários símbolos barras surgem em instantes diferentes. Monitor registra máscara e sincronismo; pressupõe sessões compatíveis e limite64 símbolos.

Aplicação: Proposta: definir política por símbolo e relógio antes de consolidar sessão; indicador não recebe automaticamente tick de todo ativo.

Fonte: [TRD, §5.4.17, p.PDF 754–757]. Estado de exemplos: NOT_RUN.

### 5.4.18 — PDF físico 757–759

Conhecimento: Tester visual calcula cada tick; no modo não visual indicadores dependentes podem calcular sob demanda de CopyBuffer. tester_everytick_calculate não altera geração de ticks. Livro relata ausência de OnDeinit/destrutores globais no teste isolado de indicadores.

Aplicação: Proposta de validação: separar geração, cálculo, visualização e cleanup; todos experimentos desta revisão NOT_RUN.

Fonte: [TRD, §5.4.18, p.PDF 757–759]. Estado de exemplos: NOT_RUN.

### 5.4.19 — PDF físico 759–760

Conhecimento: Indicadores proíbem várias operações de trading, rede, Sleep e bloqueio. Cálculo longo pode bloquear indicadores do mesmo símbolo; trabalho pesado deve residir em script/EA não negociador.

Aplicação: Aplicação arquitetural proposta: manter UI responsiva e orçamento curto de handler; não é diagnóstico do Monitor atual.

Fonte: [TRD, §5.4.19, p.PDF 759–760]. Estado de exemplos: NOT_RUN.

### 5.4.20 — PDF físico 760–762

Conhecimento: Wizard produz rascunho com janela, plots e handlers limitados; não cobre todos os eventos nem configurações.

Aplicação: Sem aplicação direta: fluxo educativo MetaEditor, não autorização para gerar ou instalar indicador.

Fonte: [TRD, §5.4.20, p.PDF 760–762]. Estado de exemplos: NOT_RUN.

### 5.5.1 — PDF físico 763–764

Conhecimento: Handles são locais ao programa; números iguais entre programas não identificam mesmo objeto. Cache e contadores dependem de parâmetros e, para custom, string do caminho/gráfico. Pedidos idênticos no mesmo programa não multiplicam ownership; ChartIndicatorGet acrescenta referência.

Aplicação: Proposta ownership: não transportar handle como identidade global; uma liberação por handle adquirido e política explícita para handles consultados.

Fonte: [TRD, §5.5.1, p.PDF 763–764]. Estado de exemplos: NOT_RUN.

### 5.5.2 — PDF físico 765–768

Conhecimento: iCustom depende de EX5 e assinatura/ordem exatas; omissão só no fim. Caminho absoluto é relativo à raiz MQL5 e relativo busca primeiro junto ao chamador, depois Indicators. Nome dinâmico exige tester_indicator. Encadeamento usa handle final após todos inputs.

Aplicação: Proposta: manifesto de dependências e caminhos canônicos; nenhum EX5 foi compilado. Trechos p765 omitindo pathname não devem ser copiados como chamada completa.

Fonte: [TRD, §5.5.2, p.PDF 765–768]. Estado de exemplos: NOT_RUN.

### 5.5.3 — PDF físico 768–770

Conhecimento: BarsCalculated distingue erro-1, não pronto0 e quantidade calculada; handle válido não significa buffer pronto. Comparação precisa considerar símbolo/timeframe do fornecedor.

Aplicação: Proposta: readiness explícito por dependência, não inferido de criação bem sucedida.

Fonte: [TRD, §5.5.3, p.PDF 768–770]. Estado de exemplos: NOT_RUN.

### 5.5.4 — PDF físico 770–779

Conhecimento: CopyBuffer recebe posição/tempo/intervalo e devolve quantidade real. Offset conta do presente; memória física do receptor é passado→presente. Pode retornar parcial ou ausência temporária. Em indicador retorna sem bloquear; EA/script podem esperar timeout. Encadeamento WPR/TEMA/fractal é demonstração de API e pode repintar barra0.

Aplicação: Proposta: exigir quantidade solicitada antes de consumir, isolar EMPTY_VALUE/NaN e fechar barra conforme contrato. Contradição p683/p772 mantida; não criar sinais comerciais a partir do exemplo.

Fonte: [TRD, §5.5.4, p.PDF 770–779]. Estado de exemplos: NOT_RUN.

### 5.5.5 — PDF físico 780–786

Conhecimento: Painel multitimeframe gera21 handles e projeta cada timeframe numa posição visual. A prontidão usa contagem do próprio timeframe. Livro adverte custo de calcular históricos completos para ler só último valor.

Aplicação: Proposta UI: orçamento de recursos e cache com ownership; painel é possibilidade futura, sem adoção do exemplo.

Fonte: [TRD, §5.5.5, p.PDF 780–786]. Estado de exemplos: NOT_RUN.

### 5.5.6 — PDF físico 786–792

Conhecimento: Catálogo fornece funções, parâmetros, enums preço/volume/média e buffers. Buffers multi-linha têm índices semânticos; Gator inclui buffers de cor.

Aplicação: Sem aplicação direta: referência de APIs para futuras dependências, não recomendação de indicadores ou validação de fórmulas Stoikus.

Fonte: [TRD, §5.5.6, p.PDF 786–792]. Estado de exemplos: NOT_RUN.

### 5.5.7 — PDF físico 792–801

Conhecimento: Stochastic demonstra criação, readiness e cópia de dois buffers; cache quente pode permitir leitura imediata, sem dispensar readiness geral. M1MA agrega dados menores e expõe limites de histórico, barra incompleta e sessões; PendingRefresh evita timer residual. UnityPro troca preços por iMA.

Aplicação: Proposta: validação por timeframe real, carga limitada e cancelamento lógico de refresh; não equiparar média de M1 a regra financeira normativa.

Fonte: [TRD, §5.5.7, p.PDF 792–801]. Estado de exemplos: NOT_RUN.

### 5.5.8 — PDF físico 801–811

Conhecimento: IndicatorCreate aceita MqlParam tipado; enums usam TYPE_INT; custom exige nome como primeiro TYPE_STRING. Tipos/ordem incorretos podem converter silenciosamente. Builder usa templates/overloads para escolher integer/double/string.

Aplicação: Proposta: schema validado antes de criação dinâmica. Snippet p806 iEnvelopes sem símbolo/timeframe é ilustrativo incompleto, não código executado.

Fonte: [TRD, §5.5.8, p.PDF 801–811]. Estado de exemplos: NOT_RUN.

### 5.5.9 — PDF físico 812–820

Conhecimento: Wrapper AutoIndicator empacota metadados de API e parseia lista de parâmetros, com fortes simplificações. Tipos/janela/quantidade de buffers custom não são inferíveis automaticamente. Escalas incompatíveis tornam linhas invisíveis.

Aplicação: Proposta: preferir contrato explícito a adivinhação de entradas; parser didático não é parser robusto de produção e normaliza strings para minúsculas.

Fonte: [TRD, §5.5.9, p.PDF 812–820]. Estado de exemplos: NOT_RUN.

### 5.5.10 — PDF físico 820–821

Conhecimento: Família ChartWindowFind, ChartIndicatorAdd/Delete/Get/Name/Total conecta cálculo a visualização.

Aplicação: Proposta: operações de enumeração e aquisição devem distinguir consulta de referência adquirida.

Fonte: [TRD, §5.5.10, p.PDF 820–821]. Estado de exemplos: NOT_RUN.

### 5.5.11 — PDF físico 821–824

Conhecimento: ChartIndicatorAdd no índice WINDOWS_TOTAL cria subjanela; cleanup usa SHORTNAME. Exemplo assume instância única e última janela, condição explicitamente limitada pelo autor.

Aplicação: Proposta ownership: localizar de novo recurso próprio antes de remover; não presumir última janela como pertencente ao programa.

Fonte: [TRD, §5.5.11, p.PDF 821–824]. Estado de exemplos: NOT_RUN.

### 5.5.12 — PDF físico 824–827

Conhecimento: PLOT_SHIFT afeta CopyBuffer: deslocamento futuroN pede offset-N. API não fornece getter externo dessa propriedade; Gator mostra buffers de cor e valor.

Aplicação: Proposta: incluir shift no contrato e não confundir deslocamento visual com avanço informacional.

Fonte: [TRD, §5.5.12, p.PDF 824–827]. Estado de exemplos: NOT_RUN.

### 5.5.13 — PDF físico 827–832

Conhecimento: IndicatorRelease invalida referência; variável conserva número e deve ser zerada para INVALID_HANDLE. Número pode ser reutilizado por outro indicador. Contador impede descarregar instância ainda usada; tester ignora release segundo livro.

Aplicação: Proposta ownership: validade e geração não podem ser inferidas do inteiro; testar cleanup fora do tester também.

Fonte: [TRD, §5.5.13, p.PDF 827–832]. Estado de exemplos: NOT_RUN.

### 5.5.14 — PDF físico 832–835

Conhecimento: IndicatorParameters devolve tipo e MqlParam efetivos pelo handle; custom pode incluir caminho e Apply to. Stringer usa cast float para exibir doubles, portanto é demonstrativo.

Aplicação: Proposta: registrar parâmetros efetivos com precisão adequada em diagnóstico, não copiar serializador para persistência normativa.

Fonte: [TRD, §5.5.14, p.PDF 832–835]. Estado de exemplos: NOT_RUN.

### 5.5.15 — PDF físico 835–836

Conhecimento: _AppliedTo descreve origem:0 forma completa,1–7 preços,8/9 indicador anterior/primeiro,10+ handle passado. Tabela weighted p836 diverge de p789.

Aplicação: Proposta: origem explícita e resolução local do handle; registrar divergência editorial antes de citar fórmula.

Fonte: [TRD, §5.5.15, p.PDF 835–836]. Estado de exemplos: NOT_RUN.

### 5.6.1 — PDF físico 837–838

Conhecimento: Um timer por programa, primeiro evento após período; eventos não se acumulam quando há outro pendente/em execução. Kill em indicador pode deixar evento residual; término destrói timer.

Aplicação: Proposta: não medir tempo de calendário contando callbacks e manter flag pending.

Fonte: [TRD, §5.6.1, p.PDF 837–838]. Estado de exemplos: NOT_RUN.

### 5.6.2 — PDF físico 838–847

Conhecimento: OnTimer é sequencial com outros handlers, não thread. Indicador dependente criado por iCustom/IndicatorCreate não recebe timer segundo livro. MultiTimer reparte um timer físico em assinantes com multiplicadores; manager não possui objetos; construtor/destrutor faz bind/unbind.

Aplicação: Proposta ownership: separar assinatura de posse e não presumir scheduler em dependência invisível. A restrição tem relevância ao avaliar exemplos anteriores, sem prova nativa.

Fonte: [TRD, §5.6.2, p.PDF 838–847]. Estado de exemplos: NOT_RUN.

### 5.6.3 — PDF físico 847–849

Conhecimento: Timer em milissegundos substitui o de segundos; callback prático limitado aproximadamente10–16ms e carga pode aumentar intervalo. Menor período aumenta tempo de teste.

Aplicação: Proposta UI: escolher frequência por necessidade e medir atraso real; exemplos de logs pertencem ao livro, NOT_RUN local.

Fonte: [TRD, §5.6.3, p.PDF 847–849]. Estado de exemplos: NOT_RUN.

### 5.7.1 — PDF físico 850–851

Conhecimento: Symbol/Period/Point/Digits equivalem às variáveis locais; propriedades de outro gráfico requerem APIs por ID.

Aplicação: Proposta: separar contexto do gráfico da entidade financeira consultada.

Fonte: [TRD, §5.7.1, p.PDF 850–851]. Estado de exemplos: NOT_RUN.

### 5.7.2 — PDF físico 851–851

Conhecimento: ChartID é long e não HWND;0 em muitas APIs significa gráfico atual, não ID efetivo0.

Aplicação: Proposta ownership: persistir escopo do ID e não confundir handle Windows com ID MQL.

Fonte: [TRD, §5.7.2, p.PDF 851–851]. Estado de exemplos: NOT_RUN.

### 5.7.3 — PDF físico 852–853

Conhecimento: ChartFirst/Next enumeram ordem interna que pode diferir das abas. Next(0) significa início, exceção ao padrão0=atual; fim é-1.

Aplicação: Proposta UI: não associar recursos por posição na aba.

Fonte: [TRD, §5.7.3, p.PDF 852–853]. Estado de exemplos: NOT_RUN.

### 5.7.4 — PDF físico 853–854

Conhecimento: ChartSymbol e ChartPeriod consultam qualquer ID; falhas devolvem string vazia ou0 e exigem checagem.

Aplicação: Proposta: não tratar retorno de erro como contexto válido.

Fonte: [TRD, §5.7.4, p.PDF 853–854]. Estado de exemplos: NOT_RUN.

### 5.7.5 — PDF físico 854–856

Conhecimento: Getters síncronos e setters assíncronos tipados; true no setter é enfileiramento. Forma bool+referência distingue falha de valor0. Múltiplas alterações podem preceder um único ChartRedraw.

Aplicação: Proposta UI: batch de atualização com confirmação apropriada, sem prometer efeito imediato.

Fonte: [TRD, §5.7.5, p.PDF 854–856]. Estado de exemplos: NOT_RUN.

### 5.7.6 — PDF físico 856–858

Conhecimento: CHART_COMMENT é editável; nomes EA/script são r/o. Comentário é estado compartilhado do gráfico.

Aplicação: Proposta ownership: não usar Comment como armazenamento exclusivo entre múltiplos componentes.

Fonte: [TRD, §5.7.6, p.PDF 856–858]. Estado de exemplos: NOT_RUN.

### 5.7.7 — PDF físico 858–858

Conhecimento: Estado maximizado/minimizado/foco difere de HWND e flag IS_OBJECT, que são r/o.

Aplicação: Proposta: estado visual não identifica proprietário do gráfico.

Fonte: [TRD, §5.7.7, p.PDF 858–858]. Estado de exemplos: NOT_RUN.

### 5.7.8 — PDF físico 858–860

Conhecimento: WINDOWS_TOTAL inclui principal; visibilidade pode ocultar subjanela sem remover índices. Chart objeto relata visível mesmo quando objeto oculto.

Aplicação: Proposta: inspecionar janela e objeto separadamente, sem usar uma flag como prova de presença visual.

Fonte: [TRD, §5.7.8, p.PDF 858–860]. Estado de exemplos: NOT_RUN.

### 5.7.9 — PDF físico 860–868

Conhecimento: Modo barras/candles/linha, foreground, shift e autoscroll são independentes. Monitor guarda snapshot/backup/restore; mudança linha↔OHLC exige rebinding/reconstrução, barras↔candles pode só redraw.

Aplicação: Proposta UI: separar mudanças de dados de mudanças de apresentação; restaurar propriedades sob contrato de ownership.

Fonte: [TRD, §5.7.9, p.PDF 860–868]. Estado de exemplos: NOT_RUN.

### 5.7.10 — PDF físico 868–871

Conhecimento: CHART_SHOW desliga preço/escalas/subjanelas mas preserva objetos/recursos, útil para interface própria. Ticker/OHLC têm dependência. Volumes usam enum oculto/tick/real.

Aplicação: Proposta UI: painel pode controlar visibilidade, com registro e restauração das propriedades alteradas; não implementar agora.

Fonte: [TRD, §5.7.10, p.PDF 868–871]. Estado de exemplos: NOT_RUN.

### 5.7.11 — PDF físico 872–873

Conhecimento: Shift size mede recuo direito10–50%; fixed position fixa âncora esquerda0–100% quando autoscroll desligado.

Aplicação: Proposta: não confundir pixels, barras e percentuais em layout.

Fonte: [TRD, §5.7.11, p.PDF 872–873]. Estado de exemplos: NOT_RUN.

### 5.7.12 — PDF físico 873–875

Conhecimento: CHART_SCALE0–5 é editável; barras visíveis, primeira barra, largura em barras/pixels são medidas r/o e dependem de recuo/redimensionamento.

Aplicação: Proposta UI: recalcular layout por medidas atuais, sem inferir largura útil da capacidade total.

Fonte: [TRD, §5.7.12, p.PDF 873–875]. Estado de exemplos: NOT_RUN.

### 5.7.13 — PDF físico 875–878

Conhecimento: Escala fixa,1:1 e pontos/barra são modos distintos. Altura programática bloqueia ajuste manual; -1 desfaz. YDISTANCE traduz coordenada global de mouse em local da subjanela.

Aplicação: Proposta UI: coordenadas com origem explícita e restauração de altura; nenhuma medida visual foi conferida em terminal.

Fonte: [TRD, §5.7.13, p.PDF 875–878]. Estado de exemplos: NOT_RUN.

### 5.7.14 — PDF físico 878–881

Conhecimento: Cores de fundo, eixos, grade, barras/candles, volumes, Bid/Ask/Last e stops são propriedades distintas. IndSubChart copia paleta do gráfico ao plot.

Aplicação: Proposta UI: adaptar contraste/paleta sem sobrepor preferências do usuário. Três linhas de código p880 estão cortadas no texto-fonte extraído; não reconstruídas como código validado.

Fonte: [TRD, §5.7.14, p.PDF 878–881]. Estado de exemplos: NOT_RUN.

### 5.7.15 — PDF físico 881–884

Conhecimento: Flags controlam menu, crosshair, scroll, teclado, navegação e drag de níveis. Desativar teclado não impede eventos de tecla. Desativar menu do gráfico preserva menu dos objetos.

Aplicação: Proposta UI: capturar entrada sem bloquear recuperação; restaurar só configuração cuja posse foi definida.

Fonte: [TRD, §5.7.15, p.PDF 881–884]. Estado de exemplos: NOT_RUN.

### 5.7.16 — PDF físico 884–885

Conhecimento: Dock/undock possui flag e limites de retângulo em tela virtual.

Aplicação: Sem aplicação direta: suporte de múltiplos monitores depende de cenário do usuário e validação nativa.

Fonte: [TRD, §5.7.16, p.PDF 884–885]. Estado de exemplos: NOT_RUN.

### 5.7.17 — PDF físico 885–887

Conhecimento: Drop possui janela, tempo/preço e pixels; tempo não é arredondado ao timeframe. Y é relativo à principal, mesmo drop em subjanela.

Aplicação: Proposta UI: nunca converter gesto em regra financeira sem normalização explícita; origem espacial preservada.

Fonte: [TRD, §5.7.17, p.PDF 885–887]. Estado de exemplos: NOT_RUN.

### 5.7.18 — PDF físico 887–890

Conhecimento: TimePriceToXY e XYToTimePrice traduzem sistemas com quantização; resultado pode ser fora da tela ou negativo. Exemplos exibem discrepância no primeiro ciclo.

Aplicação: Proposta: tolerâncias por unidade e verificação de retorno; igualdade demonstrada em exemplo não garante bijeção universal.

Fonte: [TRD, §5.7.18, p.PDF 887–890]. Estado de exemplos: NOT_RUN.

### 5.7.19 — PDF físico 890–893

Conhecimento: ChartNavigate desloca barras a partir de BEGIN/CURRENT/END. Sincronizador usa timestamp da primeira barra visível e variável global, não igualdade de índices entre timeframes.

Aplicação: Proposta: escopo de canal e ownership de autoscroll; não adotar global do exemplo como protocolo de produto.

Fonte: [TRD, §5.7.19, p.PDF 890–893]. Estado de exemplos: NOT_RUN.

### 5.7.20 — PDF físico 893–893

Conhecimento: ChartRedraw solicita pintura; não recalcula séries ou indicadores.

Aplicação: Proposta UI: reservar redraw a apresentação, sem usar como evidência de atualização dos dados.

Fonte: [TRD, §5.7.20, p.PDF 893–893]. Estado de exemplos: NOT_RUN.

### 5.7.21 — PDF físico 894–894

Conhecimento: ChartSetSymbolPeriod enfileira troca; mesmos símbolo/período podem reconstruir gráfico. Troca reinitializa EA e descarrega script que não volta sozinho.

Aplicação: Proposta: refresh é operação de ciclo de vida, não pintura inocente; avaliar impacto antes de reutilizar técnica.

Fonte: [TRD, §5.7.21, p.PDF 894–894]. Estado de exemplos: NOT_RUN.

### 5.7.22 — PDF físico 894–900

Conhecimento: Enumeração usa janela/índice e SHORTNAME; Get adquire referência. Add exige mesmo símbolo/timeframe e pode criar janela em WINDOWS_TOTAL. Delete remove primeira instância homônima e dependentes, sem necessariamente liberar cálculo. Move faz get/add/delete/release; não move objetos.

Aplicação: Proposta ownership: adquirir e liberar simetricamente, identificar instância e localizar janela novamente; não presumir exclusividade de nome ou posição.

Fonte: [TRD, §5.7.22, p.PDF 894–900]. Estado de exemplos: NOT_RUN.

## Fila exata

Próxima página não lida: **901**. Restante da extensão solicitada:901–1048,148 páginas. Página900 inclui início5.7.23 ChartOpen, limite CHARTS_MAX100 e introdução a charts em objetos; sua continuação ainda não foi lida. Completar5.7.23 e demais gráficos, depois objetos/eventos conforme títulos reais do corpus. Não marcar901–1048 como lido a partir do índice. Revisão visual de todas as figuras675–900 permanece pendente; recuperação de código cortado exige PDF/render ou fonte suplementar.
