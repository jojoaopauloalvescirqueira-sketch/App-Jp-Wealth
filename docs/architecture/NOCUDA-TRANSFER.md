# Nocuda Tool — transferência de desenhos v1

Contrato de produto N2 autorizado em 2026-09-17; base `f1d383f`.
Este formato descreve um desenho manual. Não registra operação, não gera sinal,
não modifica `S`, estudos NoCoda, parâmetros, backup ou dados financeiros.
A implementação pura é `src/js/10-domain/16-nocuda-transfer.js`; as ferramentas
Pine/MT5 e a página Ferramentas e Serviços são consumidores independentes.

## Envelope e validação

Uma linha ASCII sem espaços, quebra de linha, BOM ou caracteres de controle;
máximo **16384 bytes**. Cabeçalho `NOCUDA`; pares `chave=valor` separados por `|`.
Todos os 26 campos são obrigatórios. Campo desconhecido, repetido, vazio,
versão/geometria/escala incompatível ou campo incompleto impede importação.
Entradas podem ordenar os campos livremente; a exportação usa a ordem abaixo.
Não há HTML, URL acionável, expressão, JSON aninhado ou instrução executável.

| Campo | Conteúdo e limites |
|---|---|
| `v`, `geom` | Literais `1`, `bars1` |
| `id` | Identificador estável do desenho; 1–64 caracteres ASCII `[A-Za-z0-9._:/+-]` |
| `src` | `TV`, `MT5` ou `JPW` |
| `symbol`, `feed` | Mesma gramática de `id`; `UNKNOWN` é valor explícito permitido para feed desconhecido |
| `tf` | Período em segundos, inteiro 1–2592000; não converte gráficos não temporais |
| `scale` | `L`, escala linear; logarítmica é incompatível nesta versão |
| `a`, `b`, `c` | `UTC_MS,PRICE,OFFSET_MIN`; timestamp inteiro entre 0 e 4102444800000 inclusive; preço decimal com módulo ≤1e12; offset original inteiro −840…840 minutos |
| `d` | Largura **assinada**, decimal com `1e-12 < abs(d) ≤ 1e12` |
| `ab`, `ac` | Índice cronológico B−A e C−A, inteiros −4999…4999; `ab` não pode ser zero |
| `step` | Literal `0.125` |
| `before`, `after` | Quantidade de linhas antes da linha 1/depois da linha 17; inteiros 0–160 |
| `ext` | Extensão `R` direita, `L` esquerda, `B` ambas ou `N` nenhuma |
| `s1`, `s3`, `s5`, `s9`, `s17`, `si`, `sx` | Sete grupos de aparência, na ordem desta lista |
| `labels` | Aparência e opções dos rótulos |

Gramática decimal: `-?(0|[1-9][0-9]*)(\.[0-9]+)?`. Inteiros usam a mesma
gramática sem ponto/fracionário. Expoentes, sinal `+`, vírgula decimal,
zeros iniciais como `01` e números não finitos são recusados.
Preços de A/B/C e largura são conservados **como strings decimais**, incluindo
zeros finais; nenhuma cotação é arredondada na transferência. `offset` documenta
o relógio de origem: `UTC = horário de origem − offset`. Como o timestamp já é
UTC, o importador **não subtrai novamente** o offset. Cada âncora pode ter offset
diferente, inclusive em mudança de horário de verão.

### Aparência

Um grupo de linhas contém `ON,R,G,B,ALPHA,WIDTH,STYLE`:
`ON` é 0/1; RGB são inteiros 0–255; ALPHA é **transparência** percentual inteira
0–100 (0 opaco, 100 invisível); WIDTH é inteiro 1–5; STYLE é `S` contínuo,
`D` tracejado ou `P` pontilhado. Marcos 1/3/5/9/17 usam seu grupo próprio;
demais ordinais internos usam `si`; ordinais externos ao intervalo 1…17 usam `sx`.

`labels=MODE,SIZE,R,G,B,ALPHA,POS,VERT,GAP_PERCENT,OFFSET_BARS,SHOW_LEVEL,SHOW_PRICE,SHOW_MAX,USE_LINE_COLOR`

- MODE: `M` marcos, `A` todas ou `N` nenhuma; SIZE: inteiro 8–24.
- RGB/ALPHA têm os limites acima. POS: `L` início, `C` centro, `R` fim,
  `T` último candle; VERT: `U` acima, `O` sobre, `D` abaixo.
- GAP_PERCENT: decimal 0–50, afastamento vertical como percentual de `abs(d)`.
  OFFSET_BARS: inteiro −100…100, deslocamento horizontal em candles.
- As quatro opções finais são 0/1. SHOW_MAX identifica a linha 41 como MAX
  se estiver desenhada; não cria uma linha adicional. MODE `N` vence SHOW_MAX.
- `ON=0` no grupo também oculta seus rótulos. Transparência da linha e do rótulo
  são independentes; `USE_LINE_COLOR=1` herda somente RGB, mantendo ALPHA do
  rótulo. Nenhuma opção de aparência modifica âncoras ou largura. Cada plataforma deve declarar limites
  de renderização e conservar a aparência solicitada no transporte.

## Geometria bars1

**A e B pertencem à linha 17, nível 1; C pertence à linha 9, nível 0.**
O eixo horizontal é a sequência de candles, não milissegundos decorridos:

```text
xA = 0; xB = ab; xC = ac
m = (pB - pA) / ab
base17(x) = pA + m*x
d = base17(ac) - pC
nível(n) = (n - 9) / 8
preço(n,x) = base17(x) + (nível(n) - 1)*d
```

Assim, n=1/3/5/9/17 corresponde a −1/−0,75/−0,5/0/1.
Cada intervalo vale `d/8`, com sinal. Inclinação e sentido podem ser invertidos.
A validação confere a largura com tolerância `max(1e-10, abs(d)*1e-8)` e exige:

```text
sign(tB - tA) = sign(ab)
sign(tC - tA) = sign(ac)
sign(tC - tB) = sign(ac - ab)
```

Datas coincidentes exigem o mesmo candle. Não inferir `ab/ac` dividindo datas
pelo período: sessões, fins de semana e candles ausentes alteram a sequência.
O parser não possui histórico de mercado; conferir sintaxe/geometria não prova
que os candles existem na plataforma de destino.

Projeções padrão: `before=8`, `after=24`, ordinais −7…41 (49 linhas), último
nível 4. Limite total: 337 linhas. A numeração negativa é projeção da mesma malha,
não nova contagem de marcos. `before=after=0` mantém as 17 linhas de 1 a 17.

## Compatibilidade no destino

Antes de desenhar, a ferramenta de destino deve verificar símbolo/período,
escala linear, três candles de tempo **exato** e distâncias `ab/ac` iguais.
Não aproximar ao candle vizinho, corrigir largura, retirar sufixo de ativo ou
ajustar fuso/âncoras silenciosamente. Mapeamento entre identificadores de ativos
exige ação explícita. Feed diferente ou desconhecido exige revisão explícita;
reconhecê-lo não garante cotações/sessões idênticas. Sem histórico compatível,
recusar o novo desenho e preservar o anterior.

O JP Wealth apenas valida e apresenta os parâmetros/uma prévia geométrica.
Não tem candles de destino para certificar equivalência. A ida e volta textual
testada isoladamente não comprova compilação nem interação no TradingView/MT5.

## API JavaScript

Script clássico global `window.JPWNocudaTransfer`, ou `globalThis` em Node.
Sem DOM, storage, rede, dependências externas nem efeitos em `S`.

```js
const result = JPWNocudaTransfer.parse(text);
// {ok:true, value, canonical} ou {ok:false, error:{code,message,field}}
const textAgain = JPWNocudaTransfer.serialize(result.value);
// Lança Error com code/field se o objeto estiver incompleto ou inválido.
const exampleText = JPWNocudaTransfer.example(); // desenho inteiramente sintético
const preview = JPWNocudaTransfer.geometry(result.value);
```

`value` tem os campos de wire no mesmo nome; `v/tf/ab/ac/before/after` são
números, `d/step` são strings. `a/b/c` são `{time, price, offset}`, com price
string; `styles` agrupa `s1/s3/s5/s9/s17/si/sx`, cada qual
`{on,r,g,b,alpha,width,style}`. `labels` é
`{mode,size,r,g,b,alpha,pos,vert,gapPercent,offsetBars,showLevel,showPrice,showMax,useLineColor}`.
Flags são inteiros 0/1. Campos desconhecidos/ausentes também são recusados pelo
serializador. A função não modifica o objeto recebido.

`geometry` retorna `{slope,width,minOrdinal,maxOrdinal,minBar,maxBar,anchors,lines}`.
Cada âncora da prévia é `{bar,price}`; cada linha é
`{ordinal,level,group,visible,style,label,fromPrice,toPrice,atC}`.
`fromPrice/toPrice` usam min/max dos offsets das três âncoras. `label` contém só
o identificador base (ordinal/MAX), deixando preço/nível/posição ao renderizador.
Essa aritmética `Number` serve à visualização; os tokens de preço originais
continuam preservados para exportação. Erros não contêm o payload importado.

Fixture independente: `tools/fixtures/nocuda/synthetic-v1.txt`.
Teste focal: `node tools/nocuda_transfer_test.js`. Backup/recovery desta área é
o código textual exportado pelo usuário; o JP Wealth não o salva implicitamente.
