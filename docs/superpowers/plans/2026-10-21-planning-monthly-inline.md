# Preenchimento mensal — compacto, editável e intuitivo

Plano aprovado pelo proprietário no PLEASE IMPLEMENT THIS PLAN desta conversa. A decomposição abaixo organiza a execução; não amplia a autorização. Base real2ddbac03d67141d0, branch existente codex/planejamento-patrimonial-20261020, HEAD ea15afc9c6a9c30cc69c5b98a8b85c85211ffb34.

## Contrato aprovado

- Clicar na célula para editar, com Salvar/Cancelar. Resultado passado/atual em percentual ouUSD; múltiplos aportes/saques editados individualmente. Preferências visuais lembradas neste navegador.
- Linhas comuns de leitura até64CSSpx no desktop, sem corte nem altura fixa para valores grandes/zoom; alvos44px e tolerância visual2px. Eliminar Resultado·% repetido; USD epercentual juntos, BRLsegunda linha. Sete colunas em>=900px úteis, três abaixo; um detalhe aberto e campos únicos.
- Consulta somente leitura JPWPlanning.queries.previewResultInput({accountId,month,unit,value}) usando saldo de abertura atual e arredondamento a centavos já adotado. Gravar resultado somente pelo recordResult existente emUSD. Percentual indisponível sem abertura positiva. USD mantém validações existentes.
- Aportes exigemUSD eBRLpagos; saqueBRLopcional. Nenhuma conversão de custo automática. Editar porID, preservar histórico. Revisão/confirmar reais dentro do mês; avisar fechamentos que exigirão reconferência. Futuro continua setProjection, agora com Salvar explícito, sem blur-write.
- Saldos, patrimônio, preço médio e referências calculados. Clique fora não grava/descarta. Escape cancela, Tab natural, Enter ativa editor. Preservar rascunho/foco/cursor emresize; guardas de conta/período/navegação antes de esconder edição pendente.
- Verde suave emtodo mês passado, mesmo pendente, mantendo texto de estado. Destacar meses passados inicialmente ligado; desligar afeta somente passado, preserva atual. Todos os meses/Atual em diante; Ano incluiTodos padrão. Filtros combinados com recuperação vazia clara. Grupos sem linhas visíveis ocultos; subtotal identificado como ciclo completo.
- Guardar somente duas preferências em jpwealth_planning_monthly_view_v1, foraS eBackupCompleto, integradas à limpeza existente. Falha de armazenamento permiteuso temporário comaviso; payloadincompatível preservado.
- RED/GREEN, contraprovas e revisão independente. Preservar critérios anteriores, adaptar apenas contratos substituídos. Quatro layouts×doistemas,320–1440,899/900/901úteis, nativo200%; valores, edição, cancelamento, conflitos, recusas, múltiplos, mesesfechados, viradadomês, no-write. Oficialbuild, HTTP/offline/file/portátil/PDF e FULL atual obrigatório.
- Sem dependências novas, migração financeira, Git/publicação, alteração de normas/instruções ou memória global. Preservar Consolidado/formulário/Stoikus/motores/histórico/trêsminigames/BolsasGlobais e122pendências. Aceite humano separado.

## Decomposição executável

### Task 1: Prévia somente leitura e regressão de domínio

Somente02-state.js: acrescentar função/consulta, sem mudar escritores, previewFlow ouengine. unit='PERCENT'|'USD', value número finito; percentual em pontos (3 significa3%). Retorno mantém formato de previewFlow e acrescenta openUsd,inputUnit,inputValue; rate emfração eUSDemcentavos. USDnãoarredondadoautomaticamente: validaçãoexistente. PERCENT calculado do saldo fresco e arredondado porMath.round(valor*100)/100, como conversões atuais. Recusar saldo nãopositivo/indisponível paraPERCENT, entradas vazias/nulas/strings e unidadeinválida; erros explicativos, sem persistência/rede. Preservar0/negativos válidos e regras de saldo do motor.

Adicionar tools/planning_monthly_result_input_test.js, executar RED no módulo original antes de mudarconsulta, GREENdepois. Incluir execução no planning_state_test.js existente, sem removercasos. Testes:1000×3%=30;112,55×3%=3,38; perda;zeroUSD;0capital;semconta;futuro;incompatível;inválidos;pureza/repetição; dadosfreshapósalteração e previewescritorrecusado. Contraprova conversão errada rejeitada porasserçãonumérica. Entregar relatório/diff/recibos no workspaceown task1. Revisão independente antes de Task2.

### Task 2: Tabela, editor, preferências e provas de interface

UI03-ui.js eCSSlocais;07-finalize-session.js somente chave auxiliar/ciclo de vida necessário. Manter fórmulas/escritores intactos. Umaedição ativa com unidade/valores/token contextual; revisão readonly; confirmar comandos atuais eadotar somenteseCONFIRMED, semretry emUNKNOWN. Corrigir registro porID; não substituir totais agregados. Snapshot financeiro e delegates reais comprovam no-write, sem mocks que apaguem persistência avaliada.

Preferência envelope versionado1 com highlightPast efromCurrent booleanos, read-back, sem dados financeiros; não adicionarao workspaceBackup. Releitura naativação sem sobrescreverdraft. Chaveincompatível preservada comestado temporário e aviso; limpeza pelo mecanismoautorizado existente. Observadores invalidáveis em reset/finalização; nada ressuscita ediçãoantiga. AnoTodos padrão; alteração de filtro comdraft exige resolver antes deaplicar.

Adicionar tools/planning_monthly_inline_test.py, integrar a execução default em ui_visual_quality_test.py preservando206IDs/critérios, alterando somente estímulos explicitamenteobsoletos (ativar célula antesdeeditar, Salvar explícito eAnoTodos). Atualizar consumidores existentes somente por essescontratos, mantendo montantes/limiares/jornadas. REDantesdeUI e GREENdepois; contraprovas dealtura>64,duplicatecontrol,greenfalso,registroemdigitação,preferênciafinanceira/backup e valorUSDconvertido incorreto. Matriz exercita estado/modeloreal e garante todos120meses/dados/subtotais, não apenas contagem. Revisão independente de produto ejuiz.

### Task 3: Integração, distribuição e entrega

Reconciliação factual autorizada de PLANNING/README/CHANGELOG/CURRENT-STATE/ACTIVE-TASK/SESSION_HANDOFF; índice de regressões local sem apagar53anteriores. Históricos permanecem. Build oficial, focais, distr/web/PWAoffline/file/portátil/PDF, freeze de fontes+testes+controles e96checksatuais completos; nova execução integral se mudança material posterior. Revisão independente final, capturasantes/depois, prévia versionada e limites. Sem autoriahumana/aceitevisual presumidos, nenhum Git.
