# JPW Alavancagem Atual — fontes MT5 v1.10.1

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
  `JPW_Alavancagem_Atual` apenas informa; não envia ordens.
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
validam automaticamente os fontes da versão 1.10.1. Não há `.ex5` desta revisão
para distribuição sem compilação nativa comprovada dos fontes exatos.

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
   `JPW_Alavancagem_Diagnostics_Tests.mq5`, na pasta Scripts/JPWealth.
   Compile também `MQL5/Experts/JPWealth/JPW_Alavancagem_Observer.mq5`
   se for usar a captura opcional de execuções. Compilar não anexa o EA.

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
   abrir seu cartão no **Cockpit**, ou use o botão **Cockpit** para abrir o
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

O botão **Cockpit** abre uma janela **centralizada e temporária**. A primeira
visão reúne seis cartões: Leverage, Floating P/L, Genesis SL, as duas
distâncias Raiz N e Stop risk. Cada cartão mostra valor, `Current`, `Estimated` ou
`N/A` e um motivo curto. Clique num cartão, ou na respectiva linha do gráfico,
para examinar fórmula, insumos, origem, horário, limites e motivo do estado.
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

Em **Stops**, a mensagem de amostra ausente ou inválida aparece antes da
tabela. Quando há linhas consultáveis, posições e pendentes usam páginas
compactas; selecione uma linha para ver o detalhe completo, sem cortar valor
nominal ou percentual. A orientação “Amplie para ler a tabela” não deve
substituir uma página que cabe na janela. Se a fonte antiga ainda impedir a
leitura, confira a versão do EX5 anexado e, como contorno temporário, reduza
`InpCockpitFontSize` em **Ctrl+I → JPW_Alavancagem_Atual → Entradas**.

Em **F 1,5/1,8**, selecione uma opção; só **Aplicar** salva essa preferência e
**Cancelar** mantém o F anterior. **N/F legado** e os cenários antigos seguem
em área própria e não governam os horizontes 1W/2W. Fechar, navegar ou
redimensionar o Cockpit não altera posições, ordens, stops nem os registros
financeiros.

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
ocultas, o botão **Cockpit** continua acessível. A cor e o tamanho da fonte
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
| Preferência visual inválida | Confira Cockpit → Ajustes. O aviso trata da apresentação do gráfico; não redefine os registros financeiros. Mesmo sem linhas visíveis, o botão Cockpit deve permanecer acessível. |
| Script “removed” | É normal após terminar; confira PASS/FAIL ou confirmação USC em Experts. |
| Verifique os contratos USC | Execute o script de verificação para todos os instrumentos necessários; não force escala no perfil. |
| Estimated, sem conexão, contexto ou dados recentes | Na alavancagem, a dica mostra o motivo e a cotação mais antiga no horário do servidor. Nas linhas sobre saldo, a dica mostra o horário UTC observado pelo indicador no relógio do computador e eventual crédito não confirmado. Não é leitura atual; N/A se faltarem dados necessários. |
| Sem cotação para conversão | Falta uma rota cambial com preços utilizáveis; confira símbolos e sincronização no terminal. |
| Contrato não suportado | Confirme modo, base, moeda de cotação, tamanho e subjacente informados pelo servidor. |
| Equity inválido | Alavancagem exige equity finito e positivo. DD/saldo ainda pode ser calculado com equity zero ou negativo, se saldo e leitura forem válidos. |
| Registro do máximo não atualizado | Uma amostra Estimated, inconsistente, menor ou igual ao máximo não o altera. Lock ocupado ou gravação recusada adia a persistência; confira o diagnóstico. |
| Cor ou fonte antiga | Propriedades → Entradas → Reset / Redefinir; templates podem conservar Entradas anteriores. Canto, densidade e visibilidade ficam em Cockpit → Ajustes. |
| Consulta sem máximo exibido | Confira a conta e a pasta de dados desta instalação. O script distingue ausência, lock ocupado, registro inválido/incompatível e conta indisponível; não trata ausência como zero. |

### Ambiente de teste isolado

Use uma cópia separada do MT5, com pasta de dados própria e sem conta real conectada, preparada somente para testes. Confira a pasta em Arquivo → Abrir pasta de dados. Trocar para uma conta demo na mesma instalação não separa arquivos e configurações da sessão de uso. Esta distribuição não cria esse ambiente automaticamente.

A verificação de unidade USC pode usar as últimas cotações estruturalmente válidas,
inclusive com o mercado parado. Os quatro cálculos hipotéticos nativos precisam
concordar com uma única escala e com os valores de tick; se o MT5 recusar o
cálculo, o perfil não é confirmado. Isso não transforma uma cotação antiga em
Atual. A data técnica do perfil vem do relógio do computador; a data exibida
para cotações no painel continua sendo a do servidor.
