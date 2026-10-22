# Stoikus — painel personalizável e uso por dois gráficos

**Produto C5 / fontes 1.23.0; distribuição documental D1; cálculo 1.9.0.** O manifesto vincula **JPW_Stoikus_Uso_Fontes_v1.23.0_painel-C5.zip** e **JPW_Stoikus_Fontes_v1.23.0_painel-C5.zip** aos mesmos fontes C5. O kit de compilação **Kit_Windows_Stoikus_Painel_C5_D1.zip** e o pin separado **root-pin-Painel-C5-D1.json** têm identidade documental própria; o instalador permanece indisponível. Os pacotes R5 anteriores são históricos e não validam estes bytes. Para a conferência isolada do kit D1, copie o pin baixado para a pasta extraída com o nome interno **root-pin-R5.json**, preservando o original e seus hashes; os nomes internos R5 são compatibilidade do protocolo do kit, não identidade do pacote histórico. Siga o LEIA-PRIMEIRO.md interno antes de qualquer compilação. Nenhuma destas instruções autoriza instalação ou execução.

Compilação e interação MT5, templates, instalação e aceite humano dos mesmos bytes permanecem **NOT_RUN**. A primeira compilação e o primeiro ensaio exigem um conjunto isolado, identificado por seus próprios fontes, logs e recibos. A prévia no navegador usa dados fictícios e não substitui essa conferência.

As instruções genéricas de cópia, F7 e abertura abaixo explicam os papéis dos componentes. Elas não autorizam atualizar a instalação de uso nem promovem um pacote histórico a esta revisão.

**Instalação isolada de demonstração** é outra instalação MT5, com **pasta de dados separada** e conta demo, preparada para o primeiro ensaio sem negociação. Confira o caminho em Arquivo → Abrir pasta de dados. Trocar para uma **conta demo na mesma instalação** não separa arquivos, gráficos e configurações da sessão de uso.

| Papel | Programa no Navegador | Onde usar | O que permanece aberto |
| --- | --- | --- | --- |
| Monitor da conta | Experts → JPWealth → `JPW_Stoikus_Monitor` | Um gráfico de apoio reservado | O EA permanece anexado; mantenha esse gráfico aberto. |
| Conta e Cockpit | Indicadores → JPWealth → `JPW_Alavancagem_Atual` | O gráfico de trabalho | Indicador que fornece o painel Stoikus e o acesso **Conta**. |
| Canais e estudos | Indicadores → JPWealth → `JPW_NoCuda_Channels` | O mesmo gráfico de trabalho | Acesso **NoCuda** no painel conjunto; sozinho mantém acesso próprio. |
| Abrir Conta + NoCuda | Scripts → JPWealth → `JPW_Stoikus_Abrir_Paineis` | Execute uma vez no gráfico de trabalho | O script termina; os dois indicadores continuam anexados. |

O Monitor observa a conta inteira, mesmo em um gráfico de símbolo diferente do seu trabalho. Não envia ordens nem arma o Supervisor. O abridor não inicia o Monitor: o MT5 aceita apenas um EA por gráfico, portanto use o gráfico de apoio reservado para evitar substituir outro robô.

## Instalar e abrir

1. Extraia o ZIP e leia este guia, apresentado no pacote como **LEIA_PRIMEIRO.md**. No MT5 de teste, escolha **Arquivo → Abrir pasta de dados**. No Parallels, faça isso dentro do MT5 do Windows.
2. Preserve uma cópia dos arquivos JPWealth existentes e identifique sua versão. Copie o conteúdo das cinco subpastas do pacote **MQL5** para as mesmas subpastas da pasta de dados: **Indicators**, **Experts**, **Scripts**, **Include** e **Images**. Crie **JPWealth** se necessário. Não substitua a pasta MQL5 inteira nem os arquivos de outros programas. O guia fica na pasta extraída.
3. Pressione **F4** para abrir o MetaEditor dessa instalação. Abra e compile com **F7**, separadamente: `JPW_Stoikus_Monitor.mq5`, `JPW_Alavancagem_Atual.mq5`, `JPW_NoCuda_Channels.mq5` e `JPW_Stoikus_Abrir_Paineis.mq5`. Exija **0 errors**, confira os avisos e o `.ex5` ao lado de cada fonte. Includes `.mqh` e imagens não são compilados separadamente. Compilar não executa o programa.
4. No terminal, abra o **Navegador (Ctrl+N)** e escolha **Atualizar / Refresh**. Abra um gráfico de apoio vazio, reservado para o Monitor. Arraste `JPW_Stoikus_Monitor` de **Experts → JPWealth** para ele. Nas **Entradas**, comece com `false`, `false` e evidência vazia; esses padrões permitem iniciar com cobertura desconhecida. Deixe **Permitir negociação algorítmica** desmarcado. Confirme **OK** e mantenha o gráfico aberto.
5. Selecione o gráfico de trabalho que quer usar. Em **Scripts → JPWealth**, arraste `JPW_Stoikus_Abrir_Paineis` para esse gráfico. Não há parâmetros obrigatórios. O abridor verifica o que já está anexado e acrescenta somente o que falta, sem aplicar template, substituir EA ou alterar as configurações dos indicadores presentes.
6. Confirme os dois indicadores com **Ctrl+I**: a lista mostra os nomes curtos **Stoikus · Cockpit 1.23.0** e **Stoikus · NoCuda Channels**, não os nomes dos arquivos. Com os dois presentes, use **Conta** e **NoCuda** no painel Stoikus para abrir suas consultas; **Personalizar** ajusta as informações do painel. Para alterar parâmetros, selecione o indicador em Ctrl+I e abra **Propriedades → Entradas**. Para o Monitor, use **F7 no gráfico de apoio** (propriedades do EA no MT5; F7 no MetaEditor compila).

Você também pode anexar manualmente os dois indicadores, um após o outro, por **Indicadores → JPWealth**. Eles coexistem no mesmo gráfico. O abridor não exibe uma janela permanente: ele é um atalho para anexá-los, não o próprio painel. Quando adiciona um indicador ausente, usa seus padrões; altere depois as Entradas daquele indicador. Estudos e parâmetros de um indicador já presente são preservados.

## Quando o estado ainda não está pronto

- **Aguardando identidade:** confirme a conta e a conexão do terminal de demonstração. Ainda não há leitura atual certificada.
- **Aguardando acesso ao produtor:** confira Experts, retire Observer/Accountant ou outro Monitor dos gráficos dessa instalação e confira acesso à pasta de dados. Não apague locks ou bancos para forçar a partida.
- **Monitor ativo:** o componente está anexado; a cobertura e as amostras do painel ainda precisam ser conferidas. Esse estado não homologa cálculos.
- **Preparando Histórico Pessoal:** aguarde a auditoria em etapas. Um histórico longo pode precisar de vários ciclos; não é preciso limpar o banco. Trocar conta, filtro ou item cancela a consulta antiga e inicia a correta.
- **Degradação ou recuperação:** confira o motivo em Experts e a condição indicada pelo painel. Uma mensagem antiga de início não prova que o produtor continua saudável.

A revisão 1.23.0 reorganiza as janelas e acrescenta controles visuais, preservando a assinatura Stoikus by JP Wealth; as correções herdadas de 1.22.2 preservam bancos, preferências e estudos. O JSON tem limite de tamanho próprio; uma exportação recusada conserva o banco. Para volume maior, use CSV e confira o resultado completo. Compilação e ensaio em Windows ARM/Parallels têm recibos separados dos ensaios em um PC Windows x64.

## Personalizar as informações do painel

Com Conta e NoCuda no mesmo gráfico, o painel Stoikus reúne **Conta**, **NoCuda** e **Personalizar**. NoCuda sozinho conserva acesso próprio. Se o acesso indicar componente ausente, confira **Ctrl+I**. Para acrescentar o componente, abra **Navegador (Ctrl+N) → Indicadores → JPWealth** e arraste `JPW_Alavancagem_Atual` para Conta ou `JPW_NoCuda_Channels` para NoCuda ao gráfico de trabalho. Esse procedimento acrescenta um indicador; não inicia o Monitor da conta.

Em **Personalizar**, escolha entre sete leituras: alavancagem da conta, resultado flutuante, SL da referência, Raiz N de uma semana, Raiz N de duas semanas, risco dos stops e flutuante compensado. Marque as que quer ver e use **Subir/Descer** para ordenar. Ocultar uma métrica não interrompe seu cálculo ou acompanhamento. Quando faltar altura, use as páginas; amplie o gráfico se os controles não couberem.

Uma configuração nova sugere **alavancagem → risco dos stops → Raiz N 1W → Raiz N 2W**. Sem a preferência nova, uma configuração antiga conserva a seleção que antes aparecia. **Padrão** repõe a sugestão e a ordem, respeitando métricas ocultadas na preferência antiga compatível.

- **Prévia:** marcar, ordenar e mudar a transparência altera apenas o rascunho exibido.
- **Aplicar:** confirma seleção, ordem e transparência neste gráfico. Uma falha mantém o editor aberto com orientação; confira o aviso antes de tentar novamente.
- **Cancelar:** descarta o rascunho sem gravar essas escolhas. **Esc** faz o mesmo.
- **Teclado do editor:** **Tab/Shift+Tab** percorrem controles; **Enter/Espaço** acionam o controle indicado em Foco. Fora do editor, os atalhos anteriores continuam disponíveis.

A transparência do fundo vai de **0% (opaco) a 100% (sem fundo)**, em passos de 10%; o padrão é 30%. A prévia só é confirmada em **Aplicar**. Textos e controles permanecem opacos; as janelas Conta, NoCuda e Personalizar mantêm fundo sólido. Você pode ocultar todas as métricas: **Conta**, **NoCuda** e **Personalizar** continuam acessíveis.

As preferências são deste gráfico. Para levá-las a um template, salve-o manualmente no MT5 e confira a restauração em ensaio nativo. Carregar ou pintar o painel não grava preferências. Se um template mudar durante a edição, **Aplicar fica bloqueado**: o editor conserva o rascunho e oferece **Cancelar**. Cancele e reabra **Personalizar** para conferir a configuração atual. Abrir Conta ou NoCuda pode suspender a personalização sem aplicar seu rascunho; reabrir permite retomá-lo ou cancelá-lo.

## Recolher o painel e consultar os dados

- **− no painel Stoikus:** recolhe o painel; o acesso **Stoikus** o restaura, mantendo seleção e ordem. Isso é independente das janelas de consulta.
- **Conta ou NoCuda:** abre sua consulta. Minimizar ou recolher a janela preserva desenhos e rascunhos da sessão; não confirma formulários nem estudos.
- **Mover e ajustar largura:** arraste a faixa do cabeçalho ou a alça horizontal. A altura acompanha o conteúdo e usa paginação quando necessário.
- **N/A ou aviso de disponibilidade:** clique na métrica para ler valor completo, unidade, escopo e motivo. O aviso de disponibilidade abre **Conta → Sistema** para conferir componentes e captura. N/A não significa zero nem permissão para operar.

Conta conserva o tamanho inicial de 720 × 520 e NoCuda de 680 × 500 pixels lógicos, limitados ao gráfico; preferências válidas anteriores são respeitadas. As linhas mantêm valor, unidade, estado e escopo separados. Compilação, cliques e restauração por template desta revisão ainda exigem evidência nativa; o kit R5 anterior não valida estes novos fontes.

## Primeira configuração: o que conferir

Comece pelos padrões. No NoCuda, escolha um **período-fonte definido**, normalmente **H1**, e mantenha a malha conforme sua preferência. Em Conta, ajuste fonte e canto se o resumo não estiver legível. Pips são opcionais: deixe símbolo vazio e tamanho zero até conhecer a convenção do instrumento. As declarações de cobertura do Monitor só devem mudar quando você tiver evidência verificável.

Procure primeiro o **rótulo da Entrada no MT5**, reproduzido abaixo. O nome técnico `Inp*` é uma referência secundária de compatibilidade. As tabelas seguem a ordem de cada componente; os parâmetros avançados podem permanecer nos padrões. Esses valores iniciam componentes novos. Preferências e estudos já salvos são preservados; confira no painel o período e a malha restaurados. Alterar uma Entrada não confirma automaticamente um estudo.

### NoCuda: selecionar, conferir e acompanhar

Uma configuração nova abre em **Compacta**, com fonte 11 e tamanho nominal de 680 × 500, ajustado à escala da tela e limitado a 85% da largura e da altura do gráfico. Em **Aparência**, você pode escolher **Ampla**, **Maximizada**, fonte, canto do botão e malha. Preferências anteriores continuam sendo restauradas. **Aplicar** guarda a escolha; **Cancelar** desfaz a prévia visual. Reabrir ou atualizar a tela não salva preferências por conta própria.

Na seção **Canal**, siga três etapas:

1. **Selecionar canal:** escolha explicitamente o canal Fibonacci na lista e confira o período de referência. O canal compatível é o Fibonacci Channel do MT5 (`OBJ_FIBOCHANNEL`), com três âncoras e os 65 níveis esperados pelo NoCuda. O nome do objeto não determina seu período.
2. **Conferir prévia:** confira as três âncoras, o período e o canal original. A prévia mantém os preços das âncoras; não os ajusta ao fechamento do candle. **Cancelar prévia** conserva o estudo anterior.
3. **Confirmar vínculo:** confirma a fotografia conferida e inicia o acompanhamento. A fonte é lida novamente antes da gravação. Se tiver mudado desde a prévia, será necessário conferir outra prévia.

**Vínculo conferido** significa que as propriedades da fonte foram conferidas. As medidas continuam dependentes da validação nativa: **UNVERIFIED_NATIVE** mantém valores dependentes em **N/A** e bloqueia consulta, marcas e registro de projeção, também pelo teclado. O estado de uma fonte inválida, de uma gravação pendente ou de uma sincronização pausada tem orientação própria; confira sempre o motivo apresentado.

A faixa fixa mostra **estado, motivo e próxima ação** em todas as seções. Use **Detalhes** para ler e selecionar o motivo completo quando ele não couber na faixa. Na janela estreita, use as setas ao lado de **Seção** ou clique no nome para avançar. O conteúdo passa a uma coluna, com as setas de rolagem no rodapé. A fonte escolhida é mantida; se a área não comportar os controles, amplie o gráfico. A indicação de área insuficiente não significa que os dados estejam disponíveis.

**Pausar sincronização** interrompe o acompanhamento; **Retomar** confere a origem antes de acompanhar novamente. Se houver conflito no histórico, Retomar aparece indisponível: use **Conferir fonte** e justifique a revisão. Depois da conferência aceita, o aviso é retirado; a pausa e a revisão do histórico são estados distintos. **Desvincular** preserva os registros e solicita a restauração da visibilidade original. **Ocultar canal original** e **Mostrar canal original** são escolhas explícitas: confira eventual aviso de restauração pendente. **Recolher**, no cabeçalho ou rodapé, volta ao acesso **NoCuda** e preserva o rascunho da sessão; com Conta presente, esse acesso fica no painel Stoikus.

Em **Agora**, selecionar um nível escolhe a linha do estudo; não valida a medida nem cria uma ordem. A **malha completa** mostra todos os níveis da cópia visual; a **malha essencial** mantém 0, 0,5 e 1 nessa cópia. Essa escolha não altera o canal original nem os níveis gravados no estudo. Botões com **Indisponível** explicam o requisito ao passar o ponteiro; use o motivo e a próxima ação antes de insistir na operação.

### Conta — 12 Entradas

| Rótulo da Entrada no MT5 | Nome técnico | Padrão | Unidade / escolha | Significado e zero/vazio |
| --- | --- | --- | --- | --- |
| Cadência solicitada (s; 1–3600; ciclo até 30 s; Stops até 5 s) | `InpUpdateSeconds` | `1` | Segundos, 1–3600 | Cadência solicitada. O ciclo completo tem limite de 30 s e Stops é revalidado em até 5 s; o timer não garante intervalos exatos. Zero é inválido. |
| Idade máxima da cotação (s; 1 a 30) | `InpMaxQuoteAgeSeconds` | `30` | Segundos, 1–30 | Idade máxima da cotação para qualificá-la como recente. Zero é inválido; não transforma histórico em Current. |
| Canto do painel | `InpCorner` | `CORNER_LEFT_UPPER` | Canto do gráfico | Referência inicial do resumo: superior esquerdo. Escolha outro canto se houver sobreposição. |
| Distância horizontal do canto (px; zero ou mais) | `InpOffsetX` | `16` | Pixels, ≥0 | Distância horizontal a partir do canto. Zero encosta na borda; não desativa o painel. |
| Distância vertical do canto (px; zero ou mais) | `InpOffsetY` | `40` | Pixels, ≥0 | Distância vertical a partir do canto. Zero encosta na borda. |
| Fonte compacta no gráfico (pt; 8 a 40) | `InpFontSize` | `10` | Tamanho de fonte, 8–40 | Fonte do resumo compacto; zero é inválido. |
| Fonte do painel Conta (pt; 9 a 24) | `InpCockpitFontSize` | `11` | Tamanho de fonte, 9–24 | Fonte da janela Cockpit, independente do resumo; zero é inválido. |
| Cor do texto | `InpFontColor` | `C'118,118,118'` | Cor RGB, `#767676` | Cor do texto compacto. Ajuste para seu fundo; preto não significa desativado. |
| Ticket Genesis (0: referência única; >0: ticket aberto) | `InpGenesisTicket` | `0` | Ticket de posição aberta, ≥0 | Zero tenta inferir somente uma referência inequívoca. Ticket positivo seleciona explicitamente uma posição; não é permissão para operar. |
| Símbolo exato para pip (vazio: sem convenção manual) | `InpPipSymbol` | Vazio `""` | Símbolo exato do MT5 | Opcional, usado junto do tamanho de pip. Vazio não declara convenção; pontos e percentuais continuam disponíveis. |
| Tamanho de 1 pip em preço (0: sem convenção manual) | `InpPipSize` | `0.0` | Distância no preço, ≥0 | Zero não declara pip. Informe valor positivo apenas com o símbolo exato; casas decimais não comprovam a convenção. |
| Registro técnico (desativado por padrão) | `InpTechnicalLog` | `false` | Sim / não | Log técnico detalhado sob demanda. `false` conserva o padrão sem esse detalhamento; mensagens essenciais continuam possíveis. |

### NoCuda — 5 Entradas

| Rótulo da Entrada no MT5 | Nome técnico | Padrão | Unidade / escolha | Significado e zero/vazio |
| --- | --- | --- | --- | --- |
| Período fonte das âncoras (Atual não aceito) | `InpSourceTimeframe` | `PERIOD_H1` | Período MT5 definido | Período-fonte dos canais; H1 significa uma hora. **PERIOD_CURRENT é inválido**: escolha H1 ou outro período definido, independente do período de visualização do gráfico. |
| Malha completa ao iniciar (sim: todos os níveis) | `InpFullMesh` | `true` | Sim / não | `true` mostra a malha completa; `false` escolhe a apresentação reduzida. Não confirma nem salva um estudo. |
| Símbolo exato para pip (vazio: sem conversão) | `InpPipSymbol` | Vazio `""` | Símbolo exato do MT5 | Vazio deixa pips sem convenção declarada. Se preenchido, exige tamanho positivo e válido. |
| Tamanho de 1 pip em preço (0: só com símbolo vazio) | `InpPipSize` | `0.0` | Distância no preço | Com símbolo vazio, não há conversão declarada. Com símbolo preenchido, zero ou negativo é inválido. Não assumir pip pelas casas decimais. |
| Idade máxima da cotação (s; 1 a 3600) | `InpMaxQuoteAgeSeconds` | `30` | Segundos, 1–3600 | Limite de idade da cotação para a leitura pertinente. Zero é inválido; aumentar não homologa um estudo. |

### Monitor — 3 Entradas de cobertura

| Rótulo da Entrada no MT5 | Nome técnico | Padrão | Unidade / escolha | Significado e zero/vazio |
| --- | --- | --- | --- | --- |
| Histórico completo confirmado (não: pendente) | `InpHistoryCoverageConfirmed` | `false` | Declaração sim / não | `false` significa histórico completo não confirmado; permite iniciar e mantém a lacuna explícita. Só use `true` após conferir a cobertura do período relevante. |
| Custos completos confirmados (não: pendente) | `InpCostCoverageConfirmed` | `false` | Declaração sim / não | `false` significa custos completos não confirmados. Não bloqueia a partida; não inventa custos ausentes como zero. |
| Evidência da cobertura (vazio: não informado) | `InpCoverageEvidence` | Vazio `""` | Texto de referência | Vazio não fornece evidência. Ao declarar cobertura confirmada, registre uma referência verificável; uma frase arbitrária não comprova completude. |

Não marque as duas declarações como `true` apenas para tentar obter um painel verde. Elas não são botões de ativação. Presença do Monitor, qualidade de uma amostra e completude histórica são fatos distintos. Leia o motivo em **Cockpit → Sistema**.

## Se algo não aparecer

- **O abridor foi “loaded” e depois “removed”:** é normal que um script termine. Abra **Caixa de ferramentas (Ctrl+T) → Experts** para ler o resultado, inclusive sucesso parcial ou falha. No **Journal / Diário**, carregamento e remoção não são prova de sucesso. Scripts `Tests` e o laboratório também terminam; não são os painéis de uso.
- **Só apareceu Conta ou só NoCuda:** confira Ctrl+I e a mensagem em Experts. Verifique o `.ex5` ausente, includes/imagens da mesma versão e a pasta da instalação correta. Repita o abridor após resolver: o indicador que já estava presente é mantido. Falha parcial não remove o que abriu.
- **Não aparece no Navegador:** confirme a pasta de dados do terminal aberto, os quatro `.ex5` compilados e Atualizar / Refresh. Fontes `.mq5` sem compilação não são programas executáveis.
- **Stop risk mostra “N/A · Check Observer”:** confira o Monitor compatível, no gráfico de apoio ainda aberto da mesma instalação, e Experts. Em Conta → Sistema, leia o motivo por módulo. Ter NoCuda ou Conta anexados não inicia o Monitor. Mesmo com Monitor presente, amostra antiga, incompleta ou falha permanece indisponível.
- **Erro nas Entradas:** siga o intervalo informado em Experts. Para NoCuda, substitua PERIOD_CURRENT por H1 ou outro período definido; para pips, preencha o par símbolo exato + tamanho positivo ou mantenha a convenção vazia.
- **Botões repetidos ou indicador legado:** uma captura não identifica a origem de cada botão. Confira Ctrl+I e inventarie versões, instâncias, nomes de objetos e arquivos no terminal; preserve configurações e registros antes de qualquer limpeza dirigida. Objetos de origem desconhecida permanecem preservados. Não faça exclusão global por nome ou prefixo. O abridor mantém componentes reconhecidos e não atualiza automaticamente uma instância antiga; qualquer retirada exige identificar exatamente o alvo e conferir a versão em ambiente isolado.
- **Fibonacci importado indisponível:** o gate **UNVERIFIED_NATIVE** permanece. Importar, desenhar ou ensaiar no laboratório não comprova correspondência com o MT5. Medidas dependentes ficam bloqueadas; não forçar aprovação nem usar essas medidas em Preparar mensagem ou cópia.
- **Conta USC:** a unidade e os contratos precisam de perfil compatível. O utilitário `JPW_Alavancagem_Verificar_USC` pertence ao pacote de engenharia e segue protocolo próprio; sua ausência no ZIP de uso não libera leitura USC nem autoriza presumir escala. Use o roteiro USC do guia técnico quando necessário.

## Instalações antigas e engenharia

O ZIP de uso evita a lista de 24 testes e o laboratório no caminho inicial. O **JPW_Stoikus_Fontes_v1.23.0_painel-C5.zip** conserva o SDK completo: testes sintéticos, laboratório, utilitários USC/MDD, Supervisor opcional, produtores legados e referências do harness. A presença de um arquivo não é instrução para executá-lo. Tests e Fibo Lab servem à engenharia em ambiente isolado; resultados ficam em Experts e não homologam interação nativa.

Se sua pasta Scripts já contém versões antigas, faça um inventário com caminho, versão e data, copie os fontes e executáveis para backup e confira quais pertencem ao pacote atual. Só depois faça **remoção explícita dos fontes/executáveis obsoletos identificados**, se decidir organizar sua instalação. Não remova nem substitua **MQL5/Files**, bancos, locks, preferências ou estudos. Copiar o ZIP de uso não apaga programas antigos automaticamente.

Observer e Accountant separados são legados: **nenhum produtor legado deve executar junto com o Monitor**, mesmo em outro gráfico. Antes de uma futura atualização autorizada, confira todos os gráficos, inventarie e preserve a instalação anterior, retire os produtores antigos dos gráficos e use os programas e dependências da mesma versão. Supervisor é separado, opcional e não é necessário para a leitura; este guia não o arma.

Compilação, cliques, desenho, persistência e instalação em MT5 exigem evidência dos mesmos bytes. **NOT_RUN** não é PASS; a validação de host/site não autoriza negociação nem constitui aceite operacional.
