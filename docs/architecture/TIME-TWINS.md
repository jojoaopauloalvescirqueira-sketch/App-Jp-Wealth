# Gêmeos do Tempo

Candidate local de 15/10/2026. Ferramentas e Serviços → MiniGames apresenta dois cartões: Galton Board e Gêmeos do Tempo. Cada Abrir seleciona uma visão local do mesmo child `tools-minigames`. Não há novo submenu. `time-twins` é um alias direto para `tools/time-twins`; os aliases antigos continuam abrindo exclusivamente Galton Board.

Gêmeo A e Gêmeo B são personagens fictícios. A jornada pede prever, preparar uma variável, avançar, investigar, explicar e repetir. O laboratório livre permite alterar os dois cenários. Nada acessa contas, `S`, `DEFAULTS` ou APIs de cálculo financeiro do terminal. Os resultados não são recomendações nem dados reais do usuário.

## Modelo e unidades

Valores em reais nominais, tempo em meses e taxa efetiva anual. A taxa mensal é `(1 + taxaAnual)^(1/12) - 1`. O capital inicial entra no mês zero; juros de cada mês precedem seus aportes de fim de mês. Um aporte de valor `A`, feito no mês `m`, vale `A × (1+r)^(T-m)` no mês `T`. Sem arredondamento interno; somente a apresentação usa centavos. A soma das trajetórias individuais coincide com o saldo. Sem custos, impostos, inflação ou aleatoriedade.

O laboratório começa com R$ 1.000, R$ 100 mensais, 6% efetivos ao ano e 240 meses. Limites: 1–360 meses, inicial 0–1.000.000, mensal 0–100.000, taxa anual 0–20%. Entradas inválidas bloqueiam avanço e aplicação; a última projeção válida permanece. Sem aportes e sem base percentual são estados explícitos. Para o padrão, saldo final 48550.99872712496 e primeiro mês cujo rendimento supera seu aporte 134. O marco compara os fluxos do mesmo período; não significa independência financeira ou irrelevância dos aportes.

A apresentação separa saldo, principal já depositado, depósitos futuros e retornos; fluxos encerrados ficam em zero após o prazo de cada gêmeo. Gráficos vetoriais A/B compartilham escala e linha do tempo. O controle nativo de aporte individual agrupa por ano e permite teclado, mouse e toque. Inspeção mostra principal, retornos, valor atual, participação e multiplicação por período. Comparar sem este aporte cria um contrafactual, preservando o cenário original. Impacto de um extra e participação individual são medidas distintas.

## Missões

| ID estável | Experimento |
|---|---|
| early-start | R$ 1.000 no mês 0 versus 60, prazo 240; repetir com taxa zero |
| equal-budget | Doze aportes de R$ 100 nos meses 1–12 versus 49–60; mover calendário conservando R$ 1.200 e identidades |
| contribution-story | Selecionar aporte, inspecionar trajetória e comparar sem ele |
| three-levers | Alterar prazo, taxa e aporte mensal separadamente, restaurando a base entre variáveis |
| next-contribution | Extra de R$ 100 no mês 1 versus 120, contra base original intacta |
| crossover | Investigar primeiro rendimento mensal maior que aporte; mudar premissa e reinvestigar |

Respostas incorretas pedem nova tentativa. A ajuda permite `assisted`; concluir exige a evidência do experimento e explicação (`demonstrated`); pular guarda `skipped`. Revisitar e receber ajuda não rebaixa demonstração anterior. Nenhum desses estados prova compreensão humana.

## Módulos e API

Cinco scripts clássicos, nesta ordem, imediatamente antes de `00-core/10-download-assets.js`, que permanece imediatamente antes de `20-ui/31-tools-services.js`. Os 107 scripts herdados conservam a ordem relativa; os quatro do guia continuam no fim (112 no total).

| Módulo em `src/js/40-app/29-time-twins/` | API em `window.JPWTimeTwins` |
|---|---|
| 01-simulation.js | `simulation`: limits, periodic, project, inspect, trace, without, difference; funções puras, sem DOM/storage |
| 02-missions.js | `catalog`: ids, missions, get, create; presets novos e bases independentes |
| 03-progress.js | `progress`: key, read, write, restart; envelope estrito e releitura |
| 04-view.js | `view.panelHTML` e `view.exerciseHTML`; marcação local |
| 05-controller.js | mount(host), activate(host), deactivate(host), dispose(); controlador com activate, pause, deactivate, destroy e snapshot |

`mount` é idempotente para um host com controlador vivo. O host real é `#toolsTimeTwinsSlot`, dentro de `#minigamesTimeTwinsGame`. Montar não executa o tempo. A publicação de navegação aceita é a única oportunidade de criar instância; observadores de diálogo/visibilidade só pausam ou reativam instância viva. Sair/ocultar/abrir Settings, Notas ou Finalizar pausa. Retorno exige Continuar. Start e troca explícita de missão focam o título e revelam o primeiro controle; digitação, ticks e ativação não deslocam a tela.

Finalização incrementa a epoch auxiliar e chama `dispose()` em try/catch isolado: descarta RAM, listeners e callbacks, sem apagar progresso persistido. Fechar um diálogo depois desse descarte não remonta nada. Uma nova entrada explícita aceita cria cenário limpo, sem autoplay. O Galton mantém seu lifecycle próprio.

## Persistência e privacidade

A única chave do jogo é `jpwealth_time_twins_v1`, com exatamente `{schemaVersion:1,currentMissionId,missions:{id:status}}`. Somente IDs de missão conhecidos e estados `demonstrated`, `assisted`, `skipped`; nunca parâmetros, resultados, contas ou conteúdo financeiro. Não entra em `S` nem no Backup Completo. Storage indisponível permite progresso temporário avisado. Raw incompatível é conservado até Reiniciar explicitamente; expectedRaw e releitura detectam conflitos observáveis, sem promessa de CAS atômico entre abas.

A chave pertence à lista auxiliar existente. `removeAuxiliary:false` preserva-a; a limpeza explícita `removeAuxiliary:true` remove-a pelos controles existentes. O hook de descarte não altera essa distinção. Callbacks/controladores destruídos não voltam a escrever. Guia preserva 57 passos, sete trilhas, catálogo versão 1 e ID `general-settings-probability-lab`, cujo destino permanece o hub.

## Distribuição e verificação

Manifesto fixa ordem e SHA-256; SW precache inclui os cinco scripts locais. Gerador oficial `python3 tools/rebuild_monolith.py` produz monólito, portátil e identidade de build. O portátil é testado isolado, só seu HTML numa pasta temporária. Testes PWA aguardam SW ready, recarregam sob controle e exigem respostas offline reais de todos os cinco módulos. O jogo não solicita recursos externos; bootstrap econômico usa as fixtures oficiais.

Com runtimes já disponíveis, sem instalar dependências:

```sh
node tools/time_twins_unit_test.js
python tools/time_twins_browser_test.py --mode standalone
python tools/time_twins_browser_test.py --mode integrated --out-dir tools/.artifacts/time-twins-integrated
python tools/time_twins_browser_test.py --mode all --out-dir tools/.artifacts/time-twins-all
python tools/minigames_test.py
python tools/navigation_local_contract_test.py
python tools/learning_guide_test.py --case startup --out tools/.artifacts/time-twins-startup.json
python tools/validate_project.py
python tools/build_reproducibility_test.py
```

FULL acrescenta três checks aos 75 anteriores: time-twins-unit, time-twins-browser e minigames. Logs/recibos do candidato registram resultados efetivos; este documento descreve contratos, sem antecipar PASS global. Matriz integrada cobre quatro layouts × dois temas × duas larguras × zoom CSS 1/1,25, com geometria, foco/hover/contraste e chegada. Zoom CSS não equivale a zoom nativo. Headless/teclado e movimento reduzido não substituem toque físico, leitor de tela ou teste humano de aprendizagem. Full/host, revisão independente, aceite manual e publicação permanecem evidências separadas.
