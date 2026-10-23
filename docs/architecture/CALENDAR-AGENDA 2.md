# Calendário e Agenda — contrato aprovado23/10/2026

Fonte: plano humano [Calendário e Agenda](../superpowers/plans/2026-10-23-calendar-agenda.md), produtoN2/verificadoresN3 em CHGs dedicados. Este contrato descreve o delta autorizado, não altera normas financeiras. Implementação local; resultado técnico e aceite humano nos recibos próprios, nunca inferidos deste texto.

## Finalidade e entradas

Calendário mensal e agenda de compromissos/tarefas no botão headerCalendarBtn imediatamente antes do sino, e no workspace tools-calendar/#execEcal. JPWCalendar.open/close/mountWorkspace/deactivateWorkspace/resetContext/disposeForSession são o controlador. Duas superfícies compartilham dados/comandos e mantêm mês/dia/filtros/rolagem independentes. Diálogo HTML nativo, ancorado ao acionador quando há espaço; sheet estreito. Não empilha sobre outros diálogos. Fechar preserva rascunho; Cancelar o descarta explicitamente. A sessão captura drafts antes de descartar o controlador.

## Grade e apresentação

Red dot no centro horizontal sob numeral somente se há evento econômico correspondente aos filtros; agenda/app usam marcador separado. Hoje, seleção e quantidade são identificados também por nome acessível. Dias44px, teclado umtabstop, setas±1/7, Home/End semana de segunda a domingo, PageUp/PageDown mês, Enter/Espaço seleciona, Escape fecha/restaura foco. Conteúdo interno/ícones seguem2px CSS máximo. Preservar foco/cursor/rolagem nas atualizações. Leitura/expansão/navegação não grava dados financeiros.

Filtros de moedas USD,GBP,JPY,NZD,CHF; impactos high/medium/low/unclassified; conteúdos economic/personal/app. Defaults5moedas+high+3conteúdos. Chave jpwealth_calendar_view_v1: {schemaVersion:1,currencies:[],impacts:[],contents:[]}, arrays semduplicatas e enums conhecidos. Falha de leitura permite recorte RAM mas impede sobrescrita até leitura conferida; schema/keys desconhecidos preservados opacos. Mesma validação no backup; preferências participam da limpeza auxiliar, sem se misturar a S. Abrir/filtrar não muda sino. Observadores não alteram resultado dos comandos.

## Agenda confirmada

Agregado opcional S.personalAgenda {schemaVersion:1,revision,items}. Ausência significa agenda vazia virtual, sem criar chave por consulta; DEFAULTS/migrate permanecem. Schema futuro/conteúdo incompatível preservado sem comandos e disponível para backup/recuperação. IDs e revisões estáveis. Item: task|appointment, título, notas, date civil, allDay, startAt/endAt instantes ou null, timeZone IANA ou null, completedAt/createdAt/updatedAt e revision. Extensões compatíveis conservadas.

JPWAgenda.queries.snapshot/range/prepare/previewEntry são somente leitura. range({from,to,timeZone}) aplica fuso de visualização a instantes, com fim exclusivo, e mantém datas civis. previewEntry distingue DSTinexistente/ambíguo e exige escolha explícita em ambiguidade. Campos têm validações e mensagens; o usuário salva no próprio formulário. Tarefas têm conclusão; compromissos não. commands.save/setCompleted/remove usam token vinculado ao contexto/geração/epoch/revisão/item e escritor jpWealthPersistDocument; adoção de S somente CONFIRMED. Barreira contra RAM financeira adjacente não confirmada. REFUSED/CONFLICT preservam rascunho; UNKNOWN bloqueia repetição e encaminha recuperação. Detector de concorrência best effort do writer existente, sem alegar CAS/serialização universal entre abas.

Backup Completo mantém envelope V9.1 e transporta documento confirmado inteiro, incluindo agregado opcional. Import recusa contêiner inválido antes de adoção; schemas futuros objetos permanecem opacos. Draftprovider calendar-agenda exporta somente campos/contexto/referência, nunca tokens/consentimento. Captura genérica exclui .calendar-form; reabrir rascunho nunca executa comando. Finalização preserva documento/drafts, invalida controladores/tokens e cancela relógios.

## Tarefas do aplicativo e ciclo

Somente backup quando existe confirmação temporal válida; vencimento exato lastConfirmedAt +DG_BACKUP_DUE_DAYS×86400000, não somar datas de calendário. Falta/futuro inválido não recebe dia inventado. Entrada oferece Abrir Backup e Recuperação e é somente leitura; conclusão depende da fonte. Competências de Planejamento e outros fatos não viram prazos diários. Nova agenda não cria cobranças no sino.

Um timeout até próxima meia-noite apenas com superfície ativa/visível, cancelado ao fechar/sair/ocultar/dispose. Retorno/foco reconsulta estado. Eventos jpw-agenda-changed, econômico e backup podem atualizar superfícies necessárias; guardas de geração/request impedem aplicação atrasada. Nenhum render contínuo em repouso.

## Econômico mensal e legado semanal

JPWEconomicCalendar.queryRange({from,to,currencies,impacts,timeZone}), sources(),metadata(): pacote público validado, semDOM/fetch/storage. Evento temID,fonte,datafonte/data exibida, at oudateOnly, precisão,fuso,status,reviewedAt e impactoeditorial JP. Instantes convertidos ao fuso de visualização; data semhora mantém data dafonte e explicação explícita. Não inventar meia-noite nem interpretar tempo passado como publicação confirmada. Eventos cancelados permanecem consultáveis, rotulados Cancelado; seus marcadores seguem os mesmos filtros da lista.

Coverage porfonte/moeda/mês, com intervalos e estados confirmed/partial/pending/stale/unavailable. Nenhum resultado não é prova de calendário completo. Com dadosausentes/falha, preservar diagnóstico/último conjunto válido e não declarar resolução. Pacote inicial cobre séries declaradas no mês corrente completo e datas futuras já publicadas; fora do intervalo é cobertura não confirmada. BEAICS coletor explícito, ONSpublished/upcoming/cancelled separados, SBJcalendários estatísticos e StatsNZCPI/SPI com proveniência/termos em infra/monthly-economic-feed. BLS/Fed/RBNZ incompletos continuam explicitados como pendentes quando não curados; CHF permanecependente. Não acessar RBNZ automaticamente nem copiar calendários BoE/BoJ sem condições adequadas.

Snapshot econômico é público e independente de dados pessoais; build_package.py --check reproduz sem regravar, collect_feed.py --fetch-bea é explícito. Não há publicação/credenciais/rede adicional no navegador para este novo domínio. Atualizações públicas futuras exigem autorização de publicação; pacote local viaJSclássico funciona offline/arquivo/portátil.

JPWEcal.open/openMenu/close continuam com cache FF semanalaltoUSD/EUR/GBP/JPY em widget/overlay; tickerFFnão reconstrói Toolsmensal e não injeta dadosFFno pacote mensal. Dados/filtros/cacheIDs separados e escopos visíveis. tools-calendar eIDda lição do guia preservados.

## Validação

Casos permanentes em personal_agenda_test.js,calendar_recovery_test.py,monthly_economic_feed_test.py,calendar_agenda_test.py e extensõesui_visual_quality_test.py; distribuição própriaHTTP/PWA/file/portátil. Verificadoreslegados de população4→5 e workspaceFFsubstituído reconciliados por contrato, mantendo coberturaEUR/cache/recusa/readonly. RED/GREEN/counterproofs e gates vinculados aos bytes finais. Aceite humano, compreensão, toque físico e leitor de tela têm provas separadas. Recibos em docs/validation/calendar-agenda-20261023/.
