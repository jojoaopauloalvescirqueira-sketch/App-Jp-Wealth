# Arquitetura do Laboratorio de Probabilidade - Galton Board

## Objetivo e fronteira

O Galton Board e um simulador educacional de fisica e probabilidade, acessado em
`Configuracoes > Laboratorio de Probabilidade > Galton Board`. Ele pertence a camada
de aplicacao e nao ao dominio financeiro. O laboratorio nao le nem escreve `S`,
`DEFAULTS`, contas, ordens, ledger, perfis, credenciais, APIs ou qualquer regra
normativa do JP Wealth.

O resultado mostra como uma distribuicao empirica pode emergir de colisoes reais em
uma placa de pinos. Ele **nao e um modelo de retorno de Forex, uma previsao de mercado
ou uma promessa de desempenho**.

## Dependencia e carregamento

O motor de corpos rigidos e Planck.js `1.5.0`, vendorizado em
`src/vendor/planck/planck-1.5.0.min.js`, sob licenca MIT. O diretorio da dependencia
registra a origem, a integridade publicada e o SHA-256 dos bytes locais. Nao ha CDN,
download em runtime, telemetria ou dependencia transitiva de runtime.

O script vendorizado e os modulos do laboratorio entram no fim de
`src/js/manifest.json`, sem reordenar os scripts classicos legados. O build portatil e
o service worker consomem a mesma lista; assim a versao instalada, a versao monolitica
e a versao offline executam os mesmos bytes.

## Modulos e namespace

Os arquivos em `src/js/40-app/18-galton-board/` permanecem scripts classicos e
publicam apenas o namespace global `window.JPWGalton`. Nao ha conversao incidental
para ES Modules, framework ou bundler.

| Modulo | Responsabilidade |
|---|---|
| `01-config.js` | Defaults, limites seguros, presets, normalizacao da configuracao e contrato de preferencias |
| `02-rng.js` | PRNG deterministico, derivacao da seed e amostras usadas somente na montagem/soltura |
| `03-statistics.js` | Histograma, momentos descritivos, binomial teorica e elegibilidade da comparacao |
| `04-physics.js` | Mundo Planck, geometria, filtros de colisao, fila, integracao fixa, assentamento e descarte de corpos |
| `05-renderer.js` | Canvas responsivo, transformacao mundo-tela, histograma, curva teorica, hover e estado visual |
| `06-controller.js` | DOM, comandos, persistencia, lifecycle, acessibilidade e coordenacao entre os demais modulos |

As fronteiras sao unidirecionais: configuracao/PRNG/estatistica nao dependem de DOM;
fisica nao conhece o modal de Configuracoes; renderer apenas projeta snapshots; e o
controller e o unico orquestrador da interface. A integracao em
`09-settings-modal.js` monta ou ativa o controller, mas nao implementa fisica nem
estatistica.

```text
DOM de Configuracoes -> controller -> fisica (Planck)
                           |             |
                           |             +-> snapshot agregado
                           +-> renderer <-+
                           +-> estatistica
                           +-> preferencias isoladas
```

## Modelo fisico

### Coordenadas, gravidade e geometria

O mundo usa unidades fisicas normalizadas, independentes de pixels, com eixo `y`
positivo para cima. Para magnitude `g` e inclinacao `theta`, em radianos, a gravidade
e:

```text
gx = g * sin(theta)
gy = -g * cos(theta)
```

`theta` e limitado a `-3` ate `+3` graus. Alterar a velocidade da simulacao nao altera
`g`; apenas muda quanto tempo fisico e acumulado por unidade de tempo de tela.

Para `rows = r`, a placa contem `r` linhas triangulares de pinos e `r + 1`
compartimentos. Na linha `i`, indexada a partir de zero, ha `i + 1` pinos. A posicao
horizontal de cada pino e centralizada pela propria linha:

```text
x(i, j) = centerX + (j - i / 2) * pegSpacing
y(i)    = topY - i * rowSpacing
```

Um chute superior estreito leva a bola ao primeiro pino. Guias laterais inclinadas
acompanham o envelope dos pinos externos e se conectam aos bins, impedindo que uma
bola contorne fisicamente a malha; elas sao contenção simetrica do tabuleiro, nao um
ajuste estatistico. Paredes, piso, divisorias, guias e pinos sao corpos estaticos.
Bolas sao circulos dinamicos.
Raio, densidade, restituicao e atrito sao validados contra limites seguros antes de
criar fixtures. A validacao tambem limita `releaseJitter * pegSpacing` a metade do
raio da bola, limita a tolerancia a um quarto do raio do pino e desconta deslocamentos
opostos dos pinos ao calcular o corredor fisico. Colisao bola-bola usa filtros de
categoria e fica desligada por padrao; quando desligada, bolas ainda colidem com
pinos, paredes, piso e divisorias.

### Aleatoriedade e determinismo

A seed alimenta um PRNG explicito. Seus unicos usos permitidos sao:

- jitter no ponto de soltura de cada bola;
- tolerancia geometrica fixa dos pinos, calculada na construcao da placa.

Nao existe sorteio de esquerda/direita, impulso aleatorio ou qualquer outra decisao
aleatoria durante a trajetoria. Depois de criada, a bola evolui somente pelas forcas,
colisoes e integracao do motor.

No caso singular `releaseJitter = 0`, pinos nominais, soltura central e gravidade
vertical, a posicao inicial recebe um microdesempate simetrico de `0,01%` do
espacamento, com sinal derivado da seed. Isso evita o equilibrio numerico perfeito
sobre o primeiro pino sem introduzir sorteio durante a trajetoria. Corpos dinamicos
permanecem acordados; os assentados sao removidos normalmente.

Mesma seed, configuracao, preset e sequencia de liberacao reproduzem o experimento no
mesmo motor e runtime. Nao se promete identidade bit a bit entre navegadores,
arquiteturas, versoes de JavaScript ou Planck: arredondamento de ponto flutuante e
ordem interna de contatos podem divergir.

### Passo fixo, fila e assentamento

A fisica avanca em passos fixos de `1/120 s`, separada de `requestAnimationFrame`:

```text
accumulator += elapsedReal * speed
while accumulator >= 1/120 and substeps < MAX_SUBSTEPS:
    spawnDueBalls()
    world.step(1/120)
    classifySettledBalls()
    accumulator -= 1/120
render(interpolation/snapshot)
```

O tempo de frame e limitado antes de entrar no acumulador e o numero de substeps por
frame tambem e limitado. Isso impede uma aba suspensa de tentar recuperar minutos de
fisica de uma vez. A fila de `+1`, `+10`, `+100` ou `+500` libera corpos em cadencia
controlada e respeita um teto de corpos ativos; velocidade `0.5x`, `1x`, `2x` e `4x`
nao muda os parametros fisicos.

No modo experimental de colisao bola-bola, o scheduler conserva a proxima amostra
de soltura e espera haver distancia de pelo menos dois raios no emissor antes de
criar o corpo. Isso evita que duas bolas nascam sobrepostas sem mover, impulsionar ou
escolher a trajetoria de nenhuma delas.

Uma bola so e contabilizada depois de permanecer no compartimento com velocidade
abaixo do limiar pelo intervalo de assentamento. A marcacao e idempotente: cada bola
incrementa exatamente um bin uma unica vez. A destruicao do corpo ocorre fora da
iteracao de contatos, depois do step. Histograma e estatisticas conservam apenas
contagens agregadas; corpos assentados nao se acumulam no mundo.

Uma protecao por idade e limites externos remove corpos excepcionalmente presos ou
fora da placa. Esses casos incrementam `expiredCount` e `expiredByReason`, nao entram
no histograma e aparecem em um aviso de integridade na interface; nunca sao
silenciosamente contabilizados como observacao valida.

## Estatistica e comparacao teorica

Os compartimentos sao indexados de `0` a `rows`. A partir das frequencias empiricas o
laboratorio calcula `N`, media, desvio-padrao populacional, moda e, quando numericamente
definidos, assimetria e curtose por momentos. Estados sem amostra ou com variancia
zero exibem ausencia explicita em vez de `NaN` ou infinito.

A referencia teorica e a binomial `Binomial(rows, 0.5)`, projetada sobre o mesmo `N`;
ela nunca e ajustada aos dados observados. A curva so e elegivel quando todas as
premissas visiveis continuam simetricas:

- ponto de soltura centralizado;
- inclinacao igual a zero;
- tolerancia dos pinos igual a zero e geometria centralizada;
- colisao bola-bola desligada.

Se qualquer condicao falhar, a interface oculta a curva e informa o motivo. As
mensagens de convergencia sao qualitativas e dependem do tamanho da amostra; nao
certificam normalidade nem transformam variacao amostral em erro do motor.

## Preferencias e isolamento de dados

A unica escrita persistente do laboratorio e:

```text
localStorage['jpwealth_galton_preferences_v1']
```

O contrato versionado e:

```json
{
  "schemaVersion": 1,
  "preset": "realistic",
  "showTheory": true,
  "speed": 1,
  "releasePoint": 0,
  "tiltDegrees": 0,
  "seed": 123456789,
  "config": {
    "rows": 10,
    "pegSpacing": 1,
    "rowSpacing": 0.82,
    "pegRadius": 0.09,
    "ballRadius": 0.14,
    "ballDensity": 1,
    "ballRestitution": 0.28,
    "ballFriction": 0.22,
    "gravity": 9.81,
    "releaseJitter": 0.07,
    "pegTolerance": 0,
    "ballCollisions": false
  }
}
```

Os numeros acima ilustram o formato; os defaults e limites executaveis vivem em
`01-config.js`, e `data/samples/galton-preferences-v1.json` e a fixture canonica de
compatibilidade. A leitura normaliza os campos conhecidos e preserva extensoes
desconhecidas na proxima gravacao, permitindo evolucao aditiva do envelope.

Fila, corpos, posicoes, acumulador, estado de pausa, histograma, `N`, estatisticas,
resultado de hover e experimento em andamento nunca sao persistidos. Reabrir ou
recarregar sempre apresenta uma placa vazia com as preferencias recuperadas.

JSON invalido, envelope que nao seja objeto, ausencia de `schemaVersion` inteiro,
schema diferente de `1`, `localStorage` indisponivel, quota excedida ou falha de
escrita causam fallback seguro apenas em memoria e aviso nao bloqueante. O payload
existente e preservado e novas gravacoes nessa chave ficam bloqueadas; somente a acao
explicita `Restaurar padroes` autoriza sua substituicao. Essas falhas nunca chamam
`save()`, nunca substituem `S`, nunca escrevem `LSKEY` e nunca limpam outras chaves.
Uma gravacao compativel e cercada por `try/catch`.

A chave integra `JP_WEALTH_AUX_STORAGE_KEYS`: `Finalizar Sessao`, inclusive o evento
recebido de outra aba, remove-a com os demais dados auxiliares. A limpeza operacional
com `removeAuxiliary:false` preserva preferencias de interface. Excluir manualmente a
chave restaura somente os defaults do laboratorio e e o rollback de dados; isso exige
autorizacao humana quando executado sobre um navegador real.

Cada controller captura `JP_WEALTH_SESSION_WIPE_EPOCH` na montagem. Uma finalizacao
local ou remota incrementa esse epoch, destroi a instancia antiga e remonta uma placa
vazia apenas se o painel ainda estiver visivel. Mesmo se o hook visual falhar, uma
instancia da geracao anterior fica impedida de recriar preferencias apagadas.

## Lifecycle e desempenho

O controller possui estados explicitos de montagem, execucao, pausa e descarte.

- entrar no painel monta ou retoma uma unica instancia;
- navegar para outro painel ou fechar Configuracoes pausa o loop e desconecta o
  `ResizeObserver`;
- `document.hidden` pausa a acumulacao de tempo e evita catch-up ao retornar;
- desmontar cancela `requestAnimationFrame`, remove listeners, desconecta observers e
  destroi o mundo;
- reset destroi corpos dinamicos, zera fila/agregados e reconstrui apenas quando a
  configuracao exige nova geometria.

Chamadas repetidas de abertura nao podem duplicar loops ou listeners. O teto de corpos
ativos, a liberacao em lotes, o limite de substeps e a remocao de corpos assentados
mantem memoria e custo por frame limitados. Um painel de diagnostico pode mostrar FPS,
steps, corpos, contatos e fila somente em desenvolvimento local; ele nao envia dados.

## Renderizacao, responsividade e acessibilidade

O Canvas desenha placa, bolas e histograma, mas nao e a unica representacao dos
resultados. O renderer converte unidades do mundo para pixels a cada resize e escala o
backing store pelo `devicePixelRatio`, mantendo o modelo fisico inalterado.

Controles, estatisticas, descricao do bin e tabela/resumo por compartimento sao DOM
semantico. Todo comando e alcançavel por teclado, tem nome acessivel, foco visivel e
estado de pausa/execucao anunciado. O detalhe oferecido por hover tambem e apresentado
por foco e em uma regiao textual. Cor nunca e o unico portador de informacao.

`prefers-reduced-motion: reduce` reduz interpolacoes e animacoes decorativas sem
alterar a simulacao ou seus resultados. O layout privilegia desktop, mas o modal e os
controles permanecem contidos e rolaveis em viewport movel. Os temas claro e escuro
usam tokens semanticos existentes. A secao "O que observar" e o aviso educacional
ficam visiveis junto ao experimento.

## PWA, seguranca e privacidade

Todos os scripts declarados no manifest, inclusive Planck e os modulos do laboratorio,
devem estar no precache. O validador compara manifest e service worker para impedir que
um novo modulo funcione online e falhe silenciosamente offline. A politica de ativacao
segura do worker continua a de `PWA-UPDATE-LIFECYCLE.md`.

A superficie nova e inteiramente local: sem `fetch`, WebSocket, analytics, credencial,
HTML remoto ou `eval`. Valores de formularios sao normalizados por allowlist e limites
antes de atingir geometria, Planck ou persistencia. Texto dinamico e escrito com APIs
seguras de DOM; nenhum dado importado e tratado como instrucao ou markup confiavel.

O laboratorio nao aumenta a autoridade de wipe, exportacao ou backup. Sua preferencia
isolada nao viaja dentro da base financeira nem altera seu schema.

## Verificacao

O candidato deve manter os gates existentes e acrescentar evidencias classificadas
para:

- unitarios: PRNG, limites/configuracao, geometria, estatisticas, binomial e
  elegibilidade teorica;
- smoke fisico: contato real, `rows + 1` bins, assentamento unico, descarte e
  reproducibilidade no mesmo runtime;
- persistencia: round-trip, reload vazio, extensoes desconhecidas, JSON corrompido,
  falha de leitura/escrita, isolamento de `S` e Finalizar Sessao;
- integracao: navegacao do modal, comandos, pausa/retomada/reset, lifecycle sem loop
  duplicado, teclado e alternativa ao Canvas;
- PWA: manifest, precache, build portatil e upgrade offline;
- navegador real: desktop, `390 x 844`, claro/escuro e reduced motion;
- desempenho: lote de 10.000 bolas sem crescimento ilimitado de corpos, com tempo,
  pico de corpos e contagem final registrados; distancia para a binomial e simetria
  sao diagnosticos qualitativos, nunca thresholds de aprovacao nem motivo para ajustar
  a fisica.

Cada comando termina em `PASS`, `PRODUCT_FAIL`, `TEST_HARNESS_FAIL`,
`ENVIRONMENT_ERROR`, `BASELINE_FAIL` ou `NOT_RUN`; leitura de codigo nao equivale a
teste aprovado.

## Rollback e fase posterior

O rollback de runtime consiste em reverter os arquivos autorizados da tarefa ao
`BASE_SHA`, reconstruir os artefatos gerados e repetir os gates, sem reset destrutivo
ou reescrita de historico. A chave `jpwealth_galton_preferences_v1` so pode ser removida
do navegador real com autorizacao especifica; sua ausencia nao afeta `S`.

Ficam deliberadamente fora da Fase 1:

- roteiro de hipoteses e experimentos guiados;
- audio ou sonificacao de colisoes;
- interpretacao ou integracao com risco, Forex ou qualquer calculo financeiro;
- telemetria, sincronizacao em nuvem ou compartilhamento de resultados;
- promessa de determinismo entre plataformas.
