# Revisão independente final da pesquisa

**Resultado: PASS de rastreabilidade documental e amostra textual dirigida.** Não foi encontrado novo achado P1/P2 no escopo abaixo. A lacuna documental global anterior deixa de estar presente no snapshot final: os registros declaram 7.284 páginas REF, 2.047 TRD e 690 NN, sem faixa pendente. Isso permite encerrar o P1 de cobertura documental; não certifica uma segunda leitura integral independente nem a correção de cada interpretação dos livros.

## Escopo efetivamente executado

Li BRIEF e IMPLEMENTATION_PLAN, LEIA_ME, COMECE_AQUI, enquadramento do manual e síntese crítica; confrontei trechos selecionados do manual e das notas com o corpo extraído. Examinei notas e ledgers de diferentes leitores, incluindo os lotes finais 15b/16/17, limites de ancestrais e continuidades. A inspeção semântica independente foi amostral. O MANUAL tem 24.285 tokens separados por espaços nesta contagem simples (palavras, títulos e código incluídos); essa medida não substitui a contagem editorial de prosa nem a revisão anterior R1–R3.

Controles globais executados:

- 10.021 páginas extraídas únicas; SHA-256 recalculado do texto de todas, sem divergência.
- Inventário final de 10.021 identidades únicas: hashes coincidem com o corpus e todas têm declaração de leitura.
- Catálogo com 4.821 IDs únicos: REF 4.128, TRD 581, NN 112; nenhuma faixa invertida. Matriz preserva identidade/título/faixa do catálogo.
- União independente das faixas declaradas nas 40 entradas de evidência: REF 7.284, TRD 2.047, NN 690. Todas as 4.821 contagens de páginas lidas da matriz coincidem com essa união, sem dupla contagem das sobreposições.
- Todos os 40 hashes de evidência do resumo coincidem com os arquivos atuais.
- 7.177 comparações de hashes de páginas em campos reconhecidos dos ledgers: nenhuma divergência. Os formatos restantes não foram integralmente normalizados por esta auditoria.

A lista e os hashes do snapshot inspecionado estão em `research-final-audit.json`. Os SHA-256 dos PDFs originais foram recebidos do manifesto; não fiz nova leitura binária dos originais. Não alterei originais, produto, manual, kit, Git ou instruções.

## Amostra de corpo versus interpretação

Foram exibidas e examinadas integralmente 17 páginas de texto extraído: REF 1042, 1770, 2082, 2639, 6181, 6659, 6824, 7217; TRD 286, 1450, 1511; NN 42, 93, 547, 676, 688, 689. Uma exposição inicial conjunta sofreu truncamento; as páginas REF afetadas foram reexpostas em chamada menor. TRD141, visto parcialmente naquela chamada, não entra nas 17.

| Prova | Confronto e resultado |
|---|---|
| REF1042 / manual arquitetura | Threads próprias de EA/script/serviço e compartilhamento por símbolo nos indicadores estão representados corretamente no trecho examinado. |
| REF2082 / manual inicialização | Distinção INIT_FAILED entre EA descarregado e indicador anexado inoperante consta expressamente na fonte e no manual. |
| REF2639 / lote09 | Retorno void e gravação forçada aparecem na fonte; notas não promovem isso a transação multivariável. Não conferi nesta amostra toda a semântica de GlobalVariableTemp da página seguinte. |
| REF1770 / lote06 | A fonte lista ipiv apesar de assinaturas sem esse parâmetro; a nota registra a anomalia, sem inventar execução. |
| REF6181 / lote15b | MemoryAvailable, assinatura MemoryTotal e propriedade MEMORY_TOTAL contraditórias estão na página; a nota preserva a divergência e exige conferência futura. |
| REF6659 / lote15b e ledger16 | 15b credita somente a abertura CBmpButton; continuação é separada. Não há promoção desse leitor para todos os métodos. |
| REF6824 / lote16 | OnVScrollShow da base não faz nada e retorna true; nota distingue processamento de mudança real. |
| REF7217 / lote17 | Constantes de perda consecutiva e quantidade associada são diferenciadas no índice e na síntese da família. |
| TRD286 / notas4.1.2 | Faixa contratual NormalizeDouble 0–8 está na fonte; notas separam arredondamento de aderência a tick/step. Comentários sobre a página287 não foram revalidados aqui. |
| TRD1450 e1511 / notas tester | Sandbox do agente/FILE_COMMON e regras de visibilidade/template são evidência concreta; não foram convertidas em teste nativo do produto. |
| NN42 / notas profundas | Grafia m_cMomenum é visível no código; nota trata-a como indício bibliográfico, não defeito comprovado de produção. |
| NN93 / síntese crítica | Fonte associa correlação zero à ausência de dependência; crítica distingue correlação linear de independência. |
| NN547 / notas finais | Reformatação de buffers, substituição/alias e passagem para OpenCL têm corpo textual real; a leitura não prova restauração ou execução. |
| NN676,688,689 / manual avaliação e síntese | Reuso de treino para otimizar EA, 36 posições/21 vencedoras/PF1,48 e seleção posterior de dias constam da fonte. Manual distingue resultados relatados, calibração ausente e nova decisão que exige teste posterior. |

Não identifiquei, nessa amostra, nota que apenas repita um título sem conhecimento. Há frases de aplicação repetidas legitimamente em APIs aparentadas, acompanhadas de contratos específicos. Não tratei a presença de nota ou hash como prova automática de entendimento.

## Achados e limites de aceite

**P1/P2 novos: nenhum encontrado no escopo inspecionado.** A matriz final usa COMPLETE_TEXTUAL_DECLARATIONS no resumo e conserva `independent_full_source_audit: false`. O fechamento é documental e amostral. As notas de ancestrais dos lotes 15b/16/17 restringem-se à interseção; a completude final provém da união de páginas dos leitores, não da abertura de um capítulo-pai. Registros históricos parciais permanecem claramente descritos como históricos.

**P3 opcional — facilitar navegação da matriz para a nota.** O campo semantic_notes da matriz é genérico. 383 IDs não aparecem literalmente no Markdown combinado de pesquisa, embora títulos/seções numeradas e registros JSON permitam localizar notas, como TRD4.1.2. Acrescentar futuramente note_file/note_heading reduziria trabalho manual de conferência. Isso não é lacuna de leitura demonstrada nem requisito para fechar este parecer.

O recibo visual consultado é dirigido a 30 páginas de fontes, com identificação individual; não comprova as 10.021 páginas visualmente. A revisão das 56 páginas finais pertence aos recibos editoriais anteriores. Consultei o enquadramento do julgamento R3 e do guia: 36/36 pertence ao benchmark sintético daquela revisão, não comprova superioridade geral, MT5 ou adoção. Não reavaliei as 36 respostas, nem transferi esse resultado para a pesquisa. A distinção entre contrato da plataforma, contexto informado do Stoikus, norma competente e proposta está preservada nos trechos examinados.

Continuam fora deste parecer: segunda leitura integral dos três livros, auditoria visual integral das fontes, execução/compilação de exemplos, MetaEditor/MT5/EX5, validade financeira, aceite humano e reabertura nativa no Word. O manual foi examinado por enquadramento e citações dirigidas; a revisão de conteúdo integral anterior não foi repetida aqui.
