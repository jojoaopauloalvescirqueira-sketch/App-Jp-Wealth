# Forex: experiência e contratos de apresentação

Escopo: `CHG-JPW-FOREX-CLARITY-20261001`, plano completo aprovado pelo owner como N1/A2. A revisão organiza tarefas e apresenta os mesmos dados. Não altera policy V11, cálculos, schema, registros, migrações, consentimento, MT5, persistência ou preferências salvas. A elegibilidade normativa continua bloqueada nos casos definidos pelo motor; registro factual e autorização de execução continuam distintos.

## Destinos e contexto

As sete entradas do Forex são Visão geral, Contas e período, Operação, Histórico, Contabilidade, Planejamento e Reservas. A Visão geral apresenta “Panorama e próxima ação”; análises históricas, estatísticas e importações continuam disponíveis nos controles existentes. Seus seletores de conta, fonte e datas são de consulta. A consulta de B conserva a conta operacional A.

Contas e período distingue o contexto em uso da conta consultada. A escolha de período precede **Aplicar contexto e abrir Operação**. O botão nomeia o par que será aplicado. Consultar, mudar período de consulta e abrir detalhes não grava nem troca o contexto operacional. Aplicar conserva o comando `selectOperationalContext` e os guards originais, incluindo recusa de destino e revisão de rascunhos.

Nome da conta e data inicial do período identificam escolhas e resumos. Valores dos seletores continuam sendo os IDs originais. IDs técnicos permanecem na rastreabilidade, nos atributos e nos registros; ausência de identidade ou data é explicitada. O cabeçalho usa o mesmo período operacional nas sete entradas Forex, sem assumir que o início geral legado pertence à conta selecionada.

O Planejamento seleciona conta e período de origem do ACTUAL por nomes e datas. Trocar conta exige selecionar período e revisar a origem novamente. A revisão mantém os IDs e versões de origem; a importação usa os comandos e confirmações anteriores. Contas arquivadas e contextos de origem não conciliados permanecem representados explicitamente.

## Operação: leitura, entrada e auditoria

O título é Operação. A faixa de próxima ação fica no cartão da conta e utiliza `executionEligibility`, seu motivo textual e `canRecord` do mesmo read model. Não infere autorização a partir de campos preenchidos. O resumo conserva saldo registrado, equity, drawdown, Hard Stop, exposição total, compensada e alavancagem, com causas, bases e origem. SI e as demais proteções continuam em “Ver bases de cálculo e proteções”.

No layout padrão, as ordens seguem o resumo e precedem referências do instrumento. A mudança se limita à ordem visual padrão; layouts v6 salvos continuam prevalecendo, sem migração ou regravação automática. O cabeçalho conserva título e checklist; o mesmo acesso às seis fases fica junto às ordens.

O desktop usa sete colunas: ordem, instrumento/direção, papel/lote, preços, risco confirmado, estado e ações. “Cálculos e prévia” conserva os oito resultados anteriores de geometria e diagnósticos. “Detalhes” conserva HASH textual, resultado, custos assinados, tratamento dos custos, validação do stop, estado das pendentes, motivo, contexto capturado e comandos de fechamento, anulação e versões. Não há inputs duplicados.

No celular, as mesmas linhas e inputs são apresentados como cartões. O controller, draft map, handlers e nós DOM são compartilhados entre todos os tamanhos. Redesenhar métricas preserva input, cursor, rascunho e foco. A auditoria completa é uma tabela de 25 colunas somente leitura do mesmo read model confirmado; sua rolagem horizontal é intencional. A edição permanece nos detalhes da ordem.

Totais, risco confirmado e auditoria excluem prévias em RAM. Digitar continua usando a geometria de prévia original. Salvar linha conserva a validação de HASH, parsing, contexto, fingerprint, revisão e gravação originais. Cancelar restaura os dados confirmados. Guards de saída continuam oferecendo permanecer, descartar ou salvar e não presumem sucesso de persistência.

## Cadência de confirmação

| Tarefa | Confirmação preservada |
|---|---|
| Consulta de conta, período, fonte, datas ou histórico | Estado local de apresentação; sem gravação financeira |
| Aplicar contexto operacional | Ação explícita sobre conta e período após guards |
| Cadastro, perfil, período e observação da conta | Confirmações separadas nos formulários anteriores |
| Entrada e correção de ordem | Prévia em memória; Salvar linha confirma; correção exige motivo |
| Fechamento, anulação e finalização de operação | Comandos, motivos e confirmações originais |
| Importação de relatório MT5 | Analisar cria prévia; confirmação grava importação |
| ACTUAL no Planejamento | Revisar origem antes de importar fechamento revisado |
| Observações e propostas normativas | Registro explícito; proposta não ativa parâmetro |
| Reservas | Registrar reservas confirma o ato; preenchimento mantém o rascunho da sessão |

O motor e o editor de parâmetros têm destinos distintos: **Ver dimensionamento** e **Ver parâmetros**. Indisponibilidades apresentam causa e origem quando fornecidas pelo read model. Gráficos e radar sem série suficiente usam texto de indisponibilidade, sem desenho que pareça dado observado ou zero. Séries, métricas e entidades importadas continuam sendo obtidas pelas projeções originais.

## Correções da revisão independente

Na Visão geral, em larguras de até 1100 pixels, o panorama e a próxima ação precedem o contexto detalhado por padrão. Abrir explicitamente o contexto conserva a prioridade visual anterior. A alteração não troca conta, período nem preferências salvas.

Os controles de Forex têm alvo real de pelo menos 44 × 44 pixels e os campos principais usam texto de 16 pixels. Checkbox e radio mantêm caixa de 22 pixels dentro de um label com alvo de 44 pixels; a área clicável é o label. A regra fica restrita aos quatro hosts Forex e supera a densidade dos estilos antigos sem alterar cálculos ou os limites do cabeçalho da Operação.

O Histórico vazio mostra sempre o motivo e distingue operações finalizadas das ordens em andamento. Sem contexto selecionado, pede conta e período. **Ver Operação** e **Escolher conta e período** usam a navegação existente e seus guards. A mensagem primária não participa da ajuda automática e essas ações não gravam dados financeiros.

## Evidência e limites

`tools/forex_clarity_test.py` usa contextos Chromium isolados, fixtures de rede nomeadas e dados sintéticos. `SEED`, `seed`, `populate_example_order` e `save_example_order` podem ser reutilizados em comparações baseline/candidate. A fixture tem duas contas e períodos distintos; os comandos originais criam a ordem de exemplo e preservam HASH como texto.

O focal verifica contexto nas sete rotas, consulta B sem troca de A, aplicação explícita, controles únicos, rejeição de HASH ausente, projeções numéricas originais, prévia/cancelamento/guard/foco, auditoria readonly, teclado, origem do ACTUAL e ausência de writes durante consulta. A matriz contempla claro/escuro em 1440, 1024, 390 e 320 pixels, ações de 44 pixels, ausência de overflow da tabela compacta/página e ordens antes das referências. Capturas e medidas ficam nos artifacts indicados pela execução.

O focal também mede os alvos reais de todos os controles visíveis, inclusive campos dos detalhes abertos e labels de checkbox, texto dos campos principais, prioridade da próxima ação no celular, expansão explícita de contexto e mensagem primária do Histórico após aplicar o modo de ajuda. O fixture troca o tema tanto no HTML quanto no body para manter as duas superfícies coerentes. A comparação baseline/candidate de estado, JSON persistido e ambas as projeções usa tempo, UUIDs e Math.random determinísticos, sem normalização de campos.

As expectativas de apresentação de `forex_execution_table_test.py` e os rótulos de navegação de `forex_accounts_workspace_test.py` acompanham o contrato aprovado e documentado no CHG: abrir a seção de cálculos, acessar HASH por Detalhes, sete colunas/cartões e auditoria completa. As fixtures, números, versões, guards, cancelamento, deadlines, transporte e classificações anteriores são preservados. Resultados brutos anteriores continuam registrados, sem transformar gates falhos em PASS. Falhas intermitentes de carga exigem comparação com baseline e diagnóstico de transporte separado. Um focal aprovado não substitui a suíte oficial, o build integrado, QA do owner, homologação normativa nem validação manual com leitor de tela. Dados reais não foram lidos neste trabalho.
