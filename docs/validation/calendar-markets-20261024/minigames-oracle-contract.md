# MiniGames — remoção única de expectativa obsoleta

O contrato humano aprovado reúne Calendário e Mercados em um único item de Ferramentas. A raiz conferiu todo tools/minigames_test.py, explicitamente autorizou somente retirar tools-market-hours da lista esperada na linha23 e atualizou CHG TESTS/plano antes desta edição.

RED original executado antes de editar, exit1: assert na linha23 esperava seis filhos enquanto JPWNavigation.children('tools') retornava os cinco aprovados. Log minigames-red/stdout.txt; fonte intacta preservada em minigames-red/source-original.py, SHA2561a23f7b760b204453bcf876b8294801ddba2c0885598ea211bf5fe4e63d3786a. FULL1 bruto continua PRODUCT_FAIL em full-final.json; causa semântica desta ocorrência: TEST_HARNESS_FAIL por expectativa superada.

Mudança exata: remover um único literal tools-market-hours dessa lista. Comparação de bytes confirmou que substituir uma única ocorrência no original produz integralmente o arquivo candidato. Ordem dos outros cinco filhos, MiniGames último, hub com três jogos, Galton, motor, estado, lifecycle, pausa/RAF/observer, diálogos, foco, guia e distribuições não sofreram alteração. Diff salvo em minigames-expectations.diff; git diff --check PASS.

GREEN completo sem flags, exit0 coletado do processo: main PASS com uma montagem, três ciclos, três diálogos e32 apresentações; guia PASS; modular-file, portable-alone e PWA offline PASS, com140 respostas SW no último modo, mesmo controlador, motor executado e RAF oculto zero. Estado/storage são verificados pelo teste original. Fonte candidata preservada em minigames-green/source.py, SHA25658ed0ebf26f3c78b864f3b2cdfc7ebcbdcab58d61710625717b5098461dfea50. Log integral minigames-green/stdout.txt; recibo derivado minigames-expectations-receipt.json e minigames-green/result.json.

Runtime existente Python/Chromium1223, sem flags de seleção, dependências, gate ou produção alterados. Nenhum commit, push, merge ou publicação. O GREEN focal não substitui a auditoria independente nem o FULL2 da raiz; o primeiro recibo bruto permanece preservado.
