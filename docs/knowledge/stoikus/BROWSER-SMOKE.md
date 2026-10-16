# Browser smoke independente — mapas Stoikus

**PASS funcional: 64/64 verificações, com um achado visual P3 não bloqueante.** Chromium 148.0.7778.96, quatro contextos novos, HTML local via `file://`, viewport 1440 × 1000. Nenhum perfil ou app pessoal foi acessado.

| Mapa | Nós | Arestas | Resultado funcional |
|---|---:|---:|---|
| Mestre | 301 | 1144 | 16/16 |
| Arquitetura | 125 | 228 | 16/16 |
| Fluxos | 104 | 172 | 16/16 |
| Testes e evidências | 225 | 983 | 16/16 |

Contagens conferidas entre HTML bruto, DataSet em execução, estatísticas visíveis e graph.json. Verificados canvas visível, busca existente/inexistente, seleção e detalhes com fonte, navegação para vizinhos, filtro individual e restauração, checkbox indeterminado, ocultar/mostrar todos e áreas do sidebar. Capturas dos quatro mapas inspecionadas visualmente.

O CDN `unpkg.com/vis-network@9.1.6/standalone/umd/vis-network.min.js` retornou HTTP 200 em todos os contextos. Nenhum erro de console, exceção de página ou request falho. Essa execução dependeu do CDN; operação offline não foi verificada.

## B1 — P3: caminho Source cortado no detalhe

Reprodução em Arquitetura: buscar `JPW_PersonalHistory_Controller.mqh` e selecionar o resultado. O texto Source ocupa 407 px em um campo de 251 px; a segunda linha chega a x=1581,98 em viewport de 1440 px. O sidebar usa `overflow:hidden`, e o campo não tem tooltip nem link. Assim, o sufixo do caminho fica ilegível visualmente. O caminho completo permanece no DOM e no graph.json.

O mesmo renderer está nos quatro HTMLs: regras em `graph.html:13` e `:22`, emissão de Source em `:140`. Correção sugerida: permitir quebra de caminhos longos no detalhe (`overflow-wrap:anywhere`) ou oferecer acesso ao valor completo por tooltip/cópia. Prova estreita: `BROWSER-SMOKE-overflow.json` e `BROWSER-SMOKE-overflow.png`. Nenhum HTML foi alterado.

## Evidência e limites

`BROWSER-SMOKE.json` contém os resultados; `BROWSER-SMOKE.py` é o roteiro executado; oito PNGs mostram os estados inicial/detalhe. `BROWSER-SMOKE-overflow.py` registra a contraprova visual estreita. A primeira tentativa foi bloqueada no início do Chromium pelo sandbox e está preservada em `BROWSER-SMOKE-attempt1-sandbox.json`; a repetição autorizada com navegador temporário concluiu.

Freeze `4585e410c73fd978950a0c22204c49f64b972f3a2beb2a3ebe80b0ecbf7b1beb`: **50/50 arquivos permanecem idênticos**, antes e depois. Somente evidências BROWSER-SMOKE foram criadas.

Este smoke não reaudita todas as âncoras de fonte nem comprova a semântica de cada aresta. Compilação/execução nativa MT5/Windows: **NOT_RUN**. Eficiência de IAs: **não mensurada**. A comparação de bytes da cópia pública cabe ao agente principal.
