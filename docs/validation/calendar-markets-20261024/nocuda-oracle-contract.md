# NoCuda — substituição limitada de expectativa obsoleta

Fonte do novo contrato: plano humano aprovado de Calendário e Mercados e delegação explícita da raiz para este path após o FULL1. A produção possui cinco filhos visíveis de Ferramentas e conserva tools-market-hours como destino compatível de tools-calendar. O teste antigo exigia um sexto item visível e uma etapa de teclado por esse item removido.

RED original antes da edição: exit1, `PASS http routes`, seguido de `AssertionError: http children` na linha49. Log em nocuda-red/stdout.txt, fonte original preservada em nocuda-red/source-original.py, SHA25680e79dc598db192284b50e6a35796f21c05f80432f1d6f5bd3a0546e5d65e20a.

Delta exato, somente dois hunks de tools/nocuda_tools_test.py: retirar tools-market-hours da lista esperada; substituir a travessia antiga por NoCuda →ArrowUp→Calendário, ArrowDown→NoCuda, ArrowUp→Calendário, Enter. Há asserção de foco em cada etapa e de rota após Enter. Nenhuma outra expectativa, gate, helper, dependência ou produção alterada. Downloads,49 linhas,3 âncoras, geração/schema/limites, drafts, proteção financeira/storage, HTTP/file/portable/PWA permanecem.

GREEN completo: exit0,130 checks em nocuda-green/result.json e nocuda-green/stdout.txt. Fonte candidata preservada em nocuda-green/source.py, SHA2562295d820781c7e05e031021c441bd4b7b801738f9fd9d60dfc2320cbb0217081. Diff em nocuda-expectations.diff. Inspeção derivada confirmou os checks de todos os três modos e a sequência completa de teclado/PWA; isso não é outra execução.

O FULL1 bruto permanece PRODUCT_FAIL, conforme registrado pelo runner. A causa semântica deste mismatch é TEST_HARNESS_FAIL por expectativa deliberadamente superada, e não uma regressão de produto. Este GREEN focal não substitui o FULL2 nem a revisão independente solicitada pela raiz. A raiz mantém o recibo bruto e executará o FULL final com o verificador ajustado. Nenhuma operação Git ou publicação realizada.

Comando: NOCUDA_EVIDENCE=/private/tmp/jpw-calendar-markets-20261024/nocuda-green JP_WEALTH_CHROMIUM=Chromium1223 .superpowers/sdd/2026-10-21-planning-monthly-inline/runtime/bin/python3 tools/nocuda_tools_test.py. A mesma configuração foi usada no RED, mudando apenas o diretório de evidência. Detalhes estruturados em nocuda-expectations-receipt.json.
