# Revisão estática — compatibilidade N1 de grupos e horário civil —29/10/2026

## Veredicto

AUDIT_PASS delimitado à legitimidade e ao escopo do delta de compatibilidade. A correção preserva marcadores existentes nos próprios elementos semânticos da tabela e restaura a frase anterior para evento de precisão civil. Não identifiquei manipulação para passar testes, remoção de proteção, nó fictício, duplicação de conteúdo ou desvio do plano de apresentação.

A geometria final não foi executada nesta revisão. Reexecução dos22 casos e verificação visual dos novos bytes continuam necessárias; recibos anteriores do JS1e2e/CSSf100 são históricos para essa versão. Nenhum browser, teste funcional ou edição de repositório pelo revisor.

## Evidência e delta conferido

Li COMPATIBILITY-DELTA.json, o recibo aplicado-calendar-agenda-37.json, edges() atual e comparei as cópias before-compat19.js/before-compat-app.css com os fontes atuais. Confirmei o primeiro FAIL em calendar-edges-320-light, linha259, na expectativa de grupos Economia/Sua agenda. Não atribuo execução à asserção posterior de horário, pois o primeiro assert interrompeu essa jornada.

O delta exato tem duas mudanças JS e duas CSS:

1. O caption já existente e visível 'Economia' recebe também calendar-agenda-group. Continua sendo caption real da tabela, não h4 duplicado nem elemento escondido só para seletor.
2. O td já existente da coluna Horário recebe também calendar-event-time. Para precision==='date' restaura 'Data · horário não informado', sem calcular instante nem presumir meia-noite. A conversão dos eventos com instante permanece igual.
3. A regra composta calendar-economic-caption.calendar-agenda-group zera margin, evitando que o marcador compartilhado imponha espaçamento do grupo legado. A regra posterior :first-child também zera somente margin-top, consistente com essa neutralização.
4. calendar-economic-time neutraliza max-width/flex/font-size/line-height herdados da classe antiga. Como o td permanece item da mesma grade, flex não altera seu layout; max-width:none mantém a largura da coluna e os valores inherit conservam a tipografia que recebia antes da classe adicional. A ordem CSS posterior às regras legadas/media mantém a neutralização no recorte econômico.

Não há alteração nas definições de colunas, limites úteis700/720, alinhamento numérico, controles44px, identidade, detalhe, estado, query/API/cache/draft, fontes ou alertas. O texto civil é mais longo e pode aumentar a altura da linha; o projeto permite altura automática. Isso demanda observação nos320/compacto, não indica sozinho regressão. Não afeta a tabela semanal, que não recebe esses nós/classes novos.

## Identidades conferidas

Antes:
- JS1e2e518bef9dccca48790f9752c48ba62619cd64c128ec87c55c6c58c779c831
- CSSf1007dfe4122ac80aa2e8260b4db91079ad5291cec5f1b2dd6ab0aa3910beb38

Depois:
- JS8cfaec067a59ba393ff2aa53ad097196460e64e6de111945d92d3da21c47a518
- CSS31e7659038d380c2348919a7ffa4229be125c5893d03540a89f728e3ad3aed5e

A checagem SHA dos cinco testes presentes no repositório confirma a identidade do pacote37: agenda65555606…, distribuição cbaf54be…, helper35ea10d5…, visualb883b966…, FFf66f3578…. V3FFa3f3… não está aplicado. quality_gate.py51fae2e0… e ui_visual_quality_test.py2dacc347… conservam os hashes lidos na preparação; não há mudança de juiz causada por este deltaN1.

Não revi artefatos gerados/distribuição enquanto o responsável reconstrói o produto. PASS deste parecer é de revisão estática do delta, não PASS22/22, FULL, visual413, nativo ou aceite humano.
