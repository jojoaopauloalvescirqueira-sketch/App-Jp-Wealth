# Calendário e Mercados — validação24/10/2026

Plano humano aprovado; branch codex/calendario-mercados-20261024, base limpa a4bf278. [Plano e invariantes](../../superpowers/plans/2026-10-24-calendar-markets.md), [brief](../../work/BRIEF-CALENDAR-MARKETS-20261024.md), CHGs PRODUCT/TESTS dedicados. Sem Git/publicação.

## Estado da execução

Implementação local concluída no build `3a9f6157481ae050`. A [execução final da suíte completa](full-final.json) passou em **102/102 verificações**, sem outras classificações; processo exit0. A [integridade dos 481 arquivos de entrada](full-input-integrity.json) foi conferida ao terminar, sem mudança de bytes. O resultado histórico da base permanece separado deste recibo atual. A recompilação de fidelidade do globo conserva a limitação de ambiente descrita abaixo; aceite humano permanece pendente.

RED antes das mudanças de produto:4casos reaisHTTP (nomeúnico/compatibilidade/resumo/API), PRODUCT_FAIL esperado, sem erros de ambiente. Artefato temporário: /private/tmp/jpw-calendar-markets-20261024/tests-red/report.json. Cópias duráveis e resultados finais serão acrescentados após estabilização dos bytes.

Referência de trabalho em repouso, com fontes a4bf278 servidas por interceptação isolada:3amostras de5100ms,5consultas e5renderizações completas por amostra. Prova não usa dados reais nem mede ganho de compreensão. As duas tentativas de instrumentação anteriores foram descartadas (Proxy inválido de objeto congelado; espera por botãoB3 oculto), sem seus números integrarem a comparação.

Revisão independente e aceite humano são etapas distintas. Teste humano de localizar evento, bolsa aberta e próxima sessão permanece pendente até execução por pessoa. Histórico/incidentes anteriores não são encerrados por este documento.

## Provas focais atuais

- [21casos reais e fixtures controladas](final21.json):PASS, inputs estáveis. [Contrato e limites do verificador](test-contract.md). Novo focal é comando explícito adicional; não foi inserido no runner/CI.
- Seis contraprovas rejeitadas pela mesma entrada: eagerfull, cadência1s recolhida, limite24hexclusivo, itemmenu duplicado, texto desalinhado dentro de44px e CSSzoom no lugar de zoom nativo.
- Zoom Chromium200% real por perfil temporário:outer1440/inner720,CSSzoom1,DPR2,4layouts×2temas×resumo/exploração. [Recibo](native200.json); compreensão/leitor de tela/toque físico/Safari não são comprovados por essa execução.
- [Revisão independente do produto](review.md), [adendo do juiz](review-judge.md) e rechecks dos5achados:[foco/erro/âncora/linhas](review-p2-green.json), [alvo44px](review-ui-green.json).
- [Focais adicionais](focals-summary.json):20execuções finaisPASS,1ENVIRONMENT_ERROR na recompilação de fidelidade original do globo. Three0.186.1/esbuild0.25.12 do ambiente antigo não estão disponíveis; busca local sem cache recuperável. Não houve instalação/rede. O bundle do globo conservaSHA65d25e3fc43e00548e5a9db740a28c2f083031d5017b575b6118eff841c0f2cd.
- Primeira tentativa engine com caminho absoluto/tmp:rawENVIRONMENT_ERROR por ValueErrorrelative_to, classificado causalmente TEST_HARNESS_FAIL. Comando corrigido para destino relativo ignorado:PASS. Ambas tentativas preservadas nos recibos; não representam correção de produto.

## Comparação de trabalho em repouso

[Antes](before-rest.json) usa fontes a4bf278 servidas isoladamente. [Depois](after-rest.json) consulta o resumo do candidato. Três amostras de aproximadamente5100ms: consultas5/5/5→0/0/1; renderizações completas5/5/5→0/0/0. Mediana/p95 por amostra (nearest-rank):consultas5/5→0/1;fullrenders5/5→0/0. A consulta adicional coincide com a atualização prevista do relógio; não se afirmou ganho percentual global. Os tempos frios de entrada são observações únicas, não benchmark estatístico comparável.

## Capturas e avaliação humana

Referência visual sintética23/10/2026 15hUTC; nenhum perfil/dado do operador foi usado. [Resumo desktop](summary-1440-light.png), [celular](summary-390-light.png), [tema escuro](summary-1440-dark.png), [exploração](exploration-desktop.png), [antes](before-desktop.png). Capturas foram inspecionadas; não equivalem a compreensão humana.

Tarefas humanas pendentes:encontrar evento de amanhã; identificar bolsa aberta e próxima sessão; selecionar data passada e distinguir Agora; chegar ao mapa pelo atalho; recolher/retomar conservando consulta. Não há alegação de usabilidade comprovada.

## Escopo auditado

[Fingerprint do produto](product-fingerprint.json) e [auditoria](scope-audit.json). Motores financeiros, dados de sessões, biblioteca do globo, serviceworker, AGENTS e runner estão intactos. Artefatos derivados vieram do gerador oficial. Contratos, guia e tarefa ativa refletem o candidato local; fontes oficiais/históricas não foram reescritas como aprovação atual.

AGENTIC IMPACT CHECK:AGENTIC IMPACT DETECTED. BASIS:a consolidação da rota alterou representações consumidas por agentes; reconciliados contratos, guia, tarefa ativa e registro factual das5regressões, dentro do delta aprovado. Normas, skills, routing, autorizações, gates e configuração de memória não foram alterados. INDEX NOT REQUIRED.

## Primeiro gate completo e ajuste delimitado dos testes

A [primeira execução integral](full-first.json) terminou com 100 PASS e dois PRODUCT_FAIL brutos, em NoCuda e MiniGames. Os dois testes ainda exigiam a antiga entrada independente de Bolsas Globais. Essa entrada foi deliberadamente substituída pelo plano humano aprovado; os resultados originais permanecem preservados, e a causa foi classificada como TEST_HARNESS_FAIL, sem reescrever o recibo do runner.

O ajuste substituiu somente a lista de seis destinos pela lista exata de cinco. No NoCuda, a sequência de teclado passou a conferir NoCuda → Calendário → NoCuda → Calendário. [NoCuda: RED/GREEN, 130 checks](nocuda-oracle.json) e [revisão independente](review-nocuda-oracle.md). [MiniGames: RED/GREEN completo](minigames-oracle.json) e [revisão independente](review-minigames-oracle.md). Downloads, preservação dos dados, jogos, guia e distribuições foram mantidos. Naquele ponto iniciou-se a segunda tentativa, cuja interrupção e classificação estão registradas abaixo; o recibo final está na seção Gate completo final.

## Limite de tempo da segunda tentativa

O FULL2 atingiu o teto global inalterado de 900 segundos em ui-visual-quality, classificado ENVIRONMENT_ERROR. O usuário confirmou que usava o Mac durante a execução; interferência é possível, mas não foi demonstrada como causa. A [triagem independente](review-ui-timeout.md) identificou lentidão acumulada antes das últimas janelas nativas e confirmou as fontes idênticas. Capturas indicam progresso, não PASS de casos.

O usuário disponibilizou uma janela de aproximadamente 45 minutos sem uso. Para evitar concorrência e aproveitar essa janela, somente os processos desta tentativa foram interrompidos com SIGINT; exit130. [Registro parcial explícito](full-second-interrupted.json) e [log integral](full-second-interrupted.log): 24 checks PASS, um ENVIRONMENT_ERROR e restante interrompido/NOT_RUN. Não existe recibo oficial final nem PASS do FULL2. A tentativa FULL3 usou o mesmo comando, critérios e limite, em execução isolada; seu resultado final consta na seção seguinte.

## Gate completo final

FULL3 executado na janela declarada sem uso do Mac, com o mesmo comando, critérios e limite de tempo: **102 PASS; zero PRODUCT_FAIL, TEST_HARNESS_FAIL, ENVIRONMENT_ERROR, BASELINE_FAIL ou NOT_RUN**. [JSON integral](full-final.json), [log](full-final.log), [integridade dos inputs](full-input-integrity.json). A matriz visual dentro do gate passou em [370 casos](full-third-ui-visual.json), com fontes inalteradas.

A repetição passou sob a condição declarada sem uso; isso não demonstra a causa do atraso no FULL2. As primeiras tentativas permanecem preservadas. O resultado não concede autorização Git ou publicação, nem substitui aceite visual humano.

## Medição final do globo

[Execução isolada](performance-final.json), Chromium headless, WebGL ANGLE Metal Apple M2 Pro, 1440×900/DPR2 e movimento reduzido: PASS. Trinta seleções: mediana 6,4 ms e p95 7,2 ms até o primeiro desenho. Intervalos de desenho durante arraste: 137 amostras, mediana 8,3 ms e p95 9,0 ms. Em janelas de cinco segundos houve zero desenhos em repouso, fora da área e com mapa móvel recolhido. Renderer e Canvas conservaram identidade ao reabrir. Tempos de entrada fria/quente são observações únicas (252,3/90,2 ms), não uma comparação estatística antes/depois.

## Conferência final e aceite

Após a suíte e a medição, os [21 casos focais](final21.json) foram executados novamente: **21/21 PASS**, zero falhas/erros e inputs idênticos antes/depois. O recibo anterior permanece em [arquivo próprio](final21-before-oracle-doc-update.json); a nova execução inclui o hash final do plano com as adaptações delimitadas dos testes legados. Nenhum produto ou verificador foi alterado após o gate.

Preflight final PASS na branch autorizada; o aviso de frescor de 1.279 caminhos desde a revisão histórica ea15afc foi tratado no impacto agêntico, sem promoção do contexto antigo a estado atual. Integração estrutural JP Engenharia PASS: 20 arquivos, dois aliases, 96 registros de regressão e 13 controles; isso não substitui os testes comportamentais. Diff sem erros de whitespace.

Prévia: http://127.0.0.1:58998/index.html?v=3a9f6157481ae050, em Ferramentas e Serviços → Calendário e Mercados. Primeiro acesso recolhido; Explorar bolsas e mapa abre a exploração. Sem commit, merge, push ou publicação. Aceite humano permanece pendente; teste automático não demonstra compreensão ou preferência visual. A limitação da recompilação de fidelidade continua explicitamente aberta.

[Verificação independente dos recibos finais](review-final-receipts.md) e [auditoria pós-alteração](POST-CHANGE-AUDIT.md): sem novo achado material, limites e próximo gate humano preservados.
