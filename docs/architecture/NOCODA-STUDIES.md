# Estudos NoCoda — contrato de implementação

Memória técnica do canal de Fibonacci do método NoCoda, por instrumento. É o
workspace `Research → Forex → NoCoda`, não um scanner, gerador de sinais, ferramenta
preditiva ou mecanismo de execução.

**Informação técnica não é autorização operacional.** Nenhum valor derivado
aqui autoriza trade, libera execução, muda clearance, altera risco, gera ordem
ou recomenda exposição. Nenhuma função do domínio ou da interface escreve em
fase, ordem, LIFO, quarentena, alavancagem ou parâmetro estatutário.

## Separação de responsabilidades

| Camada | Arquivo | Responsabilidade |
|---|---|---|
| Catálogo | `src/js/10-domain/01-risk-instruments.js` | define quais instrumentos existem |
| Geometria | `src/js/10-domain/09-nocoda-geometry.js` | deriva range e subdivisão — puro |
| Estado | `src/js/00-core/03-default-state.js` + `04-persistence.js` | guarda as âncoras |
| Interface | `src/js/20-ui/14-nocoda-studies.js` | apresenta e coleta |
| Navegação | `src/js/40-app/11-operational-shell.js` + `20-ui/23-research-views.js` | encaminha |

Essas responsabilidades não se contaminam. A geometria não conhece DOM, `S`,
`localStorage` nem rede; a interface não contém fórmula.

## Identidade do instrumento

Não existe campo `id` no catálogo — a identidade sempre foi o `name`
normalizado. `instrumentId(name)` (`10-domain/01-risk-instruments.js`) dá nome
a essa regra e é a **fonte única**: `instFor()` a usa, `instrumentCatalog()` a
expõe e os estudos são chaveados por ela. A mesma identidade que as ordens já
usam em `o.par`.

`instrumentCatalog()` devolve a lista **operável** derivada de `S.instruments`
— nunca uma cópia persistida. `{all:true}` inclui os banidos. Não há símbolo de
instrumento escrito em nenhum arquivo do NoCoda, e o teste falha se aparecer.

## Modelo persistido

```js
S.nocoda = { schemaVersion: 1, studies: { [instrumentId]: NocodaStudy } }
```

```js
NocodaStudy = {
  anchor1: { datetime, price },   // linha 0, ponto 1
  anchor2: { datetime, price },   // linha 0, ponto 2
  anchor3: { datetime, price },   // linha -1
  updatedAt                        // ISO
}
```

Um estudo vigente por instrumento; o MVP não versiona histórico.

**Armazene causas, derive consequências.** Nada de `basePriceAtThirdAnchor`,
`signedRange`, `channelRange`, `subdivisionRange` ou dos 65 níveis é
persistido: seriam uma segunda fonte de verdade capaz de divergir das âncoras.
Estado visual — submenu aberto, fixado, hover, foco, instrumento em foco,
rascunho não salvo — é efêmero e nunca entra em `S`.

**Estudo de instrumento removido é preservado.** Mudança de configuração
operacional não destrói memória técnica; não há coleta destrutiva. O
instrumento some do seletor, o estudo permanece gravado.

Guarda estrutural: `nocodaNormalizeState()` em `04-persistence.js`, chamada em
`migrate()`. Vive ali, e não no módulo da feature, porque `migrate()` roda
dentro de `load()` antes de qualquer script tardio existir. Ela descarta apenas
forma errada e **preserva campos desconhecidos** dentro de cada estudo
(`STATE-SCHEMA.md` §3); chave fora da forma canônica é realocada, não apagada.
Não valida a matemática — um estudo incoerente simplesmente não produz
geometria, e apagá-lo destruiria entrada do operador em silêncio no caminho que
também atende backup importado.

## Geometria

As âncoras 1 e 2 definem a linha de nível 0; a âncora 3 pertence à paralela de
nível −1.

```text
P0(t)     = P1 + (P2 − P1) · (t − T1) / (T2 − T1)
P0AtT3    = P0(T3)
signed    = P3 − P0AtT3
range     = |signed|
subdivisão = range / 8
P(L, t)   = P0(t) − L · signed
```

O range é medido **na mesma coordenada temporal**, projetando a linha 0 até T3.
`abs(P3−P1)` e `abs(P3−P2)` são incorretos porque ignoram a inclinação — há
teste que falha se o resultado coincidir com qualquer um dos dois.

Escala do método: −4 a +4, passo 0,125 — 64 intervalos, 65 níveis. Entre −1 e 0
são 8 intervalos e 9 níveis. Os níveis vêm de índice inteiro
(`levelAt(k) = −4 + k/8`, k = 0..64) e nunca de acumulação `x += 0.125`, que
soma erro binário a cada volta.

## Tempo

Os carimbos vêm do MetaTrader e são **sem fuso**. Os componentes são
interpretados como UTC (`Date.UTC`) — não para converter fuso, mas para tornar
a aritmética determinística: lidos como hora local, duas âncoras em lados
opostos de uma virada de horário de verão dariam ranges diferentes em máquinas
diferentes. Nenhuma conversão ocorre e a interface exibe o que foi digitado.

Formato aceito: `AAAA-MM-DDTHH:MM:SS`, com segundos opcionais na entrada. O
campo é `datetime-local` com `step="1"`; quando os segundos são zero o próprio
navegador normaliza para `HH:MM`, o que não perde informação. Segundos não
nulos são preservados e influenciam o resultado.

## Validação

`nocodaValidateAnchors()` devolve erros **por campo**, e a interface os associa
ao input (`aria-invalid` + parágrafo `role="alert"` referenciado por
`aria-describedby`), além do resumo em bloco. Reprova: data inválida ou
inexistente, preço não numérico, não finito, zero ou negativo, e `T1 == T2`
(inclinação indefinida). **Não** impõe `T1 < T3 < T2`: interpolação e
extrapolação são ambas legítimas.

## Precisão

Cálculo em precisão plena, sem arredondamento intermediário. O catálogo não tem
metadado de dígitos por instrumento — não se criou uma segunda tabela de
precisão só para o NoCoda; a apresentação usa formatter neutro de até 8 casas
com zeros à direita removidos. A implementação nunca depende do texto formatado.

## Fora do MVP

Pips, pontos, porcentagem, ATR, VRM, equivalência monetária, risco, lote,
stop, take-profit, sinais, scanner, backtest, previsão, integração MT5,
importação automática de âncoras, histórico versionado, comparação entre
estudos e desenho das 65 linhas. `levelPrice()` existe para manter o motor
coerente e testável quando o desenho for implementado.

## Verificação mínima

`tools/nocoda_test.py`, no tier `standard`. Cobre: fixture canônica da
especificação; rejeição explícita das duas fórmulas ingênuas; invariantes
`P0(T1)=P1`, `P0(T2)=P2`, `P(−1,T3)=P3`; canal horizontal; âncora 3 sobre a
linha 0; interpolação e extrapolação nos dois sentidos; sinal do range; seis
casos de validação com caso de controle válido; `NaN`/`Infinity`; escala de 65
níveis sem deriva; contagem 8 intervalos / 9 níveis; identidade de instrumento;
ausência de símbolo hardcoded; seletor derivado do catálogo; instrumento novo
aparecendo sem editar a feature; cálculo ao vivo sem persistir; salvar,
recarregar e recalcular; preservação de segundos; `updatedAt`; isolamento entre
instrumentos; ciclo de backup; ausência de mutação operacional; preservação do
estudo após remoção do instrumento; e três formas de estado antigo ou malformado.
