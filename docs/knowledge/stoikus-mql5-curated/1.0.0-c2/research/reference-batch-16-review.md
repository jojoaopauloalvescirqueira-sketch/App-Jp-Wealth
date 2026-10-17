# Leitura semântica REF6660–7138 — lote16

Leitura textual integral das479 páginas físicas PDF, em15 exposições com no máximo29.500 caracteres e max_output_tokens20.000. Não houve truncamento de saída. As11 primeiras exposições preservam o layout extraído até7012; as4 seguintes normalizam somente espaços horizontais de7013–7138, sem suprimir texto, linhas ou páginas. Os hashes originais por página foram preservados e recalculados a partir do texto original, não do texto normalizado. Ledger: `reference-batch-16-coverage.json`.

MQL_NOT_RUN. Nenhuma compilação/execução MT5, inspeção visual, edição de produto/manual/harness ou alteração Git. As aplicações abaixo são propostas de engenharia para Stoikus, não afirmações de implementação existente nem regras normativas JPW. Diagramas, screenshots e aparência não foram inferidos de espaços vazios na extração.

## Síntese aplicada e limites

- O padrão dos exemplos de controles é validar Create da base, construir dependências, registrar Add, chamar Run, encaminhar OnChartEvent a ChartEvent e finalizar com Destroy(reason). Métodos de evento retornando true significam processamento; em várias bases são no-op. Proposta: testar cada transição na interface nativa, sem transformar retorno true em evidência de mudança de negócio. [REF, Panels and Dialogs, p.PDF6661–6664,6688–6691,6810–6832,6982–7007]
- Botão travável, hover, Checked, RadioButton.State e visibilidade/minimização descrevem UI. Não comprovam monitor ativo, autorização do Supervisor, trade executado ou risco recalculado. Lista/ComboBox têm valor long associado; CheckBox tem valor int separado do bool marcado; CheckGroup agrega flags; RadioGroup representa escolha enumerável. Proposta: preservar adaptadores explícitos entre UI e domínio, com IDs estáveis. [REF, CBmpButton/CCheckBox/CCheckGroup/CRadioGroup, p.PDF6672–6674,6889–6890,6904,6933]
- CSpinEdit trabalha com inteiro limitado; exemplo10–100 com inicial50 não é regra de capital nem parâmetro real de Stoikus. CListView.TotalView só pode ser especificado uma vez segundo o texto. Proposta: planejar capacidade no ciclo de criação e não usar controle visual como validador único. [REF, TotalView/CSpinEdit, p.PDF6841,6943–6958]
- As assinaturas impressas contêm incongruências: OnSetColorBorder declara OnSetColorBackground(p6698,6720,6740); OnItemClick tem parêntese/índice mal formado(p6853); ListViewItems void com retorno descrito bool(p6866); Caption getter aparece MinValue(p6963); ClientAreaRight declara ClientAreaTop(p6975); IniFileSave/Load void têm retorno textual bool(p6991–6992); OnClickButtonMinMax declara OnClickButtonClose(p7000); Minimize/Maximize void têm retorno textual bool(p7003–7004); SubwinOff descrito como getter mas void(p7007). Proposta: conferir includes da versão instalada antes de copiar declaração; não corrigir silenciosamente a fonte nem apresentar exemplo como compilado.
- Migração MQL4 exige revisar eventos, séries e inicialização; EA MQL5 não precisa de OnTick obrigatório. Isso é compatível com monitor event-driven descrito no BRIEF, sem provar execução atual. Direção padrão dos buffers é comum, e memória permanece finita apesar de ausência do antigo limite8. [REF, Moving from MQL4, p.PDF7008–7010]
- Índice7011–7044 é mapa de navegação; resumo de função não informa todos parâmetros, códigos, sincronização ou restrições. Python aparece com prefixo MT5 antigo, e DirectX duplica DXContextSetSize em entrada descrita como getter(p7021). Proposta: resolver API em capítulo substantivo e versão instalada antes de implementar; OpenCL/Python/DirectX continuam pesquisa futura, sem produto inferido.
- Índice de constantes7045–7138 foi lido até IDABORT. As colunas estreitas dividem descrições em sílabas/linhas: leitura textual não resolve validade visual da tabela. Nenhuma leitura das páginas7139–7284 é atribuída a este ledger.
- ACCOUNT distingue saldo, crédito, equity, margem livre/usada/inicial/manutenção e stop-out. Stop-out depende do modo percentual ou dinheiro; trade allowed/trade expert e demo/real são propriedades distintas. Proposta: painel deve rotular unidade e contexto em vez de tratar margem como limite normativo JPW. [REF, List of MQL5 Constants, p.PDF7047–7053]
- CHART_WINDOW_YDISTANCE explica conversão entre coordenadas de evento relativas à janela principal e objetos relativos à subjanela. CHART_EVENT_MOUSE_MOVE/OBJECT_CREATE/OBJECT_DELETE habilitam notificações; suas constantes CHARTEVENT associadas não bastam para presumir recebimento. Proposta: testar roteamento, offset e resize nos painéis. [REF, List of MQL5 Constants, p.PDF7060–7061,7070–7075]
- DEAL_POSITION_ID liga deals à vida da posição; DEAL_TIME_MSC está em milissegundos. Deals BUY/SELL cancelados podem ter lucro zerado e correção via operação de saldo separada. Proposta: reconciliação histórica deve distinguir tipo de deal, entrada/saída, comissão, swap e ajuste, sem inferir resultado econômico só de BUY/SELL. [REF, List of MQL5 Constants, p.PDF7090–7096]
- ERR cobre falhas de memória/arrays/handles, dados ausentes, gráfico, histórico, indicador, rede, notificações e arquivos; ERR_SUCCESS não substitui leitura do retorno da operação. ERR_NOTIFICATION_TOO_FREQUENT e WRONG_SETTINGS justificam diagnósticos distintos. OpenCL não suportado é capacidade de ambiente, não defeito de fórmula. Proposta: conservar causa/ID/operação em log e tratar estado indisponível como desconhecido, sem trocar por zero. [REF, List of MQL5 Constants, p.PDF7099–7127]
- FILE_COMMON usa pasta comum dos terminais; flags SHARE_READ/SHARE_WRITE não substituem READ/WRITE. BIN/CSV/TXT e ANSI/UNICODE definem representação; codepage UTF8 é separado de Unicode de dois bytes descrito em FILE_UNICODE. Proposta: registrar caminho lógico, modo e encoding dos artefatos de evidência e evitar colisões entre instâncias. [REF, List of MQL5 Constants, p.PDF7085–7087,7127–7135]
- DBL_MIN/FLT_MIN são mínimos positivos representáveis, não números mais negativos; epsilon e mantissa não definem tolerância financeira. A entrada FLT_EPSILON imprime condição com DBL_EPSILON(p7136), outra incongruência do índice. Proposta: definir tolerância por contrato do cálculo/unidade e conferir capítulo de constantes numéricas. [REF, List of MQL5 Constants, p.PDF7087–7089,7135–7138]

## Notas por ID do catálogo filtrado

Cada entrada cobre apenas a interseção das páginas indicadas com6660–7138; pais agregadores não somam nova leitura.

- **REF-0001 — MQL5 Reference** [REF, MQL5 Reference, p.PDF6660–7138]. Contêiner global; somente interseção6660–7138 lida neste ledger. Biblioteca gráfica, migração e índices não são leitura global da referência nem duplicam páginas dos filhos.

- **REF-1136 — Standard Library** [REF, Standard Library, p.PDF6660–7007]. Interseção6660–7007: controles simples/compostos, navegação e ciclo de diálogo de aplicação. Aplicação proposta ao painel de monitor, sem prova de adoção dessas classes no produto.

- **REF-3692 — Panels and Dialogs** [REF, Panels and Dialogs, p.PDF6660–7007]. Interseção6660–7007: CBmpButton até CAppDialog. Fluxo repetido dos exemplos é Create base, Create dependências, Add, Run, encaminhar ChartEvent e Destroy(reason). Proposta: separar vida da UI do monitor event-driven.

- **REF-3847 — CBmpButton** [REF, CBmpButton, p.PDF6660–6684]. Botão bitmap: exemplo associa BMP off/on, registra ON_CLICK e consulta Pressed no botão Locking(true). Aplicação proposta: ações visuais do monitor; estado pressionado não prova autorização de negociação. A abertura da classe em6659 fica fora deste lote.

- **REF-3848 — Create** [REF, Create, p.PDF6666]. CBmpButton: Cria controle em chart/subwin com nome único e retângulo x1,y1,x2,y2; bool indica sucesso. Proposta: abortar montagem incompleta e registrar nome/geometria da falha.

- **REF-3849 — Border** [REF, Border, p.PDF6667]. CBmpButton: Getter int e setter bool da largura da borda. Proposta: distinguir dimensão decorativa da área útil e verificar falha do setter.

- **REF-3850 — BmpNames** [REF, BmpNames, p.PDF6668]. CBmpButton: Associa arquivos BMP aos estados off/on, ambos argumentos padrão vazios; bool indica sucesso. Proposta: disponibilizar recursos e distinguir estado lógico de aparência.

- **REF-3851 — BmpOffName** [REF, BmpOffName, p.PDF6669]. CBmpButton: Obtém/define arquivo BMP do estado OFF; setter bool. Proposta: validar recurso da representação desligada.

- **REF-3852 — BmpOnName** [REF, BmpOnName, p.PDF6670]. CBmpButton: Obtém/define arquivo BMP do estado ON; setter bool. Proposta: não apresentar imagem ON como prova de ação efetivada.

- **REF-3853 — BmpPassiveName** [REF, BmpPassiveName, p.PDF6671]. CBmpButton: Obtém/define bitmap passivo. Proposta: recurso de estado sem hover separado do valor de negócio.

- **REF-3854 — BmpActiveName** [REF, BmpActiveName, p.PDF6672]. CBmpButton: Obtém/define bitmap ativo; ativo significa cursor sobre o controle. Proposta: não equiparar hover a monitor habilitado.

- **REF-3855 — Pressed** [REF, Pressed, p.PDF6673]. CBmpButton: Getter bool do pressionamento e setter bool que informa sucesso. Proposta: ler estado da interface sem tratá-lo como recibo de comando executado.

- **REF-3856 — Locking** [REF, Locking, p.PDF6674]. CBmpButton: Getter bool e setter void da retenção do botão; exemplo consulta Pressed após clique no botão travável. Proposta: preferências persistentes de interface, separadas da autorização do Supervisor.

- **REF-3857 — OnSetZOrder** [REF, OnSetZOrder, p.PDF6675]. CBmpButton: Handler virtual bool para OBJPROP_ZORDER: prioridade de interação; true significa evento tratado. Proposta: atualizar apresentação dependente de prioridade de interação, sem executar regra financeira por efeito visual.

- **REF-3858 — OnCreate** [REF, OnCreate, p.PDF6676]. CBmpButton: Handler virtual bool para Create: criação; true significa evento tratado. Proposta: atualizar apresentação dependente de criação, sem executar regra financeira por efeito visual.

- **REF-3859 — OnShow** [REF, OnShow, p.PDF6677]. CBmpButton: Handler virtual bool para Show: exibição; true significa evento tratado. Proposta: atualizar apresentação dependente de exibição, sem executar regra financeira por efeito visual.

- **REF-3860 — OnHide** [REF, OnHide, p.PDF6678]. CBmpButton: Handler virtual bool para Hide: ocultação; true significa evento tratado. Proposta: atualizar apresentação dependente de ocultação, sem executar regra financeira por efeito visual.

- **REF-3861 — OnMove** [REF, OnMove, p.PDF6679]. CBmpButton: Handler virtual bool para Move: movimento; true significa evento tratado. Proposta: atualizar apresentação dependente de movimento, sem executar regra financeira por efeito visual.

- **REF-3862 — OnChange** [REF, OnChange, p.PDF6680]. CBmpButton: Handler virtual bool para Change: mudança interna; true significa evento tratado. Proposta: atualizar apresentação dependente de mudança interna, sem executar regra financeira por efeito visual.

- **REF-3863 — OnActivate** [REF, OnActivate, p.PDF6681]. CBmpButton: Handler virtual bool para Activate: ativação; true significa evento tratado. Proposta: atualizar apresentação dependente de ativação, sem executar regra financeira por efeito visual.

- **REF-3864 — OnDeactivate** [REF, OnDeactivate, p.PDF6682]. CBmpButton: Handler virtual bool para Deactivate: desativação; true significa evento tratado. Proposta: atualizar apresentação dependente de desativação, sem executar regra financeira por efeito visual.

- **REF-3865 — OnMouseDown** [REF, OnMouseDown, p.PDF6683]. CBmpButton: Handler virtual bool para MouseDown: pressionamento do botão esquerdo sobre controle; true significa evento tratado. Proposta: atualizar apresentação dependente de pressionamento do botão esquerdo sobre controle, sem executar regra financeira por efeito visual.

- **REF-3866 — OnMouseUp** [REF, OnMouseUp, p.PDF6684]. CBmpButton: Handler virtual bool para MouseUp: liberação do botão esquerdo sobre controle; true significa evento tratado. Proposta: atualizar apresentação dependente de liberação do botão esquerdo sobre controle, sem executar regra financeira por efeito visual.

- **REF-3867 — CButton** [REF, CButton, p.PDF6685–6707]. Botão simples baseado em objeto Button; exemplo cria três botões, define Text, adiciona ao diálogo e torna o terceiro persistente com Locking(true). Proposta: ação de interface com identidade própria; não confundir clique com execução financeira.

- **REF-3868 — Create** [REF, Create, p.PDF6692]. CButton: Cria controle em chart/subwin com nome único e retângulo x1,y1,x2,y2; bool indica sucesso. Proposta: abortar montagem incompleta e registrar nome/geometria da falha.

- **REF-3869 — Pressed** [REF, Pressed, p.PDF6693]. CButton: Getter bool do pressionamento e setter bool que informa sucesso. Proposta: ler estado da interface sem tratá-lo como recibo de comando executado.

- **REF-3870 — Locking** [REF, Locking, p.PDF6694]. CButton: Getter bool e setter void da retenção do botão; exemplo consulta Pressed após clique no botão travável. Proposta: preferências persistentes de interface, separadas da autorização do Supervisor.

- **REF-3871 — OnSetText** [REF, OnSetText, p.PDF6695]. CButton: Handler virtual bool para OBJPROP_TEXT: texto; true significa evento tratado. Proposta: atualizar apresentação dependente de texto, sem executar regra financeira por efeito visual.

- **REF-3872 — OnSetColor** [REF, OnSetColor, p.PDF6696]. CButton: Handler virtual bool para OBJPROP_COLOR: cor do texto; true significa evento tratado. Proposta: atualizar apresentação dependente de cor do texto, sem executar regra financeira por efeito visual.

- **REF-3873 — OnSetColorBackground** [REF, OnSetColorBackground, p.PDF6697]. CButton: Handler virtual bool para OBJPROP_BGCOLOR: cor do fundo; true significa evento tratado. Proposta: atualizar apresentação dependente de cor do fundo, sem executar regra financeira por efeito visual.

- **REF-3874 — OnSetColorBorder** [REF, OnSetColorBorder, p.PDF6698]. CButton: Handler virtual bool para OBJPROP_BORDER_COLOR: cor da borda; true significa evento tratado. Proposta: atualizar apresentação dependente de cor da borda, sem executar regra financeira por efeito visual. Incongruência editorial: declaração impressa repete OnSetColorBackground; verificar nome no include.

- **REF-3875 — OnSetFont** [REF, OnSetFont, p.PDF6699]. CButton: Handler virtual bool para OBJPROP_FONT: fonte; true significa evento tratado. Proposta: atualizar apresentação dependente de fonte, sem executar regra financeira por efeito visual.

- **REF-3876 — OnSetFontSize** [REF, OnSetFontSize, p.PDF6700]. CButton: Handler virtual bool para OBJPROP_FONTSIZE: tamanho da fonte; true significa evento tratado. Proposta: atualizar apresentação dependente de tamanho da fonte, sem executar regra financeira por efeito visual.

- **REF-3877 — OnCreate** [REF, OnCreate, p.PDF6701]. CButton: Handler virtual bool para Create: criação; true significa evento tratado. Proposta: atualizar apresentação dependente de criação, sem executar regra financeira por efeito visual.

- **REF-3878 — OnShow** [REF, OnShow, p.PDF6702]. CButton: Handler virtual bool para Show: exibição; true significa evento tratado. Proposta: atualizar apresentação dependente de exibição, sem executar regra financeira por efeito visual.

- **REF-3879 — OnHide** [REF, OnHide, p.PDF6703]. CButton: Handler virtual bool para Hide: ocultação; true significa evento tratado. Proposta: atualizar apresentação dependente de ocultação, sem executar regra financeira por efeito visual.

- **REF-3880 — OnMove** [REF, OnMove, p.PDF6704]. CButton: Handler virtual bool para Move: movimento; true significa evento tratado. Proposta: atualizar apresentação dependente de movimento, sem executar regra financeira por efeito visual.

- **REF-3881 — OnResize** [REF, OnResize, p.PDF6705]. CButton: Handler virtual bool para Resize: redimensionamento; true significa evento tratado. Proposta: atualizar apresentação dependente de redimensionamento, sem executar regra financeira por efeito visual.

- **REF-3882 — OnMouseDown** [REF, OnMouseDown, p.PDF6706]. CButton: Handler virtual bool para MouseDown: pressionamento do botão esquerdo sobre controle; true significa evento tratado. Proposta: atualizar apresentação dependente de pressionamento do botão esquerdo sobre controle, sem executar regra financeira por efeito visual.

- **REF-3883 — OnMouseUp** [REF, OnMouseUp, p.PDF6707]. CButton: Handler virtual bool para MouseUp: liberação do botão esquerdo sobre controle; true significa evento tratado. Proposta: atualizar apresentação dependente de liberação do botão esquerdo sobre controle, sem executar regra financeira por efeito visual.

- **REF-3884 — CEdit** [REF, CEdit, p.PDF6708–6730]. Entrada textual baseada em Edit; exemplo libera ReadOnly(false), dimensiona pela área cliente e encaminha OnChartEvent ao diálogo. Proposta: exibir parâmetros/telemetria, validando conteúdo no domínio antes de qualquer uso.

- **REF-3885 — Create** [REF, Create, p.PDF6713]. CEdit: Cria controle em chart/subwin com nome único e retângulo x1,y1,x2,y2; bool indica sucesso. Proposta: abortar montagem incompleta e registrar nome/geometria da falha.

- **REF-3886 — ReadOnly** [REF, ReadOnly, p.PDF6714]. CEdit: Getter bool e setter bool controlam edição textual. Proposta: telemetria protegida por padrão e edição liberada apenas em campos destinados a entrada.

- **REF-3887 — TextAlign** [REF, TextAlign, p.PDF6715]. CEdit: Getter ENUM_ALIGN_MODE e setter bool do alinhamento textual. Proposta: alinhar números sem modificar precisão nem valor.

- **REF-3888 — OnObjectEndEdit** [REF, OnObjectEndEdit, p.PDF6716]. CEdit: Handler virtual bool de CHARTEVENT_OBJECT_ENDEDIT. Proposta: momento de validar texto concluído e comunicar erro, sem pressupor que digitação intermediária seja válida.

- **REF-3889 — OnSetText** [REF, OnSetText, p.PDF6717]. CEdit: Handler virtual bool para OBJPROP_TEXT: texto; true significa evento tratado. Proposta: atualizar apresentação dependente de texto, sem executar regra financeira por efeito visual.

- **REF-3890 — OnSetColor** [REF, OnSetColor, p.PDF6718]. CEdit: Handler virtual bool para OBJPROP_COLOR: cor do texto; true significa evento tratado. Proposta: atualizar apresentação dependente de cor do texto, sem executar regra financeira por efeito visual.

- **REF-3891 — OnSetColorBackground** [REF, OnSetColorBackground, p.PDF6719]. CEdit: Handler virtual bool para OBJPROP_BGCOLOR: cor do fundo; true significa evento tratado. Proposta: atualizar apresentação dependente de cor do fundo, sem executar regra financeira por efeito visual.

- **REF-3892 — OnSetColorBorder** [REF, OnSetColorBorder, p.PDF6720]. CEdit: Handler virtual bool para OBJPROP_BORDER_COLOR: cor da borda; true significa evento tratado. Proposta: atualizar apresentação dependente de cor da borda, sem executar regra financeira por efeito visual. Incongruência editorial: declaração impressa repete OnSetColorBackground; verificar nome no include.

- **REF-3893 — OnSetFont** [REF, OnSetFont, p.PDF6721]. CEdit: Handler virtual bool para OBJPROP_FONT: fonte; true significa evento tratado. Proposta: atualizar apresentação dependente de fonte, sem executar regra financeira por efeito visual.

- **REF-3894 — OnSetFontSize** [REF, OnSetFontSize, p.PDF6722]. CEdit: Handler virtual bool para OBJPROP_FONTSIZE: tamanho da fonte; true significa evento tratado. Proposta: atualizar apresentação dependente de tamanho da fonte, sem executar regra financeira por efeito visual.

- **REF-3895 — OnSetZOrder** [REF, OnSetZOrder, p.PDF6723]. CEdit: Handler virtual bool para OBJPROP_ZORDER: prioridade de interação; true significa evento tratado. Proposta: atualizar apresentação dependente de prioridade de interação, sem executar regra financeira por efeito visual.

- **REF-3896 — OnCreate** [REF, OnCreate, p.PDF6724]. CEdit: Handler virtual bool para Create: criação; true significa evento tratado. Proposta: atualizar apresentação dependente de criação, sem executar regra financeira por efeito visual.

- **REF-3897 — OnShow** [REF, OnShow, p.PDF6725]. CEdit: Handler virtual bool para Show: exibição; true significa evento tratado. Proposta: atualizar apresentação dependente de exibição, sem executar regra financeira por efeito visual.

- **REF-3898 — OnHide** [REF, OnHide, p.PDF6726]. CEdit: Handler virtual bool para Hide: ocultação; true significa evento tratado. Proposta: atualizar apresentação dependente de ocultação, sem executar regra financeira por efeito visual.

- **REF-3899 — OnMove** [REF, OnMove, p.PDF6727]. CEdit: Handler virtual bool para Move: movimento; true significa evento tratado. Proposta: atualizar apresentação dependente de movimento, sem executar regra financeira por efeito visual.

- **REF-3900 — OnResize** [REF, OnResize, p.PDF6728]. CEdit: Handler virtual bool para Resize: redimensionamento; true significa evento tratado. Proposta: atualizar apresentação dependente de redimensionamento, sem executar regra financeira por efeito visual.

- **REF-3901 — OnChange** [REF, OnChange, p.PDF6729]. CEdit: Handler virtual bool para Change: mudança interna; true significa evento tratado. Proposta: atualizar apresentação dependente de mudança interna, sem executar regra financeira por efeito visual.

- **REF-3902 — OnClick** [REF, OnClick, p.PDF6730]. CEdit: Handler virtual bool para Click: clique; true significa evento tratado. Proposta: atualizar apresentação dependente de clique, sem executar regra financeira por efeito visual.

- **REF-3903 — CPanel** [REF, CPanel, p.PDF6731–6746]. Rectangle label agrupa funções afins. Exemplo configura fundo/borda e Alignment(WND_ALIGN_CLIENT). Proposta: delimitar áreas do painel; a renderização não foi inspecionada.

- **REF-3904 — Create** [REF, Create, p.PDF6736]. CPanel: Cria controle em chart/subwin com nome único e retângulo x1,y1,x2,y2; bool indica sucesso. Proposta: abortar montagem incompleta e registrar nome/geometria da falha.

- **REF-3905 — BorderType** [REF, BorderType, p.PDF6737]. CPanel: ENUM_BORDER_TYPE seleciona tipo de borda; setter bool. Proposta: uniformizar separadores e verificar atualização do objeto.

- **REF-3906 — OnSetText** [REF, OnSetText, p.PDF6738]. CPanel: Handler virtual bool para OBJPROP_TEXT: texto; true significa evento tratado. Proposta: atualizar apresentação dependente de texto, sem executar regra financeira por efeito visual.

- **REF-3907 — OnSetColorBackground** [REF, OnSetColorBackground, p.PDF6739]. CPanel: Handler virtual bool para OBJPROP_BGCOLOR: cor do fundo; true significa evento tratado. Proposta: atualizar apresentação dependente de cor do fundo, sem executar regra financeira por efeito visual.

- **REF-3908 — OnSetColorBorder** [REF, OnSetColorBorder, p.PDF6740]. CPanel: Handler virtual bool para OBJPROP_BORDER_COLOR: cor da borda; true significa evento tratado. Proposta: atualizar apresentação dependente de cor da borda, sem executar regra financeira por efeito visual. Incongruência editorial: declaração impressa repete OnSetColorBackground; verificar nome no include.

- **REF-3909 — OnCreate** [REF, OnCreate, p.PDF6741]. CPanel: Handler virtual bool para Create: criação; true significa evento tratado. Proposta: atualizar apresentação dependente de criação, sem executar regra financeira por efeito visual.

- **REF-3910 — OnShow** [REF, OnShow, p.PDF6742]. CPanel: Handler virtual bool para Show: exibição; true significa evento tratado. Proposta: atualizar apresentação dependente de exibição, sem executar regra financeira por efeito visual.

- **REF-3911 — OnHide** [REF, OnHide, p.PDF6743]. CPanel: Handler virtual bool para Hide: ocultação; true significa evento tratado. Proposta: atualizar apresentação dependente de ocultação, sem executar regra financeira por efeito visual.

- **REF-3912 — OnMove** [REF, OnMove, p.PDF6744]. CPanel: Handler virtual bool para Move: movimento; true significa evento tratado. Proposta: atualizar apresentação dependente de movimento, sem executar regra financeira por efeito visual.

- **REF-3913 — OnResize** [REF, OnResize, p.PDF6745]. CPanel: Handler virtual bool para Resize: redimensionamento; true significa evento tratado. Proposta: atualizar apresentação dependente de redimensionamento, sem executar regra financeira por efeito visual.

- **REF-3914 — OnChange** [REF, OnChange, p.PDF6746]. CPanel: Handler virtual bool para Change: mudança interna; true significa evento tratado. Proposta: atualizar apresentação dependente de mudança interna, sem executar regra financeira por efeito visual.

- **REF-3915 — CPicture** [REF, CPicture, p.PDF6747–6759]. Imagem simples baseada em Bitmap Label; exemplo usa arquivo euro.bmp e associa ON_CLICK. Proposta: ícone informativo; presença do bitmap e aparência exigem teste nativo.

- **REF-3916 — Create** [REF, Create, p.PDF6752]. CPicture: Cria controle em chart/subwin com nome único e retângulo x1,y1,x2,y2; bool indica sucesso. Proposta: abortar montagem incompleta e registrar nome/geometria da falha.

- **REF-3917 — Border** [REF, Border, p.PDF6753]. CPicture: Getter int e setter bool da largura da borda. Proposta: distinguir dimensão decorativa da área útil e verificar falha do setter.

- **REF-3918 — BmpName** [REF, BmpName, p.PDF6754]. CPicture: Getter string e setter bool do arquivo de imagem. Proposta: mapear recurso estático disponível no terminal.

- **REF-3919 — OnCreate** [REF, OnCreate, p.PDF6755]. CPicture: Handler virtual bool para Create: criação; true significa evento tratado. Proposta: atualizar apresentação dependente de criação, sem executar regra financeira por efeito visual.

- **REF-3920 — OnShow** [REF, OnShow, p.PDF6756]. CPicture: Handler virtual bool para Show: exibição; true significa evento tratado. Proposta: atualizar apresentação dependente de exibição, sem executar regra financeira por efeito visual.

- **REF-3921 — OnHide** [REF, OnHide, p.PDF6757]. CPicture: Handler virtual bool para Hide: ocultação; true significa evento tratado. Proposta: atualizar apresentação dependente de ocultação, sem executar regra financeira por efeito visual.

- **REF-3922 — OnMove** [REF, OnMove, p.PDF6758]. CPicture: Handler virtual bool para Move: movimento; true significa evento tratado. Proposta: atualizar apresentação dependente de movimento, sem executar regra financeira por efeito visual.

- **REF-3923 — OnChange** [REF, OnChange, p.PDF6759]. CPicture: Handler virtual bool para Change: mudança interna; true significa evento tratado. Proposta: atualizar apresentação dependente de mudança interna, sem executar regra financeira por efeito visual.

- **REF-3924 — CScroll** [REF, CScroll, p.PDF6760–6779]. Base composta de barras; não é controle independente, usa CScrollH/CScrollV. Mantém limites/posição e botões fundo/inc/dec/thumb. Proposta: navegação de dados sem alterar estado de negócio.

- **REF-3925 — Create** [REF, Create, p.PDF6762]. CScroll: Cria controle em chart/subwin com nome único e retângulo x1,y1,x2,y2; bool indica sucesso. Proposta: abortar montagem incompleta e registrar nome/geometria da falha.

- **REF-3926 — OnEvent** [REF, OnEvent, p.PDF6763]. CScroll: Handler virtual bool recebe id e referências const long/double/string dos parâmetros do evento. Proposta: preservar tipos e encaminhar eventos ao controle correto; true significa evento tratado.

- **REF-3927 — MinPos** [REF, MinPos, p.PDF6764]. CScroll: Getter int e setter void da posição mínima da barra. Proposta: fixar origem da navegação e validar coerência com máximo.

- **REF-3928 — MaxPos** [REF, MaxPos, p.PDF6765]. CScroll: Getter int e setter void da posição máxima da barra. Proposta: derivar limite de navegação do conteúdo, sem confundi-lo com altura em pixels.

- **REF-3929 — CurrPos** [REF, CurrPos, p.PDF6766]. CScroll: Getter int e setter void da posição atual. Proposta: usar como cursor de apresentação, separado do índice absoluto de dados.

- **REF-3930 — CreateBack** [REF, CreateBack, p.PDF6767]. CScroll: Cria dependência de fundo; virtual bool sinaliza sucesso. Proposta: falha na dependência precisa impedir painel parcialmente funcional.

- **REF-3931 — CreateInc** [REF, CreateInc, p.PDF6768]. CScroll: Cria botão de incremento; virtual bool sinaliza sucesso. Proposta: validar montagem da navegação incremental.

- **REF-3932 — CreateDec** [REF, CreateDec, p.PDF6769]. CScroll: Cria botão de decremento; virtual bool sinaliza sucesso. Proposta: validar montagem da navegação reversa.

- **REF-3933 — CreateThumb** [REF, CreateThumb, p.PDF6770]. CScroll: Cria botão arrastável da barra; virtual bool. Proposta: manter arraste como navegação, sem disparar ação de negócio.

- **REF-3934 — OnClickInc** [REF, OnClickInc, p.PDF6771]. CScroll: Handler virtual bool de clique no incremento. Proposta: atualizar navegação/valor candidato e validar limites.

- **REF-3935 — OnClickDec** [REF, OnClickDec, p.PDF6772]. CScroll: Handler virtual bool de clique no decremento. Proposta: impedir redução fora do intervalo do conteúdo.

- **REF-3936 — OnShow** [REF, OnShow, p.PDF6773]. CScroll: Handler virtual bool para Show: exibição; true significa evento tratado. Proposta: atualizar apresentação dependente de exibição, sem executar regra financeira por efeito visual.

- **REF-3937 — OnHide** [REF, OnHide, p.PDF6774]. CScroll: Handler virtual bool para Hide: ocultação; true significa evento tratado. Proposta: atualizar apresentação dependente de ocultação, sem executar regra financeira por efeito visual.

- **REF-3938 — OnChangePos** [REF, OnChangePos, p.PDF6775]. CScroll: Handler virtual bool de mudança de posição. Proposta: atualizar conteúdo apresentado; na base CScroll não faz nada e retorna true.

- **REF-3939 — OnThumbDragStart** [REF, OnThumbDragStart, p.PDF6776]. CScroll: Handler virtual bool no início do arraste. Proposta: capturar origem de navegação sem efetivar comandos externos.

- **REF-3940 — OnThumbDragProcess** [REF, OnThumbDragProcess, p.PDF6777]. CScroll: Handler virtual bool recebe x/y atuais do cursor durante movimento. Proposta: converter geometria para posição e limitar atualização de apresentação.

- **REF-3941 — OnThumbDragEnd** [REF, OnThumbDragEnd, p.PDF6778]. CScroll: Handler virtual bool ao terminar arraste. Proposta: consolidar posição de exibição, sem inferir confirmação de operações.

- **REF-3942 — CalcPos** [REF, CalcPos, p.PDF6779]. CScroll: Método virtual int converte coordenada int em posição da barra. Proposta: manter conversão por eixo no controle especializado.

- **REF-3943 — CScrollV** [REF, CScrollV, p.PDF6780–6794]. Especialização vertical de CScroll. Exemplo configura MinPos(0), MaxPos(10) e ON_SCROLL_INC/DEC que consultam CurrPos. Proposta: navegar registros extensos; não inferir quantidade de dados da altura visual.

- **REF-3944 — CreateInc** [REF, CreateInc, p.PDF6786]. CScrollV: Cria botão de incremento; virtual bool sinaliza sucesso. Proposta: validar montagem da navegação incremental.

- **REF-3945 — CreateDec** [REF, CreateDec, p.PDF6787]. CScrollV: Cria botão de decremento; virtual bool sinaliza sucesso. Proposta: validar montagem da navegação reversa.

- **REF-3946 — CreateThumb** [REF, CreateThumb, p.PDF6788]. CScrollV: Cria botão arrastável da barra; virtual bool. Proposta: manter arraste como navegação, sem disparar ação de negócio.

- **REF-3947 — OnResize** [REF, OnResize, p.PDF6789]. CScrollV: Handler virtual bool para Resize: redimensionamento; true significa evento tratado. Proposta: atualizar apresentação dependente de redimensionamento, sem executar regra financeira por efeito visual.

- **REF-3948 — OnChangePos** [REF, OnChangePos, p.PDF6790]. CScrollV: Handler virtual bool de mudança de posição. Proposta: atualizar conteúdo apresentado. A especialização fornece o tratamento de posição.

- **REF-3949 — OnThumbDragStart** [REF, OnThumbDragStart, p.PDF6791]. CScrollV: Handler virtual bool no início do arraste. Proposta: capturar origem de navegação sem efetivar comandos externos.

- **REF-3950 — OnThumbDragProcess** [REF, OnThumbDragProcess, p.PDF6792]. CScrollV: Handler virtual bool recebe x/y atuais do cursor durante movimento. Proposta: converter geometria para posição e limitar atualização de apresentação.

- **REF-3951 — OnThumbDragEnd** [REF, OnThumbDragEnd, p.PDF6793]. CScrollV: Handler virtual bool ao terminar arraste. Proposta: consolidar posição de exibição, sem inferir confirmação de operações.

- **REF-3952 — CalcPos** [REF, CalcPos, p.PDF6794]. CScrollV: Método virtual int converte coordenada int em posição da barra. Proposta: manter conversão por eixo no controle especializado.

- **REF-3953 — CScrollH** [REF, CScrollH, p.PDF6795–6809]. Especialização horizontal; exemplo conserva nome de membro m_scroll_v apesar do tipo horizontal e configura limites0–10. Proposta: navegar colunas largas, mantendo eixo explícito na implementação.

- **REF-3954 — CreateInc** [REF, CreateInc, p.PDF6801]. CScrollH: Cria botão de incremento; virtual bool sinaliza sucesso. Proposta: validar montagem da navegação incremental.

- **REF-3955 — CreateDec** [REF, CreateDec, p.PDF6802]. CScrollH: Cria botão de decremento; virtual bool sinaliza sucesso. Proposta: validar montagem da navegação reversa.

- **REF-3956 — CreateThumb** [REF, CreateThumb, p.PDF6803]. CScrollH: Cria botão arrastável da barra; virtual bool. Proposta: manter arraste como navegação, sem disparar ação de negócio.

- **REF-3957 — OnResize** [REF, OnResize, p.PDF6804]. CScrollH: Handler virtual bool para Resize: redimensionamento; true significa evento tratado. Proposta: atualizar apresentação dependente de redimensionamento, sem executar regra financeira por efeito visual.

- **REF-3958 — OnChangePos** [REF, OnChangePos, p.PDF6805]. CScrollH: Handler virtual bool de mudança de posição. Proposta: atualizar conteúdo apresentado. A especialização fornece o tratamento de posição.

- **REF-3959 — OnThumbDragStart** [REF, OnThumbDragStart, p.PDF6806]. CScrollH: Handler virtual bool no início do arraste. Proposta: capturar origem de navegação sem efetivar comandos externos.

- **REF-3960 — OnThumbDragProcess** [REF, OnThumbDragProcess, p.PDF6807]. CScrollH: Handler virtual bool recebe x/y atuais do cursor durante movimento. Proposta: converter geometria para posição e limitar atualização de apresentação.

- **REF-3961 — OnThumbDragEnd** [REF, OnThumbDragEnd, p.PDF6808]. CScrollH: Handler virtual bool ao terminar arraste. Proposta: consolidar posição de exibição, sem inferir confirmação de operações.

- **REF-3962 — CalcPos** [REF, CalcPos, p.PDF6809]. CScrollH: Método virtual int converte coordenada int em posição da barra. Proposta: manter conversão por eixo no controle especializado.

- **REF-3963 — CWndClient** [REF, CWndClient, p.PDF6810–6832]. Área cliente composta com barras vertical/horizontal, base de CheckGroup/ListView/RadioGroup. Proposta: separar área visível de conteúdo total e recalcular geometria quando barras aparecem.

- **REF-3964 — Create** [REF, Create, p.PDF6813]. CWndClient: Cria controle em chart/subwin com nome único e retângulo x1,y1,x2,y2; bool indica sucesso. Proposta: abortar montagem incompleta e registrar nome/geometria da falha.

- **REF-3965 — OnEvent** [REF, OnEvent, p.PDF6814]. CWndClient: Handler virtual bool recebe id e referências const long/double/string dos parâmetros do evento. Proposta: preservar tipos e encaminhar eventos ao controle correto; true significa evento tratado.

- **REF-3966 — ColorBackground** [REF, ColorBackground, p.PDF6815]. CWndClient: Setter bool recebe color do fundo. Proposta: aplicar tema ao cliente e tratar eventual falha.

- **REF-3967 — ColorBorder** [REF, ColorBorder, p.PDF6816]. CWndClient: Setter bool recebe color da borda. Proposta: preservar contraste sem usar cor como único portador de estado.

- **REF-3968 — BorderType** [REF, BorderType, p.PDF6817]. CWndClient: ENUM_BORDER_TYPE seleciona tipo de borda; setter bool. Proposta: uniformizar separadores e verificar atualização do objeto.

- **REF-3969 — VScrolled** [REF, VScrolled, p.PDF6818]. CWndClient: Getter bool informa uso da barra vertical e setter bool configura flag. Proposta: ajustar conteúdo visível quando navegação vertical for habilitada.

- **REF-3970 — HScrolled** [REF, HScrolled, p.PDF6819]. CWndClient: Getter bool informa uso da barra horizontal e setter bool configura flag. Proposta: acomodar colunas sem alterar dados.

- **REF-3971 — CreateBack** [REF, CreateBack, p.PDF6820]. CWndClient: Cria dependência de fundo; virtual bool sinaliza sucesso. Proposta: falha na dependência precisa impedir painel parcialmente funcional.

- **REF-3972 — CreateScrollV** [REF, CreateScrollV, p.PDF6821]. CWndClient: Cria dependência barra vertical; virtual bool. Proposta: acompanhar falha da área navegável.

- **REF-3973 — CreateScrollH** [REF, CreateScrollH, p.PDF6822]. CWndClient: Cria dependência barra horizontal; virtual bool. Proposta: acompanhar falha da navegação lateral.

- **REF-3974 — OnResize** [REF, OnResize, p.PDF6823]. CWndClient: Handler virtual bool para Resize: redimensionamento; true significa evento tratado. Proposta: atualizar apresentação dependente de redimensionamento, sem executar regra financeira por efeito visual.

- **REF-3975 — OnVScrollShow** [REF, OnVScrollShow, p.PDF6824]. CWndClient: Handler virtual bool para VScroll Show: exibição da barra vertical; true significa evento tratado. Proposta: atualizar apresentação dependente de exibição da barra vertical, sem executar regra financeira por efeito visual. Nesta base o método não faz nada e sempre retorna true; processamento aceito não comprova deslocamento.

- **REF-3976 — OnVScrollHide** [REF, OnVScrollHide, p.PDF6825]. CWndClient: Handler virtual bool para VScroll Hide: ocultação da barra vertical; true significa evento tratado. Proposta: atualizar apresentação dependente de ocultação da barra vertical, sem executar regra financeira por efeito visual. Nesta base o método não faz nada e sempre retorna true; processamento aceito não comprova deslocamento.

- **REF-3977 — OnHScrollShow** [REF, OnHScrollShow, p.PDF6826]. CWndClient: Handler virtual bool para HScroll Show: exibição da barra horizontal; true significa evento tratado. Proposta: atualizar apresentação dependente de exibição da barra horizontal, sem executar regra financeira por efeito visual. Nesta base o método não faz nada e sempre retorna true; processamento aceito não comprova deslocamento.

- **REF-3978 — OnHScrollHide** [REF, OnHScrollHide, p.PDF6827]. CWndClient: Handler virtual bool para HScroll Hide: ocultação da barra horizontal; true significa evento tratado. Proposta: atualizar apresentação dependente de ocultação da barra horizontal, sem executar regra financeira por efeito visual. Nesta base o método não faz nada e sempre retorna true; processamento aceito não comprova deslocamento.

- **REF-3979 — OnScrollLineDown** [REF, OnScrollLineDown, p.PDF6828]. CWndClient: Handler virtual bool para ScrollLineDown: navegação uma linha abaixo; true significa evento tratado. Proposta: atualizar apresentação dependente de navegação uma linha abaixo, sem executar regra financeira por efeito visual. Nesta base o método não faz nada e sempre retorna true; processamento aceito não comprova deslocamento.

- **REF-3980 — OnScrollLineUp** [REF, OnScrollLineUp, p.PDF6829]. CWndClient: Handler virtual bool para ScrollLineUp: navegação uma linha acima; true significa evento tratado. Proposta: atualizar apresentação dependente de navegação uma linha acima, sem executar regra financeira por efeito visual. Nesta base o método não faz nada e sempre retorna true; processamento aceito não comprova deslocamento.

- **REF-3981 — OnScrollLineLeft** [REF, OnScrollLineLeft, p.PDF6830]. CWndClient: Handler virtual bool para ScrollLineLeft: navegação uma coluna à esquerda; true significa evento tratado. Proposta: atualizar apresentação dependente de navegação uma coluna à esquerda, sem executar regra financeira por efeito visual. Nesta base o método não faz nada e sempre retorna true; processamento aceito não comprova deslocamento.

- **REF-3982 — OnScrollLineRight** [REF, OnScrollLineRight, p.PDF6831]. CWndClient: Handler virtual bool para ScrollLineRight: navegação uma coluna à direita; true significa evento tratado. Proposta: atualizar apresentação dependente de navegação uma coluna à direita, sem executar regra financeira por efeito visual. Nesta base o método não faz nada e sempre retorna true; processamento aceito não comprova deslocamento.

- **REF-3983 — Rebound** [REF, Rebound, p.PDF6832]. CWndClient: Redefine geometria usando CRect. CWndClient imprime ReBound void; CAppDialog Rebound bool. Proposta: conferir grafia e retorno específicos antes de sobrescrever.

- **REF-3984 — CListView** [REF, CListView, p.PDF6833–6856]. Lista composta derivada de CWndClient; exemplo adiciona16 textos e registra ON_CHANGE. Valor long e seleção por índice/texto/valor são conceitos distintos. Proposta: selecionar programa/registro por identificador estável.

- **REF-3985 — Create** [REF, Create, p.PDF6839]. CListView: Cria controle em chart/subwin com nome único e retângulo x1,y1,x2,y2; bool indica sucesso. Proposta: abortar montagem incompleta e registrar nome/geometria da falha.

- **REF-3986 — OnEvent** [REF, OnEvent, p.PDF6840]. CListView: Handler virtual bool recebe id e referências const long/double/string dos parâmetros do evento. Proposta: preservar tipos e encaminhar eventos ao controle correto; true significa evento tratado.

- **REF-3987 — TotalView** [REF, TotalView, p.PDF6841]. CListView: Setter bool do número de itens exibidos; documentação permite especificar somente uma vez. Proposta: decidir capacidade no início da lista, sem assumir redimensionamento dinâmico irrestrito.

- **REF-3988 — AddItem** [REF, AddItem, p.PDF6842]. CListView: Adiciona texto string e valor long; bool informa sucesso. Proposta: conferir cada inserção e usar valor estável independente da posição.

- **REF-3989 — Select** [REF, Select, p.PDF6843]. CListView: Seleciona item por índice. Proposta: validar faixa do índice antes de converter seleção em entidade do monitor.

- **REF-3990 — SelectByText** [REF, SelectByText, p.PDF6844]. CListView: Seleciona item pelo texto, retornando bool. Proposta: tratar ausência/ambiguidade de rótulos; preferir valor estável para lógica.

- **REF-3991 — SelectByValue** [REF, SelectByValue, p.PDF6845]. CListView: Seleciona por valor long, retornando bool. Proposta: vincular programa a identificador estável em vez de posição da lista.

- **REF-3992 — Value** [REF, Value, p.PDF6846]. CListView: Consulta valor associado ao controle/seleção. Proposta: interpretar conforme o tipo do controle, sem confundir estado booleano, máscara e identificador. Getter long da seleção atual.

- **REF-3993 — CreateRow** [REF, CreateRow, p.PDF6847]. CListView: Cria linha por índice int; bool. Proposta: tratar falha de construção de linha como falha de apresentação.

- **REF-3994 — OnResize** [REF, OnResize, p.PDF6848]. CListView: Handler virtual bool para Resize: redimensionamento; true significa evento tratado. Proposta: atualizar apresentação dependente de redimensionamento, sem executar regra financeira por efeito visual.

- **REF-3995 — OnVScrollShow** [REF, OnVScrollShow, p.PDF6849]. CListView: Handler virtual bool para VScroll Show: exibição da barra vertical; true significa evento tratado. Proposta: atualizar apresentação dependente de exibição da barra vertical, sem executar regra financeira por efeito visual.

- **REF-3996 — OnVScrollHide** [REF, OnVScrollHide, p.PDF6850]. CListView: Handler virtual bool para VScroll Hide: ocultação da barra vertical; true significa evento tratado. Proposta: atualizar apresentação dependente de ocultação da barra vertical, sem executar regra financeira por efeito visual.

- **REF-3997 — OnScrollLineDown** [REF, OnScrollLineDown, p.PDF6851]. CListView: Handler virtual bool para ScrollLineDown: navegação uma linha abaixo; true significa evento tratado. Proposta: atualizar apresentação dependente de navegação uma linha abaixo, sem executar regra financeira por efeito visual.

- **REF-3998 — OnScrollLineUp** [REF, OnScrollLineUp, p.PDF6852]. CListView: Handler virtual bool para ScrollLineUp: navegação uma linha acima; true significa evento tratado. Proposta: atualizar apresentação dependente de navegação uma linha acima, sem executar regra financeira por efeito visual.

- **REF-3999 — OnItemClick** [REF, OnItemClick, p.PDF6853]. CListView: Handler virtual de clique em linha especificada de CListView. A assinatura impressa tem parênteses inconsistentes; proposta: conferir include antes de sobrescrever.

- **REF-4000 — Redraw** [REF, Redraw, p.PDF6854]. CListView: Redesenha controle/grupo e retorna bool. Proposta: atualizar apresentação após mudança de dados e registrar falha, sem confundir com ChartRedraw.

- **REF-4001 — RowState** [REF, RowState, p.PDF6855]. CListView: Setter bool de estado de linha/item recebe index int e select bool. Proposta: distinguir marcação visual da entidade selecionada no domínio.

- **REF-4002 — CheckView** [REF, CheckView, p.PDF6856]. CListView: Retorna bool da visibilidade da linha selecionada. Proposta: decidir navegação para a seleção sem concluir que todo conteúdo esteja visível.

- **REF-4003 — CComboBox** [REF, CComboBox, p.PDF6857–6878]. Combina exibição estática e lista suspensa; exemplo ON_CHANGE e criação de itens. Proposta: seleção de programa/perfil do monitor; mudança de seleção não arma Supervisor. Exemplo usa ItemAdd enquanto API lista AddItem: verificar include antes de reutilizar.

- **REF-4004 — Create** [REF, Create, p.PDF6863]. CComboBox: Cria controle em chart/subwin com nome único e retângulo x1,y1,x2,y2; bool indica sucesso. Proposta: abortar montagem incompleta e registrar nome/geometria da falha.

- **REF-4005 — OnEvent** [REF, OnEvent, p.PDF6864]. CComboBox: Handler virtual bool recebe id e referências const long/double/string dos parâmetros do evento. Proposta: preservar tipos e encaminhar eventos ao controle correto; true significa evento tratado.

- **REF-4006 — AddItem** [REF, AddItem, p.PDF6865]. CComboBox: Adiciona texto string e valor long; bool informa sucesso. Proposta: conferir cada inserção e usar valor estável independente da posição.

- **REF-4007 — ListViewItems** [REF, ListViewItems, p.PDF6866]. CComboBox: Configura número de elementos da lista suspensa. Assinatura void conflita com texto de retorno bool; proposta: conferir ComboBox.mqh antes de usar retorno.

- **REF-4008 — Select** [REF, Select, p.PDF6867]. CComboBox: Seleciona item por índice. Proposta: validar faixa do índice antes de converter seleção em entidade do monitor.

- **REF-4009 — SelectByText** [REF, SelectByText, p.PDF6868]. CComboBox: Seleciona item pelo texto, retornando bool. Proposta: tratar ausência/ambiguidade de rótulos; preferir valor estável para lógica.

- **REF-4010 — SelectByValue** [REF, SelectByValue, p.PDF6869]. CComboBox: Seleciona por valor long, retornando bool. Proposta: vincular programa a identificador estável em vez de posição da lista.

- **REF-4011 — Value** [REF, Value, p.PDF6870]. CComboBox: Consulta valor associado ao controle/seleção. Proposta: interpretar conforme o tipo do controle, sem confundir estado booleano, máscara e identificador. Getter long da seleção atual.

- **REF-4012 — CreateEdit** [REF, CreateEdit, p.PDF6871]. CComboBox: Cria dependência de edição; virtual bool. Proposta: validar montagem de campo antes de aceitar entrada.

- **REF-4013 — CreateButton** [REF, CreateButton, p.PDF6872]. CComboBox: Cria botão dependente; nas classes de grupo recebe índice para criar item. Proposta: validar dependências de cada escolha.

- **REF-4014 — CreateList** [REF, CreateList, p.PDF6873]. CComboBox: Cria lista dependente do combo; virtual bool. Proposta: falha deve impedir seletor aparentemente operacional.

- **REF-4015 — OnClickEdit** [REF, OnClickEdit, p.PDF6874]. CComboBox: Handler virtual bool de clique no campo do combo. Proposta: controlar abertura/seleção da lista sem efeitos financeiros.

- **REF-4016 — OnClickButton** [REF, OnClickButton, p.PDF6875]. CComboBox: Handler de clique no botão dependente. Proposta: convergir interação para atualização de estado do controle.

- **REF-4017 — OnChangeList** [REF, OnChangeList, p.PDF6876]. CComboBox: Handler virtual bool da alteração da lista do combo. Proposta: atualizar escolha exibida e validar identificador antes de usá-lo.

- **REF-4018 — ListShow** [REF, ListShow, p.PDF6877]. CComboBox: Mostra lista suspensa; virtual bool. Proposta: tratar sobreposição/visibilidade no painel em teste nativo.

- **REF-4019 — ListHide** [REF, ListHide, p.PDF6878]. CComboBox: Oculta lista suspensa; virtual bool. Proposta: fechar apresentação sem apagar escolha de domínio.

- **REF-4020 — CCheckBox** [REF, CCheckBox, p.PDF6879–6894]. Controle composto booleano com botão e label. Checked é estado; Value int é dado associado. Exemplo inicia segundo item marcado e informa estado no ON_CHANGE. Proposta: preferências de exibição com validação independente.

- **REF-4021 — Create** [REF, Create, p.PDF6885]. CCheckBox: Cria controle em chart/subwin com nome único e retângulo x1,y1,x2,y2; bool indica sucesso. Proposta: abortar montagem incompleta e registrar nome/geometria da falha.

- **REF-4022 — OnEvent** [REF, OnEvent, p.PDF6886]. CCheckBox: Handler virtual bool recebe id e referências const long/double/string dos parâmetros do evento. Proposta: preservar tipos e encaminhar eventos ao controle correto; true significa evento tratado.

- **REF-4023 — Text** [REF, Text, p.PDF6887]. CCheckBox: Getter string e setter bool do texto do label; no checkbox usa OBJPROP_TEXT. Proposta: rótulo legível separado do identificador associado.

- **REF-4024 — Color** [REF, Color, p.PDF6888]. CCheckBox: Getter color e setter bool da cor do label; checkbox usa OBJPROP_COLOR. Proposta: tema de texto sem codificar regras somente por cor.

- **REF-4025 — Checked** [REF, Checked, p.PDF6889]. CCheckBox: Getter bool e setter bool do estado de checkbox. Proposta: preferência binária de apresentação; não é autorização de negociação.

- **REF-4026 — Value** [REF, Value, p.PDF6890]. CCheckBox: Consulta valor associado ao controle/seleção. Proposta: interpretar conforme o tipo do controle, sem confundir estado booleano, máscara e identificador. Getter int e setter void; distinto de Checked(bool).

- **REF-4027 — CreateButton** [REF, CreateButton, p.PDF6891]. CCheckBox: Cria botão dependente; nas classes de grupo recebe índice para criar item. Proposta: validar dependências de cada escolha.

- **REF-4028 — CreateLabel** [REF, CreateLabel, p.PDF6892]. CCheckBox: Cria label dependente, virtual bool. Proposta: validar rótulo da opção para evitar controles sem descrição.

- **REF-4029 — OnClickButton** [REF, OnClickButton, p.PDF6893]. CCheckBox: Handler de clique no botão dependente. Proposta: convergir interação para atualização de estado do controle.

- **REF-4030 — OnClickLabel** [REF, OnClickLabel, p.PDF6894]. CCheckBox: Handler virtual bool de clique no rótulo. Proposta: oferecer mesma semântica da ação no botão sem duplicar efeito.

- **REF-4031 — CCheckGroup** [REF, CCheckGroup, p.PDF6895–6912]. Grupo permite editar flags; exemplo associa1<<i a cinco itens e seleciona0 e2. Value depende do conjunto. Proposta: múltiplos filtros simultâneos; não usar máscara como autorização de atuação.

- **REF-4032 — Create** [REF, Create, p.PDF6901]. CCheckGroup: Cria controle em chart/subwin com nome único e retângulo x1,y1,x2,y2; bool indica sucesso. Proposta: abortar montagem incompleta e registrar nome/geometria da falha.

- **REF-4033 — OnEvent** [REF, OnEvent, p.PDF6902]. CCheckGroup: Handler virtual bool recebe id e referências const long/double/string dos parâmetros do evento. Proposta: preservar tipos e encaminhar eventos ao controle correto; true significa evento tratado.

- **REF-4034 — AddItem** [REF, AddItem, p.PDF6903]. CCheckGroup: Adiciona texto string e valor long; bool informa sucesso. Proposta: conferir cada inserção e usar valor estável independente da posição.

- **REF-4035 — Value** [REF, Value, p.PDF6904]. CCheckGroup: Consulta valor associado ao controle/seleção. Proposta: interpretar conforme o tipo do controle, sem confundir estado booleano, máscara e identificador. Getter long depende dos estados de todos os itens; exemplo usa bits1<<i.

- **REF-4036 — CreateButton** [REF, CreateButton, p.PDF6905]. CCheckGroup: Cria botão dependente; nas classes de grupo recebe índice para criar item. Proposta: validar dependências de cada escolha.

- **REF-4037 — OnVScrollShow** [REF, OnVScrollShow, p.PDF6906]. CCheckGroup: Handler virtual bool para VScroll Show: exibição da barra vertical; true significa evento tratado. Proposta: atualizar apresentação dependente de exibição da barra vertical, sem executar regra financeira por efeito visual.

- **REF-4038 — OnVScrollHide** [REF, OnVScrollHide, p.PDF6907]. CCheckGroup: Handler virtual bool para VScroll Hide: ocultação da barra vertical; true significa evento tratado. Proposta: atualizar apresentação dependente de ocultação da barra vertical, sem executar regra financeira por efeito visual.

- **REF-4039 — OnScrollLineDown** [REF, OnScrollLineDown, p.PDF6908]. CCheckGroup: Handler virtual bool para ScrollLineDown: navegação uma linha abaixo; true significa evento tratado. Proposta: atualizar apresentação dependente de navegação uma linha abaixo, sem executar regra financeira por efeito visual.

- **REF-4040 — OnScrollLineUp** [REF, OnScrollLineUp, p.PDF6909]. CCheckGroup: Handler virtual bool para ScrollLineUp: navegação uma linha acima; true significa evento tratado. Proposta: atualizar apresentação dependente de navegação uma linha acima, sem executar regra financeira por efeito visual.

- **REF-4041 — OnChangeItem** [REF, OnChangeItem, p.PDF6910]. CCheckGroup: Handler virtual bool recebe índice int do item alterado. Proposta: atualizar seleção/máscara de modo determinístico.

- **REF-4042 — Redraw** [REF, Redraw, p.PDF6911]. CCheckGroup: Redesenha controle/grupo e retorna bool. Proposta: atualizar apresentação após mudança de dados e registrar falha, sem confundir com ChartRedraw.

- **REF-4043 — RowState** [REF, RowState, p.PDF6912]. CCheckGroup: Setter bool de estado de linha/item recebe index int e select bool. Proposta: distinguir marcação visual da entidade selecionada no domínio.

- **REF-4044 — CRadioButton** [REF, CRadioButton, p.PDF6913–6923]. Item composto usado dentro de CRadioGroup, não isoladamente segundo descrição. Proposta: manter exclusividade no grupo, sem assumir que State(bool) sozinho imponha regra global.

- **REF-4045 — Create** [REF, Create, p.PDF6915]. CRadioButton: Cria controle em chart/subwin com nome único e retângulo x1,y1,x2,y2; bool indica sucesso. Proposta: abortar montagem incompleta e registrar nome/geometria da falha.

- **REF-4046 — OnEvent** [REF, OnEvent, p.PDF6916]. CRadioButton: Handler virtual bool recebe id e referências const long/double/string dos parâmetros do evento. Proposta: preservar tipos e encaminhar eventos ao controle correto; true significa evento tratado.

- **REF-4047 — Text** [REF, Text, p.PDF6917]. CRadioButton: Getter string e setter bool do texto do label; no checkbox usa OBJPROP_TEXT. Proposta: rótulo legível separado do identificador associado.

- **REF-4048 — Color** [REF, Color, p.PDF6918]. CRadioButton: Getter color e setter bool da cor do label; checkbox usa OBJPROP_COLOR. Proposta: tema de texto sem codificar regras somente por cor.

- **REF-4049 — State** [REF, State, p.PDF6919]. CRadioButton: Getter bool e setter bool do estado de RadioButton. Proposta: exclusividade é responsabilidade do grupo, não de valor isolado.

- **REF-4050 — CreateButton** [REF, CreateButton, p.PDF6920]. CRadioButton: Cria botão dependente; nas classes de grupo recebe índice para criar item. Proposta: validar dependências de cada escolha.

- **REF-4051 — CreateLabel** [REF, CreateLabel, p.PDF6921]. CRadioButton: Cria label dependente, virtual bool. Proposta: validar rótulo da opção para evitar controles sem descrição.

- **REF-4052 — OnClickButton** [REF, OnClickButton, p.PDF6922]. CRadioButton: Handler de clique no botão dependente. Proposta: convergir interação para atualização de estado do controle.

- **REF-4053 — OnClickLabel** [REF, OnClickLabel, p.PDF6923]. CRadioButton: Handler virtual bool de clique no rótulo. Proposta: oferecer mesma semântica da ação no botão sem duplicar efeito.

- **REF-4054 — CRadioGroup** [REF, CRadioGroup, p.PDF6924–6942]. Grupo para campo enumerável. Exemplo associa valores1<<i e seleciona1<<2; essa escolha de representação não transforma o grupo em conjunto de flags. Proposta: modo de exibição mutuamente exclusivo.

- **REF-4055 — Create** [REF, Create, p.PDF6930]. CRadioGroup: Cria controle em chart/subwin com nome único e retângulo x1,y1,x2,y2; bool indica sucesso. Proposta: abortar montagem incompleta e registrar nome/geometria da falha.

- **REF-4056 — OnEvent** [REF, OnEvent, p.PDF6931]. CRadioGroup: Handler virtual bool recebe id e referências const long/double/string dos parâmetros do evento. Proposta: preservar tipos e encaminhar eventos ao controle correto; true significa evento tratado.

- **REF-4057 — AddItem** [REF, AddItem, p.PDF6932]. CRadioGroup: Adiciona texto string e valor long; bool informa sucesso. Proposta: conferir cada inserção e usar valor estável independente da posição.

- **REF-4058 — Value** [REF, Value, p.PDF6933]. CRadioGroup: Consulta valor associado ao controle/seleção. Proposta: interpretar conforme o tipo do controle, sem confundir estado booleano, máscara e identificador. Getter long depende dos RadioButtons; representar enumeração e não múltiplas flags simultâneas.

- **REF-4059 — CreateButton** [REF, CreateButton, p.PDF6934]. CRadioGroup: Cria botão dependente; nas classes de grupo recebe índice para criar item. Proposta: validar dependências de cada escolha.

- **REF-4060 — OnVScrollShow** [REF, OnVScrollShow, p.PDF6935]. CRadioGroup: Handler virtual bool para VScroll Show: exibição da barra vertical; true significa evento tratado. Proposta: atualizar apresentação dependente de exibição da barra vertical, sem executar regra financeira por efeito visual.

- **REF-4061 — OnVScrollHide** [REF, OnVScrollHide, p.PDF6936]. CRadioGroup: Handler virtual bool para VScroll Hide: ocultação da barra vertical; true significa evento tratado. Proposta: atualizar apresentação dependente de ocultação da barra vertical, sem executar regra financeira por efeito visual.

- **REF-4062 — OnScrollLineDown** [REF, OnScrollLineDown, p.PDF6937]. CRadioGroup: Handler virtual bool para ScrollLineDown: navegação uma linha abaixo; true significa evento tratado. Proposta: atualizar apresentação dependente de navegação uma linha abaixo, sem executar regra financeira por efeito visual.

- **REF-4063 — OnScrollLineUp** [REF, OnScrollLineUp, p.PDF6938]. CRadioGroup: Handler virtual bool para ScrollLineUp: navegação uma linha acima; true significa evento tratado. Proposta: atualizar apresentação dependente de navegação uma linha acima, sem executar regra financeira por efeito visual.

- **REF-4064 — OnChangeItem** [REF, OnChangeItem, p.PDF6939]. CRadioGroup: Handler virtual bool recebe índice int do item alterado. Proposta: atualizar seleção/máscara de modo determinístico.

- **REF-4065 — Redraw** [REF, Redraw, p.PDF6940]. CRadioGroup: Redesenha controle/grupo e retorna bool. Proposta: atualizar apresentação após mudança de dados e registrar falha, sem confundir com ChartRedraw.

- **REF-4066 — RowState** [REF, RowState, p.PDF6941]. CRadioGroup: Setter bool de estado de linha/item recebe index int e select bool. Proposta: distinguir marcação visual da entidade selecionada no domínio.

- **REF-4067 — Select** [REF, Select, p.PDF6942]. CRadioGroup: Seleciona item por índice. Proposta: validar faixa do índice antes de converter seleção em entidade do monitor. Aqui a assinatura é void, não bool.

- **REF-4068 — CSpinEdit** [REF, CSpinEdit, p.PDF6943–6958]. Editor de inteiro com limites e passo descrito; exemplo MinValue10, MaxValue100, Value50. Proposta: configurar quantidade de linhas/intervalo inteiro; limite visual não substitui regra normativa nem validação do núcleo.

- **REF-4069 — Create** [REF, Create, p.PDF6948]. CSpinEdit: Cria controle em chart/subwin com nome único e retângulo x1,y1,x2,y2; bool indica sucesso. Proposta: abortar montagem incompleta e registrar nome/geometria da falha.

- **REF-4070 — OnEvent** [REF, OnEvent, p.PDF6949]. CSpinEdit: Handler virtual bool recebe id e referências const long/double/string dos parâmetros do evento. Proposta: preservar tipos e encaminhar eventos ao controle correto; true significa evento tratado.

- **REF-4071 — MinValue** [REF, MinValue, p.PDF6950]. CSpinEdit: Getter int e setter void do mínimo de SpinEdit. Proposta: rejeitar configuração de intervalo inválida no domínio.

- **REF-4072 — MaxValue** [REF, MaxValue, p.PDF6951]. CSpinEdit: Getter int e setter void do máximo de SpinEdit. Proposta: limitar valor inteiro apresentado sem substituir validação normativa.

- **REF-4073 — Value** [REF, Value, p.PDF6952]. CSpinEdit: Consulta valor associado ao controle/seleção. Proposta: interpretar conforme o tipo do controle, sem confundir estado booleano, máscara e identificador. Getter int e setter void do inteiro corrente.

- **REF-4074 — CreateEdit** [REF, CreateEdit, p.PDF6953]. CSpinEdit: Cria dependência de edição; virtual bool. Proposta: validar montagem de campo antes de aceitar entrada.

- **REF-4075 — CreateInc** [REF, CreateInc, p.PDF6954]. CSpinEdit: Cria botão de incremento; virtual bool sinaliza sucesso. Proposta: validar montagem da navegação incremental.

- **REF-4076 — CreateDec** [REF, CreateDec, p.PDF6955]. CSpinEdit: Cria botão de decremento; virtual bool sinaliza sucesso. Proposta: validar montagem da navegação reversa.

- **REF-4077 — OnClickInc** [REF, OnClickInc, p.PDF6956]. CSpinEdit: Handler virtual bool de clique no incremento. Proposta: atualizar navegação/valor candidato e validar limites.

- **REF-4078 — OnClickDec** [REF, OnClickDec, p.PDF6957]. CSpinEdit: Handler virtual bool de clique no decremento. Proposta: impedir redução fora do intervalo do conteúdo.

- **REF-4079 — OnChangeValue** [REF, OnChangeValue, p.PDF6958]. CSpinEdit: Handler virtual bool da mudança do valor corrente. Proposta: validar inteiro candidato antes de propagá-lo ao monitor.

- **REF-4080 — CDialog** [REF, CDialog, p.PDF6959–6981]. Contêiner composto combina controles com funções diferentes e os adiciona à área cliente. Fornece caption, bordas, close e drag. Proposta: arquitetura de painel monitor; fechar janela não deve ser confundido com liquidar posição.

- **REF-4081 — Create** [REF, Create, p.PDF6961]. CDialog: Cria controle em chart/subwin com nome único e retângulo x1,y1,x2,y2; bool indica sucesso. Proposta: abortar montagem incompleta e registrar nome/geometria da falha.

- **REF-4082 — OnEvent** [REF, OnEvent, p.PDF6962]. CDialog: Handler virtual bool recebe id e referências const long/double/string dos parâmetros do evento. Proposta: preservar tipos e encaminhar eventos ao controle correto; true significa evento tratado.

- **REF-4083 — Caption** [REF, Caption, p.PDF6963]. CDialog: Getter/setter do título do diálogo; setter bool recebe string. Getter impresso como MinValue é incongruente: verificar Dialog.mqh. Proposta: título identifica programa/estado de exibição.

- **REF-4084 — Add** [REF, Add, p.PDF6964]. CDialog: Adiciona CWnd à área cliente por ponteiro ou referência, retornando bool. Proposta: conferir registro de cada controle e preservar ciclo de vida dos objetos.

- **REF-4085 — CreateWhiteBorder** [REF, CreateWhiteBorder, p.PDF6965]. CDialog: Cria dependência borda branca, virtual bool. Proposta: montagem visual completa exige retorno conferido.

- **REF-4086 — CreateBackground** [REF, CreateBackground, p.PDF6966]. CDialog: Cria dependência de fundo, virtual bool. Proposta: validar fundo da janela antes de apresentar controles.

- **REF-4087 — CreateCaption** [REF, CreateCaption, p.PDF6967]. CDialog: Cria dependência de título, virtual bool. Proposta: manter identificação do painel disponível.

- **REF-4088 — CreateButtonClose** [REF, CreateButtonClose, p.PDF6968]. CDialog: Cria botão de fechar, virtual bool. Proposta: definir fechamento do painel separadamente de estado de posições.

- **REF-4089 — CreateClientArea** [REF, CreateClientArea, p.PDF6969]. CDialog: Cria área cliente, virtual bool. Proposta: controles filhos dependem de sucesso desta etapa.

- **REF-4090 — OnClickCaption** [REF, OnClickCaption, p.PDF6970]. CDialog: Handler virtual bool de clique no título. Proposta: interação da janela sem transição automática no estado de negócio.

- **REF-4091 — OnClickButtonClose** [REF, OnClickButtonClose, p.PDF6971]. CDialog: Handler de clique no fechamento. Proposta: liberar recursos do painel com política explícita de ciclo de vida, sem ação de negociação implícita.

- **REF-4092 — ClientAreaVisible** [REF, ClientAreaVisible, p.PDF6972]. CDialog: Setter bool de visibilidade da área cliente. Proposta: ocultação é estado visual, não pausa comprovada do monitor.

- **REF-4093 — ClientAreaLeft** [REF, ClientAreaLeft, p.PDF6973]. CDialog: Retorna int X do canto superior esquerdo cliente. Proposta: posicionar filhos no referencial correto.

- **REF-4094 — ClientAreaTop** [REF, ClientAreaTop, p.PDF6974]. CDialog: Retorna int Y do canto superior esquerdo cliente. Proposta: distinguir deslocamento do título e área útil.

- **REF-4095 — ClientAreaRight** [REF, ClientAreaRight, p.PDF6975]. CDialog: Retorna X inferior direito; declaração impressa ClientAreaTop conflita com título. Proposta: verificar include antes de cálculo de largura.

- **REF-4096 — ClientAreaBottom** [REF, ClientAreaBottom, p.PDF6976]. CDialog: Retorna int Y inferior direito da área cliente. Proposta: limitar layout vertical dos filhos.

- **REF-4097 — ClientAreaWidth** [REF, ClientAreaWidth, p.PDF6977]. CDialog: Retorna int largura da área cliente. Proposta: dimensionar campos sem usar largura externa da janela.

- **REF-4098 — ClientAreaHeight** [REF, ClientAreaHeight, p.PDF6978]. CDialog: Retorna int altura da área cliente. Proposta: calcular linhas disponíveis na área útil.

- **REF-4099 — OnDialogDragStart** [REF, OnDialogDragStart, p.PDF6979]. CDialog: Handler virtual bool no início do arraste do diálogo. Proposta: registrar geometria inicial para movimentação da janela.

- **REF-4100 — OnDialogDragProcess** [REF, OnDialogDragProcess, p.PDF6980]. CDialog: Handler virtual bool durante arraste do diálogo. Proposta: atualizar coordenadas da apresentação e manter negócio independente.

- **REF-4101 — OnDialogDragEnd** [REF, OnDialogDragEnd, p.PDF6981]. CDialog: Handler virtual bool ao fim do arraste. Proposta: persistir geometria final somente se desejado.

- **REF-4102 — CAppDialog** [REF, CAppDialog, p.PDF6982–7007]. Diálogo de aplicação para EA/indicador: Create, Run, ChartEvent, Destroy(reason), minimizar e persistir estado. Proposta: ciclo de vida explícito para painel event-driven, sem exigir OnTick; persistência de janela não prova validade de configurações de risco.

- **REF-4103 — Create** [REF, Create, p.PDF6985]. CAppDialog: Cria controle em chart/subwin com nome único e retângulo x1,y1,x2,y2; bool indica sucesso. Proposta: abortar montagem incompleta e registrar nome/geometria da falha.

- **REF-4104 — Destroy** [REF, Destroy, p.PDF6986]. CAppDialog: Desinicialização virtual void recebe reason, padrão REASON_PROGRAM. Proposta: encaminhar motivo real de OnDeinit e liberar recursos do painel.

- **REF-4105 — OnEvent** [REF, OnEvent, p.PDF6987]. CAppDialog: Handler virtual bool recebe id e referências const long/double/string dos parâmetros do evento. Proposta: preservar tipos e encaminhar eventos ao controle correto; true significa evento tratado.

- **REF-4106 — Run** [REF, Run, p.PDF6988]. CAppDialog: Executa controle e retorna bool. Proposta: conferir inicialização de aplicação antes de declarar painel pronto.

- **REF-4107 — ChartEvent** [REF, ChartEvent, p.PDF6989]. CAppDialog: Handler virtual bool recebe id e parâmetros long/double/string por referência. Proposta: conectar OnChartEvent do programa ao diálogo para interação funcional.

- **REF-4108 — Minimized** [REF, Minimized, p.PDF6990]. CAppDialog: Setter bool de flag da janela minimizada. Proposta: estado de apresentação não é pausa da coleta.

- **REF-4109 — IniFileSave** [REF, IniFileSave, p.PDF6991]. CAppDialog: Persiste estado do controle em arquivo. Assinatura void e retorno textual bool são conflitantes; conferir include. Proposta: persistir geometria sem promover configuração de risco automaticamente.

- **REF-4110 — IniFileLoad** [REF, IniFileLoad, p.PDF6992]. CAppDialog: Carrega estado do controle do arquivo; assinatura void contradiz retorno textual bool. Proposta: validar conteúdo restaurado e usar defaults seguros de interface.

- **REF-4111 — IniFileName** [REF, IniFileName, p.PDF6993]. CAppDialog: Virtual string const fornece nome do arquivo incluindo nome do EA/indicador e símbolo. Proposta: avaliar colisões entre instâncias; descrição diz setter mas assinatura é getter.

- **REF-4112 — IniFileExt** [REF, IniFileExt, p.PDF6994]. CAppDialog: Virtual string const fornece extensão do arquivo de estado; descrição fala setter. Proposta: conferir extensão ao definir política de persistência.

- **REF-4113 — CreateCommon** [REF, CreateCommon, p.PDF6995]. CAppDialog: Inicialização comum bool recebe chart/name/subwin. Proposta: centralizar identidade e destino da janela.

- **REF-4114 — CreateExpert** [REF, CreateExpert, p.PDF6996]. CAppDialog: Inicialização bool específica de EA recebe retângulo. Proposta: integrar painel ao monitor event-driven sem inventar negociação.

- **REF-4115 — CreateIndicator** [REF, CreateIndicator, p.PDF6997]. CAppDialog: Inicialização bool específica de indicador recebe retângulo. Proposta: respeitar tipo de programa e janela de destino.

- **REF-4116 — CreateButtonMinMax** [REF, CreateButtonMinMax, p.PDF6998]. CAppDialog: Cria botões minimizar/maximizar, virtual void. Proposta: verificar disponibilidade pelo ciclo de montagem, sem esperar bool inexistente.

- **REF-4117 — OnClickButtonClose** [REF, OnClickButtonClose, p.PDF6999]. CAppDialog: Handler de clique no fechamento. Proposta: liberar recursos do painel com política explícita de ciclo de vida, sem ação de negociação implícita. Nesta classe a assinatura é virtual void, diferente do handler bool do CDialog.

- **REF-4118 — OnClickButtonMinMax** [REF, OnClickButtonMinMax, p.PDF7000]. CAppDialog: Handler de minimizar/maximizar, virtual void; declaração impressa repete OnClickButtonClose. Proposta: conferir método real no include.

- **REF-4119 — OnAnotherApplicationClose** [REF, OnAnotherApplicationClose, p.PDF7001]. CAppDialog: Handler externo virtual void. Proposta: tratar encerramento de outra aplicação como evento de coordenação da UI, sem assumir regra de risco.

- **REF-4120 — Rebound** [REF, Rebound, p.PDF7002]. CAppDialog: Redefine geometria usando CRect. CWndClient imprime ReBound void; CAppDialog Rebound bool. Proposta: conferir grafia e retorno específicos antes de sobrescrever.

- **REF-4121 — Minimize** [REF, Minimize, p.PDF7003]. CAppDialog: Virtual void exibe janela minimizada; retorno textual bool é incongruente. Proposta: continuar monitoramento segundo política própria, independente da janela.

- **REF-4122 — Maximize** [REF, Maximize, p.PDF7004]. CAppDialog: Virtual void restaura janela; retorno textual bool é incongruente. Proposta: redesenhar estado atual sem reexecutar inicialização de negócio.

- **REF-4123 — CreateInstanceId** [REF, CreateInstanceId, p.PDF7005]. CAppDialog: Retorna string de prefixo único para nomes dos objetos. Proposta: evitar colisões entre painéis e limitar limpeza ao prefixo próprio.

- **REF-4124 — ProgramName** [REF, ProgramName, p.PDF7006]. CAppDialog: Retorna string do programa MQL5 que usa o controle. Proposta: identificar aplicação nos diagnósticos e persistência.

- **REF-4125 — SubwinOff** [REF, SubwinOff, p.PDF7007]. CAppDialog: Descrição indica deslocamento Y da subjanela, mas assinatura void e retorno nenhum. Proposta: conferir Dialog.mqh; não usar como getter numérico sem validação.

- **REF-4126 — Moving from MQL4** [REF, Moving from MQL4, p.PDF7008–7010]. Migração MQL4→MQL5: start torna-se OnStart somente em scripts, OnTick em EA e OnCalculate em indicador; EA pode funcionar sem OnTick usando eventos. Ask/Bid/Bars e séries predefinidas não migram literalmente; _Point/_Digits e acesso explícito às séries exigem revisão. Locais não inicializadas (salvo strings), limites de array críticos, curto-circuito e precedência C++ alteram comportamento. Buffers têm direção comum por padrão e consomem memória apesar de limite ampliado. Proposta Stoikus: preservar desenho event-driven e auditar indexação/inicialização ao portar exemplos.

- **REF-4127 — List of MQL5 Functions** [REF, List of MQL5 Functions, p.PDF7011–7044]. Índice alfabético de funções, páginas7011–7044 integralmente lidas: AccountInfo/arrays, calendário, charts, OpenCL, Copy*, símbolos customizados, SQLite, DirectX, eventos/arquivos, globais/histórico, indicadores, matemática, objetos/handlers, ordens/posições, recursos/sinais, rede/strings/símbolos, terminal/tempo. Serve como mapa de procura, não contrato detalhado. Proposta: consultar API substantiva antes de implementar; separar OrderCalc* e leitura de histórico de OrderSend; Python aparece com nomes MT5Initialize/MT5Copy* e exige verificar API atual do pacote. Nenhuma integração Python/DirectX/OpenCL proposta como já existente.

- **REF-4128 — List of MQL5 Constants** [REF, List of MQL5 Constants, p.PDF7045–7138]. Somente páginas7045–7138 deste índice de constantes foram lidas;7139–7284 fora de escopo. Recorte vai de macros de compilação até IDABORT, abrangendo ACCOUNT, alinhamento/âncoras, BOOK, bordas, CHART/CHARTEVENT, cores, codepages/criptografia, limites DBL/FLT, DEAL, DRAW, Elliott, erros ERR e FILE. Proposta: navegação para contratos originais; índice de constantes não estabelece regra JPW. Descrições quebradas por colunas preservadas na leitura, com limites explícitos nas notas de síntese.
