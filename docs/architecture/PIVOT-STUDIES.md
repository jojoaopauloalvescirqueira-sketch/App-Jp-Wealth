# Estudos dos Pivots — contrato de implementação

Memória empírica dos maiores pivots H1/H4 que o operador identificou no
gráfico, por instrumento e por período histórico. É o workspace
`Research → Forex → Pivots`, não um detector automático, scanner, gerador de sinais, ferramenta
preditiva ou mecanismo de execução.

**Informação técnica não é autorização operacional.** Nenhum valor derivado
aqui autoriza trade, libera execução, muda clearance, altera risco, gera ordem
ou recomenda exposição. Nenhuma função do domínio ou da interface escreve em
fase, ordem, LIFO, quarentena, alavancagem ou parâmetro estatutário.

**O operador identifica os pivots. O JP Wealth estrutura, calcula, compara,
organiza e preserva.** O software não detecta pivots e não possui dados OHLC.

## Separação de responsabilidades

| Camada | Arquivo | Responsabilidade |
|---|---|---|
| Catálogo | `src/js/10-domain/01-risk-instruments.js` | define quais instrumentos existem |
| Núcleo | `src/js/10-domain/10-pivot-studies.js` | deriva, valida, resume e ordena — puro |
| Estado | `src/js/00-core/03-default-state.js` + `04-persistence.js` | guarda os registros |
| Interface | `src/js/20-ui/15-pivot-studies.js` | apresenta e coleta |
| Navegação | `src/js/40-app/11-operational-shell.js` + `20-ui/23-research-views.js` | encaminha |

Essas responsabilidades não se contaminam. O núcleo não conhece DOM, `S`,
`localStorage` nem rede; a interface não contém fórmula.

## Identidade do instrumento

Mesma do resto do app: `instrumentId(name)` em
`10-domain/01-risk-instruments.js` — a identidade que as ordens usam em `o.par`
e que os Estudos NoCoda usam como chave. `instrumentCatalog()` devolve a lista
operável derivada de `S.instruments`, nunca uma cópia persistida.

Não há símbolo de instrumento escrito em nenhum arquivo da feature, e o teste
falha se aparecer. O Motor de Lote **não** é a fonte: ele é outro consumidor da
mesma fonte, e por isso migrá-lo de tela não afeta esta.

O seletor oferece o catálogo operável **mais** os instrumentos que já possuem
estudo. É o que sustenta a preservação descrita abaixo — instrumento retirado
do Motor de Lote sai da operação sem tornar sua memória técnica inalcançável.

## Modelo persistido

```js
S.pivotStudies = { schemaVersion: 1, studies: [ PivotStudy ] }
```

```js
PivotStudy = {
  id, instrumentId, periodStart, periodEnd,   // AAAA-MM-DD
  createdAt, updatedAt,                        // ISO
  pivots: [ Pivot ]
}

Pivot = {
  id, timeframe,                               // H1 | H4
  startDatetime, startPrice,
  endDatetime, endPrice,
  maxCorrectionPct, notes,
  createdAt, updatedAt
}
```

**Lista, e não mapa por instrumento como o NoCoda.** A natureza aqui é
histórica: o mesmo instrumento pode ter vários estudos de períodos distintos, e
nenhum sobrescreve o outro. Períodos sobrepostos **avisam e não proíbem** —
metodologias e revisões diferentes sobre a mesma janela são legítimas, e a
decisão é do operador.

Os pivots são **contidos** pelo estudo em vez de referenciarem um `studyId`. A
contenção é a relação, e por construção não existe pivot órfão.

**Armazene causas, derive consequências.** Direção, range absoluto, amplitude
percentual, duração, veredito do critério, ranking, `n`, máximo, média,
mediana, contagens e sínteses por timeframe **não** são persistidos: seriam uma
segunda fonte de verdade capaz de divergir dos registros. Estado visual —
instrumento e estudo em foco, filtros, ordenação, formulário aberto, rascunho
não salvo — é efêmero e nunca entra em `S`.

**Nada é apagado por classificação.** Estudo de instrumento removido é
preservado; pivot que passa a exceder o critério de correção é
**reclassificado**, não excluído; filtro, troca de timeframe, de instrumento ou
de período nunca removem registro. A única exclusão é a explícita, confirmada.

Guarda estrutural: `pivotStudiesNormalizeState()` em `04-persistence.js`,
chamada em `migrate()`. Vive ali, e não no módulo da feature, porque `migrate()`
roda dentro de `load()` antes de qualquer script tardio existir, e é também o
caminho por onde passa backup importado. Ela sanea apenas a **forma** e
**preserva campos desconhecidos** (`STATE-SCHEMA.md` §3): id ausente ou
duplicado é regerado, `instrumentId` é canonizado, `timeframe` sobe para
maiúsculas, `pivots` ausente vira lista. Não valida a matemática nem o critério
— registro incoerente simplesmente não produz derivados e fica fora da
estatística; apagá-lo destruiria entrada do operador em silêncio.

O agregado entra em backup, exportação e importação sem código adicional: a
exportação leva `S` inteiro e a importação passa por `migrate()`.

## Matemática

```text
direção      = endPrice > startPrice ? alta : (endPrice < startPrice ? baixa : inválido)
range        = |endPrice − startPrice|
amplitude    = |endPrice − startPrice| / startPrice × 100
duração      = endDatetime − startDatetime          (exige fim > início)
```

A amplitude percentual é a medida de magnitude que ordena e compara os pivots.
O denominador é o preço **inicial**: a mesma diferença de 10 vale 10% saindo de
100 e 5% saindo de 200, e há teste que falha se o denominador trocar.

Cálculo em precisão plena, sem arredondamento intermediário — quem arredonda é
a apresentação (2 casas para percentuais). O catálogo não tem metadado de
dígitos por instrumento; não se criou uma segunda tabela de precisão só para
esta tela, e preço usa formatter neutro de até 8 casas com zeros à direita
removidos.

## Critério de correção

```js
PIVOT_MAX_CORRECTION_PCT = 61.8     // 10-domain/10-pivot-studies.js
```

Declarado **uma única vez**; a interface lê a constante e não repete o número —
há teste que falha se ele reaparecer. Fonte normativa: a especificação do gestor
para esta feature, que fixa 61,8 como limite **invalidante**.

```text
maxCorrectionPct <  61,8  →  critério informado: atendido   (amostra principal)
maxCorrectionPct >= 61,8  →  critério informado: excedido   (fora da amostra)
```

**Critério informado, não verificado.** O app não possui OHLC: ele registra o
percentual que o operador identificou e o compara com o limite. Nenhuma tela
afirma ter conferido o histórico do gráfico — a linguagem é "critério
informado: atendido/excedido", nunca "validado pelo mercado".

A correção tem **domínio** `0 ≤ x ≤ 100`, verificado antes do critério: a
retração é fração da própria perna, e fora dessa faixa o número deixa de
descrever o movimento. 61,8 classifica entrada válida; 0–100 recusa entrada
impossível. Um registro com correção de exatamente 61,8 é **salvo** e
classificado fora, nunca recusado.

O domínio é verificado no **núcleo** (`pivotCorrectionInDomain`), e não apenas
no formulário, porque o formulário não é o único caminho de entrada: um backup
importado atravessa `pivotStudiesNormalizeState()`, que de propósito saneia só a
forma e não apaga registro do operador. Com a regra unilateral `< 61,8`, um
arquivo com correção negativa entraria na amostra **principal** classificado
como "atende ao critério" e envenenaria a mediana das correções. Agora um valor
fora do domínio fica fora da amostra principal, fora da mediana das correções, e
a tela o rotula como **"correção fora de 0–100% — registro preservado"** em vez
de chamá-lo de excedido. O registro continua gravado, visível e editável.

## O formulário pertence ao estudo selecionado

Invariante: trocar o instrumento, trocar o estudo ou criar um estudo **fecha** o
formulário de pivot, com ou sem alteração pendente. Havendo alteração, o
descarte é confirmado antes.

A razão não é estética. O formulário edita um pivot **daquele** estudo; se
sobrevivesse à troca, o alvo da edição passaria a não pertencer à seleção, o
`Salvar` não encontraria o registro e retornaria sem gravar e sem avisar — o
operador digitaria, clicaria e nada aconteceria. Como defesa adicional, salvar
um pivot cujo alvo desapareceu (excluído em outra aba, estado recarregado por
baixo) produz mensagem explícita, nunca retorno silencioso.

## Estatística

Descritiva da amostra, e somente isso. Métricas implementadas: `n` (total e por
timeframe), máximo global e por timeframe com a identidade do registro, média,
mediana, mediana da duração, mediana das correções informadas, distribuição por
direção, síntese comparativa H1 × H4 e TOP 3 por timeframe.

A mediana é a medida central principal por resistir a extremos; a média aparece
ao lado dela, nunca sozinha. `n` acompanha sempre as medidas centrais.

`n = 0` mostra **"Sem dados"**, jamais `0%` — zero é valor observado, ausência
de observação não é. Com `n = 1`, máximo, média e mediana coincidem, o que é
matematicamente correto e não recebe mensagem de confiança inventada.

O escopo da amostra é o mesmo do filtro de critério (`valid` | `all` |
`outside`), de modo que o `n` do resumo jamais descreva uma amostra diferente da
tabela ao lado.

**Viés de seleção declarado na tela.** O operador registra deliberadamente os
maiores pivots que encontrou; a amostra não representa a frequência natural de
pivots do instrumento. Por isso é proibido derivar daqui probabilidade,
frequência esperada, expectativa, distribuição populacional, alvo, pivot
provável ou movimento projetado — e há teste que varre o texto renderizado
atrás dessa linguagem.

## Ordenação e filtros

Ordenação por amplitude (↓ padrão e ↑), data, duração e correção, sempre
**numérica** — a fixture de teste inclui 2, 4, 5, 11 e 20 justamente porque a
ordenação lexicográfica poria 11 e 20 antes de 2. Filtros de timeframe, direção
e critério; o padrão da tela é "Somente válidos". Ordenar e filtrar não alteram
dado algum: são visualização.

## Tempo

Os carimbos vêm do MetaTrader e são **sem fuso**. O parser é o mesmo dos Estudos
NoCoda (`nocodaParseTime`), reusado em vez de duplicado: os dois recebem o mesmo
dado, e uma segunda implementação seria uma segunda verdade sobre ele. Os
componentes são lidos como UTC — não para converter fuso, mas para tornar a
aritmética determinística; lidos como hora local, duas pontas em lados opostos
de uma virada de horário de verão dariam durações diferentes em máquinas
diferentes. Nenhuma conversão ocorre e a interface exibe o que foi digitado.

Período do estudo é data sem hora (`AAAA-MM-DD`), com `periodStart <= periodEnd`
— período de um único dia é legítimo.

## Acessibilidade

Rótulos reais em todo campo; erros **por campo**, associados ao input com
`aria-invalid` e parágrafo `role="alert"` referenciado por `aria-describedby`,
mais o resumo em bloco. Filtros são botões com `aria-pressed` dentro de
`role="group"` rotulado. Tabela com `<caption>`, `<th scope>` e rótulo por
célula. Os atalhos do ranking são botões de verdade — foco e teclado — apenas
pintados como link.

Abaixo de 760px a tabela vira cards pelo `data-label` que o render já escreve:
sem markup duplicado e sem rolagem horizontal impraticável. Cores só por token,
para claro e escuro saírem juntos.

## Fora do MVP

Detecção automática de pivots, ZigZag, Pine Script, dados OHLC, API de mercado,
MetaTrader em tempo real, reconhecimento gráfico, classificação automática de
estruturas, previsão, probabilidade de próximo movimento, targets, stops,
geração BUY/SELL, backtest, correlação, regressão, machine learning, automação
de Fibonacci, alteração de risco ou de lote, e gráfico de amplitude — este
último porque não existe componente de gráfico reutilizável no app (o canvas
atual é sob medida para a curva de equity) e a especificação proíbe adicionar
biblioteca só para isso.

## Verificação mínima

`tools/pivot_studies_test.py`, no tier `standard`. Cobre: fixture canônica da
especificação; direção nos três casos; amplitude relativa ao início; preços
inválidos, `NaN` e `Infinity`; duração com datas iguais e fim anterior; os
quatro formatos de duração; o critério em 0, 61,79, 61,8 e acima; onze casos de
validação por campo com caso de controle válido; período invertido e data
inexistente; sobreposição de janelas; estatística com `n` = 0, 1, ímpar e par;
escopo do critério nos três modos; TOP por timeframe; mediana com ordenação
numérica; ordenação nos quatro critérios e dois sentidos; seletor derivado do
catálogo e instrumento novo aparecendo sem editar a feature; criar estudo,
registrar, editar em lugar e excluir; cálculo ao vivo sem persistir; ausência de
derivado persistido; reclassificação sem destruição; múltiplos estudos do mesmo
instrumento; isolamento entre instrumentos; reload; ciclo de backup; preservação
do estudo após remoção do instrumento; ausência de mutação operacional;
varredura de linguagem inferencial; três formas de estado antigo; e um estado
malformado que precisa ser saneado sem perder registro nem campo desconhecido.

A suíte é submetida a teste de mutação: dez defeitos plantados de propósito no
produto — critério inclusivo, mediana sem caso par, ordenação lexicográfica,
amplitude no denominador errado, duração aceitando instantes iguais, preço igual
virando baixa, derivado persistido, filtro que não filtra, critério unilateral
aceitando correção fora do domínio e formulário sobrevivendo à troca de estudo —
e todos os dez são acusados pela suíte.
