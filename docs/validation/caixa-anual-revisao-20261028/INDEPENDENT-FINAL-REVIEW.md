# Caixa Anual — revisão independente final A0

Parecer de28/10/2026: **PASS delimitado da rastreabilidade da renomeação e dos recibos técnicos**. O resultado bruto do FULL é116/116PASS, saída0. Isso não demonstra excelência do conjunto, prontidão integral ou correção dos achados encontrados na revisão.

Esta revisão final conferiu arquivos, hashes, catálogo e recibos do executor. Não executou novamente testes, navegador, Excel nativo, reconstrução ou FULL. A única escrita deste revisor no repositório nesta etapa é este novo relatório autorizado.

## Identidade e resultado conferidos

- Branch `codex/caixa-anual-revisao-20261028`; HEAD `3e24f60f8cfe87f79335f40e95a0927379a9f834`; build `fc1a41530cdc4569`.
- [Recibo bruto](full-final.json): SHA256 `013522eba409dbaa97e64303725ffe46dfdb03f8b1bb51e84a91f51a71cc893c`. Execução28/10/2026,11:58:13–12:48:37, São Paulo; duração observada pelo supervisor3023,879segundos.
- Os116nomes e sua ordem correspondem ao catálogo FULL vigente; não há IDs duplicados, ausentes ou substituídos. Todos possuem `result:PASS` e `returncode:0`; comandos contêm os caminhos esperados do catálogo. O resumo contém116PASS e zero nos demais resultados. [Saída real](full-exit.json) confirma0. A cópia `full-attempt1-116pass.json` é idêntica ao recibo bruto e `full-output.log` coincide com o log scratch.
- `quality_gate.py` permanece SHA256 `51fae2e0a9b25972d68c9d8e70023d28536fb4f590e386e8a518eecc568ab84d`, igual ao baseline anterior à renomeação. Inspeção independente por AST confirmou FAST4, STANDARD71 e FULL116; não executou o gate.

## Congelamento e conservação

A conferência após o FULL, repetida às12:52:58, encontrou os1624inputs de [freeze-before-full.json](freeze-before-full.json) presentes e com hashes iguais. O conjunto inclui motores, estado, escritor, política, persistência, quatro juízes de rótulo, manifesto, fontes e distribuição portátil. O mapa inicial de3454arquivos não perdeu nenhum arquivo; os25caminhos alterados coincidem com [FINAL-AUDIT.json](FINAL-AUDIT.json). A renomeação não alterou fórmulas, schema, gravações financeiras, dados, IDs ou aliases. A distinção entre alterações herdadas e o delta atual foi feita contra o backup do candidato completo, preservando seu trabalho pendente.

O FULL regravou um recibo histórico pelo comportamento preexistente de `tools/hedge_prop_engine_test.js:247–248`. A comparação independente confirmou que somente `timestampUTC` diferia. A prova nova está preservada em [hedge-counterproofs-current-full.json](controls/hedge-counterproofs-current-full.json), SHA256 `f08d35edb716d724742c9bbc752622f421831e28052cb4d7c4f254cdca230319`; os bytes históricos foram restaurados ao SHA256 original `1bc9e6ce6908fb46c4f1721eb2d1b2b488ebad05c22e75caca507aaf747e3fc3`. [Recibo da conservação](controls/historical-receipt-restored.json). Esse arquivo histórico não integra os1624inputs congelados, e a restauração não mudou nenhum deles. A primeira tentativa do coletor parou no próprio guard; não foi uma falha do produto nem uma nova execução do gate.

O original XLSX permaneceu no hash autorizado `621a4e5bdefc467bede301b94e2c6f60aa05c78df3613cfac3908ef8d0c9084a`. As cópias de evidência conferidas mantêm seus hashes. A guarda temporária de suspensão foi observada ativa antes/durante a execução; supervisor, guarda e gate já não estavam presentes no `ps` após seu término. Não foi inferida uma alteração permanente de energia.

## Quatro juízes e suplementar

Os três juízes iniciais trocaram apenas quatro expectativas literais do nome. A quarta autorização acrescentou somente uma constante em `contextual_sidebar_test.py`; seu hash final é `137039c2b53065acaa72f61cf01f8352ee16d1fd4223029f0a1e47afd6541493`. As demais asserções, tolerâncias e comandos permanecem idênticos.

O teste contextual é suplementar e já estava fora do catálogo FULL116. Ele não foi removido para obter a rodada verde. A [comparação controlada final](controls/sidebar-classification-final.json) demonstra:

1. Juiz novo com DOM atual ultrapassa a asserção do nome369 e falha posteriormente em378, na expectativa de contexto da rota `research-stocks-br`.
2. O mesmo juiz, com somente o texto antigo do menu servido em memória, rejeita exatamente esse nome em369. Houve uma resposta efetivamente mutada; o disco permaneceu intacto.
3. O juiz original do baseline, com o mesmo DOM de nome antigo, ultrapassa369 e reproduz378.

O caso completo permanece **BASELINE_FAIL relativo à renomeação**. Essa prova não é uma execução de um checkout integral do baseline. As primeiras tentativas de injeção que não modificaram o breadcrumb efetivo continuam **TEST_HARNESS_FAIL**, sem crédito como RED do nome. O critério específico do nome está demonstrado; o focal suplementar completo não está aprovado.

## Pendências preservadas

- **UX-01 — P2, PRODUCT_FAIL, OPEN:** o retorno realizado pode usar uma abertura real corrigida enquanto o resumo mostra a abertura planejada sob o nome genérico Saldo inicial. O cálculo está correto; a apresentação do denominador é ambígua.
- **UX-02 — P2, PRODUCT_FAIL, OPEN:** Registros conferidos pode aparecer quando não há datas pendentes, mas existem saldos a reconciliar. Alertas e bloqueios permanecem; o texto continua contraditório.
- A programaçãoQ e a quantidade de datas civis podem divergir. A data encontrada pela busca aproximada não demonstra que o saldo desejado foi alcançado. Essa limitação aprovada exige explicação melhor, sem autorização implícita para mudar a fórmula.
- Os incidentes históricos Epoch/Alladin permanecem com causa não confirmada e abertos. Esta rodada não os encerra.

Os116checks aprovados não apagam esses achados nem o BASELINE_FAIL suplementar, pois são evidências de escopos distintos. Não há aceite visual humano, recálculo nativo completo do Excel, homologação financeira ou declaração de ausência universal de defeitos. Não houve autorização de integração Git ou publicação. O parecer valida a entrega delimitada do nome e a integridade dos recibos; **overall readiness não é declarada**.
