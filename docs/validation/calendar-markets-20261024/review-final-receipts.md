# Verificação independente final dos recibos

Escopo A0 somente leitura, sem navegador/suíte concorrente nem edição de produto, testes ou documentos oficiais. Conferência dos arquivos finais, fingerprints, condições e limitações; execução do gate foi observada pela raiz, e esta passagem verificou independentemente seus recibos e bytes.

## Resultado confirmado

- FULL3 final:102checks únicos, todosPASS/returncode0, zero demaisclassificações. JSON e log oficiais são cópias byte-idênticas de full-final3.json/.log temporários; a lista ordenada de102checks é a mesma do primeiro FULL. Branch codex/calendario-mercados-20261024, HEADa4bf278, árvore de trabalho candidata, build3a9f6157481ae050.
- UI dentro do gate:370/370casosPASS, cobertura exata/única, source_unchanged=true,370classificaçõesPASS, duração811.901s no runner. Todas as fontes declaradas pelo recibo UI conferem com o disco.
- Integridade:481inputscongelados sem drift; product-fingerprint também sem drift. full-input-integrity.json corresponde ao resultado102PASS e registra changed_after_run=[]. O inventário scope-audit agora coincide com os26paths rastreados alterados.
- Focal novo reexecutado após o gate e a performance:21/21PASS, zero failures/errors, stableInputs=true; todos os hashes atuais conferem, incluindo plano d52674351f3292d93b9fe12c46eba3eea92052e6995c2de572f0df6eb8b49d55 e teste957319a3159232db4c5a01af5f6422612e26e99198ccd1d937ba2cd87d3f4bb5. final21.json oficial é idêntico ao novo report.json; final21-before-oracle-doc-update.json preserva a fotografia anterior.
- Performance isolada:PASS;30seleções, mediana6.4ms/p957.2ms;137intervalos de desenho emarraste, mediana8.3ms/p959ms; zero desenhos por5s emrepouso/oculto/mapamóvelrecolhido; renderer/canvas retidos. SourceHashes do recibo conferem. Ambiente explícito:Chromium headless,ANGLEMetalAppleM2Pro,1440×900/DPR2,movimento reduzido,cache de shadersOS não resetado. São medições locais, não benchmark comparativo ou aceite humano.

## Histórico e limites preservados

1. FULL1 permanece100PASS/2PRODUCT_FAIL brutos. As adaptações estritas NoCuda/MiniGames foram revisadas e têmRED/GREEN; classificação causal TEST_HARNESS_FAIL não apaga nem colore deverde o recibo original.
2. FULL2 permanece tentativa interrompida:25checks completos,24PASS/1ENVIRONMENT_ERROR, restanteNOT_RUN/interrompido, semJSONoficialfinal. O timeout de900s do UI e sua causa indeterminada continuam registrados. FULL3passou na condição declarada semuso doMac, com os mesmoscritérios/limite; isso não demonstra retrospectivamente a causa do atraso.
3. Globe-fidelity continuaENVIRONMENT_ERROR/exit1 pela ausência dasferramentas originais fixadas. Bundle globoSHA65d25e3fc43e00548e5a9db740a28c2f083031d5017b575b6118eff841c0f2cd permaneceintacto. FULL102PASS não é afirmação de que todos osfocais adicionais passaram:há20PASS e essa lacuna deambiente explícita.
4. Aceite visual humano, compreensão, Safari, leitor detela e toque físico permanecempendentes; execução automática e medições não os substituem. Não houve autorizaçãoGit/publicação decorrente desta verificação.

## Conclusão da revisão

Os recibos finais sustentam a implementação local e o gate atual aprovado nos bytes conferidos. Nenhum novo defeito material do delta ou enfraquecimento dos verificadores foi identificado. README/ACTIVE-TASK mantêm o resultado atual separado das tentativas anteriores e explicam a lacuna de fidelidade e o aceite humano pendente. A revisão não fecha essa lacuna por repetição bem-sucedida e não promove o candidate a integração/publicação.

ConferênciaUTC:2026-10-24T17:39:13.000815+00:00
SHA256 final-gate-inputs.json:5dafcc41838e4fd71b5a32cae45b059eb0ce75e2694d9e28c59163c70e1b8209
