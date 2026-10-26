# Dante — guia interativo do JP Wealth

O guia apresenta os controles reais do aplicativo. A entrada **Conhecer com Dante** na acolhida é opcional; começar do zero e restaurar continuam sendo escolhas separadas. Também é possível abrir **Configurações → Conhecimento → Guia do site**. A busca das Configurações encontra o guia por “tutorial”, “primeiros passos”, “aprender” ou “ajuda”. Abrir o aplicativo não inicia uma jornada nem cria um perfil.

Este contrato descreve o candidato de 24/10/2026 sob o [brief aprovado](../work/BRIEF-DANTE-20261024.md), com produto e controles em CHGs separados. [Identidade e voz do mascote](../branding/DANTE.md) orientam o texto; não alteram os contratos financeiros. Testes locais e aceite humano têm evidências próprias.

## Jornada e trilhas

O catálogo contém 63 lições em oito trilhas de autoria. A jornada contínua apresenta oito capítulos nesta ordem:

| Capítulo | Lições | Disponibilidade |
|---|---:|---|
| Primeiros passos | 6 | Recursos gerais |
| Research | 6 | Research |
| Planejamento | 4 | Planejamento |
| Forex | 7 | Forex |
| Finanças Pessoais | 7 | Finanças Pessoais |
| Ferramentas | 6 | Recursos de Ferramentas e disponibilidade das telas originais |
| Alladin | 8 | Alladin |
| Recursos gerais | 19 | Recursos gerais |

O índice muda o cursor somente por escolha explícita. Há um único ponto de retomada, com modo `journey` ou `track`; navegar pelo índice não marca etapas como lidas. As trilhas existentes continuam acessíveis pela API legada. A trilha Forex mantém oito lições de autoria, incluindo `forex-planning`; a trilha nova `planning` tem três. Na jornada, `forex-planning` aparece uma única vez, no capítulo Planejamento, e usa a disponibilidade de Planejamento. Seu ID e seu proprietário Forex permanecem para preservar o progresso anterior.

Uma etapa indisponível mostra seu requisito. A pessoa pode atravessá-la pelos controles explícitos, voltar ao índice ou escolher pular; o guia não ativa módulos, não marca leitura automaticamente e não confirma prática. Sem plano, as lições do Consolidado e de Preenchimento mensal explicam a dependência usando a entrada existente de Planejamento. Conhecer o app não exige criar uma conta ou um plano.

**Ir para esta tela** solicita a navegação original após o clique. Diálogos, guardas e proteções de rascunhos continuam pertencendo aos controles originais. O guia destaca o destino e oferece voltar, avançar, pular e pausar. Uma mudança de tela por fora do guia, um diálogo fora do percurso permitido, um controle ausente, a perda de disponibilidade ou a mudança da base pode pausar a orientação; resolva o fluxo original e retome quando quiser.

## Falas e acessibilidade

Cada lição possui `speech`, uma lista de balões editados para Dante, com até duas frases por balão. `instruction` preserva a referência detalhada da lição. O texto é local, sem chatbot, síntese de voz ou dependência externa.

A apresentação revela 30 caracteres por segundo. Durante a digitação, a primeira ação de avanço apenas revela o balão inteiro; outra ação passa à fala seguinte. No final das falas, avançar continua dependendo das condições da lição: ler, observar a ação original ou escolher pular. Revelar texto não registra leitura nem prática.

Com redução de movimento, cada fala aparece inteira. O leitor de tela recebe uma fala completa, sem anúncio de cada caractere. Atualizações do progresso e dos alvos não reiniciam o texto nem deslocam o foco. Teclas em campos editáveis conservam sua função original; o guia acompanha os hosts de diálogos e menus, sem assumir o Escape ou remover foco de uma edição.

Índice da fala e texto parcial ficam somente em memória. Pausa, ocultação, mudança de contexto, conflito e finalização cancelam o temporizador. Retomar na mesma sessão reapresenta integralmente a fala atual; recarregar começa pela primeira fala da lição salva. Esses estados não entram em schema, backup ou preferências pessoais.

## Leitura, ação e prática

A central separa leituras ou ações observadas, etapas puladas e práticas confirmadas. Pular não significa ler ou praticar. Uma pessoa pode concluir a orientação sem lançar valores, aceitar um termo, importar um arquivo ou cadastrar uma conta.

Só existem os observadores de prática já suportados: campos existentes do orçamento de Finanças Pessoais e salvamento de Notas. A prática é opcional e começa por escolha explícita. O orçamento pode salvar ao sair do campo; Escape cancela o rascunho antes da gravação. Notas exige Salvar. A confirmação de prática depende da ação original e da conferência do resultado persistido correspondente. Cancelamento, gravação recusada ou resultado desconhecido deixam a prática pendente. O guia não guarda o conteúdo usado nessa verificação.

Planejamento, agenda, calendário, bolsas, notificações e demais lições novas são leituras. Formulário, registro mensal e agenda apresentam também sequências completas de tarefa, que a pessoa pode acompanhar ou apenas ler; o guia não transforma essa explicação em uma prática confirmada. Na central de notificações, consultar não resolve uma causa; abrir o diálogo original pausa o guia. Agenda pessoal e eventos econômicos não se transformam em cobranças no sino. Calendário segue o dia selecionado, bolsas seguem Agora e os filtros são independentes. Cobertura pendente não confirma ausência de eventos ou fechamento de bolsa.

## Progresso local e compatibilidade

A chave auxiliar continua sendo `jpwealth_learning_guide_v1`, com `catalogVersion:1`, separada de `S`, dos fatos financeiros e do Backup Completo. Os 57 IDs originais e seus proprietários são preservados como registros compatíveis: 56 permanecem ativos e `tools-nocuda` é somente histórico, fora da jornada e do índice. Sua continuação vai para `tools-genetrix` apenas ao acionar Retomar, sem nova conclusão ou prática; abrir ou ler progresso não grava essa mudança. O envelope novo usa `schemaVersion:2` e acrescenta somente `mode:'journey'|'track'` aos campos do progresso anterior: versão de catálogo, trilha proprietária, lição, pausa e estados de leitura/pulo/prática. `trackId` identifica sempre o proprietário da lição, inclusive quando seu capítulo é outro.

O leitor aceita schema1 e o interpreta em memória, sem escrever durante o boot. Um cursor antigo retoma em modo trilha; um documento novo vazio usa jornada. A gravação de schema2 ocorre por ação explícita do guia. Não há migração de perfil, dados financeiros ou formato do Backup Completo.

O progresso não guarda valores, contas financeiras, nomes, texto de notas, credenciais, horários ou cursor de fala. Origens diferentes do app têm progressos separados. Pausar e recarregar preservam o ponto quando a gravação é confirmada. Se o navegador impedir leitura ou escrita, o guia informa uso somente na sessão.

Um documento inválido ou incompatível permanece intacto até **Reiniciar progresso**, por escolha explícita e com comparação e releitura da chave. Mudanças em outra aba pausam e reconferem o estado, sem sobrescrever silenciosamente o progresso concorrente. Uma remoção não confirmada é informada. Rever lições preserva os resultados anteriores.

Importar ou trocar a base pausa a orientação e invalida observações pendentes; importação não restaura progresso do guia. A limpeza auxiliar da sessão remove a chave e desliga callbacks antes do próximo boot. O boot seguinte rearma o controlador em pausa, sem iniciar navegação ou prática.

## Contratos de integração

O catálogo, progresso, apresentação e controlador permanecem scripts clássicos locais no manifesto, com suas posições relativas preservadas. O painel `learning-guide` cria um único `#jpwLearningCenter`. Service Worker e HTML portátil recebem os scripts e assets pelo builder oficial `tools/rebuild_monolith.py`; o ciclo conservador de atualização continua sob seu contrato próprio.

`JPWLearningCatalog` é imutável e expõe:

- `version:1` e `tracks:[{id,title,description,module,steps}]`, preservando autoria e APIs legadas;
- `journey:[{id,title,module,stepIds}]`, ordem editorial completa sem duplicar IDs;
- lições com os campos existentes, `speech:string[]` e `availabilityModule` opcional, que prevalece sobre o módulo da trilha para aquela lição;
- `speechAnchors:string[]` opcional, com um seletor por fala, e `followHosts:string[]` opcional, com os hosts concretos permitidos para acompanhar aquela tarefa.

Nas três lições `planning-form`, `planning-monthly` e `tools-agenda`, cada fala aponta para os controles reais do estado correspondente. A resolução procura um controle visível; quando ele ainda não existe ou está oculto, usa o host permitido aberto e, por fim, a âncora de entrada da lição. Esse fallback permite concluir a leitura sem abrir formulário nem criar fatos. Não avança formulário, preenche campos, move foco de edição ou interpreta texto como recibo de gravação.

O formulário acompanha escolher criar/editar e conta, ano/mês, capital/aporte, perfil, parada opcional, objetivos/moedas/câmbio, dois marcos de previsão, revisão, confirmação/cancelamento e falha. O mês acompanha conta/competência, resultado percentual ou USD, zero explícito, aporte com reais pagos, saque com reais opcionais, revisão/registro e fechamento separado, inclusive anterior pendente e fechamento invalidado. Agenda acompanha tipo, título, data civil ou instante/fuso, horário inexistente/ambíguo, conferência no próprio formulário, Salvar e resposta, editar, concluir tarefa e excluir com confirmação própria. A agenda não inventa uma janela de revisão que não existe na UI.

Hosts permitidos são estreitos: formulário de Planejamento usa `configure-choice`, `create` e `edit`, mais subdiálogos de perfil/parada somente com formulário create/edit aberto; Mensal usa diálogos de resultado/aporte/saque/fechamento e guarda da edição inline. A edição inline é um formulário na página. Agenda acompanha o modal `#calendarDialog` e os hosts lógicos de rascunho `#execEcal .calendar-form` e `#calendarDialog .calendar-form`. Um host lógico é o formulário ativo que precisa reservar espaço para o guia e preservar a edição; ele pode existir na página sem ser um modal. A ordem conserva o modal primeiro e os formulários depois para preferir o dono mais específico. Reinício, arquivamento, histórico, PDF e outros diálogos continuam fora desse acompanhamento e provocam a pausa original. Seletores com `:has()` ou vírgulas são seletores CSS completos; uma vírgula interna de `:has()` não separa hosts do contrato.

`JPWLearningGuide.startJourney({stepId?})` inicia a jornada mediante escolha; `start(trackId)` conserva o modo trilha; `resume()` respeita o modo salvo. O snapshot informa `mode`; o modelo da central apresenta os capítulos em `journey`. Nenhuma dessas APIs escolhe uma conta, preenche campo financeiro ou chama um escritor de domínio para concluir uma leitura.

## Validação e limites

O focal `node tools/dante_catalog_test.mjs` executa o catálogo sem DOM e verifica os 57 IDs/proprietários antigos, versão, ordem de capítulos, cobertura única de todas as 63 lições, disponibilidade independente de Planejamento, balões curtos, imutabilidade e ausência de novos observadores de prática. Também verifica sequência semântica das três tarefas, cardinalidade das âncoras por fala, allowlist exata dos hosts e presença dos hooks nas fontes reais de UI; isso não comprova que o alvo esteja visível no navegador. [Matriz editorial e limites](../validation/dante-20261024/LESSONS.md) relaciona as áreas cobertas às fontes reais. Esse teste não demonstra navegação no navegador, aparência ou persistência financeira.

Os contratos acumulados incluem `node tools/learning_foundation_test.mjs` e `node tools/learning_controller_test.mjs`. A regressão de navegador usa raiz candidata e cópia congelada das fontes reais anteriores ao guia:

```sh
python3 tools/learning_guide_test.py --root /path/to/project --baseline-root /path/to/frozen-source --out /path/to/guide-report.json --browser system
```

A raiz `--baseline-root` contém fontes reais, sem perfil ou dados pessoais; a suíte usa contextos descartáveis. Distribuições, offline, teclado, telas pequenas, redução de movimento, limites de persistência, revisão independente e gate completo exigem provas vinculadas aos bytes finais. Esta documentação não declara execução desses testes, publicação ou aceite humano.
