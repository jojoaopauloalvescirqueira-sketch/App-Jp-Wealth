# JPW GENETRIX — fontes MT5 v1.16.1

**Da origem da operação à leitura do risco.**

## O que é hoje

O JPW GENETRIX é um conjunto de ferramentas locais para MetaTrader 5, desenvolvido para organizar a leitura das operações e tornar seus dados de exposição e risco mais claros e rastreáveis, seguindo a estrutura de desenvolvimento do JP Wealth.

Seus componentes reúnem alavancagem atual, resultado flutuante, distância ao stop da referência, Raiz N diagnóstica de uma e duas semanas, risco informativo dos stops e consulta do máximo de drawdown observado. O cockpit permite examinar posições e pendentes e preparar mensagens para conferência e compartilhamento manual.

O módulo NoCuda acompanha estudos geométricos e incorpora o trabalho com canais de Fibonacci. Na versão atual, as medidas do Fibonacci importado permanecem indisponíveis até comprovação da correspondência nativa.

O Genetrix combina indicadores, um EA observador e scripts auxiliares. Sua atuação atual é informativa e local; não executa negociações nem envia mensagens aos grupos. O site distribui arquivos e orientação, sem receber dados da conta.

Implementação em fontes, compilação, execução no MT5 e aceite operacional são estados separados. O programa não certifica automaticamente a conformidade de uma operação com o Estatuto ou com o Método NoCuda.

## Leituras e componentes

Indicador informativo de **nocional bruto das posições abertas ÷ equity**,
**flutuante ÷ saldo**, distância do mercado ao SL vigente de uma posição de
referência selecionada ou inferida e duas **distâncias Raiz N diagnósticas**,
de 1 e 2 semanas, para o símbolo exato do gráfico, e **risco informativo dos
stops**. As seis leituras aparecem por padrão num bloco compacto; cada linha
abre seu cartão no **Cockpit**.
Drawdown sobre saldo e seu máximo observado continuam calculados e ficam no
Cockpit sob demanda. Ocultar uma leitura do gráfico não interrompe seu cálculo
nem o registro do máximo observado.
O cálculo e a leitura da conta acontecem no MetaTrader 5. O site fornece o
pacote e este guia; não recebe dados da conta, resultados ou registros locais.
O pacote também inclui **JPW NoCuda Channels**, um segundo indicador para
acompanhar um canal de Fibonacci desenhado por você e consultar seus metadados.
O desenho manual por fechamentos permanece como modo legado. Ele pode ficar no
mesmo gráfico que o Cockpit, mas tem botão, desenho e registro próprios. O
desenho funciona sem o EA observador; o EA continua necessário para a linha
Stop risk do Cockpit.
O Cockpit também permite **Preparar mensagem** sobre uma posição aberta ou
ordem pendente escolhida pelo usuário. O catálogo é lido diretamente do MT5,
sem depender do EA. A mensagem permanece numa prévia local até uma ação
explícita de preparação para cópia manual ou exportação TXT; não há envio.

A alavancagem exibida não é a alavancagem contratada com a corretora, a margem
usada ou o risco até o stop. O DD sobre saldo e seu máximo observado não são o
DD operacional de ciclo do Estatuto nem o MDD pico-a-vale. Nenhuma dessas
leituras substitui os controles do JP Wealth. A distância Raiz N não define um
novo stop, não dimensiona posição, não estima probabilidade de perda e não
autoriza entrada. **F=1,5 é o padrão diagnóstico e F=1,8 é uma alternativa
selecionável**, sem homologar o parâmetro canônico P-21, que permanece PENDING.
A probabilidade de não toque exibida no Cockpit é uma referência browniana
ideal, não uma taxa comprovada no mercado ou a chance de um SL real sobreviver.
O risco dos stops usa o preço de execução até o SL vigente; não é a distância
do preço de mercado ao SL, nem certifica a conformidade da operação com o
Estatuto. Sem amostra recente e íntegra do EA observador, mostra `N/A`.

## 1. Entenda os programas

- **MetaTrader 5 (MT5):** terminal em que você acompanha a conta e os gráficos.
- **MetaEditor:** editor fornecido com o MT5; transforma o fonte em um programa
  executável pelo terminal. Compilar não executa o programa.
- **Indicador:** permanece anexado ao gráfico e atualiza sua apresentação.
  `JPW_Alavancagem_Atual` informa as métricas do Cockpit;
  `JPW_NoCuda_Channels` desenha e mede o canal. Nenhum dos dois envia ordens.
- **Script:** executa uma tarefa e termina. Há scripts de testes de cálculo,
  métricas e registro local, testes de perfil técnico e verificação das
  unidades dos contratos em contas USC. O script de consulta mostra, sob
  demanda, o máximo de DD/saldo já observado nesta instalação e conta.
- **Expert Advisor (EA):** pode reagir a eventos do terminal. O observador
  deste pacote registra fatos de execução e calcula localmente o risco
  hipotético dos stops; não envia, modifica ou cancela ordens. As cinco
  leituras anteriores funcionam sem ele; a sexta fica `N/A` sem sua amostra
  atual e íntegra.
- **.mq5:** fonte principal; **.mqh:** arquivo de apoio (include);
  **.ex5:** programa compilado que o MT5 executa.

**Resultado esperado:** distinguir o indicador que acompanha a conta dos
scripts que executam uma verificação pontual.

## 2. Baixe e extraia

Este pacote contém **fontes**. Confira no site a versão, o SHA-256 e os estados
separados de teste matemático, compilação e execução no MT5. Um download
compilado só é oferecido quando existem `.ex5` reais; compilação não equivale
à validação da leitura da corretora. Resultados das versões anteriores não
validam automaticamente os fontes da versão 1.16.1. Não há `.ex5` desta revisão
para distribuição sem compilação nativa comprovada dos fontes exatos.
**1.16.1 identifica o pacote e a identidade de execução do Cockpit/observador
recompilados desta fonte.** O cabeçalho compartilhado usa MQL `1.161`;
o componente NoCuda desta revisão declara `1.30`. Confira também o
fingerprint do pacote; o número da versão não comprova qual EX5
está instalado no terminal.

A revisão 1.16.1 adota a identidade pública **JPW GENETRIX**, com a logo vermelha do site nos cabeçalhos. Os nomes dos arquivos e das pastas permanecem iguais para preservar a instalação e os registros. No gráfico, o botão **Genetrix** abre o Cockpit; em Ctrl+I, os indicadores se identificam pela nova marca. No Navegador do MT5, procure os nomes técnicos `JPW_Alavancagem_Atual` e `JPW_NoCuda_Channels`. A logo está incorporada nos fontes/recursos; sua apresentação em MT5 e DPI depende da validação nativa dos bytes desta revisão, ainda **NOT_RUN**.

A revisão 1.16.0 acrescentou o modo **Fibonacci acompanhado** do NoCuda: captura
os parâmetros originais sem ajustar os preços ao Close, mantém uma sequência
congelada de barras e registra revisões por alterações manuais estáveis da
origem. O painel maior separa Canal, Agora, Projeção, Registro e Aparência.
O resolvedor futuro passa a admitir H1 e H4, com conferência independente da
grade de cada período. Estudos manuais e formatos financeiros são preservados.
**A equivalência entre o Fibonacci nativo e o resolvedor importado ainda é
UNVERIFIED_NATIVE. Medidas, projeções e comparações quantitativas dessa
importação ficam N/A até a validação nativa; não são anunciadas como prontas.**

A revisão 1.15.0 acrescenta a tabela unificada de posições com ticket, volume e
contribuição nocional/equity, além de fechamento exclusivo no cabeçalho. Essa
coluna preserva o núcleo financeiro 1.9.0 e não modifica registros locais.

A revisão 1.14.0 acrescenta a preparação local de mensagens por posição ou
pendente, com conferência da operação e prévia congelada. A apresentação
NoCuda/Cockpit da 1.13.0 permanece preservada.
A versão do cálculo financeiro continua **1.9.0**; as fórmulas, estados de
qualidade e formatos dos registros locais são preservados. Compilação,
interação e restauração por template desta revisão seguem **NOT_RUN** até
existir evidência dos mesmos fontes num MT5 isolado. Seleção e cópia manual
por **Ctrl+C** no campo de texto também estão **NOT_RUN**: não há confirmação
de funcionamento do clipboard no Windows nem no MT5 em macOS/Wine. Essa
pendência bloqueia a prontidão operacional do novo fluxo.

No Windows, clique com o botão direito no ZIP e escolha **Extrair tudo**.
Trabalhe na pasta extraída, não na visualização interna do ZIP.

**Resultado esperado:** uma pasta extraída com README e a organização MQL5.

## 3. Instale sem substituir a pasta MQL5 existente

1. No MT5 que você vai usar, abra **Arquivo → Abrir Pasta de Dados**. Em Windows
   no Parallels, faça isso dentro do próprio MT5 do Windows. Outra instalação
   pode ter uma pasta de dados diferente.
2. Na janela aberta, entre na pasta **MQL5 que já existe**. Preserve-a.
3. Copie somente os arquivos abaixo, um a um, da pasta extraída para o destino
   correspondente. Crie as subpastas `JPWealth` se ainda não existirem.

| Arquivo no pacote de fontes | Pasta dentro da pasta de dados do MT5 |
|---|---|
| `JPW_Alavancagem_Atual.mq5` | `MQL5/Indicators/JPWealth/` |
| `JPW_NoCuda_Channels.mq5` | `MQL5/Indicators/JPWealth/` |
| `JPW_NoCuda_Core.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_NoCuda_Projection_Core.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_NoCuda_Projection.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_NoCuda_Store.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_NoCuda_Terminal.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_NoCuda_Render.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_NoCuda_UI.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_NoCuda_Fibo_Core.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_NoCuda_Fibo_Terminal.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_NoCuda_Fibo_Store.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_NoCuda_Fibo_Sync.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_NoCuda_Fibo_Controller.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_NoCuda_Fibo_UI.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_UI_Focus.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_NoCuda_Logo.bmp` | `MQL5/Images/JPWealth/` (recurso de imagem usado na compilação) |
| `JPW_Genetrix_Brand.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Genetrix_Logo_Light_100.bmp` | `MQL5/Images/JPWealth/` (logo incorporada na compilação) |
| `JPW_Genetrix_Logo_Light_125.bmp` | `MQL5/Images/JPWealth/` (logo incorporada na compilação) |
| `JPW_Genetrix_Logo_Light_150.bmp` | `MQL5/Images/JPWealth/` (logo incorporada na compilação) |
| `JPW_Genetrix_Logo_Light_200.bmp` | `MQL5/Images/JPWealth/` (logo incorporada na compilação) |
| `JPW_Genetrix_Logo_Dark_100.bmp` | `MQL5/Images/JPWealth/` (logo incorporada na compilação) |
| `JPW_Genetrix_Logo_Dark_125.bmp` | `MQL5/Images/JPWealth/` (logo incorporada na compilação) |
| `JPW_Genetrix_Logo_Dark_150.bmp` | `MQL5/Images/JPWealth/` (logo incorporada na compilação) |
| `JPW_Genetrix_Logo_Dark_200.bmp` | `MQL5/Images/JPWealth/` (logo incorporada na compilação) |
| `JPW_Genetrix_Logo.provenance.md` | Documentação no ZIP; não precisa ser copiada para MQL5 |
| `JPW_Alavancagem_Core.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_MDD.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_Terminal.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_Profile.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_Genesis_Core.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_Genesis_Store.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_RaizN_Core.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_RaizN_Store.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_RaizN_Config.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_RaizN_Live.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_RaizN_Horizon.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_RaizN_Factor.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_RaizN_Observer.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_Panel.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_Cockpit.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_StopRisk_Core.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_StopRisk_Store.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_StopRisk_Terminal.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_Observer_Presence.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_Actions.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_Coordinator.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_Diagnostics.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_Diagnostics_Core.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_Presentation.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_Samples.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_Store_Result.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_Version.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_SignalCopy_Types.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_SignalCopy_Core.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_SignalCopy_Terminal.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_SignalCopy_Controller.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_SignalCopy_UI.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_SignalCopy_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_Alavancagem_Positions.mqh` | `MQL5/Include/JPWealth/` |
| `JPW_Alavancagem_Positions_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_Alavancagem_Diagnostics_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_Alavancagem_Observer.mq5` | `MQL5/Experts/JPWealth/` (necessário para Stop risk; opcional para as outras leituras) |
| `JPW_Alavancagem_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_Alavancagem_Metrics_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_Alavancagem_Profile_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_Alavancagem_Verificar_USC.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_Alavancagem_Consultar_MDD.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_Alavancagem_Genesis_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_Alavancagem_Genesis_Store_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_Alavancagem_RaizN_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_Alavancagem_RaizN_Store_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_Alavancagem_RaizN_Config_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_Alavancagem_RaizN_Live_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_Alavancagem_RaizN_Horizon_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_Alavancagem_RaizN_Factor_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_Alavancagem_Observer_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_Alavancagem_Panel_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_Alavancagem_StopRisk_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_NoCuda_Core_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_NoCuda_Store_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_NoCuda_Projection_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_NoCuda_Fibo_Tests.mq5` | `MQL5/Scripts/JPWealth/` |
| `JPW_NoCuda_Fibo_Lab.mq5` | `MQL5/Scripts/JPWealth/` (laboratório isolado) |

**Não substitua a pasta MQL5 inteira.** Se um arquivo JPWealth do mesmo nome já
existir, preserve uma cópia antes de atualizar somente esse arquivo. Não
substitua arquivos de outros indicadores ou robôs. O README e o `AGENTS.md`
(guia técnico para IAs) ficam na pasta extraída para consulta; nenhum deles
deve ser copiado para `MQL5`.

Se usar um pacote compilado, os `.ex5` incluídos vão para as mesmas pastas dos
respectivos `.mq5`: indicador em `Indicators/JPWealth`, scripts em
`Scripts/JPWealth` e observador opcional em `Experts/JPWealth`.

**Resultado esperado:** arquivos nas subpastas da mesma instalação, mantendo
intacto o restante do conteúdo do MT5.

## 4. Compile no MetaEditor

1. No MT5, pressione **F4** para abrir seu MetaEditor. No Mac, pode ser
   necessário usar **fn** junto da tecla de função.
2. Use **Arquivo → Abrir** no MetaEditor e abra
   `MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5`.
3. Selecione **X64 Regular** nas opções de compilação para compatibilidade
   entre computadores. Pressione **F7** ou **Compilar**.
4. Confira a aba **Erros / Errors** na parte inferior. Para prosseguir, são
   necessários **0 errors** e a geração do código. Leia e registre qualquer
   aviso antes de continuar; um aviso não equivale a uma compilação sem ressalvas.
5. Repita separadamente para `JPW_Alavancagem_Tests.mq5`,
   `JPW_Alavancagem_Metrics_Tests.mq5`, `JPW_Alavancagem_Profile_Tests.mq5`,
   `JPW_Alavancagem_Verificar_USC.mq5` e
   `JPW_Alavancagem_Consultar_MDD.mq5`,
   `JPW_Alavancagem_Genesis_Tests.mq5` e
   `JPW_Alavancagem_Genesis_Store_Tests.mq5`,
   `JPW_Alavancagem_RaizN_Tests.mq5` e
   `JPW_Alavancagem_RaizN_Store_Tests.mq5`,
   `JPW_Alavancagem_RaizN_Config_Tests.mq5`,
   `JPW_Alavancagem_RaizN_Live_Tests.mq5`,
   `JPW_Alavancagem_RaizN_Horizon_Tests.mq5`,
   `JPW_Alavancagem_RaizN_Factor_Tests.mq5`,
   `JPW_Alavancagem_Observer_Tests.mq5` e
   `JPW_Alavancagem_Panel_Tests.mq5` e
   `JPW_Alavancagem_StopRisk_Tests.mq5` e
   `JPW_Alavancagem_Diagnostics_Tests.mq5` e
   `JPW_SignalCopy_Tests.mq5`, na pasta Scripts/JPWealth.
   Compile também `MQL5/Experts/JPWealth/JPW_Alavancagem_Observer.mq5`
   se for usar a captura opcional de execuções. Compilar não anexa o EA.
6. Para desenhar canais, abra também
   `MQL5/Indicators/JPWealth/JPW_NoCuda_Channels.mq5` e pressione **F7**.
   Compile `JPW_NoCuda_Core_Tests.mq5`, `JPW_NoCuda_Store_Tests.mq5` e
   `JPW_NoCuda_Projection_Tests.mq5` e `JPW_NoCuda_Fibo_Tests.mq5` da pasta
   Scripts/JPWealth para os testes sintéticos. `JPW_NoCuda_Fibo_Lab.mq5`
   pertence ao protocolo de laboratório isolado; seu resultado não habilita
   automaticamente medidas nem comprova paridade completa. Copie também
   `JPW_NoCuda_Logo.bmp` e os oito `JPW_Genetrix_Logo_*.bmp` para `MQL5/Images/JPWealth/` antes de compilar;
   o recurso é incorporado ao executável.

Os arquivos `.mqh` são carregados como includes. **Não os compile separadamente.**
“Include não encontrado” exige conferir os arquivos em
`MQL5/Include/JPWealth/`.

**Resultado esperado:** um `.ex5` ao lado de cada `.mq5` compilado com sucesso.
Se um arquivo já veio compilado no pacote, esta etapa é dispensável para ele.

## 5. Execute o script de testes sintéticos

1. No MT5, abra o **Navegador** com **Ctrl+N**. Clique com o botão direito na
   lista e escolha **Atualizar / Refresh**.
2. Em **Scripts → JPWealth**, arraste `JPW_Alavancagem_Tests` para um gráfico
   em ambiente de teste isolado.
3. Deixe **Allow Algo Trading / Permitir negociação algorítmica desmarcado**
   e confirme **OK**.
4. Abra a **Caixa de ferramentas** com **Ctrl+T**, aba **Experts**. Confira a
   linha final `JPW_Alavancagem_Tests PASS: … asserts` ou `FAIL`.
5. Execute `JPW_Alavancagem_Metrics_Tests` da mesma forma. Ele confere as
   fórmulas e o registro local usando apenas identidades e diretórios
   sintéticos isolados. Depois execute `JPW_Alavancagem_Profile_Tests`, que
   verifica gravação, leitura e recusa de perfis técnicos sintéticos. Nenhum
   desses testes consulta conta real nem confirma os contratos da corretora.

6. Execute também `JPW_Alavancagem_Genesis_Tests` e
   `JPW_Alavancagem_Genesis_Store_Tests`. Eles cobrem seleção, distância e
   persistência com posições, identidades e diretórios **sintéticos**.
7. Execute `JPW_Alavancagem_RaizN_Tests`,
   `JPW_Alavancagem_RaizN_Store_Tests`,
   `JPW_Alavancagem_RaizN_Config_Tests`,
   `JPW_Alavancagem_RaizN_Live_Tests`,
   `JPW_Alavancagem_RaizN_Horizon_Tests`,
   `JPW_Alavancagem_RaizN_Factor_Tests`,
   `JPW_Alavancagem_Observer_Tests` e
   `JPW_Alavancagem_Panel_Tests` no mesmo ambiente isolado. Eles cobrem
   fórmula, fatores 1,5/1,8, probabilidade teórica, unidades, referência temporal,
   configuração, geometria e registros sintéticos;
   confira o PASS ou FAIL de **cada** script em Experts.
8. Execute também `JPW_Alavancagem_StopRisk_Tests` no ambiente isolado.
   Ele cobre posições, reservas pendentes, unidades e recusa de totais
   parciais com identidades sintéticas. Seu PASS não comprova que o EA anexado
   está publicando uma amostra válida na instalação real.

No **Journal / Diário**, “loaded successfully” seguido de “removed” é normal:
o script termina ao concluir a tarefa. A mensagem com o resultado está em
**Experts**. Se houver FAIL, preserve o log e não trate a versão como validada.

**Resultado esperado:** PASS para os casos sintéticos executados nessa versão.
Isso não comprova a leitura de contratos, cotações ou unidades da corretora e
não homologa o indicador em uma conta.

Execute também `JPW_Alavancagem_Diagnostics_Tests` no ambiente isolado. Ele
usa apenas diretórios e identidades sintéticos para verificar a trilha técnica,
coalescência, resumo, corrupção e exportação. Seu PASS não comprova interação nativa da UI
em outros ambientes nem a saúde da conta operacional.

Para o desenho, execute ainda `JPW_NoCuda_Core_Tests`,
`JPW_NoCuda_Store_Tests`, `JPW_NoCuda_Projection_Tests` e
`JPW_NoCuda_Fibo_Tests` da mesma pasta de scripts. Confira o resultado de
**cada** teste em Experts. Eles usam âncoras e arquivos sintéticos; um PASS
não comprova seleção por clique, projeção diária, desenho em diferentes
timeframes nem restauração por template no MT5 desta versão.

Execute também `JPW_SignalCopy_Tests` no ambiente isolado. Ele usa dados
sintéticos para conferir catálogo, agrupamento, métricas obrigatórias,
projeção de uma pendente e invalidação da prévia. Seu PASS não comprova o
clipboard, a interação dos controles ou a leitura da corretora; essas
verificações exigem recibos nativos separados da versão exata.

## 6. Verifique as unidades de uma conta USC

Para USD ou outra moeda fiduciária suportada, prossiga ao passo 7. Para
**USC**, a ferramenta usa a moeda retornada por `ACCOUNT_CURRENCY`, após
normalizar maiúsculas e espaços. Não deduz conta cent pelo nome da corretora,
sufixo `.m`, saldo ou casas decimais. Outras denominações cent não são
assumidas equivalentes.

**100 USC = 1 USD; 10.000 USC = US$ 100.** O equity é normalizado para USD uma
vez. A escala contratual é outra informação: um contrato de 1.000 unidades
pode representar a mesma exposição que um contrato bruto de 100.000
centésimos. Dividir somente o equity pode causar erro de 100 vezes.

1. Em ambiente isolado, abra **Navegador → Scripts → JPWealth** e execute
   `JPW_Alavancagem_Verificar_USC` sobre um gráfico, com Algo Trading desmarcado.
2. O script verifica os símbolos das posições abertas e do gráfico. Compara
   escalas 1 e 0,01 por meio de `OrderCalcProfit`, em movimentos hipotéticos
   positivos e negativos de dois tamanhos. **Não envia ordens.**
3. Confira em **Experts** a confirmação da verificação e da gravação do perfil.
   Falha nativa, metadados instáveis ou resultado ambíguo são recusados.
4. Volte ao indicador: ele reutiliza a confirmação compatível. Para verificar
   um novo instrumento, execute o script no gráfico desse instrumento.

A concordância exigida é de 1% e precisa identificar uma única escala, com
resultados suficientes para evitar ambiguidade de arredondamento. O cálculo
nativo de lucro pertence ao script, nunca ao indicador.

O perfil técnico fica em **MQL5/Files/JPWealth/Alavancagem**, separado por hash
da identidade da conta. Contém versão, assinatura das especificações, escala
por símbolo e data; não contém nome, login em texto, senha, saldo, equity ou
posições. Somente perfil compatível com a conta e as especificações atuais
pode ser usado. Alteração de contrato ou inconsistência de valores de tick
exige nova verificação. Não edite o perfil para forçar uma escala. Perfil
corrompido ou instrumento sem confirmação impede o total.

**Resultado esperado:** confirmação de cada instrumento necessário, ou recusa
explícita. Sem confirmação completa, não há total parcial.

## 7. Anexe o indicador e leia o estado

1. No Navegador, em **Indicadores → JPWealth**, arraste
   `JPW_Alavancagem_Atual` para um gráfico. Faça o primeiro uso em ambiente de
   demonstração isolado.
2. Confira as entradas e confirme **OK**. `InpGenesisTicket=0` solicita
   seleção automática somente quando houver um grupo único de posições com
   símbolo exato e direção iguais e um horário de abertura inequivocamente
   mais antigo. Se houver ambiguidade, confira o ticket na aba **Trade /
   Negociação** e informe-o nas Entradas; o símbolo do gráfico não escolhe a
   referência. Não é necessário habilitar Algo
   Trading, DLL ou WebRequest, nem fornecer credenciais ao site.
3. Leia `JPW: Leverage`, `Floating P/L`, `Genesis SL`,
   `Raiz N diag. 1W`, `Raiz N diag. 2W` e `Stop risk`, cada qual com seu estado e F explícito quando aplicável. As duas
   distâncias usam o **símbolo exato deste gráfico**. Clique numa linha para
   abrir seu cartão no **Cockpit**, ou use o botão **Genetrix** para abrir o
   resumo. Nele você pode escolher F=1,5 ou F=1,8 e ver DD/saldo, máximo
   observado, razões, horários, N, probabilidade teórica de não toque e
   proveniência; o máximo também pode ser consultado pelo script separado.
   Passe o mouse sobre cada linha para ver a dica completa. A sexta linha
   exige uma amostra recente e íntegra do EA observador; sem ela,
   mostra `N/A` em vez de conservar no gráfico um total antigo. Sem evidência
   recente do EA, confira o aviso `Check Observer` em Cockpit → Stops/Sistema.
   A entrada
   `InpUpdateSeconds` solicita a cadência (padrão: 1 segundo), mas a apuração
   completa é limitada pelo frescor a no máximo 30 segundos; Stop risk confere
   a sessão do EA e a composição em ciclo próprio de no máximo 5 segundos.
   O timer do MT5 não garante esses intervalos exatos.

Leverage e Floating P/L consideram a conta inteira, independentemente do
símbolo do gráfico, direção, Magic Number ou origem da posição. Compras e
vendas são somadas pelo valor absoluto no nocional; ordens pendentes ficam
fora até virarem posições. Genesis SL acompanha somente a referência
selecionada. As duas distâncias Raiz N acompanham somente o instrumento exato
do gráfico; não escolhem automaticamente uma operação. DD e MDD permanecem
independentes das seis linhas e são mostrados no Cockpit.

| Estado | Significado |
|---|---|
| **Current** | Conexão, referência temporal confiável e dados necessários válidos e recentes, dentro do limite padrão de 30 segundos. Qualifica dados, nunca homologação estatutária ou validação estatística do F. |
| **Estimated** | Leitura completa sem comprovação de atualização. Para a alavancagem, a dica informa o motivo e a cotação mais antiga usada, em horário do servidor. Flutuante e DD são estimados quando conexão, referência temporal ou contexto de crédito não são confiáveis; suas dicas usam o horário UTC observado pelo indicador no relógio do computador. |
| **N/A** | Os dados necessários para aquela métrica estão inválidos ou a leitura da conta é inconsistente. Uma conversão de nocional indisponível não oculta percentuais válidos; equity zero ou negativo ainda permite DD quando o saldo é válido. |

A primeira linha mostra, por exemplo, **`JPW: Leverage 2,75x · Current`**, **`JPW: Leverage ≈2,75x · Estimated`**
ou **`JPW: Leverage N/A`**. As demais podem mostrar **`Floating P/L: +1,25%`**,
**`Genesis SL: 3,52%`**, **`Raiz N diag. 1W: ≈3,29% · F1,5 · Estimated`** e
**`Raiz N diag. 2W: ≈4,65% · F1,5 · Estimated`**. São exemplos sintéticos com
`P0=100`, `ATR=0,40`, `N=30/60` e F=1,5; N real não é fixado em 30/60.
DD/saldo, por exemplo **`3,00%`**, fica no Cockpit, não ocupa
uma linha permanente. Uma leitura estimada acrescenta **`· Estimated`** ao
texto pertinente. Durante a preparação,
ela mostra **`JPW: Leverage Loading`** ou **`JPW: Leverage Updating`**. A dica do indicador
conserva o motivo completo, a data da cotação mais antiga quando aplicável e a
base do equity. O texto é um objeto do indicador colocado próximo ao cabeçalho;
ele não é inserido no nome nativo do par pelo MT5.

A estimativa é automática quando há dados completos, inclusive sem conexão ou
com feed parado. É uma nova apuração dos dados disponíveis, não a conservação
do total anterior. O denominador é o **último equity informado pelo terminal**:
ele e as cotações não formam fotografia histórica sincronizada. Sem referência
temporal confiável, não é inventada uma idade relativa. Quando novos dados
recentes e verificáveis voltam, o estado Current é restaurado.

`0,00x` exige ausência confirmada de posições e equity válido; exposição
positiva menor que 0,01 aparece como `<0,01x`. Durante preparação ou coleta
ainda não consistente, não interprete o número anterior como leitura atual.
Nos percentuais, zero verdadeiro aparece como `0,00%`; um valor não nulo abaixo
de 0,01% recebe a indicação `<0,01%`, com sinal positivo no flutuante positivo.

**Resultado esperado:** seis linhas pequenas e cinzas por padrão, com estado
por métrica, sem encobrir o cabeçalho do instrumento. O **Cockpit** abre uma
janela temporária para consulta e configuração; nenhuma de suas páginas ocupa
o gráfico permanentemente.
**Ctrl+I** lista os indicadores anexados ao gráfico atual; **Ctrl+N** mostra
programas instalados. O script de testes encerrado não permanece ativo.

### Entenda a distância ao SL da referência

A terceira linha usa uma **posição de referência**, não todas as posições.
`0` nas Entradas permite uma seleção inicial **inferida** somente quando todas
as posições abertas estão no mesmo grupo de símbolo exato e direção, com uma
posição inequivocamente mais antiga. Isso não prova que ela seja a operação
Gênese registrada no JP Wealth. Com vários grupos, horários empatados ou
ausentes, informe o **ticket positivo** da posição desejada em
**Ctrl+I → JPW_Alavancagem_Atual → Propriedades → Entradas → InpGenesisTicket**.
O gráfico em que o indicador está anexado não escolhe a posição.

A referência fica identificada localmente pelo `POSITION_IDENTIFIER` do MT5,
mesmo se o ticket mudar ou houver fechamento parcial. Posições posteriores não
substituem a referência. **Limite herdado da prévia 1.3.0:** ausência do identificador na
lista local deixa o encerramento indeterminado; conexão, relógio e duas
leituras iguais não comprovam sincronização das posições após reconexão. O
indicador não grava um encerramento irreversível sem essa prova. Direção
divergente bloqueia a medição sem gravar reversão irreversível. Reiniciar ou
trocar timeframe não escolhe sucessora. Para acompanhar outra referência,
informe um **novo ticket** nas Entradas. Em conta netting
OTC, a leitura é rotulada **Position SL**; em hedging, **Genesis SL** usa o SL da posição
individual. Esta métrica não cobre execução em bolsa.

Na compra, a distância é **Bid − SL**; na venda, **SL − Ask**. A linha compacta
mostra **% do preço**; a dica e o Cockpit podem informar **pontos**
(`distância / SYMBOL_POINT`). Ela não é risco
financeiro agregado e não indica que o stop tenha sido executado. “Nível do
SL alcançado/ultrapassado” se refere somente ao preço observado. “Gênese sem
SL” mantém a referência selecionada. Se outra posição do mesmo grupo tiver
um SL válido mais próximo, apenas a dica avisa; não troca a referência.

Pips são opcionais: preencha `InpPipSymbol` com o **símbolo exato** e
`InpPipSize` com o tamanho confirmado. O indicador não deduz pip pelas casas
decimais. Em USC, preços e distância não recebem fator 100. `Current (quote)`
qualifica a **cotação** com conexão e tick recente, não a sincronização do SL
local com o servidor; mesmo conectado, uma alteração em outro terminal pode
ainda não estar refletida. `Estimated` indica dados completos sem frescor
comprovado, inclusive offline. `N/A` significa falta ou ambiguidade dos dados da
referência; as outras métricas e o MDD continuam independentes.

O registro da referência fica em `MQL5/Files/JPWealth/Alavancagem/`, separado
dos slots MDD e do perfil USC. Seu nome é opaco; ele guarda identificador,
símbolo, direção, horário inicial, ticket de origem e estado, sem guardar SL,
cotações, saldos ou ordens. Um arquivo inválido ou incompatível bloqueia nova
inferência. O site não lê nem distribui esse registro.

### Entenda Stop risk sem confundi-lo com a distância Genesis SL

A sexta linha informa a **perda hipotética até os stops vigentes** na moeda da
conta e como percentual do **saldo atual**: `Stop risk: [valor] [moeda] ·
[percentual]% balance · Current`. Sem amostra atual, a linha mostra `N/A`.
O percentual é uma referência informativa de tela; os
limites do Estatuto usam o **Saldo Inicial de Referência**, e o Risco
Comprometido estatutário inclui outras parcelas. Esta linha não declara que
uma operação está conforme o Estatuto, não autoriza Defesa nem certifica que
posições do terminal pertencem à mesma tese. P-07 e P-19 permanecem pendentes.

Em conta **hedging**, o EA observador usa `OrderCalcProfit` para cada posição
aberta com o **volume remanescente**, preço de execução e SL atual. Só a perda
hipotética adversa entra no risco: `max(0, -lucro_hipotético)`. Um SL que
protege lucro contribui **zero** para essa parcela, sem compensar o risco de
outra posição. Ordens pendentes que **ampliariam** a mesma operação por
símbolo exato e direção recebem reserva separada, pelo volume pendente ainda
aberto e pela distância da entrada planejada ao SL. Reserva não é posição
executada, e não se presume exclusividade entre ordens pendentes. O total
mostrado soma as parcelas válidas sem arredondá-las antes de dividir pelo
`ACCOUNT_BALANCE` finito e positivo. `OrderCalcProfit` devolve a moeda da conta;
em USC, valor e saldo permanecem na mesma unidade, sem conversão unilateral.

Abra **Cockpit → Stops** para separar posições abertas de reservas pendentes e
conferir tickets, símbolo, direção, volume remanescente, preço de execução ou
entrada planejada, SL, perda hipotética e motivo de qualquer `N/A`. A
ordenação cronológica ajuda a examinar os fatos, mas **não prova Gênese ou
tese**. Uma leitura adicional da distância **mercado atual → SL** aparece no
menu como informação separada: ela não substitui o risco **execução → SL** da
linha. Gaps, deslizamento, custos e perdas já realizadas não entram nessa
estimativa.

A sexta linha só apresenta uma amostra **atual, completa e atribuída à mesma
instalação/conta**. O EA publica um snapshot local versionado; o indicador
apenas o lê e valida. EA ausente, amostra antiga, mudança de posições ou
pedidos, SL ausente, stop-limit não suportado ou outra entrada inválida deixam
o **total consolidado N/A**, sem soma parcial ou zero inventado. O Cockpit pode
mostrar a **última amostra** para inspeção, rotulada `LAST · NOT ACTIVE`, mas o gráfico
não a reaproveita como valor atual. Zero exige universo completo e vazio ou
parcelas válidas cujo risco seja realmente zero.

O EA emite um sinal **técnico e temporário** de presença/estado para a mesma
instalação e conta, inclusive antes do primeiro snapshot financeiro. Sem sinal
recente, “observador não confirmado” significa que o indicador **não conseguiu
confirmar** o observador; não prova sozinho se ele está desligado em todos os
gráficos. Se o sinal existe, mas a publicação está pendente ou falhou, o
Cockpit distingue **aguardando primeira amostra**, **falha de publicação** e
**amostra de stops indisponível**. Presença não valida risco: mesmo com
EA detectado, o valor fica `N/A` até haver uma amostra financeira atual,
completa e coerente. A sinalização técnica não guarda tickets nem valores.

Em **netting**, o MT5 agrega a posição e não permite atribuição auditável por
ordem da operação. O total **por operação** fica `N/A`; o menu pode mostrar a
posição agregada como contexto, sem chamá-la de Gênese ou Defesa. A métrica
não escreve em MDD, Gênese, USC ou Raiz N. O site não recebe snapshots nem
dados de conta.

### Entenda a Raiz N diagnóstica de 1W e 2W

As duas últimas linhas usam somente o **símbolo exato do gráfico**. Para cada
apuração corrente, `P0=(Bid+Ask)/2` vem do mesmo tick e o ATR nativo
`iATR(55,H4)` vem da última barra H4 concluída. `N` é o número de
fechamentos H4 **esperados** para aquele símbolo entre o instante de referência
e o fim de uma janela móvel de **7 dias civis do servidor (1W)** ou **14 dias
civis do servidor (2W)**. Não é o período 55 do ATR; não é um 30/60 ou 42/84
fixo. Essas janelas são cenários padronizados, não a intenção comprovada de
duração de uma operação. Quando o horário atual do servidor não pode ser
verificado, a referência passa a ser o **último tick disponível do próprio
símbolo**: o Cockpit informa esse carimbo e as saídas ficam **Estimated**. Não
interprete então a janela como iniciada no presente verificado.

O valor mostrado é uma **distância diagnóstica com F escolhido pelo usuário**:
`Dpreço=ATR × √N × F` e `D%=100 × ATR × √N × F / P0`.
Sem preferência salva, F=1,5. Em **Cockpit → Raiz N → F 1,5/1,8**, escolha uma das duas
opções; **Aplicar** persiste a escolha por instalação, conta e símbolo exato,
e **Cancelar** descarta o rascunho. O registro versionado fica separado do N/F
manual antigo, dos cenários, do MDD e da Gênese. Registro corrompido,
incompatível, ocupado ou inacessível não recebe o F padrão silenciosamente:
as duas saídas ficam **N/A**, com motivo. A dica e o Cockpit mostram preço,
ATR/barra, `N`, F usado, início/fim da janela, qualidade da cotação e
calendário. Em USC, preço e distância não recebem fator 100. Um número Raiz N
diagnóstico não é stop recomendado, dimensionamento, probabilidade de perda ou
autorização de entrada.

Sem um calendário datado, versionado, com cobertura dos 14 dias e aprovação
verificável para o símbolo, a projeção usa a grade semanal recorrente do MT5
confrontada com barras já observadas e fica **Estimated**. Feriados, exceções
de sessão e mudança de horário podem alterar os fechamentos futuros. Metadados
insuficientes ou contraditórios produzem **N/A**, nunca zero ou exatidão
inventada. Esta revisão não traz hash de calendário aprovado; por isso as
distâncias entregues serão **Estimated** ou **N/A**, não Current, mesmo se o
tick estiver recente. A cotação só é recente depois de um tick novo observado após a
inicialização, com referência temporal confiável e dentro de 30 segundos.
`Current` qualifica apenas qualidade dos dados; não homologa o modelo.

O Artigo 9 usa `Dpreço=ATR × √N × F`. A escolha de F=1,5 ou F=1,8 foi aprovada
para **este diagnóstico**, não para o parâmetro canônico P-21, que continua
**PENDING**. Isto não comprova eficácia no mercado nem homologa um stop. Uma
política estatutária futura exigirá aprovação distinta, com horizonte, escopo,
vigência, autoridade e hash. Com dados **sintéticos** `P0=100`, `ATR=0,40` e
`N=30`, F=1,5 produz aproximadamente `3,2863` no preço e `3,2863%` de P0;
F=1,8 produz aproximadamente `3,9436` e `3,9436%`. A contagem real de N não
é fixada em 30.

O **Cockpit** apresenta também a **probabilidade teórica de primeiro não toque**
de uma barreira adversa hipotética, fixada a partir do P0 no instante da
leitura: `2Φ(√(8/π) × F) − 1`. A referência é **98,332% para F=1,5** ou
**99,593% para F=1,8**. Para o mesmo F, 1W e 2W têm a mesma probabilidade
**nessa construção ideal** porque cada barreira é novamente dimensionada com
`√N`; as distâncias em preço são diferentes. O modelo supõe movimento
browniano sem drift, volatilidade constante e aproximação entre ATR e
dispersão. Não é a probabilidade remanescente de um SL real, chance de lucro,
probabilidade de perda da carteira ou cobertura empírica do mercado.

**Configurações manuais N/F e cenários da v1.4.0 continuam legíveis em
Cockpit → Raiz N → N/F legado**, separados das duas distâncias automáticas. Não são
migrados, aplicados silenciosamente aos horizontes 1W/2W ou reescritos. Cenário declarado após
entrada conserva rótulo retrospectivo; vínculo e comparação com SL continuam
exigindo escolha explícita. O símbolo do gráfico não escolhe uma operação.

### Use o EA observador para capturas e Stop risk

`JPW_Alavancagem_Observer` é um **EA observador local** separado. É opcional
para as cinco leituras anteriores e necessário para a amostra da sexta linha
`Stop risk`. Em MT5 isolado, depois de compilar, atualize o Navegador e anexe-o
**uma vez** em
**Expert Advisors → JPWealth** a um gráfico aberto **da mesma instalação do
terminal** em que está o indicador. Um gráfico dedicado facilita verificar se
o EA continua anexado; fechá-lo ou substituí-lo por outro EA interrompe a
observação. A ativação é manual, não feita pelo indicador nem por esta página.
Verifique em **Experts** seu
estado e a identidade da instalação/conta antes de considerar uma captura
concluída. Ele não envia ordens, não altera stops e não precisa de permissão
para negociar; as condições de carregamento/eventos do EA ainda precisam ser
confirmadas em execução nativa isolada. Não o instale na sessão operacional
para suprir uma validação pendente.

O observador registra o **primeiro negócio executado** de cada episódio
lógico como `P0` inicial e, em processo separado, apura o risco hipotético até
os stops em uma amostra identificada. Não prova o preço de decisão humana.
Adições e fechamentos parciais não reescrevem o primeiro registro; reversão
netting inicia outro episódio. Se o EA for instalado depois da entrada, um
registro reconstruído do histórico só pode ser rotulado **Reconstructed**,
quando a evidência for suficiente, nunca como captura observada no momento.
O ATR é lido da barra H4 encerrada antes do horário do negócio, ainda que o
evento seja processado depois. A projeção do calendário semanal é resolvida
no processamento e traz seu próprio horário de observação; não se afirma que
essa grade já era conhecida na execução ou na decisão humana. Dados obtidos
depois não são promovidos retrospectivamente a fatos capturados na entrada.

Os snapshots de execução e a amostra de Stop risk ficam em registros locais
separados sob
`MQL5/Files/JPWealth/Alavancagem/`, com chave opaca de conta, versão,
transações e identidades idempotentes de negócio/episódio. O indicador apenas
lê; o site e o ZIP não leem nem distribuem esses registros. Os registros de USC,
MDD, Gênese e cenários antigos permanecem separados. Falha de gravação ou
histórico incompleto não significa captura concluída.

### Abra o Cockpit para se aprofundar

O botão **Genetrix** abre uma janela **centralizada e temporária**. A primeira
visão reúne seis cartões: Leverage, Floating P/L, Genesis SL, as duas
distâncias Raiz N e Stop risk. Cada cartão mostra valor, `Current`, `Estimated` ou
`N/A` e um motivo curto. Clique num cartão, ou na respectiva linha do gráfico,
para examinar fórmula, insumos, origem, horário, limites e motivo do estado.
Nesta revisão, a janela solicita até 1040 × 760 px e permanece centralizada
dentro da área disponível do gráfico. Cabeçalho, cartões e rodapé têm superfícies
distintas para orientar a leitura; em gráfico menor, a paginação e o botão
Fechar continuam acessíveis. A fonte do Cockpit segue independente da fonte
pequena do gráfico.
Na apresentação 1.13.0, o valor recebe destaque dentro de seu cartão; o estado
fica separado da explicação curta. A aba ativa e o controle em foco têm
destaque próprio, e ações como Aplicar e Atualizar são diferenciadas da
navegação. O tema acompanha o contraste do gráfico, inclusive nas opções
legadas. Isso não muda o significado de `Current`, `Estimated` ou `N/A`.
As abas **Visão geral**, **Stops**, **Raiz N**, **Sistema** e **Ajustes** separam
o resumo das explicações. Estado dos dados mostra qualidade da cotação, ATR,
calendário e registros locais. Os estados descrevem a leitura daquela
amostra, não a aprovação estatutária do modelo.

O resumo também apresenta DD/saldo, máximo observado e probabilidade teórica
de primeiro não toque. Quando há registro do EA observador legível, mostra a
**última captura registrada** e seu horário; isso não comprova que o EA esteja
anexado ou ativo agora. A aba Stops pode mostrar uma amostra antiga somente
para auditoria, rotulada `LAST · NOT ACTIVE`; o valor antigo não ocupa a linha do gráfico.
Ausência, lock ocupado ou registro MDD inválido são
mostrados sem inventar máximo zero. O lock de leitura é liberado antes de
desenhar a janela. Se a conta ou o símbolo mudar, a amostra anterior não deve
ser apresentada como atual.

Em **Stops → Posições**, consulte as posições numa tabela única: papel,
**ticket da posição no MT5**, volume remanescente, contribuição de **Leverage**,
risco nominal e percentual sobre balance. **Conta** mostra todos os instrumentos
e direções, agrupados; **Operação** filtra somente o símbolo exato e a direção
atribuídos ao risco dos stops. A lista tem rolagem na mesma aba quando não couber
inteira. Isso não amplia o total de Stop risk para posições de outra tese.

Ticket, volume e alavancagem vêm da leitura direta do indicador, sem depender
do EA nem de SL válido. Cada contribuição é **nocional bruto da posição ÷
equity da mesma leitura**, com as conversões e a escala contratual já verificadas;
a soma antes do arredondamento confere com Leverage da conta inteira.
Buy e Sell não se compensam. Netting mostra a posição agregada. Em USC, equity e
nocionais são normalizados na mesma unidade; preços não recebem fator 100.
A contribuição não é margem usada, alavancagem contratada ou risco até o stop.

Os valores de risco continuam exigindo amostra coerente do observador e
correspondência com a posição atual. Sem essa evidência, somente os campos de
risco ficam `N/A`. Um risco antigo consultável conserva **LAST · NOT ACTIVE**
e seu horário; ele não é misturado com uma alavancagem atual sem identificação.
Pendentes permanecem em seção separada e não entram na contribuição de
alavancagem das posições executadas. A hipótese após execução pertence ao
Signal Copy.

Use **×** no cabeçalho, **Fechar** no rodapé ou **Esc** para sair da janela.
Navegar, rolar ou fechar não muda ordens, cálculos ou registros financeiros.
A restauração, a rolagem e os cliques desta revisão precisam de verificação
nativa dos mesmos bytes; sem ela, permanecem **NOT_RUN**.

Em **F 1,5/1,8**, selecione uma opção; só **Aplicar** salva essa preferência e
**Cancelar** mantém o F anterior. **N/F legado** e os cenários antigos seguem
em área própria e não governam os horizontes 1W/2W. Fechar, navegar ou
redimensionar o Cockpit não altera posições, ordens, stops nem os registros
financeiros.

### Prepare uma mensagem local de posição ou pendente

Abra **Cockpit → Preparar mensagem**. Esta consulta lê posições e ordens
pendentes diretamente do terminal; funciona independentemente do EA
observador. Ela não muda a sexta linha Stop risk, que continua exigindo a
amostra financeira do EA. Não é um novo sinal nem uma autorização de entrada.

1. Escolha **Posições** ou **Pendentes** e depois **um item** do catálogo.
   Confira instrumento exato, direção, ticket, horário, volume remanescente,
   entrada, SL e TP. Stop-limit não suportado ou leitura inconsistente
   impedem a preparação.
2. Confira o grupo da operação: somente o **mesmo símbolo exato e direção**.
   O terminal não comprova a tese. Exclua manualmente itens que não pertençam
   à operação e confirme a composição; em netting, a posição é **agregada**,
   sem decomposição auditável em ordens originais.
3. Confira os papéis propostos por antiguidade e ajuste-os quando necessário.
   **Gênese, Defesa 1, Defesa 2…** são rótulos transitórios desta mensagem,
   conferidos pelo usuário; não certificam a tese nem mudam a referência
   Gênese ou seus arquivos. Empates ou papéis ambíguos exigem conferência.
4. Gere a **prévia**. SL, alavancagem da conta, Raiz N 1W/2W e flutuante/saldo
   precisam ter leituras válidas. Uma leitura completa **Estimated** pode
   integrar a mensagem com seu estado e horário explícitos; `N/A` em uma
   dessas métricas bloqueia a preparação. **TP é opcional** e sua ausência
   aparece como **Sem TP**, nunca como zero inventado.
5. Leia a mensagem inteira antes de preparar a cópia manual ou escolher
   **TXT local**. Ela contém dados financeiros: confira o conteúdo e o
   destino escolhido por você antes de compartilhar fora do terminal.

A prévia usa uma **amostra congelada**, com identidade e horários. Navegar,
paginar, redimensionar e receber ticks não reescrevem seu texto. Antes de uma
nova preparação ou exportação, o fluxo revalida a leitura, incluindo TP;
mudança de conta, símbolo, composição, volume ou SL/TP invalida a prévia e
exige nova coleta e conferência. Fechar descarta esse estado transitório;
nenhuma atribuição de papel é gravada nos registros financeiros existentes.

A mensagem separa **entrada → SL** de **mercado atual → SL** em percentual:
as duas bases não são intercambiáveis. São distâncias de preço, não perda
nominal, garantia de execução ou substituto do Stop risk. A captura usa o
horário UTC observado no computador; horários de cotação, barra ATR e abertura
são identificados como horário do servidor quando essa é sua origem.

**Pendente é uma hipótese separada.** A alavancagem atual da conta exclui
pendentes. A projeção considera a execução de **somente a pendente escolhida,
no volume ainda pendente**, mantendo equity e cotações da amostra constantes.
Em hedging, acrescenta exposição bruta; em netting, considera a compensação
ou reversão da posição agregada. Não presume execução simultânea de outras
pendentes e não antecipa custos, lucro futuro ou equity na execução.

Raiz N 1W/2W usa o **símbolo exato do item escolhido**, com sua própria
cotação, ATR, calendário e preferência F. Escolher outro instrumento não
reutiliza os valores Raiz N do gráfico hospedeiro. A alavancagem atual e o
flutuante continuam sendo leituras da **conta inteira**, e os estados de cada
métrica ficam preservados.

Na conferência, use **alterar** para informar o papel: **0 = Gênese**,
**1 = Defesa 1**, **2 = Defesa 2**, e assim por diante. Aplicar confirma só
a mensagem; Cancelar preserva o papel anterior. **Estado** abre o motivo
completo e, após exportar, o caminho do TXT mesmo em janela compacta.

Antes de gerar a prévia, o fluxo renova a leitura apenas se a composição e
o contexto continuarem iguais; assim a conferência não exige uma corrida.
Preparar ou exportar exige revalidação em até **30 segundos da leitura da
prévia**. Se esse prazo passar, volte à conferência e gere outra prévia; os
preços do texto anterior não são renovados durante sua leitura ou seleção.

**Cópia manual:** a ferramenta prepara texto para seleção no campo; o usuário
seleciona e usa **Ctrl+C**. O indicador não escreve diretamente no clipboard,
não usa DLL e não informa **“Copiado”**, pois não confirma o conteúdo da área
de transferência. No macOS/Wine, não se presume equivalência com Command+C.
A interação nativa de seleção e Ctrl+C desta revisão está **NOT_RUN** e
permanece um bloqueio até prova em MT5 isolado.

**TXT local:** é uma alternativa acionada explicitamente, sem janela de
seleção de arquivo. Após a gravação confirmada, o painel informa a pasta e o
caminho exatos dentro de **MQL5/Files/JPWealth/SignalCopy/**. Para encontrá-lo,
abra **Arquivo → Abrir pasta de dados → MQL5 → Files → JPWealth → SignalCopy**.
O nome do arquivo não inclui login, conta ou ticket. O conteúdo não é
registrado em logs de diagnóstico, enviado ao site ou publicado
automaticamente; permanece no arquivo local criado por sua ação.

**Resultado esperado:** uma mensagem consultável e conferida de um item
selecionado, com origem, estados e limites; a preparação não abre, modifica
ou cancela ordens, posições ou stops.

### Confira a saúde e a proveniência em Sistema

Qualidade da métrica (`Current`, `Estimated`, `N/A`), saúde técnica
(normal, atenção, indisponível) e cobertura histórica (completa, incompleta,
desconhecida) são informações diferentes. Cada coleta aceita tem uma referência;
redesenhar ou redimensionar o painel não cria outra coleta financeira. Métricas
com cadências diferentes mantêm suas próprias referências e horários.

O observador registra lacunas quando sua fila excede a capacidade, uma tentativa
se esgota ou uma gravação falha. Uma captura recuperada é uma reconstrução;
não se converte em captura original. A última evidência recente não prova
atividade contínua nem garante que todos os eventos foram observados.

A trilha local guarda eventos essenciais em namespace próprio, separado de
USC, MDD, Gênese, Raiz N e Stops. Retenção padrão: **30 dias / 20 MiB**;
repetições são agrupadas. A rotação alcança somente diagnósticos. Nenhuma série
contínua de cotações, saldos, posições ou valores das métricas é gravada ali.
Falha da trilha é visível e não bloqueia os cálculos existentes.

A exportação técnica local é feita sob demanda, depois de uma prévia. Ela
exclui credenciais, login, tickets e valores financeiros. O site não recebe
registros da conta. Não confunda este arquivo com backup financeiro.

A interface compacta mantém o nome, valor e estado juntos; caso o espaço não
comporte a leitura, oferece acesso ao cockpit em vez de um número ambíguo.
A janela usa fonte própria de tamanho 11, mantém Fechar/Voltar acessíveis e
organiza os assuntos em Visão geral, Stops, Raiz N, Sistema e Ajustes.
Tab/Shift+Tab percorrem controles, Enter aciona a seleção e Esc volta/fecha;
a edição de campos preserva suas teclas. Redimensionar mantém o rascunho.

Esta revisão prepara **diagnóstico automático**, não execução de negociações.
As capacidades são observar, calcular, validar, explicar e registrar eventos.
Uma melhoria de código segue incidente → reprodução sintética → candidate →
testes → auditoria independente → promoção autorizada; não há autoatualização
ou mecanismo de autoaprovação. A versão produtora de novos máximos MDD passa
a identificar este produto; registros anteriores não são reescritos.

### Personalize apenas o que aparece no gráfico

Em **Cockpit → Ajustes**, escolha separadamente quais das seis métricas
aparecem no bloco do gráfico, o canto e a densidade compacta ou normal. A
prévia reage aos cliques; **Aplicar** confirma, **Cancelar** descarta o rascunho
e **Restaurar padrão** volta às seis métricas visíveis. Mesmo com todas
ocultas, o botão **Genetrix** continua acessível. A cor e o tamanho da fonte
continuam nas **Entradas** do indicador.

Essa escolha pertence ao **gráfico atual**, em configuração visual versionada
separada de USC, MDD, Gênese, F e Raiz N. Ocultar uma linha não pausa a leitura,
o cálculo das outras métricas ou a gravação do máximo observado. Se a
configuração visual estiver inválida, o Cockpit deve avisar e preservar os
registros financeiros; não trate dados ausentes como zero. Dois gráficos podem
ter aparências diferentes.

Para tentar reutilizar a aparência em outro gráfico, salve **manualmente** um
modelo do MT5 depois de aplicar a escolha, e confira o resultado ao reabri-lo.
O indicador não salva nem sobrescreve modelos automaticamente. A restauração
exata desta versão pelo template depende de teste nativo isolado; até existir
esse recibo, não a considere uma capacidade comprovada.

### Consulte o máximo observado sob demanda

1. Com a mesma instalação do MT5 e a conta cuja observação deseja consultar,
   abra **Navegador → Scripts → JPWealth** e execute
   `JPW_Alavancagem_Consultar_MDD` em um gráfico. Mantenha **Algo Trading
   desmarcado**. O símbolo do gráfico não limita a consulta: o registro é da
   conta inteira.
2. Leia a caixa exibida pelo MT5. Quando houver um registro válido, ela mostra
   o **máximo observado de DD/saldo**, o início da observação, o instante da
   amostra vencedora em **UTC do relógio do computador**, e o saldo e equity
   dessa amostra na moeda da conta. Feche a caixa após ler; o script termina.
3. Se aparecer ausência de registro, lock ocupado, registro inválido ou
   incompatível, ou identidade da conta indisponível, nenhum valor é exibido.
   Confira a instalação e a conta; para lock ocupado, tente novamente depois.
   Não interprete a ausência como máximo zero.

O script **somente lê** o registro desta instalação e da conta atual. Ele não
recalcula DD, não grava o registro ou perfil, não envia ordens e não altera as
seis linhas do indicador. O **Cockpit** mostra DD/saldo atual ou estimado e o
registro MDD quando legível; a caixa do script também mostra o maior valor **observado e registrado** em amostras atuais
válidas. O registro guarda a amostra vencedora, não uma série temporal. A
consulta não recupera períodos em que o indicador esteve desligado e não
calcula MDD pico-a-vale nem DD operacional de ciclo do Estatuto.

**Privacidade local:** o próprio MT5 também copia o texto da janela para a aba
**Experts** e seus arquivos locais de log. Isso inclui o máximo, saldo e equity
da amostra exibida. O script não envia esses dados ao site; examine os logs
antes de compartilhá-los com terceiros. Fechar a janela ou limpar a aba não
apaga necessariamente o arquivo de log do MT5.

### Aparência, atualização e remoção

O padrão é **cinza #767676**, fonte 8 e seis leituras no bloco com fundo de
contraste, colocado abaixo do nome nativo do instrumento. O bloco mede as
linhas conforme o espaço e a escala disponíveis; num gráfico estreito mantém
nome, valor e estado completos, ou apenas o acesso ao cockpit se não couberem. Use **Cockpit → Ajustes** para
escolher visibilidade, canto e densidade. Para cor e fonte, use **Ctrl+I →
JPW_Alavancagem_Atual → Propriedades → Entradas**. Gráficos e templates
antigos podem conservar entradas anteriores; **Reset / Redefinir** recupera
os padrões dessas Entradas, não apaga os registros financeiros locais.

A largura do bloco depende do tamanho do gráfico, da fonte e da preferência
visual, não do número que acabou de atualizar. Se uma leitura excepcionalmente
longa não couber, a linha oferece acesso ao Cockpit sem cortar o valor;
redimensionar o gráfico pode mudar a geometria normalmente.

Para atualizar: remova o indicador do gráfico, preserve uma cópia identificada
da versão anterior e substitua somente os arquivos desta ferramenta. Compile
os fontes, confira o relatório, atualize o Navegador e execute os testes da
nova versão antes de anexá-la. Não transfira o PASS da versão anterior.

Para retirar o painel, use **Ctrl+I → JPW_Alavancagem_Atual → Excluir**. Isso
não fecha posições nem altera ordens ou stops. Perfis USC, MDD, referência e
cenários Raiz N e snapshots do observador permanecem na pasta técnica. Uma desinstalação completa pode
remover somente os arquivos identificados desta ferramenta, preservando os
demais programas; preserve o registro se quiser manter o histórico observado.

O pacote de fontes inclui `AGENTS.md`, um guia técnico para IAs e revisores
que explica responsabilidades, atualização e auditoria do indicador. **Não
copie esse arquivo para a pasta MQL5**: ele acompanha os fontes e não é um
programa do MT5, uma autorização operacional ou substituto dos controles do
projeto.

## JPW NoCuda Channels — continue desenhando com o Fibonacci

`JPW_NoCuda_Channels` é um **segundo indicador**. Anexe-o em **Navegador →
Indicadores → JPWealth**, junto ao Cockpit ou sozinho. O botão **NoCuda** abre
as áreas **Canal · Agora · Projeção · Registro · Aparência**. O desenho não
precisa do EA observador e não usa posições, saldo ou a referência Gênese.

**Limite desta entrega:** importar e salvar os parâmetros não demonstra que o
resolvedor reproduz todos os detalhes geométricos do MT5. O estado
**UNVERIFIED_NATIVE** mantém as medidas do canal importado em **N/A**,
inclusive linhas próximas, distância e projeção diária. O laboratório deve
comparar os mesmos bytes e o canal nativo antes de liberar essas leituras.
Nenhum sucesso sintético ou captura antiga remove esse bloqueio.

### Caminho principal: Fibonacci acompanhado

1. **Desenhe no MT5 como já faz.** Use o Canal de Fibonacci nativo do símbolo
   exato do gráfico, com seus três pontos, níveis, descrições e raios.
   Se quiser a malha habitual, configure os 65 níveis de −4 a +4, passo 0,125.
   O indicador lê a configuração existente; não desloca pontos nem reescreve
   os níveis do objeto.
2. **Abra NoCuda e selecione o canal de origem.** Confira nome, símbolo,
   período de referência, três horários/preços e lista de níveis antes da
   primeira confirmação. A importação não aplica o ajuste ao Close do modo
   manual e não trata rótulos como números geométricos.
3. **Confirme o acompanhamento.** A primeira captura válida é gravada como
   revisão. Depois, ajustes manuais estáveis da origem podem criar novos
   checkpoints. Durante o arraste há prévia; movimento incompleto, conflito
   de geração ou falha de gravação não substituem a última revisão íntegra.
   Ticks, zoom, rolagem e navegação não criam revisões.
4. **Edite a origem no período de referência.** A visualização em outro
   período não redefine o estudo. Se o objeto for editado nesse outro
   período, a sincronização é suspensa: volte ao período de referência para
   conferir o ajuste. Não se atribui silenciosamente outro sentido às âncoras.
5. **Conserve ou remova a origem conscientemente.** Ocultar ou excluir o
   Fibonacci original não apaga a última captura íntegra já salva. Ao perder
   a origem, o estudo deixa de acompanhá-la; um rascunho incompleto não vira
   versão final. Renomear, duplicar ou recriar um objeto exige conferir o
   vínculo, pois um nome coincidente não prova que seja a mesma origem.

O objetivo é preservar preços nos mesmos instantes ao trocar o período da
tela, usando a sequência de barras congelada no período de referência.
Lacunas podem produzir segmentos com inclinação visual diferente; isso não
é uma autorização para mover os preços confirmados. Uma alteração do
histórico recebe aviso, sem reescrever âncoras ou revisões. **A prova dessa
preservação no MT5 permanece pendente.** Raios e descrições originais são
registrados; não autorizam inventar candles futuros.

### Nível, rótulo e linhas próximas

O **nível numérico** e a **descrição visível** são campos distintos. Ambos são
preservados como vieram do Fibonacci. Na convenção informada pelo proprietário:

| Descrição da linha | Nível geométrico |
|---|---|
| 1 | −1 |
| 3 | −0,75 |
| 5 | −0,50 |
| 9 | 0 |
| 17 | +1 |

Essa correspondência não limita o canal às linhas 1–17. Todos os níveis
importados permanecem consultáveis, inclusive as projeções até −4/+4 e suas
descrições originais. Nomes repetidos ou vazios não tornam duas linhas iguais:
a seleção também identifica índice e nível.

**Agora** concentra a leitura na linha mais próxima e nas adjacentes acima e
abaixo da cotação, quando a geometria estiver validada. A cotação usada, seu
horário e qualidade devem aparecer junto da leitura; não se deduz o preço
pelo local do cursor. A consulta de outra linha é manual. Contatos com a linha
são **observações declaradas pelo usuário**, sem confirmação automática de
suporte/resistência, eficácia ou terceiro contato independente. No estado
UNVERIFIED_NATIVE, uma anotação manual não valida a geometria nem libera
valores calculados.

### Janela, aparência e consulta do registro

A janela inicial usa aproximadamente **90% da área do gráfico**. Em
**Aparência**, os modos **Compacta**, **Ampla** e **Maximizada** reorganizam o
espaço; também é possível mover pelo cabeçalho e redimensionar pelo canto
inferior. O conteúdo usa fonte própria, padrão **11**, configurável de 9 a 24.
Cabeçalho, abas, cartões e ações de fechamento ficam separados; o estado do
estudo e os motivos de N/A não são confundidos com seus valores.

Campos em edição e rascunhos devem sobreviver às atualizações e ao
redimensionamento. Preferências visuais ficam num objeto do próprio gráfico;
não alteram fórmulas nem revisões. O ciclo **personalizar → salvar template →
reabrir** só poderá ser anunciado como funcional após prova no MT5 isolado.
O teclado e os cliques do Cockpit fora da interação NoCuda permanecem sob seu
próprio controle. Fonte, DPI, arraste da janela e coexistência estão sujeitos
à verificação nativa desta revisão.

**Registro** separa a origem, as capturas confirmadas e as observações manuais.
Restaurar uma versão anterior cria uma **nova revisão** e pausa o acompanhamento;
não apaga versões nem move silenciosamente a cabeça para trás.
Os estudos importados usam banco próprio em
`MQL5/Files/JPWealth/NoCuda/Fibonacci/`, separado dos estudos manuais e de todos
os registros financeiros. Uma revisão confirmada não é sobrescrita. Duas
instâncias com gerações distintas recebem conflito; arquivo corrompido ou
incompatível não autoriza reinicialização silenciosa.

### Modo manual legado: A → B → C

Os estudos anteriores continuam disponíveis, sem conversão automática para
Fibonacci. Neste modo, H1 é a fonte inicial; M15, H4 ou D1 exigem seleção
explícita. **Novo canal** inicia A → B → C e recolhe o painel durante a
marcação. Cada clique horizontal seleciona uma barra encerrada: a âncora usa
seu **Close**, colocado no horário de abertura; a altura do clique não define
o preço. Arrastar também ajusta ao Close e mantém o rascunho sem gravar.

A/B pertencem ao nível 0; C determina a largura assinada até o nível 1; o meio
é 0,5. Depois de C, confira as âncoras e preencha a justificativa antes de
**Confirmar versão**. **Editar versão** cria rascunho; **Cancelar rascunho**
restaura a revisão anterior. Somente a confirmação explícita grava esse modo.
C não constitui automaticamente terceiro contato independente. O modo manual
mantém sua malha de 65 níveis e suas revisões sem reinterpretar os números.
A antiga `Nocuda_Tool.mq5` também permanece sem migração automática.

### Projeção diária: onde a linha estará no dia escolhido

Uma linha NoCuda é uma **referência geométrica inclinada** usada na análise de
suporte e resistência. A consulta mostra onde essa referência estará **se o
canal for mantido**; não prevê a cotação. A faixa pertence à linha e não tem
interpretação probabilística.

No modo manual, abra **Medidas**, escolha a linha e use **Consultar dia** com
uma data **AAAA.MM.DD**. No modo Fibonacci, a área **Projeção** conserva o
bloqueio quantitativo enquanto a geometria estiver UNVERIFIED_NATIVE.
Todos os horários abaixo são do **servidor do MT5**:

| Leitura | O que representa |
|---|---|
| Início · 00h | Preço geométrico da linha à meia-noite. |
| Meio do dia · 12h | Preço geométrico da linha ao meio-dia. |
| Fim · 24h | Preço geométrico à meia-noite do dia seguinte. |
| Média dos extremos | `(preço de 00h + preço de 24h) ÷ 2`; não é média das cotações nem integral temporal. |
| Faixa do dia | Menor e maior preço da linha entre início e fim. |

**12h e média dos extremos podem diferir** quando existem lacunas ou sessões
parciais. Usa-se a coordenada fracionária entre aberturas da fonte, com
precisão plena antes da formatação. Para histórico, é necessária cobertura
real e coerente dos instantes; falta, divergência ou ausência do delimitador
produz **N/A**. USC não aplica fator 100 a preços ou distâncias.

O resolvedor futuro aceita **H1 e H4**, até **30 dias civis** adiante. Cada
período é confrontado com suas próprias aberturas reais nos últimos **14 dias
civis encerrados**. H1 usa horas cheias; H4 usa **00/04/08/12/16/20** do
servidor com sobreposição de sessão. Não se divide uma contagem H1 por quatro.
Qualquer incompatibilidade da grade recusa o futuro. Até **sete dias extras**
servem apenas para encontrar o delimitador de 24h. Outros períodos mantêm
consulta histórica, sem projeção futura automática.

Toda saída futura é **Estimated**: sessões semanais não confirmam feriados ou
mudanças futuras de horário de verão. Dia sem sessão fica **Sem sessão**, sem
faixa; pontos de um dia parcial fora da sessão são identificados. Uma nova
consulta pode mudar se a grade disponível mudar: o valor anterior não era um
preço futuro confirmado. A consulta identifica instante, fonte e qualidade;
cotação recente não valida geometria projetada. Consultas e marcas não criam
revisões do canal nem mudam o calendário da Raiz N.

O comando legado **Mostrar referências** só apresenta 00/12/24 quando a
conversão tempo/preço ↔ pixels for coerente e legível. Caso contrário, mantém
a tabela e explica a ausência das marcas. Medições em pips exigem tamanho
explicitamente configurado para o símbolo exato.

Este indicador não detecta canais automaticamente, envia sinais, define stop,
lote ou entrada, nem negocia. A publicação destes fontes não prova paridade
Fibonacci, restauração por template ou execução nativa. Compilação, interação,
medidas importadas e visualização dos mesmos bytes permanecem **NOT_RUN** até
os recibos de uma instalação MT5 isolada. Não é distribuído EX5 desta revisão.

## Entenda a fórmula e a cobertura

Exemplo inteiramente sintético: nocional bruto de US$ 3.600 dividido por
equity de US$ 1.000 resulta em **3,60x**. Não é leitura da conta nem previsão
de perda para um movimento de mercado.

Para saldo `B`, equity `E` e lucro flutuante informado pela conta `P`, o painel
calcula **Flutuante / saldo = 100 × P / B** e **DD / saldo = 100 ×
max(0, B − E) / B**. O saldo deve ser finito e positivo. O flutuante exige P
finito; o DD exige E finito, mas E pode ser zero ou negativo. A propriedade
`ACCOUNT_CREDIT` é lida como contexto da amostra, sem ser somada ou subtraída
nessas fórmulas. Por isso, o DD/saldo pode diferir da perda flutuante: crédito
e outros componentes da equity afetam E. A ferramenta não redefine P como E−B.
Em USC, B, E e P permanecem nas unidades originais da conta e o fator cent
se cancela nos quocientes; a normalização do nocional para a alavancagem
continua sendo um cálculo separado.

O **máximo observado de DD/saldo** começa na primeira amostra válida e atual
vista pelo indicador, inclusive quando o DD é zero. Somente uma amostra atual,
consistente e estritamente maior atualiza o registro; `Estimated` e `N/A` não
o atualizam. Ele não aparece no bloco permanente do gráfico; consulte-o em
Cockpit ou pelo script sob demanda. O arquivo local fica em
`MQL5/Files/JPWealth/Alavancagem/`, separado do perfil USC e vinculado por
chave opaca a servidor, login, moeda, escala e nome da métrica. Guarda início
da observação, máximo confirmado, saldo/equity da amostra vencedora, versão e
horário **observado pelo indicador no relógio do computador**. Não registra
operações nem credenciais. Duas instâncias usam lock sem espera, releitura e
dois slots recuperáveis; se o lock estiver ocupado ou a gravação for recusada,
a persistência fica pendente e o diagnóstico não afirma que ela foi concluída.
Arquivos incompatíveis ou ambos inválidos impedem nova escrita até análise.

Esse máximo cobre apenas os períodos em que o indicador esteve ativo e obteve
amostras atuais válidas. Não reconstrói DD de períodos desligados, não é o MDD
pico-a-vale de uma série histórica e não é o DD operacional de ciclo do
Estatuto, que usa outra base e tratamento de fluxos. O registro permanece na
pasta de dados daquela instalação do MT5; copiar o pacote de fontes, abrir o
site ou usar outra instalação não o transporta. O site não lê nem distribui
esse arquivo.

Forex fiduciário em `FOREX`/`FOREX_NO_LEVERAGE` usa lotes × contrato em
moeda-base, convertido à moeda de comparação. XAU nos modos Forex/CFD e CFDs
lineares em `CFD`/`CFDLEVERAGE` com subjacente identificado por `SYMBOL_BASIS`
ou `SYMBOL_ISIN` usam lotes × unidades contratuais × `(Bid+Ask)/2`, depois a
conversão da moeda de cotação. Em USC, contrato verificado e equity são
comparados em USD. O contrato vem dos metadados; não há um tamanho universal
de lote. Uma posição não suportada invalida o total. `CFDINDEX`, futuros,
opções, títulos e contratos inversos permanecem fora da cobertura.

Conversões usam moedas fiduciárias, por rota direta, inversa ou até duas
etapas. Rotas recentes têm prioridade; em igualdade de qualidade, a rota
válida escolhida é mantida e empates são estáveis. Metais, criptoativos e
símbolos personalizados locais não servem como intermediários cambiais.

O indicador pode selecionar pares fora da Observação do Mercado (Market Watch)
para obter cotações. A seleção pode permanecer depois da remoção; revise a
lista manualmente se quiser restaurar a organização anterior.

## Ajuda por sintoma

| Sintoma | O que conferir |
|---|---|
| Não aparece no Navegador | Pasta de dados da instância aberta, destino correto, geração do .ex5 e Atualizar no Navegador. |
| Include não encontrado | Confira os arquivos .mqh em MQL5/Include/JPWealth; compile o .mq5 principal. |
| Genesis SL: N/A | Confirme conexão, ticket da referência e SL vigente. Se a seleção automática for ambígua, informe um ticket positivo nas Entradas. Registro corrompido ou incompatível bloqueia reinferência. Em netting OTC, o rótulo é Position SL. |
| Stop risk: N/A · Check Observer | Não há confirmação recente do EA para esta instalação e conta. Confira em Navegador → Expert Advisors → JPWealth se `JPW_Alavancagem_Observer` da mesma versão está anexado a um gráfico aberto deste terminal; consulte Experts. O indicador não ativa o EA. Mesmo com todos os SLs preenchidos, ainda é necessária uma amostra completa do EA. |
| EA presente, Stop risk: N/A | Abra Cockpit → Stops/Sistema para distinguir primeira amostra pendente de falha de publicação. Confira Experts, SLs de posições e pendentes, composição estável e suporte do tipo de ordem. Uma parcela inválida impede o total; netting não fornece total auditável por operação. Amostra antiga fica só como `LAST · NOT ACTIVE` no menu. |
| Stops: “Amplie para ler a tabela” | A versão anterior usa um limite de altura que pode bloquear a tabela antes de consultar posições. Confira o EX5 instalado; até atualizar, reduzir `InpCockpitFontSize` nas Entradas pode liberar a visualização. A versão 1.10.1 pagina linhas compactas e mantém os detalhes acessíveis. |
| Raiz N 1W/2W: N/A | Confira símbolo exato, Bid/Ask, tick novo após inicialização, ATR(55) H4, sessões/calendário e o estado da preferência F. Falta de cobertura ou conflito não é zero. Registro F corrompido, incompatível ou inacessível exige tratamento explícito; não recebe padrão silencioso. Um calendário recorrente válido continua Estimated. |
| Probabilidade de não toque ausente | O Cockpit só mostra o cálculo teórico para F válido. Não use a porcentagem como probabilidade de um SL existente ou como validação observada da corretora. N/F legado não altera 1W/2W. |
| Observador sem captura | Confira se o EA opcional está realmente anexado, a conta/instalação e Experts. Histórico tardio só pode gerar Reconstructed quando completo; falha de evento, ATR ou banco não é captura concluída. |
| Linhas encavaladas ou Cockpit antigo | Confira a versão dos fontes compilados e do EX5 anexado. O ZIP de fontes não instala EX5. Recompile a revisão identificada e anexe novamente em MT5 isolado; uma captura de tela não prova os bytes instalados. |
| Preferência visual inválida | Confira Cockpit → Ajustes. O aviso trata da apresentação do gráfico; não redefine os registros financeiros. Mesmo sem linhas visíveis, o botão Genetrix deve permanecer acessível. |
| NoCuda: Projeção diária N/A | Confira a data, fonte H1/H4 para futuro, limite de 30 dias, cobertura histórica e grade semanal. Em Fibonacci importado, UNVERIFIED_NATIVE mantém medidas N/A até a prova nativa. O motivo identifica o dado faltante; nenhuma barra futura é inventada. |
| NoCuda: referências não aparecem | Leia a tabela no menu. Datas fora da área, conversão imprecisa ou marcas sobrepostas impedem só a apresentação das referências. |
| Script “removed” | É normal após terminar; confira PASS/FAIL ou confirmação USC em Experts. |
| Verifique os contratos USC | Execute o script de verificação para todos os instrumentos necessários; não force escala no perfil. |
| Estimated, sem conexão, contexto ou dados recentes | Na alavancagem, a dica mostra o motivo e a cotação mais antiga no horário do servidor. Nas linhas sobre saldo, a dica mostra o horário UTC observado pelo indicador no relógio do computador e eventual crédito não confirmado. Não é leitura atual; N/A se faltarem dados necessários. |
| Sem cotação para conversão | Falta uma rota cambial com preços utilizáveis; confira símbolos e sincronização no terminal. |
| Contrato não suportado | Confirme modo, base, moeda de cotação, tamanho e subjacente informados pelo servidor. |
| Equity inválido | Alavancagem exige equity finito e positivo. DD/saldo ainda pode ser calculado com equity zero ou negativo, se saldo e leitura forem válidos. |
| Registro do máximo não atualizado | Uma amostra Estimated, inconsistente, menor ou igual ao máximo não o altera. Lock ocupado ou gravação recusada adia a persistência; confira o diagnóstico. |
| Cor ou fonte antiga | Propriedades → Entradas → Reset / Redefinir; templates podem conservar Entradas anteriores. Canto, densidade e visibilidade ficam em Cockpit → Ajustes. |
| Consulta sem máximo exibido | Confira a conta e a pasta de dados desta instalação. O script distingue ausência, lock ocupado, registro inválido/incompatível e conta indisponível; não trata ausência como zero. |
| Preparar mensagem bloqueado | Confira o motivo do catálogo ou da prévia: SL, alavancagem, Raiz N 1W/2W e flutuante devem ser válidos. TP ausente é permitido e aparece como Sem TP. O EA não é necessário para esse catálogo. |
| A prévia da mensagem foi invalidada | Releia o catálogo e confira novamente a composição. Mudança de conta, símbolo, volume, SL ou TP não conserva o texto anterior como leitura atual. |
| Ctrl+C não copia a mensagem | Não há confirmação nativa desta interação nesta revisão. Use a ação explícita TXT local e o caminho informado pelo painel; confira a seleção/cópia em MT5 isolado antes de depender do clipboard. |

### Ambiente de teste isolado

Use uma cópia separada do MT5, com pasta de dados própria e sem conta real conectada, preparada somente para testes. Confira a pasta em Arquivo → Abrir pasta de dados. Trocar para uma conta demo na mesma instalação não separa arquivos e configurações da sessão de uso. Esta distribuição não cria esse ambiente automaticamente.

A verificação de unidade USC pode usar as últimas cotações estruturalmente válidas,
inclusive com o mercado parado. Os quatro cálculos hipotéticos nativos precisam
concordar com uma única escala e com os valores de tick; se o MT5 recusar o
cálculo, o perfil não é confirmado. Isso não transforma uma cotação antiga em
Atual. A data técnica do perfil vem do relógio do computador; a data exibida
para cotações no painel continua sendo a do servidor.
