# Dashboard — síntese e orientação

Fotografia: 2026-09-09, branch `codex/dashboard-official`, revisão `5393e4abfd4af5c8e83344914088c260a1cbfe76`, árvore equivalente à main integrada. [Visão geral, legenda e evidências da revisão](<00 - Função Principal do Software.md>). Fonte operacional: [CURRENT-STATE](../docs/governance/CURRENT-STATE.md).

## 1. Finalidade

**CONFIRMADO — proprietário:** resumir as demais áreas e permitir acesso aos módulos. É a visão declarada neste pedido. O resultado pretendido é permitir ao usuário entender o panorama e escolher onde aprofundar o trabalho.

**INFERÊNCIA:** a pergunta central é “o que merece minha atenção agora?”. A síntese deve preservar contexto suficiente para evitar que um número isolado seja interpretado como decisão de investimento.

## 2. Responsabilidades e limites

Reunir informações derivadas de Forex, Finanças Pessoais, Research e Alladin, com atalhos e estados de ausência ou indisponibilidade. A edição especializada e a responsabilidade pelo dado permanecem nos respectivos módulos.

Dashboard não é o livro de investimentos: contagens e saldos de Alladin não substituem seu histórico. A soma dos cards não representa patrimônio líquido; eles incluem moedas, competências e grandezas distintas. Seu veredito Forex é projeção do motor existente, não uma nova regra ou homologação da V11.

## 3. Uso e informações

Jornada identificada: abrir o panorama, ler os quatro resumos, escolher um atalho, trabalhar no módulo e retornar. A seção “Operação e ferramentas” permite acessar os widgets existentes; sua presença no Dashboard é conveniência de interface, não transferência da responsabilidade financeira.

Entradas: estado operacional e fechamento Forex, plano FX, métricas mensais pessoais e crédito vigente, estudos/agenda e leitores do Alladin. Saídas: cards, avisos, contagens, valores contextualizados e navegação. O resumo não grava esses dados; os renderizadores e leitores são identificados em [25-dash-macro.js](../src/js/20-ui/25-dash-macro.js), especialmente `dmForexHTML`, `dmFinpesHTML`, `dmResearchHTML` e `dmAlladinHTML`.

## 4. Estado implementado

| Recorte | Classificação e evidência |
|---|---|
| Quatro cards e atalhos profundos | CONFIRMADO — completo no recorte: funções acima, `dashMacroRender`, tratamento de clique e check `dashboard-macro` aprovado no CI referenciado |
| Resumo Forex | CONFIRMADO — risco/veredito, último fechamento e resultado/desvio do plano quando disponível; leitura do motor legado |
| Resumo pessoal | CONFIRMADO — receita, despesa, sobra, dívida, crédito vigente, pendências e comparação; mês não registrado e cobertura incompleta têm apresentação própria |
| Resumo Research | CONFIRMADO — cobertura/contagens de estudos e agenda; não avalia a qualidade ou rentabilidade de uma tese |
| Resumo Alladin | CONFIRMADO — quantidade de posições, cadastros, até três saldos de caixa e último lançamento; parcial diante da visão completa de carteira |
| Atualização e apresentação | CONFIRMADO — hooks de render/feed/visibilidade, foco preservado e ferramentas expansíveis; [teste específico](../tools/dashboard_macro_test.py) e [auditoria de entrega](../docs/audit/DASHBOARD-OFFICIAL-2026-09-09.md) registram o recorte validado |
| Patrimônio total e desempenho consolidado | Não implementados neste resumo. NÃO VERIFICADO — completude do panorama sobre dados reais ou todos os investimentos do usuário |

O CI existente confirma o teste indicado na revisão, não uma validação nova nesta tarefa. O feed externo real não foi consultado para verificar disponibilidade.

## 5. Integração

**CONFIRMADO — existente:** os quatro módulos fornecem dados para leitura no Dashboard. Research e o widget de agenda compartilham domínio/cache. `JPWNavigation` encaminha para as telas; Finanças Pessoais e Research usam destinos locais, e Alladin suas vistas próprias. Atalhos são navegação, não integração de lançamentos.

**INFERÊNCIA:** o Dashboard pode orientar prioridades de trabalho, mas a decisão continua humana. Abrir “Saldos” ou “Planejamento” não transfere dinheiro, materializa investimento ou autoriza operação.

## 6. Evolução sugerida

1. **RECOMENDAÇÃO:** tornar origem, competência e atualização dos resumos mais explícitas onde ainda houver ambiguidade. Benefício: reduzir leitura fora de contexto. Depende de metadados existentes; evitar rótulos de atualização em tempo real sem evidência.
2. **RECOMENDAÇÃO:** avaliar uma síntese das pendências já calculadas pelos módulos. Benefício: orientar a próxima ação com pouca complexidade. Depende de contratos de leitura; não criar prioridade financeira ou regra de risco nova no Dashboard.

São propostas não aprovadas. Não se sugere criar outro livro financeiro ou antecipar valuation ausente no Alladin.
