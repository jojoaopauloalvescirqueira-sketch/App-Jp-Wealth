# Revisão de aplicação do patch37 e atualização do manifest — 29/10/2026

Parecer delimitado em leitura do repositório; única escrita deste agente: este documento scratch. Nenhum browser, gerador, alteração de produto/testes/configuração, operação Git mutável ou rede externa foi executado por esta revisão.

## Resultado observado

PASS para a identidade aplicada do produto/patch37, preservação delimitada e correção do registro de hashes do manifest no estado examinado. Nenhum bloqueador material adicional encontrado nesse recorte estático. Isso não é PASS de testes de produto, FULL, distribuição ou aceite humano; tampouco autoriza o deltaFF/V3.

Raiz conferida: `/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS`.
Branch: `codex/calendario-tabela-ff-20261028`. HEAD: `3e24f60f8cfe87f79335f40e95a0927379a9f834`.

## Manifest: comparação direta antes/depois

Comparei `/private/tmp/jpw-economic-calendar-table-20261028/manifest-before-refresh.json` com `src/js/manifest.json` atual, usando parsing JSON, ordem da lista e cálculo SHA256 dos arquivos reais.

- Ambos têm exatamente127 entradas.
- Metadados de topo, inclusive runtimeAssets, são idênticos.
- Para cada entrada, path/order/section e quaisquer outros campos exceto sha256 são idênticos na mesma posição.
- Somente uma entrada muda: índice85/order85, `src/js/40-app/19-calendar-agenda.js`.
- SHA anterior declarado: `75c783bde598e03012648695de2e923cecf93509124d6d377daefc3b757616c4`.
- SHA atual declarado e calculado do produto: `1e2e518bef9dccca48790f9752c48ba62619cd64c128ec87c55c6c58c779c831`.
- As127 entradas atuais correspondem aos SHA256 dos127 scripts reais, sem divergência.
- Os127 script tags existem no index e preservam a ordem declarada.
- SHA256 do snapshot anterior: `11b6e2a9e8e510eb6163a3e12ad5bea56ccfc527032184b1bc8e0340f4e44223`.
- SHA256 do manifest atual: `e3acda276c1db4a1b11b420962f1b3bfe2ef6c2eaf5999c02f776a4333e09bb0`.

A leitura de tools/rebuild_monolith.py confirma o comportamento do mecanismo existente: somente com --refresh-manifest ele recalcula os hashes dos scripts declarados, mantendo os demais campos e a ordem. Não executei esse mecanismo; conferi o resultado em disco. tools/rebuild_monolith.py e tools/agent_preflight.py conservam os bytes-baseline.

## Produto e cinco testes

JS19 e CSS são byte a byte iguais às cópias finais de product-proposal:

- JS: `1e2e518bef9dccca48790f9752c48ba62619cd64c128ec87c55c6c58c779c831`.
- CSS: `f1007dfe4122ac80aa2e8260b4db91079ad5291cec5f1b2dd6ab0aa3910beb38`.

Calculei diretamente o SHA do patch scratch: `37a46edbd8e2c56e6327ce8dc8e42cc034c1063c2ef6a55520effa53bc8a39c3`. Os cinco arquivos aplicados correspondem exatamente a candidate-hashes.json desse patch:

- tools/calendar_agenda_test.py: `655556061f9fbbecd28f73de0861ac2e05741a658d7da0777b2591da28ab7ddd`.
- tools/calendar_distribution_test.py: `cbaf54be1a5dd0ebecf80773158a86453f849fbf0ab8734a1ad32376065003a9`.
- tools/calendar_economic_table_contract.py: `35ea10d57ed2c8c4e6042ce14a88033cc232214f28790de9eacb9e9baf85c80a`.
- tools/calendar_visual_quality_test.py: `b883b966e1be638707da5c53999392cfc6ae02da36440500ddd18fc12970b95f`.
- tools/ff_news_cache_test.py: `f66f357830f04a2c9f6eeb92ac469d8e04c190b6aa1a42aad161f65ebde859a7`.

O delta37-para-V3 permanece proposta: o ff_news_cache_test.py real ainda é o hash37 acima e contém as expectativas antigas sobre link visível e texto A confirmar. Não substituí essa expectativa nem interpretei a autorização antiga como autorização do delta posterior. A validade de tal expectativa é assunto separado da integridade do manifest.

## Causa e limites do reparo

A divergência do manifest é causalmente independente da mudança do juiz: o snapshot anterior ainda registrava o hash-baseline de JS19, enquanto o JS19 aplicado já corresponde ao produto tabular. O patch37 altera apenas cinco arquivos Python em tools; nenhum deles integra as127 entradas e nenhum altera o conteúdo de JS19. Atualizar as expectativas do FF não corrigiria esse hash, e atualizar o hash não resolve ou aprova as expectativas do FF.

O gerador existente permite reconstruir sem atualizar os hashes, quando --refresh-manifest é omitido. A condição observada é consistente com a reconstrução anterior sem esse argumento, conforme relato do responsável. A comparação antes/depois comprova que a correção atual limitou o manifest à referência do JS19 já aprovado; não alterou política, ordem ou implementação do preflight para obter PASS.

O preflight anterior BLOCKED e a aplicação do juiz após esse BLOCKED, reconhecida pelo responsável como erro de orquestração, continuam fatos históricos. O estado agora íntegro não apaga a execução anterior nem a transforma retroativamente em autorizada/conforme. Esta revisão não concede aprovação ao procedimento passado e não infere nova autorização N3.

## Preservação contra o baseline de3.578 arquivos

Nenhum arquivo-baseline ausente.3.560 hashes permanecem iguais. As18 diferenças observadas são exatamente:

- Produto/contrato já autorizados: JS19, CSS, CALENDAR-AGENDA.md e ACTIVE-TASK.md.
- Manifest: src/js/manifest.json, com a diferença única demonstrada acima.
- Quatro arquivos Python existentes do patch37; o quinto é o novo helper, inexistente no baseline.
- Nove saídas derivadas já abrangidas pela reconstrução autorizada: build-id.js, dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html e os sete payloads leverage/market-hours observados no rebuild anterior.

Todos os demais arquivos-baseline, incluindo fontes15/16, domínio, coletores, pacotes de dados econômicos, preferências/backup/persistência, escritores financeiros, quality_gate.py, ui_visual_quality_test.py, regression-memory.json, AGENTS/skills, geradores, index e sw, preservam seus hashes. Comparar hashes de payloads derivados com o baseline não prova conteúdo nativo ou validade de distribuição; nenhum teste desse tipo foi executado por mim.

## Verificação executada e pendências

Executei leitura/hash/comparações e `PYTHONDONTWRITEBYTECODE=1 python3 tools/agent_preflight.py --mode audit`: PREFLIGHT PASS,127 scripts; avisos de139 alterações e frescor material histórico permanecem explícitos. A detecção de nenhum processo rebuild ativo foi somente verificação de estado; o exit/sucesso do gerador pertence ao recibo do executor.

Browser/testes de produto/contraprovas/FULL116/visual413/distribuições/janelas nativas: NOT_RUN nesta revisão. Este parecer não amplia a autorização exata do patch37 para V3, não aprova FULL por inferência e não substitui os gates posteriores.
