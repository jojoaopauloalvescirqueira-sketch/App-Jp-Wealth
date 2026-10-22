# Inventário do delta

| Achado | Antes observado | Correção | Proteção |
|---|---|---|---|
| Stoikus |13ações sem grupos, wrapping, largura636px |5grupos verticais, ordem aprovada,320px/gutter12, scroll e teclado |regression-stoikus-vertical-groups e matriz |
| Previsão |Range do texto5px acima do centro |centralização local em ambos os eixos |regression-forecast-inner-center + contraprova de deslocamento |
| Fechar |caixa44×44 centrada, caractere tipográfico sem desenho mensurável |SVG simétrico nos3fechar, área44×44 e nome preservado |regression-close-svg-ink-center + contraprova no desenho |
| Primeiro candidato |CSS posterior recentralizava texto do menu; resize Window causava erro |prioridade local da opção e guarda de Node |medições internas e captura de pageerror em resize/lifecycle |
| Instruções |dois rótulos Source revision de fotografias distintas |hash18/10 preservado com rótulo histórico, primário20/10 mantido |teste estrutural explícito corrente +101negativas |

## Antes/depois

- [Menu antes](captures/before-regression-stoikus-vertical-groups.png) · [Menu móvel depois](captures/final-menu-320-light.png) · [Menu desktop depois](captures/final-menu-1440-dark.png).
- [Previsão antes](captures/before-regression-forecast-inner-center.png) · [Formulário móvel depois](captures/final-form-390-light.png) · [Formulário desktop depois](captures/final-form-1440-dark.png).

Capturas inspecionadas por agentes em dados sintéticos; não são teste humano. Mesmos motores, escritores e perguntas; nenhum critério financeiro alterado. Os recibos identificam os bytes e o recorte efetivamente executado.

Testecompatível com o novoSVG: o seletor de `dialog_checks` passa de todosSVGs aos cinco `svg.pl-native-chart`, com os mesmos limites. É a única adaptação de um arquivo de teste antigo;259outros permanecem byte-idênticos. Os95checks/comandos/oráculos financeiros continuam preservados. Contraprovas rejeitam gráfico real ausente/colapsado. A primeira falha e nova prova têm recibos próprios.
