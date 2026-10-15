# Eficiência do JP Wealth — 2026-10-14

Implementação sobre `0037bd3c8a7ab2b4e21f7fdcb60f66ed93230874`, na branch `codex/app-efficiency-20261014`. Build avaliado: `4b6cf8e71b699b13`.

As quatro frentes reduziram o trabalho redundante de apresentação e distribuição. A redução de latência está demonstrada principalmente na edição da grade; a abertura e o PWA ficaram na mesma escala. A navegação voltou à escala da referência depois da correção de uma regressão encontrada durante a medição.

## Comportamento entregue

- Renderização por host efetivamente exposto, incluindo Configurações, contexto expandido e abas internas do Consolidado. O catálogo normativo permanece montado por identidade de política. No retorno de navegação, Operação pode conservar sua última pintura completa se contexto, dependências e nós continuam válidos. O certificado é privado, distinto do snapshot de linhas, emitido somente após todos os pintores terminarem. Renderizações explícitas e alterações continuam frescas.
- Prévias por linha com snapshot privado e mapas de ordens/instrumentos. Somente mudanças geométricas efetivas chamam `previewOrder`; risco e totais permanecem confirmados. A digitação dimensiona a linha alterada e repaints idênticos dispensam novas medições. Salvar conserva leituras e guardas frescas.
- Notificações com caches separados por fonte e invalidação agrupada numa microtask. Escritores notificam somente depois de confirmação; exceções de observadores ficam isoladas. Entrada comum atualiza sinais locais, e falhas críticas continuam visíveis com a central fechada.
- Bootstrap leve e downloads verificados sob demanda. HTTP/PWA consome originais; modular `file://` usa sidecars por família; o portátil conserva um único HTML com JSON inerte. O loader verifica build, tamanho e SHA-256, compartilha transporte, isola cancelamentos e permite retry após falha/timeout. `generateEditable` é assíncrono e seus consumidores aguardam o conteúdo real.

## Método

Referência fixa: baseline02 integral na `main` original. Candidato: execução03 posterior à correção de navegação. Ambos usam o mesmo harness SHA-256 `3d0fac0e14d800833e9c8702ff5b04e1940551013a482a642ed5bbee896cf1c3`, Chromium `148.0.7778.96`, viewport 1440×1000, dados sintéticos proporcionais de 6/60/600 ordens e 11 amostras por série. As fontes permaneceram intactas durante cada execução. Nenhuma amostra da referência foi selecionada ou descartada para favorecer o resultado.

São execuções separadas no tempo, sem randomização ou intervalo de confiança. Carga e temperatura limitam a atribuição causal de diferenças pequenas. Com 11 amostras, o p95 empírico pelo posto mais próximo é a maior amostra. Wrappers e observadores acrescentam custo nos dois lados. Os contadores complementam os tempos.

## Edição da grade

Tempos de despacho até dois `requestAnimationFrame`, em **mediana / p95, ms**, n=11:

| Ordens | Campo | Referência | Final |
|---:|---|---:|---:|
| 6 | Motivo | 35,80 / 41,30 | 10,00 / 15,30 |
| 6 | Entrada | 39,20 / 45,40 | 12,90 / 26,70 |
| 60 | Motivo | 96,80 / 100,30 | 23,80 / 29,90 |
| 60 | Entrada | 96,20 / 127,70 | 30,60 / 64,70 |
| 600 | Motivo | 584,50 / 648,50 | 86,30 / 97,60 |
| 600 | Entrada | 588,80 / 902,60 | 103,30 / 426,90 |

No caso de 600 ordens, as medianas observadas diminuíram **85,2% no motivo** e **82,5% na entrada**. Isso se refere a este cenário e protocolo.

Chamadas medidas a `structuredClone`, por evento:

| Ordens | Motivo: referência → final | Entrada: referência → final |
|---:|---:|---:|
| 6 | 862–866 → 0 | 862 → 3 |
| 60 | 2.266–2.270 → 0 | 2.266 → 3 |
| 600 | 16.306–16.310 → 0 | 16.306 → 3 |

Nas 66 amostras finais de input, as interfaces instrumentadas registraram zero `executionBoard.read`, `state.read`, `accountContext`, `operationalSelection`, clones globais e gravações. Motivo fez zero prévias; entrada geométrica fez uma prévia e três clones locais. O focal da grade complementa os wrappers com a verificação das varreduras internas. O estado confirmado e o registro persistido permaneceram iguais. `JSON.stringify` caiu para duas chamadas por evento, sem alegação de eliminar toda serialização.

O intervalo complementar até estabilização impõe piso de 500 ms e janela de 300 ms sem mutações: ele não representa latência pura. Com 600 ordens, sua mediana foi 994,4 → 513,6 ms no motivo e 933,3 → 520,6 ms na entrada. Nenhum cenário final atingiu o limite de espera. As séries completas estão no recibo JSON.

## Navegação e abertura

**Mediana / p95, ms**, n=11:

| Caminho | Referência | Final |
|---|---:|---:|
| Histórico → Operação, 6 ordens | 29,93 / 36,39 | 30,19 / 43,12 |
| Histórico → Operação, 60 ordens | 87,37 / 97,06 | 83,11 / 90,92 |
| Histórico → Operação, 600 ordens | 651,64 / 746,53 | 648,13 / 745,49 |
| Abertura fria, SW bloqueado | 322,95 / 334,63 | 321,12 / 454,16 |
| Recarga no mesmo contexto, SW bloqueado | 300,42 / 317,54 | 305,85 / 349,62 |
| Abertura fria do cenário PWA | 318,56 / 350,95 | 322,98 / 347,59 |
| Recarga offline pelo SW/CacheStorage | 257,28 / 270,25 | 256,36 / 262,96 |

Não há ganho demonstrado em abertura/PWA; a cauda da abertura fria com SW bloqueado piorou nesta execução. Navegação mede uma chamada de automação com as duas rotas síncronas, sem quadro entre elas; não é uma medição isolada da pintura final de cada destino. A versão intermediária que quase dobrou esse custo foi preservada e corrigida por reutilização validada da pintura montada, sem adiar trabalho para fora do relógio.

O roteamento do fixture desabilita o cache HTTP comum. A recarga no mesmo contexto não mede cache HTTP quente. O teste PWA comprova reutilização offline efetiva: 11 contextos por lado, worker ativado e controlador, entradas de cache, documento/scripts recebidos do SW e SHA do build conferido. Preparação/inspeção do cache ficam fora do tempo de reabertura.

`build-id.js` passou de **1.948.914 para 31.441 bytes**, redução de **98,4%**. É redução de bytes de bootstrap, distinta de ganho de latência. Os sete originais dos envelopes permanecem idênticos; a instalação PWA conserva o precache dos originais. Sidecars exclusivos de `file://` ficam fora desse precache.

## Validação e evidências

A suíte `quality_gate.py --tier full` concluiu **75/75 comandos PASS**, sem falhas de produto, harness ou ambiente nesta rodada final. Inclui persistência, backup, finalização, conflitos entre abas, navegação, guia, notificações, grade, Consolidado, layouts/zoom, ferramentas, downloads, atualização do service worker e reprodutibilidade. Os comandos e tempos estão no recibo JSON; cada suíte conserva seus próprios casos e limites.

O focal final da grade/navegação passou em 80/80 verificações. A revisão independente conferiu o último freeze de 147 arquivos, as identidades da onda e as 20 séries temporais de cada lado. Controles financeiros, dados de distribuição, fontes MT5 e política foram preservados; a verificação de hashes cobre 120 arquivos protegidos.

Foram preservados a referência exploratória, as tentativas RED, a primeira medição interrompida por espera incorreta de ativação do SW, o candidato intermediário com regressão de navegação e o timeout de preparo de fixture. Este último não foi reproduzido no smoke posterior e não é apresentado como defeito do produto. O focal de navegação passou a criar somente a linha necessária por seu controle real; os 48 testes originais de edição conservam seis linhas e seus oráculos.

A rodada integral anterior terminou em 74 PASS e uma falha no comando do guia: duas asserções ainda exigiam o total antigo de 106 scripts. O loader autorizado elevou o manifesto a 107. A adaptação preserva a sequência anterior, os quatro módulos finais do guia e a presença única do loader antes do consumidor; essa alteração pertence ao teste, sem mudar o aplicativo. O relatório daquela rodada permanece intacto.

Recibos compactos versionados: [benchmark](../validation/app-efficiency-20261014/benchmark.json) e [suíte integral](../validation/app-efficiency-20261014/quality-gate.json). Os JSONs brutos, logs, screenshots, propostas e revisões permanecem no pacote recuperável de evidências, com hashes de origem. Os scripts de reprodução estão em `tools/app_efficiency_test.py`, `tools/forex_execution_efficiency_test.py`, `tools/notification_efficiency_test.py`, `tools/consolidated_efficiency_test.py`, `tools/download_assets_test.js`, `tools/download_assets_browser_test.py` e `tools/quality_gate.py`.

O aceite desta implementação exige redução do trabalho redundante e preservação funcional, demonstradas nos recortes acima. Os testes web não estabelecem compilação/execução nativa de MT5, instalação de PWA pelo sistema operacional, aceite humano ou publicação.
