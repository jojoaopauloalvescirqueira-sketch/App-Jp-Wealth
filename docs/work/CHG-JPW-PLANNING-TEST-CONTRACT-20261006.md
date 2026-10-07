# CHG — expectativas da caracterização do Planejamento

Contrato separado do produto, 06/10/2026. Deriva das decisões explícitas do plano
de edição mensal; não muda os gates ou suas classificações.

O teste anterior `tools/fx_planning_test.py` passou na base preservada. No primeiro
replay do candidate, recusou-se o fechamento sem conferência de depósitos; a
fixture tentou acessar um realizado que corretamente não fora gravado. O erro
bruto foi preservado externamente, antes desta adaptação.

Expectativas alteradas intencionalmente:

- Rota canônica entra em Tabela mensal; aliases preservam a visão corrente.
- Depósito deve ser registrado **antes** de finalizar. Finalização exige
  `contributionsConfirmed:true`, também no comando antigo.
- Após finalizar, edição e novo depósito no mês são recusados; somente reabertura
  explícita permite correção. O teste acrescenta contraprovas dessa proteção.
- Evento é `FX_MONTH_FINALIZED`. Reconciliação fora de ordem explica o próximo
  mês; não depende da palavra exata do texto anterior.
- Auditoria completa da tabela exige abrir seu disclosure, em lugar de manter
  detalhes extensos sempre visíveis.

São mantidos os mesmos oráculos monetários, roundtrip/unknownfields, reservas,
isolamento entre domínios, quatro destinos locais, aliases, reload, ausência de
overflow e erro no navegador. Nenhuma fórmula, tolerância ou resultado financeiro
é enfraquecido. Focais novos acrescentam ausência, lifecycle, concorrência e
falhas físicas de persistência.

A fixture de `forex_v11_ledger_planning_test.py` permanece intacta. Seu erro
anterior, anterior à seção Planejamento, não é apagado nem convertido em PASS.

Complemento após o primeiro standard bruto (41 PASS / 5 PRODUCT_FAIL):

- `navigation_ia_test.py`: somente o destino inicial canônico do Planejamento
  passa a Tabela mensal; contratos de aliases, grupos e contexto permanecem.
- `dashboard_macro_test.py` e `usd_brl_quote_test.py`: fixtures de fechamento
  conferem explicitamente depósitos. A correção da taxa de um mês fechado
  reabre o mês com motivo antes de refinalizar. Valores esperados, câmbio,
  custo médio e ausência de reprecificação histórica não mudam.
- `forex_persistence_contract_test.py`: fechamento válido declara a conferência;
  a fixture que testa falhas físicas de edição começa reaberta. A falha de
  gravação continua conservando rascunho e versão anterior. Mantidos os mesmos
  oráculos de dados, concorrência, backup, bloqueio e resultado desconhecido.

Os resultados anteriores destas suítes permanecem nas evidências externas.
Nenhum teste é retirado do gate, nenhuma classificação ou tolerância financeira
é alterada. A atualização mecânica dos hashes no manifesto precede a execução
dos geradores oficiais, sem modificar lista, ordem ou esquema.
