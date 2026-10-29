# Observações de entrega após o FULL — 29/10/2026

Executados sequencialmente, após liberação explícita do responsável: captura comparável60175 e, somente depois da confirmação independente de escopo, observação de toque3f5d. Nenhum outro teste, browser concorrente, gerador ou escrita no repositório foi iniciado por este agente. Os scripts originais permaneceram inalterados.

Este documento relata dados observados. Não substitui o FULL, não aprova globalmente a UI nem atribui PASS de produto à coleta exploratória de toque.

## Comparação visual controlada

Diretório: `product-proposal/comparison-final-20261029`.
Inventário bruto SHA256: `e23a2a0d15f82bc57a504d7b795d04fa5143154582c9ac1abede24cce91c674e`.
Launcher log preservado em `product-proposal/comparison-final-20261029-launch.log`.

Foram produzidas seis imagens, formando três pares de viewport idêntica:1440×1100claro/workspace,390×1100escuro/modal e320×1100claro/workspace. Todas as observações têm seis eventos e o mesmo domínio SHA256 `f0f906e631a0fe6df7ffd69ba95b7a4a6f9fd392d438add0ef5ff58edb2a55e7`. O inventário classification=PASS é a classificação do roteiro de captura/precondições; não é aprovação global de produto.

Antes = renderer75/CSS3bc extraídos somente em RAM do tarbaseline verificado, sobre o shell atualaabc. Depois = renderer8cfa/CSS31e congelados sobre o mesmo shell. A fixture/relógio é a RED sintética comum. Não chamar a imagem Antes de release histórica completa.

Inspecionei visualmente os três pares. Em1440 o novo mês ocupa menos espaço e a área econômica mostra os sete campos, com números alinhados à direita; a imagem antiga exibia fonte/horário original em cada cartão, sem os campos numéricos. Em390 o novo reflow mantém os três valores rotulados por evento, com proveniência recolhida, e mostra mais eventos na mesma viewport. Em320 a grade e as ações cabem melhor no painel atual, e os três valores permanecem visíveis; a fonte pública/sinal/unidade usados são sintéticos e idênticos nos dois lados.

## Sobreposição de Notas e acesso por rolagem: resultado bruto preservado

O renderer anterior teve12 alvos inspecionados no320: seis horários pendentes e seis links-fonte. Todos ficaram livres nas cinco amostras após scrollIntoView(center); aggregate bruto=true, sem interseção com Notas após a rolagem.

O renderer atual teve12 alvos: seis avisos e seis botões i. Houve uma interseção geométrica inicial entre o botão Notas e o aviso do segundo evento. Depois da rolagem, os seis avisos ficaram livres nas cinco amostras cada,30/30; nenhuma das12 caixas-alvo intersectou Notas após sua própria rolagem. O aviso inicialmente sobreposto passou às cinco amostras livres.

**O aggregate bruto atual é false e continua false no inventário. Não foi reclassificado como PASS.** Nos seis botões i, o ponto central acertou o próprio botão/descendente,6/6. As24 amostras nos quatro cantos acertaram `calendar-economic-title-line`, pai imediato da área do controle, sem interseção com Notas. Esse padrão é compatível com os cantos externos ao contorno arredondado do botão: a caixa geométrica44×44 tem border-radius12, e pontos a2px dos cantos podem atingir o pai. O coletor exige target/descendente em todos os cinco pontos e por isso agrega false. Não alterei seu critério nem o script congelado para esconder esse resultado.

A distinção exige avaliação independente: os dados não mostram Notas sobre o alvo central após rolagem, mas não demonstram que todos os44×44 pixels da caixa do botão sejam área de hit do próprio botão. Também não demonstram ausência global de sobreposição na página: um controle fixo pode continuar cobrindo outra linha no canto da viewport enquanto o alvo examinado está centralizado. A prova delimitada é de acesso aos avisos e aos centros dos controles ao rolar.

Capturas de viewport dos alvos centrais e todos os cinco hits estão no inventário; os PNGs `320-light-execEcal-after-scroll-rowN-detail-or-source-control.png` preservam a evidência dos corner misses. O código de Notas e suas regras CSS permanecem iguais ao baseline, conforme revisão anterior; a comparação controlada identifica uma ocorrência inicial específica na nova disposição, sem demonstrar perda permanente de acesso.

## Toque emulado — somente observações brutas

Diretório: `product-proposal/touch-final-20261029`.
JSON bruto: `raw-observations.json`, SHA256 `3b2ca8aef6fcf499daa5c759e19f65c0f3bad6d9f719cfe7e000388e163c6f43`.
Launcher log: `product-proposal/touch-final-20261029-launch.log`.

collection_state=completed em quatro contextos independentes; product_validation=NOT_JUDGED. Viewports390×900 e320×900, cada uma no workspace e no modal, has_touch=True. Todos registraram maxTouchPoints1, ontouchstart disponível, pointer:coarse=true e hover=false.

Nos quatro contextos, o primeiro `.tap()` foi seguido por aria-expanded=true, detalhe visível e um link Forex Factory visível. O segundo `.tap()` foi seguido por aria-expanded=false, detalhe e link ocultos. O terceiro `.tap()` voltou a expor detalhe/link. São estados lidos, sem oráculo novo de aprovação.

Nos dois modais, Escape fechou o diálogo, ocultou o detalhe por fechamento do host e devolveu foco a headerCalendarBtn. O atributo de expansão permaneceu true em RAM no DOM do modal fechado, coerente com o estado não descartado; não o registrei como detalhe visível. Nos dois workspaces, Escape preservou o detalhe aberto; o `.tap()` final foi seguido por expansãofalse e detalhe oculto.

Eventos brutos totalizados:14touchstart,14touchend,14click e4keydownEscape; todos isTrusted=true, sem touchcancel registrado. As quatro coletas têm page_errors=[]; fingerprints dos dados financeiros sintéticos antes/depois iguais. Fontes8cfa/31e e todos os hashes de shell/15/16 registrados permaneceram iguais após a coleta. Quatro screenshots de viewport do detalhe aberto acompanham o JSON.

Não houve erro de launcher/coleta nessas duas execuções; logs e inventários originais foram preservados. Exit0 do toque significa término da coleta, nunca PASS funcional. Não foram testados toque físico, outros dispositivos, leitor de tela ou aceite humano. Submeter os dados/capturas ao revisor independente antes de qualquer conclusão de entrega.

## Scripts preservados

- capture-before-after-six.py: `60175a21138dffc625ed30879fdd41aeb24bf0de7778fdf92aa46cf58b91c1ab`.
- observe-economic-touch-after-full.py: `3f5d6091f3bad0767e842d5e0fdca411807d393c7e46c91d4a78459806c5281b`.
