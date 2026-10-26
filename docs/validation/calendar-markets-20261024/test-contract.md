# Calendário e Mercados — escopo dos verificadores

Base: a4bf278cd4dc38bbaa5b905ed17a79e33684fb67, branch codex/calendario-mercados-20261024. Fontes do oráculo: pedido/plano humano delegado e docs/superpowers/plans/2026-10-24-calendar-markets.md. Nenhum gate, helper global, política financeira, norma, produção ou dado real foi editado por este executor de testes.

## Expectativas deliberadamente substituídas

- tools/market_hours_integration_test.py: antigo item visível tools-market-hours passa a ausência desse item e presença de tools-calendar com título Calendário e Mercados. Child atual passa a tools-calendar. A navegação pelo destino legado continua obrigatoriamente aceita, abre a exploração e foca marketHoursTitle. A matriz, guardas, congelamento em modal/saída, seleção, descarte, 16 bolsas e preservação integral de S/localStorage permanecem.
- tools/navigation_ia_test.py: lista de filhos de Ferramentas deixa de exigir tools-market-hours independente. Nova asserção exige aceitação de tools-market-hours com requested preservado, canonical/child tools-calendar e localView {surface:tools,view:market-hours}. Demais checks intactos.
- tools/calendar_markets_test.py é novo focal standalone: 21 IDs, host HTTP real + calendários sintéticos com motor/view/controlador reais. Não está ligado automaticamente ao quality_gate/CI; os gates e runners existentes foram preservados.

## Evidências e limites

- tests-red/report.json: RED inicial de quatro contratos ausentes, antes da produção (nome, canonical, overview e API). Nenhum pageerror.
- tests-review-p2-red/report.json: RED de foco roubado após retry assíncrono e erro de snapshot invisível na exploração móvel com mapa recolhido, antes dos fixes correspondentes.
- tests-ui-first-scoped/report.json: RED de alvo B3 22.58 × 44 px, antes do min-width 44 px.
- tests-cold-alias-red/report.json: RED de âncora fria desktop y460.67; tests-cold-alias-green/report.json: GREEN após correção, 390 e1440 px.
- tests-summary-focus-red/report.json: RED de perda de foco em nó sobrevivente quando outro item sai do top3; caso removido→toggle já passava.
- tests-combined-candidate/report.json:17 PASS/1 PRODUCT_FAIL, antes da correção de âncora fria. Não é recibo final.
- integration-http-candidate/result.json: PASS,48 apresentações e8 reflows equivalentes200%; native zoom NOT_RUN. Execução precedeu últimos fixes, requer recibo final do candidate estável.
- navigation_ia_test.py: exit0, NAV1..NAV3 PASS, antes dos últimos fixes.
- tests-final-19/report.json:19/19 PASS, nenhum pageerror, stableInputs true. A adição subsequente CM-UI-02 altera apenas o teste.
- tests-internal-alignment/report.json: CM-UI-02 PASS em320/390/720/1440 px; Range dos textos, alinhamento interno do toggle/quicklink até2 px e nomes à esquerda, sem sobreposição.
- tests-final-20/report.json:20/20 PASS, nenhum pageerror/falha, stableInputs true; teste04e2090c707e9459e2281e5ca185564215ec7657fe798d8a074e0c2cf50aa4b7.
- tests-final-21/report.json:21/21 PASS, nenhum pageerror/falha, stableInputs true; teste957319a3159232db4c5a01af5f6422612e26e99198ccd1d937ba2cd87d3f4bb5. CM-UI-03 exercita zoom nativo do engine por preferência do Chromium1223, em perfil temporário headless, sem override de viewport: outer1440/inner720=2,CSSzoom1,DPR2 em4layouts ×2temas ×resumo/full. Verifica overflow local, alvos44CSSpx, texto centralizado até2CSSpx, navegação compatível, seleção, foco e retenção de nós/filtros; estado/storage preservados. Oito capturas native200-*.png. Não comprova aceite humano, janela física ou Safari.

As tentativas tests-behavior-second e tests-viewport-diagnostic foram interrompidas com exit130 durante diagnóstico do harness: expressão evaluate terminava em atribuição de função e Playwright a invocava, aguardando Promise controlada. Correção: wrapper de bloco com retorno vazio. Não são RED de produto nem GREEN. Outras correções do harness: relógio explicitamente pausado, aguardar catálogo carregado, fixture com ancestor real #tools para CSS escopado e esperar fatos atuais após avanço de dois minutos.

## Contraprovas pela mesma entrada

Cada comando narrow retornou PRODUCT_FAIL no contrato alvo, sem pageerror e com stableInputs true. Fontes do produto foram copiadas para os próprios diretórios temporários; originais intactos.

- --mutant eager-full --only CM-API-01: montagem antecipada de fullDOM é rejeitada.
- --mutant second-cadence --only CM-LIFE-01: cadência indevida de1s no resumo é rejeitada.
- --mutant exclusive-horizon --only CM-SUM-02: troca de <= por < no horizonte24h é rejeitada.
- --mutant duplicate-nav --only CM-HOST-01: injeção runtime de item duplicado no host sintético é rejeitada.
- --mutant misaligned-content --only CM-UI-02: padding assimétrico da fixture desloca texto5.703 px enquanto mantém caixa246 ×44 px; a verificação de conteúdo rejeita a violação que um teste apenas de caixa aceitaria.
- --mutant css-native-substitute --only CM-UI-03: preferência100% + CSSzoom2 produz outer1440/inner1440=1,CSS2,DPR1 e é rejeitada pelo oráculo nativo. Recibo counterexample-css-native-substitute/report.json, sem pageerror e stableInputs true.

Recibos iniciais em counterexample-{eager-full,second-cadence,exclusive-horizon,duplicate-nav,misaligned-content}/report.json; reexecuções com a revisão20 em final-counterexample-*/report.json e revisão21 em final21-counterexample-*/report.json. São violações representativas, não prova exaustiva nem substituto da revisão independente.

Comando/runtime utilizado: JP_WEALTH_CHROMIUM apontando para chromium-1223/Google Chrome for Testing e .superpowers/sdd/2026-10-21-planning-monthly-inline/runtime/bin/python3 tools/calendar_markets_test.py --out-dir /private/tmp/jpw-calendar-markets-20261024/tests-final-21. Nenhuma dependência instalada. Fixtures e resultados são sintéticos/temporários. Sem commit, push, merge ou publicação.

## Consumidores legados reconciliados após FULL1

A primeira execução completa registrou 100 PASS e dois PRODUCT_FAIL brutos, conservados em full-first.json. NoCuda e MiniGames comparavam o catálogo com a antiga lista de seis entradas. A causa identificada foi TEST_HARNESS_FAIL: oráculo de submenu deliberadamente superado pelo plano humano, sem falha demonstrada nos downloads ou jogos. O recibo bruto não foi reclassificado nem transformado em verde.

- `tools/nocuda_tools_test.py`: remove somente o destino independente da lista exata; a navegação de teclado exige NoCuda → Calendário → NoCuda → Calendário → Enter. Dois trechos alterados, mantendo as demais provas. RED original e GREEN completo de 130 checks nos recibos próprios, com revisão independente.
- `tools/minigames_test.py`: remove somente o literal `tools-market-hours` da lista exata, preservando MiniGames no final e todos os demais bytes. RED original e GREEN completo de 32 apresentações, guia e três distribuições, com revisão independente.

Ambos estão enumerados no CHG separado dos verificadores. FULL2 exige resultado próprio no candidato final; os focais não o substituem. Runner, CI e gates permanecem intactos.

## Resultado final observado

FULL3 exit0/102PASS, UI370PASS; verificador focal repetido após atualização informativa do plano:21/21PASS, stableInputs true, sem falhas ou pageerrors. Código do teste continua SHA957319a3159232db4c5a01af5f6422612e26e99198ccd1d937ba2cd87d3f4bb5. Recibo atual final21.json, anterior preservado. Nenhum runner/gate foi editado. FULL1 e FULL2 mantêm suas classificações históricas; fidelity permanece ENVIRONMENT_ERROR explicado.
