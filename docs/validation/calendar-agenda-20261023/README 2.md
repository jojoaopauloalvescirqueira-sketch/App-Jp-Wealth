# Calendário e Agenda — entrega local

Implementação do plano aprovado em 23/10/2026, na branch `codex/calendario-agenda-20261023`, sobre `d517be0`. As 34 entradas de status anteriores, correspondentes a 92 arquivos concretos pendentes, foram preservadas. A comparação desta tarefa usa o manifesto inicial, e não atribui a ela todo o diff contra HEAD. Backup recuperável: `/private/tmp/jpw-calendar-agenda-20261023/baseline/`.

**Candidato final atual:** `85ae832b1f542745`. **Gate atual: 102/102 PASS na execução coordenada.** O gesto de Notas com zoom nativo de 200% foi interrompido; sua causa não foi comprovada. [JSON original](quality-full-final6.json) · [Log completo](quality-full-final6.log). [Prévia isolada versionada](http://127.0.0.1:58998/index.html?v=85ae832b1f542745).

## O que foi entregue

- Botão imediatamente à esquerda do sino e área completa em Ferramentas e Serviços → Calendário, compartilhando dados e comandos, com estados de visualização independentes.
- Calendário mensal com bolinha econômica centralizada abaixo do número e marcador pessoal separado. Filtros de cinco moedas, quatro impactos e três categorias de conteúdo.
- Agenda pessoal com tarefas e compromissos, Salvar/Cancelar explícitos, edição, exclusão e conclusão de tarefas. Datas civis, instantes e fusos têm tratamentos distintos; ambiguidades de horário exigem escolha.
- Escrita confirmada, recuperação de rascunhos, conflitos, inclusão no Backup Completo e preferências separadas dos registros pessoais.
- Pacote econômico local com proveniência e cobertura explícitas. O calendário semanal FF continua disponível em seus consumidores existentes e não reconstrói a nova área mensal. Economia não aumenta a contagem do sino.

O pacote contém **54 eventos**: 53 de outubro e um de novembro, das fontes BEA, ONS, Statistics Bureau of Japan e Stats NZ. Isso representa as séries selecionadas, não cobertura integral de cada economia. **CHF permanece pendente**, com links oficiais; BLS, Fed e RBNZ também não são apresentados como cobertura completa. Publicação, consulta e revisão das fontes são datas distintas. Não há alimentador remoto publicado nem envio de dados pessoais às fontes. [Fontes e cobertura](SOURCES.md).

## Verificação

A rodada final concluiu **102 checks: 101 PASS e 1 ENVIRONMENT_ERROR**: os 96 anteriores preservados, mais seis para calendário e agenda. Nenhum check obrigatório foi dispensado; timeouts e proteções válidas foram mantidos.

| Prova | Evidência já observada | Limite |
|---|---|---|
| Agenda | 22 testes unitários; oito grupos reais de recuperação | Automação com dados sintéticos |
| Calendário | 13 grupos integrados, inclusive seleção adjacente, filtros e recuperação por contexto | Aceite visual humano separado |
| Fontes | 19 testes, incluindo segurança de incorporação no portátil | Cobertura econômica parcial |
| Visual | **370/370 PASS**: 322 casos anteriores e 48 novos | Automação, sem aceite humano presumido |
| Distribuição | **4/4 PASS no build final**: HTTP, PWA realmente offline, arquivo modular e portátil isolado | Sem publicação remota |
| Compatibilidade focal | Dashboard: 30 apresentações; MiniGames: 32; NoCuda: 129 verificações | Não substituem o FULL final |
| Guia | Startup e recarga offline passaram; 13 contraprovas rejeitadas | Mantidos os 52 casos e hash dos 106 caminhos históricos |

[Resumo visual e IDs](visual-full6-summary.json) · [Prova visual completa compactada](visual-full6-raw.json.gz). A compactação foi verificada por recuperação e hash; o resumo não substitui a prova original.

A revisão independente examinou produto, persistência, fontes e verificadores. Encontrou e exigiu correção de falhas reais antes da aprovação do recorte. O resultado integral e o aceite humano continuam separados. [Revisão independente](INDEPENDENT-REVIEW.md) · [Capturas antes/depois](CAPTURES.md) · [Roteiro humano](HUMAN-ACCEPTANCE.md).

## Achados corrigidos

1. O baseline não continha o launcher e a fronteira mensal solicitados. As provas RED foram preservadas.
2. O importador aceitava contêiner pessoal inválido; guardas tipadas passaram a rejeitá-lo sem migrar dados financeiros. Schemas futuros válidos permanecem opacos.
3. Preferências ilegíveis ou incompatíveis podiam ser sobrescritas. Agora são preservadas e permitem uso temporário com aviso; três contraprovas cobrem a proteção.
4. O primeiro pacote reconstruído não incluía os três módulos novos no precache. A lista mantida em `sw.js` foi corrigida e as quatro distribuições passaram.
5. A integração do verificador visual chamava uma matriz depois de fechar o navegador. A ordem foi corrigida; a falha do harness continua registrada.
6. A seleção azul no tema escuro apresentava contraste de 2,83. O texto local foi corrigido, com critério mínimo de 4,5, sem alterar tokens globais.
7. Conteúdo econômico externo podia encerrar uma tag de script no portátil. O builder agora escapa o terminador na incorporação, preservando o JSON canônico. Duas regressões demonstraram RED/GREEN.
8. Selecionar dia adjacente e recuperar falha econômica exigiu preservar o mês, foco e último conjunto válido somente no mesmo contexto de consulta. Os três grupos adicionais passaram.
9. O cabeçalho excedia a largura em 3 px a 390 px com zoom CSS de 125%. O reflow local preserva alvos mínimos de 44 px e ordem dos controles; Dashboard e MiniGames passaram na fonte integrada.

## Histórico de execução preservado

As tentativas FULL1 e FULL2 foram interrompidas antes do fim: respectivamente para aplicar os três registros de continuidade autorizados e para conciliar a expectativa exata de links após expor licenças. São **NOT_RUN como gate completo**. Logs e motivos foram preservados.

O FULL3 completou no build `a026b4c1ed63ac75`: **94 PASS e 8 PRODUCT_FAIL brutos**, sem ENVIRONMENT_ERROR ou NOT_RUN. [JSON original](full-attempt3-raw.json) · [Log original](full-attempt3-raw.log). Três falhas compartilham o defeito real do cabeçalho. As outras cinco apontam expectativas antigas dos verificadores: catálogo 96/102, ações de cabeçalho 4/5, expressão que rejeita credenciais, workspace semanal substituído por mensal e extensão de scripts. A conciliação teve contrato e contraprovas próprios; não transforma esse FULL bruto em PASS.

`distribution-GREEN-final.json` é um nome de intenção: seu conteúdo registra PRODUCT_FAIL por precache ausente. Não é prova verde. `distribution-final2.json` é a prova focal posterior observada. Outras falhas de fixture, ordem de navegador e captura Retina foram mantidas, com causa identificada.

O focal extra `apple_experience_test.py` conserva as falhas brutas de uma expectativa histórica de quatro capítulos. O revisor recompôs o baseline e observou cinco, com fontes Dashboard idênticas. A classificação conciliada é BASELINE_FAIL daquele oráculo preexistente; o focal completo não é promovido a PASS. O contraste novo foi corrigido separadamente. Nenhum gate obrigatório foi dispensado.

## Preservação e limites

[Inventário do delta](SCOPE.md) · [Contrato do calendário](../../architecture/CALENDAR-AGENDA.md) · [Avaliação de impacto agêntico](AGENTIC-IMPACT.md). As fontes de Planejamento, Notificações, motor/política Forex, escritor canônico e AGENTS são confrontadas com a baseline. Nenhum incidente histórico foi encerrado automaticamente.

**Aceite humano: NOT_RUN.** Automação e capturas não comprovam compreensão, conforto, Safari, leitor de tela ou toque físico. Sem commit, merge, push, publicação, dependências novas, mudança de fórmulas ou configuração de memória global.

## FULL4 — resultado bruto e iteração seguinte

O build5c6a4e7af7a747a3 concluiu os102checks:99PASS e3PRODUCT_FAIL, sem checks não executados. O código e verificadores permaneceram estáveis em2.358caminhos. [JSON original](quality-full-final4.json) · [Log original](quality-full-final4.log).

O Guia passou51/52casos; uma recarga excedeu o timeout original7000ms antes do fluxo de recusa. Isso será investigado sem aumentar o timeout. Correntes eGêmeos apontaram dois efeitos da mesma ocupação excessiva do cabeçalho noGlass móvel comzoom. As provas visual369/369 e distribuição4/4 deste build continuam válidas como histórico, mas não aprovam automaticamente a correção seguinte. Nenhum teste ou critério de clique foi enfraquecido.

Duas correções documentais previamente revisadas foram aplicadas antes da próxima rodada: a descrição dos cancelados passou a refletir a lista e os marcadores existentes; ACTIVE passou a remeter o estado efetivo ao relatório. Nenhum runtime, teste, regra, autoridade ou fingerprint muda por essas frases. O candidato seguinte será novamente reconstruído e congelado.

## Correção do Glass e retorno de foco — candidato85ae832b1f542745

O grupo de ações do Glass fechado era mantido visível pelo seletor comID, que vencia a regra de recolhimento. A nova regra respeita o estado fechado, preserva alvos44px e não alcança outros layouts nem o menu aberto. Provas injetadas: Correntes48/48 eGêmeos32/32. O cabeçalho no cenário crítico reduziu404→120px, comPLAY6/6pontosacessíveis. A fonte integrada passou34cenários do cabeçalho.

O recolhimento revelou perda de foco ao fechar o calendário: Escape deixava foco noBODY. O controlador passou a usar o helper existente da navegação. ProvasRED eGREEN10/10preservadas; oráculo ampliado sem remover casos. A execução oficial passou48/48, com40apresentações (incluindo8nativas200%) e8contraprovas. Total visual requerido da próxima rodada:370.

A recarga do Guia que falhou noFULL4 passou em quatro repetições focais sem alteração de timeout ou teste. Uma execução adicional passou51jornadas, mas a invocação de triagem omitiu uma flag de metadata e teve uma falha deharness; esse resultado não é52/52 nem substitui o próximoFULL canônico. A causa do timeout isolado não foi comprovada.

Limite exploratório separado: aplicar artificialmente `style.zoom=2` a390px não equivale ao zoom nativo do navegador e revelou diálogo maior que o viewport. Esse estresse não foi corrigido nem declarado aprovado; os casos exigidos de zoom nativo200% são medidos separadamente. Preservar sete colunas e alvos44px impõe largura mínima; não se reduziram alvos para tornar a prova verde.

## FULL5 — resultado bruto e investigação de Notas

O build `85ae832b1f542745` concluiu os 102 checks: **101 PASS e 1 TEST_HARNESS_FAIL**, sem PRODUCT_FAIL, ENVIRONMENT_ERROR ou NOT_RUN. Calendário, agenda, distribuição, Guia, os três minigames e **370/370 casos visuais** passaram. Os 2.358 caminhos permaneceram estáveis durante a rodada, com as oito fontes críticas iguais à baseline. [JSON bruto](quality-full-final5.json) · [Log](quality-full-final5.log) · [Freeze](freeze-full5-after.json) · [Falha de Notas](notes-launcher-full5-raw.json).

O teste de Notas em `index.html/390/light` excedeu o timeout original ao clicar no menu móvel após o gesto de toque. Uma repetição instrumentada passou 19/19 sem alteração de produto ou oráculo; a causa permanece indeterminada e esse PASS não elimina a ocorrência original. Diagnóstico apenas no caminho de exceção será acrescentado ao teste, sem alterar critérios, timeouts ou seu caminho positivo, antes de nova rodada canônica.

A única mudança de fonte entre FULL5 e a nova rodada é diagnóstica em `tools/notes_launcher_test.py`: DOM, viewport, ancestrais, overlays, console, HTML e captura são coletados somente nos três caminhos de exceção. A reversão exata do delta recupera o teste anterior; nenhuma asserção, evento, timeout ou rota positiva foi alterada. A execução CLI original passou 19/19. [Delta](notes-launcher-diagnostics.diff) · [Contraprova de diagnóstico indisponível](notes-launcher-diagnostics-structure.json) · [CLI](notes-launcher-diagnostics-GREEN.json). O comportamento do aplicativo e o build permanecem inalterados.

## FULL6 — resultado final observado

O build `85ae832b1f542745` concluiu os **102 checks: 101 PASS e 1 ENVIRONMENT_ERROR**, sem PRODUCT_FAIL, TEST_HARNESS_FAIL, BASELINE_FAIL ou NOT_RUN. [JSON original](quality-full-final6.json) · [Log](quality-full-final6.log). O calendário passou seus **13 grupos**, a recuperação **8**, a distribuição **4**, o visual **370/370** e o Guia **52/52**. Correntes, Gêmeos e MiniGames passaram. Esses resultados não tornam o gate inteiro verde.

O teste de Notas concluiu **18/19**: o caso móvel que falhou no FULL5 passou; desta vez, no último clique de 2 px com zoom nativo de 200%, ocorreu `lostpointercapture` entre pressionar e soltar. O teste preservou sua classificação de entrada interrompida. **Isso não comprova causa externa.** Não houve erro de console, oclusão ou alteração de fontes observada nesse ponto; nenhuma mudança preventiva foi feita no produto. A causa permanece indeterminada. [Resultado de Notas](notes-launcher-full6.json) · [Captura](notes-native-full6.png) · [DOM sintético compactado](notes-native-full6.html.gz).

Os **2.358 caminhos** de produto, testes e documentação permaneceram estáveis durante a rodada. As oito fontes críticas continuam iguais à baseline. O código de Notas também foi confrontado separadamente e é idêntico ao inicial. [Freeze inicial](freeze-full6-before.json) · [Freeze final](freeze-full6-after.json). Os recibos desta pasta ficam fora do freeze, sem runtime ou oráculos.

O candidato pode ser consultado localmente para avaliação. **Aprovação técnica integral e aceite humano permanecem pendentes**; não houve commit, merge, push ou publicação. O pacote econômico também permanece parcial, com BLS, Federal Reserve, RBNZ, CHF e calendário completo de Stats NZ pendentes. As séries declaradas e os limites estão no inventário de fontes.

Os três registros de continuidade autorizados foram verificados contra os diffs: somente o prefixo aprovado foi acrescentado e os históricos anteriores preservaram seus hashes. [Prova dos três registros](context-approved-preservation.json).

## Prévia para avaliação

[Abrir candidato local versionado](http://127.0.0.1:58998/index.html?v=85ae832b1f542745). O novo ícone de calendário fica imediatamente à esquerda do sino; a mesma agenda está em Ferramentas e Serviços → Calendário. A origem local é nova e isolada: registros dos endereços anteriores permanecem lá, sem migração ou limpeza. Índice, CSS, build-id e os dois módulos públicos foram comparados byte a byte com o disco. [Verificação HTTP](preview.json). A prévia não representa aprovação do gate global, publicação ou aceite humano.

O gravador focal posterior executou os 19 casos originais e passou, com fontes e teste inalterados. Registrou 259 eventos; as seis perdas de captura tiveram liberação explícita anterior e a única com gesto ativo foi a provocação intencional do teste. A interrupção inesperada do FULL6 não foi reproduzida. O overhead de observação pode afetar uma falha intermitente; esse PASS não determina a causa, não fecha o incidente e não substitui o FULL6. [CLI 19/19](notes-native-triage-19.json) · [Eventos e pilhas](notes-native-triage-summary.json) · [Trace completo](notes-native-triage-trace.json).

## Validação coordenada anterior à integração

A suíte completa posterior concluiu **102/102 PASS**, sem falhas ou checks não executados. [JSON bruto](quality-full-coordinated.json) · [Log](quality-full-coordinated.log). O usuário informou uso de mouse durante as execuções anteriores e disponibilizou o Mac sem interação para esta rodada. Três repetições estritas de Notas também passaram previamente. Isso é compatível com interferência na entrada, sem comprovar retrospectivamente a causa de cada ocorrência histórica. Fontes e verificadores permaneceram iguais ao freeze anterior; nenhuma proteção ou timeout foi alterado. Os resultados anteriores permanecem históricos. Cobertura econômica parcial e aceite visual humano continuam separados.
