# JPW Alavancagem Atual — guia local para IAs e revisores

Este arquivo acompanha o ZIP de **fontes** da versão 1.10.1. Ele descreve o
produto; não é um programa do MT5 e **não deve ser copiado para `MQL5`**.
Aplica-se somente a `mt5/jpw-alavancagem-atual/`. Subordina-se às instruções do
repositório, ao Estatuto JP Wealth e ao Harness canônico externo. Não concede
autorização para alterar código, negociar, instalar, publicar, ativar política,
homologar P-21 ou reclassificar falhas. Resolva conflitos pela autoridade
superior e registre a divergência.

O desenvolvimento é **integralmente orientado pela estrutura JP Wealth**:
Estatuto, Anexo Paramétrico, autoridade humana e Harness canônico externo.
Este guia é um mapa operacional para IAs, não uma fonte normativa nem um
certificado de conformidade. O MT5 não prova a tese, a flag estatutária da
Gênese, a elegibilidade de Defesas ou o saldo inicial de referência apenas
pela ordem cronológica das posições.

## Mapa do produto

| Componente | Responsabilidade |
| --- | --- |
| `MQL5/Indicators/JPWealth/JPW_Alavancagem_Atual.mq5` | Ciclo de vida e encaminhamento de eventos; delega coordenação e apresentação. Não envia ordens. |
| `MQL5/Include/JPWealth/JPW_Alavancagem_Core.mqh` | Matemática pura de nocional, conversões e métricas de saldo/equity. |
| `MQL5/Include/JPWealth/JPW_Alavancagem_Terminal.mqh` | Adapta leituras do terminal, posições, símbolos, cotações e relógios. |
| `MQL5/Include/JPWealth/JPW_Alavancagem_Panel.mqh` | Geometria do bloco e da janela em pixels. |
| `MQL5/Include/JPWealth/JPW_Alavancagem_Cockpit.mqh` | Tipos de qualidade e codec da preferência **somente visual**. |
| `MQL5/Include/JPWealth/JPW_Alavancagem_Profile.mqh` | Verificação e leitura do perfil técnico USC. |
| `MQL5/Include/JPWealth/JPW_Alavancagem_MDD.mqh` | Máximo de DD sobre saldo **observado**, com registro próprio. |
| `MQL5/Include/JPWealth/JPW_Alavancagem_Genesis_*.mqh` | Seleção, cálculo e persistência da referência inferida ou escolhida. |
| `MQL5/Include/JPWealth/JPW_Alavancagem_RaizN_*.mqh` | Cenários, ATR, horizontes, F, cálculo e snapshots do observador; cada registro mantém seu contrato. |
| `MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Core.mqh` | Tipos e soma financeira de risco de stops, com recusa de total parcial. |
| `MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Terminal.mqh` | Inventário integral de posições e pendentes, identidade e digest da composição. |
| `MQL5/Include/JPWealth/JPW_Alavancagem_StopRisk_Store.mqh` | SQLite separado, geração, checksum, publicador e leitura somente para o indicador. |
| `MQL5/Include/JPWealth/JPW_Alavancagem_Observer_Presence.mqh` | Sinal técnico temporário, versionado e opaco da presença/estado do EA; nunca valida sozinho o valor de Stop risk. |
| `MQL5/Experts/JPWealth/JPW_Alavancagem_Observer.mq5` | Observa execuções e publica amostras de risco dos stops. Não negocia. A última captura não prova que o EA está ativo agora. |
| `MQL5/Scripts/JPWealth/` | Testes sintéticos, inclusive StopRisk, verificação USC e consulta sob demanda do MDD. |

O site em `index.html` explica e distribui os arquivos. Ele não calcula a
alavancagem e não lê posições, credenciais, perfis ou registros de conta. O
manifesto em `downloads/jpw-alavancagem-atual/manifest.json` lista cada fonte,
hash, download e estado de validação. `tools/build_leverage_package.py` cria o
ZIP determinístico; `tools/rebuild_monolith.py` regenera o HTML portátil e o
cache offline. `.ex5` só pode entrar no pacote com compilação nativa e hashes
ligados aos fontes exatos.

## Invariantes de cálculo e unidades

- **Leverage** = nocional **bruto de todas as posições abertas** na moeda da
  conta ÷ equity atual informado pelo terminal. Uma posição sem contrato,
  preço ou conversão verificável invalida o total; ausência de posições só
  produz `0,00x` quando confirmada. Forex, XAU e CFDs lineares suportados
  seguem suas unidades contratuais. Não transformar margem ou alavancagem
  contratada nesta métrica. Essa razão exibida é **informativa**: não calcula
  nem atesta a alavancagem estatutária do Art. 4.5 §8, cuja base é o menor
  entre Saldo Inicial de Referência e equity corrente.
- **USC**: `100 USC = 1 USD`, mas a escala de contrato é confirmada por
  instrumento no perfil técnico; jamais dividir apenas o equity ou inferir
  conta cent pelo sufixo do símbolo/corretora. `100 × P/B` e
  `100 × max(0, B−E)/B` usam B, E e P na mesma moeda original da conta; a
  escala USC se cancela.
- **Floating P/L** = `100 × ACCOUNT_PROFIT / ACCOUNT_BALANCE`.
  **DD / saldo** = `100 × max(0, balance−equity) / balance`. Crédito é
  contexto, não parcela adicionada. O MDD é o maior DD válido **observado
  pelo indicador**, não MDD pico-a-vale nem reconstrução de períodos ausentes.
- **Genesis SL**: para compra, a cotação relevante é Bid e a distância é
  `Bid−SL`; para venda, Ask e `SL−Ask`. O percentual divide pela cotação
  relevante. A referência automática é inferida sob condições restritas;
  não a apresentar como Gênese certificada. Em netting, rotular SL da posição
  agregada. Nível alcançado/ultrapassado não afirma execução do stop.
- **Raiz N diagnóstica 1W/2W**: `Dpreço = ATR(55,H4) × √N × F` e
  `D% = 100 × Dpreço / P0`, com P0 igual ao ponto médio do mesmo tick. N vem
  dos fechamentos H4 esperados em janelas móveis de 7/14 dias civis do
  servidor. F=1,5 é o padrão diagnóstico, F=1,8 uma opção; P-21 canônico
  permanece `PENDING`. Calendário projetado continua `Estimated` mesmo com
  F escolhido. A referência browniana de primeiro não toque
  `2Φ(√(8/π)×F)−1` descreve barreira hipotética sob premissas ideais;
  não é probabilidade de um SL real, chance de lucro ou cobertura empírica.
- **Stop risk** (Estatuto V11, art. 8.4, §§ 1, 2, 9 e 16): em **hedging**,
  por posição aberta use `max(0, −OrderCalcProfit(tipo, símbolo exato,
  volume remanescente, preço de execução, SL vigente))`. Some a reserva
  de cada pendente ampliadora atribuída ao mesmo símbolo e direção, com
  volume ainda pendente, preço planejado e SL. Não presuma exclusividade
  entre pendentes. Arredonde somente na apresentação. `OrderCalcProfit`
  pertence ao EA, nunca ao indicador. O resultado e `ACCOUNT_BALANCE`
  permanecem na **mesma moeda da conta**, inclusive USC; o percentual
  `100 × total / ACCOUNT_BALANCE` é **informativo**. Limites normativos
  usam o Saldo Inicial de Referência e componentes adicionais do Risco
  Comprometido. Preço atual → SL, com Bid para compra e Ask para venda,
  é outra medida, apenas para posições e exibida separadamente.

Para Stop risk, selecione a operação pelo símbolo exato e direção da
referência Gênese guardada; sem ela, só infira quando existir um único
grupo inequívoco. O Estatuto V11 art. 4.2 requer a **mesma tese**, que o
terminal não certifica. O art. 4.3 requer condições adicionais para a
Gênese. Antiguidade serve para ordenar a tabela, sem provar papéis: marque
Gênese/Defesas como inferidas ou selecionadas. Gênese encerrada permanece
encerrada, sem promover sucessora. Defesas 4+ continuam paginadas; P-07 e
P-19 do Anexo Paramétrico seguem pendentes e três defesas não são limite.
Outro instrumento ou direção não entra na soma e gera aviso. Em **netting**,
a posição agregada pode aparecer como contexto, mas a decomposição de risco
por ordem e o total da operação ficam `N/A`.

Uma posição ou pendente atribuída sem SL, tipo não suportado (inclusive
stop-limit), conversão recusada, identidade/composição instável ou saldo não
positivo torna o **consolidado `N/A`**. Subtotal somente em detalhe,
explicitamente incompleto. Zero requer universo inteiro confirmado vazio ou
parcelas válidas com risco matemático zero. O valor não inclui custos,
deslizamento, gaps ou perdas já realizadas; não é garantia de perda máxima.

As seis métricas têm validade independente. `Current` exige os dados atuais
que a métrica requer; `Estimated` indica cálculo completo sem atualidade
comprovada; `N/A` indica insumo ou consistência insuficiente. Estado de
cotação, ATR, calendário e registros locais devem ser apresentados
separadamente. Ocultar uma linha no cockpit não suspende coleta, qualidade ou
gravação do MDD. Nunca usar texto de mensagens em português para inferir o
estado: use os tipos do núcleo de apresentação.

Stop risk só é `Current` com conexão, evidência recente do EA publicador, geração
íntegra dentro do limite de 30 segundos, conta/saldo/composição conferidos
e revalidados e lease efêmera da **sessão atual** do MT5 vinculada ao mesmo
publicador e instante da amostra. `GetTickCount64` mede o tempo desde o boot
do sistema, não desde a abertura do terminal; sozinho não prova continuidade
após reinício. O EA desativa a amostra ativa quando falha ou encerra. Sem
essas provas, a linha mostra `N/A`; o último snapshot fica consultável em
**Stops** apenas como histórico. A API não expõe a idade de cada rota de
conversão interna de `OrderCalcProfit`: `Current` qualifica a amostra do EA,
não certifica preço executável de SL nem frescor de cada conversão.
O monitor da sexta linha roda em até cinco segundos e o ciclo completo das
demais leituras em até 30 segundos, mesmo quando a Entrada
`InpUpdateSeconds` solicita intervalo maior. O timer é uma frequência
solicitada, não garantia de despacho no prazo. Leitura antiga não conserva o
rótulo `Current` nem número antigo após falha de atualização.

## Fronteiras de persistência

Os registros de conta ficam sob `MQL5/Files/JPWealth/Alavancagem` e pertencem
à instalação local. Perfil USC, MDD, Gênese, cenários/configurações Raiz N,
preferência F, snapshots do observador e SQLite de Stop risk são contratos
distintos. Não os
misture, migre ou sobrescreva silenciosamente. Preserve locks, versões,
checksums, dois slots e semântica de recuperação onde já existem. Uma leitura
ocupada/corrompida/incompatível não deve virar zero nem PASS.

A preferência do cockpit é exclusivamente um objeto versionado do **gráfico**,
`JPW_COCKPIT_PREF_V2`: máscara de seis linhas, canto e densidade. O decoder
legado V1 preserva os cinco bits antigos: se todos estavam ocultos, mantém
todos ocultos; caso contrário, acrescenta a sexta linha por padrão. Não guarda
conta ou valores financeiros. Ausência significa seis linhas; configuração
inválida mostra aviso e conserva o objeto original até ação explícita. O
indicador não chama salvamento automático de template. O usuário pode salvar
um modelo manualmente, mas a restauração por template da versão exata só pode
ser anunciada após o ciclo nativo personalizar → salvar → reabrir.

## Alteração, testes e coerência

1. Identifique o candidate/fingerprint de base, preserve o snapshot, abra CHG
   conforme a classificação de risco e confirme que a worktree está correta.
   Uma captura do gráfico não identifica o EX5 instalado.
2. Delimite a mudança. Interface não altera fórmulas nem schemas financeiros.
   Troca de conta/símbolo invalida a amostra antes de exibir outro valor. O
   cockpit solicita uma leitura sob demanda de MDD e último snapshot; o
   coordenador a atende no timer e libera o lock antes de desenhar controles.
3. Rode os scripts de teste MQL5 que exercitam o **mesmo núcleo** de produção e
   os focais do host (`tools/leverage_cockpit_test.py`,
   `tools/leverage_panel_test.py`, `tools/leverage_details_event_test.py`,
   `tools/leverage_geometry_test.py`, `tools/leverage_stop_risk_test.py`,
   `tools/leverage_stop_ui_test.py`, `tools/leverage_page_test.py` e
   `tools/leverage_package_test.py`). O script MQL5
   `JPW_Alavancagem_StopRisk_Tests.mq5` usa somente dados sintéticos.
   Testes do host não provam compilação ou
   comportamento no MT5. Classifique falhas sem mascarar `PRODUCT_FAIL`.
4. Em MT5 **isolado**, compile fontes exatos no MetaEditor X64 Regular,
   execute testes sintéticos e inspecione cliques, cinco abas, tabela
   paginada, quatro cantos, gráficos estreitos, temas e DPI. Para Stop risk,
   com conta e diretório **sintéticos**, confira transação SQLite, dois EAs,
   heartbeat, EA parado, corrupção, mudança de posições/pendentes, USC e
   netting. Para preferência visual, prove o ciclo de template
   com recibos dos mesmos bytes. Sem ambiente, marque `NOT_RUN`; não publique
   `.ex5` fictício nem declare prontidão operacional.
5. Atualize README, página, manifesto e derivados pelos geradores oficiais.
   Compare `sourceFiles`, `sourceHashes`, ZIP extraído, hashes de downloads,
   versão e estados exibidos pelo site. Confirme que `AGENTS.md` está na raiz
   do ZIP, **fora de `MQL5/`**, e que nenhum dado de conta entrou no pacote.
   Execute focais, validação estrutural e `tools/quality_gate.py --tier full`
   sem alterar classificação ou trocar um fracasso por uma exceção genérica.
6. Congele os bytes e encaminhe revisão independente do produto e deste guia.
   Human Acceptance, commit, push, merge, instalação e publicação são etapas
   distintas, dependentes de autorização própria.

Rollback de produto restaura o snapshot anterior verificado e regenera os
derivados; não apaga registros de conta. **Para a revisão histórica 1.10.0**,
rollback deste guia restaura os bytes verificados de `AGENTS.md` da versão
1.9.0 e seu manifesto/ZIP a partir do
snapshot r15 em `outputs/jpw-cockpit-v190-20260929/final-r15/candidate/`;
o guia já existia, portanto não apague sua entrada. Regere os derivados pelos
geradores oficiais e confira hashes antes de alegar retorno à versão anterior.
Rollback apenas do guia, sem rollback do produto, exige novo manifesto/pacote
coerente com os fontes mantidos. Preserve os registros financeiros locais.
Consulte o CHG e a auditoria da revisão exata antes de qualquer alegação de
validação. Para a revisão **1.10.1**, use o rollback específico para r17 ao
fim deste guia; a instrução histórica r15 não se aplica.

## Engenharia da revisão 1.10.0

O sistema é orientado pela estrutura JP Wealth; isso não afirma implementação
integral do Estatuto ou do Método Nocuda. Capacidades atuais: observar,
calcular, validar, explicar e registrar diagnósticos. São excluídos negociação,
executor genérico de comandos, autoalteração de parâmetros, autoatualização de
código e autoaprovação. Um diagnóstico não concede uma autorização.

### Fronteiras de execução

O indicador principal mantém globals, ciclo de vida e encaminhamento de eventos.
`Coordinator.mqh` coordena leituras, validação, aceitação de amostras e efeitos
explícitos. `Presentation.mqh` desenha a partir do estado aceito; navegar,
redimensionar e desenhar não devem iniciar coleta financeira nem escrever
registros financeiros. O encaminhamento de eventos pode conferir somente a
identidade para invalidar um contexto trocado antes do desenho. `Actions.mqh` contém ações explícitas e rascunhos. Todos esses
nomes têm o prefixo `JPW_Alavancagem_` no pacote. Aplicar uma preferência é um
ato explícito, diferente de consultar ou cancelar.

`Samples.mqh` representa a evidência de cada métrica: ID de coleta, contexto
opaco, tipo/valor/unidade, qualidade, motivo, origem e horários. IDs avançam na
aceitação da coleta; o redesenho reutiliza o ID. Falha não conserva valor
anterior como atual; troca de conta/símbolo invalida antes de apresentar.
Métricas com cadências diferentes não fingem uma fotografia sincronizada.

`Version.mqh` separa produto, cálculo e build. A versão produtora de novas
amostras MDD usa a versão do produto; registros antigos nunca são reescritos.
O gerador oficial calcula `JPW_BUILD_ID` dos fontes MQL declarados, normalizando
somente o próprio valor desse macro. O fingerprint final inclui o cabeçalho
completo e é distinto do identificador do site. Um ID de fonte não prova que
o EX5 instalado corresponde a ele nem que houve compilação nativa.

`Store_Result.mqh` define VALID, ABSENT, BUSY, CORRUPT, INCOMPATIBLE e IO_ERROR.
Mensagens traduzidas são apresentação; nunca devem selecionar caminhos de
persistência. Ausência pode permitir inicialização prevista pelo contrato;
corrupção/incompatibilidade não autorizam reset, default silencioso ou migração.

### Trilha técnica e limites

`Diagnostics_Core.mqh` define códigos e políticas; `Diagnostics.mqh` mantém um
SQLite técnico exclusivo em `MQL5/Files/JPWealth/Alavancagem/Diagnostics`.
Somente códigos tipados, contexto opaco, referência de amostra, versões e
horários entram nessa trilha. Não adicionar login, ticket, nome de conta,
credenciais, saldo, equity, cotação ou valor de métrica como texto livre.

Retenção: 30 dias e limite total inferior a 20 MiB; banco limitado a 8 MiB,
journal DELETE limitado e exportação fixa limitada a 64 KiB, sem WAL. Repetições
são agrupadas, linhas antigas rotacionam e páginas são reutilizadas. O lock é
exclusivo, sem espera; leituras e exportações liberam-no antes de desenhar a UI.
Nunca rotacionar MDD, USC, Gênese, snapshots ou outros registros financeiros.

Exportar é uma ação local com prévia verificada, limitada aos eventos técnicos
retidos; não é backup nem série histórica financeira. Falha de gravação deve
ficar visível e não bloquear os cálculos. Não afirmar durabilidade enquanto a
gravação estiver recusada. Reconhecer/consultar o aviso não elimina sua causa.

Os marcadores temporários de escrita recusada pertencem à instância e ao
componente. `ChartID` identifica o gráfico, não o escritor. O ordinal usa um
contador temporário da sessão alocado por CAS limitado; nunca zerar ou remover
esse contador enquanto o terminal estiver aberto. Uma instância só limpa seu
próprio marcador depois de drenar a fila daquele contexto. Falha de alocação
mantém aviso conservador até o fim da sessão; sucesso de outro escritor não
pode apagá-lo. Essa concorrência ainda exige prova nativa isolada.

Callbacks de negociação apenas enfileiram. O timer processa trabalho limitado,
mede duração/adiamentos e deixa lacuna explícita em overflow, tentativas
esgotadas ou falha de gravação. Reconstrução é idempotente e nunca se apresenta
como captura original. Nenhum timer garante despacho exato; uma chamada nativa
individual não pode ser interrompida pelo orçamento de 500 ms.

Qualidade da métrica, saúde técnica e cobertura histórica são dimensões
separadas. Uma evidência recente de heartbeat não prova atividade contínua.
Um período sem lacunas detectadas não prova completude; dados ausentes ou
rotacionados ficam desconhecidos. O sistema não deve oferecer selo global verde
baseado apenas num valor Current.

### Atualização, testes e auditoria

Fluxo: incidente → reprodução sintética → correção candidata → testes → auditoria
independente → promoção autorizada. Antes de alterar uma métrica, mapear todos
os consumidores de seu envelope, estado e unidade. Manter matemática nos núcleos
existentes. Interface não cria regra financeira, nem ocultação suspende coleta.

A suíte `python3 tools/leverage_suite.py --scope all` cobre o host e a
distribuição e produz hashes antes/depois, logs e classificações por teste.
O job `.github/workflows/mt5-host.yml` é separado do gate geral;
`python3 tools/quality_gate.py --tier full` continua obrigatório e bruto.
Host/shim e SQLite do host não equivalem a compilação/execução MQL5.

| Contrato | Evidência focal |
| --- | --- |
| IDs aceitos, valores/unidades, falha e contexto | `leverage_reliability_test.py` |
| Orçamento global, filas, marcadores por instância, retry e encerramento | `leverage_scheduler_test.py` |
| Escritor SQLite real, retenção, lock, corrupção e releitura/checksum | `leverage_diagnostics_test.py` |
| Preferências, eventos, desenho e geometria | `leverage_cockpit_test.py`, `leverage_details_event_test.py`, `leverage_geometry_test.py` |
| Fórmulas e adaptadores preservados | `leverage_live_adapter_test.py`, `leverage_horizon_test.py`, `leverage_factor_test.py`, `leverage_stop_risk_test.py` |
| Logs/classificações, estabilidade dos inputs | `leverage_suite_test.py` |
| Versões, manifesto, ZIP e bytes servidos | `leverage_package_test.py`, `leverage_page_test.py` |
| Prévia, resumo e exportação diagnóstica no MT5 | Script `JPW_Alavancagem_Diagnostics_Tests.mq5`, bytes exatos; NOT_RUN sem execução nativa |
| Compilação, duas instâncias, teclado/DPI/template | MT5 isolado, bytes exatos; NOT_RUN se não comprovado |

Não enfraquecer uma asserção válida para seguir a implementação. Se o contrato
foi alterado deliberadamente pelo plano aprovado, registrar motivo e preservar
os cenários antigos pertinentes. Não renomear PRODUCT_FAIL como dívida aprovada
por conveniência. Os bloqueios históricos permanecem históricos e o candidate
atual precisa de evidência própria.

Rollback restaura os fontes preservados do r15 e regenera pacote/site pelo
processo oficial; não apaga dados financeiros. Diagnósticos têm namespace
próprio e não exigem migração dos registros financeiros. Para rollback apenas
do guia, restaurar seu snapshot separado e gerar novos hashes coerentes.

## Engenharia da revisão 1.10.1

Esta revisão deriva do candidate 1.10.0/r17 conferido em 113/113 arquivos,
fingerprint `54044877713dd3e4909a85dbf4b07c91c850f5adafd2833149970f5d5aaac223`.
Os recibos anteriores permanecem históricos, inclusive 16 PASS / 1
PRODUCT_FAIL na suíte específica, 54 PASS / 3 PRODUCT_FAIL no full e MT5 nativo
`NOT_RUN`. Não inferir identidade do EX5 instalado de uma captura do gráfico.

### Observador presente não é amostra financeira

`Observer_Presence.mqh` usa uma variável **temporária do terminal** por instância
do EA, com chave que inclui hash da versão exata do produto, identidade opaca
de conta/servidor/moeda/instalação e token opaco do publicador. O conteúdo
codifica somente estado tipado `WAITING`, `PUBLISHED` ou `FAILED` e horário
monotônico; não guarda login em texto, ticket, SL, saldo ou valor de métrica.
O EA inicia em `WAITING`, renova por timer, publica o estado da tentativa e
invalida seu próprio sinal no encerramento ou troca de conta. A renovação usa
CAS contra o **último valor exato escrito pela própria instância**: falha
transitória é tentada novamente, marcador removido é recriado e valor alterado
por outro escritor não é adotado nem removido. No encerramento, um CAS torna
o marcador inválido (`0`) imediatamente; a variável temporária pode permanecer
até fechar o terminal e uma nova instância só retoma esse valor zero por CAS.
Não substituir esse protocolo por `GlobalVariableDel`, que não aceita uma
precondição de titularidade. Leitura com mais
de **30 segundos**, relógio inválido ou versão/conta diferente não confirma
presença. Ausência de sinal significa **Observer not confirmed**, não prova
que o EA esteja desligado em todos os gráficos.

O sinal não autoriza `Current`, não altera schemas financeiros e não substitui
SQLite, lease, conexão, integridade, identidade nem digest de composição da
amostra de Stop risk. Mesmo em `PUBLISHED`, falha da validação financeira
mantém `N/A`; snapshot antigo aparece só como `LAST · NOT ACTIVE` em Stops.
Não construir total no indicador nem converter `N/A` em zero. O HUD usa
`Stop risk: N/A · Check Observer` quando a presença não é confirmada; texto
reduzido em gráfico estreito continua devendo indicar nome e estado. O
Cockpit explica manualmente como conferir o EA compatível na **mesma
instalação**, anexo a gráfico aberto, e a aba Experts. Nunca anexar o EA pelo
indicador, alterar terminal operacional ou ativar negociação por diagnóstico.

### Tabela Stops acessível

`Panel.mqh` calcula a capacidade da área útil a partir das alturas medidas.
`Presentation.mqh` primeiro distingue amostra atual, última amostra apenas
histórica e ausência de amostra; só depois desenha as linhas. Quando controles
e uma linha cabem, reduzir cabeçalhos e paginação antes de recusar a tabela.
Se o gráfico for excepcionalmente curto, conservar um botão focável para o
detalhe. Valor nominal e percentual completos ficam na linha quando há espaço
e sempre no detalhe/dica; não truncar o número financeiro para caber. Posições
e pendentes seguem seções separadas, com clique e teclado, sem mostrar uma
geração antiga como risco atual.

Na validação sintética, cobrir ausência de EA, espera inicial, falha de
publicação, sinal vencido e de outra versão/conta, reinício, duas instâncias,
primeira amostra e restauração de `N/A` para valor atual **somente** após
validação completa. Para Stops, reproduzir janela de 620 px e texto de cerca
de 32 px, fontes 9–24, DPI 100–200%, gráfico estreito, seis posições,
pendentes, amostra ausente/antiga/atual e detalhe por clique/teclado.
`leverage_observer_test.py`, `leverage_stop_ui_test.py`, `leverage_panel_test.py`,
`leverage_page_test.py` e `leverage_package_test.py` são focais do host; seu
PASS não substitui compilação e interação nativa em MT5 isolado. Congelar e
auditar produto e guia separadamente; para rollback da 1.10.1, restaurar o
r17 verificado e regenerar manifesto, ZIP, portátil e cache, preservando
registros de conta. Consulte os CHGs próprios desta revisão; este guia não
concede aceite nem promoção.
