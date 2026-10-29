# Revisão independente — FULL5

Revisão somente leitura de recibos, fontes e hashes concluída em 28/10/2026. Este arquivo novo registra o parecer; a revisão anterior permanece preservada. Nenhum teste, navegador, gerador ou alteração de produto/verificador foi executado por esta revisão.

## Resultado e identidade

**FULL5 NÃO APROVADO.** O gate terminou em 28/10/2026 às 00:49:40, horário America/Sao_Paulo, com saída 1: **114 PASS, 1 PRODUCT_FAIL e 1 TEST_HARNESS_FAIL**, total de 116 checks.

`full-final.json` foi confrontado byte a byte com `full-attempt5-114pass-2fail.json`: são idênticos. SHA-256 do recibo bruto preservado: `83fa939302338a777051852f2147e034a60d2d087ced0ec0916c60763c132cad`.

Branch registrada: `codex/mesas-proprietarias-hedge-20261027`. HEAD registrado: `3e24f60f8cfe87f79335f40e95a0927379a9f834`. Não houve operação Git nesta revisão.

## Integridade e cobertura confirmadas

Foi repetido o confronto dos hashes dos **1.621 arquivos congelados** em `freeze-before-full.json` e dos **86 caminhos protegidos** em `protected-sources.json`: nenhuma divergência encontrada. O resultado concorda com `full5-integrity.json`.

Os três checks Hedge — engine, browser e distribuição — passaram. Research, protocolo de sessões e qualidade visual também passaram no FULL5. O recibo próprio do browser Hedge confirma **oito combinações de zoom nativo 200% aprovadas**, quatro layouts e dois temas, com `outer=1440`, `inner=720` e CSS zoom `1`. Esses resultados delimitados não convertem a suíte completa em aprovação nem representam aceite visual humano.

## Falhas e limites causais

- **Alladin, PRODUCT_FAIL:** caso W6, `Page.goto` excedeu 30.000 ms esperando `load`. É uma falha distinta do clique de edição I4/I5 observado no FULL4. A coincidência da janela com suspensões do Mac é um fator ambiental concreto; o mecanismo da falha W6 não foi demonstrado.
- **Planejamento, TEST_HARNESS_FAIL:** `matrix-submenu-light-1099x720`, clique em `#pl-native-stopOpen`, timeout de 15.000 ms. O recibo registra 93 casos aprovados e um reprovado. Os logs de energia e os horários do caso demonstram suspensão do sistema durante a verificação: o caso durou 912,322055 s de relógio e terminou junto da retomada após o episódio registrado de 914 s. Suspensão/retomada é uma explicação forte para a interrupção; o mecanismo exato do timeout e a inexistência de um defeito independente não são estabelecidos apenas por esses logs.

As classificações brutas permanecem intactas. O PASS posterior de Epoch no FULL5 não demonstra a causa da indisponibilidade de `brokerFor` na fixture histórica do FULL4. **Epoch e Alladin anteriores permanecem OPEN_CAUSE_UNCONFIRMED**; a nova falha Alladin W6 também continua sem causa confirmada. Não atribuir automaticamente todas as falhas ao mesmo mecanismo.

## Próxima verificação e critérios de entrega

O caminho recomendado é executar os verificadores originais Alladin e Planejamento sequencialmente, com proteção temporária contra suspensão previamente ativa, recibos separados e registro de horários e transições de energia. Não alterar timeouts, asserções ou `wait_until`. Se W6 reaparecer, um diagnóstico passivo de navegação/rede será mais adequado que o wrapper anterior concentrado em cliques.

Os focais anunciados como em andamento não possuem resultado incluído neste parecer. Um eventual PASS focal não apaga os incidentes nem substitui um FULL íntegro. Novo FULL exige coordenação humana; o gerador de aprovação final não deve aprovar com o resultado atual. Aceite humano permanece separado.

## Evidências consultadas

- `full-attempt5-114pass-2fail.json` e `full-final.json`.
- `full5-integrity.json`, `freeze-before-full.json` e `protected-sources.json`.
- `full5-environment-triage/triage.json`, `README.md` e `planning-receipt-excerpt.json`.
- `tools/.artifacts/app-efficiency-full-20261027T233826678834/hedge-prop-browser/results.json`.

SHA-256 de `full5-integrity.json`: `f57786d9575d7a8404cb91c9ef61706e097518316dd2c1dc172a824029d3e19c`.
SHA-256 de `full5-environment-triage/triage.json`: `b5f9adb826e705808c727b27f25d69dc817b54329a3ac16bbdbce857f13b8d74`.


## Apêndice — focais originais após FULL5

Conferência documental em 28/10/2026, após a conclusão dos focais às 00:52:55. Nenhum teste ou navegador foi executado por esta revisão; somente este apêndice foi acrescentado, preservando integralmente o parecer anterior.

O recibo `full5-awake-focals/receipt.json` registra execução sequencial, sem wrapper, dos verificadores originais:

- Alladin: saída 0, de 00:51:20 a 00:52:03, duração ativa de 42,98891325 s.
- Proporções do Planejamento: saída 0, de 00:52:03 a 00:52:55, duração ativa de 52,155845334 s. O recibo próprio confirma **94 casos PASS** e fontes inalteradas.

Os hashes dos dois logs preservados foram confrontados com o recibo e correspondem. SHA-256 de `full5-awake-focals/receipt.json`: `a7cf6fbd776f19b779b938e128bd8b02690dbe280f2677b50cda8ba9a18bc3f1`.

`awake-observation.json` documenta `pmset -g assertions` às 00:52:29: o processo caffeinate 81074 mantinha asserções temporárias contra suspensão ociosa do sistema e da tela em nome do supervisor 81072. `FULL5-AUDIT.json` registra que a proteção encerrou com seu processo; essa saída foi conferida documentalmente, sem nova consulta de processos por esta revisão. Não se infere desse único instante observado uma captura contínua de todos os estados de energia.

O confronto de hashes foi repetido após os focais: **1.621 arquivos congelados e 86 protegidos, sem divergências**. O README agora registra corretamente o FULL5 reprovado e os focais separados; o inventário identifica a fotografia inicial de preservação como histórica e remete à auditoria posterior de 28 caminhos alterados em relação ao baseline.

**FULL5 continua NÃO APROVADO, com 114 PASS / 1 PRODUCT_FAIL / 1 TEST_HARNESS_FAIL.** Os focais mostram sucesso nas condições desta execução; não demonstram a causa precisa das falhas anteriores nem substituem um FULL íntegro. Epoch/Alladin históricos continuam OPEN_CAUSE_UNCONFIRMED; o mecanismo da falha W6 e o mecanismo exato do timeout de Planejamento não foram encerrados. FULL6 ainda depende de coordenação humana. Nenhuma prontidão integral ou aprovação humana é declarada.
