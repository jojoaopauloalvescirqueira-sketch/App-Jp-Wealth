# Parecer independente — contraprovas do produto compatível com controles37 —29/10/2026

## Conclusão

AUDIT_PASS delimitado à identidade e às12 rejeições deste recibo. As contraprovas atuais usam JS8cfa…/CSS31e7… e os cinco testes aplicados do pacote37, com o juiz corrigido. Não identifiquei falsoPASS por motivo errado. O recibo calendar-after-compat.json contém22/22PASS, inclusive calendar-edges-320-light, conforme execução do coordenador.

Isto não é aprovação FULL, distribuição, matriz visual413, nativos ou aceite humano. Não aplica nem autoriza V3FF; o arquivo aplicado continua FFf66f… do37. Nenhum browser, suite ou arquivo de repositório foi executado/alterado pelo revisor neste acompanhamento. Apenas leituras, comparações/hash/AST e este relatório scratch.

## Identidade verificada diretamente

Conferi os sete inputs físicos scratch (cinco candidatos e dois fontes do produto) contra input-binding.json e contra os respectivos arquivos atuais na raiz: todos iguais. Também conferi os hashes atuais de build-id.js/index.html/manifest indicados pelo binding. As entradas root-identity são referências de identidade, não cópias físicas no diretório scratch; seus hashes foram comparados aos caminhos source registrados.

- Build registrado:aabc8d09faff4aee; build-id.js SHAe09a14541af933658c25e929e5ff712ebcc79c8f55ea5605c4ac573894f36247
- ProdutoJS8cfaec067a59ba393ff2aa53ad097196460e64e6de111945d92d3da21c47a518
- ProdutoCSS31e7659038d380c2348919a7ffa4229be125c5893d03540a89f728e3ad3aed5e
- Helper35ea10d57ed2c8c4e6042ce14a88033cc232214f28790de9eacb9e9baf85c80a
- FF aplicadof66f357830f04a2c9f6eeb92ac469d8e04c190b6aa1a42aad161f65ebde859a7
- Launcher2d445a571a1c07f5d00c98e71832115aa8d540a66d1318b82994c61fdbb53516
- Recibo12CP41324d6fa98e3b29a8dcf28a38b093c095adc911778bc399b643b1c94c287d5f
- input-binding.json a484c0dc80747b003423715e58cc5b3150979cc44fae7dd24b9db7301cba12e6
- Recibo22calendar996612f3702378d648e58a33fa29cac4d438449a2816f118b6f5234adb4fdad5

## Juiz e estímulos

Li launcher-binding.diff: somente caminho de produto, hashes esperados do produto e diretório de saída diferem do launcher v2 corrigido. Comparei por AST a definição ORACLE_FRAMES e as12 chamadas record(): idênticas. Comparei também ID, estímulo, marcador esperado e largura entre os recibos v2 e atual: idênticos em todos os12 casos. O helper aplicado conserva exatamente35ea…; a tolerância e as asserções não foram ajustadas para acomodar o produto novo.

As mensagens e frames finais atuais correspondem ao oráculo pretendido:

| Casos | Asserção efetiva |
|---|---|
| CP01/CP02 | assert_values:58, zero forecast preservado / Actual não inventado |
| CP03 | assert_layout:93, sete campos visíveis |
| CP04 | assert_values:66, explicação acessível de ausência |
| CP05 | assert_layout:101, limites reais th/td; não overflow |
| CP06 | assert_layout:97, alinhamento da tinta numérica à direita |
| CP07 | assert_layout:91, cabeçalhos incompatíveis com área719 |
| CP08 | table_case:171, aviso da última coleta visível no inner_text |
| CP09 | table_case:179, detalhe anterior deve ficar fechado |
| CP10 | details:33, alvo pertencente ao próprio host |
| CP11 | table_case:193, observação com instante alterado não mantém expansão |
| CP12 | table_case:215, texto do draft permanece intacto |

Para CP08 a exceção não tem mensagem, mas a fonte da asserção e o frame final exatos são conferidos contra helper congelado. Nos demais a mensagem real e o frame do helper correspondem. A pesquisa do marcador no traceback completo não voltou; o defeito v1 permanece corrigido. Cada caso registra REJECTED, mensagem/frame correspondentes e precondição positiva; não há erro de bootstrap apresentado como rejeição do produto.

Limites anteriores continuam: CP11 também altera foco, mas falha pela expansão antes do oráculo de foco; CP12 também altera cursor, mas falha pelo valor do draft antes do cursor. Relatar essas duas rejeições pelas propriedades efetivamente alcançadas, não como múltiplas contraprovas isoladas.

## Evidência nominal e fronteira de fechamento

calendar-after-compat.json possui exatamente22 resultados, todosPASS, incluindo edges320 anteriormente vermelho. O revisor leu o recibo; não reexecutou essa suite. Essa evidência demonstra a repetição focal relatada, sem apagar o RED anterior e sem substituir FULL ou aprovação humana.

O trabalho autorizado pode registrar as12 contraprovas e22 casos focais como aprovados nos seus escopos, mantendo a pendência conhecida de adaptação FFv3 e sua autorização específica. A revisão atual não analisa as quatro distribuições em execução nem presume seus resultados. Nenhuma identidadeV3 foi usada para transformar o37 em verde.
