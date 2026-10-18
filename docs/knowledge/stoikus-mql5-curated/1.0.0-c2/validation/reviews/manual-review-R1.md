# Parecer independente R1 — manual e pesquisa

Decisão: **REVISÃO REQUERIDA**, com dois reparos técnicos localizados e uma pendência de escopo documental. Não há aprovação integral da pesquisa de 10.021 páginas. O manual já constitui uma síntese utilizável como candidato; sua extensão e correção nas amostras examinadas não encerram o requisito de leitura integral.

Objeto: `/private/tmp/jpw-stoikus-continuity-20261014/docs/knowledge/stoikus-mql5/MANUAL.md`, SHA-256 `ea102f21cb157b26bfc91404719c78b30641b019fbc6d1b41bbe999fd402c97e`, 960 linhas. Revisor separado da autoria. Li todo o texto do manual, consultei os registros de cobertura, o README e callbacks do Monitor, e confrontei contratos selecionados com o texto extraído das páginas físicas dos PDFs. Não modifiquei manual, produto, kit ou freeze; não executei MQL5 e não li respostas do piloto. Este parecer não é inspeção visual de todas as páginas nem comparação completa de todos os símbolos citados com os fontes.

## P1 — A pesquisa REF/TRD ainda não satisfaz leitura de todas as seções

**Local:** `MANUAL.md:15`; `research/reference-family-review.md:3`; `research/reference-family-review.json` (registros `all_descendant_entries_reviewed: false`); `research/engineering-coverage.json` (`whole_book_semantic_review: false`); `research/trd-semantic-coverage.json` (intervalo efetivamente lido 42–281 e seções `NOT_REVIEWED_IN_THIS_COMPLEMENT`).

**Prova:** o BRIEF exige estudo de todas as seções. A leitura das aberturas de famílias REF não lê os métodos descendentes: por exemplo, a família Matrix and Vector Methods ocupa 1287–1878, mas o registro de família identifica somente a abertura 1287. Os relatórios complementares TRD ampliam cobertura, sem demonstrar cobertura global. A redação atual é honesta e não afirma o contrário; portanto, esta é uma pendência de cumprimento do escopo, não fraude ou erro factual do texto. A informação recebida de conclusão textual NN não resolve REF/TRD e não foi convertida por este revisor em certificação independente das 690 páginas.

**Reparo concreto:** conservar o candidato com classificação explícita de síntese parcial enquanto se completa a leitura semântica restante; consolidar união de intervalos efetivamente lidos e lacunas por seção, sem propagar cobertura de pai aos filhos. Na entrega, não classificar a etapa global como concluída enquanto essa obrigação permanecer aberta. A mera extração ou um catálogo completo não resolve o achado. Nenhum reparo de texto pode substituir a leitura faltante.

## P2 — TryDifference promete resultado válido sem contrato de finitude/overflow

**Local:** `MANUAL.md:87–95`, capítulo 1.4, função `TryDifference` e explicação imediatamente posterior.

**Prova:** basta que `a.available` e `b.available` sejam verdadeiros para a função executar `out=a.value-b.value` e retornar `true`. Não há pré-condição declarada sobre valores finitos ou diferença representável. Mesmo duas entradas finitas, próximas de `DBL_MAX` e `-DBL_MAX`, têm diferença além da faixa de double. Assim, a frase “out só representa uma diferença válida quando a função retorna sucesso” sugere um contrato que o exemplo não estabelece. O próprio capítulo 4.6, linha 355, corretamente exige validação de resultados intermediários/finais, e REF p.PDF 1986 especifica que `MathIsValidNumber` rejeita infinito e NaN.

**Reparo concreto:** calcular em candidato local, rejeitar entradas não finitas e candidato não finito antes de atribuir a `out`, mantendo sua preservação na falha; alternativamente, limitar explicitamente o exemplo à disponibilidade e declarar as pré-condições de finitude e diferença representável, removendo a promessa ampla de validade. Preferível a primeira opção, coerente com o exemplo `LimiteDemonstrativo`. Não alegar compilação ou ensaio nativo após uma mudança editorial.

## P2 — Custo em parâmetros de multi-head está generalizado além da arquitetura descrita

**Local:** `MANUAL.md:740`, primeiro período do parágrafo “Múltiplas cabeças...”.

**Prova:** o texto afirma que múltiplas cabeças também aumentam a quantidade de parâmetros, sem fixar dimensões. NN 5.2.1, p.PDF 462, realmente usa matrizes `nI × 3nK` e `nI × 3nI`, mantendo largura por cabeça; nesse desenho a afirmação vale. Entretanto, se a largura total d for fixa e dividida em h cabeças com largura d/h, a soma das projeções Q/K/V tem `3 × h × d × (d/h) = 3d²` parâmetros, independentemente de h; a projeção de saída d×d também permanece constante. Portanto, a conclusão geral não decorre do simples aumento do número de cabeças. A parcela de scores explicitamente materializados pode crescer com h, distinção que também merece ser preservada.

**Reparo concreto:** escrever que **na parametrização do livro, com largura por cabeça mantida**, aumentar cabeças aumenta parâmetros/buffers; em parametrizações que mantêm a largura total, o número de parâmetros pode permanecer constante. Conservar a afirmação separada e correta de crescimento quadrático com comprimento da sequência para atenção densa.

## Condição de fechamento editorial

`MANUAL.md:23` diz que Word e PDF são “derivados conferidos”. Na revisão, `validation/editorial-build.json` ainda registra `renderState: PENDING`. Isto pode ser resolvido pela revisão visual em curso; não presumo falha dos derivados nem avalio seus renders neste parecer. Antes de manter essa frase na entrega, vincular conferência estrutural/visual e equivalência de conteúdo aos hashes finais dos derivados. Se não houver prova, trocar para estado pendente. Mudanças R2 no manual exigem regenerar seus derivados e conferir os bytes novos.

## Verificações favoráveis e limites

- Extensão: o método editorial real (`re.findall(r'\b\w+\b', texto)`) produz 24.559 unidades; sem seção final de referências, 24.329. Uma contagem conservadora, removendo também fences de código/diagramas, equações e citações principais, produz 22.727. Portanto, o intervalo de 20–30 mil palavras não depende de anexos ou de contar código para chegar ao mínimo. `wc -w` produz 23.785 no arquivo completo; a diferença é de tokenização. Não encontrei parágrafos extensos exatamente duplicados. Há retomadas de identidade/indisponibilidade/prova nos capítulos 7 e 10, pertinentes ao protocolo, sem evidência de padding necessário para cumprir extensão.
- Contratos amostrados nos PDFs: REF 1046 (reinicialização), 1155 (ARGB premultiplicado), 1263 (AS_SERIES), 1986 (finitude), 2082 (OnInit), 2098/3189 (timer), 2226 (CopyBuffer), 2642 (CAS); TRD 625/628 (globais e sobreposição), 838 (indicador dependente), 1561 (OnChartEvent no tester). Os mecanismos centrais estão corretamente representados. A frase de 3.7 sobre timer dependente poderia ser mais direta (“não recebe OnTimer”), mas não inverte o contrato e não é achado bloqueante.
- A descrição do Monitor corresponde aos callbacks inspecionados: timer, identidade, ownership e encaminhamento de transações; versão 1.23.0/MQL 1.230/cálculo 1.9.0 e NOT_RUN nativo constam do README atual. Não auditei transitivamente todas as dependências para provar ausência universal de ordens; o manual faz a distinção apropriada entre intenção de fonte e ensaio nativo.
- Normas JP Wealth, capacidade da plataforma, comportamento do candidato e proposta de evolução permanecem separados. Não identifiquei imposição de regra financeira nova nem alegação de ML operacional. O exemplo dimensional de volume S04 é matematicamente consistente e identificado como artificial.
- Os capítulos neurais contêm fórmulas dimensionais coerentes, restrição temporal do alvo, normalização apenas no treino como proposta distinta do livro, necessidade de oráculos e limites de amostras pequenas. A objeção multi-head acima é localizada. As afirmações experimentais detalhadas de NN 7.5 não foram todas rechecadas por este revisor contra imagens; não amplio a amostra de fontes consultadas para revisão independente integral do livro.
- Guia e harness: o capítulo 10 explica entradas, autoria/revisão/juiz, estados, congelamento, sessões novas e limites de generalização. Constitui um guia coerente para uso candidato; não prova eficácia frente a baseline nem substitui piloto. R2 do kit foi objeto de outro parecer; não reabri seu conteúdo nem seu freeze. Resultado comportamental segue o relatório próprio em curso.

Após os dois reparos técnicos e evidência editorial final, é possível aprovar o **conteúdo candidato do manual dentro de sua cobertura declarada**. A aprovação da **pesquisa integral** permanece uma decisão separada, dependente da cobertura semântica restante. Não são intercambiáveis.
