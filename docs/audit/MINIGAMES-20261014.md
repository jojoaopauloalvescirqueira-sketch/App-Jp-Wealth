# MiniGames — entrega local de 2026-10-14

Base `c765908516f6ef5228be0c5d7f1d98d937eb224b`, branch `codex/minigames-20261014`, build `66874031bb9ab590`.

## Resultado

Ferramentas e Serviços possui MiniGames como quinto e último destino. A central contém um cartão Galton Board com Abrir. O jogo conserva seu nome e oferece Voltar para MiniGames. A entrada antiga foi removida de Configurações/Conhecimento.

O catálogo não monta o motor. O primeiro acesso ao jogo monta uma única instância; voltar conserva tabuleiro, fila, histograma e preferências em memória, pausados. Saída e cobertura por diálogo cancelam o ciclo e desconectam o observador de tamanho; retornar exige Continuar. A regra existente de visibilidade da aba e o descarte por finalização continuam no controller original.

## Interfaces e compatibilidade

- `tools-minigames` identifica o submenu; `tools/minigames` abre o catálogo e `tools/galton` abre o jogo, com o mesmo child ativo.
- `probability-lab`, `galton-board`, `research-probability-lab`, aliases locais de Research e APIs antigas de Configurações resolvem o mesmo jogo. Com diálogo aberto, o pedido é recusado com orientação, sem fechar janelas, trocar o contexto ou cancelar rascunhos. Nenhum pedido é executado depois automaticamente.
- A lição `general-settings-probability-lab` preserva ID, trilha general e versão1. Seu destino inclui rota e visão local do catálogo. O passo funciona a partir do próprio jogo, embora os dois compartilhem canonical. Os 57 passos/sete trilhas, registros e cursor antigos continuam compatíveis.
- Avisos locais do Galton aparecem como MiniGames e apontam diretamente ao jogo. Nenhum coletor financeiro, escritor ou categoria de armazenamento foi acrescentado.

107 scripts conservam caminhos e ordem. O gerador oficial atualizou o portátil, build-id e envelopes com o novo build; o service worker usa esse identificador para o cache existente. Os conteúdos dos payloads foram preservados. Não houve nova dependência.

## Verificação

A execução final de `quality_gate.py --tier full` terminou com **75/75 comandos PASS**, sem PRODUCT_FAIL, TEST_HARNESS_FAIL, ENVIRONMENT_ERROR, BASELINE_FAIL ou NOT_RUN nessa rodada. Inclui backup, persistência, finalização, conflitos, guia, notificações, as otimizações da grade, reprodutibilidade, atualização do service worker e zoom nativo. O [recibo versionado](../validation/minigames-20261014/quality-gate.json) conserva os comandos, resultados, tempos e hashes da origem.

O novo focal comprovou catálogo sob demanda, Abrir pelo teclado, foco, três retornos com a mesma instância, fila/histograma preservados e três diálogos, com igualdade de S e de todo localStorage após preparar o epoch pela API real da fixture. Conferiu 32 combinações de apresentação e a retomada da lição a partir do jogo. O fluxo também passou em modular file://, portátil copiado sozinho e PWA offline, este com 124 respostas via service worker. São verificações funcionais locais com dados sintéticos.

Focais adicionais aprovados: Galton completo (oráculos numéricos, físicos, persistência, UI e lifecycle), Research (quatro layouts, desktop/celular, nove chamadas legadas e recusa), Configurações, navegação IA, Nocuda (109 checks) e design (110 checks). Controller do guia: 84/84. Foram inspecionadas as capturas do catálogo desktop claro e do jogo no celular escuro; as demais combinações têm verificações automatizadas.

O freeze de 1015 arquivos regulares disponíveis foi conferido sem divergência. Os 195 arquivos protegidos, incluindo domínio financeiro, schemas/persistência, backup, módulos Galton, dados, norma e MT5/distribuição, permaneceram byte-idênticos. A revisão independente global não deixou achado acionável aberto.

## Histórico de falhas e limites

A ausência inicial da central produziu RED antes da implementação. A revisão encontrou e reproduziu em navegador uma falha no guia: somente a rota compartilhada não distinguia catálogo de jogo. A correção acrescentou a visão local; o novo GREEN confirmou o retorno ao catálogo sem mudar IDs ou progresso. Tentativas e pareceres anteriores permanecem preservados.

As primeiras comparações da fixture incluíam a criação normal do epoch ao abrir Finalizar sessão. A fixture passou a estabelecer esse epoch pela API real antes da referência, mantendo a comparação rígida de S e de todas as chaves; nenhum escritor foi alterado. Outros ajustes de fixture passaram a abrir Configurações explicitamente e aguardar a microtask do lifecycle, preservando os oráculos.

Duas verificações opcionais de VM, fora da suíte integral, reproduziram falhas na própria base c765908: foundation com window separado do global e local-navigation em exec:overview. Os registros BASELINE_FAIL foram preservados; não foram apresentados como testes aprovados nem motivaram correção adjacente do runtime.

No celular, o launcher móvel de Notas sobrepõe parcialmente a borda direita de +500 na captura inspecionada; o botão conserva área exposta e a tela permite scroll. Isso não demonstrou bloqueio funcional. A matriz visual não prova ausência de toda sobreposição de elementos flutuantes.

A validação web não estabelece instalação pelo sistema operacional, execução nativa MT5, aceite manual ou publicação. A entrega permanece local nesta branch, com main e remotos preservados. Rollback: usar a revisão-base c765908 em ambiente isolado; a mudança não requer migração de dados nem limpeza de preferências.

## Coerência documental e segurança

README, Galton, navegação, disponibilidade, arquitetura, mapa e notificações foram reconciliados no recorte autorizado; histórico datado foi preservado. AGENTIC IMPACT CHECK: AGENTIC IMPACT DETECTED. BASIS: mudou o host/contrato de navegação que esses documentos representam; as descrições correntes foram ajustadas. Snapshots históricos, instruções, políticas, roteamento de agentes, gates e índices não foram reescritos. Este fechamento não afirma reconciliação geral do projeto.

A revisão do diff não identificou nova entrada externa, rede, permissão, credencial, armazenamento ou autoridade financeira. A inserção do aviso de navegação usa texto constante; o painel reutiliza o HTML do controller e recursos locais. Evidências completas e hashes permanecem no pacote recuperável da entrega, fora do corpus do aplicativo.
