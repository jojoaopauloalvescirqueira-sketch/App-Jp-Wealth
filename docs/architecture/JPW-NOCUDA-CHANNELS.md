# JPW NoCuda Channels — contrato de engenharia do candidate 1.16.0

Este mapa descreve o indicador complementar `JPW_NoCuda_Channels.mq5` e os
limites verificáveis desta revisão. É subordinado a AGENTS, ao Harness e às
decisões humanas. Não cria regra de trading, validação de mercado nem aceite
operacional. A autorização delimitada está em
[`CHG-JPW-NOCUDA-FIBO-20261001`](../work/CHG-JPW-NOCUDA-FIBO-20261001.md).
A base 1.15.0, seus fontes e recibos ficam preservados; a versão do cálculo
financeiro continua 1.9.0. Os contratos anteriores de desenho manual,
projeção diária e apresentação continuam identificáveis pelos CHGs
`CHG-JPW-NOCUDA-DAILY-20260930` e `CHG-JPW-MT5-DESIGN-20260930`.

O artigo `artigo_nocuda_integral copy.pdf`, SHA-256
`274a8921796eb9824816db9a21dd6be9299f68ae166b0b06c6346ef332fd6168`, documenta
principal, paralela externa, meio e exemplos por fechamentos H1. A grade
−4…+4 a cada 0,125, as descrições, o fluxo Fibonacci e o calendário futuro H4
são escolhas explícitas de engenharia/proprietário. Não se importam pivôs,
rankings, detecção ou eficácia estatística como regras obrigatórias. C não é
automaticamente terceiro contato independente.

## Fronteira de validade

A captura dos parâmetros de `OBJ_FIBOCHANNEL` e a hipótese geométrica do
resolvedor são etapas distintas. O estado inicial é **UNVERIFIED_NATIVE**.
A fórmula candidata não pode fornecer uma medida pública validada: preços,
distâncias, adjacentes e projeções importadas permanecem **N/A** até haver
protocolo nativo dos bytes exatos e interpretação comprovada. Um laboratório
parcial, clonagem de propriedades ou oráculo auxiliar `OBJ_CHANNEL` não prova,
isoladamente, paridade integral com o Fibonacci. Não existe liberação por
clique do usuário nem conversão de PASS host em autorização nativa.

Esta restrição não invalida as consultas legadas: o modo manual mantém seu
contrato anterior. As saídas futuras de ambos os caminhos, quando elegíveis,
continuam Estimated; paridade geométrica não aprova um calendário futuro.

## Componentes

| Fonte em MQL5 | Responsabilidade |
|---|---|
| `Indicators/JPWealth/JPW_NoCuda_Channels.mq5` | Ciclo de vida e encaminhamento dos eventos; coexistência com Cockpit. |
| `Include/JPWealth/JPW_NoCuda_Fibo_Core.mqh` | Tipos puros, captura canônica, níveis/descritivos separados, resolvedor candidato e bloqueio UNVERIFIED_NATIVE. |
| `Include/JPWealth/JPW_NoCuda_Fibo_Terminal.mqh` | Leitura coerente do objeto nativo, símbolo/feed/período e sequência observada. |
| `Include/JPWealth/JPW_NoCuda_Fibo_Store.mqh` | SQLite exclusivo Fibonacci, snapshots/revisões imutáveis, aberturas congeladas, versão/checksum/CAS. |
| `Include/JPWealth/JPW_NoCuda_Fibo_Sync.mqh` | Acompanhamento da origem, rascunho, estabilização e checkpoints por alteração manual; não por tick. |
| `Include/JPWealth/JPW_NoCuda_Fibo_Controller.mqh` | Coordenação do fluxo Fibonacci e roteamento das ações, separado do modo manual. |
| `Include/JPWealth/JPW_NoCuda_Fibo_UI.mqh` | Janela, abas, resultados e ações do modo Fibonacci. Não confere paridade nem altera registros financeiros. |
| `Include/JPWealth/JPW_UI_Focus.mqh` | Arbitragem de foco das janelas; teclas de edição não são ações globais. |
| `Images/JPWealth/JPW_NoCuda_Logo.bmp` | Recurso de marca incorporado na compilação, derivado do ativo JP Wealth existente. |
| `Include/JPWealth/JPW_NoCuda_Core.mqh` | Núcleo geométrico manual AB0/C1 por ordinal. |
| `Include/JPWealth/JPW_NoCuda_Terminal.mqh` | Seleção manual horizontal de barra encerrada e ajuste ao Close. |
| `Include/JPWealth/JPW_NoCuda_Store.mqh` | Persistência legada dos estudos manuais; não migrada/reinterpretada. |
| `Include/JPWealth/JPW_NoCuda_Render.mqh` e `JPW_NoCuda_UI.mqh` | Desenho e apresentação do modo manual. |
| `Include/JPWealth/JPW_NoCuda_Projection_Core.mqh` | Ordinal fracionário, bins H1/H4, comparação exata de sequência e consulta diária pura. |
| `Include/JPWealth/JPW_NoCuda_Projection.mqh` | Histórico e sessões semanais para consulta, sem gravar estudos nem tocar no calendário Raiz N. |

O EA observador não é dependência. O NoCuda não altera as seis métricas,
USC, MDD, Gênese, Raiz N, Stop risk, mensagens, ordens ou stops. A antiga
`downloads/nocuda/Nocuda_Tool.mq5` permanece intacta. Seus números geométricos
não são reutilizados como se obedecessem ao novo contrato.

## Dois modos, sem migração implícita

**Fibonacci acompanhado:** selecionar explicitamente um objeto do símbolo
e feed atuais; capturar seus três pontos, horários/preços completos, levels,
descrições, estilos e raios. Nenhum snap ao Close, preço escolhido pelo cursor
ou normalização silenciosa é permitido. Nome, índice do nível e descrição
são metadados distintos. A descrição `5` corresponde a −0,50 na convenção
confirmada; `1 → −1`, `3 → −0,75`, `9 → 0`, `17 → +1`. Essa convenção não
limita o estudo a 17 linhas; os 65 levels e descrições originais permanecem
consultáveis. Nomes repetidos/vazios não identificam univocamente um nível.

**Manual legado:** A/B pertencem a 0, C a 1, meio 0,5. A posição horizontal
seleciona uma barra encerrada; seu Close fica no horário de abertura. H1 é
padrão, outra fonte é adaptação explícita. A/B na mesma barra, largura zero,
não finito, barra em formação ou histórico insuficiente são recusados.

```text
m = (PB − PA) / (jB − jA)
principal(j) = PA + m × (j − jA)
H = PC − principal(jC)
preço(nível,j) = principal(j) + nível × H
nível(k) = −4 + k/8, k = 0…64
largura = abs(H); subdivisão = largura/8
```

O sinal de H é preservado; arredondamento só na apresentação. Editar ou
arrastar no modo manual cria rascunho; somente Confirmar, com justificativa,
grava outra revisão. Cancelar restaura a anterior. O schema/convenção
`AB0_C1_BARS_V1` e o banco manual não são convertidos para Fibonacci.

## Sincronização, identidade e revisões

A confirmação inicial vincula uma origem explícita a um estudo. Mudanças
manuais da origem geram prévia durante a interação e podem produzir
checkpoints depois de estabilização/debounce. Não se grava a cada tick,
redesenho, zoom, rolagem ou consulta. Esses checkpoints pertencem somente ao
novo modo acompanhado; não removem a confirmação explícita do legado.

- Edite a origem no período de referência capturado. Alteração em outro
  timeframe suspende a sincronização até conferência no período correto.
- Captura incoerente, mudança durante a leitura, rascunho incompleto,
  conflito de geração ou gravação incerta preservam a última revisão íntegra.
- A ausência da origem não apaga o estudo. Excluir/ocultar não promove a
  última prévia a revisão; fica a última captura confirmada e a origem ausente.
- Nome igual não comprova identidade após rename/clone/recriação; reconectar
  exige conferência explícita. Troca de símbolo/feed invalida o contexto.
- Reinício retoma somente registros íntegros da instalação/feed corretos.
  Mudança de conta não cria um novo canal nem autoriza misturar feeds.
- Consultar uma revisão anterior não a torna a cabeça atual nem altera o
  desenho de origem. Restaurar cria nova revisão e pausa o acompanhamento;
  não move a cabeça para trás. Conflitos nunca fazem last-write-wins.

O armazenamento novo fica em
`MQL5/Files/JPWealth/NoCuda/Fibonacci/fibo_<chave_opaca>.sqlite`, separado do
manual e dos registros financeiros. Guarda captura completa, sequência real
congelada, schema/resolvedor, geração, relação entre revisões e checksum.
Transações e comparação da geração protegem a escrita; revisões confirmadas
são imutáveis. Corrupção e incompatibilidade não autorizam reset silencioso.
A conta, credenciais, saldos e operações não são conteúdo do estudo.

O schema exclusivo Fibonacci é versão 2, sem migração silenciosa. O catálogo
consulta até 20 metadados por página e confere o índice; o snapshot completo
é validado ao abrir. Atualizações da origem apenas marcam o catálogo como
pendente de atualização: o timer não percorre o histórico inteiro. Observações
manuais abrem OHLC, barra, nível e comentário preservados, sem certificar toque.
O reset de símbolo/feed invalida os dois editores antes de voltar à interface,
mesmo quando apenas um modo estava visível.

## Tempo, cotação e consulta

A geometria importada deve usar uma coordenada temporal congelada, formada
pelas aberturas reais do período de referência e interpolação intrabar.
Trocar a visualização não recompõe essa sequência. Em gaps podem existir
segmentos visualmente diferentes para conservar o preço no mesmo instante;
essa invariância requer prova nativa. Mudança posterior no histórico gera
aviso, sem mover o que foi confirmado. Não basta armazenar apenas o hash:
a sequência necessária ao resolvedor precisa acompanhar o snapshot.

Agora prioriza linha mais próxima e adjacentes acima/abaixo da cotação, sem
reduzir o catálogo aos rótulos 1–17. Deve informar origem de preço, horário,
qualidade e o nível real. Bid e Last não são trocados silenciosamente; a
origem depende do modo do gráfico/instrumento e precisa ser explícita.
Dados ausentes ficam N/A. USC não afeta preços ou distâncias; pips exigem
tamanho explícito para o símbolo exato. Toques são consulta/anotação manual,
sem detecção automática nem certificação de suporte/resistência.

## Projeção diária H1/H4

A consulta mostra onde a referência estará se a geometria for mantida, sem
prever cotação ou toque. Os horários são civis do servidor:

```text
início = linha(00h do dia)
meio = linha(12h do dia)
fim = linha(00h do dia seguinte), exibido como 24h
média dos extremos = (início + fim)/2
faixa = [min(início,fim), max(início,fim)]
```

O ordinal é crescente; para a função afim os extremos ficam nos limites da
janela. 12h pode diferir da média quando existem lacunas ou sessões parciais.
Não é média de cotação nem integral temporal. Precisão plena precede formato.

Histórico exige aberturas reais e os delimitadores dos instantes consultados;
ausência, divergência ou falta de cobertura produz N/A. A API preservada é
`JPWNoCudaProjectionLoadTimeline(symbol, tf, anchor_open, first, last, out, reason)`:
`anchor_open` é abertura exata de barra encerrada, não horário arbitrário de
um ponto Fibonacci. `out.opens`, `observed_count`, `sessions`, `generated` e
`source` separam aberturas observadas de coordenadas projetadas. O integrador
precisa relacionar a abertura de referência à sequência congelada do estudo;
não deve recalcular âncoras pelo histórico mutável.

Futuro admite **H1 e H4**; os demais períodos continuam somente históricos.
H1 usa bins de hora cheia; H4, **00/04/08/12/16/20** do servidor. Um bin é
esperado quando há sobreposição de sessão. Valida-se a sequência completa de
aberturas reais do próprio período nos últimos **14 dias civis encerrados**;
contagens iguais com falta/extra/desalinhamento não servem como comprovação.
Sessões parciais não exigem uma barra fictícia anterior à meia-noite inicial:
o confronto cobre todos os bins esperados dos 14 dias, incluindo o primeiro.
Uma sessão parcial pode contribuir três H4 mesmo com oito H1: não se divide
H1 por quatro. A primeira cotação possível determina quando um bin parcial
já deveria existir no dia corrente. O cache breve inclui período, feed,
símbolo e contexto; não preenche barra recém-esperada que esteja ausente.

A janela selecionável vai até **30 dias civis**; até **sete dias adicionais**
servem só ao delimitador de 24h. Nunca se usa a última barra como futuro. Dia
sem sessão não recebe faixa; dias parciais identificam pontos interpolados
fora da sessão. Horários incompatíveis, grade indisponível, histórico
insuficiente ou mudança durante a coleta recusam a projeção.
Em histórico de períodos amplos, como W1, a ausência de abertura no próprio dia
não demonstra ausência de sessão. Uma consulta coberta usa os delimitadores
observados e avisa que a sessão diária não foi inferida desses candles.

Todo futuro permanece **Estimated**, pois a API semanal não aprova exceções
futuras de feriados/DST. Uma consulta tem instante, fonte e assinatura
próprios; uma consulta posterior pode mudar se a grade mudar. Não se promete
preço futuro fixo absoluto. A cotação recente não altera essa classificação.
Consultas não criam revisão nem reescrevem cenário anterior. Enquanto a
captura Fibonacci estiver UNVERIFIED_NATIVE, seus resultados derivados e
registro de projeção calculada seguem bloqueados. Observação manual não
remove esse bloqueio. O calendário da Raiz N não é alterado.

## Janela e convivência

A janela Fibonacci inicia com cerca de 90% da área do gráfico. Os presets
Compacta (até 680×520), Ampla (90%) e Maximizada (margens) conservam acesso a
Fechar; cabeçalho e canto inferior permitem mover/redimensionar. A fonte
independente tem padrão 11 e faixa 9–24. As áreas são Canal, Agora, Projeção,
Registro e Aparência. O logo é recurso local de compilação, sem acesso remoto.

Campos, seleção e rascunhos não podem ser recriados/perdidos a cada timer.
Estado, valor, motivo e origem são campos separados. Resultados financeiros
não terminam em reticências. Preferência visual versionada pertence ao
gráfico; restauração por template ainda exige teste nativo. Foco/teclado são
compartilhados explicitamente com Cockpit, sem capturar digitação de um
campo como ação de outra janela. O modo manual mantém seu fluxo legado.

## Verificação, evidência e rollback

- Núcleo manual e persistência legada: scripts `JPW_NoCuda_Core_Tests` e
  `JPW_NoCuda_Store_Tests`, com focais host correspondentes; nenhuma migração.
- Projeção: `JPW_NoCuda_Projection_Tests` e
  `tools/jpw_nocuda_projection_test.py` executam o código efetivo com cenários
  sintéticos H1/H4 de parcial, overnight, domingo, gap, extra/falta,
  desalinhamento, 14 dias, +30 dias, leitura mutável e cache entre períodos.
- Fibonacci: `JPW_NoCuda_Fibo_Tests`, `tools/jpw_nocuda_fibo_test.py` e
  `tools/jpw_nocuda_fibo_store_test.py` cobrem tipos, níveis, bloqueio nativo,
  revisões e persistência. Os replays `tools/jpw_nocuda_fibo_terminal_test.py`
  e `tools/jpw_nocuda_fibo_store_runtime_test.py` executam adaptador e fluxo
  MQL5 com APIs sintéticas/SQLite host. PASS host não prova o renderer MT5.
- `JPW_NoCuda_Fibo_Lab.mq5` é instrumento do laboratório isolado: a execução
  e seus limites devem ser documentados. Nem clonagem de propriedades nem
  comparação auxiliar habilita silenciosamente a geometria.
- Compilar bytes exatos, interagir com canal nativo, comparar preços por
  instante, remover origem, reiniciar, testar conflitos, zoom, temas, DPI,
  foco, Cockpit e template exigem recibos nativos vinculados ao fingerprint.
  Sem isso: **NOT_RUN**, sem EX5 e sem prontidão operacional.
- Pacote/página, suíte MT5 host e full bruto permanecem gates separados;
  falhas herdadas não viram aprovação por esta mudança. Não se altera juiz
  para aprovar o produto. Nenhum teste usa conta ou terminal operacional.

Rollback: restaurar somente o delta desta revisão contra o snapshot 1.15.0
referenciado no CHG; regenerar derivados pelos geradores oficiais. Preservar
o banco Fibonacci para investigação e nunca removê-lo junto com estudos
manuais, MDD, Gênese, USC, Raiz N ou Stops. Não alterar o desenho antigo nem
registros financeiros. Commit, integração, publicação e instalação continuam
separados da entrega candidata.
