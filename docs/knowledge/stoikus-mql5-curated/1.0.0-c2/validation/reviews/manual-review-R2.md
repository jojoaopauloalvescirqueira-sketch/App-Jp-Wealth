# Parecer independente R2 — deltas técnicos e anexo crítico

**APROVAÇÃO dos deltas técnicos e do laboratório no escopo delimitado. P1 da pesquisa integral permanece ABERTO.** Este parecer complementa R1 e não aprova formatos/renderização nem o piloto comportamental.

## Identidade dos arquivos examinados

- `MANUAL.md`: `e4b352013cb56964b703af285267e22dca5bd50e92147a2a28555ec7c0eeed6f`
- `research/critical-synthesis.md`: `2873f7008009b432aa128f90f6b953664ffd8f45127614fc86b55ad11a140186`
- `examples/contraprovas_matematicas.py`: `0dd35838f5f711817a8dc637d7f6941cb09ee19a1375920af6e66518452fea35`
- `validation/math-lab.json`: `fd14157899949ef528256c198f6509bdde7f35e58c08c4d004bbce2b825b8c51`

## Fechamento dos dois P2 de R1

1. **TryDifference — RESOLVIDO.** MANUAL.md:87–99 agora recusa entradas não finitas e diferença não finita antes de atribuir `out`; a saída anterior é preservada em todas as falhas explícitas. O texto declara esse contrato e separa finitude de unidade, conta e instante. A citação REF, MathIsValidNumber, p.PDF 1986 corresponde ao contrato conferido em R1. Revisão estática; compilação MQL5 e execução MT5 continuam NOT_RUN.
2. **Multi-head — RESOLVIDO.** MANUAL.md:744 condiciona o aumento de parâmetros à largura por cabeça preservada no exemplo do livro, distingue largura total fixa e separa memória de scores. NN 5.2.1 p.PDF 462, conferida em R1, mostra precisamente matrizes nI×3nK e nI×3nI. Não há mais generalização indevida de parâmetros em toda arquitetura multi-head.

## Anexo research/critical-synthesis.md

A síntese preserva a distinção entre exemplo oficial, inferência estática, contraprova matemática e reprodução nativa. As propostas são identificadas como estudos; não autorizam negociação nem implementação neural no Stoikus. As referências diretas examinadas sustentam as observações:

- **TRD p.PDF 402:** STATS=10, bucket=32767/STATS e indexação stats[MathRand()/bucket]. O limite inteiro 32760..32767 produz índice 10, fora do array. A conclusão é estática e corretamente não apresentada como reprodução MQL5.
- **NN p.PDF 93:** conferi o texto extraído e inspecionei visualmente `source-visual/NN-93.png`. A página impressa é 93 e associa coeficiente zero à ausência completa de dependência. A contraprova com X simétrico e Y=X² é pertinente. A localização corrigida é confirmada.
- **NN p.PDF 335:** a exposição usa comutatividade para sustentar indiferença à posição; a distinção entre permutar entradas e permutar os pares peso/entrada corrige precisamente essa generalização.
- **NN p.PDF 225:** normalização MACD por máximo desvio do período analisado sustenta o exemplo de influência do futuro na escala, sem alegar que toda normalização seja inválida.
- **NN p.PDF 147 e 160:** SetOpenCL contém destruição/substituição do contexto, e a restauração chama SetOpenCL(m_cOpenCL), além de trabalhar com buffers/arrays. O anexo formula obrigação de conferir ownership e dimensões, sem promover uma suspeita local a defeito operacional reproduzido.
- **NN p.PDF 676, 688 e 689:** confirmados ajuste de parâmetros do EA no conjunto de treinamento, 36 posições/21 lucrativas/fator 1,48 e sugestão de seleção posterior de dias. As ressalvas experimentais do anexo são adequadas.

As observações secundárias remetidas às notas de leitores (wrappers, pooling, caches e eixos) conservam qualificações de análise estática. Não refiz toda a leitura das notas nem transformo essas remissões em auditoria integral independente de seus trechos.

## Laboratório matemático

Inspecionei integralmente `examples/contraprovas_matematicas.py` e executei com `/usr/bin/python3`, saída 0. A saída JSON nova é semanticamente idêntica a `validation/math-lab.json`. Somente biblioteca padrão; sem rede, alteração de produto ou gravação pelo script.

Quatro demonstrações foram exercitadas: soma ponderada 17 versus 11 sob permutação somente das entradas (com controle de permutação dos pares); Pearson zero apesar de Y=X²; mudança da representação de treino ao incluir máximo futuro; derivada numérica compatível com a regra da cadeia e rejeição da expressão que omite o fator de entrada. São exemplos pequenos e concretos que fortalecem a exposição. Não constituem reprodução de redes do livro, prova estatística de mercado ou execução MQL5. Os estados NOT_RUN declarados estão corretos.

## Pendências mantidas

**P1: leitura semântica integral REF/TRD não demonstrada**, conforme R1 e o escopo comunicado pelo coordenador. A cobertura textual NN declarada pela equipe não fecha essa lacuna. O manual pode ser aprovado como síntese candidata dentro de sua cobertura declarada; a etapa de pesquisa integral continua aberta.

Word/PDF e equivalência final permanecem sob revisão própria. Não li respostas do piloto, não reabri o freeze do harness e não alterei manual, fontes, kit ou recibo matemático. Somente este parecer foi escrito.
