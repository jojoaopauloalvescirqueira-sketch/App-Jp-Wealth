# Calendário — notícias sem rolagem horizontal

Pedido03/11/2026: eliminar rolagem horizontal das notícias sem aumentar sua altura, permitir janela até20% mais larga e revisar apenas a ferramenta. Confirmação humana: em painéis estreitos, quatro colunas na linha; Atual/Projeção/Anterior no detalhe “i”.

Basecd445e99f511eb141b3b96a0e05e5d0b97984416, branch existente `codex/ux-notas-menus-20261102`. N0-V/N1 local; sem Git/publicação, alteração financeira, fontes, cache, preferência ou backup. Preservar outras worktrees.

Finalidade: consultar agenda pessoal e eventos econômicos com estado/qualidade da alimentação explícitos. Causa observada: tabela mínimo860px, larguras intrínsecas e título/avisos impediam ajuste no painel. Janela760→912px limitada àviewport; calendário mensal mantém308px, seleção e navegação. Tabela fluida com linhas44px e tipografia12–13px. Sete colunas a partir de500px úteis de notícias; quatro abaixo, valores completos rotulados no detalhe. Elipses no título/valores longos, texto integral no detalhe. Sem scroll horizontal ocultando campos.

Superfícies autorizadas: CSS local, renderizador compartilhado, contrato/testes de calendário, manifesto/derivados oficiais, registro factual e tarefa ativa. Tabela HTML conserva roles explícitos table/rowgroup/row/columnheader/cell ao usar grade CSS para alinhar colunas e detalhe responsivo. Preservar foco, expansão por identidade, refresh, rascunho, filtros, cobertura e distinção ausência/zero. Abrir detalhe pode crescer deliberadamente; linhas fechadas não crescem.

Preflight inicial BLOCKED por hash do ajuste de Notas anterior não atualizado em manifest.json. Reconciliação pelo rebuild oficial --refresh-manifest, sem editar verificador nem Notes: um hash, nenhuma ordem/metadado de script alterado. Preflight de edição com alterações conhecidas passou depois. Segundo refresh registra apenas o renderizador desta entrega. Incidente e recibo preservados fora do app.

Revisão focal: RED real nos hosts workspace/modal, GREEN de proporções, alinhamento2px, altura44px, quatro/sete campos, valores no detalhe, fontes, teclado/foco/refresh, temas e larguras320–1440px. Rebuild oficial e fonte/portátil. FULL local/Linux novos fora do escopo solicitado, NOT_RUN; não transferir PASS histórico. Não alterar gates/CI/skills.

Rollback somente do delta, reconstruindo derivados; sem dados reais ou limpeza. Cópias anteriores, capturas e recibos em outputs/calendar-fit-20261103/ da sessão Codex. Reconciliar apresentação somente nesta ficha/tarefa e expectativas focais; política operacional e persistência inalteradas.
