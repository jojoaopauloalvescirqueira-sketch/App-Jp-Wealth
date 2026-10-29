# Matriz de cálculos e preservação

Referência: primeira aba **Todas!A2:R329** do arquivo fornecido, SHA-256 `621a4e5bdefc467bede301b94e2c6f60aa05c78df3613cfac3908ef8d0c9084a`. Nenhum valor pessoal do arquivo foi importado. As equações abaixo são o contrato aprovado desta entrega, não uma política de operação ou promessa de resultado.

`T` é a meta anual; `D`, dias por semana; `M`, meses por ano; `Q = D × 52 × M / 12`; `f` é a fração das datas programadas elegíveis desde o início até dezembro sobre as datas programadas elegíveis do ano inteiro. São datas do calendário escolhido, não comprovação de trabalho realizado nem feriados oficiais presumidos.

| Propriedade | Resultado contratado | Oráculos permanentes |
|---|---|---|
| Datas civis e ano | Janeiro–dezembro; segunda a sexta; anos bissextos e exclusões explícitas | MGT-02,04,05,33,34 |
| Programação original | `Q`, inclusive quantidades fracionárias; distinta do número de datas da grade | MGT-03,06,31 |
| Meta diária e mensal | `(1+T)^(1/Q)−1` e `(1+T)^(1/M)−1` para o ano completo | MGT-06 |
| Início parcial | Meta `(1+T)^f−1`, programação `Qf`, meses `Mf`; raízes sobre essas grandezas, sem segundo redutor | MGT-07 |
| Cadeia projetada | Resultado sobre a abertura projetada; precisão mantida no cálculo, arredondamento na apresentação | MGT-06 |
| Ausência e zero | Vazio permanece pendente; zero exige registro; declaração sem resultado é outro estado | MGT-09,10,11; MANSTATE-07,11,12 |
| Fatos fora da programação | Continuam visíveis e entram no realizado; não acrescentam capitalização ou datas programadas | MGT-12,35 |
| Saldos observados | Preservados; divergência e lacuna ficam explícitas, sem recompor observações como soma teórica | MGT-13,14,15; MANSTATE-09,14 |
| Taxa realizada | Exige sequência devida completa, abertura conhecida e saldos reconciliados | MGT-09,13,14,16,22 |
| Extrapolação realizada | Base mensal `D × 4`; base anual de 240 dias, identificadas na interface | MGT-16 |
| Busca aproximada | Data da meta pela última curva acumulada menor ou igual ao alvo; equivalência pelas aberturas projetadas | MGT-23,25 |
| Termômetro | 13 verde;14 e29 amarelo;30 vermelho; avanço/atraso em texto; curvas inválidas indisponíveis | MGT-21,22,23,24 |
| Referência temporal | Ano atual usa data local; passado usa31/12; futuro não fabrica realizado ou pendência vencida | MGT-17,18 |
| Fechamento anual | Somente após o ano e pendências resolvidas; retratos imutáveis e nova revisão após correções | MGT-19,20,28; MANSTATE-13,14,16 |
| Fonte única do realizado | Comando canônico de ledger; sem coleção paralela; IDs/histórico e seleção operacional preservados | MANSTATE-02,07,09,16,25 |
| Consulta e confirmação | Consultas não gravam; token de outra sessão, revisão antiga, recusa e resultado indeterminado não autorizam repetição | MGT-29; MANSTATE-03,05,10,21,22,24,25,30,31,32 |

Os IDs MGT estão em `tools/management_annual_engine_test.js`; MANSTATE em `tools/management_annual_state_test.js`. A presença de um caso não comprova execução: os recibos do candidato e a classificação da suíte ficam no [relatório da entrega](README.md).

O termômetro negativo permanece verde conforme a referência deliberadamente preservada; a direção é mostrada separadamente. Isso não significa segurança ou autorização para operar. A grade pode ter quantidade diferente de `Q`; saldo desejado e saldo projetado de31/12 não são forçados a coincidir. A comparação nativa com Excel e o aceite visual humano permanecem separados.
