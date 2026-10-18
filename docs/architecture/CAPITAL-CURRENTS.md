# Contrato atual — Correntes de Capital: campo vivo com aprendizado

Candidate local em validação, 15/10/2026. A direção visual da primeira fatia foi confirmada pelo proprietário com “sim”; isso não homologa o conjunto ou demonstra aprendizado/diversão. O motor e o renderer do campo aceito são preservados.

## Entrada, lições e descobertas

O terceiro cartão de MiniGames mantém o laboratório acessível sem autoplay ou bloqueio por campanha. A breve explicação inicial apresenta campo vetorial, eixos e partículas. Aprender em 3 passos oferece: selecionar um ponto e avançar; aplicar/retirar pressão e observar a resposta residual; comparar profundidades no mesmo estado. A exploração livre permanece disponível e o aprendizado pode ser pausado, retomado, revisto ou pulado.

As descobertas usam o catálogo puro: `release-pressure` compara retirada/manutenção por 1 s a partir de q=0,6,p=0; `same-pulse-depth` aplica u=0,8 por 1,5 s e retira por 3 s, com profundidades 1/0,5; `shallow-band` compara perfis uniforme/rasa por 5 s, a partir de q=0,4,p=−1. Mesmos estados iniciais, instantes e escalas q[−1,1],p[−6,6]. A/B têm estilos de linha e marcadores distintos e valores finais derivados. Não há consulta a mercado futuro.

Reconhecimento de leitura depende de confirmação explícita. A prática exige ação observada e resultado correspondente na etapa atual, seguida de confirmação; não é declaração de compreensão humana. Abrir, restaurar, saltar ou rever não fabrica prática. Comparações são ações explícitas de cálculo e deixam estado, parâmetros e trajetória do laboratório intactos. Não há classificação por dinheiro.

## Fontes e fronteiras

Os seis scripts mantêm a ordem: motor `01-engine`, catálogo `02-scenarios`, progresso `03-progress`, renderer `04-field-renderer`, DOM `04-view`, controlador `05-controller`. O catálogo fornece itens estáveis e experimentos via `engine.advance`; não duplica as equações. `paramsA/B` descrevem os parâmetros iniciais e os rótulos registram o cronograma completo de u no experimento de pulso.

`JPWCapitalCurrents.mount/activate/deactivate/dispose` e identidade dos nós/rota são preservados. A seleção por toque/clique só se conclui ao terminar um toque, sem converter rolagem/cancelamento em reinício. Entrada de teclado equivalente, foco preservado e nenhuma reconstrução da lição a cada quadro. Saída, diálogo, ocultação ou perda de foco pausam; voltar não retoma sozinho.

## Progresso e recuperação

Chave nova `jpwealth_capital_field_v1`, formato exato `{version:1,steps:{ID:estado}}`. IDs: `intro-field`, `intro-pressure`, `intro-depth`, `release-pressure`, `same-pulse-depth`, `shallow-band`. Estados `seen`, `practiced`, `skipped`, apresentados como orientação vista, prática realizada e etapa pulada; evidência já obtida não é rebaixada ao rever. Não guardar conta, campo preenchido, parâmetro, valor financeiro, cenário, trajetória ou timestamp. A chave anterior `jpwealth_capital_currents_v1` permanece sem conversão.

Leitura não grava. Escrita usa comparação dos bytes lidos e confirmação por releitura. Incompatibilidade preserva bytes até reinício explícito; resultado desconhecido/conflito suspende e exige releitura. Falha com bytes comprovadamente inalterados permite RAM com aviso; nunca anunciar sucesso salvo sem confirmação. Eventos da nova chave em outra aba suspendem o fluxo, mesmo com mesmo valor. Reiniciar o progresso afeta somente a chave nova; a chave participa da limpeza auxiliar somente quando explicitamente solicitada; a política anterior para outras chaves é preservada. O descarte retira observadores e bloqueia callbacks antigos. O formato do Backup Completo e os escritores financeiros não mudam.

A proteção por bytes/releitura é otimista: detecta conflitos observados, sem prometer serialização atômica entre abas. Uma corrida entre a leitura e o setter pode sobrescrever progresso auxiliar antes da chegada do evento; não há dado financeiro nesta chave.

O modelo, oráculos e limites matemáticos da primeira fatia seguem abaixo. O gate mantém os três comandos existentes para Capital; as regressões da campanha são substituídas por provas do campo/ensino nos mesmos pontos de entrada; sua execução integrada e os gates completos são registrados nos recibos do candidate final. Resultados da campanha antiga são históricos, não validação da experiência substituta. Evidências em `tools/.artifacts/capital-field-work-20261015/phase2/`; finalização técnica e aceite continuam separados.

## Diagnóstico da matriz e evidência final

A observação antiga de excesso horizontal a 200% e a posição desatualizada de Notas foram reproduzidas com zoom CSS injetado sem o ciclo de resize. A simulação de window/visualViewport resize, seguida de dois quadros, corrige o teste sem modificar a UI ou relaxar overflow/hit targets. As 48 combinações não reproduziram esses sintomas com o ciclo correto; diagnósticos originais permanecem arquivados. Native zoom e toque físico não foram executados. O relatório e os recibos finais ficam em `tools/.artifacts/capital-field-work-20261015/phase2/REPORT.md`.

## Fotografias anteriores preservadas

# Correntes de Capital — laboratório de campo vivo

Redesign aprovado em 15/10/2026 após avaliação humana da expedição anterior: o campo parecia secundário. A primeira fatia está implementada e em validação na branch `codex/minigames-capital-currents-20261015`, preservando integralmente o candidate que contém Gêmeos do Tempo. Prévia de percepção antecede a expansão das descobertas opcionais; esta fotografia não declara o plano completo entregue.

O terceiro cartão e a visão local `capital-currents` permanecem em Ferramentas e Serviços → MiniGames. O laboratório substitui nave, carteira, pagamentos e campanha por um campo plano. Cada ponto/partícula é um cenário alternativo, não uma ordem, volume negociado ou probabilidade.

## Modelo da primeira fatia

O eixo horizontal `q` é pressão líquida efetiva fictícia, entre −1 e 1. O vertical `p` é deslocamento do preço em pontos simulados, exibido de −6 a 6 a partir de uma referência inicial arbitrária. Nenhum eixo é tempo. O relógio da simulação fica separado.

`dq/dt = (u − q)/τ` e `dp/dt = κ q / D(p)`.

Defaults: pressão aplicada `u=0,4`, `τ=1`, `κ=2` e profundidade normal `L=1`. Profundidades disponíveis `L=0,5; 1; 2`. No modo uniforme `D(p)=L`; na faixa rasa opcional `D(p)=L × [1 − 0,6 exp(−((p−1)/0,8)²)]`, sempre positiva. O motor usa passo fixo de 1/60 de unidade de tempo, solução analítica para q e RK4 para p. Arredondamento apenas na apresentação.

Retirar pressão faz q tender a zero. O preço pode continuar se deslocando enquanto q decai; não há força que o leve de volta à referência. Profundidade menor amplifica a resposta a uma pressão existente e, sozinha, não produz deslocamento quando q=u=0.

A inspiração de microestrutura vem da relação estudada entre fluxo líquido, profundidade e variação contemporânea dos preços ([Cont, Kukanov e Stoikov](https://arxiv.org/abs/1011.6402)). A equação de relaxação e o campo bidimensional deste laboratório são um modelo didático assumido; não reproduzem o livro de ofertas completo, não são uma lei universal e não fazem previsão de preços.

## Separação e apresentação

- `01-engine.js`: cálculo puro `fieldAt`, `advance` e `trace`, sem DOM, timers, aleatoriedade ou armazenamento. Estados/parametrizações inválidos são recusados; entradas preservadas.
- `04-field-renderer.js`: representação Canvas, eixos, vetores, linhas de corrente, partículas e trajetória selecionada, todos derivados do mesmo motor.
- `04-view.js`: controles e explicação em DOM semântico.
- `05-controller.js`: seleção, relógio fixo, ativação/pausa/descarte, sem escritores financeiros.

As linhas de corrente mostram caminhos se os controles atuais forem mantidos. A trajetória destacada registra o que aconteceu com o cenário selecionado. A renovação de exemplos de fundo é visual; não representa entrada de capital. Trajetórias que saem da janela não refletem nas bordas nem retornam artificialmente.

A montagem é única e sob demanda. Abrir mostra o campo pausado, sem iniciar o relógio. Saída, diálogo alheio, ocultação e perda de foco pausam; a retomada é explícita. Teclado tem campos numéricos equivalentes à seleção por ponteiro/toque e avanço por passos.

## Dados e estado da entrega

Nesta fatia, parâmetros, cenários e trajetórias ficam em memória; nenhum progresso novo é gravado. `jpwealth_capital_currents_v1` anterior é preservada sem conversão. Catálogo/progresso antigos permanecem temporariamente carregados, mas não são invocados pela nova superfície. A chave `jpwealth_capital_field_v1`, a introdução guiada e as descobertas opcionais pertencem à fase posterior do plano aprovado. Não alteram o formato do Backup Completo.

Baseline recuperável e evidências: `tools/.artifacts/capital-field-work-20261015/`. Testes focais novos: `tools/capital_field_unit_test.js` e `tools/capital_field_browser_test.py`. Testes da antiga campanha não são critérios funcionais do campo substituto; seus recibos históricos seguem abaixo e não aprovam esta revisão. Gate completo, host/distribuição, matriz integral e aceite humano serão executados/classificados no candidate final.

Sem commit, merge, push ou publicação. Clareza observada por testes automatizados/revisores e compreensão/diversão observadas em pessoas são evidências distintas.

## Experiência anterior — fotografia preservada

# Correntes de Capital — modelo, experiência e integração

Candidate local de 2026-10-15. O terceiro MiniGame preserva Galton Board e Gêmeos do Tempo. Não é uma conta de investimento nem um sistema de previsão. Fontes/testes aprovados e limites de execução são associados aos recibos próprios; este documento não comprova aceite humano, integração Git ou publicação.

## Propósito e fluxo

Pilotar uma nave que representa os pesos de dois ativos fictícios e caixa. A campanha combina descoberta do mercado, deriva de alocação, custos, compromissos e incerteza: `first-maneuver`, `weight-drift`, `wait-costs`, `cash-deadline`, `shared-storm`, `uncertain-expedition`. Entrada, seleção de missão e retorno nunca iniciam a simulação. Iniciar/Continuar são deliberados; pausa e investigação congelam o relógio. Há direcional/WASD/setas, toque/ponteiro e alternativa DOM de um passo.

A missão 1 encerra ao observar negociação e caixa ≥ 35%; a primeira corrente aparece no dia 1. As demais duram 60–75 dias simulados (1 dia por segundo ou 0,5 dia por segundo), sem contar pausa. A missão 5 parte sem caixa para permitir investigar a carteira passiva que mantém pesos iguais durante queda proporcional comum. A missão 6 tem pagamentos distintos nos dias 35 e 65 e condições de negociação que mudam após reveladas. Objetivos e custos são fictícios, definidos no catálogo; não representam uma política financeira do JP Wealth.

Nas missões com compromissos (4 e 6), cumprir os pagamentos é o sucesso principal. Mandato de pesos e controle de custos têm reconhecimentos próprios e não vetam a conclusão; patrimônio final permanece informativo. A missão 3 mantém seu objetivo didático explícito de orçamento de negociação. A verificação da explicação causal continua necessária para registrar demonstração sem ajuda.

Investigação: livro de bordo de cada pulso, comparação sem uma manobra, tentativa anterior e referência sem negociar. O cutoff limita referências ao instante observado; após a conclusão, o histórico completo daquela rodada fica disponível. Apenas o caminho externo do mercado é mantido entre tentativas: saldos, restrições, custos e pagamentos são recalculados. O jogador é pequeno perante esse cenário, sem impacto sobre seus preços externos. Compromissos sem caixa são marcados não pagos; não existe venda automática ou crédito.

O detalhe espacial do inspetor mostra os quatro estados do mesmo pulso: antes, após negociar e cobrar custo, após retorno e após pagar. Os pontos derivam dos saldos observados e usam uma única escala e translação nos dois eixos; posições coincidentes permanecem coincidentes. A ampliação em relação ao mapa visível é declarada. Selecionar um pulso histórico não avança o relógio nem altera a tentativa. A legenda externa da referência identifica tipo, datas e pagamentos; quando os instantes finais diferem, a trilha da referência fica restrita à comparação histórica do livro.

## Matemática e fronteiras da metáfora

A fonte da verdade são valores monetários H=(A,B,C). Patrimônio V=A+B+C; pesos w=H/V. Posição triangular p=wA·(0,0)+wB·(1,0)+wC·(0,5;√3/2). Posição não é lucro, risco ou liquidez negociável. Sem negociar, H'i=Hi·(1+ri), e w'i=wi·(1+ri)/Σwj(1+rj). Campo é a mudança exata de posição para o retorno revelado do último pulso. A escala visual é declarada; prolongamento só significa “se este pulso se repetisse”, sem acesso a choques futuros.

Negociar qA/qB: A+=qA; B+=qB; C−=qA+qB+κ(|qA|+|qB|). Custo no notional efetivamente executado. Capacidade em dinheiro/dia e posições/caixa limitam a execução por uma fração comum admissível. Não há short, alavancagem ou empréstimo. Os limites do perfil são sinais, não paredes. Tolerância pós-pagamento vale só para aferir o perfil, nunca para conceder prazo extra ou caixa ao pagamento.

DT=0,05 dia simulado; o desenho não altera saldos. Em cada tick: executar com condições conhecidas e cobrar custos; aplicar próximo pulso; pagar obrigações agora vencidas; revelar novas condições de liquidez para a próxima execução; apurar perfil. Retornos dependem de seed/tick/ativo, nunca de decisões do jogador. Não há impostos, rendimento no caixa ou rentabilidade prometida. Valores são arredondados só na apresentação.

Microlivro: experimento discreto com mesma ordem e saldos de referência em dois livros de profundidades diferentes, incluindo cancelamento declarado. Mostra níveis, execução, custos e cotações observadas; não cria uma força física nem previsão. Liquidez de negociação difere de caixa disponível.

Fontes conceituais: [Investor.gov — Asset Allocation](https://www.investor.gov/introduction-investing/getting-started/asset-allocation), [Boyd et al. — Multi-Period Trading via Convex Optimization, §2.5](https://stanford.edu/~boyd/papers/pdf/cvx_portfolio.pdf), [Cont, Kukanov e Stoikov — The Price Impact of Order Book Events](https://arxiv.org/abs/1011.6402). A relação contemporânea fluxo/profundidade estudada no artigo não é transportada para promessa de próximo retorno.

## Arquitetura, APIs e estado

Cinco scripts clássicos em `src/js/40-app/30-capital-currents/`: `01-engine`, `02-scenarios`, `03-progress`, `04-view`, `05-controller`. Namespace `window.JPWCapitalCurrents`.

- `engine`: DT, create, step, weights, position, field, execute, replay, compareBooks. Independente de DOM, storage, S, contas e writers.
- `catalog`: seis missões, get, evaluate e lab. Configuração estrita, estados novos por tentativa. evaluate separa objetivo, compromisso, perfil e custo; nenhum ranking de lucro.
- `progress`: KEY, VERSION, load, save, mark, restart. Somente versão e missionID→assisted/demonstrated/skipped. A demonstração não é rebaixada por ajuda ou salto posteriores. Não constitui prova de aprendizagem humana.
- `view`: estrutura/controles estáveis; Canvas para representação e DOM para valores, ações e investigação.
- `mount(host)`: instância única. activate/pause/deactivate/destroy/snapshot no controlador; activate/deactivate/dispose no namespace. Snapshot publica somente história observada, sem config/choques futuros.

Chave `jpwealth_capital_currents_v1`, somente auxiliar, fora de S e Backup Completo. Parâmetros do laboratório, valores, seeds customizadas, comandos e tentativas permanecem na RAM. Leitura inválida não normaliza bytes; salva apenas após reinício explícito. Erro de armazenamento permite sessão temporária com aviso. save/restart usam raw esperado para detectar conflito; gravação tem leitura de confirmação. Evento de outra aba pausa e pede releitura, sem descartar a tentativa em memória.

Tools hospeda `#toolsCapitalCurrentsSlot` na view local `capital-currents`, child `tools-minigames`. Navegação recusada não monta. Diálogo, saída, página oculta, blur e mudanças de movimento pausam; controles presos são liberados. Sem RAF contínuo enquanto pausado. Finalização descarta todas as instâncias/listeners/callbacks; observadores de visibilidade não ressuscitam controlador. Nova entrada explicitamente aceita pode montar uma instância limpa. Limpeza de preferências remove somente a chave auxiliar junto às demais já existentes.

## Distribuição e verificação

Manifesto com 117 scripts: 112 anteriores na mesma ordem relativa, cinco novos antes do loader de downloads. Os quatro scripts finais do guia conservam posições relativas. A lição `general-settings-probability-lab` mantém ID, trilha e versão, apontando aos três cartões. Scripts no precache; portátil/sidecars pelo gerador oficial.

Testes: motor e oráculos independentes; progresso adversarial; browser standalone/integrado; quatro layouts/temas/zoom/mobile; HTTP/file/portátil/PWA offline; Galton/TimeTwins/guia; estado financeiro/backup/finalização; reprodutibilidade/full e host/distribuição. Gates pertencem ao candidate congelado, não às evidências de versões anteriores.

Gauntlet compara ação, resposta e investigação com [PhET — Charges and Fields](https://phet.colorado.edu/sims/html/charges-and-fields/latest/charges-and-fields_en.html) realmente carregado/interagido em desktop/mobile. Modelo financeiro tem verificação própria. Reconhecimento da identidade visual impede cegamento completo e deve ser declarado. Compreensão, diversão, aprendizado humano e aceite do proprietário permanecem NOT_RUN até sessões humanas; automação não substitui essa prova.
