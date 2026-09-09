# Alladin — consolidação dos investimentos

Fotografia: 2026-09-09, branch `codex/dashboard-official`, revisão `5393e4abfd4af5c8e83344914088c260a1cbfe76`, árvore equivalente à main integrada. [Visão geral e legenda](<00 - Função Principal do Software.md>). Fonte operacional: [CURRENT-STATE](../docs/governance/CURRENT-STATE.md).

## 1. Finalidade

**CONFIRMADO — proprietário:** consolidar completamente os investimentos e oferecer uma visão integrada da carteira. É a visão declarada neste pedido; descreve o resultado pretendido, não a completude atual.

**INFERÊNCIA:** seu papel é permitir entender o que se possui e onde está, com relações confiáveis entre cadastros e acontecimentos econômicos. A finalidade patrimonial envolve profundidade que o panorama transversal do Dashboard não deve reproduzir.

## 2. Responsabilidades e limites

Alladin é responsável pelos registros patrimoniais suportados, contas, instrumentos, fatos econômicos e posições derivadas. Research trata possibilidades e fundamentação; a existência de um estudo não cria posse. Finanças Pessoais trata orçamento/fluxos pessoais; Forex mantém sua fonte operacional.

O [contrato vigente](../docs/architecture/ALLADIN.md) também inclui cadastro de bens. Isso é capacidade existente do modelo, não ampliação atribuída à declaração do proprietário. Cadastro de um bem não comprova seu valor atual, e saldo de caixa não deve ser duplicado como bem. Uma família de instrumento disponível em cadastro não comprova suporte completo a todos os eventos daquela classe de ativo.

## 3. Uso e informações

Jornada identificada: cadastrar instrumentos, bens, contas e contas de caixa; registrar fatos econômicos suportados; consultar lançamentos, saldos e posições; corrigir lançamento elegível por estorno.

Entradas: dados cadastrais, moeda, datas, montantes, quantidades e referências entre entidades informados pelo usuário. Saídas: cadastros, histórico econômico, saldo por conta de caixa e quantidade por instrumento/conta. O agregado é `S.alladin`; os leitores derivam saldos e posições. O módulo verifica compatibilidade/integridade e pode declarar os dados indisponíveis, em vez de apresentar zero.

O usuário responde pela correspondência com documentos de custódia e movimentação. A operação de compra/venda registrada no ledger representa um fato informado; não comprova que a aplicação enviou uma ordem ao mercado.

## 4. Estado implementado

| Recorte | Classificação e evidência |
|---|---|
| Cadastros das quatro entidades | CONFIRMADO — completos no recorte de leitura/criação/edição e estado cadastral: [domínio](../src/js/10-domain/13-alladin.js), [interface](../src/js/20-ui/24-alladin-views.js), checks `alladin-unit` e `alladin-ui-crud` |
| Ledger e interface econômica | CONFIRMADO — depósitos, retiradas, transferências, compras/vendas, taxas/impostos standalone e ajustes de reconciliação suportados; check `alladin-ledger` e checks `alladin-ui-ledger`/`alladin-ui-tx-write` |
| Correção por estorno | CONFIRMADO — `reverseTransaction` e interface específica; check `alladin-ui-tx-reverse`. Não é edição livre do lançamento original |
| Saldo e posição por quantidade | CONFIRMADO — leitores `saldoDeCaixa` e `posicoes`, identidade instrumento × conta; checks `alladin-position` e `alladin-ui-readonly`. Quantidade não equivale a valor de mercado |
| Suporte monetário atual | CONFIRMADO — runtime BRL/USD e montantes em unidade mínima por moeda; `reportingCurrency` não implementa conversão cambial. Não somar moedas diferentes |
| Consolidação completa de investimentos | Parcial: faltam posição consolidada entre contas, custo de aquisição/cost basis, valuation, P&L, performance e benchmark, conforme fronteiras atualizadas do contrato |
| Integrações externas e cobertura de toda a carteira real | NÃO VERIFICADO — não há evidência suficiente de importação automática de custódias, cotações e todas as classes/eventos do usuário |

Os checks são os aprovados no CI existente indicado na visão geral, sem execução nova. O contrato contém um aviso antigo de “apenas cadastro”, expressamente superado por seções posteriores: ele não foi usado para negar o ledger já existente. Ajustes de reconciliação registráveis não equivalem a um Reconciliation Engine completo. A spec externa citada pelo contrato não foi consultada; não se atribuem novas aprovações a ela.

## 5. Integração

**CONFIRMADO — existente:** Alladin fornece ao Dashboard leitores de posições, cadastros, saldos e lançamentos. Dashboard apresenta uma amostra e orienta o acesso; não mantém outro livro patrimonial.

**Pendente de contrato:** HD-1 (Forex→Alladin), HD-2 (dívida pessoal/passivo) e HD-3 (Planejamento FX) permanecem registrados no contrato. Uma transferência interna Alladin é um evento de seu próprio ledger, não uma integração automática com Forex ou Finanças Pessoais.

**RECOMENDAÇÃO:** um eventual vínculo com Research deve ser referência à fundamentação, sem confundir lista de interesse com posição. Identidades dos catálogos devem ser mapeadas explicitamente; não presumir equivalência por ticker ou nome.

## 6. Evolução sugerida

1. **RECOMENDAÇÃO:** fechar as fronteiras de origem e identificação de fatos antes de automatizar importações ou integração Forex/PF. Benefício: prevenir dupla contagem. Depende das decisões HD-1/HD-2/HD-3 e critérios de conferência; não exige duplicar ledgers.
2. **RECOMENDAÇÃO:** delimitar uma primeira visão consolidada de posições, separando quantidade de valor. Benefício: aproximar a carteira integrada com um recorte verificável. Depende de identidade, custódia e tratamento de registros indisponíveis; não antecipar método de custo ou performance.
3. **RECOMENDAÇÃO:** avaliar valuation em etapa própria após definir fontes, datas, moedas e política para dados ausentes. Benefício: conhecer valor patrimonial com contexto. Depende de contratos financeiros aprovados; nenhum método, integração de preços ou fórmula é instituído aqui.
