# Revisão independente A0 — medição visual agrupada

Conclusão técnica do recorte: **PASS**. Não identifiquei achado Critical ou Important material no delta autorizado. Esta conclusão cobre fonte, equivalência delimitada e recibos focais existentes; não aprova all413, FULL102, zoom nativo, publicação ou aceite humano.

## Identidade e autoridade

- Raiz real: `/Users/joaoalvescirqueira/Library/Mobile Documents/com~apple~CloudDocs/SOFTWARES & EAS/JP Wealth OS`.
- Branch conferida: `codex/dante-guia-20261024`; HEAD `a4bf278cd4dc38bbaa5b905ed17a79e33684fb67`.
- Contrato: `docs/work/CHG-JPW-VISUAL-MEASUREMENT-CONTROLS-20261025.md`; autorização humana indicada `call_2fef00bbd89f4bdf8537108cae962427`.
- Pacote revisado: `task-1-review-package/`; 24 entradas do manifesto tiveram SHA256 recalculado, sem divergências. As duas fontes vivas coincidem byte a byte com o pacote.
- Juiz: `f5cee3d6442bbb95901afed953ca9ea504c6c30873fd6e0751a274c8b3c5c69c`.
- Helper: `41f9d9be12248e7741cff20b8edc4d6beb8b0cd8674bc39fc175f43630d1b64e`.
- Patch: `6d6f92344c96c0b6c6e88fab1197cc8b217dac5683ddc57b272b4cd89d562767`.

Li brief, relatório, patch integral, fontes antes/depois, helper, manifesto e recibos relevantes. Li AGENTS, CHG, proposta exata aprovada, roteamento, JP Engenharia e referências de regressões/validação, preflight/change-control/post-change-audit, critical-review/test-triage; consultei os localizadores de contexto e regressões pertinentes. O recorte é o juiz em tools, sem revisão normativa financeira ou auditoria integral do produto.

## Preservação do contrato

A comparação AST independente encontra mudanças somente em `centered`, `controls_geometry` e na adição ao `counterproofs`. O único global alterado é SOURCE_FILES, que acrescenta o helper. As assertivas de centered/controls_geometry são idênticas por AST; CONTENT_GEOMETRY permanece igual. As demais funções, inclusive required_ids, validate_coverage, matrix, native_zoom, gate_counterproof e main, permanecem iguais.

Na comparação atual dos 679 hashes de baseline, mudaram apenas ACTIVE-TASK e o juiz autorizado. O gate e os inputs de produto desse conjunto permanecem iguais. O helper e o CHG são adições permitidas. Isso sustenta preservação de 413 IDs, 102 checks, tolerância2px, cap900 e ações; não equivale a executar esses casos.

O fluxo continua: localizar botões visíveis → nth na ordem original → scroll instantâneo → duplo requestAnimationFrame real → inspeção atual do botão → centered com contagem exata → tamanho mínimo e cortes → ordem/teclado/selects/inputs originais. Não há armazenamento persistente ou cache compartilhado entre controles/casos.

## Equivalência e geometria

1. CONTENT_GEOMETRY continua medindo texto por Range e SVG pelo getBBox transformado via getScreenCTM/DOMPoint, incluindo transforms do desenho. A escolha ink/text agora usa a contagem SVG já lida nesse mesmo DOM.
2. O retângulo externo reutilizado vem de getBoundingClientRect. O uso substituído de bounding_box era somente width/height. A equivalência afirmada é suficiente para botões estáveis do documento principal; não expande a homologação para iframes, shadow DOM ou animações concorrentes.
3. O algoritmo de cortes preserva os mesmos ancestrais, overflowX/Y, margens0,25px e limite em body. A leitura agrupada reduz a janela temporal entre campos sem alterar a decisão definida.
4. Não houve troca de oráculo por caixa externa apenas: centered continua julgando o conteúdo interno e seus limites. Contagem exata do locator continua sendo uma chamada real, inclusive quando recebe snapshot.

## Evidências comportamentais existentes

Não executei browser nem repeti testes. Conferi os bytes e os resultados dos recibos do implementador:

- RED: `budget-red-confirmed.json`, exit1 em `budget-red-command.json`; hash do juiz é a baseline. Falha comportamental pelo budget <=4, com três botões medidos em8 chamadas. Classificação bruta TEST_HARNESS_FAIL preservada; trata-se do RED esperado, não erro de coleta/import.
- GREEN final: `permanent-app-green.json`, exit0 e4,449s no recibo de comando com timeout900; hashes correspondem às fontes congeladas. Três botões sintéticos e12 do formulário real apresentam equivalência e8→4 chamadas, sem writers ou commands.
- Cinco violações passam por controls_geometry real: texto+5px, desenho SVG+5px, Fechar20px, corte ancestral e ausência de conteúdo. Os recibos registram o motivo correto tanto na referência quanto no batched.
- Zero/múltiplos locators são recusados em centered com e sem snapshot. Ausência de escopo e de botões é recusada por controls_geometry.
- Mudança do DOM entre chamadas mede deslocamento fresco de5,0px e é recusada. Isso demonstra nova leitura e evita confundir reaproveitamento de snapshot válido com prova positiva.
- Wiring: `wiring-counterproofs-confirmed.json` contém quatro IDs originais PASS; o ID `counterproof-forecast-inner-text` inclui `batched_measurement_counterproofs`. A chamada ao helper ocorre dentro da ação passada a record; falha do helper não desaparece do resultado do caso. O finally restaura a função instrumentada e fecha o contexto sintético.
- A falha inicial do leitor scratch de wiring (chave observed/evidence) foi preservada no pacote, corretamente diferenciada do comportamento do juiz. Não a trato como falha do produto nem como prova de wiring antes do recibo corrigido.

A referência de oito chamadas reutiliza centered atual, mas a comparação AST mostra que seu caminho padrão e assertivas não foram alterados no candidate em auditoria. Assim, não há divergência escondida do oráculo original neste recorte.

## Fresh/stale: limite que precisa acompanhar a entrega

Os negativos stale/wrong usam snapshots reais de inspeções anteriores, substituídos no proxy, e uma instrumentação verifica identidade do locator e do objeto fresco consumido imediatamente uma única vez. Isso prova o protocolo privado do chamador atual e detectaria seu reaproveitamento errado sob a instrumentação.

`centered(..., measurement=dict)` não autentica a origem de um dicionário arbitrário fora desse protocolo. Portanto, não afirmar proteção pública ou de segurança contra qualquer caller externo. Esse limite está corretamente declarado no relatório e é compatível com a proposta autorizada, que introduziu somente um snapshot local imediato. Não constitui achado impeditivo do candidate delimitado.

## Qualidade, impacto e pendências

O delta é pequeno no juiz; o helper concentra contagem delegada, comparação e contraprovas sem dependência nova, escrita financeira ou medição positiva fabricada. A contagem de RPC exclui setup, ordem e campos de maneira expressa e consistente; não é medição de tempo nem promessa de all abaixo de900s.

Preflight independente somente leitura: `python3 tools/agent_preflight.py --mode audit`, exit0/PASS, branch/HEAD esperados,94 alterações e aviso de frescor material preexistente. Não houve edição do produto, teste/browser, sinais ou Git mutável por este revisor. Executei somente leituras, hashes/análise AST em memória e gravei este relatório e seu recibo em scratch.

AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. BASIS: a representação de medição consumida pelo gate e sua lista de hashes recebem alteração autorizada; critérios e universo de casos permanecem iguais. A reconciliação documental/IMPACT global pertence ao coordenador e não é encerrada por esta revisão focal.

**All413, FULL102 e zoom nativo: NOT_RUN por este revisor; dependem dos recibos finais próprios do coordenador. Aceite humano e qualquer Git/publicação permanecem separados.** Nenhuma correção adicional é recomendada para o delta auditado. Se as duas fontes congeladas mudarem, revisar novamente a evidência afetada.

## Adendo — preparação externa do FULL (somente configuração)

A pedido do coordenador, conferi `redirect_full.py` em scratch contra a versão anterior de SHA256 `5eadae0f21b03835df0ba63270f95869a49dd4fca59f08eb7f8bac28ad523754`. O SHA atual é `234161ab54997586bbd7f889a991fc375208260d122a39d73e8c301ba656c39c`. Comparação AST independente: somente a constante OUT mudou do scratch anterior para o atual; todas as funções são idênticas. A fonte chama a entrada oficial `tools/quality_gate.py --tier full --artifact ...`; não altera catálogo nem timeout. A relocação se limita ao diretório recém-criado vazio, com checagens de identidade/posse, pausa do grupo próprio no primeiro preflight e retomada. Não executei wrapper, sinais ou selftest.

Li `redirection-selftest.json`: sete casos PASS registrados (valid, nonempty, existing, symlink, wrong-name, multiple, none). O congelamento `frozen-inputs.json` contém681 entradas: os679 caminhos anteriores mais CHG e helper, sem exclusões; todos os hashes coincidem com o disco nesta conferência. O gate continua com hash `074fd1d63154b50a1eefcbc3feac4c9f41e1d6356615bc089e04b5adffb2cd2a`.

**PASS da comparação de configuração e leitura dos recibos de selftest.** Isso não atesta execução futura do FULL, nem resolve a variância temporal anterior. Matrizall está sob responsabilidade do coordenador; não li seu log parcial como conclusão final. Nenhuma ampliação de escopo ou nova permissão decorre deste adendo.
