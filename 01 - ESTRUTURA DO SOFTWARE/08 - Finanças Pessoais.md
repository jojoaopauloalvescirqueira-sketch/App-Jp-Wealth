# Finanças Pessoais — organização pessoal e familiar

Fotografia: 2026-09-09, branch `codex/dashboard-official`, revisão `5393e4abfd4af5c8e83344914088c260a1cbfe76`, árvore equivalente à main integrada. [Visão geral e legenda](<00 - Função Principal do Software.md>). Fonte operacional: [CURRENT-STATE](../docs/governance/CURRENT-STATE.md).

## 1. Finalidade

**CONFIRMADO — proprietário:** planejar a vida financeira pessoal e familiar, incluindo registro e acompanhamento de despesas e organização financeira. É a visão declarada neste pedido.

**INFERÊNCIA:** o resultado pretendido é compreender compromissos, recursos e consequências de escolhas para tomar decisões deliberadas. O alcance familiar da finalidade não comprova contas individuais, permissões compartilhadas ou colaboração simultânea no software.

## 2. Responsabilidades e limites

O módulo organiza orçamento, receitas/despesas, dívidas, crédito, comparações mensais e cenários. Patrimônio e consolidação de investimentos pertencem ao Alladin; risco e capital operacional específico pertencem ao Forex.

**CONFIRMADO — contrato:** o domínio é fechado em relação a contas de trading, contabilidade operacional e Planejamento FX. Uma receita de trading pode ser registrada como receita pessoal pelo usuário; não há integração automática. Sobra orçamentária ou alocação registrada não prova transferência para corretora, constituição de reserva ou aquisição de investimento.

## 3. Uso e informações

Jornada identificada: selecionar competência; registrar receitas, despesas e valores realizados; acompanhar dívidas e crédito; revisar pendências/comparações; experimentar um cenário separado dos meses reais.

O agregado `S.personalFinance` guarda meses, recorrências, dívidas, linhas de crédito e cenários. O usuário informa os valores; o módulo deriva seus indicadores. No contrato vigente, montantes são centavos de BRL; ausência e zero têm significados distintos. A competência sem edição é virtual, não histórico realizado. O crédito é posição vigente, enquanto observações de dívida pertencem a competências específicas.

Saídas: projeções/realizados com cobertura explícita, sobra quando calculável, pendências e comparação. Cenários não alteram meses reais. A [fundação do domínio](../src/js/10-domain/12-personal-finance.js) contém atos `pfAct*`, métricas `pfCompMetrics`, comparação `pfCompCompare` e funções de cenário.

## 4. Estado implementado

| Recorte | Classificação e evidência |
|---|---|
| Visão Geral, Orçamento, Dívidas/Crédito, Comparativo e Cenários | CONFIRMADO — completos no recorte V1 delimitado pelo [contrato](../docs/architecture/PERSONAL-FINANCE.md), domínio e navegação; checks `finpes-overview`, `finpes-budget`, `finpes-debt-credit`, `finpes-comparison` e `finpes-scenarios` aprovados |
| Tratamento de meses e dados parciais | CONFIRMADO — materialização por edição e estados de cobertura; valores incompletos não autorizam interpretar a soma parcial como total |
| Preservação e backup | CONFIRMADO — checks `finpes-finalize-preservation` e `finpes-backup-roundtrip` aprovados no CI existente para os casos cobertos; não é auditoria de backups reais do usuário |
| Planejamento pessoal/familiar completo | Parcial frente à finalidade ampla: V1 entregue não comprova toda necessidade familiar. NÃO VERIFICADO — colaboração multiusuário, integração bancária e automação de conciliação |
| Inventário/patrimônio no módulo | Não pertence ao domínio vigente; o contrato registra retirada desse escopo e responsabilidade própria do Alladin |
| Cartão/parcelamentos e importação histórica do Excel como produtos completos | Não comprovados nesta revisão. O contrato os cita como FUTURE; isso não é aprovação nova, prazo ou promessa de entrega |

Os resultados acima são evidências anteriores consultadas, não testes executados nesta tarefa. O contrato v1 permanece intacto; este texto não amplia schema ou interpreta conteúdo financeiro inválido.

## 5. Integração

**CONFIRMADO — existente:** o Dashboard consome as métricas pessoais por funções canônicas, com competência e completude. Navegar do resumo para Orçamento ou Dívidas não cria registro financeiro.

**Manual:** o usuário registra receita recebida e eventual destinação conforme os fatos da vida pessoal. Não se presume que lucro de trading equivale a saque recebido. Uma saída destinada a investimento não comprova uma posição Alladin.

**Pendente de contrato:** a relação dívida pessoal↔passivo patrimonial é HD-2 no [Alladin](../docs/architecture/ALLADIN.md). Um vínculo futuro precisaria distinguir obrigação, observação de saldo e fluxo de pagamento, sem contar a mesma dívida duas vezes. Nenhuma transferência ou sincronização econômica é implementada por esta documentação.

## 6. Evolução sugerida

1. **RECOMENDAÇÃO:** aperfeiçoar a orientação sobre competências incompletas, crédito vigente e pendências usando os estados já existentes. Benefício: interpretação correta com baixa complexidade; não preencher ausências automaticamente.
2. **RECOMENDAÇÃO:** explicitar na jornada a diferença entre destinar recursos e confirmar a movimentação para operação/investimento. Benefício: evitar tratar orçamento como saldo investido. Depende de exemplos e de contrato futuro caso haja vínculo de dados.
3. **RECOMENDAÇÃO:** avaliar importação assistida somente após demonstrar necessidade e definir conferência/duplicidade. Benefício: reduzir digitação. Depende de formato, privacidade e compatibilidade; conexão bancária e mudanças de dados exigem autorização própria.
