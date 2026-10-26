# Revisão independente — ajuste do oráculo MiniGames

A0 somente leitura. PASS focal da revisão do delta: uma linha altera apenas a lista exata de filhos de Ferramentas, removendo tools-market-hours, conforme o submenu único aprovado. A assertiva de população/ordem permanece exata e MiniGames continua obrigatoriamente como último destino.

Comparação byte a byte executada pelo revisor: current == a4bf278:tools/minigames_test.py com uma única substituição de literal tools-calendar,tools-market-hours,tools-nocuda por tools-calendar,tools-nocuda. A cópia minigames-red/source-original.py é idêntica ao baseline. Hash original1a23f7b760b204453bcf876b8294801ddba2c0885598ea211bf5fe4e63d3786a; adaptado58ed0ebf26f3c78b864f3b2cdfc7ebcbdcab58d61710625717b5098461dfea50. git diff --check executado pelo revisor:PASS.

Arquivo inteiro inspecionado. Nenhuma proteção de catálogo3jogos, montagem única, controles, preservação de motor/rascunhos, ciclos de pausa, diálogos/Finalizar, estado/armazenamento, foco, matriz, guia ou distribuições foi retirada/relaxada. Runner/gates e produto não mudam neste ajuste.

RED lido em ../minigames-red/stdout.txt: AssertionErrorL23, seis IDs esperados contra cinco IDs aprovados. A classificação causal TEST_HARNESS_FAIL é adequada para esse oráculo superado; o primeiro FULL conserva seu raw PRODUCT_FAIL e não vira aprovação.

GREEN do executor confirmado exit0 sem flags; stdout lido em ../minigames-green/stdout.txt mostra MINIGAMES_PASS (1mount,3ciclos,3diálogos,32apresentações), guiaPASS, modular-file/portable-alone/PWAofflinePASS,140respostasSW. O revisor não executou FULL. Novo FULL obrigatório no candidate final.

Inventário do CHG TESTS e contrato do plano conferidos: NoCuda e MiniGames estão enumerados, com antes/depois delimitado. A pendência documental assinalada na revisão anterior de NoCuda está fechada.
