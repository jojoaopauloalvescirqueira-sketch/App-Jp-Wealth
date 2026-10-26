# Triagem A0 — timeout do verificador visual completo

25/10/2026. **A evidência sustenta esgotamento do limite global ao entrar no último bloco; não demonstra congelamento, defeito de UI ou latência causada pelo CloudDocs.** A origem do tempo adicional ainda não foi isolada. Nenhum teste concorrente foi iniciado pelo revisor, e nenhuma fonte/configuração foi alterada.

## Resultado bruto e fronteira

Li full-final.json:101PASS,0PRODUCT_FAIL,1ENVIRONMENT_ERROR. O check ui-visual-quality terminou com returncode124 e900,017s; quality_gate.py:163–184 aplica subprocess.run(timeout=900) e registra o timeout como erro de ambiente. Isso é contagem de checks; o trecho parcial de stdout não permite promover todos os casos UI a PASS nem dispensa os casos finais/coverage. O recibo full-input-integrity.json registra679inputs,changed=[],unchanged=true para build8c127c2f92de375e. Não fiz nova execução de gate nem conferência de todos os679arquivos durante o standalone do principal.

O último PASS disponível é compact-native200-submenu-dark. O código chama em seguida o fim/cleanup desse contexto e closure.native_zoom, depois coverage-missing-and-zero-rejected e validação/JSON. O diretório residual contém **closure-native200-r9l7kcav**, mas nenhum perfil visual-native200. Isso comprova que o perfil de closure chegou a ser criado. O ponto não está limitado a context.close do bloco compact: inclui launch, setup, seed, select, verificação de zoom ou ação do primeiro record de closure. Não há print de início de cada uma dessas fases.

## Comparação temporal verificável

| Evidência | Valor |
|---|---|
| FULL atual começou |00:56:34-03|
| Soma dos checks anteriores à UI |59,847s|
| Início aproximado da UI |00:57:33,847-03|
| Limite aproximado da UI |01:12:33,847-03|
| Birthtime do perfil closure residual |01:12:32,464499-03|
| Orçamento restante estimado nessa criação |1,3825s|

O cálculo é aproximado: started_at tem precisão de segundo e a soma não inclui todo overhead do runner. Ainda assim, o perfil do último bloco foi criado muito perto do teto900s. Não há base para chamar de travamento um bloco interrompido nesse ponto.

A rodada anterior de UI, em docs/validation/dante-20261024/full-ui-visual-quality.json, contém413PASS/source_unchanged=true e foi registrada pelo FULL anterior em850,914s. O hash de ui_visual_quality_test.py é o mesmo atual, assim como os testes compact e closure. Na rodada anterior:

- fim do último compact até início do primeiro closure:24,235692s;
- primeiro closure até fim do teste de coverage:3,863733s;
- fim do último compact até JSON final:28,386868s.

Essa comparação demonstra que o trabalho restante era historicamente bem maior que o orçamento estimado atual. Não identifica o motivo de as fases anteriores consumirem mais tempo. O resultado anterior também não aprova os bytes atuais.

## Cleanup observado e código

ui_visual_quality_test.py:native_zoom usa um perfil por bloco, criado em report.out. Após os loops, assert_fixture_requests é uma asserção síncrona sobre lista em memória; depois chama context.close e, no finally externo, shutil.rmtree. O helper de fixture não faz espera de rede nesse ponto.

closure.native_zoom (planning_monthly_close_test.py:340–358) também cria perfil em report.out, inicia contexto persistente com zoom nativo, prepara a fixture e registra oito combinações; fecha o contexto e remove o perfil nos finallys. Uma falha ordinária deveria atravessar esses finallys, mas o timeout externo mata o processo Python: a implementação local de subprocess.run chama process.kill ao receber TimeoutExpired. Assim, o finally do teste/remoção do perfil e escrita do JSON final não são garantidos nessa interrupção.

O perfil residual é evidência de arquivo não removido, **não de browser ainda vivo**. Snapshot passivo de ps não encontrou processo com --user-data-dir desse perfil antigo. Nenhum processo foi encerrado e nenhum diretório foi removido pelo revisor. Uma eventual limpeza posterior precisa distinguir artefato diagnóstico, processo antigo e contexto do standalone atual; não usar remoção/kill genérico.

## Relação com o delta e hipóteses ainda abertas

Os scripts visual/compact/closure são byte-exatos aos do recibo antigo413PASS. Entre os inputs registrados naquele recibo e os atuais diferem build-id, settings-modal, módulo calendário, manifest e teste calendário. Isso limita a investigação, mas não prova que uma fonte alterada explique o tempo.

Tempo acumulado maior, inicialização/cleanup de contextos persistentes e operações de arquivo são mecanismos possíveis. O fato de perfis e reports estarem sob CloudDocs não mede latência de sync/filesystem, e não há medida causal que atribua o timeout a essa pasta. Também não há evidência de intervenção humana, zoom manual, CPU/scheduler, corrupção de perfil ou bloqueio de context.close. Não atribuí causa a nenhuma dessas hipóteses.

A rodada standalone que o principal iniciou usa a API existente, o mesmo limite900 e saída em /private/tmp, com log sem buffering. Ela pode indicar onde e quando o progresso termina e se o trabalho completo cabe no orçamento. Uma rodada mais rápida fora de CloudDocs, isoladamente, ainda tem fatores de execução diferentes e não comprova causalidade de I/O. Conferir413IDs/cobertura, source_unchanged, exit e cleanup, preservando o timeout anterior. Não ampliar limite, pular closure/coverage ou mudar oráculos automaticamente.

## Limites e próxima evidência

Standalone estava em execução ao fechar este relatório; não foi interrompido nem executado pelo revisor. Seu resultado deve ser analisado separadamente. O FULL bruto continua101PASS/1ENVIRONMENT_ERROR, sem aprovação integral. Os PASS registrados de notification/calendar/Dante e demais blocos preservam seu recorte, sem suprir closure/coverage final.

Se repetir perto do mesmo ponto, timestamps de entrada/saída das fases seriam uma proposta de instrumentação delimitada para localizar o tempo; não foram adicionados nesta triagem. Sem ensaio concorrente, mudança de fonte, pacote novo, escrita em contratos ou operação Git de mutação.

## Identidades

- `tools/ui_visual_quality_test.py`: `f7a176ab58c048801326d84c626d9c2d4524cd38f01c69971e70d2b5977d8b03`
- `tools/planning_monthly_close_test.py`: `71c6a5f8f73cd2fae7af6f518a1a902dab0448a7bf3a21a3c938e9e601004405`
- `tools/planning_compact_table_test.py`: `4fb30ff95b9911e453e719591a08ec7a15babe430e35890ddf878a131250da52`
- `tools/quality_gate.py`: `074fd1d63154b50a1eefcbc3feac4c9f41e1d6356615bc089e04b5adffb2cd2a`
- Recibo `full-final.json`: `90247286a4d3b65af9b6c45783bcd78769c40b8d8f53b425a7d824b004b4283e`
- Recibo `full-input-integrity.json`: `1c1b67a6cf53fc0c912b66fb1f7a0d8917d05ceae3ab0d68599b8aabcf36ab7e`
- Recibo `visual-timeout-output.log`: `b1e4beec9c1540494e1cd7f9979cc7b652ffd54e066dc3c7a244be09578cb8d4`

Única escrita desta triagem: `/private/tmp/jpw-dante-calendar-20261025/VISUAL-TIMEOUT-TRIAGE.md`.


## Adendo A0 — focal visual completo concluído (25/10/2026)

**Veredito:** o focal `selection=all` tem evidência íntegra de **413/413 PASS**, `exit=0`, sem timeout, em **853,471 s**, mantendo o limite de **900 s**. O revisor leu o resultado e o recibo do comando; não iniciou testes nem navegador. Nenhum achado P0–P3 nesta conferência do focal.

### Cobertura e preservação dos oráculos

- Foram conferidos os 413 IDs exigidos e os 413 casos executados: todos PASS, únicos, sem IDs faltantes ou inesperados e sem marcações de skip/xfail/todo. As listas de IDs exigidos e executados são exatamente iguais, inclusive na ordem, às da execução anterior em `docs/validation/dante-20261024/full-ui-visual-quality.json`.
- Os oito casos `closure-native200-*` e `coverage-missing-and-zero-rejected` terminaram PASS; assim, o trecho ausente no FULL interrompido pelo limite foi efetivamente executado neste focal. O controle negativo de cobertura permanece presente e PASS.
- `required_case_ids`, `matrix`, tolerância, descrição do oráculo, limites e validação da configuração são idênticos ao recibo anterior. O hash de `tools/ui_visual_quality_test.py` coincide com ambos os recibos (`f7a176ab58c048801326d84c626d9c2d4524cd38f01c69971e70d2b5977d8b03`). Os hashes de `planning_monthly_close_test.py`, `planning_compact_table_test.py` e `quality_gate.py` continuam os registrados acima; nenhum oráculo foi alterado para obter este resultado.

### Bytes e recibos

Conferência independente por SHA-256 de **679/679 inputs** do freeze `frozen-inputs.json`: nenhum arquivo faltante ou divergente, build `8c127c2f92de375e`. Os **160/160 arquivos** do mapa `source_sha256` do focal também coincidem com os bytes atuais; `source_unchanged=true` no recibo. O mapa preserva todas as 160 entradas do recibo anterior; suas cinco diferenças são os deltas já examinados de settings, calendar, teste calendar e gerados oficiais (manifest/build). Não há delta novo de teste visual, closure, compact ou runner.

- `visual-isolated/ui-visual-quality-results.json`: `18e6db61e0a114535e794b170db211c564fb58c241da2b5bec1efa8e5330371b`
- `visual-isolated-command.json`: `bd12b0d8275113d052ac8a5b1bfce5895852cc0b240873b98e7c5f671b2c0b8a`
- `frozen-inputs.json`: `11cf8e2809ac3c871a729c5533ab3a86e5ef76a08511ea069b63e0a292639b65`

### Limites mantidos

Este é um **PASS focal**, separado do FULL. O FULL bruto anterior permanece 101 PASS / 1 ENVIRONMENT_ERROR por timeout; o novo FULL padrão em execução precisa do próprio resultado. A aprovação focal não se transmite ao FULL. O ensaio isolado, com saída via API existente `--out` em scratch, não demonstra que CloudDocs ou I/O causaram o timeout anterior. Permanecem os limites de aceitação humana, Safari, leitor de tela, toque físico e demais módulos descritos no recibo. Nenhuma fonte, teste ou contrato foi editado nesta conferência; a única escrita foi este adendo.
