# CHG-HEADER-FOCUS-20260923

Status: escopo autorizado pelo proprietário; resultado e aceite pendentes. N1 / A2.
Autoridade: pedido 90a7507e-3cd8-4cae-a215-58fa1956e2fe, recebido nesta tarefa.
Registrado antes da escrita de código. Sem commit, push, PR, merge, integração ou publicação.

## Origem, alvo e compreensão

Origem integral: /Users/joaopauloalves/.codex/header-navigation-lucide/20260923/product,
branch codex/header-navigation-lucide-20260923, HEAD b0cd4b61dc3fdd63f0fcf8bc1255455e6c59624e,
build da24235203f5d84a, fingerprint e22cb0b660cb0a9d40e324b49940b197c29e0d2a49eea1dcf8b852099ed74d54.
Derivação inclui arquivos modificados e novos sem commit, conferidos por hash.
Alvo: /Users/joaopauloalves/.codex/header-navigation-focus/20260923/product,
branch codex/header-navigation-focus-20260923, mesmo HEAD de base.

JP Wealth preserva dados financeiros locais. Este recorte corrige a continuidade do teclado
após fechar superfícies do cabeçalho. O shell escolhe um destino disponível; os controladores
Settings, Notificações e a apresentação do modal de sessão conservam a responsabilidade pelo
fechamento. Nenhum cálculo, armazenamento ou comando financeiro é redefinido.

Hoje Cancelar/Escape não retornam foco após sessão; Settings e Notificações podem tentar focar
ações ocultas pelo Glass compacto. Depois, o acionador disponível ou seu botão de acesso recebe
foco, sem disputar camadas abertas e sem interferir no handoff intencional ou confirmação.

## Fronteira

Permitir apenas delta focal em:
- src/js/40-app/07-finalize-session.js: sessão modal, entrada/saída de foco; NÃO transação financeira.
- src/js/40-app/09-settings-modal.js: retorno de foco no fechamento.
- src/js/40-app/11-operational-shell.js: helper compartilhado de disponibilidade/retorno.
- src/js/40-app/18-notification-center.js: retorno de foco no evento close.
- tools/header_focus_return_test.py: novo teste de produto diretamente relacionado, sem enfraquecer testes.
- docs/work/CHG-HEADER-FOCUS-20260923.md e adendo em ACTIVE-TASK.md.
Derivados somente pelo gerador oficial inalterado: build-id.js, src/js/manifest.json,
src/vendor/pdfjs/runtime-assets.js e dist/JP_Wealth_Risk_Terminal_V9.1_PORTABLE.html.

Preservar HTML/CSS/SVGs licenciados, quatro layouts, seleção, foco lógico, formulários,
rascunhos, nós e rotas. Não alterar domínio, dados, persistência, backup, onboarding,
Alladin/Planejamento internos, dependências, rede, Harness, gates, classificadores ou CI.
Preservar integralmente origem/evidências, main, onboarding e prévias.

## Critérios, teste e revisão

Antes do runtime: definir teste focal e executar sobre origem para registrar a falha.
Matriz: quatro layouts, claro/escuro, 1440/1024/390/320; Cancelar, Escape, backdrop,
Notificações, Configurações e Perfil. Destino conectado/visível/habilitado; sem BODY como fallback.
Adversariais: acionador indisponível, resize Glass, reabertura rápida, outra camada ativa,
restoreFocus:false e close(false), entrada por teclado e múltiplas aberturas; preservar estado/rascunho.
Teste existente de layouts, Settings, Forex/navigation e reprodutibilidade + estrutural/diff.
Congelar novo candidate após focais favoráveis; standard canônico UMA vez, comando inalterado.
Coleta externa de stdout com timestamps; se necessária coleta suplementar Alladin separada,
sem mudar asserts, limpar erros, retry, timeout ou atribuir causa ausente.
Revisão independente do diff final e recibos. Critérios técnicos não são aceite humano.
Falha histórica C12 permanece aberta independentemente de novo resultado.

Rollback: usar candidate anterior preservado; nenhum dado migrado. Descartar apenas esta
worktree mediante pedido, nunca outras árvores. Evidências em ../evidence.
Fontes: AGENTS.md, CONTEXT-MAP, PROJECT-CONTEXT, CURRENT-STATE, NAVIGATION-HIERARCHY,
CHANGE-PROCESS, QUALITY-GATES; skills preflight/change-control/browser-verification/test-triage/
post-change-audit/security-audit. Harness consultado na fonte atual do vault, SHA-256
c1b5ca9da4dfa2c9a9d1fa3d87a9f7ef9c4cb741fffeedee33d37978f5b800c8, §§12–14,24,28–30,36–49.
Fontes não serão alteradas. Próximo recorte: apresentação da Execution Board e seus componentes,
não implementado aqui. Safari/iPhone físico e tecnologias assistivas reais permanecem limites.

Destino lógico adicional, somente para os quatro acionadores conhecidos do cabeçalho indisponíveis em desktop: marca/início (#brandHomeBtn), validada como disponível. Em compacto, priorizar o botão que abre o menu. Não inventar fallback genérico para acionadores de outro contexto. Contrato focal detalhado registrado externamente antes do runtime em FOCUS-TEST-CONTRACT.json.

Precisão sobre regeneração: o gerador oficial existente não atualiza hashes de scripts no manifesto. Estes quatro campos sha256 são recalculados mecanicamente sobre os bytes, sem mudar lista/ordem. Build e portátil são gerados exclusivamente por tools/rebuild_monolith.py inalterado.

## Ajuste diretamente necessário ao foco visível — antes da escrita CSS

A observação real revelou :focus-visible verdadeiro com outline none nas ações do cabeçalho,
antes e depois do JS. Regra antiga de duas IDs usa --blue ausente; a regra focal posterior
com --shell-action perde por especificidade. A autorização de correção de apresentação/foco
é aplicada a UMA adição de seletor em src/styles/app.css, na regra de foco já existente.
Preservar declarações (2px, cor do shell, offset), medidas, SVGs, estados sem foco e demais CSS.
Não é redesign nem ampliação de alvos. Recibo: focus/outline-characterization.json.
Testes passam a exigir contorno efetivamente computado nas saídas por teclado.
Resultados anteriores desta rodada ficam como iteração anterior ao ajuste, sem sobrescrita.
