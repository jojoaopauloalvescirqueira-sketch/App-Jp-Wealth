# Matriz matemática — Hedge Prop Firm

Expectativas derivadas do plano aprovado e das duas capturas, sem depender da formatação da interface. Todos os valores são hipóteses em US$, não registros do usuário.

| Grandeza | Uma fase | Duas fases |
|---|---:|---:|
| Capital nominal por etapa | 200.000 | 200.000 |
| Taxa paga uma vez | 1.200 | 1.200 |
| Payout | 80% | 80% |
| Drawdown máximo fixo | 7% | 10% |
| Metas das avaliações | 10% | 10% / 5% |
| Reembolso assumido no exemplo | 1.200 | 1.200 |
| Razão avaliação 1 | 0,085714285714 | 0,06 |
| Perda pessoal ao passar avaliação 1 | 1.714,285714 | 1.200 |
| Razão avaliação 2 | não se aplica | 0,12 |
| Perda pessoal ao passar avaliação 2 | não se aplica | 1.200 |
| Despesa acumulada antes da financiada | 2.914,285714 | 3.600 |
| Razão financiada | 0,208163265306 | 0,18 |
| Meta financiada | 2.896,551724 | 3.870,967742 |
| Perda pessoal no alvo financiado | 602,955665 | 696,774194 |
| Reserva final com 100% adicional | 1.205,911330 | 1.393,548387 |
| Reservas totais | 2.920,197044 | 3.793,548387 |
| Orçamento incluindo a taxa | 4.120,197044 | 4.993,548387 |
| Orçamento / taxa | 3,433497537 | 4,161290323 |

Na amostra de uma fase, reembolso explicitamente zero eleva a meta financiada a 4.924,137931, sem alterar as razões. Taxa e reembolso zero produzem hedge/meta/reservas zero; o múltiplo fica indisponível.

## Custos por caminho: prova independente de duas fases

Custos aprovação/reprovação: avaliação1=20/10; avaliação2=30/15; financiada=40/20. Razões, metas, reservas e orçamento ideal ficam idênticos.

| Caminho encerrado | Despesas adicionais do caminho | Resultado após custos |
|---|---:|---:|
| Reprovar avaliação1 | 10 | -10 |
| Reprovar avaliação2 | 20+15=35 | -35 |
| Perder financiada | 20+30+20=70 | -70 |
| Atingir alvo e receber | 20+30+40=90 | -90 |
| Atingir alvo sem payout/reembolso | 90 | -4.386,774194 |

Somente esses custos adicionais são subtraídos. O resultado ideal já contém a taxa e, quando pertinente, o reembolso. Reservas não são despesas. Os desfechos são alternativos e não podem ser somados num custo agregado fictício.

## Limites da prova

Os zeros ideais são identidades condicionais construídas; não medem a trajetória, margem, execução, risco de liquidação, regras diárias/móveis ou direito ao recebimento. A referência visual não comprova o código interno da Cortex. Fontes contratuais e suas datas estão no contrato da ferramenta.
