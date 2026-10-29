# Auditoria final FULL — PASS técnico delimitado

Build `aabc8d09faff4aee`; branch `codex/calendario-tabela-ff-20261028`; HEAD `3e24f60f8cfe87f79335f40e95a0927379a9f834`. Esta auditoria leu arquivos, recibos e AST; não executou testes, browser, gerador, rede ou mutações no repositório.

O [FULL final](</Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/docs/validation/economic-calendar-table-20261028/full-final/full.json>) contém **116 registros brutos únicos, 116 PASS**, todos com returncode 0; PRODUCT_FAIL, TEST_HARNESS_FAIL, ENVIRONMENT_ERROR, BASELINE_FAIL e NOT_RUN estão zerados. Reconstruí FAST (4), STANDARD (71) e FULL (116) a partir do AST atual de `quality_gate.py`, sem importá-lo ou executá-lo: IDs, ordem, strings dos comandos e argv coincidem integralmente. A lista literal dos 116 comandos e seus estados consta no [JSON da auditoria](</private/tmp/jpw-economic-calendar-table-20261028/tests-proposal/FINAL-FULL-AUDIT.json>).

Execução registrada de 2026-10-29T11:23:25-03:00 a 2026-10-29T12:12:59-03:00, duração do supervisor **2974.432 s**. `full-exit.json` registra gate exit 0; `DELIVERY-IDENTITY.json` registra supervisor exit observado 0. O código congelado do supervisor também resolve para saída 0 nas condições registradas; o recibo `full-exit.json` não possui campo direto de exit externo do próprio supervisor.

Recalculei os **1648 hashes** de [INPUT-FREEZE](</Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/docs/validation/economic-calendar-table-20261028/full-final/INPUT-FREEZE.json>) e reenumerei a população com a mesma seleção `git ls-files -c -o --exclude-standard`: **zero alterados, novos ou removidos**. HEAD e branch atuais coincidem com freeze e entrega. As cinco fontes de controle N3/V3, gate, runner visual e fontes JS/CSS coincidem com os hashes congelados. O histórico `engine-counterproofs.json` é byte a byte igual ao before; SHA `1bc9e6ce6908fb46c4f1721eb2d1b2b488ebad05c22e75caca507aaf747e3fc3`. O resultado gerado preservado difere estruturalmente somente em `timestampUTC`. `caffeinateStopped=true`; o supervisor verificado termina e aguarda esse processo no `finally`; a ausência de processos próprios é reportada na identidade de entrega.

| Evidência filha do FULL | Contagem bruta e oráculo de integridade |
|---|---|
| Calendário | 22 IDs únicos, 22 PASS; inclui os cinco casos novos de tabela. |
| FF V3 | 186 nomes únicos, 186 PASS; 18 cenários; SHA do teste e fontes coincidem com disco e freeze. |
| Distribuição | 4/4 PASS, sequência exata HTTP, PWA offline, arquivo modular, arquivo portátil; 137 entradas before/after idênticas e vinculadas ao freeze; reloads 3/4/3/3. |
| Visual | 413 casos brutos e 413 required, ambos únicos, multisets iguais, 413 PASS. Submatriz calendário: 32 usuais + 8 native200 + 8 contraprovas = 48. Tolerância 2 px; zoom Chromium 200% registrado outer1440/inner720/CSS1. Gate visual: 894.997 s, abaixo de 900 s. |

Validei os quatro originais e os quatro gzips do [manifesto bruto](</Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/docs/validation/economic-calendar-table-20261028/full-final/RAW-RECEIPTS.json>): hashes coincidem e descompressão é byte a byte exata. O mapa visual de 153 fontes coincide com disco e freeze; os controles ausentes desse mapa estão vinculados separadamente pelo freeze global. Os cinco HTTP200 e seus hashes no [recibo da prévia](</Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS/docs/validation/economic-calendar-table-20261028/PREVIEW-DELIVERY.json>) coincidem com disco/freeze; esta auditoria não repetiu as requisições.

| Artefato | SHA-256 |
|---|---|
| FULL | `e9486e1b91770a9afb5178b3e835d4bd1233967d0408604c7fd79c9a390ff71b` |
| INPUT-FREEZE | `7ddf4ffba54e577148bad52a7a7a4a30251fdb9653d9030d05aeb7b31c653693` |
| full-exit | `9841398ee1511d974824209e8be76875400609921af83e1a5877bcb32c9aea98` |
| src/js/40-app/19-calendar-agenda.js | `8cfaec067a59ba393ff2aa53ad097196460e64e6de111945d92d3da21c47a518` |
| src/styles/app.css | `31e7659038d380c2348919a7ffa4229be125c5893d03540a89f728e3ad3aed5e` |
| tools/calendar_agenda_test.py | `655556061f9fbbecd28f73de0861ac2e05741a658d7da0777b2591da28ab7ddd` |
| tools/calendar_distribution_test.py | `cbaf54be1a5dd0ebecf80773158a86453f849fbf0ab8734a1ad32376065003a9` |
| tools/calendar_economic_table_contract.py | `35ea10d57ed2c8c4e6042ce14a88033cc232214f28790de9eacb9e9baf85c80a` |
| tools/calendar_visual_quality_test.py | `b883b966e1be638707da5c53999392cfc6ae02da36440500ddd18fc12970b95f` |
| tools/ff_news_cache_test.py | `a3f3a00c5a1ff8e1059bc7eb1fd8c69870a5ecf48d1ea2020b8033503194862a` |
| tools/quality_gate.py | `51fae2e0a9b25972d68c9d8e70023d28536fb4f590e386e8a518eecc568ab84d` |
| tools/ui_visual_quality_test.py | `2dacc347c77eade52358e1342d223e619f3e40250a03e47f1e556cae67a7370a` |

As 12 contraprovas isoladas corrigidas são evidência scratch anterior, não uma quinta execução filha do FULL. CP11 detecta perda da expansão antes da assertiva separada de foco; CP12 detecta alteração do texto antes da assertiva separada de cursor. Portanto, não comprovam isoladamente a sensibilidade negativa de foco/cursor. O primeiro recibo CP05 com matcher incorreto permanece classificado TEST_HARNESS_FAIL e não aprova 12 propriedades. Ver [inventário de testes](</private/tmp/jpw-economic-calendar-table-20261028/tests-proposal/FINAL-TEST-INVENTORY.md>) e [adendo visual](</private/tmp/jpw-economic-calendar-table-20261028/tests-proposal/inventory-visual-actual.md>).

Limites: PASS técnico da automação salva, sem aceite humano; Safari, leitor de tela e toque físico não executados; tinta do popup nativo de seleção não medida. Zoom nativo aqui significa zoom do Chromium, sem homologação MT5. Freeze cobre material versionado/não ignorado, excluindo saídas `docs/validation/`; não cobre integralmente dependências ignoradas, binários de ferramentas ou ambiente herdado. O argv de `learning-guide` usa ROOT como baseline; o valor ambiental `JPW_BASELINE_ROOT` não foi capturado separadamente. Não há inferência de publicação, operação com dados externos/reais ou validade financeira além das verificações expressamente registradas.
