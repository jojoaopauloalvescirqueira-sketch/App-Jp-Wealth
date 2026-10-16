# Estudo de janelas Stoikus — 15/10/2026

Prévia independente: `docs/preview/stoikus-window-controls/index.html`. Arquivo portátil, sem rede, imports ou dependências; contém cópias base64 exatas dos SVGs aprovados `stoikus-assinatura-clara.svg` e `stoikus-assinatura-escura.svg`. Prévia R4 e marca original preservadas. Dados, valores, gráficos, histórico e objetos são explicitamente fictícios.

## Inventário navegável

| Janela | Telas e estados | Ações ilustrativas |
| --- | --- | --- |
| Conta | Visão geral, Posições e stops, Raiz N, Sistema, Ajustes, Histórico Pessoal | Seis seções nativas; sete métricas paginadas na Visão geral; detalhes por índice; Raiz N 1W/2W; preferências visuais e proveniência |
| Histórico | Fotografia concluída, auditoria sem linhas parciais, vazio, erro | Selecionar fotografia fictícia |
| NoCuda | Manual com três âncoras; Fibo H1 identificado; prévia; vínculo visual confirmado | Selecionar, conferir, confirmar, cancelar seleção; minimizar preserva seleção |
| Monitor | Presença fictícia; preparando auditoria; acesso bloqueado | Motivo e próxima ação explícitos |
| Resumo sobre gráfico | Compacto com alavancagem/risco ao stop e qualidade/escopos; completo com sete métricas | Abrir Conta sempre acessível; minimizar/restaurar resumo independentemente; modo completo/compacto; mover; largura manual; transparência do fundo |

Normal, carregando e bloqueado são selecionáveis no laboratório. Carregando exibe travessão; bloqueado exibe N/A. Valores sintéticos não são reaproveitados como leituras atuais. O fluxo NoCuda apresenta motivo e próxima ação nos estados sem leitura, bloqueia seleção/prévia/confirmação e oculta âncoras/gráfico. Origem/fase retidas são identificadas separadamente como rascunho não atual. Saldo, equity e valores de posições ficam N/A quando indisponíveis. Mesmo confirmado, o vínculo visual não valida medidas nem executa operação. Agora/Projeção/Registro são descritos nos detalhes do canal sem inventar resultados calculados.

## Regras visuais e de janela

Grade de espaçamentos 4/8/12/16px; Arial 11pt nos painéis e 10pt no resumo; controles usuais com alvo mínimo de 36px. As duas alças de canto têm área interativa de 36 × 36px. Cartões, conteúdos e paginação à esquerda. Badges têm largura do conteúdo. Descrições dos cartões ficam em duas linhas; detalhes permitem leitura integral. Valores monetários e percentuais não usam truncamento.

Conta inicia 720 × 520px; NoCuda, 680 × 500px. Consulta limitada a 85% da largura e altura do viewport; conteúdo rola internamente quando necessário. Navegação por largura real da consulta (CSS container queries): seis seções a partir de 680px; 3+3 de 400 a 679px; seletor abaixo de 400px. Cartões viram uma coluna quando a consulta tem menos de 400px, inclusive após resize manual em desktop. Paginação uniforme aparece no conteúdo, separada do rodapé de ações.

Resumo inicia com 280px e altura pelo conteúdo; largura manual até 480px ou 85% da área disponível. Quando completo excede a altura disponível, corpo rola sem perder métricas. Transparência 0–100 em passos de 10, padrão 30%, aplicada somente à camada de fundo; texto, controles e borda permanecem opacos. Consulta permanece sólida. Janelas podem mover e aumentar/diminuir por ponteiro; redimensionamento vertical é manual somente na consulta, pois o resumo tem altura automática. Posição é limitada pelo retângulo completo da consulta/resumo após drag, resize, mudança de modo ou viewport, mantendo título, corpo, rodapé e alça dentro do stage. Minimizar consulta preserva estado e oferece restauração; cancelar NoCuda limpa seleção. Resumo tem seu próprio minimizar/restaurar; Abrir Conta continua disponível na representação minimizada.

## Semântica financeira preservada

Alavancagem: nocional bruto na moeda da conta / último equity informado pelo terminal. P/L flutuante: percentual do saldo, sem crédito. Risco ao stop: grupo por símbolo e direção, denominador saldo; não é uma tese isolada. Genesis SL: referência selecionada, N/A sem referência inequívoca. Raiz N: janelas 1W e 2W com fator contextual F1,5; amostra nativa ainda necessária. Flutuante compensado: ciclo contábil selecionado; ciclo inferido não certifica Operação formal V11. Ausência de leitura não equivale a zero. Nenhum cálculo financeiro executado no HTML.

## Verificação e limites

Teste: `tools/stoikus_window_preview_test.py`, com Playwright já disponível em `/private/tmp/jpw-quality-audit-20261012-01a131dc/runtime/bin/python` e Google Chrome instalado. Sem instalação de dependências. Execução de Chrome exigiu sandbox escalation; execução simples abortou antes dos testes. Teste red observou `AssertionError: permanent fictitious badge missing` em HTML mínimo, antes da implementação.

Matriz: larguras 320/640/1280 × temas claro/escuro × estados normal/carregando/bloqueado, quatro janelas e seis seções. Verifica ausência de overflow horizontal do documento e limite de largura da consulta; muda navegação visível conforme viewport. Adiciona compacto/completo, sete métricas, transparência em onze níveis com texto opaco, movimento, aumentar/diminuir ambas larguras, minimizar/restaurar, preservação do NoCuda, seleção manual/Fibo, confirmar/cancelar e estados de histórico. Captura erros JavaScript. Inspeção visual direta de desktop claro e mobile 320px escuro em contexto novo. Capturas iniciais transitórias removidas após inspeção. A pedido do integrador, novas capturas duráveis em `docs/preview/stoikus-window-controls/study-desktop.png` e `study-mobile.png`.

PASS da prévia não demonstra compilação, runtime, instalação, eventos, DPI ou acessibilidade de MetaTrader. Build nativo e screenshots MT5 não foram identificados nesta tarefa. Resize por teclado não implementado na prévia; este protótipo verifica ponteiro. Não houve teste financeiro, conexão a conta, ordem, exportação, commit, push ou publicação. Revisão independente inicial exigiu seis correções, reproduzidas por regressões antes da correção. Evidências R2: `study-r2-desktop.png`, `study-r2-mobile.png`, `study-r2-narrow.png`. Nova revisão cabe ao integrador; autor não se declara revisor independente.

## R2 — rastreabilidade nativa e regressões

Identidades conferidas diretamente em `JPW_Alavancagem_Presentation.mqh` (tabs/overview/Raiz N/settings) e `JPW_Alavancagem_Cockpit.mqh` (IDs). A prévia conserva atributos `data-action` nas seções 40/41/42/43/44/120, cartões/atalhos 50–56 com índices 0–6, visibilidade 60–66, canto 30, densidade 31, ajustes 27/28/29 e pager 38/39. Os botões dos sete cartões no resumo abrem os detalhes correspondentes da Conta; atributos são identificação de fluxo, não execução de handlers MT5. Ajustes são rascunho visual demonstrativo sem persistência nativa. Sistema inclui componentes Monitor/Observer, Accountant, Histórico Pessoal, Raiz N e proveniência, além do motivo/ação do produtor.

Regressões independentes no mesmo script: `--round2`. Cada caso falhou antes da alteração: identidades nativas; minimizar HUD; seletor após reduzir consulta no viewport 1280; NoCuda confirmado→bloqueado; janela movida ao canto inferior; alvo resize abaixo de 36px. Depois passaram os seis casos, incluindo sete atalhos com seus IDs e bounds após corner-resize. A matriz original também foi ampliada para verificar overflow interno do conteúdo nas seis seções.

## R3 — ocupação mínima do gráfico

HUD padrão 280 × 232,28px medidos no browser, altura natural; header com Conta/minimizar/opções e duas linhas compactas de alavancagem/risco, escopos e qualidade. Modo e transparência ficam em opções fechadas inicialmente. Completo mantém sete métricas/atalhos, índices e IDs. Minimizado vira um único botão Conta medido em 55,58 × 38px, sem alça ou opções; clicar restaura só HUD e preserva consulta aberta/fechada. Botão Conta do header abre a consulta. Aviso global fictício permanece. Alvos do header têm mínimo 36 × 36px. R3 substitui a representação minimizada descrita em R2. Regressão `--round3` e screenshots `study-r3-{desktop,mobile,minimized}.png` registram essa versão.

## Correspondência e limites da prévia

A prévia é um estudo de composição e navegação, não uma imagem produzida pelo MT5. O browser usa CSS e pode rolar o corpo; o nativo usa objetos/recursos, paginação ou acesso compacto quando o conteúdo não cabe. Alturas de fontes, eventos, empilhamento e alfa precisam de prova própria no MT5. As capturas do browser não são usadas como aceite dos quatro EX5.

Os novos testes host de apresentação devem medir cada linha na fonte emitida, aplicar o DPI uma vez e usar índices de caracteres compatíveis com o MQL. Resultados anteriores da matriz que usavam medidas sintéticas sem DPI foram recusados na revisão independente e permanecem apenas como tentativas históricas. O recibo final identifica a bancada corrigida. Falha de recurso deve preservar acesso opaco, valor integral nos detalhes, escopo da conta e limite de clique independente do alfa.

## Limite inicial e ajuste manual no nativo

No plano aprovado, “tamanho inicial […] limitado a 85% do gráfico disponível” define os novos padrões. A interface nativa conserva configurações anteriores válidas e permite um redimensionamento explícito até a área disponível do gráfico; a escolha Maximizada do NoCuda continua válida. O retângulo inteiro permanece limitado ao gráfico. O HTML mantém um teto de 85% também durante sua demonstração de resize, portanto esse teto adicional da maquete não é um limite das preferências nativas.
