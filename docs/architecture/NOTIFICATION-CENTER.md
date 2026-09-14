# Central de notificações — NOTIFICATIONS-CENTER-01

## Finalidade e alcance

Inventário inspecionado em 2026-09-14 sobre a branch
`codex/dashboard-surfaces-20260914`, HEAD
`5f0c9680bdd9a93e9d184ca751999c70193a72aa` mais o candidate visual local.
O [CHG/CTX](../work/CHG-NOTIFICATIONS-CENTER-20260914.md) delimita o complemento.
Este documento distingue os produtores existentes do contrato da central; leitura
de código não demonstra funcionamento testado. Resultados e identidade final
pertencem às evidências do candidate, não são antecipados aqui.

A central reúne sinais já produzidos pelo aplicativo e oferece acesso à sua
origem. Não é motor financeiro, ledger de auditoria, backup, sistema de tarefas
com vencimento nem serviço de entrega de mensagens. O sino
`#headerNotificationsBtn` abre `#notificationCenter`; a camada de apresentação
fica em `src/js/40-app/18-notification-center.js`, carregada ao final da ordem
existente. Não altera `S`, schemas, caches, protocolos de gravação ou permissões.

## Semântica

| Classe | Origem e significado | Comportamento preservado |
|---|---|---|
| Condição ativa | Estado atual verificável no produtor: bloqueio, falha, pendência ou evento iminente | Um item por causa/entidade. Atualizar ou retirar quando a fonte mudar; leitura não resolve a causa. |
| Mensagem da sessão | Feedback que o aplicativo efetivamente exibiu durante esta abertura | Histórico efêmero, limitado; não prova independentemente que o ato foi concluído. |
| Validação de entrada | Erro associado ao formulário ou tentativa corrente | Permanece junto do campo; o espelho não lê valores nem corrige a entrada. |
| Confirmação/decisão | `confirm()`, `prompt()`, confirmação destrutiva ou escolha de recuperação | Continua no fluxo original. O sino não confirma, descarta, salva, importa, finaliza ou desbloqueia nada automaticamente. |
| Informação estática | Avisos educacionais, lacunas do produto, descrição do estado vazio | Permanece na superfície de origem; não gera repetidamente um badge de incidente. |

Marcar como lido altera somente a apresentação nesta sessão. Não equivale a
confirmar backup, aceitar regra, homologar V11, reconhecer gravação ou dispensar
uma proteção. O histórico não modifica status/prioridade de Notas. Ausência de
item não prova ausência geral de problemas nem observabilidade completa.

## Inventário de produtores

Os caminhos abaixo são relativos à raiz do repositório. As funções citadas são
as fontes de comportamento; não se deve reconstruir seus cálculos na central.

| Área | Fonte e sinais existentes | Destino e limite |
|---|---|---|
| Dashboard | `40-app/12-global-dashboard.js`: `renderSystemStatus`; `20-ui/25-dash-macro.js`: resumos e estados parciais/indisponíveis dos módulos | É consumidor das fontes abaixo, não uma segunda causa. Deduplicar o mesmo bloqueio que aparece no resumo e no módulo. |
| Forex — operação | `20-ui/04-operational-clearance.js`: `getOperationalClearance(c)` retorna status, título, subtítulo, motivos e ação. Resume quarentena, DD/MDD, risco, stop, alavancagem, reservas, caixa e proteção. `20-ui/03-main-render.js`: banners de estado, quarentena e violação | Forex → Visão Geral/Operação. Reutilizar classificação e texto existentes, sem alterar teto, fórmula, liberação ou severidade financeira. |
| Forex — cadastro/governança | `10-domain/01-risk-instruments.js`: `getOnboardingCompletionState()`; aviso de formulário incompleto e aviso da execução | `openFirstIncompleteOnboarding()` mantém o destino pertinente e suas decisões. Seções pendentes não devem gerar duplicatas de um mesmo aviso agregado. |
| Forex — ordens/revisão | `10-domain/03-phase-transitions.js`: `needsReview` e `stopPhaseWarning`; validações de execução existentes | Encaminhar à operação para conferência. Não revisar, confirmar ou modificar ordem a partir de leitura do sino. |
| Forex — Planejamento | `30-accounting/05-fx-planning/05-fx-ui.js`: `fxpRememberDraft`, erros e feedback dos atos; barreira global de persistência desconhecida | Forex → Planejamento. Observar mensagens já exibidas. Não chamar normalizadores como `fxState`/`fxActivePlanRaw` apenas para obter notificações; leitura da central não deve normalizar `S`. |
| Finanças Pessoais | `10-domain/12-personal-finance.js`: `pfWriteBlockReason`, `pfPendingBefore`, `pfCreditLineDerived`; renderizadores `20-ui/17` a `22`: unidade incompatível, pendências de meses anteriores materializados, crédito excedido, destinações excedentes, validações e recusas | Orçamento/Dívidas/Cenários pelo roteador existente. Respeitar sentinela monetária; não materializar mês nem recalcular por aritmética paralela. Crédito/destinação excedidos continuam com a classificação e explicação do domínio. |
| Alladin | `10-domain/13-alladin.js`: `JPWAlladin.compat()` e read-models; `20-ui/24-alladin-views.js`: `alladinIndisponivel`, `alladinErroInline`, avisos de cadastro, conflito e feedback de lançamento/estorno | Alladin → Lançamentos/Saldos/Posições/Cadastros. Qualidade inválida ou agregado indisponível não vira lista vazia. `COMMITTED_WARNING` mantém a escolha Manter/Inativar no diálogo original. Consultar os leitores canônicos de ledger, posições e saldo por caixa, interrompendo na primeira recusa; não copiar números para o badge. O custo de leitura em bases grandes não foi medido. |
| Research — calendário | `40-app/15-ff-news.js` e `40-app/17-economic-calendar.js`: cache comum, eventos próximos, status de fonte/cache e agenda semanal | Agenda existente em Research → Forex → Calendário ou `JPWEcal.open`. Contrato específico abaixo. |
| Research — NoCoda | `20-ui/14-nocoda-studies.js`: `ncShowErrors`, `ncSaveStudy`, `ncDirty`, `ncStatus` | Erro de campo; parâmetros não salvos; rascunho mantido após recusa; gravação desconhecida com proibição de repetir. Retornar ao estudo sem salvar ou trocar instrumento silenciosamente. |
| Research — Pivots | `20-ui/15-pivot-studies.js`: `pvMutateStudies`, `pvShowErrors`, `pvDirty`, estudo/pivot desaparecido da base | Erro e recusa mantêm formulário. Período coincidente, descarte e exclusão continuam confirmações locais. Nenhum estudo é criado pela consulta da central. |
| Notas | `40-app/14-mvp-notes.js`: `mvpNotesPersistenceMessage`, `mvpNotesMutate`, `mvpNotesRecomputeDirty`, feedback de cópia/exportação e alvo ausente | Abrir o painel existente; preservar rascunho, seleção e pasta. Não ler corpo da nota para gerar avisos. Status/prioridade existentes não são prazo nem alarme de vencimento. |
| Research — Laboratório | `40-app/18-galton-board/06-controller.js`: `showStorageStatus`, `announce`, integridade da amostra e estado de preferências | Falha/bloqueio de preferência e corpos descartados pelo limite seguro são informações do experimento. Não montar instância para verificar avisos. Pausa, fila, reset e conteúdo educativo não devem inflar a contagem a cada frame. |
| Research — demais áreas | `20-ui/23-research-views.js`: Ações/Stocks/REITs/Others em preparação | Não há eventos ou alarmes desses conteúdos não implementados. Preservar os estados vazios declarados. |
| Sistema — base ativa | `00-core/04-persistence.js`: `jpWealthLoadRecoveryActive`, `jpWealthPersistenceIsBlocked`, `jpWealthPersistenceOutcomeIsUnknown`, `jpWealthPersistenceFailure` | Recuperação de carga, falha de armazenamento/serialização, conflito entre abas e desfecho desconhecido têm significados distintos. Preservar os banners e bloqueios, mesmo depois de marcar lido. |
| Sistema — backup/pasta | `00-core/04-persistence.js`: `dgBackupStatus`, `dgBackupAgeDays`; `00-core/06-storage-fs.js`: estado da pasta; `40-app/16-storage-governance.js`: avisos e ações; `30-accounting/01-daily-ledger.js`: exportação/importação | Configurações → Backup e Recuperação. Não abrir seletor, pedir permissão ou confirmar existência do arquivo para atualizar o sino. Texto de sucesso do produtor não se torna prova física adicional. Na revisão cumulativa, consome o estado N2 de backup já reconciliado; UNKNOWN e data inválida não são tratados como confirmação válida. |
| Sistema — sessão | `40-app/07-finalize-session.js`: `showSessionNotice`, geração da base e finalização local/remota | Avisos existentes duram oito segundos na origem. Histórico da central não pode sobreviver como conteúdo da sessão anterior após substituição confirmada da base/finalização. |
| Sistema — referências cambiais | `10-domain/04-stop-statistics.js`: `updateFxRates`, atualização total/parcial/falha; `10-domain/08-usd-brl-quote.js`: `getCurrentUsdBrlQuote`, `usdBrlLastFailure`, `usdBrlOnChange` | Reutilizar estados e assinatura existentes, sem novo fetch. Taxas diárias de referência não são cotações spot em tempo real. TTL vencido indica consulta antiga, não necessariamente taxa econômica inválida. |
| Configurações — perfil local | `40-app/09-settings-modal.js`: `settingsProfileState`, `settingsProfileSetStatus` | Foto indisponível, prévia dirty, leitura inválida, conflito, recusa e desconhecido. Destino `account`; não copiar foto/nome para histórico nem liberar bloqueio ao ler. |
| Sistema — PWA | `40-app/06-app-icons.js` e `sw.js`; estado informativo de controller em Settings | Não existe produtor de Push/Notification API ou aviso de atualização pronta. `navigator.onLine` não comprova cache íntegro ou prontidão offline. Preservar o [ciclo PWA](PWA-UPDATE-LIFECYCLE.md). |

## Observação focal da interface

Quando não há função pura de estado, a central pode observar regiões de mensagem
já produzidas. Não é autorizada uma varredura de números, inputs, textarea,
conteúdo de Notas, ledger, avatar ou canvas. Renderizadores substituem alguns
nós; a inscrição precisa acompanhar apenas as raízes/seletores declarados,
sem duplicar observers durante navegação.

| Superfície | Seletores de mensagem/estado inspecionados |
|---|---|
| Persistência/sessão | `#persistenceRecovery`, `#persistenceAlert`, `#sessionNotice` |
| Backup/pasta | `#dgBackupBanner`; mensagens `.dg-status-line` dentro dos cartões de governança existentes |
| Forex | `#mcClearanceCard`, `#execClearanceCard`, `#onboardingIncompleteBanner`, `#execOnboardingGovNote`, `#statusBanner`, `#quarantineBanner`, `#breachNote`, `#fxFetchStatus` |
| Planejamento | `#fxpCreateErr`, `#fxpPlanningErr`, `#fxpActErr`, `#fxpCErr` |
| PF | `#finpesUnitNotice`, `#fbPendingBanner`, `#fbAllocExceeds` |
| Alladin | `#alladinReadOnlyBanner`; `.session-warning` e `.session-error` restritas à área/modal Alladin, não todos os diálogos da aplicação |
| Calendário | `#gdNewsStatus`, `#gdNewsNext`; `[data-ecal-role="freshness"]`/`[data-ecal-role="empty"]` sob as raízes de agenda existentes |
| NoCoda | `#ncStatus`, `#ncFormErr`, `.nc-field-err` (`#ncErr1`, `#ncErr2`, `#ncErr3`) |
| Pivots | `#pvNewStudyErr`, `#pvFormErr`, `.pv-field-err` (`#pvErr_<campo>`) |
| Notas | `#mvpNotesCopyLive`; atributo `data-dirty` de `#mvpNotesEditorBar`, sem ler o editor |
| Laboratório | `[data-galton-storage]` e seu estado `is-error`; `[data-galton-integrity]` quando não oculto |
| Perfil | `#settingsProfileStatus[data-state]` |

Essa tabela é inventário, não declaração de que todos os seletores serão
assinados simultaneamente. Adaptadores canônicos têm prioridade; observar o
mesmo fato pelo DOM e pela função não pode duplicá-lo. Nó desmontado não prova
que uma condição global foi resolvida. Mensagem oculta ou texto antigo retido
no DOM não é um novo evento. Estados de erro e dirty exigem data/identidade da
origem, não cópia integral da superfície.

Erros inline são situações atuais da superfície aberta; um nó remontado não vira
evento com horário inventado. `ncStatus.err` e o resumo do formulário representam
uma só mensagem NoCoda; avisos de cópia/exportação das Notas também conservam essa
semântica de mensagem atual. O sino não reproduz textos estáticos de vazio ou
informação de câmbio como incidente recém-ocorrido.

O espelho de `window.alert` preserva a chamada nativa, argumentos pertinentes,
retorno e ordem dos efeitos; não intercepta `confirm`/`prompt`. A captura não
executa comandos contidos em texto. Feedback de sucesso espelhado continua sendo
uma afirmação do produtor, não uma nova verificação de persistência ou entrega.

`alert` e `showSessionNotice` não fornecem metadados de origem do domínio. Esses
eventos são classificados em Sistema, com a tela/modal contemporâneo identificado
separadamente como **Exibida em…**. O filtro também encontra esse contexto; não é
prova causal de que uma operação assíncrona ou mensagem de outra aba nasceu na
tela aberta. Não há inferência por palavras, stack trace ou acesso a dados extra.

O card Forex combina clearance e `getOnboardingCompletionState`: `done=true` não
apaga seções ainda incompletas. O card de integridade Alladin consulta os leitores
de ledger, posições e saldo por caixa, interrompendo na primeira recusa; ledger
legível sozinho não certifica saldo. Não soma valores nem modifica classificações
financeiras. Avisos da pasta usam somente mensagens já produzidas pelo cartão ou
diálogo de exportação aberto, sem verificar permissões em segundo plano.

## Calendário: fonte, frequência e deduplicação

`ffNewsReadCache()` é a entrada comum. O sanitizador existente admite apenas
eventos High de USD/EUR/JPY/GBP; a fonte fornece semana corrente, título, moeda,
data, consenso e anterior. Não fornece calendário arbitrário mensal/histórico
nem campo de resultado `actual`. Não preencher essas ausências por inferência.

O pipeline existente tem TTL de 30 minutos, poll de cinco minutos e tique de
render de um minuto. `FF_NEWS_IMMINENT_MS` define o realce de 15 minutos.
`ffNewsRenderAll()` distribui atualizações; o evento `online` e a abertura da
agenda reaproveitam `ffNewsFetch(false)`. A central lê esse mesmo estado e
recalcula sua apresentação no ciclo local/visibilidade, sem nova chamada de rede
ou alteração de frequência da fonte.

Como o feed não fornece ID próprio, um evento deve ter identidade estável pela
combinação de moeda, data e título. Tick/countdown não cria novo evento; revisão
da fonte atualiza/invalida a identidade pertinente. Evento passado deixa a
condição de iminência; ausência real de eventos é diferente de cache vazio,
ilegível, velho ou fetch falho. Horário mostrado é o horário local adotado pelas
superfícies existentes. Não inventar bloqueio operacional associado à notícia.

Navegadores podem suspender temporizadores em segundo plano. A central não
promete aviso no segundo exato, som, entrega com aplicativo fechado, notificação
do macOS ou push. Não pede permissão de notificações nem instala novo worker.

## Memória, privacidade e invalidação

Histórico e marcações de leitura ficam somente em memória da abertura atual.
Não entram no backup, `S`, localStorage, sessionStorage, IndexedDB, cache,
telemetria, servidor ou logs de desenvolvimento. Recarga não restaura esse
histórico. Preservar estados do produto não exige persistir a central.

Mensagens nativas podem conter nomes, valores, caminhos e IDs que o próprio
aplicativo exibiu. O espelho local aumenta o tempo durante o qual esses textos
ficam visíveis; por isso deve limitar tamanho/quantidade, evitar conteúdo extra
e limpar a memória em substituição confirmada de base ou encerramento. Não
capturar senhas, argumentos de depuração, stack traces, foto, corpo de nota,
campos de formulário ou conteúdo financeiro não presente no aviso. Textos
externos são inseridos como texto, nunca HTML executável.

Recusa/cancelamento de Finalizar não é finalização. A invalidação segue a geração
e o resultado realmente observáveis dos fluxos existentes, sem alterá-los. Após
finalização/importação/wipe confirmados, itens e links da geração anterior são
descartados; mensagens antigas ainda no DOM não devem repovoar o histórico.
O eventual resumo novo de encerramento pertence à geração atual. Uma base em
recuperação permanece protegida mesmo com a central vazia.

## Validação e limites

O teste focal `tools/notification_center_test.py` deve demonstrar presença e
ação do sino, filtros, lido/não lido, dedupe/resolução, cobertura de fontes,
invalidação de sessão, foco/teclado, mobile/claro/escuro, conteúdo externo seguro
e ausência de escrita/rede extra. Deve diferenciar afirmação do produtor de
verificação real e preservar todas as decisões bloqueantes.

Regressões existentes pertinentes: `ff_news_cache_test.py`,
`studies_notes_persistence_contract_test.py`, `mvp_notes_test.py`,
`notes_launcher_test.py`, `settings_modal_test.py`, `storage_governance_test.py`,
`persistence_failure_test.py`, `persistence_recovery_test.py`,
`session_epoch_protocol_test.py`, `session_write_serialization_test.py`,
`finalize_session_test.py`, `galton_board_test.py`, `usd_brl_quote_test.py`,
`research_navigation_test.py` e os testes de domínio/clearance/Alladin/PF
aplicáveis. Listar teste não significa executá-lo; resultados reais ficam no
relatório identificado do candidate.

Este complemento não resolve A12 parcial, OPEN-05/V11/FCR/FEO, AUD-05/P2,
débitos estruturais nem falhas N2 de backup. Não concede aceite, integração ou
deploy. Operação no aplicativo aberto não comprova entrega em outros clientes,
outros navegadores ou fora desta sessão.
