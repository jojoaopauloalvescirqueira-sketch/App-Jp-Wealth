# Revisão independente das duas propostas de fixture — 2026-10-24

**Parecer favorável ao delta proposto; nenhuma redução de proteção encontrada.** Revisão somente leitura: patches ainda não aplicados, fontes originais preservadas, FULL2 congelado em execução. As falhas brutas de FULL2 continuam PRODUCT_FAIL; a conclusão causal abaixo identifica a camada a corrigir, sem promover FULL2 a PASS.

## Causalidade conferida

`tools/alladin_finalize_preservation_test.py`: setup de C8/C11/C14 semeia somente Alladin. Os asserts de linhas425,494,529 assumem contas anteriores e usam length0 como sentinela de finalização indevida. `original-empty.json` comprova0→0 nas três recusas. `explicit-fixture.json`, com mesmos cenários/oráculos e somente uma conta explícita, comprova1→1 e ausência de falhas. `mutated-clear-on-abort.json` comprova1→0 e rejeição pelos três asserts. Disco truncado/ausente, Alladin e guardas são registrados separadamente. O probe importa o original e seleciona explicitamente C8/C11/C14; seu resumo legado não significa execução C1–C17.

`tools/session_write_serialization_test.py`: abrir não prepara conta; SK/SH/SH2/SI usam contagem como sentinela. `fixture-only-receipt.json` registra12 boots inicialmente vazios e execução da entrada inteira com uma conta sintética, exit0. `counter-destructive-receipt.json` e log registram exit1 e detecção dos três cenários SI após substituição deliberada do handler remoto por apagamento. Li `run-disposable.py`: produto/testes não são editados, asserções mantidas, wrapper instala apenas fixture e opcionalmente violação em RAM. Isso demonstra que a pré-condição restaurada não torna o juiz permissivo à perda.

Essas contraprovas de perda são mutações em RAM nas páginas sintéticas, não mutações de arquivo servido. Sua força é confirmar o poder dos asserts de preservação contra o efeito destrutivo; não substituem prova completa de todas as falhas possíveis dos handlers.

## Menor delta e proteções

`triage-finalize/proposed.patch` afeta somente C8/C11/C14 e a declaração da conta compartilhada. Prepara uma conta explícita com identificação sintética, exige save confirmado, captura a coleção e confere a pré-condição. Mantém cada assert antigo, acrescentando igualdade integral antes/depois da recusa para detectar alteração de campos sem mudança de cardinalidade. Preserva disco/raw, ausência de broadcast, Alladin, save recusado, desbloqueio e demais casos.

`triage-serialization/proposed.patch` afeta somente abrir, instalando uma conta sintética em RAM antes dos saves já existentes e verificando sua existência. Não adiciona save/broadcast/observação no setup; não muda segunda_aba, scheduling, locks, sequência, callbacks, expectativa ou timeout. O agregado de testes depende dessa pré-condição; o teste separado de primeiro acesso continua sem fixture. Zero na fixture é explicitamente declarado e não reintroduz exemplos no DEFAULTS do produto.

Não há remoção de assert/falhas.append, exceção permissiva, skip, mudança no runner, política, produto ou distribuição. O delta é coerente com o CHG TESTS de fixtures explícitas. É correção do harness exigida pelo contrato de boot vazio aprovado, e não justificativa para repor contas demonstrativas no produto.

## Verificações próprias

- Leitura integral de ambos patches, relatórios, harnesses temporários, recibos e trechos relevantes dos dois testes originais.
- `git apply --check <triage-finalize/proposed.patch>`: PASS.
- `git apply --check <triage-serialization/proposed.patch>`: PASS.
- Originais ainda SHA `13e923d351b6e0e18cd7be5fb77c8c389d36ad04814157bb59da523d892ae2e6` e `a3595c0c4a60c38c07287f55bbfb6b87b0fbf54b0428c95f652268a7a481f32e`, respectivamente.
- Inspeção de linhas removidas: nenhum assert, condição de recusa ou registro de falha removido.
- Nenhum browser/probe adicional, escrita no projeto ou alteração do freeze pelo auditor.

## Limites e próximos gates

Os contrafactuais comprovam a causa; não são execução dos patches exatos. A proposta finalize também acrescenta moeda/identificadores e verificações completas que ainda devem rodar na forma final. Após FULL2 terminar, aplicar somente os deltas autorizados, executar os dois focais integrais e suas contraprovas pertinentes, congelar novo fingerprint e rodar nova FULL inteira. Preservar logs/resultados brutos anteriores. Não há dispensa de gate, aceite humano ou autorização Git neste parecer.

## Recheck dos patches exatos aplicados — FULL3 pendente

**Delta confirmado conforme proposta; nenhum enfraquecimento encontrado.** A fonte atual de Alladin Finalize tem SHA `ce43caef6e53414884a5f7b06de2b3fc5ac1807277a5a340b324cbafd432cf19` e Session Serialization `2f821fe09765e5ec0dd9f203fcd8ffa87785e2629fd725feb5337130f8df2ce5`, exatamente os hashes das propostas previamente revisadas e dos dois focais integrais de `session-fixtures-final/receipt.json`. Os logs reais terminam PASS e os comandos completos têm exit0. O auditor inspecionou essas execuções; não as executou.

`triage-finalize/exact-patch-counter-verified.json` e log bruto confirmam rejeição por seis asserts: contagem antiga e nova igualdade integral em cada C8/C11/C14. Sem erro de pré-condição/ambiente. Li o probe: importa o teste corrigido, seleciona explicitamente os três casos e injeta apagamento após a recusa. Sua antiga conta auxiliar do wrapper é sobrescrita pelo setup exato de cada caso antes de save/ação; o novo cheque de pré-condição passa. A prova não pretende executar os demais casos C1–C17 na variante mutante.

`triage-serialization/exact-patch-counter.json` e log bruto confirmam a conta SERIALIZATION-SYNTHETIC instalada pelo próprio teste corrigido nos12 contextos, sem fixture adicional do wrapper. O handler remoto destrutivo em RAM é rejeitado nos três cenários SI; exit1. Esses resultados demonstram poder contra perda deliberada, não ausência universal de defeitos de sessão.

Conferência independente dos snapshots: `full-final-inputs.json`(FULL2) e `full-confirmed-inputs.json`(FULL3) contêm664 entradas cada; exatamente os dois testes diferem. Build/produto permanecem `1b695b809fe80c26`. Conferi cada hash do freeze FULL3 contra o arquivo atual: **664/664 iguais**, nenhuma divergência. A revisão não modificou projeto nem iniciou browser/probe durante a execução do gate.

Fingerprint próprio passou a19 arquivos, anterior preservado. Evidência de recheck em `independent-review-session-fixtures-recheck.json`. Parecer favorável à correção do harness aplicado. FULL2 mantém seu resultado bruto histórico; **FULL3 ainda pendente** e não recebe PASS por focais/contraprovas. Aceite humano continua NOT_RUN.
