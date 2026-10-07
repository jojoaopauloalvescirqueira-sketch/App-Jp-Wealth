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
