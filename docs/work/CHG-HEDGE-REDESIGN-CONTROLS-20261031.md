# Controles Hedge — delta dedicado de 31/10/2026

N3/control plane, autorização humana do plano com gates preservados, retransmitida pela coordenação. Base `69b6cb6`, branch `codex/hedge-didatico-20261031`. Este registro descreve a autorização recebida; não a concede.

## Antes e depois

Antes: `hedge_prop_engine_test.js` verifica 15 contratos e quatro mutantes financeiros; `hedge_prop_browser_test.py` verifica a ferramenta temporária e distribuições em entrada própria. Depois: preservar todos os casos e asserções anteriores; encadear o store e as novas jornadas após os casos legados. Saída nãozero de cada subprocesso continua nãozero no check FULL existente. Sem alterar o runner, número de checks, oráculos financeiros, tolerâncias ou prazos.

Novas entradas permanentes: `hedge_guide_store_test.js` (validação pura, revisão, marcos, raw futuro, conflito, quota, escrita incerta e substituição confirmada) e `hedge_redesign_browser_test.py` (gestos reais, sliders, foco, precisão, 1/2/Instant, catálogo factual, save/reload/etapas e responsividade). Perfis isolados e dados sintéticos. Não usar estado financeiro real, credenciais ou o perfil do proprietário.

RED store: API ausente rejeitada por assertion antes de implementar. RED browser: modo Instant ausente rejeitado após bootstrap real; a tentativa anterior de bind bloqueado pelo sandbox permanece ENVIRONMENT_ERROR. Casos de substituição tiveram RED/GREEN próprios. Não confundir testes passados com aceite visual do proprietário.

Evidências, hashes e resultados focais no relatório factual da sessão `work/implementation/hedge-report.md`. FULL combinado, revisão independente, Safari/zoom nativo e aceite humano dependem de recibos próprios; não são declarados por este CHG.

## Ajustes causais de controle observados

A primeira execução legada recusou a nova fonte oficial do catálogo; a allowlist foi acrescida somente de `https://ftmo.com/en/comparison-table/`, mantendo igualdade do conjunto e ausência de requisições automáticas. Sliders têm trilho separado do campo numérico, com alvo44px: medição por tipo preserva a regra de alinhamento de cada linha, sem comparar trilhos diferentes como se fossem um só.

A matriz de80contextos passou, mas a contraprova de deslocamento24px do campo deixou de ser rejeitada porque uma única coluna não oferece par horizontal. O estímulo original é preservado, e o oráculo foi fortalecido: controlar posição relativa ao texto/range do mesmo campo e manter tolerância2px. Não é um relaxamento de critério; o mesmo deslocamento e o de custos precisam continuar rejeitados.

O teste legado do motor escreveu seu recibo histórico na primeira execução. Os bytes de origem foram restaurados literalmente via leitura Git, e o recibo novo foi redirecionado a `tools/.artifacts/hedge-prop-engine/engine-counterproofs.json`. Os15contratos e quatro mutantes financeiros foram preservados; a tentativa atual permanece no relatório externo. Não normalizar provas históricas.

## Correções da revisão independente — mesma rodada

O revisor encontrou que a checagem somente do modo permitia substituir parâmetros/catálogo sem replacePlan. Novo caso independente altera taxa e catálogo no mesmo modo preservando o restante: RED observado e a escrita agora recusa a alteração integral do plano; somente a substituição confirmada pode modificar o snapshot.

ExpectedRaw/releitura, isoladamente, não serializavam duas abas. A API write virou Promise, usando exclusivamente o Web Lock compartilhado da base/importação, sem ramo degradado. O teste browser mantém esse lock em uma terceira aba, enfileira duas confirmações da mesma revisão e verifica nenhuma escrita antes de liberar; depois uma confirma, outra recusa por conflito, preservando todos os marcos confirmados. O produto anterior falhou ao gravar mesmo com o lock retido (RED). Novos casos cobrem owner descartado antes da liberação (cancelamento sem escrita) e capacidade Web Locks ausente (recusa explícita com parâmetros/registro anteriores preservados).

O teste de distribuição agora exercita guardar plano, confirmar etapa e recarregar também em file modular, portátil e PWA offline; as quatro origens suportaram gravação segura no Chromium de teste. Capacidade sem lock seguro é coberta em cenário separado com recusa. Mantidos todos os cenários de apresentação e oráculos anteriores, sem alterar runner, critérios de2px/44px, limites ou saída de falha. API de validação pura/schema1 do backup permanece idêntica.
