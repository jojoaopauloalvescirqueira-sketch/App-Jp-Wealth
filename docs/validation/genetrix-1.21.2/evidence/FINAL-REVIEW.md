# Parecer independente final — GENETRIX 1.21.2 no site

**Resultado: PASS no escopo de aptidão para integrar os fontes e a página local.** Não é aceite operacional do MT5, homologação do harness/modelo, publicação externa ou comprovação de Git executado. Autoria deste parecer distinta dos autores de integração; contexto de tarefa compartilhado, sem alegação de revisão cega.

## Candidato examinado

Base Git `7f0828488b2fc0ea62dc7c421174799cda47a34a`; freeze final R5 `ad70b6bd11d614265c82eed4f53d85ecc97fd478ae7d27354c6624749358840c`. Conferidos diretamente os **847 inputs**, sem ausentes ou divergências. Fingerprint reconstruído por SHA256 do mapa `files` serializado com `json.dumps(sort_keys=True)` e separadores padrão. Os 465 inputs runtime do freeze R3 continuam idênticos, portanto os gates R3 não foram transferidos para código alterado.

## Evidência e julgamento

- **Fonte/distribuição:** ZIP canônico SHA256 `a9a77be170036747fec8322fdba7d80bd6256fbcae87e4c6dadb1348ff916261`, 760092 bytes, 132 membros. 111 inputs runtime e fingerprint `9650de7a8573566f3532e3a3ecb2806d0a0e62e2afe7b8130f1331045c06a4b6`; todos coincidem com a origem. Zero EX5 no pacote e árvore corrente. Produto1.21.2/MQL1.212/cálculo1.9.0.
- **Proveniência dos juízes:** 24 registros preservados, 21 before existentes e três bridges ausentes na base. Todos os before correspondem à main e todos os after aos bytes congelados aprovados para transferência. Nenhum resultado esperado foi modificado durante a integração.
- **Construção:** builder oficial não foi alterado. Em três diretórios sintéticos próprios reproduziu o ZIP exato, manteve idempotência e recusou EX5 sem recibo. Esses três ensaios aconteceram em um processo Python; não são três sessões nativas.
- **Consumidores:** executei três processos novos independentes. Manifesto e ZIP obtidos por HTTP local coincidem integralmente; build-id e portátil carregam o mesmo manifesto e bytes incorporados, somente source. Compilado indisponível e nativeArtifact null. São localhost e arquivos, sem prova de publicação externa.
- **Gates consultados:** recibo web full R3 apresenta **57/57 PASS**, sem demais estados; host R3 apresenta **40/40 PASS**, inputs_unchanged=true. Esses gates foram executados pelo coordenador; este revisor conferiu os recibos, logs pertinentes e hashes atuais. Os quatro percursos da autoria UI terminaram exit0/PASS, incluindo a demora de teardown preservada como observação, não falha ocultada.
- **Documentos:** seis documentos focais coerentes com versão, distribuição, papéis e limitações; 59 links locais existentes. Conteúdo anterior permanece histórico. Current/Estimated, PENDING, NOT_HOMOLOGATED, BLOCKED, harness CANDIDATE, piloto FAIL e HIS-AC20 PRODUCT_FAIL não são removidos ou convertidos em PASS. O manifesto `siteIntegration=NOT_RUN` é explicitamente checkpoint de origem, com os resultados atuais apresentados em evidência própria.

Não encontrei bloqueador no escopo examinado de integração local. O site oferece fonte coerente1.21.2 e mantém o botão compilado indisponível, com a prova histórica1.20 distinguida da revisão corrente.

## Limites e camada posterior

Compilação MetaEditor e execução MT5 1.21.2 permanecem **NOT_RUN**; aceite operacional **BLOCKED_NATIVE_VALIDATION**. Não foram instalados componentes, alteradas contas, armada negociação ou verificada eficácia financeira. Commit/push/merge e hosting continuam sem resultado comprovado no instante deste parecer; seus recibos posteriores devem ser verificados separadamente.

Adotar este parecer, seus links e os recibos Git verdadeiros é **N0-D** se somente acrescentar evidência informativa, sem mudar obrigações, instruções, juiz, fonte ou runtime. Preservar R5 e congelar essa camada documental nova. Este parecer não autoriza alteração de código/teste; se houver alteração material, invalidar a evidência afetada e reexecutar os controles pertinentes. Checkpoints anteriores podem permanecer identificados como históricos, com o resultado atual ligado ao seu recibo.

Arquivos de prova desta revisão: `FINAL-REVIEW.json`, `R5-final-verification.json`, `consumer-trial-1.json` a `consumer-trial-3.json`, `independent-builder-results.json`, `canonical-review.json`, `judge-main-vs-freeze-provenance.json`, `judge-provenance-review.json` e delta contra main.
