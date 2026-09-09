# Research — estudo e fundamentação

Fotografia: 2026-09-09, branch `codex/dashboard-official`, revisão `5393e4abfd4af5c8e83344914088c260a1cbfe76`, árvore equivalente à main integrada. [Visão geral e legenda](<00 - Função Principal do Software.md>). Fonte operacional: [CURRENT-STATE](../docs/governance/CURRENT-STATE.md).

## 1. Finalidade

**CONFIRMADO — proprietário:** estudar modelos de investimento, analisar ativos e fundamentar a seleção, inclusive possibilidades futuras. É a visão declarada neste pedido. Research apoia a decisão do usuário e não pressupõe execução automática de investimentos.

**INFERÊNCIA:** seu resultado desejável é uma decisão mais bem fundamentada, com premissas compreensíveis e possibilidade de revisão, inclusive a decisão de não investir. Uma hipótese favorável não comprova retorno futuro.

## 2. Responsabilidades e limites

O estudo pertence ao Research; posse, custódia e fatos patrimoniais pertencem ao Alladin. Avaliação de risco e trabalho operacional Forex pertencem ao Forex. O Dashboard apenas resume disponibilidade de estudos e agenda.

Os contratos de NoCoda e Pivots excluem geração automática de sinais, ordens ou autorização operacional. A existência de uma área “Ações” não comprova análise de ações implementada. Não se presume que todo instrumento estudado corresponda a uma posição patrimonial.

## 3. Uso e informações

Jornadas identificadas: consultar Calendário em Research/Forex; escolher instrumento e registrar âncoras NoCoda; registrar estudos de Pivots identificados pelo operador, com período, preços, tempos e observações; revisar as derivações disponíveis.

Entradas: catálogo compartilhado de instrumentos, registros humanos e feed de calendário. Saídas: geometria do estudo NoCoda, estatística descritiva dos Pivots e apresentação da agenda. O operador identifica e informa as observações; os dados de estudo ficam em `S.nocoda` e `S.pivotStudies`. O calendário usa cache próprio. A seleção de tela é efêmera, conforme [superfície Research](../src/js/20-ui/23-research-views.js).

## 4. Estado implementado

| Recorte | Classificação e evidência |
|---|---|
| Calendário, NoCoda e Pivots em Research/Forex | CONFIRMADO — rotas, renderizadores e jornadas específicas identificados; check `research-navigation` aprovado no CI referenciado |
| NoCoda | CONFIRMADO — completo no recorte de memória técnica e geometria declarada: [contrato](../docs/architecture/NOCODA-STUDIES.md), [geometria](../src/js/10-domain/09-nocoda-geometry.js), [interface](../src/js/20-ui/14-nocoda-studies.js) e check `nocoda` |
| Pivots | CONFIRMADO — completo no recorte de registros manuais e análise descritiva: [contrato](../docs/architecture/PIVOT-STUDIES.md), [domínio](../src/js/10-domain/10-pivot-studies.js), [interface](../src/js/20-ui/15-pivot-studies.js) e check `pivot-studies`; não há detector automático/OHLC nesse contrato |
| Ações/B3, Stocks, REITs e Others | CONFIRMADO — destinos de navegação com placeholders em [index.html](../index.html), sem conteúdo funcional; não classificados como análise implementada ou evolução aprovada |
| Abrangência da visão de Research | Parcial: a finalidade declarada é mais ampla que as ferramentas Forex entregues. NÃO VERIFICADO — modelos analíticos completos para as outras áreas, cobertura comercial de dados ou qualidade preditiva |

Os checks citados foram aprovados no CI pós-merge existente; não houve nova execução. A presença de [código de feed](../src/js/40-app/15-ff-news.js) e [calendário](../src/js/40-app/17-economic-calendar.js) confirma a implementação de consumo/apresentação, não a disponibilidade atual do serviço externo.

## 5. Integração

**CONFIRMADO — existente:** NoCoda e Pivots usam a identidade do catálogo operacional de instrumentos; o Dashboard lê contagens e agenda. Catálogo compartilhado é uma relação de dados; mudar de tela pelo menu é apenas navegação.

**Manual:** o usuário interpreta o estudo ao tomar uma decisão. Não foi identificado um publicador de teses/seleções para Alladin nem envio de ordens à corretora nesses fluxos. O cadastro patrimonial Alladin tem identidade própria; símbolo semelhante não prova equivalência entre os catálogos.

## 6. Evolução sugerida

1. **RECOMENDAÇÃO:** definir um registro simples de tese, fontes, premissas e data de revisão antes de ampliar a quantidade de ferramentas. Benefício: rastreabilidade do raciocínio. Depende de decisão sobre escopo e armazenamento; não implica recomendação automática.
2. **RECOMENDAÇÃO:** escolher uma única área hoje vazia e caracterizar sua jornada com exemplos de uso. Benefício: reduzir expansão sem utilidade comprovada. Depende de fontes de dados e critérios de análise; o nome do menu não aprova o desenvolvimento.
3. **RECOMENDAÇÃO:** avaliar referência opcional entre um estudo e o instrumento no Alladin. Benefício: consultar a fundamentação de uma posição. Depende de mapeamento explícito de identidade e autoria; não criar posição ou transferência por esse vínculo.
