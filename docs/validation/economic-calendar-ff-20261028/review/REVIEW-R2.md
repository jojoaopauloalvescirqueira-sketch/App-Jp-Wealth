# Revisão independente R2 — controles e defeitos encontrados na revisão

R1 continua histórico. Esta atualização registra somente evidência observada depois das correções.

## Correções verificadas independentemente

- Mesmos três probes de runtime (status contraditório, cache incompatível sem aviso, moeda/fonte trocadas): RED→GREEN sem mudar estímulo/oráculo. Executei o juiz aplicado23 casos:23PASS, exit0 (`runtime-23-independent-green.json`). O caso22 preserva a projeção semanal FF-only/instant/fourHigh; o23 rejeita moeda/fonte incoerentes também no pacote local. Tabelas de fontes/coverage seguem públicas e síncronas; não houve uso de S/writer nesses casos.
- Validador do coletor corrigido:32 testes independentes passaram, exit0, com controles de curadoria e preservação de saída. Byte final `fetch_news.py`955906fe8ad88b7e079b2f293112a19e7fe90335f83c89c6ff7278ae6af14d1a; juizcb07378716e41b1577a29b1cd9fe70b861b20b2e759e7c4085a69194decf20a7. Testei também os offsets+01:99/+24:00 (recusados) e-04:00/Z (aceitos). Recibos `collector-32-final-independent-green.log`/`collector-final-review.json`. As nove contraprovas documentadas usam o mesmo hash do juiz, com retorno1; não executei os nove mutantes novamente, apenas li os recibos e os vínculos.
- Dois focos em Fontes/Atualizar: mesmo helper próprio em navegador headless real passou após fix (`ui-info-focus-GREEN.json`, RED separado). Nenhuma escrita financeira/pageerror.
- Foco da fonte FF entre snapshots com novos IDs: mesmo helper próprio passou após fix (`ui-economic-focus-GREEN.json`, RED separado). Dataset usa observação exata +href, matching único, e não cria identidade econômica persistente. Caso permanente UI inclui controle que muda o horário e exige não herdar foco por título/dia. Não há achado aberto remanescente nesses três controles de foco.

## Juízes e escopo conferidos

- `monthly_economic_feed_test.py` chama os juízes permanentes de runtime e coletor. O check já integra STANDARD/FULL; assim não são necessários novos IDs nem modificação do runner116.
- Harness unitário com baseline público vazio explicitamente injetado em RAM é apropriado para cache/adaptador e mantém asserções. O caso puro da fonte real e os testes de pacote/distribuição são outras provas; não confundir23 casos sintéticos com cobertura integral da alimentação/UI.
- Enum backup permanece schema1 e sobe5→9. CritérioEURinválido foi legitimamente trocado porXXX; os testes antigos de preferência5 permanecem. O novo `expanded=check(...)` só valida; sua mensagem não deve alegar roundtrip. Ainda é necessário comprovar9 moedas por export/import/retomada real, além do reload9 da distribuição e preservação5.
- `ff_news_cache_test.py` ainda exigia igualdade textual do workspace após fetch no momento da leituraR2. Substituição aprovada deve verificar atualização econômica real sem resetar host/data/filtros/rascunho/foco/agenda/S, preservando quotas/retry/legado4High e exceções. Os casos `info-focus`/`economic-focus` isolam UI com stub de query; falta vínculo permanente completo transporteFFv2→adapter→consulta16→lista/marcador se o check de cache não o exercer.
- Nenhum teste inválido deve ser removido silenciosamente: atualizar apenas pressupostos expressamente superados, capturar RED real e contraprovas. O caso de envelope/scriptunsafe permanece.

## Template de agendamento — revisão separada N3

Li o template aplicado `infra/ff-news-feed/.github/workflows/update-news.yml`, SHA9ba37cdc7bd47a6d9bdbcdc8f43e294d4da73735a95b1a32e91d65f7d77dec48, e confrontei os bytes baseline com HEAD+manifestbefore (idênticos para esse arquivo). Preserva checkout@v4, permissãocontents:write e cron30m preexistentes; acrescenta guard externo explícito `JPW_ECONOMIC_FEED_V2_ENABLED == 'true'`, uma coleta `--fetch-ff` e publicação dos três caminhos públicos. Este caminho aninhado não é workflow ativo do repositório do app. Não executei, habilitei ou publiquei o template. Nenhum blocker técnico identificado para preparação local.

O CHG/brief ainda diziam N3 “somente verificadores” no momento da leitura; devem registrar este caminho exato como template CI/controlplaneN3 dentro da preparação aprovada. Não tratar como N1 nem alegar cron ativo. A ativação/publicação do repositório externo permanece gate humano próprio. Na implantação separada, garantir que os novos arquivos públicos estejam rastreados: `git diff --quiet` sozinho ignora arquivos inéditos, embora o arquivo legado rastreado mude normalmente a cada coleta.

## Limites do parecer

Review focal de código/juízes, provas sintéticas e três controles de foco em navegador headless isolado; nenhum teste nativo, full final, dado pessoal, alteração tracked pelo revisor ou ação Git/publicação. Não foi confirmada execução agendada nem permissão jurídica. O full atual, as distribuições reconstruídas, contraprovas finais, compatibilidade de backup e aceite visual humano não são derivados destes resultados.
