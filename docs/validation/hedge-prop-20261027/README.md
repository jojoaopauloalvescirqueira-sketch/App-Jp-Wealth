# Mesas Proprietárias — Hedge Prop Firm

Implementado localmente em **Ferramentas e Serviços → Mesas Proprietárias → Hedge Prop Firm**, antes de MiniGames. Candidato `09cfa4f7b8a8dbed`, branch `codex/mesas-proprietarias-hedge-20261027`, HEAD `3e24f60f8cfe87f79335f40e95a0927379a9f834`.

## Prévia e funcionamento

[Prévia local versionada](http://127.0.0.1:51757/index.html?v=09cfa4f7b8a8dbed) · [Desktop claro — rodada 6](full6-desktop.png) · [Celular escuro — rodada 6](full6-mobile.png). O endereço depende do servidor local em execução; as capturas mostram o mesmo build do aplicativo.

- Uma ou duas fases, primeiro acesso vazio e exemplos somente por escolha. Rascunhos de cada modo permanecem em memória durante a sessão.
- Taxa, reservas e orçamento total separados; reembolso explícito e custos por caminho. Informação ausente não vira zero.
- Memória de cálculo, hipóteses, fontes datadas e lição do Dante sem prática automática.
- Sem acesso a contas ou escritores financeiros, persistência do simulador, automação de operações ou novas dependências.

## Cálculos e limites

Exemplos com reembolso integral **como hipótese didática**:

| Exemplo | Reservas | Orçamento com taxa | Meta financiada |
|---|---:|---:|---:|
| Uma fase | US$ 2.920,20 | US$ 4.120,20 | US$ 2.896,55 |
| Duas fases | US$ 3.793,55 | US$ 4.993,55 | US$ 3.870,97 |

[Fórmulas, fontes e condições](../../architecture/HEDGE-PROP-FIRM.md) · [Matriz independente de cálculos e custos](CALCULATIONS.md). A reconstrução segue as referências visuais aprovadas; não demonstra paridade com todo o código interno da Cortex. Razões de exposição não são lotes executáveis, reservas não são margem e o equilíbrio ideal não garante aprovação, recebimento ou permissão contratual. Fontes FTMO/TTP e datas de consulta permanecem visíveis.

## Resultado automatizado da tentativa 6

`quality_gate.py --tier full`: **116/116 PASS, saída 0 observada pelo supervisor**. Início `2026-10-28T10:21:39-03:00`; término `2026-10-28T11:15:24-03:00`. [Recibo integral](full-attempt6-116pass.json) · [Saída do supervisor](full6-exit.json) · [Integridade e preservação](FINAL-AUDIT.json) · [Supervisão da rodada](full6-supervision.json) · [Congelamento da rodada](freeze-attempt6.json).

Os resultados desta execução não declaram prontidão integral, aprovação universal ou encerramento dos incidentes anteriores. Nenhuma exceção foi aplicada às falhas históricas.

[Conferência HTTP da prévia](preview-identity-final6.json) · [Preservação das evidências desta rodada](full6-evidence/preservation.json) · [Ambiente e liberação da proteção temporária contra suspensão](full6-environment-triage/FINAL.md). A consulta delimitada dos registros não encontrou Sleep/Wake nem encerramento do Chrome nesta janela. O teste de downloads passou em320,058s; a causa dessa latência não foi identificada.

Os 1621 inputs congelados ficaram idênticos; os 86 caminhos protegidos permanecem iguais à referência. Nenhum dos 3310 arquivos de referência foi removido. Os 113 IDs anteriores foram preservados e três checks Hedge acrescentados. A entrega conserva o candidato e as alterações pendentes de Portfólio/Gerenciamento, Planejamento, calendário, bolsas e os três MiniGames.

Os recibos delimitam a cobertura de motor, interface, quatro layouts, temas, tamanhos, teclado e zoom nativo, além de HTTP, PWA offline, arquivo local e portátil. A matriz visual anterior de 413 casos foi preservada. Isso não é aprovação universal ou aceite humano. [Revisão independente do recibo final](INDEPENDENT-REVIEW-FULL6.md) · [Revisão anterior do produto e dos controles](INDEPENDENT-REVIEW.md) · [Catálogo do gate](gate-catalog-review.md) · [Expectativas legadas](legacy-review.md).

## Histórico e incidentes preservados

- Rodada 1 interrompida com catálogo anterior; evidência mantida.
- [Rodada 2](full-attempt2-114pass-2legacy-expectations.json): 114 PASS/2 PRODUCT_FAIL por expectativas antigas. Ajustes delimitados, contraprovas e revisão precederam a repetição.
- [Rodada 3 interrompida](full3-interruption.json): encerramento externo do Chrome confirmado pelo usuário; [diagnóstico](chrome-quit-README.md). Não convertida em aprovação.
- [Rodada 4](full-attempt4-113pass-3fail.json): **113 PASS/3 PRODUCT_FAIL, saída 1**, preservada. [Triagem original](TRIAGE-FULL4.md) · [Sleep/DarkWake observado nessa rodada](full4-environment-triage/README.md). Os registros ambientais não atribuem automaticamente causa a cada falha.
- [Rodada 5](full-attempt5-114pass-2fail.json): **114 PASS/1 PRODUCT_FAIL/1 TEST_HARNESS_FAIL**, preservada. Alladin falhou em goto/load no caso W6. Planning teve timeout de `Locator.click` em `#pl-native-stopOpen`, dentro de `geometry_journey`, caso `matrix-submenu-light-1099x720`, durante Sleep documentado. [Registros ambientais e limites](full5-environment-triage/README.md). [Focais posteriores com verificadores originais](full5-awake-focals/README.md) · [Recibo](full5-awake-focals/receipt.json) · [Conferência independente somente leitura](INDEPENDENT-REVIEW-FULL5.md). Esses focais passaram sem alteração das fontes ou critérios e sem reclassificar o FULL anterior.
- Research: causa demonstrada da leitura antes do callback de conclusão do shell. O [patch de três linhas](research-frame-PROPOSAL.patch) foi autorizado pelo usuário; [quatro controles e três contraprovas](research-frame-COUNTERPROOF-RESULT.json) e [revisão independente](research-frame-review.md) preservaram as exigências de rota e gaveta fechada. O aplicativo não mudou por essa correção do verificador.
- **Epoch e Alladin: causas históricas ainda abertas.** As repetições isoladas, os diagnósticos e a execução 6 com checks PASS não identificam a causa das falhas anteriores nem as encerram automaticamente. Nenhum patch de aplicativo ou juiz foi aplicado para essas duas ocorrências.

O teste suplementar `navigation_local_contract_test.py` conserva o comportamento herdado documentado no [inventário](INVENTORY.md); não foi usado como evidência de aprovação deste FULL.

## Aceite e preservação

**Aceite visual humano pendente.** Conferir clareza das etapas, taxa versus reservas versus orçamento, reembolso e custos. Toque físico, leitores de tela, Safari e aplicação operacional real não foram homologados por este gate.

Entrega local, **sem commit, merge, push ou publicação**. O delta não altera regras V11, dados reais, histórico financeiro ou formato de backup. Reversão deve limitar-se aos caminhos da tarefa e preservar o trabalho anterior; não usar reset/stash global.

[Inventário](INVENTORY.md) · [Impacto agêntico delimitado](AGENTIC-IMPACT.md). Nenhuma edição de skills, propagação global ou escrita de memória global integra esta entrega.
