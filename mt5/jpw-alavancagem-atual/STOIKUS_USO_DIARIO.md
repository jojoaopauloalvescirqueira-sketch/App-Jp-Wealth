# Stoikus 1.22.1 — comece por dois gráficos

Use o pacote **JPW_Stoikus_Uso_Fontes_v1.22.1.zip**. Ele contém três componentes permanentes e um abridor pontual, com seus arquivos de apoio e imagens. O cálculo permanece na versão **1.9.0**. Esta entrega contém fontes: compilação e interação nativas dos mesmos bytes permanecem **NOT_RUN**.

**Instalação isolada de demonstração** é outra instalação MT5, com **pasta de dados separada** e conta demo, preparada para o primeiro ensaio sem negociação. Confira o caminho em Arquivo → Abrir pasta de dados. Trocar para uma **conta demo na mesma instalação** não separa arquivos, gráficos e configurações da sessão de uso.

| Papel | Programa no Navegador | Onde usar | O que permanece aberto |
| --- | --- | --- | --- |
| Monitor da conta | Experts → JPWealth → `JPW_Stoikus_Monitor` | Um gráfico de apoio reservado | O EA permanece anexado; mantenha esse gráfico aberto. |
| Conta e Cockpit | Indicadores → JPWealth → `JPW_Alavancagem_Atual` | O gráfico de trabalho | Indicador com resumo e botão **Stoikus · Conta**. |
| Canais e estudos | Indicadores → JPWealth → `JPW_NoCuda_Channels` | O mesmo gráfico de trabalho | Indicador com acesso **NoCuda · Gráficos**. |
| Abrir Conta + NoCuda | Scripts → JPWealth → `JPW_Stoikus_Abrir_Paineis` | Execute uma vez no gráfico de trabalho | O script termina; os dois indicadores continuam anexados. |

O Monitor observa a conta inteira, mesmo em um gráfico de símbolo diferente do seu trabalho. Não envia ordens nem arma o Supervisor. O abridor não inicia o Monitor: o MT5 aceita apenas um EA por gráfico, portanto use o gráfico de apoio reservado para evitar substituir outro robô.

## Instalar e abrir

1. Extraia o ZIP e leia este guia, apresentado no pacote como **LEIA_PRIMEIRO.md**. No MT5 de teste, escolha **Arquivo → Abrir pasta de dados**. No Parallels, faça isso dentro do MT5 do Windows.
2. Preserve uma cópia dos arquivos JPWealth existentes e identifique sua versão. Copie o conteúdo das cinco subpastas do pacote **MQL5** para as mesmas subpastas da pasta de dados: **Indicators**, **Experts**, **Scripts**, **Include** e **Images**. Crie **JPWealth** se necessário. Não substitua a pasta MQL5 inteira nem os arquivos de outros programas. O guia fica na pasta extraída.
3. Pressione **F4** para abrir o MetaEditor dessa instalação. Abra e compile com **F7**, separadamente: `JPW_Stoikus_Monitor.mq5`, `JPW_Alavancagem_Atual.mq5`, `JPW_NoCuda_Channels.mq5` e `JPW_Stoikus_Abrir_Paineis.mq5`. Exija **0 errors**, confira os avisos e o `.ex5` ao lado de cada fonte. Includes `.mqh` e imagens não são compilados separadamente. Compilar não executa o programa.
4. No terminal, abra o **Navegador (Ctrl+N)** e escolha **Atualizar / Refresh**. Abra um gráfico de apoio vazio, reservado para o Monitor. Arraste `JPW_Stoikus_Monitor` de **Experts → JPWealth** para ele. Nas **Entradas**, comece com `false`, `false` e evidência vazia; esses padrões permitem iniciar com cobertura desconhecida. Deixe **Permitir negociação algorítmica** desmarcado. Confirme **OK** e mantenha o gráfico aberto.
5. Selecione o gráfico de trabalho que quer usar. Em **Scripts → JPWealth**, arraste `JPW_Stoikus_Abrir_Paineis` para esse gráfico. Não há parâmetros obrigatórios. O abridor verifica o que já está anexado e acrescenta somente o que falta, sem aplicar template, substituir EA ou alterar as configurações dos indicadores presentes.
6. Confirme os dois indicadores com **Ctrl+I**: a lista mostra os nomes curtos **Stoikus · Cockpit 1.22.1** e **Stoikus · NoCuda Channels**, não os nomes dos arquivos. Use **Stoikus · Conta** para o Cockpit e **NoCuda · Gráficos** para os estudos. Para alterar parâmetros, selecione o indicador em Ctrl+I e abra **Propriedades → Entradas**. Para o Monitor, use **F7 no gráfico de apoio** (propriedades do EA no MT5; F7 no MetaEditor compila).

Você também pode anexar manualmente os dois indicadores, um após o outro, por **Indicadores → JPWealth**. Eles coexistem no mesmo gráfico. O abridor não exibe uma janela permanente: ele é um atalho para anexá-los, não o próprio painel. Quando adiciona um indicador ausente, usa seus padrões; altere depois as Entradas daquele indicador. Estudos e parâmetros de um indicador já presente são preservados.

## Primeira configuração: o que conferir

Comece pelos padrões. No NoCuda, escolha um **período-fonte definido**, normalmente **H1**, e mantenha a malha conforme sua preferência. Em Conta, ajuste fonte e canto se o resumo não estiver legível. Pips são opcionais: deixe símbolo vazio e tamanho zero até conhecer a convenção do instrumento. As declarações de cobertura do Monitor só devem mudar quando você tiver evidência verificável.

Procure primeiro o **rótulo da Entrada no MT5**, reproduzido abaixo. O nome técnico `Inp*` é uma referência secundária de compatibilidade. As tabelas seguem a ordem de cada componente; os parâmetros avançados podem permanecer nos padrões. Esses valores iniciam componentes novos. Preferências e estudos já salvos são preservados; confira no painel o período e a malha restaurados. Alterar uma Entrada não confirma automaticamente um estudo.

### Conta — 12 Entradas

| Rótulo da Entrada no MT5 | Nome técnico | Padrão | Unidade / escolha | Significado e zero/vazio |
| --- | --- | --- | --- | --- |
| Cadência solicitada (s; 1–3600; ciclo até 30 s; Stops até 5 s) | `InpUpdateSeconds` | `1` | Segundos, 1–3600 | Cadência solicitada. O ciclo completo tem limite de 30 s e Stops é revalidado em até 5 s; o timer não garante intervalos exatos. Zero é inválido. |
| Idade máxima da cotação (s; 1 a 30) | `InpMaxQuoteAgeSeconds` | `30` | Segundos, 1–30 | Idade máxima da cotação para qualificá-la como recente. Zero é inválido; não transforma histórico em Current. |
| Canto do painel | `InpCorner` | `CORNER_LEFT_UPPER` | Canto do gráfico | Referência inicial do resumo: superior esquerdo. Escolha outro canto se houver sobreposição. |
| Distância horizontal do canto (px; zero ou mais) | `InpOffsetX` | `16` | Pixels, ≥0 | Distância horizontal a partir do canto. Zero encosta na borda; não desativa o painel. |
| Distância vertical do canto (px; zero ou mais) | `InpOffsetY` | `40` | Pixels, ≥0 | Distância vertical a partir do canto. Zero encosta na borda. |
| Fonte compacta no gráfico (pt; 8 a 40) | `InpFontSize` | `8` | Tamanho de fonte, 8–40 | Fonte do resumo compacto; zero é inválido. |
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
- **Indicador duplicado ou legado:** use Ctrl+I para conferir nomes/versões, preserve configurações e deixe apenas uma instância do papel necessário. O abridor preserva indicadores com nomes legados reconhecidos; isso não comprova sua versão, compatibilidade ou funcionamento. Confira esses itens separadamente: repetir o abridor não atualiza um indicador antigo. Atualização exige conferir a versão, retirar a instância antiga e então anexar a nova; o primeiro ensaio segue isolado.
- **Fibonacci importado indisponível:** o gate **UNVERIFIED_NATIVE** permanece. Importar, desenhar ou ensaiar no laboratório não comprova correspondência com o MT5. Medidas dependentes ficam bloqueadas; não forçar aprovação nem usar essas medidas em Preparar mensagem ou cópia.
- **Conta USC:** a unidade e os contratos precisam de perfil compatível. O utilitário `JPW_Alavancagem_Verificar_USC` pertence ao pacote de engenharia e segue protocolo próprio; sua ausência no ZIP de uso não libera leitura USC nem autoriza presumir escala. Use o roteiro USC do guia técnico quando necessário.

## Instalações antigas e engenharia

O ZIP de uso evita a lista de 24 testes e o laboratório no caminho inicial. O **JPW_Stoikus_Fontes_v1.22.1.zip** conserva o SDK completo: testes sintéticos, laboratório, utilitários USC/MDD, Supervisor opcional, produtores legados e referências do harness. A presença de um arquivo não é instrução para executá-lo. Tests e Fibo Lab servem à engenharia em ambiente isolado; resultados ficam em Experts e não homologam interação nativa.

Se sua pasta Scripts já contém versões antigas, faça um inventário com caminho, versão e data, copie os fontes e executáveis para backup e confira quais pertencem ao pacote atual. Só depois faça **remoção explícita dos fontes/executáveis obsoletos identificados**, se decidir organizar sua instalação. Não remova nem substitua **MQL5/Files**, bancos, locks, preferências ou estudos. Copiar o ZIP de uso não apaga programas antigos automaticamente.

Observer e Accountant separados são legados: **nenhum produtor legado deve executar junto com o Monitor**, mesmo em outro gráfico. Antes de uma futura atualização autorizada, confira todos os gráficos, inventarie e preserve a instalação anterior, retire os produtores antigos dos gráficos e use os programas e dependências da mesma versão. Supervisor é separado, opcional e não é necessário para a leitura; este guia não o arma.

Compilação, cliques, desenho, persistência e instalação em MT5 exigem evidência dos mesmos bytes. **NOT_RUN** não é PASS; a validação de host/site não autoriza negociação nem constitui aceite operacional.
