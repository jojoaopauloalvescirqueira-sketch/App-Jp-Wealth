# Revisão independente das observações finais —29/10/2026

Os comportamentos observados são compatíveis com o desenho aprovado neste recorte. Não foi identificado bloqueador funcional novo nas coletas. Há limitações visuais concretas de sobreposição transitória e de amostragem dos cantos, descritas abaixo e preservadas nos dados. Este parecer não cria controle, não altera juiz e não declara aprovação global de UI, FULL ou aceite humano.

## Identidade e alcance

Roteiros lidos e hashes conferidos: capture-before-after-six.py `60175a21138dffc625ed30879fdd41aeb24bf0de7778fdf92aa46cf58b91c1ab`; observe-economic-touch-after-full.py `3f5d6091f3bad0767e842d5e0fdca411807d393c7e46c91d4a78459806c5281b`.

Inventário de comparação SHA256 `e23a2a0d15f82bc57a504d7b795d04fa5143154582c9ac1abede24cce91c674e`. Recibo bruto de toque SHA256 `3b2ca8aef6fcf499daa5c759e19f65c0f3bad6d9f719cfe7e000388e163c6f43`.

São **seis capturas, três pares**, e não seis pares:1440 claro/workspace;390 escuro/modal;320 claro/workspace. Todos têm seis eventos e o mesmo domainSHA `f0f906e631a0fe6df7ffd69ba95b7a4a6f9fd392d438add0ef5ff58edb2a55e7`. Os seis hashes de PNG conferem. O “antes” é renderizador/CSS baseline sobre shell atual aabc; não é reprodução de release histórica. O “depois” usa19=8cfa/CSS31e. Li as seis capturas principais, duas capturas de rolagem320 (linhas1 e5) e as quatro de detalhe aberto por toque; hashes das quatro de toque também conferem.

## Apresentação observada

Em1440, mês passa de529 para308px e notícias de529 para750px, preservando largura útil1082. Cabeçalhos, linhas e valores aparecem em sete colunas; zeros/unidades/sinais da fixture permanecem. Em390, mês308px, notícias332px e valores rotulados em segunda faixa. Em320, largura útil cresce de266 para308px, mês308 e notícias308, preservando a grade mensal de sete alvos. Os três registros atuais indicam overflow econômico0. As capturas mostram menor espaço ocupado pela proveniência recolhida e mais eventos visíveis. Isso é observação destes dados, não prova exaustiva de todos os títulos/tamanhos/temas.

## Resultado negativo de amostragem preservado

No320 atual, all_targets_unobscured_after_scroll é **false**. Cada um dos seis botões i tem centro livre e caixa44×44, mas os24 pontos a2px dos cantos atingem o pai calendar-economic-title-line; portanto cada unobscured do i é false. O CSS compartilhado tem border-radius12px: o padrão de hits é coerente com cantos externos à forma arredondada, sem elemento de Notas sobre o alvo. Não substituí o agregado por true, nem redefini critério/controle. Esses dados não provam que todo pixel da caixa44×44 seja clicável; comprovam somente os pontos registrados. O centro SVG serializa hit como objeto vazio, mas clear=true decorre da relação contains calculada pelo próprio roteiro.

Os seis avisos têm cinco pontos livres após rolagem; os seis centros do i ficam livres; nenhuma caixa de aviso/i intersecta Notas após centralização. Antes de rolar, há uma interseção geométrica do segundo aviso com Notas em320. Na captura inicial e nas capturas de toque do workspace, o botão flutuante pode encobrir parte de conteúdo próximo ao rodapé. Isto é uma limitação visual real, não “ausência absoluta de sobreposição”. A rolagem demonstrada permite acessar as linhas sem essa sobreposição; nenhuma inacessibilidade persistente foi evidenciada. Cinco pontos livres, isoladamente, não provam que toda a tinta entre eles esteja descoberta.

O classification=PASS do inventário corresponde apenas à conclusão das capturas/precondições de fixture/identidade; não julga o agregado false nem representa PASS de acessibilidade. functional_gate e human_acceptance continuam NOT_RUN no inventário.

## Toque e Escape

Quatro contextos claros independentes390/320 × workspace/modal, has_touch=True. Os registros contêm14 touchstart,14 touchend e14 click, todos isTrusted=true, além de quatro Escapes confiáveis. Em cada contexto: detalhe inicia recolhido; primeiro tap abre e torna a fonte visível; segundo recolhe; terceiro reabre. O link permanece Forex Factory e as capturas mostram horário original/fuso e explicação da ausência de Atual.

No modal, Escape fecha o diálogo e devolve foco a headerCalendarBtn; aria-expanded permanece true na árvore oculta, o que não equivale a detalhe visível. No workspace, Escape conserva o detalhe aberto e o foco no i; o tap final o recolhe. Ambos correspondem ao contrato legado, sem sequência inventada de duplo Escape.

Os quatro hashes financeiros antes/depois coincidem e não há pageerror registrado. Isso cobre o estado sintético após bootstrap, não dados do operador nem ausência de toda escrita no storage efêmero. Recibo mantém product_validation=NOT_JUDGED; collection_state=completed informa coleta concluída. Fontes e shell registram estabilidade no final.

## Limites finais

Nenhum browser, teste, gerador ou edição de repo foi executado nesta revisão; apenas leitura dos scripts, JSON, imagens, fontes pertinentes e escrita deste relatório scratch. A coleta de toque exercita o primeiro evento em tema claro; não é prova de todos os eventos/temas, dispositivo físico, Safari/iOS/Android nativo, nem aceite humano. Comparação visual não transforma baseline em release antiga nem amplia116/413. O resultado FULL deve ser reconciliado em revisão própria.
