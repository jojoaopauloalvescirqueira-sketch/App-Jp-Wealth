# Forex — Execution Board

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
