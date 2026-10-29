# Gerenciamento — planejamento anual e caixa diário

Contrato do candidato de26/10/2026, delimitado pelo [plano humano aprovado](../superpowers/plans/2026-10-26-portfolio-management.md), [mudança de produto](../work/CHG-JPW-PORTFOLIO-MANAGEMENT-PRODUCT-20261026.md) e contrato separado dos controles. Descreve a implementação em validação; não declara homologação financeira, aprovação humana da aparência ou publicação.

Nome público atualizado para **Caixa Anual** em28/10/2026, preservando IDs, dados, contratos e cálculos. [Revisão da primeira aba e limites conhecidos](../validation/caixa-anual-revisao-20261028/README.md). Esta renomeação não resolve automaticamente os achados de apresentação registrados na revisão.

## Finalidade, referência e adaptações aprovadas

Gerenciamento reúne **Reservas** e **Caixa Anual**, independentemente da disponibilidade de Forex. Reservas conserva seu motor e seus limites. Caixa Anual (antes apresentado como Contabilidade) substitui a antiga tela pública por planejamento anual e fechamento diário inspirados na primeira aba da planilha fornecida, preservando fatos e históricos anteriores.

Referência autorizada: `Planejamento_com_aporte copy.xlsx`, SHA-256 `621a4e5bdefc467bede301b94e2c6f60aa05c78df3613cfac3908ef8d0c9084a`, primeira aba **Todas**, região A2:R329. A investigação leu OOXML, fórmulas, comentários, estilos e valores em cache, sem editar nem recalcular o original. O pacote contém três abas visíveis e não contém VBA, conexões, controles ou links externos. Isso não demonstra ausência de automações externas em outro ambiente. As abas Referências e Crescimento+Aportes não fazem parte desta substituição.

A referência apresenta indicadores e uma tabela densa com Planejado e Realizado lado a lado, além de subtotais semanais. Seu calendário possui sementes históricas independentes do início do plano; esse defeito não é reproduzido. No site:

- O horizonte é o **ano civil**, da data inicial confirmada até31/12, com segunda a sexta e exclusões explícitas. Sem feriados presumidos e sem manter artificialmente261 linhas.
- A consulta usa hoje no ano corrente,31/12 em ano encerrado e estado ainda não iniciado nos anos futuros.
- Abertura e moeda vêm da conta/período confirmados, sem conversão cambial implícita. Uma divergência entre moeda do plano e moeda do período restaurado torna a consulta indisponível, inclusive quando não há lançamentos; o histórico conserva sua moeda original. Consultar Gerenciamento não aplica o contexto na operação Forex.
- Resultado diário é manual e monetário; não há soma automática das operações, aportes ou saques. Valores ausentes não viram zero.
- Editar usa prévia, confirmação explícita e Cancelar. Correção e anulação preservam auditoria; o fechamento anual é um ato novo e explícito.

Os exemplos monetários do arquivo não são dados iniciais do produto. Criar ou consultar uma base vazia não cria contas, planos ou resultados.

## Cálculo e apresentação

Para objetivo anual `T`, dias por semana `D` e meses por ano `M`, mantém-se a programação `Q = D ×52 × M/12`, inclusive valores fracionários. A fração do ano é `f = úteis(início…31/12) / úteis(01/01…31/12)`, com os dois limites inclusivos e as mesmas exclusões declaradas. A meta parcial é `(1+T)^f−1`, os períodos parciais são `Q×f` e os meses parciais são `M×f`. As raízes correspondentes fornecem as metas diária e mensal; não há um segundo redutor. Falta de datas elegíveis ou domínio numérico inválido produz explicação, não uma taxa zero fabricada.

A quantidade de datas da grade pode diferir de `Q×f`, como já acontecia entre a programação e a grade original. A interface mostra as contagens separadamente; não promete alcançar o saldo desejado em31/12 nem ajusta a taxa para forçar essa coincidência. `referenceYears` e `referenceDays` preservam as referências editáveis M4/N4, com sugestões1 e364; seus quocientes são descritivos e não comandam o calendário ou as taxas.

Planejado reinveste a taxa diária sobre o saldo projetado anterior. Realizado consulta os fechamentos canônicos e conserva saldos observados. Correções recalculam apenas a cadeia que o escritor original identifica como derivada; não substituem observações independentes. Mudança do saldo confirmado anterior ao início atualiza a abertura real consultada, mas não altera silenciosamente a abertura planejada já confirmada. Uma programação revista exige novo ato explícito e conserva a versão anterior.

Os cálculos mantêm precisão numérica, inclusive resultados como1,001 na moeda da conta. Arredondamento pertence à apresentação. As extrapolações realizadas preservam os períodos originais: mensal `D×4` e anual240. Só aparecem quando a abertura e a posição estão disponíveis e os dias devidos foram resolvidos, sem divergência de saldos. Dias úteis decorridos, dias registrados, declarações e pendências são contagens distintas; calendário não comprova dias efetivamente trabalhados.

O termômetro conserva a busca aproximada por **aberturas projetadas**: data equivalente é a última abertura projetada menor ou igual ao saldo real; diferença é data equivalente menos referência do ano. Preserva deliberadamente as cores da fonte: abaixo de14 dias verde,14 a29 amarelo e acima de29 vermelho. Avanço/atraso aparece em texto separado; verde não significa ausência de risco nem elegibilidade operacional. Alvo zero/negativo ou sequência não crescente deixam a comparação indisponível, sem alterar o alvo. A data projetada da meta também conserva a aproximação da fonte, não uma interpolação ou primeira ultrapassagem garantida.

A tabela ampla mantém os blocos Planejado/Realizado e as semanas civis. Na apresentação estreita, três colunas e detalhes conservam os valores completos. Datas com fatos reais fora da programação continuam acessíveis e entram no realizado; não recebem capitalização projetada adicional.

## Estado, confirmação e conservação

`S.managementAnnual` é opcional, `schemaVersion:1`, com revisão, planos e auditoria. Há uma configuração por **conta + período + ano**. Cada plano conserva configuração, origem da abertura, revisões, declarações vigentes e retratos anuais. **Não armazena uma segunda coleção operacional de resultados reais.** O ledger de `JPWForex.state` permanece a fonte única desses fatos.

O início deriva de `openingBook` confirmado ou do último fechamento anterior à data inicial, com ID/versão e origem disponíveis para revisão. Saldo inexistente ou não positivo impede confirmar essa configuração, sem substituir dados financeiros. O saldo digitado pelo chamador não suplanta a origem confirmada.

**Dia sem resultado** é uma declaração explícita, distinta de um lançamento de resultado zero e de uma célula vazia. Ela conserva o saldo conhecido e não altera programação ou metas. Não pode contradizer um fechamento existente. Retirar uma declaração exige confirmação e motivo; sua versão retirada fica na auditoria antes de um eventual registro financeiro posterior.

O retrato anual só pode ser confirmado **após31/12**, com os dias devidos resolvidos e os saldos reconciliados. Ele conserva resumo, linhas, revisão e dependências conferidas. Não encerra o período Forex nem apaga lançamentos. Mudança posterior nas fontes — inclusive na abertura anterior ao início — sinaliza reconferência e conserva o retrato anterior; uma nova confirmação acrescenta outro retrato.

Consultas não inicializam nem migram dados. Comandos conferem sessão, geração, epoch, revisão do agregado, conta, período e revisão do contexto. O escritor confirmado existente faz comparação com a base durável e releitura. Não se autoriza outra gravação automaticamente após conflito ou recusa. `UNKNOWN` bloqueia repetição e também impede apresentar a memória financeira tentativa como dado confirmado. A interface conserva o preenchimento para a recuperação/revisão original.

O agregado acompanha o Backup Completo e o encerramento por fazer parte do documento confirmado completo. Backups antigos sem essa família continuam válidos; presença incompatível é recusada antes de normalização ou substituição e preservada pelo fluxo existente de recuperação. O formato do Backup Completo não mudou. O validador verifica estrutura, identidades históricas, revisões e ausência de campos de segredo; uma validação estrutural local não autentica autoria nem comprova a realidade econômica dos registros.

## Interfaces e ciclo de vida

Scripts clássicos, sem nova dependência:

- `JPWAnnualEngine`: `dateKey`, `dayDifference`, `validateConfig`, `calendar`, `build` e `dependencies`; cálculos puros, sem DOM, armazenamento ou rede.
- `JPWManagementAnnual.queries`: `context`, `token`, `model`, `previewPlan`, `previewResult`, `previewAnnualClose`, `listPlans` e `snapshot`.
- `JPWManagementAnnual.commands`: `savePlan`, `recordResult`, `voidResult`, `declareNoResult`, `revokeNoResult`, `closeAnnual` e `resetContext`; `resetContext` e `invalidate` também ficam no namespace para o ciclo de vida.
- `JPWManagement`: `activate`, `deactivate`, `reset`, `setView`, `render`, `context`, `guardNavigation`, `hasPendingWork` e `backupDrafts`.

Alvos identificam `{accountId,periodId,year}`. A configuração usa `startDate`, `annualTarget`, `daysPerWeek`, `monthsPerYear`, `excludedDates` e referências opcionais; prévia acrescenta abertura e moeda confirmadas. Resultado recebe `{target,date,value,id?,note?}`. A observação é texto inerte de até500 caracteres, sem caracteres de controle; quando omitida numa correção, conserva a anterior. As prévias retornam `ok`, `status`, `errors` e o conteúdo correspondente; modelo acrescenta plano, retratos e `closureStatus`. Comandos recebem token da revisão e confirmação explícita; retorno `CONFIRMED` é distinto de `INVALID`, `CONFLICT`, `REFUSED` e `UNKNOWN`.

Seletores de Gerenciamento ficam em memória. Rascunhos usam as guardas e recuperação do workspace existente; navegar, alterar contexto e sair exigem resolver a edição pendente. Finalizar a sessão preserva o documento confirmado e invalida a apresentação; não recupera um rascunho como lançamento financeiro. A rota canônica é `management-accounting`; entradas antigas de Contabilidade resolvem para essa área após navegação aceita.

Recusar uma troca de contexto restaura os valores visíveis da conta, período e ano aceitos sem recriar os controles. A identidade local de sessão usa `crypto.randomUUID` quando disponível e o mesmo fallback de identificadores já utilizado por Planejamento e Agenda nos demais contextos; não é uma credencial criptográfica. Inicializar ou consultar essa identidade não cria registros nem grava o documento.

`resetContext()` não grava e retorna `true` somente ao reconhecer uma nova época de base/sessão confirmada ou a liberação verificada de uma gravação indeterminada. A memória precisa coincidir com o retrato confirmado; troca normal da raiz durante gravações e renderizações repetidas retornam `false`, preservando a edição em curso. A apresentação pode limpar seu estado efêmero quando esse retorno identifica a mudança efetiva de contexto, sem transformar memória tentativa em autorização de gravação.

## Provas e limites

Entradas focais permanentes: `node tools/management_annual_engine_test.js`, `node tools/management_annual_state_test.js`, `node tools/management_guide_test.mjs` e as provas de interface/integração registradas no gate. Na iteração atual foram observados35 casos do motor e32 de estado aprovados, além de13 de compatibilidade do guia. O estado executa os comandos Forex reais, com fronteiras sintéticas de persistência; casos adicionais executam o escritor real com armazenamento controlado. Esses focais não substituem navegador, Backup Completo, distribuições, zoom ou FULL do candidato final.

Contraprovas e recibos próprios identificam os bytes e os critérios; uma rodada antiga não aprova uma modificação posterior. O XLSX não foi executado no Excel nesta investigação. Comparação humana da dinâmica e da aparência, leitor de tela e toque físico continuam avaliações separadas. A implementação não altera a política V11, autoriza operações, conecta ao Excel/Sheets nem publica o site.

## Cadastro compartilhado — ownership de apresentação

Cadastro e preparação recebem `owner:management` somente a partir de uma rota Gerenciamento aceita. O owner é capturado antes de abrir o diálogo, permanece nas cadeias de cadastro/preparação e é revalidado nos atos. O padrão dos consumidores antigos continua Forex. Congelar Forex não suspende o diálogo de Gerenciamento; congelar Gerenciamento suspende seu próprio preenchimento.

A preparação em Gerenciamento não ativa o contexto operacional: a opção de torná-lo período atual fica indisponível nessa origem, e o atalho final volta à área sem chamar `useContext`. A lista de contas/períodos é atualizada após confirmação, sem escolher outra conta automaticamente. Reaproveitam-se os mesmos comandos e base de contas; rascunhos de cadastro não viram registros ao cancelar.

Limite de orientação: o indicador legado de trabalho pendente de Forex ainda consulta o estado global do fluxo compartilhado e pode considerar uma ficha aberta de Gerenciamento. O diálogo conserva seu owner e as guardas efetivas; nenhum valor é gravado ou apagado por esse indicador. Isso é uma pendência informativa, não uma dispensa de falha material.
