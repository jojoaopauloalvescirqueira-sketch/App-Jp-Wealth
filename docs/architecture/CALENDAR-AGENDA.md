# Calendário e Agenda — contrato aprovado23/10/2026

## Calendário e Mercados — integração24/10/2026

[Plano aprovado](../superpowers/plans/2026-10-24-calendar-markets.md). Ferramentas → Calendário e Mercados mantém tools-calendar como destino único. Calendário e Agenda permanece em #execEcal; Bolsas Globais — Agora é seção irmã, com resumo de três abertas/três próximas24h e exploração sob demanda. O modal ao lado do sino não muda. Calendário segue a data selecionada; bolsas seguem Agora, com filtros independentes. tools-market-hours e chamada local antiga conservam intenção de abrir diretamente a exploração, canonicalizada para tools-calendar após aceite.

JPWMarketHours.mount(host,{collapsed:true}) cria resumo; sem opções conserva full. setExpanded(boolean) mantém instância/catálogo/snapshot, filtros, seleção e DOM. Resumo atualiza ao minuto/limites; full só é montado na primeira expansão. Renderer executado somente com mapa expandido e visível; câmera/quadros pausam fora da viewport, diálogo, hidden, blur, saída ou descarte. Falhas no resumo oferecem retry e mantêm último diagnóstico identificado como não atual. Não altera calendários, fontes, persistência ou escritores financeiros.

Novos resultados: [validação desta integração](../validation/calendar-markets-20261024/README.md), somente quando os recibos existirem. Evidências anteriores abaixo mantêm seu escopo histórico; não comprovam este candidate.

Fonte: plano humano [Calendário e Agenda](../superpowers/plans/2026-10-23-calendar-agenda.md), produtoN2/verificadoresN3 em CHGs dedicados. Este contrato descreve o delta autorizado, não altera normas financeiras. Implementação local; resultado técnico e aceite humano nos recibos próprios, nunca inferidos deste texto.

## Finalidade e entradas

Calendário mensal e agenda de compromissos/tarefas no botão headerCalendarBtn imediatamente antes do sino, e no workspace tools-calendar/#execEcal. JPWCalendar.open/close/mountWorkspace/deactivateWorkspace/resetContext/disposeForSession são o controlador. Duas superfícies compartilham dados/comandos e mantêm mês/dia/filtros/rolagem independentes. Diálogo HTML nativo, ancorado ao acionador quando há espaço; sheet estreito. Não empilha sobre outros diálogos. Fechar preserva rascunho; Cancelar o descarta explicitamente. A sessão captura drafts antes de descartar o controlador.

## Grade e apresentação

Red dot no centro horizontal sob numeral somente se há evento econômico correspondente aos filtros; agenda/app usam marcador separado. Hoje, seleção e quantidade são identificados também por nome acessível. Dias44px, teclado umtabstop, setas±1/7, Home/End semana de segunda a domingo, PageUp/PageDown mês, Enter/Espaço seleciona, Escape fecha/restaura foco. Conteúdo interno/ícones seguem2px CSS máximo. Preservar foco/cursor/rolagem nas atualizações. Leitura/expansão/navegação não grava dados financeiros.

Filtros de moedas USD, EUR, GBP, JPY, CHF, CAD, AUD, NZD e CNY; impactos high/medium/low/unclassified; conteúdos economic/personal/app. Primeiro acesso seleciona nove moedas, Alto e os três conteúdos. A chave `jpwealth_calendar_view_v1` e seu schemaVersion 1 permanecem; preferências válidas salvas são preservadas, sem incluir novas moedas silenciosamente. O painel identifica moedas novas desmarcadas e oferece inclusão explícita. Validações das preferências e do Backup Completo aceitam os mesmos nove códigos. Dados incompatíveis permanecem opacos; falhas de leitura não autorizam sobrescrita. Abrir, filtrar ou consultar não modifica dados financeiros nem a contagem do sino.


## Notícias em tabela compacta — revisão28/10/2026

As duas superfícies mensais apresentam um único conjunto de sete campos: Horário, Moeda, Impacto, Evento, Atual, Projeção e Anterior. A data/fuso/quantidade e situação da consulta econômica aparecem uma vez no cabeçalho. O painel reserva308px para o mês (sete alvos44px sem gap), mantém a agenda ao lado com700px úteis ou mais e empilha abaixo desse limite. Com720px úteis nas notícias há sete colunas semânticas; abaixo disso cada evento usa identificação e uma faixa Atual/Projeção/Anterior rotulada, com altura automática, quebra de texto e ausência de rolagem horizontal. Compromissos, tarefas e itens do aplicativo mantêm seus grupos.

Projeção e Anterior reproduzem o texto já recebido, incluindo sinais, unidades e zero. Atual significa resultado econômico divulgado, ausente nesta alimentação: travessão e explicação acessível **Não fornecido nesta alimentação**. Não inferir Atual pela Projeção, Anterior, relógio, publicação ou mudança de captura. O tipo de impacto é identificado por símbolo/nome acessível, sem cores de resultado favorável/desfavorável.

O botão i na célula Evento tem nome específico, alvo44px e expansão inline de fonte/horário original/referências/explicação. Cancelamento, conflito, horário provisório ou ausência na última coleta permanecem visíveis recolhidos. Estado de expansão somente em RAM por superfície; uma observação exata e única pode conservar detalhe após refresh, sem transferir foco/expansão a título semelhante, ID reutilizado com horário diferente ou duplicata ambígua. Desaparecimento do evento recupera foco no cabeçalho apenas quando o foco pertencia à linha retirada; não rouba foco do editor pessoal. Atualizações preservam rolagem e formulário. Escape conserva o fechamento nativo do diálogo e retorno ao acionador.

Este delta modifica somente renderização/CSS e contrato. APIs, consulta síncrona, adaptador, cache, pacote público, preferências, backup, consumidores semanais, agenda e Bolsas Globais permanecem. Verificadores novos têm CHG próprio; evidências deste candidato em [tabela econômica](../validation/economic-calendar-table-20261028/README.md), sem herdar aprovação do FULL anterior.

## Agenda confirmada

Agregado opcional S.personalAgenda {schemaVersion:1,revision,items}. Ausência significa agenda vazia virtual, sem criar chave por consulta; DEFAULTS/migrate permanecem. Schema futuro/conteúdo incompatível preservado sem comandos e disponível para backup/recuperação. IDs e revisões estáveis. Item: task|appointment, título, notas, date civil, allDay, startAt/endAt instantes ou null, timeZone IANA ou null, completedAt/createdAt/updatedAt e revision. Extensões compatíveis conservadas.

JPWAgenda.queries.snapshot/range/prepare/previewEntry são somente leitura. range({from,to,timeZone}) aplica fuso de visualização a instantes, com fim exclusivo, e mantém datas civis. previewEntry distingue DSTinexistente/ambíguo e exige escolha explícita em ambiguidade. Campos têm validações e mensagens; o usuário salva no próprio formulário. Tarefas têm conclusão; compromissos não. commands.save/setCompleted/remove usam token vinculado ao contexto/geração/epoch/revisão/item e escritor jpWealthPersistDocument; adoção de S somente CONFIRMED. Barreira contra RAM financeira adjacente não confirmada. REFUSED/CONFLICT preservam rascunho; UNKNOWN bloqueia repetição e encaminha recuperação. Detector de concorrência best effort do writer existente, sem alegar CAS/serialização universal entre abas.

Backup Completo mantém envelope V9.1 e transporta documento confirmado inteiro, incluindo agregado opcional. Import recusa contêiner inválido antes de adoção; schemas futuros objetos permanecem opacos. Draftprovider calendar-agenda exporta somente campos/contexto/referência, nunca tokens/consentimento. Captura genérica exclui .calendar-form; reabrir rascunho nunca executa comando. Finalização preserva documento/drafts, invalida controladores/tokens e cancela relógios.

## Tarefas do aplicativo e ciclo

Somente backup quando existe confirmação temporal válida; vencimento exato lastConfirmedAt +DG_BACKUP_DUE_DAYS×86400000, não somar datas de calendário. Falta/futuro inválido não recebe dia inventado. Entrada oferece Abrir Backup e Recuperação e é somente leitura; conclusão depende da fonte. Competências de Planejamento e outros fatos não viram prazos diários. Nova agenda não cria cobranças no sino.

Um timeout até próxima meia-noite apenas com superfície ativa/visível, cancelado ao fechar/sair/ocultar/dispose. Retorno/foco reconsulta estado. Eventos jpw-agenda-changed, econômico e backup podem atualizar superfícies necessárias; guardas de geração/request impedem aplicação atrasada. Nenhum render contínuo em repouso.

## Econômico mensal e legado semanal — revisão 28/10/2026

`JPWCalendarFeed` é o produtor compartilhado de rede/cache públicos e ciclo de vida; mantém snapshot/status/refresh, compatibilidade semanal e descarte/retomada explícitos de sessão. O domínio `JPWEconomicCalendar.queryRange({from,to,currencies,impacts,timeZone})`, sources() e metadata() permanece síncrono e não executa rede, persistência financeira ou leitura de contas. Calendário do cabeçalho, workspace e consumidores semanais reutilizam o produtor existente; um evento de atualização não reconstrói Bolsas Globais nem descarta rascunhos.

A composição usa a base oficial anterior, o pacote público local v2 e o cache validado do alimentador disponível. O v1 remoto continua compatível e explicitamente parcial: USD/EUR/GBP/JPY de Alto impacto. O v2 contém nove moedas e todos os impactos exportados. Payload v2 inválido não substitui o último conjunto válido. Dados externos são apresentados como texto; URLs são HTTPS sem credenciais e o pacote embutido é produzido pelo gerador oficial.

Os metadados compostos distinguem origens por evento (`editorialPolicy.kind: mixed`) e a política de atualização: FF7200s pela coleta e fontes oficiais pelo prazo individual de coverage.validUntil. `officialBaseMetadata` conserva separadamente textos, cinco moedas, IDs de fontes e referências da base oficial anterior; suas declarações antigas não descrevem o conjunto combinado. `generatedAtScope` identifica a referência histórica. Essa distinção vale também para uma base oficial que recebe v1/v2 posteriormente em RAM; base somente oficial sem feed mantém seu próprio escopo. O retorno continua síncrono e é uma cópia independente.

A cobertura é por fonte, moeda e intervalo, com estados confirmed/partial/pending/stale/unavailable. Export FF semanal só cobre observações da semana capturada; snapshots anteriores não inventam meses ausentes nem confirmam cobertura completa. Atualidade da fonte e download do navegador são distintos. `collectedAt` preserva a captura; `packagePublishedAt` é apresentado como “Geração do pacote”, sem alegar publicação remota; atualização nativa desconhecida permanece nula. Após duas horas sem nova coleta FF, sinalizar desatualização sem apagar histórico. Reprocessamento offline não renova a data da fonte.

Eventos FF conservam impacto do provedor (`impactOrigin: provider`, `providerImpact`) e ID local de observação, com sourceUid nulo e identidade de snapshot. O export não prova resultado realizado, hora confirmada, publicação, reagendamento ou cancelamento. `observationStatus: not-in-latest` significa somente que a observação não consta na captura mais recente da mesma semana; conservar os dados e o aviso. Uma semana posterior não marca toda a semana anterior como desaparecida. Não ligar eventos por semelhança genérica de título/data.

Sete associações de famílias documentadas ligam os tópicos Fed/BoC de 28/10 aos seus pares FF sem duplicá-los. A união preserva as duas proveniências; discrepâncias de horário ou cancelamento permanecem visíveis. Classificação das fontes oficiais é editorial JP Wealth e a do FF continua pertencendo ao provedor. Tópicos sem associação explícita conservam suas identidades. Instantes são convertidos ao fuso de visualização; datas sem hora mantêm o dia da fonte. Não presumir meia-noite ou publicação por passagem do tempo. Estados e informações ausentes permanecem distintos de zero.

BEA, catálogo ONS, famílias SBJ e publicações Stats NZ anteriores permanecem preservados com seus limites e carimbos. Os complementos oficiais Fed/BoC cobrem famílias de política monetária selecionadas, não o mês inteiro das moedas. Demais calendários BLS/Fed/BoE/BoJ/NZD e agendas oficiais CHF continuam pendentes onde não coletados ou permitidos. A presença de dados FF em CHF não estabelece licença das agendas oficiais suíças. Não automatizar RBNZ nem reutilizar diretamente agendas BoE/BoJ sem a condição correspondente.

O coletor local faz uma leitura pública FF e deriva o recorte v2 e o v1 legado da mesma captura. Arquivos semanais e recibos são preservados; bytes idênticos são compartilhados por hash. Falha de rede/HTTP/JSON/validação retorna saída não zero antes de substituir visões boas. Cada arquivo usa substituição atômica individual, sem promessa de transação entre arquivos. `--rebuild-archives --check` reproduz sem rede ou regravação. O build oficial incorpora o snapshot para HTTP, offline, arquivo local e portátil.

A permissão não comercial FF foi declarada pelo proprietário e não auditada documentalmente pelo agente. Fonte, atribuição e limites permanecem identificados. Preparar um coletor ou modelo de workflow não publica nem ativa o endpoint externo. O modelo conserva a cadência planejada de 30 minutos e exige habilitação externa explícita; publicação, credenciais e operações Git pertencem a uma etapa autorizada separada.

`JPWEcal.open/openMenu/close` continua oferecendo o calendário **semanal** no legado, com o recorte quatro moedas/Alto, derivado pelo mesmo produtor. `tools-calendar`, o progresso do guia e as preferências válidas são preservados. Consultar notícias, expandir informações, mudar filtros e atualizar o feed público não gera notificações econômicas no sino nem grava fatos financeiros.


## Validação

Casos permanentes em personal_agenda_test.js,calendar_recovery_test.py,monthly_economic_feed_test.py,calendar_agenda_test.py e extensõesui_visual_quality_test.py; distribuição própriaHTTP/PWA/file/portátil. Verificadoreslegados de população4→5 e workspaceFFsubstituído reconciliados por contrato, mantendo coberturaEUR/cache/recusa/readonly. RED/GREEN/counterproofs e gates vinculados aos bytes finais. Aceite humano, compreensão, toque físico e leitor de tela têm provas separadas. Recibos históricos em docs/validation/calendar-agenda-20261023/. A integração FF de 28/10 possui recibos próprios em docs/validation/economic-calendar-ff-20261028/; resultados anteriores não aprovam os novos bytes.
