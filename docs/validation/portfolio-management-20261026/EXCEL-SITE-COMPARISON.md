# Comparação de referência — primeira aba Todas

Fonte: `Todas!A2:R329`, XLSX SHA256 `621a4e5bdefc467bede301b94e2c6f60aa05c78df3613cfac3908ef8d0c9084a`. Análise do arquivo e das fórmulas, com renderização local parcial de `A1:R30` via `artifact_tool`. Essa prévia apresentou diferenças de recálculo/cache e serve somente para examinar composição parcial, sem comprovar paridade numérica nativa ou a aba inteira. Não houve execução no Excel nativo nem importação dos valores pessoais. A imagem original permanece apenas no scratch, pois contém valores pessoais; as capturas da entrega são sintéticas. As outras duas abas não integram a implementação; o pacote fornecido não contém VBA.

| Função da primeira aba | Implementação | Diferença deliberada |
|---|---|---|
| Planejado verde e Realizado azul, lado a lado | Tabela anual com abertura, resultado, fechamento e acumulado | Em largura útil<900px usa três colunas e detalhes acessíveis |
| Metas diária e mensal | Raízes da meta composta sobre programação confirmada | Para início parcial aplica f uma vez à meta e às grandezas programadas |
| Programação de dias | dias/semana×52×meses/12 | Datas civis disponíveis são outra contagem; não afirmar que Q equivale às datas |
| Datas e subtotais semanais | Calendário janeiro–dezembro, segunda–sexta e exclusões explícitas | Corrige a inconsistência histórica de ano/dias da semana; não presume feriados de bolsa |
| Resultado diário manual | Célula monetária com prévia, revisão e confirmação | Vazio é pendente; zero só após registro explícito; correções/anulações auditadas |
| Saldo encadeado | Writer canônico da conta/período | Saldos observados existentes são preservados; divergências sinalizadas |
| Acumulado e extrapolações | Retorno acumulado; mensal dias/semana×4; anual240 | Incompletude impede taxas que exigem sequência completa |
| Data final e termômetro | Busca aproximada, avanço/atraso e limites13/14/29/30 | Curva inválida/sem equivalência mostra motivo, sem data inventada; cores não indicam autorização |
| Referências de dias da planilha | Detalhe expansível com anos, dias, meses e semanas | Referências descritivas não substituem calendário confirmado |
| Acréscimo aprovado do site: fechamento anual | Revisão explícita após 31/12 e pendências resolvidas | Não é função atribuída à aba original: o site acrescenta retratos versionados e reconferência após correções, sem fechar período ou ordens Forex |

## Exemplo exclusivamente sintético

Capital confirmado1000, meta anual25%,5dias/semana e12meses: Q=260; meta diária=(1,25)^(1/260)−1. Em2026, início01/10 tem66/261datas disponíveis: f=66/261, meta parcial=(1,25)^f−1 e Qparcial=260f. Aplicar a raiz sobre essas duas grandezas preserva a meta diária original; não aplicar f novamente.

A tabela pode conter mais ou menos datas do que Q. O saldo projetado de31/12 usa as datas efetivamente programadas, enquanto o saldo desejado usa a meta confirmada; eles não são forçados a coincidir. Datas fora da programação com fatos ou declarações ficam visíveis, sem alterar a programação. Esses exemplos e os testes não são dados do proprietário, resultados previstos ou política operacional.

## Aceite

Testes automáticos conferem fórmulas, limites e preservação; revisão independente confere evidências e integração. A semelhança percebida, clareza e facilidade de preenchimento ainda exigem teste e aceite do usuário.
