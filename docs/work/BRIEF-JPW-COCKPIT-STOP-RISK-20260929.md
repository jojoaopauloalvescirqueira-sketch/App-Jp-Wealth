# Brief — JPW Cockpit 1.9.0, risco dos stops

## Identidade e fronteira

- Proprietário / data: JP Wealth, 2026-09-29. Pedido explícito `PLEASE IMPLEMENT THIS PLAN` para a v1.9.0.
- Objetivo: sexta métrica informativa no gráfico e tabela auditável de posições/pedidos pendentes da operação no cockpit; atualizar guia local para IAs em CHG separado.
- Raiz/branch: `/private/tmp/jpw-alavancagem-atual-20260926`, `codex/jpw-alavancagem-atual-20260926`; HEAD/base `f5145b25e86af6b4ccbfef847cba0d84d74e7c8a`.
- Trabalho preexistente: r14 local não commitado, 42 entradas no `git status`, 83/83 arquivos conferidos com o snapshot final r14; fingerprint `37c3da2485d100601039dfd36a364c1c28dbf0e2212ac6878538201a7b0dd977`. Nenhuma limpeza, reset ou mudança de branch.
- Risco e autoridade: N3/A4 financeiro para produto, N3/A4 control plane para guia. Autorização cobre implementação e validação local, sem commit/push/merge/publicação/instalação operacional.
- CHGs: `CHG-JPW-COCKPIT-STOP-RISK-20260929` e `CHG-JPW-COCKPIT-STOP-RISK-AI-GUIDE-20260929`. Produto congelado antes do guia.
- Arquivos: MQL5 local, página, README, manifesto, geradores/derivados oficiais e focais pertinentes; guia AGENTS.md local só no segundo CHG. Estatuto, Anexo, Harness externo, root AGENTS e dados de conta real intocados.

## Síntese de compreensão

1. **Finalidade.** JP Wealth preserva capital e registra risco com integridade; a nova métrica dá observabilidade ao risco aberto sem autorizar novas Defesas nem certificar conformidade V11. Fontes: `README.md`, `docs/governance/PROJECT-CONTEXT.md`, Estatuto V11.
2. **Responsabilidade.** O EA observador calcula perdas hipotéticas com `OrderCalcProfit` em moeda da conta e publica snapshot completo. O indicador lê, valida e apresenta a amostra; o site apenas orienta instalação e interpretação, sem dados de conta. Fontes: código r14 de EA/indicador, MetaQuotes `OrderCalcProfit` e `DatabaseOpen`.
3. **Antes/depois.** R14: cinco métricas e cockpit sem tabela de stops. R15 proposto: sexta linha, abas com Stops, linhas detalhadas e estados de indisponibilidade honestos. Full r14 `49 PASS / 8 PRODUCT_FAIL`, nativo `NOT_RUN`, sem herança de aprovação.
4. **Impacto.** Exige balance, moeda, modo hedging/netting, posições, pedidos pendentes e SL vigente; mudança de composição/conta invalida o snapshot. Entram preferência visual v2, SQLite exclusivo da métrica e novos arquivos no pacote. MDD/Gênese/USC/Raiz N, inclusive registros, ficam independentes.
5. **Limites.** Art. 8.4 §§1º–2º define preço de execução→SL × volume remanescente, não preço de mercado→SL; piso zero no SL protetor. Percentual sobre saldo atual é informativo, não o limite do Saldo Inicial de Referência. Operação requer tese/ativo/direção; terminal não certifica tese/flag Gênese. Sem SL, tipo não suportado ou composição instável gera N/A, não zero. Netting não permite decomposição auditável por ordem. P-07/P-19 seguem pendentes.
6. **Evidência.** Focais sintéticos de matemática/identidade/persistência/UX, ZIP/manifesto/site e full bruto no candidate final; auditorias independentes de produto e guia. MetaEditor/MT5 isolado somente se utilizável, em recibos vinculados aos bytes exatos; caso contrário `NOT_RUN`. Aceite humano posterior.

| Fonte | Revisão/hash e trecho | Papel e acesso | Fato sustentado |
| --- | --- | --- | --- |
| `docs/normative/Estatuto_JP_WEALTH_UNIFICADO.pdf` | SHA-256 `2dab6166bb8513cd9beb7fe39c574971af086ebae66683d99c0e6fac69eb6769`; Arts. 4.2–4.3, 8.4 §§1º–2º, 9º, 15–17 | Norma local, lida por extração PDF em 2026-09-29 | Identidade da operação, Gênese, risco e pendentes |
| `docs/normative/ANEXO_PARAMETRICO_CANONICO.md` | SHA-256 `6240b6330a35fd488f16d4191129eeb01aff8f7a4707158c043afb37d91cdc23`; D-01, D-08, P-07/P-19 | Norma subordinada, leitura local | Unidades e parâmetros ainda pendentes |
| Harness externo atual | SHA-256 `b5680c22e44cf3f4a5cd3aa5deeb96f8b65c7908f14543e8c5d7f0c2f4e17b95`; §§12–19, 28–30 | Control plane externo, lido localmente | CHG, freeze, auditoria e limites de autoridade |
| `final-r14/CANDIDATE.json` | Fingerprint `37c3da2485d100601039dfd36a364c1c28dbf0e2212ac6878538201a7b0dd977` | Evidência de baseline, 83/83 hashes conferidos | Fonte de reversão, sem aprovação nova |

## Contrato e validação

- Menor delta: núcleo/adapter/SQLite novo para risco, sem alterar contratos dos quatro registros anteriores; EA calcula, indicador apenas consome.
- Hedge por posição com `max(0,-OrderCalcProfit(...))`; reservas pendentes atribuíveis somadas, sem exclusividade inferida; total não arredondado dividido por balance positivo. Mesmo valor/moeda da conta, inclusive USC, sem conversão unilateral.
- Uma posição/pedido falho invalida o total. Zero exige universo completo e vazio. Amostra SQLite com versão, conta opaca, geração, composição, checksum e idade; indicador valida antes de exibir. EA ausente/atrasado = `N/A` no gráfico; último snapshot somente no menu.
- Preferência antiga de cinco bits preservada; sexto visível por padrão exceto quando todos os cinco estavam ocultos. Preferência visual nunca altera cálculo/persistência financeira.
- Dados sintéticos apenas. Nenhuma chamada de negociação ou leitura de conta real pelo agente. Nenhum `.ex5` sem compilação exata em ambiente isolado.
- Reversão: restaurar bytes r14 do produto, não remover registros existentes; SQLite novo é separado e não toca MDD/Gênese/USC/Raiz N. Guia revogado separadamente para o freeze de produto.
