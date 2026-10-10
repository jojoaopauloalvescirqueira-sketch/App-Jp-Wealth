# Suplemento independente — falha de link do CI e delta do juiz

**PASS no escopo da correção local do comando de link.** O CI1 permanece FAILURE, sem apagar ou reclassificar sua tentativa. A nova aprovação de CI depende de execução futura no Ubuntu.

## Falha observada e proveniência

O run37872820141 terminou com39PASS,0PRODUCT_FAIL e1TEST_HARNESS_FAIL. Família `jpw_genetrix_risk_test`: clang++ falhou ao ligar `SHA256`, antes da execução de qualquer assertion. O comando não continha `-lcrypto`; o shim compartilhado usa CommonCrypto em Apple e OpenSSL nas demais plataformas. O defeito é do aparato de teste, não evidência de erro na fórmula ou execução do Supervisor.

`tools/jpw_genetrix_risk_test.py` e `tools/leverage_config_test.py` são byte-idênticos na base7f082848 e no head90b39df7… da tentativa falha; a condição já existia. O pipeline ampliado incluiu a família antes omitida. O metadata do run vincula o head do PR, mas o recibo do host registra o checkout efetivo do merge sintético GitHub `b871ca267c705bfdf30ed9a5642a6084c66e37d1`; ambos são preservados. Artifact11590939021 e logs foram obtidos independentemente por API.

## Delta examinado

A mudança de hash `e9a445c66df1ceb0323cf7707d66119cb76179bc7e6ffa61d1698927883886dd` → `bd4e00a853f72dca015b6d8978287b9132fa842cc675bcb93f72e46625e3f5a7` contém somente `import sys` e inclusão de `-lcrypto` quando `sys.platform != 'darwin'`. Removidas apenas essas adições na AST de comparação, todo o restante é idêntico: strings C++ embutidas, critérios, assertions, traduções e resultados esperados. `-Wall`, `-Wextra` e `-Werror` são conservados. Workflows não foram alterados.

Executei três processos novos controlando o valor de platform na construção extraída do próprio comando: Darwin conserva exatamente o argv anterior; Linux e Win32 acrescentam somente `-lcrypto`. Referências determinísticas rejeitam o comando sem essa ligação no ramo não Darwin e a retirada de `-Werror`. São controles de construção de comando, não uma compilação Linux. Docker/Podman/Colima e OpenSSL local não estavam disponíveis; não foi simulada uma prova nativa inexistente.

Os132membros canônicos, ZIPa9a77…/760092bytes e fingerprint111inputs9650de… continuam iguais. Nenhum produto, fórmula, norma, fixture, expectativa ou workflow foi editado pelo revisor. O novo juiz precisa de seu próprio freeze/recibo; os resultados R3/R5/R7 anteriores mantêm seus bytes e alcance históricos.

## Limites

Até este checkpoint, o Quality Gate1 permanece em andamento e o novo CI de link não foi executado. Não aprovar merge com o run obrigatório vermelho. Mac host, Ubuntu host, MetaEditor e interação MT5 são camadas diferentes; nativoMT5 continua NOT_RUN/BLOCKED.

Provas: `LINKER-SUPPLEMENT.json`, `baseline-linker-preexistence.json`, `linker-control-1.json` a `linker-control-3.json`, `02-MT5Host-artifact.zip`, `mt5-host.json`, `jpw_genetrix_risk_test.log`, metadata/jobs API01–03.

## Recibo local posterior examinado

Li independentemente o `mt5-host-R8.json` produzido pelo autor: 40/40 PASS, `inputs_unchanged=true`, vinculado ao novo juiz `bd4e00a…`. Seu log de risco registra 51 assertions PASS, compile/execute host exit0, com compilação e execução nativas em `NOT_RUN`. Este parecer observa o recibo; não declara execução própria dessa suíte nem comprova link no Linux. SHA256 do recibo: `803523cb446bcc2223079bc3cc4c36a94ae9f87a8fea6d571f34b960cfbc6982`. O freezeR8 contém somente a adição condicional do link e os dois ajustes EOF já revisados em relação ao runtimeR3. O fullR8 e o novo CI exigem seus próprios resultados completos.
