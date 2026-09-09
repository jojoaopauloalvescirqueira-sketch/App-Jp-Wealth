# Forex — operação ativa e gerenciamento de risco

Fotografia: 2026-09-09, branch `codex/dashboard-official`, revisão `5393e4abfd4af5c8e83344914088c260a1cbfe76`, árvore equivalente à main integrada. [Visão geral e legenda](<00 - Função Principal do Software.md>). Fonte operacional: [CURRENT-STATE](../docs/governance/CURRENT-STATE.md).

## 1. Finalidade

**CONFIRMADO — proprietário:** ambiente de trabalho ativo em derivativos e gerenciamento de risco, idealizado como “Estatuto JP Wealth Vivo”: aproximar o trabalho operacional das regras e controles aprovados. Esta é a visão declarada neste pedido.

Essa expressão descreve a finalidade pretendida. **CONFIRMADO — contexto e índice normativo:** a adoção documental V11 não adaptou o motor financeiro legado. Logo, a expressão não comprova que o software implementa o Estatuto vigente.

**INFERÊNCIA — interpretação de produto:** aproximar trabalho e regras exige que o usuário consiga compreender a origem dos controles e relacioná-los aos registros da operação. Isso orienta a experiência desejada, sem estabelecer controles adicionais ou declarar conformidade atual.

## 2. Responsabilidades e limites

Forex reúne preparação, conta, operação, risco, apuração e planejamento específico. Research fornece ambiente de estudo; Finanças Pessoais trata orçamento pessoal/familiar; Alladin tem a responsabilidade de consolidação dos investimentos.

Um valor planejado não é saldo recebido nem investimento possuído. O plano FX não substitui o orçamento familiar. Controles e registros na aplicação não comprovam execução externa, custódia ou proteção efetiva em uma corretora. As saídas do motor existente são descritas como comportamento de software, não como nova norma financeira.

## 3. Uso e informações

Jornada identificada: cadastrar/consultar conta e início do período; revisar preparação; acompanhar ordens registradas e risco; registrar resultados/fechamentos; consultar apuração e histórico; elaborar ou revisar o plano FX e seus realizados mensais.

Entradas: parâmetros e registros informados pelo operador, instrumentos, ordens e resultados, saldo de fechamento, premissas e aportes do plano. Saídas: cálculo de risco/fase/exposição e veredito operacional, histórico/apuração e comparação entre baseline, previsão vigente e realizado. O usuário continua responsável pela exatidão e correspondência com registros externos.

Fontes de dados identificadas incluem `S.params`, `S.phases`, `S.accounts`, `S.ledger` e `S.fxPlanning`. São estruturas distintas: o fechamento diário e o realizado mensal do planejamento não devem ser presumidos sincronizados apenas por pertencerem ao mesmo módulo.

## 4. Estado implementado

| Recorte | Classificação e evidência |
|---|---|
| Seis destinos Forex | CONFIRMADO — Visão Geral, Preparação, Conta, Operação, Apuração e Planejamento em [navegação](../src/js/40-app/01-navigation.js); funções abaixo sustentam o conteúdo além dos títulos |
| Risco/veredito e guardas operacionais | CONFIRMADO — implementados no [cálculo](../src/js/10-domain/02-risk-calculations.js), [veredito](../src/js/20-ui/04-operational-clearance.js) e fluxos de ordens; checks `order-guards` e `operation-finalize` aprovados no recorte existente |
| Fechamento e apuração | CONFIRMADO — [ledger diário](../src/js/30-accounting/01-daily-ledger.js) ordena registros, sincroniza saldo e preserva arquivo de períodos; [motor contábil](../src/js/30-accounting/02-accounting-engine.js) apresenta a apuração. Isso não prova reconciliação automática com extrato externo |
| Planejamento FX | CONFIRMADO — completo no recorte de plano, premissas, realizados e comparações descrito no [contrato](../docs/architecture/FX-PLANNING.md), [motor](../src/js/30-accounting/05-fx-planning/02-fx-engine.js) e [estado](../src/js/30-accounting/05-fx-planning/03-fx-state.js); check `fx-planning` aprovado |
| “Estatuto Vivo” aderente à V11 | Parcial como finalidade: documentos V11 adotados, motor ainda legado. NÃO VERIFICADO — conformidade financeira integral com V11; divergências FCR/FEO e estados pendentes permanecem no [índice normativo](../docs/normative/README.md) |
| Execução automática em corretoras | NÃO VERIFICADO — não há evidência suficiente para atribuir essa capacidade ao módulo nesta revisão |

Os checks pertencem ao CI existente citado na visão geral. `statute-documentary` comprova seu recorte documental, não conformidade de cálculos. Seções históricas do contrato FX referem artigos/regras anteriores; não são revalidadas nem promovidas a norma vigente por este documento.

## 5. Integração

**CONFIRMADO — existente:** o Dashboard projeta risco, veredito, último fechamento e resultados disponíveis do plano. Research compartilha o catálogo de instrumentos; seus estudos não liberam operação. O planejamento consome referência diária USD/BRL por [provedor de cotação](../src/js/10-domain/08-usd-brl-quote.js), separada das premissas futuras.

**Manual:** receita efetivamente destinada à vida pessoal pode ser registrada pelo usuário em Finanças Pessoais. Isso não estabelece transferência automatizada. **Pendente de contrato:** publicação Forex→Alladin e fronteira do plano com patrimônio são HD-1/HD-3 no [contrato Alladin](../docs/architecture/ALLADIN.md). Duplicar os mesmos recursos no ledger de trading e no patrimônio sem vínculo definido pode produzir dupla contagem.

## 6. Evolução sugerida

1. **RECOMENDAÇÃO:** tratar a adequação V11 como projeto próprio, começando pelas divergências já registradas e decisões humanas necessárias. Benefício: reduzir risco de falsa conformidade. Depende de autoridade normativa e testes específicos; não propõe parâmetros ou fórmulas aqui.
2. **RECOMENDAÇÃO:** explicitar a origem e a conferência dos dados operacionais em relação a extratos. Benefício: reduzir divergência entre registro e fato externo. Depende de definir a jornada; importação ou conexão automática não está aprovada.
3. **RECOMENDAÇÃO:** definir uma única projeção de fatos Forex para Alladin, se desejada. Benefício: evitar duplicidade e trabalho manual. Depende da decisão HD-1 e da distinção entre planejado, executado e possuído; não criar outro ledger Forex.
