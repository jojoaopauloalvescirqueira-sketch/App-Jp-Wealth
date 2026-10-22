# Planejamento independente — 20/10/2026

O candidato atual substitui o planejamento FX por menu principal independente. Contrato vigente: [PLANNING](PLANNING.md). As fotografias abaixo descrevem a implementação anterior, retirada da distribuição ativa; os dados `S.fxPlanning` continuam preservados e exportáveis, sem conversão automática.

## Fluxo atual

As abas são **Comece aqui**, **Consolidado**, **Preenchimento mensal** e **Referência**. No primeiro acesso, sem conta ativa, somente Comece aqui aparece. **Preencher o formulário** abre a sequência de configuração baseada no formulário nativo: ano e mês iniciais, capital inicial em USD, aporte mensal em USD, perfil de risco, custo mensal atual opcional, renda mensal desejada e identificação opcional da conta. A revisão antecede a confirmação; voltar permite corrigir respostas. A liberação do plano depende da gravação confirmada.

Consolidado reúne as contas ou consulta uma conta, com controles próprios de ano da projeção, período do gráfico e modo da tabela. Esses controles não modificam lançamentos. Preenchimento mensal e Referência têm seletores individuais. Referência conserva a projeção inicial; alterar premissas futuras não a substitui.

## Grade mensal atual

Cada plano individual cobre 120 meses consecutivos. A grade reproduz as **18 colunas financeiras D:U** da planilha: Fase, Mês, Saldo inicial (US$), Resultado (%), Situação, Resultado (US$), Resultado (R$), Câmbio (R$/US$), Saque (US$), Aporte (US$), Patrimônio (US$), Patrimônio (R$), Finalizado, Pago no mês (R$), Preço médio (R$/US$), Última cotação (R$/US$), Variação cambial (%) e Custo informado / situação. Na origem, A:C comportam o seletor de conta mesclado; não correspondem a três colunas financeiras adicionais.

A cada bloco de 12 meses do plano, uma linha de fechamento mostra saldo inicial, somas dos resultados e fluxos e patrimônio final do bloco, com as conversões correspondentes. O agrupamento acompanha a fase desde o mês inicial, podendo atravessar dois anos civis. Usa **12 MESES** nesses blocos e **FECHAMENTO** quando o bloco coincide com janeiro a dezembro; não substitui o resumo anual do Consolidado. O percentual de resultado do rodapé permanece vazio.

**Registrar rentabilidade**, **Registrar aporte** e **Registrar saque** conduzem pelas perguntas de mês e valores até a revisão e a confirmação explícita. Rentabilidade registra o resultado total mensal em USD, inclusive negativo ou zero; não inclui aportes e saques. Seu percentual deriva do saldo inicial do mês. Aportes e saques ocorrem no fim do mês e afetam os rendimentos seguintes. Corrigir o resultado substitui seu total anterior, preservando o histórico; corrigir fatos reabre os fechamentos dependentes para nova conferência.

As células azuis de taxa e aporte alteram somente a projeção futura pelos escritores existentes. Taxa vazia usa 0% provisório e conserva a situação pendente; zero explícito é uma premissa distinta. Aporte futuro vazio permanece vazio no registro e na exibição, calculando zero; não equivale visualmente a preencher zero e não cria lançamento. Aportes previstos não confirmados expiram ao fim do mês. **Finalizado = Sim** exige resultado registrado, conferência explícita dos fluxos e continuidade dos fechamentos anteriores; meses futuros não são finalizados.

## Confirmação, reinício e rascunhos

Formulários e consultas de prévia não gravam fatos. Fechar ou cancelar conserva respostas como rascunho da sessão; uma ação recusada não produz mensagem de sucesso nem descarta o rascunho. O Backup Completo pode preservar esses campos como material de trabalho, separado dos lançamentos. Rascunhos importados ficam disponíveis para leitura e cópia, exigindo conferência manual antes de qualquer nova confirmação.

**Reiniciar** apresenta alcance, contas e quantidades afetadas, com ciência e frase de confirmação. O reinício de uma conta arquiva seu plano completo, reaplica as premissas atuais em um novo plano e preserva a referência financeira; a comparação de renda passa a usar os objetivos vigentes no reinício. Reiniciar todas arquiva os planos ativos e deixa a configuração pendente em Comece aqui. Somente a confirmação de um novo formulário reativa a identidade reservada. O comando confirmado é aplicado pelo escritor do documento como um único candidato; cancelar antes da confirmação não modifica os registros. **Iniciar outro plano** permanece uma ação distinta de criação de nova referência, com arquivamento do plano anterior e as verificações de fatos registrados.

## Registro histórico preservado

# Planejamento Patrimonial — edição mensal

Candidate local de 06/10/2026. [Contrato da mudança](../work/CHG-JPW-PLANNING-MONTHLY-20261006.md).

## Trabalho na tabela

Forex → Planejamento patrimonial abre **Tabela mensal**. O planejamento é global
em USD, independente da conta operacional. A conversão BRL conserva a origem e
a referência temporal do câmbio. A ordem da tela é contexto, premissas gerais,
meses, gráfico e resumo anual.

Uma célula editável inicia um rascunho. A prévia usa o mesmo motor que os valores
salvos. **Salvar mês** confirma conjuntamente os ajustes; **Cancelar edição**
restaura o salvo. Enter termina a edição da célula sem gravar e Esc desfaz essa
edição. Redesenho, consulta e troca de ferramenta não são atos de gravação.

As premissas gerais incluem rentabilidade mensal informada pelo usuário e
depósitos recorrentes pessoal/Prop. Exceções mensais têm precedência. Alterar
premissas gerais preserva exceções, previsões retiradas e realizados. O resumo da
ação informa os meses que podem mudar.

## Ausência, zero e encadeamento

**Retirar previsão deste mês** registra ausência explícita. Zero continua um
valor válido; campo vazio não é zero. Premissas posteriores ficam guardadas,
mas os resultados dependentes ficam indisponíveis com a origem da lacuna.
Preencher o mês ou registrar o realizado permite retomar o encadeamento.
**Voltar às premissas gerais** é um comando distinto, que retira a exceção do
mês. Não apaga realizados, baseline ou revisões.

O cálculo preservado é resultado = saldo inicial × rentabilidade; saldo final =
saldo inicial + resultado + depósitos. Depósitos não recebem rentabilidade no
mesmo mês. Rebase é uma ação avançada explícita, jamais um preenchimento
automático de lacunas.

## Realizado e proteção

**Registrar realizado** pede uma única entrada original: percentual ou nominal
USD. A outra medida é derivada pelo motor. Depósitos efetivos vêm do ledger,
sem promover previsões. Finalização exige base e resultado válidos e conferência
explícita dos depósitos, mesmo zero. A linha confirmada fica azul clara com o
rótulo **Finalizado**; sinal e valores negativos continuam identificados.

Finalização protege também os comandos antigos, importações e inclusão/remoção
de depósitos. Reabrir exige motivo, conserva a versão confirmada e marca os
realizados posteriores **Base em revisão**. Percentual/nominal original e origem
não são substituídos. Reconferência ocorre cronologicamente; projeção retomada
parte do último realizado contíguo confirmado. A reabertura não converte um
realizado em projeção.

## Dados e persistência

`planningRevision:3` acrescenta ausência de previsão e ciclo de fechamento.
Revisão 2 continua legível; seus realizados são tratados como finalizados.
Consultar não migra nem grava. Schemas incompatíveis são recusados sem
reinicializar a base. Baseline, cenários, snapshots, ledger e proveniência ficam
preservados. Revisões guardam os elementos necessários à reconstrução anterior.

Cada comando confirmado percorre uma vez o writer existente. Recusa conserva o
rascunho; resultado desconhecido não é anunciado como sucesso e requer releitura.
Conflitos entre abas continuam protegidos pelo contrato de persistência atual.
Rascunhos são transitórios e não têm recuperação prometida após recarga.

Os gráficos dividem séries em segmentos na ausência de valores. Conversão,
desvio e resumo anual indicam cobertura parcial; subtotal identificado não vira
total completo. A tabela permanece a alternativa de consulta dos valores.

## Verificação e retorno

Focais adicionais: `tools/fx_monthly_board_test.py`,
`tools/fx_monthly_domain_test.py` e `tools/fx_monthly_chart_test.py`, além das
regressões e gates existentes. Resultados brutos e limitações são externos ao
pacote, em `jpw-planning-monthly-20261006`.

Retorno seguro usa a distribuição anterior **junto de seu backup anterior**.
Não abrir uma base revisão 3 num runtime antigo nem remover campos para forçar
compatibilidade. Esta entrega é candidate local; não comprova integração,
publicação, homologação normativa ou recalculação da planilha no Excel.
