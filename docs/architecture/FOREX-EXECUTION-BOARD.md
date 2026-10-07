# Forex — Execution Board

**Contrato atual do candidate local de 2026-10-05:** [Proporções de planilha](#proporções-de-planilha--candidate-2026-10-05), sobre [Operação como planilha](#operação-como-planilha--candidate-2026-10-01). As seções datadas abaixo preservam contratos e evidências históricos; não descrevem uma aprovação da revisão atual.

Campanha FOREX-EXECUTION-BOARD-01, base integrada `594c86ebf13661d0e5846a3b64a0288631fd938d`, branch `codex/forex-execution-board-20260915`. Contrato e limites em [CHG/CTX](../work/CHG-FOREX-EXECUTION-BOARD-20260915.md). Estado: revisão local, validação e aceite separados. Recibos de execução/fingerprint/recovery em `/Users/joaopauloalves/.codex/forex-execution-board/20260915/evidence/`.

## Autoridade e responsabilidade

Constituição → Estatuto V11 → Anexo nos elementos delegados → `JPWForex.policy`/`engine` → projeção → UI. Parâmetros normativos permanecem inalterados; as projeções operacionais aprovadas abaixo ampliam o domínio sem substituir a avaliação normativa. A planilha orienta a organização da informação; suas fórmulas divergentes e incompletas não são oráculo. Registrar fato continua distinto de autorizar execução.

`10-domain/18-execution-board-model.js` é projeção sem escrita. `read` resolve a seleção e chama o modelo; `project` agrega fixtures/contexto explícito; `instrumentInputs` compartilha contratos/conversões com os leitores de risco; `closedNetResult` aplica o tratamento de custos declarado. `20-ui/30-execution-board.js` apresenta resultados e rascunhos RAM. Não contém fórmulas financeiras. `19-execution-market.js` coordena o provedor diário, usando os comandos de `00-forex-state.js`.

## Identidade e escopo

Cada conta cadastrada pode conservar uma operação ativa em seu próprio período. Sem seleção explícita, a única Mestre cadastrada é proposta; ausência ou ambiguidade exige seleção. A seleção operacional não é a seleção analítica do Consolidado. SI, saldo contábil e equity são observações distintas por conta/período, com fonte e instante; ausência não é zero. Responsáveis de onboarding são declarados da sessão, não cadastro por conta.

Registros conciliados exigem conta, período, moeda, operação, instrumento e identidade suficientes. Ordens anuladas/rascunhos não viram posições. Ausência de identidade, papel, resultado ou custos não vira zero. Grades LEGACY conservam índices/nomes; não são migradas automaticamente para Gênese, Ataque, Intermédio, Defesa, Cuidado e Preparação.

## Leituras financeiras

Risco de stops é monetário positivo; resultado realizado tem sinal. Custos `INCLUDED_IN_RESULT` não são somados de novo; `SEPARATE_FROM_RESULT` exige valor assinado e soma uma vez. Compensada pelas defesas = risco aberto − líquido das ordens explicitamente DEFENSE; compensada da operação usa todos os encerramentos conciliados. Resultado negativo amplia a leitura econômica, ganho pode torná-la negativa. Isso não reduz RC normativo nem amplia orçamento.

RC, alavancagem normativa, DD, fases, capacidade prudencial e stops normativos vêm do motor. A alavancagem normativa usa nocional bruto / min(SI,equity). DD22% é encerramento estatutário, não stop-out da corretora. As faixas de DD não são orçamento de stops. A capacidade prudencial restante não é margem da corretora ou admissão autorizada.

Referências de lotes: fatores vigentes P-12b × min(SI,equity) / nocional de um lote na moeda da conta. Mostram precisão teórica, não volume arredondado para execução. Conversão usa caminhos identificados de moedas, observações manuais ou referências diárias datadas; preço legado mostrado não se torna conversão observada. Cada perna preserva origem e data. Contrato, conversão ou base ausentes impedem cálculo. Restrições de instrumentos permanecem.

ATR55/660 em unidades de preço, H4, pertence ao instrumento/conta/período. VRM/stop mínimo/múltiplo usam esse contexto. A observação global anterior permanece legada e não alimenta automaticamente todos os pares. O formulário do Motor grava agora o instrumento selecionado. Raiz-N não recebe fator fixo da planilha.

Resultado completo do período permanece indisponível: ledger diário não captura moeda e cobertura reconciliadas suficientes. Resultado desta operação é apresentado separadamente. Lucro Técnico, MOR, P14/P17/P18 e fator P21 permanecem ausentes conforme suas lacunas específicas. O pacote não encerra A12 parcial, OPEN-05/V11/FCR/FEO, AUD-05/P2 nem concede homologação financeira.

## Escrita e rascunhos

Input/change só alteram Map em RAM. Salvar linha valida campos e envia um único `operationRecordOrders` com versão/identidade esperadas e um motivo para toda a correção. Versão confirmada divergente recusa; cancelar relê a linha. Correção preserva revisão anterior. Fechamento continua via fluxo explícito de resultado/custos. Não há autosave por tecla.

Render de cotações/métricas não reconstrói inputs da tabela. Navegação para outra área ou Motor oferece Salvar, Descartar ou Permanecer; checklist e Settings podem abrir mantendo o rascunho. Exclusão que mudaria índices resolve rascunhos antes. Finalizar Operação e Finalizar Sessão resolvem rascunhos antes dos fluxos; descarte definitivo só após commit confirmado. Não existe promessa de recuperação de RAM após recarga; beforeunload avisa quando possível.

## Observações e referências diárias

Extensões opcionais de `S.forex`, sem novo store nem normalização destrutiva: `instrumentContexts` e `dailyReferences`, ambas versionadas. Primeira ausência não implica criação em render. Comandos usam `mutate`/epoch/concorrência/confirmação existentes. Schema futuro não é convertido. Importação do backup rejeita versão incompatível antes de trocar a base.

`recordInstrumentContext` vincula conta/período/instrumento/moeda e componentes preço, ATR, contrato e conversão; origem, instante, motivo e expectedRevision acompanham o ato. Campos vazios da UI não apagam componente confirmado. Revisões anteriores são preservadas. Snapshot de ordem inclui a observação disponível e referência diária no registro, sem afirmar admissão pré-execução.

Frankfurter permanece referência diária, consultada localmente pelo provedor existente. Data da taxa e horário de consulta são distintos; taxa/par/data inválidos são rejeitados. Observações manuais têm precedência e não são sobrescritas. `S.instruments.preco` antigo não é atualizado como se fosse preço de execução. Não se obtêm equity ao vivo ou ATR automaticamente.

O controlador coordena requisições, timeout, respostas parciais e cancelamento. Lote válido é gravado uma vez; repetição das mesmas taxas/datas/identidades não regrava nem altera audit ou fetchedAt confirmado. A hora da última consulta sem alteração é transitória. Recusa conserva prévia RAM e oferece repetição explícita da gravação; UNKNOWN impede nova tentativa cega. Epoch/revisão impedem respostas tardias após troca/finalização de reintroduzir dados. Cancelamento libera controladores; não confirma atualização.

## Backup, finalização e recuperação

Backup completo contém contextos confirmados por conta, períodos, lançamentos, observações e snapshots de ordens. Arquivo original e segredos não são incluídos. O backup completo preserva rascunhos recuperáveis para revisão, sem lançá-los automaticamente. Finalizar Sessão encerra processos temporários e desbloqueios, preservando contas, operações e históricos confirmados para retomada. Snapshot do histórico mantém os dados efetivamente capturados; não completa passado com cadastro atual.

Falha/quota/UNKNOWN seguem os escritores existentes: nenhuma mensagem de sucesso antecipada; não realizar retry cego. Usar cópia de recuperação e fluxo existente para desfecho desconhecido. Rollback de código só no delta desta worktree, com baseline externo e hashes; nenhuma autorização para reset/stash/limpeza de outras árvores.

## Verificação

Focais novos: `forex_execution_projection_test.py`, `forex_execution_market_test.py`, `forex_execution_board_test.py`. Regressões adaptadas somente quando a expectativa antiga era autosave/geometria ou ATR global; contraprovas de persistência/custos/identidade permanecem. FULL, browser, PWA e portátil seguem ferramentas existentes, sem mudar gates. O relatório externo informa resultados reais, falhas intermediárias e identidade exata; a existência deste documento não é evidência de PASS.


## Preparação e importação — 2026-09-16

Contrato [CHG-FOREX-IMPORT-OPERATION-20260916](../work/CHG-FOREX-IMPORT-OPERATION-20260916.md), base `61120ec`. Os atalhos do painel abrem importação HTML/PDF, cadastro manual e preparação da conta/período. As seis fases permanecem descobertas mesmo sem contexto; nesse caso a tela oferece preparação, sem criar conta, período ou ordem em render. A grade LEGACY de quatro fases conserva sua identidade. Em telas até 767 px cada linha usa os mesmos campos/eventos em uma ficha vertical.

`JPWFXConsolidatedUI.openAccountSetup` coordena confirmações separadas: cadastro, período, e observação financeira opcional. O relatório sugere identificação e exibe saldo/equity e referência documental. SI e saldo contábil de abertura permanecem vazios até declaração explícita. A data/hora e o fuso da equity exigem conferência. Seleção de período já existente não cria outro período; nenhum ticket importado vira ordem manual ou recebe fase automaticamente. Os comandos canônicos continuam responsáveis por invariantes financeiros e persistência; o controlador confere sessão, conta, agregado e leitura após gravação. Fechar preserva apenas etapas que já foram confirmadas.

A importação HTML detecta convenção numérica pelos campos reconhecidos, independentemente do idioma. Formato ambíguo exige escolha decimal com ponto/vírgula; formatos incompatíveis são recusados. Datas dia/mês ou mês/dia exigem evidência inequívoca ou escolha explícita. Valores originais e interpretação aparecem nas mensagens de revisão, sem executar HTML importado.

O leitor PDF usa os mesmos recursos PDF.js fixados localmente. Em `file://`, `src/vendor/pdfjs/runtime-assets.js`, gerado pelo comando oficial, carrega sob demanda os módulos incorporados; HTTP/PWA continuam usando os recursos locais originais. O portátil incorpora os recursos. Não há CDN ou OCR. PDFs textuais aceitam o resumo reconhecido e tabelas MT5 com colunas separadas e cabeçalhos reconhecíveis/repetidos em cada página. Identidades divergentes, transações ilegíveis e falta de cabeçalho são recusadas. Limites: 32 MiB de arquivo, 200 páginas, 250 mil itens e 12 MiB de texto, com timeout e cancelamento.

O envelope público `mt5-summary-pdf-v1` permanece compatível; a indicação `PDF_TEXT_TABLES` distingue tabelas extraídas de um resumo sem tickets. A completude do histórico PDF não é presumida. Dados ausentes permanecem indisponíveis. Não se promete reconhecimento de PDFs digitalizados ou de qualquer layout de corretora.

Verificações específicas: `fx_import_numbers_test.py`, `fx_pdf_local_test.py`, `fx_account_setup_test.py` e `fx_import_operation_test.py`. A última usa a interface real nas seis fases e confere recarga, conta distinta e backup completo em outra sessão descartável, com versões modular/portátil, arquivo/HTTP e larguras 390/768/1440. Resultados e capturas estão no relatório do candidate, separados de aceite e integração. O contrato atual de backup completo inclui rascunhos recuperáveis para revisão; nunca os lança automaticamente.


## Contrato tabular — 2026-09-22

Candidate isolado baseado em `a62258f`, autorizado pelo plano integral; contrato [CHG-FOREX-EXECUTION-TABLE-20260922](../work/CHG-FOREX-EXECUTION-TABLE-20260922.md). Esta seção atualiza apresentação, identidade e projeções; a fotografia de 2026-09-15 acima permanece histórica.

Forex apresenta Dashboard, Execution Board, History, Contabilidade, Management Accounts, Planejamento e Reservas. History hospeda exclusivamente operações completas finalizadas. Management Accounts reúne Contas e Fator de Correção. Os quatro layouts usam os mesmos destinos/controladores e guardas de rascunhos.

A Board apresenta contexto da conta/período, resumo operacional e tabelas por fase. Grupos de colunas distinguem identidade, geometria, cálculo, exposição, resultado e gravação. ID e HASH fixos no desktop; no celular somente ID permanece fixo. A tabela rola horizontalmente, sem conversão para cartões. Edição e diagnóstico recebem orientação na interface. Cabeçalhos, valores calculados e campos editáveis têm apresentação distinta.

| Leitura operacional | Base e regra |
|---|---|
| Hard Stop | SI × 0,78 + movimentações líquidas conciliadas; piso de equity, não controle remoto da corretora |
| Total Exposure | Risco positivo até o stop das ordens abertas, com direção e stop favorável respeitados; percentual sobre saldo contábil atual |
| Compensed Exposure | Risco aberto menos resultado líquido realizado exclusivamente DEFENSE; perdas ampliam, ganhos reduzem; custos uma vez |
| Alavancagem utilizada | Nocional bruto das posições abertas na moeda da conta / saldo contábil atual, sem compensar BUY/SELL |
| ATR Multiple | abs(entrada − stop) / ATR55 H4, sem usar preço atual |
| VRM | ATR55 H4 / ATR660 H4, razão em × |
| Raiz-N declarado | ATR55 H4 × √N × F; percentual divide a distância pela entrada |

Pendentes são apresentados separadamente e permanecem no risco comprometido normativo aplicável. RC, limites e alavancagem normativa não são substituídos pelas projeções sobre saldo. Conversão do risco usa moeda de cotação; nocional distingue moeda-base. Dados ausentes geram leitura indisponível e motivo, nunca zero artificial.

`executionBoard.previewOrder` é puro: atualiza somente geometria, ATR e Raiz-N da linha em RAM. Células alteradas são identificadas como não salvas; exposição e totais confirmados só mudam após writer aceito. `displayRows` inclui rascunhos para geometria; `rows` conserva somente fatos registrados para agregação.

`brokerHash` é texto opaco, sem conversão numérica nem unicidade global. Novas ordens abertas/fechadas exigem ID manual e HASH. Pendentes exigem ID e recebem o marcador `identityContractVersion:1`, que exige HASH ao abrir. Ordens legadas sem marcador continuam consultáveis, complementáveis e fecháveis; IDs técnicos não mudam. Importação MT5 não presume que ticket corresponde ao HASH.

`S.forex.executionDiagnostics` é opcional, schema1, por conta/período/instrumento; N inteiro positivo H4 e F positivo são declarados independentemente para uma e duas semanas. Não há defaults. O comando `recordExecutionDiagnostics` valida revisão/epoch e grava com origem declarada, data e motivo; falha conserva rascunho, desfecho desconhecido segue recuperação existente. Campo omitido preserva horizonte; `null` remove explicitamente. Esses cenários não modificam P21, stop ou autorização de execução.

Backup Completo valida a extensão e HASH antes de escrever, aceita ausência em backups antigos e preserva revisão/declaração. `calculationInputs.executionDiagnostics` captura o cenário disponível em cada registro ou correção factual da ordem. Finalizar a operação preserva a última versão confirmada de cada ordem; não consulta o cenário atual para completar ou recalcular o passado. Todos os schemas existentes permanecem nas versões atuais.

Focais adicionais: `forex_execution_identity_test.py`, `forex_execution_table_test.py` e `forex_navigation_table_test.py`, além de projeção, motor, histórico, persistência e gate completo. Somente fixtures sintéticas; recibos externos registram build, hashes e limitações reais. Implementação local não equivale a integração, publicação ou aceite visual.


## Gestão centralizada — candidate 2026-09-23

Ordem Forex: Dashboard → Contas e Período → Execution Board → History → Contabilidade → Planejamento → Reservas. Os quatro layouts reutilizam nós/rotas; aliases `contas`, `forex-account` e `motor` permanecem. A preferência de ordem dos seis módulos N1 não é regravada.

A Board mostra conta/período/operação e informações operacionais, com `Gerenciar em Contas e Período`; não possui cadastro nem seletor mutante de conta. A nova página separa conta examinada em RAM de `operationalSelection`. `selectOperationalContext` valida cadastro único e par conta/período antes de mudar ambas seleções, sem persistência. Rascunhos são resolvidos antes de trocar contexto ou navegar. Respostas tardias conferem escopo, geração e tentativa. Recarregar conserva o fallback anterior Mestre única/período atual, não promete última seleção persistida.

## Operação como planilha — candidate 2026-10-01

Contratos separados: [interface N1/A2](../work/CHG-JPW-EXECUTION-WORKBOOK-20261001.md) e [referências do Motor N3/A4](../work/CHG-JPW-LOT-REFERENCES-20261001.md). A aprovação do plano permite este delta local; não homologa parâmetros nem autoriza execução, integração ou publicação. O snapshot externo preserva as 182 alterações anteriores. Estatuto, Anexo, motor normativo, schemas, escritores e pacote MT5 não são alterados.

A sequência padrão é contexto operacional → resumo confirmado → ferramentas → ordens. Esta superfície adota esse fluxo visual e de teclado; o objeto salvo de personalização do Editor, seus IDs e tamanhos permanecem íntegros, sem migrar ou regravar a ordem antiga. A tabela contínua possui colunas próprias para identificação, instrumento, direção, papel, lote, entrada, SL, TP, oito diagnósticos, risco nominal, risco percentual, estado e ações. Fases são separadores de linhas; vazio oferece Adicionar ordem. Apenas ID e instrumento ficam fixos horizontalmente. A grade contém sua própria rolagem; abaixo de 768 px de área útil, as mesmas linhas, inputs e comandos são apresentadas em lista. HASH, custos, resultado, motivos e versões continuam nos detalhes da mesma ordem. Não há formulário concorrente nem linha artificial preenchida.

Matriz, Raiz N e Motor ocupam abas de uma superfície única. A Matriz diferencia fase da conta e fase factual da ordem; grades LEGACY não são convertidas. Raiz N conserva ATR55 H4 e N/F declarados por horizonte, sem defaults, e calcula o percentual da linha sobre a entrada. ATR660 continua reservado ao VRM. Nenhuma observação vem automaticamente do Excel, vault ou MT5.

O Motor apresenta quatro métricas, com fator, fonte, unidade, base e memória: `initialNormal`/`initialRestrictive` usam Fator × SI ÷ nocional por lote; `currentNormal`/`currentRestrictive` usam Fator × min(SI,equity) ÷ nocional por lote. Os aliases anteriores `normal`/`restrictive` conservam o resultado corrente. SI positivo permite a referência inicial mesmo sem equity; nesse caso o teto corrente permanece indisponível. Contrato ou conversão ausentes impedem o cálculo. USC conserva numerador e base na mesma moeda. Não há arredondamento de execução, preenchimento de ordem ou lote autorizado; P-14/P-17/P-18 e demais lacunas permanecem explícitas.

O alias `motor`, chamadas antigas de seleção e seus atalhos abrem `forex-operation`/`panel` e `executionBoardUI.openTool('motor')`, após os guards atuais. O host antigo conserva IDs de compatibilidade, permanece oculto e não edita o catálogo global. Explorar ferramentas não grava preferência financeira.

Digitar modifica somente o rascunho RAM e recalcula geometria/ATR/Raiz N pelo núcleo existente. Risco e totais continuam na versão confirmada até writer aceito. Salvar, cancelar, corrigir, fechar e anular reutilizam os comandos anteriores. Redesenhar e rolar não materializam dados; mudança de contexto ou versão conflitante recusa gravação. Rascunhos, foco e campos não são perdidos ao trocar de ferramenta.

Novos focais: `forex_execution_workbook_test.py` (tarefas e responsividade reais em navegador sintético) e `forex_lot_references_test.py` (modelo produtivo e duas bases). Expectativas antigas de apresentação podem acompanhar o contrato; números, fixtures, gates, classificações, clocks e writers permanecem. Recibos de execução, capturas, fingerprint e rollback ficam no relatório externo do candidate. Testes locais não equivalem a aceite humano ou homologação normativa.

`accountProfileContext` diferencia perfil cadastral atual, destino próximo período e referência capturada no período consultado. Ausência histórica não usa perfil atual nem Base. O cabeçalho Forex e Board leem contexto; simulações globais continuam globais. Perfis não substituem risco efetivo: a política V11 atual continua avaliando observações e ordens; P30 permanece PENDING e replicação bloqueada. Nenhuma fórmula foi alterada.

`Contas e Período` reutiliza a conciliação histórica e observações da conta examinada; registrar observação ali não seleciona a conta na Board. Memória de Correção, Firewall e aplicação de lote continuam no domínio existente, sem inputs cadastrais diretos por tecla. Períodos são atuais/anteriores/pendentes; não foi criado encerramento formal.


## Proporções de planilha — candidate 2026-10-05

Implementação delimitada pelo [CHG de produto](../work/CHG-JPW-OPERATION-PROPORTIONS-20261005.md); expectativas de apresentação no [contrato de testes separado](../work/CHG-JPW-OPERATION-PROPORTIONS-TEST-20261005.md). Base a47ebee preservada; resultado local sujeito à revisão, gates e aceite humano.

A grade mantém vinte colunas, ID/Instrumento fixos e rolagem própria. Desktop com ponteiro fino adota 14 px e alvos de 36 px na preferência padrão; toque e lista por largura útil inferior a 768 px usam 16 px e 48 px. A preferência de fonte escala texto, controles e colunas; zoom não é neutralizado. Se ID/Instrumento longos deixarem menos de 320 px úteis para os demais campos, a grade usa a mesma lista responsiva, preservando os controles e os valores; cancelamento explícito recalcula as larguras. Cabeçalhos e linhas crescem quando o conteúdo exige. Não há persistência nova de densidade.

Fases mostram nome, quantidade, Diagnósticos e + Ordem em uma faixa; fases vazias não criam outra linha. Detalhe fechado não reserva espaço. Campos de HASH, custos, resultado e justificativa continuam montados uma vez, no detalhe da própria ordem, aberto automaticamente quando uma validação requer o campo. Salvar e Cancelar dependem de edição e dos bloqueios existentes. Ações preservam nomes acessíveis e foco útil depois de salvar/cancelar. Rascunhos RAM e comandos do domínio permanecem os mesmos.

Um estado Não salvo por ordem evita duplicação de mensagens; cabeçalhos distinguem diagnósticos de prévia e risco confirmado. Não arredondar ou ocultar valores para obter o layout. Funções financeiras, registros, schemas e MT5 não mudam. O focal `tools/forex_execution_proportions_test.py` complementa o workbook; oráculos financeiros antigos permanecem e falhas anteriores são reportadas sem reclassificação. Recibos, medidas, capturas, fingerprint e rollback são externos ao produto.

## Candidate visual — risco por ordem (2026-10-05)

Contrato CHG-JPW-FOREX-VISUAL-RISK-20261005, base ac3a2fa. O cartão de exposição passa a incluir barras horizontais das ordens abertas confirmadas do contexto. O consumidor usa `rows[].operationalRisk` e o total `operational.exposure`; nominal e percentual sobre saldo contábil registrado são os mesmos da grade. Nunca usa risco percentual SI como substituto. Pendentes conservam sua parcela separada.

Mostrar inicialmente as seis maiores ordens calculáveis e dar acesso a todas e aos motivos das indisponíveis. Zero confirmado difere de ausência; cobertura incompleta não permite mostrar subtotal como total. Barra é um acesso ao detalhe já existente, sem criar editor ou comando de gravação. Rascunhos não alteram barras; confirmação de salvar atualiza a leitura.

Expansão é estado visual transitório da sessão. Em largura útil >=960px, resumo e barras ficam lado a lado; de768 a959px empilhados; abaixo de768px começam recolhidos. Preferência explícita de expansão sobrevive resize/navegação sem nova chave persistida. A grade mantém vinte colunas e seu contrato14/36desktop16/48toque. Domínio, contexto, unidades e persistências permanecem inalterados; DD14 conhecido segue fora do delta.

## Candidate: registros documentados da operação (2026-10-05)

CHG-JPW-FOREX-PROFESSIONAL-RECORDS-20261005 acrescenta `operationRecords` ao read model, exclusivamente para apresentação. Não altera fórmulas, dados salvos, versões de schema ou comandos. O envelope de `operationHistory` permanece schema1; a versão2 de cada snapshot de operação é um contrato distinto.

A cronologia concilia conta, período, moeda e identidade de operação. Usa criação local preservada, revisões imutáveis das ordens e snapshots de finalização do mesmo contexto. Horários, razões ou revisões ausentes permanecem desconhecidos; duplicação/conflito não são reconciliados por inferência. Eventos locais não certificam sequência ou horários da corretora.

O disclosure Registros da operação permite selecionar a ativa ou uma encerrada do período em RAM, abrir detalhes somente leitura e localizar uma ordem corrente após reconferir sua identidade. Consulta não remonta os campos de edição nem atualiza valores confirmados por rascunhos; rolagem e seleção são preservadas quando a projeção não muda. O seletor não aplica contexto operacional. Vinte colunas e proporções 14/36 desktop e16/48 toque permanecem.

Resultados dos testes, auditoria e fingerprint pertencem à entrega externa `outputs/jpw-forex-professional-panel-20261005`; não presumir aceite de implementação a partir desta descrição. O defeito financeiro DD14 permanece fora do delta.

## Ferramentas sob demanda — candidate 2026-10-05

#ebToolsToggle expande #ebToolsBody, inicialmente hidden/inert. Os mesmos controles continuam montados ao fechar; openTool revela a região antes de selecionar a aba, inclusive no alias Motor. O estado de apresentação não integra S/storage. A grade mantém vinte colunas, 14/36 no desktop e16/48 no toque, IDs e escritores. Bases detalhadas ficam em disclosures, mas bloqueios e valores confirmados permanecem explícitos.

O launcher de Notas no Forex é um botão no fluxo da página; o lembrete de backup usa o mesmo nó e handlers em #forexAdvisorySlot. Fora do Forex o comportamento anterior e suas preferências permanecem. A mudança não confirma backup nem produz fatos financeiros.
