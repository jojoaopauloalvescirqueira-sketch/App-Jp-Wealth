# Dante — cobertura editorial do catálogo

Candidato de 24/10/2026, branch `codex/dante-guia-20261024`, base `a4bf278cd4dc38bbaa5b905ed17a79e33684fb67`. Escopo: catálogo, identidade editorial e contrato do guia. Os 57 IDs existentes e seus proprietários permanecem; sete leituras novas levam a 64 lições. O progresso continua separado da base financeira. Este registro não prova que um comando financeiro foi executado.

| Recorte | Lições da jornada | Controle/destino e fonte conferidos | Limite e precondição |
|---|---:|---|---|
| Primeiros passos | 6 | Dashboard, menu, localização e ajuda; catálogo e controlador do guia | LOCAL depende da origem; texto visível não comprova gravação |
| Research | 6 | `research-forex`, NoCoda, pivôs e áreas reservadas; catálogo e navegação | Só Salvar confirma estudos; espaços reservados não prometem análise |
| Planejamento | 4 | `forex-planning` e `planning-form`, `planning-consolidated`, `planning-monthly`; `#planning` como fallback, âncoras dos campos/previsão/revisão e hosts concretos em `06-planning/03-ui.js`; contrato `PLANNING.md` | `availabilityModule:'planning'` no ID legado; Consolidado e Mensal requerem plano, sem forçar cadastro ou nova prática |
| Forex | 7 | Contas/contexto, Desempenho, Operação, Histórico, Contabilidade e Reservas; destinos existentes | Não escolhe conta/período nem declara elegibilidade; Checklist salva durante respostas |
| Finanças Pessoais | 7 | Visão geral, orçamento, receitas, despesas, dívidas, comparação e cenários | Diferencia mês virtual e mês registrado; orçamento pode salvar ao sair do campo |
| Calendário | 2 | `tools-calendar` e `tools-calendar-coverage`, `#execEcal`, `19-calendar-agenda.js` e `CALENDAR-AGENDA.md` | Calendário mensal e widget FF têm coberturas distintas; filtros/fuso/data podem alterar leitura |
| Agenda | 1 | `tools-agenda`, `#execEcal`, `19-personal-agenda.js` e `19-calendar-agenda.js` | Salvar solicita gravação; confirmação depende da resposta original; Fechar preserva rascunho; Cancelar descarta; nenhum observador de prática novo |
| Bolsas Globais | 1 | `tools-markets`, `#marketHoursTool`; seção real em `index.html`, `31-tools-services.js` e `31-market-hours/03-view.js` | Agora e filtros independem do dia da agenda; Sem confirmação não significa fechada |
| Outras ferramentas | 3 | Nocuda Tool, Stoikus — MT5, Estrutura Normativa; destinos existentes | Validação não cria fato; download de fonte não comprova execução MT5 |
| Alladin | 8 | Estado e sete visões legadas | Congelamento preservado; estorno exige comando e confirmação próprios |
| Notas e configurações | 16 | Notas, salvamento, 14 entradas legadas incluindo MiniGames | Prática de nota só com escritor/resultado original; conta local não é corretora |
| Backup e sessão | 2 | Backup e Recuperação, Finalizar sessão | Download solicitado não prova arquivo salvo; leitura não importa nem encerra sessão |
| Notificações | 1 | `general-notifications`, `#headerNotificationsBtn`, `18-notification-center.js` | Leitura; diálogo original pausa guia; consultar aviso não resolve causa; agenda não alimenta cobrança no sino |

A trilha proprietária `forex` continua com oito lições. A jornada retira somente a referência de `forex-planning` do capítulo Forex e a coloca uma vez no capítulo Planejamento, junto das três leituras novas de proprietário `planning`. A trilha `general` mantém as 18 lições originais em sua ordem e acrescenta notificações ao fim; `start('general')` continua na ação de abrir Notas. Ferramentas conserva Calendário como primeira lição e a ordem relativa das quatro lições antigas.

## Observação e persistência

Não foram criados tipos de ação nem prática. A expansão após a revisão independente completa os percursos de formulário, registro/fechamento mensal e agenda sem acrescentar IDs ou prometer ensino integral de todas as tarefas do app. Permanecem ações `menu`, `help`, `notes`, `session` e práticas `budget`, `notes`, sob os observadores existentes de `28-learning-guide.js`. As sete lições novas são `kind:'read'`; Entendi reconhece leitura, e Pular registra uma escolha distinta. A instrução detalhada existente continua no catálogo; `speech` fornece balões editados, de até duas frases e 280 caracteres no focal, para todas as lições.

## Provas deste recorte

`tools/dante_catalog_test.mjs` roda o arquivo real em VM sem DOM, com lista independente dos 57 IDs/proprietários antigos. Verifica versão 1, ordem dos oito capítulos, referência única de todas as lições, exceção de disponibilidade de Planejamento, texto curto/plain text, observadores permitidos, leituras novas e imutabilidade.

RED: contra a cópia do catálogo anterior ao delta, a expectativa `continuous journey is required` falhou por ausência da jornada; classificação `PRODUCT_FAIL` referente ao comportamento novo aprovado ainda ausente. GREEN: o mesmo teste no catálogo novo terminou `PASS`, 57 IDs antigos, 64 lições e oito capítulos. Os logs do recorte ficam em `/private/tmp/jpw-dante-20261024/reports/catalog-red.log` e `catalog-green.log`.

Contraprovas sobre cópias descartáveis removem `speech`, duplicam um ID na jornada e alteram o proprietário de uma lição antiga. Cada cópia precisa ser rejeitada pelo mesmo focal; resultados próprios em `catalog-counterproofs.log`. As contraprovas não alteram o catálogo de produto.

A validação de catálogo não executa navegação, diálogos, persistência financeira, typing, acessibilidade ou renderização. Focais de controlador, Foundation, navegador, distribuições, FULL, revisão independente e aceite humano são responsabilidades da validação integrada, com seus próprios recibos. Resultado de fonte não é aceite visual ou financeiro.

## Complemento de tarefas completas após revisão independente

As três lições continuam `kind:read`, com propriedades opcionais `speechAnchors` e `followHosts`. Há uma âncora para cada fala (13 no formulário, 15 no mês, 13 na agenda), fallback na entrada e hosts concretos delimitados. Nenhum novo writer ou observador de prática foi criado.

| Lição | Percurso editorial e tipos de caso | Hooks reais de UI | Fronteira |
|---|---|---|---|
| planning-form | escolha explícita criar/editar/conta; ano/mês, capital/aporte, perfil, parada opcional, objetivos/moedas; previsão com dois marcos; revisão, confirmar/cancelar; erro/conflito/indeterminado | `pl-native-ano/mes/saldo/aporte`, `openProfiles`, `stopOpen`, `custoValor/sonhoBRL`, `forecastArea`, `data-pl-native-review/success` | somente diálogos configure-choice/create/edit; perfil/parada exigem formulário create/edit aberto; nenhum reinício/arquivo/PDF/histórico |
| planning-monthly | conta/mês, percentual/USD, lucro/prejuízo/zero explícito/ausência, aporte+BRL obrigatório, saque+BRL opcional, revisão/registro, fechamento separado, anterior pendente, correção e fechamento invalidado, recusa/UNKNOWN | `data-pl-account/month`, `data-pl-inline-open/editor/review`, `name=unit/value`, `confirmFlows`, `closure-save-result`, `closure-previous` | formulário inline na página; só diálogos result/contribution/withdrawal/finalize e guarda contextual inline; correção narrada não autoriza abrir histórico pelo guia |
| tools-agenda | criar/editar tipo+título+data; tarefa civil/compromisso dia inteiro/instante+fuso; horário inexistente/ambíguo; conferir formulário e salvar; confirmação/recusa/conflito/UNKNOWN; concluir tarefa; excluir/manter; cancelar/fechar | `.calendar-form`, `name=kind/allDay/startTime/timeZone`, `.calendar-form-ambiguities/errors`, ações new/edit/save-form/refresh-revision/remove-form/confirm-remove/cancel-form, `data-calendar-complete` | hosts lógicos `#execEcal .calendar-form` e `#calendarDialog .calendar-form`, além do modal `#calendarDialog`; reservam fluxo no formulário ativo e não inventam etapa de revisão nem recibo; conclusão e exclusão pertencem aos comandos originais |

O focal novo foi primeiro `PRODUCT_FAIL` por faltar a sequência de campos no catálogo anterior à expansão (`catalog-tasks-red.log`). Depois passou com os três percursos e a mesma contagem 64 (`catalog-tasks-green.log`). Uma asserção auxiliar inicial procurou o literal `data-pl-inline-editor` onde a UI cria a propriedade via `dataset.plInlineEditor`; essa falha foi `TEST_HARNESS_FAIL`, corrigida para confrontar o hook real sem alterar o produto.

Além das contraprovas anteriores, cópias descartáveis devem ser rejeitadas quando omitem previsão com dois marcos, trocam ausência por zero, omitem o caso de horário inexistente/ambíguo, quebram a cardinalidade de âncoras ou permitem host genérico. Oráculos: conteúdo e ordem das fases, uma âncora por fala e allowlist exata dos hosts. Logs `catalog-tasks-counterproofs.log`. Esta prova de fonte não substitui a navegação real entre campos/diálogos, preservação de rascunho, medição visual ou persistência; a validação integrada possui recibos próprios.

## Host lógico do rascunho da agenda

O focal real identificou que o guia flutuante podia cobrir Dia inteiro após Novo ou troca de Tipo. A allowlist da agenda passou a ser exatamente `#calendarDialog`, `#execEcal .calendar-form`, `#calendarDialog .calendar-form`, nessa ordem. O modal continua sendo o host de diálogo; o formulário é um host lógico de edição, inclusive no workspace sem modal, para o consumidor reservar fluxo e manter campos acessíveis. A correção de layout/reancoragem pertence ao controlador e à apresentação, com seus recibos próprios; o focal de catálogo comprova somente a allowlist e a rejeição de host genérico/omissão do formulário. Os 64 IDs permanecem.
